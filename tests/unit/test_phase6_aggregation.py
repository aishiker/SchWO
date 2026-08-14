"""Adversarial coverage for Phase-6 aggregation evidence contracts."""

from __future__ import annotations

import os
import json
from pathlib import Path

import pytest

from schwgw.validation.phase6_aggregation import (
    AGGREGATE_SCHEMA, KEY_RESULT_SCHEMA, SHARD_RESULT_SCHEMA, SOLVER_ENVELOPE_SCHEMA,
    AggregationContractError, ExpectedContext, NORMALIZED_PAYLOAD_SCHEMA, sha256_bytes,
    source_file_identity, validate_aggregate_result, validate_component, validate_key_result,
    validate_shard_result, validate_subset_certificate,
)
from schwgw.validation.phase6_domain import RadialKey, canonical_json_bytes, jsonl_bytes
from schwgw.validation.phase6_execution_contract import ShardInventory


CONTEXT = ExpectedContext("a" * 64, "b" * 64, "c" * 64, "d" * 64)
ODD2, ODD3, EVEN2 = RadialKey("0.5", "odd", 2), RadialKey("0.5", "odd", 3), RadialKey("0.5", "even", 2)


def _frozen_json(tmp_path: Path, name: str, payload: object, *, writable_root: bool = False) -> dict[str, object]:
    root = tmp_path / name
    root.mkdir()
    path = root / "artifact.json"
    path.write_bytes(canonical_json_bytes(payload))
    os.chmod(path, 0o444)
    os.chmod(root, 0o755 if writable_root else 0o555)
    return source_file_identity(path, require_immutable=True)


def _frozen_bytes(tmp_path: Path, name: str, data: bytes) -> dict[str, object]:
    root = tmp_path / name
    root.mkdir()
    path = root / "artifact.jsonl"
    path.write_bytes(data)
    os.chmod(path, 0o444)
    os.chmod(root, 0o555)
    return source_file_identity(path, require_immutable=True)


def _fixed_policy(tmp_path: Path, value: str = "1", *, frozen: bool = True) -> dict[str, object]:
    payload = {"schema": "schwgw_phase6_fixed_target_policy_v1", "metric_class": "absolute_error", "metric_version": "v1", "threshold_name": "test-bound", "threshold_value": value, "frozen_before_calibration": frozen, "paper_agreement_gate": False, "global_green_permitted": False, "maximum_claim_state": "PASS", **CONTEXT.as_record()}
    return _frozen_json(tmp_path, f"policy-{len(list(tmp_path.iterdir()))}", payload)


def _threshold(tmp_path: Path, value: str = "1", *, writable_root: bool = False, selector: bool = False, frozen: bool = True) -> dict[str, object]:
    policy = _fixed_policy(tmp_path, value, frozen=frozen)
    payload = {"schema": "schwgw_phase6_threshold_artifact_v3", "kind": "FIXED_A_PRIORI", "metric_class": "absolute_error", "metric_version": "v1", "threshold_name": "test-bound", "threshold_value": value, "maximum_claim_state": "PASS", "fixed_target_policy_identity": policy, **CONTEXT.as_record()}
    if selector:
        payload["kind"] = "CALIBRATED_SELECTOR"
        payload["maximum_claim_state"] = "PARTIAL"
        payload["calibration_evidence_identity"] = _calibration_evidence(tmp_path, policy)
    return {"artifact_identity": _frozen_json(tmp_path, f"threshold-{len(list(tmp_path.iterdir()))}", payload, writable_root=writable_root), "name": "test-bound", "value": value, "metric_class": "absolute_error", "metric_version": "v1"}


def _calibration_evidence(tmp_path: Path, policy: dict[str, object], *, extension_sha: str = "ec41b9c7898344717f8d290525a2462461dc3614d7fb0b75fe5c8ae4b1e80bfe") -> dict[str, object]:
    def identity(name: str) -> dict[str, object]:
        return _frozen_json(tmp_path, f"cal-{name}-{len(list(tmp_path.iterdir()))}", {"schema": f"test_{name}_v1"})
    root = Path(__file__).resolve().parents[2]
    transition = source_file_identity(root / "runs/phase6/v1_execution_contract_v4_20260806/D_transition_calibration.jsonl", require_immutable=True)
    external = source_file_identity(root / "runs/phase6/v1_execution_contract_v4_20260806/D_external_direct_calibration.jsonl", require_immutable=True)
    extension = source_file_identity(root / "runs/phase6/v1_domain_freeze_v3_20260806/D_ext.jsonl", require_immutable=True)
    def decode(path: Path) -> set[RadialKey]:
        return {RadialKey.from_record(json.loads(line)) for line in path.read_text().splitlines()}
    transition_set, external_set = decode(Path(str(transition["path"]))), decode(Path(str(external["path"])))
    derived_keys = {"transition_external_overlap": tuple(sorted(transition_set & external_set, key=RadialKey.order_key)), "external_direct_only": tuple(sorted(external_set - transition_set, key=RadialKey.order_key)), "transition_only": tuple(sorted(transition_set - external_set, key=RadialKey.order_key))}
    def listing(name: str, keys: tuple[RadialKey, ...]) -> dict[str, object]:
        item = _frozen_bytes(tmp_path, f"{name}-{len(list(tmp_path.iterdir()))}", jsonl_bytes(keys))
        return {"identity": item, "sha256": item["sha256"], "count": len(keys), "sector_counts": {"odd": sum(key.sector == "odd" for key in keys), "even": sum(key.sector == "even" for key in keys)}}
    all_transition_only = derived_keys["transition_only"]
    fit = all_transition_only[:44]
    holdout = all_transition_only[44:90]
    quarantine = all_transition_only[90:]
    splits = {"fit": listing("fit", fit), "locked_holdout": listing("holdout", holdout), "quarantine": listing("quarantine", quarantine)}
    def typed(name: str, schema: str) -> dict[str, object]:
        return {"identity": _frozen_json(tmp_path, f"typed-{name}-{len(list(tmp_path.iterdir()))}", {"schema": schema, **CONTEXT.as_record()}), "expected_schema": schema, "role": name}
    support = {"schema": "schwgw_phase6_selector_support_hull_v1", "kM_min": "0.1", "kM_max": "4", "sectors": ["odd", "even"], "source_fit_key_list_sha256": splits["fit"]["sha256"], "transition_only_sha256": listing("transition-only-copy", all_transition_only)["sha256"], "out_of_support_policy": "NOT_ASSESSED", "domain_extension_frequencies": ["0.01", "0.05", "8"]}
    derived = {name: listing(name, keys) for name, keys in derived_keys.items()}
    support["transition_only_sha256"] = derived["transition_only"]["sha256"]
    payload = {"schema": "schwgw_phase6_selector_calibration_evidence_v1", **CONTEXT.as_record(), "calibration_status": "UNPOPULATED", "transition": {"sha256": transition["sha256"], "count": 158, "identity": transition}, "external_direct": {"sha256": external["sha256"], "count": 30, "identity": external}, "extension": {"sha256": extension_sha, "count": 1770, "identity": extension}, "derived_sets": derived, "split_identities": splits, "derivation_code_identity": identity("code"), "feature_schema": typed("feature", "schwgw_phase6_selector_feature_schema_v1"), "fixed_target_policy_identity": policy, "raw_evidence": typed("raw", "schwgw_phase6_calibration_raw_evidence_v1"), "checkpoint": typed("checkpoint", "schwgw_phase6_calibration_checkpoint_v1"), "backend_hashes": {"backend": "a" * 64}, "source_hashes": {"source": "b" * 64}, "config_hashes": {"config": "c" * 64}, "code_hashes": {"code": "d" * 64}, "support_hull_identity": _frozen_json(tmp_path, f"support-{len(list(tmp_path.iterdir()))}", support), "epsilon": "0.20", "delta": "0.10", "n_fit": splits["fit"]["sector_counts"], "no_self_use": True, "overlap_counted_once": True, "maximum_claim_state": "PARTIAL"}
    return _frozen_json(tmp_path, f"calibration-{len(list(tmp_path.iterdir()))}", payload)


def _component(tmp_path: Path, state: str = "NOT_ASSESSED", measured: str = "0", *, selector: bool = False) -> dict[str, object]:
    return {"state": state, "reason": "explicit test", "threshold": _threshold(tmp_path, selector=selector), "measured_value": measured, "metric": "absolute", "comparison": "LE", "coverage": "key"}


def _shard(*keys: RadialKey) -> ShardInventory:
    return ShardInventory("kM=0.5;sector=odd", "0.5", "odd", keys, len(keys), 0)


def _adapter(tmp_path: Path, key: RadialKey, shard: ShardInventory, *, parity: bool = False, empty: bool = False, payload_key: RadialKey | None = None, extra: bool = False) -> dict[str, object]:
    categories = {} if empty else {name: {"values": {"raw": "0"}} for name in ("s_complex_phase", "finite_radius_state", "flux_wronskian", "independent_backend_difference")}
    payload = {"schema": NORMALIZED_PAYLOAD_SCHEMA, "key": (payload_key or key).to_record(), "shard_id": shard.shard_id, "shard_key_list_sha256": shard.key_list_sha256, **CONTEXT.as_record(), "categories": categories}
    if extra:
        payload["paper_specific_stale_field"] = "forbidden"
    identity = _frozen_json(tmp_path, f"payload-{len(list(tmp_path.iterdir()))}", payload)
    return {"schema": SOLVER_ENVELOPE_SCHEMA, "key": key.to_record(), "shard_id": shard.shard_id, "shard_key_list_sha256": shard.key_list_sha256, **CONTEXT.as_record(), "independently_solved_sector": not parity, "provenance": {"transmission": "RESOLVED", "external_coverage": "INDEPENDENT", "even_solution": "PARITY_DERIVED" if parity else "INDEPENDENT"}, "solver_payload_identity": identity}


def _result(tmp_path: Path, key: RadialKey, shard: ShardInventory, *, state: str = "NOT_ASSESSED", parity: bool = False, empty: bool = False, payload_key: RadialKey | None = None, extra: bool = False) -> dict[str, object]:
    observables = {name: _component(tmp_path, state) for name in ("s_complex_phase", "finite_radius_state", "flux_wronskian", "independent_backend_difference")}
    numerical = {name: _component(tmp_path, state) for name in ("lmax", "r_in", "r_out", "jost_order", "ode_tolerance", "arithmetic_precision", "axis_limit", "backend_difference")}
    convention = {name: _component(tmp_path, state) for name in ("observer", "tetrad", "polarization_basis", "phase_origin", "total_scattered_definition")}
    return {"schema": KEY_RESULT_SCHEMA, "key": key.to_record(), "shard_id": shard.shard_id, "shard_key_list_sha256": shard.key_list_sha256, **CONTEXT.as_record(), "solver_adapter": _adapter(tmp_path, key, shard, parity=parity, empty=empty, payload_key=payload_key, extra=extra), "observables": observables, "numerical_budget": numerical, "convention_budget": convention, "acceptance_state": state}


def _certificate(tmp_path: Path, keys: tuple[RadialKey, ...], aggregate: dict[str, object], *, state: str = "NOT_ASSESSED") -> dict[str, object]:
    raw = jsonl_bytes(keys)
    observables = {name: _component(tmp_path, state) for name in ("s_complex_phase", "finite_radius_state", "flux_wronskian", "independent_backend_difference")}
    numerical = {name: _component(tmp_path, state) for name in ("lmax", "r_in", "r_out", "jost_order", "ode_tolerance", "arithmetic_precision", "axis_limit", "backend_difference")}
    convention = {name: _component(tmp_path, state) for name in ("observer", "tetrad", "polarization_basis", "phase_origin", "total_scattered_definition")}
    return {"schema": "schwgw_phase6_v1_subset_certificate_v2", "certificate_class": "FREQUENCY_SECTOR", "key_count": len(keys), "key_list_sha256": sha256_bytes(raw), "key_list_identity": _frozen_bytes(tmp_path, f"keys-{len(list(tmp_path.iterdir()))}", raw), "source_aggregate_identity": _frozen_json(tmp_path, f"aggregate-{len(list(tmp_path.iterdir()))}", aggregate), **CONTEXT.as_record(), "observable_states": observables, "numerical_budget": numerical, "convention_budget": convention, "derived_from_counts": False, "global_green_permitted": False, "acceptance_state": state}


def test_pass_cannot_contradict_threshold_comparison(tmp_path: Path) -> None:
    with pytest.raises(AggregationContractError, match="contradicts"):
        validate_component(_component(tmp_path, "PASS", "2"), label="test", context=CONTEXT)


def test_threshold_requires_immutable_direct_root(tmp_path: Path) -> None:
    component = _component(tmp_path)
    component["threshold"] = _threshold(tmp_path, writable_root=True)
    with pytest.raises(AggregationContractError, match="mode 0555"):
        validate_component(component, label="test", context=CONTEXT)


def test_empty_or_cross_key_adapter_is_rejected(tmp_path: Path) -> None:
    shard = _shard(ODD2)
    with pytest.raises(AggregationContractError, match="categories"):
        validate_key_result(_result(tmp_path, ODD2, shard, empty=True), expected_key=ODD2, expected_shard=shard, context=CONTEXT)
    result = _result(tmp_path, ODD2, shard, payload_key=ODD3)
    with pytest.raises(AggregationContractError, match="payload key/shard"):
        validate_key_result(result, expected_key=ODD2, expected_shard=shard, context=CONTEXT)
    with pytest.raises(AggregationContractError, match="payload schema changed"):
        validate_key_result(_result(tmp_path, ODD2, shard, extra=True), expected_key=ODD2, expected_shard=shard, context=CONTEXT)


def test_selector_provenance_rejects_forged_calibration_and_set_drift(tmp_path: Path) -> None:
    with pytest.raises(AggregationContractError, match="unpopulated selector"):
        validate_component(_component(tmp_path, "PASS", selector=True), label="selector", context=CONTEXT)
    policy = _fixed_policy(tmp_path)
    bad_evidence = _calibration_evidence(tmp_path, policy, extension_sha="d572c88259ef4b42b490af263d012a8de880458902dcf5a4d303c9f587cd466b")
    artifact = {"schema": "schwgw_phase6_threshold_artifact_v3", "kind": "CALIBRATED_SELECTOR", "metric_class": "absolute_error", "metric_version": "v1", "threshold_name": "test-bound", "threshold_value": "1", "maximum_claim_state": "PARTIAL", "fixed_target_policy_identity": policy, "calibration_evidence_identity": bad_evidence, **CONTEXT.as_record()}
    component = {"state": "PARTIAL", "reason": "test", "threshold": {"artifact_identity": _frozen_json(tmp_path, f"bad-artifact-{len(list(tmp_path.iterdir()))}", artifact), "name": "test-bound", "value": "1", "metric_class": "absolute_error", "metric_version": "v1"}, "measured_value": "0", "metric": "absolute", "comparison": "LE", "coverage": "key"}
    with pytest.raises(AggregationContractError, match="extension binding drift"):
        validate_component(component, label="selector", context=CONTEXT)


def test_threshold_policy_and_overlap_provenance_fail_closed(tmp_path: Path) -> None:
    policy = _fixed_policy(tmp_path, frozen=False)
    artifact = {"schema": "schwgw_phase6_threshold_artifact_v3", "kind": "FIXED_A_PRIORI", "metric_class": "absolute_error", "metric_version": "v1", "threshold_name": "test-bound", "threshold_value": "1", "maximum_claim_state": "PASS", "fixed_target_policy_identity": policy, **CONTEXT.as_record()}
    component = {"state": "PARTIAL", "reason": "test", "threshold": {"artifact_identity": _frozen_json(tmp_path, f"late-artifact-{len(list(tmp_path.iterdir()))}", artifact), "name": "test-bound", "value": "1", "metric_class": "absolute_error", "metric_version": "v1"}, "measured_value": "0", "metric": "absolute", "comparison": "LE", "coverage": "key"}
    with pytest.raises(AggregationContractError, match="fixed target policy semantics"):
        validate_component(component, label="fixed", context=CONTEXT)


def test_key_state_is_derived_and_parity_even_cannot_pass(tmp_path: Path) -> None:
    shard = _shard(ODD2)
    bad = _result(tmp_path, ODD2, shard)
    bad["acceptance_state"] = "PASS"
    with pytest.raises(AggregationContractError, match="not derived"):
        validate_key_result(bad, expected_key=ODD2, expected_shard=shard, context=CONTEXT)
    even_shard = ShardInventory("kM=0.5;sector=even", "0.5", "even", (EVEN2,), 1, 0)
    with pytest.raises(AggregationContractError, match="parity-derived"):
        validate_key_result(_result(tmp_path, EVEN2, even_shard, state="PASS", parity=True), expected_key=EVEN2, expected_shard=even_shard, context=CONTEXT)


def test_contract_only_forbids_pass(tmp_path: Path) -> None:
    shard = _shard(ODD2)
    with pytest.raises(AggregationContractError, match="contradicts"):
        validate_key_result(_result(tmp_path, ODD2, shard, state="PASS"), expected_key=ODD2, expected_shard=shard, context=CONTEXT, contract_only=True)


def test_shard_reloads_immutable_key_result_identities_in_order(tmp_path: Path) -> None:
    shard = _shard(ODD2, ODD3)
    first = _frozen_json(tmp_path, "result-one", _result(tmp_path, ODD2, shard))
    second = _frozen_json(tmp_path, "result-two", _result(tmp_path, ODD3, shard))
    record = {"schema": SHARD_RESULT_SCHEMA, "shard_id": shard.shard_id, "shard_key_list_sha256": shard.key_list_sha256, **CONTEXT.as_record(), "key_result_identities": [second, first], "state_counts": {"NOT_ASSESSED": 2, "PARTIAL": 0, "PASS": 0, "FAIL": 0}, "aggregate_key_order_sha256": sha256_bytes(jsonl_bytes(shard.keys)), "acceptance_state": "NOT_ASSESSED"}
    with pytest.raises(AggregationContractError, match="key/shard mismatch"):
        validate_shard_result(record, expected_shard=shard, context=CONTEXT)


def test_aggregate_rejects_fake_86_shard_count() -> None:
    from scripts.phase6_freeze_v1_execution_contract import load_bound_domain
    bundle, _ = load_bound_domain()
    fake = {"schema": AGGREGATE_SCHEMA, **CONTEXT.as_record(), "shard_result_identities": [], "membership_counts": {"production": 16048, "extension": 1770, "union": 17818}, "aggregate_key_order_sha256": sha256_bytes(jsonl_bytes(bundle.union)), "acceptance_state": "NOT_ASSESSED"}
    with pytest.raises(AggregationContractError, match="shard count"):
        validate_aggregate_result(fake, bundle=bundle, context=CONTEXT)


def test_certificate_must_bind_enumerated_subset_not_free_scope(tmp_path: Path) -> None:
    from scripts.phase6_freeze_v1_execution_contract import load_bound_domain
    bundle, _ = load_bound_domain()
    with pytest.raises(AggregationContractError, match="schema changed"):
        validate_subset_certificate({"schema": "x", "scope": "subset"}, bundle=bundle, context=CONTEXT)


def test_certificate_rejects_empty_and_out_of_union_subsets(tmp_path: Path) -> None:
    from scripts.phase6_freeze_v1_execution_contract import load_bound_domain
    bundle, _ = load_bound_domain()
    aggregate = {"schema": AGGREGATE_SCHEMA}
    with pytest.raises(AggregationContractError, match="canonical/enumerated"):
        validate_subset_certificate(_certificate(tmp_path, (), aggregate), bundle=bundle, context=CONTEXT)
    outside = RadialKey("0.1", "odd", 1000)
    with pytest.raises(AggregationContractError, match="outside D_union"):
        validate_subset_certificate(_certificate(tmp_path, (outside,), aggregate), bundle=bundle, context=CONTEXT)


def test_certificate_checks_source_context_and_derived_component_fold(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from schwgw.validation import phase6_aggregation as aggregation
    from scripts.phase6_freeze_v1_execution_contract import load_bound_domain
    bundle, _ = load_bound_domain()
    forged = {"schema": AGGREGATE_SCHEMA, **{name: "f" * 64 for name in CONTEXT.as_record()}, "shard_result_identities": [], "membership_counts": {"production": 16048, "extension": 1770, "union": 17818}, "aggregate_key_order_sha256": sha256_bytes(jsonl_bytes(bundle.union)), "acceptance_state": "NOT_ASSESSED"}
    with pytest.raises(AggregationContractError, match="context identity"):
        validate_subset_certificate(_certificate(tmp_path, (ODD2,), forged), bundle=bundle, context=CONTEXT)
    result = _result(tmp_path, ODD2, _shard(ODD2))
    monkeypatch.setattr(aggregation, "_aggregate_result_map", lambda *args, **kwargs: {ODD2: result})
    validish = {"schema": AGGREGATE_SCHEMA}
    with pytest.raises(AggregationContractError, match="component state is not derived"):
        validate_subset_certificate(_certificate(tmp_path, (ODD2,), validish, state="PASS"), bundle=bundle, context=CONTEXT)
