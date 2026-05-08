from __future__ import annotations

import unittest

import numpy as np

from modules.cmr import lincoln_petersen
from modules.growth import simulate_growth
from modules.leslie import build_leslie_matrix
from simulations.pva_engine import simulate_pva, summarize_pva


class ModelTests(unittest.TestCase):
    def test_growth_shapes(self) -> None:
        t, exponential, logistic = simulate_growth(100, 0.1, 500, 10)
        self.assertEqual(len(t), 11)
        self.assertGreater(exponential[-1], exponential[0])
        self.assertLessEqual(logistic[-1], 500)

    def test_leslie_matrix_structure(self) -> None:
        matrix = build_leslie_matrix([0, 1.2, 0.8], [0.4, 0.6])
        self.assertEqual(matrix.shape, (3, 3))
        self.assertTrue(np.allclose(matrix[0], [0, 1.2, 0.8]))
        self.assertEqual(matrix[1, 0], 0.4)
        self.assertEqual(matrix[2, 1], 0.6)

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


if __name__ == "__main__":
    unittest.main()
