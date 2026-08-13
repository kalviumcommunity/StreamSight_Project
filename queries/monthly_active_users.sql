SELECT
    substr(transaction_date,1,7) AS month,

    COUNT(DISTINCT user_id) AS active_users,

    COUNT(DISTINCT CASE
        WHEN customer_type='Enterprise'
        THEN user_id
    END) AS enterprise_users,

    COUNT(DISTINCT CASE
        WHEN customer_type='SMB'
        THEN user_id
    END) AS smb_users

FROM customers_cleaned

GROUP BY month

ORDER BY month DESC;