from __future__ import annotations

import math

import plotly.graph_objects as go
import streamlit as st

from core.export import build_pdf_report
from data.examples import CMR_SCENARIOS
from utils.ui import explain, section, teacher_note


def lincoln_petersen(marked: int, captured: int, recaptured: int) -> tuple[float, float, float]:
    estimate = ((marked + 1) * (captured + 1) / (recaptured + 1)) - 1
    variance = (
        (marked + 1)
        * (captured + 1)
        * (marked - recaptured)
        * (captured - recaptured)
        / (((recaptured + 1) ** 2) * (recaptured + 2))
    )
    se = math.sqrt(max(variance, 0))
    return estimate, max(0, estimate - 1.96 * se), estimate + 1.96 * se


def render(context: dict) -> None:
    section(
        "Capture-Marquage-Recapture",
        "Estimateur de Lincoln-Petersen avec correction de Chapman.",
    )
    scenario_name = st.selectbox("Exemple ornithologique", list(CMR_SCENARIOS.keys()))
    scenario = CMR_SCENARIOS[scenario_name]

    col1, col2 = st.columns([0.8, 1.4])
    with col1:
        marked = st.slider("Individus marqués M", 10, 1000, scenario["marked"])
        captured = st.slider("Individus capturés C", 10, 1000, scenario["captured"])
        recaptured = st.slider("Marqués recapturés R", 1, min(marked, captured), scenario["recaptured"])

    estimate, low, high = lincoln_petersen(marked, captured, recaptured)
    with col2:
        fig = go.Figure()
        fig.add_bar(x=["M", "C", "R", "N estimé"], y=[marked, captured, recaptured, estimate])
        fig.add_trace(
            go.Scatter(
                x=["N estimé", "N estimé"],
                y=[low, high],
                mode="lines+markers",
                name="IC 95 %",
            )
        )
        fig.update_layout(yaxis_title="Nombre d'individus", showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    recapture_rate = recaptured / captured
    st.metric("Abondance estimée", f"{estimate:,.0f}", f"IC95 % [{low:,.0f} ; {high:,.0f}]")
    explain(
        f"Le taux de recapture est de {100 * recapture_rate:.1f} %. "
        f"Un faible nombre de recaptures élargit l'incertitude et peut rendre l'estimation instable."
    )
    teacher_note(
        "Hypothèses clés : population fermée, mélange homogène, marques non perdues, probabilités de capture similaires.",
        context,
    )

    pdf = build_pdf_report(
        "ORNI-LAB - Capture-Marquage-Recapture",
        [
            f"Scénario : {scenario_name}.",
            f"M = {marked}, C = {captured}, R = {recaptured}.",
            f"N estimé = {estimate:.0f}, IC95 % = [{low:.0f}; {high:.0f}].",
            "Interprétation : la précision dépend fortement du taux de recapture.",
        ],
    )
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_cmr.pdf", "application/pdf")
