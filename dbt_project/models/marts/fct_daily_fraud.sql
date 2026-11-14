select
    day_index,
    txn_type,
    count(*) as txn_count,
    sum(amount) as total_amount,
    sum(case when is_fraud then 1 else 0 end) as fraud_count,
    sum(case when is_fraud then amount else 0 end) as fraud_amount,
    round(
        100.0 * sum(case when is_fraud then 1 else 0 end) / count(*),
        4
    ) as fraud_rate_pct
from {{ ref('stg_transactions') }}
group by 1, 2
