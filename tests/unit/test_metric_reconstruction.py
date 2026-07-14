import unittest

import numpy as np

from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
from schwgw.perturbations import Sector
from schwgw.perturbations.reconstruction import (
    MetricModeComponents,
    reconstruct_metric_mode,
)


class MetricReconstructionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bg = SchwarzschildBackground(M=1.0)

    def test_reconstruction_rejects_non_radiative_or_non_exterior_inputs(self) -> None:
        with self.assertRaises(ValueError):
            reconstruct_metric_mode(Sector.ODD, 1, 0.7, 20.0, 1.0, 0.0, self.bg)
        with self.assertRaises(ValueError):
            reconstruct_metric_mode(Sector.ODD, 2, 0.0, 20.0, 1.0, 0.0, self.bg)
        with self.assertRaises(ValueError):
            reconstruct_metric_mode(Sector.EVEN, 2, 0.7, self.bg.horizon_radius, 1.0, 0.0, self.bg)

    def test_reconstruction_returns_only_rw_gauge_components_for_each_sector(self) -> None:
        odd = reconstruct_metric_mode(Sector.ODD, 2, 0.7, 20.0, 1.0 + 2.0j, 0.1j, self.bg)
        even = reconstruct_metric_mode("even", 2, 0.7, 20.0, 1.0 + 2.0j, 0.1j, self.bg)

        self.assertIsInstance(odd, MetricModeComponents)
        self.assertEqual(odd.sector, Sector.ODD)
        self.assertEqual(set(odd.components), {"Bt", "B1"})
        self.assertEqual(even.sector, Sector.EVEN)
        self.assertEqual(set(even.components), {"tt", "Rt", "L0", "T0"})

    def test_reconstruction_is_linear_in_master_function_and_areal_derivative(self) -> None:
        first = reconstruct_metric_mode(
            Sector.EVEN,
            3,
            0.9,
            18.0,
            0.4 - 0.7j,
            0.03 + 0.02j,
            self.bg,
        )
        second = reconstruct_metric_mode(
            Sector.EVEN,
            3,
            0.9,
            18.0,
            -0.2 + 0.5j,
            -0.01 + 0.04j,
            self.bg,
        )
        combined = reconstruct_metric_mode(
            Sector.EVEN,
            3,
            0.9,
            18.0,
            2.0 * (0.4 - 0.7j) - 0.5 * (-0.2 + 0.5j),
            2.0 * (0.03 + 0.02j) - 0.5 * (-0.01 + 0.04j),
            self.bg,
        )

        for label in first.components:
            self.assertAlmostEqual(
                combined.components[label],
                2.0 * first.components[label] - 0.5 * second.components[label],
            )

    def test_zero_master_function_and_derivative_give_zero_metric_components(self) -> None:
        for sector in (Sector.ODD, Sector.EVEN):
            components = reconstruct_metric_mode(sector, 2, 0.7, 20.0, 0.0, 0.0, self.bg)
            for value in components.components.values():
                self.assertEqual(value, 0.0)

    def test_odd_reconstruction_uses_areal_derivative_not_tortoise_derivative(self) -> None:
        r = 20.0
        dpsi_drstar = 0.03 + 0.02j
        dpsi_dr = dpsi_drstar / self.bg.f(r)

        components = reconstruct_metric_mode(Sector.ODD, 2, 0.7, r, 0.8 - 0.1j, dpsi_dr, self.bg)

        self.assertAlmostEqual(components.components["Bt"], 0.4428571428571429 - 1.885714285714286j)

    def test_formula_smoke_values_match_t6a_audit_for_selected_mode(self) -> None:
        odd = reconstruct_metric_mode(
            Sector.ODD,
            2,
            0.7,
            20.0,
            1.2 - 0.4j,
            0.03 + 0.02j,
            self.bg,
        )
        even = reconstruct_metric_mode(
            Sector.EVEN,
            2,
            0.7,
            20.0,
            1.2 - 0.4j,
            0.03 + 0.02j,
            self.bg,
        )

        expected_odd = {
            "B1": -26.666666666666664 + 8.88888888888889j,
            "Bt": -2.314285714285714j,
        }
        expected_even = {
            "T0": 81.29302325581395 - 16.29767441860465j,
            "Rt": 0.03509043927648579 - 1.1547286821705427j,
            "L0": -14.309893135428558 + 4.796204688553705j,
            "tt": -11.591013439697132 + 3.8849257977285014j,
        }

        for label, expected in expected_odd.items():
            np.testing.assert_allclose(odd.components[label], expected, rtol=1e-14, atol=1e-14)
        for label, expected in expected_even.items():
            np.testing.assert_allclose(even.components[label], expected, rtol=1e-14, atol=1e-14)


if __name__ == "__main__":
    unittest.main()
