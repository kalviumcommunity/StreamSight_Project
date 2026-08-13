SELECT

    transaction_date,

    COUNT(user_id) AS total_users,

    COUNT(
        CASE
            WHEN completion_rate >= 50
            THEN 1
        END
    ) AS engaged_users,

    COUNT(
        CASE
            WHEN completion_rate >= 80
            THEN 1
        END
    ) AS high_engagement,

    ROUND(
        100.0 *
        COUNT(
            CASE
                WHEN completion_rate >= 80
                THEN 1
            END
        ) /
        COUNT(*),
        1
    ) AS conversion_pct

FROM customers_cleaned

GROUP BY transaction_date

ORDER BY transaction_date DESC;