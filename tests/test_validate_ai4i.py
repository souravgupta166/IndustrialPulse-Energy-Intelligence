
import pandas as pd
import pytest

from ingestion.validate_ai4i import (
    EXPECTED_COLUMNS,
    validate_dataframe,
)


@pytest.fixture
def valid_dataframe():
    """Create a valid 10,000-row dataset for validation tests."""
    return pd.DataFrame(
        {
            "Type": ["L"] * 10_000,
            "Air temperature": [298.1] * 10_000,
            "Process temperature": [308.6] * 10_000,
            "Rotational speed": [1500] * 10_000,
            "Torque": [40.0] * 10_000,
            "Tool wear": [10] * 10_000,
            "Machine failure": [0] * 10_000,
            "TWF": [0] * 10_000,
            "HDF": [0] * 10_000,
            "PWF": [0] * 10_000,
            "OSF": [0] * 10_000,
            "RNF": [0] * 10_000,
        },
        columns=EXPECTED_COLUMNS,
    )


def test_valid_dataset_passes(valid_dataframe):
    """A valid dataset should pass validation."""
    validate_dataframe(valid_dataframe)


def test_missing_values_fail(valid_dataframe):
    """Missing values should be rejected."""
    valid_dataframe.loc[0, "Torque"] = float("nan")

    with pytest.raises(ValueError, match="Missing values"):
        validate_dataframe(valid_dataframe)


def test_invalid_failure_label_fails(valid_dataframe):
    """Binary failure labels must be zero or one."""
    valid_dataframe.loc[0, "Machine failure"] = 2

    with pytest.raises(ValueError, match="Machine failure"):
        validate_dataframe(valid_dataframe)


def test_invalid_machine_type_fails(valid_dataframe):
    """Machine type must be L, M, or H."""
    valid_dataframe.loc[0, "Type"] = "X"

    with pytest.raises(ValueError, match="machine type"):
        validate_dataframe(valid_dataframe)


def test_negative_torque_fails(valid_dataframe):
    """Negative torque must be rejected."""
    valid_dataframe.loc[0, "Torque"] = -1

    with pytest.raises(ValueError, match="negative values"):
        validate_dataframe(valid_dataframe)


def test_expected_row_count_is_enforced(valid_dataframe):
    """The source-specific row-count contract must be enforced."""
    with pytest.raises(ValueError, match="Expected 10,000 rows"):
        validate_dataframe(
            valid_dataframe.iloc[:5].copy(),
            expected_rows=10_000,
        )


def test_unexpected_column_fails(valid_dataframe):
    """An unexpected schema must be rejected."""
    valid_dataframe["unexpected_column"] = 1

    with pytest.raises(ValueError, match="Unexpected schema"):
        validate_dataframe(valid_dataframe)
