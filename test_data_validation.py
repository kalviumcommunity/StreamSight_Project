import os
import tempfile
import unittest

import pandas as pd

from data_validation import (
    deduplicate_records,
    validate_data_quality,
    validate_dataset,
    validate_file_exists,
    validate_schema,
)


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

    def test_quality_validation_reports_missing_values_and_duplicates(self):
        df = pd.DataFrame({
            "customer_id": [1, 1, 2],
            "transaction_date": ["2025-01-15", "2025-01-15", "2025-01-20"],
            "amount": [150.5, 150.5, None],
            "product_category": ["Electronics", "Electronics", "Books"],
        })

        ok, message = validate_data_quality(df)

        self.assertFalse(ok)
        self.assertIn("missing", message.lower())
        self.assertIn("duplicate", message.lower())

    def test_valid_dataset_report_passes_for_sample_file(self):
        expected_columns = ["customer_id", "transaction_date", "amount", "product_category"]
        report = validate_dataset("data/raw/sample_data.csv", expected_columns=expected_columns)

        self.assertTrue(report["valid"])
        self.assertEqual(report["statistics"]["rows"], 18)
        self.assertEqual(report["statistics"]["columns"], 4)
        self.assertIn("file_exists", report["checks"])
        self.assertIn("schema", report["checks"])

    def test_deduplicate_records_logs_removed_rows_and_writes_audit(self):
        df = pd.DataFrame(
            {
                "customer_id": [1, 1, 2, 2],
                "transaction_date": ["2025-01-01", "2025-01-01", "2025-02-02", "2025-02-02"],
                "amount": [100.0, None, 50.0, 50.0],
                "product_category": ["Electronics", None, "Books", "Books"],
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            audit_path = os.path.join(tmpdir, "duplicate_audit.csv")
            deduped_df, audit_log, comparison = deduplicate_records(
                df,
                subset=["customer_id", "transaction_date"],
                strategy="most_complete",
                audit_path=audit_path,
            )

            self.assertEqual(len(deduped_df), 2)
            self.assertEqual(comparison["rows_removed"], 2)
            self.assertEqual(len(audit_log), 2)
            self.assertTrue(os.path.exists(audit_path))


if __name__ == "__main__":
    unittest.main()
