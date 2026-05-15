from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.optimize import minimize_scalar
from scipy.special import erf, erfinv

from core.export import build_pdf_report
from utils.ui import csv_template_button, explain, learning_notes, module_intro, section, style_figure, teacher_note


def _effective_strip_width(sigma: float, strip_width: float) -> float:
    return float(sigma * np.sqrt(np.pi / 2.0) * erf(strip_width / (sigma * np.sqrt(2.0))))


def fit_half_normal(distances: np.ndarray, strip_width: float) -> dict[str, float]:
    if len(distances) < 2:
        sigma_init = float(np.std(distances)) if len(distances) else strip_width / 2.0
        return {"sigma": round(sigma_init, 1), "esw": round(_effective_strip_width(sigma_init, strip_width), 1), "n": len(distances)}

    def neg_ll(log_sigma: float) -> float:
        sigma = np.exp(log_sigma)
        esw = _effective_strip_width(sigma, strip_width)
        if esw <= 0:
            return 1e10
        return float(len(distances) * np.log(esw) + np.sum(distances ** 2) / (2.0 * sigma ** 2))

    result = minimize_scalar(neg_ll, bounds=(np.log(1e-2), np.log(strip_width * 5.0)), method="bounded")
    sigma_hat = float(np.exp(result.x))
    esw = _effective_strip_width(sigma_hat, strip_width)
    return {"sigma": round(sigma_hat, 1), "esw": round(esw, 1), "n": int(len(distances))}


def simulate_distances(
    true_density: float,
    sigma_true: float,
    strip_width: float,
    transect_length_m: float,
    n_transects: int,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    esw_true = _effective_strip_width(sigma_true, strip_width)
    # Area in ha: 2 * ESW(m) * L(m) * K / 10000
    expected_n = max(1, int(true_density * 2.0 * esw_true * transect_length_m * n_transects / 10000.0))
    n_animals = rng.poisson(expected_n)
    # Sample from truncated half-normal via inverse CDF
    u = rng.uniform(0.0, 1.0, n_animals)
    scale = erf(strip_width / (sigma_true * np.sqrt(2.0)))
    distances = sigma_true * np.sqrt(2.0) * erfinv(u * scale)
    return distances.clip(0.0, strip_width)


def render(context: dict) -> None:
    is_data = context.get("data") is not None
    section("Distance sampling", "Estimer la densité d'oiseaux à partir des distances d'observation.")
    module_intro(
        "Le distance sampling estime la densité animale en modélisant la chute de détection avec la distance à l'observateur.",
        "Il corrige le biais de détection sans visites répétées : la distribution des distances observées révèle la détectabilité.",
        "En ornithologie, il est utilisé pour les transects linéaires et les points fixes pour les espèces chantant peu ou détectées à distance variable.",
    )

    left, right = st.columns([0.9, 1.55])

    if context.get("data") is not None:
        data_src = context["data"]
        numeric_cols = context["numeric_columns"]
        if not numeric_cols:
            st.warning("Le fichier ne contient pas de colonne numérique de distances.")
            return
        with left:
            csv_template_button(
                pd.DataFrame({"Distance_m": [12.4, 45.1, 78.9, 3.2, 120.5, 55.7, 22.0, 88.3]}),
                "template_distance_sampling.csv",
            )
            dist_col = st.selectbox("Colonne distances (m)", numeric_cols)
            strip_width = st.number_input("Demi-largeur W (m)", min_value=1.0, value=200.0, step=10.0)
            transect_length = st.number_input("Longueur totale des transects (m)", min_value=100.0, value=3000.0, step=100.0)
            n_transects = st.number_input("Nombre de transects", min_value=1, value=6)
        raw_distances = data_src[dist_col].dropna().values.astype(float)
        distances = raw_distances[(raw_distances >= 0) & (raw_distances <= strip_width)]
        n_filtered = len(raw_distances) - len(distances)
        if len(raw_distances) > 0 and n_filtered / len(raw_distances) > 0.5:
            st.warning(
                f"{n_filtered}/{len(raw_distances)} distances ({100*n_filtered/len(raw_distances):.0f}%) "
                f"écartées car > W = {strip_width:.0f} m. Vérifiez la valeur de W ou les données."
            )
        true_density = None
    else:
        with left:
            true_density = st.slider("Densité vraie (ind/ha)", 0.5, 20.0, 5.0, step=0.5)
            sigma_true = st.slider("Largeur effective vraie σ (m)", 10, 200, 60)
            strip_width = st.slider("Demi-largeur du transect W (m)", 50, 500, 200)
            transect_length = st.slider("Longueur d'un transect (m)", 200, 2000, 500, step=100)
            n_transects = st.slider("Nombre de transects", 1, 20, 6)
            seed = st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=33)
        distances = simulate_distances(true_density, sigma_true, float(strip_width), float(transect_length), n_transects, int(seed))
    fit = fit_half_normal(distances, float(strip_width))

    area_m2 = 2.0 * fit["esw"] * transect_length * n_transects
    estimated_density = fit["n"] * 10000.0 / area_m2 if area_m2 > 0 else 0.0
    bias_pct = 100.0 * (estimated_density / true_density - 1.0) if true_density > 0 else 0.0

    with right:
        bin_edges = np.linspace(0.0, strip_width, 30)
        hist_vals, _ = np.histogram(distances, bins=bin_edges)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
        scale = float(max(hist_vals)) if max(hist_vals) > 0 else 1.0
        curve_x = np.linspace(0.0, strip_width, 200)
        curve_y = np.exp(-(curve_x ** 2) / (2.0 * fit["sigma"] ** 2)) * scale

        fig = go.Figure()
        fig.add_bar(x=bin_centers, y=hist_vals, name="Distances observées", marker_color="#4dabf7", opacity=0.75)
        fig.add_scatter(
            x=curve_x, y=curve_y,
            mode="lines", name=f"Demi-normale (σ̂ = {fit['sigma']:.0f} m)",
            line={"width": 3, "color": "#39d98a"},
        )
        fig.add_vline(x=fit["esw"], line_dash="dot", annotation_text=f"ESW = {fit['esw']:.0f} m")
        fig.update_layout(xaxis_title="Distance perpendiculaire (m)", yaxis_title="Détections", hovermode="x unified")
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Détections n", f"{fit['n']}")
    c2.metric("σ̂ estimé (m)", f"{fit['sigma']:.0f}", f"Vrai : {sigma_true} m" if true_density else "")
    c3.metric("ESW estimée (m)", f"{fit['esw']:.0f}")
    if true_density:
        c4.metric("Densité estimée", f"{estimated_density:.2f}", f"Vraie : {true_density:.1f} ind/ha")
    else:
        c4.metric("Densité estimée", f"{estimated_density:.2f} ind/ha")

    if true_density:
        explain(
            f"La largeur efficace de bande (ESW = {fit['esw']:.0f} m) est la distance à laquelle un transect "
            f"sans chute de détection détecterait le même nombre d'oiseaux. "
            f"Densité estimée = {estimated_density:.2f} ind/ha (biais : {bias_pct:+.1f} %)."
        )
    else:
        explain(
            f"La largeur efficace de bande estimée est ESW = {fit['esw']:.0f} m. "
            f"Densité estimée = {estimated_density:.2f} ind/ha sur {float(transect_length)*int(n_transects)/1000:.1f} km de transects."
        )
    teacher_note(
        f"ESW = sigma * sqrt(pi/2) * erf(W / (sigma*sqrt(2))). "
        f"D = n / (2 * ESW * L * K) avec L et K en mètres et transects. "
        "En pratique, l'intervalle de confiance sur D est estimé par bootstrap ou delta-méthode.",
        context,
    )
    learning_notes(
        "L'ESW est le cœur du distance sampling : elle convertit des comptages en surface effectivement couverte.",
        "La fonction demi-normale suppose une détection parfaite à distance 0. D'autres fonctions (hazard-rate) peuvent mieux s'ajuster.",
        None if is_data else "Réduis σ à 20 m et W à 100 m : que se passe-t-il sur le nombre de détections et la précision de l'estimation ?",
    )

    dist_df = pd.DataFrame({"Distance_m": distances.round(1)})
    st.download_button(
        "Exporter les distances CSV",
        dist_df.to_csv(index=False).encode("utf-8"),
        "orni_lab_distance.csv",
        "text/csv",
    )
    if is_data:
        pdf_lines = [
            f"Transects = {int(n_transects)}, longueur = {transect_length} m, demi-largeur W = {strip_width} m.",
            f"Detections = {fit['n']}. sigma_estime = {fit['sigma']:.1f} m.",
            f"ESW = {fit['esw']:.1f} m. Densite_estimee = {estimated_density:.2f} ind/ha.",
        ]
    else:
        pdf_lines = [
            f"Transects = {n_transects}, longueur = {transect_length} m, demi-largeur W = {strip_width} m.",
            f"Detections = {fit['n']}. sigma_vrai = {sigma_true} m, sigma_estime = {fit['sigma']:.1f} m.",
            f"ESW = {fit['esw']:.1f} m. Densite_vraie = {true_density:.1f}, Densite_estimee = {estimated_density:.2f} ind/ha.",
            f"Biais estimation = {bias_pct:+.1f} %.",
        ]
    pdf = build_pdf_report("ORNI-LAB - Distance sampling", pdf_lines)
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_distance.pdf", "application/pdf")
