"""collecte et préparation des données"""
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import requests
import yfinance as yf

from . import BRUT

SUPPORTS = {
    "SPY": "actions américaines, S&P 500",
    "EFA": "actions développées hors États-Unis et Canada",
    "EEM": "actions émergentes",
    "IEF": "obligations du Trésor américain à 7–10 ans",
    "GLD": "or physique",
    "SHY": "obligations du Trésor américain à 1–3 ans",
}


def telecharger_sources(dossier):
    """refait la collecte dans un dossier vide sans écraser les données du rendu"""
    dossier.mkdir(parents=True, exist_ok=True)
    if any(dossier.iterdir()):
        raise FileExistsError("Choisir un dossier vide pour la nouvelle collecte")
    sources = []
    for code_fonds in SUPPORTS:
        cours = yf.Ticker(code_fonds).history(
            start="2005-12-30", end="2026-01-01",
            auto_adjust=False, actions=True, keepna=True)
        if cours.empty:
            raise ValueError(f"Aucune donnée reçue pour {code_fonds}")
        # yfinance fournit déjà les dates locales de séance
        cours.index = cours.index.tz_localize(None)
        nom = f"{code_fonds}.csv"
        cours.to_csv(dossier / nom, index_label="Date")
        sources.append({"fichier": nom, "source": "Yahoo Finance via yfinance",
                        "collecte_utc": datetime.now(timezone.utc).isoformat()})

    for debut, fin in [(2004, 2013), (2014, 2023), (2024, 2025)]:
        reponse = requests.post(
            "https://api.bls.gov/publicAPI/v1/timeseries/data/",
            json={"seriesid": ["CUSR0000SA0"], "startyear": str(debut), "endyear": str(fin)},
            timeout=45)
        reponse.raise_for_status()
        assert reponse.json()["status"] == "REQUEST_SUCCEEDED"
        nom = f"CPI_{debut}_{fin}.json"
        (dossier / nom).write_bytes(reponse.content)
        sources.append({"fichier": nom, "source": "BLS API v1",
                        "collecte_utc": datetime.now(timezone.utc).isoformat()})
    informations = {"yfinance_version": yf.__version__, "debut_cours": "2005-12-30",
                    "fin_cours_exclue": "2026-01-01", "sources": sources}
    (dossier / "collecte.json").write_text(json.dumps(informations, indent=2))


def lire_cours(code_fonds):
    """lit les cours sauvegardés depuis yfinance sans accès au réseau"""
    cours = pd.read_csv(BRUT / f"{code_fonds}.csv", index_col="Date", parse_dates=True)
    cours = cours.loc["2005-12-30":"2025-12-31", ["Adj Close", "Close"]]
    cours = cours.rename(columns={"Adj Close": "ajuste", "Close": "cloture"})
    assert cours.index.is_unique and cours.index.is_monotonic_increasing
    assert not ((cours <= 0) | np.isinf(cours)).any().any()
    return cours


def preparer_prix():
    """prépare les prix communs et les tableaux de contrôle"""
    cours_ajustes = {}
    cours_cloture = {}
    effectifs = {}
    for code_fonds in SUPPORTS:
        cours = lire_cours(code_fonds)
        cours_ajustes[code_fonds] = cours["ajuste"]
        cours_cloture[code_fonds] = cours["cloture"]
        effectifs[code_fonds] = len(cours)

    prix_avant = pd.DataFrame(cours_ajustes)
    # on garde uniquement les dates disponibles pour tous les fonds
    prix = prix_avant.dropna()
    qualite = pd.DataFrame({
        "exposition": SUPPORTS,
        "dates reçues": effectifs,
        "prix manquants": prix_avant.isna().sum(),
    })
    assert str(prix.index[0].date()) == "2005-12-30"
    assert str(prix.index[-1].date()) == "2025-12-31"

    clotures = pd.DataFrame(cours_cloture)
    comparaison = pd.DataFrame({
        "rendement ajusté (%)": (prix.iloc[-1] / prix.iloc[0] - 1) * 100,
        "sans distributions (%)": (clotures.iloc[-1] / clotures.iloc[0] - 1) * 100,
    })
    return prix, qualite, comparaison



def lire_inflation():
    """calcule la variation annuelle des prix sans compléter les mois absents"""
    valeurs = {}
    for fichier in sorted(BRUT.glob("CPI_*.json")):
        serie = json.loads(fichier.read_text())["Results"]["series"][0]
        assert serie["seriesID"] == "CUSR0000SA0"
        for ligne in serie["data"]:
            mois = int(ligne["period"][1:])
            # on garde les mois et pas les moyennes annuelles
            if 1 <= mois <= 12:
                date = f"{ligne['year']}-{mois:02d}"
                assert date not in valeurs
                valeurs[date] = ligne["value"]

    indice = pd.Series(valeurs)
    indice.index = pd.PeriodIndex(indice.index, freq="M")
    indice = pd.to_numeric(indice, errors="coerce")
    calendrier = pd.period_range("2004-01", "2025-12", freq="M")
    indice = indice.reindex(calendrier)
    inflation = (100 * indice.pct_change(12, fill_method=None)).loc["2006-01":].rename("inflation_pct")
    return inflation
