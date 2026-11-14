select
    row_number() over (
        order by step, nameorig, namedest, amount, oldbalanceorg
    ) as txn_id,
    step,
    (step - 1) // 24 as day_index,
    (step - 1) % 24 as hour_of_day,
    type as txn_type,
    amount,
    nameorig as sender_id,
    namedest as receiver_id,
    oldbalanceorg as sender_balance_before,
    newbalanceorig as sender_balance_after,
    oldbalancedest as receiver_balance_before,
    newbalancedest as receiver_balance_after,
    isfraud = 1 as is_fraud
from {{ source('raw', 'transactions') }}
