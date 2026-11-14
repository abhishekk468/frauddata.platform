select txn_id
from {{ ref('stg_transactions') }}
where is_fraud
  and txn_type not in ('TRANSFER', 'CASH_OUT')
