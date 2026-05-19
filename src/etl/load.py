"""load.py
Load transformed data into a simple SQLite data warehouse under `data/warehouse/`.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "warehouse" / "warehouse.db"


def write_df_to_table(df, table_name: str):
    conn = sqlite3.connect(DB_PATH)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
