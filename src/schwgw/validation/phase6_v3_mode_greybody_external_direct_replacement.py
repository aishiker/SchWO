"""V3.1-X external-direct supervision, publication, and whole-gate wiring."""

from __future__ import annotations

from datetime import UTC, datetime
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys
import time
from typing import Any, Callable, Mapping, Sequence
import unicodedata

from schwgw.validation.phase6_v3_external_direct import (
    BHPT_SNAPSHOT_AUTHORITY,
    BHPT_SNAPSHOT_AUTHORITY_SHA256,
    BHPT_SNAPSHOT_ROOT,
    CERTIFICATE_IDS,
    DESIGN_PATH,
    DESIGN_SHA256,
    ExternalDirectContractError,
    GATE_ID,
    PACKAGE_PATH,
    PACKAGE_SHA256,
    ROOT,
    T4_PROMPT_PATH,
    T4_PROMPT_SHA256,
    T7_PACKAGE_PROMPT_PATH,
    T7_PACKAGE_PROMPT_SHA256,
    T7_PACKAGE_REVIEW_PATH,
    T7_PACKAGE_REVIEW_SHA256,
    T7_SCIENCE_PROMPT_PATH,
    T7_SCIENCE_PROMPT_SHA256,
    canonical_bytes,
    build_sentinel_budgets,
    compact_jsonl_record,
    derive_node_record,
    expected_graph,
    load_jsonl,
    materialize_overlay,
    resource_projection,
    sha256,
    static_contract,
    base_snapshot_identity,
    validate_node_records,
    validate_official_budgets,
    validate_overlay,
    validate_sentinel_budgets,
    LOADED_SOURCE_CONTEXTS,
    LOADED_SOURCE_PATHS,
)


ARTIFACT_REV = 1
WLS_PATH = ROOT / "scripts/phase6_v3_1_x_bhpt_direct.wls"
CORE_PATH = ROOT / "src/schwgw/validation/phase6_v3_external_direct.py"
PRODUCER_PATH = (
    ROOT / "src/schwgw/validation/"
    "phase6_v3_mode_greybody_external_direct_replacement.py"
)
CLI_PATH = ROOT / "scripts/phase6_v3_1_x_external_direct.py"
UNIT_TEST_PATH = ROOT / "tests/unit/test_phase6_v3_external_direct.py"
REGRESSION_TEST_PATH = (
    ROOT / "tests/regression/test_phase6_v3_external_direct_publication.py"
)
IMPLEMENTATION_PATHS = (
    WLS_PATH,
    CORE_PATH,
    PRODUCER_PATH,
    CLI_PATH,
    UNIT_TEST_PATH,
    REGRESSION_TEST_PATH,
)
WOLFRAM_KERNEL = Path(
    "/Volumes/JohnnyTforGR/Applications/Wolfram.app/Contents/MacOS/WolframKernel"
)
WOLFRAM_KERNEL_SHA256 = (
    "70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c"
)
PYTHON_EXECUTABLE = Path(
    "/opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/"
    "Python.framework/Versions/3.14/bin/python3.14"
)
ROOT_PARENT = ROOT / "runs/phase6/classic_scattering"
MICRO_OPERATION = "source_load_micro_sentinel"
FULL_WLS_OPERATION = "external_direct_node"
MICRO_STAGE = "source-load-micro-sentinel"
MICRO_PATTERN = re.compile(
    r"v3_1_x_source_load_micro_sentinel_v1_(?P<utc>\d{8}T\d{6}Z)_py314"
)
SENTINEL_PATTERN = re.compile(
    r"v3_1_x_external_direct_sentinel_repair2_v1_"
    r"(?P<utc>\d{8}T\d{6}Z)_py314"
)
OFFICIAL_PATTERN = re.compile(r"v3_1_x_external_direct_v1_(?P<utc>\d{8}T\d{6}Z)_py314")
REPAIR2_PACKAGE_PATH = (
    ROOT / "configs/phase6_v3_1_x_sentinel_repair_cycle2_source_ledger_package.json"
)
REPAIR2_PACKAGE_SHA256 = (
    "2f4f2304b4e9507a3627ee26d3aadd9d7632152d7367653746bedf1ec591673c"
)
REPAIR2_PACKAGE_REVIEW_PATH = (
    ROOT / "docs/handoffs/archive/"
    "T7_2026-08-13_v3_1_x_sentinel_repair_cycle2_source_ledger_"
    "package_delta_review_1.md"
)
REPAIR2_PACKAGE_REVIEW_SHA256 = (
    "4acf5aa7e09874576da100a3b9c7c6acee2ea033d7da798dde689f1611da5685"
)
IMPLEMENTATION_REVIEW_PATH = (
    ROOT / "docs/handoffs/archive/"
    "T7_2026-08-13_v3_1_x_sentinel_repair_cycle2_source_ledger_"
    "implementation_delta_review.md"
)
IMPLEMENTATION_REVIEW_REQUIRED_TOKENS = (
    "ADVANCE_DECISION: ADVANCE",
    "CLAIM_STATUS: NOT_ASSESSED",
    "GATE_LABEL: ACCEPT GREEN / V3.1-X SOURCE-LEDGER REPAIR CYCLE 2 "
    "IMPLEMENTATION READY FOR ONE-USE MICRO DISPATCH",
)
IMPLEMENTATION_REVIEW_REQUIRED_AUTHORITY_HASHES = (
    REPAIR2_PACKAGE_SHA256,
    REPAIR2_PACKAGE_REVIEW_SHA256,
    "582bc3248a6acf7164485203d317b2cdc0d2a7819a13dcdb584e86e9a90bebdf",
    "bdbe1c1d05b086cac50d3dd5b99759a5d131b86e73788f92b0788bc9775eba1b",
    "d78e6ba25a8b8f8885d75552e50fbe52f9715fd4288d1a58982021448da2d97f",
    "52096dc832fed2bc64153273e3d5d69ac446ac96ccf63bf468d12e7b25162aa1",
    "1cf801469dc13fd076a5dd87e86c728b3b5c1c681c24f5d59e507f6172ab7c75",
    "7f002b2e2abb5a80d0836ff4d458a52842af4aad337db0d1e50c8dc1ce8da232",
)
MICRO_REVIEW_PATH = (
    ROOT / "docs/handoffs/archive/"
    "T7_2026-08-13_v3_1_x_source_load_micro_sentinel_terminal_review.md"
)
MICRO_REVIEW_REQUIRED_TOKENS = (
    "ADVANCE_DECISION: ADVANCE",
    "CLAIM_STATUS: NOT_ASSESSED",
    "GATE_LABEL: ACCEPT GREEN / V3.1-X SOURCE-LOAD MICRO SENTINEL SUFFICIENT "
    "FOR ONE-USE FULL SENTINEL DISPATCH",
)
MICRO_REVIEW_FAILURE_TOKENS = (
    "ADVANCE_DECISION: ESCALATE",
    "CLAIM_STATUS: FAIL",
    "GATE_LABEL: ESCALATE / T0 ADJUDICATION REQUIRED",
)
FULL_SENTINEL_REVIEW_PATH = (
    ROOT / "docs/handoffs/archive/"
    "T7_2026-08-13_v3_1_x_external_direct_sentinel_attempt_0003_terminal_review.md"
)
DISPATCH_ARCHIVE_DIR = ROOT / "docs/handoffs/archive"
MICRO_DISPATCH_PATTERN = re.compile(
    r"T0_2026\-08\-13_v3_1_x_source_load_micro_sentinel_dispatch_"
    r"attempt_0001\.json"
)
SENTINEL_DISPATCH_PATTERN = re.compile(
    r"T0_2026\-08\-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0003\.json"
)
OFFICIAL_DISPATCH_PATTERN = re.compile(
    r"T0_\d{4}-\d{2}-\d{2}_v3_1_x_external_direct_official_dispatch_attempt_0001\.json"
)
REQUESTED_EXECUTION_ENVIRONMENT = {
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONPATH": "runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src",
}
OBSERVED_CLEAN_LAUNCH_ENVIRONMENT = {
    "LC_CTYPE": "C.UTF-8",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONPATH": "runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src",
    "__CF_USER_TEXT_ENCODING": "0x1F5:0x19:0x34",
}
# Backward-compatible name for test-only callers; production validation always
# distinguishes the execve request from the macOS-observed startup state.
EXACT_EXECUTION_ENVIRONMENT = REQUESTED_EXECUTION_ENVIRONMENT
EXPECTED_COUNTS = {
    "route_a_modes": 496,
    "route_a_nodes": 9920,
    "route_u_keys": 318,
    "route_u_nodes": 954,
    "route_b_keys": 102,
    "route_b_nodes": 458,
    "route_c_keys": 23,
    "route_c_nodes": 161,
    "route_c_boundary_solutions": 322,
    "route_c_overlaps": 483,
    "thresholds": 16,
    "certificates": 5,
}
SOURCE_FIELD_ORDER = ("context", "path", "sha256", "size", "mode", "nlink")
OVERLAY_DIRECTORY_PATHS = (".", "Kernel", "Kernel/MST", "Tests", "Tests/Correctness")
MICRO_COUNTERS = {
    "wolfram_launch_count": 1,
    "request_count": 1,
    "source_record_count_start": 8,
    "source_record_count_end": 8,
    "external_api_call_count": 0,
    "regge_wheeler_radial_call_count": 0,
    "solver_call_count": 0,
    "boundary_solution_count": 0,
    "overlap_record_count": 0,
    "scientific_call_count": 0,
}
MICRO_MAX_ROOT_BYTES = 16 * 1024 * 1024
FAILED_SENTINEL_ROOTS = (
    ROOT_PARENT / "v3_1_x_external_direct_sentinel_v1_20260813T055002Z_py314",
    ROOT_PARENT / "v3_1_x_external_direct_sentinel_v1_20260813T085010Z_py314",
)

ChildRunner = Callable[[Path, Path, Mapping[str, Any]], Mapping[str, Any]]


def validate_clean_launch_environment(observed: Mapping[str, str]) -> bool:
    """Return true only for the frozen macOS clean-launch startup map."""

    return dict(observed) == OBSERVED_CLEAN_LAUNCH_ENVIRONMENT


def _reject_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ExternalDirectContractError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def _loads_unique_json(raw: bytes, *, label: str) -> Any:
    try:
        return json.loads(raw, object_pairs_hook=_reject_duplicate_object_pairs)
    except ExternalDirectContractError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ExternalDirectContractError(f"invalid JSON: {label}") from exc


def load_canonical(path: Path) -> dict[str, Any]:
    """Load canonical JSON while rejecting duplicate members at every depth."""

    raw = path.read_bytes()
    value = _loads_unique_json(raw, label=str(path))
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise ExternalDirectContractError(f"noncanonical JSON: {path}")
    return value


def normalize_loaded_source_ledger(records: Any) -> list[list[Any]]:
    """Apply the one frozen six-field semantic projection in ordered-8 form."""

    if not isinstance(records, list) or len(records) != len(LOADED_SOURCE_CONTEXTS):
        raise ExternalDirectContractError("loaded-source ledger cardinality mismatch")
    projection: list[list[Any]] = []
    contexts: list[str] = []
    paths: list[str] = []
    for ordinal, (record, context, expected_path) in enumerate(
        zip(
            records,
            LOADED_SOURCE_CONTEXTS,
            LOADED_SOURCE_PATHS,
            strict=True,
        )
    ):
        if not isinstance(record, Mapping) or set(record) != set(SOURCE_FIELD_ORDER):
            raise ExternalDirectContractError(
                f"loaded-source record schema mismatch: {ordinal}"
            )
        values = [record[field] for field in SOURCE_FIELD_ORDER]
        if not all(isinstance(value, str) for value in values[:3]) or not all(
            type(value) is int for value in values[3:]
        ):
            raise ExternalDirectContractError(
                f"loaded-source record type mismatch: {ordinal}"
            )
        source_path = values[1]
        components = source_path.split("/")
        if (
            values[0] != context
            or source_path != expected_path
            or unicodedata.normalize("NFC", source_path) != source_path
            or source_path.startswith("/")
            or source_path.endswith("/")
            or any(component in {"", ".", ".."} for component in components)
            or "\\" in source_path
            or ":" in source_path
            or re.fullmatch(r"[A-Za-z0-9._/-]+", source_path) is None
            or re.fullmatch(r"[0-9a-f]{64}", values[2]) is None
            or values[3] < 0
            or values[4] != 0o444
            or values[5] != 1
        ):
            raise ExternalDirectContractError(
                f"loaded-source record semantic mismatch: {ordinal}"
            )
        contexts.append(values[0])
        paths.append(source_path)
        projection.append(values)
    if len(set(contexts)) != len(contexts) or len(set(paths)) != len(paths):
        raise ExternalDirectContractError("loaded-source duplicate context/path")
    return projection


def _overlay_inode_inventory(root: Path) -> dict[str, Any]:
    """Bind 25 files and five directories, including device/inode provenance."""

    if not root.is_absolute() or root.is_symlink():
        raise ExternalDirectContractError("overlay root alias")
    resolved = root.resolve(strict=True)
    if resolved != root:
        raise ExternalDirectContractError("overlay root alias")
    paths = [resolved, *resolved.rglob("*")]
    directories = [item for item in paths if item.is_dir()]
    files = [item for item in paths if item.is_file()]
    relative_directories = sorted(
        "." if item == resolved else item.relative_to(resolved).as_posix()
        for item in directories
    )
    if relative_directories != sorted(OVERLAY_DIRECTORY_PATHS) or len(files) != 25:
        raise ExternalDirectContractError("overlay inode inventory cardinality drift")
    directory_records: list[dict[str, Any]] = []
    file_records: list[dict[str, Any]] = []
    for path in sorted(directories):
        info = path.lstat()
        if path.is_symlink() or not stat.S_ISDIR(info.st_mode):
            raise ExternalDirectContractError("overlay directory alias")
        directory_records.append(
            {
                "path": "."
                if path == resolved
                else path.relative_to(resolved).as_posix(),
                "dev": info.st_dev,
                "ino": info.st_ino,
                "mode": stat.S_IMODE(info.st_mode),
                "nlink": info.st_nlink,
            }
        )
    for path in sorted(files):
        info = path.lstat()
        if (
            path.is_symlink()
            or not stat.S_ISREG(info.st_mode)
            or info.st_nlink != 1
            or path.resolve(strict=True) != path
        ):
            raise ExternalDirectContractError("overlay file alias/link drift")
        file_records.append(
            {
                "path": path.relative_to(resolved).as_posix(),
                "dev": info.st_dev,
                "ino": info.st_ino,
                "mode": stat.S_IMODE(info.st_mode),
                "nlink": info.st_nlink,
                "size": info.st_size,
                "sha256": sha256(path),
            }
        )
    if any(item["mode"] != 0o555 for item in directory_records) or any(
        item["mode"] != 0o444 for item in file_records
    ):
        raise ExternalDirectContractError("overlay inode inventory mode drift")
    return {
        "schema": "schwo.phase6.v3_1_x.overlay_inode_inventory.v1",
        "root": str(resolved),
        "directories": directory_records,
        "files": file_records,
    }


def _projection_sha256(projection: Sequence[Sequence[Any]]) -> str:
    return hashlib.sha256(
        json.dumps(projection, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def _file_identity(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise ExternalDirectContractError(f"unsafe file identity: {path}")
    path = path.resolve(strict=True)
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ExternalDirectContractError(f"unsafe file identity: {path}")
    return {
        "path": str(path),
        "sha256": sha256(path),
        "size": info.st_size,
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
        "dev": info.st_dev,
        "ino": info.st_ino,
    }


def _directory_identity(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise ExternalDirectContractError(f"unsafe directory identity: {path}")
    path = path.resolve(strict=True)
    info = path.stat()
    if not stat.S_ISDIR(info.st_mode):
        raise ExternalDirectContractError(f"unsafe directory identity: {path}")
    return {
        "path": str(path),
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
        "dev": info.st_dev,
        "ino": info.st_ino,
    }


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _exclusive_publish(path: Path, data: bytes, *, mode: int = 0o444) -> dict[str, Any]:
    """Publish bytes without following or replacing an existing target."""

    if not path.parent.is_dir() or path.parent.is_symlink():
        raise ExternalDirectContractError("publication parent is unsafe")
    partial = path.parent / f".{path.name}.{os.getpid()}.{time.time_ns()}.partial"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(partial, flags, 0o600)
    try:
        with os.fdopen(fd, "wb", closefd=False) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.fchmod(fd, mode)
        os.fsync(fd)
    finally:
        os.close(fd)
    try:
        os.link(partial, path, follow_symlinks=False)
        partial.unlink()
        _fsync_directory(path.parent)
    except BaseException:
        if partial.exists() and not partial.is_symlink():
            partial.unlink()
        raise
    identity = _file_identity(path)
    if identity["mode"] != mode or identity["nlink"] != 1:
        raise ExternalDirectContractError("durable publication identity mismatch")
    return identity


def _jsonl_bytes(records: Sequence[Mapping[str, Any]]) -> bytes:
    return b"".join(compact_jsonl_record(item) for item in records)


def implementation_hashes() -> dict[str, str]:
    result: dict[str, str] = {}
    for path in IMPLEMENTATION_PATHS:
        if not path.is_file() or path.is_symlink():
            raise ExternalDirectContractError(f"implementation path absent: {path}")
        result[str(path.relative_to(ROOT))] = sha256(path)
    if len(result) != 6:
        raise ExternalDirectContractError("implementation path cardinality drift")
    return result


def _verify_bound_file(
    path: Path, expected_sha: str, *, frozen: bool = False
) -> dict[str, Any]:
    identity = _file_identity(path)
    if identity["sha256"] != expected_sha or (frozen and identity["mode"] != 0o444):
        raise ExternalDirectContractError(f"frozen identity drift: {path}")
    return identity


def _verify_repair2_package_gate() -> dict[str, Any]:
    package_identity = _verify_bound_file(
        REPAIR2_PACKAGE_PATH, REPAIR2_PACKAGE_SHA256, frozen=True
    )
    package = load_canonical(REPAIR2_PACKAGE_PATH)
    if (
        package.get("schema")
        != "schwo.phase6.v3_1_x.source_ledger_repair_cycle2_package.v1"
        or package.get("repair_id") != "phase6_v3_1_x_source_ledger_repair_cycle2_v1"
        or package.get("implementation_scope", {}).get("allowed_unique_paths")
        != [
            "scripts/phase6_v3_1_x_bhpt_direct.wls",
            "src/schwgw/validation/phase6_v3_mode_greybody_"
            "external_direct_replacement.py",
            "scripts/phase6_v3_1_x_external_direct.py",
            "tests/unit/test_phase6_v3_external_direct.py",
            "tests/regression/test_phase6_v3_external_direct_publication.py",
        ]
        or package["implementation_scope"]["direct_physics_core_must_remain_sha256"]
        != "981c2b220c3e67e400f0d8c420fdf4f89ac57962483fa0a02bf9ed3649948da4"
    ):
        raise ExternalDirectContractError("repair-2 package contract mismatch")
    if package.get("authority_chain") != {
        "future_full_sentinel_dispatch": (
            "docs/handoffs/archive/T0_2026-08-13_v3_1_x_external_direct_"
            "sentinel_dispatch_attempt_0003.json"
        ),
        "future_full_sentinel_review": (
            "docs/handoffs/archive/T7_2026-08-13_v3_1_x_external_direct_"
            "sentinel_attempt_0003_terminal_review.md"
        ),
        "future_implementation_review": str(
            IMPLEMENTATION_REVIEW_PATH.relative_to(ROOT)
        ),
        "future_micro_dispatch": (
            "docs/handoffs/archive/T0_2026-08-13_v3_1_x_source_load_micro_"
            "sentinel_dispatch_attempt_0001.json"
        ),
        "future_micro_review": str(MICRO_REVIEW_PATH.relative_to(ROOT)),
        "future_package_review": (
            "docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_"
            "cycle2_source_ledger_package_review.md"
        ),
        "future_review_sha256_hardcoded_in_production": False,
        "later_root_t0_dispatch_supplies_exact_future_review_sha256": True,
        "micro_failure_tokens": list(MICRO_REVIEW_FAILURE_TOKENS),
        "micro_success_tokens": list(MICRO_REVIEW_REQUIRED_TOKENS),
        "multiple_or_runtime_selected_authorities_permitted": False,
    }:
        raise ExternalDirectContractError("repair-2 authority graph mismatch")
    identities: dict[str, dict[str, Any]] = {}
    for item in package["members"]:
        path = ROOT / item["path"]
        identities[str(path)] = _verify_bound_file(path, item["sha256"], frozen=True)
    for relative, digest in package["source_bindings"].items():
        path = ROOT / relative
        identities[str(path)] = _verify_bound_file(path, digest, frozen=True)
    for relative, digest in package["protected_radial_identities"].items():
        path = ROOT / relative
        identities[str(path)] = _verify_bound_file(path, digest)
    review_identity = _verify_bound_file(
        REPAIR2_PACKAGE_REVIEW_PATH,
        REPAIR2_PACKAGE_REVIEW_SHA256,
        frozen=True,
    )
    review_text = REPAIR2_PACKAGE_REVIEW_PATH.read_text()
    for token in (
        "ADVANCE_DECISION: ADVANCE",
        "CLAIM_STATUS: NOT_ASSESSED",
        "GATE_LABEL: ACCEPT GREEN / V3.1-X SOURCE-LEDGER REPAIR CYCLE 2 "
        "PACKAGE READY FOR T6",
        REPAIR2_PACKAGE_SHA256,
    ):
        if token not in review_text:
            raise ExternalDirectContractError("repair-2 package approval mismatch")
    identities[str(REPAIR2_PACKAGE_REVIEW_PATH)] = review_identity
    return {
        "package": package,
        "package_identity": package_identity,
        "identities": identities,
    }


def verify_start_gate() -> dict[str, Any]:
    repair2 = _verify_repair2_package_gate()
    package_identity = _verify_bound_file(PACKAGE_PATH, PACKAGE_SHA256, frozen=True)
    package = load_canonical(PACKAGE_PATH)
    if package.get("schema") != "schwo.phase6.v3_1_x.external_direct_route_package.v1":
        raise ExternalDirectContractError("package schema mismatch")
    frozen_fixed: dict[Path, str] = {
        DESIGN_PATH: DESIGN_SHA256,
        T4_PROMPT_PATH: T4_PROMPT_SHA256,
        T7_PACKAGE_PROMPT_PATH: T7_PACKAGE_PROMPT_SHA256,
        T7_SCIENCE_PROMPT_PATH: T7_SCIENCE_PROMPT_SHA256,
        T7_PACKAGE_REVIEW_PATH: T7_PACKAGE_REVIEW_SHA256,
        BHPT_SNAPSHOT_AUTHORITY: BHPT_SNAPSHOT_AUTHORITY_SHA256,
    }
    for item in package["members"]:
        frozen_fixed[ROOT / item["path"]] = item["sha256"]
    for item in package["review_basis"].values():
        frozen_fixed[ROOT / item["path"]] = item["sha256"]
    identities = {
        str(path): _verify_bound_file(path, digest, frozen=True)
        for path, digest in frozen_fixed.items()
    }
    identities.update(
        {
            str(ROOT / path): _verify_bound_file(ROOT / path, digest)
            for path, digest in package["protected_radial_identities"].items()
        }
    )
    review = T7_PACKAGE_REVIEW_PATH.read_text()
    for token in (
        "ADVANCE_DECISION: ADVANCE",
        "CLAIM_STATUS: NOT_ASSESSED",
        "ACCEPT GREEN / V3.1-X EXTERNAL DIRECT-ROUTE PACKAGE READY FOR T4",
        PACKAGE_SHA256,
    ):
        if token not in review:
            raise ExternalDirectContractError("formal package approval mismatch")
    snapshot = base_snapshot_identity()
    if (
        snapshot["content_inventory_sha256"]
        != package["base_external_runtime"]["bhpt_snapshot"]["content_inventory_sha256"]
        or snapshot["identity_inventory_sha256"]
        != package["base_external_runtime"]["bhpt_snapshot"][
            "restored_identity_inventory_sha256"
        ]
        or _file_identity(BHPT_SNAPSHOT_ROOT / "Kernel/NumericalIntegration.m")[
            "sha256"
        ]
        != package["base_external_runtime"]["bhpt_snapshot"][
            "numerical_integration_sha256"
        ]
    ):
        raise ExternalDirectContractError("base NumericalIntegration drift")
    identities[str(BHPT_SNAPSHOT_ROOT)] = snapshot
    identities[str(WOLFRAM_KERNEL)] = _verify_bound_file(
        WOLFRAM_KERNEL, WOLFRAM_KERNEL_SHA256
    )
    identities.update(repair2["identities"])
    identities[str(REPAIR2_PACKAGE_PATH)] = repair2["package_identity"]
    static = static_contract()
    expected_overlay = {
        item["name"]: item["sha256"] for item in package["overlay_variants"]
    }
    if static["overlay_hashes"] != expected_overlay:
        raise ExternalDirectContractError("overlay package mismatch")
    if package["route_admission_criteria"] != {
        key: float(value)
        for key, value in __import__(
            "schwgw.validation.phase6_v3_external_direct", fromlist=["ROUTE_ADMISSION"]
        ).ROUTE_ADMISSION.items()
    }:
        raise ExternalDirectContractError("route admission criteria drift")
    return {
        "schema": "schwo.phase6.v3_1_x.start_gate.v1",
        "package": package,
        "package_identity": package_identity,
        "repair2_package": repair2["package"],
        "repair2_package_identity": repair2["package_identity"],
        "identities": identities,
        "implementation_hashes": implementation_hashes(),
        "static_contract": static,
        "scientific_evidence": False,
    }


def build_source_ledger(start_gate: Mapping[str, Any]) -> dict[str, Any]:
    fresh = verify_start_gate()
    if fresh["package_identity"] != start_gate["package_identity"]:
        raise ExternalDirectContractError("package changed after start")
    if fresh["repair2_package_identity"] != start_gate["repair2_package_identity"]:
        raise ExternalDirectContractError("repair-2 package changed after start")
    if fresh["identities"] != start_gate["identities"]:
        raise ExternalDirectContractError(
            "source/protected authority changed after start"
        )
    if fresh["implementation_hashes"] != start_gate["implementation_hashes"]:
        raise ExternalDirectContractError("implementation changed after start")
    return {
        "schema": "schwo.phase6.v3_1_x.source_ledger.v1",
        "gate_id": GATE_ID,
        "package": fresh["package_identity"],
        "repair2_package": fresh["repair2_package_identity"],
        "authorities": fresh["identities"],
        "implementation_hashes": fresh["implementation_hashes"],
        "protected_radial_identities": fresh["package"]["protected_radial_identities"],
        "bhpt_snapshot": fresh["package"]["base_external_runtime"]["bhpt_snapshot"],
        "predecessor_science_reused": False,
        "sentinel_science_reused": False,
    }


def _validate_utc_namespace(root: Path, stage: str) -> Path:
    if root.exists() or root.is_symlink():
        raise ExternalDirectContractError("execution root must be absent")
    if (
        not root.is_absolute()
        or unicodedata.normalize("NFC", str(root)) != str(root)
        or root.parent.is_symlink()
        or root.parent != root.parent.resolve(strict=True)
    ):
        raise ExternalDirectContractError("execution root alias")
    parent = root.parent.resolve(strict=True)
    if parent != ROOT_PARENT.resolve(strict=True):
        raise ExternalDirectContractError("execution root parent mismatch")
    patterns = {
        MICRO_STAGE: MICRO_PATTERN,
        "sentinel": SENTINEL_PATTERN,
        "official": OFFICIAL_PATTERN,
    }
    try:
        pattern = patterns[stage]
    except KeyError as exc:
        raise ExternalDirectContractError("execution stage mismatch") from exc
    match = pattern.fullmatch(root.name)
    if match is None:
        raise ExternalDirectContractError("execution root namespace mismatch")
    try:
        datetime.strptime(match.group("utc"), "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
    except ValueError as exc:
        raise ExternalDirectContractError(
            "execution root UTC timestamp invalid"
        ) from exc
    resolved_candidate = root.resolve(strict=False)
    if resolved_candidate != root:
        raise ExternalDirectContractError("execution root alias")
    return root


def _expected_invocation(
    stage: str, dispatch_path: Path, dispatch_sha: str
) -> dict[str, Any]:
    return {
        "executable": str(PYTHON_EXECUTABLE),
        "script": str(CLI_PATH),
        "launcher": str(CLI_PATH),
        "command": stage,
        # This field belongs to the non-circular dispatch payload.  The file is
        # necessarily absent while that payload is being assembled; the outer
        # CLI argument supplies and authenticates its eventual digest.
        "dispatch_path": str(dispatch_path.resolve(strict=False)),
        "dispatch_sha256_source": "outer_cli_argument",
        "cwd": str(ROOT),
    }


def _validate_runtime_invocation(
    stage: str, dispatch_path: Path, dispatch_sha: str
) -> None:
    expected_argv = [
        str(CLI_PATH),
        stage,
        "--dispatch",
        str(dispatch_path.resolve(strict=True)),
        "--dispatch-sha256",
        dispatch_sha,
    ]
    if (
        Path(sys.executable).resolve(strict=True)
        != PYTHON_EXECUTABLE.resolve(strict=True)
        or Path.cwd().resolve(strict=True) != ROOT
        or sys.argv != expected_argv
    ):
        raise ExternalDirectContractError("live executable/argv/cwd mismatch")


def _validate_fixed_review(
    binding: Any,
    *,
    expected_path: Path,
    required_tokens: Sequence[str],
    forbidden_tokens: Sequence[str] = (),
) -> tuple[dict[str, Any], str]:
    if not isinstance(binding, Mapping) or set(binding) != {"path", "sha256"}:
        raise ExternalDirectContractError("review binding mismatch")
    unresolved = Path(binding["path"])
    if (
        not unresolved.is_absolute()
        or unresolved.is_symlink()
        or unresolved != expected_path
        or unresolved != unresolved.resolve(strict=True)
    ):
        raise ExternalDirectContractError("review path mismatch")
    identity = _verify_bound_file(unresolved, binding["sha256"], frozen=True)
    text = unresolved.read_text()
    if any(token not in text for token in required_tokens) or any(
        token in text for token in forbidden_tokens
    ):
        raise ExternalDirectContractError("review verdict mismatch")
    return identity, text


def _validate_existing_micro_root_path(root: Path) -> Path:
    if (
        not root.is_absolute()
        or root.is_symlink()
        or root.parent.is_symlink()
        or root != root.resolve(strict=True)
        or root.parent != ROOT_PARENT.resolve(strict=True)
        or MICRO_PATTERN.fullmatch(root.name) is None
        or stat.S_IMODE(root.stat().st_mode) != 0o555
    ):
        raise ExternalDirectContractError("micro root authority mismatch")
    match = MICRO_PATTERN.fullmatch(root.name)
    assert match is not None
    try:
        datetime.strptime(match.group("utc"), "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
    except ValueError as exc:
        raise ExternalDirectContractError("micro root UTC invalid") from exc
    return root


def validate_dispatch(
    dispatch_path: Path,
    dispatch_sha: str,
    *,
    stage: str,
    start_gate: Mapping[str, Any],
) -> dict[str, Any]:
    if stage not in {MICRO_STAGE, "sentinel", "official"}:
        raise ExternalDirectContractError("dispatch stage mismatch")
    if stage != "official":
        unresolved_dispatch_path = dispatch_path
        if (
            not unresolved_dispatch_path.is_absolute()
            or unresolved_dispatch_path.is_symlink()
            or unresolved_dispatch_path != unresolved_dispatch_path.resolve(strict=True)
        ):
            raise ExternalDirectContractError("dispatch authority namespace mismatch")
    dispatch_path = dispatch_path.resolve(strict=True)
    pattern = {
        MICRO_STAGE: MICRO_DISPATCH_PATTERN,
        "sentinel": SENTINEL_DISPATCH_PATTERN,
        "official": OFFICIAL_DISPATCH_PATTERN,
    }[stage]
    if (
        dispatch_path.parent != DISPATCH_ARCHIVE_DIR.resolve(strict=True)
        or pattern.fullmatch(dispatch_path.name) is None
    ):
        raise ExternalDirectContractError("dispatch authority namespace mismatch")
    identity = _verify_bound_file(dispatch_path, dispatch_sha, frozen=True)
    payload = load_canonical(dispatch_path)
    required = {
        "schema",
        "gate_id",
        "stage",
        "exact_root",
        "package_sha256",
        "implementation_hashes",
        "implementation_review",
        "invocation",
        "requested_environment",
        "observed_environment",
        "one_use_id",
        "predecessor_science_reused",
        "sentinel_science_reused",
    }
    if stage == MICRO_STAGE:
        required.add("operation")
    elif stage == "sentinel":
        required.update({"operation", "micro_review", "micro_root"})
    else:
        required.add("sentinel_review")
    if set(payload) != required:
        raise ExternalDirectContractError("dispatch schema mismatch")
    if (
        payload["schema"] != "schwo.phase6.v3_1_x.external_direct_dispatch.v1"
        or payload["gate_id"] != GATE_ID
        or payload["stage"] != stage
        or payload["package_sha256"]
        != (PACKAGE_SHA256 if stage == "official" else REPAIR2_PACKAGE_SHA256)
        or payload["implementation_hashes"] != start_gate["implementation_hashes"]
        or payload["predecessor_science_reused"] is not False
        or payload["sentinel_science_reused"] is not False
        or not isinstance(payload["one_use_id"], str)
        or len(payload["one_use_id"]) < 32
    ):
        raise ExternalDirectContractError("dispatch authority mismatch")
    if stage == MICRO_STAGE and payload["operation"] != MICRO_OPERATION:
        raise ExternalDirectContractError("micro dispatch operation mismatch")
    if stage == "sentinel" and payload["operation"] != FULL_WLS_OPERATION:
        raise ExternalDirectContractError("sentinel dispatch operation mismatch")
    root = _validate_utc_namespace(Path(payload["exact_root"]), stage)
    expected_invocation = _expected_invocation(stage, dispatch_path, dispatch_sha)
    if payload["invocation"] != expected_invocation:
        raise ExternalDirectContractError("dispatch invocation mismatch")
    _validate_runtime_invocation(stage, dispatch_path, dispatch_sha)
    if (
        payload["requested_environment"] != REQUESTED_EXECUTION_ENVIRONMENT
        or payload["observed_environment"] != OBSERVED_CLEAN_LAUNCH_ENVIRONMENT
        or not validate_clean_launch_environment(dict(os.environ))
    ):
        raise ExternalDirectContractError("execution environment authority mismatch")
    review_identity, text = _validate_fixed_review(
        payload["implementation_review"],
        expected_path=IMPLEMENTATION_REVIEW_PATH,
        required_tokens=IMPLEMENTATION_REVIEW_REQUIRED_TOKENS,
    )
    if not all(
        digest in text for digest in IMPLEMENTATION_REVIEW_REQUIRED_AUTHORITY_HASHES
    ):
        raise ExternalDirectContractError("implementation review authority mismatch")
    if not all(
        digest in text for digest in start_gate["implementation_hashes"].values()
    ):
        raise ExternalDirectContractError("implementation review hash binding mismatch")
    micro_authority: dict[str, Any] | None = None
    if stage == "sentinel":
        micro_review_identity, micro_text = _validate_fixed_review(
            payload["micro_review"],
            expected_path=MICRO_REVIEW_PATH,
            required_tokens=MICRO_REVIEW_REQUIRED_TOKENS,
            forbidden_tokens=(
                *MICRO_REVIEW_FAILURE_TOKENS,
                "35-call sentinel",
                "35/70/105",
            ),
        )
        micro_binding = payload["micro_root"]
        if not isinstance(micro_binding, Mapping) or set(micro_binding) != {
            "path",
            "manifest_sha256",
        }:
            raise ExternalDirectContractError("micro root binding mismatch")
        micro_root = _validate_existing_micro_root_path(Path(micro_binding["path"]))
        micro_manifest = _verify_bound_file(
            micro_root / "manifest.json",
            micro_binding["manifest_sha256"],
            frozen=True,
        )
        validate_source_load_micro(
            micro_root, require_real_child=True, validate_live_sources=False
        )
        micro_source = load_canonical(micro_root / "source_start.json")
        if (
            micro_source.get("implementation_hashes")
            != start_gate["implementation_hashes"]
            or micro_source.get("repair2_package")
            != start_gate["repair2_package_identity"]
            or micro_source.get("package") != start_gate["package_identity"]
            or micro_source.get("authorities") != start_gate["identities"]
            or micro_source.get("protected_radial_identities")
            != start_gate["package"]["protected_radial_identities"]
            or micro_source.get("bhpt_snapshot")
            != start_gate["package"]["base_external_runtime"]["bhpt_snapshot"]
        ):
            raise ExternalDirectContractError("source drift after micro approval")
        for token in (
            str(micro_root),
            micro_manifest["sha256"],
            REPAIR2_PACKAGE_SHA256,
            *start_gate["implementation_hashes"].values(),
        ):
            if token not in micro_text:
                raise ExternalDirectContractError("micro review authority mismatch")
        micro_authority = {
            "review": micro_review_identity,
            "root": _directory_identity(micro_root),
            "manifest": micro_manifest,
        }
    elif stage == "official":
        sentinel_review = payload["sentinel_review"]
        if set(sentinel_review) != {"path", "sha256"}:
            raise ExternalDirectContractError("sentinel review binding mismatch")
        sentinel_path = Path(sentinel_review["path"])
        _verify_bound_file(sentinel_path, sentinel_review["sha256"], frozen=True)
        sentinel_text = sentinel_path.read_text()
        for token in (
            "ADVANCE_DECISION: ADVANCE",
            "CLAIM_STATUS: PASS",
            "ACCEPT GREEN / V3.1-X SENTINEL SUFFICIENT FOR ONE-USE OFFICIAL DISPATCH",
        ):
            if token not in sentinel_text:
                raise ExternalDirectContractError("sentinel review verdict mismatch")
    for existing in ROOT_PARENT.glob("v3_1_x*_py314/dispatch_consumption.json"):
        try:
            if load_canonical(existing).get("one_use_id") == payload["one_use_id"]:
                raise ExternalDirectContractError("dispatch replay")
        except FileNotFoundError:
            continue
    return {
        "payload": payload,
        "identity": identity,
        "root": root,
        "implementation_review": review_identity,
        "micro_authority": micro_authority,
    }


def _loaded_source_records(overlay_identity: Mapping[str, Any]) -> list[dict[str, Any]]:
    lookup = {item["path"]: item for item in overlay_identity["identity_records"]}
    try:
        records = [
            {"context": context, **lookup[path]}
            for context, path in zip(
                LOADED_SOURCE_CONTEXTS, LOADED_SOURCE_PATHS, strict=True
            )
        ]
    except KeyError as exc:
        raise ExternalDirectContractError("loaded source inventory missing") from exc
    normalize_loaded_source_ledger(records)
    return records


def build_wls_request(
    expected: Mapping[str, Any],
    overlay_identity: Mapping[str, Any],
    *,
    operation: str = FULL_WLS_OPERATION,
) -> dict[str, Any]:
    if operation not in {FULL_WLS_OPERATION, MICRO_OPERATION}:
        raise ExternalDirectContractError("WLS operation mismatch")
    return {
        "schema": "schwo.phase6.v3_1_x.external_direct_wls_request.v1",
        "operation": operation,
        "gate_id": GATE_ID,
        "expected": dict(expected),
        "overlay": {
            "root": overlay_identity["root"],
            "variant": overlay_identity["variant"],
            "numerical_source_sha256": overlay_identity["numerical_source_sha256"],
            "content_sha256": overlay_identity["content_sha256"],
            "identity_sha256": overlay_identity["identity_sha256"],
        },
        "loaded_source_records": _loaded_source_records(overlay_identity),
        "method_contract": {
            "spin": 2,
            "method": "NumericalIntegration",
            "boundary_conditions": ["In", "Up"],
            "potential": "ReggeWheeler",
            "mst_call_count": 0,
            "internal_solver_call_count": 0,
        },
    }


def _process_group_empty(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    return False


def _open_exclusive_stream(path: Path) -> Any:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return os.fdopen(os.open(path, flags, 0o600), "wb")


def _close_stream(handle: Any, path: Path) -> dict[str, Any]:
    handle.flush()
    os.fsync(handle.fileno())
    handle.close()
    os.chmod(path, 0o444)
    _fsync_directory(path.parent)
    return _file_identity(path)


def _utc_timestamp() -> str:
    """Return an absolute, unambiguous controller timestamp."""

    return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _stream_closure(handle: Any | None, path: Path) -> dict[str, Any]:
    """Close an opened raw stream without allowing a later terminal gap."""

    if handle is None:
        return {"state": "NOT_OPENED", "identity": None, "error": None}
    try:
        return {
            "state": "CLOSED",
            "identity": _close_stream(handle, path),
            "error": None,
        }
    except BaseException as exc:  # terminal record must still describe this failure
        try:
            handle.close()
        except BaseException:
            pass
        return {
            "state": "CLOSE_FAILED",
            "identity": _file_identity(path)
            if path.exists() and not path.is_symlink()
            else None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def _terminate_and_reap(
    process: subprocess.Popen[bytes] | None, pgid: int | None
) -> dict[str, Any]:
    """Close every post-Popen error window before terminal publication."""

    actions: list[str] = []
    returncode: int | None = None
    wait_error: str | None = None
    if process is None:
        return {
            "returncode": None,
            "actions": actions,
            "wait_error": None,
            "child_reaped": False,
            "process_group_empty": pgid is None,
        }
    try:
        if process.poll() is None and pgid is not None:
            os.killpg(pgid, signal.SIGTERM)
            actions.append("SIGTERM")
        try:
            returncode = process.wait(timeout=10)
            actions.append("wait")
        except subprocess.TimeoutExpired:
            if pgid is not None:
                os.killpg(pgid, signal.SIGKILL)
                actions.append("SIGKILL")
            returncode = process.wait(timeout=10)
            actions.append("wait_after_SIGKILL")
    except BaseException as exc:
        wait_error = f"{type(exc).__name__}: {exc}"
        try:
            returncode = process.poll()
        except BaseException:
            returncode = None
    return {
        "returncode": returncode,
        "actions": actions,
        "wait_error": wait_error,
        "child_reaped": process.poll() is not None,
        "process_group_empty": pgid is not None and _process_group_empty(pgid),
    }


def _lifecycle_record(
    *,
    schema: str,
    expected: Mapping[str, Any],
    command: Sequence[str],
    started_utc: str,
    started_ns: int,
    finished_utc: str,
    pid: int | None,
    sid: int | None,
    pgid: int | None,
    returncode: int | None,
    timed_out: bool,
    closure: Mapping[str, Any],
    stdout: Mapping[str, Any],
    stderr: Mapping[str, Any],
    observed_environment: Mapping[str, str] | None,
    exception: BaseException | None,
    child_execution_kind: str,
) -> dict[str, Any]:
    return {
        "schema": schema,
        "call_ordinal": expected["call_ordinal"],
        "argv": list(command),
        "cwd": str(ROOT),
        "requested_environment": dict(REQUESTED_EXECUTION_ENVIRONMENT),
        "observed_environment": dict(observed_environment)
        if observed_environment is not None
        else None,
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "started_ns": started_ns,
        "finished_ns": time.time_ns(),
        "pid": pid,
        "sid": sid,
        "pgid": pgid,
        "returncode": returncode,
        "signal": -returncode
        if isinstance(returncode, int) and returncode < 0
        else None,
        "timed_out": timed_out,
        "popen_wait_called": bool(closure["actions"]),
        "child_reaped": closure["child_reaped"],
        "process_group_empty": closure["process_group_empty"],
        "cleanup_actions": list(closure["actions"]),
        "wait_error": closure["wait_error"],
        "stdout": dict(stdout),
        "stderr": dict(stderr),
        "exception_type": type(exception).__name__ if exception is not None else None,
        "exception_message": str(exception) if exception is not None else None,
        "child_execution_kind": child_execution_kind,
    }


def run_wolfram_child(
    request_path: Path,
    output_path: Path,
    expected: Mapping[str, Any],
    *,
    timeout_seconds: float = 7200,
    lifecycle_prefix: Path | None = None,
) -> Mapping[str, Any]:
    """Run one child with controller-owned immutable lifecycle publication."""

    load_canonical(request_path)
    kernel_identity = _verify_bound_file(WOLFRAM_KERNEL, WOLFRAM_KERNEL_SHA256)
    wls_identity = _file_identity(WLS_PATH)
    if output_path.exists() or output_path.is_symlink():
        raise ExternalDirectContractError("raw output collision")
    if lifecycle_prefix is None:
        staging_path = output_path.with_suffix(".child.raw.json")
        prelaunch_path = output_path.with_suffix(".prelaunch.json")
        running_path = output_path.with_suffix(".running.json")
        receipt_path = output_path.with_suffix(".receipt.json")
        terminal_path = output_path.with_suffix(".terminal.json")
        stdout_path = output_path.with_suffix(".stdout.raw")
        stderr_path = output_path.with_suffix(".stderr.raw")
    else:
        if lifecycle_prefix.parent != output_path.parent:
            raise ExternalDirectContractError("lifecycle prefix parent mismatch")
        staging_path = lifecycle_prefix.with_suffix(".staging.json")
        prelaunch_path = lifecycle_prefix.with_suffix(".prelaunch.json")
        running_path = lifecycle_prefix.with_suffix(".running.json")
        receipt_path = lifecycle_prefix.with_suffix(".receipt.json")
        terminal_path = lifecycle_prefix.with_suffix(".terminal.json")
        stdout_path = lifecycle_prefix.with_suffix(".stdout.raw")
        stderr_path = lifecycle_prefix.with_suffix(".stderr.raw")
    command = [
        str(WOLFRAM_KERNEL),
        "-script",
        str(WLS_PATH),
        str(request_path),
        str(staging_path),
    ]
    started_utc = _utc_timestamp()
    started = time.time_ns()
    _exclusive_publish(
        prelaunch_path,
        canonical_bytes(
            {
                "schema": "schwo.phase6.v3_1_x.child_prelaunch.v1",
                "call_ordinal": expected["call_ordinal"],
                "argv": command,
                "cwd": str(ROOT),
                "requested_environment": dict(REQUESTED_EXECUTION_ENVIRONMENT),
                "started_utc": started_utc,
                "started_ns": started,
                "request": _file_identity(request_path),
                "kernel": kernel_identity,
                "wls": wls_identity,
                "raw_final_path": str(output_path),
                "raw_staging_path": str(staging_path),
                "child_execution_kind": "REAL_WOLFRAM_KERNEL",
            }
        ),
    )
    stdout: Any | None = None
    stderr: Any | None = None
    process: subprocess.Popen[bytes] | None = None
    pid: int | None = None
    pgid: int | None = None
    sid: int | None = None
    returncode: int | None = None
    timed_out = False
    child_exception: BaseException | None = None
    observed_environment: Mapping[str, str] | None = None
    raw: dict[str, Any] | None = None
    try:
        stdout = _open_exclusive_stream(stdout_path)
        stderr = _open_exclusive_stream(stderr_path)
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env=dict(OBSERVED_CLEAN_LAUNCH_ENVIRONMENT),
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
        pid = process.pid
        pgid = os.getpgid(pid)
        sid = os.getsid(pid)
        _exclusive_publish(
            running_path,
            canonical_bytes(
                {
                    "schema": "schwo.phase6.v3_1_x.child_running.v1",
                    "call_ordinal": expected["call_ordinal"],
                    "pid": pid,
                    "sid": sid,
                    "pgid": pgid,
                    "prelaunch": _file_identity(prelaunch_path),
                    "requested_environment": dict(REQUESTED_EXECUTION_ENVIRONMENT),
                    "started_utc": started_utc,
                    "started_ns": started,
                }
            ),
        )
        try:
            returncode = process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            closure = _terminate_and_reap(process, pgid)
            returncode = closure["returncode"]
        if process.poll() is not None and returncode is None:
            returncode = process.returncode
        if returncode == 0 and not timed_out and staging_path.is_file():
            candidate = _loads_unique_json(
                staging_path.read_bytes(), label=str(staging_path)
            )
            if not isinstance(candidate, dict):
                raise ExternalDirectContractError(
                    "Wolfram raw JSON schema type mismatch"
                )
            runtime = candidate.get("runtime")
            if not isinstance(runtime, Mapping):
                raise ExternalDirectContractError("Wolfram runtime environment missing")
            observed = runtime.get("observed_environment")
            if not validate_clean_launch_environment(
                observed if isinstance(observed, Mapping) else {}
            ):
                raise ExternalDirectContractError(
                    "Wolfram observed environment mismatch"
                )
            observed_environment = dict(observed)
            raw = candidate
    except BaseException as exc:
        child_exception = exc
    finally:
        closure = _terminate_and_reap(process, pgid)
        if closure["returncode"] is not None:
            returncode = closure["returncode"]
        stdout_state = _stream_closure(stdout, stdout_path)
        stderr_state = _stream_closure(stderr, stderr_path)
    finished_utc = _utc_timestamp()
    receipt = _lifecycle_record(
        schema="schwo.phase6.v3_1_x.child_receipt.v2",
        expected=expected,
        command=command,
        started_utc=started_utc,
        started_ns=started,
        finished_utc=finished_utc,
        pid=pid,
        sid=sid,
        pgid=pgid,
        returncode=returncode,
        timed_out=timed_out,
        closure=closure,
        stdout=stdout_state,
        stderr=stderr_state,
        observed_environment=observed_environment,
        exception=child_exception,
        child_execution_kind="REAL_WOLFRAM_KERNEL",
    )
    receipt["prelaunch"] = _file_identity(prelaunch_path)
    receipt["running"] = (
        _file_identity(running_path)
        if running_path.exists() and not running_path.is_symlink()
        else None
    )
    receipt_identity = _exclusive_publish(receipt_path, canonical_bytes(receipt))
    terminal = {
        **_lifecycle_record(
            schema="schwo.phase6.v3_1_x.child_terminal.v2",
            expected=expected,
            command=command,
            started_utc=started_utc,
            started_ns=started,
            finished_utc=finished_utc,
            pid=pid,
            sid=sid,
            pgid=pgid,
            returncode=returncode,
            timed_out=timed_out,
            closure=closure,
            stdout=stdout_state,
            stderr=stderr_state,
            observed_environment=observed_environment,
            exception=child_exception,
            child_execution_kind="REAL_WOLFRAM_KERNEL",
        ),
        "receipt": receipt_identity,
        "prelaunch": receipt["prelaunch"],
        "running": receipt["running"],
    }
    _exclusive_publish(terminal_path, canonical_bytes(terminal))
    if child_exception is not None:
        raise ExternalDirectContractError(
            "Wolfram child lifecycle exception"
        ) from child_exception
    if (
        returncode != 0
        or timed_out
        or not closure["child_reaped"]
        or not closure["process_group_empty"]
        or stdout_state["state"] != "CLOSED"
        or stderr_state["state"] != "CLOSED"
        or not isinstance(stderr_state["identity"], Mapping)
        or stderr_state["identity"]["size"] != 0
        or raw is None
    ):
        raise ExternalDirectContractError("Wolfram child terminal failure")
    _exclusive_publish(output_path, canonical_bytes(raw))
    staging_path.unlink()
    _fsync_directory(staging_path.parent)
    return raw


def execute_external_plan(
    evidence_root: Path,
    *,
    stage: str,
    child_runner: ChildRunner = run_wolfram_child,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Execute a frozen graph; tests inject a zero-science fake child."""

    plan = expected_graph(stage)
    evidence_root.mkdir(mode=0o700, parents=False, exist_ok=False)
    overlays = evidence_root / "overlays"
    records_root = evidence_root / "node_evidence"
    overlays.mkdir(mode=0o700)
    records_root.mkdir(mode=0o700)
    records: list[dict[str, Any]] = []
    raw_records: list[dict[str, Any]] = []
    outcomes: list[dict[str, Any]] = []
    prior_error: BaseException | None = None
    for expected in plan:
        token = f"call_{expected['call_ordinal']:04d}"
        if prior_error is not None:
            error = {
                "schema": "schwo.phase6.v3_1_x.node_error.v1",
                "call_ordinal": expected["call_ordinal"],
                "key": expected["key"],
                "node": expected["node"],
                "status": "NOT_STARTED_AFTER_PRIOR_FAILURE",
                "scientific_pass": False,
                "exception_type": type(prior_error).__name__,
                "exception_message": str(prior_error),
            }
            error_identity = _exclusive_publish(
                records_root / f"{token}.error.json", canonical_bytes(error)
            )
            outcomes.append({**error, "error": error_identity})
            continue
        overlay_root = overlays / token
        overlay_identity = materialize_overlay(
            BHPT_SNAPSHOT_ROOT,
            overlay_root,
            expected["node"]["overlay_variant"],
        )
        request = build_wls_request(expected, overlay_identity)
        request_path = records_root / f"{token}.request.json"
        output_path = records_root / f"{token}.raw.json"
        _exclusive_publish(request_path, canonical_bytes(request))
        validate_overlay(overlay_root, expected["node"]["overlay_variant"])
        overlay_start = _overlay_inode_inventory(overlay_root)
        overlay_start_identity = _exclusive_publish(
            records_root / f"{token}.overlay_start.json",
            canonical_bytes(overlay_start),
        )
        try:
            raw = dict(child_runner(request_path, output_path, expected))
            if not output_path.is_file() or output_path.is_symlink():
                raise ExternalDirectContractError(
                    "controller-owned raw publication missing"
                )
            raw_from_file = load_canonical(output_path)
            if raw_from_file != raw:
                raise ExternalDirectContractError("child return/file payload mismatch")
            lifecycle_paths = {
                "request": request_path,
                "prelaunch": output_path.with_suffix(".prelaunch.json"),
                "running": output_path.with_suffix(".running.json"),
                "stdout": output_path.with_suffix(".stdout.raw"),
                "stderr": output_path.with_suffix(".stderr.raw"),
                "receipt": output_path.with_suffix(".receipt.json"),
                "terminal": output_path.with_suffix(".terminal.json"),
                "raw": output_path,
            }
            lifecycle = {
                name: _file_identity(path) for name, path in lifecycle_paths.items()
            }
            validate_overlay(overlay_root, expected["node"]["overlay_variant"])
            overlay_end = _overlay_inode_inventory(overlay_root)
            if overlay_end != overlay_start:
                raise ExternalDirectContractError("overlay inode/source replacement")
            overlay_end_identity = _exclusive_publish(
                records_root / f"{token}.overlay_end.json",
                canonical_bytes(overlay_end),
            )
            derived = derive_node_record(
                raw, expected, expected_loaded_sources=request["loaded_source_records"]
            )
            record_identity = _exclusive_publish(
                records_root / f"{token}.record.json", canonical_bytes(derived)
            )
            raw_records.append(raw)
            records.append(derived)
            outcomes.append(
                {
                    "schema": "schwo.phase6.v3_1_x.node_outcome.v1",
                    "call_ordinal": expected["call_ordinal"],
                    "key": expected["key"],
                    "node": expected["node"],
                    "status": "SUCCESS",
                    "scientific_pass": True,
                    "lifecycle": lifecycle,
                    "overlay_inode_start": overlay_start_identity,
                    "overlay_inode_end": overlay_end_identity,
                    "record": record_identity,
                }
            )
        except BaseException as exc:
            prior_error = exc
            error = {
                "schema": "schwo.phase6.v3_1_x.node_error.v1",
                "call_ordinal": expected["call_ordinal"],
                "key": expected["key"],
                "node": expected["node"],
                "status": "ERROR",
                "scientific_pass": False,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
            }
            error_identity = _exclusive_publish(
                records_root / f"{token}.error.json", canonical_bytes(error)
            )
            outcomes.append({**error, "error": error_identity})
    _exclusive_publish(evidence_root / "raw_records.jsonl", _jsonl_bytes(raw_records))
    _exclusive_publish(evidence_root / "records.jsonl", _jsonl_bytes(records))
    _exclusive_publish(evidence_root / "outcomes.jsonl", _jsonl_bytes(outcomes))
    if len(outcomes) != len(plan) or [
        item["call_ordinal"] for item in outcomes
    ] != list(range(len(plan))):
        raise ExternalDirectContractError("node outcome totality/order mismatch")
    if prior_error is not None:
        raise prior_error
    validate_node_records(records, stage)
    return records, raw_records


def validate_execution_outcomes(root: Path, stage: str) -> list[dict[str, Any]]:
    """Reload the exact success-or-error index; PASS roots admit successes only."""

    plan = expected_graph(stage)
    outcomes = load_jsonl(root / "outcomes.jsonl")
    if len(outcomes) != len(plan):
        raise ExternalDirectContractError("outcome index cardinality mismatch")
    for expected, outcome in zip(plan, outcomes, strict=True):
        if (
            outcome.get("schema") != "schwo.phase6.v3_1_x.node_outcome.v1"
            or outcome.get("call_ordinal") != expected["call_ordinal"]
            or outcome.get("key") != expected["key"]
            or outcome.get("node") != expected["node"]
            or outcome.get("status") != "SUCCESS"
            or outcome.get("scientific_pass") is not True
        ):
            raise ExternalDirectContractError("PASS outcome index drift")
        lifecycle = outcome.get("lifecycle")
        if not isinstance(lifecycle, Mapping) or set(lifecycle) != {
            "request",
            "prelaunch",
            "running",
            "stdout",
            "stderr",
            "receipt",
            "terminal",
            "raw",
        }:
            raise ExternalDirectContractError("child lifecycle totality mismatch")
        start_identity = outcome.get("overlay_inode_start")
        end_identity = outcome.get("overlay_inode_end")
        if (
            not isinstance(start_identity, Mapping)
            or not isinstance(end_identity, Mapping)
            or _file_identity(Path(start_identity["path"])) != start_identity
            or _file_identity(Path(end_identity["path"])) != end_identity
            or load_canonical(Path(start_identity["path"]))
            != load_canonical(Path(end_identity["path"]))
        ):
            raise ExternalDirectContractError("overlay inode closure drift")
        for identity in lifecycle.values():
            if (
                not isinstance(identity, Mapping)
                or _file_identity(Path(identity["path"])) != identity
            ):
                raise ExternalDirectContractError("child lifecycle identity drift")
        prelaunch = load_canonical(Path(lifecycle["prelaunch"]["path"]))
        running = load_canonical(Path(lifecycle["running"]["path"]))
        receipt = load_canonical(Path(lifecycle["receipt"]["path"]))
        terminal = load_canonical(Path(lifecycle["terminal"]["path"]))
        expected_command = [
            str(WOLFRAM_KERNEL),
            "-script",
            str(WLS_PATH),
            str(Path(lifecycle["request"]["path"])),
            str(Path(lifecycle["raw"]["path"]).with_suffix(".child.raw.json")),
        ]
        if (
            prelaunch.get("schema") != "schwo.phase6.v3_1_x.child_prelaunch.v1"
            or prelaunch.get("call_ordinal") != expected["call_ordinal"]
            or prelaunch.get("request") != lifecycle["request"]
            or prelaunch.get("requested_environment") != REQUESTED_EXECUTION_ENVIRONMENT
            or running.get("schema") != "schwo.phase6.v3_1_x.child_running.v1"
            or running.get("call_ordinal") != expected["call_ordinal"]
            or running.get("prelaunch") != lifecycle["prelaunch"]
            or running.get("requested_environment") != REQUESTED_EXECUTION_ENVIRONMENT
            or prelaunch.get("argv") != expected_command
            or prelaunch.get("child_execution_kind") != "REAL_WOLFRAM_KERNEL"
            or prelaunch.get("cwd") != str(ROOT)
            or not isinstance(prelaunch.get("started_utc"), str)
            or not prelaunch["started_utc"].endswith("Z")
            or not isinstance(prelaunch.get("started_ns"), int)
        ):
            raise ExternalDirectContractError("child prelaunch/running semantic drift")
        for item, schema in (
            (receipt, "schwo.phase6.v3_1_x.child_receipt.v2"),
            (terminal, "schwo.phase6.v3_1_x.child_terminal.v2"),
        ):
            if (
                item.get("schema") != schema
                or item.get("call_ordinal") != expected["call_ordinal"]
                or item.get("requested_environment") != REQUESTED_EXECUTION_ENVIRONMENT
                or item.get("observed_environment") != OBSERVED_CLEAN_LAUNCH_ENVIRONMENT
                or item.get("returncode") != 0
                or item.get("signal") is not None
                or item.get("timed_out") is not False
                or item.get("popen_wait_called") is not True
                or item.get("child_reaped") is not True
                or item.get("process_group_empty") is not True
                or item.get("wait_error") is not None
                or item.get("exception_type") is not None
                or item.get("exception_message") is not None
                or item.get("child_execution_kind") != "REAL_WOLFRAM_KERNEL"
                or item.get("argv") != expected_command
                or item.get("cwd") != str(ROOT)
                or item.get("prelaunch") != lifecycle["prelaunch"]
                or item.get("running") != lifecycle["running"]
                or item.get("pid") != running.get("pid")
                or item.get("sid") != running.get("sid")
                or item.get("pgid") != running.get("pgid")
                or not isinstance(item.get("started_utc"), str)
                or not isinstance(item.get("finished_utc"), str)
                or not item["started_utc"].endswith("Z")
                or not item["finished_utc"].endswith("Z")
                or item["finished_utc"] < item["started_utc"]
            ):
                raise ExternalDirectContractError("child terminal semantic drift")
        if terminal.get("receipt") != lifecycle["receipt"]:
            raise ExternalDirectContractError("child receipt/terminal binding drift")
        for stream_name in ("stdout", "stderr"):
            stream = terminal.get(stream_name)
            if (
                not isinstance(stream, Mapping)
                or stream.get("state") != "CLOSED"
                or stream.get("error") is not None
                or stream.get("identity") != lifecycle[stream_name]
            ):
                raise ExternalDirectContractError("child stream closure semantic drift")
        if lifecycle["stderr"]["size"] != 0:
            raise ExternalDirectContractError("child stderr contract mismatch")
        if _file_identity(Path(outcome["record"]["path"])) != outcome["record"]:
            raise ExternalDirectContractError("node record identity drift")
    return outcomes


def _seal_tree(root: Path) -> None:
    for path in sorted(
        (item for item in root.rglob("*") if item.is_file()), reverse=True
    ):
        if path.is_symlink() or path.stat().st_nlink != 1:
            raise ExternalDirectContractError("terminal file link drift")
        os.chmod(path, 0o444)
    for path in sorted(
        (item for item in root.rglob("*") if item.is_dir()),
        key=lambda p: len(p.parts),
        reverse=True,
    ):
        if path.is_symlink():
            raise ExternalDirectContractError("terminal directory symlink")
        os.chmod(path, 0o555)
        _fsync_directory(path)


def build_manifest(
    root: Path, *, state: str, exclude: Sequence[str] = ("manifest.json",)
) -> dict[str, Any]:
    excluded = set(exclude)
    artifacts = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative in excluded:
            continue
        identity = _file_identity(path)
        artifacts[relative] = {
            key: identity[key] for key in ("sha256", "size", "mode", "nlink")
        }
    return {
        "schema": "schwo.phase6.v3_1_x.external_direct_manifest.v1",
        "gate_id": GATE_ID,
        "artifact_rev": ARTIFACT_REV,
        "overall_state": state,
        "artifacts": artifacts,
    }


def validate_manifest(root: Path, *, expected_state: str) -> dict[str, Any]:
    manifest = load_canonical(root / "manifest.json")
    if manifest != build_manifest(root, state=expected_state):
        raise ExternalDirectContractError("manifest rebuild mismatch")
    return manifest


def _terminalize_failure(root: Path, stage: str, exc: BaseException) -> None:
    if not root.exists() or root.is_symlink():
        return
    try:
        failure = {
            "schema": "schwo.phase6.v3_1_x.failure.v1",
            "gate_id": GATE_ID,
            "stage": stage,
            "scientific_pass": False,
            "resumable": False,
            "retry_permitted": False,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "global_green": False,
        }
        if not (root / "failure.json").exists():
            _exclusive_publish(root / "failure.json", canonical_bytes(failure))
        _seal_tree(root)
        os.chmod(root, 0o755)
        if not (root / "manifest.json").exists():
            manifest = build_manifest(root, state="FAIL")
            _exclusive_publish(root / "manifest.json", canonical_bytes(manifest))
        os.chmod(root, 0o555)
        _fsync_directory(root.parent)
    except BaseException as publication_exc:
        raise ExternalDirectContractError(
            "failure terminal publication incomplete"
        ) from publication_exc


def _consume_dispatch(root: Path, authority: Mapping[str, Any]) -> dict[str, Any]:
    payload = authority["payload"]
    consumption = {
        "schema": "schwo.phase6.v3_1_x.dispatch_consumption.v1",
        "gate_id": GATE_ID,
        "stage": payload["stage"],
        "one_use_id": payload["one_use_id"],
        "dispatch": authority["identity"],
        "exact_root": str(root),
        "implementation_hashes": payload["implementation_hashes"],
        "implementation_review": authority["implementation_review"],
        "invocation": payload["invocation"],
        "requested_environment": payload["requested_environment"],
        "observed_environment": payload["observed_environment"],
        "science_calls_before_consumption": 0,
        "predecessor_science_reused": False,
        "sentinel_science_reused": False,
    }
    if "operation" in payload:
        consumption["operation"] = payload["operation"]
    if authority.get("micro_authority") is not None:
        consumption["micro_authority"] = authority["micro_authority"]
    _exclusive_publish(root / "dispatch_consumption.json", canonical_bytes(consumption))
    return consumption


@contextmanager
def _begin_root(authority: Mapping[str, Any], start_gate: Mapping[str, Any]) -> Any:
    """Create and hold the one never-replaced writer lock through closure."""

    root = authority["root"]
    root.mkdir(mode=0o700, parents=False, exist_ok=False)
    lock_path = root / ".writer.lock"
    _exclusive_publish(
        lock_path,
        canonical_bytes(
            {
                "schema": "schwo.phase6.v3_1_x.stable_writer_lock.v1",
                "pid": os.getpid(),
                "gate_id": GATE_ID,
                "stage": authority["payload"]["stage"],
            }
        ),
        mode=0o400,
    )
    fd = os.open(lock_path, os.O_RDONLY)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise ExternalDirectContractError("stable writer lock unavailable") from exc
        _exclusive_publish(
            root / "writer_exclusion.json",
            canonical_bytes(
                {
                    "schema": "schwo.phase6.v3_1_x.writer_exclusion.v1",
                    "stable_lock": _file_identity(lock_path),
                    "flock_mode": "LOCK_EX|LOCK_NB",
                    "held_until_terminal_closure": True,
                }
            ),
        )
        consumption = _consume_dispatch(root, authority)
        source = build_source_ledger(start_gate)
        _exclusive_publish(root / "source_start.json", canonical_bytes(source))
        _exclusive_publish(
            root / "static_contract.json",
            canonical_bytes(start_gate["static_contract"]),
        )
        yield root, consumption
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def _validate_micro_wls_result(
    raw: Mapping[str, Any],
    request: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> list[list[Any]]:
    required = {
        "schema",
        "operation",
        "key",
        "node",
        "overlay",
        "projection_field_order",
        "expected_source_projection",
        "loaded_contexts_start",
        "loaded_contexts_end",
        "loaded_source_start",
        "loaded_source_end",
        "loaded_source_projection_start",
        "loaded_source_projection_end",
        "preload_state",
        "paclet",
        "counters",
        "scientific_evidence",
        "reusable_as_science",
        "reusable_as_full_sentinel_record",
        "terminal_state",
        "runtime",
    }
    expected_projection = normalize_loaded_source_ledger(
        request["loaded_source_records"]
    )
    if (
        set(raw) != required
        or raw.get("schema") != "schwo.phase6.v3_1_x.source_load_micro_wls_result.v1"
        or raw.get("operation") != MICRO_OPERATION
        or raw.get("key") != expected["key"]
        or raw.get("node") != expected["node"]
        or raw.get("overlay") != request["overlay"]
        or raw.get("projection_field_order") != list(SOURCE_FIELD_ORDER)
        or raw.get("expected_source_projection") != expected_projection
        or raw.get("loaded_contexts_start") != list(LOADED_SOURCE_CONTEXTS)
        or raw.get("loaded_contexts_end") != list(LOADED_SOURCE_CONTEXTS)
        or raw.get("counters") != MICRO_COUNTERS
        or raw.get("scientific_evidence") is not False
        or raw.get("reusable_as_science") is not False
        or raw.get("reusable_as_full_sentinel_record") is not False
        or raw.get("terminal_state") != "PASS_PENDING_FORMAL_T7_REVIEW"
    ):
        raise ExternalDirectContractError("micro WLS result contract mismatch")
    start = normalize_loaded_source_ledger(raw["loaded_source_start"])
    end = normalize_loaded_source_ledger(raw["loaded_source_end"])
    if (
        start != expected_projection
        or end != expected_projection
        or raw["loaded_source_projection_start"] != expected_projection
        or raw["loaded_source_projection_end"] != expected_projection
    ):
        raise ExternalDirectContractError("micro WLS source projection mismatch")
    preload = raw["preload_state"]
    if (
        not isinstance(preload, Mapping)
        or set(preload)
        != {
            "packages",
            "context_path",
            "search_path",
            "regge_wheeler_context_count",
            "regge_wheeler_paclet_candidate_count",
            "find_file_before_load",
        }
        or preload["regge_wheeler_context_count"] != 0
        or type(preload["regge_wheeler_paclet_candidate_count"]) is not int
        or preload["regge_wheeler_paclet_candidate_count"] < 0
        or (
            preload["find_file_before_load"] is not None
            and not isinstance(preload["find_file_before_load"], str)
        )
        or any(
            not isinstance(items, list)
            or not all(isinstance(item, str) for item in items)
            for items in (
                preload["packages"],
                preload["context_path"],
                preload["search_path"],
            )
        )
        or any(
            item.startswith("ReggeWheeler`")
            for item in (*preload["packages"], *preload["context_path"])
        )
    ):
        raise ExternalDirectContractError("micro preloaded context contamination")
    paclet = raw["paclet"]
    if (
        not isinstance(paclet, Mapping)
        or set(paclet) != {"candidate_count_after_load", "loaded_count", "loaded_root"}
        or type(paclet["candidate_count_after_load"]) is not int
        or paclet["candidate_count_after_load"] < 1
        or paclet["loaded_count"] != 1
        or paclet["loaded_root"] != request["overlay"]["root"]
    ):
        raise ExternalDirectContractError("micro Paclet origin mismatch")
    runtime = raw["runtime"]
    if (
        not isinstance(runtime, Mapping)
        or set(runtime)
        != {"wolfram_version", "system_id", "observed_environment", "fake_child"}
        or not isinstance(runtime["wolfram_version"], str)
        or not isinstance(runtime["system_id"], str)
        or runtime["fake_child"] is not False
        or not validate_clean_launch_environment(runtime["observed_environment"])
    ):
        raise ExternalDirectContractError("micro runtime identity mismatch")
    return expected_projection


def _micro_lifecycle_paths(root: Path) -> dict[str, Path]:
    return {
        "request": root / "micro_request.json",
        "prelaunch": root / "child.prelaunch.json",
        "running": root / "child.running.json",
        "stdout": root / "child.stdout.raw",
        "stderr": root / "child.stderr.raw",
        "receipt": root / "child.receipt.json",
        "terminal": root / "child.terminal.json",
        "raw": root / "source_load_result.json",
    }


def _validate_micro_lifecycle(
    root: Path, expected: Mapping[str, Any]
) -> dict[str, dict[str, Any]]:
    paths = _micro_lifecycle_paths(root)
    identities = {name: _file_identity(path) for name, path in paths.items()}
    prelaunch = load_canonical(paths["prelaunch"])
    running = load_canonical(paths["running"])
    receipt = load_canonical(paths["receipt"])
    terminal = load_canonical(paths["terminal"])
    command = [
        str(WOLFRAM_KERNEL),
        "-script",
        str(WLS_PATH),
        str(paths["request"]),
        str(root / "child.staging.json"),
    ]
    if (
        prelaunch.get("schema") != "schwo.phase6.v3_1_x.child_prelaunch.v1"
        or prelaunch.get("call_ordinal") != 0
        or prelaunch.get("argv") != command
        or prelaunch.get("cwd") != str(ROOT)
        or prelaunch.get("request") != identities["request"]
        or prelaunch.get("kernel")
        != _verify_bound_file(WOLFRAM_KERNEL, WOLFRAM_KERNEL_SHA256)
        or prelaunch.get("wls") != _file_identity(WLS_PATH)
        or prelaunch.get("raw_final_path") != str(paths["raw"])
        or prelaunch.get("raw_staging_path") != str(root / "child.staging.json")
        or prelaunch.get("requested_environment") != REQUESTED_EXECUTION_ENVIRONMENT
        or prelaunch.get("child_execution_kind") != "REAL_WOLFRAM_KERNEL"
        or running.get("schema") != "schwo.phase6.v3_1_x.child_running.v1"
        or running.get("call_ordinal") != 0
        or running.get("prelaunch") != identities["prelaunch"]
        or running.get("requested_environment") != REQUESTED_EXECUTION_ENVIRONMENT
    ):
        raise ExternalDirectContractError("micro child prelaunch/running mismatch")
    if (
        not all(
            type(running.get(key)) is int and running[key] > 0
            for key in ("pid", "sid", "pgid")
        )
        or running["pid"] != running["sid"]
        or running["pid"] != running["pgid"]
    ):
        raise ExternalDirectContractError("micro child process identity mismatch")
    for item, schema in (
        (receipt, "schwo.phase6.v3_1_x.child_receipt.v2"),
        (terminal, "schwo.phase6.v3_1_x.child_terminal.v2"),
    ):
        if (
            item.get("schema") != schema
            or item.get("call_ordinal") != 0
            or item.get("argv") != command
            or item.get("cwd") != str(ROOT)
            or item.get("requested_environment") != REQUESTED_EXECUTION_ENVIRONMENT
            or item.get("observed_environment") != OBSERVED_CLEAN_LAUNCH_ENVIRONMENT
            or item.get("returncode") != 0
            or item.get("signal") is not None
            or item.get("timed_out") is not False
            or item.get("popen_wait_called") is not True
            or item.get("child_reaped") is not True
            or item.get("process_group_empty") is not True
            or item.get("wait_error") is not None
            or item.get("exception_type") is not None
            or item.get("exception_message") is not None
            or item.get("child_execution_kind") != "REAL_WOLFRAM_KERNEL"
            or item.get("prelaunch") != identities["prelaunch"]
            or item.get("running") != identities["running"]
            or item.get("pid") != running["pid"]
            or item.get("sid") != running["sid"]
            or item.get("pgid") != running["pgid"]
        ):
            raise ExternalDirectContractError("micro child terminal mismatch")
    if terminal.get("receipt") != identities["receipt"]:
        raise ExternalDirectContractError("micro child receipt binding mismatch")
    for stream_name in ("stdout", "stderr"):
        stream = terminal.get(stream_name)
        if (
            not isinstance(stream, Mapping)
            or stream.get("state") != "CLOSED"
            or stream.get("error") is not None
            or stream.get("identity") != identities[stream_name]
            or identities[stream_name]["size"] != 0
        ):
            raise ExternalDirectContractError("micro child stream closure mismatch")
    if (root / "child.staging.json").exists() or (
        root / "child.staging.json"
    ).is_symlink():
        raise ExternalDirectContractError("micro child staging residue")
    return identities


def _micro_allowed_files(root: Path) -> set[str]:
    overlay_files = {
        f"overlay/{item['path']}"
        for item in base_snapshot_identity()["identity_records"]
    }
    return overlay_files | {
        ".writer.lock",
        "writer_exclusion.json",
        "dispatch_consumption.json",
        "source_start.json",
        "static_contract.json",
        "overlay_identity_start.json",
        "micro_request.json",
        "child.prelaunch.json",
        "child.running.json",
        "child.stdout.raw",
        "child.stderr.raw",
        "child.receipt.json",
        "child.terminal.json",
        "source_load_result.json",
        "overlay_identity_end.json",
        "source_end.json",
        "micro_result.json",
        "manifest.json",
    }


def validate_source_load_micro(
    root: Path,
    *,
    require_real_child: bool = True,
    validate_live_sources: bool = True,
) -> None:
    root = _validate_existing_micro_root_path(root)
    if stat.S_IMODE(root.stat().st_mode) != 0o555:
        raise ExternalDirectContractError("micro root mode mismatch")
    validate_manifest(root, expected_state="PASS")
    actual_files = {
        item.relative_to(root).as_posix() for item in root.rglob("*") if item.is_file()
    }
    if actual_files != _micro_allowed_files(root):
        raise ExternalDirectContractError("micro artifact allowlist mismatch")
    actual_directories = {
        item.relative_to(root).as_posix() for item in root.rglob("*") if item.is_dir()
    }
    if actual_directories != {
        "overlay",
        "overlay/Kernel",
        "overlay/Kernel/MST",
        "overlay/Tests",
        "overlay/Tests/Correctness",
    } or any(
        stat.S_IMODE(item.stat().st_mode) != 0o555
        for item in root.rglob("*")
        if item.is_dir()
    ):
        raise ExternalDirectContractError("micro directory closure mismatch")
    if (
        sum(item.stat().st_size for item in root.rglob("*") if item.is_file())
        > MICRO_MAX_ROOT_BYTES
    ):
        raise ExternalDirectContractError("micro root size cap exceeded")
    overlay_identity = validate_overlay(root / "overlay", "rin10_m1")
    overlay_start = load_canonical(root / "overlay_identity_start.json")
    overlay_end = load_canonical(root / "overlay_identity_end.json")
    if overlay_start != overlay_end or overlay_end != _overlay_inode_inventory(
        root / "overlay"
    ):
        raise ExternalDirectContractError("micro overlay inode closure mismatch")
    source_start = load_canonical(root / "source_start.json")
    source_end = load_canonical(root / "source_end.json")
    if source_start != source_end:
        raise ExternalDirectContractError("micro source authority closure mismatch")
    expected = expected_graph("sentinel")[0]
    request = load_canonical(root / "micro_request.json")
    expected_request = build_wls_request(
        expected, overlay_identity, operation=MICRO_OPERATION
    )
    if request != expected_request:
        raise ExternalDirectContractError("micro request reconstruction mismatch")
    raw = load_canonical(root / "source_load_result.json")
    projection = _validate_micro_wls_result(raw, request, expected)
    lifecycle = _validate_micro_lifecycle(root, expected)
    result = load_canonical(root / "micro_result.json")
    required_result = {
        "schema",
        "gate_id",
        "operation",
        "root",
        "key",
        "node",
        "status",
        "child_execution_kind",
        "dispatch",
        "dispatch_consumption",
        "implementation_review",
        "repair2_package",
        "implementation_hashes",
        "request",
        "source_start",
        "source_end",
        "overlay_identity_start",
        "overlay_identity_end",
        "source_load_result",
        "child_lifecycle",
        "source_projection_sha256",
        "counters",
        "runtime",
        "scientific_evidence",
        "reusable_as_science",
        "reusable_as_full_sentinel_record",
        "full_sentinel_call_count_contribution",
        "global_green",
    }
    if (
        set(result) != required_result
        or result["schema"] != "schwo.phase6.v3_1_x.source_load_micro_result.v1"
        or result["gate_id"] != GATE_ID
        or result["operation"] != MICRO_OPERATION
        or result["root"] != str(root)
        or result["key"] != expected["key"]
        or result["node"] != expected["node"]
        or result["status"] != "PASS_PENDING_FORMAL_T7_REVIEW"
        or result["child_execution_kind"] != "REAL_WOLFRAM_KERNEL"
        or result["repair2_package"] != source_start["repair2_package"]
        or result["implementation_hashes"] != source_start["implementation_hashes"]
        or result["request"] != _file_identity(root / "micro_request.json")
        or result["source_start"] != _file_identity(root / "source_start.json")
        or result["source_end"] != _file_identity(root / "source_end.json")
        or result["overlay_identity_start"]
        != _file_identity(root / "overlay_identity_start.json")
        or result["overlay_identity_end"]
        != _file_identity(root / "overlay_identity_end.json")
        or result["source_load_result"]
        != _file_identity(root / "source_load_result.json")
        or result["child_lifecycle"] != lifecycle
        or result["source_projection_sha256"] != _projection_sha256(projection)
        or result["counters"] != MICRO_COUNTERS
        or result["runtime"] != raw["runtime"]
        or result["scientific_evidence"] is not False
        or result["reusable_as_science"] is not False
        or result["reusable_as_full_sentinel_record"] is not False
        or result["full_sentinel_call_count_contribution"] != 0
        or result["global_green"] is not False
    ):
        raise ExternalDirectContractError("micro result reload mismatch")
    consumption = load_canonical(root / "dispatch_consumption.json")
    if (
        consumption.get("stage") != MICRO_STAGE
        or consumption.get("operation") != MICRO_OPERATION
        or consumption.get("science_calls_before_consumption") != 0
        or result["dispatch_consumption"]
        != _file_identity(root / "dispatch_consumption.json")
        or result["dispatch"] != consumption["dispatch"]
        or result["implementation_review"] != consumption["implementation_review"]
    ):
        raise ExternalDirectContractError("micro dispatch consumption mismatch")
    if require_real_child and result["child_execution_kind"] != "REAL_WOLFRAM_KERNEL":
        raise ExternalDirectContractError("formal micro rejects test double")
    if validate_live_sources:
        live = verify_start_gate()
        if build_source_ledger(live) != source_start:
            raise ExternalDirectContractError("micro live source drift")


def run_source_load_micro(dispatch_path: Path, dispatch_sha: str) -> dict[str, Any]:
    """Consume one formal micro dispatch and launch one real zero-science child."""

    start_gate = verify_start_gate()
    authority = validate_dispatch(
        dispatch_path,
        dispatch_sha,
        stage=MICRO_STAGE,
        start_gate=start_gate,
    )
    stage = MICRO_OPERATION
    with _begin_root(authority, start_gate) as (root, _):
        try:
            expected = expected_graph("sentinel")[0]
            overlay_identity = materialize_overlay(
                BHPT_SNAPSHOT_ROOT,
                root / "overlay",
                expected["node"]["overlay_variant"],
            )
            validate_overlay(root / "overlay", expected["node"]["overlay_variant"])
            overlay_start = _overlay_inode_inventory(root / "overlay")
            overlay_start_identity = _exclusive_publish(
                root / "overlay_identity_start.json", canonical_bytes(overlay_start)
            )
            request = build_wls_request(
                expected, overlay_identity, operation=MICRO_OPERATION
            )
            request_identity = _exclusive_publish(
                root / "micro_request.json", canonical_bytes(request)
            )
            raw = dict(
                run_wolfram_child(
                    root / "micro_request.json",
                    root / "source_load_result.json",
                    expected,
                    timeout_seconds=120,
                    lifecycle_prefix=root / "child",
                )
            )
            projection = _validate_micro_wls_result(raw, request, expected)
            overlay_end = _overlay_inode_inventory(root / "overlay")
            if overlay_end != overlay_start:
                raise ExternalDirectContractError(
                    "micro overlay inode/source replacement"
                )
            overlay_end_identity = _exclusive_publish(
                root / "overlay_identity_end.json", canonical_bytes(overlay_end)
            )
            lifecycle = _validate_micro_lifecycle(root, expected)
            source_end = build_source_ledger(start_gate)
            if source_end != load_canonical(root / "source_start.json"):
                raise ExternalDirectContractError("micro source-end drift")
            source_end_identity = _exclusive_publish(
                root / "source_end.json", canonical_bytes(source_end)
            )
            result = {
                "schema": "schwo.phase6.v3_1_x.source_load_micro_result.v1",
                "gate_id": GATE_ID,
                "operation": MICRO_OPERATION,
                "root": str(root),
                "key": expected["key"],
                "node": expected["node"],
                "status": "PASS_PENDING_FORMAL_T7_REVIEW",
                "child_execution_kind": "REAL_WOLFRAM_KERNEL",
                "dispatch": authority["identity"],
                "dispatch_consumption": _file_identity(
                    root / "dispatch_consumption.json"
                ),
                "implementation_review": authority["implementation_review"],
                "repair2_package": start_gate["repair2_package_identity"],
                "implementation_hashes": start_gate["implementation_hashes"],
                "request": request_identity,
                "source_start": _file_identity(root / "source_start.json"),
                "source_end": source_end_identity,
                "overlay_identity_start": overlay_start_identity,
                "overlay_identity_end": overlay_end_identity,
                "source_load_result": _file_identity(root / "source_load_result.json"),
                "child_lifecycle": lifecycle,
                "source_projection_sha256": _projection_sha256(projection),
                "counters": MICRO_COUNTERS,
                "runtime": raw["runtime"],
                "scientific_evidence": False,
                "reusable_as_science": False,
                "reusable_as_full_sentinel_record": False,
                "full_sentinel_call_count_contribution": 0,
                "global_green": False,
            }
            _exclusive_publish(root / "micro_result.json", canonical_bytes(result))
            _seal_tree(root)
            os.chmod(root, 0o755)
            manifest = build_manifest(root, state="PASS")
            manifest_identity = _exclusive_publish(
                root / "manifest.json", canonical_bytes(manifest)
            )
            os.chmod(root, 0o555)
            _fsync_directory(root.parent)
            validate_source_load_micro(
                root, require_real_child=True, validate_live_sources=False
            )
            return {"root": str(root), "manifest": manifest_identity, "result": result}
        except BaseException as exc:
            _terminalize_failure(root, stage, exc)
            raise


def run_sentinel(
    dispatch_path: Path,
    dispatch_sha: str,
    *,
    child_runner: ChildRunner = run_wolfram_child,
) -> dict[str, Any]:
    start_gate = verify_start_gate()
    authority = validate_dispatch(
        dispatch_path, dispatch_sha, stage="sentinel", start_gate=start_gate
    )
    stage = "external_sentinel"
    with _begin_root(authority, start_gate) as (root, _):
        try:
            records, _ = execute_external_plan(
                root / "external_evidence", stage="sentinel", child_runner=child_runner
            )
            selected = [item for item in records if item["node"]["node_id"] == "P1"]
            if len(selected) != 23:
                raise ExternalDirectContractError(
                    "sentinel selected-node totality mismatch"
                )
            sentinel_budgets = build_sentinel_budgets(records)
            if sentinel_budgets["status"] != "PASS":
                raise ExternalDirectContractError(
                    "sentinel numerical admission failure"
                )
            projection = resource_projection(
                records, free_bytes=shutil.disk_usage(ROOT).free
            )
            if (
                not projection["runtime_gate_passed"]
                or not projection["disk_gate_passed"]
            ):
                raise ExternalDirectContractError("sentinel resource gate failed")
            source_end = build_source_ledger(start_gate)
            if source_end != load_canonical(root / "source_start.json"):
                raise ExternalDirectContractError("sentinel source-end drift")
            _exclusive_publish(root / "source_end.json", canonical_bytes(source_end))
            _exclusive_publish(
                root / "resource_projection.json", canonical_bytes(projection)
            )
            _exclusive_publish(
                root / "sentinel_budgets.json", canonical_bytes(sentinel_budgets)
            )
            _exclusive_publish(
                root / "sentinel_result.json",
                canonical_bytes(
                    {
                        "schema": "schwo.phase6.v3_1_x.sentinel_result.v1",
                        "gate_id": GATE_ID,
                        "status": "PASS_NOT_REUSABLE",
                        "call_count": 35,
                        "boundary_solution_count": 70,
                        "overlap_count": 105,
                        "selected_key_count": 23,
                        "scientific_evidence_scope": "sentinel_only",
                        "official_reuse_permitted": False,
                        "independent_review_state": "NOT_ASSESSED",
                    }
                ),
            )
            _seal_tree(root)
            os.chmod(root, 0o755)
            manifest = build_manifest(root, state="PASS")
            identity = _exclusive_publish(
                root / "manifest.json", canonical_bytes(manifest)
            )
            os.chmod(root, 0o555)
            validate_sentinel(root)
            return {
                "root": str(root),
                "manifest": identity,
                "resource_projection": projection,
            }
        except BaseException as exc:
            _terminalize_failure(root, stage, exc)
            raise


def validate_sentinel(root: Path) -> None:
    root = root.resolve(strict=True)
    if stat.S_IMODE(root.stat().st_mode) != 0o555:
        raise ExternalDirectContractError("sentinel root mode mismatch")
    validate_manifest(root, expected_state="PASS")
    records = load_jsonl(root / "external_evidence/records.jsonl")
    validate_node_records(records, "sentinel")
    validate_execution_outcomes(root / "external_evidence", "sentinel")
    validate_sentinel_budgets(load_canonical(root / "sentinel_budgets.json"), records)
    result = load_canonical(root / "sentinel_result.json")
    if (
        result.get("status") != "PASS_NOT_REUSABLE"
        or result.get("official_reuse_permitted") is not False
    ):
        raise ExternalDirectContractError("sentinel result mismatch")
    projection = load_canonical(root / "resource_projection.json")
    if not projection.get("runtime_gate_passed") or not projection.get(
        "disk_gate_passed"
    ):
        raise ExternalDirectContractError("sentinel resource closure mismatch")
    if load_canonical(root / "source_start.json") != load_canonical(
        root / "source_end.json"
    ):
        raise ExternalDirectContractError("sentinel source closure mismatch")


def _external_selected(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    selected = []
    for offset in range(0, len(records), 7):
        record = records[offset + 1]
        overlap = record["overlaps"][1]
        selected.append(
            {
                "schema": "schwo.phase6.v3_1_x.external_selected.v1",
                "key": record["key"],
                "S": overlap["S"],
                "Gamma_flux": overlap["Gamma_flux"],
                "Gamma_S": overlap["Gamma_S"],
                "fresh_external_call_count": 7,
                "method": "NumericalIntegration",
                "genuinely_independent": True,
                "even_independent_solve": False,
                "predecessor_science_reused": False,
            }
        )
    return selected


def _compute_fresh_routes_before_c() -> dict[str, Any]:
    """Fresh Route A/U/B implementation, imported only on official science."""

    from schwgw.validation import phase6_v3_mode_greybody_cycle2 as cycle2
    from schwgw.validation import phase6_v3_mode_greybody_hp_replacement as hp

    modes = []
    ladders = []
    views = []
    for ordinal, key in enumerate(cycle2.build_mode_inventory()):
        mode, ladder = cycle2.solve_route_a_mode(key)
        modes.append(mode)
        ladders.extend(ladder)
        views.append(
            hp.selector_view(
                mode,
                ordinal=ordinal,
                record_sha256=hashlib.sha256(
                    cycle2.compact_jsonl_record(mode)
                ).hexdigest(),
            )
        )
    route_map = hp.build_route_map(views)
    route_u = []
    route_u_ladders = []
    route_map_sha = hashlib.sha256(canonical_bytes(route_map)).hexdigest()
    for entry in route_map["entries"]:
        if entry["selector"]["use_route_u"]:
            node_records, admission = hp.solve_route_u_ladder(
                entry, route_map_sha256=route_map_sha
            )
            route_u.extend(node_records)
            route_u_ladders.append(admission)
    ap_records = [cycle2.solve_ap_node(node) for node in cycle2.ap_node_plan()]
    return {
        "cycle2": cycle2,
        "hp": hp,
        "modes": modes,
        "ladders": ladders,
        "route_map": route_map,
        "route_u": route_u,
        "route_u_ladders": route_u_ladders,
        "ap": ap_records,
    }


def run_official(
    dispatch_path: Path,
    dispatch_sha: str,
    *,
    child_runner: ChildRunner = run_wolfram_child,
    fresh_routes_runner: Callable[
        [], Mapping[str, Any]
    ] = _compute_fresh_routes_before_c,
) -> dict[str, Any]:
    start_gate = verify_start_gate()
    authority = validate_dispatch(
        dispatch_path, dispatch_sha, stage="official", start_gate=start_gate
    )
    stage = "route_a_u_b"
    with _begin_root(authority, start_gate) as (root, _):
        try:
            routes = fresh_routes_runner()
            _exclusive_publish(
                root / "route_a_records.jsonl", _jsonl_bytes(routes["modes"])
            )
            _exclusive_publish(
                root / "route_a_ladders.jsonl", _jsonl_bytes(routes["ladders"])
            )
            _exclusive_publish(
                root / "unitarity_route_map.json", canonical_bytes(routes["route_map"])
            )
            _exclusive_publish(
                root / "route_u_records.jsonl", _jsonl_bytes(routes["route_u"])
            )
            _exclusive_publish(
                root / "route_u_ladders.jsonl", _jsonl_bytes(routes["route_u_ladders"])
            )
            _exclusive_publish(
                root / "route_b_records.jsonl", _jsonl_bytes(routes["ap"])
            )
            stage = "route_c"
            records, _ = execute_external_plan(
                root / "external_evidence", stage="official", child_runner=child_runner
            )
            budgets = validate_official_budgets(records)
            selected = _external_selected(records)
            stage = "thresholds"
            evaluation = routes["hp"].evaluate_all_thresholds(
                routes["modes"],
                routes["ladders"],
                routes["route_map"],
                routes["route_u"],
                routes["route_u_ladders"],
                routes["ap"],
                selected,
            )
            if not evaluation["all_pass"]:
                raise ExternalDirectContractError(
                    "whole-gate scientific threshold failure"
                )
            counts = evaluation["summary"]["counts"]
            if any(
                counts.get(key) != value
                for key, value in EXPECTED_COUNTS.items()
                if key in counts
            ):
                raise ExternalDirectContractError("whole-gate count drift")
            source_end = build_source_ledger(start_gate)
            if source_end != load_canonical(root / "source_start.json"):
                raise ExternalDirectContractError("official source-end drift")
            _exclusive_publish(root / "source_end.json", canonical_bytes(source_end))
            _exclusive_publish(
                root / "external_budgets.json", canonical_bytes({"budgets": budgets})
            )
            _exclusive_publish(
                root / "summary.json", canonical_bytes(evaluation["summary"])
            )
            _exclusive_publish(
                root / "uncertainty_budget.json",
                canonical_bytes(evaluation["uncertainty_budget"]),
            )
            _exclusive_publish(
                root / "official_result.json",
                canonical_bytes(
                    {
                        "schema": "schwo.phase6.v3_1_x.official_result.v1",
                        "gate_id": GATE_ID,
                        "status": "PASS_PENDING_FORMAL_T7_REVIEW",
                        "counts": EXPECTED_COUNTS,
                        "certificate_ids": list(CERTIFICATE_IDS),
                        "thresholds_passed": 16,
                        "predecessor_science_reused": False,
                        "sentinel_science_reused": False,
                        "global_green": False,
                    }
                ),
            )
            _seal_tree(root)
            os.chmod(root, 0o755)
            manifest = build_manifest(root, state="PASS")
            identity = _exclusive_publish(
                root / "manifest.json", canonical_bytes(manifest)
            )
            os.chmod(root, 0o555)
            validate_official(root, validate_live_sources=False)
            return {"root": str(root), "manifest": identity, "evaluation": evaluation}
        except BaseException as exc:
            _terminalize_failure(root, stage, exc)
            raise


def validate_official(root: Path, *, validate_live_sources: bool = True) -> None:
    root = root.resolve(strict=True)
    if stat.S_IMODE(root.stat().st_mode) != 0o555:
        raise ExternalDirectContractError("official root mode mismatch")
    validate_manifest(root, expected_state="PASS")
    records = load_jsonl(root / "external_evidence/records.jsonl")
    budgets = validate_official_budgets(records)
    validate_execution_outcomes(root / "external_evidence", "official")
    modes = load_jsonl(root / "route_a_records.jsonl")
    ladders = load_jsonl(root / "route_a_ladders.jsonl")
    route_map = load_canonical(root / "unitarity_route_map.json")
    route_u = load_jsonl(root / "route_u_records.jsonl")
    route_u_ladders = load_jsonl(root / "route_u_ladders.jsonl")
    route_b = load_jsonl(root / "route_b_records.jsonl")
    if (
        len(modes),
        len(ladders),
        len(route_u),
        len(route_u_ladders),
        len(route_b),
    ) != (496, 9920, 954, 318, 458):
        raise ExternalDirectContractError(
            "official Route-A/U/B reload cardinality mismatch"
        )
    result = load_canonical(root / "official_result.json")
    if (
        result.get("status") != "PASS_PENDING_FORMAL_T7_REVIEW"
        or result.get("counts") != EXPECTED_COUNTS
        or result.get("certificate_ids") != list(CERTIFICATE_IDS)
        or result.get("thresholds_passed") != 16
        or result.get("predecessor_science_reused") is not False
        or result.get("sentinel_science_reused") is not False
        or result.get("global_green") is not False
        or len(budgets) != 23
    ):
        raise ExternalDirectContractError("official result mismatch")
    if load_canonical(root / "source_start.json") != load_canonical(
        root / "source_end.json"
    ):
        raise ExternalDirectContractError("official source closure mismatch")
    if validate_live_sources:
        verify_start_gate()
        from schwgw.validation import phase6_v3_mode_greybody_hp_replacement as hp

        evaluation = hp.evaluate_all_thresholds(
            modes,
            ladders,
            route_map,
            route_u,
            route_u_ladders,
            route_b,
            _external_selected(records),
        )
        if (
            not evaluation["all_pass"]
            or load_canonical(root / "summary.json") != evaluation["summary"]
            or load_canonical(root / "uncertainty_budget.json")
            != evaluation["uncertainty_budget"]
        ):
            raise ExternalDirectContractError("official threshold reload mismatch")


def preflight_payload() -> dict[str, Any]:
    gate = verify_start_gate()
    return {
        "schema": "schwo.phase6.v3_1_x.preflight.v1",
        "gate_id": GATE_ID,
        "status": "PASS",
        "static_contract": gate["static_contract"],
        "implementation_hashes": gate["implementation_hashes"],
        "wolfram_launches": 0,
        "solver_science_calls": 0,
        "dispatch_files_created": 0,
        "real_roots_created": 0,
    }
