from dataclasses import dataclass

import polars as pl

from src.analytics.config import (
    CUSTOMERS_FILE,
    ORDERS_FILE,
    ORDER_ITEMS_FILE,
    PAYMENTS_FILE,
    PRODUCTS_FILE,
    SELLERS_FILE,
)


@dataclass(frozen=True)
class DatasetContract:
    name: str
    path: object
    required_columns: tuple[str, ...]


DATASET_CONTRACTS = (
    DatasetContract(
        name="orders",
        path=ORDERS_FILE,
        required_columns=(
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ),
    ),
    DatasetContract(
        name="order_items",
        path=ORDER_ITEMS_FILE,
        required_columns=(
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
        ),
    ),
    DatasetContract(
        name="payments",
        path=PAYMENTS_FILE,
        required_columns=(
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
        ),
    ),
    DatasetContract(
        name="products",
        path=PRODUCTS_FILE,
        required_columns=(
            "product_id",
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ),
    ),
    DatasetContract(
        name="sellers",
        path=SELLERS_FILE,
        required_columns=(
            "seller_id",
            "seller_zip_code_prefix",
            "seller_city",
            "seller_state",
        ),
    ),
    DatasetContract(
        name="customers",
        path=CUSTOMERS_FILE,
        required_columns=(
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ),
    ),
)


def validate_source_contracts() -> list[dict]:
    results = []

    for contract in DATASET_CONTRACTS:
        path = contract.path

        if not path.exists():
            results.append(
                {
                    "dataset": contract.name,
                    "passed": False,
                    "message": f"Source file does not exist: {path}",
                    "missing_columns": list(contract.required_columns),
                }
            )
            continue

        df = pl.read_csv(path)

        actual_columns = set(df.columns)
        missing_columns = [
            column
            for column in contract.required_columns
            if column not in actual_columns
        ]

        results.append(
            {
                "dataset": contract.name,
                "passed": len(missing_columns) == 0,
                "message": (
                    "Source contract satisfied."
                    if not missing_columns
                    else "Required source columns are missing."
                ),
                "missing_columns": missing_columns,
                "row_count": df.height,
                "column_count": len(df.columns),
            }
        )

    return results


def main() -> None:
    results = validate_source_contracts()

    print("Source contract validation completed.")

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(
            f"{status} | "
            f"{result['dataset']} | "
            f"rows={result['row_count'] if 'row_count' in result else 0} | "
            f"missing={result['missing_columns']}"
        )

    if not all(result["passed"] for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()