import os
import pandas as pd
import numpy as np

os.makedirs('output', exist_ok=True)


def check_threshold_alerts(metrics, rules):
    """Alert when key metrics fall outside configured thresholds."""
    alerts = []
    for metric_name, rule in rules.items():
        value = metrics.get(metric_name)
        if value is None:
            continue
        if value < rule.get('min', float('-inf')):
            alerts.append(f"⚠️ {metric_name} BELOW MIN: {value} < {rule['min']}")
        elif value > rule.get('max', float('inf')):
            alerts.append(f"⚠️ {metric_name} ABOVE MAX: {value} > {rule['max']}")
    return alerts


def detect_anomalies_zscore(series, threshold=2.0):
    """Flag values beyond N standard deviations from the rolling mean."""
    if series is None or series.empty:
        return pd.Series(dtype=float)

    mean = series.mean()
    std = series.std()
    if pd.isna(std) or std == 0:
        return pd.Series(dtype=float)

    z_scores = np.abs((series - mean) / std)
    return series[z_scores > threshold]


def build_anomaly_report(series, metric_name='daily_revenue', threshold=2.0):
    """Create a structured anomaly report for monitoring and alerting."""
    anomalies = detect_anomalies_zscore(series, threshold=threshold)
    if anomalies.empty:
        return {
            'metric_name': metric_name,
            'anomaly_count': 0,
            'severity': 'low',
            'anomalies': [],
        }

    mean = series.mean()
    std = series.std()
    anomaly_details = []
    for timestamp, value in anomalies.items():
        anomaly_details.append({
            'timestamp': timestamp,
            'value': float(value),
            'expected_range': f"{mean - 2 * std:.2f}-{mean + 2 * std:.2f}",
            'severity': 'high' if abs(value - mean) > 3 * std else 'medium',
        })

    return {
        'metric_name': metric_name,
        'anomaly_count': len(anomaly_details),
        'severity': 'high' if anomaly_details else 'low',
        'anomalies': anomaly_details,
    }


def investigate_anomaly(df: pd.DataFrame, date_col='transaction_date', value_col='amount', status_col='status', segment_col='payment_method', success_value='completed'):
    if date_col not in df.columns or value_col not in df.columns or status_col not in df.columns:
        raise ValueError('Required columns for investigation are missing')

    work = df.copy()
    work[date_col] = pd.to_datetime(work[date_col], errors='coerce')
    work = work.dropna(subset=[date_col]).sort_values(date_col)
    work['success_rate'] = (work[status_col] == success_value).astype(int)

    daily_success = work.groupby(work[date_col].dt.date)['success_rate'].mean()
    anomaly_date = daily_success[daily_success < 0.5].index[0] if (daily_success < 0.5).any() else None

    findings = []
    if anomaly_date is None:
        findings.append('No anomaly window identified')
        return {'anomaly_date': None, 'findings': findings}

    anomaly_day = work[work[date_col].dt.date == anomaly_date]
    hourly_success = anomaly_day.groupby(anomaly_day[date_col].dt.hour)['success_rate'].mean()

    if segment_col in work.columns:
        during_window = anomaly_day[anomaly_day[date_col].dt.hour.isin([11, 12, 13])]
        segment_summary = during_window.groupby(segment_col)['success_rate'].mean().sort_values()
    else:
        segment_summary = pd.Series(dtype='float64')

    findings.append(f"Anomaly date: {anomaly_date}")
    findings.append(f"Hourly success trend: {hourly_success.to_dict()}")
    if not segment_summary.empty:
        findings.append(f"Segment impact: {segment_summary.to_dict()}")
    return {
        'anomaly_date': anomaly_date,
        'hourly_success': hourly_success,
        'segment_summary': segment_summary,
        'findings': findings,
    }


def write_investigation_report(df: pd.DataFrame, output_path='output/root_cause_report.txt'):
    result = investigate_anomaly(df)
    lines = ['Root Cause Investigation Report', '==============================', '']
    lines.extend(result['findings'])
    with open(output_path, 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(lines))
    return output_path
