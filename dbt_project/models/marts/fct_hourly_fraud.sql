select
    hour_of_day,
    count(*) as txn_count,
    sum(case when is_fraud then 1 else 0 end) as fraud_count,
    round(
        100.0 * sum(case when is_fraud then 1 else 0 end) / count(*),
        4
    ) as fraud_rate_pct
from {{ ref('stg_transactions') }}
where txn_type in ('TRANSFER', 'CASH_OUT')
group by 1
order by 1
