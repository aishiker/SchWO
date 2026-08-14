"""Resumable pole-safe boundary ladders for the failed Phase-6 V1 domain.

The runner consumes the exact 5,798 fail-closed keys in the immutable V1
conditioning campaign and evaluates five same-equation scaled-tortoise nodes:
the frozen baseline, two near-horizon boundary placements, and two farther
outer boundaries.  It is diagnostic evidence only.  No threshold is defined,
the backend is not independent, and convention uncertainty remains unassessed.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import stat
import sys
from time import perf_counter
from typing import Any

import numpy as np
import scipy

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.numerics.conditioned_radial import (
    ConditionedRadialRequest,
    ConditionedRadialResult,
)
from schwgw.numerics.scaled_tortoise_radial import (
    solve_scaled_tortoise_radial_at_radius,
)
from schwgw.perturbations import Sector
from schwgw.validation.phase6_conditioning_campaign import (
    CAMPAIGN_INDEX_SCHEMA,
    EXPECTED_KEY_COUNT,
    EXPECTED_SHARD_COUNT,
    validate_published_conditioning_campaign,
)
from schwgw.validation.phase6_conditioning_scan import SOLVER_PAYLOAD_SCHEMA
from schwgw.validation.phase6_execution_contract import (
    KEY_PAYLOAD_ENVELOPE_SCHEMA,
)

SCHEMA = "schwgw_phase6_v1_radial_failure_boundary_ladders_diagnostic_v1"
KEY_RECORD_SCHEMA = f"{SCHEMA}_key_record"
SUMMARY_SCHEMA = f"{SCHEMA}_summary"
MANIFEST_SCHEMA = f"{SCHEMA}_manifest"
EXPECTED_FAILED_KEY_COUNT = 5_798
EXPECTED_SUCCESS_KEY_COUNT = 12_020
EXPECTED_BACKEND = "scipy_float64_scaled_tortoise_radial_repair_v1"
EXPECTED_METHOD = "scaled_tortoise_full_state_jost_ratio"
FIXED_RTOL = 1.0e-10
FIXED_ATOL = 1.0e-12
FIXED_JOST_ORDER = 160

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CAMPAIGN_ROOT = (
    PROJECT_ROOT / "runs/phase6/radial_validation/"
    "v1_conditioning_campaign_v1_20260808_py314"
)

Solver = Callable[
    [ConditionedRadialRequest, SchwarzschildBackground], ConditionedRadialResult
]


@dataclass(frozen=True)
class BoundaryNode:
    node_id: str
    axis: str
    r_in_eps: float
    r_out_factor: float


BOUNDARY_NODES = (
    BoundaryNode("baseline", "baseline", 1.0e-6, 1.0),
    BoundaryNode("r_in_3e-6", "r_in", 3.0e-6, 1.0),
    BoundaryNode("r_in_3e-7", "r_in", 3.0e-7, 1.0),
    BoundaryNode("r_out_x2", "r_out", 1.0e-6, 2.0),
    BoundaryNode("r_out_x4", "r_out", 1.0e-6, 4.0),
)


@dataclass(frozen=True)
class FailedKey:
    key: Mapping[str, Any]
    key_id: str
    shard_id: str
    selected_r_out_M: float
    required_radius_M: float
    predecessor_failures: Mapping[str, str]
    predecessor_payload_identity: Mapping[str, Any]

    def inventory_record(self) -> dict[str, Any]:
        return {
            "key": dict(self.key),
            "key_id": self.key_id,
            "payload_sha256": self.predecessor_payload_identity["sha256"],
            "selected_r_out_M": self.selected_r_out_M,
            "shard_id": self.shard_id,
        }


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _identity(path: Path) -> dict[str, Any]:
    original = path.absolute()
    status = original.lstat()
    if not original.is_file() or original.is_symlink() or status.st_nlink != 1:
        raise RuntimeError(f"identity source must be a regular nlink1 file: {original}")
    return {
        "mode": stat.S_IMODE(status.st_mode),
        "nlink": status.st_nlink,
        "path": str(original),
        "sha256": _sha256_file(original),
        "size": status.st_size,
    }


def _validate_identity(expected: Mapping[str, Any], path: Path) -> None:
    if dict(expected) != _identity(path):
        raise RuntimeError(f"file identity changed: {path}")


def _load_json(path: Path, *, canonical: bool = False) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    if canonical and raw != _canonical_bytes(value):
        raise RuntimeError(f"non-canonical JSON: {path}")
    return value


def _write_all(descriptor: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("file write made no progress")
        view = view[written:]


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_exclusive(path: Path, value: Any) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        _write_all(descriptor, _canonical_bytes(value))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    _fsync_directory(path.parent)


def _create_empty_exclusive(path: Path) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    _fsync_directory(path.parent)


def _write_atomic(path: Path, value: Any) -> None:
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    _write_exclusive(temporary, value)
    os.replace(temporary, path)
    _fsync_directory(path.parent)


def _append_fsynced(path: Path, value: Any) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_APPEND)
    try:
        _write_all(descriptor, _canonical_bytes(value))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


class _WriterGuard:
    def __init__(self, path: Path, *, resume: bool) -> None:
        flags = os.O_RDWR if resume else os.O_RDWR | os.O_CREAT | os.O_EXCL
        descriptor = os.open(path, flags, 0o644)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            os.close(descriptor)
            raise RuntimeError("output root already has an active writer") from exc
        self._stream = os.fdopen(descriptor, "r+b", buffering=0)
        self._previous = self._read_previous() if resume else None

    def _read_previous(self) -> dict[str, Any] | None:
        self._stream.seek(0)
        raw = self._stream.read()
        if not raw:
            return None
        value = json.loads(raw)
        if not isinstance(value, dict) or raw != _canonical_bytes(value):
            raise RuntimeError("writer.lock is not a canonical guard record")
        return value

    def write_state(self, state: str, **extra: Any) -> None:
        record = {
            "schema": f"{SCHEMA}_writer_guard",
            "state": state,
            "pid": os.getpid(),
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "single_writer_enforced": True,
            "single_writer_mechanism": "fcntl.flock(LOCK_EX|LOCK_NB)",
            **extra,
        }
        if self._previous is not None:
            record["resumed_after"] = {
                "pid": self._previous.get("pid"),
                "state": self._previous.get("state"),
                "updated_at_utc": self._previous.get("updated_at_utc"),
            }
        self._stream.seek(0)
        self._stream.truncate(0)
        self._stream.write(_canonical_bytes(record))
        self._stream.flush()
        os.fsync(self._stream.fileno())

    def __enter__(self) -> _WriterGuard:
        return self

    def __exit__(self, *_: object) -> None:
        try:
            fcntl.flock(self._stream.fileno(), fcntl.LOCK_UN)
        finally:
            self._stream.close()


def _key_id(key: Mapping[str, Any]) -> str:
    return f"kM={key['kM']};sector={key['sector']};ell={int(key['ell'])}"


def _key_sort(spec: FailedKey) -> tuple[Decimal, int, int]:
    sector_order = 0 if spec.key["sector"] == "odd" else 1
    return Decimal(str(spec.key["kM"])), sector_order, int(spec.key["ell"])


def _finite_float(value: Any, *, label: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"{label} is not numeric") from exc
    if not math.isfinite(result):
        raise RuntimeError(f"{label} is not finite")
    return result


def discover_failed_keys(campaign_root: Path) -> tuple[FailedKey, ...]:
    """Live-rebuild the immutable campaign and enumerate exact failure keys."""

    root = campaign_root.resolve(strict=True)
    validate_published_conditioning_campaign(root)
    index = _load_json(root / "conditioning_campaign_index.json", canonical=True)
    if (
        index.get("schema") != CAMPAIGN_INDEX_SCHEMA
        or index.get("overall_state") != "FAIL"
        or index.get("coverage", {}).get("D_union_exact_coverage") is not True
        or index.get("coverage", {}).get("key_count") != EXPECTED_KEY_COUNT
        or index.get("coverage", {}).get("shard_count") != EXPECTED_SHARD_COUNT
        or index.get("terminal_completion_counts")
        != {
            "COMPLETED": EXPECTED_SUCCESS_KEY_COUNT,
            "COMPLETED_FAIL_CLOSED": EXPECTED_FAILED_KEY_COUNT,
        }
        or index.get("global_green_permitted") is not False
    ):
        raise RuntimeError("conditioning campaign coverage or policy changed")
    raw_shards = index.get("shards")
    if not isinstance(raw_shards, Sequence) or len(raw_shards) != EXPECTED_SHARD_COUNT:
        raise RuntimeError("conditioning campaign shard inventory changed")

    failed: list[FailedKey] = []
    successes = 0
    total = 0
    seen: set[str] = set()
    for shard in raw_shards:
        if not isinstance(shard, Mapping) or not isinstance(
            shard.get("shard"), Mapping
        ):
            raise RuntimeError("conditioning campaign shard entry is malformed")
        shard_record = shard["shard"]
        shard_id = str(shard_record.get("shard_id"))
        shard_root = Path(str(shard.get("root"))).resolve(strict=True)
        payloads = sorted(shard_root.glob("key_*__payload.json"))
        if len(payloads) != int(shard_record.get("key_count", -1)):
            raise RuntimeError(f"payload inventory changed for {shard_id}")
        for payload_path in payloads:
            total += 1
            envelope = _load_json(payload_path, canonical=True)
            if (
                envelope.get("schema") != KEY_PAYLOAD_ENVELOPE_SCHEMA
                or envelope.get("solver_payload_schema") != SOLVER_PAYLOAD_SCHEMA
            ):
                raise RuntimeError(f"conditioning envelope changed: {payload_path}")
            solver_payload = envelope.get("solver_payload")
            if not isinstance(solver_payload, Mapping):
                raise RuntimeError(f"missing solver payload: {payload_path}")
            if solver_payload.get("acceptance_state") == "PARTIAL":
                successes += 1
                continue
            if solver_payload.get("acceptance_state") != "FAIL":
                raise RuntimeError(f"unexpected failure-domain state: {payload_path}")
            key_raw = envelope.get("key")
            if not isinstance(key_raw, Mapping) or solver_payload.get("key") != key_raw:
                raise RuntimeError(f"failure key metadata mismatch: {payload_path}")
            key = {
                "ell": int(key_raw.get("ell")),
                "kM": str(key_raw.get("kM")),
                "sector": str(key_raw.get("sector")),
            }
            identity = _key_id(key)
            if identity in seen:
                raise RuntimeError(f"duplicate failure key: {identity}")
            seen.add(identity)
            failures = solver_payload.get("failures")
            outer = solver_payload.get("outer_selection")
            scope = solver_payload.get("scope_qualification")
            if (
                not isinstance(failures, Mapping)
                or not failures
                or not isinstance(outer, Mapping)
                or outer.get("status") != "SUPPORTED"
                or not isinstance(scope, Mapping)
                or solver_payload.get("results") != {}
            ):
                raise RuntimeError(f"failure payload contract changed: {payload_path}")
            failed.append(
                FailedKey(
                    key=key,
                    key_id=identity,
                    shard_id=shard_id,
                    selected_r_out_M=_finite_float(
                        outer.get("selected_r_out_M"), label="selected_r_out_M"
                    ),
                    required_radius_M=_finite_float(
                        scope.get("required_radius_M"), label="required_radius_M"
                    ),
                    predecessor_failures={str(k): str(v) for k, v in failures.items()},
                    predecessor_payload_identity=_identity(payload_path),
                )
            )
    failed.sort(key=_key_sort)
    if (
        total != EXPECTED_KEY_COUNT
        or successes != EXPECTED_SUCCESS_KEY_COUNT
        or len(failed) != EXPECTED_FAILED_KEY_COUNT
    ):
        raise RuntimeError(
            f"failure enumeration changed: total={total}, "
            f"success={successes}, failed={len(failed)}"
        )
    return tuple(failed)


def build_request(spec: FailedKey, node: BoundaryNode) -> ConditionedRadialRequest:
    return ConditionedRadialRequest(
        sector=Sector(str(spec.key["sector"])),
        ell=int(spec.key["ell"]),
        k=float(spec.key["kM"]),
        required_radius=spec.required_radius_M,
        r_out=spec.selected_r_out_M * node.r_out_factor,
        r_in_eps=node.r_in_eps,
        rtol=FIXED_RTOL,
        atol=FIXED_ATOL,
        outer_basis="jost_1_over_r",
        outer_series_order=FIXED_JOST_ORDER,
        integration_method="DOP853",
    )


def _complex_record(value: complex) -> dict[str, float]:
    record = {
        "abs": float(abs(value)),
        "imag": float(value.imag),
        "phase_rad": float(np.angle(value)),
        "real": float(value.real),
    }
    if not all(math.isfinite(item) for item in record.values()):
        raise RuntimeError("non-finite complex result")
    return record


def _state_record(result: ConditionedRadialResult) -> dict[str, Any]:
    return {
        "psi": _complex_record(complex(result.psi)),
        "dpsi_dr": _complex_record(complex(result.dpsi_dr)),
        "log_abs_psi": float(result.log_abs_psi),
        "phase_psi_rad": float(result.phase_psi),
        "log_abs_dpsi_dr": float(result.log_abs_dpsi_dr),
        "phase_dpsi_dr_rad": float(result.phase_dpsi_dr),
    }


def _run_node(spec: FailedKey, node: BoundaryNode, *, solver: Solver) -> dict[str, Any]:
    started_at = perf_counter()
    request = build_request(spec, node)
    common = {
        "node": asdict(node),
        "request": {
            "r_in_eps": request.r_in_eps,
            "r_out_M": request.r_out,
            "rtol": request.rtol,
            "atol": request.atol,
            "jost_order": request.outer_series_order,
        },
        "scientific_acceptance": False,
    }
    try:
        result = solver(request, SchwarzschildBackground(M=1.0))
        diagnostics = dict(result.diagnostics)
        required = {
            "backend": EXPECTED_BACKEND,
            "method": EXPECTED_METHOD,
            "scientific_acceptance": False,
            "independent_validation": False,
            "paper_specific_envelope_used": False,
            "legacy_path_used": False,
            "newman_penrose_path_used": False,
            "pseudoinverse_used": False,
            "riccati_variable_used": False,
        }
        for name, expected in required.items():
            if diagnostics.get(name) != expected:
                raise RuntimeError(f"scaled-tortoise provenance mismatch: {name}")
        a_out = complex(result.A_out)
        scattering = -a_out / ((-1) ** int(spec.key["ell"]))
        flux_names = (
            "flux_balance",
            "flux_residual",
            "reflection_probability",
            "horizon_transmission_probability",
        )
        flux = {
            name: _finite_float(diagnostics.get(name), label=name)
            for name in flux_names
        }
        return {
            **common,
            "status": "MEASURED",
            "failure": None,
            "A_out": _complex_record(a_out),
            "S": _complex_record(scattering),
            "S_definition": "-A_out/((-1)**ell)",
            "T_horizon": _complex_record(complex(result.T_horizon)),
            "log_abs_T_horizon": float(result.log_abs_T_horizon),
            "phase_T_horizon_rad": float(result.phase_T_horizon),
            "required_radius_state": _state_record(result),
            "flux": flux,
            "diagnostics": {
                **required,
                "outer_boundary_residual": diagnostics.get("outer_boundary_residual"),
                "match_condition_number": diagnostics.get("match_condition_number"),
                "maximum_current_relative_drift": diagnostics.get(
                    "maximum_current_relative_drift"
                ),
                "current_drift_resolved": diagnostics.get("current_drift_resolved"),
                "segment_count": diagnostics.get("segment_count"),
                "rhs_evaluations": diagnostics.get("rhs_evaluations"),
            },
            "runtime_seconds": float(perf_counter() - started_at),
        }
    except Exception as exc:  # noqa: BLE001 - failure is scientific evidence
        return {
            **common,
            "status": "FAIL",
            "failure": f"{type(exc).__name__}: {exc}",
            "runtime_seconds": float(perf_counter() - started_at),
        }


def _complex_from_node(node: Mapping[str, Any], name: str) -> complex:
    value = node[name]
    if not isinstance(value, Mapping):
        raise RuntimeError(f"node complex value is missing: {name}")
    return complex(float(value["real"]), float(value["imag"]))


def _wrapped_signed(value: float) -> float:
    return float(math.atan2(math.sin(value), math.cos(value)))


def _complex_delta(
    baseline: Mapping[str, Any], trial: Mapping[str, Any], name: str
) -> dict[str, float]:
    left = _complex_from_node(baseline, name)
    right = _complex_from_node(trial, name)
    phase = _wrapped_signed(float(np.angle(right)) - float(np.angle(left)))
    return {
        "complex_abs": float(abs(right - left)),
        "modulus_abs": float(abs(abs(right) - abs(left))),
        "wrapped_phase_rad": phase,
        "wrapped_phase_abs_rad": abs(phase),
    }


def _node_delta(
    baseline: Mapping[str, Any], trial: Mapping[str, Any]
) -> dict[str, Any]:
    base_state = baseline["required_radius_state"]
    trial_state = trial["required_radius_state"]
    if not isinstance(base_state, Mapping) or not isinstance(trial_state, Mapping):
        raise RuntimeError("required-radius state is missing")
    t_phase = _wrapped_signed(
        float(trial["phase_T_horizon_rad"]) - float(baseline["phase_T_horizon_rad"])
    )
    return {
        "S": _complex_delta(baseline, trial, "S"),
        "T_horizon": {
            **_complex_delta(baseline, trial, "T_horizon"),
            "log_abs_difference": float(
                trial["log_abs_T_horizon"] - baseline["log_abs_T_horizon"]
            ),
            "log_abs_abs_difference": float(
                abs(trial["log_abs_T_horizon"] - baseline["log_abs_T_horizon"])
            ),
            "wrapped_log_phase_rad": t_phase,
            "wrapped_log_phase_abs_rad": abs(t_phase),
        },
        "required_radius_state": {
            "psi": {
                **_complex_delta(base_state, trial_state, "psi"),
                "log_abs_difference": float(
                    trial_state["log_abs_psi"] - base_state["log_abs_psi"]
                ),
                "log_abs_abs_difference": float(
                    abs(trial_state["log_abs_psi"] - base_state["log_abs_psi"])
                ),
            },
            "dpsi_dr": {
                **_complex_delta(base_state, trial_state, "dpsi_dr"),
                "log_abs_difference": float(
                    trial_state["log_abs_dpsi_dr"] - base_state["log_abs_dpsi_dr"]
                ),
                "log_abs_abs_difference": float(
                    abs(trial_state["log_abs_dpsi_dr"] - base_state["log_abs_dpsi_dr"])
                ),
            },
        },
        "flux": {
            name: float(abs(trial["flux"][name] - baseline["flux"][name]))
            for name in (
                "flux_balance",
                "flux_residual",
                "reflection_probability",
                "horizon_transmission_probability",
            )
        },
    }


def _max_leaf(left: Any, right: Any) -> Any:
    if isinstance(left, Mapping) and isinstance(right, Mapping):
        return {name: _max_leaf(left[name], right[name]) for name in left}
    return max(abs(float(left)), abs(float(right)))


def _summarize_nodes(nodes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    measured = [node for node in nodes if node.get("status") == "MEASURED"]
    convention = {
        "status": "NOT_ASSESSED",
        "upper_bound": None,
        "reason": "absolute phase/tetrad/observer conventions are not varied",
    }
    if len(measured) != len(BOUNDARY_NODES):
        return {
            "state": "FAIL",
            "measured_node_count": len(measured),
            "failed_node_count": len(BOUNDARY_NODES) - len(measured),
            "deltas_from_baseline": {},
            "numerical_uncertainty_budget": {
                "status": "NOT_ASSESSED_INCOMPLETE_LADDER",
                "upper_bound": None,
            },
            "convention_uncertainty_budget": convention,
        }
    by_id = {str(node["node"]["node_id"]): node for node in measured}
    baseline = by_id["baseline"]
    deltas = {
        node_id: _node_delta(baseline, by_id[node_id])
        for node_id in (
            "r_in_3e-6",
            "r_in_3e-7",
            "r_out_x2",
            "r_out_x4",
        )
    }
    return {
        "state": "PARTIAL",
        "measured_node_count": len(measured),
        "failed_node_count": 0,
        "deltas_from_baseline": deltas,
        "numerical_uncertainty_budget": {
            "status": "PARTIAL",
            "upper_bound": None,
            "r_in_envelope": _max_leaf(deltas["r_in_3e-6"], deltas["r_in_3e-7"]),
            "r_out_envelope": _max_leaf(deltas["r_out_x2"], deltas["r_out_x4"]),
            "unclosed_components": [
                "tolerance ladder",
                "Jost-order ladder",
                "arbitrary-precision boundary ladder",
                "external independent comparison",
            ],
        },
        "convention_uncertainty_budget": convention,
    }


def execute_failed_key(
    spec: FailedKey,
    *,
    ordinal: int,
    solver: Solver = solve_scaled_tortoise_radial_at_radius,
) -> dict[str, Any]:
    nodes = [_run_node(spec, node, solver=solver) for node in BOUNDARY_NODES]
    return {
        "schema": KEY_RECORD_SCHEMA,
        "ordinal": ordinal,
        "key": dict(spec.key),
        "key_id": spec.key_id,
        "shard_id": spec.shard_id,
        "selected_r_out_M": spec.selected_r_out_M,
        "predecessor_failures": dict(spec.predecessor_failures),
        "predecessor_payload_identity": dict(spec.predecessor_payload_identity),
        "solver_call_count": len(BOUNDARY_NODES),
        "nodes": nodes,
        "ladder_summary": _summarize_nodes(nodes),
        "diagnostic_only": True,
        "scientific_acceptance": False,
        "global_green_permitted": False,
        "independence_role": "SAME_EQUATION_SAME_JOST_BOUNDARY_LADDER",
        "production_finite_radius_states": "NOT_ASSESSED",
    }


def _source_identities(campaign_root: Path, runner_path: Path) -> dict[str, Any]:
    paths = {
        "campaign_index": campaign_root / "conditioning_campaign_index.json",
        "campaign_manifest": campaign_root / "manifest.json",
        "boundary_ladder_module": Path(__file__).resolve(),
        "boundary_ladder_runner": runner_path.resolve(strict=True),
        "scaled_tortoise_backend": PROJECT_ROOT
        / "src/schwgw/numerics/scaled_tortoise_radial.py",
        "predecessor_conditioned_backend": PROJECT_ROOT
        / "src/schwgw/numerics/conditioned_radial.py",
        "jost_matching": PROJECT_ROOT / "src/schwgw/numerics/matching.py",
        "potentials": PROJECT_ROOT / "src/schwgw/perturbations/potentials.py",
        "schwarzschild_background": PROJECT_ROOT
        / "src/schwgw/backgrounds/schwarzschild.py",
    }
    return {name: _identity(path) for name, path in sorted(paths.items())}


def _build_contract(
    *,
    campaign_root: Path,
    failed_keys: Sequence[FailedKey],
    selected: Sequence[FailedKey],
    runner_path: Path,
    limit: int | None,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign_role": "failed_domain_pole_safe_boundary_ladder_diagnostic",
        "campaign_root": str(campaign_root),
        "predecessor_failed_key_count": len(failed_keys),
        "predecessor_success_key_count": EXPECTED_SUCCESS_KEY_COUNT,
        "failed_key_inventory_sha256": _sha256_bytes(
            _canonical_bytes([spec.inventory_record() for spec in failed_keys])
        ),
        "selected_key_count": len(selected),
        "selected_key_inventory_sha256": _sha256_bytes(
            _canonical_bytes([spec.inventory_record() for spec in selected])
        ),
        "ladder_nodes": [asdict(node) for node in BOUNDARY_NODES],
        "fixed_solver_configuration": {
            "rtol": FIXED_RTOL,
            "atol": FIXED_ATOL,
            "jost_order": FIXED_JOST_ORDER,
            "outer_basis": "jost_1_over_r",
        },
        "expected_solver_call_count": len(selected) * len(BOUNDARY_NODES),
        "limit": limit,
        "source_identities": _source_identities(campaign_root, runner_path),
        "runtime": {
            "implementation": platform.python_implementation(),
            "python": sys.version,
            "python_executable": sys.executable,
            "python_3_14": sys.version_info[:2] == (3, 14),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
        },
        "resume_protocol": (
            "canonical prefix-validated JSONL; append and fsync per key; "
            "kernel-held single-writer lock"
        ),
        "diagnostic_only": True,
        "science_executed": True,
        "scientific_acceptance": False,
        "global_green_permitted": False,
        "li_figure_agreement_primary_gate": False,
        "full_paper_figure_rerun": False,
        "production_finite_radius_states": "NOT_ASSESSED",
        "convention_uncertainty": "NOT_ASSESSED",
    }


def _validate_resume_contract(
    existing: Mapping[str, Any], expected: Mapping[str, Any]
) -> None:
    ignored = {"created_at_utc"}
    if {key: value for key, value in existing.items() if key not in ignored} != {
        key: value for key, value in expected.items() if key not in ignored
    }:
        raise RuntimeError("resume contract or source identities changed")


def _read_records(path: Path, selected: Sequence[FailedKey]) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    if not raw:
        return []
    records: list[dict[str, Any]] = []
    for index, line in enumerate(raw.splitlines(keepends=True)):
        if not line.endswith(b"\n"):
            raise RuntimeError("records.jsonl has an incomplete trailing record")
        value = json.loads(line)
        if not isinstance(value, dict) or line != _canonical_bytes(value):
            raise RuntimeError(f"invalid canonical record at line {index + 1}")
        if index >= len(selected):
            raise RuntimeError("records.jsonl exceeds selected inventory")
        expected = selected[index]
        if (
            value.get("schema") != KEY_RECORD_SCHEMA
            or value.get("ordinal") != index + 1
            or value.get("key_id") != expected.key_id
            or value.get("key") != dict(expected.key)
            or value.get("predecessor_payload_identity")
            != dict(expected.predecessor_payload_identity)
            or value.get("ladder_summary", {}).get("state") not in {"PARTIAL", "FAIL"}
            or value.get("scientific_acceptance") is not False
        ):
            raise RuntimeError(f"record prefix mismatch at line {index + 1}")
        records.append(value)
    return records


def _progress(
    *, selected_count: int, records: Sequence[Mapping[str, Any]], started_at: float
) -> dict[str, Any]:
    states = Counter(str(record["ladder_summary"]["state"]) for record in records)
    return {
        "schema": f"{SCHEMA}_progress",
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "selected_key_count": selected_count,
        "completed_key_count": len(records),
        "remaining_key_count": selected_count - len(records),
        "key_state_counts": dict(sorted(states.items())),
        "elapsed_this_invocation_seconds": float(perf_counter() - started_at),
        "terminal": len(records) == selected_count,
        "scientific_acceptance": False,
        "global_green_permitted": False,
    }


def _iter_numeric_leaves(value: Any, prefix: str = "") -> list[tuple[str, float]]:
    if isinstance(value, Mapping):
        leaves: list[tuple[str, float]] = []
        for name, child in value.items():
            path = f"{prefix}.{name}" if prefix else str(name)
            leaves.extend(_iter_numeric_leaves(child, path))
        return leaves
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return [(prefix, abs(float(value)))]
    return []


def _summary(records: Sequence[Mapping[str, Any]], started_at: float) -> dict[str, Any]:
    states = Counter(str(record["ladder_summary"]["state"]) for record in records)
    node_statuses = Counter(
        str(node["status"]) for record in records for node in record["nodes"]
    )
    maxima: dict[str, float] = {}
    for record in records:
        deltas = record["ladder_summary"].get("deltas_from_baseline", {})
        for path, value in _iter_numeric_leaves(deltas):
            maxima[path] = max(maxima.get(path, 0.0), value)
    return {
        "schema": SUMMARY_SCHEMA,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "selected_key_count": len(records),
        "completed_key_count": len(records),
        "solver_call_count": len(records) * len(BOUNDARY_NODES),
        "key_state_counts": dict(sorted(states.items())),
        "node_status_counts": dict(sorted(node_statuses.items())),
        "overall_state": "FAIL" if states.get("FAIL") else "PARTIAL",
        "maximum_observed_boundary_deltas": dict(sorted(maxima.items())),
        "numerical_uncertainty_budget": {
            "status": "PARTIAL" if not states.get("FAIL") else "INCOMPLETE",
            "upper_bound": None,
            "observed_maxima_are_not_acceptance_thresholds": True,
        },
        "convention_uncertainty_budget": {
            "status": "NOT_ASSESSED",
            "upper_bound": None,
        },
        "scope": "selected subset of exact 5,798 predecessor fail-closed keys",
        "same_implementation_family": True,
        "independent_scientific_validation": False,
        "diagnostic_only": True,
        "science_executed": True,
        "scientific_acceptance": False,
        "global_green_permitted": False,
        "production_finite_radius_states": "NOT_ASSESSED",
        "elapsed_this_invocation_seconds": float(perf_counter() - started_at),
    }


def _prepare_root(output_root: Path, *, resume: bool) -> Path:
    absolute = output_root.absolute()
    parent = absolute.parent.resolve(strict=True)
    root = parent / absolute.name
    if resume:
        if not root.is_dir() or root.is_symlink():
            raise RuntimeError("--resume requires an existing regular output root")
        if stat.S_IMODE(root.stat().st_mode) == 0o555:
            raise RuntimeError("output root is already sealed")
    else:
        if root.exists() or root.is_symlink():
            raise RuntimeError("fresh output root already exists")
        os.mkdir(root, mode=0o700)
        _fsync_directory(parent)
    return root


def _seal(root: Path) -> None:
    for path in root.iterdir():
        if not path.is_file() or path.is_symlink() or path.stat().st_nlink != 1:
            raise RuntimeError(f"cannot seal non-regular artifact: {path}")
        path.chmod(0o444)
    root.chmod(0o555)
    _fsync_directory(root)
    _fsync_directory(root.parent)


def validate_terminal_root(root: Path) -> dict[str, Any]:
    resolved = root.resolve(strict=True)
    if stat.S_IMODE(resolved.stat().st_mode) != 0o555:
        raise RuntimeError("terminal boundary-ladder root must be 0555")
    expected = {
        "manifest.json",
        "progress.json",
        "records.jsonl",
        "run_contract.json",
        "summary.json",
        "writer.lock",
    }
    if {path.name for path in resolved.iterdir()} != expected:
        raise RuntimeError("terminal boundary-ladder inventory changed")
    for path in resolved.iterdir():
        identity = _identity(path)
        if identity["mode"] != 0o444 or identity["nlink"] != 1:
            raise RuntimeError(f"terminal artifact is not 0444/nlink1: {path}")
    manifest = _load_json(resolved / "manifest.json", canonical=True)
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise RuntimeError("boundary-ladder manifest schema changed")
    files = manifest.get("files")
    if not isinstance(files, Mapping) or set(files) != expected - {"manifest.json"}:
        raise RuntimeError("boundary-ladder manifest identities changed")
    for name, identity in files.items():
        if not isinstance(identity, Mapping):
            raise RuntimeError("boundary-ladder identity is malformed")
        _validate_identity(identity, resolved / str(name))
    contract = _load_json(resolved / "run_contract.json", canonical=True)
    summary = _load_json(resolved / "summary.json", canonical=True)
    progress = _load_json(resolved / "progress.json", canonical=True)
    selected = int(contract.get("selected_key_count", -1))
    if (
        contract.get("schema") != SCHEMA
        or contract.get("predecessor_failed_key_count") != EXPECTED_FAILED_KEY_COUNT
        or contract.get("scientific_acceptance") is not False
        or contract.get("convention_uncertainty") != "NOT_ASSESSED"
        or summary.get("schema") != SUMMARY_SCHEMA
        or summary.get("overall_state") not in {"PARTIAL", "FAIL"}
        or summary.get("scientific_acceptance") is not False
        or progress.get("terminal") is not True
        or len((resolved / "records.jsonl").read_bytes().splitlines()) != selected
        or summary.get("completed_key_count") != selected
        or summary.get("solver_call_count") != selected * len(BOUNDARY_NODES)
    ):
        raise RuntimeError("terminal boundary-ladder accounting or policy changed")
    return {
        "root": str(resolved),
        "selected_key_count": selected,
        "solver_call_count": summary["solver_call_count"],
        "overall_state": summary["overall_state"],
        "key_state_counts": summary["key_state_counts"],
        "node_status_counts": summary["node_status_counts"],
        "maximum_observed_boundary_deltas": summary["maximum_observed_boundary_deltas"],
        "manifest_sha256": _sha256_file(resolved / "manifest.json"),
        "records_sha256": _sha256_file(resolved / "records.jsonl"),
    }


def run(
    *,
    output_root: Path,
    runner_path: Path,
    campaign_root: Path = DEFAULT_CAMPAIGN_ROOT,
    limit: int | None = None,
    resume: bool = False,
    solver: Solver = solve_scaled_tortoise_radial_at_radius,
) -> dict[str, Any]:
    started_at = perf_counter()
    campaign = campaign_root.resolve(strict=True)
    failed_keys = discover_failed_keys(campaign)
    if limit is not None and not 1 <= limit <= EXPECTED_FAILED_KEY_COUNT:
        raise ValueError(f"limit must be in [1, {EXPECTED_FAILED_KEY_COUNT}]")
    selected = failed_keys if limit is None else failed_keys[:limit]
    contract = _build_contract(
        campaign_root=campaign,
        failed_keys=failed_keys,
        selected=selected,
        runner_path=runner_path,
        limit=limit,
    )
    root = _prepare_root(output_root, resume=resume)
    with _WriterGuard(root / "writer.lock", resume=resume) as guard:
        guard.write_state("ACTIVE", resume=resume)
        try:
            contract_path = root / "run_contract.json"
            records_path = root / "records.jsonl"
            progress_path = root / "progress.json"
            if resume:
                _validate_resume_contract(
                    _load_json(contract_path, canonical=True), contract
                )
            else:
                _write_exclusive(contract_path, contract)
                _create_empty_exclusive(records_path)
            records = _read_records(records_path, selected)
            _write_atomic(
                progress_path,
                _progress(
                    selected_count=len(selected),
                    records=records,
                    started_at=started_at,
                ),
            )
            for index in range(len(records), len(selected)):
                record = execute_failed_key(
                    selected[index], ordinal=index + 1, solver=solver
                )
                _append_fsynced(records_path, record)
                records.append(record)
                _write_atomic(
                    progress_path,
                    _progress(
                        selected_count=len(selected),
                        records=records,
                        started_at=started_at,
                    ),
                )
            records = _read_records(records_path, selected)
            if len(records) != len(selected):
                raise RuntimeError("terminal record count changed")
            summary = _summary(records, started_at)
            _write_exclusive(root / "summary.json", summary)
            _write_atomic(
                progress_path,
                _progress(
                    selected_count=len(selected),
                    records=records,
                    started_at=started_at,
                ),
            )
            guard.write_state(
                "TERMINAL", completed_key_count=len(records), resume=resume
            )
            inputs = (
                "progress.json",
                "records.jsonl",
                "run_contract.json",
                "summary.json",
                "writer.lock",
            )
            try:
                for name in inputs:
                    (root / name).chmod(0o444)
                manifest = {
                    "schema": MANIFEST_SCHEMA,
                    "created_at_utc": datetime.now(timezone.utc).isoformat(),
                    "files": {name: _identity(root / name) for name in inputs},
                    "selected_key_count": len(selected),
                    "overall_state": summary["overall_state"],
                    "scientific_acceptance": False,
                    "global_green_permitted": False,
                }
                _write_exclusive(root / "manifest.json", manifest)
                _seal(root)
            except BaseException:
                for path in root.iterdir():
                    if path.is_file() and not path.is_symlink():
                        path.chmod(0o644)
                raise
        except BaseException:
            guard.write_state("INTERRUPTED_OR_FAILED", resume=resume)
            _fsync_directory(root)
            raise
    return validate_terminal_root(root)


def require_exact_cpython314() -> None:
    if platform.python_implementation() != "CPython" or sys.version_info[:2] != (
        3,
        14,
    ):
        raise RuntimeError("boundary-ladder evidence requires exact CPython 3.14")


__all__ = [
    "BOUNDARY_NODES",
    "DEFAULT_CAMPAIGN_ROOT",
    "EXPECTED_FAILED_KEY_COUNT",
    "FailedKey",
    "SCHEMA",
    "build_request",
    "discover_failed_keys",
    "execute_failed_key",
    "require_exact_cpython314",
    "run",
    "validate_terminal_root",
]
