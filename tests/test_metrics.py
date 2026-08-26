import polars as pl
import pytest

from src.analytics.metrics import validate_kpis


def valid_kpi_dataframe() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "total_orders": [100],
            "total_customers": [80],
            "total_items_sold": [120],
            "product_revenue": [10000.0],
            "gross_merchandise_value": [12000.0],
            "average_order_value": [120.0],
            "repeat_customer_rate": [0.10],
            "cancellation_rate": [0.05],
            "late_delivery_rate": [0.08],
            "average_delivery_days": [12.5],
        }
    )


def test_validate_kpis_accepts_valid_output():
    kpis = valid_kpi_dataframe()

    validate_kpis(kpis)


def test_validate_kpis_rejects_missing_column():
    kpis = valid_kpi_dataframe().drop("late_delivery_rate")

    with pytest.raises(ValueError, match="missing columns"):
        validate_kpis(kpis)


def test_validate_kpis_rejects_invalid_rate():
    kpis = valid_kpi_dataframe().with_columns(
        pl.lit(1.5).alias("late_delivery_rate")
    )

    with pytest.raises(ValueError, match="between 0 and 1"):
        validate_kpis(kpis)


def test_validate_kpis_rejects_negative_metric():
    kpis = valid_kpi_dataframe().with_columns(
        pl.lit(-1).alias("total_orders")
    )

    with pytest.raises(ValueError, match="cannot be negative"):
        validate_kpis(kpis)