"""graphiques du rapport avec matplotlib"""
import matplotlib.pyplot as plt

couleurs = {
    "Actions US": "#173F5F", "Actions monde": "#D55E00",
    "US 60/40": "#007E87", "Monde 60/40": "#8E6C8A",
    "US 50/30/20": "#AD7B16", "US 60/40 court": "#727C86",
    "US 60/40 cash": "#2E8B57",
}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False})


def tracer_capital(capital):
    """compare la croissance des sept portefeuilles en base cent"""
    axe = (100 * capital).plot(figsize=(10, 5), logy=True,
                              color=[couleurs[nom] for nom in capital])
    axe.set(title="Croissance des sept allocations", xlabel="Année",
            ylabel="Capital en USD base 100 — échelle logarithmique")
    axe.set_yticks([50, 100, 200, 400, 800], ["50", "100", "200", "400", "800"])
    axe.minorticks_off()
    axe.legend(ncol=3, fontsize=8)
    axe.grid(alpha=.2)
    plt.tight_layout()
    plt.show()


def tracer_reculs(recul):
    """compare les pertes depuis le sommet de quatre portefeuilles"""
    noms = ["Actions US", "Actions monde", "US 60/40", "US 50/30/20"]
    axe = (100 * recul[noms]).plot(figsize=(10, 5), color=[couleurs[n] for n in noms])
    axe.set(title="Recul depuis le sommet propre à chaque portefeuille",
            xlabel="Année", ylabel="Recul depuis le plus haut (%)")
    axe.legend(ncol=2, fontsize=8, loc="lower right")
    axe.grid(alpha=.2)
    plt.tight_layout()
    plt.show()


def tracer_episodes(performance_episodes, episodes):
    """compare les rendements sur les mêmes dates de baisse de spy"""
    figure, axe = plt.subplots(figsize=(10, 5))
    image = axe.imshow(performance_episodes, cmap="RdBu", vmin=-60, vmax=60, aspect="auto")
    dates = [f"{ligne.sommet:%Y-%m} → {ligne.creux:%Y-%m}" for ligne in episodes.itertuples()]
    axe.set_xticks(range(len(performance_episodes.columns)), performance_episodes.columns,
                   rotation=20, ha="right")
    axe.set_yticks(range(len(episodes)), dates)
    for i, ligne in enumerate(performance_episodes.to_numpy()):
        for j, valeur in enumerate(ligne):
            axe.text(j, i, f"{valeur:.1f} %", ha="center", va="center",
                     color="white" if abs(valeur) > 40 else "black", fontsize=9)
    axe.set_title("Rendement du sommet au creux de SPY")
    figure.colorbar(image, ax=axe, label="Rendement composé (%)")
    plt.tight_layout()
    plt.show()


def tracer_correlations(correlations):
    """affiche les corrélations entre les actifs"""
    figure, axe = plt.subplots(figsize=(7, 5))
    image = axe.imshow(correlations, cmap="RdBu", vmin=-1, vmax=1)
    axe.set_xticks(range(len(correlations)), correlations.columns)
    axe.set_yticks(range(len(correlations)), correlations.index)
    for i, ligne in enumerate(correlations.to_numpy()):
        for j, valeur in enumerate(ligne):
            axe.text(j, i, f"{valeur:.2f}", ha="center", va="center",
                     color="white" if abs(valeur) > .65 else "black")
    axe.set_title("Corrélations quotidiennes des actifs — 2007–2025")
    figure.colorbar(image, ax=axe, label="Coefficient de Pearson")
    plt.tight_layout()
    plt.show()
