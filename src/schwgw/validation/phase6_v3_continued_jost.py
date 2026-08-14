"""V3.1-local deterministic continued-Jost coefficient extraction.

This module does not change the protected radial backend.  Each logical node
calls :func:`solve_scaled_tortoise_radial_at_radius` exactly once.  When the
frozen requested match radius is too close to the centrifugal turning scale,
the protected solve is initialized at a geometry-only auxiliary radius and
the same Jost columns are transported back to the requested radius.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp

from schwgw.backgrounds.base import StaticSphericalBackground
from schwgw.numerics.conditioned_radial import (
    ConditionedFiniteRadiusState,
    ConditionedRadialRequest,
)
from schwgw.numerics.matching import OuterBasisState, outer_asymptotic_basis
from schwgw.numerics.scaled_tortoise_radial import (
    solve_scaled_tortoise_radial_at_radius,
)
from schwgw.perturbations import Sector, V_RW, V_Zerilli


class ContinuedJostError(RuntimeError):
    """The frozen continued-Jost node could not be evaluated."""


@dataclass(frozen=True)
class ContinuedJostGeometry:
    requested_match_radius: float
    jost_initialization_radius: float
    auxiliary_exponent: int


@dataclass(frozen=True)
class _ScaledColumn:
    psi: complex
    momentum: complex
    log_scale: float
    rhs_evaluations: int
    segment_count: int
    maximum_current_relative_drift: float


def continued_jost_geometry(
    *, ell: int, k: float, r_match: float
) -> ContinuedJostGeometry:
    """Return the unique frozen geometry-only auxiliary-radius decision."""

    if ell < 2 or not math.isfinite(k) or k <= 0.0:
        raise ValueError("invalid continued-Jost mode")
    if not math.isfinite(r_match) or r_match <= 2.0:
        raise ValueError("invalid requested match radius")
    threshold = 4.0 * math.sqrt(ell * (ell + 1))
    candidates = [
        n
        for n in (0, 1, 2)
        if k * (2**n * r_match) >= threshold
        or math.isclose(
            k * (2**n * r_match), threshold, rel_tol=8 * math.ulp(1.0), abs_tol=0.0
        )
    ]
    if not candidates:
        raise ContinuedJostError("frozen auxiliary-radius domain is empty")
    exponent = candidates[0]
    return ContinuedJostGeometry(
        requested_match_radius=float(r_match),
        jost_initialization_radius=float((2**exponent) * r_match),
        auxiliary_exponent=exponent,
    )


def solve_continued_jost_node(
    request: ConditionedRadialRequest,
    background: StaticSphericalBackground,
    *,
    shadow_auxiliary_exponent: int | None = None,
) -> dict[str, Any]:
    """Evaluate one frozen Route-A node through the protected public solver.

    ``shadow_auxiliary_exponent`` is permitted only for the predeclared
    direct-versus-shadow diagnostic.  Production callers leave it ``None``.
    """

    geometry = continued_jost_geometry(
        ell=request.ell,
        k=request.k,
        r_match=float(request.r_out),
    )
    if shadow_auxiliary_exponent is not None:
        if geometry.auxiliary_exponent != 0 or shadow_auxiliary_exponent != 1:
            raise ValueError(
                "shadow continuation is only the frozen n_aux=0 -> 1 check"
            )
        geometry = ContinuedJostGeometry(
            requested_match_radius=geometry.requested_match_radius,
            jost_initialization_radius=2.0 * geometry.requested_match_radius,
            auxiliary_exponent=1,
        )
    if geometry.auxiliary_exponent == 0:
        protected = solve_scaled_tortoise_radial_at_radius(request, background)
        return _direct_record(request=request, geometry=geometry, protected=protected)

    auxiliary_request = replace(
        request,
        r_out=geometry.jost_initialization_radius,
        evaluation_radii=tuple(
            sorted({*request.evaluation_radii, geometry.requested_match_radius})
        ),
    )
    protected = solve_scaled_tortoise_radial_at_radius(auxiliary_request, background)
    match_state = _unique_state_at_radius(
        protected.finite_radius_states,
        geometry.requested_match_radius,
    )
    lapse_match = float(background.f(geometry.requested_match_radius))
    physical_psi, physical_momentum, physical_log_scale = _scaled_physical_state(
        match_state,
        lapse=lapse_match,
    )

    incoming_aux = _protected_basis(request, background, geometry, sign=-1)
    outgoing_aux = _protected_basis(request, background, geometry, sign=1)
    incoming = _continue_column(
        basis=incoming_aux,
        request=request,
        background=background,
        r_start=geometry.jost_initialization_radius,
        r_target=geometry.requested_match_radius,
    )
    outgoing = _continue_column(
        basis=outgoing_aux,
        request=request,
        background=background,
        r_start=geometry.jost_initialization_radius,
        r_target=geometry.requested_match_radius,
    )
    matrix = np.asarray(
        [[incoming.psi, outgoing.psi], [incoming.momentum, outgoing.momentum]],
        dtype=np.complex128,
    )
    rhs = np.asarray([physical_psi, physical_momentum], dtype=np.complex128)
    if not np.all(np.isfinite(matrix)) or not np.all(np.isfinite(rhs)):
        raise ContinuedJostError("continued-Jost matching inputs are non-finite")
    determinant = complex(np.linalg.det(matrix))
    determinant_scale = max(
        abs(matrix[0, 0] * matrix[1, 1]) + abs(matrix[0, 1] * matrix[1, 0]),
        np.finfo(float).tiny,
    )
    if abs(determinant) <= np.finfo(float).eps * determinant_scale:
        raise ContinuedJostError("continued-Jost matching matrix is singular")
    try:
        c_in, c_out = np.linalg.solve(matrix, rhs)
    except np.linalg.LinAlgError as exc:
        raise ContinuedJostError("continued-Jost exact solve failed") from exc
    if not _finite_complex(c_in) or not _finite_complex(c_out) or c_in == 0:
        raise ContinuedJostError("continued-Jost coefficients are invalid")

    log_abs_a_in = math.log(abs(c_in)) + physical_log_scale - incoming.log_scale
    log_abs_a_out = math.log(abs(c_out)) + physical_log_scale - outgoing.log_scale
    phase_a_in = _principal_phase(float(np.angle(c_in)))
    phase_a_out = _principal_phase(float(np.angle(c_out)))
    log_abs_reflection = log_abs_a_out - log_abs_a_in
    phase_reflection = _principal_phase(phase_a_out - phase_a_in)
    reflection = _finite_complex_from_log(log_abs_reflection, phase_reflection)
    log_abs_t = float(protected.log_abs_T_horizon) - log_abs_a_in
    phase_t = _principal_phase(float(protected.phase_T_horizon) - phase_a_in)
    transmission = _compatibility_complex_from_log(log_abs_t, phase_t)
    reconstructed = matrix @ np.asarray([c_in, c_out], dtype=np.complex128)
    match_residual = float(
        np.linalg.norm(reconstructed - rhs)
        / max(np.linalg.norm(rhs), np.finfo(float).tiny)
    )
    condition = float(np.linalg.cond(matrix))
    column_wronskian = (
        incoming.psi * outgoing.momentum - incoming.momentum * outgoing.psi
    )
    conjugacy_value = float(
        abs(outgoing.psi - np.conj(incoming.psi))
        / max(abs(outgoing.psi), abs(incoming.psi), np.finfo(float).tiny)
    )
    conjugacy_derivative = float(
        abs(outgoing.momentum - np.conj(incoming.momentum))
        / max(abs(outgoing.momentum), abs(incoming.momentum), np.finfo(float).tiny)
    )
    return _physical_record(
        request=request,
        geometry=geometry,
        reflection=reflection,
        log_abs_reflection=log_abs_reflection,
        phase_reflection=phase_reflection,
        log_abs_t=log_abs_t,
        phase_t=phase_t,
        transmission=transmission,
        protected=protected,
        diagnostics={
            "algorithm": "v3_local_numerically_continued_jost_matching",
            "protected_route_a_call_count": 1,
            "final_match_at_requested_radius": True,
            "match_residual": match_residual,
            "match_condition_number": condition,
            "basis_determinant_abs": float(abs(determinant)),
            "column_wronskian_abs": float(abs(column_wronskian)),
            "conjugacy_value_residual": conjugacy_value,
            "conjugacy_derivative_residual": conjugacy_derivative,
            "incoming_basis_series_residual": float(incoming_aux.series_residual),
            "outgoing_basis_series_residual": float(outgoing_aux.series_residual),
            "incoming_basis_tail_ratio": float(incoming_aux.tail_ratio),
            "outgoing_basis_tail_ratio": float(outgoing_aux.tail_ratio),
            "incoming_column_log_scale": incoming.log_scale,
            "outgoing_column_log_scale": outgoing.log_scale,
            "physical_state_log_scale": physical_log_scale,
            "incoming_column_current_drift": incoming.maximum_current_relative_drift,
            "outgoing_column_current_drift": outgoing.maximum_current_relative_drift,
            "continued_rhs_evaluations": incoming.rhs_evaluations
            + outgoing.rhs_evaluations,
            "continued_segment_count": incoming.segment_count + outgoing.segment_count,
            "raw_c_in": _complex_record(c_in),
            "raw_c_out": _complex_record(c_out),
            "log_abs_a_in": log_abs_a_in,
            "arg_a_in": phase_a_in,
            "log_abs_a_out": log_abs_a_out,
            "arg_a_out": phase_a_out,
        },
    )


def _protected_basis(
    request: ConditionedRadialRequest,
    background: StaticSphericalBackground,
    geometry: ContinuedJostGeometry,
    *,
    sign: int,
) -> OuterBasisState:
    return outer_asymptotic_basis(
        sector=request.sector,
        ell=request.ell,
        r=geometry.jost_initialization_radius,
        k=request.k,
        background=background,
        sign=sign,
        basis=request.outer_basis,
        series_order=request.outer_series_order,
    )


def _continue_column(
    *,
    basis: OuterBasisState,
    request: ConditionedRadialRequest,
    background: StaticSphericalBackground,
    r_start: float,
    r_target: float,
) -> _ScaledColumn:
    lapse_start = float(background.f(r_start))
    state = np.asarray([basis.psi, lapse_start * basis.dpsi_dr], dtype=np.complex128)
    initial_scale = float(max(abs(state[0]), abs(state[1])))
    if not math.isfinite(initial_scale) or initial_scale <= np.finfo(float).tiny:
        raise ContinuedJostError("continued-Jost initial column is unresolved")
    state /= initial_scale
    log_scale = math.log(initial_scale)
    rstar = float(background.r_star(r_start))
    target_rstar = float(background.r_star(r_target))
    if not target_rstar < rstar:
        raise ContinuedJostError("continued-Jost direction is not inward")
    initial_current = float(np.imag(np.conj(state[0]) * state[1]))
    rhs_evaluations = 0
    segments = 0
    maximum_drift = 0.0

    def rhs(current_rstar: float, current: np.ndarray) -> np.ndarray:
        radius = float(background.r_from_r_star(current_rstar))
        potential = float(_potential(request.sector, request.ell, radius, background))
        return np.asarray([current[1], (potential - request.k**2) * current[0]])

    while rstar > target_rstar:
        endpoint = max(target_rstar, rstar - 4.0)
        segment = solve_ivp(
            rhs,
            (rstar, endpoint),
            state,
            method="DOP853",
            rtol=request.rtol,
            atol=request.atol,
            t_eval=np.asarray([endpoint]),
        )
        rhs_evaluations += int(segment.nfev)
        segments += 1
        if not segment.success or segment.y.shape != (2, 1):
            raise ContinuedJostError(
                f"continued-Jost propagation failed: {segment.message}"
            )
        state = np.asarray(segment.y[:, -1], dtype=np.complex128)
        if not np.all(np.isfinite(state)):
            raise ContinuedJostError("continued-Jost column became non-finite")
        scale = float(max(abs(state[0]), abs(state[1])))
        if not math.isfinite(scale) or scale <= np.finfo(float).tiny:
            raise ContinuedJostError("continued-Jost column rescaling failed")
        state /= scale
        log_scale += math.log(scale)
        current = float(np.imag(np.conj(state[0]) * state[1]))
        if initial_current != 0.0 and current != 0.0:
            log_ratio = (
                math.log(abs(current))
                + 2.0 * log_scale
                - (math.log(abs(initial_current)) + 2.0 * math.log(initial_scale))
            )
            if abs(log_ratio) < 700.0:
                maximum_drift = max(maximum_drift, abs(math.expm1(log_ratio)))
        rstar = endpoint
    return _ScaledColumn(
        psi=complex(state[0]),
        momentum=complex(state[1]),
        log_scale=log_scale,
        rhs_evaluations=rhs_evaluations,
        segment_count=segments,
        maximum_current_relative_drift=maximum_drift,
    )


def _direct_record(
    *,
    request: ConditionedRadialRequest,
    geometry: ContinuedJostGeometry,
    protected: Any,
) -> dict[str, Any]:
    reflection = complex(protected.A_out)
    log_abs_reflection = math.log(abs(reflection))
    phase_reflection = _principal_phase(float(np.angle(reflection)))
    return _physical_record(
        request=request,
        geometry=geometry,
        reflection=reflection,
        log_abs_reflection=log_abs_reflection,
        phase_reflection=phase_reflection,
        log_abs_t=float(protected.log_abs_T_horizon),
        phase_t=float(protected.phase_T_horizon),
        transmission=complex(protected.T_horizon),
        protected=protected,
        diagnostics={
            "algorithm": "protected_scaled_tortoise_direct",
            "protected_route_a_call_count": 1,
            "final_match_at_requested_radius": True,
            "match_residual": float(protected.diagnostics["outer_boundary_residual"]),
            "match_condition_number": float(
                protected.diagnostics["match_condition_number"]
            ),
        },
    )


def _physical_record(
    *,
    request: ConditionedRadialRequest,
    geometry: ContinuedJostGeometry,
    reflection: complex,
    log_abs_reflection: float,
    phase_reflection: float,
    log_abs_t: float,
    phase_t: float,
    transmission: complex,
    protected: Any,
    diagnostics: dict[str, Any],
) -> dict[str, Any]:
    s_factor = (-1) ** (request.ell + 1)
    s_value = complex(s_factor * reflection)
    phase_s = _principal_phase(phase_reflection + (0.0 if s_factor == 1 else math.pi))
    log_gamma_flux = 2.0 * log_abs_t
    gamma_flux = _compatibility_positive_from_log(log_gamma_flux)
    gamma_s = float(-math.expm1(2.0 * log_abs_reflection))
    omega = float(request.k)
    f_in = omega
    f_out = omega * math.exp(
        min(2.0 * log_abs_reflection, math.log(np.finfo(float).max))
    )
    f_h = omega * gamma_flux
    return {
        "schema": "schwo.phase6.v3_1.continued_jost_node.v1",
        "sector": request.sector.value,
        "ell": request.ell,
        "kM": format(request.k, ".17g"),
        "requested_match_radius": geometry.requested_match_radius,
        "jost_initialization_radius": geometry.jost_initialization_radius,
        "auxiliary_exponent": geometry.auxiliary_exponent,
        "r_in_eps": request.r_in_eps,
        "rtol": request.rtol,
        "atol": request.atol,
        "jost_order": request.outer_series_order,
        "A_in": _complex_record(1.0 + 0.0j),
        "A_out": _complex_record(reflection),
        "S": _complex_record(s_value),
        "log_abs_S": log_abs_reflection,
        "phase_S": phase_s,
        "T_horizon": _complex_record(transmission),
        "log_abs_T_horizon": log_abs_t,
        "phase_T_horizon": phase_t,
        "signed_currents": {"j_in": -f_in, "j_out": f_out, "j_H": -f_h},
        "positive_fluxes": {"F_in": f_in, "F_out": f_out, "F_H": f_h},
        "log_Gamma_flux": log_gamma_flux,
        "Gamma_flux": gamma_flux,
        "Gamma_flux_decimal": _arbitrary_exponent_decimal(log_gamma_flux),
        "Gamma_S": gamma_s,
        "flux_balance_residual": abs(f_in - f_out - f_h) / f_in,
        "protected_result": {
            "log_abs_T_horizon": float(protected.log_abs_T_horizon),
            "phase_T_horizon": float(protected.phase_T_horizon),
            "r_out": float(protected.diagnostics["r_out"]),
            "backend": protected.diagnostics["backend"],
        },
        "diagnostics": diagnostics,
    }


def _scaled_physical_state(
    state: ConditionedFiniteRadiusState, *, lapse: float
) -> tuple[complex, complex, float]:
    log_psi = float(state.log_abs_psi)
    log_momentum = float(state.log_abs_dpsi_dr) + math.log(lapse)
    scale = max(log_psi, log_momentum)
    psi = complex(math.exp(log_psi - scale) * np.exp(1j * state.phase_psi))
    momentum = complex(
        math.exp(log_momentum - scale) * np.exp(1j * state.phase_dpsi_dr)
    )
    if not _finite_complex(psi) or not _finite_complex(momentum):
        raise ContinuedJostError("continued-Jost physical match state is invalid")
    return psi, momentum, scale


def _unique_state_at_radius(
    states: tuple[ConditionedFiniteRadiusState, ...], radius: float
) -> ConditionedFiniteRadiusState:
    selected = [state for state in states if state.radius == radius]
    if len(selected) != 1:
        raise ContinuedJostError("requested-radius protected state is not unique")
    return selected[0]


def _potential(
    sector: Sector, ell: int, radius: float, background: StaticSphericalBackground
) -> float:
    return float(
        V_RW(ell, radius, background)
        if sector is Sector.ODD
        else V_Zerilli(ell, radius, background)
    )


def _complex_record(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag)}


def _arbitrary_exponent_decimal(log_value: float) -> dict[str, Any]:
    exponent = math.floor(log_value / math.log(10.0))
    mantissa = math.exp(log_value - exponent * math.log(10.0))
    return {"mantissa": format(mantissa, ".17g"), "exponent10": int(exponent)}


def _compatibility_positive_from_log(log_value: float) -> float:
    if log_value < math.log(float(np.nextafter(0.0, 1.0))):
        return 0.0
    return float(math.exp(log_value))


def _compatibility_complex_from_log(log_abs: float, phase: float) -> complex:
    if log_abs < math.log(float(np.nextafter(0.0, 1.0))):
        return 0.0j
    return _finite_complex_from_log(log_abs, phase)


def _finite_complex_from_log(log_abs: float, phase: float) -> complex:
    value = complex(math.exp(log_abs) * np.exp(1j * phase))
    if not _finite_complex(value):
        raise ContinuedJostError("continued-Jost normalized complex is non-finite")
    return value


def _principal_phase(value: float) -> float:
    return float(np.angle(np.exp(1j * value)))


def _finite_complex(value: complex) -> bool:
    return bool(np.isfinite(value.real) and np.isfinite(value.imag))


__all__ = [
    "ContinuedJostError",
    "ContinuedJostGeometry",
    "continued_jost_geometry",
    "solve_continued_jost_node",
]
