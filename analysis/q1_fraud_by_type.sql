select
    txn_type,
    sum(fraud_amount) as fraud_value,
    round(
        100 * sum(fraud_amount) / sum(sum(fraud_amount)) over (),
        2
    ) as pct_of_fraud_value
from main.fct_daily_fraud
group by 1
order by 2 desc
