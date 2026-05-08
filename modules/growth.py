from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import sympy as sp

from core.export import build_pdf_report
from utils.ui import explain, learning_notes, module_intro, section, style_figure, teacher_note


def simulate_growth(n0: float, r: float, k: float, years: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    t = np.arange(years + 1)
    exponential = n0 * np.exp(r * t)
    logistic = k / (1 + ((k - n0) / n0) * np.exp(-r * t))
    return t, exponential, logistic


def render(context: dict) -> None:
    section(
        "Croissance exponentielle et logistique",
        "Exemple : colonie nicheuse suivie pendant plusieurs saisons de reproduction.",
    )
    module_intro(
        "Ces modèles décrivent comment l'effectif d'une population varie au cours du temps. "
        "Le modèle exponentiel suppose une croissance sans limite, alors que le modèle logistique ajoute une capacité de charge K.",
        "Ils servent à comparer des scénarios simples de croissance, de déclin ou de stabilisation et à comprendre le rôle de la densité-dépendance.",
        "En ornithologie, ils aident à interpréter l'évolution d'une colonie, l'effet d'un habitat limité ou le potentiel de récupération après une perturbation.",
    )
    col_controls, col_plot = st.columns([0.9, 1.6])

    with col_controls:
        n0 = st.slider("Population initiale N₀", 5, 2000, 120, step=5)
        r = st.slider("Taux intrinsèque r", -0.30, 0.80, 0.18, step=0.01)
        k = st.slider("Capacité de charge K", 50, 5000, 850, step=25)
        years = st.slider("Durée de projection (années)", 5, 80, 35)

    t, exponential, logistic = simulate_growth(n0, r, k, years)
    results = pd.DataFrame({"Année": t, "Exponentiel": exponential, "Logistique": logistic})
    fig = go.Figure()
    fig.add_scatter(x=t, y=exponential, name="Exponentiel", mode="lines", line={"width": 3})
    fig.add_scatter(x=t, y=logistic, name="Logistique", mode="lines", line={"width": 3})
    fig.add_hline(y=k, line_dash="dot", annotation_text="K")
    fig.update_layout(
        xaxis_title="Années",
        yaxis_title="Effectif projeté",
        hovermode="x unified",
        legend_title="Modèle",
    )
    style_figure(fig)

    with col_plot:
        st.plotly_chart(fig, use_container_width=True)

    final_exp = float(exponential[-1])
    final_log = float(logistic[-1])
    growth_state = "augmente" if r > 0 else "diminue"
    explain(
        f"La population {growth_state} avec r = {r:.2f}. "
        f"Le modèle exponentiel atteint {final_exp:,.0f} individus, alors que "
        f"le modèle logistique se stabilise vers K = {k:,.0f} avec {final_log:,.0f} individus."
    )
    learning_notes(
        "La capacité de charge empêche une croissance illimitée.",
        "Ces modèles ne représentent pas explicitement l'âge, la météo, la dispersion ou les catastrophes.",
        "Diminue K et observe à partir de quand la courbe logistique se stabilise.",
    )

    n_sym, r_sym, k_sym = sp.symbols("N r K")
    teacher_note(
        f"Équations : exponentiel N(t)=N0·exp(rt) ; logistique "
        f"N(t)=K/(1+((K-N0)/N0)·exp(-rt)). "
        f"Forme différentielle : dN/dt = {r_sym * n_sym * (1 - n_sym / k_sym)}.",
        context,
    )

    pdf = build_pdf_report(
        "ORNI-LAB - Croissance",
        [
            f"N0 = {n0}, r = {r:.2f}, K = {k}, horizon = {years} ans.",
            f"Effectif final exponentiel : {final_exp:.0f}.",
            f"Effectif final logistique : {final_log:.0f}.",
            "Interprétation : la densité-dépendance limite la croissance lorsque l'effectif approche K.",
        ],
    )
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_croissance.pdf", "application/pdf")
    st.download_button("Exporter les données CSV", results.to_csv(index=False).encode("utf-8"), "orni_lab_croissance.csv", "text/csv")
