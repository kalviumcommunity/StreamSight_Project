# KPI Sources and Lineage

This document lists the data sources and reasoning for each KPI implemented in `kpi_dashboard.py`.

1. Total Revenue
   - Source: `output/processed_sales.csv`
   - Column: `amount`
   - Definition: Sum of `amount` for the report month (determined from the latest date available in the clean layer). Prior period uses the previous calendar month.
   - Validation: Cross-check sums against downstream aggregations or `database/views/vw_monthly_revenue.sql` if present.

2. Active Users
   - Source: `output/validated_engagement_data.csv`
   - Column: `user_id`, `transaction_date`
   - Definition: Count of distinct `user_id` who have activity in the report month.
   - Validation: Compare with `vw_active_users` view if available.

3. Average Order Value (AOV)
   - Source: `output/processed_sales.csv`
   - Column: `amount`
   - Definition: Mean `amount` for orders in the report month.

4. Churn Rate
   - Source: `output/processed_sales.csv`
   - Column: `customer_id`, `transaction_date`
   - Definition: Percentage of customers who purchased in the prior month but did not purchase in the report month. Expressed as a percent.
   - Note: If there is no prior-month data available, churn is reported as 0.0% to avoid division by zero.

5. Customer Satisfaction
   - Source: `output/validated_engagement_data.csv`
   - Column: `completion_rate`
   - Definition: Mean `completion_rate` for the report month mapped to a 5-point scale by dividing by 20 (so 100% -> 5.0).

General notes
- All KPI computations derive from cleaned/validated CSVs under `output/` (the clean data layer), not raw uploads.
- The dashboard determines the report month using the most recent `transaction_date` across these files so it adapts to newly uploaded data automatically.
- Percent change between current and prior period is computed as: `(current - prior) / prior * 100`. If the prior value is 0, change is reported as `0%` to avoid misleading infinities.
