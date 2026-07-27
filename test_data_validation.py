import os
import tempfile
import unittest

import pandas as pd

from data_validation import validate_dataset, validate_file_exists, validate_schema


class DataValidationTests(unittest.TestCase):
    def test_missing_file_is_reported(self):
        ok, message = validate_file_exists("data/raw/does_not_exist.csv")
        self.assertFalse(ok)
        self.assertIn("File not found", message)

    def test_schema_validation_reports_missing_and_extra_columns(self):
        df = pd.DataFrame({"customer_id": [1], "amount": [10.0], "unexpected": [True]})
        ok, message = validate_schema(df, ["customer_id", "transaction_date", "amount", "product_category"])
        self.assertFalse(ok)
        self.assertIn("Missing", message)
        self.assertIn("Extra", message)

    def test_valid_dataset_report_passes_for_sample_file(self):
        expected_columns = ["customer_id", "transaction_date", "amount", "product_category"]
        report = validate_dataset("data/raw/sample_data.csv", expected_columns=expected_columns)

        self.assertTrue(report["valid"])
        self.assertEqual(report["statistics"]["rows"], 18)
        self.assertEqual(report["statistics"]["columns"], 4)
        self.assertIn("file_exists", report["checks"])
        self.assertIn("schema", report["checks"])


if __name__ == "__main__":
    unittest.main()
