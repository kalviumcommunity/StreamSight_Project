-- agg_daily_revenue
-- Daily pre-aggregated revenue table for high-performance dashboard queries.
CREATE TABLE IF NOT EXISTS agg_daily_revenue (
  aggregation_date DATE,
  product_line VARCHAR(100),
  total_revenue NUMERIC(18,2),
  order_count INTEGER,
  avg_order_value NUMERIC(18,2),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO agg_daily_revenue (aggregation_date, product_line, total_revenue, order_count, avg_order_value, updated_at)
SELECT
  DATE(o.order_date) AS aggregation_date,
  p.product_line,
  SUM(o.order_amount) AS total_revenue,
  COUNT(DISTINCT o.order_id) AS order_count,
  AVG(o.order_amount) AS avg_order_value,
  CURRENT_TIMESTAMP AS updated_at
FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE o.order_status = 'shipped'
GROUP BY DATE(o.order_date), p.product_line;
