from __future__ import annotations

import plotly.express as px
import streamlit as st

from core.export import build_pdf_report
try:
    from simulations.pva_engine import simulate_pva, summarize_pva
except ImportError as _pva_err:
    simulate_pva = None  # type: ignore[assignment]
    summarize_pva = None  # type: ignore[assignment]
    _PVA_IMPORT_ERROR = str(_pva_err)
else:
    _PVA_IMPORT_ERROR = ""
from utils.ui import explain, learning_notes, module_intro, section, style_figure, teacher_formula, teacher_note, teacher_pitfalls


@st.cache_data
def _run_pva(n0, mean_r, sd_r, k, years, iterations, threshold, loss, seed):
    return simulate_pva(n0, mean_r, sd_r, k, years, iterations, threshold, loss, seed)


def render(context: dict) -> None:
    if _PVA_IMPORT_ERROR:
        st.error(f"Module PVA non disponible : {_PVA_IMPORT_ERROR}")
        return
    section("PVA et conservation", "Analyse de viabilité de population avec incertitude environnementale.")
    module_intro(
        "Une PVA simule de nombreuses trajectoires possibles d'une population afin d'estimer son risque de quasi-extinction.",
        "Elle sert à comparer des scénarios de conservation quand l'avenir est incertain : démographie, habitat, mortalité ou climat.",
        "En ornithologie de conservation, elle aide à prioriser les actions pour les espèces menacées, colonies isolées ou populations réintroduites.",
    )

    left, right = st.columns([0.9, 1.55])
    with left:
        n0 = st.slider("Effectif initial", 10, 2000, 180)
        mean_r = st.slider("Croissance moyenne r", -0.25, 0.35, 0.04, step=0.01)
        sd_r = st.slider("Variabilité environnementale", 0.0, 0.30, 0.09, step=0.01)
        k = st.slider("Capacité de charge", 50, 100000, 900, step=100)
        threshold = st.slider("Seuil de quasi-extinction", 1, 200, 25)
        loss = st.slider("Pertes annuelles fixes", 0, 100, 6)
        years = st.slider("Horizon", 10, 100, 50)
        iterations = st.slider("Nombre de simulations", 50, 1000, 250, step=50)
        seed = int(st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=42) or 42)

    data = _run_pva(n0, mean_r, sd_r, k, years, iterations, threshold, loss, int(seed))
    summary = summarize_pva(data, threshold)
    yearly = data.groupby("annee")["effectif"].quantile([0.05, 0.5, 0.95]).unstack().reset_index()
    yearly.columns = ["Année", "P05", "Médiane", "P95"]

    with right:
        fig = px.line(yearly, x="Année", y=["P05", "Médiane", "P95"], labels={"value": "Effectif", "variable": "Quantile"})
        fig.add_hline(y=threshold, line_dash="dot", annotation_text="Seuil")
        fig.update_traces(line={"width": 3})
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Risque quasi-extinction", f"{100 * summary['risk']:.1f} %")
    c2.metric("Médiane finale", f"{summary['median_final']:.0f}")
    c3.metric("Moyenne finale", f"{summary['mean_final']:.0f}")
    level = "élevé" if summary["risk"] > 0.3 else "modéré" if summary["risk"] > 0.1 else "faible"
    explain(f"Le risque estimé est {level} : {100 * summary['risk']:.1f} % des trajectoires atteignent le seuil de quasi-extinction.")
    teacher_note(
        "Cette PVA simule des trajectoires stochastiques N(t+1) = N(t)·exp(r̄ + εₜ) avec εₜ ~ N(0, σ²ₑ). "
        "Deux sources de stochasticité : (1) stochasticité démographique (variance binomiale des naissances/décès, "
        "proportionnelle à 1/√N — critique pour N < 50) ; (2) stochasticité environnementale (variance inter-annuelle de r, "
        "σ²ₑ — domine pour les grandes populations). "
        "Règle MVP de Franklin (1980) : 50 individus évitent la dépression de consanguinité à court terme ; "
        "500 maintiennent le potentiel évolutif (Ne/N ≈ 0,1 pour les oiseaux). "
        "Révisée à 100/1000 par Frankham (2014) pour tenir compte des effets génétiques à long terme. "
        "Continuum slow-fast : espèces 'slow' (rapaces, albatros — longue durée de vie, faible fécondité) "
        "ont λ très sensible à la survie adulte ; espèces 'fast' (passereaux annuels) plus sensibles aux fécondités. "
        "Modèle de Levins : f* = 1 − e/c (fraction de parcelles occupées à l'équilibre) — "
        "métapopulation viable seulement si c > e.",
        context,
    )
    teacher_formula(
        "Modèle stochastique discret (base de la PVA pédagogique)",
        r"N(t+1) = \max\!\Bigl(0,\;\min\!\bigl(K,\;N(t)\cdot e^{\bar{r}+\varepsilon_t} - \text{pertes}\bigr)\Bigr)"
        r"\qquad \varepsilon_t \sim \mathcal{N}(0,\,\sigma_e^2)",
        context,
    )
    teacher_formula(
        "Modèle de métapopulation de Levins (Chap. 7, ORNI 422)",
        r"\frac{df}{dt} = c\,f\,(1-f) - e\,f \qquad f^* = 1 - \frac{e}{c}",
        context,
    )
    teacher_formula(
        "Règle MVP — Franklin (1980) révisée Frankham (2014)",
        r"\text{MVP}_{\text{court terme}} = 50\;\text{ind.}\;(\text{consanguinité})"
        r"\qquad \text{MVP}_{\text{long terme}} = 500{-}1000\;\text{ind.}\;(\text{potentiel évolutif})",
        context,
    )
    teacher_pitfalls(
        [
            "Traiter le risque estimé par PVA comme une probabilité précise : l'incertitude sur r̄ et σ peut facilement doubler ou tripler ce risque.",
            "Confondre stochasticité démographique (variance des événements individuels) et environnementale (variance inter-annuelle de r) : effets très différents selon la taille de population.",
            "Oublier la consanguinité et les effets génétiques dans une PVA simple : ils amplifient le risque d'extinction pour N < 50.",
            "Interpréter 'risque = 0 %' comme 'population sûre' : sur un court horizon de simulation, les événements rares ne se produisent pas encore.",
            "Appliquer la règle 50/500 sans tenir compte de l'espèce : la dispersion, le sex-ratio et la structure sociale modifient fortement la taille efficace Ne.",
        ],
        context,
    )
    learning_notes(
        "Le risque dépend autant de la variance que de la croissance moyenne.",
        "Une PVA simplifiée peut sous-estimer les événements rares, la consanguinité ou les catastrophes.",
        "Teste l'effet d'une baisse des pertes annuelles fixes sur le risque.",
    )

    st.download_button("Exporter les trajectoires CSV", data.to_csv(index=False).encode("utf-8"), "orni_lab_pva.csv", "text/csv")
    pdf = build_pdf_report(
        "ORNI-LAB - PVA et conservation",
        [f"Risque = {100 * summary['risk']:.1f} %. Médiane finale = {summary['median_final']:.0f}. Paramètres : N0={n0}, r={mean_r:.2f}, sd={sd_r:.2f}, K={k}."],
    )
    if pdf:
        st.download_button("Exporter le résumé PDF", pdf, "orni_lab_pva.pdf", "application/pdf")
