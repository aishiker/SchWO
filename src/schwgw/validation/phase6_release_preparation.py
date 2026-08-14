"""Strict Phase-6 V1 release preparation and evidence normalization.

This module composes heterogeneous, already terminal evidence into the one
input schema accepted by :mod:`schwgw.validation.phase6_release`.  It is a
metadata operation only: no solver, renderer, paper-figure comparison, or
threshold calibration is run here.

The release map deliberately cannot state a scientific result.  Native state,
coverage, uncertainty records, provenance, and blockers are extracted by
typed adapters.  Each native artifact is copied byte-for-byte into a fresh
immutable snapshot; the sole ``RESULT`` in a release envelope is a canonical
normalization projection which records both the origin and snapshot identity.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat

from schwgw.validation.phase6_domain import canonical_json_bytes
from schwgw.validation.phase6_execution_contract import (
    SHARD_CHECKPOINT_SCHEMA,
    SHARD_RESULT_SCHEMA,
)
from schwgw.validation.phase6_release import (
    CERTIFICATE_SCHEMA,
    CONVENTION_BUDGET_FIELDS,
    EVIDENCE_ENVELOPE_SCHEMA,
    GATE_OBSERVABLES,
    NUMERICAL_BUDGET_FIELDS,
    REQUIRED_LEDGER_SLICES,
    STATES,
    SUBMISSION_SCHEMA,
    Phase6ReleaseError,
    authoritative_contract_bindings,
    direct_file_identity,
    has_forbidden_global_claim,
    sha256_bytes,
    validate_submission,
)


RELEASE_MAP_SCHEMA = "schwgw_phase6_v1_release_preparation_map_v1"
NORMALIZED_RESULT_SCHEMA = "schwgw_phase6_v1_release_normalized_result_v1"
PREPARATION_MANIFEST_SCHEMA = "schwgw_phase6_v1_release_preparation_manifest_v1"
TYPED_PHYSICAL_RESULT_SCHEMA = "schwgw_phase6_v1_typed_physical_result_v1"
PRODUCTION_FINITE_RADIUS_RESULT_SCHEMA = (
    "schwgw_phase6_v1_production_finite_radius_result_v1"
)
V0_VERIFICATION_SCHEMA = "schwgw_phase6_v1_v0_verification_report_v1"
STAGE_A_EVIDENCE_SCHEMA = "schwgw_phase6_independent_mpmath_selected_anchor_evidence_v1"
BHPT_MST_BENCHMARK_SCHEMA = "schwo_bhpt_reggewheeler_mst_benchmark_v1"
BHPT_MST_COMPARISON_SCHEMA = "schwo_bhpt_reggewheeler_mst_comparison_v1"
BHPT_DIRECT_EVIDENCE_SCHEMA = "schwgw_phase6_bhpt_direct_selected_evidence_v1"
BHPT_DIRECT_RAW_SCHEMA = "schwgw_phase6_bhpt_direct_selected_raw_v1"
BHPT_DIRECT_COMPARISON_SCHEMA = "schwgw_phase6_bhpt_direct_conditioned_comparison_v1"
BHPT_DIRECT_COMPARISON_MANIFEST_SCHEMA = (
    "schwgw_phase6_bhpt_direct_conditioned_comparison_manifest_v1"
)
OBSERVABLE_BUNDLE_SCHEMA = "schwgw_phase6_populated_observable_evidence_v1"
CONDITIONING_CAMPAIGN_INDEX_SCHEMA = "schwgw_phase6_conditioning_campaign_index_v1"
CONDITIONING_CAMPAIGN_MANIFEST_SCHEMA = (
    "schwgw_phase6_conditioning_campaign_manifest_v1"
)
PRODUCTION_CAMPAIGN_RESULT_SCHEMA = "schwgw_phase6_production_finite_radius_campaign_v1"
PRODUCTION_CAMPAIGN_MANIFEST_SCHEMA = (
    "schwgw_phase6_production_finite_radius_campaign_manifest_v1"
)

ADAPTERS = (
    "BHPT_DIRECT_V1",
    "BHPT_DIRECT_COMPARISON_V1",
    "BHPT_MST_LEGACY_V1",
    "CONDITIONING_CAMPAIGN_V1",
    "CONDITIONING_SHARD_V1",
    "OBSERVABLE_FORMAL_ROOT_V1",
    "PRODUCTION_FINITE_RADIUS_V1",
    "PRODUCTION_FINITE_RADIUS_CAMPAIGN_V1",
    "STAGE_A_MPMATH_V1",
    "TYPED_PHYSICAL_RESULT_V1",
    "V0_IMPLEMENTATION_VERIFICATION_V1",
    "V1_AP_SELECTED_EVIDENCE_V1",
    "V1_FINAL_RADIAL_BASELINE_V2",
    "V1_PRODUCTION_STATE_EVIDENCE_V1",
    "V1_RADIAL_SELECTED_ACCEPTANCE_V1",
)

POLICY = {
    "acceptance_is_per_observable_and_domain": True,
    "full_paper_figure_rerun_performed": False,
    "global_green_permitted": False,
    "li_figure_agreement_primary_gate": False,
    "publisher_generated_science": False,
}

_ID = re.compile(r"[a-z0-9][a-z0-9_.-]{0,95}")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_FORBIDDEN_PRIMARY = re.compile(r"(?:\bli\b|paper[ _-]?fig|raster)", re.I)
_STATE_RANK = {"PASS": 0, "NOT_ASSESSED": 1, "PARTIAL": 2, "FAIL": 3}
_FLOAT64_UNASSESSED_SENTINEL = float.fromhex("0x1.fffffffffffffp+1023")
_STAGE_A_LIMITATION_REWRITES = {
    "no V1/full-domain/project/global GREEN claim": (
        "selected-anchor evidence does not establish V1 full-domain acceptance"
    )
}
_CONDITIONING_CAMPAIGN_INDEX_FIELDS = frozenset(
    {
        "budget_summaries",
        "campaign_code_hashes",
        "campaign_source_identities",
        "contract_only",
        "coverage",
        "execution_integrity",
        "failure_summary",
        "frozen_inputs",
        "generic_conditioning_source_hashes",
        "global_green_permitted",
        "implementation_source_sha_hashes",
        "kernel_unit_test_only",
        "li_figure_agreement_primary_gate",
        "observable_status_counts",
        "overall_state",
        "paper_agreement_gate",
        "production_finite_radius_states",
        "runtime_identity_groups",
        "schema",
        "science_executed",
        "scientific_evidence",
        "scope_qualification",
        "selection_summary",
        "shards",
        "solver_call_count",
        "status",
        "terminal_completion_counts",
        "transition_summary",
    }
)
_PRODUCTION_CAMPAIGN_RESULT_FIELDS = frozenset(
    {
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
)
_LEGACY_MST_HASHES = {
    "comparison.json": (
        "274786add2947174fd6be43224c5e28de4c3da1b14a6fd9f97638a3c55218281"
    ),
    "external_bhpt_mst.json": (
        "0a6359692b9321a60c3f0308a2119968af57c7a0541cd27b6e9636334853f08e"
    ),
}
_ADAPTER_REQUIRED_ARTIFACTS: dict[str, frozenset[str] | None] = {
    "STAGE_A_MPMATH_V1": frozenset(
        {"selected_anchor_evidence.json", "manifest.json", "checkpoint.json"}
    ),
    "CONDITIONING_SHARD_V1": frozenset(
        {
            "run_contract.json",
            "shard_result.json",
            "shard_checkpoint.json",
            "manifest.json",
        }
    ),
    "CONDITIONING_CAMPAIGN_V1": frozenset(
        {"conditioning_campaign_index.json", "manifest.json"}
    ),
    "BHPT_MST_LEGACY_V1": frozenset(_LEGACY_MST_HASHES),
    # The direct root has terminal-dependent logs.  Its own immutable manifest
    # supplies the exact inventory, so the map must enumerate every root file.
    "BHPT_DIRECT_V1": None,
    "BHPT_DIRECT_COMPARISON_V1": frozenset(
        {"comparison.json", "manifest.json", "report.json"}
    ),
    "OBSERVABLE_FORMAL_ROOT_V1": frozenset(
        {"observable_evidence.json", "manifest.json"}
    ),
    "TYPED_PHYSICAL_RESULT_V1": frozenset({"report.json"}),
    "PRODUCTION_FINITE_RADIUS_V1": frozenset({"report.json"}),
    "PRODUCTION_FINITE_RADIUS_CAMPAIGN_V1": frozenset(
        {"campaign_result.json", "manifest.json"}
    ),
    "V0_IMPLEMENTATION_VERIFICATION_V1": frozenset({"verification.json"}),
    "V1_AP_SELECTED_EVIDENCE_V1": frozenset(
        {"manifest.json", "report.json", "source_ledger.json"}
    ),
    "V1_FINAL_RADIAL_BASELINE_V2": frozenset(
        {"manifest.json", "report.json", "summary.json"}
    ),
    "V1_PRODUCTION_STATE_EVIDENCE_V1": frozenset(
        {"manifest.json", "report.json", "source_ledger.json"}
    ),
    "V1_RADIAL_SELECTED_ACCEPTANCE_V1": frozenset(
        {"manifest.json", "report.json", "summary.json"}
    ),
}


class Phase6PreparationError(Phase6ReleaseError):
    """Raised for unsafe input, ambiguous normalization, or publication drift."""


@dataclass(frozen=True)
class OriginArtifact:
    """Stable bytes plus their identity before the preparation snapshot exists."""

    relative_path: str
    raw: bytes
    payload: Mapping[str, object] | None
    origin_identity: Mapping[str, object]


@dataclass(frozen=True)
class DerivedEvidence:
    """Adapter output used to build one normalized release evidence projection."""

    evidence_id: str
    adapter: str
    role: str
    independence_class: str
    state: str
    blocker: Mapping[str, str] | None
    science_executed: bool
    implementation_hashes: tuple[str, ...]
    expected_items: int
    assessed_item_ids: tuple[str, ...]
    assessed_items: int
    coverage_family: str
    numerical_budget: Mapping[str, Mapping[str, object]]
    convention_budget: Mapping[str, Mapping[str, object]]
    native_summary: Mapping[str, object]
    native_domain: Mapping[str, object] | None
    limitations: tuple[str, ...]
    method: str


@dataclass(frozen=True)
class PreparedPlan:
    """Fully validated no-write composition plan."""

    release_map: Mapping[str, object]
    sources: Mapping[str, tuple[DerivedEvidence, tuple[OriginArtifact, ...]]]
    generated: Mapping[str, DerivedEvidence]


def _exact(value: object, fields: set[str], label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != fields:
        raise Phase6PreparationError(f"{label} schema changed")
    return value


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise Phase6PreparationError(f"{label} is not a canonical identifier")
    return value


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Phase6PreparationError(f"{label} must be non-empty text")
    return value


def _sha(value: object, label: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise Phase6PreparationError(f"{label} is not SHA-256")
    return value


def _json_value(value: object, label: str) -> None:
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int) and not isinstance(value, bool):
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _json_value(item, f"{label}[{index}]")
        return
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) or not key for key in value):
            raise Phase6PreparationError(f"{label} has an invalid key")
        for key, item in value.items():
            _json_value(item, f"{label}.{key}")
        return
    raise Phase6PreparationError(f"{label} contains float or unsupported data")


def _finite_json(value: object, label: str) -> None:
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int) and not isinstance(value, bool):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise Phase6PreparationError(f"{label} contains non-finite data")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _finite_json(item, f"{label}[{index}]")
        return
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) or not key for key in value):
            raise Phase6PreparationError(f"{label} has an invalid key")
        for key, item in value.items():
            _finite_json(item, f"{label}.{key}")
        return
    raise Phase6PreparationError(f"{label} contains unsupported data")


def _decimal_text(value: object, *, fallback: str | None = None) -> str | None:
    if value is None:
        return fallback
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise Phase6PreparationError("uncertainty estimate is not numeric")
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise Phase6PreparationError("uncertainty estimate is not decimal") from exc
    if not number.is_finite() or number < 0:
        raise Phase6PreparationError("uncertainty estimate must be finite/nonnegative")
    return format(number, "f")


def _worst(states: Sequence[str]) -> str:
    if not states:
        return "NOT_ASSESSED"
    if any(state not in STATES for state in states):
        raise Phase6PreparationError("native state vocabulary changed")
    return max(states, key=_STATE_RANK.__getitem__)


def _item_id(value: object) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _required_budget(
    fields: Sequence[str],
    *,
    state: str = "NOT_ASSESSED",
    estimate: object = None,
    units: str = "dimensionless",
    reason: str = "native source did not quantify this component",
) -> dict[str, dict[str, object]]:
    if state not in STATES:
        raise Phase6PreparationError("budget state changed")
    canonical_estimate = _decimal_text(
        estimate,
        fallback="1" if state in {"PASS", "FAIL"} else None,
    )
    return {
        field: {
            "state": state,
            "estimate": canonical_estimate,
            "units": units,
            "reason": reason,
        }
        for field in fields
    }


def _budget_component(
    *, state: str, estimate: object, units: object, reason: object
) -> dict[str, object]:
    if state not in STATES:
        raise Phase6PreparationError("budget component state changed")
    return {
        "state": state,
        "estimate": _decimal_text(
            estimate,
            fallback="1" if state in {"PASS", "FAIL"} else None,
        ),
        "units": _text(units, "budget units") if units is not None else "dimensionless",
        "reason": _text(reason, "budget reason"),
    }


def _validate_map(value: object) -> Mapping[str, object]:
    item = _exact(
        value,
        {"schema", "preparation_id", "release_id", "sources", "certificates", "policy"},
        "release preparation map",
    )
    if item["schema"] != RELEASE_MAP_SCHEMA or item["policy"] != POLICY:
        raise Phase6PreparationError("release-map schema/policy changed")
    _identifier(item["preparation_id"], "preparation_id")
    _identifier(item["release_id"], "release_id")
    sources = item["sources"]
    if not isinstance(sources, list):
        raise Phase6PreparationError("release-map sources must be a list")
    source_ids: list[str] = []
    selectors: set[tuple[str, str, bytes]] = set()
    for index, raw_source in enumerate(sources):
        source = _exact(
            raw_source,
            {"evidence_id", "adapter", "origin_root", "expected_artifacts", "selector"},
            f"source[{index}]",
        )
        evidence_id = _identifier(source["evidence_id"], f"source[{index}] evidence_id")
        source_ids.append(evidence_id)
        adapter = source["adapter"]
        if adapter not in ADAPTERS:
            raise Phase6PreparationError(f"source {evidence_id} adapter changed")
        origin = Path(_text(source["origin_root"], "origin_root"))
        if not origin.is_absolute():
            raise Phase6PreparationError("origin_root must be absolute")
        selector = source["selector"]
        if adapter == "OBSERVABLE_FORMAL_ROOT_V1":
            selected = _exact(
                selector, {"source_certificate_id"}, "observable selector"
            )
            _text(selected["source_certificate_id"], "source certificate id")
        elif adapter in {
            "CONDITIONING_CAMPAIGN_V1",
            "PRODUCTION_FINITE_RADIUS_CAMPAIGN_V1",
            "V1_FINAL_RADIAL_BASELINE_V2",
            "V1_PRODUCTION_STATE_EVIDENCE_V1",
        }:
            selected = _exact(selector, {"projection"}, "campaign selector")
            if selected["projection"] not in {
                "generic_conditioning_backend",
                "radial_s_matrix_flux",
            }:
                raise Phase6PreparationError("campaign projection changed")
        elif selector != {}:
            raise Phase6PreparationError(
                f"source {evidence_id} selector is not allowed"
            )
        selector_key = (str(adapter), str(origin), canonical_json_bytes(selector))
        if selector_key in selectors:
            raise Phase6PreparationError("duplicate source root/adapter/selector")
        selectors.add(selector_key)
        artifacts = source["expected_artifacts"]
        if not isinstance(artifacts, list) or not artifacts:
            raise Phase6PreparationError(f"source {evidence_id} artifact list is empty")
        names: list[str] = []
        digests: list[str] = []
        for artifact_index, raw_artifact in enumerate(artifacts):
            artifact = _exact(
                raw_artifact,
                {"relative_path", "sha256"},
                f"source {evidence_id} artifact[{artifact_index}]",
            )
            relative = _text(artifact["relative_path"], "relative artifact path")
            pure = PurePosixPath(relative)
            if pure.is_absolute() or len(pure.parts) != 1 or pure.name != relative:
                raise Phase6PreparationError(
                    "source artifacts must be direct root files"
                )
            names.append(relative)
            digests.append(_sha(artifact["sha256"], "expected artifact sha256"))
        if names != sorted(set(names)) or len(set(digests)) != len(digests):
            raise Phase6PreparationError("source artifacts are unordered/duplicate")
        required = _ADAPTER_REQUIRED_ARTIFACTS[str(adapter)]
        if required is not None and set(names) != set(required):
            raise Phase6PreparationError(
                f"source {evidence_id} does not enumerate the exact adapter artifacts"
            )
        if (
            adapter == "BHPT_MST_LEGACY_V1"
            and {record["relative_path"]: record["sha256"] for record in artifacts}
            != _LEGACY_MST_HASHES
        ):
            raise Phase6PreparationError(
                "legacy MST bytes are not the frozen v4 evidence"
            )
    if source_ids != sorted(set(source_ids)):
        raise Phase6PreparationError("sources are not in unique evidence_id order")

    certificates = item["certificates"]
    if not isinstance(certificates, list) or not certificates:
        raise Phase6PreparationError("certificate plans are empty")
    certificate_ids: list[str] = []
    scopes: list[tuple[str, str, str]] = []
    used_evidence: set[str] = set()
    for index, raw_certificate in enumerate(certificates):
        certificate = _exact(
            raw_certificate,
            {
                "certificate_id",
                "gate",
                "observable",
                "parameter_domain",
                "evidence_ids",
                "primary_acceptance_gate",
            },
            f"certificate plan[{index}]",
        )
        certificate_id = _identifier(
            certificate["certificate_id"], f"certificate[{index}] id"
        )
        certificate_ids.append(certificate_id)
        gate = _text(certificate["gate"], "certificate gate")
        observable = _text(certificate["observable"], "certificate observable")
        if gate not in GATE_OBSERVABLES or observable not in GATE_OBSERVABLES[gate]:
            raise Phase6PreparationError("certificate gate/observable changed")
        domain = _exact(
            certificate["parameter_domain"],
            {
                "domain_id",
                "description",
                "parameters",
                "selection_policy",
                "expected_items",
            },
            "certificate parameter domain",
        )
        domain_id = _identifier(domain["domain_id"], "certificate domain_id")
        _text(domain["description"], "certificate domain description")
        _text(domain["selection_policy"], "certificate selection policy")
        parameters = domain["parameters"]
        if not isinstance(parameters, Mapping) or not parameters:
            raise Phase6PreparationError("certificate parameters must be explicit")
        _json_value(parameters, "certificate parameters")
        expected_items = domain["expected_items"]
        if (
            isinstance(expected_items, bool)
            or not isinstance(expected_items, int)
            or expected_items < 1
        ):
            raise Phase6PreparationError("certificate expected_items is invalid")
        scopes.append((gate, observable, domain_id))
        evidence_ids = certificate["evidence_ids"]
        if (
            not isinstance(evidence_ids, list)
            or evidence_ids != sorted(set(evidence_ids))
            or any(evidence_id not in source_ids for evidence_id in evidence_ids)
        ):
            raise Phase6PreparationError("certificate evidence references changed")
        used_evidence.update(evidence_ids)
        primary = _text(
            certificate["primary_acceptance_gate"], "primary acceptance gate"
        )
        if _FORBIDDEN_PRIMARY.search(primary):
            raise Phase6PreparationError("Li/paper/raster cannot be a primary gate")
        if gate == "V6" and evidence_ids:
            raise Phase6PreparationError("V6 policy evidence is preparation-derived")
    if certificate_ids != sorted(set(certificate_ids)) or len(set(scopes)) != len(
        scopes
    ):
        raise Phase6PreparationError("certificate plans are unordered/duplicate")
    if set(source_ids) != used_evidence:
        raise Phase6PreparationError(
            "source evidence must be referenced exactly by scope"
        )
    missing = REQUIRED_LEDGER_SLICES - {
        (gate, observable) for gate, observable, _ in scopes
    }
    if missing:
        raise Phase6PreparationError(
            f"release map omits required slices: {sorted(missing)}"
        )
    return item


def _stable_origin_file(
    root: Path,
    relative_path: str,
    expected_sha256: str,
    *,
    legacy_mutable: bool,
) -> OriginArtifact:
    absolute = root / relative_path
    if any(component.is_symlink() for component in (absolute, *absolute.parents)):
        raise Phase6PreparationError("origin artifact path contains a symlink")
    try:
        resolved = absolute.resolve(strict=True)
        before = absolute.lstat()
    except OSError as exc:
        raise Phase6PreparationError(f"origin artifact is missing: {absolute}") from exc
    if (
        resolved != absolute
        or absolute.parent != root
        or not stat.S_ISREG(before.st_mode)
    ):
        raise Phase6PreparationError("origin artifact is not a direct regular file")
    if before.st_nlink != 1:
        raise Phase6PreparationError("origin artifact must be nlink1")
    if not legacy_mutable and stat.S_IMODE(before.st_mode) != 0o444:
        raise Phase6PreparationError("modern origin artifact must be 0444")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(absolute, flags)
    try:
        opened_before = os.fstat(descriptor)
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        opened_after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    raw = b"".join(chunks)
    after = absolute.lstat()
    signature = lambda info: (  # noqa: E731 - compact immutable stat projection
        info.st_dev,
        info.st_ino,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
        info.st_mode,
        info.st_nlink,
    )
    if (
        signature(before) != signature(opened_before)
        or signature(before) != signature(opened_after)
        or signature(before) != signature(after)
    ):
        raise Phase6PreparationError("origin artifact changed during stable read")
    digest = sha256_bytes(raw)
    if digest != expected_sha256:
        raise Phase6PreparationError(f"origin artifact hash changed: {relative_path}")
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise Phase6PreparationError("native adapter artifact is not JSON") from exc
    if not isinstance(payload, Mapping):
        raise Phase6PreparationError("native adapter artifact is not a JSON object")
    _finite_json(payload, f"native {relative_path}")
    return OriginArtifact(
        relative_path=relative_path,
        raw=raw,
        payload=payload,
        origin_identity={
            "path": str(absolute),
            "sha256": digest,
            "size": before.st_size,
            "mode": stat.S_IMODE(before.st_mode),
            "nlink": before.st_nlink,
        },
    )


def _load_origin(source: Mapping[str, object]) -> tuple[OriginArtifact, ...]:
    adapter = str(source["adapter"])
    root = Path(str(source["origin_root"])).absolute()
    legacy = adapter == "BHPT_MST_LEGACY_V1"
    if any(component.is_symlink() for component in (root, *root.parents)):
        raise Phase6PreparationError("origin root contains a symlink")
    try:
        resolved = root.resolve(strict=True)
        root_info = root.lstat()
    except OSError as exc:
        raise Phase6PreparationError(f"origin root is unavailable: {root}") from exc
    if resolved != root or not stat.S_ISDIR(root_info.st_mode):
        raise Phase6PreparationError("origin root must be a direct directory")
    if not legacy and stat.S_IMODE(root_info.st_mode) != 0o555:
        raise Phase6PreparationError("modern origin root must be immutable 0555")
    artifacts = tuple(
        _stable_origin_file(
            root,
            str(record["relative_path"]),
            str(record["sha256"]),
            legacy_mutable=legacy,
        )
        for record in source["expected_artifacts"]
    )
    if adapter == "BHPT_DIRECT_COMPARISON_V1" and {
        child.name for child in root.iterdir()
    } != {"comparison.json", "manifest.json", "report.json"}:
        raise Phase6PreparationError(
            "BHPT direct comparison root must contain its exact three-file inventory"
        )
    if adapter == "BHPT_DIRECT_V1":
        manifest = next(
            (
                artifact.payload
                for artifact in artifacts
                if artifact.relative_path == "manifest.json"
            ),
            None,
        )
        if not isinstance(manifest, Mapping) or not isinstance(
            manifest.get("files"), Mapping
        ):
            raise Phase6PreparationError("BHPT direct manifest inventory is missing")
        expected_names = {*manifest["files"], "manifest.json"}
        if {artifact.relative_path for artifact in artifacts} != expected_names:
            raise Phase6PreparationError(
                "BHPT direct map does not snapshot its exact manifest inventory"
            )
    return artifacts


def _artifact_payload(
    artifacts: Sequence[OriginArtifact], name: str
) -> Mapping[str, object]:
    matches = [
        artifact.payload for artifact in artifacts if artifact.relative_path == name
    ]
    if len(matches) != 1 or not isinstance(matches[0], Mapping):
        raise Phase6PreparationError(f"adapter artifact is missing: {name}")
    return matches[0]


def _native_identity_matches(value: object, artifact: OriginArtifact) -> bool:
    """Match native identities with an optional hardened inode field.

    Release identities intentionally omit inode because a byte-for-byte
    snapshot necessarily has a different inode.  Some native publishers keep
    the origin inode in their internal linkage records, however.  Accept that
    additional field only when it still matches the live, immutable origin;
    no other native identity extension is permitted.
    """

    if not isinstance(value, Mapping):
        return False
    origin = dict(artifact.origin_identity)
    fields = set(origin)
    native_fields = set(value)
    if native_fields != fields and native_fields != fields | {"inode"}:
        return False
    if any(value.get(name) != expected for name, expected in origin.items()):
        return False
    if "inode" not in value:
        return True
    inode = value["inode"]
    if isinstance(inode, bool) or not isinstance(inode, int) or inode < 0:
        return False
    try:
        return Path(str(origin["path"])).lstat().st_ino == inode
    except OSError:
        return False


def _stage_a_terminal_projection(
    modes: object,
) -> tuple[str, dict[str, int], tuple[str, ...]]:
    """Derive aggregate state without allowing a top-level YELLOW to hide FAIL."""

    if not isinstance(modes, list) or len(modes) != 8:
        raise Phase6PreparationError("Stage-A mode inventory changed")
    native_states: list[str] = []
    item_ids: list[str] = []
    for mode in modes:
        if not isinstance(mode, Mapping) or not isinstance(mode.get("mode"), Mapping):
            raise Phase6PreparationError("Stage-A mode record changed")
        status = mode.get("status")
        if status == "FAIL_CLOSED_NUMERICAL_INSTABILITY":
            native_states.append("FAIL")
        elif status == "STABLE_SELECTED_ANCHOR_INCOMPLETE_LADDERS":
            native_states.append("PARTIAL")
        else:
            raise Phase6PreparationError("Stage-A terminal scientific status changed")
        item_ids.append(_item_id(mode["mode"]))
    counts = Counter(native_states)
    return (
        "FAIL" if counts["FAIL"] else "PARTIAL",
        {
            "NOT_ASSESSED": 0,
            "PARTIAL": counts["PARTIAL"],
            "PASS": 0,
            "FAIL": counts["FAIL"],
        },
        tuple(sorted(item_ids)),
    )


def _stage_a_release_limitations(value: object) -> tuple[str, ...]:
    """Project native Stage-A caveats into domain-qualified release prose.

    The one rewrite is exact and auditable.  It removes status language that
    the release schema deliberately forbids without weakening the native
    caveat.  Any other project-wide status wording fails closed instead of
    being silently laundered.
    """

    if not isinstance(value, list) or not value:
        raise Phase6PreparationError("Stage-A limitations changed")
    result: list[str] = []
    for index, item in enumerate(value):
        text = _text(item, f"Stage-A limitation[{index}]")
        projected = _STAGE_A_LIMITATION_REWRITES.get(text, text)
        if has_forbidden_global_claim(projected):
            raise Phase6PreparationError(
                "Stage-A limitation contains release-forbidden global-status wording"
            )
        result.append(projected)
    return tuple(result)


def _stage_a(evidence_id: str, artifacts: Sequence[OriginArtifact]) -> DerivedEvidence:
    try:
        from schwgw.validation.phase6_mpmath_radial import (  # noqa: PLC0415
            validate_stage_a_evidence,
        )
    except ImportError as exc:
        raise Phase6PreparationError(
            "Stage-A adapter requires its frozen mpmath runtime overlay"
        ) from exc

    evidence = _artifact_payload(artifacts, "selected_anchor_evidence.json")
    if evidence.get("schema_version") != STAGE_A_EVIDENCE_SCHEMA:
        raise Phase6PreparationError("Stage-A source schema changed")
    validate_stage_a_evidence(evidence)
    manifest = _artifact_payload(artifacts, "manifest.json")
    checkpoint = _artifact_payload(artifacts, "checkpoint.json")
    evidence_artifact = next(
        artifact
        for artifact in artifacts
        if artifact.relative_path == "selected_anchor_evidence.json"
    )
    if (
        manifest.get("schema_version")
        != "schwgw_phase6_mpmath_selected_anchor_manifest_v1"
        or checkpoint.get("schema_version")
        != "schwgw_phase6_mpmath_selected_anchor_checkpoint_v1"
        or not _native_identity_matches(manifest.get("evidence"), evidence_artifact)
        or not _native_identity_matches(checkpoint.get("evidence"), evidence_artifact)
    ):
        raise Phase6PreparationError("Stage-A manifest/checkpoint linkage changed")
    state, item_state_counts, item_ids = _stage_a_terminal_projection(evidence["modes"])
    numerical = _required_budget(NUMERICAL_BUDGET_FIELDS)
    measured = {"r_in", "r_out", "jost_order", "ode_tolerance", "arithmetic_precision"}
    for name in measured:
        numerical[name] = _budget_component(
            state=state,
            estimate="1" if state == "FAIL" else None,
            units="dimensionless",
            reason=(
                "Stage-A contains fail-closed numerical-instability terminals"
                if state == "FAIL"
                else "bounded Stage-A ladder is measured but cannot close production acceptance"
            ),
        )
    backend = evidence["backend_identity"]
    if not isinstance(backend, Mapping):
        raise Phase6PreparationError("Stage-A backend identity changed")
    implementation = _sha(
        backend.get("implementation_source_sha256"), "Stage-A implementation hash"
    )
    return DerivedEvidence(
        evidence_id=evidence_id,
        adapter="STAGE_A_MPMATH_V1",
        role="INDEPENDENT_SCIENCE",
        independence_class="ALGORITHMICALLY_INDEPENDENT",
        state=state,
        blocker=None,
        science_executed=True,
        implementation_hashes=(implementation,),
        expected_items=8,
        assessed_item_ids=tuple(sorted(item_ids)),
        assessed_items=8,
        coverage_family="stage_a_mpmath_v1",
        numerical_budget=numerical,
        convention_budget=_required_budget(CONVENTION_BUDGET_FIELDS),
        native_summary={
            "native_overall_status": evidence["overall_status"],
            "native_item_state_counts": item_state_counts,
            "covered_key_count": 8,
            "production_key_count": 16048,
            "production_missing_key_count": 16040,
        },
        native_domain=None,
        limitations=_stage_a_release_limitations(evidence["limitations"]),
        method="independent arbitrary-precision Stage-A; native terminal states preserved",
    )


def _conditioning_status_projection(
    native_state: str, aggregate_attempt_status: str
) -> tuple[str, str, bool]:
    """Project conditioning status without allowing execution FAIL to be hidden."""

    if native_state not in STATES or aggregate_attempt_status not in STATES:
        raise Phase6PreparationError("conditioning status vocabulary changed")
    if aggregate_attempt_status == "FAIL":
        return (
            "FAIL",
            "FAILURE_DIAGNOSTIC"
            if native_state == "NOT_ASSESSED"
            else "PRIMARY_SCIENCE",
            native_state != "NOT_ASSESSED",
        )
    if native_state == "NOT_ASSESSED":
        return "NOT_ASSESSED", "BLOCKER", False
    return native_state, "PRIMARY_SCIENCE", True


def _conditioning(
    evidence_id: str,
    artifacts: Sequence[OriginArtifact],
    root: Path,
) -> DerivedEvidence:
    contract = _artifact_payload(artifacts, "run_contract.json")
    result = _artifact_payload(artifacts, "shard_result.json")
    checkpoint = _artifact_payload(artifacts, "shard_checkpoint.json")
    manifest = _artifact_payload(artifacts, "manifest.json")
    # Reuse the producer's strict reload validator.  It only reopens immutable
    # artifacts and cannot execute a solver.
    try:
        from scripts.phase6_run_conditioning_scan_shard import (  # noqa: PLC0415
            _validate_completed_root,
        )

        _validate_completed_root(root, contract)
    except Exception as exc:
        raise Phase6PreparationError("conditioning shard strict reload failed") from exc
    if (
        result.get("schema") != SHARD_RESULT_SCHEMA
        or checkpoint.get("schema") != SHARD_CHECKPOINT_SCHEMA
        or manifest.get("schema") != "schwgw_phase6_conditioning_shard_manifest_v1"
    ):
        raise Phase6PreparationError("conditioning aggregate schema changed")
    state = result.get("acceptance_state")
    if state not in STATES:
        raise Phase6PreparationError("conditioning acceptance state changed")
    keys = contract.get("shard_keys")
    if not isinstance(keys, list) or not keys:
        raise Phase6PreparationError("conditioning shard key inventory changed")
    summary = result.get("summary")
    if not isinstance(summary, Mapping) or summary.get("key_count") != len(keys):
        raise Phase6PreparationError("conditioning coverage summary changed")
    numerical_native = checkpoint.get("numerical_budget")
    convention_native = checkpoint.get("convention_budget")
    if not isinstance(numerical_native, Mapping) or not isinstance(
        convention_native, Mapping
    ):
        raise Phase6PreparationError("conditioning budgets are missing")
    numerical_status = numerical_native.get("status")
    convention_status = convention_native.get("status")
    if numerical_status not in STATES or convention_status not in STATES:
        raise Phase6PreparationError("conditioning budget state changed")
    numerical_components = numerical_native.get("components")
    convention_components = convention_native.get("components")
    if not isinstance(numerical_components, Mapping) or not isinstance(
        convention_components, Mapping
    ):
        raise Phase6PreparationError("conditioning budget components changed")
    numerical = {
        name: _budget_component(
            state=str(numerical_status),
            estimate=numerical_components.get(name),
            units="dimensionless",
            reason="conditioning shard aggregate native numerical budget",
        )
        for name in NUMERICAL_BUDGET_FIELDS
    }
    convention = _required_budget(CONVENTION_BUDGET_FIELDS)
    for name in convention_components:
        if name not in convention:
            raise Phase6PreparationError("conditioning convention component changed")
        convention[name] = _budget_component(
            state=str(convention_status),
            estimate=convention_components[name],
            units="dimensionless",
            reason="conditioning shard aggregate native convention budget",
        )
    hashes: set[str] = set()
    for label in ("source_hashes", "code_hashes", "backend_hashes"):
        values = checkpoint.get(label)
        if not isinstance(values, Mapping):
            raise Phase6PreparationError("conditioning implementation hashes changed")
        hashes.update(_sha(value, f"conditioning {label}") for value in values.values())
    shard = contract.get("shard")
    if not isinstance(shard, Mapping) or not isinstance(shard.get("shard_id"), str):
        raise Phase6PreparationError("conditioning shard identity changed")
    attempts = checkpoint.get("attempts")
    if (
        not isinstance(attempts, list)
        or not attempts
        or not isinstance(attempts[-1], Mapping)
        or attempts[-1].get("status") not in STATES
    ):
        raise Phase6PreparationError("conditioning aggregate attempts changed")
    release_state, role, science_executed = _conditioning_status_projection(
        str(state), str(attempts[-1]["status"])
    )
    execution_failed = attempts[-1]["status"] == "FAIL"
    independence = "SAME_IMPLEMENTATION" if role == "PRIMARY_SCIENCE" else "NONE"
    blocker: Mapping[str, str] | None = None
    implementation_hashes = tuple(sorted(hashes))
    assessed_item_ids = tuple(sorted(_item_id(key) for key in keys))
    assessed_items = len(keys)
    if state == "NOT_ASSESSED":
        implementation_hashes = ()
        assessed_item_ids = ()
        assessed_items = 0
        if not execution_failed:
            blocker = {
                "code": "CONDITIONING_SHARD_NOT_ASSESSED",
                "reason": "terminal conditioning shard contains no assessed scientific result",
            }
    return DerivedEvidence(
        evidence_id=evidence_id,
        adapter="CONDITIONING_SHARD_V1",
        role=role,
        independence_class=independence,
        state=release_state,
        blocker=blocker,
        science_executed=science_executed,
        implementation_hashes=implementation_hashes,
        expected_items=17818,
        assessed_item_ids=assessed_item_ids,
        assessed_items=assessed_items,
        coverage_family="conditioning_production_v1",
        numerical_budget=numerical,
        convention_budget=convention,
        native_summary={
            "acceptance_state": state,
            "shard_id": shard["shard_id"],
            "key_count": len(keys),
            "observable_statuses": result.get("observable_statuses"),
            "summary": summary,
            "aggregate_attempt_status": attempts[-1]["status"],
            "consumed_key_checkpoint_count": len(
                checkpoint.get("key_checkpoint_identities", [])
            ),
        },
        native_domain=None,
        limitations=(
            "conditioning shard state is retained per exact 17,818-key policy-union domain",
        ),
        method="generic conditioning production shard with strict terminal reload",
    )


def _legacy_mst(
    evidence_id: str, artifacts: Sequence[OriginArtifact]
) -> DerivedEvidence:
    try:
        from schwgw.scattering.mst_benchmark import (  # noqa: PLC0415
            validate_bhpt_mst_benchmark,
        )
    except ImportError as exc:
        raise Phase6PreparationError(
            "legacy MST adapter requires its frozen mpmath runtime overlay"
        ) from exc

    comparison = _artifact_payload(artifacts, "comparison.json")
    external = _artifact_payload(artifacts, "external_bhpt_mst.json")
    if (
        comparison.get("schema_version") != BHPT_MST_COMPARISON_SCHEMA
        or external.get("schema_version") != BHPT_MST_BENCHMARK_SCHEMA
    ):
        raise Phase6PreparationError("legacy MST source schema changed")
    normalized = validate_bhpt_mst_benchmark(external)
    records = comparison.get("records")
    if not isinstance(records, list) or len(records) != 84 or len(normalized) != 84:
        raise Phase6PreparationError("legacy MST record coverage changed")
    maxima = {
        name: max(float(record[name]) for record in records)
        for name in (
            "odd_abs_error",
            "even_abs_error",
            "odd_wrapped_phase_error",
            "even_wrapped_phase_error",
        )
    }
    if (
        comparison.get("record_count") != 84
        or comparison.get("strict_no_fitted_phase_or_normalization") is not True
        or comparison.get("strict_paper_reproduction_claim") is not False
        or comparison.get("external_even_is_independently_solved") is not False
        or comparison.get("external_json_sha256")
        != _LEGACY_MST_HASHES["external_bhpt_mst.json"]
        or any(
            not math.isclose(
                float(comparison[f"max_{name}"]), value, rel_tol=0, abs_tol=0
            )
            for name, value in maxima.items()
        )
    ):
        raise Phase6PreparationError("legacy MST comparison derivation changed")
    state = "FAIL" if comparison.get("status") == "FAIL" else "PARTIAL"
    if comparison.get("status") not in {"PASS", "FAIL"}:
        raise Phase6PreparationError("legacy MST native status changed")
    numerical = _required_budget(NUMERICAL_BUDGET_FIELDS)
    numerical["backend_difference"] = _budget_component(
        state="FAIL" if state == "FAIL" else "PARTIAL",
        estimate=maxima["odd_abs_error"],
        units="dimensionless",
        reason="84-mode external odd-sector MST complex difference",
    )
    convention = _required_budget(CONVENTION_BUDGET_FIELDS)
    convention["phase_origin"] = _budget_component(
        state="FAIL" if state == "FAIL" else "PARTIAL",
        estimate=maxima["odd_wrapped_phase_error"],
        units="rad",
        reason="absolute no-fit BHPT/local odd-sector phase convention comparison",
    )
    source_hash = _sha(
        external.get("regge_wheeler_radial_sha256"), "BHPT MST source hash"
    )
    return DerivedEvidence(
        evidence_id=evidence_id,
        adapter="BHPT_MST_LEGACY_V1",
        role="INDEPENDENT_SCIENCE",
        independence_class="EXTERNAL_SOURCE",
        state=state,
        blocker=None,
        science_executed=True,
        implementation_hashes=(source_hash,),
        expected_items=84,
        assessed_item_ids=tuple(
            sorted(
                _item_id({"kM": record["kM"], "ell": record["ell"]})
                for record in records
            )
        ),
        assessed_items=84,
        coverage_family="bhpt_mst_odd_v4",
        numerical_budget=numerical,
        convention_budget=convention,
        native_summary={
            "native_status": comparison["status"],
            "record_count": 84,
            "max_odd_abs_error": _decimal_text(maxima["odd_abs_error"]),
            "max_odd_wrapped_phase_error": _decimal_text(
                maxima["odd_wrapped_phase_error"]
            ),
            "odd_sector_independent": True,
            "external_even_is_independently_solved": False,
        },
        native_domain=None,
        limitations=(
            "odd-sector external MST is independent; even sector is exact parity-derived",
            "native PASS is implementation/calibration PASS and is capped at release PARTIAL",
        ),
        method="legacy Phase-5 BHPT MST v4 exact-byte snapshot; odd sector only independent",
    )


def _bhpt_direct(
    evidence_id: str,
    artifacts: Sequence[OriginArtifact],
    root: Path,
) -> DerivedEvidence:
    try:
        from schwgw.validation.phase6_bhpt_direct import (  # noqa: PLC0415
            _validate_frozen_root,
            validate_external_payload,
        )

        _validate_frozen_root(root)
    except Exception as exc:
        raise Phase6PreparationError(
            "BHPT direct immutable root reload failed"
        ) from exc
    evidence = _artifact_payload(artifacts, "evidence.json")
    if evidence.get("schema_version") != BHPT_DIRECT_EVIDENCE_SCHEMA:
        raise Phase6PreparationError("BHPT direct evidence schema changed")
    raw_matches = [
        artifact
        for artifact in artifacts
        if artifact.relative_path == "external_bhpt_direct.json"
    ]
    terminal_status = evidence.get("status")
    if terminal_status == "PASS":
        if len(raw_matches) != 1:
            raise Phase6PreparationError("BHPT direct PASS lacks one raw payload")
        raw = raw_matches[0].payload
        if (
            not isinstance(raw, Mapping)
            or raw.get("schema_version") != BHPT_DIRECT_RAW_SCHEMA
        ):
            raise Phase6PreparationError("BHPT direct raw schema changed")
        validated = validate_external_payload(
            raw, expected_request_sha256=str(raw.get("request_sha256"))
        )
        if (
            validated.get("status") != "PASS"
            or validated.get("scientific_acceptance_status") != "NOT_ASSESSED"
            or evidence.get("record_count") != 30
        ):
            raise Phase6PreparationError("BHPT direct source/method validation changed")
        records = raw["records"]
        item_ids = tuple(
            sorted(
                _item_id(
                    {
                        "kM": record["kM"],
                        "sector": record["sector"],
                        "ell": record["ell"],
                    }
                )
                for record in records
            )
        )
        source_hashes = raw["toolkit"]["source_hashes"]
        implementation_hashes = tuple(
            sorted(
                _sha(value, "BHPT direct source hash")
                for value in source_hashes.values()
            )
        )
        numerical = _required_budget(NUMERICAL_BUDGET_FIELDS)
        numerical["r_out"] = _budget_component(
            state="PARTIAL",
            estimate=max(
                Decimal(
                    record["numerical_uncertainty_budget"][
                        "matching_radius_phase_spread_abs"
                    ]
                )
                for record in records
            ),
            units="rad",
            reason="external three-radius matching spread; no acceptance threshold frozen",
        )
        numerical["arithmetic_precision"] = _budget_component(
            state="PARTIAL",
            estimate="800",
            units="decimal_digits",
            reason="external working precision is recorded without a precision ladder",
        )
        convention = _required_budget(CONVENTION_BUDGET_FIELDS)
        convention["phase_origin"] = _budget_component(
            state="PARTIAL",
            estimate="0",
            units="rad",
            reason="BHPT tortoise origin frozen; cross-implementation convention remains open",
        )
        return DerivedEvidence(
            evidence_id=evidence_id,
            adapter="BHPT_DIRECT_V1",
            role="INDEPENDENT_SCIENCE",
            independence_class="EXTERNAL_SOURCE",
            state="PARTIAL",
            blocker=None,
            science_executed=True,
            implementation_hashes=implementation_hashes,
            expected_items=30,
            assessed_item_ids=item_ids,
            assessed_items=30,
            coverage_family="bhpt_direct_v1",
            numerical_budget=numerical,
            convention_budget=convention,
            native_summary={
                "native_source_method_status": "PASS",
                "native_scientific_acceptance_status": "NOT_ASSESSED",
                "record_count": 30,
                "odd_record_count": 15,
                "even_record_count": 15,
                "even_is_independent_radial_solution": True,
            },
            native_domain=None,
            limitations=(
                "external direct integration is calibration evidence, not production-domain acceptance",
                "native schema/algebra PASS is capped at release PARTIAL",
            ),
            method="external BHPT direct RW/Zerilli NumericalIntegration calibration",
        )
    blocker_code = evidence.get("blocker")
    reason = evidence.get("reason")
    science_executed = evidence.get("science_executed") is True
    if terminal_status == "FAIL" and science_executed:
        if not isinstance(blocker_code, str) or not isinstance(reason, str):
            raise Phase6PreparationError("BHPT direct FAIL diagnostic changed")
        return DerivedEvidence(
            evidence_id=evidence_id,
            adapter="BHPT_DIRECT_V1",
            role="FAILURE_DIAGNOSTIC",
            independence_class="NONE",
            state="FAIL",
            blocker=None,
            science_executed=False,
            implementation_hashes=(),
            expected_items=30,
            assessed_item_ids=(),
            assessed_items=0,
            coverage_family="bhpt_direct_v1",
            numerical_budget=_required_budget(
                NUMERICAL_BUDGET_FIELDS, state="FAIL", reason=reason
            ),
            convention_budget=_required_budget(CONVENTION_BUDGET_FIELDS),
            native_summary={
                "native_status": terminal_status,
                "native_blocker": blocker_code,
            },
            native_domain=None,
            limitations=(reason,),
            method="external BHPT direct execution failure diagnostic",
        )
    if (
        terminal_status != "NOT_ASSESSED"
        or science_executed
        or not isinstance(blocker_code, str)
        or not isinstance(reason, str)
    ):
        raise Phase6PreparationError(
            "BHPT direct terminal evidence is neither result nor blocker"
        )
    blocker = {"code": blocker_code, "reason": reason}
    return DerivedEvidence(
        evidence_id=evidence_id,
        adapter="BHPT_DIRECT_V1",
        role="BLOCKER",
        independence_class="NONE",
        state="NOT_ASSESSED",
        blocker=blocker,
        science_executed=False,
        implementation_hashes=(),
        expected_items=30,
        assessed_item_ids=(),
        assessed_items=0,
        coverage_family="bhpt_direct_v1",
        numerical_budget=_required_budget(NUMERICAL_BUDGET_FIELDS),
        convention_budget=_required_budget(CONVENTION_BUDGET_FIELDS),
        native_summary={
            "native_status": terminal_status,
            "native_blocker": blocker_code,
        },
        native_domain=None,
        limitations=(reason,),
        method="external BHPT direct runtime/source blocker",
    )


def _load_identity_json(identity: Mapping[str, object]) -> Mapping[str, object]:
    path = Path(str(identity.get("path")))
    raw = path.read_bytes()
    payload = json.loads(raw)
    if not isinstance(payload, Mapping) or raw != canonical_json_bytes(payload):
        raise Phase6PreparationError("native referenced JSON is not canonical")
    return payload


def _load_identity_jsonl(
    identity: Mapping[str, object],
) -> tuple[Mapping[str, object], ...]:
    path = Path(str(identity.get("path")))
    raw = path.read_bytes()
    records: list[Mapping[str, object]] = []
    for line in raw.splitlines(keepends=True):
        payload = json.loads(line)
        if not isinstance(payload, Mapping) or canonical_json_bytes(payload) != line:
            raise Phase6PreparationError("native referenced JSONL is not canonical")
        records.append(payload)
    return tuple(records)


def _observable(
    evidence_id: str,
    artifacts: Sequence[OriginArtifact],
    selector: Mapping[str, object],
) -> DerivedEvidence:
    from schwgw.validation.phase6_observable_evidence import (  # noqa: PLC0415
        validate_bundle as validate_observable_bundle,
    )

    bundle = _artifact_payload(artifacts, "observable_evidence.json")
    if bundle.get("schema") != OBSERVABLE_BUNDLE_SCHEMA:
        raise Phase6PreparationError("observable bundle schema changed")
    validate_observable_bundle(bundle)
    source_certificate_id = str(selector["source_certificate_id"])
    matches = [
        certificate
        for certificate in bundle["certificates"]
        if certificate.get("certificate_id") == source_certificate_id
    ]
    if len(matches) != 1:
        raise Phase6PreparationError(
            "observable source certificate selection is not unique"
        )
    certificate = matches[0]
    native_state = certificate["state"]
    if native_state not in STATES:
        raise Phase6PreparationError("observable native state changed")
    domain = _load_identity_json(certificate["parameter_domain_identity"])
    assessed_records = _load_identity_jsonl(domain["assessed_item_index_identity"])
    coverage = domain["coverage"]
    if native_state == "NOT_ASSESSED":
        role = "BLOCKER"
        independence = "NONE"
        state = "NOT_ASSESSED"
        blocker: Mapping[str, str] | None = {
            "code": "NO_OBSERVABLE_MEASUREMENT",
            "reason": "native observable certificate contains no assessed result",
        }
        implementation_hashes: tuple[str, ...] = ()
        science_executed = False
    else:
        role = "PRIMARY_SCIENCE"
        independence = "SAME_IMPLEMENTATION"
        state = "PARTIAL" if native_state == "PASS" else str(native_state)
        blocker = None
        science_executed = True
        hashes: set[str] = set()
        for descriptor in certificate["evidence_inventory"].values():
            if descriptor["role"] != "PRIMARY_SCIENCE":
                continue
            for identity in descriptor["provenance"]["source_snapshot_identities"]:
                hashes.add(_sha(identity["sha256"], "observable implementation hash"))
        if not hashes:
            # The normalized primary envelope needs an implementation identity;
            # bind the populated bundle bytes when producer source snapshots do
            # not expose a dedicated implementation digest.
            hashes.add(
                next(
                    artifact.origin_identity["sha256"]
                    for artifact in artifacts
                    if artifact.relative_path == "observable_evidence.json"
                )
            )
        implementation_hashes = tuple(sorted(hashes))
    numerical = _required_budget(NUMERICAL_BUDGET_FIELDS)
    numerical_name_map = {
        "lmax": "lmax_tail",
        **{name: name for name in NUMERICAL_BUDGET_FIELDS if name != "lmax"},
    }
    for target, native_name in numerical_name_map.items():
        native = certificate["numerical_budget"][native_name]
        assessment = native["assessment"]
        numerical[target] = _budget_component(
            state=str(assessment["state"]),
            estimate=assessment["measured_value"],
            units=assessment["units"],
            reason=assessment["reason"],
        )
    convention = _required_budget(CONVENTION_BUDGET_FIELDS)
    for name in CONVENTION_BUDGET_FIELDS:
        native = certificate["convention_budget"][name]
        assessment = native["assessment"]
        convention[name] = _budget_component(
            state=str(assessment["state"]),
            estimate=assessment["measured_value"],
            units=assessment["units"],
            reason=assessment["reason"],
        )
    native_domain = {
        "gate": certificate["acceptance_gate"],
        "observable": certificate["observable"],
        "domain_id": domain["domain_id"],
        "parameters": domain["parameters"],
        "selection_policy": domain["selection_policy"],
        "expected_items": coverage["expected_items"],
    }
    return DerivedEvidence(
        evidence_id=evidence_id,
        adapter="OBSERVABLE_FORMAL_ROOT_V1",
        role=role,
        independence_class=independence,
        state=state,
        blocker=blocker,
        science_executed=science_executed,
        implementation_hashes=implementation_hashes,
        expected_items=int(coverage["expected_items"]),
        assessed_item_ids=tuple(
            sorted(_item_id(record) for record in assessed_records)
        ),
        assessed_items=int(coverage["assessed_items"]),
        coverage_family=f"observable_bundle:{source_certificate_id}",
        numerical_budget=numerical,
        convention_budget=convention,
        native_summary={
            "native_certificate_id": source_certificate_id,
            "native_state": native_state,
            "normalized_state": state,
            "native_science_roles": sorted(
                {
                    descriptor["role"]
                    for descriptor in certificate["evidence_inventory"].values()
                    if descriptor["role"] in {"PRIMARY_SCIENCE", "INDEPENDENT_SCIENCE"}
                }
            ),
        },
        native_domain=native_domain,
        limitations=tuple(str(item) for item in certificate["limitations"])
        + (
            ("native PASS capped at PARTIAL in a single-role release projection",)
            if native_state == "PASS"
            else ()
        ),
        method="populated observable certificate, normalized without role laundering",
    )


def _validate_typed_budget(
    value: object, fields: Sequence[str], label: str
) -> dict[str, Mapping[str, object]]:
    budget = _exact(value, set(fields), label)
    result: dict[str, Mapping[str, object]] = {}
    for name in fields:
        record = _exact(
            budget[name], {"state", "estimate", "units", "reason"}, f"{label}.{name}"
        )
        result[name] = _budget_component(
            state=str(record["state"]),
            estimate=record["estimate"],
            units=record["units"],
            reason=record["reason"],
        )
    return result


def _typed_physical(
    evidence_id: str,
    artifacts: Sequence[OriginArtifact],
    *,
    production_finite_radius: bool,
    allow_bhpt_direct_comparison: bool = False,
) -> DerivedEvidence:
    report = _artifact_payload(artifacts, "report.json")
    expected_schema = (
        PRODUCTION_FINITE_RADIUS_RESULT_SCHEMA
        if production_finite_radius
        else TYPED_PHYSICAL_RESULT_SCHEMA
    )
    fields = {
        "schema",
        "result_id",
        "role",
        "independence_class",
        "gate",
        "observable",
        "parameter_domain",
        "item_results",
        "state",
        "reason",
        "limitations",
        "implementation_source_sha256s",
        "numerical_uncertainty_budget",
        "convention_uncertainty_budget",
        "scientific_evidence",
        "science_executed",
        "kernel_unit_test_only",
        "global_green_permitted",
        "li_figure_agreement_primary_gate",
        "full_paper_figure_rerun",
        "observer_qualification",
    }
    item = _exact(report, fields, "typed physical report")
    if (
        item["schema"] != expected_schema
        or item["scientific_evidence"] is not True
        or item["science_executed"] is not True
        or item["kernel_unit_test_only"] is not False
        or item["global_green_permitted"] is not False
        or item["li_figure_agreement_primary_gate"] is not False
        or item["full_paper_figure_rerun"] is not False
    ):
        raise Phase6PreparationError("typed physical report policy changed")
    _identifier(item["result_id"], "typed result_id")
    role = item["role"]
    independence = item["independence_class"]
    if role == "PRIMARY_SCIENCE" and independence != "SAME_IMPLEMENTATION":
        raise Phase6PreparationError("typed primary independence is contradictory")
    if role == "INDEPENDENT_SCIENCE" and independence not in {
        "ALGORITHMICALLY_INDEPENDENT",
        "EXTERNAL_SOURCE",
    }:
        raise Phase6PreparationError("typed independent source is not independent")
    if role not in {"PRIMARY_SCIENCE", "INDEPENDENT_SCIENCE"}:
        raise Phase6PreparationError("typed physical role changed")
    gate = item["gate"]
    observable = item["observable"]
    if gate not in GATE_OBSERVABLES or observable not in GATE_OBSERVABLES[gate]:
        raise Phase6PreparationError("typed physical gate/observable changed")
    domain = _exact(
        item["parameter_domain"],
        {
            "domain_id",
            "description",
            "parameters",
            "selection_policy",
            "expected_items",
            "expected_item_ids",
        },
        "typed physical domain",
    )
    _identifier(domain["domain_id"], "typed domain_id")
    _text(domain["description"], "typed domain description")
    _text(domain["selection_policy"], "typed selection policy")
    if not isinstance(domain["parameters"], Mapping) or not domain["parameters"]:
        raise Phase6PreparationError("typed domain parameters changed")
    _json_value(domain["parameters"], "typed domain parameters")
    expected_items = domain["expected_items"]
    if (
        isinstance(expected_items, bool)
        or not isinstance(expected_items, int)
        or expected_items < 1
    ):
        raise Phase6PreparationError("typed domain expected_items changed")
    expected_item_ids = domain["expected_item_ids"]
    if (
        not isinstance(expected_item_ids, list)
        or expected_item_ids != sorted(set(expected_item_ids))
        or len(expected_item_ids) != expected_items
        or any(
            not isinstance(value, str) or not _ID.fullmatch(value)
            for value in expected_item_ids
        )
    ):
        raise Phase6PreparationError("typed expected item inventory changed")
    item_results = item["item_results"]
    if not isinstance(item_results, list):
        raise Phase6PreparationError("typed item_results must be a list")
    ids: list[str] = []
    states: list[str] = []
    for index, raw_result in enumerate(item_results):
        result = _exact(raw_result, {"item_id", "state"}, f"typed item[{index}]")
        ids.append(_identifier(result["item_id"], "typed item_id"))
        if result["state"] not in STATES or result["state"] == "NOT_ASSESSED":
            raise Phase6PreparationError("typed assessed item state changed")
        states.append(str(result["state"]))
    if (
        ids != sorted(set(ids))
        or not set(ids) <= set(expected_item_ids)
        or len(ids) > expected_items
    ):
        raise Phase6PreparationError("typed assessed item inventory changed")
    numerical = _validate_typed_budget(
        item["numerical_uncertainty_budget"],
        NUMERICAL_BUDGET_FIELDS,
        "typed numerical budget",
    )
    convention = _validate_typed_budget(
        item["convention_uncertainty_budget"],
        CONVENTION_BUDGET_FIELDS,
        "typed convention budget",
    )
    budget_states = [
        str(record["state"]) for record in (*numerical.values(), *convention.values())
    ]
    if "FAIL" in [*states, *budget_states]:
        derived_state = "FAIL"
    elif (
        ids == expected_item_ids
        and states
        and all(state == "PASS" for state in states)
        and all(state == "PASS" for state in budget_states)
    ):
        derived_state = "PASS"
    else:
        derived_state = "PARTIAL"
    if item["state"] != derived_state:
        raise Phase6PreparationError("typed physical state is not derived")
    hashes = item["implementation_source_sha256s"]
    if (
        not isinstance(hashes, list)
        or hashes != sorted(set(hashes))
        or not hashes
        or any(
            not isinstance(value, str) or not _SHA256.fullmatch(value)
            for value in hashes
        )
    ):
        raise Phase6PreparationError("typed implementation hashes changed")
    observer = _exact(
        item["observer_qualification"],
        {
            "output_kind",
            "worldline_tetrad_pure_gauge_test",
            "detector_response_claim_permitted",
        },
        "typed observer qualification",
    )
    detector_pass = observer["worldline_tetrad_pure_gauge_test"] == "PASS"
    if observer["worldline_tetrad_pure_gauge_test"] not in STATES or (
        observer["detector_response_claim_permitted"] is not detector_pass
    ):
        raise Phase6PreparationError("typed detector-response qualification changed")
    is_bhpt_direct_comparison = (
        domain["domain_id"] == "bhpt_direct_conditioned_selected_30"
        or observer["output_kind"] == "RADIAL_S_MATRIX_CROSS_BACKEND_COMPARISON"
    )
    if is_bhpt_direct_comparison and not allow_bhpt_direct_comparison:
        raise Phase6PreparationError(
            "BHPT direct comparison report requires its dedicated three-file adapter"
        )
    if production_finite_radius and (
        gate != "V4" or observable != "finite_radius_tidal_detector"
    ):
        raise Phase6PreparationError("production finite-radius report has wrong scope")
    if gate == "V4":
        if (
            not detector_pass
            and observer["output_kind"] != "FINITE_RADIUS_TIDAL_RESPONSE"
        ):
            raise Phase6PreparationError(
                "finite-radius output overclaims detector response"
            )
        if not detector_pass and derived_state == "PASS":
            raise Phase6PreparationError(
                "pure-gauge detector test is required for V4 PASS"
            )
    limitations = item["limitations"]
    if not isinstance(limitations, list) or any(
        not isinstance(text, str) or not text for text in limitations
    ):
        raise Phase6PreparationError("typed physical limitations changed")
    return DerivedEvidence(
        evidence_id=evidence_id,
        adapter=(
            "PRODUCTION_FINITE_RADIUS_V1"
            if production_finite_radius
            else "TYPED_PHYSICAL_RESULT_V1"
        ),
        role=str(role),
        independence_class=str(independence),
        state=derived_state,
        blocker=None,
        science_executed=True,
        implementation_hashes=tuple(str(value) for value in hashes),
        expected_items=expected_items,
        assessed_item_ids=tuple(ids),
        assessed_items=len(ids),
        coverage_family=f"typed:{item['result_id']}",
        numerical_budget=numerical,
        convention_budget=convention,
        native_summary={
            "native_state": derived_state,
            "native_item_state_counts": {
                state: states.count(state) for state in STATES
            },
            "observer_qualification": observer,
        },
        native_domain={
            **dict(domain),
            "gate": gate,
            "observable": observable,
        },
        limitations=tuple(str(text) for text in limitations),
        method="strict typed immutable physical validation report",
    )


def _bhpt_direct_comparison(
    evidence_id: str,
    artifacts: Sequence[OriginArtifact],
    root: Path,
) -> DerivedEvidence:
    """Bind the typed projection to its native three-file comparison root."""

    from schwgw.validation.phase6_bhpt_direct_comparison import (  # noqa: PLC0415
        BHPTConditionedComparisonError,
        COMPARISON_SCHEMA,
        MANIFEST_SCHEMA,
        TYPED_RESULT_SCHEMA,
        validate_comparison_payload,
        validate_published_bhpt_conditioned_comparison,
        validate_typed_report,
    )

    if (
        COMPARISON_SCHEMA != BHPT_DIRECT_COMPARISON_SCHEMA
        or MANIFEST_SCHEMA != BHPT_DIRECT_COMPARISON_MANIFEST_SCHEMA
        or TYPED_RESULT_SCHEMA != TYPED_PHYSICAL_RESULT_SCHEMA
    ):
        raise Phase6PreparationError("BHPT direct comparison schema binding changed")
    comparison_artifact = next(
        artifact
        for artifact in artifacts
        if artifact.relative_path == "comparison.json"
    )
    report_artifact = next(
        artifact for artifact in artifacts if artifact.relative_path == "report.json"
    )
    comparison = comparison_artifact.payload
    report = report_artifact.payload
    if not isinstance(comparison, Mapping) or not isinstance(report, Mapping):
        raise Phase6PreparationError("BHPT direct comparison payload is missing")
    try:
        validate_published_bhpt_conditioned_comparison(root)
        validate_comparison_payload(comparison)
        validate_typed_report(
            report,
            comparison=comparison,
            comparison_sha256=str(comparison_artifact.origin_identity["sha256"]),
        )
    except (BHPTConditionedComparisonError, OSError) as exc:
        raise Phase6PreparationError(
            "BHPT direct comparison native three-file validation failed"
        ) from exc
    manifest = _exact(
        _artifact_payload(artifacts, "manifest.json"),
        {
            "comparison_identity",
            "comparison_status_counts",
            "created_at_utc",
            "global_green_permitted",
            "key_count",
            "li_figure_agreement_primary_gate",
            "overall_state",
            "release_projection",
            "report_identity",
            "schema",
            "source_role_ledger",
            "status",
        },
        "BHPT direct comparison manifest",
    )
    if (
        manifest["schema"] != BHPT_DIRECT_COMPARISON_MANIFEST_SCHEMA
        or not _native_identity_matches(
            manifest["comparison_identity"], comparison_artifact
        )
        or not _native_identity_matches(manifest["report_identity"], report_artifact)
        or manifest["comparison_status_counts"]
        != {"FAIL": 6, "NOT_ASSESSED": 0, "PARTIAL": 24, "PASS": 0}
        or manifest["global_green_permitted"] is not False
        or manifest["li_figure_agreement_primary_gate"] is not False
        or manifest["key_count"] != 30
        or manifest["overall_state"] != "FAIL"
        or manifest["release_projection"] != comparison["release_projection"]
        or manifest["source_role_ledger"] != comparison["source_role_ledger"]
        or manifest["status"] != "COMPLETE_WITH_INTERNAL_SCIENTIFIC_FAILURES"
    ):
        raise Phase6PreparationError(
            "BHPT direct comparison manifest/detail/report linkage changed"
        )
    derived = _typed_physical(
        evidence_id,
        artifacts,
        production_finite_radius=False,
        allow_bhpt_direct_comparison=True,
    )
    if (
        derived.state != "FAIL"
        or derived.role != "INDEPENDENT_SCIENCE"
        or derived.independence_class != "EXTERNAL_SOURCE"
        or derived.expected_items != 30
        or derived.assessed_items != 30
        or derived.native_summary["native_item_state_counts"]
        != {"NOT_ASSESSED": 0, "PARTIAL": 24, "PASS": 0, "FAIL": 6}
    ):
        raise Phase6PreparationError(
            "BHPT direct comparison 24/6 release projection changed"
        )
    source_evidence = _exact(
        comparison["source_evidence"],
        {"bhpt_direct", "conditioning_campaign", "conditioning_shards"},
        "BHPT direct comparison source evidence",
    )
    return replace(
        derived,
        adapter="BHPT_DIRECT_COMPARISON_V1",
        coverage_family="bhpt_direct_conditioned_comparison:selected_30",
        native_summary={
            **dict(derived.native_summary),
            "native_comparison_sha256": comparison_artifact.origin_identity["sha256"],
            "native_report_sha256": report_artifact.origin_identity["sha256"],
            "comparison_status_counts": dict(comparison["comparison_status_counts"]),
            "source_role_ledger": dict(comparison["source_role_ledger"]),
            "external_source_evidence": dict(source_evidence["bhpt_direct"]),
            "internal_source_evidence": {
                "conditioning_campaign": dict(source_evidence["conditioning_campaign"]),
                "conditioning_shards": list(source_evidence["conditioning_shards"]),
            },
        },
        limitations=derived.limitations
        + (
            "native comparison source-role ledger and full external/internal identities are preserved in the immutable comparison snapshot",
        ),
        method=(
            "strict BHPT-direct versus conditioned-radial three-file comparison "
            "reload with native source rebuild"
        ),
    )


def _v1_radial_selected_acceptance(
    evidence_id: str,
    artifacts: Sequence[OriginArtifact],
    root: Path,
) -> DerivedEvidence:
    """Bind the repaired 30-key SchWO/BHPT acceptance root."""

    from schwgw.validation.phase6_v1_radial_acceptance import (  # noqa: PLC0415
        EXPECTED_KEY_COUNT,
        MANIFEST_SCHEMA,
        SUMMARY_SCHEMA,
        V1RadialAcceptanceError,
        validate_published_selected_acceptance,
    )

    try:
        native = validate_published_selected_acceptance(root)
    except (V1RadialAcceptanceError, OSError) as exc:
        raise Phase6PreparationError(
            "V1 selected radial acceptance native validation failed"
        ) from exc
    manifest = _artifact_payload(artifacts, "manifest.json")
    summary = _artifact_payload(artifacts, "summary.json")
    if (
        manifest.get("schema") != MANIFEST_SCHEMA
        or summary.get("schema") != SUMMARY_SCHEMA
        or dict(summary) != native
        or summary.get("overall_state") != "PASS"
        or summary.get("record_count") != EXPECTED_KEY_COUNT
        or summary.get("numerical_pass_key_count") != EXPECTED_KEY_COUNT
        or summary.get("failed_key_count") != 0
    ):
        raise Phase6PreparationError(
            "V1 selected radial acceptance is not an exact 30/30 PASS"
        )
    derived = _typed_physical(
        evidence_id,
        artifacts,
        production_finite_radius=False,
        allow_bhpt_direct_comparison=True,
    )
    if (
        derived.state != "PASS"
        or derived.role != "INDEPENDENT_SCIENCE"
        or derived.independence_class != "EXTERNAL_SOURCE"
        or derived.expected_items != EXPECTED_KEY_COUNT
        or derived.assessed_items != EXPECTED_KEY_COUNT
        or derived.native_summary["native_item_state_counts"]
        != {"NOT_ASSESSED": 0, "PARTIAL": 0, "PASS": EXPECTED_KEY_COUNT, "FAIL": 0}
    ):
        raise Phase6PreparationError(
            "V1 selected radial acceptance release projection changed"
        )
    return replace(
        derived,
        adapter="V1_RADIAL_SELECTED_ACCEPTANCE_V1",
        coverage_family="v1_radial_selected_acceptance:bhpt_30",
        native_summary={
            **dict(derived.native_summary),
            "direct_root": dict(summary["direct_root"]),
            "native_summary_sha256": sha256_bytes(canonical_json_bytes(summary)),
            "source_role_ledger": dict(summary["source_role_ledger"]),
        },
        method=(
            "strict 30-key repaired-boundary SchWO versus independent external "
            "Regge-Wheeler/Zerilli acceptance reload"
        ),
    )


def _v1_ap_selected_evidence(
    evidence_id: str,
    artifacts: Sequence[OriginArtifact],
    root: Path,
) -> DerivedEvidence:
    """Bind the independently solved 24-anchor mpmath evidence wrapper."""

    from schwgw.validation.phase6_v1_ap_selected_evidence import (  # noqa: PLC0415
        MANIFEST_SCHEMA,
        V1APSelectedEvidenceError,
        validate_published_ap_selected_evidence,
    )

    try:
        native = validate_published_ap_selected_evidence(root)
    except (V1APSelectedEvidenceError, OSError) as exc:
        raise Phase6PreparationError(
            "V1 AP selected evidence native validation failed"
        ) from exc
    manifest = _artifact_payload(artifacts, "manifest.json")
    report = _artifact_payload(artifacts, "report.json")
    if (
        manifest.get("schema") != MANIFEST_SCHEMA
        or dict(report) != native
        or report.get("state") != "PARTIAL"
    ):
        raise Phase6PreparationError("V1 AP selected wrapper changed")
    derived = _typed_physical(
        evidence_id,
        artifacts,
        production_finite_radius=False,
    )
    if (
        derived.state != "PARTIAL"
        or derived.role != "INDEPENDENT_SCIENCE"
        or derived.independence_class != "ALGORITHMICALLY_INDEPENDENT"
        or derived.expected_items != 24
        or derived.assessed_items != 24
        or derived.native_summary["native_item_state_counts"]
        != {"NOT_ASSESSED": 0, "PARTIAL": 0, "PASS": 24, "FAIL": 0}
    ):
        raise Phase6PreparationError("V1 AP selected release projection changed")
    ledger = _artifact_payload(artifacts, "source_ledger.json")
    return replace(
        derived,
        adapter="V1_AP_SELECTED_EVIDENCE_V1",
        coverage_family="v1_ap_selected:24",
        native_summary={
            **dict(derived.native_summary),
            "source_ledger": dict(ledger),
        },
        method="strict independent 60/80-dps and step-size ladder reload",
    )


def _v1_final_radial_baseline_v2(
    evidence_id: str,
    artifacts: Sequence[OriginArtifact],
    root: Path,
    selector: object,
) -> DerivedEvidence:
    """Bind the exact turning-aware D_union algorithmic baseline."""

    from schwgw.validation.phase6_v1_final_radial_baseline_v2 import (  # noqa: PLC0415
        EXPECTED_KEY_COUNT,
        MANIFEST_SCHEMA,
        SUMMARY_SCHEMA,
        V1FinalBaselineV2Error,
        validate_published_final_baseline_v2,
    )

    try:
        native = validate_published_final_baseline_v2(root)
    except (V1FinalBaselineV2Error, OSError) as exc:
        raise Phase6PreparationError(
            "V1 final radial baseline native validation failed"
        ) from exc
    manifest = _artifact_payload(artifacts, "manifest.json")
    summary = _artifact_payload(artifacts, "summary.json")
    selected = _exact(selector, {"projection"}, "V1 final-baseline selector")
    projection = str(selected["projection"])
    if projection not in {"radial_s_matrix_flux", "generic_conditioning_backend"}:
        raise Phase6PreparationError("V1 final-baseline projection changed")
    if (
        manifest.get("schema") != MANIFEST_SCHEMA
        or summary.get("schema") != SUMMARY_SCHEMA
        or dict(summary) != native
        or summary.get("overall_state") != "PASS"
        or summary.get("numerical_state") != "PASS"
        or summary.get("completed_key_count") != EXPECTED_KEY_COUNT
        or summary.get("pass_key_count") != EXPECTED_KEY_COUNT
        or summary.get("failed_key_count") != 0
    ):
        raise Phase6PreparationError(
            "V1 final radial baseline is not an exact 17,818-key algorithmic PASS"
        )
    derived = _typed_physical(
        evidence_id,
        artifacts,
        production_finite_radius=False,
    )
    if (
        derived.state != "PARTIAL"
        or derived.role != "PRIMARY_SCIENCE"
        or derived.independence_class != "SAME_IMPLEMENTATION"
        or derived.expected_items != EXPECTED_KEY_COUNT
        or derived.assessed_items != EXPECTED_KEY_COUNT
        or derived.native_summary["native_item_state_counts"]
        != {"NOT_ASSESSED": 0, "PARTIAL": 0, "PASS": EXPECTED_KEY_COUNT, "FAIL": 0}
    ):
        raise Phase6PreparationError(
            "V1 final radial baseline conservative projection changed"
        )
    native_domain = dict(derived.native_domain or {})
    if projection == "generic_conditioning_backend":
        native_domain.update(
            {
                "description": (
                    "exact frozen D_union unified turning-aware generic backend; "
                    "independent full-domain backend comparison remains open"
                ),
                "domain_id": "final_turning_aware_d_union_backend_17818",
                "gate": "V1Q",
                "observable": "generic_conditioning_backend",
                "selection_policy": (
                    "exact ordered D_union through one generic turning-proxy and "
                    "Jost-quality policy; no named-mode envelope"
                ),
            }
        )
    return replace(
        derived,
        adapter="V1_FINAL_RADIAL_BASELINE_V2",
        coverage_family=(
            "v1q_final_turning_aware_d_union:17818"
            if projection == "generic_conditioning_backend"
            else "v1_final_turning_aware_d_union:17818"
        ),
        native_summary={
            **dict(derived.native_summary),
            "algorithmic_summary": dict(summary),
            "projection": projection,
        },
        native_domain=native_domain,
        method=(
            "strict full D_union generic turning-aware backend projection; "
            "independent full-domain backend difference remains NOT_ASSESSED"
            if projection == "generic_conditioning_backend"
            else (
                "strict full D_union turning-aware/r_in-repaired baseline reload; "
                "independent-backend budgets remain selected-domain"
            )
        ),
    )


def _v1_production_state_evidence(
    evidence_id: str,
    artifacts: Sequence[OriginArtifact],
    root: Path,
    selector: object,
) -> DerivedEvidence:
    """Bind the exact D_prod original-plus-repair radial-state composition."""

    from schwgw.validation.phase6_v1_production_state_evidence import (  # noqa: PLC0415
        MANIFEST_SCHEMA,
        V1ProductionStateEvidenceError,
        validate_published_production_state_evidence,
    )

    try:
        native = validate_published_production_state_evidence(root)
    except (V1ProductionStateEvidenceError, OSError) as exc:
        raise Phase6PreparationError(
            "V1 production state evidence native validation failed"
        ) from exc
    manifest = _artifact_payload(artifacts, "manifest.json")
    report = _artifact_payload(artifacts, "report.json")
    selected = _exact(selector, {"projection"}, "V1 production-state selector")
    projection = str(selected["projection"])
    if projection not in {"radial_s_matrix_flux", "generic_conditioning_backend"}:
        raise Phase6PreparationError("V1 production-state projection changed")
    if (
        manifest.get("schema") != MANIFEST_SCHEMA
        or dict(report) != native
        or report.get("state") != "PARTIAL"
    ):
        raise Phase6PreparationError("V1 production state wrapper changed")
    derived = _typed_physical(
        evidence_id,
        artifacts,
        production_finite_radius=False,
    )
    if (
        derived.state != "PARTIAL"
        or derived.role != "PRIMARY_SCIENCE"
        or derived.independence_class != "SAME_IMPLEMENTATION"
        or derived.expected_items != 16_048
        or derived.assessed_items != 16_048
        or derived.native_summary["native_item_state_counts"]
        != {"NOT_ASSESSED": 0, "PARTIAL": 0, "PASS": 16_048, "FAIL": 0}
    ):
        raise Phase6PreparationError(
            "V1 production state conservative projection changed"
        )
    ledger = _artifact_payload(artifacts, "source_ledger.json")
    native_domain = dict(derived.native_domain or {})
    if projection == "generic_conditioning_backend":
        native_domain.update(
            {
                "description": (
                    "exact repaired D_prod generic-backend radial-state coverage; "
                    "independent full-domain backend comparison remains open"
                ),
                "domain_id": "production_d_prod_backend_repaired_16048",
                "gate": "V1Q",
                "observable": "generic_conditioning_backend",
                "selection_policy": (
                    "exact frozen D_prod original 12666 plus generic scaled-tortoise "
                    "repair 3382; no domain extrapolation"
                ),
            }
        )
    return replace(
        derived,
        adapter="V1_PRODUCTION_STATE_EVIDENCE_V1",
        coverage_family=(
            "v1q_production_generic_backend_states:16048"
            if projection == "generic_conditioning_backend"
            else "v1_production_eight_radius_states:16048"
        ),
        native_summary={
            **dict(derived.native_summary),
            "projection": projection,
            "source_ledger": dict(ledger),
        },
        native_domain=native_domain,
        method=(
            "strict original 12,666 plus repaired 3,382 generic-backend exact-state projection; "
            "independent full-domain backend difference remains NOT_ASSESSED"
            if projection == "generic_conditioning_backend"
            else "strict original 12,666 plus repaired 3,382 exact-state reload"
        ),
    )


def _campaign_state_counts(
    value: object,
    *,
    expected_items: int,
    label: str,
) -> dict[str, int]:
    counts = _exact(value, set(STATES), label)
    normalized: dict[str, int] = {}
    for state in STATES:
        count = counts[state]
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise Phase6PreparationError(f"{label} contains an invalid count")
        normalized[state] = count
    if sum(normalized.values()) != expected_items:
        raise Phase6PreparationError(f"{label} does not cover its exact domain")
    return normalized


def _campaign_hashes(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, Mapping) or not value:
        raise Phase6PreparationError(f"{label} is empty")
    hashes = tuple(sorted({_sha(digest, label) for digest in value.values()}))
    return hashes


def _conditioning_campaign_budget(
    value: object,
    *,
    fields: Sequence[str],
    state: str,
    kind: str,
    expected_items: int,
) -> dict[str, Mapping[str, object]]:
    summary = _exact(value, {"components", "status_counts"}, f"{kind} budget")
    _campaign_state_counts(
        summary["status_counts"],
        expected_items=expected_items,
        label=f"{kind} budget status counts",
    )
    components = summary["components"]
    if not isinstance(components, Mapping):
        raise Phase6PreparationError(f"{kind} budget components changed")
    native_fields = (
        set(NUMERICAL_BUDGET_FIELDS)
        if kind == "numerical"
        else set(CONVENTION_BUDGET_FIELDS) - {"worldline"}
    )
    if set(components) != native_fields:
        raise Phase6PreparationError(f"{kind} campaign budget fields changed")
    normalized: dict[str, Mapping[str, object]] = {}
    for field in fields:
        native_field = "observer" if field == "worldline" else field
        component = _exact(
            components[native_field],
            {
                "assessed_count",
                "maximum_assessed",
                "minimum_assessed",
                "unassessed_sentinel_count",
            },
            f"{kind} campaign budget component {native_field}",
        )
        assessed = component["assessed_count"]
        unassessed = component["unassessed_sentinel_count"]
        if (
            isinstance(assessed, bool)
            or not isinstance(assessed, int)
            or assessed < 0
            or isinstance(unassessed, bool)
            or not isinstance(unassessed, int)
            or unassessed < 0
            or assessed + unassessed != expected_items
        ):
            raise Phase6PreparationError(f"{kind} campaign component coverage changed")
        maximum = component["maximum_assessed"]
        minimum = component["minimum_assessed"]
        if assessed == 0:
            if maximum is not None or minimum is not None:
                raise Phase6PreparationError(
                    f"{kind} campaign unassessed component has an estimate"
                )
        else:
            maximum_text = _decimal_text(maximum)
            minimum_text = _decimal_text(minimum)
            if (
                maximum_text is None
                or minimum_text is None
                or Decimal(minimum_text) > Decimal(maximum_text)
            ):
                raise Phase6PreparationError(
                    f"{kind} campaign component extrema changed"
                )
        component_state = "NOT_ASSESSED" if assessed == 0 else "PARTIAL"
        normalized[field] = _budget_component(
            state=component_state,
            estimate=maximum if assessed else None,
            units="dimensionless",
            reason=(
                f"conditioning campaign {kind} component {native_field}: "
                f"assessed={assessed}, unassessed={unassessed}; native aggregate "
                f"scientific state={state} is tracked separately"
            ),
        )
    return normalized


def _conditioning_transition_budget(
    value: object,
    *,
    fields: Sequence[str],
    state: str,
    kind: str,
    transition_counts: Mapping[str, int],
) -> dict[str, Mapping[str, object]]:
    """Project D_union summaries onto the exact 158-key transition domain."""

    summary = _exact(value, {"components", "status_counts"}, f"{kind} budget")
    _campaign_state_counts(
        summary["status_counts"],
        expected_items=17_818,
        label=f"{kind} budget status counts",
    )
    components = summary["components"]
    native_fields = (
        set(NUMERICAL_BUDGET_FIELDS)
        if kind == "numerical"
        else set(CONVENTION_BUDGET_FIELDS) - {"worldline"}
    )
    if not isinstance(components, Mapping) or set(components) != native_fields:
        raise Phase6PreparationError(f"{kind} campaign budget fields changed")
    transition_assessed = transition_counts["PARTIAL"] + transition_counts["PASS"]
    transition_unassessed = 158 - transition_assessed
    result: dict[str, Mapping[str, object]] = {}
    for field in fields:
        native_field = "observer" if field == "worldline" else field
        component = _exact(
            components[native_field],
            {
                "assessed_count",
                "maximum_assessed",
                "minimum_assessed",
                "unassessed_sentinel_count",
            },
            f"{kind} campaign budget component {native_field}",
        )
        selected_assessed = (
            0
            if native_field == "backend_difference"
            or (kind == "convention" and native_field != "phase_origin")
            else transition_assessed
        )
        selected_unassessed = 158 - selected_assessed
        if selected_assessed and component["maximum_assessed"] is None:
            raise Phase6PreparationError(
                f"transition {kind} component lacks an assessed estimate"
            )
        component_state = "PARTIAL" if selected_assessed else "NOT_ASSESSED"
        result[field] = _budget_component(
            state=component_state,
            estimate=(component["maximum_assessed"] if selected_assessed else None),
            units="dimensionless",
            reason=(
                f"conditioning transition-domain {kind} component {native_field}: "
                f"assessed={selected_assessed}, unassessed={selected_unassessed} "
                f"within 158 keys (native successful={transition_assessed}, "
                f"native failed/open={transition_unassessed}); aggregate scientific "
                f"state={state} is tracked separately"
            ),
        )
    return result


def _campaign_domain_keys(
    projection: str,
    *,
    production: bool,
) -> tuple[object, ...]:
    from schwgw.validation import phase6_conditioning_campaign as conditioning  # noqa: PLC0415

    frozen = conditioning.load_frozen_scan_contract(
        conditioning.DOMAIN_ROOT,
        conditioning.EXECUTION_ROOT,
    )
    if production:
        from schwgw.validation.phase6_production_finite_radius import (  # noqa: PLC0415
            load_frozen_production_contract,
        )

        project_root = Path(__file__).resolve().parents[3]
        production_contract = load_frozen_production_contract(
            project_root / "runs/phase6/v1_domain_freeze_v3_20260806",
            project_root / "runs/phase6/v1_execution_contract_v4_20260806",
        )
        if projection not in {
            "generic_conditioning_backend",
            "radial_s_matrix_flux",
        }:
            raise Phase6PreparationError("campaign projection changed")
        if len(production_contract.production_keys) != 16_048:
            raise Phase6PreparationError("frozen D_prod domain changed")
        return tuple(production_contract.production_keys)
    if projection == "generic_conditioning_backend":
        transition = tuple(
            sorted(frozen.transition_keys, key=lambda key: key.order_key())
        )
        if len(transition) != 158:
            raise Phase6PreparationError("frozen transition domain changed")
        return transition
    if projection != "radial_s_matrix_flux":
        raise Phase6PreparationError("campaign projection changed")
    if len(frozen.union_keys) != 17_818:
        raise Phase6PreparationError("frozen D_union domain changed")
    return tuple(frozen.union_keys)


def _conditioning_campaign(
    evidence_id: str,
    artifacts: Sequence[OriginArtifact],
    root: Path,
    selector: object,
) -> DerivedEvidence:
    from schwgw.validation.phase6_conditioning_campaign import (  # noqa: PLC0415
        ConditioningCampaignError,
        validate_published_conditioning_campaign,
    )

    try:
        validate_published_conditioning_campaign(root)
    except ConditioningCampaignError as exc:
        raise Phase6PreparationError(
            "conditioning campaign native validation failed"
        ) from exc
    selected = _exact(selector, {"projection"}, "conditioning campaign selector")
    projection = str(selected["projection"])
    index_artifact = next(
        artifact
        for artifact in artifacts
        if artifact.relative_path == "conditioning_campaign_index.json"
    )
    index = _exact(
        index_artifact.payload,
        set(_CONDITIONING_CAMPAIGN_INDEX_FIELDS),
        "conditioning campaign index",
    )
    manifest = _exact(
        _artifact_payload(artifacts, "manifest.json"),
        {
            "campaign_index_identity",
            "created_at_utc",
            "global_green_permitted",
            "key_count",
            "li_figure_agreement_primary_gate",
            "schema",
            "shard_count",
            "status",
        },
        "conditioning campaign manifest",
    )
    if (
        index["schema"] != CONDITIONING_CAMPAIGN_INDEX_SCHEMA
        or index["scientific_evidence"] is not True
        or index["science_executed"] is not True
        or index["kernel_unit_test_only"] is not False
        or index["contract_only"] is not False
        or index["global_green_permitted"] is not False
        or index["li_figure_agreement_primary_gate"] is not False
        or index["paper_agreement_gate"] is not False
        or manifest["schema"] != CONDITIONING_CAMPAIGN_MANIFEST_SCHEMA
        or manifest["global_green_permitted"] is not False
        or manifest["li_figure_agreement_primary_gate"] is not False
        or manifest["campaign_index_identity"] != dict(index_artifact.origin_identity)
    ):
        raise Phase6PreparationError("conditioning campaign policy/linkage changed")
    coverage = _exact(
        index["coverage"],
        {
            "D_union_exact_coverage",
            "D_union_key_list_sha256",
            "extension_key_count",
            "key_count",
            "production_key_count",
            "shard_count",
            "transition_key_count",
        },
        "conditioning campaign coverage",
    )
    if coverage != {
        "D_union_exact_coverage": True,
        "D_union_key_list_sha256": (
            "a5793564dfc28e815699966208ae6605eeeedce9e3629f09512b70e08196810b"
        ),
        "extension_key_count": 1770,
        "key_count": 17_818,
        "production_key_count": 16_048,
        "shard_count": 86,
        "transition_key_count": 158,
    }:
        raise Phase6PreparationError("conditioning campaign exact coverage changed")
    failure = _exact(
        index["failure_summary"],
        {"exact_reason_counts", "scientific_failure_key_count"},
        "conditioning campaign failure summary",
    )
    failure_count = failure["scientific_failure_key_count"]
    if isinstance(failure_count, bool) or not isinstance(failure_count, int):
        raise Phase6PreparationError("conditioning campaign failure count changed")
    native_state = "FAIL" if failure_count else "PARTIAL"
    expected_status = (
        "INDEX_COMPLETE_WITH_SCIENTIFIC_FAILURES"
        if failure_count
        else "INDEX_COMPLETE_WITHOUT_SCIENTIFIC_FAILURES"
    )
    if (
        failure_count < 0
        or failure_count > 17_818
        or index["overall_state"] != native_state
        or index["status"] != expected_status
        or manifest["status"] != expected_status
        or manifest["key_count"] != 17_818
        or manifest["shard_count"] != 86
        or index["production_finite_radius_states"] != "NOT_ASSESSED"
        or not isinstance(index["shards"], list)
        or len(index["shards"]) != 86
    ):
        raise Phase6PreparationError("conditioning campaign native state changed")
    observables = _exact(
        index["observable_status_counts"],
        {
            "conditioning_transition_calibration",
            "flux_conservation",
            "production_finite_radius_states",
            "radial_s_matrix",
            "required_radius_radial_state",
        },
        "conditioning campaign observables",
    )
    for name, counts in observables.items():
        _campaign_state_counts(
            counts,
            expected_items=17_818,
            label=f"conditioning observable {name}",
        )
    if observables["production_finite_radius_states"] != {
        "NOT_ASSESSED": 17_818,
        "PARTIAL": 0,
        "PASS": 0,
        "FAIL": 0,
    }:
        raise Phase6PreparationError(
            "conditioning campaign promoted production finite-radius states"
        )
    transition = _exact(
        index["transition_summary"],
        {"key_count", "key_status_counts", "node_status_counts", "solver_call_count"},
        "conditioning transition summary",
    )
    if transition["key_count"] != 158:
        raise Phase6PreparationError("conditioning transition count changed")
    transition_counts = _campaign_state_counts(
        transition["key_status_counts"],
        expected_items=158,
        label="conditioning transition key counts",
    )
    keys = _campaign_domain_keys(projection, production=False)
    expected_items = len(keys)
    if projection == "generic_conditioning_backend":
        selected_counts = transition_counts
    else:
        selected_counts = _campaign_state_counts(
            observables["radial_s_matrix"],
            expected_items=17_818,
            label="conditioning radial S-matrix counts",
        )
    state = "FAIL" if native_state == "FAIL" or selected_counts["FAIL"] else "PARTIAL"
    budgets = _exact(
        index["budget_summaries"],
        {"convention", "numerical"},
        "conditioning campaign budgets",
    )
    if projection == "generic_conditioning_backend":
        numerical = _conditioning_transition_budget(
            budgets["numerical"],
            fields=NUMERICAL_BUDGET_FIELDS,
            state=state,
            kind="numerical",
            transition_counts=transition_counts,
        )
        convention = _conditioning_transition_budget(
            budgets["convention"],
            fields=CONVENTION_BUDGET_FIELDS,
            state=state,
            kind="convention",
            transition_counts=transition_counts,
        )
    else:
        numerical = _conditioning_campaign_budget(
            budgets["numerical"],
            fields=NUMERICAL_BUDGET_FIELDS,
            state=state,
            kind="numerical",
            expected_items=17_818,
        )
        convention = _conditioning_campaign_budget(
            budgets["convention"],
            fields=CONVENTION_BUDGET_FIELDS,
            state=state,
            kind="convention",
            expected_items=17_818,
        )
    scope = _exact(
        index["scope_qualification"],
        {"observer_response_claim", "radial_s_matrix_only", "required_radius_M"},
        "conditioning campaign scope",
    )
    if (
        scope["observer_response_claim"] is not False
        or scope["radial_s_matrix_only"] is not True
    ):
        raise Phase6PreparationError("conditioning campaign scope was promoted")
    implementation_hashes = _campaign_hashes(
        index["implementation_source_sha_hashes"],
        "conditioning implementation hash",
    )
    return DerivedEvidence(
        evidence_id=evidence_id,
        adapter="CONDITIONING_CAMPAIGN_V1",
        role="PRIMARY_SCIENCE",
        independence_class="SAME_IMPLEMENTATION",
        state=state,
        blocker=None,
        science_executed=True,
        implementation_hashes=implementation_hashes,
        expected_items=expected_items,
        assessed_item_ids=tuple(_item_id(key.to_record()) for key in keys),
        assessed_items=expected_items,
        coverage_family=f"conditioning_campaign:{projection}",
        numerical_budget=numerical,
        convention_budget=convention,
        native_summary={
            "projection": projection,
            "native_overall_state": native_state,
            "native_selected_state_counts": selected_counts,
            "scientific_failure_key_count": failure_count,
            "coverage": dict(coverage),
            "scope_qualification": dict(scope),
        },
        native_domain=None,
        limitations=(
            "radial S-matrix/backend evidence only; no observer or detector response claim",
            f"native campaign contains {failure_count} fail-closed keys",
        ),
        method="strict 86-shard conditioning campaign reload and selected domain projection",
    )


def _production_campaign_budget(
    value: object,
    *,
    fields: Sequence[str],
    state: str,
    kind: str,
) -> dict[str, Mapping[str, object]]:
    budget = _exact(value, {"components", "status"}, f"production {kind} budget")
    if budget["status"] != state:
        raise Phase6PreparationError("production campaign budget state changed")
    components = budget["components"]
    native_fields = (
        set(NUMERICAL_BUDGET_FIELDS)
        if kind == "numerical"
        else set(CONVENTION_BUDGET_FIELDS) - {"worldline"}
    )
    if not isinstance(components, Mapping) or set(components) != native_fields:
        raise Phase6PreparationError("production campaign budget fields changed")
    result: dict[str, Mapping[str, object]] = {}
    for field in fields:
        native_field = "observer" if field == "worldline" else field
        value = components[native_field]
        canonical = _decimal_text(value)
        if canonical is None:
            raise Phase6PreparationError("production campaign budget value changed")
        unassessed = float(value) == _FLOAT64_UNASSESSED_SENTINEL
        result[field] = _budget_component(
            state="NOT_ASSESSED" if unassessed else "PARTIAL",
            estimate=None if unassessed else canonical,
            units="dimensionless",
            reason=(
                f"production finite-radius campaign {kind} component "
                f"{native_field}; {'unassessed sentinel' if unassessed else 'single-configuration estimate'}; "
                f"native aggregate scientific state={state} is tracked separately"
            ),
        )
    return result


def _production_finite_radius_campaign(
    evidence_id: str,
    artifacts: Sequence[OriginArtifact],
    root: Path,
    selector: object,
) -> DerivedEvidence:
    from schwgw.validation.phase6_production_finite_radius_campaign import (  # noqa: PLC0415
        ProductionCampaignError,
        validate_campaign_result,
    )

    selected = _exact(selector, {"projection"}, "production campaign selector")
    projection = str(selected["projection"])
    result_artifact = next(
        artifact
        for artifact in artifacts
        if artifact.relative_path == "campaign_result.json"
    )
    payload = _exact(
        result_artifact.payload,
        set(_PRODUCTION_CAMPAIGN_RESULT_FIELDS),
        "production finite-radius campaign result",
    )
    try:
        validate_campaign_result(payload)
    except ProductionCampaignError as exc:
        raise Phase6PreparationError(
            "production finite-radius native campaign validation failed"
        ) from exc
    manifest = _exact(
        _artifact_payload(artifacts, "manifest.json"),
        {"campaign_result_identity", "global_green_permitted", "schema", "status"},
        "production finite-radius campaign manifest",
    )
    if (
        payload["schema"] != PRODUCTION_CAMPAIGN_RESULT_SCHEMA
        or payload["scientific_evidence"] is not True
        or payload["science_executed"] is not True
        or payload["kernel_unit_test_only"] is not False
        or payload["contract_only"] is not False
        or payload["global_green_permitted"] is not False
        or manifest["schema"] != PRODUCTION_CAMPAIGN_MANIFEST_SCHEMA
        or manifest["status"] != "COMPLETE"
        or manifest["global_green_permitted"] is not False
        or manifest["campaign_result_identity"] != dict(result_artifact.origin_identity)
    ):
        raise Phase6PreparationError(
            "production finite-radius campaign policy/linkage changed"
        )
    state = payload["overall_state"]
    if state not in {"PARTIAL", "FAIL"} or payload["acceptance"] != state:
        raise Phase6PreparationError("production campaign state changed")
    coverage = _exact(
        payload["coverage"],
        {
            "D_prod_key_count",
            "D_prod_key_list_sha256",
            "exact_eight_state_mode_count",
            "frequency_count",
            "missing_eight_state_mode_count",
            "missing_eight_state_modes",
            "radial_state_record_count",
            "shard_count",
            "terminal_count",
        },
        "production campaign coverage",
    )
    if (
        coverage["D_prod_key_count"] != 16_048
        or coverage["D_prod_key_list_sha256"]
        != "54f13ea2473fb0a04ca5e16277edae31335c03b11753973d83a934cce2f0872b"
        or coverage["frequency_count"] != 40
        or coverage["shard_count"] != 80
        or coverage["terminal_count"] != 16_048
    ):
        raise Phase6PreparationError("production campaign D_prod coverage changed")
    qualification = _exact(
        payload["release_qualification"],
        {
            "finite_radius_outputs_are_observer_qualified",
            "full_paper_figure_rerun",
            "global_green_permitted",
            "independent_backend_difference_closed",
            "radial_state_evidence_only",
        },
        "production campaign qualification",
    )
    if qualification != {
        "finite_radius_outputs_are_observer_qualified": False,
        "full_paper_figure_rerun": False,
        "global_green_permitted": False,
        "independent_backend_difference_closed": False,
        "radial_state_evidence_only": True,
    }:
        raise Phase6PreparationError("production campaign observer scope was promoted")
    observables = payload["observable_statuses"]
    if not isinstance(observables, Mapping) or any(
        observables.get(name) not in {"NOT_ASSESSED", "PARTIAL"}
        for name in (
            "observer_qualified_tidal_response",
            "detector_response",
            "infinity_waveform",
            "convention_closure",
        )
    ):
        raise Phase6PreparationError("production campaign observer claim changed")
    keys = _campaign_domain_keys(projection, production=True)
    expected_items = len(keys)
    numerical = _production_campaign_budget(
        payload["numerical_budget"],
        fields=NUMERICAL_BUDGET_FIELDS,
        state=str(state),
        kind="numerical",
    )
    convention = _production_campaign_budget(
        payload["convention_budget"],
        fields=CONVENTION_BUDGET_FIELDS,
        state=str(state),
        kind="convention",
    )
    hashes: dict[str, object] = {}
    for field in (
        "implementation_source_sha256s",
        "campaign_implementation_source_sha256s",
    ):
        values = payload[field]
        if not isinstance(values, Mapping):
            raise Phase6PreparationError("production implementation hashes changed")
        for name, digest in values.items():
            qualified = f"{field}:{name}"
            if qualified in hashes:
                raise Phase6PreparationError("production implementation name collision")
            hashes[qualified] = digest
    implementation_hashes = _campaign_hashes(
        hashes,
        "production implementation hash",
    )
    mode_counts = _exact(
        payload["mode_state_counts"],
        {"PARTIAL", "FAIL"},
        "production campaign mode counts",
    )
    if (
        any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in mode_counts.values()
        )
        or sum(mode_counts.values()) != 16_048
        or (state == "FAIL") != (mode_counts["FAIL"] > 0)
    ):
        raise Phase6PreparationError("production campaign mode failures changed")
    return DerivedEvidence(
        evidence_id=evidence_id,
        adapter="PRODUCTION_FINITE_RADIUS_CAMPAIGN_V1",
        role="PRIMARY_SCIENCE",
        independence_class="SAME_IMPLEMENTATION",
        state=str(state),
        blocker=None,
        science_executed=True,
        implementation_hashes=implementation_hashes,
        expected_items=expected_items,
        assessed_item_ids=tuple(_item_id(key.to_record()) for key in keys),
        assessed_items=expected_items,
        coverage_family=f"production_finite_radius_campaign:{projection}",
        numerical_budget=numerical,
        convention_budget=convention,
        native_summary={
            "projection": projection,
            "native_overall_state": state,
            "native_mode_state_counts": dict(mode_counts),
            "coverage": dict(coverage),
            "observable_statuses": dict(observables),
            "release_qualification": dict(qualification),
        },
        native_domain=None,
        limitations=(
            "radial master-state/Q018-backend evidence only; observer, tetrad, and detector response are not assessed",
            f"native campaign fail-closed mode count={mode_counts['FAIL']}",
        ),
        method="strict 80-shard D_prod campaign reload and radial-only domain projection",
    )


def _v0_report(
    evidence_id: str, artifacts: Sequence[OriginArtifact]
) -> DerivedEvidence:
    report = _artifact_payload(artifacts, "verification.json")
    item = _exact(
        report,
        {
            "schema",
            "verification_id",
            "checks",
            "source_report_sha256s",
            "verification_state",
            "global_green_permitted",
            "li_figure_agreement_primary_gate",
        },
        "V0 verification report",
    )
    if (
        item["schema"] != V0_VERIFICATION_SCHEMA
        or item["global_green_permitted"] is not False
        or item["li_figure_agreement_primary_gate"] is not False
    ):
        raise Phase6PreparationError("V0 verification policy changed")
    _identifier(item["verification_id"], "V0 verification_id")
    checks = _exact(
        item["checks"],
        {
            "stale_production_metadata",
            "legacy_np_isolation",
            "legacy_pseudoinverse_isolation",
            "full_test_suite",
        },
        "V0 verification checks",
    )
    states: list[str] = []
    normalized_checks: dict[str, object] = {}
    for name, raw_check in checks.items():
        check = _exact(
            raw_check,
            {"state", "command", "passed", "failed", "skipped", "report_sha256"},
            f"V0 check {name}",
        )
        state = check["state"]
        if state not in {"PARTIAL", "PASS", "FAIL"}:
            raise Phase6PreparationError("V0 check state changed")
        for count_name in ("passed", "failed", "skipped"):
            count = check[count_name]
            if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                raise Phase6PreparationError("V0 check counts changed")
        _text(check["command"], "V0 verification command")
        _sha(check["report_sha256"], "V0 check report hash")
        if state == "PASS" and not (check["failed"] == 0 and check["passed"] > 0):
            raise Phase6PreparationError("V0 PASS check state/counts contradict")
        if check["failed"] > 0 and state != "FAIL":
            raise Phase6PreparationError("V0 check hides failed verification")
        if state == "FAIL" and check["failed"] == 0:
            raise Phase6PreparationError("V0 FAIL lacks failed checks")
        states.append(str(state))
        normalized_checks[str(name)] = dict(check)
    derived = (
        "FAIL"
        if "FAIL" in states
        else ("PASS" if all(state == "PASS" for state in states) else "PARTIAL")
    )
    if item["verification_state"] != derived:
        raise Phase6PreparationError("V0 verification state is not derived")
    report_hashes = item["source_report_sha256s"]
    expected_report_hashes = sorted(
        {str(check["report_sha256"]) for check in normalized_checks.values()}
    )
    if (
        not isinstance(report_hashes, list)
        or report_hashes != sorted(set(report_hashes))
        or not report_hashes
        or any(
            not isinstance(value, str) or not _SHA256.fullmatch(value)
            for value in report_hashes
        )
        or report_hashes != expected_report_hashes
    ):
        raise Phase6PreparationError("V0 source report identities changed")
    return DerivedEvidence(
        evidence_id=evidence_id,
        adapter="V0_IMPLEMENTATION_VERIFICATION_V1",
        role="IMPLEMENTATION_VERIFICATION",
        independence_class="NONE",
        state=derived,
        blocker=None,
        science_executed=False,
        implementation_hashes=(),
        expected_items=1,
        assessed_item_ids=("v0_verification",),
        assessed_items=1,
        coverage_family="v0_verification",
        numerical_budget={},
        convention_budget={},
        native_summary={
            "checks": normalized_checks,
            "source_report_sha256s": report_hashes,
        },
        native_domain=None,
        limitations=(
            () if derived == "PASS" else ("V0 verification is not fully passing",)
        ),
        method="machine-readable stale-metadata, legacy-isolation, and full-suite verification",
    )


def _derive_source(
    source: Mapping[str, object], artifacts: Sequence[OriginArtifact]
) -> DerivedEvidence:
    evidence_id = str(source["evidence_id"])
    adapter = str(source["adapter"])
    root = Path(str(source["origin_root"])).absolute()
    if adapter == "STAGE_A_MPMATH_V1":
        return _stage_a(evidence_id, artifacts)
    if adapter == "CONDITIONING_CAMPAIGN_V1":
        return _conditioning_campaign(evidence_id, artifacts, root, source["selector"])
    if adapter == "CONDITIONING_SHARD_V1":
        return _conditioning(evidence_id, artifacts, root)
    if adapter == "BHPT_MST_LEGACY_V1":
        return _legacy_mst(evidence_id, artifacts)
    if adapter == "BHPT_DIRECT_V1":
        return _bhpt_direct(evidence_id, artifacts, root)
    if adapter == "BHPT_DIRECT_COMPARISON_V1":
        return _bhpt_direct_comparison(evidence_id, artifacts, root)
    if adapter == "OBSERVABLE_FORMAL_ROOT_V1":
        return _observable(evidence_id, artifacts, source["selector"])
    if adapter == "TYPED_PHYSICAL_RESULT_V1":
        return _typed_physical(evidence_id, artifacts, production_finite_radius=False)
    if adapter == "PRODUCTION_FINITE_RADIUS_V1":
        return _typed_physical(evidence_id, artifacts, production_finite_radius=True)
    if adapter == "PRODUCTION_FINITE_RADIUS_CAMPAIGN_V1":
        return _production_finite_radius_campaign(
            evidence_id, artifacts, root, source["selector"]
        )
    if adapter == "V0_IMPLEMENTATION_VERIFICATION_V1":
        return _v0_report(evidence_id, artifacts)
    if adapter == "V1_AP_SELECTED_EVIDENCE_V1":
        return _v1_ap_selected_evidence(evidence_id, artifacts, root)
    if adapter == "V1_FINAL_RADIAL_BASELINE_V2":
        return _v1_final_radial_baseline_v2(
            evidence_id, artifacts, root, source["selector"]
        )
    if adapter == "V1_PRODUCTION_STATE_EVIDENCE_V1":
        return _v1_production_state_evidence(
            evidence_id, artifacts, root, source["selector"]
        )
    if adapter == "V1_RADIAL_SELECTED_ACCEPTANCE_V1":
        return _v1_radial_selected_acceptance(evidence_id, artifacts, root)
    raise Phase6PreparationError("unsupported adapter")


def _generated_v0(evidence_id: str) -> DerivedEvidence:
    return DerivedEvidence(
        evidence_id=evidence_id,
        adapter="PREPARATION_GENERATED_V0_OPEN_V1",
        role="IMPLEMENTATION_VERIFICATION",
        independence_class="NONE",
        state="PARTIAL",
        blocker=None,
        science_executed=False,
        implementation_hashes=(),
        expected_items=1,
        assessed_item_ids=(),
        assessed_items=0,
        coverage_family="v0_verification",
        numerical_budget={},
        convention_budget={},
        native_summary={
            "verification_state": "PARTIAL",
            "missing_required_external_report": V0_VERIFICATION_SCHEMA,
        },
        native_domain=None,
        limitations=(
            "no immutable final V0 stale-metadata/legacy-isolation/full-suite report was supplied",
        ),
        method="fail-closed V0 open-verification projection",
    )


def _generated_v6(evidence_id: str) -> DerivedEvidence:
    return DerivedEvidence(
        evidence_id=evidence_id,
        adapter="PREPARATION_GENERATED_V6_POLICY_V1",
        role="POLICY_VERIFICATION",
        independence_class="NONE",
        state="PASS",
        blocker=None,
        science_executed=False,
        implementation_hashes=(),
        expected_items=1,
        assessed_item_ids=("v6_release_policy",),
        assessed_items=1,
        coverage_family="v6_release_policy",
        numerical_budget={},
        convention_budget={},
        native_summary={
            "verification_state": "PASS",
            "verified_policy": POLICY,
            "bindings": [
                "domain_v3",
                "execution_v4",
                "aggregation_v8",
                "observable_v2",
            ],
        },
        native_domain=None,
        limitations=(),
        method="preparation and release validator policy verification",
    )


def _generated_blocker(evidence_id: str, expected_items: int) -> DerivedEvidence:
    blocker = {
        "code": "NO_TERMINAL_IMMUTABLE_EVIDENCE",
        "reason": "release map supplies no terminal immutable result for this observable/domain",
    }
    return DerivedEvidence(
        evidence_id=evidence_id,
        adapter="PREPARATION_GENERATED_BLOCKER_V1",
        role="BLOCKER",
        independence_class="NONE",
        state="NOT_ASSESSED",
        blocker=blocker,
        science_executed=False,
        implementation_hashes=(),
        expected_items=expected_items,
        assessed_item_ids=(),
        assessed_items=0,
        coverage_family=evidence_id,
        numerical_budget=_required_budget(NUMERICAL_BUDGET_FIELDS),
        convention_budget=_required_budget(CONVENTION_BUDGET_FIELDS),
        native_summary={"status": "NOT_ASSESSED", "blocker": blocker["code"]},
        native_domain=None,
        limitations=(blocker["reason"],),
        method="absence-of-terminal-evidence blocker; not a scientific result",
    )


def _plans_by_evidence(
    release_map: Mapping[str, object],
) -> dict[str, list[Mapping[str, object]]]:
    result: dict[str, list[Mapping[str, object]]] = {}
    for certificate in release_map["certificates"]:
        for evidence_id in certificate["evidence_ids"]:
            result.setdefault(str(evidence_id), []).append(certificate)
    return result


def _validate_derived_scope(
    derived: DerivedEvidence, certificate: Mapping[str, object]
) -> None:
    gate = str(certificate["gate"])
    observable = str(certificate["observable"])
    domain = certificate["parameter_domain"]
    if derived.expected_items != domain["expected_items"]:
        raise Phase6PreparationError(
            f"{derived.evidence_id} native coverage does not match certificate domain"
        )
    allowed: dict[str, set[str]] = {
        "STAGE_A_MPMATH_V1": {"V1"},
        "BHPT_MST_LEGACY_V1": {"V1"},
        "BHPT_DIRECT_V1": {"V1"},
        "BHPT_DIRECT_COMPARISON_V1": {"V1"},
        "CONDITIONING_CAMPAIGN_V1": {"V1", "V1Q"},
        "CONDITIONING_SHARD_V1": {"V1", "V1Q"},
        "OBSERVABLE_FORMAL_ROOT_V1": {gate},
        "TYPED_PHYSICAL_RESULT_V1": {gate},
        "PRODUCTION_FINITE_RADIUS_V1": {"V4"},
        "PRODUCTION_FINITE_RADIUS_CAMPAIGN_V1": {"V1", "V1Q"},
        "V0_IMPLEMENTATION_VERIFICATION_V1": {"V0"},
        "V1_AP_SELECTED_EVIDENCE_V1": {"V1"},
        "V1_FINAL_RADIAL_BASELINE_V2": {"V1", "V1Q"},
        "V1_PRODUCTION_STATE_EVIDENCE_V1": {"V1", "V1Q"},
        "V1_RADIAL_SELECTED_ACCEPTANCE_V1": {"V1"},
    }
    if gate not in allowed[derived.adapter]:
        raise Phase6PreparationError(
            f"adapter {derived.adapter} cannot support gate {gate}"
        )
    if derived.native_domain is not None:
        native = derived.native_domain
        if "gate" in native and native["gate"] != gate:
            raise Phase6PreparationError(
                f"{derived.evidence_id} native gate differs from release map"
            )
        if "observable" in native and native["observable"] != observable:
            raise Phase6PreparationError(
                f"{derived.evidence_id} native observable differs from release map"
            )
        for name in ("domain_id", "parameters", "selection_policy", "expected_items"):
            if native[name] != domain[name]:
                raise Phase6PreparationError(
                    f"{derived.evidence_id} native domain differs from release map"
                )
    if (
        derived.adapter == "PRODUCTION_FINITE_RADIUS_V1"
        and observable != "finite_radius_tidal_detector"
    ):
        raise Phase6PreparationError(
            "finite-radius campaign attached to wrong observable"
        )
    if (
        derived.adapter
        in {"BHPT_DIRECT_COMPARISON_V1", "V1_RADIAL_SELECTED_ACCEPTANCE_V1"}
        and observable != "radial_s_matrix_flux"
    ):
        raise Phase6PreparationError(
            "BHPT direct comparison attached to wrong observable"
        )
    if derived.adapter == "V1_FINAL_RADIAL_BASELINE_V2":
        expected_observable = {
            "V1": "radial_s_matrix_flux",
            "V1Q": "generic_conditioning_backend",
        }[gate]
        if observable != expected_observable:
            raise Phase6PreparationError(
                "final radial baseline attached to wrong observable"
            )
        if derived.native_summary.get("projection") != expected_observable:
            raise Phase6PreparationError(
                "final radial projection differs from its gate/observable"
            )
    if (
        derived.adapter == "V1_AP_SELECTED_EVIDENCE_V1"
        and observable != "radial_s_matrix_flux"
    ):
        raise Phase6PreparationError(
            "AP selected evidence attached to wrong observable"
        )
    if derived.adapter == "V1_PRODUCTION_STATE_EVIDENCE_V1":
        expected_observable = {
            "V1": "radial_s_matrix_flux",
            "V1Q": "generic_conditioning_backend",
        }[gate]
        if observable != expected_observable:
            raise Phase6PreparationError(
                "production state evidence attached to wrong observable"
            )
        if derived.native_summary.get("projection") != expected_observable:
            raise Phase6PreparationError(
                "production state projection differs from its gate/observable"
            )
    if derived.adapter in {
        "CONDITIONING_CAMPAIGN_V1",
        "PRODUCTION_FINITE_RADIUS_CAMPAIGN_V1",
    }:
        expected_observable = {
            "V1": "radial_s_matrix_flux",
            "V1Q": "generic_conditioning_backend",
        }[gate]
        if observable != expected_observable:
            raise Phase6PreparationError(
                "radial-only campaign attached to wrong observable"
            )
        if derived.native_summary.get("projection") != expected_observable:
            raise Phase6PreparationError(
                "campaign selector differs from its gate/observable"
            )


def prepare_release_map(value: object) -> PreparedPlan:
    """Validate a release map and every live source without writing anything."""

    release_map = _validate_map(value)
    # Check-only must validate the same exact v3/v4/v8/v2 predecessors that
    # publication will embed; a stale binding cannot wait until final release.
    authoritative_contract_bindings()
    sources: dict[str, tuple[DerivedEvidence, tuple[OriginArtifact, ...]]] = {}
    source_records = {str(item["evidence_id"]): item for item in release_map["sources"]}
    plans_by_evidence = _plans_by_evidence(release_map)
    native_signatures: dict[
        tuple[tuple[str, int], ...], tuple[str, str, Mapping[str, object]]
    ] = {}
    for evidence_id in sorted(source_records):
        source = source_records[evidence_id]
        artifacts = _load_origin(source)
        signature = tuple(
            sorted(
                (
                    str(artifact.origin_identity["sha256"]),
                    int(artifact.origin_identity["size"]),
                )
                for artifact in artifacts
            )
        )
        if signature in native_signatures:
            prior_id, prior_adapter, prior_selector = native_signatures[signature]
            selector_reuse_adapters = {
                "CONDITIONING_CAMPAIGN_V1",
                "OBSERVABLE_FORMAL_ROOT_V1",
                "PRODUCTION_FINITE_RADIUS_CAMPAIGN_V1",
                "V1_FINAL_RADIAL_BASELINE_V2",
                "V1_PRODUCTION_STATE_EVIDENCE_V1",
            }
            observable_reuse = (
                source["adapter"] in selector_reuse_adapters
                and prior_adapter == source["adapter"]
                and source["selector"] != prior_selector
            )
            if not observable_reuse:
                raise Phase6PreparationError(
                    f"duplicate native evidence bytes: {prior_id} and {evidence_id}"
                )
        else:
            native_signatures[signature] = (
                evidence_id,
                str(source["adapter"]),
                source["selector"],
            )
        derived = _derive_source(source, artifacts)
        for certificate in plans_by_evidence[evidence_id]:
            _validate_derived_scope(derived, certificate)
        sources[evidence_id] = (derived, artifacts)

    generated: dict[str, DerivedEvidence] = {}
    for certificate in release_map["certificates"]:
        gate = str(certificate["gate"])
        evidence_ids = certificate["evidence_ids"]
        cert_id = str(certificate["certificate_id"])
        expected_items = int(certificate["parameter_domain"]["expected_items"])
        if gate == "V0" and not evidence_ids:
            evidence_id = f"generated_v0_{cert_id}"
            generated[evidence_id] = _generated_v0(evidence_id)
        elif gate == "V6":
            evidence_id = f"generated_v6_{cert_id}"
            generated[evidence_id] = _generated_v6(evidence_id)
        elif not evidence_ids:
            evidence_id = f"blocker_{cert_id}"
            generated[evidence_id] = _generated_blocker(evidence_id, expected_items)
    if set(sources) & set(generated):
        raise Phase6PreparationError("generated/source evidence id collision")
    return PreparedPlan(release_map=release_map, sources=sources, generated=generated)


def preflight_release_map(value: object) -> dict[str, object]:
    """Return deterministic source/certificate states without creating a root."""

    plan = prepare_release_map(value)
    evidence = {evidence_id: item[0] for evidence_id, item in plan.sources.items()}
    evidence.update(plan.generated)
    certificate_states = _preview_certificate_states(plan, evidence)
    return {
        "preparation_id": plan.release_map["preparation_id"],
        "release_id": plan.release_map["release_id"],
        "source_evidence_count": len(plan.sources),
        "generated_support_count": len(plan.generated),
        "certificate_count": len(plan.release_map["certificates"]),
        "evidence_state_counts": {
            state: sum(item.state == state for item in evidence.values())
            for state in STATES
        },
        "certificate_state_counts": {
            state: list(certificate_states.values()).count(state) for state in STATES
        },
        "certificate_states": certificate_states,
        "global_status": None,
        "output_written": False,
    }


def _scope(certificate: Mapping[str, object]) -> dict[str, str]:
    return {
        "gate": str(certificate["gate"]),
        "observable": str(certificate["observable"]),
        "domain_id": str(certificate["parameter_domain"]["domain_id"]),
    }


def _certificate_evidence_ids(
    plan: PreparedPlan, certificate: Mapping[str, object]
) -> list[str]:
    ids = [str(value) for value in certificate["evidence_ids"]]
    cert_id = str(certificate["certificate_id"])
    gate = str(certificate["gate"])
    if gate == "V0" and not ids:
        ids.append(f"generated_v0_{cert_id}")
    elif gate == "V6":
        ids.append(f"generated_v6_{cert_id}")
    elif not ids:
        ids.append(f"blocker_{cert_id}")
    return sorted(ids)


def _coverage(outputs: Sequence[DerivedEvidence], expected_items: int) -> int:
    driving = [output for output in outputs if output.role not in {"BLOCKER"}]
    if not driving:
        return 0
    families: dict[str, list[DerivedEvidence]] = {}
    for output in driving:
        families.setdefault(output.coverage_family, []).append(output)
    family_sets: list[set[str] | None] = []
    family_counts: list[int] = []
    for records in families.values():
        item_sets = [set(record.assessed_item_ids) for record in records]
        if all(item_sets):
            union = set().union(*item_sets)
            family_sets.append(union)
            family_counts.append(len(union))
        else:
            family_sets.append(None)
            family_counts.append(sum(record.assessed_items for record in records))
    if len(family_counts) == 1:
        return min(expected_items, family_counts[0])
    if all(item_set is not None for item_set in family_sets):
        intersection = set.intersection(
            *(item_set for item_set in family_sets if item_set is not None)
        )
        return min(expected_items, len(intersection))
    return min(expected_items, min(family_counts))


def _combined_budget(
    outputs: Sequence[DerivedEvidence],
    *,
    fields: Sequence[str],
    kind: str,
) -> dict[str, Mapping[str, object]]:
    result: dict[str, Mapping[str, object]] = {}
    for name in fields:
        records: list[tuple[DerivedEvidence, Mapping[str, object]]] = []
        for output in outputs:
            if output.role == "BLOCKER":
                continue
            budget = (
                output.numerical_budget
                if kind == "numerical"
                else output.convention_budget
            )
            if name in budget:
                record = budget[name]
                if record["state"] == "PASS" and output.state != "PASS":
                    record = {
                        **record,
                        "state": "PARTIAL",
                        "reason": (
                            f"{record['reason']}; component PASS capped because its "
                            f"release evidence state is {output.state}"
                        ),
                    }
                records.append((output, record))
        if not records:
            result[name] = {
                "state": "NOT_ASSESSED",
                "estimate": None,
                "units": "dimensionless",
                "reason": "no cited result quantifies this component",
                "evidence_ids": [],
            }
            continue
        states = [str(record["state"]) for _, record in records]
        state = _worst(states)
        selected = [
            (output, record) for output, record in records if record["state"] == state
        ]
        estimates = [
            Decimal(str(record["estimate"]))
            for _, record in selected
            if record["estimate"] is not None
        ]
        units = {str(record["units"]) for _, record in selected}
        if state in {"PASS", "FAIL"} and not estimates:
            estimates = [Decimal(1)]
        result[name] = {
            "state": state,
            "estimate": format(max(estimates), "f") if estimates else None,
            "units": next(iter(units)) if len(units) == 1 else "mixed",
            "reason": "; ".join(
                sorted({str(record["reason"]) for _, record in selected})
            ),
            "evidence_ids": sorted(
                output.evidence_id for output, _ in selected if state != "NOT_ASSESSED"
            ),
        }
    return result


def _derive_certificate_state(
    outputs: Sequence[DerivedEvidence],
    *,
    gate: str,
    coverage_complete: bool,
    numerical: Mapping[str, Mapping[str, object]],
    convention: Mapping[str, Mapping[str, object]],
) -> str:
    states = [output.state for output in outputs if output.role != "BLOCKER"]
    if "FAIL" in states:
        return "FAIL"
    if not states:
        return "NOT_ASSESSED"
    if gate in {"V0", "V6"}:
        return (
            "PASS"
            if states and all(state == "PASS" for state in states) and coverage_complete
            else "PARTIAL"
        )
    roles = {output.role for output in outputs}
    budget_states = [
        str(record["state"])
        for budget in (numerical, convention)
        for record in budget.values()
    ]
    primary_hashes = {
        digest
        for output in outputs
        if output.role == "PRIMARY_SCIENCE"
        for digest in output.implementation_hashes
    }
    independent_hashes = {
        digest
        for output in outputs
        if output.role == "INDEPENDENT_SCIENCE"
        for digest in output.implementation_hashes
    }
    if (
        coverage_complete
        and states
        and all(state == "PASS" for state in states)
        and all(state == "PASS" for state in budget_states)
        and {"PRIMARY_SCIENCE", "INDEPENDENT_SCIENCE"} <= roles
        and not primary_hashes & independent_hashes
    ):
        return "PASS"
    return "PARTIAL"


def _preview_certificate_states(
    plan: PreparedPlan, evidence: Mapping[str, DerivedEvidence]
) -> dict[str, str]:
    states: dict[str, str] = {}
    for certificate in plan.release_map["certificates"]:
        outputs = [
            evidence[evidence_id]
            for evidence_id in _certificate_evidence_ids(plan, certificate)
        ]
        expected = int(certificate["parameter_domain"]["expected_items"])
        assessed = _coverage(outputs, expected)
        numerical = _combined_budget(
            outputs, fields=NUMERICAL_BUDGET_FIELDS, kind="numerical"
        )
        convention = _combined_budget(
            outputs, fields=CONVENTION_BUDGET_FIELDS, kind="convention"
        )
        states[str(certificate["certificate_id"])] = _derive_certificate_state(
            outputs,
            gate=str(certificate["gate"]),
            coverage_complete=assessed == expected,
            numerical=numerical,
            convention=convention,
        )
    return states


def _assessment_for_release(record: Mapping[str, object]) -> dict[str, object]:
    state = str(record["state"])
    return {
        "applicability": "REQUIRED",
        "state": state,
        "estimate": record["estimate"],
        "units": record["units"],
        "reason": record["reason"],
        "evidence_ids": record["evidence_ids"],
    }


def _na_budget(fields: Sequence[str]) -> dict[str, object]:
    return {
        name: {
            "applicability": "NOT_APPLICABLE",
            "state": "NOT_ASSESSED",
            "estimate": None,
            "units": None,
            "reason": "physical uncertainty component is not applicable to this policy gate",
            "evidence_ids": [],
        }
        for name in fields
    }


def _build_certificate(
    plan: PreparedPlan,
    certificate: Mapping[str, object],
    evidence: Mapping[str, DerivedEvidence],
) -> dict[str, object]:
    evidence_ids = _certificate_evidence_ids(plan, certificate)
    outputs = [evidence[evidence_id] for evidence_id in evidence_ids]
    expected = int(certificate["parameter_domain"]["expected_items"])
    assessed = _coverage(outputs, expected)
    numerical = _combined_budget(
        outputs, fields=NUMERICAL_BUDGET_FIELDS, kind="numerical"
    )
    convention = _combined_budget(
        outputs, fields=CONVENTION_BUDGET_FIELDS, kind="convention"
    )
    gate = str(certificate["gate"])
    state = _derive_certificate_state(
        outputs,
        gate=gate,
        coverage_complete=assessed == expected,
        numerical=numerical,
        convention=convention,
    )
    blockers = {
        tuple(sorted(output.blocker.items()))
        for output in outputs
        if output.blocker is not None
    }
    if state == "NOT_ASSESSED" and len(blockers) != 1:
        raise Phase6PreparationError("NOT_ASSESSED certificate needs one exact blocker")
    blocker = dict(next(iter(blockers))) if state == "NOT_ASSESSED" else None
    limitations = sorted(
        {limitation for output in outputs for limitation in output.limitations}
        | (
            {f"coverage incomplete: {assessed}/{expected} assessed"}
            if assessed != expected
            else set()
        )
    )
    domain = certificate["parameter_domain"]
    return {
        "schema": CERTIFICATE_SCHEMA,
        "certificate_id": certificate["certificate_id"],
        "gate": gate,
        "observable": certificate["observable"],
        "parameter_domain": {
            "domain_id": domain["domain_id"],
            "description": domain["description"],
            "parameters": domain["parameters"],
            "selection_policy": domain["selection_policy"],
            "coverage": {
                "expected_items": expected,
                "assessed_items": assessed,
                "complete": assessed == expected,
            },
        },
        "state": state,
        "reason": "state is derived from typed native evidence, exact coverage, and separate uncertainty budgets",
        "primary_acceptance_gate": certificate["primary_acceptance_gate"],
        "evidence_ids": evidence_ids,
        "numerical_uncertainty_budget": (
            _na_budget(NUMERICAL_BUDGET_FIELDS)
            if gate in {"V0", "V6"}
            else {
                name: _assessment_for_release(record)
                for name, record in numerical.items()
            }
        ),
        "convention_uncertainty_budget": (
            _na_budget(CONVENTION_BUDGET_FIELDS)
            if gate in {"V0", "V6"}
            else {
                name: _assessment_for_release(record)
                for name, record in convention.items()
            }
        ),
        "limitations": limitations,
        "blocker": blocker,
    }


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _new_directory(path: Path, mode: int = 0o700) -> None:
    os.mkdir(path, mode)
    _fsync_directory(path.parent)


def _publish_file(path: Path, data: bytes) -> None:
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
    if path.read_bytes() != data:
        raise Phase6PreparationError("published preparation bytes changed")


def _seal_directory(path: Path) -> None:
    os.chmod(path, 0o555)
    _fsync_directory(path)
    _fsync_directory(path.parent)


def _seal_tree(root: Path) -> None:
    if not root.exists() or root.is_symlink():
        return
    for path in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if path.is_symlink():
            continue
        if path.is_file():
            os.chmod(path, 0o444)
        elif path.is_dir():
            os.chmod(path, 0o555)
    os.chmod(root, 0o555)
    _fsync_directory(root.parent)


def _new_root(path: Path) -> Path:
    root = path.absolute()
    if any(component.is_symlink() for component in (root.parent, *root.parent.parents)):
        raise Phase6PreparationError("preparation output parent contains a symlink")
    try:
        normalized = root.parent.resolve(strict=True) / root.name
    except OSError as exc:
        raise Phase6PreparationError(
            "preparation output parent is unavailable"
        ) from exc
    if root != normalized or root.exists() or root.is_symlink():
        raise Phase6PreparationError("refusing to overwrite/alias preparation root")
    _new_directory(root)
    return root


def _projection_payload(
    derived: DerivedEvidence,
    *,
    scopes: Sequence[Mapping[str, str]],
    snapshots: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    return {
        "schema": NORMALIZED_RESULT_SCHEMA,
        "evidence_id": derived.evidence_id,
        "adapter": derived.adapter,
        "release_evidence_state": derived.state,
        "role": derived.role,
        "independence_class": derived.independence_class,
        "scientific_evidence": derived.role
        in {"PRIMARY_SCIENCE", "INDEPENDENT_SCIENCE"},
        "science_executed": derived.science_executed,
        "kernel_unit_test_only": False,
        "verification_evidence": derived.role
        in {"IMPLEMENTATION_VERIFICATION", "POLICY_VERIFICATION"},
        "policy_verification": derived.role == "POLICY_VERIFICATION",
        "verification_state": derived.state,
        "failure": (
            {"reason": "; ".join(derived.limitations)}
            if derived.role == "FAILURE_DIAGNOSTIC"
            else None
        ),
        "blocker": derived.blocker,
        "implementation_source_sha256s": list(derived.implementation_hashes),
        "coverage": {
            "expected_items": derived.expected_items,
            "assessed_items": derived.assessed_items,
            "assessed_item_ids": list(derived.assessed_item_ids),
            "complete": derived.assessed_items == derived.expected_items,
            "coverage_family": derived.coverage_family,
        },
        "numerical_uncertainty_budget": derived.numerical_budget,
        "convention_uncertainty_budget": derived.convention_budget,
        "native_summary": derived.native_summary,
        "native_domain": derived.native_domain,
        "limitations": list(derived.limitations),
        "scopes": list(scopes),
        "source_snapshots": list(snapshots),
        "normalization_is_new_science": False,
        "publisher_generated_science": False,
        "global_green_permitted": False,
        "paper_agreement_primary_gate": False,
        "li_figure_agreement_primary_gate": False,
        "full_paper_figure_rerun": False,
    }


def _envelope_payload(
    derived: DerivedEvidence,
    *,
    scopes: Sequence[Mapping[str, str]],
    projection_identity: Mapping[str, object],
    snapshot_identities: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    artifacts: list[dict[str, object]] = [
        {
            "artifact_role": "RESULT",
            "expected_schema": NORMALIZED_RESULT_SCHEMA,
            "identity": dict(projection_identity),
            "media_type": "application/json",
        }
    ]
    artifacts.extend(
        {
            "artifact_role": "SOURCE_SNAPSHOT",
            "expected_schema": None,
            "identity": dict(identity),
            "media_type": "application/octet-stream",
        }
        for identity in snapshot_identities
    )
    artifacts.sort(key=lambda item: str(item["identity"]["path"]))
    return {
        "schema": EVIDENCE_ENVELOPE_SCHEMA,
        "evidence_id": derived.evidence_id,
        "role": derived.role,
        "independence_class": derived.independence_class,
        "declared_state": derived.state,
        "scientific_evidence": derived.role
        in {"PRIMARY_SCIENCE", "INDEPENDENT_SCIENCE"},
        "science_executed": derived.science_executed,
        "kernel_unit_test_only": False,
        "blocker": derived.blocker,
        "implementation_source_sha256s": list(derived.implementation_hashes),
        "scopes": list(scopes),
        "source_artifacts": artifacts,
        "producer": "Phase-6 V1 strict release preparation",
        "method": derived.method,
        "global_green_permitted": False,
        "li_figure_agreement_primary_gate": False,
        "full_paper_figure_rerun": False,
    }


def publish_preparation(value: object, output_root: str | Path) -> dict[str, object]:
    """Publish one fresh immutable preparation root from a validated map."""

    plan = prepare_release_map(value)
    root = _new_root(Path(output_root))
    try:
        for name in ("sources", "normalized", "envelopes"):
            _new_directory(root / name)
        evidence: dict[str, DerivedEvidence] = {
            evidence_id: record[0] for evidence_id, record in plan.sources.items()
        }
        evidence.update(plan.generated)
        plans_by_evidence = _plans_by_evidence(plan.release_map)
        generated_plans: dict[str, list[Mapping[str, object]]] = {}
        for certificate in plan.release_map["certificates"]:
            for evidence_id in _certificate_evidence_ids(plan, certificate):
                if evidence_id in plan.generated:
                    generated_plans.setdefault(evidence_id, []).append(certificate)
        plans_by_evidence.update(generated_plans)

        snapshot_inventory: dict[str, list[dict[str, object]]] = {}
        projection_inventory: dict[str, dict[str, object]] = {}
        envelope_inventory: dict[str, dict[str, object]] = {}
        for evidence_id in sorted(evidence):
            derived = evidence[evidence_id]
            source_dir = root / "sources" / evidence_id
            normalized_dir = root / "normalized" / evidence_id
            envelope_dir = root / "envelopes" / evidence_id
            _new_directory(source_dir)
            _new_directory(normalized_dir)
            _new_directory(envelope_dir)
            origin_artifacts = plan.sources.get(evidence_id, (derived, ()))[1]
            snapshot_records: list[dict[str, object]] = []
            for artifact in origin_artifacts:
                snapshot_path = source_dir / artifact.relative_path
                _publish_file(snapshot_path, artifact.raw)
            _seal_directory(source_dir)
            snapshot_identities = [
                direct_file_identity(source_dir / artifact.relative_path)
                for artifact in origin_artifacts
            ]
            for artifact, identity in zip(
                origin_artifacts, snapshot_identities, strict=True
            ):
                if identity["sha256"] != artifact.origin_identity["sha256"]:
                    raise Phase6PreparationError(
                        "snapshot bytes differ from native origin"
                    )
                snapshot_records.append(
                    {
                        "relative_path": artifact.relative_path,
                        "origin_identity": dict(artifact.origin_identity),
                        "snapshot_identity": dict(identity),
                        "copy_sha256_equal": True,
                    }
                )
            snapshot_inventory[evidence_id] = [
                dict(identity) for identity in snapshot_identities
            ]
            scopes = sorted(
                (_scope(certificate) for certificate in plans_by_evidence[evidence_id]),
                key=lambda item: (item["gate"], item["observable"], item["domain_id"]),
            )
            projection = _projection_payload(
                derived, scopes=scopes, snapshots=snapshot_records
            )
            projection_path = normalized_dir / "result.json"
            _publish_file(projection_path, canonical_json_bytes(projection))
            _seal_directory(normalized_dir)
            projection_identity = direct_file_identity(projection_path)
            projection_inventory[evidence_id] = dict(projection_identity)
            envelope = _envelope_payload(
                derived,
                scopes=scopes,
                projection_identity=projection_identity,
                snapshot_identities=snapshot_identities,
            )
            envelope_path = envelope_dir / "evidence.json"
            _publish_file(envelope_path, canonical_json_bytes(envelope))
            _seal_directory(envelope_dir)
            envelope_inventory[evidence_id] = direct_file_identity(envelope_path)
        for directory in (root / "sources", root / "normalized", root / "envelopes"):
            _seal_directory(directory)

        certificates = [
            _build_certificate(plan, certificate, evidence)
            for certificate in plan.release_map["certificates"]
        ]
        certificates.sort(key=lambda item: str(item["certificate_id"]))
        submission = {
            "schema": SUBMISSION_SCHEMA,
            "release_id": plan.release_map["release_id"],
            "contract_bindings": authoritative_contract_bindings(),
            "evidence_envelope_identities": [
                envelope_inventory[evidence_id]
                for evidence_id in sorted(envelope_inventory)
            ],
            "certificates": certificates,
            "policy": dict(POLICY),
        }
        validate_submission(submission)
        _publish_file(root / "release_map.json", canonical_json_bytes(plan.release_map))
        _publish_file(
            root / "canonical_submission.json", canonical_json_bytes(submission)
        )
        # The manifest is intentionally the final write.  Its identities become
        # direct-file identities after the root is sealed.
        manifest = {
            "schema": PREPARATION_MANIFEST_SCHEMA,
            "preparation_id": plan.release_map["preparation_id"],
            "release_id": plan.release_map["release_id"],
            "release_map_sha256": sha256_bytes(canonical_json_bytes(plan.release_map)),
            "canonical_submission_sha256": sha256_bytes(
                canonical_json_bytes(submission)
            ),
            "evidence_envelope_identities": {
                evidence_id: envelope_inventory[evidence_id]
                for evidence_id in sorted(envelope_inventory)
            },
            "normalized_result_identities": {
                evidence_id: projection_inventory[evidence_id]
                for evidence_id in sorted(projection_inventory)
            },
            "source_snapshot_identities": {
                evidence_id: snapshot_inventory[evidence_id]
                for evidence_id in sorted(snapshot_inventory)
            },
            "certificate_count": len(certificates),
            "certificate_state_counts": {
                state: sum(
                    certificate["state"] == state for certificate in certificates
                )
                for state in STATES
            },
            "global_status": None,
            "global_green_permitted": False,
            "li_figure_agreement_primary_gate": False,
            "full_paper_figure_rerun_performed": False,
            "publisher_generated_science": False,
        }
        _publish_file(root / "manifest.json", canonical_json_bytes(manifest))
        _seal_tree(root)
        return validate_published_preparation(root)
    except BaseException:
        _seal_tree(root)
        raise


def _canonical_object(path: Path) -> Mapping[str, object]:
    raw = path.read_bytes()
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise Phase6PreparationError(f"published artifact is not JSON: {path}") from exc
    if not isinstance(payload, Mapping) or raw != canonical_json_bytes(payload):
        raise Phase6PreparationError(
            f"published artifact is not canonical JSON: {path}"
        )
    return payload


def validate_published_preparation(root: str | Path) -> dict[str, object]:
    """Reload an immutable preparation root and all release-facing identities."""

    path = Path(root).absolute()
    if any(component.is_symlink() for component in (path, *path.parents)):
        raise Phase6PreparationError("published preparation contains a symlink")
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise Phase6PreparationError("published preparation is unavailable") from exc
    expected_top = {
        "sources",
        "normalized",
        "envelopes",
        "release_map.json",
        "canonical_submission.json",
        "manifest.json",
    }
    if (
        resolved != path
        or stat.S_IMODE(path.lstat().st_mode) != 0o555
        or {child.name for child in path.iterdir()} != expected_top
    ):
        raise Phase6PreparationError("published preparation layout/mode changed")
    for child in path.rglob("*"):
        info = child.lstat()
        if child.is_symlink():
            raise Phase6PreparationError("published preparation contains an alias")
        if child.is_dir() and stat.S_IMODE(info.st_mode) != 0o555:
            raise Phase6PreparationError("published preparation directory is mutable")
        if child.is_file() and (
            stat.S_IMODE(info.st_mode) != 0o444 or info.st_nlink != 1
        ):
            raise Phase6PreparationError(
                "published preparation file is mutable/aliased"
            )
    release_map = _canonical_object(path / "release_map.json")
    _validate_map(release_map)
    submission = _canonical_object(path / "canonical_submission.json")
    inventory, certificates = validate_submission(submission)
    manifest = _canonical_object(path / "manifest.json")
    fields = {
        "schema",
        "preparation_id",
        "release_id",
        "release_map_sha256",
        "canonical_submission_sha256",
        "evidence_envelope_identities",
        "normalized_result_identities",
        "source_snapshot_identities",
        "certificate_count",
        "certificate_state_counts",
        "global_status",
        "global_green_permitted",
        "li_figure_agreement_primary_gate",
        "full_paper_figure_rerun_performed",
        "publisher_generated_science",
    }
    if set(manifest) != fields or manifest["schema"] != PREPARATION_MANIFEST_SCHEMA:
        raise Phase6PreparationError("preparation manifest schema changed")
    states = Counter(str(certificate["state"]) for certificate in certificates)
    if (
        manifest["preparation_id"] != release_map["preparation_id"]
        or manifest["release_id"] != release_map["release_id"]
        or manifest["release_id"] != submission["release_id"]
        or manifest["release_map_sha256"]
        != sha256_bytes((path / "release_map.json").read_bytes())
        or manifest["canonical_submission_sha256"]
        != sha256_bytes((path / "canonical_submission.json").read_bytes())
        or manifest["certificate_count"] != len(certificates)
        or manifest["certificate_state_counts"]
        != {state: states[state] for state in STATES}
        or manifest["global_status"] is not None
        or manifest["global_green_permitted"] is not False
        or manifest["li_figure_agreement_primary_gate"] is not False
        or manifest["full_paper_figure_rerun_performed"] is not False
        or manifest["publisher_generated_science"] is not False
    ):
        raise Phase6PreparationError("preparation manifest is not derived")
    expected_envelopes = {
        evidence_id: record["identity"] for evidence_id, record in inventory.items()
    }
    if manifest["evidence_envelope_identities"] != expected_envelopes:
        raise Phase6PreparationError("preparation envelope inventory changed")
    normalized = manifest["normalized_result_identities"]
    snapshots = manifest["source_snapshot_identities"]
    if set(normalized) != set(inventory) or set(snapshots) != set(inventory):
        raise Phase6PreparationError("preparation source/projection inventory changed")
    expected_evidence_ids = set(inventory)
    for directory_name in ("sources", "normalized", "envelopes"):
        actual_evidence_ids = {
            child.name for child in (path / directory_name).iterdir()
        }
        if actual_evidence_ids != expected_evidence_ids:
            raise Phase6PreparationError(
                f"preparation {directory_name} directory inventory changed"
            )
    for evidence_id in sorted(inventory):
        if {child.name for child in (path / "normalized" / evidence_id).iterdir()} != {
            "result.json"
        }:
            raise Phase6PreparationError("normalized projection layout changed")
        if {child.name for child in (path / "envelopes" / evidence_id).iterdir()} != {
            "evidence.json"
        }:
            raise Phase6PreparationError("evidence envelope layout changed")
        projection_identity = direct_file_identity(
            path / "normalized" / evidence_id / "result.json"
        )
        if normalized[evidence_id] != projection_identity:
            raise Phase6PreparationError("normalized projection identity changed")
        projection = _canonical_object(Path(str(projection_identity["path"])))
        if (
            projection.get("schema") != NORMALIZED_RESULT_SCHEMA
            or projection.get("evidence_id") != evidence_id
            or projection.get("normalization_is_new_science") is not False
            or projection.get("publisher_generated_science") is not False
        ):
            raise Phase6PreparationError("normalized projection claims changed")
        actual_snapshots = [
            direct_file_identity(child)
            for child in sorted((path / "sources" / evidence_id).iterdir())
        ]
        if snapshots[evidence_id] != actual_snapshots:
            raise Phase6PreparationError("source snapshot inventory changed")
        projection_snapshots = projection.get("source_snapshots")
        if (
            not isinstance(projection_snapshots, list)
            or [item["snapshot_identity"] for item in projection_snapshots]
            != actual_snapshots
        ):
            raise Phase6PreparationError("projection/source snapshot linkage changed")
        for record in projection_snapshots:
            if (
                record.get("copy_sha256_equal") is not True
                or record["origin_identity"]["sha256"]
                != record["snapshot_identity"]["sha256"]
            ):
                raise Phase6PreparationError("native bytes were not copied exactly")
    return {
        "preparation_id": manifest["preparation_id"],
        "release_id": manifest["release_id"],
        "evidence_root": str(path),
        "canonical_submission": str(path / "canonical_submission.json"),
        "canonical_submission_sha256": manifest["canonical_submission_sha256"],
        "evidence_envelope_count": len(inventory),
        "certificate_count": len(certificates),
        "certificate_state_counts": manifest["certificate_state_counts"],
        "global_status": None,
    }


__all__ = [
    "ADAPTERS",
    "BHPT_DIRECT_COMPARISON_MANIFEST_SCHEMA",
    "BHPT_DIRECT_COMPARISON_SCHEMA",
    "CONDITIONING_CAMPAIGN_INDEX_SCHEMA",
    "CONDITIONING_CAMPAIGN_MANIFEST_SCHEMA",
    "NORMALIZED_RESULT_SCHEMA",
    "PREPARATION_MANIFEST_SCHEMA",
    "PRODUCTION_CAMPAIGN_MANIFEST_SCHEMA",
    "PRODUCTION_CAMPAIGN_RESULT_SCHEMA",
    "PRODUCTION_FINITE_RADIUS_RESULT_SCHEMA",
    "Phase6PreparationError",
    "RELEASE_MAP_SCHEMA",
    "TYPED_PHYSICAL_RESULT_SCHEMA",
    "V0_VERIFICATION_SCHEMA",
    "prepare_release_map",
    "preflight_release_map",
    "publish_preparation",
    "validate_published_preparation",
]
