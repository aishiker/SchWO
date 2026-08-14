"""Fail-closed generic Phase-6 V1 aggregation and evidence contracts.

No solver is imported here.  This module accepts only immutable, canonical
evidence whose key, domain, execution, threshold, and result identities can
all be reloaded and rechecked.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
import hashlib
import json
import stat

from schwgw.validation.phase6_domain import (
    DomainBundle, RadialKey, canonical_json_bytes, jsonl_bytes,
    validate_ordered_unique_keys,
)
from schwgw.validation.phase6_execution_contract import ShardInventory, shard_inventory


AGGREGATION_SCHEMA = "schwgw_phase6_v1_aggregation_contract_v1"
SOLVER_ENVELOPE_SCHEMA = "schwgw_phase6_v1_solver_adapter_envelope_v2"
NORMALIZED_PAYLOAD_SCHEMA = "schwgw_phase6_v1_normalized_solver_payload_v1"
KEY_RESULT_SCHEMA = "schwgw_phase6_v1_aggregation_key_result_v2"
SHARD_RESULT_SCHEMA = "schwgw_phase6_v1_aggregation_shard_result_v2"
SHARD_CHECKPOINT_SCHEMA = "schwgw_phase6_v1_aggregation_shard_checkpoint_v2"
AGGREGATE_SCHEMA = "schwgw_phase6_v1_aggregate_result_v2"
CERTIFICATE_SCHEMA = "schwgw_phase6_v1_subset_certificate_v2"
STATES = ("NOT_ASSESSED", "PARTIAL", "PASS", "FAIL")
COMPARISONS = ("LE", "LT", "GE", "GT", "EQ")
OBSERVABLES = ("s_complex_phase", "finite_radius_state", "flux_wronskian", "independent_backend_difference")
NUMERICAL_BUDGETS = ("lmax", "r_in", "r_out", "jost_order", "ode_tolerance", "arithmetic_precision", "axis_limit", "backend_difference")
CONVENTION_BUDGETS = ("observer", "tetrad", "polarization_basis", "phase_origin", "total_scattered_definition")
CERTIFICATE_CLASSES = ("FREQUENCY_SECTOR", "CALIBRATION_CLASS", "DOMAIN_EXTENSION")
THRESHOLD_ARTIFACT_SCHEMA = "schwgw_phase6_threshold_artifact_v3"
FIXED_TARGET_POLICY_SCHEMA = "schwgw_phase6_fixed_target_policy_v1"
CALIBRATION_EVIDENCE_SCHEMA = "schwgw_phase6_selector_calibration_evidence_v1"
TRANSITION_SHA256 = "942fce669ee62f8194859f0481f7f3e926f4771176ec627d9013cda610dcb951"
EXTERNAL_DIRECT_SHA256 = "d572c88259ef4b42b490af263d012a8de880458902dcf5a4d303c9f587cd466b"
EXTENSION_SHA256 = "ec41b9c7898344717f8d290525a2462461dc3614d7fb0b75fe5c8ae4b1e80bfe"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRANSITION_PATH = PROJECT_ROOT / "runs/phase6/v1_execution_contract_v4_20260806/D_transition_calibration.jsonl"
EXTERNAL_DIRECT_PATH = PROJECT_ROOT / "runs/phase6/v1_execution_contract_v4_20260806/D_external_direct_calibration.jsonl"


class AggregationContractError(ValueError):
    """Raised for stale, noncanonical, incomplete, or contradictory evidence."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _exact(value: object, fields: set[str], label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != fields:
        raise AggregationContractError(f"{label} schema changed")
    return value


def _decimal(value: object, label: str) -> Decimal:
    if not isinstance(value, str) or not value or "e" in value.lower() or value.startswith("+"):
        raise AggregationContractError(f"{label} must be a canonical finite decimal string")
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise AggregationContractError(f"{label} is not decimal") from exc
    if not parsed.is_finite() or format(parsed, "f") != value:
        raise AggregationContractError(f"{label} must be a canonical finite decimal string")
    return parsed


def _state(value: object, label: str) -> str:
    if value not in STATES:
        raise AggregationContractError(f"{label} has invalid state")
    return str(value)


def _key(value: object, label: str) -> RadialKey:
    if not isinstance(value, Mapping):
        raise AggregationContractError(f"{label} key is not a mapping")
    try:
        return RadialKey.from_record(value)
    except ValueError as exc:
        raise AggregationContractError(f"{label} key is invalid") from exc


def source_file_identity(path: str | Path, *, require_immutable: bool = False) -> dict[str, object]:
    """Identity of a direct regular file, rejecting every symlink component."""

    absolute = Path(path).absolute()
    if any(item.is_symlink() for item in (absolute, *absolute.parents)):
        raise AggregationContractError("source path has a symlink component")
    resolved = absolute.resolve(strict=True)
    if resolved != absolute:
        raise AggregationContractError("source path resolves through an alias")
    info = resolved.lstat()
    mode = stat.S_IMODE(info.st_mode)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise AggregationContractError("source is not a regular nlink1 file")
    if require_immutable and mode != 0o444:
        raise AggregationContractError("evidence file is not mode 0444")
    return {"mode": mode, "nlink": info.st_nlink, "path": str(resolved), "sha256": sha256_bytes(resolved.read_bytes()), "size": info.st_size}


def _identity(value: object, label: str, *, immutable: bool = False, root_immutable: bool = False) -> Mapping[str, object]:
    identity = _exact(value, {"mode", "nlink", "path", "sha256", "size"}, label)
    if not all(isinstance(identity[name], expected) for name, expected in (("path", str), ("sha256", str), ("size", int), ("mode", int), ("nlink", int))) or len(str(identity["sha256"])) != 64:
        raise AggregationContractError(f"{label} identity types changed")
    actual = source_file_identity(Path(str(identity["path"])), require_immutable=immutable)
    if actual != identity:
        raise AggregationContractError(f"{label} identity no longer matches bytes")
    if root_immutable:
        parent = Path(str(identity["path"])).parent
        if parent.is_symlink() or stat.S_IMODE(parent.lstat().st_mode) != 0o555:
            raise AggregationContractError(f"{label} parent is not direct mode 0555")
    return identity


def validate_immutable_root(root: str | Path, *, files: Sequence[str]) -> dict[str, Mapping[str, object]]:
    path = Path(root).absolute()
    if path.is_symlink() or path.resolve(strict=True) != path or stat.S_IMODE(path.lstat().st_mode) != 0o555:
        raise AggregationContractError("evidence root is not direct mode 0555")
    if set(child.name for child in path.iterdir()) != set(files):
        raise AggregationContractError("evidence root has unexpected or missing files")
    return {name: _identity(source_file_identity(path / name, require_immutable=True), name, immutable=True, root_immutable=True) for name in files}


def _load_json(identity: object, label: str, *, schema: str) -> Mapping[str, object]:
    verified = _identity(identity, label, immutable=True, root_immutable=True)
    raw = Path(str(verified["path"])).read_bytes()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AggregationContractError(f"{label} is not JSON") from exc
    if not isinstance(payload, Mapping) or canonical_json_bytes(payload) != raw or payload.get("schema") != schema:
        raise AggregationContractError(f"{label} is not canonical expected-schema JSON")
    return payload


def _load_key_jsonl(identity: object, label: str) -> tuple[tuple[RadialKey, ...], Mapping[str, object]]:
    verified = _identity(identity, label, immutable=True, root_immutable=True)
    raw = Path(str(verified["path"])).read_bytes()
    if not raw.endswith(b"\n"):
        raise AggregationContractError(f"{label} lacks final LF")
    try:
        keys = tuple(_key(json.loads(line), label) for line in raw.splitlines())
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise AggregationContractError(f"{label} is not radial-key JSONL") from exc
    try:
        validate_ordered_unique_keys(keys)
    except ValueError as exc:
        raise AggregationContractError(f"{label} is not ordered unique") from exc
    if jsonl_bytes(keys) != raw:
        raise AggregationContractError(f"{label} is not canonical JSONL")
    return keys, verified


def _sector_counts(keys: Sequence[RadialKey]) -> dict[str, int]:
    return {"odd": sum(key.sector == "odd" for key in keys), "even": sum(key.sector == "even" for key in keys)}


def _derived_set_record(value: object, label: str, expected: set[RadialKey]) -> None:
    record = _exact(value, {"identity", "sha256", "count", "sector_counts"}, label)
    keys, identity = _load_key_jsonl(record["identity"], label)
    if set(keys) != expected or len(keys) != len(expected) or record["sha256"] != identity["sha256"] or record["count"] != len(keys) or record["sector_counts"] != _sector_counts(keys):
        raise AggregationContractError(f"{label} bytes/count/sector drift")


def _comparison(measured: Decimal, threshold: Decimal, comparison: str) -> bool:
    return {"LE": measured <= threshold, "LT": measured < threshold, "GE": measured >= threshold, "GT": measured > threshold, "EQ": measured == threshold}[comparison]


def _validate_fixed_target_policy(value: object, context: "ExpectedContext") -> Mapping[str, object]:
    policy = _load_json(value, "fixed target policy", schema=FIXED_TARGET_POLICY_SCHEMA)
    fields = {"schema", "metric_class", "metric_version", "threshold_name", "threshold_value", "frozen_before_calibration", "paper_agreement_gate", "global_green_permitted", "maximum_claim_state", *context.as_record()}
    policy = _exact(policy, fields, "fixed target policy")
    _context(policy, context)
    if not all(isinstance(policy[name], str) and policy[name] for name in ("metric_class", "metric_version", "threshold_name")) or _decimal(policy["threshold_value"], "fixed target value") is None or policy["frozen_before_calibration"] is not True or policy["paper_agreement_gate"] is not False or policy["global_green_permitted"] is not False or policy["maximum_claim_state"] not in ("PASS", "PARTIAL"):
        raise AggregationContractError("fixed target policy semantics changed")
    return policy


def _validate_calibration_evidence(value: object, context: "ExpectedContext", fixed_identity: object) -> Mapping[str, object]:
    evidence = _load_json(value, "selector calibration evidence", schema=CALIBRATION_EVIDENCE_SCHEMA)
    fields = {"schema", *context.as_record(), "calibration_status", "transition", "external_direct", "extension", "derived_sets", "split_identities", "derivation_code_identity", "feature_schema", "fixed_target_policy_identity", "raw_evidence", "checkpoint", "backend_hashes", "source_hashes", "config_hashes", "code_hashes", "support_hull_identity", "epsilon", "delta", "n_fit", "no_self_use", "overlap_counted_once", "maximum_claim_state"}
    evidence = _exact(evidence, fields, "selector calibration evidence")
    _context(evidence, context)
    for name, digest, count in (("transition", TRANSITION_SHA256, 158), ("external_direct", EXTERNAL_DIRECT_SHA256, 30), ("extension", EXTENSION_SHA256, 1770)):
        record = _exact(evidence[name], {"sha256", "count", "identity"}, f"selector {name}")
        if record["sha256"] != digest or record["count"] != count or _identity(record["identity"], f"selector {name} identity", immutable=True, root_immutable=True)["sha256"] != digest:
            raise AggregationContractError(f"selector {name} binding drift")
    transition_keys, _ = _load_key_jsonl(evidence["transition"]["identity"], "frozen transition")
    external_keys, _ = _load_key_jsonl(evidence["external_direct"]["identity"], "frozen external-direct")
    if Path(str(evidence["transition"]["identity"]["path"])) != TRANSITION_PATH or Path(str(evidence["external_direct"]["identity"]["path"])) != EXTERNAL_DIRECT_PATH:
        raise AggregationContractError("selector calibration source path drift")
    transition, external = set(transition_keys), set(external_keys)
    derived = evidence["derived_sets"]
    if not isinstance(derived, Mapping) or set(derived) != {"transition_external_overlap", "external_direct_only", "transition_only"}:
        raise AggregationContractError("selector derived-set schema changed")
    _derived_set_record(derived["transition_external_overlap"], "transition/external overlap", transition & external)
    _derived_set_record(derived["external_direct_only"], "external-direct only", external - transition)
    _derived_set_record(derived["transition_only"], "transition only", transition - external)
    transition_only = transition - external
    if evidence["fixed_target_policy_identity"] != fixed_identity:
        raise AggregationContractError("selector fixed-target identity mismatch")
    _identity(evidence["derivation_code_identity"], "selector derivation code", immutable=True, root_immutable=True)
    for name, schema in (("feature_schema", "schwgw_phase6_selector_feature_schema_v1"), ("raw_evidence", "schwgw_phase6_calibration_raw_evidence_v1"), ("checkpoint", "schwgw_phase6_calibration_checkpoint_v1")):
        typed = _exact(evidence[name], {"identity", "expected_schema", "role"}, f"selector {name}")
        if typed["expected_schema"] != schema or not isinstance(typed["role"], str) or not typed["role"]:
            raise AggregationContractError(f"selector {name} typed identity changed")
        loaded = _load_json(typed["identity"], f"selector {name}", schema=schema)
        _context(loaded, context)
    splits = evidence["split_identities"]
    if not isinstance(splits, Mapping) or set(splits) != {"fit", "locked_holdout", "quarantine"}:
        raise AggregationContractError("selector split identity schema changed")
    split_sets: list[set[RadialKey]] = []
    split_counts: dict[str, dict[str, int]] = {}
    for name, record in splits.items():
        record = _exact(record, {"identity", "sha256", "count", "sector_counts"}, f"selector split {name}")
        keys, identity = _load_key_jsonl(record["identity"], f"selector split {name}")
        sectors = record["sector_counts"]
        if record["sha256"] != identity["sha256"] or not isinstance(record["count"], int) or record["count"] < 1 or not isinstance(sectors, Mapping) or _sector_counts(keys) != sectors or not set(keys) <= transition_only:
            raise AggregationContractError(f"selector split {name} binding/count drift")
        split_sets.append(set(keys))
        split_counts[name] = _sector_counts(keys)
    if any(left & right for index, left in enumerate(split_sets) for right in split_sets[index + 1:]) or set().union(*split_sets) != transition_only:
        raise AggregationContractError("selector split partition drift")
    for name in ("backend_hashes", "source_hashes", "config_hashes", "code_hashes"):
        mapping = evidence[name]
        if not isinstance(mapping, Mapping) or not mapping or any(not isinstance(key, str) or len(str(value)) != 64 for key, value in mapping.items()):
            raise AggregationContractError(f"selector {name} missing")
    support = _load_json(evidence["support_hull_identity"], "selector support hull", schema="schwgw_phase6_selector_support_hull_v1")
    expected_support = {"schema": "schwgw_phase6_selector_support_hull_v1", "kM_min": "0.1", "kM_max": "4", "sectors": ["odd", "even"], "source_fit_key_list_sha256": splits["fit"]["sha256"], "transition_only_sha256": derived["transition_only"]["sha256"], "out_of_support_policy": "NOT_ASSESSED", "domain_extension_frequencies": ["0.01", "0.05", "8"]}
    n_fit = evidence["n_fit"]
    if support != expected_support or _decimal(evidence["epsilon"], "selector epsilon") != Decimal("0.20") or _decimal(evidence["delta"], "selector delta") != Decimal("0.10") or n_fit != split_counts["fit"] or any(not isinstance(n_fit[sector], int) or n_fit[sector] < 20 for sector in ("odd", "even")) or evidence["no_self_use"] is not True or evidence["overlap_counted_once"] is not True or evidence["maximum_claim_state"] != "PARTIAL":
        raise AggregationContractError("selector calibration semantics changed")
    if evidence["calibration_status"] not in ("UNPOPULATED", "POPULATED"):
        raise AggregationContractError("selector calibration status changed")
    return evidence


def validate_component(record: object, *, label: str, context: "ExpectedContext", contract_only: bool = False) -> Mapping[str, object]:
    fields = {"state", "reason", "threshold", "measured_value", "metric", "comparison", "coverage"}
    item = _exact(record, fields, label)
    state = _state(item["state"], label)
    if not all(isinstance(item[name], str) and item[name] for name in ("reason", "metric", "coverage")):
        raise AggregationContractError(f"{label} lacks explicit reason/metric/coverage")
    comparison = item["comparison"]
    if comparison not in COMPARISONS:
        raise AggregationContractError(f"{label} comparison vocabulary changed")
    measured, threshold_value = _decimal(item["measured_value"], f"{label} measured value"), None
    threshold = _exact(item["threshold"], {"artifact_identity", "name", "value", "metric_class", "metric_version"}, label)
    threshold_value = _decimal(threshold["value"], f"{label} threshold value")
    if not all(isinstance(threshold[name], str) and threshold[name] for name in ("name", "metric_class", "metric_version")):
        raise AggregationContractError(f"{label} threshold provenance changed")
    artifact = _load_json(threshold["artifact_identity"], f"{label} threshold artifact", schema=THRESHOLD_ARTIFACT_SCHEMA)
    base = {"schema", "kind", "metric_class", "metric_version", "threshold_name", "threshold_value", "maximum_claim_state", "fixed_target_policy_identity", *context.as_record()}
    if artifact.get("kind") == "FIXED_A_PRIORI":
        artifact = _exact(artifact, base, f"{label} threshold artifact")
    elif artifact.get("kind") == "CALIBRATED_SELECTOR":
        artifact = _exact(artifact, base | {"calibration_evidence_identity"}, f"{label} threshold artifact")
    else:
        raise AggregationContractError(f"{label} threshold artifact kind changed")
    _context(artifact, context)
    if {"metric_class": artifact["metric_class"], "metric_version": artifact["metric_version"], "threshold_name": artifact["threshold_name"], "threshold_value": artifact["threshold_value"]} != {"metric_class": threshold["metric_class"], "metric_version": threshold["metric_version"], "threshold_name": threshold["name"], "threshold_value": threshold["value"]} or artifact["maximum_claim_state"] not in ("PASS", "PARTIAL"):
        raise AggregationContractError(f"{label} threshold artifact binding mismatch")
    policy = _validate_fixed_target_policy(artifact["fixed_target_policy_identity"], context)
    if policy["metric_class"] != artifact["metric_class"] or policy["metric_version"] != artifact["metric_version"] or policy["threshold_name"] != artifact["threshold_name"] or policy["threshold_value"] != artifact["threshold_value"]:
        raise AggregationContractError(f"{label} fixed target policy binding mismatch")
    if artifact["kind"] == "CALIBRATED_SELECTOR":
        calibration = _validate_calibration_evidence(artifact["calibration_evidence_identity"], context, artifact["fixed_target_policy_identity"])
        if calibration["calibration_status"] != "POPULATED":
            raise AggregationContractError("unpopulated selector calibration cannot create an artifact")
        if artifact["maximum_claim_state"] != "PARTIAL":
            raise AggregationContractError("calibrated selector cannot claim PASS")
    elif artifact["maximum_claim_state"] != policy["maximum_claim_state"]:
        raise AggregationContractError("fixed target claim state mismatch")
    eligible = _comparison(measured, threshold_value, str(comparison))
    if state == "PASS" and (contract_only or not eligible or artifact["maximum_claim_state"] != "PASS"):
        raise AggregationContractError(f"{label} PASS contradicts calibrated threshold comparison")
    return item


def validate_component_map(records: object, names: Sequence[str], *, label: str, context: "ExpectedContext", contract_only: bool = False) -> Mapping[str, Mapping[str, object]]:
    if not isinstance(records, Mapping) or set(records) != set(names):
        raise AggregationContractError(f"{label} component names changed")
    return {name: validate_component(records[name], label=f"{label}.{name}", context=context, contract_only=contract_only) for name in names}


@dataclass(frozen=True)
class ExpectedContext:
    domain_contract_sha256: str
    domain_union_key_list_sha256: str
    execution_contract_sha256: str
    execution_manifest_sha256: str

    def as_record(self) -> dict[str, str]:
        return {"domain_contract_sha256": self.domain_contract_sha256, "domain_union_key_list_sha256": self.domain_union_key_list_sha256, "execution_contract_sha256": self.execution_contract_sha256, "execution_manifest_sha256": self.execution_manifest_sha256}


def _context(record: Mapping[str, object], context: ExpectedContext) -> None:
    if any(record.get(name) != value for name, value in context.as_record().items()):
        raise AggregationContractError("context identity mismatch")


def validate_solver_adapter_envelope(envelope: object, *, expected_key: RadialKey, expected_shard: ShardInventory, context: ExpectedContext) -> Mapping[str, object]:
    fields = {"schema", "key", "shard_id", "shard_key_list_sha256", *context.as_record(), "independently_solved_sector", "provenance", "solver_payload_identity"}
    item = _exact(envelope, fields, "solver adapter envelope")
    if item["schema"] != SOLVER_ENVELOPE_SCHEMA or _key(item["key"], "adapter") != expected_key or item["shard_id"] != expected_shard.shard_id or item["shard_key_list_sha256"] != expected_shard.key_list_sha256 or not isinstance(item["independently_solved_sector"], bool):
        raise AggregationContractError("solver adapter key/shard provenance mismatch")
    _context(item, context)
    provenance = _exact(item["provenance"], {"transmission", "external_coverage", "even_solution"}, "solver provenance")
    if provenance["transmission"] not in ("RESOLVED", "UNRESOLVED") or provenance["external_coverage"] not in ("NONE", "EXTERNAL_ONLY", "INDEPENDENT") or provenance["even_solution"] not in ("INDEPENDENT", "PARITY_DERIVED", "NOT_APPLICABLE"):
        raise AggregationContractError("solver provenance vocabulary changed")
    payload_fields = {"schema", "key", "shard_id", "shard_key_list_sha256", *context.as_record(), "categories"}
    payload = _exact(_load_json(item["solver_payload_identity"], "normalized solver payload", schema=NORMALIZED_PAYLOAD_SCHEMA), payload_fields, "normalized solver payload")
    if payload["schema"] != NORMALIZED_PAYLOAD_SCHEMA or _key(payload["key"], "payload") != expected_key or payload["shard_id"] != expected_shard.shard_id or payload["shard_key_list_sha256"] != expected_shard.key_list_sha256:
        raise AggregationContractError("normalized solver payload key/shard mismatch")
    _context(payload, context)
    if not isinstance(payload["categories"], Mapping) or set(payload["categories"]) != set(OBSERVABLES):
        raise AggregationContractError("normalized solver payload categories changed")
    for name, category in payload["categories"].items():
        values = _exact(category, {"values"}, f"payload category {name}")["values"]
        if not isinstance(values, Mapping) or not values or any(not isinstance(key, str) or not key for key in values):
            raise AggregationContractError("normalized payload values are empty")
        for value in values.values():
            _decimal(value, f"payload category {name} value")
    return item


def _derived_state(observables: Mapping[str, Mapping[str, object]], numerical: Mapping[str, Mapping[str, object]], convention: Mapping[str, Mapping[str, object]]) -> str:
    states = [str(item["state"]) for group in (observables, numerical, convention) for item in group.values()]
    if "FAIL" in states:
        return "FAIL"
    if all(state == "PASS" for state in states):
        return "PASS"
    if "PARTIAL" in states or "PASS" in states:
        return "PARTIAL"
    return "NOT_ASSESSED"


def validate_key_result(result: object, *, expected_key: RadialKey, expected_shard: ShardInventory, context: ExpectedContext, contract_only: bool = False) -> Mapping[str, object]:
    fields = {"schema", "key", "shard_id", "shard_key_list_sha256", *context.as_record(), "solver_adapter", "observables", "numerical_budget", "convention_budget", "acceptance_state"}
    item = _exact(result, fields, "key result")
    if item["schema"] != KEY_RESULT_SCHEMA or _key(item["key"], "result") != expected_key or item["shard_id"] != expected_shard.shard_id or item["shard_key_list_sha256"] != expected_shard.key_list_sha256:
        raise AggregationContractError("key result key/shard mismatch")
    _context(item, context)
    adapter = validate_solver_adapter_envelope(item["solver_adapter"], expected_key=expected_key, expected_shard=expected_shard, context=context)
    observables = validate_component_map(item["observables"], OBSERVABLES, label="observables", context=context, contract_only=contract_only)
    numerical = validate_component_map(item["numerical_budget"], NUMERICAL_BUDGETS, label="numerical", context=context, contract_only=contract_only)
    convention = validate_component_map(item["convention_budget"], CONVENTION_BUDGETS, label="convention", context=context, contract_only=contract_only)
    derived = _derived_state(observables, numerical, convention)
    if item["acceptance_state"] != derived or (contract_only and derived == "PASS"):
        raise AggregationContractError("key acceptance state is not derived from components")
    provenance = adapter["provenance"]
    if (provenance["transmission"] == "UNRESOLVED" and observables["flux_wronskian"]["state"] == "PASS") or (provenance["external_coverage"] == "EXTERNAL_ONLY" and observables["independent_backend_difference"]["state"] == "PASS"):
        raise AggregationContractError("provenance-gated observable PASS is invalid")
    if expected_key.sector == "even" and (not adapter["independently_solved_sector"] or provenance["even_solution"] == "PARITY_DERIVED") and derived == "PASS":
        raise AggregationContractError("parity-derived even key cannot be PASS")
    return item


def _load_key_results(identities: object, expected: Sequence[RadialKey], shard: ShardInventory, context: ExpectedContext, *, contract_only: bool) -> list[Mapping[str, object]]:
    if not isinstance(identities, list) or len(identities) != len(expected):
        raise AggregationContractError("key-result identity count mismatch")
    results = [_load_json(identity, "key result identity", schema=KEY_RESULT_SCHEMA) for identity in identities]
    for result, key in zip(results, expected, strict=True):
        validate_key_result(result, expected_key=key, expected_shard=shard, context=context, contract_only=contract_only)
    if [_key(result["key"], "key result") for result in results] != list(expected):
        raise AggregationContractError("key-result identities are foreign, duplicate, or reordered")
    return results


def _state_counts(results: Sequence[Mapping[str, object]]) -> dict[str, int]:
    return {state: sum(result["acceptance_state"] == state for result in results) for state in STATES}


def _state_from_counts(counts: Mapping[str, int]) -> str:
    if counts["FAIL"]:
        return "FAIL"
    if counts["PASS"] and sum(counts.values()) == counts["PASS"]:
        return "PASS"
    if counts["PARTIAL"] or counts["PASS"]:
        return "PARTIAL"
    return "NOT_ASSESSED"


def validate_shard_result(result: object, *, expected_shard: ShardInventory, context: ExpectedContext, contract_only: bool = False) -> Mapping[str, object]:
    fields = {"schema", "shard_id", "shard_key_list_sha256", *context.as_record(), "key_result_identities", "state_counts", "aggregate_key_order_sha256", "acceptance_state"}
    item = _exact(result, fields, "shard result")
    if item["schema"] != SHARD_RESULT_SCHEMA or item["shard_id"] != expected_shard.shard_id or item["shard_key_list_sha256"] != expected_shard.key_list_sha256:
        raise AggregationContractError("shard result identity mismatch")
    _context(item, context)
    results = _load_key_results(item["key_result_identities"], expected_shard.keys, expected_shard, context, contract_only=contract_only)
    counts = _state_counts(results)
    if item["state_counts"] != counts or item["acceptance_state"] != _state_from_counts(counts) or (contract_only and item["acceptance_state"] == "PASS") or item["aggregate_key_order_sha256"] != sha256_bytes(jsonl_bytes(expected_shard.keys)):
        raise AggregationContractError("shard counts/key-order hash are not derived")
    return item


def validate_shard_checkpoint(checkpoint: object, *, expected_shard: ShardInventory, context: ExpectedContext, contract_only: bool = False) -> Mapping[str, object]:
    fields = {"schema", "shard_id", "shard_key_list_sha256", *context.as_record(), "completed_key_result_identities", "next_key_index", "state_counts"}
    item = _exact(checkpoint, fields, "shard checkpoint")
    if item["schema"] != SHARD_CHECKPOINT_SCHEMA or item["shard_id"] != expected_shard.shard_id or item["shard_key_list_sha256"] != expected_shard.key_list_sha256 or not isinstance(item["next_key_index"], int) or isinstance(item["next_key_index"], bool):
        raise AggregationContractError("shard checkpoint identity/index mismatch")
    _context(item, context)
    count = item["next_key_index"]
    if count < 0 or count > len(expected_shard.keys):
        raise AggregationContractError("checkpoint boundary is invalid")
    results = _load_key_results(item["completed_key_result_identities"], expected_shard.keys[:count], expected_shard, context, contract_only=contract_only)
    if item["state_counts"] != _state_counts(results):
        raise AggregationContractError("checkpoint counts are not derived")
    return item


def validate_aggregate_result(result: object, *, bundle: DomainBundle, context: ExpectedContext, contract_only: bool = False) -> Mapping[str, object]:
    fields = {"schema", *context.as_record(), "shard_result_identities", "membership_counts", "aggregate_key_order_sha256", "acceptance_state"}
    item = _exact(result, fields, "aggregate result")
    if item["schema"] != AGGREGATE_SCHEMA:
        raise AggregationContractError("aggregate schema mismatch")
    _context(item, context)
    shards = shard_inventory(bundle)
    if not isinstance(item["shard_result_identities"], list) or len(item["shard_result_identities"]) != 86:
        raise AggregationContractError("aggregate shard count mismatch")
    payloads = [_load_json(identity, "shard result identity", schema=SHARD_RESULT_SCHEMA) for identity in item["shard_result_identities"]]
    for payload, shard in zip(payloads, shards, strict=True):
        validate_shard_result(payload, expected_shard=shard, context=context, contract_only=contract_only)
    if [payload["shard_id"] for payload in payloads] != [shard.shard_id for shard in shards]:
        raise AggregationContractError("aggregate shard identities are foreign, duplicate, or reordered")
    production, extension = set(bundle.production), set(bundle.extension)
    counts = {"production": sum(key in production for key in bundle.union), "extension": sum(key in extension for key in bundle.union), "union": len(bundle.union)}
    shard_counts = {state: sum(payload["acceptance_state"] == state for payload in payloads) for state in STATES}
    if item["membership_counts"] != counts or item["acceptance_state"] != _state_from_counts(shard_counts) or (contract_only and item["acceptance_state"] == "PASS") or item["aggregate_key_order_sha256"] != sha256_bytes(jsonl_bytes(bundle.union)):
        raise AggregationContractError("aggregate membership/order hash are not derived")
    return item


def _fold_states(states: Sequence[str]) -> str:
    if not states:
        raise AggregationContractError("cannot derive a state from an empty subset")
    if "FAIL" in states:
        return "FAIL"
    if all(state == "PASS" for state in states):
        return "PASS"
    if "PARTIAL" in states or "PASS" in states:
        return "PARTIAL"
    return "NOT_ASSESSED"


def _aggregate_result_map(
    aggregate: Mapping[str, object], *, bundle: DomainBundle, context: ExpectedContext,
    contract_only: bool,
) -> dict[RadialKey, Mapping[str, object]]:
    """Reload the exact key-result chain after aggregate validation."""

    validate_aggregate_result(aggregate, bundle=bundle, context=context, contract_only=contract_only)
    found: dict[RadialKey, Mapping[str, object]] = {}
    for shard_identity, shard in zip(aggregate["shard_result_identities"], shard_inventory(bundle), strict=True):
        shard_payload = _load_json(shard_identity, "certificate shard result", schema=SHARD_RESULT_SCHEMA)
        for key_identity, key in zip(shard_payload["key_result_identities"], shard.keys, strict=True):
            result = _load_json(key_identity, "certificate key result", schema=KEY_RESULT_SCHEMA)
            if _key(result["key"], "certificate key result") != key or key in found:
                raise AggregationContractError("certificate aggregate key chain changed")
            found[key] = result
    if tuple(sorted(found, key=RadialKey.order_key)) != bundle.union:
        raise AggregationContractError("certificate aggregate does not reconstruct D_union")
    return found


def validate_subset_certificate(
    certificate: object, *, bundle: DomainBundle, context: ExpectedContext,
    contract_only: bool = False,
) -> Mapping[str, object]:
    fields = {"schema", "certificate_class", "key_count", "key_list_sha256", "key_list_identity", "source_aggregate_identity", *context.as_record(), "observable_states", "numerical_budget", "convention_budget", "derived_from_counts", "global_green_permitted", "acceptance_state"}
    item = _exact(certificate, fields, "subset certificate")
    if item["schema"] != CERTIFICATE_SCHEMA or item["certificate_class"] not in CERTIFICATE_CLASSES or item["global_green_permitted"] is not False or item["derived_from_counts"] is not False or not isinstance(item["key_count"], int):
        raise AggregationContractError("certificate class/global/count policy changed")
    _context(item, context)
    keys_identity = _identity(item["key_list_identity"], "certificate key list", immutable=True, root_immutable=True)
    raw = Path(str(keys_identity["path"])).read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise AggregationContractError("certificate key list lacks final LF")
    try:
        keys = tuple(_key(json.loads(line), "certificate") for line in raw.splitlines())
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise AggregationContractError("certificate key list is invalid JSONL") from exc
    try:
        validate_ordered_unique_keys(keys)
    except ValueError as exc:
        raise AggregationContractError("certificate subset is not canonically ordered") from exc
    if not keys or jsonl_bytes(keys) != raw or len(keys) != item["key_count"] or sha256_bytes(raw) != item["key_list_sha256"] or len(set(keys)) != len(keys):
        raise AggregationContractError("certificate subset is not canonical/enumerated")
    if not set(keys) <= set(bundle.union):
        raise AggregationContractError("certificate subset contains key outside D_union")
    source_aggregate = _load_json(item["source_aggregate_identity"], "certificate source aggregate", schema=AGGREGATE_SCHEMA)
    result_map = _aggregate_result_map(source_aggregate, bundle=bundle, context=context, contract_only=contract_only)
    observables = validate_component_map(item["observable_states"], OBSERVABLES, label="certificate observables", context=context, contract_only=contract_only)
    numerical = validate_component_map(item["numerical_budget"], NUMERICAL_BUDGETS, label="certificate numerical", context=context, contract_only=contract_only)
    convention = validate_component_map(item["convention_budget"], CONVENTION_BUDGETS, label="certificate convention", context=context, contract_only=contract_only)
    for label, supplied, field in (("observable", observables, "observables"), ("numerical", numerical, "numerical_budget"), ("convention", convention, "convention_budget")):
        for name, component in supplied.items():
            states = [str(result_map[key][field][name]["state"]) for key in keys]
            if component["state"] != _fold_states(states):
                raise AggregationContractError(f"certificate {label} component state is not derived from subset")
    if item["acceptance_state"] != _derived_state(observables, numerical, convention) or (contract_only and item["acceptance_state"] == "PASS"):
        raise AggregationContractError("certificate acceptance state is not derived")
    return item
