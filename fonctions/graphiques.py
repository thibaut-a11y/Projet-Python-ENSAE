"""graphiques du rapport"""
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.ticker import PercentFormatter, NullFormatter
from io import BytesIO
from IPython.display import Image, display


plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": "white"})
couleurs = {
    "Actions US": "#173F5F",
    "Actions monde": "#D55E00",
    "US 60/40": "#007E87",
    "Monde 60/40": "#8E6C8A",
    "US 50/30/20": "#AD7B16",
    "US 60/40 court": "#727C86",
}


def afficher_figure(figure):
    """affiche la figure en mémoire sans créer de fichier intermédiaire"""
    figure.text(.01, -.03, "Source : Yahoo Finance, cours ajustés ; calculs du projet, 2006–2025",
                fontsize=8, color="#596773")
    # le tampon conserve la figure en mémoire au lieu de créer un fichier
    tampon = BytesIO()
    figure.savefig(tampon, format="png", dpi=160, bbox_inches="tight")
    plt.close(figure)
    display(Image(data=tampon.getvalue()))


def tracer_capital(capital):
    """trace le capital des six allocations avec une échelle logarithmique"""
    figure, axe = plt.subplots(figsize=(10, 5), layout="constrained")
    for nom in capital:
        axe.plot(capital.index, 100 * capital[nom], label=nom, color=couleurs[nom], linewidth=1.3)
    axe.set_yscale("log")
    axe.set_yticks([50, 100, 200, 400, 800], ["50", "100", "200", "400", "800"])
    axe.yaxis.set_minor_formatter(NullFormatter())
    axe.set(title="Croissance des six allocations", xlabel="Année",
            ylabel="Capital en USD, base 100 fin 2005 (échelle logarithmique)")
    axe.legend(ncol=3, fontsize=8, loc="upper left")
    axe.grid(alpha=.2)
    afficher_figure(figure)


def tracer_reculs(recul):
    """trace les reculs depuis le sommet propre à chaque portefeuille"""
    figure, axe = plt.subplots(figsize=(10, 5), layout="constrained")
    for nom in ["Actions US", "Actions monde", "US 60/40", "US 50/30/20"]:
        axe.plot(recul.index, 100 * recul[nom], label=nom, color=couleurs[nom], linewidth=1.2)
    axe.set_title("Recul depuis le sommet propre à chaque portefeuille", pad=40)
    axe.set(xlabel="Année", ylabel="Recul depuis le plus haut (%)")
    axe.yaxis.set_major_formatter(PercentFormatter(100))
    axe.legend(ncol=4, fontsize=8, loc="lower left", bbox_to_anchor=(0, 1.01))
    axe.grid(alpha=.2)
    afficher_figure(figure)


def tracer_episodes(performance_episodes, episodes):
    """compare les pertes des portefeuilles pendant les cycles de spy"""
    etiquettes = [f"{ligne.sommet:%d/%m/%Y} → {ligne.creux:%d/%m/%Y}" for ligne in episodes.itertuples()]
    figure, axe = plt.subplots(figsize=(10, 4.5), layout="constrained")
    image = axe.imshow(performance_episodes, cmap="RdBu", aspect="auto",
                       norm=TwoSlopeNorm(vmin=-60, vcenter=0, vmax=20))
    axe.set_xticks(range(len(performance_episodes.columns)), performance_episodes.columns,
                   rotation=20, ha="right")
    axe.set_yticks(range(len(episodes)), etiquettes)
    for numero_ligne, ligne in enumerate(performance_episodes.to_numpy()):
        for numero_colonne, valeur in enumerate(ligne):
            axe.text(numero_colonne, numero_ligne, f"{valeur:.1f} %", ha="center", va="center",
                     color="white" if valeur < -40 else "#263746", fontsize=9)
    axe.set_title("Rendement du sommet au creux de SPY : mêmes dates pour tous", pad=12)
    figure.colorbar(image, ax=axe, label="Rendement composé (%)", shrink=.8)
    afficher_figure(figure)


def tracer_correlations(correlations):
    """affiche les corrélations entre les rendements des actifs"""
    figure, axe = plt.subplots(figsize=(7, 5), layout="constrained")
    image = axe.imshow(correlations, cmap="RdBu", vmin=-1, vmax=1)
    axe.set_xticks(range(len(correlations.columns)), correlations.columns)
    axe.set_yticks(range(len(correlations.index)), correlations.index)
    for numero_ligne, ligne in enumerate(correlations.to_numpy()):
        for numero_colonne, valeur in enumerate(ligne):
            axe.text(numero_colonne, numero_ligne, f"{valeur:.2f}", ha="center", va="center",
                     color="white" if abs(valeur) > .65 else "#263746")
    axe.set_title("Corrélations des rendements quotidiens, 2006–2025")
    figure.colorbar(image, ax=axe, label="Coefficient de Pearson", shrink=.8)
    afficher_figure(figure)
