"""vérifications indépendantes des données et des calculs"""
import numpy as np
import pandas as pd


def capital_par_parts(prix, poids):
    """reconstitue le capital avec des parts fixes pendant chaque mois"""
    capitaux_mensuels = []
    capital_depart = 1.0
    date_depart = prix.index[0]
    prix_suivants = prix.iloc[1:]
    mois = prix_suivants.index.to_period("M")
    for _, cours_mois in prix_suivants.groupby(mois):
        evolutions = cours_mois / prix.loc[date_depart]
        # chaque colonne est multipliée par le poids du même actif
        capital_mois = capital_depart * (evolutions * poids).sum(axis=1)
        capitaux_mensuels.append(capital_mois)
        capital_depart = capital_mois.iloc[-1]
        date_depart = cours_mois.index[-1]
    return pd.concat(capitaux_mensuels)


def verifier_calendrier(prix, rendements):
    """contrôle les prix et le calendrier commun des rendements"""
    assert prix.index.is_unique and prix.index.is_monotonic_increasing
    assert np.isfinite(prix.to_numpy()).all() and (prix > 0).all().all()
    assert len(rendements) == len(prix) - 1
    assert prix.index[1:].equals(rendements.index)


def verifier_spy(prix, rendements, capital, poids_cibles):
    """vérifie les poids et le portefeuille entièrement investi en spy"""
    assert np.isfinite(rendements.to_numpy()).all() and (rendements > -1).all().all()
    np.testing.assert_allclose(poids_cibles.sum(axis=1), 1)
    rendements_spy = prix["SPY"].pct_change(fill_method=None).iloc[1:]
    np.testing.assert_allclose(rendements["Actions US"], rendements_spy, atol=1e-11)
    np.testing.assert_allclose(capital["Actions US"], prix["SPY"] / prix["SPY"].iloc[0], rtol=1e-8)


def verifier_reculs(capital, synthese):
    """recalcule les reculs maximaux avec une boucle"""
    for nom in capital:
        sommet = 1.0
        pire_recul = 0.0
        for valeur in capital[nom]:
            sommet = max(sommet, valeur)
            pire_recul = min(pire_recul, valeur / sommet - 1)
        assert np.isclose(100 * pire_recul, synthese.loc[nom, "recul maximal (%)"], atol=1e-7)


def verifier_episodes(capital, episodes):
    """vérifie les sommets les creux et les premières récupérations"""
    marche = capital["Actions US"]
    plus_haut = marche.cummax()
    for ligne in episodes.itertuples():
        fin = ligne.recuperation if pd.notna(ligne.recuperation) else marche.index[-1]
        assert ligne.sommet <= ligne.creux <= fin
        sommet = marche.loc[ligne.sommet]
        assert np.isclose(sommet, plus_haut.loc[ligne.sommet])
        assert np.isclose(marche.loc[ligne.creux], marche.loc[ligne.sommet:fin].min())
        assert marche.loc[ligne.creux] / sommet - 1 <= -.10
        dates_intermediaires = (marche.index > ligne.sommet) & (marche.index < fin)
        assert (marche.loc[dates_intermediaires] < sommet).all()
        if pd.notna(ligne.recuperation):
            assert marche.loc[fin] >= sommet


def verifier_portefeuilles(prix, poids_cibles, capital):
    """compare les six trajectoires au calcul indépendant en parts fixes"""
    for nom, poids in poids_cibles.iterrows():
        capital_attendu = capital_par_parts(prix, poids)
        np.testing.assert_allclose(capital.loc[capital_attendu.index, nom], capital_attendu, rtol=1e-8, atol=1e-9)


def verifier_temoin(prix, capital, episodes, comparaison):
    """contrôle le témoin et les écarts au portefeuille obligataire"""
    prix_temoin = prix[["SPY"]].copy()
    prix_temoin["poche_nulle"] = 1.0
    poids = pd.Series({"SPY": .60, "poche_nulle": .40})
    capital_attendu = capital_par_parts(prix_temoin, poids)
    capital_attendu.loc[prix.index[0]] = 1.0
    assert comparaison.sommet.equals(episodes.sommet)
    assert comparaison.creux.equals(episodes.creux)
    for numero, ligne in episodes.iterrows():
        perte_temoin = 100 * (capital_attendu.loc[ligne.creux] / capital_attendu.loc[ligne.sommet] - 1)
        perte_6040 = 100 * (capital.loc[ligne.creux, "US 60/40"]
                            / capital.loc[ligne.sommet, "US 60/40"] - 1)
        assert np.isclose(comparaison.loc[numero, "Témoin nul (%)"], perte_temoin, atol=1e-8)
        assert np.isclose(comparaison.loc[numero, "US 60/40 (%)"], perte_6040, atol=1e-8)
        assert np.isclose(comparaison.loc[numero, "écart 60/40 − témoin (points)"],
                          perte_6040 - perte_temoin, atol=1e-8)
