from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.spatial import ConvexHull

from core.export import build_pdf_report
from utils.ui import csv_template_button, data_incompatible, explain, learning_notes, module_intro, section, style_figure, teacher_note, teacher_pitfalls

_PALETTE = ["#39d98a", "#4dabf7", "#ff6b6b", "#ffd166", "#b197fc", "#20c997", "#fd7e14", "#e64980"]


def simulate_gps_data(
    n_individuals: int,
    n_locations: int,
    spread: float,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(1, n_individuals + 1):
        cx, cy = rng.uniform(10, 90), rng.uniform(10, 90)
        x = rng.normal(cx, spread, n_locations)
        y = rng.normal(cy, spread, n_locations)
        rows.append(pd.DataFrame({
            "Individu": [f"Ind{i:02d}"] * n_locations,
            "X": x.round(3),
            "Y": y.round(3),
        }))
    return pd.concat(rows, ignore_index=True)


def compute_mcp(x: np.ndarray, y: np.ndarray, pct: float) -> dict:
    pts = np.column_stack([x, y])
    centroid = pts.mean(axis=0)
    dists = np.linalg.norm(pts - centroid, axis=1)
    mask = dists <= np.percentile(dists, pct)
    core = pts[mask]

    if len(core) < 3:
        return {"area": 0.0, "hull_xy": np.empty((0, 2)), "n_used": int(mask.sum()), "n_total": len(pts)}

    hull = ConvexHull(core)
    vertices = core[hull.vertices]
    hull_closed = np.vstack([vertices, vertices[0]])

    return {
        "area": round(float(hull.volume), 4),  # ConvexHull.volume = area in 2-D
        "hull_xy": hull_closed,
        "core": core,
        "n_used": int(mask.sum()),
        "n_total": len(pts),
    }


def _hex_to_rgba(h: str, alpha: float = 0.12) -> str:
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def render(context: dict) -> None:
    section("Domaine vital — MCP", "Minimum Convex Polygon pour estimer le domaine vital à partir de localisations GPS.")
    module_intro(
        "Le MCP délimite le plus petit polygone convexe contenant X % des localisations d'un individu. C'est l'estimateur de domaine vital le plus répandu et le plus simple à calculer.",
        "Rapide, facile à interpréter et largement utilisé pour comparer les domaines vitaux entre individus, sexes ou saisons dans les études de télémétrie.",
        "En ornithologie, les données GPS de rapaces, cigognes, passereaux ou limicoles équipés de balises permettent de cartographier zones de chasse, de repos et de migration.",
    )

    left, right = st.columns([0.9, 1.55])

    if context.get("data") is not None:
        data_src = context["data"]
        num_cols = context["numeric_columns"]
        cat_cols = context["categorical_columns"]
        if len(num_cols) < 2:
            data_incompatible(
                "Ce module nécessite deux colonnes numériques de coordonnées GPS (X/longitude et Y/latitude) pour calculer le polygone convexe.",
                [
                    "Vérifiez que votre fichier contient des colonnes de coordonnées numériques (ex. : X, Y ou Longitude, Latitude).",
                    "Les coordonnées doivent être des nombres décimaux (ex. : 48.853, 2.349), pas des chaînes de caractères.",
                    "Si vous avez des coordonnées en DMS (degrés-minutes-secondes), convertissez-les d'abord en degrés décimaux.",
                    "Téléchargez l'exemple CSV pour voir la structure attendue.",
                ],
            )
            return
        with left:
            csv_template_button(
                pd.DataFrame({
                    "Individu": ["A", "A", "A", "A", "B", "B", "B", "B"],
                    "X": [48.21, 48.53, 49.10, 47.83, 52.31, 53.12, 52.84, 51.95],
                    "Y": [2.31, 2.35, 2.29, 2.38, 2.41, 2.39, 2.45, 2.43],
                }),
                "template_mcp.csv",
            )
            x_col = st.selectbox("Colonne X (longitude / est)", num_cols)
            y_col = st.selectbox("Colonne Y (latitude / nord)", [c for c in num_cols if c != x_col])
            id_col = st.selectbox("Colonne individu (optionnel)", ["—"] + cat_cols)
            pct = st.slider("Percentile MCP (%)", 50, 100, 95)

        cols_to_use = [x_col, y_col] + ([id_col] if id_col != "—" else [])
        data = data_src[cols_to_use].dropna().copy()
        data = data.rename(columns={x_col: "X", y_col: "Y"})
        if id_col != "—":
            data = data.rename(columns={id_col: "Individu"})
        else:
            data["Individu"] = "Tous"
    else:
        with left:
            n_ind = st.slider("Nombre d'individus", 1, 8, 3)
            n_locs = st.slider("Localisations par individu", 20, 200, 60)
            spread = st.slider("Dispersion spatiale (unités)", 1.0, 20.0, 5.0, step=0.5)
            pct = st.slider("Percentile MCP (%)", 50, 100, 95)
            seed = st.number_input("Graine", 1, 9999, 7)
        data = simulate_gps_data(n_ind, n_locs, spread, int(seed))

    individuals = sorted(data["Individu"].unique())
    fig = go.Figure()
    records = []

    for i, ind in enumerate(individuals):
        sub = data[data["Individu"] == ind]
        x_arr, y_arr = sub["X"].values, sub["Y"].values
        c = _PALETTE[i % len(_PALETTE)]
        mcp = compute_mcp(x_arr, y_arr, pct)
        records.append({
            "Individu": ind,
            f"Aire MCP {pct}%": mcp["area"],
            "N utilisé": mcp["n_used"],
            "N total": mcp["n_total"],
        })

        fig.add_scatter(
            x=x_arr, y=y_arr, mode="markers", name=f"{ind}",
            marker={"size": 5, "color": c, "opacity": 0.45},
            legendgroup=ind,
        )
        if len(mcp["hull_xy"]) >= 3:
            fig.add_scatter(
                x=mcp["hull_xy"][:, 0], y=mcp["hull_xy"][:, 1],
                mode="lines", name=f"{ind} MCP {pct}%",
                line={"width": 2.5, "color": c},
                fill="toself", fillcolor=_hex_to_rgba(c),
                legendgroup=ind,
            )

    fig.update_layout(xaxis_title="X", yaxis_title="Y", hovermode="closest")
    style_figure(fig)

    with right:
        st.plotly_chart(fig, use_container_width=True)

    summary = pd.DataFrame(records)
    st.dataframe(summary, use_container_width=True)

    mean_area = summary[f"Aire MCP {pct}%"].mean()
    explain(
        f"MCP {pct}% : aire moyenne = {mean_area:.2f} unités². "
        f"Les {100 - pct}% de localisations les plus éloignées du centroïde sont exclues, "
        f"réduisant l'influence des excursions exceptionnelles."
    )

    teacher_note(
        f"Le MCP 100% est très sensible aux points aberrants (excursions rares, erreurs GPS). "
        f"Le MCP {pct}% exclut les {100 - pct}% de points les plus éloignés du centroïde. "
        f"L'aire augmente mécaniquement avec N : comparer uniquement des individus avec un effort équivalent. "
        f"Référence fondatrice : Mohr (1947).",
        context,
    )
    teacher_pitfalls(
        [
            f"Comparer des MCP entre individus avec des N différents : l'aire MCP augmente avec N même si le domaine vital est identique.",
            "Utiliser le MCP pour des espèces avec des mouvements bimodaux (ex: migration) : le polygone englobe des zones non utilisées.",
            "Ignorer les erreurs de localisation GPS : un fix erroné en bordure peut gonfler massivement l'aire MCP 100%.",
            "Confondre domaine vital (zone fréquentée) et territoire défendu : le MCP ne distingue pas les deux.",
        ],
        context,
    )
    learning_notes(
        "Le MCP surestime souvent le domaine vital si les points sont agrégés en clusters : le KDE est alors préférable.",
        "L'unité de l'aire dépend du système de coordonnées : UTM (km²), degrés décimaux ou local.",
        None if context.get("data") else "Augmente N et observe comment l'aire du MCP croît avec le nombre de localisations.",
    )

    pdf_lines = [f"MCP {pct}% — {len(individuals)} individu(s), {len(data)} localisations."]
    for rec in records:
        pdf_lines.append(f"  {rec['Individu']} : aire = {rec[f'Aire MCP {pct}%']:.4f}, N = {rec['N utilisé']}/{rec['N total']}.")
    pdf = build_pdf_report("ORNI-LAB - Domaine vital MCP", pdf_lines)
    if pdf:
        st.download_button("Exporter résumé PDF", pdf, "orni_lab_mcp.pdf", "application/pdf")
    st.download_button(
        "Exporter localisations CSV",
        data.to_csv(index=False).encode("utf-8"),
        "orni_lab_mcp_data.csv", "text/csv",
    )
