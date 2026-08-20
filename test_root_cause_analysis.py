import pandas as pd
from pathlib import Path
from tempfile import TemporaryDirectory

from root_cause_analysis import (
    check_threshold_alerts,
    detect_anomalies_zscore,
    build_anomaly_report,
)


def test_check_threshold_alerts_flags_out_of_range_metrics():
    metrics = {"daily_revenue": 2500, "transaction_count": 50, "signup_rate": 5}
    rules = {
        "daily_revenue": {"min": 5000, "max": 50000},
        "transaction_count": {"min": 100, "max": 10000},
        "signup_rate": {"min": 10, "max": 500},
    }

    alerts = check_threshold_alerts(metrics, rules)

    assert len(alerts) == 3
    assert any("daily_revenue" in alert for alert in alerts)
    assert any("transaction_count" in alert for alert in alerts)
    assert any("signup_rate" in alert for alert in alerts)


def test_detect_anomalies_zscore_flags_statistical_outliers():
    series = pd.Series([100, 105, 103, 110, 102, 950, 104, 108])

    anomalies = detect_anomalies_zscore(series, threshold=2.0)

    assert anomalies.index.tolist() == [5]
    assert anomalies.iloc[0] == 950


def test_build_anomaly_report_returns_structured_findings():
    series = pd.Series([100, 105, 103, 110, 102, 950, 104, 108], index=pd.date_range("2025-01-01", periods=8, freq="D"))

    report = build_anomaly_report(series, metric_name="daily_revenue")

    assert report["metric_name"] == "daily_revenue"
    assert report["anomaly_count"] == 1
    assert report["severity"] == "high"
    assert report["anomalies"][0]["value"] == 950


def test_monitor_metrics_persists_statistical_anomaly_log():
    from root_cause_analysis import monitor_metrics

    series = pd.Series([100, 102, 98, 101, 100, 500], index=pd.date_range("2026-01-01", periods=6, freq="D"))
    with TemporaryDirectory() as directory:
        log_path = Path(directory) / "anomalies.csv"
        result = monitor_metrics(
            {"daily_revenue": 2500},
            {"daily_revenue": {"min": 5000, "max": 50000}},
            {"daily_revenue": series},
            anomaly_log_path=log_path,
        )

        assert len(result["threshold_alerts"]) == 1
        assert result["anomaly_reports"][0]["anomaly_count"] == 1
        assert result["alert_count"] == 2
        assert log_path.exists()
