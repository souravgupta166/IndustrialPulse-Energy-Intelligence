import pandas as pd

from ingestion.standardize_ai4i import standardize_dataframe


def test_standardization_preserves_rows_and_values():
    raw = pd.DataFrame(
        {
            "Type": ["L", "M"],
            "Air temperature": [298.1, 299.0],
            "Process temperature": [308.6, 309.0],
            "Rotational speed": [1500, 1600],
            "Torque": [40.0, 35.0],
            "Tool wear": [10, 20],
            "Machine failure": [0, 1],
            "TWF": [0, 1],
            "HDF": [0, 0],
            "PWF": [0, 0],
            "OSF": [0, 0],
            "RNF": [0, 0],
        }
    )

    result = standardize_dataframe(raw)

    assert len(result) == 2
    assert result["source_record_id"].tolist() == [1, 2]
    assert result["machine_type"].tolist() == ["L", "M"]
    assert result["air_temperature_k"].tolist() == [298.1, 299.0]
    assert result["machine_failure"].tolist() == [0, 1]


def test_standardized_columns_are_snake_case():
    raw = pd.DataFrame(
        {
            "Type": ["L"],
            "Air temperature": [298.1],
            "Process temperature": [308.6],
            "Rotational speed": [1500],
            "Torque": [40.0],
            "Tool wear": [10],
            "Machine failure": [0],
            "TWF": [0],
            "HDF": [0],
            "PWF": [0],
            "OSF": [0],
            "RNF": [0],
        }
    )

    result = standardize_dataframe(raw)

    assert "machine_type" in result.columns
    assert "air_temperature_k" in result.columns
    assert "Air temperature" not in result.columns
