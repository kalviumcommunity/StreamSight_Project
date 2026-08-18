import sqlite3
import pandas as pd
from datetime import datetime

# ============================================================
# DATABASE CONNECTION
# ============================================================

DB_PATH = "analytics.db"

conn = sqlite3.connect(DB_PATH)

print("✓ Database connection successful")


# ============================================================
# LOAD DATA
# ============================================================

logins_df = pd.read_sql(
    "SELECT * FROM logins",
    conn
)

orders_df = pd.read_sql(
    "SELECT * FROM orders",
    conn
)

# Convert date columns to datetime
logins_df["login_date"] = pd.to_datetime(
    logins_df["login_date"]
)

orders_df["order_date"] = pd.to_datetime(
    orders_df["order_date"]
)

print(f"✓ Logins loaded: {len(logins_df)}")
print(f"✓ Orders loaded: {len(orders_df)}")


# ============================================================
# TASK 1 - METRIC 1
# ACTIVE USERS - SQL
# ============================================================

sql_query_1 = """
SELECT COUNT(DISTINCT user_id) AS active_users
FROM logins
WHERE login_date >= date('now', '-30 days');
"""

sql_metric1 = pd.read_sql(
    sql_query_1,
    conn
).iloc[0, 0]


# ============================================================
# ACTIVE USERS - PYTHON
# ============================================================

cutoff_date = (
    pd.Timestamp.today().normalize()
    - pd.Timedelta(days=30)
)

py_metric1 = logins_df[
    logins_df["login_date"] >= cutoff_date
]["user_id"].nunique()


# ============================================================
# TASK 1 - METRIC 2
# AVERAGE ORDER VALUE - SQL
# ============================================================

sql_query_2 = """
SELECT AVG(order_amount) AS aov
FROM orders;
"""

sql_metric2 = pd.read_sql(
    sql_query_2,
    conn
).iloc[0, 0]


# ============================================================
# AVERAGE ORDER VALUE - PYTHON
# ============================================================

py_metric2 = orders_df[
    "order_amount"
].mean()


# ============================================================
# TASK 1 - METRIC 3
# CUSTOMER CHURN - SQL
# ============================================================

sql_query_3 = """
WITH previous_month AS (

    SELECT DISTINCT customer_id

    FROM orders

    WHERE order_date >=
          date('now', 'start of month', '-1 month')

      AND order_date <
          date('now', 'start of month')

      AND order_amount > 0
),

current_month AS (

    SELECT DISTINCT customer_id

    FROM orders

    WHERE order_date >=
          date('now', 'start of month')

      AND order_date <
          date('now', 'start of month', '+1 month')
)

SELECT COUNT(DISTINCT p.customer_id)
       AS churned_customers

FROM previous_month p

LEFT JOIN current_month c
    ON p.customer_id = c.customer_id

WHERE c.customer_id IS NULL;
"""

sql_metric3 = pd.read_sql(
    sql_query_3,
    conn
).iloc[0, 0]


# ============================================================
# CUSTOMER CHURN - PYTHON
# ============================================================

today = pd.Timestamp.today().normalize()

current_month_start = today.replace(day=1)

previous_month_start = (
    current_month_start
    - pd.DateOffset(months=1)
)

previous_month_end = current_month_start


previous_month_customers = orders_df[
    (orders_df["order_date"] >= previous_month_start)
    &
    (orders_df["order_date"] < previous_month_end)
    &
    (orders_df["order_amount"] > 0)
]["customer_id"].unique()


current_month_customers = orders_df[
    (orders_df["order_date"] >= current_month_start)
    &
    (
        orders_df["order_date"]
        <
        current_month_start + pd.DateOffset(months=1)
    )
]["customer_id"].unique()


py_metric3 = len(
    set(previous_month_customers)
    -
    set(current_month_customers)
)


# ============================================================
# TASK 1 - DISPLAY RESULTS
# ============================================================

print()
print("=" * 60)
print("TASK 1 - SQL VS PYTHON")
print("=" * 60)

print("\nActive Users:")
print(f"SQL    : {sql_metric1}")
print(f"Python : {py_metric1}")

print("\nAverage Order Value:")
print(f"SQL    : ${sql_metric2:.2f}")
print(f"Python : ${py_metric2:.2f}")

print("\nCustomer Churn:")
print(f"SQL    : {sql_metric3}")
print(f"Python : {py_metric3}")


# ============================================================
# TASK 2 - COMPARE RESULTS
# ============================================================

comparison = pd.DataFrame({

    "Metric": [
        "Active Users",
        "AOV",
        "Churn"
    ],

    "SQL": [
        sql_metric1,
        sql_metric2,
        sql_metric3
    ],

    "Python": [
        py_metric1,
        py_metric2,
        py_metric3
    ]
})


comparison["Difference"] = (
    comparison["SQL"]
    -
    comparison["Python"]
).abs()


comparison["Percent_Difference"] = 0.0


for index, row in comparison.iterrows():

    if row["SQL"] != 0:

        comparison.loc[
            index,
            "Percent_Difference"
        ] = (
            row["Difference"]
            /
            abs(row["SQL"])
            *
            100
        )


comparison["Status"] = comparison.apply(

    lambda row:
        "PASS"
        if row["Percent_Difference"] <= 0.1
        else "FAIL",

    axis=1
)


print()
print("=" * 60)
print("TASK 2 - METRICS COMPARISON")
print("=" * 60)

print(
    comparison.to_string(index=False)
)


# ============================================================
# TASK 3 - AUTOMATED VALIDATION FUNCTION
# ============================================================

def validate_metrics(
    connection,
    tolerance_pct=0.1
):
    """
    Validate SQL and Python metric calculations.

    Parameters
    ----------
    connection:
        SQLite database connection.

    tolerance_pct:
        Maximum allowed percentage difference.

    Returns
    -------
    DataFrame:
        Validation report.
    """

    # Load data
    logins = pd.read_sql(
        "SELECT * FROM logins",
        connection
    )

    orders = pd.read_sql(
        "SELECT * FROM orders",
        connection
    )

    # Convert dates
    logins["login_date"] = pd.to_datetime(
        logins["login_date"]
    )

    orders["order_date"] = pd.to_datetime(
        orders["order_date"]
    )

    # -------------------------
    # ACTIVE USERS
    # -------------------------

    sql_active = pd.read_sql(
        sql_query_1,
        connection
    ).iloc[0, 0]

    python_active = logins[
        logins["login_date"] >= cutoff_date
    ]["user_id"].nunique()


    # -------------------------
    # AOV
    # -------------------------

    sql_aov = pd.read_sql(
        sql_query_2,
        connection
    ).iloc[0, 0]

    python_aov = orders[
        "order_amount"
    ].mean()


    # -------------------------
    # CHURN
    # -------------------------

    sql_churn = pd.read_sql(
        sql_query_3,
        connection
    ).iloc[0, 0]


    previous_customers = orders[
        (orders["order_date"] >= previous_month_start)
        &
        (orders["order_date"] < previous_month_end)
        &
        (orders["order_amount"] > 0)
    ]["customer_id"].unique()


    current_customers = orders[
        (orders["order_date"] >= current_month_start)
        &
        (
            orders["order_date"]
            <
            current_month_start
            + pd.DateOffset(months=1)
        )
    ]["customer_id"].unique()


    python_churn = len(
        set(previous_customers)
        -
        set(current_customers)
    )


    # -------------------------
    # METRIC DEFINITIONS
    # -------------------------

    metrics = [

        (
            "active_users",
            sql_active,
            python_active,
            0
        ),

        (
            "aov",
            sql_aov,
            python_aov,
            tolerance_pct
        ),

        (
            "churn",
            sql_churn,
            python_churn,
            0
        )
    ]


    validation_report = []


    # -------------------------
    # VALIDATE EACH METRIC
    # -------------------------

    for (
        name,
        sql_value,
        python_value,
        tolerance
    ) in metrics:

        difference = abs(
            sql_value
            -
            python_value
        )


        if sql_value != 0:

            pct_difference = (
                difference
                /
                abs(sql_value)
                *
                100
            )

        else:

            pct_difference = 0


        status = (
            "PASS"
            if pct_difference <= tolerance
            else "FAIL"
        )


        validation_report.append({

            "Metric": name,

            "SQL": sql_value,

            "Python": python_value,

            "Difference": difference,

            "Pct_Difference":
                round(
                    pct_difference,
                    2
                ),

            "Tolerance":
                tolerance,

            "Status":
                status,

            "Timestamp":
                datetime.now()
        })


    return pd.DataFrame(
        validation_report
    )


# ============================================================
# RUN AUTOMATED VALIDATION
# ============================================================

report = validate_metrics(conn)


print()
print("=" * 60)
print("TASK 3 - AUTOMATED VALIDATION")
print("=" * 60)

print(
    report.to_string(index=False)
)


# ============================================================
# SAVE VALIDATION REPORT
# ============================================================

report.to_csv(
    "output/validation_report.csv",
    index=False
)

print()
print(
    "✓ Validation report saved:"
)

print(
    "  output/validation_report.csv"
)


# ============================================================
# TASK 4 - ROOT CAUSE DOCUMENTATION
# ============================================================

with open(
    "output/root_cause_analysis.txt",
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "SQL VS PYTHON METRIC VALIDATION\n"
    )

    file.write(
        "================================\n\n"
    )

    file.write(
        "Alignment steps:\n"
    )

    file.write(
        "1. SQL and Python use the same date ranges.\n"
    )

    file.write(
        "2. Both calculations count distinct users.\n"
    )

    file.write(
        "3. Both AOV calculations use order_amount.\n"
    )

    file.write(
        "4. Both churn calculations identify customers "
        "active in the previous month but not the current month.\n"
    )

    file.write(
        "5. Python date columns are explicitly converted "
        "to datetime.\n\n"
    )

    file.write(
        "If a discrepancy occurs, investigate:\n"
    )

    file.write(
        "- NULL handling\n"
    )

    file.write(
        "- Date boundaries\n"
    )

    file.write(
        "- Timezone differences\n"
    )

    file.write(
        "- Data type conversion\n"
    )

    file.write(
        "- JOIN behavior\n"
    )

    file.write(
        "- Filter conditions\n"
    )


print(
    "✓ Root cause analysis saved:"
)

print(
    "  output/root_cause_analysis.txt"
)


# ============================================================
# TASK 5 - FOLLOW-UP QUESTION
# ============================================================

with open(
    "output/follow_up_answer.txt",
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "WHY MANUAL INVESTIGATION IS NECESSARY\n"
    )

    file.write(
        "======================================\n\n"
    )

    file.write(
        "A tolerance threshold only detects that "
        "two calculations are different. It does not "
        "determine which calculation is correct.\n\n"
    )

    file.write(
        "Automatically fixing a discrepancy could "
        "change a correct metric into an incorrect one.\n\n"
    )

    file.write(
        "Manual investigation is necessary to identify "
        "the actual root cause, such as NULL handling, "
        "date boundaries, timezone differences, joins, "
        "or incorrect filters.\n\n"
    )

    file.write(
        "A metric can also slowly drift while remaining "
        "below the tolerance threshold. Therefore, "
        "automated validation should detect problems, "
        "while human investigation determines the "
        "correct fix."
    )


print(
    "✓ Follow-up answer saved:"
)

print(
    "  output/follow_up_answer.txt"
)


# ============================================================
# CLOSE DATABASE
# ============================================================

conn.close()

print()
print("=" * 60)
print("✓ METRIC VALIDATION COMPLETED")
print("=" * 60)