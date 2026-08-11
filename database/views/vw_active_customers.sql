-- vw_active_customers
-- Customer activity view used by dashboards that need customer engagement and order recency.
CREATE VIEW vw_active_customers AS
SELECT
  c.customer_id,
  c.customer_name,
  c.customer_type,
  COUNT(DISTINCT o.order_id) AS order_count_30d,
  SUM(o.order_amount) AS revenue_30d,
  MAX(o.order_date) AS last_order_date,
  DATE_PART('day', CURRENT_DATE - MAX(o.order_date)) AS days_since_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
  AND o.order_date >= CURRENT_DATE - INTERVAL '30 days'
WHERE c.deleted_at IS NULL
GROUP BY c.customer_id, c.customer_name, c.customer_type;
