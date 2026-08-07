import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def safe_read_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file not found: {path}")
    return pd.read_csv(path)


def normalize_series(s: pd.Series) -> pd.Series:
    if s.max() == s.min():
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - s.min()) / (s.max() - s.min())


def compute_segment_metrics(df: pd.DataFrame, segment_col='customer_type') -> pd.DataFrame:
    required = {segment_col}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required column: {segment_col}")

    # Common metric columns we expect; gracefully handle missing ones
    metrics = {}
    if 'lifetime_value' in df.columns:
        metrics['avg_ltv'] = ('lifetime_value', 'mean')
    if 'churn' in df.columns:
        metrics['churn_rate'] = ('churn', 'mean')
    if 'support_tickets' in df.columns:
        metrics['avg_tickets'] = ('support_tickets', 'mean')
    if 'support_cost' in df.columns:
        metrics['avg_support_cost'] = ('support_cost', 'mean')
    if 'customer_id' in df.columns:
        metrics['customer_count'] = ('customer_id', 'count')

    if not metrics:
        raise ValueError('No recognized metric columns found in data')

    agg_spec = {k: v for k, v in metrics.items()}
    summary = df.groupby(segment_col).agg(**agg_spec).reset_index()

    # format churn if present (ensure between 0-1)
    if 'churn_rate' in summary.columns:
        # if churn looks like percentages >1, scale down
        if summary['churn_rate'].max() > 1:
            summary['churn_rate'] = summary['churn_rate'] / 100.0

    return summary


def save_summary(summary: pd.DataFrame, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, 'segment_summary.csv')
    txt_path = os.path.join(out_dir, 'segment_summary.txt')
    summary.to_csv(csv_path, index=False)
    with open(txt_path, 'w', encoding='utf-8') as fh:
        fh.write(summary.to_string(index=False))
    return csv_path, txt_path


def plot_heatmap(summary: pd.DataFrame, out_dir: str, cmap='RdYlGn'):
    os.makedirs(out_dir, exist_ok=True)
    # pick numeric columns for heatmap
    numerics = summary.select_dtypes(include=[np.number]).copy()
    if numerics.shape[1] == 0:
        raise ValueError('No numeric columns to plot in heatmap')

    # Normalize each column for color comparison
    normed = numerics.apply(normalize_series)
    normed.index = summary.iloc[:, 0]  # segment names as index

    plt.figure(figsize=(max(6, normed.shape[1] * 1.5), max(4, normed.shape[0] * 0.6)))
    sns.heatmap(normed, annot=numerics.round(3), cmap=cmap, fmt='g')
    plt.title('Segment Comparison Heatmap (normalized)')
    plt.tight_layout()
    out_path = os.path.join(out_dir, 'segment_heatmap.png')
    plt.savefig(out_path)
    plt.close()
    return out_path


def plot_boxplots(df: pd.DataFrame, segment_col: str, numeric_cols: list, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    saved = []
    for col in numeric_cols:
        if col not in df.columns:
            continue
        plt.figure(figsize=(8, 4))
        sns.boxplot(data=df, x=segment_col, y=col)
        plt.title(f'{col} distribution by {segment_col}')
        plt.tight_layout()
        path = os.path.join(out_dir, f'boxplot_{col}.png')
        plt.savefig(path)
        plt.close()
        saved.append(path)
    return saved


def main():
    parser = argparse.ArgumentParser(description='Segment comparator: compute metrics and visualizations by segment')
    parser.add_argument('--input', '-i', default='data/engagement_data.csv', help='Input CSV file')
    parser.add_argument('--segment-col', '-s', default='customer_type', help='Column to segment by')
    parser.add_argument('--out', '-o', default='output', help='Output directory')
    args = parser.parse_args()

    df = safe_read_csv(args.input)
    summary = compute_segment_metrics(df, segment_col=args.segment_col)
    csv_path, txt_path = save_summary(summary, args.out)
    heatmap_path = None
    try:
        heatmap_path = plot_heatmap(summary, args.out)
    except Exception:
        heatmap_path = None

    boxplots = plot_boxplots(df, args.segment_col, ['lifetime_value', 'support_tickets', 'support_cost', 'amount'], args.out)

    print('Summary saved to:', csv_path)
    print('Text summary saved to:', txt_path)
    if heatmap_path:
        print('Heatmap saved to:', heatmap_path)
    if boxplots:
        print('Boxplots saved to:', ', '.join(boxplots))


if __name__ == '__main__':
    main()
