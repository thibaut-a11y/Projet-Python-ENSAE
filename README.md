# Projet portefeuille en crise

Comparaison de sept portefeuilles entre le 1er juin 2007 et le 31 décembre 2025. La démarche, les résultats et leurs limites sont dans [rapport.ipynb](rapport.ipynb).

## Lancer le rapport

Installer les dépendances avec Python 3.13, depuis le dossier du projet :

```bash
python -m pip install -r requirements.txt
```

Sous Windows, si nécessaire : `py -3.13 -m pip install -r requirements.txt`.

Ouvrir **rapport.ipynb** et lancer **Tout exécuter / Run All**.

## Données

Les deux fichiers Parquet de `data/raw/` permettent d'exécuter le rapport sans connexion ni clé API. Conserver ce dossier et `fonctions/` avec le notebook.

Collecte du 27 novembre 2026 :

- `asset_prices.parquet` : cours ajustés des sept ETF, téléchargés avec `fetch_yahoo()` (yfinance 1.8.0) depuis Yahoo Finance.
- `CPIAUCSL.parquet` : indice mensuel américain, de juin 2006 à décembre 2025, téléchargé depuis l'[export public FRED](https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL&cosd=2006-06-01&coed=2025-12-31), puis sauvegardé en Parquet. Octobre 2025 est manquant.

## Refaire la collecte

Pour utiliser l'API FRED, créer à la racine un fichier `.env` contenant `FRED_API_KEY=votre_cle`, puis exécuter depuis le dossier du projet :

```python
from fonctions.scraping import fetch_yahoo, fetch_fred

fetch_yahoo()
fetch_fred()
```

Ces appels remplacent les sauvegardes. Les sources pouvant être révisées, relancer ensuite le notebook et vérifier les commentaires chiffrés.
