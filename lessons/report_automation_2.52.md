# Report Automation: Exports for Stakeholders

Hey Report Automation Expert!

Welcome. Analysis lives in notebooks and dashboards. But stakeholders need portable outputs: Excel datasets, PDF reports, HTML summaries they can download, save, share. This lesson teaches you to export analytical output in formats stakeholders understand - CSV for data, PDF for reports, HTML for interactive sharing - and to automate this process so new reports generate on schedule without manual work.

Every analysis that was never acted on because stakeholders could not download the results, that was lost when a dashboard went down, or that required an analyst to regenerate it manually every week failed at export strategy. This lesson teaches you to build export pipelines that deliver insights to stakeholders reliably and automatically.

## The Real Scenario

### The Problem

An analyst finishes a weekly churn report. The data lives only in a Streamlit app. A business partner asks "can you send me the cleaned dataset and the summary?" The analyst must manually export to CSV. The report is in markdown - the partner wants PDF. The visualizations are Plotly - the partner needs static images. Manual work multiplies. This happens every week. The analyst spends more time exporting than analyzing.

### The Solution

Build automated export functions that generate CSV, PDF, and HTML at the push of a button (or on a schedule). One command produces cleaned data, summary report, and visualizations in multiple formats. Stakeholders download what they need. Analysts focus on analysis, not manual exports.

## Designing For Multiple Output Formats

Three Output Formats Every Analysis Needs

1. Cleaned CSV Dataset

The raw data output. Enable stakeholders to do their own analysis in Excel. Include metadata: source, refresh date, record count, data dictionary.

2. PDF Summary Report

Executive summary + key findings. Portable, shareable, suitable for email and meetings. No interactivity - all insights are baked in.

3. HTML Interactive Report

Full analysis with interactive Plotly charts. Stakeholders explore in browser. Can be emailed as single file or hosted on intranet.

## Automating Export With Reusable Functions

Write Once, Export Everywhere

Export function pattern

Create a function that accepts dataframe, summary text, and charts. It outputs CSV to one folder, converts markdown summary to PDF, embeds charts in HTML. One call generates all formats.

Example snippet (see `export/report_exporter.py`):

```python
from export.report_exporter import export_analysis

# df: pandas.DataFrame
# summary_text: markdown string
# charts_dict: {'chart name': plotly_fig}

paths = export_analysis(df, summary_text, charts_dict, output_dir='output/reports')
print(paths)
```

## Versioning and Tracking Report Changes

Report history enables audit trails and comparisons

Always timestamp outputs. Use format: YYYY-MM-DD_HHMMSS. Keep previous reports available so stakeholders can compare week-to-week or month-to-month. Archived reports answer "Did this metric improve from last month?" without regenerating. Timestamp enables traceability - which version was used for which decision.

## Handling Errors In Automated Exports

Automated processes must not crash silently

If scheduled export fails (database down, missing column, permission denied), the script should: (1) Log error with timestamp and details, (2) Send alert to data team, (3) Skip export gracefully without crashing, (4) Retry on next schedule. Never leave stakeholders without reports - if export fails, notify them immediately so they know to check the dashboard manually.

## Email Delivery Of Reports

Automated email delivery moves insights from analyst desk to executive inbox

After export completes, send email with: (1) Brief summary of key findings, (2) Links to download CSV and HTML, (3) Link to dashboard, (4) When next report runs. Email delivery bypasses the "I forgot to download the report" problem. Insights reach stakeholders proactively.

**You just learned** how to automate report generation and delivery. Stakeholders receive fresh analysis on schedule. Analysts are freed from manual exports. This is how data products scale.
