"""Training pipeline for Olist bad-review classification."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import MODELS_DIR


TARGET = "bad_review"
ID_COLUMNS = ["order_id"]
NUMERIC_FEATURES = [
    "total_price",
    "total_freight",
    "freight_ratio",
    "max_installments",
    "item_count",
    "unique_product_count",
    "unique_seller_count",
    "delivery_days",
    "delay_days",
    "is_delayed",
    "order_month",
    "approval_hours",
    "carrier_days",
]
CATEGORICAL_FEATURES = [
    "payment_type",
    "product_category_name_english",
    "customer_state",
    "seller_state",
    "order_day_of_week",
]


def build_preprocessor() -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, NUMERIC_FEATURES),
            ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )


def build_model(model_name: str = "random_forest") -> Pipeline:
    preprocessor = build_preprocessor()
    if model_name == "logistic_regression":
        estimator = LogisticRegression(max_iter=1000, class_weight="balanced")
    elif model_name == "hist_gradient_boosting":
        estimator = HistGradientBoostingClassifier(max_iter=250, learning_rate=0.06, random_state=42)
    elif model_name == "random_forest":
        estimator = RandomForestClassifier(
            n_estimators=300,
            min_samples_leaf=3,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=42,
        )
    else:
        raise ValueError("model_name must be logistic_regression, random_forest, or hist_gradient_boosting")
    return Pipeline(steps=[("preprocess", preprocessor), ("model", estimator)])


def train_model(
    model_dataset: pd.DataFrame,
    model_name: str = "random_forest",
    output_path: Path | None = None,
) -> tuple[Pipeline, dict]:
    """Train, evaluate and optionally persist a bad-review classifier."""
    required = [TARGET, *NUMERIC_FEATURES, *CATEGORICAL_FEATURES]
    missing = [column for column in required if column not in model_dataset.columns]
    if missing:
        raise KeyError(f"Missing model columns: {missing}")

    df = model_dataset.dropna(subset=[TARGET]).copy()
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipeline = build_model(model_name)
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    y_proba = predict_probability(pipeline, X_test)

    metrics = {
        "model_name": model_name,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "positive_rate": float(y.mean()),
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_proba)) if y_proba is not None else None,
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred, zero_division=0, output_dict=True),
    }

    if output_path is None:
        output_path = MODELS_DIR / "bad_review_classifier.pkl"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipeline, "metrics": metrics, "features": NUMERIC_FEATURES + CATEGORICAL_FEATURES}, output_path)
    return pipeline, metrics


def predict_probability(model: Pipeline, X: pd.DataFrame):
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    if hasattr(model, "decision_function"):
        scores = model.decision_function(X)
        return 1 / (1 + np.exp(-scores))
    return None
