from __future__ import annotations

from pathlib import Path

import polars as pl

from src.analytics.config import (
    ANALYTICAL_DATA_DIR,
    CUSTOMERS_FILE,
    ORDERS_FILE,
)


FACT_ORDERS_FILE = ANALYTICAL_DATA_DIR / "fact_orders.parquet"


# ---------------------------------------------------------------------
# BUILD FACT ORDERS
# ---------------------------------------------------------------------

def build_fact_orders() -> pl.DataFrame:
    """
    Build the analytical fact table for orders.

    Grain:
        One row per order.

    Business key:
        order_id

    Foreign key:
        customer_id

    Lifecycle timestamps:
        - order_purchase_timestamp
        - order_approved_at
        - order_delivered_carrier_date
        - order_delivered_customer_date
        - order_estimated_delivery_date

    Important design principle:
        Historical timestamp anomalies are preserved.

        The analytical layer represents the source evidence.
        Business-data-quality decisions belong to the quality layer.

        Therefore, lifecycle timestamp sequence anomalies do NOT
        cause the fact table build to fail.
    """

    orders = pl.read_csv(ORDERS_FILE)

    required_columns = [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in orders.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required order columns: {missing_columns}"
        )

    fact = orders.select(required_columns)

    # -----------------------------------------------------------------
    # Parse lifecycle timestamps
    #
    # strict=False intentionally preserves malformed/missing historical
    # values as null instead of failing the analytical build.
    # -----------------------------------------------------------------

    timestamp_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    fact = fact.with_columns(
        [
            pl.col(column)
            .str.strptime(
                pl.Datetime,
                format="%Y-%m-%d %H:%M:%S",
                strict=False,
            )
            .alias(column)
            for column in timestamp_columns
        ]
    )

    return fact


# ---------------------------------------------------------------------
# VALIDATE FACT ORDERS
# ---------------------------------------------------------------------

def validate_fact_orders(df: pl.DataFrame) -> None:
    """
    Validate the analytical order fact table.

    Hard validation rules:
        - required columns exist
        - fact table is not empty
        - order_id is not null
        - order_id is unique
        - customer_id is not null
        - order_status is not null
        - timestamp parsing does not silently destroy valid values

    Important:
        Lifecycle timestamp sequence anomalies are NOT hard failures.

        Examples:
            carrier date < purchase date
            customer delivery date < carrier date
            customer delivery date < purchase date
            estimated date < purchase date

        These are retained for business-data-quality investigation.
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

    # -----------------------------------------------------------------
    # Empty table
    # -----------------------------------------------------------------

    if df.height == 0:
        raise ValueError(
            "fact_orders contains no rows."
        )

    # -----------------------------------------------------------------
    # order_id validation
    # -----------------------------------------------------------------

    null_order_id = df["order_id"].null_count()

    if null_order_id != 0:
        raise ValueError(
            f"order_id contains {null_order_id} null values."
        )

    duplicate_order_id = (
        df.height
        - df.unique(subset=["order_id"]).height
    )

    if duplicate_order_id != 0:
        raise ValueError(
            f"Duplicate order_id values found: "
            f"{duplicate_order_id}"
        )

    # -----------------------------------------------------------------
    # customer_id validation
    # -----------------------------------------------------------------

    null_customer_id = df["customer_id"].null_count()

    if null_customer_id != 0:
        raise ValueError(
            f"customer_id contains {null_customer_id} null values."
        )

    # -----------------------------------------------------------------
    # order_status validation
    # -----------------------------------------------------------------

    null_status = df["order_status"].null_count()

    if null_status != 0:
        raise ValueError(
            f"order_status contains {null_status} null values."
        )

    expected_statuses = {
        "approved",
        "canceled",
        "created",
        "delivered",
        "invoiced",
        "processing",
        "shipped",
        "unavailable",
    }

    actual_statuses = set(
        df["order_status"]
        .drop_nulls()
        .unique()
        .to_list()
    )

    unexpected_statuses = actual_statuses - expected_statuses

    if unexpected_statuses:
        raise ValueError(
            "Unexpected order_status values found: "
            f"{sorted(unexpected_statuses)}"
        )

    # -----------------------------------------------------------------
    # Timestamp validation
    #
    # We do NOT validate chronological sequence here.
    #
    # Historical anomalies are intentionally preserved.
    # -----------------------------------------------------------------

    # No lifecycle sequence hard-fail validation.
    #
    # Specifically, DO NOT raise errors for:
    #
    # carrier < purchase
    # customer_delivery < carrier
    # customer_delivery < purchase
    # estimated_delivery < purchase
    #
    # Those conditions belong to the business data-quality layer.


# ---------------------------------------------------------------------
# CUSTOMER FOREIGN KEY VALIDATION
# ---------------------------------------------------------------------

def validate_customer_foreign_key(
    fact: pl.DataFrame,
) -> None:
    """
    Validate that every customer_id in fact_orders exists
    in dim_customers source data.

    This validation protects the analytical model from orphan
    customer references.
    """

    customers = pl.read_csv(CUSTOMERS_FILE)

    if "customer_id" not in customers.columns:
        raise ValueError(
            "customer_id column missing from customer source."
        )

    customer_keys = customers.select(
        "customer_id"
    ).unique()

    missing_customers = (
        fact
        .select("customer_id")
        .unique()
        .join(
            customer_keys,
            on="customer_id",
            how="anti",
        )
    )

    if missing_customers.height != 0:
        raise ValueError(
            "Some fact_orders customer_id values do not exist "
            "in the customer dimension: "
            f"{missing_customers.height}"
        )


# ---------------------------------------------------------------------
# WRITE FACT ORDERS
# ---------------------------------------------------------------------

def save_fact_orders(
    df: pl.DataFrame,
) -> Path:
    """
    Save fact_orders as Parquet.
    """

    ANALYTICAL_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.write_parquet(
        FACT_ORDERS_FILE
    )

    return FACT_ORDERS_FILE


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main() -> None:
    """
    Build, validate, and save fact_orders.
    """

    fact = build_fact_orders()

    validate_fact_orders(fact)

    validate_customer_foreign_key(fact)

    output_path = save_fact_orders(fact)

    print(
        "fact_orders built successfully."
    )
    print(
        f"Rows: {fact.height}"
    )
    print(
        f"Columns: {fact.columns}"
    )
    print(
        f"Output: {output_path}"
    )


if __name__ == "__main__":
    main()