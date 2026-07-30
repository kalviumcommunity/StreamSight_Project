import pandas as pd

from data_validation import analyze_missing_before, impute_missing_values


def test_analyze_missing_before_reports_null_summary():
    df = pd.DataFrame(
        {
            "customer_id": [1, None, 3],
            "amount": [100.0, None, 300.0],
            "product_category": ["Books", None, "Books"],
            "transaction_date": ["2025-01-01", None, "2025-01-03"],
        }
    )

    summary = analyze_missing_before(df)

    assert summary["total_rows"] == 3
    assert summary["missing_values"]["amount"] == 1
    assert summary["missing_values"]["product_category"] == 1
    assert summary["missing_values"]["transaction_date"] == 1


def test_impute_missing_values_applies_strategy_per_column():
    df = pd.DataFrame(
        {
            "customer_id": [1, None, 3],
            "amount": [100.0, None, 300.0],
            "product_category": ["Books", None, "Books"],
            "transaction_date": ["2025-01-01", None, "2025-01-03"],
        }
    )

    cleaned_df, audit_log = impute_missing_values(df, critical_columns=["customer_id"])

    assert len(cleaned_df) == 2
    assert cleaned_df["amount"].isna().sum() == 0
    assert cleaned_df["product_category"].isna().sum() == 0
    assert cleaned_df["transaction_date"].isna().sum() == 0
    assert any(entry["strategy"] == "drop_rows" for entry in audit_log)
    assert any(entry["strategy"] == "median" for entry in audit_log)
    assert any(entry["strategy"] == "mode" for entry in audit_log)
    assert any(entry["strategy"] == "forward_fill" for entry in audit_log)
