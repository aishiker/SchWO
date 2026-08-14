"""Strict producer for the Phase-6 V0 implementation verification report.

The producer consumes four already executed, immutable check reports.  It
does not run tests and accepts no caller-supplied state.  Check states, the
overall V0 state, and every report hash are derived from canonical report
bytes, assertion outcomes, actual counts, and the recorded process exit
status.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shlex
import stat
from typing import Final

from schwgw.validation.phase6_domain import canonical_json_bytes
from schwgw.validation.phase6_release import sha256_bytes


CHECK_REPORT_SCHEMA: Final = "schwgw_phase6_v1_v0_check_report_v1"
VERIFICATION_SCHEMA: Final = "schwgw_phase6_v1_v0_verification_report_v1"
REQUIRED_CHECK_IDS: Final = (
    "full_test_suite",
    "legacy_np_isolation",
    "legacy_pseudoinverse_isolation",
    "stale_production_metadata",
)
CHECK_STATES: Final = ("PARTIAL", "PASS", "FAIL")
ASSERTION_OUTCOMES: Final = ("FAIL", "PASS", "SKIP")
OUTPUT_FILES: Final = frozenset({"verification.json"})
FORMAL_ROOT_MODE: Final = 0o555
FORMAL_FILE_MODE: Final = 0o444

_ID = re.compile(r"[a-z0-9][a-z0-9_.-]{0,95}")
_SHA256 = re.compile(r"[0-9a-f]{64}")


class Phase6V0VerificationError(ValueError):
    """Raised when a check report or immutable V0 root fails closed."""


@dataclass(frozen=True)
class LoadedCheckReport:
    """One validated immutable report and its derived release projection."""

    check_id: str
    raw: bytes
    identity: Mapping[str, object]
    state: str
    command: str
    passed: int
    failed: int
    skipped: int


@dataclass(frozen=True)
class V0VerificationPlan:
    """Deterministic pre-publication plan with no filesystem side effects."""

    verification: Mapping[str, object]
    reports: tuple[LoadedCheckReport, ...]


def _exact(value: object, fields: set[str], label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != fields:
        raise Phase6V0VerificationError(f"{label} schema changed")
    return value


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise Phase6V0VerificationError(f"{label} must be non-empty text")
    return value


def _identifier(value: object, label: str) -> str:
    text = _text(value, label)
    if not _ID.fullmatch(text):
        raise Phase6V0VerificationError(f"{label} is not canonical")
    return text


def _nonnegative_integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise Phase6V0VerificationError(f"{label} must be a nonnegative integer")
    return value


def _path_has_symlink(path: Path) -> bool:
    return any(component.is_symlink() for component in (path, *path.parents))


def _stat_signature(value: os.stat_result) -> tuple[int, ...]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
        value.st_mode,
        value.st_nlink,
    )


def _stable_file_bytes(
    path: Path,
    *,
    required_mode: int | None,
    required_parent_mode: int | None,
) -> tuple[bytes, dict[str, object]]:
    absolute = path.absolute()
    if not absolute.is_absolute() or _path_has_symlink(absolute):
        raise Phase6V0VerificationError(f"file path contains an alias: {absolute}")
    try:
        resolved = absolute.resolve(strict=True)
        before = absolute.lstat()
        parent = absolute.parent.lstat()
    except OSError as exc:
        raise Phase6V0VerificationError(f"cannot inspect file: {absolute}") from exc
    mode = stat.S_IMODE(before.st_mode)
    if (
        resolved != absolute
        or not stat.S_ISREG(before.st_mode)
        or before.st_nlink != 1
        or (required_mode is not None and mode != required_mode)
        or (
            required_parent_mode is not None
            and (
                not stat.S_ISDIR(parent.st_mode)
                or stat.S_IMODE(parent.st_mode) != required_parent_mode
            )
        )
    ):
        raise Phase6V0VerificationError(
            f"file is not a direct immutable nlink1 report/source: {absolute}"
        )
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(absolute, flags)
    try:
        opened_before = os.fstat(descriptor)
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        opened_after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    after = absolute.lstat()
    if not (
        _stat_signature(before)
        == _stat_signature(opened_before)
        == _stat_signature(opened_after)
        == _stat_signature(after)
    ):
        raise Phase6V0VerificationError(f"file changed during stable read: {absolute}")
    raw = b"".join(chunks)
    return raw, {
        "mode": mode,
        "nlink": before.st_nlink,
        "path": str(absolute),
        "sha256": sha256_bytes(raw),
        "size": before.st_size,
    }


def _canonical_object(raw: bytes, label: str) -> Mapping[str, object]:
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise Phase6V0VerificationError(f"{label} is not JSON") from exc
    if not isinstance(payload, Mapping) or canonical_json_bytes(payload) != raw:
        raise Phase6V0VerificationError(f"{label} is not canonical JSON")
    return payload


def _validate_working_directory(value: object) -> str:
    text = _text(value, "check working_directory")
    path = Path(text)
    if not path.is_absolute() or _path_has_symlink(path):
        raise Phase6V0VerificationError(
            "check working_directory must be an absolute direct path"
        )
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise Phase6V0VerificationError(
            "check working_directory is unavailable"
        ) from exc
    if resolved != path or not path.is_dir():
        raise Phase6V0VerificationError(
            "check working_directory must resolve to itself"
        )
    return text


def _validate_source_identity(
    value: object, *, report_path: Path
) -> Mapping[str, object]:
    identity = _exact(
        value,
        {"mode", "nlink", "path", "sha256", "size"},
        "check source identity",
    )
    source_path = Path(_text(identity["path"], "check source path"))
    if not source_path.is_absolute() or source_path == report_path:
        raise Phase6V0VerificationError(
            "check source path must be absolute and external to its report"
        )
    digest = identity["sha256"]
    if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
        raise Phase6V0VerificationError("check source hash is invalid")
    _nonnegative_integer(identity["size"], "check source size")
    _nonnegative_integer(identity["mode"], "check source mode")
    _nonnegative_integer(identity["nlink"], "check source nlink")
    _, actual = _stable_file_bytes(
        source_path,
        required_mode=None,
        required_parent_mode=None,
    )
    if dict(identity) != actual:
        raise Phase6V0VerificationError(f"check source identity drifted: {source_path}")
    return identity


def _validate_check_report_payload(
    payload: object,
    *,
    report_path: Path,
    expected_check_id: str,
    verify_sources: bool,
) -> tuple[str, str, int, int, int]:
    report = _exact(
        payload,
        {
            "schema",
            "check_id",
            "command_argv",
            "working_directory",
            "exit_status",
            "assertions",
            "counts",
            "source_identities",
            "execution_complete",
            "global_green_permitted",
            "li_figure_agreement_primary_gate",
        },
        "V0 check report",
    )
    if (
        report["schema"] != CHECK_REPORT_SCHEMA
        or report["check_id"] != expected_check_id
        or report["execution_complete"] is not True
        or report["global_green_permitted"] is not False
        or report["li_figure_agreement_primary_gate"] is not False
    ):
        raise Phase6V0VerificationError("V0 check report policy/identity changed")
    command_argv = report["command_argv"]
    if (
        not isinstance(command_argv, list)
        or not command_argv
        or any(
            not isinstance(argument, str) or not argument or "\x00" in argument
            for argument in command_argv
        )
    ):
        raise Phase6V0VerificationError("check command_argv is invalid")
    working_directory = _validate_working_directory(report["working_directory"])
    exit_status = report["exit_status"]
    if (
        isinstance(exit_status, bool)
        or not isinstance(exit_status, int)
        or not 0 <= exit_status <= 255
    ):
        raise Phase6V0VerificationError("check exit_status is invalid")
    assertions = report["assertions"]
    if not isinstance(assertions, list) or not assertions:
        raise Phase6V0VerificationError("check assertions are empty")
    assertion_ids: list[str] = []
    outcomes: list[str] = []
    for raw_assertion in assertions:
        assertion = _exact(
            raw_assertion,
            {"assertion_id", "outcome", "detail"},
            "V0 check assertion",
        )
        assertion_ids.append(_identifier(assertion["assertion_id"], "V0 assertion_id"))
        outcome = assertion["outcome"]
        if outcome not in ASSERTION_OUTCOMES:
            raise Phase6V0VerificationError("V0 assertion outcome changed")
        outcomes.append(str(outcome))
        _text(assertion["detail"], "V0 assertion detail")
    if assertion_ids != sorted(set(assertion_ids)):
        raise Phase6V0VerificationError("V0 assertions must be ordered and unique")
    counts = _exact(report["counts"], {"passed", "failed", "skipped"}, "counts")
    passed = _nonnegative_integer(counts["passed"], "check passed count")
    failed = _nonnegative_integer(counts["failed"], "check failed count")
    skipped = _nonnegative_integer(counts["skipped"], "check skipped count")
    expected_counts = Counter(outcomes)
    if (passed, failed, skipped) != (
        expected_counts["PASS"],
        expected_counts["FAIL"],
        expected_counts["SKIP"],
    ):
        raise Phase6V0VerificationError(
            "check counts are not derived from assertion outcomes"
        )
    if (exit_status == 0) != (failed == 0):
        raise Phase6V0VerificationError(
            "check exit_status contradicts failed assertion count"
        )
    source_identities = report["source_identities"]
    if not isinstance(source_identities, list) or not source_identities:
        raise Phase6V0VerificationError("check source identity inventory is empty")
    source_paths: list[str] = []
    for raw_identity in source_identities:
        if verify_sources:
            identity = _validate_source_identity(raw_identity, report_path=report_path)
        else:
            identity = _exact(
                raw_identity,
                {"mode", "nlink", "path", "sha256", "size"},
                "check source identity",
            )
            path = Path(_text(identity["path"], "check source path"))
            if not path.is_absolute() or path == report_path:
                raise Phase6V0VerificationError(
                    "check source path must be absolute and external to its report"
                )
            digest = identity["sha256"]
            if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
                raise Phase6V0VerificationError("check source hash is invalid")
            _nonnegative_integer(identity["size"], "check source size")
            _nonnegative_integer(identity["mode"], "check source mode")
            nlink = _nonnegative_integer(identity["nlink"], "check source nlink")
            if nlink != 1:
                raise Phase6V0VerificationError("check source must record nlink1")
        source_paths.append(str(identity["path"]))
    if source_paths != sorted(set(source_paths)):
        raise Phase6V0VerificationError(
            "check source identities must be ordered and unique"
        )
    state = "FAIL" if failed else ("PASS" if passed else "PARTIAL")
    command = f"cd {shlex.quote(working_directory)} && {shlex.join(command_argv)}"
    return state, command, passed, failed, skipped


def validate_check_report_payload(
    payload: object,
    *,
    report_path: str | Path,
    expected_check_id: str,
    verify_sources: bool = True,
) -> tuple[str, str, int, int, int]:
    """Validate one exact trusted-runner report and derive its state/counts."""

    if expected_check_id not in REQUIRED_CHECK_IDS:
        raise Phase6V0VerificationError("unknown V0 check id")
    path = Path(report_path)
    if not path.is_absolute():
        raise Phase6V0VerificationError("V0 report validation path must be absolute")
    return _validate_check_report_payload(
        payload,
        report_path=path,
        expected_check_id=expected_check_id,
        verify_sources=verify_sources,
    )


def _load_check_report(path: Path, expected_check_id: str) -> LoadedCheckReport:
    absolute = path.absolute()
    raw, identity = _stable_file_bytes(
        absolute,
        required_mode=FORMAL_FILE_MODE,
        required_parent_mode=FORMAL_ROOT_MODE,
    )
    payload = _canonical_object(raw, f"V0 check report {expected_check_id}")
    state, command, passed, failed, skipped = _validate_check_report_payload(
        payload,
        report_path=absolute,
        expected_check_id=expected_check_id,
        verify_sources=True,
    )
    return LoadedCheckReport(
        check_id=expected_check_id,
        raw=raw,
        identity=identity,
        state=state,
        command=command,
        passed=passed,
        failed=failed,
        skipped=skipped,
    )


def _absolute_report_path(value: str | Path, check_id: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        raise Phase6V0VerificationError(
            f"V0 check report path must be absolute: {check_id}"
        )
    return path


def _validate_verification_payload(value: object) -> Mapping[str, object]:
    report = _exact(
        value,
        {
            "schema",
            "verification_id",
            "checks",
            "source_report_sha256s",
            "verification_state",
            "global_green_permitted",
            "li_figure_agreement_primary_gate",
        },
        "V0 verification report",
    )
    if (
        report["schema"] != VERIFICATION_SCHEMA
        or report["global_green_permitted"] is not False
        or report["li_figure_agreement_primary_gate"] is not False
    ):
        raise Phase6V0VerificationError("V0 verification policy changed")
    _identifier(report["verification_id"], "V0 verification_id")
    checks = _exact(report["checks"], set(REQUIRED_CHECK_IDS), "V0 checks")
    states: list[str] = []
    hashes: list[str] = []
    for check_id in REQUIRED_CHECK_IDS:
        check = _exact(
            checks[check_id],
            {"state", "command", "passed", "failed", "skipped", "report_sha256"},
            f"V0 verification check {check_id}",
        )
        state = check["state"]
        if state not in CHECK_STATES:
            raise Phase6V0VerificationError("V0 verification check state changed")
        passed = _nonnegative_integer(check["passed"], "V0 passed count")
        failed = _nonnegative_integer(check["failed"], "V0 failed count")
        _nonnegative_integer(check["skipped"], "V0 skipped count")
        _text(check["command"], "V0 check command")
        digest = check["report_sha256"]
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise Phase6V0VerificationError("V0 check report hash changed")
        derived = "FAIL" if failed else ("PASS" if passed else "PARTIAL")
        if state != derived:
            raise Phase6V0VerificationError("V0 check state is not derived")
        states.append(str(state))
        hashes.append(digest)
    overall = (
        "FAIL"
        if "FAIL" in states
        else ("PASS" if all(state == "PASS" for state in states) else "PARTIAL")
    )
    if report["verification_state"] != overall:
        raise Phase6V0VerificationError("V0 overall state is not derived")
    source_hashes = report["source_report_sha256s"]
    if (
        not isinstance(source_hashes, list)
        or source_hashes != sorted(set(source_hashes))
        or source_hashes != sorted(set(hashes))
        or len(source_hashes) != len(REQUIRED_CHECK_IDS)
    ):
        raise Phase6V0VerificationError("V0 source report hash inventory changed")
    return report


def prepare_v0_verification(
    verification_id: str,
    report_paths: Mapping[str, str | Path],
) -> V0VerificationPlan:
    """Load four immutable reports and derive the exact final V0 payload."""

    identifier = _identifier(verification_id, "V0 verification_id")
    if not isinstance(report_paths, Mapping) or set(report_paths) != set(
        REQUIRED_CHECK_IDS
    ):
        raise Phase6V0VerificationError(
            "V0 report paths must contain exactly the four required check IDs"
        )
    loaded = tuple(
        _load_check_report(
            _absolute_report_path(report_paths[check_id], check_id),
            check_id,
        )
        for check_id in REQUIRED_CHECK_IDS
    )
    report_paths_seen = [str(report.identity["path"]) for report in loaded]
    report_hashes = [str(report.identity["sha256"]) for report in loaded]
    if len(set(report_paths_seen)) != len(loaded) or len(set(report_hashes)) != len(
        loaded
    ):
        raise Phase6V0VerificationError("V0 check reports are duplicated/aliased")
    checks = {
        report.check_id: {
            "state": report.state,
            "command": report.command,
            "passed": report.passed,
            "failed": report.failed,
            "skipped": report.skipped,
            "report_sha256": report.identity["sha256"],
        }
        for report in loaded
    }
    states = [report.state for report in loaded]
    overall = (
        "FAIL"
        if "FAIL" in states
        else ("PASS" if all(state == "PASS" for state in states) else "PARTIAL")
    )
    verification = {
        "schema": VERIFICATION_SCHEMA,
        "verification_id": identifier,
        "checks": checks,
        "source_report_sha256s": sorted(report_hashes),
        "verification_state": overall,
        "global_green_permitted": False,
        "li_figure_agreement_primary_gate": False,
    }
    _validate_verification_payload(verification)
    return V0VerificationPlan(verification=verification, reports=loaded)


def _summary(
    verification: Mapping[str, object],
    *,
    evidence_root: str | None,
    output_written: bool,
) -> dict[str, object]:
    states = Counter(
        str(check["state"])
        for check in verification["checks"].values()
        if isinstance(check, Mapping)
    )
    raw = canonical_json_bytes(verification)
    return {
        "verification_id": verification["verification_id"],
        "verification_state": verification["verification_state"],
        "check_state_counts": {state: states[state] for state in CHECK_STATES},
        "source_report_sha256s": verification["source_report_sha256s"],
        "verification_sha256": sha256_bytes(raw),
        "evidence_root": evidence_root,
        "output_written": output_written,
        "global_green_permitted": False,
    }


def preflight_v0_verification(
    verification_id: str,
    report_paths: Mapping[str, str | Path],
) -> dict[str, object]:
    """Derive and validate V0 evidence without creating an output path."""

    plan = prepare_v0_verification(verification_id, report_paths)
    return _summary(plan.verification, evidence_root=None, output_written=False)


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _new_root(path: Path) -> Path:
    root = path.absolute()
    if _path_has_symlink(root.parent):
        raise Phase6V0VerificationError("V0 output parent contains a symlink")
    try:
        normalized = root.parent.resolve(strict=True) / root.name
    except OSError as exc:
        raise Phase6V0VerificationError("V0 output parent is unavailable") from exc
    if root != normalized or root.exists() or root.is_symlink():
        raise Phase6V0VerificationError("refusing to overwrite/alias V0 output root")
    os.mkdir(root, 0o700)
    _fsync_directory(root.parent)
    return root


def _formal_file_identity(path: Path) -> dict[str, object]:
    absolute = path.absolute()
    try:
        info = absolute.lstat()
    except OSError as exc:
        raise Phase6V0VerificationError(
            f"cannot inspect V0 formal file: {absolute}"
        ) from exc
    if (
        absolute.is_symlink()
        or not stat.S_ISREG(info.st_mode)
        or stat.S_IMODE(info.st_mode) != FORMAL_FILE_MODE
        or info.st_nlink != 1
    ):
        raise Phase6V0VerificationError(
            "V0 formal file must be direct 0444 regular nlink1 evidence"
        )
    raw = absolute.read_bytes()
    return {
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
        "path": str(absolute),
        "sha256": sha256_bytes(raw),
        "size": info.st_size,
    }


def _exclusive_bytes(path: Path, data: bytes) -> dict[str, object]:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(descriptor)
    os.chmod(path, FORMAL_FILE_MODE)
    _fsync_directory(path.parent)
    if path.read_bytes() != data:
        raise Phase6V0VerificationError("published V0 bytes changed on readback")
    return _formal_file_identity(path)


def _seal_root(root: Path) -> None:
    if not root.exists() or root.is_symlink():
        return
    for child in root.iterdir():
        if child.is_file() and not child.is_symlink():
            os.chmod(child, FORMAL_FILE_MODE)
    os.chmod(root, FORMAL_ROOT_MODE)
    _fsync_directory(root)
    _fsync_directory(root.parent)


def validate_published_v0_root(root: str | Path) -> dict[str, object]:
    """Reload the exact one-file immutable V0 evidence root."""

    path = Path(root).absolute()
    if _path_has_symlink(path):
        raise Phase6V0VerificationError("published V0 root contains an alias")
    try:
        resolved = path.resolve(strict=True)
        root_info = path.lstat()
    except OSError as exc:
        raise Phase6V0VerificationError("published V0 root is unavailable") from exc
    if (
        resolved != path
        or not stat.S_ISDIR(root_info.st_mode)
        or stat.S_IMODE(root_info.st_mode) != FORMAL_ROOT_MODE
        or {child.name for child in path.iterdir()} != OUTPUT_FILES
    ):
        raise Phase6V0VerificationError("published V0 root layout/mode changed")
    verification_path = path / "verification.json"
    identity = _formal_file_identity(verification_path)
    raw = verification_path.read_bytes()
    verification = _validate_verification_payload(
        _canonical_object(raw, "published V0 verification")
    )
    if identity["sha256"] != sha256_bytes(canonical_json_bytes(verification)):
        raise Phase6V0VerificationError("published V0 identity/bytes changed")
    return _summary(
        verification,
        evidence_root=str(path),
        output_written=True,
    )


def publish_v0_verification(
    verification_id: str,
    report_paths: Mapping[str, str | Path],
    output_root: str | Path,
) -> dict[str, object]:
    """Publish one fresh immutable V0 root after a complete source preflight."""

    plan = prepare_v0_verification(verification_id, report_paths)
    root = _new_root(Path(output_root))
    try:
        _exclusive_bytes(
            root / "verification.json", canonical_json_bytes(plan.verification)
        )
        _seal_root(root)
        return validate_published_v0_root(root)
    except BaseException:
        _seal_root(root)
        raise


__all__ = [
    "ASSERTION_OUTCOMES",
    "CHECK_REPORT_SCHEMA",
    "CHECK_STATES",
    "FORMAL_FILE_MODE",
    "FORMAL_ROOT_MODE",
    "Phase6V0VerificationError",
    "REQUIRED_CHECK_IDS",
    "VERIFICATION_SCHEMA",
    "preflight_v0_verification",
    "prepare_v0_verification",
    "publish_v0_verification",
    "validate_check_report_payload",
    "validate_published_v0_root",
]
