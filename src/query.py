import sys
from pathlib import Path

import duckdb
import pandas as pd


pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python src/query.py '<sql>'|<file.sql>")

    argument = sys.argv[1]
    sql = Path(argument).read_text() if argument.endswith(".sql") else argument

    con = duckdb.connect("warehouse.duckdb", read_only=True)
    try:
        print(con.execute(sql).df().to_string(index=False))
    finally:
        con.close()


if __name__ == "__main__":
    main()
