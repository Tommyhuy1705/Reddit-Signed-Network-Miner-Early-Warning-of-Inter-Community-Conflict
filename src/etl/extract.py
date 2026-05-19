"""extract.py
Functions to extract raw Reddit TSV files from `data/raw/`.
"""

import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]


def list_raw_files():
    """Return list of raw files in data/raw."""
    raw_dir = PROJECT_ROOT / "data" / "raw"
    return list(raw_dir.glob("*.tsv"))
