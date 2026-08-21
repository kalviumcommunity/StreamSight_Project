import os
import time
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine


# ============================================================
# DATABASE CONNECTION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "analytics.db")

engine = create_engine(f"sqlite:///{DB_PATH}")

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading data from database...")

df = pd.read_sql(
    "SELECT * FROM customers_cleaned",
    engine
)

df["transaction_date"] = pd.to_datetime(
    df["transaction_date"]
)

print(f"Loaded {len(df)} records.")


# ============================================================
# TASK 1 - CHART 1
# DAILY REVENUE TREND
# ============================================================

print("\nCreating Chart 1 - Revenue Trend...")

daily_revenue = (
    df.groupby("transaction_date")
    .agg(
        revenue=("amount", "sum"),
        order_count=("user_id", "count")
    )
    .reset_index()
    .sort_values("transaction_date")
)

fig1 = go.Figure(
    data=go.Scatter(
        x=daily_revenue["transaction_date"],
        y=daily_revenue["revenue"],
        mode="lines+markers",

        hovertemplate=(
            "<b>%{x|%Y-%m-%d}</b><br>"
            "Revenue: $%{y:,.2f}<br>"
            "<extra></extra>"
        ),

        line=dict(width=2),
        marker=dict(size=8)
    )
)

fig1.update_layout(
    title="Daily Revenue Trend",
    xaxis_title="Date",
    yaxis_title="Revenue ($)",
    hovermode="x unified",
    height=500
)

chart1_path = os.path.join(
    OUTPUT_DIR,
    "chart1_revenue_trend.html"
)

fig1.write_html(chart1_path)

print(f"✓ Chart 1 saved: {chart1_path}")


# ============================================================
# TASK 1 - CHART 2
# PRODUCT PERFORMANCE
# ============================================================

print("\nCreating Chart 2 - Product Performance...")

product_data = (
    df.groupby("product_category")
    .agg(
        revenue=("amount", "sum"),
        order_count=("user_id", "count"),
        avg_order_value=("amount", "mean")
    )
    .reset_index()
)

fig2 = go.Figure(
    data=go.Bar(
        x=product_data["product_category"],
        y=product_data["revenue"],

        hovertemplate=(
            "<b>%{x}</b><br>"
            "Revenue: $%{y:,.2f}<br>"
            "Order Count: %{customdata[0]:,}<br>"
            "Average Order Value: $%{customdata[1]:,.2f}"
            "<extra></extra>"
        ),

        customdata=product_data[
            ["order_count", "avg_order_value"]
        ].values
    )
)

fig2.update_layout(
    title="Revenue by Product Category",
    xaxis_title="Product Category",
    yaxis_title="Revenue ($)",
    height=500
)

chart2_path = os.path.join(
    OUTPUT_DIR,
    "chart2_product_performance.html"
)

fig2.write_html(chart2_path)

print(f"✓ Chart 2 saved: {chart2_path}")


# ============================================================
# TASK 2
# DROPDOWN METRIC SELECTOR
# ============================================================

print("\nCreating Chart 3 - Metric Selector...")

products = product_data["product_category"].tolist()

revenue_data = product_data["revenue"].tolist()

# We don't have actual profit in the database.
# Use revenue as the available business metric.
# For the third metric, use order count.
order_count = product_data["order_count"].tolist()

# Create an estimated profit metric for demonstration.
# This is NOT actual profit because the database has no cost column.
profit_data = [
    value * 0.30
    for value in revenue_data
]


fig3 = go.Figure()

fig3.add_trace(
    go.Bar(
        x=products,
        y=revenue_data,
        name="Revenue",
        visible=True
    )
)

fig3.add_trace(
    go.Bar(
        x=products,
        y=profit_data,
        name="Estimated Profit",
        visible=False
    )
)

fig3.add_trace(
    go.Bar(
        x=products,
        y=order_count,
        name="Order Count",
        visible=False
    )
)


fig3.update_layout(
    updatemenus=[
        dict(
            active=0,
            x=0.0,
            y=1.15,
            buttons=[
                dict(
                    label="Revenue",
                    method="update",
                    args=[
                        {"visible": [True, False, False]},
                        {"title": "Revenue by Product Category"}
                    ]
                ),

                dict(
                    label="Estimated Profit",
                    method="update",
                    args=[
                        {"visible": [False, True, False]},
                        {"title": "Estimated Profit by Product Category"}
                    ]
                ),

                dict(
                    label="Order Count",
                    method="update",
                    args=[
                        {"visible": [False, False, True]},
                        {"title": "Order Count by Product Category"}
                    ]
                )
            ]
        )
    ],

    title="Product Performance",
    height=500
)

chart3_path = os.path.join(
    OUTPUT_DIR,
    "chart3_metric_selector.html"
)

fig3.write_html(chart3_path)

print(f"✓ Chart 3 saved: {chart3_path}")


# ============================================================
# TASK 3
# ZOOM / PAN / RESET / SELECT
# ============================================================

print("\nCreating Chart 4 - Interactive Chart...")

fig4 = go.Figure(
    data=go.Scatter(
        x=df["transaction_date"],
        y=df["amount"],
        mode="markers",

        marker=dict(size=10),

        hovertemplate=(
            "<b>Date:</b> %{x|%Y-%m-%d}<br>"
            "<b>Amount:</b> $%{y:,.2f}"
            "<extra></extra>"
        )
    )
)

fig4.update_layout(
    title="Interactive Transaction Amounts",
    xaxis_title="Transaction Date",
    yaxis_title="Amount ($)",

    dragmode="zoom",

    hovermode="closest",

    height=600
)

chart4_path = os.path.join(
    OUTPUT_DIR,
    "chart4_interactive.html"
)

fig4.write_html(chart4_path)

print(f"✓ Chart 4 saved: {chart4_path}")


# ============================================================
# TASK 5
# DATE RANGE SLIDER EXAMPLE
# ============================================================

fig5 = go.Figure(
    data=go.Scatter(
        x=daily_revenue["transaction_date"],
        y=daily_revenue["revenue"],
        mode="lines+markers"
    )
)

fig5.update_layout(
    title="Revenue Trend with Date Range Slider",

    xaxis=dict(
        title="Date",

        rangeslider=dict(
            visible=True
        ),

        rangeselector=dict(
            buttons=[
                dict(
                    count=7,
                    label="7 Days",
                    step="day",
                    stepmode="backward"
                ),

                dict(
                    count=1,
                    label="1 Month",
                    step="month",
                    stepmode="backward"
                ),

                dict(
                    count=3,
                    label="3 Months",
                    step="month",
                    stepmode="backward"
                ),

                dict(
                    step="all",
                    label="All"
                )
            ]
        )
    ),

    yaxis_title="Revenue ($)",

    height=500
)

chart5_path = os.path.join(
    OUTPUT_DIR,
    "chart5_date_range.html"
)

fig5.write_html(chart5_path)

print(f"✓ Chart 5 saved: {chart5_path}")


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n" + "=" * 60)
print("PLOTLY ANALYSIS COMPLETED")
print("=" * 60)

print("\nGenerated files:")

print("✓ chart1_revenue_trend.html")
print("✓ chart2_product_performance.html")
print("✓ chart3_metric_selector.html")
print("✓ chart4_interactive.html")
print("✓ chart5_date_range.html")

print("\nOpen the HTML files in your browser to test them.")