from __future__ import annotations

import pandas as pd
import streamlit as st
from app.auth import is_teacher, get_role


PLOTLY_COLORS = ["#39d98a", "#4dabf7", "#ff6b6b", "#ffd166", "#b197fc", "#20c997"]

# ─── Palettes par section ─────────────────────────────────────────────────────
_SECTION_BIRDS = {
    "Biostatistique":            ("📊", "#4dabf7", "#0d2a40"),
    "Dynamique des populations": ("🦅", "#39d98a", "#0a2818"),
}


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
    categorical = [c for c in frame.columns if c not in numeric
                   and frame[c].nunique(dropna=True) <= 30]
    return numeric, categorical


# ══════════════════════════════════════════════════════════════════════════════
# CSS GLOBAL — thème oiseaux
# ══════════════════════════════════════════════════════════════════════════════

def apply_global_style() -> None:
    st.markdown("""
    <style>
    /* ── Variables ── */
    :root {
        --orni-green:       #39d98a;
        --orni-green-dark:  #20b26b;
        --orni-coral:       #ff6b6b;
        --orni-yellow:      #ffd166;
        --orni-blue:        #4dabf7;
        --orni-orange:      #fd7e14;
        --orni-ink:         #f0f7f4;
        --orni-muted:       #8aa89a;
        --orni-bg:          #060d0a;
        --orni-panel:       #0c1710;
        --orni-panel-soft:  #111f16;
        --orni-line:        #1e3328;
    }

    /* ── Header Streamlit ── */
    header[data-testid="stHeader"] {
        background: var(--orni-bg) !important;
        box-shadow: none !important;
        border-bottom: 1px solid var(--orni-line);
    }
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"],
    #MainMenu { display: none !important; }
    div[data-testid="stToolbar"] { visibility: hidden !important; }
    header[data-testid="stHeader"] button,
    header[data-testid="stHeader"] a {
        visibility: visible !important;
        opacity: 1 !important;
        color: var(--orni-muted) !important;
    }
    header[data-testid="stHeader"] button:hover {
        color: var(--orni-green) !important;
        background: rgba(57,217,138,0.10) !important;
    }

    /* ── Fond principal avec oiseaux en vol (SVG encodé) ── */
    .stApp {
        background-color: var(--orni-bg);
        background-image:
            url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='600' height='400'%3E%3Cg fill='none' stroke='rgba(57,217,138,0.06)' stroke-width='1.8' stroke-linecap='round'%3E%3Cpath d='M60,80 C67,70 78,70 85,80'/%3E%3Cpath d='M85,80 C92,70 103,70 110,80'/%3E%3Cpath d='M200,150 C207,140 218,140 225,150'/%3E%3Cpath d='M225,150 C232,140 243,140 250,150'/%3E%3Cpath d='M400,60 C407,50 418,50 425,60'/%3E%3Cpath d='M425,60 C432,50 443,50 450,60'/%3E%3Cpath d='M500,200 C507,190 518,190 525,200'/%3E%3Cpath d='M525,200 C532,190 543,190 550,200'/%3E%3Cpath d='M150,300 C157,290 168,290 175,300'/%3E%3Cpath d='M175,300 C182,290 193,290 200,300'/%3E%3Cpath d='M350,340 C357,330 368,330 375,340'/%3E%3Cpath d='M375,340 C382,330 393,330 400,340'/%3E%3C/g%3E%3C/svg%3E"),
            radial-gradient(ellipse at 10% 0%,  rgba(57,217,138,0.13), transparent 35rem),
            radial-gradient(ellipse at 90% 5%,  rgba(77,171,247,0.10), transparent 30rem),
            radial-gradient(ellipse at 50% 90%, rgba(32,178,107,0.07), transparent 25rem);
        color: var(--orni-ink);
    }

    .main .block-container {
        max-width: 1300px;
        padding-top: 0.8rem;
        padding-bottom: 3rem;
    }

    /* ── Typographie ── */
    h1, h2, h3 { letter-spacing: 0; color: var(--orni-ink); font-weight: 750; }
    p, span, label, div, li { color: var(--orni-ink); }
    [data-testid="stCaptionContainer"], .stCaption, small { color: var(--orni-muted) !important; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, #040d07 0%, #091408 40%, #0b1f12 75%, #061209 100%),
            url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='300'%3E%3Cg fill='none' stroke='rgba(57,217,138,0.08)' stroke-width='1.4' stroke-linecap='round'%3E%3Cpath d='M30,50 C35,42 44,42 49,50'/%3E%3Cpath d='M49,50 C54,42 63,42 68,50'/%3E%3Cpath d='M100,120 C105,112 114,112 119,120'/%3E%3Cpath d='M119,120 C124,112 133,112 138,120'/%3E%3Cpath d='M20,200 C25,192 34,192 39,200'/%3E%3Cpath d='M39,200 C44,192 53,192 58,200'/%3E%3C/g%3E%3C/svg%3E");
        border-right: 1px solid var(--orni-line);
    }
    [data-testid="stSidebar"] * { color: #e8f4ee !important; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label { color: #c8ddd0 !important; }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        background: rgba(57,217,138,0.08);
        border: 1px solid rgba(57,217,138,0.18);
        border-radius: 8px;
        padding: 0.2rem 0.5rem;
        margin-bottom: 0.3rem;
        transition: all 0.2s;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(57,217,138,0.20);
        border-color: rgba(57,217,138,0.55);
    }
    [data-testid="stSidebar"] hr { border-color: rgba(57,217,138,0.18); }

    /* ── Hero header ── */
    .orni-hero {
        position: relative;
        overflow: hidden;
        padding: 1.8rem 2.2rem 1.5rem 2.2rem;
        border-left: 6px solid var(--orni-green);
        background:
            linear-gradient(120deg,
                rgba(57,217,138,0.18) 0%,
                rgba(32,178,107,0.10) 40%,
                rgba(77,171,247,0.10) 100%),
            var(--orni-panel);
        border-radius: 14px;
        border-top: 1px solid rgba(57,217,138,0.22);
        border-right: 1px solid var(--orni-line);
        border-bottom: 1px solid var(--orni-line);
        box-shadow: 0 20px 60px rgba(0,0,0,0.45), inset 0 1px 0 rgba(57,217,138,0.12);
        margin-bottom: 1.4rem;
    }
    .orni-hero h1 {
        margin: 0 0 0.3rem 0;
        font-size: clamp(2.2rem, 4vw, 3.8rem);
        line-height: 1;
        background: linear-gradient(90deg, #39d98a, #4dabf7, #ffd166);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .orni-caption { color: var(--orni-muted); font-size: 1.05rem; }
    .orni-hero-birds {
        position: absolute;
        right: 2rem;
        top: 50%;
        transform: translateY(-50%);
        font-size: 2.8rem;
        opacity: 0.45;
        letter-spacing: 0.4rem;
        filter: drop-shadow(0 0 12px rgba(57,217,138,0.4));
    }
    .orni-hero-tag {
        display: inline-block;
        background: rgba(57,217,138,0.14);
        border: 1px solid rgba(57,217,138,0.30);
        border-radius: 20px;
        padding: 0.2rem 0.75rem;
        font-size: 0.78rem;
        color: var(--orni-green) !important;
        font-weight: 700;
        letter-spacing: 0.05em;
        margin-right: 0.4rem;
        margin-top: 0.6rem;
    }

    /* ── Métriques ── */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, var(--orni-panel), var(--orni-panel-soft));
        border: 1px solid var(--orni-line);
        border-radius: 10px;
        padding: 0.9rem 1rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.28);
        transition: transform 0.15s, box-shadow 0.15s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 36px rgba(57,217,138,0.12);
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: var(--orni-ink) !important; }

    /* ── Graphiques / DataFrames ── */
    div[data-testid="stPlotlyChart"],
    div[data-testid="stDataFrame"],
    div[data-testid="stExpander"] {
        background: var(--orni-panel);
        border: 1px solid var(--orni-line);
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 14px 38px rgba(0,0,0,0.32);
    }
    div[data-testid="stDataFrame"] { background: var(--orni-panel-soft); }

    /* ── Inputs ── */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    input, textarea {
        background: var(--orni-panel-soft) !important;
        border-color: var(--orni-line) !important;
        color: var(--orni-ink) !important;
    }
    .stSlider [data-baseweb="slider"] div { color: var(--orni-green); }

    /* ── Boutons ── */
    .stDownloadButton button,
    .stButton button {
        background: linear-gradient(135deg, var(--orni-green), var(--orni-green-dark));
        color: #04110a;
        border: none;
        border-radius: 9px;
        font-weight: 700;
        letter-spacing: 0.02em;
        box-shadow: 0 4px 16px rgba(57,217,138,0.28);
        transition: all 0.2s;
    }
    .stDownloadButton button:hover,
    .stButton button:hover {
        background: linear-gradient(135deg, #4ef7a8, var(--orni-green));
        box-shadow: 0 6px 24px rgba(57,217,138,0.42);
        transform: translateY(-1px);
    }

    /* ── Alertes ── */
    .stAlert {
        background: rgba(77,171,247,0.10);
        border: 1px solid rgba(77,171,247,0.28);
        border-radius: 8px;
    }

    /* ── Module intro cards ── */
    .orni-intro {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.85rem;
        margin: 0.8rem 0 1.2rem 0;
    }
    .orni-intro > div {
        background: linear-gradient(160deg, rgba(18,30,20,0.98), rgba(12,23,16,0.98));
        border: 1px solid var(--orni-line);
        border-radius: 12px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 28px rgba(0,0,0,0.28);
        transition: border-color 0.2s;
    }
    .orni-intro > div:hover { border-color: rgba(57,217,138,0.35); }
    .orni-intro strong { color: var(--orni-green); display: block; margin-bottom: 0.4rem; font-size:0.92rem; }
    .orni-intro p { color: var(--orni-muted); margin: 0; line-height: 1.5; font-size:0.88rem; }

    /* ── Section cards (page d'accueil) ── */
    .orni-section-card {
        position: relative;
        overflow: hidden;
        border-radius: 18px;
        padding: 2.2rem 1.8rem 1.6rem 1.8rem;
        text-align: center;
        min-height: 320px;
        transition: transform 0.25s, box-shadow 0.25s;
        margin-bottom: 0.8rem;
    }
    .orni-section-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 28px 70px rgba(0,0,0,0.45) !important;
    }
    .orni-section-card-bio {
        background:
            radial-gradient(ellipse at 80% 20%, rgba(77,171,247,0.22), transparent 60%),
            linear-gradient(145deg, #0a1e33, #0d2540);
        border: 2px solid rgba(77,171,247,0.30);
        box-shadow: 0 18px 48px rgba(77,171,247,0.12);
    }
    .orni-section-card-dyn {
        background:
            radial-gradient(ellipse at 20% 80%, rgba(57,217,138,0.22), transparent 60%),
            linear-gradient(145deg, #091a0e, #0d2416);
        border: 2px solid rgba(57,217,138,0.30);
        box-shadow: 0 18px 48px rgba(57,217,138,0.12);
    }
    .orni-section-card ul {
        list-style: none; padding: 0; margin: 0.7rem 0 0 0; text-align:left;
    }
    .orni-section-card ul li {
        padding: 0.18rem 0;
        font-size: 0.85rem;
        color: #a8c4b8;
    }
    .orni-section-card ul li::before { content: "🐦 "; }

    /* ── Welcome band ── */
    .orni-welcome {
        background: linear-gradient(90deg,
            rgba(57,217,138,0.12), rgba(77,171,247,0.10), rgba(253,126,20,0.07));
        border: 1px solid rgba(57,217,138,0.18);
        border-radius: 12px;
        padding: 1.2rem 2rem;
        text-align: center;
        margin-bottom: 1.8rem;
    }

    /* ── Teacher mode ── */
    .orni-teacher-banner {
        background: linear-gradient(90deg, rgba(255,209,102,0.20), rgba(255,209,102,0.04));
        border-left: 5px solid #ffd166;
        border-radius: 0 10px 10px 0;
        padding: 0.6rem 1.2rem;
        margin-bottom: 1.2rem;
        font-weight: 700;
        color: #ffd166;
        font-size: 0.88rem;
        letter-spacing: 0.05em;
        box-shadow: inset 0 0 30px rgba(255,209,102,0.05);
    }
    .orni-teacher-note {
        background: linear-gradient(135deg, rgba(255,209,102,0.10), rgba(255,209,102,0.03));
        border: 1px solid rgba(255,209,102,0.38);
        border-left: 4px solid #ffd166;
        border-radius: 8px;
        padding: 0.85rem 1.1rem;
        margin: 0.8rem 0;
    }
    .orni-teacher-note-header {
        color: #ffd166; font-weight: 700; font-size: 0.78rem;
        letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.45rem;
    }
    .orni-teacher-note-body { color: #e4ecf4; font-size: 0.91rem; line-height: 1.65; margin: 0; }
    .orni-teacher-pitfalls {
        background: rgba(255,107,107,0.07);
        border: 1px solid rgba(255,107,107,0.32);
        border-left: 4px solid #ff6b6b;
        border-radius: 8px;
        padding: 0.85rem 1.1rem;
        margin: 0.8rem 0;
    }
    .orni-teacher-pitfalls-header {
        color: #ff6b6b; font-weight: 700; font-size: 0.78rem;
        letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.45rem;
    }
    .orni-teacher-pitfalls ul { color: #e4ecf4; margin: 0; padding-left: 1.3rem; }
    .orni-teacher-pitfalls li { font-size: 0.89rem; line-height: 1.6; margin-bottom: 0.25rem; }
    .orni-teacher-formula {
        background: rgba(77,171,247,0.07);
        border: 1px solid rgba(77,171,247,0.30);
        border-left: 4px solid #4dabf7;
        border-radius: 8px;
        padding: 0.75rem 1.1rem;
        margin: 0.8rem 0;
    }
    .orni-teacher-formula-header {
        color: #4dabf7; font-weight: 700; font-size: 0.78rem;
        letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.4rem;
    }

    /* ── Profil auteur ── */
    .orni-author-card {
        background: linear-gradient(145deg, rgba(57,217,138,0.13), rgba(77,171,247,0.08));
        border: 1px solid rgba(57,217,138,0.30);
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        margin-top: 0.4rem;
    }
    .orni-author-avatar {
        width: 52px; height: 52px;
        border-radius: 50%;
        background: linear-gradient(135deg, #39d98a, #4dabf7);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem;
        margin: 0 auto 0.65rem auto;
        box-shadow: 0 4px 16px rgba(57,217,138,0.35);
    }
    .orni-author-name {
        font-weight: 800;
        font-size: 0.96rem;
        color: #f0f7f4 !important;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .orni-author-title {
        font-size: 0.76rem;
        color: var(--orni-green) !important;
        text-align: center;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .orni-author-spec {
        font-size: 0.74rem;
        color: #8aa89a !important;
        text-align: center;
        line-height: 1.45;
        margin-bottom: 0.7rem;
        font-style: italic;
    }
    .orni-author-contact {
        font-size: 0.78rem;
        color: #a8c4b8 !important;
        text-align: center;
        line-height: 1.7;
    }
    .orni-author-contact a { color: var(--orni-green) !important; text-decoration: none; }
    .orni-tag-pill {
        display: inline-block;
        background: rgba(57,217,138,0.12);
        border: 1px solid rgba(57,217,138,0.22);
        border-radius: 12px;
        padding: 0.1rem 0.5rem;
        font-size: 0.68rem;
        color: var(--orni-green) !important;
        margin: 0.15rem;
        font-weight: 600;
    }

    /* ── Responsive ── */
    @media (max-width: 760px) {
        .main .block-container { padding: 1rem; }
        .orni-hero { padding: 1.2rem; }
        .orni-intro { grid-template-columns: 1fr; }
        .orni-hero-birds { display: none; }
    }
    </style>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

def render_header(title: str, subtitle: str) -> None:
    st.markdown(f"""
    <div class="orni-hero">
        <div class="orni-hero-birds">🦅 🐦 🦉</div>
        <h1>🪶 {title}</h1>
        <div class="orni-caption">{subtitle}</div>
        <div style="margin-top:0.7rem">
            <span class="orni-hero-tag">🌿 Écologie quantitative</span>
            <span class="orni-hero-tag">📐 Biostatistique</span>
            <span class="orni-hero-tag">🦆 Dynamique des populations</span>
            <span class="orni-hero-tag">🐧 Conservation</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar() -> dict:
    # Logo sidebar
    st.sidebar.markdown("""
    <div style="text-align:center;padding:0.6rem 0 0.2rem 0;">
        <div style="font-size:2.4rem;filter:drop-shadow(0 0 10px rgba(57,217,138,0.5))">🪶</div>
        <div style="font-size:1.05rem;font-weight:800;color:#39d98a;letter-spacing:0.08em">ORNI-LAB</div>
        <div style="font-size:0.7rem;color:#5a8a6a;letter-spacing:0.04em">Modélisation Ornithologique</div>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.divider()

    # Mode — verrouillé en Étudiant si rôle = student
    role = get_role()
    if role == "student":
        mode = "Étudiant"
        st.sidebar.markdown(
            '<div style="background:rgba(77,171,247,0.12);border:1px solid rgba(77,171,247,0.35);'
            'border-radius:7px;padding:0.3rem 0.7rem;font-size:0.79rem;color:#4dabf7;'
            'text-align:center;margin:0.3rem 0 0.1rem 0;font-weight:700;letter-spacing:0.04em">'
            '👨‍🎓 MODE ÉTUDIANT</div>',
            unsafe_allow_html=True,
        )
    else:
        _raw = st.sidebar.radio(
            "Mode d'affichage",
            ["👨‍🎓  Étudiant", "🎓  Enseignant"],
            index=1 if role == "teacher" else 0,
            horizontal=True,
            help="Mode Enseignant : formules LaTeX, notes pédagogiques et erreurs fréquentes.",
        )
        mode = "Enseignant" if "Enseignant" in _raw else "Étudiant"
        if mode == "Enseignant":
            st.sidebar.markdown(
                '<div style="background:rgba(255,209,102,0.14);border:1px solid rgba(255,209,102,0.40);'
                'border-radius:7px;padding:0.3rem 0.7rem;font-size:0.79rem;color:#ffd166;'
                'text-align:center;margin:0.3rem 0 0.1rem 0;font-weight:700;letter-spacing:0.04em">'
                '🎓 MODE ENSEIGNANT ACTIF</div>',
                unsafe_allow_html=True,
            )
    st.sidebar.divider()

    # Chargement CSV
    st.sidebar.markdown("**🗂️ Données de terrain**")
    uploaded = st.sidebar.file_uploader(
        "Charger un CSV (optionnel)", type=["csv"], label_visibility="collapsed"
    )
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
            # Effacer un éventuel partage depuis Analyse CSV
            st.session_state.pop("_orni_shared_df",    None)
            st.session_state.pop("_orni_shared_fname", None)
            st.sidebar.success(f"✅ {len(data):,} lignes · {len(data.columns)} colonnes")
        except Exception as exc:
            st.sidebar.error(f"Erreur : {exc}")

    elif st.session_state.get("_orni_shared_df") is not None:
        # Fallback : fichier partagé par le module Analyse CSV
        data          = st.session_state["_orni_shared_df"]
        data_filename = st.session_state.get("_orni_shared_fname", "Analyse CSV")
        numeric_columns, categorical_columns = _split_columns(data)
        st.sidebar.info(
            f"📂 **{data_filename}** ({len(data):,} lignes)\n\n"
            "_Partagé depuis Analyse CSV_"
        )
        if st.sidebar.button("✕ Effacer ces données", use_container_width=True):
            st.session_state.pop("_orni_shared_df",    None)
            st.session_state.pop("_orni_shared_fname", None)
            st.rerun()

    st.sidebar.divider()
    st.sidebar.caption(
        "Les paramètres modifient les sorties en temps réel. "
        "Exports PDF et CSV disponibles dans chaque module."
    )

    # ── Documentation ──────────────────────────────────────────────────────
    st.sidebar.divider()
    st.sidebar.markdown("#### 📖 Documentation")

    with st.sidebar.expander("À propos d'ORNI-LAB"):
        st.markdown("""
**ORNI-LAB** est un laboratoire interactif de modélisation ornithologique conçu pour l'enseignement universitaire en écologie et biologie des populations.

Il propose **18 modules** répartis en deux sections :
- 📊 **Biostatistique** (8 modules)
- 🦅 **Dynamique des populations** (10 modules)

Utilisable avec des **données simulées** ou des **fichiers CSV terrain** — du L3 au doctorat.
        """)

    with st.sidebar.expander("📋 Comment utiliser"):
        st.markdown("""
**1.** Choisir un mode : 👨‍🎓 Étudiant ou 🎓 Enseignant
**2.** Charger un CSV terrain (optionnel)
**3.** Naviguer depuis la page d'accueil vers une section
**4.** Ajuster les paramètres — résultats en temps réel
**5.** Exporter PDF ou CSV depuis chaque module
        """)

    with st.sidebar.expander("📊 Biostatistique — 8 modules"):
        st.markdown("""
| Module | Utilité |
|:---|:---|
| Analyse CSV | Exploration guidée d'un fichier |
| Stats descriptives | Résumer et visualiser |
| Corrélation & régression | Relation entre 2 variables |
| Tests statistiques | t-test, ANOVA, Mann-Whitney |
| GLM comptage | Poisson / binomial négatif |
| Modèle mixte (LMM) | Effets aléatoires |
| Domaine vital — MCP | Polygone convexe GPS |
| Domaine vital — KDE | Estimation à noyau |
        """)

    with st.sidebar.expander("🦅 Dynamique — 10 modules"):
        st.markdown("""
| Module | Utilité |
|:---|:---|
| Richesse & diversité | Shannon, Simpson |
| Croissance | Exponentielle / logistique |
| Matrices de Leslie | Projection structurée |
| CMR | Lincoln-Petersen |
| Occupation | MacKenzie ψ et p |
| Distance sampling | Densité transect |
| Lotka-Volterra | Proie-prédateur |
| Séries temporelles | Mann-Kendall |
| PVA | Risque d'extinction |
| Scénarios | Comparer actions |
        """)

    with st.sidebar.expander("📁 Format CSV"):
        st.markdown("""
- Séparateur : **virgule** ou **point-virgule**
- En-têtes en 1ère ligne
- Décimales : `.` ou `,` (converti automatiquement)
- Colonnes vides ignorées automatiquement
- Chaque module propose un **exemple CSV**
        """)

    # ── À propos de l'auteur ───────────────────────────────────────────────
    st.sidebar.divider()
    st.sidebar.markdown("#### 👤 À propos")
    st.sidebar.markdown("""
<div class="orni-author-card">
    <div class="orni-author-avatar">🧑‍🔬</div>
    <div class="orni-author-name">Abdoulaye Diop</div>
    <div class="orni-author-title">Bioinformaticien · Biomathématicien</div>
    <div class="orni-author-spec">
        Analyse &amp; modélisation des systèmes biologiques<br>
        Écologie quantitative · Biologie computationnelle
    </div>
    <div style="text-align:center;margin-bottom:0.55rem">
        <span class="orni-tag-pill">🧬 Bioinformatique</span>
        <span class="orni-tag-pill">📐 Biomathématiques</span>
        <span class="orni-tag-pill">🌿 Écologie</span>
        <span class="orni-tag-pill">💻 Calcul scientifique</span>
    </div>
    <div class="orni-author-contact">
        📧 <a href="mailto:dioplayes@gmail.com">dioplayes@gmail.com</a><br>
        📱 +221 77 113 07 48
    </div>
</div>
""", unsafe_allow_html=True)

    return {
        "mode": mode,
        "is_teacher": mode == "Enseignant",
        "data": data,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "data_filename": data_filename,
    }


# ══════════════════════════════════════════════════════════════════════════════
# TEACHER MODE
# ══════════════════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════════════════
# PAGE D'ACCUEIL
# ══════════════════════════════════════════════════════════════════════════════

def render_home_page(sections: dict, section_meta: dict) -> None:
    # Bandeau de bienvenue
    st.markdown("""
    <div class="orni-welcome">
        <div style="font-size:2.5rem;margin-bottom:0.4rem">
            🦢 &nbsp; 🦅 &nbsp; 🦉 &nbsp; 🐦 &nbsp; 🦆 &nbsp; 🐧 &nbsp; 🦜 &nbsp; 🦩
        </div>
        <h2 style="font-size:1.55rem;font-weight:700;margin:0 0 0.3rem 0;
                   background:linear-gradient(90deg,#39d98a,#4dabf7);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                   background-clip:text;">
            Bienvenue dans ORNI-LAB
        </h2>
        <p style="color:#8aa89a;font-size:0.95rem;margin:0;">
            Choisissez votre domaine d'étude pour commencer l'exploration.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    section_names = list(sections.keys())
    card_classes  = ["orni-section-card-bio", "orni-section-card-dyn"]
    section_icons = ["🔬 📊 📈 🧮", "🦅 🌱 🌊 🌍"]
    section_emojis = [
        ("📊", "#4dabf7"),
        ("🦅", "#39d98a"),
    ]

    for idx, (col, section_name) in enumerate(zip([col1, col2], section_names)):
        meta    = section_meta[section_name]
        modules = sections[section_name]
        n       = len(modules)
        items   = "".join(f"<li>{m}</li>" for m in list(modules.keys())[:6])
        if n > 6:
            items += f"<li style='color:#5a7a6a;font-style:italic'>+ {n-6} autres…</li>"
        emoji, color = section_emojis[idx]

        with col:
            st.markdown(f"""
            <div class="orni-section-card {card_classes[idx]}">
                <div style="font-size:4rem;line-height:1;margin-bottom:0.5rem;
                            filter:drop-shadow(0 0 16px {color}60)">{emoji}</div>
                <div style="font-size:0.72rem;color:{color};font-weight:700;
                            letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.3rem">
                    {section_icons[idx]}
                </div>
                <h2 style="font-size:1.35rem;margin:0 0 0.2rem 0;color:{color};font-weight:800">
                    {section_name}
                </h2>
                <div style="color:#5a7a6a;font-size:0.79rem;font-style:italic;margin-bottom:0.7rem">
                    {meta['subtitle']}
                </div>
                <p style="color:#7a9a8a;font-size:0.85rem;line-height:1.5;margin-bottom:0.9rem">
                    {meta['description']}
                </p>
                <ul>{items}</ul>
            </div>
            """, unsafe_allow_html=True)
            if st.button(
                f"{emoji} Accéder — {section_name}",
                key=f"home_enter_{section_name}",
                use_container_width=True,
            ):
                st.session_state["section"] = section_name
                st.session_state["module"] = list(modules.keys())[0]

    # Guide de décision
    st.divider()
    st.markdown("""
    <div style="text-align:center;margin-bottom:1rem;">
        <span style="font-size:1.5rem">🧭</span>
        <h3 style="display:inline;margin-left:0.5rem;font-size:1.2rem">
            Quel outil pour quelle question ?
        </h3>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Guide rapide pour choisir le bon module selon votre question de recherche.")

    _TREE = [
        ("Explorer et résumer un jeu de données terrain",        "Analyse CSV",                          "📊"),
        ("Décrire la distribution d'une variable morphologique", "Statistiques descriptives",            "📊"),
        ("Comparer groupes (masse, envergure, comptage…)",       "Tests statistiques",                   "📊"),
        ("Quantifier une relation entre deux variables",         "Corrélation et régression",            "📊"),
        ("Modéliser des comptages avec habitat et effort",       "GLM pour données de comptage",         "📊"),
        ("Données groupées par site ou individu (LMM)",         "Modèle mixte (LMM)",                   "📊"),
        ("Cartographier le domaine vital (GPS, polygone)",       "Domaine vital — MCP",                  "📊"),
        ("Domaine vital probabiliste avec isopleths",            "Domaine vital — KDE",                  "📊"),
        ("Mesurer la diversité d'une communauté",                "Richesse spécifique et diversité",     "🦅"),
        ("Modéliser croissance et capacité de charge",           "Croissance exponentielle/logistique",  "🦅"),
        ("Projeter une population structurée en âge",            "Matrices de Leslie",                   "🦅"),
        ("Estimer l'abondance par marquage-recapture",           "Capture-Marquage-Recapture",           "🦅"),
        ("Corriger le biais de détectabilité",                   "Modèles d'occupation",                 "🦅"),
        ("Estimer la densité sur des transects",                 "Distance sampling",                    "🦅"),
        ("Modéliser des interactions proie-prédateur",           "Lotka-Volterra",                       "🦅"),
        ("Détecter un déclin ou reprise pluriannuelle",          "Séries temporelles de population",     "🦅"),
        ("Évaluer le risque d'extinction",                       "PVA et conservation",                  "🦅"),
        ("Comparer des stratégies de conservation",              "Scénarios de gestion",                 "🦅"),
    ]

    header = "| Question | Module recommandé | Section |"
    sep    = "|:---|:---|:---:|"
    rows   = "\n".join(f"| {q} | **{m}** | {e} |" for q, m, e in _TREE)
    st.markdown(f"{header}\n{sep}\n{rows}")


# ══════════════════════════════════════════════════════════════════════════════
# COMPOSANTS DE MODULE
# ══════════════════════════════════════════════════════════════════════════════

def explain(text: str) -> None:
    st.markdown(
        f'<div style="background:rgba(57,217,138,0.07);border-left:3px solid #39d98a;'
        f'border-radius:0 8px 8px 0;padding:0.6rem 1rem;margin:0.6rem 0;'
        f'font-size:0.89rem;color:#c8e8d8;line-height:1.55">'
        f'<strong style="color:#39d98a">💡 Interprétation.</strong> {text}</div>',
        unsafe_allow_html=True,
    )


def section(title: str, caption: str | None = None) -> None:
    st.subheader(title)
    if caption:
        st.caption(caption)


def csv_template_button(df: "pd.DataFrame", filename: str) -> None:
    with st.expander("📎 Format de fichier attendu", expanded=False):
        st.caption("Exemple de structure CSV compatible avec ce module :")
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "⬇ Télécharger exemple CSV",
            df.to_csv(index=False).encode("utf-8"),
            filename, "text/csv",
            key=f"tpl_{filename}",
        )


def module_intro(what: str, why: str, ornithology: str) -> None:
    st.markdown(f"""
    <div class="orni-intro">
        <div>
            <strong>🔍 C'est quoi ?</strong>
            <p>{what}</p>
        </div>
        <div>
            <strong>⚡ Pourquoi l'utiliser ?</strong>
            <p>{why}</p>
        </div>
        <div>
            <strong>🐦 Intérêt ornithologique</strong>
            <p>{ornithology}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def learning_notes(takeaway: str, limits: str, exercise: str | None = None) -> None:
    if exercise is None:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**📌 À retenir.** {takeaway}")
        with col2:
            st.markdown(f"**⚠️ Limites.** {limits}")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**📌 À retenir.** {takeaway}")
        with col2:
            st.markdown(f"**⚠️ Limites.** {limits}")
        with col3:
            st.markdown(f"**🧪 Mini-exercice.** {exercise}")


def style_figure(fig):
    fig.update_layout(
        template="plotly_dark",
        colorway=PLOTLY_COLORS,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#070f09",
        font={"family": "Arial, sans-serif", "color": "#f0f7f4"},
        margin={"l": 50, "r": 24, "t": 35, "b": 45},
        legend={"bgcolor": "rgba(10,20,14,0.85)", "bordercolor": "#1e3328", "borderwidth": 1},
    )
    fig.update_xaxes(showgrid=True, gridcolor="#1a2e20", zerolinecolor="#2a4030")
    fig.update_yaxes(showgrid=True, gridcolor="#1a2e20", zerolinecolor="#2a4030")
    return fig
