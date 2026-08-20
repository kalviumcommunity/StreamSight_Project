import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


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
    cleaned = df.copy()
    if "customer_id" in cleaned.columns:
        cleaned = cleaned.dropna(subset=["customer_id"])
    elif "user_id" in cleaned.columns:
        cleaned = cleaned.dropna(subset=["user_id"])
    if "amount" in cleaned.columns:
        cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce")
        cleaned = cleaned.dropna(subset=["amount"])
        cleaned = cleaned[cleaned["amount"] > 0]
    logger.info("Cleaned: %d -> %d rows", initial, len(cleaned))
    return cleaned.reset_index(drop=True)


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Aggregating...")
    aggregated = df.copy()
    if "segment" not in aggregated.columns:
        aggregated["segment"] = "all"
    if "order_id" not in aggregated.columns:
        aggregated["order_id"] = range(1, len(aggregated) + 1)
    if "amount" not in aggregated.columns:
        aggregated["amount"] = 0

    agg = (
        aggregated.groupby("segment", dropna=False)
        .agg(total_revenue=("amount", "sum"), order_count=("order_id", "count"), avg_order=("amount", "mean"))
        .reset_index()
    )
    logger.info("Aggregated %d segments", len(agg))
    return agg


def write_output(df: pd.DataFrame, agg: pd.DataFrame, output_dir: str) -> None:
    logger.info("Writing output to: %s", output_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    cleaned_path = output_path / "cleaned_data.csv"
    agg_path = output_path / "aggregated_metrics.csv"
    df.to_csv(cleaned_path, index=False)
    agg.to_csv(agg_path, index=False)
    logger.info("Wrote %s and %s", cleaned_path, agg_path)


def main():
    parser = argparse.ArgumentParser(description="Run full pipeline: ingest, clean, aggregate, output")
    parser.add_argument("--input", required=False, default="data/engagement_data.csv", help="Path to input CSV file")
    parser.add_argument("--output", required=False, default="output", help="Output directory")
    args = parser.parse_args()

    start = datetime.now(timezone.utc)
    logger.info("Pipeline started at %s UTC", start.isoformat())
    try:
        raw = ingest(args.input)
        cleaned = clean(raw)
        agg = aggregate(cleaned)
        write_output(cleaned, agg, args.output)
    except Exception as e:
        logger.exception("Pipeline failed: %s", e)
        raise
    end = datetime.now(timezone.utc)
    logger.info("Pipeline finished at %s UTC (elapsed: %s)", end.isoformat(), end - start)


if __name__ == "__main__":
    main()
