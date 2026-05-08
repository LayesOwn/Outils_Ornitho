from __future__ import annotations

import numpy as np
import pandas as pd


def simulate_pva(
    n0: int,
    mean_r: float,
    sd_r: float,
    carrying_capacity: int,
    years: int,
    iterations: int,
    quasi_extinction_threshold: int,
    harvest_or_loss: int = 0,
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for run in range(iterations):
        n = float(n0)
        for year in range(years + 1):
            rows.append(
                {
                    "simulation": run,
                    "annee": year,
                    "effectif": max(n, 0),
                    "quasi_extinct": n <= quasi_extinction_threshold,
                }
            )
            if year == years:
                break
            r = rng.normal(mean_r, sd_r)
            density_term = max(0.0, 1 - n / carrying_capacity)
            n = n + r * n * density_term - harvest_or_loss
            n = max(0.0, n + rng.normal(0, max(1.0, 0.03 * n)))
    return pd.DataFrame(rows)


def summarize_pva(frame: pd.DataFrame, threshold: int) -> dict[str, float]:
    final = frame.groupby("simulation", as_index=False).tail(1)
    ever_low = frame.groupby("simulation")["effectif"].min() <= threshold
    return {
        "median_final": float(final["effectif"].median()),
        "mean_final": float(final["effectif"].mean()),
        "risk": float(ever_low.mean()),
    }
