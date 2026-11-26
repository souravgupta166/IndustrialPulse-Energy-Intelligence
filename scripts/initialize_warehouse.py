from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = ROOT / "data" / "raw" / "ai4i_2020_predictive_maintenance.csv"
DATABASE = ROOT / "data" / "processed" / "industrialpulse.duckdb"
PROFILES_DIR = ROOT / ".dbt_profiles"
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "warehouse_initialization.log"


def write_log(message: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(message.rstrip() + "\n")


def run_step(label: str, command: list[str], timeout: int = 900) -> str:
    print(f"\n{'=' * 72}\n{label}\n{'=' * 72}", flush=True)
    write_log(f"\n{'=' * 72}\n{label}\nCOMMAND: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        write_log(output)
        raise RuntimeError(
            f"{label} timed out after {timeout} seconds.\n{output}"
        ) from exc

    output = result.stdout or ""
    print(output, flush=True)
    write_log(output)

    if result.returncode != 0:
        raise RuntimeError(
            f"{label} failed with exit code {result.returncode}.\n"
            f"Full output saved in {LOG_FILE}.\n\n{output[-14000:]}"
        )

    return output


def create_profile() -> None:
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE.parent.mkdir(parents=True, exist_ok=True)

    database_path = DATABASE.resolve().as_posix()
    profile_text = (
        "industrialpulse:\n"
        "  target: dev\n"
        "  outputs:\n"
        "    dev:\n"
        "      type: duckdb\n"
        f"      path: '{database_path}'\n"
        "      schema: main\n"
        "      threads: 4\n"
    )

    profile_file = PROFILES_DIR / "profiles.yml"
    profile_file.write_text(profile_text, encoding="utf-8")
    print(f"Created dbt profile: {profile_file}", flush=True)


def dbt_command(*args: str) -> list[str]:
    dbt_executable = shutil.which("dbt")

    if dbt_executable:
        return [
            dbt_executable, *args,
            "--project-dir", str(ROOT),
            "--profiles-dir", str(PROFILES_DIR),
            "--no-use-colors",
        ]

    return [
        sys.executable, "-m", "dbt.cli.main", *args,
        "--project-dir", str(ROOT),
        "--profiles-dir", str(PROFILES_DIR),
        "--no-use-colors",
    ]


def run_dbt(*args: str) -> None:
    run_step(f"dbt {' '.join(args)}", dbt_command(*args))


def main() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.write_text(
        "IndustrialPulse warehouse initialization log\n",
        encoding="utf-8",
    )

    required_files = [
        ROOT / "dbt_project.yml",
        ROOT / "ingestion" / "download_ai4i.py",
        ROOT / "ingestion" / "validate_ai4i.py",
        ROOT / "ingestion" / "standardize_ai4i.py",
        ROOT / "ingestion" / "load_local_warehouse.py",
        ROOT / "models" / "staging" / "sources.yml",
    ]

    missing_files = [str(path) for path in required_files if not path.exists()]
    if missing_files:
        raise FileNotFoundError(
            "Required project files are missing:\n" + "\n".join(missing_files)
        )

    create_profile()

    if not RAW_CSV.exists():
        run_step(
            "Downloading UCI AI4I dataset",
            [sys.executable, "-m", "ingestion.download_ai4i"],
            timeout=600,
        )

    run_step(
        "Validating source dataset",
        [sys.executable, "-m", "ingestion.validate_ai4i"],
    )
    run_step(
        "Standardising source dataset",
        [sys.executable, "-m", "ingestion.standardize_ai4i"],
    )
    run_step(
        "Loading DuckDB raw table",
        [sys.executable, "-m", "ingestion.load_local_warehouse"],
    )

    if not DATABASE.exists():
        raise FileNotFoundError(f"DuckDB database was not created: {DATABASE}")

    run_dbt("debug")
    run_dbt("run", "--no-partial-parse")
    run_dbt("test", "--no-partial-parse")

    import duckdb

    with duckdb.connect(str(DATABASE), read_only=True) as connection:
        observation_count = connection.execute(
            "SELECT COUNT(*) FROM main.int_machine_observations"
        ).fetchone()[0]
        mart_count = connection.execute(
            "SELECT COUNT(*) FROM main.mart_maintenance_kpis"
        ).fetchone()[0]

    if observation_count <= 0 or mart_count <= 0:
        raise RuntimeError(
            f"Warehouse verification failed: observations={observation_count}, "
            f"KPI rows={mart_count}"
        )

    success_message = (
        "\nWAREHOUSE INITIALISATION SUCCEEDED\n"
        f"Observations: {observation_count:,}\n"
        f"KPI rows: {mart_count:,}\n"
    )
    print(success_message, flush=True)
    write_log(success_message)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        error_message = (
            "\nWAREHOUSE INITIALISATION FAILED\n"
            f"{type(exc).__name__}: {exc}\n"
        )
        print(error_message, file=sys.stderr, flush=True)
        write_log(error_message)
        raise
