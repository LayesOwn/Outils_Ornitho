from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.optimize import minimize

from core.export import build_pdf_report
from utils.ui import (
    csv_template_button,
    data_incompatible,
    explain,
    learning_notes,
    module_intro,
    section,
    style_figure,
    teacher_formula,
    teacher_note,
    teacher_objectives,
    teacher_pitfalls,
    teacher_summary,
)


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
    # Flag extreme logit values (|logit| > 4.5 ≈ p < 0.01 or p > 0.99)
    converged_extreme = abs(result.x[0]) > 4.5 or abs(result.x[1]) > 4.5
    return {
        "psi": round(psi_hat, 3),
        "p": round(p_hat, 3),
        "naive": round(naive, 3),
        "converged_extreme": converged_extreme,
        "converged": bool(result.success),
    }


def render(context: dict) -> None:
    section("Modèles d'occupation", "Estimer l'occupation réelle quand la détection est imparfaite.")
    module_intro(
        "Un modèle d'occupation estime la probabilité qu'un site soit occupé (ψ) et la probabilité de détecter l'espèce lors d'une visite (p), séparément.",
        "Sans corriger la détectabilité, l'occupation naïve sous-estime l'occupation réelle : une absence d'observation n'est pas une absence de l'espèce.",
        "En ornithologie, c'est fondamental pour les espèces discrètes : pics, rapaces nocturnes, passereaux forestiers ou espèces à faible taux de détection.",
    )
    teacher_objectives(
        [
            "Comprendre que « non détecté » ≠ « absent » : la détection est imparfaite (p < 1).",
            "Séparer la probabilité d'occupation ψ de la probabilité de détection p grâce aux visites répétées.",
            "Mesurer le biais de l'occupation naïve (proportion de sites où l'espèce a été vue) et son lien avec p et le nombre de visites K.",
            "Savoir qu'il faut ≥ 3 visites quand p est faible pour que le modèle soit identifiable.",
        ],
        context,
    )

    left, right = st.columns([0.9, 1.55])

    if context.get("data") is not None:
        data_src = context["data"]
        numeric_cols = context["numeric_columns"]
        # Detect binary columns (values 0 or 1 only)
        binary_cols = [c for c in numeric_cols if data_src[c].dropna().isin([0, 1]).all() and data_src[c].notna().sum() >= 5]
        if len(binary_cols) < 2:
            data_incompatible(
                "Le modèle d'occupation nécessite au moins 2 colonnes binaires (valeurs 0/1 uniquement), une par visite de terrain : 0 = espèce non détectée, 1 = espèce détectée.",
                [
                    "Vérifiez que votre fichier contient bien des colonnes de présence/absence encodées en 0 et 1.",
                    "Si vos données sont au format long (une ligne par observation), pivotez d'abord le tableau pour obtenir une colonne par visite.",
                    "Les colonnes avec uniquement des 0 ou des 1 mais moins de 5 données valides sont exclues — vérifiez les valeurs manquantes.",
                    "Téléchargez l'exemple CSV (colonnes V1, V2, V3…) pour voir la structure attendue.",
                ],
            )
            return
        with left:
            csv_template_button(
                pd.DataFrame({"Site": ["S01", "S02", "S03", "S04", "S05"], "V1": [1, 0, 1, 0, 1], "V2": [1, 0, 0, 1, 1], "V3": [0, 0, 1, 0, 1]}),
                "template_occupation.csv",
            )
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
            seed = int(st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=55) or 55)
        history = simulate_detection_history(n_sites, n_visits, psi_true, p_true, int(seed))

    with st.spinner("Ajustement du modèle d'occupation…"):
        estimates = fit_occupancy(history)
    if estimates.get("converged_extreme"):
        st.warning(
            "⚠ Le modèle a convergé vers des valeurs extrêmes (ψ ou p proche de 0 ou 1). "
            "Cela peut indiquer un échantillon trop petit, trop peu de visites, ou des données avec trop de zéros ou trop de détections."
        )
    naive_theory = psi_true * (1.0 - (1.0 - p_true) ** n_visits) if psi_true is not None else None
    prob_miss = (1.0 - p_true) ** n_visits if p_true is not None else None

    with right:
        if psi_true is not None:
            labels = ["ψ vraie", "ψ estimée\n(modèle)", "Occupation\nnaïve"]
            values = [psi_true, estimates["psi"], estimates["naive"]]
            colors = ["#39d98a", "#4dabf7", "#ff6b6b"]
        else:
            labels = ["ψ estimée\n(modèle)", "Occupation\nnaïve"]
            values = [estimates["psi"], estimates["naive"]]
            colors = ["#4dabf7", "#ff6b6b"]
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
        n_show = min(30, history.shape[0])
        hist_df = pd.DataFrame(
            history[:n_show],
            columns=[f"V{v + 1}" for v in range(n_visits)],
            index=[f"S{i + 1}" for i in range(n_show)],
        )
        st.dataframe(hist_df, use_container_width=True)

    teacher_note(
        (
            f"Occupation naïve théorique = ψ × (1 − (1−p)^K) = "
            f"{psi_true:.2f} × (1 − {1 - p_true:.2f}^{n_visits}) = {naive_theory:.3f}. "
            if psi_true is not None else ""
        ) + "Le modèle maximise la vraisemblance en estimant ψ et p simultanément via logit-link et optimisation Nelder-Mead.",
        context,
    )
    teacher_formula(
        "Vraisemblance du modèle d'occupation (MacKenzie et al. 2002)",
        r"\mathcal{L}(\psi, p \mid \mathbf{y}) = \prod_{i=1}^{N} \Bigl["
        r"\psi \cdot p^{y_i}(1-p)^{K-y_i} + \mathbf{1}_{[y_i=0]}(1-\psi)"
        r"\Bigr]"
        r"\qquad \hat{\psi}_{\text{naïve}} = \psi\bigl[1-(1-p)^K\bigr]",
        context,
    )
    teacher_pitfalls(
        [
            "Confondre absence d'observation et absence réelle : une non-détection n'implique pas que le site est inoccupé.",
            "Violer l'hypothèse de population fermée : si l'espèce peut arriver/partir entre visites, ψ est mal estimée.",
            "Trop peu de visites répétées (K < 3) avec p faible : le modèle ne peut pas séparer ψ de p — la vraisemblance est plate.",
            "Interpréter p comme une propriété fixe de l'espèce : p varie selon la saison, la météo, l'observateur.",
        ],
        context,
    )
    learning_notes(
        "Plus p est faible ou K est petit, plus le biais de l'occupation naïve est grand.",
        "Le modèle suppose une population fermée entre visites et une détection indépendante d'un site à l'autre.",
        None if psi_true is None else "Réduis le nombre de visites à 1 : le modèle peut-il encore distinguer ψ de p ?",
    )
    teacher_summary(
        [
            "Deux paramètres distincts : <strong>ψ</strong> (probabilité qu'un site soit occupé) et <strong>p</strong> (probabilité de détecter l'espèce si présente).",
            "L'<strong>occupation naïve</strong> (sites où vu / sites totaux) sous-estime ψ d'autant plus que p est faible.",
            "Les <strong>visites répétées</strong> (K ≥ 3) sur les mêmes sites permettent de séparer ψ et p par maximum de vraisemblance.",
            "Hypothèse de fermeture entre visites ; p dépend de la saison, météo, observateur — d'où l'intérêt d'intégrer des covariables (ψ ~ habitat, p ~ effort).",
            "Même famille de méthodes que le distance sampling : corriger la <strong>détection imparfaite</strong> plutôt que la nier.",
        ],
        context,
        reference="ORNI 422 — Chap. 6 : Méthodes d'estimation (détection imparfaite)",
    )

    pdf_lines = [
        f"Sites = {history.shape[0]}, visites = {n_visits}.",
        f"Estimations : psi = {estimates['psi']:.3f}, p = {estimates['p']:.3f}.",
        f"Occupation naive = {estimates['naive']:.3f} (biais = {bias:+.3f}).",
    ]
    if psi_true is not None:
        pdf_lines.insert(1, f"Parametres vrais : psi = {psi_true:.3f}, p = {p_true:.3f}.")
    pdf = build_pdf_report("ORNI-LAB - Modèles d'occupation", pdf_lines)
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_occupation.pdf", "application/pdf")
