# Documentation Index

## Purpose

This index provides a navigation guide to the documentation for the **Enterprise E-Commerce Analytics** project.

The documentation is organized so that a reviewer can move from project overview to KPI definitions, data architecture, reporting scope, insights, decisions, and terminology.

---

## Documentation Map

### 1. Project Overview

**File:**

```text
README.md
```

Contains:

- project overview
- business objectives
- analytical architecture
- KPI baseline
- Power BI semantic model
- dashboard pages
- key insights
- business recommendations
- reporting scope
- validation summary
- project structure
- reproducibility
- portfolio positioning

Start here for the overall project.

---

### 2. KPI Definitions

**File:**

```text
docs/kpi_definitions.md
```

Contains the controlled definitions of the project's core KPIs, including:

- Total Orders
- Total Customers
- Total Items Sold
- Product Revenue
- Freight Revenue
- GMV
- Average Order Value
- Repeat Customers
- Repeat Customer Rate
- Cancellation Rate
- Late Orders
- Late Delivery Rate
- Average Delivery Days

Also documents:

- formula
- source of truth
- grain
- inclusion rules
- validation baseline
- filter context
- KPI governance principles

Use this document whenever a metric definition needs to be checked.

---

### 3. Data Model

**File:**

```text
docs/data_model.md
```

Contains:

- analytical architecture
- dimensions
- fact tables
- analytical marts
- table grain
- primary and foreign keys
- customer identity model
- Date dimension
- Power BI semantic model
- relationship design
- filter direction
- data integrity validation
- DAX measure layer

Use this document to understand how the data model supports the reporting layer.

---

### 4. Reporting Scope

**File:**

```text
docs/reporting_scope.md
```

Defines the distinction between:

```text
Underlying analytical model
2016-09-04 -> 2018-11-12
```

and:

```text
Default dashboard presentation
2017-2018
```

It explains why 2016 remains in the analytical model but is not selected in the default dashboard view.

Use this document when reviewing historical-period coverage and dashboard scope.

---

### 5. Business Insights

**File:**

```text
docs/insights.md
```

Contains the final:

- Sales Performance findings
- Customer Retention findings
- Logistics Performance findings
- Product Performance findings
- Order Status findings
- Sales Trend findings
- Geographic Customer Concentration findings
- Executive insight summary
- Business recommendations
- Analytical guardrails

Use this document to understand the business story derived from the validated dashboard.

---

### 6. Decision Log

**File:**

```text
docs/decision_log.md
```

Records major analytical and project decisions, including:

- analytical layer before Power BI
- preservation of table grain
- dedicated Date dimension
- customer identity distinction
- relationship and filter-direction decisions
- KPI reconciliation
- logistics KPI correction
- Average Delivery Days alignment
- 2016 reporting-scope decision
- static storytelling text
- PBIX Git exclusion
- documentation approach
- final QA process

Use this document when the reasoning behind an implementation decision needs to be understood.

---

### 7. Glossary

**File:**

```text
docs/glossary.md
```

Defines important project terms, including:

- Analytical Fact
- Analytical Mart
- Analytical Layer
- AOV
- Business Insight
- Business Recommendation
- Customer ID
- Customer Unique ID
- Data Model
- Date Dimension
- DAX
- Fact Table
- GMV
- KPI
- Late Delivery
- Late Delivery Rate
- Late Orders
- Measure
- Semantic Model
- Slicer
- Source of Truth
- Time Intelligence
- Grain
- Primary Key
- Foreign Key
- Referential Integrity
- Filter Context
- QA
- Portfolio Case Study

Use this document as the terminology reference for the project.

---

## Recommended Reading Order

For a new reviewer, the recommended sequence is:

```text
1. README.md
       |
       v
2. docs/data_model.md
       |
       v
3. docs/kpi_definitions.md
       |
       v
4. docs/reporting_scope.md
       |
       v
5. docs/insights.md
       |
       v
6. docs/decision_log.md
       |
       v
7. docs/glossary.md
```

This sequence moves from:

```text
Project overview
      |
      v
Data architecture
      |
      v
Metric definitions
      |
      v
Reporting scope
      |
      v
Business findings
      |
      v
Implementation decisions
      |
      v
Terminology
```

---

## Power BI Report Navigation

The Power BI report contains four primary pages:

```text
Page 1 - Executive Overview
Page 2 - Customer & Product Analysis
Page 3 - Logistics & Operations
Page 4 - Business Insights & Storytelling
```

### Page 1 - Executive Overview

Answers:

```text
How is the business performing overall?
```

### Page 2 - Customer & Product Analysis

Answers:

```text
Who are the customers and which products drive revenue?
```

### Page 3 - Logistics & Operations

Answers:

```text
How well is the business delivering orders?
```

### Page 4 - Business Insights & Storytelling

Answers:

```text
What are the key findings and what should the business consider doing?
```

---

## Final Validation References

The documentation is based on the validated project state.

Key final KPI values:

```text
Total Orders            = 99,441
Total Items Sold        = 112,650
Product Revenue         = 13,591,643.70
Freight Revenue         = 2,251,909.54
GMV                     = 15,843,553.24
Average Order Value     = 159.33
Total Customers         = 96,096
Repeat Customers        = 2,997
Repeat Customer Rate    = 3.12%
Late Orders             = 6,535
Late Delivery Rate      = 6.77%
Average Delivery Days   = 12.56
```

Final QA checkpoints:

```text
QA-01 KPI Reconciliation      PASS
QA-02 Filter & Slicer         PASS
QA-03 Time / Date             PASS
QA-04 Visual & Storytelling   PASS
QA-05 Project Readiness       PASS
```

---

## Project Artifact Reference

The Power BI report is stored locally at:

```text
powerbi/Enterprise-ECommerce-Analytics.pbix
```

The PBIX file is intentionally ignored by Git because it is a binary reporting artifact.

The version-controlled repository contains the analytical code, documentation, tests, configuration, and reproducible project structure.

---

## Documentation Principle

The documentation set follows a simple separation of concerns:

```text
README
    = What is the project?

Data Model
    = How is the data structured?

KPI Definitions
    = What do the metrics mean?

Reporting Scope
    = What period is presented and why?

Insights
    = What did the analysis find?

Decision Log
    = Why were key choices made?

Glossary
    = What do the project terms mean?
```

This structure is intended to make the project easy to review, reproduce, maintain, and present as a professional Data Analyst portfolio case study.
