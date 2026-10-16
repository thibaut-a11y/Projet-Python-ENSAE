"""Paramètres communs du projet."""

from pathlib import Path

# Chemins définis à partir de l'emplacement de ce fichier.
PROJECT_DIR = Path(__file__).resolve().parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_DIR / "data" / "processed"

# Univers étudié.
CURRENCY = "USD"
TICKERS = ["SPY", "IEF", "GLD", "BIL"]
FRED_SERIES = ["CPIAUCSL", "DGS10"]

# Périodes d'analyse, bornes incluses.
PILOT_START = "2019-01-01"
PILOT_END = "2023-12-31"

ANALYSIS_START = "2007-06-01"
ANALYSIS_END = "2025-12-31"

# Bornes de fin exclusives utilisées pour télécharger avec yfinance.
PILOT_DOWNLOAD_END = "2024-01-01"
FULL_DOWNLOAD_END = "2026-01-01"

# Pondérations cibles, rétablies à chaque fin de mois.
PORTFOLIO_WEIGHTS = {
    "A": {"SPY": 1.00, "IEF": 0.00, "GLD": 0.00, "BIL": 0.00},
    "B": {"SPY": 0.60, "IEF": 0.00, "GLD": 0.00, "BIL": 0.40},
    "C": {"SPY": 0.60, "IEF": 0.40, "GLD": 0.00, "BIL": 0.00},
    "D": {"SPY": 0.60, "IEF": 0.30, "GLD": 0.10, "BIL": 0.00},
}

DRAWDOWN_THRESHOLD = -0.10
