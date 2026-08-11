import unittest
from database.data_layer import validate_data_layer


class TestDataLayerValidation(unittest.TestCase):
    def test_validate_data_layer(self):
        report = validate_data_layer(base_dir="database")
        self.assertIsInstance(report, dict)
        self.assertIn("views", report)
        self.assertIn("aggregations", report)
        self.assertTrue(all(view["valid_name"] for view in report["views"]))
        self.assertTrue(all(agg["valid_name"] for agg in report["aggregations"]))
        self.assertEqual(report["errors"], [])


if __name__ == "__main__":
    unittest.main()
