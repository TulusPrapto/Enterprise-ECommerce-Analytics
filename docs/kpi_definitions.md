# KPI Definitions

## Purpose

This document defines the core business KPIs used in the **Enterprise E-Commerce Analytics** project.

The KPI layer is designed to keep business definitions consistent across the Python/Polars analytical pipeline and the Power BI semantic model.

## KPI Summary

| KPI | Definition | Primary Source | Grain / Context |
|---|---|---|---|
| Total Orders | Number of analytical orders | `fact_orders` | 1 row per order |
| Total Customers | Number of unique customers | `mart_customers` / `customer_unique_id` | 1 row per unique customer |
| Total Items Sold | Total quantity of products sold | `mart_products` / order items | 1 row per order item |
| Product Revenue | Sum of product prices | `mart_products` / order items | Order-item level |
| Freight Revenue | Sum of freight values | `fact_order_items` | Order-item level |
| GMV | Total product value including freight | `mart_products` | Order-item level |
| Average Order Value | GMV divided by total orders | `mart_products` + `fact_orders` | Order-level denominator |
| Repeat Customers | Customers with more than one order | `mart_customers` | Customer level |
| Repeat Customer Rate | Repeat Customers / Total Customers | `mart_customers` | Customer level |
| Cancellation Rate | Canceled Orders / Total Orders | `fact_orders` | Order level |
| Late Orders | Delivered orders arriving after estimated delivery date | `mart_logistics` | Order level |
| Late Delivery Rate | Late delivered orders / orders with delivery timestamp | `mart_logistics` | Order level |
| Average Delivery Days | Average elapsed time from purchase to customer delivery | `mart_logistics` | Delivered-order level |

## 1. Total Orders

**Definition:** Total number of orders in the analytical order population.

**Formula**

```text
COUNT(order_id)
```

**Source of Truth**

```text
fact_orders
```

**Grain**

```text
1 row = 1 order_id
```

**Official baseline:** `99,441`

The project validates `fact_orders.order_id` as unique and non-null.

## 2. Total Customers

**Definition:** Number of unique customers represented in the customer-level analytical population.

**Formula**

```text
COUNT(DISTINCT customer_unique_id)
```

**Source of Truth**

```text
mart_customers
```

**Grain:** `1 row = 1 customer_unique_id`

**Official baseline:** `96,096`

### Important modeling note

`customer_id` and `customer_unique_id` represent different analytical concepts in this project. For customer-level metrics such as total customers and repeat-customer analysis, use `customer_unique_id` rather than counting `customer_id` as though each record represented a distinct long-term customer.

## 3. Total Items Sold

**Definition:** Total quantity of products sold through analytical order items.

**Formula**

```text
SUM(quantity)
```

**Source of Truth:** `mart_products` with the underlying order-item grain retained.

**Official baseline:** `112,650`

**Grain:** `1 row = 1 order item`

## 4. Product Revenue

**Definition:** Total monetary value of product prices.

**Formula**

```text
SUM(price)
```

**Source of Truth:** `mart_products`

**Official baseline:** `13,591,643.70`

Product Revenue measures the product-price component only and does not include freight.

## 5. Freight Revenue

**Definition used in the Power BI reporting layer:** Total freight value associated with analytical order items.

**Formula**

```text
SUM(freight_value)
```

**Source:** `fact_order_items`

**Official baseline:** `2,251,909.54`

### Modeling note

Freight Revenue is used as a reporting KPI in Power BI. It is not separately listed as an official `MetricDefinition` entry in the current Python KPI catalog, so it should be treated as a reporting-layer measure derived from `fact_order_items`.

## 6. Gross Merchandise Value (GMV)

**Definition:** Total product value including freight value.

**Formula**

```text
SUM(price + freight_value)
```

**Source of Truth:** `mart_products`

**Official baseline:** `15,843,553.24`

### Relationship to Product Revenue

```text
GMV = Product Revenue + Freight Revenue
```

For the project baseline:

```text
13,591,643.70
+ 2,251,909.54
----------------
15,843,553.24
```

## 7. Average Order Value (AOV)

**Definition:** Average gross merchandise value per order.

**Formula**

```text
GMV / Total Orders
```

**Source of Truth:** `mart_products + fact_orders`

**Official baseline:** `159.33`

AOV is an order-level business KPI. It should not be calculated by averaging individual order-item prices.

## 8. Repeat Customers

**Definition:** Customers with more than one order across the available analytical period.

**Formula**

```text
COUNT(customer_unique_id where total_orders > 1)
```

**Source of Truth:** `mart_customers`

**Official baseline:** `2,997`

A customer is considered repeat when the same `customer_unique_id` is associated with more than one order.

## 9. Repeat Customer Rate

**Definition:** Percentage of customers with more than one order.

**Formula**

```text
Repeat Customers / Total Customers
```

**Source of Truth:** `mart_customers`

**Official baseline:** `3.12%`

**Exact baseline used in Python validation:** approximately `3.1188%`.

## 10. Cancellation Rate

**Definition:** Percentage of analytical orders whose status is `canceled`.

**Formula**

```text
Canceled Orders / Total Orders
```

**Source of Truth:** `fact_orders`

**Numerator:** `order_status = "canceled"`

**Denominator:** all analytical orders.

## 11. Late Orders

**Definition:** Number of delivered orders whose actual delivery date occurred after the estimated delivery date.

**Source of Truth:** `mart_logistics`

**Business rule:**

```text
is_late_delivery = true
```

where:

```text
estimated_delivery_variance_days > 0
```

The variance is calculated using **date-level logic**:

```text
actual customer delivery date
-
estimated delivery date
```

**Official baseline:** `6,535`

### Important implementation note

The Power BI implementation was reconciled to the Python analytical definition after identifying that a DateTime comparison incorrectly classified same-day deliveries with different time components as late. The final Power BI measure therefore uses date-level comparison to match the analytical mart definition.

## 12. Late Delivery Rate

**Definition:** Percentage of orders with a delivery timestamp that arrived after the estimated delivery date.

**Formula**

```text
Late Delivered Orders / Orders With Delivery Timestamp
```

**Source of Truth:** `mart_logistics`

**Numerator:** `is_late_delivery = true`

**Denominator:** `has_delivery_timestamp = true`

**Official baseline:** `6.77%`

**Exact baseline from the current analytical mart:** `0.06773705377503213` (approximately `6.773705%`).

## 13. Average Delivery Days

**Definition:** Average elapsed time from order purchase to customer delivery.

**Formula**

```text
AVERAGE(purchase_to_delivery_days)
```

where:

```text
purchase_to_delivery_days = customer delivery timestamp - order purchase timestamp
```

**Source of Truth:** `mart_logistics`

**Inclusion rule:** orders with a non-null customer delivery timestamp.

**Official baseline:** `12.56 days`

**Exact baseline from the current analytical mart:** `12.558702304032051 days`.

The Power BI implementation was aligned to the analytical definition by calculating elapsed seconds and dividing by `86,400` seconds per day rather than using whole-day `DATEDIFF` logic.

## KPI Validation Baseline

The final reconciled KPI baseline used for the default all-data context is:

| KPI | Value |
|---|---:|
| Total Orders | 99,441 |
| Total Items Sold | 112,650 |
| Product Revenue | 13,591,643.70 |
| Freight Revenue | 2,251,909.54 |
| GMV | 15,843,553.24 |
| Average Order Value | 159.33 |
| Total Customers | 96,096 |
| Repeat Customers | 2,997 |
| Repeat Customer Rate | 3.12% |
| Late Orders | 6,535 |
| Late Delivery Rate | 6.77% |
| Average Delivery Days | 12.56 |

## Filter Context

All KPIs are intended to be evaluated under Power BI filter context.

For the default dashboard presentation:

```text
Year:
2017 + 2018
```

`2016` remains available in the underlying model and can be selected by the user.

When filters such as Year or Order Status are applied, the displayed KPI values are expected to change according to the active filter context.

## Governance Principles

1. Business definitions should be documented before or alongside implementation.
2. Python/Polars analytical calculations and Power BI DAX should follow the same KPI contract.
3. Grain must be preserved when calculating metrics.
4. Customer-level metrics should use `customer_unique_id`.
5. Logistics classification must use the same date-level business rule across analytical and reporting layers.
6. KPI mismatches must be investigated before final reporting.
7. Descriptive findings should not be presented as causal conclusions without supporting analysis.

## Validation Status

The KPI layer has been validated through:

- primary-key checks
- foreign-key/orphan checks
- fact-to-mart reconciliation
- date-dimension coverage checks
- KPI reconciliation between Python/Polars and Power BI
- filter and slicer testing
- cross-page Year synchronization
- logistics KPI definition reconciliation

Final logistics reconciliation:

```text
Late Orders = 6,535
Late Delivery Rate = 6.77%
Average Delivery Days = 12.56
```

These values are the approved baseline for the current Power BI report.
