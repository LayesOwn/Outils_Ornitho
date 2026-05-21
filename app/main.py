from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path so modules/ and utils/ are importable
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st

from app.auth import check_access
from app.config import APP_SUBTITLE, APP_TITLE, SECTION_META, SECTIONS
from utils.ui import apply_global_style, render_header, render_home_page, render_sidebar, render_teacher_banner, split_columns

# Session-state keys for section-specific data
_SECTION_DATA_KEYS: dict[str, str] = {
    "Biostatistique": "_orni_data_biostat",
    "Dynamique des populations": "_orni_data_dynpop",
}


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🪶",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_global_style()

    if not check_access():
        st.stop()

    render_header(APP_TITLE, APP_SUBTITLE)

    # Initialize navigation state
    if "section" not in st.session_state:
        st.session_state["section"] = None
    if "module" not in st.session_state:
        st.session_state["module"] = None

    context = render_sidebar()
    render_teacher_banner(context)

    section_name: str | None = st.session_state["section"]

    # Inject section-specific data into context
    sk = _SECTION_DATA_KEYS.get(section_name, "") if section_name else ""
    context["section_data_key"] = sk
    if sk and st.session_state.get(sk) is not None:
        section_df = st.session_state[sk]
        num_cols, cat_cols = split_columns(section_df)
        context["data"] = section_df
        context["numeric_columns"] = num_cols
        context["categorical_columns"] = cat_cols
        context["data_filename"] = st.session_state.get(f"{sk}_fname", "")

    if section_name is None:
        render_home_page(SECTIONS, SECTION_META)
    else:
        # Sidebar: section navigation injected below global params
        modules_in_section = SECTIONS[section_name]
        meta = SECTION_META[section_name]

        st.sidebar.divider()
        st.sidebar.markdown(f"**{meta['emoji']} {section_name}**")

        # Data status indicator for this section
        if context.get("data") is not None:
            fname = context.get("data_filename", "fichier.csv")
            n_rows = len(context["data"])
            st.sidebar.info(f"📂 **{fname}**\n{n_rows:,} lignes chargées")
            if st.sidebar.button("✕ Effacer les données", use_container_width=True, key="clear_section_data"):
                st.session_state.pop(sk, None)
                st.session_state.pop(f"{sk}_fname", None)
                st.rerun()

        if st.sidebar.button("← Accueil", use_container_width=True):
            st.session_state["section"] = None
            st.session_state["module"] = None
            st.rerun()

        module_keys = list(modules_in_section.keys())
        current_module = st.session_state["module"]
        default_idx = module_keys.index(current_module) if current_module in module_keys else 0

        module_name = st.sidebar.radio("Module", module_keys, index=default_idx)
        st.session_state["module"] = module_name
        st.sidebar.caption(modules_in_section[module_name].description)

        with st.container():
            try:
                modules_in_section[module_name].renderer(context)
            except Exception as exc:
                st.error(f"Erreur dans le module **{module_name}** : {exc}")
                with st.expander("Détail de l'erreur"):
                    from app.auth import is_teacher
                    if is_teacher():
                        import traceback
                        st.code(traceback.format_exc(), language="python")
                    else:
                        st.caption("Contactez votre enseignant en lui indiquant le message ci-dessus.")


if __name__ == "__main__":
    main()
