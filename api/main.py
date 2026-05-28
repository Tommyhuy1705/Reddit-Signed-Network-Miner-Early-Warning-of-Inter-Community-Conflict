"""FastAPI service for the Olist analytics project."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.config import MODELS_DIR, PROCESSED_DIR, WAREHOUSE_DIR
from src.models.predict import load_model, predict

app = FastAPI(title="Olist E-Commerce Analytics API")


class PredictionRequest(BaseModel):
    total_price: float
    total_freight: float
    freight_ratio: float | None = None
    payment_type: str = "credit_card"
    max_installments: int = 1
    item_count: int = 1
    unique_product_count: int = 1
    unique_seller_count: int = 1
    product_category_name_english: str = "unknown"
    customer_state: str = "SP"
    seller_state: str = "SP"
    delivery_days: float = 7.0
    delay_days: float = 0.0
    is_delayed: int = 0
    order_month: int = 1
    order_day_of_week: str = "Monday"
    approval_hours: float = 1.0
    carrier_days: float = 2.0


@app.get("/health")
async def health():
    return {"status": "ok", "project": "olist-ecommerce-analytics"}


@app.get("/summary")
async def summary():
    path = PROCESSED_DIR / "dataset_summary.csv"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Run scripts/build_processed.py first.")
    return pd.read_csv(path).to_dict(orient="records")


@app.get("/metrics")
async def metrics():
    path = MODELS_DIR / "bad_review_metrics.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Run scripts/train_bad_review_model.py first.")
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/cube")
async def cube(limit: int = 100):
    path = WAREHOUSE_DIR / "iceberg_cube_results.csv"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Run scripts/run_iceberg_cube.py first.")
    return pd.read_csv(path).head(limit).to_dict(orient="records")


@app.post("/predict")
async def predict_bad_review(payload: PredictionRequest):
    try:
        bundle = load_model()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    row = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    if row["freight_ratio"] is None:
        row["freight_ratio"] = row["total_freight"] / row["total_price"] if row["total_price"] else 0
    result = predict(bundle, pd.DataFrame([row])).iloc[0].to_dict()
    return result
