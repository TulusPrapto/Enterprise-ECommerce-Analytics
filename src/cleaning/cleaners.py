from __future__ import annotations

from typing import Callable

import polars as pl


def read_csv(file_path) -> pl.DataFrame:
    """
    Load a raw CSV dataset into a Polars DataFrame.

    Raw files are read only; this function never modifies them.
    """
    return pl.read_csv(
        file_path,
        infer_schema_length=10_000,
        null_values=["", "NULL", "null"],
    )


def normalize_text_columns(
    df: pl.DataFrame,
    columns: list[str],
) -> pl.DataFrame:
    """
    Trim leading/trailing whitespace from selected string columns.

    Only existing columns are transformed.
    """
    existing_columns = [
        column
        for column in columns
        if column in df.columns
        and df.schema[column] == pl.String
    ]

    if not existing_columns:
        return df

    return df.with_columns(
        [
            pl.col(column).str.strip_chars().alias(column)
            for column in existing_columns
        ]
    )


def normalize_empty_strings(
    df: pl.DataFrame,
    columns: list[str],
) -> pl.DataFrame:
    """
    Convert empty or whitespace-only strings into NULL.

    Only existing string columns are transformed.
    """
    existing_columns = [
        column
        for column in columns
        if column in df.columns
        and df.schema[column] == pl.String
    ]

    if not existing_columns:
        return df

    return df.with_columns(
        [
            pl.when(pl.col(column).str.strip_chars() == "")
            .then(None)
            .otherwise(pl.col(column))
            .alias(column)
            for column in existing_columns
        ]
    )


def cast_datetime_columns(
    df: pl.DataFrame,
    columns: list[str],
) -> pl.DataFrame:
    """
    Convert selected columns from String to Datetime.

    Invalid values become NULL rather than crashing the pipeline.
    """
    existing_columns = [
        column
        for column in columns
        if column in df.columns
    ]

    if not existing_columns:
        return df

    return df.with_columns(
        [
            pl.col(column)
            .str.strptime(
                pl.Datetime,
                format=None,
                strict=False,
            )
            .alias(column)
            for column in existing_columns
        ]
    )


def standardize_dataset(
    df: pl.DataFrame,
    *,
    text_columns: list[str] | None = None,
    datetime_columns: list[str] | None = None,
) -> pl.DataFrame:
    """
    Apply generic, business-safe standardization to a dataset.
    """
    text_columns = text_columns or []
    datetime_columns = datetime_columns or []

    result = df

    result = normalize_text_columns(
        result,
        text_columns,
    )

    result = normalize_empty_strings(
        result,
        text_columns,
    )

    result = cast_datetime_columns(
        result,
        datetime_columns,
    )

    return result


def get_dataset_transformer(
    file_name: str,
) -> Callable[[pl.DataFrame], pl.DataFrame]:
    """
    Return the transformation function appropriate for a dataset.

    Dataset-specific rules will be added incrementally.
    """
    return lambda df: df