import math
import unittest

import numpy as np

from schwgw.backgrounds import SchwarzschildBackground as PackageSchwarzschildBackground
from schwgw.backgrounds.schwarzschild import SchwarzschildBackground


class SchwarzschildBackgroundTests(unittest.TestCase):
    def test_package_import_exposes_schwarzschild_background(self) -> None:
        self.assertIs(PackageSchwarzschildBackground, SchwarzschildBackground)

    def test_f_matches_schwarzschild_lapse(self) -> None:
        bg = SchwarzschildBackground(M=2.5)
        r = np.array([6.0, 10.0, 25.0])

        np.testing.assert_allclose(bg.f(r), 1.0 - 2.0 * bg.M / r, rtol=1e-14)
        self.assertIsInstance(bg.f(10.0), float)
        np.testing.assert_allclose(bg.f([6.0, 10.0]), np.array([1.0 / 6.0, 0.5]))

    def test_df_dr_matches_schwarzschild_lapse_derivative(self) -> None:
        bg = SchwarzschildBackground(M=2.5)
        r = np.array([6.0, 10.0, 25.0])

        np.testing.assert_allclose(bg.df_dr(r), 2.0 * bg.M / r**2, rtol=1e-14)
        self.assertIsInstance(bg.df_dr(10.0), float)

    def test_tortoise_derivative_matches_inverse_lapse(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        r_values = np.array([3.0, 6.0, 20.0])
        step = 1e-5

        numerical = (bg.r_star(r_values + step) - bg.r_star(r_values - step)) / (
            2.0 * step
        )

        np.testing.assert_allclose(numerical, bg.drstar_dr(r_values), rtol=1e-9)
        np.testing.assert_allclose(bg.drstar_dr(r_values), 1.0 / bg.f(r_values), rtol=1e-14)

    def test_lapse_has_expected_horizon_and_infinity_limits(self) -> None:
        bg = SchwarzschildBackground(M=1.0)

        self.assertLess(abs(bg.f(2.0 * bg.M * (1.0 + 1e-12))), 2e-12)
        self.assertTrue(math.isclose(bg.f(1e16), 1.0, rel_tol=1e-12))

    def test_inverse_tortoise_round_trips_exterior_radius(self) -> None:
        bg = SchwarzschildBackground(M=1.7)
        r_values = np.array([3.5, 4.0, 8.0, 30.0])

        recovered = bg.r_from_r_star(bg.r_star(r_values))

        np.testing.assert_allclose(recovered, r_values, rtol=1e-13, atol=1e-13)
        self.assertIsInstance(bg.r_from_r_star(bg.r_star(6.0)), float)

    def test_exterior_only_methods_reject_horizon_and_interior_radius(self) -> None:
        bg = SchwarzschildBackground(M=1.0)

        for bad_radius in (0.0, -1.0, 2.0, 1.5):
            with self.assertRaises(ValueError):
                bg.r_star(bad_radius)
            with self.assertRaises(ValueError):
                bg.drstar_dr(bad_radius)

    def test_positive_mass_is_required(self) -> None:
        with self.assertRaises(ValueError):
            SchwarzschildBackground(M=0.0)
        with self.assertRaises(ValueError):
            SchwarzschildBackground(M=-1.0)

    def test_horizon_radius_is_two_m(self) -> None:
        bg = SchwarzschildBackground(M=3.0)

        self.assertTrue(math.isclose(bg.horizon_radius, 6.0, rel_tol=0.0, abs_tol=0.0))
