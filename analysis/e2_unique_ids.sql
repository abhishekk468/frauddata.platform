select
    count(*) as total_rows,
    count(distinct nameOrig) as unique_senders,
    count(distinct nameDest) as unique_receivers
from raw.transactions;
