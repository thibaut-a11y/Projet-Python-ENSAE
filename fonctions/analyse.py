"""calcul des portefeuilles et des indicateurs"""
import numpy as np
import pandas as pd


ALLOCATIONS = {
    "Actions US": {"SPY": 1.0},
    "Actions monde": {"SPY": .60, "EFA": .25, "EEM": .15},
    "US 60/40": {"SPY": .60, "IEF": .40},
    "Monde 60/40": {"SPY": .36, "EFA": .15, "EEM": .09, "IEF": .40},
    "US 50/30/20": {"SPY": .50, "IEF": .30, "GLD": .20},
    "US 60/40 court": {"SPY": .60, "SHY": .40},
    "US 60/40 cash": {"SPY": .60, "BIL": .40},
}


def simuler_portefeuille(prix, allocation, frequence="M"):
    poids_cibles = pd.Series(allocation, dtype=float)
    variations = prix[poids_cibles.index].pct_change().iloc[1:]  # 1. rendement quotidien de chaque actif

    poids = poids_cibles.copy()
    date_precedente = prix.index[0]
    rendements = []

    for date, variation in variations.iterrows():
        if date.to_period(frequence) != date_precedente.to_period(frequence):
            poids = poids_cibles.copy()          # 4. début de nouveau mois : on réajuste les proportions à 60/40

        rendement = (poids * variation).sum()    # 2. rendement du portefeuille ce jour-là
        rendements.append(rendement)

        poids = poids * (1 + variation)          # 3a. chaque actif grossit/baisse selon sa variation
        poids = poids / poids.sum()              # 3b. on re-divise par le total pour retrouver les % (somme = 100 %)
        date_precedente = date

    return pd.Series(rendements, index=variations.index)


def simuler_allocations(prix, frequence="M"):
    """applique la simulation aux sept allocations"""
    rendements = {}
    for nom, poids in ALLOCATIONS.items():
        rendements[nom] = simuler_portefeuille(prix, poids, frequence)
    return pd.DataFrame(rendements)


def capital_et_recul(rendements, date_initiale):
    """calcule le capital et le recul depuis le meilleur niveau atteint"""
    depart = pd.DataFrame(1.0, index=[date_initiale], columns=rendements.columns)
    capital = pd.concat([depart, (1 + rendements).cumprod()])
    recul = capital / capital.cummax() - 1
    return capital, recul


def indicateurs(rendements, capital, recul):
    """résume le rendement annualisé la volatilité et le recul maximal"""
    # la durée totale est exprimée en années calendaires
    annees = (capital.index[-1] - capital.index[0]).days / 365.25
    return pd.DataFrame({
        "rendement annualisé (%)": 100 * (capital.iloc[-1] ** (1 / annees) - 1),
        "volatilité annualisée (%)": 100 * rendements.std(ddof=1) * np.sqrt(252),
        "recul maximal (%)": 100 * recul.min(),
    })


def reperer_episodes(capital_marche, seuil=.10):
    """repère les baisses depuis un sommet et leur première récupération"""
    sommet = creux = capital_marche.index[0]
    lignes = []
    for date, valeur in capital_marche.iloc[1:].items():
        if valeur >= capital_marche.loc[sommet]:
            recul = capital_marche.loc[creux] / capital_marche.loc[sommet] - 1
            if recul <= -seuil:
                lignes.append((sommet, creux, date))
            sommet = creux = date
        elif valeur < capital_marche.loc[creux]:
            creux = date
    # le dernier cycle peut ne pas être terminé
    recul = capital_marche.loc[creux] / capital_marche.loc[sommet] - 1
    if recul <= -seuil:
        lignes.append((sommet, creux, pd.NaT))
    return pd.DataFrame(lignes, columns=["sommet", "creux", "recuperation"])


def rendements_episodes(capital, episodes):
    """compare les portefeuilles entre les mêmes dates de sommet et de creux"""
    valeurs = []
    for ligne in episodes.itertuples():
        rendement = capital.loc[ligne.creux] / capital.loc[ligne.sommet] - 1
        valeurs.append(100 * rendement)
    return pd.DataFrame(valeurs, columns=capital.columns, index=episodes.index)


def pertes_en_baisse(rendements):
    """compare les rendements pendant les séances négatives de spy"""
    reference = rendements["Actions US"]
    jours_baisse = reference < 0
    reference_baisse = reference.loc[jours_baisse]
    resultats = {}
    for nom in rendements:
        serie = rendements.loc[jours_baisse, nom]
        resultats[nom] = {
            "rendement moyen (%)": 100 * serie.mean(),
            "mieux que SPY (%)": 100 * (serie > reference_baisse).mean(),
            "sans perte (%)": 100 * (serie >= 0).mean(),
        }
    return pd.DataFrame(resultats).T


def contexte_inflation(rendements_actifs, inflation):
    """Compare la corrélation mensuelle SPY-IEF selon que l'inflation est < 3 % ou >= 3 %."""
    # 1. Passer de l'indice des prix au taux d'inflation annuel (%) par mois
    taux = 100 * inflation["CPIAUCSL"].pct_change(12, fill_method=None)
    taux.index = taux.index.to_period("M")

    # 2. Regrouper les rendements quotidiens par mois et coller l'inflation dessus
    mensuel = (1 + rendements_actifs).resample("ME").prod() - 1
    mensuel.index = mensuel.index.to_period("M")
    mensuel["inflation"] = taux
    mensuel = mensuel.dropna(subset=["inflation"])

    # 3. Séparer en 2 groupes simples (< 3 % et >= 3 %) et calculer la corrélation
    basse = mensuel[mensuel["inflation"] < 3]
    haute = mensuel[mensuel["inflation"] >= 3]
    return pd.DataFrame({
        "nombre de mois": [len(basse), len(haute)],
        "corrélation mensuelle SPY–IEF": [basse["SPY"].corr(basse["IEF"]), haute["SPY"].corr(haute["IEF"])],
    }, index=["inflation < 3 %", "inflation ≥ 3 %"])


def comparer_decennies(rendements):
    """Compare l'écart moyen à SPY les jours de baisse sur les deux sous-périodes."""
    p1 = pertes_en_baisse(rendements.loc[:"2015-12-31"])["rendement moyen (%)"]
    p2 = pertes_en_baisse(rendements.loc["2016-01-01":])["rendement moyen (%)"]
    return pd.DataFrame({
        "2007–2015 (pb)": 100 * (p1 - p1["Actions US"]),
        "2016–2025 (pb)": 100 * (p2 - p2["Actions US"]),
    })


def comparer_seuils(capital):
    """compte les cycles mieux traversés que spy pour deux seuils de baisse"""
    lignes = []
    for seuil in [.10, .20]:
        episodes = reperer_episodes(capital["Actions US"], seuil)
        performances = rendements_episodes(capital, episodes)
        for nom in capital:
            mieux_que_spy = performances[nom] > performances["Actions US"]
            sans_perte = performances[nom] >= 0
            lignes.append({
                "seuil (%)": seuil * 100,
                "portefeuille": nom,
                "cycles": len(episodes),
                "cycles mieux que SPY": int(mieux_que_spy.sum()),
                "cycles sans perte": int(sans_perte.sum()),
            })
    return pd.DataFrame(lignes).set_index(["seuil (%)", "portefeuille"])


def comparer_temoin(prix, rendements, episodes):
    """compare le portefeuille obligataire au témoin avec une poche constante"""
    prix_temoin = prix[["SPY"]].copy()
    prix_temoin["poche_nulle"] = 1.0
    temoin = simuler_portefeuille(prix_temoin, {"SPY": .60, "poche_nulle": .40})
    comparaison = pd.DataFrame({
        "US 60/40 (%)": rendements["US 60/40"],
        "Témoin nul (%)": temoin,
    })
    capital, _ = capital_et_recul(comparaison, prix.index[0])
    performances = rendements_episodes(capital, episodes)
    performances["écart 60/40 − témoin (points)"] = (
        performances["US 60/40 (%)"] - performances["Témoin nul (%)"])
    performances.insert(0, "creux", episodes.creux)
    performances.insert(0, "sommet", episodes.sommet)
    return performances
