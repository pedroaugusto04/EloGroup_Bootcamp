"""Conversões comuns para envelopes JSON seguros."""

from typing import Any
import numpy as np
import pandas as pd


def python_value(value: Any) -> Any:
    if value is None or (not isinstance(value, (list, dict)) and pd.isna(value)):
        return None
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat() if value.time().isoformat() == "00:00:00" else value.isoformat()
    if hasattr(value, "isoformat") and not isinstance(value, str):
        return value.isoformat()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def records(df: pd.DataFrame) -> list[dict]:
    return [{key: python_value(value) for key, value in row.items()} for row in df.to_dict("records")]


def one_row(df: pd.DataFrame) -> dict:
    return records(df)[0] if not df.empty else {}
