"""Focused tests for generic Phase-6 V1 execution-contract data only."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from schwgw.io.tablei_paper_inferred import DEFAULT_SOURCE_MERGE, load_uniform_source_contract
from schwgw.validation.phase6_domain import (
    RadialKey,
    build_v1_domain,
    canonical_json_bytes,
    jsonl_bytes,
    sha256_bytes,
    source_file_identity,
)
from schwgw.validation.phase6_execution_contract import (
    CHECKPOINT_SCHEMA,
    CONVENTION_BUDGET_FIELDS,
    EXPECTED_TRANSITION_KEY_LIST_SHA256,
    KEY_PAYLOAD_ENVELOPE_SCHEMA,
    NUMERICAL_BUDGET_FIELDS,
    ExecutionContractError,
    calibration_jsonl_bytes,
    execution_contract_payload,
    external_direct_calibration_keys,
    finite_response_radii_from_source,
    shard_inventory,
    resume_claims_sha256,
    transition_calibration_keys,
    validate_key_checkpoint,
    validate_resume_eligible,
    validate_shard_inventory,
)


def _bundle():
    schedule, _ = load_uniform_source_contract()
    return build_v1_domain(schedule)


def _checkpoint(tmp_path: Path):
    root = tmp_path / f"evidence-{len(list(tmp_path.iterdir()))}"
    root.mkdir()
    artifact = root / "immutable-result.json"
    payload_path = root / "solver-payload.json"
    keys = (RadialKey("0.1", "odd", 2), RadialKey("0.1", "odd", 3))
    shard = {
        "kM": "0.1",
        "key_count": len(keys),
        "key_list_sha256": sha256_bytes(jsonl_bytes(keys)),
        "sector": "odd",
        "shard_id": "kM=0.1;sector=odd",
    }
    checkpoint = {
        "acceptance_state": "PASS",
        "actual_precision": {"backend": "independent_backend", "digits": 80},
        "attempts": [{"attempt": 1, "status": "PASS"}],
        "backend_hashes": {"independent_backend": "f" * 64},
        "code_hashes": {"backend": "d" * 64},
        "config_hashes": {"execution": "e" * 64},
        "convention_budget": {
            "status": "PASS",
            "components": {name: 0.0 for name in CONVENTION_BUDGET_FIELDS},
        },
        "domain_contract_sha256": "a" * 64,
        "domain_union_key_list_sha256": "b" * 64,
        "execution_contract_sha256": "c" * 64,
        "execution_manifest_sha256": "d" * 64,
        "global_green_permitted": False,
        "key": {"ell": 2, "kM": "0.1", "sector": "odd"},
        "ladder": {
            "axis_map_sha256": sha256_bytes(canonical_json_bytes([
                {"actual_precision_digits": 80, "node_id": "baseline", "tolerance": 1e-8}
            ])),
            "failures": [],
            "nodes": [{"actual_precision_digits": 80, "node_id": "baseline", "status": "PASS", "tolerance": 1e-8}],
        },
        "numerical_budget": {
            "status": "PASS",
            "components": {name: 0.0 for name in NUMERICAL_BUDGET_FIELDS},
        },
        "observable_statuses": {"radial_s_matrix": "PASS", "flux": "PASS"},
        "provenance": {"legacy": False, "np": False, "pseudoinverse": False},
        "schema": CHECKPOINT_SCHEMA,
        "source_hashes": {"bound_domain": "a" * 64},
        "shard": shard,
    }
    checkpoint["result_identity"] = {"mode": 0o444, "nlink": 1, "path": "pending", "sha256": "0" * 64, "size": 1}
    payload = {
        name: checkpoint[name]
        for name in (
            "domain_contract_sha256", "domain_union_key_list_sha256",
            "execution_contract_sha256", "execution_manifest_sha256", "key", "shard",
        )
    }
    payload.update({
        "schema": KEY_PAYLOAD_ENVELOPE_SCHEMA,
        "solver_payload_schema": "schwgw_phase6_independent_mpmath_radial_backend_v1",
        "solver_payload": {
            "A_in": {"imag": "0", "real": "1"},
            "A_out": {"imag": "0", "real": "0"},
            "S": {"imag": "0", "real": "0"},
            "signed_flux": {"horizon": "-1", "infinity_in": "-1"},
            "schema_version": "schwgw_phase6_independent_mpmath_radial_backend_v1",
        },
    })
    payload_path.write_bytes(canonical_json_bytes(payload))
    payload_path.chmod(0o444)
    result = {
        name: checkpoint[name]
        for name in (
            "acceptance_state", "actual_precision", "domain_contract_sha256",
            "domain_union_key_list_sha256", "execution_contract_sha256",
            "execution_manifest_sha256", "key", "observable_statuses", "shard",
        )
    }
    result["schema"] = "schwgw_phase6_v1_key_result_v1"
    result["payload_schema"] = KEY_PAYLOAD_ENVELOPE_SCHEMA
    result["payload_identity"] = source_file_identity(payload_path)
    result["resume_claims_sha256"] = resume_claims_sha256(checkpoint)
    artifact.write_bytes(canonical_json_bytes(result))
    artifact.chmod(0o444)
    checkpoint["result_identity"] = source_file_identity(artifact)
    root.chmod(0o555)
    return checkpoint


def _context(checkpoint):
    keys = (RadialKey("0.1", "odd", 2), RadialKey("0.1", "odd", 3))
    return {
        "backend_hashes": {"independent_backend": "f" * 64},
        "code_hashes": {"backend": "d" * 64},
        "config_hashes": {"execution": "e" * 64},
        "domain_contract_sha256": "a" * 64,
        "domain_union_key_list_sha256": "b" * 64,
        "execution_contract_sha256": "c" * 64,
        "execution_manifest_sha256": "d" * 64,
        "ladder_axis_descriptors": [
            {"actual_precision_digits": 80, "node_id": "baseline", "tolerance": 1e-8}
        ],
        "ladder_axis_map_sha256": sha256_bytes(canonical_json_bytes([
            {"actual_precision_digits": 80, "node_id": "baseline", "tolerance": 1e-8}
        ])),
        "actual_precision": {"backend": "independent_backend", "digits": 80},
        "shard": {
            "kM": "0.1", "key_count": 2, "key_list_sha256": sha256_bytes(jsonl_bytes(keys)),
            "sector": "odd", "shard_id": "kM=0.1;sector=odd",
        },
        "shard_keys": [key.to_record() for key in keys],
        "source_hashes": {"bound_domain": "a" * 64},
        "evidence_root": str(Path(checkpoint["result_identity"]["path"]).parent),
    }


def test_transition_formula_order_cardinality_and_independent_hash() -> None:
    radii = finite_response_radii_from_source(Path(DEFAULT_SOURCE_MERGE))
    keys = transition_calibration_keys(radii)
    assert len(radii) == 8
    assert len(keys) == 158
    from schwgw.validation.phase6_domain import sha256_bytes

    assert sha256_bytes(calibration_jsonl_bytes(keys)) == EXPECTED_TRANSITION_KEY_LIST_SHA256
    assert keys[0].to_record() == {"ell": 2, "kM": "0.1", "sector": "odd"}
    assert keys[-1].to_record() == {"ell": 161, "kM": "4", "sector": "even"}


def test_external_direct_calibration_is_exact_separate_30_key_set() -> None:
    keys = external_direct_calibration_keys()
    assert len(keys) == 30
    assert {(key.kM, key.ell) for key in keys if key.kM == "0.5"} == {("0.5", 2)}
    assert {(key.kM, key.ell) for key in keys if key.kM == "2"} == {
        ("2", 60), ("2", 79), ("2", 80), ("2", 81), ("2", 153)
    }


def test_shards_are_exact_disjoint_86_partition_of_union() -> None:
    bundle = _bundle()
    shards = shard_inventory(bundle)
    validate_shard_inventory(shards, bundle)
    assert len(shards) == 86
    assert sum(item.production_key_count for item in shards) == 16048
    assert sum(item.extension_key_count for item in shards) == 1770
    assert sum(len(item.keys) for item in shards) == 17818
    assert all(item.production_key_count == 0 or item.extension_key_count == 0 for item in shards)


def test_contract_declares_per_key_and_per_shard_fail_closed_schemas() -> None:
    bundle = _bundle()
    transition = transition_calibration_keys(
        finite_response_radii_from_source(Path(DEFAULT_SOURCE_MERGE))
    )
    payload = execution_contract_payload(
        bound_domain={"domain_contract_sha256": "a" * 64},
        finite_radius_source={"source_identity": {"sha256": "b" * 64}},
        transition_keys=transition,
        external_keys=external_direct_calibration_keys(),
        shards=shard_inventory(bundle),
        source_identities={"test": {"sha256": "c" * 64}},
        consumed_execution_predecessors=[{"reason": "FIRST_EXECUTION_ROOT_CONSUMED_NON_AUTHORITATIVE"}],
    )
    schema = payload["checkpoint_resume_contract"]
    assert schema["key_checkpoint_schema"] == CHECKPOINT_SCHEMA
    assert schema["shard_checkpoint_schema"] == "schwgw_phase6_v1_shard_checkpoint_v1"
    assert "source_hashes" in schema["shard_required_fields"]
    assert payload["domain_acceptance"]["global_green_permitted"] is False


def test_checkpoint_resume_accepts_only_exact_pass_identity(tmp_path: Path) -> None:
    checkpoint = _checkpoint(tmp_path)
    path = Path(checkpoint["result_identity"]["path"])
    validate_key_checkpoint(checkpoint, expected_context=_context(checkpoint), result_path=path)
    validate_resume_eligible(checkpoint, expected_context=_context(checkpoint), result_path=path)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda item: item.__setitem__("domain_contract_sha256", "x" * 64),
        lambda item: item["result_identity"].__setitem__("path", ""),
        lambda item: item["result_identity"].__setitem__("nlink", 2),
        lambda item: item.__setitem__("schema", "legacy_schema"),
        lambda item: item["observable_statuses"].__setitem__("flux", "GREEN"),
        lambda item: item["numerical_budget"]["components"].pop("lmax"),
        lambda item: item.__setitem__("global_green_permitted", True),
        lambda item: item["provenance"].__setitem__("np", True),
    ],
)
def test_checkpoint_tampering_rejects(mutate, tmp_path: Path) -> None:
    checkpoint = deepcopy(_checkpoint(tmp_path))
    mutate(checkpoint)
    with pytest.raises(ExecutionContractError):
        validate_key_checkpoint(
            checkpoint,
            expected_context=_context(checkpoint),
            result_path=Path(checkpoint["result_identity"]["path"]),
        )


def test_resume_rejects_partial_and_failed_numerical_budget(tmp_path: Path) -> None:
    checkpoint = _checkpoint(tmp_path)
    checkpoint["acceptance_state"] = "PARTIAL"
    with pytest.raises(ExecutionContractError):
        validate_resume_eligible(checkpoint, expected_context=_context(checkpoint), result_path=Path(checkpoint["result_identity"]["path"]))


def test_checkpoint_rejects_valid_looking_wrong_hash_and_path_alias(tmp_path: Path) -> None:
    checkpoint = _checkpoint(tmp_path)
    checkpoint["code_hashes"]["backend"] = "9" * 64
    with pytest.raises(ExecutionContractError, match="code_hashes mismatch"):
        validate_key_checkpoint(
            checkpoint, expected_context=_context(checkpoint), result_path=Path(checkpoint["result_identity"]["path"])
        )
    checkpoint = _checkpoint(tmp_path)
    alias = tmp_path / "copied-result.json"
    alias.write_bytes(Path(checkpoint["result_identity"]["path"]).read_bytes())
    alias.chmod(0o444)
    checkpoint["result_identity"] = source_file_identity(alias)
    with pytest.raises(ExecutionContractError):
        validate_key_checkpoint(
            checkpoint, expected_context=_context(checkpoint), result_path=Path(checkpoint["result_identity"]["path"])
        )


def test_checkpoint_rejects_hardlinked_artifact(tmp_path: Path) -> None:
    checkpoint = _checkpoint(tmp_path)
    artifact = Path(checkpoint["result_identity"]["path"])
    alias = tmp_path / "hardlink-result.json"
    alias.hardlink_to(artifact)
    with pytest.raises(ExecutionContractError):
        validate_key_checkpoint(checkpoint, expected_context=_context(checkpoint), result_path=alias)


def test_checkpoint_rejects_ladder_mismatch(tmp_path: Path) -> None:
    checkpoint = _checkpoint(tmp_path)
    checkpoint["ladder"]["nodes"][0]["node_id"] = "wrong-node"
    with pytest.raises(ExecutionContractError, match="ladder node order"):
        validate_key_checkpoint(
            checkpoint, expected_context=_context(checkpoint), result_path=Path(checkpoint["result_identity"]["path"])
        )


def test_checkpoint_rejects_wrong_valid_ladder_tolerance_or_precision(tmp_path: Path) -> None:
    checkpoint = _checkpoint(tmp_path)
    checkpoint["ladder"]["nodes"][0]["tolerance"] = 2e-8
    with pytest.raises(ExecutionContractError, match="descriptor differs"):
        validate_key_checkpoint(
            checkpoint, expected_context=_context(checkpoint), result_path=Path(checkpoint["result_identity"]["path"])
        )
    checkpoint = _checkpoint(tmp_path)
    checkpoint["actual_precision"]["digits"] = 81
    with pytest.raises(ExecutionContractError, match="actual precision differs"):
        validate_key_checkpoint(
            checkpoint, expected_context=_context(checkpoint), result_path=Path(checkpoint["result_identity"]["path"])
        )


def test_resume_rejects_nonpass_ladder_node(tmp_path: Path) -> None:
    checkpoint = _checkpoint(tmp_path)
    checkpoint["ladder"]["nodes"][0]["status"] = "PARTIAL"
    with pytest.raises(ExecutionContractError, match="resume claims"):
        validate_resume_eligible(
            checkpoint, expected_context=_context(checkpoint), result_path=Path(checkpoint["result_identity"]["path"])
        )


def test_checkpoint_claim_hash_rejects_budget_or_attempt_tampering(tmp_path: Path) -> None:
    checkpoint = _checkpoint(tmp_path)
    checkpoint["numerical_budget"]["components"]["lmax"] = 1e-6
    with pytest.raises(ExecutionContractError, match="resume claims"):
        validate_key_checkpoint(
            checkpoint, expected_context=_context(checkpoint), result_path=Path(checkpoint["result_identity"]["path"])
        )
    checkpoint = _checkpoint(tmp_path)
    checkpoint["attempts"][0]["status"] = "PARTIAL"
    with pytest.raises(ExecutionContractError, match="resume claims"):
        validate_key_checkpoint(
            checkpoint, expected_context=_context(checkpoint), result_path=Path(checkpoint["result_identity"]["path"])
        )


def test_result_requires_direct_0555_non_symlink_evidence_root(tmp_path: Path) -> None:
    checkpoint = _checkpoint(tmp_path)
    root = Path(checkpoint["result_identity"]["path"]).parent
    root.chmod(0o755)
    with pytest.raises(ExecutionContractError, match="0555"):
        validate_key_checkpoint(
            checkpoint, expected_context=_context(checkpoint), result_path=Path(checkpoint["result_identity"]["path"])
        )
    root.chmod(0o555)
    alias = tmp_path / "symlinked-evidence"
    alias.symlink_to(root, target_is_directory=True)
    context = _context(checkpoint)
    context["evidence_root"] = str(alias)
    with pytest.raises(ExecutionContractError, match="0555"):
        validate_key_checkpoint(
            checkpoint, expected_context=context, result_path=Path(checkpoint["result_identity"]["path"])
        )


def test_result_artifact_requires_0444_and_canonical_linked_json(tmp_path: Path) -> None:
    checkpoint = _checkpoint(tmp_path)
    artifact = Path(checkpoint["result_identity"]["path"])
    artifact.chmod(0o644)
    checkpoint["result_identity"] = source_file_identity(artifact)
    with pytest.raises(ExecutionContractError, match="mode must be 0444"):
        validate_key_checkpoint(checkpoint, expected_context=_context(checkpoint), result_path=artifact)
    root = artifact.parent
    root.chmod(0o755)
    artifact.write_bytes(b"{}\n")
    artifact.chmod(0o444)
    checkpoint["result_identity"] = source_file_identity(artifact)
    root.chmod(0o555)
    with pytest.raises(ExecutionContractError, match="result artifact schema"):
        validate_key_checkpoint(checkpoint, expected_context=_context(checkpoint), result_path=artifact)


def test_payload_envelope_rejects_cross_key_substitution(tmp_path: Path) -> None:
    checkpoint = _checkpoint(tmp_path)
    result_path = Path(checkpoint["result_identity"]["path"])
    root = result_path.parent
    payload_path = root / "solver-payload.json"
    root.chmod(0o755)
    payload_path.chmod(0o644)
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    payload["key"] = {"ell": 3, "kM": "0.1", "sector": "odd"}
    payload_path.write_bytes(canonical_json_bytes(payload))
    payload_path.chmod(0o444)
    result_path.chmod(0o644)
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result["payload_identity"] = source_file_identity(payload_path)
    result_path.write_bytes(canonical_json_bytes(result))
    result_path.chmod(0o444)
    checkpoint["result_identity"] = source_file_identity(result_path)
    root.chmod(0o555)
    with pytest.raises(ExecutionContractError, match="payload key linkage"):
        validate_key_checkpoint(
            checkpoint, expected_context=_context(checkpoint), result_path=result_path
        )


def test_resume_rejects_convention_or_observable_failure(tmp_path: Path) -> None:
    checkpoint = _checkpoint(tmp_path)
    checkpoint["convention_budget"]["status"] = "PARTIAL"
    with pytest.raises(ExecutionContractError, match="resume claims"):
        validate_resume_eligible(
            checkpoint, expected_context=_context(checkpoint), result_path=Path(checkpoint["result_identity"]["path"])
        )
    checkpoint = _checkpoint(tmp_path)
    checkpoint["observable_statuses"]["flux"] = "FAIL"
    with pytest.raises(ExecutionContractError, match="observable"):
        validate_resume_eligible(
            checkpoint, expected_context=_context(checkpoint), result_path=Path(checkpoint["result_identity"]["path"])
        )
    checkpoint = _checkpoint(tmp_path)
    checkpoint["numerical_budget"]["status"] = "FAIL"
    with pytest.raises(ExecutionContractError, match="resume claims"):
        validate_resume_eligible(checkpoint, expected_context=_context(checkpoint), result_path=Path(checkpoint["result_identity"]["path"]))
