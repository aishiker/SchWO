"""Frozen paper-specific radial oracles retained for legacy evidence only.

This module isolates the historical Li/Table-I/Q018 envelopes from the generic
production radial solver.  The adapters remain opt-in, fail closed outside
their frozen envelopes, and never constitute Phase-6 scientific acceptance.
"""

from __future__ import annotations

import json
from typing import Any, Mapping

import numpy as np

from schwgw.backgrounds.base import StaticSphericalBackground
from schwgw.numerics.boundary_conditions import BoundaryConfig
from schwgw.numerics.q018_delta0p1_risk_envelope import (
    FREQUENCIES as _Q018_DELTA0P1_RISK_FREQUENCIES,
    POINTS as _Q018_DELTA0P1_RISK_POINTS,
    TRANSITION_SEGMENTS as _Q018_DELTA0P1_RISK_TRANSITION_SEGMENTS,
)
from schwgw.numerics.q018_further_local_envelope import (
    FREQUENCIES as _Q018_FURTHER_LOCAL_FREQUENCIES,
    POINTS as _Q018_FURTHER_LOCAL_POINTS,
    TRANSITION_SEGMENTS as _Q018_FURTHER_LOCAL_TRANSITION_SEGMENTS,
)
from schwgw.numerics.q018_tablei_literal_failed_child_envelope import (
    FREQUENCIES as _Q018_LITERAL_FAILED_CHILD_FREQUENCIES,
    POINTS as _Q018_LITERAL_FAILED_CHILD_POINTS,
    TRANSITION_SEGMENTS as _Q018_LITERAL_FAILED_CHILD_TRANSITION_SEGMENTS,
)
from schwgw.numerics.q018_tablei_another_bounded_local_envelope import (
    FREQUENCIES as _Q018_ANOTHER_BOUNDED_LOCAL_FREQUENCIES,
    POINTS as _Q018_ANOTHER_BOUNDED_LOCAL_POINTS,
    TRANSITION_SEGMENTS as _Q018_ANOTHER_BOUNDED_LOCAL_TRANSITION_SEGMENTS,
)
from schwgw.numerics.q018_targeted_adaptive_envelope import (
    FREQUENCIES as _Q018_TARGETED_ADAPTIVE_FREQUENCIES,
    POINTS as _Q018_TARGETED_ADAPTIVE_POINTS,
    TRANSITION_SEGMENTS as _Q018_TARGETED_ADAPTIVE_TRANSITION_SEGMENTS,
)
from schwgw.numerics.radial_solver import (
    RadialDiagnosticWarning,
    RadialDiagnostics,
    RadialSolution,
)
from schwgw.perturbations import Sector


_Q018_REQUIRED_RADIUS_ORACLE_NAME = "q018_riccati"
_Q018_REQUIRED_RADIUS_ORACLE_SOLVER = "q018_required_radius_oracle"
_Q018_TABLEI_KM4_TRANSITION_ORACLE_NAME = "q018_tablei_km4_transition"
_Q018_TABLEI_KM4_TRANSITION_ORACLE_SOLVER = (
    "q018_tablei_km4_transition_oracle"
)
_Q018_TABLEI_REVIEW_GRID_TRANSITION_ORACLE_NAME = (
    "q018_tablei_review_grid_transition"
)
_Q018_TABLEI_REVIEW_GRID_TRANSITION_ORACLE_SOLVER = (
    "q018_tablei_review_grid_transition_oracle"
)
_Q018_DELTA0P1_RISK_ORACLE_NAME = "q018_tablei_delta0p1_risk_pilot_transition"
_Q018_DELTA0P1_RISK_ORACLE_SOLVER = (
    "q018_tablei_delta0p1_risk_pilot_transition_oracle"
)
_Q018_TARGETED_ADAPTIVE_ORACLE_NAME = (
    "q018_tablei_targeted_adaptive_transition"
)
_Q018_TARGETED_ADAPTIVE_ORACLE_SOLVER = (
    "q018_tablei_targeted_adaptive_transition_oracle"
)
_Q018_FURTHER_LOCAL_ORACLE_NAME = "q018_tablei_further_local_transition"
_Q018_FURTHER_LOCAL_ORACLE_SOLVER = (
    "q018_tablei_further_local_transition_oracle"
)
_Q018_LITERAL_FAILED_CHILD_ORACLE_NAME = (
    "q018_tablei_literal_failed_child_transition"
)
_Q018_LITERAL_FAILED_CHILD_ORACLE_SOLVER = (
    "q018_tablei_literal_failed_child_transition_oracle"
)
_Q018_ANOTHER_BOUNDED_LOCAL_ORACLE_NAME = (
    "q018_tablei_another_bounded_local_transition"
)
_Q018_ANOTHER_BOUNDED_LOCAL_ORACLE_SOLVER = (
    "q018_tablei_another_bounded_local_transition_oracle"
)
_Q018_REQUIRED_RADIUS = 60.0
_Q018_REQUIRED_R_OUT = 300.0
_Q018_REQUIRED_K = 2.0
_Q018_REQUIRED_M = 1.0
_Q018_REQUIRED_R_IN_EPS = 1e-6
_Q018_REQUIRED_RTOL = 1e-10
_Q018_REQUIRED_ATOL = 1e-12
_Q018_ALLOWED_ELLS = tuple(range(153, 181))
_Q018_ALLOWED_ELLS_LABEL = "153..180"
_Q018_TABLEI_KM4_REQUIRED_RADIUS = 39.051248
_Q018_TABLEI_KM4_REQUIRED_R_OUT = 300.0
_Q018_TABLEI_KM4_REQUIRED_K = 4.0
_Q018_TABLEI_KM4_ALLOWED_ELLS = tuple(range(177, 241))
_Q018_TABLEI_KM4_ALLOWED_ELLS_LABEL = "177..240"
_Q018_TABLEI_REVIEW_GRID_REQUIRED_R_OUT = 300.0
_Q018_TABLEI_REVIEW_GRID_ALLOWED_KS = (2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0)
_Q018_TABLEI_REVIEW_GRID_ALLOWED_KS_LABEL = "2.5,2.75,3.0,3.25,3.5,3.75,4.0"
_Q018_TABLEI_REVIEW_GRID_POINTS = (
    ("near_axis_x0_z30", 30.0),
    ("near_axis_x1_z30", float(np.sqrt(1.0**2 + 30.0**2))),
    ("near_axis_x2_z30", float(np.sqrt(2.0**2 + 30.0**2))),
    ("near_axis_x3_z30", float(np.sqrt(3.0**2 + 30.0**2))),
    ("far_axis_x10_z30", float(np.sqrt(10.0**2 + 30.0**2))),
    ("far_axis_x15_z30", float(np.sqrt(15.0**2 + 30.0**2))),
    ("far_axis_x20_z30", float(np.sqrt(20.0**2 + 30.0**2))),
    ("far_axis_x25_z30", float(np.sqrt(25.0**2 + 30.0**2))),
)
_Q018_TABLEI_REVIEW_GRID_ALLOWED_RADII_LABEL = ",".join(
    f"{radius:.17g}" for _, radius in _Q018_TABLEI_REVIEW_GRID_POINTS
)
_Q018_REVIEW_ALL_TABLEI_POINTS = tuple(
    point_id for point_id, _ in _Q018_TABLEI_REVIEW_GRID_POINTS
)
_Q018_TABLEI_REVIEW_GRID_TRANSITION_SEGMENTS = {
    2.5: (
        (160, 160, _Q018_REVIEW_ALL_TABLEI_POINTS),
        (161, 169, ("far_axis_x25_z30",)),
    ),
    2.75: (
        (163, 163, _Q018_REVIEW_ALL_TABLEI_POINTS),
        (164, 171, ("far_axis_x20_z30", "far_axis_x25_z30")),
        (172, 181, ("far_axis_x25_z30",)),
    ),
    3.0: (
        (166, 166, _Q018_REVIEW_ALL_TABLEI_POINTS),
        (
            167,
            173,
            ("far_axis_x15_z30", "far_axis_x20_z30", "far_axis_x25_z30"),
        ),
        (174, 182, ("far_axis_x20_z30", "far_axis_x25_z30")),
        (183, 193, ("far_axis_x25_z30",)),
    ),
    3.25: (
        (169, 169, _Q018_REVIEW_ALL_TABLEI_POINTS),
        (
            170,
            175,
            (
                "far_axis_x10_z30",
                "far_axis_x15_z30",
                "far_axis_x20_z30",
                "far_axis_x25_z30",
            ),
        ),
        (
            176,
            183,
            ("far_axis_x15_z30", "far_axis_x20_z30", "far_axis_x25_z30"),
        ),
        (184, 193, ("far_axis_x20_z30", "far_axis_x25_z30")),
        (194, 205, ("far_axis_x25_z30",)),
    ),
    3.5: (
        (172, 178, _Q018_REVIEW_ALL_TABLEI_POINTS),
        (
            179,
            179,
            (
                "near_axis_x3_z30",
                "far_axis_x10_z30",
                "far_axis_x15_z30",
                "far_axis_x20_z30",
                "far_axis_x25_z30",
            ),
        ),
        (
            180,
            185,
            (
                "far_axis_x10_z30",
                "far_axis_x15_z30",
                "far_axis_x20_z30",
                "far_axis_x25_z30",
            ),
        ),
        (
            186,
            193,
            ("far_axis_x15_z30", "far_axis_x20_z30", "far_axis_x25_z30"),
        ),
        (194, 204, ("far_axis_x20_z30", "far_axis_x25_z30")),
        (205, 217, ("far_axis_x25_z30",)),
    ),
    3.75: (
        (175, 188, _Q018_REVIEW_ALL_TABLEI_POINTS),
        (
            189,
            195,
            (
                "far_axis_x10_z30",
                "far_axis_x15_z30",
                "far_axis_x20_z30",
                "far_axis_x25_z30",
            ),
        ),
        (
            196,
            204,
            ("far_axis_x15_z30", "far_axis_x20_z30", "far_axis_x25_z30"),
        ),
        (205, 215, ("far_axis_x20_z30", "far_axis_x25_z30")),
        (216, 228, ("far_axis_x25_z30",)),
    ),
    4.0: (
        (177, 197, _Q018_REVIEW_ALL_TABLEI_POINTS),
        (
            198,
            198,
            (
                "near_axis_x3_z30",
                "far_axis_x10_z30",
                "far_axis_x15_z30",
                "far_axis_x20_z30",
                "far_axis_x25_z30",
            ),
        ),
        (
            199,
            205,
            (
                "far_axis_x10_z30",
                "far_axis_x15_z30",
                "far_axis_x20_z30",
                "far_axis_x25_z30",
            ),
        ),
        (
            206,
            214,
            ("far_axis_x15_z30", "far_axis_x20_z30", "far_axis_x25_z30"),
        ),
        (215, 226, ("far_axis_x20_z30", "far_axis_x25_z30")),
        (227, 240, ("far_axis_x25_z30",)),
    ),
}
_Q018_LOCAL_GRID_STEP = 1e-6
_SUPPORTED_REQUIRED_RADIUS_ORACLE_NAMES = (
    _Q018_REQUIRED_RADIUS_ORACLE_NAME,
    _Q018_TABLEI_KM4_TRANSITION_ORACLE_NAME,
    _Q018_TABLEI_REVIEW_GRID_TRANSITION_ORACLE_NAME,
    _Q018_DELTA0P1_RISK_ORACLE_NAME,
    _Q018_TARGETED_ADAPTIVE_ORACLE_NAME,
    _Q018_FURTHER_LOCAL_ORACLE_NAME,
    _Q018_LITERAL_FAILED_CHILD_ORACLE_NAME,
    _Q018_ANOTHER_BOUNDED_LOCAL_ORACLE_NAME,
)


def is_legacy_oracle_supported(name: object) -> bool:
    """Return whether *name* selects one frozen legacy oracle envelope."""

    return name in _SUPPORTED_REQUIRED_RADIUS_ORACLE_NAMES


def validate_legacy_oracle_request(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
    r_out: float,
    barrier_action: float,
) -> None:
    """Validate legacy opt-in context before the generic solver is attempted."""

    oracle_name = config.experimental_required_radius_oracle
    if oracle_name not in _SUPPORTED_REQUIRED_RADIUS_ORACLE_NAMES:
        raise ValueError(
            "unsupported experimental_required_radius_oracle: "
            f"{oracle_name!r}"
        )
    validators = {
        _Q018_TABLEI_KM4_TRANSITION_ORACLE_NAME: (
            _validate_q018_tablei_km4_transition_oracle_envelope
        ),
        _Q018_TABLEI_REVIEW_GRID_TRANSITION_ORACLE_NAME: (
            _validate_q018_tablei_review_grid_transition_oracle_envelope
        ),
        _Q018_DELTA0P1_RISK_ORACLE_NAME: (
            _validate_q018_delta0p1_risk_oracle_envelope
        ),
        _Q018_TARGETED_ADAPTIVE_ORACLE_NAME: (
            _validate_q018_targeted_adaptive_oracle_envelope
        ),
        _Q018_FURTHER_LOCAL_ORACLE_NAME: (
            _validate_q018_further_local_oracle_envelope
        ),
        _Q018_LITERAL_FAILED_CHILD_ORACLE_NAME: (
            _validate_q018_literal_failed_child_oracle_envelope
        ),
        _Q018_ANOTHER_BOUNDED_LOCAL_ORACLE_NAME: (
            _validate_q018_another_bounded_local_oracle_envelope
        ),
    }
    validator = validators.get(oracle_name)
    if validator is not None:
        validator(
            sector=sector,
            ell=ell,
            k=k,
            background=background,
            config=config,
            r_out=r_out,
            barrier_action=barrier_action,
            validate_mode=False,
        )


def solve_legacy_required_radius_oracle(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
    r_in: float,
    r_out: float,
    barrier_action: float,
) -> RadialSolution:
    """Execute one frozen legacy oracle after the generic path fails."""

    return _solve_radial_mode_required_radius_oracle(
        sector=sector,
        ell=ell,
        k=k,
        background=background,
        config=config,
        r_in=r_in,
        r_out=r_out,
        barrier_action=barrier_action,
    )


def _solve_radial_mode_required_radius_oracle(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
    r_in: float,
    r_out: float,
    barrier_action: float,
) -> RadialSolution:
    oracle_name = config.experimental_required_radius_oracle
    if oracle_name not in _SUPPORTED_REQUIRED_RADIUS_ORACLE_NAMES:
        raise ValueError(
            "unsupported experimental_required_radius_oracle: "
            f"{oracle_name!r}"
        )
    if oracle_name == _Q018_REQUIRED_RADIUS_ORACLE_NAME:
        _validate_q018_required_radius_oracle_envelope(
            sector=sector,
            ell=ell,
            k=k,
            background=background,
            config=config,
            r_out=r_out,
            barrier_action=barrier_action,
        )
        solver_name = _Q018_REQUIRED_RADIUS_ORACLE_SOLVER
        warning_code = "q018_required_radius_oracle_used"
        ode_status = "Q018 reviewed opt-in oracle used"
        warning_message = (
            "Reviewed Q018 opt-in required-radius oracle used for the "
            "T4u continuous R60_K2 suppressed-mode envelope; the returned "
            "solution is only certified at required_eval_radius."
        )
        production_review_id = "T4u/T7ap-pending"
        experimental_evidence = "T4u continuous ell=153..180 matrix"
    elif oracle_name == _Q018_TABLEI_KM4_TRANSITION_ORACLE_NAME:
        _validate_q018_tablei_km4_transition_oracle_envelope(
            sector=sector,
            ell=ell,
            k=k,
            background=background,
            config=config,
            r_out=r_out,
            barrier_action=barrier_action,
        )
        solver_name = _Q018_TABLEI_KM4_TRANSITION_ORACLE_SOLVER
        warning_code = "q018_tablei_km4_transition_oracle_used"
        ode_status = "Q018 kM=4 Table-I transition opt-in oracle used"
        warning_message = (
            "Reviewed Q018 opt-in required-radius oracle used for the "
            "T4x kM=4 Table-I transition envelope; the returned solution "
            "is only certified at required_eval_radius."
        )
        production_review_id = "T4x/T7bp-pending"
        experimental_evidence = (
            "T4x complete measured kM=4 Table-I transition set ell=177..240"
        )
    elif oracle_name == _Q018_TABLEI_REVIEW_GRID_TRANSITION_ORACLE_NAME:
        _validate_q018_tablei_review_grid_transition_oracle_envelope(
            sector=sector,
            ell=ell,
            k=k,
            background=background,
            config=config,
            r_out=r_out,
            barrier_action=barrier_action,
        )
        solver_name = _Q018_TABLEI_REVIEW_GRID_TRANSITION_ORACLE_SOLVER
        warning_code = "q018_tablei_review_grid_transition_oracle_used"
        ode_status = "Q018 Fig.5/Fig.6 review-grid transition opt-in oracle used"
        warning_message = (
            "Reviewed Q018 opt-in required-radius oracle used for the "
            "T4y Fig.5/Fig.6 review-grid transition envelope; the returned "
            "solution is only certified at required_eval_radius."
        )
        production_review_id = "T4y/T7bq-pending"
        experimental_evidence = (
            "T4y complete measured Fig.5/Fig.6 review-grid transition set"
        )
    elif oracle_name == _Q018_DELTA0P1_RISK_ORACLE_NAME:
        _validate_q018_delta0p1_risk_oracle_envelope(
            sector=sector,
            ell=ell,
            k=k,
            background=background,
            config=config,
            r_out=r_out,
            barrier_action=barrier_action,
        )
        solver_name = _Q018_DELTA0P1_RISK_ORACLE_SOLVER
        warning_code = "q018_tablei_delta0p1_risk_pilot_transition_oracle_used"
        ode_status = "Q018 Delta0p1 risk-pilot transition opt-in oracle used"
        warning_message = (
            "Reviewed Q018 opt-in required-radius oracle used for the "
            "T4z Delta0p1 risk-pilot transition envelope; the returned "
            "solution is only certified at required_eval_radius."
        )
        production_review_id = "T4z/T7bv-pending"
        experimental_evidence = (
            "T4z complete measured Delta0p1 risk-pilot transition set"
        )
    elif oracle_name == _Q018_TARGETED_ADAPTIVE_ORACLE_NAME:
        _validate_q018_targeted_adaptive_oracle_envelope(
            sector=sector,
            ell=ell,
            k=k,
            background=background,
            config=config,
            r_out=r_out,
            barrier_action=barrier_action,
        )
        solver_name = _Q018_TARGETED_ADAPTIVE_ORACLE_SOLVER
        warning_code = "q018_tablei_targeted_adaptive_transition_oracle_used"
        ode_status = "Q018 targeted-adaptive transition opt-in oracle used"
        warning_message = (
            "Reviewed Q018 opt-in required-radius oracle used for the "
            "T4aa targeted-adaptive radial transition envelope; the returned "
            "solution is only certified at required_eval_radius."
        )
        production_review_id = "T4aa/T7by-pending"
        experimental_evidence = (
            "T4aa complete measured targeted-adaptive transition set"
        )
    elif oracle_name == _Q018_FURTHER_LOCAL_ORACLE_NAME:
        _validate_q018_further_local_oracle_envelope(
            sector=sector,
            ell=ell,
            k=k,
            background=background,
            config=config,
            r_out=r_out,
            barrier_action=barrier_action,
        )
        solver_name = _Q018_FURTHER_LOCAL_ORACLE_SOLVER
        warning_code = "q018_tablei_further_local_transition_oracle_used"
        ode_status = "Q018 further-local transition opt-in oracle used"
        warning_message = (
            "Reviewed Q018 opt-in required-radius oracle used for the "
            "T4ab further-local radial transition envelope; the returned "
            "solution is only certified at required_eval_radius."
        )
        production_review_id = "T4ab/T7ca-pending"
        experimental_evidence = (
            "T4ab complete measured further-local transition set"
        )
    elif oracle_name == _Q018_LITERAL_FAILED_CHILD_ORACLE_NAME:
        _validate_q018_literal_failed_child_oracle_envelope(
            sector=sector,
            ell=ell,
            k=k,
            background=background,
            config=config,
            r_out=r_out,
            barrier_action=barrier_action,
        )
        solver_name = _Q018_LITERAL_FAILED_CHILD_ORACLE_SOLVER
        warning_code = (
            "q018_tablei_literal_failed_child_transition_oracle_used"
        )
        ode_status = "Q018 literal failed-child transition opt-in oracle used"
        warning_message = (
            "Reviewed Q018 opt-in required-radius oracle used for the "
            "T4ac literal failed-child radial transition envelope; the returned "
            "solution is only certified at required_eval_radius."
        )
        production_review_id = "T4ac/T7cc-pending"
        experimental_evidence = (
            "T4ac complete measured literal failed-child transition set"
        )
    elif oracle_name == _Q018_ANOTHER_BOUNDED_LOCAL_ORACLE_NAME:
        _validate_q018_another_bounded_local_oracle_envelope(
            sector=sector,
            ell=ell,
            k=k,
            background=background,
            config=config,
            r_out=r_out,
            barrier_action=barrier_action,
        )
        solver_name = _Q018_ANOTHER_BOUNDED_LOCAL_ORACLE_SOLVER
        warning_code = (
            "q018_tablei_another_bounded_local_transition_oracle_used"
        )
        ode_status = "Q018 another-bounded-local transition opt-in oracle used"
        warning_message = (
            "Reviewed Q018 opt-in required-radius oracle used for the "
            "T4ad another-bounded-local radial transition envelope; the "
            "returned solution is only certified at required_eval_radius."
        )
        production_review_id = "T4ad/T7ce-pending"
        experimental_evidence = (
            "T4ad complete measured another-bounded-local transition set"
        )
    else:
        raise ValueError(
            "unsupported experimental_required_radius_oracle: "
            f"{oracle_name!r}"
        )

    from schwgw.numerics.experimental.q018_rescaled_oracle import (
        RescaledOracleRequest,
        solve_q018_rescaled_oracle,
    )

    required_radius = float(config.required_eval_radius)
    request = RescaledOracleRequest(
        sector=sector,
        ell=ell,
        k=float(k),
        required_radius=required_radius,
        r_out=float(r_out),
        r_in_eps=float(config.r_in_eps),
        rtol=float(config.rtol),
        atol=float(config.atol),
        precision_dps=80,
        method_hint="rescaled_log_amplitude",
    )
    result = solve_q018_rescaled_oracle(request, background)
    oracle_diagnostics = dict(result.diagnostics)

    outer_boundary_residual = _diagnostic_float(
        oracle_diagnostics,
        "outer_boundary_residual",
    )
    normalization_residual = _diagnostic_float(
        oracle_diagnostics,
        "normalization_residual",
    )
    log_derivative_match_residual = _diagnostic_float(
        oracle_diagnostics,
        "log_derivative_match_residual",
    )
    effective_residual = max(
        outer_boundary_residual,
        normalization_residual,
        log_derivative_match_residual,
    )
    _validate_q018_oracle_result(
        result=result,
        residual=effective_residual,
        outer_boundary_residual=outer_boundary_residual,
        normalization_residual=normalization_residual,
        log_derivative_match_residual=log_derivative_match_residual,
        sector=sector,
        ell=ell,
        k=k,
    )

    r_grid = np.array(
        [required_radius, required_radius + _Q018_LOCAL_GRID_STEP],
        dtype=float,
    )
    psi = np.array(
        [result.psi, result.psi + result.dpsi_dr * _Q018_LOCAL_GRID_STEP],
        dtype=complex,
    )
    dpsi_dr = np.array([result.dpsi_dr, result.dpsi_dr], dtype=complex)
    phase_factor = -result.A_out / (((-1) ** ell) * result.A_in)

    oracle_metadata: dict[str, str | int | float | bool] = {
        "experimental_required_radius_oracle": str(oracle_name),
        "method": str(oracle_diagnostics["method"]),
        "experimental": bool(oracle_diagnostics["experimental"]),
        "unit_incoming_at_infinity": bool(
            oracle_diagnostics["unit_incoming_at_infinity"]
        ),
        "production_integration_review_id": production_review_id,
        "experimental_evidence": experimental_evidence,
        "required_eval_radius": required_radius,
        "r_out": float(r_out),
        "r_in_eps": float(config.r_in_eps),
        "rtol": float(config.rtol),
        "atol": float(config.atol),
        "actual_precision_bits": int(oracle_diagnostics["actual_precision_bits"]),
        "actual_decimal_digits": float(
            oracle_diagnostics["actual_decimal_digits"]
        ),
        "requested_precision_dps": int(oracle_diagnostics["requested_precision_dps"]),
        "finite_psi": bool(oracle_diagnostics["finite_psi"]),
        "finite_dpsi_dr": bool(oracle_diagnostics["finite_dpsi_dr"]),
        "finite_A_in": bool(oracle_diagnostics["finite_A_in"]),
        "finite_A_out": bool(oracle_diagnostics["finite_A_out"]),
        "outer_boundary_residual": outer_boundary_residual,
        "normalization_residual": normalization_residual,
        "log_derivative_match_residual": log_derivative_match_residual,
        "riccati_steps": int(oracle_diagnostics["riccati_steps"]),
        "outward_steps": int(oracle_diagnostics["outward_steps"]),
        "runtime_seconds": _diagnostic_float(oracle_diagnostics, "runtime_seconds"),
        "valid_at_required_radius": bool(
            oracle_diagnostics["valid_at_required_radius"]
        ),
        "A_in_role": "outer exp(-i k r_star) incoming coefficient",
    }
    if oracle_name == _Q018_TABLEI_REVIEW_GRID_TRANSITION_ORACLE_NAME:
        point_id = _q018_tablei_review_grid_point_id(required_radius)
        if point_id is not None:
            oracle_metadata["review_grid_point_id"] = point_id
    elif oracle_name == _Q018_DELTA0P1_RISK_ORACLE_NAME:
        point_id = _q018_delta0p1_risk_point_id(required_radius)
        if point_id is not None:
            oracle_metadata["review_grid_point_id"] = point_id
    elif oracle_name == _Q018_TARGETED_ADAPTIVE_ORACLE_NAME:
        point_id = _q018_targeted_adaptive_point_id(required_radius)
        if point_id is not None:
            oracle_metadata["review_grid_point_id"] = point_id
    elif oracle_name == _Q018_FURTHER_LOCAL_ORACLE_NAME:
        point_id = _q018_further_local_point_id(required_radius)
        if point_id is not None:
            oracle_metadata["review_grid_point_id"] = point_id
    elif oracle_name == _Q018_LITERAL_FAILED_CHILD_ORACLE_NAME:
        point_id = _q018_literal_failed_child_point_id(required_radius)
        if point_id is not None:
            oracle_metadata["review_grid_point_id"] = point_id
    elif oracle_name == _Q018_ANOTHER_BOUNDED_LOCAL_ORACLE_NAME:
        point_id = _q018_another_bounded_local_point_id(required_radius)
        if point_id is not None:
            oracle_metadata["review_grid_point_id"] = point_id
    warning = RadialDiagnosticWarning(
        code=warning_code,
        severity="warning",
        message=warning_message,
        sector=sector.value,
        ell=ell,
        k=float(k),
        solver=solver_name,
        barrier_action=float(barrier_action),
        raw_wronskian_residual=log_derivative_match_residual,
        effective_wronskian_residual=effective_residual,
        flux_residual=effective_residual,
        boundary_residual=outer_boundary_residual,
        expected_flux_scale=0.0,
        match_condition_number=_diagnostic_float(
            oracle_diagnostics,
            "match_condition_number",
        ),
        valid_until_r=required_radius,
        required_eval_radius=required_radius,
        required_eval_radius_covered=True,
        metadata=oracle_metadata,
    )
    diagnostics = RadialDiagnostics(
        boundary_residual=outer_boundary_residual,
        wronskian_residual=effective_residual,
        flux_residual=effective_residual,
        ode_n_steps=(
            int(oracle_diagnostics["riccati_steps"])
            + int(oracle_diagnostics["outward_steps"])
        ),
        ode_status=ode_status,
        r_in=r_in,
        r_out=r_out,
        atol=config.atol,
        rtol=config.rtol,
        match_condition_number=_diagnostic_float(
            oracle_diagnostics,
            "match_condition_number",
        ),
        solver=solver_name,
        barrier_action=barrier_action,
        raw_wronskian_residual=log_derivative_match_residual,
        expected_flux_scale=0.0,
        warnings=(warning,),
    )
    return RadialSolution(
        sector=sector,
        ell=ell,
        k=k,
        r_grid=r_grid,
        psi=psi,
        dpsi_dr=dpsi_dr,
        A_in=complex(result.A_in),
        A_out=complex(result.A_out),
        phase_factor=complex(phase_factor),
        phase_shift=complex(-0.5j * np.log(phase_factor)),
        diagnostics=diagnostics,
        background=background,
        valid_until_r=required_radius,
    )


def _validate_q018_required_radius_oracle_envelope(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
    r_out: float,
    barrier_action: float,
) -> None:
    reasons: list[str] = []
    if getattr(background, "name", None) != "schwarzschild":
        reasons.append("background is not Schwarzschild")
    if not _strict_float_equal(float(getattr(background, "M", np.nan)), _Q018_REQUIRED_M):
        reasons.append("M is not 1")
    if ell not in _Q018_ALLOWED_ELLS:
        reasons.append("ell is outside reviewed matrix")
    if not _strict_float_equal(float(k), _Q018_REQUIRED_K):
        reasons.append("k is outside reviewed matrix")
    if config.required_eval_radius is None:
        reasons.append("required_eval_radius is missing")
    elif not _strict_float_equal(
        float(config.required_eval_radius),
        _Q018_REQUIRED_RADIUS,
    ):
        reasons.append("required_eval_radius is outside reviewed matrix")
    if not _strict_float_equal(float(r_out), _Q018_REQUIRED_R_OUT):
        reasons.append("r_out is outside reviewed matrix")
    if not _strict_float_equal(float(config.r_in_eps), _Q018_REQUIRED_R_IN_EPS):
        reasons.append("r_in_eps is outside reviewed matrix")
    if not _strict_float_equal(float(config.rtol), _Q018_REQUIRED_RTOL):
        reasons.append("rtol is outside reviewed matrix")
    if not _strict_float_equal(float(config.atol), _Q018_REQUIRED_ATOL):
        reasons.append("atol is outside reviewed matrix")

    if reasons:
        metadata: dict[str, str | int | float | bool] = {
            "code": "q018_experimental_oracle_out_of_envelope",
            "severity": "error",
            "message": (
                "Q018 reviewed opt-in oracle was requested outside the "
                "T4u continuous validated envelope."
            ),
            "experimental_required_radius_oracle": _Q018_REQUIRED_RADIUS_ORACLE_NAME,
            "sector": sector.value,
            "ell": int(ell),
            "k": float(k),
            "background_name": str(getattr(background, "name", "<unknown>")),
            "M": float(getattr(background, "M", np.nan)),
            "r_out": float(r_out),
            "required_eval_radius": (
                float("nan")
                if config.required_eval_radius is None
                else float(config.required_eval_radius)
            ),
            "r_in_eps": float(config.r_in_eps),
            "rtol": float(config.rtol),
            "atol": float(config.atol),
            "barrier_action": float(barrier_action),
            "allowed_ells": _Q018_ALLOWED_ELLS_LABEL,
            "allowed_k": _Q018_REQUIRED_K,
            "allowed_M": _Q018_REQUIRED_M,
            "allowed_required_eval_radius": _Q018_REQUIRED_RADIUS,
            "allowed_r_out": _Q018_REQUIRED_R_OUT,
            "rejection_reasons": "; ".join(reasons),
        }
        raise RuntimeError(
            "q018_experimental_oracle_out_of_envelope: structured radial no-go; "
            f"metadata={json.dumps(metadata, sort_keys=True)}"
        )


def _validate_q018_tablei_km4_transition_oracle_envelope(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
    r_out: float,
    barrier_action: float,
    validate_mode: bool = True,
) -> None:
    reasons: list[str] = []
    if getattr(background, "name", None) != "schwarzschild":
        reasons.append("background is not Schwarzschild")
    if not _strict_float_equal(float(getattr(background, "M", np.nan)), _Q018_REQUIRED_M):
        reasons.append("M is not 1")
    if validate_mode and sector not in (Sector.ODD, Sector.EVEN):
        reasons.append("sector is outside reviewed matrix")
    if validate_mode and ell not in _Q018_TABLEI_KM4_ALLOWED_ELLS:
        reasons.append("ell is outside reviewed matrix")
    if not _strict_float_equal(float(k), _Q018_TABLEI_KM4_REQUIRED_K):
        reasons.append("k is outside reviewed matrix")
    if config.required_eval_radius is None:
        reasons.append("required_eval_radius is missing")
    elif not _strict_float_equal(
        float(config.required_eval_radius),
        _Q018_TABLEI_KM4_REQUIRED_RADIUS,
    ):
        reasons.append("required_eval_radius is outside reviewed matrix")
    if not _strict_float_equal(float(r_out), _Q018_TABLEI_KM4_REQUIRED_R_OUT):
        reasons.append("r_out is outside reviewed matrix")
    if not _strict_float_equal(float(config.r_in_eps), _Q018_REQUIRED_R_IN_EPS):
        reasons.append("r_in_eps is outside reviewed matrix")
    if not _strict_float_equal(float(config.rtol), _Q018_REQUIRED_RTOL):
        reasons.append("rtol is outside reviewed matrix")
    if not _strict_float_equal(float(config.atol), _Q018_REQUIRED_ATOL):
        reasons.append("atol is outside reviewed matrix")

    if reasons:
        metadata: dict[str, str | int | float | bool] = {
            "code": "q018_experimental_oracle_out_of_envelope",
            "severity": "error",
            "message": (
                "Q018 reviewed opt-in oracle was requested outside the "
                "T4x kM=4 Table-I transition validated envelope."
            ),
            "experimental_required_radius_oracle": (
                _Q018_TABLEI_KM4_TRANSITION_ORACLE_NAME
            ),
            "sector": sector.value,
            "ell": int(ell),
            "k": float(k),
            "background_name": str(getattr(background, "name", "<unknown>")),
            "M": float(getattr(background, "M", np.nan)),
            "r_out": float(r_out),
            "required_eval_radius": (
                float("nan")
                if config.required_eval_radius is None
                else float(config.required_eval_radius)
            ),
            "r_in_eps": float(config.r_in_eps),
            "rtol": float(config.rtol),
            "atol": float(config.atol),
            "barrier_action": float(barrier_action),
            "allowed_ells": _Q018_TABLEI_KM4_ALLOWED_ELLS_LABEL,
            "allowed_k": _Q018_TABLEI_KM4_REQUIRED_K,
            "allowed_M": _Q018_REQUIRED_M,
            "allowed_required_eval_radius": _Q018_TABLEI_KM4_REQUIRED_RADIUS,
            "allowed_r_out": _Q018_TABLEI_KM4_REQUIRED_R_OUT,
            "rejection_reasons": "; ".join(reasons),
        }
        raise RuntimeError(
            "q018_experimental_oracle_out_of_envelope: structured radial no-go; "
            f"metadata={json.dumps(metadata, sort_keys=True)}"
        )


def _validate_q018_tablei_review_grid_transition_oracle_envelope(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
    r_out: float,
    barrier_action: float,
    validate_mode: bool = True,
) -> None:
    reasons: list[str] = []
    point_id = (
        None
        if config.required_eval_radius is None
        else _q018_tablei_review_grid_point_id(float(config.required_eval_radius))
    )
    normalized_k = _q018_tablei_review_grid_k(float(k))
    if getattr(background, "name", None) != "schwarzschild":
        reasons.append("background is not Schwarzschild")
    if not _strict_float_equal(float(getattr(background, "M", np.nan)), _Q018_REQUIRED_M):
        reasons.append("M is not 1")
    if validate_mode and sector not in (Sector.ODD, Sector.EVEN):
        reasons.append("sector is outside reviewed matrix")
    if normalized_k is None:
        reasons.append("k is outside reviewed matrix")
    if config.required_eval_radius is None:
        reasons.append("required_eval_radius is missing")
    elif point_id is None:
        reasons.append("required_eval_radius is outside reviewed Table-I radii")
    if (
        validate_mode
        and normalized_k is not None
        and point_id is not None
        and not _q018_tablei_review_grid_mode_allowed(
            k=normalized_k,
            ell=ell,
            point_id=point_id,
        )
    ):
        reasons.append("mode is outside measured transition set")
    if not _strict_float_equal(
        float(r_out),
        _Q018_TABLEI_REVIEW_GRID_REQUIRED_R_OUT,
    ):
        reasons.append("r_out is outside reviewed matrix")
    if not _strict_float_equal(float(config.r_in_eps), _Q018_REQUIRED_R_IN_EPS):
        reasons.append("r_in_eps is outside reviewed matrix")
    if not _strict_float_equal(float(config.rtol), _Q018_REQUIRED_RTOL):
        reasons.append("rtol is outside reviewed matrix")
    if not _strict_float_equal(float(config.atol), _Q018_REQUIRED_ATOL):
        reasons.append("atol is outside reviewed matrix")

    if reasons:
        metadata: dict[str, str | int | float | bool] = {
            "code": "q018_experimental_oracle_out_of_envelope",
            "severity": "error",
            "message": (
                "Q018 reviewed opt-in oracle was requested outside the "
                "T4y Fig.5/Fig.6 review-grid transition validated envelope."
            ),
            "experimental_required_radius_oracle": (
                _Q018_TABLEI_REVIEW_GRID_TRANSITION_ORACLE_NAME
            ),
            "sector": sector.value,
            "ell": int(ell),
            "k": float(k),
            "background_name": str(getattr(background, "name", "<unknown>")),
            "M": float(getattr(background, "M", np.nan)),
            "r_out": float(r_out),
            "required_eval_radius": (
                float("nan")
                if config.required_eval_radius is None
                else float(config.required_eval_radius)
            ),
            "r_in_eps": float(config.r_in_eps),
            "rtol": float(config.rtol),
            "atol": float(config.atol),
            "barrier_action": float(barrier_action),
            "allowed_k": _Q018_TABLEI_REVIEW_GRID_ALLOWED_KS_LABEL,
            "allowed_M": _Q018_REQUIRED_M,
            "allowed_required_eval_radii": (
                _Q018_TABLEI_REVIEW_GRID_ALLOWED_RADII_LABEL
            ),
            "allowed_r_out": _Q018_TABLEI_REVIEW_GRID_REQUIRED_R_OUT,
            "review_grid_point_id": "" if point_id is None else point_id,
            "validated_transition_segments": (
                "T4y compressed measured Fig.5/Fig.6 review-grid transition set"
            ),
            "rejection_reasons": "; ".join(reasons),
        }
        raise RuntimeError(
            "q018_experimental_oracle_out_of_envelope: structured radial no-go; "
            f"metadata={json.dumps(metadata, sort_keys=True)}"
        )


def _q018_tablei_review_grid_point_id(required_radius: float) -> str | None:
    for point_id, radius in _Q018_TABLEI_REVIEW_GRID_POINTS:
        if _strict_float_equal(float(required_radius), radius):
            return point_id
    return None


def _q018_tablei_review_grid_k(k: float) -> float | None:
    for allowed_k in _Q018_TABLEI_REVIEW_GRID_ALLOWED_KS:
        if _strict_float_equal(float(k), allowed_k):
            return allowed_k
    return None


def _q018_tablei_review_grid_mode_allowed(
    *,
    k: float,
    ell: int,
    point_id: str,
) -> bool:
    for ell_min, ell_max, point_ids in _Q018_TABLEI_REVIEW_GRID_TRANSITION_SEGMENTS[k]:
        if ell_min <= int(ell) <= ell_max and point_id in point_ids:
            return True
    return False


def _validate_q018_targeted_adaptive_oracle_envelope(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
    r_out: float,
    barrier_action: float,
    validate_mode: bool = True,
) -> None:
    """Require literal T4aa sector-aware transition membership."""
    reasons: list[str] = []
    point_id = (
        None
        if config.required_eval_radius is None
        else _q018_targeted_adaptive_point_id(
            float(config.required_eval_radius)
        )
    )
    normalized_k = _q018_targeted_adaptive_k(float(k))
    if getattr(background, "name", None) != "schwarzschild":
        reasons.append("background is not Schwarzschild")
    if not _strict_float_equal(float(getattr(background, "M", np.nan)), _Q018_REQUIRED_M):
        reasons.append("M is not 1")
    if validate_mode and sector not in (Sector.ODD, Sector.EVEN):
        reasons.append("sector is outside reviewed matrix")
    if normalized_k is None:
        reasons.append("k is outside measured targeted-adaptive matrix")
    if config.required_eval_radius is None:
        reasons.append("required_eval_radius is missing")
    elif point_id is None:
        reasons.append("required_eval_radius is outside measured Table-I radii")
    if (
        validate_mode
        and normalized_k is not None
        and point_id is not None
        and not _q018_targeted_adaptive_mode_allowed(
            k=normalized_k,
            sector=sector,
            ell=ell,
            point_id=point_id,
        )
    ):
        reasons.append("mode is outside measured targeted-adaptive transition set")
    if not _strict_float_equal(float(r_out), _Q018_TABLEI_REVIEW_GRID_REQUIRED_R_OUT):
        reasons.append("r_out is outside reviewed matrix")
    if not _strict_float_equal(float(config.r_in_eps), _Q018_REQUIRED_R_IN_EPS):
        reasons.append("r_in_eps is outside reviewed matrix")
    if not _strict_float_equal(float(config.rtol), _Q018_REQUIRED_RTOL):
        reasons.append("rtol is outside reviewed matrix")
    if not _strict_float_equal(float(config.atol), _Q018_REQUIRED_ATOL):
        reasons.append("atol is outside reviewed matrix")

    if reasons:
        metadata: dict[str, str | int | float | bool] = {
            "code": "q018_experimental_oracle_out_of_envelope",
            "severity": "error",
            "message": (
                "Q018 reviewed opt-in oracle was requested outside the "
                "T4aa targeted-adaptive sector-aware transition envelope."
            ),
            "experimental_required_radius_oracle": _Q018_TARGETED_ADAPTIVE_ORACLE_NAME,
            "sector": sector.value,
            "ell": int(ell),
            "k": float(k),
            "background_name": str(getattr(background, "name", "<unknown>")),
            "M": float(getattr(background, "M", np.nan)),
            "r_out": float(r_out),
            "required_eval_radius": (
                float("nan")
                if config.required_eval_radius is None
                else float(config.required_eval_radius)
            ),
            "r_in_eps": float(config.r_in_eps),
            "rtol": float(config.rtol),
            "atol": float(config.atol),
            "barrier_action": float(barrier_action),
            "allowed_k": ",".join(
                f"{allowed_k:.17g}"
                for allowed_k in _Q018_TARGETED_ADAPTIVE_FREQUENCIES
            ),
            "allowed_M": _Q018_REQUIRED_M,
            "allowed_required_eval_radii": ",".join(
                f"{radius:.17g}" for _, radius in _Q018_TARGETED_ADAPTIVE_POINTS
            ),
            "allowed_r_out": _Q018_TABLEI_REVIEW_GRID_REQUIRED_R_OUT,
            "review_grid_point_id": "" if point_id is None else point_id,
            "validated_transition_segments": (
                "T4aa complete measured targeted-adaptive transition set"
            ),
            "rejection_reasons": "; ".join(reasons),
        }
        raise RuntimeError(
            "q018_experimental_oracle_out_of_envelope: structured radial no-go; "
            f"metadata={json.dumps(metadata, sort_keys=True)}"
        )


def _q018_targeted_adaptive_point_id(required_radius: float) -> str | None:
    for point_id, radius in _Q018_TARGETED_ADAPTIVE_POINTS:
        if _strict_float_equal(float(required_radius), radius):
            return point_id
    return None


def _q018_targeted_adaptive_k(k: float) -> float | None:
    for allowed_k in _Q018_TARGETED_ADAPTIVE_FREQUENCIES:
        if _strict_float_equal(float(k), allowed_k):
            return allowed_k
    return None


def _q018_targeted_adaptive_mode_allowed(
    *,
    k: float,
    sector: Sector,
    ell: int,
    point_id: str,
) -> bool:
    for ell_min, ell_max, point_ids in _Q018_TARGETED_ADAPTIVE_TRANSITION_SEGMENTS[
        (k, sector.value)
    ]:
        if ell_min <= int(ell) <= ell_max and point_id in point_ids:
            return True
    return False


def _validate_q018_further_local_oracle_envelope(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
    r_out: float,
    barrier_action: float,
    validate_mode: bool = True,
) -> None:
    """Require literal T4ab sector-aware transition membership."""
    reasons: list[str] = []
    point_id = (
        None
        if config.required_eval_radius is None
        else _q018_further_local_point_id(float(config.required_eval_radius))
    )
    normalized_k = _q018_further_local_k(float(k))
    if getattr(background, "name", None) != "schwarzschild":
        reasons.append("background is not Schwarzschild")
    if not _strict_float_equal(float(getattr(background, "M", np.nan)), _Q018_REQUIRED_M):
        reasons.append("M is not 1")
    if validate_mode and sector not in (Sector.ODD, Sector.EVEN):
        reasons.append("sector is outside reviewed matrix")
    if normalized_k is None:
        reasons.append("k is outside measured further-local matrix")
    if config.required_eval_radius is None:
        reasons.append("required_eval_radius is missing")
    elif point_id is None:
        reasons.append("required_eval_radius is outside measured Table-I radii")
    if (
        validate_mode
        and normalized_k is not None
        and point_id is not None
        and not _q018_further_local_mode_allowed(
            k=normalized_k,
            sector=sector,
            ell=ell,
            point_id=point_id,
        )
    ):
        reasons.append("mode is outside measured further-local transition set")
    if not _strict_float_equal(float(r_out), _Q018_TABLEI_REVIEW_GRID_REQUIRED_R_OUT):
        reasons.append("r_out is outside reviewed matrix")
    if not _strict_float_equal(float(config.r_in_eps), _Q018_REQUIRED_R_IN_EPS):
        reasons.append("r_in_eps is outside reviewed matrix")
    if not _strict_float_equal(float(config.rtol), _Q018_REQUIRED_RTOL):
        reasons.append("rtol is outside reviewed matrix")
    if not _strict_float_equal(float(config.atol), _Q018_REQUIRED_ATOL):
        reasons.append("atol is outside reviewed matrix")

    if reasons:
        metadata: dict[str, str | int | float | bool] = {
            "code": "q018_experimental_oracle_out_of_envelope",
            "severity": "error",
            "message": (
                "Q018 reviewed opt-in oracle was requested outside the "
                "T4ab further-local sector-aware transition envelope."
            ),
            "experimental_required_radius_oracle": _Q018_FURTHER_LOCAL_ORACLE_NAME,
            "sector": sector.value,
            "ell": int(ell),
            "k": float(k),
            "background_name": str(getattr(background, "name", "<unknown>")),
            "M": float(getattr(background, "M", np.nan)),
            "r_out": float(r_out),
            "required_eval_radius": (
                float("nan")
                if config.required_eval_radius is None
                else float(config.required_eval_radius)
            ),
            "r_in_eps": float(config.r_in_eps),
            "rtol": float(config.rtol),
            "atol": float(config.atol),
            "barrier_action": float(barrier_action),
            "allowed_k": ",".join(
                f"{allowed_k:.17g}" for allowed_k in _Q018_FURTHER_LOCAL_FREQUENCIES
            ),
            "allowed_M": _Q018_REQUIRED_M,
            "allowed_required_eval_radii": ",".join(
                f"{radius:.17g}" for _, radius in _Q018_FURTHER_LOCAL_POINTS
            ),
            "allowed_r_out": _Q018_TABLEI_REVIEW_GRID_REQUIRED_R_OUT,
            "review_grid_point_id": "" if point_id is None else point_id,
            "validated_transition_segments": (
                "T4ab complete measured further-local transition set"
            ),
            "rejection_reasons": "; ".join(reasons),
        }
        raise RuntimeError(
            "q018_experimental_oracle_out_of_envelope: structured radial no-go; "
            f"metadata={json.dumps(metadata, sort_keys=True)}"
        )


def _q018_further_local_point_id(required_radius: float) -> str | None:
    for point_id, radius in _Q018_FURTHER_LOCAL_POINTS:
        if _strict_float_equal(float(required_radius), radius):
            return point_id
    return None


def _q018_further_local_k(k: float) -> float | None:
    for allowed_k in _Q018_FURTHER_LOCAL_FREQUENCIES:
        if _strict_float_equal(float(k), allowed_k):
            return allowed_k
    return None


def _q018_further_local_mode_allowed(
    *,
    k: float,
    sector: Sector,
    ell: int,
    point_id: str,
) -> bool:
    for ell_min, ell_max, point_ids in _Q018_FURTHER_LOCAL_TRANSITION_SEGMENTS[
        (k, sector.value)
    ]:
        if ell_min <= int(ell) <= ell_max and point_id in point_ids:
            return True
    return False


def _validate_q018_literal_failed_child_oracle_envelope(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
    r_out: float,
    barrier_action: float,
    validate_mode: bool = True,
) -> None:
    """Require literal T4ac sector-aware failed-child membership."""
    reasons: list[str] = []
    point_id = (
        None
        if config.required_eval_radius is None
        else _q018_literal_failed_child_point_id(
            float(config.required_eval_radius)
        )
    )
    normalized_k = _q018_literal_failed_child_k(float(k))
    if getattr(background, "name", None) != "schwarzschild":
        reasons.append("background is not Schwarzschild")
    if not _strict_float_equal(
        float(getattr(background, "M", np.nan)), _Q018_REQUIRED_M
    ):
        reasons.append("M is not 1")
    if validate_mode and sector not in (Sector.ODD, Sector.EVEN):
        reasons.append("sector is outside reviewed matrix")
    if normalized_k is None:
        reasons.append("k is outside measured literal failed-child matrix")
    if config.required_eval_radius is None:
        reasons.append("required_eval_radius is missing")
    elif point_id is None:
        reasons.append("required_eval_radius is outside measured Table-I radii")
    if (
        validate_mode
        and normalized_k is not None
        and point_id is not None
        and not _q018_literal_failed_child_mode_allowed(
            k=normalized_k,
            sector=sector,
            ell=ell,
            point_id=point_id,
        )
    ):
        reasons.append(
            "mode is outside measured literal failed-child transition set"
        )
    if not _strict_float_equal(
        float(r_out), _Q018_TABLEI_REVIEW_GRID_REQUIRED_R_OUT
    ):
        reasons.append("r_out is outside reviewed matrix")
    if not _strict_float_equal(float(config.r_in_eps), _Q018_REQUIRED_R_IN_EPS):
        reasons.append("r_in_eps is outside reviewed matrix")
    if not _strict_float_equal(float(config.rtol), _Q018_REQUIRED_RTOL):
        reasons.append("rtol is outside reviewed matrix")
    if not _strict_float_equal(float(config.atol), _Q018_REQUIRED_ATOL):
        reasons.append("atol is outside reviewed matrix")

    if reasons:
        metadata: dict[str, str | int | float | bool] = {
            "code": "q018_experimental_oracle_out_of_envelope",
            "severity": "error",
            "message": (
                "Q018 reviewed opt-in oracle was requested outside the "
                "T4ac literal failed-child sector-aware transition envelope."
            ),
            "experimental_required_radius_oracle": (
                _Q018_LITERAL_FAILED_CHILD_ORACLE_NAME
            ),
            "sector": sector.value,
            "ell": int(ell),
            "k": float(k),
            "background_name": str(getattr(background, "name", "<unknown>")),
            "M": float(getattr(background, "M", np.nan)),
            "r_out": float(r_out),
            "required_eval_radius": (
                float("nan")
                if config.required_eval_radius is None
                else float(config.required_eval_radius)
            ),
            "r_in_eps": float(config.r_in_eps),
            "rtol": float(config.rtol),
            "atol": float(config.atol),
            "barrier_action": float(barrier_action),
            "allowed_k": ",".join(
                f"{allowed_k:.17g}"
                for allowed_k in _Q018_LITERAL_FAILED_CHILD_FREQUENCIES
            ),
            "allowed_M": _Q018_REQUIRED_M,
            "allowed_required_eval_radii": ",".join(
                f"{radius:.17g}"
                for _, radius in _Q018_LITERAL_FAILED_CHILD_POINTS
            ),
            "allowed_r_out": _Q018_TABLEI_REVIEW_GRID_REQUIRED_R_OUT,
            "review_grid_point_id": "" if point_id is None else point_id,
            "validated_transition_segments": (
                "T4ac complete measured literal failed-child transition set"
            ),
            "rejection_reasons": "; ".join(reasons),
        }
        raise RuntimeError(
            "q018_experimental_oracle_out_of_envelope: structured radial no-go; "
            f"metadata={json.dumps(metadata, sort_keys=True)}"
        )


def _q018_literal_failed_child_point_id(
    required_radius: float,
) -> str | None:
    for point_id, radius in _Q018_LITERAL_FAILED_CHILD_POINTS:
        if _strict_float_equal(float(required_radius), radius):
            return point_id
    return None


def _q018_literal_failed_child_k(k: float) -> float | None:
    for allowed_k in _Q018_LITERAL_FAILED_CHILD_FREQUENCIES:
        if _strict_float_equal(float(k), allowed_k):
            return allowed_k
    return None


def _q018_literal_failed_child_mode_allowed(
    *,
    k: float,
    sector: Sector,
    ell: int,
    point_id: str,
) -> bool:
    for ell_min, ell_max, point_ids in (
        _Q018_LITERAL_FAILED_CHILD_TRANSITION_SEGMENTS[(k, sector.value)]
    ):
        if ell_min <= int(ell) <= ell_max and point_id in point_ids:
            return True
    return False


def _validate_q018_another_bounded_local_oracle_envelope(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
    r_out: float,
    barrier_action: float,
    validate_mode: bool = True,
) -> None:
    """Require literal T4ad sector-aware failed-child membership."""
    reasons: list[str] = []
    point_id = (
        None
        if config.required_eval_radius is None
        else _q018_another_bounded_local_point_id(
            float(config.required_eval_radius)
        )
    )
    normalized_k = _q018_another_bounded_local_k(float(k))
    if getattr(background, "name", None) != "schwarzschild":
        reasons.append("background is not Schwarzschild")
    if not _strict_float_equal(
        float(getattr(background, "M", np.nan)), _Q018_REQUIRED_M
    ):
        reasons.append("M is not 1")
    if validate_mode and sector not in (Sector.ODD, Sector.EVEN):
        reasons.append("sector is outside reviewed matrix")
    if normalized_k is None:
        reasons.append("k is outside measured another-bounded-local matrix")
    if config.required_eval_radius is None:
        reasons.append("required_eval_radius is missing")
    elif point_id is None:
        reasons.append("required_eval_radius is outside measured Table-I radii")
    if (
        validate_mode
        and normalized_k is not None
        and point_id is not None
        and not _q018_another_bounded_local_mode_allowed(
            k=normalized_k,
            sector=sector,
            ell=ell,
            point_id=point_id,
        )
    ):
        reasons.append(
            "mode is outside measured another-bounded-local transition set"
        )
    if not _strict_float_equal(
        float(r_out), _Q018_TABLEI_REVIEW_GRID_REQUIRED_R_OUT
    ):
        reasons.append("r_out is outside reviewed matrix")
    if not _strict_float_equal(float(config.r_in_eps), _Q018_REQUIRED_R_IN_EPS):
        reasons.append("r_in_eps is outside reviewed matrix")
    if not _strict_float_equal(float(config.rtol), _Q018_REQUIRED_RTOL):
        reasons.append("rtol is outside reviewed matrix")
    if not _strict_float_equal(float(config.atol), _Q018_REQUIRED_ATOL):
        reasons.append("atol is outside reviewed matrix")

    if reasons:
        metadata: dict[str, str | int | float | bool] = {
            "code": "q018_experimental_oracle_out_of_envelope",
            "severity": "error",
            "message": (
                "Q018 reviewed opt-in oracle was requested outside the "
                "T4ad another-bounded-local sector-aware transition envelope."
            ),
            "experimental_required_radius_oracle": (
                _Q018_ANOTHER_BOUNDED_LOCAL_ORACLE_NAME
            ),
            "sector": sector.value,
            "ell": int(ell),
            "k": float(k),
            "background_name": str(getattr(background, "name", "<unknown>")),
            "M": float(getattr(background, "M", np.nan)),
            "r_out": float(r_out),
            "required_eval_radius": (
                float("nan")
                if config.required_eval_radius is None
                else float(config.required_eval_radius)
            ),
            "r_in_eps": float(config.r_in_eps),
            "rtol": float(config.rtol),
            "atol": float(config.atol),
            "barrier_action": float(barrier_action),
            "allowed_k": ",".join(
                f"{allowed_k:.17g}"
                for allowed_k in _Q018_ANOTHER_BOUNDED_LOCAL_FREQUENCIES
            ),
            "allowed_M": _Q018_REQUIRED_M,
            "allowed_required_eval_radii": ",".join(
                f"{radius:.17g}"
                for _, radius in _Q018_ANOTHER_BOUNDED_LOCAL_POINTS
            ),
            "allowed_r_out": _Q018_TABLEI_REVIEW_GRID_REQUIRED_R_OUT,
            "review_grid_point_id": "" if point_id is None else point_id,
            "validated_transition_segments": (
                "T4ad complete measured another-bounded-local transition set"
            ),
            "rejection_reasons": "; ".join(reasons),
        }
        raise RuntimeError(
            "q018_experimental_oracle_out_of_envelope: structured radial no-go; "
            f"metadata={json.dumps(metadata, sort_keys=True)}"
        )


def _q018_another_bounded_local_point_id(
    required_radius: float,
) -> str | None:
    for point_id, radius in _Q018_ANOTHER_BOUNDED_LOCAL_POINTS:
        if _strict_float_equal(float(required_radius), radius):
            return point_id
    return None


def _q018_another_bounded_local_k(k: float) -> float | None:
    for allowed_k in _Q018_ANOTHER_BOUNDED_LOCAL_FREQUENCIES:
        if _strict_float_equal(float(k), allowed_k):
            return allowed_k
    return None


def _q018_another_bounded_local_mode_allowed(
    *,
    k: float,
    sector: Sector,
    ell: int,
    point_id: str,
) -> bool:
    for ell_min, ell_max, point_ids in (
        _Q018_ANOTHER_BOUNDED_LOCAL_TRANSITION_SEGMENTS[(k, sector.value)]
    ):
        if ell_min <= int(ell) <= ell_max and point_id in point_ids:
            return True
    return False


def _validate_q018_delta0p1_risk_oracle_envelope(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
    r_out: float,
    barrier_action: float,
    validate_mode: bool = True,
) -> None:
    """Require literal T4z risk-pilot membership, without interpolation."""
    reasons: list[str] = []
    point_id = (
        None
        if config.required_eval_radius is None
        else _q018_delta0p1_risk_point_id(float(config.required_eval_radius))
    )
    normalized_k = _q018_delta0p1_risk_k(float(k))
    if getattr(background, "name", None) != "schwarzschild":
        reasons.append("background is not Schwarzschild")
    if not _strict_float_equal(float(getattr(background, "M", np.nan)), _Q018_REQUIRED_M):
        reasons.append("M is not 1")
    if validate_mode and sector not in (Sector.ODD, Sector.EVEN):
        reasons.append("sector is outside reviewed matrix")
    if normalized_k is None:
        reasons.append("k is outside measured risk-pilot matrix")
    if config.required_eval_radius is None:
        reasons.append("required_eval_radius is missing")
    elif point_id is None:
        reasons.append("required_eval_radius is outside measured Table-I radii")
    if (
        validate_mode
        and normalized_k is not None
        and point_id is not None
        and not _q018_delta0p1_risk_mode_allowed(
            k=normalized_k,
            ell=ell,
            point_id=point_id,
        )
    ):
        reasons.append("mode is outside measured transition set")
    if not _strict_float_equal(float(r_out), _Q018_TABLEI_REVIEW_GRID_REQUIRED_R_OUT):
        reasons.append("r_out is outside reviewed matrix")
    if not _strict_float_equal(float(config.r_in_eps), _Q018_REQUIRED_R_IN_EPS):
        reasons.append("r_in_eps is outside reviewed matrix")
    if not _strict_float_equal(float(config.rtol), _Q018_REQUIRED_RTOL):
        reasons.append("rtol is outside reviewed matrix")
    if not _strict_float_equal(float(config.atol), _Q018_REQUIRED_ATOL):
        reasons.append("atol is outside reviewed matrix")

    if reasons:
        metadata: dict[str, str | int | float | bool] = {
            "code": "q018_experimental_oracle_out_of_envelope",
            "severity": "error",
            "message": (
                "Q018 reviewed opt-in oracle was requested outside the "
                "T4z Delta0p1 risk-pilot transition validated envelope."
            ),
            "experimental_required_radius_oracle": _Q018_DELTA0P1_RISK_ORACLE_NAME,
            "sector": sector.value,
            "ell": int(ell),
            "k": float(k),
            "background_name": str(getattr(background, "name", "<unknown>")),
            "M": float(getattr(background, "M", np.nan)),
            "r_out": float(r_out),
            "required_eval_radius": (
                float("nan")
                if config.required_eval_radius is None
                else float(config.required_eval_radius)
            ),
            "r_in_eps": float(config.r_in_eps),
            "rtol": float(config.rtol),
            "atol": float(config.atol),
            "barrier_action": float(barrier_action),
            "allowed_k": ",".join(
                f"{allowed_k:.17g}" for allowed_k in _Q018_DELTA0P1_RISK_FREQUENCIES
            ),
            "allowed_M": _Q018_REQUIRED_M,
            "allowed_required_eval_radii": ",".join(
                f"{radius:.17g}" for _, radius in _Q018_DELTA0P1_RISK_POINTS
            ),
            "allowed_r_out": _Q018_TABLEI_REVIEW_GRID_REQUIRED_R_OUT,
            "review_grid_point_id": "" if point_id is None else point_id,
            "validated_transition_segments": (
                "T4z complete measured Delta0p1 risk-pilot transition set"
            ),
            "rejection_reasons": "; ".join(reasons),
        }
        raise RuntimeError(
            "q018_experimental_oracle_out_of_envelope: structured radial no-go; "
            f"metadata={json.dumps(metadata, sort_keys=True)}"
        )


def _q018_delta0p1_risk_point_id(required_radius: float) -> str | None:
    for point_id, radius in _Q018_DELTA0P1_RISK_POINTS:
        if _strict_float_equal(float(required_radius), radius):
            return point_id
    return None


def _q018_delta0p1_risk_k(k: float) -> float | None:
    for allowed_k in _Q018_DELTA0P1_RISK_FREQUENCIES:
        if _strict_float_equal(float(k), allowed_k):
            return allowed_k
    return None


def _q018_delta0p1_risk_mode_allowed(
    *,
    k: float,
    ell: int,
    point_id: str,
) -> bool:
    for ell_min, ell_max, point_ids in _Q018_DELTA0P1_RISK_TRANSITION_SEGMENTS[k]:
        if ell_min <= int(ell) <= ell_max and point_id in point_ids:
            return True
    return False


def _validate_q018_oracle_result(
    *,
    result: Any,
    residual: float,
    outer_boundary_residual: float,
    normalization_residual: float,
    log_derivative_match_residual: float,
    sector: Sector,
    ell: int,
    k: float,
) -> None:
    if (
        result.valid_at_required_radius
        and _finite_complex(result.psi)
        and _finite_complex(result.dpsi_dr)
        and _finite_complex(result.A_in)
        and _finite_complex(result.A_out)
        and abs(result.A_in - 1.0) < 1e-8
        and outer_boundary_residual < 1e-8
        and normalization_residual < 1e-8
        and log_derivative_match_residual < 1e-7
    ):
        return

    metadata: dict[str, str | int | float | bool] = {
        "code": "q018_experimental_oracle_residual_failure",
        "severity": "error",
        "sector": sector.value,
        "ell": int(ell),
        "k": float(k),
        "finite_psi": _finite_complex(result.psi),
        "finite_dpsi_dr": _finite_complex(result.dpsi_dr),
        "finite_A_in": _finite_complex(result.A_in),
        "finite_A_out": _finite_complex(result.A_out),
        "abs_A_in_minus_one": float(abs(result.A_in - 1.0)),
        "outer_boundary_residual": float(outer_boundary_residual),
        "normalization_residual": float(normalization_residual),
        "log_derivative_match_residual": float(log_derivative_match_residual),
        "effective_residual": float(residual),
    }
    raise RuntimeError(
        "q018_experimental_oracle_residual_failure: structured radial no-go; "
        f"metadata={json.dumps(metadata, sort_keys=True)}"
    )


def _diagnostic_float(
    diagnostics: Mapping[str, object],
    key: str,
) -> float:
    value = float(diagnostics[key])
    if not np.isfinite(value):
        raise RuntimeError(f"Q018 oracle diagnostic {key!r} is non-finite.")
    return value


def _strict_float_equal(value: float, target: float) -> bool:
    return bool(np.isclose(value, target, rtol=0.0, atol=1e-15))


def _finite_complex(value: complex) -> bool:
    return bool(np.isfinite(value.real) and np.isfinite(value.imag))
