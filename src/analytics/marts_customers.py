from __future__ import annotations

from pathlib import Path

import polars as pl

from src.analytics.config import (
    ANALYTICAL_DATA_DIR,
    DIM_CUSTOMERS_FILE,
    FACT_ORDERS_FILE,
    FACT_ORDER_ITEMS_FILE,
    FACT_PAYMENTS_FILE,
)


MART_CUSTOMERS_FILE = (
    ANALYTICAL_DATA_DIR / "mart_customers.parquet"
)

FACT_REVIEWS_FILE = (
    ANALYTICAL_DATA_DIR / "fact_order_reviews.parquet"
)

# ---------------------------------------------------------------------
# LOADERS
# ---------------------------------------------------------------------


def load_dimensions_and_facts() -> tuple[
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
]:
    """
    Load the customer dimension and analytical fact tables.

    Returns:
        customers
        orders
        order_items
        payments
        reviews
    """

    customers = pl.read_parquet(DIM_CUSTOMERS_FILE)
    orders = pl.read_parquet(FACT_ORDERS_FILE)
    order_items = pl.read_parquet(FACT_ORDER_ITEMS_FILE)
    payments = pl.read_parquet(FACT_PAYMENTS_FILE)
    reviews = pl.read_parquet(FACT_REVIEWS_FILE)

    return (
        customers,
        orders,
        order_items,
        payments,
        reviews,
    )


# ---------------------------------------------------------------------
# CUSTOMER MAPPING
# ---------------------------------------------------------------------


def build_order_customer_map(
    customers: pl.DataFrame,
    orders: pl.DataFrame,
) -> pl.DataFrame:
    """
    Build the mapping between order_id and customer_unique_id.

    Grain:
        One row per order_id.

    This mapping is required because the item, payment,
    and review facts use order_id rather than
    customer_unique_id.
    """

    customer_map = orders.select(
        [
            "order_id",
            "customer_id",
        ]
    ).join(
        customers.select(
            [
                "customer_id",
                "customer_unique_id",
            ]
        ),
        on="customer_id",
        how="left",
    )

    if customer_map.height != orders.height:
        raise ValueError(
            "Order/customer mapping changed the order row count."
        )

    if (
        customer_map["customer_unique_id"]
        .null_count()
        != 0
    ):
        raise ValueError(
            "Some orders could not be mapped to "
            "customer_unique_id."
        )

    duplicate_orders = (
        customer_map.height
        - customer_map.unique(
            subset=["order_id"]
        ).height
    )

    if duplicate_orders != 0:
        raise ValueError(
            "Order/customer mapping contains duplicate "
            f"order_id values: {duplicate_orders}"
        )

    return customer_map


# ---------------------------------------------------------------------
# ORDER METRICS
# ---------------------------------------------------------------------


def build_customer_order_metrics(
    customers: pl.DataFrame,
    orders: pl.DataFrame,
) -> pl.DataFrame:
    """
    Build customer-level order metrics.

    Grain:
        One row per customer_unique_id.
    """

    order_customer_map = build_order_customer_map(
        customers,
        orders,
    )

    order_metrics = (
        order_customer_map
        .join(
            orders.select(
                [
                    "order_id",
                    "order_status",
                    "order_purchase_timestamp",
                ]
            ),
            on="order_id",
            how="left",
        )
        .group_by("customer_unique_id")
        .agg(
            [
                pl.len().alias("total_orders"),
                (
                    pl.col("order_status") == "delivered"
                )
                .sum()
                .alias("delivered_orders"),
                (
                    pl.col("order_status") == "canceled"
                )
                .sum()
                .alias("canceled_orders"),
                (
                    ~pl.col("order_status").is_in(
                        ["delivered", "canceled"]
                    )
                )
                .sum()
                .alias("other_orders"),
                pl.col(
                    "order_purchase_timestamp"
                ).min().alias("first_order_date"),
                pl.col(
                    "order_purchase_timestamp"
                ).max().alias("last_order_date"),
            ]
        )
        .with_columns(
            (
                pl.col("last_order_date")
                - pl.col("first_order_date")
            )
            .dt.total_days()
            .cast(pl.Int64)
            .alias("customer_lifetime_days"),
            (
                pl.col("total_orders") > 1
            ).alias("is_repeat_customer"),
        )
    )

    return order_metrics


# ---------------------------------------------------------------------
# ITEM METRICS
# ---------------------------------------------------------------------


def build_customer_item_metrics(
    customers: pl.DataFrame,
    orders: pl.DataFrame,
    order_items: pl.DataFrame,
) -> pl.DataFrame:
    """
    Build customer-level order-item metrics.

    Grain:
        One row per customer_unique_id.
    """

    order_customer_map = build_order_customer_map(
        customers,
        orders,
    )

    item_metrics = (
        order_items
        .join(
            order_customer_map,
            on="order_id",
            how="inner",
        )
        .group_by("customer_unique_id")
        .agg(
            [
                pl.col("order_item_id")
                .len()
                .alias("total_items"),
                pl.col("price")
                .sum()
                .alias("total_product_spend"),
                pl.col("freight_value")
                .sum()
                .alias("total_freight_spend"),
                pl.col("item_gross_value")
                .sum()
                .alias("total_item_gross_value"),
            ]
        )
    )

    return item_metrics


# ---------------------------------------------------------------------
# PAYMENT METRICS
# ---------------------------------------------------------------------


def build_customer_payment_metrics(
    customers: pl.DataFrame,
    orders: pl.DataFrame,
    payments: pl.DataFrame,
) -> pl.DataFrame:
    """
    Build customer-level payment metrics.

    Grain:
        One row per customer_unique_id.
    """

    order_customer_map = build_order_customer_map(
        customers,
        orders,
    )

    payment_metrics = (
        payments
        .join(
            order_customer_map,
            on="order_id",
            how="inner",
        )
        .group_by("customer_unique_id")
        .agg(
            [
                pl.len().alias(
                    "payment_record_count"
                ),
                pl.col("payment_value")
                .sum()
                .alias("total_payment"),
            ]
        )
    )

    return payment_metrics


# ---------------------------------------------------------------------
# REVIEW METRICS
# ---------------------------------------------------------------------


def build_customer_review_metrics(
    customers: pl.DataFrame,
    orders: pl.DataFrame,
    reviews: pl.DataFrame,
) -> pl.DataFrame:
    """
    Build customer-level review metrics.

    Grain:
        One row per customer_unique_id.
    """

    order_customer_map = build_order_customer_map(
        customers,
        orders,
    )

    review_metrics = (
        reviews
        .join(
            order_customer_map,
            on="order_id",
            how="inner",
        )
        .group_by("customer_unique_id")
        .agg(
            [
                pl.len().alias("review_count"),
                pl.col("review_score")
                .mean()
                .alias("average_review_score"),
            ]
        )
    )

    return review_metrics


# ---------------------------------------------------------------------
# MART BUILD
# ---------------------------------------------------------------------

def build_customer_master(
    customers: pl.DataFrame,
    orders: pl.DataFrame,
) -> pl.DataFrame:
    """
    Build one-row-per-customer master attributes.

    Grain:
        One row per customer_unique_id.

    Business rules:
        - customer_id_count = number of historical customer_id records
        - customer_city/state = location from the latest order
    """

    order_customer = (
        orders
        .select(
            [
                "order_id",
                "customer_id",
                "order_purchase_timestamp",
            ]
        )
        .join(
            customers.select(
                [
                    "customer_id",
                    "customer_unique_id",
                    "customer_city",
                    "customer_state",
                ]
            ),
            on="customer_id",
            how="left",
        )
    )

    latest_customer_location = (
        order_customer
        .sort(
            [
                "customer_unique_id",
                "order_purchase_timestamp",
            ]
        )
        .group_by("customer_unique_id")
        .agg(
            [
                pl.col("customer_city")
                .last()
                .alias("customer_city"),

                pl.col("customer_state")
                .last()
                .alias("customer_state"),
            ]
        )
    )

    customer_master = (
        customers
        .group_by("customer_unique_id")
        .agg(
            pl.col("customer_id")
            .n_unique()
            .alias("customer_id_count")
        )
        .join(
            latest_customer_location,
            on="customer_unique_id",
            how="left",
        )
    )

    return customer_master

def build_mart_customers() -> pl.DataFrame:
    """
    Build mart_customers.

    Grain:
        One row per customer_unique_id
        represented in fact_orders.
    """

    (
        customers,
        orders,
        order_items,
        payments,
        reviews,
    ) = load_dimensions_and_facts()

    order_metrics = build_customer_order_metrics(
        customers,
        orders,
    )

    item_metrics = build_customer_item_metrics(
        customers,
        orders,
        order_items,
    )

    payment_metrics = build_customer_payment_metrics(
        customers,
        orders,
        payments,
    )

    review_metrics = build_customer_review_metrics(
        customers,
        orders,
        reviews,
    )

    customer_attributes = build_customer_master(
        customers,
        orders,
    )

    mart = (
        customer_attributes
        .join(
            order_metrics,
            on="customer_unique_id",
            how="left",
        )
        .join(
            item_metrics,
            on="customer_unique_id",
            how="left",
        )
        .join(
            payment_metrics,
            on="customer_unique_id",
            how="left",
        )
        .join(
            review_metrics,
            on="customer_unique_id",
            how="left",
        )
        .with_columns(
            [
                pl.col("total_items")
                .fill_null(0)
                .cast(pl.Int64),

                pl.col("total_product_spend")
                .fill_null(0.0),

                pl.col("total_freight_spend")
                .fill_null(0.0),

                pl.col("total_item_gross_value")
                .fill_null(0.0),

                pl.col("payment_record_count")
                .fill_null(0)
                .cast(pl.Int64),

                pl.col("total_payment")
                .fill_null(0.0),

                pl.col("review_count")
                .fill_null(0)
                .cast(pl.Int64),
            ]
        )
        .with_columns(
            pl.when(
                pl.col("total_orders") > 0
            )
            .then(
                pl.col("total_item_gross_value")
                / pl.col("total_orders")
            )
            .otherwise(None)
            .alias("average_order_value")
        )
        .select(
            [
                "customer_unique_id",
                "customer_city",
                "customer_state",
                "total_orders",
                "delivered_orders",
                "canceled_orders",
                "other_orders",
                "total_items",
                "total_product_spend",
                "total_freight_spend",
                "total_item_gross_value",
                "payment_record_count",
                "total_payment",
                "average_order_value",
                "review_count",
                "average_review_score",
                "first_order_date",
                "last_order_date",
                "customer_lifetime_days",
                "is_repeat_customer",
            ]
        )
        .sort("customer_unique_id")
    )

    return mart

# ---------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------


def validate_mart_customers(
    mart: pl.DataFrame,
) -> None:
    """
    Validate mart_customers structural and business rules.
    """

    required_columns = [
        "customer_unique_id",
        "customer_city",
        "customer_state",
        "total_orders",
        "delivered_orders",
        "canceled_orders",
        "other_orders",
        "total_items",
        "total_product_spend",
        "total_freight_spend",
        "total_item_gross_value",
        "payment_record_count",
        "total_payment",
        "average_order_value",
        "review_count",
        "average_review_score",
        "first_order_date",
        "last_order_date",
        "customer_lifetime_days",
        "is_repeat_customer",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in mart.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required mart columns: {missing_columns}"
        )

    if mart.height == 0:
        raise ValueError(
            "mart_customers contains no rows."
        )

    # Grain validation.
    duplicate_customer_keys = (
        mart.height
        - mart.unique(
            subset=["customer_unique_id"]
        ).height
    )

    if duplicate_customer_keys != 0:
        raise ValueError(
            "Duplicate customer_unique_id values: "
            f"{duplicate_customer_keys}"
        )

    # Required customer key.
    if (
        mart["customer_unique_id"]
        .null_count()
        != 0
    ):
        raise ValueError(
            "customer_unique_id contains null values."
        )

    # Count metrics must not be negative.
    count_columns = [
        "total_orders",
        "delivered_orders",
        "canceled_orders",
        "other_orders",
        "total_items",
        "payment_record_count",
        "review_count",
    ]

    for column in count_columns:
        negative_count = mart.filter(
            pl.col(column) < 0
        ).height

        if negative_count != 0:
            raise ValueError(
                f"{column} contains "
                f"{negative_count} negative values."
            )

    # Monetary metrics must not be negative.
    monetary_columns = [
        "total_product_spend",
        "total_freight_spend",
        "total_item_gross_value",
        "total_payment",
        "average_order_value",
    ]

    for column in monetary_columns:
        negative_count = mart.filter(
            pl.col(column) < 0
        ).height

        if negative_count != 0:
            raise ValueError(
                f"{column} contains "
                f"{negative_count} negative values."
            )

    # Order status components must reconcile.
    invalid_status_totals = mart.filter(
        pl.col("total_orders")
        != (
            pl.col("delivered_orders")
            + pl.col("canceled_orders")
            + pl.col("other_orders")
        )
    ).height

    if invalid_status_totals != 0:
        raise ValueError(
            "Order status components do not reconcile "
            f"for {invalid_status_totals} customers."
        )

    # Repeat-customer flag.
    invalid_repeat_flags = mart.filter(
        pl.col("is_repeat_customer")
        != (pl.col("total_orders") > 1)
    ).height

    if invalid_repeat_flags != 0:
        raise ValueError(
            "Invalid is_repeat_customer flags: "
            f"{invalid_repeat_flags}"
        )

    # Review score range.
    invalid_review_scores = mart.filter(
        pl.col("average_review_score").is_not_null()
        & (
            (pl.col("average_review_score") < 1)
            | (pl.col("average_review_score") > 5)
        )
    ).height

    if invalid_review_scores != 0:
        raise ValueError(
            "Invalid average_review_score values: "
            f"{invalid_review_scores}"
        )


# ---------------------------------------------------------------------
# RECONCILIATION
# ---------------------------------------------------------------------


def validate_mart_reconciliation(
    mart: pl.DataFrame,
    orders: pl.DataFrame,
    order_items: pl.DataFrame,
    payments: pl.DataFrame,
) -> None:
    """
    Reconcile customer-level additive metrics against
    their source facts.
    """

    total_orders = mart["total_orders"].sum()

    if total_orders != orders.height:
        raise ValueError(
            "Order reconciliation failed: "
            f"mart={total_orders}, fact={orders.height}"
        )

    total_items = mart["total_items"].sum()

    if total_items != order_items.height:
        raise ValueError(
            "Item reconciliation failed: "
            f"mart={total_items}, fact={order_items.height}"
        )

    mart_product_spend = mart[
        "total_product_spend"
    ].sum()

    fact_product_spend = order_items[
        "price"
    ].sum()

    if abs(
        mart_product_spend
        - fact_product_spend
    ) > 0.01:
        raise ValueError(
            "Product spend reconciliation failed: "
            f"mart={mart_product_spend}, "
            f"fact={fact_product_spend}"
        )

    mart_freight = mart[
        "total_freight_spend"
    ].sum()

    fact_freight = order_items[
        "freight_value"
    ].sum()

    if abs(
        mart_freight
        - fact_freight
    ) > 0.01:
        raise ValueError(
            "Freight reconciliation failed: "
            f"mart={mart_freight}, "
            f"fact={fact_freight}"
        )

    mart_payment = mart[
        "total_payment"
    ].sum()

    fact_payment = payments[
        "payment_value"
    ].sum()

    if abs(
        mart_payment
        - fact_payment
    ) > 0.01:
        raise ValueError(
            "Payment reconciliation failed: "
            f"mart={mart_payment}, "
            f"fact={fact_payment}"
        )


# ---------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------


def save_mart_customers(
    mart: pl.DataFrame,
) -> Path:
    """
    Save mart_customers as Parquet.
    """

    ANALYTICAL_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    mart.write_parquet(
        MART_CUSTOMERS_FILE
    )

    return MART_CUSTOMERS_FILE


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------


def main() -> None:
    (
        customers,
        orders,
        order_items,
        payments,
        reviews,
    ) = load_dimensions_and_facts()

    mart = build_mart_customers()

    validate_mart_customers(mart)

    validate_mart_reconciliation(
        mart,
        orders,
        order_items,
        payments,
    )

    output_path = save_mart_customers(
        mart
    )

    print("mart_customers built successfully.")
    print(f"Rows: {mart.height}")
    print(f"Columns: {mart.columns}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()