from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import math

import numpy as np
import pytest

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.numerics import (
    BoundaryConfig,
    RadialDiagnostics,
    RadialDiagnosticWarning,
    RadialSolution,
)
from schwgw.perturbations import Sector
from schwgw.validation.phase6_radial_pilot import (
    PILOT_SCHEMA,
    RadialPilotContractError,
    attach_external_comparisons,
    backend_capabilities,
    run_mode_ladder,
    selected_pilot_modes,
    validate_pilot_evidence,
)


HASH = "a" * 64


def _fake_solver(
    sector: Sector,
    ell: int,
    k: float,
    background: SchwarzschildBackground,
    config: BoundaryConfig,
) -> RadialSolution:
    phase_offset = (
        config.r_in_eps
        + float(config.r_out or 0.0) * 1e-10
        + config.outer_series_order * 1e-10
        + config.rtol * 1e3
    )
    q018 = config.experimental_required_radius_oracle is not None
    low_ell_anchor = ell == 2 and k == 0.5 and not q018
    magnitude = math.sqrt(3.0) if low_ell_anchor else (1.0 if q018 else 0.8)
    A_in = (2.0 if low_ell_anchor else 1.0) + 0.0j
    A_out = magnitude * np.exp(1j * phase_offset)
    r_grid = np.array([2.1, 3.0])
    psi = np.exp(-1j * k * background.r_star(r_grid))
    dpsi_dr = (-1j * k / background.f(r_grid)) * psi
    horizon_scale = (
        0.0
        if q018 or low_ell_anchor
        else 2.0 * k * (abs(A_in) ** 2 - magnitude**2)
    )
    warnings = ()
    if q018:
        warnings = (
            RadialDiagnosticWarning(
                code="q018_required_radius_oracle_used",
                severity="warning",
                message="fake Q018 metadata witness",
                sector=sector.value,
                ell=ell,
                k=k,
                solver="q018_required_radius_oracle",
                barrier_action=700.0,
                raw_wronskian_residual=2e-10,
                effective_wronskian_residual=2e-10,
                flux_residual=3e-10,
                boundary_residual=1e-12,
                expected_flux_scale=0.0,
                match_condition_number=1.5,
                metadata={
                    "actual_precision_bits": 53,
                    "actual_decimal_digits": 15.95,
                    "requested_precision_dps": 80,
                },
            ),
        )
    diagnostics = RadialDiagnostics(
        boundary_residual=1e-12,
        wronskian_residual=2e-10,
        raw_wronskian_residual=2e-10,
        flux_residual=3e-10,
        expected_flux_scale=horizon_scale,
        ode_n_steps=2,
        ode_status="fake selected-pilot solve",
        r_in=2.1,
        r_out=float(config.r_out or 300.0),
        atol=config.atol,
        rtol=config.rtol,
        match_condition_number=1.5,
        solver="q018_required_radius_oracle" if q018 else "outward_shooting",
        warnings=warnings,
        outer_basis=config.outer_basis,
        outer_series_order=config.outer_series_order,
    )
    return RadialSolution(
        sector=sector,
        ell=ell,
        k=k,
        r_grid=r_grid,
        psi=psi,
        dpsi_dr=dpsi_dr,
        A_in=A_in,
        A_out=complex(A_out),
        phase_factor=complex(-A_out / (((-1) ** ell) * A_in)),
        phase_shift=0.0j,
        diagnostics=diagnostics,
        background=background,
        valid_until_r=3.0,
    )


def _provenance() -> dict[str, dict[str, str]]:
    return {
        "scipy_source": {"radial": HASH},
        "scipy_dependencies": {"scipy": HASH},
        "common_inputs": {"config": HASH},
        "mst_source": {"mst": HASH},
        "mpmath_dependencies": {"mpmath": HASH},
        "bhpt_source": {"bhpt": HASH},
        "bhpt_dependencies": {"wolfram": HASH},
        "bhpt_inputs": {"input": HASH},
        "mpmath_ode_candidate_source": {"candidate": HASH},
    }


def _payload() -> dict:
    records = []
    for mode in selected_pilot_modes():
        record = run_mode_ladder(mode, solver=_fake_solver)
        baseline = record["baseline"]["phase_factor"]
        value = complex(baseline["real"], baseline["imag"])
        attach_external_comparisons(
            record,
            bhpt_record=None,
            mst_odd=value,
            mst_even=value,
            mst_recurrence_residual=1e-50,
        )
        records.append(record)
    return {
        "schema_version": PILOT_SCHEMA,
        "scope": "selected_mode_development_pilot",
        "overall_status": "YELLOW_PARTIAL_SELECTED_MODE_EVIDENCE",
        "global_green_permitted": False,
        "pilot_domain": {
            "covered_key_count": 7,
            "production_deduplicated_key_count": 16048,
            "production_missing_key_count": 16041,
            "full_v1_domain_complete": False,
        },
        "backend_capabilities": [
            item.to_metadata()
            for item in backend_capabilities(
                mpmath_version="1.4.1", provenance=_provenance()
            )
        ],
        "modes": records,
        "source_identities": {"pilot": HASH},
        "limitations": ["selected pilot only"],
    }


def test_selected_mode_inventory_is_bounded_and_spans_required_regimes() -> None:
    modes = selected_pilot_modes()
    assert len(modes) == 7
    assert {mode.sector for mode in modes} == {Sector.ODD, Sector.EVEN}
    assert {mode.regime for mode in modes} == {
        "low_ell_absorptive_anchor",
        "ordinary_oscillatory",
        "near_turning_ell_equals_k_r_eval",
        "q018_high_barrier_anchor",
    }
    turning = [mode for mode in modes if mode.regime.startswith("near_turning")]
    assert all(mode.ell == mode.kM * mode.r_eval for mode in turning)


def test_signed_flux_is_direct_and_q018_never_gets_physical_flux_pass() -> None:
    ordinary = run_mode_ladder(selected_pilot_modes()[0], solver=_fake_solver)
    flux = ordinary["baseline"]["flux"]
    assert flux["F_inf_in_signed"] < 0.0
    assert flux["F_inf_out_signed"] > 0.0
    assert flux["F_H_signed"] < 0.0
    assert flux["horizon_flux_inferred_from_one_minus_R"] is False
    assert flux["internal_accounting_only"] is True
    assert flux["independently_validated"] is False
    assert flux["absolute_balance_residual"] == pytest.approx(0.0, abs=2e-15)
    assert set(flux["signed_wronskian_inner"]) == {"real", "imag"}
    assert ordinary["layers"]["internal_flux_wronskian"][
        "physical_flux_status"
    ] == "PASS_INTERNAL_ACCOUNTING_ONLY"

    q018 = run_mode_ladder(selected_pilot_modes()[-1], solver=_fake_solver)
    q018_flux = q018["baseline"]["flux"]
    assert q018_flux["F_H_signed"] is None
    assert q018_flux["relative_balance_residual"] is None
    assert q018["layers"]["internal_flux_wronskian"]["physical_flux_status"].startswith(
        "NOT_ASSESSED"
    )
    precision = q018["baseline"]["diagnostics"]["q018_precision_truth"]
    assert precision["actual_precision_bits"] == 53
    assert precision["actual_decimal_digits"] == 15.95
    assert precision["requested_precision_dps"] == 80
    assert "actual_precision_dps" not in precision


def test_outward_horizon_flux_uses_direct_inner_current_not_one_minus_r() -> None:
    def direct_current_solver(*args, **kwargs):
        solution = _fake_solver(*args, **kwargs)
        solution.A_in = 2.0 + 0.0j
        solution.A_out = complex(math.sqrt(3.0), 0.0)
        solution.phase_factor = -solution.A_out / (
            ((-1) ** solution.ell) * solution.A_in
        )
        solution.diagnostics = replace(
            solution.diagnostics,
            expected_flux_scale=0.0,
            solver="outward_shooting",
        )
        return solution

    record = run_mode_ladder(selected_pilot_modes()[0], solver=direct_current_solver)
    flux = record["baseline"]["flux"]
    assert flux["horizon_flux_source"] == (
        "direct_inner_current_from_horizon_normalized_solution"
    )
    assert flux["F_H_signed"] == pytest.approx(-1.0)
    assert flux["absolute_balance_residual"] == pytest.approx(0.0, abs=2e-15)
    assert flux["horizon_flux_inferred_from_one_minus_R"] is False
    assert record["layers"]["internal_flux_wronskian"][
        "physical_flux_status"
    ] == "PASS_INTERNAL_ACCOUNTING_ONLY"


def test_subresolution_horizon_flux_cannot_receive_physical_flux_pass() -> None:
    def subresolution_solver(*args, **kwargs):
        solution = _fake_solver(*args, **kwargs)
        solution.A_out = complex(np.exp(2e-8j))
        solution.phase_factor = -solution.A_out / (((-1) ** solution.ell) * solution.A_in)
        solution.diagnostics = replace(
            solution.diagnostics,
            expected_flux_scale=1e-30,
        )
        return solution

    record = run_mode_ladder(
        selected_pilot_modes()[0], solver=subresolution_solver
    )
    flux = record["baseline"]["flux"]
    assert flux["F_H_signed"] is None
    assert flux["recorded_transmission_fraction"] < flux["float64_resolution_floor"]
    assert record["layers"]["internal_flux_wronskian"]["physical_flux_status"].startswith(
        "NOT_ASSESSED"
    )
    assert "Q018" not in record["layers"]["internal_flux_wronskian"][
        "physical_flux_status"
    ]


def test_ladder_bookkeeping_keeps_nodes_failures_and_forbids_partial_closure() -> None:
    record = run_mode_ladder(selected_pilot_modes()[0], solver=_fake_solver)
    ladder = record["layers"]["numerical_ladder"]
    assert ladder["full_phase6_ladder_complete"] is False
    assert ladder["axes"]["r_out"]["declared_nodes"] == [
        300.0,
        600.0,
        1200.0,
        1800.0,
        2400.0,
    ]
    assert ladder["axes"]["r_out"]["missing_nodes"] == [1800.0, 2400.0]
    assert ladder["axes"]["r_out"]["closure_permitted"] is False
    assert ladder["axes"]["r_out"]["final_pair"] is not None
    assert ladder["axes"]["r_out"]["extrapolation_model"].startswith("none")


def test_backend_capabilities_separate_precision_and_fail_closed() -> None:
    capabilities = {
        item.backend_id: item
        for item in backend_capabilities(
            mpmath_version="1.4.1", provenance=_provenance()
        )
    }
    scipy_backend = capabilities["scipy_float64_radial_ode"]
    assert scipy_backend.actual_precision_bits == 53
    assert scipy_backend.actual_working_dps is None
    assert scipy_backend.genuinely_independent is False
    assert capabilities["local_mpmath_mst"].actual_working_dps == 70
    assert capabilities["bhpt_direct_integration"].status == "OPEN"
    assert capabilities["independent_arbitrary_precision_ode"].blocker


def test_selected_key_mst_failure_is_recorded_without_independence_claim() -> None:
    record = run_mode_ladder(selected_pilot_modes()[0], solver=_fake_solver)
    attach_external_comparisons(
        record,
        bhpt_record=None,
        mst_odd=None,
        mst_even=None,
        mst_recurrence_residual=None,
        mst_blocker="RuntimeError: wrong renormalized-angular-momentum branch",
    )
    external = record["layers"]["external_algorithm"]
    assert external["diagnostic_comparison_status"] == (
        "EXTERNAL_BACKEND_UNAVAILABLE_FOR_SELECTED_KEY"
    )
    comparison = external["comparisons"][0]
    assert comparison["status"] == "OPEN_FOR_SELECTED_KEY"
    assert comparison["genuinely_independent_for_this_sector"] is False
    assert comparison["value"] is None


def test_evidence_validates_with_separate_open_uncertainties_and_no_green() -> None:
    payload = _payload()
    validate_pilot_evidence(payload)
    assert all(record["numerical_uncertainty"]["closed"] is False for record in payload["modes"])
    assert all(
        record["convention_uncertainty"]["closed"] is False
        for record in payload["modes"]
    )
    even = [record for record in payload["modes"] if record["mode"]["sector"] == "even"]
    assert all(
        record["layers"]["external_algorithm"]["even_independent_solve"] is False
        for record in even
    )

    overstated = deepcopy(payload)
    overstated["overall_status"] = "GREEN"
    with pytest.raises(RadialPilotContractError, match="cannot claim"):
        validate_pilot_evidence(overstated)


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (
            lambda payload: payload["modes"][0]["baseline"]["phase_factor"].update(
                real=math.nan
            ),
            "finite",
        ),
        (
            lambda payload: payload["modes"][0]["layers"]["numerical_ladder"][
                "axes"
            ]["r_out"].update(closure_permitted=True),
            "incomplete ladder",
        ),
        (
            lambda payload: payload["modes"][-1]["layers"][
                "internal_flux_wronskian"
            ].update(physical_flux_status="PASS_INTERNAL_ACCOUNTING_ONLY"),
            "Q018",
        ),
        (
            lambda payload: payload["modes"][1]["layers"]["external_algorithm"].update(
                even_independent_solve=True
            ),
            "even parity",
        ),
    ],
)
def test_evidence_rejects_schema_and_scientific_overstatement(mutator, message) -> None:
    payload = _payload()
    mutator(payload)
    with pytest.raises(RadialPilotContractError, match=message):
        validate_pilot_evidence(payload)
