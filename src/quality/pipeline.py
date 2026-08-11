from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.cleaning.cleaners import read_csv
from src.cleaning.config import PROCESSED_DATA_DIR
from src.quality.scoring import calculate_quality_score
from src.quality.validators import (
    validate_orders,
    validate_order_items,
    validate_payments,
    validate_reviews,
    validate_products,
    validate_relationships,
)


REPORT_DIR = Path("reports/quality")
REPORT_PATH = REPORT_DIR / "business_quality_report.json"


DATASET_VALIDATORS = {
    "olist_orders_dataset.csv": validate_orders,
    "olist_order_items_dataset.csv": validate_order_items,
    "olist_order_payments_dataset.csv": validate_payments,
    "olist_order_reviews_dataset.csv": validate_reviews,
    "olist_products_dataset.csv": validate_products,
}


def serialize_result(result):
    """Convert RuleResult into JSON-safe dictionary."""
    return {
        "rule_id": result.rule_id,
        "dataset": result.dataset,
        "severity": result.severity,
        "passed": result.passed,
        "evaluated_rows": result.evaluated_rows,
        "affected_rows": result.affected_rows,
        "message": result.message,
        "sample": result.sample,
    }


def run_quality_pipeline():
    """
    Execute all Business Data Quality rules and generate
    business_quality_report.json.
    """

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # 1. Read processed datasets
    # ---------------------------------------------------------

    datasets = {}

    for dataset_name in [
        "olist_orders_dataset.csv",
        "olist_order_items_dataset.csv",
        "olist_order_payments_dataset.csv",
        "olist_order_reviews_dataset.csv",
        "olist_products_dataset.csv",
        "olist_sellers_dataset.csv",
    ]:
        path = PROCESSED_DATA_DIR / dataset_name

        if not path.exists():
            raise FileNotFoundError(
                f"Processed dataset not found: {path}"
            )

        datasets[dataset_name] = read_csv(path)

    # ---------------------------------------------------------
    # 2. Dataset-level business rules
    # ---------------------------------------------------------

    results = []

    for dataset_name, validator in DATASET_VALIDATORS.items():
        df = datasets[dataset_name]

        dataset_results = validator(df)

        results.extend(dataset_results)

    # ---------------------------------------------------------
    # 3. Relationship rules
    # ---------------------------------------------------------

    relationship_results = validate_relationships(
        orders=datasets["olist_orders_dataset.csv"],
        order_items=datasets["olist_order_items_dataset.csv"],
        payments=datasets["olist_order_payments_dataset.csv"],
        reviews=datasets["olist_order_reviews_dataset.csv"],
        products=datasets["olist_products_dataset.csv"],
        sellers=datasets["olist_sellers_dataset.csv"],
    )

    results.extend(relationship_results)

    # ---------------------------------------------------------
    # 4. Calculate quality score
    # ---------------------------------------------------------

    score = calculate_quality_score(results)

    # ---------------------------------------------------------
    # 5. Build rule summary
    # ---------------------------------------------------------

    rule_summary = []

    for result in results:
        rule_summary.append(
            serialize_result(result)
        )

    # ---------------------------------------------------------
    # 6. Build dataset summary
    # ---------------------------------------------------------

    dataset_summary = {}

    for result in results:
        dataset = result.dataset

        if dataset not in dataset_summary:
            dataset_summary[dataset] = {
                "total_rules": 0,
                "passed_rules": 0,
                "failed_rules": 0,
                "affected_rows": 0,
            }

        dataset_summary[dataset]["total_rules"] += 1

        if result.passed:
            dataset_summary[dataset]["passed_rules"] += 1
        else:
            dataset_summary[dataset]["failed_rules"] += 1
            dataset_summary[dataset]["affected_rows"] += (
                result.affected_rows
            )

    # ---------------------------------------------------------
    # 7. Overall summary
    # ---------------------------------------------------------

    summary = {
        "total_rules": score.total_rules,
        "passed_rules": score.passed_rules,
        "failed_rules": score.failed_rules,
        "warning_failures": score.warning_failures,
        "critical_failures": score.critical_failures,
        "quality_score": score.score,
        "grade": score.grade,
        "status": score.status,
    }

    # ---------------------------------------------------------
    # 8. Failed rules summary
    # ---------------------------------------------------------

    failed_rules = [
        serialize_result(result)
        for result in results
        if not result.passed
    ]

    # ---------------------------------------------------------
    # 9. Build final report
    # ---------------------------------------------------------

    report = {
        "metadata": {
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "data_modified": False,
            "source": "data/processed",
        },
        "summary": summary,
        "dataset_summary": dataset_summary,
        "failed_rules": failed_rules,
        "rules": rule_summary,
    }

    # ---------------------------------------------------------
    # 10. Write JSON report
    # ---------------------------------------------------------

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return report


def main():
    report = run_quality_pipeline()

    summary = report["summary"]

    print("Business Data Quality pipeline completed.")
    print(f"Rules evaluated: {summary['total_rules']}")
    print(f"Rules passed: {summary['passed_rules']}")
    print(f"Rules failed: {summary['failed_rules']}")
    print(f"Warning failures: {summary['warning_failures']}")
    print(f"Critical failures: {summary['critical_failures']}")
    print(f"Quality score: {summary['quality_score']}")
    print(f"Grade: {summary['grade']}")
    print(f"Status: {summary['status']}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
