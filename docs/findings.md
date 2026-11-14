# Fraud analytics findings

## Finding 1: TRANSFER versus CASH_OUT

TRANSFER carries 50.32% of fraud value and CASH_OUT carries 49.68%, so monitoring should start with both transaction types rather than prioritizing only one.

## Finding 2: Highest-risk hours

Hour 4 has the highest fraud rate at 57.9114%, followed by hour 3 at 53.5156%, so monitoring and review capacity should be concentrated in hours 3–5.

## Finding 3: Fraud rate by amount

Transactions over 500,000 have the highest fraud rate at 1.229%, compared with 0.163% for transactions from 100,000 to 500,000, so high-value transactions deserve additional risk controls.

## Finding 4: Blocking by amount

Blocking every TRANSFER or CASH_OUT above 500,000 would stop 93.74% of fraud value while blocking 11.24% of legitimate transactions. A threshold alone creates material customer friction, which is why the project adds a model for more selective decisions.
