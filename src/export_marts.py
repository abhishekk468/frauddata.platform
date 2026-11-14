from pathlib import Path

import duckdb


OUT = Path("dashboard_data")
TABLES = ["fct_daily_fraud", "fct_hourly_fraud", "fct_threshold_tradeoff"]


def main() -> None:
    OUT.mkdir(exist_ok=True)
    con = duckdb.connect("warehouse.duckdb", read_only=True)
    try:
        for table in TABLES:
            path = (OUT / f"{table}.parquet").as_posix()
            con.execute(
                f"copy (select * from main.{table}) to '{path}' (format parquet)"
            )
            print("exported", path)
    finally:
        con.close()


if __name__ == "__main__":
    main()
