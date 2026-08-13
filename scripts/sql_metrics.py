import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "sqlite:///analytics.db"
)


def load_query(query_name):

    with open(
        f"queries/{query_name}.sql",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# -----------------------
# Monthly Active Users
# -----------------------

mau_query = load_query(
    "monthly_active_users"
)

mau = pd.read_sql(
    mau_query,
    engine
)

print("\nMONTHLY ACTIVE USERS")
print(mau)


# -----------------------
# Revenue
# -----------------------

revenue_query = load_query(
    "revenue_by_segment"
)

revenue = pd.read_sql(
    revenue_query,
    engine
)

print("\nREVENUE BY SEGMENT")
print(revenue)


# -----------------------
# Funnel
# -----------------------

funnel_query = load_query(
    "conversion_funnel"
)

funnel = pd.read_sql(
    funnel_query,
    engine
)

print("\nFUNNEL")
print(funnel)


# -----------------------
# Validation
# -----------------------

def validate_metrics(
    mau_df,
    revenue_df,
    funnel_df
):

    assert mau_df.isnull().sum().sum() == 0

    assert revenue_df.isnull().sum().sum() == 0

    assert (
        revenue_df["monthly_revenue"] > 0
    ).all()

    assert (
        funnel_df["conversion_pct"] >= 0
    ).all()

    assert (
        funnel_df["conversion_pct"] <= 100
    ).all()

    print("\n✓ All metrics validated")


validate_metrics(
    mau,
    revenue,
    funnel
)