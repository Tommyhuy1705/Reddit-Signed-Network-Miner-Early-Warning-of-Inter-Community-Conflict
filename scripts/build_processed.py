"""Build processed CSV artifacts from the raw Olist CSV files."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.config import ensure_project_dirs
from src.etl.extract import load_olist_tables, summarize_tables
from src.etl.load import save_processed_outputs
from src.etl.transform import build_model_dataset, build_order_features, build_star_schema


def main() -> None:
    ensure_project_dirs()
    tables = load_olist_tables()
    summary = summarize_tables(tables)
    order_features = build_order_features(tables)
    model_dataset = build_model_dataset(order_features)
    star_schema = build_star_schema(tables, order_features)
    save_processed_outputs(order_features, model_dataset, star_schema)
    summary.to_csv("data/processed/dataset_summary.csv", index=False)
    print("Processed artifacts saved to data/processed/")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
