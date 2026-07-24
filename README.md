# StreamSight_Project

A production-ready data pipeline demonstrating Python data workflow foundations.

## Team
Aman Tanmay Shubhdeep

## Overview

This project implements a sales data processing pipeline using the three-function pattern (ingest, process, output) for production-ready data workflows. The pipeline processes customer transaction data, cleans and transforms it, and outputs enriched results with customer metrics.

## Project Structure

```
StreamSight_Project/
├── data/
│   └── raw/
│       └── sample_data.csv       # Input transaction data
├── output/
│   └── processed_sales.csv       # Output processed data
├── logs/
│   └── workflow.log              # Pipeline execution logs
├── process_sales.py              # Main pipeline script
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Installation

Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the data pipeline:

```bash
python process_sales.py
```

The pipeline will:
1. Ingest raw sales data from `data/raw/sample_data.csv`
2. Process the data (remove duplicates, filter transactions, calculate customer metrics)
3. Output results to `output/processed_sales.csv`
4. Log all operations to `logs/workflow.log`

## Pipeline Functions

### ingest_data(filepath)
Reads CSV file into a pandas DataFrame. Handles file validation and error logging.

### process_data(df, min_amount=0)
Transforms raw data by:
- Removing duplicate transactions
- Filtering transactions below minimum amount
- Filling missing values with median
- Calculating customer metrics (total spend, transaction count)

### output_results(df, filepath)
Writes processed results to CSV file. Creates output directory if needed.

## Configuration

Modify these constants in `process_sales.py` to customize the pipeline:

- `INPUT_FILE`: Path to input data file
- `OUTPUT_FILE`: Path to output file
- `LOG_FILE`: Path to log file
- `MIN_AMOUNT`: Minimum transaction amount threshold
- `CHURN_THRESHOLD_DAYS`: Customer churn threshold (for future use)

## Logging

All pipeline operations are logged to `logs/workflow.log` with timestamps and severity levels. Check this file for debugging and audit trails.

## Design Principles

This project follows production data engineering best practices:

- **Separation of concerns**: Ingest, process, and output are separate functions
- **Configuration at top**: All hard-coded values in one place
- **Comprehensive logging**: Every operation is logged for debugging
- **Error handling**: Graceful error handling with informative messages
- **Documentation**: Complete docstrings for all functions
- **Modularity**: Functions can be tested and reused independently
