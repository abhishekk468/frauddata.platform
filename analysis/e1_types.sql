select
    type,
    count(*) as n,
    sum(isFraud) as fraud
from raw.transactions
group by 1
order by 2 desc;
