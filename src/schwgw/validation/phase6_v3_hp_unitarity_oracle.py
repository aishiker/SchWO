"""Independent arbitrary-precision S-route oracle for Phase-6 V3.1-U.

This module deliberately imports no Route-A or protected radial implementation.
It reuses only the independently expressed mpmath RW/Zerilli equations and
integrators already used by Route B.  Every call starts from analytic boundary
data and returns a fresh complex scattering amplitude.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
import time
from typing import Any, Mapping, Sequence

import mpmath as mp

from schwgw.validation.phase6_mpmath_radial import (
    MpmathMode,
    MpmathRadialContractError,
    MpmathSolveConfig,
    _integrate_state_to_radii,
    _integrate_to_radii,
    independent_jost_basis,
    schwarzschild_rstar,
)


ORACLE_SCHEMA = "schwo.phase6.v3_1_u.oracle_node.v1"
LADDER_SCHEMA = "schwo.phase6.v3_1_u.oracle_ladder.v1"
ADJACENT_LOG_GAMMA_MAX = mp.mpf("2e-5")
ADJACENT_S_SYMMETRIC_RELATIVE_MAX = mp.mpf("5e-8")
MINIMUM_GUARD_DIGITS = 30


class HPUnitarityOracleError(RuntimeError):
    """The independent Route-U oracle failed closed."""


@dataclass(frozen=True)
class OracleMode:
    kM: str
    ell: int
    parity: str

    def __post_init__(self) -> None:
        if self.parity not in {"odd", "even"} or self.ell < 2:
            raise ValueError("invalid Route-U mode")
        if not mp.isfinite(mp.mpf(self.kM)) or mp.mpf(self.kM) <= 0:
            raise ValueError("invalid Route-U frequency")

    def payload(self) -> dict[str, Any]:
        return {"ell": self.ell, "kM": self.kM, "parity": self.parity}


def gamma_decimal_value(record: Mapping[str, Any]) -> mp.mpf:
    """Parse the direct Route-A arbitrary-exponent Gamma representation."""

    if set(record) != {"exponent10", "mantissa"}:
        raise HPUnitarityOracleError("Gamma decimal schema mismatch")
    exponent = record["exponent10"]
    mantissa_text = record["mantissa"]
    if not isinstance(exponent, int) or isinstance(exponent, bool):
        raise HPUnitarityOracleError("Gamma exponent must be an integer")
    if not isinstance(mantissa_text, str):
        raise HPUnitarityOracleError("Gamma mantissa must be decimal text")
    with mp.workdps(100):
        mantissa = mp.mpf(mantissa_text)
        value = mantissa * mp.power(10, exponent)
        if not mp.isfinite(value) or value <= 0 or not (1 <= mantissa < 10):
            raise HPUnitarityOracleError("Gamma decimal is not normalized positive")
        return +value


def precision_schedule(gamma_decimal: Mapping[str, Any]) -> tuple[int, int, int]:
    """Return the frozen non-post-hoc three-node precision schedule."""

    gamma_decimal_value(gamma_decimal)
    e10 = gamma_decimal["exponent10"]
    p0 = 20 * math.ceil(max(80, 30 - e10) / 20)
    nodes = (p0, p0 + 40, p0 + 100)
    if nodes[0] + e10 < MINIMUM_GUARD_DIGITS:
        raise HPUnitarityOracleError("precision schedule lacks guard digits")
    return nodes


def independent_geometry(
    *, ell: int, k: mp.mpf, k_decimal: str, match_radius: mp.mpf
) -> tuple[mp.mpf, int]:
    """Apply the frozen closed auxiliary-radius rule without cancellation.

    The returned radius is still ``2**q * match_radius`` in mpmath arithmetic.
    Only membership in the fixed exponent set is evaluated in an algebraically
    equivalent squared form.  In particular, the turning-radius branch has
    ``(k R_match)^2/L2 == 1`` by construction, so its exponent-2 endpoint is
    represented exactly instead of subtracting two rounded square roots.
    """

    try:
        exact_k = Fraction(k_decimal)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise HPUnitarityOracleError(
            "invalid independent oracle frequency text"
        ) from exc
    if (
        not isinstance(ell, int)
        or isinstance(ell, bool)
        or ell < 2
        or not isinstance(k_decimal, str)
        or mp.mpf(k_decimal) != k
        or exact_k <= 0
        or not mp.isfinite(k)
        or k <= 0
        or not mp.isfinite(match_radius)
        or match_radius <= 2
    ):
        raise HPUnitarityOracleError("invalid independent oracle geometry")
    l2 = ell * (ell + 1)
    fixed_radius = mp.mpf(300)
    fixed_ratio_squared = (300 * exact_k) ** 2
    fixed_branch = fixed_ratio_squared >= l2
    expected_match = fixed_radius if fixed_branch else mp.sqrt(l2) / k
    if match_radius != expected_match:
        raise HPUnitarityOracleError("independent oracle match radius drift")

    for exponent in (0, 1, 2):
        if fixed_branch:
            admissible = (4**exponent) * fixed_ratio_squared >= 16 * l2
        else:
            admissible = 4**exponent >= 16
        if admissible:
            return (2**exponent) * match_radius, exponent
    raise HPUnitarityOracleError("independent oracle auxiliary-radius domain empty")


def solve_oracle_node(
    mode: OracleMode,
    *,
    dps: int,
    route_a_gamma_decimal: Mapping[str, Any],
    route_map_sha256: str,
    mode_ordinal: int,
    precision_ordinal: int,
) -> dict[str, Any]:
    """Perform one fresh independent mpmath solve and derive Gamma_S from S."""

    schedule = precision_schedule(route_a_gamma_decimal)
    if precision_ordinal not in range(3) or dps != schedule[precision_ordinal]:
        raise HPUnitarityOracleError("Route-U precision node differs from schedule")
    if not isinstance(route_map_sha256, str) or len(route_map_sha256) != 64:
        raise HPUnitarityOracleError("Route-U route-map identity malformed")
    started = time.perf_counter()
    with mp.workdps(dps):
        k = mp.mpf(mode.kM)
        match_radius = max(mp.mpf(300), mp.sqrt(mode.ell * (mode.ell + 1)) / k)
        outer_radius, auxiliary_exponent = independent_geometry(
            ell=mode.ell,
            k=k,
            k_decimal=mode.kM,
            match_radius=match_radius,
        )
        ap_mode = MpmathMode(
            mode_id=f"v31u_{mode.kM}_{mode.parity}_{mode.ell}",
            regime="v3_1_u_fresh_oracle",
            sector=mode.parity,
            ell=mode.ell,
            kM=float(mode.kM),
            evaluation_radius_M=40.0,
        )
        config = MpmathSolveConfig(
            working_dps=dps,
            r_in_eps=1e-10,
            maximum_step_rstar=min(0.2, 0.015 / float(mode.kM)),
            pilot_match_radius_M=float(match_radius),
        )
        raw = _fresh_match(
            ap_mode,
            config,
            match_radius=match_radius,
            outer_radius=outer_radius,
            jost_order=160,
        )
        s_value = raw["S"]
        log_abs_s = mp.log(abs(s_value))
        gamma_s = -mp.expm1(2 * log_abs_s)
        if not mp.isfinite(gamma_s) or gamma_s <= 0:
            raise HPUnitarityOracleError("Route-U Gamma_S is unresolved/nonpositive")
        log_gamma_s = mp.log(gamma_s)
        e10 = int(route_a_gamma_decimal["exponent10"])
        guard_digits = dps + e10
        if guard_digits < MINIMUM_GUARD_DIGITS:
            raise HPUnitarityOracleError(
                "Route-U recorded guard margin is insufficient"
            )
        call_payload = {
            "dps": dps,
            "mode": mode.payload(),
            "mode_ordinal": mode_ordinal,
            "precision_ordinal": precision_ordinal,
            "route_map_sha256": route_map_sha256,
        }
        call_id = hashlib.sha256(
            json.dumps(call_payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        digits = dps
        return {
            "schema": ORACLE_SCHEMA,
            "mode": mode.payload(),
            "mode_ordinal": mode_ordinal,
            "precision_ordinal": precision_ordinal,
            "requested_dps": dps,
            "actual_dps": mp.mp.dps,
            "actual_bits": mp.mp.prec,
            "guard_digits": guard_digits,
            "precision_schedule": list(schedule),
            "route_map_sha256": route_map_sha256,
            "fresh_call_id": call_id,
            "fresh_call_count": 1,
            "route_b_record_or_cache_reused": False,
            "route_a_numerical_code_shared": False,
            "protected_radial_imported": False,
            "backend": f"mpmath {mp.__version__}",
            "equation": "RW" if mode.parity == "odd" else "Zerilli",
            "fourier_convention": "exp(-i k t)",
            "S_U": _complex_record(s_value, digits),
            "log_abs_S_U": _real_record(log_abs_s, digits),
            "Gamma_S_U": _real_record(gamma_s, digits),
            "log_Gamma_S_U": _real_record(log_gamma_s, digits),
            "unit_incoming_T_H": _complex_record(raw["T_H"], digits),
            "direct_Gamma_flux_U_diagnostic": _real_record(
                abs(raw["T_H"]) ** 2, digits
            ),
            "matching": {
                "match_radius": _real_record(match_radius, digits),
                "jost_initialization_radius": _real_record(outer_radius, digits),
                "auxiliary_exponent": auxiliary_exponent,
                "jost_order": 160,
                "reconstruction_residual": _real_record(raw["match_residual"], digits),
                "basis_determinant": _complex_record(raw["determinant"], digits),
                "incoming_tail_ratio": _real_record(raw["incoming_tail"], digits),
                "outgoing_tail_ratio": _real_record(raw["outgoing_tail"], digits),
            },
            "integration_steps": raw["integration_steps"],
            "elapsed_seconds": time.perf_counter() - started,
        }


def validate_oracle_ladder(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Validate exactly three ordered nodes and both numerical-admission bounds."""

    if len(records) != 3:
        raise HPUnitarityOracleError("Route-U ladder is not exactly three nodes")
    first = records[0]
    schedule = tuple(first["precision_schedule"])
    if tuple(item["requested_dps"] for item in records) != schedule:
        raise HPUnitarityOracleError("Route-U ladder order/schedule mismatch")
    if tuple(item["precision_ordinal"] for item in records) != (0, 1, 2):
        raise HPUnitarityOracleError("Route-U precision ordinals mismatch")
    mode = first["mode"]
    route_map_sha = first["route_map_sha256"]
    if any(
        item["schema"] != ORACLE_SCHEMA
        or item["mode"] != mode
        or item["route_map_sha256"] != route_map_sha
        or item["fresh_call_count"] != 1
        or item["guard_digits"] < MINIMUM_GUARD_DIGITS
        or item["route_b_record_or_cache_reused"] is not False
        or item["route_a_numerical_code_shared"] is not False
        or item["protected_radial_imported"] is not False
        for item in records
    ):
        raise HPUnitarityOracleError("Route-U ladder identity/provenance mismatch")
    log_changes: list[str] = []
    s_changes: list[str] = []
    with mp.workdps(max(item["requested_dps"] for item in records) + 30):
        for item in records:
            gamma = mp.mpf(item["Gamma_S_U"])
            log_gamma = mp.mpf(item["log_Gamma_S_U"])
            s_value = _mp_complex(item["S_U"])
            operand_tolerance = mp.power(10, -item["guard_digits"] + 5)
            if (
                not mp.isfinite(gamma)
                or gamma <= 0
                or abs(mp.log(gamma) - log_gamma) > operand_tolerance
                or abs(-mp.expm1(2 * mp.log(abs(s_value))) - gamma)
                > gamma * operand_tolerance
            ):
                raise HPUnitarityOracleError("Route-U serialized operand mismatch")
        for left, right in zip(records, records[1:]):
            log_delta = abs(
                mp.mpf(left["log_Gamma_S_U"]) - mp.mpf(right["log_Gamma_S_U"])
            )
            s_left, s_right = _mp_complex(left["S_U"]), _mp_complex(right["S_U"])
            s_delta = (
                2
                * abs(s_left - s_right)
                / max(abs(s_left) + abs(s_right), mp.mpf("1e-100000"))
            )
            log_changes.append(_real_record(log_delta, 50))
            s_changes.append(_real_record(s_delta, 50))
            if log_delta > ADJACENT_LOG_GAMMA_MAX:
                raise HPUnitarityOracleError(
                    "Route-U adjacent log-Gamma admission failed"
                )
            if s_delta > ADJACENT_S_SYMMETRIC_RELATIVE_MAX:
                raise HPUnitarityOracleError("Route-U adjacent S admission failed")
    return {
        "schema": LADDER_SCHEMA,
        "mode": mode,
        "mode_ordinal": first["mode_ordinal"],
        "precision_schedule": list(schedule),
        "fresh_call_ids": [item["fresh_call_id"] for item in records],
        "adjacent_log_Gamma_S_changes": log_changes,
        "adjacent_S_symmetric_relative_changes": s_changes,
        "maximum_adjacent_log_Gamma_S_change": max(log_changes, key=mp.mpf),
        "maximum_adjacent_S_symmetric_relative_change": max(s_changes, key=mp.mpf),
        "minimum_guard_digits": min(item["guard_digits"] for item in records),
        "status": "PASS",
    }


def _fresh_match(
    mode: MpmathMode,
    config: MpmathSolveConfig,
    *,
    match_radius: mp.mpf,
    outer_radius: mp.mpf,
    jost_order: int,
) -> dict[str, Any]:
    """Fresh bidirectional exact 2x2 match, independent of Route A."""

    states, horizon_steps, _drift, _initial = _integrate_to_radii(
        mode, config, (match_radius,)
    )
    horizon = states[mp.nstr(match_radius, 30)]
    h, hp = mp.mpc(horizon[1]), mp.mpc(horizon[2])
    if h == 0:
        raise MpmathRadialContractError("Route-U horizon solution vanished")
    k = mp.mpf(str(mode.kM))
    incoming = independent_jost_basis(
        sector=mode.sector,
        ell=mode.ell,
        k=k,
        radius=outer_radius,
        sign=-1,
        order_cap=jost_order,
    )
    outgoing = independent_jost_basis(
        sector=mode.sector,
        ell=mode.ell,
        k=k,
        radius=outer_radius,
        sign=1,
        order_cap=jost_order,
    )
    if outer_radius == match_radius:
        jin, jin_p = mp.mpc(incoming[0]), mp.mpc(incoming[1])
        jout, jout_p = mp.mpc(outgoing[0]), mp.mpc(outgoing[1])
        outer_steps = 0
    else:
        initial = [outer_radius, incoming[0], incoming[1], outgoing[0], outgoing[1]]
        propagated, outer_steps, _ = _integrate_state_to_radii(
            mode,
            initial,
            start_rstar=schwarzschild_rstar(outer_radius),
            radii=(match_radius,),
            maximum_step_rstar=mp.mpf(str(config.maximum_step_rstar)),
            outward=False,
        )
        matched = propagated[mp.nstr(match_radius, 30)]
        jin, jin_p = mp.mpc(matched[1]), mp.mpc(matched[2])
        jout, jout_p = mp.mpc(matched[3]), mp.mpc(matched[4])
    log_derivative = hp / h
    denominator = jout_p - log_derivative * jout
    if denominator == 0:
        raise MpmathRadialContractError("Route-U match is singular")
    reflection = (log_derivative * jin - jin_p) / denominator
    physical = jin + reflection * jout
    physical_p = jin_p + reflection * jout_p
    transmission = physical / h
    if transmission == 0:
        raise MpmathRadialContractError("Route-U transmission vanished")
    determinant = jin * jout_p - jin_p * jout
    residual = abs(physical_p / physical - log_derivative)
    return {
        "S": -reflection / ((-1) ** mode.ell),
        "T_H": transmission,
        "determinant": determinant,
        "match_residual": residual,
        "incoming_tail": mp.mpf(incoming[3]),
        "outgoing_tail": mp.mpf(outgoing[3]),
        "integration_steps": horizon_steps + outer_steps,
    }


def _complex_record(value: mp.mpc, digits: int) -> dict[str, str]:
    real = mp.nstr(mp.re(value), digits)
    imag = mp.nstr(mp.im(value), digits)
    serialized = mp.mpc(mp.mpf(real), mp.mpf(imag))
    return {"real": real, "imag": imag, "abs": mp.nstr(abs(serialized), digits)}


def _real_record(value: mp.mpf, digits: int) -> str:
    return mp.nstr(mp.mpf(value), digits)


def _mp_complex(value: Mapping[str, Any]) -> mp.mpc:
    if set(value) != {"real", "imag", "abs"}:
        raise HPUnitarityOracleError("Route-U complex record schema mismatch")
    result = mp.mpc(mp.mpf(value["real"]), mp.mpf(value["imag"]))
    magnitude = mp.mpf(value["abs"])
    if magnitude < 0 or abs(abs(result) - magnitude) > max(
        abs(result), magnitude, mp.mpf("1e-100000")
    ) * mp.mpf("1e-40"):
        raise HPUnitarityOracleError("Route-U complex record magnitude mismatch")
    return result


__all__ = [
    "ADJACENT_LOG_GAMMA_MAX",
    "ADJACENT_S_SYMMETRIC_RELATIVE_MAX",
    "HPUnitarityOracleError",
    "MINIMUM_GUARD_DIGITS",
    "OracleMode",
    "gamma_decimal_value",
    "independent_geometry",
    "precision_schedule",
    "solve_oracle_node",
    "validate_oracle_ladder",
]
