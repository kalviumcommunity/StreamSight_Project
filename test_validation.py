import pandas as pd

from data_validation import analyze_missing_before, impute_missing_values
from process_sales import process_data


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


def test_process_data_adds_temporal_features():
    df = pd.DataFrame(
        {
            "customer_id": [1, 2],
            "transaction_date": ["2025-01-15", "2025-01-16"],
            "amount": [100.0, 80.0],
            "product_category": ["Electronics", "Books"],
        }
    )

    processed_df = process_data(df, min_amount=0)

    assert "day_of_week" in processed_df.columns
    assert "hour_of_day" in processed_df.columns
    assert "week_number" in processed_df.columns
    assert "days_since_purchase" in processed_df.columns
    assert processed_df.loc[0, "day_of_week"] == "Wednesday"
    assert processed_df.loc[0, "hour_of_day"] == 0
    assert processed_df.loc[0, "dow_numeric"] == 2
