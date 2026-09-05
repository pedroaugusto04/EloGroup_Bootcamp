"""
src/utils/statistics.py
Funções estatísticas puras para análise de dispersão, quartis e outliers (Tukey IQR).
"""

from typing import Dict, Any
import numpy as np
import pandas as pd


def calculate_iqr_stats(series: pd.Series, k: float = 1.5) -> Dict[str, Any]:
    """
    Calcula quartis (Q1, Mediana, Q3), limites de Tukey (IQR) e contagem de outliers.
    """
    s = series.dropna()
    if s.empty:
        return {
            "n": 0, "mean": 0.0, "min": 0.0, "q1": 0.0, "median": 0.0,
            "q3": 0.0, "max": 0.0, "iqr": 0.0, "lower_bound": 0.0, "upper_bound": 0.0,
            "outliers_low_count": 0, "outliers_high_count": 0, "total_outliers": 0, "outlier_pct": 0.0
        }

    q1 = float(np.percentile(s, 25))
    q3 = float(np.percentile(s, 75))
    iqr = q3 - q1
    lower_bound = q1 - k * iqr
    upper_bound = q3 + k * iqr

    outliers_low = s[s < lower_bound]
    outliers_high = s[s > upper_bound]
    total_outliers = len(outliers_low) + len(outliers_high)

    return {
        "n": len(s),
        "mean": float(s.mean()),
        "min": float(s.min()),
        "q1": q1,
        "median": float(s.median()),
        "q3": q3,
        "max": float(s.max()),
        "iqr": iqr,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "outliers_low_count": len(outliers_low),
        "outliers_high_count": len(outliers_high),
        "total_outliers": total_outliers,
        "outlier_pct": (total_outliers / len(s) * 100.0) if len(s) > 0 else 0.0,
    }
