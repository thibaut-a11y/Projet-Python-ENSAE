from pathlib import Path
import pandas as pd
import yfinance as yf

# Définition des actifs étudiés
TICKERS = {
    "SPY": "Actions",
    "IEF": "Obligations",
    "GLD": "Or",
    "BIL": "Trésorerie",
}

# Chemin relatif à la racine du projet pour fonctionner partout (script ou notebook)
BASE_DIR = (
    Path(__file__).resolve().parent.parent
    if "__file__" in locals()
    else Path.cwd()
)
DATA_RAW_PATH = BASE_DIR / "data" / "raw" / "asset_prices.parquet"


def fetch_and_save_data(
    tickers: list[str] = list(TICKERS.keys()),
    start_date: str = "2007-06-01",  # on commence à récupérer les données en juin
    end_date: str = "2026-01-01",   #on finit en décembre
    filepath: Path = DATA_RAW_PATH,
):
    """Télécharge les cours ajustés depuis Yahoo Finance et les stocke en local (format Parquet).

    Si le fichier existe déjà, il est chargé directement 
    """
    if filepath.exists():
        print(f"Chargement des données depuis : {filepath}")
        return pd.read_parquet(filepath)

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


if __name__ == "__main__":
    prices = fetch_and_save_data()
    print(prices.head())