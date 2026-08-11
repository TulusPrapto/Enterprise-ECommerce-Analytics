# Business Data Quality Exception Investigation

## 1. Purpose

This document records the investigation and business interpretation of data-quality exceptions identified during the Business Data Quality assessment of the Enterprise E-Commerce Analytics dataset.

The objective is not to automatically modify historical data, but to determine whether identified exceptions should be accepted, retained, flagged, investigated further, or treated as business-rule exceptions.

The investigation is based on the output of the Business Data Quality framework and its supporting exception-analysis artifacts.

---

## 2. Investigation Scope

The Business Data Quality framework evaluates 18 business rules across the following domains:

* Orders
* Order Items
* Payments
* Reviews
* Products
* Relationships

The latest quality assessment produced:

| Metric            | Result |
| ----------------- | -----: |
| Total rules       |     18 |
| Passed rules      |     13 |
| Failed rules      |      5 |
| Warning failures  |      4 |
| Critical failures |      1 |
| Quality score     |  87.04 |
| Grade             |      B |
| Status            | REVIEW |
| Data modified     |  False |

The five failed rules were selected for exception investigation:

* ORD-001
* ORD-005
* PAY-001
* PAY-003
* PROD-001

Relationship rules REL-001 through REL-005 passed successfully and therefore did not require exception remediation.

---

## 3. Exception Register

| Rule ID  | Domain   | Severity | Affected Rows | Decision           | Business Impact |
| -------- | -------- | -------- | ------------: | ------------------ | --------------- |
| ORD-001  | Orders   | WARNING  |             8 | ACCEPT_WITH_CAVEAT | LOW             |
| ORD-005  | Orders   | WARNING  |            23 | FLAG_INVESTIGATE   | MEDIUM          |
| PAY-001  | Payments | WARNING  |             9 | REVIEW_RULE        | MEDIUM          |
| PAY-003  | Payments | FAIL     |             2 | FAIL_INVESTIGATE   | HIGH            |
| PROD-001 | Products | WARNING  |             4 | FLAG               | MEDIUM          |

The exception population is small relative to the overall dataset, but the exceptions have different business implications. Therefore, remediation is determined by rule semantics and business impact rather than affected-row count alone.

---

# 4. Deep Investigation Findings

## 4.1 ORD-001 — Missing Customer Delivery Date

### Rule

Delivered orders should contain a customer delivery date.

### Result

* Affected rows: 8
* Severity: WARNING
* Decision: ACCEPT_WITH_CAVEAT
* Treatment: FLAG_INCOMPLETE_DELIVERY_RECORD
* Business impact: LOW

### Investigation

Eight delivered orders do not contain an actual customer delivery date.

The deep investigation found:

* 7 of the 8 affected orders contain carrier delivery information.
* All 8 affected orders contain an estimated delivery date.
* The affected records should therefore not automatically be interpreted as completely missing delivery information.

### Business interpretation

The absence of an actual customer delivery timestamp represents an incomplete historical delivery record.

However, the available carrier and estimated delivery information provides additional evidence about the order lifecycle.

Automatically imputing the customer delivery date would create synthetic historical information and could introduce false precision.

### Decision

**ACCEPT_WITH_CAVEAT**

### Treatment

**FLAG_INCOMPLETE_DELIVERY_RECORD**

The original value should remain unchanged. The record may be flagged for downstream analysis where actual customer delivery timing is required.

---

## 4.2 ORD-005 — Customer Delivery Before Carrier Delivery

### Rule

Customer delivery date should not precede carrier delivery date.

### Result

* Affected rows: 23
* Severity: WARNING
* Decision: FLAG_INVESTIGATE
* Treatment: RETAIN_AND_FLAG
* Business impact: MEDIUM

### Investigation

Twenty-three records contain a customer delivery timestamp earlier than the carrier delivery timestamp.

All 23 affected records have:

```text
order_status = delivered
```

The observed date-gap distribution is:

| Statistic |         Gap |
| --------- | ----------: |
| Minimum   |  ~0.02 days |
| Median    |  ~1.66 days |
| Mean      |  ~3.27 days |
| Maximum   | ~16.10 days |

### Business interpretation

The anomaly is inconsistent with the expected physical delivery sequence.

Possible explanations may include timestamp recording problems, source-system sequencing issues, or historical data anomalies. The available dataset does not provide sufficient evidence to determine the exact cause.

Therefore, automatically swapping, correcting, or imputing timestamps would risk altering historical evidence.

### Decision

**FLAG_INVESTIGATE**

### Treatment

**RETAIN_AND_FLAG**

The original timestamps should be retained. Records should be excluded or separately flagged when analytical logic requires a valid delivery sequence.

---

## 4.3 PAY-001 — Zero or Negative Payment Value

### Rule

Payment records should normally contain a positive payment value.

### Result

* Affected rows: 9
* Severity: WARNING
* Decision: REVIEW_RULE
* Treatment: RETAIN_ZERO_VALUE_PAYMENT
* Business impact: MEDIUM

### Investigation

Nine payment records have non-positive payment values.

The detailed investigation found:

* Zero values: 9
* Negative values: 0
* Therefore, all affected records contain exactly zero payment value.
* Several records use `voucher` or `not_defined` payment types.
* Some affected orders contain multiple payment records.

### Business interpretation

The evidence does not support automatically classifying all zero-value payment records as invalid.

Zero-value records may represent a business or payment-system condition rather than a corrupted numerical value.

The current rule should therefore be reviewed before being promoted to a hard failure.

### Decision

**REVIEW_RULE**

### Treatment

**RETAIN_ZERO_VALUE_PAYMENT**

Zero-value payment records should remain in the dataset and should not be replaced with arbitrary positive values or deleted without additional business evidence.

---

## 4.4 PAY-003 — Invalid Payment Installments

### Rule

Payment installments must fall within the accepted business range.

### Result

* Affected rows: 2
* Severity: FAIL
* Decision: FAIL_INVESTIGATE
* Treatment: RETAIN_AND_FLAG
* Business impact: HIGH

### Investigation

Two payment records contain:

```text
payment_installments = 0
```

Both records contain positive payment values.

The investigation therefore identifies a semantic inconsistency between the payment amount and installment count.

The affected records are credit-card payment records.

### Business interpretation

A zero installment value associated with a positive payment amount does not conform to the expected installment semantics represented by the dataset.

Because payment analysis can directly affect revenue, payment-method, financing, and customer-behavior analysis, these records require explicit treatment.

### Decision

**FAIL_INVESTIGATE**

### Treatment

**RETAIN_AND_FLAG**

The source values should be retained. Downstream analytical models requiring valid installment semantics should exclude or separately flag these records.

No automatic replacement value should be introduced without an authoritative business definition.

---

## 4.5 PROD-001 — Non-Positive Product Weight

### Rule

Product weight should be positive when populated.

### Result

* Affected rows: 4
* Severity: WARNING
* Decision: FLAG
* Treatment: RETAIN_AND_FLAG
* Business impact: MEDIUM

### Investigation

Four products have:

```text
product_weight_g = 0
```

All four affected products appear in the order-items dataset.

Their other recorded dimensions remain populated, including length, height, and width.

### Business interpretation

The zero weight values may affect logistics-related calculations, shipping analysis, freight analysis, and other models that depend on physical product characteristics.

Because all affected products have sales activity, the issue is relevant to actual analytical use rather than being limited to unused catalog records.

However, the dataset does not provide an authoritative replacement weight.

### Decision

**FLAG**

### Treatment

**RETAIN_AND_FLAG**

The zero weight should remain unchanged until an authoritative product source is available.

---

# 5. Business Decision Summary

The exception investigation results in five different business decisions.

| Rule     | Decision           | Treatment                       |
| -------- | ------------------ | ------------------------------- |
| ORD-001  | ACCEPT_WITH_CAVEAT | FLAG_INCOMPLETE_DELIVERY_RECORD |
| ORD-005  | FLAG_INVESTIGATE   | RETAIN_AND_FLAG                 |
| PAY-001  | REVIEW_RULE        | RETAIN_ZERO_VALUE_PAYMENT       |
| PAY-003  | FAIL_INVESTIGATE   | RETAIN_AND_FLAG                 |
| PROD-001 | FLAG               | RETAIN_AND_FLAG                 |

The common principle is:

> Data-quality exceptions should be investigated and classified before modification. Historical source values should not be changed without sufficient business evidence.

---

# 6. Data Treatment Policy

The current Business Data Quality framework follows a **non-destructive data-quality policy**.

### 6.1 No automatic imputation

Missing or anomalous values are not automatically replaced when the dataset does not provide sufficient evidence for a correct replacement.

This applies particularly to:

* Customer delivery dates
* Product weights
* Payment installment values

### 6.2 No automatic deletion

Records are not deleted solely because they fail a business-quality rule.

Instead, failed records are retained and can be flagged for downstream analytical use.

### 6.3 Preserve historical evidence

Original source values are preserved whenever possible.

This is especially important for timestamp anomalies such as ORD-005 because correcting historical timestamps without authoritative evidence could introduce fabricated information.

### 6.4 Separate quality status from analytical usability

A record can remain in the source dataset while being considered unsuitable for a specific analytical calculation.

For example:

* A payment record can remain available for payment-history analysis while being excluded from installment-based analysis.
* A product can remain available for product-sales analysis while its weight is excluded from logistics calculations.
* An order can remain available for order-volume analysis while being excluded from delivery-duration calculations if its delivery timestamps are unreliable.

---

# 7. Downstream Analytical Impact

The identified exceptions should be considered when building downstream analytical models.

## Orders

ORD-001 and ORD-005 may affect:

* Delivery-time calculations
* Delivery SLA analysis
* Logistics performance
* Customer delivery experience analysis

## Payments

PAY-001 and PAY-003 may affect:

* Payment-value aggregation
* Payment-method analysis
* Installment analysis
* Revenue reconciliation
* Payment behavior analysis

## Products

PROD-001 may affect:

* Shipping analysis
* Freight analysis
* Product logistics
* Weight-based operational metrics

Therefore, downstream datasets should expose appropriate quality flags rather than silently correcting these records.

---

# 8. Governance Recommendations

The following governance controls are recommended for future pipeline iterations.

### 8.1 Preserve rule-level evidence

Every quality run should retain:

* Rule ID
* Dataset
* Severity
* Evaluated rows
* Affected rows
* Pass/fail status
* Representative samples
* Business decision
* Treatment

### 8.2 Monitor recurring exceptions

Rules that repeatedly fail across future data refreshes should be reviewed to determine whether the issue originates from:

* Source-system behavior
* Data-entry processes
* ETL transformations
* Business-rule definitions
* Historical data limitations

### 8.3 Review warning rules periodically

Warning rules should not automatically become hard failures.

PAY-001 demonstrates why rule semantics should be reviewed against actual business behavior before changing severity.

### 8.4 Establish authoritative reference sources

Future remediation should preferably use authoritative sources for:

* Actual delivery timestamps
* Product weights
* Payment/installment definitions

### 8.5 Maintain non-destructive quality controls

Quality controls should identify and classify problematic records without unnecessarily modifying historical source data.

---

# 9. Current Quality Position

The current dataset achieves a **Business Data Quality score of 87.04 (Grade B)**.

The framework identifies five exceptions requiring business attention:

* 2 order-related exceptions
* 2 payment-related exceptions
* 1 product-related exception

The five exceptions do not justify blanket dataset rejection.

Instead, the appropriate business position is:

**The dataset is usable with controlled caveats and targeted exception handling.**

The quality status therefore remains:

**REVIEW**

---

# 10. Final Conclusion

The Business Data Quality investigation demonstrates that data quality should not be evaluated solely through a pass/fail mechanism.

The five failed rules represent different business situations:

* incomplete historical records,
* temporal inconsistencies,
* potentially legitimate zero-value payment records,
* semantically invalid installment values,
* and incomplete product logistics attributes.

The investigation therefore adopts a rule-specific treatment strategy rather than applying a single remediation policy to all exceptions.

No source data was modified during the investigation.

The resulting framework provides a controlled foundation for downstream analytics by making data-quality limitations explicit, traceable, and actionable.
