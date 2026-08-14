#!/usr/bin/env python3
"""Publish a populated, immutable Phase-6 per-observable evidence bundle.

This publisher performs no scientific calculation.  It accepts only a
canonical submission whose referenced evidence has already been frozen.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat

from schwgw.validation.phase6_domain import canonical_json_bytes
from schwgw.validation.phase6_observable_evidence import (
    BUNDLE_SCHEMA,
    MANIFEST_SCHEMA,
    ObservableEvidenceError,
    build_bundle,
    direct_file_identity,
    sha256_bytes,
    validate_bundle,
    validate_submission,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILES = ("manifest.json", "observable_evidence.json")


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _direct_draft_bytes(path: Path) -> bytes:
    absolute = path.absolute()
    if any(item.is_symlink() for item in (absolute, *absolute.parents)):
        raise ObservableEvidenceError("submission path contains a symlink component")
    try:
        resolved = absolute.resolve(strict=True)
        info = absolute.lstat()
    except OSError as exc:
        raise ObservableEvidenceError(f"cannot read submission: {absolute}") from exc
    if resolved != absolute or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ObservableEvidenceError("submission must be a direct regular nlink1 file")
    return absolute.read_bytes()


def _load_submission(path: Path) -> tuple[dict[str, object], str]:
    raw = _direct_draft_bytes(path)
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ObservableEvidenceError("submission is not JSON") from exc
    if not isinstance(payload, dict) or canonical_json_bytes(payload) != raw:
        raise ObservableEvidenceError("submission must be canonical JSON")
    validate_submission(payload)
    return payload, sha256_bytes(raw)


def _new_root(path: Path) -> Path:
    root = path.absolute()
    if any(item.is_symlink() for item in (root.parent, *root.parent.parents)):
        raise ObservableEvidenceError("output parent contains a symlink component")
    if root.exists() or root.is_symlink() or not root.parent.is_dir():
        raise ObservableEvidenceError(
            f"refusing to overwrite/alias evidence root: {root}"
        )
    os.mkdir(root, 0o700)
    _fsync_directory(root.parent)
    return root


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
    identity = direct_file_identity(path, require_immutable_parent=False)
    if path.read_bytes() != data:
        raise ObservableEvidenceError(f"published bytes changed: {path}")
    return identity


def _seal_root(root: Path) -> None:
    for child in root.iterdir():
        if child.is_file() and not child.is_symlink():
            os.chmod(child, 0o444)
    os.chmod(root, 0o555)
    _fsync_directory(root)
    _fsync_directory(root.parent)


def validate_published_root(root: str | Path) -> dict[str, object]:
    path = Path(root).absolute()
    if any(item.is_symlink() for item in (path, *path.parents)):
        raise ObservableEvidenceError("published root contains a symlink component")
    try:
        resolved = path.resolve(strict=True)
        root_info = path.lstat()
    except OSError as exc:
        raise ObservableEvidenceError(f"cannot inspect published root: {path}") from exc
    if (
        resolved != path
        or not stat.S_ISDIR(root_info.st_mode)
        or stat.S_IMODE(root_info.st_mode) != 0o555
        or set(child.name for child in path.iterdir()) != set(OUTPUT_FILES)
    ):
        raise ObservableEvidenceError("published root layout/mode changed")
    evidence_identity = direct_file_identity(path / "observable_evidence.json")
    manifest_identity = direct_file_identity(path / "manifest.json")
    evidence_raw = (path / "observable_evidence.json").read_bytes()
    manifest_raw = (path / "manifest.json").read_bytes()
    try:
        evidence = json.loads(evidence_raw)
        manifest = json.loads(manifest_raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ObservableEvidenceError("published root contains non-JSON bytes") from exc
    if not isinstance(evidence, dict) or canonical_json_bytes(evidence) != evidence_raw:
        raise ObservableEvidenceError(
            "published observable evidence is not canonical JSON"
        )
    if not isinstance(manifest, dict) or canonical_json_bytes(manifest) != manifest_raw:
        raise ObservableEvidenceError("published manifest is not canonical JSON")
    validate_bundle(evidence)
    fields = {
        "schema",
        "bundle_schema",
        "observable_evidence_identity",
        "certificate_count",
        "state_counts",
        "scientific_pass_claimed",
        "global_green_permitted",
        "li_figure_agreement_primary_gate",
        "publisher_generated_science",
        "submission_sha256",
    }
    if set(manifest) != fields or manifest["schema"] != MANIFEST_SCHEMA:
        raise ObservableEvidenceError("published manifest schema changed")
    if (
        manifest["bundle_schema"] != BUNDLE_SCHEMA
        or manifest["observable_evidence_identity"] != evidence_identity
        or manifest["certificate_count"] != evidence["certificate_count"]
        or manifest["state_counts"] != evidence["state_counts"]
        or manifest["scientific_pass_claimed"] != evidence["scientific_pass_claimed"]
        or manifest["global_green_permitted"] is not False
        or manifest["li_figure_agreement_primary_gate"] is not False
        or manifest["publisher_generated_science"] is not False
        or not isinstance(manifest["submission_sha256"], str)
        or len(manifest["submission_sha256"]) != 64
    ):
        raise ObservableEvidenceError("published manifest is not derived from bundle")
    return {
        "certificate_count": evidence["certificate_count"],
        "evidence_root": str(path),
        "manifest_sha256": manifest_identity["sha256"],
        "observable_evidence_sha256": evidence_identity["sha256"],
        "state_counts": evidence["state_counts"],
    }


def publish_submission(submission_path: Path, output_root: Path) -> dict[str, object]:
    submission, submission_sha256 = _load_submission(submission_path)
    certificates = validate_submission(submission)
    bundle = build_bundle(certificates)
    validate_bundle(bundle)
    root = _new_root(output_root)
    try:
        evidence_identity = _publish_file(
            root / "observable_evidence.json", canonical_json_bytes(bundle)
        )
        manifest = {
            "schema": MANIFEST_SCHEMA,
            "bundle_schema": BUNDLE_SCHEMA,
            "observable_evidence_identity": evidence_identity,
            "certificate_count": bundle["certificate_count"],
            "state_counts": bundle["state_counts"],
            "scientific_pass_claimed": bundle["scientific_pass_claimed"],
            "global_green_permitted": False,
            "li_figure_agreement_primary_gate": False,
            "publisher_generated_science": False,
            "submission_sha256": submission_sha256,
        }
        _publish_file(root / "manifest.json", canonical_json_bytes(manifest))
        _seal_root(root)
        return validate_published_root(root)
    except BaseException:
        _seal_root(root)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--submission", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            publish_submission(args.submission, args.output_root), sort_keys=True
        )
    )


if __name__ == "__main__":
    main()
