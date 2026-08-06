import pandas as pd
import os


# Create output directory


os.makedirs("output", exist_ok=True)


# Load data
df = pd.read_csv(

    
    "data/engagement_data.csv"
)

print("Data loaded successfully")
print(f"Total records: {len(df)}")


# Convert date
df["transaction_date"] = pd.to_datetime(
    df["transaction_date"],
    format="%Y-%m-%d",
    errors="coerce"
)


# Optional feature engineering utilities (safe no-op if columns missing)
try:
    from feature_engineering import (
        transactions_per_month,
        avg_spend_per_transaction,
        lifetime_value_per_month,
        engagement_bin,
        spend_tier_quantile,
        compute_rfm,
    )
except Exception:
    transactions_per_month = None


# Example: compute common ratio features only when source columns exist
if transactions_per_month is not None and {'total_transactions', 'days_as_customer'}.issubset(df.columns):
    df['transactions_per_month'] = transactions_per_month(df)

if transactions_per_month is not None and {'total_spent', 'total_transactions'}.issubset(df.columns):
    df['avg_spend_per_transaction'] = avg_spend_per_transaction(df)



# ==============================
# VALIDATION RULES
# ==============================

# Null checks
df["valid_user_id"] = df["user_id"].notna()

df["valid_video_id"] = df["video_id"].notna()


# Range checks
df["valid_watch_duration"] = (
    df["watch_duration"] >= 0
)

df["valid_pause_count"] = (
    df["pause_count"] >= 0
)

df["valid_completion_rate"] = (
    (df["completion_rate"] >= 0) &
    (df["completion_rate"] <= 100)
)

df["valid_amount"] = (
    df["amount"] >= 0
)


# Business rule
today = pd.Timestamp.today().normalize()

df["valid_transaction_date"] = (
    df["transaction_date"] <= today
)


# ==============================
# COMBINE VALIDATION RESULTS
# ==============================

validation_cols = [
    "valid_user_id",
    "valid_video_id",
    "valid_watch_duration",
    "valid_pause_count",
    "valid_completion_rate",
    "valid_transaction_date",
    "valid_amount"
]

df["passes_all_checks"] = (
    df[validation_cols].all(axis=1)
)


# ==============================
# ISOLATE FAILURES
# ==============================

failures = df[
    ~df["passes_all_checks"]
]

clean_data = df[
    df["passes_all_checks"]
]


# ==============================
# SAVE OUTPUT
# ==============================

failures.to_csv(
    "output/validation_failures.csv",
    index=False
)

clean_data.to_csv(
    "output/validated_engagement_data.csv",
    index=False
)


# ==============================
# REPORT
# ==============================

print("\n==============================")
print("VALIDATION REPORT")
print("==============================")

print(f"Total Records : {len(df)}")
print(f"Passed        : {len(clean_data)}")
print(f"Failed        : {len(failures)}")


print("\nRule Results:")

for column in validation_cols:

    passed = df[column].sum()

    failed = len(df) - passed

    print(
        f"{column}: "
        f"Passed={passed}, "
        f"Failed={failed}"
    )


print("\nOutput files created:")
print("- output/validation_failures.csv")
print("- output/validated_engagement_data.csv")

# Optional segment aggregation insights
try:
    from segment_analysis import build_segment_summary, build_pivot_table, write_segment_insights
except Exception:
    build_segment_summary = None

if build_segment_summary is not None:
    try:
        # Use a best-effort approach: if the cleaned data has the expected business columns,
        # create segment summary and pivot insights.
        if {'customer_type', 'product_category', 'amount', 'customer_id'}.issubset(clean_data.columns):
            write_segment_insights(clean_data, output_path='output/segment_insights.txt')
            print("Segment insights written to output/segment_insights.txt")
        else:
            print("Segment insights skipped: expected business columns are missing")
    except Exception as exc:
        print(f"Segment insights skipped: {exc}")