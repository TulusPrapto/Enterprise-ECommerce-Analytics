# Dataset Inventory

| Item           | Value                                    |
| -------------- | ---------------------------------------- |
| Project        | Enterprise E-Commerce Analytics Platform |
| Repository     | Enterprise-ECommerce-Analytics           |
| Document       | Dataset Inventory                        |
| Version        | 0.1.0                                    |
| Sprint         | 2                                        |
| Document Owner | Tulus Prapto                             |
| Reviewer       | ChatGPT                                  |
| Status         | Approved                                 |
| Last Updated   | 2026-08-07                               |

---

# 1. Purpose

This document inventories all source datasets used in the Enterprise E-Commerce Analytics Platform. It provides a high-level overview of each dataset before schema validation and data profiling.

---

# 2. Source Dataset Overview

| Dataset                               | Expected Business Domain | Expected Primary Key     |
| ------------------------------------- | ------------------------ | ------------------------ |
| olist_orders_dataset.csv              | Orders                   | order_id                 |
| olist_order_items_dataset.csv         | Order Items              | order_id + order_item_id |
| olist_order_payments_dataset.csv      | Payments                 | (To be validated)        |
| olist_order_reviews_dataset.csv       | Reviews                  | review_id                |
| olist_products_dataset.csv            | Products                 | product_id               |
| olist_customers_dataset.csv           | Customers                | customer_id              |
| olist_sellers_dataset.csv             | Sellers                  | seller_id                |
| olist_geolocation_dataset.csv         | Geolocation              | (To be validated)        |
| product_category_name_translation.csv | Category Translation     | product_category_name    |

---

# 3. Expected Relationships

The expected relationships will be validated during the Schema Validation and Relationship Analysis phases.

| Parent Table | Child Table                       | Join Key              |
| ------------ | --------------------------------- | --------------------- |
| customers    | orders                            | customer_id           |
| orders       | order_items                       | order_id              |
| orders       | order_payments                    | order_id              |
| orders       | order_reviews                     | order_id              |
| order_items  | products                          | product_id            |
| order_items  | sellers                           | seller_id             |
| products     | product_category_name_translation | product_category_name |

---

# 4. Expected Analytical Domains

The datasets support the following analytical domains:

* Executive Performance
* Sales Analysis
* Revenue Analysis
* Customer Analytics
* Product Analytics
* Seller Analytics
* Logistics Analytics
* Customer Experience Analytics

---

# 5. Validation Checklist

The following checks will be completed in subsequent stages:

* Dataset availability
* Row count
* Column count
* Schema validation
* Primary key validation
* Foreign key validation
* Missing value assessment
* Duplicate assessment
* Data profiling

---

# 6. Next Phase

The next phase validates the schema of every dataset, including column names, data types, row counts, and candidate keys.

---

# Revision History

| Version | Date       | Author       | Description               |
| ------- | ---------- | ------------ | ------------------------- |
| 0.1.0   | 2026-08-07 | Tulus Prapto | Initial dataset inventory |
