"""Auditable planning and execution primitives for the Phase-6 conditioning scan.

The module binds the immutable Phase-6 domain/execution contracts, selects a
finite outer boundary from a frozen paper-independent conditioning policy, and
executes one generic float64 baseline per supported key.  Only the 158 frozen
transition keys receive additional ``r_in``/``r_out``/Jost/tolerance ladders.

Nothing in this module promotes a single-backend result to physical acceptance.
Numerical and convention budgets remain separate, Li-figure agreement is not an
input, and unsupported configurations fail closed before a radial solve.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Protocol

import numpy as np

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.numerics.conditioned_radial import (
    ConditionedRadialRequest,
    ConditionedRadialResult,
    solve_conditioned_radial_at_radius,
)
from schwgw.numerics.matching import outer_asymptotic_basis
from schwgw.perturbations import Sector, V_RW, V_Zerilli
from schwgw.validation.phase6_domain import (
    RadialKey,
    canonical_json_bytes,
    jsonl_bytes,
    read_jsonl_keys,
    sha256_bytes,
    source_file_identity,
    validate_ordered_unique_keys,
)
from schwgw.validation.phase6_execution_contract import (
    CHECKPOINT_SCHEMA,
    CONVENTION_BUDGET_FIELDS,
    KEY_PAYLOAD_ENVELOPE_SCHEMA,
    KEY_RESULT_SCHEMA,
    NUMERICAL_BUDGET_FIELDS,
)


SCAN_POLICY_SCHEMA = "schwgw_phase6_conditioning_scan_policy_v1"
SOLVER_PAYLOAD_SCHEMA = "schwgw_phase6_conditioning_solver_payload_v1"
RUN_CONTRACT_SCHEMA = "schwgw_phase6_conditioning_shard_run_contract_v1"
KEY_TERMINAL_SCHEMA = "schwgw_phase6_conditioning_key_terminal_v1"
SHARD_FAILURE_SCHEMA = "schwgw_phase6_conditioning_shard_failure_v1"

EXPECTED_DOMAIN_IDENTITIES = {
    "D_union.jsonl": "a5793564dfc28e815699966208ae6605eeeedce9e3629f09512b70e08196810b",
    "domain_contract.json": "7ed99b905c3a1301d96101f357ab1fd9f4bc6e9a4922cb242d28e7cf06bb3bcf",
    "manifest.json": "f11d127e0bcfafa8f2fe24b2d3cec3e0cedc60f644d4285e6d52e53d8358d2d2",
}
EXPECTED_EXECUTION_IDENTITIES = {
    "D_transition_calibration.jsonl": (
        "942fce669ee62f8194859f0481f7f3e926f4771176ec627d9013cda610dcb951"
    ),
    "shard_inventory.jsonl": (
        "b652ceb41d0dfa3c25f10d246e98bc707721faf4d83b049b3410dc4ca0b4efff"
    ),
    "execution_contract.json": (
        "25ad4b4e723edbd44651edaa63df415141de504b85288b12c2a6a973fcb420ab"
    ),
    "manifest.json": "1de9d445d888cbb5ddbf426cc062d2fb5128cad111437ce7d147df6e004aed48",
}

UNASSESSED_FINITE_BUDGET = float(np.finfo(float).max)


class ConditioningScanError(ValueError):
    """Raised when a scan policy, frozen input, or solver result fails closed."""


class ConditionedSolver(Protocol):
    def __call__(
        self,
        request: ConditionedRadialRequest,
        background: SchwarzschildBackground,
    ) -> ConditionedRadialResult: ...


@dataclass(frozen=True)
class ConditioningPolicy:
    """Frozen, generic selection and calibration policy for the V1 scan."""

    required_radius_M: float = 40.0
    r_out_candidates_M: tuple[float, ...] = (
        300.0,
        600.0,
        1200.0,
        2400.0,
        4800.0,
        9600.0,
        19200.0,
    )
    minimum_turning_proxy_margin: float = 1.35
    maximum_outer_potential_ratio: float = 0.55
    minimum_k_r_out: float = 25.0
    maximum_scaled_jost_condition: float = 1.0e8
    minimum_relative_jost_determinant: float = 1.0e-10
    maximum_estimated_outer_segments: int = 4096
    outer_segment_width_M: float = 5.0
    maximum_flux_residual: float = 1.0e-6
    baseline_r_in_eps: float = 1.0e-6
    baseline_rtol: float = 1.0e-10
    baseline_atol: float = 1.0e-12
    baseline_jost_order: int = 160
    r_in_ladder: tuple[float, ...] = (3.0e-6, 1.0e-6, 3.0e-7)
    jost_order_ladder: tuple[int, ...] = (80, 120, 160, 224)
    tolerance_ladder: tuple[tuple[float, float], ...] = (
        (1.0e-8, 1.0e-10),
        (1.0e-10, 1.0e-12),
        (1.0e-12, 1.0e-14),
    )

    def __post_init__(self) -> None:
        finite_positive = (
            self.required_radius_M,
            *self.r_out_candidates_M,
            self.minimum_turning_proxy_margin,
            self.maximum_outer_potential_ratio,
            self.minimum_k_r_out,
            self.maximum_scaled_jost_condition,
            self.minimum_relative_jost_determinant,
            self.maximum_flux_residual,
            self.outer_segment_width_M,
            self.baseline_r_in_eps,
            self.baseline_rtol,
            self.baseline_atol,
            *self.r_in_ladder,
        )
        if any(not math.isfinite(value) or value <= 0.0 for value in finite_positive):
            raise ConditioningScanError(
                "conditioning policy contains a nonpositive value"
            )
        if tuple(sorted(set(self.r_out_candidates_M))) != self.r_out_candidates_M:
            raise ConditioningScanError("r_out candidates must be strictly increasing")
        if len(self.r_out_candidates_M) < 3:
            raise ConditioningScanError("at least three r_out candidates are required")
        if self.r_out_candidates_M[0] <= self.required_radius_M:
            raise ConditioningScanError("every r_out candidate must exceed 40M")
        if (
            isinstance(self.maximum_estimated_outer_segments, bool)
            or not isinstance(self.maximum_estimated_outer_segments, int)
            or self.maximum_estimated_outer_segments < 1
        ):
            raise ConditioningScanError("outer-segment cap must be a positive integer")
        if self.baseline_r_in_eps not in self.r_in_ladder:
            raise ConditioningScanError("r_in ladder must contain the baseline")
        if len(self.r_in_ladder) != 3 or len(set(self.r_in_ladder)) != len(
            self.r_in_ladder
        ):
            raise ConditioningScanError("r_in ladder must contain three unique nodes")
        if self.baseline_jost_order not in self.jost_order_ladder:
            raise ConditioningScanError("Jost ladder must contain the baseline")
        if len(self.jost_order_ladder) != 4 or len(set(self.jost_order_ladder)) != len(
            self.jost_order_ladder
        ):
            raise ConditioningScanError("Jost ladder must contain four unique nodes")
        if (self.baseline_rtol, self.baseline_atol) not in self.tolerance_ladder:
            raise ConditioningScanError("tolerance ladder must contain the baseline")
        if len(self.tolerance_ladder) != 3 or len(set(self.tolerance_ladder)) != len(
            self.tolerance_ladder
        ):
            raise ConditioningScanError(
                "tolerance ladder must contain three unique nodes"
            )
        if any(
            not isinstance(order, int)
            or isinstance(order, bool)
            or not 2 <= order <= 256
            for order in self.jost_order_ladder
        ):
            raise ConditioningScanError("Jost orders must be integers in [2, 256]")
        if any(
            not math.isfinite(rtol)
            or not math.isfinite(atol)
            or rtol <= 0.0
            or atol <= 0.0
            or atol >= rtol
            for rtol, atol in self.tolerance_ladder
        ):
            raise ConditioningScanError("tolerance ladder is invalid")

    def to_record(self) -> dict[str, object]:
        return {
            "baseline": {
                "atol": self.baseline_atol,
                "jost_order": self.baseline_jost_order,
                "r_in_eps": self.baseline_r_in_eps,
                "rtol": self.baseline_rtol,
            },
            "calibration": {
                "jost_order_ladder": list(self.jost_order_ladder),
                "r_in_ladder": list(self.r_in_ladder),
                "r_out_ladder_width": 3,
                "tolerance_ladder": [list(pair) for pair in self.tolerance_ladder],
                "transition_key_count": 158,
            },
            "outer_selection": {
                "maximum_estimated_outer_segments": (
                    self.maximum_estimated_outer_segments
                ),
                "outer_segment_width_M": self.outer_segment_width_M,
                "maximum_outer_potential_ratio": (self.maximum_outer_potential_ratio),
                "maximum_scaled_jost_condition": (self.maximum_scaled_jost_condition),
                "minimum_k_r_out": self.minimum_k_r_out,
                "minimum_relative_jost_determinant": (
                    self.minimum_relative_jost_determinant
                ),
                "minimum_turning_proxy_margin": (self.minimum_turning_proxy_margin),
                "r_out_candidates_M": list(self.r_out_candidates_M),
                "turning_proxy": "sqrt(ell*(ell+1))/k",
            },
            "quality_gates": {
                "maximum_flux_residual": self.maximum_flux_residual,
            },
            "required_radius_M": self.required_radius_M,
            "schema": SCAN_POLICY_SCHEMA,
        }

    @property
    def sha256(self) -> str:
        return sha256_bytes(canonical_json_bytes(self.to_record()))


DEFAULT_POLICY = ConditioningPolicy()


@dataclass(frozen=True)
class FrozenScanContract:
    domain_root: Path
    execution_root: Path
    union_keys: tuple[RadialKey, ...]
    transition_keys: frozenset[RadialKey]
    shard_records: tuple[Mapping[str, object], ...]
    domain_identities: Mapping[str, Mapping[str, object]]
    execution_identities: Mapping[str, Mapping[str, object]]

    def shard_record(self, shard_id: str) -> Mapping[str, object]:
        matches = [item for item in self.shard_records if item["shard_id"] == shard_id]
        if len(matches) != 1:
            raise ConditioningScanError(f"unknown or duplicate shard id: {shard_id}")
        return matches[0]

    def shard_keys(self, shard_id: str) -> tuple[RadialKey, ...]:
        record = self.shard_record(shard_id)
        keys = tuple(
            key
            for key in self.union_keys
            if key.kM == record["kM"] and key.sector == record["sector"]
        )
        validate_ordered_unique_keys(keys)
        if (
            len(keys) != record["key_count"]
            or sha256_bytes(jsonl_bytes(keys)) != record["key_list_sha256"]
        ):
            raise ConditioningScanError("frozen shard key identity changed")
        return keys


def _strict_json(path: Path) -> Mapping[str, object]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise ConditioningScanError(f"cannot parse frozen JSON: {path}") from exc
    if not isinstance(value, Mapping) or raw != canonical_json_bytes(value):
        raise ConditioningScanError(f"frozen JSON is not canonical: {path}")
    return value


def _strict_jsonl_records(path: Path) -> tuple[Mapping[str, object], ...]:
    try:
        raw_lines = path.read_bytes().splitlines()
    except OSError as exc:
        raise ConditioningScanError(f"cannot read frozen JSONL: {path}") from exc
    records: list[Mapping[str, object]] = []
    for line in raw_lines:
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ConditioningScanError(f"cannot parse frozen JSONL: {path}") from exc
        if (
            not isinstance(value, Mapping)
            or canonical_json_bytes(value).rstrip(b"\n") != line
        ):
            raise ConditioningScanError(f"frozen JSONL is not canonical: {path}")
        records.append(value)
    return tuple(records)


def _verified_identities(
    root: Path,
    expected: Mapping[str, str],
) -> dict[str, Mapping[str, object]]:
    if root.is_symlink() or not root.is_dir() or root.resolve(strict=True) != root:
        raise ConditioningScanError(f"frozen root is missing or aliased: {root}")
    identities: dict[str, Mapping[str, object]] = {}
    for filename, digest in expected.items():
        path = root / filename
        identity = source_file_identity(path)
        if identity["sha256"] != digest or identity["mode"] != 0o444:
            raise ConditioningScanError(f"frozen input identity changed: {path}")
        identities[filename] = identity
    return identities


def load_frozen_scan_contract(
    domain_root: str | Path,
    execution_root: str | Path,
) -> FrozenScanContract:
    """Load and independently bind the frozen 17,818/158/86 inventories."""

    domain = Path(domain_root).resolve(strict=True)
    execution = Path(execution_root).resolve(strict=True)
    domain_identities = _verified_identities(domain, EXPECTED_DOMAIN_IDENTITIES)
    execution_identities = _verified_identities(
        execution, EXPECTED_EXECUTION_IDENTITIES
    )
    union_keys = read_jsonl_keys(domain / "D_union.jsonl")
    transition_keys = read_jsonl_keys(execution / "D_transition_calibration.jsonl")
    shard_records = _strict_jsonl_records(execution / "shard_inventory.jsonl")
    domain_contract = _strict_json(domain / "domain_contract.json")
    execution_contract = _strict_json(execution / "execution_contract.json")
    if len(union_keys) != 17818 or len(transition_keys) != 158:
        raise ConditioningScanError("frozen scan cardinality changed")
    if len(shard_records) != 86:
        raise ConditioningScanError("frozen shard cardinality changed")
    if domain_contract.get("schema") != "schwgw_phase6_v1_domain_contract_v1":
        raise ConditioningScanError("frozen domain schema changed")
    if execution_contract.get("schema") != "schwgw_phase6_v1_execution_contract_v1":
        raise ConditioningScanError("frozen execution schema changed")
    transition_contract = execution_contract.get("generic_transition_calibration")
    shard_contract = execution_contract.get("shard_inventory")
    if (
        not isinstance(transition_contract, Mapping)
        or transition_contract.get("count") != 158
        or transition_contract.get("key_list_sha256")
        != EXPECTED_EXECUTION_IDENTITIES["D_transition_calibration.jsonl"]
        or not isinstance(shard_contract, Mapping)
        or shard_contract.get("count") != 86
        or shard_contract.get("records") != list(shard_records)
    ):
        raise ConditioningScanError("frozen execution inventories disagree")
    if not set(transition_keys) <= set(union_keys):
        raise ConditioningScanError("transition calibration is outside D_union")
    result = FrozenScanContract(
        domain_root=domain,
        execution_root=execution,
        union_keys=union_keys,
        transition_keys=frozenset(transition_keys),
        shard_records=shard_records,
        domain_identities=domain_identities,
        execution_identities=execution_identities,
    )
    flattened: list[RadialKey] = []
    for record in shard_records:
        if set(record) != {
            "extension_key_count",
            "kM",
            "key_count",
            "key_list_sha256",
            "production_key_count",
            "sector",
            "shard_id",
        }:
            raise ConditioningScanError("frozen shard record schema changed")
        flattened.extend(result.shard_keys(str(record["shard_id"])))
    if tuple(flattened) != union_keys:
        raise ConditioningScanError("frozen shard order/union changed")
    return result


@dataclass(frozen=True)
class OuterCandidateDiagnostic:
    r_out_M: float
    turning_proxy_margin: float
    potential_to_k2: float
    k_r_out: float
    estimated_outer_segments: int
    scaled_jost_condition: float | None
    relative_jost_determinant: float | None
    status: str
    blockers: tuple[str, ...]

    def to_record(self) -> dict[str, object]:
        return {
            "blockers": list(self.blockers),
            "estimated_outer_segments": self.estimated_outer_segments,
            "k_r_out": self.k_r_out,
            "potential_to_k2": self.potential_to_k2,
            "r_out_M": self.r_out_M,
            "relative_jost_determinant": self.relative_jost_determinant,
            "scaled_jost_condition": self.scaled_jost_condition,
            "status": self.status,
            "turning_proxy_margin": self.turning_proxy_margin,
        }


@dataclass(frozen=True)
class OuterSelection:
    key: RadialKey
    status: str
    selected_r_out_M: float | None
    turning_proxy_M: float
    candidates: tuple[OuterCandidateDiagnostic, ...]
    blocker: str | None

    @property
    def supported(self) -> bool:
        return self.status == "SUPPORTED"

    def to_record(self) -> dict[str, object]:
        return {
            "blocker": self.blocker,
            "candidates": [item.to_record() for item in self.candidates],
            "key": self.key.to_record(),
            "selected_r_out_M": self.selected_r_out_M,
            "status": self.status,
            "turning_proxy_M": self.turning_proxy_M,
        }


BasisProbe = Callable[[RadialKey, float, int], Mapping[str, float]]
PotentialProbe = Callable[[RadialKey, float], float]


def _default_potential_probe(key: RadialKey, radius: float) -> float:
    background = SchwarzschildBackground(M=1.0)
    potential = V_RW if key.sector == "odd" else V_Zerilli
    return float(potential(key.ell, radius, background))


def _default_basis_probe(
    key: RadialKey,
    radius: float,
    order: int,
) -> Mapping[str, float]:
    background = SchwarzschildBackground(M=1.0)
    sector = Sector(key.sector)
    incoming = outer_asymptotic_basis(
        sector=sector,
        ell=key.ell,
        r=radius,
        k=float(key.kM),
        background=background,
        sign=-1,
        basis="jost_1_over_r",
        series_order=order,
    )
    outgoing = outer_asymptotic_basis(
        sector=sector,
        ell=key.ell,
        r=radius,
        k=float(key.kM),
        background=background,
        sign=1,
        basis="jost_1_over_r",
        series_order=order,
    )
    matrix = np.asarray(
        [
            [incoming.psi, outgoing.psi],
            [incoming.dpsi_dr, outgoing.dpsi_dr],
        ],
        dtype=np.complex128,
    )
    norms = np.linalg.norm(matrix, axis=0)
    if (
        not np.all(np.isfinite(matrix))
        or not np.all(np.isfinite(norms))
        or np.any(norms <= np.finfo(float).tiny)
    ):
        raise ConditioningScanError("Jost basis probe is non-finite or degenerate")
    scaled = matrix / norms[np.newaxis, :]
    return {
        "condition": float(np.linalg.cond(scaled)),
        "relative_determinant": float(abs(np.linalg.det(matrix)) / np.prod(norms)),
    }


def select_outer_boundary(
    key: RadialKey,
    *,
    policy: ConditioningPolicy = DEFAULT_POLICY,
    potential_probe: PotentialProbe = _default_potential_probe,
    basis_probe: BasisProbe = _default_basis_probe,
) -> OuterSelection:
    """Select the first frozen r_out node satisfying every generic raw gate."""

    if not isinstance(key, RadialKey):
        raise TypeError("key must be a RadialKey")
    k = float(key.kM)
    turning_proxy = math.sqrt(key.ell * (key.ell + 1.0)) / k
    diagnostics: list[OuterCandidateDiagnostic] = []
    for radius in policy.r_out_candidates_M:
        margin = radius / turning_proxy
        k_radius = k * radius
        estimated_segments = math.ceil(
            (radius - policy.required_radius_M) / policy.outer_segment_width_M
        )
        blockers: list[str] = []
        if margin < policy.minimum_turning_proxy_margin:
            blockers.append("TURNING_PROXY_MARGIN")
        if k_radius < policy.minimum_k_r_out:
            blockers.append("K_R_OUT_ASYMPTOTIC_MARGIN")
        if estimated_segments > policy.maximum_estimated_outer_segments:
            blockers.append("OUTER_SEGMENT_CAP")
        try:
            potential_ratio = potential_probe(key, radius) / (k * k)
        except Exception as exc:
            potential_ratio = UNASSESSED_FINITE_BUDGET
            blockers.append(f"POTENTIAL_PROBE:{type(exc).__name__}")
        if not math.isfinite(potential_ratio) or potential_ratio < 0.0:
            blockers.append("POTENTIAL_RATIO_NONFINITE_OR_NEGATIVE")
        elif potential_ratio > policy.maximum_outer_potential_ratio:
            blockers.append("POTENTIAL_RATIO")
        condition: float | None = None
        determinant: float | None = None
        analytic_gate_passed = not blockers
        if analytic_gate_passed:
            try:
                basis = basis_probe(key, radius, policy.baseline_jost_order)
                if set(basis) != {"condition", "relative_determinant"}:
                    raise ConditioningScanError("basis probe schema changed")
                condition = float(basis["condition"])
                determinant = float(basis["relative_determinant"])
            except Exception as exc:
                blockers.append(f"JOST_PROBE:{type(exc).__name__}")
            else:
                if not math.isfinite(condition):
                    blockers.append("JOST_CONDITION_NONFINITE")
                elif condition > policy.maximum_scaled_jost_condition:
                    blockers.append("JOST_CONDITION")
                if not math.isfinite(determinant):
                    blockers.append("JOST_DETERMINANT_NONFINITE")
                elif determinant < policy.minimum_relative_jost_determinant:
                    blockers.append("JOST_DETERMINANT")
        diagnostic = OuterCandidateDiagnostic(
            r_out_M=radius,
            turning_proxy_margin=margin,
            potential_to_k2=float(potential_ratio),
            k_r_out=k_radius,
            estimated_outer_segments=estimated_segments,
            scaled_jost_condition=condition,
            relative_jost_determinant=determinant,
            status="PASS" if not blockers else "FAIL_CLOSED",
            blockers=tuple(blockers),
        )
        diagnostics.append(diagnostic)
        if not blockers:
            return OuterSelection(
                key=key,
                status="SUPPORTED",
                selected_r_out_M=radius,
                turning_proxy_M=turning_proxy,
                candidates=tuple(diagnostics),
                blocker=None,
            )
    return OuterSelection(
        key=key,
        status="UNSUPPORTED_FAIL_CLOSED",
        selected_r_out_M=None,
        turning_proxy_M=turning_proxy,
        candidates=tuple(diagnostics),
        blocker="NO_FROZEN_R_OUT_NODE_PASSES_ALL_RAW_GATES",
    )


@dataclass(frozen=True)
class SolveNode:
    node_id: str
    axis: str
    r_in_eps: float
    r_out_M: float
    jost_order: int
    rtol: float
    atol: float
    is_baseline: bool

    def descriptor(self) -> dict[str, object]:
        return {
            "actual_precision_digits": 16,
            "node_id": self.node_id,
            "tolerance": self.rtol,
        }

    def to_record(self) -> dict[str, object]:
        return {
            "atol": self.atol,
            "axis": self.axis,
            "is_baseline": self.is_baseline,
            "jost_order": self.jost_order,
            "node_id": self.node_id,
            "r_in_eps": self.r_in_eps,
            "r_out_M": self.r_out_M,
            "rtol": self.rtol,
        }


def _number_token(value: float) -> str:
    return format(value, ".17g").replace("-", "m").replace(".", "p")


def calibration_solve_nodes(
    selection: OuterSelection,
    *,
    transition_key: bool,
    policy: ConditioningPolicy = DEFAULT_POLICY,
) -> tuple[SolveNode, ...]:
    """Return a unique ordered solve plan with the baseline appearing once."""

    if not selection.supported or selection.selected_r_out_M is None:
        return ()
    baseline = SolveNode(
        node_id="baseline",
        axis="baseline",
        r_in_eps=policy.baseline_r_in_eps,
        r_out_M=selection.selected_r_out_M,
        jost_order=policy.baseline_jost_order,
        rtol=policy.baseline_rtol,
        atol=policy.baseline_atol,
        is_baseline=True,
    )
    if not transition_key:
        return (baseline,)
    nodes: list[SolveNode] = [baseline]
    for value in policy.r_in_ladder:
        if value == policy.baseline_r_in_eps:
            continue
        nodes.append(
            SolveNode(
                node_id=f"r_in_eps={_number_token(value)}",
                axis="r_in",
                r_in_eps=value,
                r_out_M=baseline.r_out_M,
                jost_order=baseline.jost_order,
                rtol=baseline.rtol,
                atol=baseline.atol,
                is_baseline=False,
            )
        )
    selected_index = policy.r_out_candidates_M.index(baseline.r_out_M)
    window_start = min(
        max(selected_index - 1, 0),
        len(policy.r_out_candidates_M) - 3,
    )
    r_out_nodes = policy.r_out_candidates_M[window_start : window_start + 3]
    if len(r_out_nodes) != 3 or baseline.r_out_M not in r_out_nodes:
        raise ConditioningScanError("three-node r_out ladder cannot be constructed")
    for value in r_out_nodes:
        if value == baseline.r_out_M:
            continue
        nodes.append(
            SolveNode(
                node_id=f"r_out_M={_number_token(value)}",
                axis="r_out",
                r_in_eps=baseline.r_in_eps,
                r_out_M=value,
                jost_order=baseline.jost_order,
                rtol=baseline.rtol,
                atol=baseline.atol,
                is_baseline=False,
            )
        )
    for order in policy.jost_order_ladder:
        if order == policy.baseline_jost_order:
            continue
        nodes.append(
            SolveNode(
                node_id=f"jost_order={order}",
                axis="jost_order",
                r_in_eps=baseline.r_in_eps,
                r_out_M=baseline.r_out_M,
                jost_order=order,
                rtol=baseline.rtol,
                atol=baseline.atol,
                is_baseline=False,
            )
        )
    for rtol, atol in policy.tolerance_ladder:
        if (rtol, atol) == (policy.baseline_rtol, policy.baseline_atol):
            continue
        nodes.append(
            SolveNode(
                node_id=(
                    f"tolerance=rtol_{_number_token(rtol)}_atol_{_number_token(atol)}"
                ),
                axis="ode_tolerance",
                r_in_eps=baseline.r_in_eps,
                r_out_M=baseline.r_out_M,
                jost_order=baseline.jost_order,
                rtol=rtol,
                atol=atol,
                is_baseline=False,
            )
        )
    configs = {
        (node.r_in_eps, node.r_out_M, node.jost_order, node.rtol, node.atol)
        for node in nodes
    }
    if (
        len(configs) != len(nodes)
        or len({node.node_id for node in nodes}) != len(nodes)
        or sum(node.is_baseline for node in nodes) != 1
        or nodes[0] != baseline
    ):
        raise ConditioningScanError("solve plan duplicates a baseline or ladder node")
    return tuple(nodes)


def _complex_record(value: complex) -> dict[str, str]:
    parsed = complex(value)
    magnitude = abs(parsed)
    if (
        not np.isfinite(parsed.real)
        or not np.isfinite(parsed.imag)
        or not math.isfinite(magnitude)
    ):
        raise ConditioningScanError("solver returned a non-finite complex value")
    return {
        "abs": format(magnitude, ".17g"),
        "imag": format(parsed.imag, ".17g"),
        "real": format(parsed.real, ".17g"),
    }


def _finite_float(value: object, label: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ConditioningScanError(f"non-finite solver diagnostic: {label}")
    return parsed


def _conditioned_result_record(
    key: RadialKey,
    node: SolveNode,
    request: ConditionedRadialRequest,
    result: ConditionedRadialResult,
) -> dict[str, object]:
    diagnostics = dict(result.diagnostics)
    if diagnostics.get("paper_specific_envelope_used") is not False:
        raise ConditioningScanError("conditioned result used a paper-specific envelope")
    if diagnostics.get("actual_precision_bits") != 53:
        raise ConditioningScanError(
            "conditioned result actual precision is not float64"
        )
    expected_diagnostics = {
        "atol": request.atol,
        "backend": "scipy_float64_conditioned_radial_v1",
        "ell": request.ell,
        "finite_radius_checkpoint_count": 1,
        "finite_radius_checkpoint_radii": format(request.required_radius, ".17g"),
        "k": request.k,
        "outer_basis": request.outer_basis,
        "outer_series_order": request.outer_series_order,
        "r_out": request.r_out,
        "required_radius": request.required_radius,
        "rtol": request.rtol,
        "scientific_acceptance": False,
        "sector": request.sector.value,
        "unit_incoming_at_infinity": True,
        "valid_at_required_radius": True,
    }
    if any(
        diagnostics.get(name) != value for name, value in expected_diagnostics.items()
    ):
        raise ConditioningScanError("conditioned result/request identity changed")
    provenance_values = " ".join(
        str(value).lower()
        for name, value in diagnostics.items()
        if name
        in {
            "algorithm",
            "backend",
            "method",
            "normalization_definition",
            "provenance",
        }
    )
    forbidden_flags = {
        "legacy",
        "newman_penrose",
        "np",
        "np_path",
        "pseudoinverse",
    }
    if any(
        diagnostics.get(name) not in {None, False} for name in forbidden_flags
    ) or any(
        token in provenance_values
        for token in (
            "legacy",
            "newman-penrose",
            "newman_penrose",
            "pseudoinverse",
        )
    ):
        raise ConditioningScanError("conditioned result contains forbidden provenance")
    if result.A_in != 1.0 + 0.0j:
        raise ConditioningScanError("conditioned result is not unit incoming")
    states = result.finite_radius_states
    if len(states) != 1 or states[0].radius != request.required_radius:
        raise ConditioningScanError(
            "baseline result must contain exactly one required-radius state"
        )
    primary_state = states[0]
    if (
        primary_state.psi != result.psi
        or primary_state.dpsi_dr != result.dpsi_dr
        or primary_state.log_abs_psi != result.log_abs_psi
        or primary_state.phase_psi != result.phase_psi
        or primary_state.log_abs_dpsi_dr != result.log_abs_dpsi_dr
        or primary_state.phase_dpsi_dr != result.phase_dpsi_dr
    ):
        raise ConditioningScanError(
            "primary finite-radius/result state linkage changed"
        )
    log_probability = 2.0 * result.log_abs_T_horizon
    if log_probability < math.log(float(np.nextafter(0.0, 1.0))):
        transmission_probability = 0.0
    elif log_probability > math.log(float(np.finfo(float).max)):
        raise ConditioningScanError("transmission probability exceeds float64")
    else:
        transmission_probability = math.exp(log_probability)
    computed_flux_residual = abs(
        abs(result.A_out) ** 2 + transmission_probability - 1.0
    )
    reported_flux_residual = _finite_float(
        diagnostics.get("flux_residual"), "flux_residual"
    )
    if not math.isclose(
        computed_flux_residual,
        reported_flux_residual,
        rel_tol=5.0e-13,
        abs_tol=5.0e-15,
    ):
        raise ConditioningScanError("reported flux residual is inconsistent")
    scattering = -result.A_out / ((-1) ** key.ell)
    required_radius_state = {
        "complex_derivative_status": primary_state.complex_derivative_status,
        "complex_state_status": primary_state.complex_state_status,
        "dpsi_dr": _complex_record(result.dpsi_dr),
        "log_abs_dpsi_dr": _finite_float(result.log_abs_dpsi_dr, "log_abs_dpsi_dr"),
        "log_abs_psi": _finite_float(result.log_abs_psi, "log_abs_psi"),
        "phase_dpsi_dr": _finite_float(result.phase_dpsi_dr, "phase_dpsi_dr"),
        "phase_psi": _finite_float(result.phase_psi, "phase_psi"),
        "psi": _complex_record(result.psi),
        "radius_M": request.required_radius,
    }
    finite_states = [
        {
            "complex_derivative_status": state.complex_derivative_status,
            "complex_state_status": state.complex_state_status,
            "dpsi_dr": _complex_record(state.dpsi_dr),
            "log_abs_dpsi_dr": _finite_float(state.log_abs_dpsi_dr, "log_abs_dpsi_dr"),
            "log_abs_psi": _finite_float(state.log_abs_psi, "log_abs_psi"),
            "phase_dpsi_dr": _finite_float(state.phase_dpsi_dr, "phase_dpsi_dr"),
            "phase_psi": _finite_float(state.phase_psi, "phase_psi"),
            "psi": _complex_record(state.psi),
            "radius_M": _finite_float(state.radius, "finite radius"),
        }
        for state in states[1:]
    ]
    raw_diagnostics: dict[str, object] = {}
    for name, value in sorted(diagnostics.items()):
        if isinstance(value, bool | int | str):
            raw_diagnostics[name] = value
        elif isinstance(value, float):
            raw_diagnostics[name] = _finite_float(value, name)
        else:
            raise ConditioningScanError(f"unsupported diagnostic type: {name}")
    return {
        "A_in": _complex_record(result.A_in),
        "A_out": _complex_record(result.A_out),
        "S": _complex_record(scattering),
        "T_horizon": _complex_record(result.T_horizon),
        "configuration": node.to_record(),
        "diagnostics": raw_diagnostics,
        "additional_requested_finite_radius_states": finite_states,
        "key": key.to_record(),
        "log_phase": {
            "log_abs_T_horizon": _finite_float(
                result.log_abs_T_horizon, "log_abs_T_horizon"
            ),
            "log_abs_dpsi_dr": _finite_float(result.log_abs_dpsi_dr, "log_abs_dpsi_dr"),
            "log_abs_psi": _finite_float(result.log_abs_psi, "log_abs_psi"),
            "phase_T_horizon": _finite_float(result.phase_T_horizon, "phase_T_horizon"),
            "phase_dpsi_dr": _finite_float(result.phase_dpsi_dr, "phase_dpsi_dr"),
            "phase_psi": _finite_float(result.phase_psi, "phase_psi"),
        },
        "required_radius_state": required_radius_state,
        "schema_version": "schwgw_phase6_conditioned_radial_node_result_v1",
    }


def _complex_from_record(value: Mapping[str, object]) -> complex:
    if set(value) != {"abs", "imag", "real"}:
        raise ConditioningScanError("complex record schema changed")
    parsed = complex(float(value["real"]), float(value["imag"]))
    if not np.isfinite(parsed.real) or not np.isfinite(parsed.imag):
        raise ConditioningScanError("complex record is non-finite")
    if not math.isclose(
        abs(parsed),
        float(value["abs"]),
        rel_tol=5.0e-15,
        abs_tol=5.0e-324,
    ):
        raise ConditioningScanError("complex magnitude record is inconsistent")
    return parsed


def _axis_max_difference(
    baseline: Mapping[str, object],
    results: Sequence[Mapping[str, object]],
) -> float:
    baseline_s = _complex_from_record(baseline["S"])  # type: ignore[arg-type]
    return max(
        (abs(_complex_from_record(result["S"]) - baseline_s) for result in results),  # type: ignore[arg-type]
        default=0.0,
    )


def _budgets_and_statuses(
    *,
    nodes: Sequence[SolveNode],
    results: Mapping[str, Mapping[str, object]],
    failures: Mapping[str, str],
    transition_key: bool,
    maximum_flux_residual: float,
) -> tuple[dict[str, object], dict[str, object], dict[str, str], str]:
    baseline = results.get("baseline")
    if baseline is None:
        numerical = {
            "components": {
                name: UNASSESSED_FINITE_BUDGET for name in NUMERICAL_BUDGET_FIELDS
            },
            "status": "FAIL",
        }
        convention = {
            "components": {
                name: UNASSESSED_FINITE_BUDGET for name in CONVENTION_BUDGET_FIELDS
            },
            "status": "FAIL",
        }
        return (
            numerical,
            convention,
            {
                "conditioning_transition_calibration": (
                    "FAIL" if transition_key else "NOT_ASSESSED"
                ),
                "flux_conservation": "FAIL",
                "production_finite_radius_states": "NOT_ASSESSED",
                "radial_s_matrix": "FAIL",
                "required_radius_radial_state": "FAIL",
            },
            "FAIL",
        )
    by_axis = {
        axis: [
            results[node.node_id]
            for node in nodes
            if node.axis == axis and node.node_id in results
        ]
        for axis in ("r_in", "r_out", "jost_order", "ode_tolerance")
    }
    axis_values = {
        axis: (
            _axis_max_difference(baseline, values)
            if transition_key and values
            else UNASSESSED_FINITE_BUDGET
        )
        for axis, values in by_axis.items()
    }
    baseline_diagnostics = baseline["diagnostics"]
    if not isinstance(baseline_diagnostics, Mapping):
        raise ConditioningScanError("baseline diagnostics are malformed")
    numerical = {
        "components": {
            "arithmetic_precision": float(np.finfo(float).eps),
            "axis_limit": 0.0,
            "backend_difference": UNASSESSED_FINITE_BUDGET,
            "jost_order": axis_values["jost_order"],
            "lmax": 0.0,
            "ode_tolerance": axis_values["ode_tolerance"],
            "r_in": axis_values["r_in"],
            "r_out": axis_values["r_out"],
        },
        "status": "FAIL" if failures else "PARTIAL",
    }
    convention = {
        "components": {
            "observer": UNASSESSED_FINITE_BUDGET,
            "phase_origin": math.pi,
            "polarization_basis": UNASSESSED_FINITE_BUDGET,
            "tetrad": UNASSESSED_FINITE_BUDGET,
            "total_scattered_definition": UNASSESSED_FINITE_BUDGET,
        },
        "status": "PARTIAL",
    }
    flux_residual = _finite_float(
        baseline_diagnostics.get("flux_residual"), "flux_residual"
    )
    flux_status = "PASS" if flux_residual <= maximum_flux_residual else "FAIL"
    if flux_status == "FAIL":
        numerical["status"] = "FAIL"
    calibration_status = "NOT_ASSESSED"
    if transition_key:
        calibration_status = "PARTIAL" if not failures else "FAIL"
    observable_statuses = {
        "conditioning_transition_calibration": calibration_status,
        "flux_conservation": flux_status,
        "production_finite_radius_states": "NOT_ASSESSED",
        "radial_s_matrix": "PARTIAL",
        "required_radius_radial_state": "PARTIAL",
    }
    acceptance_state = "FAIL" if "FAIL" in observable_statuses.values() else "PARTIAL"
    return numerical, convention, observable_statuses, acceptance_state


def execute_key_scan(
    key: RadialKey,
    selection: OuterSelection,
    *,
    transition_key: bool,
    policy: ConditioningPolicy = DEFAULT_POLICY,
    solver: ConditionedSolver = solve_conditioned_radial_at_radius,
    background: SchwarzschildBackground | None = None,
) -> dict[str, object]:
    """Execute one baseline and, only for a frozen transition key, its ladders."""

    if selection.key != key:
        raise ConditioningScanError("outer selection belongs to a different key")
    nodes = calibration_solve_nodes(
        selection,
        transition_key=transition_key,
        policy=policy,
    )
    if not selection.supported:
        blocked_node_id = "baseline_preflight"
        numerical, convention, observables, acceptance = _budgets_and_statuses(
            nodes=(),
            results={},
            failures={blocked_node_id: selection.blocker or "unsupported"},
            transition_key=transition_key,
            maximum_flux_residual=policy.maximum_flux_residual,
        )
        return {
            "acceptance_state": acceptance,
            "actual_precision": {
                "backend": "scipy_float64_conditioned_radial_v1",
                "digits": 16,
            },
            "baseline_solver_call_count": 0,
            "convention_budget": convention,
            "failures": {
                blocked_node_id: selection.blocker
                or "NO_FROZEN_R_OUT_NODE_PASSES_ALL_RAW_GATES"
            },
            "key": key.to_record(),
            "ladder_nodes": [
                {
                    "actual_precision_digits": 16,
                    "node_id": blocked_node_id,
                    "status": "FAIL",
                    "tolerance": policy.baseline_rtol,
                }
            ],
            "numerical_budget": numerical,
            "observable_statuses": observables,
            "outer_selection": selection.to_record(),
            "policy_sha256": policy.sha256,
            "results": {},
            "schema_version": SOLVER_PAYLOAD_SCHEMA,
            "scope_qualification": {
                "mode_level_s_matrix_only": True,
                "observer_response_claim": False,
                "production_finite_radius_states": "NOT_ASSESSED",
                "required_radius_M": policy.required_radius_M,
            },
            "total_solver_call_count": 0,
            "transition_key": transition_key,
        }
    actual_background = background or SchwarzschildBackground(M=1.0)
    results: dict[str, Mapping[str, object]] = {}
    failures: dict[str, str] = {}
    baseline_calls = 0
    total_calls = 0
    for node in nodes:
        request = ConditionedRadialRequest(
            sector=Sector(key.sector),
            ell=key.ell,
            k=float(key.kM),
            required_radius=policy.required_radius_M,
            r_out=node.r_out_M,
            r_in_eps=node.r_in_eps,
            rtol=node.rtol,
            atol=node.atol,
            outer_basis="jost_1_over_r",
            outer_series_order=node.jost_order,
        )
        total_calls += 1
        baseline_calls += int(node.is_baseline)
        try:
            result = solver(request, actual_background)
            results[node.node_id] = _conditioned_result_record(
                key,
                node,
                request,
                result,
            )
        except Exception as exc:
            failures[node.node_id] = (
                f"{type(exc).__name__}: {str(exc) or '<empty exception message>'}"
            )
    if baseline_calls != 1:
        raise ConditioningScanError(
            "supported key did not receive exactly one baseline"
        )
    numerical, convention, observables, acceptance = _budgets_and_statuses(
        nodes=nodes,
        results=results,
        failures=failures,
        transition_key=transition_key,
        maximum_flux_residual=policy.maximum_flux_residual,
    )
    ladder_records = [
        {
            **node.descriptor(),
            "status": "PASS" if node.node_id in results else "FAIL",
        }
        for node in nodes
    ]
    return {
        "acceptance_state": acceptance,
        "actual_precision": {
            "backend": "scipy_float64_conditioned_radial_v1",
            "digits": 16,
        },
        "baseline_solver_call_count": baseline_calls,
        "convention_budget": convention,
        "failures": failures,
        "key": key.to_record(),
        "ladder_nodes": ladder_records,
        "numerical_budget": numerical,
        "observable_statuses": observables,
        "outer_selection": selection.to_record(),
        "policy_sha256": policy.sha256,
        "results": dict(results),
        "schema_version": SOLVER_PAYLOAD_SCHEMA,
        "scope_qualification": {
            "mode_level_s_matrix_only": True,
            "observer_response_claim": False,
            "production_finite_radius_states": "NOT_ASSESSED",
            "required_radius_M": policy.required_radius_M,
        },
        "total_solver_call_count": total_calls,
        "transition_key": transition_key,
    }


def ladder_descriptor_hash(payload: Mapping[str, object]) -> str:
    nodes = payload.get("ladder_nodes")
    if not isinstance(nodes, list):
        raise ConditioningScanError("solver payload ladder nodes are missing")
    descriptors = [
        {
            "actual_precision_digits": node["actual_precision_digits"],
            "node_id": node["node_id"],
            "tolerance": node["tolerance"],
        }
        for node in nodes
        if isinstance(node, Mapping)
    ]
    if len(descriptors) != len(nodes):
        raise ConditioningScanError("solver payload ladder descriptor is malformed")
    return sha256_bytes(canonical_json_bytes(descriptors))


def checkpoint_fields_from_solver_payload(
    payload: Mapping[str, object],
) -> dict[str, object]:
    """Project a solver payload into the frozen key-checkpoint budget fields."""

    if payload.get("schema_version") != SOLVER_PAYLOAD_SCHEMA:
        raise ConditioningScanError("solver payload schema changed")
    nodes = payload.get("ladder_nodes")
    failures = payload.get("failures")
    if not isinstance(nodes, list) or not isinstance(failures, Mapping):
        raise ConditioningScanError("solver payload ladder/failure schema changed")
    failure_records = [
        {"node_id": node["node_id"], "reason": failures[node["node_id"]]}
        for node in nodes
        if isinstance(node, Mapping) and node.get("status") == "FAIL"
    ]
    return {
        "acceptance_state": payload["acceptance_state"],
        "actual_precision": payload["actual_precision"],
        "attempts": [{"attempt": 1, "status": payload["acceptance_state"]}],
        "convention_budget": payload["convention_budget"],
        "ladder": {
            "axis_map_sha256": ladder_descriptor_hash(payload),
            "failures": failure_records,
            "nodes": nodes,
        },
        "numerical_budget": payload["numerical_budget"],
        "observable_statuses": payload["observable_statuses"],
        "provenance": {
            "legacy": False,
            "np": False,
            "pseudoinverse": False,
        },
    }


def key_artifact_filenames(shard_ordinal: int, key: RadialKey) -> dict[str, str]:
    if isinstance(shard_ordinal, bool) or shard_ordinal < 0:
        raise ConditioningScanError("shard ordinal must be nonnegative")
    token = (
        f"key_{shard_ordinal:04d}__kM_{key.kM.replace('.', 'p')}__"
        f"{key.sector}__ell_{key.ell:04d}"
    )
    return {
        "payload": f"{token}__payload.json",
        "result": f"{token}__result.json",
        "checkpoint": f"{token}__checkpoint.json",
        "terminal": f"{token}__terminal.json",
    }


def source_hash_map(
    identities: Mapping[str, Mapping[str, object]],
) -> dict[str, str]:
    result: dict[str, str] = {}
    for name, identity in sorted(identities.items()):
        digest = identity.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ConditioningScanError(f"source identity lacks SHA-256: {name}")
        result[name] = digest
    return result


def scan_context_hash(record: Mapping[str, object]) -> str:
    """Hash a run context after excluding path/time/publication-only fields."""

    excluded = {"context_sha256", "created_at_utc", "output_root", "resume_from"}
    return hashlib.sha256(
        canonical_json_bytes(
            {name: value for name, value in record.items() if name not in excluded}
        )
    ).hexdigest()


__all__ = [
    "CHECKPOINT_SCHEMA",
    "ConditionedSolver",
    "ConditioningPolicy",
    "ConditioningScanError",
    "DEFAULT_POLICY",
    "EXPECTED_DOMAIN_IDENTITIES",
    "EXPECTED_EXECUTION_IDENTITIES",
    "FrozenScanContract",
    "KEY_PAYLOAD_ENVELOPE_SCHEMA",
    "KEY_RESULT_SCHEMA",
    "KEY_TERMINAL_SCHEMA",
    "OuterCandidateDiagnostic",
    "OuterSelection",
    "RUN_CONTRACT_SCHEMA",
    "SCAN_POLICY_SCHEMA",
    "SHARD_FAILURE_SCHEMA",
    "SOLVER_PAYLOAD_SCHEMA",
    "SolveNode",
    "calibration_solve_nodes",
    "checkpoint_fields_from_solver_payload",
    "execute_key_scan",
    "key_artifact_filenames",
    "ladder_descriptor_hash",
    "load_frozen_scan_contract",
    "scan_context_hash",
    "select_outer_boundary",
    "source_hash_map",
]
