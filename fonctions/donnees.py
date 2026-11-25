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