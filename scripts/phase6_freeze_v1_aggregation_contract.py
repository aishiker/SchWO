#!/usr/bin/env python3
"""Publish a no-solver, immutable Phase-6 V1 aggregation contract."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from schwgw.validation.phase6_aggregation import (
    AGGREGATION_SCHEMA,
    AggregationContractError,
    source_file_identity,
    validate_immutable_root,
)
from schwgw.validation.phase6_domain import canonical_json_bytes


ROOT = Path(__file__).resolve().parents[1]
BOUND_DOMAIN_ROOT = ROOT / "runs/phase6/v1_domain_freeze_v3_20260806"
BOUND_EXECUTION_ROOT = ROOT / "runs/phase6/v1_execution_contract_v4_20260806"
DEFAULT_OUTPUT_ROOT = ROOT / "runs/phase6/v1_aggregation_contract_v8_20260806"
CONSUMED_AGGREGATION_ROOTS = (
    (ROOT / "runs/phase6/v1_aggregation_contract_20260806", "MISSING_SHARD_CHECKPOINT_VALIDATOR"),
    (ROOT / "runs/phase6/v1_aggregation_contract_v2_20260806", "LIVE_THRESHOLD_IDENTITY_RECHECK_HARDENING"),
    (ROOT / "runs/phase6/v1_aggregation_contract_v3_20260806", "RESULT_IDENTITY_AND_DERIVED_ACCEPTANCE_HARDENING"),
    (ROOT / "runs/phase6/v1_aggregation_contract_v4_20260806", "IMMUTABLE_PAYLOAD_AND_CERTIFICATE_DERIVATION_HARDENING"),
    (ROOT / "runs/phase6/v1_aggregation_contract_v5_20260806", "EXACT_PAYLOAD_AND_NONCIRCULAR_THRESHOLD_PROVENANCE_HARDENING"),
    (ROOT / "runs/phase6/v1_aggregation_contract_v6_20260806", "RECOMPUTED_SELECTOR_SET_AND_SPLIT_EVIDENCE_HARDENING"),
    (ROOT / "runs/phase6/v1_aggregation_contract_v7_20260806", "UNPOPULATED_SELECTOR_FAIL_CLOSED_HARDENING"),
)
DOMAIN_CONTRACT_SHA256 = "7ed99b905c3a1301d96101f357ab1fd9f4bc6e9a4922cb242d28e7cf06bb3bcf"
EXECUTION_CONTRACT_SHA256 = "25ad4b4e723edbd44651edaa63df415141de504b85288b12c2a6a973fcb420ab"
EXECUTION_MANIFEST_SHA256 = "1de9d445d888cbb5ddbf426cc062d2fb5128cad111437ce7d147df6e004aed48"
AGGREGATION_MODULE = ROOT / "src/schwgw/validation/phase6_aggregation.py"


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


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
    identity = source_file_identity(path, require_immutable=True)
    if path.read_bytes() != data:
        raise AggregationContractError(f"published bytes changed: {path}")
    return identity


def _new_root(path: Path) -> Path:
    root = path.absolute()
    if root.exists() or root.is_symlink() or root.parent.is_symlink() or not root.parent.is_dir():
        raise AggregationContractError(f"refusing to overwrite/alias evidence root: {root}")
    os.mkdir(root, 0o700)
    _fsync_directory(root.parent)
    return root


def _bound_identity(root: Path, files: tuple[str, ...], *, label: str) -> dict[str, object]:
    identities = validate_immutable_root(root, files=files)
    return {"root": str(root.absolute()), "files": identities, "label": label}


def bound_predecessors() -> dict[str, object]:
    domain = _bound_identity(
        BOUND_DOMAIN_ROOT,
        ("D_ext.jsonl", "D_prod.jsonl", "D_required.jsonl", "D_union.jsonl", "domain_contract.json", "manifest.json"),
        label="accepted_v3_domain",
    )
    execution = _bound_identity(
        BOUND_EXECUTION_ROOT,
        ("D_transition_calibration.jsonl", "D_external_direct_calibration.jsonl", "shard_inventory.jsonl", "execution_contract.json", "manifest.json"),
        label="accepted_v4_execution",
    )
    if domain["files"]["domain_contract.json"]["sha256"] != DOMAIN_CONTRACT_SHA256:
        raise AggregationContractError("v3 domain contract hash mismatch")
    if execution["files"]["execution_contract.json"]["sha256"] != EXECUTION_CONTRACT_SHA256 or execution["files"]["manifest.json"]["sha256"] != EXECUTION_MANIFEST_SHA256:
        raise AggregationContractError("v4 execution contract/manifest hash mismatch")
    return {"domain": domain, "execution": execution}


def contract_payload(predecessors: dict[str, object]) -> dict[str, object]:
    return {
        "bound_predecessors": predecessors,
        "contract_only": True,
        "consumed_aggregation_predecessors": [
            {
                "reason": f"SUPERSEDED_BEFORE_AUTHORITATIVE_RELEASE_{reason}",
                "root": str(root.absolute()),
                "files": validate_immutable_root(root, files=("aggregation_contract.json", "manifest.json")),
            }
            for root, reason in CONSUMED_AGGREGATION_ROOTS
        ],
        "global_green_permitted": False,
        "no_observable_pass_claimed": True,
        "schema": AGGREGATION_SCHEMA,
        "solver_runs": 0,
        "source_identities": {
            "aggregation_contract_module": source_file_identity(AGGREGATION_MODULE),
            "aggregation_contract_script": source_file_identity(Path(__file__).absolute()),
        },
        "status": "AGGREGATION_CONTRACT_FROZEN_NO_SOLVER_RUNS",
        "thresholds_calibrated": False,
        "validation_policy": {
            "aggregate_key_count": 17818,
            "extension_key_count": 1770,
            "observable_categories": [
                "s_complex_phase", "finite_radius_state", "flux_wronskian", "independent_backend_difference",
            ],
            "production_key_count": 16048,
            "shard_count": 86,
            "states": ["NOT_ASSESSED", "PARTIAL", "PASS", "FAIL"],
        },
    }


def _validate_frozen_root(root: Path) -> None:
    files = validate_immutable_root(root, files=("aggregation_contract.json", "manifest.json"))
    payload = json.loads((root / "aggregation_contract.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if payload.get("schema") != AGGREGATION_SCHEMA or payload.get("solver_runs") != 0 or payload.get("thresholds_calibrated") is not False or payload.get("no_observable_pass_claimed") is not True:
        raise AggregationContractError("contract-only policy changed")
    if manifest != {
        "contract": files["aggregation_contract.json"],
        "global_green_permitted": False,
        "schema": AGGREGATION_SCHEMA,
        "solver_runs": 0,
        "status": "AGGREGATION_CONTRACT_FROZEN_NO_SOLVER_RUNS",
    }:
        raise AggregationContractError("aggregation manifest mismatch")
    if payload.get("bound_predecessors") != bound_predecessors():
        raise AggregationContractError("bound predecessor identity changed")
    consumed = payload.get("consumed_aggregation_predecessors")
    if not isinstance(consumed, list) or len(consumed) != len(CONSUMED_AGGREGATION_ROOTS):
        raise AggregationContractError("consumed aggregation predecessor schema changed")
    expected_consumed = contract_payload(bound_predecessors())["consumed_aggregation_predecessors"]
    if consumed != expected_consumed:
        raise AggregationContractError("consumed aggregation predecessor identity changed")
    for label, identity in payload["source_identities"].items():
        actual = source_file_identity(Path(str(identity["path"])))
        if actual != identity:
            raise AggregationContractError(f"source identity mismatch: {label}")


def freeze_aggregation_contract(output_root: Path) -> dict[str, Any]:
    predecessors = bound_predecessors()
    payload = contract_payload(predecessors)
    root = _new_root(output_root)
    try:
        contract = _publish(root / "aggregation_contract.json", canonical_json_bytes(payload))
        manifest = {
            "contract": contract,
            "global_green_permitted": False,
            "schema": AGGREGATION_SCHEMA,
            "solver_runs": 0,
            "status": "AGGREGATION_CONTRACT_FROZEN_NO_SOLVER_RUNS",
        }
        manifest_identity = _publish(root / "manifest.json", canonical_json_bytes(manifest))
        os.chmod(root, 0o555)
        _fsync_directory(root)
        _fsync_directory(root.parent)
        _validate_frozen_root(root)
    except BaseException:
        for child in root.iterdir():
            if child.is_file():
                os.chmod(child, 0o444)
        os.chmod(root, 0o555)
        _fsync_directory(root)
        _fsync_directory(root.parent)
        raise
    return {"contract_sha256": contract["sha256"], "evidence_root": str(root),
            "manifest_sha256": manifest_identity["sha256"], "solver_runs": 0}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    print(json.dumps(freeze_aggregation_contract(args.output_root), sort_keys=True))


if __name__ == "__main__":
    main()
