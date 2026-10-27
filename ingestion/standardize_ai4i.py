from pathlib import Path

import pandas as pd

from ingestion.validate_ai4i import validate_dataframe


ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "ai4i_2020_predictive_maintenance.csv"
OUTPUT_FILE = ROOT / "data" / "processed" / "ai4i_machine_data.csv"

COLUMN_MAPPING = {
    "Type": "machine_type",
    "Air temperature": "air_temperature_k",
    "Process temperature": "process_temperature_k",
    "Rotational speed": "rotational_speed_rpm",
    "Torque": "torque_nm",
    "Tool wear": "tool_wear_min",
    "Machine failure": "machine_failure",
    "TWF": "tool_wear_failure",
    "HDF": "heat_dissipation_failure",
    "PWF": "power_failure",
    "OSF": "overstrain_failure",
    "RNF": "random_failure",
}


def standardize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and standardize the original AI4I records."""

    validate_dataframe(df)

    result = df.rename(columns=COLUMN_MAPPING).copy()

    # This is a reproducible row identifier, not an original machine ID.
    result.insert(
        0,
        "source_record_id",
        range(1, len(result) + 1),
    )

    result["machine_type"] = result["machine_type"].astype("string")

    integer_columns = [
        "source_record_id",
        "rotational_speed_rpm",
        "tool_wear_min",
        "machine_failure",
        "tool_wear_failure",
        "heat_dissipation_failure",
        "power_failure",
        "overstrain_failure",
        "random_failure",
    ]

    for column in integer_columns:
        result[column] = result[column].astype("int64")

    float_columns = [
        "air_temperature_k",
        "process_temperature_k",
        "torque_nm",
    ]

    for column in float_columns:
        result[column] = result[column].astype("float64")

    return result


def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {RAW_FILE}. "
            "Run ingestion/download_ai4i.py first."
        )

    raw = pd.read_csv(RAW_FILE)
    standardized = standardize_dataframe(raw)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    standardized.to_csv(OUTPUT_FILE, index=False)

    print("STANDARDIZATION SUCCEEDED")
    print(f"Input rows: {len(raw):,}")
    print(f"Output rows: {len(standardized):,}")
    print(f"Output columns: {len(standardized.columns)}")
    print(f"Output file: {OUTPUT_FILE}")
    print("\nStandardized schema:")
    print(standardized.dtypes.to_string())
    print("\nPreview:")
    print(standardized.head().to_string(index=False))


if __name__ == "__main__":
    main()
