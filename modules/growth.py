from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats
from scipy.optimize import curve_fit

from core.export import build_pdf_report
from utils.ui import csv_template_button, data_incompatible, explain, learning_notes, module_intro, section, style_figure, teacher_formula, teacher_note, teacher_pitfalls


def simulate_growth(n0: float, r: float, k: float, years: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if n0 <= 0 or k <= 0 or years < 0:
        raise ValueError("Invalid parameters")
    t = np.arange(years + 1)
    exponential = n0 * np.exp(r * t)
    logistic = np.empty(years + 1, dtype=float)
    logistic[0] = n0
    lam = np.exp(r)
    for year in range(years):
        c = logistic[year]
        logistic[year + 1] = (k * c * lam) / (k + c * (lam - 1))
    return t, exponential, logistic


def _logistic_analytical(t: np.ndarray, n0: float, r: float, k: float) -> np.ndarray:
    ratio = (k - max(float(n0), 1e-6)) / max(float(n0), 1e-6)
    denom = 1.0 + ratio * np.exp(-r * t)
    return np.where(np.abs(denom) > 1e-10, k / denom, float(k))


def fit_logistic(t_obs: np.ndarray, n_obs: np.ndarray) -> dict:
    t_norm = (t_obs - t_obs[0]).astype(float)
    n_max = float(n_obs.max())
    n0_init = float(n_obs[0])
    r_init = 0.08 if float(n_obs[-1]) >= float(n_obs[0]) else -0.05
    k_init = n_max * 1.5 if float(n_obs[-1]) >= float(n_obs[0]) else n_max
    try:
        popt, _ = curve_fit(
            _logistic_analytical, t_norm, n_obs,
            p0=[n0_init, r_init, k_init],
            bounds=([1.0, -3.0, 1.0], [n_max * 10, 3.0, n_max * 50]),
            maxfev=20000,
        )
        n0_fit, r_fit, k_fit = popt
        n_pred = _logistic_analytical(t_norm, n0_fit, r_fit, k_fit)
        ss_res = float(np.sum((n_obs - n_pred) ** 2))
        ss_tot = float(np.sum((n_obs - n_obs.mean()) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
        return {"n0": round(float(n0_fit), 1), "r": round(float(r_fit), 4), "k": round(float(k_fit), 1), "r2": round(r2, 3), "success": True}
    except Exception:
        return {"success": False, "r2": 0.0}


def fit_exponential(t_obs: np.ndarray, n_obs: np.ndarray) -> dict:
    t_norm = (t_obs - t_obs[0]).astype(float)
    pos_mask = n_obs > 0
    if pos_mask.sum() < 2:
        return {"n0": float(n_obs[0]), "r": 0.0, "r2": 0.0, "success": False}
    slope, intercept, rvalue, _, _ = stats.linregress(t_norm[pos_mask], np.log(n_obs[pos_mask]))
    return {"n0": round(float(np.exp(intercept)), 1), "r": round(float(slope), 4), "r2": round(float(rvalue ** 2), 3), "success": True}


def render(context: dict) -> None:
    is_data = context.get("data") is not None
    section(
        "Croissance exponentielle et logistique",
        "Exemple : colonie nicheuse suivie pendant plusieurs saisons de reproduction.",
    )
    module_intro(
        "Ces modèles décrivent comment l'effectif d'une population varie au cours du temps. "
        "Le modèle exponentiel suppose une croissance sans limite, alors que le modèle logistique ajoute une capacité de charge K.",
        "Ils servent à comparer des scénarios simples de croissance, de déclin ou de stabilisation et à comprendre le rôle de la densité-dépendance.",
        "En ornithologie, ils aident à interpréter l'évolution d'une colonie, l'effet d'un habitat limité ou le potentiel de récupération après une perturbation.",
    )
    col_controls, col_plot = st.columns([0.9, 1.6])

    if is_data:
        data_src = context["data"]
        numeric_cols = context["numeric_columns"]
        if len(numeric_cols) < 2:
            data_incompatible(
                "Ce module ajuste des modèles de croissance à une série temporelle : il nécessite au moins deux colonnes numériques — une pour les années et une pour les effectifs.",
                [
                    "Vérifiez que votre fichier contient une colonne d'années (ex. : Annee, Year) et une colonne d'abondances (ex. : Effectif, N).",
                    "Si votre fichier ne contient qu'une seule colonne numérique, ajoutez les années correspondantes.",
                    "Assurez-vous que les valeurs ne sont pas formatées comme du texte.",
                    "Téléchargez l'exemple CSV (colonnes Annee / Effectif) pour voir la structure attendue.",
                ],
            )
            return
        with col_controls:
            csv_template_button(
                pd.DataFrame({"Annee": [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019], "Effectif": [120, 145, 178, 210, 248, 285, 315, 340, 360, 372]}),
                "template_croissance.csv",
            )
            year_col = st.selectbox("Colonne année", numeric_cols)
            count_col = st.selectbox("Colonne effectifs", [c for c in numeric_cols if c != year_col])
            show_log = st.radio("Échelle verticale", ["Linéaire", "Logarithmique"], horizontal=True)

        obs_df = data_src[[year_col, count_col]].dropna().sort_values(year_col)
        t_obs = obs_df[year_col].values.astype(float)
        n_obs = obs_df[count_col].values.astype(float)
        n_points = len(t_obs)

        if n_points < 3:
            st.error("Au moins 3 points temporels distincts sont nécessaires pour ajuster un modèle de croissance.")
            return

        fit_exp = fit_exponential(t_obs, n_obs)
        fit_log = fit_logistic(t_obs, n_obs) if n_points >= 5 else {"success": False, "r2": 0.0}

        t_norm = t_obs - t_obs[0]
        t_fine_norm = np.linspace(0, t_norm[-1], 200)
        t_fine_abs = t_fine_norm + t_obs[0]

        with col_plot:
            fig = go.Figure()
            fig.add_scatter(
                x=t_obs, y=n_obs, mode="markers+lines", name="Observations",
                marker={"size": 8, "color": "#ffd166"}, line={"width": 2, "color": "#ffd166"},
            )
            if fit_exp["success"]:
                exp_curve = fit_exp["n0"] * np.exp(fit_exp["r"] * t_fine_norm)
                fig.add_scatter(
                    x=t_fine_abs, y=exp_curve, mode="lines",
                    name=f"Exponentiel (R²={fit_exp['r2']:.2f})",
                    line={"width": 2, "dash": "dot"},
                )
            if fit_log["success"]:
                log_curve = _logistic_analytical(t_fine_norm, fit_log["n0"], fit_log["r"], fit_log["k"])
                fig.add_scatter(
                    x=t_fine_abs, y=log_curve, mode="lines",
                    name=f"Logistique (R²={fit_log['r2']:.2f})",
                    line={"width": 3},
                )
                fig.add_hline(y=fit_log["k"], line_dash="dot", annotation_text=f"K̂ = {fit_log['k']:,.0f}")
            if show_log == "Logarithmique":
                fig.update_yaxes(type="log")
            fig.update_layout(xaxis_title="Année", yaxis_title="Effectif", hovermode="x unified")
            style_figure(fig)
            st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Points", f"{n_points}")
        c2.metric("r̂ exponentiel", f"{fit_exp['r']:+.4f}" if fit_exp["success"] else "—", f"R²={fit_exp['r2']:.2f}" if fit_exp["success"] else "")
        c3.metric("r̂ logistique", f"{fit_log['r']:+.4f}" if fit_log.get("success") else "—", f"R²={fit_log['r2']:.2f}" if fit_log.get("success") else "")
        c4.metric("K̂ estimée", f"{fit_log['k']:,.0f}" if fit_log.get("success") else "—")

        if fit_exp["success"] and fit_log.get("success"):
            if fit_log["r2"] > fit_exp["r2"] + 0.05:
                explain(
                    f"Le modèle logistique (R²={fit_log['r2']:.2f}) s'ajuste mieux que l'exponentiel (R²={fit_exp['r2']:.2f}), "
                    f"suggérant un effet de densité-dépendance avec K̂ ≈ {fit_log['k']:,.0f}."
                )
            else:
                explain(
                    f"Le modèle exponentiel (R²={fit_exp['r2']:.2f}) s'ajuste aussi bien que le logistique — "
                    "la série ne montre pas clairement de plafonnement vers une capacité de charge."
                )
        elif fit_exp["success"]:
            explain(
                f"Ajustement exponentiel : r̂ = {fit_exp['r']:+.4f} (R² = {fit_exp['r2']:.2f}). "
                "Ajoutez ≥ 5 points pour tester le modèle logistique."
            )

        if n_points < 8:
            st.info(f"Série courte ({n_points} points) : les paramètres K̂ et r̂ peuvent être imprécis. Un minimum de 8–10 années améliore la robustesse.")
        if fit_exp["success"] and abs(fit_exp["r"]) < 0.005:
            st.info("Le taux r̂ est très proche de 0 : la population semble stable sur la période.")
        if fit_log.get("success") and fit_log["r"] < 0:
            st.info(f"Le modèle logistique converge vers r̂ < 0 : la population décline vers K̂ = {fit_log['k']:,.0f} (équilibre bas plutôt que capacité de charge classique).")

        pdf_lines = [
            f"Série : {n_points} points ({int(t_obs[0])}–{int(t_obs[-1])}).",
            (f"Ajustement exponentiel : r = {fit_exp['r']:+.4f}, R² = {fit_exp['r2']:.3f}." if fit_exp["success"] else "Ajustement exponentiel non convergé."),
            (f"Ajustement logistique : r = {fit_log['r']:+.4f}, K = {fit_log['k']:,.0f}, R² = {fit_log['r2']:.3f}." if fit_log.get("success") else "Ajustement logistique non convergé ou données insuffisantes."),
        ]
        fit_df = pd.DataFrame({"Annee": t_obs, "Effectif_obs": n_obs})
        if fit_exp["success"]:
            fit_df["Exp_ajuste"] = (fit_exp["n0"] * np.exp(fit_exp["r"] * t_norm)).round(1)
        if fit_log.get("success"):
            fit_df["Log_ajuste"] = _logistic_analytical(t_norm, fit_log["n0"], fit_log["r"], fit_log["k"]).round(1)
        st.download_button("Exporter les données et ajustement CSV", fit_df.to_csv(index=False).encode("utf-8"), "orni_lab_croissance.csv", "text/csv")

    else:
        with col_controls:
            n0 = st.slider("Population initiale N₀", 5, 2000, 120, step=5)
            r = st.slider("Taux intrinsèque r", 0.01, 0.80, 0.18, step=0.01)
            k = st.slider("Capacité de charge K", 50, 100000, 850, step=100)
            years = st.slider("Durée de projection (années)", 5, 80, 35)
            st.markdown("**Affichage du graphique**")
            y_scale = st.radio("Échelle verticale", ["Logarithmique", "Linéaire"], horizontal=True)
            y_zoom = st.slider("Zoom vertical", 1, 100, 100, help="Réduit la hauteur maximale affichée pour mieux voir les faibles effectifs.")

        t, exponential, logistic = simulate_growth(n0, r, k, years)
        results = pd.DataFrame({"Année": t, "Exponentiel": exponential, "Logistique": logistic})

        with col_plot:
            fig = go.Figure()
            fig.add_scatter(x=t, y=exponential, name="Exponentiel", mode="lines", line={"width": 3})
            fig.add_scatter(x=t, y=logistic, name="Logistique", mode="lines", line={"width": 3})
            fig.add_hline(y=k, line_dash="dot", annotation_text="K")
            max_displayed = max(float(np.max(exponential)), float(np.max(logistic)), float(k))
            upper_limit = max(1.0, max_displayed * y_zoom / 100)
            if y_scale == "Logarithmique":
                positive_values = np.concatenate([exponential[exponential > 0], logistic[logistic > 0], np.array([k])])
                lower_limit = max(0.1, float(np.min(positive_values)) * 0.8)
                fig.update_yaxes(type="log", range=[np.log10(lower_limit), np.log10(max(upper_limit, lower_limit * 10))])
            else:
                fig.update_yaxes(type="linear", range=[0, upper_limit])
            fig.update_xaxes(rangeslider={"visible": True})
            fig.update_layout(xaxis_title="Années", yaxis_title="Effectif projeté", hovermode="x unified", legend_title="Modèle")
            style_figure(fig)
            st.plotly_chart(fig, use_container_width=True)

        final_exp = float(exponential[-1])
        final_log = float(logistic[-1])
        annual_pct = 100.0 * (np.exp(r) - 1.0)
        explain(
            f"La population suit une croissance potentielle r = {r:.2f} ({annual_pct:+.1f} %/an). "
            f"Le modèle exponentiel atteint {final_exp:,.0f} individus, alors que "
            f"le modèle logistique s'ajuste vers K = {k:,.0f} avec {final_log:,.0f} individus."
        )
        pdf_lines = [
            f"N0 = {n0}, r = {r:.2f}, K = {k}, horizon = {years} ans.",
            f"Effectif final exponentiel : {final_exp:.0f}.",
            f"Effectif final logistique : {final_log:.0f}.",
            "Interprétation : la densité-dépendance limite la croissance lorsque l'effectif approche K.",
        ]
        st.download_button("Exporter les données CSV", results.to_csv(index=False).encode("utf-8"), "orni_lab_croissance.csv", "text/csv")

    learning_notes(
        "La capacité de charge empêche une croissance illimitée.",
        "Ces modèles ne représentent pas explicitement l'âge, la météo, la dispersion ou les catastrophes.",
        None if is_data else "Diminue K et observe à partir de quand la courbe logistique se stabilise.",
    )
    teacher_note(
        "Relation taux : r (instantané, continu) et λ (discret, annuel) sont liés par r = ln(λ), λ = eʳ. "
        "Le taux r = b − d (natalité − mortalité instantanées). "
        "La croissance logistique atteint son maximum de dN/dt lorsque N = K/2 : "
        "c'est le rendement maximal soutenu MSY = rK/4, concept central en gestion des populations exploitées. "
        "L'effet Allee désigne un mécanisme de rétroaction positive à faible effectif (coopération reproductrice, "
        "détection des prédateurs) : en dessous du seuil A, dN/dt < 0 malgré N > 0, "
        "ce qui crée un risque d'extinction même sans surexploitation.",
        context,
    )
    teacher_formula(
        "Croissance exponentielle et logistique — formes différentielles",
        r"\frac{dN}{dt} = rN \quad\text{(exponentiel)}"
        r"\qquad \frac{dN}{dt} = rN\!\left(1 - \frac{N}{K}\right) \quad\text{(logistique)}",
        context,
    )
    teacher_formula(
        "Rendement maximal soutenu (MSY) — gestion des populations exploitées",
        r"N^* = \frac{K}{2} \;\Rightarrow\; \left.\frac{dN}{dt}\right|_{\max} = \frac{rK}{4} = \text{MSY}",
        context,
    )
    teacher_formula(
        "Effet Allee — modèle logistique avec seuil A",
        r"\frac{dN}{dt} = rN\!\left(1 - \frac{N}{K}\right)\!\left(\frac{N}{A} - 1\right) \quad (A < K)",
        context,
    )
    teacher_pitfalls(
        [
            "Confondre r (taux instantané continu) et λ (taux discret annuel) : r = ln(λ) et λ = eʳ, ils ne sont pas égaux.",
            "Croire que N₀ < K garantit la convergence vers K : si r < 0, la population décline vers 0 quelle que soit la valeur initiale.",
            "Interpréter K comme une constante biologique : K dépend de l'habitat, de la saison et peut évoluer avec le climat.",
            "Confondre MSY (N = K/2) avec l'équilibre K : exploiter jusqu'à K/2 maximise le prélèvement soutenu, pas l'effectif.",
            "Négliger l'effet Allee dans les petites populations fragmentées : le modèle logistique simple prédit une récupération même à N très faible, ce qui surestime la résilience.",
        ],
        context,
    )

    pdf = build_pdf_report("ORNI-LAB - Croissance", pdf_lines)
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_croissance.pdf", "application/pdf")
