from __future__ import annotations

import polars as pl

from src.analytics.config import (
    ANALYTICAL_DATA_DIR,
    FACT_ORDERS_FILE,
    MART_LOGISTICS_FILE,
)


# ---------------------------------------------------------------------
# LOAD
# ---------------------------------------------------------------------


def load_fact_orders() -> pl.DataFrame:
    """
    Load the order fact table.

    Grain:
        One row per order_id.
    """

    return pl.read_parquet(FACT_ORDERS_FILE)


# ---------------------------------------------------------------------
# BUILD MART
# ---------------------------------------------------------------------


def build_mart_logistics(
    orders: pl.DataFrame,
) -> pl.DataFrame:
    """
    Build the logistics analytical mart.

    Grain:
        One row per order_id.
    """

    mart = (
        orders
        .select(
            [
                "order_id",
                "customer_id",
                "order_status",
                "order_purchase_timestamp",
                "order_approved_at",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
                "order_estimated_delivery_date",
            ]
        )
        .with_columns(
            [
                (
                    (
                        pl.col("order_approved_at")
                        - pl.col("order_purchase_timestamp")
                    )
                    .dt.total_seconds()
                    / 3600
                ).alias("approval_delay_hours"),

                (
                    (
                        pl.col("order_delivered_carrier_date")
                        - pl.col("order_purchase_timestamp")
                    )
                    .dt.total_seconds()
                    / 86400
                ).alias("purchase_to_carrier_days"),

                (
                    (
                        pl.col("order_delivered_customer_date")
                        - pl.col("order_delivered_carrier_date")
                    )
                    .dt.total_seconds()
                    / 86400
                ).alias("carrier_to_customer_days"),

                (
                    (
                        pl.col("order_delivered_customer_date")
                        - pl.col("order_purchase_timestamp")
                    )
                    .dt.total_seconds()
                    / 86400
                ).alias("purchase_to_delivery_days"),
            ]
        )
        .with_columns(
            [
                (
                    pl.col("order_delivered_customer_date").dt.date()
                    - pl.col("order_estimated_delivery_date").dt.date()
                )
                .dt.total_days()
                .cast(pl.Int64)
                .alias("estimated_delivery_variance_days"),

                (
                    pl.col("order_status") == "delivered"
                ).alias("is_delivered"),

                (
                    pl.col("order_delivered_customer_date")
                    .is_not_null()
                ).alias("has_delivery_timestamp"),

                (
                    pl.col("order_delivered_carrier_date").is_not_null()
                    & (
                        pl.col("order_delivered_carrier_date")
                        < pl.col("order_purchase_timestamp")
                    )
                ).alias("invalid_purchase_carrier_sequence"),

                (
                    pl.col("order_delivered_customer_date").is_not_null()
                    & pl.col("order_delivered_carrier_date").is_not_null()
                    & (
                        pl.col("order_delivered_customer_date")
                        < pl.col("order_delivered_carrier_date")
                    )
                ).alias("invalid_carrier_customer_sequence"),

                (
                    (pl.col("order_status") == "delivered")
                    & pl.col("order_delivered_customer_date").is_null()
                ).alias("delivered_missing_customer_date"),

                (
                    (pl.col("order_status") != "delivered")
                    & pl.col("order_delivered_customer_date").is_not_null()
                ).alias("non_delivered_has_customer_date"),
            ]
        )
        .with_columns(
            [
                (
                    pl.col("estimated_delivery_variance_days") > 0
                ).alias("is_late_delivery"),

                (
                    pl.col("estimated_delivery_variance_days") < 0
                ).alias("is_early_delivery"),

                (
                    pl.col("estimated_delivery_variance_days") == 0
                ).alias("is_on_time_delivery"),
            ]
        )
        .sort("order_id")
    )

    return mart


# ---------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------


def validate_mart_logistics(
    mart: pl.DataFrame,
) -> None:
    """
    Validate the logistics mart.
    """

    required_columns = [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "approval_delay_hours",
        "purchase_to_carrier_days",
        "carrier_to_customer_days",
        "purchase_to_delivery_days",
        "estimated_delivery_variance_days",
        "is_delivered",
        "has_delivery_timestamp",
        "invalid_purchase_carrier_sequence",
        "invalid_carrier_customer_sequence",
        "delivered_missing_customer_date",
        "non_delivered_has_customer_date",
        "is_late_delivery",
        "is_early_delivery",
        "is_on_time_delivery",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in mart.columns
    ]

    if missing_columns:
        raise ValueError(
            f"mart_logistics is missing columns: {missing_columns}"
        )

    duplicate_order_ids = (
        mart
        .group_by("order_id")
        .len()
        .filter(pl.col("len") > 1)
    )

    if duplicate_order_ids.height > 0:
        raise ValueError(
            "mart_logistics contains duplicate order_id values."
        )

    if mart["order_id"].null_count() > 0:
        raise ValueError(
            "mart_logistics contains null order_id values."
        )

    if mart.filter(
        pl.col("order_purchase_timestamp").is_null()
    ).height > 0:
        raise ValueError(
            "mart_logistics contains null purchase timestamps."
        )

    if mart.filter(
        pl.col("order_estimated_delivery_date").is_null()
    ).height > 0:
        raise ValueError(
            "mart_logistics contains null estimated delivery dates."
        )

    # Delivery classification must be mutually consistent.
    classification_sum = (
        pl.col("is_late_delivery").cast(pl.Int64)
        + pl.col("is_early_delivery").cast(pl.Int64)
        + pl.col("is_on_time_delivery").cast(pl.Int64)
    )

    invalid_classification = mart.filter(
        pl.col("estimated_delivery_variance_days").is_not_null()
        & (classification_sum != 1)
    )

    if invalid_classification.height > 0:
        raise ValueError(
            "Invalid delivery classification detected."
        )


# ---------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------


def save_mart_logistics(
    mart: pl.DataFrame,
) -> None:
    """
    Persist mart_logistics as Parquet.
    """

    ANALYTICAL_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    mart.write_parquet(MART_LOGISTICS_FILE)


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------


def main() -> None:
    orders = load_fact_orders()

    mart = build_mart_logistics(orders)

    validate_mart_logistics(mart)

    save_mart_logistics(mart)

    print("mart_logistics built successfully.")
    print(f"Rows: {mart.height}")
    print(f"Columns: {mart.columns}")
    print(f"Output: {MART_LOGISTICS_FILE}")

    print("\n=== LOGISTICS QUALITY SUMMARY ===")
    print(
        "Invalid purchase → carrier:",
        mart.filter(
            pl.col("invalid_purchase_carrier_sequence")
        ).height,
    )
    print(
        "Invalid carrier → customer:",
        mart.filter(
            pl.col("invalid_carrier_customer_sequence")
        ).height,
    )
    print(
        "Delivered missing customer date:",
        mart.filter(
            pl.col("delivered_missing_customer_date")
        ).height,
    )
    print(
        "Non-delivered with customer date:",
        mart.filter(
            pl.col("non_delivered_has_customer_date")
        ).height,
    )

    print("\n=== DELIVERY PERFORMANCE ===")
    print(
        "Early:",
        mart.filter(pl.col("is_early_delivery")).height,
    )
    print(
        "On time:",
        mart.filter(pl.col("is_on_time_delivery")).height,
    )
    print(
        "Late:",
        mart.filter(pl.col("is_late_delivery")).height,
    )


if __name__ == "__main__":
    main()