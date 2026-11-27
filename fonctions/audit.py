"""audit des cours et du calendrier de l indice des prix"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def auditer_prix(prices):
    """vérifie les cours et renvoie un diagnostic par actif"""
    assert not prices.empty, "Aucun cours disponible"
    assert prices.index.is_monotonic_increasing, "Les dates ne sont pas triées"
    assert prices.index.is_unique, "Il y a des dates en double"
    assert prices.notna().any().all(), "Une série ne contient aucun cours"
    resume = pd.DataFrame({
        "première date": prices.apply(lambda s: s.first_valid_index().date()),
        "dernière date": prices.apply(lambda s: s.last_valid_index().date()),
        "séances": prices.notna().sum(),
        "manquants": prices.isna().sum(),
        "prix <= 0": (prices <= 0).sum(),
    })
    assert np.isfinite(prices.to_numpy()).all(), "Prix manquant ou infini"
    assert (prices > 0).all().all(), "Il y a des prix négatifs ou nuls"
    return resume


def tracer_base_100(prices):
    """trace les actifs en base cent pour une exploration complémentaire"""
    base_100 = (prices / prices.iloc[0]) * 100
    base_100.plot(figsize=(10, 5))
    plt.title(f"Évolution des {prices.shape[1]} actifs en base 100")
    plt.xlabel("Année")
    plt.ylabel("Valeur d un investissement de 100 USD")
    plt.grid(True, alpha=0.3)
    plt.show()


def auditer_cpi(cpi):
    """contrôle le calendrier et compte les mois sans indice"""
    assert not cpi.empty, "Aucun indice des prix disponible"
    assert cpi.index.is_unique and cpi.index.is_monotonic_increasing
    calendrier = pd.date_range(cpi.index.min(), cpi.index.max(), freq="MS")
    assert cpi.index.equals(calendrier), "Le calendrier mensuel est incomplet"
    valeurs = cpi["CPIAUCSL"].dropna()
    assert np.isfinite(valeurs.to_numpy()).all() and (valeurs > 0).all()
    return pd.DataFrame({
        "première date": [cpi.index.min().date()],
        "dernière date": [cpi.index.max().date()],
        "nombre de mois": [len(cpi)],
        "mois sans indice": [int(cpi["CPIAUCSL"].isna().sum())],
    })
