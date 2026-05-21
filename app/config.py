from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


APP_TITLE = "ORNI-LAB"
APP_SUBTITLE = "Laboratoire interactif de modélisation ornithologique"


@dataclass(frozen=True)
class ModuleSpec:
    description: str
    renderer: Callable[[dict], None]


SECTION_META: dict[str, dict] = {
    "Biostatistique": {
        "emoji": "📊",
        "color": "#4dabf7",
        "description": "Analyser, comparer et modéliser des données d'espèces avec des méthodes statistiques rigoureuses.",
        "subtitle": "Tests, régressions, GLM et exploration de données",
    },
    "Dynamique des populations": {
        "emoji": "🦅",
        "color": "#39d98a",
        "description": "Projeter, modéliser et simuler la dynamique des populations d'oiseaux dans le temps et l'espace.",
        "subtitle": "Croissance, survie, occupation, diversité et conservation",
    },
}


def _load_sections() -> dict[str, dict[str, ModuleSpec]]:
    from modules import (
        cmr,
        count_glm,
        csv_analysis,
        descriptive_stats,
        distance_sampling,
        diversity,
        growth,
        kde,
        leslie,
        lotka_volterra,
        management_scenarios,
        mcp,
        mixed_model,
        occupancy,
        pva_conservation,
        regression,
        statistical_tests,
        timeseries_population,
    )

    return {
        "Biostatistique": {
            "Analyse Fichier": ModuleSpec(
                "Charger un fichier CSV et le rendre disponible dans tous les modules de cette section.",
                csv_analysis.render,
            ),
            "Statistiques descriptives": ModuleSpec(
                "Résumer, visualiser et interpréter un jeu de données ornithologique.",
                descriptive_stats.render,
            ),
            "Corrélation et régression": ModuleSpec(
                "Quantifier une relation entre deux variables ornithologiques.",
                regression.render,
            ),
            "Tests statistiques": ModuleSpec(
                "Comparer groupes, proportions et moyennes avec interprétation.",
                statistical_tests.render,
            ),
            "GLM pour données de comptage": ModuleSpec(
                "Modéliser l'abondance avec Poisson et binomial négatif.",
                count_glm.render,
            ),
            "Modèle mixte (LMM)": ModuleSpec(
                "Effets aléatoires pour données groupées par site, individu ou session.",
                mixed_model.render,
            ),
            "Domaine vital — MCP": ModuleSpec(
                "Minimum Convex Polygon pour estimer le domaine vital depuis des données GPS.",
                mcp.render,
            ),
            "Domaine vital — KDE": ModuleSpec(
                "Kernel Density Estimation pour une estimation probabiliste du domaine vital.",
                kde.render,
            ),
        },
        "Dynamique des populations": {
            "Analyse Fichier": ModuleSpec(
                "Charger un fichier CSV et le rendre disponible dans tous les modules de cette section.",
                csv_analysis.render,
            ),
            "Richesse spécifique et diversité": ModuleSpec(
                "Calculer Shannon, Simpson, équitabilité et courbes d'accumulation.",
                diversity.render,
            ),
            "Croissance exponentielle/logistique": ModuleSpec(
                "Comparer densité-dépendance et croissance libre.",
                growth.render,
            ),
            "Matrices de Leslie": ModuleSpec(
                "Projeter une population structurée en classes d'âge.",
                leslie.render,
            ),
            "Capture-Marquage-Recapture": ModuleSpec(
                "Estimer abondance, survie apparente et incertitude.",
                cmr.render,
            ),
            "Modèles d'occupation": ModuleSpec(
                "Estimer l'occupation et la détectabilité sur des sites à visites répétées.",
                occupancy.render,
            ),
            "Distance sampling": ModuleSpec(
                "Estimer la densité d'oiseaux à partir des distances d'observation.",
                distance_sampling.render,
            ),
            "Lotka-Volterra": ModuleSpec(
                "Explorer les oscillations proie-prédateur.",
                lotka_volterra.render,
            ),
            "Séries temporelles de population": ModuleSpec(
                "Détecter une tendance dans un suivi annuel d'oiseaux.",
                timeseries_population.render,
            ),
            "PVA et conservation": ModuleSpec(
                "Estimer le risque d'extinction sous incertitude environnementale.",
                pva_conservation.render,
            ),
            "Scénarios de gestion": ModuleSpec(
                "Comparer des actions de conservation sur une population d'oiseaux.",
                management_scenarios.render,
            ),
        },
    }


SECTIONS = _load_sections()

# Flat dict kept for backward compatibility with tests and imports
MODULES = {name: spec for section in SECTIONS.values() for name, spec in section.items()}
