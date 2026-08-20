import tempfile
from pathlib import Path

import pandas as pd

from streamlit_app import load_default_data


def test_load_default_data_parses_transaction_dates():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "validated.csv"
        pd.DataFrame(
            {"transaction_date": ["2026-01-01"], "amount": [100.0]}
        ).to_csv(path, index=False)

        loaded = load_default_data.__wrapped__(path)

        assert pd.api.types.is_datetime64_any_dtype(loaded["transaction_date"])
        assert loaded.loc[0, "amount"] == 100.0