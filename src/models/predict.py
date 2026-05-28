"""Inference helpers for the Olist bad-review classifier."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from src.config import MODELS_DIR


DEFAULT_MODEL_PATH = MODELS_DIR / "bad_review_classifier.pkl"


def load_model(model_path: Path = DEFAULT_MODEL_PATH) -> dict:
    """Load the persisted classifier bundle."""
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    return joblib.load(model_path)


def predict(model_bundle: dict, rows: pd.DataFrame) -> pd.DataFrame:
    """Return class and probability predictions for input rows."""
    pipeline = model_bundle["pipeline"]
    features = model_bundle["features"]
    X = rows[features].copy()
    prediction = pipeline.predict(X)
    if hasattr(pipeline, "predict_proba"):
        probability = pipeline.predict_proba(X)[:, 1]
    else:
        probability = [None] * len(X)
    return pd.DataFrame(
        {
            "bad_review_prediction": prediction,
            "bad_review_probability": probability,
        }
    )
