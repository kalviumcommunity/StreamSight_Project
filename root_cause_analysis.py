import os
import pandas as pd

os.makedirs('output', exist_ok=True)


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
