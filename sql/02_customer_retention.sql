-- =============================================================================
-- 02_customer_retention.sql
-- Purpose:
--   Analyze customer repeat-purchase behavior using the customer_unique_id
--   grain from the analytical customer dimension.
--
-- Business questions:
--   1. How many customers placed one order?
--   2. How many customers placed multiple orders?
--   3. What is the repeat customer rate?
--
-- Customer definition:
--   customer_unique_id represents the unique customer across orders.
--
-- Repeat customer definition:
--   A customer with two or more distinct orders.
--
-- SQL skills demonstrated:
--   - CTEs
--   - JOIN
--   - COUNT DISTINCT
--   - GROUP BY
--   - CASE WHEN
--   - Aggregate calculations
-- =============================================================================

WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM read_parquet('data/analytical/fact_orders.parquet') AS o
    INNER JOIN read_parquet('data/analytical/dim_customers.parquet') AS c
        ON o.customer_id = c.customer_id
    GROUP BY
        c.customer_unique_id
),

customer_segments AS (
    SELECT
        customer_unique_id,
        order_count,
        CASE
            WHEN order_count = 1 THEN 'One-time Customer'
            WHEN order_count >= 2 THEN 'Repeat Customer'
        END AS customer_segment
    FROM customer_orders
)

SELECT
    customer_segment,
    COUNT(*) AS customers,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS customer_rate_pct
FROM customer_segments
GROUP BY
    customer_segment
ORDER BY
    customers DESC;