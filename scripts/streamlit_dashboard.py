import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="StreamSight Dashboard",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

engine = create_engine("sqlite:///analytics.db")


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    query = """
    SELECT
        user_id,
        video_id,
        watch_duration,
        pause_count,
        completion_rate,
        transaction_date,
        amount,
        customer_type,
        product_category
    FROM customers_cleaned
    """

    df = pd.read_sql(query, engine)

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"]
    )

    return df


df = load_data()


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("📊 StreamSight Interactive Sales Dashboard")

st.write(
    "Interactive dashboard using Plotly and Streamlit."
)


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filters")

# Customer type filter

customer_types = ["All"] + sorted(
    df["customer_type"].dropna().unique().tolist()
)

selected_customer_type = st.sidebar.selectbox(
    "Customer Type",
    customer_types
)


# Product category filter

product_categories = ["All"] + sorted(
    df["product_category"].dropna().unique().tolist()
)

selected_product = st.sidebar.selectbox(
    "Product Category",
    product_categories
)


# Minimum amount filter

min_amount = st.sidebar.number_input(
    "Minimum Amount",
    min_value=0.0,
    value=0.0,
    step=100.0
)


# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_df = df.copy()

if selected_customer_type != "All":
    filtered_df = filtered_df[
        filtered_df["customer_type"]
        == selected_customer_type
    ]

if selected_product != "All":
    filtered_df = filtered_df[
        filtered_df["product_category"]
        == selected_product
    ]

filtered_df = filtered_df[
    filtered_df["amount"] >= min_amount
]


# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

total_revenue = filtered_df["amount"].sum()

total_orders = len(filtered_df)

unique_users = filtered_df["user_id"].nunique()

average_order_value = (
    filtered_df["amount"].mean()
    if len(filtered_df) > 0
    else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Revenue",
    f"${total_revenue:,.2f}"
)

col2.metric(
    "Total Orders",
    f"{total_orders:,}"
)

col3.metric(
    "Unique Users",
    f"{unique_users:,}"
)

col4.metric(
    "Average Order Value",
    f"${average_order_value:,.2f}"
)


st.divider()


# --------------------------------------------------
# REVENUE TREND
# --------------------------------------------------

st.subheader("Daily Revenue Trend")

if len(filtered_df) > 0:

    revenue_df = (
        filtered_df
        .groupby("transaction_date")
        .agg(
            revenue=("amount", "sum"),
            order_count=("amount", "count")
        )
        .reset_index()
        .sort_values("transaction_date")
    )

    fig_revenue = go.Figure()

    fig_revenue.add_trace(
        go.Scatter(
            x=revenue_df["transaction_date"],
            y=revenue_df["revenue"],
            mode="lines+markers",
            name="Revenue",

            hovertemplate=
            "<b>%{x|%Y-%m-%d}</b><br>"
            "Revenue: $%{y:,.2f}<br>"
            "<extra></extra>"
        )
    )

    fig_revenue.update_layout(
        title="Daily Revenue Trend",
        xaxis_title="Date",
        yaxis_title="Revenue ($)",
        hovermode="x unified",
        height=500
    )

    st.plotly_chart(
        fig_revenue,
        use_container_width=True
    )

else:

    st.warning("No data available for the selected filters.")


# --------------------------------------------------
# PRODUCT PERFORMANCE
# --------------------------------------------------

st.subheader("Product Performance")

if len(filtered_df) > 0:

    product_df = (
        filtered_df
        .groupby("product_category")
        .agg(
            revenue=("amount", "sum"),
            order_count=("amount", "count"),
            avg_order_value=("amount", "mean")
        )
        .reset_index()
    )

    fig_product = go.Figure()

    fig_product.add_trace(
        go.Bar(
            x=product_df["product_category"],
            y=product_df["revenue"],
            name="Revenue",

            customdata=product_df[
                ["order_count", "avg_order_value"]
            ],

            hovertemplate=
            "<b>%{x}</b><br>"
            "Revenue: $%{y:,.2f}<br>"
            "Orders: %{customdata[0]:,}<br>"
            "Average Order Value: "
            "$%{customdata[1]:,.2f}"
            "<extra></extra>"
        )
    )

    fig_product.update_layout(
        title="Revenue by Product Category",
        xaxis_title="Product Category",
        yaxis_title="Revenue ($)",
        height=500
    )

    st.plotly_chart(
        fig_product,
        use_container_width=True
    )


# --------------------------------------------------
# CUSTOMER SEGMENT PERFORMANCE
# --------------------------------------------------

st.subheader("Revenue by Customer Type")

if len(filtered_df) > 0:

    segment_df = (
        filtered_df
        .groupby("customer_type")
        .agg(
            revenue=("amount", "sum"),
            orders=("amount", "count"),
            customers=("user_id", "nunique")
        )
        .reset_index()
    )

    fig_segment = go.Figure()

    fig_segment.add_trace(
        go.Bar(
            x=segment_df["customer_type"],
            y=segment_df["revenue"],
            name="Revenue",

            customdata=segment_df[
                ["orders", "customers"]
            ],

            hovertemplate=
            "<b>%{x}</b><br>"
            "Revenue: $%{y:,.2f}<br>"
            "Orders: %{customdata[0]:,}<br>"
            "Customers: %{customdata[1]:,}"
            "<extra></extra>"
        )
    )

    fig_segment.update_layout(
        title="Revenue by Customer Type",
        xaxis_title="Customer Type",
        yaxis_title="Revenue ($)",
        height=500
    )

    st.plotly_chart(
        fig_segment,
        use_container_width=True
    )


# --------------------------------------------------
# DATA TABLE
# --------------------------------------------------

st.subheader("Filtered Data")

st.write(
    f"Showing {len(filtered_df):,} records"
)

st.dataframe(
    filtered_df,
    use_container_width=True
)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "StreamSight | Interactive Plotly + Streamlit Dashboard"
)