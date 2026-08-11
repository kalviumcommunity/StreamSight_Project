import unittest

from compare_metrics import compare_metrics, build_validation_summary


class CompareMetricsTests(unittest.TestCase):
    def test_compare_metrics_match_exact(self):
        sql_metrics = {"active_users": 1000, "revenue": 50000}
        python_metrics = {"active_users": 1000, "revenue": 50000}
        report = compare_metrics(sql_metrics, python_metrics, tolerance=0.0)
        self.assertTrue(report["matches"])
        self.assertEqual(report["discrepancies"], [])

    def test_compare_metrics_detects_discrepancy(self):
        sql_metrics = {"active_users": 1000, "revenue": 50000}
        python_metrics = {"active_users": 1050, "revenue": 49900}
        report = compare_metrics(sql_metrics, python_metrics, tolerance={"active_users": 20, "revenue": 50})
        self.assertFalse(report["matches"])
        self.assertEqual(len(report["discrepancies"]), 2)

    def test_compare_metrics_handles_non_numeric(self):
        sql_metrics = {"active_users": "1000"}
        python_metrics = {"active_users": None}
        report = compare_metrics(sql_metrics, python_metrics, tolerance=0.0)
        self.assertFalse(report["matches"])

    def test_build_validation_summary(self):
        report = {
            "matches": False,
            "sql_metrics": {"active_users": 1000},
            "python_metrics": {"active_users": 900},
            "discrepancies": [
                {
                    "metric": "active_users",
                    "sql_value": 1000,
                    "python_value": 900,
                    "absolute_difference": 100,
                    "relative_difference_pct": 11.11,
                    "tolerance": 5,
                }
            ],
        }
        summary = build_validation_summary(report)
        self.assertIn("Metric Drift Validation Report", summary)
        self.assertIn("Discrepancies:", summary)
