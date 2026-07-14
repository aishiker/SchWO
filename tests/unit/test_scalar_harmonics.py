import math
import unittest

import numpy as np

from schwgw.angular import scalar_sph_harm


def _integrate_on_sphere(values: np.ndarray, x_weights: np.ndarray) -> complex:
    phi_count = values.shape[1]
    return np.sum(values * x_weights[:, np.newaxis]) * (2.0 * math.pi / phi_count)


class ScalarSphericalHarmonicTests(unittest.TestCase):
    def test_low_order_values_match_frozen_convention(self) -> None:
        theta = np.array([0.2, 0.9, 1.4])
        phi = np.array([0.1, 0.7, 2.0])

        np.testing.assert_allclose(
            scalar_sph_harm(0, 0, theta, phi),
            np.full_like(theta, 1.0 / math.sqrt(4.0 * math.pi), dtype=complex),
            rtol=1e-14,
            atol=1e-14,
        )
        np.testing.assert_allclose(
            scalar_sph_harm(1, 0, theta, phi),
            math.sqrt(3.0 / (4.0 * math.pi)) * np.cos(theta),
            rtol=1e-14,
            atol=1e-14,
        )
        np.testing.assert_allclose(
            scalar_sph_harm(1, 1, theta, phi),
            -math.sqrt(3.0 / (8.0 * math.pi))
            * np.sin(theta)
            * np.exp(1j * phi),
            rtol=1e-14,
            atol=1e-14,
        )

    def test_conjugation_identity_for_negative_m(self) -> None:
        theta = np.array([0.3, 1.1, 2.2])
        phi = np.array([0.4, 2.5, 5.0])

        y_positive = scalar_sph_harm(4, 3, theta, phi)
        y_negative = scalar_sph_harm(4, -3, theta, phi)

        np.testing.assert_allclose(y_negative, (-1) ** 3 * np.conj(y_positive), rtol=1e-13)

    def test_numeric_orthonormality_on_gauss_legendre_grid(self) -> None:
        x_nodes, x_weights = np.polynomial.legendre.leggauss(80)
        theta = np.arccos(x_nodes)
        phi = np.linspace(0.0, 2.0 * math.pi, 160, endpoint=False)
        theta_grid, phi_grid = np.meshgrid(theta, phi, indexing="ij")

        y32 = scalar_sph_harm(3, 2, theta_grid, phi_grid)
        y31 = scalar_sph_harm(3, 1, theta_grid, phi_grid)

        norm = _integrate_on_sphere(np.conj(y32) * y32, x_weights)
        cross = _integrate_on_sphere(np.conj(y32) * y31, x_weights)

        self.assertAlmostEqual(norm.real, 1.0, delta=1e-10)
        self.assertAlmostEqual(norm.imag, 0.0, delta=1e-13)
        self.assertAlmostEqual(abs(cross), 0.0, delta=1e-12)

    def test_invalid_indices_raise(self) -> None:
        with self.assertRaises(ValueError):
            scalar_sph_harm(-1, 0, 0.5, 0.0)
        with self.assertRaises(ValueError):
            scalar_sph_harm(2, 3, 0.5, 0.0)
