from __future__ import annotations

import polars as pl

from src.analytics.config import (
    ANALYTICAL_DATA_DIR,
    ORDER_ITEMS_FILE,
)


FACT_ORDER_ITEMS_FILE = ANALYTICAL_DATA_DIR / "fact_order_items.parquet"


def build_fact_order_items() -> pl.DataFrame:
    """
    Build the order-item fact table.

    Grain:
        One row per order item.

    Business key:
        (order_id, order_item_id)

    Measures:
        price
        freight_value
        item_gross_value
    """

    df = pl.read_csv(ORDER_ITEMS_FILE)

    fact = (
        df.select(
            [
                "order_id",
                "order_item_id",
                "product_id",
                "seller_id",
                "shipping_limit_date",
                "price",
                "freight_value",
            ]
        )
        .with_columns(
            (
                pl.col("price") + pl.col("freight_value")
            ).alias("item_gross_value")
        )
    )

    return fact


def validate_fact_order_items(df: pl.DataFrame) -> None:
    """
    Validate the analytical order-item fact table.
    """

    required_columns = [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value",
        "item_gross_value",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if df.height == 0:
        raise ValueError(
            "fact_order_items contains no rows."
        )

    # Business key must be unique.
    duplicate_keys = (
        df.height
        - df.unique(
            subset=["order_id", "order_item_id"]
        ).height
    )

    if duplicate_keys != 0:
        raise ValueError(
            f"Duplicate order-item business keys: {duplicate_keys}"
        )

    # Required foreign keys must not be null.
    for column in [
        "order_id",
        "product_id",
        "seller_id",
    ]:
        null_count = df[column].null_count()

        if null_count != 0:
            raise ValueError(
                f"{column} contains {null_count} null values."
            )

    # Monetary measures must not be negative.
    for column in [
        "price",
        "freight_value",
        "item_gross_value",
    ]:
        negative_count = (
            df.filter(pl.col(column) < 0).height
        )

        if negative_count != 0:
            raise ValueError(
                f"{column} contains "
                f"{negative_count} negative values."
            )

    # Verify gross value calculation.
    incorrect_gross = (
        df.filter(
            (
                pl.col("item_gross_value")
                - (
                    pl.col("price")
                    + pl.col("freight_value")
                )
            ).abs()
            > 0.01
        )
        .height
    )

    if incorrect_gross != 0:
        raise ValueError(
            f"{incorrect_gross} rows have incorrect "
            "item_gross_value calculations."
        )


def save_fact_order_items(
    df: pl.DataFrame,
) -> None:
    """
    Save fact_order_items as Parquet.
    """

    ANALYTICAL_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.write_parquet(
        FACT_ORDER_ITEMS_FILE
    )


def main() -> None:
    fact = build_fact_order_items()

    validate_fact_order_items(fact)

    save_fact_order_items(fact)

    print("fact_order_items built successfully.")
    print(f"Rows: {fact.height}")
    print(f"Columns: {fact.columns}")
    print(f"Output: {FACT_ORDER_ITEMS_FILE}")


if __name__ == "__main__":
    main()