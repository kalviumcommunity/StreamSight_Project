import os
import time
import sqlite3
import pandas as pd
from sqlalchemy import create_engine


"""
QUERY OPTIMIZATION ANALYSIS

This script demonstrates three common SQL optimization techniques:

1. SELECT * -> Explicit column selection
2. Filter data before JOIN
3. Nested subqueries -> CTEs

The optimized queries reduce unnecessary data transfer,
reduce intermediate datasets, and improve readability.
"""


# ============================================================
# DATABASE CONNECTION
# ============================================================

DATABASE_PATH = "analytics.db"

engine = create_engine(f"sqlite:///{DATABASE_PATH}")

print("✓ Database connection created")


# ============================================================
# CHECK DATABASE TABLES
# ============================================================

with engine.connect() as conn:
    tables = conn.exec_driver_sql(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()

print("\nDATABASE TABLES:")
for table in tables:
    print(" -", table[0])


# ============================================================
# CHECK WHETHER OUR TABLE EXISTS
# ============================================================

table_name = "customers_cleaned"

with engine.connect() as conn:
    exists = conn.exec_driver_sql(
        f"""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='{table_name}'
        """
    ).fetchone()

if not exists:
    raise ValueError(
        f"Table '{table_name}' does not exist in analytics.db"
    )

print(f"\n✓ Table '{table_name}' found")


# ============================================================
# TASK 1
# SELECT * VS EXPLICIT COLUMNS
# ============================================================

print("\n" + "=" * 60)
print("TASK 1: SELECT * VS EXPLICIT COLUMNS")
print("=" * 60)


"""
Original query:

SELECT * fetches every column from the table.

This is inefficient because the analysis does not necessarily
need every available column.

The optimized query selects only the columns required for
business analysis.
"""


original_query = """
SELECT *
FROM customers_cleaned
LIMIT 1000
"""


optimized_query = """
SELECT
    user_id,
    video_id,
    transaction_date,
    amount,
    customer_type,
    product_category
FROM customers_cleaned
LIMIT 1000
"""


# Run original query
start_time = time.perf_counter()

original_result = pd.read_sql(
    original_query,
    engine
)

original_time = time.perf_counter() - start_time


# Run optimized query
start_time = time.perf_counter()

optimized_result = pd.read_sql(
    optimized_query,
    engine
)

optimized_time = time.perf_counter() - start_time


print("\nOriginal columns:")
print(original_result.columns.tolist())

print("\nOptimized columns:")
print(optimized_result.columns.tolist())

print(
    f"\nOriginal column count: "
    f"{original_result.shape[1]}"
)

print(
    f"Optimized column count: "
    f"{optimized_result.shape[1]}"
)


if original_result.shape[1] > 0:

    reduction = (
        (
            original_result.shape[1]
            - optimized_result.shape[1]
        )
        / original_result.shape[1]
    ) * 100

    print(
        f"Column reduction: {reduction:.1f}%"
    )


print(
    f"\nOriginal execution time: "
    f"{original_time:.6f} seconds"
)

print(
    f"Optimized execution time: "
    f"{optimized_time:.6f} seconds"
)


# Memory comparison

original_memory = (
    original_result.memory_usage(
        deep=True
    ).sum()
)

optimized_memory = (
    optimized_result.memory_usage(
        deep=True
    ).sum()
)


print(
    f"\nOriginal memory usage: "
    f"{original_memory:,} bytes"
)

print(
    f"Optimized memory usage: "
    f"{optimized_memory:,} bytes"
)


# ============================================================
# TASK 2
# FILTER BEFORE JOIN
# ============================================================

print("\n" + "=" * 60)
print("TASK 2: FILTER BEFORE JOIN")
print("=" * 60)


"""
Our dataset contains one table, so we demonstrate the principle
using a filtered CTE before the analytical operation.

The important optimization is:

    Filter first
        ↓
    Work with smaller dataset
        ↓
    Perform further operations

This prevents unnecessary processing of rows that will never
be used in the final analysis.
"""


# Count all transactions

transactions_count_query = """
SELECT COUNT(*) AS total_rows
FROM customers_cleaned
"""

transactions_count = pd.read_sql(
    transactions_count_query,
    engine
).iloc[0, 0]


print(
    f"\nFull table rows: "
    f"{transactions_count:,}"
)


# Count filtered transactions

filtered_transactions_query = """
SELECT COUNT(*) AS filtered_rows
FROM customers_cleaned
WHERE amount > 0
AND watch_duration >= 0
"""

filtered_transactions = pd.read_sql(
    filtered_transactions_query,
    engine
).iloc[0, 0]


print(
    f"Filtered rows: "
    f"{filtered_transactions:,}"
)


if transactions_count > 0:

    percentage = (
        filtered_transactions
        / transactions_count
    ) * 100

    reduction_factor = (
        transactions_count
        / filtered_transactions
        if filtered_transactions > 0
        else 0
    )

    print(
        f"Rows remaining after filtering: "
        f"{percentage:.1f}%"
    )

    if reduction_factor:
        print(
            f"Reduction factor: "
            f"{reduction_factor:.1f}x"
        )


# Original style

original_filter_query = """
SELECT
    user_id,
    video_id,
    amount,
    customer_type,
    product_category
FROM customers_cleaned
WHERE amount > 0
AND watch_duration >= 0
"""


original_filter_result = pd.read_sql(
    original_filter_query,
    engine
)


# Optimized style using CTE

optimized_filter_query = """
WITH filtered_data AS (

    SELECT
        user_id,
        video_id,
        amount,
        customer_type,
        product_category

    FROM customers_cleaned

    WHERE amount > 0
    AND watch_duration >= 0
)

SELECT
    user_id,
    video_id,
    amount,
    customer_type,
    product_category

FROM filtered_data
"""


optimized_filter_result = pd.read_sql(
    optimized_filter_query,
    engine
)


print(
    f"\nOriginal result rows: "
    f"{len(original_filter_result)}"
)

print(
    f"Optimized result rows: "
    f"{len(optimized_filter_result)}"
)


# ============================================================
# TASK 3
# CTE FOR READABILITY
# ============================================================

print("\n" + "=" * 60)
print("TASK 3: CTE FOR READABILITY")
print("=" * 60)


"""
Instead of deeply nested subqueries, we use named CTEs.

CTE 1:
    valid_transactions

Filters invalid transaction records.

CTE 2:
    segment_metrics

Calculates metrics for each customer segment.

Final SELECT:
    Returns the segment-level result.

Each step can be tested independently.
"""


nested_query = """
SELECT
    customer_type,
    AVG(amount) AS avg_transaction_value,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_revenue

FROM customers_cleaned

WHERE amount > 0

GROUP BY customer_type

ORDER BY avg_transaction_value DESC
"""


cte_query = """
WITH valid_transactions AS (

    -- Step 1:
    -- Keep only valid positive-value transactions.

    SELECT
        user_id,
        amount,
        customer_type,
        product_category

    FROM customers_cleaned

    WHERE amount > 0
),

segment_metrics AS (

    -- Step 2:
    -- Calculate metrics for every customer segment.

    SELECT
        customer_type,
        AVG(amount) AS avg_transaction_value,
        COUNT(*) AS transaction_count,
        SUM(amount) AS total_revenue

    FROM valid_transactions

    GROUP BY customer_type
)

-- Step 3:
-- Return final segment-level metrics.

SELECT
    customer_type,
    avg_transaction_value,
    transaction_count,
    total_revenue

FROM segment_metrics

ORDER BY avg_transaction_value DESC
"""


# Execute nested query

nested_result = pd.read_sql(
    nested_query,
    engine
)


# Execute CTE query

cte_result = pd.read_sql(
    cte_query,
    engine
)


print("\nNested query result:")
print(nested_result)


print("\nCTE query result:")
print(cte_result)


# ============================================================
# VALIDATE RESULTS
# ============================================================

print("\nRESULT VALIDATION")
print("-" * 40)


if nested_result.equals(cte_result):

    print(
        "✓ Nested query and CTE query "
        "produce identical results"
    )

else:

    print(
        "⚠ Results differ slightly."
    )

    print(
        "Check column ordering or floating-point precision."
    )


# ============================================================
# TASK 4
# COMPARISON DOCUMENT
# ============================================================

print("\n" + "=" * 60)
print("TASK 4: OPTIMIZATION COMPARISON")
print("=" * 60)


comparison = pd.DataFrame({

    "Metric": [

        "Columns Selected",
        "Filtering",
        "Intermediate Dataset",
        "Query Structure",
        "Readability",
        "Optimization Pattern"

    ],

    "Original": [

        "SELECT *",
        "After/with main operation",
        "Potentially larger",
        "Nested / less explicit",
        "Harder to follow",
        "Basic SQL"

    ],

    "Optimized": [

        "Explicit columns",
        "Filter early",
        "Smaller",
        "Named CTE steps",
        "Easier to understand",
        "Column pruning + early filtering + CTE"

    ]

})


print(
    comparison.to_string(
        index=False
    )
)


# ============================================================
# TASK 5
# FOLLOW-UP QUESTIONS
# ============================================================

print("\n" + "=" * 60)
print("TASK 5: FOLLOW-UP QUESTIONS")
print("=" * 60)


print(
    """
1. How does an index improve filtering?

An index creates a data structure that allows the database
to find matching rows without scanning the entire table.

For example, an index on transaction_date can make queries
filtering by transaction_date much faster.

Trade-off:
Indexes require additional storage and make INSERT,
UPDATE, and DELETE operations slightly more expensive because
the index must also be updated.


2. Does a CTE always get cached?

No. CTE behavior depends on the database engine and query.

Some databases may inline a CTE into the main query.
Others may materialize it.

SQLite may optimize the CTE depending on the query.
Therefore, we should not automatically assume that every CTE
is cached.


3. What can improve performance if 100 million rows remain?

Additional techniques include:

- Database indexes
- Table partitioning
- Materialized views
- Pre-aggregation
- Query result caching
- Selecting only required columns
- Filtering data as early as possible
- Proper JOIN conditions
- Database statistics and query-plan analysis

For very large datasets, partitioning and pre-aggregation
can significantly reduce the amount of data processed.
"""
)


# ============================================================
# SAVE COMPARISON REPORT
# ============================================================

os.makedirs(
    "output",
    exist_ok=True
)


report_path = (
    "output/query_optimization_report.txt"
)


with open(
    report_path,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "QUERY OPTIMIZATION REPORT\n"
    )

    file.write(
        "=========================\n\n"
    )

    file.write(
        "TASK 1 - SELECT * VS EXPLICIT COLUMNS\n"
    )

    file.write(
        f"Original columns: "
        f"{original_result.shape[1]}\n"
    )

    file.write(
        f"Optimized columns: "
        f"{optimized_result.shape[1]}\n"
    )

    file.write(
        f"Original memory: "
        f"{original_memory:,} bytes\n"
    )

    file.write(
        f"Optimized memory: "
        f"{optimized_memory:,} bytes\n"
    )

    file.write(
        f"Original execution time: "
        f"{original_time:.6f} seconds\n"
    )

    file.write(
        f"Optimized execution time: "
        f"{optimized_time:.6f} seconds\n\n"
    )

    file.write(
        "TASK 2 - EARLY FILTERING\n"
    )

    file.write(
        f"Full table rows: "
        f"{transactions_count:,}\n"
    )

    file.write(
        f"Filtered rows: "
        f"{filtered_transactions:,}\n\n"
    )

    file.write(
        "TASK 3 - CTE\n"
    )

    file.write(
        "CTE and original query comparison completed.\n\n"
    )

    file.write(
        "TASK 4 - OPTIMIZATION PATTERNS\n"
    )

    file.write(
        comparison.to_string(
            index=False
        )
    )

    file.write(
        "\n\nTASK 5 - FOLLOW-UP QUESTIONS\n"
    )

    file.write(
        "Indexing improves filtering by allowing faster "
        "lookup of matching rows.\n"
    )

    file.write(
        "CTE materialization depends on the database engine "
        "and query optimizer.\n"
    )

    file.write(
        "For very large datasets use indexes, partitioning, "
        "materialized views, caching and pre-aggregation.\n"
    )


print(
    f"\n✓ Report saved to: {report_path}"
)

print(
    "\n✓ QUERY OPTIMIZATION ANALYSIS COMPLETED"
)