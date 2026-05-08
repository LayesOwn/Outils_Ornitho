from __future__ import annotations


def build_tutor_prompt(module_name: str, student_level: str, result_summary: str) -> str:
    """Prepare a future AI tutor prompt without coupling the app to one provider."""
    return (
        "Tu es un assistant pédagogique pour des étudiants de Master en ornithologie. "
        f"Module : {module_name}. Niveau : {student_level}. "
        f"Résultats à expliquer : {result_summary}. "
        "Explique avec rigueur, donne une intuition biologique et propose une question de vérification."
    )
