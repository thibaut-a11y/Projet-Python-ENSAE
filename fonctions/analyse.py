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
}


def simuler_portefeuille(prix, allocation, frequence="M"):
    """calcule les rendements avec rééquilibrage et dérive des poids"""
    poids_cibles = pd.Series(allocation, dtype=float)
    assert np.isclose(poids_cibles.sum(), 1) and (poids_cibles >= 0).all()
    variations = prix[poids_cibles.index].pct_change(fill_method=None).iloc[1:]
    assert not variations.isna().any().any()
    poids = poids_cibles.copy()
    date_precedente = prix.index[0]
    rendements = []
    for date, variation in variations.iterrows():
        # on revient aux poids cibles au début de chaque période
        if date.to_period(frequence) != date_precedente.to_period(frequence):
            poids = poids_cibles.copy()
        rendement = poids.dot(variation)
        rendements.append(rendement)
        # entre deux rééquilibrages les poids suivent les cours
        poids = poids * (1 + variation) / (1 + rendement)
        date_precedente = date
    return pd.Series(rendements, index=variations.index)


def simuler_allocations(prix, frequence="M"):
    """applique la simulation aux six allocations"""
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
    """compare la corrélation mensuelle dans les deux groupes de taux annuels"""
    mensuel = (1 + rendements_actifs).resample("ME").prod() - 1
    mensuel.index = mensuel.index.to_period("M")
    mensuel = mensuel.join(inflation).dropna(subset=["inflation_pct"])
    mensuel["regime"] = "inflation < 3 %"
    mensuel.loc[mensuel["inflation_pct"] >= 3, "regime"] = "inflation ≥ 3 %"
    lignes = []
    for regime, groupe in mensuel.groupby("regime"):
        lignes.append({"régime": regime, "nombre de mois": len(groupe),
                       "corrélation mensuelle SPY–IEF": groupe["SPY"].corr(groupe["IEF"])})
    return pd.DataFrame(lignes).set_index("régime")


def comparer_decennies(prix):
    """compare les écarts à spy pendant les deux décennies"""
    periodes = {
        "2007–2015": prix.loc[:"2015-12-31"],
        "2016–2025": prix.loc["2015-12-31":],
    }
    ecarts = {}
    for periode, echantillon in periodes.items():
        rendements = simuler_allocations(echantillon)
        reference = rendements["Actions US"]
        jours_baisse = reference < 0
        ecarts[periode] = {}
        for nom in rendements:
            difference = rendements[nom] - reference
            # on exprime les écarts quotidiens en points de base
            ecarts[periode][nom] = 10000 * difference.loc[jours_baisse].mean()
    return pd.DataFrame(ecarts).rename_axis("écart à SPY les jours de baisse (pb)")


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
