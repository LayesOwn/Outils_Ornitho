from __future__ import annotations

import numpy as np
import pandas as pd


def _validate_pva_inputs(
    n0: int,
    carrying_capacity: int,
    years: int,
    iterations: int,
    quasi_extinction_threshold: int,
) -> None:
    if n0 < 0:
        raise ValueError("n0 must be positive or zero")
    if carrying_capacity <= 0:
        raise ValueError("carrying_capacity must be strictly positive")
    if years < 0:
        raise ValueError("years must be positive or zero")
    if iterations <= 0:
        raise ValueError("iterations must be strictly positive")
    if quasi_extinction_threshold < 0:
        raise ValueError("quasi_extinction_threshold must be positive or zero")


def project_next_population(n: float, r: float, carrying_capacity: int, harvest_or_loss: int = 0) -> float:
    """Project one deterministic PVA step with non-negative abundance."""
    if carrying_capacity <= 0:
        raise ValueError("carrying_capacity must be strictly positive")
    if n <= 0:
        return 0.0

    if r >= 0:
        annual_growth = np.exp(r)
        next_n = (carrying_capacity * n * annual_growth) / (
            carrying_capacity + n * (annual_growth - 1)
        )
    else:
        # Pure exponential decay when r < 0: density-dependence is irrelevant for a declining population.
        next_n = n * np.exp(r)

    next_n -= harvest_or_loss
    return max(0.0, next_n)


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
    _validate_pva_inputs(n0, carrying_capacity, years, iterations, quasi_extinction_threshold)
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
            n = project_next_population(n, r, carrying_capacity, harvest_or_loss)
            if n > 0:
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
