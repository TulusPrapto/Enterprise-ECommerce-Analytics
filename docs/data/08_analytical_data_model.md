# Analytical Data Model Specification

## 1. Purpose

This document defines the analytical data model for the Enterprise E-Commerce Analytics project.

The objective is to establish a stable analytical foundation between the cleaned/quality-controlled datasets and downstream business analysis.

The model must:

* preserve the original business grain of each source dataset;
* prevent accidental double-counting;
* define primary and foreign keys explicitly;
* separate transactional facts from descriptive dimensions;
* establish reusable business metrics;
* provide a consistent foundation for SQL, Python, Excel, Power BI, and future analytical automation.

This document is a design contract. Analytical-layer implementation must follow the grain, relationship, and metric definitions specified here.

---

# 2. Source Dataset Inventory

The analytical layer is based on the following cleaned datasets.

| Dataset                            | Business Domain | Intended Grain                 |
| ---------------------------------- | --------------- | ------------------------------ |
| `olist_orders_dataset.csv`         | Orders          | One row per order              |
| `olist_order_items_dataset.csv`    | Order Items     | One row per order item         |
| `olist_order_payments_dataset.csv` | Payments        | One row per payment record     |
| `olist_order_reviews_dataset.csv`  | Reviews         | One row per review             |
| `olist_products_dataset.csv`       | Products        | One row per product            |
| `olist_sellers_dataset.csv`        | Sellers         | One row per seller             |
| `olist_customers_dataset.csv`      | Customers       | One row per customer           |
| `olist_geolocation_dataset.csv`    | Geography       | One row per geolocation record |

The analytical model must not assume that all datasets share the same grain.

---

# 3. Core Analytical Principle

The most important modeling principle is:

> Never join multiple one-to-many transactional tables together before defining the intended analytical grain.

For example:

```text
1 order
 â”œâ”€â”€ many order items
 â””â”€â”€ many payment records
```

A direct join between orders, order items, and payments can multiply rows.

Therefore:

```text
orders Ã— order_items Ã— payments
```

must not be used directly to calculate revenue, order count, or payment totals.

Metrics must first be calculated at their native grain and then aggregated or joined at a controlled grain.

---

# 4. Entity Relationship Overview

The conceptual model is:

```text
                         dim_customer
                              â”‚
                              â”‚ customer_id
                              â–¼
                         fact_order
                         â”‚    â”‚
             order_id â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                 â”‚                            â”‚
                 â”‚                            â”‚
                 â–¼                            â–¼
          fact_order_item                fact_payment
                 â”‚
          â”Œâ”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”
          â”‚             â”‚
          â–¼             â–¼
     dim_product    dim_seller


fact_order
    â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–º fact_review

dim_product
    â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–º product attributes

dim_customer
    â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–º customer attributes
```

The analytical model uses separate fact tables for different transactional grains.

---

# 5. Fact Tables

## 5.1 `fact_order`

### Grain

One row represents exactly one customer order.

### Business key

`order_id`

### Source

`olist_orders_dataset.csv`

### Core attributes

* `order_id`
* `customer_id`
* `order_status`
* `order_purchase_timestamp`
* `order_approved_at`
* `order_delivered_carrier_date`
* `order_delivered_customer_date`
* `order_estimated_delivery_date`

### Derived analytical attributes

The analytical layer may derive:

* purchase date;
* purchase year;
* purchase month;
* purchase week;
* purchase day;
* purchase weekday;
* delivery duration;
* estimated delivery duration;
* delivery delay;
* delivery status category.

### Important rule

`fact_order` must remain at one row per order.

No order-item or payment-level columns should be physically joined into this table unless they have first been aggregated to one row per order.

---

# 6. `fact_order_item`

### Grain

One row represents one product item within one order.

### Source

`olist_order_items_dataset.csv`

### Business key

Composite key:

```text
order_id + order_item_id
```

### Core attributes

* `order_id`
* `order_item_id`
* `product_id`
* `seller_id`
* `shipping_limit_date`
* `price`
* `freight_value`

### Derived metrics

At item grain:

* item revenue;
* freight value;
* item total value.

The preferred item-level sales value is:

```text
item_total_value = price + freight_value
```

### Important rule

Revenue calculated from `fact_order_item` must not be joined directly to payment-level records.

---

# 7. `fact_payment`

### Grain

One row represents one payment record for an order.

### Source

`olist_order_payments_dataset.csv`

### Business key

Composite key:

```text
order_id + payment_sequential
```

### Core attributes

* `order_id`
* `payment_sequential`
* `payment_type`
* `payment_installments`
* `payment_value`

### Important rule

Payment value represents payment-record-level information.

Payment totals must be aggregated to order grain before being joined to `fact_order`.

Example:

```text
fact_payment
     â†“
GROUP BY order_id
     â†“
order_payment_summary
```

Only then may the result be joined to `fact_order`.

---

# 8. `fact_review`

### Grain

One row represents one review record.

### Source

`olist_order_reviews_dataset.csv`

### Business key

`review_id`

### Core attributes

* `review_id`
* `order_id`
* `review_score`
* `review_comment_title`
* `review_comment_message`
* `review_creation_date`
* `review_answer_timestamp`

### Derived analytical attributes

Possible derived fields:

* review score category;
* positive/neutral/negative classification;
* review response duration.

### Important rule

Review metrics must not be treated as order metrics without defining how multiple reviews for an order are handled.

---

# 9. Dimensions

## 9.1 `dim_customer`

### Grain

One row represents one customer.

### Business key

`customer_id`

### Source

`olist_customers_dataset.csv`

### Attributes

* `customer_id`
* `customer_unique_id`
* `customer_zip_code_prefix`
* `customer_city`
* `customer_state`

### Analytical role

Used for:

* customer segmentation;
* geographic analysis;
* customer order frequency;
* repeat customer analysis;
* customer lifetime analysis.

### Important distinction

`customer_id` and `customer_unique_id` must not be treated as interchangeable.

The analytical model must explicitly define which identifier is used for:

* order-level operational relationships;
* customer-level behavioral analysis.

---

# 10. `dim_product`

### Grain

One row represents one product.

### Business key

`product_id`

### Source

`olist_products_dataset.csv`

### Attributes

* `product_id`
* `product_category_name`
* `product_name_length`
* `product_description_length`
* `product_photos_qty`
* `product_weight_g`
* `product_length_cm`
* `product_height_cm`
* `product_width_cm`

### Analytical role

Used for:

* product performance;
* category performance;
* product-level revenue;
* product volume;
* logistics analysis.

---

# 11. `dim_seller`

### Grain

One row represents one seller.

### Business key

`seller_id`

### Source

`olist_sellers_dataset.csv`

### Attributes

* `seller_id`
* `seller_zip_code_prefix`
* `seller_city`
* `seller_state`

### Analytical role

Used for:

* seller performance;
* seller revenue;
* seller order volume;
* seller freight analysis;
* seller geographic analysis.

---

# 12. `dim_date`

A reusable date dimension should be created by the analytical layer.

### Grain

One row represents one calendar date.

### Suggested attributes

* `date`
* `year`
* `quarter`
* `month`
* `month_name`
* `week`
* `day`
* `day_name`
* `is_weekend`

### Analytical role

Used for consistent time-series analysis.

---

# 13. Relationship Rules

The primary relationships are:

```text
dim_customer.customer_id
        â”‚
        â””â”€â”€< fact_order.customer_id
```

```text
fact_order.order_id
        â”‚
        â”œâ”€â”€< fact_order_item.order_id
        â”‚
        â”œâ”€â”€< fact_payment.order_id
        â”‚
        â””â”€â”€< fact_review.order_id
```

```text
dim_product.product_id
        â”‚
        â””â”€â”€< fact_order_item.product_id
```

```text
dim_seller.seller_id
        â”‚
        â””â”€â”€< fact_order_item.seller_id
```

The symbol:

```text
<
```

indicates a one-to-many relationship.

---

# 14. Grain Compatibility Rules

The following rules are mandatory.

## Rule 1 â€” Order grain

Order-level metrics must use `fact_order`.

Examples:

* order count;
* cancellation rate;
* delivery performance;
* average order processing time.

---

## Rule 2 â€” Item grain

Product and seller sales metrics must use `fact_order_item`.

Examples:

* product revenue;
* category revenue;
* seller revenue;
* freight value;
* units sold.

---

## Rule 3 â€” Payment grain

Payment metrics must use `fact_payment`.

Examples:

* total payment value;
* payment method mix;
* installment distribution.

---

## Rule 4 â€” Review grain

Review metrics must use `fact_review`.

Examples:

* average review score;
* review volume;
* review sentiment classification.

---

## Rule 5 â€” No uncontrolled fan-out

The following pattern is prohibited:

```text
fact_order
   JOIN fact_order_item
   JOIN fact_payment
   JOIN fact_review
```

unless every many-side table has first been aggregated to the target grain.

---

# 15. Anti-Double-Counting Strategy

## Example

Suppose:

```text
Order A
    2 order items
    2 payment records
```

A direct join can produce:

```text
2 Ã— 2 = 4 rows
```

This means an order-level metric can accidentally be multiplied.

Therefore:

### Correct pattern

```text
fact_order_item
      â†“
aggregate by order_id
      â†“
order_item_summary
```

and:

```text
fact_payment
      â†“
aggregate by order_id
      â†“
order_payment_summary
```

Then:

```text
fact_order
   â”‚
   â”œâ”€â”€ order_item_summary
   â”‚
   â””â”€â”€ order_payment_summary
```

This produces controlled one-to-one joins at order grain.

---

# 16. Revenue Definition

Revenue must be explicitly defined.

For product sales analysis:

```text
gross_item_sales = SUM(price)
```

For logistics-inclusive sales value:

```text
order_item_value = SUM(price + freight_value)
```

The analytical layer must preserve both concepts rather than silently treating them as the same metric.

### Recommended naming

```text
gross_product_sales
freight_value
gross_order_item_value
```

This prevents ambiguity in downstream analysis.

---

# 17. Order Count Definition

The canonical order count is:

```text
COUNT(DISTINCT order_id)
```

It must not be calculated by counting rows after joining to `fact_order_item`.

For example:

```text
COUNT(order_item_rows)
```

is not equivalent to order count.

---

# 18. Customer Count Definition

Operational customer count may use:

```text
COUNT(DISTINCT customer_id)
```

Behavioral customer analysis should use:

```text
COUNT(DISTINCT customer_unique_id)
```

The selected identifier must always be documented in the metric definition.

---

# 19. Repeat Customer Definition

A repeat customer is defined as a customer with more than one order.

Conceptually:

```text
customer_order_count > 1
```

The customer identifier used for repeat-customer analysis must be:

```text
customer_unique_id
```

unless a specific analysis explicitly requires the operational `customer_id`.

---

# 20. Delivery Metrics

Delivery metrics belong primarily to `fact_order`.

Potential metrics include:

### Delivery duration

```text
order_delivered_customer_date
-
order_purchase_timestamp
```

### Carrier duration

```text
order_delivered_carrier_date
-
order_purchase_timestamp
```

### Customer delivery delay

```text
order_delivered_customer_date
-
order_estimated_delivery_date
```

The analytical layer must preserve null values rather than automatically imputing missing historical dates.

---

# 21. Data Quality Interaction

The analytical layer must respect the Business Data Quality Framework.

Current quality status:

```text
Rules evaluated: 18
Rules passed: 13
Rules failed: 5
Quality score: 87.04
Grade: B
Status: REVIEW
```

Known exceptions include:

```text
ORD-001
ORD-005
PAY-001
PAY-003
PROD-001
```

The analytical layer must not silently "fix" these records.

The current business decisions specify that affected records should generally be retained and flagged rather than overwritten.

---

# 22. Quality-Aware Analytical Principle

A record can be:

```text
analytically usable
```

while simultaneously being:

```text
quality-flagged
```

Therefore analytical datasets should support quality metadata where appropriate.

Suggested fields:

```text
quality_flag
quality_rule_id
```

These fields should only be added when they do not change the underlying business grain.

---

# 23. Metric Layer Principles

Every reusable metric must define:

1. metric name;
2. business definition;
3. source fact;
4. grain;
5. aggregation method;
6. filters;
7. exclusions;
8. quality considerations.

Example:

```text
Metric:
Gross Product Sales

Definition:
Sum of item price across order-item records.

Source:
fact_order_item

Grain:
Order item

Aggregation:
SUM(price)

Quality consideration:
Do not join payment records before aggregation.
```

---

# 24. Initial KPI Catalog

The initial analytical layer should support at least the following KPIs.

## Sales

* Gross Product Sales
* Freight Value
* Gross Order Item Value
* Orders
* Units Sold
* Average Order Value

## Customers

* Unique Customers
* Orders per Customer
* Repeat Customers
* Repeat Customer Rate

## Products

* Product Revenue
* Units Sold by Product
* Category Revenue
* Category Units Sold

## Sellers

* Seller Revenue
* Seller Orders
* Seller Freight Value
* Average Seller Order Value

## Payments

* Payment Value
* Payment Count
* Payment Method Mix
* Average Payment Value
* Installment Distribution

## Reviews

* Review Count
* Average Review Score
* Review Score Distribution

## Delivery

* Average Delivery Duration
* Median Delivery Duration
* Late Delivery Rate
* Carrier Processing Duration

---

# 25. Future Analytical Marts

The following marts may be created after the core analytical layer is stable:

```text
mart_sales_daily
mart_product_performance
mart_customer_behavior
mart_seller_performance
mart_payment_analysis
mart_delivery_performance
mart_review_analysis
```

These marts should be derived from the core facts and dimensions rather than directly from raw datasets.

---

# 26. Implementation Sequence

The implementation must follow this sequence:

```text
1. Validate source datasets
        â†“
2. Build dimensions
        â†“
3. Build fact tables
        â†“
4. Validate analytical grain
        â†“
5. Build reusable metrics
        â†“
6. Validate metric calculations
        â†“
7. Build analytical marts
        â†“
8. Perform business analysis
        â†“
9. Build dashboards
```

---

# 27. Acceptance Criteria

The analytical data model is considered ready for implementation when:

* every fact has an explicitly defined grain;
* every dimension has an explicitly defined grain;
* primary/business keys are documented;
* major relationships are documented;
* revenue definitions are explicit;
* order-count definitions are explicit;
* customer-count definitions are explicit;
* repeat-customer definition is explicit;
* payment aggregation rules are explicit;
* review aggregation rules are explicit;
* delivery metric definitions are explicit;
* double-counting risks are documented;
* quality exceptions are acknowledged;
* no analytical metric relies on uncontrolled many-to-many joins.

---

# 28. Design Decision

The Enterprise E-Commerce Analytics project will use a **multi-fact analytical model** rather than forcing all transactions into a single wide table.

The primary reason is preservation of business grain and prevention of metric distortion.

The analytical architecture therefore follows:

```text
                     DIMENSIONS
                         â”‚
          â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
          â”‚              â”‚              â”‚
          â–¼              â–¼              â–¼
     FACT_ORDER   FACT_ORDER_ITEM   FACT_PAYMENT
          â”‚              â”‚              â”‚
          â”‚              â”‚              â”‚
          â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                         â”‚
                    METRIC LAYER
                         â”‚
                         â–¼
                  ANALYTICAL MARTS
                         â”‚
                         â–¼
                 BUSINESS ANALYSIS
                         â”‚
                         â–¼
                     DASHBOARD
```

This specification is the contract for the next implementation phase.
