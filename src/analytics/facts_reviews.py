from pathlib import Path

import polars as pl

from src.analytics.config import (
    ANALYTICAL_DATA_DIR,
    REVIEWS_FILE,
)


FACT_REVIEWS_FILE = ANALYTICAL_DATA_DIR / "fact_order_reviews.parquet"


def build_fact_order_reviews() -> pl.DataFrame:
    """
    Build the analytical fact table for order reviews.

    Grain:
        One row per review_id + order_id combination.

    Important:
        review_id is NOT treated as a unique primary key because
        the source data contains review_id values associated with
        multiple orders.

        The validated business key is:
            (review_id, order_id)

    No source rows are deduplicated or removed.
    """

    reviews = pl.read_csv(REVIEWS_FILE)

    required_columns = [
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in reviews.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required review columns: {missing_columns}"
        )

    fact = reviews.select(required_columns)

    # ---------------------------------------------------------
    # Basic null validation
    # ---------------------------------------------------------

    if fact["review_id"].null_count() > 0:
        raise ValueError(
            "Null review_id values found."
        )

    if fact["order_id"].null_count() > 0:
        raise ValueError(
            "Null order_id values found."
        )

    # ---------------------------------------------------------
    # Business-key validation
    #
    # review_id alone is NOT unique in the source data.
    # The validated business key is review_id + order_id.
    # ---------------------------------------------------------

    duplicate_business_keys = (
        fact
        .group_by(["review_id", "order_id"])
        .len()
        .filter(pl.col("len") > 1)
    )

    if duplicate_business_keys.height > 0:
        raise ValueError(
            "Duplicate review_id + order_id combinations found: "
            f"{duplicate_business_keys.height}"
        )

    # ---------------------------------------------------------
    # Review score validation
    # ---------------------------------------------------------

    invalid_scores = fact.filter(
        (pl.col("review_score") < 1)
        | (pl.col("review_score") > 5)
    )

    if invalid_scores.height > 0:
        raise ValueError(
            "Invalid review_score values found: "
            f"{invalid_scores.height}"
        )

    # ---------------------------------------------------------
    # Preserve all source rows.
    #
    # Do NOT use unique() or deduplicate on review_id.
    # The source contains legitimate repeated review_id values
    # across different orders.
    # ---------------------------------------------------------

    return fact


def write_fact_order_reviews(fact: pl.DataFrame) -> Path:
    """
    Write fact_order_reviews to the analytical layer.
    """

    ANALYTICAL_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fact.write_parquet(FACT_REVIEWS_FILE)

    return FACT_REVIEWS_FILE


def main() -> None:
    fact = build_fact_order_reviews()

    output_path = write_fact_order_reviews(fact)

    print("fact_order_reviews built successfully.")
    print(f"Rows: {fact.height}")
    print(f"Columns: {fact.columns}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()