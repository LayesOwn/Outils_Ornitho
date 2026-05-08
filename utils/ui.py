from __future__ import annotations

import streamlit as st


PLOTLY_COLORS = ["#39d98a", "#4dabf7", "#ff6b6b", "#ffd166", "#b197fc", "#20c997"]


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
        header[data-testid="stHeader"] {
            background: transparent;
            height: 0;
        }
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        div[data-testid="stStatusWidget"],
        #MainMenu {
            display: none;
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
            padding-top: 2.2rem;
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
    mode = st.sidebar.radio(
        "Mode",
        ["Étudiant", "Enseignant"],
        index=0,
        horizontal=True,
    )
    st.sidebar.divider()
    st.sidebar.caption(
        "Les paramètres modifient les sorties en temps réel. "
        "Les exports PDF reprennent les résultats et l'interprétation."
    )
    return {"mode": mode, "is_teacher": mode == "Enseignant"}


def teacher_note(text: str, context: dict) -> None:
    if context.get("is_teacher"):
        st.info(text)


def explain(text: str) -> None:
    st.markdown(f"**Interprétation automatique.** {text}")


def section(title: str, caption: str | None = None) -> None:
    st.subheader(title)
    if caption:
        st.caption(caption)


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


def learning_notes(takeaway: str, limits: str, exercise: str) -> None:
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
