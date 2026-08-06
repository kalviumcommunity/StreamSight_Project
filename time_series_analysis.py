import os
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs('output', exist_ok=True)


def build_time_series_features(df: pd.DataFrame, date_col='transaction_date', value_col='amount', resample_freq='ME'):
    if date_col not in df.columns:
        raise ValueError(f'Missing date column: {date_col}')
    if value_col not in df.columns:
        raise ValueError(f'Missing value column: {value_col}')

    ts = df.copy()
    ts[date_col] = pd.to_datetime(ts[date_col], errors='coerce')
    ts = ts.dropna(subset=[date_col])
    ts = ts.sort_values(date_col)
    ts = ts.set_index(date_col)

    ts['rolling_mean_7'] = ts[value_col].rolling(window=7).mean()
    ts['rolling_mean_30'] = ts[value_col].rolling(window=30).mean()
    ts['cumulative_value'] = ts[value_col].cumsum()

    resampled = ts[value_col].resample(resample_freq).sum()
    ts['period_change_pct'] = ts[value_col].pct_change() * 100
    ts['resampled_value'] = resampled.reindex(ts.index).ffill()

    return ts.reset_index()


def plot_time_series(df: pd.DataFrame, date_col='transaction_date', value_col='amount', output_path='output/time_series_trend.png'):
    plot_df = df.copy()
    plot_df[date_col] = pd.to_datetime(plot_df[date_col], errors='coerce')
    plot_df = plot_df.dropna(subset=[date_col]).sort_values(date_col)

    plt.figure(figsize=(10, 5))
    plt.plot(plot_df[date_col], plot_df[value_col], label='Raw', alpha=0.4)
    if 'rolling_mean_7' in plot_df.columns:
        plt.plot(plot_df[date_col], plot_df['rolling_mean_7'], label='7-day MA')
    if 'rolling_mean_30' in plot_df.columns:
        plt.plot(plot_df[date_col], plot_df['rolling_mean_30'], label='30-day MA')
    plt.legend()
    plt.title('Time-Series Trend')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path


def write_time_series_summary(df: pd.DataFrame, output_path='output/time_series_summary.txt'):
    ts = build_time_series_features(df)
    latest = ts.iloc[-1] if not ts.empty else None
    lines = []
    lines.append('Time-Series Summary')
    lines.append('===================')
    lines.append('')
    if latest is not None:
        lines.append(f"Latest value: {latest['amount']:.2f}")
        lines.append(f"7-day rolling mean: {latest['rolling_mean_7']:.2f}")
        lines.append(f"30-day rolling mean: {latest['rolling_mean_30']:.2f}")
        lines.append(f"Latest period change pct: {latest['period_change_pct']:.2f}%")
        lines.append(f"Cumulative value: {latest['cumulative_value']:.2f}")
    with open(output_path, 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(lines))
    return output_path
