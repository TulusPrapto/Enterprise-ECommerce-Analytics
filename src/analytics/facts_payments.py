from pathlib import Path

import polars as pl

from src.analytics.config import (
    ANALYTICAL_DATA_DIR,
    PAYMENTS_FILE,
)


FACT_ORDER_PAYMENTS_FILE = ANALYTICAL_DATA_DIR / "fact_order_payments.parquet"


def build_fact_order_payments() -> pl.DataFrame:
    """
    Build fact_order_payments.

    Grain:
        1 row = 1 payment record for 1 order.

    Source:
        olist_order_payments_dataset.csv

    Business rule:
        Payment records are retained at their original grain.
        Multiple payment records for the same order are valid and
        must not be collapsed at the fact-table level.
    """

    payments = pl.read_csv(PAYMENTS_FILE)

    required_columns = [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in payments.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required payment columns: {missing_columns}"
        )

    fact = payments.select(required_columns)

    # Explicit type normalization.
    fact = fact.with_columns(
        [
            pl.col("order_id").cast(pl.Utf8),
            pl.col("payment_sequential").cast(pl.Int64),
            pl.col("payment_type").cast(pl.Utf8),
            pl.col("payment_installments").cast(pl.Int64),
            pl.col("payment_value").cast(pl.Float64),
        ]
    )

    # Deterministic ordering.
    fact = fact.sort(
        [
            "order_id",
            "payment_sequential",
        ]
    )

    # Basic structural validation.
    if fact.height == 0:
        raise ValueError("fact_order_payments is empty.")

    if fact["order_id"].null_count() > 0:
        raise ValueError(
            "fact_order_payments contains null order_id values."
        )

    if fact["payment_sequential"].null_count() > 0:
        raise ValueError(
            "fact_order_payments contains null payment_sequential values."
        )

    # payment_sequential should identify the payment sequence
    # within an order. The combination should therefore be unique.
    duplicate_count = (
        fact.height
        - fact.unique(
            subset=[
                "order_id",
                "payment_sequential",
            ]
        ).height
    )

    if duplicate_count > 0:
        raise ValueError(
            "Duplicate order_id + payment_sequential combinations found: "
            f"{duplicate_count}"
        )

    return fact


def save_fact_order_payments(
    fact: pl.DataFrame,
) -> Path:
    """
    Save fact_order_payments as Parquet.
    """

    ANALYTICAL_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fact.write_parquet(
        FACT_ORDER_PAYMENTS_FILE,
    )

    return FACT_ORDER_PAYMENTS_FILE


def main() -> None:
    fact = build_fact_order_payments()
    output = save_fact_order_payments(fact)

    print("fact_order_payments built successfully.")
    print(f"Rows: {fact.height}")
    print(f"Columns: {fact.columns}")
    print(f"Output: {output}")


if __name__ == "__main__":
    main()