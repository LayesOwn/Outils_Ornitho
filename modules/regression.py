from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from core.export import build_pdf_report
from data.examples import wing_mass_dataset
from utils.ui import csv_template_button, data_incompatible, explain, learning_notes, module_intro, section, style_figure, teacher_note


def render(context: dict) -> None:
    is_data = context.get("data") is not None
    section(
        "Corrélation et régression",
        None if is_data else "Exemple : relation entre longueur de l'aile et masse corporelle chez des passereaux.",
    )
    module_intro(
        "La corrélation mesure l'intensité d'une relation entre deux variables. La régression estime une équation permettant de prédire une variable à partir d'une autre.",
        "Ces outils servent à tester une relation biologique, quantifier sa force et produire une prédiction avec une incertitude.",
        "En ornithologie, ils permettent d'étudier les liens entre morphologie, condition corporelle, climat, habitat, abondance ou succès reproducteur.",
    )
    left, right = st.columns([0.85, 1.6])

    if context.get("data") is not None:
        import pandas as _pd
        data_src = context["data"]
        numeric_cols = context["numeric_columns"]
        if len(numeric_cols) < 2:
            data_incompatible(
                "Ce module nécessite au moins deux colonnes numériques pour calculer une corrélation ou ajuster une régression.",
                [
                    "Vérifiez que votre fichier contient deux mesures quantitatives (ex. : longueur de l'aile et masse corporelle).",
                    "Si une colonne numérique est lue comme texte, assurez-vous que les décimales utilisent '.' ou ',' (converti automatiquement).",
                    "Téléchargez l'exemple CSV pour voir la structure attendue.",
                ],
            )
            return
        with left:
            csv_template_button(
                _pd.DataFrame({"Longueur_aile_mm": [72.1, 75.4, 68.9, 80.2, 71.3], "Masse_g": [18.2, 20.1, 17.4, 22.5, 17.9]}),
                "template_regression.csv",
            )
            x_col = st.selectbox("Variable explicative X", numeric_cols, index=0)
            y_opts = [c for c in numeric_cols if c != x_col]
            y_col = st.selectbox("Variable réponse Y", y_opts, index=0)
        data = data_src[[x_col, y_col]].dropna().rename(columns={x_col: "X", y_col: "Y"})
        data.columns = [x_col, y_col]
    else:
        with left:
            n = st.slider("Nombre d'oiseaux mesurés", 12, 120, 42)
            noise = st.slider("Variabilité individuelle", 0.5, 8.0, 2.4, step=0.1)
            seed = st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=7)
        data = wing_mass_dataset(seed=int(seed), n=n, noise=noise)
        x_col, y_col = "Longueur de l'aile (mm)", "Masse corporelle (g)"

    if len(data) < 3:
        data_incompatible(
            f"Seulement {len(data)} observation(s) valide(s) après suppression des valeurs manquantes — il en faut au moins 3.",
            [
                "Vérifiez que les colonnes sélectionnées ne contiennent pas trop de valeurs vides (NA).",
                "Utilisez le module <b>Analyse CSV</b> pour identifier et corriger les lignes incomplètes.",
            ],
        )
        return

    x = data[x_col]
    y = data[y_col]
    if x.std() == 0:
        data_incompatible(
            f"La colonne <b>{x_col}</b> est constante (toutes les valeurs sont identiques) — la régression est impossible.",
            [
                "Choisissez une autre variable explicative X qui varie réellement dans vos données.",
                f"Vérifiez que la colonne <b>{x_col}</b> n'est pas un identifiant ou un code fixe.",
            ],
        )
        return
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    data["Prédiction"] = intercept + slope * x

    with right:
        sorted_data = data.sort_values(x_col)
        fig = go.Figure()
        fig.add_scatter(
            x=data[x_col],
            y=data[y_col],
            mode="markers",
            name="Observations",
            marker={"size": 10, "line": {"width": 1, "color": "#ffffff"}},
        )
        fig.add_scatter(
            x=sorted_data[x_col],
            y=sorted_data["Prédiction"],
            mode="lines",
            name="Régression linéaire",
            line={"width": 3},
        )
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            hovermode="closest",
        )
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("r de Pearson", f"{r_value:.3f}")
    c2.metric("R²", f"{r_value**2:.3f}")
    c3.metric("p-value", f"{p_value:.3g}")

    direction = "positive" if slope > 0 else "négative"
    abs_r = abs(r_value)
    if abs_r >= 0.9:
        strength_label = "très forte"
    elif abs_r >= 0.7:
        strength_label = "forte"
    elif abs_r >= 0.5:
        strength_label = "assez forte"
    elif abs_r >= 0.3:
        strength_label = "modérée"
    else:
        strength_label = "faible"

    r2_pct = 100 * r_value ** 2
    r2_quality = (
        "excellente" if r2_pct >= 81
        else "bonne" if r2_pct >= 49
        else "acceptable" if r2_pct >= 25
        else "faible"
    )

    explain(
        f"**r = {r_value:.3f}** : corrélation {strength_label} et {direction}. "
        f"Une unité supplémentaire de {x_col} est associée à **{slope:.3g}** unité de {y_col}. "
        f"**R² = {r_value**2:.3f}** ({r2_pct:.1f} %) : qualité de prédiction {r2_quality} — "
        f"le modèle linéaire explique {r2_pct:.1f} % de la variabilité de {y_col}."
    )

    with st.expander("Cours : Interpréter r de Pearson et R²"):
        st.markdown("#### Grille d'interprétation de r de Pearson")
        st.markdown(
            "Le coefficient r mesure l'intensité et le sens d'une relation **linéaire** entre deux variables (−1 ≤ r ≤ +1).\n\n"
            "| |r| | Interprétation | Exemple ornithologique |\n"
            "|-------|----------------|------------------------|\n"
            "| < 0,3 | Faible | Pas de relation claire |\n"
            "| 0,3 – 0,5 | Modérée | Lien tarsométatarse / masse |\n"
            "| 0,5 – 0,7 | Assez forte | Longueur du bec / taille de proie |\n"
            "| 0,7 – 0,9 | Forte | Longueur aile / masse corporelle |\n"
            "| ≥ 0,9 | Très forte | Mesures répétées du même individu |\n"
        )
        st.markdown("#### Interprétation de R²")
        st.markdown(
            "R² = r² : proportion de la variance de Y expliquée par le modèle linéaire.\n\n"
            "| R² | Qualité du modèle |\n"
            "|----|-------------------|\n"
            "| ≥ 81 % | Excellente |\n"
            "| 49 – 81 % | Bonne |\n"
            "| 25 – 49 % | Acceptable |\n"
            "| < 25 % | Faible — chercher d'autres variables explicatives |\n"
        )
        st.markdown("#### Équation de régression linéaire")
        st.markdown(
            "Le modèle s'écrit **Y = a + b × X** où :\n\n"
            f"- **b = {slope:.4g}** (pente) : variation de {y_col} pour +1 unité de {x_col}\n"
            f"- **a = {intercept:.4g}** (ordonnée à l'origine)\n\n"
            f"→ Équation ajustée : **{y_col} = {intercept:.3g} + {slope:.3g} × {x_col}**\n\n"
            "**Résidus** : écart entre valeur observée et valeur prédite. "
            "Des résidus aléatoirement répartis de part et d'autre de zéro confirment que le modèle linéaire est approprié. "
            "Un résidu systématique (courbe, entonnoir) signale une hypothèse violée."
        )
        st.info(
            "Corrélation ≠ causalité. Une corrélation forte peut résulter d'une variable confondante "
            "(ex. : longueur de l'aile et masse toutes deux liées à l'âge ou au sexe)."
        )

    learning_notes(
        "Vérifier toujours la significativité (p-value) ET la taille d'effet (R²). Un R² > 49 % indique un modèle à bonne capacité prédictive.",
        "Une corrélation forte ne prouve pas de causalité. R² mesure la linéarité : une relation courbe peut donner un r faible même avec un lien réel.",
        None if is_data else "Augmente la variabilité individuelle et observe à partir de quel niveau R² devient inférieur à 25 %.",
    )
    teacher_note(
        f"Équation ajustée : {y_col} = {intercept:.3g} + {slope:.3g} × {x_col}. "
        "Faire distinguer corrélation, causalité et qualité prédictive. "
        "Montrer le calcul de b = Cov(X,Y)/Var(X) et a = ȳ − b×x̄.",
        context,
    )

    with st.expander("Voir les données"):
        st.dataframe(data, use_container_width=True)
    st.download_button("Exporter les données CSV", data.to_csv(index=False).encode("utf-8"), "orni_lab_regression.csv", "text/csv")

    pdf = build_pdf_report(
        "ORNI-LAB - Corrélation et régression",
        [
            f"n = {len(data)}, X = {x_col}, Y = {y_col}.",
            f"Pente = {slope:.3f}, intercept = {intercept:.3f}.",
            f"r = {r_value:.3f}, R2 = {r_value**2:.3f}, p = {p_value:.3g}.",
            f"Interpretation : relation {strength_label} ({direction}).",
        ],
    )
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_regression.pdf", "application/pdf")
