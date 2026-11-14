import argparse
import time
from pathlib import Path

import duckdb


CSV = Path("data/raw/paysim.csv").as_posix()
DB = "warehouse.duckdb"
LAST_DAY = 30


def setup(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("create schema if not exists raw")
    con.execute(
        f"""
        create table if not exists raw.transactions as
        select *, 0 as load_day
        from read_csv_auto('{CSV}')
        limit 0
        """
    )


def load_day(con: duckdb.DuckDBPyConnection, day: int) -> int:
    lo, hi = day * 24 + 1, (day + 1) * 24
    con.execute("delete from raw.transactions where load_day = ?", [day])
    con.execute(
        f"""
        insert into raw.transactions
        select *, {day} as load_day
        from read_csv_auto('{CSV}')
        where step between {lo} and {hi}
        """
    )
    return con.execute(
        "select count(*) from raw.transactions where load_day = ?", [day]
    ).fetchone()[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--day", type=int)
    group.add_argument("--all", action="store_true")
    args = parser.parse_args()

    days = range(LAST_DAY + 1) if args.all else [args.day]
    if not args.all and not 0 <= args.day <= LAST_DAY:
        parser.error(f"--day must be between 0 and {LAST_DAY}")

    con = duckdb.connect(DB)
    try:
        setup(con)
        for day in days:
            t0 = time.time()
            count = load_day(con, day)
            print(f"day {day:02d}: {count:>9,} rows in {time.time() - t0:.1f}s")

        total = con.execute("select count(*) from raw.transactions").fetchone()[0]
        print(f"total rows in raw.transactions: {total:,}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
