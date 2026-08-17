# Reporting Scope

## Purpose

This document defines the reporting-period scope used by the **Enterprise E-Commerce Analytics** Power BI report.

The reporting scope is a presentation decision only. It does **not** remove, overwrite, or exclude underlying analytical records from the project data model.

---

## 1. Underlying Analytical Model Coverage

The analytical Date dimension covers the full available date range:

```text
2016-09-04 -> 2018-11-12
```

The underlying model retains the complete analytical population, including all available 2016, 2017, and 2018 records.

Therefore:

```text
2016 = retained in the model
2017 = retained in the model
2018 = retained in the model
```

No historical year was deleted from the analytical layer because of the reporting presentation decision.

---

## 2. Default Dashboard Presentation Scope

The default Power BI dashboard presentation focuses on:

```text
2017-2018
```

The Year slicer is configured so that the default report view emphasizes:

```text
2016   = not selected
2017   = selected
2018   = selected
```

Users can still select 2016 from the Year slicer when they need to inspect the earlier period.

---

## 3. Why 2016 Is Not Included in the Default Visual Scope

The 2016 period contains very limited transaction activity relative to the main observation period.

In particular:

- September 2016 contains only a very small number of transactions.
- October 2016 contains limited transaction activity.
- November 2016 contains no transactions.
- December 2016 contains only a very small number of transactions.

Because of this sparse activity, including 2016 by default can make monthly reporting visuals harder to interpret.

A month with no transaction activity may also be absent from a visual when the plotted measure has no corresponding fact records, which can make the early time series appear visually irregular.

For presentation purposes, focusing the default dashboard view on 2017-2018 provides a clearer representation of the primary activity period.

---

## 4. Reporting Scope Principle

The project intentionally separates:

```text
Data / Model Scope
        |
        | full analytical coverage
        v
2016-09-04 -> 2018-11-12

        versus

Default Presentation Scope
        |
        | reporting readability
        v
2017-2018
```

This distinction is important.

The default dashboard scope is **not** a data-cleaning rule and is **not** a statement that 2016 data is invalid.

It is a reporting and presentation decision.

---

## 5. November 2016 and the Date Dimension

The absence of November 2016 transactions should not be interpreted as a missing date in the Date dimension.

The `dim_date` table remains a continuous calendar dimension across its defined coverage.

Conceptually:

```text
dim_date
2016-09
2016-10
2016-11
2016-12
...

fact_orders
2016-09 -> transactions
2016-10 -> transactions
2016-11 -> no transactions
2016-12 -> transactions
```

Therefore:

```text
No transactions in a month
        !=
Missing calendar date in dim_date
```

This distinction is important for correct Power BI time-series modeling.

---

## 6. Power BI Presentation Behavior

The report retains 2016 in the underlying model and Year slicer.

Default:

```text
Year
[ ] 2016
[x] 2017
[x] 2018
```

User exploration:

```text
[ ] 2016
[ ] 2017
[ ] 2018
```

or any other combination supported by the slicer.

The report therefore supports both:

1. a cleaner default executive presentation using 2017-2018;
2. historical exploration of 2016 when required.

---

## 7. Dashboard Documentation Wording

The dashboard's reporting-scope note is represented by the following wording:

> **Reporting Scope:** Visuals focus on 2017-2018 because 2016 contains limited transaction activity, including one month with no transactions. 2016 remains available in the underlying analytical model.

This statement is intentionally concise so that it can be used in portfolio documentation or as a reporting-scope note without overwhelming the dashboard.

---

## 8. Analytical Governance

The reporting scope follows these principles:

1. Do not delete historical records solely to improve dashboard appearance.
2. Keep the complete analytical model available for audit and exploration.
3. Separate data-quality decisions from presentation decisions.
4. Document any default visual scope that differs from the underlying model coverage.
5. Allow users to access the excluded-by-default period through interactive filtering where appropriate.

---

## 9. Current Approved Scope

| Scope | Value |
|---|---|
| Underlying Date Dimension | 2016-09-04 to 2018-11-12 |
| Default Dashboard View | 2017-2018 |
| 2016 Data in Model | Retained |
| 2016 in Year Slicer | Available |
| Reason for Default Exclusion | Limited activity and one month with no transactions |
| Nature of Decision | Presentation / reporting scope |

---

## 10. Final Statement

The Enterprise E-Commerce Analytics project does **not** remove 2016 from the analytical model.

Instead:

```text
Full analytical model
        +
Default reporting focus on 2017-2018
        =
Clearer dashboard presentation
without loss of historical data
```

This approach preserves analytical completeness while improving the readability of the default executive reporting experience.
