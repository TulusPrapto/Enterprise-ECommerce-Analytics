from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import polars as pl


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "profiling"
OUTPUT_FILE = OUTPUT_DIR / "data_profile.json"

TOP_N_CATEGORIES = 20


DATASETS = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]


TEMPORAL_COLUMNS = {
    "olist_orders_dataset.csv": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "olist_order_items_dataset.csv": [
        "shipping_limit_date",
    ],
    "olist_order_reviews_dataset.csv": [
        "review_creation_date",
        "review_answer_timestamp",
    ],
}


def clean_json_value(value: Any) -> Any:
    """Convert Polars/Python values into JSON-safe values."""
    if value is None:
        return None

    if isinstance(value, (datetime,)):
        return value.isoformat()

    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            return None

    if isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


def safe_percentage(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 4)


def profile_numeric_column(
    df: pl.DataFrame,
    column_name: str,
) -> dict[str, Any]:
    series = df[column_name]

    null_count = series.null_count()
    non_null = series.drop_nulls()

    if non_null.len() == 0:
        return {
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
            "std": None,
            "q1": None,
            "q3": None,
            "iqr": None,
            "zero_count": 0,
            "negative_count": 0,
            "potential_outlier_count": 0,
            "potential_outlier_percentage": 0.0,
        }

    q1 = non_null.quantile(0.25)
    q3 = non_null.quantile(0.75)

    if q1 is None or q3 is None:
        iqr = None
        outlier_count = 0
    else:
        iqr = q3 - q1
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        outlier_mask = (
            (non_null < lower_bound)
            | (non_null > upper_bound)
        )

        outlier_count = outlier_mask.sum()

    zero_count = (non_null == 0).sum()
    negative_count = (non_null < 0).sum()

    return {
        "min": clean_json_value(non_null.min()),
        "max": clean_json_value(non_null.max()),
        "mean": clean_json_value(non_null.mean()),
        "median": clean_json_value(non_null.median()),
        "std": clean_json_value(non_null.std()),
        "q1": clean_json_value(q1),
        "q3": clean_json_value(q3),
        "iqr": clean_json_value(iqr),
        "zero_count": int(zero_count),
        "negative_count": int(negative_count),
        "potential_outlier_count": int(outlier_count),
        "potential_outlier_percentage": safe_percentage(
            outlier_count,
            non_null.len(),
        ),
    }


def profile_categorical_column(
    df: pl.DataFrame,
    column_name: str,
) -> dict[str, Any]:
    series = df[column_name]

    non_null_count = series.len() - series.null_count()
    unique_count = series.n_unique()

    top_values = (
        df.select(column_name)
        .drop_nulls()
        .group_by(column_name)
        .len(name="count")
        .sort("count", descending=True)
        .head(TOP_N_CATEGORIES)
    )

    values = []

    for row in top_values.iter_rows(named=True):
        count = row["count"]

        values.append(
            {
                "value": clean_json_value(row[column_name]),
                "count": count,
                "percentage": safe_percentage(count, non_null_count),
            }
        )

    return {
        "unique_count": unique_count,
        "top_values": values,
    }


def profile_temporal_column(
    df: pl.DataFrame,
    column_name: str,
) -> dict[str, Any]:
    series = df[column_name]

    non_null = series.drop_nulls()

    if non_null.len() == 0:
        return {
            "min": None,
            "max": None,
            "null_count": series.null_count(),
            "invalid_count": 0,
        }

    parsed = non_null.str.to_datetime(
        strict=False,
    )

    invalid_count = parsed.null_count()

    valid = parsed.drop_nulls()

    if valid.len() == 0:
        return {
            "min": None,
            "max": None,
            "null_count": series.null_count(),
            "invalid_count": invalid_count,
        }

    return {
        "min": clean_json_value(valid.min()),
        "max": clean_json_value(valid.max()),
        "null_count": series.null_count(),
        "invalid_count": invalid_count,
    }


def profile_dataset(file_name: str) -> dict[str, Any]:
    file_path = RAW_DATA_DIR / file_name

    print(f"Profiling: {file_name}")

    df = pl.read_csv(
        file_path,
        infer_schema_length=10000,
        try_parse_dates=False,
    )

    row_count = df.height
    column_count = df.width

    duplicate_row_count = df.height - df.unique().height

    columns = []

    temporal_columns = set(TEMPORAL_COLUMNS.get(file_name, []))

    numeric_types = {
        pl.Int8,
        pl.Int16,
        pl.Int32,
        pl.Int64,
        pl.UInt8,
        pl.UInt16,
        pl.UInt32,
        pl.UInt64,
        pl.Float32,
        pl.Float64,
    }

    for column_name in df.columns:
        series = df[column_name]

        null_count = series.null_count()
        unique_count = series.n_unique()

        column_profile: dict[str, Any] = {
            "name": column_name,
            "dtype": str(series.dtype),
            "null_count": null_count,
            "null_percentage": safe_percentage(
                null_count,
                row_count,
            ),
            "unique_count": unique_count,
            "unique_percentage": safe_percentage(
                unique_count,
                row_count,
            ),
        }

        if column_name in temporal_columns:
            column_profile["temporal"] = profile_temporal_column(
                df,
                column_name,
            )

        elif series.dtype in numeric_types:
            column_profile["numeric"] = profile_numeric_column(
                df,
                column_name,
            )

        else:
            column_profile["categorical"] = profile_categorical_column(
                df,
                column_name,
            )

        columns.append(column_profile)

    return {
        "file_name": file_name,
        "file_size_bytes": file_path.stat().st_size,
        "row_count": row_count,
        "column_count": column_count,
        "duplicate_row_count": duplicate_row_count,
        "duplicate_row_percentage": safe_percentage(
            duplicate_row_count,
            row_count,
        ),
        "columns": columns,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now(timezone.utc)

    profiles = []

    for file_name in DATASETS:
        file_path = RAW_DATA_DIR / file_name

        if not file_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {file_path}"
            )

        profiles.append(
            profile_dataset(file_name)
        )

    finished_at = datetime.now(timezone.utc)

    output = {
        "metadata": {
            "generated_at_utc": finished_at.isoformat(),
            "started_at_utc": started_at.isoformat(),
            "project": "Enterprise E-Commerce Analytics",
            "tool": "Python + Polars",
            "polars_version": pl.__version__,
            "top_n_categories": TOP_N_CATEGORIES,
            "dataset_count": len(profiles),
        },
        "datasets": profiles,
    }

    OUTPUT_FILE.write_text(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
            default=clean_json_value,
        ),
        encoding="utf-8",
    )

    print()
    print(f"Profiling completed: {len(profiles)} datasets")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()