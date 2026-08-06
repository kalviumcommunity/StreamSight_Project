"""Correlation and relationship analysis utilities.

Provides Pearson and Spearman correlation matrices, a heatmap export, and a
summary of strong correlations for feature selection.
"""
from typing import Optional
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

os.makedirs("output", exist_ok=True)


def compute_correlation_matrices(df: pd.DataFrame) -> dict:
    numeric_df = df.select_dtypes(include=['number']).copy()
    if numeric_df.empty:
        return {"pearson": pd.DataFrame(), "spearman": pd.DataFrame()}
    pearson = numeric_df.corr(method='pearson')
    spearman = numeric_df.corr(method='spearman')
    return {"pearson": pearson, "spearman": spearman}


def plot_correlation_heatmap(corr: pd.DataFrame, title: str = 'Correlation Matrix', savepath: Optional[str] = None):
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr, annot=False, cmap='coolwarm', center=0)
    plt.title(title)
    plt.tight_layout()
    if savepath is None:
        savepath = 'output/correlation_heatmap.png'
    plt.savefig(savepath)
    plt.close()
    return savepath


def summarize_strong_correlations(corr: pd.DataFrame, threshold: float = 0.7) -> pd.DataFrame:
    if corr.empty:
        return pd.DataFrame(columns=['var1', 'var2', 'correlation'])
    corr_flat = corr.stack()
    strong = corr_flat[(corr_flat.abs() > threshold) & (corr_flat != 1.0)]
    strong = strong.sort_values(ascending=False)
    result = strong.reset_index()
    result.columns = ['var1', 'var2', 'correlation']
    return result


if __name__ == '__main__':
    path = 'output/validated_engagement_data.csv'
    if os.path.exists(path):
        df = pd.read_csv(path)
        matrices = compute_correlation_matrices(df)
        for name, corr in matrices.items():
            print(f'[{name}]')
            print(corr.head())
            plot_correlation_heatmap(corr, title=f'{name.title()} Correlation Matrix')
            print(summarize_strong_correlations(corr).head())
    else:
        print('Validated data not found at output/validated_engagement_data.csv')
