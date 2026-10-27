
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run_step(description: str, command: list[str]) -> None:
    print(f"\n{'=' * 60}")
    print(description)
    print(f"{'=' * 60}")

    subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        env=os.environ.copy(),
    )


def main() -> None:
    raw_csv = ROOT / "data" / "raw" / "ai4i_2020_predictive_maintenance.csv"
    database = ROOT / "data" / "processed" / "industrialpulse.duckdb"

    # Rebuild on a fresh deployment or when the local database is absent.
    if database.exists() and raw_csv.exists():
        print(f"Warehouse already exists: {database}")
    else:
        run_step(
            "Downloading AI4I dataset",
            [PYTHON, "-m", "ingestion.download_ai4i"],
        )

        run_step(
            "Validating source dataset",
            [PYTHON, "-m", "ingestion.validate_ai4i"],
        )

        run_step(
            "Standardising source data",
            [PYTHON, "-m", "ingestion.standardize_ai4i"],
        )

        run_step(
            "Loading local DuckDB warehouse",
            [PYTHON, "-m", "ingestion.load_local_warehouse"],
        )

    run_step(
        "Building dbt models",
        [PYTHON, "-m", "dbt.cli.main", "run", "--project-dir", str(ROOT)],
    )

    print("\nIndustrialPulse warehouse is ready.")


if __name__ == "__main__":
    main()
