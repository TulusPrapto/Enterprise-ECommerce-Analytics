# Business Insights

## Purpose

This document records the final business insights and recommendations presented in the **Enterprise E-Commerce Analytics** Power BI report.

The findings below are descriptive and are based on the validated KPI layer and dashboard analysis. Recommendations are action-oriented but are not presented as proven causal effects.

---

## 1. Sales Performance

### Finding

GMV reached **15.84M**, with Product Revenue contributing approximately **13.59M**.

Monthly revenue shows a strong upward trend before stabilizing at a relatively high level during 2018.

### Business Implication

The business operates at substantial transaction scale, with meaningful product-value and freight-value contributions to total GMV.

### Recommendation

Use monthly demand patterns, product mix, and order-value behavior to improve inventory planning, promotional timing, and revenue-per-order opportunities.

---

## 2. Customer Retention

### Finding

Repeat customers account for **3.12%** of total customers.

The validated customer baseline is:

```text
Total Customers      = 96,096
Repeat Customers     = 2,997
Repeat Customer Rate = 3.12%
```

### Business Implication

Repeat purchasing represents a relatively small component of the customer base.

This indicates an opportunity to investigate repeat-purchase behavior, although the dashboard alone does not establish why customers do or do not return.

### Recommendation

Develop targeted retention campaigns and personalized offers to increase repeat purchases.

Potential follow-up analyses include:

- customer cohorts
- time to second purchase
- repeat purchase by product category
- repeat purchase by geography
- customer-value segmentation

---

## 3. Logistics Performance

### Finding

**6,535 orders** were classified as late, resulting in an overall **6.77% late delivery rate**.

The validated logistics baseline is:

```text
Late Orders            = 6,535
Late Delivery Rate     = 6.77%
Average Delivery Days  = 12.56
```

### Business Implication

Delivery performance remains an important operational monitoring area.

The dashboard identifies the scale of late delivery but does not by itself establish a causal relationship between delivery delays and customer retention or revenue.

### Recommendation

Investigate the main causes of late deliveries and prioritize improvement in high-delay periods or regions.

Useful follow-up breakdowns include:

- seller
- customer state
- product category
- month
- delivery duration
- order-status exceptions

---

## 4. Product Performance

### Finding

Revenue is concentrated among several leading product categories, with `beleza_saude` generating the highest category revenue in the analysis.

The dashboard also provides a Top 10 Products (SKU) by Revenue view.

### Business Implication

Leading categories and SKUs make a meaningful contribution to overall product revenue and may warrant closer attention in commercial and inventory planning.

### Recommendation

Maintain product availability and marketing support for leading categories while identifying opportunities in underperforming categories.

Further analysis should consider:

- SKU-level revenue contribution
- item volume
- average selling value
- category growth over time
- repeat-purchase behavior by category

---

## 5. Order Status

### Finding

Delivered orders dominate the order-status distribution.

The validated overall order population is:

```text
Total Orders = 99,441
Delivered    = 96,478
```

Other statuses include shipped, canceled, unavailable, invoiced, processing, created, and approved.

### Business Implication

The majority of orders reach delivered status, while the remaining statuses represent a smaller but important exception population for operational monitoring.

### Recommendation

Monitor non-delivered and exception statuses to identify operational bottlenecks, cancellation patterns, and unresolved orders.

---

## 6. Sales Trend

### Finding

Order activity and product revenue increase materially across the main observation period, with stronger activity during the 2017-2018 reporting window.

### Business Implication

The observed growth in transaction activity suggests meaningful expansion during the principal observation period.

The final periods should still be interpreted in the context of transaction coverage and partial-period effects.

### Recommendation

Use monthly demand patterns to support:

- inventory planning
- promotional timing
- operational capacity planning
- sales forecasting
- product assortment decisions

---

## 7. Geographic Customer Concentration

### Finding

Customer distribution is geographically concentrated, with **Sao Paulo (SP)** having the largest customer population in the Top 10 States view.

The dashboard is designed to show active customers within the selected period.

### Business Implication

Geographic concentration may influence fulfillment planning, customer acquisition priorities, and service-level monitoring.

### Recommendation

Compare customer concentration with:

- revenue contribution
- repeat-purchase rate
- delivery performance
- seller coverage

This can help distinguish high-volume markets from high-value or high-risk markets.

---

## 8. Executive Insight Summary

The project identifies four primary business themes:

```text
Sales
Strong transaction scale and sustained activity during the main reporting period.

Customer
Low repeat-customer penetration creates a potential retention opportunity.

Product
A limited group of leading categories and SKUs contributes significant revenue.

Logistics
Late delivery remains an important operational performance area.
```

---

## 9. Business Recommendations

### 1. Improve Customer Retention

Develop targeted retention campaigns and personalized offers to increase repeat purchases.

### 2. Monitor Delivery Performance

Investigate the main causes of late deliveries and prioritize improvement in high-delay periods or regions.

### 3. Focus on High-Performing Categories

Maintain availability and marketing support for leading categories while identifying opportunities in underperforming categories.

### 4. Leverage Sales Trends

Use monthly demand patterns to improve inventory planning, promotional timing, and operational capacity.

---

## 10. Analytical Guardrails

The following guardrails apply to interpretation of the findings:

1. The dashboard provides descriptive and diagnostic evidence rather than proof of causation.
2. A high-value category does not by itself prove that additional marketing investment will increase revenue.
3. A late-delivery rate does not by itself prove an impact on customer retention.
4. Repeat Customer Rate should be interpreted in the context of the available observation period and customer lifecycle.
5. 2016 is retained in the analytical model but excluded from the default dashboard presentation because transaction activity is limited and November 2016 contains no transactions.

---

## 11. Reporting Scope Reference

The underlying analytical model retains:

2016-09-04 -> 2018-11-12

The default dashboard presentation focuses on:

2017-2018

This is a presentation decision only. Historical data remains available in the model and through the Year slicer.

---

## 12. Final Portfolio Narrative

The project can be summarized as:

```text
Strong transaction scale
        +
Low repeat-purchase penetration
        +
Concentrated product contribution
        +
Meaningful delivery-performance opportunity
        =
Clear areas for further commercial and operational investigation
```

The dashboard therefore moves from:

```text
What happened?
```

to:

```text
Why does it matter?
```

and finally:

```text
What should the business investigate or do next?
```

This is the intended analytical storytelling pattern for the project.
