from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from simulations.pva_engine import simulate_pva, summarize_pva
from utils.ui import explain, learning_notes, module_intro, section, style_figure


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
        seed = st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=91)

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
    learning_notes(
        "Comparer plusieurs actions évite de raisonner sur un seul futur possible.",
        "Le résultat dépend des hypothèses ; il faut les justifier avec des données de terrain.",
        "Compare la restauration seule et l'action combinée : que gagne-t-on réellement ?",
    )
    display = results.copy()
    display["Risque quasi-extinction"] = display["Risque quasi-extinction"].map(lambda v: f"{100 * v:.1f} %")
    st.dataframe(display, use_container_width=True)
    st.download_button("Exporter les scénarios CSV", results.to_csv(index=False).encode("utf-8"), "orni_lab_scenarios.csv", "text/csv")
