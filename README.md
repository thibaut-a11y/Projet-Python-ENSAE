# La diversification résiste-t-elle aux baisses de marché ?

Projet de Python — ENSAE, 2026–2027.

## Équipe

Alexandre D'HERISSART / Thibaut ROSSET

## Problématique

Lors des baisses du marché actions, les obligations et l’or
protègent-ils davantage qu’une allocation en trésorerie,
à exposition actions identique ?

Nous comparons quatre portefeuilles pour distinguer le bénéfice
de la diversification du simple effet d’une exposition réduite
aux actions.

## Portefeuilles étudiés

| Portefeuille | SPY — Actions | IEF — Obligations | GLD — Or | BIL — Trésorerie |
|---|---:|---:|---:|---:|
| A | 100 % | 0 % | 0 % | 0 % |
| B | 60 % | 0 % | 0 % | 40 % |
| C | 60 % | 40 % | 0 % | 0 % |
| D | 60 % | 30 % | 10 % | 0 % |

## Périmètre

- Devise : dollar américain.
- Période d’analyse visée : juin 2007 à décembre 2025.
- Données de marché quotidiennes ; analyse notamment mensuelle.
- Rééquilibrage mensuel des portefeuilles.
- Premier audit sur 2019–2023 avant extension de la collecte.

La disponibilité et la qualité des données restent à vérifier.

## Données envisagées

- Yahoo Finance, via yfinance : SPY, IEF, GLD et BIL.
- FRED : indice des prix CPIAUCSL et taux américain à dix ans DGS10.

Les sources et contrôles sont documentés dans docs/sources.md.
Le protocole d’analyse est décrit dans docs/cadrage.md.

## Organisation

- config.py : paramètres communs.
- src/ : fonctions de collecte et de nettoyage.
- notebooks/ : audit et analyses commentées.
- docs/ : cadrage et documentation.
- data/raw/ : copies locales des données brutes.
- data/processed/ : données nettoyées.

Les données locales sont exclues de Git.
Leur méthode de récupération et leur accès seront documentés
avant le rendu.

## Installation

Depuis la racine du dépôt :

    python -m pip install -r requirements.txt

Ouvrir ensuite notebooks/01_audit_donnees.ipynb dans VS Code
et sélectionner le noyau Python de l’environnement utilisé.

## État d’avancement

Structure initiale créée.
Prochaine étape : collecte pilote et audit des quatre ETF.
