import os
import pandas as pd

os.makedirs('output', exist_ok=True)


def build_segment_summary(df: pd.DataFrame, group_cols=None, value_col='amount', agg_col='customer_id'):
    if group_cols is None:
        group_cols = ['customer_type']
    if not isinstance(group_cols, list):
        group_cols = [group_cols]

    required = set(group_cols)
    if not required.issubset(df.columns):
        missing = sorted(required - set(df.columns))
        raise ValueError(f'Missing required columns for grouping: {missing}')

    if value_col not in df.columns:
        raise ValueError(f'Missing value column: {value_col}')

    if agg_col not in df.columns:
        raise ValueError(f'Missing aggregation column: {agg_col}')

    summary = df.groupby(group_cols).agg(
        total_value=(value_col, 'sum'),
        record_count=(agg_col, 'count'),
        avg_value=(value_col, 'mean'),
    ).reset_index()

    summary = summary.sort_values('total_value', ascending=False)
    summary['value_rank'] = summary['total_value'].rank(ascending=False, method='dense').astype(int)
    return summary


def build_pivot_table(df: pd.DataFrame, index_col='customer_type', columns_col='product_category', value_col='amount'):
    if index_col not in df.columns or columns_col not in df.columns or value_col not in df.columns:
        raise ValueError('Required columns are missing for pivot table creation')

    pivot = pd.pivot_table(
        df,
        values=value_col,
        index=index_col,
        columns=columns_col,
        aggfunc='sum',
        fill_value=0,
    )
    return pivot


def write_segment_insights(df: pd.DataFrame, output_path='output/segment_insights.txt'):
    summary = build_segment_summary(df)
    pivot = build_pivot_table(df)

    lines = []
    lines.append('Segment Insights Report')
    lines.append('======================')
    lines.append('')
    lines.append('Top segments by total value:')
    lines.append(summary.head(10).to_string(index=False))
    lines.append('')
    lines.append('Pivot table by segment and product:')
    lines.append(pivot.to_string())

    with open(output_path, 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(lines))

    return output_path
