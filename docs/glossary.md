# Glossary

## Purpose

This glossary defines important business, analytical, data-modeling, Power BI, and project terms used in the **Enterprise E-Commerce Analytics** project.

---

## A

### Analytical Fact

A detailed analytical table that preserves a defined business grain, such as one row per order or one row per order item.

Examples:

```text
fact_orders
fact_order_items
fact_order_payments
fact_order_reviews
```

### Analytical Mart

A business-oriented analytical table designed for a specific analysis or reporting purpose.

Examples:

```text
mart_sales
mart_customers
mart_products
mart_logistics
```

### Analytical Layer

The validated data layer between source/raw preparation and reporting.

In this project, the analytical layer contains facts, dimensions, marts, and KPI outputs built with Python/Polars.

---

## AOV

### Average Order Value

Average gross merchandise value per order.

Formula:

```text
AOV = GMV / Total Orders
```

Project baseline:

```text
159.33
```

---

## B

### Business Insight

A meaningful finding derived from validated analytical results that helps explain what is happening in the business.

Example:

```text
Repeat Customer Rate = 3.12%
```

The insight should describe what the result means without claiming unsupported causality.

### Business Recommendation

An action or area for investigation suggested by the analytical findings.

Example:

```text
Improve Customer Retention
```

Recommendations in this project are not presented as proven causal solutions.

---

## C

### Customer ID

`customer_id` is the customer identifier used in the order-level source/analytical relationship.

It is distinct from `customer_unique_id`.

### Customer Unique ID

`customer_unique_id` represents the long-term unique customer identity used for customer-level metrics.

It is used for:

```text
Total Customers
Repeat Customers
Repeat Customer Rate
```

### Customer Retention

The ability to encourage customers to return and make additional purchases.

In this project, repeat-purchase behavior is used as a descriptive retention signal.

---

## D

### Dashboard

An interactive Power BI reporting page containing KPIs, visualizations, filters, and business narrative.

### Data Model

The structural representation of facts, dimensions, marts, keys, relationships, grains, and filters used for analytical reporting.

### Data Quality

The degree to which data is structurally valid, complete, consistent, and usable for the intended analytical purpose.

### Date Dimension

A dedicated calendar table used for date filtering, chronological reporting, and time-based analysis.

In this project:

```text
dim_date
```

is the official Power BI Date Table.

### DAX

Data Analysis Expressions, the formula language used to create measures and calculated logic in Power BI.

Examples:

```text
Total Orders
Late Orders
Repeat Customers
Late Delivery Rate
```

---

## E

### Executive Overview

The first Power BI page that summarizes overall business performance for a management or executive audience.

In this project:

```text
Page 1 - Executive Overview
```

---

## F

### Fact Table

A table containing measurable business events at a defined grain.

Examples:

```text
fact_orders
fact_order_items
fact_order_payments
fact_order_reviews
```

### Freight Revenue

The freight-value component used in the Power BI reporting layer.

Project baseline:

```text
2,251,909.54
```

---

## G

### GMV

Gross Merchandise Value.

In this project, GMV is defined as total product value including freight.

Formula:

```text
GMV = SUM(price + freight_value)
```

Project baseline:

```text
15,843,553.24
```

---

## K

### KPI

Key Performance Indicator.

A defined business metric used to monitor performance.

Examples:

```text
Total Orders
Product Revenue
GMV
Repeat Customer Rate
Late Delivery Rate
```

### KPI Catalog

The controlled set of official metric definitions used by the analytical pipeline.

The Python metric catalog specifies fields such as:

```text
name
description
formula
source_of_truth
numerator
denominator
inclusion_rule
exclusion_rule
```

---

## L

### Late Delivery

An order is classified as late when the actual customer delivery date occurs after the estimated delivery date.

The analytical rule is:

```text
estimated_delivery_variance_days > 0
```

The comparison uses date-level logic.

### Late Delivery Rate

Percentage of orders with a delivery timestamp that arrived after the estimated delivery date.

Formula:

```text
Late Delivered Orders / Orders With Delivery Timestamp
```

Project baseline:

```text
6.77%
```

### Late Orders

Number of orders classified as late according to the validated logistics rule.

Project baseline:

```text
6,535
```

### Logistics Mart

The analytical mart containing order-level delivery, timing, and logistics-quality attributes.

Table:

```text
mart_logistics
```

Grain:

```text
1 row = 1 order
```

---

## M

### Mart

A business-oriented analytical table designed to support a specific analysis domain.

Examples:

```text
Sales Mart
Customer Mart
Product Mart
Logistics Mart
```

### Measure

A dynamic calculation in Power BI that responds to filter context.

Examples:

```text
Total Orders
Product Revenue
Late Delivery Rate
Repeat Customer Rate
```

---

## P

### Power BI Semantic Model

The logical reporting model used by Power BI to organize tables, relationships, measures, filters, and business logic.

### Product Revenue

Total monetary value of product prices.

Formula:

```text
SUM(price)
```

Project baseline:

```text
13,591,643.70
```

---

## R

### Repeat Customer

A customer whose `customer_unique_id` is associated with more than one order across the analytical period.

Project baseline:

```text
2,997
```

### Repeat Customer Rate

Percentage of customers with more than one order.

Formula:

```text
Repeat Customers / Total Customers
```

Project baseline:

```text
3.12%
```

### Reporting Scope

The period intentionally presented by default in the dashboard.

For this project:

```text
Default dashboard view = 2017-2018
```

The underlying analytical model retains the full available date range.

---

## S

### Semantic Model

The analytical structure exposed to reporting tools, including tables, relationships, measures, and filter behavior.

In this project, the semantic model is implemented in Power BI.

### Slicer

An interactive Power BI visual used to filter report content.

Examples:

```text
Year
Order Status
```

### Source of Truth

The authoritative analytical source used to define and validate a metric or business concept.

For example:

```text
Late Delivery Rate
Source of Truth = mart_logistics
```

---

## T

### Total Customers

Number of unique customers represented by `customer_unique_id`.

Project baseline:

```text
96,096
```

### Total Items Sold

Total quantity of products sold through analytical order items.

Formula:

```text
SUM(quantity)
```

Project baseline:

```text
112,650
```

### Total Orders

Total number of analytical orders.

Formula:

```text
COUNT(order_id)
```

Project baseline:

```text
99,441
```

### Time Intelligence

Date-based analytical calculations that support comparisons across periods such as year, month, quarter, and other calendar intervals.

This project uses `dim_date` as the foundation for time-based filtering and reporting.

---

## FURTHER DATA-MODELING TERMS

### Grain

The meaning represented by one row in a table.

Examples:

```text
fact_orders
1 row = 1 order

fact_order_items
1 row = 1 order item

mart_customers
1 row = 1 customer_unique_id

mart_logistics
1 row = 1 order
```

Correct grain is essential to avoid incorrect aggregations.

### Primary Key

A field or combination of fields that uniquely identifies a row at the table's defined grain.

Examples:

```text
fact_orders -> order_id
dim_products -> product_id
dim_sellers -> seller_id
dim_customers -> customer_id
```

### Foreign Key

A field that references an identifier in another table and supports relationships between analytical entities.

Examples:

```text
fact_orders.customer_id
fact_order_items.product_id
fact_order_items.seller_id
```

### Referential Integrity

The condition where foreign-key values correctly correspond to valid related records.

The project validates orphan relationships before reporting.

---

## POWER BI TERMS

### Filter Context

The set of active filters that determine the data included in a Power BI measure calculation.

Year and Order Status slicers create filter context in this project.

### Cross-Page Slicer Synchronization

The ability for a slicer selection to remain synchronized across multiple Power BI pages.

The Year slicer is synchronized across the dashboard pages.

### Secondary Y-Axis

A second numerical axis used in a combination chart when two measures have different scales.

The New vs Repeat Customers visual uses a secondary axis so that repeat customers remain visible beside new-customer volume.

---

## PROJECT TERMS

### QA

Quality Assurance.

The project used five final QA checkpoints:

```text
QA-01 KPI Reconciliation
QA-02 Filter & Slicer
QA-03 Time / Date
QA-04 Visual & Storytelling
QA-05 Project Readiness
```

All were completed successfully.

### Portfolio Case Study

A project presented as evidence of practical analytical capability, combining:

```text
Data
+
Model
+
Metrics
+
Visualization
+
Insight
+
Recommendation
```

This project is intended to demonstrate an end-to-end Data Analyst workflow.

---

## FINAL REFERENCE

The most important project concepts are:

```text
Facts
Dimensions
Marts
Grain
KPIs
DAX
Semantic Model
Date Dimension
Filter Context
Business Insights
Business Recommendations
```

These terms describe the structure used to move from raw analytical evidence to validated business reporting.
