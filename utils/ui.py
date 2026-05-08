from __future__ import annotations

import streamlit as st


def apply_global_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --orni-green: #1f6f5b;
            --orni-ink: #17211f;
            --orni-muted: #5c6b66;
            --orni-bg: #f7faf8;
            --orni-line: #d9e5df;
        }
        .stApp {
            background: var(--orni-bg);
            color: var(--orni-ink);
        }
        h1, h2, h3 {
            letter-spacing: 0;
        }
        [data-testid="stSidebar"] {
            background: #eef5f1;
            border-right: 1px solid var(--orni-line);
        }
        .orni-hero {
            padding: 1.2rem 1.4rem;
            border-left: 6px solid var(--orni-green);
            background: #ffffff;
            margin-bottom: 1rem;
        }
        .orni-caption {
            color: var(--orni-muted);
            font-size: 0.98rem;
        }
        .metric-card {
            background: #ffffff;
            border: 1px solid var(--orni-line);
            border-radius: 8px;
            padding: 0.85rem 1rem;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid var(--orni-line);
            border-radius: 8px;
            padding: 0.75rem;
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
