from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.export import build_pdf_report
from utils.ui import csv_template_button, explain, learning_notes, module_intro, section, style_figure, teacher_formula, teacher_note, teacher_pitfalls


def simulate_mixed_data(
    n_sites: int,
    n_per_site: int,
    slope: float,
    site_sd: float,
    residual_sd: float,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    site_effects = rng.normal(0, site_sd, n_sites)
    rows = []
    for s in range(n_sites):
        wing = rng.uniform(60, 100, n_per_site)
        mass = 10.0 + slope * wing + site_effects[s] + rng.normal(0, residual_sd, n_per_site)
        rows.append(pd.DataFrame({
            "Site": [f"S{s + 1:02d}"] * n_per_site,
            "Envergure_mm": wing.round(1),
            "Masse_g": mass.round(1),
        }))
    return pd.concat(rows, ignore_index=True)


def fit_mixed_model(data: pd.DataFrame, fixed_col: str, response_col: str, group_col: str) -> dict:
    try:
        import statsmodels.api as sm
        import statsmodels.formula.api as smf
        from scipy import stats as _sp
    except ImportError:
        return {"error": "statsmodels non disponible — pip install statsmodels"}

    # ── Extraction sécurisée par copie directe des valeurs (évite tout problème
    #    de noms dupliqués ou de types inattendus dans le DataFrame source) ──────
    try:
        y_vals = pd.to_numeric(data[response_col], errors="coerce").values
        x_vals = pd.to_numeric(data[fixed_col],    errors="coerce").values
        g_vals = data[group_col].astype(str).values
    except Exception as exc:
        return {"error": f"Impossible d'extraire les colonnes : {exc}"}

    # DataFrame propre avec noms neutres — aucun risque de collision
    sub = pd.DataFrame({"_Y": y_vals, "_X": x_vals, "_G": g_vals}).dropna()

    # ── Validations ──────────────────────────────────────────────────────────
    if sub["_G"].nunique() < 2:
        return {"error": "Il faut au moins 2 groupes distincts pour ajuster un modèle mixte."}
    if len(sub) < 5:
        return {"error": "Moins de 5 observations valides — impossible d'ajuster le modèle."}
    if sub["_X"].std() == 0:
        return {"error": f"La variable '{fixed_col}' est constante — régression impossible."}

    try:
        result = smf.mixedlm("_Y ~ _X", sub, groups=sub["_G"]).fit(reml=True, disp=False)

        # ── Effets fixes : on travaille uniquement sur fe_params ─────────
        fe_params = result.fe_params          # toujours 2 éléments : Intercept + _X
        n_fe      = len(fe_params)

        # SE : bse_fe d'abord, sinon on coupe bse aux n_fe premiers éléments
        try:
            bse_arr = np.asarray(result.bse_fe)[:n_fe]
        except AttributeError:
            bse_arr = np.asarray(result.bse)[:n_fe]

        # p-values : on filtre explicitement sur l'index de fe_params
        pv_series = result.pvalues
        if hasattr(pv_series, "reindex"):
            pv_series = pv_series.reindex(fe_params.index)
        pv_arr = np.asarray(pv_series)[:n_fe]

        coef_arr = np.asarray(fe_params)
        z_arr    = np.where(bse_arr != 0, coef_arr / bse_arr, 0.0)

        labels = ["Intercept", fixed_col][:n_fe]

        fe = pd.DataFrame({
            "Coef.": coef_arr.round(4),
            "SE":    bse_arr.round(4),
            "z":     z_arr.round(3),
            "p":     [f"{float(v):.2e}" if float(v) < 0.0001 else round(float(v), 4)
                      for v in pv_arr],
        }, index=labels)
        fe.index.name = "Paramètre"

        # ── Composantes de variance ──────────────────────────────────────
        try:
            var_re = float(result.cov_re.iloc[0, 0])
        except Exception:
            var_re = 0.0
        var_res = float(result.scale)
        icc = var_re / (var_re + var_res) if (var_re + var_res) > 0 else 0.0

        # ── AIC (fallback manuel si NaN) ─────────────────────────────────
        aic_val = float(result.aic)
        if np.isnan(aic_val):
            aic_val = -2.0 * float(result.llf) + 2.0 * n_fe

        # ── Nombre de groupes ────────────────────────────────────────────
        try:
            n_groups = int(result.ngroups)
        except AttributeError:
            n_groups = int(sub["_G"].nunique())

        return {
            "fixed_effects": fe,
            "var_re":   round(var_re, 4),
            "var_res":  round(var_res, 4),
            "icc":      round(icc, 4),
            "fitted":   np.asarray(result.fittedvalues),
            "resid":    np.asarray(result.resid),
            "aic":      round(aic_val, 2),
            "n_groups": n_groups,
        }

    except Exception as exc:
        return {"error": f"Échec d'ajustement : {exc}"}


def render(context: dict) -> None:
    section("Modèles mixtes (LMM)", "Effets aléatoires pour données groupées ou répétées.")
    module_intro(
        "Un modèle linéaire mixte (LMM) sépare la variance en effets fixes (prédicteurs biologiques) et effets aléatoires (sites, individus, sessions).",
        "Indispensable quand les observations ne sont pas indépendantes : oiseaux mesurés sur plusieurs sites, individus suivis dans le temps.",
        "En ornithologie, les données de suivi sont presque toujours groupées (par site, colonie ou individu) : ignorer cette structure gonfle artificiellement les faux positifs.",
    )

    left, right = st.columns([0.9, 1.55])

    if context.get("data") is not None:
        data_src = context["data"]
        num_cols = context["numeric_columns"]
        cat_cols = context["categorical_columns"]
        if len(num_cols) < 2 or not cat_cols:
            st.warning("Il faut au moins deux colonnes numériques (Y et X) et une colonne catégorielle de groupes.")
            return
        with left:
            csv_template_button(
                pd.DataFrame({
                    "Site": ["A", "A", "A", "B", "B", "B", "C", "C"],
                    "Envergure_mm": [72, 75, 78, 68, 71, 74, 80, 82],
                    "Masse_g": [18.2, 19.1, 20.0, 16.8, 17.9, 18.5, 21.1, 21.8],
                }),
                "template_mixedlm.csv",
            )
            resp = st.selectbox("Variable réponse (Y)", num_cols)
            pred = st.selectbox("Prédicteur fixe (X)", [c for c in num_cols if c != resp])
            grp = st.selectbox("Effet aléatoire (groupe)", cat_cols)
        data = data_src[[resp, pred, grp]].dropna()
        resp_name, pred_name, grp_name = resp, pred, grp
    else:
        with left:
            n_sites = st.slider("Nombre de sites", 5, 30, 12)
            n_per = st.slider("Individus par site", 3, 20, 8)
            slope = st.slider("Pente fixe (masse ~ envergure)", 0.0, 0.5, 0.18, step=0.01)
            site_sd = st.slider("Écart-type effet site", 0.0, 5.0, 2.0, step=0.1)
            res_sd = st.slider("Écart-type résiduel", 0.5, 5.0, 1.5, step=0.1)
            seed = st.number_input("Graine", 1, 9999, 42)
        data = simulate_mixed_data(n_sites, n_per, slope, site_sd, res_sd, int(seed))
        resp_name, pred_name, grp_name = "Masse_g", "Envergure_mm", "Site"

    res = fit_mixed_model(data, pred_name, resp_name, grp_name)

    if "error" in res:
        st.error(res["error"])
        return

    with right:
        fig = go.Figure()
        palette = ["#39d98a", "#4dabf7", "#ff6b6b", "#ffd166", "#b197fc",
                   "#20c997", "#fd7e14", "#e64980", "#74c0fc", "#a9e34b"]
        groups = sorted(data[grp_name].unique())
        for i, g in enumerate(groups[:10]):
            mask = data[grp_name] == g
            fig.add_scatter(
                x=data.loc[mask, pred_name], y=data.loc[mask, resp_name],
                mode="markers", name=str(g),
                marker={"size": 6, "color": palette[i % len(palette)], "opacity": 0.7},
                legendgroup=str(g),
            )
        x_range = np.linspace(data[pred_name].min(), data[pred_name].max(), 120)
        fe = res["fixed_effects"]
        intercept = float(fe.iloc[0]["Coef."])
        slope_val = float(fe.iloc[1]["Coef."]) if len(fe) > 1 else 0.0
        fig.add_scatter(
            x=x_range, y=intercept + slope_val * x_range,
            mode="lines", name="Effet fixe global",
            line={"width": 3, "dash": "dash", "color": "#ffffff"},
            showlegend=True,
        )
        fig.update_layout(xaxis_title=pred_name, yaxis_title=resp_name)
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("AIC", f"{res['aic']:.1f}")
    c2.metric("ICC", f"{res['icc']:.3f}", help="Part de variance due aux groupes (0–1)")
    c3.metric("Var. aléatoire", f"{res['var_re']:.3f}", help=f"Variance entre {grp_name}")
    c4.metric("Var. résiduelle", f"{res['var_res']:.3f}")

    st.markdown("**Effets fixes**")
    st.dataframe(res["fixed_effects"], use_container_width=True)

    icc_pct = res["icc"] * 100
    explain(
        f"ICC = {res['icc']:.3f} : {icc_pct:.1f} % de la variance totale est attribuable aux différences entre {grp_name}. "
        + ("Ignorer cet effet de groupe biaiserait les p-values vers le bas." if icc_pct > 10
           else "La structure de groupe contribue peu à la variance totale ici.")
    )

    with st.expander("Diagnostics résidus"):
        fig_r = go.Figure()
        fig_r.add_scatter(
            x=res["fitted"], y=res["resid"], mode="markers",
            marker={"size": 5, "color": "#4dabf7", "opacity": 0.6},
        )
        fig_r.add_hline(y=0, line_dash="dash", line_color="#39d98a")
        fig_r.update_layout(xaxis_title="Valeurs ajustées", yaxis_title="Résidus", height=270)
        style_figure(fig_r)
        st.plotly_chart(fig_r, use_container_width=True)

    teacher_note(
        f"Un ICC > 0.1 justifie l'usage d'un modèle mixte (ici ICC = {res['icc']:.3f} sur {res['n_groups']} groupes). "
        f"REML est recommandé pour estimer les composantes de variance ; utiliser ML uniquement pour comparer "
        f"deux modèles avec des effets fixes différents via un test du rapport de vraisemblance.",
        context,
    )
    teacher_formula(
        "Modèle LMM et ICC",
        r"y_{ij} = \underbrace{\beta_0 + \beta_1 x_{ij}}_{\text{effets fixes}}"
        r"+ \underbrace{b_j}_{\substack{\text{effet}\\\text{aléatoire}}} + \varepsilon_{ij}"
        r"\quad b_j \sim \mathcal{N}(0,\sigma^2_b),\;\varepsilon_{ij}\sim\mathcal{N}(0,\sigma^2_\varepsilon)"
        r"\qquad \text{ICC} = \frac{\sigma^2_b}{\sigma^2_b + \sigma^2_\varepsilon}",
        context,
    )
    teacher_pitfalls(
        [
            "Utiliser ML au lieu de REML pour estimer les composantes de variance : ML sous-estime σ²_b.",
            "Traiter le groupe comme effet fixe quand il représente un échantillon d'une population de groupes : l'effet aléatoire est alors plus approprié.",
            "Ignorer l'ICC et utiliser OLS quand les observations sont groupées : les erreurs-type des effets fixes sont sous-estimées → faux positifs.",
            "Ne pas vérifier la normalité des effets aléatoires (QQ-plot des b_j estimés).",
        ],
        context,
    )
    learning_notes(
        "L'effet aléatoire absorbe la corrélation intra-groupe : les p-values des effets fixes sont fiables.",
        "Le LMM suppose des effets aléatoires gaussiens et une variance résiduelle homogène.",
        None if context.get("data") else "Augmente la SD des sites : à partir de quel ICC le modèle OLS produit-il de faux positifs ?",
    )

    pdf_lines = [
        f"Modele : {resp_name} ~ {pred_name} + (1 | {grp_name}). N = {len(data)}, groupes = {res['n_groups']}.",
        f"ICC = {res['icc']:.3f}, variance aleatoire = {res['var_re']:.4f}, residuelle = {res['var_res']:.4f}.",
        f"AIC = {res['aic']:.1f}.",
    ]
    pdf = build_pdf_report("ORNI-LAB - Modele mixte LMM", pdf_lines)
    if pdf:
        st.download_button("Exporter résumé PDF", pdf, "orni_lab_mixedlm.pdf", "application/pdf")
