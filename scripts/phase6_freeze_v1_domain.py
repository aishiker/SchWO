#!/usr/bin/env python3
"""Freeze the exact non-numerical Phase-6 V1 radial-domain contract.

The script reads accepted Fig. 5/6 source metadata only.  It neither imports
nor invokes a radial solver.  A successful invocation creates a new,
no-overwrite evidence directory and makes its files/root read-only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
from typing import Any

from schwgw.io.tablei_paper_inferred import DEFAULT_SOURCE_MERGE, load_uniform_source_contract
from schwgw.validation.phase6_domain import (
    DOMAIN_SCHEMA,
    DomainBundle,
    DomainContractError,
    ProductionLmax,
    build_v1_domain,
    canonical_km,
    canonical_json_bytes,
    contract_payload,
    jsonl_bytes,
    read_jsonl_keys,
    sha256_bytes,
    source_file_identity,
    validate_bundle,
    validate_contract_payload,
)


ROOT = Path(__file__).resolve().parents[1]
PHASE6_CONFIG = ROOT / "configs/phase6_independent_physical_validation.yaml"
SOURCE_MODULE = ROOT / "src/schwgw/io/tablei_paper_inferred.py"
DOMAIN_MODULE = ROOT / "src/schwgw/validation/phase6_domain.py"
DEFAULT_OUTPUT_ROOT = ROOT / "runs/phase6/v1_domain_freeze_v3_20260806"
CONSUMED_ROOTS = (
    ROOT / "runs/phase6/v1_domain_freeze_20260806",
    ROOT / "runs/phase6/v1_domain_freeze_v2_20260806",
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _file_identity(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    status = resolved.lstat()
    if not stat.S_ISREG(status.st_mode) or status.st_nlink != 1:
        raise DomainContractError(f"evidence file must be a regular nlink1 file: {resolved}")
    return {
        "mode": stat.S_IMODE(status.st_mode),
        "nlink": status.st_nlink,
        "path": str(resolved),
        "sha256": _sha256_file(resolved),
        "size": status.st_size,
    }


def _domain_file_identity(path: Path, *, count: int) -> dict[str, object]:
    identity = _file_identity(path)
    return {"count": count, **identity}


def _source_identity(path: Path) -> dict[str, object]:
    return source_file_identity(path)


def _publish_no_overwrite(path: Path, data: bytes) -> dict[str, object]:
    """Publish exact bytes atomically through O_EXCL, then lock read-only."""

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
    identity = _file_identity(path)
    if path.read_bytes() != data or identity["sha256"] != sha256_bytes(data):
        raise DomainContractError(f"published bytes changed: {path}")
    return identity


def _new_evidence_root(path: Path) -> Path:
    path = path.resolve()
    if path.exists() or path.is_symlink():
        raise DomainContractError(f"refusing to overwrite existing evidence root: {path}")
    parent = path.parent
    if not parent.is_dir() or parent.is_symlink():
        raise DomainContractError(f"evidence parent must be an existing real directory: {parent}")
    os.mkdir(path, 0o700)
    _fsync_directory(parent)
    return path


def _source_identities(source_merge: Path) -> dict[str, dict[str, object]]:
    source_sidecar = Path(str(source_merge) + ".json")
    script_path = Path(__file__).resolve()
    sources = {
        "accepted_uniform40_merged_npz": source_merge,
        "accepted_uniform40_merged_sidecar": source_sidecar,
        "phase6_config": PHASE6_CONFIG,
        "phase6_domain_module": DOMAIN_MODULE,
        "phase6_freeze_script": script_path,
        "uniform_source_contract_loader": SOURCE_MODULE,
    }
    return {name: _source_identity(path) for name, path in sorted(sources.items())}


def _schedule_source_bindings(bindings: list[dict[str, Any]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for raw in bindings:
        try:
            km = canonical_km(raw["kM"])
            pair = [int(value) for value in raw["lmax_pair"]]
            source_text = str(raw["source"])
            expected_hash = str(raw["source_sha256"])
        except (KeyError, TypeError, ValueError) as exc:
            raise DomainContractError("malformed uniform schedule source binding") from exc
        if len(pair) != 2:
            raise DomainContractError(f"invalid lmax pair binding for kM={km}")
        path = Path(source_text)
        resolved = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
        identity = _source_identity(resolved)
        if identity["sha256"] != expected_hash:
            raise DomainContractError(f"schedule source hash mismatch for kM={km}: {source_text}")
        records.append(
            {
                "binding_source": source_text,
                "binding_source_sha256": expected_hash,
                "kM": km,
                "kind": raw.get("kind"),
                "lmax_pair": pair,
                "resolved_source_identity": identity,
                "row": raw.get("row"),
            }
        )
    if len(records) != 40:
        raise DomainContractError("uniform schedule binding cardinality changed")
    return records


def _consumed_predecessor_provenance() -> list[dict[str, object]]:
    names = (
        "D_ext.jsonl",
        "D_prod.jsonl",
        "D_required.jsonl",
        "D_union.jsonl",
        "domain_contract.json",
        "manifest.json",
    )
    records: list[dict[str, object]] = []
    for raw_root in CONSUMED_ROOTS:
        root = raw_root.resolve(strict=True)
        records.append(
            {
                "evidence_root": str(root),
                "file_identities": {name: _source_identity(root / name) for name in names},
                "reason": "PREVIOUS_FREEZE_CONSUMED_NON_AUTHORITATIVE",
            }
        )
    return records


def _validate_reloaded_source_identity(identity: object, *, label: str) -> None:
    if not isinstance(identity, dict) or set(identity) != {"mode", "nlink", "path", "sha256", "size"}:
        raise DomainContractError(f"invalid reloaded source identity: {label}")
    current = _source_identity(Path(str(identity["path"])))
    if current != identity:
        raise DomainContractError(f"reloaded source identity mismatch: {label}")


def _validate_frozen_root(root: Path) -> None:
    """Reload all files and sources before root permission hardening."""

    contract_path = root / "domain_contract.json"
    manifest_path = root / "manifest.json"
    payload = json.loads(contract_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    names = ("D_prod.jsonl", "D_ext.jsonl", "D_required.jsonl", "D_union.jsonl")
    data_by_name = {name: (root / name).read_bytes() for name in names}
    keys_by_name = {name: read_jsonl_keys(root / name) for name in names}
    production_lmax = tuple(
        ProductionLmax(raw["kM"], tuple(raw["lmax_pair"]))
        for raw in payload["production_source"]["frequency_lmax"]
    )
    bundle = DomainBundle(
        production_lmax=production_lmax,
        production=keys_by_name["D_prod.jsonl"],
        extension=keys_by_name["D_ext.jsonl"],
        required=keys_by_name["D_required.jsonl"],
        union=keys_by_name["D_union.jsonl"],
    )
    validate_bundle(bundle)
    validate_contract_payload(payload, bundle=bundle, domain_file_bytes=data_by_name)
    for name, count in {
        "D_prod.jsonl": len(bundle.production),
        "D_ext.jsonl": len(bundle.extension),
        "D_required.jsonl": len(bundle.required),
        "D_union.jsonl": len(bundle.union),
    }.items():
        if _domain_file_identity(root / name, count=count) != payload["domain_files"][name]:
            raise DomainContractError(f"reloaded domain file identity mismatch: {name}")
    for name, identity in payload["source_identities"].items():
        _validate_reloaded_source_identity(identity, label=str(name))
    for record in payload["production_source"]["schedule_source_bindings"]:
        _validate_reloaded_source_identity(
            record["resolved_source_identity"], label=f"schedule kM={record['kM']}"
        )
    for predecessor in payload["consumed_predecessors"]:
        for name, identity in predecessor["file_identities"].items():
            _validate_reloaded_source_identity(identity, label=f"consumed {name}")
    if manifest["contract"] != _file_identity(contract_path):
        raise DomainContractError("manifest contract identity mismatch")
    if manifest["domain_files"] != payload["domain_files"]:
        raise DomainContractError("manifest domain identity mismatch")


def freeze_domain(output_root: Path, *, source_merge: Path = DEFAULT_SOURCE_MERGE) -> dict[str, Any]:
    """Freeze one fresh evidence package and return its independently usable summary."""

    source_merge = (ROOT / source_merge).resolve() if not source_merge.is_absolute() else source_merge.resolve()
    schedule, bindings = load_uniform_source_contract(source_merge)
    bundle = build_v1_domain(schedule)
    validate_bundle(bundle)
    if len(bindings) != 40:
        raise DomainContractError("uniform source binding cardinality changed")
    schedule_bindings = _schedule_source_bindings(bindings)
    consumed_predecessors = _consumed_predecessor_provenance()

    output_root = _new_evidence_root(output_root)
    data_by_name = {
        "D_prod.jsonl": jsonl_bytes(bundle.production),
        "D_ext.jsonl": jsonl_bytes(bundle.extension),
        "D_required.jsonl": jsonl_bytes(bundle.required),
        "D_union.jsonl": jsonl_bytes(bundle.union),
    }
    identities: dict[str, dict[str, object]] = {}
    try:
        for name in sorted(data_by_name):
            published = _publish_no_overwrite(output_root / name, data_by_name[name])
            identities[name] = {
                "count": data_by_name[name].count(b"\n"),
                **published,
            }
        payload = contract_payload(
            bundle,
            source_identities=_source_identities(source_merge),
            domain_file_identities=identities,
            schedule_source_bindings=schedule_bindings,
            consumed_predecessors=consumed_predecessors,
        )
        contract_identity = _publish_no_overwrite(
            output_root / "domain_contract.json", canonical_json_bytes(payload)
        )
        manifest_payload = {
            "contract": contract_identity,
            "domain_files": identities,
            "global_green_permitted": False,
            "numerical_solves_executed": 0,
            "schema": DOMAIN_SCHEMA,
            "status": "DOMAIN_CONTRACT_FROZEN_NO_NUMERICAL_SOLVES",
        }
        manifest_identity = _publish_no_overwrite(
            output_root / "manifest.json", canonical_json_bytes(manifest_payload)
        )

        # This must complete before chmod: it reloads every exact set and every
        # production/schedule/predecessor source identity from disk.
        _validate_frozen_root(output_root)
    except BaseException:
        # Deliberately leave an immutable partial root for forensic inspection; no overwrite/retry.
        for child in output_root.iterdir():
            if child.is_file():
                os.chmod(child, 0o444)
        os.chmod(output_root, 0o555)
        _fsync_directory(output_root)
        _fsync_directory(output_root.parent)
        raise

    os.chmod(output_root, 0o555)
    _fsync_directory(output_root)
    _fsync_directory(output_root.parent)
    final_status = output_root.lstat()
    if stat.S_IMODE(final_status.st_mode) != 0o555:
        raise DomainContractError("evidence root permission hardening failed")
    return {
        "contract_sha256": contract_identity["sha256"],
        "evidence_root": str(output_root),
        "manifest_sha256": manifest_identity["sha256"],
        "set_counts": {
            "D_ext": len(bundle.extension),
            "D_prod": len(bundle.production),
            "D_prod_intersection_D_required": len(set(bundle.production) & set(bundle.required)),
            "D_required": len(bundle.required),
            "D_union": len(bundle.union),
        },
        "source_identities": _source_identities(source_merge),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--source-merge", type=Path, default=DEFAULT_SOURCE_MERGE)
    args = parser.parse_args()
    print(json.dumps(freeze_domain(args.output_root, source_merge=args.source_merge), sort_keys=True))


if __name__ == "__main__":
    main()
