"""
Contrôle d'accès à deux niveaux.

Variables d'environnement à définir sur PythonAnywhere (onglet Web > Environment variables) :
  ACCESS_CODE_STUDENT  — code pour les étudiants (mode Étudiant forcé)
  ACCESS_CODE_TEACHER  — code pour l'enseignant  (accès complet + mode Enseignant)

Si les deux variables sont vides → accès libre (développement local).
Un même code peut être utilisé pour les deux rôles si nécessaire.
"""
from __future__ import annotations

import os

import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SESSION_KEY  = "ornilab_authenticated"
ROLE_KEY     = "ornilab_role"          # "student" | "teacher" | "free"


def get_role() -> str:
    """Retourne le rôle de la session courante."""
    return st.session_state.get(ROLE_KEY, "free")


def is_teacher() -> bool:
    return get_role() == "teacher"


def check_access() -> bool:
    """
    Affiche l'écran de connexion si l'utilisateur n'est pas authentifié.
    Retourne True si l'accès est accordé, False sinon.
    """
    if st.session_state.get(SESSION_KEY):
        return True

    student_code = os.environ.get("ACCESS_CODE_STUDENT", "").strip()
    teacher_code = os.environ.get("ACCESS_CODE_TEACHER", "").strip()

    if not student_code and not teacher_code:
        # Aucun code configuré → accès libre uniquement en développement local
        import os
        on_pythonanywhere = bool(os.environ.get("PYTHONANYWHERE_SITE") or os.environ.get("PYTHONANYWHERE_DOMAIN"))
        if on_pythonanywhere:
            # Sur PythonAnywhere sans codes configurés : bloquer avec message explicite
            st.error("⚠️ Configuration manquante : les variables ACCESS_CODE_STUDENT et ACCESS_CODE_TEACHER ne sont pas définies.")
            st.info("Rendez-vous dans l'onglet **Web > Environment variables** de PythonAnywhere pour les configurer.")
            st.stop()
            return False
        st.session_state[SESSION_KEY] = True
        st.session_state[ROLE_KEY] = "free"
        return True

    _render_login(student_code, teacher_code)
    return False


def _render_login(student_code: str, teacher_code: str) -> None:
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("---")
        st.markdown(
            "<h2 style='text-align:center'>🪶 ORNI-LAB</h2>"
            "<p style='text-align:center;color:#8aa89a;margin-bottom:1.5rem'>"
            "Laboratoire pédagogique interactif en écologie quantitative</p>",
            unsafe_allow_html=True,
        )

        st.markdown("### 🔑 Accès sécurisé")
        st.caption("Entrez le code fourni par votre enseignant pour cette séance.")

        code_saisi = st.text_input(
            "Code d'accès",
            type="password",
            placeholder="Votre code de séance…",
            key="login_input",
        )

        if st.button("Valider →", type="primary", use_container_width=True):
            role = _check_code(code_saisi.strip(), student_code, teacher_code)
            if role:
                st.session_state[SESSION_KEY] = True
                st.session_state[ROLE_KEY] = role
                st.rerun()
            else:
                st.error("Code invalide. Vérifiez auprès de votre enseignant.")

        st.markdown("---")
        st.caption(
            "Enseignants : définir `ACCESS_CODE_STUDENT` et `ACCESS_CODE_TEACHER` "
            "dans les variables d'environnement PythonAnywhere."
        )


def _check_code(code: str, student_code: str, teacher_code: str) -> str | None:
    """Retourne le rôle correspondant au code, ou None si invalide."""
    if not code:
        return None
    if teacher_code and code == teacher_code:
        return "teacher"
    if student_code and code == student_code:
        return "student"
    return None
