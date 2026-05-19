from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy.integrate import solve_ivp

from core.export import build_pdf_report
from utils.ui import explain, learning_notes, module_intro, section, style_figure, teacher_formula, teacher_note, teacher_pitfalls


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
    module_intro(
        "Le modèle de Lotka-Volterra décrit les interactions cycliques entre une population de proies et une population de prédateurs.",
        "Il sert à comprendre comment la prédation peut produire des oscillations, des retards de réponse et des équilibres dynamiques.",
        "En ornithologie, il aide à explorer les relations entre oiseaux proies et rapaces, ou entre oiseaux insectivores et ressources alimentaires saisonnières.",
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
    results = pd.DataFrame({"Temps": t, "Proies": prey, "Prédateurs": predator})

    with right:
        fig = go.Figure()
        fig.add_scatter(x=t, y=prey, name="Proies", mode="lines", line={"width": 3})
        fig.add_scatter(x=t, y=predator, name="Prédateurs", mode="lines", line={"width": 3})
        fig.update_layout(xaxis_title="Temps", yaxis_title="Effectif", hovermode="x unified")
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    phase = px.line(x=prey, y=predator, labels={"x": "Proies", "y": "Prédateurs"}, title="Portrait de phase")
    phase.update_traces(line={"width": 3})
    style_figure(phase)
    st.plotly_chart(phase, use_container_width=True)

    prey_eq = gamma / delta
    predator_eq = alpha / beta
    explain(
        f"L'équilibre théorique se situe autour de {prey_eq:.0f} proies et {predator_eq:.0f} prédateurs. "
        "Les oscillations montrent un décalage temporel : les prédateurs augmentent après les proies."
    )
    learning_notes(
        "Les interactions proie-prédateur peuvent créer des cycles avec retard temporel.",
        "Le modèle ne contient ni saisonnalité, ni capacité de charge, ni comportements de refuge.",
        "Augmente la mortalité des prédateurs et observe l'effet sur l'amplitude des cycles.",
    )
    teacher_note(
        "Notation ORNI 422 : α = croissance intrinsèque des proies, a = taux de prédation (β dans le code), "
        "e = efficacité de conversion (δ), m = mortalité des prédateurs (γ). "
        "L'isocline nulle proie (dN/dt = 0) donne P = r/a — droite horizontale dans le plan (N, P). "
        "L'isocline nulle prédateur (dP/dt = 0) donne N = m/(ea) — droite verticale. "
        "Leur intersection est l'équilibre, qui est un centre conservatif (oscillations permanentes sans amortissement). "
        "La réponse fonctionnelle de Holling décrit le comportement de chasse : "
        "Type I (linéaire, pas de satiation), Type II (hyperbolique, satiation), Type III (sigmoïde, apprentissage). "
        "En ornithologie : Type II est la plus commune chez les rapaces spécialistes.",
        context,
    )
    teacher_formula(
        "Système de Lotka-Volterra (Chap. 5, ORNI 422)",
        r"\frac{dN}{dt} = rN - aNP \qquad \frac{dP}{dt} = -mP + eaNP",
        context,
    )
    teacher_formula(
        "Équilibre — intersection des isoclines nulles",
        r"N^* = \frac{m}{e\,a} \qquad P^* = \frac{r}{a}",
        context,
    )
    teacher_formula(
        "Réponses fonctionnelles de Holling",
        r"f_{\mathrm{I}}(N)= aN \qquad"
        r"f_{\mathrm{II}}(N)= \frac{aN}{1+ahN} \qquad"
        r"f_{\mathrm{III}}(N)= \frac{aN^2}{1+ahN^2}",
        context,
    )
    teacher_pitfalls(
        [
            "Confondre les paramètres : dans ce module, α = croissance proie, β = taux de prédation — "
            "la notation varie selon les manuels (parfois r, a, e, m).",
            "Croire que l'équilibre LV classique est stable : c'est un centre conservatif — une perturbation produit une nouvelle orbite fermée, pas un retour au point fixe.",
            "Ignorer l'absence de capacité de charge pour les proies : sans K, les proies peuvent croître indéfiniment si le prédateur disparaît.",
            "Confondre réponse fonctionnelle (f(N), comportement individuel du prédateur) et réponse numérique (changement d'effectif du prédateur).",
            "Interpréter le portrait de phase comme une spirale convergente : c'est une ellipse fermée (conservatif), pas un attracteur.",
        ],
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
    st.download_button("Exporter les données CSV", results.to_csv(index=False).encode("utf-8"), "orni_lab_lotka_volterra.csv", "text/csv")
