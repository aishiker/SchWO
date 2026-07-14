from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np
from numpy.typing import ArrayLike
from scipy.integrate import solve_bvp, solve_ivp
from scipy.interpolate import CubicSpline

from schwgw.backgrounds.base import StaticSphericalBackground
from schwgw.numerics.boundary_conditions import (
    BoundaryConfig,
    horizon_ingoing_initial_data,
    radial_domain,
)
from schwgw.numerics.matching import match_outer_asymptotic
from schwgw.numerics.q018_delta0p1_risk_envelope import (
    FREQUENCIES as _Q018_DELTA0P1_RISK_FREQUENCIES,
    POINTS as _Q018_DELTA0P1_RISK_POINTS,
    TRANSITION_SEGMENTS as _Q018_DELTA0P1_RISK_TRANSITION_SEGMENTS,
)
from schwgw.perturbations import Sector, V_RW, V_Zerilli


_FIRST_PASS_WRONSKIAN_TARGET = 1e-7
_HEALTHY_BOUNDARY_RESIDUAL = 1e-8
_BVP_BRANCH_BARRIER_ACTION = 8.0
_TRANSITION_BARRIER_ACTION_WIDTH = 2.0
_TRANSITION_FLUX_SCALE_FACTOR = 4.0
_HEALTHY_MATCH_CONDITION_NUMBER = 10.0
_BVP_MAX_NODES = 50000
_EVANESCENT_SUPPRESSION_BARRIER_ACTION = 706.0
_EVANESCENT_SUPPRESSION_TAIL_ACTION = 55.0
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
)


@dataclass(frozen=True)
class RadialDiagnosticWarning:
    code: str
    severity: str
    message: str
    sector: str
    ell: int
    k: float
    solver: str
    barrier_action: float
    raw_wronskian_residual: float
    effective_wronskian_residual: float
    flux_residual: float
    boundary_residual: float
    expected_flux_scale: float
    match_condition_number: float
    suppression_bound: float | None = None
    valid_until_r: float | None = None
    required_eval_radius: float | None = None
    required_eval_radius_covered: bool | None = None
    no_go_reason: str | None = None
    metadata: Mapping[str, str | int | float | bool] | None = None

    def to_metadata(self) -> dict[str, str | int | float | bool]:
        metadata: dict[str, str | int | float | bool] = {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "sector": self.sector,
            "ell": self.ell,
            "k": self.k,
            "solver": self.solver,
            "barrier_action": self.barrier_action,
            "raw_wronskian_residual": self.raw_wronskian_residual,
            "effective_wronskian_residual": self.effective_wronskian_residual,
            "flux_residual": self.flux_residual,
            "boundary_residual": self.boundary_residual,
            "expected_flux_scale": self.expected_flux_scale,
            "match_condition_number": self.match_condition_number,
        }
        if self.suppression_bound is not None:
            metadata["suppression_bound"] = self.suppression_bound
        if self.valid_until_r is not None:
            metadata["valid_until_r"] = self.valid_until_r
        if self.required_eval_radius is not None:
            metadata["required_eval_radius"] = self.required_eval_radius
        if self.required_eval_radius_covered is not None:
            metadata["required_eval_radius_covered"] = self.required_eval_radius_covered
        if self.no_go_reason is not None:
            metadata["no_go_reason"] = self.no_go_reason
        if self.metadata is not None:
            metadata.update(dict(self.metadata))
        return metadata


@dataclass(frozen=True)
class RadialDiagnostics:
    boundary_residual: float
    wronskian_residual: float
    ode_n_steps: int
    ode_status: str
    r_in: float
    r_out: float
    atol: float
    rtol: float
    match_condition_number: float
    flux_residual: float = 0.0
    solver: str = "outward_shooting"
    barrier_action: float = 0.0
    raw_wronskian_residual: float = 0.0
    expected_flux_scale: float = 0.0
    warnings: tuple[RadialDiagnosticWarning, ...] = ()


@dataclass
class RadialSolution:
    sector: Sector
    ell: int
    k: float
    r_grid: np.ndarray
    psi: np.ndarray
    dpsi_dr: np.ndarray
    A_in: complex
    A_out: complex
    phase_factor: complex
    phase_shift: complex
    diagnostics: RadialDiagnostics
    background: StaticSphericalBackground
    valid_until_r: float | None = None
    _psi_spline: CubicSpline | None = None
    _dpsi_dr_spline: CubicSpline | None = None

    def __post_init__(self) -> None:
        self.r_grid = np.asarray(self.r_grid, dtype=float)
        self.psi = np.asarray(self.psi, dtype=complex)
        self.dpsi_dr = np.asarray(self.dpsi_dr, dtype=complex)
        self._psi_spline = CubicSpline(self.r_grid, self.psi)
        self._dpsi_dr_spline = CubicSpline(self.r_grid, self.dpsi_dr)

    def psi_at(self, r: ArrayLike) -> complex | np.ndarray:
        radius = self._validate_eval_radius(r)
        values = self._psi_spline(radius)
        return _return_scalar_if_scalar_input(values, r)

    def dpsi_dr_at(self, r: ArrayLike) -> complex | np.ndarray:
        radius = self._validate_eval_radius(r)
        values = self._dpsi_dr_spline(radius)
        return _return_scalar_if_scalar_input(values, r)

    def dpsi_drstar_at(self, r: ArrayLike) -> complex | np.ndarray:
        radius = self._validate_eval_radius(r)
        values = self.background.f(radius) * self._dpsi_dr_spline(radius)
        return _return_scalar_if_scalar_input(values, r)

    def _validate_eval_radius(self, r: ArrayLike) -> np.ndarray:
        radius = np.asarray(r, dtype=float)
        upper_limit = self.r_grid[-1] if self.valid_until_r is None else self.valid_until_r
        if np.any(radius <= self.background.horizon_radius):
            raise ValueError("Radial solution evaluation requires r > r_horizon.")
        if np.any((radius < self.r_grid[0]) | (radius > upper_limit)):
            raise ValueError("Radial solution evaluation is outside the solved domain.")
        return radius


def solve_radial_mode(
    sector: Sector | str,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    boundary_config: BoundaryConfig | None = None,
) -> RadialSolution:
    """Solve one Schwarzschild RW/Zerilli radial mode.

    Low-barrier modes use unit-horizon outward shooting.  High-barrier modes
    use a unit-incoming-at-infinity BVP, while preserving the public contract
    that A_in is the outer exp(-i k r_star) coefficient.
    """
    sector_enum = _coerce_sector(sector)
    config = boundary_config or BoundaryConfig()
    r_in, r_out = radial_domain(ell=ell, k=k, background=background, config=config)
    barrier_action = _barrier_action(sector_enum, ell, k, background, r_in, r_out)
    oracle_name = config.experimental_required_radius_oracle
    if (
        oracle_name is not None
        and oracle_name not in _SUPPORTED_REQUIRED_RADIUS_ORACLE_NAMES
    ):
        raise ValueError(
            "unsupported experimental_required_radius_oracle: "
            f"{oracle_name!r}"
        )
    if oracle_name == _Q018_TABLEI_KM4_TRANSITION_ORACLE_NAME:
        _validate_q018_tablei_km4_transition_oracle_envelope(
            sector=sector_enum,
            ell=ell,
            k=k,
            background=background,
            config=config,
            r_out=r_out,
            barrier_action=barrier_action,
            validate_mode=False,
        )
    if oracle_name == _Q018_TABLEI_REVIEW_GRID_TRANSITION_ORACLE_NAME:
        _validate_q018_tablei_review_grid_transition_oracle_envelope(
            sector=sector_enum,
            ell=ell,
            k=k,
            background=background,
            config=config,
            r_out=r_out,
            barrier_action=barrier_action,
            validate_mode=False,
        )
    if oracle_name == _Q018_DELTA0P1_RISK_ORACLE_NAME:
        _validate_q018_delta0p1_risk_oracle_envelope(
            sector=sector_enum,
            ell=ell,
            k=k,
            background=background,
            config=config,
            r_out=r_out,
            barrier_action=barrier_action,
            validate_mode=False,
        )

    try:
        if _requires_stabilized_solver(barrier_action):
            return _solve_radial_mode_bvp(
                sector=sector_enum,
                ell=ell,
                k=k,
                background=background,
                config=config,
                r_in=r_in,
                r_out=r_out,
                barrier_action=barrier_action,
            )

        return _solve_radial_mode_outward(
            sector=sector_enum,
            ell=ell,
            k=k,
            background=background,
            config=config,
            r_in=r_in,
            r_out=r_out,
            barrier_action=barrier_action,
        )
    except RuntimeError as exc:
        if (
            oracle_name in _SUPPORTED_REQUIRED_RADIUS_ORACLE_NAMES
            and _is_required_radius_oracle_recoverable_error(exc)
        ):
            return _solve_radial_mode_required_radius_oracle(
                sector=sector_enum,
                ell=ell,
                k=k,
                background=background,
                config=config,
                r_in=r_in,
                r_out=r_out,
                barrier_action=barrier_action,
            )
        raise


def _is_required_radius_uncovered_error(exc: RuntimeError) -> bool:
    return "evanescent_tail_required_radius_uncovered" in str(exc)


def _is_required_radius_oracle_recoverable_error(exc: RuntimeError) -> bool:
    message = str(exc)
    return (
        "evanescent_tail_required_radius_uncovered" in message
        or "evanescent_tail_required_radius_solver_failed" in message
    )


def _solve_radial_mode_outward(
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
    psi_in, dpsi_dr_in = horizon_ingoing_initial_data(
        r_in=r_in,
        k=k,
        background=background,
    )

    solve_kwargs: dict[str, Any] = {
        "method": config.method,
        "rtol": config.rtol,
        "atol": config.atol,
        "dense_output": config.dense_output,
    }
    if config.max_step is not None:
        solve_kwargs["max_step"] = config.max_step

    result = solve_ivp(
        lambda r, y: _radial_rhs(r, y, sector, ell, k, background),
        (r_in, r_out),
        np.array([psi_in, dpsi_dr_in], dtype=complex),
        **solve_kwargs,
    )
    if not result.success:
        raise RuntimeError(f"Radial ODE solve failed: {result.message}")

    r_grid = np.asarray(result.t, dtype=float)
    psi = np.asarray(result.y[0], dtype=complex)
    dpsi_dr = np.asarray(result.y[1], dtype=complex)
    A_in, A_out, boundary_residual, condition_number = match_outer_asymptotic(
        psi=psi[-1],
        dpsi_dr=dpsi_dr[-1],
        r=r_grid[-1],
        k=k,
        background=background,
    )
    if abs(A_in) <= 100.0 * np.finfo(float).eps:
        raise RuntimeError("Outer matching produced near-zero A_in; phase shift is unreliable.")

    phase_factor = -A_out / (((-1) ** ell) * A_in)
    wronskian_residual = _wronskian_residual(psi, dpsi_dr, r_grid, background)
    diagnostics = RadialDiagnostics(
        boundary_residual=boundary_residual,
        wronskian_residual=wronskian_residual,
        flux_residual=wronskian_residual,
        ode_n_steps=len(r_grid),
        ode_status=result.message,
        r_in=r_in,
        r_out=r_out,
        atol=config.atol,
        rtol=config.rtol,
        match_condition_number=condition_number,
        solver="outward_shooting",
        barrier_action=barrier_action,
        raw_wronskian_residual=wronskian_residual,
    )
    return RadialSolution(
        sector=sector,
        ell=ell,
        k=k,
        r_grid=r_grid,
        psi=psi,
        dpsi_dr=dpsi_dr,
        A_in=A_in,
        A_out=A_out,
        phase_factor=complex(phase_factor),
        phase_shift=complex(-0.5j * np.log(phase_factor)),
        diagnostics=diagnostics,
        background=background,
    )


def _solve_radial_mode_bvp(
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
    """Solve high-barrier modes as a two-point boundary value problem.

    The returned solution is normalized to unit incoming amplitude at
    infinity: A_in ~= 1.  This preserves the public scaling contract because
    callers already multiply by the desired incident coefficient divided by
    A_in.
    """

    rstar_in = background.r_star(r_in)
    rstar_out = background.r_star(r_out)
    mesh_size = _bvp_initial_mesh_size(barrier_action)
    rstar_mesh = np.linspace(rstar_in, rstar_out, mesh_size)
    y_guess = _bvp_initial_guess(rstar_mesh, ell, k)
    parameter_guess = np.array([0.0, -float((-1) ** ell)], dtype=float)

    bvp_tol = max(config.rtol, 1e-8)
    result = solve_bvp(
        lambda rstar, y, parameters: _bvp_rhs(
            rstar,
            y,
            sector,
            ell,
            k,
            background,
        ),
        lambda left, right, parameters: _bvp_boundary_residual(
            left,
            right,
            parameters,
            k,
            rstar_out,
        ),
        rstar_mesh,
        y_guess,
        p=parameter_guess,
        tol=bvp_tol,
        bc_tol=bvp_tol,
        max_nodes=_BVP_MAX_NODES,
    )
    if result.status != 0:
        if _is_extreme_evanescent_tail(barrier_action):
            suppressed = _solve_radial_mode_evanescent_tail_suppressed(
                sector=sector,
                ell=ell,
                k=k,
                background=background,
                config=config,
                r_in=r_in,
                r_out=r_out,
                barrier_action=barrier_action,
                bvp_failure_message=result.message,
                fallback_failure_message=(
                    "bidirectional basis integration skipped because the "
                    "barrier action is at the double-precision dynamic-range limit"
                ),
            )
            if suppressed is not None:
                return suppressed
        try:
            return _solve_radial_mode_bidirectional(
                sector=sector,
                ell=ell,
                k=k,
                background=background,
                config=config,
                r_in=r_in,
                r_out=r_out,
                barrier_action=barrier_action,
                bvp_failure_message=result.message,
            )
        except RuntimeError as fallback_error:
            if _is_extreme_evanescent_tail(barrier_action):
                suppressed = _solve_radial_mode_evanescent_tail_suppressed(
                    sector=sector,
                    ell=ell,
                    k=k,
                    background=background,
                    config=config,
                    r_in=r_in,
                    r_out=r_out,
                    barrier_action=barrier_action,
                    bvp_failure_message=result.message,
                    fallback_failure_message=str(fallback_error),
                )
                if suppressed is not None:
                    return suppressed
            required_radius_failure = _required_radius_uncovered_failure_if_available(
                sector=sector,
                ell=ell,
                k=k,
                background=background,
                config=config,
                r_in=r_in,
                r_out=r_out,
                barrier_action=barrier_action,
                bvp_failure_message=result.message,
                fallback_failure_message=str(fallback_error),
            )
            if required_radius_failure is not None:
                raise required_radius_failure from fallback_error
            required_radius_solver_failure = (
                _required_radius_solver_failure_if_available(
                    sector=sector,
                    ell=ell,
                    k=k,
                    background=background,
                    config=config,
                    r_in=r_in,
                    r_out=r_out,
                    barrier_action=barrier_action,
                    bvp_failure_message=result.message,
                    fallback_failure_message=(
                        f"bidirectional fallback failed: {fallback_error}"
                    ),
                )
            )
            if required_radius_solver_failure is not None:
                raise required_radius_solver_failure from fallback_error
            message = _bvp_failure_message(
                sector=sector,
                ell=ell,
                k=k,
                r_out=r_out,
                barrier_action=barrier_action,
                mesh_size=mesh_size,
                result_message=result.message,
            )
            raise RuntimeError(
                f"{message}; bidirectional fallback failed: {fallback_error}"
            ) from fallback_error

    rstar_grid = result.x
    r_grid = np.asarray(background.r_from_r_star(rstar_grid), dtype=float)
    psi = result.y[0] + 1j * result.y[1]
    dpsi_drstar = result.y[2] + 1j * result.y[3]
    dpsi_dr = dpsi_drstar / background.f(r_grid)
    A_out_parameter = complex(result.p[0], result.p[1])

    A_in, A_out, boundary_residual, condition_number = match_outer_asymptotic(
        psi=psi[-1],
        dpsi_dr=dpsi_dr[-1],
        r=r_grid[-1],
        k=k,
        background=background,
    )
    boundary_residual = max(
        boundary_residual,
        _bvp_boundary_norm(result, k, rstar_out),
        abs(A_out - A_out_parameter),
    )
    if abs(A_in) <= 100.0 * np.finfo(float).eps:
        raise RuntimeError("Stabilized radial solve produced near-zero A_in.")

    max_collocation_residual = float(np.max(result.rms_residuals))
    flux_residual = max(max_collocation_residual, boundary_residual)
    raw_wronskian_residual = _wronskian_residual(psi, dpsi_dr, r_grid, background)
    horizon_amplitude = psi[0] / np.exp(-1j * k * rstar_grid[0])
    expected_flux_scale = 2.0 * k * abs(horizon_amplitude) ** 2
    if expected_flux_scale > np.sqrt(np.finfo(float).eps):
        wronskian_residual = raw_wronskian_residual
    else:
        wronskian_residual = flux_residual

    warnings = _radial_diagnostic_warnings(
        sector=sector,
        ell=ell,
        k=k,
        solver="bvp_unit_infinity",
        barrier_action=barrier_action,
        raw_wronskian_residual=raw_wronskian_residual,
        effective_wronskian_residual=wronskian_residual,
        flux_residual=flux_residual,
        boundary_residual=boundary_residual,
        expected_flux_scale=expected_flux_scale,
        match_condition_number=condition_number,
        psi=psi,
        dpsi_dr=dpsi_dr,
    )

    phase_factor = -A_out / (((-1) ** ell) * A_in)
    diagnostics = RadialDiagnostics(
        boundary_residual=boundary_residual,
        wronskian_residual=wronskian_residual,
        flux_residual=flux_residual,
        ode_n_steps=len(r_grid),
        ode_status=result.message,
        r_in=r_in,
        r_out=r_out,
        atol=config.atol,
        rtol=config.rtol,
        match_condition_number=condition_number,
        solver="bvp_unit_infinity",
        barrier_action=barrier_action,
        raw_wronskian_residual=raw_wronskian_residual,
        expected_flux_scale=expected_flux_scale,
        warnings=warnings,
    )
    return RadialSolution(
        sector=sector,
        ell=ell,
        k=k,
        r_grid=r_grid,
        psi=psi,
        dpsi_dr=dpsi_dr,
        A_in=A_in,
        A_out=A_out,
        phase_factor=complex(phase_factor),
        phase_shift=complex(-0.5j * np.log(phase_factor)),
        diagnostics=diagnostics,
        background=background,
    )


def _solve_radial_mode_bidirectional(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
    r_in: float,
    r_out: float,
    barrier_action: float,
    bvp_failure_message: str,
) -> RadialSolution:
    """Construct a unit-infinity solution by matching radial bases."""

    match_radius = _bidirectional_match_radius(
        sector=sector,
        ell=ell,
        k=k,
        background=background,
        r_in=r_in,
        r_out=r_out,
    )
    horizon_psi, horizon_dpsi_dr = horizon_ingoing_initial_data(
        r_in=r_in,
        k=k,
        background=background,
    )
    horizon = _integrate_radial_basis(
        sector=sector,
        ell=ell,
        k=k,
        background=background,
        config=config,
        r_start=r_in,
        r_stop=match_radius,
        psi_start=horizon_psi,
        dpsi_dr_start=horizon_dpsi_dr,
    )

    rstar_out = background.r_star(r_out)
    f_out = background.f(r_out)
    incoming_psi = np.exp(-1j * k * rstar_out)
    incoming_dpsi_dr = (-1j * k / f_out) * incoming_psi
    outgoing_psi = np.exp(1j * k * rstar_out)
    outgoing_dpsi_dr = (1j * k / f_out) * outgoing_psi
    incoming = _integrate_radial_basis(
        sector=sector,
        ell=ell,
        k=k,
        background=background,
        config=config,
        r_start=r_out,
        r_stop=match_radius,
        psi_start=incoming_psi,
        dpsi_dr_start=incoming_dpsi_dr,
    )
    outgoing = _integrate_radial_basis(
        sector=sector,
        ell=ell,
        k=k,
        background=background,
        config=config,
        r_start=r_out,
        r_stop=match_radius,
        psi_start=outgoing_psi,
        dpsi_dr_start=outgoing_dpsi_dr,
    )

    horizon_match = _basis_state_at(horizon, match_radius)
    incoming_match = _basis_state_at(incoming, match_radius)
    outgoing_match = _basis_state_at(outgoing, match_radius)
    match_matrix = np.column_stack([horizon_match, -outgoing_match])
    _validate_bidirectional_match_inputs(
        sector=sector,
        ell=ell,
        k=k,
        match_radius=match_radius,
        horizon_match=horizon_match,
        incoming_match=incoming_match,
        outgoing_match=outgoing_match,
        match_matrix=match_matrix,
    )
    try:
        horizon_scale, A_out_parameter = np.linalg.solve(match_matrix, incoming_match)
        match_condition_number = float(np.linalg.cond(match_matrix))
    except np.linalg.LinAlgError as exc:
        raise RuntimeError(
            "Bidirectional radial matching linear algebra failed "
            f"(sector={sector.value}, ell={ell}, k={k}, "
            f"match_radius={match_radius:.12g}): {exc}"
        ) from exc
    match_residual = _bidirectional_match_residual(
        match_matrix=match_matrix,
        coefficients=np.array([horizon_scale, A_out_parameter], dtype=complex),
        rhs=incoming_match,
    )

    r_left = np.asarray(horizon.t, dtype=float)
    psi_left = horizon_scale * np.asarray(horizon.y[0], dtype=complex)
    dpsi_left = horizon_scale * np.asarray(horizon.y[1], dtype=complex)

    r_right_desc = np.asarray(incoming.t, dtype=float)
    incoming_right = incoming.sol(r_right_desc)
    outgoing_right = outgoing.sol(r_right_desc)
    psi_right_desc = incoming_right[0] + A_out_parameter * outgoing_right[0]
    dpsi_right_desc = incoming_right[1] + A_out_parameter * outgoing_right[1]
    r_right = r_right_desc[::-1]
    psi_right = psi_right_desc[::-1]
    dpsi_right = dpsi_right_desc[::-1]

    r_grid = np.concatenate([r_left, r_right[1:]])
    psi = np.concatenate([psi_left, psi_right[1:]])
    dpsi_dr = np.concatenate([dpsi_left, dpsi_right[1:]])
    if not (
        np.all(np.isfinite(r_grid))
        and np.all(np.isfinite(psi.real))
        and np.all(np.isfinite(psi.imag))
        and np.all(np.isfinite(dpsi_dr.real))
        and np.all(np.isfinite(dpsi_dr.imag))
    ):
        raise RuntimeError("Bidirectional radial matching produced non-finite fields.")
    if np.any(np.diff(r_grid) <= 0.0):
        raise RuntimeError("Bidirectional radial matching produced a non-monotonic grid.")

    A_in, A_out, boundary_residual, boundary_condition_number = match_outer_asymptotic(
        psi=psi[-1],
        dpsi_dr=dpsi_dr[-1],
        r=r_grid[-1],
        k=k,
        background=background,
    )
    if abs(A_in) <= 100.0 * np.finfo(float).eps:
        raise RuntimeError("Bidirectional radial matching produced near-zero A_in.")

    match_jump = _bidirectional_match_jump(
        left_state=np.array([psi_left[-1], dpsi_left[-1]], dtype=complex),
        right_state=np.array([psi_right[0], dpsi_right[0]], dtype=complex),
    )
    raw_wronskian_residual = _wronskian_residual(psi, dpsi_dr, r_grid, background)
    expected_flux_scale = 2.0 * k * abs(horizon_scale) ** 2
    flux_residual = max(boundary_residual, match_residual, match_jump)
    if expected_flux_scale > np.sqrt(np.finfo(float).eps):
        wronskian_residual = raw_wronskian_residual
    else:
        wronskian_residual = flux_residual

    phase_factor = -A_out / (((-1) ** ell) * A_in)
    diagnostics = RadialDiagnostics(
        boundary_residual=boundary_residual,
        wronskian_residual=wronskian_residual,
        flux_residual=flux_residual,
        ode_n_steps=len(r_grid),
        ode_status=(
            "BVP failed with "
            f"{bvp_failure_message}; used bidirectional match at r={match_radius:.12g}"
        ),
        r_in=r_in,
        r_out=r_out,
        atol=config.atol,
        rtol=config.rtol,
        match_condition_number=max(match_condition_number, boundary_condition_number),
        solver="bidirectional_match",
        barrier_action=barrier_action,
        raw_wronskian_residual=raw_wronskian_residual,
        expected_flux_scale=expected_flux_scale,
    )
    return RadialSolution(
        sector=sector,
        ell=ell,
        k=k,
        r_grid=r_grid,
        psi=psi,
        dpsi_dr=dpsi_dr,
        A_in=A_in,
        A_out=A_out,
        phase_factor=complex(phase_factor),
        phase_shift=complex(-0.5j * np.log(phase_factor)),
        diagnostics=diagnostics,
        background=background,
    )


def _solve_radial_mode_evanescent_tail_suppressed(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
    r_in: float,
    r_out: float,
    barrier_action: float,
    bvp_failure_message: str,
    fallback_failure_message: str,
) -> RadialSolution | None:
    tail_domain = _evanescent_tail_domain(
        sector=sector,
        ell=ell,
        k=k,
        background=background,
        r_in=r_in,
        r_out=r_out,
    )
    if tail_domain is None:
        return None
    valid_until_r, local_tail_action = tail_domain
    suppression_bound = float(np.exp(-local_tail_action))
    if not np.isfinite(suppression_bound) or suppression_bound <= 0.0:
        suppression_bound = 0.0

    required_eval_radius = config.required_eval_radius
    if required_eval_radius is not None and valid_until_r < float(required_eval_radius):
        raise RuntimeError(
            _evanescent_tail_required_radius_failure_message(
                sector=sector,
                ell=ell,
                k=k,
                barrier_action=barrier_action,
                suppression_bound=suppression_bound,
                valid_until_r=float(valid_until_r),
                local_tail_action=float(local_tail_action),
                required_eval_radius=float(required_eval_radius),
                bvp_failure_message=bvp_failure_message,
                fallback_failure_message=fallback_failure_message,
            )
        )

    r_grid = np.linspace(r_in, valid_until_r, 16)
    psi = np.zeros_like(r_grid, dtype=complex)
    dpsi_dr = np.zeros_like(r_grid, dtype=complex)
    A_in = 1.0 + 0.0j
    A_out = -complex((-1) ** ell)
    phase_factor = -A_out / (((-1) ** ell) * A_in)
    warning = RadialDiagnosticWarning(
        code="evanescent_tail_suppressed",
        severity="warning",
        message=(
            "Extreme high-ell evanescent tail is below double-precision "
            "resolution over the recorded interior domain; direct BVP "
            "failed, and bidirectional matching was skipped or failed "
            "before this structured suppression policy was applied."
        ),
        sector=sector.value,
        ell=ell,
        k=float(k),
        solver="evanescent_tail_suppressed",
        barrier_action=float(barrier_action),
        raw_wronskian_residual=0.0,
        effective_wronskian_residual=suppression_bound,
        flux_residual=suppression_bound,
        boundary_residual=suppression_bound,
        expected_flux_scale=0.0,
        match_condition_number=0.0,
        suppression_bound=suppression_bound,
        valid_until_r=float(valid_until_r),
        required_eval_radius=(
            None if required_eval_radius is None else float(required_eval_radius)
        ),
        required_eval_radius_covered=(
            None if required_eval_radius is None else valid_until_r >= float(required_eval_radius)
        ),
    )
    diagnostics = RadialDiagnostics(
        boundary_residual=suppression_bound,
        wronskian_residual=suppression_bound,
        flux_residual=suppression_bound,
        ode_n_steps=len(r_grid),
        ode_status=(
            "BVP failed with "
            f"{bvp_failure_message}; bidirectional fallback failed with "
            f"{fallback_failure_message}; evanescent tail suppressed for "
            f"r <= {valid_until_r:.12g} with local WKB action "
            f"{local_tail_action:.12g}"
        ),
        r_in=r_in,
        r_out=r_out,
        atol=config.atol,
        rtol=config.rtol,
        match_condition_number=0.0,
        solver="evanescent_tail_suppressed",
        barrier_action=barrier_action,
        raw_wronskian_residual=0.0,
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
        A_in=A_in,
        A_out=A_out,
        phase_factor=complex(phase_factor),
        phase_shift=complex(-0.5j * np.log(phase_factor)),
        diagnostics=diagnostics,
        background=background,
        valid_until_r=float(valid_until_r),
    )


def _evanescent_tail_required_radius_failure_message(
    *,
    sector: Sector,
    ell: int,
    k: float,
    barrier_action: float,
    suppression_bound: float,
    valid_until_r: float,
    local_tail_action: float,
    required_eval_radius: float,
    bvp_failure_message: str,
    fallback_failure_message: str,
) -> str:
    metadata: dict[str, str | int | float | bool] = {
        "code": "evanescent_tail_required_radius_uncovered",
        "severity": "error",
        "message": (
            "Extreme evanescent-tail suppression did not certify the requested "
            "evaluation radius."
        ),
        "sector": sector.value,
        "ell": ell,
        "k": float(k),
        "solver": "evanescent_tail_suppressed",
        "barrier_action": float(barrier_action),
        "suppression_bound": float(suppression_bound),
        "valid_until_r": float(valid_until_r),
        "local_tail_action": float(local_tail_action),
        "tail_action_threshold": float(_EVANESCENT_SUPPRESSION_TAIL_ACTION),
        "required_eval_radius": float(required_eval_radius),
        "required_eval_radius_covered": False,
        "no_go_reason": (
            "required_eval_radius exceeds the certified zero-tail domain; "
            "R60 support needs a target-radius conservative bound or a "
            "rescaled/log-amplitude radial architecture."
        ),
        "bvp_failure_message": bvp_failure_message,
        "fallback_failure_message": fallback_failure_message,
    }
    return (
        "evanescent_tail_required_radius_uncovered: structured radial no-go; "
        f"metadata={json.dumps(metadata, sort_keys=True)}"
    )


def _evanescent_tail_required_radius_solver_failure_message(
    *,
    sector: Sector,
    ell: int,
    k: float,
    barrier_action: float,
    valid_until_r: float,
    local_tail_action: float,
    required_eval_radius: float,
    bvp_failure_message: str,
    fallback_failure_message: str,
) -> str:
    metadata: dict[str, str | int | float | bool] = {
        "code": "evanescent_tail_required_radius_solver_failed",
        "severity": "error",
        "message": (
            "Stabilized radial BVP and bidirectional fallback failed before "
            "returning a certified required-radius solution."
        ),
        "sector": sector.value,
        "ell": ell,
        "k": float(k),
        "solver": "bvp_unit_infinity",
        "barrier_action": float(barrier_action),
        "valid_until_r": float(valid_until_r),
        "local_tail_action": float(local_tail_action),
        "tail_action_threshold": float(_EVANESCENT_SUPPRESSION_TAIL_ACTION),
        "required_eval_radius": float(required_eval_radius),
        "required_eval_radius_covered": True,
        "no_go_reason": (
            "required_eval_radius lies inside the current local-tail "
            "certificate, but the production BVP and bidirectional fallback "
            "did not produce a finite radial solution; a reviewed "
            "rescaled/log-amplitude radial adapter is required."
        ),
        "bvp_failure_message": bvp_failure_message,
        "fallback_failure_message": fallback_failure_message,
    }
    return (
        "evanescent_tail_required_radius_solver_failed: structured radial no-go; "
        f"metadata={json.dumps(metadata, sort_keys=True)}"
    )


def _required_radius_uncovered_failure_if_available(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
    r_in: float,
    r_out: float,
    barrier_action: float,
    bvp_failure_message: str,
    fallback_failure_message: str,
) -> RuntimeError | None:
    required_eval_radius = config.required_eval_radius
    if required_eval_radius is None:
        return None
    tail_domain = _evanescent_tail_domain(
        sector=sector,
        ell=ell,
        k=k,
        background=background,
        r_in=r_in,
        r_out=r_out,
    )
    if tail_domain is None:
        return None
    valid_until_r, local_tail_action = tail_domain
    if valid_until_r >= float(required_eval_radius):
        return None
    suppression_bound = float(np.exp(-local_tail_action))
    if not np.isfinite(suppression_bound) or suppression_bound <= 0.0:
        suppression_bound = 0.0
    return RuntimeError(
        _evanescent_tail_required_radius_failure_message(
            sector=sector,
            ell=ell,
            k=k,
            barrier_action=barrier_action,
            suppression_bound=suppression_bound,
            valid_until_r=float(valid_until_r),
            local_tail_action=float(local_tail_action),
            required_eval_radius=float(required_eval_radius),
            bvp_failure_message=bvp_failure_message,
            fallback_failure_message=fallback_failure_message,
        )
    )


def _required_radius_solver_failure_if_available(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
    r_in: float,
    r_out: float,
    barrier_action: float,
    bvp_failure_message: str,
    fallback_failure_message: str,
) -> RuntimeError | None:
    required_eval_radius = config.required_eval_radius
    if required_eval_radius is None:
        return None
    tail_domain = _evanescent_tail_domain(
        sector=sector,
        ell=ell,
        k=k,
        background=background,
        r_in=r_in,
        r_out=r_out,
    )
    if tail_domain is None:
        return None
    valid_until_r, local_tail_action = tail_domain
    if valid_until_r < float(required_eval_radius):
        return None
    return RuntimeError(
        _evanescent_tail_required_radius_solver_failure_message(
            sector=sector,
            ell=ell,
            k=k,
            barrier_action=barrier_action,
            valid_until_r=float(valid_until_r),
            local_tail_action=float(local_tail_action),
            required_eval_radius=float(required_eval_radius),
            bvp_failure_message=bvp_failure_message,
            fallback_failure_message=fallback_failure_message,
        )
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
        "precision_dps": int(oracle_diagnostics["precision_dps"]),
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


def _finite_complex_array(value: np.ndarray) -> bool:
    array = np.asarray(value)
    return bool(np.all(np.isfinite(array.real)) and np.all(np.isfinite(array.imag)))


def _radial_rhs(
    r: float,
    y: np.ndarray,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
) -> np.ndarray:
    psi, dpsi_dr = y
    f = background.f(r)
    df_dr = background.df_dr(r)
    potential = _potential(sector, ell, r, background)
    d2psi_dr2 = -(f * df_dr * dpsi_dr + (k**2 - potential) * psi) / f**2
    return np.array([dpsi_dr, d2psi_dr2], dtype=complex)


def _bvp_rhs(
    rstar: np.ndarray,
    y: np.ndarray,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
) -> np.ndarray:
    radius = background.r_from_r_star(rstar)
    psi = y[0] + 1j * y[1]
    dpsi_drstar = y[2] + 1j * y[3]
    potential = _potential(sector, ell, radius, background)
    d2psi_drstar2 = -(k**2 - potential) * psi
    return np.vstack(
        [
            dpsi_drstar.real,
            dpsi_drstar.imag,
            d2psi_drstar2.real,
            d2psi_drstar2.imag,
        ]
    )


def _bvp_boundary_residual(
    left: np.ndarray,
    right: np.ndarray,
    parameters: np.ndarray,
    k: float,
    rstar_out: float,
) -> np.ndarray:
    A_out = complex(parameters[0], parameters[1])
    left_psi = complex(left[0], left[1])
    left_dpsi_drstar = complex(left[2], left[3])
    ingoing_residual = left_dpsi_drstar + 1j * k * left_psi

    incoming = np.exp(-1j * k * rstar_out)
    outgoing = np.exp(1j * k * rstar_out)
    right_psi = complex(right[0], right[1])
    right_dpsi_drstar = complex(right[2], right[3])
    outer_psi_residual = right_psi - (incoming + A_out * outgoing)
    outer_derivative_residual = right_dpsi_drstar - (
        -1j * k * incoming + 1j * k * A_out * outgoing
    )
    return np.array(
        [
            ingoing_residual.real,
            ingoing_residual.imag,
            outer_psi_residual.real,
            outer_psi_residual.imag,
            outer_derivative_residual.real,
            outer_derivative_residual.imag,
        ]
    )


def _bvp_initial_guess(rstar_grid: np.ndarray, ell: int, k: float) -> np.ndarray:
    incoming = np.exp(-1j * k * rstar_grid)
    # A total-reflection guess is close to the high-ell tunneling regime and
    # also acceptable for moderate barriers; solve_bvp adjusts the phase.
    outgoing_coefficient = -float((-1) ** ell)
    psi = incoming + outgoing_coefficient * np.exp(1j * k * rstar_grid)
    dpsi_drstar = -1j * k * incoming + 1j * k * outgoing_coefficient * np.exp(
        1j * k * rstar_grid
    )
    return np.vstack([psi.real, psi.imag, dpsi_drstar.real, dpsi_drstar.imag])


def _bvp_boundary_norm(result, k: float, rstar_out: float) -> float:
    residual = _bvp_boundary_residual(
        result.y[:, 0],
        result.y[:, -1],
        result.p,
        k,
        rstar_out,
    )
    return float(np.linalg.norm(residual))


def _bvp_initial_mesh_size(barrier_action: float) -> int:
    return int(min(1200, max(400, 40 * max(barrier_action, 1.0))))


def _integrate_radial_basis(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
    r_start: float,
    r_stop: float,
    psi_start: complex,
    dpsi_dr_start: complex,
):
    solve_kwargs: dict[str, Any] = {
        "method": config.method,
        "rtol": config.rtol,
        "atol": config.atol,
        "dense_output": True,
    }
    if config.max_step is not None:
        solve_kwargs["max_step"] = config.max_step
    result = solve_ivp(
        lambda r, y: _radial_rhs(r, y, sector, ell, k, background),
        (r_start, r_stop),
        np.array([psi_start, dpsi_dr_start], dtype=complex),
        **solve_kwargs,
    )
    if not result.success:
        raise RuntimeError(f"Radial basis integration failed: {result.message}")
    return result


def _basis_state_at(result, radius: float) -> np.ndarray:
    values = result.sol(radius)
    return np.array([values[0], values[1]], dtype=complex)


def _bidirectional_match_radius(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    r_in: float,
    r_out: float,
) -> float:
    turning_points = _turning_points(
        sector=sector,
        ell=ell,
        k=k,
        background=background,
        r_in=r_in,
        r_out=r_out,
    )
    if turning_points:
        outer_turning = turning_points[-1]
        return float(np.clip(1.05 * outer_turning, r_in, r_out))

    radius_grid = np.linspace(r_in, r_out, 4096)
    peak_index = int(np.argmax(_potential(sector, ell, radius_grid, background)))
    return float(radius_grid[peak_index])


def _turning_points(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    r_in: float,
    r_out: float,
) -> list[float]:
    radius_grid = np.linspace(r_in, r_out, 4096)
    potential_offset = _potential(sector, ell, radius_grid, background) - k**2
    crossings = np.where(np.diff(np.signbit(potential_offset)))[0]
    turning_points = []
    for crossing in crossings:
        r_left = radius_grid[crossing]
        r_right = radius_grid[crossing + 1]
        v_left = potential_offset[crossing]
        v_right = potential_offset[crossing + 1]
        if v_right != v_left:
            root = r_left - v_left * (r_right - r_left) / (v_right - v_left)
        else:
            root = 0.5 * (r_left + r_right)
        turning_points.append(float(root))
    return turning_points


def _is_extreme_evanescent_tail(barrier_action: float) -> bool:
    return barrier_action >= _EVANESCENT_SUPPRESSION_BARRIER_ACTION


def _evanescent_tail_domain(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    r_in: float,
    r_out: float,
) -> tuple[float, float] | None:
    turning_points = _turning_points(
        sector=sector,
        ell=ell,
        k=k,
        background=background,
        r_in=r_in,
        r_out=r_out,
    )
    if len(turning_points) < 2:
        return None
    inner_turning, outer_turning = turning_points[0], turning_points[-1]
    rstar_grid = np.linspace(
        background.r_star(inner_turning), background.r_star(outer_turning), 8192
    )
    radius = np.asarray(background.r_from_r_star(rstar_grid), dtype=float)
    attenuation = np.sqrt(
        np.maximum(np.asarray(_potential(sector, ell, radius, background)) - k**2, 0.0)
    )
    drstar = np.diff(rstar_grid)
    segment_action = 0.5 * (attenuation[:-1] + attenuation[1:]) * drstar
    action_from_inner = np.concatenate([[0.0], np.cumsum(segment_action)])
    tail_action = action_from_inner[-1] - action_from_inner
    eligible = np.where(tail_action >= _EVANESCENT_SUPPRESSION_TAIL_ACTION)[0]
    if len(eligible) == 0:
        return None
    valid_index = int(eligible[-1])
    valid_until_r = float(radius[valid_index])
    if valid_until_r <= r_in:
        return None
    return valid_until_r, float(tail_action[valid_index])


def _bidirectional_match_residual(
    *,
    match_matrix: np.ndarray,
    coefficients: np.ndarray,
    rhs: np.ndarray,
) -> float:
    residual = match_matrix @ coefficients - rhs
    scale = max(
        float(np.linalg.norm(match_matrix @ coefficients)),
        float(np.linalg.norm(rhs)),
        np.finfo(float).eps,
    )
    return float(np.linalg.norm(residual) / scale)


def _bidirectional_match_jump(
    *,
    left_state: np.ndarray,
    right_state: np.ndarray,
) -> float:
    scale = max(
        float(np.linalg.norm(left_state)),
        float(np.linalg.norm(right_state)),
        np.finfo(float).eps,
    )
    return float(np.linalg.norm(left_state - right_state) / scale)


def _validate_bidirectional_match_inputs(
    *,
    sector: Sector,
    ell: int,
    k: float,
    match_radius: float,
    horizon_match: np.ndarray,
    incoming_match: np.ndarray,
    outgoing_match: np.ndarray,
    match_matrix: np.ndarray,
) -> None:
    finite_flags = {
        "horizon_match": _finite_complex_array(horizon_match),
        "incoming_match": _finite_complex_array(incoming_match),
        "outgoing_match": _finite_complex_array(outgoing_match),
        "match_matrix": _finite_complex_array(match_matrix),
    }
    if all(finite_flags.values()):
        return
    raise RuntimeError(
        "bidirectional radial matching produced non-finite match data "
        f"(sector={sector.value}, ell={ell}, k={k}, "
        f"match_radius={match_radius:.12g}, finite={finite_flags})"
    )


def _bvp_failure_message(
    *,
    sector: Sector,
    ell: int,
    k: float,
    r_out: float,
    barrier_action: float,
    mesh_size: int,
    result_message: str,
) -> str:
    return (
        "Stabilized radial BVP solve failed"
        f" (sector={sector.value}, ell={ell}, k={k}, r_out={r_out}, "
        f"barrier_action={barrier_action:.12g}, solver=bvp_unit_infinity, "
        f"initial_mesh={mesh_size}, max_nodes={_BVP_MAX_NODES}): "
        f"{result_message}"
    )


def _potential(
    sector: Sector,
    ell: int,
    r: float | np.ndarray,
    background: StaticSphericalBackground,
) -> float | np.ndarray:
    if sector is Sector.ODD:
        return V_RW(ell, r, background)
    return V_Zerilli(ell, r, background)


def _barrier_action(
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    r_in: float,
    r_out: float,
) -> float:
    rstar_grid = np.linspace(background.r_star(r_in), background.r_star(r_out), 2048)
    radius = background.r_from_r_star(rstar_grid)
    potential = _potential(sector, ell, radius, background)
    forbidden_wavenumber = np.sqrt(np.maximum(np.asarray(potential) - k**2, 0.0))
    return float(np.trapezoid(forbidden_wavenumber, rstar_grid))


def _requires_stabilized_solver(barrier_action: float) -> bool:
    return barrier_action > _BVP_BRANCH_BARRIER_ACTION


def _radial_diagnostic_warnings(
    *,
    sector: Sector,
    ell: int,
    k: float,
    solver: str,
    barrier_action: float,
    raw_wronskian_residual: float,
    effective_wronskian_residual: float,
    flux_residual: float,
    boundary_residual: float,
    expected_flux_scale: float,
    match_condition_number: float,
    psi: np.ndarray,
    dpsi_dr: np.ndarray,
) -> tuple[RadialDiagnosticWarning, ...]:
    sqrt_eps = np.sqrt(np.finfo(float).eps)
    is_transition = (
        _BVP_BRANCH_BARRIER_ACTION
        < barrier_action
        <= _BVP_BRANCH_BARRIER_ACTION + _TRANSITION_BARRIER_ACTION_WIDTH
    )
    flux_near_switch = (
        sqrt_eps
        < expected_flux_scale
        <= _TRANSITION_FLUX_SCALE_FACTOR * sqrt_eps
    )
    healthy_auxiliary_diagnostics = (
        boundary_residual < _HEALTHY_BOUNDARY_RESIDUAL
        and flux_residual < _FIRST_PASS_WRONSKIAN_TARGET
        and match_condition_number < _HEALTHY_MATCH_CONDITION_NUMBER
        and np.all(np.isfinite(psi.real))
        and np.all(np.isfinite(psi.imag))
        and np.all(np.isfinite(dpsi_dr.real))
        and np.all(np.isfinite(dpsi_dr.imag))
    )
    if not (
        solver == "bvp_unit_infinity"
        and raw_wronskian_residual > _FIRST_PASS_WRONSKIAN_TARGET
        and is_transition
        and flux_near_switch
        and healthy_auxiliary_diagnostics
    ):
        return ()

    return (
        RadialDiagnosticWarning(
            code="transition_raw_wronskian_warning",
            severity="warning",
            message=(
                "Raw Wronskian relative residual is above the first-pass target "
                "in a BVP transition mode whose horizon flux scale is near "
                "sqrt(eps), while boundary and collocation diagnostics remain healthy."
            ),
            sector=sector.value,
            ell=ell,
            k=float(k),
            solver=solver,
            barrier_action=float(barrier_action),
            raw_wronskian_residual=float(raw_wronskian_residual),
            effective_wronskian_residual=float(effective_wronskian_residual),
            flux_residual=float(flux_residual),
            boundary_residual=float(boundary_residual),
            expected_flux_scale=float(expected_flux_scale),
            match_condition_number=float(match_condition_number),
        ),
    )


def _wronskian_residual(
    psi: np.ndarray,
    dpsi_dr: np.ndarray,
    r_grid: np.ndarray,
    background: StaticSphericalBackground,
) -> float:
    f = background.f(r_grid)
    wronskian = f * (np.conjugate(psi) * dpsi_dr - psi * np.conjugate(dpsi_dr))
    reference = np.median(wronskian)
    denominator = max(float(abs(reference)), np.finfo(float).eps)
    return float(np.max(np.abs(wronskian - reference)) / denominator)


def _coerce_sector(sector: Sector | str) -> Sector:
    try:
        return sector if isinstance(sector, Sector) else Sector(sector)
    except ValueError as exc:
        raise ValueError("sector must be 'odd' or 'even'.") from exc


def _return_scalar_if_scalar_input(values: np.ndarray, original: ArrayLike) -> complex | np.ndarray:
    if np.isscalar(original) or np.asarray(original).ndim == 0:
        return complex(values)
    return values
