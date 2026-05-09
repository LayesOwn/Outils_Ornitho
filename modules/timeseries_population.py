from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from core.export import build_pdf_report
from utils.ui import csv_template_button, explain, learning_notes, module_intro, section, style_figure, teacher_note


def simulate_population_series(n_years: int, n0: int, trend_r: float, sd_noise: float, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    years = np.arange(1, n_years + 1)
    true_n = n0 * np.exp(trend_r * (years - 1))
    noise = rng.normal(0, sd_noise, n_years)
    observed = np.maximum(0, np.round(true_n * (1.0 + noise))).astype(int)
    return pd.DataFrame({"Annee": years, "Effectif": observed, "Tendance_vraie": true_n.round(1)})


def mann_kendall_test(series: np.ndarray) -> dict[str, float | str]:
    n = len(series)
    s = 0.0
    for i in range(n - 1):
        s += float(np.sum(np.sign(series[i + 1:] - series[i])))
    var_s = n * (n - 1) * (2 * n + 5) / 18.0
    z = (s - np.sign(s)) / np.sqrt(var_s) if s != 0.0 else 0.0
    p_value = float(2.0 * (1.0 - stats.norm.cdf(abs(z))))
    if p_value < 0.05:
        trend = "croissante" if s > 0 else "déclinante"
    else:
        trend = "stable (non significative)"
    return {"S": s, "z": round(float(z), 3), "pvalue": round(p_value, 4), "trend": trend}


def moving_average(series: np.ndarray, window: int) -> np.ndarray:
    result = np.full(len(series), np.nan)
    for i in range(window - 1, len(series)):
        result[i] = float(np.mean(series[i - window + 1: i + 1]))
    return result


def render(context: dict) -> None:
    is_data = context.get("data") is not None
    section("Séries temporelles de population", "Détecter une tendance dans un suivi annuel d'oiseaux.")
    module_intro(
        "Une série temporelle de population suit l'évolution de l'abondance d'une espèce sur plusieurs années consécutives.",
        "Elle sert à détecter des déclins ou des reprises, à évaluer l'efficacité d'une mesure de conservation et à produire une alerte précoce.",
        "En ornithologie, les programmes STOC, BBS ou LPO produisent ces séries ; distinguer la tendance du bruit de comptage est indispensable.",
    )

    left, right = st.columns([0.9, 1.55])

    if context.get("data") is not None:
        data_src = context["data"]
        numeric_cols = context["numeric_columns"]
        if len(numeric_cols) < 2:
            st.warning("Le fichier doit contenir au moins une colonne année et une colonne abondance.")
            return
        with left:
            csv_template_button(
                pd.DataFrame({"Annee": [2015, 2016, 2017, 2018, 2019, 2020], "Effectif": [480, 453, 421, 398, 375, 352]}),
                "template_serie_temporelle.csv",
            )
            year_col = st.selectbox("Colonne année", numeric_cols)
            count_col = st.selectbox("Colonne abondance", [c for c in numeric_cols if c != year_col])
            agg_func = st.radio("Agrégation par année", ["Somme", "Moyenne"], horizontal=True)
            window = st.slider("Fenêtre de lissage (années)", 2, 7, 3)
        agg = "sum" if agg_func == "Somme" else "mean"
        yearly = data_src[[year_col, count_col]].dropna()
        yearly = yearly.groupby(year_col)[count_col].agg(agg).reset_index()
        yearly = yearly.sort_values(year_col)
        data = yearly.rename(columns={year_col: "Annee", count_col: "Effectif"})
        data["Annee"] = data["Annee"].astype(int)
        trend_r = None
    else:
        with left:
            n_years = st.slider("Durée du suivi (années)", 5, 40, 20)
            n0 = st.slider("Effectif de départ", 50, 5000, 500)
            trend_r = st.slider("Tendance annuelle réelle r", -0.15, 0.10, -0.04, step=0.005, format="%.3f")
            sd_noise = st.slider("Variabilité interannuelle (CV)", 0.05, 0.60, 0.20, step=0.01)
            window = st.slider("Fenêtre de lissage (années)", 2, 7, 3)
            seed = st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=44)
        data = simulate_population_series(n_years, n0, trend_r, sd_noise, int(seed))
    trend_lin = stats.linregress(data["Annee"], data["Effectif"])
    mk = mann_kendall_test(data["Effectif"].values)
    smoothed = moving_average(data["Effectif"].values, window)
    lin_fit = trend_lin.intercept + trend_lin.slope * data["Annee"]

    with right:
        fig = go.Figure()
        fig.add_scatter(
            x=data["Annee"], y=data["Effectif"],
            mode="lines+markers", name="Observations",
            line={"width": 2}, marker={"size": 6},
        )
        fig.add_scatter(
            x=data["Annee"], y=smoothed,
            mode="lines", name=f"Lissage {window} ans",
            line={"width": 3, "dash": "dash"},
        )
        fig.add_scatter(
            x=data["Annee"], y=lin_fit,
            mode="lines", name="Régression linéaire",
            line={"width": 2, "dash": "dot"},
        )
        fig.update_layout(xaxis_title="Année de suivi", yaxis_title="Effectif observé", hovermode="x unified")
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    if trend_r is not None:
        annual_pct = 100.0 * (np.exp(trend_r) - 1.0)
        c1.metric("Tendance vraie r", f"{trend_r:+.3f}", f"{annual_pct:+.1f} % / an")
    else:
        c1.metric("Années", f"{len(data)}")
    c2.metric("Pente OLS", f"{trend_lin.slope:+.1f}", f"R² = {trend_lin.rvalue ** 2:.2f}")
    c3.metric("Mann-Kendall z", f"{mk['z']:+.3f}", f"p = {mk['pvalue']:.3f}")
    c4.metric("Tendance MK", str(mk["trend"]))

    if trend_r is not None:
        annual_pct = 100.0 * (np.exp(trend_r) - 1.0)
        direction = "déclinante" if trend_r < -0.005 else "croissante" if trend_r > 0.005 else "stable"
        explain(
            f"La tendance simulée est {direction} (r = {trend_r:+.3f}, soit {annual_pct:+.1f} % par an). "
            f"Le test de Mann-Kendall détecte une tendance {mk['trend']} (z = {mk['z']:.3f}, p = {mk['pvalue']:.3f})."
        )
    else:
        explain(
            f"Série de {len(data)} années. "
            f"Le test de Mann-Kendall détecte une tendance {mk['trend']} (z = {mk['z']:.3f}, p = {mk['pvalue']:.3f})."
        )
    teacher_note(
        "OLS suppose un déclin linéaire de l'effectif brut. Une régression sur log(effectif) suppose un taux "
        "de changement constant — plus cohérent avec un r biologique. Mann-Kendall est non paramétrique et "
        "robuste aux valeurs aberrantes et aux distributions non normales.",
        context,
    )
    learning_notes(
        "Un déclin de 3 % par an donne une réduction de 50 % en 23 ans.",
        "Mann-Kendall ne localise pas la rupture ; pour détecter quand le changement a commencé, utiliser un test de rupture (Pettitt, CUSUM).",
        None if is_data else "Augmente la variabilité interannuelle : à partir de quel CV le déclin simulé n'est-il plus détectable ?",
    )

    with st.expander("Voir la série complète"):
        st.dataframe(data, use_container_width=True)

    st.download_button(
        "Exporter la série CSV",
        data.to_csv(index=False).encode("utf-8"),
        "orni_lab_serie_temporelle.csv",
        "text/csv",
    )
    if is_data:
        pdf_lines = [
            f"Suivi de {len(data)} ans.",
            f"Regression OLS : pente = {trend_lin.slope:+.1f}, R2 = {trend_lin.rvalue ** 2:.2f}.",
            f"Mann-Kendall : z = {mk['z']:.3f}, p = {mk['pvalue']:.4f}, tendance {mk['trend']}.",
        ]
    else:
        annual_pct = 100.0 * (np.exp(trend_r) - 1.0)
        pdf_lines = [
            f"Suivi de {n_years} ans. N0 = {n0}. Tendance vraie r = {trend_r:+.3f} ({annual_pct:+.1f} %/an).",
            f"Regression OLS : pente = {trend_lin.slope:+.1f}, R2 = {trend_lin.rvalue ** 2:.2f}.",
            f"Mann-Kendall : z = {mk['z']:.3f}, p = {mk['pvalue']:.4f}, tendance {mk['trend']}.",
        ]
    pdf = build_pdf_report("ORNI-LAB - Series temporelles", pdf_lines)
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_serie_temporelle.pdf", "application/pdf")
