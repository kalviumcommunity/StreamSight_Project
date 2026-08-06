import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os


# -----------------------------------
# Load validated dataset
# -----------------------------------

def load_data(filepath):

    try:
        df = pd.read_csv(filepath)

        print("Data loaded successfully")
        print(f"Total Records: {len(df)}")
        print()

        return df

    except FileNotFoundError:
        print("File not found")
        raise



# -----------------------------------
# Calculate correlations
# -----------------------------------

def calculate_correlation(df):

    # Select only numerical columns

    numeric_columns = [
        "watch_duration",
        "pause_count",
        "completion_rate",
        "amount"
    ]


    numeric_df = df[numeric_columns]


    print("Numerical Data Used:")
    print(numeric_df.head())
    print()


    # Pearson

    pearson_corr = numeric_df.corr(
        method="pearson"
    )


    print("==============================")
    print("PEARSON CORRELATION")
    print("==============================")

    print(pearson_corr)


    print()


    # Spearman

    spearman_corr = numeric_df.corr(
        method="spearman"
    )


    print("==============================")
    print("SPEARMAN CORRELATION")
    print("==============================")

    print(spearman_corr)


    return pearson_corr



# -----------------------------------
# Create Heatmap
# -----------------------------------

def create_heatmap(correlation):

    plt.figure(
        figsize=(10,8)
    )


    sns.heatmap(
        correlation,
        annot=True,
        cmap="coolwarm",
        center=0
    )


    plt.title(
        "StreamSight Viewer Engagement Correlation"
    )


    plt.tight_layout()


    plt.savefig(
        "output/correlation_heatmap.png"
    )


    plt.close()


    print(
        "\nHeatmap saved:"
        " output/correlation_heatmap.png"
    )


# -----------------------------------
# Find Strong Relationships
# -----------------------------------

def find_strong_relationships(correlation):


    correlation_pairs = correlation.unstack()


    strong_pairs = correlation_pairs[
        (abs(correlation_pairs) > 0.7)
        &
        (correlation_pairs != 1)
    ]


    print()
    print("==============================")
    print("STRONG RELATIONSHIPS")
    print("==============================")


    if len(strong_pairs) == 0:

        print(
            "No strong correlations found"
        )

    else:

        for pair,value in strong_pairs.items():

            print(
                f"{pair[0]} <-> {pair[1]} : {value:.2f}"
            )



# -----------------------------------
# Generate Business Explanation
# -----------------------------------

def generate_report():

    report = """

StreamSight Correlation Analysis Report

Purpose:
Identify relationships between viewer engagement metrics.

Findings:

1. Watch Duration:
Higher watch duration generally indicates stronger viewer engagement.

2. Completion Rate:
Completion rate is used as a retention indicator.

3. Pause Frequency:
High pause counts may indicate lower engagement.

Important:
Correlation does not prove causation.

A strong correlation means two metrics move together.
It does not mean one metric directly causes another.

Business teams should investigate further before making decisions.

"""


    with open(
        "output/correlation_report.txt",
        "w"
    ) as file:

        file.write(report)


    print(
        "Report generated:"
        " output/correlation_report.txt"
    )



# -----------------------------------
# Main Execution
# -----------------------------------

if __name__ == "__main__":


    file_path = (
        "output/"
        "validated_engagement_data.csv"
    )


    df = load_data(file_path)


    correlation = calculate_correlation(df)


    create_heatmap(correlation)


    find_strong_relationships(
        correlation
    )


    generate_report()