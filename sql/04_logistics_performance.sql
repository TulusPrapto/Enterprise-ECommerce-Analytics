-- =============================================================================
-- 04_logistics_performance.sql
-- Purpose:
--   Analyze delivery performance using actual and estimated delivery dates.
--
-- Business questions:
--   1. How many orders were delivered?
--   2. How many delivered orders were late?
--   3. What is the late delivery rate?
--   4. What is the average delivery time?
--
-- Delivery analysis scope:
--   Only orders with an actual delivered customer date are included.
--
-- Late delivery definition:
--   Actual delivery date > estimated delivery date.
--
-- SQL skills demonstrated:
--   - CTE
--   - CASE WHEN
--   - Date arithmetic
--   - Aggregate calculations
--   - Conditional aggregation
-- =============================================================================

WITH delivery_metrics AS (
    SELECT
        order_id,
        order_status,
        order_purchase_timestamp,
        order_delivered_customer_date,
        order_estimated_delivery_date,

        DATE_DIFF(
            'day',
            CAST(order_purchase_timestamp AS DATE),
            CAST(order_delivered_customer_date AS DATE)
        ) AS delivery_days,

        CASE
            WHEN order_delivered_customer_date
                 > order_estimated_delivery_date
            THEN 1
            ELSE 0
        END AS is_late

    FROM read_parquet('data/analytical/fact_orders.parquet')

    WHERE order_delivered_customer_date IS NOT NULL
)

SELECT
    COUNT(*) AS delivered_orders,

    SUM(is_late) AS late_orders,

    ROUND(
        100.0 * SUM(is_late) / COUNT(*),
        2
    ) AS late_delivery_rate_pct,

    ROUND(
        AVG(delivery_days),
        2
    ) AS average_delivery_days,

    MIN(delivery_days) AS min_delivery_days,

    MAX(delivery_days) AS max_delivery_days

FROM delivery_metrics;