from __future__ import annotations

import polars as pl

from src.analytics.config import (
    ANALYTICAL_DATA_DIR,
    DIM_CUSTOMERS_FILE,
    FACT_ORDERS_FILE,
    FACT_ORDER_ITEMS_FILE,
    MART_LOGISTICS_FILE,
    MART_PRODUCTS_FILE,
)
from src.analytics.metrics import calculate_kpis, validate_kpis


# ---------------------------------------------------------------------
# KPI SUMMARY
# ---------------------------------------------------------------------


def build_kpi_summary() -> pl.DataFrame:
    """
    Build the current KPI snapshot.

    Grain:
        One row per KPI.

    Output columns:
        metric_key
        metric_name
        metric_value
        metric_unit
    """

    kpis = calculate_kpis()

    validate_kpis(kpis)

    metric_metadata = [
        ("total_orders", "Total Orders", "count"),
        ("total_customers", "Total Customers", "count"),
        ("total_items_sold", "Total Items Sold", "count"),
        ("product_revenue", "Product Revenue", "currency"),
        ("gross_merchandise_value", "Gross Merchandise Value", "currency"),
        ("average_order_value", "Average Order Value", "currency"),
        ("repeat_customer_rate", "Repeat Customer Rate", "percentage"),
        ("cancellation_rate", "Cancellation Rate", "percentage"),
        ("late_delivery_rate", "Late Delivery Rate", "percentage"),
        ("average_delivery_days", "Average Delivery Days", "days"),
    ]

    rows = []

    for metric_key, metric_name, metric_unit in metric_metadata:
        rows.append(
            {
                "metric_key": metric_key,
                "metric_name": metric_name,
                "metric_value": kpis[metric_key][0],
                "metric_unit": metric_unit,
            }
        )

    return pl.DataFrame(rows)


# ---------------------------------------------------------------------
# MONTHLY KPI REPORT
# ---------------------------------------------------------------------

def build_monthly_kpi_report() -> pl.DataFrame:
    """
    Build monthly KPI reporting dataset.

    Grain:
        One row per calendar month based on order purchase date.

    All order-item metrics are assigned to the month in which
    the corresponding order was purchased.
    """

    orders = pl.read_parquet(FACT_ORDERS_FILE)

    order_items = pl.read_parquet(FACT_ORDER_ITEMS_FILE)

    customers = pl.read_parquet(DIM_CUSTOMERS_FILE)

    logistics = pl.read_parquet(MART_LOGISTICS_FILE)

    # -------------------------------------------------------------
    # Order → customer mapping
    # -------------------------------------------------------------

    order_customer_map = (
        orders
        .select(
            [
                "order_id",
                "customer_id",
                "order_purchase_timestamp",
            ]
        )
        .join(
            customers.select(
                [
                    "customer_id",
                    "customer_unique_id",
                ]
            ),
            on="customer_id",
            how="left",
        )
        .with_columns(
            pl.col("order_purchase_timestamp")
            .dt.truncate("1mo")
            .alias("month")
        )
    )

    # -------------------------------------------------------------
    # Monthly orders
    # -------------------------------------------------------------

    monthly_orders = (
        order_customer_map
        .group_by("month")
        .agg(
            [
                pl.len().alias("total_orders"),

                pl.col("customer_unique_id")
                .n_unique()
                .alias("total_customers"),

                (
                    pl.col("customer_id")
                    .n_unique()
                ).alias("total_customer_ids"),

                (
                    pl.col("order_id")
                    .filter(
                        pl.col("order_id").is_not_null()
                    )
                    .count()
                ).alias("order_count_check"),
            ]
        )
    )

    # -------------------------------------------------------------
    # Monthly cancellation
    # -------------------------------------------------------------

    monthly_cancellations = (
        orders
        .with_columns(
            pl.col("order_purchase_timestamp")
            .dt.truncate("1mo")
            .alias("month")
        )
        .group_by("month")
        .agg(
            (
                pl.col("order_status") == "canceled"
            )
            .sum()
            .alias("canceled_orders")
        )
    )

    # -------------------------------------------------------------
    # Order items
    #
    # IMPORTANT:
    # fact_order_items does not carry the business reporting month
    # directly. Therefore join through order_id and inherit the
    # purchase month from fact_orders.
    # -------------------------------------------------------------

    item_monthly_source = (
        order_items
        .select(
            [
                "order_id",
                "price",
                "freight_value",
                "item_gross_value",
            ]
        )
        .join(
            order_customer_map.select(
                [
                    "order_id",
                    "month",
                ]
            ),
            on="order_id",
            how="left",
        )
    )

    monthly_items = (
        item_monthly_source
        .group_by("month")
        .agg(
            [
                pl.len().alias("total_items_sold"),

                pl.col("price")
                .sum()
                .alias("product_revenue"),

                pl.col("freight_value")
                .sum()
                .alias("freight_revenue"),

                pl.col("item_gross_value")
                .sum()
                .alias("gross_merchandise_value"),
            ]
        )
    )

    # -------------------------------------------------------------
    # Monthly logistics
    #
    # Logistics already contains one row per order, so its purchase
    # timestamp is used directly as the reporting month.
    # -------------------------------------------------------------

    monthly_logistics = (
        logistics
        .with_columns(
            pl.col("order_purchase_timestamp")
            .dt.truncate("1mo")
            .alias("month")
        )
        .group_by("month")
        .agg(
            [
                pl.col("is_late_delivery")
                .sum()
                .alias("late_orders"),

                pl.col("has_delivery_timestamp")
                .sum()
                .alias("orders_with_delivery"),

                pl.col("purchase_to_delivery_days")
                .mean()
                .alias("average_delivery_days"),
            ]
        )
    )

    # -------------------------------------------------------------
    # Combine monthly datasets
    # -------------------------------------------------------------

    monthly = (
        monthly_orders
        .join(
            monthly_cancellations,
            on="month",
            how="left",
        )
        .join(
            monthly_items,
            on="month",
            how="left",
        )
        .join(
            monthly_logistics,
            on="month",
            how="left",
        )
        .with_columns(
            [
                pl.col("canceled_orders")
                .fill_null(0)
                .cast(pl.Int64),

                pl.col("total_items_sold")
                .fill_null(0)
                .cast(pl.Int64),

                pl.col("product_revenue")
                .fill_null(0.0),

                pl.col("freight_revenue")
                .fill_null(0.0),

                pl.col("gross_merchandise_value")
                .fill_null(0.0),

                pl.col("late_orders")
                .fill_null(0)
                .cast(pl.Int64),

                pl.col("orders_with_delivery")
                .fill_null(0)
                .cast(pl.Int64),
            ]
        )
        .with_columns(
            [
                pl.when(
                    pl.col("total_orders") > 0
                )
                .then(
                    pl.col("gross_merchandise_value")
                    / pl.col("total_orders")
                )
                .otherwise(None)
                .alias("average_order_value"),

                pl.when(
                    pl.col("total_orders") > 0
                )
                .then(
                    pl.col("canceled_orders")
                    / pl.col("total_orders")
                )
                .otherwise(None)
                .alias("cancellation_rate"),

                pl.when(
                    pl.col("orders_with_delivery") > 0
                )
                .then(
                    pl.col("late_orders")
                    / pl.col("orders_with_delivery")
                )
                .otherwise(None)
                .alias("late_delivery_rate"),
            ]
        )
        .select(
            [
                "month",
                "total_orders",
                "total_customers",
                "total_items_sold",
                "product_revenue",
                "freight_revenue",
                "gross_merchandise_value",
                "average_order_value",
                "canceled_orders",
                "cancellation_rate",
                "late_orders",
                "orders_with_delivery",
                "late_delivery_rate",
                "average_delivery_days",
            ]
        )
        .sort("month")
    )

    return monthly


# ---------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------


def validate_kpi_summary(
    summary: pl.DataFrame,
) -> None:
    """
    Validate KPI summary structure.
    """

    required_columns = [
        "metric_key",
        "metric_name",
        "metric_value",
        "metric_unit",
    ]

    missing = [
        column
        for column in required_columns
        if column not in summary.columns
    ]

    if missing:
        raise ValueError(
            f"KPI summary missing columns: {missing}"
        )

    if summary.height != 10:
        raise ValueError(
            f"Expected 10 KPI rows, found {summary.height}"
        )

    if summary["metric_key"].n_unique() != 10:
        raise ValueError(
            "KPI summary contains duplicate metric keys."
        )


def validate_monthly_kpi_report(
    monthly: pl.DataFrame,
) -> None:
    """
    Validate monthly KPI reporting dataset.
    """

    if monthly.height == 0:
        raise ValueError(
            "Monthly KPI report is empty."
        )

    if monthly["month"].n_unique() != monthly.height:
        raise ValueError(
            "Monthly KPI report contains duplicate months."
        )

    rate_columns = [
        "cancellation_rate",
        "late_delivery_rate",
    ]

    for column in rate_columns:
        invalid = monthly.filter(
            (pl.col(column) < 0)
            | (pl.col(column) > 1)
        )

        if invalid.height > 0:
            raise ValueError(
                f"Invalid rate values detected in {column}."
            )

    non_negative_columns = [
        "total_orders",
        "total_customers",
        "total_items_sold",
        "product_revenue",
        "freight_revenue",
        "gross_merchandise_value",
        "average_order_value",
        "canceled_orders",
        "late_orders",
        "orders_with_delivery",
        "average_delivery_days",
    ]

    for column in non_negative_columns:
        invalid = monthly.filter(
            pl.col(column).is_not_null()
            & (pl.col(column) < 0)
        )

        if invalid.height > 0:
            raise ValueError(
                f"Negative values detected in {column}."
            )


# ---------------------------------------------------------------------
# PERSISTENCE
# ---------------------------------------------------------------------


def save_reporting_datasets() -> tuple:
    """
    Build, validate, and persist reporting datasets.
    """

    ANALYTICAL_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary = build_kpi_summary()

    monthly = build_monthly_kpi_report()

    validate_kpi_summary(summary)

    validate_monthly_kpi_report(monthly)

    summary_path = (
        ANALYTICAL_DATA_DIR
        / "kpi_summary.parquet"
    )

    monthly_path = (
        ANALYTICAL_DATA_DIR
        / "kpi_monthly.parquet"
    )

    summary.write_parquet(summary_path)

    monthly.write_parquet(monthly_path)

    return (
        summary,
        monthly,
        summary_path,
        monthly_path,
    )


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------


def main() -> None:
    """
    Build reporting datasets.
    """

    (
        summary,
        monthly,
        summary_path,
        monthly_path,
    ) = save_reporting_datasets()

    print("=== KPI REPORTING LAYER ===")

    print(
        f"KPI summary rows: {summary.height}"
    )

    print(
        f"Monthly KPI rows: {monthly.height}"
    )

    print(
        f"Summary output: {summary_path}"
    )

    print(
        f"Monthly output: {monthly_path}"
    )

    print("\n=== KPI SUMMARY ===")

    print(summary)

    print("\n=== MONTHLY KPI SAMPLE ===")

    print(
        monthly.head(10)
    )


if __name__ == "__main__":
    main()