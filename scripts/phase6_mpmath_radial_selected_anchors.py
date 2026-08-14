#!/usr/bin/env python3
"""Run the bounded Phase-6 independent-mpmath radial S-matrix pilot."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import stat
import sys
import time
from typing import Mapping, Sequence

import mpmath as mp
import numpy as np
import scipy

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.numerics import BoundaryConfig, solve_radial_mode
from schwgw.perturbations import Sector
from schwgw.scattering.mst import schwarzschild_mst_phase_factor
from schwgw.validation.phase6_mpmath_radial import (
    EVIDENCE_SCHEMA,
    MpmathEvaluationPoint,
    MpmathMode,
    MpmathSolveConfig,
    prove_call_graph_isolation,
    result_for,
    selected_stage_a_modes,
    solve_mode_batch,
    validate_stage_a_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
BACKEND_SOURCE = ROOT / "src/schwgw/validation/phase6_mpmath_radial.py"
BHPT_EVIDENCE = (
    ROOT / "runs/phase5/paper_figures/bhpt_mst_benchmark_20260803_v4/"
    "external_bhpt_mst.json"
)
V6B_EVIDENCE = (
    ROOT / "runs/phase6/radial_validation/v1_selected_mode_pilot_v6b_20260806_py314/"
    "selected_mode_evidence.json"
)
V1_DIAGNOSTIC_ROOT = (
    ROOT / "runs/phase6/radial_validation/"
    "v1_stage_a_mpmath_selected_anchors_v1_20260806_py314"
)
V2_DIAGNOSTIC_ROOT = (
    ROOT / "runs/phase6/radial_validation/"
    "v1_stage_a_mpmath_selected_anchors_v2_20260806_py314"
)
V3_DIAGNOSTIC_ROOT = (
    ROOT / "runs/phase6/radial_validation/"
    "v1_stage_a_mpmath_selected_anchors_v3_20260806_py314"
)
DOMAIN_FREEZE_ROOT = ROOT / "runs/phase6/v1_domain_freeze_v3_20260806"
EXECUTION_CONTRACT_ROOT = ROOT / "runs/phase6/v1_execution_contract_v4_20260806"
RADIAL_VALIDATION_ROOT = ROOT / "runs/phase6/radial_validation"
PRECISION_NODES = (50, 70, 100)
R_IN_NODES = (3.0e-6, 1.0e-6, 3.0e-7)
R_OUT_NODES = (300.0, 600.0)
JOST_NODES = (80, 120, 160)
STEP_NODES = (0.1, 0.05, 0.025)
BASELINE_R_OUT = 300.0
BASELINE_JOST = 160
BASELINE_STEP = 0.025
BASELINE_R_IN = 1.0e-6
STAGE_A_POINT_X = (0, 1, 2, 3, 10, 15, 20, 25)
MODE_TERMINAL_SCHEMA = "schwgw_phase6_mpmath_mode_terminal_v1"
RUN_FAILURE_SCHEMA = "schwgw_phase6_mpmath_run_failure_v1"
EXPECTED_BATCH_LABELS = (
    "precision_dps_50",
    "precision_dps_70",
    "precision_dps_100",
    "step_rstar_0p1",
    "step_rstar_0p05",
    "r_in_eps_3em06",
    "r_in_eps_3em07",
)
MODE_EXECUTION_STATUSES = {
    "COMPLETED",
    "EXECUTION_FAILED",
    "NOT_STARTED_DUE_TO_RUN_FAILURE",
}


def _stage_a_evaluation_points() -> tuple[MpmathEvaluationPoint, ...]:
    """Derive the Stage-A Table-I finite-state requests outside the backend."""

    with mp.workdps(120):
        return tuple(
            MpmathEvaluationPoint(
                point_id=f"near_axis_x{x}_z30",
                radius_M=mp.nstr(mp.sqrt(mp.mpf(30) ** 2 + mp.mpf(x) ** 2), 110),
            )
            for x in STAGE_A_POINT_X
        )


STAGE_A_EVALUATION_POINTS = _stage_a_evaluation_points()


def _canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _publish_json(path: Path, payload: object) -> dict[str, object]:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"output collision: {path}")
    data = _canonical_bytes(payload)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise
    os.chmod(path, 0o444)
    _fsync_directory(path.parent)
    reloaded = path.read_bytes()
    if reloaded != data:
        raise RuntimeError("published JSON reload mismatch")
    info = path.stat()
    if (
        not stat.S_ISREG(info.st_mode)
        or info.st_nlink != 1
        or stat.S_IMODE(info.st_mode) != 0o444
    ):
        raise RuntimeError("published JSON stat identity mismatch")
    return {
        "path": str(path.resolve(strict=True)),
        "sha256": hashlib.sha256(data).hexdigest(),
        "size": len(data),
        "inode": info.st_ino,
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
    }


def _publish_terminal_json(path: Path, payload: object) -> dict[str, object]:
    """Atomically publish a complete, fsynced, no-replace terminal record."""

    if path.exists() or path.is_symlink():
        raise FileExistsError(f"output collision: {path}")
    data = _canonical_bytes(payload)
    staging = path.with_name(
        f".{path.name}.o_excl_staging_{os.getpid()}_{time.time_ns()}"
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(staging, flags, 0o600)
    linked = False
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(staging, 0o444)
        _fsync_directory(path.parent)
        os.link(staging, path, follow_symlinks=False)
        linked = True
        _fsync_directory(path.parent)
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise
    finally:
        try:
            staging.unlink()
        except FileNotFoundError:
            pass
        _fsync_directory(path.parent)
    if not linked:
        raise RuntimeError("terminal JSON publication did not create the final link")
    reloaded = path.read_bytes()
    if reloaded != data:
        raise RuntimeError("published terminal JSON reload mismatch")
    info = path.stat()
    if (
        not stat.S_ISREG(info.st_mode)
        or info.st_nlink != 1
        or stat.S_IMODE(info.st_mode) != 0o444
    ):
        raise RuntimeError("published terminal JSON stat identity mismatch")
    return {
        "path": str(path.resolve(strict=True)),
        "sha256": hashlib.sha256(data).hexdigest(),
        "size": len(data),
        "inode": info.st_ino,
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
    }


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _source_identity(path: Path) -> dict[str, object]:
    target = path.resolve(strict=True)
    info = target.stat()
    return {
        "path": str(target),
        "sha256": _sha256(target),
        "size": info.st_size,
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
    }


def _reject_duplicate_json_keys(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise RuntimeError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise RuntimeError(f"non-finite JSON constant: {value}")


def _reload_canonical_json(path: Path) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"JSON artifact is missing or aliased: {path}")
    raw = path.read_bytes()
    try:
        payload = json.loads(
            raw,
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"JSON artifact is malformed: {path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"JSON artifact is not an object: {path}")
    if raw != _canonical_bytes(payload):
        raise RuntimeError(f"JSON artifact is not canonical: {path}")
    return payload


def _existing_published_identity(path: Path) -> dict[str, object]:
    target = path.resolve(strict=True)
    if target != path or path.is_symlink() or not path.is_file():
        raise RuntimeError(f"published artifact path/alias mismatch: {path}")
    info = path.stat()
    if (
        not stat.S_ISREG(info.st_mode)
        or info.st_nlink != 1
        or stat.S_IMODE(info.st_mode) != 0o444
    ):
        raise RuntimeError(f"published artifact stat identity mismatch: {path}")
    data = path.read_bytes()
    return {
        "path": str(target),
        "sha256": hashlib.sha256(data).hexdigest(),
        "size": len(data),
        "inode": info.st_ino,
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
    }


def _validate_published_identity(
    identity: object,
    *,
    expected_path: Path,
) -> dict[str, object]:
    if not isinstance(identity, Mapping) or set(identity) != {
        "path",
        "sha256",
        "size",
        "inode",
        "mode",
        "nlink",
    }:
        raise RuntimeError("published identity schema mismatch")
    actual = _existing_published_identity(expected_path)
    if dict(identity) != actual:
        raise RuntimeError(f"published identity content/stat drift: {expected_path}")
    return actual


def _checkpoint_prefix(mode_root: Path) -> list[dict[str, object]]:
    identities: list[dict[str, object]] = []
    missing_seen = False
    for label in EXPECTED_BATCH_LABELS:
        path = mode_root / f"{label}.json"
        exists = path.exists() or path.is_symlink()
        if not exists:
            missing_seen = True
            continue
        if missing_seen:
            raise RuntimeError("mode checkpoint inventory is not an ordered prefix")
        payload = _reload_canonical_json(path)
        if set(payload) != {
            "schema_version",
            "label",
            "status",
            "failure",
            "batch",
        }:
            raise RuntimeError("mode batch checkpoint exact schema mismatch")
        if (
            payload.get("schema_version") != "schwgw_phase6_mpmath_mode_checkpoint_v1"
            or payload.get("label") != label
            or payload.get("status") not in {"PASS", "FAIL_CLOSED"}
        ):
            raise RuntimeError("mode batch checkpoint key/order mismatch")
        if (payload["status"] == "PASS") != (
            payload.get("failure") is None and isinstance(payload.get("batch"), Mapping)
        ):
            raise RuntimeError("mode batch checkpoint status/payload mismatch")
        if payload["status"] == "FAIL_CLOSED" and not (
            isinstance(payload.get("failure"), str)
            and payload["failure"]
            and payload.get("batch") is None
        ):
            raise RuntimeError("failed mode batch checkpoint is malformed")
        identities.append(_existing_published_identity(path))
    allowed = {f"{label}.json" for label in EXPECTED_BATCH_LABELS} | {"terminal.json"}
    actual_entries = {path.name for path in mode_root.iterdir()}
    if not actual_entries <= allowed:
        raise RuntimeError("mode checkpoint directory contains a foreign entry")
    return identities


def _mode_failure_record(stage: str, exc: Exception) -> dict[str, str]:
    return {
        "stage": stage,
        "exception_type": type(exc).__name__,
        "message": str(exc) or "<empty exception message>",
    }


def _mode_terminal_payload(
    *,
    mode_index: int,
    mode: MpmathMode,
    execution_status: str,
    checkpoint_identities: Sequence[Mapping[str, object]],
    mode_evidence: Mapping[str, object] | None,
    failure: Mapping[str, str] | None,
) -> dict[str, object]:
    scientific_status = (
        mode_evidence.get("status") if mode_evidence is not None else "NOT_ASSESSED"
    )
    return {
        "schema_version": MODE_TERMINAL_SCHEMA,
        "mode_index": mode_index,
        "mode": mode.to_metadata(),
        "execution_status": execution_status,
        "scientific_status": scientific_status,
        "checkpoint_identities": [dict(item) for item in checkpoint_identities],
        "mode_evidence": None if mode_evidence is None else dict(mode_evidence),
        "failure": None if failure is None else dict(failure),
    }


def _validate_mode_terminal(
    payload: Mapping[str, object],
    *,
    mode_index: int,
    mode: MpmathMode,
    mode_root: Path,
) -> None:
    if set(payload) != {
        "schema_version",
        "mode_index",
        "mode",
        "execution_status",
        "scientific_status",
        "checkpoint_identities",
        "mode_evidence",
        "failure",
    }:
        raise RuntimeError("mode terminal exact schema mismatch")
    if (
        payload.get("schema_version") != MODE_TERMINAL_SCHEMA
        or payload.get("mode_index") != mode_index
        or payload.get("mode") != mode.to_metadata()
        or payload.get("execution_status") not in MODE_EXECUTION_STATUSES
    ):
        raise RuntimeError("mode terminal order/key binding mismatch")
    checkpoint_identities = payload.get("checkpoint_identities")
    if not isinstance(checkpoint_identities, list):
        raise RuntimeError("mode terminal checkpoint inventory is malformed")
    on_disk = _checkpoint_prefix(mode_root)
    if checkpoint_identities != on_disk:
        raise RuntimeError("mode terminal checkpoint identity/order mismatch")
    execution_status = payload["execution_status"]
    evidence = payload.get("mode_evidence")
    failure = payload.get("failure")
    if execution_status == "COMPLETED":
        if len(on_disk) != len(EXPECTED_BATCH_LABELS):
            raise RuntimeError("completed mode checkpoint cardinality mismatch")
        if (
            not isinstance(evidence, Mapping)
            or evidence.get("mode") != mode.to_metadata()
            or evidence.get("status") != payload.get("scientific_status")
            or evidence.get("checkpoint_identities") != on_disk
            or failure is not None
        ):
            raise RuntimeError("completed mode terminal payload mismatch")
        return
    if evidence is not None or payload.get("scientific_status") != "NOT_ASSESSED":
        raise RuntimeError("incomplete mode terminal overstates science")
    if not isinstance(failure, Mapping) or set(failure) != {
        "stage",
        "exception_type",
        "message",
    }:
        raise RuntimeError("incomplete mode terminal failure schema mismatch")
    if not all(isinstance(failure[field], str) and failure[field] for field in failure):
        raise RuntimeError("incomplete mode terminal failure is empty")
    if execution_status == "NOT_STARTED_DUE_TO_RUN_FAILURE" and on_disk:
        raise RuntimeError("not-started mode unexpectedly has batch checkpoints")


def _publish_mode_terminal(
    *,
    mode_index: int,
    mode: MpmathMode,
    mode_root: Path,
    execution_status: str,
    mode_evidence: Mapping[str, object] | None,
    failure: Mapping[str, str] | None,
) -> dict[str, object]:
    checkpoint_identities = _checkpoint_prefix(mode_root)
    payload = _mode_terminal_payload(
        mode_index=mode_index,
        mode=mode,
        execution_status=execution_status,
        checkpoint_identities=checkpoint_identities,
        mode_evidence=mode_evidence,
        failure=failure,
    )
    identity = _publish_terminal_json(mode_root / "terminal.json", payload)
    reloaded = _reload_canonical_json(mode_root / "terminal.json")
    _validate_mode_terminal(
        reloaded,
        mode_index=mode_index,
        mode=mode,
        mode_root=mode_root,
    )
    _validate_published_identity(identity, expected_path=mode_root / "terminal.json")
    return identity


def _reload_mode_terminals(
    checkpoint_root: Path,
    *,
    require_all_completed: bool,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    expected_modes = selected_stage_a_modes()
    expected_names = {mode.mode_id for mode in expected_modes}
    actual_entries = {path.name for path in checkpoint_root.iterdir()}
    if actual_entries != expected_names:
        raise RuntimeError("mode terminal directory cardinality/key mismatch")
    evidence_records: list[dict[str, object]] = []
    identities: list[dict[str, object]] = []
    for mode_index, mode in enumerate(expected_modes):
        mode_root = checkpoint_root / mode.mode_id
        if mode_root.is_symlink() or not mode_root.is_dir():
            raise RuntimeError("mode terminal directory path/alias mismatch")
        terminal_path = mode_root / "terminal.json"
        payload = _reload_canonical_json(terminal_path)
        _validate_mode_terminal(
            payload,
            mode_index=mode_index,
            mode=mode,
            mode_root=mode_root,
        )
        if require_all_completed and payload["execution_status"] != "COMPLETED":
            raise RuntimeError("Stage-A mode execution did not complete")
        if payload["execution_status"] == "COMPLETED":
            evidence = payload["mode_evidence"]
            if not isinstance(evidence, dict):
                raise RuntimeError(
                    "completed mode evidence did not reload as an object"
                )
            evidence_records.append(evidence)
        identities.append(_existing_published_identity(terminal_path))
    if require_all_completed and len(evidence_records) != len(expected_modes):
        raise RuntimeError("Stage-A reloaded mode evidence cardinality mismatch")
    return evidence_records, identities


def _package_tree_identity(package_root: Path) -> dict[str, object]:
    root = package_root.resolve(strict=True)
    files: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise RuntimeError("runtime package tree contains a symlink")
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        identity = _source_identity(path)
        if identity["nlink"] != 1:
            raise RuntimeError("runtime package tree contains a linked file")
        files.append(
            {
                "relative_path": relative.as_posix(),
                "sha256": identity["sha256"],
                "size": identity["size"],
                "mode": identity["mode"],
                "nlink": identity["nlink"],
            }
        )
    return {
        "root": str(root),
        "file_count": len(files),
        "files": files,
        "derived_bytecode_policy": "exclude __pycache__ directories and *.pyc files",
        "canonical_inventory_sha256": hashlib.sha256(
            _canonical_bytes(files)
        ).hexdigest(),
    }


def _runtime_identity(output_root: Path) -> dict[str, object]:
    overlay_root = Path(mp.__file__).resolve(strict=True).parents[1]
    expected_overlay = (
        ROOT / "runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314"
    ).resolve(strict=True)
    if overlay_root != expected_overlay:
        raise RuntimeError("mpmath was not loaded from the frozen project overlay")
    expected_pythonpath = os.pathsep.join((str(expected_overlay), str(ROOT / "src")))
    if os.environ.get("PYTHONDONTWRITEBYTECODE") != "1":
        raise RuntimeError("Phase-6 AP runtime requires PYTHONDONTWRITEBYTECODE=1")
    if os.environ.get("PYTHONPATH") != expected_pythonpath:
        raise RuntimeError("Phase-6 AP runtime requires exact overlay-first PYTHONPATH")
    shadowing = [
        entry
        for entry in sys.path
        if "python3.10" in entry and "site-packages" in entry
    ]
    if shadowing:
        raise RuntimeError("incompatible Python-3.10 site-packages shadows runtime")
    recorded_sys_path = list(sys.path)
    expected_import_prefix = [
        str(Path(__file__).resolve(strict=True).parent),
        str(expected_overlay),
        str((ROOT / "src").resolve(strict=True)),
    ]
    if recorded_sys_path[:3] != expected_import_prefix:
        raise RuntimeError("Phase-6 AP sys.path is not runner/overlay/src ordered")
    for entry in recorded_sys_path:
        if not entry:
            continue
        candidate = Path(entry)
        if candidate == expected_overlay:
            continue
        if (candidate / "mpmath" / "__init__.py").is_file() or (
            candidate / "mpmath.py"
        ).is_file():
            raise RuntimeError("foreign mpmath import candidate shadows provenance")
    if Path.cwd().resolve(strict=True) != ROOT:
        raise RuntimeError("Phase-6 AP runner cwd must be the project root")
    output = output_root.resolve(strict=False)
    expected_output_parent = RADIAL_VALIDATION_ROOT.resolve(strict=True)
    try:
        output_relative = output.relative_to(expected_output_parent)
    except ValueError as exc:
        raise RuntimeError("Phase-6 AP output root is out of scope") from exc
    if output_relative == Path("."):
        raise RuntimeError("Phase-6 AP output root must be a fresh child")
    canonical_argv = [
        str(Path(__file__).resolve(strict=True)),
        "--output-root",
        str(output),
    ]
    if list(sys.argv) != canonical_argv:
        raise RuntimeError("Phase-6 AP runner argv is not canonical")
    executable = Path(sys.executable).resolve(strict=True)
    package_tree = _package_tree_identity(expected_overlay)
    required_distribution_files = {
        "mpmath/__init__.py",
        "mpmath-1.4.1.dist-info/METADATA",
        "mpmath-1.4.1.dist-info/RECORD",
        "mpmath-1.4.1.dist-info/licenses/LICENSE",
    }
    if not required_distribution_files <= {
        record["relative_path"] for record in package_tree["files"]
    }:
        raise RuntimeError("frozen mpmath distribution inventory is incomplete")
    return {
        "schema": "schwgw_phase6_ap_runtime_identity_v2",
        "python": {
            "executable": _source_identity(executable),
            "implementation_name": sys.implementation.name,
            "implementation_version": platform.python_version(),
            "cache_tag": sys.implementation.cache_tag,
            "platform": platform.platform(),
        },
        "mpmath": {
            "version": mp.__version__,
            "import_origin": _source_identity(Path(mp.__file__)),
            "package_tree": package_tree,
        },
        "loading": {
            "mechanism": "exact overlay-first PYTHONPATH",
            "overlay_root": str(expected_overlay),
            "pythonpath": expected_pythonpath,
            "sys_path": recorded_sys_path,
            "python3p10_site_packages_entries": shadowing,
            "numpy": {
                "version": np.__version__,
                "origin": _source_identity(Path(np.__file__)),
            },
            "scipy": {
                "version": scipy.__version__,
                "origin": _source_identity(Path(scipy.__file__)),
            },
        },
        "invocation": {
            "cwd": str(Path.cwd().resolve(strict=True)),
            "argv": canonical_argv,
            "environment": {
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONPATH": expected_pythonpath,
            },
            "reproducible_command": shlex.join([str(executable), *canonical_argv]),
        },
    }


def _batch_checkpoint(
    mode_root: Path,
    *,
    label: str,
    batch: Mapping[str, object] | None,
    failure: str | None,
) -> tuple[dict[str, object], Mapping[str, object] | None]:
    payload = {
        "schema_version": "schwgw_phase6_mpmath_mode_checkpoint_v1",
        "label": label,
        "status": "PASS" if failure is None else "FAIL_CLOSED",
        "failure": failure,
        "batch": batch,
    }
    return _publish_json(mode_root / f"{label}.json", payload), batch


def _run_batch(
    mode: MpmathMode,
    mode_root: Path,
    *,
    label: str,
    dps: int,
    r_in_eps: float,
    step: float,
    r_out_nodes: Sequence[float],
    jost_orders: Sequence[int],
) -> tuple[dict[str, object], Mapping[str, object] | None, str | None]:
    try:
        batch = solve_mode_batch(
            mode,
            MpmathSolveConfig(
                working_dps=dps,
                r_in_eps=r_in_eps,
                maximum_step_rstar=step,
            ),
            evaluation_points=STAGE_A_EVALUATION_POINTS,
            r_out_nodes=r_out_nodes,
            jost_orders=jost_orders,
        )
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
        identity, _ = _batch_checkpoint(
            mode_root, label=label, batch=None, failure=failure
        )
        return identity, None, failure
    identity, stored = _batch_checkpoint(
        mode_root, label=label, batch=batch, failure=None
    )
    return identity, stored, None


def _axis_record(
    name: str,
    nodes: Sequence[object],
    results: Sequence[Mapping[str, object] | None],
    failures: Sequence[str | None],
) -> dict[str, object]:
    expected_nodes = {
        "precision_dps": PRECISION_NODES,
        "step_rstar": STEP_NODES,
        "r_in_eps": R_IN_NODES,
        "r_out_M": R_OUT_NODES,
        "jost_order": JOST_NODES,
    }
    if name not in expected_nodes or tuple(nodes) != expected_nodes[name]:
        raise RuntimeError("ladder nodes are not the exact frozen ordered nodes")
    if not (len(nodes) == len(results) == len(failures)):
        raise RuntimeError("ladder node/result/failure length mismatch")
    if len({repr(node) for node in nodes}) != len(nodes):
        raise RuntimeError("ladder nodes must be ordered and unique")
    with mp.workdps(120):
        values = [
            None if result is None else _mp_complex_record_checked(result["S"])
            for result in results
        ]
        for value, failure in zip(values, failures):
            if (value is None) != (failure is not None):
                raise RuntimeError("ladder failure bookkeeping mismatch")
        delta_values: list[mp.mpf | None] = [
            None if left is None or right is None else abs(right - left)
            for left, right in zip(values, values[1:])
        ]
        deltas = [value for value in delta_values if value is not None]
    final_pair = None
    if len(values) >= 2 and values[-2] is not None and values[-1] is not None:
        with mp.workdps(120):
            final_pair = {
                "nodes": [nodes[-2], nodes[-1]],
                "absolute_S_difference_decimal": mp.nstr(
                    abs(values[-1] - values[-2]), 110
                ),
            }
    record = {
        "axis": name,
        "nodes": list(nodes),
        "S_values": [
            None if result is None else dict(result["S"]) for result in results
        ],
        "statuses": ["PASS" if value is not None else "FAIL" for value in values],
        "failure_reasons": list(failures),
        "missing_flag": any(value is None for value in values),
        "nonmonotonic_flag": any(
            later > earlier for earlier, later in zip(deltas, deltas[1:])
        ),
        "final_pair": final_pair,
        "adjacent_S_differences_decimal": [
            None if value is None else mp.nstr(value, 110) for value in delta_values
        ],
        "max_adjacent_S_difference_decimal": (
            mp.nstr(max(deltas), 110) if len(deltas) == len(nodes) - 1 else None
        ),
        "extrapolation_model": "bounded raw ladder; no production-domain closure",
        "remainder_estimate_decimal": (
            None if not deltas else mp.nstr(deltas[-1], 110)
        ),
        "selected_nodes_complete": all(value is not None for value in values)
        and len(nodes) >= 2,
        "closure_permitted": False,
        "phase6_declared_axis_nodes_complete": False,
    }
    if (
        name == "step_rstar"
        and tuple(nodes) == STEP_NODES
        and all(value is not None for value in values)
    ):
        with mp.workdps(120):
            coarse, middle, fine = values
            denominator = abs(middle - fine)
            record["extrapolation_model"] = "RK4 Richardson from 0.1/0.05/0.025"
            record["richardson_order"] = 4
            record["richardson_extrapolated_S"] = {
                "real": mp.nstr(mp.re(fine + (fine - middle) / 15), 100),
                "imag": mp.nstr(mp.im(fine + (fine - middle) / 15), 100),
            }
            record["remainder_estimate_decimal"] = mp.nstr(denominator / 15, 110)
            record["observed_refinement_ratio_decimal"] = (
                mp.nstr(abs(coarse - middle) / denominator, 110)
                if denominator
                else None
            )
    return record


def _mp_complex_record_checked(value: Mapping[str, object]) -> mp.mpc:
    if set(value) != {"real", "imag", "abs"}:
        raise RuntimeError("complex record schema mismatch")
    result = mp.mpc(mp.mpf(str(value["real"])), mp.mpf(str(value["imag"])))
    recorded_abs = mp.mpf(str(value["abs"]))
    if not all(
        mp.isfinite(item) for item in (mp.re(result), mp.im(result), recorded_abs)
    ):
        raise RuntimeError("complex record is non-finite")
    if recorded_abs < 0:
        raise RuntimeError("complex record absolute value is negative")
    digits = min(
        _decimal_significant_digits(str(value[field]))
        for field in ("real", "imag", "abs")
    )
    tolerance = max(
        max(abs(result), recorded_abs) * mp.power(10, -max(10, digits - 4)),
        mp.mpf("1e-10000"),
    )
    if abs(abs(result) - recorded_abs) > tolerance:
        raise RuntimeError("complex record absolute value is inconsistent")
    return result


def _decimal_significant_digits(value: str) -> int:
    mantissa = value.lower().split("e", maxsplit=1)[0].lstrip("+-")
    digits = "".join(character for character in mantissa if character.isdigit())
    significant = digits.lstrip("0")
    return max(1, len(significant))


def _comparison_complex_record(value: mp.mpc) -> dict[str, str]:
    # External comparison values are produced by float64 backends.  Serializing
    # their binary values with the active arbitrary-precision context would
    # advertise digits the backends never computed and can make ``abs`` look
    # inconsistent with the separately rounded real/imaginary components.
    # Round the components first at round-trip-safe float64 precision, then
    # derive the magnitude from exactly those serialized components.
    with mp.workdps(80):
        parsed = mp.mpc(value)
        real_text = mp.nstr(mp.re(parsed), 17)
        imag_text = mp.nstr(mp.im(parsed), 17)
        serialized = mp.mpc(mp.mpf(real_text), mp.mpf(imag_text))
        return {
            "real": real_text,
            "imag": imag_text,
            "abs": mp.nstr(abs(serialized), 17),
        }


def _external_complex(real: object, imag: object) -> mp.mpc:
    return mp.mpc(mp.mpf(str(real)), mp.mpf(str(imag)))


def _finite_state_relative_difference(
    left: Mapping[str, object], right: Mapping[str, object]
) -> str:
    left_states = left.get("finite_radius_states")
    right_states = right.get("finite_radius_states")
    if not isinstance(left_states, list) or not isinstance(right_states, list):
        raise RuntimeError("finite-radius states are absent")
    if [item.get("point_id") for item in left_states] != [
        item.get("point_id") for item in right_states
    ]:
        raise RuntimeError("finite-radius state point order mismatch")
    with mp.workdps(120):
        differences: list[mp.mpf] = []
        for left_state, right_state in zip(left_states, right_states):
            for key in ("psi_over_Ain", "dpsi_dr_over_Ain"):
                left_value = _mp_complex_record_checked(left_state[key])
                right_value = _mp_complex_record_checked(right_state[key])
                scale = max(abs(left_value), abs(right_value), mp.mpf("1e-1000"))
                differences.append(abs(left_value - right_value) / scale)
        return mp.nstr(max(differences, default=mp.mpf(0)), 110)


def _scipy_comparison(
    mode: MpmathMode, baseline: Mapping[str, object]
) -> dict[str, object]:
    sector = Sector(mode.sector)
    # The diagnostic regime label is non-operative.  Select the existing
    # project comparison route from the numerical key only.
    q018 = mode.ell >= 40.0 * mode.kM
    config = BoundaryConfig(
        r_in_eps=BASELINE_R_IN,
        r_out=BASELINE_R_OUT,
        rtol=1.0e-10,
        atol=1.0e-12,
        required_eval_radius=mode.evaluation_radius_M if q018 else None,
        experimental_required_radius_oracle="q018_riccati" if q018 else None,
        outer_basis="jost_1_over_r",
        outer_series_order=BASELINE_JOST,
    )
    solution = solve_radial_mode(
        sector, mode.ell, mode.kM, SchwarzschildBackground(M=1.0), config
    )
    scipy_s = _external_complex(solution.phase_factor.real, solution.phase_factor.imag)
    independent_s = _mp_complex_record_checked(baseline["S"])
    return {
        "backend": "project_scipy_jost_radial_solver",
        "status": "AVAILABLE",
        "genuinely_independent": False,
        "shared_components": [],
        "role": "cross-backend comparison only; not part of mpmath call graph",
        "solver": solution.diagnostics.solver,
        "actual_precision_bits": 53,
        "actual_decimal_digits": 15.95,
        "S": _comparison_complex_record(scipy_s),
        "absolute_S_difference_decimal": mp.nstr(abs(independent_s - scipy_s), 110),
        "no_phase_or_normalization_fit": True,
    }


def _mst_comparison(
    mode: MpmathMode, baseline: Mapping[str, object]
) -> dict[str, object]:
    mst = schwarzschild_mst_phase_factor(mode.ell, k=mode.kM, working_dps=70)
    raw_value = mst.odd if mode.sector == "odd" else mst.even
    value = _external_complex(raw_value.real, raw_value.imag)
    return {
        "backend": "local_mpmath_mst",
        "status": "AVAILABLE",
        "method": "MST recurrence",
        "genuinely_independent": False,
        "independence_role": "algorithmic internal cross-check; not source-independent external evidence",
        "even_independent_solve": False if mode.sector == "even" else None,
        "even_note": (
            "parity-derived; not an independent even radial solve"
            if mode.sector == "even"
            else None
        ),
        "requested_precision_dps": 70,
        "actual_precision_bits": 53,
        "actual_decimal_digits": 15.95,
        "recurrence_residual": mp.nstr(mp.mpf(str(mst.recurrence_residual)), 110),
        "S": _comparison_complex_record(value),
        "absolute_S_difference_decimal": mp.nstr(
            abs(_mp_complex_record_checked(baseline["S"]) - value), 110
        ),
        "no_phase_or_normalization_fit": True,
    }


def _bhpt_comparison(
    mode: MpmathMode,
    baseline: Mapping[str, object],
    records: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    matches = [
        record
        for record in records
        if mp.mpf(str(record["kM"])) == mp.mpf(str(mode.kM))
        and int(record["ell"]) == mode.ell
    ]
    if not matches:
        return _external_comparison_failure(
            "frozen_external_bhpt_reggewheeler_mst",
            mode,
            RuntimeError("frozen BHPT MST artifact does not cover this key"),
        )
    if len(matches) != 1:
        raise RuntimeError("BHPT key is not unique")
    key = "odd" if mode.sector == "odd" else "even_from_chandrasekhar"
    value_record = matches[0][key]
    value = _external_complex(value_record["real"], value_record["imag"])
    return {
        "backend": "frozen_external_bhpt_reggewheeler_mst",
        "status": "AVAILABLE",
        "method": "MST",
        "genuinely_independent": mode.sector == "odd",
        "even_independent_solve": False if mode.sector == "even" else None,
        "even_note": (
            "Chandrasekhar parity-derived; not an independent even solve"
            if mode.sector == "even"
            else None
        ),
        "actual_precision_bits": 53,
        "actual_decimal_digits": 15.95,
        "S": _comparison_complex_record(value),
        "absolute_S_difference_decimal": mp.nstr(
            abs(_mp_complex_record_checked(baseline["S"]) - value), 110
        ),
        "no_phase_or_normalization_fit": True,
    }


def _external_comparison_failure(
    backend: str,
    mode: MpmathMode,
    exc: Exception,
) -> dict[str, object]:
    common = {
        "backend": backend,
        "status": "OPEN_OR_FAIL_CLOSED",
        "genuinely_independent": False,
        "blocker": f"{type(exc).__name__}: {exc}",
    }
    if backend == "project_scipy_jost_radial_solver":
        return {
            **common,
            "shared_components": [],
            "role": "cross-backend comparison only; not part of mpmath call graph",
            "actual_precision_bits": 53,
            "actual_decimal_digits": 15.95,
        }
    if backend == "local_mpmath_mst":
        return {
            **common,
            "even_independent_solve": False if mode.sector == "even" else None,
            "requested_precision_dps": 70,
            "actual_precision_bits": 53,
            "actual_decimal_digits": 15.95,
        }
    if backend == "frozen_external_bhpt_reggewheeler_mst":
        return {
            **common,
            "even_independent_solve": False if mode.sector == "even" else None,
            "actual_precision_bits": 53,
            "actual_decimal_digits": 15.95,
        }
    raise RuntimeError("unknown external comparison backend")


def _collect_external_comparisons(
    mode: MpmathMode,
    baseline: Mapping[str, object],
    bhpt_records: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    comparisons = (
        (
            "project_scipy_jost_radial_solver",
            lambda: _scipy_comparison(mode, baseline),
        ),
        ("local_mpmath_mst", lambda: _mst_comparison(mode, baseline)),
        (
            "frozen_external_bhpt_reggewheeler_mst",
            lambda: _bhpt_comparison(mode, baseline, bhpt_records),
        ),
    )
    results: list[dict[str, object]] = []
    for backend, function in comparisons:
        try:
            result = function()
            if result.get("backend") != backend:
                raise RuntimeError(
                    "comparison returned a noncanonical backend identity"
                )
        except Exception as exc:
            result = _external_comparison_failure(backend, mode, exc)
        results.append(result)
    return results


def _mode_evidence(
    mode: MpmathMode,
    mode_root: Path,
    bhpt_records: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    checkpoint_identities: list[dict[str, object]] = []
    precision_batches: dict[int, Mapping[str, object] | None] = {}
    precision_failures: dict[int, str | None] = {}
    for dps in PRECISION_NODES:
        identity, batch, failure = _run_batch(
            mode,
            mode_root,
            label=f"precision_dps_{dps}",
            dps=dps,
            r_in_eps=BASELINE_R_IN,
            step=BASELINE_STEP,
            r_out_nodes=R_OUT_NODES,
            jost_orders=JOST_NODES,
        )
        checkpoint_identities.append(identity)
        precision_batches[dps] = batch
        precision_failures[dps] = failure

    extra_batches: dict[str, Mapping[str, object] | None] = {}
    extra_failures: dict[str, str | None] = {}
    for step in STEP_NODES[:-1]:
        label = f"step_rstar_{str(step).replace('.', 'p')}"
        identity, batch, failure = _run_batch(
            mode,
            mode_root,
            label=label,
            dps=70,
            r_in_eps=BASELINE_R_IN,
            step=step,
            r_out_nodes=(BASELINE_R_OUT,),
            jost_orders=(BASELINE_JOST,),
        )
        checkpoint_identities.append(identity)
        extra_batches[label] = batch
        extra_failures[label] = failure
    for r_in in (R_IN_NODES[0], R_IN_NODES[-1]):
        label = f"r_in_eps_{r_in:.0e}".replace("-", "m")
        identity, batch, failure = _run_batch(
            mode,
            mode_root,
            label=label,
            dps=70,
            r_in_eps=r_in,
            step=BASELINE_STEP,
            r_out_nodes=(BASELINE_R_OUT,),
            jost_orders=(BASELINE_JOST,),
        )
        checkpoint_identities.append(identity)
        extra_batches[label] = batch
        extra_failures[label] = failure

    def extract(
        batch: Mapping[str, object] | None, r_out: float, order: int
    ) -> Mapping[str, object] | None:
        return (
            None if batch is None else result_for(batch, r_out=r_out, jost_order=order)
        )

    precision_results = [
        extract(precision_batches[dps], BASELINE_R_OUT, BASELINE_JOST)
        for dps in PRECISION_NODES
    ]
    baseline = precision_results[-1]
    blockers: list[str] = []
    if baseline is None:
        blockers.append(f"100-dps baseline failed: {precision_failures[100]}")
        return (
            {
                "mode": mode.to_metadata(),
                "status": "FAIL_CLOSED_NUMERICAL_INSTABILITY",
                "baseline": None,
                "ladders": {
                    "precision_dps": _axis_record(
                        "precision_dps",
                        PRECISION_NODES,
                        precision_results,
                        [precision_failures[dps] for dps in PRECISION_NODES],
                    ),
                    "step_rstar": _axis_record(
                        "step_rstar",
                        STEP_NODES,
                        [None] * len(STEP_NODES),
                        ["baseline unavailable"] * len(STEP_NODES),
                    ),
                    "r_in_eps": _axis_record(
                        "r_in_eps",
                        R_IN_NODES,
                        [None] * len(R_IN_NODES),
                        ["baseline unavailable"] * len(R_IN_NODES),
                    ),
                    "r_out_M": _axis_record(
                        "r_out_M",
                        R_OUT_NODES,
                        [None] * len(R_OUT_NODES),
                        ["baseline unavailable"] * len(R_OUT_NODES),
                    ),
                    "jost_order": _axis_record(
                        "jost_order",
                        JOST_NODES,
                        [None] * len(JOST_NODES),
                        ["baseline unavailable"] * len(JOST_NODES),
                    ),
                },
                "external_comparisons": [],
                "numerical_uncertainty": {"closed": False},
                "convention_uncertainty": {"closed": False},
                "blockers": blockers,
                "closure_blockers": [
                    "bounded Stage-A nodes omit the full declared Phase-6 ladder",
                    "AP fixed-step ladder is not the production adaptive-tolerance ladder",
                    "full 17,818-key policy-extended union domain is not evaluated",
                ],
                "checkpoint_identities": checkpoint_identities,
            },
            checkpoint_identities,
        )

    step_labels = [
        f"step_rstar_{str(step).replace('.', 'p')}" for step in STEP_NODES[:-1]
    ]
    step_results = [
        extract(extra_batches[label], BASELINE_R_OUT, BASELINE_JOST)
        for label in step_labels
    ] + [extract(precision_batches[70], BASELINE_R_OUT, BASELINE_JOST)]
    r_in_labels = [
        f"r_in_eps_{R_IN_NODES[0]:.0e}".replace("-", "m"),
        None,
        f"r_in_eps_{R_IN_NODES[-1]:.0e}".replace("-", "m"),
    ]
    r_in_results = [
        extract(extra_batches[r_in_labels[0]], BASELINE_R_OUT, BASELINE_JOST),
        extract(precision_batches[70], BASELINE_R_OUT, BASELINE_JOST),
        extract(extra_batches[r_in_labels[-1]], BASELINE_R_OUT, BASELINE_JOST),
    ]
    r_out_results = [
        extract(precision_batches[70], radius, BASELINE_JOST) for radius in R_OUT_NODES
    ]
    jost_results = [
        extract(precision_batches[70], BASELINE_R_OUT, order) for order in JOST_NODES
    ]
    ladders = {
        "precision_dps": _axis_record(
            "precision_dps",
            PRECISION_NODES,
            precision_results,
            [precision_failures[dps] for dps in PRECISION_NODES],
        ),
        "step_rstar": _axis_record(
            "step_rstar",
            STEP_NODES,
            step_results,
            [extra_failures[label] for label in step_labels] + [precision_failures[70]],
        ),
        "r_in_eps": _axis_record(
            "r_in_eps",
            R_IN_NODES,
            r_in_results,
            [
                extra_failures[r_in_labels[0]],
                precision_failures[70],
                extra_failures[r_in_labels[-1]],
            ],
        ),
        "r_out_M": _axis_record(
            "r_out_M",
            R_OUT_NODES,
            r_out_results,
            [precision_failures[70], precision_failures[70]],
        ),
        "jost_order": _axis_record(
            "jost_order",
            JOST_NODES,
            jost_results,
            [precision_failures[70]] * len(JOST_NODES),
        ),
    }
    finite_precision_deltas: list[str] = []
    finite_step_deltas: list[str] = []
    finite_state_failure: str | None = None
    try:
        if any(item is None for item in precision_results + step_results):
            raise RuntimeError("finite-state ladder contains a missing node")
        finite_precision_deltas = [
            _finite_state_relative_difference(left, right)
            for left, right in zip(precision_results, precision_results[1:])
        ]
        finite_step_deltas = [
            _finite_state_relative_difference(left, right)
            for left, right in zip(step_results, step_results[1:])
        ]
    except Exception as exc:
        finite_state_failure = f"{type(exc).__name__}: {exc}"
    finite_state_ladder = {
        "precision_nodes_dps": list(PRECISION_NODES),
        "precision_max_relative_state_differences_decimal": finite_precision_deltas,
        "step_nodes_rstar": list(STEP_NODES),
        "step_max_relative_state_differences_decimal": finite_step_deltas,
        "missing_flag": finite_state_failure is not None,
        "failure_reason": finite_state_failure,
        "precision_nonmonotonic_flag": any(
            mp.mpf(later) > mp.mpf(earlier)
            for earlier, later in zip(
                finite_precision_deltas, finite_precision_deltas[1:]
            )
        ),
        "step_nonmonotonic_flag": any(
            mp.mpf(later) > mp.mpf(earlier)
            for earlier, later in zip(finite_step_deltas, finite_step_deltas[1:])
        ),
        "closure_permitted": False,
    }
    external = _collect_external_comparisons(mode, baseline, bhpt_records)
    flux = baseline["signed_flux"]
    wronskian = baseline["wronskian"]
    matching = baseline["matching"]
    flux_blockers: list[str] = []
    scattering_blockers: list[str] = []
    finite_state_blockers: list[str] = []
    if flux["transmission_resolved_at_actual_precision"] is not True:
        flux_blockers.append(
            "horizon transmission is below the 100-dps resolution margin"
        )
    if mp.mpf(str(flux["relative_balance_residual"])) > mp.mpf("1e-5"):
        flux_blockers.append(
            "signed flux balance residual exceeds bounded 1e-5 diagnostic"
        )
    if mp.mpf(str(wronskian["maximum_relative_current_drift"])) > mp.mpf("1e-5"):
        flux_blockers.append("Wronskian/current drift exceeds bounded 1e-5 diagnostic")
    if mp.mpf(str(matching["reconstruction_residual"])) > mp.mpf("1e-25"):
        scattering_blockers.append("independent Jost matching residual exceeds 1e-25")
    if matching.get("selected_jost_gate_passed") is not True:
        scattering_blockers.append(
            "selected Jost node failed tail/conjugacy/determinant/condition gates"
        )
    precision_delta_record = ladders["precision_dps"][
        "max_adjacent_S_difference_decimal"
    ]
    precision_delta = (
        None if precision_delta_record is None else mp.mpf(precision_delta_record)
    )
    if precision_delta is None or precision_delta > mp.mpf("1e-20"):
        scattering_blockers.append("50/70/100-dps S ladder is not converged to 1e-20")
    axis_limits = {
        "precision_dps": "1e-20",
        "step_rstar": "2e-6",
        "r_in_eps": "5e-5",
        "r_out_M": "1e-8",
        "jost_order": "1e-10",
    }
    for axis_name, axis in ladders.items():
        if axis["missing_flag"]:
            scattering_blockers.append(f"{axis_name} bounded ladder has a missing node")
        if axis["nonmonotonic_flag"]:
            scattering_blockers.append(f"{axis_name} bounded ladder is nonmonotonic")
        delta_record = axis["max_adjacent_S_difference_decimal"]
        delta = None if delta_record is None else mp.mpf(delta_record)
        if delta is None or delta > mp.mpf(axis_limits[axis_name]):
            scattering_blockers.append(
                f"{axis_name} bounded ladder exceeds {axis_limits[axis_name]}"
            )
    step_remainder_record = ladders["step_rstar"]["remainder_estimate_decimal"]
    step_remainder = (
        None if step_remainder_record is None else mp.mpf(step_remainder_record)
    )
    if step_remainder is None or step_remainder > mp.mpf("2e-7"):
        scattering_blockers.append("RK4 Richardson step remainder exceeds 2e-7")
    if finite_state_ladder["missing_flag"]:
        finite_state_blockers.append("finite-state precision/step ladder is incomplete")
    if finite_state_ladder["precision_nonmonotonic_flag"]:
        finite_state_blockers.append("finite-state precision ladder is nonmonotonic")
    if finite_state_ladder["step_nonmonotonic_flag"]:
        finite_state_blockers.append("finite-state step ladder is nonmonotonic")
    if not finite_precision_deltas or mp.mpf(finite_precision_deltas[-1]) > mp.mpf(
        "1e-18"
    ):
        finite_state_blockers.append(
            "finite-state 70/100-dps relative difference exceeds 1e-18"
        )
    if not finite_step_deltas or mp.mpf(finite_step_deltas[-1]) > mp.mpf("2e-6"):
        finite_state_blockers.append(
            "finite-state 0.05/0.025 relative difference exceeds 2e-6"
        )
    blockers.extend(scattering_blockers)
    blockers.extend(finite_state_blockers)
    blockers.extend(flux_blockers)
    measured = [
        mp.mpf(axis["max_adjacent_S_difference_decimal"])
        for axis in ladders.values()
        if axis["max_adjacent_S_difference_decimal"] is not None
    ]
    independent_differences = [
        mp.mpf(str(item["absolute_S_difference_decimal"]))
        for item in external
        if item.get("genuinely_independent") is True
        and item.get("absolute_S_difference_decimal") is not None
    ]
    conservative = max(measured + independent_differences, default=None)
    return (
        {
            "mode": mode.to_metadata(),
            "status": (
                "STABLE_SELECTED_ANCHOR_INCOMPLETE_LADDERS"
                if not blockers
                else "FAIL_CLOSED_NUMERICAL_INSTABILITY"
            ),
            "baseline": baseline,
            "S_status": (
                "STABLE_BOUNDED_SELECTED_NODES"
                if not scattering_blockers
                else "FAIL_CLOSED_DISCRETIZATION_OR_MATCHING"
            ),
            "finite_radius_state_status": (
                "STABLE_BOUNDED_SELECTED_NODES"
                if not finite_state_blockers
                else "FAIL_CLOSED_UNRESOLVED_FINITE_STATE"
            ),
            "finite_radius_state_ladder": finite_state_ladder,
            "flux_status": (
                "RESOLVED_INTERNAL_FLUX_ACCOUNTING"
                if not flux_blockers
                else "FAIL_CLOSED_UNRESOLVED_OR_UNBALANCED_FLUX"
            ),
            "ladders": ladders,
            "external_comparisons": external,
            "numerical_uncertainty": {
                "metric": "absolute complex S difference",
                "conservative_max_over_ladders_and_independent_backends_decimal": (
                    None if conservative is None else mp.nstr(conservative, 110)
                ),
                "closed": False,
                "reason": "bounded Stage-A anchors do not close full V1 uncertainty",
            },
            "convention_uncertainty": {
                "Fourier_convention": "exp(-i k t)",
                "S_definition": "-unit_incoming_A_out/[(-1)^ell unit_incoming_A_in]",
                "tortoise_definition": "r+2 log(r/2-1)",
                "phase_or_normalization_fit": False,
                "closed": False,
            },
            "blockers": blockers,
            "closure_blockers": [
                "bounded Stage-A nodes omit the full declared Phase-6 ladder",
                "AP fixed-step ladder is not the production adaptive-tolerance ladder",
                "full 17,818-key policy-extended union domain is not evaluated",
            ],
            "checkpoint_identities": checkpoint_identities,
        },
        checkpoint_identities,
    )


def _runtime_cost(records: Sequence[Mapping[str, object]]) -> dict[str, object]:
    by_dps: dict[str, list[tuple[float, int]]] = {
        str(dps): [] for dps in PRECISION_NODES
    }
    for record in records:
        for checkpoint in record["checkpoint_identities"]:
            path = Path(checkpoint["path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            batch = payload.get("batch")
            if not isinstance(batch, Mapping):
                continue
            dps = str(batch["configuration"]["working_dps"])
            if dps in by_dps:
                by_dps[dps].append(
                    (float(batch["elapsed_seconds"]), int(batch["integration_steps"]))
                )
    return {
        "by_working_dps": {
            dps: {
                "run_count": len(values),
                "total_seconds": sum(value[0] for value in values),
                "total_steps": sum(value[1] for value in values),
                "seconds_per_step": (
                    sum(value[0] for value in values)
                    / sum(value[1] for value in values)
                    if values and sum(value[1] for value in values)
                    else None
                ),
            }
            for dps, values in by_dps.items()
        },
        "optimization": (
            "every selected mode uses one outward horizon integration across the "
            "match/eight finite radii; each inward two-basis integration is reused "
            "across the same eight finite radii"
        ),
        "full_domain_runtime_extrapolation_permitted": False,
    }


def _validate_output_destination(output_root: Path) -> None:
    if output_root.exists() or output_root.is_symlink():
        raise FileExistsError(f"output root exists: {output_root}")
    if output_root != output_root.resolve(strict=False):
        raise RuntimeError("Phase-6 AP output root must be an absolute canonical path")
    expected_parent = RADIAL_VALIDATION_ROOT.resolve(strict=True)
    if output_root.parent.resolve(strict=True) != expected_parent:
        raise RuntimeError(
            "Phase-6 AP output root must be a direct validation-root child"
        )


def _seal_output_root(output_root: Path) -> None:
    checkpoint_root = output_root / "mode_checkpoints"
    if checkpoint_root.is_dir() and not checkpoint_root.is_symlink():
        for mode in selected_stage_a_modes():
            mode_root = checkpoint_root / mode.mode_id
            if mode_root.is_dir() and not mode_root.is_symlink():
                os.chmod(mode_root, 0o555)
        os.chmod(checkpoint_root, 0o555)
    os.chmod(output_root, 0o555)
    _fsync_directory(output_root.parent)


def _ensure_failure_terminals(
    output_root: Path,
    *,
    stage: str,
    active_mode_id: str | None,
    exc: Exception,
) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    checkpoint_root = output_root / "mode_checkpoints"
    checkpoint_root.mkdir(mode=0o700, exist_ok=True)
    identities: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []
    failure = _mode_failure_record(stage, exc)
    for mode_index, mode in enumerate(selected_stage_a_modes()):
        mode_root = checkpoint_root / mode.mode_id
        try:
            mode_root.mkdir(mode=0o700, exist_ok=True)
            terminal_path = mode_root / "terminal.json"
            if not terminal_path.exists() and not terminal_path.is_symlink():
                checkpoints = _checkpoint_prefix(mode_root)
                execution_status = (
                    "EXECUTION_FAILED"
                    if mode.mode_id == active_mode_id or checkpoints
                    else "NOT_STARTED_DUE_TO_RUN_FAILURE"
                )
                _publish_mode_terminal(
                    mode_index=mode_index,
                    mode=mode,
                    mode_root=mode_root,
                    execution_status=execution_status,
                    mode_evidence=None,
                    failure=failure,
                )
            payload = _reload_canonical_json(terminal_path)
            _validate_mode_terminal(
                payload,
                mode_index=mode_index,
                mode=mode,
                mode_root=mode_root,
            )
            identities.append(_existing_published_identity(terminal_path))
        except Exception as terminal_exc:
            errors.append(
                {
                    "mode_id": mode.mode_id,
                    "error": f"{type(terminal_exc).__name__}: {terminal_exc}",
                }
            )
    return identities, errors


def _publish_run_failure(
    output_root: Path,
    *,
    stage: str,
    active_mode_id: str | None,
    exc: Exception,
) -> dict[str, object]:
    terminal_identities, terminal_errors = _ensure_failure_terminals(
        output_root,
        stage=stage,
        active_mode_id=active_mode_id,
        exc=exc,
    )
    status_counts = {status: 0 for status in MODE_EXECUTION_STATUSES}
    checkpoint_root = output_root / "mode_checkpoints"
    for mode in selected_stage_a_modes():
        terminal_path = checkpoint_root / mode.mode_id / "terminal.json"
        try:
            payload = _reload_canonical_json(terminal_path)
        except Exception:
            continue
        status = payload.get("execution_status")
        if status in status_counts:
            status_counts[status] += 1
    payload = {
        "schema_version": RUN_FAILURE_SCHEMA,
        "status": "FAIL_CLOSED_EXECUTION",
        "output_root": str(output_root.resolve(strict=True)),
        "runner_identity": _source_identity(Path(__file__)),
        "backend_identity": _source_identity(BACKEND_SOURCE),
        "stage": stage,
        "active_mode_id": active_mode_id,
        "failure": _mode_failure_record(stage, exc),
        "expected_mode_order": [
            mode.to_metadata() for mode in selected_stage_a_modes()
        ],
        "mode_terminal_identities": terminal_identities,
        "mode_terminal_errors": terminal_errors,
        "mode_execution_status_counts": status_counts,
        "terminal_protocol_complete": (
            not terminal_errors
            and len(terminal_identities) == len(selected_stage_a_modes())
        ),
        "published_success_artifacts": {
            filename: (output_root / filename).is_file()
            for filename in (
                "selected_anchor_evidence.json",
                "manifest.json",
                "checkpoint.json",
            )
        },
        "global_green_permitted": False,
        "paper_figure_runs": 0,
    }
    identity = _publish_terminal_json(output_root / "failure.json", payload)
    reloaded = _reload_canonical_json(output_root / "failure.json")
    if reloaded != payload or set(reloaded) != {
        "schema_version",
        "status",
        "output_root",
        "runner_identity",
        "backend_identity",
        "stage",
        "active_mode_id",
        "failure",
        "expected_mode_order",
        "mode_terminal_identities",
        "mode_terminal_errors",
        "mode_execution_status_counts",
        "terminal_protocol_complete",
        "published_success_artifacts",
        "global_green_permitted",
        "paper_figure_runs",
    }:
        raise RuntimeError("top-level failure artifact reload/schema mismatch")
    expected_modes = selected_stage_a_modes()
    expected_mode_ids = {mode.mode_id for mode in expected_modes}
    failure = reloaded.get("failure")
    terminal_identities_record = reloaded.get("mode_terminal_identities")
    terminal_errors_record = reloaded.get("mode_terminal_errors")
    status_counts_record = reloaded.get("mode_execution_status_counts")
    published_record = reloaded.get("published_success_artifacts")
    if (
        reloaded["schema_version"] != RUN_FAILURE_SCHEMA
        or reloaded["status"] != "FAIL_CLOSED_EXECUTION"
        or reloaded["output_root"] != str(output_root.resolve(strict=True))
        or reloaded["expected_mode_order"]
        != [mode.to_metadata() for mode in expected_modes]
        or reloaded["active_mode_id"] not in expected_mode_ids | {None}
        or not isinstance(failure, Mapping)
        or set(failure) != {"stage", "exception_type", "message"}
        or failure.get("stage") != reloaded["stage"]
        or any(
            not isinstance(failure.get(field), str) or not failure[field]
            for field in ("stage", "exception_type", "message")
        )
        or not isinstance(terminal_identities_record, list)
        or not isinstance(terminal_errors_record, list)
        or any(
            not isinstance(error, Mapping)
            or set(error) != {"mode_id", "error"}
            or error.get("mode_id") not in expected_mode_ids
            or not isinstance(error.get("error"), str)
            or not error["error"]
            for error in terminal_errors_record
        )
        or not isinstance(status_counts_record, Mapping)
        or set(status_counts_record) != MODE_EXECUTION_STATUSES
        or any(
            not isinstance(count, int) or isinstance(count, bool) or count < 0
            for count in status_counts_record.values()
        )
        or sum(status_counts_record.values()) > len(expected_modes)
        or not isinstance(published_record, Mapping)
        or set(published_record)
        != {
            "selected_anchor_evidence.json",
            "manifest.json",
            "checkpoint.json",
        }
        or any(not isinstance(value, bool) for value in published_record.values())
        or published_record
        != {
            filename: (output_root / filename).is_file()
            for filename in (
                "selected_anchor_evidence.json",
                "manifest.json",
                "checkpoint.json",
            )
        }
        or not isinstance(reloaded["terminal_protocol_complete"], bool)
        or reloaded["global_green_permitted"] is not False
        or reloaded["paper_figure_runs"] != 0
    ):
        raise RuntimeError("top-level failure artifact invariant mismatch")
    if reloaded["runner_identity"] != _source_identity(
        Path(__file__).resolve(strict=True)
    ) or reloaded["backend_identity"] != _source_identity(
        BACKEND_SOURCE.resolve(strict=True)
    ):
        raise RuntimeError("top-level failure source identity drift")
    terminal_positions: list[int] = []
    for terminal_identity in terminal_identities_record:
        if not isinstance(terminal_identity, Mapping):
            raise RuntimeError("top-level mode terminal identity is malformed")
        path = Path(str(terminal_identity.get("path")))
        matches = [
            index
            for index, mode in enumerate(expected_modes)
            if path == output_root / "mode_checkpoints" / mode.mode_id / "terminal.json"
        ]
        if len(matches) != 1:
            raise RuntimeError("top-level mode terminal key binding mismatch")
        terminal_positions.append(matches[0])
        _validate_published_identity(terminal_identity, expected_path=path)
    if terminal_positions != sorted(set(terminal_positions)):
        raise RuntimeError("top-level mode terminal order/cardinality mismatch")
    if reloaded["terminal_protocol_complete"] is True and (
        terminal_errors_record
        or len(terminal_identities_record) != len(expected_modes)
        or sum(status_counts_record.values()) != len(expected_modes)
    ):
        raise RuntimeError("top-level failure terminal completion claim mismatch")
    _validate_published_identity(identity, expected_path=output_root / "failure.json")
    return identity


def _validate_success_reload(
    output_root: Path,
    *,
    evidence: Mapping[str, object],
    evidence_identity: Mapping[str, object],
    manifest: Mapping[str, object],
    manifest_identity: Mapping[str, object],
    checkpoint: Mapping[str, object],
    checkpoint_identity: Mapping[str, object],
    mode_terminal_identities: Sequence[Mapping[str, object]],
) -> None:
    reloaded_evidence = _reload_canonical_json(
        output_root / "selected_anchor_evidence.json"
    )
    reloaded_manifest = _reload_canonical_json(output_root / "manifest.json")
    reloaded_checkpoint = _reload_canonical_json(output_root / "checkpoint.json")
    if reloaded_evidence != evidence:
        raise RuntimeError("final evidence reload mismatch")
    validate_stage_a_evidence(reloaded_evidence)
    if reloaded_manifest != manifest or set(reloaded_manifest) != {
        "schema_version",
        "created_at_utc",
        "elapsed_seconds",
        "python",
        "mpmath",
        "evidence",
        "checkpoint_identities",
        "mode_terminal_identities",
        "source_identities",
        "input_contract",
        "input_sha256",
        "full_domain_runs",
        "paper_figure_runs",
        "global_green_permitted",
    }:
        raise RuntimeError("final manifest reload/schema mismatch")
    if reloaded_checkpoint != checkpoint or set(reloaded_checkpoint) != {
        "schema_version",
        "status",
        "evidence",
        "manifest",
        "mode_terminal_identities",
        "covered_key_count",
        "production_missing_key_count",
        "policy_extended_union_missing_key_count",
        "mode_statuses",
        "global_green_permitted",
    }:
        raise RuntimeError("final checkpoint reload/schema mismatch")
    if (
        reloaded_manifest["evidence"] != evidence_identity
        or reloaded_manifest["mode_terminal_identities"]
        != list(mode_terminal_identities)
        or reloaded_checkpoint["evidence"] != evidence_identity
        or reloaded_checkpoint["manifest"] != manifest_identity
        or reloaded_checkpoint["mode_terminal_identities"]
        != list(mode_terminal_identities)
    ):
        raise RuntimeError("final artifact identity binding mismatch")
    _validate_published_identity(
        evidence_identity,
        expected_path=output_root / "selected_anchor_evidence.json",
    )
    _validate_published_identity(
        manifest_identity,
        expected_path=output_root / "manifest.json",
    )
    _validate_published_identity(
        checkpoint_identity,
        expected_path=output_root / "checkpoint.json",
    )
    reloaded_modes, reloaded_terminal_identities = _reload_mode_terminals(
        output_root / "mode_checkpoints",
        require_all_completed=True,
    )
    if reloaded_modes != evidence["modes"] or reloaded_terminal_identities != list(
        mode_terminal_identities
    ):
        raise RuntimeError("final mode terminal reload/order mismatch")


def _stage_a_source_paths() -> tuple[Path, ...]:
    """Return every source/input identity bound by one Stage-A execution."""

    return (
        Path(__file__),
        BACKEND_SOURCE,
        ROOT / "scripts/verify_fig2_high_precision.py",
        ROOT / "src/schwgw/numerics/radial_solver.py",
        ROOT / "src/schwgw/numerics/matching.py",
        ROOT / "src/schwgw/scattering/mst.py",
        ROOT / "docs/phase6_independent_physical_validation.md",
        ROOT / "configs/phase6_independent_physical_validation.yaml",
        BHPT_EVIDENCE,
        V6B_EVIDENCE,
        V1_DIAGNOSTIC_ROOT / "selected_anchor_evidence.json",
        V2_DIAGNOSTIC_ROOT / "selected_anchor_evidence.json",
        V3_DIAGNOSTIC_ROOT / "selected_anchor_evidence.json",
        DOMAIN_FREEZE_ROOT / "D_prod.jsonl",
        DOMAIN_FREEZE_ROOT / "D_ext.jsonl",
        DOMAIN_FREEZE_ROOT / "D_required.jsonl",
        DOMAIN_FREEZE_ROOT / "D_union.jsonl",
        DOMAIN_FREEZE_ROOT / "domain_contract.json",
        DOMAIN_FREEZE_ROOT / "manifest.json",
        EXECUTION_CONTRACT_ROOT / "execution_contract.json",
        EXECUTION_CONTRACT_ROOT / "manifest.json",
        Path(mp.__file__),
    )


def _run_allocated(
    output_root: Path,
    execution_state: dict[str, str | None],
) -> dict[str, object]:
    checkpoint_root = output_root / "mode_checkpoints"
    execution_state["stage"] = "runtime_identity"
    runtime_identity = _runtime_identity(output_root)
    execution_state["stage"] = "source_identity_snapshot"
    source_paths = _stage_a_source_paths()
    source_identities = [_source_identity(path) for path in source_paths]
    started = time.perf_counter()
    execution_state["stage"] = "call_graph_isolation"
    isolation = prove_call_graph_isolation(BACKEND_SOURCE)
    execution_state["stage"] = "external_bhpt_input_reload"
    bhpt = json.loads(BHPT_EVIDENCE.read_text(encoding="utf-8"))
    for mode_index, mode in enumerate(selected_stage_a_modes()):
        execution_state["stage"] = f"mode:{mode.mode_id}"
        execution_state["active_mode_id"] = mode.mode_id
        mode_root = checkpoint_root / mode.mode_id
        record, identities = _mode_evidence(mode, mode_root, bhpt["records"])
        checkpoint_identities = _checkpoint_prefix(mode_root)
        if (
            identities != checkpoint_identities
            or record.get("checkpoint_identities") != checkpoint_identities
        ):
            raise RuntimeError("mode result/checkpoint order or identity mismatch")
        _publish_mode_terminal(
            mode_index=mode_index,
            mode=mode,
            mode_root=mode_root,
            execution_status="COMPLETED",
            mode_evidence=record,
            failure=None,
        )
        execution_state["active_mode_id"] = None
    execution_state["stage"] = "mode_terminal_reload"
    modes, mode_terminal_identities = _reload_mode_terminals(
        checkpoint_root,
        require_all_completed=True,
    )
    checkpoint_identities = [
        dict(identity)
        for record in modes
        for identity in record["checkpoint_identities"]
    ]
    for mode in selected_stage_a_modes():
        os.chmod(checkpoint_root / mode.mode_id, 0o555)
    os.chmod(checkpoint_root, 0o555)

    execution_state["stage"] = "source_identity_recheck"
    if [_source_identity(path) for path in source_paths] != source_identities:
        raise RuntimeError("Stage-A source/input identity changed during execution")
    input_contract = {
        "modes": [mode.to_metadata() for mode in selected_stage_a_modes()],
        "precision_dps": list(PRECISION_NODES),
        "r_in_eps": list(R_IN_NODES),
        "r_out_M": list(R_OUT_NODES),
        "jost_order": list(JOST_NODES),
        "maximum_step_rstar": list(STEP_NODES),
        "pilot_match_radius_M": 60.0,
        "evaluation_points": [
            point.to_metadata() for point in STAGE_A_EVALUATION_POINTS
        ],
    }
    input_sha256 = hashlib.sha256(_canonical_bytes(input_contract)).hexdigest()
    evaluation_points_payload = [
        point.to_metadata() for point in STAGE_A_EVALUATION_POINTS
    ]
    evaluation_points_sha256 = hashlib.sha256(
        _canonical_bytes(evaluation_points_payload)
    ).hexdigest()
    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "scope": "bounded_selected_anchor_pilot",
        "overall_status": "YELLOW_SELECTED_ANCHORS_ONLY",
        "global_green_permitted": False,
        "runtime_identity": runtime_identity,
        "execution_contract": {
            "root": str(EXECUTION_CONTRACT_ROOT.resolve(strict=True)),
            "contract_sha256": "25ad4b4e723edbd44651edaa63df415141de504b85288b12c2a6a973fcb420ab",
            "manifest_sha256": "1de9d445d888cbb5ddbf426cc062d2fb5128cad111437ce7d147df6e004aed48",
            "payload_role": "bounded Stage-A calibration payload",
            "resumable_full_shard_pass": False,
        },
        "evaluation_point_contract": {
            "points": evaluation_points_payload,
            "sha256": evaluation_points_sha256,
            "role": "Stage-A runner-frozen finite-state requests; generic backend input",
        },
        "declared_domain": {
            "covered_keys": [mode.to_metadata() for mode in selected_stage_a_modes()],
            "covered_key_count": 8,
            "production_deduplicated_key_count": 16048,
            "production_missing_key_count": 16040,
            "policy_extended_union_key_count": 17818,
            "policy_extended_union_missing_key_count": 17810,
            "audit_extension_key_count": 1770,
            "audit_required_key_count": 3392,
            "production_required_overlap_count": 1622,
            "inventory_provenance": "immutable T8 v1 domain freeze v3",
            "counts_claim_scope": "exact immutable domain manifests",
            "exact_domain_manifests_available": True,
            "domain_freeze": {
                "root": str(DOMAIN_FREEZE_ROOT.resolve(strict=True)),
                "D_prod_sha256": "54f13ea2473fb0a04ca5e16277edae31335c03b11753973d83a934cce2f0872b",
                "D_ext_sha256": "ec41b9c7898344717f8d290525a2462461dc3614d7fb0b75fe5c8ae4b1e80bfe",
                "D_required_sha256": "2468dbac29608bbfd7faa4143f9632fe3134df1c6a162cdbfbeeba15b7b3e021",
                "D_union_sha256": "a5793564dfc28e815699966208ae6605eeeedce9e3629f09512b70e08196810b",
                "domain_contract_sha256": "7ed99b905c3a1301d96101f357ab1fd9f4bc6e9a4922cb242d28e7cf06bb3bcf",
                "manifest_sha256": "f11d127e0bcfafa8f2fe24b2d3cec3e0cedc60f644d4285e6d52e53d8358d2d2",
            },
            "full_v1_domain_complete": False,
        },
        "backend_identity": {
            "name": "independent_mpmath_rw_zerilli_rk4_jost",
            "implementation_version": "schwgw_phase6_independent_mpmath_radial_backend_v1",
            "implementation_source_sha256": isolation["source_sha256"],
            "actual_backend": f"mpmath {mp.__version__}",
            "genuinely_independent": True,
            "input_sha256": input_sha256,
            "dependency_hashes": {
                "mpmath_source_sha256": _sha256(Path(mp.__file__)),
            },
            "shared_components": [
                "RW/Zerilli equations and scattering conventions only"
            ],
            "call_graph_isolation": "AST/import audit; no project SciPy radial/Jost/matching imports or calls",
            "project_scipy_radial_solver_in_backend_call_graph": False,
            "project_jost_in_backend_call_graph": False,
            "project_matching_in_backend_call_graph": False,
        },
        "call_graph_isolation": isolation,
        "diagnostic_thresholds": {
            "scope": "provisional selected-anchor diagnostics only; not calibrated V1 acceptance criteria",
            "precision_S_max": 1.0e-20,
            "step_S_max": 2.0e-6,
            "r_in_S_max": 5.0e-5,
            "r_out_S_max": 1.0e-8,
            "jost_S_max": 1.0e-10,
            "finite_state_precision_relative_max": 1.0e-18,
            "finite_state_step_relative_max": 2.0e-6,
            "signed_flux_relative_balance_max": 1.0e-5,
            "adaptive_tolerance_ladder_present": False,
        },
        "consumed_diagnostic_roots": [
            {
                "path": str(V1_DIAGNOSTIC_ROOT.resolve(strict=True)),
                "role": "consumed diagnostic; non-authoritative and never overwritten",
                "authoritative": False,
                "evidence_sha256": "ce797ffff60938b9674aadf996241a51a5f18c070ddec004806ab91e09a68887",
                "manifest_sha256": "a2a57946ef7842b00506de696ab92c710a079465032f322769850595c7f092b1",
                "checkpoint_sha256": "e7961e278a803543d447d7788410f04f71ef49a2f5ddfbb97a95eeeca3c35c13",
            },
            {
                "path": str(V2_DIAGNOSTIC_ROOT.resolve(strict=True)),
                "role": "consumed diagnostic with cancellation-dominated outer finite states; non-authoritative",
                "authoritative": False,
                "evidence_sha256": "5b7f1366c79e71da189c7edc815e77acb695560df62b642f4ee541c97c4aa6fb",
                "manifest_sha256": "3d191185ba74a1ef4a769162a42b813eae50dc3969620b738a4892a3d071f6f0",
                "checkpoint_sha256": "0cf03dbff5b78d5e9b52cebf166798f49f18abdb3857af53fbb3dbb00a5f55bc",
            },
            {
                "path": str(V3_DIAGNOSTIC_ROOT.resolve(strict=True)),
                "role": "consumed diagnostic preceding T7 fail-closed schema/Jost/domain fixes",
                "authoritative": False,
                "evidence_sha256": "2264414fb090018c9ca450b91a021bc34ac2cc4893ffdd45a06a32c37a304d95",
                "manifest_sha256": "6b9f03c972228d2993cbd577a85899c7423f137834bf913cc302c5bee02b988e",
                "checkpoint_sha256": "1350d28bf97442b2ac7f0b20ed7958f8baca73a95c4c10fd73a5cf4d2f38197d",
            },
        ],
        "modes": modes,
        "source_identities": source_identities,
        "limitations": [
            "eight selected anchors only; 16040 production and 17810 policy-union keys remain unassessed",
            "BHPT direct integration remains OPEN",
            "full r_in/r_out/Jost/step/precision production ladders remain OPEN",
            "Q018/turning acceptance requires resolved transmission and stable ladders",
            "Q018 S/finite-state stability is separate; unresolved T_H forbids flux closure",
            "fixed r_out<=2400 is not asymptotic at kM=0.01, ell=84 (turning scale about 8400M); full V1 requires fail-closed adaptive r_out extension",
            "AP fixed-step convergence is not the production adaptive-tolerance ladder",
            "60M is an explicitly frozen Stage-A pilot match node, not a generic match-radius policy; full V1Q must select and ladder match radii from turning/conditioning diagnostics independently of requested finite-state radii",
            "no V1/full-domain/project/global GREEN claim",
        ],
        "runtime_cost": _runtime_cost(modes),
    }
    execution_state["stage"] = "aggregate_evidence_validation"
    validate_stage_a_evidence(evidence)
    execution_state["stage"] = "aggregate_evidence_publication"
    evidence_identity = _publish_json(
        output_root / "selected_anchor_evidence.json", evidence
    )
    elapsed = time.perf_counter() - started
    manifest = {
        "schema_version": "schwgw_phase6_mpmath_selected_anchor_manifest_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": elapsed,
        "python": platform.python_version(),
        "mpmath": mp.__version__,
        "evidence": evidence_identity,
        "checkpoint_identities": checkpoint_identities,
        "mode_terminal_identities": mode_terminal_identities,
        "source_identities": source_identities,
        "input_contract": input_contract,
        "input_sha256": input_sha256,
        "full_domain_runs": 0,
        "paper_figure_runs": 0,
        "global_green_permitted": False,
    }
    manifest_identity = _publish_json(output_root / "manifest.json", manifest)
    checkpoint = {
        "schema_version": "schwgw_phase6_mpmath_selected_anchor_checkpoint_v1",
        "status": "YELLOW_SELECTED_ANCHORS_ONLY",
        "evidence": evidence_identity,
        "manifest": manifest_identity,
        "mode_terminal_identities": mode_terminal_identities,
        "covered_key_count": 8,
        "production_missing_key_count": 16040,
        "policy_extended_union_missing_key_count": 17810,
        "mode_statuses": {
            record["mode"]["mode_id"]: record["status"] for record in modes
        },
        "global_green_permitted": False,
    }
    execution_state["stage"] = "final_checkpoint_publication"
    checkpoint_identity = _publish_json(output_root / "checkpoint.json", checkpoint)
    execution_state["stage"] = "final_artifact_reload"
    _validate_success_reload(
        output_root,
        evidence=evidence,
        evidence_identity=evidence_identity,
        manifest=manifest,
        manifest_identity=manifest_identity,
        checkpoint=checkpoint,
        checkpoint_identity=checkpoint_identity,
        mode_terminal_identities=mode_terminal_identities,
    )
    execution_state["stage"] = "complete"
    _seal_output_root(output_root)
    return {
        "root": str(output_root.resolve()),
        "evidence": evidence_identity,
        "manifest": manifest_identity,
        "checkpoint": checkpoint_identity,
        "elapsed_seconds": elapsed,
        "mode_statuses": checkpoint["mode_statuses"],
    }


def run(output_root: Path) -> dict[str, object]:
    _validate_output_destination(output_root)
    output_root.mkdir(mode=0o700)
    execution_state: dict[str, str | None] = {
        "stage": "output_allocation",
        "active_mode_id": None,
    }
    try:
        checkpoint_root = output_root / "mode_checkpoints"
        checkpoint_root.mkdir(mode=0o700)
        for mode in selected_stage_a_modes():
            (checkpoint_root / mode.mode_id).mkdir(mode=0o700)
        return _run_allocated(output_root, execution_state)
    except Exception as exc:
        stage = execution_state.get("stage") or "unknown"
        active_mode_id = execution_state.get("active_mode_id")
        try:
            failure_identity = _publish_run_failure(
                output_root,
                stage=stage,
                active_mode_id=active_mode_id,
                exc=exc,
            )
            _seal_output_root(output_root)
        except Exception as publication_exc:
            raise RuntimeError(
                "Stage-A failed and durable failure publication also failed: "
                f"{type(publication_exc).__name__}: {publication_exc}"
            ) from exc
        raise RuntimeError(
            "Stage-A failed closed at "
            f"{stage}; durable failure artifact: {failure_identity['path']}"
        ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(json.dumps(run(args.output_root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
