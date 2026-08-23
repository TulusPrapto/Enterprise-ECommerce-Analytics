-- =============================================================================
-- 05_data_quality_checks.sql
-- Purpose:
--   Validate critical data-quality and referential-integrity conditions
--   across the analytical order, customer, product, and order-item layers.
--
-- Checks:
--   1. Duplicate order IDs
--   2. NULL critical order fields
--   3. Orphan customer keys
--   4. Orphan product keys
--
-- Expected result:
--   All issue counts should be zero.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Duplicate order IDs
-- -----------------------------------------------------------------------------

SELECT
    'duplicate_order_ids' AS check_name,
    COUNT(*) AS issue_count
FROM (
    SELECT
        order_id
    FROM read_parquet('data/analytical/fact_orders.parquet')
    GROUP BY order_id
    HAVING COUNT(*) > 1
);


-- -----------------------------------------------------------------------------
-- 2. NULL critical order fields
-- -----------------------------------------------------------------------------

SELECT
    'null_order_id' AS check_name,
    COUNT(*) AS issue_count
FROM read_parquet('data/analytical/fact_orders.parquet')
WHERE order_id IS NULL

UNION ALL

SELECT
    'null_customer_id' AS check_name,
    COUNT(*) AS issue_count
FROM read_parquet('data/analytical/fact_orders.parquet')
WHERE customer_id IS NULL

UNION ALL

SELECT
    'null_purchase_timestamp' AS check_name,
    COUNT(*) AS issue_count
FROM read_parquet('data/analytical/fact_orders.parquet')
WHERE order_purchase_timestamp IS NULL;


-- -----------------------------------------------------------------------------
-- 3. Orphan customer keys
-- -----------------------------------------------------------------------------

SELECT
    'orphan_customer_ids' AS check_name,
    COUNT(*) AS issue_count
FROM read_parquet('data/analytical/fact_orders.parquet') AS o
LEFT JOIN read_parquet('data/analytical/dim_customers.parquet') AS c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;


-- -----------------------------------------------------------------------------
-- 4. Orphan product keys
-- -----------------------------------------------------------------------------

SELECT
    'orphan_product_ids' AS check_name,
    COUNT(*) AS issue_count
FROM read_parquet('data/analytical/fact_order_items.parquet') AS i
LEFT JOIN read_parquet('data/analytical/dim_products.parquet') AS p
    ON i.product_id = p.product_id
WHERE p.product_id IS NULL;