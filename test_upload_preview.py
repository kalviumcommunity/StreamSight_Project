import io
import unittest

import pandas as pd

from upload_preview import build_column_summary, build_preview_metrics, load_uploaded_dataframe


class UploadPreviewTests(unittest.TestCase):
    def test_load_uploaded_dataframe_csv(self):
        payload = "customer_id,amount,category\n1,10.5,A\n2,20.0,B\n"
        uploaded = io.BytesIO(payload.encode("utf-8"))
        uploaded.name = "sample.csv"

        df = load_uploaded_dataframe(uploaded)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertEqual(list(df.columns), ["customer_id", "amount", "category"])

    def test_load_uploaded_dataframe_json(self):
        payload = '{"customer_id": [1, 2], "amount": [10.5, 20.0], "category": ["A", "B"]}'
        uploaded = io.BytesIO(payload.encode("utf-8"))
        uploaded.name = "sample.json"

        df = load_uploaded_dataframe(uploaded)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertEqual(df["category"].tolist(), ["A", "B"])

    def test_build_column_summary_and_metrics(self):
        df = pd.DataFrame(
            {
                "customer_id": [1, None, 3],
                "amount": [10.5, 20.0, None],
                "category": ["A", "B", "A"],
            }
        )

        summary = build_column_summary(df)
        metrics = build_preview_metrics(df)

        self.assertEqual(list(summary.columns), ["Column", "Type", "Non-Null", "Null Count", "Null %"])
        self.assertEqual(metrics["rows"], 3)
        self.assertEqual(metrics["columns"], 3)
        self.assertEqual(summary.loc[summary["Column"] == "customer_id", "Null Count"].iloc[0], 1)
        self.assertAlmostEqual(summary.loc[summary["Column"] == "amount", "Null %"].iloc[0], 33.3)

    def test_loader_cleans_headers_whitespace_and_empty_rows(self):
        payload = " customer_id , amount \n1,10.5\n,   \n"
        uploaded = io.BytesIO(payload.encode("utf-8"))
        uploaded.name = "sample.csv"

        df = load_uploaded_dataframe(uploaded)

        self.assertEqual(list(df.columns), ["customer_id", "amount"])
        self.assertEqual(len(df), 1)


if __name__ == "__main__":
    unittest.main()
