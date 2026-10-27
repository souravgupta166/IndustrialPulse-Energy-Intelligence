
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

RAW_CSV = ROOT / "data" / "raw" / "ai4i_2020_predictive_maintenance.csv"
STANDARDIZED_CSV = ROOT / "data" / "processed" / "ai4i_machine_data.csv"
DATABASE = ROOT / "data" / "processed" / "industrialpulse.duckdb"

# A project-local profile directory works in Linux and Windows.
PROFILES_DIR = ROOT / ".dbt_profiles"


def run_step(description: str, command: list[str]) -> None:
    """Run a pipeline step and show its output on failure."""

    print(f"\n{'=' * 60}\n{description}\n{'=' * 60}")

    result = subprocess.run(
        command,
        cwd=ROOT,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )

    if result.stdout:
        print(result.stdout)

    if result.returncode != 0:
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        raise RuntimeError(
            f"{description} failed with exit code {result.returncode}"
        )

    if result.stderr:
        # Preserve warnings without treating them as failures.
        print(result.stderr, file=sys.stderr)


def create_dbt_profile() -> None:
    """Create a DuckDB profile for this deployment environment."""

    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE.parent.mkdir(parents=True, exist_ok=True)

    # Use forward slashes so the path works with dbt on Windows too.
    database_path = DATABASE.resolve().as_posix()

    profile = f"""industrialpulse:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: '{database_path}'
      schema: main
      threads: 4
"""

    (PROFILES_DIR / "profiles.yml").write_text(
        profile,
        encoding="utf-8",
    )

    print(f"Created dbt profile: {PROFILES_DIR / 'profiles.yml'}")
    print(f"DuckDB database: {DATABASE}")


def run_dbt(*arguments: str) -> None:
    """Run dbt with the explicitly configured project and profile."""

    run_step(
        f"dbt {' '.join(arguments)}",
        [
            PYTHON,
            "-m",
            "dbt.cli.main",
            *arguments,
            "--project-dir",
            str(ROOT),
            "--profiles-dir",
            str(PROFILES_DIR),
        ],
    )


def main() -> None:
    """Download, validate, standardise, load, and transform the dataset."""

    create_dbt_profile()

    if not RAW_CSV.exists():
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

    # Always reload so the warehouse matches the current processed CSV.
    run_step(
        "Loading local DuckDB warehouse",
        [PYTHON, "-m", "ingestion.load_local_warehouse"],
    )

    run_dbt("debug")
    run_dbt("run")
    run_dbt("test")

    print("\nIndustrialPulse warehouse initialisation completed successfully.")


if __name__ == "__main__":
    main()
