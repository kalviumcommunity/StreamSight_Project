import os
import pandas as pd
from sqlalchemy import create_engine, inspect


# ============================================================
# 1. DATABASE CONNECTION
# ============================================================

DATABASE_PATH = "analytics.db"
TABLE_NAME = "customers_cleaned"


def create_database_connection(database_path=DATABASE_PATH):
    """
    Create and test a SQLite database connection.

    Parameters:
        database_path (str): SQLite database file path.

    Returns:
        SQLAlchemy engine
    """

    engine = create_engine(
        f"sqlite:///{database_path}"
    )

    # Test connection
    with engine.connect():
        print("✓ Database connection successful")

    return engine


# ============================================================
# 2. LOAD DATA
# ============================================================

def load_cleaned_data_to_database(
    df,
    table_name=TABLE_NAME,
    database_path=DATABASE_PATH
):
    """
    Load a cleaned Pandas DataFrame into a SQLite database.

    Parameters:
        df (pd.DataFrame): Cleaned data to load.
        table_name (str): Name of database table.
        database_path (str): SQLite database file path.

    Returns:
        SQLAlchemy engine
    """

    engine = create_database_connection(
        database_path
    )

    # Load DataFrame into database
    df.to_sql(
        table_name,
        engine,
        if_exists="replace",
        index=False
    )

    print("✓ Data loaded into database")

    # Verify row count
    count = pd.read_sql(
        f"SELECT COUNT(*) AS row_count FROM {table_name}",
        engine
    )

    rows_loaded = count.iloc[0]["row_count"]

    print(f"Rows loaded: {rows_loaded}")

    return engine


# ============================================================
# 3. VALIDATE TABLE SCHEMA
# ============================================================

def validate_table_schema(
    engine,
    table_name=TABLE_NAME
):
    """
    Inspect and display the database table schema.
    """

    inspector = inspect(engine)

    columns = inspector.get_columns(
        table_name
    )

    print("\n# TABLE SCHEMA")

    for column in columns:

        nullable = (
            "NULL"
            if column["nullable"]
            else "NOT NULL"
        )

        print(
            f"{column['name']:20} "
            f"{str(column['type']):15} "
            f"{nullable}"
        )

    return columns


# ============================================================
# 4. VALIDATE EXPECTED COLUMNS
# ============================================================

def validate_expected_columns(
    engine,
    table_name=TABLE_NAME
):
    """
    Check whether expected columns exist.
    """

    inspector = inspect(engine)

    columns = inspector.get_columns(
        table_name
    )

    actual_columns = {
        column["name"]
        for column in columns
    }

    expected_columns = {
        "user_id",
        "video_id",
        "watch_duration",
        "pause_count",
        "completion_rate",
        "transaction_date",
        "amount",
        "customer_type",
        "product_category"
    }

    print("\n# COLUMN VALIDATION")

    for column in sorted(expected_columns):

        if column in actual_columns:
            print(f"✓ {column}")
        else:
            print(f"✗ {column} MISSING")


# ============================================================
# 5. QUERY DATA
# ============================================================

def query_database(engine):
    """
    Run example queries against the database.
    """

    # Simple SELECT query
    query = f"""
    SELECT *
    FROM {TABLE_NAME}
    LIMIT 5
    """

    results = pd.read_sql(
        query,
        engine
    )

    print("\n# QUERY RESULTS")
    print(results)

    # Aggregation query
    query_aggregation = f"""
    SELECT
        customer_type,
        COUNT(*) AS customer_count,
        SUM(amount) AS total_revenue,
        AVG(amount) AS average_revenue
    FROM {TABLE_NAME}
    GROUP BY customer_type
    ORDER BY total_revenue DESC
    """

    summary = pd.read_sql(
        query_aggregation,
        engine
    )

    print("\n# SUMMARY BY CUSTOMER TYPE")
    print(summary)

    return results, summary


# ============================================================
# 6. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("==============================")
    print("DATABASE SETUP")
    print("==============================")

    # --------------------------------------------------------
    # Load CSV data
    # --------------------------------------------------------

    data_path = os.path.join(
        "data",
        "engagement_data.csv"
    )

    print("\nLoading data...")

    df = pd.read_csv(
        data_path
    )

    print("Data loaded successfully")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    # --------------------------------------------------------
    # Create database and load data
    # --------------------------------------------------------

    engine = load_cleaned_data_to_database(
        df,
        table_name=TABLE_NAME,
        database_path=DATABASE_PATH
    )

    # --------------------------------------------------------
    # Validate schema
    # --------------------------------------------------------

    validate_table_schema(
        engine,
        TABLE_NAME
    )

    # --------------------------------------------------------
    # Validate columns
    # --------------------------------------------------------

    validate_expected_columns(
        engine,
        TABLE_NAME
    )

    # --------------------------------------------------------
    # Query database
    # --------------------------------------------------------

    query_database(
        engine
    )

    print("\n==============================")
    print("DATABASE SETUP COMPLETED")
    print("==============================")