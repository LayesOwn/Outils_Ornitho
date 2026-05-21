from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from core.export import build_pdf_report
from utils.ui import csv_template_button, data_incompatible, explain, learning_notes, module_intro, section, style_figure


def generate_counts(seed: int, sites: int, mean_count: int, dispersion: float) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    habitats = rng.choice(["Forêt", "Savane", "Zone humide", "Agroécosystème"], size=sites)
    effects = pd.Series(habitats).map({"Forêt": 1.15, "Savane": 0.9, "Zone humide": 1.35, "Agroécosystème": 0.75}).to_numpy()
    probability = np.clip(dispersion / (dispersion + mean_count * effects), 0.05, 0.95)
    counts = rng.negative_binomial(max(1, int(dispersion)), probability)
    return pd.DataFrame({"Site": [f"S{i + 1:02d}" for i in range(sites)], "Habitat": habitats, "Abondance": counts})


def render(context: dict) -> None:
    is_data = context.get("data") is not None
    section(
        "Statistiques descriptives",
        None if is_data else "Exemple : abondance observée sur des points d'écoute.",
    )
    module_intro(
        "Les statistiques descriptives résument un jeu de données avec des indicateurs de tendance centrale (moyenne, médiane) et de dispersion (écart-type, IQR, CV). Elles s'appliquent aux variables quantitatives continues (masse, taille d'aile) ou discrètes (abondance).",
        "Elles servent à comprendre la structure d'un jeu de données avant tout test ou modèle : identifier la forme de la distribution, repérer les valeurs aberrantes et choisir les bons indicateurs.",
        "En ornithologie, elles permettent de résumer des abondances par point d'écoute, des masses corporelles, des richesses spécifiques ou des succès reproducteurs, et de détecter des sites atypiques.",
    )

    left, right = st.columns([0.85, 1.55])

    if is_data:
        data_src = context["data"]
        numeric_cols = context["numeric_columns"]
        cat_cols = context["categorical_columns"]
        if not numeric_cols:
            data_incompatible(
                "Aucune colonne numérique détectée dans le fichier chargé. Ce module nécessite au moins une variable quantitative (abondance, masse, longueur…).",
                [
                    "Vérifiez que les valeurs numériques n'utilisent pas un format non reconnu (ex. : espaces comme séparateurs de milliers).",
                    "Assurez-vous que les décimales sont '.' ou ',' — ORNI-LAB convertit automatiquement.",
                    "Si votre fichier ne contient que des codes ou des catégories, ce module n'est pas adapté.",
                    "Téléchargez l'exemple CSV pour voir la structure attendue.",
                ],
            )
            return
        with left:
            csv_template_button(
                pd.DataFrame({"Abondance": [12, 5, 23, 8, 17], "Habitat": ["Forêt", "Savane", "Zone humide", "Forêt", "Savane"]}),
                "template_stats_descriptives.csv",
            )
            count_col = st.selectbox("Colonne d'abondance", numeric_cols)
            hab_col = st.selectbox("Colonne d'habitat (optionnel)", ["—"] + cat_cols)
        sub = data_src[[count_col] + ([hab_col] if hab_col != "—" else [])].dropna(subset=[count_col])
        data = sub.rename(columns={count_col: "Abondance"})
        if hab_col == "—":
            data["Habitat"] = "Tous les sites"
        else:
            data = data.rename(columns={hab_col: "Habitat"})
        x_title = count_col
    else:
        with left:
            sites = st.slider("Nombre de sites", 10, 120, 48)
            mean_count = st.slider("Abondance moyenne attendue", 1, 80, 18)
            dispersion = st.slider("Agrégation spatiale", 1.0, 30.0, 8.0, step=1.0)
            seed = st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=21)
        data = generate_counts(int(seed), sites, mean_count, dispersion)
        x_title = "Nombre d'individus observés"

    desc = data["Abondance"].describe()

    with right:
        fig = px.histogram(data, x="Abondance", color="Habitat", marginal="box", nbins=18)
        fig.update_layout(xaxis_title=x_title, yaxis_title="Nombre de sites")
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    mean_val = desc["mean"]
    median_val = desc["50%"]
    std_val = desc["std"]
    q1 = desc["25%"]
    q3 = desc["75%"]
    iqr = q3 - q1
    cv = (std_val / mean_val * 100) if mean_val != 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Moyenne", f"{mean_val:.1f}")
    c2.metric("Médiane", f"{median_val:.1f}")
    c3.metric("Écart-type", f"{std_val:.1f}")
    c4.metric("Maximum", f"{desc['max']:.0f}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Q1 (25 %)", f"{q1:.1f}")
    c6.metric("Q3 (75 %)", f"{q3:.1f}")
    c7.metric("IQR", f"{iqr:.1f}")
    c8.metric("CV (%)", f"{cv:.1f}")

    diff = mean_val - median_val
    if abs(diff) < 0.05 * max(mean_val, 0.001):
        asym_msg = "la distribution est approximativement symétrique"
    elif diff > 0:
        asym_msg = (
            f"la moyenne ({mean_val:.1f}) > médiane ({median_val:.1f}) : distribution "
            "asymétrique à droite — quelques sites très riches tirent la moyenne vers le haut"
        )
    else:
        asym_msg = (
            f"la moyenne ({mean_val:.1f}) < médiane ({median_val:.1f}) : distribution "
            "asymétrique à gauche — quelques très petites valeurs abaissent la moyenne"
        )
    cv_level = "faible (distribution homogène entre sites)" if cv < 15 else "modérée" if cv < 30 else "forte — forte hétérogénéité spatiale"
    explain(
        f"{asym_msg.capitalize()}. "
        f"Le coefficient de variation est **{cv:.1f} %** : variabilité {cv_level}. "
        f"L'IQR = {iqr:.1f} représente l'étendue des 50 % centraux des valeurs."
    )

    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr
    outliers = data["Abondance"][(data["Abondance"] < lower_fence) | (data["Abondance"] > upper_fence)]

    with st.expander("Cours : Indicateurs statistiques clés"):
        st.markdown("#### Types de variables quantitatives")
        st.markdown(
            "| Type | Description | Exemples ornithologiques |\n"
            "|------|-------------|-------------------------|\n"
            "| **Discrète** | Valeurs entières, comptage | Nombre d'individus, d'œufs, d'espèces |\n"
            "| **Continue** | Valeurs réelles | Masse (g), longueur de l'aile (mm), distance |\n"
        )
        st.markdown("#### Tendance centrale : moyenne vs médiane")
        st.markdown(
            "La **moyenne** est sensible aux valeurs extrêmes. La **médiane** (Q2) est robuste. "
            "Leur comparaison révèle la forme de la distribution :\n\n"
            "- Moyenne ≈ Médiane → distribution symétrique\n"
            "- Moyenne > Médiane → asymétrie à droite (longue queue vers les grandes valeurs)\n"
            "- Moyenne < Médiane → asymétrie à gauche\n\n"
            "**En ornithologie**, les comptages sont presque toujours asymétriques à droite : "
            "la plupart des sites ont peu d'individus et quelques sites concentrent les effectifs."
        )
        st.markdown("#### Coefficient de variation (CV)")
        st.markdown(
            "CV = (écart-type / moyenne) × 100. Permet de comparer la dispersion quelle que soit l'unité.\n\n"
            "| CV | Interprétation |\n"
            "|----|----------------|\n"
            "| < 15 % | Faible variabilité — population homogène entre sites |\n"
            "| 15 – 30 % | Variabilité modérée — variation naturelle normale |\n"
            "| ≥ 30 % | Forte variabilité — forte hétérogénéité spatiale |\n"
        )
        st.markdown("#### Quartiles et détection des valeurs aberrantes")
        st.markdown(
            "- **Q1** = 25 % des valeurs sont en-dessous  \n"
            "- **Q2** = médiane = 50 %  \n"
            "- **Q3** = 75 %  \n"
            "- **IQR** = Q3 − Q1 (étendue inter-quartile, couvre 50 % des données centrales)\n\n"
            "**Règle de Tukey :** une valeur est potentiellement aberrante si elle dépasse "
            "Q3 + 1,5 × IQR ou est en-dessous de Q1 − 1,5 × IQR."
        )
        st.info(
            f"Pour ce jeu de données — borne inférieure : {lower_fence:.1f} | borne supérieure : {upper_fence:.1f}. "
            f"**{len(outliers)} valeur(s) potentiellement aberrante(s) détectée(s)**."
        )

    learning_notes(
        "Toujours examiner la distribution (histogramme + boxplot) et comparer moyenne/médiane avant de conclure. Calculer le CV pour évaluer l'homogénéité entre sites.",
        "La moyenne est sensible aux valeurs aberrantes. Sur des comptages d'oiseaux, la distribution est souvent asymétrique à droite — la médiane est alors plus représentative.",
        None if is_data else "Augmente l'agrégation spatiale et observe comment la moyenne, la médiane et le CV évoluent. À partir de quel CV parle-t-on de forte hétérogénéité ?",
    )

    with st.expander("Données et résumé par habitat"):
        st.dataframe(data, use_container_width=True)
        summary = data.groupby("Habitat")["Abondance"].agg(["count", "mean", "median", "std"]).round(2)
        st.dataframe(summary, use_container_width=True)

    st.download_button("Exporter les données CSV", data.to_csv(index=False).encode("utf-8"), "orni_lab_stats_descriptives.csv", "text/csv")
    pdf = build_pdf_report(
        "ORNI-LAB - Statistiques descriptives",
        [f"N = {len(data)}. Moyenne = {desc['mean']:.2f}. Mediane = {desc['50%']:.2f}. Ecart-type = {desc['std']:.2f}."],
    )
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_stats_descriptives.pdf", "application/pdf")
