import json
from pathlib import Path

import polars as pl

from src.cleaning.config import PROCESSED_DATA_DIR
from src.cleaning.cleaners import read_csv


REPORT_DIR = Path("reports/quality")
OUTPUT_PATH = REPORT_DIR / "exception_deep_analysis.json"


def analyze_orders(df: pl.DataFrame) -> dict:
    delivered = df.filter(
        pl.col("order_status") == "delivered"
    )

    missing_customer_delivery = delivered.filter(
        pl.col("order_delivered_customer_date").is_null()
    )

    carrier_customer_anomaly = delivered.filter(
        pl.col("order_delivered_carrier_date").is_not_null()
        & pl.col("order_delivered_customer_date").is_not_null()
        & (
            pl.col("order_delivered_customer_date")
            < pl.col("order_delivered_carrier_date")
        )
    )

    # Convert timestamps for magnitude analysis.
    anomaly_with_gap = carrier_customer_anomaly.with_columns(
        (
            pl.col("order_delivered_carrier_date").str.to_datetime()
            - pl.col("order_delivered_customer_date").str.to_datetime()
        )
        .dt.total_seconds()
        .alias("gap_seconds")
    )

    gap_summary = (
        anomaly_with_gap
        .select(
            [
                pl.len().alias("count"),
                pl.col("gap_seconds").min().alias("min_gap_seconds"),
                pl.col("gap_seconds").max().alias("max_gap_seconds"),
                pl.col("gap_seconds").mean().alias("avg_gap_seconds"),
                pl.col("gap_seconds").median().alias("median_gap_seconds"),
            ]
        )
        .to_dicts()[0]
    )

    return {
        "ORD-001": {
            "affected_rows": missing_customer_delivery.height,
            "status_distribution": (
                missing_customer_delivery
                .group_by("order_status")
                .len()
                .to_dicts()
            ),
            "has_carrier_date": missing_customer_delivery.filter(
                pl.col("order_delivered_carrier_date").is_not_null()
            ).height,
            "has_estimated_date": missing_customer_delivery.filter(
                pl.col("order_estimated_delivery_date").is_not_null()
            ).height,
            "records": missing_customer_delivery.to_dicts(),
        },
        "ORD-005": {
            "affected_rows": carrier_customer_anomaly.height,
            "gap_summary_seconds": gap_summary,
            "gap_summary_days": {
                "min": gap_summary["min_gap_seconds"] / 86400,
                "max": gap_summary["max_gap_seconds"] / 86400,
                "mean": gap_summary["avg_gap_seconds"] / 86400,
                "median": gap_summary["median_gap_seconds"] / 86400,
            },
            "records": anomaly_with_gap.to_dicts(),
        },
    }


def analyze_payments(df: pl.DataFrame) -> dict:
    invalid_value = df.filter(
        pl.col("payment_value") <= 0
    )

    invalid_installments = df.filter(
        (pl.col("payment_installments") < 1)
        | (pl.col("payment_installments") > 24)
    )

    return {
        "PAY-001": {
            "affected_rows": invalid_value.height,
            "zero_values": invalid_value.filter(
                pl.col("payment_value") == 0
            ).height,
            "negative_values": invalid_value.filter(
                pl.col("payment_value") < 0
            ).height,
            "payment_type_distribution": (
                invalid_value
                .group_by("payment_type")
                .len()
                .sort("len", descending=True)
                .to_dicts()
            ),
            "records": invalid_value.to_dicts(),
        },
        "PAY-003": {
            "affected_rows": invalid_installments.height,
            "below_minimum": invalid_installments.filter(
                pl.col("payment_installments") < 1
            ).height,
            "above_maximum": invalid_installments.filter(
                pl.col("payment_installments") > 24
            ).height,
            "records": invalid_installments.to_dicts(),
        },
    }


def analyze_products(
    products: pl.DataFrame,
    order_items: pl.DataFrame,
) -> dict:
    """Investigate PROD-001."""

    invalid_weight = products.filter(
        pl.col("product_weight_g") <= 0
    )

    ordered_product_ids = (
        order_items
        .select("product_id")
        .unique()
        .with_columns(
            pl.lit(True).alias("appears_in_order_items")
        )
    )

    sold_products = (
        invalid_weight
        .join(
            ordered_product_ids,
            on="product_id",
            how="left",
        )
        .with_columns(
            pl.col("appears_in_order_items")
            .fill_null(False)
        )
    )

    return {
        "PROD-001": {
            "affected_rows": invalid_weight.height,
            "sold_product_count": sold_products.filter(
                pl.col("appears_in_order_items")
            ).height,
            "unsold_product_count": sold_products.filter(
                ~pl.col("appears_in_order_items")
            ).height,
            "records": sold_products.to_dicts(),
        }
    }


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    orders = read_csv(
        PROCESSED_DATA_DIR / "olist_orders_dataset.csv"
    )

    payments = read_csv(
        PROCESSED_DATA_DIR / "olist_order_payments_dataset.csv"
    )

    products = read_csv(
        PROCESSED_DATA_DIR / "olist_products_dataset.csv"
    )

    order_items = read_csv(
        PROCESSED_DATA_DIR / "olist_order_items_dataset.csv"
    )

    report = {
        "metadata": {
            "purpose": (
                "Deep evidence analysis of business data quality "
                "exceptions identified by the business quality rules."
            ),
            "source_directory": str(PROCESSED_DATA_DIR),
            "data_modified": False,
        },
        "exceptions": {
            "orders": analyze_orders(orders),
            "payments": analyze_payments(payments),
            "products": analyze_products(
                products,
                order_items,
            ),
        },
    }

    OUTPUT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    print("Deep exception analysis completed.")
    print(f"Report: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()