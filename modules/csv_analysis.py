from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from core.export import build_pdf_report
from utils.ui import explain, learning_notes, module_intro, section, style_figure


def clean_uploaded_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with empty columns removed and numeric strings converted."""
    data = frame.copy()
    data = data.dropna(axis=1, how="all")
    data.columns = [str(column).strip() for column in data.columns]

    for column in data.columns:
        if data[column].dtype == "object":
            converted = pd.to_numeric(data[column].astype(str).str.replace(",", ".", regex=False), errors="coerce")
            if converted.notna().sum() >= max(3, int(0.7 * data[column].notna().sum())):
                data[column] = converted

    return data


def split_columns_by_type(frame: pd.DataFrame) -> tuple[list[str], list[str]]:
    numeric_columns = frame.select_dtypes(include="number").columns.tolist()
    categorical_columns = [
        column
        for column in frame.columns
        if column not in numeric_columns and frame[column].nunique(dropna=True) <= 30
    ]
    return numeric_columns, categorical_columns


def describe_numeric_columns(frame: pd.DataFrame, numeric_columns: list[str]) -> pd.DataFrame:
    if not numeric_columns:
        return pd.DataFrame()
    summary = frame[numeric_columns].describe().T
    summary["missing"] = frame[numeric_columns].isna().sum()
    summary["cv"] = summary["std"] / summary["mean"].abs()
    return summary.rename(
        columns={
            "count": "n",
            "mean": "moyenne",
            "std": "ecart_type",
            "min": "minimum",
            "50%": "mediane",
            "max": "maximum",
        }
    )


def fit_linear_regression(frame: pd.DataFrame, x_column: str, y_column: str) -> dict[str, float]:
    data = frame[[x_column, y_column]].dropna()
    if len(data) < 3:
        raise ValueError("At least three complete rows are required")
    result = stats.linregress(data[x_column], data[y_column])
    return {
        "n": float(len(data)),
        "slope": float(result.slope),
        "intercept": float(result.intercept),
        "r": float(result.rvalue),
        "r2": float(result.rvalue**2),
        "pvalue": float(result.pvalue),
        "stderr": float(result.stderr),
    }


def compare_two_groups(frame: pd.DataFrame, group_column: str, value_column: str) -> dict[str, float | str]:
    data = frame[[group_column, value_column]].dropna()
    groups = data[group_column].drop_duplicates().tolist()
    if len(groups) != 2:
        raise ValueError("Exactly two groups are required")

    first = data.loc[data[group_column] == groups[0], value_column]
    second = data.loc[data[group_column] == groups[1], value_column]
    if len(first) < 2 or len(second) < 2:
        raise ValueError("Each group needs at least two observations")

    test = stats.ttest_ind(first, second, equal_var=False)
    return {
        "group_a": str(groups[0]),
        "group_b": str(groups[1]),
        "n_a": float(len(first)),
        "n_b": float(len(second)),
        "mean_a": float(first.mean()),
        "mean_b": float(second.mean()),
        "difference": float(first.mean() - second.mean()),
        "t": float(test.statistic),
        "pvalue": float(test.pvalue),
    }


def _read_csv(uploaded_file) -> pd.DataFrame:
    separators = {",": "Virgule", ";": "Point-virgule", "\t": "Tabulation"}
    separator_label = st.selectbox("Séparateur CSV", list(separators.values()), index=1)
    separator = {label: value for value, label in separators.items()}[separator_label]
    return pd.read_csv(uploaded_file, sep=separator)


def render(context: dict) -> None:
    section("Analyse CSV", "Charger un fichier de terrain et produire une première analyse exploratoire.")
    module_intro(
        "Ce module lit un fichier CSV, détecte les variables numériques et catégorielles, puis calcule les indicateurs essentiels.",
        "Il sert à passer d'un tableau brut à une lecture scientifique : distribution, valeurs manquantes, relation entre variables et comparaison de groupes.",
        "En ornithologie, il peut analyser des comptages, mesures morphologiques, succès reproducteurs, habitats, sites ou années de suivi.",
    )

    if context.get("data") is not None:
        data = context["data"]
        source_name = context.get("data_filename", "fichier importé")
        st.info(f"Données chargées depuis la sidebar : **{source_name}** — {len(data):,} lignes, {len(data.columns)} colonnes.")
    else:
        uploaded_file = st.file_uploader("Charger un fichier CSV", type=["csv"])
        if uploaded_file is None:
            st.info("Charge un fichier CSV contenant au moins une colonne numérique pour commencer l'analyse.")
            return
        try:
            raw_data = _read_csv(uploaded_file)
            data = clean_uploaded_data(raw_data)
            source_name = uploaded_file.name
        except Exception as exc:
            st.error(f"Impossible de lire le fichier CSV : {exc}")
            return

    numeric_columns, categorical_columns = split_columns_by_type(data)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lignes", f"{len(data):,}")
    c2.metric("Colonnes", f"{len(data.columns):,}")
    c3.metric("Variables numériques", f"{len(numeric_columns):,}")
    c4.metric("Variables catégorielles", f"{len(categorical_columns):,}")

    with st.expander("Aperçu des données", expanded=True):
        st.dataframe(data.head(100), use_container_width=True)

    if not numeric_columns:
        st.warning("Aucune colonne numérique exploitable n'a été détectée.")
        return

    summary = describe_numeric_columns(data, numeric_columns).round(3)
    tabs = st.tabs(["Résumé", "Distribution", "Relation", "Groupes", "Export"])

    with tabs[0]:
        st.dataframe(summary, use_container_width=True)
        missing_total = int(data.isna().sum().sum())
        explain(
            f"Le fichier contient {len(data):,} lignes et {missing_total:,} valeurs manquantes. "
            "Le coefficient de variation aide à repérer les variables très hétérogènes."
        )

    with tabs[1]:
        selected_numeric = st.selectbox("Variable numérique", numeric_columns)
        color_column = st.selectbox("Colorer par groupe", ["Aucun"] + categorical_columns)
        fig = px.histogram(
            data,
            x=selected_numeric,
            color=None if color_column == "Aucun" else color_column,
            marginal="box",
            nbins=30,
        )
        fig.update_layout(xaxis_title=selected_numeric, yaxis_title="Nombre d'observations")
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        if len(numeric_columns) < 2:
            st.info("Il faut au moins deux colonnes numériques pour analyser une relation.")
        else:
            x_column = st.selectbox("Variable explicative X", numeric_columns, index=0)
            y_options = [column for column in numeric_columns if column != x_column]
            y_column = st.selectbox("Variable réponse Y", y_options, index=0)
            regression = fit_linear_regression(data, x_column, y_column)

            plot_data = data[[x_column, y_column]].dropna().sort_values(x_column)
            fig = px.scatter(plot_data, x=x_column, y=y_column)
            predicted = regression["intercept"] + regression["slope"] * plot_data[x_column]
            fig.add_trace(
                go.Scatter(
                    x=plot_data[x_column],
                    y=predicted,
                    mode="lines",
                    name="Régression linéaire",
                    line={"width": 3},
                )
            )
            fig.update_layout(xaxis_title=x_column, yaxis_title=y_column)
            style_figure(fig)
            st.plotly_chart(fig, use_container_width=True)

            r1, r2, r3, r4 = st.columns(4)
            r1.metric("n", f"{regression['n']:.0f}")
            r2.metric("Pente", f"{regression['slope']:.3g}")
            r3.metric("R²", f"{regression['r2']:.3f}")
            r4.metric("p-value", f"{regression['pvalue']:.3g}")
            explain(
                f"Une unité supplémentaire de {x_column} est associée à "
                f"{regression['slope']:.3g} unité de {y_column}. "
                f"Le modèle explique {100 * regression['r2']:.1f} % de la variation observée."
            )

    with tabs[3]:
        valid_group_columns = [
            column for column in categorical_columns if data[column].dropna().nunique() == 2
        ]
        if not valid_group_columns:
            st.info("Il faut une colonne catégorielle avec exactement deux groupes pour lancer un test de Welch.")
        else:
            group_column = st.selectbox("Variable de groupe", valid_group_columns)
            value_column = st.selectbox("Variable numérique à comparer", numeric_columns)
            comparison = compare_two_groups(data, group_column, value_column)

            fig = px.box(data, x=group_column, y=value_column, points="all", color=group_column)
            fig.update_layout(showlegend=False)
            style_figure(fig)
            st.plotly_chart(fig, use_container_width=True)

            g1, g2, g3 = st.columns(3)
            g1.metric("Différence moyenne", f"{comparison['difference']:.3g}")
            g2.metric("t de Welch", f"{comparison['t']:.3g}")
            g3.metric("p-value", f"{comparison['pvalue']:.3g}")
            explain(
                f"La moyenne de {comparison['group_a']} est {comparison['mean_a']:.3g}, "
                f"celle de {comparison['group_b']} est {comparison['mean_b']:.3g}. "
                "Interprète la p-value avec la taille d'effet et le contexte biologique."
            )

    with tabs[4]:
        cleaned_csv = data.to_csv(index=False).encode("utf-8")
        st.download_button("Exporter les données nettoyées CSV", cleaned_csv, "orni_lab_donnees_nettoyees.csv", "text/csv")

        report_lines = [
            f"Fichier analyse : {source_name}.",
            f"Lignes = {len(data)}, colonnes = {len(data.columns)}.",
            f"Variables numériques = {', '.join(numeric_columns)}.",
            f"Variables catégorielles = {', '.join(categorical_columns) if categorical_columns else 'aucune détectée'}.",
        ]
        for variable, row in summary.head(10).iterrows():
            report_lines.append(
                f"{variable}: n={row['n']:.0f}, moyenne={row['moyenne']:.3g}, "
                f"mediane={row['mediane']:.3g}, ecart-type={row['ecart_type']:.3g}."
            )
        pdf = build_pdf_report("ORNI-LAB - Analyse CSV", report_lines)
        if pdf:
            st.download_button("Exporter le résumé PDF", pdf, "orni_lab_analyse_csv.pdf", "application/pdf")

    learning_notes(
        "Une analyse exploratoire sert à formuler des hypothèses, pas à conclure définitivement.",
        "Les résultats dépendent de la qualité du fichier : unités, valeurs manquantes, doublons et protocole d'échantillonnage.",
        "Identifie une variable biologique cible, puis teste si elle varie selon l'habitat, le site ou l'année.",
    )
