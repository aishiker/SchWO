import math
import unittest

import numpy as np

from schwgw.angular import scalar_sph_harm, spin_weighted_sph_harm


def _integrate_on_sphere(values: np.ndarray, x_weights: np.ndarray) -> complex:
    phi_count = values.shape[1]
    return np.sum(values * x_weights[:, np.newaxis]) * (2.0 * math.pi / phi_count)


class SpinWeightedSphericalHarmonicTests(unittest.TestCase):
    def test_spin_zero_matches_scalar_spherical_harmonic(self) -> None:
        theta = np.array([0.2, 0.9, 1.7])
        phi = np.array([0.1, 2.1, 4.4])

        np.testing.assert_allclose(
            spin_weighted_sph_harm(0, 3, -2, theta, phi),
            scalar_sph_harm(3, -2, theta, phi),
            rtol=1e-13,
            atol=1e-13,
        )

    def test_high_ell_spin_weighted_values_are_finite(self) -> None:
        for ell in (60, 72, 120):
            with self.subTest(ell=ell):
                value = spin_weighted_sph_harm(-2, ell, 2, 0.4, 0.0)
                self.assertTrue(np.isfinite(value.real))
                self.assertTrue(np.isfinite(value.imag))

    def test_high_ell_spin_zero_matches_scalar_spherical_harmonic(self) -> None:
        theta = np.array([0.3, 0.8, 1.6, 2.4])
        phi = np.array([0.2, 1.3, 2.7, 4.9])

        np.testing.assert_allclose(
            spin_weighted_sph_harm(0, 45, 4, theta, phi),
            scalar_sph_harm(45, 4, theta, phi),
            rtol=5e-11,
            atol=5e-13,
        )

    def test_orthonormality_for_representative_spin_weights(self) -> None:
        x_nodes, x_weights = np.polynomial.legendre.leggauss(90)
        theta = np.arccos(x_nodes)
        phi = np.linspace(0.0, 2.0 * math.pi, 180, endpoint=False)
        theta_grid, phi_grid = np.meshgrid(theta, phi, indexing="ij")

        for spin in (-2, -1, 0, 1, 2):
            with self.subTest(spin=spin):
                y = spin_weighted_sph_harm(spin, 3, 1, theta_grid, phi_grid)
                norm = _integrate_on_sphere(np.conj(y) * y, x_weights)
                self.assertAlmostEqual(norm.real, 1.0, delta=1e-10)
                self.assertAlmostEqual(norm.imag, 0.0, delta=1e-13)

    def test_conjugation_identity_follows_project_wigner_definition(self) -> None:
        # From _sY_lm = (-1)^s N [D^l_{m,-s}]^* and
        # D^l_{m,m'} = (-1)^(m-m') [D^l_{-m,-m'}]^*, this project convention gives
        # (_sY_lm)^* = (-1)^(s+m) _{-s}Y_{l,-m}.
        theta = np.array([0.4, 1.2, 2.3])
        phi = np.array([0.2, 2.7, 5.5])

        y = spin_weighted_sph_harm(2, 4, -1, theta, phi)
        conjugate_partner = spin_weighted_sph_harm(-2, 4, 1, theta, phi)

        np.testing.assert_allclose(np.conj(y), (-1) ** (2 - 1) * conjugate_partner, rtol=1e-13)

    def test_high_ell_conjugation_identity_remains_stable(self) -> None:
        theta = np.array([0.35, 1.1, 2.2])
        phi = np.array([0.2, 2.4, 5.0])
        ell = 72
        spin = 2
        m = -2

        y = spin_weighted_sph_harm(spin, ell, m, theta, phi)
        conjugate_partner = spin_weighted_sph_harm(-spin, ell, -m, theta, phi)

        np.testing.assert_allclose(
            np.conj(y),
            (-1) ** (spin + m) * conjugate_partner,
            rtol=5e-10,
            atol=5e-12,
        )

    def test_invalid_indices_raise(self) -> None:
        with self.assertRaises(ValueError):
            spin_weighted_sph_harm(3, 2, 0, 0.5, 0.0)
        with self.assertRaises(ValueError):
            spin_weighted_sph_harm(0, 2, 3, 0.5, 0.0)
