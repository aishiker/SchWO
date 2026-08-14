from __future__ import annotations

from dataclasses import dataclass
import math
from time import perf_counter
from typing import Mapping

import numpy as np
from scipy.integrate import solve_ivp

from schwgw.backgrounds.base import StaticSphericalBackground
from schwgw.numerics.matching import outer_asymptotic_basis
from schwgw.perturbations import Sector, V_RW, V_Zerilli

DiagnosticValue = bool | int | float | str


@dataclass(frozen=True)
class _ScaledCheckpoint:
    radius: float
    psi_scaled: complex
    dpsi_dr_scaled: complex
    accumulated_log_scale: float


@dataclass(frozen=True)
class _ScaledOuterState:
    y_required: complex
    horizon_normalized_log_abs_psi_required: float
    horizon_normalized_phase_psi_required: float
    psi_outer_scaled: complex
    dpsi_dr_outer_scaled: complex
    accumulated_log_scale: float
    rhs_evaluations: int
    status: str
    checkpoints: tuple[_ScaledCheckpoint, ...]


@dataclass(frozen=True)
class ConditionedRadialRequest:
    """Generic, paper-independent conditioned finite-radius solve request."""

    sector: Sector
    ell: int
    k: float
    required_radius: float
    r_out: float
    r_in_eps: float = 1e-6
    rtol: float = 1e-10
    atol: float = 1e-12
    outer_basis: str = "jost_1_over_r"
    outer_series_order: int = 160
    integration_method: str = "DOP853"
    evaluation_radii: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.sector, Sector):
            raise TypeError("sector must be a Sector enum value.")
        if self.ell < 2:
            raise ValueError("ell must be at least 2.")
        _require_positive_finite("k", self.k)
        _require_positive_finite("required_radius", self.required_radius)
        _require_positive_finite("r_out", self.r_out)
        _require_positive_finite("r_in_eps", self.r_in_eps)
        _require_positive_finite("rtol", self.rtol)
        _require_positive_finite("atol", self.atol)
        if self.required_radius >= self.r_out:
            raise ValueError("required_radius must be strictly smaller than r_out.")
        normalized_radii = tuple(float(radius) for radius in self.evaluation_radii)
        if any(not np.isfinite(radius) for radius in normalized_radii):
            raise ValueError("evaluation_radii must be finite")
        if any(
            radius < self.required_radius or radius >= self.r_out
            for radius in normalized_radii
        ):
            raise ValueError("evaluation_radii must lie in [required_radius, r_out)")
        if len(normalized_radii) != len(set(normalized_radii)):
            raise ValueError("evaluation_radii must not contain duplicates")
        object.__setattr__(self, "evaluation_radii", normalized_radii)
        if self.outer_basis != "jost_1_over_r":
            raise ValueError("conditioned backend requires jost_1_over_r")
        if (
            isinstance(self.outer_series_order, bool)
            or not isinstance(self.outer_series_order, int)
            or not 2 <= self.outer_series_order <= 256
        ):
            raise ValueError("outer_series_order must be an integer in [2, 256]")
        if self.integration_method != "DOP853":
            raise ValueError("conditioned backend currently requires DOP853")


@dataclass(frozen=True)
class ConditionedFiniteRadiusState:
    """Unit-incoming state at one explicitly requested Schwarzschild radius."""

    radius: float
    psi: complex
    dpsi_dr: complex
    log_abs_psi: float
    phase_psi: float
    log_abs_dpsi_dr: float
    phase_dpsi_dr: float
    complex_state_status: str
    complex_derivative_status: str


@dataclass(frozen=True)
class ConditionedRadialResult:
    """Unit-incoming state with a durable log-amplitude representation."""

    psi: complex
    dpsi_dr: complex
    A_in: complex
    A_out: complex
    T_horizon: complex
    log_abs_T_horizon: float
    phase_T_horizon: float
    log_abs_psi: float
    phase_psi: float
    log_abs_dpsi_dr: float
    phase_dpsi_dr: float
    finite_radius_states: tuple[ConditionedFiniteRadiusState, ...]
    diagnostics: Mapping[str, DiagnosticValue]

    def __post_init__(self) -> None:
        for name in ("psi", "dpsi_dr", "A_in", "A_out", "T_horizon"):
            if not _finite_complex(complex(getattr(self, name))):
                raise ValueError(f"{name} must be finite")
        for name in (
            "log_abs_psi",
            "phase_psi",
            "log_abs_dpsi_dr",
            "phase_dpsi_dr",
            "log_abs_T_horizon",
            "phase_T_horizon",
        ):
            value = float(getattr(self, name))
            if not np.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)

    @property
    def valid_at_required_radius(self) -> bool:
        return bool(self.diagnostics.get("valid_at_required_radius", False))


def solve_conditioned_radial_at_radius(
    request: ConditionedRadialRequest,
    background: StaticSphericalBackground,
) -> ConditionedRadialResult:
    """Solve with a Riccati target state and rescaled outward propagation.

    The logarithmic derivative ``y=(d psi/dr*)/psi`` is propagated from the
    horizon to ``required_radius``.  A normalized full complex state is then
    propagated to ``r_out`` in short segments with positive real rescaling.
    A column-scaled exact 2x2 solve against the Jost basis yields the ratio
    ``A_out/A_in`` without a pseudoinverse.  This avoids carrying exponentially
    large forbidden-region amplitudes.  If the
    unit-incoming field at ``required_radius`` is below float64's subnormal
    range, ``psi``/``dpsi_dr`` are represented as zero *only for compatibility*;
    the exact float64 log-amplitude and phase remain in the result and the
    diagnostic status is ``LOG_SCALED_UNDERFLOW``.
    """
    if not isinstance(request, ConditionedRadialRequest):
        raise TypeError("request must be a ConditionedRadialRequest.")
    if background.horizon_radius >= request.required_radius:
        raise ValueError("required_radius must be outside the background horizon.")
    if request.required_radius >= request.r_out:
        raise ValueError("required_radius must be strictly smaller than r_out.")

    started_at = perf_counter()
    r_in = background.horizon_radius * (1.0 + request.r_in_eps)
    required_radius = float(request.required_radius)
    if required_radius <= r_in:
        raise ValueError("required_radius must be larger than the near-horizon radius.")

    trajectory = _conditioned_trajectory(
        request=request,
        background=background,
        r_in=r_in,
        required_radius=required_radius,
        checkpoint_radii=tuple(sorted({required_radius, *request.evaluation_radii})),
    )
    y_required = trajectory.y_required

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
        raise RuntimeError("conditioned incoming Jost coefficient is unresolved")
    reflection_ratio = outgoing_coefficient / incoming_coefficient

    log_abs_A_in_horizon_normalized = (
        trajectory.horizon_normalized_log_abs_psi_required
        + trajectory.accumulated_log_scale
        + math.log(abs(incoming_coefficient))
    )
    phase_A_in_horizon_normalized = _principal_phase(
        trajectory.horizon_normalized_phase_psi_required
        + np.angle(incoming_coefficient)
    )
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
    primary_state = finite_radius_states[0]
    if primary_state.radius != required_radius:
        raise RuntimeError("conditioned primary checkpoint ordering changed")
    psi = primary_state.psi
    dpsi_dr = primary_state.dpsi_dr
    log_abs_psi = primary_state.log_abs_psi
    phase_psi = primary_state.phase_psi
    log_abs_dpsi_dr = primary_state.log_abs_dpsi_dr
    phase_dpsi_dr = primary_state.phase_dpsi_dr
    psi_status = primary_state.complex_state_status
    derivative_status = primary_state.complex_derivative_status
    A_in = 1.0 + 0.0j
    A_out = complex(reflection_ratio)
    transmission_probability = _probability_from_log(log_abs_T_horizon)
    reflection_probability = float(abs(A_out) ** 2)
    flux_balance = reflection_probability + transmission_probability
    flux_residual = float(abs(flux_balance - 1.0))

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
        "method": "scaled_log_riccati_jost_ratio",
        "backend": "scipy_float64_conditioned_radial_v1",
        "paper_specific_envelope_used": False,
        "scientific_acceptance": False,
        "required_radius": required_radius,
        "required_log_derivative_real": float(y_required.real),
        "required_log_derivative_imag": float(y_required.imag),
        "finite_radius_checkpoint_count": len(finite_radius_states),
        "finite_radius_checkpoint_radii": ",".join(
            format(state.radius, ".17g") for state in finite_radius_states
        ),
        "r_out": float(request.r_out),
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
        "finite_psi": _finite_complex(psi),
        "finite_dpsi_dr": _finite_complex(dpsi_dr),
        "finite_A_in": _finite_complex(A_in),
        "finite_A_out": _finite_complex(A_out),
        "finite_T_horizon": _finite_complex(T_horizon),
        "complex_state_status": psi_status,
        "complex_derivative_status": derivative_status,
        "complex_transmission_status": transmission_status,
        "log_abs_psi": float(log_abs_psi),
        "phase_psi": float(phase_psi),
        "log_abs_dpsi_dr": float(log_abs_dpsi_dr),
        "phase_dpsi_dr": float(phase_dpsi_dr),
        "log_abs_T_horizon": float(log_abs_T_horizon),
        "phase_T_horizon": float(phase_T_horizon),
        "reflection_probability": reflection_probability,
        "horizon_transmission_probability": transmission_probability,
        "flux_balance": flux_balance,
        "flux_residual": flux_residual,
        "horizon_flux_resolved": True,
        "outer_boundary_residual": float(boundary_residual),
        "normalization_definition": "A_in set exactly to one after Jost ratio",
        "match_condition_number": float(condition_number),
        "match_condition_number_censored_at_float_max": condition_number_censored,
        "rhs_evaluations": int(trajectory.rhs_evaluations),
        "integration_status": trajectory.status,
        "accumulated_log_scale": float(trajectory.accumulated_log_scale),
        "runtime_seconds": float(elapsed_seconds),
        "outer_basis": request.outer_basis,
        "outer_series_order": int(request.outer_series_order),
        "phase_handling": (
            "required-radius phase recovered from the complex Jost incoming "
            "coefficient; positive real segment rescalings preserve phase"
        ),
        "amplitude_normalization": "unit incoming from Jost ratio and log-amplitude difference",
        "derivative_recovery": "log/phase of dpsi_dr=(y/f)*psi",
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
        raise RuntimeError(
            "generic conditioned radial oracle produced non-finite output."
        )

    return ConditionedRadialResult(
        psi=psi,
        dpsi_dr=dpsi_dr,
        A_in=A_in,
        A_out=A_out,
        T_horizon=T_horizon,
        log_abs_T_horizon=log_abs_T_horizon,
        phase_T_horizon=phase_T_horizon,
        log_abs_psi=log_abs_psi,
        phase_psi=phase_psi,
        log_abs_dpsi_dr=log_abs_dpsi_dr,
        phase_dpsi_dr=phase_dpsi_dr,
        finite_radius_states=finite_radius_states,
        diagnostics=diagnostics,
    )


def _conditioned_trajectory(
    *,
    request: ConditionedRadialRequest,
    background: StaticSphericalBackground,
    r_in: float,
    required_radius: float,
    checkpoint_radii: tuple[float, ...],
) -> _ScaledOuterState:
    """Propagate to the target in Riccati form, then outward with rescaling."""

    def riccati_rhs(r: float, state: np.ndarray) -> list[float]:
        value = complex(state[0], state[1])
        derivative = (
            _potential(request.sector, request.ell, r, background)
            - request.k**2
            - value**2
        ) / background.f(r)
        logarithmic_amplitude_derivative = value / background.f(r)
        return [
            derivative.real,
            derivative.imag,
            logarithmic_amplitude_derivative.real,
            logarithmic_amplitude_derivative.imag,
        ]

    horizon_phase = -request.k * float(background.r_star(r_in))

    riccati = solve_ivp(
        riccati_rhs,
        (r_in, required_radius),
        np.array([0.0, -request.k, 0.0, horizon_phase], dtype=float),
        method=request.integration_method,
        rtol=request.rtol,
        atol=request.atol,
    )
    if not riccati.success:
        raise RuntimeError(f"conditioned Riccati propagation failed: {riccati.message}")
    y_required = complex(riccati.y[0, -1], riccati.y[1, -1])
    if not _finite_complex(y_required):
        raise RuntimeError("conditioned Riccati target state is non-finite")

    derivative_required = y_required / background.f(required_radius)
    state = np.array(
        [1.0, 0.0, derivative_required.real, derivative_required.imag],
        dtype=float,
    )
    accumulated_log_scale = 0.0
    current = required_radius
    rhs_evaluations = int(riccati.nfev)
    segment_count = 0
    checkpoint_index = 1
    checkpoints = [
        _ScaledCheckpoint(
            radius=required_radius,
            psi_scaled=1.0 + 0.0j,
            dpsi_dr_scaled=derivative_required,
            accumulated_log_scale=0.0,
        )
    ]
    if not checkpoint_radii or checkpoint_radii[0] != required_radius:
        raise RuntimeError("conditioned checkpoint inventory must start at target")

    def full_state_rhs(r: float, current_state: np.ndarray) -> list[float]:
        psi = complex(current_state[0], current_state[1])
        derivative = complex(current_state[2], current_state[3])
        lapse = background.f(r)
        second_derivative = (
            -(
                lapse * background.df_dr(r) * derivative
                + (
                    request.k**2
                    - _potential(request.sector, request.ell, r, background)
                )
                * psi
            )
            / lapse**2
        )
        return [
            derivative.real,
            derivative.imag,
            second_derivative.real,
            second_derivative.imag,
        ]

    while current < float(request.r_out):
        local_potential = float(
            _potential(request.sector, request.ell, current, background)
        )
        local_growth = math.sqrt(max(local_potential - request.k**2, 0.0))
        local_growth /= float(background.f(current))
        chunk = min(
            5.0,
            24.0 / max(local_growth, 1.0e-12),
            float(request.r_out) - current,
        )
        if not np.isfinite(chunk) or chunk <= 1.0e-10:
            raise RuntimeError("conditioned rescaling chunk became unresolved")
        endpoint = current + chunk
        if checkpoint_index < len(checkpoint_radii):
            endpoint = min(endpoint, checkpoint_radii[checkpoint_index])
        segment = solve_ivp(
            full_state_rhs,
            (current, endpoint),
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
                f"conditioned rescaled state propagation failed: {segment.message}"
            )
        state = np.asarray(segment.y[:, -1], dtype=float)
        if not np.all(np.isfinite(state)):
            raise RuntimeError("conditioned rescaled state became non-finite")
        psi = complex(state[0], state[1])
        derivative = complex(state[2], state[3])
        scale = max(abs(psi), abs(derivative))
        if not np.isfinite(scale) or scale <= np.finfo(float).tiny:
            raise RuntimeError("conditioned rescaling factor is unresolved")
        state /= scale
        accumulated_log_scale += math.log(scale)
        current = endpoint
        if (
            checkpoint_index < len(checkpoint_radii)
            and current == checkpoint_radii[checkpoint_index]
        ):
            checkpoints.append(
                _ScaledCheckpoint(
                    radius=current,
                    psi_scaled=complex(state[0], state[1]),
                    dpsi_dr_scaled=complex(state[2], state[3]),
                    accumulated_log_scale=float(accumulated_log_scale),
                )
            )
            checkpoint_index += 1

    if checkpoint_index != len(checkpoint_radii):
        raise RuntimeError("conditioned finite-radius checkpoint inventory incomplete")

    return _ScaledOuterState(
        y_required=y_required,
        horizon_normalized_log_abs_psi_required=float(riccati.y[2, -1]),
        horizon_normalized_phase_psi_required=float(riccati.y[3, -1]),
        psi_outer_scaled=complex(state[0], state[1]),
        dpsi_dr_outer_scaled=complex(state[2], state[3]),
        accumulated_log_scale=float(accumulated_log_scale),
        rhs_evaluations=rhs_evaluations,
        status=(
            f"Riccati target solve plus {segment_count} positively rescaled "
            "outer segments"
        ),
        checkpoints=tuple(checkpoints),
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


def _scaled_two_by_two_solve(
    matrix: np.ndarray,
    rhs: np.ndarray,
) -> tuple[complex, complex]:
    """Solve after independent positive column scaling, without pseudoinverse."""

    column_norms = np.linalg.norm(matrix, axis=0)
    if (
        matrix.shape != (2, 2)
        or rhs.shape != (2,)
        or not np.all(np.isfinite(matrix))
        or not np.all(np.isfinite(rhs))
        or not np.all(np.isfinite(column_norms))
        or np.any(column_norms <= np.finfo(float).tiny)
    ):
        raise RuntimeError("conditioned Jost matching inputs are invalid")
    scaled_matrix = matrix / column_norms[np.newaxis, :]
    try:
        scaled_coefficients = np.linalg.solve(scaled_matrix, rhs)
    except np.linalg.LinAlgError as exc:
        raise RuntimeError("conditioned Jost matching is singular") from exc
    coefficients = scaled_coefficients / column_norms
    if not np.all(np.isfinite(coefficients)):
        raise RuntimeError("conditioned Jost matching coefficients are non-finite")
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
        raise RuntimeError(
            "conditioned checkpoint contains an exact zero state component"
        )
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


def _principal_phase(value: float) -> float:
    return float(np.angle(np.exp(1.0j * float(value))))


def _complex_from_log(log_abs: float, phase: float) -> tuple[complex, str]:
    if not np.isfinite(log_abs) or not np.isfinite(phase):
        raise RuntimeError("conditioned log-amplitude representation is non-finite")
    log_smallest = math.log(float(np.nextafter(0.0, 1.0)))
    log_largest = math.log(float(np.finfo(float).max))
    if log_abs < log_smallest:
        return 0.0j, "LOG_SCALED_UNDERFLOW"
    if log_abs > log_largest:
        raise RuntimeError("conditioned unit-incoming field exceeds float64 range")
    return complex(math.exp(log_abs) * np.exp(1.0j * phase)), "FINITE_COMPLEX"


def _probability_from_log(log_abs_amplitude: float) -> float:
    log_probability = 2.0 * float(log_abs_amplitude)
    if not math.isfinite(log_probability):
        raise RuntimeError("conditioned transmission log-probability is non-finite")
    log_smallest = math.log(float(np.nextafter(0.0, 1.0)))
    log_largest = math.log(float(np.finfo(float).max))
    if log_probability < log_smallest:
        return 0.0
    if log_probability > log_largest:
        raise RuntimeError("conditioned transmission probability exceeds float64")
    return float(math.exp(log_probability))


def _finite_complex(value: complex) -> bool:
    return bool(np.isfinite(value.real) and np.isfinite(value.imag))


def _require_positive_finite(name: str, value: float) -> None:
    if not np.isfinite(float(value)) or float(value) <= 0.0:
        raise ValueError(f"{name} must be positive and finite.")


__all__ = [
    "ConditionedFiniteRadiusState",
    "ConditionedRadialRequest",
    "ConditionedRadialResult",
    "solve_conditioned_radial_at_radius",
]
