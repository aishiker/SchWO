#!/usr/bin/env python3
"""Publish an immutable Phase-6 V1 per-observable release ledger.

This command performs no numerical calculation.  It consumes one canonical
submission and already frozen evidence envelopes, then creates exactly one
fresh evidence root.  Existing roots are never reused or replaced.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat

from schwgw.validation.phase6_domain import canonical_json_bytes
from schwgw.validation.phase6_release import (
    LEDGER_SCHEMA,
    MANIFEST_SCHEMA,
    Phase6ReleaseError,
    build_ledger,
    direct_file_identity,
    sha256_bytes,
    validate_ledger,
    validate_submission,
)


OUTPUT_FILES = ("manifest.json", "release_ledger.json")


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _direct_submission_bytes(path: Path) -> bytes:
    absolute = path.absolute()
    if any(component.is_symlink() for component in (absolute, *absolute.parents)):
        raise Phase6ReleaseError("submission path contains a symlink component")
    try:
        resolved = absolute.resolve(strict=True)
        info = absolute.lstat()
    except OSError as exc:
        raise Phase6ReleaseError(f"cannot read release submission: {absolute}") from exc
    if resolved != absolute or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise Phase6ReleaseError("submission must be a direct regular nlink1 file")
    return absolute.read_bytes()


def _load_submission(path: Path) -> tuple[dict[str, object], str]:
    raw = _direct_submission_bytes(path)
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise Phase6ReleaseError("release submission is not JSON") from exc
    if not isinstance(payload, dict) or canonical_json_bytes(payload) != raw:
        raise Phase6ReleaseError("release submission must be canonical JSON")
    validate_submission(payload)
    return payload, sha256_bytes(raw)


def _new_root(path: Path) -> Path:
    root = path.absolute()
    if any(component.is_symlink() for component in (root.parent, *root.parent.parents)):
        raise Phase6ReleaseError("output parent contains a symlink component")
    try:
        normalized = root.parent.resolve(strict=True) / root.name
    except OSError as exc:
        raise Phase6ReleaseError(
            f"cannot resolve output parent: {root.parent}"
        ) from exc
    if normalized != root:
        raise Phase6ReleaseError("output root must be a normalized direct path")
    if root.exists() or root.is_symlink() or not root.parent.is_dir():
        raise Phase6ReleaseError(f"refusing to overwrite/alias release root: {root}")
    os.mkdir(root, 0o700)
    _fsync_directory(root.parent)
    return root


def _unsealed_identity(path: Path) -> dict[str, object]:
    absolute = path.absolute()
    info = absolute.lstat()
    if (
        absolute.is_symlink()
        or not stat.S_ISREG(info.st_mode)
        or info.st_nlink != 1
        or stat.S_IMODE(info.st_mode) != 0o444
    ):
        raise Phase6ReleaseError("published file is not a direct 0444 nlink1 file")
    return {
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
        "path": str(absolute),
        "sha256": sha256_bytes(absolute.read_bytes()),
        "size": info.st_size,
    }


def _publish_file(path: Path, data: bytes) -> dict[str, object]:
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
    os.chmod(path, 0o444)
    _fsync_directory(path.parent)
    identity = _unsealed_identity(path)
    if path.read_bytes() != data:
        raise Phase6ReleaseError(f"published bytes changed: {path}")
    return identity


def _seal_root(root: Path) -> None:
    for child in root.iterdir():
        if child.is_file() and not child.is_symlink():
            os.chmod(child, 0o444)
    os.chmod(root, 0o555)
    _fsync_directory(root)
    _fsync_directory(root.parent)


def validate_published_root(root: str | Path) -> dict[str, object]:
    """Validate exact layout, permissions, bytes, identities, and derived claims."""

    path = Path(root).absolute()
    if any(component.is_symlink() for component in (path, *path.parents)):
        raise Phase6ReleaseError("published root contains a symlink component")
    try:
        resolved = path.resolve(strict=True)
        root_info = path.lstat()
    except OSError as exc:
        raise Phase6ReleaseError(
            f"cannot inspect published release root: {path}"
        ) from exc
    if (
        resolved != path
        or not stat.S_ISDIR(root_info.st_mode)
        or stat.S_IMODE(root_info.st_mode) != 0o555
        or {child.name for child in path.iterdir()} != set(OUTPUT_FILES)
    ):
        raise Phase6ReleaseError("published release root layout/mode changed")
    ledger_identity = direct_file_identity(path / "release_ledger.json")
    manifest_identity = direct_file_identity(path / "manifest.json")
    ledger_raw = (path / "release_ledger.json").read_bytes()
    manifest_raw = (path / "manifest.json").read_bytes()
    try:
        ledger = json.loads(ledger_raw)
        manifest = json.loads(manifest_raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise Phase6ReleaseError(
            "published release root contains non-JSON bytes"
        ) from exc
    if not isinstance(ledger, dict) or canonical_json_bytes(ledger) != ledger_raw:
        raise Phase6ReleaseError("published release ledger is not canonical JSON")
    if not isinstance(manifest, dict) or canonical_json_bytes(manifest) != manifest_raw:
        raise Phase6ReleaseError("published release manifest is not canonical JSON")
    validate_ledger(ledger)
    fields = {
        "schema",
        "ledger_schema",
        "release_id",
        "release_ledger_identity",
        "certificate_count",
        "state_counts",
        "gate_certificate_counts",
        "pass_certificate_count",
        "global_status",
        "global_green_permitted",
        "li_figure_agreement_primary_gate",
        "full_paper_figure_rerun_performed",
        "publisher_generated_science",
        "submission_sha256",
    }
    if set(manifest) != fields or manifest["schema"] != MANIFEST_SCHEMA:
        raise Phase6ReleaseError("published release manifest schema changed")
    if (
        manifest["ledger_schema"] != LEDGER_SCHEMA
        or manifest["release_id"] != ledger["release_id"]
        or manifest["release_ledger_identity"] != ledger_identity
        or manifest["certificate_count"] != ledger["certificate_count"]
        or manifest["state_counts"] != ledger["state_counts"]
        or manifest["gate_certificate_counts"] != ledger["gate_certificate_counts"]
        or manifest["pass_certificate_count"] != ledger["pass_certificate_count"]
        or manifest["global_status"] is not None
        or manifest["global_green_permitted"] is not False
        or manifest["li_figure_agreement_primary_gate"] is not False
        or manifest["full_paper_figure_rerun_performed"] is not False
        or manifest["publisher_generated_science"] is not False
        or manifest["submission_sha256"] != ledger["submission_sha256"]
    ):
        raise Phase6ReleaseError("published manifest is not derived from its ledger")
    return {
        "certificate_count": ledger["certificate_count"],
        "evidence_root": str(path),
        "manifest_sha256": manifest_identity["sha256"],
        "release_ledger_sha256": ledger_identity["sha256"],
        "state_counts": ledger["state_counts"],
    }


def publish_submission(submission_path: Path, output_root: Path) -> dict[str, object]:
    """Publish one fresh immutable root from a validated canonical submission."""

    submission, submission_sha256 = _load_submission(submission_path)
    ledger = build_ledger(submission, submission_sha256=submission_sha256)
    root = _new_root(output_root)
    try:
        ledger_identity = _publish_file(
            root / "release_ledger.json", canonical_json_bytes(ledger)
        )
        manifest = {
            "schema": MANIFEST_SCHEMA,
            "ledger_schema": LEDGER_SCHEMA,
            "release_id": ledger["release_id"],
            "release_ledger_identity": ledger_identity,
            "certificate_count": ledger["certificate_count"],
            "state_counts": ledger["state_counts"],
            "gate_certificate_counts": ledger["gate_certificate_counts"],
            "pass_certificate_count": ledger["pass_certificate_count"],
            "global_status": None,
            "global_green_permitted": False,
            "li_figure_agreement_primary_gate": False,
            "full_paper_figure_rerun_performed": False,
            "publisher_generated_science": False,
            "submission_sha256": submission_sha256,
        }
        _publish_file(root / "manifest.json", canonical_json_bytes(manifest))
        _seal_root(root)
        return validate_published_root(root)
    except BaseException:
        _seal_root(root)
        raise


def preflight_submission(submission_path: Path) -> dict[str, object]:
    """Validate and derive counts without creating an output path."""

    submission, submission_sha256 = _load_submission(submission_path)
    ledger = build_ledger(submission, submission_sha256=submission_sha256)
    return {
        "release_id": ledger["release_id"],
        "submission_sha256": submission_sha256,
        "evidence_envelope_count": len(ledger["evidence_inventory"]),
        "certificate_count": ledger["certificate_count"],
        "state_counts": ledger["state_counts"],
        "gate_certificate_counts": ledger["gate_certificate_counts"],
        "pass_certificate_count": ledger["pass_certificate_count"],
        "global_status": None,
        "output_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--submission", type=Path, required=True)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="validate all live inputs and derived counts without writing a root",
    )
    args = parser.parse_args(argv)
    if args.check_only:
        if args.output_root is not None:
            parser.error("--check-only cannot be combined with --output-root")
        result = preflight_submission(args.submission)
    else:
        if args.output_root is None:
            parser.error("--output-root is required unless --check-only is used")
        result = publish_submission(args.submission, args.output_root)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
