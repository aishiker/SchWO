"""Resumable successful-domain continuity diagnostics for Phase-6 V1.

The diagnostic reloads the immutable 86-shard conditioning campaign, selects
its exact 12,020 ``COMPLETED``/``PARTIAL`` keys, and evaluates each baseline
configuration once with the isolated scaled-tortoise backend.  It compares
the new result with the predecessor payload without defining an acceptance
threshold or changing the frozen V1 evidence.

This is a same-equation, same-Jost-basis implementation continuity check.  It
is not an independent scientific validation and cannot establish a convention
budget, an observer response, or a global GREEN state.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
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

SCHEMA = "schwgw_phase6_v1_radial_success_continuity_diagnostic_v1"
KEY_RECORD_SCHEMA = f"{SCHEMA}_key_record"
SUMMARY_SCHEMA = f"{SCHEMA}_summary"
MANIFEST_SCHEMA = f"{SCHEMA}_manifest"
EXPECTED_SUCCESS_KEY_COUNT = 12_020
EXPECTED_FAILURE_KEY_COUNT = 5_798
EXPECTED_BACKEND = "scipy_float64_scaled_tortoise_radial_repair_v1"
EXPECTED_METHOD = "scaled_tortoise_full_state_jost_ratio"

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CAMPAIGN_ROOT = (
    PROJECT_ROOT / "runs/phase6/radial_validation/"
    "v1_conditioning_campaign_v1_20260808_py314"
)

Solver = Callable[
    [ConditionedRadialRequest, SchwarzschildBackground], ConditionedRadialResult
]


@dataclass(frozen=True)
class SuccessfulKey:
    """One fully provenance-bound predecessor baseline configuration."""

    key: Mapping[str, Any]
    key_id: str
    shard_id: str
    predecessor_payload_identity: Mapping[str, Any]
    required_radius_M: float
    r_out_M: float
    r_in_eps: float
    rtol: float
    atol: float
    jost_order: int
    predecessor_A_out: complex
    predecessor_T_horizon: complex
    predecessor_log_abs_T: float
    predecessor_phase_T: float
    predecessor_flux_residual: float
    predecessor_flux_balance: float
    predecessor_reflection_probability: float
    predecessor_transmission_probability: float
    predecessor_numerical_budget: Mapping[str, Any]
    predecessor_convention_budget: Mapping[str, Any]

    def inventory_record(self) -> dict[str, Any]:
        """Return the stable fields that bind enumeration and resume order."""

        return {
            "key": dict(self.key),
            "key_id": self.key_id,
            "payload_sha256": self.predecessor_payload_identity["sha256"],
            "r_out_M": self.r_out_M,
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
    """A persistent audit file backed by a kernel nonblocking exclusive lock."""

    def __init__(self, path: Path, *, resume: bool) -> None:
        self.path = path
        flags = os.O_RDWR
        if resume:
            flags |= 0
        else:
            flags |= os.O_CREAT | os.O_EXCL
        self._descriptor = os.open(path, flags, 0o644)
        try:
            fcntl.flock(self._descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            os.close(self._descriptor)
            raise RuntimeError("output root already has an active writer") from exc
        self._stream = os.fdopen(self._descriptor, "r+b", buffering=0)
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
            "single_writer_mechanism": "fcntl.flock(LOCK_EX|LOCK_NB)",
            "single_writer_enforced": True,
            **extra,
        }
        if self._previous is not None:
            record["resumed_after"] = {
                "pid": self._previous.get("pid"),
                "state": self._previous.get("state"),
                "updated_at_utc": self._previous.get("updated_at_utc"),
            }
        payload = _canonical_bytes(record)
        self._stream.seek(0)
        self._stream.truncate(0)
        self._stream.write(payload)
        self._stream.flush()
        os.fsync(self._stream.fileno())

    def close(self) -> None:
        try:
            fcntl.flock(self._stream.fileno(), fcntl.LOCK_UN)
        finally:
            self._stream.close()

    def __enter__(self) -> _WriterGuard:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def _key_id(key: Mapping[str, Any]) -> str:
    return f"kM={key['kM']};sector={key['sector']};ell={int(key['ell'])}"


def _key_sort(spec: SuccessfulKey) -> tuple[Decimal, int, int]:
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


def _complex_from_record(value: Any, *, label: str) -> complex:
    if not isinstance(value, Mapping) or set(value) != {"abs", "imag", "real"}:
        raise RuntimeError(f"{label} has an invalid complex record")
    result = complex(
        _finite_float(value["real"], label=f"{label}.real"),
        _finite_float(value["imag"], label=f"{label}.imag"),
    )
    recorded_abs = _finite_float(value["abs"], label=f"{label}.abs")
    if not math.isclose(abs(result), recorded_abs, rel_tol=5.0e-15, abs_tol=5.0e-324):
        raise RuntimeError(f"{label} modulus is internally inconsistent")
    return result


def _mapping_copy(value: Any, *, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise RuntimeError(f"{label} is not an object")
    return json.loads(json.dumps(value, allow_nan=False))


def _successful_spec(
    *, payload_path: Path, envelope: Mapping[str, Any], shard_id: str
) -> SuccessfulKey | None:
    if (
        envelope.get("schema") != KEY_PAYLOAD_ENVELOPE_SCHEMA
        or envelope.get("solver_payload_schema") != SOLVER_PAYLOAD_SCHEMA
    ):
        raise RuntimeError(f"conditioning payload envelope changed: {payload_path}")
    solver_payload = envelope.get("solver_payload")
    if not isinstance(solver_payload, Mapping):
        raise RuntimeError(f"missing solver payload: {payload_path}")
    acceptance = solver_payload.get("acceptance_state")
    if acceptance == "FAIL":
        return None
    if acceptance != "PARTIAL" or solver_payload.get("failures") != {}:
        raise RuntimeError(f"unexpected successful-key state: {payload_path}")
    key = _mapping_copy(envelope.get("key"), label="key")
    if solver_payload.get("key") != key:
        raise RuntimeError(f"solver/envelope key mismatch: {payload_path}")
    key_record = {
        "ell": int(key.get("ell")),
        "kM": str(key.get("kM")),
        "sector": str(key.get("sector")),
    }
    if key_record["sector"] not in {"odd", "even"} or key_record["ell"] < 2:
        raise RuntimeError(f"invalid radial key: {payload_path}")

    results = solver_payload.get("results")
    if not isinstance(results, Mapping) or "baseline" not in results:
        raise RuntimeError(f"successful payload has no baseline: {payload_path}")
    baseline = results["baseline"]
    if not isinstance(baseline, Mapping) or baseline.get("key") != key_record:
        raise RuntimeError(f"baseline key mismatch: {payload_path}")
    configuration = baseline.get("configuration")
    diagnostics = baseline.get("diagnostics")
    log_phase = baseline.get("log_phase")
    scope = solver_payload.get("scope_qualification")
    outer = solver_payload.get("outer_selection")
    for name, value in (
        ("configuration", configuration),
        ("diagnostics", diagnostics),
        ("log_phase", log_phase),
        ("scope", scope),
        ("outer_selection", outer),
    ):
        if not isinstance(value, Mapping):
            raise RuntimeError(f"baseline {name} missing: {payload_path}")
    if (
        configuration.get("axis") != "baseline"
        or configuration.get("node_id") != "baseline"
        or configuration.get("is_baseline") is not True
        or outer.get("status") != "SUPPORTED"
    ):
        raise RuntimeError(f"baseline configuration changed: {payload_path}")
    required_radius = _finite_float(
        scope.get("required_radius_M"), label="required_radius_M"
    )
    r_out = _finite_float(configuration.get("r_out_M"), label="r_out_M")
    if r_out != _finite_float(outer.get("selected_r_out_M"), label="selected_r_out_M"):
        raise RuntimeError(f"baseline r_out selection mismatch: {payload_path}")
    if required_radius != _finite_float(
        diagnostics.get("required_radius"), label="diagnostic required_radius"
    ):
        raise RuntimeError(f"required-radius metadata mismatch: {payload_path}")
    if (
        diagnostics.get("backend") != "scipy_float64_conditioned_radial_v1"
        or diagnostics.get("outer_basis") != "jost_1_over_r"
        or diagnostics.get("scientific_acceptance") is not False
    ):
        raise RuntimeError(f"predecessor backend provenance changed: {payload_path}")

    return SuccessfulKey(
        key=key_record,
        key_id=_key_id(key_record),
        shard_id=shard_id,
        predecessor_payload_identity=_identity(payload_path),
        required_radius_M=required_radius,
        r_out_M=r_out,
        r_in_eps=_finite_float(configuration.get("r_in_eps"), label="r_in_eps"),
        rtol=_finite_float(configuration.get("rtol"), label="rtol"),
        atol=_finite_float(configuration.get("atol"), label="atol"),
        jost_order=int(configuration.get("jost_order")),
        predecessor_A_out=_complex_from_record(
            baseline.get("A_out"), label="baseline.A_out"
        ),
        predecessor_T_horizon=_complex_from_record(
            baseline.get("T_horizon"), label="baseline.T_horizon"
        ),
        predecessor_log_abs_T=_finite_float(
            log_phase.get("log_abs_T_horizon"), label="log_abs_T_horizon"
        ),
        predecessor_phase_T=_finite_float(
            log_phase.get("phase_T_horizon"), label="phase_T_horizon"
        ),
        predecessor_flux_residual=_finite_float(
            diagnostics.get("flux_residual"), label="flux_residual"
        ),
        predecessor_flux_balance=_finite_float(
            diagnostics.get("flux_balance"), label="flux_balance"
        ),
        predecessor_reflection_probability=_finite_float(
            diagnostics.get("reflection_probability"),
            label="reflection_probability",
        ),
        predecessor_transmission_probability=_finite_float(
            diagnostics.get("horizon_transmission_probability"),
            label="horizon_transmission_probability",
        ),
        predecessor_numerical_budget=_mapping_copy(
            solver_payload.get("numerical_budget"), label="numerical_budget"
        ),
        predecessor_convention_budget=_mapping_copy(
            solver_payload.get("convention_budget"), label="convention_budget"
        ),
    )


def discover_successful_keys(campaign_root: Path) -> tuple[SuccessfulKey, ...]:
    """Live-rebuild the immutable campaign and enumerate exactly 12,020 keys."""

    root = campaign_root.resolve(strict=True)
    validate_published_conditioning_campaign(root)
    index = _load_json(root / "conditioning_campaign_index.json", canonical=True)
    if (
        index.get("schema") != CAMPAIGN_INDEX_SCHEMA
        or index.get("coverage", {}).get("D_union_exact_coverage") is not True
        or index.get("coverage", {}).get("key_count") != EXPECTED_KEY_COUNT
        or index.get("coverage", {}).get("shard_count") != EXPECTED_SHARD_COUNT
        or index.get("terminal_completion_counts")
        != {
            "COMPLETED": EXPECTED_SUCCESS_KEY_COUNT,
            "COMPLETED_FAIL_CLOSED": EXPECTED_FAILURE_KEY_COUNT,
        }
        or index.get("production_finite_radius_states") != "NOT_ASSESSED"
        or index.get("global_green_permitted") is not False
    ):
        raise RuntimeError("conditioning campaign coverage or policy changed")
    raw_shards = index.get("shards")
    if not isinstance(raw_shards, Sequence) or len(raw_shards) != EXPECTED_SHARD_COUNT:
        raise RuntimeError("conditioning campaign shard inventory changed")

    specs: list[SuccessfulKey] = []
    total_payloads = 0
    fail_closed = 0
    seen: set[str] = set()
    for shard in raw_shards:
        if not isinstance(shard, Mapping):
            raise RuntimeError("conditioning campaign shard entry is malformed")
        shard_record = shard.get("shard")
        if not isinstance(shard_record, Mapping):
            raise RuntimeError("conditioning campaign shard identity is missing")
        shard_id = str(shard_record.get("shard_id"))
        shard_root = Path(str(shard.get("root"))).resolve(strict=True)
        payload_paths = sorted(shard_root.glob("key_*__payload.json"))
        if len(payload_paths) != int(shard_record.get("key_count", -1)):
            raise RuntimeError(f"payload inventory changed for {shard_id}")
        for payload_path in payload_paths:
            total_payloads += 1
            envelope = _load_json(payload_path, canonical=True)
            spec = _successful_spec(
                payload_path=payload_path,
                envelope=envelope,
                shard_id=shard_id,
            )
            if spec is None:
                fail_closed += 1
                continue
            if spec.key_id in seen:
                raise RuntimeError(f"duplicate successful key: {spec.key_id}")
            seen.add(spec.key_id)
            specs.append(spec)
    specs.sort(key=_key_sort)
    if (
        total_payloads != EXPECTED_KEY_COUNT
        or fail_closed != EXPECTED_FAILURE_KEY_COUNT
        or len(specs) != EXPECTED_SUCCESS_KEY_COUNT
    ):
        raise RuntimeError(
            "conditioning successful-domain enumeration changed: "
            f"total={total_payloads}, success={len(specs)}, fail={fail_closed}"
        )
    return tuple(specs)


def _complex_record(value: complex) -> dict[str, float]:
    values = {
        "abs": float(abs(value)),
        "imag": float(value.imag),
        "phase_rad": float(np.angle(value)),
        "real": float(value.real),
    }
    if not all(math.isfinite(item) for item in values.values()):
        raise RuntimeError("backend returned a non-finite complex value")
    return values


def _wrapped_signed(value: float) -> float:
    return float(math.atan2(math.sin(value), math.cos(value)))


def _retained_diagnostics(result: ConditionedRadialResult) -> dict[str, Any]:
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
    retained_names = {
        *required,
        "actual_precision_bits",
        "atol",
        "current_drift_resolved",
        "flux_balance",
        "flux_residual",
        "horizon_transmission_probability",
        "match_condition_number",
        "maximum_current_relative_drift",
        "outer_basis",
        "outer_boundary_residual",
        "outer_series_order",
        "reflection_probability",
        "rhs_evaluations",
        "r_in",
        "r_out",
        "rtol",
        "runtime_seconds",
        "segment_count",
        "transmission_resolved_in_float64_balance",
        "unresolved_current_segment_count",
    }
    return {
        name: diagnostics[name]
        for name in sorted(retained_names)
        if name in diagnostics
    }


def build_request(spec: SuccessfulKey) -> ConditionedRadialRequest:
    """Reproduce the exact predecessor baseline numerical configuration."""

    return ConditionedRadialRequest(
        sector=Sector(str(spec.key["sector"])),
        ell=int(spec.key["ell"]),
        k=float(spec.key["kM"]),
        required_radius=spec.required_radius_M,
        r_out=spec.r_out_M,
        r_in_eps=spec.r_in_eps,
        rtol=spec.rtol,
        atol=spec.atol,
        outer_basis="jost_1_over_r",
        outer_series_order=spec.jost_order,
        integration_method="DOP853",
    )


def compare_successful_key(
    spec: SuccessfulKey,
    *,
    ordinal: int,
    solver: Solver = solve_scaled_tortoise_radial_at_radius,
) -> dict[str, Any]:
    """Run one baseline and preserve success as PARTIAL or errors as FAIL."""

    started_at = perf_counter()
    common: dict[str, Any] = {
        "schema": KEY_RECORD_SCHEMA,
        "ordinal": ordinal,
        "key": dict(spec.key),
        "key_id": spec.key_id,
        "shard_id": spec.shard_id,
        "predecessor_payload_identity": dict(spec.predecessor_payload_identity),
        "solver_call_count": 1,
        "diagnostic_only": True,
        "scientific_acceptance": False,
        "global_green_permitted": False,
        "independence_role": "SAME_EQUATION_SAME_JOST_IMPLEMENTATION_CONTINUITY",
        "convention_uncertainty_budget": {
            "status": "NOT_ASSESSED",
            "upper_bound": None,
            "predecessor_budget": dict(spec.predecessor_convention_budget),
            "reason": "absolute phase/tetrad/observer convention not independently fixed",
        },
    }
    try:
        request = build_request(spec)
        result = solver(request, SchwarzschildBackground(M=1.0))
        diagnostics = _retained_diagnostics(result)
        new_A_out = complex(result.A_out)
        new_T = complex(result.T_horizon)
        a_delta = new_A_out - spec.predecessor_A_out
        a_phase_delta = _wrapped_signed(
            float(np.angle(new_A_out)) - float(np.angle(spec.predecessor_A_out))
        )
        t_phase_delta = _wrapped_signed(
            float(result.phase_T_horizon) - spec.predecessor_phase_T
        )
        new_flux_residual = _finite_float(
            diagnostics.get("flux_residual"), label="new flux_residual"
        )
        new_flux_balance = _finite_float(
            diagnostics.get("flux_balance"), label="new flux_balance"
        )
        new_reflection = _finite_float(
            diagnostics.get("reflection_probability"),
            label="new reflection_probability",
        )
        new_transmission = _finite_float(
            diagnostics.get("horizon_transmission_probability"),
            label="new transmission_probability",
        )
        comparison = {
            "A_out": {
                "complex_abs_difference": float(abs(a_delta)),
                "difference": _complex_record(a_delta),
                "modulus_abs_difference": float(
                    abs(abs(new_A_out) - abs(spec.predecessor_A_out))
                ),
                "wrapped_phase_difference_rad": a_phase_delta,
                "wrapped_phase_abs_difference_rad": abs(a_phase_delta),
            },
            "T_horizon": {
                "complex_abs_difference": float(
                    abs(new_T - spec.predecessor_T_horizon)
                ),
                "log_abs_difference": float(
                    result.log_abs_T_horizon - spec.predecessor_log_abs_T
                ),
                "log_abs_abs_difference": float(
                    abs(result.log_abs_T_horizon - spec.predecessor_log_abs_T)
                ),
                "wrapped_phase_difference_rad": t_phase_delta,
                "wrapped_phase_abs_difference_rad": abs(t_phase_delta),
            },
            "flux": {
                "balance_abs_difference": float(
                    abs(new_flux_balance - spec.predecessor_flux_balance)
                ),
                "reflection_probability_abs_difference": float(
                    abs(new_reflection - spec.predecessor_reflection_probability)
                ),
                "residual_abs_difference": float(
                    abs(new_flux_residual - spec.predecessor_flux_residual)
                ),
                "transmission_probability_abs_difference": float(
                    abs(new_transmission - spec.predecessor_transmission_probability)
                ),
            },
        }
        common.update(
            {
                "status": "PARTIAL",
                "failure": None,
                "request": {
                    "atol": request.atol,
                    "jost_order": request.outer_series_order,
                    "r_in_eps": request.r_in_eps,
                    "r_out_M": request.r_out,
                    "required_radius_M": request.required_radius,
                    "rtol": request.rtol,
                },
                "predecessor": {
                    "A_out": _complex_record(spec.predecessor_A_out),
                    "T_horizon": _complex_record(spec.predecessor_T_horizon),
                    "flux_balance": spec.predecessor_flux_balance,
                    "flux_residual": spec.predecessor_flux_residual,
                    "log_abs_T_horizon": spec.predecessor_log_abs_T,
                    "phase_T_horizon": spec.predecessor_phase_T,
                    "reflection_probability": spec.predecessor_reflection_probability,
                    "transmission_probability": (
                        spec.predecessor_transmission_probability
                    ),
                },
                "candidate": {
                    "A_out": _complex_record(new_A_out),
                    "T_horizon": _complex_record(new_T),
                    "diagnostics": diagnostics,
                    "flux_balance": new_flux_balance,
                    "flux_residual": new_flux_residual,
                    "log_abs_T_horizon": float(result.log_abs_T_horizon),
                    "phase_T_horizon": float(result.phase_T_horizon),
                    "reflection_probability": new_reflection,
                    "transmission_probability": new_transmission,
                },
                "comparison": comparison,
                "numerical_uncertainty_budget": {
                    "status": "PARTIAL",
                    "upper_bound": None,
                    "predecessor_budget": dict(spec.predecessor_numerical_budget),
                    "measured_same_configuration_differences": comparison,
                    "unclosed_components": [
                        "candidate tolerance ladder",
                        "candidate Jost-order ladder",
                        "candidate r_in/r_out ladder",
                        "independent arbitrary-precision comparison",
                    ],
                },
                "runtime_seconds": float(perf_counter() - started_at),
            }
        )
    except Exception as exc:  # noqa: BLE001 - retain every scientific failure
        common.update(
            {
                "status": "FAIL",
                "failure": f"{type(exc).__name__}: {exc}",
                "request": None,
                "predecessor": None,
                "candidate": None,
                "comparison": None,
                "numerical_uncertainty_budget": {
                    "status": "NOT_ASSESSED_SOLVER_FAILURE",
                    "upper_bound": None,
                    "predecessor_budget": dict(spec.predecessor_numerical_budget),
                },
                "runtime_seconds": float(perf_counter() - started_at),
            }
        )
    return common


def _source_identities(campaign_root: Path, runner_path: Path) -> dict[str, Any]:
    paths = {
        "campaign_index": campaign_root / "conditioning_campaign_index.json",
        "campaign_manifest": campaign_root / "manifest.json",
        "continuity_module": Path(__file__).resolve(),
        "continuity_runner": runner_path.resolve(strict=True),
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
    successful_keys: Sequence[SuccessfulKey],
    selected: Sequence[SuccessfulKey],
    limit: int | None,
    runner_path: Path,
) -> dict[str, Any]:
    full_inventory = [spec.inventory_record() for spec in successful_keys]
    selected_inventory = [spec.inventory_record() for spec in selected]
    return {
        "schema": SCHEMA,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign_role": "successful_domain_implementation_continuity_diagnostic",
        "campaign_root": str(campaign_root),
        "predecessor_completed_partial_key_count": len(successful_keys),
        "predecessor_fail_closed_key_count": EXPECTED_FAILURE_KEY_COUNT,
        "successful_key_inventory_sha256": _sha256_bytes(
            _canonical_bytes(full_inventory)
        ),
        "selected_key_count": len(selected),
        "selected_key_inventory_sha256": _sha256_bytes(
            _canonical_bytes(selected_inventory)
        ),
        "expected_solver_call_count": len(selected),
        "one_baseline_solve_per_key": True,
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
            "canonical prefix-validated JSONL; append and fsync once per key; "
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
        raise RuntimeError("resume contract or implementation source identity changed")


def _read_records(
    path: Path, selected: Sequence[SuccessfulKey]
) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    if not raw:
        return []
    lines = raw.splitlines(keepends=True)
    records: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        if not line.endswith(b"\n"):
            raise RuntimeError("records.jsonl has an incomplete trailing record")
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"invalid records.jsonl line {index + 1}") from exc
        if not isinstance(record, dict) or line != _canonical_bytes(record):
            raise RuntimeError(f"non-canonical records.jsonl line {index + 1}")
        if index >= len(selected):
            raise RuntimeError("records.jsonl exceeds selected inventory")
        expected = selected[index]
        if (
            record.get("schema") != KEY_RECORD_SCHEMA
            or record.get("ordinal") != index + 1
            or record.get("key_id") != expected.key_id
            or record.get("key") != dict(expected.key)
            or record.get("predecessor_payload_identity")
            != dict(expected.predecessor_payload_identity)
            or record.get("status") not in {"PARTIAL", "FAIL"}
            or record.get("scientific_acceptance") is not False
            or record.get("global_green_permitted") is not False
        ):
            raise RuntimeError(f"records.jsonl prefix mismatch at line {index + 1}")
        records.append(record)
    return records


def _progress(
    *, selected_count: int, records: Sequence[Mapping[str, Any]], started_at: float
) -> dict[str, Any]:
    states = Counter(str(record["status"]) for record in records)
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


def _maximum(records: Sequence[Mapping[str, Any]], path: Sequence[str]) -> float | None:
    values: list[float] = []
    for record in records:
        current: Any = record
        for name in path:
            if not isinstance(current, Mapping) or name not in current:
                current = None
                break
            current = current[name]
        if isinstance(current, (int, float)) and math.isfinite(float(current)):
            values.append(float(current))
    return max(values) if values else None


def _summary(records: Sequence[Mapping[str, Any]], started_at: float) -> dict[str, Any]:
    counts = Counter(str(record["status"]) for record in records)
    maxima = {
        "A_out_complex_abs_difference": _maximum(
            records, ("comparison", "A_out", "complex_abs_difference")
        ),
        "A_out_modulus_abs_difference": _maximum(
            records, ("comparison", "A_out", "modulus_abs_difference")
        ),
        "A_out_wrapped_phase_abs_difference_rad": _maximum(
            records,
            ("comparison", "A_out", "wrapped_phase_abs_difference_rad"),
        ),
        "T_log_abs_abs_difference": _maximum(
            records, ("comparison", "T_horizon", "log_abs_abs_difference")
        ),
        "T_wrapped_phase_abs_difference_rad": _maximum(
            records,
            ("comparison", "T_horizon", "wrapped_phase_abs_difference_rad"),
        ),
        "flux_residual_abs_difference": _maximum(
            records, ("comparison", "flux", "residual_abs_difference")
        ),
        "candidate_flux_residual": _maximum(records, ("candidate", "flux_residual")),
    }
    return {
        "schema": SUMMARY_SCHEMA,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "selected_key_count": len(records),
        "completed_key_count": len(records),
        "solver_call_count": len(records),
        "key_state_counts": dict(sorted(counts.items())),
        "overall_state": "FAIL" if counts.get("FAIL") else "PARTIAL",
        "maximum_measured_differences": maxima,
        "numerical_uncertainty_budget": {
            "status": "PARTIAL",
            "upper_bound": None,
            "observed_maxima_are_not_acceptance_thresholds": True,
            "maximum_measured_differences": maxima,
        },
        "convention_uncertainty_budget": {
            "status": "NOT_ASSESSED",
            "upper_bound": None,
        },
        "scope": "selected subset of exact 12,020 predecessor COMPLETED/PARTIAL keys",
        "same_implementation_family": True,
        "independent_scientific_validation": False,
        "diagnostic_only": True,
        "science_executed": True,
        "scientific_acceptance": False,
        "global_green_permitted": False,
        "production_finite_radius_states": "NOT_ASSESSED",
        "elapsed_this_invocation_seconds": float(perf_counter() - started_at),
    }


def _prepare_output_root(output_root: Path, *, resume: bool) -> Path:
    absolute = output_root.absolute()
    parent = absolute.parent.resolve(strict=True)
    resolved_candidate = parent / absolute.name
    if resume:
        if not resolved_candidate.is_dir() or resolved_candidate.is_symlink():
            raise RuntimeError("--resume requires an existing regular output directory")
        if stat.S_IMODE(resolved_candidate.stat().st_mode) == 0o555:
            raise RuntimeError("output root is already sealed")
    else:
        if resolved_candidate.exists() or resolved_candidate.is_symlink():
            raise RuntimeError("fresh output root already exists")
        os.mkdir(resolved_candidate, mode=0o700)
        _fsync_directory(parent)
    return resolved_candidate


def _seal_root(root: Path) -> None:
    for path in root.iterdir():
        if not path.is_file() or path.is_symlink() or path.stat().st_nlink != 1:
            raise RuntimeError(f"cannot seal non-regular output artifact: {path}")
        path.chmod(0o444)
    root.chmod(0o555)
    _fsync_directory(root)
    _fsync_directory(root.parent)


def validate_terminal_root(root: Path) -> dict[str, Any]:
    """Reload a sealed diagnostic and verify inventory, hashes, and policy."""

    resolved = root.resolve(strict=True)
    if resolved.is_symlink() or stat.S_IMODE(resolved.stat().st_mode) != 0o555:
        raise RuntimeError(
            "terminal continuity root must be an immutable 0555 directory"
        )
    names = {path.name for path in resolved.iterdir()}
    expected_names = {
        "manifest.json",
        "progress.json",
        "records.jsonl",
        "run_contract.json",
        "summary.json",
        "writer.lock",
    }
    if names != expected_names:
        raise RuntimeError("terminal continuity root inventory changed")
    for path in resolved.iterdir():
        identity = _identity(path)
        if identity["mode"] != 0o444 or identity["nlink"] != 1:
            raise RuntimeError(f"terminal artifact is not 0444/nlink1: {path}")
    manifest = _load_json(resolved / "manifest.json", canonical=True)
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise RuntimeError("continuity manifest schema changed")
    files = manifest.get("files")
    if not isinstance(files, Mapping) or set(files) != expected_names - {
        "manifest.json"
    }:
        raise RuntimeError("continuity manifest inventory changed")
    for name, identity in files.items():
        if not isinstance(identity, Mapping):
            raise RuntimeError("continuity manifest identity is malformed")
        _validate_identity(identity, resolved / str(name))
    contract = _load_json(resolved / "run_contract.json", canonical=True)
    summary = _load_json(resolved / "summary.json", canonical=True)
    progress = _load_json(resolved / "progress.json", canonical=True)
    if (
        contract.get("schema") != SCHEMA
        or contract.get("scientific_acceptance") is not False
        or contract.get("global_green_permitted") is not False
        or contract.get("convention_uncertainty") != "NOT_ASSESSED"
        or summary.get("schema") != SUMMARY_SCHEMA
        or summary.get("scientific_acceptance") is not False
        or summary.get("global_green_permitted") is not False
        or summary.get("overall_state") not in {"PARTIAL", "FAIL"}
        or progress.get("terminal") is not True
    ):
        raise RuntimeError("terminal continuity policy claims changed")
    selected_count = int(contract.get("selected_key_count", -1))
    raw_lines = (resolved / "records.jsonl").read_bytes().splitlines()
    if (
        len(raw_lines) != selected_count
        or summary.get("completed_key_count") != selected_count
        or summary.get("solver_call_count") != selected_count
        or progress.get("completed_key_count") != selected_count
    ):
        raise RuntimeError("terminal continuity accounting changed")
    return {
        "root": str(resolved),
        "selected_key_count": selected_count,
        "overall_state": summary["overall_state"],
        "key_state_counts": summary["key_state_counts"],
        "maximum_measured_differences": summary["maximum_measured_differences"],
        "manifest_sha256": _sha256_file(resolved / "manifest.json"),
        "records_sha256": _sha256_file(resolved / "records.jsonl"),
    }


def run(
    *,
    output_root: Path,
    campaign_root: Path = DEFAULT_CAMPAIGN_ROOT,
    runner_path: Path,
    limit: int | None = None,
    resume: bool = False,
    solver: Solver = solve_scaled_tortoise_radial_at_radius,
) -> dict[str, Any]:
    """Execute or explicitly resume one isolated continuity diagnostic root."""

    started_at = perf_counter()
    campaign = campaign_root.resolve(strict=True)
    successful_keys = discover_successful_keys(campaign)
    if limit is not None and not 1 <= limit <= EXPECTED_SUCCESS_KEY_COUNT:
        raise ValueError(f"limit must be in [1, {EXPECTED_SUCCESS_KEY_COUNT}]")
    selected = successful_keys if limit is None else successful_keys[:limit]
    contract = _build_contract(
        campaign_root=campaign,
        successful_keys=successful_keys,
        selected=selected,
        limit=limit,
        runner_path=runner_path,
    )
    root = _prepare_output_root(output_root, resume=resume)
    guard_path = root / "writer.lock"

    with _WriterGuard(guard_path, resume=resume) as guard:
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
                record = compare_successful_key(
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
            reloaded = _read_records(records_path, selected)
            if len(reloaded) != len(selected):
                raise RuntimeError(
                    "terminal record count does not match selected inventory"
                )
            summary = _summary(reloaded, started_at)
            _write_exclusive(root / "summary.json", summary)
            _write_atomic(
                progress_path,
                _progress(
                    selected_count=len(selected),
                    records=reloaded,
                    started_at=started_at,
                ),
            )
            guard.write_state(
                "TERMINAL",
                completed_key_count=len(reloaded),
                resume=resume,
            )
            manifest_inputs = (
                "progress.json",
                "records.jsonl",
                "run_contract.json",
                "summary.json",
                "writer.lock",
            )
            try:
                for name in manifest_inputs:
                    (root / name).chmod(0o444)
                manifest = {
                    "schema": MANIFEST_SCHEMA,
                    "created_at_utc": datetime.now(timezone.utc).isoformat(),
                    "files": {name: _identity(root / name) for name in manifest_inputs},
                    "selected_key_count": len(selected),
                    "overall_state": summary["overall_state"],
                    "scientific_acceptance": False,
                    "global_green_permitted": False,
                }
                _write_exclusive(root / "manifest.json", manifest)
                _seal_root(root)
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
    """Reject evidence execution under any runtime except exact CPython 3.14."""

    if platform.python_implementation() != "CPython" or sys.version_info[:2] != (
        3,
        14,
    ):
        raise RuntimeError("continuity evidence requires exact CPython 3.14")


__all__ = [
    "DEFAULT_CAMPAIGN_ROOT",
    "EXPECTED_FAILURE_KEY_COUNT",
    "EXPECTED_SUCCESS_KEY_COUNT",
    "KEY_RECORD_SCHEMA",
    "MANIFEST_SCHEMA",
    "SCHEMA",
    "SUMMARY_SCHEMA",
    "SuccessfulKey",
    "build_request",
    "compare_successful_key",
    "discover_successful_keys",
    "require_exact_cpython314",
    "run",
    "validate_terminal_root",
]
