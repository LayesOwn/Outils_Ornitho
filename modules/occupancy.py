from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.optimize import minimize

from core.export import build_pdf_report
from utils.ui import explain, learning_notes, module_intro, section, style_figure, teacher_note


def simulate_detection_history(n_sites: int, n_visits: int, psi: float, p: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    occupied = rng.binomial(1, psi, n_sites).astype(bool)
    history = np.zeros((n_sites, n_visits), dtype=int)
    for i in range(n_sites):
        if occupied[i]:
            history[i] = rng.binomial(1, p, n_visits)
    return history


def fit_occupancy(history: np.ndarray) -> dict[str, float]:
    n_sites, n_visits = history.shape
    detections = history.sum(axis=1)
    naive = float((detections > 0).mean())

    def neg_log_likelihood(params: np.ndarray) -> float:
        psi = 1.0 / (1.0 + np.exp(-params[0]))
        p = 1.0 / (1.0 + np.exp(-params[1]))
        ll = 0.0
        for yi in detections:
            prob = psi * (p ** yi) * ((1.0 - p) ** (n_visits - yi))
            if yi == 0:
                prob += 1.0 - psi
            ll += np.log(max(prob, 1e-300))
        return -ll

    result = minimize(neg_log_likelihood, [0.0, 0.0], method="Nelder-Mead",
                      options={"xatol": 1e-6, "fatol": 1e-6, "maxiter": 5000})
    psi_hat = 1.0 / (1.0 + np.exp(-result.x[0]))
    p_hat = 1.0 / (1.0 + np.exp(-result.x[1]))
    return {"psi": round(psi_hat, 3), "p": round(p_hat, 3), "naive": round(naive, 3)}


def render(context: dict) -> None:
    section("Modèles d'occupation", "Estimer l'occupation réelle quand la détection est imparfaite.")
    module_intro(
        "Un modèle d'occupation estime la probabilité qu'un site soit occupé (ψ) et la probabilité de détecter l'espèce lors d'une visite (p), séparément.",
        "Sans corriger la détectabilité, l'occupation naïve sous-estime l'occupation réelle : une absence d'observation n'est pas une absence de l'espèce.",
        "En ornithologie, c'est fondamental pour les espèces discrètes : pics, rapaces nocturnes, passereaux forestiers ou espèces à faible taux de détection.",
    )

    left, right = st.columns([0.9, 1.55])

    if context.get("data") is not None:
        data_src = context["data"]
        numeric_cols = context["numeric_columns"]
        # Detect binary columns (values 0 or 1 only)
        binary_cols = [c for c in numeric_cols if data_src[c].dropna().isin([0, 1]).all() and data_src[c].notna().sum() >= 5]
        if len(binary_cols) < 2:
            st.warning(
                "Aucune paire de colonnes binaires (0/1) détectée. "
                "Le modèle d'occupation attend une colonne par visite avec 0 = non détecté, 1 = détecté."
            )
            return
        with left:
            visit_cols = st.multiselect(
                "Colonnes de visites (binaires 0/1)",
                binary_cols,
                default=binary_cols[:min(4, len(binary_cols))],
            )
        if len(visit_cols) < 2:
            st.info("Sélectionnez au moins 2 colonnes de visites.")
            return
        history = data_src[visit_cols].dropna().values.astype(int)
        n_visits = len(visit_cols)
        psi_true = None
        p_true = None
    else:
        with left:
            n_sites = st.slider("Nombre de sites", 20, 300, 80)
            n_visits = st.slider("Visites répétées par site", 2, 8, 3)
            psi_true = st.slider("Occupation vraie ψ", 0.05, 0.99, 0.60, step=0.01)
            p_true = st.slider("Détection vraie p", 0.05, 0.99, 0.35, step=0.01)
            seed = st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=55)
        history = simulate_detection_history(n_sites, n_visits, psi_true, p_true, int(seed))

    estimates = fit_occupancy(history)
    naive_theory = psi_true * (1.0 - (1.0 - p_true) ** n_visits) if psi_true is not None else None
    prob_miss = (1.0 - p_true) ** n_visits if p_true is not None else None

    with right:
        labels = ["ψ vraie", "ψ estimée\n(modèle)", "Occupation\nnaïve"]
        values = [psi_true, estimates["psi"], estimates["naive"]]
        colors = ["#39d98a", "#4dabf7", "#ff6b6b"]
        fig = go.Figure()
        fig.add_bar(
            x=labels, y=values,
            marker_color=colors,
            text=[f"{v:.3f}" for v in values],
            textposition="outside",
        )
        fig.update_layout(yaxis_title="Probabilité d'occupation", yaxis_range=[0, 1.15], showlegend=False)
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("ψ estimée", f"{estimates['psi']:.3f}", f"Vraie : {psi_true:.3f}" if psi_true else "")
    c2.metric("p estimée", f"{estimates['p']:.3f}", f"Vraie : {p_true:.3f}" if p_true else "")
    bias = estimates["naive"] - estimates["psi"]
    c3.metric("Biais occupation naïve", f"{bias:+.3f}")

    if psi_true is not None:
        explain(
            f"L'occupation naïve ({estimates['naive']:.3f}) sous-estime ψ de {abs(estimates['naive'] - psi_true):.3f}. "
            f"Avec p = {p_true:.2f} et {n_visits} visites, la probabilité de manquer l'espèce sur un site occupé est "
            f"{prob_miss:.3f}. "
            f"La correction théorique donne une occupation naïve attendue de {naive_theory:.3f}."
        )
    else:
        explain(
            f"Occupation naïve (proportion de sites avec ≥1 détection) = {estimates['naive']:.3f}. "
            f"Le modèle corrige pour la détectabilité et estime ψ = {estimates['psi']:.3f}, p = {estimates['p']:.3f}."
        )

    with st.expander("Historique de détection (30 premiers sites)"):
        n_show = min(30, n_sites)
        hist_df = pd.DataFrame(
            history[:n_show],
            columns=[f"V{v + 1}" for v in range(n_visits)],
            index=[f"S{i + 1}" for i in range(n_show)],
        )
        st.dataframe(hist_df, use_container_width=True)

    teacher_note(
        (
            f"Occupation naïve théorique = psi × (1 − (1−p)^K) = "
            f"{psi_true:.2f} × (1 − {1 - p_true:.2f}^{n_visits}) = {naive_theory:.3f}. "
            if psi_true is not None else ""
        ) + "Le modèle maximise la vraisemblance en estimant psi et p simultanément (logit-link, Nelder-Mead).",
        context,
    )
    learning_notes(
        "Plus p est faible ou K est petit, plus le biais de l'occupation naïve est grand.",
        "Le modèle suppose une population fermée entre visites et une détection indépendante d'un site à l'autre.",
        "Réduis le nombre de visites à 1 : le modèle peut-il encore distinguer ψ de p ?",
    )

    pdf = build_pdf_report(
        "ORNI-LAB - Modèles d'occupation",
        [
            f"Sites = {n_sites}, visites = {n_visits}.",
            f"Parametres vrais : psi = {psi_true:.3f}, p = {p_true:.3f}.",
            f"Estimations : psi = {estimates['psi']:.3f}, p = {estimates['p']:.3f}.",
            f"Occupation naive = {estimates['naive']:.3f} (biais = {bias:+.3f}).",
        ],
    )
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_occupation.pdf", "application/pdf")
