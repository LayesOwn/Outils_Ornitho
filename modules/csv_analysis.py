from __future__ import annotations

import csv as _csv
import io
import warnings

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from core.export import build_pdf_report
from utils.ui import explain, learning_notes, module_intro, section, style_figure

warnings.filterwarnings("ignore", category=RuntimeWarning)

# ── Constantes ────────────────────────────────────────────────────────────────
_ENCODINGS   = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "utf-16"]
_SEPARATORS  = {",": "Virgule (,)", ";": "Point-virgule (;)", "\t": "Tabulation", "|": "Pipe (|)"}
_NULL_VALUES = {"", "na", "n/a", "nan", "null", "none", "nd", "nr", "#n/a", "#na", "-", "--"}


# ══════════════════════════════════════════════════════════════════════════════
# CHARGEMENT & NETTOYAGE
# ══════════════════════════════════════════════════════════════════════════════

def _sniff_separator(raw: bytes) -> str:
    try:
        sample = raw[:4096].decode("utf-8", errors="replace")
        dialect = _csv.Sniffer().sniff(sample, delimiters=",;\t|")
        return dialect.delimiter
    except Exception:
        return ";"


def _try_load(raw: bytes, sep: str, enc: str) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(io.BytesIO(raw), sep=sep, encoding=enc, on_bad_lines="skip",
                         skipinitialspace=True, na_values=list(_NULL_VALUES),
                         keep_default_na=True)
        if df.shape[1] >= 1:
            return df
    except Exception:
        pass
    return None


def auto_load(raw: bytes) -> tuple[pd.DataFrame, str, str]:
    """Détecte automatiquement séparateur et encodage. Retourne (df, encoding, sep)."""
    sep_auto = _sniff_separator(raw)
    for enc in _ENCODINGS:
        df = _try_load(raw, sep_auto, enc)
        if df is not None and df.shape[1] > 1:
            return df, enc, sep_auto
    for sep in [";", ",", "\t", "|"]:
        for enc in _ENCODINGS:
            df = _try_load(raw, sep, enc)
            if df is not None and df.shape[1] > 1:
                return df, enc, sep
    raise ValueError("Impossible de lire ce fichier CSV. Vérifiez le format et l'encodage.")


def deep_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoyage approfondi : noms de colonnes, décimales, types, dates, doublons."""
    df = df.copy()
    # Noms de colonnes propres
    df.columns = [str(c).strip().replace("﻿", "") for c in df.columns]
    # Supprimer colonnes et lignes entièrement vides
    df = df.dropna(axis=1, how="all").dropna(axis=0, how="all")
    # Nettoyer les chaînes
    for col in df.select_dtypes("object").columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({v: np.nan for v in _NULL_VALUES})
    # Conversion numérique intelligente (virgule décimale, espaces)
    for col in df.select_dtypes("object").columns:
        converted = pd.to_numeric(
            df[col].astype(str).str.replace(",", ".", regex=False).str.replace(r"\s", "", regex=True),
            errors="coerce",
        )
        n_valid = converted.notna().sum()
        n_present = df[col].notna().sum()
        if n_present > 0 and n_valid / n_present >= 0.75:
            df[col] = converted
    # Détection de dates (colonnes dont le nom contient "date" ou "year"/"annee")
    for col in df.select_dtypes("object").columns:
        if any(k in col.lower() for k in ("date", "year", "annee", "année", "time")):
            parsed = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
            if parsed.notna().mean() >= 0.5:
                df[col] = parsed
    return df


def split_columns(df: pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
    num = df.select_dtypes("number").columns.tolist()
    dt  = df.select_dtypes("datetime").columns.tolist()
    cat = [c for c in df.columns if c not in num and c not in dt
           and df[c].nunique(dropna=True) <= 100]
    return num, cat, dt


# ══════════════════════════════════════════════════════════════════════════════
# PROFIL UNIVARIÉ
# ══════════════════════════════════════════════════════════════════════════════

def profile_numeric(series: pd.Series) -> dict:
    s = series.dropna()
    if len(s) < 2:
        return {"n": len(s), "manquantes": int(series.isna().sum())}
    q1, q3 = float(s.quantile(0.25)), float(s.quantile(0.75))
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers_iqr = int(((s < lo) | (s > hi)).sum())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        zscores = np.abs(stats.zscore(s, nan_policy="omit"))
    outliers_z = int((zscores > 3).sum())
    # Normalité
    w_stat = p_norm = np.nan
    if 3 <= len(s) <= 5000:
        try:
            w_stat, p_norm = stats.shapiro(s)
        except Exception:
            pass
    elif len(s) > 5000:
        try:
            _, p_norm = stats.kstest((s - s.mean()) / s.std(), "norm")
            w_stat = np.nan
        except Exception:
            pass
    return {
        "n": int(len(s)),
        "manquantes": int(series.isna().sum()),
        "% manquantes": round(100 * series.isna().mean(), 1),
        "moyenne": round(float(s.mean()), 4),
        "médiane": round(float(s.median()), 4),
        "écart-type": round(float(s.std()), 4),
        "min": round(float(s.min()), 4),
        "Q1": round(q1, 4),
        "Q3": round(q3, 4),
        "max": round(float(s.max()), 4),
        "IQR": round(iqr, 4),
        "asymétrie": round(float(s.skew()), 3),
        "aplatissement": round(float(s.kurtosis()), 3),
        "outliers IQR": outliers_iqr,
        "outliers Z>3": outliers_z,
        "Shapiro W": round(float(w_stat), 4) if not np.isnan(w_stat) else "—",
        "Shapiro p": round(float(p_norm), 5) if not np.isnan(p_norm) else "—",
    }


def profile_categorical(series: pd.Series) -> dict:
    s = series.dropna().astype(str)
    vc = s.value_counts()
    return {
        "n": int(len(s)),
        "manquantes": int(series.isna().sum()),
        "% manquantes": round(100 * series.isna().mean(), 1),
        "modalités uniques": int(s.nunique()),
        "mode": str(vc.index[0]) if len(vc) > 0 else "—",
        "fréquence mode": int(vc.iloc[0]) if len(vc) > 0 else 0,
        "% mode": round(100 * vc.iloc[0] / len(s), 1) if len(vc) > 0 else 0,
    }


# ══════════════════════════════════════════════════════════════════════════════
# ANALYSE BIVARIÉE
# ══════════════════════════════════════════════════════════════════════════════

def bivariate_num_num(df: pd.DataFrame, x_col: str, y_col: str) -> dict | None:
    data = df[[x_col, y_col]].dropna()
    if len(data) < 3:
        return None
    x, y = data[x_col].values, data[y_col].values
    if x.std() == 0 or y.std() == 0:
        return None
    try:
        lr = stats.linregress(x, y)
        r_sp, p_sp = stats.spearmanr(x, y)
        return {
            "n": len(data),
            "pearson_r": round(float(lr.rvalue), 4),
            "pearson_r2": round(float(lr.rvalue ** 2), 4),
            "pearson_p": float(lr.pvalue),
            "spearman_r": round(float(r_sp), 4),
            "spearman_p": float(p_sp),
            "pente": round(float(lr.slope), 6),
            "intercept": round(float(lr.intercept), 6),
            "stderr": round(float(lr.stderr), 6),
            "data": data,
        }
    except Exception:
        return None


def bivariate_num_cat(df: pd.DataFrame, cat_col: str, num_col: str) -> dict | None:
    data = df[[cat_col, num_col]].dropna()
    groups = {str(g): data.loc[data[cat_col] == g, num_col].values
              for g in data[cat_col].unique()}
    arrays = [v for v in groups.values() if len(v) >= 2]
    if len(arrays) < 2:
        return None
    try:
        if len(arrays) == 2:
            a, b = arrays[0], arrays[1]
            t_stat, t_p = stats.ttest_ind(a, b, equal_var=False)
            u_stat, u_p = stats.mannwhitneyu(a, b, alternative="two-sided")
            labels = list(groups.keys())[:2]
            return {"type": "2g", "groups": groups, "labels": labels,
                    "t_stat": round(float(t_stat), 4), "t_p": float(t_p),
                    "u_stat": round(float(u_stat), 4), "u_p": float(u_p), "data": data}
        else:
            f_stat, f_p = stats.f_oneway(*arrays)
            h_stat, h_p = stats.kruskal(*arrays)
            # Eta² (taille d'effet ANOVA)
            grand_mean = data[num_col].mean()
            ss_between = sum(len(v) * (v.mean() - grand_mean) ** 2 for v in arrays)
            ss_total = ((data[num_col] - grand_mean) ** 2).sum()
            eta2 = ss_between / ss_total if ss_total > 0 else np.nan
            return {"type": "kg", "groups": groups, "n_groups": len(arrays),
                    "f_stat": round(float(f_stat), 4), "f_p": float(f_p),
                    "h_stat": round(float(h_stat), 4), "h_p": float(h_p),
                    "eta2": round(float(eta2), 4), "data": data}
    except Exception:
        return None


def bivariate_cat_cat(df: pd.DataFrame, col1: str, col2: str) -> dict | None:
    ct = pd.crosstab(df[col1].dropna().astype(str), df[col2].dropna().astype(str))
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return None
    try:
        chi2, p, dof, _ = stats.chi2_contingency(ct)
        n = int(ct.values.sum())
        v = np.sqrt(chi2 / (n * (min(ct.shape) - 1))) if n > 0 else np.nan
        return {"chi2": round(float(chi2), 4), "p": float(p), "dof": int(dof),
                "cramers_v": round(float(v), 4), "n": n, "contingency": ct}
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════════════
# UTILITAIRES D'AFFICHAGE
# ══════════════════════════════════════════════════════════════════════════════

def _pval_badge(p: float) -> str:
    if p < 0.001:
        return f"{p:.2e} ***"
    if p < 0.01:
        return f"{p:.4f} **"
    if p < 0.05:
        return f"{p:.4f} *"
    return f"{p:.4f} ns"


def _sig_color(p: float) -> str:
    return "#39d98a" if p < 0.05 else "#ff6b6b"


def _outlier_flag(series: pd.Series) -> pd.Series:
    s = series.dropna()
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    return (series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)


# ══════════════════════════════════════════════════════════════════════════════
# RENDER PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def render(context: dict) -> None:  # noqa: C901
    section("Analyse CSV", "Exploration et analyse professionnelle d'un jeu de données terrain.")
    module_intro(
        "Ce module charge n'importe quel fichier CSV (auto-détection encodage/séparateur), "
        "nettoie les données en profondeur et produit une analyse exploratoire complète.",
        "Il couvre : profil de chaque variable, détection d'outliers, tests de normalité, "
        "corrélations (Pearson/Spearman), comparaisons de groupes et tableau de contingence.",
        "Idéal pour des données de terrain : comptages STOC, mesures morphologiques, "
        "données de baguage, suivis GPS, relevés d'habitat ou résultats de protocoles LPO.",
    )

    # ── Chargement ────────────────────────────────────────────────────────────
    enc_used = sep_used = source_name = None
    if context.get("data") is not None:
        raw_df   = context["data"]
        source_name = context.get("data_filename", "fichier sidebar")
        df = deep_clean(raw_df)
        st.info(f"Données chargées depuis la sidebar : **{source_name}** — {len(df):,} lignes, {len(df.columns)} colonnes.")
    else:
        uploaded = st.file_uploader("Charger un fichier CSV", type=["csv", "txt", "tsv"])
        if uploaded is None:
            st.info("Déposez un fichier CSV pour commencer l'analyse.")
            return

        raw_bytes = uploaded.read()
        source_name = uploaded.name

        # Mode auto vs manuel
        load_mode = st.radio("Détection du format", ["Automatique", "Manuel"], horizontal=True)
        if load_mode == "Automatique":
            try:
                raw_df, enc_used, sep_used = auto_load(raw_bytes)
                st.success(f"Détection automatique — Encodage : **{enc_used}** | Séparateur : **{repr(sep_used)}**")
            except ValueError as e:
                st.error(str(e))
                return
        else:
            col_enc, col_sep = st.columns(2)
            with col_enc:
                enc_used = st.selectbox("Encodage", _ENCODINGS)
            with col_sep:
                sep_label = st.selectbox("Séparateur", list(_SEPARATORS.values()))
                sep_used  = {v: k for k, v in _SEPARATORS.items()}[sep_label]
            raw_df = _try_load(raw_bytes, sep_used, enc_used)
            if raw_df is None:
                st.error("Impossible de lire le fichier avec ces paramètres.")
                return

        try:
            df = deep_clean(raw_df)
        except Exception as e:
            st.error(f"Erreur de nettoyage : {e}")
            return

        # Partager avec tous les modules via session_state
        st.session_state["_orni_shared_df"]   = df
        st.session_state["_orni_shared_fname"] = source_name
        st.success(
            f"✅ **{source_name}** chargé et partagé avec tous les modules. "
            "Rechargez la page ou naviguez vers un autre module pour l'utiliser."
        )

    num_cols, cat_cols, dt_cols = split_columns(df)
    n_dup = int(df.duplicated().sum())

    # ── Métriques globales ────────────────────────────────────────────────────
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Lignes", f"{len(df):,}")
    m2.metric("Colonnes", f"{len(df.columns):,}")
    m3.metric("Numériques", f"{len(num_cols)}")
    m4.metric("Catégorielles", f"{len(cat_cols)}")
    m5.metric("Dates", f"{len(dt_cols)}")
    m6.metric("Doublons", f"{n_dup}", delta=None if n_dup == 0 else f"⚠ {n_dup}")

    # ── Onglets principaux ────────────────────────────────────────────────────
    tabs = st.tabs([
        "📋 Aperçu",
        "🩺 Qualité",
        "📊 Univarié",
        "🔗 Relations",
        "🌡️ Corrélations",
        "💾 Export",
    ])

    # ════════════════════════════════ APERÇU ══════════════════════════════════
    with tabs[0]:
        st.subheader("Aperçu des données")
        n_preview = st.slider("Nombre de lignes à afficher", 5, min(500, len(df)), 20)
        st.dataframe(df.head(n_preview), use_container_width=True)

        st.subheader("Types de colonnes détectés")
        dtype_df = pd.DataFrame({
            "Colonne": df.columns,
            "Type Pandas": df.dtypes.astype(str).values,
            "Catégorie": [
                "Numérique" if c in num_cols
                else "Date" if c in dt_cols
                else "Catégorielle" if c in cat_cols
                else "Texte libre"
                for c in df.columns
            ],
            "Valeurs manquantes": df.isna().sum().values,
            "% manquantes": (100 * df.isna().mean()).round(1).values,
            "Valeurs uniques": [df[c].nunique() for c in df.columns],
        })
        st.dataframe(dtype_df, use_container_width=True)

        if n_dup > 0:
            st.warning(f"**{n_dup} lignes dupliquées** détectées. Utiliser l'export pour obtenir la version dédupliquée.")

        explain(
            f"Le fichier contient {len(df):,} lignes et {len(df.columns)} colonnes après nettoyage. "
            f"Valeurs manquantes totales : {int(df.isna().sum().sum()):,}. "
            f"Colonnes numériques : {len(num_cols)}, catégorielles : {len(cat_cols)}, dates : {len(dt_cols)}."
        )

    # ══════════════════════════════ QUALITÉ ═══════════════════════════════════
    with tabs[1]:
        st.subheader("Valeurs manquantes")
        miss = df.isna().mean().sort_values(ascending=False)
        miss = miss[miss > 0]
        if miss.empty:
            st.success("Aucune valeur manquante détectée.")
        else:
            fig_miss = go.Figure(go.Bar(
                x=miss.index.tolist(),
                y=(miss * 100).round(1).tolist(),
                marker_color=["#ff6b6b" if v > 20 else "#ffd166" if v > 5 else "#4dabf7"
                              for v in miss.values],
                text=[f"{v:.1f}%" for v in (miss * 100).values],
                textposition="outside",
            ))
            fig_miss.update_layout(yaxis_title="% manquantes", xaxis_title="Colonne",
                                   yaxis_range=[0, min(110, miss.max() * 120)])
            style_figure(fig_miss)
            st.plotly_chart(fig_miss, use_container_width=True)
            st.caption("Rouge > 20 % | Orange > 5 % | Bleu ≤ 5 %")

        st.subheader("Outliers (variables numériques)")
        if not num_cols:
            st.info("Aucune colonne numérique.")
        else:
            outlier_rows = []
            for col in num_cols:
                s = df[col].dropna()
                if len(s) < 4:
                    continue
                q1, q3 = s.quantile(0.25), s.quantile(0.75)
                iqr = q3 - q1
                n_iqr = int(((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum())
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    zs = np.abs(stats.zscore(s, nan_policy="omit"))
                n_z = int((zs > 3).sum())
                outlier_rows.append({"Colonne": col, "Outliers IQR": n_iqr,
                                     "% IQR": round(100 * n_iqr / len(s), 1),
                                     "Outliers Z>3": n_z,
                                     "% Z": round(100 * n_z / len(s), 1)})
            if outlier_rows:
                st.dataframe(pd.DataFrame(outlier_rows), use_container_width=True)
                st.caption("IQR : points en dehors de [Q1−1.5·IQR, Q3+1.5·IQR]. Z>3 : distance > 3 écarts-types.")

        st.subheader("Doublons")
        if n_dup == 0:
            st.success("Aucune ligne dupliquée.")
        else:
            st.warning(f"{n_dup} lignes identiques détectées sur {len(df):,} lignes ({100*n_dup/len(df):.1f}%).")
            if st.checkbox("Afficher les lignes dupliquées"):
                st.dataframe(df[df.duplicated(keep=False)], use_container_width=True)

    # ════════════════════════════ UNIVARIÉ ════════════════════════════════════
    with tabs[2]:
        all_cols = num_cols + cat_cols + dt_cols
        if not all_cols:
            st.warning("Aucune colonne exploitable.")
        else:
            sel_col = st.selectbox("Sélectionner une variable", all_cols)

            if sel_col in num_cols:
                prof = profile_numeric(df[sel_col])
                st.subheader(f"Profil numérique — {sel_col}")
                # Métriques principales
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("n valides", prof.get("n", "—"))
                c2.metric("Manquantes", f"{prof.get('manquantes', 0)} ({prof.get('% manquantes', 0):.1f}%)")
                c3.metric("Moyenne", prof.get("moyenne", "—"))
                c4.metric("Médiane", prof.get("médiane", "—"))
                c5, c6, c7, c8 = st.columns(4)
                c5.metric("Écart-type", prof.get("écart-type", "—"))
                c6.metric("Asymétrie", prof.get("asymétrie", "—"))
                c7.metric("Outliers IQR", prof.get("outliers IQR", "—"))
                c8.metric("Outliers Z>3", prof.get("outliers Z>3", "—"))

                # Shapiro
                p_shap = prof.get("Shapiro p")
                if p_shap not in (None, "—"):
                    is_normal = float(p_shap) >= 0.05
                    label = "Distribution normale (Shapiro p ≥ 0.05)" if is_normal \
                            else "Distribution non normale (Shapiro p < 0.05)"
                    (st.success if is_normal else st.warning)(
                        f"**Test de normalité Shapiro-Wilk** — W = {prof['Shapiro W']}, p = {_pval_badge(float(p_shap))} → {label}"
                    )

                # Tableau complet
                with st.expander("Tableau complet des statistiques"):
                    st.dataframe(pd.DataFrame(prof, index=["valeur"]).T, use_container_width=True)

                # Graphiques
                g1, g2 = st.tabs(["Histogramme + KDE", "Boîte à moustaches"])
                with g1:
                    show_outliers = st.checkbox("Masquer les outliers IQR", value=False, key=f"mask_{sel_col}")
                    plot_s = df[sel_col].copy()
                    if show_outliers:
                        flag = _outlier_flag(plot_s)
                        plot_s = plot_s[~flag]
                    fig = px.histogram(plot_s.dropna(), nbins=40, marginal="violin",
                                       color_discrete_sequence=["#4dabf7"],
                                       labels={plot_s.name: sel_col})
                    fig.update_layout(xaxis_title=sel_col, yaxis_title="Fréquence")
                    style_figure(fig)
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    color_by = st.selectbox("Colorer par", ["—"] + cat_cols, key=f"bxcat_{sel_col}")
                    fig = px.box(df, y=sel_col,
                                 x=None if color_by == "—" else color_by,
                                 color=None if color_by == "—" else color_by,
                                 points="outliers",
                                 color_discrete_sequence=px.colors.qualitative.Set2)
                    style_figure(fig)
                    st.plotly_chart(fig, use_container_width=True)

            elif sel_col in cat_cols:
                prof = profile_categorical(df[sel_col])
                st.subheader(f"Profil catégoriel — {sel_col}")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("n valides", prof["n"])
                c2.metric("Manquantes", f"{prof['manquantes']} ({prof['% manquantes']:.1f}%)")
                c3.metric("Modalités uniques", prof["modalités uniques"])
                c4.metric("Mode", f"{prof['mode']} ({prof['% mode']:.1f}%)")

                vc = df[sel_col].dropna().astype(str).value_counts().reset_index()
                vc.columns = ["Modalité", "Effectif"]
                vc["% total"] = (100 * vc["Effectif"] / vc["Effectif"].sum()).round(1)

                g1, g2 = st.tabs(["Barres", "Tableau de fréquences"])
                with g1:
                    top_n = st.slider("Top N modalités", 5, min(50, len(vc)), min(20, len(vc)),
                                      key=f"topn_{sel_col}")
                    fig = px.bar(vc.head(top_n), x="Modalité", y="Effectif",
                                 color="Effectif", color_continuous_scale="Blues",
                                 text="% total")
                    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                    fig.update_layout(xaxis_tickangle=-40, coloraxis_showscale=False)
                    style_figure(fig)
                    st.plotly_chart(fig, use_container_width=True)
                with g2:
                    st.dataframe(vc, use_container_width=True)

            elif sel_col in dt_cols:
                st.subheader(f"Profil temporel — {sel_col}")
                s = df[sel_col].dropna()
                st.metric("Plage temporelle", f"{s.min().date()} → {s.max().date()}")
                st.metric("Valeurs manquantes", f"{df[sel_col].isna().sum()}")
                # Distribution par année si pertinent
                years = s.dt.year.value_counts().sort_index()
                fig = px.bar(x=years.index, y=years.values,
                             labels={"x": "Année", "y": "Nombre d'observations"},
                             color_discrete_sequence=["#39d98a"])
                style_figure(fig)
                st.plotly_chart(fig, use_container_width=True)

    # ═══════════════════════════ RELATIONS ════════════════════════════════════
    with tabs[3]:
        rel_type = st.radio(
            "Type de relation à analyser",
            ["Numérique × Numérique", "Numérique × Catégorielle", "Catégorielle × Catégorielle"],
            horizontal=True,
        )

        # ── Num × Num ──────────────────────────────────────────────────────
        if rel_type == "Numérique × Numérique":
            if len(num_cols) < 2:
                st.info("Il faut au moins deux colonnes numériques.")
            else:
                c1, c2 = st.columns(2)
                x_col = c1.selectbox("Variable X (explicative)", num_cols, index=0)
                y_options = [c for c in num_cols if c != x_col]
                y_col = c2.selectbox("Variable Y (réponse)", y_options, index=0)
                color_col = st.selectbox("Colorer par (optionnel)", ["—"] + cat_cols)

                res = bivariate_num_num(df, x_col, y_col)
                if res is None:
                    st.warning("Régression impossible : variance nulle ou trop peu de données.")
                else:
                    data_plot = res["data"].copy()
                    if color_col != "—" and color_col in df.columns:
                        data_plot = data_plot.join(df[color_col])
                    fig = px.scatter(
                        data_plot, x=x_col, y=y_col,
                        color=None if color_col == "—" else color_col,
                        trendline="ols", trendline_scope="overall",
                        opacity=0.7, color_discrete_sequence=px.colors.qualitative.Set2,
                    )
                    fig.update_layout(xaxis_title=x_col, yaxis_title=y_col)
                    style_figure(fig)
                    st.plotly_chart(fig, use_container_width=True)

                    # Résultats
                    st.markdown("**Corrélation de Pearson (linéaire)**")
                    r1, r2, r3 = st.columns(3)
                    r1.metric("r de Pearson", f"{res['pearson_r']:.4f}")
                    r2.metric("R²", f"{res['pearson_r2']:.4f}")
                    r3.metric("p-value", _pval_badge(res["pearson_p"]))

                    st.markdown("**Corrélation de Spearman (rangs — non linéaire)**")
                    s1, s2 = st.columns(2)
                    s1.metric("ρ de Spearman", f"{res['spearman_r']:.4f}")
                    s2.metric("p-value", _pval_badge(res["spearman_p"]))

                    st.markdown("**Régression linéaire simple (OLS)**")
                    reg1, reg2, reg3 = st.columns(3)
                    reg1.metric("Pente", f"{res['pente']:.4g}")
                    reg2.metric("Intercept", f"{res['intercept']:.4g}")
                    reg3.metric("Erreur-type pente", f"{res['stderr']:.4g}")

                    p_val = res["pearson_p"]
                    force = abs(res["pearson_r"])
                    qualif = "forte" if force > 0.7 else "modérée" if force > 0.4 else "faible"
                    direction = "positive" if res["pearson_r"] > 0 else "négative"
                    explain(
                        f"Corrélation de Pearson r = {res['pearson_r']:.3f} ({qualif}, {direction}). "
                        f"Le modèle OLS explique {100*res['pearson_r2']:.1f}% de la variance de {y_col}. "
                        f"p-value = {_pval_badge(p_val)}. "
                        f"Spearman ρ = {res['spearman_r']:.3f} (robuste aux non-linéarités et outliers)."
                    )

                    # Résidus
                    with st.expander("Graphique des résidus"):
                        pred = res["intercept"] + res["pente"] * data_plot[x_col]
                        resid = data_plot[y_col] - pred
                        fig_r = px.scatter(x=pred, y=resid, labels={"x": "Valeurs ajustées", "y": "Résidus"},
                                           color_discrete_sequence=["#ffd166"], opacity=0.6)
                        fig_r.add_hline(y=0, line_dash="dash", line_color="#ff6b6b")
                        style_figure(fig_r)
                        st.plotly_chart(fig_r, use_container_width=True)
                        st.caption("Les résidus doivent être distribués aléatoirement autour de 0 (homoscédasticité).")

        # ── Num × Cat ──────────────────────────────────────────────────────
        elif rel_type == "Numérique × Catégorielle":
            if not num_cols or not cat_cols:
                st.info("Il faut au moins une colonne numérique et une colonne catégorielle.")
            else:
                c1, c2 = st.columns(2)
                cat_col = c1.selectbox("Variable catégorielle (groupes)", cat_cols)
                num_col = c2.selectbox("Variable numérique à comparer", num_cols)

                # Filtrer les groupes ayant assez de données
                valid_groups = [g for g in df[cat_col].dropna().unique()
                                if df.loc[df[cat_col] == g, num_col].dropna().shape[0] >= 2]
                if len(valid_groups) < 2:
                    st.warning("Moins de 2 groupes avec des données suffisantes (n ≥ 2).")
                else:
                    data_filt = df[df[cat_col].isin(valid_groups)]
                    fig = px.box(data_filt, x=cat_col, y=num_col, color=cat_col,
                                 points="outliers", color_discrete_sequence=px.colors.qualitative.Set2)
                    fig.update_layout(showlegend=False, xaxis_tickangle=-30)
                    style_figure(fig)
                    st.plotly_chart(fig, use_container_width=True)

                    res = bivariate_num_cat(data_filt, cat_col, num_col)
                    if res is not None:
                        if res["type"] == "2g":
                            st.markdown("**Test de Welch (t-test, 2 groupes)**")
                            t1, t2 = st.columns(2)
                            t1.metric("t de Welch", f"{res['t_stat']:.4f}")
                            t2.metric("p-value", _pval_badge(res["t_p"]))
                            st.markdown("**Test de Mann-Whitney U (non paramétrique)**")
                            u1, u2 = st.columns(2)
                            u1.metric("U", f"{res['u_stat']:.1f}")
                            u2.metric("p-value", _pval_badge(res["u_p"]))
                        else:
                            st.markdown(f"**ANOVA unidirectionnelle ({res['n_groups']} groupes)**")
                            a1, a2, a3 = st.columns(3)
                            a1.metric("F", f"{res['f_stat']:.4f}")
                            a2.metric("p-value", _pval_badge(res["f_p"]))
                            a3.metric("η² (taille d'effet)", f"{res['eta2']:.4f}")
                            st.markdown("**Kruskal-Wallis (non paramétrique)**")
                            k1, k2 = st.columns(2)
                            k1.metric("H", f"{res['h_stat']:.4f}")
                            k2.metric("p-value", _pval_badge(res["h_p"]))

                        # Tableau des moyennes par groupe
                        with st.expander("Statistiques par groupe"):
                            grp_stats = data_filt.groupby(cat_col)[num_col].agg(
                                n="count", moyenne="mean", médiane="median", écart_type="std"
                            ).round(3)
                            st.dataframe(grp_stats, use_container_width=True)

        # ── Cat × Cat ──────────────────────────────────────────────────────
        else:
            if len(cat_cols) < 2:
                st.info("Il faut au moins deux colonnes catégorielles.")
            else:
                c1, c2 = st.columns(2)
                col1 = c1.selectbox("Variable catégorielle 1", cat_cols, index=0)
                col2 = c2.selectbox("Variable catégorielle 2",
                                    [c for c in cat_cols if c != col1], index=0)

                res = bivariate_cat_cat(df, col1, col2)
                if res is None:
                    st.warning("Test impossible : trop peu de modalités ou de données.")
                else:
                    st.markdown("**Table de contingence**")
                    st.dataframe(res["contingency"], use_container_width=True)

                    # Heatmap de la table de contingence
                    fig = px.imshow(res["contingency"], color_continuous_scale="Blues",
                                    labels={"color": "Effectif"},
                                    text_auto=True, aspect="auto")
                    fig.update_layout(xaxis_title=col2, yaxis_title=col1)
                    style_figure(fig)
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("**Test du χ² d'indépendance**")
                    x1, x2, x3, x4 = st.columns(4)
                    x1.metric("χ²", f"{res['chi2']:.4f}")
                    x2.metric("ddl", res["dof"])
                    x3.metric("p-value", _pval_badge(res["p"]))
                    x4.metric("V de Cramér", f"{res['cramers_v']:.4f}")

                    v = res["cramers_v"]
                    assoc = "forte" if v > 0.5 else "modérée" if v > 0.3 else "faible" if v > 0.1 else "négligeable"
                    explain(
                        f"χ²({res['dof']}) = {res['chi2']:.3f}, p = {_pval_badge(res['p'])}. "
                        f"V de Cramér = {v:.3f} → association {assoc} entre les deux variables catégorielles. "
                        f"(V = 0 : aucune association, V = 1 : association parfaite ; seuils indicatifs : 0.1 / 0.3 / 0.5)"
                    )

    # ══════════════════════════ CORRÉLATIONS ══════════════════════════════════
    with tabs[4]:
        if len(num_cols) < 2:
            st.info("Il faut au moins deux colonnes numériques pour calculer une matrice de corrélation.")
        else:
            method = st.radio("Méthode", ["Pearson", "Spearman"], horizontal=True)
            min_periods = st.slider("Minimum d'observations communes", 3, 30, 10)

            corr_data = df[num_cols].dropna(thresh=2)
            corr_m = corr_data.corr(method=method.lower(), min_periods=min_periods)

            # Masquer le triangle supérieur
            mask_upper = np.triu(np.ones(corr_m.shape, dtype=bool), k=1)
            corr_display = corr_m.copy()
            corr_display[mask_upper] = np.nan

            fig = px.imshow(
                corr_display,
                color_continuous_scale="RdBu_r",
                zmin=-1, zmax=1,
                text_auto=".2f",
                aspect="auto",
                labels={"color": f"r ({method})"},
            )
            fig.update_traces(textfont_size=9)
            fig.update_layout(title=f"Matrice de corrélation — {method}")
            style_figure(fig)
            st.plotly_chart(fig, use_container_width=True)

            # Top corrélations absolues
            st.subheader("Top corrélations les plus fortes")
            pairs = []
            for i, c1 in enumerate(num_cols):
                for j, c2 in enumerate(num_cols):
                    if j <= i:
                        continue
                    val = corr_m.loc[c1, c2]
                    if not np.isnan(val):
                        pairs.append({"Variable 1": c1, "Variable 2": c2,
                                      f"r ({method})": round(val, 4),
                                      "|r|": round(abs(val), 4)})
            if pairs:
                pairs_df = pd.DataFrame(pairs).sort_values("|r|", ascending=False)
                st.dataframe(pairs_df.drop(columns=["|r|"]).head(20), use_container_width=True)

            explain(
                f"Pearson mesure les corrélations linéaires (sensible aux outliers). "
                "Spearman est basé sur les rangs — plus robuste aux distributions asymétriques. "
                "Les valeurs proches de ±1 indiquent une forte corrélation."
            )

    # ═══════════════════════════ EXPORT ═══════════════════════════════════════
    with tabs[5]:
        st.subheader("Exporter les données")
        remove_dup = st.checkbox("Supprimer les doublons à l'export", value=True)
        export_df = df.drop_duplicates() if remove_dup else df

        col_a, col_b = st.columns(2)
        with col_a:
            cleaned_csv = export_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇ CSV nettoyé",
                cleaned_csv,
                f"{source_name or 'donnees'}_nettoye.csv",
                "text/csv",
                use_container_width=True,
            )
        with col_b:
            # Rapport PDF
            lines = [
                f"Fichier : {source_name}",
                f"Lignes : {len(df):,}  |  Colonnes : {len(df.columns)}",
                f"Doublons : {n_dup}",
                f"Colonnes numériques : {', '.join(num_cols) or 'aucune'}",
                f"Colonnes catégorielles : {', '.join(cat_cols) or 'aucune'}",
                "",
                "── Profils numériques ──",
            ]
            for col in num_cols[:15]:
                p = profile_numeric(df[col])
                lines.append(
                    f"  {col}: n={p.get('n', '?')}, moy={p.get('moyenne', '?')}, "
                    f"med={p.get('médiane', '?')}, sd={p.get('écart-type', '?')}, "
                    f"outliers IQR={p.get('outliers IQR', '?')}"
                )
            lines += ["", "── Profils catégoriels ──"]
            for col in cat_cols[:10]:
                p = profile_categorical(df[col])
                lines.append(f"  {col}: {p['modalités uniques']} modalités, mode={p['mode']} ({p['% mode']:.1f}%)")
            pdf = build_pdf_report("ORNI-LAB - Analyse CSV", lines)
            if pdf:
                st.download_button(
                    "⬇ Rapport PDF",
                    pdf,
                    "orni_lab_analyse_csv.pdf",
                    "application/pdf",
                    use_container_width=True,
                )

        st.subheader("Statistiques descriptives complètes")
        if num_cols:
            st.dataframe(
                df[num_cols].describe().T.round(4),
                use_container_width=True,
            )

    # ── Notes pédagogiques ────────────────────────────────────────────────────
    learning_notes(
        "L'analyse exploratoire précède toute modélisation : elle révèle outliers, "
        "distributions non normales et corrélations parasites.",
        "Préférez Spearman à Pearson si la distribution est asymétrique ou si les outliers "
        "sont nombreux — Spearman est insensible aux valeurs extrêmes.",
        "Un V de Cramér > 0.3 entre deux variables catégorielles indique une association "
        "non négligeable à interpréter biologiquement.",
    )
