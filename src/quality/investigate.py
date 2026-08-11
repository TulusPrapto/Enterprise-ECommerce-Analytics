import json
from pathlib import Path

import polars as pl

from src.cleaning.config import PROCESSED_DATA_DIR
from src.cleaning.cleaners import read_csv


REPORT_DIR = Path("reports/quality")
OUTPUT_PATH = REPORT_DIR / "exception_investigation.json"


def investigate_orders(df: pl.DataFrame) -> dict:
    """Investigate ORD-001 and ORD-005."""

    delivered = df.filter(
        pl.col("order_status") == "delivered"
    )

    ord_001 = delivered.filter(
        pl.col("order_delivered_customer_date").is_null()
    )

    ord_005 = delivered.filter(
        pl.col("order_delivered_carrier_date").is_not_null()
        & pl.col("order_delivered_customer_date").is_not_null()
        & (
            pl.col("order_delivered_customer_date")
            < pl.col("order_delivered_carrier_date")
        )
    )

    return {
        "ORD-001": {
            "rule": "Delivered orders should have customer delivery dates.",
            "affected_rows": ord_001.height,
            "sample": ord_001.select(
                [
                    "order_id",
                    "order_status",
                    "order_purchase_timestamp",
                    "order_estimated_delivery_date",
                    "order_delivered_carrier_date",
                    "order_delivered_customer_date",
                ]
            ).head(20).to_dicts(),
        },
        "ORD-005": {
            "rule": "Customer delivery date should not precede carrier delivery date.",
            "affected_rows": ord_005.height,
            "sample": ord_005.select(
                [
                    "order_id",
                    "order_purchase_timestamp",
                    "order_delivered_carrier_date",
                    "order_delivered_customer_date",
                    "order_estimated_delivery_date",
                ]
            ).head(20).to_dicts(),
        },
    }


def investigate_payments(df: pl.DataFrame) -> dict:
    """Investigate PAY-001 and PAY-003."""

    pay_001 = df.filter(
        pl.col("payment_value") <= 0
    )

    pay_003 = df.filter(
        (pl.col("payment_installments") < 1)
        | (pl.col("payment_installments") > 24)
    )

    return {
        "PAY-001": {
            "rule": "Payment value should be greater than zero.",
            "affected_rows": pay_001.height,
            "sample": pay_001.select(
                [
                    "order_id",
                    "payment_sequential",
                    "payment_type",
                    "payment_installments",
                    "payment_value",
                ]
            ).to_dicts(),
        },
        "PAY-003": {
            "rule": "Payment installments should be between 1 and 24.",
            "affected_rows": pay_003.height,
            "sample": pay_003.select(
                [
                    "order_id",
                    "payment_sequential",
                    "payment_type",
                    "payment_installments",
                    "payment_value",
                ]
            ).to_dicts(),
        },
    }


def investigate_products(df: pl.DataFrame) -> dict:
    """Investigate PROD-001."""

    prod_001 = df.filter(
        pl.col("product_weight_g") <= 0
    )

    return {
        "PROD-001": {
            "rule": "Product weight should be greater than zero.",
            "affected_rows": prod_001.height,
            "sample": prod_001.select(
                [
                    "product_id",
                    "product_category_name",
                    "product_weight_g",
                    "product_length_cm",
                    "product_height_cm",
                    "product_width_cm",
                ]
            ).to_dicts(),
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

    report = {
        "metadata": {
            "purpose": (
                "Investigate business data quality exceptions "
                "without modifying source or processed data."
            ),
            "source": str(PROCESSED_DATA_DIR),
        },
        "investigations": {
            "orders": investigate_orders(orders),
            "payments": investigate_payments(payments),
            "products": investigate_products(products),
        },
    }

    OUTPUT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("Exception investigation completed.")
    print(f"Report: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()