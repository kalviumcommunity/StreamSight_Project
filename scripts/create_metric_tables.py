import sqlite3
import pandas as pd

DB_PATH = "analytics.db"

conn = sqlite3.connect(DB_PATH)

# ============================================================
# LOGINS TABLE
# ============================================================

logins_data = {
    "user_id": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
    "login_date": [
        "2026-07-28",
        "2026-07-29",
        "2026-07-30",
        "2026-07-31",
        "2026-07-31",
        "2026-07-31",
        "2026-07-30",
        "2026-07-29",
        "2026-07-28",
        "2026-07-31"
    ]
}

logins_df = pd.DataFrame(logins_data)

logins_df.to_sql(
    "logins",
    conn,
    if_exists="replace",
    index=False
)

# ============================================================
# ORDERS TABLE
# ============================================================

orders_data = {
    "customer_id": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
    "order_date": [
        "2026-07-28",
        "2026-07-29",
        "2026-07-30",
        "2026-07-31",
        "2026-07-31",
        "2026-07-31",
        "2026-07-30",
        "2026-07-29",
        "2026-07-28",
        "2026-07-31"
    ],
    "order_amount": [
        1200.50,
        900.00,
        1500.75,
        500.00,
        700.00,
        800.00,
        900.00,
        900.00,
        650.00,
        1100.00
    ]
}

orders_df = pd.DataFrame(orders_data)

orders_df.to_sql(
    "orders",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print("✓ logins table created")
print("✓ orders table created")