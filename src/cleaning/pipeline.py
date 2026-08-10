from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from src.cleaning.cleaners import standardize_dataset, read_csv
from src.cleaning.config import (
    CLEANING_REPORT_DIR,
    DATASETS,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
)
from src.cleaning.contracts import DATASET_CONTRACTS
from src.cleaning.validators import validate_dataset


def clean_dataset(
    file_name: str,
    *,
    write_output: bool = True,
) -> dict:
    """
    Run the deterministic v1 cleaning process for one dataset.

    v1 intentionally performs only safe structural standardization:
    - load CSV
    - normalize configured text columns
    - convert empty strings to null
    - validate the cleaned dataset
    - optionally write processed CSV

    No rows are deleted and no values are imputed.
    """

    contract = DATASET_CONTRACTS[file_name]

    raw_path = RAW_DATA_DIR / file_name
    processed_path = PROCESSED_DATA_DIR / file_name

    print(f"Cleaning: {file_name}")

    raw_df = read_csv(raw_path)

    cleaned_df = standardize_dataset(
        raw_df,
        text_columns=list(contract.text_columns),
    )

    validation = validate_dataset(
        raw_df,
        cleaned_df,
        file_name,
        required_columns=list(contract.required_columns),
        primary_key=list(contract.primary_key) if contract.primary_key else None,
    )

    if not validation.passed:
        raise RuntimeError(
            f"Validation failed for {file_name}: "
            f"{validation.checks}"
        )

    if write_output:
        PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        cleaned_df.write_csv(processed_path)

    return {
        "file_name": file_name,
        "raw_row_count": raw_df.height,
        "cleaned_row_count": cleaned_df.height,
        "column_count": cleaned_df.width,
        "output_path": str(processed_path),
        "validation_passed": validation.passed,
        "checks": validation.checks,
    }


def run_pipeline() -> dict:
    """
    Run cleaning pipeline for all registered datasets.
    """

    started_at = datetime.now(timezone.utc)

    CLEANING_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    for file_name in DATASETS:
        result = clean_dataset(file_name)
        results.append(result)

    completed_at = datetime.now(timezone.utc)

    report = {
        "metadata": {
            "pipeline": "deterministic_cleaning_v1",
            "dataset_count": len(results),
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
        },
        "summary": {
            "datasets_processed": len(results),
            "datasets_passed": sum(
                1 for result in results
                if result["validation_passed"]
            ),
            "datasets_failed": sum(
                1 for result in results
                if not result["validation_passed"]
            ),
        },
        "datasets": results,
    }

    report_path = CLEANING_REPORT_DIR / "cleaning_run_report.json"

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(f"Cleaning completed: {len(results)} datasets")
    print(f"Report: {report_path}")

    return report


if __name__ == "__main__":
    run_pipeline()