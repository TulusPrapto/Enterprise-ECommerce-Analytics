# Enterprise E-Commerce Analytics

> End-to-end e-commerce analytics portfolio project using **Python, Polars, SQL, Power BI, DAX, KPI governance, data validation, and business storytelling**.

[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/TulusPrapto/Enterprise-ECommerce-Analytics)
[![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?logo=powerbi&logoColor=black)](#power-bi-dashboard)
[![Python](https://img.shields.io/badge/Python-Polars-3776AB?logo=python&logoColor=white)](#technology-stack)

---

## Executive Summary

This project analyzes an e-commerce dataset across **sales, customers, products, and logistics** and demonstrates a complete Data Analyst workflow from analytical data preparation to executive reporting.

The project was built as a production-style portfolio case study rather than as a visualization-only exercise.

### What the project demonstrates

```text
Source Data
    ↓
Cleaning & Analytical Preparation
    ↓
Facts & Dimensions
    ↓
Analytical Marts
    ↓
KPI Definitions & Calculation
    ↓
Validation & Reconciliation
    ↓
Power BI Semantic Model
    ↓
DAX Measures
    ↓
Executive Dashboards
    ↓
Business Insights & Recommendations
```

---

## Business Questions

The analysis focuses on five core business areas.

### Sales Performance

- How are order volume and revenue evolving over time?
- What is the contribution of product revenue and freight?
- What is the overall GMV and Average Order Value?

### Customer Analysis

- How large is the customer base?
- How many customers make repeat purchases?
- How does repeat-customer activity evolve by month?
- Where are active customers concentrated geographically?

### Product Analysis

- Which product categories generate the most revenue?
- Which SKUs contribute the most revenue?
- How concentrated is revenue among leading products?

### Logistics & Operations

- How many orders are delivered late?
- What is the late delivery rate?
- How long does delivery take on average?
- How are orders distributed across operational statuses?

### Business Storytelling

- What are the most important findings?
- What business areas deserve attention?
- What actions or follow-up analyses should management consider?

---

## Key Results

The following figures are the final reconciled baseline used in the current report.

| KPI | Result |
|---|---:|
| **GMV** | **15,843,553.24** |
| **Product Revenue** | **13,591,643.70** |
| **Total Orders** | **99,441** |
| **Total Items Sold** | **112,650** |
| **Average Order Value** | **159.33** |
| **Total Customers** | **96,096** |
| **Repeat Customers** | **2,997** |
| **Repeat Customer Rate** | **3.12%** |
| **Late Orders** | **6,535** |
| **Late Delivery Rate** | **6.77%** |
| **Average Delivery Days** | **12.56** |

### Executive takeaways

1. **Sales:** GMV reached approximately **15.84M**, supported by **13.59M** in product revenue.
2. **Customers:** Repeat customers represent **3.12%** of the customer base, indicating a potential retention opportunity.
3. **Products:** Revenue is concentrated among several leading product categories and SKUs.
4. **Logistics:** **6,535 orders** were classified as late, producing a **6.77% late delivery rate**.

---

## Power BI Dashboard

The report contains four focused pages.

| Page | Purpose |
|---|---|
| **Page 1 — Executive Overview** | Overall sales, customer, product, logistics, and operational performance |
| **Page 2 — Customer & Product Analysis** | New vs repeat customers, geography, and top products |
| **Page 3 — Logistics & Operations** | Delivery performance, late orders, and order status |
| **Page 4 — Business Insights & Storytelling** | Key findings, business implications, and recommendations |

### Dashboard preview

The Power BI artifact is stored locally at:

```text
powerbi/Enterprise-ECommerce-Analytics.pbix
```

The `.pbix` file is intentionally excluded from Git because it is a binary reporting artifact.

For a public portfolio presentation, dashboard screenshots can be added under:

```text
assets/dashboard/
```

without changing the analytical model or documentation structure.

---

## Key Business Insights

### Sales Performance

Monthly revenue and order activity show a strong upward trend across the main observation period, followed by a relatively high and more stable activity level during 2018.

### Customer Retention

Repeat customers represent a relatively small share of the customer base. This makes repeat-purchase behavior an important area for further analysis.

### Logistics

Late delivery remains an operational monitoring area. The final reconciled logistics baseline is:

```text
Late Orders            = 6,535
Late Delivery Rate     = 6.77%
Average Delivery Days  = 12.56
```

### Product Performance

Revenue is concentrated among several leading categories, with `beleza_saude` generating the highest category revenue in the analysis.

---

## Business Recommendations

### 1. Improve Customer Retention

Develop targeted retention campaigns and personalized offers to increase repeat purchases.

### 2. Monitor Delivery Performance

Investigate the main causes of late deliveries and prioritize improvement in high-delay periods or regions.

### 3. Focus on High-Performing Categories

Maintain availability and marketing support for leading categories while identifying opportunities in underperforming categories.

### 4. Leverage Sales Trends

Use monthly demand patterns to improve inventory planning, promotional timing, and operational capacity.

> These recommendations are action-oriented suggestions. They are not presented as proven causal effects without additional analysis.

---

## Analytical Architecture

The project follows a layered analytical architecture:

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
Dashboard / Storytelling
```

### Dimensions

```text
dim_date
dim_customers
dim_products
dim_sellers
```

### Fact tables

```text
fact_orders
fact_order_items
fact_order_payments
fact_order_reviews
```

### Analytical marts

```text
mart_sales
mart_customers
mart_products
mart_logistics
```

### KPI / reporting outputs

```text
kpi_summary
kpi_monthly
```

---

## Data Model

The primary Power BI relationships are:

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

The main active date relationship is:

```text
dim_date[date]
      1
      |
      *
      v
fact_orders[order_purchase_date]
```

The project preserves the distinction between:

```text
customer_id
customer_unique_id
```

Customer-level metrics such as Total Customers and Repeat Customers use `customer_unique_id`.

More detail is documented in [`docs/data_model.md`](docs/data_model.md).

---

## KPI Governance

The project treats KPI definitions as an analytical contract shared between the Python/Polars pipeline and Power BI.

Core KPI definitions are documented in:

[`docs/kpi_definitions.md`](docs/kpi_definitions.md)

### Important logistics definitions

**Late Orders**

```text
estimated_delivery_variance_days > 0
```

using date-level comparison.

**Late Delivery Rate**

```text
Late Delivered Orders / Orders With Delivery Timestamp
```

**Average Delivery Days**

```text
Average(purchase_to_delivery_days)
```

The Power BI measures were reconciled against the analytical mart before final QA.

---

## Reporting Scope

The underlying model retains the full available analytical date range:

```text
2016-09-04 -> 2018-11-12
```

The default dashboard presentation focuses on:

```text
2017-2018
```

because 2016 contains limited transaction activity, including one month with no transactions.

### Important

**2016 is not deleted.**

It remains available in the underlying model and can still be selected from the Year slicer.

This is a **presentation/reporting decision**, not a data-removal decision.

See [`docs/reporting_scope.md`](docs/reporting_scope.md) for the full explanation.

---

## Data Quality & Validation

The analytical layer and Power BI report were validated through multiple checkpoints.

### Analytical validation

- primary-key uniqueness
- null validation
- foreign-key / orphan checks
- date-dimension coverage
- fact-to-mart reconciliation
- order-grain validation
- product and seller referential integrity

### Power BI QA

```text
QA-01 KPI Reconciliation      PASS
QA-02 Filter & Slicer         PASS
QA-03 Time / Date             PASS
QA-04 Visual & Storytelling   PASS
QA-05 Project Readiness       PASS
```

### Final logistics reconciliation

```text
Late Orders             = 6,535
Late Delivery Rate      = 6.77%
Average Delivery Days   = 12.56
```

---

## Technology Stack

| Area | Technology |
|---|---|
| Data preparation | Python |
| Analytical processing | Polars |
| Querying / SQL assets | SQL |
| Data modeling | Dimensional / analytical modeling |
| BI / Reporting | Power BI |
| Measures | DAX |
| Version control | Git / GitHub |
| Documentation | Markdown |

---

## Project Structure

```text
Enterprise-ECommerce-Analytics/
│
├── data/
│   ├── raw/                    # local source files; ignored by Git
│   ├── cleaned/
│   └── analytical/             # generated analytical outputs; ignored by Git
│
├── src/
│   └── analytics/              # Python / Polars analytical pipeline
│
├── sql/                        # SQL assets
├── notebooks/                  # exploratory work
├── tests/                      # validation / testing
├── dashboard/                  # dashboard-related assets
│
├── docs/
│   ├── business/
│   ├── data/
│   ├── data_model.md
│   ├── kpi_definitions.md
│   ├── reporting_scope.md
│   ├── insights.md
│   ├── decision_log.md
│   ├── glossary.md
│   └── index.md
│
├── powerbi/
│   └── Enterprise-ECommerce-Analytics.pbix
│       # local Power BI artifact; ignored by Git
│
├── README.md
├── CHANGELOG.md
├── pyproject.toml
├── requirements.txt
└── .gitignore
```

---

## Reproducibility

The analytical pipeline uses Python and Polars.

Typical execution pattern:

```powershell
python -m py_compile <module_path>
python -m <module>
```

The project follows:

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

---

## Documentation

The repository contains detailed supporting documentation:

| Document | Purpose |
|---|---|
| [`docs/data_model.md`](docs/data_model.md) | Data architecture, grain, relationships, and semantic model |
| [`docs/kpi_definitions.md`](docs/kpi_definitions.md) | Official KPI definitions and validation baseline |
| [`docs/reporting_scope.md`](docs/reporting_scope.md) | Reporting-period scope and 2016 handling |
| [`docs/insights.md`](docs/insights.md) | Business findings and recommendations |
| [`docs/decision_log.md`](docs/decision_log.md) | Major analytical and implementation decisions |
| [`docs/glossary.md`](docs/glossary.md) | Project terminology |
| [`docs/index.md`](docs/index.md) | Documentation navigation |

---

## Data Source Note

The project uses the Olist Brazilian E-Commerce dataset as the analytical source.

Raw source files are intentionally **not included in the public Git repository**. They remain local and are ignored by Git.

This keeps the public repository focused on:

```text
Source preparation
+
Analytical code
+
Model
+
Metrics
+
Validation
+
Power BI methodology
+
Business storytelling
```

For the exact data-source and reporting decisions, see the project documentation.

---

## Git & Repository Hygiene

The repository intentionally excludes:

```text
.env
data/raw/
data/analytical/
data/processed/
powerbi/*.pbix
```

The public repository therefore contains the version-controlled analytical and documentation assets without publishing the raw source CSV files or local Power BI binary.

---

## Portfolio Positioning

This project is intended to demonstrate an end-to-end **Data Analyst / BI Analyst** workflow rather than only a dashboard-building exercise.

It demonstrates practical capability across:

```text
Data preparation
Analytical modeling
Dimensional design
KPI governance
Data-quality validation
Python / Polars analytics
SQL
Power BI semantic modeling
DAX
Dashboard design
Business storytelling
Business recommendations
Git-based project management
```

The project emphasizes the analytical process:

```text
Reliable data
    +
Clear metric definitions
    +
Validated calculations
    +
Useful visualization
    +
Business interpretation
```

---

## Repository Status

Current project status:

```text
Analytics pipeline          COMPLETE
Power BI dashboard          COMPLETE
KPI reconciliation          COMPLETE
Dashboard QA                COMPLETE
Documentation               COMPLETE
Git repository hygiene      COMPLETE
Portfolio packaging         COMPLETE
```

**Project status: COMPLETE**

---

## Related Documentation

Start with:

- [`docs/index.md`](docs/index.md)
- [`docs/data_model.md`](docs/data_model.md)
- [`docs/kpi_definitions.md`](docs/kpi_definitions.md)
- [`docs/insights.md`](docs/insights.md)

