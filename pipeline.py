import argparse
import logging
import os
import pandas as pd
from datetime import datetime


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def ingest(file_path: str) -> pd.DataFrame:
    logger.info("Ingesting data from: %s", file_path)
    df = pd.read_csv(file_path)
    logger.info("Ingested %d rows", len(df))
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning data...")
    initial = len(df)
    if "customer_id" in df.columns:
        df = df.dropna(subset=["customer_id"])
    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df = df.dropna(subset=["amount"])
        df = df[df["amount"] > 0]
    logger.info("Cleaned: %d -> %d rows", initial, len(df))
    return df


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Aggregating...")
    if "segment" not in df.columns:
        df["segment"] = "all"
    if "order_id" not in df.columns:
        df["order_id"] = range(1, len(df) + 1)
    if "amount" not in df.columns:
        df["amount"] = 0

    agg = (
        df.groupby("segment")
        .agg(total_revenue=("amount", "sum"), order_count=("order_id", "count"), avg_order=("amount", "mean"))
        .reset_index()
    )
    logger.info("Aggregated %d segments", len(agg))
    return agg


def write_output(df: pd.DataFrame, agg: pd.DataFrame, output_dir: str) -> None:
    logger.info("Writing output to: %s", output_dir)
    os.makedirs(output_dir, exist_ok=True)
    cleaned_path = os.path.join(output_dir, "cleaned_data.csv")
    agg_path = os.path.join(output_dir, "aggregated_metrics.csv")
    df.to_csv(cleaned_path, index=False)
    agg.to_csv(agg_path, index=False)
    logger.info("Wrote %s and %s", cleaned_path, agg_path)


def main():
    parser = argparse.ArgumentParser(description="Run full pipeline: ingest, clean, aggregate, output")
    parser.add_argument("--input", required=False, default="data/engagement_data.csv", help="Path to input CSV file")
    parser.add_argument("--output", required=False, default="output", help="Output directory")
    args = parser.parse_args()

    start = datetime.utcnow()
    logger.info("Pipeline started at %s UTC", start.isoformat())
    try:
        raw = ingest(args.input)
        cleaned = clean(raw)
        agg = aggregate(cleaned)
        write_output(cleaned, agg, args.output)
    except Exception as e:
        logger.exception("Pipeline failed: %s", e)
        raise
    end = datetime.utcnow()
    logger.info("Pipeline finished at %s UTC (elapsed: %s)", end.isoformat(), end - start)


if __name__ == "__main__":
    main()
