from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from core.export import build_pdf_report
from data.examples import default_leslie_values
from utils.ui import explain, section, teacher_note


def build_leslie_matrix(fecundity: list[float], survival: list[float]) -> np.ndarray:
    matrix = np.zeros((len(fecundity), len(fecundity)))
    matrix[0, :] = fecundity
    for i, s in enumerate(survival, start=1):
        matrix[i, i - 1] = s
    return matrix


def project_population(matrix: np.ndarray, initial: np.ndarray, years: int) -> pd.DataFrame:
    values = [initial]
    for _ in range(years):
        values.append(matrix @ values[-1])
    frame = pd.DataFrame(values, columns=["Juvéniles", "1 an", "2 ans", "3 ans et +"])
    frame.insert(0, "Année", np.arange(years + 1))
    frame["Total"] = frame.drop(columns="Année").sum(axis=1)
    return frame


def render(context: dict) -> None:
    section(
        "Matrices de Leslie",
        "Exemple : projection d'une population femelle structurée par âge.",
    )
    fecundity, survival, initial = default_leslie_values()
    left, right = st.columns([1, 1.5])

    with left:
        years = st.slider("Durée de projection", 5, 60, 25)
        st.markdown("**Fécondités par classe**")
        fecundity = [
            st.number_input(f"F{i}", min_value=0.0, max_value=5.0, value=float(v), step=0.05)
            for i, v in enumerate(fecundity)
        ]
        st.markdown("**Survies entre classes**")
        survival = [
            st.slider(f"S{i}→{i+1}", 0.0, 1.0, float(v), step=0.01)
            for i, v in enumerate(survival)
        ]

    matrix = build_leslie_matrix(fecundity, survival)
    projection = project_population(matrix, np.array(initial, dtype=float), years)
    eigenvalues = np.linalg.eigvals(matrix)
    lambda_dom = float(np.max(eigenvalues.real))

    with right:
        st.dataframe(pd.DataFrame(matrix).round(3), use_container_width=True)
        fig = px.line(
            projection,
            x="Année",
            y=["Juvéniles", "1 an", "2 ans", "3 ans et +", "Total"],
            labels={"value": "Effectif", "variable": "Classe"},
        )
        st.plotly_chart(fig, use_container_width=True)

    trend = "croissante" if lambda_dom > 1 else "déclinante" if lambda_dom < 1 else "stable"
    explain(
        f"La valeur propre dominante λ = {lambda_dom:.3f}. "
        f"La population projetée est donc {trend} à long terme."
    )
    teacher_note(
        "Discussion : λ résume la croissance asymptotique, mais la trajectoire initiale dépend fortement "
        "de la structure d'âge de départ.",
        context,
    )

    pdf = build_pdf_report(
        "ORNI-LAB - Matrice de Leslie",
        [
            f"Fécondités : {fecundity}.",
            f"Survies : {survival}.",
            f"Lambda dominant : {lambda_dom:.3f}.",
            f"Diagnostic : population {trend}.",
        ],
    )
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_leslie.pdf", "application/pdf")
