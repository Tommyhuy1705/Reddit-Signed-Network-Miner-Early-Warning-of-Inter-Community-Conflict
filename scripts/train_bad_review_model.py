"""Train and save the bad-review classifier."""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.config import MODELS_DIR, PROCESSED_DIR, ensure_project_dirs
from src.etl.extract import load_olist_tables
from src.etl.load import save_processed_outputs
from src.etl.transform import build_model_dataset, build_order_features, build_star_schema
from src.models.train import train_model


def main() -> None:
    ensure_project_dirs()
    model_path = PROCESSED_DIR / "model_dataset.csv"
    if model_path.exists():
        model_dataset = pd.read_csv(model_path)
    else:
        tables = load_olist_tables()
        order_features = build_order_features(tables)
        model_dataset = build_model_dataset(order_features)
        save_processed_outputs(order_features, model_dataset, build_star_schema(tables, order_features))

    _, metrics = train_model(model_dataset, model_name="random_forest")
    metrics_path = MODELS_DIR / "bad_review_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in metrics.items() if k != "classification_report"}, indent=2))


if __name__ == "__main__":
    main()
