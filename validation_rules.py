"""Reusable validation rules for engagement data."""

import json
from pathlib import Path

import pandas as pd


def _require_dataframe(df):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame")


def validate_range(series, minimum=None, maximum=None):
    """Return a boolean mask for values inside an inclusive range."""
    result = series.notna()
    if minimum is not None:
        result &= series >= minimum
    if maximum is not None:
        result &= series <= maximum
    return result


def validate_not_null(series):
    """Return a boolean mask for required values, including non-empty strings."""
    return series.notna() & series.astype("string").str.strip().ne("")


def validate_pattern(series, pattern):
    """Return a boolean mask for values matching a regular expression."""
    return series.astype("string").str.fullmatch(pattern, na=False)


def validate_referential_integrity(series, valid_values):
    """Return a boolean mask for foreign keys found in the reference values."""
    return series.notna() & series.isin(set(valid_values))


def apply_validation_rules(df, reference_ids=None, today=None):
    """Apply validation rules and return the annotated frame and rule columns."""
    _require_dataframe(df)
    validated = df.copy()
    today = pd.Timestamp.today().normalize() if today is None else pd.Timestamp(today)
    rule_columns = []

    def add_rule(name, mask):
        validated[name] = mask.fillna(False).astype(bool)
        rule_columns.append(name)

    for column in ("user_id", "video_id", "customer_id"):
        if column in validated:
            add_rule(f"valid_{column}", validate_not_null(validated[column]))

    ranges = {
        "watch_duration": (0, None),
        "pause_count": (0, None),
        "completion_rate": (0, 100),
        "amount": (0, None),
        "price": (0, None),
    }
    for column, (minimum, maximum) in ranges.items():
        if column in validated:
            add_rule(f"valid_{column}", validate_range(validated[column], minimum, maximum))

    if "email" in validated:
        add_rule("valid_email_format", validate_pattern(validated["email"], r"[^@\s]+@[^@\s]+\.[^@\s]+"))
    if "phone" in validated:
        add_rule("valid_phone_format", validate_pattern(validated["phone"], r"\d{10}"))
    if "product_category" in validated:
        add_rule("valid_product_category", validate_not_null(validated["product_category"]))

    if reference_ids is not None and "customer_id" in validated:
        add_rule("valid_customer_reference", validate_referential_integrity(validated["customer_id"], reference_ids))

    if "transaction_date" in validated:
        dates = pd.to_datetime(validated["transaction_date"], errors="coerce")
        add_rule("valid_transaction_date", dates.notna() & (dates <= today))

    if {"start_date", "end_date"}.issubset(validated.columns):
        starts = pd.to_datetime(validated["start_date"], errors="coerce")
        ends = pd.to_datetime(validated["end_date"], errors="coerce")
        add_rule("valid_date_order", starts.notna() & ends.notna() & (ends >= starts))
    elif {"campaign_start_date", "campaign_end_date"}.issubset(validated.columns):
        starts = pd.to_datetime(validated["campaign_start_date"], errors="coerce")
        ends = pd.to_datetime(validated["campaign_end_date"], errors="coerce")
        add_rule("valid_campaign_date_order", starts.notna() & ends.notna() & (ends >= starts))

    if not rule_columns:
        raise ValueError("No supported validation columns found")
    validated["passes_all_checks"] = validated[rule_columns].all(axis=1)
    return validated, rule_columns


def build_validation_report(validated, rule_columns):
    """Build a JSON-serializable summary of validation results."""
    _require_dataframe(validated)
    return {
        "total_records": len(validated),
        "passed_records": int(validated["passes_all_checks"].sum()),
        "failed_records": int((~validated["passes_all_checks"]).sum()),
        "rules": {
            rule: {
                "passed": int(validated[rule].sum()),
                "failed": int((~validated[rule]).sum()),
            }
            for rule in rule_columns
        },
    }


def run_validation(input_path="data/engagement_data.csv", output_dir="output", reference_ids=None):
    """Validate a CSV, isolate failures, and write clean data and a JSON report."""
    df = pd.read_csv(input_path)
    validated, rule_columns = apply_validation_rules(df, reference_ids=reference_ids)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    validated.loc[~validated["passes_all_checks"]].to_csv(output_path / "validation_failures.csv", index=False)
    validated.loc[validated["passes_all_checks"]].to_csv(output_path / "validated_engagement_data.csv", index=False)
    report = build_validation_report(validated, rule_columns)
    with (output_path / "validation_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    return validated, report


if __name__ == "__main__":
    validated_df, validation_report = run_validation()
    print(f"Total Records : {validation_report['total_records']}")
    print(f"Passed        : {validation_report['passed_records']}")
    print(f"Failed        : {validation_report['failed_records']}")
    for rule, counts in validation_report["rules"].items():
        print(f"{rule}: Passed={counts['passed']}, Failed={counts['failed']}")
