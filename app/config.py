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
        descriptive_stats,
        growth,
        leslie,
        lotka_volterra,
        management_scenarios,
        pva_conservation,
        regression,
        statistical_tests,
    )

    return {
        "Statistiques descriptives": ModuleSpec(
            "Résumer, visualiser et interpréter un jeu de données ornithologique.",
            descriptive_stats.render,
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
        "Lotka-Volterra": ModuleSpec(
            "Explorer les oscillations proie-prédateur.",
            lotka_volterra.render,
        ),
        "Tests statistiques": ModuleSpec(
            "Comparer groupes, proportions et moyennes avec interprétation.",
            statistical_tests.render,
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
