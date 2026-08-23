-- =============================================================================
-- 03_product_performance.sql
-- Purpose:
--   Rank products by gross revenue using the analytical product and
--   order-item layers.
--
-- Business questions:
--   1. Which products generate the most gross revenue?
--   2. What product categories do the top products belong to?
--   3. How concentrated is revenue among top-performing products?
--
-- Revenue definition:
--   Gross revenue is calculated from fact_order_items.item_gross_value.
--
-- SQL skills demonstrated:
--   - CTE
--   - JOIN
--   - GROUP BY
--   - SUM
--   - Window function / RANK
--   - Top-N filtering
-- =============================================================================

WITH product_sales AS (
    SELECT
        i.product_id,
        p.product_category_name,
        SUM(i.item_gross_value) AS gross_revenue,
        COUNT(*) AS items_sold,
        COUNT(DISTINCT i.order_id) AS orders
    FROM read_parquet('data/analytical/fact_order_items.parquet') AS i
    INNER JOIN read_parquet('data/analytical/dim_products.parquet') AS p
        ON i.product_id = p.product_id
    GROUP BY
        i.product_id,
        p.product_category_name
),

ranked_products AS (
    SELECT
        product_id,
        product_category_name,
        gross_revenue,
        items_sold,
        orders,
        RANK() OVER (
            ORDER BY gross_revenue DESC
        ) AS revenue_rank
    FROM product_sales
)

SELECT
    revenue_rank,
    product_id,
    COALESCE(product_category_name, 'Unknown') AS product_category,
    items_sold,
    orders,
    ROUND(gross_revenue, 2) AS gross_revenue
FROM ranked_products
WHERE revenue_rank <= 10
ORDER BY revenue_rank;