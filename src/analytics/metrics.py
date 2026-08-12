from __future__ import annotations

from dataclasses import dataclass

import polars as pl

from src.analytics.config import (
    FACT_ORDERS_FILE,
    MART_CUSTOMERS_FILE,
    MART_LOGISTICS_FILE,
    MART_PRODUCTS_FILE,
)


# ---------------------------------------------------------------------
# METRIC CONTRACT
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class MetricDefinition:
    """
    Contract defining one official business metric.
    """

    name: str
    description: str
    formula: str
    source_of_truth: str
    numerator: str | None = None
    denominator: str | None = None
    inclusion_rule: str | None = None
    exclusion_rule: str | None = None


METRIC_CATALOG = {
    "total_orders": MetricDefinition(
        name="Total Orders",
        description="Total number of orders in the analytical order population.",
        formula="COUNT(order_id)",
        source_of_truth="fact_orders",
        inclusion_rule="Include every analytical order record.",
    ),

    "total_customers": MetricDefinition(
        name="Total Customers",
        description="Number of unique customers represented in the customer mart.",
        formula="COUNT(DISTINCT customer_unique_id)",
        source_of_truth="mart_customers",
        inclusion_rule="Include every customer represented in mart_customers.",
    ),

    "total_items_sold": MetricDefinition(
        name="Total Items Sold",
        description="Total quantity of products sold through order items.",
        formula="SUM(quantity)",
        source_of_truth="mart_products",
        inclusion_rule="Include every analytical order item.",
    ),

    "product_revenue": MetricDefinition(
        name="Product Revenue",
        description="Total monetary value of product prices.",
        formula="SUM(price)",
        source_of_truth="mart_products",
        inclusion_rule="Include every analytical order item.",
    ),

    "gross_merchandise_value": MetricDefinition(
        name="Gross Merchandise Value",
        description="Total product value including freight value.",
        formula="SUM(price + freight_value)",
        source_of_truth="mart_products",
        inclusion_rule="Include every analytical order item.",
    ),

    "average_order_value": MetricDefinition(
        name="Average Order Value",
        description="Average gross merchandise value per order.",
        formula="Gross Merchandise Value / Total Orders",
        source_of_truth="mart_products + fact_orders",
        inclusion_rule="Include the complete analytical order population.",
    ),

    "repeat_customer_rate": MetricDefinition(
        name="Repeat Customer Rate",
        description="Percentage of customers with more than one order.",
        formula="Repeat Customers / Total Customers",
        source_of_truth="mart_customers",
        numerator="Customers where is_repeat_customer = true",
        denominator="All customers in mart_customers",
    ),

    "cancellation_rate": MetricDefinition(
        name="Cancellation Rate",
        description="Percentage of orders with canceled status.",
        formula="Canceled Orders / Total Orders",
        source_of_truth="fact_orders",
        numerator="Orders where order_status = canceled",
        denominator="All analytical orders",
    ),

    "late_delivery_rate": MetricDefinition(
        name="Late Delivery Rate",
        description=(
            "Percentage of orders with a delivery timestamp "
            "that arrived after the estimated delivery date."
        ),
        formula="Late Delivered Orders / Orders With Delivery Timestamp",
        source_of_truth="mart_logistics",
        numerator="Orders where is_late_delivery = true",
        denominator="Orders where has_delivery_timestamp = true",
    ),

    "average_delivery_days": MetricDefinition(
        name="Average Delivery Days",
        description="Average elapsed time from purchase to customer delivery.",
        formula="AVG(purchase_to_delivery_days)",
        source_of_truth="mart_logistics",
        inclusion_rule=(
            "Include orders with a non-null customer delivery timestamp."
        ),
    ),
}


# ---------------------------------------------------------------------
# METRIC REGISTRY
# ---------------------------------------------------------------------


def get_metric(name: str) -> MetricDefinition:
    """
    Return one metric definition by key.
    """

    try:
        return METRIC_CATALOG[name]
    except KeyError as exc:
        raise KeyError(
            f"Unknown metric: {name}. "
            f"Available metrics: {sorted(METRIC_CATALOG)}"
        ) from exc


def list_metrics() -> list[str]:
    """
    Return all registered metric keys.
    """

    return sorted(METRIC_CATALOG)


# ---------------------------------------------------------------------
# LOADERS
# ---------------------------------------------------------------------


def load_metric_sources() -> tuple[
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
]:
    """
    Load analytical datasets required for KPI calculation.

    Returns:
        orders
        customers
        products
        logistics
    """

    orders = pl.read_parquet(FACT_ORDERS_FILE)
    customers = pl.read_parquet(MART_CUSTOMERS_FILE)
    products = pl.read_parquet(MART_PRODUCTS_FILE)
    logistics = pl.read_parquet(MART_LOGISTICS_FILE)

    return (
        orders,
        customers,
        products,
        logistics,
    )


# ---------------------------------------------------------------------
# KPI CALCULATION
# ---------------------------------------------------------------------


def calculate_kpis() -> pl.DataFrame:
    """
    Calculate the official KPI snapshot.

    Grain:
        One row containing the official KPI set.
    """

    (
        orders,
        customers,
        products,
        logistics,
    ) = load_metric_sources()

    # -------------------------------------------------------------
    # Volume metrics
    # -------------------------------------------------------------

    total_orders = orders.height

    total_customers = customers.height

    total_items_sold = products["total_items_sold"].sum()

    # -------------------------------------------------------------
    # Revenue metrics
    # -------------------------------------------------------------

    product_revenue = products["total_product_revenue"].sum()

    gross_merchandise_value = products["total_gross_value"].sum()

    average_order_value = (
        gross_merchandise_value / total_orders
        if total_orders > 0
        else None
    )

    # -------------------------------------------------------------
    # Customer metrics
    # -------------------------------------------------------------

    repeat_customers = customers.filter(
        pl.col("is_repeat_customer") == True
    ).height

    repeat_customer_rate = (
        repeat_customers / total_customers
        if total_customers > 0
        else None
    )

    # -------------------------------------------------------------
    # Order quality metrics
    # -------------------------------------------------------------

    canceled_orders = orders.filter(
        pl.col("order_status") == "canceled"
    ).height

    cancellation_rate = (
        canceled_orders / total_orders
        if total_orders > 0
        else None
    )

    # -------------------------------------------------------------
    # Logistics metrics
    # -------------------------------------------------------------

    orders_with_delivery = logistics.filter(
        pl.col("has_delivery_timestamp") == True
    )

    late_delivered_orders = orders_with_delivery.filter(
        pl.col("is_late_delivery") == True
    ).height

    late_delivery_rate = (
        late_delivered_orders / orders_with_delivery.height
        if orders_with_delivery.height > 0
        else None
    )

    delivery_days = logistics.filter(
        pl.col("purchase_to_delivery_days").is_not_null()
    )["purchase_to_delivery_days"]

    average_delivery_days = (
        delivery_days.mean()
        if delivery_days.len() > 0
        else None
    )

    return pl.DataFrame(
        {
            "total_orders": [total_orders],
            "total_customers": [total_customers],
            "total_items_sold": [total_items_sold],
            "product_revenue": [product_revenue],
            "gross_merchandise_value": [gross_merchandise_value],
            "average_order_value": [average_order_value],
            "repeat_customer_rate": [repeat_customer_rate],
            "cancellation_rate": [cancellation_rate],
            "late_delivery_rate": [late_delivery_rate],
            "average_delivery_days": [average_delivery_days],
        }
    )


# ---------------------------------------------------------------------
# KPI VALIDATION
# ---------------------------------------------------------------------


def validate_kpis(
    kpis: pl.DataFrame,
) -> None:
    """
    Validate the KPI snapshot against structural
    and business rules.
    """

    required_columns = [
        "total_orders",
        "total_customers",
        "total_items_sold",
        "product_revenue",
        "gross_merchandise_value",
        "average_order_value",
        "repeat_customer_rate",
        "cancellation_rate",
        "late_delivery_rate",
        "average_delivery_days",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in kpis.columns
    ]

    if missing_columns:
        raise ValueError(
            f"KPI output is missing columns: {missing_columns}"
        )

    if kpis.height != 1:
        raise ValueError(
            f"KPI output must contain exactly one row. "
            f"Found: {kpis.height}"
        )

    non_negative_metrics = [
        "total_orders",
        "total_customers",
        "total_items_sold",
        "product_revenue",
        "gross_merchandise_value",
        "average_order_value",
        "average_delivery_days",
    ]

    for metric in non_negative_metrics:
        value = kpis[metric][0]

        if value is not None and value < 0:
            raise ValueError(
                f"KPI cannot be negative: {metric}"
            )

    rate_metrics = [
        "repeat_customer_rate",
        "cancellation_rate",
        "late_delivery_rate",
    ]

    for metric in rate_metrics:
        value = kpis[metric][0]

        if value is not None and not 0 <= value <= 1:
            raise ValueError(
                f"KPI rate must be between 0 and 1: "
                f"{metric}={value}"
            )


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------


def main() -> None:
    """
    Execute the KPI calculation and validation pipeline.
    """

    print("=== KPI CALCULATION ===")

    kpis = calculate_kpis()

    validate_kpis(kpis)

    print(kpis)


if __name__ == "__main__":
    main()