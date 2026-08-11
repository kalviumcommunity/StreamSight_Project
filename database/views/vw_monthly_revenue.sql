-- vw_monthly_revenue
-- Official monthly revenue definition for dashboards.
-- Uses net revenue after refunds and only includes shipped orders.
CREATE VIEW vw_monthly_revenue AS
SELECT
  DATE_TRUNC('month', o.order_date) AS revenue_month,
  COUNT(DISTINCT o.order_id) AS order_count,
  SUM(o.order_amount) - COALESCE(SUM(r.refund_amount), 0) AS net_revenue,
  AVG(o.order_amount) AS average_order_value,
  COUNT(DISTINCT o.customer_id) AS active_customers
FROM orders o
LEFT JOIN refunds r ON o.order_id = r.order_id
WHERE o.order_status = 'shipped'
GROUP BY DATE_TRUNC('month', o.order_date);
