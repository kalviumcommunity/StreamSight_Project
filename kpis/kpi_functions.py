import pandas as pd


def calculate_mau(df, days=30):

    cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)

    users = df[
        df["transaction_date"] >= cutoff
    ]["user_id"].nunique()

    return users



def calculate_revenue_per_customer(df):

    revenue = df["amount"].sum()

    customers = df["user_id"].nunique()

    return revenue / customers



def calculate_average_transaction(df):

    return df["amount"].mean()



def calculate_total_revenue(df):

    return df["amount"].sum()



def calculate_payment_success_rate(successful, total):

    if total == 0:
        return 0

    return successful / total



def calculate_churn_rate(df):

    return 0.05