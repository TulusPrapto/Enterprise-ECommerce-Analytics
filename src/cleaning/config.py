from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ============================================================
# DATA DIRECTORIES
# ============================================================

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


# ============================================================
# REPORT DIRECTORIES
# ============================================================

CLEANING_REPORT_DIR = PROJECT_ROOT / "reports" / "cleaning"


# ============================================================
# DATASET REGISTRY
# ============================================================

DATASETS = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]


# ============================================================
# OUTPUT CONFIGURATION
# ============================================================

OUTPUT_FORMAT = "parquet"


# ============================================================
# PIPELINE BEHAVIOR
# ============================================================

PRESERVE_ROW_COUNT = True
FAIL_ON_CRITICAL_VALIDATION = True