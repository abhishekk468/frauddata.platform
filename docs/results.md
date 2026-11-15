# Model results and leakage experiment

| Model | PR-AUC (test) |
|---|---:|
| Isolation Forest | 0.5741 |
| Logistic Regression | 0.9702 |
| XGBoost | 0.9952 |

At the validation-chosen threshold on the clean-feature test set:

- Precision = 0.9253
- Recall = 0.9971
- Cost with model = 406,405.0800
- Cost with no model = 2,340,743,287.2300

The XGBoost model won with a PR-AUC of 0.9952, ahead of Logistic Regression at
0.9702 and Isolation Forest at 0.5741. The selected threshold was 0.0128:
it catches nearly all fraud while sending a smaller set of transactions for
manual review. Under the stated assumptions, the model reduces simulated
cost by approximately 2.34 billion compared with taking no action.

The leakage experiment added the post-transaction balance columns. XGBoost
PR-AUC increased from 0.9952 without them to 0.9960 with them, while the
model cost decreased from 406,405.0800 to 7,370.0000. These columns are still
excluded from the production feature set because they are only known after the
transaction completes and therefore are unavailable at approval time.

Assumptions: each flagged transaction costs 5 for manual review; missed fraud
costs its transaction amount. PaySim is a simulation, so these results should
not be treated as real-world performance.
