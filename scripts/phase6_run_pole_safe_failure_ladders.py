#!/usr/bin/env python3
"""Run a resumable pole-safe diagnostic over every failed V1 radial key.

This campaign is intentionally diagnostic rather than acceptance evidence.  It
revisits the exact 5,798 keys that failed closed in the immutable Phase-6 V1
conditioning campaign and evaluates five tolerance/Jost-order nodes with the
fresh scaled full-state tortoise-coordinate backend.

The job needs no network access.  One canonical JSON record is appended and
fsynced after every key, so an interrupted job can resume without recomputing
completed keys.  The immutable V1 source roots are read only and are never
modified.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from decimal import Decimal
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
from schwgw.numerics.conditioned_radial import ConditionedRadialRequest
from schwgw.numerics.scaled_tortoise_radial import (
    solve_scaled_tortoise_radial_at_radius,
)
from schwgw.perturbations import Sector

SCHEMA = "schwgw_phase6_v1_radial_pole_safe_repair_ladders_diagnostic_v1"
EXPECTED_FAILED_KEY_COUNT = 5_798
DEFAULT_CAMPAIGN_INDEX = Path(
    "runs/phase6/radial_validation/"
    "v1_conditioning_campaign_v1_20260808_py314/"
    "conditioning_campaign_index.json"
)


@dataclass(frozen=True)
class LadderNode:
    node_id: str
    rtol: float
    atol: float
    jost_order: int


LADDER_NODES = (
    LadderNode("baseline", 1.0e-10, 1.0e-12, 160),
    LadderNode("tolerance_loose", 1.0e-8, 1.0e-10, 160),
    LadderNode("tolerance_tight", 1.0e-12, 1.0e-14, 160),
    LadderNode("jost_order_120", 1.0e-10, 1.0e-12, 120),
    LadderNode("jost_order_224", 1.0e-10, 1.0e-12, 224),
)


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _identity(path: Path) -> dict[str, Any]:
    resolved = path.resolve(strict=True)
    info = resolved.stat()
    return {
        "path": str(resolved),
        "sha256": _sha256(resolved),
        "size": info.st_size,
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
    }


def _write_exclusive(path: Path, value: Any) -> None:
    payload = _canonical_bytes(value)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("exclusive JSON write made no progress")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_atomic(path: Path, value: Any) -> None:
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    _write_exclusive(temporary, value)
    os.replace(temporary, path)


def _pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _claim_process_guard(output_root: Path) -> Path:
    guard_path = output_root / "process_guard.json"
    current: dict[str, Any] = {
        "schema": f"{SCHEMA}_process_guard",
        "state": "ACTIVE",
        "pid": os.getpid(),
        "started_at_utc": datetime.now(UTC).isoformat(),
        "single_writer_enforced": True,
    }
    if not guard_path.exists():
        _write_exclusive(guard_path, current)
        return guard_path
    previous = _load_json(guard_path)
    previous_pid = previous.get("pid")
    if (
        previous.get("state") == "ACTIVE"
        and isinstance(previous_pid, int)
        and _pid_is_alive(previous_pid)
    ):
        raise RuntimeError(f"output root already has live writer PID {previous_pid}")
    current["resumed_after"] = {
        "pid": previous_pid,
        "state": previous.get("state"),
        "started_at_utc": previous.get("started_at_utc"),
    }
    _write_atomic(guard_path, current)
    return guard_path


def _append_fsynced(path: Path, value: Any) -> None:
    payload = _canonical_bytes(value)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("JSONL append made no progress")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected a JSON object: {path}")
    return value


def _key_id(key: dict[str, Any]) -> str:
    return f"kM={key['kM']};sector={key['sector']};ell={int(key['ell'])}"


def _key_sort(record: dict[str, Any]) -> tuple[Decimal, str, int]:
    key = record["key"]
    return Decimal(str(key["kM"])), str(key["sector"]), int(key["ell"])


def _discover_failed_keys(index_path: Path) -> list[dict[str, Any]]:
    campaign = _load_json(index_path)
    if campaign.get("schema") != "schwgw_phase6_conditioning_campaign_index_v1":
        raise RuntimeError("conditioning campaign schema changed")
    if campaign.get("overall_state") != "FAIL":
        raise RuntimeError("conditioning predecessor is not the frozen FAIL campaign")
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for shard in campaign.get("shards", []):
        root = Path(shard["root"]).resolve(strict=True)
        for payload_path in sorted(root.glob("key_*__payload.json")):
            envelope = _load_json(payload_path)
            solver_payload = envelope.get("solver_payload")
            if not isinstance(solver_payload, dict):
                raise RuntimeError(f"invalid solver payload: {payload_path}")
            if solver_payload.get("acceptance_state") != "FAIL":
                continue
            key = envelope["key"]
            identity = _key_id(key)
            if identity in seen:
                raise RuntimeError(f"duplicate failed key: {identity}")
            seen.add(identity)
            outer = solver_payload.get("outer_selection", {})
            selected_r_out = outer.get("selected_r_out_M")
            if not isinstance(selected_r_out, (int, float)) or not math.isfinite(
                float(selected_r_out)
            ):
                raise RuntimeError(f"failed key has no finite r_out: {identity}")
            records.append(
                {
                    "key": {
                        "kM": str(key["kM"]),
                        "sector": str(key["sector"]),
                        "ell": int(key["ell"]),
                    },
                    "key_id": identity,
                    "selected_r_out_M": float(selected_r_out),
                    "predecessor_failure_reasons": solver_payload.get("failures", {}),
                    "predecessor_payload_identity": _identity(payload_path),
                }
            )
    records.sort(key=_key_sort)
    if len(records) != EXPECTED_FAILED_KEY_COUNT:
        raise RuntimeError(
            f"expected {EXPECTED_FAILED_KEY_COUNT} failed keys, found {len(records)}"
        )
    return records


def _complex_value(value: complex) -> dict[str, float]:
    real = float(value.real)
    imag = float(value.imag)
    magnitude = float(abs(value))
    phase = float(np.angle(value))
    if not all(math.isfinite(item) for item in (real, imag, magnitude, phase)):
        raise RuntimeError("non-finite complex result")
    return {
        "real": real,
        "imag": imag,
        "magnitude": magnitude,
        "phase": phase,
    }


def _run_node(key_record: dict[str, Any], node: LadderNode) -> dict[str, Any]:
    key = key_record["key"]
    started = perf_counter()
    try:
        request = ConditionedRadialRequest(
            sector=Sector(str(key["sector"])),
            ell=int(key["ell"]),
            k=float(key["kM"]),
            required_radius=40.0,
            r_out=float(key_record["selected_r_out_M"]),
            r_in_eps=1.0e-6,
            rtol=node.rtol,
            atol=node.atol,
            outer_basis="jost_1_over_r",
            outer_series_order=node.jost_order,
        )
        result = solve_scaled_tortoise_radial_at_radius(
            request,
            SchwarzschildBackground(M=1.0),
        )
        return {
            "node": asdict(node),
            "status": "MEASURED",
            "A_out_over_A_in": _complex_value(result.A_out),
            "T_horizon": _complex_value(result.T_horizon),
            "log_abs_T_horizon": float(result.log_abs_T_horizon),
            "phase_T_horizon": float(result.phase_T_horizon),
            "required_radius_psi": _complex_value(result.psi),
            "required_radius_dpsi_dr": _complex_value(result.dpsi_dr),
            "flux_residual": float(result.diagnostics["flux_residual"]),
            "outer_boundary_residual": float(
                result.diagnostics["outer_boundary_residual"]
            ),
            "match_condition_number": float(
                result.diagnostics["match_condition_number"]
            ),
            "segment_count": int(result.diagnostics["segment_count"]),
            "rhs_evaluations": int(result.diagnostics["rhs_evaluations"]),
            "runtime_seconds": float(perf_counter() - started),
            "backend": str(result.diagnostics["backend"]),
            "method": str(result.diagnostics["method"]),
            "riccati_variable_used": bool(result.diagnostics["riccati_variable_used"]),
            "scientific_acceptance": False,
        }
    except Exception as exc:  # diagnostic campaign must retain every failure
        return {
            "node": asdict(node),
            "status": "FAIL",
            "failure": f"{type(exc).__name__}: {exc}",
            "runtime_seconds": float(perf_counter() - started),
            "scientific_acceptance": False,
        }


def _angular_difference(left: float, right: float) -> float:
    return abs(math.atan2(math.sin(left - right), math.cos(left - right)))


def _summarize_ladder(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    measured = [node for node in nodes if node["status"] == "MEASURED"]
    if len(measured) != len(LADDER_NODES):
        return {
            "state": "FAIL",
            "measured_node_count": len(measured),
            "failed_node_count": len(LADDER_NODES) - len(measured),
            "numerical_uncertainty": "NOT_ASSESSED_INCOMPLETE_LADDER",
            "convention_uncertainty": "NOT_ASSESSED",
        }
    baseline = next(node for node in measured if node["node"]["node_id"] == "baseline")
    tolerance = next(
        node for node in measured if node["node"]["node_id"] == "tolerance_tight"
    )
    order = next(
        node for node in measured if node["node"]["node_id"] == "jost_order_224"
    )

    def delta(other: dict[str, Any]) -> dict[str, float]:
        base = baseline["A_out_over_A_in"]
        trial = other["A_out_over_A_in"]
        complex_delta = abs(
            complex(base["real"], base["imag"]) - complex(trial["real"], trial["imag"])
        )
        return {
            "complex_abs": float(complex_delta),
            "modulus_abs": float(abs(base["magnitude"] - trial["magnitude"])),
            "phase_abs_rad": float(_angular_difference(base["phase"], trial["phase"])),
            "log_abs_T_abs": float(
                abs(baseline["log_abs_T_horizon"] - other["log_abs_T_horizon"])
            ),
        }

    return {
        "state": "PARTIAL",
        "measured_node_count": len(measured),
        "failed_node_count": 0,
        "numerical_uncertainty": {
            "tolerance_baseline_vs_tight": delta(tolerance),
            "jost_order_160_vs_224": delta(order),
            "maximum_flux_residual": max(node["flux_residual"] for node in measured),
        },
        "convention_uncertainty": "NOT_ASSESSED",
    }


def _read_completed_records(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    completed: dict[str, dict[str, Any]] = {}
    raw_lines = path.read_bytes().splitlines()
    for index, raw in enumerate(raw_lines):
        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            if index == len(raw_lines) - 1:
                raise RuntimeError(
                    "records.jsonl has an incomplete trailing record; preserve it for audit"
                ) from None
            raise
        key_id = record.get("key_id")
        if not isinstance(key_id, str) or key_id in completed:
            raise RuntimeError("records.jsonl contains an invalid or duplicate key")
        completed[key_id] = record
    return completed


def _source_identities(project_root: Path, index_path: Path) -> dict[str, Any]:
    paths = {
        "campaign_index": index_path,
        "repair_backend": project_root
        / "src/schwgw/numerics/scaled_tortoise_radial.py",
        "runner": Path(__file__).resolve(),
        "v1_conditioned_backend": project_root
        / "src/schwgw/numerics/conditioned_radial.py",
        "jost_matching": project_root / "src/schwgw/numerics/matching.py",
        "potentials": project_root / "src/schwgw/perturbations/potentials.py",
        "schwarzschild_background": project_root
        / "src/schwgw/backgrounds/schwarzschild.py",
    }
    return {name: _identity(path) for name, path in paths.items()}


def _build_contract(
    *,
    project_root: Path,
    index_path: Path,
    failed_keys: list[dict[str, Any]],
    limit: int | None,
) -> dict[str, Any]:
    selected = failed_keys if limit is None else failed_keys[:limit]
    key_list_sha = hashlib.sha256(
        _canonical_bytes([record["key_id"] for record in selected])
    ).hexdigest()
    return {
        "schema": SCHEMA,
        "campaign_role": "diagnostic_repair_ladder",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "project_root": str(project_root),
        "source_identities": _source_identities(project_root, index_path),
        "predecessor_failed_key_count": len(failed_keys),
        "selected_key_count": len(selected),
        "selected_key_list_sha256": key_list_sha,
        "ladder_nodes": [asdict(node) for node in LADDER_NODES],
        "required_radius_M": 40.0,
        "expected_solver_call_count": len(selected) * len(LADDER_NODES),
        "runtime": {
            "python": sys.version,
            "python_executable": sys.executable,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "diagnostic_only": True,
        "scientific_acceptance": False,
        "global_green_permitted": False,
        "li_figure_agreement_primary_gate": False,
        "full_paper_figure_rerun": False,
        "resume_protocol": "one canonical fsynced JSONL record per completed key",
        "limit": limit,
    }


def _validate_resume_contract(
    existing: dict[str, Any], expected: dict[str, Any]
) -> None:
    ignored = {"created_at_utc"}
    existing_stable = {
        key: value for key, value in existing.items() if key not in ignored
    }
    expected_stable = {
        key: value for key, value in expected.items() if key not in ignored
    }
    if existing_stable != expected_stable:
        raise RuntimeError("existing output root was created by a different contract")


def _progress(
    *,
    selected_count: int,
    completed: dict[str, dict[str, Any]],
    started_at: float,
) -> dict[str, Any]:
    states = Counter(record["ladder_summary"]["state"] for record in completed.values())
    return {
        "schema": f"{SCHEMA}_progress",
        "pid": os.getpid(),
        "updated_at_utc": datetime.now(UTC).isoformat(),
        "selected_key_count": selected_count,
        "completed_key_count": len(completed),
        "remaining_key_count": selected_count - len(completed),
        "key_state_counts": dict(sorted(states.items())),
        "elapsed_this_invocation_seconds": perf_counter() - started_at,
        "terminal": len(completed) == selected_count,
        "diagnostic_only": True,
        "scientific_acceptance": False,
    }


def _seal_root(root: Path) -> None:
    for path in root.iterdir():
        if path.is_file():
            path.chmod(0o444)
    root.chmod(0o555)


def run(*, output_root: Path, index_path: Path, limit: int | None) -> None:
    started_at = perf_counter()
    project_root = Path(__file__).resolve().parents[1]
    index_path = index_path.resolve(strict=True)
    failed_keys = _discover_failed_keys(index_path)
    if limit is not None and not 1 <= limit <= len(failed_keys):
        raise ValueError(f"limit must be in [1, {len(failed_keys)}]")
    selected = failed_keys if limit is None else failed_keys[:limit]
    contract = _build_contract(
        project_root=project_root,
        index_path=index_path,
        failed_keys=failed_keys,
        limit=limit,
    )

    output_root = output_root.resolve()
    if output_root.exists() and stat.S_IMODE(output_root.stat().st_mode) == 0o555:
        raise RuntimeError("output root is already sealed")
    output_root.mkdir(parents=True, exist_ok=True)
    process_guard_path = _claim_process_guard(output_root)
    contract_path = output_root / "run_contract.json"
    if contract_path.exists():
        _validate_resume_contract(_load_json(contract_path), contract)
    else:
        _write_exclusive(contract_path, contract)

    records_path = output_root / "records.jsonl"
    completed = _read_completed_records(records_path)
    selected_ids = {record["key_id"] for record in selected}
    if not set(completed).issubset(selected_ids):
        raise RuntimeError("records.jsonl contains keys outside this contract")
    progress_path = output_root / "progress.json"
    _write_atomic(
        progress_path,
        _progress(
            selected_count=len(selected),
            completed=completed,
            started_at=started_at,
        ),
    )

    for ordinal, key_record in enumerate(selected, start=1):
        key_id = key_record["key_id"]
        if key_id in completed:
            continue
        nodes = [_run_node(key_record, node) for node in LADDER_NODES]
        record = {
            "schema": f"{SCHEMA}_key_record",
            "ordinal": ordinal,
            "key": key_record["key"],
            "key_id": key_id,
            "selected_r_out_M": key_record["selected_r_out_M"],
            "predecessor_failure_reasons": key_record["predecessor_failure_reasons"],
            "predecessor_payload_identity": key_record["predecessor_payload_identity"],
            "nodes": nodes,
            "ladder_summary": _summarize_ladder(nodes),
            "diagnostic_only": True,
            "scientific_acceptance": False,
        }
        _append_fsynced(records_path, record)
        completed[key_id] = record
        _write_atomic(
            progress_path,
            _progress(
                selected_count=len(selected),
                completed=completed,
                started_at=started_at,
            ),
        )

    reloaded = _read_completed_records(records_path)
    if set(reloaded) != selected_ids:
        raise RuntimeError("terminal JSONL inventory does not match the contract")
    node_statuses = Counter(
        node["status"] for record in reloaded.values() for node in record["nodes"]
    )
    key_states = Counter(
        record["ladder_summary"]["state"] for record in reloaded.values()
    )
    summary = {
        "schema": f"{SCHEMA}_summary",
        "completed_at_utc": datetime.now(UTC).isoformat(),
        "selected_key_count": len(selected),
        "completed_key_count": len(reloaded),
        "solver_node_count": sum(node_statuses.values()),
        "node_status_counts": dict(sorted(node_statuses.items())),
        "key_state_counts": dict(sorted(key_states.items())),
        "records_sha256": _sha256(records_path),
        "elapsed_this_invocation_seconds": perf_counter() - started_at,
        "diagnostic_only": True,
        "scientific_acceptance": False,
        "global_green_permitted": False,
        "result_state": "PARTIAL" if not key_states.get("FAIL") else "FAIL",
        "scope": "only the 5,798 V1 conditioned-backend failure keys",
        "convention_uncertainty": "NOT_ASSESSED",
    }
    summary_path = output_root / "summary.json"
    _write_exclusive(summary_path, summary)
    _write_atomic(
        progress_path,
        _progress(
            selected_count=len(selected),
            completed=reloaded,
            started_at=started_at,
        ),
    )
    process_guard = _load_json(process_guard_path)
    process_guard["state"] = "TERMINAL"
    process_guard["completed_at_utc"] = datetime.now(UTC).isoformat()
    _write_atomic(process_guard_path, process_guard)
    manifest = {
        "schema": f"{SCHEMA}_manifest",
        "files": {
            name: _identity(output_root / name)
            for name in (
                "run_contract.json",
                "process_guard.json",
                "records.jsonl",
                "progress.json",
                "summary.json",
            )
        },
    }
    _write_exclusive(output_root / "manifest.json", manifest)
    _seal_root(output_root)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument(
        "--campaign-index",
        type=Path,
        default=DEFAULT_CAMPAIGN_INDEX,
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Smoke-test only: evaluate the first N failure keys.",
    )
    arguments = parser.parse_args()
    run(
        output_root=arguments.output_root,
        index_path=arguments.campaign_index,
        limit=arguments.limit,
    )


if __name__ == "__main__":
    main()
