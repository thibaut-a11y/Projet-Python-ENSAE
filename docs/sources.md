# Sources et traçabilité

## Séries envisagées

| Source | Identifiant | Rôle | Fréquence source |
|---|---|---|---|
| Yahoo Finance | SPY | Actions américaines | Quotidienne |
| Yahoo Finance | IEF | Obligations du Trésor américain 7–10 ans | Quotidienne |
| Yahoo Finance | GLD | Exposition à l’or | Quotidienne |
| Yahoo Finance | BIL | Bons du Trésor américain à très court terme | Quotidienne |
| FRED | CPIAUCSL | Indice des prix américain | Mensuelle |
| FRED | DGS10 | Taux du Trésor américain à dix ans | Quotidienne |

BIL représente un placement de trésorerie rémunéré :
son rendement ne sera pas supposé nul.

DGS10 est un taux obligataire, pas un rendement de détention d’IEF.
CPIAUCSL est un indice de prix, pas directement un taux d’inflation.

## Références

- https://finance.yahoo.com/quote/SPY/history/
- https://finance.yahoo.com/quote/IEF/history/
- https://finance.yahoo.com/quote/GLD/history/
- https://finance.yahoo.com/quote/BIL/history/
- https://fred.stlouisfed.org/series/CPIAUCSL
- https://fred.stlouisfed.org/series/DGS10
- https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html

## État des vérifications

Collecte non encore testée dans ce dépôt.

## Informations à enregistrer à chaque collecte

- Date et heure de téléchargement.
- Source et identifiant de la série.
- Paramètres utilisés et version de la bibliothèque.
- Dates demandées et dates effectivement obtenues.
- Nombre d’observations.
- Colonnes, unités et ajustements.
- Nom du fichier brut sauvegardé.

## Contrôles à réaliser

- Dates triées et sans doublons.
- Présence des colonnes attendues.
- Valeurs manquantes et périodes sans observations.
- Cohérence des prix et des unités.
- Distributions et ajustements des ETF.
- Couverture commune des actifs.

Les fichiers bruts seront conservés séparément des fichiers nettoyés.
Les transformations seront réalisées par le code et documentées.