# Protocole d’analyse

## Question

Les obligations et l’or apportent-ils une protection supplémentaire
par rapport à la trésorerie lors des baisses du marché actions,
à exposition actions identique ?

## Comparaisons

- A : 100 % SPY.
- B : 60 % SPY et 40 % BIL.
- C : 60 % SPY et 40 % IEF.
- D : 60 % SPY, 30 % IEF et 10 % GLD.

A sert de référence actions.
B sert de référence pour les portefeuilles diversifiés C et D.
Les différences C − B et D − B sont centrales dans l’analyse.

## Périmètre

- Analyse en USD.
- Période cible : juin 2007 à décembre 2025.
- Collecte pilote : 2019–2023.
- Collecte quotidienne, puis construction de rendements mensuels.
- Retour aux pondérations cibles à chaque fin de mois,
  pour la période suivante.

## Définition des baisses

Analyse principale : mois où le rendement de SPY est négatif.

Analyse complémentaire : épisodes où SPY atteint une baisse
d’au moins 10 % par rapport à son précédent sommet.

Le drawdown est défini par :

    drawdown = valeur / maximum historique − 1

Le seuil de baisse est donc drawdown <= −0,10.
Les épisodes seront suivis du sommet jusqu’à sa récupération,
sans compter plusieurs fois des épisodes imbriqués.

Un épisode encore ouvert en fin d’échantillon sera signalé
comme non récupéré.

## Indicateurs prévus

- Rendements cumulés et mensuels.
- Écarts de rendement entre C et B, puis D et B.
- Fréquence de surperformance de C et D par rapport à B.
- Volatilité et corrélations.
- Drawdown maximal et temps de récupération.

Chaque résultat sera interprété en lien avec la problématique.

## Enrichissement macroéconomique

- CPIAUCSL : calcul de l’inflation à partir de l’indice des prix.
- DGS10 : niveau et variation du taux américain à dix ans.

Ces variables serviront à contextualiser les résultats.
Les associations observées ne démontreront pas une causalité.

## Points à vérifier et à documenter

- Couverture effective des séries.
- Ajustements des prix et traitement des distributions.
- Valeurs manquantes et différences de calendrier.
- Données antérieures nécessaires au premier rendement.
- Agrégation et alignement des séries macroéconomiques.
- Hypothèses concernant les frais de transaction et la fiscalité.
- Limites des ETF comme représentations des classes d’actifs.