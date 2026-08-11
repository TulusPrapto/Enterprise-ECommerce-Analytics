# Business Data Quality Specification

## 1. Purpose

This specification defines the business-level data quality rules for the Enterprise E-Commerce Analytics project.

The objective is to determine whether the cleaned datasets are sufficiently valid, consistent, complete, and logically coherent for downstream business analysis, KPI calculation, analytical datasets, and dashboards.

This layer is intentionally separated from technical data cleaning.

Technical cleaning verifies that datasets satisfy structural and technical requirements such as:

* Required columns exist
* Primary keys are valid
* Rows are preserved
* Text values are standardized
* Basic dataset structure is valid

Business Data Quality verifies whether the data makes sense from an analytical and business perspective.

---

## 2. Scope

The Business Data Quality layer covers the following datasets:

1. `olist_customers_dataset.csv`
2. `olist_orders_dataset.csv`
3. `olist_order_items_dataset.csv`
4. `olist_order_payments_dataset.csv`
5. `olist_order_reviews_dataset.csv`
6. `olist_products_dataset.csv`
7. `olist_sellers_dataset.csv`
8. `olist_geolocation_dataset.csv`
9. `product_category_name_translation.csv`

The primary focus is on rules that affect business analysis.

---

## 3. Quality Dimensions

Business Data Quality will be evaluated across the following dimensions:

### 3.1 Validity

Values must fall within acceptable business ranges or permitted categories.

Examples:

* `review_score` must be between 1 and 5.
* `price` must not be negative.
* `freight_value` must not be negative.
* Payment values must not be negative.

### 3.2 Completeness

Required business information should be present when it is expected to exist.

Examples:

* Delivered orders should normally contain order items.
* Delivered orders should normally contain payment records.
* Required timestamps should exist for the relevant order lifecycle stage.

Exceptions identified during relationship analysis must be explicitly considered rather than automatically treated as errors.

### 3.3 Consistency

Related values and datasets should agree with one another.

Examples:

* Orders referenced by order items must exist in the orders dataset.
* Products referenced by order items must exist in the products dataset.
* Sellers referenced by order items must exist in the sellers dataset.

### 3.4 Temporal Consistency

Business timestamps must follow a logically valid sequence.

Expected order lifecycle:

`purchase → approval → shipping → delivery`

Rules must identify impossible timestamp sequences.

### 3.5 Financial Consistency

Financial measures must be internally coherent.

Examples:

* Item price must not be negative.
* Freight value must not be negative.
* Payment values must not be negative.
* Aggregated payment and order-item values should be investigated when materially inconsistent.

### 3.6 Analytical Usability

Data quality issues must be assessed according to their potential impact on business analysis.

Not every anomaly should result in a dataset failure.

---

## 4. Severity Classification

Each business-quality rule must have a severity.

### CRITICAL

An issue that can materially invalidate a major business metric or analytical conclusion.

Examples:

* Impossible order lifecycle timestamps affecting delivery analysis.
* Broken transaction relationships affecting revenue calculation.

### HIGH

An issue that can materially affect a specific analysis or KPI.

Examples:

* Delivered orders without expected transaction components.
* Material payment inconsistencies.

### MEDIUM

An issue that affects analytical completeness or segmentation but does not invalidate the entire dataset.

Examples:

* Missing geographic enrichment.
* Missing category translation.

### LOW

An issue with limited analytical impact.

Examples:

* Minor enrichment gaps that do not affect core transaction metrics.

---

# 5. Business Quality Rules

## BQ-001 — Review Score Validity

**Dataset:** `olist_order_reviews_dataset.csv`

`review_score` must contain values from 1 through 5.

**Severity:** HIGH

**Failure condition:**

```text
review_score < 1 OR review_score > 5
```

**Business impact:**

Invalid review scores can distort customer satisfaction, product quality, and seller performance analysis.

---

## BQ-002 — Product Price Validity

**Dataset:** `olist_order_items_dataset.csv`

`price` must not be negative.

**Severity:** HIGH

**Failure condition:**

```text
price < 0
```

**Business impact:**

Invalid prices can directly distort revenue, product performance, category revenue, and seller revenue calculations.

---

## BQ-003 — Freight Value Validity

**Dataset:** `olist_order_items_dataset.csv`

`freight_value` must not be negative.

**Severity:** MEDIUM

**Failure condition:**

```text
freight_value < 0
```

**Business impact:**

Invalid freight values can distort logistics-cost and order-value analysis.

---

## BQ-004 — Payment Value Validity

**Dataset:** `olist_order_payments_dataset.csv`

`payment_value` must not be negative.

**Severity:** HIGH

**Failure condition:**

```text
payment_value < 0
```

**Business impact:**

Invalid payment values can distort revenue and payment-method analysis.

---

## BQ-005 — Order Item Reference Integrity

**Datasets:**

* `olist_orders_dataset.csv`
* `olist_order_items_dataset.csv`

Every order referenced by an order item must exist in the orders dataset.

**Severity:** CRITICAL

**Failure condition:**

An `order_id` exists in order items but does not exist in orders.

**Business impact:**

Broken order-item relationships can produce incorrect revenue, order volume, product, and seller analysis.

---

## BQ-006 — Payment Reference Integrity

**Datasets:**

* `olist_orders_dataset.csv`
* `olist_order_payments_dataset.csv`

Every payment record should reference an existing order.

**Severity:** CRITICAL

**Failure condition:**

A payment record references an unknown `order_id`.

**Business impact:**

Unmatched payments can cause incorrect financial aggregation.

---

## BQ-007 — Product Reference Integrity

**Datasets:**

* `olist_products_dataset.csv`
* `olist_order_items_dataset.csv`

Every product referenced by order items should exist in the products dataset.

**Severity:** CRITICAL

**Failure condition:**

An order item references a product that does not exist in the product master.

**Business impact:**

Can invalidate product and category-level sales analysis.

---

## BQ-008 — Seller Reference Integrity

**Datasets:**

* `olist_sellers_dataset.csv`
* `olist_order_items_dataset.csv`

Every seller referenced by an order item should exist in the seller dataset.

**Severity:** CRITICAL

**Failure condition:**

An order item references an unknown seller.

**Business impact:**

Can invalidate seller performance and seller revenue analysis.

---

## BQ-009 — Delivered Order Without Items

**Dataset relationship:**

`orders → order_items`

Delivered orders should normally have at least one order item.

**Severity:** HIGH

**Failure condition:**

```text
order_status = delivered
AND order has zero order_items
```

**Important exception:**

The relationship analysis identified 775 orders without items overall, but most were:

* unavailable: 603
* canceled: 164
* created: 5
* invoiced: 2
* shipped: 1

Therefore, the rule must focus specifically on delivered orders rather than treating every order without items as a business-quality failure.

---

## BQ-010 — Delivered Order Without Payment

**Dataset relationship:**

`orders → payments`

Delivered orders should normally have at least one payment record.

**Severity:** CRITICAL

**Failure condition:**

```text
order_status = delivered
AND order has zero payment records
```

**Known finding from relationship analysis:**

There is 1 order without a payment record, and it is classified as `delivered`.

This case must be explicitly reported by the Business Data Quality pipeline.

---

## BQ-011 — Delivered Order Without Review

**Dataset relationship:**

`orders → reviews`

A delivered order may or may not have a review.

**Severity:** LOW

**Failure condition:**

None by default.

**Reason:**

The relationship analysis identified 768 orders without reviews, including 646 delivered orders.

A missing review should therefore not automatically be treated as a data-quality failure because reviewing a purchase is not necessarily mandatory.

The rule should instead report:

* delivered orders without reviews
* percentage of delivered orders without reviews

as an analytical completeness indicator.

---

## BQ-012 — Order Lifecycle Timestamp Consistency

**Dataset:** `olist_orders_dataset.csv`

Order timestamps must follow a logical sequence.

Expected sequence:

```text
order_purchase_timestamp
        ↓
order_approved_at
        ↓
order_delivered_carrier_date
        ↓
order_delivered_customer_date
```

**Severity:** HIGH

**Failure conditions include:**

```text
approval < purchase
carrier delivery < purchase
customer delivery < purchase
customer delivery < carrier delivery
```

Only comparisons involving non-null timestamps should be evaluated.

---

## BQ-013 — Delivery Timestamp and Order Status Consistency

**Dataset:** `olist_orders_dataset.csv`

Order status should be reasonably consistent with available lifecycle timestamps.

Examples:

* `delivered` should normally have customer delivery information.
* Orders that have not reached delivery should not contain implausible customer-delivery timestamps.

**Severity:** HIGH

The exact status-to-timestamp matrix must be implemented explicitly in the validation layer.

---

## BQ-014 — Payment Multiplicity

**Dataset:** `olist_order_payments_dataset.csv`

Multiple payment records for a single order are valid and must not automatically be treated as duplicates.

**Severity:** INFORMATIONAL

The relationship analysis identified:

```text
Orders with multiple payment records: 2,961
Maximum payment records per order: 29
```

These records must be preserved because multiple payment installments or payment components can legitimately belong to one order.

---

## BQ-015 — Order Item Multiplicity

**Dataset:** `olist_order_items_dataset.csv`

Multiple order-item records for a single order are expected.

**Severity:** INFORMATIONAL

The relationship analysis identified:

```text
Orders with multiple items: 9,803
Maximum items per order: 21
```

Multiple items must not be interpreted as duplicate transactions.

---

## BQ-016 — Review Multiplicity

**Dataset:** `olist_order_reviews_dataset.csv`

Multiple reviews associated with an order are possible in the source data and must be investigated rather than automatically removed.

**Severity:** MEDIUM

The relationship analysis identified:

```text
Orders with multiple reviews: 547
Maximum reviews per order: 3
```

The composite key:

```text
(review_id, order_id)
```

is used as the technical uniqueness contract.

---

## BQ-017 — Product Category Translation Completeness

**Datasets:**

* `olist_products_dataset.csv`
* `product_category_name_translation.csv`

Untranslated product categories should be reported.

**Severity:** MEDIUM

Known unmatched categories:

```text
pc_gamer
portateis_cozinha_e_preparadores_de_alimentos
```

Affected products:

```text
pc_gamer                                      3
portateis_cozinha_e_preparadores_de_alimentos 10
```

These categories should not be deleted merely because an English translation is unavailable.

---

## BQ-018 — Customer Geographic Enrichment

**Datasets:**

* `olist_customers_dataset.csv`
* `olist_geolocation_dataset.csv`

Unmatched customer ZIP prefixes should be reported.

**Severity:** MEDIUM

Known relationship analysis finding:

```text
Unmatched customer ZIP prefixes: 157
Affected customer rows: 278
```

Missing geographic enrichment must not cause customer transaction records to be deleted.

---

## BQ-019 — Seller Geographic Enrichment

**Datasets:**

* `olist_sellers_dataset.csv`
* `olist_geolocation_dataset.csv`

Unmatched seller ZIP prefixes should be reported.

**Severity:** MEDIUM

Known finding:

```text
Unmatched seller ZIP prefixes: 7
Affected seller rows: 7
```

Missing seller geographic enrichment must not cause seller or order-item records to be deleted.

---

# 6. Rule Execution Policy

Business-quality rules are divided into three outcomes:

### FAIL

The condition represents a genuine business-quality violation.

Example:

```text
Delivered order without payment
```

### WARN

The condition represents an analytical limitation or enrichment gap but does not necessarily invalidate the underlying transaction.

Example:

```text
Customer ZIP prefix has no geographic match
```

### INFO

The condition is expected behavior and should be documented rather than treated as a defect.

Example:

```text
Order contains multiple payment records
```

---

# 7. Business Data Quality Report

The pipeline must produce a machine-readable report containing:

* Rule ID
* Dataset
* Dimension
* Severity
* Status
* Affected row count
* Affected percentage
* Description
* Business impact
* Sample records where appropriate

Recommended output:

```text
reports/quality/
└── business_quality_report.json
```

---

# 8. Overall Quality Status

The overall Business Data Quality status should be determined using the following logic:

```text
CRITICAL failure
        ↓
Overall status = FAIL

No CRITICAL failure
but HIGH violations exist
        ↓
Overall status = WARNING

Only MEDIUM / LOW / INFO findings
        ↓
Overall status = PASS WITH WARNINGS
```

The pipeline must preserve individual rule results even when the overall status is FAIL or WARNING.

---

# 9. Design Principle

Business Data Quality must not silently modify source or processed data.

Its responsibility is to:

1. Detect business-quality issues.
2. Quantify affected records.
3. Classify severity.
4. Explain business impact.
5. Produce an auditable report.

Data remediation decisions must be made explicitly in a later analytical or transformation stage.

---

# 10. Next Implementation Stage

After this specification is reviewed and approved, implementation should proceed with:

```text
src/quality/
├── __init__.py
├── config.py
├── rules.py
├── validators.py
└── pipeline.py
```

The implementation must consume the cleaned datasets from:

```text
data/processed/
```

and produce:

```text
reports/quality/business_quality_report.json
```

The Business Data Quality layer must not alter the cleaned datasets.



# ========================================================================
# ===========    Versi Lain dari Business Data Quality Spec ==============
# ========================================================================
# Business Data Quality Specification

## 1. Purpose

This document defines business-level data quality rules for the Olist
e-commerce dataset.

The objective is to ensure that the cleaned datasets are not only
structurally valid, but also logically consistent with expected
e-commerce business behavior.

Business Data Quality validation is performed after structural cleaning
and relationship validation.

---

## 2. Validation Principles

Business Data Quality validation focuses on:

1. Order lifecycle consistency
2. Financial consistency
3. Product and order-item consistency
4. Payment consistency
5. Review consistency
6. Delivery-date consistency
7. Customer and seller consistency
8. Business-rule plausibility

A business rule failure does not automatically mean that the source
data is incorrect. Some rules identify legitimate business exceptions
that require investigation.

---

## 3. Severity Levels

### FAIL

A critical business rule is violated and the affected records should
not be used blindly for downstream analytics.

### WARNING

A business rule identifies an unusual or potentially problematic
condition, but the records may still be valid.

### INFO

The condition is informative and does not represent a data-quality
failure.

---

# 4. Dataset-Level Business Rules

## 4.1 Orders

Dataset:

`olist_orders_dataset.csv`

### Rule ORD-001 — Delivered orders should have delivery date

Condition:

If:

`order_status = delivered`

then:

`order_delivered_customer_date IS NOT NULL`

Severity:

WARNING

Reason:

A delivered order without a customer delivery date may indicate
incomplete operational data.

---

### Rule ORD-002 — Delivered orders should have estimated delivery date

Condition:

If:

`order_status = delivered`

then:

`order_estimated_delivery_date IS NOT NULL`

Severity:

WARNING

---

### Rule ORD-003 — Delivered date should not precede purchase date

Condition:

`order_delivered_customer_date >= order_purchase_timestamp`

Severity:

FAIL

---

### Rule ORD-004 — Approved date should not precede purchase date

Condition:

`order_approved_at >= order_purchase_timestamp`

Severity:

WARNING

Null approved dates are allowed because some orders may never reach
the approval stage.

---

### Rule ORD-005 — Delivery date should not precede shipping date

Condition:

`order_delivered_customer_date >= order_delivered_carrier_date`

Severity:

WARNING

Only evaluate records where both dates are available.

---

# 5. Order Item Rules

Dataset:

`olist_order_items_dataset.csv`

### Rule ITEM-001 — Price must be non-negative

Condition:

`price >= 0`

Severity:

FAIL

---

### Rule ITEM-002 — Freight value must be non-negative

Condition:

`freight_value >= 0`

Severity:

FAIL

---

### Rule ITEM-003 — Order item quantity must be positive

The dataset does not contain an explicit quantity field.

Therefore this rule is NOT applicable.

---

# 6. Payment Rules

Dataset:

`olist_order_payments_dataset.csv`

### Rule PAY-001 — Payment value must be positive

Condition:

`payment_value > 0`

Severity:

WARNING

Zero-value payments may represent exceptional business situations.

---

### Rule PAY-002 — Payment sequential must be positive

Condition:

`payment_sequential >= 1`

Severity:

FAIL

---

### Rule PAY-003 — Payment installments must be positive

Condition:

`payment_installments >= 1`

Severity:

FAIL

---

# 7. Review Rules

Dataset:

`olist_order_reviews_dataset.csv`

### Rule REV-001 — Review score must be between 1 and 5

Condition:

`1 <= review_score <= 5`

Severity:

FAIL

---

### Rule REV-002 — Review creation date should not precede order purchase date

This rule requires joining reviews with orders.

Condition:

`review_creation_date >= order_purchase_timestamp`

Severity:

WARNING

Only evaluate records where both dates are available.

---

# 8. Product Rules

Dataset:

`olist_products_dataset.csv`

### Rule PROD-001 — Product weight must be positive

Condition:

`product_weight_g > 0`

Severity:

WARNING

Null values are allowed.

---

### Rule PROD-002 — Product dimensions must be positive

Applicable columns:

- product_length_cm
- product_height_cm
- product_width_cm

Condition:

Each non-null dimension must be greater than zero.

Severity:

WARNING

---

# 9. Seller Rules

Dataset:

`olist_sellers_dataset.csv`

### Rule SELL-001 — Seller ZIP code must be valid

Condition:

`seller_zip_code_prefix` must be within the Brazilian ZIP-code
numeric range represented by the dataset.

Severity:

WARNING

---

# 10. Customer Rules

Dataset:

`olist_customers_dataset.csv`

### Rule CUST-001 — Customer ZIP code must be numeric

Condition:

`customer_zip_code_prefix` must contain a valid numeric ZIP prefix.

Severity:

WARNING

---

# 11. Cross-Dataset Financial Rules

## Rule FIN-001 — Order payment total should be non-negative

Aggregate:

`SUM(payment_value)` by `order_id`

Condition:

Total payment value must be >= 0.

Severity:

FAIL

---

## Rule FIN-002 — Order item merchandise value should be non-negative

Aggregate:

`SUM(price)` by `order_id`

Condition:

Total item price must be >= 0.

Severity:

FAIL

---

# 12. Cross-Dataset Order Rules

## Rule REL-001 — Order items must reference existing orders

Foreign key:

`order_items.order_id -> orders.order_id`

Severity:

FAIL

This rule is expected to pass based on relationship validation.

---

## Rule REL-002 — Payments must reference existing orders

Foreign key:

`payments.order_id -> orders.order_id`

Severity:

FAIL

---

## Rule REL-003 — Reviews must reference existing orders

Foreign key:

`reviews.order_id -> orders.order_id`

Severity:

FAIL

---

## Rule REL-004 — Order items must reference existing products

Foreign key:

`order_items.product_id -> products.product_id`

Severity:

FAIL

---

## Rule REL-005 — Order items must reference existing sellers

Foreign key:

`order_items.seller_id -> sellers.seller_id`

Severity:

FAIL

---

# 13. Expected Exceptions

The following conditions have already been observed during relationship
analysis and should not automatically be treated as cleaning failures:

### Orders without order items

Observed:

775 orders.

Most are associated with:

- unavailable
- canceled
- created
- invoiced
- shipped

These records require business interpretation rather than automatic
deletion.

---

### Orders without reviews

Observed:

768 orders.

The absence of a review is not necessarily a data-quality problem.

Reviews are optional customer behavior.

Severity:

INFO

---

### Orders with multiple payments

Observed:

2,961 orders.

Multiple payment records are valid because the payment dataset supports
multiple payment records per order.

Severity:

INFO

---

### Orders with multiple order items

Observed:

9,803 orders.

Multiple order items per order are expected e-commerce behavior.

Severity:

INFO

---

### Duplicate review_id

The source dataset contains repeated `review_id` values associated with
different orders.

The validated business key is:

`(review_id, order_id)`

Therefore `review_id` alone must not be treated as a unique primary key.

---

# 14. Business Data Quality Output

The validator should produce:

`reports/business_quality/business_data_quality_report.json`

The report should contain:

- execution timestamp
- dataset
- rule ID
- rule description
- severity
- evaluated row count
- affected row count
- pass/fail status
- sample affected records where applicable

---

# 15. Quality Status

Overall business data quality status should follow:

### PASS

No FAIL rules are violated.

### WARNING

No FAIL rules are violated, but one or more WARNING rules are violated.

### FAIL

At least one FAIL rule is violated.

---

# 16. Important Principle

Business Data Quality validation must not silently modify source or
processed datasets.

The validator is diagnostic.

Cleaning and business-quality validation are separate stages.

The business-quality validator must produce evidence that can be reviewed
before any additional transformation is performed.