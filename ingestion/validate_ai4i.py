
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "ai4i_2020_predictive_maintenance.csv"
MANIFEST_FILE = ROOT / "data" / "raw" / "ai4i_manifest.json"

EXPECTED_COLUMNS = [
    "Type",
    "Air temperature",
    "Process temperature",
    "Rotational speed",
    "Torque",
    "Tool wear",
    "Machine failure",
    "TWF",
    "HDF",
    "PWF",
    "OSF",
    "RNF",
]

BINARY_COLUMNS = [
    "Machine failure",
    "TWF",
    "HDF",
    "PWF",
    "OSF",
    "RNF",
]

NUMERIC_COLUMNS = [
    "Air temperature",
    "Process temperature",
    "Rotational speed",
    "Torque",
    "Tool wear",
]


def validate_dataframe(
    df: pd.DataFrame,
    expected_rows: int | None = None,
) -> None:
    """Validate AI4I schema, values, and data-quality rules."""

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if list(df.columns) != EXPECTED_COLUMNS:
        raise ValueError(
            f"Unexpected schema. Expected {EXPECTED_COLUMNS}; "
            f"received {list(df.columns)}"
        )

    if expected_rows is not None and len(df) != expected_rows:
        raise ValueError(
            f"Expected {expected_rows:,} rows; received {len(df):,}"
        )

    if df.empty:
        raise ValueError("Dataset is empty")

    if df.isna().any().any():
        missing = df.columns[df.isna().any()].tolist()
        raise ValueError(f"Missing values detected in: {missing}")

    if not df["Type"].isin(["L", "M", "H"]).all():
        raise ValueError("Unexpected machine type")

    for column in NUMERIC_COLUMNS:
        values = pd.to_numeric(df[column], errors="coerce")

        if values.isna().any():
            raise ValueError(f"{column} contains non-numeric values")

        if not values.map(math.isfinite).all():
            raise ValueError(f"{column} contains non-finite values")

        if (values < 0).any():
            raise ValueError(f"{column} contains negative values")

    if (df["Rotational speed"] <= 0).any():
        raise ValueError("Rotational speed must be greater than zero")

    for column in BINARY_COLUMNS:
        if not df[column].isin([0, 1]).all():
            raise ValueError(f"{column} must contain only 0 or 1")


def sha256_file(path: Path) -> str:
    """Calculate a file's SHA-256 checksum."""

    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def main() -> None:
    """Validate the downloaded dataset and generate a manifest."""

    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {RAW_FILE}. "
            "Run ingestion.download_ai4i first."
        )

    df = pd.read_csv(RAW_FILE)

    # Enforce the expected source dataset size.
    validate_dataframe(df, expected_rows=10_000)

    manifest = {
        "dataset": "AI4I 2020 Predictive Maintenance",
        "source": "UCI Machine Learning Repository",
        "source_url": (
            "https://archive.ics.uci.edu/dataset/601/"
            "ai4i+2020+predictive+maintenance+dataset"
        ),
        "dataset_id": 601,
        "data_character": (
            "Synthetic predictive-maintenance dataset; "
            "not live factory telemetry"
        ),
        "file": RAW_FILE.name,
        "sha256": sha256_file(RAW_FILE),
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "missing_values": int(df.isna().sum().sum()),
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "validation_status": "passed",
    }

    MANIFEST_FILE.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    print("DATA QUALITY VALIDATION PASSED")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Missing values: {df.isna().sum().sum()}")
    print(f"SHA-256: {manifest['sha256']}")
    print(f"Manifest: {MANIFEST_FILE}")


if __name__ == "__main__":
    main()
