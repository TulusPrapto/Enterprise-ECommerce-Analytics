# Sprint 01 — Environment Setup

## Objective
Menyiapkan lingkungan kerja untuk proyek **Enterprise E-Commerce Analytics Platform** sehingga seluruh pipeline dapat dijalankan secara reproducible.

---

## Tools Used

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Data processing & automation |
| DuckDB | latest | Analytical database |
| Polars | latest | High-performance DataFrame |
| PyArrow | latest | Parquet support |
| Pandas | latest | Compatibility |
| Plotly | latest | Interactive visualization |
| Matplotlib | latest | Static visualization |
| Jupyter | latest | Exploration & notebooks |
| Git | latest | Version control |
| Power BI | latest | Dashboard |

---

## Project Structure

```text
Enterprise-ECommerce-Analytics/
├── data/
├── database/
├── docs/
├── sql/
├── python/
├── notebooks/
├── reports/
├── dashboard/
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Environment Setup

### Create virtual environment

```bash
python -m venv .venv
```

### Activate

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install duckdb polars pandas pyarrow matplotlib plotly openpyxl jupyter notebook ipykernel scipy numpy
```

### Export requirements

```bash
pip freeze > requirements.txt
```

---

## Validation

```python
import duckdb
import polars
import pyarrow
import pandas

print("Environment OK!")
```

Expected output:

```text
Environment OK!
```

---

## Git Initialization

```bash
git init
git add .
git commit -m "Initialize project structure"
```

---

## Outcome

- Environment ready
- Dependencies installed
- Project structure created
- Git repository initialized
- Reproducible setup documented
