"""Independent V3.1 mpmath matching at an exact requested radius.

This module is deliberately separate from the binary64 Route-A adapter.  It
uses only the already-audited, independently expressed mpmath RW/Zerilli
equations and Jost recurrence.  In particular, it handles the frozen
``n_aux == 0`` case without moving the requested match radius.
"""

from __future__ import annotations

import time
from typing import Any

import mpmath as mp

from schwgw.validation.phase6_mpmath_radial import (
    MpmathEvaluationPoint,
    MpmathMode,
    MpmathRadialContractError,
    MpmathSolveConfig,
    _complex_record,
    _integrate_to_radii,
    _real_record,
    _signed_current,
    independent_jost_basis,
)


def solve_exact_radius_direct(
    mode: MpmathMode,
    config: MpmathSolveConfig,
    *,
    evaluation_point: MpmathEvaluationPoint,
    match_radius: float,
    jost_order: int,
) -> dict[str, Any]:
    """Solve the independent AP direct branch at ``match_radius`` exactly."""

    started = time.perf_counter()
    with mp.workdps(config.working_dps):
        radius = mp.mpf(str(match_radius))
        point_radius = mp.mpf(evaluation_point.radius_M)
        if point_radius >= radius:
            raise MpmathRadialContractError(
                "AP evaluation point must be inside the exact match radius"
            )
        states, horizon_steps, horizon_drift, horizon_initial = _integrate_to_radii(
            mode, config, (point_radius, radius)
        )
        horizon = states[mp.nstr(radius, 30)]
        h = mp.mpc(horizon[1])
        hp = mp.mpc(horizon[2])
        if h == 0:
            raise MpmathRadialContractError("AP horizon solution vanished")
        k = mp.mpf(str(mode.kM))
        incoming = independent_jost_basis(
            sector=mode.sector,
            ell=mode.ell,
            k=k,
            radius=radius,
            sign=-1,
            order_cap=jost_order,
        )
        outgoing = independent_jost_basis(
            sector=mode.sector,
            ell=mode.ell,
            k=k,
            radius=radius,
            sign=1,
            order_cap=jost_order,
        )
        jin, jin_p = mp.mpc(incoming[0]), mp.mpc(incoming[1])
        jout, jout_p = mp.mpc(outgoing[0]), mp.mpc(outgoing[1])
        log_derivative = hp / h
        denominator = jout_p - log_derivative * jout
        if denominator == 0:
            raise MpmathRadialContractError("AP direct match is singular")
        reflection = (log_derivative * jin - jin_p) / denominator
        physical = jin + reflection * jout
        physical_p = jin_p + reflection * jout_p
        transmission = physical / h
        if transmission == 0:
            raise MpmathRadialContractError("AP direct transmission vanished")
        s_value = -reflection / ((-1) ** mode.ell)
        reflection_fraction = abs(reflection) ** 2
        transmission_fraction = abs(transmission) ** 2
        f_in = -2 * k
        f_out = 2 * k * reflection_fraction
        f_h = -2 * k * transmission_fraction
        absolute_balance = abs((f_in + f_out) - f_h)
        relative_balance = absolute_balance / abs(f_in)
        match_residual = abs(physical_p / physical - log_derivative)
        determinant = jin * jout_p - jin_p * jout
        determinant_scale = max(abs(jin * jout_p) + abs(jin_p * jout), mp.eps)
        condition = max(abs(jin), abs(jout), abs(log_derivative)) / max(
            abs(denominator), mp.eps
        )
        conjugacy_value = abs(jout - mp.conj(jin)) / max(abs(jout), abs(jin), mp.eps)
        conjugacy_derivative = abs(jout_p - mp.conj(jin_p)) / max(
            abs(jout_p), abs(jin_p), mp.eps
        )
        digits = min(config.working_dps, 180)
        finite = states[mp.nstr(point_radius, 30)]
        lapse = 1 - 2 / point_radius
        psi = transmission * mp.mpc(finite[1])
        momentum = transmission * mp.mpc(finite[2])
        initial_current = _signed_current(horizon_initial)
        physical_inner_current = abs(transmission) ** 2 * initial_current
        physical_match_current = mp.im(mp.conj(physical) * physical_p)
        tail_threshold = max(mp.mpf(incoming[5]), mp.mpf(outgoing[5]))
        selected_jost_gate = (
            ((not bool(incoming[4])) or mp.mpf(incoming[3]) <= mp.mpf(incoming[5]))
            and ((not bool(outgoing[4])) or mp.mpf(outgoing[3]) <= mp.mpf(outgoing[5]))
            and conjugacy_value <= mp.power(10, -min(20, config.working_dps // 3))
            and conjugacy_derivative <= mp.power(10, -min(20, config.working_dps // 3))
            and abs(determinant) / determinant_scale
            >= mp.power(10, -min(20, config.working_dps // 3))
        )
        if not selected_jost_gate:
            raise MpmathRadialContractError("AP selected Jost gate failed")
        elapsed = time.perf_counter() - started
        result = {
            "schema_version": "schwo.phase6.mpmath_radial_backend.v3",
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
                "shared_components": [
                    "RW/Zerilli equations and scattering conventions only"
                ],
            },
            "configuration": {
                "M": 1,
                "Fourier_convention": "exp(-i k t)",
                "r_in_eps": config.r_in_eps,
                "r_out_M": match_radius,
                "actual_r_out_M": _real_record(radius, digits),
                "r_out_radius_error": "0.0",
                "maximum_step_rstar": config.maximum_step_rstar,
                "Jost_order_cap": jost_order,
                "horizon_normalization": "unit exp(-i k r_star)",
                "outer_basis": "independent local AP J_in/J_out at exact match radius",
                "integration_architecture": "v3_1_exact_radius_direct_match",
                "common_match_radius_M": match_radius,
                "match_radius_policy": "frozen V3.1 requested node",
            },
            "unit_incoming_A_in": _complex_record(mp.mpc(1), digits),
            "unit_incoming_A_out": _complex_record(reflection, digits),
            "horizon_normalized_A_in": _complex_record(1 / transmission, digits),
            "horizon_normalized_A_out": _complex_record(
                reflection / transmission, digits
            ),
            "reflection_amplitude_Aout_over_Ain": _complex_record(reflection, digits),
            "S": _complex_record(s_value, digits),
            "unit_incoming_horizon_amplitude_T_H": _complex_record(
                transmission, digits
            ),
            "finite_radius_states": [
                {
                    "point_id": evaluation_point.point_id,
                    "radius_M": _real_record(point_radius, digits),
                    "actual_radius_M": _real_record(point_radius, digits),
                    "psi_over_Ain": _complex_record(psi, digits),
                    "dpsi_dr_over_Ain": _complex_record(momentum / lapse, digits),
                    "authoritative_branch": "T_H times outward horizon solution",
                }
            ],
            "signed_flux": {
                "F_inf_in": _real_record(f_in, digits),
                "F_inf_out": _real_record(f_out, digits),
                "F_H": _real_record(f_h, digits),
                "F_loss": "0.0",
                "horizon_flux_source": "direct |T_H|^2; not inferred from R",
                "horizon_flux_inferred_from_one_minus_R": False,
                "reflection_fraction": _real_record(reflection_fraction, digits),
                "horizon_transmission_fraction": _real_record(
                    transmission_fraction, digits
                ),
                "absolute_balance_residual": _real_record(absolute_balance, digits),
                "relative_balance_residual": _real_record(relative_balance, digits),
                "fraction_balance_residual": _real_record(
                    abs(reflection_fraction + transmission_fraction - 1), digits
                ),
            },
            "wronskian": {
                "raw_unit_horizon_signed_current": _real_record(
                    initial_current, digits
                ),
                "inner_signed_current": _real_record(physical_inner_current, digits),
                "outer_signed_current": _real_record(physical_match_current, digits),
                "maximum_relative_current_drift": _real_record(horizon_drift, digits),
            },
            "matching": {
                "reconstruction_residual": _real_record(match_residual, digits),
                "condition_estimate": _real_record(condition, digits),
                "incoming_effective_order": int(incoming[2]),
                "outgoing_effective_order": int(outgoing[2]),
                "incoming_tail_ratio": _real_record(mp.mpf(incoming[3]), digits),
                "outgoing_tail_ratio": _real_record(mp.mpf(outgoing[3]), digits),
                "tail_threshold": _real_record(tail_threshold, digits),
                "incoming_cap_reached": bool(incoming[4]),
                "outgoing_cap_reached": bool(outgoing[4]),
                "incoming_termination_reason": str(incoming[6]),
                "outgoing_termination_reason": str(outgoing[6]),
                "conjugacy_value_residual": _real_record(conjugacy_value, digits),
                "conjugacy_derivative_residual": _real_record(
                    conjugacy_derivative, digits
                ),
                "basis_determinant": _complex_record(determinant, digits),
                "basis_determinant_relative": _real_record(
                    abs(determinant) / determinant_scale, digits
                ),
                "selected_jost_gate_passed": selected_jost_gate,
            },
            "integration": {
                "steps": horizon_steps,
                "horizon_steps": horizon_steps,
                "outer_basis_steps": 0,
                "maximum_radius_state_drift": "0.0",
                "elapsed_seconds": elapsed,
            },
        }
    return {
        "result": result,
        "integration_steps": horizon_steps,
        "elapsed_seconds": elapsed,
    }


__all__ = ["solve_exact_radius_direct"]
