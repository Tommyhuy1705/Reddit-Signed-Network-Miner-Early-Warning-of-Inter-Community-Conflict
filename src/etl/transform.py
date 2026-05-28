"""Cleaning, feature engineering and dimensional modeling for Olist."""

from __future__ import annotations

import numpy as np
import pandas as pd


DATETIME_COLUMNS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": ["shipping_limit_date"],
    "order_reviews": ["review_creation_date", "review_answer_timestamp"],
}


def clean_tables(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Normalize dtypes, categories and missing values without losing business rows."""
    cleaned = {name: df.copy() for name, df in tables.items()}

    for table_name, columns in DATETIME_COLUMNS.items():
        for column in columns:
            cleaned[table_name][column] = pd.to_datetime(cleaned[table_name][column], errors="coerce")

    products = cleaned["products"]
    products["product_category_name"] = products["product_category_name"].fillna("unknown")
    for column in [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]:
        products[column] = pd.to_numeric(products[column], errors="coerce")
        products[column] = products[column].fillna(products[column].median())

    for table_name, columns in {
        "order_items": ["order_item_id", "price", "freight_value"],
        "order_payments": ["payment_sequential", "payment_installments", "payment_value"],
        "order_reviews": ["review_score"],
    }.items():
        for column in columns:
            cleaned[table_name][column] = pd.to_numeric(cleaned[table_name][column], errors="coerce")

    cleaned["category_translation"]["product_category_name"] = cleaned["category_translation"][
        "product_category_name"
    ].fillna("unknown")
    return cleaned


def build_order_features(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Create a one-row-per-order analytical table for EDA, ML and dashboards."""
    tables = clean_tables(tables)
    orders = tables["orders"].copy()
    customers = tables["customers"].copy()
    items = tables["order_items"].copy()
    payments = tables["order_payments"].copy()
    reviews = tables["order_reviews"].copy()
    products = tables["products"].copy()
    sellers = tables["sellers"].copy()
    translation = tables["category_translation"].copy()

    products = products.merge(translation, on="product_category_name", how="left")
    products["product_category_name_english"] = products["product_category_name_english"].fillna(
        products["product_category_name"]
    )

    items_products = items.merge(
        products[
            [
                "product_id",
                "product_category_name_english",
                "product_weight_g",
                "product_length_cm",
                "product_height_cm",
                "product_width_cm",
            ]
        ],
        on="product_id",
        how="left",
    ).merge(sellers, on="seller_id", how="left")

    category_mode = (
        items_products.groupby("order_id")["product_category_name_english"]
        .agg(lambda s: s.mode().iat[0] if not s.mode().empty else "unknown")
        .rename("product_category_name_english")
    )
    seller_mode = (
        items_products.groupby("order_id")["seller_state"]
        .agg(lambda s: s.mode().iat[0] if not s.mode().empty else "unknown")
        .rename("seller_state")
    )
    item_agg = items_products.groupby("order_id").agg(
        item_count=("order_item_id", "count"),
        unique_product_count=("product_id", "nunique"),
        unique_seller_count=("seller_id", "nunique"),
        total_price=("price", "sum"),
        total_freight=("freight_value", "sum"),
        avg_item_price=("price", "mean"),
        avg_product_weight_g=("product_weight_g", "mean"),
    )
    item_agg = item_agg.join([category_mode, seller_mode]).reset_index()

    payment_type = (
        payments.sort_values(["order_id", "payment_value"], ascending=[True, False])
        .drop_duplicates("order_id")[["order_id", "payment_type", "payment_installments"]]
    )
    payment_agg = payments.groupby("order_id").agg(
        payment_value=("payment_value", "sum"),
        payment_count=("payment_sequential", "count"),
        max_installments=("payment_installments", "max"),
    )
    payment_agg = payment_agg.reset_index().merge(payment_type, on="order_id", how="left")

    review_agg = reviews.sort_values("review_answer_timestamp").groupby("order_id").agg(
        review_score=("review_score", "mean"),
        review_count=("review_id", "count"),
        has_review_comment=("review_comment_message", lambda s: int(s.notna().any())),
    )

    df = (
        orders.merge(customers, on="customer_id", how="left")
        .merge(item_agg, on="order_id", how="left")
        .merge(payment_agg, on="order_id", how="left")
        .merge(review_agg, on="order_id", how="left")
    )

    df["order_purchase_date"] = df["order_purchase_timestamp"].dt.date
    df["order_year"] = df["order_purchase_timestamp"].dt.year
    df["order_month"] = df["order_purchase_timestamp"].dt.month
    df["order_year_month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    df["order_day_of_week"] = df["order_purchase_timestamp"].dt.day_name()
    df["approval_hours"] = hours_between(df["order_purchase_timestamp"], df["order_approved_at"])
    df["carrier_days"] = days_between(df["order_approved_at"], df["order_delivered_carrier_date"])
    df["delivery_days"] = days_between(df["order_purchase_timestamp"], df["order_delivered_customer_date"])
    df["estimated_delivery_days"] = days_between(
        df["order_purchase_timestamp"], df["order_estimated_delivery_date"]
    )
    df["delay_days"] = days_between(df["order_estimated_delivery_date"], df["order_delivered_customer_date"])
    df["is_delayed"] = (df["delay_days"] > 0).astype("Int64")
    df["freight_ratio"] = np.where(df["total_price"] > 0, df["total_freight"] / df["total_price"], np.nan)
    df["review_group"] = pd.cut(
        df["review_score"],
        bins=[0, 2, 3, 5],
        labels=["bad", "neutral", "good"],
        include_lowest=True,
    ).astype("object")
    df["bad_review"] = np.select(
        [df["review_score"] <= 2, df["review_score"] >= 4],
        [1, 0],
        default=np.nan,
    )
    df["installments_group"] = pd.cut(
        df["max_installments"].fillna(0),
        bins=[-1, 1, 3, 6, 24],
        labels=["single", "2-3", "4-6", "7+"],
    ).astype("object")

    fill_zero = [
        "item_count",
        "unique_product_count",
        "unique_seller_count",
        "total_price",
        "total_freight",
        "payment_value",
        "payment_count",
        "max_installments",
    ]
    for column in fill_zero:
        df[column] = df[column].fillna(0)
    for column in ["product_category_name_english", "seller_state", "payment_type"]:
        df[column] = df[column].fillna("unknown")

    return df


def build_model_dataset(order_features: pd.DataFrame) -> pd.DataFrame:
    """Filter and select columns for bad-review classification."""
    model_columns = [
        "order_id",
        "bad_review",
        "total_price",
        "total_freight",
        "freight_ratio",
        "payment_type",
        "max_installments",
        "item_count",
        "unique_product_count",
        "unique_seller_count",
        "product_category_name_english",
        "customer_state",
        "seller_state",
        "delivery_days",
        "delay_days",
        "is_delayed",
        "order_month",
        "order_day_of_week",
        "approval_hours",
        "carrier_days",
    ]
    df = order_features[model_columns].copy()
    df = df[df["bad_review"].notna()].copy()
    df["bad_review"] = df["bad_review"].astype(int)
    return df


def build_star_schema(tables: dict[str, pd.DataFrame], order_features: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Build a compact star schema for PostgreSQL/SQL Server loading."""
    tables = clean_tables(tables)
    items = tables["order_items"].copy()
    products = tables["products"].merge(tables["category_translation"], on="product_category_name", how="left")
    products["product_category_name_english"] = products["product_category_name_english"].fillna(
        products["product_category_name"]
    )

    fact = items.merge(
        order_features[
            [
                "order_id",
                "customer_id",
                "order_purchase_date",
                "order_status",
                "payment_type",
                "max_installments",
                "review_score",
                "delivery_days",
                "delay_days",
                "is_delayed",
                "bad_review",
            ]
        ],
        on="order_id",
        how="left",
    )
    fact["fact_order_item_id"] = np.arange(1, len(fact) + 1)
    fact["date_key"] = pd.to_datetime(fact["order_purchase_date"], errors="coerce").dt.strftime("%Y%m%d")
    fact["payment_key"] = fact["payment_type"].fillna("unknown") + "_" + fact["max_installments"].fillna(0).astype(
        int
    ).astype(str)
    fact = fact[
        [
            "fact_order_item_id",
            "order_id",
            "order_item_id",
            "date_key",
            "customer_id",
            "seller_id",
            "product_id",
            "payment_key",
            "order_status",
            "price",
            "freight_value",
            "review_score",
            "delivery_days",
            "delay_days",
            "is_delayed",
            "bad_review",
        ]
    ]

    dim_date = make_dim_date(order_features["order_purchase_timestamp"])
    dim_customer = tables["customers"].drop_duplicates("customer_id")
    dim_seller = tables["sellers"].drop_duplicates("seller_id")
    dim_product = products.drop_duplicates("product_id")
    dim_payment = (
        order_features[["payment_type", "max_installments", "installments_group"]]
        .drop_duplicates()
        .assign(
            payment_type=lambda d: d["payment_type"].fillna("unknown"),
            max_installments=lambda d: d["max_installments"].fillna(0).astype(int),
        )
    )
    dim_payment["payment_key"] = dim_payment["payment_type"] + "_" + dim_payment["max_installments"].astype(str)
    dim_payment = dim_payment[["payment_key", "payment_type", "max_installments", "installments_group"]]
    dim_status = pd.DataFrame({"order_status": sorted(order_features["order_status"].dropna().unique())})

    return {
        "dim_date": dim_date,
        "dim_customer": dim_customer,
        "dim_seller": dim_seller,
        "dim_product": dim_product,
        "dim_payment": dim_payment,
        "dim_order_status": dim_status,
        "fact_order_items": fact,
    }


def make_dim_date(series: pd.Series) -> pd.DataFrame:
    dates = pd.to_datetime(series, errors="coerce").dt.normalize().dropna().drop_duplicates().sort_values()
    dim = pd.DataFrame({"date": dates})
    dim["date_key"] = dim["date"].dt.strftime("%Y%m%d")
    dim["year"] = dim["date"].dt.year
    dim["quarter"] = dim["date"].dt.quarter
    dim["month"] = dim["date"].dt.month
    dim["day"] = dim["date"].dt.day
    dim["day_of_week"] = dim["date"].dt.day_name()
    return dim[["date_key", "date", "year", "quarter", "month", "day", "day_of_week"]]


def days_between(start: pd.Series, end: pd.Series) -> pd.Series:
    return (end - start).dt.total_seconds() / 86400


def hours_between(start: pd.Series, end: pd.Series) -> pd.Series:
    return (end - start).dt.total_seconds() / 3600
