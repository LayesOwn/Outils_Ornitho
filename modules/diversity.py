from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from core.export import build_pdf_report
from utils.ui import csv_template_button, data_incompatible, explain, learning_notes, module_intro, section, style_figure


def compute_diversity_indices(counts: np.ndarray) -> dict[str, float]:
    counts = counts[counts > 0]
    s = int(len(counts))
    n = int(counts.sum())
    if s == 0:
        return {"S": 0, "N": 0, "H": 0.0, "D": 0.0, "J": 0.0}
    p = counts / n
    h = float(-np.sum(p * np.log(p)))
    d = float(1.0 - np.sum(p ** 2))
    j = h / np.log(s) if s > 1 else 1.0
    return {"S": s, "N": n, "H": round(h, 3), "D": round(d, 3), "J": round(j, 3)}


def accumulation_curve(presence_matrix: np.ndarray, iterations: int = 200, seed: int = 1) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n_sites, n_species = presence_matrix.shape
    curves = np.zeros((iterations, n_sites), dtype=int)
    for k in range(iterations):
        order = rng.permutation(n_sites)
        seen = np.zeros(n_species, dtype=bool)
        for step, site in enumerate(order):
            seen |= presence_matrix[site] > 0
            curves[k, step] = seen.sum()
    return pd.DataFrame({
        "Sites": np.arange(1, n_sites + 1),
        "Moyenne": curves.mean(axis=0),
        "P05": np.percentile(curves, 5, axis=0),
        "P95": np.percentile(curves, 95, axis=0),
    })


def simulate_community(n_sites: int, n_species: int, mean_abundance: float, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    habitats_list = ["Forêt", "Savane", "Zone humide", "Agroécosystème"]
    hab_effects = {"Forêt": 1.20, "Savane": 0.85, "Zone humide": 1.35, "Agroécosystème": 0.65}
    habitat_labels = rng.choice(habitats_list, size=n_sites)
    species_cols = [f"Esp{j + 1:02d}" for j in range(n_species)]
    rows = []
    for i, hab in enumerate(habitat_labels):
        effect = hab_effects[hab]
        expected = mean_abundance * effect * rng.lognormal(0, 0.6, n_species)
        counts = rng.poisson(expected)
        row: dict = {"Site": f"S{i + 1:02d}", "Habitat": hab}
        for j, c in enumerate(counts):
            row[species_cols[j]] = int(c)
        rows.append(row)
    return pd.DataFrame(rows)


def render(context: dict) -> None:
    is_data = context.get("data") is not None
    section("Richesse spécifique et diversité", "Comparer la diversité d'oiseaux entre habitats.")
    module_intro(
        "Les indices de diversité résument la richesse (nombre d'espèces) et l'équitabilité (répartition des abondances) d'une communauté.",
        "Ils servent à comparer des habitats, à suivre l'effet d'une restauration ou à détecter un appauvrissement biologique au fil du temps.",
        "En ornithologie, ils permettent de comparer des points d'écoute, des sites protégés ou restaurés, des saisons ou des années de suivi.",
    )

    left, right = st.columns([0.85, 1.55])

    if context.get("data") is not None:
        data_src = context["data"]
        numeric_cols = context["numeric_columns"]
        cat_cols = context["categorical_columns"]
        if len(numeric_cols) < 2:
            data_incompatible(
                "Ce module calcule la diversité à partir d'une matrice site × espèces : il faut au moins 2 colonnes numériques représentant des abondances par espèce.",
                [
                    "Chaque colonne numérique doit représenter le comptage d'une espèce (ex. : Esp01, Esp02…).",
                    "Vérifiez que les abondances ne sont pas stockées en une seule colonne 'Espèce / Abondance' — dans ce cas, pivotez le tableau d'abord.",
                    "Si votre fichier ne contient qu'une colonne, le module <b>Statistiques descriptives</b> est plus adapté.",
                    "Téléchargez l'exemple CSV pour voir la structure site × espèces attendue.",
                ],
            )
            return
        with left:
            csv_template_button(
                pd.DataFrame({"Habitat": ["Forêt", "Savane", "Zone humide"], "Esp01": [5, 2, 8], "Esp02": [3, 4, 1], "Esp03": [0, 3, 6], "Esp04": [2, 1, 4]}),
                "template_diversite.csv",
            )
            st.markdown("**Format attendu : une colonne par espèce (largeur), une ligne par site.**")
            species_cols = st.multiselect(
                "Colonnes espèces", numeric_cols,
                default=numeric_cols[:min(10, len(numeric_cols))],
            )
            hab_col = st.selectbox("Colonne d'habitat (optionnel)", ["—"] + cat_cols)
        if len(species_cols) < 2:
            st.info("Sélectionnez au moins 2 colonnes espèces.")
            return
        data = data_src[species_cols].fillna(0).copy()
        if hab_col != "—":
            data.insert(0, "Habitat", data_src[hab_col].values)
        else:
            data.insert(0, "Habitat", "Tous les sites")
        data.insert(0, "Site", [f"S{i+1:02d}" for i in range(len(data))])
        species_matrix = data[species_cols].values
    else:
        with left:
            n_sites = st.slider("Nombre de sites", 20, 150, 60)
            n_species = st.slider("Richesse régionale (pool d'espèces)", 10, 60, 24)
            mean_abundance = st.slider("Abondance moyenne par espèce", 0.5, 10.0, 2.5, step=0.5)
            seed = st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=17)
        data = simulate_community(n_sites, n_species, mean_abundance, int(seed))
        species_cols = [c for c in data.columns if c.startswith("Esp")]
        species_matrix = data[species_cols].values

    indices_rows = []
    for hab in data["Habitat"].unique():
        mask = data["Habitat"] == hab
        pooled = species_matrix[mask].sum(axis=0)
        idx = compute_diversity_indices(pooled)
        idx["Habitat"] = hab
        idx["Sites"] = int(mask.sum())
        indices_rows.append(idx)
    indices_df = pd.DataFrame(indices_rows).set_index("Habitat")

    with right:
        fig = px.bar(
            indices_df.reset_index(),
            x="Habitat",
            y="H",
            color="Habitat",
            text=indices_df["H"].reset_index(drop=True).round(2),
            labels={"H": "Shannon H'"},
        )
        fig.update_layout(showlegend=False, yaxis_title="Indice de Shannon H'")
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    tabs = st.tabs(["Indices", "Courbe d'accumulation", "Export"])

    with tabs[0]:
        display = indices_df[["Sites", "S", "N", "H", "D", "J"]].rename(
            columns={
                "S": "Richesse S",
                "N": "Abondance totale",
                "H": "Shannon H'",
                "D": "Simpson 1-D",
                "J": "Équitabilité J",
            }
        )
        st.dataframe(display.round(3), use_container_width=True)
        best_hab = indices_df["H"].idxmax()
        explain(
            f"L'habitat le plus diversifié est {best_hab} (H' = {indices_df.loc[best_hab, 'H']:.3f}). "
            "Shannon H' intègre richesse et équitabilité ; Simpson 1-D est plus sensible aux espèces dominantes."
        )

    with tabs[1]:
        acc_seed = int(seed) if not is_data else 1
        acc = accumulation_curve(species_matrix, iterations=200, seed=acc_seed)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=np.concatenate([acc["Sites"], acc["Sites"].values[::-1]]),
            y=np.concatenate([acc["P95"], acc["P05"].values[::-1]]),
            fill="toself",
            fillcolor="rgba(57,217,138,0.15)",
            line={"color": "rgba(0,0,0,0)"},
            name="IC 90 %",
        ))
        fig2.add_trace(go.Scatter(
            x=acc["Sites"], y=acc["Moyenne"],
            mode="lines", name="Richesse moyenne", line={"width": 3},
        ))
        fig2.update_layout(xaxis_title="Sites échantillonnés", yaxis_title="Espèces cumulées")
        style_figure(fig2)
        st.plotly_chart(fig2, use_container_width=True)
        explain(
            "Un plateau indique que l'inventaire est proche d'être complet. "
            "Une courbe encore croissante à droite suggère qu'il faudrait davantage de sites."
        )

    with tabs[2]:
        st.download_button(
            "Exporter les données CSV",
            data.to_csv(index=False).encode("utf-8"),
            "orni_lab_diversite.csv",
            "text/csv",
        )
        sim_lines = [f"Sites = {n_sites}. Pool régional = {n_species} espèces."] if not is_data else [f"Sites = {len(data)}. Espèces = {len(species_cols)}."]
        pdf = build_pdf_report(
            "ORNI-LAB - Richesse spécifique et diversité",
            sim_lines + [f"{hab}: S={row['S']}, H'={row['H']:.3f}, J={row['J']:.3f}." for hab, row in indices_df.iterrows()],
        )
        if pdf:
            st.download_button("Exporter le résumé PDF", pdf, "orni_lab_diversite.pdf", "application/pdf")

    learning_notes(
        "Shannon H' combine richesse et équitabilité ; une communauté dominée par une seule espèce a un H' bas.",
        "Les indices dépendent de l'effort d'échantillonnage ; comparer uniquement des communautés collectées avec le même protocole.",
        None if is_data else "Réduis le nombre de sites : à partir de combien la richesse estimée se stabilise-t-elle sur la courbe d'accumulation ?",
    )
