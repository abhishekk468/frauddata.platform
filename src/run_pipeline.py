import subprocess
import sys


def run(command: list[str], cwd: str | None = None) -> None:
    print(">>", " ".join(command))
    result = subprocess.run(command, cwd=cwd)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    run([sys.executable, "src/ingest.py", "--all"])
    run([sys.executable, "-m", "dbt.cli.main", "build", "--profiles-dir", "."], cwd="dbt_project")
    run([sys.executable, "src/export_marts.py"])
    run([sys.executable, "src/train.py"])
    print("pipeline finished")


if __name__ == "__main__":
    main()
