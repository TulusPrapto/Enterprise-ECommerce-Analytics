# Data Profiling Specification

## Document Metadata

| Field | Value |
|---|---|
| Project | Enterprise E-Commerce Analytics |
| Analysis Phase | Sprint 2.4.1 — Data Profiling |
| Document Owner | Tulus Prapto |
| Tool | Python + Polars |
| Python Version | 3.14.6 |
| Polars Version | 1.43.2 |
| Input | Raw Olist CSV datasets |
| Output | data_profile.json |
| Status | Specification |

---

## 1. Objective

The objective of data profiling is to quantitatively describe the structure,
distribution, completeness, cardinality, temporal coverage, and potential
anomalies of the raw datasets before data cleaning and transformation.

Profiling is an observation activity.

No source data will be modified during this phase.

---

## 2. Profiling Principles

1. Raw CSV files remain unchanged.
2. Profiling is reproducible through Python.
3. Polars is the primary profiling engine.
4. Profiling results are stored as machine-readable JSON.
5. Human-readable findings are documented separately.
6. Profiling does not automatically classify every finding as a data-quality
   error.
7. Business interpretation is performed during Data Quality Assessment.
8. Statistics must preserve the analytical meaning of each table.

---

## 3. Dataset-Level Profiling

For every dataset, capture:

- file name
- row count
- column count
- file size
- duplicate row count
- duplicate row percentage

---

## 4. Column-Level Profiling

For every column, capture:

- column name
- data type
- null count
- null percentage
- unique count
- unique percentage

---

## 5. Numeric Profiling

For numeric columns, capture:

- minimum
- maximum
- mean
- median
- standard deviation
- Q1
- Q3
- IQR
- zero count
- negative count

---

## 6. Categorical Profiling

For categorical columns, capture:

- unique count
- top 20 values
- frequency
- percentage of total rows

Only the top 20 categorical values are stored to prevent excessive report
size for high-cardinality columns.

---

## 7. Temporal Profiling

For temporal columns, capture:

- minimum timestamp/date
- maximum timestamp/date
- null count
- invalid/unparseable value count

Raw timestamp columns remain unchanged in the source layer.

---

## 8. Missingness Profiling

Missingness must be reported as both:

- absolute count
- percentage of rows

Missingness is measured, not automatically treated as an error.

---

## 9. Duplicate Profiling

Duplicate rows are measured at the dataset level.

Primary-key uniqueness is handled separately by schema and relationship
analysis.

A duplicate row does not automatically imply a business duplicate.

---

## 10. Outlier Screening

Potential numeric outliers are screened using the IQR method:

lower_bound = Q1 - 1.5 × IQR

upper_bound = Q3 + 1.5 × IQR

The profiler reports:

- lower bound
- upper bound
- potential outlier count
- potential outlier percentage

Outliers are not automatically removed or corrected.

---

## 11. Table-Specific Profiling

### Customers

Profile:

- customer state
- customer city
- customer ZIP prefix
- customer uniqueness

### Orders

Profile:

- order status
- purchase timestamp
- approval timestamp
- carrier delivery timestamp
- customer delivery timestamp
- estimated delivery timestamp

### Order Items

Profile:

- item sequence
- price
- freight value
- product distribution
- seller distribution

### Payments

Profile:

- payment type
- payment installments
- payment value
- payment records per order

### Reviews

Profile:

- review score
- review comment title missingness
- review comment message missingness
- review creation date
- review answer timestamp

### Products

Profile:

- product category
- product name length
- product description length
- product photos quantity
- product weight
- product dimensions

### Sellers

Profile:

- seller state
- seller city
- seller ZIP prefix

### Geolocation

Profile:

- ZIP prefix
- latitude
- longitude
- city
- state

### Category Translation

Profile:

- source category
- translated category
- translation coverage

---

## 12. Output Contract

The profiler must generate:

reports/profiling/data_profile.json

The JSON must contain:

- profiling metadata
- dataset-level statistics
- column-level statistics
- numeric statistics
- categorical statistics
- temporal statistics
- missingness statistics
- outlier screening results
- table-specific profiling results

---

## 13. Reproducibility

The profiler must be executable from the project root using:

python src/profiling/data_profiler.py

The output must be reproducible from the raw datasets using the project's
Python environment.

---

## 14. Quality Gate

Sprint 2.4.1 is considered complete when:

- profiling specification exists
- profiler implementation follows the specification
- JSON output is generated
- JSON is valid
- all nine datasets are profiled
- raw data remains unchanged
- profiling execution completes without errors
- profiling output can be consumed by the subsequent Data Quality phase