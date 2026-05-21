from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.export import build_pdf_report
from utils.ui import csv_template_button, data_incompatible, explain, learning_notes, module_intro, section, style_figure, teacher_formula, teacher_note, teacher_pitfalls


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


def _safe_scalar(x) -> float:
    """Convert any scalar-like (numpy scalar, 0-d array, 1x1 DataFrame…) to float."""
    arr = np.asarray(x)
    return float(arr.flat[0])


def fit_mixed_model(
    y: np.ndarray,
    x: np.ndarray,
    groups: np.ndarray,
    pred_label: str = "Prédicteur",
) -> dict:
    """Fit a LMM from pre-extracted 1D numpy arrays. All DataFrame extraction
    is done by the caller to avoid column-name ambiguity issues."""
    try:
        import statsmodels.formula.api as smf
    except ImportError:
        return {"error": "statsmodels non disponible — pip install statsmodels"}

    sub = pd.DataFrame({"_Y": np.asarray(y, dtype=float),
                         "_X": np.asarray(x, dtype=float),
                         "_G": np.asarray(groups, dtype=str)})
    sub = sub.replace([np.inf, -np.inf], np.nan).dropna()

    n_groups = int(sub["_G"].nunique())
    if n_groups < 2:
        return {"error": "Il faut au moins 2 groupes distincts pour un modèle mixte."}
    if len(sub) < 6:
        return {"error": f"Seulement {len(sub)} observations valides — minimum 6 requis."}
    if float(sub["_X"].std()) == 0.0:
        return {"error": "Le prédicteur X est constant — régression impossible."}

    # ── Ajustement ──────────────────────────────────────────────────────────
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = smf.mixedlm("_Y ~ _X", sub, groups=sub["_G"]).fit(
                reml=True, disp=False
            )
    except Exception as exc:
        return {"error": f"Échec du modèle mixte : {exc}"}

    # ── Extraction ultra-défensive ───────────────────────────────────────────
    try:
        # Effets fixes (toujours une Series dans statsmodels)
        fe_params = result.fe_params
        fe_arr = np.asarray(fe_params).flatten()
        n_fe = len(fe_arr)

        # SE — bse_fe ou bse, gère DataFrame (pas d'opérateur 'or' sur Series)
        try:
            bse_raw = result.bse_fe
        except AttributeError:
            bse_raw = result.bse
        bse_arr = np.asarray(bse_raw).flatten()[:n_fe]

        # p-values — index contient FE + RE, on filtre sur les clés FE
        pv_raw = result.pvalues
        fe_keys = list(fe_params.index)
        if isinstance(pv_raw, pd.DataFrame):
            pv_arr = pv_raw.values.flatten()[:n_fe]
        else:
            pv_series = pd.Series(np.asarray(pv_raw).flatten(), index=pv_raw.index)
            fe_mask = pv_series.index.isin(fe_keys)
            pv_arr = pv_series[fe_mask].values[:n_fe] if fe_mask.sum() >= n_fe else np.asarray(pv_raw).flatten()[:n_fe]

        z_arr = np.where((bse_arr != 0) & np.isfinite(bse_arr), fe_arr / bse_arr, 0.0)
        labels = ["Intercept", pred_label][:n_fe]

        fe_table = pd.DataFrame({
            "Coef.": np.round(fe_arr, 4),
            "SE":    np.round(bse_arr, 4),
            "z":     np.round(z_arr, 3),
            "p":     [
                (f"{float(v):.2e}" if float(v) < 0.0001 else round(float(v), 4))
                if np.isfinite(v) else "—"
                for v in pv_arr
            ],
        }, index=labels)
        fe_table.index.name = "Paramètre"

        # Composantes de variance — _safe_scalar évite le bool ambiguïté
        cov_re_obj = result.cov_re
        var_re = _safe_scalar(cov_re_obj) if cov_re_obj is not None else 0.0
        var_res = _safe_scalar(result.scale)
        icc = var_re / (var_re + var_res) if (var_re + var_res) > 0 else 0.0

        # AIC
        aic_raw = _safe_scalar(result.aic)
        aic_val = aic_raw if np.isfinite(aic_raw) else -2.0 * _safe_scalar(result.llf) + 2.0 * n_fe

        # Fitted / résidus — toujours 1D
        fitted = np.asarray(result.fittedvalues).flatten()
        resid  = np.asarray(result.resid).flatten()

        return {
            "fixed_effects": fe_table,
            "var_re":   round(var_re, 4),
            "var_res":  round(var_res, 4),
            "icc":      round(icc, 4),
            "fitted":   fitted,
            "resid":    resid,
            "aic":      round(aic_val, 2),
            "n_groups": n_groups,
            "n_obs":    len(sub),
            "group_sizes": sub.groupby("_G").size().to_dict(),
        }

    except Exception as exc:
        return {"error": f"Extraction des résultats impossible : {exc}"}


# ─── helpers ────────────────────────────────────────────────────────────────

def _get_col_values(df: pd.DataFrame, col: str) -> np.ndarray:
    """Safe column extraction — always returns 1D array even with duplicate names."""
    raw = df[col]
    if isinstance(raw, pd.DataFrame):
        raw = raw.iloc[:, 0]
    return np.asarray(raw).flatten()


def _group_stats(df: pd.DataFrame, grp_col: str, val_col: str) -> pd.DataFrame:
    g = _get_col_values(df, grp_col)
    v = _get_col_values(df, val_col)
    sub = pd.DataFrame({"g": g, "v": v}).dropna()
    rows = []
    for name, grp in sub.groupby("g"):
        rows.append({
            "Groupe": name,
            "n": len(grp),
            "Moyenne": round(grp["v"].mean(), 3),
            "Médiane": round(grp["v"].median(), 3),
            "Écart-type": round(grp["v"].std(), 3),
        })
    return pd.DataFrame(rows)


# ─── render ─────────────────────────────────────────────────────────────────

def render(context: dict) -> None:
    section("Modèles mixtes (LMM)", "Effets aléatoires pour données groupées ou répétées.")
    module_intro(
        "Un modèle linéaire mixte (LMM) sépare la variance en effets fixes (prédicteurs biologiques) et effets aléatoires (sites, individus, sessions).",
        "Indispensable quand les observations ne sont pas indépendantes : oiseaux mesurés sur plusieurs sites, individus suivis dans le temps.",
        "En ornithologie, les données de suivi sont presque toujours groupées (par site, colonie ou individu) : ignorer cette structure gonfle artificiellement les faux positifs.",
    )

    is_data = context.get("data") is not None
    left, right = st.columns([0.9, 1.55])

    # ── Sélection des variables ─────────────────────────────────────────────
    if is_data:
        data_src = context["data"]
        num_cols = context["numeric_columns"]
        cat_cols = context["categorical_columns"]

        # Colonnes catégorielles élargies : accepter aussi les numériques à faible cardinalité
        low_card_num = [c for c in num_cols if data_src[c].nunique(dropna=True) <= 20]
        grp_options = cat_cols + [c for c in low_card_num if c not in cat_cols]

        if len(num_cols) < 2 or not grp_options:
            data_incompatible(
                "Ce module nécessite au moins deux colonnes numériques (Y et X) et une colonne de groupes "
                "(catégorielle ou numérique à faible cardinalité, ex. : Site, Individu, Année).",
                [
                    "Vérifiez que votre fichier contient des mesures numériques (masse, longueur, abondance…).",
                    "Ajoutez une colonne identifiant les groupes — texte ou code numérique avec ≤ 20 modalités.",
                    "Si toutes les colonnes sont des mesures continues, utilisez <b>Corrélation et régression</b>.",
                    "Téléchargez l'exemple CSV pour voir la structure attendue.",
                ],
            )
            return

        with left:
            csv_template_button(
                pd.DataFrame({
                    "Site": ["A", "A", "A", "B", "B", "B", "C", "C", "C"],
                    "Envergure_mm": [72, 75, 78, 68, 71, 74, 80, 82, 79],
                    "Masse_g": [18.2, 19.1, 20.0, 16.8, 17.9, 18.5, 21.1, 21.8, 20.5],
                }),
                "template_mixedlm.csv",
            )
            st.markdown("**Variables du modèle**")
            resp = st.selectbox("Variable réponse Y", num_cols, key="lmm_resp")
            remaining_num = [c for c in num_cols if c != resp]
            pred = st.selectbox("Prédicteur fixe X", remaining_num, key="lmm_pred") if remaining_num else None
            grp  = st.selectbox("Effet aléatoire (groupe)", grp_options, key="lmm_grp")

            st.markdown("**Options**")
            apply_log = st.checkbox("Log-transformation de Y (log(Y+1))", value=False, key="lmm_log",
                                    help="Utile pour des comptages ou des valeurs très asymétriques")
            min_n_grp = st.slider("Taille minimale par groupe", 2, 10, 3, key="lmm_min_n",
                                  help="Groupes avec moins de N observations sont exclus")

        if pred is None:
            st.warning("Il faut au moins deux colonnes numériques distinctes pour X et Y.")
            return

        # Extraction sécurisée — toujours 1D pour éviter l'ambiguïté DataFrame
        y_raw = pd.to_numeric(_get_col_values(data_src, resp),   errors="coerce")
        x_raw = pd.to_numeric(_get_col_values(data_src, pred),   errors="coerce")
        g_raw = _get_col_values(data_src, grp).astype(str)

        tmp = pd.DataFrame({"y": y_raw, "x": x_raw, "g": g_raw}).dropna()

        # Exclure les groupes trop petits
        grp_counts = tmp["g"].value_counts()
        valid_groups = grp_counts[grp_counts >= min_n_grp].index
        tmp = tmp[tmp["g"].isin(valid_groups)].copy()

        resp_name, pred_name, grp_name = resp, pred, grp

    else:
        with left:
            n_sites = st.slider("Nombre de sites", 5, 30, 12, key="lmm_sim_sites")
            n_per   = st.slider("Individus par site", 3, 20, 8, key="lmm_sim_nper")
            slope   = st.slider("Pente fixe", 0.0, 0.5, 0.18, step=0.01, key="lmm_sim_slope")
            site_sd = st.slider("Écart-type effet site", 0.0, 5.0, 2.0, step=0.1, key="lmm_sim_sitesd")
            res_sd  = st.slider("Écart-type résiduel", 0.5, 5.0, 1.5, step=0.1, key="lmm_sim_ressd")
            seed    = int(st.number_input("Graine", 1, 9999, 42, key="lmm_seed") or 42)
            apply_log = False
            min_n_grp = 3
        sim = simulate_mixed_data(n_sites, n_per, slope, site_sd, res_sd, int(seed))
        tmp = pd.DataFrame({"y": sim["Masse_g"], "x": sim["Envergure_mm"], "g": sim["Site"]})
        resp_name, pred_name, grp_name = "Masse_g", "Envergure_mm", "Site"

    # ── Aperçu des données sélectionnées ────────────────────────────────────
    if is_data:
        n_excluded = len(pd.DataFrame({"y": y_raw, "x": x_raw, "g": g_raw}).dropna()) - len(tmp)
        n_groups_ok = tmp["g"].nunique()

        if len(tmp) < 6 or n_groups_ok < 2:
            data_incompatible(
                f"Après filtrage (groupes < {min_n_grp} observations exclus), il reste "
                f"{len(tmp)} observation(s) dans {n_groups_ok} groupe(s) — insuffisant pour le modèle.",
                [
                    f"Réduisez la taille minimale par groupe (actuellement {min_n_grp}).",
                    "Vérifiez que la colonne de groupe choisie a bien plusieurs modalités avec des données.",
                    "Utilisez <b>Corrélation et régression</b> si vous n'avez pas de structure groupée.",
                ],
            )
            return

        with left:
            st.markdown("**Aperçu par groupe**")
            gstats = _group_stats(tmp, "g", "y")
            tiny = gstats[gstats["n"] < 5]
            if len(tiny) > 0:
                st.caption(f"⚠ {len(tiny)} groupe(s) avec < 5 obs — convergence incertaine.")
            st.dataframe(gstats.rename(columns={"Groupe": grp_name, "Moyenne": resp_name[:12]}),
                         use_container_width=True, hide_index=True)
            if n_excluded > 0:
                st.caption(f"ℹ {n_excluded} ligne(s) exclue(s) (NA ou groupe trop petit).")

    # ── Transformation ──────────────────────────────────────────────────────
    y_fit = np.log1p(tmp["y"].values) if apply_log else tmp["y"].values
    x_fit = tmp["x"].values
    g_fit = tmp["g"].values

    if apply_log:
        display_resp = f"log(1+{resp_name})"
    else:
        display_resp = resp_name

    # ── Ajustement ──────────────────────────────────────────────────────────
    with st.spinner("Ajustement du modèle mixte…"):
        res = fit_mixed_model(y_fit, x_fit, g_fit, pred_label=pred_name)

    if "error" in res:
        data_incompatible(
            f"Le modèle mixte n'a pas pu être ajusté : {res['error']}",
            [
                "Réduisez la taille minimale par groupe ou vérifiez que les groupes ont suffisamment de variance.",
                "Essayez la log-transformation si la variable réponse est très asymétrique.",
                f"Vérifiez que {pred_name} n'est pas constant dans certains groupes.",
                "Si le problème persiste, utilisez <b>Corrélation et régression</b> (OLS sans effet groupe).",
            ],
        )
        return

    # ── Visualisation ───────────────────────────────────────────────────────
    with right:
        fig = go.Figure()
        palette = ["#39d98a", "#4dabf7", "#ff6b6b", "#ffd166", "#b197fc",
                   "#20c997", "#fd7e14", "#e64980", "#74c0fc", "#a9e34b"]
        unique_groups = sorted(tmp["g"].unique().tolist())
        for i, g in enumerate(unique_groups[:10]):
            mask = (tmp["g"] == g).values   # numpy bool array — jamais ambigu
            fig.add_scatter(
                x=x_fit[mask], y=y_fit[mask],
                mode="markers", name=str(g),
                marker={"size": 6, "color": palette[i % len(palette)], "opacity": 0.7},
                legendgroup=str(g),
            )
        x_range = np.linspace(float(x_fit.min()), float(x_fit.max()), 120)
        fe = res["fixed_effects"]
        intercept = float(fe.iloc[0]["Coef."])
        slope_val = float(fe.iloc[1]["Coef."]) if len(fe) > 1 else 0.0
        fig.add_scatter(
            x=x_range, y=intercept + slope_val * x_range,
            mode="lines", name="Effet fixe global",
            line={"width": 3, "dash": "dash", "color": "#ffffff"},
        )
        fig.update_layout(xaxis_title=pred_name, yaxis_title=display_resp)
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    # ── Métriques ───────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("AIC", f"{res['aic']:.1f}")
    c2.metric("ICC", f"{res['icc']:.3f}", help="Part de variance due aux groupes (0–1)")
    c3.metric("Var. aléatoire", f"{res['var_re']:.4f}", help=f"Variance entre {grp_name}")
    c4.metric("Var. résiduelle", f"{res['var_res']:.4f}")

    st.markdown("**Effets fixes**")
    st.dataframe(res["fixed_effects"], use_container_width=True)

    icc_pct = res["icc"] * 100
    if icc_pct > 30:
        icc_msg = f"ICC élevé ({icc_pct:.1f} %) — la structure de groupe est très importante, le LMM est bien justifié."
    elif icc_pct > 10:
        icc_msg = f"ICC modéré ({icc_pct:.1f} %) — ignorer les groupes biaiserait les p-values."
    else:
        icc_msg = f"ICC faible ({icc_pct:.1f} %) — la structure de groupe contribue peu ; une régression OLS pourrait suffire."
    explain(icc_msg)

    # ── Diagnostics ─────────────────────────────────────────────────────────
    with st.expander("Diagnostics résidus"):
        fig_r = go.Figure()
        fig_r.add_scatter(
            x=res["fitted"].tolist(), y=res["resid"].tolist(), mode="markers",
            marker={"size": 5, "color": "#4dabf7", "opacity": 0.6},
        )
        fig_r.add_hline(y=0, line_dash="dash", line_color="#39d98a")
        fig_r.update_layout(xaxis_title="Valeurs ajustées", yaxis_title="Résidus", height=270)
        style_figure(fig_r)
        st.plotly_chart(fig_r, use_container_width=True)
        st.caption("Un nuage aléatoire autour de 0 confirme l'homoscédasticité. Un entonnoir ou une courbe signale une hypothèse violée.")

    # ── Pédagogie ───────────────────────────────────────────────────────────
    teacher_note(
        f"Un ICC > 0.1 justifie l'usage d'un modèle mixte (ici ICC = {res['icc']:.3f} sur {res['n_groups']} groupes). "
        "REML est recommandé pour estimer les composantes de variance ; utiliser ML uniquement pour comparer "
        "deux modèles avec des effets fixes différents via un test du rapport de vraisemblance.",
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
            "Traiter le groupe comme effet fixe quand il représente un échantillon d'une population de groupes.",
            "Ignorer l'ICC et utiliser OLS quand les observations sont groupées : les SE des effets fixes sont sous-estimées → faux positifs.",
            "Ne pas vérifier la normalité des effets aléatoires (QQ-plot des b_j estimés).",
        ],
        context,
    )
    learning_notes(
        "L'effet aléatoire absorbe la corrélation intra-groupe : les p-values des effets fixes sont fiables.",
        "Le LMM suppose des effets aléatoires gaussiens et une variance résiduelle homogène.",
        None if is_data else "Augmente la SD des sites : à partir de quel ICC le modèle OLS produit-il de faux positifs ?",
    )

    # ── Export ──────────────────────────────────────────────────────────────
    pdf_lines = [
        f"Modele : {display_resp} ~ {pred_name} + (1 | {grp_name}). N = {res['n_obs']}, groupes = {res['n_groups']}.",
        f"ICC = {res['icc']:.3f}, variance aleatoire = {res['var_re']:.4f}, residuelle = {res['var_res']:.4f}.",
        f"AIC = {res['aic']:.1f}.",
    ]
    pdf = build_pdf_report("ORNI-LAB - Modele mixte LMM", pdf_lines)
    if pdf:
        st.download_button("Exporter résumé PDF", pdf, "orni_lab_mixedlm.pdf", "application/pdf")
