from pathlib import Path

from src.cleaning.config import PROCESSED_DATA_DIR


# ---------------------------------------------------------------------
# ANALYTICAL DATA DIRECTORIES
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ANALYTICAL_DATA_DIR = PROJECT_ROOT / "data" / "analytical"

ANALYTICAL_OUTPUT_DIR = PROJECT_ROOT / "reports" / "analytics"


# ---------------------------------------------------------------------
# SOURCE DATA
# ---------------------------------------------------------------------

SOURCE_DATA_DIR = PROCESSED_DATA_DIR


# ---------------------------------------------------------------------
# SOURCE DATASETS
# ---------------------------------------------------------------------

ORDERS_FILE = SOURCE_DATA_DIR / "olist_orders_dataset.csv"
ORDER_ITEMS_FILE = SOURCE_DATA_DIR / "olist_order_items_dataset.csv"
PAYMENTS_FILE = SOURCE_DATA_DIR / "olist_order_payments_dataset.csv"
REVIEWS_FILE = SOURCE_DATA_DIR / "olist_order_reviews_dataset.csv"
PRODUCTS_FILE = SOURCE_DATA_DIR / "olist_products_dataset.csv"
SELLERS_FILE = SOURCE_DATA_DIR / "olist_sellers_dataset.csv"
CUSTOMERS_FILE = SOURCE_DATA_DIR / "olist_customers_dataset.csv"
GEOLOCATION_FILE = SOURCE_DATA_DIR / "olist_geolocation_dataset.csv"


# ---------------------------------------------------------------------
# ANALYTICAL OUTPUTS
# ---------------------------------------------------------------------

FACT_ORDERS_FILE = ANALYTICAL_DATA_DIR / "fact_orders.parquet"
FACT_ORDER_ITEMS_FILE = ANALYTICAL_DATA_DIR / "fact_order_items.parquet"
FACT_PAYMENTS_FILE = ANALYTICAL_DATA_DIR / "fact_order_payments.parquet"
FACT_ORDER_REVIEWS_FILE = ANALYTICAL_DATA_DIR / "fact_order_reviews.parquet"

DIM_CUSTOMERS_FILE = ANALYTICAL_DATA_DIR / "dim_customers.parquet"
DIM_PRODUCTS_FILE = ANALYTICAL_DATA_DIR / "dim_products.parquet"
DIM_SELLERS_FILE = ANALYTICAL_DATA_DIR / "dim_sellers.parquet"

MART_SALES_FILE = ANALYTICAL_DATA_DIR / "mart_sales.parquet"
MART_CUSTOMERS_FILE = ANALYTICAL_DATA_DIR / "mart_customers.parquet"
MART_PRODUCTS_FILE = ANALYTICAL_DATA_DIR / "mart_products.parquet"
MART_LOGISTICS_FILE = ANALYTICAL_DATA_DIR / "mart_logistics.parquet"


# ---------------------------------------------------------------------
# REPORTS
# ---------------------------------------------------------------------

ANALYTICAL_MODEL_REPORT = ANALYTICAL_OUTPUT_DIR / "analytical_model_report.json"