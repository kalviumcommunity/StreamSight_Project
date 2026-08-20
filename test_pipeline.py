import tempfile
import unittest
from pathlib import Path

import pandas as pd

from pipeline import aggregate, clean, ingest, write_output


class PipelineTests(unittest.TestCase):
    def test_clean_drops_invalid_amounts_and_preserves_input(self):
        source = pd.DataFrame(
            {
                "user_id": [1, None, 3, 4],
                "amount": [10, 20, -1, "invalid"],
            }
        )

        cleaned = clean(source)

        self.assertEqual(cleaned["user_id"].tolist(), [1])
        self.assertEqual(source["amount"].tolist(), [10, 20, -1, "invalid"])

    def test_aggregate_uses_defaults_for_engagement_data(self):
        source = pd.DataFrame({"user_id": [1, 2], "amount": [10.0, 20.0]})

        result = aggregate(source)

        self.assertEqual(result.to_dict("records"), [{
            "segment": "all",
            "total_revenue": 30.0,
            "order_count": 2,
            "avg_order": 15.0,
        }])
        self.assertNotIn("segment", source.columns)

    def test_pipeline_writes_cleaned_and_aggregate_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.csv"
            output_path = Path(directory) / "output"
            pd.DataFrame({"customer_id": [1], "amount": [25.0]}).to_csv(input_path, index=False)

            raw = ingest(input_path)
            write_output(clean(raw), aggregate(clean(raw)), output_path)

            self.assertTrue((output_path / "cleaned_data.csv").exists())
            self.assertTrue((output_path / "aggregated_metrics.csv").exists())


if __name__ == "__main__":
    unittest.main()