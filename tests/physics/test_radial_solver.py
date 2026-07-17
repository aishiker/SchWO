import json
import unittest
from dataclasses import dataclass

import numpy as np
import pytest

from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
from schwgw.numerics import radial_solver
from schwgw.numerics import BoundaryConfig, solve_radial_mode
from schwgw.perturbations import Sector, V_RW


@dataclass(frozen=True)
class ModeDiagnostic:
    sector: str
    ell: int
    k: float
    solver: str
    barrier_action: float
    abs_A_in: float
    abs_A_out: float
    wronskian_near_horizon: complex
    wronskian_mid_grid: complex
    wronskian_outer: complex
    wronskian_residual: float
    flux_residual: float
    boundary_residual: float
    max_abs_psi: float
    ode_n_steps: int
    match_condition_number: float


@pytest.mark.physics
class RadialSolverPhysicsTests(unittest.TestCase):
    def test_returned_solution_satisfies_radial_ode_residual(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        solution = solve_radial_mode(
            Sector.ODD,
            2,
            0.5,
            bg,
            BoundaryConfig(r_in_eps=1e-5, r_out=80.0, rtol=1e-10, atol=1e-12),
        )
        probe_radii = np.linspace(5.0, 70.0, 8)
        step = 1e-3
        residuals = []

        for radius in probe_radii:
            d2psi_dr2 = (
                solution.dpsi_dr_at(radius + step)
                - solution.dpsi_dr_at(radius - step)
            ) / (2.0 * step)
            psi = solution.psi_at(radius)
            dpsi_dr = solution.dpsi_dr_at(radius)
            lapse = bg.f(radius)
            potential = V_RW(solution.ell, radius, bg)
            residual = (
                lapse**2 * d2psi_dr2
                + lapse * bg.df_dr(radius) * dpsi_dr
                + (solution.k**2 - potential) * psi
            )
            scale = max(
                abs(lapse**2 * d2psi_dr2)
                + abs(lapse * bg.df_dr(radius) * dpsi_dr)
                + abs((solution.k**2 - potential) * psi),
                np.finfo(float).eps,
            )
            residuals.append(abs(residual) / scale)

        # This probes the stored cubic interpolation with a finite-difference
        # derivative, so the threshold is an interpolation residual rather than
        # the solve_ivp local truncation error.
        self.assertLess(max(residuals), 3e-4)

    def test_wronskian_residual_meets_first_pass_threshold(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        solution = solve_radial_mode(
            Sector.ODD,
            2,
            0.5,
            bg,
            BoundaryConfig(r_in_eps=1e-5, r_out=80.0, rtol=1e-10, atol=1e-12),
        )

        self.assertLess(solution.diagnostics.wronskian_residual, 1e-7)

    def test_wronskian_residual_does_not_worsen_with_tighter_tolerances(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        loose = solve_radial_mode(
            Sector.EVEN,
            2,
            0.5,
            bg,
            BoundaryConfig(r_in_eps=1e-5, r_out=80.0, rtol=1e-8, atol=1e-10),
        )
        tight = solve_radial_mode(
            Sector.EVEN,
            2,
            0.5,
            bg,
            BoundaryConfig(r_in_eps=1e-5, r_out=80.0, rtol=1e-10, atol=1e-12),
        )

        self.assertLessEqual(
            tight.diagnostics.wronskian_residual,
            1.05 * loose.diagnostics.wronskian_residual,
        )

    def test_high_ell_radial_wronskian_diagnostic_remains_stable(self) -> None:
        cases = (
            (Sector.ODD, 8, 0.5),
            (Sector.EVEN, 8, 0.5),
            (Sector.ODD, 12, 0.5),
            (Sector.EVEN, 12, 0.5),
            (Sector.ODD, 6, 0.2),
            (Sector.EVEN, 6, 0.2),
        )

        for sector, ell, k in cases:
            with self.subTest(sector=sector.value, ell=ell, k=k):
                diagnostic = _mode_diagnostic(sector, ell=ell, k=k, r_out=120.0)

                self.assertLess(
                    diagnostic.wronskian_residual,
                    1e-7,
                    msg=f"high-ell radial diagnostic drifted: {diagnostic}",
                )
                self.assertLess(
                    diagnostic.flux_residual,
                    1e-7,
                    msg=f"high-ell flux diagnostic drifted: {diagnostic}",
                )
                self.assertLess(diagnostic.boundary_residual, 1e-8)
                self.assertEqual(diagnostic.solver, "bvp_unit_infinity")
                self.assertGreater(diagnostic.barrier_action, 8.0)
                self.assertLess(diagnostic.abs_A_in, 1.0 + 1e-8)
                self.assertGreater(diagnostic.abs_A_in, 1.0 - 1e-8)
                self.assertLess(diagnostic.abs_A_out, 1.0 + 1e-8)
                self.assertTrue(np.isfinite(diagnostic.max_abs_psi))
                self.assertLess(diagnostic.max_abs_psi, 10.0)
                self.assertTrue(np.isfinite(diagnostic.match_condition_number))
                self.assertLess(diagnostic.match_condition_number, 10.0)

    def test_ell_twelve_radial_solution_is_finite_with_small_boundary_residual(self) -> None:
        for sector in (Sector.ODD, Sector.EVEN):
            with self.subTest(sector=sector.value):
                diagnostic = _mode_diagnostic(sector, ell=12, k=0.5, r_out=120.0)

                self.assertTrue(np.isfinite(diagnostic.max_abs_psi))
                self.assertLess(diagnostic.max_abs_psi, 10.0)
                self.assertLess(diagnostic.boundary_residual, 1e-8)
                self.assertLess(diagnostic.wronskian_residual, 1e-5)

    def test_transition_mode_records_structured_radial_warning(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        solution = solve_radial_mode(
            Sector.EVEN,
            3,
            0.2,
            bg,
            BoundaryConfig(r_in_eps=1e-6, r_out=120.0, rtol=1e-10, atol=1e-12),
        )

        diagnostics = solution.diagnostics
        self.assertGreater(diagnostics.raw_wronskian_residual, 1e-7)
        self.assertEqual(diagnostics.wronskian_residual, diagnostics.raw_wronskian_residual)
        self.assertLess(diagnostics.flux_residual, 1e-7)
        self.assertLess(diagnostics.boundary_residual, 1e-8)
        self.assertGreater(diagnostics.expected_flux_scale, np.sqrt(np.finfo(float).eps))

        self.assertEqual(len(diagnostics.warnings), 1)
        warning = diagnostics.warnings[0]
        self.assertEqual(warning.code, "transition_raw_wronskian_warning")
        self.assertEqual(warning.severity, "warning")
        self.assertEqual(warning.sector, "even")
        self.assertEqual(warning.ell, 3)
        self.assertEqual(warning.solver, "bvp_unit_infinity")
        self.assertEqual(
            warning.raw_wronskian_residual,
            diagnostics.raw_wronskian_residual,
        )
        self.assertEqual(
            warning.effective_wronskian_residual,
            diagnostics.wronskian_residual,
        )
        json.dumps(warning.to_metadata())

    def test_healthy_high_barrier_modes_do_not_emit_radial_warnings(self) -> None:
        bg = SchwarzschildBackground(M=1.0)

        for sector in (Sector.ODD, Sector.EVEN):
            with self.subTest(sector=sector.value):
                solution = solve_radial_mode(
                    sector,
                    6,
                    0.2,
                    bg,
                    BoundaryConfig(r_in_eps=1e-6, r_out=120.0, rtol=1e-10, atol=1e-12),
                )

                self.assertLess(solution.diagnostics.wronskian_residual, 1e-7)
                self.assertLess(solution.diagnostics.flux_residual, 1e-7)
                self.assertEqual(solution.diagnostics.warnings, ())

    def test_k1p5_long_domain_transition_modes_survive_bvp_mesh_failure(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        config = BoundaryConfig(
            r_in_eps=1e-6,
            r_out=300.0,
            rtol=1e-10,
            atol=1e-12,
        )

        for sector in (Sector.ODD, Sector.EVEN):
            with self.subTest(sector=sector.value):
                solution = solve_radial_mode(sector, 10, 1.5, bg, config)
                diagnostics = solution.diagnostics

                self.assertEqual(diagnostics.solver, "bidirectional_match")
                self.assertGreater(diagnostics.barrier_action, 8.0)
                self.assertLess(diagnostics.wronskian_residual, 1e-7)
                self.assertLess(diagnostics.flux_residual, 1e-7)
                self.assertLess(diagnostics.boundary_residual, 1e-8)
                self.assertLess(abs(solution.A_in - 1.0), 1e-8)
                self.assertTrue(np.all(np.isfinite(solution.psi)))
                self.assertTrue(np.all(np.isfinite(solution.dpsi_dr)))
                self.assertLess(float(np.max(np.abs(solution.psi))), 10.0)

    def test_extreme_evanescent_tail_records_structured_suppression(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        config = BoundaryConfig(
            r_in_eps=1e-6,
            r_out=300.0,
            rtol=1e-10,
            atol=1e-12,
        )

        solution = solve_radial_mode(Sector.ODD, 153, 2.0, bg, config)
        diagnostics = solution.diagnostics

        self.assertEqual(diagnostics.solver, "evanescent_tail_suppressed")
        self.assertGreater(diagnostics.barrier_action, 700.0)
        self.assertLess(diagnostics.wronskian_residual, 1e-20)
        self.assertLess(diagnostics.flux_residual, 1e-20)
        self.assertLess(abs(solution.A_in - 1.0), 1e-12)
        self.assertGreater(solution.r_grid[-1], np.sqrt(30.0**2 + 30.0**2))
        self.assertEqual(solution.psi_at(np.sqrt(30.0**2 + 30.0**2)), 0.0j)

        self.assertEqual(len(diagnostics.warnings), 1)
        warning = diagnostics.warnings[0]
        self.assertEqual(warning.code, "evanescent_tail_suppressed")
        self.assertEqual(warning.severity, "warning")
        self.assertEqual(warning.sector, "odd")
        self.assertEqual(warning.ell, 153)
        self.assertEqual(warning.solver, "evanescent_tail_suppressed")
        self.assertLess(warning.flux_residual, 1e-20)
        json.dumps(warning.to_metadata())

    def test_extreme_evanescent_tail_required_eval_radius_fails_closed(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        config = BoundaryConfig(
            r_in_eps=1e-6,
            r_out=300.0,
            rtol=1e-10,
            atol=1e-12,
            required_eval_radius=60.0,
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "evanescent_tail_required_radius_uncovered",
        ) as raised:
            solve_radial_mode(Sector.ODD, 153, 2.0, bg, config)

        message = str(raised.exception)
        metadata = json.loads(message.split("metadata=", 1)[1])
        self.assertEqual(metadata["code"], "evanescent_tail_required_radius_uncovered")
        self.assertEqual(metadata["sector"], "odd")
        self.assertEqual(metadata["ell"], 153)
        self.assertEqual(metadata["required_eval_radius"], 60.0)
        self.assertFalse(metadata["required_eval_radius_covered"])
        self.assertLess(metadata["valid_until_r"], 60.0)
        json.dumps(metadata)

    def test_km4_tablei_transition_linear_algebra_failure_fails_closed(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        config = BoundaryConfig(
            r_in_eps=1e-6,
            r_out=300.0,
            rtol=1e-10,
            atol=1e-12,
            required_eval_radius=39.051248,
        )

        for sector in (Sector.ODD, Sector.EVEN):
            with self.subTest(sector=sector.value):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "evanescent_tail_required_radius_uncovered",
                ) as raised:
                    solve_radial_mode(sector, 177, 4.0, bg, config)

                message = str(raised.exception)
                metadata = json.loads(message.split("metadata=", 1)[1])
                self.assertEqual(
                    metadata["code"],
                    "evanescent_tail_required_radius_uncovered",
                )
                self.assertEqual(metadata["sector"], sector.value)
                self.assertEqual(metadata["ell"], 177)
                self.assertEqual(metadata["k"], 4.0)
                self.assertEqual(metadata["required_eval_radius"], 39.051248)
                self.assertFalse(metadata["required_eval_radius_covered"])
                self.assertLess(metadata["valid_until_r"], 39.051248)
                self.assertIn("bidirectional", metadata["fallback_failure_message"])
                json.dumps(metadata)

    def test_review_grid_solver_failure_at_required_radius_fails_closed(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        required_radius = float(np.sqrt(20.0**2 + 30.0**2))
        config = BoundaryConfig(
            r_in_eps=1e-6,
            r_out=300.0,
            rtol=1e-10,
            atol=1e-12,
            required_eval_radius=required_radius,
        )

        for sector in (Sector.ODD, Sector.EVEN):
            with self.subTest(sector=sector.value):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "evanescent_tail_required_radius_solver_failed",
                ) as raised:
                    solve_radial_mode(sector, 160, 2.5, bg, config)

                message = str(raised.exception)
                metadata = json.loads(message.split("metadata=", 1)[1])
                self.assertEqual(
                    metadata["code"],
                    "evanescent_tail_required_radius_solver_failed",
                )
                self.assertEqual(metadata["sector"], sector.value)
                self.assertEqual(metadata["ell"], 160)
                self.assertEqual(metadata["k"], 2.5)
                self.assertEqual(metadata["required_eval_radius"], required_radius)
                self.assertTrue(metadata["required_eval_radius_covered"])
                self.assertGreater(metadata["valid_until_r"], required_radius)
                self.assertIn("bidirectional", metadata["fallback_failure_message"])
                json.dumps(metadata)

    def test_delta0p1_risk_pilot_transition_recovers_only_inside_exact_envelope(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        required_radius = float(np.sqrt(15.0**2 + 30.0**2))
        config = BoundaryConfig(
            r_in_eps=1e-6,
            r_out=300.0,
            rtol=1e-10,
            atol=1e-12,
            required_eval_radius=required_radius,
            experimental_required_radius_oracle=(
                "q018_tablei_delta0p1_risk_pilot_transition"
            ),
        )

        for sector in (Sector.ODD, Sector.EVEN):
            with self.subTest(sector=sector.value):
                solution = solve_radial_mode(sector, 164, 2.8, bg, config)
                self.assertEqual(
                    solution.diagnostics.solver,
                    "q018_tablei_delta0p1_risk_pilot_transition_oracle",
                )
                self.assertEqual(solution.valid_until_r, required_radius)
                self.assertEqual(
                    solution.diagnostics.warnings[0].code,
                    "q018_tablei_delta0p1_risk_pilot_transition_oracle_used",
                )

    def test_targeted_adaptive_adapter_rejects_wrong_frequency_fail_closed(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        config = BoundaryConfig(
            r_in_eps=1e-6,
            r_out=300.0,
            rtol=1e-10,
            atol=1e-12,
            required_eval_radius=30.0,
            experimental_required_radius_oracle=(
                "q018_tablei_targeted_adaptive_transition"
            ),
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "q018_experimental_oracle_out_of_envelope",
        ):
            solve_radial_mode(Sector.ODD, 2, 0.36, bg, config)

    def test_further_local_adapter_recovers_only_inside_literal_envelope(self) -> None:
        bg = SchwarzschildBackground(M=1.0)
        required_radius = 30.0
        config = BoundaryConfig(
            r_in_eps=1e-6,
            r_out=300.0,
            rtol=1e-10,
            atol=1e-12,
            required_eval_radius=required_radius,
            experimental_required_radius_oracle=(
                "q018_tablei_further_local_transition"
            ),
        )

        for sector in (Sector.ODD, Sector.EVEN):
            with self.subTest(sector=sector.value):
                solution = solve_radial_mode(sector, 163, 2.7625, bg, config)
                self.assertEqual(
                    solution.diagnostics.solver,
                    "q018_tablei_further_local_transition_oracle",
                )
                self.assertEqual(solution.valid_until_r, required_radius)
                self.assertEqual(
                    solution.diagnostics.warnings[0].code,
                    "q018_tablei_further_local_transition_oracle_used",
                )

    def test_further_local_adapter_rejects_every_wrong_contract_field(self) -> None:
        oracle = "q018_tablei_further_local_transition"
        base = {
            "r_in_eps": 1e-6,
            "r_out": 300.0,
            "rtol": 1e-10,
            "atol": 1e-12,
            "required_eval_radius": 30.0,
            "experimental_required_radius_oracle": oracle,
        }
        cases = (
            (SchwarzschildBackground(M=1.1), 163, 2.7625, base),
            (SchwarzschildBackground(M=1.0), 163, 2.7626, base),
            (
                SchwarzschildBackground(M=1.0),
                163,
                2.7625,
                {**base, "required_eval_radius": 30.000000000000004},
            ),
            (SchwarzschildBackground(M=1.0), 163, 2.7625, {**base, "r_out": 301.0}),
            (SchwarzschildBackground(M=1.0), 163, 2.7625, {**base, "r_in_eps": 1e-5}),
            (SchwarzschildBackground(M=1.0), 163, 2.7625, {**base, "rtol": 1e-9}),
            (SchwarzschildBackground(M=1.0), 163, 2.7625, {**base, "atol": 1e-11}),
        )
        for background, ell, k, values in cases:
            with self.subTest(ell=ell, k=k, values=values):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "q018_experimental_oracle_out_of_envelope",
                ):
                    solve_radial_mode(
                        Sector.ODD,
                        ell,
                        k,
                        background,
                        BoundaryConfig(**values),
                    )

        with self.assertRaisesRegex(
            RuntimeError,
            "q018_experimental_oracle_out_of_envelope",
        ):
            radial_solver._validate_q018_further_local_oracle_envelope(
                sector=Sector.ODD,
                ell=182,
                k=2.7625,
                background=SchwarzschildBackground(M=1.0),
                config=BoundaryConfig(**base),
                r_out=300.0,
                barrier_action=0.0,
            )


def _mode_diagnostic(sector: Sector, ell: int, k: float, r_out: float) -> ModeDiagnostic:
    bg = SchwarzschildBackground(M=1.0)
    solution = solve_radial_mode(
        sector,
        ell,
        k,
        bg,
        BoundaryConfig(r_in_eps=1e-6, r_out=r_out, rtol=1e-10, atol=1e-12),
    )
    wronskian = _wronskian_samples(solution)
    return ModeDiagnostic(
        sector=solution.sector.value,
        ell=solution.ell,
        k=solution.k,
        solver=solution.diagnostics.solver,
        barrier_action=solution.diagnostics.barrier_action,
        abs_A_in=abs(solution.A_in),
        abs_A_out=abs(solution.A_out),
        wronskian_near_horizon=complex(wronskian[0]),
        wronskian_mid_grid=complex(wronskian[len(wronskian) // 2]),
        wronskian_outer=complex(wronskian[-1]),
        wronskian_residual=solution.diagnostics.wronskian_residual,
        flux_residual=solution.diagnostics.flux_residual,
        boundary_residual=solution.diagnostics.boundary_residual,
        max_abs_psi=float(np.max(np.abs(solution.psi))),
        ode_n_steps=solution.diagnostics.ode_n_steps,
        match_condition_number=solution.diagnostics.match_condition_number,
    )


def _wronskian_samples(solution) -> np.ndarray:
    f = solution.background.f(solution.r_grid)
    return f * (
        np.conjugate(solution.psi) * solution.dpsi_dr
        - solution.psi * np.conjugate(solution.dpsi_dr)
    )


if __name__ == "__main__":
    unittest.main()
