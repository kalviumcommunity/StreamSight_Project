import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import chardet
except ImportError:  # pragma: no cover - optional dependency
    chardet = None


def validate_file_exists(filepath):
    path = Path(filepath)
    if not path.exists():
        return False, f"File not found: {path}"
    if not path.is_file():
        return False, f"Path is not a file: {path}"
    if path.stat().st_size == 0:
        return False, "File is empty"
    return True, "File exists and has content"


def validate_file_format(filepath, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = ["csv", "json", "xlsx"]

    extension = Path(filepath).suffix.lower().lstrip(".")
    if not extension:
        return False, f"Unsupported file format: no extension found in {filepath}"
    if extension not in allowed_extensions:
        return False, f"Unsupported extension: .{extension}. Allowed: {', '.join(allowed_extensions)}"
    return True, f"Format valid: .{extension}"


def validate_schema(df, expected_columns):
    missing = [col for col in expected_columns if col not in df.columns]
    extra = [col for col in df.columns if col not in expected_columns]

    if missing or extra:
        messages = []
        if missing:
            messages.append(f"Missing: {missing}")
        if extra:
            messages.append(f"Extra: {extra}")
        return False, " | ".join(messages)

    return True, "Schema valid"


def validate_data_quality(df):
    missing_value_columns = [col for col in df.columns if df[col].isna().any()]
    duplicate_rows = int(df.duplicated().sum())

    issues = []
    if missing_value_columns:
        issues.append(f"Missing values in: {missing_value_columns}")
    if duplicate_rows:
        issues.append(f"Duplicate rows found: {duplicate_rows}")

    if issues:
        return False, " | ".join(issues)

    return True, "Data quality check passed"


def deduplicate_records(df, subset=None, strategy="most_complete", audit_path=None, report_path=None):
    """Remove duplicates, preserve the best row, and write an audit trail."""
    if df is None:
        raise ValueError("A pandas DataFrame is required")
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame")

    if strategy not in {"first", "last", "most_complete"}:
        raise ValueError("strategy must be one of: first, last, most_complete")

    if subset is None:
        subset = list(df.columns)
    elif isinstance(subset, str):
        subset = [subset]
    else:
        subset = list(subset)

    if not subset:
        subset = list(df.columns)

    missing_columns = [col for col in subset if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Subset columns not found in DataFrame: {missing_columns}")

    original_df = df.copy()
    duplicate_mask = original_df.duplicated(subset=subset, keep=False)
    exact_duplicate_mask = original_df.duplicated(keep=False)
    duplicate_groups = original_df.loc[duplicate_mask]
    audit_timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    rows_to_remove = []
    row_keep_map = {}

    for _, group in original_df.groupby(subset, dropna=False, sort=False):
        if len(group) <= 1:
            continue

        if strategy == "first":
            keep_idx = group.index[0]
        elif strategy == "last":
            keep_idx = group.index[-1]
        else:
            completeness = group.notna().sum(axis=1)
            ranked_group = group.assign(_completeness=completeness).sort_values(
                by="_completeness",
                ascending=False,
                kind="mergesort",
            )
            keep_idx = ranked_group.index[0]

        for row_idx in group.index:
            row_keep_map[row_idx] = keep_idx

        rows_to_remove.extend([idx for idx in group.index if idx != keep_idx])

    deduped_df = original_df.drop(index=rows_to_remove).copy()

    audit_log = []
    for row_idx in sorted(rows_to_remove):
        audit_log.append({
            "row_index": int(row_idx),
            "retained_row_index": int(row_keep_map[row_idx]),
            "duplicate_type": "exact" if exact_duplicate_mask.loc[row_idx] else "near",
            "strategy": strategy,
            "duplicate_subset": subset,
            "removed_at": audit_timestamp,
            "reason": "Removed as duplicate based on the selected key columns.",
        })

    removed_df = original_df.loc[rows_to_remove].copy()
    if not removed_df.empty:
        removed_df["retained_row_index"] = removed_df.index.map(row_keep_map)
        removed_df["duplicate_type"] = [
            "exact" if exact_duplicate_mask.loc[row_idx] else "near"
            for row_idx in removed_df.index
        ]
        removed_df["deduplication_strategy"] = strategy
        removed_df["deduplication_reason"] = "Removed as duplicate based on the selected key columns."
        removed_df["removed_at"] = audit_timestamp

    if audit_path is not None:
        path = Path(audit_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        removed_df.to_csv(path, index=False)

    comparison = {
        "rows_before": int(len(original_df)),
        "rows_after": int(len(deduped_df)),
        "rows_removed": int(len(original_df) - len(deduped_df)),
        "removal_pct": round((len(original_df) - len(deduped_df)) / len(original_df) * 100, 2) if len(original_df) else 0.0,
        "duplicate_groups": int(duplicate_groups.groupby(subset, dropna=False).ngroups) if not duplicate_groups.empty else 0,
        "exact_duplicate_rows": int(exact_duplicate_mask.loc[rows_to_remove].sum()) if rows_to_remove else 0,
        "near_duplicate_rows": int(sum(not exact_duplicate_mask.loc[row_idx] for row_idx in rows_to_remove)),
        "strategy": strategy,
        "subset": subset,
    }

    if report_path is not None:
        path = Path(report_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump({"comparison": comparison, "audit_log": audit_log}, handle, indent=2, default=str)

    return deduped_df, audit_log, comparison


def analyze_missing_before(df):
    """Return a summary of missing values before imputation."""
    if df is None:
        raise ValueError("A pandas DataFrame is required")
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame")

    total_rows = len(df)
    missing_values = {}
    missing_percentages = {}

    for column in df.columns:
        null_count = int(df[column].isna().sum())
        if null_count > 0:
            missing_values[column] = null_count
            missing_percentages[column] = round((null_count / total_rows) * 100, 2) if total_rows else 0.0

    return {
        "total_rows": total_rows,
        "missing_values": missing_values,
        "missing_percentages": missing_percentages,
    }


def _is_time_like_column(column_name, series):
    if pd.api.types.is_datetime64_any_dtype(series):
        return True

    column_name = str(column_name).lower()
    return any(token in column_name for token in ["date", "time", "timestamp"])


def impute_missing_values(df, critical_columns=None, report_path=None):
    """Impute missing values using column-appropriate strategies and return an audit trail."""
    if df is None:
        raise ValueError("A pandas DataFrame is required")
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame")

    cleaned_df = df.copy()
    critical_columns = critical_columns or []
    audit_log = []

    for column in cleaned_df.columns:
        if column in critical_columns:
            continue

        before_nulls = int(cleaned_df[column].isna().sum())
        if before_nulls == 0:
            continue

        if pd.api.types.is_numeric_dtype(cleaned_df[column]):
            fill_value = cleaned_df[column].median()
            cleaned_df[column] = cleaned_df[column].fillna(fill_value)
            strategy = "median"
            reasoning = "Numerical columns use the median to reduce the impact of outliers."
        elif _is_time_like_column(column, cleaned_df[column]):
            cleaned_df[column] = pd.to_datetime(cleaned_df[column], errors="coerce").ffill()
            strategy = "forward_fill"
            reasoning = "Time-oriented columns use forward fill because the most recent known value is the best estimate for short gaps."
        else:
            mode_value = cleaned_df[column].mode(dropna=True)
            if not mode_value.empty:
                fill_value = mode_value.iloc[0]
                cleaned_df[column] = cleaned_df[column].fillna(fill_value)
            else:
                cleaned_df[column] = cleaned_df[column].fillna("UNKNOWN")
            strategy = "mode"
            reasoning = "Categorical columns use the mode to preserve the dominant business category."

        audit_log.append({
            "column": column,
            "strategy": strategy,
            "reasoning": reasoning,
            "before_nulls": before_nulls,
            "after_nulls": int(cleaned_df[column].isna().sum()),
        })

    for column in critical_columns:
        if column not in cleaned_df.columns:
            continue

        before_nulls = int(cleaned_df[column].isna().sum())
        if before_nulls > 0:
            cleaned_df = cleaned_df.dropna(subset=[column]).copy()
            audit_log.append({
                "column": column,
                "strategy": "drop_rows",
                "reasoning": "Critical identifier values are missing; rows cannot be reliably traced.",
                "before_nulls": before_nulls,
                "after_nulls": int(cleaned_df[column].isna().sum()),
            })

    if report_path is not None:
        path = Path(report_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump({
                "summary": analyze_missing_before(df),
                "audit_log": audit_log,
            }, handle, indent=2, default=str)

    return cleaned_df, audit_log


def detect_encoding(filepath):
    path = Path(filepath)
    try:
        with path.open("rb") as handle:
            sample = handle.read(10000)
    except Exception as exc:  # pragma: no cover - defensive path
        return "unknown", 0.0, f"Could not read file for encoding detection: {exc}"

    if chardet is not None:
        result = chardet.detect(sample) or {}
        encoding = result.get("encoding") or "unknown"
        confidence = result.get("confidence", 0.0) or 0.0
        if encoding:
            return encoding, confidence, f"Detected: {encoding} ({confidence:.0%})"

    try:
        sample.decode("utf-8")
        return "utf-8", 1.0, "Detected: utf-8 (100%)"
    except UnicodeDecodeError:
        try:
            sample.decode("latin-1")
            return "latin-1", 0.5, "Detected: latin-1 (50%)"
        except UnicodeDecodeError:
            return "unknown", 0.0, "Encoding detection unavailable"


def validate_encoding(filepath, expected_encoding="utf-8"):
    detected, confidence, message = detect_encoding(filepath)
    if detected == "unknown":
        return False, f"Could not determine encoding for {filepath}"

    normalized_detected = detected.lower()
    normalized_expected = expected_encoding.lower()

    if normalized_expected == "utf-8" and normalized_detected in {"utf-8", "utf-8-sig", "ascii"}:
        return True, message

    if normalized_detected != normalized_expected:
        return False, f"Detected {detected} but expected {expected_encoding}"

    return True, message


def load_dataframe(filepath, encoding="utf-8"):
    path = Path(filepath)
    extension = path.suffix.lower()

    if extension == ".csv":
        return pd.read_csv(path, encoding=encoding)
    if extension == ".json":
        return pd.read_json(path)
    raise ValueError(f"Unsupported format for loading: {extension}")


def capture_stats(filepath, df):
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "file_size_mb": round(Path(filepath).stat().st_size / (1024 * 1024), 3),
    }


def validate_merge(left, right, on=None, how="left", output_unmatched_left=None, output_unmatched_right=None, report_path="output/join_validation_report.json"):
    """Validate a merge operation and return a merged DataFrame plus a summary report."""
    if not isinstance(left, pd.DataFrame) or not isinstance(right, pd.DataFrame):
        raise TypeError("left and right must both be pandas DataFrame objects")

    if on is None:
        raise ValueError("The 'on' parameter must be provided")

    if isinstance(on, str):
        join_keys = [on]
    else:
        join_keys = list(on)

    missing_left = [key for key in join_keys if key not in left.columns]
    missing_right = [key for key in join_keys if key not in right.columns]
    if missing_left or missing_right:
        raise ValueError(f"Join keys missing: left={missing_left}, right={missing_right}")

    merged_df = left.merge(right, on=join_keys, how=how, indicator=True)
    left_rows = len(left)
    right_rows = len(right)
    merged_rows = len(merged_df)

    left_key_df = left[join_keys].drop_duplicates()
    right_key_df = right[join_keys].drop_duplicates()

    left_distinct_keys = len(left_key_df)
    right_distinct_keys = len(right_key_df)
    merged_distinct_keys = len(merged_df[join_keys].drop_duplicates())

    left_duplicate_key_rows = left_rows - left_distinct_keys
    right_duplicate_key_rows = right_rows - right_distinct_keys

    left_match = left_key_df.merge(right_key_df, on=join_keys, how="left", indicator=True)
    unmatched_left_keys = left_match.loc[left_match["_merge"] == "left_only", join_keys].drop(columns=["_merge"])
    unmatched_left = int(len(unmatched_left_keys))

    right_match = right_key_df.merge(left_key_df, on=join_keys, how="left", indicator=True)
    unmatched_right_keys = right_match.loc[right_match["_merge"] == "left_only", join_keys].drop(columns=["_merge"])
    unmatched_right = int(len(unmatched_right_keys))

    if output_unmatched_left is not None and unmatched_left:
        path = Path(output_unmatched_left)
        path.parent.mkdir(parents=True, exist_ok=True)
        unmatched_left_df = left.merge(unmatched_left_keys, on=join_keys, how="inner")
        unmatched_left_df.to_csv(path, index=False)

    if output_unmatched_right is not None and unmatched_right:
        path = Path(output_unmatched_right)
        path.parent.mkdir(parents=True, exist_ok=True)
        unmatched_right_df = right.merge(unmatched_right_keys, on=join_keys, how="inner")
        unmatched_right_df.to_csv(path, index=False)

    if left_duplicate_key_rows > 0 and right_duplicate_key_rows > 0:
        join_cardinality = "many-to-many"
    elif left_duplicate_key_rows > 0:
        join_cardinality = "many-to-one"
    elif right_duplicate_key_rows > 0:
        join_cardinality = "one-to-many"
    else:
        join_cardinality = "one-to-one"

    validation_issues = []
    if how == "left" and merged_rows < left_rows:
        validation_issues.append("Left join returned fewer rows than left input, which is unexpected.")
    if how == "right" and merged_rows < right_rows:
        validation_issues.append("Right join returned fewer rows than right input, which is unexpected.")
    if how == "outer" and merged_rows < max(left_rows, right_rows):
        validation_issues.append("Outer join returned fewer rows than expected for a full outer join.")

    report = {
        "join_type": how,
        "left_rows": left_rows,
        "right_rows": right_rows,
        "merged_rows": merged_rows,
        "left_distinct_keys": left_distinct_keys,
        "right_distinct_keys": right_distinct_keys,
        "merged_distinct_keys": merged_distinct_keys,
        "left_duplicate_key_rows": left_duplicate_key_rows,
        "right_duplicate_key_rows": right_duplicate_key_rows,
        "join_cardinality": join_cardinality,
        "unmatched_left_rows": unmatched_left,
        "unmatched_right_rows": unmatched_right,
        "valid": len(validation_issues) == 0,
        "row_count_validation": {
            "issues": validation_issues,
            "expected_relationship": (
                "merged_rows >= left_rows" if how == "left" else
                "merged_rows >= right_rows" if how == "right" else
                "merged_rows >= max(left_rows, right_rows)" if how == "outer" else
                "matched rows only"
            ),
        },
    }

    if report_path is not None:
        _write_report(report, report_path)

    return merged_df, report


def validate_dataset(filepath, expected_columns, allowed_extensions=None, expected_encoding="utf-8", report_path="output/intake_report.json", return_dataframe=False):
    report = {
        "timestamp": datetime.now().isoformat(),
        "filepath": str(filepath),
        "valid": False,
        "checks": {},
        "statistics": {},
    }

    file_ok, file_message = validate_file_exists(filepath)
    report["checks"]["file_exists"] = file_message
    if not file_ok:
        _write_report(report, report_path)
        return (report, None) if return_dataframe else report

    format_ok, format_message = validate_file_format(filepath, allowed_extensions=allowed_extensions)
    report["checks"]["format"] = format_message
    if not format_ok:
        _write_report(report, report_path)
        return (report, None) if return_dataframe else report

    encoding_ok, encoding_message = validate_encoding(filepath, expected_encoding=expected_encoding)
    report["checks"]["encoding"] = encoding_message
    if not encoding_ok:
        _write_report(report, report_path)
        return (report, None) if return_dataframe else report

    detected_encoding = encoding_message.split("Detected: ", 1)[1].split(" (", 1)[0] if "Detected:" in encoding_message else expected_encoding
    try:
        df = load_dataframe(filepath, encoding=detected_encoding)
    except Exception as exc:
        report["checks"]["load"] = f"Could not load dataset: {exc}"
        _write_report(report, report_path)
        return (report, None) if return_dataframe else report

    schema_ok, schema_message = validate_schema(df, expected_columns)
    report["checks"]["schema"] = schema_message
    if not schema_ok:
        _write_report(report, report_path)
        return (report, None) if return_dataframe else report

    quality_ok, quality_message = validate_data_quality(df)
    report["checks"]["quality"] = quality_message
    if not quality_ok:
        _write_report(report, report_path)
        return (report, None) if return_dataframe else report

    report["checks"]["dimensions"] = f"Rows: {len(df)}, Columns: {len(df.columns)}"
    report["statistics"] = capture_stats(filepath, df)
    report["valid"] = True

    _write_report(report, report_path)
    return (report, df) if return_dataframe else report


def detect_outliers_zscore(df, column, threshold=3.0):
    if column not in df.columns:
        raise ValueError(f"Column not found in DataFrame: {column}")
    if not pd.api.types.is_numeric_dtype(df[column]):
        raise TypeError(f"Z-score outlier detection requires numeric data: {column}")

    series = df[column].astype(float)
    std = series.std(ddof=0)
    if std == 0 or series.empty:
        return pd.Series(False, index=df.index)

    z_scores = np.abs((series - series.mean()) / std)
    return z_scores > threshold


def detect_outliers_iqr(df, column, factor=1.5):
    if column not in df.columns:
        raise ValueError(f"Column not found in DataFrame: {column}")
    if not pd.api.types.is_numeric_dtype(df[column]):
        raise TypeError(f"IQR outlier detection requires numeric data: {column}")

    series = df[column].dropna().astype(float)
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - factor * iqr
    upper_bound = q3 + factor * iqr

    return (df[column] < lower_bound) | (df[column] > upper_bound)


def handle_outliers(df, column, action="flag", strategy="iqr", threshold=3.0, factor=1.5, report_path=None):
    if action not in {"cap", "remove", "flag"}:
        raise ValueError("action must be one of: cap, remove, flag")
    if strategy not in {"iqr", "zscore"}:
        raise ValueError("strategy must be one of: iqr, zscore")

    if strategy == "zscore":
        outlier_mask = detect_outliers_zscore(df, column, threshold=threshold)
    else:
        outlier_mask = detect_outliers_iqr(df, column, factor=factor)

    lower_bound = None
    upper_bound = None
    if strategy == "iqr":
        series = df[column].dropna().astype(float)
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - factor * iqr
        upper_bound = q3 + factor * iqr
    else:
        series = df[column].astype(float)
        std = series.std(ddof=0)
        lower_bound = series.mean() - threshold * std
        upper_bound = series.mean() + threshold * std

    cleaned_df = df.copy()
    audit_entry = {
        "column": column,
        "strategy": strategy,
        "action": action,
        "outlier_count": int(outlier_mask.sum()),
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "reasoning": "Detected outliers using statistical bounds and handled them according to the specified strategy.",
    }

    if action == "cap":
        cleaned_df[f"is_{column}_outlier"] = outlier_mask.astype(int)
        cleaned_df[f"{column}_capped"] = cleaned_df[column].clip(lower=lower_bound, upper=upper_bound)
    elif action == "remove":
        cleaned_df = cleaned_df.loc[~outlier_mask].copy()
    else:
        cleaned_df[f"is_{column}_outlier"] = outlier_mask.astype(int)

    if report_path is not None:
        path = Path(report_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump({"outlier_audit": audit_entry}, handle, indent=2, default=str)

    return cleaned_df, [audit_entry]


def _write_report(report, report_path):
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, default=str)
