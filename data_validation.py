import json
import os
from datetime import datetime
from pathlib import Path

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


def _write_report(report, report_path):
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, default=str)
