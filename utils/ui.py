from __future__ import annotations

import pandas as pd
import streamlit as st


PLOTLY_COLORS = ["#39d98a", "#4dabf7", "#ff6b6b", "#ffd166", "#b197fc", "#20c997"]


def _clean_data(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy().dropna(axis=1, how="all")
    data.columns = [str(c).strip() for c in data.columns]
    for col in data.columns:
        if data[col].dtype == "object":
            converted = pd.to_numeric(
                data[col].astype(str).str.replace(",", ".", regex=False), errors="coerce"
            )
            if converted.notna().sum() >= max(3, int(0.7 * data[col].notna().sum())):
                data[col] = converted
    return data


def _split_columns(frame: pd.DataFrame) -> tuple[list[str], list[str]]:
    numeric = frame.select_dtypes(include="number").columns.tolist()
    categorical = [c for c in frame.columns if c not in numeric and frame[c].nunique(dropna=True) <= 30]
    return numeric, categorical


def apply_global_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --orni-green: #39d98a;
            --orni-green-dark: #20b26b;
            --orni-coral: #ff6b6b;
            --orni-yellow: #ffd166;
            --orni-blue: #4dabf7;
            --orni-ink: #f8fafc;
            --orni-muted: #b9c4cf;
            --orni-bg: #05070b;
            --orni-panel: #10161f;
            --orni-panel-soft: #151d28;
            --orni-line: #263241;
        }
        /* Header Streamlit : on le garde à sa taille naturelle (le bouton
           de sidebar y est ancré), on le colorie juste comme notre fond */
        header[data-testid="stHeader"] {
            background: var(--orni-bg) !important;
            box-shadow: none !important;
            border-bottom: 1px solid var(--orni-line);
        }
        /* Cacher uniquement les éléments de branding/toolbar, PAS le toggle sidebar */
        div[data-testid="stDecoration"],
        div[data-testid="stStatusWidget"],
        #MainMenu {
            display: none !important;
        }
        div[data-testid="stToolbar"] {
            visibility: hidden !important;
        }
        /* Styler le bouton de toggle sidebar pour qu'il reste visible */
        header[data-testid="stHeader"] button,
        header[data-testid="stHeader"] a {
            visibility: visible !important;
            opacity: 1 !important;
            color: var(--orni-muted) !important;
        }
        header[data-testid="stHeader"] button:hover {
            color: var(--orni-green) !important;
            background: rgba(57,217,138,0.1) !important;
        }
        .stApp {
            background:
                radial-gradient(circle at 18% 0%, rgba(57, 217, 138, 0.12), transparent 28rem),
                radial-gradient(circle at 84% 8%, rgba(77, 171, 247, 0.12), transparent 26rem),
                var(--orni-bg);
            color: var(--orni-ink);
        }
        .main .block-container {
            max-width: 1280px;
            padding-top: 1rem;
            padding-bottom: 3rem;
        }
        h1, h2, h3 {
            letter-spacing: 0;
            color: var(--orni-ink);
            font-weight: 750;
        }
        p, span, label, div, li {
            color: var(--orni-ink);
        }
        [data-testid="stCaptionContainer"],
        .stCaption,
        small {
            color: var(--orni-muted) !important;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #080d13 0%, #101a23 48%, #123528 100%);
            border-right: 1px solid var(--orni-line);
        }
        [data-testid="stSidebar"] * {
            color: #f8fafc !important;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label {
            color: #dce7ef !important;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            background: rgba(255, 255, 255, 0.07);
            border: 1px solid rgba(255, 255, 255, 0.14);
            border-radius: 8px;
            padding: 0.2rem 0.35rem;
            margin-bottom: 0.3rem;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: rgba(57, 217, 138, 0.14);
            border-color: rgba(57, 217, 138, 0.45);
        }
        [data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.16);
        }
        .orni-hero {
            padding: 1.7rem 2rem;
            border-left: 7px solid var(--orni-green);
            background:
                linear-gradient(135deg, rgba(57, 217, 138, 0.16), rgba(77, 171, 247, 0.10)),
                var(--orni-panel);
            margin-bottom: 1.6rem;
            border-radius: 10px;
            border-top: 1px solid var(--orni-line);
            border-right: 1px solid var(--orni-line);
            border-bottom: 1px solid var(--orni-line);
            box-shadow: 0 18px 44px rgba(0, 0, 0, 0.34);
        }
        .orni-hero h1 {
            margin: 0 0 0.45rem 0;
            font-size: clamp(2.2rem, 4vw, 4rem);
            line-height: 1;
        }
        .orni-caption {
            color: var(--orni-muted);
            font-size: 1.05rem;
        }
        .metric-card {
            background: var(--orni-panel);
            border: 1px solid var(--orni-line);
            border-radius: 8px;
            padding: 0.85rem 1rem;
        }
        div[data-testid="stMetric"] {
            background: var(--orni-panel);
            border: 1px solid var(--orni-line);
            border-radius: 8px;
            padding: 0.85rem 1rem;
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.24);
        }
        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--orni-ink) !important;
        }
        div[data-testid="stPlotlyChart"],
        div[data-testid="stDataFrame"],
        div[data-testid="stExpander"] {
            background: var(--orni-panel);
            border: 1px solid var(--orni-line);
            border-radius: 10px;
            padding: 0.5rem;
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.28);
        }
        div[data-testid="stDataFrame"] {
            background: var(--orni-panel-soft);
        }
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        input,
        textarea {
            background: var(--orni-panel-soft) !important;
            border-color: var(--orni-line) !important;
            color: var(--orni-ink) !important;
        }
        .stSlider [data-baseweb="slider"] div {
            color: var(--orni-green);
        }
        .stDownloadButton button,
        .stButton button {
            background: var(--orni-green);
            color: #06100b;
            border: 1px solid var(--orni-green-dark);
            border-radius: 8px;
            font-weight: 700;
        }
        .stDownloadButton button:hover,
        .stButton button:hover {
            background: var(--orni-green-dark);
            border-color: var(--orni-green-dark);
            color: #ffffff;
        }
        .stAlert {
            background: rgba(77, 171, 247, 0.12);
            border: 1px solid rgba(77, 171, 247, 0.34);
            color: var(--orni-ink);
        }
        .orni-intro {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.9rem;
            margin: 1rem 0 1.4rem 0;
        }
        .orni-intro > div {
            background: linear-gradient(180deg, rgba(21, 29, 40, 0.98), rgba(16, 22, 31, 0.98));
            border: 1px solid var(--orni-line);
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 14px 30px rgba(0, 0, 0, 0.22);
        }
        .orni-intro strong {
            color: var(--orni-green);
            display: block;
            margin-bottom: 0.45rem;
        }
        .orni-intro p {
            color: var(--orni-muted);
            margin: 0;
            line-height: 1.45;
        }
        .orni-section-card {
            background: linear-gradient(135deg, rgba(21,29,40,0.98), rgba(16,22,31,0.98));
            border: 2px solid var(--orni-line);
            border-radius: 14px;
            padding: 2rem 1.8rem 1.4rem 1.8rem;
            text-align: center;
            min-height: 300px;
            transition: border-color 0.25s, box-shadow 0.25s;
            box-shadow: 0 18px 44px rgba(0,0,0,0.30);
            margin-bottom: 0.8rem;
        }
        .orni-section-card:hover {
            border-color: rgba(57,217,138,0.55);
            box-shadow: 0 22px 55px rgba(57,217,138,0.12);
        }
        .orni-section-card ul {
            list-style: none;
            padding: 0;
            margin: 0.6rem 0 0 0;
        }
        .orni-section-card ul li::before {
            content: "▸ ";
            color: var(--orni-green);
        }
        .orni-teacher-banner {
            background: linear-gradient(90deg, rgba(255,209,102,0.18), rgba(255,209,102,0.05));
            border-left: 5px solid #ffd166;
            border-radius: 0 8px 8px 0;
            padding: 0.55rem 1.1rem;
            margin-bottom: 1.4rem;
            font-weight: 700;
            color: #ffd166;
            font-size: 0.88rem;
            letter-spacing: 0.05em;
        }
        .orni-teacher-note {
            background: linear-gradient(135deg, rgba(255,209,102,0.09), rgba(255,209,102,0.03));
            border: 1px solid rgba(255,209,102,0.38);
            border-left: 4px solid #ffd166;
            border-radius: 8px;
            padding: 0.85rem 1.1rem 0.85rem 1rem;
            margin: 0.8rem 0;
        }
        .orni-teacher-note-header {
            color: #ffd166;
            font-weight: 700;
            font-size: 0.78rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }
        .orni-teacher-note-body {
            color: #e4ecf4;
            font-size: 0.91rem;
            line-height: 1.65;
            margin: 0;
        }
        .orni-teacher-pitfalls {
            background: rgba(255,107,107,0.07);
            border: 1px solid rgba(255,107,107,0.32);
            border-left: 4px solid #ff6b6b;
            border-radius: 8px;
            padding: 0.85rem 1.1rem 0.85rem 1rem;
            margin: 0.8rem 0;
        }
        .orni-teacher-pitfalls-header {
            color: #ff6b6b;
            font-weight: 700;
            font-size: 0.78rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }
        .orni-teacher-pitfalls ul {
            color: #e4ecf4;
            margin: 0;
            padding-left: 1.3rem;
        }
        .orni-teacher-pitfalls li {
            font-size: 0.89rem;
            line-height: 1.6;
            margin-bottom: 0.25rem;
        }
        .orni-teacher-formula {
            background: rgba(77,171,247,0.07);
            border: 1px solid rgba(77,171,247,0.30);
            border-left: 4px solid #4dabf7;
            border-radius: 8px;
            padding: 0.75rem 1.1rem;
            margin: 0.8rem 0;
        }
        .orni-teacher-formula-header {
            color: #4dabf7;
            font-weight: 700;
            font-size: 0.78rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }
        @media (max-width: 760px) {
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1rem;
            }
            .orni-hero {
                padding: 1.2rem 1.1rem;
            }
            .orni-intro {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="orni-hero">
            <h1>{title}</h1>
            <div class="orni-caption">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> dict:
    st.sidebar.title("Paramètres ORNI-LAB")
    _raw = st.sidebar.radio(
        "Mode d'affichage",
        ["👨‍🎓  Étudiant", "🎓  Enseignant"],
        index=0,
        horizontal=True,
        help="Mode Enseignant : active les notes pédagogiques, formules et erreurs fréquentes.",
    )
    mode = "Enseignant" if "Enseignant" in _raw else "Étudiant"
    if mode == "Enseignant":
        st.sidebar.markdown(
            '<div style="background:rgba(255,209,102,0.14);border:1px solid rgba(255,209,102,0.45);'
            'border-radius:6px;padding:0.3rem 0.7rem;font-size:0.8rem;color:#ffd166;'
            'text-align:center;margin:0.3rem 0 0.1rem 0;font-weight:700;letter-spacing:0.04em">'
            '🎓 MODE ENSEIGNANT ACTIF</div>',
            unsafe_allow_html=True,
        )
    st.sidebar.divider()

    st.sidebar.markdown("**Données de terrain**")
    uploaded = st.sidebar.file_uploader("Charger un CSV (optionnel)", type=["csv"], label_visibility="collapsed")

    data: pd.DataFrame | None = None
    numeric_columns: list[str] = []
    categorical_columns: list[str] = []
    data_filename: str = ""

    if uploaded is not None:
        sep_labels = {",": "Virgule", ";": "Point-virgule", "\t": "Tabulation"}
        sep_choice = st.sidebar.selectbox("Séparateur", list(sep_labels.values()), index=1)
        sep = {v: k for k, v in sep_labels.items()}[sep_choice]
        try:
            uploaded.seek(0)
            raw = pd.read_csv(uploaded, sep=sep)
            data = _clean_data(raw)
            numeric_columns, categorical_columns = _split_columns(data)
            data_filename = uploaded.name
            st.sidebar.success(f"{len(data):,} lignes · {len(data.columns)} colonnes")
        except Exception as exc:
            st.sidebar.error(f"Erreur lecture : {exc}")

    st.sidebar.divider()
    st.sidebar.caption(
        "Les paramètres modifient les sorties en temps réel. "
        "Les exports PDF reprennent les résultats et l'interprétation."
    )

    # ── Documentation ──────────────────────────────────────────────────────
    st.sidebar.divider()
    st.sidebar.markdown("#### 📖 Documentation")

    with st.sidebar.expander("À propos d'ORNI-LAB"):
        st.markdown(
            """
**ORNI-LAB** est un laboratoire interactif de modélisation ornithologique conçu pour l'enseignement universitaire en écologie et biologie des populations.

Il propose **18 modules** répartis en deux sections complémentaires, utilisables avec des données simulées ou des fichiers CSV terrain.

Conçu pour les TD, TP et le travail en autonomie — du L3 au M2.
            """
        )

    with st.sidebar.expander("Comment utiliser l'application"):
        st.markdown(
            """
**1. Choisir un mode**
- 👨‍🎓 **Étudiant** : résultats et interprétations automatiques
- 🎓 **Enseignant** : + formules LaTeX, notes pédagogiques et erreurs fréquentes

**2. Charger des données (optionnel)**
Déposez un fichier CSV terrain via *Données de terrain*. Sans fichier, chaque module génère une simulation pédagogique.

**3. Naviguer**
Choisissez une section depuis la **page d'accueil**, puis sélectionnez un module dans la sidebar.

**4. Explorer**
Ajustez les paramètres — les graphiques et résultats se mettent à jour en temps réel.

**5. Exporter**
Chaque module propose un export **CSV** des données et un rapport **PDF** avec résultats et interprétation.
            """
        )

    with st.sidebar.expander("📊 Biostatistique — 8 modules"):
        st.markdown(
            """
| Module | Utilité |
|:---|:---|
| Statistiques descriptives | Résumer et visualiser un jeu de données |
| Analyse CSV | Exploration guidée d'un fichier terrain |
| Corrélation et régression | Relation entre deux variables |
| Tests statistiques | Comparer groupes, t-test, ANOVA, Mann-Whitney |
| GLM comptage | Poisson / binomial négatif avec habitat et effort |
| Modèle mixte (LMM) | Effets aléatoires pour données groupées |
| Domaine vital — MCP | Polygone convexe minimum depuis GPS |
| Domaine vital — KDE | Estimation à noyau, isopleths 50 %–95 % |
            """
        )

    with st.sidebar.expander("🦅 Dynamique des populations — 10 modules"):
        st.markdown(
            """
| Module | Utilité |
|:---|:---|
| Richesse & diversité | Shannon, Simpson, courbes d'accumulation |
| Croissance exp./logistique | Densité-dépendance, capacité de charge |
| Matrices de Leslie | Projection par classes d'âge, λ, élasticité |
| CMR | Capture-Marquage-Recapture, Lincoln-Petersen |
| Modèles d'occupation | ψ et p séparés, MacKenzie et al. 2002 |
| Distance sampling | Densité par transect, demi-normale |
| Lotka-Volterra | Oscillations proie-prédateur |
| Séries temporelles | Mann-Kendall, tendance pluriannuelle |
| PVA et conservation | Risque d'extinction, stochasticité |
| Scénarios de gestion | Comparer des actions de conservation |
            """
        )

    with st.sidebar.expander("Format CSV attendu"):
        st.markdown(
            """
- Séparateur : **virgule** ou **point-virgule** (sélectionnable)
- En-têtes en première ligne
- Colonnes numériques : décimales avec `.` ou `,`
- Colonnes vides automatiquement ignorées
- Chaque module propose un **exemple CSV téléchargeable** via *Format de fichier attendu*
            """
        )

    return {
        "mode": mode,
        "is_teacher": mode == "Enseignant",
        "data": data,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "data_filename": data_filename,
    }


def render_teacher_banner(context: dict) -> None:
    if context.get("is_teacher"):
        st.markdown(
            '<div class="orni-teacher-banner">'
            '🎓 MODE ENSEIGNANT — Notes pédagogiques, formules et erreurs fréquentes activées'
            '</div>',
            unsafe_allow_html=True,
        )


def teacher_note(text: str, context: dict) -> None:
    if context.get("is_teacher"):
        st.markdown(
            f'<div class="orni-teacher-note">'
            f'<div class="orni-teacher-note-header">🎓 Note pédagogique</div>'
            f'<div class="orni-teacher-note-body">{text}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def teacher_formula(label: str, latex: str, context: dict) -> None:
    if context.get("is_teacher"):
        st.markdown(
            f'<div class="orni-teacher-formula">'
            f'<div class="orni-teacher-formula-header">📐 {label}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.latex(latex)


def teacher_pitfalls(items: list[str], context: dict) -> None:
    if context.get("is_teacher"):
        li = "".join(f"<li>{item}</li>" for item in items)
        st.markdown(
            f'<div class="orni-teacher-pitfalls">'
            f'<div class="orni-teacher-pitfalls-header">⚠️ Erreurs fréquentes</div>'
            f'<ul>{li}</ul>'
            f'</div>',
            unsafe_allow_html=True,
        )


def explain(text: str) -> None:
    st.markdown(f"**Interprétation automatique.** {text}")


def section(title: str, caption: str | None = None) -> None:
    st.subheader(title)
    if caption:
        st.caption(caption)


def csv_template_button(df: "pd.DataFrame", filename: str) -> None:
    with st.expander("Format de fichier attendu", expanded=False):
        st.caption("Exemple de structure CSV compatible avec ce module :")
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "Télécharger exemple CSV",
            df.to_csv(index=False).encode("utf-8"),
            filename,
            "text/csv",
            key=f"tpl_{filename}",
        )


def module_intro(what: str, why: str, ornithology: str) -> None:
    st.markdown(
        f"""
        <div class="orni-intro">
            <div>
                <strong>C'est quoi ?</strong>
                <p>{what}</p>
            </div>
            <div>
                <strong>Pourquoi l'utiliser ?</strong>
                <p>{why}</p>
            </div>
            <div>
                <strong>Intérêt ornithologique</strong>
                <p>{ornithology}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def learning_notes(takeaway: str, limits: str, exercise: str | None = None) -> None:
    if exercise is None:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**À retenir.** {takeaway}")
        with col2:
            st.markdown(f"**Limites.** {limits}")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**À retenir.** {takeaway}")
        with col2:
            st.markdown(f"**Limites.** {limits}")
        with col3:
            st.markdown(f"**Mini-exercice.** {exercise}")


def style_figure(fig):
    fig.update_layout(
        template="plotly_dark",
        colorway=PLOTLY_COLORS,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0b1118",
        font={"family": "Arial, sans-serif", "color": "#f8fafc"},
        margin={"l": 50, "r": 24, "t": 35, "b": 45},
        legend={"bgcolor": "rgba(16,22,31,0.82)", "bordercolor": "#263241", "borderwidth": 1},
    )
    fig.update_xaxes(showgrid=True, gridcolor="#253244", zerolinecolor="#3a4a5e")
    fig.update_yaxes(showgrid=True, gridcolor="#253244", zerolinecolor="#3a4a5e")
    return fig


def render_home_page(sections: dict, section_meta: dict) -> None:
    st.markdown(
        """
        <div style="text-align:center;margin-bottom:1.8rem;">
            <h2 style="font-size:1.7rem;font-weight:700;margin-bottom:0.4rem;">
                Choisissez votre domaine d'étude
            </h2>
            <p style="color:var(--orni-muted);font-size:1rem;margin:0;">
                Deux sections complémentaires pour explorer la biologie des populations d'oiseaux.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")
    section_names = list(sections.keys())

    for col, section_name in zip([col1, col2], section_names):
        meta = section_meta[section_name]
        modules = sections[section_name]
        n = len(modules)
        module_items = "".join(f"<li>{m}</li>" for m in list(modules.keys())[:5])
        if n > 5:
            module_items += f"<li style='color:var(--orni-muted);font-style:italic'>+ {n - 5} autres…</li>"

        with col:
            st.markdown(
                f"""
                <div class="orni-section-card">
                    <div style="font-size:3.5rem;line-height:1;margin-bottom:0.6rem">{meta['emoji']}</div>
                    <h2 style="font-size:1.4rem;margin:0 0 0.25rem 0;color:{meta['color']}">{section_name}</h2>
                    <div style="color:var(--orni-muted);font-size:0.82rem;margin-bottom:0.9rem;font-style:italic">{meta['subtitle']}</div>
                    <p style="color:var(--orni-muted);font-size:0.88rem;line-height:1.5;margin-bottom:0.9rem">{meta['description']}</p>
                    <ul style="color:#c9d4de;font-size:0.84rem;text-align:left;list-style:none;padding:0;margin:0">
                        {module_items}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                f"Entrer — {section_name} →",
                key=f"home_enter_{section_name}",
                use_container_width=True,
            ):
                st.session_state["section"] = section_name
                st.session_state["module"] = list(modules.keys())[0]

    st.divider()
    st.markdown("### Quel outil pour quelle question ?")
    st.caption("Guide rapide pour orienter votre choix de module selon la question de recherche.")

    _DECISION_TREE = [
        ("Explorer et résumer un jeu de données terrain", "Statistiques descriptives", "Biostatistique"),
        ("Charger un CSV et produire une analyse guidée", "Analyse CSV", "Biostatistique"),
        ("Comparer des groupes (masse, envergure, comptage…)", "Tests statistiques", "Biostatistique"),
        ("Quantifier une relation entre deux variables", "Corrélation et régression", "Biostatistique"),
        ("Modéliser des comptages avec habitat et effort", "GLM pour données de comptage", "Biostatistique"),
        ("Mesurer la diversité spécifique d'un site", "Richesse spécifique et diversité", "Dynamique des populations"),
        ("Comprendre la densité-dépendance et la croissance", "Croissance exponentielle/logistique", "Dynamique des populations"),
        ("Projeter une population par classes d'âge", "Matrices de Leslie", "Dynamique des populations"),
        ("Estimer l'abondance absolue par marquage-recapture", "Capture-Marquage-Recapture", "Dynamique des populations"),
        ("Corriger le biais de détectabilité sur des sites", "Modèles d'occupation", "Dynamique des populations"),
        ("Estimer la densité sur des transects linéaires", "Distance sampling", "Dynamique des populations"),
        ("Modéliser des interactions proie-prédateur", "Lotka-Volterra", "Dynamique des populations"),
        ("Détecter un déclin ou une reprise pluriannuelle", "Séries temporelles de population", "Dynamique des populations"),
        ("Évaluer le risque d'extinction d'une espèce", "PVA et conservation", "Dynamique des populations"),
        ("Comparer des stratégies de conservation", "Scénarios de gestion", "Dynamique des populations"),
    ]

    header = "| Je veux… | Module recommandé | Section |"
    sep = "|:---|:---|:---|"
    rows = "\n".join(f"| {q} | **{t}** | {s} |" for q, t, s in _DECISION_TREE)
    st.markdown(f"{header}\n{sep}\n{rows}")
