import unittest

import numpy as np

from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
from schwgw.perturbations import V_RW, V_Zerilli
from schwgw.perturbations.potentials import (
    lambda_parameter,
    regge_wheeler_potential,
    zerilli_potential,
)


class RWZPotentialTests(unittest.TestCase):
    def test_public_aliases_match_rwz_potential_functions(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        r = np.array([3.0, 6.0, 20.0])

        np.testing.assert_allclose(V_RW(2, r, bg), regge_wheeler_potential(2, r, bg))
        np.testing.assert_allclose(V_Zerilli(2, r, bg), zerilli_potential(2, r, bg))

    def test_regge_wheeler_potential_has_expected_horizon_and_infinity_limits(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        ell = 3

        near_horizon_r = 2.0 * bg.M * (1.0 + np.array([1e-7, 1e-8, 1e-9]))
        near_horizon = regge_wheeler_potential(ell, near_horizon_r, bg)
        self.assertLess(np.max(np.abs(near_horizon)), 2e-6)

        far_r = np.array([1e5, 2e5, 4e5])
        leading_ratio = regge_wheeler_potential(ell, far_r, bg) / (
            ell * (ell + 1) / far_r**2
        )
        np.testing.assert_allclose(leading_ratio, np.ones_like(far_r), rtol=3e-4)

    def test_zerilli_potential_has_expected_horizon_and_infinity_limits(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        ell = 4

        near_horizon_r = 2.0 * bg.M * (1.0 + np.array([1e-7, 1e-8, 1e-9]))
        near_horizon = zerilli_potential(ell, near_horizon_r, bg)
        self.assertLess(np.max(np.abs(near_horizon)), 2e-6)

        far_r = np.array([1e5, 2e5, 4e5])
        leading_ratio = zerilli_potential(ell, far_r, bg) / (
            ell * (ell + 1) / far_r**2
        )
        np.testing.assert_allclose(leading_ratio, np.ones_like(far_r), rtol=3e-4)

    def test_lambda_parameter_matches_convention(self) -> None:
        self.assertEqual(lambda_parameter(2), 2.0)
        self.assertEqual(lambda_parameter(3), 5.0)
        self.assertEqual(lambda_parameter(4), 9.0)

    def test_radiative_potentials_require_ell_at_least_two(self) -> None:
        bg = SchwarzschildBackground(M=1.0)

        for ell in (0, 1):
            with self.assertRaises(ValueError):
                regge_wheeler_potential(ell, 10.0, bg)
            with self.assertRaises(ValueError):
                zerilli_potential(ell, 10.0, bg)
            with self.assertRaises(ValueError):
                lambda_parameter(ell)

    def test_potentials_require_exterior_radius(self) -> None:
        bg = SchwarzschildBackground(M=1.0)

        for bad_radius in (0.0, -1.0, 2.0, 1.5):
            with self.assertRaises(ValueError):
                regge_wheeler_potential(2, bad_radius, bg)
            with self.assertRaises(ValueError):
                zerilli_potential(2, bad_radius, bg)

    def test_potentials_preserve_scalar_and_array_input_shape(self) -> None:
        bg = SchwarzschildBackground(M=1.0)

        self.assertIsInstance(regge_wheeler_potential(2, 10.0, bg), float)
        self.assertIsInstance(zerilli_potential(2, 10.0, bg), float)

        r = [6.0, 10.0, 20.0]
        rw_values = regge_wheeler_potential(2, r, bg)
        zerilli_values = zerilli_potential(2, r, bg)

        self.assertIsInstance(rw_values, np.ndarray)
        self.assertIsInstance(zerilli_values, np.ndarray)
        self.assertEqual(rw_values.shape, (3,))
        self.assertEqual(zerilli_values.shape, (3,))
