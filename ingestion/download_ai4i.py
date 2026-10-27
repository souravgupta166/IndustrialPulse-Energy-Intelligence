from pathlib import Path

import pandas as pd
from ucimlrepo import fetch_ucirepo


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_FILE = RAW_DIR / "ai4i_2020_predictive_maintenance.csv"


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("Fetching UCI AI4I 2020 Predictive Maintenance dataset...")
    dataset = fetch_ucirepo(id=601)

    features = dataset.data.features
    targets = dataset.data.targets

    if features is None or targets is None:
        raise RuntimeError("The dataset did not return both features and targets.")

    data = pd.concat(
        [
            features.reset_index(drop=True),
            targets.reset_index(drop=True),
        ],
        axis=1,
    )

    if data.empty:
        raise RuntimeError("The downloaded dataset is empty.")

    if data.columns.duplicated().any():
        raise ValueError("Duplicate column names found in downloaded data.")

    data.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved dataset: {OUTPUT_FILE}")
    print(f"Rows: {len(data):,}")
    print(f"Columns: {len(data.columns)}")
    print("\nColumn names:")
    print(data.columns.tolist())
    print("\nMissing values:")
    print(data.isna().sum().to_string())
    print("\nPreview:")
    print(data.head().to_string(index=False))


if __name__ == "__main__":
    main()
