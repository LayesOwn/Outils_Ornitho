from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from core.export import build_pdf_report
from utils.ui import explain, learning_notes, module_intro, section, style_figure


def generate_counts(seed: int, sites: int, mean_count: int, dispersion: float) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    habitats = rng.choice(["Forêt", "Savane", "Zone humide", "Agroécosystème"], size=sites)
    effects = pd.Series(habitats).map({"Forêt": 1.15, "Savane": 0.9, "Zone humide": 1.35, "Agroécosystème": 0.75}).to_numpy()
    probability = np.clip(dispersion / (dispersion + mean_count * effects), 0.05, 0.95)
    counts = rng.negative_binomial(max(1, int(dispersion)), probability)
    return pd.DataFrame({"Site": [f"S{i + 1:02d}" for i in range(sites)], "Habitat": habitats, "Abondance": counts})


def render(context: dict) -> None:
    section("Statistiques descriptives", "Exemple : abondance observée sur des points d'écoute.")
    module_intro(
        "Les statistiques descriptives résument un jeu de données avec des indicateurs simples : moyenne, médiane, dispersion, minimum et maximum.",
        "Elles servent à comprendre rapidement la structure d'un jeu de données avant d'appliquer un modèle ou un test.",
        "En ornithologie, elles permettent de résumer des abondances, masses, tailles d'ailes, richesses spécifiques ou succès reproducteurs.",
    )

    left, right = st.columns([0.85, 1.55])
    with left:
        sites = st.slider("Nombre de sites", 10, 120, 48)
        mean_count = st.slider("Abondance moyenne attendue", 1, 80, 18)
        dispersion = st.slider("Agrégation spatiale", 1.0, 30.0, 8.0, step=1.0)
        seed = st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=21)

    data = generate_counts(int(seed), sites, mean_count, dispersion)
    stats = data["Abondance"].describe()

    with right:
        fig = px.histogram(data, x="Abondance", color="Habitat", marginal="box", nbins=18)
        fig.update_layout(xaxis_title="Nombre d'individus observés", yaxis_title="Nombre de sites")
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Moyenne", f"{stats['mean']:.1f}")
    c2.metric("Médiane", f"{stats['50%']:.1f}")
    c3.metric("Écart-type", f"{stats['std']:.1f}")
    c4.metric("Maximum", f"{stats['max']:.0f}")
    explain(
        f"La moyenne est {stats['mean']:.1f}, tandis que la médiane est {stats['50%']:.1f}. "
        "Un écart important entre ces valeurs indique une distribution asymétrique, fréquente dans les comptages d'oiseaux."
    )
    learning_notes(
        "Toujours regarder la distribution avant de conclure.",
        "La moyenne seule peut masquer des sites très riches ou très pauvres.",
        "Augmente l'agrégation spatiale et observe l'effet sur la moyenne et la médiane.",
    )

    with st.expander("Données et résumé par habitat"):
        st.dataframe(data, use_container_width=True)
        summary = data.groupby("Habitat")["Abondance"].agg(["count", "mean", "median", "std"]).round(2)
        st.dataframe(summary, use_container_width=True)

    st.download_button("Exporter les données CSV", data.to_csv(index=False).encode("utf-8"), "orni_lab_stats_descriptives.csv", "text/csv")
    pdf = build_pdf_report(
        "ORNI-LAB - Statistiques descriptives",
        [f"Sites = {sites}. Moyenne = {stats['mean']:.2f}. Médiane = {stats['50%']:.2f}. Écart-type = {stats['std']:.2f}."],
    )
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_stats_descriptives.pdf", "application/pdf")
