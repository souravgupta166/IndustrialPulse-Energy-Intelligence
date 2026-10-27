
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
CSV_FILE = ROOT / "data" / "processed" / "ai4i_machine_data.csv"
DB_FILE = ROOT / "data" / "processed" / "industrialpulse.duckdb"
TABLE_NAME = "raw_ai4i_machine_data"


def main() -> None:
    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"Standardized CSV not found: {CSV_FILE}. "
            "Run ingestion.standardize_ai4i first."
        )

    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    connection = duckdb.connect(str(DB_FILE))

    try:
        connection.execute(
            """
            CREATE OR REPLACE TABLE main.raw_ai4i_machine_data AS
            SELECT *
            FROM read_csv_auto(?)
            """,
            [str(CSV_FILE)],
        )

        row_count = connection.execute(
            f"SELECT COUNT(*) FROM main.{TABLE_NAME}"
        ).fetchone()[0]

        distinct_ids = connection.execute(
            f"SELECT COUNT(DISTINCT source_record_id) "
            f"FROM main.{TABLE_NAME}"
        ).fetchone()[0]

        null_ids = connection.execute(
            f"SELECT COUNT(*) FROM main.{TABLE_NAME} "
            "WHERE source_record_id IS NULL"
        ).fetchone()[0]

        if row_count != 10_000:
            raise ValueError(f"Expected 10,000 rows; found {row_count}")

        if distinct_ids != row_count:
            raise ValueError("Source record IDs are not unique")

        if null_ids != 0:
            raise ValueError("Null source record IDs found")

        columns = connection.execute(
            f"DESCRIBE main.{TABLE_NAME}"
        ).fetchall()

        print("LOCAL WAREHOUSE LOAD SUCCEEDED")
        print(f"Database: {DB_FILE}")
        print(f"Table: main.{TABLE_NAME}")
        print(f"Rows: {row_count:,}")
        print(f"Distinct record IDs: {distinct_ids:,}")
        print(f"Null record IDs: {null_ids}")
        print("\nTable schema:")

        for column in columns:
            print(f"  {column[0]}: {column[1]}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
