from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from core.export import build_pdf_report
from data.examples import wing_mass_dataset
from utils.ui import explain, section, teacher_note


def render(context: dict) -> None:
    section(
        "Corrélation et régression",
        "Exemple : relation entre longueur de l'aile et masse corporelle chez des passereaux.",
    )
    left, right = st.columns([0.85, 1.6])
    with left:
        n = st.slider("Nombre d'oiseaux mesurés", 12, 120, 42)
        noise = st.slider("Variabilité individuelle", 0.5, 8.0, 2.4, step=0.1)
        seed = st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=7)

    data = wing_mass_dataset(seed=int(seed), n=n)
    rng = np.random.default_rng(int(seed) + 11)
    data["Masse corporelle (g)"] = (
        0.42 * data["Longueur de l'aile (mm)"] - 12 + rng.normal(0, noise, n)
    ).round(1)

    x = data["Longueur de l'aile (mm)"]
    y = data["Masse corporelle (g)"]
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    data["Prédiction"] = intercept + slope * x

    with right:
        sorted_data = data.sort_values("Longueur de l'aile (mm)")
        fig = go.Figure()
        fig.add_scatter(
            x=data["Longueur de l'aile (mm)"],
            y=data["Masse corporelle (g)"],
            mode="markers",
            name="Observations",
            text=[f"Prédiction : {value:.1f} g" for value in data["Prédiction"]],
            hovertemplate="Aile: %{x:.1f} mm<br>Masse: %{y:.1f} g<br>%{text}<extra></extra>",
        )
        fig.add_scatter(
            x=sorted_data["Longueur de l'aile (mm)"],
            y=sorted_data["Prédiction"],
            mode="lines",
            name="Régression linéaire",
        )
        fig.update_layout(
            xaxis_title="Longueur de l'aile (mm)",
            yaxis_title="Masse corporelle (g)",
            hovermode="closest",
        )
        st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("r de Pearson", f"{r_value:.3f}")
    c2.metric("R²", f"{r_value**2:.3f}")
    c3.metric("p-value", f"{p_value:.3g}")

    strength = "forte" if abs(r_value) > 0.7 else "modérée" if abs(r_value) > 0.4 else "faible"
    explain(
        f"La relation est {strength} et positive : chaque millimètre d'aile supplémentaire "
        f"est associé à environ {slope:.2f} g de masse en plus. "
        f"Le modèle explique {100 * r_value**2:.1f} % de la variation observée."
    )
    teacher_note(
        f"Équation ajustée : masse = {intercept:.2f} + {slope:.2f} × aile. "
        "Faire distinguer corrélation, causalité et qualité prédictive.",
        context,
    )

    with st.expander("Voir les données"):
        st.dataframe(data, use_container_width=True)

    pdf = build_pdf_report(
        "ORNI-LAB - Corrélation et régression",
        [
            f"n = {n}, pente = {slope:.3f}, intercept = {intercept:.3f}.",
            f"r = {r_value:.3f}, R2 = {r_value**2:.3f}, p = {p_value:.3g}.",
            f"Interprétation : relation {strength} entre aile et masse.",
        ],
    )
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_regression.pdf", "application/pdf")
