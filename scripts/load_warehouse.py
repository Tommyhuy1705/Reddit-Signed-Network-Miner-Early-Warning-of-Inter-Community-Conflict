"""Load the Olist star schema into PostgreSQL or SQL Server."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.config import get_database_url
from src.etl.extract import load_olist_tables
from src.etl.load import load_star_schema_to_database
from src.etl.transform import build_order_features, build_star_schema


def main() -> None:
    tables = load_olist_tables()
    order_features = build_order_features(tables)
    star_schema = build_star_schema(tables, order_features)
    load_star_schema_to_database(star_schema, database_url=get_database_url())
    print("Loaded star schema into configured database.")


if __name__ == "__main__":
    main()
