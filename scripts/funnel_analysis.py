import pandas as pd
import matplotlib.pyplot as plt
import os


# Create output folder
os.makedirs("output", exist_ok=True)


# ==============================
# Load Data
# ==============================

df = pd.read_csv(
    "data/funnel_data.csv"
)


# ==============================
# Task 1
# Define Funnel Stages
# ==============================

stages = {

    "Sign Up":
        len(df[df["signup_completed"] == 1]),

    "Email Entered":
        len(df[df["email_entered"] == 1]),

    "Password Created":
        len(df[df["password_created"] == 1]),

    "Email Verified":
        len(df[df["email_verified"] == 1]),

    "Payment Added":
        len(df[df["payment_added"] == 1]),

    "First Purchase":
        len(df[df["first_purchase"] == 1])
}


print(stages)



# ==============================
# Task 2
# Drop Off Calculation
# ==============================


stage_names = list(stages.keys())
stage_values = list(stages.values())


drop_data = []


for i in range(len(stage_values)-1):

    before = stage_values[i]
    after = stage_values[i+1]

    lost = before - after

    completion = (
        after / before
    ) * 100


    drop_rate = (
        lost / before
    ) * 100


    drop_data.append({

        "from_stage":
        stage_names[i],

        "to_stage":
        stage_names[i+1],

        "users_lost":
        lost,

        "completion_rate":
        f"{completion:.1f}%",

        "drop_rate":
        f"{drop_rate:.1f}%"

    })


funnel_df = pd.DataFrame(drop_data)


print("\nDrop Analysis")
print(funnel_df)



# Biggest bottleneck

biggest_drop = funnel_df.loc[
    funnel_df["users_lost"].idxmax()
]


print("\nBiggest Drop:")
print(biggest_drop)



# ==============================
# Task 3
# Funnel Visualization
# ==============================


plt.figure(
    figsize=(12,6)
)


plt.bar(
    stages.keys(),
    stages.values()
)


for stage,count in stages.items():

    plt.text(
        stage,
        count,
        str(count),
        ha="center"
    )


plt.xlabel("Funnel Stage")

plt.ylabel("Users")

plt.title(
    "Signup Funnel Analysis"
)


plt.xticks(
    rotation=45
)


plt.tight_layout()


plt.savefig(
    "output/funnel_chart.png"
)


plt.close()



# ==============================
# Task 4
# Business Impact
# ==============================


revenue_per_customer = 100


impact = []


for index,row in funnel_df.iterrows():

    lost = row["users_lost"]


    impact.append({

        "drop_point":
        row["from_stage"]
        +
        " -> "
        +
        row["to_stage"],


        "users_lost":
        lost,


        "revenue_impact":
        lost * revenue_per_customer

    })


impact_df = pd.DataFrame(
    impact
)


print("\nBusiness Impact")

print(
    impact_df
)



# ==============================
# Task 5
# Generate Report
# ==============================


highest = biggest_drop


recommendation = f"""

FUNNEL OPTIMIZATION REPORT
==========================


Critical Bottleneck:

Stage:
{highest['from_stage']} -> {highest['to_stage']}


Users Lost:
{highest['users_lost']}


Drop Rate:
{highest['drop_rate']}


Revenue Impact:
${highest['users_lost'] * 100}


Possible Causes:

- Poor user experience
- Too many fields
- Lack of trust
- Step introduced too early


Recommended Actions:

1. Simplify this step
2. Run A/B testing
3. Measure conversion improvement
4. Deploy successful changes


Expected Improvement:

10% recovery could generate:

Additional Users:
{int(highest['users_lost']*0.1)}

Additional Revenue:
${int(highest['users_lost']*0.1*100)}

"""


with open(
    "output/funnel_analysis.txt",
    "w"
) as file:

    file.write(
        funnel_df.to_string()
    )

    file.write(
        "\n\n"
    )

    file.write(
        recommendation
    )


print(
    "\nFunnel analysis completed"
)