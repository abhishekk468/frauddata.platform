select
    txn_id,
    step,
    is_fraud,
    amount,
    case when txn_type = 'TRANSFER' then 1 else 0 end as is_transfer,
    hour_of_day,
    sender_balance_before as oldbalance_org,
    receiver_balance_before as oldbalance_dest,
    case
        when sender_balance_before > 0
            then least(amount / sender_balance_before, 10)
        else -1
    end as drain_ratio,
    case
        when sender_balance_before > 0 and amount >= sender_balance_before
            then 1
        else 0
    end as drains_account,
    case when receiver_balance_before = 0 then 1 else 0 end as dest_balance_zero,
    count(*) over (
        partition by receiver_id
        order by step, txn_id
        rows between unbounded preceding and 1 preceding
    ) as dest_prev_txn_count,
    sender_balance_after as newbalance_org,
    receiver_balance_after as newbalance_dest
from {{ ref('stg_transactions') }}
where txn_type in ('TRANSFER', 'CASH_OUT')
