"""Project-wide paths and database configuration."""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional at import time
    load_dotenv = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "dataset"
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
WAREHOUSE_DIR = DATA_DIR / "warehouse"
MODELS_DIR = PROJECT_ROOT / "models"

if load_dotenv:
    load_dotenv(PROJECT_ROOT / ".env")


OLIST_FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def ensure_project_dirs() -> None:
    """Create runtime output directories."""
    for path in (RAW_DIR, PROCESSED_DIR, WAREHOUSE_DIR, MODELS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def get_database_url() -> str:
    """Return SQLAlchemy URL for PostgreSQL or SQL Server.

    Preferred: set OLIST_DATABASE_URL directly, for example:
    postgresql+psycopg2://user:password@localhost:5432/olist_dwh

    Alternatives:
    - OLIST_DB_DIALECT=postgresql with OLIST_DB_USER/PASSWORD/HOST/PORT/NAME
    - OLIST_DB_DIALECT=mssql with OLIST_DB_USER/PASSWORD/HOST/PORT/NAME/DRIVER
    """
    direct_url = os.getenv("OLIST_DATABASE_URL")
    if direct_url:
        return direct_url

    dialect = os.getenv("OLIST_DB_DIALECT", "postgresql").lower()
    user = os.getenv("OLIST_DB_USER", "postgres")
    password = os.getenv("OLIST_DB_PASSWORD", "postgres")
    host = os.getenv("OLIST_DB_HOST", "localhost")
    database = os.getenv("OLIST_DB_NAME", "olist_dwh")

    if dialect in {"postgres", "postgresql"}:
        port = os.getenv("OLIST_DB_PORT", "5432")
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

    if dialect in {"sqlserver", "mssql"}:
        port = os.getenv("OLIST_DB_PORT", "1433")
        driver = os.getenv("OLIST_DB_DRIVER", "ODBC Driver 17 for SQL Server")
        driver = driver.replace(" ", "+")
        return f"mssql+pyodbc://{user}:{password}@{host}:{port}/{database}?driver={driver}"

    raise ValueError(
        "Unsupported OLIST_DB_DIALECT. Use 'postgresql', 'postgres', 'mssql', or 'sqlserver'."
    )
