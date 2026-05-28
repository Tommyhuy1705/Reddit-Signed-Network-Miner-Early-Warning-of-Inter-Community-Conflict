"""Streamlit dashboard for Olist E-Commerce Analytics."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import MODELS_DIR, PROCESSED_DIR, WAREHOUSE_DIR
from src.models.predict import load_model, predict


st.set_page_config(page_title="Olist E-Commerce Analytics", layout="wide")


@st.cache_data
def load_order_features() -> pd.DataFrame:
    path = PROCESSED_DIR / "order_features.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data
def load_cube() -> pd.DataFrame:
    path = WAREHOUSE_DIR / "iceberg_cube_results.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    st.sidebar.header("Filters")
    states = sorted(df["customer_state"].dropna().unique())
    categories = sorted(df["product_category_name_english"].dropna().unique())
    selected_states = st.sidebar.multiselect("Customer state", states, default=states[:8])
    selected_categories = st.sidebar.multiselect("Category", categories, default=categories[:12])
    filtered = df.copy()
    if selected_states:
        filtered = filtered[filtered["customer_state"].isin(selected_states)]
    if selected_categories:
        filtered = filtered[filtered["product_category_name_english"].isin(selected_categories)]
    return filtered


def overview_tab(df: pd.DataFrame) -> None:
    total_orders = df["order_id"].nunique()
    revenue = df["total_price"].sum()
    avg_review = df["review_score"].mean()
    delay_rate = df["is_delayed"].mean()
    bad_review_rate = df["bad_review"].mean()

    cols = st.columns(5)
    cols[0].metric("Orders", f"{total_orders:,.0f}")
    cols[1].metric("Revenue", f"{revenue:,.0f} BRL")
    cols[2].metric("Avg review", f"{avg_review:.2f}")
    cols[3].metric("Delay rate", f"{delay_rate:.1%}")
    cols[4].metric("Bad review rate", f"{bad_review_rate:.1%}")

    monthly = df.groupby("order_year_month", as_index=False).agg(
        orders=("order_id", "nunique"),
        revenue=("total_price", "sum"),
    )
    st.subheader("Monthly Revenue")
    st.line_chart(monthly.set_index("order_year_month")["revenue"])

    left, right = st.columns(2)
    status = df["order_status"].value_counts().reset_index()
    status.columns = ["order_status", "orders"]
    left.subheader("Order Status")
    left.bar_chart(status.set_index("order_status")["orders"])
    reviews = df["review_score"].value_counts().sort_index().reset_index()
    reviews.columns = ["review_score", "orders"]
    right.subheader("Review Score Distribution")
    right.bar_chart(reviews.set_index("review_score")["orders"])


def eda_tab(df: pd.DataFrame) -> None:
    top_categories = (
        df.groupby("product_category_name_english", as_index=False)
        .agg(revenue=("total_price", "sum"), orders=("order_id", "nunique"), review=("review_score", "mean"))
        .sort_values("revenue", ascending=False)
        .head(20)
    )
    st.subheader("Top Categories by Revenue")
    st.bar_chart(top_categories.set_index("product_category_name_english")["revenue"])

    left, right = st.columns(2)
    payment = df.groupby("payment_type", as_index=False).agg(orders=("order_id", "nunique"), revenue=("total_price", "sum"))
    left.subheader("Payment Mix")
    left.bar_chart(payment.set_index("payment_type")["orders"])
    geo = df.groupby("customer_state", as_index=False).agg(revenue=("total_price", "sum"), orders=("order_id", "nunique"))
    right.subheader("Revenue by Customer State")
    right.bar_chart(geo.sort_values("revenue", ascending=False).set_index("customer_state")["revenue"])

    delivery = (
        df.groupby("product_category_name_english", as_index=False)
        .agg(delay_rate=("is_delayed", "mean"), avg_delivery_days=("delivery_days", "mean"), orders=("order_id", "nunique"))
        .query("orders >= 100")
        .sort_values("delay_rate", ascending=False)
        .head(20)
    )
    st.subheader("Highest Delay Rate Categories")
    st.bar_chart(delivery.set_index("product_category_name_english")["delay_rate"])


def cube_tab() -> None:
    cube = load_cube()
    if cube.empty:
        st.warning("No cube output found. Run `python scripts/run_iceberg_cube.py` first.")
        return
    themes = sorted(cube["cube_theme"].dropna().unique()) if "cube_theme" in cube.columns else []
    theme = st.selectbox("Cube theme", themes) if themes else None
    shown = cube[cube["cube_theme"] == theme] if theme else cube
    sort_col = st.selectbox("Sort by", ["count_orders", "sum_revenue", "bad_review_rate", "delay_rate"])
    st.dataframe(shown.sort_values(sort_col, ascending=False).head(200), use_container_width=True)


def prediction_tab(df: pd.DataFrame) -> None:
    model_path = MODELS_DIR / "bad_review_classifier.pkl"
    if not model_path.exists():
        st.warning("No trained model found. Run `python scripts/train_bad_review_model.py` first.")
        return

    categories = sorted(df["product_category_name_english"].dropna().unique())
    states = sorted(df["customer_state"].dropna().unique())
    weekdays = sorted(df["order_day_of_week"].dropna().unique())
    payments = sorted(df["payment_type"].dropna().unique())

    left, right = st.columns(2)
    row = {
        "total_price": left.number_input("Total price", min_value=0.0, value=120.0),
        "total_freight": right.number_input("Freight", min_value=0.0, value=20.0),
        "payment_type": left.selectbox("Payment type", payments, index=payments.index("credit_card") if "credit_card" in payments else 0),
        "max_installments": right.number_input("Installments", min_value=0, max_value=24, value=1),
        "item_count": left.number_input("Item count", min_value=1, max_value=30, value=1),
        "unique_product_count": right.number_input("Unique products", min_value=1, max_value=30, value=1),
        "unique_seller_count": left.number_input("Unique sellers", min_value=1, max_value=10, value=1),
        "product_category_name_english": right.selectbox("Category", categories),
        "customer_state": left.selectbox("Customer state", states, index=states.index("SP") if "SP" in states else 0),
        "seller_state": right.selectbox("Seller state", states, index=states.index("SP") if "SP" in states else 0),
        "delivery_days": left.number_input("Delivery days", value=7.0),
        "delay_days": right.number_input("Delay days", value=0.0),
        "is_delayed": int(right.checkbox("Delayed", value=False)),
        "order_month": left.slider("Order month", 1, 12, 6),
        "order_day_of_week": right.selectbox("Order day", weekdays),
        "approval_hours": left.number_input("Approval hours", value=1.0),
        "carrier_days": right.number_input("Carrier days", value=2.0),
    }
    row["freight_ratio"] = row["total_freight"] / row["total_price"] if row["total_price"] else 0

    if st.button("Predict bad review risk"):
        result = predict(load_model(), pd.DataFrame([row])).iloc[0]
        st.metric("Bad review probability", f"{result['bad_review_probability']:.1%}")
        st.write("Prediction:", "Bad review risk" if result["bad_review_prediction"] == 1 else "Low risk")


def main() -> None:
    st.title("Olist E-Commerce Analytics")
    df = load_order_features()
    if df.empty:
        st.info("Run `python scripts/build_processed.py` to create processed data before using the dashboard.")
        return

    filtered = sidebar_filters(df)
    tab_overview, tab_eda, tab_cube, tab_predict = st.tabs(["Overview", "EDA", "Iceberg Cube", "Prediction"])
    with tab_overview:
        overview_tab(filtered)
    with tab_eda:
        eda_tab(filtered)
    with tab_cube:
        cube_tab()
    with tab_predict:
        prediction_tab(df)


if __name__ == "__main__":
    main()
