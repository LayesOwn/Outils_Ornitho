from __future__ import annotations

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy.integrate import solve_ivp

from core.export import build_pdf_report
from utils.ui import explain, section, teacher_note


def lotka_volterra_system(_t: float, state: list[float], alpha: float, beta: float, delta: float, gamma: float) -> list[float]:
    prey, predator = state
    return [
        alpha * prey - beta * prey * predator,
        delta * prey * predator - gamma * predator,
    ]


def simulate(
    prey0: float,
    predator0: float,
    alpha: float,
    beta: float,
    delta: float,
    gamma: float,
    duration: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    t_eval = np.linspace(0, duration, duration * 10 + 1)
    solution = solve_ivp(
        lotka_volterra_system,
        (0, duration),
        [prey0, predator0],
        args=(alpha, beta, delta, gamma),
        t_eval=t_eval,
        max_step=0.2,
    )
    return solution.t, solution.y[0], solution.y[1]


def render(context: dict) -> None:
    section(
        "Lotka-Volterra",
        "Exemple : petits passereaux granivores et rapaces spécialisés dans une mosaïque agricole.",
    )
    left, right = st.columns([0.85, 1.55])
    with left:
        prey0 = st.slider("Proies initiales", 10, 1000, 320)
        predator0 = st.slider("Prédateurs initiaux", 1, 200, 38)
        alpha = st.slider("Croissance des proies α", 0.01, 1.20, 0.42, step=0.01)
        beta = st.slider("Prédation β", 0.0001, 0.0200, 0.0040, step=0.0001, format="%.4f")
        delta = st.slider("Conversion δ", 0.0001, 0.0200, 0.0018, step=0.0001, format="%.4f")
        gamma = st.slider("Mortalité prédateurs γ", 0.01, 1.20, 0.36, step=0.01)
        duration = st.slider("Durée", 10, 120, 55)

    t, prey, predator = simulate(prey0, predator0, alpha, beta, delta, gamma, duration)

    with right:
        fig = go.Figure()
        fig.add_scatter(x=t, y=prey, name="Proies", mode="lines")
        fig.add_scatter(x=t, y=predator, name="Prédateurs", mode="lines")
        fig.update_layout(xaxis_title="Temps", yaxis_title="Effectif", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    phase = px.line(x=prey, y=predator, labels={"x": "Proies", "y": "Prédateurs"}, title="Portrait de phase")
    st.plotly_chart(phase, use_container_width=True)

    prey_eq = gamma / delta
    predator_eq = alpha / beta
    explain(
        f"L'équilibre théorique se situe autour de {prey_eq:.0f} proies et {predator_eq:.0f} prédateurs. "
        "Les oscillations montrent un décalage temporel : les prédateurs augmentent après les proies."
    )
    teacher_note(
        "Le modèle est volontairement simple : il ne contient ni capacité de charge, ni saisonnalité, "
        "ni refuge spatial. Ces extensions sont pertinentes pour un futur module avancé.",
        context,
    )

    pdf = build_pdf_report(
        "ORNI-LAB - Lotka-Volterra",
        [
            f"Conditions initiales : proies = {prey0}, prédateurs = {predator0}.",
            f"Paramètres : alpha={alpha:.2f}, beta={beta:.4f}, delta={delta:.4f}, gamma={gamma:.2f}.",
            f"Equilibre théorique : proies={prey_eq:.0f}, prédateurs={predator_eq:.0f}.",
            "Interprétation : dynamique cyclique avec réponse retardée du prédateur.",
        ],
    )
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_lotka_volterra.pdf", "application/pdf")
