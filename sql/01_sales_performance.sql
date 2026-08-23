-- =============================================================================
-- 01_sales_performance.sql
-- Purpose:
--   Analyze monthly sales performance using the analytical Parquet layer.
--
-- Data sources:
--   - fact_orders
--   - fact_order_items
--
-- Business questions:
--   1. How many orders were placed each month?
--   2. How many items were sold?
--   3. What was the gross revenue?
--   4. What was the average order value?
--
-- SQL skills demonstrated:
--   - CTE
--   - JOIN
--   - DATE_TRUNC
--   - GROUP BY
--   - COUNT DISTINCT
--   - SUM
--   - CASE-safe division
-- =============================================================================

WITH order_items AS (
    SELECT
        o.order_id,
        o.order_purchase_timestamp,
        i.order_item_id,
        i.item_gross_value
    FROM read_parquet('data/analytical/fact_orders.parquet') AS o
    INNER JOIN read_parquet('data/analytical/fact_order_items.parquet') AS i
        ON o.order_id = i.order_id
),

monthly_sales AS (
    SELECT
        DATE_TRUNC('month', order_purchase_timestamp) AS sales_month,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(order_item_id) AS total_items_sold,
        SUM(item_gross_value) AS gross_revenue
    FROM order_items
    GROUP BY
        DATE_TRUNC('month', order_purchase_timestamp)
)

SELECT
    sales_month,
    total_orders,
    total_items_sold,
    ROUND(gross_revenue, 2) AS gross_revenue,
    ROUND(
        gross_revenue / NULLIF(total_orders, 0),
        2
    ) AS average_order_value
FROM monthly_sales
ORDER BY sales_month;