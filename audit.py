"""fonctions d'audit et de préparation des données"""
import matplotlib.pyplot as plt
import pandas as pd


def auditer_prix(prices):
    """Vérifie la qualité des cours et renvoie un tableau récapitulatif par actif."""
    assert prices.index.is_monotonic_increasing, "Les dates ne sont pas triées"
    assert prices.index.is_unique, "Il y a des dates en double"

    resume = pd.DataFrame({
        "première date": prices.apply(lambda s: s.first_valid_index().date()),
        "dernière date": prices.apply(lambda s: s.last_valid_index().date()),
        "séances": prices.notna().sum(),
        "manquants": prices.isna().sum(),
        "prix <= 0": (prices <= 0).sum(),
    })

    assert not prices.isna().any().any(), "Il y a des valeurs manquantes dans les prix"
    assert (prices > 0).all().all(), "Il y a des prix négatifs ou nuls"
    return resume


def tracer_base_100(prices):
    """Trace l'évolution des actifs ramenés à une base 100 au premier jour."""
    base_100 = (prices / prices.iloc[0]) * 100
    base_100.plot(figsize=(10, 5))
    plt.title(f"Évolution des {prices.shape[1]} actifs - Base 100")
    plt.ylabel("Valeur d'un investissement de 100 $")
    plt.grid(True, alpha=0.3)
    plt.show()


def auditer_cpi(cpi):
    """Affiche le nombre de mois reçus et le nombre de valeurs manquantes."""
    return pd.DataFrame({
        "première date": [cpi.index.min().date()],
        "dernière date": [cpi.index.max().date()],
        "nombre de lignes": [len(cpi)],
        "cases nulles": [int(cpi["CPIAUCSL"].isna().sum())],
    })
