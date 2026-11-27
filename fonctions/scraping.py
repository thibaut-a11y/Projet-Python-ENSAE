import os
from pathlib import Path
import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv



# Définition des actifs étudiés
TICKERS = {
    "SPY": "Actions",
    "IEF": "Obligations à moyen terme",
    "SHY" : "Obligations à court terme",
    "GLD": "Or",
    "BIL": "Trésorerie",
    "EFA": "Actions pays développés hors USA et Canada",
    "EEM": "Actions pays émergents"
}

# Chemin relatif à la racine du projet pour fonctionner partout (script ou notebook)
BASE_DIR = (
    Path(__file__).resolve().parent.parent
    if "__file__" in locals()
    else Path.cwd()
)
DATA_RAW_PATH = BASE_DIR / "data" / "raw" / "asset_prices.parquet"

def fetch_fred(start_date="2006-06-01", end_date="2025-12-31"):
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
    )
    r.raise_for_status()
    obs = pd.DataFrame(r.json()["observations"])
    df = pd.DataFrame(
        {"CPIAUCSL": pd.to_numeric(obs["value"], errors="coerce").to_numpy()},
        index=pd.to_datetime(obs["date"]),
    )
    path = BASE_DIR / "data" / "raw" / "CPIAUCSL.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    df.to_parquet(path)
    return df

def fetch_yahoo(
    tickers: list[str] = list(TICKERS.keys()),
    start_date: str = "2007-06-01",  # on commence à récupérer les données en juin
    end_date: str = "2026-01-01",   #on finit en décembre
    filepath: Path = DATA_RAW_PATH,
):
    """Télécharge les cours ajustés depuis Yahoo Finance et les stocke en local (format Parquet). Si un fichier existe déjà, il est supprimé"""
    if filepath.exists():
        filepath.unlink()
        print(f"Ancien fichier supprimé : {filepath}")

    print(f"Téléchargement des cours pour {tickers} depuis Yahoo Finance...")
    
    df_raw = yf.download(
        tickers=tickers,
        start=start_date,
        end=end_date,
        auto_adjust=True, # auto_adjust=True intègre les dividendes réinvestis et les splits (Total Return)
        progress=False,
    )
    df_prices = df_raw["Close"]
    
    filepath.parent.mkdir(parents=True, exist_ok=True) # On crée le dossier data/raw
    df_prices.to_parquet(filepath) # On sauvegarde au format parquet les données
    print(f"Données sauvegardées avec succès dans : {filepath}") 
    
    
    return df_prices  # On renvoie le tableau  

