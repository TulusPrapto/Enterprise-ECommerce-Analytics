from dataclasses import dataclass
from typing import Iterable

from src.quality.validators import RuleResult


@dataclass(frozen=True)
class QualityScore:
    total_rules: int
    passed_rules: int
    failed_rules: int
    warning_failures: int
    critical_failures: int
    score: float
    grade: str
    status: str


def calculate_quality_score(results: Iterable[RuleResult]) -> QualityScore:
    results = list(results)

    total_rules = len(results)

    if total_rules == 0:
        return QualityScore(
            total_rules=0,
            passed_rules=0,
            failed_rules=0,
            warning_failures=0,
            critical_failures=0,
            score=100.0,
            grade="A",
            status="PASS",
        )

    failed = [r for r in results if not r.passed]

    warning_failures = sum(
        1 for r in failed if r.severity.upper() == "WARNING"
    )

    critical_failures = sum(
        1 for r in failed if r.severity.upper() == "FAIL"
    )

    passed_rules = total_rules - len(failed)
    failed_rules = len(failed)

    # Weighted scoring:
    # WARNING = 1 penalty
    # FAIL = 3 penalty
    penalty = warning_failures + (critical_failures * 3)

    max_penalty = total_rules * 3

    score = max(
        0.0,
        100.0 * (1 - penalty / max_penalty),
    )

    if score >= 95:
        grade = "A"
    elif score >= 85:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 50:
        grade = "D"
    else:
        grade = "F"

    status = "PASS" if critical_failures == 0 else "REVIEW"

    return QualityScore(
        total_rules=total_rules,
        passed_rules=passed_rules,
        failed_rules=failed_rules,
        warning_failures=warning_failures,
        critical_failures=critical_failures,
        score=round(score, 2),
        grade=grade,
        status=status,
    )