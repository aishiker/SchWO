"""Validate and aggregate all 80 production finite-radius shard roots.

The campaign layer performs no radial solve.  It independently reloads every
immutable shard artifact, proves exact ``D_prod`` coverage, checks all terminal
and payload identities, counts eight-state mode records, and preserves every
mode failure.  A complete clean campaign is still only ``PARTIAL`` because the
observer/convention and independent-backend uncertainty axes remain open.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import json
import math
from pathlib import Path
import stat

import numpy as np

from schwgw.validation.phase6_domain import (
    RadialKey,
    canonical_json_bytes,
    jsonl_bytes,
    sha256_bytes,
    source_file_identity,
)
from schwgw.validation.phase6_production_finite_radius import (
    DEFAULT_POLICY,
    KEY_TERMINAL_SCHEMA,
    MANIFEST_SCHEMA,
    RUN_CONTRACT_SCHEMA,
    SHARD_RESULT_SCHEMA,
    FrozenProductionContract,
    ProductionFiniteRadiusError,
    key_artifact_filenames,
    scientific_context_hash,
    source_hash_map,
    validate_solver_payload,
)


CAMPAIGN_RESULT_SCHEMA = "schwgw_phase6_production_finite_radius_campaign_v1"
CAMPAIGN_MANIFEST_SCHEMA = "schwgw_phase6_production_finite_radius_campaign_manifest_v1"


class ProductionCampaignError(ValueError):
    """Raised when the 80-root campaign proof fails structurally."""


def _strict_json(path: Path) -> dict[str, object]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON constant: {token}")
            ),
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise ProductionCampaignError(f"cannot parse canonical JSON: {path}") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
        raise ProductionCampaignError(f"artifact is not canonical JSON: {path}")
    return value


def _validate_identity(path: Path, expected: Mapping[str, object]) -> None:
    if set(expected) != {"mode", "nlink", "path", "sha256", "size"}:
        raise ProductionCampaignError("artifact identity schema changed")
    actual = source_file_identity(path)
    if actual != dict(expected) or actual["mode"] != 0o444 or actual["nlink"] != 1:
        raise ProductionCampaignError(f"artifact identity mismatch: {path}")


def _validate_source_identity(path: Path, expected: Mapping[str, object]) -> None:
    if set(expected) != {"mode", "nlink", "path", "sha256", "size"}:
        raise ProductionCampaignError("source identity schema changed")
    if path.is_symlink() or not path.is_file():
        raise ProductionCampaignError(f"source is missing or aliased: {path}")
    actual = source_file_identity(path)
    if actual != dict(expected) or actual["nlink"] != 1:
        raise ProductionCampaignError(f"source identity mismatch: {path}")


def _validate_manifest(root: Path) -> Mapping[str, Mapping[str, object]]:
    manifest = _strict_json(root / "manifest.json")
    files = manifest.get("files")
    actual_names = {path.name for path in root.iterdir() if path.is_file()}
    if (
        manifest.get("schema") != MANIFEST_SCHEMA
        or manifest.get("status") != "COMPLETE"
        or manifest.get("global_green_permitted") is not False
        or not isinstance(files, Mapping)
        or set(files) | {"manifest.json"} != actual_names
        or manifest.get("file_count_excluding_manifest") != len(files)
    ):
        raise ProductionCampaignError(f"shard manifest changed: {root}")
    result: dict[str, Mapping[str, object]] = {}
    for name, identity in files.items():
        if not isinstance(name, str) or not isinstance(identity, Mapping):
            raise ProductionCampaignError("manifest identity schema changed")
        _validate_identity(root / name, identity)
        result[name] = identity
    return result


def _validate_current_implementation_sources(
    run_contract: Mapping[str, object],
) -> dict[str, str]:
    identities = run_contract.get("implementation_source_identities")
    hashes = run_contract.get("implementation_source_sha256s")
    if not isinstance(identities, Mapping) or not isinstance(hashes, Mapping):
        raise ProductionCampaignError("implementation source binding is missing")
    normalized: dict[str, Mapping[str, object]] = {}
    for name, identity in identities.items():
        if not isinstance(name, str) or not isinstance(identity, Mapping):
            raise ProductionCampaignError("implementation identity schema changed")
        _validate_source_identity(Path(str(identity.get("path", ""))), identity)
        normalized[name] = identity
    actual_hashes = source_hash_map(normalized)
    if actual_hashes != dict(hashes):
        raise ProductionCampaignError("implementation hash map changed")
    return actual_hashes


def _validate_terminal(
    terminal: Mapping[str, object],
    *,
    ordinal: int,
    key: RadialKey,
) -> None:
    if (
        terminal.get("schema") != KEY_TERMINAL_SCHEMA
        or terminal.get("ordinal") != ordinal
        or terminal.get("key") != key.to_record()
        or terminal.get("global_green_permitted") is not False
        or terminal.get("acceptance_state") not in {"PARTIAL", "FAIL"}
        or terminal.get("execution_status") != "COMPLETED"
        or terminal.get("provenance")
        != {"legacy": False, "np": False, "pseudoinverse": False}
    ):
        raise ProductionCampaignError("formal terminal content changed")


def _worst(values: Sequence[str]) -> str:
    if not values:
        return "NOT_ASSESSED"
    if "FAIL" in values:
        return "FAIL"
    if "PARTIAL" in values:
        return "PARTIAL"
    if all(value == "PASS" for value in values):
        return "PASS"
    return "NOT_ASSESSED"


def validate_shard_root(
    root: str | Path,
    *,
    frozen: FrozenProductionContract,
) -> dict[str, object]:
    """Reload one formal shard root and return its raw validated evidence."""

    path = Path(root).resolve(strict=True)
    if (
        path.is_symlink()
        or not path.is_dir()
        or stat.S_IMODE(path.stat().st_mode) != 0o555
    ):
        raise ProductionCampaignError("shard root must be direct immutable")
    manifest_files = _validate_manifest(path)
    if "failure.json" in manifest_files:
        raise ProductionCampaignError(
            "infrastructure-failed root is not campaign input"
        )
    run_contract = _strict_json(path / "run_contract.json")
    shard_result = _strict_json(path / "shard_result.json")
    if run_contract.get("schema") != RUN_CONTRACT_SCHEMA:
        raise ProductionCampaignError("shard run-contract schema changed")
    if run_contract.get("context_sha256") != scientific_context_hash(run_contract):
        raise ProductionCampaignError("shard scientific context hash changed")
    expected_bound_inputs = {
        "coordinate_source": dict(frozen.coordinate_source_identity),
        "domain": {
            name: dict(identity) for name, identity in frozen.domain_identities.items()
        },
        "execution": {
            name: dict(identity)
            for name, identity in frozen.execution_identities.items()
        },
    }
    if (
        run_contract.get("bound_inputs") != expected_bound_inputs
        or run_contract.get("global_green_permitted") is not False
        or run_contract.get("paper_figure_agreement_gate") != "PROHIBITED"
        or run_contract.get("policy_sha256") != DEFAULT_POLICY.sha256
        or run_contract.get("policy") != DEFAULT_POLICY.to_record()
        or run_contract.get("table_i_sites")
        != [site.to_record() for site in frozen.sites]
    ):
        raise ProductionCampaignError("shard frozen scientific binding changed")
    mode = run_contract.get("execution_mode")
    if mode != {
        "contract_only": False,
        "kernel_unit_test_only": False,
        "science_executed": True,
        "scientific_evidence": True,
        "selector_injected": False,
        "solver_injected": False,
        "status": "PRODUCTION_SCIENCE_EXECUTION",
    }:
        raise ProductionCampaignError(
            "test/contract-only root is not scientific evidence"
        )
    shard = run_contract.get("shard")
    if not isinstance(shard, Mapping) or not isinstance(shard.get("shard_id"), str):
        raise ProductionCampaignError("shard identity is malformed")
    frozen_shard = frozen.shard_record(str(shard["shard_id"]))
    keys = frozen.shard_keys(str(shard["shard_id"]))
    if dict(shard) != dict(frozen_shard) or run_contract.get("shard_keys") != [
        key.to_record() for key in keys
    ]:
        raise ProductionCampaignError("shard differs from frozen D_prod partition")
    implementation_hashes = _validate_current_implementation_sources(run_contract)
    expected_shard_result_fields = {
        "acceptance",
        "all_terminal_identities",
        "contract_only",
        "convention_budget",
        "failures",
        "global_green_permitted",
        "implementation_source_sha256s",
        "infrastructure_failure",
        "kernel_unit_test_only",
        "numerical_budget",
        "observable_statuses",
        "overall_state",
        "root",
        "schema",
        "science_executed",
        "scientific_evidence",
        "shard",
        "summary",
    }
    if (
        set(shard_result) != expected_shard_result_fields
        or shard_result.get("schema") != SHARD_RESULT_SCHEMA
        or shard_result.get("scientific_evidence") is not True
        or shard_result.get("science_executed") is not True
        or shard_result.get("kernel_unit_test_only") is not False
        or shard_result.get("contract_only") is not False
        or shard_result.get("global_green_permitted") is not False
        or shard_result.get("overall_state") not in {"PARTIAL", "FAIL"}
        or shard_result.get("acceptance") != shard_result.get("overall_state")
        or shard_result.get("infrastructure_failure") is not None
        or shard_result.get("implementation_source_sha256s") != implementation_hashes
    ):
        raise ProductionCampaignError("formal shard result fields changed")
    terminals: list[dict[str, object]] = []
    terminal_identities: list[Mapping[str, object]] = []
    payload_identities: list[Mapping[str, object]] = []
    mode_records: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    for ordinal, key in enumerate(keys):
        names = key_artifact_filenames(ordinal, key)
        terminal_path = path / names["terminal"]
        terminal = _strict_json(terminal_path)
        _validate_terminal(terminal, ordinal=ordinal, key=key)
        terminal_identity = source_file_identity(terminal_path)
        terminal_identities.append(terminal_identity)
        terminals.append(terminal)
        payload_identity = terminal.get("payload_identity")
        if not isinstance(payload_identity, Mapping):
            raise ProductionCampaignError("completed terminal lacks payload identity")
        payload_path = path / names["payload"]
        if Path(str(payload_identity.get("path", ""))) != payload_path:
            raise ProductionCampaignError("payload escaped its immutable shard root")
        _validate_identity(payload_path, payload_identity)
        payload = _strict_json(payload_path)
        try:
            validate_solver_payload(payload, key=key, sites=frozen.sites)
        except ProductionFiniteRadiusError as exc:
            raise ProductionCampaignError("mode payload validation failed") from exc
        if payload["acceptance_state"] != terminal["acceptance_state"]:
            raise ProductionCampaignError("payload/terminal acceptance mismatch")
        payload_identities.append(payload_identity)
        has_eight_states = (
            isinstance(payload.get("result"), Mapping)
            and isinstance(payload["result"].get("finite_radius_states"), list)  # type: ignore[union-attr]
            and len(payload["result"]["finite_radius_states"]) == 8  # type: ignore[index]
        )
        mode_records.append(
            {
                "acceptance_state": payload["acceptance_state"],
                "has_exact_eight_radial_states": has_eight_states,
                "key": key.to_record(),
                "observable_statuses": payload["observable_statuses"],
                "payload_identity": dict(payload_identity),
                "terminal_identity": dict(terminal_identity),
            }
        )
        if payload["acceptance_state"] == "FAIL":
            failures.append(
                {
                    "failures": payload["failures"],
                    "key": key.to_record(),
                    "payload_identity": dict(payload_identity),
                }
            )
    if shard_result.get("all_terminal_identities") != [
        dict(value) for value in terminal_identities
    ]:
        raise ProductionCampaignError("raw terminal identity ledger changed")
    expected_summary = {
        "blocked_nonreusable_predecessor_count": 0,
        "key_count": len(keys),
        "mode_state_counts": {
            state: sum(item["acceptance_state"] == state for item in terminals)
            for state in ("PARTIAL", "FAIL")
        },
        "payload_count": len(payload_identities),
        "solver_call_count_this_run": sum(
            int(item["solver_call_count"]) for item in terminals
        ),
        "terminal_count": len(terminals),
    }
    if shard_result.get("summary") != expected_summary:
        raise ProductionCampaignError("formal shard summary changed")
    if shard_result.get("failures") != failures:
        raise ProductionCampaignError("formal shard failure ledger changed")
    expected_state = (
        "FAIL"
        if any(item["acceptance_state"] == "FAIL" for item in terminals)
        else "PARTIAL"
    )
    if shard_result.get("overall_state") != expected_state:
        raise ProductionCampaignError("mode failure was hidden by shard result")
    return {
        "failures": failures,
        "implementation_source_identities": run_contract[
            "implementation_source_identities"
        ],
        "implementation_source_sha256s": implementation_hashes,
        "keys": [key.to_record() for key in keys],
        "mode_records": mode_records,
        "payload_identities": [dict(value) for value in payload_identities],
        "root": str(path),
        "root_manifest_identity": source_file_identity(path / "manifest.json"),
        "shard": dict(shard),
        "shard_result": shard_result,
        "shard_result_identity": source_file_identity(path / "shard_result.json"),
        "terminal_identities": [dict(value) for value in terminal_identities],
    }


def build_campaign_result(
    shard_roots: Sequence[str | Path],
    *,
    frozen: FrozenProductionContract,
    campaign_implementation_identities: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    """Build a full 80-root campaign result after exact independent reload."""

    if len(shard_roots) != 80:
        raise ProductionCampaignError("campaign requires exactly 80 shard roots")
    resolved = tuple(Path(root).resolve(strict=True) for root in shard_roots)
    if len(set(resolved)) != 80:
        raise ProductionCampaignError("campaign shard roots must be unique")
    validated = [validate_shard_root(root, frozen=frozen) for root in resolved]
    by_shard = {item["shard"]["shard_id"]: item for item in validated}  # type: ignore[index]
    expected_shards = [str(item["shard_id"]) for item in frozen.shard_records]
    if len(by_shard) != 80 or set(by_shard) != set(expected_shards):
        raise ProductionCampaignError("campaign shard-id set differs from D_prod")
    ordered = [by_shard[shard_id] for shard_id in expected_shards]
    source_hash_sets = {
        canonical_json_bytes(item["implementation_source_sha256s"]) for item in ordered
    }
    if len(source_hash_sets) != 1:
        raise ProductionCampaignError(
            "production shards used different implementation-source hashes"
        )
    source_identity_sets = {
        canonical_json_bytes(item["implementation_source_identities"])
        for item in ordered
    }
    if len(source_identity_sets) != 1:
        raise ProductionCampaignError(
            "production shards used different implementation-source identities"
        )
    flattened_keys = tuple(
        RadialKey.from_record(record)
        for item in ordered
        for record in item["keys"]  # type: ignore[union-attr]
    )
    if (
        flattened_keys != frozen.production_keys
        or len(flattened_keys) != 16_048
        or sha256_bytes(jsonl_bytes(flattened_keys))
        != frozen.domain_identities["D_prod.jsonl"]["sha256"]
    ):
        raise ProductionCampaignError("campaign key union differs from exact D_prod")
    modes = [
        record
        for item in ordered
        for record in item["mode_records"]  # type: ignore[union-attr]
    ]
    failures = [
        {"shard_id": item["shard"]["shard_id"], **failure}  # type: ignore[index]
        for item in ordered
        for failure in item["failures"]  # type: ignore[union-attr]
    ]
    state_counts = {
        state: sum(record["acceptance_state"] == state for record in modes)
        for state in ("PARTIAL", "FAIL")
    }
    eight_state_count = sum(record["has_exact_eight_radial_states"] for record in modes)
    missing_state_modes = [
        record["key"] for record in modes if not record["has_exact_eight_radial_states"]
    ]
    overall = "FAIL" if failures or missing_state_modes else "PARTIAL"
    observable_names = sorted(
        {
            name
            for record in modes
            for name in record["observable_statuses"]  # type: ignore[union-attr]
        }
    )
    observables = {
        name: _worst(
            [
                str(record["observable_statuses"].get(name, "NOT_ASSESSED"))  # type: ignore[union-attr]
                for record in modes
            ]
        )
        for name in observable_names
    }
    all_terminal_identities = [
        {
            "identity": record["terminal_identity"],
            "key": record["key"],
            "shard_id": item["shard"]["shard_id"],  # type: ignore[index]
        }
        for item in ordered
        for record in item["mode_records"]  # type: ignore[union-attr]
    ]
    shard_result_identities = [
        {
            "identity": item["shard_result_identity"],
            "shard_id": item["shard"]["shard_id"],  # type: ignore[index]
        }
        for item in ordered
    ]
    implementation_hashes = next(iter(ordered))["implementation_source_sha256s"]
    return {
        "acceptance": overall,
        "all_raw_terminal_identities": all_terminal_identities,
        "campaign_implementation_source_identities": {
            name: dict(identity)
            for name, identity in campaign_implementation_identities.items()
        },
        "campaign_implementation_source_sha256s": source_hash_map(
            campaign_implementation_identities
        ),
        "contract_only": False,
        "convention_budget": {
            "components": {
                name: float(np.finfo(float).max)
                for name in (
                    "observer",
                    "tetrad",
                    "polarization_basis",
                    "phase_origin",
                    "total_scattered_definition",
                )
            },
            "status": "FAIL" if overall == "FAIL" else "PARTIAL",
        },
        "coverage": {
            "D_prod_key_count": len(flattened_keys),
            "D_prod_key_list_sha256": sha256_bytes(jsonl_bytes(flattened_keys)),
            "exact_eight_state_mode_count": eight_state_count,
            "frequency_count": len({key.kM for key in flattened_keys}),
            "missing_eight_state_mode_count": len(missing_state_modes),
            "missing_eight_state_modes": missing_state_modes,
            "radial_state_record_count": 8 * eight_state_count,
            "shard_count": len(ordered),
            "terminal_count": len(all_terminal_identities),
        },
        "failures": failures,
        "global_green_permitted": False,
        "implementation_source_sha256s": implementation_hashes,
        "implementation_source_identities": next(iter(ordered))[
            "implementation_source_identities"
        ],
        "kernel_unit_test_only": False,
        "mode_state_counts": state_counts,
        "numerical_budget": {
            "components": {
                name: (
                    float(np.finfo(float).eps)
                    if name == "arithmetic_precision"
                    else float(np.finfo(float).max)
                )
                for name in (
                    "lmax",
                    "r_in",
                    "r_out",
                    "jost_order",
                    "ode_tolerance",
                    "arithmetic_precision",
                    "axis_limit",
                    "backend_difference",
                )
            },
            "status": "FAIL" if overall == "FAIL" else "PARTIAL",
        },
        "observable_statuses": observables,
        "overall_state": overall,
        "release_qualification": {
            "finite_radius_outputs_are_observer_qualified": False,
            "full_paper_figure_rerun": False,
            "global_green_permitted": False,
            "independent_backend_difference_closed": False,
            "radial_state_evidence_only": True,
        },
        "schema": CAMPAIGN_RESULT_SCHEMA,
        "science_executed": True,
        "scientific_evidence": True,
        "shard_result_identities": shard_result_identities,
    }


def validate_campaign_result(payload: Mapping[str, object]) -> None:
    """Fail closed on campaign release-field or coverage promotion."""

    expected_fields = {
        "acceptance",
        "all_raw_terminal_identities",
        "campaign_implementation_source_identities",
        "campaign_implementation_source_sha256s",
        "contract_only",
        "convention_budget",
        "coverage",
        "failures",
        "global_green_permitted",
        "implementation_source_identities",
        "implementation_source_sha256s",
        "kernel_unit_test_only",
        "mode_state_counts",
        "numerical_budget",
        "observable_statuses",
        "overall_state",
        "release_qualification",
        "schema",
        "science_executed",
        "scientific_evidence",
        "shard_result_identities",
    }
    if (
        set(payload) != expected_fields
        or payload.get("schema") != CAMPAIGN_RESULT_SCHEMA
        or payload.get("scientific_evidence") is not True
        or payload.get("science_executed") is not True
        or payload.get("kernel_unit_test_only") is not False
        or payload.get("contract_only") is not False
        or payload.get("global_green_permitted") is not False
        or payload.get("overall_state") not in {"PARTIAL", "FAIL"}
        or payload.get("acceptance") != payload.get("overall_state")
    ):
        raise ProductionCampaignError("campaign release fields changed")
    coverage = payload.get("coverage")
    exact_state_count = (
        coverage.get("exact_eight_state_mode_count")
        if isinstance(coverage, Mapping)
        else None
    )
    missing_state_count = (
        coverage.get("missing_eight_state_mode_count")
        if isinstance(coverage, Mapping)
        else None
    )
    if (
        not isinstance(coverage, Mapping)
        or coverage.get("D_prod_key_count") != 16_048
        or coverage.get("D_prod_key_list_sha256")
        != "54f13ea2473fb0a04ca5e16277edae31335c03b11753973d83a934cce2f0872b"
        or coverage.get("frequency_count") != 40
        or coverage.get("shard_count") != 80
        or coverage.get("terminal_count") != 16_048
        or isinstance(exact_state_count, bool)
        or not isinstance(exact_state_count, int)
        or isinstance(missing_state_count, bool)
        or not isinstance(missing_state_count, int)
        or coverage.get("radial_state_record_count") != 8 * exact_state_count
        or exact_state_count + missing_state_count != 16_048
    ):
        raise ProductionCampaignError("campaign coverage fields changed")
    failures = payload.get("failures")
    missing = missing_state_count
    if not isinstance(failures, list):
        raise ProductionCampaignError("campaign failure ledger changed")
    expected = "FAIL" if failures or missing else "PARTIAL"
    if payload.get("overall_state") != expected:
        raise ProductionCampaignError("campaign failures were hidden")
    expected_budget_status = "FAIL" if expected == "FAIL" else "PARTIAL"
    for budget_name in ("numerical_budget", "convention_budget"):
        budget = payload.get(budget_name)
        if (
            not isinstance(budget, Mapping)
            or set(budget) != {"components", "status"}
            or budget.get("status") != expected_budget_status
            or not isinstance(budget.get("components"), Mapping)
        ):
            raise ProductionCampaignError("campaign budget schema/status changed")
        for value in budget["components"].values():
            try:
                parsed = float(value)
            except (TypeError, ValueError) as exc:
                raise ProductionCampaignError(
                    "campaign budget contains a non-number"
                ) from exc
            if not math.isfinite(parsed) or parsed < 0.0:
                raise ProductionCampaignError("campaign budget is invalid")
    convention_components = payload["convention_budget"]["components"]
    if any(
        float(convention_components[name]) == 0.0
        for name in ("observer", "tetrad", "polarization_basis")
    ):
        raise ProductionCampaignError("unassessed convention budget is zero")
    observable_statuses = payload.get("observable_statuses")
    if not isinstance(observable_statuses, Mapping) or any(
        observable_statuses.get(name) not in {"NOT_ASSESSED", "PARTIAL"}
        for name in (
            "observer_qualified_tidal_response",
            "detector_response",
            "infinity_waveform",
            "convention_closure",
        )
    ):
        raise ProductionCampaignError("campaign observer/convention claim was promoted")
    terminal_identities = payload.get("all_raw_terminal_identities")
    shard_identities = payload.get("shard_result_identities")
    if (
        not isinstance(terminal_identities, list)
        or len(terminal_identities) != 16_048
        or not isinstance(shard_identities, list)
        or len(shard_identities) != 80
    ):
        raise ProductionCampaignError("campaign raw identity ledgers changed")
    terminal_keys: list[RadialKey] = []
    terminal_states: list[str] = []
    terminal_paths: set[str] = set()
    terminal_shards: set[str] = set()
    for record in (*terminal_identities, *shard_identities):
        if not isinstance(record, Mapping) or not isinstance(
            record.get("identity"), Mapping
        ):
            raise ProductionCampaignError("campaign identity record changed")
        _validate_identity(
            Path(str(record["identity"].get("path", ""))), record["identity"]
        )
    for record in terminal_identities:
        key_record = record.get("key")
        shard_id = record.get("shard_id")
        if not isinstance(key_record, Mapping) or not isinstance(shard_id, str):
            raise ProductionCampaignError("campaign terminal ledger fields changed")
        key = RadialKey.from_record(key_record)
        terminal = _strict_json(Path(str(record["identity"]["path"])))
        if (
            terminal.get("schema") != KEY_TERMINAL_SCHEMA
            or terminal.get("key") != key.to_record()
            or terminal.get("acceptance_state") not in {"PARTIAL", "FAIL"}
        ):
            raise ProductionCampaignError("campaign terminal content changed")
        terminal_keys.append(key)
        terminal_states.append(str(terminal["acceptance_state"]))
        terminal_paths.add(str(record["identity"]["path"]))
        terminal_shards.add(shard_id)
    if (
        len(terminal_paths) != 16_048
        or len(terminal_shards) != 80
        or tuple(terminal_keys) != tuple(sorted(terminal_keys, key=RadialKey.order_key))
        or sha256_bytes(jsonl_bytes(terminal_keys))
        != coverage["D_prod_key_list_sha256"]
    ):
        raise ProductionCampaignError("campaign terminal key coverage changed")
    mode_state_counts = payload.get("mode_state_counts")
    expected_mode_counts = {
        state: terminal_states.count(state) for state in ("PARTIAL", "FAIL")
    }
    if (
        mode_state_counts != expected_mode_counts
        or len(failures) != expected_mode_counts["FAIL"]
    ):
        raise ProductionCampaignError("campaign terminal state counts changed")
    qualification = payload.get("release_qualification")
    if (
        not isinstance(qualification, Mapping)
        or qualification.get("global_green_permitted") is not False
        or qualification.get("finite_radius_outputs_are_observer_qualified")
        is not False
        or qualification.get("radial_state_evidence_only") is not True
    ):
        raise ProductionCampaignError("campaign scope was promoted")
    for identity_field, hash_field in (
        (
            "implementation_source_identities",
            "implementation_source_sha256s",
        ),
        (
            "campaign_implementation_source_identities",
            "campaign_implementation_source_sha256s",
        ),
    ):
        identities = payload.get(identity_field)
        hashes = payload.get(hash_field)
        if not isinstance(identities, Mapping) or not isinstance(hashes, Mapping):
            raise ProductionCampaignError("campaign implementation binding changed")
        normalized: dict[str, Mapping[str, object]] = {}
        for name, identity in identities.items():
            if not isinstance(name, str) or not isinstance(identity, Mapping):
                raise ProductionCampaignError(
                    "campaign implementation identity changed"
                )
            _validate_source_identity(Path(str(identity.get("path", ""))), identity)
            normalized[name] = identity
        if source_hash_map(normalized) != dict(hashes):
            raise ProductionCampaignError("campaign implementation hashes changed")


__all__ = [
    "CAMPAIGN_MANIFEST_SCHEMA",
    "CAMPAIGN_RESULT_SCHEMA",
    "ProductionCampaignError",
    "build_campaign_result",
    "validate_campaign_result",
    "validate_shard_root",
]
