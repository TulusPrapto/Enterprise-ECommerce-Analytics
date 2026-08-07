from pathlib import Path
import json

import polars as pl


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
REPORT_DIR = PROJECT_ROOT / "reports" / "relationships"

REPORT_DIR.mkdir(parents=True, exist_ok=True)


TABLES = {
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


RELATIONSHIPS = [
    {
        "name": "customers_to_orders",
        "parent_table": "customers",
        "parent_key": ["customer_id"],
        "child_table": "orders",
        "child_key": ["customer_id"],
    },
    {
        "name": "orders_to_order_items",
        "parent_table": "orders",
        "parent_key": ["order_id"],
        "child_table": "order_items",
        "child_key": ["order_id"],
    },
    {
        "name": "orders_to_payments",
        "parent_table": "orders",
        "parent_key": ["order_id"],
        "child_table": "payments",
        "child_key": ["order_id"],
    },
    {
        "name": "orders_to_reviews",
        "parent_table": "orders",
        "parent_key": ["order_id"],
        "child_table": "reviews",
        "child_key": ["order_id"],
    },
    {
        "name": "products_to_order_items",
        "parent_table": "products",
        "parent_key": ["product_id"],
        "child_table": "order_items",
        "child_key": ["product_id"],
    },
    {
        "name": "sellers_to_order_items",
        "parent_table": "sellers",
        "parent_key": ["seller_id"],
        "child_table": "order_items",
        "child_key": ["seller_id"],
    },
    {
        "name": "products_to_category_translation",
        "parent_table": "category_translation",
        "parent_key": ["product_category_name"],
        "child_table": "products",
        "child_key": ["product_category_name"],
    },
    {
        "name": "customers_to_geolocation",
        "parent_table": "geolocation",
        "parent_key": ["geolocation_zip_code_prefix"],
        "child_table": "customers",
        "child_key": ["customer_zip_code_prefix"],
    },
    {
        "name": "sellers_to_geolocation",
        "parent_table": "geolocation",
        "parent_key": ["geolocation_zip_code_prefix"],
        "child_table": "sellers",
        "child_key": ["seller_zip_code_prefix"],
    },
]


def load_tables():
    tables = {}

    for table_name, filename in TABLES.items():
        path = RAW_DATA_DIR / filename

        print(f"Loading: {filename}")

        tables[table_name] = pl.read_csv(
            path,
            infer_schema_length=10_000,
        )

    return tables


def key_stats(df: pl.DataFrame, keys: list[str]) -> dict:
    total_rows = len(df)

    null_rows = (
        df.select(
            pl.any_horizontal(
                [pl.col(key).is_null() for key in keys]
            ).sum()
        ).item()
    )

    unique_keys = (
        df.select(keys)
        .unique()
        .height
    )

    duplicate_key_rows = total_rows - unique_keys

    return {
        "row_count": total_rows,
        "unique_key_count": unique_keys,
        "duplicate_key_rows": duplicate_key_rows,
        "null_key_rows": null_rows,
        "is_unique": (
            duplicate_key_rows == 0
            and null_rows == 0
        ),
    }


def analyze_relationship(
    parent_df: pl.DataFrame,
    child_df: pl.DataFrame,
    relationship: dict,
) -> dict:

    parent_keys = relationship["parent_key"]
    child_keys = relationship["child_key"]

    parent_key_stats = key_stats(
        parent_df,
        parent_keys,
    )

    child_key_stats = key_stats(
        child_df,
        child_keys,
    )

    parent_values = (
        parent_df
        .select(parent_keys)
        .drop_nulls()
        .unique()
    )

    child_values = (
        child_df
        .select(child_keys)
        .drop_nulls()
        .unique()
    )

    # Child keys that do not exist in parent table
    child_orphans = (
        child_values
        .join(
            parent_values,
            left_on=child_keys,
            right_on=parent_keys,
            how="anti",
        )
        .height
    )

    # Parent keys that have no matching child
    parent_without_children = (
        parent_values
        .join(
            child_values,
            left_on=parent_keys,
            right_on=child_keys,
            how="anti",
        )
        .height
    )

    # Number of child records associated with each parent key
    child_counts = (
        child_df
        .group_by(child_keys)
        .len(name="child_row_count")
    )

    max_children_per_parent = (
        child_counts
        .select(
            pl.col("child_row_count").max()
        )
        .item()
    )

    avg_children_per_parent = (
        child_counts
        .select(
            pl.col("child_row_count").mean()
        )
        .item()
    )

    return {
        "relationship": relationship["name"],
        "parent_table": relationship["parent_table"],
        "parent_key": parent_keys,
        "child_table": relationship["child_table"],
        "child_key": child_keys,
        "parent_key_stats": parent_key_stats,
        "child_key_stats": child_key_stats,
        "orphan_child_key_count": child_orphans,
        "parent_key_without_children_count": parent_without_children,
        "max_child_rows_per_parent": max_children_per_parent,
        "avg_child_rows_per_parent": round(
            avg_children_per_parent,
            4,
        )
        if avg_children_per_parent is not None
        else None,
        "referential_integrity": (
            child_orphans == 0
        ),
    }


def main():
    tables = load_tables()

    results = []

    for relationship in RELATIONSHIPS:

        print(
            f"Analyzing: "
            f"{relationship['parent_table']} -> "
            f"{relationship['child_table']}"
        )

        result = analyze_relationship(
            parent_df=tables[
                relationship["parent_table"]
            ],
            child_df=tables[
                relationship["child_table"]
            ],
            relationship=relationship,
        )

        results.append(result)

    output = {
        "project": "Enterprise E-Commerce Analytics",
        "analysis": "Relationship Analysis",
        "relationships": results,
    }

    output_file = (
        REPORT_DIR
        / "relationship_profile.json"
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            indent=2,
        )

    print()
    print(
        f"Relationship analysis completed: "
        f"{len(results)} relationships"
    )

    print(
        f"Output: {output_file}"
    )


if __name__ == "__main__":
    main()