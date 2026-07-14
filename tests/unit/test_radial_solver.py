import unittest

import numpy as np

from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
from schwgw.numerics import BoundaryConfig, solve_radial_mode
from schwgw.numerics.boundary_conditions import (
    horizon_ingoing_initial_data,
    radial_domain,
)
from schwgw.perturbations import Sector


class BoundaryConfigTests(unittest.TestCase):
    def test_boundary_config_defaults_are_valid(self) -> None:
        config = BoundaryConfig()

        self.assertGreater(config.r_in_eps, 0.0)
        self.assertIsNone(config.r_out)
        self.assertIsNone(config.required_eval_radius)
        self.assertGreater(config.rtol, 0.0)
        self.assertGreater(config.atol, 0.0)
        self.assertEqual(config.method, "DOP853")
        self.assertIsNone(config.max_step)
        self.assertTrue(config.dense_output)

    def test_radial_domain_uses_horizon_offset_and_background_outer_hint(self) -> None:
        bg = SchwarzschildBackground(M=1.5)
        config = BoundaryConfig(r_in_eps=1e-5, r_out=None)

        r_in, r_out = radial_domain(ell=3, k=0.25, background=bg, config=config)

        self.assertAlmostEqual(r_in, 2.0 * bg.M * (1.0 + config.r_in_eps))
        self.assertEqual(r_out, bg.asymptotic_region_hint(0.25, 3))
        self.assertGreater(r_out, r_in)

    def test_radial_domain_rejects_invalid_parameters(self) -> None:
        bg = SchwarzschildBackground(M=1.0)

        with self.assertRaises(ValueError):
            radial_domain(ell=2, k=0.0, background=bg, config=BoundaryConfig())
        with self.assertRaises(ValueError):
            radial_domain(ell=1, k=0.5, background=bg, config=BoundaryConfig())
        with self.assertRaises(ValueError):
            radial_domain(
                ell=2,
                k=0.5,
                background=bg,
                config=BoundaryConfig(r_in_eps=0.0),
            )
        with self.assertRaises(ValueError):
            radial_domain(
                ell=2,
                k=0.5,
                background=bg,
                config=BoundaryConfig(r_in_eps=1e-4, r_out=2.0),
            )
        with self.assertRaises(ValueError):
            radial_domain(
                ell=2,
                k=0.5,
                background=bg,
                config=BoundaryConfig(r_out=80.0, required_eval_radius=2.0),
            )
        with self.assertRaises(ValueError):
            radial_domain(
                ell=2,
                k=0.5,
                background=bg,
                config=BoundaryConfig(r_out=80.0, required_eval_radius=120.0),
            )
        with self.assertRaises(ValueError):
            radial_domain(
                ell=2,
                k=0.5,
                background=bg,
                config=BoundaryConfig(r_out=80.0, required_eval_radius=np.inf),
            )

    def test_horizon_ingoing_initial_data_has_expected_derivative_ratio(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        k = 0.5
        r_in = 2.0 * bg.M * (1.0 + 1e-6)

        psi, dpsi_dr = horizon_ingoing_initial_data(r_in=r_in, k=k, background=bg)

        self.assertTrue(np.isfinite(psi))
        self.assertTrue(np.isfinite(dpsi_dr))
        self.assertNotEqual(psi, 0.0)
        self.assertAlmostEqual(dpsi_dr / psi, -1j * k / bg.f(r_in))


class RadialSolverTests(unittest.TestCase):
    def test_solve_radial_mode_returns_finite_complex_arrays_for_both_sectors(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        config = BoundaryConfig(r_in_eps=1e-5, r_out=40.0, rtol=1e-8, atol=1e-10)

        for sector in (Sector.ODD, Sector.EVEN, "odd", "even"):
            solution = solve_radial_mode(sector, 2, 0.5, bg, config)

            self.assertEqual(solution.ell, 2)
            self.assertEqual(solution.k, 0.5)
            self.assertEqual(solution.r_grid.shape, solution.psi.shape)
            self.assertEqual(solution.r_grid.shape, solution.dpsi_dr.shape)
            self.assertTrue(np.all(np.diff(solution.r_grid) > 0.0))
            self.assertTrue(np.all(solution.r_grid > bg.horizon_radius))
            self.assertTrue(np.all(np.isfinite(solution.psi)))
            self.assertTrue(np.all(np.isfinite(solution.dpsi_dr)))
            self.assertTrue(np.iscomplexobj(solution.psi))
            self.assertTrue(np.iscomplexobj(solution.dpsi_dr))

    def test_solve_radial_mode_rejects_invalid_sector_string(self) -> None:
        bg = SchwarzschildBackground(M=1.0)

        with self.assertRaises(ValueError):
            solve_radial_mode("polar", 2, 0.5, bg, BoundaryConfig(r_out=20.0))

    def test_outer_matching_coefficients_reconstruct_boundary_state(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        solution = solve_radial_mode(
            Sector.ODD,
            2,
            0.5,
            bg,
            BoundaryConfig(r_in_eps=1e-5, r_out=60.0, rtol=1e-9, atol=1e-11),
        )

        r_out = solution.r_grid[-1]
        r_star = bg.r_star(r_out)
        f = bg.f(r_out)
        ingoing = np.exp(-1j * solution.k * r_star)
        outgoing = np.exp(1j * solution.k * r_star)
        reconstructed_psi = solution.A_in * ingoing + solution.A_out * outgoing
        reconstructed_derivative = (
            (-1j * solution.k / f) * solution.A_in * ingoing
            + (1j * solution.k / f) * solution.A_out * outgoing
        )

        np.testing.assert_allclose(reconstructed_psi, solution.psi[-1], rtol=1e-9, atol=1e-11)
        np.testing.assert_allclose(
            reconstructed_derivative,
            solution.dpsi_dr[-1],
            rtol=1e-9,
            atol=1e-11,
        )
        self.assertLess(solution.diagnostics.boundary_residual, 1e-8)
        self.assertGreater(solution.diagnostics.match_condition_number, 0.0)
        self.assertAlmostEqual(
            solution.phase_factor,
            -solution.A_out / ((-1) ** solution.ell * solution.A_in),
        )

    def test_radial_solution_interpolates_values_and_derivatives_on_domain(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        solution = solve_radial_mode(
            Sector.EVEN,
            3,
            0.4,
            bg,
            BoundaryConfig(r_in_eps=1e-5, r_out=50.0, rtol=1e-9, atol=1e-11),
        )
        index = len(solution.r_grid) // 2
        r_mid = solution.r_grid[index]

        self.assertAlmostEqual(solution.psi_at(r_mid), solution.psi[index])
        self.assertAlmostEqual(solution.dpsi_dr_at(r_mid), solution.dpsi_dr[index])
        self.assertAlmostEqual(
            solution.dpsi_drstar_at(r_mid),
            bg.f(r_mid) * solution.dpsi_dr[index],
        )

        sample_r = solution.r_grid[[1, index, -2]]
        self.assertEqual(solution.psi_at(sample_r).shape, sample_r.shape)
        np.testing.assert_allclose(
            solution.dpsi_drstar_at(sample_r),
            bg.f(sample_r) * solution.dpsi_dr_at(sample_r),
            rtol=1e-12,
            atol=1e-12,
        )

        with self.assertRaises(ValueError):
            solution.psi_at(bg.horizon_radius)
        with self.assertRaises(ValueError):
            solution.psi_at(0.5 * (bg.horizon_radius + solution.r_grid[0]))
        with self.assertRaises(ValueError):
            solution.dpsi_dr_at(solution.r_grid[-1] + 1.0)


if __name__ == "__main__":
    unittest.main()
