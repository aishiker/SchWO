import math
import unittest

import numpy as np

from schwgw.angular import scalar_sph_harm, wigner_D


class WignerDTests(unittest.TestCase):
    def test_identity_rotation_is_kronecker_delta(self) -> None:
        ell = 3

        for m in range(-ell, ell + 1):
            for mp in range(-ell, ell + 1):
                expected = 1.0 if m == mp else 0.0
                self.assertAlmostEqual(wigner_D(ell, m, mp, 0.0, 0.0, 0.0), expected)

    def test_ell_zero_is_constant_one(self) -> None:
        self.assertEqual(wigner_D(0, 0, 0, 1.2, 0.7, -0.4), 1.0)

    def test_fixed_ell_matrix_is_unitary(self) -> None:
        ell = 4
        ms = np.arange(-ell, ell + 1)
        matrix = np.array(
            [
                [wigner_D(ell, int(m), int(mp), 0.3, 1.1, -0.8) for mp in ms]
                for m in ms
            ],
            dtype=complex,
        )

        np.testing.assert_allclose(
            matrix.conj().T @ matrix,
            np.eye(2 * ell + 1),
            rtol=1e-12,
            atol=1e-12,
        )

    def test_wigner_relation_reproduces_scalar_harmonics(self) -> None:
        theta = np.array([0.2, 1.0, 2.4])
        phi = np.array([0.1, 2.0, 5.1])
        ell = 3
        m = -2

        from_wigner = math.sqrt((2 * ell + 1) / (4.0 * math.pi)) * np.conj(
            wigner_D(ell, m, 0, phi, theta, 0.0)
        )

        np.testing.assert_allclose(from_wigner, scalar_sph_harm(ell, m, theta, phi), rtol=1e-13)

    def test_high_ell_wigner_values_are_finite(self) -> None:
        for ell in (60, 72, 120):
            with self.subTest(ell=ell):
                value = wigner_D(ell, 2, -2, 0.0, 0.4, 0.0)
                self.assertTrue(np.isfinite(value.real))
                self.assertTrue(np.isfinite(value.imag))

    def test_high_ell_boundary_angles_are_finite_and_keep_identity_limit(self) -> None:
        ell = 72

        self.assertAlmostEqual(wigner_D(ell, 2, 2, 0.3, 0.0, -0.2), np.exp(-0.2j))
        self.assertAlmostEqual(wigner_D(ell, 2, -2, 0.3, 0.0, -0.2), 0.0)

        for mp in (-2, 2):
            with self.subTest(mp=mp):
                value = wigner_D(ell, 2, mp, 0.0, math.pi, 0.0)
                self.assertTrue(np.isfinite(value.real))
                self.assertTrue(np.isfinite(value.imag))

    def test_invalid_indices_raise(self) -> None:
        with self.assertRaises(ValueError):
            wigner_D(-1, 0, 0, 0.0, 0.0, 0.0)
        with self.assertRaises(ValueError):
            wigner_D(2, 3, 0, 0.0, 0.0, 0.0)
        with self.assertRaises(ValueError):
            wigner_D(2, 0, -3, 0.0, 0.0, 0.0)
