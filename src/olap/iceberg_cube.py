"""Iceberg Cube utilities for Olist analytical patterns."""

from __future__ import annotations

from itertools import combinations

import pandas as pd


def compute_iceberg_cube(
    df: pd.DataFrame,
    dimensions: list[str],
    min_count: int = 100,
    min_revenue: float | None = None,
    high_bad_review_rate: float | None = None,
) -> pd.DataFrame:
    """Compute iceberg cube across all non-empty combinations of dimensions.

    The cube keeps only groups that satisfy at least one threshold:
    count >= min_count, revenue >= min_revenue, or bad_review_rate >= threshold.
    """
    missing = [dimension for dimension in dimensions if dimension not in df.columns]
    if missing:
        raise KeyError(f"Missing cube dimensions: {missing}")

    work = df.copy()
    work["order_count"] = 1
    if "total_price" not in work.columns:
        work["total_price"] = 0
    if "bad_review" not in work.columns:
        work["bad_review"] = pd.NA
    if "is_delayed" not in work.columns:
        work["is_delayed"] = pd.NA

    cuboids = []
    for size in range(1, len(dimensions) + 1):
        for group_cols in combinations(dimensions, size):
            grouped = (
                work.groupby(list(group_cols), dropna=False)
                .agg(
                    count_orders=("order_count", "sum"),
                    sum_revenue=("total_price", "sum"),
                    avg_review_score=("review_score", "mean"),
                    avg_delivery_days=("delivery_days", "mean"),
                    delay_rate=("is_delayed", "mean"),
                    bad_review_rate=("bad_review", "mean"),
                )
                .reset_index()
            )
            grouped["cuboid"] = " x ".join(group_cols)
            grouped["dimension_count"] = size

            for dimension in dimensions:
                if dimension not in grouped.columns:
                    grouped[dimension] = "ALL"

            keep = grouped["count_orders"] >= min_count
            if min_revenue is not None:
                keep = keep | (grouped["sum_revenue"] >= min_revenue)
            if high_bad_review_rate is not None:
                keep = keep | (
                    (grouped["bad_review_rate"] >= high_bad_review_rate)
                    & (grouped["count_orders"] >= max(20, min_count // 2))
                )
            cuboids.append(grouped.loc[keep])

    if not cuboids:
        return pd.DataFrame()

    ordered_columns = [
        "cuboid",
        "dimension_count",
        *dimensions,
        "count_orders",
        "sum_revenue",
        "avg_review_score",
        "avg_delivery_days",
        "delay_rate",
        "bad_review_rate",
    ]
    result = pd.concat(cuboids, ignore_index=True)
    return result[ordered_columns].sort_values(
        ["dimension_count", "count_orders", "sum_revenue"],
        ascending=[True, False, False],
    )


def compute_default_olist_cubes(order_features: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Return seminar-friendly iceberg cubes for core Olist business themes."""
    cubes = {
        "sales_by_time_category_state": compute_iceberg_cube(
            order_features,
            ["order_year_month", "product_category_name_english", "customer_state"],
            min_count=150,
            min_revenue=15000,
        ),
        "delivery_quality": compute_iceberg_cube(
            order_features,
            ["seller_state", "product_category_name_english", "is_delayed"],
            min_count=100,
            high_bad_review_rate=0.25,
        ),
        "payment_satisfaction": compute_iceberg_cube(
            order_features,
            ["payment_type", "installments_group", "review_group"],
            min_count=100,
            high_bad_review_rate=0.25,
        ),
        "geo_trade_lanes": compute_iceberg_cube(
            order_features,
            ["customer_state", "seller_state", "review_group"],
            min_count=100,
            min_revenue=10000,
        ),
    }
    return cubes
