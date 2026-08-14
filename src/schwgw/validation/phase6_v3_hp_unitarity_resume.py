"""Additive, fail-closed resume controller for the interrupted V3.1-U root.

This module is deliberately control-plane only.  Numerical work is delegated
to the byte-frozen V3.1-U implementation after an immutable authority commit.
The original science files and the original ``source_start.json`` are never
rewritten.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
import base64
import ctypes
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shlex
import stat
import subprocess
import sys
from typing import Any, Callable, Iterator, Mapping, Sequence

from schwgw.validation.phase6_v3_mode_greybody import (
    ROOT,
    V31ContractError,
    build_inventory_payload,
    build_mode_inventory,
    canonical_bytes,
)
from schwgw.validation import phase6_v3_mode_greybody_cycle2 as cycle2
from schwgw.validation import phase6_v3_mode_greybody_hp_replacement as original


GATE_ID = "phase6_v3_1_u_resume_controller_repair_1"
PARENT_GATE_ID = "phase6_v3_1_hp_unitarity_deficit_replacement_v1"
PACKAGE_PATH = ROOT / "configs/phase6_v3_1_u_resume_controller_package.json"
PACKAGE_SHA256 = "2fcd2e4cc57845b32573047fa3989e1bfcd4f520eefcea6f6df6504d164602fe"
DESIGN_PATH = ROOT / "docs/phase6_v3_1_u_resume_controller_design.md"
DESIGN_SHA256 = "094235c0ce0158521da81ec0587899dc6dc942ab92866e8afe8f3102487fa9d7"
PROMPT_PATH = ROOT / "docs/prompts/phase6_t4_v3_1_u_resume_controller.md"
PROMPT_SHA256 = "72e40f540d3f406c6d1af79931d425b9efc8e5517f21d6e91ba9b1c8b0333b05"
PACKAGE_APPROVAL_PATH = (
    ROOT / "docs/handoffs/archive/"
    "T7_2026-08-12_v3_1_u_resume_controller_package_delta_review_1.md"
)
PACKAGE_APPROVAL_SHA256 = (
    "f2aa03db09dd344462cddcba392ded858663232a5948377b44c673651b9e0326"
)
REAL_ROOT = (
    ROOT / "runs/phase6/classic_scattering/"
    "v3_1_hp_unitarity_deficit_v1_20260811T143911Z_py314"
)
CONTROLLER_PATH = Path(__file__).resolve()
CLI_PATH = ROOT / "scripts/phase6_v3_1_hp_unitarity_resume.py"
UNIT_TEST_PATH = ROOT / "tests/unit/test_phase6_v3_hp_unitarity_resume.py"
REGRESSION_TEST_PATH = (
    ROOT / "tests/regression/test_phase6_v3_hp_unitarity_resume_publication.py"
)
ORIGINAL_PREFIX_RECORDS_SHA256 = (
    "932129a4921cd71b7867bcc2f0e146ed6940eb84403f366b58989e447402b9a0"
)
ORIGINAL_PREFIX_LADDERS_SHA256 = (
    "8f387abb83115ac76d87170bc5c1220d6effc6f4586c6202bb069fb35cb8d088"
)
ORIGINAL_PREFIX_RECORDS_SIZE = 943_913
ORIGINAL_PREFIX_LADDERS_SIZE = 16_898_419
ORIGINAL_PREFIX_MODE_COUNT = 435
ORIGINAL_PREFIX_LADDER_COUNT = 8_700
CHECKPOINT_INVENTORY_SHA256 = (
    "2269f129814c26d609cf3fdd0a451a5fd35661a576cf4d030f4f7b9516366d11"
)
LOCK_SHA256 = hashlib.sha256(b"").hexdigest()
RENAME_EXCL = 0x00000004


class ResumeContractError(V31ContractError):
    """A resume control-plane invariant failed."""


class InjectedInterruption(BaseException):
    """Test-only simulated process death at a durable boundary."""


FaultHook = Callable[[str, Path, int], None]


@dataclass(frozen=True)
class PrefixState:
    mode_count: int
    ladder_count: int
    next_ordinal: int
    records_sha256: str
    ladders_sha256: str
    records_size: int
    ladders_size: int
    next_mode: Mapping[str, Any] | None
    checkpoint_inventory_sha256: str


@dataclass(frozen=True)
class Authority:
    implementation_approval: Path
    implementation_approval_sha256: str
    dispatch: Path
    dispatch_sha256: str


@dataclass(frozen=True)
class ScienceCallbacks:
    solve_route_a_mode: Callable[[Any], tuple[dict[str, Any], list[dict[str, Any]]]]
    solve_route_u_ladder: Callable[..., tuple[list[dict[str, Any]], dict[str, Any]]]
    solve_ap_node: Callable[[Mapping[str, Any]], dict[str, Any]]
    run_external_records: Callable[[Path], list[dict[str, Any]]]


def default_science_callbacks() -> ScienceCallbacks:
    return ScienceCallbacks(
        cycle2.solve_route_a_mode,
        original.solve_route_u_ladder,
        cycle2.solve_ap_node,
        cycle2.run_external_records,
    )


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_identity(path: Path, *, include_inode: bool = True) -> dict[str, Any]:
    info = path.lstat()
    if path.is_symlink() or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ResumeContractError(f"unsafe resume file: {path}")
    result: dict[str, Any] = {
        "sha256": _sha256(path),
        "size": info.st_size,
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
    }
    if include_inode:
        result.update({"device": info.st_dev, "inode": info.st_ino})
    return result


def _strict_pairs(pairs: Sequence[tuple[str, Any]], where: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ResumeContractError(f"duplicate JSON key {key!r}: {where}")
        result[key] = value
    return result


def strict_json_bytes(payload: bytes, *, where: str) -> Any:
    try:
        return json.loads(
            payload,
            object_pairs_hook=lambda pairs: _strict_pairs(pairs, where),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ResumeContractError(f"invalid JSON: {where}") from exc


def strict_json(path: Path) -> Any:
    return strict_json_bytes(path.read_bytes(), where=str(path))


def strict_jsonl_prefix(
    path: Path, *, permit_partial_tail: bool = False
) -> tuple[list[Any], bytes]:
    payload = path.read_bytes()
    if not payload:
        return [], b""
    complete_end = payload.rfind(b"\n") + 1
    tail = payload[complete_end:]
    if tail and not permit_partial_tail:
        raise ResumeContractError(f"torn JSONL record: {path}")
    records: list[Any] = []
    for ordinal, line in enumerate(payload[:complete_end].splitlines(), 1):
        if not line:
            raise ResumeContractError(f"blank JSONL record: {path}:{ordinal}")
        records.append(strict_json_bytes(line, where=f"{path}:{ordinal}"))
    return records, tail


def _checkpoint_inventory(
    root: Path, count: int, *, allow_later: bool = False
) -> tuple[dict[str, Any], str]:
    checkpoint_root = root / "mode_checkpoints"
    expected_names = [f"route_a_{ordinal:04d}.json" for ordinal in range(count)]
    actual = sorted(path.name for path in checkpoint_root.glob("route_a_*.json"))
    if (not allow_later and actual != expected_names) or (
        allow_later and actual[:count] != expected_names
    ):
        raise ResumeContractError("Route-A checkpoint gap, duplicate, or extra file")
    inventory = build_mode_inventory()
    mapping: dict[str, Any] = {}
    for ordinal, name in enumerate(expected_names):
        path = checkpoint_root / name
        expected = {
            "schema": "schwo.phase6.v3_1_u.route_a_checkpoint.v1",
            "ordinal": ordinal,
            "mode": inventory[ordinal].payload(),
            "status": "COMPUTED_NOT_ACCEPTED",
            "node_count": 20,
        }
        if strict_json(path) != expected:
            raise ResumeContractError(f"Route-A checkpoint payload mismatch: {ordinal}")
        mapping[f"mode_checkpoints/{name}"] = _file_identity(path, include_inode=False)
    compact = json.dumps(
        mapping, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return mapping, _sha256_bytes(compact)


def _pending_suffix_is_authenticated(root: Path, path: Path) -> bool:
    actual = path.read_bytes()
    control = root / "resume_control"
    if not control.is_dir():
        return False
    for prepared_path in sorted(control.glob("attempt_*/transactions/*/prepared.json")):
        transaction = prepared_path.parent
        recovered = any(
            candidate.exists()
            for candidate in control.glob(
                "attempt_*/recovered_transactions/"
                f"{transaction.parent.parent.name}__{transaction.name}/commit.json"
            )
        )
        if (transaction / "commit.json").exists() or recovered:
            continue
        prepared = strict_json(prepared_path)
        for target in prepared["targets"]:
            if Path(target["path"]).resolve() != path.resolve():
                continue
            block = _decode_target(target)
            pre_size = int(target["pre_size"])
            if (
                len(actual) >= pre_size
                and _sha256_bytes(actual[:pre_size]) == target["pre_sha256"]
                and len(actual) - pre_size <= len(block)
                and block[: len(actual) - pre_size] == actual[pre_size:]
            ):
                return True
    return False


def verify_controller_gate() -> dict[str, Any]:
    package = strict_json(PACKAGE_PATH)
    fixed: dict[Path, str] = {
        PACKAGE_PATH: PACKAGE_SHA256,
        DESIGN_PATH: DESIGN_SHA256,
        PROMPT_PATH: PROMPT_SHA256,
        PACKAGE_APPROVAL_PATH: PACKAGE_APPROVAL_SHA256,
    }
    fixed.update(
        {ROOT / path: digest for path, digest in package["source_bindings"].items()}
    )
    fixed.update(
        {
            ROOT / path: digest
            for path, digest in package["protected_radial_identities"].items()
        }
    )
    identities: dict[str, Any] = {}
    for path, digest in fixed.items():
        if _sha256(path) != digest:
            raise ResumeContractError(f"frozen resume source drift: {path}")
        identities[str(path)] = _file_identity(path)
    approval = PACKAGE_APPROVAL_PATH.read_text()
    for token in (
        "ADVANCE_DECISION: ADVANCE",
        "CLAIM_STATUS: NOT_ASSESSED",
        "ACCEPT GREEN / V3.1-U RESUME-CONTROLLER REPAIR PACKAGE READY FOR T4",
        PACKAGE_SHA256,
    ):
        if token not in approval:
            raise ResumeContractError("formal resume package approval mismatch")
    return {"package": package, "identities": identities}


def _validate_original_contract(root: Path, *, logical_root: Path) -> None:
    contract = strict_json(root / "run_contract.json")
    source_start = strict_json(root / "source_start.json")
    package = strict_json(PACKAGE_PATH)
    bound = package["source_bindings"]
    for name in ("run_contract.json", "source_start.json", "inventory.json"):
        expected_sha = bound[str(logical_root.relative_to(ROOT) / name)]
        if _sha256(root / name) != expected_sha:
            raise ResumeContractError(f"original {name} byte identity mismatch")
    if (
        contract.get("schema") != "schwo.phase6.v3_1_u.run_contract.v1"
        or contract.get("gate_id") != PARENT_GATE_ID
        or contract.get("artifact_rev") != 1
        or Path(contract.get("official_root", "")).resolve() != logical_root.resolve()
        or contract.get("counts") != original.EXPECTED_FIXED_COUNTS
        or contract.get("resume_policy")
        != "verified system interruption with exact contiguous prefix only"
        or contract.get("predecessor_science_reused") is not False
        or contract.get("source_start_sha256")
        != _sha256_bytes(canonical_bytes(source_start))
        or strict_json(root / "inventory.json") != build_inventory_payload()
    ):
        raise ResumeContractError("original run/source/inventory contract mismatch")
    live = original.build_source_ledger(original.verify_start_gate())
    if source_start != live:
        raise ResumeContractError(
            "original source_start no longer matches live sources"
        )


def _validate_resume_runtime(root: Path, authority: Authority) -> None:
    contract = strict_json(root / "run_contract.json")
    expected_argv = [
        str(CLI_PATH.resolve(strict=True)),
        "resume",
        "--root",
        str(root.resolve(strict=True)),
        "--implementation-approval",
        str(authority.implementation_approval.resolve(strict=True)),
        "--implementation-approval-sha256",
        authority.implementation_approval_sha256,
        "--dispatch",
        str(authority.dispatch.resolve(strict=True)),
        "--dispatch-sha256",
        authority.dispatch_sha256,
    ]
    if (
        Path(sys.executable).resolve() != Path(contract["executable"]).resolve()
        or Path.cwd().resolve() != Path(contract["cwd"]).resolve()
        or sys.version_info[:2] != (3, 14)
        or os.environ.get("PYTHONDONTWRITEBYTECODE") != "1"
        or [str(Path(sys.argv[0]).resolve()), *sys.argv[1:]] != expected_argv
    ):
        raise ResumeContractError(
            "resume executable/runtime/cwd/argv identity mismatch"
        )


def _validate_mode_prefix(
    root: Path,
    records: Sequence[Mapping[str, Any]],
    ladders: Sequence[Mapping[str, Any]],
) -> None:
    inventory = build_mode_inventory()
    if len(records) > len(inventory) or len(ladders) != 20 * len(records):
        raise ResumeContractError("Route-A prefix cardinality mismatch")
    for ordinal, (mode, key) in enumerate(zip(records, inventory, strict=False)):
        expected = key.payload()
        if (
            mode.get("mode") != expected
            or mode.get("node_count") != 20
            or mode.get("protected_call_count") != 20
        ):
            raise ResumeContractError(f"Route-A mode mismatch at ordinal {ordinal}")
        group = ladders[20 * ordinal : 20 * (ordinal + 1)]
        if [item.get("mode") for item in group] != [expected] * 20:
            raise ResumeContractError(f"Route-A ladder key mismatch at {ordinal}")
        if [item.get("node") for item in group] != cycle2.route_a_node_graph(key):
            raise ResumeContractError(f"Route-A ladder graph mismatch at {ordinal}")
        if mode.get("metrics") != cycle2.route_a_mode_metrics(group):
            raise ResumeContractError(f"Route-A metrics mismatch at {ordinal}")
        selected = [
            item["result"]
            for item in group
            if cycle2._node_tuple(item["node"]) == (1e-10, 1, 160, 1e-10, 1e-12)
        ]
        if len(selected) != 1 or mode.get("baseline") != selected[0]:
            raise ResumeContractError(f"Route-A baseline mismatch at {ordinal}")


def _process_liveness(root: Path) -> dict[str, Any]:
    root_text = str(root.resolve())
    own_pid = os.getpid()
    process = subprocess.run(
        ["ps", "ax", "-o", "pid=,ppid=,pgid=,state=,command="],
        capture_output=True,
        text=True,
        check=True,
    )
    related = []
    resume_name = CLI_PATH.name
    original_name = "phase6_v3_1_hp_unitarity.py"
    for line in process.stdout.splitlines():
        try:
            pid_text, remainder = line.strip().split(None, 1)
            pid = int(pid_text)
            command = remainder.split(None, 3)[-1]
            tokens = shlex.split(command)
        except (ValueError, IndexError):
            raise ResumeContractError("malformed related-process row") from None
        if pid == own_pid or root_text not in tokens:
            continue
        executable = Path(tokens[0]).name if tokens else ""
        launched = (
            tokens[1]
            if executable.startswith("python") and len(tokens) > 1
            else (tokens[0] if tokens else "")
        )
        is_resume_writer = Path(launched).name == resume_name and "resume" in tokens
        is_original_writer = (
            Path(launched).name == original_name
            and "--output-root" in tokens
            and root_text in tokens
        )
        if is_resume_writer or is_original_writer:
            related.append(line.strip())
    files = [
        root / ".writer.lock",
        root / "records.jsonl",
        root / "ladder_records.jsonl",
    ]
    lsof = subprocess.run(
        ["lsof", "-n", "-P", "-F", "pfa", "--", *(str(path) for path in files)],
        capture_output=True,
        text=True,
        check=False,
    )
    open_pids: set[int] = set()
    current_pid: int | None = None
    current_fd: str | None = None
    for row in lsof.stdout.splitlines():
        if row.startswith("p") and row[1:].isdigit():
            current_pid = int(row[1:])
            current_fd = None
        elif row.startswith("f"):
            current_fd = row[1:]
        elif row.startswith("a") and current_pid not in (None, own_pid):
            if current_fd is None:
                raise ResumeContractError("malformed lsof access row")
            if row[1:] in {"w", "u"}:
                open_pids.add(current_pid)
    writable_open_pids = sorted(open_pids)
    return {
        "schema": "schwo.phase6.v3_1_u.resume_liveness.v1",
        "checked_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exact_root": root_text,
        "related_process_rows": related,
        "other_open_writer_pids": writable_open_pids,
        "read_only_observers_excluded": True,
        "active_writer": bool(related or writable_open_pids),
    }


def inspect_interrupted_root(
    root: Path,
    *,
    logical_root: Path = REAL_ROOT,
    check_liveness: bool = True,
) -> dict[str, Any]:
    """Strictly read and validate a resumable prefix; never opens the flock."""

    physical = root.resolve(strict=True)
    if physical.is_symlink() or not physical.is_dir():
        raise ResumeContractError("unsafe resume root")
    gate = verify_controller_gate()
    _validate_original_contract(physical, logical_root=logical_root)
    for forbidden in (
        "failure.json",
        "failure_manifest.json",
        "failed_evaluation.json",
        "manifest.json",
    ):
        if (physical / forbidden).exists():
            raise ResumeContractError(
                f"terminal/nonresumable artifact present: {forbidden}"
            )
    lock = _file_identity(physical / ".writer.lock")
    expected_lock = gate["package"]["interrupted_root"]["writer_lock"]
    if not (physical / "resume_control").exists():
        lock_keys = ("sha256", "size", "mode", "nlink")
        if any(lock[key] != expected_lock[key] for key in lock_keys):
            raise ResumeContractError("stable original lock identity mismatch")
        if physical == logical_root.resolve() and any(
            lock[key] != expected_lock[key] for key in ("device", "inode")
        ):
            raise ResumeContractError("stable original lock inode/device mismatch")
    else:
        exclusions = sorted(
            (physical / "resume_control").glob("attempt_*/writer_exclusion.json")
        )
        first_exclusion = (
            strict_json(exclusions[0])["identity"] if exclusions else expected_lock
        )
        terminal_lock = (
            stat.S_IMODE(physical.stat().st_mode) == 0o555 and lock["mode"] == 0o444
        )
        comparable = {key: value for key, value in lock.items() if key != "mode"}
        expected_comparable = {
            key: value for key, value in first_exclusion.items() if key != "mode"
        }
        if comparable != expected_comparable or (
            not terminal_lock and lock["mode"] != first_exclusion["mode"]
        ):
            raise ResumeContractError(
                "stable writer lock identity changed across attempts"
            )
    records, records_tail = strict_jsonl_prefix(
        physical / "records.jsonl", permit_partial_tail=True
    )
    ladders, ladders_tail = strict_jsonl_prefix(
        physical / "ladder_records.jsonl", permit_partial_tail=True
    )
    checkpoint_count = len(
        tuple((physical / "mode_checkpoints").glob("route_a_*.json"))
    )
    if len(records) not in (checkpoint_count, checkpoint_count + 1):
        raise ResumeContractError("Route-A records/checkpoint cardinality mismatch")
    if not 20 * checkpoint_count <= len(ladders) <= 20 * (checkpoint_count + 1):
        raise ResumeContractError("Route-A ladder/checkpoint cardinality mismatch")
    pending_records = bool(records_tail or len(records) > checkpoint_count)
    pending_ladders = bool(ladders_tail or len(ladders) > 20 * checkpoint_count)
    if pending_records and not _pending_suffix_is_authenticated(
        physical, physical / "records.jsonl"
    ):
        raise ResumeContractError("unauthenticated Route-A records suffix")
    if pending_ladders and not _pending_suffix_is_authenticated(
        physical, physical / "ladder_records.jsonl"
    ):
        raise ResumeContractError("unauthenticated Route-A ladder suffix")
    _validate_mode_prefix(
        physical,
        records[:checkpoint_count],
        ladders[: 20 * checkpoint_count],
    )
    checkpoints, checkpoint_digest = _checkpoint_inventory(physical, checkpoint_count)
    if checkpoint_count == ORIGINAL_PREFIX_MODE_COUNT and not (
        pending_records or pending_ladders
    ):
        if (
            len(ladders) != ORIGINAL_PREFIX_LADDER_COUNT
            or _sha256(physical / "records.jsonl") != ORIGINAL_PREFIX_RECORDS_SHA256
            or _sha256(physical / "ladder_records.jsonl")
            != ORIGINAL_PREFIX_LADDERS_SHA256
            or (physical / "records.jsonl").stat().st_size
            != ORIGINAL_PREFIX_RECORDS_SIZE
            or (physical / "ladder_records.jsonl").stat().st_size
            != ORIGINAL_PREFIX_LADDERS_SIZE
            or checkpoint_digest != CHECKPOINT_INVENTORY_SHA256
        ):
            raise ResumeContractError("frozen interrupted prefix identity mismatch")
    if checkpoint_count < ORIGINAL_PREFIX_MODE_COUNT:
        raise ResumeContractError("Route-A prefix predates the frozen interruption")
    _validate_resume_control_prefix(physical, checkpoint_count)
    liveness = (
        _process_liveness(physical) if check_liveness else {"active_writer": False}
    )
    if liveness["active_writer"]:
        raise ResumeContractError("active or ambiguous writer exists")
    inventory = build_mode_inventory()
    next_mode = (
        inventory[checkpoint_count].payload()
        if checkpoint_count < len(inventory)
        else None
    )
    state = PrefixState(
        checkpoint_count,
        20 * checkpoint_count,
        checkpoint_count,
        _sha256(physical / "records.jsonl"),
        _sha256(physical / "ladder_records.jsonl"),
        (physical / "records.jsonl").stat().st_size,
        (physical / "ladder_records.jsonl").stat().st_size,
        next_mode,
        checkpoint_digest,
    )
    return {
        "schema": "schwo.phase6.v3_1_u.resume_inspection.v1",
        "gate_id": GATE_ID,
        "physical_root": str(physical),
        "logical_root": str(logical_root.resolve()),
        "prefix": state.__dict__,
        "checkpoint_inventory": checkpoints,
        "lock_identity": lock,
        "liveness": liveness,
        "controller_gate": gate["identities"],
        "mutations": 0,
        "science_calls": 0,
    }


def _rename_exclusive(source: Path, target: Path) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    function = getattr(libc, "renamex_np", None)
    if function is None:
        raise ResumeContractError("Darwin renamex_np(RENAME_EXCL) unavailable")
    function.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
    function.restype = ctypes.c_int
    if function(os.fsencode(source), os.fsencode(target), RENAME_EXCL) != 0:
        error = ctypes.get_errno()
        raise FileExistsError(error, os.strerror(error), str(target))


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_publish(
    path: Path,
    payload: bytes,
    *,
    staging_token: str,
    hook: FaultHook | None = None,
) -> dict[str, Any]:
    """Publish complete bytes under an absent final name with renamex_np."""

    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.parent.is_symlink() or not path.parent.is_dir():
        raise ResumeContractError(f"unsafe atomic-publication directory: {path.parent}")
    staging = path.parent / f".{path.name}.staging.{staging_token}"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(staging, flags, 0o600)
    try:
        if hook:
            hook("after_staging_create", path, 0)
        view = memoryview(payload)
        written = 0
        while written < len(view):
            count = os.write(fd, view[written:])
            if count <= 0:
                raise ResumeContractError("short atomic staging write")
            written += count
            if hook:
                hook("during_staging_write", path, written)
        os.fsync(fd)
        os.fchmod(fd, 0o444)
        os.fsync(fd)
        if hook:
            hook("after_staging_fsync", path, written)
    finally:
        os.close(fd)
    if hook:
        hook("before_atomic_rename", path, len(payload))
    _rename_exclusive(staging, path)
    if hook:
        hook("after_atomic_rename", path, len(payload))
    _fsync_directory(path.parent)
    return _file_identity(path)


def append_authenticated_tail(
    path: Path,
    *,
    pre_size: int,
    pre_sha256: str,
    block: bytes,
    expected_identity: Mapping[str, Any] | None = None,
    hook: FaultHook | None = None,
) -> dict[str, Any]:
    """Complete only a byte-identical missing tail of a prepared append block."""

    before = path.read_bytes()
    if len(before) < pre_size or _sha256_bytes(before[:pre_size]) != pre_sha256:
        raise ResumeContractError(f"authenticated preappend prefix mismatch: {path}")
    suffix = before[pre_size:]
    if len(suffix) > len(block) or block[: len(suffix)] != suffix:
        raise ResumeContractError(f"unknown or mismatched append suffix: {path}")
    if expected_identity:
        identity = _file_identity(path)
        for key in ("device", "inode", "mode", "nlink"):
            if identity[key] != expected_identity[key]:
                raise ResumeContractError(f"preappend file identity drift: {path}")
    missing = block[len(suffix) :]
    flags = os.O_WRONLY | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        offset = 0
        while offset < len(missing):
            count = os.write(fd, missing[offset : offset + 1])
            if count != 1:
                raise ResumeContractError("short O_APPEND write")
            offset += 1
            if hook:
                hook("after_append_byte", path, len(suffix) + offset)
        os.fsync(fd)
    finally:
        os.close(fd)
    final = path.read_bytes()
    if final != before[:pre_size] + block:
        raise ResumeContractError(f"postappend block mismatch: {path}")
    return _file_identity(path)


@contextmanager
def stable_writer_exclusion(
    root: Path,
    *,
    terminalize_after_authority: bool = False,
    hook: FaultHook | None = None,
) -> Iterator[tuple[int, dict[str, Any]]]:
    path = root / ".writer.lock"
    identity = _file_identity(path)
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ResumeContractError("stable writer lock is live") from exc
        if _file_identity(path) != identity:
            raise ResumeContractError("stable writer lock changed during acquisition")
        try:
            yield fd, identity
        except Exception as exc:
            if terminalize_after_authority and any(
                (root / "resume_control").glob("attempt_*/authority_commit.json")
            ):
                _terminalize_resume_failure(root, exc, hook=hook)
            raise
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def _write_full(fd: int, payload: bytes) -> None:
    view = memoryview(payload)
    offset = 0
    while offset < len(view):
        count = os.write(fd, view[offset:])
        if count <= 0:
            raise ResumeContractError("short write")
        offset += count


def _authority_text(path: Path, digest: str, required: Sequence[str]) -> dict[str, Any]:
    if _sha256(path) != digest:
        raise ResumeContractError(f"authority hash mismatch: {path}")
    text = path.read_text()
    if any(token not in text for token in required):
        raise ResumeContractError(f"authority content mismatch: {path}")
    return _file_identity(path)


def implementation_hashes() -> dict[str, str]:
    paths = (CONTROLLER_PATH, CLI_PATH, UNIT_TEST_PATH, REGRESSION_TEST_PATH)
    return {str(path): _sha256(path) for path in paths}


def _prior_authority_chain(
    root: Path, *, before_attempt: int | None = None
) -> dict[str, Any]:
    control = root / "resume_control"
    attempts: list[dict[str, Any]] = []
    if control.exists():
        if control.is_symlink() or not control.is_dir():
            raise ResumeContractError("unsafe resume authority-chain root")
        paths = sorted(control.glob("attempt_[0-9][0-9][0-9][0-9]"))
        if before_attempt is not None:
            paths = paths[: before_attempt - 1]
        for ordinal, attempt in enumerate(paths, 1):
            if attempt.name != f"attempt_{ordinal:04d}":
                raise ResumeContractError("nonmonotone prior authority chain")
            files = {}
            for path in sorted(attempt.rglob("*")):
                if path.is_symlink():
                    raise ResumeContractError("symlink in prior authority chain")
                if path.is_file():
                    identity = _file_identity(path, include_inode=False)
                    files[str(path.relative_to(attempt))] = {
                        key: identity[key] for key in ("sha256", "size", "nlink")
                    }
            authority_path = attempt / "resume_authority.json"
            authority_dispatch = None
            if authority_path.exists():
                payload = strict_json(authority_path)
                authority_dispatch = payload.get("authorities", {}).get("dispatch")
            attempts.append(
                {
                    "attempt": ordinal,
                    "classification": "COMMITTED_AUTHORITY"
                    if (attempt / "authority_commit.json").exists()
                    else "ABANDONED_PRE_SCIENCE",
                    "authority_dispatch": authority_dispatch,
                    "files": files,
                }
            )
    payload = {
        "schema": "schwo.phase6.v3_1_u.prior_authority_chain.v1",
        "attempts": attempts,
    }
    return {
        "payload": payload,
        "sha256": _sha256_bytes(canonical_bytes(payload)),
        "next_attempt": len(attempts) + 1,
    }


def build_dispatch_payload(
    root: Path,
    *,
    implementation_approval: Path,
    implementation_approval_sha256: str,
    authorized_at_utc: str,
    check_liveness: bool = True,
) -> dict[str, Any]:
    """Build the exact one-use dispatch object without mutating the root."""

    root = root.resolve(strict=True)
    inspection = inspect_interrupted_root(
        root, logical_root=REAL_ROOT, check_liveness=check_liveness
    )
    chain = _prior_authority_chain(root)
    return {
        "schema": "schwo.phase6.v3_1_u.resume_dispatch.v1",
        "gate_id": GATE_ID,
        "single_use": True,
        "exact_root": str(root),
        "next_attempt": chain["next_attempt"],
        "prefix": inspection["prefix"],
        "stable_lock_identity": inspection["lock_identity"],
        "prior_authority_chain_sha256": chain["sha256"],
        "implementation_approval": {
            "path": str(implementation_approval.resolve(strict=True)),
            "sha256": implementation_approval_sha256,
        },
        "implementation_hashes": implementation_hashes(),
        "authorized_at_utc": authorized_at_utc,
    }


def validate_authorities(
    authority: Authority,
    root: Path,
    inspection: Mapping[str, Any],
) -> dict[str, Any]:
    hashes = implementation_hashes()
    approval_required = [
        "ADVANCE_DECISION: ADVANCE",
        "CLAIM_STATUS: NOT_ASSESSED",
        "V3.1-U RESUME-CONTROLLER",
        PACKAGE_SHA256,
        *hashes.values(),
    ]
    approval_identity = _authority_text(
        authority.implementation_approval,
        authority.implementation_approval_sha256,
        approval_required,
    )
    if _sha256(authority.dispatch) != authority.dispatch_sha256:
        raise ResumeContractError("dispatch authority hash mismatch")
    dispatch = strict_json(authority.dispatch)
    chain = _prior_authority_chain(root)
    expected_keys = {
        "schema",
        "gate_id",
        "single_use",
        "exact_root",
        "next_attempt",
        "prefix",
        "stable_lock_identity",
        "prior_authority_chain_sha256",
        "implementation_approval",
        "implementation_hashes",
        "authorized_at_utc",
    }
    if (
        set(dispatch) != expected_keys
        or dispatch["schema"] != "schwo.phase6.v3_1_u.resume_dispatch.v1"
        or dispatch["gate_id"] != GATE_ID
        or dispatch["single_use"] is not True
        or Path(dispatch["exact_root"]).resolve() != root.resolve()
        or dispatch["next_attempt"] != chain["next_attempt"]
        or dispatch["prefix"] != inspection["prefix"]
        or dispatch["stable_lock_identity"] != inspection["lock_identity"]
        or dispatch["prior_authority_chain_sha256"] != chain["sha256"]
        or dispatch["implementation_approval"]
        != {
            "path": str(authority.implementation_approval.resolve(strict=True)),
            "sha256": authority.implementation_approval_sha256,
        }
        or dispatch["implementation_hashes"] != hashes
        or not isinstance(dispatch["authorized_at_utc"], str)
        or not dispatch["authorized_at_utc"].endswith("Z")
    ):
        raise ResumeContractError("one-use dispatch binding mismatch")
    dispatch_identity = _file_identity(authority.dispatch)
    for attempt in chain["payload"]["attempts"]:
        used = attempt["authority_dispatch"]
        if used is not None and used.get("sha256") == dispatch_identity["sha256"]:
            raise ResumeContractError("one-use dispatch authority was already consumed")
    return {
        "implementation_approval": approval_identity,
        "dispatch": dispatch_identity,
        "dispatch_binding": dispatch,
        "prior_authority_chain": chain,
        "implementation_hashes": hashes,
    }


def _next_attempt(root: Path) -> tuple[Path, int, list[dict[str, Any]]]:
    control = root / "resume_control"
    control.mkdir(mode=0o700, exist_ok=True)
    if control.is_symlink() or not control.is_dir():
        raise ResumeContractError("unsafe resume_control directory")
    existing = sorted(path for path in control.glob("attempt_[0-9][0-9][0-9][0-9]"))
    adjudications: list[dict[str, Any]] = []
    for expected, path in enumerate(existing, 1):
        if path.name != f"attempt_{expected:04d}" or not path.is_dir():
            raise ResumeContractError("resume attempt chain is nonmonotone")
        commit = path / "authority_commit.json"
        files = sorted(item.name for item in path.iterdir() if item.is_file())
        adjudications.append(
            {
                "attempt": expected,
                "authority_committed": commit.exists(),
                "files": files,
                "classification": "COMMITTED_AUTHORITY"
                if commit.exists()
                else "ABANDONED_PRE_SCIENCE",
            }
        )
    ordinal = len(existing) + 1
    attempt = control / f"attempt_{ordinal:04d}"
    attempt.mkdir(mode=0o700)
    _fsync_directory(control)
    return attempt, ordinal, adjudications


def _publish_attempt_authority(
    root: Path,
    inspection: Mapping[str, Any],
    authority: Authority,
    lock_identity: Mapping[str, Any],
    *,
    authority_identities: Mapping[str, Any] | None = None,
    hook: FaultHook | None = None,
) -> tuple[Path, dict[str, Any]]:
    authority_identities = authority_identities or validate_authorities(
        authority, root, inspection
    )
    attempt, ordinal, adjudications = _next_attempt(root)
    if ordinal != authority_identities["dispatch_binding"]["next_attempt"]:
        raise ResumeContractError("dispatch attempt ordinal changed before publication")
    token = f"attempt{ordinal:04d}"
    payloads: list[tuple[str, bytes]] = [
        (
            "attempt_intent.json",
            canonical_bytes(
                {
                    "schema": "schwo.phase6.v3_1_u.resume_attempt_intent.v1",
                    "gate_id": GATE_ID,
                    "attempt": ordinal,
                    "root": str(root.resolve()),
                    "next_ordinal": inspection["prefix"]["next_ordinal"],
                }
            ),
        ),
        ("prelock_liveness.json", canonical_bytes(inspection["liveness"])),
        ("stable_writer_lock_snapshot.bin", (root / ".writer.lock").read_bytes()),
        (
            "writer_exclusion.json",
            canonical_bytes(
                {
                    "schema": "schwo.phase6.v3_1_u.writer_exclusion.v1",
                    "stable_path": str((root / ".writer.lock").resolve()),
                    "identity": lock_identity,
                    "flock_held": True,
                    "stable_path_renamed_or_unlinked": False,
                }
            ),
        ),
        (
            "abandoned_attempt_adjudication.json",
            canonical_bytes(
                {
                    "schema": "schwo.phase6.v3_1_u.abandoned_attempts.v1",
                    "prior_attempts": adjudications,
                }
            ),
        ),
        (
            "resume_authority.json",
            canonical_bytes(
                {
                    "schema": "schwo.phase6.v3_1_u.resume_authority.v1",
                    "gate_id": GATE_ID,
                    "parent_gate_id": PARENT_GATE_ID,
                    "attempt": ordinal,
                    "created_at_utc": datetime.now(UTC)
                    .isoformat()
                    .replace("+00:00", "Z"),
                    "inspection": inspection,
                    "authorities": authority_identities,
                    "original_run_contract": _file_identity(root / "run_contract.json"),
                    "original_source_start": _file_identity(root / "source_start.json"),
                    "original_inventory": _file_identity(root / "inventory.json"),
                    "runtime": {
                        "executable": str(Path(sys.executable).resolve()),
                        "argv": list(sys.argv),
                        "cwd": str(Path.cwd().resolve()),
                    },
                    "predecessor_science_reused": False,
                }
            ),
        ),
        (
            "resume_source_start.json",
            canonical_bytes(
                {
                    "schema": "schwo.phase6.v3_1_u.resume_source_ledger.v1",
                    "controller_sources": {
                        path: _file_identity(Path(path))
                        for path in implementation_hashes()
                    },
                    "package": _file_identity(PACKAGE_PATH),
                    "design": _file_identity(DESIGN_PATH),
                    "prompt": _file_identity(PROMPT_PATH),
                    "package_approval": _file_identity(PACKAGE_APPROVAL_PATH),
                    "implementation_approval": authority_identities[
                        "implementation_approval"
                    ],
                    "dispatch": authority_identities["dispatch"],
                }
            ),
        ),
    ]
    identities: dict[str, Any] = {}
    for name, payload in payloads:
        identities[name] = atomic_publish(
            attempt / name, payload, staging_token=token, hook=hook
        )
    commit = {
        "schema": "schwo.phase6.v3_1_u.resume_authority_commit.v1",
        "attempt": ordinal,
        "authority_files": identities,
        "science_calls_before_commit": 0,
    }
    identities["authority_commit.json"] = atomic_publish(
        attempt / "authority_commit.json",
        canonical_bytes(commit),
        staging_token=token,
        hook=hook,
    )
    return attempt, identities


def _encode_target(
    path: Path, block: bytes, *, hook: FaultHook | None = None
) -> dict[str, Any]:
    before = path.read_bytes() if path.exists() else b""
    if not path.exists():
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags, 0o600)
        os.fsync(fd)
        os.close(fd)
        _fsync_directory(path.parent)
        if hook:
            hook("after_empty_target_creation", path, 0)
    identity = _file_identity(path)
    return {
        "path": str(path),
        "pre_size": len(before),
        "pre_sha256": _sha256_bytes(before),
        "file_identity": {
            key: identity[key] for key in ("device", "inode", "mode", "nlink")
        },
        "block_sha256": _sha256_bytes(block),
        "block_size": len(block),
        "block_base64": base64.b64encode(block).decode("ascii"),
    }


def _decode_target(target: Mapping[str, Any]) -> bytes:
    block = base64.b64decode(target["block_base64"], validate=True)
    if (
        len(block) != target["block_size"]
        or _sha256_bytes(block) != target["block_sha256"]
    ):
        raise ResumeContractError("prepared block identity mismatch")
    return block


def execute_prepared_transaction(
    prepared_path: Path,
    *,
    checkpoint_path: Path | None,
    commit_path: Path,
    token: str,
    hook: FaultHook | None = None,
) -> None:
    prepared = strict_json(prepared_path)
    for target in prepared["targets"]:
        append_authenticated_tail(
            Path(target["path"]),
            pre_size=target["pre_size"],
            pre_sha256=target["pre_sha256"],
            block=_decode_target(target),
            expected_identity=target["file_identity"],
            hook=hook,
        )
    if checkpoint_path is not None:
        checkpoint = base64.b64decode(prepared["checkpoint_base64"], validate=True)
        if _sha256_bytes(checkpoint) != prepared["checkpoint_sha256"]:
            raise ResumeContractError("prepared checkpoint identity mismatch")
        if not checkpoint_path.exists():
            atomic_publish(checkpoint_path, checkpoint, staging_token=token, hook=hook)
        elif checkpoint_path.read_bytes() != checkpoint:
            raise ResumeContractError("existing checkpoint differs from prepared bytes")
        _fsync_directory(checkpoint_path.parent)
    commit_payload = canonical_bytes(
        {
            "schema": "schwo.phase6.v3_1_u.transaction_commit.v1",
            "prepared": _file_identity(prepared_path),
            "targets": [
                _file_identity(Path(target["path"])) for target in prepared["targets"]
            ],
            "checkpoint": _file_identity(checkpoint_path)
            if checkpoint_path is not None
            else None,
        }
    )
    if not commit_path.exists():
        atomic_publish(commit_path, commit_payload, staging_token=token, hook=hook)
    elif commit_path.read_bytes() != commit_payload:
        raise ResumeContractError("transaction commit drift")


def _transaction(
    attempt: Path,
    *,
    stage: str,
    ordinal: int,
    input_payload: Mapping[str, Any],
    solve: Callable[[], tuple[list[tuple[Path, bytes]], bytes | None]],
    checkpoint_path: Path | None,
    authority_commit: Path,
    hook: FaultHook | None,
) -> None:
    transaction = attempt / "transactions" / f"{stage}_{ordinal:04d}"
    transaction.mkdir(mode=0o700, parents=True)
    token = f"{attempt.name}.{stage}.{ordinal:04d}"
    logical_solver_call_ordinals = (
        list(range(20 * ordinal, 20 * (ordinal + 1)))
        if stage == "route_a"
        else [ordinal]
    )
    intent = {
        "schema": "schwo.phase6.v3_1_u.transaction_intent.v1",
        "stage": stage,
        "ordinal": ordinal,
        "input": dict(input_payload),
        "logical_solver_call_ordinals": logical_solver_call_ordinals,
        "authority_commit": _file_identity(authority_commit),
    }
    atomic_publish(
        transaction / "intent.json",
        canonical_bytes(intent),
        staging_token=token,
        hook=hook,
    )
    targets, checkpoint = solve()
    encoded = [_encode_target(path, block, hook=hook) for path, block in targets]
    prepared: dict[str, Any] = {
        "schema": "schwo.phase6.v3_1_u.prepared_transaction.v1",
        "stage": stage,
        "ordinal": ordinal,
        "intent": _file_identity(transaction / "intent.json"),
        "targets": encoded,
        "checkpoint_sha256": _sha256_bytes(checkpoint) if checkpoint else None,
        "checkpoint_base64": base64.b64encode(checkpoint).decode("ascii")
        if checkpoint
        else None,
    }
    prepared_path = transaction / "prepared.json"
    if hook:
        hook("before_prepared_publication", prepared_path, 0)
    atomic_publish(
        prepared_path, canonical_bytes(prepared), staging_token=token, hook=hook
    )
    execute_prepared_transaction(
        prepared_path,
        checkpoint_path=checkpoint_path,
        commit_path=transaction / "commit.json",
        token=token,
        hook=hook,
    )


def _recover_prepared(root: Path, attempt: Path, *, hook: FaultHook | None) -> None:
    for old_attempt in sorted((root / "resume_control").glob("attempt_[0-9]*")):
        if old_attempt == attempt:
            continue
        for transaction in sorted((old_attempt / "transactions").glob("*")):
            prepared = transaction / "prepared.json"
            commit = transaction / "commit.json"
            if prepared.exists() and not commit.exists():
                payload = strict_json(prepared)
                checkpoint = payload.get("checkpoint_base64")
                checkpoint_path = None
                if checkpoint:
                    stage = payload["stage"]
                    prefix = "route_a" if stage == "route_a" else stage
                    checkpoint_ordinal = int(payload["ordinal"])
                    if stage == "route_u":
                        intent = strict_json(transaction / "intent.json")
                        checkpoint_ordinal = int(intent["input"]["ordinal"])
                    checkpoint_path = (
                        root
                        / "mode_checkpoints"
                        / f"{prefix}_{checkpoint_ordinal:04d}.json"
                    )
                recovered = (
                    attempt
                    / "recovered_transactions"
                    / f"{old_attempt.name}__{transaction.name}"
                )
                recovered.mkdir(mode=0o700, parents=True)
                execute_prepared_transaction(
                    prepared,
                    checkpoint_path=checkpoint_path,
                    commit_path=recovered / "commit.json",
                    token=f"{attempt.name}.recover.{transaction.name}",
                    hook=hook,
                )


def _create_empty_jsonl(path: Path) -> None:
    if path.exists():
        return
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    _fsync_directory(path.parent)


def _jsonl_block(records: Sequence[Mapping[str, Any]]) -> bytes:
    return b"".join(cycle2.compact_jsonl_record(item) for item in records)


def _committed_transaction_exists(root: Path, stage: str, ordinal: int) -> bool:
    control = root / "resume_control"
    matches = []
    for attempt in sorted(control.glob("attempt_[0-9][0-9][0-9][0-9]")):
        transaction = attempt / "transactions" / f"{stage}_{ordinal:04d}"
        if transaction.exists():
            matches.append(
                _transaction_commit_path(control, attempt, transaction) is not None
            )
    if sum(matches) > 1:
        raise ResumeContractError("duplicate or ambiguous committed transaction")
    return sum(matches) == 1


def _verify_original_prefix_ranges(root: Path) -> None:
    records = (root / "records.jsonl").read_bytes()
    ladders = (root / "ladder_records.jsonl").read_bytes()
    if (
        _sha256_bytes(records[:ORIGINAL_PREFIX_RECORDS_SIZE])
        != ORIGINAL_PREFIX_RECORDS_SHA256
        or _sha256_bytes(ladders[:ORIGINAL_PREFIX_LADDERS_SIZE])
        != ORIGINAL_PREFIX_LADDERS_SHA256
    ):
        raise ResumeContractError("original science prefix bytes changed")


def _resume_source_ledger(attempt: Path, authority: Authority) -> dict[str, Any]:
    del attempt
    return {
        "schema": "schwo.phase6.v3_1_u.resume_source_ledger.v1",
        "controller_sources": {
            path: _file_identity(Path(path)) for path in implementation_hashes()
        },
        "package": _file_identity(PACKAGE_PATH),
        "design": _file_identity(DESIGN_PATH),
        "prompt": _file_identity(PROMPT_PATH),
        "package_approval": _file_identity(PACKAGE_APPROVAL_PATH),
        "implementation_approval": _file_identity(authority.implementation_approval),
        "dispatch": _file_identity(authority.dispatch),
    }


def remaining_route_a_ordinals(prefix_count: int) -> tuple[int, ...]:
    """Return the frozen suffix plan without inspecting any scientific value."""

    if not 0 <= prefix_count <= 496:
        raise ResumeContractError("Route-A prefix count is outside the frozen domain")
    return tuple(range(prefix_count, 496))


def _resume_root_active(
    root: Path,
    authority: Authority,
    *,
    logical_root: Path,
    callbacks: ScienceCallbacks | None = None,
    hook: FaultHook | None = None,
) -> dict[str, Any]:
    """Resume a reviewed interrupted root under a committed one-use authority."""

    root = root.resolve(strict=True)
    inspection = inspect_interrupted_root(root, logical_root=logical_root)
    _validate_resume_runtime(root, authority)
    authority_identities = validate_authorities(authority, root, inspection)
    callbacks = callbacks or default_science_callbacks()
    with stable_writer_exclusion(root, terminalize_after_authority=True, hook=hook) as (
        _lock_fd,
        lock_identity,
    ):
        liveness = _process_liveness(root)
        if liveness["active_writer"]:
            raise ResumeContractError("writer appeared under stable flock")
        attempt, _authority_files = _publish_attempt_authority(
            root,
            inspection,
            authority,
            lock_identity,
            authority_identities=authority_identities,
            hook=hook,
        )
        authority_commit = attempt / "authority_commit.json"
        _recover_prepared(root, attempt, hook=hook)
        current = inspect_interrupted_root(root, check_liveness=False)["prefix"][
            "next_ordinal"
        ]
        inventory = build_mode_inventory()
        for ordinal in remaining_route_a_ordinals(current):
            key = inventory[ordinal]

            def solve_a(key: Any = key, ordinal: int = ordinal):
                mode, ladders = callbacks.solve_route_a_mode(key)
                checkpoint = canonical_bytes(
                    {
                        "schema": "schwo.phase6.v3_1_u.route_a_checkpoint.v1",
                        "ordinal": ordinal,
                        "mode": key.payload(),
                        "status": "COMPUTED_NOT_ACCEPTED",
                        "node_count": 20,
                    }
                )
                return [
                    (root / "ladder_records.jsonl", _jsonl_block(ladders)),
                    (root / "records.jsonl", cycle2.compact_jsonl_record(mode)),
                ], checkpoint

            _transaction(
                attempt,
                stage="route_a",
                ordinal=ordinal,
                input_payload=key.payload(),
                solve=solve_a,
                checkpoint_path=root
                / "mode_checkpoints"
                / f"route_a_{ordinal:04d}.json",
                authority_commit=authority_commit,
                hook=hook,
            )
            _verify_original_prefix_ranges(root)

        modes, tail = strict_jsonl_prefix(root / "records.jsonl")
        if tail or len(modes) != 496:
            raise ResumeContractError("Route A is incomplete before route-map freeze")
        selector_views = [
            original.selector_view(
                mode,
                ordinal=ordinal,
                record_sha256=_sha256_bytes(cycle2.compact_jsonl_record(mode)),
            )
            for ordinal, mode in enumerate(modes)
        ]
        route_map = original.build_route_map(selector_views)
        if not (root / "unitarity_route_map.json").exists():
            atomic_publish(
                root / "unitarity_route_map.json",
                canonical_bytes(route_map),
                staging_token=f"{attempt.name}.route_map",
                hook=hook,
            )
        original.validate_route_map(strict_json(root / "unitarity_route_map.json"))
        route_map_identity = _file_identity(root / "unitarity_route_map.json")

        _create_empty_jsonl(root / "route_u_records.jsonl")
        _create_empty_jsonl(root / "route_u_ladders.jsonl")
        done_u, _ = strict_jsonl_prefix(root / "route_u_ladders.jsonl")
        selected = [
            entry for entry in route_map["entries"] if entry["selector"]["use_route_u"]
        ]
        for selected_ordinal, entry in enumerate(selected[len(done_u) :], len(done_u)):

            def solve_u(entry: Mapping[str, Any] = entry):
                records, admission = callbacks.solve_route_u_ladder(
                    entry, route_map_sha256=route_map_identity["sha256"]
                )
                checkpoint = canonical_bytes(
                    {
                        "schema": "schwo.phase6.v3_1_u.route_u_checkpoint.v1",
                        "ordinal": entry["ordinal"],
                        "mode": entry["mode"],
                        "status": "COMPUTED_NOT_ACCEPTED",
                        "route_map_sha256": route_map_identity["sha256"],
                        "precision_schedule": admission["precision_schedule"],
                    }
                )
                return [
                    (root / "route_u_records.jsonl", _jsonl_block(records)),
                    (
                        root / "route_u_ladders.jsonl",
                        cycle2.compact_jsonl_record(admission),
                    ),
                ], checkpoint

            _transaction(
                attempt,
                stage="route_u",
                ordinal=selected_ordinal,
                input_payload=entry,
                solve=solve_u,
                checkpoint_path=root
                / "mode_checkpoints"
                / f"route_u_{entry['ordinal']:04d}.json",
                authority_commit=authority_commit,
                hook=hook,
            )

        _create_empty_jsonl(root / "ap_records.jsonl")
        done_b, _ = strict_jsonl_prefix(root / "ap_records.jsonl")
        plan = cycle2.ap_node_plan()
        for ordinal, node in enumerate(plan[len(done_b) :], len(done_b)):

            def solve_b(node: Mapping[str, Any] = node):
                record = callbacks.solve_ap_node(node)
                checkpoint = canonical_bytes(
                    {
                        "schema": "schwo.phase6.v3_1_u.route_b_checkpoint.v1",
                        "ordinal": ordinal,
                        "node": node,
                        "status": "COMPUTED_NOT_ACCEPTED",
                    }
                )
                return [
                    (root / "ap_records.jsonl", cycle2.compact_jsonl_record(record))
                ], checkpoint

            _transaction(
                attempt,
                stage="route_b",
                ordinal=ordinal,
                input_payload=node,
                solve=solve_b,
                checkpoint_path=root
                / "mode_checkpoints"
                / f"route_b_{ordinal:04d}.json",
                authority_commit=authority_commit,
                hook=hook,
            )

        _validate_resume_control_prefix(root, 496)
        if not _committed_transaction_exists(root, "route_c", 0):

            def solve_c():
                raw_stage = attempt / "external_raw.science_staging.json"
                records_c = callbacks.run_external_records(raw_stage)
                if len(records_c) != 23:
                    raise ResumeContractError("Route-C record count mismatch")
                return [
                    (root / "external_records.jsonl", _jsonl_block(records_c)),
                    (root / "external_raw.json", raw_stage.read_bytes()),
                ], None

            _transaction(
                attempt,
                stage="route_c",
                ordinal=0,
                input_payload={"record_count": 23},
                solve=solve_c,
                checkpoint_path=None,
                authority_commit=authority_commit,
                hook=hook,
            )

        ladders, _ = strict_jsonl_prefix(root / "ladder_records.jsonl")
        u_records, _ = strict_jsonl_prefix(root / "route_u_records.jsonl")
        u_ladders, _ = strict_jsonl_prefix(root / "route_u_ladders.jsonl")
        ap_records, _ = strict_jsonl_prefix(root / "ap_records.jsonl")
        external_records, _ = strict_jsonl_prefix(root / "external_records.jsonl")
        evaluation = original.evaluate_all_thresholds(
            modes,
            ladders,
            route_map,
            u_records,
            u_ladders,
            ap_records,
            external_records,
        )
        if not evaluation["all_pass"]:
            atomic_publish(
                root / "failed_evaluation.json",
                canonical_bytes(evaluation),
                staging_token=f"{attempt.name}.failed_evaluation",
                hook=hook,
            )
            raise ResumeContractError("official V3.1-U threshold/certificate failure")
        original_source_start = strict_json(root / "source_start.json")
        original_source_end = original.build_source_ledger(original.verify_start_gate())
        if original_source_start != original_source_end:
            raise ResumeContractError("original source identity drift during resume")
        atomic_publish(
            root / "source_map.json",
            canonical_bytes(
                {"start": original_source_start, "end": original_source_end}
            ),
            staging_token=f"{attempt.name}.source_map",
            hook=hook,
        )
        resume_start = strict_json(attempt / "resume_source_start.json")
        resume_end = _resume_source_ledger(attempt, authority)
        if resume_start != resume_end:
            raise ResumeContractError("resume source identity drift")
        atomic_publish(
            root / "resume_source_map.json",
            canonical_bytes({"start": resume_start, "end": resume_end}),
            staging_token=f"{attempt.name}.resume_source_map",
            hook=hook,
        )
        attempts = sorted((root / "resume_control").glob("attempt_[0-9]*"))
        atomic_publish(
            root / "resume_authority_index.json",
            canonical_bytes(
                {
                    "schema": "schwo.phase6.v3_1_u.resume_authority_index.v1",
                    "attempts": [
                        {
                            "attempt": path.name,
                            "classification": "COMMITTED_AUTHORITY"
                            if (path / "authority_commit.json").exists()
                            else "ABANDONED_PRE_SCIENCE",
                            "authority_commit": _file_identity(
                                path / "authority_commit.json"
                            )
                            if (path / "authority_commit.json").exists()
                            else None,
                        }
                        for path in attempts
                    ],
                }
            ),
            staging_token=f"{attempt.name}.authority_index",
            hook=hook,
        )
        for name, payload in (
            ("uncertainty_budget.json", evaluation["uncertainty_budget"]),
            ("summary.json", evaluation["summary"]),
            (
                "report.json",
                {
                    "schema": "schwo.phase6.v3_1_u.report.v1",
                    "gate_id": original.GATE_ID,
                    "terminal": True,
                    "candidate_success": True,
                    "global_status": None,
                    "global_green_permitted": False,
                    "independent_review_state": "NOT_ASSESSED",
                    "resumed_under": GATE_ID,
                },
            ),
        ):
            atomic_publish(
                root / name,
                canonical_bytes(payload),
                staging_token=f"{attempt.name}.{name}",
                hook=hook,
            )
        _verify_original_prefix_ranges(root)
        os.chmod(root / ".writer.lock", 0o444)
        original._seal_tree(root)
        os.chmod(root, 0o755)
        manifest = original.build_manifest(root, overall_state="PASS")
        atomic_publish(
            root / "manifest.json",
            canonical_bytes(manifest),
            staging_token=f"{attempt.name}.manifest",
            hook=hook,
        )
        os.chmod(root, 0o555)
        original.validate_official_candidate(root, validate_live_sources=True)
        validate_resumed_candidate(root, authority=authority)
        return {"root": str(root), "evaluation": evaluation, "attempt": attempt.name}


def _terminalize_resume_failure(
    root: Path, exc: Exception, *, hook: FaultHook | None = None
) -> None:
    committed = sorted(
        (root / "resume_control").glob("attempt_*/authority_commit.json")
    )
    if not committed or (root / "failure.json").exists():
        return
    latest = committed[-1].parent
    if hook:
        hook("failure_flock_held", root / "failure.json", 0)
    if stat.S_IMODE(root.stat().st_mode) != 0o755:
        os.chmod(root, 0o755)
        _fsync_directory(root.parent)
    failure = {
        "schema": "schwo.phase6.v3_1_u.resume_failure.v1",
        "gate_id": GATE_ID,
        "parent_gate_id": PARENT_GATE_ID,
        "attempt": latest.name,
        "exception_type": type(exc).__name__,
        "exception_message": str(exc),
        "scientific_pass": False,
        "resumable": False,
        "stable_writer_lock_retained": True,
    }
    atomic_publish(
        root / "failure.json",
        canonical_bytes(failure),
        staging_token=f"{latest.name}.failure",
    )
    os.chmod(root / ".writer.lock", 0o444)
    original._seal_tree(root)
    os.chmod(root, 0o755)
    atomic_publish(
        root / "failure_manifest.json",
        canonical_bytes(original.build_manifest(root, overall_state="FAILED")),
        staging_token=f"{latest.name}.failure_manifest",
    )
    os.chmod(root, 0o555)
    if hook:
        hook("failure_root_sealed_under_flock", root / "failure_manifest.json", 0)


def _resume_root(
    root: Path,
    authority: Authority,
    *,
    logical_root: Path,
    callbacks: ScienceCallbacks | None = None,
    hook: FaultHook | None = None,
) -> dict[str, Any]:
    return _resume_root_active(
        root,
        authority,
        logical_root=logical_root,
        callbacks=callbacks,
        hook=hook,
    )


def resume_root(
    root: Path,
    authority: Authority,
    *,
    callbacks: ScienceCallbacks | None = None,
    hook: FaultHook | None = None,
) -> dict[str, Any]:
    """Production entry point, restricted to the exact interrupted root."""

    resolved = root.resolve(strict=True)
    if resolved != REAL_ROOT.resolve():
        raise ResumeContractError(
            "official resume may target only the exact interrupted root"
        )
    return _resume_root(
        resolved,
        authority,
        logical_root=REAL_ROOT,
        callbacks=callbacks,
        hook=hook,
    )


def _canonical_jsonl_block(block: bytes, *, where: str) -> list[Mapping[str, Any]]:
    if block and not block.endswith(b"\n"):
        raise ResumeContractError(f"prepared JSONL block is torn: {where}")
    records: list[Mapping[str, Any]] = []
    for ordinal, line in enumerate(block.splitlines(), 1):
        record = strict_json_bytes(line, where=f"{where}:{ordinal}")
        if not isinstance(record, dict):
            raise ResumeContractError(
                f"prepared JSONL record is not an object: {where}"
            )
        if cycle2.compact_jsonl_record(record) != line + b"\n":
            raise ResumeContractError(f"prepared JSONL record is noncanonical: {where}")
        records.append(record)
    return records


def _transaction_commit_path(
    control: Path, source_attempt: Path, transaction: Path
) -> Path | None:
    direct = transaction / "commit.json"
    recovered = sorted(
        control.glob(
            "attempt_*/recovered_transactions/"
            f"{source_attempt.name}__{transaction.name}/commit.json"
        )
    )
    candidates = ([direct] if direct.exists() else []) + recovered
    if len(candidates) > 1:
        raise ResumeContractError("duplicate transaction commit/recovery")
    return candidates[0] if candidates else None


def _validate_prepared_transaction(
    root: Path,
    control: Path,
    attempt: Path,
    transaction: Path,
) -> dict[str, Any]:
    intent_path = transaction / "intent.json"
    prepared_path = transaction / "prepared.json"
    expected_staging = {
        f".intent.json.staging.{attempt.name}.{transaction.name[:-5]}."
        f"{transaction.name[-4:]}",
        f".prepared.json.staging.{attempt.name}.{transaction.name[:-5]}."
        f"{transaction.name[-4:]}",
        f".commit.json.staging.{attempt.name}.{transaction.name[:-5]}."
        f"{transaction.name[-4:]}",
    }
    allowed = {"intent.json", "prepared.json", "commit.json"}
    for path in transaction.iterdir():
        if path.is_symlink() or path.is_dir():
            raise ResumeContractError("unsafe or extra transaction control path")
        if path.name not in allowed and path.name not in expected_staging:
            raise ResumeContractError("unknown transaction control file")
    if (transaction / "commit.json").exists() and any(
        path.name.startswith(".") for path in transaction.iterdir()
    ):
        raise ResumeContractError("committed transaction retains staging fragment")
    if not intent_path.exists():
        raise ResumeContractError("transaction directory lacks atomic intent")
    if not prepared_path.exists():
        # A final intent with no prepared bytes is an authenticated recalculation point.
        return {
            "stage": transaction.name.rsplit("_", 1)[0],
            "ordinal": int(transaction.name[-4:]),
            "state": "INTENT_ONLY",
            "targets": [],
            "attempt": attempt.name,
        }
    intent = strict_json(intent_path)
    prepared = strict_json(prepared_path)
    if set(intent) != {
        "schema",
        "stage",
        "ordinal",
        "input",
        "logical_solver_call_ordinals",
        "authority_commit",
    } or set(prepared) != {
        "schema",
        "stage",
        "ordinal",
        "intent",
        "targets",
        "checkpoint_sha256",
        "checkpoint_base64",
    }:
        raise ResumeContractError("transaction intent/prepared schema mismatch")
    stage = intent["stage"]
    ordinal = intent["ordinal"]
    if (
        intent["schema"] != "schwo.phase6.v3_1_u.transaction_intent.v1"
        or prepared["schema"] != "schwo.phase6.v3_1_u.prepared_transaction.v1"
        or stage not in {"route_a", "route_u", "route_b", "route_c"}
        or not isinstance(ordinal, int)
        or ordinal < 0
        or prepared["stage"] != stage
        or prepared["ordinal"] != ordinal
        or transaction.name != f"{stage}_{ordinal:04d}"
        or prepared["intent"] != _file_identity(intent_path)
        or intent["authority_commit"]
        != _file_identity(attempt / "authority_commit.json")
    ):
        raise ResumeContractError("transaction identity/order mismatch")
    expected_calls = (
        list(range(20 * ordinal, 20 * (ordinal + 1)))
        if stage == "route_a"
        else [ordinal]
    )
    if intent["logical_solver_call_ordinals"] != expected_calls:
        raise ResumeContractError("transaction logical solver-call ordinal mismatch")
    if stage == "route_a":
        inventory = build_mode_inventory()
        if ordinal >= len(inventory) or intent["input"] != inventory[ordinal].payload():
            raise ResumeContractError("Route-A transaction input mismatch")
    target_names = {
        "route_a": ["ladder_records.jsonl", "records.jsonl"],
        "route_u": ["route_u_records.jsonl", "route_u_ladders.jsonl"],
        "route_b": ["ap_records.jsonl"],
        "route_c": ["external_records.jsonl", "external_raw.json"],
    }[stage]
    targets = prepared["targets"]
    if not isinstance(targets, list) or len(targets) != len(target_names):
        raise ResumeContractError("prepared target inventory mismatch")
    expected_commit_targets: list[dict[str, Any]] = []
    target_chain: list[dict[str, Any]] = []
    all_blocks_complete = True
    for target, name in zip(targets, target_names, strict=True):
        if set(target) != {
            "path",
            "pre_size",
            "pre_sha256",
            "file_identity",
            "block_sha256",
            "block_size",
            "block_base64",
        }:
            raise ResumeContractError("prepared target schema mismatch")
        path = Path(target["path"])
        if path.resolve(strict=True) != (root / name).resolve(strict=True):
            raise ResumeContractError("prepared target escaped frozen root geometry")
        file_identity = target["file_identity"]
        if set(file_identity) != {"device", "inode", "mode", "nlink"}:
            raise ResumeContractError("prepared preappend identity schema mismatch")
        live_identity = _file_identity(path)
        if (
            any(
                live_identity[key] != file_identity[key]
                for key in ("device", "inode", "nlink")
            )
            or file_identity["mode"] != 0o600
        ):
            raise ResumeContractError("prepared target inode/link/mode drift")
        block = _decode_target(target)
        actual = path.read_bytes()
        pre_size = target["pre_size"]
        if (
            not isinstance(pre_size, int)
            or pre_size < 0
            or len(actual) < pre_size
            or _sha256_bytes(actual[:pre_size]) != target["pre_sha256"]
        ):
            raise ResumeContractError("prepared target preappend prefix mismatch")
        suffix = actual[pre_size : pre_size + len(block)]
        if suffix != block[: len(suffix)] or len(suffix) > len(block):
            raise ResumeContractError("prepared target suffix mismatch")
        block_complete = len(suffix) == len(block)
        all_blocks_complete &= block_complete
        if name.endswith(".jsonl"):
            records = _canonical_jsonl_block(block, where=str(prepared_path))
            expected_counts = {
                ("route_a", "ladder_records.jsonl"): 20,
                ("route_a", "records.jsonl"): 1,
                ("route_u", "route_u_records.jsonl"): 3,
                ("route_u", "route_u_ladders.jsonl"): 1,
                ("route_b", "ap_records.jsonl"): 1,
                ("route_c", "external_records.jsonl"): 23,
            }
            if len(records) != expected_counts[(stage, name)]:
                raise ResumeContractError("prepared JSONL record count mismatch")
        end_size = pre_size + len(block)
        expected_commit_targets.append(
            {
                "sha256": _sha256_bytes(actual[:pre_size] + block),
                "size": end_size,
                "mode": file_identity["mode"],
                "nlink": file_identity["nlink"],
                "device": file_identity["device"],
                "inode": file_identity["inode"],
            }
        )
        target_chain.append(
            {
                "name": name,
                "pre_size": pre_size,
                "pre_sha256": target["pre_sha256"],
                "end_size": end_size,
                "end_sha256": _sha256_bytes(actual[:pre_size] + block),
                "block_size": len(block),
                "block_sha256": target["block_sha256"],
            }
        )
    checkpoint_path: Path | None = None
    checkpoint_identity = None
    if prepared["checkpoint_base64"] is not None:
        checkpoint = base64.b64decode(prepared["checkpoint_base64"], validate=True)
        if _sha256_bytes(checkpoint) != prepared["checkpoint_sha256"]:
            raise ResumeContractError("prepared checkpoint bytes mismatch")
        checkpoint_prefix = "route_a" if stage == "route_a" else stage
        checkpoint_ordinal = (
            int(intent["input"]["ordinal"]) if stage == "route_u" else ordinal
        )
        checkpoint_path = (
            root
            / "mode_checkpoints"
            / f"{checkpoint_prefix}_{checkpoint_ordinal:04d}.json"
        )
        if checkpoint_path.exists():
            if checkpoint_path.read_bytes() != checkpoint:
                raise ResumeContractError("published checkpoint differs from prepared")
            checkpoint_identity = _file_identity(checkpoint_path)
    elif prepared["checkpoint_sha256"] is not None or stage != "route_c":
        raise ResumeContractError("prepared checkpoint schema mismatch")
    commit_path = _transaction_commit_path(control, attempt, transaction)
    if commit_path is None:
        return {
            "stage": stage,
            "ordinal": ordinal,
            "state": "PREPARED",
            "targets": target_chain,
            "attempt": attempt.name,
        }
    if not all_blocks_complete or (
        checkpoint_path is not None and not checkpoint_path.exists()
    ):
        raise ResumeContractError(
            "transaction committed before data/checkpoint closure"
        )
    commit = strict_json(commit_path)
    expected_commit = {
        "schema": "schwo.phase6.v3_1_u.transaction_commit.v1",
        "prepared": _file_identity(prepared_path),
        "targets": expected_commit_targets,
        "checkpoint": checkpoint_identity,
    }
    if commit != expected_commit:
        raise ResumeContractError("transaction commit reconstruction mismatch")
    return {
        "stage": stage,
        "ordinal": ordinal,
        "state": "COMMITTED",
        "targets": target_chain,
        "attempt": attempt.name,
    }


def _validate_formal_target_chains(
    root: Path, transactions: Sequence[Mapping[str, Any]]
) -> None:
    empty_sha = _sha256_bytes(b"")
    current: dict[str, tuple[int, str]] = {
        "records.jsonl": (
            ORIGINAL_PREFIX_RECORDS_SIZE,
            ORIGINAL_PREFIX_RECORDS_SHA256,
        ),
        "ladder_records.jsonl": (
            ORIGINAL_PREFIX_LADDERS_SIZE,
            ORIGINAL_PREFIX_LADDERS_SHA256,
        ),
        "route_u_records.jsonl": (0, empty_sha),
        "route_u_ladders.jsonl": (0, empty_sha),
        "ap_records.jsonl": (0, empty_sha),
        "external_records.jsonl": (0, empty_sha),
        "external_raw.json": (0, empty_sha),
    }
    stage_rank = {"route_a": 0, "route_u": 1, "route_b": 2, "route_c": 3}
    prepared = [item for item in transactions if item["state"] != "INTENT_ONLY"]
    prepared.sort(key=lambda item: (stage_rank[item["stage"]], item["ordinal"]))
    seen: set[tuple[str, int]] = set()
    unresolved_by_name: dict[str, Mapping[str, Any]] = {}
    for item in prepared:
        key = (item["stage"], item["ordinal"])
        if key in seen:
            raise ResumeContractError("duplicate prepared transaction key")
        seen.add(key)
        for target in item["targets"]:
            name = target["name"]
            if name in unresolved_by_name:
                raise ResumeContractError(
                    "transaction follows unresolved target suffix"
                )
            if (target["pre_size"], target["pre_sha256"]) != current[name]:
                raise ResumeContractError("formal target append chain is discontinuous")
            if item["state"] == "COMMITTED":
                current[name] = (target["end_size"], target["end_sha256"])
            else:
                unresolved_by_name[name] = target
    for name, expected in current.items():
        path = root / name
        if not path.exists():
            if expected != (0, empty_sha) or name in unresolved_by_name:
                raise ResumeContractError("formal target missing from append chain")
            continue
        identity = _file_identity(path)
        if name in unresolved_by_name:
            target = unresolved_by_name[name]
            if not target["pre_size"] <= identity["size"] <= target["end_size"]:
                raise ResumeContractError("unresolved formal target size mismatch")
        elif (identity["size"], identity["sha256"]) != expected:
            raise ResumeContractError(
                "formal target has unauthenticated trailing bytes"
            )


_AUTHORITY_FILE_ORDER = (
    "attempt_intent.json",
    "prelock_liveness.json",
    "stable_writer_lock_snapshot.bin",
    "writer_exclusion.json",
    "abandoned_attempt_adjudication.json",
    "resume_authority.json",
    "resume_source_start.json",
)


def _validate_utc(value: Any, where: str) -> None:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ResumeContractError(f"invalid UTC timestamp: {where}")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ResumeContractError(f"invalid UTC timestamp: {where}") from exc
    if parsed.tzinfo != UTC:
        raise ResumeContractError(f"non-UTC timestamp: {where}")


def _reconstruct_prior_adjudication(root: Path, attempt_ordinal: int) -> dict[str, Any]:
    prior = []
    for ordinal in range(1, attempt_ordinal):
        path = root / "resume_control" / f"attempt_{ordinal:04d}"
        committed = (path / "authority_commit.json").exists()
        prior.append(
            {
                "attempt": ordinal,
                "authority_committed": committed,
                "files": sorted(item.name for item in path.iterdir() if item.is_file()),
                "classification": "COMMITTED_AUTHORITY"
                if committed
                else "ABANDONED_PRE_SCIENCE",
            }
        )
    return {
        "schema": "schwo.phase6.v3_1_u.abandoned_attempts.v1",
        "prior_attempts": prior,
    }


def _validate_attempt_control_inventory(
    root: Path, attempt: Path, ordinal: int
) -> tuple[str, ...]:
    finals = tuple(name for name in _AUTHORITY_FILE_ORDER if (attempt / name).exists())
    allowed_files = set(finals)
    if (attempt / "authority_commit.json").exists():
        allowed_files.add("authority_commit.json")
    if (attempt / "external_raw.science_staging.json").exists():
        if not (attempt / "transactions/route_c_0000/intent.json").exists():
            raise ResumeContractError("unbound Route-C science staging file")
        allowed_files.add("external_raw.science_staging.json")
    unknown = []
    for path in attempt.iterdir():
        if path.is_symlink():
            raise ResumeContractError("symlink in attempt control inventory")
        if path.is_file() and path.name not in allowed_files:
            unknown.append(path.name)
        elif path.is_dir() and path.name not in {
            "transactions",
            "recovered_transactions",
        }:
            raise ResumeContractError("unknown attempt-level control directory")
    if finals != _AUTHORITY_FILE_ORDER[: len(finals)]:
        raise ResumeContractError("authority files are not a contiguous prefix")
    committed = (attempt / "authority_commit.json").exists()
    if committed and len(finals) != len(_AUTHORITY_FILE_ORDER):
        raise ResumeContractError("authority commit lacks complete authority prefix")
    expected_staging = None
    if not committed and len(finals) < len(_AUTHORITY_FILE_ORDER):
        expected_staging = (
            f".{_AUTHORITY_FILE_ORDER[len(finals)]}.staging.attempt{ordinal:04d}"
        )
    if unknown not in ([], [expected_staging]):
        raise ResumeContractError("unknown attempt-level control file")
    if committed and unknown:
        raise ResumeContractError("committed attempt retains authority staging")
    terminal = stat.S_IMODE(root.stat().st_mode) == 0o555
    for name in allowed_files:
        path = attempt / name
        identity = _file_identity(path)
        allowed_modes = (
            {0o444, 0o600, 0o644}
            if name == "external_raw.science_staging.json"
            else {0o444}
        )
        if identity["nlink"] != 1 or identity["mode"] not in allowed_modes:
            raise ResumeContractError("attempt control file identity mismatch")
    if unknown:
        staging_identity = _file_identity(attempt / unknown[0])
        if staging_identity["nlink"] != 1 or staging_identity["mode"] != (
            0o444 if terminal else 0o600
        ):
            raise ResumeContractError("authority staging identity mismatch")
    return finals


def _authority_paths_from_runtime(
    runtime: Mapping[str, Any], root: Path
) -> tuple[Path, str, Path, str]:
    if set(runtime) != {"executable", "argv", "cwd"}:
        raise ResumeContractError("resume runtime schema mismatch")
    argv = runtime["argv"]
    if not isinstance(argv, list) or len(argv) != 12:
        raise ResumeContractError("resume authority argv shape mismatch")
    if (
        Path(argv[0]).resolve() != CLI_PATH.resolve()
        or tuple(argv[index] for index in (1, 2, 4, 6, 8, 10))
        != (
            "resume",
            "--root",
            "--implementation-approval",
            "--implementation-approval-sha256",
            "--dispatch",
            "--dispatch-sha256",
        )
        or Path(argv[3]).resolve() != root.resolve()
    ):
        raise ResumeContractError("resume authority argv binding mismatch")
    contract = strict_json(root / "run_contract.json")
    if (
        Path(runtime["executable"]).resolve() != Path(contract["executable"]).resolve()
        or Path(runtime["cwd"]).resolve() != Path(contract["cwd"]).resolve()
    ):
        raise ResumeContractError("resume authority executable/cwd mismatch")
    return Path(argv[5]), argv[7], Path(argv[9]), argv[11]


def _validate_attempt_authority_semantics(
    root: Path, attempt: Path, ordinal: int
) -> None:
    finals = _validate_attempt_control_inventory(root, attempt, ordinal)
    if not finals:
        return
    intent = strict_json(attempt / "attempt_intent.json")
    if (
        set(intent) != {"schema", "gate_id", "attempt", "root", "next_ordinal"}
        or intent["schema"] != "schwo.phase6.v3_1_u.resume_attempt_intent.v1"
        or intent["gate_id"] != GATE_ID
        or intent["attempt"] != ordinal
        or Path(intent["root"]).resolve() != root.resolve()
        or not isinstance(intent["next_ordinal"], int)
        or not ORIGINAL_PREFIX_MODE_COUNT <= intent["next_ordinal"] <= 496
    ):
        raise ResumeContractError("attempt-intent semantic mismatch")
    if "prelock_liveness.json" not in finals:
        return
    liveness = strict_json(attempt / "prelock_liveness.json")
    if (
        set(liveness)
        != {
            "schema",
            "checked_at_utc",
            "exact_root",
            "related_process_rows",
            "other_open_writer_pids",
            "read_only_observers_excluded",
            "active_writer",
        }
        or liveness["schema"] != "schwo.phase6.v3_1_u.resume_liveness.v1"
        or Path(liveness["exact_root"]).resolve() != root.resolve()
        or liveness["related_process_rows"] != []
        or liveness["other_open_writer_pids"] != []
        or liveness["read_only_observers_excluded"] is not True
        or liveness["active_writer"] is not False
    ):
        raise ResumeContractError("prelock-liveness semantic mismatch")
    _validate_utc(liveness["checked_at_utc"], "prelock_liveness")
    if "stable_writer_lock_snapshot.bin" not in finals:
        return
    snapshot = attempt / "stable_writer_lock_snapshot.bin"
    if snapshot.read_bytes() != b"" or _sha256(snapshot) != LOCK_SHA256:
        raise ResumeContractError("stable-lock snapshot mismatch")
    if "writer_exclusion.json" not in finals:
        return
    exclusion = strict_json(attempt / "writer_exclusion.json")
    if (
        set(exclusion)
        != {
            "schema",
            "stable_path",
            "identity",
            "flock_held",
            "stable_path_renamed_or_unlinked",
        }
        or exclusion["schema"] != "schwo.phase6.v3_1_u.writer_exclusion.v1"
        or Path(exclusion["stable_path"]).resolve() != (root / ".writer.lock").resolve()
        or exclusion["flock_held"] is not True
        or exclusion["stable_path_renamed_or_unlinked"] is not False
    ):
        raise ResumeContractError("writer-exclusion semantic mismatch")
    historical_lock = exclusion["identity"]
    live_lock = _file_identity(root / ".writer.lock")
    if set(historical_lock) != {"sha256", "size", "mode", "nlink", "device", "inode"}:
        raise ResumeContractError("writer-exclusion identity schema mismatch")
    if historical_lock["mode"] != 0o600 or any(
        historical_lock[key] != live_lock[key]
        for key in ("sha256", "size", "nlink", "device", "inode")
    ):
        raise ResumeContractError("stable writer-lock identity mismatch")
    if "abandoned_attempt_adjudication.json" not in finals:
        return
    if strict_json(attempt / "abandoned_attempt_adjudication.json") != (
        _reconstruct_prior_adjudication(root, ordinal)
    ):
        raise ResumeContractError("prior-attempt adjudication mismatch")
    if "resume_authority.json" not in finals:
        return
    resume_authority = strict_json(attempt / "resume_authority.json")
    expected_keys = {
        "schema",
        "gate_id",
        "parent_gate_id",
        "attempt",
        "created_at_utc",
        "inspection",
        "authorities",
        "original_run_contract",
        "original_source_start",
        "original_inventory",
        "runtime",
        "predecessor_science_reused",
    }
    if (
        set(resume_authority) != expected_keys
        or resume_authority["schema"] != "schwo.phase6.v3_1_u.resume_authority.v1"
        or resume_authority["gate_id"] != GATE_ID
        or resume_authority["parent_gate_id"] != PARENT_GATE_ID
        or resume_authority["attempt"] != ordinal
        or resume_authority["predecessor_science_reused"] is not False
        or resume_authority["original_run_contract"]
        != _file_identity(root / "run_contract.json")
        or resume_authority["original_source_start"]
        != _file_identity(root / "source_start.json")
        or resume_authority["original_inventory"]
        != _file_identity(root / "inventory.json")
    ):
        raise ResumeContractError("resume-authority provenance mismatch")
    _validate_utc(resume_authority["created_at_utc"], "resume_authority")
    inspection = resume_authority["inspection"]
    if (
        not isinstance(inspection, dict)
        or inspection.get("schema") != "schwo.phase6.v3_1_u.resume_inspection.v1"
        or inspection.get("gate_id") != GATE_ID
        or Path(inspection.get("physical_root", "")).resolve() != root.resolve()
        or Path(inspection.get("logical_root", "")).resolve() != REAL_ROOT.resolve()
        or inspection.get("lock_identity") != historical_lock
        or inspection.get("liveness") != liveness
        or inspection.get("mutations") != 0
        or inspection.get("science_calls") != 0
        or inspection.get("controller_gate") != verify_controller_gate()["identities"]
    ):
        raise ResumeContractError("resume-inspection semantic mismatch")
    prefix = inspection.get("prefix", {})
    count = prefix.get("mode_count")
    if not isinstance(count, int) or not ORIGINAL_PREFIX_MODE_COUNT <= count <= 496:
        raise ResumeContractError("resume-inspection prefix count mismatch")
    checkpoints, checkpoint_digest = _checkpoint_inventory(
        root, count, allow_later=True
    )
    inventory = build_mode_inventory()
    expected_next = inventory[count].payload() if count < len(inventory) else None
    if (
        count != intent["next_ordinal"]
        or prefix.get("ladder_count") != 20 * count
        or prefix.get("next_ordinal") != count
        or prefix.get("next_mode") != expected_next
        or prefix.get("checkpoint_inventory_sha256") != checkpoint_digest
        or inspection.get("checkpoint_inventory") != checkpoints
    ):
        raise ResumeContractError("resume-inspection prefix mismatch")
    for label, filename in (
        ("records", "records.jsonl"),
        ("ladders", "ladder_records.jsonl"),
    ):
        size = prefix.get(f"{label}_size")
        digest = prefix.get(f"{label}_sha256")
        live = (root / filename).read_bytes()
        if (
            not isinstance(size, int)
            or size < 0
            or size > len(live)
            or digest != _sha256_bytes(live[:size])
        ):
            raise ResumeContractError(
                "resume-inspection JSONL prefix identity mismatch"
            )
    approval_path, approval_sha, dispatch_path, dispatch_sha = (
        _authority_paths_from_runtime(resume_authority["runtime"], root)
    )
    authorities = resume_authority["authorities"]
    if set(authorities) != {
        "implementation_approval",
        "dispatch",
        "dispatch_binding",
        "prior_authority_chain",
        "implementation_hashes",
    }:
        raise ResumeContractError("resume authority-set schema mismatch")
    hashes = implementation_hashes()
    approval = _authority_text(
        approval_path,
        approval_sha,
        [
            "ADVANCE_DECISION: ADVANCE",
            "CLAIM_STATUS: NOT_ASSESSED",
            "V3.1-U RESUME-CONTROLLER",
            PACKAGE_SHA256,
            *hashes.values(),
        ],
    )
    dispatch_identity = _file_identity(dispatch_path)
    if _sha256(dispatch_path) != dispatch_sha:
        raise ResumeContractError("dispatch source identity mismatch")
    dispatch = strict_json(dispatch_path)
    prior_chain = _prior_authority_chain(root, before_attempt=ordinal)
    if (
        authorities["implementation_approval"] != approval
        or authorities["dispatch"] != dispatch_identity
        or authorities["dispatch_binding"] != dispatch
        or authorities["prior_authority_chain"] != prior_chain
        or authorities["implementation_hashes"] != hashes
        or dispatch.get("next_attempt") != ordinal
        or dispatch.get("prefix") != prefix
        or dispatch.get("stable_lock_identity") != historical_lock
        or dispatch.get("prior_authority_chain_sha256") != prior_chain["sha256"]
        or dispatch.get("implementation_hashes") != hashes
        or dispatch.get("implementation_approval")
        != {"path": str(approval_path.resolve()), "sha256": approval_sha}
        or dispatch.get("single_use") is not True
        or dispatch.get("gate_id") != GATE_ID
        or Path(dispatch.get("exact_root", "")).resolve() != root.resolve()
    ):
        raise ResumeContractError("dispatch/prior-chain semantic mismatch")
    _validate_utc(dispatch.get("authorized_at_utc"), "dispatch")
    if "resume_source_start.json" not in finals:
        return
    source = strict_json(attempt / "resume_source_start.json")
    expected_source = {
        "schema": "schwo.phase6.v3_1_u.resume_source_ledger.v1",
        "controller_sources": {path: _file_identity(Path(path)) for path in hashes},
        "package": _file_identity(PACKAGE_PATH),
        "design": _file_identity(DESIGN_PATH),
        "prompt": _file_identity(PROMPT_PATH),
        "package_approval": _file_identity(PACKAGE_APPROVAL_PATH),
        "implementation_approval": approval,
        "dispatch": dispatch_identity,
    }
    if source != expected_source:
        raise ResumeContractError("resume source-start semantic mismatch")
    commit_path = attempt / "authority_commit.json"
    if not commit_path.exists():
        return
    expected_commit = {
        "schema": "schwo.phase6.v3_1_u.resume_authority_commit.v1",
        "attempt": ordinal,
        "authority_files": {
            name: _file_identity(attempt / name) for name in _AUTHORITY_FILE_ORDER
        },
        "science_calls_before_commit": 0,
    }
    if strict_json(commit_path) != expected_commit:
        raise ResumeContractError("authority-commit reconstruction mismatch")


def _validate_resume_control_prefix(root: Path, route_a_count: int) -> None:
    control = root / "resume_control"
    if not control.exists():
        if route_a_count != ORIGINAL_PREFIX_MODE_COUNT:
            raise ResumeContractError("new Route-A bytes lack resume authority")
        return
    for path in control.iterdir():
        if (
            path.is_symlink()
            or not path.is_dir()
            or len(path.name) != len("attempt_0000")
            or not path.name.startswith("attempt_")
            or not path.name.removeprefix("attempt_").isdigit()
        ):
            raise ResumeContractError("unknown resume-control path")
    attempts = sorted(control.glob("attempt_[0-9][0-9][0-9][0-9]"))
    transactions: list[dict[str, Any]] = []
    for ordinal, attempt in enumerate(attempts, 1):
        if (
            attempt.name != f"attempt_{ordinal:04d}"
            or attempt.is_symlink()
            or not attempt.is_dir()
        ):
            raise ResumeContractError("nonmonotone resume attempt chain")
        _validate_attempt_authority_semantics(root, attempt, ordinal)
        commit = attempt / "authority_commit.json"
        if commit.exists():
            payload = strict_json(commit)
            if (
                set(payload)
                != {
                    "schema",
                    "attempt",
                    "authority_files",
                    "science_calls_before_commit",
                }
                or payload.get("schema")
                != "schwo.phase6.v3_1_u.resume_authority_commit.v1"
                or payload.get("attempt") != ordinal
                or payload.get("science_calls_before_commit") != 0
            ):
                raise ResumeContractError("resume authority commit mismatch")
            expected_authority_names = {
                "attempt_intent.json",
                "prelock_liveness.json",
                "stable_writer_lock_snapshot.bin",
                "writer_exclusion.json",
                "abandoned_attempt_adjudication.json",
                "resume_authority.json",
                "resume_source_start.json",
            }
            if set(payload["authority_files"]) != expected_authority_names:
                raise ResumeContractError("resume authority file inventory mismatch")
            for name, identity in payload["authority_files"].items():
                if _file_identity(attempt / name) != identity:
                    raise ResumeContractError("resume authority file drift")
        elif (attempt / "transactions").exists():
            raise ResumeContractError(
                "science transaction exists before authority commit"
            )
        for transaction in sorted((attempt / "transactions").glob("*")):
            if transaction.is_symlink() or not transaction.is_dir():
                raise ResumeContractError("unsafe transaction path")
            parts = transaction.name.rsplit("_", 1)
            if (
                len(parts) != 2
                or parts[0] not in {"route_a", "route_u", "route_b", "route_c"}
                or len(parts[1]) != 4
                or not parts[1].isdigit()
            ):
                raise ResumeContractError("unknown transaction control directory")
            transactions.append(
                _validate_prepared_transaction(root, control, attempt, transaction)
            )
        recovered_root = attempt / "recovered_transactions"
        if recovered_root.exists():
            for recovered in recovered_root.iterdir():
                if recovered.is_symlink() or not recovered.is_dir():
                    raise ResumeContractError("unsafe recovery control directory")
                pieces = recovered.name.split("__", 1)
                if len(pieces) != 2:
                    raise ResumeContractError("unknown recovery control directory")
                source = control / pieces[0] / "transactions" / pieces[1]
                if not source.is_dir() or not (source / "prepared.json").exists():
                    raise ResumeContractError(
                        "recovery directory lacks source transaction"
                    )
                expected_staging = (
                    f".commit.json.staging.{attempt.name}.recover.{pieces[1]}"
                )
                actual: set[str] = set()
                for path in recovered.iterdir():
                    if path.is_symlink() or path.is_dir():
                        raise ResumeContractError("unsafe recovery control path")
                    actual.add(path.name)
                allowed = {"commit.json", expected_staging}
                if not actual.issubset(allowed) or (
                    "commit.json" in actual and expected_staging in actual
                ):
                    raise ResumeContractError("extra recovery control file")
    committed_transactions = [
        (item["stage"], item["ordinal"])
        for item in transactions
        if item["state"] == "COMMITTED"
    ]
    route_a = [
        ordinal for stage, ordinal in committed_transactions if stage == "route_a"
    ]
    if route_a not in (
        list(range(ORIGINAL_PREFIX_MODE_COUNT, route_a_count)),
        list(range(ORIGINAL_PREFIX_MODE_COUNT, route_a_count + 1)),
    ):
        raise ResumeContractError("Route-A resume transaction sequence mismatch")
    unresolved = [
        item
        for item in transactions
        if item["state"] != "COMMITTED"
        and (item["stage"], item["ordinal"]) not in committed_transactions
    ]
    if len(unresolved) > 1:
        raise ResumeContractError("multiple unresolved science transactions")
    if (root / "manifest.json").exists() and unresolved:
        raise ResumeContractError("terminal candidate contains unresolved transaction")
    for stage in ("route_u", "route_b", "route_c"):
        stage_items = [
            ordinal
            for item_stage, ordinal in committed_transactions
            if item_stage == stage
        ]
        if stage_items and stage_items != list(range(len(stage_items))):
            raise ResumeContractError(f"{stage} transaction sequence mismatch")
    _validate_formal_target_chains(root, transactions)


def validate_resumed_candidate(root: Path, *, authority: Authority) -> None:
    """Read-only additive terminal validator; original validator is mandatory."""

    root = root.resolve(strict=True)
    original.validate_official_candidate(root, validate_live_sources=True)
    if stat.S_IMODE((root / ".writer.lock").stat().st_mode) != 0o444:
        raise ResumeContractError("terminal stable lock mode mismatch")
    _verify_original_prefix_ranges(root)
    _validate_resume_control_prefix(root, 496)
    index = strict_json(root / "resume_authority_index.json")
    attempts = sorted((root / "resume_control").glob("attempt_[0-9]*"))
    latest = attempts[-1]
    latest_authority = strict_json(latest / "resume_authority.json")
    dispatch_identity = _file_identity(authority.dispatch)
    if (
        _sha256(authority.dispatch) != authority.dispatch_sha256
        or latest_authority["authorities"]["dispatch"] != dispatch_identity
        or latest_authority["authorities"]["implementation_approval"]
        != _file_identity(authority.implementation_approval)
        or latest_authority["authorities"]["implementation_hashes"]
        != implementation_hashes()
        or latest_authority["authorities"]["dispatch_binding"]
        != strict_json(authority.dispatch)
    ):
        raise ResumeContractError("terminal consumed authority mismatch")
    uses = sum(
        strict_json(path / "resume_authority.json")["authorities"]["dispatch"].get(
            "sha256"
        )
        == dispatch_identity["sha256"]
        for path in attempts
        if (path / "resume_authority.json").exists()
    )
    if uses != 1:
        raise ResumeContractError("terminal dispatch consumption is not one-use")
    if [item["attempt"] for item in index["attempts"]] != [p.name for p in attempts]:
        raise ResumeContractError("resume authority index mismatch")
    for item, path in zip(index["attempts"], attempts, strict=True):
        commit = path / "authority_commit.json"
        expected = {
            "attempt": path.name,
            "classification": "COMMITTED_AUTHORITY"
            if commit.exists()
            else "ABANDONED_PRE_SCIENCE",
            "authority_commit": _file_identity(commit) if commit.exists() else None,
        }
        if item != expected:
            raise ResumeContractError("indexed authority commit drift")
    source_map = strict_json(root / "resume_source_map.json")
    expected = _resume_source_ledger(latest, authority)
    if source_map != {"start": expected, "end": expected}:
        raise ResumeContractError("resume source map mismatch")
    manifest = strict_json(root / "manifest.json")
    required = {
        ".writer.lock",
        "resume_source_map.json",
        "resume_authority_index.json",
    }
    if not required.issubset(manifest["artifacts"]):
        raise ResumeContractError("terminal manifest omits resume evidence")


__all__ = [
    "Authority",
    "FaultHook",
    "InjectedInterruption",
    "PrefixState",
    "REAL_ROOT",
    "ResumeContractError",
    "ScienceCallbacks",
    "append_authenticated_tail",
    "atomic_publish",
    "default_science_callbacks",
    "implementation_hashes",
    "inspect_interrupted_root",
    "resume_root",
    "remaining_route_a_ordinals",
    "stable_writer_exclusion",
    "validate_resumed_candidate",
    "verify_controller_gate",
]
