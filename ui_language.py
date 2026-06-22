import streamlit as st

LANGUAGES = {
    "en": "English",
    "ro": "Română",
}


def get_language():
    return st.session_state.get("language", "en")


def tr(en, ro):
    return ro if get_language() == "ro" else en


def render_language_switcher():
    if "language" not in st.session_state:
        st.session_state.language = "en"

    current_index = list(LANGUAGES.keys()).index(st.session_state.language)
    selected = st.selectbox(
        "Language / Limbă",
        options=list(LANGUAGES.keys()),
        format_func=lambda code: LANGUAGES[code],
        index=current_index,
        label_visibility="collapsed",
    )
    st.session_state.language = selected
