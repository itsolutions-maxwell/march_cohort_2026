"""
Runs every .sql file in a folder against BigQuery, in filename order (which
is why the raw/silver/gold files are numbered — 01_, 02_, ... controls
execution order, e.g. silver/05_encounters.sql depends on silver/02 and
silver/03 already existing).

Usage (from the hospital-analytics/ directory, with GCP credentials
available via `gcloud auth application-default login` or
GOOGLE_APPLICATION_CREDENTIALS):

    python -m bigquery.run_sql_folder raw
    python -m bigquery.run_sql_folder silver
    python -m bigquery.run_sql_folder gold
    python -m bigquery.run_sql_folder bigquery/sql_queries/gold   # a full path works too

Each file's contents are sent to BigQuery as one query, so a file with
several ;-separated statements (like 00_create_datasets.sql) runs as a
single multi-statement script.
"""

import argparse
import sys
from pathlib import Path

from google.cloud import bigquery

from app.config import settings

SQL_QUERIES_DIR = Path(__file__).parent / "sql_queries"


def resolve_folder(name: str) -> Path:
    as_path = Path(name)
    if as_path.is_dir():
        return as_path

    under_sql_queries = SQL_QUERIES_DIR / name
    if under_sql_queries.is_dir():
        return under_sql_queries

    raise SystemExit(f"No such folder: {name!r} (looked in . and {SQL_QUERIES_DIR})")


def run_folder(folder: Path) -> bool:
    sql_files = sorted(folder.glob("*.sql"))
    if not sql_files:
        print(f"No .sql files found in {folder}")
        return True

    client = bigquery.Client(project=settings.gcp_project_id)
    all_ok = True

    for path in sql_files:
        sql = path.read_text()
        try:
            client.query(sql).result()
            print(f"  OK: {path.name}")
        except Exception as exc:  # noqa: BLE001 — report and keep going
            all_ok = False
            print(f"  FAILED: {path.name}\n    {exc}")

    return all_ok


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", help="Folder name under bigquery/sql_queries/ (e.g. raw, silver, gold), or a path")
    args = parser.parse_args()

    folder = resolve_folder(args.folder)
    print(f"Running {folder}:")
    ok = run_folder(folder)

    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
