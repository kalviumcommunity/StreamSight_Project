import os
import pandas as pd

# Create output directory if it does not exist
os.makedirs("output", exist_ok=True)


# ============================================================
# 1. BUILD SEGMENT SUMMARY
# ============================================================

def build_segment_summary(
    df: pd.DataFrame,
    group_cols=None,
    value_col="amount",
    agg_col="user_id"
):
    """
    Create summary metrics for each customer segment.
    """

    if group_cols is None:
        group_cols = ["customer_type"]

    if not isinstance(group_cols, list):
        group_cols = [group_cols]

    # Check grouping columns
    required = set(group_cols)

    if not required.issubset(df.columns):
        missing = sorted(
            required - set(df.columns)
        )

        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # Check value column
    if value_col not in df.columns:
        raise ValueError(
            f"Missing value column: {value_col}"
        )

    # Check aggregation column
    if agg_col not in df.columns:
        raise ValueError(
            f"Missing aggregation column: {agg_col}"
        )

    # Calculate metrics
    summary = df.groupby(group_cols).agg(

        total_value=(
            value_col,
            "sum"
        ),

        record_count=(
            agg_col,
            "count"
        ),

        avg_value=(
            value_col,
            "mean"
        )

    ).reset_index()

    # Sort by total value
    summary = summary.sort_values(
        "total_value",
        ascending=False
    )

    # Rank segments
    summary["value_rank"] = (
        summary["total_value"]
        .rank(
            ascending=False,
            method="dense"
        )
        .astype(int)
    )

    return summary


# ============================================================
# 2. BUILD PIVOT TABLE
# ============================================================

def build_pivot_table(
    df,
    index_col="customer_type",
    columns_col="product_category",
    value_col="amount"
):
    """
    Compare value across customer segments and
    product categories.
    """

    required_columns = [
        index_col,
        columns_col,
        value_col
    ]

    for column in required_columns:

        if column not in df.columns:
            raise ValueError(
                f"Missing required column: {column}"
            )

    pivot = pd.pivot_table(
        df,
        values=value_col,
        index=index_col,
        columns=columns_col,
        aggfunc="sum",
        fill_value=0
    )

    return pivot


# ============================================================
# 3. CREATE BUSINESS INSIGHTS
# ============================================================

def create_business_insights(
    df,
    summary,
    pivot
):
    """
    Generate concise business insights based on
    segment metrics.
    """

    lines = []

    # --------------------------------------------------------
    # Highest and lowest value segments
    # --------------------------------------------------------

    top_segment = summary.iloc[0]
    bottom_segment = summary.iloc[-1]

    top_name = top_segment["customer_type"]
    bottom_name = bottom_segment["customer_type"]

    top_total = top_segment["total_value"]
    bottom_total = bottom_segment["total_value"]

    top_average = top_segment["avg_value"]
    bottom_average = bottom_segment["avg_value"]

    lines.append("Business Insights")
    lines.append("-----------------")

    lines.append(
        f"1. {top_name} is the highest-value segment "
        f"with total value of ${top_total:,.2f} "
        f"and average value of ${top_average:,.2f}."
    )

    lines.append(
        f"2. {bottom_name} is the lowest-value segment "
        f"with total value of ${bottom_total:,.2f} "
        f"and average value of ${bottom_average:,.2f}."
    )

    # --------------------------------------------------------
    # Product comparison
    # --------------------------------------------------------

    if "Movies" in pivot.columns and "Series" in pivot.columns:

        for segment in pivot.index:

            movies_value = pivot.loc[
                segment,
                "Movies"
            ]

            series_value = pivot.loc[
                segment,
                "Series"
            ]

            if movies_value > series_value:

                lines.append(
                    f"3. {segment} generates more value "
                    f"from Movies (${movies_value:,.2f}) "
                    f"than Series (${series_value:,.2f})."
                )

            elif series_value > movies_value:

                lines.append(
                    f"3. {segment} generates more value "
                    f"from Series (${series_value:,.2f}) "
                    f"than Movies (${movies_value:,.2f})."
                )

            else:

                lines.append(
                    f"3. {segment} generates equal value "
                    f"from Movies and Series."
                )

    # --------------------------------------------------------
    # Business implication
    # --------------------------------------------------------

    lines.append(
        "4. Content and retention strategies should be "
        "customized by customer segment instead of using "
        "a single strategy for all customers."
    )

    return lines


# ============================================================
# 4. WRITE SEGMENT REPORT
# ============================================================

def write_segment_insights(
    df,
    output_path="output/segment_insights.txt"
):
    """
    Generate the complete segment analysis report.
    """

    summary = build_segment_summary(df)

    pivot = build_pivot_table(df)

    lines = []

    # ========================================================
    # HEADER
    # ========================================================

    lines.append(
        "Segment Insights Report"
    )

    lines.append(
        "======================"
    )

    lines.append("")

    # ========================================================
    # DATASET INFORMATION
    # ========================================================

    lines.append(
        "Dataset Information"
    )

    lines.append(
        "-------------------"
    )

    lines.append(
        f"Total Records: {len(df)}"
    )

    lines.append(
        f"Total Segments: {df['customer_type'].nunique()}"
    )

    lines.append("")

    # ========================================================
    # SEGMENT SUMMARY
    # ========================================================

    lines.append(
        "Segment Summary"
    )

    lines.append(
        "---------------"
    )

    lines.append(
        summary.to_string(index=False)
    )

    lines.append("")

    # ========================================================
    # PIVOT TABLE
    # ========================================================

    lines.append(
        "Segment vs Product Comparison"
    )

    lines.append(
        "-----------------------------"
    )

    lines.append(
        pivot.to_string()
    )

    lines.append("")

    # ========================================================
    # BUSINESS INSIGHTS
    # ========================================================

    insight_lines = create_business_insights(
        df,
        summary,
        pivot
    )

    lines.extend(insight_lines)

    lines.append("")

    # ========================================================
    # SAMPLE SIZE CAUTION
    # ========================================================

    lines.append(
        "Caution: Small Segment Sizes"
    )

    lines.append(
        "----------------------------"
    )

    lines.append(
        f"The analysis contains only {len(df)} total records."
    )

    lines.append(
        "Segment-level results may be unstable when "
        "sample sizes are small."
    )

    lines.append(
        "The observed differences should therefore be "
        "treated as preliminary findings."
    )

    lines.append(
        "A larger dataset should be used before making "
        "major business decisions."
    )

    lines.append("")

    # ========================================================
    # SAVE REPORT
    # ========================================================

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as handle:

        handle.write(
            "\n".join(lines)
        )

    return output_path


# ============================================================
# 5. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print(
        "Loading engagement data..."
    )

    # Load dataset
    df = pd.read_csv(
        "data/engagement_data.csv"
    )

    print(
        f"Loaded {len(df)} records."
    )

    # ========================================================
    # SEGMENT SUMMARY
    # ========================================================

    print(
        "\n=============================="
    )

    print(
        "SEGMENT SUMMARY"
    )

    print(
        "=============================="
    )

    summary = build_segment_summary(
        df
    )

    print(
        summary.to_string(
            index=False
        )
    )

    # ========================================================
    # PIVOT TABLE
    # ========================================================

    print(
        "\n=============================="
    )

    print(
        "PIVOT TABLE"
    )

    print(
        "=============================="
    )

    pivot = build_pivot_table(
        df
    )

    print(
        pivot
    )

    # ========================================================
    # BUSINESS INSIGHTS
    # ========================================================

    print(
        "\n=============================="
    )

    print(
        "BUSINESS INSIGHTS"
    )

    print(
        "=============================="
    )

    insights = create_business_insights(
        df,
        summary,
        pivot
    )

    for line in insights:
        print(line)

    # ========================================================
    # WRITE REPORT
    # ========================================================

    report = write_segment_insights(
        df
    )

    print(
        "\n=============================="
    )

    print(
        f"Report generated: {report}"
    )

    print(
        "=============================="
    )