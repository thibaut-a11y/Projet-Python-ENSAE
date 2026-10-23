"""Préparation des prix et calcul des rendements"""

import numpy as np
import pandas as pd


def prepare_prices(datasets, tickers):
    """comme expliquer dans le notebook, on réunit les prix ajustés dans une table commune"""
    price_series = {}

    for ticker in tickers:
        data = datasets[ticker]

        if data.index.has_duplicates:
            raise ValueError(f"{ticker} : dates dupliquées")

        price_series[ticker] = data["Adj Close"]

    prices = pd.DataFrame(price_series).sort_index()

    if prices.empty:
        raise ValueError("La table des prix est vide")

    if not np.isfinite(prices.to_numpy()).all():
        raise ValueError("Des prix sont manquants ou non finis")

    if (prices <= 0).any().any():
        raise ValueError("Des prix sont nuls ou négatifs")

    return prices


def compute_returns(prices, start, end):
    """on calcule les rendements quotidiens et mensuels"""
    daily_returns = prices.pct_change(fill_method=None)
    daily_returns = daily_returns.loc[start:end]

    monthly_prices = prices.resample("ME").last()

    monthly_returns = monthly_prices.pct_change(fill_method=None)
    monthly_returns = monthly_returns.loc[start:end]

    if (
        daily_returns.isna().any().any()
        or monthly_returns.isna().any().any()
    ):
        raise ValueError(
            "Des rendements sont manquants "
            "Vérifier la couverture et les prix antérieurs "
            "au début de l'analyse"
        )

    return daily_returns, monthly_returns