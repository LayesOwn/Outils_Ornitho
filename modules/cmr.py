from __future__ import annotations

import math

import plotly.graph_objects as go
import streamlit as st

from core.export import build_pdf_report
from data.examples import CMR_SCENARIOS
from utils.ui import explain, learning_notes, module_intro, section, style_figure, teacher_formula, teacher_note, teacher_pitfalls


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
    module_intro(
        "La capture-marquage-recapture estime la taille d'une population à partir du nombre d'individus marqués puis retrouvés lors d'une seconde capture.",
        "Elle est utilisée quand il est impossible de compter tous les individus directement, notamment dans des populations mobiles ou partiellement détectables.",
        "Pour les oiseaux, elle sert à estimer l'abondance, la survie apparente, la fidélité au site et la dynamique de populations baguées.",
    )
    scenario_name = st.selectbox("Exemple ornithologique", list(CMR_SCENARIOS.keys()))
    scenario = CMR_SCENARIOS[scenario_name]

    col1, col2 = st.columns([0.8, 1.4])
    with col1:
        marked = st.slider("Individus marqués M", 10, 1000, scenario["marked"])
        captured = st.slider("Individus capturés C", 10, 1000, scenario["captured"])
        recaptured = st.slider("Marqués recapturés R", 1, min(marked, captured), min(scenario["recaptured"], min(marked, captured)))

    estimate, low, high = lincoln_petersen(marked, captured, recaptured)
    with col2:
        fig = go.Figure()
        fig.add_bar(
            x=["M", "C", "R", "N estimé"],
            y=[marked, captured, recaptured, estimate],
            marker_color=["#39d98a", "#4dabf7", "#ff6b6b", "#ffd166"],
        )
        fig.add_trace(
            go.Scatter(
                x=["N estimé", "N estimé"],
                y=[low, high],
                mode="lines+markers",
                name="IC 95 %",
            )
        )
        fig.update_layout(yaxis_title="Nombre d'individus", showlegend=True)
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    recapture_rate = recaptured / captured
    st.metric("Abondance estimée", f"{estimate:,.0f}", f"IC95 % [{low:,.0f} ; {high:,.0f}]")
    explain(
        f"Le taux de recapture est de {100 * recapture_rate:.1f} %. "
        f"Un faible nombre de recaptures élargit l'incertitude et peut rendre l'estimation instable."
    )
    learning_notes(
        "Plus le taux de recapture est élevé, plus l'estimation est précise.",
        "La méthode est sensible à la perte de marques, aux migrations et aux captures non homogènes.",
        "Diminue R et observe comment l'intervalle de confiance s'élargit.",
    )
    teacher_note(
        "Quatre hypothèses du Lincoln-Petersen : (1) population fermée entre les deux sessions, "
        "(2) mélange homogène des individus marqués dans la population, "
        "(3) marques non perdues, non déposées, détectables, "
        "(4) probabilités de capture identiques pour tous les individus (pas de hétérogénéité). "
        "La correction de Chapman est recommandée quand R < 7 : elle est sans biais alors que l'estimateur original est biaisé positivement. "
        "En population ouverte (sessions multiples), le modèle CJS estime la survie apparente φᵢ et la probabilité de recapture pᵢ. "
        "Jolly-Seber ajoute l'estimation de la taille de population. "
        "Le robust design de Pollock combine des sessions primaires (population ouverte) "
        "et des sessions secondaires rapprochées (population fermée) pour estimer φ, p, et N simultanément.",
        context,
    )
    teacher_formula(
        "Estimateurs Lincoln-Petersen et Chapman (Chap. 6, ORNI 422)",
        r"\hat{N} = \frac{M \cdot C}{R} \quad\text{(LP original)}"
        r"\qquad \hat{N}_C = \frac{(M+1)(C+1)}{R+1} - 1 \quad\text{(Chapman, sans biais)}",
        context,
    )
    teacher_formula(
        "Variance et intervalle de confiance de Chapman",
        r"\widehat{\mathrm{Var}}(\hat{N}_C) = \frac{(M+1)(C+1)(M-R)(C-R)}{(R+1)^2\,(R+2)}"
        r"\qquad \mathrm{IC}_{95\%} = \hat{N}_C \pm 1{,}96\,\hat{\sigma}",
        context,
    )
    teacher_pitfalls(
        [
            "Appliquer Lincoln-Petersen sur une population ouverte : si des individus naissent, meurent ou migrent entre M et C, N est surestimé.",
            "Ignorer la perte de bagues : si des bagues tombent entre les sessions, R est sous-estimé et N surestimé.",
            "Confondre φ (survie apparente CJS) et la survie vraie : φ = survie × fidélité au site — la dispersion est confondue avec la mortalité.",
            "Utiliser l'estimateur LP original quand R < 7 sans correction Chapman : biais positif important.",
            "Croire que le taux de recapture observé (R/C) est la probabilité de recapture p : ils coïncident seulement si toutes les hypothèses sont vérifiées.",
        ],
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
