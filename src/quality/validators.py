from dataclasses import dataclass, asdict
from typing import Any

import polars as pl


@dataclass
class RuleResult:
    rule_id: str
    dataset: str
    severity: str
    passed: bool
    evaluated_rows: int
    affected_rows: int
    message: str
    sample: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _sample_records(
    df: pl.DataFrame,
    columns: list[str] | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Convert a small sample of a DataFrame into JSON-friendly records.
    """
    if df.height == 0:
        return []

    if columns:
        available = [c for c in columns if c in df.columns]
        if available:
            df = df.select(available)

    return df.head(limit).to_dicts()


def _result(
    rule_id: str,
    dataset: str,
    severity: str,
    passed: bool,
    evaluated_rows: int,
    affected_rows: int,
    message: str,
    sample_df: pl.DataFrame | None = None,
    sample_columns: list[str] | None = None,
) -> RuleResult:
    """
    Standard constructor for RuleResult.
    """
    sample = []

    if sample_df is not None:
        sample = _sample_records(
            sample_df,
            columns=sample_columns,
        )

    return RuleResult(
        rule_id=rule_id,
        dataset=dataset,
        severity=severity,
        passed=passed,
        evaluated_rows=evaluated_rows,
        affected_rows=affected_rows,
        message=message,
        sample=sample,
    )


# ============================================================
# ORDERS
# ============================================================

def validate_orders(df: pl.DataFrame) -> list[RuleResult]:
    results: list[RuleResult] = []

    # ---------------------------------------------------------
    # ORD-001
    # Delivered orders should have customer delivery date.
    # ---------------------------------------------------------
    affected = df.filter(
        (pl.col("order_status") == "delivered")
        & pl.col("order_delivered_customer_date").is_null()
    )

    results.append(
        _result(
            rule_id="ORD-001",
            dataset="olist_orders_dataset.csv",
            severity="WARNING",
            passed=affected.height == 0,
            evaluated_rows=df.filter(
                pl.col("order_status") == "delivered"
            ).height,
            affected_rows=affected.height,
            message=(
                "All delivered orders have customer delivery dates."
                if affected.height == 0
                else "Some delivered orders are missing customer delivery dates."
            ),
            sample_df=affected,
            sample_columns=[
                "order_id",
                "order_status",
            ],
        )
    )

    # ---------------------------------------------------------
    # ORD-002
    # Delivered orders should have estimated delivery date.
    # ---------------------------------------------------------
    affected = df.filter(
        (pl.col("order_status") == "delivered")
        & pl.col("order_estimated_delivery_date").is_null()
    )

    results.append(
        _result(
            rule_id="ORD-002",
            dataset="olist_orders_dataset.csv",
            severity="WARNING",
            passed=affected.height == 0,
            evaluated_rows=df.filter(
                pl.col("order_status") == "delivered"
            ).height,
            affected_rows=affected.height,
            message=(
                "All delivered orders have an estimated delivery date."
                if affected.height == 0
                else "Some delivered orders are missing estimated delivery dates."
            ),
            sample_df=affected,
            sample_columns=[
                "order_id",
                "order_status",
            ],
        )
    )

    # ---------------------------------------------------------
    # ORD-003
    # Customer delivery date must not precede purchase timestamp.
    # ---------------------------------------------------------
    affected = df.filter(
        pl.col("order_delivered_customer_date").is_not_null()
        & pl.col("order_purchase_timestamp").is_not_null()
        & (
            pl.col("order_delivered_customer_date")
            < pl.col("order_purchase_timestamp")
        )
    )

    results.append(
        _result(
            rule_id="ORD-003",
            dataset="olist_orders_dataset.csv",
            severity="FAIL",
            passed=affected.height == 0,
            evaluated_rows=df.height,
            affected_rows=affected.height,
            message=(
                "Delivery dates are not earlier than purchase timestamps."
                if affected.height == 0
                else "Some delivery dates precede purchase timestamps."
            ),
            sample_df=affected,
            sample_columns=[
                "order_id",
                "order_purchase_timestamp",
                "order_delivered_customer_date",
            ],
        )
    )

    # ---------------------------------------------------------
    # ORD-004
    # Approval timestamp should not precede purchase timestamp.
    # ---------------------------------------------------------
    affected = df.filter(
        pl.col("order_approved_at").is_not_null()
        & pl.col("order_purchase_timestamp").is_not_null()
        & (
            pl.col("order_approved_at")
            < pl.col("order_purchase_timestamp")
        )
    )

    results.append(
        _result(
            rule_id="ORD-004",
            dataset="olist_orders_dataset.csv",
            severity="WARNING",
            passed=affected.height == 0,
            evaluated_rows=df.height,
            affected_rows=affected.height,
            message=(
                "Approval timestamps do not precede purchase timestamps."
                if affected.height == 0
                else "Some approval timestamps precede purchase timestamps."
            ),
            sample_df=affected,
            sample_columns=[
                "order_id",
                "order_purchase_timestamp",
                "order_approved_at",
            ],
        )
    )

    # ---------------------------------------------------------
    # ORD-005
    # Customer delivery date should not precede carrier delivery date.
    # ---------------------------------------------------------
    affected = df.filter(
        pl.col("order_delivered_carrier_date").is_not_null()
        & pl.col("order_delivered_customer_date").is_not_null()
        & (
            pl.col("order_delivered_customer_date")
            < pl.col("order_delivered_carrier_date")
        )
    )

    results.append(
        _result(
            rule_id="ORD-005",
            dataset="olist_orders_dataset.csv",
            severity="WARNING",
            passed=affected.height == 0,
            evaluated_rows=df.height,
            affected_rows=affected.height,
            message=(
                "Customer delivery dates do not precede carrier delivery dates."
                if affected.height == 0
                else "Some customer delivery dates precede carrier delivery dates."
            ),
            sample_df=affected,
            sample_columns=[
                "order_id",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
            ],
        )
    )

    return results


# ============================================================
# ORDER ITEMS
# ============================================================

def validate_order_items(df: pl.DataFrame) -> list[RuleResult]:
    results: list[RuleResult] = []

    # ---------------------------------------------------------
    # ITEM-001
    # Item price must be non-negative.
    # ---------------------------------------------------------
    affected = df.filter(
        pl.col("price") < 0
    )

    results.append(
        _result(
            rule_id="ITEM-001",
            dataset="olist_order_items_dataset.csv",
            severity="FAIL",
            passed=affected.height == 0,
            evaluated_rows=df.height,
            affected_rows=affected.height,
            message=(
                "All item prices are non-negative."
                if affected.height == 0
                else "Some item prices are negative."
            ),
            sample_df=affected,
            sample_columns=[
                "order_id",
                "order_item_id",
                "product_id",
                "price",
            ],
        )
    )

    # ---------------------------------------------------------
    # ITEM-002
    # Freight value must be non-negative.
    # ---------------------------------------------------------
    affected = df.filter(
        pl.col("freight_value") < 0
    )

    results.append(
        _result(
            rule_id="ITEM-002",
            dataset="olist_order_items_dataset.csv",
            severity="FAIL",
            passed=affected.height == 0,
            evaluated_rows=df.height,
            affected_rows=affected.height,
            message=(
                "All freight values are non-negative."
                if affected.height == 0
                else "Some freight values are negative."
            ),
            sample_df=affected,
            sample_columns=[
                "order_id",
                "order_item_id",
                "price",
                "freight_value",
            ],
        )
    )

    return results


# ============================================================
# PAYMENTS
# ============================================================

def validate_payments(df: pl.DataFrame) -> list[RuleResult]:
    results: list[RuleResult] = []

    # ---------------------------------------------------------
    # PAY-001
    # Payment value should be positive.
    # ---------------------------------------------------------
    affected = df.filter(
        pl.col("payment_value") <= 0
    )

    results.append(
        _result(
            rule_id="PAY-001",
            dataset="olist_order_payments_dataset.csv",
            severity="WARNING",
            passed=affected.height == 0,
            evaluated_rows=df.height,
            affected_rows=affected.height,
            message=(
                "All payment values are positive."
                if affected.height == 0
                else "Some payment records have zero or negative values."
            ),
            sample_df=affected,
            sample_columns=[
                "order_id",
                "payment_sequential",
                "payment_type",
                "payment_installments",
                "payment_value",
            ],
        )
    )

    # ---------------------------------------------------------
    # PAY-002
    # Payment sequential must be >= 1.
    # ---------------------------------------------------------
    affected = df.filter(
        pl.col("payment_sequential") < 1
    )

    results.append(
        _result(
            rule_id="PAY-002",
            dataset="olist_order_payments_dataset.csv",
            severity="FAIL",
            passed=affected.height == 0,
            evaluated_rows=df.height,
            affected_rows=affected.height,
            message=(
                "All payment sequential values are valid."
                if affected.height == 0
                else "Some payment sequential values are invalid."
            ),
            sample_df=affected,
            sample_columns=[
                "order_id",
                "payment_sequential",
            ],
        )
    )

    # ---------------------------------------------------------
    # PAY-003
    # Installments must be between 1 and 24.
    # ---------------------------------------------------------
    affected = df.filter(
        (pl.col("payment_installments") < 1)
        | (pl.col("payment_installments") > 24)
    )

    results.append(
        _result(
            rule_id="PAY-003",
            dataset="olist_order_payments_dataset.csv",
            severity="FAIL",
            passed=affected.height == 0,
            evaluated_rows=df.height,
            affected_rows=affected.height,
            message=(
                "All payment installment values are valid."
                if affected.height == 0
                else "Some payment records have invalid installment values."
            ),
            sample_df=affected,
            sample_columns=[
                "order_id",
                "payment_sequential",
                "payment_type",
                "payment_installments",
                "payment_value",
            ],
        )
    )

    return results


# ============================================================
# REVIEWS
# ============================================================

def validate_reviews(df: pl.DataFrame) -> list[RuleResult]:
    results: list[RuleResult] = []

    # ---------------------------------------------------------
    # REV-001
    # Review score must be between 1 and 5.
    # ---------------------------------------------------------
    affected = df.filter(
        (pl.col("review_score") < 1)
        | (pl.col("review_score") > 5)
    )

    results.append(
        _result(
            rule_id="REV-001",
            dataset="olist_order_reviews_dataset.csv",
            severity="FAIL",
            passed=affected.height == 0,
            evaluated_rows=df.height,
            affected_rows=affected.height,
            message=(
                "All review scores are between 1 and 5."
                if affected.height == 0
                else "Some review scores are outside the valid 1-5 range."
            ),
            sample_df=affected,
            sample_columns=[
                "review_id",
                "order_id",
                "review_score",
            ],
        )
    )

    return results


# ============================================================
# PRODUCTS
# ============================================================

def validate_products(df: pl.DataFrame) -> list[RuleResult]:
    results: list[RuleResult] = []

    # ---------------------------------------------------------
    # PROD-001
    # Product weight should be positive when provided.
    # ---------------------------------------------------------
    affected = df.filter(
        pl.col("product_weight_g").is_not_null()
        & (pl.col("product_weight_g") <= 0)
    )

    results.append(
        _result(
            rule_id="PROD-001",
            dataset="olist_products_dataset.csv",
            severity="WARNING",
            passed=affected.height == 0,
            evaluated_rows=df.filter(
                pl.col("product_weight_g").is_not_null()
            ).height,
            affected_rows=affected.height,
            message=(
                "All non-null product weight values are greater than zero."
                if affected.height == 0
                else "Some products have non-positive weight values."
            ),
            sample_df=affected,
            sample_columns=[
                "product_id",
                "product_weight_g",
                "product_length_cm",
                "product_height_cm",
                "product_width_cm",
            ],
        )
    )

    # ---------------------------------------------------------
    # PROD-002
    # Product dimensions should be positive when provided.
    # ---------------------------------------------------------
    dimension_columns = [
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]

    dimension_condition = None

    for column in dimension_columns:
        condition = (
            pl.col(column).is_not_null()
            & (pl.col(column) <= 0)
        )

        if dimension_condition is None:
            dimension_condition = condition
        else:
            dimension_condition = dimension_condition | condition

    affected = df.filter(dimension_condition)

    results.append(
        _result(
            rule_id="PROD-002",
            dataset="olist_products_dataset.csv",
            severity="WARNING",
            passed=affected.height == 0,
            evaluated_rows=df.height,
            affected_rows=affected.height,
            message=(
                "All non-null product dimensions are greater than zero."
                if affected.height == 0
                else "Some products have non-positive dimensions."
            ),
            sample_df=affected,
            sample_columns=[
                "product_id",
                "product_length_cm",
                "product_height_cm",
                "product_width_cm",
            ],
        )
    )

    return results


# ============================================================
# RELATIONSHIPS
# ============================================================

def validate_relationships(
    orders: pl.DataFrame,
    order_items: pl.DataFrame,
    payments: pl.DataFrame,
    reviews: pl.DataFrame,
    products: pl.DataFrame,
    sellers: pl.DataFrame,
) -> list[RuleResult]:
    """
    Validate referential integrity across the core Olist datasets.

    REL-001:
        Every order item must reference an existing order.

    REL-002:
        Every payment must reference an existing order.

    REL-003:
        Every review must reference an existing order.

    REL-004:
        Every order item must reference an existing product.

    REL-005:
        Every order item must reference an existing seller.
    """

    results: list[RuleResult] = []

    # ---------------------------------------------------------
    # Reference tables
    # ---------------------------------------------------------

    valid_orders = (
        orders
        .select("order_id")
        .drop_nulls()
        .unique()
    )

    valid_products = (
        products
        .select("product_id")
        .drop_nulls()
        .unique()
    )

    valid_sellers = (
        sellers
        .select("seller_id")
        .drop_nulls()
        .unique()
    )

    # ---------------------------------------------------------
    # REL-001
    # Every order item must reference an existing order.
    # ---------------------------------------------------------

    affected = (
        order_items
        .filter(pl.col("order_id").is_not_null())
        .join(
            valid_orders,
            on="order_id",
            how="anti",
        )
    )

    results.append(
        _result(
            rule_id="REL-001",
            dataset="olist_order_items_dataset.csv",
            severity="FAIL",
            passed=affected.height == 0,
            evaluated_rows=order_items.filter(
                pl.col("order_id").is_not_null()
            ).height,
            affected_rows=affected.height,
            message=(
                "All order items reference existing orders."
                if affected.height == 0
                else "Some order items reference non-existing orders."
            ),
            sample_df=affected,
            sample_columns=[
                "order_id",
                "order_item_id",
                "product_id",
                "seller_id",
            ],
        )
    )

    # ---------------------------------------------------------
    # REL-002
    # Every payment must reference an existing order.
    # ---------------------------------------------------------

    affected = (
        payments
        .filter(pl.col("order_id").is_not_null())
        .join(
            valid_orders,
            on="order_id",
            how="anti",
        )
    )

    results.append(
        _result(
            rule_id="REL-002",
            dataset="olist_order_payments_dataset.csv",
            severity="FAIL",
            passed=affected.height == 0,
            evaluated_rows=payments.filter(
                pl.col("order_id").is_not_null()
            ).height,
            affected_rows=affected.height,
            message=(
                "All payments reference existing orders."
                if affected.height == 0
                else "Some payments reference non-existing orders."
            ),
            sample_df=affected,
            sample_columns=[
                "order_id",
                "payment_sequential",
                "payment_type",
                "payment_value",
            ],
        )
    )

    # ---------------------------------------------------------
    # REL-003
    # Every review must reference an existing order.
    # ---------------------------------------------------------

    affected = (
        reviews
        .filter(pl.col("order_id").is_not_null())
        .join(
            valid_orders,
            on="order_id",
            how="anti",
        )
    )

    results.append(
        _result(
            rule_id="REL-003",
            dataset="olist_order_reviews_dataset.csv",
            severity="FAIL",
            passed=affected.height == 0,
            evaluated_rows=reviews.filter(
                pl.col("order_id").is_not_null()
            ).height,
            affected_rows=affected.height,
            message=(
                "All reviews reference existing orders."
                if affected.height == 0
                else "Some reviews reference non-existing orders."
            ),
            sample_df=affected,
            sample_columns=[
                "review_id",
                "order_id",
            ],
        )
    )

    # ---------------------------------------------------------
    # REL-004
    # Every order item must reference an existing product.
    # ---------------------------------------------------------

    affected = (
        order_items
        .filter(pl.col("product_id").is_not_null())
        .join(
            valid_products,
            on="product_id",
            how="anti",
        )
    )

    results.append(
        _result(
            rule_id="REL-004",
            dataset="olist_order_items_dataset.csv",
            severity="FAIL",
            passed=affected.height == 0,
            evaluated_rows=order_items.filter(
                pl.col("product_id").is_not_null()
            ).height,
            affected_rows=affected.height,
            message=(
                "All order items reference existing products."
                if affected.height == 0
                else "Some order items reference non-existing products."
            ),
            sample_df=affected,
            sample_columns=[
                "order_id",
                "order_item_id",
                "product_id",
            ],
        )
    )

    # ---------------------------------------------------------
    # REL-005
    # Every order item must reference an existing seller.
    # ---------------------------------------------------------

    affected = (
        order_items
        .filter(pl.col("seller_id").is_not_null())
        .join(
            valid_sellers,
            on="seller_id",
            how="anti",
        )
    )

    results.append(
        _result(
            rule_id="REL-005",
            dataset="olist_order_items_dataset.csv",
            severity="FAIL",
            passed=affected.height == 0,
            evaluated_rows=order_items.filter(
                pl.col("seller_id").is_not_null()
            ).height,
            affected_rows=affected.height,
            message=(
                "All order items reference existing sellers."
                if affected.height == 0
                else "Some order items reference non-existing sellers."
            ),
            sample_df=affected,
            sample_columns=[
                "order_id",
                "order_item_id",
                "seller_id",
            ],
        )
    )

    return results