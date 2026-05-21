from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from core.export import build_pdf_report
from utils.ui import csv_template_button, data_incompatible, explain, learning_notes, module_intro, section, style_figure, teacher_note


def generate_two_groups(seed: int, n_a: int, n_b: int, mean_a: float, mean_b: float, sd: float) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    values = np.concatenate([rng.normal(mean_a, sd, n_a), rng.normal(mean_b, sd, n_b)]).clip(0, None)
    return pd.DataFrame({"Habitat": ["Forêt restaurée"] * n_a + ["Forêt dégradée"] * n_b, "Succès reproducteur": values})


def _apply_transform(vals: np.ndarray, method: str) -> np.ndarray:
    if method == "log(Y+1)":
        return np.log1p(vals)
    if method == "√Y":
        return np.sqrt(np.clip(vals, 0, None))
    return vals


def _shapiro_table(data: pd.DataFrame, hab_label: str, val_label: str, groups) -> dict[str, dict]:
    results = {}
    for g in groups:
        mask = (data[hab_label].astype(str) == str(g))
        vals = data.loc[mask, val_label].dropna().values
        if len(vals) >= 3:
            stat, pval = stats.shapiro(vals[:5000])
            results[str(g)] = {
                "stat": float(stat), "pval": float(pval), "n": len(vals), "vals": vals,
                "skew": float(pd.Series(vals).skew()),
            }
    return results


def _group_summary(data: pd.DataFrame, hab_label: str, val_label: str, groups) -> pd.DataFrame:
    rows = []
    for g in groups:
        mask = (data[hab_label].astype(str) == str(g))
        v = data.loc[mask, val_label].dropna()
        rows.append({
            "Groupe": str(g),
            "n": len(v),
            "Moyenne": round(float(v.mean()), 3) if len(v) > 0 else np.nan,
            "Médiane": round(float(v.median()), 3) if len(v) > 0 else np.nan,
            "Écart-type": round(float(v.std()), 3) if len(v) > 1 else np.nan,
            "Asymétrie": round(float(v.skew()), 2) if len(v) > 2 else np.nan,
        })
    return pd.DataFrame(rows)


def render(context: dict) -> None:
    is_data = context.get("data") is not None
    section(
        "Tests statistiques",
        None if is_data else "Exemple : comparaison du succès reproducteur entre deux habitats.",
    )
    module_intro(
        "Un test statistique évalue si une différence observée entre groupes est compatible avec le hasard (H₀) ou si elle est trop grande pour être due au seul hasard (H₁). Il produit une p-value : probabilité d'obtenir un écart au moins aussi grand si H₀ était vraie.",
        "Il sert à formaliser une comparaison tout en maîtrisant le risque de se tromper : risque α (faux positif, seuil = 0,05) et risque β (faux négatif). La normalité des données détermine le choix du test.",
        "En ornithologie, il permet de comparer le succès reproducteur entre habitats, l'abondance selon les années, ou l'effet d'une mesure de conservation — en distinguant une vraie différence biologique du bruit d'échantillonnage.",
    )

    left, right = st.columns([0.9, 1.5])

    # ── Sélection des variables ─────────────────────────────────────────────
    if is_data:
        data_src = context["data"]
        numeric_cols = context["numeric_columns"]
        cat_cols     = context["categorical_columns"]

        if not numeric_cols or not cat_cols:
            data_incompatible(
                "Ce module compare des groupes : il nécessite au moins une colonne numérique (la mesure à comparer) "
                "et une colonne catégorielle (les groupes, ex. : Habitat, Sexe, Site).",
                [
                    "Vérifiez que votre fichier contient une colonne de mesures numériques (abondance, masse, longueur…).",
                    "Ajoutez une colonne de groupe avec des étiquettes texte (ex. : 'Forêt', 'Savane', 'M', 'F').",
                    "Si toutes vos colonnes sont numériques, encodez les groupes en texte et rechargez le fichier.",
                    "Téléchargez l'exemple CSV pour voir la structure Habitat / Succès_repro attendue.",
                ],
            )
            return

        with left:
            csv_template_button(
                pd.DataFrame({"Habitat": ["Forêt", "Forêt", "Savane", "Savane"], "Succes_repro": [3.2, 2.9, 1.8, 2.1]}),
                "template_tests_stat.csv",
            )
            st.markdown("**Variables**")
            value_col = st.selectbox("Variable numérique à comparer", numeric_cols, key="test_val")

            # Proposer toutes colonnes avec ≥ 2 modalités comme groupe potentiel
            all_cat = [c for c in context["data"].columns
                       if c != value_col and context["data"][c].nunique(dropna=True) >= 2]
            if not all_cat:
                all_cat = cat_cols
            group_col = st.selectbox("Variable de groupe", all_cat, key="test_grp")

            st.markdown("**Options**")
            transform = st.selectbox(
                "Transformation de Y",
                ["Aucune", "log(Y+1)", "√Y"],
                key="test_transf",
                help="Utile pour normaliser des comptages (log) ou des pourcentages (√).",
            )
            remove_outliers = st.checkbox(
                "Exclure les valeurs aberrantes (> 3 × IQR)",
                value=False,
                key="test_outliers",
                help="Retire les points extrêmes définis par la règle 3×IQR par groupe.",
            )

        # ── Construction du sous-tableau ──────────────────────────────────
        sub_raw = data_src[[group_col, value_col]].copy()
        sub_raw[group_col]  = sub_raw[group_col].astype(str)
        sub_raw[value_col]  = pd.to_numeric(sub_raw[value_col], errors="coerce")
        sub_raw = sub_raw.dropna()

        all_groups = sorted(sub_raw[group_col].unique().tolist())

        # Sélection des groupes si trop nombreux
        selected_groups = all_groups
        if len(all_groups) > 6:
            with left:
                st.caption(f"⚠ {len(all_groups)} modalités — sélectionnez 2 à 6 groupes :")
                selected_groups = st.multiselect(
                    "Groupes à comparer",
                    options=all_groups,
                    default=all_groups[:4],
                    max_selections=6,
                    key="test_grp_select",
                )
            if len(selected_groups) < 2:
                data_incompatible(
                    "Sélectionnez au moins 2 groupes pour effectuer le test.",
                    ["Cochez au moins 2 groupes dans la liste ci-dessus."],
                )
                return

        sub_all = sub_raw[sub_raw[group_col].isin(selected_groups)].copy()

        if len(selected_groups) < 2 or sub_all[group_col].nunique() < 2:
            data_incompatible(
                f"La colonne <b>{group_col}</b> ne contient qu'une seule modalité après filtrage.",
                [
                    "Choisissez une autre colonne de groupe contenant ≥ 2 valeurs distinctes.",
                    "Vérifiez que les valeurs manquantes ne masquent pas une deuxième modalité.",
                ],
            )
            return

        # Filtre outliers par groupe (IQR)
        if remove_outliers:
            def _iqr_filter(grp):
                q1, q3 = grp[value_col].quantile(0.25), grp[value_col].quantile(0.75)
                iqr = q3 - q1
                return grp[(grp[value_col] >= q1 - 3 * iqr) & (grp[value_col] <= q3 + 3 * iqr)]
            sub_filtered = sub_all.groupby(group_col, group_keys=False).apply(_iqr_filter)
            n_removed = len(sub_all) - len(sub_filtered)
            sub_all = sub_filtered
            if n_removed > 0:
                with left:
                    st.caption(f"ℹ {n_removed} valeur(s) aberrante(s) exclue(s).")

        # Transformation
        sub_all = sub_all.copy()
        if transform != "Aucune":
            sub_all[value_col] = _apply_transform(sub_all[value_col].values, transform)
        display_val = f"{transform[:5]}({value_col})" if transform != "Aucune" else value_col

        groups    = np.array(selected_groups)
        data      = sub_all
        hab_label = group_col
        val_label = value_col

    else:
        # ── Mode simulation ──────────────────────────────────────────────
        with left:
            n_a    = st.slider("Nids en forêt restaurée", 8, 120, 36)
            n_b    = st.slider("Nids en forêt dégradée",  8, 120, 34)
            mean_a = st.slider("Moyenne restaurée",  0.0, 6.0, 3.2, step=0.1)
            mean_b = st.slider("Moyenne dégradée",   0.0, 6.0, 2.4, step=0.1)
            sd     = st.slider("Variabilité entre nids", 0.2, 3.0, 1.1, step=0.1)
            seed   = st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=33)
        data      = generate_two_groups(int(seed), n_a, n_b, mean_a, mean_b, sd)
        hab_label = "Habitat"
        val_label = "Succès reproducteur"
        display_val = val_label
        groups    = data[hab_label].unique()
        transform = "Aucune"

    n_groups = len(groups)

    # ── Résumé par groupe ────────────────────────────────────────────────────
    summary_df = _group_summary(data, hab_label, val_label, groups)

    # ── Avertissement si certains groupes ont trop peu d'observations ────────
    tiny_groups = summary_df[summary_df["n"] < 5]
    if len(tiny_groups) > 0 and is_data:
        st.warning(
            f"⚠ {len(tiny_groups)} groupe(s) avec moins de 5 observations "
            f"({', '.join(tiny_groups['Groupe'].tolist())}). "
            "Les tests peuvent manquer de puissance. Envisagez de regrouper des catégories similaires."
        )

    # ── Graphique ────────────────────────────────────────────────────────────
    with right:
        fig = px.box(data, x=hab_label, y=val_label, points="all", color=hab_label)
        fig.update_layout(showlegend=False, xaxis_title=hab_label, yaxis_title=display_val)
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    with left:
        st.markdown("**Résumé par groupe**")
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        # Recommandation automatique du test
        shapiro_pre = _shapiro_table(data, hab_label, val_label, groups)
        normal_flag = all(r["pval"] > 0.05 for r in shapiro_pre.values()) if shapiro_pre else True
        skewed      = any(abs(r.get("skew", 0)) > 1.0 for r in shapiro_pre.values())

        if transform == "Aucune" and skewed:
            st.info("Asymétrie détectée. Essayez la transformation log(Y+1) ou √Y pour améliorer la normalité.")

        if normal_flag:
            st.success("✓ Normalité compatible — test paramétrique recommandé.")
        else:
            st.warning("✗ Non-normalité détectée — test non-paramétrique recommandé.")

    # ── Calcul des tests ─────────────────────────────────────────────────────
    shapiro = _shapiro_table(data, hab_label, val_label, groups)
    all_normal = all(r["pval"] > 0.05 for r in shapiro.values()) if shapiro else True

    if n_groups == 2:
        g0, g1 = str(groups[0]), str(groups[1])
        group_a = data.loc[data[hab_label].astype(str) == g0, val_label].dropna().values
        group_b = data.loc[data[hab_label].astype(str) == g1, val_label].dropna().values
        if len(group_a) < 2 or len(group_b) < 2:
            data_incompatible(
                "Un des deux groupes n'a pas assez d'observations (minimum 2) pour effectuer un test.",
                ["Vérifiez les groupes sélectionnés ou réduisez le filtre de valeurs aberrantes."],
            )
            return
        welch  = stats.ttest_ind(group_a, group_b, equal_var=False)
        mwu    = stats.mannwhitneyu(group_a, group_b, alternative="two-sided")
        effect = float(np.mean(group_a) - np.mean(group_b))
        pooled_sd = float(np.sqrt((np.std(group_a, ddof=1) ** 2 + np.std(group_b, ddof=1) ** 2) / 2))
        cohens_d  = effect / pooled_sd if pooled_sd > 0 else 0.0
    else:
        valid_series = [
            data.loc[data[hab_label].astype(str) == str(g), val_label].dropna().values
            for g in groups
            if len(data.loc[data[hab_label].astype(str) == str(g), val_label].dropna()) >= 2
        ]
        if len(valid_series) < 2:
            data_incompatible(
                "Pas assez de groupes avec des données suffisantes (≥ 2 obs chacun) pour l'ANOVA / Kruskal-Wallis.",
                [
                    "Vérifiez que les groupes sélectionnés ne contiennent pas trop de valeurs manquantes.",
                    "Réduisez le filtre de valeurs aberrantes ou augmentez la taille d'échantillon.",
                    "Si vous avez exactement 2 groupes valides, revenez à une sélection de 2 groupes.",
                ],
            )
            return
        anova_f,   anova_p   = stats.f_oneway(*valid_series)
        kruskal_h, kruskal_p = stats.kruskal(*valid_series)
        all_vals  = np.concatenate(valid_series)
        ss_between = sum(len(s) * (np.mean(s) - np.mean(all_vals)) ** 2 for s in valid_series)
        ss_total   = sum(np.sum((s - np.mean(all_vals)) ** 2) for s in valid_series)
        eta2 = float(ss_between / ss_total) if ss_total > 0 else 0.0

    # ── Expander cours ───────────────────────────────────────────────────────
    with st.expander("Cours : Logique des tests statistiques et choix du test"):
        st.markdown("#### Hypothèses H₀ et H₁")
        st.markdown(
            "- **H₀ (hypothèse nulle)** : il n'y a pas de différence entre les groupes\n"
            "- **H₁ (hypothèse alternative)** : il existe une différence réelle\n\n"
            "| p-value | Décision | Interprétation |\n"
            "|---------|----------|----------------|\n"
            "| < 0,05 | Rejeter H₀ | Différence significative |\n"
            "| ≥ 0,05 | Ne pas rejeter H₀ | Pas de preuve suffisante |\n"
        )
        st.markdown("#### Arbre de décision")
        st.markdown(
            "```\n"
            "Comparer des moyennes/médianes\n"
            "│\n"
            "├── 2 groupes\n"
            "│   ├── Normal (Shapiro p > 0,05) → Test t de Welch\n"
            "│   └── Non-normal ou n < 20     → Mann-Whitney U\n"
            "│\n"
            "└── ≥ 3 groupes\n"
            "    ├── Normal → ANOVA  →  post-hoc Tukey HSD\n"
            "    └── Non-normal → Kruskal-Wallis  →  Dunn-Bonferroni\n"
            "```\n"
        )
        st.markdown(
            "| Taille d'effet | Faible | Modéré | Fort |\n"
            "|---|---|---|---|\n"
            "| d de Cohen | 0,2 | 0,5 | 0,8 |\n"
            "| η² (ANOVA) | 0,01 | 0,06 | 0,14 |\n"
        )

    # ── Onglets résultats ─────────────────────────────────────────────────────
    tabs = st.tabs(["Normalité", "Test paramétrique", "Test non-paramétrique", "Export"])

    # --- Normalité ---
    with tabs[0]:
        st.markdown("#### Shapiro-Wilk (H₀ : distribution normale)")
        sw_rows = [
            {
                "Groupe": g,
                "n": r["n"],
                "W": round(r["stat"], 4),
                "p-value": round(r["pval"], 4),
                "Asymétrie": round(r.get("skew", 0), 2),
                "Décision": "Normale ✓" if r["pval"] > 0.05 else "Non-normale ✗",
            }
            for g, r in shapiro.items()
        ]
        st.dataframe(pd.DataFrame(sw_rows), use_container_width=True, hide_index=True)
        if all_normal:
            st.success("Toutes les distributions sont compatibles avec la normalité (p > 0.05) → test paramétrique approprié.")
        else:
            st.warning("Au moins un groupe s'écarte de la normalité → test non-paramétrique recommandé.")
            if transform == "Aucune":
                st.info("Essayez la transformation log(Y+1) ou √Y dans les options ci-dessus pour améliorer la normalité.")

        groups_with_data = [g for g in groups if str(g) in shapiro]
        n_cols = min(len(groups_with_data), 4)
        if n_cols > 0:
            st.markdown("**Q-Q plots** (points alignés = normale)")
            cols = st.columns(n_cols)
            for i, g in enumerate(groups_with_data[:4]):
                r = shapiro[str(g)]
                (osm, osr), (slope_qq, intercept_qq, _) = stats.probplot(r["vals"])
                fig_qq = go.Figure()
                fig_qq.add_scatter(x=osm, y=osr, mode="markers", marker={"size": 5, "color": "#4dabf7"})
                x_line = np.array([float(min(osm)), float(max(osm))])
                fig_qq.add_scatter(x=x_line, y=slope_qq * x_line + intercept_qq,
                                   mode="lines", line={"dash": "dash", "color": "#39d98a", "width": 2})
                fig_qq.update_layout(title={"text": str(g), "font": {"size": 12}},
                                     xaxis_title="Quantiles théoriques", yaxis_title="Quantiles observés",
                                     height=260, showlegend=False, margin={"l": 40, "r": 10, "t": 35, "b": 40})
                style_figure(fig_qq)
                with cols[i]:
                    st.plotly_chart(fig_qq, use_container_width=True)

        teacher_note(
            "Shapiro-Wilk est le plus puissant pour n < 50. Pour n > 50, préférer Lilliefors ou le Q-Q plot visuel. "
            "Un Q-Q plot donne une information complémentaire que la p-value seule ne fournit pas.",
            context,
        )

    # --- Paramétrique ---
    with tabs[1]:
        if n_groups == 2:
            st.markdown(f"#### Test t de Welch — {g0} vs {g1}")
            st.caption("Comparaison de deux moyennes avec variances inégales possibles.")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Différence des moyennes", f"{effect:+.3g}")
            c2.metric("t de Welch", f"{welch.statistic:.3f}")
            c3.metric("p-value", f"{welch.pvalue:.3g}")
            c4.metric("d de Cohen", f"{cohens_d:.2f}")
            conc = "significative (p < 0.05)" if welch.pvalue < 0.05 else "non significative (p ≥ 0.05)"
            mag  = "grande" if abs(cohens_d) > 0.8 else "modérée" if abs(cohens_d) > 0.5 else "faible"
            explain(f"Différence {g0}−{g1} = {effect:+.3g} — {conc}. Taille d'effet d = {cohens_d:.2f} ({mag}).")
            if not all_normal:
                st.info("Données non normales — vérifiez aussi l'onglet Test non-paramétrique.")
        else:
            st.markdown(f"#### ANOVA à un facteur — {n_groups} groupes")
            c1, c2, c3 = st.columns(3)
            c1.metric("F", f"{anova_f:.3f}")
            c2.metric("p-value", f"{anova_p:.3g}")
            c3.metric("η²", f"{eta2:.3f}", help="Part de variance expliquée par le facteur groupe")
            if anova_p < 0.05:
                explain(f"ANOVA significative (F = {anova_f:.3f}, p = {anova_p:.3g}, η² = {eta2:.3f}). "
                        "Une analyse post-hoc est nécessaire pour identifier quels groupes diffèrent.")
            else:
                explain(f"ANOVA non significative (F = {anova_f:.3f}, p = {anova_p:.3g}).")
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
            if not all_normal:
                st.info("Données non normales — vérifiez aussi l'onglet Test non-paramétrique.")
        teacher_note(
            "Le test t de Welch ne suppose pas l'égalité des variances. "
            "L'ANOVA suppose normalité et homoscédasticité. "
            "d de Cohen : 0.2 = faible, 0.5 = modéré, 0.8 = fort. η² = SS_entre / SS_total.",
            context,
        )

    # --- Non-paramétrique ---
    with tabs[2]:
        if n_groups == 2:
            st.markdown(f"#### Mann-Whitney U — {g0} vs {g1}")
            st.caption("Alternative non-paramétrique au test t. Robuste aux non-normalités et aux valeurs aberrantes.")
            c1, c2 = st.columns(2)
            c1.metric("U statistic", f"{mwu.statistic:.1f}")
            c2.metric("p-value", f"{mwu.pvalue:.3g}")
            conc_mw = "significative (p < 0.05)" if mwu.pvalue < 0.05 else "non significative (p ≥ 0.05)"
            explain(f"Mann-Whitney U : différence {conc_mw} (U = {mwu.statistic:.1f}, p = {mwu.pvalue:.3g}).")
            if welch.pvalue < 0.05 and mwu.pvalue >= 0.05:
                st.warning("Test t significatif mais pas Mann-Whitney — inspectez les outliers ou la distribution.")
            elif welch.pvalue >= 0.05 and mwu.pvalue < 0.05:
                st.warning("Mann-Whitney significatif mais pas le test t — probable non-normalité influente.")
        else:
            st.markdown(f"#### Kruskal-Wallis — {n_groups} groupes")
            st.caption("Alternative non-paramétrique à l'ANOVA. Basé sur les rangs.")
            c1, c2 = st.columns(2)
            c1.metric("H statistic", f"{kruskal_h:.3f}")
            c2.metric("p-value", f"{kruskal_p:.3g}")
            if kruskal_p < 0.05:
                explain(f"Kruskal-Wallis significatif (H = {kruskal_h:.3f}, p = {kruskal_p:.3g}). "
                        "Tests de Dunn (Bonferroni) recommandés pour les comparaisons pairées.")
            else:
                explain(f"Kruskal-Wallis non significatif (H = {kruskal_h:.3f}, p = {kruskal_p:.3g}).")
            if anova_p < 0.05 and kruskal_p >= 0.05:
                st.warning("ANOVA significative mais pas Kruskal-Wallis — la normalité est peut-être critique ici.")
        teacher_note(
            "Mann-Whitney U = test de Wilcoxon à deux échantillons. "
            "Kruskal-Wallis est l'extension non-paramétrique de l'ANOVA. "
            "Post-hoc après Kruskal-Wallis : test de Dunn avec correction de Bonferroni.",
            context,
        )

    # --- Export ---
    with tabs[3]:
        st.download_button(
            "Exporter les données CSV",
            data.to_csv(index=False).encode("utf-8"),
            "orni_lab_tests.csv", "text/csv",
        )
        if n_groups == 2:
            pdf_lines = [
                f"Variable : {display_val}. Groupes : {g0} (n={len(group_a)}) vs {g1} (n={len(group_b)}).",
                f"Difference des moyennes = {effect:+.3g}. d de Cohen = {cohens_d:.3f}.",
                f"Test de Welch : t = {welch.statistic:.3f}, p = {welch.pvalue:.3g}.",
                f"Mann-Whitney U : U = {mwu.statistic:.1f}, p = {mwu.pvalue:.3g}.",
                "Shapiro-Wilk : " + " | ".join(f"{g} W={r['stat']:.4f} p={r['pval']:.4f}" for g, r in shapiro.items()),
            ]
        else:
            pdf_lines = [
                f"Variable : {display_val}. {n_groups} groupes.",
                f"ANOVA : F = {anova_f:.3f}, p = {anova_p:.3g}, eta2 = {eta2:.3f}.",
                f"Kruskal-Wallis : H = {kruskal_h:.3f}, p = {kruskal_p:.3g}.",
                "Shapiro-Wilk : " + " | ".join(f"{g} W={r['stat']:.4f} p={r['pval']:.4f}" for g, r in shapiro.items()),
            ]
        pdf = build_pdf_report("ORNI-LAB - Tests statistiques", pdf_lines)
        if pdf:
            st.download_button("Exporter le résumé PDF", pdf, "orni_lab_tests.pdf", "application/pdf")

    learning_notes(
        "Démarche : (1) Poser H₀/H₁, (2) Vérifier la normalité (Shapiro-Wilk), (3) Choisir le test, (4) Interpréter p-value ET taille d'effet.",
        "Une p-value significative ne prouve pas une importance biologique — un grand n peut rendre significative une différence négligeable. Toujours rapporter d ou η².",
        None if is_data else "Réduis le n progressivement : à partir de quel seuil la conclusion change-t-elle ?",
    )
