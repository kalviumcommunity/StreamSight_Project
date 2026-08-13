SELECT

    customer_type,

    substr(transaction_date,1,7) AS month,

    COUNT(*) AS order_count,

    ROUND(SUM(amount),2) AS monthly_revenue,

    ROUND(AVG(amount),2) AS avg_order_value,

    COUNT(DISTINCT user_id) AS unique_customers,

    ROUND(
        SUM(amount) /
        COUNT(DISTINCT user_id),
        2
    ) AS revenue_per_customer

FROM customers_cleaned

GROUP BY customer_type, month

ORDER BY month DESC, monthly_revenue DESC;