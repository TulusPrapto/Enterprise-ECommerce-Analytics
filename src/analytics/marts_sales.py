from __future__ import annotations

from pathlib import Path

import polars as pl

from src.analytics.config import (
    ANALYTICAL_DATA_DIR,
)


MART_SALES_FILE = ANALYTICAL_DATA_DIR / "mart_sales.parquet"

FACT_ORDERS_FILE = ANALYTICAL_DATA_DIR / "fact_orders.parquet"
FACT_ORDER_ITEMS_FILE = ANALYTICAL_DATA_DIR / "fact_order_items.parquet"
FACT_PAYMENTS_FILE = ANALYTICAL_DATA_DIR / "fact_order_payments.parquet"
FACT_REVIEWS_FILE = ANALYTICAL_DATA_DIR / "fact_order_reviews.parquet"
DIM_CUSTOMERS_FILE = ANALYTICAL_DATA_DIR / "dim_customers.parquet"


# ---------------------------------------------------------------------
# LOAD
# ---------------------------------------------------------------------

def load_sources() -> tuple[
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
]:
    """
    Load the analytical source tables required by mart_sales.
    """

    paths = [
        FACT_ORDERS_FILE,
        FACT_ORDER_ITEMS_FILE,
        FACT_PAYMENTS_FILE,
        FACT_REVIEWS_FILE,
        DIM_CUSTOMERS_FILE,
    ]

    missing = [
        path
        for path in paths
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            "Required analytical source files are missing:\n"
            + "\n".join(str(path) for path in missing)
        )

    return (
        pl.read_parquet(FACT_ORDERS_FILE),
        pl.read_parquet(FACT_ORDER_ITEMS_FILE),
        pl.read_parquet(FACT_PAYMENTS_FILE),
        pl.read_parquet(FACT_REVIEWS_FILE),
        pl.read_parquet(DIM_CUSTOMERS_FILE),
    )


# ---------------------------------------------------------------------
# AGGREGATIONS
# ---------------------------------------------------------------------

def aggregate_items(
    fact_order_items: pl.DataFrame,
) -> pl.DataFrame:
    """
    Aggregate order items to order grain.

    Grain:
        One row per order_id.
    """

    return (
        fact_order_items
        .group_by("order_id")
        .agg(
            [
                pl.len().alias("item_count"),
                pl.col("price")
                .sum()
                .alias("item_price_total"),
                pl.col("freight_value")
                .sum()
                .alias("freight_total"),
                pl.col("item_gross_value")
                .sum()
                .alias("order_item_gross"),
            ]
        )
    )


def aggregate_payments(
    fact_payments: pl.DataFrame,
) -> pl.DataFrame:
    """
    Aggregate payments to order grain.

    Grain:
        One row per order_id.
    """

    return (
        fact_payments
        .group_by("order_id")
        .agg(
            [
                pl.len().alias("payment_record_count"),
                pl.col("payment_value")
                .sum()
                .alias("payment_total"),
            ]
        )
    )


def aggregate_reviews(
    fact_reviews: pl.DataFrame,
) -> pl.DataFrame:
    """
    Aggregate reviews to order grain.

    Grain:
        One row per order_id.

    review_id is intentionally NOT used as the grouping key
    because the source permits repeated review_id values across
    different orders.
    """

    return (
        fact_reviews
        .group_by("order_id")
        .agg(
            [
                pl.len().alias("review_count"),
                pl.col("review_score")
                .mean()
                .alias("average_review_score"),
            ]
        )
    )


# ---------------------------------------------------------------------
# BUILD MART
# ---------------------------------------------------------------------

def build_mart_sales() -> pl.DataFrame:
    """
    Build the sales analytical mart.

    Grain:
        One row per order_id.

    Fan-out protection:
        Items, payments, and reviews are independently aggregated
        to order grain before joining to fact_orders.
    """

    (
        fact_orders,
        fact_order_items,
        fact_payments,
        fact_reviews,
        dim_customers,
    ) = load_sources()

    items = aggregate_items(
        fact_order_items
    )

    payments = aggregate_payments(
        fact_payments
    )

    reviews = aggregate_reviews(
        fact_reviews
    )

    customer_attributes = dim_customers.select(
        [
            "customer_id",
            "customer_unique_id",
            "customer_city",
            "customer_state",
        ]
    )

    mart = (
        fact_orders
        .join(
            customer_attributes,
            on="customer_id",
            how="left",
        )
        .join(
            items,
            on="order_id",
            how="left",
        )
        .join(
            payments,
            on="order_id",
            how="left",
        )
        .join(
            reviews,
            on="order_id",
            how="left",
        )
        .with_columns(
            [
                pl.col("item_count")
                .fill_null(0),

                pl.col("item_price_total")
                .fill_null(0.0),

                pl.col("freight_total")
                .fill_null(0.0),

                pl.col("order_item_gross")
                .fill_null(0.0),

                pl.col("payment_record_count")
                .fill_null(0),

                pl.col("payment_total")
                .fill_null(0.0),

                pl.col("review_count")
                .fill_null(0),
            ]
        )
    )

    return mart


# ---------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------

def validate_mart_sales(
    mart: pl.DataFrame,
) -> None:
    """
    Validate mart_sales.

    Expected grain:
        One row per order_id.
    """

    required_columns = [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "item_count",
        "item_price_total",
        "freight_total",
        "order_item_gross",
        "payment_record_count",
        "payment_total",
        "review_count",
        "average_review_score",
        "customer_unique_id",
        "customer_city",
        "customer_state",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in mart.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing mart_sales columns: {missing_columns}"
        )

    if mart.height == 0:
        raise ValueError(
            "mart_sales contains no rows."
        )

    # ---------------------------------------------------------
    # Grain
    # ---------------------------------------------------------

    duplicate_orders = (
        mart.height
        - mart.unique(
            subset=["order_id"]
        ).height
    )

    if duplicate_orders != 0:
        raise ValueError(
            f"mart_sales contains {duplicate_orders} "
            "duplicate order_id rows."
        )

    # ---------------------------------------------------------
    # Required keys
    # ---------------------------------------------------------

    for column in [
        "order_id",
        "customer_id",
    ]:
        null_count = mart[column].null_count()

        if null_count != 0:
            raise ValueError(
                f"{column} contains {null_count} null values."
            )

    # ---------------------------------------------------------
    # Non-negative measures
    # ---------------------------------------------------------

    for column in [
        "item_count",
        "item_price_total",
        "freight_total",
        "order_item_gross",
        "payment_record_count",
        "payment_total",
        "review_count",
    ]:
        negative_count = (
            mart
            .filter(pl.col(column) < 0)
            .height
        )

        if negative_count != 0:
            raise ValueError(
                f"{column} contains "
                f"{negative_count} negative values."
            )

    # ---------------------------------------------------------
    # Review score
    # ---------------------------------------------------------

    invalid_review_scores = (
        mart
        .filter(
            pl.col("average_review_score").is_not_null()
            & (
                (pl.col("average_review_score") < 1)
                | (pl.col("average_review_score") > 5)
            )
        )
        .height
    )

    if invalid_review_scores != 0:
        raise ValueError(
            "Invalid average_review_score values found: "
            f"{invalid_review_scores}"
        )

    # ---------------------------------------------------------
    # Gross-value reconciliation
    # ---------------------------------------------------------

    incorrect_gross = (
        mart
        .filter(
            (
                pl.col("order_item_gross")
                - (
                    pl.col("item_price_total")
                    + pl.col("freight_total")
                )
            ).abs()
            > 0.01
        )
        .height
    )

    if incorrect_gross != 0:
        raise ValueError(
            "order_item_gross does not reconcile with "
            "item_price_total + freight_total for "
            f"{incorrect_gross} orders."
        )


# ---------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------

def save_mart_sales(
    mart: pl.DataFrame,
) -> Path:
    """
    Save mart_sales as Parquet.
    """

    ANALYTICAL_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    mart.write_parquet(
        MART_SALES_FILE
    )

    return MART_SALES_FILE


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main() -> None:
    mart = build_mart_sales()

    validate_mart_sales(
        mart
    )

    output_path = save_mart_sales(
        mart
    )

    print("mart_sales built successfully.")
    print(f"Rows: {mart.height}")
    print(f"Columns: {mart.columns}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()