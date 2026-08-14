"""Strict full-campaign indexing for Phase-6 conditioning scan shards.

The campaign index is an integrity and accounting layer.  It does not run a
solver, compare against a paper figure, or turn a completed scientific
``FAIL`` into an execution failure.  Publication is possible only after all
86 immutable shard roots have been independently reloaded and their exact
17,818-key union has been recovered.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import math
import os
from pathlib import Path
import stat
import time

import numpy as np

from schwgw.validation.phase6_conditioning_scan import (
    DEFAULT_POLICY,
    KEY_TERMINAL_SCHEMA,
    RUN_CONTRACT_SCHEMA,
    SOLVER_PAYLOAD_SCHEMA,
    FrozenScanContract,
    OuterCandidateDiagnostic,
    OuterSelection,
    calibration_solve_nodes,
    checkpoint_fields_from_solver_payload,
    key_artifact_filenames,
    load_frozen_scan_contract,
    scan_context_hash,
    source_hash_map,
)
from schwgw.validation.phase6_domain import (
    RadialKey,
    canonical_json_bytes,
    jsonl_bytes,
    sha256_bytes,
    source_file_identity,
)
from schwgw.validation.phase6_execution_contract import (
    ACCEPTANCE_STATES,
    CONVENTION_BUDGET_FIELDS,
    KEY_PAYLOAD_ENVELOPE_SCHEMA,
    NUMERICAL_BUDGET_FIELDS,
    SHARD_CHECKPOINT_SCHEMA,
    SHARD_RESULT_SCHEMA,
    validate_key_checkpoint,
)


CAMPAIGN_INDEX_SCHEMA = "schwgw_phase6_conditioning_campaign_index_v1"
CAMPAIGN_MANIFEST_SCHEMA = "schwgw_phase6_conditioning_campaign_manifest_v1"
CAMPAIGN_SHARD_ENTRY_SCHEMA = "schwgw_phase6_conditioning_campaign_shard_entry_v1"
CAMPAIGN_ROOT_PREFIX = "v1_conditioning_scan_"
CAMPAIGN_ROOT_SUFFIX = "_v1_20260808_py314"
EXPECTED_SHARD_COUNT = 86
EXPECTED_KEY_COUNT = 17_818
EXPECTED_PRODUCTION_KEY_COUNT = 16_048
EXPECTED_EXTENSION_KEY_COUNT = 1_770
EXPECTED_TRANSITION_KEY_COUNT = 158
FLOAT64_UNASSESSED_SENTINEL = float(np.finfo(float).max)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOMAIN_ROOT = PROJECT_ROOT / "runs/phase6/v1_domain_freeze_v3_20260806"
EXECUTION_ROOT = PROJECT_ROOT / "runs/phase6/v1_execution_contract_v4_20260806"
AGGREGATION_ROOT = PROJECT_ROOT / "runs/phase6/v1_aggregation_contract_v8_20260806"
AGGREGATION_IDENTITIES = {
    "aggregation_contract.json": (
        "742db1cf159e0bb9c41eb2621b7084f09bca65acd934fdcf639f25f486fa49d2"
    ),
    "manifest.json": (
        "427ddf4984690e930b225f0a3c782b99cbf65eb1a30fcb77f8f1ee67ab53675c"
    ),
}

OBSERVABLE_NAMES = (
    "conditioning_transition_calibration",
    "flux_conservation",
    "production_finite_radius_states",
    "radial_s_matrix",
    "required_radius_radial_state",
)
LOCAL_TERMINAL_STATUSES = ("COMPLETED", "COMPLETED_FAIL_CLOSED")


class ConditioningCampaignError(ValueError):
    """Raised for incomplete, aliased, mutable, or contradictory campaigns."""


def _exact_mapping(
    value: object,
    fields: set[str],
    label: str,
) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != fields:
        raise ConditioningCampaignError(f"{label} exact schema changed")
    return value


def _direct_absolute(path: str | Path, *, kind: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        raise ConditioningCampaignError(f"{kind} must be an absolute path")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise ConditioningCampaignError(f"{kind} does not exist: {candidate}") from exc
    if candidate != resolved or any(
        component.is_symlink() for component in (candidate, *candidate.parents)
    ):
        raise ConditioningCampaignError(f"{kind} must be a direct non-aliased path")
    return candidate


def _immutable_root(path: str | Path, *, label: str) -> Path:
    root = _direct_absolute(path, kind=label)
    info = root.lstat()
    if not stat.S_ISDIR(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o555:
        raise ConditioningCampaignError(f"{label} must be a mode-0555 directory")
    return root


def _strict_file_identity(path: Path) -> dict[str, object]:
    if path.parent.is_symlink() or path.is_symlink() or not path.is_file():
        raise ConditioningCampaignError(f"artifact is missing or aliased: {path}")
    identity = source_file_identity(path)
    if identity["mode"] != 0o444 or identity["nlink"] != 1:
        raise ConditioningCampaignError(
            f"artifact is not immutable 0444/nlink1: {path}"
        )
    return identity


def _validate_identity(
    value: object,
    *,
    path: Path,
    label: str,
) -> dict[str, object]:
    identity = _exact_mapping(
        value,
        {"mode", "nlink", "path", "sha256", "size"},
        label,
    )
    actual = _strict_file_identity(path)
    if dict(identity) != actual:
        raise ConditioningCampaignError(f"{label} no longer matches exact bytes")
    return actual


def _strict_json(path: Path) -> dict[str, object]:
    _strict_file_identity(path)
    raw = path.read_bytes()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConditioningCampaignError(f"artifact is malformed JSON: {path}") from exc
    if not isinstance(payload, dict) or canonical_json_bytes(payload) != raw:
        raise ConditioningCampaignError(f"artifact is not canonical JSON: {path}")
    return payload


def _finite_number(value: object, label: str, *, nonnegative: bool = True) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConditioningCampaignError(f"{label} is not numeric")
    parsed = float(value)
    if not math.isfinite(parsed) or (nonnegative and parsed < 0.0):
        raise ConditioningCampaignError(f"{label} is not finite/nonnegative")
    return parsed


def _state_counts(values: Sequence[str]) -> dict[str, int]:
    counts = Counter(values)
    if set(counts) - set(ACCEPTANCE_STATES):
        raise ConditioningCampaignError("unknown acceptance state")
    return {state: counts[state] for state in ACCEPTANCE_STATES}


def _merge_state_counts(
    records: Sequence[Mapping[str, int]],
) -> dict[str, int]:
    return {
        state: sum(int(record.get(state, 0)) for record in records)
        for state in ACCEPTANCE_STATES
    }


def _worst_state(values: Sequence[str]) -> str:
    rank = {"PASS": 0, "NOT_ASSESSED": 1, "PARTIAL": 2, "FAIL": 3}
    if not values:
        return "NOT_ASSESSED"
    if any(value not in rank for value in values):
        raise ConditioningCampaignError("unknown state in worst-state reduction")
    return max(values, key=rank.__getitem__)


def _strict_source_identities(value: object) -> dict[str, Mapping[str, object]]:
    if not isinstance(value, Mapping) or set(value) != {
        "background_base",
        "conditioned_backend",
        "matching",
        "potentials",
        "scan_module",
        "schwarzschild_background",
        "shard_runner",
    }:
        raise ConditioningCampaignError("run source-identity inventory changed")
    result: dict[str, Mapping[str, object]] = {}
    for name, raw_identity in sorted(value.items()):
        identity = _exact_mapping(
            raw_identity,
            {"mode", "nlink", "path", "sha256", "size"},
            f"source identity {name}",
        )
        path = _direct_absolute(str(identity["path"]), kind=f"source {name}")
        actual = source_file_identity(path)
        if actual != dict(identity):
            raise ConditioningCampaignError(f"live source identity changed: {name}")
        result[str(name)] = dict(identity)
    return result


def _parse_outer_selection(
    value: object,
    *,
    key: RadialKey,
) -> OuterSelection:
    item = _exact_mapping(
        value,
        {
            "blocker",
            "candidates",
            "key",
            "selected_r_out_M",
            "status",
            "turning_proxy_M",
        },
        "outer selection",
    )
    if item["key"] != key.to_record():
        raise ConditioningCampaignError("outer selection key changed")
    turning_proxy = _finite_number(item["turning_proxy_M"], "turning proxy")
    raw_candidates = item["candidates"]
    if not isinstance(raw_candidates, list) or not raw_candidates:
        raise ConditioningCampaignError("outer selection candidates are missing")
    candidates: list[OuterCandidateDiagnostic] = []
    for index, raw in enumerate(raw_candidates):
        record = _exact_mapping(
            raw,
            {
                "blockers",
                "estimated_outer_segments",
                "k_r_out",
                "potential_to_k2",
                "r_out_M",
                "relative_jost_determinant",
                "scaled_jost_condition",
                "status",
                "turning_proxy_margin",
            },
            "outer candidate",
        )
        radius = _finite_number(record["r_out_M"], "outer candidate radius")
        if (
            index >= len(DEFAULT_POLICY.r_out_candidates_M)
            or radius != (DEFAULT_POLICY.r_out_candidates_M[index])
        ):
            raise ConditioningCampaignError("outer candidate ordering changed")
        blockers = record["blockers"]
        if not isinstance(blockers, list) or any(
            not isinstance(blocker, str) or not blocker for blocker in blockers
        ):
            raise ConditioningCampaignError("outer candidate blockers changed")
        status_value = record["status"]
        if status_value not in {"PASS", "FAIL_CLOSED"} or (
            (status_value == "PASS") != (not blockers)
        ):
            raise ConditioningCampaignError(
                "outer candidate status contradicts blockers"
            )
        segments = record["estimated_outer_segments"]
        if isinstance(segments, bool) or not isinstance(segments, int) or segments < 1:
            raise ConditioningCampaignError("outer segment estimate changed")

        def optional_finite(raw_value: object, label: str) -> float | None:
            if raw_value is None:
                return None
            return _finite_number(raw_value, label)

        candidate = OuterCandidateDiagnostic(
            r_out_M=radius,
            turning_proxy_margin=_finite_number(
                record["turning_proxy_margin"], "turning proxy margin"
            ),
            potential_to_k2=_finite_number(
                record["potential_to_k2"], "outer potential ratio"
            ),
            k_r_out=_finite_number(record["k_r_out"], "k r_out"),
            estimated_outer_segments=segments,
            scaled_jost_condition=optional_finite(
                record["scaled_jost_condition"], "scaled Jost condition"
            ),
            relative_jost_determinant=optional_finite(
                record["relative_jost_determinant"], "relative Jost determinant"
            ),
            status=str(status_value),
            blockers=tuple(blockers),
        )
        if candidate.status == "PASS" and (
            candidate.scaled_jost_condition is None
            or candidate.relative_jost_determinant is None
        ):
            raise ConditioningCampaignError("passing outer candidate lacks Jost probes")
        candidates.append(candidate)
    status_value = item["status"]
    selected = item["selected_r_out_M"]
    blocker = item["blocker"]
    if status_value == "SUPPORTED":
        selected_value = _finite_number(selected, "selected r_out")
        if (
            blocker is not None
            or candidates[-1].status != "PASS"
            or any(candidate.status == "PASS" for candidate in candidates[:-1])
            or selected_value != candidates[-1].r_out_M
        ):
            raise ConditioningCampaignError("supported outer selection is inconsistent")
    elif status_value == "UNSUPPORTED_FAIL_CLOSED":
        selected_value = None
        if (
            selected is not None
            or blocker != "NO_FROZEN_R_OUT_NODE_PASSES_ALL_RAW_GATES"
            or len(candidates) != len(DEFAULT_POLICY.r_out_candidates_M)
            or any(candidate.status == "PASS" for candidate in candidates)
        ):
            raise ConditioningCampaignError(
                "unsupported outer selection is inconsistent"
            )
    else:
        raise ConditioningCampaignError("outer selection status changed")
    selection = OuterSelection(
        key=key,
        status=str(status_value),
        selected_r_out_M=selected_value,
        turning_proxy_M=turning_proxy,
        candidates=tuple(candidates),
        blocker=None if blocker is None else str(blocker),
    )
    if selection.to_record() != dict(item):
        raise ConditioningCampaignError("outer selection serialization changed")
    return selection


def _validate_plan(
    plan: object,
    *,
    key: RadialKey,
    shard_ordinal: int,
    domain_ordinal: int,
    transition_key: bool,
) -> tuple[Mapping[str, object], OuterSelection]:
    item = _exact_mapping(
        plan,
        {
            "domain_ordinal",
            "key",
            "ladder_axis_descriptors",
            "ladder_axis_map_sha256",
            "outer_selection",
            "shard_ordinal",
            "solve_nodes",
            "transition_key",
        },
        "key plan",
    )
    if (
        item["key"] != key.to_record()
        or item["shard_ordinal"] != shard_ordinal
        or item["domain_ordinal"] != domain_ordinal
        or item["transition_key"] is not transition_key
    ):
        raise ConditioningCampaignError("key plan order/domain binding changed")
    selection = _parse_outer_selection(item["outer_selection"], key=key)
    nodes = calibration_solve_nodes(
        selection,
        transition_key=transition_key,
        policy=DEFAULT_POLICY,
    )
    expected_nodes = [node.to_record() for node in nodes]
    if item["solve_nodes"] != expected_nodes:
        raise ConditioningCampaignError("key solve-node plan changed")
    if selection.supported:
        descriptors = [node.descriptor() for node in nodes]
    else:
        descriptors = [
            {
                "actual_precision_digits": 16,
                "node_id": "baseline_preflight",
                "tolerance": DEFAULT_POLICY.baseline_rtol,
            }
        ]
    if item["ladder_axis_descriptors"] != descriptors or item[
        "ladder_axis_map_sha256"
    ] != sha256_bytes(canonical_json_bytes(descriptors)):
        raise ConditioningCampaignError("key ladder descriptor identity changed")
    return item, selection


def _expected_context(
    contract: Mapping[str, object],
    plan: Mapping[str, object],
    *,
    root: Path,
) -> dict[str, object]:
    return {
        "actual_precision": contract["actual_precision"],
        "backend_hashes": contract["backend_hashes"],
        "code_hashes": contract["code_hashes"],
        "config_hashes": contract["config_hashes"],
        "domain_contract_sha256": contract["domain_contract_sha256"],
        "domain_union_key_list_sha256": contract["domain_union_key_list_sha256"],
        "evidence_root": str(root),
        "execution_contract_sha256": contract["execution_contract_sha256"],
        "execution_manifest_sha256": contract["execution_manifest_sha256"],
        "ladder_axis_descriptors": plan["ladder_axis_descriptors"],
        "ladder_axis_map_sha256": plan["ladder_axis_map_sha256"],
        "shard": contract["shard"],
        "shard_keys": contract["shard_keys"],
        "source_hashes": contract["source_hashes"],
    }


def _validate_solver_payload(
    payload: Mapping[str, object],
    *,
    checkpoint: Mapping[str, object],
    terminal: Mapping[str, object],
    plan: Mapping[str, object],
    selection: OuterSelection,
    key: RadialKey,
) -> tuple[Counter[str], Counter[str]]:
    expected_fields = {
        "acceptance_state",
        "actual_precision",
        "baseline_solver_call_count",
        "convention_budget",
        "failures",
        "key",
        "ladder_nodes",
        "numerical_budget",
        "observable_statuses",
        "outer_selection",
        "policy_sha256",
        "results",
        "schema_version",
        "scope_qualification",
        "total_solver_call_count",
        "transition_key",
    }
    if set(payload) != expected_fields or payload.get("schema_version") != (
        SOLVER_PAYLOAD_SCHEMA
    ):
        raise ConditioningCampaignError("conditioning solver payload schema changed")
    if (
        payload["key"] != key.to_record()
        or payload["transition_key"] is not plan["transition_key"]
        or payload["outer_selection"] != plan["outer_selection"]
        or payload["policy_sha256"] != DEFAULT_POLICY.sha256
    ):
        raise ConditioningCampaignError("conditioning solver payload context changed")
    scope = _exact_mapping(
        payload["scope_qualification"],
        {
            "mode_level_s_matrix_only",
            "observer_response_claim",
            "production_finite_radius_states",
            "required_radius_M",
        },
        "solver scope qualification",
    )
    if scope != {
        "mode_level_s_matrix_only": True,
        "observer_response_claim": False,
        "production_finite_radius_states": "NOT_ASSESSED",
        "required_radius_M": 40.0,
    }:
        raise ConditioningCampaignError("finite-radius/observer scope was promoted")
    projected = checkpoint_fields_from_solver_payload(payload)
    if any(checkpoint.get(name) != value for name, value in projected.items()):
        raise ConditioningCampaignError(
            "checkpoint is not the exact payload projection"
        )
    nodes = payload["ladder_nodes"]
    failures = payload["failures"]
    results = payload["results"]
    if (
        not isinstance(nodes, list)
        or not isinstance(failures, Mapping)
        or not isinstance(results, Mapping)
    ):
        raise ConditioningCampaignError("solver result/failure inventory changed")
    node_ids = [
        node.get("node_id") if isinstance(node, Mapping) else None for node in nodes
    ]
    pass_ids = {
        str(node["node_id"])
        for node in nodes
        if isinstance(node, Mapping) and node.get("status") == "PASS"
    }
    fail_ids = {
        str(node["node_id"])
        for node in nodes
        if isinstance(node, Mapping) and node.get("status") == "FAIL"
    }
    if (
        len(node_ids) != len(set(node_ids))
        or set(results) != pass_ids
        or set(failures) != fail_ids
        or any(
            not isinstance(reason, str) or not reason for reason in failures.values()
        )
    ):
        raise ConditioningCampaignError(
            "solver node results do not partition the ladder"
        )
    planned_calls = len(plan["solve_nodes"]) if selection.supported else 0
    if (
        payload["total_solver_call_count"] != planned_calls
        or terminal["solver_call_count_this_run"] != planned_calls
        or payload["baseline_solver_call_count"] != (1 if selection.supported else 0)
    ):
        raise ConditioningCampaignError("solver-call accounting changed")
    for node_id, raw_result in results.items():
        result = _exact_mapping(
            raw_result,
            {
                "A_in",
                "A_out",
                "S",
                "T_horizon",
                "additional_requested_finite_radius_states",
                "configuration",
                "diagnostics",
                "key",
                "log_phase",
                "required_radius_state",
                "schema_version",
            },
            "conditioned node result",
        )
        if (
            result["schema_version"]
            != "schwgw_phase6_conditioned_radial_node_result_v1"
            or result["key"] != key.to_record()
            or result["configuration"]
            != next(node for node in plan["solve_nodes"] if node["node_id"] == node_id)
            or result["additional_requested_finite_radius_states"] != []
        ):
            raise ConditioningCampaignError("conditioned node result identity changed")
        diagnostics = result["diagnostics"]
        if not isinstance(diagnostics, Mapping) or (
            diagnostics.get("paper_specific_envelope_used") is not False
            or diagnostics.get("scientific_acceptance") is not False
            or diagnostics.get("backend") != "scipy_float64_conditioned_radial_v1"
        ):
            raise ConditioningCampaignError(
                "node result used forbidden acceptance path"
            )
    return Counter(str(value) for value in failures.values()), Counter(
        str(node["status"]) for node in nodes if isinstance(node, Mapping)
    )


def _validate_run_contract(
    contract: Mapping[str, object],
    *,
    root: Path,
    frozen: FrozenScanContract,
    shard_id: str,
) -> tuple[
    Mapping[str, object],
    tuple[RadialKey, ...],
    tuple[tuple[Mapping[str, object], OuterSelection], ...],
]:
    fields = {
        "actual_precision",
        "backend_hashes",
        "code_hashes",
        "config_hashes",
        "context_sha256",
        "created_at_utc",
        "domain_contract_sha256",
        "domain_union_key_list_sha256",
        "execution_contract_sha256",
        "execution_manifest_sha256",
        "execution_mode",
        "global_green_permitted",
        "key_plans",
        "observable_definitions",
        "output_root",
        "paper_figure_runs",
        "policy",
        "policy_sha256",
        "resume_from",
        "runtime_identity",
        "schema",
        "shard",
        "shard_keys",
        "source_hashes",
        "source_identities",
        "status",
        "transition_contract_sha256",
    }
    item = _exact_mapping(contract, fields, "conditioning run contract")
    expected_shard = dict(frozen.shard_record(shard_id))
    keys = frozen.shard_keys(shard_id)
    if (
        item["schema"] != RUN_CONTRACT_SCHEMA
        or item["shard"] != expected_shard
        or item["shard_keys"] != [key.to_record() for key in keys]
        or item["global_green_permitted"] is not False
        or item["paper_figure_runs"] != 0
        or item["status"] != "FROZEN_SHARD_PLAN_NO_ACCEPTANCE_CLAIM"
        or item["output_root"] != str(root)
        or item["resume_from"] is not None
        or item["policy"] != DEFAULT_POLICY.to_record()
        or item["policy_sha256"] != DEFAULT_POLICY.sha256
        or item["context_sha256"] != scan_context_hash(item)
    ):
        raise ConditioningCampaignError("conditioning run contract claims changed")
    if item["actual_precision"] != {
        "backend": "scipy_float64_conditioned_radial_v1",
        "digits": 16,
    }:
        raise ConditioningCampaignError("conditioning arithmetic identity changed")
    mode = _exact_mapping(
        item["execution_mode"],
        {
            "scientific_use_permitted",
            "selector_injected",
            "solver_injected",
            "status",
        },
        "execution mode",
    )
    if mode != {
        "scientific_use_permitted": True,
        "selector_injected": False,
        "solver_injected": False,
        "status": "PRODUCTION_GENERIC_CONDITIONED_BACKEND",
    }:
        raise ConditioningCampaignError("conditioning run was not production generic")
    observable_definitions = _exact_mapping(
        item["observable_definitions"],
        {
            "flux_residual",
            "normalization",
            "production_finite_radius_states",
            "radial_s_matrix",
            "required_radius_state",
        },
        "observable definitions",
    )
    if (
        observable_definitions["production_finite_radius_states"] != "NOT_ASSESSED"
        or observable_definitions["required_radius_state"]
        != "Schwarzschild radius r/M=40"
    ):
        raise ConditioningCampaignError("run contract promoted finite-radius output")
    expected_context = {
        "domain_contract_sha256": frozen.domain_identities["domain_contract.json"][
            "sha256"
        ],
        "domain_union_key_list_sha256": frozen.domain_identities["D_union.jsonl"][
            "sha256"
        ],
        "execution_contract_sha256": frozen.execution_identities[
            "execution_contract.json"
        ]["sha256"],
        "execution_manifest_sha256": frozen.execution_identities["manifest.json"][
            "sha256"
        ],
        "transition_contract_sha256": frozen.execution_identities[
            "D_transition_calibration.jsonl"
        ]["sha256"],
    }
    if any(item[name] != value for name, value in expected_context.items()):
        raise ConditioningCampaignError("frozen domain/execution binding changed")
    source_identities = _strict_source_identities(item["source_identities"])
    implementation_hashes = {
        f"source:{name}": digest
        for name, digest in source_hash_map(source_identities).items()
    }
    frozen_hashes = {
        **{
            f"domain:{name}": identity["sha256"]
            for name, identity in sorted(frozen.domain_identities.items())
        },
        **{
            f"execution:{name}": identity["sha256"]
            for name, identity in sorted(frozen.execution_identities.items())
        },
    }
    if item["source_hashes"] != {**frozen_hashes, **implementation_hashes}:
        raise ConditioningCampaignError("run source-hash map changed")
    if item["backend_hashes"] != {
        "conditioned_backend": source_identities["conditioned_backend"]["sha256"],
        "matching": source_identities["matching"]["sha256"],
        "potentials": source_identities["potentials"]["sha256"],
    } or item["code_hashes"] != {
        "scan_module": source_identities["scan_module"]["sha256"],
        "shard_runner": source_identities["shard_runner"]["sha256"],
    }:
        raise ConditioningCampaignError("run backend/code hashes changed")
    if item["config_hashes"] != {"conditioning_policy": DEFAULT_POLICY.sha256}:
        raise ConditioningCampaignError("run configuration hash changed")
    runtime = item["runtime_identity"]
    if not isinstance(runtime, Mapping) or set(runtime) != {
        "actual_arithmetic",
        "numpy",
        "python",
        "scipy",
    }:
        raise ConditioningCampaignError("runtime identity schema changed")
    plans = item["key_plans"]
    if not isinstance(plans, list) or len(plans) != len(keys):
        raise ConditioningCampaignError("run key-plan cardinality changed")
    domain_ordinals = {key: ordinal for ordinal, key in enumerate(frozen.union_keys)}
    validated_plans = tuple(
        _validate_plan(
            plan,
            key=key,
            shard_ordinal=ordinal,
            domain_ordinal=domain_ordinals[key],
            transition_key=key in frozen.transition_keys,
        )
        for ordinal, (plan, key) in enumerate(zip(plans, keys, strict=True))
    )
    return item, keys, validated_plans


@dataclass(frozen=True)
class ValidatedConditioningShard:
    """A complete shard whose immutable key-level chain was reloaded."""

    root: Path
    shard: Mapping[str, object]
    keys: tuple[RadialKey, ...]
    top_identities: Mapping[str, Mapping[str, object]]
    context_sha256: str
    source_hashes: Mapping[str, str]
    backend_hashes: Mapping[str, str]
    code_hashes: Mapping[str, str]
    config_hashes: Mapping[str, str]
    runtime_identity: Mapping[str, object]
    solver_call_count: int
    elapsed_seconds: float
    terminal_status_counts: Mapping[str, int]
    key_acceptance_counts: Mapping[str, int]
    numerical_status_counts: Mapping[str, int]
    convention_status_counts: Mapping[str, int]
    observable_status_counts: Mapping[str, Mapping[str, int]]
    numerical_components: Mapping[str, tuple[float, ...]]
    convention_components: Mapping[str, tuple[float, ...]]
    failure_reason_counts: Mapping[str, int]
    transition_key_count: int
    transition_solver_call_count: int
    transition_key_status_counts: Mapping[str, int]
    transition_node_status_counts: Mapping[str, int]
    supported_key_count: int
    unsupported_key_count: int
    selected_r_out_counts: Mapping[str, int]

    @property
    def shard_id(self) -> str:
        return str(self.shard["shard_id"])

    @property
    def scientific_failure_key_count(self) -> int:
        return int(self.key_acceptance_counts.get("FAIL", 0))

    def to_entry(self) -> dict[str, object]:
        return {
            "acceptance_status_counts": dict(self.key_acceptance_counts),
            "context_sha256": self.context_sha256,
            "elapsed_seconds": self.elapsed_seconds,
            "execution_integrity": "PASS_COMPLETE_IMMUTABLE_SHARD",
            "failure_reason_counts": dict(sorted(self.failure_reason_counts.items())),
            "identities": {
                name: dict(identity)
                for name, identity in sorted(self.top_identities.items())
            },
            "observable_status_counts": {
                name: dict(counts)
                for name, counts in sorted(self.observable_status_counts.items())
            },
            "root": str(self.root),
            "runtime_identity_sha256": sha256_bytes(
                canonical_json_bytes(self.runtime_identity)
            ),
            "schema": CAMPAIGN_SHARD_ENTRY_SCHEMA,
            "scientific_failure_key_count": self.scientific_failure_key_count,
            "shard": dict(self.shard),
            "solver_call_count": self.solver_call_count,
            "terminal_completion_counts": dict(self.terminal_status_counts),
            "transition": {
                "key_count": self.transition_key_count,
                "key_status_counts": dict(self.transition_key_status_counts),
                "node_status_counts": dict(self.transition_node_status_counts),
                "solver_call_count": self.transition_solver_call_count,
            },
        }


def _validate_top_aggregates(
    *,
    root: Path,
    contract: Mapping[str, object],
    terminals: Sequence[Mapping[str, object]],
    terminal_identities: Sequence[Mapping[str, object]],
    checkpoints: Sequence[Mapping[str, object]],
    checkpoint_identities: Sequence[Mapping[str, object]],
) -> tuple[
    Mapping[str, object],
    Mapping[str, object],
    Mapping[str, object],
    Mapping[str, Mapping[str, object]],
]:
    result_path = root / "shard_result.json"
    checkpoint_path = root / "shard_checkpoint.json"
    manifest_path = root / "manifest.json"
    result = _strict_json(result_path)
    shard_checkpoint = _strict_json(checkpoint_path)
    manifest = _strict_json(manifest_path)
    result_identity = _strict_file_identity(result_path)
    checkpoint_identity = _strict_file_identity(checkpoint_path)
    manifest_identity = _strict_file_identity(manifest_path)
    run_contract_identity = _strict_file_identity(root / "run_contract.json")
    observable_statuses = {
        name: _worst_state(
            [str(checkpoint["observable_statuses"][name]) for checkpoint in checkpoints]
        )
        for name in OBSERVABLE_NAMES
    }
    solver_calls = sum(int(item["solver_call_count_this_run"]) for item in terminals)
    expected_result = {
        "acceptance_state": _worst_state(
            [str(checkpoint["acceptance_state"]) for checkpoint in checkpoints]
        ),
        "global_green_permitted": False,
        "key_terminal_identities": [dict(identity) for identity in terminal_identities],
        "observable_statuses": observable_statuses,
        "paper_figure_runs": 0,
        "schema": SHARD_RESULT_SCHEMA,
        "shard": contract["shard"],
        "summary": {
            "blocked_nonreusable_predecessor_count": 0,
            "key_count": len(terminals),
            "reused_strict_pass_count": 0,
            "solver_call_count_this_run": solver_calls,
        },
    }
    if result != expected_result:
        raise ConditioningCampaignError("shard result is not the exact key reduction")
    scientific_failures = any(
        terminal["execution_status"] == "COMPLETED_FAIL_CLOSED"
        for terminal in terminals
    )
    numerical_statuses = [
        str(checkpoint["numerical_budget"]["status"]) for checkpoint in checkpoints
    ]
    convention_statuses = [
        str(checkpoint["convention_budget"]["status"]) for checkpoint in checkpoints
    ]
    numerical_components = {
        name: (
            FLOAT64_UNASSESSED_SENTINEL
            if scientific_failures
            else max(
                float(checkpoint["numerical_budget"]["components"][name])
                for checkpoint in checkpoints
            )
        )
        for name in NUMERICAL_BUDGET_FIELDS
    }
    convention_components = {
        name: (
            FLOAT64_UNASSESSED_SENTINEL
            if scientific_failures
            else max(
                float(checkpoint["convention_budget"]["components"][name])
                for checkpoint in checkpoints
            )
        )
        for name in CONVENTION_BUDGET_FIELDS
    }
    expected_checkpoint = {
        "attempts": [
            {"attempt": 1, "status": "FAIL" if scientific_failures else "PARTIAL"}
        ],
        "backend_hashes": contract["backend_hashes"],
        "code_hashes": contract["code_hashes"],
        "config_hashes": contract["config_hashes"],
        "convention_budget": {
            "components": convention_components,
            "status": (
                "FAIL" if scientific_failures else _worst_state(convention_statuses)
            ),
        },
        "domain_contract_sha256": contract["domain_contract_sha256"],
        "domain_union_key_list_sha256": contract["domain_union_key_list_sha256"],
        "global_green_permitted": False,
        "key_checkpoint_identities": [
            dict(identity) for identity in checkpoint_identities
        ],
        "key_list_sha256": contract["shard"]["key_list_sha256"],
        "numerical_budget": {
            "components": numerical_components,
            "status": (
                "FAIL" if scientific_failures else _worst_state(numerical_statuses)
            ),
        },
        "observable_statuses": observable_statuses,
        "result_identity": result_identity,
        "schema": SHARD_CHECKPOINT_SCHEMA,
        "shard_id": contract["shard"]["shard_id"],
        "source_hashes": contract["source_hashes"],
    }
    if shard_checkpoint != expected_checkpoint:
        raise ConditioningCampaignError(
            "shard checkpoint is not the exact separate-budget reduction"
        )
    manifest_fields = {
        "created_at_utc",
        "elapsed_seconds",
        "global_green_permitted",
        "key_terminal_identities",
        "paper_figure_runs",
        "run_contract_identity",
        "schema",
        "shard_checkpoint_identity",
        "shard_result_identity",
    }
    if set(manifest) != manifest_fields or (
        manifest.get("schema") != "schwgw_phase6_conditioning_shard_manifest_v1"
        or manifest.get("global_green_permitted") is not False
        or manifest.get("paper_figure_runs") != 0
        or manifest.get("key_terminal_identities")
        != [dict(identity) for identity in terminal_identities]
    ):
        raise ConditioningCampaignError("conditioning shard manifest changed")
    _finite_number(manifest["elapsed_seconds"], "shard elapsed seconds")
    if (
        not isinstance(manifest["created_at_utc"], str)
        or not manifest["created_at_utc"]
    ):
        raise ConditioningCampaignError("shard creation time is missing")
    _validate_identity(
        manifest["run_contract_identity"],
        path=root / "run_contract.json",
        label="manifest run contract",
    )
    _validate_identity(
        manifest["shard_result_identity"],
        path=result_path,
        label="manifest shard result",
    )
    _validate_identity(
        manifest["shard_checkpoint_identity"],
        path=checkpoint_path,
        label="manifest shard checkpoint",
    )
    return (
        result,
        shard_checkpoint,
        manifest,
        {
            "manifest.json": manifest_identity,
            "run_contract.json": run_contract_identity,
            "shard_checkpoint.json": checkpoint_identity,
            "shard_result.json": result_identity,
        },
    )


def validate_conditioning_shard_root(
    root: str | Path,
    *,
    frozen: FrozenScanContract | None = None,
    expected_shard_id: str | None = None,
) -> ValidatedConditioningShard:
    """Reload one complete local shard and return independently derived counts."""

    frozen_contract = frozen or load_frozen_scan_contract(DOMAIN_ROOT, EXECUTION_ROOT)
    shard_root = _immutable_root(root, label="conditioning shard root")
    contract = _strict_json(shard_root / "run_contract.json")
    shard_raw = contract.get("shard")
    if not isinstance(shard_raw, Mapping) or not isinstance(
        shard_raw.get("shard_id"), str
    ):
        raise ConditioningCampaignError("run contract does not identify a shard")
    shard_id = str(shard_raw["shard_id"])
    if expected_shard_id is not None and shard_id != expected_shard_id:
        raise ConditioningCampaignError("root was mapped to the wrong shard id")
    try:
        frozen_contract.shard_record(shard_id)
    except Exception as exc:
        raise ConditioningCampaignError(
            f"unknown conditioning shard: {shard_id}"
        ) from exc
    contract, keys, plans = _validate_run_contract(
        contract,
        root=shard_root,
        frozen=frozen_contract,
        shard_id=shard_id,
    )
    actual_names = {child.name for child in shard_root.iterdir()}
    if any(not child.is_file() or child.is_symlink() for child in shard_root.iterdir()):
        raise ConditioningCampaignError(
            "shard root contains non-file or aliased entries"
        )
    expected_names = {
        "manifest.json",
        "run_contract.json",
        "shard_checkpoint.json",
        "shard_result.json",
    }
    for ordinal, key in enumerate(keys):
        expected_names.update(key_artifact_filenames(ordinal, key).values())
    if actual_names != expected_names:
        missing = sorted(expected_names - actual_names)
        extra = sorted(actual_names - expected_names)
        raise ConditioningCampaignError(
            f"shard artifact inventory changed; missing={missing[:5]} extra={extra[:5]}"
        )
    terminals: list[Mapping[str, object]] = []
    terminal_identities: list[Mapping[str, object]] = []
    checkpoints: list[Mapping[str, object]] = []
    checkpoint_identities: list[Mapping[str, object]] = []
    failure_reasons: Counter[str] = Counter()
    transition_node_statuses: Counter[str] = Counter()
    transition_key_statuses: list[str] = []
    transition_calls = 0
    selected_r_outs: Counter[str] = Counter()
    supported = 0
    unsupported = 0
    numerical_components = {name: [] for name in NUMERICAL_BUDGET_FIELDS}
    convention_components = {name: [] for name in CONVENTION_BUDGET_FIELDS}
    observable_values = {name: [] for name in OBSERVABLE_NAMES}
    for ordinal, (key, plan_pair) in enumerate(zip(keys, plans, strict=True)):
        plan, selection = plan_pair
        filenames = key_artifact_filenames(ordinal, key)
        terminal_path = shard_root / filenames["terminal"]
        terminal = _strict_json(terminal_path)
        terminal_fields = {
            "checkpoint_identity",
            "domain_ordinal",
            "execution_status",
            "failure",
            "global_green_permitted",
            "key",
            "predecessor",
            "schema",
            "shard_ordinal",
            "solver_call_count_this_run",
        }
        if set(terminal) != terminal_fields or (
            terminal.get("schema") != KEY_TERMINAL_SCHEMA
            or terminal.get("execution_status") not in LOCAL_TERMINAL_STATUSES
            or terminal.get("global_green_permitted") is not False
            or terminal.get("key") != key.to_record()
            or terminal.get("shard_ordinal") != ordinal
            or terminal.get("domain_ordinal") != plan["domain_ordinal"]
            or terminal.get("failure") is not None
            or terminal.get("predecessor") is not None
        ):
            raise ConditioningCampaignError(
                "campaign requires a complete local scientific terminal"
            )
        checkpoint_path = shard_root / filenames["checkpoint"]
        checkpoint_identity = _validate_identity(
            terminal["checkpoint_identity"],
            path=checkpoint_path,
            label="terminal checkpoint",
        )
        checkpoint = _strict_json(checkpoint_path)
        result_path = shard_root / filenames["result"]
        try:
            validate_key_checkpoint(
                checkpoint,
                expected_context=_expected_context(contract, plan, root=shard_root),
                result_path=result_path,
            )
        except Exception as exc:
            raise ConditioningCampaignError(
                f"key checkpoint failed frozen validation: {key.to_record()}"
            ) from exc
        acceptance = checkpoint["acceptance_state"]
        if acceptance not in {"PARTIAL", "FAIL"} or (
            (acceptance == "FAIL")
            != (terminal["execution_status"] == "COMPLETED_FAIL_CLOSED")
        ):
            raise ConditioningCampaignError(
                "scientific FAIL/completed terminal classification changed"
            )
        observables = checkpoint["observable_statuses"]
        if not isinstance(observables, Mapping) or set(observables) != set(
            OBSERVABLE_NAMES
        ):
            raise ConditioningCampaignError("key observable inventory changed")
        if observables["production_finite_radius_states"] != "NOT_ASSESSED":
            raise ConditioningCampaignError(
                "conditioning scan cannot promote finite-radius production states"
            )
        result = _strict_json(result_path)
        payload_identity = result.get("payload_identity")
        if not isinstance(payload_identity, Mapping):
            raise ConditioningCampaignError("key result lacks payload identity")
        payload_path = shard_root / filenames["payload"]
        _validate_identity(
            payload_identity,
            path=payload_path,
            label="result payload",
        )
        envelope = _strict_json(payload_path)
        if (
            envelope.get("schema") != KEY_PAYLOAD_ENVELOPE_SCHEMA
            or envelope.get("solver_payload_schema") != SOLVER_PAYLOAD_SCHEMA
            or envelope.get("key") != key.to_record()
            or envelope.get("shard") != contract["shard"]
        ):
            raise ConditioningCampaignError("key payload envelope changed")
        solver_payload = envelope.get("solver_payload")
        if not isinstance(solver_payload, Mapping):
            raise ConditioningCampaignError("key solver payload is missing")
        reasons, node_statuses = _validate_solver_payload(
            solver_payload,
            checkpoint=checkpoint,
            terminal=terminal,
            plan=plan,
            selection=selection,
            key=key,
        )
        failure_reasons.update(reasons)
        if key in frozen_contract.transition_keys:
            transition_calls += int(terminal["solver_call_count_this_run"])
            transition_key_statuses.append(str(acceptance))
            transition_node_statuses.update(node_statuses)
        if selection.supported:
            supported += 1
            selected_r_outs[format(selection.selected_r_out_M, ".17g")] += 1
        else:
            unsupported += 1
        for name in NUMERICAL_BUDGET_FIELDS:
            numerical_components[name].append(
                float(checkpoint["numerical_budget"]["components"][name])
            )
        for name in CONVENTION_BUDGET_FIELDS:
            convention_components[name].append(
                float(checkpoint["convention_budget"]["components"][name])
            )
        for name in OBSERVABLE_NAMES:
            observable_values[name].append(str(observables[name]))
        terminals.append(terminal)
        terminal_identities.append(_strict_file_identity(terminal_path))
        checkpoints.append(checkpoint)
        checkpoint_identities.append(checkpoint_identity)
    _, _, manifest, top_identities = _validate_top_aggregates(
        root=shard_root,
        contract=contract,
        terminals=terminals,
        terminal_identities=terminal_identities,
        checkpoints=checkpoints,
        checkpoint_identities=checkpoint_identities,
    )
    return ValidatedConditioningShard(
        root=shard_root,
        shard=dict(contract["shard"]),
        keys=keys,
        top_identities=top_identities,
        context_sha256=str(contract["context_sha256"]),
        source_hashes=dict(contract["source_hashes"]),
        backend_hashes=dict(contract["backend_hashes"]),
        code_hashes=dict(contract["code_hashes"]),
        config_hashes=dict(contract["config_hashes"]),
        runtime_identity=dict(contract["runtime_identity"]),
        solver_call_count=sum(
            int(terminal["solver_call_count_this_run"]) for terminal in terminals
        ),
        elapsed_seconds=float(manifest["elapsed_seconds"]),
        terminal_status_counts={
            status: sum(
                terminal["execution_status"] == status for terminal in terminals
            )
            for status in LOCAL_TERMINAL_STATUSES
        },
        key_acceptance_counts=_state_counts(
            [str(checkpoint["acceptance_state"]) for checkpoint in checkpoints]
        ),
        numerical_status_counts=_state_counts(
            [
                str(checkpoint["numerical_budget"]["status"])
                for checkpoint in checkpoints
            ]
        ),
        convention_status_counts=_state_counts(
            [
                str(checkpoint["convention_budget"]["status"])
                for checkpoint in checkpoints
            ]
        ),
        observable_status_counts={
            name: _state_counts(values) for name, values in observable_values.items()
        },
        numerical_components={
            name: tuple(values) for name, values in numerical_components.items()
        },
        convention_components={
            name: tuple(values) for name, values in convention_components.items()
        },
        failure_reason_counts=dict(failure_reasons),
        transition_key_count=len(transition_key_statuses),
        transition_solver_call_count=transition_calls,
        transition_key_status_counts=_state_counts(transition_key_statuses),
        transition_node_status_counts={
            state: transition_node_statuses[state] for state in ACCEPTANCE_STATES
        },
        supported_key_count=supported,
        unsupported_key_count=unsupported,
        selected_r_out_counts=dict(
            sorted(selected_r_outs.items(), key=lambda x: Decimal(x[0]))
        ),
    )


def campaign_shard_root_name(shard: Mapping[str, object]) -> str:
    """Return the one strict V1 campaign dirname for a frozen shard record."""

    if not isinstance(shard.get("kM"), str) or shard.get("sector") not in {
        "odd",
        "even",
    }:
        raise ConditioningCampaignError("cannot name an invalid shard record")
    token = str(shard["kM"]).replace("-", "m").replace(".", "p")
    return f"{CAMPAIGN_ROOT_PREFIX}k{token}_{shard['sector']}{CAMPAIGN_ROOT_SUFFIX}"


def resolve_roots_parent(
    parent: str | Path,
    *,
    frozen: FrozenScanContract | None = None,
) -> tuple[Path, ...]:
    """Resolve exactly the frozen campaign namespace under one direct parent."""

    frozen_contract = frozen or load_frozen_scan_contract(DOMAIN_ROOT, EXECUTION_ROOT)
    roots_parent = _direct_absolute(parent, kind="conditioning roots parent")
    if not roots_parent.is_dir():
        raise ConditioningCampaignError("conditioning roots parent is not a directory")
    expected = {
        campaign_shard_root_name(record): roots_parent
        / campaign_shard_root_name(record)
        for record in frozen_contract.shard_records
    }
    campaign_children = {
        child.name: child
        for child in roots_parent.iterdir()
        if child.name.startswith(CAMPAIGN_ROOT_PREFIX)
    }
    if set(campaign_children) != set(expected):
        missing = sorted(set(expected) - set(campaign_children))
        extra = sorted(set(campaign_children) - set(expected))
        raise ConditioningCampaignError(
            f"roots-parent campaign namespace mismatch; missing={missing[:5]} "
            f"extra={extra[:5]}"
        )
    return tuple(
        expected[campaign_shard_root_name(record)]
        for record in frozen_contract.shard_records
    )


def resolve_explicit_shard_roots(paths: Sequence[str | Path]) -> tuple[Path, ...]:
    """Require 86 unique explicit roots; shard mapping is checked on reload."""

    if len(paths) != EXPECTED_SHARD_COUNT:
        raise ConditioningCampaignError("exactly 86 --shard-root values are required")
    roots = tuple(_direct_absolute(path, kind="explicit shard root") for path in paths)
    if len(set(roots)) != len(roots):
        raise ConditioningCampaignError("explicit shard roots contain duplicates")
    return roots


def validate_campaign_shards(
    shard_roots: Sequence[str | Path],
    *,
    frozen: FrozenScanContract | None = None,
) -> tuple[ValidatedConditioningShard, ...]:
    """Map, reject duplicates/missing roots, and validate all 86 shards."""

    frozen_contract = frozen or load_frozen_scan_contract(DOMAIN_ROOT, EXECUTION_ROOT)
    if len(shard_roots) != EXPECTED_SHARD_COUNT:
        raise ConditioningCampaignError("campaign must provide exactly 86 shard roots")
    root_by_shard: dict[str, Path] = {}
    for raw_root in shard_roots:
        root = _immutable_root(raw_root, label="conditioning shard root")
        contract = _strict_json(root / "run_contract.json")
        shard = contract.get("shard")
        shard_id = shard.get("shard_id") if isinstance(shard, Mapping) else None
        if not isinstance(shard_id, str):
            raise ConditioningCampaignError("shard root lacks a shard id")
        if shard_id in root_by_shard:
            raise ConditioningCampaignError(f"duplicate shard root for {shard_id}")
        root_by_shard[shard_id] = root
    expected_ids = [str(record["shard_id"]) for record in frozen_contract.shard_records]
    if set(root_by_shard) != set(expected_ids):
        missing = sorted(set(expected_ids) - set(root_by_shard))
        extra = sorted(set(root_by_shard) - set(expected_ids))
        raise ConditioningCampaignError(
            f"campaign shard-id coverage changed; missing={missing} extra={extra}"
        )
    return tuple(
        validate_conditioning_shard_root(
            root_by_shard[shard_id],
            frozen=frozen_contract,
            expected_shard_id=shard_id,
        )
        for shard_id in expected_ids
    )


def _bound_frozen_inputs(frozen: FrozenScanContract) -> dict[str, object]:
    aggregation = _immutable_root(
        AGGREGATION_ROOT,
        label="Phase-6 aggregation-v8 contract root",
    )
    if {child.name for child in aggregation.iterdir()} != set(AGGREGATION_IDENTITIES):
        raise ConditioningCampaignError("aggregation-v8 root inventory changed")
    aggregation_files: dict[str, Mapping[str, object]] = {}
    for filename, digest in AGGREGATION_IDENTITIES.items():
        identity = _strict_file_identity(aggregation / filename)
        if identity["sha256"] != digest:
            raise ConditioningCampaignError("aggregation-v8 identity changed")
        aggregation_files[filename] = identity
    aggregation_manifest = _strict_json(aggregation / "manifest.json")
    if (
        aggregation_manifest.get("global_green_permitted") is not False
        or aggregation_manifest.get("solver_runs") != 0
        or aggregation_manifest.get("contract")
        != aggregation_files["aggregation_contract.json"]
    ):
        raise ConditioningCampaignError("aggregation-v8 manifest claims changed")
    return {
        "aggregation_v8": {
            "files": aggregation_files,
            "root": str(aggregation),
        },
        "domain_v3": {
            "files": {
                name: dict(identity)
                for name, identity in sorted(frozen.domain_identities.items())
            },
            "root": str(frozen.domain_root),
        },
        "execution_v4": {
            "files": {
                name: dict(identity)
                for name, identity in sorted(frozen.execution_identities.items())
            },
            "root": str(frozen.execution_root),
        },
    }


def _budget_summary(
    shards: Sequence[ValidatedConditioningShard],
    *,
    kind: str,
) -> dict[str, object]:
    if kind == "numerical":
        fields = NUMERICAL_BUDGET_FIELDS
        statuses = [shard.numerical_status_counts for shard in shards]
        component_maps = [shard.numerical_components for shard in shards]
    elif kind == "convention":
        fields = CONVENTION_BUDGET_FIELDS
        statuses = [shard.convention_status_counts for shard in shards]
        component_maps = [shard.convention_components for shard in shards]
    else:
        raise ConditioningCampaignError("unknown budget kind")
    components: dict[str, object] = {}
    for name in fields:
        values = [value for mapping in component_maps for value in mapping[name]]
        assessed = [value for value in values if value != FLOAT64_UNASSESSED_SENTINEL]
        components[name] = {
            "assessed_count": len(assessed),
            "maximum_assessed": max(assessed) if assessed else None,
            "minimum_assessed": min(assessed) if assessed else None,
            "unassessed_sentinel_count": len(values) - len(assessed),
        }
    return {
        "components": components,
        "status_counts": _merge_state_counts(statuses),
    }


def _validate_campaign_source_identities(
    value: Mapping[str, Mapping[str, object]],
) -> dict[str, Mapping[str, object]]:
    if set(value) != {"campaign_module", "campaign_runner"}:
        raise ConditioningCampaignError("campaign source identity names changed")
    result: dict[str, Mapping[str, object]] = {}
    for name, identity in sorted(value.items()):
        record = _exact_mapping(
            identity,
            {"mode", "nlink", "path", "sha256", "size"},
            f"campaign source {name}",
        )
        path = _direct_absolute(str(record["path"]), kind=f"campaign source {name}")
        actual = source_file_identity(path)
        if actual != dict(record):
            raise ConditioningCampaignError(f"campaign source changed: {name}")
        result[name] = actual
    return result


def campaign_index_from_validated_shards(
    shards: Sequence[ValidatedConditioningShard],
    *,
    frozen: FrozenScanContract,
    campaign_source_identities: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    """Reduce already validated shards, retaining separate uncertainty budgets."""

    if len(shards) != EXPECTED_SHARD_COUNT:
        raise ConditioningCampaignError("validated campaign must contain 86 shards")
    expected_ids = [str(record["shard_id"]) for record in frozen.shard_records]
    if [shard.shard_id for shard in shards] != expected_ids:
        raise ConditioningCampaignError("validated shard ordering/identity changed")
    if len({shard.root for shard in shards}) != len(shards):
        raise ConditioningCampaignError("validated shard roots are duplicated")
    all_keys: list[RadialKey] = []
    for shard in shards:
        expected_keys = frozen.shard_keys(shard.shard_id)
        if shard.keys != expected_keys or dict(shard.shard) != dict(
            frozen.shard_record(shard.shard_id)
        ):
            raise ConditioningCampaignError("validated shard key inventory changed")
        all_keys.extend(shard.keys)
    if tuple(all_keys) != frozen.union_keys or len(all_keys) != EXPECTED_KEY_COUNT:
        raise ConditioningCampaignError("campaign does not exactly cover D_union")
    if (
        sha256_bytes(jsonl_bytes(all_keys))
        != frozen.domain_identities["D_union.jsonl"]["sha256"]
    ):
        raise ConditioningCampaignError("campaign D_union byte identity changed")
    source_hashes = dict(shards[0].source_hashes)
    backend_hashes = dict(shards[0].backend_hashes)
    code_hashes = dict(shards[0].code_hashes)
    config_hashes = dict(shards[0].config_hashes)
    if any(
        dict(shard.source_hashes) != source_hashes
        or dict(shard.backend_hashes) != backend_hashes
        or dict(shard.code_hashes) != code_hashes
        or dict(shard.config_hashes) != config_hashes
        for shard in shards[1:]
    ):
        raise ConditioningCampaignError("campaign source/backend/config hashes drifted")
    observable_counts = {
        name: _merge_state_counts(
            [shard.observable_status_counts[name] for shard in shards]
        )
        for name in OBSERVABLE_NAMES
    }
    if observable_counts["production_finite_radius_states"] != {
        "NOT_ASSESSED": EXPECTED_KEY_COUNT,
        "PARTIAL": 0,
        "PASS": 0,
        "FAIL": 0,
    }:
        raise ConditioningCampaignError(
            "campaign promoted production finite-radius states"
        )
    transition_count = sum(shard.transition_key_count for shard in shards)
    if transition_count != EXPECTED_TRANSITION_KEY_COUNT:
        raise ConditioningCampaignError("campaign transition-key count changed")
    production_count = sum(int(shard.shard["production_key_count"]) for shard in shards)
    extension_count = sum(int(shard.shard["extension_key_count"]) for shard in shards)
    if (
        production_count != EXPECTED_PRODUCTION_KEY_COUNT
        or extension_count != EXPECTED_EXTENSION_KEY_COUNT
    ):
        raise ConditioningCampaignError("campaign production/extension counts changed")
    campaign_sources = _validate_campaign_source_identities(campaign_source_identities)
    runtime_groups: dict[str, dict[str, object]] = {}
    for shard in shards:
        digest = sha256_bytes(canonical_json_bytes(shard.runtime_identity))
        if digest not in runtime_groups:
            runtime_groups[digest] = {
                "runtime_identity": dict(shard.runtime_identity),
                "shard_count": 0,
            }
        runtime_groups[digest]["shard_count"] = (
            int(runtime_groups[digest]["shard_count"]) + 1
        )
    failure_reasons: Counter[str] = Counter()
    selected_r_outs: Counter[str] = Counter()
    for shard in shards:
        failure_reasons.update(shard.failure_reason_counts)
        selected_r_outs.update(shard.selected_r_out_counts)
    scientific_failures = sum(shard.scientific_failure_key_count for shard in shards)
    terminal_counts = {
        status: sum(shard.terminal_status_counts.get(status, 0) for shard in shards)
        for status in LOCAL_TERMINAL_STATUSES
    }
    if terminal_counts["COMPLETED_FAIL_CLOSED"] != scientific_failures:
        raise ConditioningCampaignError("scientific fail-closed accounting changed")
    implementation_source_hashes = {
        name.removeprefix("source:"): digest
        for name, digest in source_hashes.items()
        if name.startswith("source:")
    }
    implementation_source_hashes.update(
        {
            name: str(identity["sha256"])
            for name, identity in sorted(campaign_sources.items())
        }
    )
    return {
        "budget_summaries": {
            "convention": _budget_summary(shards, kind="convention"),
            "numerical": _budget_summary(shards, kind="numerical"),
        },
        "campaign_code_hashes": {
            name: identity["sha256"]
            for name, identity in sorted(campaign_sources.items())
        },
        "campaign_source_identities": campaign_sources,
        "contract_only": False,
        "coverage": {
            "D_union_exact_coverage": True,
            "D_union_key_list_sha256": frozen.domain_identities["D_union.jsonl"][
                "sha256"
            ],
            "extension_key_count": extension_count,
            "key_count": len(all_keys),
            "production_key_count": production_count,
            "shard_count": len(shards),
            "transition_key_count": transition_count,
        },
        "execution_integrity": {
            "completed_shard_count": len(shards),
            "execution_failure_key_count": 0,
            "execution_failure_shard_count": 0,
            "scientific_failures_are_not_execution_failures": True,
            "status": "PASS_COMPLETE_IMMUTABLE_CAMPAIGN",
        },
        "failure_summary": {
            "exact_reason_counts": dict(sorted(failure_reasons.items())),
            "scientific_failure_key_count": scientific_failures,
        },
        "frozen_inputs": _bound_frozen_inputs(frozen),
        "generic_conditioning_source_hashes": source_hashes,
        "global_green_permitted": False,
        "implementation_source_sha_hashes": dict(
            sorted(implementation_source_hashes.items())
        ),
        "kernel_unit_test_only": False,
        "li_figure_agreement_primary_gate": False,
        "observable_status_counts": observable_counts,
        "paper_agreement_gate": False,
        "production_finite_radius_states": "NOT_ASSESSED",
        "overall_state": "FAIL" if scientific_failures else "PARTIAL",
        "runtime_identity_groups": {
            digest: value for digest, value in sorted(runtime_groups.items())
        },
        "schema": CAMPAIGN_INDEX_SCHEMA,
        "science_executed": True,
        "scientific_evidence": True,
        "scope_qualification": {
            "observer_response_claim": False,
            "radial_s_matrix_only": True,
            "required_radius_M": 40.0,
        },
        "selection_summary": {
            "selected_r_out_counts": dict(
                sorted(selected_r_outs.items(), key=lambda item: Decimal(item[0]))
            ),
            "supported_key_count": sum(shard.supported_key_count for shard in shards),
            "unsupported_key_count": sum(
                shard.unsupported_key_count for shard in shards
            ),
        },
        "shards": [shard.to_entry() for shard in shards],
        "solver_call_count": sum(shard.solver_call_count for shard in shards),
        "status": (
            "INDEX_COMPLETE_WITH_SCIENTIFIC_FAILURES"
            if scientific_failures
            else "INDEX_COMPLETE_WITHOUT_SCIENTIFIC_FAILURES"
        ),
        "terminal_completion_counts": terminal_counts,
        "transition_summary": {
            "key_count": transition_count,
            "key_status_counts": _merge_state_counts(
                [shard.transition_key_status_counts for shard in shards]
            ),
            "node_status_counts": _merge_state_counts(
                [shard.transition_node_status_counts for shard in shards]
            ),
            "solver_call_count": sum(
                shard.transition_solver_call_count for shard in shards
            ),
        },
    }


def build_conditioning_campaign_index(
    shard_roots: Sequence[str | Path],
    *,
    campaign_source_identities: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    """Validate all frozen shards and build one deterministic campaign index."""

    frozen = load_frozen_scan_contract(DOMAIN_ROOT, EXECUTION_ROOT)
    shards = validate_campaign_shards(shard_roots, frozen=frozen)
    return campaign_index_from_validated_shards(
        shards,
        frozen=frozen,
        campaign_source_identities=campaign_source_identities,
    )


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _publish_json_exclusive(path: Path, payload: object) -> dict[str, object]:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"output collision: {path}")
    data = canonical_json_bytes(payload)
    staging = path.with_name(
        f".{path.name}.o_excl_staging_{os.getpid()}_{time.time_ns()}"
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(staging, flags, 0o600)
    linked = False
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(staging, 0o444)
        _fsync_directory(path.parent)
        os.link(staging, path, follow_symlinks=False)
        linked = True
        _fsync_directory(path.parent)
    finally:
        try:
            staging.unlink()
        except FileNotFoundError:
            pass
        _fsync_directory(path.parent)
    if not linked:
        raise ConditioningCampaignError("exclusive campaign publication failed")
    identity = _strict_file_identity(path)
    if identity["sha256"] != hashlib.sha256(data).hexdigest():
        raise ConditioningCampaignError("published campaign identity changed")
    return identity


def publish_conditioning_campaign(
    output_root: str | Path,
    *,
    shard_roots: Sequence[str | Path],
    campaign_source_identities: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    """Publish a fresh two-file campaign root after complete validation."""

    output = Path(output_root)
    if not output.is_absolute() or output.resolve(strict=False) != output:
        raise ConditioningCampaignError("output root must be absolute and canonical")
    if output.exists() or output.is_symlink():
        raise FileExistsError("campaign output root must be fresh")
    parent = _direct_absolute(output.parent, kind="campaign output parent")
    if not parent.is_dir():
        raise ConditioningCampaignError("campaign output parent is not a directory")
    payload = build_conditioning_campaign_index(
        shard_roots,
        campaign_source_identities=campaign_source_identities,
    )
    output.mkdir(mode=0o700)
    os.chmod(output, 0o700)
    try:
        index_identity = _publish_json_exclusive(
            output / "conditioning_campaign_index.json", payload
        )
        manifest = {
            "campaign_index_identity": index_identity,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "global_green_permitted": False,
            "key_count": EXPECTED_KEY_COUNT,
            "li_figure_agreement_primary_gate": False,
            "schema": CAMPAIGN_MANIFEST_SCHEMA,
            "shard_count": EXPECTED_SHARD_COUNT,
            "status": payload["status"],
        }
        manifest_identity = _publish_json_exclusive(output / "manifest.json", manifest)
        os.chmod(output, 0o555)
        _fsync_directory(output)
        _fsync_directory(output.parent)
        validate_published_conditioning_campaign(output)
    except BaseException:
        for child in output.iterdir():
            if child.is_file() and not child.is_symlink():
                os.chmod(child, 0o444)
        os.chmod(output, 0o555)
        _fsync_directory(output)
        _fsync_directory(output.parent)
        raise
    return {
        "campaign_index_identity": index_identity,
        "evidence_root": str(output),
        "manifest_identity": manifest_identity,
        "scientific_failure_key_count": payload["failure_summary"][
            "scientific_failure_key_count"
        ],
        "status": payload["status"],
    }


def validate_published_conditioning_campaign(root: str | Path) -> None:
    """Reload a published campaign and independently rebuild its full index."""

    campaign_root = _immutable_root(root, label="conditioning campaign root")
    if {child.name for child in campaign_root.iterdir()} != {
        "conditioning_campaign_index.json",
        "manifest.json",
    }:
        raise ConditioningCampaignError("campaign root inventory changed")
    index_path = campaign_root / "conditioning_campaign_index.json"
    manifest_path = campaign_root / "manifest.json"
    payload = _strict_json(index_path)
    manifest = _strict_json(manifest_path)
    if payload.get("schema") != CAMPAIGN_INDEX_SCHEMA:
        raise ConditioningCampaignError("campaign index schema changed")
    expected_manifest_fields = {
        "campaign_index_identity",
        "created_at_utc",
        "global_green_permitted",
        "key_count",
        "li_figure_agreement_primary_gate",
        "schema",
        "shard_count",
        "status",
    }
    if set(manifest) != expected_manifest_fields or (
        manifest.get("schema") != CAMPAIGN_MANIFEST_SCHEMA
        or manifest.get("global_green_permitted") is not False
        or manifest.get("li_figure_agreement_primary_gate") is not False
        or manifest.get("key_count") != EXPECTED_KEY_COUNT
        or manifest.get("shard_count") != EXPECTED_SHARD_COUNT
        or manifest.get("status") != payload.get("status")
    ):
        raise ConditioningCampaignError("campaign manifest claims changed")
    _validate_identity(
        manifest["campaign_index_identity"],
        path=index_path,
        label="campaign index",
    )
    raw_sources = payload.get("campaign_source_identities")
    raw_shards = payload.get("shards")
    if not isinstance(raw_sources, Mapping) or not isinstance(raw_shards, list):
        raise ConditioningCampaignError("campaign rebuild inputs are missing")
    shard_roots = []
    for entry in raw_shards:
        if not isinstance(entry, Mapping) or not isinstance(entry.get("root"), str):
            raise ConditioningCampaignError("campaign shard entry is malformed")
        shard_roots.append(str(entry["root"]))
    rebuilt = build_conditioning_campaign_index(
        shard_roots,
        campaign_source_identities=raw_sources,  # type: ignore[arg-type]
    )
    if rebuilt != payload:
        raise ConditioningCampaignError("published campaign differs from live rebuild")


__all__ = [
    "AGGREGATION_ROOT",
    "CAMPAIGN_INDEX_SCHEMA",
    "CAMPAIGN_MANIFEST_SCHEMA",
    "CAMPAIGN_ROOT_PREFIX",
    "CAMPAIGN_ROOT_SUFFIX",
    "ConditioningCampaignError",
    "ValidatedConditioningShard",
    "build_conditioning_campaign_index",
    "campaign_index_from_validated_shards",
    "campaign_shard_root_name",
    "publish_conditioning_campaign",
    "resolve_explicit_shard_roots",
    "resolve_roots_parent",
    "validate_campaign_shards",
    "validate_conditioning_shard_root",
    "validate_published_conditioning_campaign",
]
