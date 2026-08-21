import tempfile
from pathlib import Path

import pandas as pd

from validate_data import validate


def test_validate_passes_for_expected_schema_and_quality():
    df = pd.DataFrame(
        {
            "customer_id": list(range(1, 121)),
            "order_id": list(range(1001, 1121)),
            "amount": [float(i) for i in range(10, 130)],
            "date": pd.date_range("2024-01-01", periods=120, freq="D").astype(str),
            "segment": ["A", "B", "A", "C", "A", "B", "A", "C", "B", "A"] * 12,
        }
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "cleaned_data.csv"
        df.to_csv(path, index=False)

        assert validate(str(path)) == 0


def test_validate_fails_when_required_columns_are_missing():
    df = pd.DataFrame({"customer_id": [1, 2, 3], "amount": [10.0, 20.0, 30.0]})

    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "broken_data.csv"
        df.to_csv(path, index=False)

        assert validate(str(path)) == 1
