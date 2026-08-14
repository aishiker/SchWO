"""Independent arbitrary-precision Schwarzschild RW/Zerilli S-matrix solver.

This Phase-6 backend deliberately has no dependency on the project SciPy
radial solver, Jost evaluator, or matching implementation.  The only shared
scientific surface is the stated RW/Zerilli equations and scattering
convention, re-expressed here with mpmath arithmetic.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shlex
import sys
import time
from typing import Mapping, Sequence

import mpmath as mp


BACKEND_SCHEMA = "schwgw_phase6_independent_mpmath_radial_backend_v1"
EVIDENCE_SCHEMA = "schwgw_phase6_independent_mpmath_selected_anchor_evidence_v1"
SECTORS = ("odd", "even")
_FORBIDDEN_IMPORT_PREFIXES = ("numpy", "scipy", "schwgw")
_FORBIDDEN_CALL_NAMES = (
    "solve_radial_mode",
    "outer_asymptotic_basis",
    "match_outer_asymptotic",
)


class MpmathRadialContractError(ValueError):
    """Raised when backend inputs or evidence violate the Phase-6 contract."""


@dataclass(frozen=True)
class MpmathMode:
    mode_id: str
    regime: str
    sector: str
    ell: int
    kM: float
    evaluation_radius_M: float = 60.0

    def __post_init__(self) -> None:
        if not self.mode_id or not self.regime:
            raise MpmathRadialContractError("mode identity must be non-empty")
        if self.sector not in SECTORS:
            raise MpmathRadialContractError("sector must be odd or even")
        if self.ell < 2 or not math.isfinite(self.kM) or self.kM <= 0.0:
            raise MpmathRadialContractError("invalid radial mode")
        if not math.isfinite(self.evaluation_radius_M) or self.evaluation_radius_M <= 2:
            raise MpmathRadialContractError("evaluation radius must be outside 2M")

    def to_metadata(self) -> dict[str, object]:
        return {
            "mode_id": self.mode_id,
            "regime": self.regime,
            "sector": self.sector,
            "ell": self.ell,
            "kM": self.kM,
            "evaluation_radius_M": self.evaluation_radius_M,
        }


@dataclass(frozen=True)
class MpmathEvaluationPoint:
    """Generic immutable finite-radius request for the independent backend."""

    point_id: str
    radius_M: str

    def __post_init__(self) -> None:
        if not self.point_id or not isinstance(self.radius_M, str):
            raise MpmathRadialContractError("evaluation point fields must be non-empty")
        try:
            radius = mp.mpf(self.radius_M)
        except (TypeError, ValueError) as exc:
            raise MpmathRadialContractError("evaluation radius is malformed") from exc
        if not mp.isfinite(radius) or radius <= 2:
            raise MpmathRadialContractError("evaluation radius must be finite and outside 2M")

    def to_metadata(self) -> dict[str, str]:
        return {"point_id": self.point_id, "radius_M": self.radius_M}


@dataclass(frozen=True)
class MpmathSolveConfig:
    working_dps: int
    r_in_eps: float = 1.0e-6
    maximum_step_rstar: float = 0.2
    pilot_match_radius_M: float = 60.0

    def __post_init__(self) -> None:
        if self.working_dps < 30:
            raise MpmathRadialContractError("working_dps must be at least 30")
        if not math.isfinite(self.r_in_eps) or self.r_in_eps <= 0.0:
            raise MpmathRadialContractError("r_in_eps must be positive")
        if not math.isfinite(self.maximum_step_rstar) or self.maximum_step_rstar <= 0:
            raise MpmathRadialContractError("maximum_step_rstar must be positive")
        if not math.isfinite(self.pilot_match_radius_M) or self.pilot_match_radius_M <= 40:
            raise MpmathRadialContractError("pilot match radius must exceed finite-state radii")


def selected_stage_a_modes() -> tuple[MpmathMode, ...]:
    """Return the fixed eight-key Stage-A arbitrary-precision pilot."""

    return (
        MpmathMode("ap_low_odd_k0p5_l2", "low_ell_absorptive", "odd", 2, 0.5),
        MpmathMode("ap_low_even_k0p5_l2", "low_ell_absorptive", "even", 2, 0.5),
        MpmathMode("ap_ordinary_odd_k1_l20", "ordinary", "odd", 20, 1.0),
        MpmathMode("ap_ordinary_even_k1_l20", "ordinary", "even", 20, 1.0),
        MpmathMode("ap_turning_odd_k2_l120", "turning", "odd", 120, 2.0),
        MpmathMode("ap_turning_even_k2_l120", "turning", "even", 120, 2.0),
        MpmathMode("ap_q018_odd_k2_l153", "q018_anchor", "odd", 153, 2.0),
        MpmathMode("ap_q018_even_k2_l153", "q018_anchor", "even", 153, 2.0),
    )


def schwarzschild_rstar(radius: mp.mpf) -> mp.mpf:
    """Return r_* for M=1 with the additive constant fixed by Phase 6."""

    radius = mp.mpf(radius)
    if radius <= 2:
        raise MpmathRadialContractError("rstar requires r > 2M")
    return radius + 2 * mp.log(radius / 2 - 1)


def radial_potential(sector: str, ell: int, radius: mp.mpf) -> mp.mpf:
    """Evaluate the independently expressed RW or Zerilli potential."""

    if sector not in SECTORS or ell < 2:
        raise MpmathRadialContractError("invalid potential sector or ell")
    radius = mp.mpf(radius)
    if radius <= 2:
        raise MpmathRadialContractError("potential requires r > 2M")
    lapse = 1 - 2 / radius
    if sector == "odd":
        return lapse / radius**2 * (ell * (ell + 1) - 6 / radius)
    lambda_ = mp.mpf(ell - 1) * (ell + 2) / 2
    mass_over_r = 1 / radius
    capital_lambda = lambda_ + 3 * mass_over_r
    bracket = (
        2 * lambda_**2 * (lambda_ + 1)
        + 6 * lambda_**2 * mass_over_r
        + 18 * lambda_ * mass_over_r**2
        + 18 * mass_over_r**3
    )
    return lapse / radius**2 * bracket / capital_lambda**2


def _potential_series(sector: str, ell: int, order: int) -> list[mp.mpf]:
    values = [mp.mpf("0") for _ in range(order + 1)]
    angular = mp.mpf(ell * (ell + 1))
    if sector == "odd":
        values[2] = angular
        if order >= 3:
            values[3] = -2 * angular - 6
        if order >= 4:
            values[4] = 12
        return values
    lambda_ = mp.mpf((ell - 1) * (ell + 2)) / 2
    bracket = [mp.mpf("0") for _ in range(order + 1)]
    bracket[0] = 2 * lambda_**2 * (lambda_ + 1)
    if order >= 1:
        bracket[1] = 6 * lambda_**2
    if order >= 2:
        bracket[2] = 18 * lambda_
    if order >= 3:
        bracket[3] = 18
    inverse_square = [
        mp.mpf((-1) ** index)
        * (index + 1)
        * (3 / lambda_) ** index
        / lambda_**2
        for index in range(order + 1)
    ]
    quotient = [mp.mpf("0") for _ in range(order + 1)]
    for left, left_value in enumerate(bracket):
        for right, right_value in enumerate(inverse_square[: order + 1 - left]):
            quotient[left + right] += left_value * right_value
    for index in range(order - 1):
        values[index + 2] += quotient[index]
        if index + 3 <= order:
            values[index + 3] -= 2 * quotient[index]
    return values


def independent_jost_basis(
    *,
    sector: str,
    ell: int,
    k: mp.mpf,
    radius: mp.mpf,
    sign: int,
    order_cap: int,
) -> tuple[mp.mpc, mp.mpc, int, mp.mpf, bool, mp.mpf, str]:
    """Return local mpmath Jost value and dpsi/dr_* without project code."""

    if sign not in (-1, 1) or not 2 <= order_cap <= 256:
        raise MpmathRadialContractError("invalid Jost sign or order")
    potential = _potential_series(sector, ell, order_cap + 2)
    f_squared = (mp.mpf(1), mp.mpf(-4), mp.mpf(4))
    derivative_coefficients = (
        2j * sign * k,
        -4j * sign * k,
        mp.mpf(2),
        mp.mpf(-4),
    )
    terms: list[mp.mpc] = [mp.mpc(1)]
    decreasing_run = 0
    increasing_run = 0
    optimal_index: int | None = None
    threshold = mp.power(10, -min(60, max(20, mp.mp.dps // 2)))
    cap_reached = True
    termination_reason = "order_cap_reached"
    for index in range(1, order_cap + 1):
        power = index + 1
        known = mp.mpc(0)
        for offset, coefficient in enumerate(f_squared):
            source = power - offset - 2
            if 0 <= source < index:
                known += (
                    coefficient
                    * source
                    * (source + 1)
                    * terms[source]
                    * radius ** (source - index)
                )
        for offset, coefficient in enumerate(derivative_coefficients):
            source = power - offset - 1
            if 0 <= source < index:
                known += (
                    coefficient
                    * (-source)
                    * terms[source]
                    * radius ** (source - index)
                )
        for offset in range(2, min(power, len(potential) - 1) + 1):
            source = power - offset
            if 0 <= source < index:
                known -= potential[offset] * terms[source] * radius ** (source - index)
        pivot = -2j * sign * k * index
        terms.append(-known / pivot)
        if abs(terms[-1]) < abs(terms[-2]):
            decreasing_run += 1
            increasing_run = 0
            optimal_index = None
        else:
            if increasing_run == 0 and decreasing_run >= 8:
                optimal_index = index - 1
            increasing_run += 1
            decreasing_run = 0
        if increasing_run >= 4 and optimal_index is not None:
            terms = terms[: optimal_index + 1]
            cap_reached = False
            termination_reason = "optimal_truncation_after_term_growth"
            break
        if index >= 16 and max(abs(value) for value in terms[-4:]) < threshold:
            terms = terms[: index + 1]
            cap_reached = False
            termination_reason = "tail_threshold_reached"
            break
    series = mp.fsum(terms)
    derivative_r = -mp.fsum(
        index * value for index, value in enumerate(terms)
    ) / radius
    phase = mp.exp(sign * 1j * k * schwarzschild_rstar(radius))
    lapse = 1 - 2 / radius
    value = phase * series
    derivative_rstar = phase * (sign * 1j * k * series + lapse * derivative_r)
    tail_width = min(4, len(terms) - 1)
    tail_ratio = mp.fsum(abs(value) for value in terms[-tail_width:]) / max(
        abs(series), mp.eps
    )
    return (
        value,
        derivative_rstar,
        len(terms) - 1,
        tail_ratio,
        cap_reached,
        threshold,
        termination_reason,
    )


def _rhs(
    mode: MpmathMode,
    state: Sequence[mp.mpf | mp.mpc],
) -> tuple[mp.mpf | mp.mpc, ...]:
    if len(state) < 3 or len(state) % 2 != 1:
        raise MpmathRadialContractError("radial state must contain r and field pairs")
    radius = mp.mpf(state[0])
    lapse = 1 - 2 / radius
    potential = radial_potential(mode.sector, mode.ell, radius)
    factor = -(mp.mpf(str(mode.kM)) ** 2 - potential)
    result: list[mp.mpf | mp.mpc] = [lapse]
    for index in range(1, len(state), 2):
        psi = mp.mpc(state[index])
        momentum = mp.mpc(state[index + 1])
        result.extend((momentum, factor * psi))
    return tuple(result)


def _rk4_step(
    mode: MpmathMode,
    state: Sequence[mp.mpf | mp.mpc],
    step: mp.mpf,
) -> list[mp.mpf | mp.mpc]:
    first = _rhs(mode, state)
    second_state = [value + step * slope / 2 for value, slope in zip(state, first)]
    second = _rhs(mode, second_state)
    third_state = [value + step * slope / 2 for value, slope in zip(state, second)]
    third = _rhs(mode, third_state)
    fourth_state = [value + step * slope for value, slope in zip(state, third)]
    fourth = _rhs(mode, fourth_state)
    return [
        value + step * (a + 2 * b + 2 * c + d) / 6
        for value, a, b, c, d in zip(state, first, second, third, fourth)
    ]


def _signed_current(state: Sequence[mp.mpf | mp.mpc]) -> mp.mpf:
    return mp.im(mp.conj(mp.mpc(state[1])) * mp.mpc(state[2]))


def _integrate_to_radii(
    mode: MpmathMode,
    config: MpmathSolveConfig,
    radii: Sequence[mp.mpf],
) -> tuple[dict[str, list[mp.mpf | mp.mpc]], int, mp.mpf, list[mp.mpf | mp.mpc]]:
    r_in = 2 * (1 + mp.mpf(str(config.r_in_eps)))
    k = mp.mpf(str(mode.kM))
    x = schwarzschild_rstar(r_in)
    phase = mp.exp(-1j * k * x)
    state: list[mp.mpf | mp.mpc] = [r_in, phase, -1j * k * phase]
    initial_state = list(state)
    initial_current = _signed_current(initial_state)
    max_current_drift = mp.mpf(0)
    maximum_step = mp.mpf(str(config.maximum_step_rstar))
    outputs: dict[str, list[mp.mpf | mp.mpc]] = {}
    steps = 0
    for radius in sorted({mp.mpf(value) for value in radii}):
        if radius <= r_in:
            raise MpmathRadialContractError("checkpoint radius must exceed r_in")
        target = schwarzschild_rstar(radius)
        while x < target:
            step = min(maximum_step, target - x)
            state = _rk4_step(mode, state, step)
            x += step
            steps += 1
            drift = abs(_signed_current(state) - initial_current) / abs(initial_current)
            max_current_drift = max(max_current_drift, drift)
        # r is an analytic coordinate state.  Reset it at an exact checkpoint;
        # the pre-reset drift is a discretization diagnostic, not science data.
        state[0] = radius
        outputs[mp.nstr(radius, 30)] = list(state)
    return outputs, steps, max_current_drift, initial_state


def _validate_evaluation_points(
    evaluation_points: Sequence[MpmathEvaluationPoint],
) -> tuple[MpmathEvaluationPoint, ...]:
    points = tuple(evaluation_points)
    if not points or any(not isinstance(point, MpmathEvaluationPoint) for point in points):
        raise MpmathRadialContractError("evaluation points must be explicit immutable inputs")
    if len({point.point_id for point in points}) != len(points):
        raise MpmathRadialContractError("evaluation point IDs must be unique")
    radii = [mp.mpf(point.radius_M) for point in points]
    if len(set(radii)) != len(radii):
        raise MpmathRadialContractError("evaluation point radii must be unique")
    return points


def _integrate_state_to_radii(
    mode: MpmathMode,
    state: Sequence[mp.mpf | mp.mpc],
    *,
    start_rstar: mp.mpf,
    radii: Sequence[mp.mpf],
    maximum_step_rstar: mp.mpf,
    outward: bool,
) -> tuple[dict[str, list[mp.mpf | mp.mpc]], int, mp.mpf]:
    """Integrate a one- or multi-field state to exact ordered radius checkpoints."""

    ordered = sorted({mp.mpf(value) for value in radii}, reverse=not outward)
    current = list(state)
    x = mp.mpf(start_rstar)
    outputs: dict[str, list[mp.mpf | mp.mpc]] = {}
    steps = 0
    maximum_radius_error = mp.mpf(0)
    for radius in ordered:
        target = schwarzschild_rstar(radius)
        if outward and target <= x:
            raise MpmathRadialContractError("outward checkpoint is not ahead")
        if not outward and target >= x:
            raise MpmathRadialContractError("inward checkpoint is not behind")
        while (x < target) if outward else (x > target):
            remaining = abs(target - x)
            step = min(maximum_step_rstar, remaining)
            signed_step = step if outward else -step
            current = _rk4_step(mode, current, signed_step)
            x += signed_step
            steps += 1
        radius_error = mp.mpf(current[0]) - radius
        maximum_radius_error = max(maximum_radius_error, abs(radius_error))
        current[0] = radius
        outputs[mp.nstr(radius, 30)] = list(current)
    return outputs, steps, maximum_radius_error


def _complex_record(value: mp.mpc, digits: int) -> dict[str, str]:
    if not isinstance(digits, int) or isinstance(digits, bool) or digits < 2:
        raise MpmathRadialContractError("complex record digits must be an integer >= 2")
    # The three decimal fields form one evidence record.  Round the Cartesian
    # components first and derive the magnitude from those exact serialized
    # values; separately rounding |z| can otherwise violate the validator at
    # the final quoted digit, especially for exponentially small T_H values.
    with mp.workdps(max(80, digits + 20)):
        result = mp.mpc(value)
        real_text = mp.nstr(mp.re(result), digits)
        imag_text = mp.nstr(mp.im(result), digits)
        serialized = mp.mpc(mp.mpf(real_text), mp.mpf(imag_text))
        return {
            "real": real_text,
            "imag": imag_text,
            "abs": mp.nstr(abs(serialized), digits),
        }


def _real_record(value: mp.mpf, digits: int) -> str:
    return mp.nstr(mp.mpf(value), digits)


def complex_from_record(value: object) -> complex:
    """Decode a complex record lossily for UI/tests, never evidence arithmetic."""

    if not isinstance(value, Mapping) or set(value) != {"real", "imag", "abs"}:
        raise MpmathRadialContractError("complex record schema mismatch")
    result = complex(float(value["real"]), float(value["imag"]))
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise MpmathRadialContractError("complex record is non-finite")
    return result


def _diagnostic_outward_match_unreachable(
    *,
    mode: MpmathMode,
    state: Sequence[mp.mpf | mp.mpc],
    radius: mp.mpf,
    order: int,
    initial_state: Sequence[mp.mpf | mp.mpc],
    config: MpmathSolveConfig,
    integration_steps: int,
    max_current_drift: mp.mpf,
    evaluation_states: Mapping[str, Sequence[mp.mpf | mp.mpc]],
    evaluation_points: Sequence[MpmathEvaluationPoint],
    elapsed_seconds: float,
) -> dict[str, object]:
    """Consumed-v1 outward diagnostic; unreachable from the authoritative solver."""
    k = mp.mpf(str(mode.kM))
    actual_radius = mp.mpf(state[0])
    (
        incoming,
        incoming_p,
        incoming_order,
        incoming_tail,
        _incoming_cap,
        _incoming_threshold,
        _incoming_termination,
    ) = independent_jost_basis(
        sector=mode.sector,
        ell=mode.ell,
        k=k,
        radius=actual_radius,
        sign=-1,
        order_cap=order,
    )
    (
        outgoing,
        outgoing_p,
        outgoing_order,
        outgoing_tail,
        _outgoing_cap,
        _outgoing_threshold,
        _outgoing_termination,
    ) = independent_jost_basis(
        sector=mode.sector,
        ell=mode.ell,
        k=k,
        radius=actual_radius,
        sign=1,
        order_cap=order,
    )
    psi = mp.mpc(state[1])
    momentum = mp.mpc(state[2])
    determinant = incoming * outgoing_p - incoming_p * outgoing
    if determinant == 0:
        raise MpmathRadialContractError("singular independent Jost matching matrix")
    a_in = (psi * outgoing_p - momentum * outgoing) / determinant
    a_out = (incoming * momentum - incoming_p * psi) / determinant
    if a_in == 0:
        raise MpmathRadialContractError("matched A_in is zero")
    reconstructed_psi = a_in * incoming + a_out * outgoing
    reconstructed_p = a_in * incoming_p + a_out * outgoing_p
    match_residual = max(
        abs(reconstructed_psi - psi) / max(abs(psi), mp.eps),
        abs(reconstructed_p - momentum) / max(abs(momentum), mp.eps),
    )
    inverse_norm = max(
        abs(outgoing_p / determinant),
        abs(outgoing / determinant),
        abs(incoming_p / determinant),
        abs(incoming / determinant),
    )
    condition_estimate = max(
        abs(incoming), abs(outgoing), abs(incoming_p), abs(outgoing_p)
    ) * inverse_norm
    reflection_amplitude = a_out / a_in
    phase_factor = -a_out / (((-1) ** mode.ell) * a_in)
    f_infinity_in = -2 * k * abs(a_in) ** 2
    f_infinity_out = 2 * k * abs(a_out) ** 2
    f_horizon = 2 * _signed_current(initial_state)
    absolute_balance = abs((f_infinity_in + f_infinity_out) - f_horizon)
    relative_balance = absolute_balance / abs(f_infinity_in)
    reflection_fraction = abs(reflection_amplitude) ** 2
    transmission_fraction = -f_horizon / -f_infinity_in
    fraction_balance = abs(reflection_fraction + transmission_fraction - 1)
    resolution_floor = mp.power(10, -(config.working_dps - 10))
    transmission_resolved = transmission_fraction > resolution_floor
    digits = min(config.working_dps, 100)
    finite_states = []
    for point in _validate_evaluation_points(evaluation_points):
        point_id = point.point_id
        requested_radius = mp.mpf(point.radius_M)
        evaluation_state = evaluation_states[mp.nstr(requested_radius, 30)]
        eval_radius = mp.mpf(evaluation_state[0])
        eval_lapse = 1 - 2 / eval_radius
        eval_psi = mp.mpc(evaluation_state[1])
        eval_p = mp.mpc(evaluation_state[2])
        finite_states.append(
            {
                "point_id": point_id,
                "radius_M": _real_record(requested_radius, digits),
                "actual_radius_M": _real_record(eval_radius, digits),
                "psi_over_Ain": _complex_record(eval_psi / a_in, digits),
                "dpsi_dr_over_Ain": _complex_record(
                    eval_p / (eval_lapse * a_in), digits
                ),
            }
        )
    return {
        "schema_version": BACKEND_SCHEMA,
        "mode": mode.to_metadata(),
        "backend": {
            "actual_backend": f"mpmath {mp.__version__}",
            "requested_precision_dps": config.working_dps,
            "actual_decimal_digits": mp.mp.dps,
            "actual_precision_bits": mp.mp.prec,
            "rounding": "mpmath libmp nearest",
            "guard_digits": 0,
            "genuinely_independent": True,
            "even_independent_solve": mode.sector == "even",
            "shared_components": ["RW/Zerilli equations and scattering conventions only"],
        },
        "configuration": {
            "M": 1,
            "Fourier_convention": "exp(-i k t)",
            "r_in_eps": config.r_in_eps,
            "r_out_M": float(radius),
            "actual_r_out_M": _real_record(actual_radius, digits),
            "r_out_radius_error": _real_record(actual_radius - radius, digits),
            "maximum_step_rstar": config.maximum_step_rstar,
            "Jost_order_cap": order,
            "horizon_normalization": "unit exp(-i k r_star)",
            "outer_basis": "local exp(+-i k r_star) sum(a_n/r^n)",
            "integration_architecture": "outward_horizon_normalized",
        },
        "horizon_normalized_A_in": _complex_record(a_in, digits),
        "horizon_normalized_A_out": _complex_record(a_out, digits),
        "reflection_amplitude_Aout_over_Ain": _complex_record(
            reflection_amplitude, digits
        ),
        "S": _complex_record(phase_factor, digits),
        "finite_radius_states": finite_states,
        "signed_flux": {
            "F_inf_in": _real_record(f_infinity_in, digits),
            "F_inf_out": _real_record(f_infinity_out, digits),
            "F_H": _real_record(f_horizon, digits),
            "F_loss": "0.0",
            "horizon_flux_source": "direct unit-horizon inner current",
            "horizon_flux_inferred_from_one_minus_R": False,
            "reflection_fraction": _real_record(reflection_fraction, digits),
            "horizon_transmission_fraction": _real_record(
                transmission_fraction, digits
            ),
            "absolute_balance_residual": _real_record(absolute_balance, digits),
            "relative_balance_residual": _real_record(relative_balance, digits),
            "fraction_balance_residual": _real_record(fraction_balance, digits),
            "transmission_resolution_floor": _real_record(resolution_floor, digits),
            "transmission_resolved_at_actual_precision": transmission_resolved,
            "acceptance_scope": "internal accounting plus independent algorithm comparison",
        },
        "wronskian": {
            "inner_signed_current": _real_record(_signed_current(initial_state), digits),
            "outer_signed_current": _real_record(_signed_current(state), digits),
            "inner_W": _complex_record(2j * _signed_current(initial_state), digits),
            "outer_W": _complex_record(2j * _signed_current(state), digits),
            "maximum_relative_current_drift": _real_record(
                max_current_drift, digits
            ),
        },
        "matching": {
            "reconstruction_residual": _real_record(match_residual, digits),
            "condition_estimate": _real_record(condition_estimate, digits),
            "incoming_effective_order": incoming_order,
            "outgoing_effective_order": outgoing_order,
            "maximum_tail_ratio": _real_record(
                max(incoming_tail, outgoing_tail), digits
            ),
        },
        "integration": {
            "steps": integration_steps,
            "elapsed_seconds": elapsed_seconds,
            "checkpoint_reuse": "one integration reused for eight finite radii and r_out nodes",
        },
    }


def _bidirectional_match(
    *,
    mode: MpmathMode,
    config: MpmathSolveConfig,
    r_out: mp.mpf,
    order: int,
    horizon_states: Mapping[str, Sequence[mp.mpf | mp.mpc]],
    horizon_initial: Sequence[mp.mpf | mp.mpc],
    horizon_steps: int,
    horizon_drift: mp.mpf,
    elapsed_seconds: float,
    evaluation_points: Sequence[MpmathEvaluationPoint],
) -> dict[str, object]:
    """Match inward independent Jost bases to the horizon log derivative."""

    k = mp.mpf(str(mode.kM))
    (
        incoming,
        incoming_p,
        incoming_order,
        incoming_tail,
        incoming_cap,
        incoming_threshold,
        incoming_termination,
    ) = independent_jost_basis(
        sector=mode.sector,
        ell=mode.ell,
        k=k,
        radius=r_out,
        sign=-1,
        order_cap=order,
    )
    (
        outgoing,
        outgoing_p,
        outgoing_order,
        outgoing_tail,
        outgoing_cap,
        outgoing_threshold,
        outgoing_termination,
    ) = independent_jost_basis(
        sector=mode.sector,
        ell=mode.ell,
        k=k,
        radius=r_out,
        sign=1,
        order_cap=order,
    )
    outer_state: list[mp.mpf | mp.mpc] = [
        r_out,
        incoming,
        incoming_p,
        outgoing,
        outgoing_p,
    ]
    points = _validate_evaluation_points(evaluation_points)
    finite_radii = tuple(mp.mpf(point.radius_M) for point in points)
    match_radius = mp.mpf(str(config.pilot_match_radius_M))
    targets = tuple(finite_radii) + (match_radius,)
    outer_states, outer_steps, radius_drift = _integrate_state_to_radii(
        mode,
        outer_state,
        start_rstar=schwarzschild_rstar(r_out),
        radii=targets,
        maximum_step_rstar=mp.mpf(str(config.maximum_step_rstar)),
        outward=False,
    )
    match = outer_states[mp.nstr(match_radius, 30)]
    horizon = list(horizon_states[mp.nstr(match_radius, 30)])
    horizon[0] = match_radius
    h = mp.mpc(horizon[1])
    hp = mp.mpc(horizon[2])
    incoming_match = mp.mpc(match[1])
    incoming_p_match = mp.mpc(match[2])
    outgoing_match = mp.mpc(match[3])
    outgoing_p_match = mp.mpc(match[4])
    if h == 0:
        raise MpmathRadialContractError("horizon solution vanished at match radius")
    log_derivative = hp / h
    denominator = outgoing_p_match - log_derivative * outgoing_match
    if denominator == 0:
        raise MpmathRadialContractError("singular bidirectional match denominator")
    reflection_amplitude = (
        log_derivative * incoming_match - incoming_p_match
    ) / denominator
    physical_match = incoming_match + reflection_amplitude * outgoing_match
    physical_p_match = incoming_p_match + reflection_amplitude * outgoing_p_match
    transmission_amplitude = physical_match / h
    if transmission_amplitude == 0:
        raise MpmathRadialContractError("unit-incoming horizon amplitude vanished")
    horizon_normalized_a_in = 1 / transmission_amplitude
    horizon_normalized_a_out = reflection_amplitude / transmission_amplitude
    log_match_residual = abs(
        physical_p_match / physical_match - log_derivative
    )
    phase_factor = -reflection_amplitude / ((-1) ** mode.ell)
    f_infinity_in = -2 * k
    f_infinity_out = 2 * k * abs(reflection_amplitude) ** 2
    f_horizon = -2 * k * abs(transmission_amplitude) ** 2
    absolute_balance = abs((f_infinity_in + f_infinity_out) - f_horizon)
    relative_balance = absolute_balance / abs(f_infinity_in)
    reflection_fraction = abs(reflection_amplitude) ** 2
    transmission_fraction = abs(transmission_amplitude) ** 2
    fraction_balance = abs(reflection_fraction + transmission_fraction - 1)
    resolution_floor = mp.power(10, -(config.working_dps - 10))
    transmission_resolved = transmission_fraction > resolution_floor
    physical_currents: list[mp.mpf] = []
    cancellation_conditions: list[mp.mpf] = []
    outer_state_relative_residuals: list[mp.mpf] = []
    finite_states: list[dict[str, object]] = []
    digits = min(config.working_dps, 100)
    for point, requested_radius in zip(points, finite_radii):
        point_id = point.point_id
        state = outer_states[mp.nstr(requested_radius, 30)]
        horizon_finite = horizon_states[mp.nstr(requested_radius, 30)]
        radius = mp.mpf(state[0])
        lapse = 1 - 2 / radius
        incoming_term = mp.mpc(state[1])
        outgoing_term = reflection_amplitude * mp.mpc(state[3])
        incoming_p_term = mp.mpc(state[2])
        outgoing_p_term = reflection_amplitude * mp.mpc(state[4])
        outer_psi = incoming_term + outgoing_term
        outer_momentum = incoming_p_term + outgoing_p_term
        psi = transmission_amplitude * mp.mpc(horizon_finite[1])
        momentum = transmission_amplitude * mp.mpc(horizon_finite[2])
        cancellation_condition = max(
            (abs(incoming_term) + abs(outgoing_term)) / max(abs(outer_psi), mp.eps),
            (abs(incoming_p_term) + abs(outgoing_p_term))
            / max(abs(outer_momentum), mp.eps),
        )
        cancellation_conditions.append(cancellation_condition)
        outer_state_relative_residual = max(
            abs(outer_psi - psi) / max(abs(outer_psi), abs(psi), mp.eps),
            abs(outer_momentum - momentum)
            / max(abs(outer_momentum), abs(momentum), mp.eps),
        )
        outer_state_relative_residuals.append(outer_state_relative_residual)
        physical_currents.append(mp.im(mp.conj(psi) * momentum))
        finite_states.append(
            {
                "point_id": point_id,
                "radius_M": _real_record(requested_radius, digits),
                "actual_radius_M": _real_record(radius, digits),
                "psi_over_Ain": _complex_record(psi, digits),
                "dpsi_dr_over_Ain": _complex_record(momentum / lapse, digits),
                "authoritative_branch": "T_H times outward horizon solution",
                "outer_combination_crosscheck": {
                    "psi_over_Ain": _complex_record(outer_psi, digits),
                    "dpsi_dr_over_Ain": _complex_record(
                        outer_momentum / lapse, digits
                    ),
                    "cancellation_condition": _real_record(
                        cancellation_condition, digits
                    ),
                    "relative_to_authoritative_state_residual": _real_record(
                        outer_state_relative_residual, digits
                    ),
                },
            }
        )
    physical_current_match = mp.im(
        mp.conj(physical_match) * physical_p_match
    )
    current_scale = max(abs(physical_current_match), mp.eps)
    physical_drift = max(
        (abs(value - physical_current_match) / current_scale for value in physical_currents),
        default=mp.mpf(0),
    )
    maximum_current_drift = max(horizon_drift, physical_drift)
    raw_unit_horizon_current = _signed_current(horizon_initial)
    inner_physical_current = abs(transmission_amplitude) ** 2 * raw_unit_horizon_current
    condition_estimate = (
        max(abs(incoming_match), abs(outgoing_match), abs(log_derivative))
        / max(abs(denominator), mp.eps)
    )
    basis_determinant = incoming_match * outgoing_p_match - (
        incoming_p_match * outgoing_match
    )
    determinant_scale = max(
        abs(incoming_match * outgoing_p_match)
        + abs(incoming_p_match * outgoing_match),
        mp.eps,
    )
    determinant_relative = abs(basis_determinant) / determinant_scale
    conjugacy_value_residual = abs(outgoing - mp.conj(incoming)) / max(
        abs(outgoing), abs(incoming), mp.eps
    )
    conjugacy_derivative_residual = abs(outgoing_p - mp.conj(incoming_p)) / max(
        abs(outgoing_p), abs(incoming_p), mp.eps
    )
    jost_health_threshold = mp.power(10, -min(20, config.working_dps // 3))
    incoming_acceptable = (not incoming_cap) or incoming_tail <= incoming_threshold
    outgoing_acceptable = (not outgoing_cap) or outgoing_tail <= outgoing_threshold
    selected_jost_gate_passed = (
        incoming_acceptable
        and outgoing_acceptable
        and conjugacy_value_residual <= jost_health_threshold
        and conjugacy_derivative_residual <= jost_health_threshold
        and determinant_relative >= jost_health_threshold
        and condition_estimate <= 1 / jost_health_threshold
    )
    cancellation_limit = mp.power(10, config.working_dps - 10)
    outer_residual_limit = mp.power(10, -min(20, config.working_dps // 3))
    outer_crosscheck_resolved = (
        max(cancellation_conditions) < cancellation_limit
        and max(outer_state_relative_residuals) < outer_residual_limit
    )
    return {
        "schema_version": BACKEND_SCHEMA,
        "mode": mode.to_metadata(),
        "backend": {
            "actual_backend": f"mpmath {mp.__version__}",
            "requested_precision_dps": config.working_dps,
            "actual_decimal_digits": mp.mp.dps,
            "actual_precision_bits": mp.mp.prec,
            "rounding": "mpmath libmp nearest",
            "guard_digits": 0,
            "genuinely_independent": True,
            "even_independent_solve": mode.sector == "even",
            "shared_components": ["RW/Zerilli equations and scattering conventions only"],
        },
        "configuration": {
            "M": 1,
            "Fourier_convention": "exp(-i k t)",
            "r_in_eps": config.r_in_eps,
            "r_out_M": float(r_out),
            "actual_r_out_M": _real_record(r_out, digits),
            "r_out_radius_error": "0.0",
            "maximum_step_rstar": config.maximum_step_rstar,
            "Jost_order_cap": order,
            "horizon_normalization": "unit exp(-i k r_star) propagated only to common match radius",
            "outer_basis": "independent local J_in/J_out propagated inward",
            "integration_architecture": "bidirectional_log_derivative_match",
            "common_match_radius_M": float(match_radius),
            "match_radius_policy": "explicit frozen Stage-A pilot node; not a generic backend policy",
        },
        "unit_incoming_A_in": _complex_record(mp.mpc(1), digits),
        "unit_incoming_A_out": _complex_record(reflection_amplitude, digits),
        "horizon_normalized_A_in": _complex_record(
            horizon_normalized_a_in, digits
        ),
        "horizon_normalized_A_out": _complex_record(
            horizon_normalized_a_out, digits
        ),
        "reflection_amplitude_Aout_over_Ain": _complex_record(
            reflection_amplitude, digits
        ),
        "S": _complex_record(phase_factor, digits),
        "unit_incoming_horizon_amplitude_T_H": _complex_record(
            transmission_amplitude, digits
        ),
        "finite_radius_states": finite_states,
        "finite_radius_state_resolution": {
            "authoritative_construction": "T_H*H(r) from a single outward horizon pass",
            "outer_combination_is_authoritative": False,
            "outer_combination_max_cancellation_condition": _real_record(
                max(cancellation_conditions), digits
            ),
            "outer_combination_resolution_limit": _real_record(
                cancellation_limit, digits
            ),
            "outer_combination_max_relative_to_authoritative_residual": _real_record(
                max(outer_state_relative_residuals), digits
            ),
            "outer_combination_relative_residual_limit": _real_record(
                outer_residual_limit, digits
            ),
            "outer_combination_crosscheck_resolved": outer_crosscheck_resolved,
            "complex_log_amplitude_required_for_generic_float64_backend": True,
        },
        "signed_flux": {
            "F_inf_in": _real_record(f_infinity_in, digits),
            "F_inf_out": _real_record(f_infinity_out, digits),
            "F_H": _real_record(f_horizon, digits),
            "F_loss": "0.0",
            "horizon_flux_source": "direct |T_H|^2 from bidirectional match; not inferred from R",
            "horizon_flux_inferred_from_one_minus_R": False,
            "reflection_fraction": _real_record(reflection_fraction, digits),
            "horizon_transmission_fraction": _real_record(transmission_fraction, digits),
            "absolute_balance_residual": _real_record(absolute_balance, digits),
            "relative_balance_residual": _real_record(relative_balance, digits),
            "fraction_balance_residual": _real_record(fraction_balance, digits),
            "transmission_resolution_floor": _real_record(resolution_floor, digits),
            "transmission_resolved_at_actual_precision": transmission_resolved,
            "candidate_outputs_separately_assessable": True,
            "acceptance_scope": "independent S/finite-state comparison; flux closure only when resolved",
        },
        "wronskian": {
            "raw_unit_horizon_signed_current": _real_record(
                raw_unit_horizon_current, digits
            ),
            "inner_signed_current": _real_record(inner_physical_current, digits),
            "outer_signed_current": _real_record(physical_current_match, digits),
            "inner_W": _complex_record(2j * inner_physical_current, digits),
            "outer_W": _complex_record(2j * physical_current_match, digits),
            "maximum_relative_current_drift": _real_record(maximum_current_drift, digits),
        },
        "matching": {
            "reconstruction_residual": _real_record(log_match_residual, digits),
            "condition_estimate": _real_record(condition_estimate, digits),
            "incoming_effective_order": incoming_order,
            "outgoing_effective_order": outgoing_order,
            "maximum_tail_ratio": _real_record(max(incoming_tail, outgoing_tail), digits),
            "incoming_tail_ratio": _real_record(incoming_tail, digits),
            "outgoing_tail_ratio": _real_record(outgoing_tail, digits),
            "incoming_tail_threshold": _real_record(incoming_threshold, digits),
            "outgoing_tail_threshold": _real_record(outgoing_threshold, digits),
            "incoming_cap_reached": incoming_cap,
            "outgoing_cap_reached": outgoing_cap,
            "incoming_termination_reason": incoming_termination,
            "outgoing_termination_reason": outgoing_termination,
            "conjugacy_value_residual": _real_record(
                conjugacy_value_residual, digits
            ),
            "conjugacy_derivative_residual": _real_record(
                conjugacy_derivative_residual, digits
            ),
            "basis_determinant": _complex_record(basis_determinant, digits),
            "basis_determinant_relative": _real_record(
                determinant_relative, digits
            ),
            "jost_health_threshold": _real_record(jost_health_threshold, digits),
            "selected_jost_gate_passed": selected_jost_gate_passed,
            "coarse_cap_reached_permitted_as_raw_ladder_only": True,
        },
        "integration": {
            "steps": horizon_steps + outer_steps,
            "horizon_steps": horizon_steps,
            "outer_basis_steps": outer_steps,
            "maximum_radius_state_drift": _real_record(radius_drift, digits),
            "elapsed_seconds": elapsed_seconds,
            "checkpoint_reuse": "one outward horizon pass supplies H at match/eight radii; one inward two-basis pass supplies match and optional crosschecks",
        },
    }


def solve_mode_batch(
    mode: MpmathMode,
    config: MpmathSolveConfig,
    *,
    evaluation_points: Sequence[MpmathEvaluationPoint],
    r_out_nodes: Sequence[float],
    jost_orders: Sequence[int],
) -> dict[str, object]:
    """Solve one mode and reuse integrations across finite radii/ladders."""

    points = _validate_evaluation_points(evaluation_points)
    if not r_out_nodes or not jost_orders:
        raise MpmathRadialContractError("r_out and Jost ladders must be non-empty")
    largest_inner_radius = max(
        mp.mpf(str(config.pilot_match_radius_M)),
        *(mp.mpf(point.radius_M) for point in points),
    )
    if any(mp.mpf(str(value)) <= largest_inner_radius for value in r_out_nodes):
        raise MpmathRadialContractError("r_out must exceed match/evaluation radii")
    if len(set(r_out_nodes)) != len(r_out_nodes) or len(set(jost_orders)) != len(
        jost_orders
    ):
        raise MpmathRadialContractError("ladder nodes must be unique")
    started = time.perf_counter()
    with mp.workdps(config.working_dps):
        matches: list[dict[str, object]] = []
        match_radius = mp.mpf(str(config.pilot_match_radius_M))
        if any(mp.mpf(point.radius_M) >= match_radius for point in points):
            raise MpmathRadialContractError(
                "pilot match radius must exceed every requested finite-state radius"
            )
        horizon_states, horizon_steps, drift, initial = _integrate_to_radii(
            mode,
            config,
            tuple(mp.mpf(point.radius_M) for point in points) + (match_radius,),
        )
        for r_out in r_out_nodes:
            radius = mp.mpf(str(r_out))
            for order in jost_orders:
                matches.append(
                    _bidirectional_match(
                        mode=mode,
                        config=config,
                        r_out=radius,
                        order=order,
                        horizon_states=horizon_states,
                        horizon_initial=initial,
                        horizon_steps=horizon_steps,
                        horizon_drift=drift,
                        elapsed_seconds=time.perf_counter() - started,
                        evaluation_points=points,
                    )
                )
        steps = horizon_steps + sum(
            int(item["integration"]["outer_basis_steps"]) for item in matches
        )
        elapsed = time.perf_counter() - started
    return {
        "mode": mode.to_metadata(),
        "configuration": {
            "working_dps": config.working_dps,
            "r_in_eps": config.r_in_eps,
            "maximum_step_rstar": config.maximum_step_rstar,
            "pilot_match_radius_M": config.pilot_match_radius_M,
            "evaluation_points": [point.to_metadata() for point in points],
            "r_out_nodes": list(r_out_nodes),
            "jost_orders": list(jost_orders),
        },
        "integration_steps": steps,
        "elapsed_seconds": elapsed,
        "matches": matches,
    }


def result_for(
    batch: Mapping[str, object], *, r_out: float, jost_order: int
) -> Mapping[str, object]:
    matches = batch.get("matches")
    if not isinstance(matches, list):
        raise MpmathRadialContractError("batch matches are missing")
    selected = [
        item
        for item in matches
        if isinstance(item, Mapping)
        and item.get("configuration", {}).get("r_out_M") == r_out
        and item.get("configuration", {}).get("Jost_order_cap") == jost_order
    ]
    if len(selected) != 1:
        raise MpmathRadialContractError("requested batch result is not unique")
    return selected[0]


def prove_call_graph_isolation(path: str | Path) -> dict[str, object]:
    """AST-audit the backend source for forbidden imports and call surfaces."""

    source_path = Path(path).resolve(strict=True)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: list[str] = []
    calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
    forbidden_imports = sorted(
        name
        for name in imports
        if any(name == prefix or name.startswith(f"{prefix}.") for prefix in _FORBIDDEN_IMPORT_PREFIXES)
    )
    forbidden_calls = sorted(set(calls).intersection(_FORBIDDEN_CALL_NAMES))
    diagnostic_outward_calls = calls.count("_diagnostic_outward_match_unreachable")
    if forbidden_imports or forbidden_calls or diagnostic_outward_calls:
        raise MpmathRadialContractError("independent backend call graph is contaminated")
    return {
        "source_path": str(source_path),
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "imports": sorted(set(imports)),
        "forbidden_imports": forbidden_imports,
        "forbidden_calls": forbidden_calls,
        "project_scipy_radial_solver_called": False,
        "project_jost_called": False,
        "project_matching_called": False,
        "consumed_outward_diagnostic_call_count": diagnostic_outward_calls,
        "authoritative_solver_architecture": "bidirectional for every mode; regime label is metadata only",
        "isolation_passed": True,
    }


def validate_stage_a_evidence(payload: Mapping[str, object]) -> None:
    """Fail closed on malformed or overstated selected-anchor evidence."""

    required = {
        "schema_version",
        "scope",
        "overall_status",
        "global_green_permitted",
        "evaluation_point_contract",
        "runtime_identity",
        "execution_contract",
        "declared_domain",
        "backend_identity",
        "call_graph_isolation",
        "diagnostic_thresholds",
        "consumed_diagnostic_roots",
        "modes",
        "source_identities",
        "limitations",
        "runtime_cost",
    }
    if set(payload) != required or payload.get("schema_version") != EVIDENCE_SCHEMA:
        raise MpmathRadialContractError("Stage-A evidence schema mismatch")
    if payload.get("scope") != "bounded_selected_anchor_pilot":
        raise MpmathRadialContractError("Stage-A scope mismatch")
    if payload.get("global_green_permitted") is not False:
        raise MpmathRadialContractError("selected anchors cannot claim global GREEN")
    if payload.get("overall_status") == "GREEN":
        raise MpmathRadialContractError("selected anchors cannot claim V1 GREEN")
    _validate_runtime_identity(payload.get("runtime_identity"))
    _validate_execution_contract(payload.get("execution_contract"))
    point_contract = payload.get("evaluation_point_contract")
    if not isinstance(point_contract, Mapping) or set(point_contract) != {
        "points",
        "sha256",
        "role",
    }:
        raise MpmathRadialContractError("evaluation-point contract schema mismatch")
    raw_points = point_contract.get("points")
    if not isinstance(raw_points, list) or len(raw_points) != 8:
        raise MpmathRadialContractError("evaluation-point inventory mismatch")
    try:
        evaluation_points = tuple(
            MpmathEvaluationPoint(
                point_id=item["point_id"], radius_M=item["radius_M"]
            )
            for item in raw_points
            if isinstance(item, Mapping) and set(item) == {"point_id", "radius_M"}
        )
    except (KeyError, TypeError) as exc:
        raise MpmathRadialContractError("evaluation-point record malformed") from exc
    if len(evaluation_points) != len(raw_points):
        raise MpmathRadialContractError("evaluation-point record malformed")
    _validate_evaluation_points(evaluation_points)
    point_bytes = (
        json.dumps(raw_points, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")
    if (
        point_contract.get("sha256") != hashlib.sha256(point_bytes).hexdigest()
        or point_contract.get("role")
        != "Stage-A runner-frozen finite-state requests; generic backend input"
    ):
        raise MpmathRadialContractError("evaluation-point contract identity mismatch")
    thresholds = payload.get("diagnostic_thresholds")
    if (
        not isinstance(thresholds, Mapping)
        or thresholds.get("adaptive_tolerance_ladder_present") is not False
        or "provisional" not in str(thresholds.get("scope"))
    ):
        raise MpmathRadialContractError("diagnostic thresholds are overstated")
    consumed = payload.get("consumed_diagnostic_roots")
    if (
        not isinstance(consumed, list)
        or len(consumed) != 3
        or any(item.get("authoritative") is not False for item in consumed)
    ):
        raise MpmathRadialContractError("consumed diagnostic root binding is missing")
    for item in consumed:
        if not isinstance(item, Mapping) or set(item) != {
            "path",
            "role",
            "authoritative",
            "evidence_sha256",
            "manifest_sha256",
            "checkpoint_sha256",
        }:
            raise MpmathRadialContractError("consumed diagnostic root schema mismatch")
        root = Path(str(item["path"]))
        if root.is_symlink() or not root.is_dir() or root.resolve(strict=True) != root:
            raise MpmathRadialContractError("consumed diagnostic root path drift")
        for filename, identity_key in (
            ("selected_anchor_evidence.json", "evidence_sha256"),
            ("manifest.json", "manifest_sha256"),
            ("checkpoint.json", "checkpoint_sha256"),
        ):
            artifact = root / filename
            if artifact.is_symlink() or not artifact.is_file():
                raise MpmathRadialContractError("consumed diagnostic artifact missing")
            info = artifact.stat()
            if info.st_nlink != 1 or hashlib.sha256(artifact.read_bytes()).hexdigest() != item[
                identity_key
            ]:
                raise MpmathRadialContractError("consumed diagnostic artifact drift")
    isolation = payload.get("call_graph_isolation")
    if (
        not isinstance(isolation, Mapping)
        or set(isolation)
        != {
            "source_path",
            "source_sha256",
            "imports",
            "forbidden_imports",
            "forbidden_calls",
            "project_scipy_radial_solver_called",
            "project_jost_called",
            "project_matching_called",
            "consumed_outward_diagnostic_call_count",
            "authoritative_solver_architecture",
            "isolation_passed",
        }
        or isolation.get("isolation_passed") is not True
        or isolation.get("forbidden_imports") != []
        or isolation.get("forbidden_calls") != []
        or isolation.get("consumed_outward_diagnostic_call_count") != 0
    ):
        raise MpmathRadialContractError("call-graph isolation is missing")
    backend = payload.get("backend_identity")
    if not isinstance(backend, Mapping) or set(backend) != {
        "name",
        "implementation_version",
        "implementation_source_sha256",
        "actual_backend",
        "genuinely_independent",
        "input_sha256",
        "dependency_hashes",
        "shared_components",
        "call_graph_isolation",
        "project_scipy_radial_solver_in_backend_call_graph",
        "project_jost_in_backend_call_graph",
        "project_matching_in_backend_call_graph",
    }:
        raise MpmathRadialContractError("backend identity is missing")
    if backend.get("actual_backend") != f"mpmath {mp.__version__}":
        raise MpmathRadialContractError("actual backend identity mismatch")
    if backend.get("genuinely_independent") is not True:
        raise MpmathRadialContractError("backend independence is overstated")
    if (
        backend.get("name") != "independent_mpmath_rw_zerilli_rk4_jost"
        or backend.get("implementation_version") != BACKEND_SCHEMA
        or backend.get("implementation_source_sha256")
        != isolation.get("source_sha256")
        or not isinstance(backend.get("input_sha256"), str)
        or len(backend["input_sha256"]) != 64
        or backend.get("shared_components")
        != ["RW/Zerilli equations and scattering conventions only"]
        or backend.get("call_graph_isolation")
        != "AST/import audit; no project SciPy radial/Jost/matching imports or calls"
        or any(
            backend.get(field) is not False
            for field in (
                "project_scipy_radial_solver_in_backend_call_graph",
                "project_jost_in_backend_call_graph",
                "project_matching_in_backend_call_graph",
            )
        )
    ):
        raise MpmathRadialContractError("backend provenance/independence mismatch")
    dependency_hashes = backend.get("dependency_hashes")
    if (
        not isinstance(dependency_hashes, Mapping)
        or set(dependency_hashes) != {"mpmath_source_sha256"}
        or dependency_hashes["mpmath_source_sha256"]
        != hashlib.sha256(Path(mp.__file__).read_bytes()).hexdigest()
    ):
        raise MpmathRadialContractError("backend dependency identity mismatch")
    domain = payload.get("declared_domain")
    if not isinstance(domain, Mapping) or domain.get("covered_key_count") != 8:
        raise MpmathRadialContractError("selected-anchor inventory mismatch")
    if domain.get("production_deduplicated_key_count") != 16048:
        raise MpmathRadialContractError("production-domain inventory mismatch")
    if domain.get("policy_extended_union_key_count") != 17818:
        raise MpmathRadialContractError("policy-union inventory mismatch")
    _validate_domain_freeze(domain)
    if domain.get("full_v1_domain_complete") is not False:
        raise MpmathRadialContractError("Stage A cannot close the full V1 domain")
    modes = payload.get("modes")
    if not isinstance(modes, list) or len(modes) != 8:
        raise MpmathRadialContractError("Stage-A mode records are incomplete")
    expected = [mode.to_metadata() for mode in selected_stage_a_modes()]
    if [record.get("mode") for record in modes] != expected:
        raise MpmathRadialContractError("Stage-A mode order mismatch")
    for record in modes:
        if not isinstance(record, Mapping):
            raise MpmathRadialContractError("mode evidence is malformed")
        if record.get("status") not in {
            "STABLE_SELECTED_ANCHOR_INCOMPLETE_LADDERS",
            "FAIL_CLOSED_NUMERICAL_INSTABILITY",
        }:
            raise MpmathRadialContractError("mode status is invalid")
        ladders = record.get("ladders")
        if not isinstance(ladders, Mapping) or set(ladders) != {
            "precision_dps",
            "step_rstar",
            "r_in_eps",
            "r_out_M",
            "jost_order",
        }:
            raise MpmathRadialContractError("mode ladder inventory mismatch")
        if ladders["precision_dps"].get("nodes") != [50, 70, 100]:
            raise MpmathRadialContractError("50/70/100 precision ladder missing")
        for axis in ladders.values():
            if axis.get("closure_permitted") is not False:
                raise MpmathRadialContractError("bounded ladder cannot claim closure")
        for axis_name, axis in ladders.items():
            _validate_axis_evidence(axis_name, axis)
        baseline = record.get("baseline")
        if not isinstance(baseline, Mapping):
            if set(record) != {
                "mode",
                "status",
                "baseline",
                "ladders",
                "external_comparisons",
                "numerical_uncertainty",
                "convention_uncertainty",
                "blockers",
                "closure_blockers",
                "checkpoint_identities",
            }:
                raise MpmathRadialContractError("failed-mode exact schema mismatch")
            if (
                record.get("status") == "FAIL_CLOSED_NUMERICAL_INSTABILITY"
                and isinstance(record.get("blockers"), list)
                and record["blockers"]
            ):
                _validate_mode_closure_metadata(record)
                _validate_checkpoint_identities(
                    record.get("checkpoint_identities"), record["mode"]["mode_id"]
                )
                continue
            raise MpmathRadialContractError("mode baseline missing without blocker")
        if set(record) != {
            "mode",
            "status",
            "baseline",
            "S_status",
            "finite_radius_state_status",
            "finite_radius_state_ladder",
            "flux_status",
            "ladders",
            "external_comparisons",
            "numerical_uncertainty",
            "convention_uncertainty",
            "blockers",
            "closure_blockers",
            "checkpoint_identities",
        }:
            raise MpmathRadialContractError("mode evidence exact schema mismatch")
        _validate_baseline_exact_schema(baseline)
        with mp.workdps(120):
            unit_a_in = _mpc_from_evidence_record(baseline["unit_incoming_A_in"])
            unit_a_out = _mpc_from_evidence_record(baseline["unit_incoming_A_out"])
            horizon_a_in = _mpc_from_evidence_record(
                baseline["horizon_normalized_A_in"]
            )
            horizon_a_out = _mpc_from_evidence_record(
                baseline["horizon_normalized_A_out"]
            )
            transmission = _mpc_from_evidence_record(
                baseline["unit_incoming_horizon_amplitude_T_H"]
            )
            reflection = _mpc_from_evidence_record(
                baseline["reflection_amplitude_Aout_over_Ain"]
            )
            scattering = _mpc_from_evidence_record(baseline["S"])
            if (
                not _mp_close(unit_a_in, mp.mpc(1), baseline["unit_incoming_A_in"])
                or not _mp_close(
                    unit_a_out, reflection, baseline["unit_incoming_A_out"]
                )
                or not _mp_close(
                    horizon_a_in * transmission,
                    mp.mpc(1),
                    baseline["horizon_normalized_A_in"],
                )
                or not _mp_close(
                    horizon_a_out * transmission,
                    reflection,
                    baseline["horizon_normalized_A_out"],
                )
                or not _mp_close(
                    scattering,
                    -reflection / ((-1) ** record["mode"]["ell"]),
                    baseline["S"],
                )
            ):
                raise MpmathRadialContractError(
                    "amplitude normalization identity mismatch"
                )
        _validate_external_comparisons(
            record.get("external_comparisons"), record["mode"]
        )
        _validate_mode_closure_metadata(record)
        _validate_checkpoint_identities(
            record.get("checkpoint_identities"), record["mode"]["mode_id"]
        )
        if baseline.get("mode") != record.get("mode"):
            raise MpmathRadialContractError("baseline outer mode binding mismatch")
        backend_record = baseline.get("backend")
        if not isinstance(backend_record, Mapping):
            raise MpmathRadialContractError("baseline precision truth missing")
        if backend_record.get("requested_precision_dps") != 100:
            raise MpmathRadialContractError("baseline requested dps mismatch")
        if backend_record.get("actual_decimal_digits") != 100:
            raise MpmathRadialContractError("baseline actual decimal digits mismatch")
        actual_bits = backend_record.get("actual_precision_bits")
        if not isinstance(actual_bits, int) or actual_bits < 332:
            raise MpmathRadialContractError("baseline actual precision bits mismatch")
        if record["mode"]["sector"] == "even" and backend_record.get(
            "even_independent_solve"
        ) is not True:
            raise MpmathRadialContractError("even mode is not an independent solve")
        flux = baseline.get("signed_flux")
        if not isinstance(flux, Mapping):
            raise MpmathRadialContractError("signed flux is missing")
        for field in ("F_inf_in", "F_inf_out", "F_H", "F_loss"):
            _validate_finite_real(flux.get(field), "signed flux")
        for field in (
            "reflection_fraction",
            "horizon_transmission_fraction",
            "absolute_balance_residual",
            "relative_balance_residual",
            "fraction_balance_residual",
            "transmission_resolution_floor",
        ):
            _validate_finite_real(
                flux.get(field), "flux fraction/residual", nonnegative=True
            )
        if flux.get("horizon_flux_inferred_from_one_minus_R") is not False:
            raise MpmathRadialContractError("horizon flux cannot be inferred from R")
        finite_states = baseline.get("finite_radius_states")
        if not isinstance(finite_states, list) or len(finite_states) != 8:
            raise MpmathRadialContractError("eight finite-radius states are required")
        for index, (state, point) in enumerate(zip(finite_states, evaluation_points)):
            if not isinstance(state, Mapping) or state.get("point_id") != point.point_id:
                raise MpmathRadialContractError("finite-state point order mismatch")
            if set(state) != {
                "point_id",
                "radius_M",
                "actual_radius_M",
                "psi_over_Ain",
                "dpsi_dr_over_Ain",
                "authoritative_branch",
                "outer_combination_crosscheck",
            }:
                raise MpmathRadialContractError("finite-state exact schema mismatch")
            if not _radius_record_matches(state.get("radius_M"), point.radius_M):
                raise MpmathRadialContractError("finite-state radius mismatch")
            if not _radius_record_matches(
                state.get("actual_radius_M"), point.radius_M
            ):
                raise MpmathRadialContractError("finite-state actual radius mismatch")
            if state.get("authoritative_branch") != "T_H times outward horizon solution":
                raise MpmathRadialContractError("finite-state branch is not authoritative")
            for field in ("psi_over_Ain", "dpsi_dr_over_Ain"):
                _validate_complex_evidence_record(state.get(field), f"finite state {index}")
            crosscheck = state.get("outer_combination_crosscheck")
            if not isinstance(crosscheck, Mapping) or set(crosscheck) != {
                "psi_over_Ain",
                "dpsi_dr_over_Ain",
                "cancellation_condition",
                "relative_to_authoritative_state_residual",
            }:
                raise MpmathRadialContractError("outer finite-state crosscheck missing")
            for field in ("psi_over_Ain", "dpsi_dr_over_Ain"):
                _validate_complex_evidence_record(crosscheck.get(field), "outer crosscheck")
            for field in (
                "cancellation_condition",
                "relative_to_authoritative_state_residual",
            ):
                _validate_finite_real(
                    crosscheck.get(field), "outer crosscheck", nonnegative=True
                )
        resolution = baseline.get("finite_radius_state_resolution")
        if (
            not isinstance(resolution, Mapping)
            or resolution.get("outer_combination_is_authoritative") is not False
            or not isinstance(
                resolution.get("outer_combination_crosscheck_resolved"), bool
            )
        ):
            raise MpmathRadialContractError("finite-state resolution metadata missing")
        cancellation = mp.mpf(
            str(resolution["outer_combination_max_cancellation_condition"])
        )
        cancellation_limit = mp.mpf(
            str(resolution["outer_combination_resolution_limit"])
        )
        state_residual = mp.mpf(
            str(
                resolution[
                    "outer_combination_max_relative_to_authoritative_residual"
                ]
            )
        )
        state_residual_limit = mp.mpf(
            str(resolution["outer_combination_relative_residual_limit"])
        )
        for value in (
            cancellation,
            cancellation_limit,
            state_residual,
            state_residual_limit,
        ):
            if not mp.isfinite(value) or value < 0:
                raise MpmathRadialContractError(
                    "finite-state resolution quantity is invalid"
                )
        expected_crosscheck = (
            cancellation < cancellation_limit
            and state_residual < state_residual_limit
        )
        if resolution["outer_combination_crosscheck_resolved"] is not expected_crosscheck:
            raise MpmathRadialContractError("outer crosscheck resolution flag mismatch")
        finite_ladder = record.get("finite_radius_state_ladder")
        if (
            not isinstance(finite_ladder, Mapping)
            or set(finite_ladder)
            != {
                "precision_nodes_dps",
                "precision_max_relative_state_differences_decimal",
                "step_nodes_rstar",
                "step_max_relative_state_differences_decimal",
                "missing_flag",
                "failure_reason",
                "precision_nonmonotonic_flag",
                "step_nonmonotonic_flag",
                "closure_permitted",
            }
            or finite_ladder.get("closure_permitted") is not False
        ):
            raise MpmathRadialContractError("finite-state ladder evidence is missing")
        if finite_ladder["precision_nodes_dps"] != [50, 70, 100] or finite_ladder[
            "step_nodes_rstar"
        ] != [0.1, 0.05, 0.025]:
            raise MpmathRadialContractError("finite-state ladder nodes mismatch")
        precision_state_deltas = finite_ladder[
            "precision_max_relative_state_differences_decimal"
        ]
        step_state_deltas = finite_ladder[
            "step_max_relative_state_differences_decimal"
        ]
        if not (
            isinstance(precision_state_deltas, list)
            and isinstance(step_state_deltas, list)
            and len(precision_state_deltas) == 2
            and len(step_state_deltas) == 2
        ):
            raise MpmathRadialContractError("finite-state delta inventory mismatch")
        for value in precision_state_deltas + step_state_deltas:
            _validate_finite_real(value, "finite-state ladder", nonnegative=True)
        expected_finite_stable = (
            finite_ladder["missing_flag"] is False
            and finite_ladder["failure_reason"] is None
            and finite_ladder["precision_nonmonotonic_flag"] is False
            and finite_ladder["step_nonmonotonic_flag"] is False
            and mp.mpf(precision_state_deltas[-1]) <= mp.mpf("1e-18")
            and mp.mpf(step_state_deltas[-1]) <= mp.mpf("2e-6")
        )
        if record.get("S_status") not in {
            "STABLE_BOUNDED_SELECTED_NODES",
            "FAIL_CLOSED_DISCRETIZATION_OR_MATCHING",
        }:
            raise MpmathRadialContractError("S status is missing")
        if record.get("finite_radius_state_status") not in {
            "STABLE_BOUNDED_SELECTED_NODES",
            "FAIL_CLOSED_UNRESOLVED_FINITE_STATE",
        }:
            raise MpmathRadialContractError("finite-state status is missing")
        if (
            record["finite_radius_state_status"]
            == "STABLE_BOUNDED_SELECTED_NODES"
        ) is not expected_finite_stable:
            raise MpmathRadialContractError("finite-state status/gate mismatch")
        matching = baseline.get("matching")
        if not isinstance(matching, Mapping):
            raise MpmathRadialContractError("matching evidence is missing")
        for field in (
            "reconstruction_residual",
            "condition_estimate",
            "incoming_tail_ratio",
            "outgoing_tail_ratio",
            "incoming_tail_threshold",
            "outgoing_tail_threshold",
            "conjugacy_value_residual",
            "conjugacy_derivative_residual",
            "basis_determinant_relative",
            "jost_health_threshold",
        ):
            _validate_finite_real(
                matching.get(field), "matching", nonnegative=True
            )
        if not isinstance(matching.get("incoming_cap_reached"), bool) or not isinstance(
            matching.get("outgoing_cap_reached"), bool
        ):
            raise MpmathRadialContractError("Jost cap metadata is missing")
        if matching.get("selected_jost_gate_passed") is not True:
            raise MpmathRadialContractError("selected Jost baseline is unhealthy")
        _validate_complex_evidence_record(
            matching.get("basis_determinant"), "basis determinant"
        )
        health = mp.mpf(str(matching["jost_health_threshold"]))
        incoming_tail = mp.mpf(str(matching["incoming_tail_ratio"]))
        outgoing_tail = mp.mpf(str(matching["outgoing_tail_ratio"]))
        incoming_threshold = mp.mpf(str(matching["incoming_tail_threshold"]))
        outgoing_threshold = mp.mpf(str(matching["outgoing_tail_threshold"]))
        raw_jost_gate = (
            (
                not matching["incoming_cap_reached"]
                or incoming_tail <= incoming_threshold
            )
            and (
                not matching["outgoing_cap_reached"]
                or outgoing_tail <= outgoing_threshold
            )
            and mp.mpf(str(matching["conjugacy_value_residual"])) <= health
            and mp.mpf(str(matching["conjugacy_derivative_residual"])) <= health
            and mp.mpf(str(matching["basis_determinant_relative"])) >= health
            and mp.mpf(str(matching["condition_estimate"])) <= 1 / health
        )
        if not raw_jost_gate:
            raise MpmathRadialContractError("selected Jost raw gates are unhealthy")
        wronskian = baseline.get("wronskian")
        if not isinstance(wronskian, Mapping):
            raise MpmathRadialContractError("Wronskian evidence is missing")
        for field in (
            "raw_unit_horizon_signed_current",
            "inner_signed_current",
            "outer_signed_current",
            "maximum_relative_current_drift",
        ):
            _validate_finite_real(
                wronskian.get(field),
                "Wronskian",
                nonnegative=field == "maximum_relative_current_drift",
            )
        for field in ("inner_W", "outer_W"):
            _validate_complex_evidence_record(wronskian.get(field), "Wronskian")
        axis_limits = {
            "precision_dps": mp.mpf("1e-20"),
            "step_rstar": mp.mpf("2e-6"),
            "r_in_eps": mp.mpf("5e-5"),
            "r_out_M": mp.mpf("1e-8"),
            "jost_order": mp.mpf("1e-10"),
        }
        expected_s_stable = matching["selected_jost_gate_passed"] is True
        for axis_name, axis in ladders.items():
            maximum = axis["max_adjacent_S_difference_decimal"]
            expected_s_stable = expected_s_stable and (
                axis["missing_flag"] is False
                and axis["nonmonotonic_flag"] is False
                and maximum is not None
                and mp.mpf(maximum) <= axis_limits[axis_name]
            )
        expected_s_stable = expected_s_stable and mp.mpf(
            ladders["step_rstar"]["remainder_estimate_decimal"]
        ) <= mp.mpf("2e-7")
        if (
            record["S_status"] == "STABLE_BOUNDED_SELECTED_NODES"
        ) is not expected_s_stable:
            raise MpmathRadialContractError("S status/gate mismatch")
        expected_flux_resolved = (
            flux["transmission_resolved_at_actual_precision"] is True
            and mp.mpf(str(flux["relative_balance_residual"])) <= mp.mpf("1e-5")
            and mp.mpf(str(wronskian["maximum_relative_current_drift"]))
            <= mp.mpf("1e-5")
        )
        if (
            record["flux_status"] == "RESOLVED_INTERNAL_FLUX_ACCOUNTING"
        ) is not expected_flux_resolved:
            raise MpmathRadialContractError("flux status/gate mismatch")
        blockers = record.get("blockers")
        if not isinstance(blockers, list):
            raise MpmathRadialContractError("mode blocker list missing")
        expected_mode_stable = (
            expected_s_stable and expected_finite_stable and expected_flux_resolved
        )
        if (
            record.get("status") == "STABLE_SELECTED_ANCHOR_INCOMPLETE_LADDERS"
        ) is not expected_mode_stable:
            raise MpmathRadialContractError("mode status/gate mismatch")
        if expected_mode_stable is not (not blockers):
            raise MpmathRadialContractError("mode blockers/status mismatch")
    source_identities = payload.get("source_identities")
    if not isinstance(source_identities, list) or not source_identities:
        raise MpmathRadialContractError("source identities are missing")
    for identity in source_identities:
        if (
            not isinstance(identity, Mapping)
            or set(identity) != {"path", "sha256", "size", "mode", "nlink"}
            or not isinstance(identity.get("path"), str)
            or not isinstance(identity.get("size"), int)
            or not isinstance(identity.get("mode"), int)
            or identity.get("nlink") != 1
            or not isinstance(identity.get("sha256"), str)
            or len(identity["sha256"]) != 64
        ):
            raise MpmathRadialContractError("source identity schema mismatch")
        source_path = Path(identity["path"])
        if (
            source_path.is_symlink()
            or not source_path.is_file()
            or source_path.resolve(strict=True) != source_path
        ):
            raise MpmathRadialContractError("source identity path is not regular")
        source_stat = source_path.stat()
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if (
            source_stat.st_size != identity["size"]
            or source_stat.st_mode & 0o7777 != identity["mode"]
            or source_stat.st_nlink != identity["nlink"]
            or digest != identity["sha256"]
        ):
            raise MpmathRadialContractError("source identity content/stat drift")


def _validate_file_identity_record(
    identity: object, *, expected_path: Path | None = None
) -> Path:
    if not isinstance(identity, Mapping) or set(identity) != {
        "path",
        "sha256",
        "size",
        "mode",
        "nlink",
    }:
        raise MpmathRadialContractError("bound file identity schema mismatch")
    path = Path(str(identity["path"]))
    if (
        (expected_path is not None and path != expected_path)
        or path.is_symlink()
        or not path.is_file()
        or path.resolve(strict=True) != path
    ):
        raise MpmathRadialContractError("bound file path identity mismatch")
    info = path.stat()
    if (
        info.st_size != identity["size"]
        or info.st_mode & 0o7777 != identity["mode"]
        or info.st_nlink != identity["nlink"]
        or identity["nlink"] != 1
        or hashlib.sha256(path.read_bytes()).hexdigest() != identity["sha256"]
    ):
        raise MpmathRadialContractError("bound file content/stat drift")
    return path


def _validate_runtime_identity(value: object) -> None:
    if not isinstance(value, Mapping) or set(value) != {
        "schema",
        "python",
        "mpmath",
        "loading",
        "invocation",
    }:
        raise MpmathRadialContractError("AP runtime identity schema mismatch")
    if value.get("schema") != "schwgw_phase6_ap_runtime_identity_v2":
        raise MpmathRadialContractError("AP runtime identity version mismatch")
    project_root = Path(__file__).resolve(strict=True).parents[3]
    expected_overlay = (
        project_root
        / "runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314"
    ).resolve(strict=True)
    python = value.get("python")
    if not isinstance(python, Mapping) or set(python) != {
        "executable",
        "implementation_name",
        "implementation_version",
        "cache_tag",
        "platform",
    }:
        raise MpmathRadialContractError("CPython identity schema mismatch")
    executable = Path(sys.executable).resolve(strict=True)
    _validate_file_identity_record(python["executable"], expected_path=executable)
    if (
        python.get("implementation_name") != "cpython"
        or python.get("implementation_version") != platform.python_version()
        or not str(python["implementation_version"]).startswith("3.14.")
        or python.get("cache_tag") != sys.implementation.cache_tag
        or python.get("platform") != platform.platform()
    ):
        raise MpmathRadialContractError("CPython implementation identity mismatch")
    mpmath_identity = value.get("mpmath")
    if not isinstance(mpmath_identity, Mapping) or set(mpmath_identity) != {
        "version",
        "import_origin",
        "package_tree",
    }:
        raise MpmathRadialContractError("mpmath runtime identity schema mismatch")
    if mpmath_identity.get("version") != mp.__version__:
        raise MpmathRadialContractError("mpmath version mismatch")
    origin = _validate_file_identity_record(
        mpmath_identity["import_origin"], expected_path=Path(mp.__file__).resolve()
    )
    package = mpmath_identity.get("package_tree")
    if not isinstance(package, Mapping) or set(package) != {
        "root",
        "file_count",
        "files",
        "derived_bytecode_policy",
        "canonical_inventory_sha256",
    }:
        raise MpmathRadialContractError("mpmath package inventory schema mismatch")
    package_root = expected_overlay
    if (
        Path(str(package["root"])) != package_root
        or origin.parent.parent != expected_overlay
    ):
        raise MpmathRadialContractError("mpmath package root mismatch")
    records = package.get("files")
    if (
        not isinstance(records, list)
        or package.get("file_count") != len(records)
        or package.get("derived_bytecode_policy")
        != "exclude __pycache__ directories and *.pyc files"
        or any(
            "__pycache__" in Path(str(record.get("relative_path"))).parts
            or Path(str(record.get("relative_path"))).suffix == ".pyc"
            for record in records
            if isinstance(record, Mapping)
        )
    ):
        raise MpmathRadialContractError("mpmath package inventory count mismatch")
    required_distribution_files = {
        "mpmath/__init__.py",
        "mpmath-1.4.1.dist-info/METADATA",
        "mpmath-1.4.1.dist-info/RECORD",
        "mpmath-1.4.1.dist-info/licenses/LICENSE",
    }
    if not required_distribution_files <= {
        str(record.get("relative_path"))
        for record in records
        if isinstance(record, Mapping)
    }:
        raise MpmathRadialContractError("mpmath distribution inventory is incomplete")
    actual_records: list[dict[str, object]] = []
    for path in sorted(package_root.rglob("*")):
        if path.is_symlink():
            raise MpmathRadialContractError("mpmath package contains a symlink")
        if not path.is_file():
            continue
        relative = path.relative_to(package_root)
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        info = path.stat()
        actual_records.append(
            {
                "relative_path": relative.as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "size": info.st_size,
                "mode": info.st_mode & 0o7777,
                "nlink": info.st_nlink,
            }
        )
    inventory_bytes = (
        json.dumps(
            actual_records, sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        + "\n"
    ).encode("utf-8")
    if (
        records != actual_records
        or any(record.get("nlink") != 1 for record in actual_records)
        or package.get("canonical_inventory_sha256")
        != hashlib.sha256(inventory_bytes).hexdigest()
    ):
        raise MpmathRadialContractError("mpmath package inventory drift")
    loading = value.get("loading")
    expected_pythonpath = os.pathsep.join(
        (str(expected_overlay), str(project_root / "src"))
    )
    if not isinstance(loading, Mapping) or set(loading) != {
        "mechanism",
        "overlay_root",
        "pythonpath",
        "sys_path",
        "python3p10_site_packages_entries",
        "numpy",
        "scipy",
    }:
        raise MpmathRadialContractError("AP loading identity schema mismatch")
    recorded_sys_path = loading.get("sys_path")
    expected_runner = (
        project_root / "scripts/phase6_mpmath_radial_selected_anchors.py"
    ).resolve(strict=True)
    expected_import_prefix = [
        str(expected_runner.parent),
        str(expected_overlay),
        str((project_root / "src").resolve(strict=True)),
    ]
    if not isinstance(recorded_sys_path, list) or any(
        not isinstance(entry, str) for entry in recorded_sys_path
    ):
        raise MpmathRadialContractError("recorded sys.path is malformed")
    foreign_mpmath_entries: list[str] = []
    for entry in recorded_sys_path:
        if not entry:
            continue
        candidate = Path(entry)
        if candidate == expected_overlay:
            continue
        if (candidate / "mpmath" / "__init__.py").is_file() or (
            candidate / "mpmath.py"
        ).is_file():
            foreign_mpmath_entries.append(entry)
    if (
        loading.get("mechanism") != "exact overlay-first PYTHONPATH"
        or loading.get("overlay_root") != str(expected_overlay)
        or loading.get("pythonpath") != expected_pythonpath
        or recorded_sys_path[:3] != expected_import_prefix
        or loading.get("python3p10_site_packages_entries") != []
        or any(
            "python3.10" in entry and "site-packages" in entry
            for entry in recorded_sys_path
        )
        or foreign_mpmath_entries
    ):
        raise MpmathRadialContractError("AP overlay loading mechanism mismatch")
    for module_name in ("numpy", "scipy"):
        module = sys.modules.get(module_name)
        record = loading.get(module_name)
        if (
            module is None
            or not isinstance(record, Mapping)
            or set(record) != {"version", "origin"}
            or record.get("version") != module.__version__
        ):
            raise MpmathRadialContractError("scientific runtime module identity mismatch")
        _validate_file_identity_record(
            record["origin"], expected_path=Path(module.__file__).resolve(strict=True)
        )
    invocation = value.get("invocation")
    if not isinstance(invocation, Mapping) or set(invocation) != {
        "cwd",
        "argv",
        "environment",
        "reproducible_command",
    }:
        raise MpmathRadialContractError("runtime invocation schema mismatch")
    expected_environment = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": expected_pythonpath,
    }
    recorded_argv = invocation.get("argv")
    if not isinstance(recorded_argv, list) or len(recorded_argv) != 3:
        raise MpmathRadialContractError("runtime invocation argv is malformed")
    output_root = Path(str(recorded_argv[2]))
    expected_output_parent = (
        project_root / "runs/phase6/radial_validation"
    ).resolve(strict=True)
    try:
        output_relative = output_root.relative_to(expected_output_parent)
    except ValueError as exc:
        raise MpmathRadialContractError(
            "runtime invocation output root is out of scope"
        ) from exc
    stored_executable = Path(str(python["executable"]["path"]))
    if (
        invocation.get("cwd") != str(project_root)
        or recorded_argv[0] != str(expected_runner)
        or recorded_argv[1] != "--output-root"
        or not output_root.is_absolute()
        or output_relative == Path(".")
        or output_root.is_symlink()
        or not output_root.is_dir()
        or output_root.resolve(strict=True) != output_root
        or invocation.get("environment") != expected_environment
        or invocation.get("reproducible_command")
        != shlex.join([str(stored_executable), *recorded_argv])
    ):
        raise MpmathRadialContractError("runtime invocation identity mismatch")


def _validate_execution_contract(value: object) -> None:
    if not isinstance(value, Mapping) or set(value) != {
        "root",
        "contract_sha256",
        "manifest_sha256",
        "payload_role",
        "resumable_full_shard_pass",
    }:
        raise MpmathRadialContractError("execution-contract binding schema mismatch")
    root = (
        Path(__file__).resolve(strict=True).parents[3]
        / "runs/phase6/v1_execution_contract_v4_20260806"
    )
    if (
        Path(str(value["root"])) != root
        or root.is_symlink()
        or not root.is_dir()
        or root.stat().st_mode & 0o7777 != 0o555
        or value.get("contract_sha256")
        != "25ad4b4e723edbd44651edaa63df415141de504b85288b12c2a6a973fcb420ab"
        or value.get("manifest_sha256")
        != "1de9d445d888cbb5ddbf426cc062d2fb5128cad111437ce7d147df6e004aed48"
        or value.get("payload_role") != "bounded Stage-A calibration payload"
        or value.get("resumable_full_shard_pass") is not False
    ):
        raise MpmathRadialContractError("execution-contract binding mismatch")
    for filename, digest, size in (
        ("execution_contract.json", value["contract_sha256"], 29024),
        ("manifest.json", value["manifest_sha256"], 1298),
    ):
        path = root / filename
        info = path.stat()
        if (
            path.is_symlink()
            or not path.is_file()
            or info.st_mode & 0o7777 != 0o444
            or info.st_nlink != 1
            or info.st_size != size
            or hashlib.sha256(path.read_bytes()).hexdigest() != digest
        ):
            raise MpmathRadialContractError("execution-contract file identity drift")
    manifest = json.loads(
        (root / "manifest.json").read_text(encoding="utf-8"),
        object_pairs_hook=_strict_json_object,
    )
    if (
        not isinstance(manifest, Mapping)
        or manifest.get("schema") != "schwgw_phase6_v1_execution_contract_v1"
        or manifest.get("status") != "EXECUTION_CONTRACT_FROZEN_NO_NUMERICAL_SOLVES"
        or manifest.get("numerical_solves_executed") != 0
        or manifest.get("global_green_permitted") is not False
    ):
        raise MpmathRadialContractError("execution-contract manifest semantics drift")
    expected_identities = {
        "contract": "execution_contract.json",
        **{
            filename: filename
            for filename in (
                "D_external_direct_calibration.jsonl",
                "D_transition_calibration.jsonl",
                "shard_inventory.jsonl",
            )
        },
    }
    for key, filename in expected_identities.items():
        identity = (
            manifest.get("contract")
            if key == "contract"
            else manifest.get("evidence_files", {}).get(key)
        )
        _validate_file_identity_record(identity, expected_path=root / filename)


def _validate_mode_closure_metadata(record: Mapping[str, object]) -> None:
    numerical = record.get("numerical_uncertainty")
    if not isinstance(numerical, Mapping):
        raise MpmathRadialContractError("numerical uncertainty schema mismatch")
    if set(numerical) == {"closed"}:
        if numerical.get("closed") is not False:
            raise MpmathRadialContractError("numerical uncertainty overclaim")
    elif set(numerical) == {
        "metric",
        "conservative_max_over_ladders_and_independent_backends_decimal",
        "closed",
        "reason",
    }:
        if (
            numerical.get("metric") != "absolute complex S difference"
            or numerical.get("closed") is not False
            or numerical.get("reason")
            != "bounded Stage-A anchors do not close full V1 uncertainty"
        ):
            raise MpmathRadialContractError("numerical uncertainty overclaim")
        conservative = numerical[
            "conservative_max_over_ladders_and_independent_backends_decimal"
        ]
        if conservative is not None:
            _validate_finite_real(
                conservative, "numerical uncertainty", nonnegative=True
            )
    else:
        raise MpmathRadialContractError("numerical uncertainty schema mismatch")
    convention = record.get("convention_uncertainty")
    if not isinstance(convention, Mapping):
        raise MpmathRadialContractError("convention uncertainty schema mismatch")
    if set(convention) == {"closed"}:
        if convention.get("closed") is not False:
            raise MpmathRadialContractError("convention uncertainty overclaim")
    elif set(convention) == {
        "Fourier_convention",
        "S_definition",
        "tortoise_definition",
        "phase_or_normalization_fit",
        "closed",
    }:
        if (
            convention.get("Fourier_convention") != "exp(-i k t)"
            or convention.get("S_definition")
            != "-unit_incoming_A_out/[(-1)^ell unit_incoming_A_in]"
            or convention.get("tortoise_definition") != "r+2 log(r/2-1)"
            or convention.get("phase_or_normalization_fit") is not False
            or convention.get("closed") is not False
        ):
            raise MpmathRadialContractError("convention uncertainty mismatch")
    else:
        raise MpmathRadialContractError("convention uncertainty schema mismatch")
    if record.get("closure_blockers") != [
        "bounded Stage-A nodes omit the full declared Phase-6 ladder",
        "AP fixed-step ladder is not the production adaptive-tolerance ladder",
        "full 17,818-key policy-extended union domain is not evaluated",
    ]:
        raise MpmathRadialContractError("Stage-A closure blocker mismatch")


def _validate_checkpoint_identities(value: object, mode_id: object) -> None:
    if not isinstance(mode_id, str) or not isinstance(value, list) or len(value) != 7:
        raise MpmathRadialContractError("mode checkpoint inventory mismatch")
    paths: set[Path] = set()
    for identity in value:
        if not isinstance(identity, Mapping) or set(identity) != {
            "path",
            "sha256",
            "size",
            "inode",
            "mode",
            "nlink",
        }:
            raise MpmathRadialContractError("mode checkpoint identity schema mismatch")
        path = Path(str(identity["path"]))
        if (
            path in paths
            or mode_id not in path.parts
            or path.is_symlink()
            or not path.is_file()
            or path.resolve(strict=True) != path
        ):
            raise MpmathRadialContractError("mode checkpoint path/alias mismatch")
        paths.add(path)
        info = path.stat()
        if (
            info.st_size != identity["size"]
            or info.st_ino != identity["inode"]
            or info.st_mode & 0o7777 != identity["mode"]
            or info.st_mode & 0o7777 != 0o444
            or info.st_nlink != identity["nlink"]
            or identity["nlink"] != 1
            or hashlib.sha256(path.read_bytes()).hexdigest() != identity["sha256"]
        ):
            raise MpmathRadialContractError("mode checkpoint content/stat drift")


def _validate_finite_real(
    value: object, label: str, *, nonnegative: bool = False
) -> None:
    try:
        parsed = mp.mpf(str(value))
    except (TypeError, ValueError) as exc:
        raise MpmathRadialContractError(f"{label} real field is malformed") from exc
    if not mp.isfinite(parsed):
        raise MpmathRadialContractError(f"{label} real field is non-finite")
    if nonnegative and parsed < 0:
        raise MpmathRadialContractError(f"{label} real field is negative")


def _validate_domain_freeze(domain: Mapping[str, object]) -> None:
    expected_keys = {
        "covered_keys",
        "covered_key_count",
        "production_deduplicated_key_count",
        "production_missing_key_count",
        "policy_extended_union_key_count",
        "policy_extended_union_missing_key_count",
        "audit_extension_key_count",
        "audit_required_key_count",
        "production_required_overlap_count",
        "inventory_provenance",
        "counts_claim_scope",
        "exact_domain_manifests_available",
        "domain_freeze",
        "full_v1_domain_complete",
    }
    if set(domain) != expected_keys:
        raise MpmathRadialContractError("declared-domain exact schema mismatch")
    if (
        domain.get("counts_claim_scope") != "exact immutable domain manifests"
        or domain.get("exact_domain_manifests_available") is not True
        or domain.get("audit_extension_key_count") != 1770
        or domain.get("audit_required_key_count") != 3392
        or domain.get("production_required_overlap_count") != 1622
        or domain.get("covered_keys")
        != [mode.to_metadata() for mode in selected_stage_a_modes()]
        or domain.get("production_missing_key_count") != 16040
        or domain.get("policy_extended_union_missing_key_count") != 17810
    ):
        raise MpmathRadialContractError("exact domain counts/binding mismatch")
    binding = domain.get("domain_freeze")
    if not isinstance(binding, Mapping) or set(binding) != {
        "root",
        "D_prod_sha256",
        "D_ext_sha256",
        "D_required_sha256",
        "D_union_sha256",
        "domain_contract_sha256",
        "manifest_sha256",
    }:
        raise MpmathRadialContractError("domain freeze binding schema mismatch")
    root = Path(str(binding["root"]))
    expected_root = (
        Path(__file__).resolve(strict=True).parents[3]
        / "runs/phase6/v1_domain_freeze_v3_20260806"
    )
    if (
        root != expected_root
        or root.is_symlink()
        or not root.is_dir()
        or root.resolve(strict=True) != root
        or root.stat().st_mode & 0o7777 != 0o555
    ):
        raise MpmathRadialContractError("domain freeze root identity mismatch")
    file_bindings = {
        "D_prod.jsonl": ("D_prod_sha256", 16048, 605958),
        "D_ext.jsonl": ("D_ext_sha256", 1770, 65025),
        "D_required.jsonl": ("D_required_sha256", 3392, 123892),
        "D_union.jsonl": ("D_union_sha256", 17818, 670983),
        "domain_contract.json": ("domain_contract_sha256", None, 29635),
        "manifest.json": ("manifest_sha256", None, 1480),
    }
    line_sets: dict[str, set[bytes]] = {}
    for filename, (hash_key, expected_count, expected_size) in file_bindings.items():
        path = root / filename
        if path.is_symlink() or not path.is_file() or path.resolve(strict=True) != path:
            raise MpmathRadialContractError("domain artifact path identity mismatch")
        info = path.stat()
        data = path.read_bytes()
        if (
            info.st_nlink != 1
            or info.st_mode & 0o7777 != 0o444
            or info.st_size != expected_size
            or hashlib.sha256(data).hexdigest() != binding[hash_key]
        ):
            raise MpmathRadialContractError("domain artifact hash/stat drift")
        if expected_count is not None:
            lines = data.splitlines()
            if (
                not data.endswith(b"\n")
                or data != b"\n".join(lines) + b"\n"
                or len(lines) != expected_count
                or len(set(lines)) != expected_count
            ):
                raise MpmathRadialContractError("domain JSONL count/uniqueness mismatch")
            for line in lines:
                parsed = json.loads(line, object_pairs_hook=_strict_json_object)
                canonical = json.dumps(
                    parsed,
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                ).encode("utf-8")
                if canonical != line:
                    raise MpmathRadialContractError("domain JSONL is noncanonical")
            line_sets[filename] = set(lines)
    prod = line_sets["D_prod.jsonl"]
    extension = line_sets["D_ext.jsonl"]
    required = line_sets["D_required.jsonl"]
    union = line_sets["D_union.jsonl"]
    overlap = prod & required
    if (
        prod & extension
        or union != prod | extension
        or not extension <= required
        or len(overlap) != 1622
        or required != overlap | extension
    ):
        raise MpmathRadialContractError("domain exact set arithmetic mismatch")


def _strict_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise MpmathRadialContractError("duplicate JSON member in domain artifact")
        result[key] = value
    return result


def _radius_record_matches(value: object, expected: str) -> bool:
    with mp.workdps(120):
        return abs(mp.mpf(str(value)) - mp.mpf(expected)) <= mp.mpf("1e-30")


def _validate_complex_evidence_record(value: object, label: str) -> None:
    if not isinstance(value, Mapping) or set(value) != {"real", "imag", "abs"}:
        raise MpmathRadialContractError(f"{label} complex schema mismatch")
    with mp.workdps(120):
        real = mp.mpf(str(value["real"]))
        imag = mp.mpf(str(value["imag"]))
        magnitude = mp.mpf(str(value["abs"]))
        if not all(mp.isfinite(item) for item in (real, imag, magnitude)):
            raise MpmathRadialContractError(f"{label} complex field is non-finite")
        if magnitude < 0:
            raise MpmathRadialContractError(f"{label} magnitude is negative")
        computed = abs(mp.mpc(real, imag))
        digits = min(
            _decimal_significant_digits(str(value[field]))
            for field in ("real", "imag", "abs")
        )
        tolerance = max(
            max(computed, magnitude) * mp.power(10, -max(10, digits - 4)),
            mp.mpf("1e-10000"),
        )
        if abs(computed - magnitude) > tolerance:
            raise MpmathRadialContractError(f"{label} complex magnitude mismatch")


def _mpc_from_evidence_record(value: object) -> mp.mpc:
    _validate_complex_evidence_record(value, "complex value")
    assert isinstance(value, Mapping)
    return mp.mpc(mp.mpf(str(value["real"])), mp.mpf(str(value["imag"])))


def _mp_close(left: mp.mpc, right: mp.mpc, precision_record: object) -> bool:
    assert isinstance(precision_record, Mapping)
    digits = min(
        _decimal_significant_digits(str(precision_record[field]))
        for field in ("real", "imag", "abs")
    )
    scale = max(abs(left), abs(right), mp.mpf("1e-10000"))
    return abs(left - right) <= scale * mp.power(10, -max(10, digits - 5))


def _decimal_significant_digits(value: str) -> int:
    mantissa = value.lower().split("e", maxsplit=1)[0].lstrip("+-")
    digits = "".join(character for character in mantissa if character.isdigit())
    # Leading zeros only locate the decimal point.  Counting them made, for
    # example, a 100-digit fixed-point value near 1e-26 advertise 126 digits.
    significant = digits.lstrip("0")
    return max(1, len(significant))


def _validate_axis_evidence(axis_name: str, axis: object) -> None:
    expected_nodes = {
        "precision_dps": [50, 70, 100],
        "step_rstar": [0.1, 0.05, 0.025],
        "r_in_eps": [3e-6, 1e-6, 3e-7],
        "r_out_M": [300.0, 600.0],
        "jost_order": [80, 120, 160],
    }
    base_keys = {
        "axis",
        "nodes",
        "S_values",
        "statuses",
        "failure_reasons",
        "missing_flag",
        "nonmonotonic_flag",
        "final_pair",
        "adjacent_S_differences_decimal",
        "max_adjacent_S_difference_decimal",
        "extrapolation_model",
        "remainder_estimate_decimal",
        "selected_nodes_complete",
        "closure_permitted",
        "phase6_declared_axis_nodes_complete",
    }
    step_keys = base_keys | {
        "richardson_order",
        "richardson_extrapolated_S",
        "observed_refinement_ratio_decimal",
    }
    if not isinstance(axis, Mapping) or frozenset(axis) not in {
        frozenset(base_keys),
        frozenset(step_keys),
    }:
        raise MpmathRadialContractError("ladder exact schema mismatch")
    nodes = axis.get("nodes")
    if axis.get("axis") != axis_name or nodes != expected_nodes[axis_name]:
        raise MpmathRadialContractError("ladder node order mismatch")
    values = axis.get("S_values")
    statuses = axis.get("statuses")
    failures = axis.get("failure_reasons")
    if not all(isinstance(item, list) for item in (values, statuses, failures)):
        raise MpmathRadialContractError("ladder list schema mismatch")
    if not (len(values) == len(statuses) == len(failures) == len(nodes)):
        raise MpmathRadialContractError("ladder list length mismatch")
    parsed: list[mp.mpc | None] = []
    with mp.workdps(120):
        for value, status, failure in zip(values, statuses, failures):
            if value is None:
                if status != "FAIL" or not isinstance(failure, str) or not failure:
                    raise MpmathRadialContractError("ladder failed-node bookkeeping mismatch")
                parsed.append(None)
            else:
                if status != "PASS" or failure is not None:
                    raise MpmathRadialContractError("ladder passed-node bookkeeping mismatch")
                _validate_complex_evidence_record(value, "ladder S")
                parsed.append(
                    mp.mpc(mp.mpf(str(value["real"])), mp.mpf(str(value["imag"])))
                )
        deltas = [
            None if left is None or right is None else abs(right - left)
            for left, right in zip(parsed, parsed[1:])
        ]
        expected_deltas = [
            None if value is None else mp.nstr(value, 110) for value in deltas
        ]
        if axis.get("adjacent_S_differences_decimal") != expected_deltas:
            raise MpmathRadialContractError("ladder adjacent delta mismatch")
        complete = all(value is not None for value in parsed)
        expected_max = (
            mp.nstr(max(value for value in deltas if value is not None), 110)
            if complete
            else None
        )
        if axis.get("max_adjacent_S_difference_decimal") != expected_max:
            raise MpmathRadialContractError("ladder maximum delta mismatch")
        if axis.get("missing_flag") is not (not complete):
            raise MpmathRadialContractError("ladder missing flag mismatch")
        available_deltas = [value for value in deltas if value is not None]
        nonmonotonic = any(
            later > earlier
            for earlier, later in zip(available_deltas, available_deltas[1:])
        )
        if axis.get("nonmonotonic_flag") is not nonmonotonic:
            raise MpmathRadialContractError("ladder monotonic flag mismatch")
        expected_final = None
        if parsed[-2] is not None and parsed[-1] is not None:
            expected_final = {
                "nodes": nodes[-2:],
                "absolute_S_difference_decimal": mp.nstr(
                    abs(parsed[-1] - parsed[-2]), 110
                ),
            }
        if axis.get("final_pair") != expected_final:
            raise MpmathRadialContractError("ladder final-pair mismatch")
        if axis.get("selected_nodes_complete") is not complete:
            raise MpmathRadialContractError("ladder completeness mismatch")
        if axis.get("closure_permitted") is not False or axis.get(
            "phase6_declared_axis_nodes_complete"
        ) is not False:
            raise MpmathRadialContractError("bounded ladder overclaims closure")
        if axis_name == "step_rstar" and complete:
            if set(axis) != step_keys or axis.get("richardson_order") != 4:
                raise MpmathRadialContractError("Richardson exact schema mismatch")
            coarse, middle, fine = parsed
            denominator = abs(middle - fine)
            expected_remainder = mp.nstr(denominator / 15, 110)
            expected_ratio = (
                mp.nstr(abs(coarse - middle) / denominator, 110)
                if denominator
                else None
            )
            if axis.get("remainder_estimate_decimal") != expected_remainder or axis.get(
                "observed_refinement_ratio_decimal"
            ) != expected_ratio:
                raise MpmathRadialContractError("Richardson diagnostics mismatch")
            extrapolated = fine + (fine - middle) / 15
            if axis.get("richardson_extrapolated_S") != {
                "real": mp.nstr(mp.re(extrapolated), 100),
                "imag": mp.nstr(mp.im(extrapolated), 100),
            }:
                raise MpmathRadialContractError("Richardson extrapolate mismatch")
        elif set(axis) != base_keys:
            raise MpmathRadialContractError("non-step ladder has Richardson fields")


def _validate_baseline_exact_schema(baseline: Mapping[str, object]) -> None:
    expected = {
        "schema_version",
        "mode",
        "backend",
        "configuration",
        "unit_incoming_A_in",
        "unit_incoming_A_out",
        "horizon_normalized_A_in",
        "horizon_normalized_A_out",
        "reflection_amplitude_Aout_over_Ain",
        "S",
        "unit_incoming_horizon_amplitude_T_H",
        "finite_radius_states",
        "finite_radius_state_resolution",
        "signed_flux",
        "wronskian",
        "matching",
        "integration",
    }
    if set(baseline) != expected or baseline.get("schema_version") != BACKEND_SCHEMA:
        raise MpmathRadialContractError("baseline exact schema mismatch")
    nested_sets = {
        "backend": {
            "actual_backend",
            "requested_precision_dps",
            "actual_decimal_digits",
            "actual_precision_bits",
            "rounding",
            "guard_digits",
            "genuinely_independent",
            "even_independent_solve",
            "shared_components",
        },
        "configuration": {
            "M",
            "Fourier_convention",
            "r_in_eps",
            "r_out_M",
            "actual_r_out_M",
            "r_out_radius_error",
            "maximum_step_rstar",
            "Jost_order_cap",
            "horizon_normalization",
            "outer_basis",
            "integration_architecture",
            "common_match_radius_M",
            "match_radius_policy",
        },
        "finite_radius_state_resolution": {
            "authoritative_construction",
            "outer_combination_is_authoritative",
            "outer_combination_max_cancellation_condition",
            "outer_combination_resolution_limit",
            "outer_combination_max_relative_to_authoritative_residual",
            "outer_combination_relative_residual_limit",
            "outer_combination_crosscheck_resolved",
            "complex_log_amplitude_required_for_generic_float64_backend",
        },
        "signed_flux": {
            "F_inf_in",
            "F_inf_out",
            "F_H",
            "F_loss",
            "horizon_flux_source",
            "horizon_flux_inferred_from_one_minus_R",
            "reflection_fraction",
            "horizon_transmission_fraction",
            "absolute_balance_residual",
            "relative_balance_residual",
            "fraction_balance_residual",
            "transmission_resolution_floor",
            "transmission_resolved_at_actual_precision",
            "candidate_outputs_separately_assessable",
            "acceptance_scope",
        },
        "wronskian": {
            "raw_unit_horizon_signed_current",
            "inner_signed_current",
            "outer_signed_current",
            "inner_W",
            "outer_W",
            "maximum_relative_current_drift",
        },
        "matching": {
            "reconstruction_residual",
            "condition_estimate",
            "incoming_effective_order",
            "outgoing_effective_order",
            "maximum_tail_ratio",
            "incoming_tail_ratio",
            "outgoing_tail_ratio",
            "incoming_tail_threshold",
            "outgoing_tail_threshold",
            "incoming_cap_reached",
            "outgoing_cap_reached",
            "incoming_termination_reason",
            "outgoing_termination_reason",
            "conjugacy_value_residual",
            "conjugacy_derivative_residual",
            "basis_determinant",
            "basis_determinant_relative",
            "jost_health_threshold",
            "selected_jost_gate_passed",
            "coarse_cap_reached_permitted_as_raw_ladder_only",
        },
        "integration": {
            "steps",
            "horizon_steps",
            "outer_basis_steps",
            "maximum_radius_state_drift",
            "elapsed_seconds",
            "checkpoint_reuse",
        },
    }
    for field, keys in nested_sets.items():
        nested = baseline.get(field)
        if not isinstance(nested, Mapping) or set(nested) != keys:
            raise MpmathRadialContractError(f"baseline {field} exact schema mismatch")
    configuration = baseline["configuration"]
    assert isinstance(configuration, Mapping)
    if (
        configuration.get("M") != 1
        or configuration.get("Fourier_convention") != "exp(-i k t)"
        or configuration.get("r_in_eps") != 1.0e-6
        or configuration.get("r_out_M") != 300.0
        or mp.mpf(str(configuration.get("actual_r_out_M"))) != mp.mpf("300")
        or mp.mpf(str(configuration.get("r_out_radius_error"))) != 0
        or configuration.get("maximum_step_rstar") != 0.025
        or configuration.get("Jost_order_cap") != 160
        or configuration.get("horizon_normalization")
        != "unit exp(-i k r_star) propagated only to common match radius"
        or configuration.get("outer_basis")
        != "independent local J_in/J_out propagated inward"
        or configuration.get("integration_architecture")
        != "bidirectional_log_derivative_match"
        or configuration.get("common_match_radius_M") != 60.0
        or configuration.get("match_radius_policy")
        != "explicit frozen Stage-A pilot node; not a generic backend policy"
    ):
        raise MpmathRadialContractError("baseline selected configuration drift")
    for field in (
        "unit_incoming_A_in",
        "unit_incoming_A_out",
        "horizon_normalized_A_in",
        "horizon_normalized_A_out",
        "reflection_amplitude_Aout_over_Ain",
        "S",
        "unit_incoming_horizon_amplitude_T_H",
    ):
        _validate_complex_evidence_record(baseline.get(field), field)


def _validate_external_comparisons(value: object, mode: Mapping[str, object]) -> None:
    if (
        not isinstance(value, list)
        or len(value) != 3
        or any(not isinstance(item, Mapping) for item in value)
        or mode.get("sector") not in SECTORS
    ):
        raise MpmathRadialContractError("external comparison inventory mismatch")
    if [item.get("backend") for item in value] != [
        "project_scipy_jost_radial_solver",
        "local_mpmath_mst",
        "frozen_external_bhpt_reggewheeler_mst",
    ]:
        raise MpmathRadialContractError("external comparison order mismatch")
    scipy, local_mst, bhpt = value
    expected_even_flag = False if mode["sector"] == "even" else None
    scipy_available_keys = {
        "backend",
        "status",
        "genuinely_independent",
        "shared_components",
        "role",
        "solver",
        "actual_precision_bits",
        "actual_decimal_digits",
        "S",
        "absolute_S_difference_decimal",
        "no_phase_or_normalization_fit",
    }
    scipy_open_keys = {
        "backend",
        "status",
        "genuinely_independent",
        "shared_components",
        "role",
        "actual_precision_bits",
        "actual_decimal_digits",
        "blocker",
    }
    if set(scipy) not in (scipy_available_keys, scipy_open_keys):
        raise MpmathRadialContractError("SciPy comparison schema/role mismatch")
    if (
        scipy.get("genuinely_independent") is not False
        or scipy.get("shared_components") != []
        or scipy.get("role")
        != "cross-backend comparison only; not part of mpmath call graph"
        or scipy.get("actual_precision_bits") != 53
        or scipy.get("actual_decimal_digits") != 15.95
    ):
        raise MpmathRadialContractError("SciPy comparison precision mismatch")
    if set(scipy) == scipy_available_keys:
        if (
            scipy.get("status") != "AVAILABLE"
            or not isinstance(scipy.get("solver"), str)
            or not scipy["solver"]
            or scipy.get("no_phase_or_normalization_fit") is not True
        ):
            raise MpmathRadialContractError("SciPy available comparison mismatch")
        _validate_complex_evidence_record(scipy.get("S"), "SciPy comparison S")
        _validate_finite_real(
            scipy.get("absolute_S_difference_decimal"),
            "SciPy comparison difference",
            nonnegative=True,
        )
    elif (
        scipy.get("status") != "OPEN_OR_FAIL_CLOSED"
        or not isinstance(scipy.get("blocker"), str)
        or not scipy["blocker"]
    ):
        raise MpmathRadialContractError("SciPy open comparison mismatch")
    local_available_keys = {
        "backend",
        "status",
        "method",
        "genuinely_independent",
        "independence_role",
        "even_independent_solve",
        "even_note",
        "requested_precision_dps",
        "actual_precision_bits",
        "actual_decimal_digits",
        "recurrence_residual",
        "S",
        "absolute_S_difference_decimal",
        "no_phase_or_normalization_fit",
    }
    local_open_keys = {
        "backend",
        "status",
        "genuinely_independent",
        "even_independent_solve",
        "requested_precision_dps",
        "actual_precision_bits",
        "actual_decimal_digits",
        "blocker",
    }
    if set(local_mst) not in (local_available_keys, local_open_keys) or local_mst.get(
        "genuinely_independent"
    ) is not False:
        raise MpmathRadialContractError("local MST independence/schema mismatch")
    if (
        local_mst.get("even_independent_solve") is not expected_even_flag
        or local_mst.get("requested_precision_dps") != 70
        or local_mst.get("actual_precision_bits") != 53
        or local_mst.get("actual_decimal_digits") != 15.95
    ):
        raise MpmathRadialContractError("local MST precision/parity mismatch")
    if set(local_mst) == local_available_keys:
        expected_even_note = (
            "parity-derived; not an independent even radial solve"
            if mode["sector"] == "even"
            else None
        )
        if (
            local_mst.get("status") != "AVAILABLE"
            or local_mst.get("method") != "MST recurrence"
            or local_mst.get("independence_role")
            != "algorithmic internal cross-check; not source-independent external evidence"
            or local_mst.get("even_note") != expected_even_note
            or local_mst.get("no_phase_or_normalization_fit") is not True
        ):
            raise MpmathRadialContractError("local MST available comparison mismatch")
        _validate_complex_evidence_record(local_mst.get("S"), "local MST S")
        _validate_finite_real(
            local_mst.get("absolute_S_difference_decimal"),
            "local MST difference",
            nonnegative=True,
        )
        _validate_finite_real(
            local_mst.get("recurrence_residual"),
            "local MST recurrence residual",
            nonnegative=True,
        )
    elif (
        local_mst.get("status") != "OPEN_OR_FAIL_CLOSED"
        or not isinstance(local_mst.get("blocker"), str)
        or not local_mst["blocker"]
    ):
        raise MpmathRadialContractError("local MST open comparison mismatch")
    bhpt_available_keys = {
        "backend",
        "status",
        "method",
        "genuinely_independent",
        "even_independent_solve",
        "even_note",
        "actual_precision_bits",
        "actual_decimal_digits",
        "S",
        "absolute_S_difference_decimal",
        "no_phase_or_normalization_fit",
    }
    bhpt_open_keys = {
        "backend",
        "status",
        "genuinely_independent",
        "even_independent_solve",
        "actual_precision_bits",
        "actual_decimal_digits",
        "blocker",
    }
    if set(bhpt) not in (bhpt_available_keys, bhpt_open_keys):
        raise MpmathRadialContractError("BHPT comparison schema mismatch")
    if (
        bhpt.get("even_independent_solve") is not expected_even_flag
        or bhpt.get("actual_precision_bits") != 53
        or bhpt.get("actual_decimal_digits") != 15.95
    ):
        raise MpmathRadialContractError("BHPT comparison precision/parity mismatch")
    if set(bhpt) == bhpt_available_keys:
        expected_bhpt_independence = mode["sector"] == "odd"
        expected_even_note = (
            "Chandrasekhar parity-derived; not an independent even solve"
            if mode["sector"] == "even"
            else None
        )
        if (
            bhpt.get("status") != "AVAILABLE"
            or bhpt.get("method") != "MST"
            or bhpt.get("genuinely_independent") is not expected_bhpt_independence
            or bhpt.get("even_note") != expected_even_note
            or bhpt.get("no_phase_or_normalization_fit") is not True
        ):
            raise MpmathRadialContractError("BHPT available comparison mismatch")
        _validate_complex_evidence_record(bhpt.get("S"), "BHPT comparison S")
        _validate_finite_real(
            bhpt.get("absolute_S_difference_decimal"),
            "BHPT comparison difference",
            nonnegative=True,
        )
    elif (
        bhpt.get("status") != "OPEN_OR_FAIL_CLOSED"
        or bhpt.get("genuinely_independent") is not False
        or not isinstance(bhpt.get("blocker"), str)
        or not bhpt["blocker"]
    ):
        raise MpmathRadialContractError("BHPT open comparison mismatch")


__all__ = [
    "BACKEND_SCHEMA",
    "EVIDENCE_SCHEMA",
    "MpmathEvaluationPoint",
    "MpmathMode",
    "MpmathRadialContractError",
    "MpmathSolveConfig",
    "complex_from_record",
    "independent_jost_basis",
    "prove_call_graph_isolation",
    "radial_potential",
    "result_for",
    "schwarzschild_rstar",
    "selected_stage_a_modes",
    "solve_mode_batch",
    "validate_stage_a_evidence",
]
