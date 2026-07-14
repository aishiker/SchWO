import math
import unittest

import numpy as np

from schwgw.waves import (
    IncidentPlaneGW,
    circular_to_linear,
    linear_to_circular,
    sigma_l,
)


class PolarizationConversionTests(unittest.TestCase):
    def test_linear_and_circular_maps_are_inverse_for_complex_amplitudes(self) -> None:
        samples = [
            (1.0 + 2.0j, -0.5 + 0.75j),
            (-3.0j, 2.25),
            (0.0, 0.0j),
        ]

        for A_plus, A_cross in samples:
            with self.subTest(A_plus=A_plus, A_cross=A_cross):
                A_L, A_R = linear_to_circular(A_plus, A_cross)
                recovered_plus, recovered_cross = circular_to_linear(A_L, A_R)

                self.assertAlmostEqual(recovered_plus, complex(A_plus))
                self.assertAlmostEqual(recovered_cross, complex(A_cross))

    def test_pure_plus_and_pure_cross_follow_frozen_convention(self) -> None:
        A_L, A_R = linear_to_circular(2.0, 0.0)
        self.assertAlmostEqual(A_L, math.sqrt(2.0))
        self.assertAlmostEqual(A_R, math.sqrt(2.0))

        A_L, A_R = linear_to_circular(0.0, 3.0)
        self.assertAlmostEqual(A_L, 3.0j / math.sqrt(2.0))
        self.assertAlmostEqual(A_R, -3.0j / math.sqrt(2.0))

    def test_circular_special_cases_are_checked_algebraically(self) -> None:
        A_plus, A_cross = circular_to_linear(math.sqrt(2.0), 0.0)
        self.assertAlmostEqual(A_plus, 1.0)
        self.assertAlmostEqual(A_cross, -1.0j)

        A_plus, A_cross = circular_to_linear(0.0, math.sqrt(2.0))
        self.assertAlmostEqual(A_plus, 1.0)
        self.assertAlmostEqual(A_cross, 1.0j)

    def test_invalid_amplitudes_fail_when_complex_conversion_fails(self) -> None:
        with self.assertRaises(TypeError):
            linear_to_circular(object(), 1.0)
        with self.assertRaises(TypeError):
            circular_to_linear(np.array([1.0, 2.0]), 1.0)


def _expected_A_lm(ell: int, m: int, A_L: complex, A_R: complex, parity_sign: int) -> complex:
    normalization = (1j) ** ell * math.sqrt(2.0 * math.pi * (2 * ell + 1) / sigma_l(ell))
    return normalization * (
        (A_L if m == -2 else 0.0) + parity_sign * (A_R if m == 2 else 0.0)
    )


class IncidentPlaneGWTests(unittest.TestCase):
    def test_dataclass_validates_k_and_incident_direction(self) -> None:
        wave = IncidentPlaneGW(k=0.75, A_plus=1.0 + 0.25j, A_cross=-0.5j)

        self.assertEqual(wave.k, 0.75)
        self.assertEqual(wave.incident_direction, "+z")

        with self.assertRaises(ValueError):
            IncidentPlaneGW(k=0.0, A_plus=1.0, A_cross=0.0)
        with self.assertRaises(ValueError):
            IncidentPlaneGW(k=-1.0, A_plus=1.0, A_cross=0.0)
        with self.assertRaises(NotImplementedError):
            IncidentPlaneGW(k=1.0, A_plus=1.0, A_cross=0.0, incident_direction="-z")

    def test_circular_properties_match_frozen_convention(self) -> None:
        wave = IncidentPlaneGW(k=2.0, A_plus=0.9 + 1.1j, A_cross=0.4 + 0.6j)
        expected_left, expected_right = linear_to_circular(wave.A_plus, wave.A_cross)

        self.assertAlmostEqual(wave.A_L, expected_left)
        self.assertAlmostEqual(wave.A_R, expected_right)

    def test_sigma_l_matches_radiative_convention(self) -> None:
        self.assertEqual(sigma_l(2), 24)
        self.assertEqual(sigma_l(3), 120)
        self.assertEqual(sigma_l(4), 360)

        with self.assertRaises(ValueError):
            sigma_l(1)

    def test_A_lm_selection_rule_and_even_odd_signs(self) -> None:
        wave = IncidentPlaneGW(k=1.3, A_plus=0.9 + 1.1j, A_cross=0.4 + 0.6j)

        for ell in (2, 3, 4):
            for m in range(-ell, ell + 1):
                with self.subTest(ell=ell, m=m):
                    expected_even = _expected_A_lm(ell, m, wave.A_L, wave.A_R, parity_sign=1)
                    expected_odd = _expected_A_lm(ell, m, wave.A_L, wave.A_R, parity_sign=-1)

                    self.assertAlmostEqual(wave.A_lm_plus(ell, m), expected_even)
                    self.assertAlmostEqual(wave.A_lm_even(ell, m), expected_even)
                    self.assertAlmostEqual(wave.A_lm_minus(ell, m), expected_odd)
                    self.assertAlmostEqual(wave.A_lm_odd(ell, m), expected_odd)

                    if m not in (-2, 2):
                        self.assertEqual(wave.A_lm_even(ell, m), 0.0)
                        self.assertEqual(wave.A_lm_odd(ell, m), 0.0)

    def test_A_lm_rejects_non_radiative_or_invalid_modes(self) -> None:
        wave = IncidentPlaneGW(k=1.0, A_plus=1.0, A_cross=0.0)

        with self.assertRaises(ValueError):
            wave.A_lm_even(1, 0)
        with self.assertRaises(ValueError):
            wave.A_lm_odd(2, 3)

    def test_c_lm_coefficients_follow_frozen_phase_convention(self) -> None:
        wave = IncidentPlaneGW(k=1.7, A_plus=0.9 + 1.1j, A_cross=0.4 + 0.6j)

        for ell in (2, 3, 4):
            for m in range(-ell, ell + 1):
                with self.subTest(ell=ell, m=m):
                    expected_odd = -((1j) ** (ell + 1)) / 2.0 * wave.A_lm_minus(ell, m)
                    expected_even = ((1j) ** (ell + 1)) / wave.k * wave.A_lm_plus(ell, m)

                    self.assertAlmostEqual(wave.c_lm_odd(ell, m), expected_odd)
                    self.assertAlmostEqual(wave.c_lm_even(ell, m), expected_even)

                    if m not in (-2, 2):
                        self.assertEqual(wave.c_lm_odd(ell, m), 0.0)
                        self.assertEqual(wave.c_lm_even(ell, m), 0.0)

    def test_c_lm_odd_exponent_binding_differs_from_common_mistake(self) -> None:
        wave = IncidentPlaneGW(k=1.0, A_plus=1.0, A_cross=0.0)
        ell = 3
        m = -2

        expected = -((1j) ** (ell + 1)) / 2.0 * wave.A_lm_minus(ell, m)
        mistaken = ((-1j) ** (ell + 1)) / 2.0 * wave.A_lm_minus(ell, m)

        self.assertNotAlmostEqual(expected, mistaken)
        self.assertAlmostEqual(wave.c_lm_odd(ell, m), expected)
