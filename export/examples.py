"""
Example Export Usage

Demonstrates how to use the export system to generate
multi-format reports and deliver them to stakeholders.
"""

import pandas as pd
from export.export_manager import ExportManager
from export.export_scheduler import ExportScheduler
import plotly.graph_objects as go
import plotly.express as px


def example_basic_export():
    """Example 1: Basic export with CSV and HTML."""
    # Create sample data
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=30),
        'revenue': [1000 + i*50 for i in range(30)],
        'customers': [100 + i*5 for i in range(30)],
        'churn_rate': [0.05 + i*0.001 for i in range(30)]
    })

    # Initialize exporter
    exporter = ExportManager(base_output_dir="output")

    # Create summary markdown
    summary = """
    # Weekly Revenue Report
    
    ## Overview
    This week showed strong revenue growth with a 15% increase week-over-week.
    Customer acquisition remained steady at 5 new customers per day.
    
    ## Key Metrics
    - Total Revenue: $45,000
    - New Customers: 150
    - Churn Rate: 3.5%
    
    ## Recommendations
    1. Continue current marketing strategy
    2. Invest in customer retention programs
    3. Focus on high-value segments
    """

    # Create sample charts
    fig_revenue = px.line(
        df,
        x='date',
        y='revenue',
        title='Daily Revenue Trend'
    )

    fig_customers = px.bar(
        df,
        x='date',
        y='customers',
        title='Daily New Customers'
    )

    charts = {
        'Revenue Trend': fig_revenue,
        'New Customers': fig_customers,
    }

    # Define data dictionary
    data_dict = {
        'date': 'Transaction date',
        'revenue': 'Daily revenue in USD',
        'customers': 'Number of new customers',
        'churn_rate': 'Customer churn rate (%)'
    }

    # Export
    result = exporter.export_analysis(
        df=df,
        report_name="Weekly_Revenue_Report",
        summary_text=summary,
        charts_dict=charts,
        metadata={
            'source': 'sales_database',
            'frequency': 'weekly',
            'last_updated': '2024-01-15'
        },
        data_dictionary=data_dict
    )

    print("Export completed!")
    print(f"CSV: {result['csv']}")
    print(f"HTML: {result['html']}")
    print(f"PDF: {result['pdf']}")


def example_send_report():
    """Example 2: Export and send via email."""
    exporter = ExportManager(base_output_dir="output")

    # ... (prepare data and export as above) ...
    result = {}  # Placeholder for export result

    # Send via email
    success = exporter.send_report(
        export_result=result,
        recipient_email="manager@company.com",
        subject="Weekly Revenue Report - Ready for Review",
        body="""
        Hi Manager,

        Your weekly revenue report is ready. 

        Key highlights:
        - Revenue up 15% week-over-week
        - 150 new customers acquired
        - Churn rate stable at 3.5%

        Download the attached files to review full analysis.

        Thanks,
        Analytics Team
        """,
        include_files=['csv', 'html', 'metadata']
    )

    if success:
        print("Report sent successfully!")
    else:
        print("Failed to send report")


def example_scheduled_export():
    """Example 3: Schedule weekly report generation."""
    scheduler = ExportScheduler()

    def generate_weekly_report():
        """This runs every Monday at 9am."""
        print("Generating weekly report...")
        # Load data, create visualizations, export
        # exporter.export_analysis(...)

    # Schedule to run every Monday at 9:00 AM
    scheduler.schedule_weekly(
        job_name="weekly_revenue_report",
        job_func=generate_weekly_report,
        day_of_week="mon",
        hour=9,
        minute=0
    )

    # Start scheduler
    scheduler.start()
    print("Scheduler started. Reports will run automatically.")

    # Keep running
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()


def example_with_error_handling():
    """Example 4: Export with error handling and alerts."""
    exporter = ExportManager(base_output_dir="output")

    try:
        # Prepare and export
        df = pd.DataFrame({...})  # Your data here
        result = exporter.export_analysis(
            df=df,
            report_name="Sales_Analysis",
            summary_text="# Sales Report",
        )
        print(f"Export successful: {result['timestamp']}")

    except Exception as e:
        print(f"Export failed: {str(e)}")
        # Error is logged automatically
        # Consider sending alert to data team via Slack/email


if __name__ == "__main__":
    print("Export System Examples")
    print("=" * 50)
    print("\nExample 1: Basic Export")
    # example_basic_export()

    print("\nExample 2: Send Report via Email")
    # example_send_report()

    print("\nExample 3: Scheduled Export")
    # example_scheduled_export()
