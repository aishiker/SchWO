#!/usr/bin/env python3
"""Freeze generic Phase-6 V1 calibration and shard/resume contract data only."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
from typing import Any

from schwgw.validation.phase6_domain import (
    DOMAIN_SCHEMA,
    DomainBundle,
    ProductionLmax,
    canonical_json_bytes,
    read_jsonl_keys,
    source_file_identity,
    validate_bundle,
    validate_contract_payload,
)
from schwgw.validation.phase6_execution_contract import (
    EXECUTION_SCHEMA,
    ExecutionContractError,
    calibration_jsonl_bytes,
    execution_contract_payload,
    external_direct_calibration_keys,
    finite_response_radii_from_source,
    shard_inventory,
    transition_calibration_keys,
    validate_shard_inventory,
)


ROOT = Path(__file__).resolve().parents[1]
BOUND_DOMAIN_ROOT = ROOT / "runs/phase6/v1_domain_freeze_v3_20260806"
DEFAULT_OUTPUT_ROOT = ROOT / "runs/phase6/v1_execution_contract_v4_20260806"
CONSUMED_EXECUTION_ROOTS = (
    ROOT / "runs/phase6/v1_execution_contract_20260806",
    ROOT / "runs/phase6/v1_execution_contract_v2_20260806",
    ROOT / "runs/phase6/v1_execution_contract_v3_20260806",
)
PHASE6_CONFIG = ROOT / "configs/phase6_independent_physical_validation.yaml"
EXECUTION_MODULE = ROOT / "src/schwgw/validation/phase6_execution_contract.py"


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


def _identity(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    info = resolved.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ExecutionContractError(f"identity target must be a regular nlink1 file: {resolved}")
    return {
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
        "path": str(resolved),
        "sha256": _sha256_file(resolved),
        "size": info.st_size,
    }


def _source_identity(path: Path) -> dict[str, object]:
    return source_file_identity(path)


def _publish(path: Path, data: bytes) -> dict[str, object]:
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
    identity = _identity(path)
    if path.read_bytes() != data or identity["sha256"] != hashlib.sha256(data).hexdigest():
        raise ExecutionContractError(f"published bytes changed: {path}")
    return identity


def _new_root(path: Path) -> Path:
    resolved = path.resolve()
    if resolved.exists() or resolved.is_symlink():
        raise ExecutionContractError(f"refusing to overwrite evidence root: {resolved}")
    if not resolved.parent.is_dir() or resolved.parent.is_symlink():
        raise ExecutionContractError(f"invalid evidence parent: {resolved.parent}")
    os.mkdir(resolved, 0o700)
    _fsync_directory(resolved.parent)
    return resolved


def _load_jsonl_records(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_bytes().splitlines(), start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ExecutionContractError(f"invalid JSONL: {path} line {line_number}") from exc
        if not isinstance(record, dict) or canonical_json_bytes(record).rstrip(b"\n") != line:
            raise ExecutionContractError(f"non-canonical JSONL: {path} line {line_number}")
        records.append(record)
    return records


def _validate_source_identity(identity: object, *, label: str) -> None:
    if not isinstance(identity, dict) or set(identity) != {"mode", "nlink", "path", "sha256", "size"}:
        raise ExecutionContractError(f"source identity schema changed: {label}")
    actual = _source_identity(Path(str(identity["path"])))
    if actual != identity:
        raise ExecutionContractError(f"source identity mismatch: {label}")


def load_bound_domain(root: Path = BOUND_DOMAIN_ROOT) -> tuple[DomainBundle, dict[str, object]]:
    """Reload and verify every byte-bound domain file and source binding."""

    root = root.resolve(strict=True)
    expected_files = (
        "D_ext.jsonl",
        "D_prod.jsonl",
        "D_required.jsonl",
        "D_union.jsonl",
        "domain_contract.json",
        "manifest.json",
    )
    if stat.S_IMODE(root.lstat().st_mode) != 0o555:
        raise ExecutionContractError("bound domain root is not immutable")
    files = {name: _identity(root / name) for name in expected_files}
    if any(identity["mode"] != 0o444 for identity in files.values()):
        raise ExecutionContractError("bound domain file mode changed")
    payload = json.loads((root / "domain_contract.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    names = ("D_prod.jsonl", "D_ext.jsonl", "D_required.jsonl", "D_union.jsonl")
    data = {name: (root / name).read_bytes() for name in names}
    keys = {name: read_jsonl_keys(root / name) for name in names}
    try:
        production_lmax = tuple(
            ProductionLmax(row["kM"], tuple(row["lmax_pair"]))
            for row in payload["production_source"]["frequency_lmax"]
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ExecutionContractError("bound production lmax metadata changed") from exc
    bundle = DomainBundle(
        production_lmax=production_lmax,
        production=keys["D_prod.jsonl"],
        extension=keys["D_ext.jsonl"],
        required=keys["D_required.jsonl"],
        union=keys["D_union.jsonl"],
    )
    validate_bundle(bundle)
    validate_contract_payload(payload, bundle=bundle, domain_file_bytes=data)
    if payload.get("schema") != DOMAIN_SCHEMA or manifest.get("contract") != files["domain_contract.json"]:
        raise ExecutionContractError("bound domain manifest/contract identity changed")
    if manifest.get("domain_files") != payload.get("domain_files"):
        raise ExecutionContractError("bound domain manifest file identities changed")
    for label, identity in payload["source_identities"].items():
        _validate_source_identity(identity, label=f"bound {label}")
    records = payload["production_source"]["schedule_source_bindings"]
    if not isinstance(records, list) or len(records) != 40:
        raise ExecutionContractError("bound schedule binding cardinality changed")
    for record in records:
        if not isinstance(record, dict):
            raise ExecutionContractError("bound schedule binding type changed")
        _validate_source_identity(
            record.get("resolved_source_identity"), label=f"bound schedule {record.get('kM')}"
        )
        if record["resolved_source_identity"]["sha256"] != record.get("binding_source_sha256"):
            raise ExecutionContractError("bound schedule source hash changed")
    return bundle, {
        "D_union_key_list_sha256": files["D_union.jsonl"]["sha256"],
        "domain_contract_sha256": files["domain_contract.json"]["sha256"],
        "file_identities": files,
        "root": str(root),
    }


def _source_identities(finite_radius_source: Path) -> dict[str, dict[str, object]]:
    return {
        "execution_contract_module": _source_identity(EXECUTION_MODULE),
        "execution_contract_script": _source_identity(Path(__file__).resolve()),
        "finite_response_coordinate_source": _source_identity(finite_radius_source),
        "phase6_config": _source_identity(PHASE6_CONFIG),
    }


def _consumed_execution_predecessors() -> list[dict[str, object]]:
    names = (
        "D_transition_calibration.jsonl",
        "D_external_direct_calibration.jsonl",
        "shard_inventory.jsonl",
        "execution_contract.json",
        "manifest.json",
    )
    records: list[dict[str, object]] = []
    for index, raw_root in enumerate(CONSUMED_EXECUTION_ROOTS, start=1):
        root = raw_root.resolve(strict=True)
        records.append(
            {
                "evidence_root": str(root),
                "file_identities": {name: _source_identity(root / name) for name in names},
                "reason": (
                    "FIRST_EXECUTION_ROOT_CONSUMED_NON_AUTHORITATIVE"
                    if index == 1
                    else "STALE_EXECUTION_ROOT_CONSUMED_NON_AUTHORITATIVE"
                ),
            }
        )
    return records


def _validate_frozen_root(root: Path) -> None:
    """Reload all new sets, inventory, manifest, and the bound source domain."""

    bundle, bound = load_bound_domain()
    contract_path = root / "execution_contract.json"
    manifest_path = root / "manifest.json"
    payload = json.loads(contract_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("schema") != EXECUTION_SCHEMA or payload.get("bound_domain") != bound:
        raise ExecutionContractError("execution contract bound-domain identity changed")
    finite_identity = payload["source_identities"]["finite_response_coordinate_source"]
    _validate_source_identity(finite_identity, label="finite-response coordinate source")
    for label, identity in payload["source_identities"].items():
        _validate_source_identity(identity, label=str(label))
    predecessors = payload.get("consumed_execution_predecessors")
    if not isinstance(predecessors, list) or len(predecessors) != 3:
        raise ExecutionContractError("consumed execution predecessor provenance changed")
    for predecessor in predecessors:
        if not isinstance(predecessor, dict) or not isinstance(predecessor.get("file_identities"), dict):
            raise ExecutionContractError("consumed execution predecessor schema changed")
        for label, identity in predecessor["file_identities"].items():
            _validate_source_identity(identity, label=f"consumed execution {label}")
    radii = finite_response_radii_from_source(Path(str(finite_identity["path"])))
    transition = transition_calibration_keys(radii)
    external = external_direct_calibration_keys()
    transition_bytes = calibration_jsonl_bytes(transition)
    external_bytes = calibration_jsonl_bytes(external)
    if (root / "D_transition_calibration.jsonl").read_bytes() != transition_bytes:
        raise ExecutionContractError("transition calibration reload mismatch")
    if (root / "D_external_direct_calibration.jsonl").read_bytes() != external_bytes:
        raise ExecutionContractError("external direct calibration reload mismatch")
    shards = shard_inventory(bundle)
    actual_shards = _load_jsonl_records(root / "shard_inventory.jsonl")
    expected_shards = [record.to_record() for record in shards]
    if actual_shards != expected_shards:
        raise ExecutionContractError("shard inventory reload mismatch")
    validate_shard_inventory(shards, bundle)
    expected_files = (
        "D_transition_calibration.jsonl",
        "D_external_direct_calibration.jsonl",
        "shard_inventory.jsonl",
        "execution_contract.json",
        "manifest.json",
    )
    identities = {name: _identity(root / name) for name in expected_files}
    if any(identity["mode"] != 0o444 for identity in identities.values()):
        raise ExecutionContractError("execution evidence file mode changed")
    if manifest.get("contract") != identities["execution_contract.json"]:
        raise ExecutionContractError("execution manifest contract identity changed")
    if manifest.get("evidence_files") != {
        name: identities[name]
        for name in ("D_transition_calibration.jsonl", "D_external_direct_calibration.jsonl", "shard_inventory.jsonl")
    }:
        raise ExecutionContractError("execution manifest evidence identities changed")


def freeze_execution_contract(output_root: Path) -> dict[str, Any]:
    """Publish one new immutable generic calibration and shard contract package."""

    bundle, bound_domain = load_bound_domain()
    finite_source = Path(str(
        json.loads((BOUND_DOMAIN_ROOT / "domain_contract.json").read_text(encoding="utf-8"))
        ["source_identities"]["accepted_uniform40_merged_npz"]["path"]
    ))
    radii = finite_response_radii_from_source(finite_source)
    transition = transition_calibration_keys(radii)
    external = external_direct_calibration_keys()
    shards = shard_inventory(bundle)
    payload = execution_contract_payload(
        bound_domain=bound_domain,
        finite_radius_source={
            "path": str(finite_source.resolve(strict=True)),
            "radii_M": [str(radius) for radius in radii],
            "source_identity": _source_identity(finite_source),
        },
        transition_keys=transition,
        external_keys=external,
        shards=shards,
        source_identities=_source_identities(finite_source),
        consumed_execution_predecessors=_consumed_execution_predecessors(),
    )
    output_root = _new_root(output_root)
    files = {
        "D_transition_calibration.jsonl": calibration_jsonl_bytes(transition),
        "D_external_direct_calibration.jsonl": calibration_jsonl_bytes(external),
        "shard_inventory.jsonl": b"".join(
            canonical_json_bytes(record.to_record()) for record in shards
        ),
    }
    try:
        identities = {name: _publish(output_root / name, data) for name, data in sorted(files.items())}
        contract_identity = _publish(output_root / "execution_contract.json", canonical_json_bytes(payload))
        manifest = {
            "contract": contract_identity,
            "evidence_files": identities,
            "global_green_permitted": False,
            "numerical_solves_executed": 0,
            "schema": EXECUTION_SCHEMA,
            "status": "EXECUTION_CONTRACT_FROZEN_NO_NUMERICAL_SOLVES",
        }
        manifest_identity = _publish(output_root / "manifest.json", canonical_json_bytes(manifest))
        _validate_frozen_root(output_root)
    except BaseException:
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
    if stat.S_IMODE(output_root.lstat().st_mode) != 0o555:
        raise ExecutionContractError("execution evidence root permission hardening failed")
    return {
        "contract_sha256": contract_identity["sha256"],
        "evidence_root": str(output_root),
        "external_direct_count": len(external),
        "manifest_sha256": manifest_identity["sha256"],
        "shard_count": len(shards),
        "transition_count": len(transition),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    print(json.dumps(freeze_execution_contract(args.output_root), sort_keys=True))


if __name__ == "__main__":
    main()
