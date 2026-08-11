from typing import Any, Dict, Optional, Union


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _relative_diff(actual: float, expected: float) -> float:
    if expected == 0:
        return abs(actual - expected)
    return abs((actual - expected) / expected) * 100


def compare_metrics(
    sql_metrics: Dict[str, Any],
    python_metrics: Dict[str, Any],
    tolerance: Union[float, Dict[str, float]] = 0.0,
) -> Dict[str, Any]:
    """Compare SQL and Python metrics and report drift.

    Args:
        sql_metrics: Metrics computed from the SQL layer.
        python_metrics: Metrics computed from the Python layer.
        tolerance: Global or per-metric numeric tolerance.

    Returns:
        A validation report with matched status and discrepancies.
    """
    if isinstance(tolerance, dict):
        tolerance_map = tolerance
    else:
        tolerance_map = {}
    global_tolerance = None if isinstance(tolerance, dict) else float(tolerance)

    report = {
        "sql_metrics": sql_metrics,
        "python_metrics": python_metrics,
        "matches": True,
        "discrepancies": [],
    }

    metric_names = sorted(set(sql_metrics) | set(python_metrics))

    for metric in metric_names:
        sql_value = sql_metrics.get(metric)
        py_value = python_metrics.get(metric)

        if sql_value == py_value:
            continue

        sql_float = _safe_float(sql_value)
        py_float = _safe_float(py_value)
        metric_tolerance = tolerance_map.get(metric, global_tolerance)

        if sql_float is not None and py_float is not None:
            absolute_diff = abs(sql_float - py_float)
            relative_diff = _relative_diff(sql_float, py_float)
            threshold = metric_tolerance if metric_tolerance is not None else 0.0
            grown = absolute_diff > threshold
            if not grown:
                continue
            report["matches"] = False
            report["discrepancies"].append(
                {
                    "metric": metric,
                    "sql_value": sql_value,
                    "python_value": py_value,
                    "absolute_difference": absolute_diff,
                    "relative_difference_pct": relative_diff,
                    "tolerance": threshold,
                }
            )
        else:
            report["matches"] = False
            report["discrepancies"].append(
                {
                    "metric": metric,
                    "sql_value": sql_value,
                    "python_value": py_value,
                    "reason": "Non-numeric or mismatched types require manual review.",
                }
            )

    return report


def build_validation_summary(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("Metric Drift Validation Report")
    lines.append("=============================")
    lines.append(f"Overall match: {report['matches']}")
    lines.append(f"Compared metrics: {len(report['sql_metrics'])} SQL metrics, {len(report['python_metrics'])} Python metrics")

    if report["discrepancies"]:
        lines.append("")
        lines.append("Discrepancies:")
        for diff in report["discrepancies"]:
            if "absolute_difference" in diff:
                lines.append(
                    f"- {diff['metric']}: SQL={diff['sql_value']}, Python={diff['python_value']}, "
                    f"abs_diff={diff['absolute_difference']:.4f}, rel_diff={diff['relative_difference_pct']:.2f}%, tolerance={diff['tolerance']}"
                )
            else:
                lines.append(
                    f"- {diff['metric']}: SQL={diff['sql_value']}, Python={diff['python_value']} ({diff['reason']})"
                )
    else:
        lines.append("")
        lines.append("No discrepancies detected within tolerance.")

    return "\n".join(lines)
