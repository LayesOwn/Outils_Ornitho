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
    from modules import cmr, growth, leslie, lotka_volterra, regression

    return {
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
    }


MODULES = _load_modules()
