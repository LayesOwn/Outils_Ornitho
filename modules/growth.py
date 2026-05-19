from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from core.export import build_pdf_report
from utils.ui import explain, learning_notes, module_intro, section, style_figure, teacher_formula, teacher_note, teacher_pitfalls


def _validate_growth_inputs(n0: float, k: float, years: int) -> None:
    if n0 <= 0:
        raise ValueError("n0 must be strictly positive")
    if k <= 0:
        raise ValueError("k must be strictly positive")
    if years < 0:
        raise ValueError("years must be positive or zero")


def simulate_growth(n0: float, r: float, k: float, years: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    _validate_growth_inputs(n0, k, years)
    t = np.arange(years + 1)
    exponential = n0 * np.exp(r * t)

    logistic = np.empty(years + 1, dtype=float)
    logistic[0] = n0
    annual_growth = np.exp(r)
    for year in range(years):
        current = logistic[year]
        logistic[year + 1] = (k * current * annual_growth) / (k + current * (annual_growth - 1))

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
        r = st.slider("Taux intrinsèque r", 0.01, 0.80, 0.18, step=0.01)
        k = st.slider("Capacité de charge K", 50, 100000, 850, step=100)
        years = st.slider("Durée de projection (années)", 5, 80, 35)

    t, exponential, logistic = simulate_growth(n0, r, k, years)
    results = pd.DataFrame({"Année": t, "Exponentiel": exponential, "Logistique": logistic})

    with col_controls:
        st.markdown("**Affichage du graphique**")
        y_scale = st.radio("Échelle verticale", ["Logarithmique", "Linéaire"], horizontal=True)
        y_zoom = st.slider(
            "Zoom vertical",
            1,
            100,
            100,
            help="Réduit la hauteur maximale affichée pour mieux voir les faibles effectifs.",
        )

    fig = go.Figure()
    fig.add_scatter(x=t, y=exponential, name="Exponentiel", mode="lines", line={"width": 3})
    fig.add_scatter(x=t, y=logistic, name="Logistique", mode="lines", line={"width": 3})
    fig.add_hline(y=k, line_dash="dot", annotation_text="K")

    max_displayed = max(float(np.max(exponential)), float(np.max(logistic)), float(k))
    upper_limit = max(1.0, max_displayed * y_zoom / 100)
    if y_scale == "Logarithmique":
        positive_values = np.concatenate([exponential[exponential > 0], logistic[logistic > 0], np.array([k])])
        lower_limit = max(0.1, float(np.min(positive_values)) * 0.8)
        fig.update_yaxes(type="log", range=[np.log10(lower_limit), np.log10(max(upper_limit, lower_limit * 10))])
    else:
        fig.update_yaxes(type="linear", range=[0, upper_limit])

    fig.update_xaxes(rangeslider={"visible": True})
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
    explain(
        f"La population suit une croissance potentielle r = {r:.2f}. "
        f"Le modèle exponentiel atteint {final_exp:,.0f} individus, alors que "
        f"le modèle logistique s'ajuste vers K = {k:,.0f} avec {final_log:,.0f} individus."
    )
    learning_notes(
        "La capacité de charge empêche une croissance illimitée.",
        "Ces modèles ne représentent pas explicitement l'âge, la météo, la dispersion ou les catastrophes.",
        "Diminue K et observe à partir de quand la courbe logistique se stabilise.",
    )

    teacher_note(
        "Relation taux : r (instantané, continu) et λ (discret, annuel) sont liés par r = ln(λ), λ = eʳ. "
        "Le taux r = b − d (natalité − mortalité instantanées). "
        "La croissance logistique atteint son maximum de dN/dt lorsque N = K/2 : "
        "c'est le rendement maximal soutenu MSY = rK/4, concept central en gestion des populations exploitées. "
        "L'effet Allee désigne un mécanisme de rétroaction positive à faible effectif (coopération reproductrice, "
        "détection des prédateurs) : en dessous du seuil A, dN/dt < 0 malgré N > 0, "
        "ce qui crée un risque d'extinction même sans surexploitation.",
        context,
    )
    teacher_formula(
        "Croissance exponentielle et logistique — formes différentielles",
        r"\frac{dN}{dt} = rN \quad\text{(exponentiel)}"
        r"\qquad \frac{dN}{dt} = rN\!\left(1 - \frac{N}{K}\right) \quad\text{(logistique)}",
        context,
    )
    teacher_formula(
        "Rendement maximal soutenu (MSY) — gestion des populations exploitées",
        r"N^* = \frac{K}{2} \;\Rightarrow\; \left.\frac{dN}{dt}\right|_{\max} = \frac{rK}{4} = \text{MSY}",
        context,
    )
    teacher_formula(
        "Effet Allee — modèle logistique avec seuil A",
        r"\frac{dN}{dt} = rN\!\left(1 - \frac{N}{K}\right)\!\left(\frac{N}{A} - 1\right) \quad (A < K)",
        context,
    )
    teacher_pitfalls(
        [
            "Confondre r (taux instantané continu) et λ (taux discret annuel) : r = ln(λ) et λ = eʳ, ils ne sont pas égaux.",
            "Croire que N₀ < K garantit la convergence vers K : si r < 0, la population décline vers 0 quelle que soit la valeur initiale.",
            "Interpréter K comme une constante biologique : K dépend de l'habitat, de la saison et peut évoluer avec le climat.",
            "Confondre MSY (N = K/2) avec l'équilibre K : exploiter jusqu'à K/2 maximise le prélèvement soutenu, pas l'effectif.",
            "Négliger l'effet Allee dans les petites populations fragmentées : le modèle logistique simple prédit une récupération même à N très faible, ce qui surestime la résilience.",
        ],
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
