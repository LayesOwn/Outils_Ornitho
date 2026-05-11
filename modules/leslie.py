from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.export import build_pdf_report
from data.examples import default_leslie_values
from utils.ui import explain, learning_notes, module_intro, section, style_figure, teacher_formula, teacher_note, teacher_pitfalls


def build_leslie_matrix(fecundity: list[float], survival: list[float]) -> np.ndarray:
    n = len(fecundity)
    if len(survival) != n - 1:
        raise ValueError(
            f"Attendu {n - 1} probabilités de survie pour {n} classes d'âge, reçu {len(survival)}."
        )
    matrix = np.zeros((n, n))
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
    frame["Total"] = frame[["Juvéniles", "1 an", "2 ans", "3 ans et +"]].sum(axis=1)
    return frame


def compute_demography(matrix: np.ndarray) -> dict:
    """
    Compute lambda, sensitivity, elasticity, stable age distribution,
    and reproductive values from a Leslie matrix.

    Sensitivity_ij = v_i * w_j / <v, w>   (Caswell 2001)
    Elasticity_ij  = (a_ij / lambda) * sensitivity_ij
    """
    eigenvalues, right_vecs = np.linalg.eig(matrix)
    _, left_vecs = np.linalg.eig(matrix.T)

    idx_r = int(np.argmax(eigenvalues.real))
    idx_l = int(np.argmax(np.linalg.eig(matrix.T)[0].real))

    lambda_dom = float(eigenvalues[idx_r].real)

    w = right_vecs[:, idx_r].real.copy()
    v = left_vecs[:, idx_l].real.copy()

    if w[0] < 0:
        w = -w
    if v[0] < 0:
        v = -v

    # Stable age distribution (proportions, sums to 1)
    stable_age = w / w.sum()

    # Reproductive values relative to first class
    repro_values = v / v[0]

    # Scale v so that <v_scaled, stable_age> = 1
    # This guarantees that sum(elasticities) = 1 (Caswell 2001)
    v_scaled = v / float(np.dot(v, stable_age))

    sensitivity = np.outer(v_scaled, stable_age)
    elasticity = (matrix * sensitivity) / lambda_dom if lambda_dom != 0 else np.zeros_like(matrix)

    return {
        "lambda": lambda_dom,
        "stable_age": stable_age,
        "repro_values": repro_values,
        "sensitivity": sensitivity,
        "elasticity": elasticity,
    }


def render(context: dict) -> None:
    section(
        "Matrices de Leslie",
        "Projection d'une population femelle structurée par âge — sensibilité et élasticité.",
    )
    module_intro(
        "Une matrice de Leslie projette une population divisée en classes d'âge à partir des fécondités et des probabilités de survie.",
        "Elle permet d'identifier les classes d'âge qui contribuent le plus à la croissance ou au déclin, via l'analyse de sensibilité et d'élasticité.",
        "Indispensable pour cibler les actions de conservation : faut-il améliorer la survie juvénile, la survie adulte ou le succès reproducteur ?",
    )
    fecundity, survival, initial = default_leslie_values()
    class_labels = ["Juvéniles", "1 an", "2 ans", "3 ans et +"]

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
            st.slider(f"S{i}→{i + 1}", 0.0, 1.0, float(v), step=0.01)
            for i, v in enumerate(survival)
        ]

    matrix = build_leslie_matrix(fecundity, survival)
    projection = project_population(matrix, np.array(initial, dtype=float), years)
    demo = compute_demography(matrix)
    lambda_dom = demo["lambda"]

    with right:
        st.dataframe(
            pd.DataFrame(matrix, index=class_labels, columns=class_labels).round(3),
            use_container_width=True,
        )
        fig = px.line(
            projection,
            x="Année",
            y=["Juvéniles", "1 an", "2 ans", "3 ans et +", "Total"],
            labels={"value": "Effectif", "variable": "Classe"},
        )
        fig.update_traces(line={"width": 3})
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    trend = "croissante" if lambda_dom > 1 else "déclinante" if lambda_dom < 1 else "stable"
    explain(
        f"La valeur propre dominante λ = {lambda_dom:.4f}. "
        f"La population projetée est {trend} à long terme "
        f"({100 * (lambda_dom - 1):+.1f} % par génération)."
    )

    # --- Analyse démographique en onglets ---
    tabs = st.tabs(["Structure stable & Valeurs reproductives", "Sensibilité", "Élasticité"])

    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Distribution d'âge stable**")
            st.caption("Proportion de chaque classe à l'équilibre asymptotique.")
            fig_sad = go.Figure(go.Bar(
                x=class_labels,
                y=demo["stable_age"],
                marker_color=["#39d98a", "#4dabf7", "#ff6b6b", "#ffd166"],
                text=[f"{v:.1%}" for v in demo["stable_age"]],
                textposition="outside",
            ))
            fig_sad.update_layout(yaxis_title="Proportion", yaxis_range=[0, max(demo["stable_age"]) * 1.25])
            style_figure(fig_sad)
            st.plotly_chart(fig_sad, use_container_width=True)
        with c2:
            st.markdown("**Valeurs reproductives**")
            st.caption("Contribution relative de chaque classe à la croissance future (classe 0 = référence).")
            fig_rv = go.Figure(go.Bar(
                x=class_labels,
                y=demo["repro_values"],
                marker_color=["#39d98a", "#4dabf7", "#ff6b6b", "#ffd166"],
                text=[f"{v:.2f}" for v in demo["repro_values"]],
                textposition="outside",
            ))
            fig_rv.update_layout(yaxis_title="Valeur reproductive relative", yaxis_range=[0, max(demo["repro_values"]) * 1.25])
            style_figure(fig_rv)
            st.plotly_chart(fig_rv, use_container_width=True)
        teacher_note(
            "La distribution stable est le vecteur propre droit normalisé (w/Σw). "
            "La valeur reproductive est le vecteur propre gauche de Aᵀ, normalisé à 1 pour les juvéniles. "
            "Elle indique ce que vaut un individu de cette classe pour la croissance future de la population.",
            context,
        )
        teacher_formula(
            "Vecteurs propres — définitions",
            r"A\mathbf{w} = \lambda_1 \mathbf{w} \quad\text{(distribution stable, vecteur droit)}"
            r"\qquad A^\top \mathbf{v} = \lambda_1 \mathbf{v} \quad\text{(valeurs reproductives, vecteur gauche)}",
            context,
        )
        teacher_pitfalls(
            [
                "Le signe des vecteurs propres est arbitraire : toujours vérifier que w[0] > 0 avant de normaliser.",
                "La valeur reproductive de la classe 0 est fixée à 1 par convention (normalisation relative) — ce n'est pas une valeur absolue.",
                "La distribution stable ne correspond à la structure observée qu'à long terme, après convergence.",
            ],
            context,
        )

    with tabs[1]:
        st.markdown("**Matrice de sensibilité** — ∂λ/∂aᵢⱼ")
        st.caption(
            "Chaque cellule indique de combien λ changerait si l'élément correspondant de la matrice augmentait d'une unité. "
            "Indépendant de la valeur courante de l'élément."
        )
        sens = demo["sensitivity"]
        fig_s = go.Figure(go.Heatmap(
            z=sens,
            x=class_labels,
            y=class_labels,
            text=[[f"{v:.4f}" for v in row] for row in sens],
            texttemplate="%{text}",
            colorscale="Viridis",
            colorbar={"title": "Sensibilité"},
        ))
        fig_s.update_layout(
            xaxis_title="Classe d'âge de départ (j)",
            yaxis_title="Classe d'âge cible (i)",
            height=350,
        )
        style_figure(fig_s)
        st.plotly_chart(fig_s, use_container_width=True)
        max_idx = np.unravel_index(np.argmax(sens), sens.shape)
        st.info(
            f"Sensibilité maximale : a[{class_labels[max_idx[0]]}, {class_labels[max_idx[1]]}] = {sens[max_idx]:.4f}. "
            "Un changement absolu de cet élément aurait le plus grand impact sur λ."
        )
        teacher_note(
            "La sensibilité répond à : 'si cet élément de la matrice change d'une unité, de combien λ change-t-il ?' "
            "— sans tenir compte de l'amplitude actuelle de l'élément. C'est une dérivée partielle.",
            context,
        )
        teacher_formula(
            "Sensibilité (Caswell 2001)",
            r"S_{ij} = \frac{\partial \lambda}{\partial a_{ij}} = \frac{v_i \, w_j}{\langle \mathbf{v}, \mathbf{w} \rangle}",
            context,
        )
        teacher_pitfalls(
            [
                "La sensibilité compare des changements absolus : une fécondité et une survie ne sont pas comparables en sensibilité (unités différentes).",
                "Un a_ij = 0 peut avoir une sensibilité non nulle : cela indique le 'potentiel' de cet élément, pas son impact actuel.",
            ],
            context,
        )

    with tabs[2]:
        st.markdown("**Matrice d'élasticité** — aᵢⱼ/λ · ∂λ/∂aᵢⱼ")
        st.caption(
            "Variation relative de λ pour une variation relative de 1 % de l'élément. "
            "Les élasticités somment à 1 — outil clé pour prioriser les actions de conservation."
        )
        elas = demo["elasticity"]
        fig_e = go.Figure(go.Heatmap(
            z=elas,
            x=class_labels,
            y=class_labels,
            text=[[f"{v:.4f}" for v in row] for row in elas],
            texttemplate="%{text}",
            colorscale="RdYlGn",
            colorbar={"title": "Élasticité"},
        ))
        fig_e.update_layout(
            xaxis_title="Classe d'âge de départ (j)",
            yaxis_title="Classe d'âge cible (i)",
            height=350,
        )
        style_figure(fig_e)
        st.plotly_chart(fig_e, use_container_width=True)
        max_e_idx = np.unravel_index(np.argmax(elas), elas.shape)
        elas_pct = elas[max_e_idx]
        st.success(
            f"Élasticité maximale : a[{class_labels[max_e_idx[0]]}, {class_labels[max_e_idx[1]]}] = {elas_pct:.4f}. "
            f"Une augmentation de 1 % de cet élément produit une augmentation de {100 * elas_pct:.2f} % de λ. "
            "**C'est le levier de conservation le plus efficace.**"
        )
        teacher_note(
            "L'élasticité est adimensionnelle et permet de comparer des éléments de nature différente (survie vs fécondité). "
            "Pour les oiseaux longévifs (rapaces, albatros), l'élasticité est souvent maximale sur la survie adulte. "
            "Pour les espèces à durée de vie courte, elle peut être plus élevée sur les fécondités.",
            context,
        )
        teacher_formula(
            "Élasticité (Caswell 2001) — propriété clé : Σe_ij = 1",
            r"e_{ij} = \frac{a_{ij}}{\lambda} \cdot S_{ij} = \frac{a_{ij}}{\lambda} \cdot \frac{v_i \, w_j}{\langle \mathbf{v}, \mathbf{w} \rangle}"
            r"\qquad \sum_{i,j} e_{ij} = 1",
            context,
        )
        teacher_pitfalls(
            [
                "Confondre sensibilité (Δλ pour Δa = 1, dimensionné) et élasticité (Δλ/λ pour Δa/a = 1, adimensionnel).",
                "Interpréter une élasticité élevée sur les fécondités comme 'il faut augmenter les fécondités' : en conservation, il faut d'abord vérifier la faisabilité biologique.",
                "Oublier que Σe_ij = 1 : si la somme s'écarte de 1, la normalisation des vecteurs est incorrecte.",
                "Comparer les élasticités entre espèces sans tenir compte de la structure de la matrice (nombre de classes, période).",
            ],
            context,
        )

    st.divider()
    learning_notes(
        "λ > 1 : croissance. λ < 1 : déclin. L'élasticité identifie quel paramètre démographique protéger en priorité.",
        "Le modèle suppose fécondités et survies constantes dans le temps — pas de saisonnalité, ni de catastrophes.",
        "Compare l'élasticité de la survie adulte et du succès reproducteur : lequel contrôle le plus λ ?",
    )

    elas_flat = {
        f"e[{class_labels[i]},{class_labels[j]}]": round(float(elas[i, j]), 4)
        for i in range(len(class_labels))
        for j in range(len(class_labels))
        if matrix[i, j] > 0
    }
    elas_lines = [f"  {k} = {v}" for k, v in elas_flat.items()]

    pdf = build_pdf_report(
        "ORNI-LAB - Matrice de Leslie",
        [
            f"Fécondités : {[round(f, 3) for f in fecundity]}.",
            f"Survies : {[round(s, 3) for s in survival]}.",
            f"Lambda dominant : {lambda_dom:.4f} (population {trend}).",
            f"Structure stable : {[round(float(v), 3) for v in demo['stable_age']]}.",
            f"Valeurs reproductives : {[round(float(v), 3) for v in demo['repro_values']]}.",
            "Élasticités des éléments non nuls :",
        ] + elas_lines,
    )
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_leslie.pdf", "application/pdf")
    st.download_button(
        "Exporter la projection CSV",
        projection.to_csv(index=False).encode("utf-8"),
        "orni_lab_leslie.csv",
        "text/csv",
    )
