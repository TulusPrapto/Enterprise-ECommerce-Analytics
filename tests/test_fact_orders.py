import polars as pl
import pytest

from src.analytics.facts_orders import validate_fact_orders


REQUIRED_COLUMNS = [
    "order_id",
    "customer_id",
    "order_status",
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


def valid_orders() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "order_id": ["order_1", "order_2"],
            "customer_id": ["customer_1", "customer_2"],
            "order_status": ["delivered", "canceled"],
            "order_purchase_timestamp": [None, None],
            "order_approved_at": [None, None],
            "order_delivered_carrier_date": [None, None],
            "order_delivered_customer_date": [None, None],
            "order_estimated_delivery_date": [None, None],
        }
    )


def test_validate_fact_orders_accepts_valid_data():
    validate_fact_orders(valid_orders())


def test_validate_fact_orders_rejects_duplicate_order_id():
    df = valid_orders().with_columns(
        pl.lit("order_1").alias("order_id")
    )

    with pytest.raises(ValueError, match="Duplicate order_id"):
        validate_fact_orders(df)


def test_validate_fact_orders_rejects_unexpected_status():
    df = valid_orders().with_columns(
        pl.lit("invalid_status").alias("order_status")
    )

    with pytest.raises(ValueError, match="Unexpected order_status"):
        validate_fact_orders(df)