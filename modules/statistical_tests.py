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

    if context.get("data") is not None:
        data_src = context["data"]
        numeric_cols = context["numeric_columns"]
        cat_cols = context["categorical_columns"]
        if not numeric_cols or not cat_cols:
            st.warning("Le fichier doit contenir au moins une colonne numérique et une colonne catégorielle.")
            return
        with left:
            value_col = st.selectbox("Variable numérique à comparer", numeric_cols)
            group_col = st.selectbox("Variable de groupe (2 modalités)", cat_cols)
        sub = data_src[[group_col, value_col]].dropna()
        groups = sub[group_col].unique()
        if len(groups) != 2:
            st.warning(f"La colonne **{group_col}** contient {len(groups)} modalité(s). Exactement 2 sont requises.")
            return
        group_a = sub.loc[sub[group_col] == groups[0], value_col]
        group_b = sub.loc[sub[group_col] == groups[1], value_col]
        data = sub.rename(columns={group_col: "Groupe", value_col: "Valeur"})
        hab_label, val_label = "Groupe", "Valeur"
    else:
        with left:
            n_a = st.slider("Nids en forêt restaurée", 8, 120, 36)
            n_b = st.slider("Nids en forêt dégradée", 8, 120, 34)
            mean_a = st.slider("Moyenne restaurée", 0.0, 6.0, 3.2, step=0.1)
            mean_b = st.slider("Moyenne dégradée", 0.0, 6.0, 2.4, step=0.1)
            sd = st.slider("Variabilité entre nids", 0.2, 3.0, 1.1, step=0.1)
            seed = st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=33)
        data = generate_two_groups(int(seed), n_a, n_b, mean_a, mean_b, sd)
        data = data.rename(columns={"Habitat": "Groupe", "Succès reproducteur": "Valeur"})
        groups = data["Groupe"].unique()
        group_a = data.loc[data["Groupe"] == groups[0], "Valeur"]
        group_b = data.loc[data["Groupe"] == groups[1], "Valeur"]
        hab_label, val_label = "Groupe", "Valeur"

    test = stats.ttest_ind(group_a, group_b, equal_var=False)
    effect = float(group_a.mean() - group_b.mean())

    with right:
        fig = px.box(data, x="Groupe", y="Valeur", points="all", color="Groupe")
        fig.update_layout(showlegend=False)
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Différence moyenne", f"{effect:.2f}")
    c2.metric("t de Welch", f"{test.statistic:.2f}")
    c3.metric("p-value", f"{test.pvalue:.3g}")
    conclusion = "statistiquement nette" if test.pvalue < 0.05 else "non concluante au seuil 5 %"
    g0, g1 = str(groups[0]), str(groups[1])
    explain(
        f"Différence moyenne ({g0} vs {g1}) : {effect:.3g}. "
        f"p-value = {test.pvalue:.3g} → comparaison {conclusion}."
    )
    teacher_note("Point de discussion : distinguer taille d'effet, p-value, puissance statistique et importance écologique.", context)
    learning_notes(
        "Une p-value ne mesure pas l'importance biologique de l'effet.",
        "Le test suppose des observations indépendantes et une variable quantitative comparable.",
        "Réduis la taille d'échantillon et observe comment la conclusion devient moins stable.",
    )

    st.download_button("Exporter les données CSV", data.to_csv(index=False).encode("utf-8"), "orni_lab_tests.csv", "text/csv")
    pdf = build_pdf_report(
        "ORNI-LAB - Tests statistiques",
        [
            f"Groupes : {g0} (n={len(group_a)}) vs {g1} (n={len(group_b)}).",
            f"Difference moyenne = {effect:.3g}. t = {test.statistic:.3f}. p = {test.pvalue:.3g}. Conclusion : {conclusion}.",
        ],
    )
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_tests.pdf", "application/pdf")
