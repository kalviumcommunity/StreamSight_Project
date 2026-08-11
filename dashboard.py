import json
from pathlib import Path

import pandas as pd

from kpis.kpi_functions import (
    calculate_average_transaction,
    calculate_churn_rate,
    calculate_mau,
    calculate_revenue_per_customer,
    calculate_total_revenue,
)


def _ensure_date_column(df, date_col="transaction_date"):
    if date_col not in df.columns:
        raise ValueError(f"Missing date column: {date_col}")
    result = df.copy()
    result[date_col] = pd.to_datetime(result[date_col], errors="coerce")
    if result[date_col].isna().any():
        result = result.dropna(subset=[date_col])
    return result


def build_dashboard_kpis(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        raise ValueError("DataFrame must contain at least one row to build dashboard KPIs.")

    target_df = _ensure_date_column(df)

    kpis = {
        "monthly_active_users": int(calculate_mau(target_df)),
        "revenue_per_customer": float(calculate_revenue_per_customer(target_df)),
        "average_transaction_value": float(calculate_average_transaction(target_df)),
        "total_revenue": float(calculate_total_revenue(target_df)),
        "churn_rate": float(calculate_churn_rate(target_df)),
    }

    if "payment_status" in target_df.columns:
        successful = target_df["payment_status"].astype(str).str.lower().isin(["success", "completed", "paid"])
        kpis["payment_success_rate"] = float(successful.sum() / len(target_df))

    if "customer_acquisition_cost" in target_df.columns:
        kpis["customer_acquisition_cost"] = float(target_df["customer_acquisition_cost"].mean())

    kpis["report_summary"] = (
        "Top-level dashboard KPIs for status monitoring."
        " Use these values to answer whether the business is on track."
    )

    return kpis


def build_dashboard_trends(df: pd.DataFrame, date_col="transaction_date", value_col="amount") -> dict:
    ts_df = _ensure_date_column(df, date_col=date_col)
    if value_col not in ts_df.columns:
        raise ValueError(f"Missing value column: {value_col}")

    ts = ts_df.set_index(date_col).sort_index()
    monthly_revenue = (
        ts[value_col]
        .resample("M")
        .sum()
        .rename("revenue")
        .reset_index()
    )

    weekly_active_users = (
        ts_df
        .groupby(pd.Grouper(key=date_col, freq="W"))["user_id"]
        .nunique()
        .rename("active_users")
        .reset_index()
    )

    trend_summary = {
        "monthly_revenue": monthly_revenue.to_dict(orient="records"),
        "weekly_active_users": weekly_active_users.to_dict(orient="records"),
        "latest_revenue": float(monthly_revenue["revenue"].iloc[-1]) if not monthly_revenue.empty else 0.0,
        "latest_active_users": int(weekly_active_users["active_users"].iloc[-1]) if not weekly_active_users.empty else 0,
    }

    if len(monthly_revenue) >= 2:
        prior = monthly_revenue["revenue"].iloc[-2]
        current = monthly_revenue["revenue"].iloc[-1]
        trend_summary["month_over_month_change_pct"] = float(((current - prior) / prior) * 100) if prior else 0.0

    return trend_summary


def build_dashboard_segments(df: pd.DataFrame) -> dict:
    segments = {}

    if "customer_type" in df.columns:
        segment_revenue = (
            df.groupby("customer_type")["amount"]
            .sum()
            .sort_values(ascending=False)
            .rename("revenue")
            .reset_index()
        )
        segments["revenue_by_customer_type"] = segment_revenue.to_dict(orient="records")

    if "product_category" in df.columns:
        category_revenue = (
            df.groupby("product_category")["amount"]
            .sum()
            .sort_values(ascending=False)
            .rename("revenue")
            .reset_index()
        )
        segments["revenue_by_product_category"] = category_revenue.to_dict(orient="records")

    if "customer_type" in df.columns and "product_category" in df.columns:
        cross_tab = (
            df.groupby(["customer_type", "product_category"])["amount"]
            .sum()
            .reset_index()
            .sort_values(["customer_type", "amount"], ascending=[True, False])
        )
        segments["segment_product_matrix"] = cross_tab.to_dict(orient="records")

    if not segments:
        raise ValueError("No recognized segment columns found to build dashboard segments.")

    segments["report_summary"] = (
        "Segment-level dashboard metrics for identifying which business areas deserve attention."
    )

    return segments


def write_dashboard_report(
    kpis: dict,
    trends: dict,
    segments: dict,
    output_path="output/dashboard_report.txt",
    json_path="output/dashboard_report.json",
) -> tuple[str, str]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("Dashboard Summary")
    lines.append("=================")
    lines.append("")
    lines.append("Level 1: Status")
    lines.append("-------------")
    for name, value in kpis.items():
        if name == "report_summary":
            continue
        lines.append(f"{name}: {value}")
    lines.append("")
    lines.append("Level 2: Trends")
    lines.append("-------------")
    if trends:
        lines.append("Monthly revenue trend:")
        for row in trends.get("monthly_revenue", []):
            lines.append(f"  {row['transaction_date'].strftime('%Y-%m')} -> {row['revenue']:.2f}")
        lines.append("")
        lines.append("Weekly active users trend:")
        for row in trends.get("weekly_active_users", []):
            lines.append(f"  {row['transaction_date'].strftime('%Y-%m-%d')} -> {row['active_users']}")
    lines.append("")
    lines.append("Level 3: Segments")
    lines.append("-------------")
    if "revenue_by_customer_type" in segments:
        lines.append("Revenue by customer type:")
        for row in segments["revenue_by_customer_type"]:
            lines.append(f"  {row['customer_type']}: {row['revenue']:.2f}")
    if "revenue_by_product_category" in segments:
        lines.append("")
        lines.append("Revenue by product category:")
        for row in segments["revenue_by_product_category"]:
            lines.append(f"  {row['product_category']}: {row['revenue']:.2f}")
    lines.append("")
    lines.append("Level 4: Detail")
    lines.append("-------------")
    lines.append("Use the generated JSON report to power dashboard filters and drill-down views.")

    with path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    if json_path:
        json_path = Path(json_path)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with json_path.open("w", encoding="utf-8") as handle:
            json.dump({"kpis": kpis, "trends": trends, "segments": segments}, handle, indent=2, default=str)

    return str(path), str(json_path)
