import sys, unittest
from dataclasses import replace
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ac import (ACParams, optimal_trajectory, twap_trajectory, front_loaded, expected_cost,  # noqa: E402
                cost_variance, kappa, simulate_shortfall)


class TestAC(unittest.TestCase):
    def setUp(self):
        self.p = ACParams()

    def test_boundary_conditions(self):
        for lam in (0.0, 1e-7, 1e-5):
            x = optimal_trajectory(lam, self.p)
            self.assertAlmostEqual(x[0], self.p.X)
            self.assertAlmostEqual(x[-1], 0.0, places=6)
            self.assertTrue(np.all(np.diff(x) <= 1e-9))  # selling only

    def test_risk_neutral_is_twap(self):
        np.testing.assert_allclose(optimal_trajectory(1e-14, self.p), twap_trajectory(self.p), rtol=1e-5, atol=1e-3)

    def test_higher_risk_aversion_sells_faster(self):
        x_lo, x_hi = optimal_trajectory(1e-7, self.p), optimal_trajectory(1e-5, self.p)
        self.assertLess(x_hi[1], x_lo[1])
        self.assertGreater(kappa(1e-5, self.p), kappa(1e-7, self.p))

    def test_twap_minimises_expected_cost(self):
        E_twap = expected_cost(twap_trajectory(self.p), self.p)
        for lam in (1e-7, 1e-6, 1e-5):
            self.assertLessEqual(E_twap, expected_cost(optimal_trajectory(lam, self.p), self.p) + 1e-6)

    def test_immediate_has_zero_variance(self):
        self.assertEqual(cost_variance(front_loaded(self.p), self.p), 0.0)

    def test_optimal_beats_perturbations(self):
        lam = 1e-6
        x = optimal_trajectory(lam, self.p)
        U = expected_cost(x, self.p) + lam * cost_variance(x, self.p)
        rng = np.random.default_rng(0)
        for _ in range(50):
            y = x.copy()
            y[1:-1] += rng.normal(0, 2e4, len(x) - 2)
            self.assertGreaterEqual(expected_cost(y, self.p) + lam * cost_variance(y, self.p), U - 1e-3)

    def test_monte_carlo_matches_analytic(self):
        x = optimal_trajectory(1e-6, self.p)
        sf = simulate_shortfall(x, self.p, 200000, seed=3)
        E, sd = expected_cost(x, self.p), np.sqrt(cost_variance(x, self.p))
        self.assertLess(abs(sf.mean() - E), 4 * sd / np.sqrt(len(sf)))
        self.assertAlmostEqual(sf.std() / sd, 1.0, places=2)


if __name__ == "__main__":
    unittest.main()
