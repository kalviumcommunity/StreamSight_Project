# 1. IMPORTS - Everything the script needs at the top
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from pathlib import Path

from data_validation import analyze_missing_before, deduplicate_records, handle_outliers, impute_missing_values, validate_dataset

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
    
    # Merge metrics back to original data
    df = df.merge(customer_metrics, on='customer_id', how='left')
    
    rows_after = len(df)
    logging.info(f"Processing: {rows_before} rows → {rows_after} rows")
    logging.info(f"Unique customers: {df['customer_id'].nunique()}")
    
    return df


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
        
        print("\nStep 3: Outputting results...")
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
