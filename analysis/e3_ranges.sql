select
    min(step) as min_step,
    max(step) as max_step,
    min(amount) as min_amount,
    max(amount) as max_amount
from raw.transactions;
