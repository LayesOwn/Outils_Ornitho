from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from simulations.pva_engine import simulate_pva, summarize_pva
except ImportError as _pva_err:
    simulate_pva = None  # type: ignore[assignment]
    summarize_pva = None  # type: ignore[assignment]
    _PVA_IMPORT_ERROR = str(_pva_err)
else:
    _PVA_IMPORT_ERROR = ""
from utils.ui import explain, learning_notes, module_intro, section, style_figure, teacher_formula, teacher_note, teacher_pitfalls


@st.cache_data
def run_scenario_table(n0: int, years: int, seed: int) -> pd.DataFrame:
    scenarios = {
        "Sans action": {"mean_r": 0.00, "sd_r": 0.11, "loss": 10, "k": 700},
        "Restauration habitat": {"mean_r": 0.05, "sd_r": 0.09, "loss": 6, "k": 1100},
        "Réduction mortalité": {"mean_r": 0.03, "sd_r": 0.08, "loss": 2, "k": 800},
        "Action combinée": {"mean_r": 0.07, "sd_r": 0.07, "loss": 1, "k": 1200},
    }
    rows = []
    for i, (name, params) in enumerate(scenarios.items()):
        data = simulate_pva(n0, params["mean_r"], params["sd_r"], params["k"], years, 250, 25, params["loss"], seed + i)
        summary = summarize_pva(data, 25)
        rows.append({"Scénario": name, "Risque quasi-extinction": summary["risk"], "Médiane finale": summary["median_final"]})
    return pd.DataFrame(rows)


def render(context: dict) -> None:
    if _PVA_IMPORT_ERROR:
        st.error(f"Module Scénarios non disponible : {_PVA_IMPORT_ERROR}")
        return
    section("Scénarios de gestion", "Comparer plusieurs actions de conservation sur une même population.")
    module_intro(
        "Un scénario de gestion est une hypothèse d'action : restaurer l'habitat, réduire la mortalité ou combiner plusieurs mesures.",
        "Comparer les scénarios aide à choisir les actions qui réduisent le plus le risque pour un coût écologique ou opérationnel donné.",
        "En ornithologie, cette approche soutient les plans d'action pour colonies nicheuses, espèces menacées ou sites de migration.",
    )

    left, right = st.columns([0.75, 1.6])
    with left:
        n0 = st.slider("Effectif initial commun", 20, 1500, 160)
        years = st.slider("Horizon de comparaison", 10, 80, 40)
        seed = int(st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=91) or 91)

    results = run_scenario_table(n0, years, int(seed))
    with right:
        fig = px.bar(
            results,
            x="Scénario",
            y="Risque quasi-extinction",
            color="Scénario",
            text=results["Risque quasi-extinction"].map(lambda v: f"{100 * v:.1f} %"),
        )
        fig.update_layout(yaxis_tickformat=".0%", showlegend=False)
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    best = results.sort_values("Risque quasi-extinction").iloc[0]
    explain(f"Le scénario le plus favorable est « {best['Scénario']} », avec un risque estimé de {100 * best['Risque quasi-extinction']:.1f} %.")
    teacher_note(
        "Un scénario de gestion est une simulation PVA sous un jeu d'hypothèses explicites : taux de croissance moyen r̄, "
        "variabilité environnementale σ_e, capacité de charge K et pertes annuelles fixes (prélèvement, mortalité additionnelle). "
        "La comparaison entre scénarios repose sur deux métriques : (1) le risque de quasi-extinction (fraction de trajectoires "
        "passant sous le seuil quasi-extinction avant l'horizon) et (2) la médiane finale de l'effectif. "
        "Un scénario peut réduire le risque sans augmenter la médiane (si l'action élimine les mauvaises trajectoires) "
        "ou augmenter la médiane sans réduire le risque (si quelques trajectoires explosent mais les pires persistent). "
        "La décision de gestion doit tenir compte des deux. "
        "Principe d'optimalité : l'action optimale maximise une fonction d'utilité (ex. : risque minimal sous contrainte budgétaire) "
        "— la comparaison graphique est utile mais ne remplace pas une analyse décisionnelle formelle.",
        context,
    )
    teacher_formula(
        "Risque de quasi-extinction — estimateur Monte-Carlo",
        r"P(\text{QE}) = \frac{1}{B}\sum_{b=1}^{B} \mathbf{1}\!\left[\min_{t \le T} N_b(t) \le N_{\min}\right]"
        r"\qquad N_b(t+1) = \max\!\bigl(0,\,\min(K,\,N_b(t)\,e^{\bar{r}+\varepsilon_t} - \text{pertes})\bigr)",
        context,
    )
    teacher_formula(
        "Impact d'une réduction de mortalité sur λ — perturbation de premier ordre",
        r"\Delta\lambda \approx \frac{\partial\lambda}{\partial s}\,\Delta s"
        r"\qquad \text{(sensibilité de Leslie, Caswell 2001)}",
        context,
    )
    teacher_pitfalls(
        [
            "Comparer des scénarios avec des paramètres par défaut non justifiés : les résultats sont sensibles à r̄ et σ_e — une analyse de sensibilité paramétrique est indispensable.",
            "Interpréter un risque = 0 % comme 'population sûre' sur un court horizon : les événements rares n'ont pas encore eu le temps de se produire.",
            "Choisir le scénario qui maximise uniquement la médiane finale : une médiane haute peut masquer un risque élevé si la variance est grande.",
            "Supposer que les effets des actions sont additifs : restauration habitat + réduction mortalité peut interagir de façon non linéaire avec la densité-dépendance.",
            "Omettre le coût opérationnel et la faisabilité : l'action combinée est souvent la 'meilleure' en simulation mais la plus difficile à mettre en œuvre.",
        ],
        context,
    )
    learning_notes(
        "Comparer plusieurs actions évite de raisonner sur un seul futur possible.",
        "Le résultat dépend des hypothèses ; il faut les justifier avec des données de terrain.",
        "Compare la restauration seule et l'action combinée : que gagne-t-on réellement ?",
    )
    display = results.copy()
    display["Risque quasi-extinction"] = display["Risque quasi-extinction"].map(lambda v: f"{100 * v:.1f} %")
    st.dataframe(display, use_container_width=True)
    st.download_button("Exporter les scénarios CSV", results.to_csv(index=False).encode("utf-8"), "orni_lab_scenarios.csv", "text/csv")
