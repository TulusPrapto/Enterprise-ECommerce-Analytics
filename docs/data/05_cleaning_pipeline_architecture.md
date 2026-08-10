# Cleaning Pipeline Architecture

## Document Metadata

| Field          | Value                                            |
| -------------- | ------------------------------------------------ |
| Document Title | Cleaning Pipeline Architecture                   |
| Project        | Enterprise E-Commerce Analytics                  |
| Document Owner | Tulus Prapto                                     |
| Phase          | Sprint 3.2                                       |
| Previous Phase | Sprint 3.1 — Cleaning & Standardization Strategy |
| Primary Tool   | Python + Polars                                  |
| Output Format  | Parquet                                          |
| Status         | Ready for Implementation                         |

---

# 1. Architecture Objective

Cleaning pipeline dirancang untuk mengubah raw CSV menjadi standardized analytical data tanpa memodifikasi raw source.

Pipeline harus reproducible, modular, auditable, dan dapat digunakan kembali.

---

# 2. Directory Architecture

```text
data/
├── raw/
└── processed/

src/
└── cleaning/
    ├── __init__.py
    ├── config.py
    ├── cleaners.py
    ├── validators.py
    └── pipeline.py

reports/
└── cleaning/
    ├── cleaning_summary.json
    └── validation_report.json
```

---

# 3. Processing Flow

```text
Raw CSV
   │
   ▼
Load
   │
   ▼
Schema Inspection
   │
   ▼
Type Standardization
   │
   ▼
Business-safe Cleaning
   │
   ▼
Validation
   │
   ▼
Write Parquet
   │
   ▼
Post-write Validation
   │
   ▼
Cleaning Report
```

---

# 4. Module Responsibilities

## config.py

Responsible for:

* path configuration;
* dataset registry;
* output configuration;
* pipeline constants.

---

## cleaners.py

Responsible for:

* loading datasets;
* type conversion;
* datetime conversion;
* text standardization;
* category normalization;
* business-safe transformations.

The module must not modify raw files.

---

## validators.py

Responsible for:

* schema validation;
* row-count validation;
* null validation;
* identifier validation;
* numeric validation;
* business-rule validation.

---

## pipeline.py

Responsible for orchestration:

```text
load
→ clean
→ validate
→ write
→ validate output
→ report
```

---

# 5. Data Preservation Rules

Raw data is immutable.

The pipeline must not:

* overwrite raw CSV;
* delete raw records;
* invent missing values;
* invent translations;
* silently drop rows;
* silently change identifiers.

---

# 6. Grain Preservation

Each dataset must retain its intended analytical grain.

Examples:

```text
orders
1 row = 1 order

order_items
1 row = 1 order item

order_payments
1 row = 1 payment record
```

Transformations that change grain must be implemented separately from the cleaning layer.

---

# 7. Output Contract

Each processed dataset must:

* be written as Parquet;
* have deterministic schema;
* preserve identifiers;
* preserve valid NULL values;
* be readable by Polars;
* be readable by DuckDB;
* have validation results recorded.

---

# 8. Reporting Contract

The pipeline must generate machine-readable reports.

## cleaning_summary.json

Should contain:

* dataset name;
* input row count;
* output row count;
* input columns;
* output columns;
* transformations applied;
* execution status.

## validation_report.json

Should contain:

* validation checks;
* pass/fail status;
* detected anomalies;
* row-count comparison;
* schema validation;
* null validation;
* business-rule validation.

---

# 9. Failure Policy

If a critical validation fails:

```text
Validation FAILED
       ↓
Do NOT publish output
       ↓
Record error
       ↓
Fix pipeline
       ↓
Run again
```

The pipeline must not silently continue after a critical validation failure.

---

# 10. Reproducibility

The same raw input and same pipeline version should produce deterministic output.

All transformations must be implemented in source-controlled Python code.

---

# 11. Future Integration

After cleaning validation passes:

```text
Parquet
   ↓
DuckDB
   ↓
SQL transformations
   ↓
Analytical marts
   ↓
Power BI / Python analytics
```

DuckDB is therefore a downstream analytical layer and not part of the raw-data cleaning process.

---

# 12. Acceptance Criteria

Sprint 3.2 is complete when:

1. Cleaning directories exist.
2. Python cleaning package exists.
3. Cleaning modules have defined responsibilities.
4. Raw data preservation rule is documented.
5. Grain preservation is documented.
6. Validation is treated as a mandatory pipeline stage.
7. Parquet is defined as the processed-data output.
8. DuckDB is explicitly downstream of validated Parquet.
9. Cleaning reports are defined.
10. Failure behavior is defined.
