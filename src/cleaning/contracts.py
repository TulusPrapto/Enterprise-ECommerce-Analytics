from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DatasetContract:
    """
    Declarative contract describing the expected structure
    and basic cleaning rules for a raw dataset.
    """

    file_name: str
    required_columns: tuple[str, ...]
    primary_key: tuple[str, ...]
    text_columns: tuple[str, ...] = field(default_factory=tuple)
    datetime_columns: tuple[str, ...] = field(default_factory=tuple)


DATASET_CONTRACTS = {
    "olist_customers_dataset.csv": DatasetContract(
        file_name="olist_customers_dataset.csv",
        required_columns=(
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ),
        primary_key=("customer_id",),
        text_columns=(
            "customer_id",
            "customer_unique_id",
            "customer_city",
            "customer_state",
        ),
    ),

    "olist_orders_dataset.csv": DatasetContract(
        file_name="olist_orders_dataset.csv",
        required_columns=(
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ),
        primary_key=("order_id",),
        text_columns=(
            "order_id",
            "customer_id",
            "order_status",
        ),
        datetime_columns=(
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ),
    ),

    "olist_order_items_dataset.csv": DatasetContract(
        file_name="olist_order_items_dataset.csv",
        required_columns=(
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
        ),
        primary_key=(
            "order_id",
            "order_item_id",
        ),
        text_columns=(
            "order_id",
            "product_id",
            "seller_id",
        ),
        datetime_columns=(
            "shipping_limit_date",
        ),
    ),

    "olist_order_payments_dataset.csv": DatasetContract(
        file_name="olist_order_payments_dataset.csv",
        required_columns=(
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
        ),
        primary_key=(
            "order_id",
            "payment_sequential",
        ),
        text_columns=(
            "order_id",
            "payment_type",
        ),
    ),

    "olist_order_reviews_dataset.csv": DatasetContract(
        file_name="olist_order_reviews_dataset.csv",
        required_columns=(
            "review_id",
            "order_id",
            "review_score",
            "review_comment_title",
            "review_comment_message",
            "review_creation_date",
            "review_answer_timestamp",
        ),
        primary_key=(
            "review_id", 
            "order_id"
        ),
        text_columns=(
            "review_id",
            "order_id",
            "review_comment_title",
            "review_comment_message",
        ),
        datetime_columns=(
            "review_creation_date",
            "review_answer_timestamp",
        ),
    ),

    "olist_products_dataset.csv": DatasetContract(
        file_name="olist_products_dataset.csv",
        required_columns=(
            "product_id",
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ),
        primary_key=("product_id",),
        text_columns=(
            "product_id",
            "product_category_name",
        ),
    ),

    "olist_sellers_dataset.csv": DatasetContract(
        file_name="olist_sellers_dataset.csv",
        required_columns=(
            "seller_id",
            "seller_zip_code_prefix",
            "seller_city",
            "seller_state",
        ),
        primary_key=("seller_id",),
        text_columns=(
            "seller_id",
            "seller_city",
            "seller_state",
        ),
    ),

    "olist_geolocation_dataset.csv": DatasetContract(
        file_name="olist_geolocation_dataset.csv",
        required_columns=(
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state",
        ),
        # This dataset contains repeated ZIP-prefix records.
        # Therefore the ZIP prefix is the business lookup key,
        # not a unique physical row identifier.
        primary_key=(),
        text_columns=(
            "geolocation_city",
            "geolocation_state",
        ),
    ),

    "product_category_name_translation.csv": DatasetContract(
        file_name="product_category_name_translation.csv",
        required_columns=(
            "product_category_name",
            "product_category_name_english",
        ),
        primary_key=("product_category_name",),
        text_columns=(
            "product_category_name",
            "product_category_name_english",
        ),
    ),
}


def get_contract(file_name: str) -> DatasetContract:
    """
    Return the contract for a registered dataset.
    """
    try:
        return DATASET_CONTRACTS[file_name]
    except KeyError as exc:
        raise ValueError(
            f"No dataset contract registered for: {file_name}"
        ) from exc