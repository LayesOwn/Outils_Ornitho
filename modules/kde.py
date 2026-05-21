from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import gaussian_kde

from core.export import build_pdf_report
from utils.ui import csv_template_button, data_incompatible, explain, learning_notes, module_intro, section, style_figure, teacher_formula, teacher_note, teacher_pitfalls

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
        cx, cy = rng.uniform(15, 85), rng.uniform(15, 85)
        x = rng.normal(cx, spread, n_locations)
        y = rng.normal(cy, spread, n_locations)
        rows.append(pd.DataFrame({
            "Individu": [f"Ind{i:02d}"] * n_locations,
            "X": x.round(3),
            "Y": y.round(3),
        }))
    return pd.concat(rows, ignore_index=True)


def compute_kde_homerange(
    x: np.ndarray,
    y: np.ndarray,
    bw_factor: float,
    levels: list[int],
    grid_n: int = 150,
) -> dict:
    margin = 2.5
    sx, sy = x.std(), y.std()
    xmin, xmax = x.min() - margin * sx, x.max() + margin * sx
    ymin, ymax = y.min() - margin * sy, y.max() + margin * sy

    xi = np.linspace(xmin, xmax, grid_n)
    yi = np.linspace(ymin, ymax, grid_n)
    xx, yy = np.meshgrid(xi, yi)

    with st.spinner("Calcul de la densité KDE…"):
        kde = gaussian_kde(np.vstack([x, y]), bw_method=bw_factor)
        zz = kde(np.vstack([xx.ravel(), yy.ravel()])).reshape(grid_n, grid_n)

    dx = (xmax - xmin) / grid_n
    dy = (ymax - ymin) / grid_n
    cell_area = dx * dy

    # Isopleth thresholds: find density level containing `level`% of probability
    z_flat_desc = np.sort(zz.ravel())[::-1]
    cumprob = np.cumsum(z_flat_desc) / z_flat_desc.sum()

    thresholds: dict[int, float] = {}
    areas: dict[int, float] = {}
    for lev in levels:
        idx = int(np.searchsorted(cumprob, lev / 100.0))
        idx = min(idx, len(z_flat_desc) - 1)
        thresh = float(z_flat_desc[idx])
        thresholds[lev] = thresh
        areas[lev] = round(float((zz >= thresh).sum() * cell_area), 4)

    return {"xi": xi, "yi": yi, "zz": zz, "thresholds": thresholds, "areas": areas}


def render(context: dict) -> None:
    section("Domaine vital — KDE", "Kernel Density Estimation pour une estimation probabiliste du domaine vital.")
    module_intro(
        "Le KDE (Kernel Density Estimation) estime une surface de densité de probabilité à partir des localisations GPS, puis extrait des isopleths (contours de probabilité) pour délimiter le domaine vital.",
        "Plus robuste que le MCP aux excursions rares et aux distributions non convexes ; distingue les zones cœur (50%) des zones de fréquentation (95%).",
        "Standard actuel en écologie du mouvement pour les oiseaux équipés de GPS ou PTT (balises Argos). Utilisé pour identifier les habitats critiques, couloirs migratoires et zones de reproduction.",
    )

    left, right = st.columns([0.9, 1.55])

    if context.get("data") is not None:
        data_src = context["data"]
        num_cols = context["numeric_columns"]
        cat_cols = context["categorical_columns"]
        if len(num_cols) < 2:
            data_incompatible(
                "Ce module nécessite deux colonnes numériques de coordonnées GPS (X/longitude et Y/latitude) pour estimer la densité de probabilité.",
                [
                    "Vérifiez que votre fichier contient des colonnes de coordonnées numériques (ex. : X, Y ou Longitude, Latitude).",
                    "Les coordonnées doivent être des nombres décimaux — vérifiez que les virgules décimales sont bien interprétées.",
                    "Si vous avez des coordonnées en DMS, convertissez-les en degrés décimaux avant l'import.",
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
                "template_kde.csv",
            )
            x_col = st.selectbox("Colonne X (longitude / est)", num_cols)
            y_col = st.selectbox("Colonne Y (latitude / nord)", [c for c in num_cols if c != x_col])
            id_col = st.selectbox("Colonne individu (optionnel)", ["—"] + cat_cols)
            bw = st.slider("Facteur de lissage (bandwidth)", 0.1, 2.0, 0.5, step=0.05,
                           help="Multiplicateur de la règle de Scott. 1.0 = Scott par défaut.")
            levels = st.multiselect("Isopleths (%)", [50, 75, 90, 95, 99], default=[50, 95])

        cols_to_use = [x_col, y_col] + ([id_col] if id_col != "—" else [])
        data = data_src[cols_to_use].dropna().copy()
        data = data.rename(columns={x_col: "X", y_col: "Y"})
        if id_col != "—":
            data = data.rename(columns={id_col: "Individu"})
        else:
            data["Individu"] = "Tous"
    else:
        with left:
            n_ind = st.slider("Nombre d'individus", 1, 4, 2)
            n_locs = st.slider("Localisations par individu", 30, 300, 80)
            spread = st.slider("Dispersion spatiale (unités)", 1.0, 20.0, 6.0, step=0.5)
            bw = st.slider("Facteur de lissage (bandwidth)", 0.1, 2.0, 0.5, step=0.05)
            levels = st.multiselect("Isopleths (%)", [50, 75, 90, 95, 99], default=[50, 95])
            seed = int(st.number_input("Graine", 1, 9999, 12) or 12)
        data = simulate_gps_data(n_ind, n_locs, spread, int(seed))

    if not levels:
        st.info("Sélectionnez au moins un isopleth.")
        return

    individuals = sorted(data["Individu"].unique())
    records = []

    isopleth_colors = {50: "#ff6b6b", 75: "#ffd166", 90: "#4dabf7", 95: "#39d98a", 99: "#b197fc"}

    tabs = st.tabs([f"Individu {ind}" for ind in individuals[:4]] + (["…"] if len(individuals) > 4 else []))

    for t_idx, ind in enumerate(individuals[:4]):
        sub = data[data["Individu"] == ind]
        x_arr, y_arr = sub["X"].values, sub["Y"].values

        if len(x_arr) < 5:
            with tabs[t_idx]:
                st.warning(f"{ind} : pas assez de points (< 5).")
            continue

        kde_res = compute_kde_homerange(x_arr, y_arr, bw, sorted(levels))
        xi, yi, zz = kde_res["xi"], kde_res["yi"], kde_res["zz"]
        thresholds = kde_res["thresholds"]
        areas = kde_res["areas"]

        fig = go.Figure()

        # Density heatmap
        fig.add_heatmap(
            x=xi, y=yi, z=zz,
            colorscale="YlOrRd",
            opacity=0.7,
            colorbar={"title": "Densité", "thickness": 12},
            showscale=True,
        )

        # Isopleth contour lines for each level
        for lev in sorted(levels, reverse=True):
            thresh = thresholds[lev]
            color = isopleth_colors.get(lev, "#ffffff")
            fig.add_contour(
                x=xi, y=yi, z=zz,
                contours={
                    "type": "constraint",
                    "operation": ">=",
                    "value": thresh,
                    "coloring": "none",
                },
                line={"width": 2.5, "color": color},
                name=f"{lev}% isopleth",
                showscale=False,
                showlegend=True,
            )

        # GPS points overlay
        fig.add_scatter(
            x=x_arr, y=y_arr, mode="markers", name="Localisations",
            marker={"size": 4, "color": "#ffffff", "opacity": 0.35},
            showlegend=True,
        )

        fig.update_layout(
            xaxis_title="X", yaxis_title="Y",
            title={"text": f"KDE — {ind}", "font": {"size": 14}},
        )
        style_figure(fig)

        row = {"Individu": ind}
        for lev in sorted(levels):
            row[f"Aire {lev}%"] = areas[lev]
        records.append(row)

        with tabs[t_idx]:
            st.plotly_chart(fig, use_container_width=True)
            area_cols = st.columns(len(levels))
            for k, lev in enumerate(sorted(levels)):
                area_cols[k].metric(f"Aire {lev}%", f"{areas[lev]:.3f} u²")

    with right if len(individuals) == 1 else st.container():
        pass  # single-individual layout handled in tab

    if records:
        st.divider()
        summary = pd.DataFrame(records)
        st.dataframe(summary, use_container_width=True)

        lev_main = 95 if 95 in levels else levels[-1]
        mean_area = summary[f"Aire {lev_main}%"].mean() if f"Aire {lev_main}%" in summary.columns else 0.0
        explain(
            f"Isopleth {lev_main}% : aire moyenne = {mean_area:.3f} unités². "
            f"Le bandwidth actuel (facteur {bw:.2f} × règle de Scott) contrôle le lissage : "
            f"trop petit → surface fragmentée, trop grand → domaine surestimé."
        )

    teacher_note(
        "La règle de Scott (h = n^{-1/6} * σ) est optimale pour une distribution gaussienne bivariée. "
        "En pratique, un facteur entre 0.5 et 1.5 est raisonnable selon la complexité du domaine. "
        "L'isopleth 50% délimite la zone cœur (core area), l'isopleth 95% le domaine vital complet. "
        "Le KDE est plus stable que le MCP pour des données asymétriques ou multi-modales.",
        context,
    )
    teacher_formula(
        "Estimateur à noyau bivarié (KDE)",
        r"\hat{f}(\mathbf{x}) = \frac{1}{n\,h^2} \sum_{i=1}^{n} K\!\left(\frac{\mathbf{x} - \mathbf{x}_i}{h}\right)"
        r"\quad K(\mathbf{u}) = \frac{1}{2\pi}e^{-\|\mathbf{u}\|^2/2}"
        r"\qquad h_{\text{Scott}} = n^{-1/6}\,\hat{\sigma}",
        context,
    )
    teacher_pitfalls(
        [
            "Choisir un bandwidth trop petit (sous-lissage) : la surface de densité est fragmentée et ne représente pas le vrai domaine vital.",
            "Choisir un bandwidth trop grand (sur-lissage) : la surface déborde sur des habitats non utilisés → aire surestimée.",
            "Ignorer l'autocorrélation temporelle des données GPS haute fréquence (≥ 1 fix/h) : les localisations ne sont pas indépendantes → bandwidth biaisé.",
            "Comparer des isopleths entre individus sans normaliser l'unité spatiale (degrés vs UTM km²) : les aires sont incomparables.",
            "Utiliser le KDE sur moins de 30 localisations : l'estimateur devient très instable.",
        ],
        context,
    )
    learning_notes(
        "L'isopleth 95% KDE est moins sensible aux excursions rares que le MCP 100%, mais dépend du choix du bandwidth.",
        "Le KDE suppose l'indépendance des localisations : un suivi GPS haute fréquence introduit de l'autocorrélation.",
        None if context.get("data") else "Modifie le bandwidth : compare l'aire KDE 95% à l'aire MCP 95% pour le même individu.",
    )

    pdf_lines = [
        f"KDE (bw_factor = {bw:.2f}) — {len(individuals)} individu(s), {len(data)} localisations.",
        f"Isopleths calcules : {sorted(levels)}.",
    ]
    for rec in records:
        line = f"  {rec['Individu']} :"
        for lev in sorted(levels):
            line += f"  {lev}% = {rec.get(f'Aire {lev}%', '—'):.3f}u²"
        pdf_lines.append(line)
    pdf = build_pdf_report("ORNI-LAB - Domaine vital KDE", pdf_lines)
    if pdf:
        st.download_button("Exporter résumé PDF", pdf, "orni_lab_kde.pdf", "application/pdf")
    st.download_button(
        "Exporter localisations CSV",
        data.to_csv(index=False).encode("utf-8"),
        "orni_lab_kde_data.csv", "text/csv",
    )
