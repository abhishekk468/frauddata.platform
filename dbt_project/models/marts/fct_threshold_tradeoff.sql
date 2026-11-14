with thresholds as (
    select unnest([0, 10000, 50000, 100000, 200000, 500000, 1000000])
        as amount_threshold
),
base as (
    select amount, is_fraud
    from {{ ref('stg_transactions') }}
    where txn_type in ('TRANSFER', 'CASH_OUT')
)
select
    t.amount_threshold,
    sum(case when b.is_fraud and b.amount > t.amount_threshold then 1 else 0 end)
        as fraud_blocked,
    sum(case when b.is_fraud then 1 else 0 end) as fraud_total,
    sum(case when not b.is_fraud and b.amount > t.amount_threshold then 1 else 0 end)
        as legit_blocked,
    sum(case when not b.is_fraud then 1 else 0 end) as legit_total,
    round(
        100.0 * sum(
            case when b.is_fraud and b.amount > t.amount_threshold then b.amount else 0 end
        ) / sum(case when b.is_fraud then b.amount else 0 end),
        2
    ) as fraud_value_blocked_pct,
    round(
        100.0 * sum(
            case when not b.is_fraud and b.amount > t.amount_threshold then 1 else 0 end
        ) / sum(case when not b.is_fraud then 1 else 0 end),
        2
    ) as legit_blocked_pct
from thresholds t
cross join base b
group by t.amount_threshold
order by t.amount_threshold
