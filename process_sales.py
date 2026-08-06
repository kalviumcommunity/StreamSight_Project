# 1. IMPORTS - Everything the script needs at the top
import pandas as pd
import numpy as np
from datetime import datetime
import time
import logging
from pathlib import Path

from data_validation import analyze_missing_before, deduplicate_records, handle_outliers, impute_missing_values, validate_dataset, validate_merge

# 2. CONFIGURATION - Hard-coded paths, settings, thresholds
INPUT_FILE = "data/raw/sample_data.csv"
OUTPUT_FILE = "output/processed_sales.csv"
LOG_FILE = "logs/workflow.log"
MIN_AMOUNT = 0
CHURN_THRESHOLD_DAYS = 90

# 3. LOGGING SETUP - Capture what happens for debugging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 4. MAIN FUNCTIONS

def ingest_data(filepath):
    """
    Read CSV file into DataFrame.
    
    This function handles data ingestion from a CSV file. It validates
    that the file exists and returns a pandas DataFrame for downstream
    processing.
    
    Args:
        filepath (str): Path to the CSV file to read
        
    Returns:
        pd.DataFrame: Raw data from the CSV file
        
    Raises:
        FileNotFoundError: If the specified file does not exist
        ValueError: If the file is empty or cannot be parsed
        
    Example:
        >>> df = ingest_data("data/raw/sample_data.csv")
        >>> print(df.head())
    """
    try:
        filepath = Path(filepath)
        expected_columns = ['customer_id', 'transaction_date', 'amount', 'product_category']
        report, df = validate_dataset(filepath, expected_columns=expected_columns, allowed_extensions=['csv'], return_dataframe=True)

        if not report.get('valid', False):
            raise ValueError(report['checks'].get('schema') or report['checks'].get('file_exists') or report['checks'].get('format') or report['checks'].get('encoding') or 'Data validation failed')

        if df is None or df.empty:
            raise ValueError(f"File is empty: {filepath.absolute()}")

        logging.info(f"Ingested {len(df)} rows from {filepath}")
        return df

    except pd.errors.EmptyDataError:
        logging.error(f"File is empty or malformed: {filepath}")
        raise ValueError(f"File is empty or malformed: {filepath}")
    except Exception as e:
        logging.error(f"Error ingesting data from {filepath}: {str(e)}")
        raise


def process_data(df, min_amount=0):
    """
    Apply transformations to sales data.
    
    This function performs data cleaning and transformation including:
    - Removing duplicate transactions
    - Filtering out transactions below minimum amount threshold
    - Filling missing values with median
    - Calculating customer metrics (total spend, transaction count)
    
    Args:
        df (pd.DataFrame): Raw sales data with columns:
            - customer_id (int): Unique customer identifier
            - transaction_date (str): Date of transaction (YYYY-MM-DD)
            - amount (float): Transaction amount
            - product_category (str): Category of product purchased
        min_amount (float): Minimum transaction amount to include (default: 0)
        
    Returns:
        pd.DataFrame: Processed data with additional columns:
            - total_spend (float): Sum of all customer transactions
            - transaction_count (int): Number of transactions per customer
            
    Raises:
        ValueError: If DataFrame is empty or missing required columns
        
    Example:
        >>> clean_df = process_data(raw_df, min_amount=50)
        >>> print(clean_df.head())
    """
    if df.empty:
        raise ValueError("Input DataFrame cannot be empty")
    
    required_columns = ['customer_id', 'transaction_date', 'amount', 'product_category']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    rows_before = len(df)

    # Remove duplicate transactions while preserving the most complete record
    df, duplicate_audit, duplicate_comparison = deduplicate_records(
        df,
        subset=['customer_id', 'transaction_date'],
        strategy='most_complete',
        audit_path='output/removed_duplicates_audit.csv',
    )
    if duplicate_audit:
        logging.info(
            "Deduplication removed %s rows (%s%%) using %s",
            duplicate_comparison['rows_removed'],
            duplicate_comparison['removal_pct'],
            duplicate_comparison['strategy'],
        )

    # Filter transactions below minimum amount
    # Business rule: Small transactions may be errors or insignificant
    df = df[df['amount'] >= min_amount]
    
    # Profile the missing values before applying any rule
    missing_summary = analyze_missing_before(df)
    if missing_summary["missing_values"]:
        logging.info(f"Missing values before imputation: {missing_summary['missing_values']}")

    # Apply column-aware imputation strategies and capture the audit trail
    df, audit_log = impute_missing_values(
        df,
        critical_columns=['customer_id'],
        report_path='output/missing_value_report.json',
    )

    for entry in audit_log:
        logging.info(
            "Imputation strategy for %s: %s (before=%s, after=%s)",
            entry['column'],
            entry['strategy'],
            entry['before_nulls'],
            entry['after_nulls'],
        )

    df, outlier_audit = handle_outliers(
        df,
        column='amount',
        action='cap',
        strategy='iqr',
        factor=1.5,
        report_path='output/outlier_detection_report.json',
    )

    for entry in outlier_audit:
        logging.info(
            "Outlier handling for %s: %s count=%s action=%s",
            entry['column'],
            entry['strategy'],
            entry['outlier_count'],
            entry['action'],
        )
    
    # Convert transaction_date to datetime for analysis
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')

    # Extract time-based features that enable downstream aggregation and recency analysis
    df['day_of_week'] = df['transaction_date'].dt.day_name()
    df['dow_numeric'] = df['transaction_date'].dt.dayofweek
    df['hour_of_day'] = df['transaction_date'].dt.hour
    df['week_number'] = df['transaction_date'].dt.isocalendar().week.astype('Int64')
    df['days_since_purchase'] = (pd.Timestamp.now().normalize() - df['transaction_date'].dt.normalize()).dt.days
    
    # Calculate customer metrics
    # These metrics help identify high-value customers for targeting
    customer_metrics = df.groupby('customer_id').agg({
        'amount': ['sum', 'count'],
        'transaction_date': ['min', 'max']
    }).reset_index()
    
    customer_metrics.columns = ['customer_id', 'total_spend', 'transaction_count', 
                                 'first_purchase', 'last_purchase']
    
     # Validate the join explicitly before merging
    merged_df, merge_report = validate_merge(
        df,
        customer_metrics,
        on='customer_id',
        how='left',
        output_unmatched_left='output/unmatched_customers.csv',
        output_unmatched_right='output/unmatched_customer_metrics.csv',
        report_path='output/join_validation_report.json',
    )

    logging.info(
        "Join validation report: left_rows=%s right_rows=%s merged_rows=%s unmatched_left_rows=%s unmatched_right_rows=%s",
        merge_report['left_rows'],
        merge_report['right_rows'],
        merge_report['merged_rows'],
        merge_report['unmatched_left_rows'],
        merge_report['unmatched_right_rows'],
    )

    df = merged_df
 
    # Merge metrics back to original data
    df = df.merge(customer_metrics, on='customer_id', how='left')
    
    # ------------------------------
    # NumPy vectorized feature engineering
    # ------------------------------
    # Min-max normalization for transaction-level `amount`
    try:
        revenue_array = df['amount'].values.astype(float)
        r_min = revenue_array.min()
        r_max = revenue_array.max()
        if r_max - r_min == 0:
            df['amount_normalized'] = 0.0
        else:
            df['amount_normalized'] = (revenue_array - r_min) / (r_max - r_min)

        # Z-score normalization for `amount`
        r_mean = revenue_array.mean()
        r_std = revenue_array.std()
        if r_std == 0:
            df['amount_zscore'] = 0.0
        else:
            df['amount_zscore'] = (revenue_array - r_mean) / r_std

        # Rank customers/transactions by `amount` (1 = highest)
        order = np.argsort(-revenue_array)
        ranks = np.empty(len(revenue_array), dtype=int)
        ranks[order] = np.arange(1, len(revenue_array) + 1)
        df['amount_rank'] = ranks
    except Exception:
        # If column missing or conversion fails, skip silently (upstream validations exist)
        pass

    # Vectorize same set of calculations for per-customer `total_spend` if available
    if 'total_spend' in df.columns:
        try:
            total_array = df['total_spend'].values.astype(float)
            t_min, t_max = total_array.min(), total_array.max()
            if t_max - t_min == 0:
                df['total_spend_normalized'] = 0.0
            else:
                df['total_spend_normalized'] = (total_array - t_min) / (t_max - t_min)

            t_mean, t_std = total_array.mean(), total_array.std()
            if t_std == 0:
                df['total_spend_zscore'] = 0.0
            else:
                df['total_spend_zscore'] = (total_array - t_mean) / t_std

            order_t = np.argsort(-total_array)
            ranks_t = np.empty(len(total_array), dtype=int)
            ranks_t[order_t] = np.arange(1, len(total_array) + 1)
            df['total_spend_rank'] = ranks_t
        except Exception:
            pass

    # Quick performance comparison helper (loop vs NumPy)
    def _timing_demo(series: pd.Series) -> dict:
        a = series.values.astype(float)
        start = time.time()
        # loop version
        tmp = []
        for v in series:
            tmp.append(v * 1.1)
        loop_time = time.time() - start

        start = time.time()
        _ = a * 1.1
        np_time = time.time() - start

        speedup = float('inf') if np_time == 0 else loop_time / np_time
        return {"loop": loop_time, "numpy": np_time, "speedup": speedup}

    try:
        perf = _timing_demo(df['amount'])
        logging.info("Normalization timing - loop: %.6fs, numpy: %.6fs, speedup: %.1fx", perf['loop'], perf['numpy'], perf['speedup'])
    except Exception:
        pass
    
     rows_after = len(df)
    logging.info(f"Processing: {rows_before} rows → {rows_after} rows")
    logging.info(f"Unique customers: {df['customer_id'].nunique()}")
    
    return df


def build_segment_insights(df, value_column='amount', segment_column='product_category', time_column='day_of_week'):
    """
    Build grouped segment insights using split-apply-combine aggregation.

    The function summarizes revenue by segment and time-based dimension, ranks
    segments by total revenue, and returns a pivot table for quick comparison.

    Args:
        df (pd.DataFrame): Processed sales data
        value_column (str): Numeric column to aggregate
        segment_column (str): Column used as the segment key
        time_column (str): Column used as the secondary grouping dimension

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: Ranked metrics and pivot table
    """
    if df.empty:
        raise ValueError("Input DataFrame cannot be empty")

    required_columns = [segment_column, value_column]
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns for insights: {missing_cols}")

    if time_column not in df.columns:
        if 'transaction_date' in df.columns:
            df = df.copy()
            df[time_column] = pd.to_datetime(df['transaction_date'], errors='coerce').dt.day_name()
        else:
            raise ValueError(f"Missing required column for insights: {time_column}")

    metrics_df = (
        df.groupby([segment_column, time_column], dropna=False)
        .agg(
            total_revenue=(value_column, 'sum'),
            transaction_count=(value_column, 'count'),
            avg_order_value=(value_column, 'mean'),
        )
        .reset_index()
    )

    metrics_df['revenue_rank'] = metrics_df['total_revenue'].rank(method='dense', ascending=False).astype(int)
    metrics_df = metrics_df.sort_values(['revenue_rank', 'total_revenue'], ascending=[True, False]).reset_index(drop=True)

    pivot_df = pd.pivot_table(
        df,
        values=value_column,
        index=segment_column,
        columns=time_column,
        aggfunc='sum',
        fill_value=0,
    )

    return metrics_df, pivot_df


def output_results(df, filepath):
    """
    Write processed results to CSV file.
    
    This function handles the output of processed data to a CSV file.
    It creates the output directory if it doesn't exist and writes
    the DataFrame with no index for cleaner output.
    
    Args:
        df (pd.DataFrame): Processed data to write
        filepath (str): Path where the CSV file should be saved
        
    Raises:
        ValueError: If DataFrame is empty
        IOError: If unable to write to the specified file
        
    Example:
        >>> output_results(processed_df, "output/processed_sales.csv")
    """
    if df.empty:
        raise ValueError("Cannot output empty DataFrame")
    
    try:
        filepath = Path(filepath)
        
        # Create output directory if it doesn't exist
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to CSV without index
        df.to_csv(filepath, index=False)
        
        logging.info(f"Output saved: {filepath.absolute()}")
        print(f"✓ Processed {len(df)} records")
        print(f"✓ Output saved to: {filepath.absolute()}")
        
    except Exception as e:
        logging.error(f"Error writing output to {filepath}: {str(e)}")
        raise


# 5. MAIN EXECUTION - Orchestrate the workflow
if __name__ == "__main__":
    try:
        print("=" * 50)
        print("StreamSight Sales Data Pipeline")
        print("=" * 50)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        print("Step 1: Validating and ingesting data...")
        data = ingest_data(INPUT_FILE)
        print(f"  ✓ Loaded {len(data)} raw transactions")
        print("  ✓ Validation report saved to output/intake_report.json")
        
        print("\nStep 2: Processing data...")
        clean_data = process_data(data, min_amount=MIN_AMOUNT)
        print(f"  ✓ Processed {len(clean_data)} transactions")
        print(f"  ✓ {clean_data['customer_id'].nunique()} unique customers")
        
        print("\nStep 3: Generating segment insights...")
        segment_metrics, segment_pivot = build_segment_insights(clean_data)
        segment_metrics.to_csv('output/segment_insights.csv', index=False)
        segment_pivot.to_csv('output/segment_pivot.csv')
        print("  ✓ Segment metrics saved to output/segment_insights.csv")
        print("  ✓ Segment pivot table saved to output/segment_pivot.csv")
        
        print("\nStep 4: Outputting results...")
        output_results(clean_data, OUTPUT_FILE)
        
        print("\n" + "=" * 50)
        print("✓ Workflow completed successfully")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
    except Exception as e:
        logging.error(f"Workflow failed: {str(e)}")
        print(f"\n✗ Error: {str(e)}")
        print("Check logs/workflow.log for details")
        exit(1)
