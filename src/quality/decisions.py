from dataclasses import dataclass


@dataclass(frozen=True)
class BusinessDecision:
    rule_id: str
    decision: str
    treatment: str
    business_impact: str
    rationale: str


BUSINESS_DECISIONS = (
    BusinessDecision(
        rule_id="ORD-001",
        decision="ACCEPT_WITH_CAVEAT",
        treatment="FLAG_INCOMPLETE_DELIVERY_RECORD",
        business_impact="LOW",
        rationale=(
            "Only 8 delivered orders are affected. "
            "Most still contain carrier delivery information and "
            "all affected records contain estimated delivery dates. "
            "Actual customer delivery date should not be imputed."
        ),
    ),
    BusinessDecision(
        rule_id="ORD-005",
        decision="FLAG_INVESTIGATE",
        treatment="RETAIN_AND_FLAG",
        business_impact="MEDIUM",
        rationale=(
            "23 delivered orders contain customer delivery dates "
            "earlier than carrier delivery dates. The anomaly has a "
            "median gap of approximately 1.66 days and a maximum gap "
            "of approximately 16.10 days, so automatic correction "
            "would risk altering historical evidence."
        ),
    ),
    BusinessDecision(
        rule_id="PAY-001",
        decision="REVIEW_RULE",
        treatment="RETAIN_ZERO_VALUE_PAYMENT",
        business_impact="MEDIUM",
        rationale=(
            "All 9 affected records have payment_value equal to zero "
            "and none are negative. Several records use voucher or "
            "not_defined payment types, and some affected orders "
            "contain multiple payment records. The exception should "
            "therefore be interpreted as a business anomaly rather "
            "than automatically classified as invalid payment data."
        ),
    ),
    BusinessDecision(
        rule_id="PAY-003",
        decision="FAIL_INVESTIGATE",
        treatment="RETAIN_AND_FLAG",
        business_impact="HIGH",
        rationale=(
            "Two payment records contain payment_installments equal "
            "to zero while having positive payment values. This is "
            "inconsistent with the expected installment semantics and "
            "should remain an explicit data-quality failure."
        ),
    ),
    BusinessDecision(
        rule_id="PROD-001",
        decision="FLAG",
        treatment="RETAIN_AND_FLAG",
        business_impact="MEDIUM",
        rationale=(
            "Four products have zero product weight and all four "
            "appear in order_items. The anomaly can affect logistics "
            "and freight analysis. Weight should not be imputed without "
            "an authoritative product source."
        ),
    ),
)


def get_decision(rule_id: str) -> BusinessDecision:
    for decision in BUSINESS_DECISIONS:
        if decision.rule_id == rule_id:
            return decision

    raise KeyError(f"Unknown rule_id: {rule_id}")

# ==========================
import json
from pathlib import Path


DECISION_REPORT_PATH = Path(
    "reports/quality/business_decision_register.json"
)


def build_decision_register() -> dict:
    return {
        "metadata": {
            "data_modified": False,
            "decision_count": len(BUSINESS_DECISIONS),
            "purpose": (
                "Document business treatment and analytical implications "
                "for identified data quality exceptions."
            ),
        },
        "decisions": [
            {
                "rule_id": decision.rule_id,
                "decision": decision.decision,
                "treatment": decision.treatment,
                "business_impact": decision.business_impact,
                "rationale": decision.rationale,
            }
            for decision in BUSINESS_DECISIONS
        ],
    }


def write_decision_register() -> None:
    DECISION_REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = build_decision_register()

    DECISION_REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("Business decision register generated.")
    print(f"Decisions: {len(BUSINESS_DECISIONS)}")
    print(f"Report: {DECISION_REPORT_PATH}")


if __name__ == "__main__":
    write_decision_register()