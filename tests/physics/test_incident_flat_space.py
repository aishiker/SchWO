import unittest

import numpy as np
import pytest
from scipy.special import spherical_jn

from schwgw.waves import IncidentPlaneGW


pytestmark = pytest.mark.physics


class IncidentFlatSpaceMasterTests(unittest.TestCase):
    def test_flat_space_master_functions_match_spherical_bessel_formulas(self) -> None:
        wave = IncidentPlaneGW(k=1.7, A_plus=0.9 + 1.1j, A_cross=0.4 + 0.6j)
        ell = 4
        r = np.array([0.25, 1.5, 8.0])

        expected_odd = -wave.k * r * wave.A_lm_minus(ell, -2) * spherical_jn(ell, wave.k * r)
        expected_even = 2.0 * r * wave.A_lm_plus(ell, 2) * spherical_jn(ell, wave.k * r)

        np.testing.assert_allclose(
            wave.flat_space_master_odd(ell, -2, r),
            expected_odd,
            rtol=1e-14,
            atol=1e-14,
        )
        np.testing.assert_allclose(
            wave.flat_space_master_even(ell, 2, r),
            expected_even,
            rtol=1e-14,
            atol=1e-14,
        )

    def test_flat_space_master_functions_handle_scalar_and_array_r(self) -> None:
        wave = IncidentPlaneGW(k=0.8, A_plus=1.0, A_cross=0.0)

        odd_scalar = wave.flat_space_master_odd(2, -2, 3.0)
        even_values = wave.flat_space_master_even(2, 2, [1.0, 2.0, 3.0])

        self.assertIsInstance(odd_scalar, complex)
        self.assertIsInstance(even_values, np.ndarray)
        self.assertEqual(even_values.shape, (3,))

    def test_flat_space_master_functions_reject_nonpositive_radius(self) -> None:
        wave = IncidentPlaneGW(k=1.0, A_plus=1.0, A_cross=0.0)

        for bad_r in (0.0, -1.0, [1.0, 0.0, 2.0]):
            with self.subTest(r=bad_r):
                with self.assertRaises(ValueError):
                    wave.flat_space_master_odd(2, -2, bad_r)
                with self.assertRaises(ValueError):
                    wave.flat_space_master_even(2, 2, bad_r)

    def test_large_kr_matches_outgoing_ingoing_asymptotic_form(self) -> None:
        wave = IncidentPlaneGW(k=1.3, A_plus=0.9 + 1.1j, A_cross=0.4 + 0.6j)
        ell = 3
        r = np.array([20000.0, 30000.0, 50000.0])
        phase = wave.k * r
        radial_phase = np.exp(-1j * phase) - (-1) ** ell * np.exp(1j * phase)

        odd_expected = wave.c_lm_odd(ell, -2) * radial_phase
        even_expected = wave.c_lm_even(ell, 2) * radial_phase

        np.testing.assert_allclose(
            wave.flat_space_master_odd(ell, -2, r),
            odd_expected,
            rtol=7e-4,
            atol=7e-4,
        )
        np.testing.assert_allclose(
            wave.flat_space_master_even(ell, 2, r),
            even_expected,
            rtol=7e-4,
            atol=7e-4,
        )
