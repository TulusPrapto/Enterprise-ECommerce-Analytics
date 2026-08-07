# Relationship Analysis

## Document Metadata

| Field | Value |
|---|---|
| Project | Enterprise E-Commerce Analytics |
| Analysis Phase | Sprint 2.3 — Relationship Analysis |
| Document Owner | Tulus Prapto |
| Dataset | Brazilian E-Commerce Public Dataset by Olist |
| Analysis Tool | Python + Polars |
| Evidence | relationship_profile.json, relationship_deep_validation.json |
| Status | Final |

---

## 1. Objective

The objective of this analysis is to identify and validate relationships between
the source datasets, determine cardinality, assess referential integrity,
identify orphan records and missing child records, and detect potential
analytical join risks.

---

## 2. Relationship Map

customers
    |
    | 1:1
    v
orders
    |
    +---- 1:N ----> order_items
    |
    +---- 1:N ----> payments
    |
    +---- 1:N ----> reviews

products
    |
    | 1:N
    v
order_items

sellers
    |
    | 1:N
    v
order_items

category_translation
    |
    | 1:N
    v
products

geolocation
    |
    +---- ZIP ----> customers
    |
    +---- ZIP ----> sellers

---

## 3. Relationship Validation Results

All primary transactional relationships were validated for referential
integrity.

| Relationship | Orphan Child | Parent Without Child | RI |
|---|---:|---:|---|
| customers → orders | 0 | 0 | True |
| orders → order_items | 0 | 775 | True |
| orders → payments | 0 | 1 | True |
| orders → reviews | 0 | 768 | True |
| products → order_items | 0 | 0 | True |
| sellers → order_items | 0 | 0 | True |

Reference-data relationships have incomplete coverage.

| Relationship | Orphan / Unmatched | Assessment |
|---|---:|---|
| products → category translation | 2 categories | Reference coverage gap |
| customers → geolocation | 157 ZIP prefixes / 278 customers | Reference coverage gap |
| sellers → geolocation | 7 ZIP prefixes / 7 sellers | Reference coverage gap |

---

## 4. Orders Without Items

A total of 775 orders do not have corresponding order-item records.

| Order Status | Count |
|---|---:|
| unavailable | 603 |
| canceled | 164 |
| created | 5 |
| invoiced | 2 |
| shipped | 1 |
| **Total** | **775** |

Most cases are associated with `unavailable` or `canceled` orders and are
therefore considered consistent with the lifecycle state.

One `shipped` order without an order-item record represents an exception
requiring investigation.

No delivered order was identified as missing order-item records.

---

## 5. Orders Without Payments

One order does not have a corresponding payment record.

The order status is:

- delivered: 1

A delivered order without a payment record is classified as a high-priority
data-quality exception.

The record should be retained and flagged rather than deleted.

Recommended analytical flag:

`payment_missing_flag`

---

## 6. Orders Without Reviews

A total of 768 orders do not have review records.

| Order Status | Count |
|---|---:|
| delivered | 646 |
| shipped | 75 |
| canceled | 20 |
| unavailable | 14 |
| processing | 6 |
| invoiced | 5 |
| created | 2 |
| **Total** | **768** |

Missing reviews are considered an expected business condition because customers
are not required to submit a review.

The relationship is therefore modeled as:

`orders 1:N reviews`

with zero reviews being valid.

---

## 7. Category Translation Coverage

Two product categories are not present in the translation reference:

- `pc_gamer`
- `portateis_cozinha_e_preparadores_de_alimentos`

They affect 13 products in total.

These records should not be removed or manually translated without an
authoritative reference.

The original Portuguese category value should be preserved.

---

## 8. Geolocation Coverage

### Customer Geolocation

157 customer ZIP prefixes do not have a matching geolocation record,
affecting 278 customer rows.

This is classified as a reference-data coverage limitation rather than a
customer-data quality failure.

### Seller Geolocation

7 seller ZIP prefixes do not have a matching geolocation record,
affecting 7 seller rows.

This is also classified as a reference-data coverage limitation.

---

## 9. One-to-Many Relationships

The dataset contains substantial one-to-many relationships.

| Relationship | Evidence |
|---|---:|
| Orders with multiple order items | 9,803 |
| Maximum items per order | 21 |
| Orders with multiple payment records | 2,961 |
| Maximum payment records per order | 29 |
| Orders with multiple reviews | 547 |
| Maximum reviews per order | 3 |

---

## 10. Fan-Out Risk

Multiple child tables are connected to the order grain.

For example:

`orders → order_items`
`orders → payments`
`orders → reviews`

Joining all child tables directly can create multiplicative row expansion.

Therefore, order-level analytical datasets must aggregate child tables to the
required grain before joining them.

Recommended pattern:

```text
order_items
    ↓
aggregate by order_id
    ↓
order_item_summary
        \
         \
orders -----> analytical_order
         /
        /
payment_summary
    ↑
aggregate by order_id