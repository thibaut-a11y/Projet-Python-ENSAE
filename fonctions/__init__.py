"""chemin des données brutes du projet"""
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
BRUT = RACINE / "data/raw"
