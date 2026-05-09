from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


APP_TITLE = "ORNI-LAB"
APP_SUBTITLE = "Laboratoire interactif de modélisation ornithologique"


@dataclass(frozen=True)
class ModuleSpec:
    description: str
    renderer: Callable[[dict], None]


def _load_modules() -> dict[str, ModuleSpec]:
    from modules import (
        cmr,
        count_glm,
        csv_analysis,
        descriptive_stats,
        distance_sampling,
        diversity,
        growth,
        leslie,
        lotka_volterra,
        management_scenarios,
        occupancy,
        pva_conservation,
        regression,
        statistical_tests,
        timeseries_population,
    )

    return {
        "Statistiques descriptives": ModuleSpec(
            "Résumer, visualiser et interpréter un jeu de données ornithologique.",
            descriptive_stats.render,
        ),
        "Analyse CSV": ModuleSpec(
            "Charger un fichier CSV et produire une analyse exploratoire guidée.",
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
        "Corrélation et régression": ModuleSpec(
            "Quantifier une relation entre deux variables ornithologiques.",
            regression.render,
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
        "Tests statistiques": ModuleSpec(
            "Comparer groupes, proportions et moyennes avec interprétation.",
            statistical_tests.render,
        ),
        "GLM pour données de comptage": ModuleSpec(
            "Modéliser l'abondance avec Poisson et binomial négatif.",
            count_glm.render,
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
    }


MODULES = _load_modules()
