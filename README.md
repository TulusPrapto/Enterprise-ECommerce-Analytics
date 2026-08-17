# Enterprise E-Commerce Analytics

An end-to-end e-commerce analytics project that combines Python/Polars analytical engineering with a Power BI semantic model and executive dashboards.

The project is designed to demonstrate a professional Data Analyst workflow from raw-source preparation and analytical modeling through KPI definition, reconciliation, Power BI reporting, business insights, and recommendations.

## Project Overview

This project analyzes e-commerce order, product, customer, payment, review, and logistics data to answer key business questions across sales, customers, products, and delivery operations.

The analytical workflow follows:

```text
Raw / Cleaning
      ↓
Analytical Facts
      ↓
Dimensions
      ↓
Analytical Marts
      ↓
KPI Metric Catalog
      ↓
KPI Calculation
      ↓
Reporting Layer
      ↓
Power BI Semantic Model
      ↓
DAX Measures
      ↓
Executive Dashboards
      ↓
Business Insights & Recommendations
```

## Business Objectives

The project focuses on five primary analytical areas:

1. **Sales Performance**
   - Order volume
   - Product revenue
   - Freight revenue
   - GMV
   - Average Order Value
   - Monthly sales trends

2. **Customer Analysis**
   - Customer base
   - Repeat customers
   - Repeat customer rate
   - New vs repeat customer behavior
   - Geographic customer distribution

3. **Product Analysis**
   - Revenue by product category
   - Top products by revenue
   - Product sales contribution

4. **Logistics & Operations**
   - Late orders
   - Late delivery rate
   - Average delivery days
   - Order-status distribution
   - Monthly delivery performance

5. **Business Storytelling**
   - Key business findings
   - Business implications
   - Action-oriented recommendations

## Analytical Architecture

### Dimensions

- `dim_date`
- `dim_customers`
- `dim_products`
- `dim_sellers`

### Fact Tables

- `fact_orders` — one row per order
- `fact_order_items` — one row per order item
- `fact_order_payments` — one row per payment record
- `fact_order_reviews` — one row per review record

### Analytical Marts

- `mart_sales`
- `mart_customers`
- `mart_products`
- `mart_logistics`

### Reporting Outputs

- `kpi_summary`
- `kpi_monthly`
- Power BI semantic model and `.pbix` report

## Key Data Characteristics

The validated analytical layer contains:

| Table | Rows | Grain |
|---|---:|---|
| `dim_customers` | 99,441 | One row per `customer_id` |
| `dim_date` | 800 | One row per calendar date |
| `dim_products` | 32,951 | One row per product |
| `dim_sellers` | 3,095 | One row per seller |
| `fact_orders` | 99,441 | One row per order |
| `fact_order_items` | 112,650 | One row per order item |
| `fact_order_payments` | 103,886 | One row per payment record |
| `fact_order_reviews` | 99,224 | One row per review record |
| `mart_customers` | 96,096 | One row per `customer_unique_id` |
| `mart_logistics` | 99,441 | One row per order |

## KPI Baseline

The following values were reconciled between the analytical pipeline and Power BI under the default all-data context:

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

### Logistics KPI Definition

The official logistics definitions are based on the analytical KPI contract:

- **Late Delivery Rate** = Late delivered orders / orders with a delivery timestamp.
- **Average Delivery Days** = Average elapsed time from purchase to customer delivery.
- A late delivery is based on the delivery date occurring after the estimated delivery date, using date-level logic consistent with the analytical mart.

## Power BI Semantic Model

The Power BI model uses the validated analytical tables as its foundation.

Core relationships include:

```text
dim_date
   │
   └── 1:* → fact_orders

fact_orders
   ├── 1:* → fact_order_items
   ├── 1:* → fact_order_payments
   └── 1:* → fact_order_reviews

fact_order_items
   ├── *:1 → dim_products
   └── *:1 → dim_sellers

fact_orders
   └── 1:1 ↔ dim_customers
```

The main active date relationship is based on:

```text
dim_date[date]
        ↓
fact_orders[order_purchase_date]
```

`dim_date` is configured as the Power BI Date Table.

## Power BI Report Pages

### Page 1 — Executive Overview

Provides a high-level view of:

- Sales KPIs
- Product category performance
- Customer overview
- Logistics KPIs
- Order-status distribution
- Monthly order trends
- Year and order-status slicers

### Page 2 — Customer & Product Analysis

Focuses on:

- New vs repeat customers by month
- Repeat customer behavior
- Top states by active customers in the selected period
- Top products (SKU) by revenue
- Year filtering

### Page 3 — Logistics & Operations

Focuses on:

- Late orders
- Late delivery rate
- Average delivery days
- Late delivery trend
- Average delivery-day trend
- Order-status distribution

### Page 4 — Business Insights & Storytelling

Combines executive KPIs, monthly trends, customer behavior, key business insights, and business recommendations.

## Key Business Insights

1. **Sales Performance**  
   GMV reached 15.84M, with Product Revenue contributing approximately 13.59M. Monthly revenue shows a strong upward trend before stabilizing at a relatively high level during 2018.

2. **Customer Retention**  
   Repeat customers account for 3.12% of total customers, indicating that repeat purchasing remains a relatively small component of the customer base.

3. **Logistics**  
   6,535 orders were classified as late, resulting in an overall 6.77% late delivery rate. Delivery performance should therefore remain a key operational monitoring area.

4. **Product Performance**  
   Revenue is concentrated among several leading product categories, with `beleza_saude` generating the highest category revenue in the analysis.

## Business Recommendations

1. **Improve Customer Retention**  
   Develop targeted retention campaigns and personalized offers to increase repeat purchases.

2. **Monitor Delivery Performance**  
   Investigate the main causes of late deliveries and prioritize improvement in high-delay periods or regions.

3. **Focus on High-Performing Categories**  
   Maintain availability and marketing support for leading categories while identifying opportunities in underperforming categories.

4. **Leverage Sales Trends**  
   Use monthly demand patterns to improve inventory planning, promotional timing, and operational capacity.

## Reporting Scope

The underlying analytical model retains the full available date range.

For the default dashboard presentation, visuals focus on **2017–2018** because 2016 contains limited transaction activity, including one month with no transactions. **2016 remains available in the underlying analytical model and can still be selected from the Year slicer.**

The report therefore separates:

- **Underlying model coverage:** full analytical date range.
- **Default dashboard view:** 2017–2018.

## Data Quality & Validation

Before Power BI modeling, the analytical layer was validated through:

- Primary-key uniqueness checks
- Null validation
- Foreign-key/orphan checks
- Fact-to-mart reconciliation
- Date-dimension continuity and coverage checks
- Order-grain validation
- Product and seller referential integrity checks
- KPI reconciliation between Python/Polars and Power BI

Examples of validated integrity checks include:

```text
fact_orders.order_id uniqueness       PASS
fact_orders → dim_customers           PASS
fact_order_items → dim_products       PASS
fact_order_items → dim_sellers        PASS
fact_orders → mart_sales              PASS
fact_orders → mart_logistics          PASS
purchase dates missing from dim_date  0
```

## Data Modeling Principles

The project intentionally preserves source evidence in the analytical layer. Historical timestamp anomalies are not silently overwritten in analytical fact construction; business-data-quality handling is separated from analytical representation.

The Power BI model follows these principles:

- Preserve analytical grain.
- Avoid unnecessary fact-to-fact joins.
- Use controlled relationship directions.
- Use a dedicated Date dimension.
- Validate KPI definitions against the analytical pipeline.
- Separate descriptive findings from causal claims.

## Project Structure

```text
Enterprise-ECommerce-Analytics/
│
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── analytical/            # generated analytical Parquet files
│
├── src/
│   └── analytics/             # Python/Polars analytical pipeline
│
├── sql/                       # SQL assets
├── notebooks/                 # exploratory work
├── tests/                     # validation/testing
├── dashboard/                 # dashboard-related assets
├── docs/                      # project documentation
├── reports/                   # optional report artifacts
├── powerbi/
│   └── Enterprise-ECommerce-Analytics.pbix
│                               # local Power BI artifact; ignored by Git
│
├── README.md
├── CHANGELOG.md
├── pyproject.toml
├── requirements.txt
└── .gitignore
```

## Power BI Artifact

The Power BI report is stored locally at:

```text
powerbi/Enterprise-ECommerce-Analytics.pbix
```

The `.pbix` file is intentionally ignored by Git because it is a binary reporting artifact. The analytical code, documentation, and project structure remain version-controlled.

## Reproducibility

The analytical pipeline is built with Python and Polars. Typical execution follows the project module pattern:

```powershell
python -m py_compile <module_path>
python -m <module>
```

The project follows a controlled workflow:

```text
Build
  ↓
Validate
  ↓
Reconcile
  ↓
Save
  ↓
Power BI Model
  ↓
DAX
  ↓
Dashboard QA
  ↓
Documentation
```

## Git Checkpoint

The project has a clean Git checkpoint after the Power BI artifact exclusion was added:

```text
5cf9d5d chore: ignore Power BI report files
```

Previous analytical foundation checkpoint:

```text
5b6ea91 feat: finalize date dimension, KPI metrics, and reporting layer
```

## Portfolio Positioning

This project demonstrates an end-to-end Data Analyst workflow covering:

- Data preparation
- Analytical modeling
- Dimensional design
- KPI governance
- Data-quality validation
- Python/Polars analytics
- Power BI semantic modeling
- DAX measures
- Dashboard design
- Business storytelling
- Action-oriented recommendations
- Git-based project management

The project is intended to be presented as a **production-style e-commerce analytics portfolio case study** rather than only a visualization exercise.
