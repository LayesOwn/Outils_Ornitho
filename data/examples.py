from __future__ import annotations

import numpy as np
import pandas as pd


def wing_mass_dataset(seed: int = 7, n: int = 42) -> pd.DataFrame:
    """Synthetic but realistic passerine dataset for regression exercises."""
    rng = np.random.default_rng(seed)
    wing = rng.normal(72, 6.5, n).clip(55, 92)
    mass = 0.42 * wing - 12 + rng.normal(0, 2.4, n)
    return pd.DataFrame(
        {
            "Longueur de l'aile (mm)": wing.round(1),
            "Masse corporelle (g)": mass.round(1),
        }
    )


def default_leslie_values() -> tuple[list[float], list[float], list[int]]:
    fecundity = [0.0, 0.7, 1.2, 0.8]
    survival = [0.38, 0.62, 0.55]
    initial = [120, 55, 35, 18]
    return fecundity, survival, initial


CMR_SCENARIOS = {
    "Colonies de Sternes pierregarins": {
        "marked": 180,
        "captured": 140,
        "recaptured": 42,
    },
    "Population de Mésanges charbonnières": {
        "marked": 95,
        "captured": 80,
        "recaptured": 21,
    },
    "Dortoir de Moineaux dorés": {
        "marked": 260,
        "captured": 210,
        "recaptured": 64,
    },
}
