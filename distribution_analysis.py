"""Distribution analysis utilities: skewness, kurtosis, hist/KDE plotting, segment comparison.

Saves plots under `output/` by default.
"""
from typing import Optional
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


os.makedirs("output", exist_ok=True)


def compute_distribution_stats(series: pd.Series) -> dict:
    arr = series.dropna().astype(float).values
    if arr.size == 0:
        return {}
    skewness = float(stats.skew(arr))
    kurt = float(stats.kurtosis(arr, fisher=False))
    return {
        "count": int(arr.size),
        "mean": float(arr.mean()),
        "median": float(np.median(arr)),
        "std": float(arr.std()),
        "skewness": skewness,
        "kurtosis": kurt,
        "min": float(arr.min()),
        "max": float(arr.max()),
        "iqr": float(np.percentile(arr, 75) - np.percentile(arr, 25)),
    }


def plot_hist_kde(series: pd.Series, col_name: str, bins: int = 50, savepath: Optional[str] = None):
    arr = series.dropna().astype(float).values
    if arr.size == 0:
        return None
    plt.figure(figsize=(10, 5))
    plt.hist(arr, bins=bins, density=True, alpha=0.5, edgecolor='black', label='hist')
    try:
        kde = stats.gaussian_kde(arr)
        xs = np.linspace(arr.min(), arr.max(), 200)
        plt.plot(xs, kde(xs), label='kde')
    except Exception:
        pass
    plt.xlabel(col_name)
    plt.ylabel('Density')
    plt.title(f'Distribution of {col_name}')
    plt.legend()
    if savepath is None:
        savepath = f"output/distribution_{col_name}.png"
    plt.tight_layout()
    plt.savefig(savepath)
    plt.close()
    return savepath


def compare_segments_plot(df: pd.DataFrame, col: str, low_q: float = 0.25, high_q: float = 0.75, bins: int = 40, savepath: Optional[str] = None):
    if col not in df.columns:
        return None
    series = df[col].dropna().astype(float)
    if series.empty:
        return None
    q_low = series.quantile(low_q)
    q_high = series.quantile(high_q)
    low_seg = series[series <= q_low]
    high_seg = series[series >= q_high]

    plt.figure(figsize=(10, 5))
    plt.hist(low_seg, bins=bins, alpha=0.5, label=f'low (<= {low_q})', density=True)
    plt.hist(high_seg, bins=bins, alpha=0.5, label=f'high (>= {high_q})', density=True)
    try:
        xs = np.linspace(series.min(), series.max(), 200)
        plt.plot(xs, stats.gaussian_kde(low_seg)(xs), label='low_kde')
        plt.plot(xs, stats.gaussian_kde(high_seg)(xs), label='high_kde')
    except Exception:
        pass
    plt.xlabel(col)
    plt.ylabel('Density')
    plt.title(f'Compare segments for {col}')
    plt.legend()
    if savepath is None:
        savepath = f"output/compare_{col}.png"
    plt.tight_layout()
    plt.savefig(savepath)
    plt.close()
    return savepath


if __name__ == "__main__":
    # Quick CLI for local runs
    path = "output/validated_engagement_data.csv"
    if not os.path.exists(path):
        print("Validated data not found at output/validated_engagement_data.csv")
    else:
        df = pd.read_csv(path)
        target_cols = [c for c in ["amount", "total_spend", "transaction_count"] if c in df.columns]
        for col in target_cols:
            stats = compute_distribution_stats(df[col])
            print(f"Stats for {col}:", stats)
            print("Saving plots...")
            plot_hist_kde(df[col], col)
            compare_segments_plot(df, col)
