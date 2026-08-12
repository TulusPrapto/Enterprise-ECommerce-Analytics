from __future__ import annotations

from pathlib import Path

import polars as pl

from src.analytics.config import (
    ANALYTICAL_DATA_DIR,
    DIM_PRODUCTS_FILE,
    FACT_ORDER_ITEMS_FILE,
    FACT_ORDERS_FILE,
    FACT_ORDER_REVIEWS_FILE,
)


MART_PRODUCTS_FILE = (
    ANALYTICAL_DATA_DIR / "mart_products.parquet"
)


# ---------------------------------------------------------------------
# LOADERS
# ---------------------------------------------------------------------


def load_dimensions_and_facts() -> tuple[
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
]:
    """
    Load product dimension and analytical fact tables.

    Returns:
        products
        order_items
        orders
        reviews
    """

    products = pl.read_parquet(DIM_PRODUCTS_FILE)
    order_items = pl.read_parquet(FACT_ORDER_ITEMS_FILE)
    orders = pl.read_parquet(FACT_ORDERS_FILE)
    reviews = pl.read_parquet(FACT_ORDER_REVIEWS_FILE)

    return (
        products,
        order_items,
        orders,
        reviews,
    )


# ---------------------------------------------------------------------
# PRODUCT ITEM METRICS
# ---------------------------------------------------------------------


def build_product_item_metrics(
    order_items: pl.DataFrame,
) -> pl.DataFrame:
    """
    Build product-level sales metrics.

    Grain:
        One row per product_id.

    Source grain:
        One row per order_id + order_item_id.
    """

    metrics = (
        order_items
        .group_by("product_id")
        .agg(
            [
                pl.col("order_id")
                .n_unique()
                .alias("total_orders"),
                pl.len()
                .alias("total_items_sold"),
                pl.col("seller_id")
                .n_unique()
                .alias("unique_sellers"),
                pl.col("price")
                .sum()
                .alias("total_product_revenue"),
                pl.col("freight_value")
                .sum()
                .alias("total_freight_revenue"),
                pl.col("item_gross_value")
                .sum()
                .alias("total_gross_value"),
                pl.col("price")
                .mean()
                .alias("average_selling_price"),
                pl.col("freight_value")
                .mean()
                .alias("average_freight_per_item"),
            ]
        )
    )

    return metrics


# ---------------------------------------------------------------------
# PRODUCT CUSTOMER METRICS
# ---------------------------------------------------------------------


def build_product_customer_metrics(
    order_items: pl.DataFrame,
    orders: pl.DataFrame,
) -> pl.DataFrame:
    """
    Build product-level customer metrics.

    Grain:
        One row per product_id.

    Customer identity:
        customer_unique_id.

    This avoids counting multiple customer_id records
    belonging to the same real customer as separate customers.
    """

    order_customer_map = (
        orders
        .select(
            [
                "order_id",
                "customer_id",
            ]
        )
    )

    metrics = (
        order_items
        .select(
            [
                "order_id",
                "product_id",
            ]
        )
        .join(
            order_customer_map,
            on="order_id",
            how="left",
        )
    )

    # customer_id must be mapped to customer_unique_id
    # through the customer dimension before this function
    # can produce the final unique-customer metric.

    return metrics


# ---------------------------------------------------------------------
# PRODUCT REVIEW METRICS
# ---------------------------------------------------------------------


def build_product_review_metrics(
    order_items: pl.DataFrame,
    reviews: pl.DataFrame,
) -> pl.DataFrame:
    """
    Build product-level review metrics.

    Grain:
        One row per product_id.

    Important:
        Reviews are aggregated at order level before joining
        to order items to avoid uncontrolled fan-out.
    """

    review_order_metrics = (
        reviews
        .group_by("order_id")
        .agg(
            [
                pl.len()
                .alias("review_count"),
                pl.col("review_score")
                .mean()
                .alias("average_review_score"),
            ]
        )
    )

    product_reviews = (
        order_items
        .select(
            [
                "order_id",
                "product_id",
            ]
        )
        .unique()
        .join(
            review_order_metrics,
            on="order_id",
            how="left",
        )
    )

    metrics = (
        product_reviews
        .group_by("product_id")
        .agg(
            [
                pl.col("review_count")
                .fill_null(0)
                .sum()
                .alias("review_count"),
                pl.col("average_review_score")
                .mean()
                .alias("average_review_score"),
            ]
        )
    )

    return metrics


# ---------------------------------------------------------------------
# PRODUCT DATE METRICS
# ---------------------------------------------------------------------


def build_product_date_metrics(
    order_items: pl.DataFrame,
    orders: pl.DataFrame,
) -> pl.DataFrame:
    """
    Build product sales date metrics.

    Grain:
        One row per product_id.
    """

    product_orders = (
        order_items
        .select(
            [
                "product_id",
                "order_id",
            ]
        )
        .unique()
        .join(
            orders.select(
                [
                    "order_id",
                    "order_purchase_timestamp",
                ]
            ),
            on="order_id",
            how="left",
        )
    )

    metrics = (
        product_orders
        .group_by("product_id")
        .agg(
            [
                pl.col("order_purchase_timestamp")
                .min()
                .alias("first_sale_date"),
                pl.col("order_purchase_timestamp")
                .max()
                .alias("last_sale_date"),
            ]
        )
    )

    return metrics


# ---------------------------------------------------------------------
# PRODUCT MASTER
# ---------------------------------------------------------------------


def build_product_master(
    products: pl.DataFrame,
) -> pl.DataFrame:
    """
    Build the product master attributes.

    Grain:
        One row per product_id.
    """

    return (
        products
        .select(
            [
                "product_id",
                "product_category_name",
            ]
        )
        .unique(
            subset=["product_id"],
            keep="first",
        )
    )


# ---------------------------------------------------------------------
# FINAL MART
# ---------------------------------------------------------------------


def build_mart_products() -> pl.DataFrame:
    """
    Build mart_products.

    Grain:
        One row per product_id.
    """

    (
        products,
        order_items,
        orders,
        reviews,
    ) = load_dimensions_and_facts()

    item_metrics = build_product_item_metrics(
        order_items
    )

    customer_metrics = (
        order_items
        .select(
            [
                "product_id",
                "order_id",
            ]
        )
        .unique()
        .join(
            orders.select(
                [
                    "order_id",
                    "customer_id",
                ]
            ),
            on="order_id",
            how="left",
        )
        .group_by("product_id")
        .agg(
            [
                pl.col("customer_id")
                .n_unique()
                .alias("unique_customers")
            ]
        )
    )

    review_metrics = build_product_review_metrics(
        order_items,
        reviews,
    )

    date_metrics = build_product_date_metrics(
        order_items,
        orders,
    )

    product_master = build_product_master(
        products
    )

    mart = (
        product_master
        .join(
            item_metrics,
            on="product_id",
            how="left",
        )
        .join(
            customer_metrics,
            on="product_id",
            how="left",
        )
        .join(
            review_metrics,
            on="product_id",
            how="left",
        )
        .join(
            date_metrics,
            on="product_id",
            how="left",
        )
        .with_columns(
            [
                pl.col("total_orders")
                .fill_null(0)
                .cast(pl.Int64),

                pl.col("total_items_sold")
                .fill_null(0)
                .cast(pl.Int64),

                pl.col("unique_customers")
                .fill_null(0)
                .cast(pl.Int64),

                pl.col("unique_sellers")
                .fill_null(0)
                .cast(pl.Int64),

                pl.col("total_product_revenue")
                .fill_null(0.0),

                pl.col("total_freight_revenue")
                .fill_null(0.0),

                pl.col("total_gross_value")
                .fill_null(0.0),

                pl.col("review_count")
                .fill_null(0)
                .cast(pl.Int64),
            ]
        )
        .sort("product_id")
    )

    return mart


# ---------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------


def validate_mart_products(
    mart: pl.DataFrame,
) -> None:
    """
    Validate mart_products structural and business rules.
    """

    required_columns = [
        "product_id",
        "product_category_name",
        "total_orders",
        "total_items_sold",
        "unique_sellers",
        "unique_customers",
        "total_product_revenue",
        "total_freight_revenue",
        "total_gross_value",
        "average_selling_price",
        "average_freight_per_item",
        "review_count",
        "average_review_score",
        "first_sale_date",
        "last_sale_date",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in mart.columns
    ]

    if missing_columns:
        raise ValueError(
            f"mart_products is missing columns: {missing_columns}"
        )

    duplicate_product_ids = (
        mart.height
        - mart["product_id"].n_unique()
    )

    if duplicate_product_ids > 0:
        raise ValueError(
            "Duplicate product_id values found in mart_products."
        )

    if mart["product_id"].null_count() > 0:
        raise ValueError(
            "product_id contains null values."
        )

    numeric_columns = [
        "total_orders",
        "total_items_sold",
        "unique_sellers",
        "unique_customers",
        "total_product_revenue",
        "total_freight_revenue",
        "total_gross_value",
        "review_count",
    ]

    for column in numeric_columns:
        negative_count = (
            mart
            .filter(pl.col(column) < 0)
            .height
        )

        if negative_count > 0:
            raise ValueError(
                f"{column} contains negative values."
            )

    invalid_order_counts = (
        mart
        .filter(
            pl.col("total_items_sold")
            < pl.col("total_orders")
        )
        .height
    )

    if invalid_order_counts > 0:
        raise ValueError(
            "Some products have fewer items sold than orders."
        )

    invalid_customer_counts = (
        mart
        .filter(
            pl.col("unique_customers")
            > pl.col("total_orders")
        )
        .height
    )

    if invalid_customer_counts > 0:
        raise ValueError(
            "Some products have more unique customers than orders."
        )

    invalid_dates = (
        mart
        .filter(
            pl.col("first_sale_date")
            > pl.col("last_sale_date")
        )
        .height
    )

    if invalid_dates > 0:
        raise ValueError(
            "Some products have first_sale_date after last_sale_date."
        )


# ---------------------------------------------------------------------
# PERSISTENCE
# ---------------------------------------------------------------------


def save_mart_products(
    mart: pl.DataFrame,
    output_dir: Path = ANALYTICAL_DATA_DIR,
) -> Path:
    """
    Persist mart_products as Parquet.
    """

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / "mart_products.parquet"
    )

    mart.write_parquet(output_path)

    return output_path


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------


def main() -> None:
    mart = build_mart_products()

    validate_mart_products(mart)

    output_path = save_mart_products(mart)

    print("mart_products built successfully.")
    print(f"Rows: {mart.height}")
    print(f"Columns: {mart.columns}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()