"""Fonctions de collecte et de sauvegarde des données des ETF."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf


def download_etfs(tickers, start, end):
    """Télécharge les données quotidiennes pour chaque ETF."""
    datasets = {}

    for ticker in tickers:
        print(f"Téléchargement de {ticker}...")

        data = yf.download(
            ticker,
            start=start,
            end=end,
            interval="1d",
            auto_adjust=False,
            actions=True,
            keepna=True,
            repair=False,
            threads=False,
            progress=False,
            multi_level_index=False,
            timeout=30,
        )

        if data is None or data.empty:
            raise ValueError(f"Aucune donnée reçue pour {ticker}.")

        expected_columns = {
            "Close", "Adj Close", "Dividends", "Stock Splits"
        }
        missing_columns = expected_columns - set(data.columns)

        if missing_columns:
            raise ValueError(
                f"{ticker} : colonnes absentes : {missing_columns}"
            )

        if data["Adj Close"].isna().all():
            raise ValueError(f"Aucun prix ajusté disponible pour {ticker}.")

        datasets[ticker] = data

    return datasets


def save_data(datasets, folder, start, end):
    """Enregistre un CSV par ETF et un fichier de métadonnées."""
    folder = Path(folder)

    if (folder / "metadata.json").exists():
        raise FileExistsError("Une collecte est déjà sauvegardée ici.")

    folder.mkdir(parents=True, exist_ok=True)

    for ticker, data in datasets.items():
        data.to_csv(folder / f"{ticker}.csv", index_label="Date")

    metadata = {
        "source": "Yahoo Finance",
        "saved_at_utc": datetime.now(timezone.utc).isoformat(),
        "tickers": list(datasets),
        "start": start,
        "end_exclusive": end,
        "yfinance_version": yf.__version__,
        "pandas_version": pd.__version__,
        "options": {
            "interval": "1d",
            "auto_adjust": False,
            "actions": True,
            "keepna": True,
            "repair": False,
            "multi_level_index": False,
        },
    }

    with open(folder / "metadata.json", "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2, ensure_ascii=False)


def load_data(folder):
    """Recharge les CSV et les métadonnées d'une collecte."""
    folder = Path(folder)

    with open(folder / "metadata.json", encoding="utf-8") as file:
        metadata = json.load(file)

    datasets = {}

    for ticker in metadata["tickers"]:
        datasets[ticker] = pd.read_csv(
            folder / f"{ticker}.csv",
            index_col="Date",
            parse_dates=["Date"],
        )

    return datasets, metadata