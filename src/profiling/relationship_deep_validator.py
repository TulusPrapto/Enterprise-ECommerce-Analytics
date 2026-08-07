from pathlib import Path
import json

import polars as pl


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
REPORT_DIR = PROJECT_ROOT / "reports" / "relationships"

REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# DATA SOURCES
# ---------------------------------------------------------

FILES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def load_csv(table_name: str) -> pl.DataFrame:
    path = RAW_DATA_DIR / FILES[table_name]

    print(f"Loading: {FILES[table_name]}")

    return pl.read_csv(
        path,
        infer_schema_length=10_000,
    )


def unique_non_null(
    df: pl.DataFrame,
    column: str,
) -> pl.DataFrame:

    return (
        df
        .select(column)
        .drop_nulls()
        .unique()
    )


def unmatched_values(
    child_df: pl.DataFrame,
    child_key: str,
    parent_df: pl.DataFrame,
    parent_key: str,
) -> pl.DataFrame:

    child_values = unique_non_null(
        child_df,
        child_key,
    )

    parent_values = unique_non_null(
        parent_df,
        parent_key,
    )

    return (
        child_values
        .join(
            parent_values,
            left_on=child_key,
            right_on=parent_key,
            how="anti",
        )
        .sort(child_key)
    )


# ---------------------------------------------------------
# 1. CATEGORY TRANSLATION VALIDATION
# ---------------------------------------------------------

def validate_categories(
    products: pl.DataFrame,
    translations: pl.DataFrame,
) -> dict:

    unmatched = unmatched_values(
        child_df=products,
        child_key="product_category_name",
        parent_df=translations,
        parent_key="product_category_name",
    )

    affected_products = (
        products
        .join(
            unmatched,
            on="product_category_name",
            how="inner",
        )
        .group_by("product_category_name")
        .len(name="product_count")
        .sort("product_count", descending=True)
    )

    return {
        "relationship": "category_translation_to_products",
        "unmatched_category_count": unmatched.height,
        "unmatched_categories": (
            unmatched
            .to_dicts()
        ),
        "affected_product_counts": (
            affected_products
            .to_dicts()
        ),
    }


# ---------------------------------------------------------
# 2. CUSTOMER GEOLOCATION VALIDATION
# ---------------------------------------------------------

def validate_customer_geolocation(
    customers: pl.DataFrame,
    geolocation: pl.DataFrame,
) -> dict:

    unmatched = unmatched_values(
        child_df=customers,
        child_key="customer_zip_code_prefix",
        parent_df=geolocation,
        parent_key="geolocation_zip_code_prefix",
    )

    affected_customers = (
        customers
        .join(
            unmatched,
            left_on="customer_zip_code_prefix",
            right_on="customer_zip_code_prefix",
            how="inner",
        )
    )

    return {
        "relationship": "geolocation_to_customers",
        "unmatched_zip_prefix_count": unmatched.height,
        "unmatched_zip_prefixes": (
            unmatched
            .to_dicts()
        ),
        "affected_customer_row_count": (
            affected_customers.height
        ),
    }


# ---------------------------------------------------------
# 3. SELLER GEOLOCATION VALIDATION
# ---------------------------------------------------------

def validate_seller_geolocation(
    sellers: pl.DataFrame,
    geolocation: pl.DataFrame,
) -> dict:

    unmatched = unmatched_values(
        child_df=sellers,
        child_key="seller_zip_code_prefix",
        parent_df=geolocation,
        parent_key="geolocation_zip_code_prefix",
    )

    affected_sellers = (
        sellers
        .join(
            unmatched,
            left_on="seller_zip_code_prefix",
            right_on="seller_zip_code_prefix",
            how="inner",
        )
    )

    return {
        "relationship": "geolocation_to_sellers",
        "unmatched_zip_prefix_count": unmatched.height,
        "unmatched_zip_prefixes": (
            unmatched
            .to_dicts()
        ),
        "affected_seller_row_count": (
            affected_sellers.height
        ),
    }


# ---------------------------------------------------------
# 4. ORDERS WITHOUT ITEMS
# ---------------------------------------------------------

def validate_orders_without_items(
    orders: pl.DataFrame,
    order_items: pl.DataFrame,
) -> dict:

    orders_without_items = (
        orders
        .select([
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
        ])
        .join(
            order_items
            .select("order_id")
            .unique(),
            on="order_id",
            how="anti",
        )
        .sort("order_status")
    )

    status_distribution = (
        orders_without_items
        .group_by("order_status")
        .len(name="order_count")
        .sort("order_count", descending=True)
    )

    return {
        "issue": "orders_without_order_items",
        "order_count": orders_without_items.height,
        "status_distribution": (
            status_distribution
            .to_dicts()
        ),
        "sample_orders": (
            orders_without_items
            .head(50)
            .to_dicts()
        ),
    }


# ---------------------------------------------------------
# 5. ORDERS WITHOUT PAYMENTS
# ---------------------------------------------------------

def validate_orders_without_payments(
    orders: pl.DataFrame,
    payments: pl.DataFrame,
) -> dict:

    orders_without_payments = (
        orders
        .select([
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
        ])
        .join(
            payments
            .select("order_id")
            .unique(),
            on="order_id",
            how="anti",
        )
        .sort("order_status")
    )

    return {
        "issue": "orders_without_payments",
        "order_count": orders_without_payments.height,
        "status_distribution": (
            orders_without_payments
            .group_by("order_status")
            .len(name="order_count")
            .sort("order_count", descending=True)
            .to_dicts()
        ),
        "sample_orders": (
            orders_without_payments
            .head(50)
            .to_dicts()
        ),
    }


# ---------------------------------------------------------
# 6. ORDERS WITHOUT REVIEWS
# ---------------------------------------------------------

def validate_orders_without_reviews(
    orders: pl.DataFrame,
    reviews: pl.DataFrame,
) -> dict:

    orders_without_reviews = (
        orders
        .select([
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
        ])
        .join(
            reviews
            .select("order_id")
            .unique(),
            on="order_id",
            how="anti",
        )
        .sort("order_status")
    )

    status_distribution = (
        orders_without_reviews
        .group_by("order_status")
        .len(name="order_count")
        .sort("order_count", descending=True)
    )

    return {
        "issue": "orders_without_reviews",
        "order_count": orders_without_reviews.height,
        "status_distribution": (
            status_distribution
            .to_dicts()
        ),
        "sample_orders": (
            orders_without_reviews
            .head(50)
            .to_dicts()
        ),
    }


# ---------------------------------------------------------
# 7. PAYMENT MULTIPLICITY
# ---------------------------------------------------------

def analyze_payment_multiplicity(
    payments: pl.DataFrame,
) -> dict:

    counts = (
        payments
        .group_by("order_id")
        .len(name="payment_record_count")
    )

    return {
        "grain": "order_id + payment_sequential",
        "orders_with_multiple_payment_records": (
            counts
            .filter(
                pl.col("payment_record_count") > 1
            )
            .height
        ),
        "maximum_payment_records_per_order": (
            counts
            .select(
                pl.col("payment_record_count").max()
            )
            .item()
        ),
    }


# ---------------------------------------------------------
# 8. ORDER ITEM MULTIPLICITY
# ---------------------------------------------------------

def analyze_item_multiplicity(
    order_items: pl.DataFrame,
) -> dict:

    counts = (
        order_items
        .group_by("order_id")
        .len(name="item_record_count")
    )

    return {
        "grain": "order_id + order_item_id",
        "orders_with_multiple_items": (
            counts
            .filter(
                pl.col("item_record_count") > 1
            )
            .height
        ),
        "maximum_items_per_order": (
            counts
            .select(
                pl.col("item_record_count").max()
            )
            .item()
        ),
    }


# ---------------------------------------------------------
# 9. REVIEW MULTIPLICITY
# ---------------------------------------------------------

def analyze_review_multiplicity(
    reviews: pl.DataFrame,
) -> dict:

    counts = (
        reviews
        .group_by("order_id")
        .len(name="review_record_count")
    )

    return {
        "grain": "review_id / review record",
        "orders_with_multiple_reviews": (
            counts
            .filter(
                pl.col("review_record_count") > 1
            )
            .height
        ),
        "maximum_reviews_per_order": (
            counts
            .select(
                pl.col("review_record_count").max()
            )
            .item()
        ),
    }


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("DEEP RELATIONSHIP VALIDATION")
    print("=" * 60)

    customers = load_csv("customers")
    orders = load_csv("orders")
    order_items = load_csv("order_items")
    payments = load_csv("payments")
    reviews = load_csv("reviews")
    products = load_csv("products")
    sellers = load_csv("sellers")
    geolocation = load_csv("geolocation")
    translations = load_csv("category_translation")

    print("\nValidating category translation...")
    category_result = validate_categories(
        products,
        translations,
    )

    print("Validating customer geolocation...")
    customer_geo_result = validate_customer_geolocation(
        customers,
        geolocation,
    )

    print("Validating seller geolocation...")
    seller_geo_result = validate_seller_geolocation(
        sellers,
        geolocation,
    )

    print("Validating orders without items...")
    orders_without_items_result = (
        validate_orders_without_items(
            orders,
            order_items,
        )
    )

    print("Validating orders without payments...")
    orders_without_payments_result = (
        validate_orders_without_payments(
            orders,
            payments,
        )
    )

    print("Validating orders without reviews...")
    orders_without_reviews_result = (
        validate_orders_without_reviews(
            orders,
            reviews,
        )
    )

    print("Analyzing payment multiplicity...")
    payment_result = analyze_payment_multiplicity(
        payments,
    )

    print("Analyzing order-item multiplicity...")
    item_result = analyze_item_multiplicity(
        order_items,
    )

    print("Analyzing review multiplicity...")
    review_result = analyze_review_multiplicity(
        reviews,
    )

    report = {
        "project": "Enterprise E-Commerce Analytics",
        "analysis": "Deep Relationship Validation",
        "category_translation": category_result,
        "customer_geolocation": customer_geo_result,
        "seller_geolocation": seller_geo_result,
        "orders_without_items": orders_without_items_result,
        "orders_without_payments": orders_without_payments_result,
        "orders_without_reviews": orders_without_reviews_result,
        "payment_multiplicity": payment_result,
        "order_item_multiplicity": item_result,
        "review_multiplicity": review_result,
    }

    output_file = (
        REPORT_DIR
        / "relationship_deep_validation.json"
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("=" * 60)
    print("VALIDATION COMPLETED")
    print("=" * 60)
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()