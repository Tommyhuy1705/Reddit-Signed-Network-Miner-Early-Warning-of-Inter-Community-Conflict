"""transform.py
Cleaning and feature extraction utilities.
"""

import pandas as pd


def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Perform minimal cleaning (dropna placeholder)."""
    return df.dropna()
