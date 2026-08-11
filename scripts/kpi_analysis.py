import pandas as pd
import json
import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from kpis.kpi_functions import *

df = pd.read_csv(
    "data/engagement_data.csv"
)


df["transaction_date"] = pd.to_datetime(
    df["transaction_date"]
)


# Calculate KPIs

mau = calculate_mau(df)

rpc = calculate_revenue_per_customer(df)

total_revenue = calculate_total_revenue(df)

avg_transaction = calculate_average_transaction(df)


current_kpis = {

    "mau":mau,

    "revenue_per_customer":rpc,

    "churn_rate":0.05,

    "payment_success_rate":0.98,

    "customer_acquisition_cost":35

}


print("\nCURRENT KPIs")
print("================")

for k,v in current_kpis.items():

    print(
        k,
        ":",
        v
    )


# Load targets

with open(
    "kpis/kpi_validation_targets.json"
) as file:

    targets=json.load(file)



print("\nVALIDATION REPORT")
print("=================")


for kpi,value in current_kpis.items():

    minimum = targets[kpi]["min"]

    maximum = targets[kpi]["max"]


    if minimum <= value <= maximum:

        status="PASS"

    else:

        status="ALERT"


    print(
        kpi,
        value,
        status
    )



# KPI Decomposition

print("\nKPI DECOMPOSITION")
print("=================")


print(
    "Total Revenue:",
    total_revenue
)


print("\nRevenue By User")

print(
    df.groupby("user_id")["amount"].sum()
)

print("\nRevenue By Customer Type")
print("========================")

print(
    df.groupby("customer_type")["amount"].sum()
)


print("\nRevenue By Product Category")
print("==========================")

print(
    df.groupby("product_category")["amount"].sum()
)