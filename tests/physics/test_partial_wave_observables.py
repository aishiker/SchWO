import unittest

import numpy as np
import pytest

from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
from schwgw.numerics import BoundaryConfig
from schwgw.scattering.partial_wave import compute_polarization


pytestmark = pytest.mark.physics


class PartialWaveObservablePhysicsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bg = SchwarzschildBackground(M=1.0)
        self.boundary_config = BoundaryConfig(r_in_eps=1e-5, r_out=60.0, rtol=1e-8, atol=1e-10)

    def test_finite_radius_polarization_smoke_values_are_finite(self) -> None:
        result = compute_polarization(
            background=self.bg,
            k=0.5,
            r=20.0,
            theta=0.4,
            phi=0.3,
            A_plus=1.0 + 0.2j,
            A_cross=0.1 - 0.4j,
            lmax=4,
            boundary_config=self.boundary_config,
        )

        for value in (result.h_plus, result.h_cross, result.psi0_hat, result.psi4_hat):
            self.assertTrue(np.isfinite(value.real))
            self.assertTrue(np.isfinite(value.imag))
        self.assertEqual(result.diagnostics["lmax"], 4.0)
        self.assertEqual(result.diagnostics["radial_solve_count"], 6.0)
        self.assertIn("max_boundary_residual", result.diagnostics)
        self.assertIn("max_wronskian_residual", result.diagnostics)

    def test_lmax_change_remains_finite_and_records_diagnostics(self) -> None:
        common = dict(
            background=self.bg,
            k=0.5,
            r=20.0,
            theta=0.4,
            phi=0.3,
            A_plus=1.0 + 0.2j,
            A_cross=0.1 - 0.4j,
            boundary_config=self.boundary_config,
        )

        l3 = compute_polarization(**common, lmax=3)
        l4 = compute_polarization(**common, lmax=4)

        self.assertEqual(l3.diagnostics["lmax"], 3.0)
        self.assertEqual(l4.diagnostics["lmax"], 4.0)
        self.assertTrue(np.isfinite((l4.h_plus - l3.h_plus).real))
        self.assertTrue(np.isfinite((l4.h_plus - l3.h_plus).imag))
        self.assertTrue(np.isfinite((l4.h_cross - l3.h_cross).real))
        self.assertTrue(np.isfinite((l4.h_cross - l3.h_cross).imag))

    def test_near_axis_angles_do_not_produce_nan_or_inf(self) -> None:
        result = compute_polarization(
            background=self.bg,
            k=0.5,
            r=20.0,
            theta=0.0,
            phi=0.0,
            A_plus=1.0,
            A_cross=0.3j,
            lmax=3,
            boundary_config=self.boundary_config,
        )

        for value in (result.h_plus, result.h_cross, result.psi0_hat, result.psi4_hat):
            self.assertTrue(np.isfinite(value.real))
            self.assertTrue(np.isfinite(value.imag))


if __name__ == "__main__":
    unittest.main()
