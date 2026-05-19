from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from core.export import build_pdf_report
from utils.ui import csv_template_button, explain, learning_notes, module_intro, section, style_figure, teacher_note


def generate_two_groups(seed: int, n_a: int, n_b: int, mean_a: float, mean_b: float, sd: float) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    values = np.concatenate([rng.normal(mean_a, sd, n_a), rng.normal(mean_b, sd, n_b)]).clip(0, None)
    return pd.DataFrame({"Habitat": ["Forêt restaurée"] * n_a + ["Forêt dégradée"] * n_b, "Succès reproducteur": values})


def _shapiro_table(data: pd.DataFrame, hab_label: str, val_label: str, groups: np.ndarray) -> dict[str, dict]:
    results = {}
    for g in groups:
        vals = data.loc[data[hab_label] == g, val_label].dropna().values
        if len(vals) >= 3:
            stat, pval = stats.shapiro(vals[:5000])
            results[str(g)] = {"stat": float(stat), "pval": float(pval), "n": len(vals), "vals": vals}
    return results


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

    if is_data:
        data_src = context["data"]
        numeric_cols = context["numeric_columns"]
        cat_cols = context["categorical_columns"]
        if not numeric_cols or not cat_cols:
            st.warning("Le fichier doit contenir au moins une colonne numérique et une colonne catégorielle.")
            return
        with left:
            csv_template_button(
                pd.DataFrame({"Habitat": ["Forêt", "Forêt", "Savane", "Savane"], "Succes_repro": [3.2, 2.9, 1.8, 2.1]}),
                "template_tests_stat.csv",
            )
            value_col = st.selectbox("Variable numérique à comparer", numeric_cols)
            group_col = st.selectbox("Variable de groupe (2 à 6 modalités)", cat_cols)
        sub = data_src[[group_col, value_col]].dropna()
        groups = sub[group_col].unique()
        if len(groups) < 2:
            st.warning(f"La colonne **{group_col}** ne contient qu'une seule modalité.")
            return
        if len(groups) > 6:
            st.warning(f"La colonne **{group_col}** contient {len(groups)} modalités. Sélectionnez une colonne avec 2 à 6 groupes.")
            return
        data = sub
        hab_label, val_label = group_col, value_col
    else:
        with left:
            n_a = st.slider("Nids en forêt restaurée", 8, 120, 36)
            n_b = st.slider("Nids en forêt dégradée", 8, 120, 34)
            mean_a = st.slider("Moyenne restaurée", 0.0, 6.0, 3.2, step=0.1)
            mean_b = st.slider("Moyenne dégradée", 0.0, 6.0, 2.4, step=0.1)
            sd = st.slider("Variabilité entre nids", 0.2, 3.0, 1.1, step=0.1)
            seed = st.number_input("Graine aléatoire", min_value=1, max_value=9999, value=33)
        data = generate_two_groups(int(seed), n_a, n_b, mean_a, mean_b, sd)
        hab_label, val_label = "Habitat", "Succès reproducteur"
        groups = data[hab_label].unique()

    n_groups = len(groups)

    # Box plot
    with right:
        fig = px.box(data, x=hab_label, y=val_label, points="all", color=hab_label)
        fig.update_layout(showlegend=False, xaxis_title=hab_label, yaxis_title=val_label)
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    # Summary metrics per group (in left below controls)
    with left:
        means_df = data.groupby(hab_label)[val_label].agg(["count", "mean", "std"]).round(3).reset_index()
        means_df.columns = [hab_label, "n", "Moyenne", "Écart-type"]
        st.dataframe(means_df, use_container_width=True)

    # ---------- Normalité (Shapiro-Wilk) ----------
    shapiro = _shapiro_table(data, hab_label, val_label, groups)
    all_normal = all(r["pval"] > 0.05 for r in shapiro.values()) if shapiro else True

    # ---------- Compute tests ----------
    if n_groups == 2:
        g0, g1 = groups[0], groups[1]
        group_a = data.loc[data[hab_label] == g0, val_label].dropna().values
        group_b = data.loc[data[hab_label] == g1, val_label].dropna().values
        welch = stats.ttest_ind(group_a, group_b, equal_var=False)
        mwu = stats.mannwhitneyu(group_a, group_b, alternative="two-sided")
        effect = float(np.mean(group_a) - np.mean(group_b))
        cohens_d = effect / float(np.sqrt((np.std(group_a, ddof=1) ** 2 + np.std(group_b, ddof=1) ** 2) / 2))
    else:
        valid_series = [
            data.loc[data[hab_label] == g, val_label].dropna().values
            for g in groups
            if len(data.loc[data[hab_label] == g, val_label].dropna()) >= 2
        ]
        if len(valid_series) < 2:
            st.warning("Il faut au moins 2 groupes avec 2 observations chacun pour effectuer l'ANOVA / Kruskal-Wallis.")
            return
        anova_f, anova_p = stats.f_oneway(*valid_series)
        kruskal_h, kruskal_p = stats.kruskal(*valid_series)
        # Eta-squared (effect size for ANOVA)
        ss_between = sum(
            len(s) * (np.mean(s) - np.mean(np.concatenate(valid_series))) ** 2
            for s in valid_series
        )
        ss_total = sum(np.sum((s - np.mean(np.concatenate(valid_series))) ** 2) for s in valid_series)
        eta2 = float(ss_between / ss_total) if ss_total > 0 else 0.0

    with st.expander("Cours : Logique des tests statistiques et choix du test"):
        st.markdown("#### Hypothèses H₀ et H₁")
        st.markdown(
            "- **H₀ (hypothèse nulle)** : il n'y a pas de différence entre les groupes (différence = 0 en population)\n"
            "- **H₁ (hypothèse alternative)** : il existe une différence réelle entre les groupes\n\n"
            "Le test calcule la probabilité d'observer un écart au moins aussi grand **si H₀ était vraie**. "
            "Cette probabilité s'appelle la **p-value**.\n\n"
            "| p-value | Décision | Interprétation |\n"
            "|---------|----------|----------------|\n"
            "| < 0,05 | Rejeter H₀ | La différence est significative — peu probable par hasard |\n"
            "| ≥ 0,05 | Ne pas rejeter H₀ | Aucune preuve suffisante d'une différence réelle |\n"
        )
        st.markdown("#### Risques d'erreur")
        st.markdown(
            "- **Risque α (erreur de type I)** : rejeter H₀ alors qu'elle est vraie (faux positif). Fixé à α = 0,05 en biologie.\n"
            "- **Risque β (erreur de type II)** : ne pas rejeter H₀ alors qu'H₁ est vraie (faux négatif). "
            "Dépend de la taille d'échantillon et de la taille d'effet.\n"
        )
        st.markdown("#### Arbre de décision — quel test choisir ?")
        st.markdown(
            "```\n"
            "Comparer des moyennes/médianes\n"
            "│\n"
            "├── 2 groupes\n"
            "│   ├── Données normales (Shapiro p > 0,05) → Test t de Welch\n"
            "│   └── Non-normales ou petits effectifs (n < 20) → Mann-Whitney U\n"
            "│\n"
            "└── 3 groupes ou plus\n"
            "    ├── Données normales → ANOVA à un facteur\n"
            "    │   └── Si p < 0,05 → Tests post-hoc (Tukey HSD)\n"
            "    └── Non-normales → Kruskal-Wallis\n"
            "        └── Si p < 0,05 → Tests de Dunn (Bonferroni)\n"
            "```\n"
        )
        st.markdown("#### Taille d'effet : au-delà de la p-value")
        st.markdown(
            "La p-value indique si un effet **existe**, pas s'il est biologiquement **important**.\n\n"
            "| Indicateur | Faible | Modéré | Fort |\n"
            "|-----------|--------|--------|------|\n"
            "| d de Cohen (2 groupes) | 0,2 | 0,5 | 0,8 |\n"
            "| η² (ANOVA) | 0,01 | 0,06 | 0,14 |\n"
        )

    # ---------- Tabs ----------
    tab_labels = ["Normalité", "Test paramétrique", "Test non-paramétrique", "Export"]
    tabs = st.tabs(tab_labels)

    # --- Tab 0 : Normalité ---
    with tabs[0]:
        st.markdown("#### Test de Shapiro-Wilk (H₀ : distribution normale)")
        st.caption(
            "Le test de Shapiro-Wilk vérifie si les données d'un groupe suivent une loi normale. "
            "Si p > 0,05 → on ne rejette pas H₀ : la distribution est compatible avec la normalité → test paramétrique possible. "
            "Si p ≤ 0,05 → les données s'écartent significativement de la normalité → utiliser le test non-paramétrique."
        )
        sw_rows = [
            {
                "Groupe": g,
                "n": r["n"],
                "W": round(r["stat"], 4),
                "p-value": round(r["pval"], 4),
                "Décision": "Normale ✓" if r["pval"] > 0.05 else "Non-normale ✗",
            }
            for g, r in shapiro.items()
        ]
        st.dataframe(pd.DataFrame(sw_rows), use_container_width=True)

        if all_normal:
            st.success("Toutes les distributions semblent normales (p > 0.05). Un test paramétrique est approprié.")
        else:
            st.warning("Au moins un groupe s'écarte de la normalité (p ≤ 0.05). Le test non-paramétrique est recommandé.")

        # Q-Q plots (max 4 per row)
        groups_with_data = [g for g in groups if str(g) in shapiro]
        n_cols = min(len(groups_with_data), 4)
        if n_cols > 0:
            st.markdown("**Graphiques Q-Q** (points alignés sur la droite = distribution normale)")
            cols = st.columns(n_cols)
            for i, g in enumerate(groups_with_data[:4]):
                r = shapiro[str(g)]
                (osm, osr), (slope, intercept, _) = stats.probplot(r["vals"])
                fig_qq = go.Figure()
                fig_qq.add_scatter(
                    x=osm, y=osr, mode="markers", name="Données",
                    marker={"size": 5, "color": "#4dabf7"},
                )
                x_line = np.array([min(osm), max(osm)])
                fig_qq.add_scatter(
                    x=x_line, y=slope * x_line + intercept,
                    mode="lines", name="Référence normale",
                    line={"dash": "dash", "color": "#39d98a", "width": 2},
                )
                fig_qq.update_layout(
                    title={"text": str(g), "font": {"size": 12}},
                    xaxis_title="Quantiles théoriques",
                    yaxis_title="Quantiles observés",
                    height=260,
                    showlegend=False,
                    margin={"l": 40, "r": 10, "t": 35, "b": 40},
                )
                style_figure(fig_qq)
                with cols[i]:
                    st.plotly_chart(fig_qq, use_container_width=True)

        teacher_note(
            "Shapiro-Wilk est le test de normalité le plus puissant pour les petits échantillons (n < 50). "
            "Pour n > 50, le test de Lilliefors (ou Kolmogorov-Smirnov corrigé) est souvent préféré. "
            "Un Q-Q plot donne une information visuelle complémentaire que la p-value seule ne fournit pas.",
            context,
        )

    # --- Tab 1 : Paramétrique ---
    with tabs[1]:
        if n_groups == 2:
            st.markdown(f"#### Test t de Welch — {str(g0)} vs {str(g1)}")
            st.caption("Comparaison de deux moyennes avec variances potentiellement inégales (robuste à l'hétéroscédasticité).")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Différence des moyennes", f"{effect:+.3g}")
            c2.metric("t de Welch", f"{welch.statistic:.3f}")
            c3.metric("p-value", f"{welch.pvalue:.3g}")
            c4.metric("d de Cohen", f"{cohens_d:.2f}")
            conc = "significative (p < 0.05)" if welch.pvalue < 0.05 else "non significative (p ≥ 0.05)"
            mag = "grande" if abs(cohens_d) > 0.8 else "modérée" if abs(cohens_d) > 0.5 else "faible"
            explain(
                f"La différence {str(g0)} − {str(g1)} = {effect:+.3g} est {conc}. "
                f"La taille d'effet (d = {cohens_d:.2f}) est {mag}."
            )
            if not all_normal:
                st.info("Les données ne semblent pas normalement distribuées — vérifiez aussi l'onglet Test non-paramétrique.")
        else:
            st.markdown(f"#### ANOVA à un facteur — {n_groups} groupes")
            st.caption("Comparaison simultanée de plusieurs moyennes (H₀ : toutes les moyennes sont égales).")
            c1, c2, c3 = st.columns(3)
            c1.metric("F", f"{anova_f:.3f}")
            c2.metric("p-value", f"{anova_p:.3g}")
            c3.metric("η² (taille d'effet)", f"{eta2:.3f}")
            if anova_p < 0.05:
                explain(
                    f"L'ANOVA détecte une différence significative entre les {n_groups} groupes "
                    f"(F = {anova_f:.3f}, p = {anova_p:.3g}, η² = {eta2:.3f}). "
                    "Une analyse post-hoc est nécessaire pour identifier quels groupes diffèrent."
                )
            else:
                explain(
                    f"L'ANOVA ne détecte pas de différence significative (F = {anova_f:.3f}, p = {anova_p:.3g})."
                )
            st.dataframe(means_df, use_container_width=True)
            if not all_normal:
                st.info("Les données ne semblent pas normalement distribuées — vérifiez aussi l'onglet Test non-paramétrique.")
        teacher_note(
            "Le test t de Welch ne suppose pas l'égalité des variances (contrairement au test t classique). "
            "L'ANOVA suppose normalité et homoscédasticité. Le d de Cohen : 0.2 = faible, 0.5 = modéré, 0.8 = fort. "
            "η² = SS_entre / SS_total mesure la proportion de variance expliquée par le facteur.",
            context,
        )

    # --- Tab 2 : Non-paramétrique ---
    with tabs[2]:
        if n_groups == 2:
            st.markdown(f"#### Test de Mann-Whitney U — {str(g0)} vs {str(g1)}")
            st.caption("Alternative non-paramétrique au test t. Compare les distributions, pas les moyennes. Robuste aux non-normalités et aux valeurs aberrantes.")
            c1, c2 = st.columns(2)
            c1.metric("U statistic", f"{mwu.statistic:.1f}")
            c2.metric("p-value", f"{mwu.pvalue:.3g}")
            conc_mw = "significative (p < 0.05)" if mwu.pvalue < 0.05 else "non significative (p ≥ 0.05)"
            explain(
                f"Le test de Mann-Whitney U donne une différence {conc_mw} (U = {mwu.statistic:.1f}, p = {mwu.pvalue:.3g}). "
                "Il teste si les valeurs d'un groupe tendent à être supérieures à celles de l'autre."
            )
            if welch.pvalue < 0.05 and mwu.pvalue >= 0.05:
                st.warning("Le test paramétrique est significatif mais pas le non-paramétrique. Inspectez les distributions et les valeurs aberrantes.")
            elif welch.pvalue >= 0.05 and mwu.pvalue < 0.05:
                st.warning("Le test non-paramétrique est significatif mais pas le paramétrique. Probable non-normalité ou valeurs aberrantes influentes.")
        else:
            st.markdown(f"#### Test de Kruskal-Wallis — {n_groups} groupes")
            st.caption("Alternative non-paramétrique à l'ANOVA. Basé sur les rangs, robuste aux non-normalités.")
            c1, c2 = st.columns(2)
            c1.metric("H statistic", f"{kruskal_h:.3f}")
            c2.metric("p-value", f"{kruskal_p:.3g}")
            if kruskal_p < 0.05:
                explain(
                    f"Le test de Kruskal-Wallis détecte une différence significative entre les {n_groups} groupes "
                    f"(H = {kruskal_h:.3f}, p = {kruskal_p:.3g}). "
                    "Des tests de Dunn (comparaisons pairées avec correction de Bonferroni) permettraient d'identifier les paires différentes."
                )
            else:
                explain(
                    f"Le test de Kruskal-Wallis ne détecte pas de différence significative "
                    f"(H = {kruskal_h:.3f}, p = {kruskal_p:.3g})."
                )
            if anova_p < 0.05 and kruskal_p >= 0.05:
                st.warning("L'ANOVA est significative mais pas Kruskal-Wallis. Inspectez les distributions : la normalité peut être critique ici.")
        teacher_note(
            "Mann-Whitney U est souvent appelé 'test de Wilcoxon à deux échantillons'. "
            "Kruskal-Wallis est l'extension non-paramétrique de l'ANOVA. "
            "Pour les comparaisons post-hoc après Kruskal-Wallis, le test de Dunn avec correction de Bonferroni est standard.",
            context,
        )

    # --- Tab 3 : Export ---
    with tabs[3]:
        st.download_button(
            "Exporter les données CSV",
            data.to_csv(index=False).encode("utf-8"),
            "orni_lab_tests.csv",
            "text/csv",
        )
        g0_str, g1_str = str(groups[0]), str(groups[1]) if n_groups >= 2 else ("", "")
        if n_groups == 2:
            pdf_lines = [
                f"Groupes : {g0_str} (n={len(group_a)}) vs {g1_str} (n={len(group_b)}).",
                f"Difference des moyennes = {effect:+.3g}.",
                f"Test de Welch : t = {welch.statistic:.3f}, p = {welch.pvalue:.3g}.",
                f"Test de Mann-Whitney U : U = {mwu.statistic:.1f}, p = {mwu.pvalue:.3g}.",
                f"d de Cohen = {cohens_d:.3f}.",
                "Shapiro-Wilk : " + " | ".join(
                    f"{g} W={r['stat']:.4f} p={r['pval']:.4f}"
                    for g, r in shapiro.items()
                ),
            ]
        else:
            pdf_lines = [
                f"ANOVA ({n_groups} groupes) : F = {anova_f:.3f}, p = {anova_p:.3g}, eta2 = {eta2:.3f}.",
                f"Kruskal-Wallis : H = {kruskal_h:.3f}, p = {kruskal_p:.3g}.",
                "Shapiro-Wilk : " + " | ".join(
                    f"{g} W={r['stat']:.4f} p={r['pval']:.4f}"
                    for g, r in shapiro.items()
                ),
            ]
        pdf = build_pdf_report("ORNI-LAB - Tests statistiques", pdf_lines)
        if pdf:
            st.download_button("Exporter le résumé PDF", pdf, "orni_lab_tests.pdf", "application/pdf")

    learning_notes(
        "Démarche en 4 étapes : (1) Poser H₀/H₁, (2) Vérifier la normalité (Shapiro-Wilk), (3) Choisir le test adapté, (4) Interpréter p-value ET taille d'effet.",
        "Une p-value significative ne prouve pas une importance biologique — un grand n peut rendre significative une différence négligeable. Toujours rapporter la taille d'effet (d de Cohen ou η²).",
        None if is_data else "Réduis la taille d'échantillon progressivement : à partir de quel n la conclusion change-t-elle ? Observe comment la p-value augmente quand n diminue.",
    )
