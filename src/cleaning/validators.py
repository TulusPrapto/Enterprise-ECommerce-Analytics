from __future__ import annotations

from dataclasses import dataclass

import polars as pl


@dataclass
class ValidationResult:
    dataset: str
    passed: bool
    checks: list[dict]


def validate_not_empty(
    df: pl.DataFrame,
    dataset: str,
) -> dict:
    row_count = df.height

    return {
        "check": "not_empty",
        "passed": row_count > 0,
        "row_count": row_count,
        "message": (
            "Dataset contains rows."
            if row_count > 0
            else "Dataset is empty."
        ),
    }


def validate_required_columns(
    df: pl.DataFrame,
    dataset: str,
    required_columns: list[str],
) -> dict:
    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    return {
        "check": "required_columns",
        "passed": len(missing_columns) == 0,
        "missing_columns": missing_columns,
        "message": (
            "All required columns are present."
            if not missing_columns
            else f"Missing columns: {missing_columns}"
        ),
    }


def validate_row_count_preserved(
    raw_df: pl.DataFrame,
    cleaned_df: pl.DataFrame,
) -> dict:
    raw_count = raw_df.height
    cleaned_count = cleaned_df.height

    return {
        "check": "row_count_preserved",
        "passed": raw_count == cleaned_count,
        "raw_row_count": raw_count,
        "cleaned_row_count": cleaned_count,
        "message": (
            "Row count preserved."
            if raw_count == cleaned_count
            else "Row count changed during cleaning."
        ),
    }


def validate_primary_key(
    df: pl.DataFrame,
    primary_key: str,
) -> dict:
    if primary_key not in df.columns:
        return {
            "check": "primary_key",
            "passed": False,
            "primary_key": primary_key,
            "message": f"Primary key column '{primary_key}' not found.",
        }

    null_count = df.select(
        pl.col(primary_key).is_null().sum()
    ).item()

    duplicate_count = (
        df.height
        - df.select(pl.col(primary_key).n_unique()).item()
    )

    passed = (
        null_count == 0
        and duplicate_count == 0
    )

    return {
        "check": "primary_key",
        "passed": passed,
        "primary_key": primary_key,
        "null_count": null_count,
        "duplicate_count": duplicate_count,
        "message": (
            "Primary key is valid."
            if passed
            else "Primary key contains NULL or duplicate values."
        ),
    }


def validate_primary_key(
    df: pl.DataFrame,
    primary_key: str | list[str] | tuple[str, ...] | None,
) -> dict:
    """
    Validate a single-column or composite primary key.
    """

    if not primary_key:
        return {
            "check": "primary_key",
            "passed": True,
            "primary_key": None,
            "message": "No primary key constraint defined.",
        }

    if isinstance(primary_key, str):
        columns = [primary_key]
    else:
        columns = list(primary_key)

    missing_columns = [
        column
        for column in columns
        if column not in df.columns
    ]

    if missing_columns:
        return {
            "check": "primary_key",
            "passed": False,
            "primary_key": columns,
            "missing_columns": missing_columns,
            "message": "Primary key column(s) not found.",
        }

    null_count = (
        df.select(
            pl.any_horizontal(
                pl.col(column).is_null()
                for column in columns
            )
        )
        .to_series()
        .sum()
    )

    duplicate_count = (
        df.height
        - df.select(columns).unique().height
    )

    passed = (
        null_count == 0
        and duplicate_count == 0
    )

    return {
        "check": "primary_key",
        "passed": passed,
        "primary_key": columns,
        "null_count": null_count,
        "duplicate_count": duplicate_count,
        "message": (
            "Primary key is valid."
            if passed
            else "Primary key contains null or duplicate values."
        ),
    }

def validate_dataset(
    raw_df: pl.DataFrame,
    cleaned_df: pl.DataFrame,
    dataset: str,
    *,
    required_columns: list[str] | None = None,
    primary_key: str | None = None,
) -> ValidationResult:

    checks = []

    checks.append(
        validate_not_empty(
            cleaned_df,
            dataset,
        )
    )

    if required_columns:
        checks.append(
            validate_required_columns(
                cleaned_df,
                dataset,
                required_columns,
            )
        )

    checks.append(
        validate_row_count_preserved(
            raw_df,
            cleaned_df,
        )
    )

    if primary_key:
        checks.append(
            validate_primary_key(
                cleaned_df,
                primary_key,
            )
        )

    passed = all(
        check["passed"]
        for check in checks
    )

    return ValidationResult(
        dataset=dataset,
        passed=passed,
        checks=checks,
    )