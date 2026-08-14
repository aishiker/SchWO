#!/usr/bin/env python3
"""Independent arbitrary-precision spot check for Li-Hou-Zhao Fig. 2.

The radial calculation in this script does not call the project SciPy radial
solver.  It integrates the RW/Zerilli equation in tortoise coordinate with
mpmath arithmetic, matches a horizon-ingoing logarithmic derivative to
independently integrated incoming/outgoing outer bases, and performs a
step-halving/Richardson check before evaluating the strict Kinnersley Psi4
shell with the frozen angular/reconstruction formulas.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import time
from typing import Any, Callable

import mpmath as mp
import numpy as np

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.perturbations import Sector, reconstruct_metric_mode
from schwgw.scattering.weyl import assemble_weyl_scalars, weyl_mode_components
from schwgw.waves import IncidentPlaneGW


@dataclass(frozen=True)
class HighPrecisionRadialState:
    psi: mp.mpc
    dpsi_dr: mp.mpc
    reflection: mp.mpc
    radius_error: mp.mpf
    outer_basis_orders: tuple[int, int]
    outer_basis_max_tail_ratio: mp.mpf


def _potential(sector: Sector, ell: int, radius: mp.mpf) -> mp.mpf:
    f = 1 - 2 / radius
    if sector is Sector.ODD:
        return f / radius**2 * (ell * (ell + 1) - 6 / radius)
    lambda_ = mp.mpf(ell - 1) * (ell + 2) / 2
    mass_over_r = 1 / radius
    Lambda = lambda_ + 3 * mass_over_r
    bracket = (
        2 * lambda_**2 * (lambda_ + 1)
        + 6 * lambda_**2 * mass_over_r
        + 18 * lambda_ * mass_over_r**2
        + 18 * mass_over_r**3
    )
    return f / radius**2 * bracket / Lambda**2


def _rstar(radius: mp.mpf) -> mp.mpf:
    return radius + 2 * mp.log(radius / 2 - 1)


def _potential_series(
    sector: Sector,
    ell: int,
    order: int,
) -> list[mp.mpf]:
    """Return the independent formal ``V=sum(v_n/r**n)`` coefficients."""

    values = [mp.mpf("0") for _ in range(order + 1)]
    angular = mp.mpf(ell * (ell + 1))
    if sector is Sector.ODD:
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


def _jost_outer_basis(
    *,
    sector: Sector,
    ell: int,
    frequency: mp.mpf,
    radius: mp.mpf,
    sign: int,
    order_cap: int,
) -> tuple[mp.mpc, mp.mpc, int, mp.mpf]:
    """Evaluate one Jost basis independently with mpmath arithmetic.

    The returned derivative is with respect to tortoise radius, matching the
    state used by the independent RK4 integrator.  The asymptotic series is
    stopped at its numerically detected least term rather than summed past
    the divergent tail.
    """

    potential = _potential_series(sector, ell, order_cap + 2)
    f_squared = (mp.mpf(1), mp.mpf(-4), mp.mpf(4))
    derivative_coefficients = (
        2j * sign * frequency,
        -4j * sign * frequency,
        mp.mpf(2),
        mp.mpf(-4),
    )
    terms: list[mp.mpc] = [mp.mpc(1)]
    decreasing_run = 0
    increasing_run = 0
    optimal_index: int | None = None
    threshold = mp.power(10, -min(40, max(20, mp.mp.dps // 2)))
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
        pivot = -2j * sign * frequency * index
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
            break
        if index >= 16 and max(abs(value) for value in terms[-4:]) < threshold:
            terms = terms[: index + 1]
            break
    series = mp.fsum(terms)
    derivative_r = -mp.fsum(
        index * value for index, value in enumerate(terms)
    ) / radius
    phase = mp.exp(sign * 1j * frequency * _rstar(radius))
    lapse = 1 - 2 / radius
    value = phase * series
    derivative_rstar = phase * (sign * 1j * frequency * series + lapse * derivative_r)
    tail_width = min(4, len(terms) - 1)
    tail_ratio = mp.fsum(abs(value) for value in terms[-tail_width:]) / max(
        abs(series), mp.eps
    )
    return value, derivative_rstar, len(terms) - 1, tail_ratio


def _rhs(
    sector: Sector,
    ell: int,
    frequency: mp.mpf,
    state: list[mp.mpf | mp.mpc],
) -> list[mp.mpf | mp.mpc]:
    radius = mp.mpf(state[0])
    f = 1 - 2 / radius
    potential = _potential(sector, ell, radius)
    result: list[mp.mpf | mp.mpc] = [f]
    for index in range(1, len(state), 2):
        psi = mp.mpc(state[index])
        momentum = mp.mpc(state[index + 1])
        result.extend((momentum, -(frequency**2 - potential) * psi))
    return result


def _rk4_step(
    function: Callable[[list[mp.mpf | mp.mpc]], list[mp.mpf | mp.mpc]],
    state: list[mp.mpf | mp.mpc],
    step: mp.mpf,
) -> list[mp.mpf | mp.mpc]:
    first = function(state)
    second_state = [value + step * slope / 2 for value, slope in zip(state, first)]
    second = function(second_state)
    third_state = [value + step * slope / 2 for value, slope in zip(state, second)]
    third = function(third_state)
    fourth_state = [value + step * slope for value, slope in zip(state, third)]
    fourth = function(fourth_state)
    return [
        value + step * (a + 2 * b + 2 * c + d) / 6
        for value, a, b, c, d in zip(state, first, second, third, fourth)
    ]


def _integrate(
    function: Callable[[list[mp.mpf | mp.mpc]], list[mp.mpf | mp.mpc]],
    state: list[mp.mpf | mp.mpc],
    start: mp.mpf,
    stop: mp.mpf,
    maximum_step: mp.mpf,
) -> tuple[list[mp.mpf | mp.mpc], int]:
    count = int(mp.ceil(abs(stop - start) / maximum_step))
    step = (stop - start) / count
    current = state
    for _ in range(count):
        current = _rk4_step(function, current, step)
    return current, count


def solve_normalized_radial_state(
    *,
    sector: Sector,
    ell: int,
    frequency: mp.mpf,
    radius: mp.mpf,
    r_in_eps: mp.mpf,
    r_out: mp.mpf,
    maximum_step: mp.mpf,
    outer_series_order: int,
) -> tuple[HighPrecisionRadialState, int]:
    """Solve for the unit-incoming radial state at ``radius``."""

    r_in = 2 + r_in_eps
    x_in = _rstar(r_in)
    x_observer = _rstar(radius)
    x_out = _rstar(r_out)
    def rhs(state: list[mp.mpf | mp.mpc]) -> list[mp.mpf | mp.mpc]:
        return _rhs(sector, ell, frequency, state)

    horizon_phase = mp.exp(-1j * frequency * x_in)
    horizon, horizon_steps = _integrate(
        rhs,
        [r_in, horizon_phase, -1j * frequency * horizon_phase],
        x_in,
        x_observer,
        maximum_step,
    )
    incoming, incoming_derivative, incoming_order, incoming_tail = _jost_outer_basis(
        sector=sector,
        ell=ell,
        frequency=frequency,
        radius=r_out,
        sign=-1,
        order_cap=outer_series_order,
    )
    outgoing, outgoing_derivative, outgoing_order, outgoing_tail = _jost_outer_basis(
        sector=sector,
        ell=ell,
        frequency=frequency,
        radius=r_out,
        sign=1,
        order_cap=outer_series_order,
    )
    bases, basis_steps = _integrate(
        rhs,
        [
            r_out,
            incoming,
            incoming_derivative,
            outgoing,
            outgoing_derivative,
        ],
        x_out,
        x_observer,
        maximum_step,
    )
    horizon_log_derivative = mp.mpc(horizon[2]) / mp.mpc(horizon[1])
    incoming_value = mp.mpc(bases[1])
    incoming_derivative = mp.mpc(bases[2])
    outgoing_value = mp.mpc(bases[3])
    outgoing_derivative = mp.mpc(bases[4])
    reflection = (
        horizon_log_derivative * incoming_value - incoming_derivative
    ) / (outgoing_derivative - horizon_log_derivative * outgoing_value)
    psi = incoming_value + reflection * outgoing_value
    dpsi_drstar = incoming_derivative + reflection * outgoing_derivative
    f_observer = 1 - 2 / radius
    return (
        HighPrecisionRadialState(
            psi=psi,
            dpsi_dr=dpsi_drstar / f_observer,
            reflection=reflection,
            radius_error=mp.mpf(bases[0]) - radius,
            outer_basis_orders=(incoming_order, outgoing_order),
            outer_basis_max_tail_ratio=max(incoming_tail, outgoing_tail),
        ),
        horizon_steps + basis_steps,
    )


def _richardson(coarse: mp.mpc, fine: mp.mpc) -> tuple[mp.mpc, mp.mpf]:
    extrapolated = (16 * fine - coarse) / 15
    return extrapolated, abs(fine - coarse) / 15


def _quadratic_inverse_radius_extrapolation(
    radii: tuple[float, float, float],
    values: tuple[mp.mpc, mp.mpc, mp.mpc],
) -> tuple[mp.mpc, mp.mpf]:
    """Extrapolate three values to ``1/r_out=0`` and estimate fit order."""

    inverse_radii = [1 / mp.mpf(str(radius)) for radius in radii]
    design = mp.matrix([[1, value, value**2] for value in inverse_radii])
    quadratic = mp.lu_solve(design, mp.matrix(values))[0]
    linear_design = mp.matrix(
        [[1, inverse_radii[index]] for index in (1, 2)]
    )
    linear = mp.lu_solve(
        linear_design,
        mp.matrix([values[1], values[2]]),
    )[0]
    return mp.mpc(quadratic), abs(quadratic - linear)


def _strict_psi4_shell(
    *,
    ell: int,
    frequency: float,
    radius: float,
    theta: float,
    phi: float,
    A_plus: complex,
    A_cross: complex,
    radial_states: dict[Sector, tuple[complex, complex]],
) -> complex:
    background = SchwarzschildBackground(M=1.0)
    incident = IncidentPlaneGW(frequency, A_plus, A_cross)
    modes = []
    for sector in (Sector.ODD, Sector.EVEN):
        psi, derivative = radial_states[sector]
        for m in (-2, 2):
            coefficient = (
                incident.c_lm_odd(ell, m)
                if sector is Sector.ODD
                else incident.c_lm_even(ell, m)
            )
            metric = reconstruct_metric_mode(
                sector,
                ell,
                frequency,
                radius,
                coefficient * psi,
                coefficient * derivative,
                background,
            )
            modes.append(
                weyl_mode_components(
                    sector,
                    ell,
                    m,
                    frequency,
                    radius,
                    theta,
                    phi,
                    metric,
                    background,
                )
            )
    return complex(assemble_weyl_scalars(modes)["Psi4"])


def _complex_record(value: complex | mp.mpc, digits: int = 50) -> dict[str, str]:
    converted = mp.mpc(value)
    return {
        "real": mp.nstr(converted.real, digits),
        "imag": mp.nstr(converted.imag, digits),
        "abs": mp.nstr(abs(converted), digits),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(args: argparse.Namespace) -> dict[str, Any]:
    mp.mp.dps = args.dps
    started = time.perf_counter()
    source = Path(__file__).resolve()
    artifact_path = args.reference_npz.resolve()
    with np.load(artifact_path, allow_pickle=False) as artifact:
        ell_axis = np.asarray(artifact["lmax_values"], dtype=int)
        stored_shells = {
            ell: complex(
                artifact["psi4_shell_kinnersley"][
                    int(np.where(artifact["kM_values"] == args.kM)[0][0]),
                    int(np.where(np.isclose(artifact["theta_values"], args.theta))[0][0]),
                    int(np.where(ell_axis == ell)[0][0]),
                ]
            )
            for ell in args.ells
        }

    cases: list[dict[str, Any]] = []
    r_out_ladder = tuple(float(value) for value in args.r_out_ladder)
    for ell in args.ells:
        radial_extrapolated: dict[Sector, tuple[complex, complex]] = {}
        radial_case: dict[str, Any] = {}
        for sector in (Sector.ODD, Sector.EVEN):
            psi_ladder: list[mp.mpc] = []
            derivative_ladder: list[mp.mpc] = []
            radius_records: list[dict[str, Any]] = []
            for r_out in r_out_ladder:
                coarse, coarse_steps = solve_normalized_radial_state(
                    sector=sector,
                    ell=ell,
                    frequency=mp.mpf(str(args.kM)),
                    radius=mp.mpf(str(args.radius)),
                    r_in_eps=mp.mpf(str(args.r_in_eps)),
                    r_out=mp.mpf(str(r_out)),
                    maximum_step=mp.mpf(str(args.coarse_step)),
                    outer_series_order=args.outer_series_order,
                )
                fine, fine_steps = solve_normalized_radial_state(
                    sector=sector,
                    ell=ell,
                    frequency=mp.mpf(str(args.kM)),
                    radius=mp.mpf(str(args.radius)),
                    r_in_eps=mp.mpf(str(args.r_in_eps)),
                    r_out=mp.mpf(str(r_out)),
                    maximum_step=mp.mpf(str(args.fine_step)),
                    outer_series_order=args.outer_series_order,
                )
                psi_at_radius, psi_step_error = _richardson(
                    coarse.psi, fine.psi
                )
                derivative_at_radius, derivative_step_error = _richardson(
                    coarse.dpsi_dr,
                    fine.dpsi_dr,
                )
                psi_ladder.append(psi_at_radius)
                derivative_ladder.append(derivative_at_radius)
                radius_records.append(
                    {
                        "r_out": r_out,
                        "psi_over_Ain": _complex_record(psi_at_radius),
                        "dpsi_dr_over_Ain": _complex_record(
                            derivative_at_radius
                        ),
                        "psi_step_error_estimate": mp.nstr(
                            psi_step_error, 20
                        ),
                        "dpsi_dr_step_error_estimate": mp.nstr(
                            derivative_step_error, 20
                        ),
                        "coarse_reflection": _complex_record(
                            coarse.reflection, 30
                        ),
                        "fine_reflection": _complex_record(fine.reflection, 30),
                        "coarse_steps": coarse_steps,
                        "fine_steps": fine_steps,
                        "fine_radius_error": mp.nstr(fine.radius_error, 20),
                        "coarse_outer_basis_orders": list(
                            coarse.outer_basis_orders
                        ),
                        "fine_outer_basis_orders": list(fine.outer_basis_orders),
                        "fine_outer_basis_max_tail_ratio": mp.nstr(
                            fine.outer_basis_max_tail_ratio, 20
                        ),
                    }
                )
            psi, psi_r_out_error = _quadratic_inverse_radius_extrapolation(
                r_out_ladder,
                tuple(psi_ladder),  # type: ignore[arg-type]
            )
            derivative, derivative_r_out_error = (
                _quadratic_inverse_radius_extrapolation(
                    r_out_ladder,
                    tuple(derivative_ladder),  # type: ignore[arg-type]
                )
            )
            radial_extrapolated[sector] = (complex(psi), complex(derivative))
            radial_case[sector.value] = {
                "r_out_ladder": radius_records,
                "psi_over_Ain_extrapolated": _complex_record(psi),
                "dpsi_dr_over_Ain_extrapolated": _complex_record(derivative),
                "psi_r_out_error_estimate": mp.nstr(psi_r_out_error, 20),
                "dpsi_dr_r_out_error_estimate": mp.nstr(
                    derivative_r_out_error, 20
                ),
                "outer_basis": "Jost exp(+-ikr*) sum(a_n/r^n)",
                "r_out_extrapolation": "quadratic in 1/r_out",
            }
        shell = _strict_psi4_shell(
            ell=ell,
            frequency=args.kM,
            radius=args.radius,
            theta=args.theta,
            phi=args.phi,
            A_plus=args.A_plus,
            A_cross=args.A_cross,
            radial_states=radial_extrapolated,
        )
        stored = stored_shells[ell]
        cases.append(
            {
                "ell": ell,
                "radial": radial_case,
                "high_precision_radial_shell_psi4": _complex_record(shell, 30),
                "stored_double_shell_psi4": _complex_record(stored, 30),
                "shell_absolute_difference": abs(shell - stored),
                "shell_relative_difference": abs(shell - stored) / max(abs(shell), 1.0e-300),
                "exceeds_unit_amplitude": bool(abs(shell) > 1.0),
                "exceeds_1e6_amplitude": bool(abs(shell) > 1.0e6),
            }
        )
    return {
        "schema_version": "schwgw_fig2_arbitrary_precision_jost_rout_v3",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": (
            "independent mpmath tortoise-coordinate RK4; horizon logarithmic "
            "derivative matched to separately integrated Jost 1/r incoming/outgoing "
            "bases; "
            "step-halving plus fourth-order Richardson extrapolation"
        ),
        "mpmath_working_precision_digits": args.dps,
        "discretization_note": (
            "working precision is not the claimed number of correct output digits; "
            "reported coarse/fine Richardson estimates bound the integration error"
        ),
        "parameters": {
            "M": 1.0,
            "kM": args.kM,
            "radius_over_M": args.radius,
            "theta": args.theta,
            "phi": args.phi,
            "A_plus": {"real": args.A_plus.real, "imag": args.A_plus.imag},
            "A_cross": {"real": args.A_cross.real, "imag": args.A_cross.imag},
            "ells": list(args.ells),
            "r_in_eps": args.r_in_eps,
            "r_out_ladder": list(r_out_ladder),
            "r_out_extrapolation": "quadratic in 1/r_out",
            "outer_basis": "jost_1_over_r",
            "outer_series_order_cap": args.outer_series_order,
            "coarse_step_rstar": args.coarse_step,
            "fine_step_rstar": args.fine_step,
        },
        "source": {"path": str(source), "sha256": _sha256(source)},
        "reference": {"path": str(artifact_path), "sha256": _sha256(artifact_path)},
        "cases": cases,
        "all_shells_below_unit_amplitude": all(
            not case["exceeds_unit_amplitude"] for case in cases
        ),
        "all_shells_below_1e6_amplitude": all(
            not case["exceeds_1e6_amplitude"] for case in cases
        ),
        "elapsed_seconds": time.perf_counter() - started,
    }


def _complex_argument(value: str) -> complex:
    return complex(value.replace("i", "j"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dps", type=int, default=80)
    parser.add_argument("--ells", type=int, nargs="+", default=(110, 120, 130, 140))
    parser.add_argument("--kM", type=float, default=2.0)
    parser.add_argument("--radius", type=float, default=60.0)
    parser.add_argument("--theta", type=float, default=math.pi / 6.0)
    parser.add_argument("--phi", type=float, default=0.0)
    parser.add_argument("--A-plus", type=_complex_argument, default=0.9 + 1.1j)
    parser.add_argument("--A-cross", type=_complex_argument, default=0.4 + 0.6j)
    parser.add_argument("--r-in-eps", type=float, default=1.0e-10)
    parser.add_argument(
        "--r-out-ladder",
        type=float,
        nargs=3,
        default=(300.0, 600.0, 1200.0),
    )
    parser.add_argument("--outer-series-order", type=int, default=160)
    parser.add_argument("--coarse-step", type=float, default=0.02)
    parser.add_argument("--fine-step", type=float, default=0.01)
    parser.add_argument(
        "--reference-npz",
        type=Path,
        default=Path(
            "runs/phase5/paper_figures/fig2_strict_psi4_convergence/"
            "fig2_strict_psi4_convergence_data.npz"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "runs/phase5/paper_figures/fig2_high_precision_20260802/"
            "fig2_high_precision_spotcheck.json"
        ),
    )
    args = parser.parse_args()
    if not 60 <= args.dps <= 100:
        parser.error("--dps must lie in the independently reviewed 60..100 range")
    if args.fine_step <= 0.0 or args.coarse_step <= args.fine_step:
        parser.error("require 0 < fine-step < coarse-step")
    if args.coarse_step / args.fine_step != 2.0:
        parser.error("Richardson check requires coarse-step == 2*fine-step")
    if not 2 <= args.outer_series_order <= 256:
        parser.error("--outer-series-order must lie in 2..256")
    if any(value <= args.radius for value in args.r_out_ladder):
        parser.error("every r-out ladder value must exceed the observer radius")
    if tuple(sorted(set(args.r_out_ladder))) != tuple(args.r_out_ladder):
        parser.error("r-out ladder must contain three unique increasing radii")
    return args


def main() -> int:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing output collision: {args.output}")
    result = verify(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    temporary = args.output.with_name(f".{args.output.name}.partial")
    if temporary.exists():
        raise FileExistsError(f"refusing temporary collision: {temporary}")
    with temporary.open("x", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, args.output)
    print(json.dumps({
        "event": "fig2_high_precision_spotcheck_complete",
        "output": str(args.output),
        "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "all_shells_below_unit_amplitude": result["all_shells_below_unit_amplitude"],
        "elapsed_seconds": result["elapsed_seconds"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
