# Data Model

## Purpose

This document describes the analytical data architecture and Power BI semantic model used in the **Enterprise E-Commerce Analytics** project.

The model separates analytical facts, reusable dimensions, business-oriented marts, KPI outputs, and reporting semantics so that business metrics can be validated before they are presented in Power BI.

---

## 1. Architecture Overview

The project follows this analytical flow:

```text
Raw / Cleaning
      v
Analytical Facts
      v
Dimensions
      v
Analytical Marts
      v
KPI Metric Catalog
      v
KPI Calculation
      v
Reporting Layer
      v
Power BI Semantic Model
      v
DAX Measures
      v
Dashboard / Storytelling
```

The Python/Polars analytical layer is the source foundation for the Power BI reporting layer.

The main principle is:

```text
Build -> Validate -> Reconcile -> Save -> Report
```

---

## 2. Analytical Layers

### 2.1 Analytical Facts

The detailed transaction layer contains:

```text
fact_orders
fact_order_items
fact_order_payments
fact_order_reviews
```

These tables preserve different business grains and should not be flattened into a single unrestricted mega-table.

### 2.2 Dimensions

The reusable dimensions are:

```text
dim_date
dim_customers
dim_products
dim_sellers
```

Dimensions provide descriptive context for analytical facts.

### 2.3 Analytical Marts

Business-oriented marts are:

```text
mart_sales
mart_customers
mart_products
mart_logistics
```

Marts provide specialized analytical views and remain useful for validation, business analysis, and specialized reporting.

### 2.4 KPI / Reporting Outputs

The analytical reporting layer also contains:

```text
kpi_summary
kpi_monthly
```

These provide precomputed KPI outputs used for validation and reporting reference.

---

## 3. Dimension Tables

| Table | Rows | Grain | Primary Key / Business Identifier |
|---|---:|---|---|
| `dim_date` | 800 | One row per calendar date | `date` / `date_key` |
| `dim_customers` | 99,441 | One row per `customer_id` | `customer_id` |
| `dim_products` | 32,951 | One row per product | `product_id` |
| `dim_sellers` | 3,095 | One row per seller | `seller_id` |

### `dim_date`

`dim_date` is the dedicated calendar dimension.

Its coverage is:

```text
2016-09-04 -> 2018-11-12
```

It contains calendar attributes such as:

- date
- year
- quarter
- quarter number
- month
- month number
- month name
- year_month
- year_month_sort
- week
- day
- day name
- day of week
- weekend flag

In Power BI, `dim_date` is configured as the official Date Table.

### `dim_customers`

`dim_customers` is keyed by `customer_id`.

It also contains `customer_unique_id`, which represents the long-term customer identity used by customer-level metrics such as:

```text
Total Customers
Repeat Customers
Repeat Customer Rate
```

The distinction is important:

```text
customer_id
    = order/customer record identifier in the source analytical model

customer_unique_id
    = unique long-term customer identifier
```

### `dim_products`

Provides product-level attributes used for:

- category analysis
- product analysis
- product revenue
- item volume
- SKU-level reporting

### `dim_sellers`

Provides seller-level context used for:

- seller analysis
- logistics analysis
- seller geography
- seller/order-item relationships

---

## 4. Fact Tables

| Table | Rows | Grain | Primary Key |
|---|---:|---|---|
| `fact_orders` | 99,441 | One row per order | `order_id` |
| `fact_order_items` | 112,650 | One row per order item | order-item identifier |
| `fact_order_payments` | 103,886 | One row per payment record | payment record key / order context |
| `fact_order_reviews` | 99,224 | One row per review record | review record key / order context |

### `fact_orders`

This is the central order-level fact.

Typical analytical fields include:

```text
order_id
customer_id
order_status
order_purchase_timestamp
order_approved_at
order_delivered_carrier_date
order_delivered_customer_date
order_estimated_delivery_date
```

The table has one row per `order_id`.

### `fact_order_items`

Grain:

```text
1 row = 1 order item
```

It supports:

- items sold
- product revenue
- freight value
- product analysis
- seller analysis

It connects order transactions to:

```text
product_id
seller_id
order_id
```

### `fact_order_payments`

Grain:

```text
1 row = 1 payment record
```

Payment records may be multiple per order. This must be respected when building measures to avoid double counting.

### `fact_order_reviews`

Grain:

```text
1 row = 1 review record
```

Reviews are analyzed independently from order-item grain.

---

## 5. Analytical Marts

### `mart_sales`

Sales-oriented analytical mart used for sales analysis and reconciliation.

### `mart_customers`

Customer-grain mart:

```text
1 row = 1 customer_unique_id
```

Current validated row count:

```text
96,096
```

It supports customer-level metrics such as:

- repeat customer identification
- customer order behavior
- customer value
- customer activity

### `mart_products`

Product-oriented analytical mart used for product analysis and KPI calculations.

### `mart_logistics`

Logistics mart:

```text
1 row = 1 order_id
```

Current validated row count:

```text
99,441
```

Important logistics attributes include:

```text
approval_delay_hours
purchase_to_carrier_days
carrier_to_customer_days
purchase_to_delivery_days
estimated_delivery_variance_days
is_delivered
has_delivery_timestamp
invalid_purchase_carrier_sequence
invalid_carrier_customer_sequence
delivered_missing_customer_date
non_delivered_has_customer_date
is_late_delivery
is_early_delivery
is_on_time_delivery
```

The late-delivery business rule is based on:

```text
estimated_delivery_variance_days > 0
```

where the variance is evaluated at the **date level**.

---

## 6. Power BI Semantic Model

The Power BI model uses the validated analytical layer as its foundation.

The main relationships are:

```text
dim_date
   |
   | 1 : *
   v
fact_orders
   |
   |-- 1 : * -> fact_order_items
   |-- 1 : * -> fact_order_payments
   |-- 1 : * -> fact_order_reviews

fact_order_items
   |-- * : 1 -> dim_products
   |-- * : 1 -> dim_sellers

fact_orders
   |-- 1 : 1 <-> dim_customers
```

### Date relationship

The principal active reporting relationship is:

```text
dim_date[date]
      1
      |
      *
      v
fact_orders[order_purchase_date]
```

`order_purchase_date` is a Date-only field derived from `order_purchase_timestamp`.

The `dim_date` table is marked as the Power BI Date Table.

---

## 7. Relationship Design Principles

### 7.1 Preserve grain

Relationships must respect each table's business grain.

Examples:

```text
fact_orders
1 row = 1 order

fact_order_items
1 row = 1 order item

fact_order_payments
1 row = 1 payment record

fact_order_reviews
1 row = 1 review record
```

These grains must not be treated as interchangeable.

### 7.2 Controlled filter direction

The model uses controlled relationship directions wherever supported by the Power BI relationship design.

Dimension-to-fact filtering is preferred to unrestricted bidirectional propagation.

The `dim_customers` to `fact_orders` relationship is a `1:1` relationship in the current source model, so Power BI requires bidirectional filtering for that relationship.

This is an observed property of the validated source model rather than an arbitrary modeling choice.

### 7.3 Avoid accidental fact multiplication

Payment, review, and order-item tables have grains that can produce multiple records per order.

For example:

```text
1 order
  |-- multiple order items
  |-- multiple payments
  |-- potentially multiple review records
```

A naive flat join could multiply rows and inflate revenue or order counts.

The project therefore preserves separate fact grains.

---

## 8. Customer Identity Model

Customer identity is an important modeling consideration.

The project contains both:

```text
customer_id
customer_unique_id
```

They must not be treated as interchangeable.

### `customer_id`

Used by the order-level source/analytical relationship:

```text
fact_orders[customer_id]
<->
dim_customers[customer_id]
```

### `customer_unique_id`

Used for long-term customer-level identity:

```text
Total Customers
Repeat Customers
Repeat Customer Rate
Customer Analysis
```

This distinction is critical for repeat-purchase analysis.

---

## 9. Date Model and Time Intelligence

The project uses a dedicated Date dimension rather than relying only on transaction timestamps.

The Date dimension provides:

```text
year
quarter
month
year_month
year_month_sort
```

This supports:

- monthly trends
- yearly comparison
- period filtering
- future time-intelligence measures

The report uses:

```text
dim_date[year]
dim_date[year_month]
```

for slicers and chronological visual axes.

`year_month` is sorted using:

```text
year_month_sort
```

to maintain chronological order.

---

## 10. Data Integrity Validation

The semantic model was built only after analytical validation.

Validated checks include:

```text
fact_orders.order_id uniqueness            PASS
fact_orders -> dim_customers                PASS
fact_order_items -> dim_products            PASS
fact_order_items -> dim_sellers             PASS
fact_orders -> mart_sales                   PASS
fact_orders -> mart_logistics               PASS
purchase dates missing from dim_date        0
```

Additional analytical validations included:

- primary-key uniqueness
- null checks
- orphan / foreign-key checks
- date coverage
- fact-to-mart reconciliation
- order-grain validation
- product coverage
- seller coverage

---

## 11. Power BI Measure Layer

The semantic model supports DAX measures including:

```text
Total Orders
Total Items Sold
Product Revenue
Freight Revenue
GMV
Average Order Value
Total Customers
Repeat Customers
Repeat Customer Rate
Canceled Orders
Cancellation Rate
Late Orders
Late Delivery Rate
Average Delivery Days
```

The measures are validated against the Python/Polars KPI layer.

Important logistics reconciliation:

```text
Late Orders             = 6,535
Late Delivery Rate      = 6.77%
Average Delivery Days   = 12.56
```

The Power BI implementation was corrected to match the analytical date-level business rules.

---

## 12. Reporting Scope

The underlying model retains the full available analytical date range:

```text
2016-09-04 -> 2018-11-12
```

The default dashboard presentation focuses on:

```text
2017-2018
```

because 2016 has limited transaction activity, including one month with no transactions.

Important:

```text
2016 is NOT deleted.
```

It remains available in the model and can still be selected from the Year slicer.

---

## 13. Modeling Principles

The project follows these principles:

1. Preserve source analytical grain.
2. Separate dimensions from facts.
3. Avoid unnecessary flat-table joins.
4. Prevent double counting.
5. Use a dedicated Date dimension.
6. Make business definitions explicit.
7. Reconcile Power BI measures against the analytical pipeline.
8. Separate descriptive insight from unsupported causal claims.
9. Preserve anomalous source evidence rather than silently overwriting it.

---

## 14. Semantic Model as Portfolio Evidence

The Power BI semantic model is part of the project evidence that the workflow covers more than visualization.

It demonstrates:

```text
Data preparation
      v
Analytical modeling
      v
Data validation
      v
Semantic modeling
      v
DAX
      v
Dashboard
      v
Business interpretation
```

This makes the project suitable for presentation as an end-to-end Data Analyst portfolio case study.
