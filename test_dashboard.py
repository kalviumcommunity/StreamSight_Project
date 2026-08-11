import unittest
import pandas as pd

from dashboard import (
    build_dashboard_kpis,
    build_dashboard_segments,
    build_dashboard_trends,
)


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "transaction_date": ["2026-01-01", "2026-01-08", "2026-02-01", "2026-02-15"],
                "amount": [100.0, 150.0, 200.0, 250.0],
                "user_id": [1, 2, 1, 3],
                "customer_type": ["Enterprise", "SMB", "Enterprise", "SMB"],
                "product_category": ["Movies", "Series", "Movies", "Series"],
                "payment_status": ["Success", "Success", "Failed", "Success"],
            }
        )

    def test_build_dashboard_kpis(self):
        kpis = build_dashboard_kpis(self.df)
        self.assertIn("monthly_active_users", kpis)
        self.assertIn("total_revenue", kpis)
        self.assertIn("payment_success_rate", kpis)
        self.assertGreater(kpis["total_revenue"], 0)
        self.assertGreaterEqual(kpis["payment_success_rate"], 0.0)

    def test_build_dashboard_trends(self):
        trends = build_dashboard_trends(self.df)
        self.assertIn("monthly_revenue", trends)
        self.assertIn("weekly_active_users", trends)
        self.assertEqual(len(trends["monthly_revenue"]), 2)
        self.assertEqual(len(trends["weekly_active_users"]), 3)

    def test_build_dashboard_segments(self):
        segments = build_dashboard_segments(self.df)
        self.assertIn("revenue_by_customer_type", segments)
        self.assertIn("revenue_by_product_category", segments)
        self.assertEqual(len(segments["revenue_by_customer_type"]), 2)
        self.assertEqual(len(segments["revenue_by_product_category"]), 2)


if __name__ == "__main__":
    unittest.main()
