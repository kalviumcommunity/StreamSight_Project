from __future__ import annotations

from io import StringIO
from typing import IO, Any

import pandas as pd


def clean_uploaded_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize headers and remove rows that contain no usable values."""
    if df is None:
        raise ValueError("DataFrame is required.")

    cleaned = df.copy()
    cleaned.columns = [str(column).strip() for column in cleaned.columns]
    if any(not column for column in cleaned.columns):
        raise ValueError("The uploaded file contains a blank column name.")
    if cleaned.columns.duplicated().any():
        raise ValueError("The uploaded file contains duplicate column names.")

    for column in cleaned.select_dtypes(include=["object", "string"]).columns:
        cleaned[column] = cleaned[column].replace(r"^\s*$", pd.NA, regex=True)

    return cleaned.dropna(how="all").reset_index(drop=True)


def load_uploaded_dataframe(uploaded_file: IO[Any] | None) -> pd.DataFrame:
    """Load a CSV or JSON file uploaded via Streamlit or a file-like object."""
    if uploaded_file is None:
        raise ValueError("No file uploaded.")

    if not hasattr(uploaded_file, "read"):
        raise TypeError("Uploaded file is not readable.")

    filename = str(getattr(uploaded_file, "name", "")).lower()

    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)

    try:
        if filename.endswith(".csv"):
            return clean_uploaded_dataframe(pd.read_csv(uploaded_file))
        if filename.endswith(".json"):
            if hasattr(uploaded_file, "getvalue"):
                payload = uploaded_file.getvalue()
            else:
                payload = uploaded_file.read()
            if isinstance(payload, (bytes, bytearray)):
                payload = payload.decode("utf-8")
            if not isinstance(payload, str):
                payload = str(payload)
            return clean_uploaded_dataframe(pd.read_json(StringIO(payload)))
    except Exception as exc:  # pragma: no cover - bubbled to caller for user-friendly UI handling
        raise ValueError(f"Could not read this file. Please check the format. Details: {exc}") from exc

    raise ValueError("Unsupported file type. Please upload CSV or JSON.")


def build_preview_metrics(df: pd.DataFrame) -> dict:
    if df is None:
        raise ValueError("DataFrame is required.")

    rows = len(df)
    columns = len(df.columns)
    total_nulls = int(df.isnull().sum().sum())
    total_cells = rows * columns
    null_pct = (total_nulls / total_cells * 100.0) if total_cells else 0.0

    return {
        "rows": rows,
        "columns": columns,
        "total_nulls": total_nulls,
        "null_pct": round(null_pct, 1),
    }


def build_column_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        raise ValueError("DataFrame is required.")

    summary = pd.DataFrame(
        {
            "Column": df.columns,
            "Type": df.dtypes.astype(str).values,
            "Non-Null": df.notnull().sum().values,
            "Null Count": df.isnull().sum().values,
            "Null %": (df.isnull().sum() / len(df) * 100).round(1).values,
        }
    )
    return summary


def render_upload_preview(uploaded_file: IO[Any] | None):
    """Render the upload/preview workflow for a Streamlit app."""
    try:
        import streamlit as st
    except ImportError as exc:  # pragma: no cover - runtime only
        raise RuntimeError("streamlit is required to render the upload preview.") from exc

    if uploaded_file is None:
        st.info("Upload a CSV or JSON file to begin.")
        return None

    try:
        df = load_uploaded_dataframe(uploaded_file)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()
    except Exception:
        st.error("Could not read this file. Please check the format.")
        st.stop()

    if df.empty:
        st.warning("The uploaded file is empty. Please check your data.")
        st.stop()

    st.success(f"File loaded: {getattr(uploaded_file, 'name', 'uploaded_file')} ({len(df)} rows, {len(df.columns)} columns)")

    metrics = build_preview_metrics(df)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", f"{metrics['rows']:,}")
    with col2:
        st.metric("Columns", str(metrics["columns"]))
    with col3:
        st.metric("Null %", f"{metrics['null_pct']:.1f}%")

    st.divider()
    st.subheader("First 10 Rows")
    st.dataframe(df.head(10), use_container_width=True)

    st.subheader("Column Summary")
    st.dataframe(build_column_summary(df), use_container_width=True)

    st.subheader("Descriptive Statistics")
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        st.caption("No numeric columns available for descriptive statistics.")
    else:
        st.dataframe(numeric_df.describe(), use_container_width=True)

    return df
