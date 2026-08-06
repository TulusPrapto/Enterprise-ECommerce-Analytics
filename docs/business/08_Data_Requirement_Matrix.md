# Data Requirement Matrix

| Item           | Value                                    |
| -------------- | ---------------------------------------- |
| Project        | Enterprise E-Commerce Analytics Platform |
| Repository     | Enterprise-ECommerce-Analytics           |
| Document       | Data Requirement Matrix                  |
| Version        | 0.1.0                                    |
| Sprint         | 1                                        |
| Document Owner | Tulus Prapto                             |
| Reviewer       | ChatGPT                                  |
| Status         | Approved                                 |
| Last Updated   | 2026-08-06                               |

---

# 1. Purpose

The Data Requirement Matrix (DRM) maps business requirements to the datasets, tables, columns, transformations, and analytical outputs required throughout the Enterprise E-Commerce Analytics Platform.

The DRM serves as the primary bridge between Business Understanding and Data Understanding.

---

# 2. Source Datasets

The project uses the following Olist datasets:

| Dataset                           | Description                      |
| --------------------------------- | -------------------------------- |
| olist_orders_dataset              | Order lifecycle information      |
| olist_order_items_dataset         | Products purchased in each order |
| olist_order_payments_dataset      | Payment details                  |
| olist_order_reviews_dataset       | Customer reviews                 |
| olist_products_dataset            | Product information              |
| olist_customers_dataset           | Customer information             |
| olist_sellers_dataset             | Seller information               |
| olist_geolocation_dataset         | Geographic reference             |
| product_category_name_translation | Category translation             |

---

# 3. Requirement Matrix

| BQ    | KPI            | Main Table    | Supporting Tables     | Primary Join Key | Expected Output              |
| ----- | -------------- | ------------- | --------------------- | ---------------- | ---------------------------- |
| BQ-01 | KPI-01         | orders        | order_items, payments | order_id         | Overall business performance |
| BQ-02 | KPI-01, KPI-02 | orders        | order_items           | order_id         | Executive KPIs               |
| BQ-06 | KPI-01         | order_items   | orders                | order_id         | Revenue trend                |
| BQ-09 | KPI-08         | order_items   | products              | product_id       | Category revenue             |
| BQ-16 | KPI-06         | customers     | orders                | customer_id      | Repeat customer analysis     |
| BQ-23 | KPI-08         | products      | order_items           | product_id       | Category performance         |
| BQ-27 | KPI-09         | sellers       | order_items           | seller_id        | Seller performance           |
| BQ-33 | KPI-10         | orders        | -                     | order_id         | Delivery time                |
| BQ-34 | KPI-11         | orders        | -                     | order_id         | Late delivery rate           |
| BQ-37 | KPI-12         | order_reviews | orders                | order_id         | Customer review score        |

---

# 4. Required Columns

## Orders

* order_id
* customer_id
* order_status
* order_purchase_timestamp
* order_approved_at
* order_delivered_customer_date
* order_estimated_delivery_date

## Order Items

* order_id
* product_id
* seller_id
* price
* freight_value

## Payments

* order_id
* payment_type
* payment_installments
* payment_value

## Customers

* customer_id
* customer_unique_id
* customer_city
* customer_state

## Products

* product_id
* product_category_name

## Sellers

* seller_id
* seller_city
* seller_state

## Reviews

* review_score
* review_creation_date

---

# 5. Join Relationships

| Left Table  | Right Table | Join Key    | Join Type |
| ----------- | ----------- | ----------- | --------- |
| orders      | order_items | order_id    | INNER     |
| orders      | payments    | order_id    | LEFT      |
| orders      | reviews     | order_id    | LEFT      |
| orders      | customers   | customer_id | INNER     |
| order_items | products    | product_id  | LEFT      |
| order_items | sellers     | seller_id   | LEFT      |

---

# 6. Data Quality Requirements

Before analysis begins, each table will be assessed for:

* Missing values
* Duplicate records
* Invalid timestamps
* Invalid foreign keys
* Unexpected null values
* Data type consistency

---

# 7. Planned Transformations

The following transformations are expected:

* Date standardization
* Revenue aggregation
* Category normalization
* Customer aggregation
* Seller aggregation
* Delivery duration calculation
* Late delivery flag
* Repeat customer identification
* Monthly summary generation

---

# 8. Output Mapping

| Output                        | Source                 |
| ----------------------------- | ---------------------- |
| Executive Dashboard           | KPI-01 to KPI-05       |
| Sales Dashboard               | KPI-01, KPI-07, KPI-08 |
| Customer Dashboard            | KPI-03, KPI-06         |
| Seller Dashboard              | KPI-09                 |
| Operations Dashboard          | KPI-10, KPI-11         |
| Customer Experience Dashboard | KPI-12                 |

---

# 9. Validation Strategy

Every analytical dataset must satisfy the following validation checks:

* Join completeness verified.
* Record counts documented.
* Null values assessed.
* Duplicate records evaluated.
* KPI totals reconciled.
* Transformation logic documented.

---

# 10. Next Phase

The next phase defines the complete analytical roadmap that connects every sprint into a single end-to-end implementation plan.

---

# Revision History

| Version | Date       | Author       | Description                     |
| ------- | ---------- | ------------ | ------------------------------- |
| 0.1.0   | 2026-08-06 | Tulus Prapto | Initial Data Requirement Matrix |
