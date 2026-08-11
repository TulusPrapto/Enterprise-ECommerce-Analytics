from dataclasses import dataclass
from typing import Literal


Severity = Literal["FAIL", "WARNING", "INFO"]


@dataclass(frozen=True)
class BusinessRule:
    rule_id: str
    dataset: str
    domain: str
    description: str
    severity: Severity


BUSINESS_RULES = [
    BusinessRule(
        rule_id="ORD-001",
        dataset="olist_orders_dataset.csv",
        domain="orders",
        description="Delivered orders should have a customer delivery date.",
        severity="WARNING",
    ),
    BusinessRule(
        rule_id="ORD-002",
        dataset="olist_orders_dataset.csv",
        domain="orders",
        description="Delivered orders should have an estimated delivery date.",
        severity="WARNING",
    ),
    BusinessRule(
        rule_id="ORD-003",
        dataset="olist_orders_dataset.csv",
        domain="orders",
        description="Customer delivery date must not precede purchase timestamp.",
        severity="FAIL",
    ),
    BusinessRule(
        rule_id="ORD-004",
        dataset="olist_orders_dataset.csv",
        domain="orders",
        description="Approval timestamp should not precede purchase timestamp.",
        severity="WARNING",
    ),
    BusinessRule(
        rule_id="ORD-005",
        dataset="olist_orders_dataset.csv",
        domain="orders",
        description="Customer delivery date should not precede carrier delivery date.",
        severity="WARNING",
    ),
    BusinessRule(
        rule_id="ITEM-001",
        dataset="olist_order_items_dataset.csv",
        domain="order_items",
        description="Product price must not be negative.",
        severity="FAIL",
    ),
    BusinessRule(
        rule_id="ITEM-002",
        dataset="olist_order_items_dataset.csv",
        domain="order_items",
        description="Freight value must not be negative.",
        severity="FAIL",
    ),
    BusinessRule(
        rule_id="PAY-001",
        dataset="olist_order_payments_dataset.csv",
        domain="payments",
        description="Payment value should be greater than zero.",
        severity="WARNING",
    ),
    BusinessRule(
        rule_id="PAY-002",
        dataset="olist_order_payments_dataset.csv",
        domain="payments",
        description="Payment sequential must be at least 1.",
        severity="FAIL",
    ),
    BusinessRule(
        rule_id="PAY-003",
        dataset="olist_order_payments_dataset.csv",
        domain="payments",
        description="Payment installments must be at least 1.",
        severity="FAIL",
    ),
    BusinessRule(
        rule_id="REV-001",
        dataset="olist_order_reviews_dataset.csv",
        domain="reviews",
        description="Review score must be between 1 and 5.",
        severity="FAIL",
    ),
    BusinessRule(
        rule_id="PROD-001",
        dataset="olist_products_dataset.csv",
        domain="products",
        description="Product weight should be greater than zero when present.",
        severity="WARNING",
    ),
    BusinessRule(
        rule_id="PROD-002",
        dataset="olist_products_dataset.csv",
        domain="products",
        description="Product dimensions should be greater than zero when present.",
        severity="WARNING",
    ),
    BusinessRule(
        rule_id="REL-001",
        dataset="olist_order_items_dataset.csv",
        domain="relationships",
        description="Every order item must reference an existing order.",
        severity="FAIL",
    ),
    BusinessRule(
        rule_id="REL-002",
        dataset="olist_order_payments_dataset.csv",
        domain="relationships",
        description="Every payment must reference an existing order.",
        severity="FAIL",
    ),
    BusinessRule(
        rule_id="REL-003",
        dataset="olist_order_reviews_dataset.csv",
        domain="relationships",
        description="Every review must reference an existing order.",
        severity="FAIL",
    ),
    BusinessRule(
        rule_id="REL-004",
        dataset="olist_order_items_dataset.csv",
        domain="relationships",
        description="Every order item must reference an existing product.",
        severity="FAIL",
    ),
    BusinessRule(
        rule_id="REL-005",
        dataset="olist_order_items_dataset.csv",
        domain="relationships",
        description="Every order item must reference an existing seller.",
        severity="FAIL",
    ),
]


def get_rule(rule_id: str) -> BusinessRule:
    for rule in BUSINESS_RULES:
        if rule.rule_id == rule_id:
            return rule

    raise KeyError(f"Unknown business rule: {rule_id}")


def get_rules_by_dataset(dataset: str) -> list[BusinessRule]:
    return [
        rule
        for rule in BUSINESS_RULES
        if rule.dataset == dataset
    ]


def get_rules_by_severity(
    severity: Severity,
) -> list[BusinessRule]:
    return [
        rule
        for rule in BUSINESS_RULES
        if rule.severity == severity
    ]