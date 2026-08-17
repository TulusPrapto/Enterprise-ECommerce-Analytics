# Decision Log

## Purpose

This document records important analytical, modeling, Power BI, and project-structure decisions made during the **Enterprise E-Commerce Analytics** project.

The goal is to preserve the reasoning behind major implementation choices so the project remains understandable and reproducible.

---

## Decision 01 - Build an Analytical Layer Before Power BI

### Decision

Build and validate the analytical layer with Python/Polars before creating the final Power BI semantic model.

### Reason

The analytical layer provides a controlled source for:

- data transformation
- analytical facts
- dimensions
- marts
- KPI calculations
- reconciliation

This reduces the risk of building dashboard logic directly on raw data.

### Result

Power BI was built from validated analytical Parquet outputs rather than directly from raw source tables.

---

## Decision 02 - Preserve Table Grain

### Decision

Keep facts at their intended business grain instead of flattening all transactions into one wide table.

### Reason

The project contains different grains:

```text
fact_orders
1 row = 1 order

fact_order_items
1 row = 1 order item

fact_order_payments
1 row = 1 payment record

fact_order_reviews
1 row = 1 review record
```

Flattening these grains can create row multiplication and inflate metrics.

### Result

Revenue, order counts, payment analysis, and review analysis can be calculated without unintended fact multiplication.

---

## Decision 03 - Use a Dedicated Date Dimension

### Decision

Use `dim_date` as the official calendar dimension for Power BI.

### Reason

A dedicated Date dimension provides:

- consistent Year filtering
- chronological month sorting
- calendar attributes
- future time-intelligence support
- a single date-filtering layer

### Result

The active reporting relationship is:

```text
dim_date[date]
      |
      v
fact_orders[order_purchase_date]
```

`dim_date` was marked as the Power BI Date Table.

---

## Decision 04 - Preserve Customer Identity Distinction

### Decision

Keep `customer_id` and `customer_unique_id` as separate analytical concepts.

### Reason

`customer_id` is used in the order-level source relationship, while `customer_unique_id` represents long-term customer identity.

Repeat-purchase analysis requires the long-term identity.

### Result

Customer-level metrics use `customer_unique_id`, including:

```text
Total Customers
Repeat Customers
Repeat Customer Rate
```

---

## Decision 05 - Avoid Unnecessary Bidirectional Relationships

### Decision

Prefer controlled dimension-to-fact filtering rather than changing all relationships to bidirectional filtering.

### Reason

Unrestricted bidirectional filtering can create ambiguous filter propagation and make semantic-model behavior harder to control.

### Exception

The current `dim_customers` to `fact_orders` relationship is a `1:1` relationship in the validated source model and required bidirectional behavior in Power BI for the observed model configuration.

### Result

Filter behavior was handled with targeted measures where necessary rather than changing the overall model indiscriminately.

---

## Decision 06 - Use Targeted Measures for Period-Sensitive Customer Analysis

### Decision

Calculate period-sensitive customer metrics from the order fact context when a dimension table does not naturally receive the Date filter.

### Reason

A Year filter flows through `dim_date` to `fact_orders`, but does not necessarily filter `dim_customers` directly.

For example, the `Top 10 States by Active Customers in Selected Period` visual required a measure based on the filtered order population.

### Result

Customer Analysis visuals became responsive to the Year slicer without changing the overall relationship architecture.

---

## Decision 07 - Reconcile Power BI KPIs Against the Analytical Pipeline

### Decision

Treat the Python/Polars KPI layer as the analytical contract and reconcile Power BI DAX against it.

### Reason

A dashboard can display plausible numbers while still using a different business definition.

The project therefore validates KPI definitions before finalizing the report.

### Result

A logistics discrepancy was discovered and investigated before the final dashboard was approved.

---

## Decision 08 - Use Date-Level Logic for Late Delivery

### Decision

Late delivery classification must compare delivery and estimated delivery at the date level.

### Reason

The analytical mart defines:

```text
estimated_delivery_variance_days > 0
```

using dates rather than full timestamps.

A direct DateTime comparison in DAX initially classified same-day deliveries with different time components as late.

### Result

The Power BI `Late Orders` and `Late Delivery Rate` measures were corrected to match the analytical definition.

Final reconciled values:

```text
Late Orders          = 6,535
Late Delivery Rate   = 6.77%
```

---

## Decision 09 - Align Average Delivery Days With the Analytical Definition

### Decision

Calculate elapsed delivery time using the same fractional-day logic used by the analytical mart.

### Reason

The analytical pipeline calculates elapsed seconds and divides by 86,400 seconds per day.

A whole-day `DATEDIFF` implementation in DAX produced a slightly different result.

### Result

The Power BI implementation was aligned to the analytical definition.

Final value:

```text
Average Delivery Days = 12.56
```

---

## Decision 10 - Keep 2016 in the Analytical Model

### Decision

Do not delete or modify 2016 records even though the default dashboard view focuses on 2017-2018.

### Reason

2016 contains limited transaction activity, including a month with no transactions.

Showing the sparse 2016 period by default made some monthly visuals harder to interpret.

### Result

The underlying model retains the full date range:

```text
2016-09-04 -> 2018-11-12
```

while the default dashboard presentation uses:

```text
2017-2018
```

2016 remains selectable through the Year slicer.

---

## Decision 11 - Use Static Insight Text for Overall Findings

### Decision

Keep Key Business Insights and Business Recommendations as static explanatory text rather than attempting to dynamically rewrite the narrative for every slicer state.

### Reason

The Page 4 text is intended to communicate overall validated findings and recommendations.

Dynamic slicers can change KPI values and visual trends, but a static narrative avoids presenting a global finding as though it were automatically recomputed for every filter combination.

### Result

The report separates:

```text
Dynamic visuals and KPIs
        +
Static overall business narrative
```

---

## Decision 12 - Keep Dashboard Pages Focused

### Decision

Use four primary Power BI pages with distinct analytical purposes.

### Result

```text
Page 1 - Executive Overview
Page 2 - Customer & Product Analysis
Page 3 - Logistics & Operations
Page 4 - Business Insights & Storytelling
```

Each page answers a different business question rather than repeating the same visual analysis.

---

## Decision 13 - Exclude 2016 From the Default Dashboard View Only

### Decision

Set the default Year slicer state to:

```text
2016 = not selected
2017 = selected
2018 = selected
```

### Reason

This improves readability of the main reporting visuals while preserving historical access.

### Result

The dashboard presents the main activity period by default, while 2016 remains available for exploration.

---

## Decision 14 - Keep the PBIX Outside Git Tracking

### Decision

Store the Power BI report locally but exclude `.pbix` files from Git tracking.

### Reason

The PBIX is a binary reporting artifact and the final file is approximately 36 MB.

The repository should prioritize version-controlled:

- analytical code
- tests
- documentation
- configuration
- reproducible project structure

### Result

The `.gitignore` contains:

```text
powerbi/*.pbix
```

The report remains locally available at:

```text
powerbi/Enterprise-ECommerce-Analytics.pbix
```

---

## Decision 15 - Keep Documentation in Markdown

### Decision

Use Markdown documentation in `docs/` and a top-level `README.md`.

### Reason

Markdown is:

- version-controllable
- portable
- readable on GitHub
- easy to review
- suitable for portfolio presentation

### Result

The project documentation is organized into separate topic-specific files.

---

## Decision 16 - Separate Insight From Causal Claim

### Decision

Do not present descriptive dashboard findings as proven causal relationships.

### Examples

The report may state:

```text
Late Delivery Rate = 6.77%
```

But it should not automatically state:

```text
Late delivery caused customer churn.
```

without additional causal or cohort analysis.

Similarly, a high-revenue product category does not by itself prove that more marketing investment will increase revenue.

### Result

Business recommendations are framed as areas for investigation or action rather than unsupported causal conclusions.

---

## Decision 17 - Validate Before Final Portfolio Packaging

### Decision

Complete dashboard QA before finalizing portfolio documentation.

### QA checkpoints

```text
QA-01 KPI Reconciliation      PASS
QA-02 Filter & Slicer         PASS
QA-03 Time / Date             PASS
QA-04 Visual & Storytelling   PASS
QA-05 Project Readiness       PASS
```

### Result

The dashboard and documentation were finalized only after KPI, filter, time, visual, and repository checks.

---

## 18. Final Architectural Principle

The project follows this overall decision pattern:

```text
Preserve evidence
      |
      v
Model at correct grain
      |
      v
Define metrics explicitly
      |
      v
Validate analytical outputs
      |
      v
Reconcile Power BI
      |
      v
Build focused dashboards
      |
      v
Separate findings from causal claims
      |
      v
Document decisions
```

This approach is intended to keep the project reproducible, auditable, and suitable for presentation as a professional Data Analyst portfolio case study.
