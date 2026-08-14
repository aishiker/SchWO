"""Pole-safe float64 Schwarzschild radial propagation in tortoise coordinate.

This module is a fresh Phase-6 V1 radial-repair backend.  It deliberately does not
modify :mod:`schwgw.numerics.conditioned_radial`, whose exact bytes are bound
into the immutable V1 campaign evidence.

The V1 backend evolves the logarithmic derivative ``psi'/psi`` and therefore
can encounter a projective-coordinate pole after the conserved imaginary
part falls below float64 resolution in a forbidden region.  Here the complete
complex state ``(psi, dpsi/dr_*)`` is evolved instead.  Short tortoise-coordinate
segments are followed by positive-real rescaling, so neither a zero of one
state component nor exponential barrier growth creates a Riccati pole.  The
positive rescalings are accumulated logarithmically and cannot change phase.

This is a same-equation, same-Jost-basis numerical repair, not an independent
scientific validator.  Results retain ``scientific_acceptance=False`` until
they are compared with an arbitrary-precision or external implementation and
their numerical and convention ladders are closed.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from time import perf_counter
import numpy as np
from scipy.integrate import solve_ivp

from schwgw.backgrounds.base import StaticSphericalBackground
from schwgw.numerics.conditioned_radial import (
    ConditionedFiniteRadiusState,
    ConditionedRadialRequest,
    ConditionedRadialResult,
)
from schwgw.numerics.matching import outer_asymptotic_basis
from schwgw.perturbations import Sector, V_RW, V_Zerilli

DiagnosticValue = bool | int | float | str

_MAX_TORTOISE_CHUNK = 4.0
_MAX_FORBIDDEN_LOG_GROWTH_PER_SEGMENT = 24.0
_ENDPOINT_ULPS = 8.0


@dataclass(frozen=True)
class _ScaledCheckpoint:
    radius: float
    psi_scaled: complex
    dpsi_dr_scaled: complex
    accumulated_log_scale: float


@dataclass(frozen=True)
class _ScaledTrajectory:
    checkpoints: tuple[_ScaledCheckpoint, ...]
    psi_outer_scaled: complex
    dpsi_dr_outer_scaled: complex
    accumulated_log_scale: float
    rhs_evaluations: int
    segment_count: int
    rstar_start: float
    rstar_end: float
    maximum_current_relative_drift: float
    current_drift_resolved: bool
    unresolved_current_segment_count: int
    minimum_segment_rstar: float
    maximum_segment_rstar: float


def solve_scaled_tortoise_radial_at_radius(
    request: ConditionedRadialRequest,
    background: StaticSphericalBackground,
) -> ConditionedRadialResult:
    """Return a unit-incoming state using pole-safe scaled full-state evolution.

    The horizon-normalized state starts as
    ``psi=exp(-i k r_*), dpsi/dr_*=-i k psi`` at the requested near-horizon
    radius.  It is propagated once to every requested finite radius and to
    ``r_out``.  At ``r_out`` an exact column-scaled 2x2 solve against the
    frozen Jost basis gives ``A_out/A_in`` without a pseudoinverse.
    """

    if not isinstance(request, ConditionedRadialRequest):
        raise TypeError("request must be a ConditionedRadialRequest.")
    if background.horizon_radius >= request.required_radius:
        raise ValueError("required_radius must be outside the background horizon.")
    if request.required_radius >= request.r_out:
        raise ValueError("required_radius must be strictly smaller than r_out.")

    started_at = perf_counter()
    r_in = float(background.horizon_radius * (1.0 + request.r_in_eps))
    finite_radii = tuple(
        sorted({float(request.required_radius), *request.evaluation_radii})
    )
    trajectory = _scaled_tortoise_trajectory(
        request=request,
        background=background,
        r_in=r_in,
        finite_radii=finite_radii,
    )

    incoming = outer_asymptotic_basis(
        sector=request.sector,
        ell=request.ell,
        r=float(request.r_out),
        k=request.k,
        background=background,
        sign=-1,
        basis=request.outer_basis,
        series_order=request.outer_series_order,
    )
    outgoing = outer_asymptotic_basis(
        sector=request.sector,
        ell=request.ell,
        r=float(request.r_out),
        k=request.k,
        background=background,
        sign=1,
        basis=request.outer_basis,
        series_order=request.outer_series_order,
    )
    basis_matrix = np.array(
        [
            [incoming.psi, outgoing.psi],
            [incoming.dpsi_dr, outgoing.dpsi_dr],
        ],
        dtype=np.complex128,
    )
    outer_state = np.array(
        [trajectory.psi_outer_scaled, trajectory.dpsi_dr_outer_scaled],
        dtype=np.complex128,
    )
    incoming_coefficient, outgoing_coefficient = _scaled_two_by_two_solve(
        basis_matrix,
        outer_state,
    )
    coefficient_floor = np.finfo(float).eps * max(
        abs(outgoing_coefficient),
        1.0,
    )
    if abs(incoming_coefficient) <= coefficient_floor:
        raise RuntimeError("scaled-tortoise incoming Jost coefficient is unresolved")

    reflection_ratio = outgoing_coefficient / incoming_coefficient
    log_abs_A_in_horizon_normalized = trajectory.accumulated_log_scale + math.log(
        abs(incoming_coefficient)
    )
    phase_A_in_horizon_normalized = float(np.angle(incoming_coefficient))
    log_abs_T_horizon = -log_abs_A_in_horizon_normalized
    phase_T_horizon = _principal_phase(-phase_A_in_horizon_normalized)
    T_horizon, transmission_status = _complex_from_log(
        log_abs_T_horizon,
        phase_T_horizon,
    )

    finite_radius_states = tuple(
        _unit_incoming_checkpoint_state(
            checkpoint,
            incoming_coefficient=incoming_coefficient,
            outer_log_scale=trajectory.accumulated_log_scale,
        )
        for checkpoint in trajectory.checkpoints
    )
    if not finite_radius_states or finite_radius_states[0].radius != float(
        request.required_radius
    ):
        raise RuntimeError("scaled-tortoise primary checkpoint ordering changed")
    primary_state = finite_radius_states[0]

    A_in = 1.0 + 0.0j
    A_out = complex(reflection_ratio)
    transmission_probability = _probability_from_log(log_abs_T_horizon)
    reflection_probability = float(abs(A_out) ** 2)
    flux_balance = reflection_probability + transmission_probability
    flux_residual = float(abs(flux_balance - 1.0))
    transmission_resolved = bool(transmission_probability > np.finfo(float).eps)

    reconstructed_state = basis_matrix @ np.array(
        [incoming_coefficient, outgoing_coefficient],
        dtype=np.complex128,
    )
    boundary_residual = float(
        np.linalg.norm(reconstructed_state - outer_state)
        / max(np.linalg.norm(outer_state), np.finfo(float).eps)
    )
    condition_number_raw = float(np.linalg.cond(basis_matrix))
    condition_number_censored = not np.isfinite(condition_number_raw)
    condition_number = (
        float(np.finfo(float).max)
        if condition_number_censored
        else condition_number_raw
    )
    elapsed_seconds = perf_counter() - started_at

    diagnostics: dict[str, DiagnosticValue] = {
        "method": "scaled_tortoise_full_state_jost_ratio",
        "backend": "scipy_float64_scaled_tortoise_radial_repair_v1",
        "backend_version": 1,
        "paper_specific_envelope_used": False,
        "scientific_acceptance": False,
        "independent_validation": False,
        "required_radius": float(request.required_radius),
        "finite_radius_checkpoint_count": len(finite_radius_states),
        "finite_radius_checkpoint_radii": ",".join(
            format(state.radius, ".17g") for state in finite_radius_states
        ),
        "r_in": r_in,
        "r_out": float(request.r_out),
        "rstar_start": trajectory.rstar_start,
        "rstar_end": trajectory.rstar_end,
        "ell": int(request.ell),
        "sector": request.sector.value,
        "k": float(request.k),
        "actual_precision_bits": 53,
        "actual_decimal_digits": 15.95,
        "precision_note": "actual scipy float64; no arbitrary-precision claim",
        "rtol": float(request.rtol),
        "atol": float(request.atol),
        "unit_incoming_at_infinity": True,
        "valid_at_required_radius": True,
        "finite_psi": _finite_complex(primary_state.psi),
        "finite_dpsi_dr": _finite_complex(primary_state.dpsi_dr),
        "finite_A_in": _finite_complex(A_in),
        "finite_A_out": _finite_complex(A_out),
        "finite_T_horizon": _finite_complex(T_horizon),
        "complex_state_status": primary_state.complex_state_status,
        "complex_derivative_status": primary_state.complex_derivative_status,
        "complex_transmission_status": transmission_status,
        "log_abs_psi": primary_state.log_abs_psi,
        "phase_psi": primary_state.phase_psi,
        "log_abs_dpsi_dr": primary_state.log_abs_dpsi_dr,
        "phase_dpsi_dr": primary_state.phase_dpsi_dr,
        "log_abs_T_horizon": float(log_abs_T_horizon),
        "phase_T_horizon": float(phase_T_horizon),
        "reflection_probability": reflection_probability,
        "horizon_transmission_probability": transmission_probability,
        "transmission_resolved_in_float64_balance": transmission_resolved,
        "flux_balance": flux_balance,
        "flux_residual": flux_residual,
        "flux_interpretation": "internal signed-current identity only",
        "outer_boundary_residual": boundary_residual,
        "normalization_definition": "A_in set exactly to one after Jost ratio",
        "match_condition_number": condition_number,
        "match_condition_number_censored_at_float_max": condition_number_censored,
        "rhs_evaluations": trajectory.rhs_evaluations,
        "segment_count": trajectory.segment_count,
        "minimum_segment_rstar": trajectory.minimum_segment_rstar,
        "maximum_segment_rstar": trajectory.maximum_segment_rstar,
        "maximum_current_relative_drift": (trajectory.maximum_current_relative_drift),
        "current_drift_resolved": trajectory.current_drift_resolved,
        "unresolved_current_segment_count": (
            trajectory.unresolved_current_segment_count
        ),
        "integration_status": (
            f"{trajectory.segment_count} positively rescaled full-state "
            "tortoise-coordinate segments"
        ),
        "accumulated_log_scale": trajectory.accumulated_log_scale,
        "runtime_seconds": float(elapsed_seconds),
        "outer_basis": request.outer_basis,
        "outer_series_order": int(request.outer_series_order),
        "propagation_coordinate": "r_star",
        "propagated_state": "complex psi and dpsi_drstar",
        "riccati_variable_used": False,
        "positive_real_rescaling": True,
        "maximum_tortoise_chunk": _MAX_TORTOISE_CHUNK,
        "maximum_forbidden_log_growth_per_segment": (
            _MAX_FORBIDDEN_LOG_GROWTH_PER_SEGMENT
        ),
        "phase_handling": (
            "absolute horizon phase exp(-i k r_star) and positive-real "
            "rescalings; unit-incoming phase removed with the Jost coefficient"
        ),
        "amplitude_normalization": (
            "unit incoming from Jost ratio and accumulated logarithmic scaling"
        ),
        "derivative_recovery": "dpsi_dr=(dpsi_drstar)/f at exact checkpoints",
        "legacy_path_used": False,
        "newman_penrose_path_used": False,
        "pseudoinverse_used": False,
    }

    if not all(
        bool(diagnostics[key])
        for key in (
            "finite_psi",
            "finite_dpsi_dr",
            "finite_A_in",
            "finite_A_out",
            "finite_T_horizon",
        )
    ):
        raise RuntimeError("scaled-tortoise backend produced non-finite output")

    return ConditionedRadialResult(
        psi=primary_state.psi,
        dpsi_dr=primary_state.dpsi_dr,
        A_in=A_in,
        A_out=A_out,
        T_horizon=T_horizon,
        log_abs_T_horizon=float(log_abs_T_horizon),
        phase_T_horizon=float(phase_T_horizon),
        log_abs_psi=primary_state.log_abs_psi,
        phase_psi=primary_state.phase_psi,
        log_abs_dpsi_dr=primary_state.log_abs_dpsi_dr,
        phase_dpsi_dr=primary_state.phase_dpsi_dr,
        finite_radius_states=finite_radius_states,
        diagnostics=diagnostics,
    )


def _scaled_tortoise_trajectory(
    *,
    request: ConditionedRadialRequest,
    background: StaticSphericalBackground,
    r_in: float,
    finite_radii: tuple[float, ...],
) -> _ScaledTrajectory:
    """Propagate one horizon-normalized complex state with bounded rescaling."""

    if not finite_radii or finite_radii[0] != float(request.required_radius):
        raise RuntimeError("scaled-tortoise checkpoint inventory must start at target")
    target_radii = (*finite_radii, float(request.r_out))
    target_rstars = tuple(float(background.r_star(radius)) for radius in target_radii)
    rstar_start = float(background.r_star(r_in))
    rstar_end = target_rstars[-1]
    if not all(
        left < right
        for left, right in zip((rstar_start, *target_rstars[:-1]), target_rstars)
    ):
        raise RuntimeError("scaled-tortoise checkpoint coordinates are not ordered")

    horizon_phase = -request.k * rstar_start
    psi_initial = complex(np.exp(1.0j * horizon_phase))
    momentum_initial = -1.0j * request.k * psi_initial
    state = np.array(
        [
            psi_initial.real,
            psi_initial.imag,
            momentum_initial.real,
            momentum_initial.imag,
        ],
        dtype=float,
    )

    def rhs(rstar: float, current_state: np.ndarray) -> list[float]:
        radius = float(background.r_from_r_star(rstar))
        psi = complex(current_state[0], current_state[1])
        momentum = complex(current_state[2], current_state[3])
        momentum_derivative = (
            float(_potential(request.sector, request.ell, radius, background))
            - request.k**2
        ) * psi
        return [
            momentum.real,
            momentum.imag,
            momentum_derivative.real,
            momentum_derivative.imag,
        ]

    current_rstar = rstar_start
    accumulated_log_scale = 0.0
    target_index = 0
    rhs_evaluations = 0
    segment_count = 0
    checkpoints: list[_ScaledCheckpoint] = []
    segment_lengths: list[float] = []
    maximum_current_relative_drift = 0.0
    unresolved_current_segment_count = 0
    initial_current_abs = float(request.k)

    while current_rstar < rstar_end:
        radius = float(background.r_from_r_star(current_rstar))
        local_growth = math.sqrt(
            max(
                float(_potential(request.sector, request.ell, radius, background))
                - request.k**2,
                0.0,
            )
        )
        chunk = min(
            _MAX_TORTOISE_CHUNK,
            _MAX_FORBIDDEN_LOG_GROWTH_PER_SEGMENT / max(local_growth, 1.0e-12),
            rstar_end - current_rstar,
        )
        endpoint = current_rstar + chunk
        if target_index < len(target_rstars):
            endpoint = min(endpoint, target_rstars[target_index])
        if (
            not np.isfinite(endpoint)
            or endpoint <= current_rstar
            or endpoint - current_rstar
            <= _ENDPOINT_ULPS * abs(float(np.spacing(current_rstar)))
        ):
            raise RuntimeError("scaled-tortoise segment became unresolved")

        segment = solve_ivp(
            rhs,
            (current_rstar, endpoint),
            state,
            method=request.integration_method,
            rtol=request.rtol,
            atol=request.atol,
            t_eval=np.array([endpoint]),
        )
        rhs_evaluations += int(segment.nfev)
        segment_count += 1
        if not segment.success or segment.y.shape != (4, 1):
            raise RuntimeError(
                f"scaled-tortoise full-state propagation failed: {segment.message}"
            )
        state = np.asarray(segment.y[:, -1], dtype=float)
        if not np.all(np.isfinite(state)):
            raise RuntimeError("scaled-tortoise full state became non-finite")

        psi = complex(state[0], state[1])
        momentum = complex(state[2], state[3])
        scale = max(abs(psi), abs(momentum))
        if not np.isfinite(scale) or scale <= np.finfo(float).tiny:
            raise RuntimeError("scaled-tortoise rescaling factor is unresolved")
        state /= scale
        accumulated_log_scale += math.log(scale)
        segment_lengths.append(endpoint - current_rstar)
        current_rstar = endpoint

        scaled_psi = complex(state[0], state[1])
        scaled_momentum = complex(state[2], state[3])
        scaled_current = float(np.imag(np.conj(scaled_psi) * scaled_momentum))
        if scaled_current < 0.0:
            log_current_abs = math.log(-scaled_current) + 2.0 * accumulated_log_scale
            log_ratio = log_current_abs - math.log(initial_current_abs)
            if abs(log_ratio) <= math.log(np.finfo(float).max):
                maximum_current_relative_drift = max(
                    maximum_current_relative_drift,
                    abs(math.expm1(log_ratio)),
                )
            else:
                unresolved_current_segment_count += 1
        else:
            unresolved_current_segment_count += 1

        if target_index < len(target_rstars) and _same_endpoint(
            current_rstar, target_rstars[target_index]
        ):
            target_radius = target_radii[target_index]
            if target_index < len(finite_radii):
                checkpoints.append(
                    _ScaledCheckpoint(
                        radius=target_radius,
                        psi_scaled=scaled_psi,
                        dpsi_dr_scaled=(
                            scaled_momentum / float(background.f(target_radius))
                        ),
                        accumulated_log_scale=float(accumulated_log_scale),
                    )
                )
            target_index += 1

    if target_index != len(target_rstars) or len(checkpoints) != len(finite_radii):
        raise RuntimeError("scaled-tortoise checkpoint inventory incomplete")
    if not segment_lengths:
        raise RuntimeError("scaled-tortoise propagation used no segments")

    psi_outer_scaled = complex(state[0], state[1])
    momentum_outer_scaled = complex(state[2], state[3])
    dpsi_dr_outer_scaled = momentum_outer_scaled / float(
        background.f(float(request.r_out))
    )
    if not _finite_complex(psi_outer_scaled) or not _finite_complex(
        dpsi_dr_outer_scaled
    ):
        raise RuntimeError("scaled-tortoise outer state is non-finite")

    return _ScaledTrajectory(
        checkpoints=tuple(checkpoints),
        psi_outer_scaled=psi_outer_scaled,
        dpsi_dr_outer_scaled=dpsi_dr_outer_scaled,
        accumulated_log_scale=float(accumulated_log_scale),
        rhs_evaluations=rhs_evaluations,
        segment_count=segment_count,
        rstar_start=rstar_start,
        rstar_end=rstar_end,
        maximum_current_relative_drift=float(maximum_current_relative_drift),
        current_drift_resolved=unresolved_current_segment_count == 0,
        unresolved_current_segment_count=unresolved_current_segment_count,
        minimum_segment_rstar=float(min(segment_lengths)),
        maximum_segment_rstar=float(max(segment_lengths)),
    )


def _scaled_two_by_two_solve(
    matrix: np.ndarray,
    rhs: np.ndarray,
) -> tuple[complex, complex]:
    """Solve after independent positive column scaling, without least squares."""

    column_norms = np.linalg.norm(matrix, axis=0)
    if (
        matrix.shape != (2, 2)
        or rhs.shape != (2,)
        or not np.all(np.isfinite(matrix))
        or not np.all(np.isfinite(rhs))
        or not np.all(np.isfinite(column_norms))
        or np.any(column_norms <= np.finfo(float).tiny)
    ):
        raise RuntimeError("scaled-tortoise Jost matching inputs are invalid")
    scaled_matrix = matrix / column_norms[np.newaxis, :]
    try:
        scaled_coefficients = np.linalg.solve(scaled_matrix, rhs)
    except np.linalg.LinAlgError as exc:
        raise RuntimeError("scaled-tortoise Jost matching is singular") from exc
    coefficients = scaled_coefficients / column_norms
    if not np.all(np.isfinite(coefficients)):
        raise RuntimeError("scaled-tortoise Jost coefficients are non-finite")
    return complex(coefficients[0]), complex(coefficients[1])


def _unit_incoming_checkpoint_state(
    checkpoint: _ScaledCheckpoint,
    *,
    incoming_coefficient: complex,
    outer_log_scale: float,
) -> ConditionedFiniteRadiusState:
    normalization_log_abs = math.log(abs(incoming_coefficient)) + outer_log_scale
    normalization_phase = float(np.angle(incoming_coefficient))
    psi_abs = abs(checkpoint.psi_scaled)
    derivative_abs = abs(checkpoint.dpsi_dr_scaled)
    if psi_abs == 0.0 or derivative_abs == 0.0:
        raise RuntimeError("scaled-tortoise checkpoint has a zero state component")
    log_abs_psi = (
        math.log(psi_abs) + checkpoint.accumulated_log_scale - normalization_log_abs
    )
    phase_psi = _principal_phase(np.angle(checkpoint.psi_scaled) - normalization_phase)
    log_abs_dpsi_dr = (
        math.log(derivative_abs)
        + checkpoint.accumulated_log_scale
        - normalization_log_abs
    )
    phase_dpsi_dr = _principal_phase(
        np.angle(checkpoint.dpsi_dr_scaled) - normalization_phase
    )
    psi, psi_status = _complex_from_log(log_abs_psi, phase_psi)
    dpsi_dr, derivative_status = _complex_from_log(
        log_abs_dpsi_dr,
        phase_dpsi_dr,
    )
    return ConditionedFiniteRadiusState(
        radius=float(checkpoint.radius),
        psi=psi,
        dpsi_dr=dpsi_dr,
        log_abs_psi=float(log_abs_psi),
        phase_psi=float(phase_psi),
        log_abs_dpsi_dr=float(log_abs_dpsi_dr),
        phase_dpsi_dr=float(phase_dpsi_dr),
        complex_state_status=psi_status,
        complex_derivative_status=derivative_status,
    )


def _potential(
    sector: Sector,
    ell: int,
    radius: float,
    background: StaticSphericalBackground,
) -> float:
    if sector is Sector.ODD:
        return float(V_RW(ell, radius, background))
    return float(V_Zerilli(ell, radius, background))


def _same_endpoint(left: float, right: float) -> bool:
    return bool(
        abs(left - right)
        <= _ENDPOINT_ULPS * max(abs(float(np.spacing(right))), np.finfo(float).tiny)
    )


def _principal_phase(value: float) -> float:
    return float(np.angle(np.exp(1.0j * float(value))))


def _complex_from_log(log_abs: float, phase: float) -> tuple[complex, str]:
    if not np.isfinite(log_abs) or not np.isfinite(phase):
        raise RuntimeError("scaled-tortoise log-amplitude is non-finite")
    log_smallest = math.log(float(np.nextafter(0.0, 1.0)))
    log_largest = math.log(float(np.finfo(float).max))
    if log_abs < log_smallest:
        return 0.0j, "LOG_SCALED_UNDERFLOW"
    if log_abs > log_largest:
        raise RuntimeError("scaled-tortoise unit-incoming field exceeds float64")
    return complex(math.exp(log_abs) * np.exp(1.0j * phase)), "FINITE_COMPLEX"


def _probability_from_log(log_abs_amplitude: float) -> float:
    log_probability = 2.0 * float(log_abs_amplitude)
    if not math.isfinite(log_probability):
        raise RuntimeError("scaled-tortoise probability logarithm is non-finite")
    log_smallest = math.log(float(np.nextafter(0.0, 1.0)))
    log_largest = math.log(float(np.finfo(float).max))
    if log_probability < log_smallest:
        return 0.0
    if log_probability > log_largest:
        raise RuntimeError("scaled-tortoise transmission probability exceeds float64")
    return float(math.exp(log_probability))


def _finite_complex(value: complex) -> bool:
    return bool(np.isfinite(value.real) and np.isfinite(value.imag))


__all__ = ["solve_scaled_tortoise_radial_at_radius"]
