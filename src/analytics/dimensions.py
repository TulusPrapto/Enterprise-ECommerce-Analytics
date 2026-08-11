from pathlib import Path

import polars as pl

from src.analytics.config import (
    ANALYTICAL_DATA_DIR,
    CUSTOMERS_FILE,
    PRODUCTS_FILE,
    SELLERS_FILE,
)


# =============================================================
# CUSTOMER DIMENSION
# =============================================================

CUSTOMER_COLUMNS = [
    "customer_id",
    "customer_unique_id",
    "customer_zip_code_prefix",
    "customer_city",
    "customer_state",
]


def build_dim_customers() -> pl.DataFrame:
    """
    Build the customer dimension from the processed customer dataset.

    Grain:
        One row per customer_id.
    """

    customers = pl.read_csv(CUSTOMERS_FILE)

    dim_customers = (
        customers
        .select(CUSTOMER_COLUMNS)
        .unique(subset=["customer_id"], keep="first")
        .sort("customer_id")
    )

    return dim_customers


def validate_dim_customers(
    df: pl.DataFrame,
) -> None:
    """
    Validate the customer dimension before persistence.
    """

    required_columns = set(CUSTOMER_COLUMNS)

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"dim_customers is missing columns: {sorted(missing_columns)}"
        )

    duplicate_customer_ids = (
        df
        .group_by("customer_id")
        .len()
        .filter(pl.col("len") > 1)
    )

    if duplicate_customer_ids.height > 0:
        raise ValueError(
            "dim_customers contains duplicate customer_id values."
        )

    if df["customer_id"].null_count() > 0:
        raise ValueError(
            "dim_customers contains null customer_id values."
        )


def save_dim_customers(
    df: pl.DataFrame,
    output_dir: Path = ANALYTICAL_DATA_DIR,
) -> Path:
    """
    Persist dim_customers as Parquet.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "dim_customers.parquet"

    df.write_parquet(output_path)

    return output_path


# =============================================================
# PRODUCT DIMENSION
# =============================================================

PRODUCT_COLUMNS = [
    "product_id",
    "product_category_name",
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
]


def build_dim_products() -> pl.DataFrame:
    """
    Build the product dimension from the processed product dataset.

    Grain:
        One row per product_id.
    """

    products = pl.read_csv(PRODUCTS_FILE)

    dim_products = (
        products
        .select(PRODUCT_COLUMNS)
        .unique(subset=["product_id"], keep="first")
        .sort("product_id")
    )

    return dim_products


def validate_dim_products(
    df: pl.DataFrame,
) -> None:
    """
    Validate the product dimension before persistence.
    """

    required_columns = set(PRODUCT_COLUMNS)

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"dim_products is missing columns: {sorted(missing_columns)}"
        )

    duplicate_product_ids = (
        df
        .group_by("product_id")
        .len()
        .filter(pl.col("len") > 1)
    )

    if duplicate_product_ids.height > 0:
        raise ValueError(
            "dim_products contains duplicate product_id values."
        )

    if df["product_id"].null_count() > 0:
        raise ValueError(
            "dim_products contains null product_id values."
        )


def save_dim_products(
    df: pl.DataFrame,
    output_dir: Path = ANALYTICAL_DATA_DIR,
) -> Path:
    """
    Persist dim_products as Parquet.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "dim_products.parquet"

    df.write_parquet(output_path)

    return output_path


# =============================================================
# SELLER DIMENSION
# =============================================================

SELLER_COLUMNS = [
    "seller_id",
    "seller_zip_code_prefix",
    "seller_city",
    "seller_state",
]


def build_dim_sellers() -> pl.DataFrame:
    """
    Build the seller dimension from the processed seller dataset.

    Grain:
        One row per seller_id.
    """

    sellers = pl.read_csv(SELLERS_FILE)

    dim_sellers = (
        sellers
        .select(SELLER_COLUMNS)
        .unique(subset=["seller_id"], keep="first")
        .sort("seller_id")
    )

    return dim_sellers


def validate_dim_sellers(
    df: pl.DataFrame,
) -> None:
    """
    Validate the seller dimension before persistence.
    """

    required_columns = set(SELLER_COLUMNS)

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"dim_sellers is missing columns: {sorted(missing_columns)}"
        )

    duplicate_seller_ids = (
        df
        .group_by("seller_id")
        .len()
        .filter(pl.col("len") > 1)
    )

    if duplicate_seller_ids.height > 0:
        raise ValueError(
            "dim_sellers contains duplicate seller_id values."
        )

    if df["seller_id"].null_count() > 0:
        raise ValueError(
            "dim_sellers contains null seller_id values."
        )


def save_dim_sellers(
    df: pl.DataFrame,
    output_dir: Path = ANALYTICAL_DATA_DIR,
) -> Path:
    """
    Persist dim_sellers as Parquet.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "dim_sellers.parquet"

    df.write_parquet(output_path)

    return output_path


# =============================================================
# MAIN
# =============================================================

def main() -> None:
    # ---------------------------------------------------------
    # Customer dimension
    # ---------------------------------------------------------

    dim_customers = build_dim_customers()

    validate_dim_customers(dim_customers)

    customer_output = save_dim_customers(dim_customers)

    print("dim_customers built successfully.")
    print(f"Rows: {dim_customers.height}")
    print(f"Columns: {dim_customers.columns}")
    print(f"Output: {customer_output}")

    # ---------------------------------------------------------
    # Product dimension
    # ---------------------------------------------------------

    dim_products = build_dim_products()

    validate_dim_products(dim_products)

    product_output = save_dim_products(dim_products)

    print("dim_products built successfully.")
    print(f"Rows: {dim_products.height}")
    print(f"Columns: {dim_products.columns}")
    print(f"Output: {product_output}")

    # ---------------------------------------------------------
    # Seller dimension
    # ---------------------------------------------------------

    dim_sellers = build_dim_sellers()

    validate_dim_sellers(dim_sellers)

    seller_output = save_dim_sellers(dim_sellers)

    print("dim_sellers built successfully.")
    print(f"Rows: {dim_sellers.height}")
    print(f"Columns: {dim_sellers.columns}")
    print(f"Output: {seller_output}")


if __name__ == "__main__":
    main()