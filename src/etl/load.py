"""Load processed Olist data into PostgreSQL or SQL Server."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import PROCESSED_DIR, get_database_url


def create_db_engine(database_url: str | None = None):
    """Create a SQLAlchemy engine for PostgreSQL or SQL Server."""
    from sqlalchemy import create_engine

    return create_engine(database_url or get_database_url(), future=True)


def write_dataframe(df: pd.DataFrame, table_name: str, engine, schema: str | None = None) -> None:
    """Replace a database table with DataFrame contents."""
    df.to_sql(table_name, engine, schema=schema, if_exists="replace", index=False, chunksize=5000, method="multi")


def load_star_schema_to_database(
    star_schema: dict[str, pd.DataFrame],
    database_url: str | None = None,
    schema: str | None = None,
) -> None:
    """Load all dimensional tables and the fact table into the configured database."""
    from sqlalchemy import text

    engine = create_db_engine(database_url)
    with engine.begin() as conn:
        if schema:
            dialect = conn.dialect.name
            if dialect == "postgresql":
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            elif dialect == "mssql":
                conn.execute(
                    text(
                        f"IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{schema}') "
                        f"EXEC('CREATE SCHEMA {schema}')"
                    )
                )

    load_order = [
        "dim_date",
        "dim_customer",
        "dim_seller",
        "dim_product",
        "dim_payment",
        "dim_order_status",
        "fact_order_items",
    ]
    for table_name in load_order:
        write_dataframe(star_schema[table_name], table_name, engine, schema=schema)


def save_processed_outputs(
    order_features: pd.DataFrame,
    model_dataset: pd.DataFrame,
    star_schema: dict[str, pd.DataFrame],
    output_dir: Path = PROCESSED_DIR,
) -> None:
    """Save processed artifacts for notebooks, app and offline review."""
    output_dir.mkdir(parents=True, exist_ok=True)
    order_features.to_csv(output_dir / "order_features.csv", index=False)
    model_dataset.to_csv(output_dir / "model_dataset.csv", index=False)
    for table_name, df in star_schema.items():
        df.to_csv(output_dir / f"{table_name}.csv", index=False)


def read_processed_table(table_name: str, processed_dir: Path = PROCESSED_DIR) -> pd.DataFrame:
    """Read a processed CSV table by logical name."""
    return pd.read_csv(processed_dir / f"{table_name}.csv")
