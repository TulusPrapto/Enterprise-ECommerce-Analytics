from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import polars as pl

from src.analytics.config import (
    ANALYTICAL_DATA_DIR,
    FACT_ORDERS_FILE,
)


# =============================================================
# CONFIGURATION
# =============================================================

DIM_DATE_FILE = ANALYTICAL_DATA_DIR / "dim_date.parquet"


# =============================================================
# DATE DIMENSION
# =============================================================

DATE_COLUMNS = [
    "date_key",
    "date",
    "year",
    "quarter",
    "quarter_number",
    "month",
    "month_number",
    "month_name",
    "year_month",
    "year_month_sort",
    "week",
    "day",
    "day_name",
    "day_of_week",
    "is_weekend",
]


def get_date_range() -> tuple[date, date]:
    """
    Determine the required calendar range from fact_orders.

    Start:
        Minimum order purchase date.

    End:
        Maximum estimated delivery date.

    This ensures the date dimension covers the complete
    analytical reporting period.
    """

    orders = pl.read_parquet(FACT_ORDERS_FILE)

    min_date = (
        orders
        .select(
            pl.col("order_purchase_timestamp")
            .dt.date()
            .min()
            .alias("min_date")
        )
        .item()
    )

    max_estimated_date = (
        orders
        .select(
            pl.col("order_estimated_delivery_date")
            .dt.date()
            .max()
            .alias("max_date")
        )
        .item()
    )

    if min_date is None:
        raise ValueError(
            "Unable to determine minimum purchase date."
        )

    if max_estimated_date is None:
        raise ValueError(
            "Unable to determine maximum estimated delivery date."
        )

    return min_date, max_estimated_date


def build_dim_date() -> pl.DataFrame:
    """
    Build the calendar/date dimension.

    Grain:
        One row per calendar date.
    """

    start_date, end_date = get_date_range()

    number_of_days = (
        end_date - start_date
    ).days + 1

    dates = [
        start_date + timedelta(days=i)
        for i in range(number_of_days)
    ]

    dim_date = (
        pl.DataFrame(
            {
                "date": dates,
            }
        )
        .with_columns(
            [
                pl.col("date")
                .dt.strftime("%Y%m%d")
                .cast(pl.Int32)
                .alias("date_key"),

                pl.col("date")
                .dt.year()
                .alias("year"),

                (
                    ((pl.col("date").dt.month() - 1) // 3) + 1
                )
                .alias("quarter_number"),

                pl.concat_str(
                    [
                        pl.lit("Q"),
                        (
                            ((pl.col("date").dt.month() - 1) // 3) + 1
                        ).cast(pl.String),
                    ]
                )
                .alias("quarter"),

                pl.col("date")
                .dt.month()
                .alias("month"),

                pl.col("date")
                .dt.month()
                .alias("month_number"),

                pl.col("date")
                .dt.strftime("%B")
                .alias("month_name"),

                pl.col("date")
                .dt.strftime("%Y-%m")
                .alias("year_month"),

                (
                    pl.col("date").dt.year() * 100
                    + pl.col("date").dt.month()
                )
                .alias("year_month_sort"),

                pl.col("date")
                .dt.week()
                .alias("week"),

                pl.col("date")
                .dt.day()
                .alias("day"),

                pl.col("date")
                .dt.strftime("%A")
                .alias("day_name"),

                pl.col("date")
                .dt.weekday()
                .alias("day_of_week"),

                (
                    pl.col("date").dt.weekday() >= 6
                )
                .alias("is_weekend"),
            ]
        )
        .select(DATE_COLUMNS)
        .sort("date")
    )

    return dim_date


# =============================================================
# VALIDATION
# =============================================================

def validate_dim_date(
    df: pl.DataFrame,
) -> None:
    """
    Validate the date dimension before persistence.
    """

    required_columns = set(DATE_COLUMNS)

    missing_columns = (
        required_columns - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"dim_date is missing columns: "
            f"{sorted(missing_columns)}"
        )

    if df.height == 0:
        raise ValueError(
            "dim_date contains no rows."
        )

    # ---------------------------------------------------------
    # Date key validation
    # ---------------------------------------------------------

    if df["date_key"].null_count() > 0:
        raise ValueError(
            "dim_date contains null date_key values."
        )

    if (
        df.height
        != df["date_key"].n_unique()
    ):
        raise ValueError(
            "dim_date contains duplicate date_key values."
        )

    # ---------------------------------------------------------
    # Date uniqueness
    # ---------------------------------------------------------

    if (
        df.height
        != df["date"].n_unique()
    ):
        raise ValueError(
            "dim_date contains duplicate dates."
        )

    # ---------------------------------------------------------
    # Calendar continuity
    # ---------------------------------------------------------

    expected_days = (
        df["date"].max()
        - df["date"].min()
    ).days + 1

    if df.height != expected_days:
        raise ValueError(
            "dim_date contains gaps in the calendar."
        )

    # ---------------------------------------------------------
    # Date key consistency
    # ---------------------------------------------------------

    incorrect_date_keys = (
        df.filter(
            pl.col("date_key")
            != pl.col("date")
            .dt.strftime("%Y%m%d")
            .cast(pl.Int32)
        )
        .height
    )

    if incorrect_date_keys != 0:
        raise ValueError(
            f"{incorrect_date_keys} rows have "
            "incorrect date_key values."
        )

    # ---------------------------------------------------------
    # Quarter validation
    # ---------------------------------------------------------

    invalid_quarters = (
        df.filter(
            (
                pl.col("quarter_number") < 1
            )
            | (
                pl.col("quarter_number") > 4
            )
        )
        .height
    )

    if invalid_quarters != 0:
        raise ValueError(
            f"{invalid_quarters} rows have "
            "invalid quarter numbers."
        )

    # ---------------------------------------------------------
    # Month validation
    # ---------------------------------------------------------

    invalid_months = (
        df.filter(
            (
                pl.col("month_number") < 1
            )
            | (
                pl.col("month_number") > 12
            )
        )
        .height
    )

    if invalid_months != 0:
        raise ValueError(
            f"{invalid_months} rows have "
            "invalid month numbers."
        )

    # ---------------------------------------------------------
    # Weekend validation
    # ---------------------------------------------------------

    incorrect_weekends = (
        df.filter(
            pl.col("is_weekend")
            != (
                pl.col("day_of_week") >= 6
            )
        )
        .height
    )

    if incorrect_weekends != 0:
        raise ValueError(
            f"{incorrect_weekends} rows have "
            "incorrect weekend flags."
        )


# =============================================================
# PERSISTENCE
# =============================================================

def save_dim_date(
    df: pl.DataFrame,
    output_dir: Path = ANALYTICAL_DATA_DIR,
) -> Path:
    """
    Persist dim_date as Parquet.
    """

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir / "dim_date.parquet"
    )

    df.write_parquet(output_path)

    return output_path


# =============================================================
# MAIN
# =============================================================

def main() -> None:

    dim_date = build_dim_date()

    validate_dim_date(dim_date)

    output_path = save_dim_date(dim_date)

    print(
        "dim_date built successfully."
    )

    print(
        f"Rows: {dim_date.height}"
    )

    print(
        f"Columns: {dim_date.columns}"
    )

    print(
        f"Start date: "
        f"{dim_date['date'].min()}"
    )

    print(
        f"End date: "
        f"{dim_date['date'].max()}"
    )

    print(
        f"Output: {output_path}"
    )


if __name__ == "__main__":
    main()