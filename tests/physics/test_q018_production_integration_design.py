import json

import numpy as np
import pytest

import schwgw.numerics as public_numerics
import schwgw.numerics.radial_solver as radial_solver_module
from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
from schwgw.numerics import BoundaryConfig, RadialSolution, solve_radial_mode
import schwgw.numerics.experimental.q018_rescaled_oracle as q018_oracle_module
from schwgw.numerics.experimental.q018_rescaled_oracle import (
    RescaledOracleRequest,
    solve_q018_rescaled_oracle,
)
from schwgw.numerics.q018_delta0p1_risk_envelope import POINTS as RISK_POINTS
from schwgw.perturbations import Sector


Q018_R60_MATRIX = tuple(
    (sector, ell)
    for ell in (153, 156, 168, 180)
    for sector in (Sector.ODD, Sector.EVEN)
)

Q018_R60_CONTINUOUS_SUPPRESSED_MATRIX = tuple(
    (sector, ell)
    for ell in range(153, 181)
    for sector in (Sector.ODD, Sector.EVEN)
)

Q018_TABLEI_KM4_TRANSITION_MATRIX = tuple(
    (sector, ell)
    for ell in range(177, 241)
    for sector in (Sector.ODD, Sector.EVEN)
)

Q018_TABLEI_KM4_TRANSITION_ANCHORS = tuple(
    (sector, ell)
    for ell in (177, 208, 240)
    for sector in (Sector.ODD, Sector.EVEN)
)

Q018_REVIEW_GRID_TRANSITION_ANCHORS = (
    (Sector.ODD, 2.5, 160, "far_axis_x20_z30", float(np.sqrt(20.0**2 + 30.0**2))),
    (Sector.EVEN, 2.5, 160, "far_axis_x25_z30", float(np.sqrt(25.0**2 + 30.0**2))),
    (Sector.ODD, 3.0, 166, "near_axis_x0_z30", 30.0),
    (Sector.EVEN, 3.5, 172, "near_axis_x2_z30", float(np.sqrt(2.0**2 + 30.0**2))),
    (Sector.ODD, 3.75, 228, "far_axis_x25_z30", float(np.sqrt(25.0**2 + 30.0**2))),
    (Sector.EVEN, 4.0, 240, "far_axis_x25_z30", float(np.sqrt(25.0**2 + 30.0**2))),
)

Q018_DELTA0P1_RISK_FREQUENCIES = (0.4, 0.8, 0.9, 1.6, 1.7, 2.8, 2.9, 3.8, 3.9)
Q018_DELTA0P1_RISK_ORACLE = "q018_tablei_delta0p1_risk_pilot_transition"
Q018_DELTA0P1_LMAX = {
    0.4: (24, 36, 60, 84),
    0.8: (24, 36, 60, 84),
    0.9: (24, 36, 60, 84),
    1.6: (72, 96, 120, 144),
    1.7: (84, 108, 132, 156),
    2.8: (180, 204, 228, 252),
    2.9: (192, 216, 240, 264),
    3.8: (276, 300, 324, 348),
    3.9: (288, 312, 336, 360),
}
Q018_DELTA0P1_POINT_RADII = dict(RISK_POINTS)
Q018_DELTA0P1_RISK_TRANSITION_ANCHORS = (
    (Sector.ODD, 2.8, 164, "far_axis_x15_z30"),
    (Sector.EVEN, 2.9, 165, "near_axis_x0_z30"),
    (Sector.ODD, 3.8, 175, "near_axis_x0_z30"),
    (Sector.EVEN, 3.9, 176, "near_axis_x0_z30"),
)


def _r60_boundary_config(**overrides) -> BoundaryConfig:
    values = {
        "r_in_eps": 1e-6,
        "r_out": 300.0,
        "rtol": 1e-10,
        "atol": 1e-12,
        "required_eval_radius": 60.0,
    }
    values.update(overrides)
    return BoundaryConfig(**values)


def _tablei_km4_boundary_config(**overrides) -> BoundaryConfig:
    values = {
        "r_in_eps": 1e-6,
        "r_out": 300.0,
        "rtol": 1e-10,
        "atol": 1e-12,
        "required_eval_radius": 39.051248,
    }
    values.update(overrides)
    return BoundaryConfig(**values)


def _tablei_review_grid_boundary_config(
    required_eval_radius: float,
    **overrides,
) -> BoundaryConfig:
    values = {
        "r_in_eps": 1e-6,
        "r_out": 300.0,
        "rtol": 1e-10,
        "atol": 1e-12,
        "required_eval_radius": required_eval_radius,
    }
    values.update(overrides)
    return BoundaryConfig(**values)


def _tablei_review_grid_oracle_request(
    sector: Sector,
    k: float,
    ell: int,
    required_radius: float,
) -> RescaledOracleRequest:
    return RescaledOracleRequest(
        sector=sector,
        ell=ell,
        k=k,
        required_radius=required_radius,
        r_out=300.0,
        r_in_eps=1e-6,
        rtol=1e-10,
        atol=1e-12,
        precision_dps=80,
        method_hint="rescaled_log_amplitude",
    )


def _delta0p1_risk_boundary_config(
    required_eval_radius: float,
    **overrides,
) -> BoundaryConfig:
    return _tablei_review_grid_boundary_config(required_eval_radius, **overrides)


def _delta0p1_risk_oracle_request(
    sector: Sector,
    k: float,
    ell: int,
    required_radius: float,
) -> RescaledOracleRequest:
    return _tablei_review_grid_oracle_request(sector, k, ell, required_radius)


def test_delta0p1_risk_adapter_name_is_supported() -> None:
    background = SchwarzschildBackground(M=1.0)
    config = _tablei_review_grid_boundary_config(
        float(np.sqrt(25.0**2 + 30.0**2)),
        experimental_required_radius_oracle=Q018_DELTA0P1_RISK_ORACLE,
    )

    solution = solve_radial_mode(Sector.ODD, 190, 2.8, background, config)

    assert isinstance(solution, RadialSolution)


@pytest.mark.physics
@pytest.mark.parametrize(
    ("sector", "k", "ell", "point_id"),
    Q018_DELTA0P1_RISK_TRANSITION_ANCHORS,
)
def test_delta0p1_risk_adapter_returns_oracle_solution_on_each_transition_frequency(
    sector: Sector,
    k: float,
    ell: int,
    point_id: str,
) -> None:
    required_radius = Q018_DELTA0P1_POINT_RADII[point_id]
    background = SchwarzschildBackground(M=1.0)
    config = _delta0p1_risk_boundary_config(
        required_radius,
        experimental_required_radius_oracle=Q018_DELTA0P1_RISK_ORACLE,
    )

    solution = solve_radial_mode(sector, ell, k, background, config)

    assert isinstance(solution, RadialSolution)
    assert solution.sector is sector
    assert solution.ell == ell
    assert solution.k == k
    assert solution.valid_until_r == required_radius
    assert solution.diagnostics.solver == (
        "q018_tablei_delta0p1_risk_pilot_transition_oracle"
    )
    assert solution.diagnostics.ode_status == (
        "Q018 Delta0p1 risk-pilot transition opt-in oracle used"
    )
    assert len(solution.diagnostics.warnings) == 1
    metadata = solution.diagnostics.warnings[0].to_metadata()
    assert metadata["code"] == (
        "q018_tablei_delta0p1_risk_pilot_transition_oracle_used"
    )
    assert metadata["experimental_required_radius_oracle"] == Q018_DELTA0P1_RISK_ORACLE
    assert metadata["production_integration_review_id"] == "T4z/T7bv-pending"
    assert metadata["experimental_evidence"] == (
        "T4z complete measured Delta0p1 risk-pilot transition set"
    )
    assert metadata["review_grid_point_id"] == point_id
    assert metadata["required_eval_radius"] == required_radius
    assert metadata["outer_boundary_residual"] < 1e-8
    assert metadata["normalization_residual"] < 1e-8
    assert metadata["log_derivative_match_residual"] < 1e-7


@pytest.mark.parametrize(
    ("sector", "k", "ell", "point_id"),
    Q018_DELTA0P1_RISK_TRANSITION_ANCHORS,
)
def test_delta0p1_risk_adapter_matches_direct_oracle_on_transition_anchors(
    sector: Sector,
    k: float,
    ell: int,
    point_id: str,
) -> None:
    required_radius = Q018_DELTA0P1_POINT_RADII[point_id]
    background = SchwarzschildBackground(M=1.0)
    config = _delta0p1_risk_boundary_config(
        required_radius,
        experimental_required_radius_oracle=Q018_DELTA0P1_RISK_ORACLE,
    )

    solution = solve_radial_mode(sector, ell, k, background, config)
    oracle = solve_q018_rescaled_oracle(
        _delta0p1_risk_oracle_request(sector, k, ell, required_radius),
        background,
    )

    assert solution.A_in == pytest.approx(oracle.A_in, rel=0.0, abs=1e-12)
    assert solution.A_out == pytest.approx(oracle.A_out, rel=1e-12, abs=1e-18)
    assert solution.psi_at(required_radius) == pytest.approx(
        oracle.psi,
        rel=1e-12,
        abs=1e-24,
    )
    assert solution.dpsi_dr_at(required_radius) == pytest.approx(
        oracle.dpsi_dr,
        rel=1e-12,
        abs=1e-24,
    )


@pytest.mark.physics
@pytest.mark.parametrize("k", Q018_DELTA0P1_RISK_FREQUENCIES)
@pytest.mark.parametrize("sector", (Sector.ODD, Sector.EVEN))
def test_delta0p1_risk_opt_in_keeps_default_covered_modes_on_production_path(
    sector: Sector,
    k: float,
) -> None:
    required_radius = Q018_DELTA0P1_POINT_RADII["near_axis_x0_z30"]
    background = SchwarzschildBackground(M=1.0)
    config = _delta0p1_risk_boundary_config(
        required_radius,
        experimental_required_radius_oracle=Q018_DELTA0P1_RISK_ORACLE,
    )

    solution = solve_radial_mode(sector, 2, k, background, config)

    assert isinstance(solution, RadialSolution)
    assert solution.diagnostics.solver != (
        "q018_tablei_delta0p1_risk_pilot_transition_oracle"
    )
    assert all(
        warning.code != "q018_tablei_delta0p1_risk_pilot_transition_oracle_used"
        for warning in solution.diagnostics.warnings
    )


@pytest.mark.parametrize(
    ("background", "k", "required_radius", "config_overrides"),
    (
        (SchwarzschildBackground(M=1.01), 2.8, Q018_DELTA0P1_POINT_RADII["far_axis_x15_z30"], {}),
        (SchwarzschildBackground(M=1.0), 2.81, Q018_DELTA0P1_POINT_RADII["far_axis_x15_z30"], {}),
        (SchwarzschildBackground(M=1.0), 2.8, 36.1, {}),
        (SchwarzschildBackground(M=1.0), 2.8, Q018_DELTA0P1_POINT_RADII["far_axis_x15_z30"], {"r_out": 301.0}),
        (SchwarzschildBackground(M=1.0), 2.8, Q018_DELTA0P1_POINT_RADII["far_axis_x15_z30"], {"rtol": 1e-9}),
        (SchwarzschildBackground(M=1.0), 2.8, Q018_DELTA0P1_POINT_RADII["far_axis_x15_z30"], {"atol": 1e-11}),
    ),
)
def test_delta0p1_risk_adapter_rejects_out_of_envelope_global_axes(
    background: SchwarzschildBackground,
    k: float,
    required_radius: float,
    config_overrides: dict[str, float],
) -> None:
    config = _delta0p1_risk_boundary_config(
        required_radius,
        experimental_required_radius_oracle=Q018_DELTA0P1_RISK_ORACLE,
        **config_overrides,
    )

    with pytest.raises(
        RuntimeError,
        match="q018_experimental_oracle_out_of_envelope",
    ) as raised:
        solve_radial_mode(Sector.ODD, 164, k, background, config)

    metadata = json.loads(str(raised.value).split("metadata=", 1)[1])
    assert metadata["experimental_required_radius_oracle"] == Q018_DELTA0P1_RISK_ORACLE


@pytest.mark.parametrize(
    ("ell", "point_id"),
    ((164, "near_axis_x0_z30"), (163, "far_axis_x15_z30")),
)
def test_delta0p1_risk_adapter_rejects_unmeasured_ell_or_point_membership(
    ell: int,
    point_id: str,
) -> None:
    background = SchwarzschildBackground(M=1.0)
    config = _delta0p1_risk_boundary_config(Q018_DELTA0P1_POINT_RADII[point_id])

    with pytest.raises(
        RuntimeError,
        match="q018_experimental_oracle_out_of_envelope",
    ) as raised:
        radial_solver_module._validate_q018_delta0p1_risk_oracle_envelope(
            sector=Sector.ODD,
            ell=ell,
            k=2.8,
            background=background,
            config=config,
            r_out=300.0,
            barrier_action=800.0,
        )

    metadata = json.loads(str(raised.value).split("metadata=", 1)[1])
    assert "mode is outside measured transition set" in metadata["rejection_reasons"]


@pytest.mark.physics
@pytest.mark.parametrize("sector,ell", Q018_R60_CONTINUOUS_SUPPRESSED_MATRIX)
def test_q018_r60_default_production_path_remains_fail_closed(
    sector: Sector,
    ell: int,
) -> None:
    background = SchwarzschildBackground(M=1.0)

    with pytest.raises(
        RuntimeError,
        match="evanescent_tail_required_radius_uncovered",
    ) as raised:
        solve_radial_mode(sector, ell, 2.0, background, _r60_boundary_config())

    metadata = json.loads(str(raised.value).split("metadata=", 1)[1])
    assert metadata["code"] == "evanescent_tail_required_radius_uncovered"
    assert metadata["sector"] == sector.value
    assert metadata["ell"] == ell
    assert metadata["required_eval_radius"] == 60.0
    assert metadata["required_eval_radius_covered"] is False
    assert metadata["valid_until_r"] < 60.0


def _oracle_request(sector: Sector, ell: int) -> RescaledOracleRequest:
    return RescaledOracleRequest(
        sector=sector,
        ell=ell,
        k=2.0,
        required_radius=60.0,
        r_out=300.0,
        r_in_eps=1e-6,
        rtol=1e-10,
        atol=1e-12,
        precision_dps=80,
        method_hint="rescaled_log_amplitude",
    )


def _tablei_km4_oracle_request(sector: Sector, ell: int) -> RescaledOracleRequest:
    return RescaledOracleRequest(
        sector=sector,
        ell=ell,
        k=4.0,
        required_radius=39.051248,
        r_out=300.0,
        r_in_eps=1e-6,
        rtol=1e-10,
        atol=1e-12,
        precision_dps=80,
        method_hint="rescaled_log_amplitude",
    )


@pytest.mark.physics
@pytest.mark.parametrize("sector", (Sector.ODD, Sector.EVEN))
@pytest.mark.parametrize("ell", (2, 152))
def test_q018_run_level_opt_in_keeps_default_covered_modes_on_production_path(
    sector: Sector,
    ell: int,
) -> None:
    background = SchwarzschildBackground(M=1.0)
    config = _r60_boundary_config(experimental_required_radius_oracle="q018_riccati")

    solution = solve_radial_mode(sector, ell, 2.0, background, config)

    assert isinstance(solution, RadialSolution)
    assert solution.diagnostics.solver != "q018_required_radius_oracle"
    assert solution.r_grid[0] < 60.0 < solution.r_grid[-1]
    assert np.isfinite(solution.psi_at(60.0).real)
    assert np.isfinite(solution.psi_at(60.0).imag)
    assert np.isfinite(solution.dpsi_dr_at(60.0).real)
    assert np.isfinite(solution.dpsi_dr_at(60.0).imag)
    assert all(
        warning.code != "q018_required_radius_oracle_used"
        for warning in solution.diagnostics.warnings
    )


@pytest.mark.physics
@pytest.mark.parametrize("sector", (Sector.ODD, Sector.EVEN))
@pytest.mark.parametrize("ell", (176, 241))
def test_q018_tablei_km4_opt_in_keeps_default_covered_modes_on_production_path(
    sector: Sector,
    ell: int,
) -> None:
    background = SchwarzschildBackground(M=1.0)
    config = _tablei_km4_boundary_config(
        experimental_required_radius_oracle="q018_tablei_km4_transition"
    )

    solution = solve_radial_mode(sector, ell, 4.0, background, config)

    assert isinstance(solution, RadialSolution)
    assert solution.diagnostics.solver != "q018_tablei_km4_transition_oracle"
    assert solution.r_grid[0] < 39.051248
    if solution.valid_until_r is None:
        assert 39.051248 < solution.r_grid[-1]
    else:
        assert 39.051248 <= solution.valid_until_r
    assert np.isfinite(solution.psi_at(39.051248).real)
    assert np.isfinite(solution.psi_at(39.051248).imag)
    assert all(
        warning.code != "q018_tablei_km4_transition_oracle_used"
        for warning in solution.diagnostics.warnings
    )


@pytest.mark.physics
@pytest.mark.parametrize("sector,ell", Q018_R60_CONTINUOUS_SUPPRESSED_MATRIX)
def test_q018_reviewed_opt_in_returns_local_production_radial_solution(
    sector: Sector,
    ell: int,
) -> None:
    background = SchwarzschildBackground(M=1.0)
    config = _r60_boundary_config(experimental_required_radius_oracle="q018_riccati")

    solution = solve_radial_mode(sector, ell, 2.0, background, config)

    assert isinstance(solution, RadialSolution)
    assert solution.sector is sector
    assert solution.ell == ell
    assert solution.k == 2.0
    assert solution.valid_until_r == 60.0
    assert solution.diagnostics.solver == "q018_required_radius_oracle"
    assert solution.diagnostics.ode_status == "Q018 reviewed opt-in oracle used"
    assert abs(solution.A_in - 1.0) < 1e-8
    assert np.isfinite(solution.A_out.real)
    assert np.isfinite(solution.A_out.imag)
    assert np.isfinite(solution.psi_at(60.0).real)
    assert np.isfinite(solution.psi_at(60.0).imag)
    assert np.isfinite(solution.dpsi_dr_at(60.0).real)
    assert np.isfinite(solution.dpsi_dr_at(60.0).imag)
    with pytest.raises(ValueError, match="outside the solved domain"):
        solution.psi_at(60.0 + 1e-4)

    diagnostics = solution.diagnostics
    assert diagnostics.boundary_residual < 1e-8
    assert diagnostics.wronskian_residual < 1e-7
    assert diagnostics.flux_residual < 1e-7
    assert diagnostics.raw_wronskian_residual < 1e-7
    assert diagnostics.match_condition_number > 0.0
    assert diagnostics.barrier_action > 700.0
    assert len(diagnostics.warnings) == 1

    metadata = diagnostics.warnings[0].to_metadata()
    json.dumps(metadata)
    assert metadata["code"] == "q018_required_radius_oracle_used"
    assert metadata["experimental_required_radius_oracle"] == "q018_riccati"
    assert metadata["method"] == "riccati_log_derivative_match"
    assert metadata["experimental"] is True
    assert metadata["unit_incoming_at_infinity"] is True
    assert metadata["production_integration_review_id"] == "T4u/T7ap-pending"
    assert metadata["experimental_evidence"] == "T4u continuous ell=153..180 matrix"
    assert metadata["required_eval_radius"] == 60.0
    assert metadata["r_out"] == 300.0
    assert metadata["rtol"] == 1e-10
    assert metadata["atol"] == 1e-12
    assert metadata["finite_psi"] is True
    assert metadata["finite_dpsi_dr"] is True
    assert metadata["finite_A_in"] is True
    assert metadata["finite_A_out"] is True
    assert metadata["outer_boundary_residual"] < 1e-8
    assert metadata["normalization_residual"] < 1e-8
    assert metadata["log_derivative_match_residual"] < 1e-7


@pytest.mark.physics
@pytest.mark.parametrize("sector,ell", Q018_TABLEI_KM4_TRANSITION_MATRIX)
def test_q018_tablei_km4_opt_in_returns_local_production_radial_solution(
    sector: Sector,
    ell: int,
) -> None:
    background = SchwarzschildBackground(M=1.0)
    config = _tablei_km4_boundary_config(
        experimental_required_radius_oracle="q018_tablei_km4_transition"
    )

    solution = solve_radial_mode(sector, ell, 4.0, background, config)

    assert isinstance(solution, RadialSolution)
    assert solution.sector is sector
    assert solution.ell == ell
    assert solution.k == 4.0
    assert solution.valid_until_r == 39.051248
    assert solution.diagnostics.solver == "q018_tablei_km4_transition_oracle"
    assert (
        solution.diagnostics.ode_status
        == "Q018 kM=4 Table-I transition opt-in oracle used"
    )
    assert abs(solution.A_in - 1.0) < 1e-8
    assert np.isfinite(solution.A_out.real)
    assert np.isfinite(solution.A_out.imag)
    assert np.isfinite(solution.psi_at(39.051248).real)
    assert np.isfinite(solution.psi_at(39.051248).imag)
    assert np.isfinite(solution.dpsi_dr_at(39.051248).real)
    assert np.isfinite(solution.dpsi_dr_at(39.051248).imag)
    with pytest.raises(ValueError, match="outside the solved domain"):
        solution.psi_at(39.051248 + 1e-4)

    diagnostics = solution.diagnostics
    assert diagnostics.boundary_residual < 1e-8
    assert diagnostics.wronskian_residual < 1e-7
    assert diagnostics.flux_residual < 1e-7
    assert diagnostics.raw_wronskian_residual < 1e-7
    assert diagnostics.match_condition_number > 0.0
    assert diagnostics.barrier_action > 700.0
    assert len(diagnostics.warnings) == 1

    metadata = diagnostics.warnings[0].to_metadata()
    json.dumps(metadata)
    assert metadata["code"] == "q018_tablei_km4_transition_oracle_used"
    assert metadata["experimental_required_radius_oracle"] == (
        "q018_tablei_km4_transition"
    )
    assert metadata["method"] == "riccati_log_derivative_match"
    assert metadata["experimental"] is True
    assert metadata["unit_incoming_at_infinity"] is True
    assert metadata["production_integration_review_id"] == "T4x/T7bp-pending"
    assert metadata["experimental_evidence"] == (
        "T4x complete measured kM=4 Table-I transition set ell=177..240"
    )
    assert metadata["required_eval_radius"] == 39.051248
    assert metadata["r_out"] == 300.0
    assert metadata["rtol"] == 1e-10
    assert metadata["atol"] == 1e-12
    assert metadata["finite_psi"] is True
    assert metadata["finite_dpsi_dr"] is True
    assert metadata["finite_A_in"] is True
    assert metadata["finite_A_out"] is True
    assert metadata["outer_boundary_residual"] < 1e-8
    assert metadata["normalization_residual"] < 1e-8
    assert metadata["log_derivative_match_residual"] < 1e-7


@pytest.mark.parametrize("sector,ell", Q018_R60_MATRIX)
def test_q018_opt_in_matches_direct_experimental_oracle_on_review_anchor_modes(
    sector: Sector,
    ell: int,
) -> None:
    background = SchwarzschildBackground(M=1.0)
    config = _r60_boundary_config(experimental_required_radius_oracle="q018_riccati")

    solution = solve_radial_mode(sector, ell, 2.0, background, config)
    oracle = solve_q018_rescaled_oracle(_oracle_request(sector, ell), background)

    assert solution.A_in == pytest.approx(oracle.A_in, rel=0.0, abs=1e-12)
    assert solution.A_out == pytest.approx(oracle.A_out, rel=1e-12, abs=1e-18)
    assert solution.psi_at(60.0) == pytest.approx(oracle.psi, rel=1e-12, abs=1e-24)
    assert solution.dpsi_dr_at(60.0) == pytest.approx(
        oracle.dpsi_dr,
        rel=1e-12,
        abs=1e-24,
    )


@pytest.mark.parametrize("sector,ell", Q018_TABLEI_KM4_TRANSITION_ANCHORS)
def test_q018_tablei_km4_opt_in_matches_direct_experimental_oracle_on_anchor_modes(
    sector: Sector,
    ell: int,
) -> None:
    background = SchwarzschildBackground(M=1.0)
    config = _tablei_km4_boundary_config(
        experimental_required_radius_oracle="q018_tablei_km4_transition"
    )

    solution = solve_radial_mode(sector, ell, 4.0, background, config)
    oracle = solve_q018_rescaled_oracle(
        _tablei_km4_oracle_request(sector, ell),
        background,
    )

    assert solution.A_in == pytest.approx(oracle.A_in, rel=0.0, abs=1e-12)
    assert solution.A_out == pytest.approx(oracle.A_out, rel=1e-12, abs=1e-18)
    assert solution.psi_at(39.051248) == pytest.approx(
        oracle.psi,
        rel=1e-12,
        abs=1e-24,
    )
    assert solution.dpsi_dr_at(39.051248) == pytest.approx(
        oracle.dpsi_dr,
        rel=1e-12,
        abs=1e-24,
    )


@pytest.mark.physics
@pytest.mark.parametrize("sector", (Sector.ODD, Sector.EVEN))
@pytest.mark.parametrize(("ell", "k"), ((159, 2.5), (241, 4.0)))
def test_q018_review_grid_opt_in_keeps_default_covered_modes_on_production_path(
    sector: Sector,
    ell: int,
    k: float,
) -> None:
    required_radius = float(np.sqrt(25.0**2 + 30.0**2))
    background = SchwarzschildBackground(M=1.0)
    config = _tablei_review_grid_boundary_config(
        required_radius,
        experimental_required_radius_oracle="q018_tablei_review_grid_transition",
    )

    solution = solve_radial_mode(sector, ell, k, background, config)

    assert isinstance(solution, RadialSolution)
    assert solution.diagnostics.solver != "q018_tablei_review_grid_transition_oracle"
    if solution.valid_until_r is None:
        assert required_radius < solution.r_grid[-1]
    else:
        assert required_radius <= solution.valid_until_r
    assert np.isfinite(solution.psi_at(required_radius).real)
    assert np.isfinite(solution.dpsi_dr_at(required_radius).real)
    assert all(
        warning.code != "q018_tablei_review_grid_transition_oracle_used"
        for warning in solution.diagnostics.warnings
    )


@pytest.mark.physics
@pytest.mark.parametrize(
    ("sector", "k", "ell", "point_id", "required_radius"),
    Q018_REVIEW_GRID_TRANSITION_ANCHORS,
)
def test_q018_review_grid_opt_in_returns_local_production_radial_solution(
    sector: Sector,
    k: float,
    ell: int,
    point_id: str,
    required_radius: float,
) -> None:
    background = SchwarzschildBackground(M=1.0)
    config = _tablei_review_grid_boundary_config(
        required_radius,
        experimental_required_radius_oracle="q018_tablei_review_grid_transition",
    )

    solution = solve_radial_mode(sector, ell, k, background, config)

    assert isinstance(solution, RadialSolution)
    assert solution.sector is sector
    assert solution.ell == ell
    assert solution.k == k
    assert solution.valid_until_r == required_radius
    assert solution.diagnostics.solver == "q018_tablei_review_grid_transition_oracle"
    assert (
        solution.diagnostics.ode_status
        == "Q018 Fig.5/Fig.6 review-grid transition opt-in oracle used"
    )
    assert abs(solution.A_in - 1.0) < 1e-8
    assert np.isfinite(solution.A_out.real)
    assert np.isfinite(solution.A_out.imag)
    assert np.isfinite(solution.psi_at(required_radius).real)
    assert np.isfinite(solution.psi_at(required_radius).imag)
    assert np.isfinite(solution.dpsi_dr_at(required_radius).real)
    assert np.isfinite(solution.dpsi_dr_at(required_radius).imag)

    diagnostics = solution.diagnostics
    assert diagnostics.boundary_residual < 1e-8
    assert diagnostics.wronskian_residual < 1e-7
    assert diagnostics.flux_residual < 1e-7
    assert diagnostics.raw_wronskian_residual < 1e-7
    assert diagnostics.match_condition_number > 0.0
    assert len(diagnostics.warnings) == 1

    metadata = diagnostics.warnings[0].to_metadata()
    json.dumps(metadata)
    assert metadata["code"] == "q018_tablei_review_grid_transition_oracle_used"
    assert metadata["experimental_required_radius_oracle"] == (
        "q018_tablei_review_grid_transition"
    )
    assert metadata["production_integration_review_id"] == "T4y/T7bq-pending"
    assert metadata["experimental_evidence"] == (
        "T4y complete measured Fig.5/Fig.6 review-grid transition set"
    )
    assert metadata["review_grid_point_id"] == point_id
    assert metadata["required_eval_radius"] == required_radius
    assert metadata["finite_psi"] is True
    assert metadata["finite_dpsi_dr"] is True
    assert metadata["finite_A_in"] is True
    assert metadata["finite_A_out"] is True


@pytest.mark.parametrize(
    ("sector", "k", "ell", "point_id", "required_radius"),
    Q018_REVIEW_GRID_TRANSITION_ANCHORS[:3],
)
def test_q018_review_grid_opt_in_matches_direct_experimental_oracle_on_anchor_modes(
    sector: Sector,
    k: float,
    ell: int,
    point_id: str,
    required_radius: float,
) -> None:
    background = SchwarzschildBackground(M=1.0)
    config = _tablei_review_grid_boundary_config(
        required_radius,
        experimental_required_radius_oracle="q018_tablei_review_grid_transition",
    )

    solution = solve_radial_mode(sector, ell, k, background, config)
    oracle = solve_q018_rescaled_oracle(
        _tablei_review_grid_oracle_request(sector, k, ell, required_radius),
        background,
    )

    assert point_id
    assert solution.A_in == pytest.approx(oracle.A_in, rel=0.0, abs=1e-12)
    assert solution.A_out == pytest.approx(oracle.A_out, rel=1e-12, abs=1e-18)
    assert solution.psi_at(required_radius) == pytest.approx(
        oracle.psi,
        rel=1e-12,
        abs=1e-24,
    )
    assert solution.dpsi_dr_at(required_radius) == pytest.approx(
        oracle.dpsi_dr,
        rel=1e-12,
        abs=1e-24,
    )


def test_q018_default_path_does_not_call_experimental_oracle(monkeypatch) -> None:
    def fail_if_called(*args, **kwargs):
        raise AssertionError("default production path must not call Q018 oracle")

    monkeypatch.setattr(q018_oracle_module, "solve_q018_rescaled_oracle", fail_if_called)
    background = SchwarzschildBackground(M=1.0)

    with pytest.raises(
        RuntimeError,
        match="evanescent_tail_required_radius_uncovered",
    ):
        solve_radial_mode(Sector.ODD, 153, 2.0, background, _r60_boundary_config())


def test_q018_tablei_km4_default_path_does_not_call_experimental_oracle(
    monkeypatch,
) -> None:
    def fail_if_called(*args, **kwargs):
        raise AssertionError("default production path must not call Q018 oracle")

    monkeypatch.setattr(q018_oracle_module, "solve_q018_rescaled_oracle", fail_if_called)
    background = SchwarzschildBackground(M=1.0)

    with pytest.raises(
        RuntimeError,
        match="evanescent_tail_required_radius_uncovered",
    ):
        solve_radial_mode(
            Sector.ODD,
            177,
            4.0,
            background,
            _tablei_km4_boundary_config(),
        )


def test_q018_review_grid_default_path_does_not_call_experimental_oracle(
    monkeypatch,
) -> None:
    def fail_if_called(*args, **kwargs):
        raise AssertionError("default production path must not call Q018 oracle")

    monkeypatch.setattr(q018_oracle_module, "solve_q018_rescaled_oracle", fail_if_called)
    background = SchwarzschildBackground(M=1.0)

    with pytest.raises(
        RuntimeError,
        match="evanescent_tail_required_radius_solver_failed",
    ):
        solve_radial_mode(
            Sector.ODD,
            160,
            2.5,
            background,
            _tablei_review_grid_boundary_config(float(np.sqrt(20.0**2 + 30.0**2))),
        )


@pytest.mark.parametrize(
    ("sector", "ell", "k", "config"),
    (
        (
            Sector.ODD,
            181,
            2.0,
            _r60_boundary_config(experimental_required_radius_oracle="q018_riccati"),
        ),
        (
            Sector.ODD,
            153,
            2.0,
            _r60_boundary_config(
                experimental_required_radius_oracle="q018_riccati",
                required_eval_radius=80.0,
            ),
        ),
        (
            Sector.ODD,
            153,
            2.0,
            _r60_boundary_config(
                experimental_required_radius_oracle="q018_riccati",
                r_out=301.0,
            ),
        ),
        (
            Sector.ODD,
            181,
            4.0,
            _r60_boundary_config(experimental_required_radius_oracle="q018_riccati"),
        ),
    ),
)
def test_q018_reviewed_opt_in_rejects_out_of_envelope(
    sector: Sector,
    ell: int,
    k: float,
    config: BoundaryConfig,
) -> None:
    background = SchwarzschildBackground(M=1.0)

    with pytest.raises(
        RuntimeError,
        match="q018_experimental_oracle_out_of_envelope",
    ) as raised:
        solve_radial_mode(sector, ell, k, background, config)

    metadata = json.loads(str(raised.value).split("metadata=", 1)[1])
    assert metadata["code"] == "q018_experimental_oracle_out_of_envelope"
    assert metadata["experimental_required_radius_oracle"] == "q018_riccati"
    assert metadata["sector"] == sector.value
    assert metadata["ell"] == ell
    assert metadata["k"] == k
    assert metadata["allowed_ells"] == "153..180"


@pytest.mark.parametrize(
    ("background", "sector", "ell", "k", "config"),
    (
        (
            SchwarzschildBackground(M=1.01),
            Sector.ODD,
            177,
            4.0,
            _tablei_km4_boundary_config(
                experimental_required_radius_oracle="q018_tablei_km4_transition",
                required_eval_radius=60.0,
            ),
        ),
        (
            SchwarzschildBackground(M=1.0),
            Sector.ODD,
            177,
            4.001,
            _tablei_km4_boundary_config(
                experimental_required_radius_oracle="q018_tablei_km4_transition"
            ),
        ),
        (
            SchwarzschildBackground(M=1.0),
            Sector.ODD,
            177,
            4.0,
            _tablei_km4_boundary_config(
                experimental_required_radius_oracle="q018_tablei_km4_transition",
                required_eval_radius=39.151248,
            ),
        ),
        (
            SchwarzschildBackground(M=1.0),
            Sector.ODD,
            177,
            4.0,
            _tablei_km4_boundary_config(
                experimental_required_radius_oracle="q018_tablei_km4_transition",
                r_out=301.0,
            ),
        ),
        (
            SchwarzschildBackground(M=1.0),
            Sector.ODD,
            177,
            4.0,
            _tablei_km4_boundary_config(
                experimental_required_radius_oracle="q018_tablei_km4_transition",
                rtol=1e-9,
            ),
        ),
        (
            SchwarzschildBackground(M=1.0),
            Sector.ODD,
            177,
            4.0,
            _tablei_km4_boundary_config(
                experimental_required_radius_oracle="q018_tablei_km4_transition",
                atol=1e-11,
            ),
        ),
        (
            SchwarzschildBackground(M=1.0),
            Sector.ODD,
            241,
            4.0,
            _tablei_km4_boundary_config(
                experimental_required_radius_oracle="q018_tablei_km4_transition",
                required_eval_radius=60.0,
            ),
        ),
    ),
)
def test_q018_tablei_km4_opt_in_rejects_out_of_envelope(
    background: SchwarzschildBackground,
    sector: Sector,
    ell: int,
    k: float,
    config: BoundaryConfig,
) -> None:
    with pytest.raises(
        RuntimeError,
        match="q018_experimental_oracle_out_of_envelope",
    ) as raised:
        solve_radial_mode(sector, ell, k, background, config)

    metadata = json.loads(str(raised.value).split("metadata=", 1)[1])
    assert metadata["code"] == "q018_experimental_oracle_out_of_envelope"
    assert metadata["experimental_required_radius_oracle"] == (
        "q018_tablei_km4_transition"
    )
    assert metadata["sector"] == sector.value
    assert metadata["ell"] == ell
    assert metadata["k"] == k
    assert metadata["allowed_ells"] == "177..240"


@pytest.mark.parametrize(
    ("background", "sector", "ell", "k", "config"),
    (
        (
            SchwarzschildBackground(M=1.01),
            Sector.ODD,
            160,
            2.5,
            _tablei_review_grid_boundary_config(
                float(np.sqrt(20.0**2 + 30.0**2)),
                experimental_required_radius_oracle="q018_tablei_review_grid_transition",
            ),
        ),
        (
            SchwarzschildBackground(M=1.0),
            Sector.ODD,
            160,
            2.6,
            _tablei_review_grid_boundary_config(
                float(np.sqrt(20.0**2 + 30.0**2)),
                experimental_required_radius_oracle="q018_tablei_review_grid_transition",
            ),
        ),
        (
            SchwarzschildBackground(M=1.0),
            Sector.ODD,
            160,
            2.5,
            _tablei_review_grid_boundary_config(
                36.1,
                experimental_required_radius_oracle="q018_tablei_review_grid_transition",
            ),
        ),
        (
            SchwarzschildBackground(M=1.0),
            Sector.ODD,
            160,
            2.5,
            _tablei_review_grid_boundary_config(
                float(np.sqrt(20.0**2 + 30.0**2)),
                experimental_required_radius_oracle="q018_tablei_review_grid_transition",
                r_out=301.0,
            ),
        ),
        (
            SchwarzschildBackground(M=1.0),
            Sector.ODD,
            160,
            2.5,
            _tablei_review_grid_boundary_config(
                float(np.sqrt(20.0**2 + 30.0**2)),
                experimental_required_radius_oracle="q018_tablei_review_grid_transition",
                rtol=1e-9,
            ),
        ),
        (
            SchwarzschildBackground(M=1.0),
            Sector.ODD,
            160,
            2.5,
            _tablei_review_grid_boundary_config(
                float(np.sqrt(20.0**2 + 30.0**2)),
                experimental_required_radius_oracle="q018_tablei_review_grid_transition",
                atol=1e-11,
            ),
        ),
    ),
)
def test_q018_review_grid_opt_in_rejects_out_of_envelope(
    background: SchwarzschildBackground,
    sector: Sector,
    ell: int,
    k: float,
    config: BoundaryConfig,
) -> None:
    with pytest.raises(
        RuntimeError,
        match="q018_experimental_oracle_out_of_envelope",
    ) as raised:
        solve_radial_mode(sector, ell, k, background, config)

    metadata = json.loads(str(raised.value).split("metadata=", 1)[1])
    assert metadata["code"] == "q018_experimental_oracle_out_of_envelope"
    assert metadata["experimental_required_radius_oracle"] == (
        "q018_tablei_review_grid_transition"
    )
    assert metadata["sector"] == sector.value
    assert metadata["ell"] == ell
    assert metadata["k"] == k
    assert metadata["allowed_k"] == "2.5,2.75,3.0,3.25,3.5,3.75,4.0"


def test_q018_production_oracle_unknown_opt_in_fails_closed() -> None:
    background = SchwarzschildBackground(M=1.0)
    config = _r60_boundary_config(experimental_required_radius_oracle="unknown")

    with pytest.raises(ValueError, match="unsupported experimental_required_radius_oracle"):
        solve_radial_mode(Sector.ODD, 153, 2.0, background, config)


def test_q018_experimental_oracle_is_not_publicly_exported() -> None:
    assert not hasattr(public_numerics, "solve_q018_rescaled_oracle")
    assert "solve_q018_rescaled_oracle" not in public_numerics.__all__
