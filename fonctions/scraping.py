"""collecte et lecture des cours et de l indice des prix"""
import os
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv

TICKERS = {
    "SPY": "Actions américaines",
    "EFA": "Actions pays développés hors USA et Canada",
    "EEM": "Actions pays émergents",
    "IEF": "Obligations à moyen terme",
    "GLD": "Or",
    "SHY": "Obligations à court terme",
}

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_PATH = BASE_DIR / "data" / "raw" / "asset_prices.parquet"


def fetch_fred(start_date="2005-01-01", end_date="2025-12-31", actualiser=False):
    path = BASE_DIR / "data" / "raw" / "CPIAUCSL.parquet"
    if path.exists() and not actualiser:
        return pd.read_parquet(path).loc[start_date:end_date]

    load_dotenv(BASE_DIR / ".env")
    r = requests.get(
        "https://api.stlouisfed.org/fred/series/observations",
        params={
            "series_id": "CPIAUCSL",
            "api_key": os.getenv("FRED_API_KEY"),
            "file_type": "json",
            "observation_start": start_date,
            "observation_end": end_date,
        },
        timeout=45,
    )
    r.raise_for_status()
    obs = pd.DataFrame(r.json()["observations"])
    df = pd.DataFrame(
        {"CPIAUCSL": pd.to_numeric(obs["value"], errors="coerce").to_numpy()},
        index=pd.to_datetime(obs["date"]),
    )
    # on garde un calendrier mensuel complet même si un mois est absent
    calendrier = pd.date_range(start_date, end_date, freq="MS")
    df = df.reindex(calendrier).rename_axis("Date")
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
    return df


def fetch_yahoo(
    tickers: list[str] = list(TICKERS.keys()),
    start_date: str = "2005-12-30",
    end_date: str = "2026-01-01",
    filepath: Path = DATA_RAW_PATH,
    actualiser=False,
):
    """lit les prix sauvegardés ou refait la collecte groupée avec yfinance"""
    clotures = filepath.with_name("asset_closes.parquet")
    if filepath.exists() and clotures.exists() and not actualiser:
        prix = pd.read_parquet(filepath)
        dates = (prix.index >= start_date) & (prix.index < end_date)
        return prix.loc[dates, tickers]

    print(f"Téléchargement des cours pour {tickers} depuis Yahoo Finance")
    df_raw = yf.download(
        tickers=tickers,
        start=start_date,
        end=end_date,
        auto_adjust=False,
        keepna=True,
        progress=False,
    )
    if df_raw.empty:
        raise ValueError("Aucun cours reçu de Yahoo Finance")
    # on garde les ajustements et les clôtures pour leur comparaison
    df_prices = df_raw["Adj Close"].reindex(columns=tickers)
    df_close = df_raw["Close"].reindex(columns=tickers)
    df_prices.index = df_prices.index.tz_localize(None)
    df_close.index = df_close.index.tz_localize(None)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df_prices.to_parquet(filepath)
    df_close.to_parquet(clotures)
    print(f"Données sauvegardées dans {filepath.parent}")
    return df_prices
