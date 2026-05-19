from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path so modules/ and utils/ are importable
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import streamlit as st

from app.config import APP_SUBTITLE, APP_TITLE, SECTION_META, SECTIONS
from utils.ui import apply_global_style, render_header, render_home_page, render_sidebar, render_teacher_banner


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🪶",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_global_style()
    render_header(APP_TITLE, APP_SUBTITLE)

    # Initialize navigation state
    if "section" not in st.session_state:
        st.session_state["section"] = None
    if "module" not in st.session_state:
        st.session_state["module"] = None

    context = render_sidebar()
    render_teacher_banner(context)

    section_name: str | None = st.session_state["section"]

    if section_name is None:
        render_home_page(SECTIONS, SECTION_META)
    else:
        # Sidebar: section navigation injected below global params
        modules_in_section = SECTIONS[section_name]
        meta = SECTION_META[section_name]

        st.sidebar.divider()
        st.sidebar.markdown(f"**{meta['emoji']} {section_name}**")

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
                    import traceback
                    st.code(traceback.format_exc(), language="python")


if __name__ == "__main__":
    main()
