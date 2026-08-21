import sys
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = ["customer_id", "order_id", "amount", "date", "segment"]
MIN_ROWS = 100


def validate(file_path: str, min_rows: int = MIN_ROWS) -> int:
    """Run all validation checks. Return 0 on success and 1 on failure."""
    print(f"Validating: {file_path}")
    path = Path(file_path)

    if not path.exists():
        print(f"ERROR: File not found: {path}")
        return 1

    try:
        df = pd.read_csv(path)
    except Exception as exc:  # pragma: no cover - runtime guard
        print(f"ERROR: Could not read CSV: {exc}")
        return 1

    errors = []

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {missing}")
    else:
        print("PASS: All required columns present")

    if "amount" in df.columns:
        if not pd.api.types.is_numeric_dtype(df["amount"]):
            errors.append("Column 'amount' is not numeric")
        else:
            print("PASS: amount column is numeric")

    if len(df) < min_rows:
        errors.append(f"Row count {len(df)} below minimum {min_rows}")
    else:
        print(f"PASS: Row count {len(df)} meets minimum")

    null_cols = [column for column in df.columns if df[column].isnull().all()]
    if null_cols:
        errors.append(f"Fully null columns: {null_cols}")
    else:
        print("PASS: No fully null columns")

    if errors:
        print("\nVALIDATION FAILED:")
        for error in errors:
            print(f"  ERROR: {error}")
        return 1

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_data.py <csv_path>")
        raise SystemExit(1)
    raise SystemExit(validate(sys.argv[1]))
