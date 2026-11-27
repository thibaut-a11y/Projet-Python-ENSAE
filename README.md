# Projet portefeuille en crise

Comparaison de six portefeuilles sur 2006–2025.

## Lancement

Avec Python 3.13, depuis le dossier du projet :

```bash
python -m pip install -r requirements.txt
```

Ouvrir `rapport.ipynb` et lancer **Tout exécuter**. Sur macOS avec Python géré par Homebrew, créer un environnement si nécessaire :

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Données

Les trois fichiers Parquet dans `data/raw/` permettent de reproduire le rapport sans téléchargement. Ils sont issus des CSV Yahoo Finance et des JSON BLS fournis dans la version précédente, convertis sans changer les valeurs. `collecte.json` conserve leur provenance. L'indice BLS sauvegardé est nommé `CPIAUCSL` pour correspondre à la série diffusée par FRED.

`scraping.py` regroupe la collecte et la lecture ; `audit.py` vérifie les sources.

## Refaire les téléchargements

Une actualisation remplace les sauvegardes et peut modifier les résultats. Pour FRED, créer un fichier personnel `.env` contenant `FRED_API_KEY=...`, sans le publier. Puis exécuter dans Python :

```python
from fonctions.scraping import fetch_yahoo, fetch_fred

prix = fetch_yahoo(actualiser=True)
cpi = fetch_fred(actualiser=True)
```

Relancer ensuite le rapport et vérifier sa rédaction avec les nouveaux résultats. Le fichier `collecte.json` décrit les sauvegardes fournies : mettre aussi à jour leur provenance après une actualisation.
