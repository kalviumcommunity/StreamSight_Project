import os
from pathlib import Path
import pandas as pd
import numpy as np

os.makedirs('output', exist_ok=True)


def build_threshold_alerts(metrics, rules):
    """Return structured alerts when metrics fall outside configured thresholds."""
    alerts = []
    for metric_name, rule in rules.items():
        value = metrics.get(metric_name)
        if value is None or pd.isna(value):
            continue
        if value < rule.get('min', float('-inf')):
            alerts.append({
                'metric': metric_name,
                'value': value,
                'direction': 'below_min',
                'threshold': rule['min'],
                'severity': rule.get('severity', 'high'),
                'message': f"{metric_name} BELOW MIN: {value} < {rule['min']}",
            })
        elif value > rule.get('max', float('inf')):
            alerts.append({
                'metric': metric_name,
                'value': value,
                'direction': 'above_max',
                'threshold': rule['max'],
                'severity': rule.get('severity', 'high'),
                'message': f"{metric_name} ABOVE MAX: {value} > {rule['max']}",
            })
    return alerts


def check_threshold_alerts(metrics, rules):
    """Return readable threshold alerts for backward compatibility."""
    return [f"⚠️ {alert['message']}" for alert in build_threshold_alerts(metrics, rules)]


def detect_anomalies_zscore(series, threshold=2.0, rolling_window=None, min_periods=None):
    """Flag values beyond N standard deviations from a global or rolling mean."""
    if series is None or series.empty:
        return pd.Series(dtype=float)

    numeric_series = pd.to_numeric(series, errors='coerce').dropna()
    if numeric_series.empty:
        return pd.Series(dtype=float)

    if rolling_window is None:
        mean = numeric_series.mean()
        std = numeric_series.std()
        if pd.isna(std) or std == 0:
            return pd.Series(dtype=float)
        z_scores = np.abs((numeric_series - mean) / std)
    else:
        if rolling_window < 2:
            raise ValueError('rolling_window must be at least 2')
        periods = min_periods or rolling_window
        rolling = numeric_series.rolling(rolling_window, min_periods=periods)
        means = rolling.mean()
        stds = rolling.std()
        z_scores = ((numeric_series - means) / stds).abs()
    return numeric_series[z_scores > threshold]


def build_anomaly_report(series, metric_name='daily_revenue', threshold=2.0, rolling_window=None):
    """Create a structured anomaly report for monitoring and alerting."""
    numeric_series = pd.to_numeric(series, errors='coerce').dropna()
    anomalies = detect_anomalies_zscore(
        numeric_series,
        threshold=threshold,
        rolling_window=rolling_window,
    )
    if anomalies.empty:
        return {
            'metric_name': metric_name,
            'anomaly_count': 0,
            'severity': 'low',
            'anomalies': [],
        }

    mean = numeric_series.mean()
    std = numeric_series.std()
    anomaly_details = []
    for timestamp, value in anomalies.items():
        z_score = abs((value - mean) / std) if std else 0.0
        anomaly_details.append({
            'timestamp': timestamp.isoformat() if hasattr(timestamp, 'isoformat') else timestamp,
            'value': float(value),
            'expected_range': f"{mean - threshold * std:.2f}-{mean + threshold * std:.2f}",
            'z_score': round(float(z_score), 4),
            'severity': 'high' if z_score > 3 else 'medium',
        })

    return {
        'metric_name': metric_name,
        'anomaly_count': len(anomaly_details),
        'severity': 'high' if anomaly_details else 'low',
        'anomalies': anomaly_details,
    }


def monitor_metrics(metrics, rules, series_by_metric=None, threshold=2.0, rolling_window=None, anomaly_log_path=None):
    """Run threshold and statistical monitoring and optionally persist anomalies."""
    threshold_alerts = build_threshold_alerts(metrics, rules)
    anomaly_reports = []
    for metric_name, series in (series_by_metric or {}).items():
        report = build_anomaly_report(
            series,
            metric_name=metric_name,
            threshold=threshold,
            rolling_window=rolling_window,
        )
        anomaly_reports.append(report)

    if anomaly_log_path is not None:
        write_anomaly_log(
            series_by_metric or {},
            threshold=threshold,
            rolling_window=rolling_window,
            output_path=anomaly_log_path,
        )

    return {
        'threshold_alerts': threshold_alerts,
        'anomaly_reports': anomaly_reports,
        'alert_count': len(threshold_alerts) + sum(report['anomaly_count'] for report in anomaly_reports),
    }


def write_anomaly_log(series_by_metric, threshold=2.0, rolling_window=None, output_path='output/anomalies.csv'):
    """Persist every statistical anomaly with its expected range and severity."""
    rows = []
    for metric_name, series in series_by_metric.items():
        report = build_anomaly_report(series, metric_name, threshold, rolling_window)
        for anomaly in report['anomalies']:
            rows.append({
                'timestamp': anomaly['timestamp'],
                'metric': metric_name,
                'value': anomaly['value'],
                'expected_range': anomaly['expected_range'],
                'z_score': anomaly['z_score'],
                'severity': anomaly['severity'],
            })
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=['timestamp', 'metric', 'value', 'expected_range', 'z_score', 'severity']).to_csv(path, index=False)
    return path


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
