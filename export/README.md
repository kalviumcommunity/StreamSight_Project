# Export & Report Generation System

## Overview

The Export & Report Generation system automates the delivery of analytical insights to stakeholders in multiple formats:

- **CSV Datasets** - Raw data for Excel analysis with metadata
- **PDF Reports** - Executive summaries suitable for email and meetings
- **HTML Interactive Reports** - Full analysis with embedded Plotly charts
- **Automated Email Delivery** - Reports sent to stakeholders on schedule
- **Version Control** - Track all export history with timestamps
- **Error Handling** - Graceful failures with logging and alerts

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Email Configuration

Copy the environment template and add your credentials:

```bash
cp export/.env.example .env
```

Edit `.env` with your SMTP settings:

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
```

**For Gmail:**
1. Enable 2-Factor Authentication
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Generate a password for "Mail" and "Windows Computer"
4. Use the generated password in `.env`

## Quick Start

### Basic Export (CSV + HTML)

```python
from export.export_manager import ExportManager
import pandas as pd
import plotly.express as px

# Initialize exporter
exporter = ExportManager(base_output_dir="output")

# Prepare your data
df = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=30),
    'revenue': [1000 + i*50 for i in range(30)],
    'customers': [100 + i*5 for i in range(30)]
})

# Create a summary
summary = """
# Weekly Report

Revenue grew 15% this week.

- Total: $45,000
- New Customers: 150
"""

# Create visualizations
fig = px.line(df, x='date', y='revenue', title='Revenue Trend')

# Export in all formats
result = exporter.export_analysis(
    df=df,
    report_name="Weekly_Report",
    summary_text=summary,
    charts_dict={'Revenue': fig},
    data_dictionary={'revenue': 'Daily revenue', 'customers': 'New customers'}
)

# Result contains:
# {
#   'csv': '/path/to/data.csv',
#   'html': '/path/to/report.html',
#   'pdf': '/path/to/report.pdf',
#   'metadata': '/path/to/metadata.json',
#   'timestamp': '2024-01-15_143022'
# }
```

### Send Report via Email

```python
# Send the generated report
exporter.send_report(
    export_result=result,
    recipient_email="manager@company.com",
    subject="Weekly Report - Ready for Review",
    body="Your weekly revenue report is attached.",
    include_files=['csv', 'html', 'metadata']
)
```

### Schedule Automated Reports

```python
from export.export_scheduler import ExportScheduler

scheduler = ExportScheduler()

def generate_weekly_report():
    # Your export logic here
    pass

# Run every Monday at 9:00 AM
scheduler.schedule_weekly(
    job_name="weekly_report",
    job_func=generate_weekly_report,
    day_of_week="mon",
    hour=9,
    minute=0
)

scheduler.start()
```

## Output Structure

Each export creates a timestamped directory:

```
output/
├── Weekly_Report/
│   ├── 2024-01-15_143022/
│   │   ├── data.csv                 # Dataset
│   │   ├── data_dictionary.json     # Column descriptions
│   │   ├── metadata.json            # Report metadata
│   │   ├── report.html              # Interactive report
│   │   ├── report.pdf               # Executive summary
│   │   └── README.md                # Usage guide
│   ├── 2024-01-14_093045/           # Previous version
│   └── ...
├── logs/
│   ├── exports_20240115.log         # Daily log file
│   └── export_errors.log            # Error tracking
└── export_history.json              # Version control
```

## Features

### 1. Multi-Format Export

All three formats (CSV, PDF, HTML) are generated from a single call:

```python
result = exporter.export_analysis(
    df=your_data,
    report_name="Sales_Report",
    summary_text=markdown_content,
    charts_dict={'Sales': fig1, 'Growth': fig2}
)
```

### 2. Data Dictionary

Include column descriptions in CSV exports:

```python
data_dict = {
    'revenue': 'Total sales in USD',
    'customers': 'Number of unique customers',
    'churn_rate': 'Percentage of customers lost'
}

result = exporter.export_analysis(
    df=df,
    report_name="Report",
    summary_text="...",
    data_dictionary=data_dict
)
```

### 3. Interactive HTML Reports

- Responsive design works on all devices
- Embedded Plotly charts are fully interactive
- Data preview table at bottom
- Professional styling and navigation
- Self-contained (no external dependencies needed)

### 4. Version Control & History

Track all exports automatically:

```python
# Get report history
history = exporter.get_report_history("Weekly_Report")

print(f"Total exports: {history['total_exports']}")
print(f"Successful: {history['successful_exports']}")
print(f"Failed: {history['failed_exports']}")
print(f"Latest: {history['latest']}")
```

### 5. Automated Cleanup

Remove old exports to save disk space:

```python
from export.version_control import VersionControl

vc = VersionControl(Path("output"))

# Keep only last 30 days
removed = vc.cleanup_old_exports(days_to_keep=30)
print(f"Cleaned up {removed} directories")
```

## Error Handling

The system handles errors gracefully:

```python
try:
    result = exporter.export_analysis(...)
except Exception as e:
    # Error is logged automatically
    # Alert file is created at: output/logs/export_errors.log
    # Retry logic can be implemented here
    print(f"Export failed: {str(e)}")
```

Errors are tracked in `output/logs/export_errors.log` with timestamps and details.

## Email Delivery

### Simple Email

```python
exporter.send_report(
    export_result=result,
    recipient_email="user@company.com",
    subject="Your Report",
    body="Report is ready.",
    include_files=['csv', 'html']
)
```

### Bulk Email to Multiple Recipients

```python
from export.email_delivery import EmailDelivery

email = EmailDelivery()

recipients = ['user1@company.com', 'user2@company.com']
status = email.send_bulk_reports(
    recipients=recipients,
    subject="Team Report",
    body="Analysis complete.",
    attachments=[result['csv'], result['html']]
)

for email_addr, success in status.items():
    print(f"{email_addr}: {'✓' if success else '✗'}")
```

### Professional Email Template

```python
from export.email_delivery import EmailDelivery

body = EmailDelivery.create_email_template(
    report_name="Weekly Sales",
    key_findings=[
        "Revenue up 15% week-over-week",
        "150 new customers acquired",
        "Churn rate stable at 3.5%"
    ],
    dashboard_url="https://dashboard.company.com",
    next_run="Next Monday at 9 AM"
)

exporter.send_report(
    export_result=result,
    recipient_email="manager@company.com",
    subject="Weekly Sales Report",
    body=body
)
```

## Configuration

Edit `export/config.json` to customize:

- Output directory
- PDF page settings
- HTML styling
- Email recipients
- Scheduled report frequency
- Logging level
- Error handling retry logic

## API Reference

### ExportManager

```python
# Main export function
export_analysis(
    df,                    # DataFrame to export
    report_name,           # Report identifier
    summary_text,          # Markdown summary
    charts_dict=None,      # Dict of chart names -> Plotly figures
    metadata=None,         # Custom metadata
    data_dictionary=None   # Column descriptions
)

# Email delivery
send_report(
    export_result,         # Result from export_analysis()
    recipient_email,       # Email address
    subject,               # Email subject
    body,                  # Email body
    include_files=None     # Files to attach
)

# Version history
get_report_history(report_name)
```

### ExportScheduler

```python
# Schedule daily report
schedule_daily(job_name, job_func, hour=9, minute=0)

# Schedule weekly report
schedule_weekly(job_name, job_func, day_of_week="mon", hour=9, minute=0)

# Schedule monthly report
schedule_monthly(job_name, job_func, day_of_month=1, hour=9, minute=0)

# Start/stop scheduler
start()
stop()
```

### VersionControl

```python
# Get report history
get_report_history(report_name)

# Get latest export
get_latest_export(report_name)

# Get exports since date
get_exports_since(report_name, days_ago=7)

# Cleanup old files
cleanup_old_exports(days_to_keep=30)
```

## Troubleshooting

### PDF Generation Issues

If PDF generation fails, WeasyPrint may not be installed:

```bash
pip install weasyprint
```

On macOS, you may need:
```bash
brew install python3 cairo pango gdk-pixbuf libffi
```

### Email Not Sending

Check that `.env` is properly configured:

```bash
# Verify credentials are set
echo $SENDER_EMAIL
echo $SENDER_PASSWORD
```

For Gmail, ensure:
1. 2FA is enabled
2. App password is used (not regular password)
3. Port is 587 (not 465)
4. TLS is enabled

### Memory Issues with Large Datasets

For very large CSVs, consider exporting in chunks:

```python
# Export only a sample for HTML preview
preview_df = df.head(1000)

result = exporter.export_analysis(
    df=df,              # Full data for CSV
    report_name="...",
    summary_text="...",
    # ... HTML will use preview_df for data table
)
```

## Performance Tips

1. **Batch Processing** - Export multiple reports in sequence to avoid memory issues
2. **Chart Optimization** - Use `sample()` for large datasets in charts
3. **Asynchronous Scheduling** - Use `ExportScheduler` for non-blocking execution
4. **Cleanup** - Regularly run `cleanup_old_exports()` to free disk space

## Security Considerations

1. **Credentials** - Never commit `.env` to version control
2. **Email** - Use app passwords, not plain credentials
3. **File Permissions** - Set restrictive permissions on export directories
4. **Data Privacy** - Include appropriate disclaimers in reports
5. **Archive** - Keep reports only as long as retention policy allows

## Contributing

To extend the export system:

1. Add new generators (e.g., `Excel export`) in new module
2. Update `ExportManager` to call new generator
3. Add tests in `test_export_*.py`
4. Update documentation

## Version History

- **v2.50** (Jan 2024) - Initial release with CSV, PDF, HTML, and email support
- Scheduled exports via APScheduler
- Version control and history tracking
- Error handling and logging
- Professional HTML templates
