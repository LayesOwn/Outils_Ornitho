from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from core.export import _pdf_safe_text, build_pdf_report
from modules.cmr import lincoln_petersen
from modules.csv_analysis import (
    clean_uploaded_data,
    compare_two_groups,
    describe_numeric_columns,
    fit_linear_regression,
    split_columns_by_type,
)
from modules.diversity import accumulation_curve, compute_diversity_indices, simulate_community
from modules.distance_sampling import fit_half_normal, simulate_distances
from modules.growth import simulate_growth
from modules.leslie import build_leslie_matrix, compute_demography
from modules.occupancy import fit_occupancy, simulate_detection_history
from modules.timeseries_population import mann_kendall_test, simulate_population_series
from simulations.pva_engine import project_next_population, simulate_pva, summarize_pva


class ModelTests(unittest.TestCase):
    def test_growth_shapes(self) -> None:
        t, exponential, logistic = simulate_growth(100, 0.1, 500, 10)
        self.assertEqual(len(t), 11)
        self.assertGreater(exponential[-1], exponential[0])
        self.assertLessEqual(logistic[-1], 500)

    def test_growth_logistic_stays_non_negative_when_initial_above_capacity(self) -> None:
        _t, _exponential, logistic = simulate_growth(2000, 0.3, 50, 30)
        self.assertTrue(np.isfinite(logistic).all())
        self.assertTrue((logistic >= 0).all())
        self.assertLess(logistic[-1], logistic[0])

    def test_growth_rejects_invalid_inputs(self) -> None:
        with self.assertRaises(ValueError):
            simulate_growth(0, 0.1, 500, 10)
        with self.assertRaises(ValueError):
            simulate_growth(100, 0.1, 0, 10)

    def test_leslie_matrix_structure(self) -> None:
        matrix = build_leslie_matrix([0, 1.2, 0.8], [0.4, 0.6])
        self.assertEqual(matrix.shape, (3, 3))
        self.assertTrue(np.allclose(matrix[0], [0, 1.2, 0.8]))
        self.assertEqual(matrix[1, 0], 0.4)
        self.assertEqual(matrix[2, 1], 0.6)

    def test_leslie_validation_rejects_inconsistent_lengths(self) -> None:
        with self.assertRaises(ValueError):
            build_leslie_matrix([0, 1.2, 0.8], [0.4])  # 3 fecundities needs 2 survivals

    def test_leslie_sensitivity_elasticity(self) -> None:
        matrix = build_leslie_matrix([0, 0.7, 1.2, 0.8], [0.38, 0.62, 0.55])
        demo = compute_demography(matrix)
        self.assertGreater(demo["lambda"], 0)
        self.assertAlmostEqual(demo["stable_age"].sum(), 1.0, places=5)
        self.assertAlmostEqual(float(demo["repro_values"][0]), 1.0, places=5)
        # Elasticities of non-zero elements should sum to 1
        elas_sum = float(np.sum(demo["elasticity"][matrix > 0]))
        self.assertAlmostEqual(elas_sum, 1.0, delta=0.01)

    def test_cmr_estimate_positive(self) -> None:
        estimate, low, high = lincoln_petersen(180, 140, 42)
        self.assertGreater(estimate, 0)
        self.assertLess(low, estimate)
        self.assertGreater(high, estimate)

    def test_pva_summary_bounds(self) -> None:
        data = simulate_pva(100, 0.02, 0.01, 500, 10, 20, 10, seed=3)
        summary = summarize_pva(data, 10)
        self.assertGreaterEqual(summary["risk"], 0)
        self.assertLessEqual(summary["risk"], 1)
        self.assertGreaterEqual(summary["median_final"], 0)

    def test_pva_step_declines_above_capacity_with_positive_growth(self) -> None:
        next_n = project_next_population(1200, 0.1, 600)
        self.assertLess(next_n, 1200)

    def test_pva_step_declines_with_negative_growth(self) -> None:
        next_n = project_next_population(200, -0.1, 600)
        self.assertAlmostEqual(next_n, 180.967, places=3)

    def test_pdf_export_normalizes_scientific_symbols(self) -> None:
        self.assertEqual(_pdf_safe_text("λ α β γ δ N₀ → K R²"), "lambda alpha beta gamma delta N0 -> K R2")
        pdf = build_pdf_report("Test λ", ["N₀ → K"])
        self.assertIsInstance(pdf, bytes)
        self.assertTrue(pdf.startswith(b"%PDF-"))

    def test_csv_cleaning_and_column_detection(self) -> None:
        data = pd.DataFrame(
            {
                " masse ": ["10,5", "11,0", "12,2"],
                "Habitat": ["Foret", "Savane", "Foret"],
                "Vide": [np.nan, np.nan, np.nan],
            }
        )
        cleaned = clean_uploaded_data(data)
        numeric_columns, categorical_columns = split_columns_by_type(cleaned)

        self.assertEqual(cleaned.columns.tolist(), ["masse", "Habitat"])
        self.assertIn("masse", numeric_columns)
        self.assertIn("Habitat", categorical_columns)
        self.assertAlmostEqual(float(cleaned["masse"].iloc[0]), 10.5)

    def test_csv_numeric_summary(self) -> None:
        data = pd.DataFrame({"count": [1, 2, 3, np.nan]})
        summary = describe_numeric_columns(data, ["count"])

        self.assertEqual(summary.loc["count", "n"], 3)
        self.assertEqual(summary.loc["count", "missing"], 1)
        self.assertEqual(summary.loc["count", "mediane"], 2)

    def test_csv_regression_and_group_comparison(self) -> None:
        data = pd.DataFrame(
            {
                "wing": [1, 2, 3, 4, 5, 6],
                "mass": [2, 4, 6, 8, 10, 12],
                "habitat": ["A", "A", "A", "B", "B", "B"],
            }
        )
        regression = fit_linear_regression(data, "wing", "mass")
        comparison = compare_two_groups(data, "habitat", "mass")

        self.assertAlmostEqual(regression["slope"], 2.0)
        self.assertAlmostEqual(regression["r2"], 1.0)
        self.assertLess(comparison["difference"], 0)

    def test_pva_extinct_population_stays_extinct(self) -> None:
        data = simulate_pva(0, 0.1, 0.0, 500, 10, 10, 0, seed=1)
        self.assertTrue((data["effectif"] == 0).all())

    def test_pva_reproducible_with_same_seed(self) -> None:
        data1 = simulate_pva(100, 0.05, 0.1, 500, 10, 5, 10, seed=99)
        data2 = simulate_pva(100, 0.05, 0.1, 500, 10, 5, 10, seed=99)
        pd.testing.assert_frame_equal(data1, data2)

    def test_csv_regression_rejects_insufficient_data(self) -> None:
        data = pd.DataFrame({"x": [1.0, 2.0], "y": [2.0, 4.0]})
        with self.assertRaises(ValueError):
            fit_linear_regression(data, "x", "y")

    def test_csv_group_comparison_rejects_singleton_group(self) -> None:
        data = pd.DataFrame({"group": ["A", "B", "B", "B"], "value": [1.0, 2.0, 3.0, 4.0]})
        with self.assertRaises(ValueError):
            compare_two_groups(data, "group", "value")

    # --- diversity ---

    def test_diversity_indices_uniform_community(self) -> None:
        counts = np.array([10, 10, 10, 10])
        idx = compute_diversity_indices(counts)
        self.assertEqual(idx["S"], 4)
        self.assertAlmostEqual(idx["J"], 1.0, places=3)

    def test_diversity_indices_monodominant(self) -> None:
        counts = np.array([100, 1, 1, 1])
        idx = compute_diversity_indices(counts)
        self.assertLess(idx["H"], np.log(4))
        self.assertLess(idx["J"], 1.0)

    def test_accumulation_curve_shape(self) -> None:
        data = simulate_community(30, 10, 2.0, seed=1)
        species_cols = [c for c in data.columns if c.startswith("Esp")]
        acc = accumulation_curve(data[species_cols].values, iterations=50, seed=1)
        self.assertEqual(len(acc), 30)
        self.assertTrue((np.diff(acc["Moyenne"]) >= 0).all())

    # --- occupancy ---

    def test_occupancy_high_detection_recovers_psi(self) -> None:
        history = simulate_detection_history(200, 5, psi=0.8, p=0.9, seed=7)
        est = fit_occupancy(history)
        self.assertAlmostEqual(est["psi"], 0.8, delta=0.10)
        self.assertAlmostEqual(est["p"], 0.9, delta=0.10)

    def test_occupancy_naive_underestimates_psi(self) -> None:
        history = simulate_detection_history(300, 2, psi=0.7, p=0.3, seed=11)
        est = fit_occupancy(history)
        self.assertLess(est["naive"], est["psi"])

    # --- timeseries ---

    def test_mann_kendall_increasing_series(self) -> None:
        series = np.arange(1, 21, dtype=float)
        mk = mann_kendall_test(series)
        self.assertGreater(mk["S"], 0)
        self.assertLess(mk["pvalue"], 0.001)
        self.assertEqual(mk["trend"], "croissante")

    def test_mann_kendall_flat_series(self) -> None:
        series = np.ones(20)
        mk = mann_kendall_test(series)
        self.assertEqual(mk["S"], 0.0)

    def test_timeseries_simulation_shape(self) -> None:
        data = simulate_population_series(25, 500, -0.03, 0.15, seed=1)
        self.assertEqual(len(data), 25)
        self.assertTrue((data["Effectif"] >= 0).all())

    # --- distance sampling ---

    def test_distance_sampling_recovers_sigma(self) -> None:
        distances = simulate_distances(5.0, 60.0, 200.0, 500.0, 10, seed=1)
        fit = fit_half_normal(distances, 200.0)
        self.assertAlmostEqual(fit["sigma"], 60.0, delta=15.0)
        self.assertGreater(fit["esw"], 0)

    def test_distance_sampling_esw_less_than_strip_width(self) -> None:
        distances = simulate_distances(3.0, 40.0, 150.0, 400.0, 5, seed=2)
        fit = fit_half_normal(distances, 150.0)
        self.assertLess(fit["esw"], 150.0)


if __name__ == "__main__":
    unittest.main()
