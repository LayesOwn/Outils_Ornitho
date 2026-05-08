from __future__ import annotations

import streamlit as st

from app.config import APP_SUBTITLE, APP_TITLE, MODULES
from utils.ui import apply_global_style, render_header, render_sidebar


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🪶",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_global_style()
    render_header(APP_TITLE, APP_SUBTITLE)

    context = render_sidebar()
    module_name = st.sidebar.radio("Simulateur", list(MODULES.keys()))
    st.sidebar.caption(MODULES[module_name].description)

    module = MODULES[module_name]
    with st.container():
        module.renderer(context)


if __name__ == "__main__":
    main()
