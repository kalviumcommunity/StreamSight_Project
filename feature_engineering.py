"""Feature engineering utilities: ratio features, binning, and RFM scoring.

Functions operate on pandas DataFrames or Series and add derived columns.
"""
from typing import Optional, Sequence
import pandas as pd


def transactions_per_month(df: pd.DataFrame, trans_col: str = "total_transactions",
                           days_col: str = "days_as_customer",
                           out_col: str = "transactions_per_month") -> pd.Series:
    """Compute transactions per 30-day month (handle zeros/NaN).
    Returns the resulting Series (does not modify df unless assigned).
    """
    days = df[days_col].replace(0, pd.NA)
    months = days.astype(float) / 30.0
    return df[trans_col].astype(float) / months


def avg_spend_per_transaction(df: pd.DataFrame, spend_col: str = "total_spent",
                              trans_col: str = "total_transactions",
                              out_col: str = "avg_spend_per_transaction") -> pd.Series:
    """Compute average spend per transaction (handle division by zero).
    """
    trans = df[trans_col].replace(0, pd.NA).astype(float)
    return df[spend_col].astype(float) / trans


def lifetime_value_per_month(df: pd.DataFrame, spend_col: str = "total_spent",
                              days_col: str = "days_as_customer",
                              out_col: str = "lifetime_value_per_month") -> pd.Series:
    days = df[days_col].replace(0, pd.NA).astype(float)
    months = days / 30.0
    return df[spend_col].astype(float) / months


def engagement_bin(series: pd.Series, bins: Sequence[float] = (0, 2, 10, float("inf")),
                   labels: Optional[Sequence[str]] = ("low", "medium", "high")) -> pd.Series:
    """Bin engagement numeric series into labeled tiers using pd.cut."""
    return pd.cut(series, bins=list(bins), labels=list(labels), include_lowest=True)


def spend_tier_quantile(series: pd.Series, q: int = 4,
                        labels: Optional[Sequence[str]] = None) -> pd.Series:
    """Create equal-frequency quantile tiers using pd.qcut."""
    if labels is None:
        labels = [f"tier_{i+1}" for i in range(q)]
    return pd.qcut(series, q=q, labels=labels, duplicates="drop")


def compute_rfm(df: pd.DataFrame, recency_col: str, frequency_col: str, monetary_col: str,
                q: int = 5) -> pd.DataFrame:
    """Compute RFM component scores (1..q) and combined `rfm_score`.

    Returns a DataFrame with the added columns: `recency_score`, `frequency_score`,
    `monetary_score`, and `rfm_score`.
    """
    out = pd.DataFrame(index=df.index)
    # For recency, lower is better so invert the quantiles
    out['recency_score'] = pd.qcut(df[recency_col].rank(method='first', ascending=False), q=q, labels=range(q, 0, -1)).astype(int)
    out['frequency_score'] = pd.qcut(df[frequency_col].rank(method='first', ascending=True), q=q, labels=range(1, q+1)).astype(int)
    out['monetary_score'] = pd.qcut(df[monetary_col].rank(method='first', ascending=True), q=q, labels=range(1, q+1)).astype(int)
    out['rfm_score'] = out['recency_score'] + out['frequency_score'] + out['monetary_score']
    return out
