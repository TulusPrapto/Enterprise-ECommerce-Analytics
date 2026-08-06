# Business Questions

| Item           | Value                                    |
| -------------- | ---------------------------------------- |
| Project        | Enterprise E-Commerce Analytics Platform |
| Repository     | Enterprise-ECommerce-Analytics           |
| Document       | Business Questions                       |
| Version        | 0.1.0                                    |
| Sprint         | 1                                        |
| Document Owner | Tulus Prapto                             |
| Reviewer       | ChatGPT                                  |
| Status         | Approved                                 |
| Last Updated   | 2026-08-06                               |

---

# 1. Purpose

This document defines the key business questions that the Enterprise E-Commerce Analytics Platform is expected to answer.

The questions translate stakeholder information needs into measurable analytical requirements and establish the foundation for KPI definition, data requirements, SQL analysis, exploratory data analysis, visualization, and dashboard development.

---

# 2. Analytical Domains

The business questions are organized into six analytical domains:

1. Executive Performance
2. Sales and Revenue
3. Customer Analytics
4. Product and Category Performance
5. Seller Performance
6. Operations and Customer Experience

---

# 3. Executive Performance

**Primary Stakeholder:** Executive Board

### BQ-01

How has overall business performance changed over time?

### BQ-02

How are total revenue, orders, customers, and average order value trending?

### BQ-03

Which product categories contribute the most to business performance?

### BQ-04

Which geographic markets contribute the most to orders and revenue?

### BQ-05

Are there identifiable periods of strong growth or declining performance?

**Expected Business Value**

These questions provide executives with a high-level view of company performance and help identify strategic growth opportunities or areas requiring management attention.

---

# 4. Sales and Revenue

**Primary Stakeholders:** Sales Manager and Finance Manager

### BQ-06

How does revenue change over time?

### BQ-07

What are the monthly and yearly sales trends?

### BQ-08

Which products generate the highest sales value?

### BQ-09

Which product categories generate the highest revenue?

### BQ-10

What is the average order value and how does it change over time?

### BQ-11

Which geographic regions generate the highest sales?

### BQ-12

How are customers using different payment methods?

### BQ-13

How do installment patterns relate to transaction value?

**Expected Business Value**

The analysis helps sales and finance stakeholders understand revenue drivers, sales patterns, payment behavior, and opportunities for commercial optimization.

---

# 5. Customer Analytics

**Primary Stakeholder:** Marketing Manager

### BQ-14

How many unique customers purchase from the marketplace?

### BQ-15

Where are customers geographically concentrated?

### BQ-16

What proportion of customers make repeat purchases?

### BQ-17

How does purchasing behavior differ between new and repeat customers?

### BQ-18

Which customers contribute the highest transactional value?

### BQ-19

Can customers be segmented based on purchasing behavior?

### BQ-20

What patterns can be identified in customer purchase frequency and monetary value?

**Expected Business Value**

These questions support customer segmentation, retention analysis, and more targeted marketing strategies.

---

# 6. Product and Category Performance

**Primary Stakeholders:** Sales Manager and Executive Board

### BQ-21

Which products have the highest sales volume?

### BQ-22

Which products generate the highest sales value?

### BQ-23

Which product categories generate the highest revenue?

### BQ-24

Which categories receive the largest number of orders?

### BQ-25

How does category performance change over time?

### BQ-26

Are there products or categories with strong sales volume but relatively low customer ratings?

**Expected Business Value**

The analysis helps identify high-performing products, category growth opportunities, and potential product-quality issues.

---

# 7. Seller Performance

**Primary Stakeholder:** Seller Success Manager

### BQ-27

Which sellers generate the highest sales value?

### BQ-28

Which sellers process the largest number of orders?

### BQ-29

How concentrated are marketplace sales among sellers?

### BQ-30

How does seller performance vary geographically?

### BQ-31

Which sellers are associated with stronger or weaker customer review outcomes?

### BQ-32

Which sellers may require performance improvement initiatives?

**Expected Business Value**

These questions help the marketplace identify top-performing sellers and sellers that may require additional operational support.

---

# 8. Operations and Customer Experience

**Primary Stakeholders:** Operations Manager and Customer Experience Manager

### BQ-33

What is the average delivery time?

### BQ-34

What proportion of delivered orders arrive after the estimated delivery date?

### BQ-35

How does delivery performance vary across geographic regions?

### BQ-36

How does delivery performance change over time?

### BQ-37

What is the distribution of customer review scores?

### BQ-38

Is delivery performance associated with customer review scores?

### BQ-39

Which product categories receive the lowest customer ratings?

### BQ-40

Which operational patterns are associated with poor customer experience?

**Expected Business Value**

These questions help identify logistics bottlenecks and potential drivers of customer dissatisfaction.

---

# 9. Business Question Prioritization

Not every question has the same analytical priority.

| Priority | Meaning                                                   |
| -------- | --------------------------------------------------------- |
| P1       | Critical for executive decision-making and core dashboard |
| P2       | Important for functional analysis                         |
| P3       | Supporting or exploratory analysis                        |

## P1 — Core Questions

* BQ-01 Overall business performance
* BQ-02 Core KPI trends
* BQ-06 Revenue trends
* BQ-09 Category revenue
* BQ-10 Average order value
* BQ-16 Repeat purchase behavior
* BQ-23 Category performance
* BQ-27 Seller revenue performance
* BQ-33 Delivery time
* BQ-34 Late delivery rate
* BQ-37 Customer review performance
* BQ-38 Delivery and review relationship

## P2 — Functional Questions

* Geographic performance
* Payment behavior
* Customer segmentation
* Product performance
* Seller concentration
* Regional logistics performance
* Category-level customer experience

## P3 — Exploratory Questions

* Installment behavior
* Detailed customer purchasing patterns
* Seller improvement opportunities
* Cross-domain operational patterns

---

# 10. Analytical Traceability

Each business question will eventually be connected to:

* Stakeholder
* KPI
* Source table
* Required fields
* Transformation rule
* SQL query
* EDA analysis
* Visualization
* Dashboard
* Business insight
* Recommendation

Example:

| Component         | Definition                                                   |
| ----------------- | ------------------------------------------------------------ |
| Business Question | BQ-34: What proportion of delivered orders arrive late?      |
| Stakeholder       | Operations Manager                                           |
| KPI               | Late Delivery Rate                                           |
| Required Data     | Estimated and actual delivery dates                          |
| Analysis          | Compare actual delivery date against estimated delivery date |
| Visualization     | Monthly late-delivery trend                                  |
| Insight           | Identify periods or regions with elevated late delivery      |
| Decision          | Prioritize logistics improvement initiatives                 |

This traceability framework ensures that every analytical output can be linked to a clearly defined business requirement.

---

# 11. Analytical Guardrails

The following principles will be applied when answering the business questions:

* Revenue definitions must be documented before calculation.
* Customer-level analysis must distinguish between customer identifiers available in the source data.
* Cancelled and unavailable orders must not automatically be treated as completed sales.
* Delivery metrics must only use orders with appropriate delivery information.
* Review analysis must account for missing reviews where applicable.
* Correlation or association must not automatically be interpreted as causation.
* Business conclusions must remain within the limitations of the available historical dataset.

---

# 12. Expected Analytical Outputs

The business questions will eventually produce:

* Executive KPI summary
* Revenue trend analysis
* Product and category analysis
* Customer segmentation
* Repeat purchase analysis
* Seller performance analysis
* Delivery performance analysis
* Customer experience analysis
* Interactive Power BI dashboards
* Executive insights and recommendations

---

# 13. Next Phase

The next phase defines the KPI Framework.

Each core business question will be mapped to measurable metrics with documented definitions, calculation logic, analytical grain, dimensions, and business interpretation.

---

# Revision History

| Version | Date       | Author       | Description                         |
| ------- | ---------- | ------------ | ----------------------------------- |
| 0.1.0   | 2026-08-06 | Tulus Prapto | Initial business question framework |
