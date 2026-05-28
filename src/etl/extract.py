"""Data extraction utilities for the Olist Brazilian E-Commerce dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import DATASET_DIR, OLIST_FILES


def dataset_file_paths(dataset_dir: Path = DATASET_DIR) -> dict[str, Path]:
    """Return canonical CSV paths for all expected Olist tables."""
    return {name: dataset_dir / filename for name, filename in OLIST_FILES.items()}


def validate_dataset_files(dataset_dir: Path = DATASET_DIR) -> None:
    """Fail early if any required dataset file is missing."""
    missing = [str(path) for path in dataset_file_paths(dataset_dir).values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing Olist CSV files: " + ", ".join(missing))


def load_olist_tables(dataset_dir: Path = DATASET_DIR) -> dict[str, pd.DataFrame]:
    """Load every Olist CSV into a dictionary of pandas DataFrames."""
    validate_dataset_files(dataset_dir)
    tables: dict[str, pd.DataFrame] = {}
    for name, path in dataset_file_paths(dataset_dir).items():
        encoding = "utf-8-sig" if name == "category_translation" else "utf-8"
        tables[name] = pd.read_csv(path, encoding=encoding)
    return tables


def summarize_tables(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Return shape, duplicate and missing-value summary for report/EDA."""
    rows = []
    for name, df in tables.items():
        rows.append(
            {
                "table_name": name,
                "rows": len(df),
                "columns": len(df.columns),
                "duplicate_rows": int(df.duplicated().sum()),
                "missing_cells": int(df.isna().sum().sum()),
                "columns_list": ", ".join(df.columns),
            }
        )
    return pd.DataFrame(rows).sort_values("table_name").reset_index(drop=True)
