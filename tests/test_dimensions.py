import polars as pl
import pytest

from src.analytics.dimensions import validate_dim_customers


def valid_customers() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "customer_id": ["customer_1", "customer_2"],
            "customer_unique_id": ["unique_1", "unique_2"],
            "customer_zip_code_prefix": [1000, 2000],
            "customer_city": ["city_a", "city_b"],
            "customer_state": ["state_a", "state_b"],
        }
    )


def test_validate_dim_customers_accepts_valid_data():
    validate_dim_customers(valid_customers())


def test_validate_dim_customers_rejects_duplicate_customer_id():
    df = valid_customers().with_columns(
        pl.lit("customer_1").alias("customer_id")
    )

    with pytest.raises(ValueError, match="duplicate customer_id"):
        validate_dim_customers(df)