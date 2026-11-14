select
    case
        when amount < 10000 then '1_under_10k'
        when amount < 100000 then '2_10k_to_100k'
        when amount < 500000 then '3_100k_to_500k'
        else '4_over_500k'
    end as amount_band,
    count(*) as txns,
    sum(case when is_fraud then 1 else 0 end) as fraud,
    round(
        100.0 * avg(case when is_fraud then 1.0 else 0.0 end),
        3
    ) as fraud_rate_pct
from main.stg_transactions
where txn_type in ('TRANSFER', 'CASH_OUT')
group by 1
order by 1
