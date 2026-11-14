import duckdb


con = duckdb.connect("warehouse.duckdb")
try:
    con.execute("update raw.transactions set amount = -1 where step = 1")
finally:
    con.close()

print("corrupted step 1: amounts set to -1")
