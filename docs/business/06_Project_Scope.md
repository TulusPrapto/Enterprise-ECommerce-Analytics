# Project Scope

| Item           | Value                                    |
| -------------- | ---------------------------------------- |
| Project        | Enterprise E-Commerce Analytics Platform |
| Repository     | Enterprise-ECommerce-Analytics           |
| Document       | Project Scope                            |
| Version        | 0.1.0                                    |
| Sprint         | 1                                        |
| Document Owner | Tulus Prapto                             |
| Reviewer       | ChatGPT                                  |
| Status         | Approved                                 |
| Last Updated   | 2026-08-06                               |

---

# 1. Purpose

This document defines the scope of the Enterprise E-Commerce Analytics Platform. It establishes the analytical boundaries, expected deliverables, assumptions, exclusions, and implementation constraints to ensure that the project remains focused and manageable.

---

# 2. Project Goal

Design and implement an end-to-end analytics platform capable of transforming raw e-commerce transactional data into business insights through a reproducible and scalable analytical workflow.

---

# 3. In Scope

The following activities are included in the project:

## Business Understanding

* Business context
* Stakeholder analysis
* Business questions
* KPI framework

## Data Understanding

* Dataset exploration
* Data profiling
* Relationship analysis
* Data quality assessment

## Data Engineering

* CSV ingestion
* DuckDB database creation
* SQL transformation
* Parquet dataset generation

## Analytics

* Exploratory Data Analysis (EDA)
* Statistical summaries
* Trend analysis
* Customer analysis
* Product analysis
* Seller analysis
* Logistics analysis

## Visualization

* Python visualizations
* Interactive Power BI dashboards

## Documentation

* Technical documentation
* Business documentation
* Data dictionary
* Executive report
* README
* GitHub portfolio

---

# 4. Out of Scope

The following activities are intentionally excluded:

* Machine Learning models
* Demand forecasting
* Recommendation systems
* Fraud detection
* Real-time streaming analytics
* Cloud deployment
* Data warehouse implementation
* API development
* Web application development
* Production monitoring

---

# 5. Project Assumptions

The project assumes that:

* Source datasets are publicly available.
* Historical data is sufficient for analysis.
* Data quality issues can be resolved through transformation.
* Business KPIs can be derived from transactional data.
* Stakeholders primarily require analytical reporting.

---

# 6. Constraints

The project is subject to the following constraints:

* Historical datasets only.
* Offline analytical workflow.
* No production database access.
* No real-time data ingestion.
* Analysis limited to available Olist datasets.

---

# 7. Deliverables

The project will produce:

* DuckDB analytical database
* SQL scripts
* Parquet datasets
* Polars transformation pipeline
* EDA notebook
* Business insights
* Power BI dashboard
* Technical documentation
* GitHub repository

---

# 8. Acceptance Criteria

The project will be considered complete when:

* Data ingestion is reproducible.
* KPI calculations are validated.
* Dashboards display approved KPIs.
* Business questions are answered.
* Documentation is complete.
* Repository is fully reproducible.

---

# 9. Next Phase

The next phase defines measurable success criteria for evaluating the overall effectiveness of the project.

---

# Revision History

| Version | Date       | Author       | Description           |
| ------- | ---------- | ------------ | --------------------- |
| 0.1.0   | 2026-08-06 | Tulus Prapto | Initial Project Scope |
