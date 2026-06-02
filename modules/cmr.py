from __future__ import annotations

import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.export import build_pdf_report
from data.examples import CMR_SCENARIOS
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


def lincoln_petersen(marked: int, captured: int, recaptured: int) -> tuple[float, float, float]:
    estimate = ((marked + 1) * (captured + 1) / (recaptured + 1)) - 1
    variance = (
        (marked + 1)
        * (captured + 1)
        * (marked - recaptured)
        * (captured - recaptured)
        / (((recaptured + 1) ** 2) * (recaptured + 2))
    )
    se = math.sqrt(max(variance, 0))
    return estimate, max(0, estimate - 1.96 * se), estimate + 1.96 * se


def render(context: dict) -> None:
    is_data = context.get("data") is not None
    section(
        "Capture-Marquage-Recapture",
        "Estimateur de Lincoln-Petersen avec correction de Chapman.",
    )
    module_intro(
        "La capture-marquage-recapture estime la taille d'une population à partir du nombre d'individus marqués puis retrouvés lors d'une seconde capture.",
        "Elle est utilisée quand il est impossible de compter tous les individus directement, notamment dans des populations mobiles ou partiellement détectables.",
        "Pour les oiseaux, elle sert à estimer l'abondance, la survie apparente, la fidélité au site et la dynamique de populations baguées.",
    )
    teacher_objectives(
        [
            "Appliquer l'estimateur de Lincoln-Petersen N̂ = M·C/R et savoir quand préférer la correction de Chapman (R faible).",
            "Calculer l'intervalle de confiance et relier sa largeur au taux de recapture.",
            "Énoncer et vérifier les 4 hypothèses (population fermée, mélange homogène, marques permanentes, captures équiprobables).",
            "Distinguer populations fermées (Lincoln-Petersen, Chapman, Schnabel) et ouvertes (Jolly-Seber, CJS, robust design de Pollock).",
            "Comprendre que le CJS estime une survie apparente φ (survie × fidélité au site), pas la survie vraie.",
        ],
        context,
    )

    if is_data:
        data_src = context["data"]
        numeric_cols = context["numeric_columns"]
        if len(numeric_cols) < 3:
            data_incompatible(
                "Ce module nécessite au moins 3 colonnes numériques représentant les effectifs de chaque session CMR : individus marqués (M), individus capturés en session 2 (C), et marqués recapturés (R).",
                [
                    "Préparez un tableau avec au moins trois colonnes numériques : M (marquages), C (captures totales), R (recaptures de marqués).",
                    "Chaque ligne peut représenter une session, une espèce ou un site différent.",
                    "Vérifiez que R ≤ M et R ≤ C — des valeurs incohérentes donneront des estimations aberrantes.",
                    "Téléchargez l'exemple CSV pour voir la structure attendue.",
                ],
            )
            return

        col1, col2 = st.columns([0.85, 1.4])
        with col1:
            csv_template_button(
                pd.DataFrame({
                    "Session": ["Mésange 2022", "Mésange 2023", "Merle 2022"],
                    "Marquages_M": [45, 52, 80],
                    "Captures_C": [38, 41, 65],
                    "Recaptures_R": [12, 15, 20],
                }),
                "template_cmr.csv",
            )
            cat_cols = context["categorical_columns"]
            label_col = st.selectbox("Colonne d'étiquettes (optionnel)", ["—"] + cat_cols)
            m_col = st.selectbox("Colonne Marquages (M)", numeric_cols)
            remaining = [c for c in numeric_cols if c != m_col]
            c_col = st.selectbox("Colonne Captures totales (C)", remaining)
            remaining2 = [c for c in remaining if c != c_col]
            r_col = st.selectbox("Colonne Recaptures de marqués (R)", remaining2)

        rows = data_src[[m_col, c_col, r_col]].dropna()
        rows = rows[(rows[m_col] > 0) & (rows[c_col] > 0) & (rows[r_col] > 0)]
        rows = rows[rows[r_col] <= rows[[m_col, c_col]].min(axis=1)]

        if len(rows) == 0:
            st.error("Aucune ligne valide (M > 0, C > 0, R > 0, R ≤ min(M, C)). Vérifiez vos données et la sélection des colonnes.")
            return

        results_rows = []
        for idx in rows.index:
            m_val = int(rows.loc[idx, m_col])
            c_val = int(rows.loc[idx, c_col])
            r_val = int(rows.loc[idx, r_col])
            n_est, low, high = lincoln_petersen(m_val, c_val, r_val)
            label = str(data_src.loc[idx, label_col]) if label_col != "—" and label_col in data_src.columns else f"Ligne {idx + 1}"
            results_rows.append({
                "Session": label,
                "M": m_val, "C": c_val, "R": r_val,
                "N̂": round(n_est), "IC95 inf.": round(low), "IC95 sup.": round(high),
                "Taux recapture": round(r_val / c_val, 3),
            })
        results_df = pd.DataFrame(results_rows)

        with col2:
            if len(results_df) == 1:
                row = results_df.iloc[0]
                fig = go.Figure()
                fig.add_bar(
                    x=["M", "C", "R", "N̂ estimé"],
                    y=[row["M"], row["C"], row["R"], row["N̂"]],
                    marker_color=["#39d98a", "#4dabf7", "#ff6b6b", "#ffd166"],
                )
                fig.add_trace(go.Scatter(
                    x=["N̂ estimé", "N̂ estimé"],
                    y=[row["IC95 inf."], row["IC95 sup."]],
                    mode="lines+markers", name="IC 95 %",
                ))
                fig.update_layout(yaxis_title="Individus", showlegend=True)
                style_figure(fig)
                st.plotly_chart(fig, use_container_width=True)
            else:
                fig = go.Figure()
                fig.add_scatter(
                    x=results_df["Session"], y=results_df["N̂"],
                    mode="markers+lines", name="N̂", marker={"size": 10, "color": "#ffd166"}, line={"width": 2},
                )
                fig.add_scatter(
                    x=pd.concat([results_df["Session"], results_df["Session"].iloc[::-1]]),
                    y=pd.concat([results_df["IC95 sup."], results_df["IC95 inf."].iloc[::-1]]),
                    fill="toself", fillcolor="rgba(255,209,102,0.15)",
                    line={"color": "rgba(0,0,0,0)"}, name="IC 95 %",
                )
                fig.update_layout(xaxis_title="Session", yaxis_title="Abondance estimée N̂")
                style_figure(fig)
                st.plotly_chart(fig, use_container_width=True)

        st.dataframe(results_df, use_container_width=True)
        n_mean = results_df["N̂"].mean()
        rate_mean = results_df["Taux recapture"].mean()
        explain(
            f"{len(results_df)} session(s) analysée(s). "
            f"Abondance estimée moyenne : {n_mean:,.0f} individus. "
            f"Taux de recapture moyen : {100 * rate_mean:.1f} %."
        )

        low_rate = results_df[results_df["Taux recapture"] < 0.10]
        if len(low_rate) > 0:
            st.warning(
                f"{len(low_rate)} session(s) avec un taux de recapture < 10 % : l'estimation N̂ est très imprécise. "
                "Augmentez l'effort de recapture ou vérifiez les données."
            )
        incoherent = results_df[(results_df["R"] > results_df["M"]) | (results_df["R"] > results_df["C"])]
        if len(incoherent) > 0:
            st.error("Certaines lignes ont R > M ou R > C, ce qui est biologiquement impossible. Vérifiez vos données.")

        pdf_lines = [f"Sessions analysées : {len(results_df)}. N̂ moyen = {n_mean:.0f}. Taux recapture moyen = {100*rate_mean:.1f}%."]
        for _, row in results_df.iterrows():
            pdf_lines.append(f"  {row['Session']} : M={row['M']}, C={row['C']}, R={row['R']}, N̂={row['N̂']} IC95[{row['IC95 inf.']}; {row['IC95 sup.']}].")
        st.download_button("Exporter les résultats CSV", results_df.to_csv(index=False).encode("utf-8"), "orni_lab_cmr.csv", "text/csv")

    else:
        scenario_name = st.selectbox("Exemple ornithologique", list(CMR_SCENARIOS.keys()))
        scenario = CMR_SCENARIOS[scenario_name]
        col1, col2 = st.columns([0.8, 1.4])
        with col1:
            marked = st.slider("Individus marqués M", 10, 1000, scenario["marked"])
            captured = st.slider("Individus capturés C", 10, 1000, scenario["captured"])
            recaptured = st.slider("Marqués recapturés R", 1, min(marked, captured), min(scenario["recaptured"], min(marked, captured)))

        estimate, low, high = lincoln_petersen(marked, captured, recaptured)
        with col2:
            fig = go.Figure()
            fig.add_bar(
                x=["M", "C", "R", "N estimé"],
                y=[marked, captured, recaptured, estimate],
                marker_color=["#39d98a", "#4dabf7", "#ff6b6b", "#ffd166"],
            )
            fig.add_trace(go.Scatter(
                x=["N estimé", "N estimé"],
                y=[low, high],
                mode="lines+markers", name="IC 95 %",
            ))
            fig.update_layout(yaxis_title="Nombre d'individus", showlegend=True)
            style_figure(fig)
            st.plotly_chart(fig, use_container_width=True)

        recapture_rate = recaptured / captured
        st.metric("Abondance estimée", f"{estimate:,.0f}", f"IC95 % [{low:,.0f} ; {high:,.0f}]")
        explain(
            f"Le taux de recapture est de {100 * recapture_rate:.1f} %. "
            "Un faible nombre de recaptures élargit l'incertitude et peut rendre l'estimation instable."
        )
        if recapture_rate < 0.10:
            st.warning("Taux de recapture < 10 % : l'estimation N̂ est très imprécise. L'IC 95 % est large.")
        if recaptured < 7:
            st.info("R < 7 : la correction de Chapman est ici indispensable — l'estimateur LP original serait fortement biaisé positivement.")

        pdf_lines = [
            f"Scénario : {scenario_name}.",
            f"M = {marked}, C = {captured}, R = {recaptured}.",
            f"N estimé = {estimate:.0f}, IC95 % = [{low:.0f}; {high:.0f}].",
            "Interprétation : la précision dépend fortement du taux de recapture.",
        ]

    learning_notes(
        "Plus le taux de recapture est élevé, plus l'estimation est précise.",
        "La méthode est sensible à la perte de marques, aux migrations et aux captures non homogènes.",
        None if is_data else "Diminue R et observe comment l'intervalle de confiance s'élargit.",
    )
    teacher_note(
        "Quatre hypothèses du Lincoln-Petersen : (1) population fermée entre les deux sessions, "
        "(2) mélange homogène des individus marqués dans la population, "
        "(3) marques non perdues, non déposées, détectables, "
        "(4) probabilités de capture identiques pour tous les individus (pas de hétérogénéité). "
        "La correction de Chapman est recommandée quand R < 7 : elle est sans biais alors que l'estimateur original est biaisé positivement. "
        "En population ouverte (sessions multiples), le modèle CJS estime la survie apparente φᵢ et la probabilité de recapture pᵢ. "
        "Jolly-Seber ajoute l'estimation de la taille de population. "
        "Le robust design de Pollock combine des sessions primaires (population ouverte) "
        "et des sessions secondaires rapprochées (population fermée) pour estimer φ, p, et N simultanément.",
        context,
    )
    teacher_formula(
        "Estimateurs Lincoln-Petersen et Chapman (Chap. 6, ORNI 422)",
        r"\hat{N} = \frac{M \cdot C}{R} \quad\text{(LP original)}"
        r"\qquad \hat{N}_C = \frac{(M+1)(C+1)}{R+1} - 1 \quad\text{(Chapman, sans biais)}",
        context,
    )
    teacher_formula(
        "Variance et intervalle de confiance de Chapman",
        r"\widehat{\mathrm{Var}}(\hat{N}_C) = \frac{(M+1)(C+1)(M-R)(C-R)}{(R+1)^2\,(R+2)}"
        r"\qquad \mathrm{IC}_{95\%} = \hat{N}_C \pm 1{,}96\,\hat{\sigma}",
        context,
    )
    teacher_pitfalls(
        [
            "Appliquer Lincoln-Petersen sur une population ouverte : si des individus naissent, meurent ou migrent entre M et C, N est surestimé.",
            "Ignorer la perte de bagues : si des bagues tombent entre les sessions, R est sous-estimé et N surestimé.",
            "Confondre φ (survie apparente CJS) et la survie vraie : φ = survie × fidélité au site — la dispersion est confondue avec la mortalité.",
            "Utiliser l'estimateur LP original quand R < 7 sans correction Chapman : biais positif important.",
            "Croire que le taux de recapture observé (R/C) est la probabilité de recapture p : ils coïncident seulement si toutes les hypothèses sont vérifiées.",
        ],
        context,
    )
    teacher_summary(
        [
            "Principe : la proportion de marqués dans la recapture reflète celle de la population → <strong>M/N = R/C</strong> ⇒ N̂ = M·C/R.",
            "Toujours préférer la <strong>correction de Chapman</strong> N̂ = (M+1)(C+1)/(R+1) − 1 (sans biais, surtout si R &lt; 10).",
            "La précision dépend du <strong>taux de recapture</strong> : R faible → IC très large.",
            "4 hypothèses du modèle fermé ; leur violation (population ouverte, perte de bagues, trap-happiness) biaise N̂.",
            "Population ouverte → <strong>CJS</strong> (survie apparente φ et p) ; <strong>Jolly-Seber</strong> ajoute N ; <strong>robust design</strong> estime N, φ et l'émigration temporaire.",
        ],
        context,
        reference="ORNI 422 — Chap. 6 : Méthodes d'estimation (CMR)",
    )

    pdf = build_pdf_report("ORNI-LAB - Capture-Marquage-Recapture", pdf_lines)
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_cmr.pdf", "application/pdf")
