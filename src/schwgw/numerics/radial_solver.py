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
from schwgw.numerics.matching import (
    match_outer_asymptotic,
    outer_asymptotic_basis,
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
_CONDITIONED_LOCAL_GRID_STEP = 1e-6


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
    outer_basis: str = "jost_1_over_r"
    outer_series_order: int = 160


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
    if config.conditioning_backend is not None:
        force_conditioned = config.conditioning_backend == "scaled_log_riccati_forced"
        if force_conditioned or _requires_stabilized_solver(barrier_action):
            return _solve_radial_mode_conditioned(
                sector=sector_enum,
                ell=ell,
                k=k,
                background=background,
                config=config,
                r_in=r_in,
                r_out=r_out,
                barrier_action=barrier_action,
                selector=(
                    "explicit_forced"
                    if force_conditioned
                    else "pre_solve_barrier_action_threshold"
                ),
            )
    oracle_name = config.experimental_required_radius_oracle
    if oracle_name is not None:
        from schwgw.numerics.legacy.paper_oracles import (
            validate_legacy_oracle_request,
        )

        validate_legacy_oracle_request(
            sector=sector_enum,
            ell=ell,
            k=k,
            background=background,
            config=config,
            r_out=r_out,
            barrier_action=barrier_action,
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
        if oracle_name is not None and _is_required_radius_oracle_recoverable_error(
            exc
        ):
            from schwgw.numerics.legacy.paper_oracles import (
                solve_legacy_required_radius_oracle,
            )

            return solve_legacy_required_radius_oracle(
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


def _solve_radial_mode_conditioned(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
    r_in: float,
    r_out: float,
    barrier_action: float,
    selector: str,
) -> RadialSolution:
    """Adapt the generic scaled/log backend to the finite-radius public API."""

    from schwgw.numerics.conditioned_radial import (
        ConditionedRadialRequest,
        solve_conditioned_radial_at_radius,
    )

    if config.required_eval_radius is None:
        raise ValueError("generic conditioned backend requires required_eval_radius")
    required_radius = float(config.required_eval_radius)
    request = ConditionedRadialRequest(
        sector=sector,
        ell=ell,
        k=float(k),
        required_radius=required_radius,
        r_out=float(r_out),
        r_in_eps=float(config.r_in_eps),
        rtol=float(config.rtol),
        atol=float(config.atol),
        outer_basis=config.outer_basis,
        outer_series_order=config.outer_series_order,
    )
    result = solve_conditioned_radial_at_radius(request, background)
    evidence = dict(result.diagnostics)
    boundary_residual = _diagnostic_float(evidence, "outer_boundary_residual")
    condition_number = _diagnostic_float(evidence, "match_condition_number")
    state_status = str(evidence["complex_state_status"])
    derivative_status = str(evidence["complex_derivative_status"])
    local_step = min(
        _CONDITIONED_LOCAL_GRID_STEP,
        0.5 * (r_out - required_radius),
    )
    if local_step <= 0.0:
        raise RuntimeError("conditioned local compatibility grid is empty")
    r_grid = np.array([required_radius, required_radius + local_step], dtype=float)
    allowed_statuses = {"FINITE_COMPLEX", "LOG_SCALED_UNDERFLOW"}
    if state_status not in allowed_statuses or derivative_status not in allowed_statuses:
        raise RuntimeError(
            "conditioned backend returned incompatible complex-state statuses"
        )
    psi = np.array(
        [result.psi, result.psi + result.dpsi_dr * local_step],
        dtype=complex,
    )
    dpsi_dr = np.array([result.dpsi_dr, result.dpsi_dr], dtype=complex)

    phase_factor = -result.A_out / (((-1) ** ell) * result.A_in)
    selector_description = (
        "caller explicitly forced the generic backend"
        if selector == "explicit_forced"
        else (
            f"pre-solve barrier_action >= {_BVP_BRANCH_BARRIER_ACTION}; "
            "no frequency, radius-grid point, figure, or paper-specific key was used"
        )
    )
    metadata: dict[str, str | int | float | bool] = {
        "conditioning_backend": str(config.conditioning_backend),
        "conditioning_selector": selector,
        "conditioning_selector_description": selector_description,
        "paper_specific_envelope_used": False,
        "physical_claim": False,
        "scientific_acceptance": False,
        "required_eval_radius": required_radius,
        "r_in_eps": float(config.r_in_eps),
        "r_out": float(r_out),
        "rtol": float(config.rtol),
        "atol": float(config.atol),
        "outer_basis": config.outer_basis,
        "outer_series_order": int(config.outer_series_order),
        "actual_precision_bits": int(evidence["actual_precision_bits"]),
        "actual_decimal_digits": float(evidence["actual_decimal_digits"]),
        "complex_state_status": state_status,
        "complex_derivative_status": derivative_status,
        "log_abs_psi": float(result.log_abs_psi),
        "phase_psi": float(result.phase_psi),
        "log_abs_dpsi_dr": float(result.log_abs_dpsi_dr),
        "phase_dpsi_dr": float(result.phase_dpsi_dr),
        "T_horizon_real": float(result.T_horizon.real),
        "T_horizon_imag": float(result.T_horizon.imag),
        "log_abs_T_horizon": float(result.log_abs_T_horizon),
        "phase_T_horizon": float(result.phase_T_horizon),
        "complex_transmission_status": str(
            evidence["complex_transmission_status"]
        ),
        "reflection_probability": float(evidence["reflection_probability"]),
        "horizon_transmission_probability": float(
            evidence["horizon_transmission_probability"]
        ),
        "flux_balance": float(evidence["flux_balance"]),
        "horizon_flux_resolved": True,
        "wronskian_residual_available": False,
        "flux_residual_available": True,
        "unavailable_wronskian_residual_sentinel": 1.0,
        "unit_incoming_at_infinity": True,
    }
    warning = RadialDiagnosticWarning(
        code="generic_conditioned_radial_backend_used",
        severity="warning",
        message=(
            "Paper-independent scaled/log Riccati backend returned a state "
            "qualified only at required_eval_radius. Its internal horizon-flux "
            "accounting still requires independent precision ladders before "
            "scientific acceptance."
        ),
        sector=sector.value,
        ell=ell,
        k=float(k),
        solver="conditioned_scaled_log_riccati",
        barrier_action=float(barrier_action),
        raw_wronskian_residual=1.0,
        effective_wronskian_residual=float(evidence["flux_residual"]),
        flux_residual=float(evidence["flux_residual"]),
        boundary_residual=boundary_residual,
        expected_flux_scale=0.0,
        match_condition_number=condition_number,
        valid_until_r=required_radius,
        required_eval_radius=required_radius,
        required_eval_radius_covered=True,
        no_go_reason=(
            "finite-radius state, S ratio, and internal horizon-flux accounting "
            "available; physical acceptance is not supplied without independent "
            "precision and backend ladders"
        ),
        metadata=metadata,
    )
    diagnostics = RadialDiagnostics(
        boundary_residual=boundary_residual,
        wronskian_residual=1.0,
        flux_residual=float(evidence["flux_residual"]),
        ode_n_steps=int(evidence["rhs_evaluations"]),
        ode_status=(
            "generic conditioned scaled/log backend; "
            f"selector={selector}; state={state_status}"
        ),
        r_in=r_in,
        r_out=r_out,
        atol=config.atol,
        rtol=config.rtol,
        match_condition_number=condition_number,
        solver="conditioned_scaled_log_riccati",
        barrier_action=barrier_action,
        raw_wronskian_residual=1.0,
        expected_flux_scale=0.0,
        warnings=(warning,),
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
        A_in=complex(result.A_in),
        A_out=complex(result.A_out),
        phase_factor=complex(phase_factor),
        phase_shift=complex(-0.5j * np.log(phase_factor)),
        diagnostics=diagnostics,
        background=background,
        valid_until_r=required_radius,
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
        sector=sector,
        ell=ell,
        basis=config.outer_basis,
        series_order=config.outer_series_order,
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
    incoming_basis = outer_asymptotic_basis(
        sector=sector,
        ell=ell,
        r=r_out,
        k=k,
        background=background,
        sign=-1,
        basis=config.outer_basis,
        series_order=config.outer_series_order,
    )
    outgoing_basis = outer_asymptotic_basis(
        sector=sector,
        ell=ell,
        r=r_out,
        k=k,
        background=background,
        sign=1,
        basis=config.outer_basis,
        series_order=config.outer_series_order,
    )
    f_out = float(background.f(r_out))
    incoming_dpsi_drstar = f_out * incoming_basis.dpsi_dr
    outgoing_dpsi_drstar = f_out * outgoing_basis.dpsi_dr
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
            incoming_basis.psi,
            incoming_dpsi_drstar,
            outgoing_basis.psi,
            outgoing_dpsi_drstar,
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
        sector=sector,
        ell=ell,
        basis=config.outer_basis,
        series_order=config.outer_series_order,
    )
    boundary_residual = max(
        boundary_residual,
        _bvp_boundary_norm(
            result,
            k,
            incoming_basis.psi,
            incoming_dpsi_drstar,
            outgoing_basis.psi,
            outgoing_dpsi_drstar,
        ),
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

    incoming_basis = outer_asymptotic_basis(
        sector=sector,
        ell=ell,
        r=r_out,
        k=k,
        background=background,
        sign=-1,
        basis=config.outer_basis,
        series_order=config.outer_series_order,
    )
    outgoing_basis = outer_asymptotic_basis(
        sector=sector,
        ell=ell,
        r=r_out,
        k=k,
        background=background,
        sign=1,
        basis=config.outer_basis,
        series_order=config.outer_series_order,
    )
    incoming = _integrate_radial_basis(
        sector=sector,
        ell=ell,
        k=k,
        background=background,
        config=config,
        r_start=r_out,
        r_stop=match_radius,
        psi_start=incoming_basis.psi,
        dpsi_dr_start=incoming_basis.dpsi_dr,
    )
    outgoing = _integrate_radial_basis(
        sector=sector,
        ell=ell,
        k=k,
        background=background,
        config=config,
        r_start=r_out,
        r_stop=match_radius,
        psi_start=outgoing_basis.psi,
        dpsi_dr_start=outgoing_basis.dpsi_dr,
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
        sector=sector,
        ell=ell,
        basis=config.outer_basis,
        series_order=config.outer_series_order,
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


def _diagnostic_float(
    diagnostics: Mapping[str, object],
    key: str,
) -> float:
    value = float(diagnostics[key])
    if not np.isfinite(value):
        raise RuntimeError(f"radial backend diagnostic {key!r} is non-finite.")
    return value


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
    incoming: complex,
    incoming_dpsi_drstar: complex,
    outgoing: complex,
    outgoing_dpsi_drstar: complex,
) -> np.ndarray:
    A_out = complex(parameters[0], parameters[1])
    left_psi = complex(left[0], left[1])
    left_dpsi_drstar = complex(left[2], left[3])
    ingoing_residual = left_dpsi_drstar + 1j * k * left_psi

    right_psi = complex(right[0], right[1])
    right_dpsi_drstar = complex(right[2], right[3])
    outer_psi_residual = right_psi - (incoming + A_out * outgoing)
    outer_derivative_residual = right_dpsi_drstar - (
        incoming_dpsi_drstar + A_out * outgoing_dpsi_drstar
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


def _bvp_boundary_norm(
    result,
    k: float,
    incoming: complex,
    incoming_dpsi_drstar: complex,
    outgoing: complex,
    outgoing_dpsi_drstar: complex,
) -> float:
    residual = _bvp_boundary_residual(
        result.y[:, 0],
        result.y[:, -1],
        result.p,
        k,
        incoming,
        incoming_dpsi_drstar,
        outgoing,
        outgoing_dpsi_drstar,
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
