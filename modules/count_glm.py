from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from core.export import build_pdf_report
from utils.ui import csv_template_button, explain, learning_notes, module_intro, section, style_figure, teacher_formula, teacher_note, teacher_pitfalls

_HABITATS = ["Forêt", "Savane", "Zone humide", "Agroécosystème"]
_HAB_EFFECTS = {"Forêt": 1.4, "Savane": 0.8, "Zone humide": 1.8, "Agroécosystème": 0.5}


def simulate_count_data(
    n_sites: int,
    n_years: int,
    mean_count: float,
    year_trend: float,
    overdispersion: float,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    years = np.arange(2010, 2010 + n_years)
    rows = []
    for year in years:
        for _ in range(n_sites):
            hab = rng.choice(_HABITATS)
            effort = int(rng.integers(1, 5))
            mu = mean_count * _HAB_EFFECTS[hab] * np.exp(year_trend * (year - 2010)) * effort
            if overdispersion <= 1.05:
                count = int(rng.poisson(max(mu, 1e-6)))
            else:
                alpha = overdispersion - 1.0
                r = max(0.05, mu / alpha)
                p_nb = r / (r + mu)
                count = int(rng.negative_binomial(r, p_nb))
            rows.append({"Annee": int(year), "Habitat": hab, "Effort": effort, "Abondance": max(0, count)})
    return pd.DataFrame(rows)


def _fit_glm(data: pd.DataFrame, family_name: str) -> dict:
    try:
        import statsmodels.api as sm
        import statsmodels.formula.api as smf
    except ImportError:
        return {"error": "statsmodels non disponible — installez-le avec : pip install statsmodels"}

    offset = np.log(data["Effort"].clip(lower=1).astype(float)).values
    formula = "Abondance ~ C(Habitat) + Annee"

    try:
        if family_name == "Poisson":
            result = smf.glm(formula, data=data, family=sm.families.Poisson(), offset=offset).fit(disp=False)
            overdispersion_ratio = round(result.pearson_chi2 / result.df_resid, 3) if result.df_resid > 0 else float("nan")
        else:
            result = smf.negativebinomial(formula, data=data, offset=offset).fit(
                disp=False, method="nm", maxiter=500
            )
            overdispersion_ratio = float("nan")

        ci = result.conf_int()
        coef_table = pd.DataFrame({
            "IRR": np.exp(result.params).round(3),
            "IC 2.5 %": np.exp(ci.iloc[:, 0]).round(3),
            "IC 97.5 %": np.exp(ci.iloc[:, 1]).round(3),
            "p-value": result.pvalues.round(4),
        })
        pearson_resid = result.resid_pearson if hasattr(result, "resid_pearson") else None
        fitted = result.fittedvalues.values if hasattr(result, "fittedvalues") else None
        return {
            "coef_table": coef_table,
            "aic": round(float(result.aic), 1),
            "overdispersion": overdispersion_ratio,
            "pearson_resid": pearson_resid,
            "fitted": fitted,
        }
    except Exception as exc:
        return {"error": f"Échec d'ajustement ({family_name}) : {exc}"}


def render(context: dict) -> None:
    is_data = context.get("data") is not None
    section("GLM pour données de comptage", "Poisson et binomial négatif avec habitat, tendance et effort.")
    module_intro(
        "Un GLM de Poisson modélise des comptages entiers en supposant que la variance égale la moyenne. Quand la variance la dépasse (surdispersion), le binomial négatif est plus adapté.",
        "Il permet de contrôler simultanément pour l'habitat, l'effort d'échantillonnage et la tendance temporelle, contrairement aux tests t qui supposent la normalité.",
        "En ornithologie, les comptages sur points d'écoute sont rarement normaux ; le GLM Poisson ou binomial négatif est le standard pour modéliser l'abondance.",
    )

    left, right = st.columns([0.9, 1.55])

    if context.get("data") is not None:
        data_src = context["data"]
        numeric_cols = context["numeric_columns"]
        cat_cols = context["categorical_columns"]
        if not numeric_cols:
            st.warning("Le fichier ne contient pas de colonne numérique exploitable.")
            return
        with left:
            csv_template_button(
                pd.DataFrame({"Abondance": [12, 5, 23, 0, 8, 17], "Habitat": ["Forêt", "Savane", "Zone humide", "Agroéco", "Forêt", "Zone humide"], "Annee": [2018, 2018, 2019, 2019, 2020, 2020], "Effort": [2, 1, 3, 1, 2, 4]}),
                "template_glm_comptage.csv",
            )
            abond_col = st.selectbox("Colonne abondance (comptage)", numeric_cols)
            hab_col = st.selectbox("Colonne habitat (optionnel)", ["—"] + cat_cols)
            year_col = st.selectbox("Colonne année (optionnel)", ["—"] + numeric_cols)
            effort_col = st.selectbox("Colonne effort (optionnel)", ["—"] + numeric_cols)
        import pandas as _pd
        data = _pd.DataFrame({"Abondance": data_src[abond_col].fillna(0).clip(lower=0).astype(int)})
        data["Habitat"] = data_src[hab_col].values if hab_col != "—" else "Site"
        data["Annee"] = data_src[year_col].fillna(2010).astype(int).values if year_col != "—" else 2010
        data["Effort"] = data_src[effort_col].fillna(1).clip(lower=1).astype(int).values if effort_col != "—" else 1
        data = data.dropna()
    else:
        with left:
            n_sites = st.slider("Sites par année", 10, 80, 30)
            n_years = st.slider("Nombre d'années", 3, 15, 8)
            mean_count = st.slider("Abondance moyenne de base", 1.0, 20.0, 5.0, step=0.5)
            year_trend = st.slider("Tendance annuelle (log-échelle)", -0.15, 0.15, -0.04, step=0.01, format="%.2f")
            overdispersion = st.slider("Surdispersion simulée (1 = Poisson pur)", 1.0, 5.0, 2.0, step=0.1)
            seed = st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=66)
        data = simulate_count_data(n_sites, n_years, mean_count, year_trend, overdispersion, int(seed))

    with right:
        fig = px.histogram(
            data, x="Abondance", color="Habitat", nbins=25, barmode="overlay",
            labels={"Abondance": "Abondance observée"},
        )
        fig.update_layout(yaxis_title="Fréquence")
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    with st.spinner("Ajustement des modèles…"):
        poisson_res = _fit_glm(data, "Poisson")
        nb_res = _fit_glm(data, "NB")

    if "error" in poisson_res:
        st.error(poisson_res["error"])
        return

    tabs = st.tabs(["Poisson", "Binomial négatif", "Comparaison", "Diagnostics résidus", "Export"])

    with tabs[0]:
        disp = poisson_res["overdispersion"]
        st.markdown(f"**AIC = {poisson_res['aic']}  ·  Surdispersion Pearson/df = {disp:.2f}**")
        if not np.isnan(disp) and disp > 2.0:
            st.warning(f"Ratio de surdispersion élevé ({disp:.2f} > 2) : le binomial négatif est recommandé.")
        st.dataframe(poisson_res["coef_table"], use_container_width=True)
        explain(
            "Chaque IRR (Incidence Rate Ratio) multiplie l'abondance attendue par rapport à la modalité de référence "
            "(Agroécosystème, année 2010), à effort égal. IRR < 1 → moins d'oiseaux, IRR > 1 → plus d'oiseaux."
        )

    with tabs[1]:
        if "error" in nb_res:
            st.error(nb_res["error"])
        else:
            st.markdown(f"**AIC = {nb_res['aic']}  ·  Surdispersion interne modélisée**")
            st.dataframe(nb_res["coef_table"], use_container_width=True)
            explain(
                "Le binomial négatif estime un paramètre de surdispersion supplémentaire. "
                "Si son AIC est nettement inférieur au modèle Poisson, il est à préférer."
            )

    with tabs[2]:
        if "error" not in nb_res:
            comp = pd.DataFrame({
                "Modèle": ["Poisson", "Binomial négatif"],
                "AIC": [poisson_res["aic"], nb_res["aic"]],
                "Surdispersion Pearson/df": [poisson_res["overdispersion"], "—"],
            })
            st.dataframe(comp, use_container_width=True)
            fig2 = px.bar(comp, x="Modèle", y="AIC", color="Modèle", text="AIC")
            fig2.update_layout(showlegend=False)
            style_figure(fig2)
            st.plotly_chart(fig2, use_container_width=True)
            best = "Poisson" if poisson_res["aic"] <= nb_res["aic"] else "Binomial négatif"
            explain(f"Le modèle le mieux ajusté selon l'AIC est le {best}.")

    with tabs[3]:  # Diagnostics résidus
        import plotly.graph_objects as go
        from scipy import stats as _stats
        st.markdown("#### Diagnostics du modèle Poisson")
        st.caption(
            "Ces graphiques vérifient les hypothèses du GLM : "
            "homoscédasticité des résidus, absence de structure résiduelle, et normalité approximative."
        )
        pr = poisson_res.get("pearson_resid")
        ft = poisson_res.get("fitted")
        if pr is not None and ft is not None:
            pr = np.array(pr)
            ft = np.array(ft)
            d1, d2 = st.columns(2)
            with d1:
                fig_rf = go.Figure()
                fig_rf.add_scatter(
                    x=ft, y=pr, mode="markers",
                    marker={"size": 5, "color": "#4dabf7", "opacity": 0.6},
                    name="Résidus",
                )
                fig_rf.add_hline(y=0, line_dash="dash", line_color="#39d98a")
                fig_rf.add_hline(y=2, line_dash="dot", line_color="#ff6b6b")
                fig_rf.add_hline(y=-2, line_dash="dot", line_color="#ff6b6b")
                fig_rf.update_layout(
                    xaxis_title="Valeurs ajustées",
                    yaxis_title="Résidus de Pearson",
                    title={"text": "Résidus vs valeurs ajustées", "font": {"size": 13}},
                    height=300,
                )
                style_figure(fig_rf)
                st.plotly_chart(fig_rf, use_container_width=True)
                pct_out = float(np.mean(np.abs(pr) > 2) * 100)
                if pct_out > 5:
                    st.warning(f"{pct_out:.1f} % des résidus ont |r| > 2 (attendu ≤ 5 %). Le modèle Poisson sous-ajuste probablement — envisagez le binomial négatif.")
                else:
                    st.success(f"Seulement {pct_out:.1f} % des résidus hors ±2. Ajustement satisfaisant.")
            with d2:
                (osm, osr), (slope, intercept, _) = _stats.probplot(pr)
                fig_qq = go.Figure()
                fig_qq.add_scatter(
                    x=osm, y=osr, mode="markers",
                    marker={"size": 5, "color": "#4dabf7", "opacity": 0.6},
                    name="Résidus",
                )
                x_line = np.array([min(osm), max(osm)])
                fig_qq.add_scatter(
                    x=x_line, y=slope * x_line + intercept,
                    mode="lines", line={"dash": "dash", "color": "#39d98a", "width": 2},
                    name="Référence",
                )
                fig_qq.update_layout(
                    xaxis_title="Quantiles théoriques (N(0,1))",
                    yaxis_title="Résidus de Pearson",
                    title={"text": "Q-Q des résidus de Pearson", "font": {"size": 13}},
                    height=300,
                )
                style_figure(fig_qq)
                st.plotly_chart(fig_qq, use_container_width=True)

            disp = poisson_res["overdispersion"]
            if not np.isnan(disp):
                st.metric("Ratio surdispersion Pearson/df", f"{disp:.3f}", help="Idéalement proche de 1. > 2 : surdispersion marquée.")
        else:
            st.info("Diagnostics de résidus non disponibles pour ce modèle.")
        teacher_note(
            "Les résidus de Pearson sont définis comme (y_i − μ̂_i) / √(V(μ̂_i)). "
            "Un ratio Pearson/df >> 1 indique de la surdispersion : le modèle Poisson sous-estime la variance. "
            "Le Q-Q plot des résidus teste approximativement la normalité asymptotique des résidus.",
            context,
        )

    with tabs[4]:  # Export
        st.download_button("Exporter les données CSV", data.to_csv(index=False).encode("utf-8"), "orni_lab_glm.csv", "text/csv")
        if is_data:
            lines = [f"Donnees terrain : {len(data)} observations."]
        else:
            lines = [f"Sites/an = {n_sites}, annees = {n_years}, surdispersion simulee = {overdispersion:.1f}."]
        lines.append(f"Poisson AIC = {poisson_res['aic']}, Pearson/df = {poisson_res['overdispersion']:.2f}.")
        if "error" not in nb_res:
            lines.append(f"Binomial negatif AIC = {nb_res['aic']}.")
        pdf = build_pdf_report("ORNI-LAB - GLM de comptage", lines)
        if pdf:
            st.download_button("Exporter le résumé PDF", pdf, "orni_lab_glm.pdf", "application/pdf")

    teacher_note(
        "Le quasi-Poisson n'a pas d'AIC : il gonfle les erreurs-type sans changer les coefficients. "
        "Le binomial négatif modélise la surdispersion via un mélange Poisson-Gamma (variance = μ + μ²/r). "
        "L'offset log(effort) est crucial : il transforme un comptage brut en taux normalisé par l'effort.",
        context,
    )
    teacher_formula(
        "GLM Poisson avec offset — lien log",
        r"\log(\mu_i) = \beta_0 + \beta_1 x_{i1} + \cdots + \beta_k x_{ik} + \underbrace{\log(\text{effort}_i)}_{\text{offset (coefficient fixé à 1)}}"
        r"\qquad \text{IRR} = e^{\hat{\beta}_j}",
        context,
    )
    teacher_formula(
        "Surdispersion — Binomial négatif",
        r"\text{Var}(Y_i) = \mu_i + \frac{\mu_i^2}{r} \quad (r > 0)"
        r"\qquad \phi_{\text{Pearson}} = \frac{\chi^2_{\text{Pearson}}}{df} \xrightarrow{H_0: \text{Poisson}} 1",
        context,
    )
    teacher_pitfalls(
        [
            "Omettre l'offset quand l'effort varie entre sites/années : les coefficients estiment des comptages bruts, pas des taux.",
            "Ignorer la surdispersion (φ >> 1) avec un GLM Poisson : les erreurs-type sont sous-estimées → p-values trop petites.",
            "Confondre IRR < 1 et 'l'habitat est mauvais' : l'IRR est relatif à la modalité de référence, pas à zéro.",
            "Inclure des covariables corrélées (multicolinéarité) : les IRR individuels deviennent instables même si le modèle global est bon.",
        ],
        context,
    )
    learning_notes(
        "L'AIC compare les modèles : plus il est bas, meilleur est l'ajustement pénalisé par la complexité.",
        "Un GLM ne remplace pas un bon protocole : biais de détection, sites non indépendants et effort variable doivent être justifiés.",
        None if is_data else "Mets la tendance à -0.10 et observe comment l'IRR de l'année reflète ce déclin.",
    )
