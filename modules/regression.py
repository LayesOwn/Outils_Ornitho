from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from core.export import build_pdf_report
from data.examples import wing_mass_dataset
from utils.ui import csv_template_button, explain, learning_notes, module_intro, section, style_figure, teacher_note


def render(context: dict) -> None:
    is_data = context.get("data") is not None
    section(
        "Corrélation et régression",
        None if is_data else "Exemple : relation entre longueur de l'aile et masse corporelle chez des passereaux.",
    )
    module_intro(
        "La corrélation mesure l'intensité d'une relation entre deux variables. La régression estime une équation permettant de prédire une variable à partir d'une autre.",
        "Ces outils servent à tester une relation biologique, quantifier sa force et produire une prédiction avec une incertitude.",
        "En ornithologie, ils permettent d'étudier les liens entre morphologie, condition corporelle, climat, habitat, abondance ou succès reproducteur.",
    )
    left, right = st.columns([0.85, 1.6])

    if context.get("data") is not None:
        import pandas as _pd
        data_src = context["data"]
        numeric_cols = context["numeric_columns"]
        if len(numeric_cols) < 2:
            st.warning("Le fichier doit contenir au moins deux colonnes numériques.")
            return
        with left:
            csv_template_button(
                _pd.DataFrame({"Longueur_aile_mm": [72.1, 75.4, 68.9, 80.2, 71.3], "Masse_g": [18.2, 20.1, 17.4, 22.5, 17.9]}),
                "template_regression.csv",
            )
            x_col = st.selectbox("Variable explicative X", numeric_cols, index=0)
            y_opts = [c for c in numeric_cols if c != x_col]
            y_col = st.selectbox("Variable réponse Y", y_opts, index=0)
        data = data_src[[x_col, y_col]].dropna().rename(columns={x_col: "X", y_col: "Y"})
        data.columns = [x_col, y_col]
    else:
        with left:
            n = st.slider("Nombre d'oiseaux mesurés", 12, 120, 42)
            noise = st.slider("Variabilité individuelle", 0.5, 8.0, 2.4, step=0.1)
            seed = st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=7)
        data = wing_mass_dataset(seed=int(seed), n=n, noise=noise)
        x_col, y_col = "Longueur de l'aile (mm)", "Masse corporelle (g)"

    if len(data) < 3:
        st.warning("Pas assez d'observations valides (minimum 3) pour ajuster une régression.")
        return

    x = data[x_col]
    y = data[y_col]
    if x.std() == 0:
        st.warning(f"La colonne **{x_col}** est constante — régression impossible.")
        return
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    data["Prédiction"] = intercept + slope * x

    with right:
        sorted_data = data.sort_values(x_col)
        fig = go.Figure()
        fig.add_scatter(
            x=data[x_col],
            y=data[y_col],
            mode="markers",
            name="Observations",
            marker={"size": 10, "line": {"width": 1, "color": "#ffffff"}},
        )
        fig.add_scatter(
            x=sorted_data[x_col],
            y=sorted_data["Prédiction"],
            mode="lines",
            name="Régression linéaire",
            line={"width": 3},
        )
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            hovermode="closest",
        )
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("r de Pearson", f"{r_value:.3f}")
    c2.metric("R²", f"{r_value**2:.3f}")
    c3.metric("p-value", f"{p_value:.3g}")

    direction = "positive" if slope > 0 else "négative"
    strength = "forte" if abs(r_value) > 0.7 else "modérée" if abs(r_value) > 0.4 else "faible"
    explain(
        f"La relation est {strength} et {direction} : une unité supplémentaire de {x_col} "
        f"est associée à {slope:.3g} unité de {y_col}. "
        f"Le modèle explique {100 * r_value**2:.1f} % de la variation observée."
    )
    learning_notes(
        "R² indique la proportion de variation expliquée par le modèle linéaire.",
        "Une corrélation ne prouve pas une causalité et peut être influencée par des variables cachées.",
        None if is_data else "Augmente la variabilité individuelle et observe l'effet sur R² et la p-value.",
    )
    teacher_note(
        f"Équation ajustée : {y_col} = {intercept:.3g} + {slope:.3g} × {x_col}. "
        "Faire distinguer corrélation, causalité et qualité prédictive.",
        context,
    )

    with st.expander("Voir les données"):
        st.dataframe(data, use_container_width=True)
    st.download_button("Exporter les données CSV", data.to_csv(index=False).encode("utf-8"), "orni_lab_regression.csv", "text/csv")

    pdf = build_pdf_report(
        "ORNI-LAB - Corrélation et régression",
        [
            f"n = {len(data)}, X = {x_col}, Y = {y_col}.",
            f"Pente = {slope:.3f}, intercept = {intercept:.3f}.",
            f"r = {r_value:.3f}, R2 = {r_value**2:.3f}, p = {p_value:.3g}.",
            f"Interpretation : relation {strength} ({direction}).",
        ],
    )
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_regression.pdf", "application/pdf")
