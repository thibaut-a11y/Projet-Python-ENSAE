# Projet portefeuille en crise

Comparaison de six portefeuilles sur 2006–2025. Le [rapport](rapport.ipynb) présente la démarche, les résultats et leurs limites.

## Installation et lancement

Prérequis : **Python 3.13**. Cloner le dépôt ou télécharger et extraire le ZIP, puis ouvrir un terminal dans le dossier contenant `requirements.txt`.

Sous Windows :

```powershell
py -3.13 --version
py -3.13 -m pip install -r requirements.txt
```

Si `python` désigne déjà Python 3.13, utiliser simplement `python -m pip install -r requirements.txt`.

Ouvrir ensuite **`rapport.ipynb`** et lancer **Run All / Tout exécuter**.

## Données

Les données sont fournies dans `data/raw/` : **six CSV téléchargés avec yfinance** et **trois JSON du BLS**. Conserver ce dossier et `fonctions/` avec le notebook. Après installation des dépendances, le rapport peut être exécuté sans connexion.

## Options facultatives

Un environnement `.venv` peut être utilisé pour isoler les dépendances. Pour ouvrir JupyterLab dans le navigateur sous Windows : `py -3.13 -m jupyterlab`.

## Refaire la collecte

Pour télécharger de nouvelles données dans un dossier distinct, exécuter depuis le dossier du projet dans Python :

```python
from pathlib import Path
from fonctions.donnees import telecharger_sources

telecharger_sources(Path("data/nouvelle_collecte"))
```
