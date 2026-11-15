import json
from pathlib import Path

import pandas as pd
import xgboost as xgb
from fastapi import FastAPI
from pydantic import BaseModel, Field


BASE = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE / "models"

model = xgb.XGBClassifier()
model.load_model(MODEL_DIR / "xgb.json")
meta = json.loads((MODEL_DIR / "meta.json").read_text())
FEATURES = meta["features"]
THRESHOLD = meta["threshold"]

app = FastAPI(title="Fraud Scoring API")


class Transaction(BaseModel):
    step: int = Field(ge=1, le=744)
    txn_type: str = Field(pattern="^(TRANSFER|CASH_OUT)$")
    amount: float = Field(ge=0)
    oldbalance_org: float = Field(ge=0)
    oldbalance_dest: float = Field(ge=0)
    dest_prev_txn_count: int = Field(ge=0)


def build_features(transaction: Transaction) -> pd.DataFrame:
    drain_ratio = (
        min(transaction.amount / transaction.oldbalance_org, 10)
        if transaction.oldbalance_org > 0
        else -1
    )
    row = {
        "amount": transaction.amount,
        "is_transfer": 1 if transaction.txn_type == "TRANSFER" else 0,
        "hour_of_day": (transaction.step - 1) % 24,
        "oldbalance_org": transaction.oldbalance_org,
        "oldbalance_dest": transaction.oldbalance_dest,
        "drain_ratio": drain_ratio,
        "drains_account": int(
            transaction.oldbalance_org > 0
            and transaction.amount >= transaction.oldbalance_org
        ),
        "dest_balance_zero": int(transaction.oldbalance_dest == 0),
        "dest_prev_txn_count": transaction.dest_prev_txn_count,
    }
    return pd.DataFrame([row])[FEATURES]


@app.get("/health")
def health():
    return {"status": "ok", "threshold": THRESHOLD}


@app.post("/predict")
def predict(transaction: Transaction):
    probability = float(model.predict_proba(build_features(transaction))[0, 1])
    return {
        "fraud_probability": probability,
        "flag": probability >= THRESHOLD,
        "threshold": THRESHOLD,
    }
