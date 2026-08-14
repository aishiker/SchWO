"""Independent arbitrary-precision selected-anchor radial repair campaign.

The numerical call graph in this module is deliberately isolated from the
project's NumPy/SciPy radial implementations.  It evaluates the Regge--Wheeler
and Zerilli potentials, outer Jost recurrence, and full-state RK4 propagation
directly with :mod:`mpmath`.  Immutable float64 campaign artifacts are read
only to select a deterministic diagnostic domain; none of their numerical
outputs enter the arbitrary-precision solve.
"""

from __future__ import annotations

import ast
from collections import Counter
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from decimal import Decimal, localcontext
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import socket
import stat
import sys
import time

import mpmath as mp


CAMPAIGN_INDEX_SHA256 = (
    "e26b53ecb7997808a52da4dae5420fa7c4ebf5e1e46df88519fa8903e1956de6"
)
CAMPAIGN_INDEX_SCHEMA = "schwgw_phase6_conditioning_campaign_index_v1"
CAMPAIGN_MANIFEST_SCHEMA = "schwgw_phase6_conditioning_campaign_manifest_v1"
KEY_CHECKPOINT_SCHEMA = "schwgw_phase6_v1_key_checkpoint_v1"
PLAN_SCHEMA = "schwgw_phase6_ap_radial_repair_plan_v1"
NODE_SCHEMA = "schwgw_phase6_ap_radial_repair_node_v1"
ANCHOR_RESULT_SCHEMA = "schwgw_phase6_ap_radial_repair_anchor_result_v1"
SUMMARY_SCHEMA = "schwgw_phase6_ap_radial_repair_summary_v1"
MANIFEST_SCHEMA = "schwgw_phase6_ap_radial_repair_manifest_v1"
CHECKPOINT_SCHEMA = "schwgw_phase6_ap_radial_repair_checkpoint_v1"

EXPECTED_FAILURE_COUNT = 5_798
TARGET_ANCHOR_COUNT = 24
FULL_PRECISION_DPS = (60, 80)
FULL_STEP_RSTAR = ("0.0016", "0.0008")
R_IN_EPS = "0.000001"
R_OUT_M = "300"
MATCH_RADIUS_M = "60"
JOST_ORDER = 160
SECTORS = ("odd", "even")
K_BANDS = (
    ("low", Decimal("0.3"), Decimal("1"), Decimal("0.65")),
    ("mid_low", Decimal("1.1"), Decimal("2"), Decimal("1.55")),
    ("mid_high", Decimal("2.1"), Decimal("3"), Decimal("2.55")),
    ("high", Decimal("3.1"), Decimal("8"), Decimal("5.5")),
)
SEVERITY_BANDS = (
    ("mild", Decimal("0"), Decimal("0.06"), Decimal("0.04"), Decimal("0.25")),
    (
        "moderate",
        Decimal("0.06"),
        Decimal("0.1"),
        Decimal("0.08"),
        Decimal("0.5"),
    ),
    (
        "severe",
        Decimal("0.1"),
        Decimal("Infinity"),
        Decimal("0.14"),
        Decimal("0.75"),
    ),
)
NUMERICAL_THRESHOLDS = {
    "arithmetic_precision_relative_delta": Decimal("1e-20"),
    "flux_fraction_residual": Decimal("1e-8"),
    "jost_tail_ratio": Decimal("1e-15"),
    "match_condition_estimate": Decimal("1e50"),
    "match_log_derivative_residual": Decimal("1e-20"),
    "step_size_relative_delta": Decimal("2e-6"),
}


class APRadialRepairError(ValueError):
    """Raised when the repair plan, solver, or evidence protocol drifts."""


class APRadialNumericalError(RuntimeError):
    """A fail-closed numerical terminal for one selected anchor."""


@dataclass(frozen=True)
class FailureKey:
    """One immutable fail-closed conditioning key eligible for repair."""

    kM: str
    sector: str
    ell: int
    shard_id: str
    shard_ordinal: int
    selected_r_out_M: str
    turning_severity: str
    checkpoint_identity: Mapping[str, object]
    run_contract_identity: Mapping[str, object]

    def key_record(self) -> dict[str, object]:
        return {"ell": self.ell, "kM": self.kM, "sector": self.sector}


@dataclass(frozen=True)
class RepairAnchor:
    """A deterministic stratum representative."""

    anchor_id: str
    source: FailureKey
    k_band: str
    severity_band: str
    stratum_candidate_count: int
    ell_quantile_target: str

    def to_record(self) -> dict[str, object]:
        return {
            "anchor_id": self.anchor_id,
            "checkpoint_identity": dict(self.source.checkpoint_identity),
            "ell_quantile_target": self.ell_quantile_target,
            "k_band": self.k_band,
            "key": self.source.key_record(),
            "run_contract_identity": dict(self.source.run_contract_identity),
            "selected_r_out_M": self.source.selected_r_out_M,
            "severity_band": self.severity_band,
            "shard_id": self.source.shard_id,
            "shard_ordinal": self.source.shard_ordinal,
            "stratum_candidate_count": self.stratum_candidate_count,
            "turning_severity": self.source.turning_severity,
        }


@dataclass(frozen=True)
class RepairSolveConfig:
    """Frozen ladder for the production selected-anchor campaign."""

    precision_dps: tuple[int, ...] = FULL_PRECISION_DPS
    step_rstar: tuple[str, ...] = FULL_STEP_RSTAR
    r_in_eps: str = R_IN_EPS
    r_out_M: str = R_OUT_M
    match_radius_M: str = MATCH_RADIUS_M
    jost_order: int = JOST_ORDER

    def __post_init__(self) -> None:
        if self.precision_dps != FULL_PRECISION_DPS:
            raise APRadialRepairError("repair precision ladder changed")
        if self.step_rstar != FULL_STEP_RSTAR:
            raise APRadialRepairError("repair step-size ladder changed")
        if (
            self.r_in_eps != R_IN_EPS
            or self.r_out_M != R_OUT_M
            or self.match_radius_M != MATCH_RADIUS_M
            or self.jost_order != JOST_ORDER
        ):
            raise APRadialRepairError("repair normalization/configuration changed")

    def to_record(self) -> dict[str, object]:
        return {
            "Fourier_convention": "exp(-i k t)",
            "even_sector_policy": "independent Zerilli solve; never parity-derived",
            "horizon_normalization": "unit exp(-i k r_star) at r=2(1+r_in_eps)",
            "jost_order": self.jost_order,
            "match_radius_M": self.match_radius_M,
            "outer_basis": "independent exp(+-i k r_star) sum(a_n/r^n)",
            "precision_dps": list(self.precision_dps),
            "r_in_eps": self.r_in_eps,
            "r_out_M": self.r_out_M,
            "step_rstar": list(self.step_rstar),
            "tortoise_origin": "r_star=r+2*log(r/2-1), M=1",
        }


def canonical_json_bytes(payload: object) -> bytes:
    """Serialize one finite canonical JSON value."""

    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _immutable_root(path: Path, *, label: str) -> Path:
    root = path.absolute()
    if root.is_symlink() or root.resolve(strict=True) != root:
        raise APRadialRepairError(f"{label} is aliased")
    info = root.lstat()
    if not stat.S_ISDIR(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o555:
        raise APRadialRepairError(f"{label} must be a direct 0555 directory")
    return root


def _canonical_immutable_json(
    path: Path, *, expected_sha256: str | None = None
) -> tuple[Mapping[str, object], dict[str, object]]:
    absolute = path.absolute()
    if absolute.is_symlink() or absolute.resolve(strict=True) != absolute:
        raise APRadialRepairError(f"immutable JSON is aliased: {absolute}")
    info = absolute.lstat()
    if (
        not stat.S_ISREG(info.st_mode)
        or stat.S_IMODE(info.st_mode) != 0o444
        or info.st_nlink != 1
    ):
        raise APRadialRepairError(f"immutable JSON mode/link changed: {absolute}")
    raw = absolute.read_bytes()
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise APRadialRepairError(f"invalid JSON: {absolute}") from exc
    if not isinstance(payload, Mapping) or raw != canonical_json_bytes(payload):
        raise APRadialRepairError(f"noncanonical JSON: {absolute}")
    digest = sha256_bytes(raw)
    if expected_sha256 is not None and digest != expected_sha256:
        raise APRadialRepairError(f"immutable JSON hash changed: {absolute}")
    return payload, {
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
        "path": str(absolute),
        "sha256": digest,
        "size": info.st_size,
    }


def _identity_matches(actual: Mapping[str, object], expected: object) -> bool:
    return isinstance(expected, Mapping) and dict(actual) == dict(expected)


def _checkpoint_filename(ordinal: int, key: Mapping[str, object]) -> str:
    km = str(key["kM"]).replace(".", "p")
    return (
        f"key_{ordinal:04d}__kM_{km}__{key['sector']}__"
        f"ell_{int(key['ell']):04d}__checkpoint.json"
    )


def _validate_key(key: object) -> tuple[str, str, int]:
    if not isinstance(key, Mapping) or set(key) != {"ell", "kM", "sector"}:
        raise APRadialRepairError("conditioning key schema changed")
    km, sector, ell = key["kM"], key["sector"], key["ell"]
    if (
        not isinstance(km, str)
        or not isinstance(sector, str)
        or sector not in SECTORS
        or isinstance(ell, bool)
        or not isinstance(ell, int)
        or ell < 2
    ):
        raise APRadialRepairError("conditioning key value changed")
    decimal = Decimal(km)
    if not decimal.is_finite() or decimal <= 0:
        raise APRadialRepairError("conditioning kM is invalid")
    return km, sector, ell


def _turning_severity(km: str, ell: int, r_out: object) -> str:
    with localcontext() as context:
        context.prec = 60
        value = Decimal(ell * (ell + 1)).sqrt() / Decimal(km) / Decimal(str(r_out))
        return format(value, ".50g")


def load_fail_closed_keys(
    campaign_root: str | Path,
) -> tuple[tuple[FailureKey, ...], Mapping[str, object]]:
    """Strictly reload the immutable 5,798-key failure inventory."""

    root = _immutable_root(Path(campaign_root), label="conditioning campaign root")
    index, index_identity = _canonical_immutable_json(
        root / "conditioning_campaign_index.json",
        expected_sha256=CAMPAIGN_INDEX_SHA256,
    )
    manifest, _ = _canonical_immutable_json(root / "manifest.json")
    if (
        index.get("schema") != CAMPAIGN_INDEX_SCHEMA
        or index.get("scientific_evidence") is not True
        or index.get("science_executed") is not True
        or index.get("global_green_permitted") is not False
        or index.get("failure_summary", {}).get("scientific_failure_key_count")
        != EXPECTED_FAILURE_COUNT
        or manifest.get("schema") != CAMPAIGN_MANIFEST_SCHEMA
        or manifest.get("campaign_index_identity") != index_identity
    ):
        raise APRadialRepairError("conditioning campaign identity/status changed")
    entries = index.get("shards")
    if not isinstance(entries, list) or len(entries) != 86:
        raise APRadialRepairError("conditioning shard inventory changed")

    failures: list[FailureKey] = []
    per_shard = Counter()
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise APRadialRepairError("conditioning shard entry changed")
        shard = entry.get("shard")
        identities = entry.get("identities")
        if not isinstance(shard, Mapping) or not isinstance(identities, Mapping):
            raise APRadialRepairError("conditioning shard provenance changed")
        shard_id = shard.get("shard_id")
        if not isinstance(shard_id, str):
            raise APRadialRepairError("conditioning shard ID changed")
        shard_root = _immutable_root(
            Path(str(entry.get("root"))), label=f"conditioning shard {shard_id}"
        )
        contract, contract_identity = _canonical_immutable_json(
            shard_root / "run_contract.json"
        )
        if not _identity_matches(
            contract_identity, identities.get("run_contract.json")
        ):
            raise APRadialRepairError("conditioning run-contract identity changed")
        keys, plans = contract.get("shard_keys"), contract.get("key_plans")
        if (
            not isinstance(keys, list)
            or not isinstance(plans, list)
            or len(keys) != len(plans)
            or len(keys) != shard.get("key_count")
        ):
            raise APRadialRepairError("conditioning key-plan inventory changed")
        for ordinal, (key, plan) in enumerate(zip(keys, plans, strict=True)):
            km, sector, ell = _validate_key(key)
            if (
                not isinstance(plan, Mapping)
                or plan.get("key") != key
                or plan.get("shard_ordinal") != ordinal
            ):
                raise APRadialRepairError("conditioning key plan changed")
            checkpoint, checkpoint_identity = _canonical_immutable_json(
                shard_root / _checkpoint_filename(ordinal, key)
            )
            state = checkpoint.get("acceptance_state")
            if (
                checkpoint.get("schema") != KEY_CHECKPOINT_SCHEMA
                or checkpoint.get("key") != key
                or checkpoint.get("global_green_permitted") is not False
                or state not in {"PARTIAL", "FAIL"}
            ):
                raise APRadialRepairError("conditioning checkpoint changed")
            if state != "FAIL":
                continue
            selection = plan.get("outer_selection")
            if not isinstance(selection, Mapping):
                raise APRadialRepairError("conditioning outer selection changed")
            r_out = selection.get("selected_r_out_M")
            if r_out != 300.0:
                raise APRadialRepairError("repair source failure r_out changed")
            failures.append(
                FailureKey(
                    kM=km,
                    sector=sector,
                    ell=ell,
                    shard_id=shard_id,
                    shard_ordinal=ordinal,
                    selected_r_out_M="300",
                    turning_severity=_turning_severity(km, ell, r_out),
                    checkpoint_identity=checkpoint_identity,
                    run_contract_identity=contract_identity,
                )
            )
            per_shard[shard_id] += 1
        if per_shard[shard_id] != entry.get("scientific_failure_key_count"):
            raise APRadialRepairError("per-shard failure count changed")
    ordered = tuple(
        sorted(
            failures,
            key=lambda item: (Decimal(item.kM), SECTORS.index(item.sector), item.ell),
        )
    )
    if (
        len(ordered) != EXPECTED_FAILURE_COUNT
        or len({(item.kM, item.sector, item.ell) for item in ordered})
        != EXPECTED_FAILURE_COUNT
    ):
        raise APRadialRepairError("fail-closed source domain changed")
    return ordered, index_identity


def _k_band(value: Decimal) -> tuple[str, Decimal]:
    for name, lower, upper, target in K_BANDS:
        if lower <= value <= upper:
            return name, target
    raise APRadialRepairError("failure kM lies outside repair bands")


def _severity_band(value: Decimal) -> tuple[str, Decimal, Decimal]:
    for name, lower, upper, target, ell_quantile in SEVERITY_BANDS:
        if lower <= value < upper:
            return name, target, ell_quantile
    raise APRadialRepairError("turning severity lies outside repair bands")


def _quantile(values: Sequence[int], fraction: Decimal) -> Decimal:
    ordered = sorted(values)
    if not ordered:
        raise APRadialRepairError("cannot select an empty stratum")
    position = fraction * Decimal(len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return Decimal(ordered[lower]) * (1 - weight) + Decimal(ordered[upper]) * weight


def select_repair_anchors(
    failures: Sequence[FailureKey], *, target_count: int = TARGET_ANCHOR_COUNT
) -> tuple[RepairAnchor, ...]:
    """Select one deterministic representative of each 4x2x3 stratum."""

    if target_count != TARGET_ANCHOR_COUNT:
        raise APRadialRepairError("production repair anchor count must be 24")
    groups: dict[tuple[str, str, str], list[FailureKey]] = {}
    for item in failures:
        k_name, _ = _k_band(Decimal(item.kM))
        severity_name, _, _ = _severity_band(Decimal(item.turning_severity))
        groups.setdefault((k_name, item.sector, severity_name), []).append(item)
    expected = {
        (k_name, sector, severity_name)
        for k_name, *_ in K_BANDS
        for sector in SECTORS
        for severity_name, *_ in SEVERITY_BANDS
    }
    if set(groups) != expected:
        raise APRadialRepairError("repair stratification lost a required cell")
    selected: list[tuple[tuple[str, str, str], FailureKey, int, Decimal]] = []
    for stratum in sorted(
        groups,
        key=lambda value: (
            [item[0] for item in K_BANDS].index(value[0]),
            SECTORS.index(value[1]),
            [item[0] for item in SEVERITY_BANDS].index(value[2]),
        ),
    ):
        candidates = groups[stratum]
        k_target = next(item[3] for item in K_BANDS if item[0] == stratum[0])
        _, severity_target, ell_fraction = next(
            (item[0], item[3], item[4])
            for item in SEVERITY_BANDS
            if item[0] == stratum[2]
        )
        ell_target = _quantile([item.ell for item in candidates], ell_fraction)
        chosen = min(
            candidates,
            key=lambda item: (
                abs(Decimal(item.turning_severity) - severity_target),
                abs(Decimal(item.kM) - k_target),
                abs(Decimal(item.ell) - ell_target),
                Decimal(item.kM),
                item.ell,
            ),
        )
        selected.append((stratum, chosen, len(candidates), ell_fraction))
    if len(selected) != target_count:
        raise APRadialRepairError("repair selection cardinality changed")
    result = []
    for ordinal, (stratum, source, count, fraction) in enumerate(selected):
        result.append(
            RepairAnchor(
                anchor_id=(
                    f"repair_{ordinal:02d}_k{source.kM.replace('.', 'p')}_"
                    f"{source.sector}_l{source.ell}"
                ),
                source=source,
                k_band=stratum[0],
                severity_band=stratum[2],
                stratum_candidate_count=count,
                ell_quantile_target=str(fraction),
            )
        )
    return tuple(result)


def benchmark_anchors(anchors: Sequence[RepairAnchor]) -> tuple[RepairAnchor, ...]:
    """Freeze one ordinary odd and one worst-severity even timing key."""

    low = next(
        item
        for item in anchors
        if item.k_band == "low"
        and item.source.sector == "odd"
        and item.severity_band == "moderate"
    )
    high = next(
        item
        for item in anchors
        if item.k_band == "high"
        and item.source.sector == "even"
        and item.severity_band == "severe"
    )
    return (low, high)


def schwarzschild_rstar(radius: mp.mpf) -> mp.mpf:
    radius = mp.mpf(radius)
    if radius <= 2:
        raise APRadialNumericalError("r_star requires r>2M")
    return radius + 2 * mp.log(radius / 2 - 1)


def radial_potential(sector: str, ell: int, radius: mp.mpf) -> mp.mpf:
    """Independent arbitrary-precision RW/Zerilli potential for M=1."""

    radius = mp.mpf(radius)
    if sector not in SECTORS or ell < 2 or radius <= 2:
        raise APRadialNumericalError("invalid potential input")
    lapse = 1 - 2 / radius
    if sector == "odd":
        return lapse * (ell * (ell + 1) / radius**2 - 6 / radius**3)
    lam = mp.mpf((ell - 1) * (ell + 2)) / 2
    numerator = (
        2 * lam**2 * (lam + 1) * radius**3
        + 6 * lam**2 * radius**2
        + 18 * lam * radius
        + 18
    )
    return lapse * numerator / (radius**3 * (lam * radius + 3) ** 2)


def _potential_series(sector: str, ell: int, order: int) -> list[mp.mpf]:
    values = [mp.mpf(0) for _ in range(order + 1)]
    angular = mp.mpf(ell * (ell + 1))
    if sector == "odd":
        values[2] = angular
        if order >= 3:
            values[3] = -2 * angular - 6
        if order >= 4:
            values[4] = 12
        return values
    lam = mp.mpf((ell - 1) * (ell + 2)) / 2
    bracket = [mp.mpf(0) for _ in range(order + 1)]
    bracket[0] = 2 * lam**2 * (lam + 1)
    if order >= 1:
        bracket[1] = 6 * lam**2
    if order >= 2:
        bracket[2] = 18 * lam
    if order >= 3:
        bracket[3] = 18
    inverse = [
        mp.mpf((-1) ** index) * (index + 1) * (3 / lam) ** index / lam**2
        for index in range(order + 1)
    ]
    quotient = [mp.mpf(0) for _ in range(order + 1)]
    for left, left_value in enumerate(bracket):
        for right, right_value in enumerate(inverse[: order + 1 - left]):
            quotient[left + right] += left_value * right_value
    for index in range(order - 1):
        values[index + 2] += quotient[index]
        if index + 3 <= order:
            values[index + 3] -= 2 * quotient[index]
    return values


def independent_jost_basis(
    *, sector: str, ell: int, k: mp.mpf, radius: mp.mpf, sign: int, order: int
) -> tuple[mp.mpc, mp.mpc, int, mp.mpf]:
    """Evaluate an independently generated local 1/r Jost basis."""

    if sign not in {-1, 1} or not 2 <= order <= 256:
        raise APRadialNumericalError("invalid Jost request")
    potential = _potential_series(sector, ell, order + 2)
    f_squared = (mp.mpf(1), mp.mpf(-4), mp.mpf(4))
    derivative = (2 * mp.j * sign * k, -4 * mp.j * sign * k, mp.mpf(2), mp.mpf(-4))
    terms: list[mp.mpc] = [mp.mpc(1)]
    decreasing = increasing = 0
    optimal: int | None = None
    threshold = mp.power(10, -min(50, max(20, mp.mp.dps // 2)))
    for index in range(1, order + 1):
        power, known = index + 1, mp.mpc(0)
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
        for offset, coefficient in enumerate(derivative):
            source = power - offset - 1
            if 0 <= source < index:
                known += (
                    coefficient * (-source) * terms[source] * radius ** (source - index)
                )
        for offset in range(2, min(power, len(potential) - 1) + 1):
            source = power - offset
            if 0 <= source < index:
                known -= potential[offset] * terms[source] * radius ** (source - index)
        terms.append(-known / (-2 * mp.j * sign * k * index))
        if abs(terms[-1]) < abs(terms[-2]):
            decreasing += 1
            increasing, optimal = 0, None
        else:
            if increasing == 0 and decreasing >= 8:
                optimal = index - 1
            increasing += 1
            decreasing = 0
        if increasing >= 4 and optimal is not None:
            terms = terms[: optimal + 1]
            break
        if index >= 16 and max(abs(value) for value in terms[-4:]) < threshold:
            break
    series = mp.fsum(terms)
    derivative_r = -mp.fsum(index * value for index, value in enumerate(terms)) / radius
    phase = mp.exp(sign * mp.j * k * schwarzschild_rstar(radius))
    lapse = 1 - 2 / radius
    value = phase * series
    momentum = phase * (sign * mp.j * k * series + lapse * derivative_r)
    width = min(4, len(terms) - 1)
    tail = mp.fsum(abs(value) for value in terms[-width:]) / max(abs(series), mp.eps)
    return value, momentum, len(terms) - 1, tail


def _rhs(
    sector: str, ell: int, k: mp.mpf, state: Sequence[mp.mpf | mp.mpc]
) -> tuple[mp.mpf | mp.mpc, ...]:
    radius = mp.mpf(state[0])
    lapse = 1 - 2 / radius
    factor = radial_potential(sector, ell, radius) - k**2
    result: list[mp.mpf | mp.mpc] = [lapse]
    for index in range(1, len(state), 2):
        result.extend((mp.mpc(state[index + 1]), factor * mp.mpc(state[index])))
    return tuple(result)


def _rk4_step(
    sector: str,
    ell: int,
    k: mp.mpf,
    state: Sequence[mp.mpf | mp.mpc],
    step: mp.mpf,
) -> list[mp.mpf | mp.mpc]:
    one = _rhs(sector, ell, k, state)
    two_state = [value + step * slope / 2 for value, slope in zip(state, one)]
    two = _rhs(sector, ell, k, two_state)
    three_state = [value + step * slope / 2 for value, slope in zip(state, two)]
    three = _rhs(sector, ell, k, three_state)
    four_state = [value + step * slope for value, slope in zip(state, three)]
    four = _rhs(sector, ell, k, four_state)
    return [
        value + step * (a + 2 * b + 2 * c + d) / 6
        for value, a, b, c, d in zip(state, one, two, three, four)
    ]


def _current(state: Sequence[mp.mpf | mp.mpc], pair: int = 0) -> mp.mpf:
    offset = 1 + 2 * pair
    return mp.im(mp.conj(mp.mpc(state[offset])) * mp.mpc(state[offset + 1]))


def _integrate(
    *,
    sector: str,
    ell: int,
    k: mp.mpf,
    state: Sequence[mp.mpf | mp.mpc],
    target_radius: mp.mpf,
    maximum_step: mp.mpf,
) -> tuple[list[mp.mpf | mp.mpc], int, mp.mpf]:
    current = list(state)
    x = schwarzschild_rstar(mp.mpf(current[0]))
    target = schwarzschild_rstar(target_radius)
    direction = 1 if target > x else -1
    initial_current = _current(current)
    scale = max(abs(initial_current), mp.eps)
    drift, steps = mp.mpf(0), 0
    while (x < target) if direction > 0 else (x > target):
        step = min(maximum_step, abs(target - x)) * direction
        current = _rk4_step(sector, ell, k, current, step)
        x += step
        steps += 1
        drift = max(drift, abs(_current(current) - initial_current) / scale)
    current[0] = target_radius
    return current, steps, drift


def _complex_record(value: mp.mpc, digits: int) -> dict[str, str]:
    real, imag = mp.nstr(mp.re(value), digits), mp.nstr(mp.im(value), digits)
    serialized = mp.mpc(mp.mpf(real), mp.mpf(imag))
    return {"abs": mp.nstr(abs(serialized), digits), "imag": imag, "real": real}


def _relative_complex(
    left: Mapping[str, object], right: Mapping[str, object]
) -> mp.mpf:
    with mp.workdps(120):
        a = mp.mpc(mp.mpf(str(left["real"])), mp.mpf(str(left["imag"])))
        b = mp.mpc(mp.mpf(str(right["real"])), mp.mpf(str(right["imag"])))
        return +abs(a - b) / max(abs(a), abs(b), mp.mpf(1))


def solve_anchor_node(
    anchor: RepairAnchor, *, precision_dps: int, maximum_step_rstar: str
) -> dict[str, object]:
    """Solve one full-state RW/Zerilli node using only mpmath arithmetic."""

    started = time.monotonic()
    with mp.workdps(precision_dps):
        k = mp.mpf(anchor.source.kM)
        r_in = 2 * (1 + mp.mpf(R_IN_EPS))
        r_out, match = mp.mpf(R_OUT_M), mp.mpf(MATCH_RADIUS_M)
        step = mp.mpf(maximum_step_rstar)
        inner_phase = mp.exp(-mp.j * k * schwarzschild_rstar(r_in))
        horizon, horizon_steps, current_drift = _integrate(
            sector=anchor.source.sector,
            ell=anchor.source.ell,
            k=k,
            state=[r_in, inner_phase, -mp.j * k * inner_phase],
            target_radius=match,
            maximum_step=step,
        )
        incoming, incoming_p, incoming_order, incoming_tail = independent_jost_basis(
            sector=anchor.source.sector,
            ell=anchor.source.ell,
            k=k,
            radius=r_out,
            sign=-1,
            order=JOST_ORDER,
        )
        outgoing, outgoing_p, outgoing_order, outgoing_tail = independent_jost_basis(
            sector=anchor.source.sector,
            ell=anchor.source.ell,
            k=k,
            radius=r_out,
            sign=1,
            order=JOST_ORDER,
        )
        outer, outer_steps, _ = _integrate(
            sector=anchor.source.sector,
            ell=anchor.source.ell,
            k=k,
            state=[r_out, incoming, incoming_p, outgoing, outgoing_p],
            target_radius=match,
            maximum_step=step,
        )
        h, hp = mp.mpc(horizon[1]), mp.mpc(horizon[2])
        if h == 0:
            raise APRadialNumericalError("horizon state vanished at match radius")
        log_h = hp / h
        ji, jip, jo, jop = map(mp.mpc, outer[1:5])
        denominator = jop - log_h * jo
        if denominator == 0:
            raise APRadialNumericalError("singular bidirectional match")
        reflection = (log_h * ji - jip) / denominator
        physical, physical_p = ji + reflection * jo, jip + reflection * jop
        if physical == 0:
            raise APRadialNumericalError("matched physical state vanished")
        transmission = physical / h
        log_residual = abs(physical_p / physical - log_h)
        scattering = -reflection / ((-1) ** anchor.source.ell)
        reflection_fraction = abs(reflection) ** 2
        transmission_fraction = abs(transmission) ** 2
        flux_residual = abs(reflection_fraction + transmission_fraction - 1)
        condition = max(abs(ji), abs(jo), abs(log_h)) / max(abs(denominator), mp.eps)
        conjugacy = max(
            abs(outgoing - mp.conj(incoming))
            / max(abs(outgoing), abs(incoming), mp.eps),
            abs(outgoing_p - mp.conj(incoming_p))
            / max(abs(outgoing_p), abs(incoming_p), mp.eps),
        )
        digits = min(precision_dps, 70)
        return {
            "anchor_id": anchor.anchor_id,
            "backend": {
                "actual_decimal_digits": mp.mp.dps,
                "actual_precision_bits": mp.mp.prec,
                "arithmetic": f"mpmath {mp.__version__}",
                "even_independent_solve": anchor.source.sector == "even",
                "numpy_used": False,
                "parity_derived_even_used": False,
                "scipy_used": False,
            },
            "configuration": {
                "Fourier_convention": "exp(-i k t)",
                "horizon_normalization": "unit exp(-i k r_star)",
                "jost_order": JOST_ORDER,
                "match_radius_M": MATCH_RADIUS_M,
                "maximum_step_rstar": maximum_step_rstar,
                "precision_dps": precision_dps,
                "r_in_eps": R_IN_EPS,
                "r_out_M": R_OUT_M,
                "tortoise_origin": "r_star=r+2*log(r/2-1), M=1",
            },
            "diagnostics": {
                "flux_fraction_residual": mp.nstr(flux_residual, digits),
                "horizon_current_maximum_relative_drift": mp.nstr(
                    current_drift, digits
                ),
                "jost_conjugacy_residual": mp.nstr(conjugacy, digits),
                "jost_tail_ratio": mp.nstr(max(incoming_tail, outgoing_tail), digits),
                "match_condition_estimate": mp.nstr(condition, digits),
                "match_log_derivative_residual": mp.nstr(log_residual, digits),
            },
            "elapsed_seconds": time.monotonic() - started,
            "integration_steps": horizon_steps + outer_steps,
            "jost_effective_orders": {
                "incoming": incoming_order,
                "outgoing": outgoing_order,
            },
            "key": anchor.source.key_record(),
            "reflection_amplitude": _complex_record(reflection, digits),
            "reflection_fraction": mp.nstr(reflection_fraction, digits),
            "schema": NODE_SCHEMA,
            "scattering_S": _complex_record(scattering, digits),
            "status": "COMPLETED",
            "transmission_amplitude": _complex_record(transmission, digits),
            "transmission_fraction": mp.nstr(transmission_fraction, digits),
        }


def _budget_record(
    estimate: mp.mpf, threshold: Decimal, *, comparison: str, units: str
) -> dict[str, object]:
    passed = estimate <= mp.mpf(str(threshold))
    return {
        "comparison": comparison,
        "estimate": mp.nstr(estimate, 50),
        "state": "PASS" if passed else "FAIL",
        "threshold": str(threshold),
        "units": units,
    }


def solve_anchor_ladder(anchor: RepairAnchor) -> dict[str, object]:
    """Run the frozen 2x2 precision/step ladder and derive its closure state."""

    started = time.monotonic()
    nodes: list[dict[str, object]] = []
    try:
        for dps in FULL_PRECISION_DPS:
            for step in FULL_STEP_RSTAR:
                nodes.append(
                    solve_anchor_node(
                        anchor, precision_dps=dps, maximum_step_rstar=step
                    )
                )
    except APRadialNumericalError as exc:
        return {
            "anchor": anchor.to_record(),
            "convention_uncertainty_budget": _convention_budget(),
            "elapsed_seconds": time.monotonic() - started,
            "failure": f"{type(exc).__name__}: {exc}",
            "global_green_permitted": False,
            "ladder_closed": False,
            "nodes": nodes,
            "numerical_uncertainty_budget": {
                "overall_state": "FAIL",
                "reason": "arbitrary-precision node failed closed",
            },
            "schema": ANCHOR_RESULT_SCHEMA,
            "scientific_acceptance": False,
            "status": "FAIL_CLOSED",
        }
    by_node = {
        (
            int(node["configuration"]["precision_dps"]),
            str(node["configuration"]["maximum_step_rstar"]),
        ): node
        for node in nodes
    }
    coarse_step, fine_step = FULL_STEP_RSTAR
    baseline = by_node[(80, fine_step)]
    with mp.workdps(120):
        step_delta = _relative_complex(
            baseline["scattering_S"], by_node[(80, coarse_step)]["scattering_S"]
        )
        precision_delta = _relative_complex(
            baseline["scattering_S"], by_node[(60, fine_step)]["scattering_S"]
        )
        diagnostics = baseline["diagnostics"]
        numerical = {
            "arithmetic_precision": _budget_record(
                precision_delta,
                NUMERICAL_THRESHOLDS["arithmetic_precision_relative_delta"],
                comparison=f"60 versus 80 dps at fixed step {fine_step}",
                units="relative_complex_S",
            ),
            "flux_balance": _budget_record(
                mp.mpf(str(diagnostics["flux_fraction_residual"])),
                NUMERICAL_THRESHOLDS["flux_fraction_residual"],
                comparison=f"|R|^2+|T|^2-1 at 80 dps / step {fine_step}",
                units="dimensionless",
            ),
            "jost_tail": _budget_record(
                mp.mpf(str(diagnostics["jost_tail_ratio"])),
                NUMERICAL_THRESHOLDS["jost_tail_ratio"],
                comparison="maximum incoming/outgoing local Jost tail ratio",
                units="dimensionless",
            ),
            "match_condition": _budget_record(
                mp.mpf(str(diagnostics["match_condition_estimate"])),
                NUMERICAL_THRESHOLDS["match_condition_estimate"],
                comparison="bidirectional match condition estimate",
                units="dimensionless",
            ),
            "match_residual": _budget_record(
                mp.mpf(str(diagnostics["match_log_derivative_residual"])),
                NUMERICAL_THRESHOLDS["match_log_derivative_residual"],
                comparison="matched logarithmic derivative residual",
                units="inverse_M",
            ),
            "step_size": _budget_record(
                step_delta,
                NUMERICAL_THRESHOLDS["step_size_relative_delta"],
                comparison=f"RK4 step {coarse_step} versus {fine_step} at 80 dps",
                units="relative_complex_S",
            ),
        }
    ladder_closed = all(item["state"] == "PASS" for item in numerical.values())
    numerical["overall_state"] = "PASS" if ladder_closed else "FAIL"
    return {
        "anchor": anchor.to_record(),
        "baseline": baseline,
        "convention_uncertainty_budget": _convention_budget(),
        "elapsed_seconds": time.monotonic() - started,
        "failure": None,
        "global_green_permitted": False,
        "ladder_closed": ladder_closed,
        "nodes": nodes,
        "numerical_uncertainty_budget": numerical,
        "schema": ANCHOR_RESULT_SCHEMA,
        "scientific_acceptance": ladder_closed,
        "status": "LADDER_CLOSED" if ladder_closed else "FAIL_CLOSED_LADDER",
    }


def _convention_budget() -> dict[str, object]:
    return {
        "even_sector": {
            "state": "FROZEN",
            "value": "independent Zerilli radial solve; no parity derivation",
        },
        "fourier_sign": {"state": "FROZEN", "value": "exp(-i k t)"},
        "horizon_normalization": {
            "state": "FROZEN",
            "value": "unit exp(-i k r_star) at r=2(1+1e-6)",
        },
        "overall_state": "FROZEN_NOT_EXTERNALLY_CROSSCHECKED",
        "phase_origin": {
            "state": "FROZEN",
            "value": "r_star=r+2*log(r/2-1), M=1",
        },
        "scattering_definition": {
            "state": "FROZEN",
            "value": "S=-A_out/[(-1)^ell A_in]",
        },
    }


def file_identity(path: Path) -> dict[str, object]:
    info = path.lstat()
    return {
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
        "path": str(path.absolute()),
        "sha256": sha256_file(path),
        "size": info.st_size,
    }


def prove_call_graph_isolation(paths: Sequence[Path]) -> dict[str, object]:
    """Reject NumPy/SciPy and project float-backend imports/calls."""

    forbidden_imports = {"numpy", "scipy"}
    forbidden_modules = {
        "phase6_mpmath_radial",
        "schwgw.validation.phase6_mpmath_radial",
    }
    forbidden_fragments = {"schwgw.numerics", "conditioned_radial", "radial_solver"}
    forbidden_calls = {
        "__import__",
        "import_module",
        "lstsq",
        "pinv",
        "solve_ivp",
        "solve_radial_mode",
    }
    records = []
    for raw_path in paths:
        path = raw_path.resolve(strict=True)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports: list[str] = []
        calls: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.append(node.func.attr)
        if any(name.split(".")[0] in forbidden_imports for name in imports):
            raise APRadialRepairError("repair call graph imports NumPy/SciPy")
        if forbidden_modules & set(imports) or any(
            fragment in name for fragment in forbidden_fragments for name in imports
        ):
            raise APRadialRepairError("repair call graph imports a prohibited backend")
        if forbidden_calls & set(calls):
            raise APRadialRepairError("repair call graph invokes a prohibited solver")
        records.append(
            {
                "calls_sha256": sha256_bytes(canonical_json_bytes(sorted(calls))),
                "imports": sorted(imports),
                "path": str(path),
                "sha256": sha256_file(path),
            }
        )
    return {
        "isolated": True,
        "numpy_used": False,
        "paths": records,
        "scipy_used": False,
    }


def verify_mpmath_runtime(project_root: Path) -> dict[str, object]:
    overlay = (
        project_root / "runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314"
    ).resolve(strict=True)
    origin = Path(mp.__file__).resolve(strict=True)
    if mp.__version__ != "1.4.1" or overlay not in origin.parents:
        raise APRadialRepairError("repair requires the frozen mpmath 1.4.1 overlay")
    expected_pythonpath = os.pathsep.join((str(overlay), str(project_root / "src")))
    if os.environ.get("PYTHONDONTWRITEBYTECODE") != "1":
        raise APRadialRepairError("repair requires PYTHONDONTWRITEBYTECODE=1")
    if os.environ.get("PYTHONPATH") != expected_pythonpath:
        raise APRadialRepairError("repair requires exact overlay-first PYTHONPATH")
    if Path.cwd().resolve(strict=True) != project_root.resolve(strict=True):
        raise APRadialRepairError("repair runner must execute from the project root")
    return {
        "import_origin": file_identity(origin),
        "python_executable": file_identity(Path(sys.executable).resolve(strict=True)),
        "pythonpath": expected_pythonpath,
        "version": mp.__version__,
    }


def build_repair_plan(
    *,
    run_id: str,
    campaign_root: str | Path,
    implementation_paths: Sequence[Path],
    campaign_kind: str,
) -> dict[str, object]:
    if campaign_kind not in {"FULL_SELECTED_REPAIR", "TWO_ANCHOR_TIMING_BENCHMARK"}:
        raise APRadialRepairError("repair campaign kind changed")
    failures, source_identity = load_fail_closed_keys(campaign_root)
    full = select_repair_anchors(failures)
    selected = benchmark_anchors(full) if campaign_kind.startswith("TWO_") else full
    project_root = Path(__file__).resolve().parents[3]
    plan = {
        "anchors": [item.to_record() for item in selected],
        "campaign_kind": campaign_kind,
        "conditioning_campaign_index_identity": dict(source_identity),
        "convention_uncertainty_budget": _convention_budget(),
        "failure_source_count": len(failures),
        "full_selection_anchor_count": len(full),
        "global_green_permitted": False,
        "implementation_isolation": prove_call_graph_isolation(implementation_paths),
        "li_figure_agreement_primary_gate": False,
        "normalization_frozen": True,
        "numerical_thresholds": {
            key: str(value) for key, value in sorted(NUMERICAL_THRESHOLDS.items())
        },
        "paper_figure_runs": 0,
        "planned_anchor_count": len(selected),
        "run_id": run_id,
        "runtime": verify_mpmath_runtime(project_root),
        "schema": PLAN_SCHEMA,
        "scientific_acceptance": False,
        "selection_policy": (
            "one deterministic representative per 4 kM bands x 2 sectors x 3 "
            "turning-severity bands; ell quantile target frozen per severity"
        ),
        "solve_config": RepairSolveConfig().to_record(),
    }
    return plan


def _publish_exclusive(path: Path, payload: object) -> dict[str, object]:
    if path.exists() or path.is_symlink():
        raise APRadialRepairError(f"exclusive output collision: {path}")
    raw = canonical_json_bytes(payload)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    with os.fdopen(descriptor, "wb", closefd=True) as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    os.chmod(path, 0o444)
    _fsync_directory(path.parent)
    return file_identity(path)


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


@contextmanager
def _writer_lock(root: Path) -> Iterator[None]:
    lock_path = root / ".writer.lock"
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(lock_path, flags, 0o600)
    handle = os.fdopen(descriptor, "r+b", closefd=True)
    try:
        info = os.fstat(handle.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise APRadialRepairError("repair writer lock is not a direct file")
        os.fchmod(handle.fileno(), 0o600)
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise APRadialRepairError(
                "repair root already has an active writer"
            ) from exc
        handle.seek(0)
        handle.truncate()
        handle.write(
            canonical_json_bytes(
                {
                    "hostname": socket.gethostname(),
                    "pid": os.getpid(),
                    "schema": "schwgw_phase6_single_writer_lock_v1",
                }
            )
        )
        handle.flush()
        os.fsync(handle.fileno())
        yield
    finally:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def _result_filename(ordinal: int, anchor_id: str) -> str:
    return f"anchor_{ordinal:02d}__{anchor_id}.json"


def _load_direct_canonical(path: Path) -> Mapping[str, object]:
    absolute = path.absolute()
    if absolute.is_symlink() or absolute.resolve(strict=True) != absolute:
        raise APRadialRepairError(f"repair artifact is aliased: {absolute}")
    info = absolute.lstat()
    if (
        not stat.S_ISREG(info.st_mode)
        or stat.S_IMODE(info.st_mode) != 0o444
        or info.st_nlink != 1
    ):
        raise APRadialRepairError(f"repair artifact mode/link changed: {absolute}")
    raw = path.read_bytes()
    payload = json.loads(raw)
    if not isinstance(payload, Mapping) or raw != canonical_json_bytes(payload):
        raise APRadialRepairError(f"repair artifact is not canonical: {path}")
    return payload


def _publish_or_validate(path: Path, payload: object) -> dict[str, object]:
    if path.exists() or path.is_symlink():
        stored = _load_direct_canonical(path)
        if canonical_json_bytes(stored) != canonical_json_bytes(payload):
            raise APRadialRepairError(f"resumed artifact content changed: {path}")
        return file_identity(path)
    return _publish_exclusive(path, payload)


def _validate_anchor_result(result: Mapping[str, object], anchor: RepairAnchor) -> None:
    if (
        result.get("schema") != ANCHOR_RESULT_SCHEMA
        or result.get("anchor") != anchor.to_record()
        or result.get("global_green_permitted") is not False
        or not isinstance(result.get("ladder_closed"), bool)
        or result.get("scientific_acceptance") != result.get("ladder_closed")
        or not isinstance(result.get("elapsed_seconds"), (int, float))
        or isinstance(result.get("elapsed_seconds"), bool)
        or not math.isfinite(float(result["elapsed_seconds"]))
        or float(result["elapsed_seconds"]) < 0
        or not isinstance(result.get("numerical_uncertainty_budget"), Mapping)
        or not isinstance(result.get("convention_uncertainty_budget"), Mapping)
    ):
        raise APRadialRepairError("anchor solver result schema changed")


def _anchor_from_record(record: Mapping[str, object]) -> RepairAnchor:
    key = record["key"]
    km, sector, ell = _validate_key(key)
    source = FailureKey(
        kM=km,
        sector=sector,
        ell=ell,
        shard_id=str(record["shard_id"]),
        shard_ordinal=int(record["shard_ordinal"]),
        selected_r_out_M=str(record["selected_r_out_M"]),
        turning_severity=str(record["turning_severity"]),
        checkpoint_identity=record["checkpoint_identity"],
        run_contract_identity=record["run_contract_identity"],
    )
    return RepairAnchor(
        anchor_id=str(record["anchor_id"]),
        source=source,
        k_band=str(record["k_band"]),
        severity_band=str(record["severity_band"]),
        stratum_candidate_count=int(record["stratum_candidate_count"]),
        ell_quantile_target=str(record["ell_quantile_target"]),
    )


def _summary(
    plan: Mapping[str, object], results: Sequence[Mapping[str, object]]
) -> dict[str, object]:
    states = Counter(str(item["status"]) for item in results)
    elapsed = sum(float(item["elapsed_seconds"]) for item in results)
    full_projection = elapsed / max(len(results), 1) * TARGET_ANCHOR_COUNT
    all_closed = bool(results) and all(
        item["ladder_closed"] is True for item in results
    )
    scientific_acceptance = (
        plan["campaign_kind"] == "FULL_SELECTED_REPAIR"
        and len(results) == TARGET_ANCHOR_COUNT
        and all_closed
    )
    return {
        "anchor_state_counts": dict(sorted(states.items())),
        "campaign_kind": plan["campaign_kind"],
        "completed_anchor_count": len(results),
        "convention_uncertainty_budget": _convention_budget(),
        "elapsed_anchor_seconds": elapsed,
        "full_24_anchor_projected_seconds": full_projection,
        "global_green_permitted": False,
        "ladder_closed_anchor_count": sum(
            item["ladder_closed"] is True for item in results
        ),
        "numerical_and_convention_budgets_separate": True,
        "planned_anchor_count": plan["planned_anchor_count"],
        "projected_under_10h": full_projection < 36_000,
        "run_id": plan["run_id"],
        "schema": SUMMARY_SCHEMA,
        "scientific_acceptance": scientific_acceptance,
        "status": (
            "SELECTED_ANCHOR_LADDERS_CLOSED"
            if scientific_acceptance
            else (
                "TIMING_BENCHMARK_COMPLETE_NO_SCIENTIFIC_ACCEPTANCE"
                if plan["campaign_kind"] == "TWO_ANCHOR_TIMING_BENCHMARK"
                else "FULL_SELECTED_REPAIR_FAIL_CLOSED"
            )
        ),
    }


def run_repair_campaign(
    *,
    output_root: str | Path,
    plan: Mapping[str, object],
    resume: bool = False,
    solver: Callable[[RepairAnchor], Mapping[str, object]] = solve_anchor_ladder,
) -> dict[str, object]:
    """Run/resume an append-only, single-writer selected-anchor campaign."""

    if (
        plan.get("schema") != PLAN_SCHEMA
        or plan.get("campaign_kind")
        not in {"FULL_SELECTED_REPAIR", "TWO_ANCHOR_TIMING_BENCHMARK"}
        or plan.get("global_green_permitted") is not False
        or plan.get("scientific_acceptance") is not False
        or plan.get("li_figure_agreement_primary_gate") is not False
    ):
        raise APRadialRepairError("repair plan policy/schema changed")
    root = Path(output_root).absolute()
    plan_raw = canonical_json_bytes(plan)
    plan_sha = sha256_bytes(plan_raw)
    if root.exists():
        if (
            not resume
            or root.is_symlink()
            or stat.S_IMODE(root.lstat().st_mode) != 0o700
        ):
            raise APRadialRepairError(
                "existing repair root requires --resume and mode 0700"
            )
        if (
            canonical_json_bytes(_load_direct_canonical(root / "campaign_plan.json"))
            != plan_raw
        ):
            raise APRadialRepairError("resume plan differs from frozen campaign plan")
    else:
        if resume:
            raise APRadialRepairError("--resume requires an existing partial root")
        root.mkdir(parents=True, mode=0o700)
        os.chmod(root, 0o700)
        _publish_exclusive(root / "campaign_plan.json", plan)
    anchors_raw = plan.get("anchors")
    if not isinstance(anchors_raw, list) or len(anchors_raw) != plan.get(
        "planned_anchor_count"
    ):
        raise APRadialRepairError("repair plan anchor inventory changed")
    anchors = tuple(_anchor_from_record(item) for item in anchors_raw)
    with _writer_lock(root):
        results: list[Mapping[str, object]] = []
        for ordinal, anchor in enumerate(anchors):
            result_path = root / _result_filename(ordinal, anchor.anchor_id)
            if result_path.exists():
                result = _load_direct_canonical(result_path)
            else:
                result = dict(solver(anchor))
                _validate_anchor_result(result, anchor)
                _publish_exclusive(result_path, result)
            _validate_anchor_result(result, anchor)
            results.append(result)
            checkpoint_path = root / f"checkpoint_{ordinal:02d}.json"
            _publish_or_validate(
                checkpoint_path,
                {
                    "anchor_id": anchor.anchor_id,
                    "completed_anchor_count": ordinal + 1,
                    "global_green_permitted": False,
                    "plan_sha256": plan_sha,
                    "result_identity": file_identity(result_path),
                    "schema": CHECKPOINT_SCHEMA,
                },
            )
        summary = _summary(plan, results)
        summary_identity = _publish_or_validate(root / "summary.json", summary)
        inventory = {
            child.name: file_identity(child)
            for child in sorted(root.iterdir(), key=lambda item: item.name)
            if child.name not in {".writer.lock", "manifest.json"}
        }
        _publish_or_validate(
            root / "manifest.json",
            {
                "files": inventory,
                "global_green_permitted": False,
                "plan_sha256": plan_sha,
                "schema": MANIFEST_SCHEMA,
                "status": summary["status"],
                "summary_identity": summary_identity,
            },
        )
        os.unlink(root / ".writer.lock")
        for child in root.iterdir():
            os.chmod(child, 0o444)
        os.chmod(root, 0o555)
        _fsync_directory(root)
        _fsync_directory(root.parent)
    return dict(summary)


__all__ = [
    "ANCHOR_RESULT_SCHEMA",
    "APRadialNumericalError",
    "APRadialRepairError",
    "FailureKey",
    "RepairAnchor",
    "RepairSolveConfig",
    "benchmark_anchors",
    "build_repair_plan",
    "canonical_json_bytes",
    "independent_jost_basis",
    "load_fail_closed_keys",
    "prove_call_graph_isolation",
    "radial_potential",
    "run_repair_campaign",
    "select_repair_anchors",
    "solve_anchor_ladder",
    "solve_anchor_node",
]
