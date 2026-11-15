import argparse
import json

import duckdb
import mlflow
import numpy as np
import xgboost as xgb
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


CLEAN = [
    "amount",
    "is_transfer",
    "hour_of_day",
    "oldbalance_org",
    "oldbalance_dest",
    "drain_ratio",
    "drains_account",
    "dest_balance_zero",
    "dest_prev_txn_count",
]
POST = ["newbalance_org", "newbalance_dest"]
REVIEW_COST = 5.0


def load():
    con = duckdb.connect("warehouse.duckdb", read_only=True)
    try:
        return con.execute("select * from main.fct_features").df()
    finally:
        con.close()


def business_cost(y, amount, scores, threshold):
    flagged = scores >= threshold
    missed = amount[(y == 1) & (~flagged)].sum()
    return missed + REVIEW_COST * flagged.sum()


def best_threshold(y, amount, scores):
    grid = np.unique(np.quantile(scores, np.linspace(0.5, 0.9999, 200)))
    costs = [business_cost(y, amount, scores, threshold) for threshold in grid]
    return float(grid[int(np.argmin(costs))])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-post", action="store_true")
    args = parser.parse_args()

    features = CLEAN + (POST if args.with_post else [])
    df = load()

    train = df[df["step"] <= 500]
    val = df[(df["step"] > 500) & (df["step"] <= 620)]
    test = df[df["step"] > 620]
    print(
        "fraud rows train/val/test:",
        int(train["is_fraud"].sum()),
        int(val["is_fraud"].sum()),
        int(test["is_fraud"].sum()),
    )

    Xtr, ytr = train[features], train["is_fraud"].astype(int).values
    Xva, yva = val[features], val["is_fraud"].astype(int).values
    Xte, yte = test[features], test["is_fraud"].astype(int).values

    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("fraud-detection")
    run_name = "with_post_balances" if args.with_post else "clean_features"

    with mlflow.start_run(run_name=run_name):
        mlflow.log_param("features", ",".join(features))
        mlflow.log_param("review_cost", REVIEW_COST)

        logreg = make_pipeline(
            StandardScaler(),
            LogisticRegression(class_weight="balanced", max_iter=1000),
        )
        logreg.fit(Xtr, ytr)
        lr_pr = average_precision_score(yte, logreg.predict_proba(Xte)[:, 1])

        iso = IsolationForest(
            n_estimators=200,
            contamination="auto",
            random_state=42,
        )
        iso.fit(Xtr)
        iso_pr = average_precision_score(yte, -iso.score_samples(Xte))

        ratio = float((ytr == 0).sum() / max((ytr == 1).sum(), 1))
        model = xgb.XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=ratio,
            eval_metric="aucpr",
            tree_method="hist",
            random_state=42,
        )
        model.fit(Xtr, ytr, eval_set=[(Xva, yva)], verbose=False)

        val_scores = model.predict_proba(Xva)[:, 1]
        threshold = best_threshold(yva, val["amount"].values, val_scores)
        test_scores = model.predict_proba(Xte)[:, 1]
        xgb_pr = average_precision_score(yte, test_scores)

        flagged = test_scores >= threshold
        tp = int(((yte == 1) & flagged).sum())
        fp = int(((yte == 0) & flagged).sum())
        fn = int(((yte == 1) & ~flagged).sum())
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        cost = float(
            business_cost(yte, test["amount"].values, test_scores, threshold)
        )
        no_model_cost = float(test.loc[test["is_fraud"], "amount"].sum())

        metrics = {
            "pr_auc_logreg": lr_pr,
            "pr_auc_isolation_forest": iso_pr,
            "pr_auc_xgboost": xgb_pr,
            "precision_at_threshold": precision,
            "recall_at_threshold": recall,
            "business_cost_model": cost,
            "business_cost_no_model": no_model_cost,
            "threshold": threshold,
        }

        for key, value in metrics.items():
            mlflow.log_metric(key, value)
            print(f"{key:28s} {value:,.4f}")

        if not args.with_post:
            model.save_model("models/xgb.json")
            metadata = {"features": features, "threshold": threshold}
            with open("models/meta.json", "w") as file:
                json.dump(metadata, file)
            mlflow.log_artifact("models/meta.json")


if __name__ == "__main__":
    main()
