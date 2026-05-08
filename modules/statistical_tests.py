from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy import stats

from core.export import build_pdf_report
from utils.ui import explain, learning_notes, module_intro, section, style_figure, teacher_note


def generate_two_groups(seed: int, n_a: int, n_b: int, mean_a: float, mean_b: float, sd: float) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    values = np.concatenate([rng.normal(mean_a, sd, n_a), rng.normal(mean_b, sd, n_b)]).clip(0, None)
    return pd.DataFrame({"Habitat": ["Forêt restaurée"] * n_a + ["Forêt dégradée"] * n_b, "Succès reproducteur": values})


def render(context: dict) -> None:
    section("Tests statistiques", "Exemple : comparaison du succès reproducteur entre deux habitats.")
    module_intro(
        "Un test statistique évalue si une différence observée est compatible avec le hasard sous une hypothèse nulle.",
        "Il sert à formaliser une comparaison entre groupes ou conditions, tout en tenant compte de la variabilité d'échantillonnage.",
        "En ornithologie, il aide à comparer des habitats, des années, des traitements de conservation ou des pressions anthropiques.",
    )

    left, right = st.columns([0.9, 1.5])
    with left:
        n_a = st.slider("Nids en forêt restaurée", 8, 120, 36)
        n_b = st.slider("Nids en forêt dégradée", 8, 120, 34)
        mean_a = st.slider("Moyenne restaurée", 0.0, 6.0, 3.2, step=0.1)
        mean_b = st.slider("Moyenne dégradée", 0.0, 6.0, 2.4, step=0.1)
        sd = st.slider("Variabilité entre nids", 0.2, 3.0, 1.1, step=0.1)
        seed = st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=33)

    data = generate_two_groups(int(seed), n_a, n_b, mean_a, mean_b, sd)
    group_a = data.loc[data["Habitat"] == "Forêt restaurée", "Succès reproducteur"]
    group_b = data.loc[data["Habitat"] == "Forêt dégradée", "Succès reproducteur"]
    test = stats.ttest_ind(group_a, group_b, equal_var=False)
    effect = group_a.mean() - group_b.mean()

    with right:
        fig = px.box(data, x="Habitat", y="Succès reproducteur", points="all", color="Habitat")
        fig.update_layout(showlegend=False)
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Différence moyenne", f"{effect:.2f}")
    c2.metric("t de Welch", f"{test.statistic:.2f}")
    c3.metric("p-value", f"{test.pvalue:.3g}")
    conclusion = "statistiquement nette" if test.pvalue < 0.05 else "non concluante au seuil 5 %"
    explain(f"La différence moyenne est de {effect:.2f} jeunes par nid. La p-value vaut {test.pvalue:.3g}, donc la comparaison est {conclusion}.")
    teacher_note("Point de discussion : distinguer taille d'effet, p-value, puissance statistique et importance écologique.", context)
    learning_notes(
        "Une p-value ne mesure pas l'importance biologique de l'effet.",
        "Le test suppose des observations indépendantes et une variable quantitative comparable.",
        "Réduis la taille d'échantillon et observe comment la conclusion devient moins stable.",
    )

    st.download_button("Exporter les données CSV", data.to_csv(index=False).encode("utf-8"), "orni_lab_tests.csv", "text/csv")
    pdf = build_pdf_report(
        "ORNI-LAB - Tests statistiques",
        [f"Différence moyenne = {effect:.2f}. t = {test.statistic:.2f}. p = {test.pvalue:.3g}. Conclusion : {conclusion}."],
    )
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_tests.pdf", "application/pdf")
