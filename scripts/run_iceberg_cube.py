"""Compute default Iceberg Cube outputs for Olist."""

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.config import PROCESSED_DIR, WAREHOUSE_DIR, ensure_project_dirs
from src.etl.extract import load_olist_tables
from src.etl.transform import build_order_features
from src.olap.iceberg_cube import compute_default_olist_cubes


def main() -> None:
    ensure_project_dirs()
    features_path = PROCESSED_DIR / "order_features.csv"
    if features_path.exists():
        order_features = pd.read_csv(features_path)
    else:
        order_features = build_order_features(load_olist_tables())

    cubes = compute_default_olist_cubes(order_features)
    combined = []
    for name, cube in cubes.items():
        output_path = WAREHOUSE_DIR / f"iceberg_cube_{name}.csv"
        cube.to_csv(output_path, index=False)
        combined.append(cube.assign(cube_theme=name))
        print(f"Saved {output_path} ({len(cube)} rows)")
    if combined:
        pd.concat(combined, ignore_index=True).to_csv(WAREHOUSE_DIR / "iceberg_cube_results.csv", index=False)


if __name__ == "__main__":
    main()
