"""Fail-closed populated observable evidence for Phase-6 gates V2--V5.

The zero-science observable contract freezes the vocabulary only.  This
module validates later, populated releases without treating a unit test, a
contract fixture, or Li-figure agreement as scientific acceptance evidence.

The validator is intentionally structural.  It verifies exact domains,
immutable artifact identities, provenance, a-priori threshold records, and
state derivation.  It does not independently recompute a scientific metric.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal, InvalidOperation
from pathlib import Path
import hashlib
import json
import re
import stat

from schwgw.validation.phase6_domain import canonical_json_bytes
from schwgw.validation.phase6_observable_contract import (
    SCHEMA as ZERO_CONTRACT_SCHEMA,
    validate_payload as validate_zero_contract,
)


BUNDLE_SCHEMA = "schwgw_phase6_populated_observable_evidence_v1"
CERTIFICATE_SCHEMA = "schwgw_phase6_observable_domain_certificate_v1"
DOMAIN_SCHEMA = "schwgw_phase6_observable_parameter_domain_v1"
SUBMISSION_SCHEMA = "schwgw_phase6_observable_evidence_submission_v1"
MANIFEST_SCHEMA = "schwgw_phase6_observable_evidence_manifest_v1"
THRESHOLD_SCHEMA = "schwgw_phase6_observable_threshold_policy_v1"

STATES = ("NOT_ASSESSED", "PARTIAL", "PASS", "FAIL")
COMPARISONS = ("LE", "LT", "GE", "GT", "EQ")
APPLICABILITY = ("REQUIRED", "NOT_APPLICABLE")
EVIDENCE_ROLES = (
    "PRIMARY_SCIENCE",
    "INDEPENDENT_SCIENCE",
    "CONVENTION_DEFINITION",
    "THRESHOLD_POLICY",
    "SECONDARY_PAPER_REGRESSION",
    "SOFTWARE_TEST_ONLY",
    "CONTRACT_ONLY",
)
INDEPENDENCE_CLASSES = (
    "SAME_IMPLEMENTATION",
    "ALGORITHMICALLY_INDEPENDENT",
    "EXTERNAL_SOURCE",
    "NONE",
)
MEDIA_TYPES = (
    "application/json",
    "application/x-jsonlines",
    "application/octet-stream",
)
PRECISION_KINDS = (
    "BINARY_FLOAT",
    "ARBITRARY_PRECISION",
    "EXACT_SYMBOLIC",
    "NOT_APPLICABLE",
)

OBSERVABLE_GATES = {
    "master_to_strain_flux": "V2",
    "metric_psi4_external_crosscheck": "V2",
    "spin2_scattering_limits": "V3",
    "finite_radius_tidal_detector": "V4",
    "complex_lensing_matrix": "V5",
}
REQUIRED_CHECKS = {
    "master_to_strain_flux": {
        "master_strain_waveform": False,
        "infinity_flux": False,
        "horizon_flux": False,
        "radial_flux_consistency": True,
    },
    "metric_psi4_external_crosscheck": {
        "master_vs_metric": False,
        "master_vs_psi4": False,
        "master_vs_external": True,
    },
    "spin2_scattering_limits": {
        "low_frequency_differential": True,
        "low_frequency_absorption": True,
        "high_frequency_absorption": True,
        "backward_glory": True,
        "helicity_parity": False,
        "series_lmax_convergence": False,
    },
    "finite_radius_tidal_detector": {
        "static_observer_response": False,
        "freefall_observer_response": False,
        "pure_gauge_response_invariance": True,
        "tetrad_transport": False,
    },
    "complex_lensing_matrix": {
        "two_incident_basis_rank": False,
        "basis_rotation_covariance": True,
        "phase_convention_frozen": False,
        "matrix_diagnostics": False,
    },
}
NUMERICAL_BUDGETS = (
    "r_in",
    "r_out",
    "jost_order",
    "ode_tolerance",
    "arithmetic_precision",
    "backend_difference",
    "lmax_tail",
    "axis_limit",
)
CONVENTION_BUDGETS = (
    "observer",
    "worldline",
    "tetrad",
    "polarization_basis",
    "phase_origin",
    "total_scattered_definition",
)
MINIMUM_CONVENTION_BUDGETS = {
    observable: frozenset(CONVENTION_BUDGETS) for observable in OBSERVABLE_GATES
}
MINIMUM_CONVENTION_BUDGETS["spin2_scattering_limits"] = frozenset(
    {"polarization_basis", "phase_origin", "total_scattered_definition"}
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ZERO_CONTRACT_ROOT = PROJECT_ROOT / "runs/phase6/v1_observable_contract_v2_20260806"
ZERO_CONTRACT_PATH = ZERO_CONTRACT_ROOT / "observable_contract.json"
ZERO_CONTRACT_SHA256 = (
    "3853df8fbc245b81552198d99201778e4020d82f618e3f80ac745768fc3d104b"
)

_ID = re.compile(r"[a-z0-9][a-z0-9_.-]{0,63}")
_FORBIDDEN_SCOPE = re.compile(r"(?:^|[_\s-])(global|project|schwo)(?:$|[_\s-])", re.I)


class ObservableEvidenceError(ValueError):
    """Raised for stale, ambiguous, incomplete, or contradictory evidence."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _exact(value: object, fields: set[str], label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != fields:
        raise ObservableEvidenceError(f"{label} schema changed")
    return value


def _required_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ObservableEvidenceError(f"{label} must be non-empty text")
    return value


def _validate_json_value(value: object, label: str) -> None:
    """Require unambiguous JSON values; physical decimals stay strings."""

    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int) and not isinstance(value, bool):
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_value(item, f"{label}[{index}]")
        return
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) or not key for key in value):
            raise ObservableEvidenceError(f"{label} has a non-text/empty key")
        for key, item in value.items():
            _validate_json_value(item, f"{label}.{key}")
        return
    raise ObservableEvidenceError(f"{label} contains a float or unsupported JSON value")


def _canonical_decimal(
    value: object, label: str, *, nonnegative: bool = False
) -> Decimal:
    if (
        not isinstance(value, str)
        or not value
        or "e" in value.lower()
        or value.startswith("+")
    ):
        raise ObservableEvidenceError(
            f"{label} must be a canonical finite decimal string"
        )
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ObservableEvidenceError(f"{label} is not decimal") from exc
    if not result.is_finite() or format(result, "f") != value:
        raise ObservableEvidenceError(
            f"{label} must be a canonical finite decimal string"
        )
    if nonnegative and result < 0:
        raise ObservableEvidenceError(f"{label} must be nonnegative")
    return result


def direct_file_identity(
    path: str | Path,
    *,
    require_immutable: bool = True,
    require_immutable_parent: bool = True,
) -> dict[str, object]:
    """Return a live identity while rejecting symlink and hardlink aliases."""

    absolute = Path(path).absolute()
    if any(item.is_symlink() for item in (absolute, *absolute.parents)):
        raise ObservableEvidenceError("evidence path contains a symlink component")
    try:
        resolved = absolute.resolve(strict=True)
        info = absolute.lstat()
    except OSError as exc:
        raise ObservableEvidenceError(
            f"cannot identify evidence file: {absolute}"
        ) from exc
    if resolved != absolute or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ObservableEvidenceError("evidence must be a direct regular nlink1 file")
    mode = stat.S_IMODE(info.st_mode)
    if require_immutable and mode != 0o444:
        raise ObservableEvidenceError("evidence file must be mode 0444")
    parent_info = absolute.parent.lstat()
    if require_immutable_parent and (
        absolute.parent.is_symlink() or stat.S_IMODE(parent_info.st_mode) != 0o555
    ):
        raise ObservableEvidenceError("evidence parent must be a direct mode 0555 root")
    return {
        "mode": mode,
        "nlink": info.st_nlink,
        "path": str(absolute),
        "sha256": sha256_bytes(absolute.read_bytes()),
        "size": info.st_size,
    }


def _identity(
    value: object,
    label: str,
    *,
    immutable: bool = True,
    immutable_parent: bool = True,
) -> Mapping[str, object]:
    identity = _exact(value, {"mode", "nlink", "path", "sha256", "size"}, label)
    if (
        not isinstance(identity["path"], str)
        or not isinstance(identity["sha256"], str)
        or isinstance(identity["size"], bool)
        or not isinstance(identity["size"], int)
        or not isinstance(identity["mode"], int)
        or not isinstance(identity["nlink"], int)
    ):
        raise ObservableEvidenceError(f"{label} identity types changed")
    actual = direct_file_identity(
        str(identity["path"]),
        require_immutable=immutable,
        require_immutable_parent=immutable_parent,
    )
    if dict(identity) != actual:
        raise ObservableEvidenceError(f"{label} identity no longer matches live bytes")
    return identity


def _load_canonical_json(
    identity: object, label: str, *, schema: str
) -> Mapping[str, object]:
    checked = _identity(identity, label)
    raw = Path(str(checked["path"])).read_bytes()
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ObservableEvidenceError(f"{label} is not JSON") from exc
    if (
        not isinstance(payload, Mapping)
        or canonical_json_bytes(payload) != raw
        or payload.get("schema", payload.get("schema_version")) != schema
    ):
        raise ObservableEvidenceError(f"{label} is not canonical expected-schema JSON")
    return payload


def _load_canonical_jsonl(
    identity: object, label: str
) -> tuple[Mapping[str, object], ...]:
    checked = _identity(identity, label)
    raw = Path(str(checked["path"])).read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise ObservableEvidenceError(f"{label} lacks final LF")
    records: list[Mapping[str, object]] = []
    lines = raw.splitlines(keepends=True)
    for line in lines:
        try:
            record = json.loads(line)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ObservableEvidenceError(f"{label} is not JSONL") from exc
        if (
            not isinstance(record, Mapping)
            or not record
            or canonical_json_bytes(record) != line
        ):
            raise ObservableEvidenceError(f"{label} has a noncanonical/empty record")
        _validate_json_value(record, f"{label} record")
        records.append(record)
    canonical_lines = [canonical_json_bytes(record) for record in records]
    if canonical_lines != sorted(canonical_lines) or len(set(canonical_lines)) != len(
        canonical_lines
    ):
        raise ObservableEvidenceError(f"{label} is not canonical ordered unique JSONL")
    return tuple(records)


def _validate_identity_list(value: object, label: str, *, nonempty: bool) -> None:
    if not isinstance(value, list) or (nonempty and not value):
        raise ObservableEvidenceError(f"{label} identity list is invalid")
    seen: set[tuple[str, str]] = set()
    for index, identity in enumerate(value):
        checked = _identity(identity, f"{label}[{index}]")
        key = (str(checked["path"]), str(checked["sha256"]))
        if key in seen:
            raise ObservableEvidenceError(f"{label} contains a duplicate identity")
        seen.add(key)


def _validate_provenance(value: object, label: str, *, science: bool) -> None:
    fields = {
        "producer",
        "producer_version",
        "method",
        "run_id",
        "actual_arithmetic",
        "source_snapshot_identities",
        "config_identities",
        "input_identities",
    }
    item = _exact(value, fields, f"{label} provenance")
    for name in ("producer", "producer_version", "method", "run_id"):
        _required_text(item[name], f"{label} provenance {name}")
    arithmetic = _exact(
        item["actual_arithmetic"],
        {"backend", "precision_kind", "decimal_digits"},
        f"{label} arithmetic",
    )
    _required_text(arithmetic["backend"], f"{label} arithmetic backend")
    kind = arithmetic["precision_kind"]
    digits = arithmetic["decimal_digits"]
    if kind not in PRECISION_KINDS:
        raise ObservableEvidenceError(f"{label} precision kind changed")
    if kind in {"EXACT_SYMBOLIC", "NOT_APPLICABLE"}:
        if digits is not None:
            raise ObservableEvidenceError(
                f"{label} nonnumeric arithmetic must not claim digits"
            )
    elif isinstance(digits, bool) or not isinstance(digits, int) or digits < 1:
        raise ObservableEvidenceError(f"{label} actual decimal digits are invalid")
    if science and kind == "NOT_APPLICABLE":
        raise ObservableEvidenceError(
            f"{label} science evidence lacks actual arithmetic"
        )
    _validate_identity_list(
        item["source_snapshot_identities"],
        f"{label} source snapshots",
        nonempty=True,
    )
    _validate_identity_list(
        item["config_identities"], f"{label} configs", nonempty=False
    )
    _validate_identity_list(
        item["input_identities"], f"{label} inputs", nonempty=science
    )


def _contract_only_payload(payload: Mapping[str, object]) -> bool:
    return bool(
        payload.get("contract_only") is True
        or payload.get("no_observable_pass_claimed") is True
        or (
            payload.get("solver_runs") == 0
            and payload.get("scientific_pass_claimed") is False
        )
    )


def _validate_threshold_policy(payload: Mapping[str, object], evidence_id: str) -> None:
    item = _exact(
        payload,
        {
            "schema",
            "frozen_before_measurement",
            "global_green_permitted",
            "paper_agreement_primary_gate",
            "thresholds",
        },
        f"threshold policy {evidence_id}",
    )
    if (
        item["schema"] != THRESHOLD_SCHEMA
        or item["frozen_before_measurement"] is not True
        or item["global_green_permitted"] is not False
        or item["paper_agreement_primary_gate"] is not False
    ):
        raise ObservableEvidenceError(f"threshold policy {evidence_id} policy changed")
    thresholds = item["thresholds"]
    if not isinstance(thresholds, Mapping) or not thresholds:
        raise ObservableEvidenceError(f"threshold policy {evidence_id} is empty")
    for metric, threshold in thresholds.items():
        if not isinstance(metric, str) or not _ID.fullmatch(metric):
            raise ObservableEvidenceError(
                f"threshold policy {evidence_id} metric id changed"
            )
        record = _exact(
            threshold,
            {"comparison", "units", "value"},
            f"threshold policy {evidence_id} metric {metric}",
        )
        if record["comparison"] not in COMPARISONS:
            raise ObservableEvidenceError(
                f"threshold policy {evidence_id} comparison changed"
            )
        _required_text(record["units"], f"threshold policy {evidence_id} units")
        _canonical_decimal(
            record["value"],
            f"threshold policy {evidence_id} value",
            nonnegative=True,
        )


def _validate_evidence_descriptor(
    value: object, evidence_id: str
) -> Mapping[str, object]:
    fields = {
        "identity",
        "media_type",
        "expected_schema",
        "role",
        "independence_class",
        "provenance",
    }
    item = _exact(value, fields, f"evidence {evidence_id}")
    role = item["role"]
    independence = item["independence_class"]
    media_type = item["media_type"]
    if role not in EVIDENCE_ROLES or independence not in INDEPENDENCE_CLASSES:
        raise ObservableEvidenceError(
            f"evidence {evidence_id} role/independence changed"
        )
    if media_type not in MEDIA_TYPES:
        raise ObservableEvidenceError(f"evidence {evidence_id} media type changed")
    science = role in {"PRIMARY_SCIENCE", "INDEPENDENT_SCIENCE"}
    if role == "PRIMARY_SCIENCE" and independence != "SAME_IMPLEMENTATION":
        raise ObservableEvidenceError(
            f"evidence {evidence_id} primary independence is contradictory"
        )
    if role == "INDEPENDENT_SCIENCE" and independence not in {
        "ALGORITHMICALLY_INDEPENDENT",
        "EXTERNAL_SOURCE",
    }:
        raise ObservableEvidenceError(
            f"evidence {evidence_id} is not independently generated"
        )
    if (
        role not in {"PRIMARY_SCIENCE", "INDEPENDENT_SCIENCE"}
        and independence != "NONE"
    ):
        raise ObservableEvidenceError(
            f"evidence {evidence_id} support role claims independence"
        )
    _validate_provenance(item["provenance"], f"evidence {evidence_id}", science=science)
    checked = _identity(item["identity"], f"evidence {evidence_id} artifact")
    expected_schema = item["expected_schema"]
    if media_type == "application/json":
        schema = _required_text(
            expected_schema, f"evidence {evidence_id} expected schema"
        )
        payload = _load_canonical_json(
            checked, f"evidence {evidence_id} artifact", schema=schema
        )
        if science:
            if (
                _contract_only_payload(payload)
                or payload.get("scientific_evidence") is not True
                or payload.get("kernel_unit_test_only") is not False
                or payload.get("global_green_permitted") is not False
                or payload.get("paper_agreement_primary_gate") is not False
            ):
                raise ObservableEvidenceError(
                    f"evidence {evidence_id} contract/unit/paper artifact cannot be science evidence"
                )
        elif role == "THRESHOLD_POLICY":
            if schema != THRESHOLD_SCHEMA:
                raise ObservableEvidenceError(
                    f"evidence {evidence_id} threshold schema changed"
                )
            _validate_threshold_policy(payload, evidence_id)
        elif (
            role == "SOFTWARE_TEST_ONLY"
            and payload.get("kernel_unit_test_only") is not True
        ):
            raise ObservableEvidenceError(
                f"evidence {evidence_id} software-test role is not declared"
            )
        elif role == "CONTRACT_ONLY" and not _contract_only_payload(payload):
            raise ObservableEvidenceError(
                f"evidence {evidence_id} contract-only role is not declared"
            )
        elif (
            role == "SECONDARY_PAPER_REGRESSION"
            and payload.get("paper_agreement_primary_gate") is not False
        ):
            raise ObservableEvidenceError(
                f"evidence {evidence_id} paper evidence lacks secondary policy"
            )
    elif science:
        raise ObservableEvidenceError(
            f"evidence {evidence_id} science evidence requires a JSON envelope"
        )
    elif expected_schema is not None:
        raise ObservableEvidenceError(
            f"evidence {evidence_id} non-JSON schema must be null"
        )
    return item


def _source_signature(descriptor: Mapping[str, object]) -> tuple[str, ...]:
    provenance = descriptor["provenance"]
    return tuple(
        sorted(
            str(identity["sha256"])
            for identity in provenance["source_snapshot_identities"]
        )
    )


def _validate_independence_inventory(
    inventory: Mapping[str, Mapping[str, object]],
) -> None:
    primary = {
        _source_signature(descriptor)
        for descriptor in inventory.values()
        if descriptor["role"] == "PRIMARY_SCIENCE"
    }
    independent = {
        _source_signature(descriptor)
        for descriptor in inventory.values()
        if descriptor["role"] == "INDEPENDENT_SCIENCE"
    }
    if primary & independent:
        raise ObservableEvidenceError(
            "independent science evidence duplicates a primary source signature"
        )


def _validate_domain_binding(
    inventory: Mapping[str, Mapping[str, object]],
    domain_identity: Mapping[str, object],
) -> None:
    for evidence_id, descriptor in inventory.items():
        if descriptor["role"] not in {"PRIMARY_SCIENCE", "INDEPENDENT_SCIENCE"}:
            continue
        inputs = descriptor["provenance"]["input_identities"]
        if not any(dict(identity) == dict(domain_identity) for identity in inputs):
            raise ObservableEvidenceError(
                f"science evidence {evidence_id} is not bound to the certificate domain"
            )


def _validate_domain(
    identity: object, *, observable: str, gate: str
) -> Mapping[str, object]:
    domain = _load_canonical_json(identity, "parameter domain", schema=DOMAIN_SCHEMA)
    fields = {
        "schema",
        "domain_id",
        "observable",
        "acceptance_gate",
        "parameters",
        "selection_policy",
        "item_index_identity",
        "assessed_item_index_identity",
        "coverage",
    }
    domain = _exact(domain, fields, "parameter domain")
    domain_id = _required_text(domain["domain_id"], "domain id")
    if _FORBIDDEN_SCOPE.search(domain_id):
        raise ObservableEvidenceError("parameter domain cannot be global/project-wide")
    if domain["observable"] != observable or domain["acceptance_gate"] != gate:
        raise ObservableEvidenceError("parameter domain observable/gate mismatch")
    if not isinstance(domain["parameters"], Mapping) or not domain["parameters"]:
        raise ObservableEvidenceError("parameter domain must have explicit parameters")
    _validate_json_value(domain["parameters"], "parameter domain parameters")
    _required_text(domain["selection_policy"], "parameter domain selection policy")
    expected = _load_canonical_jsonl(domain["item_index_identity"], "domain item index")
    assessed = _load_canonical_jsonl(
        domain["assessed_item_index_identity"], "assessed domain item index"
    )
    expected_lines = [canonical_json_bytes(record) for record in expected]
    assessed_lines = [canonical_json_bytes(record) for record in assessed]
    assessed_set = set(assessed_lines)
    if not expected or not assessed_set <= set(expected_lines):
        raise ObservableEvidenceError(
            "assessed domain items are not an exact expected subset"
        )
    if [line for line in expected_lines if line in assessed_set] != assessed_lines:
        raise ObservableEvidenceError("assessed domain subset order changed")
    coverage = _exact(
        domain["coverage"],
        {"expected_items", "assessed_items", "complete"},
        "domain coverage",
    )
    expected_count, assessed_count = (
        coverage["expected_items"],
        coverage["assessed_items"],
    )
    if (
        isinstance(expected_count, bool)
        or not isinstance(expected_count, int)
        or isinstance(assessed_count, bool)
        or not isinstance(assessed_count, int)
        or expected_count != len(expected)
        or assessed_count != len(assessed)
        or coverage["complete"] is not (assessed_count == expected_count)
    ):
        raise ObservableEvidenceError(
            "domain coverage is not derived from exact indexes"
        )
    return domain


def _comparison(measured: Decimal, threshold: Decimal, comparison: str) -> bool:
    return {
        "LE": measured <= threshold,
        "LT": measured < threshold,
        "GE": measured >= threshold,
        "GT": measured > threshold,
        "EQ": measured == threshold,
    }[comparison]


def _evidence_roles(
    ids: Sequence[str], inventory: Mapping[str, Mapping[str, object]]
) -> set[str]:
    return {str(inventory[evidence_id]["role"]) for evidence_id in ids}


def _validate_assessment(
    value: object,
    *,
    label: str,
    inventory: Mapping[str, Mapping[str, object]],
    independence_required: bool | None,
    science_required: bool,
) -> Mapping[str, object]:
    fields = {
        "state",
        "reason",
        "coverage",
        "metric",
        "measured_value",
        "threshold_value",
        "comparison",
        "units",
        "evidence_ids",
    }
    if independence_required is not None:
        fields.add("independence_required")
    item = _exact(value, fields, label)
    state = item["state"]
    if state not in STATES:
        raise ObservableEvidenceError(f"{label} state changed")
    _required_text(item["reason"], f"{label} reason")
    if (
        independence_required is not None
        and item["independence_required"] is not independence_required
    ):
        raise ObservableEvidenceError(f"{label} independence policy changed")
    evidence_ids = item["evidence_ids"]
    if (
        not isinstance(evidence_ids, list)
        or any(
            not isinstance(item_id, str) or item_id not in inventory
            for item_id in evidence_ids
        )
        or len(evidence_ids) != len(set(evidence_ids))
    ):
        raise ObservableEvidenceError(f"{label} evidence references are invalid")
    if state == "NOT_ASSESSED":
        if (
            item["coverage"] != "NONE"
            or any(
                item[name] is not None
                for name in (
                    "metric",
                    "measured_value",
                    "threshold_value",
                    "comparison",
                    "units",
                )
            )
            or evidence_ids
        ):
            raise ObservableEvidenceError(f"{label} NOT_ASSESSED must carry no result")
        return item
    if item["coverage"] not in {"INCOMPLETE", "COMPLETE"}:
        raise ObservableEvidenceError(f"{label} assessed coverage changed")
    metric = _required_text(item["metric"], f"{label} metric")
    del metric
    _required_text(item["units"], f"{label} units")
    measured = _canonical_decimal(
        item["measured_value"], f"{label} measured value", nonnegative=True
    )
    if not evidence_ids:
        raise ObservableEvidenceError(f"{label} assessed result lacks evidence")
    roles = _evidence_roles(evidence_ids, inventory)
    science_roles = {"PRIMARY_SCIENCE", "INDEPENDENT_SCIENCE"}
    if science_required and not roles & science_roles:
        raise ObservableEvidenceError(
            f"{label} is supported only by non-science evidence"
        )
    threshold_value = item["threshold_value"]
    comparison = item["comparison"]
    threshold_ids = [
        evidence_id
        for evidence_id in evidence_ids
        if inventory[evidence_id]["role"] == "THRESHOLD_POLICY"
    ]
    if threshold_value is None or comparison is None:
        if (
            threshold_ids
            or threshold_value is not None
            or comparison is not None
            or state != "PARTIAL"
            or item["coverage"] != "INCOMPLETE"
        ):
            raise ObservableEvidenceError(
                f"{label} incomplete threshold/state is contradictory"
            )
        return item
    threshold = _canonical_decimal(
        threshold_value, f"{label} threshold", nonnegative=True
    )
    if comparison not in COMPARISONS:
        raise ObservableEvidenceError(f"{label} comparison changed")
    if len(threshold_ids) != 1:
        raise ObservableEvidenceError(
            f"{label} threshold lacks one immutable policy evidence"
        )
    policy = _load_canonical_json(
        inventory[threshold_ids[0]]["identity"],
        f"{label} threshold policy",
        schema=THRESHOLD_SCHEMA,
    )
    thresholds = policy["thresholds"]
    if item["metric"] not in thresholds or thresholds[item["metric"]] != {
        "comparison": comparison,
        "units": item["units"],
        "value": threshold_value,
    }:
        raise ObservableEvidenceError(
            f"{label} threshold is not bound to its policy artifact"
        )
    passed = _comparison(measured, threshold, str(comparison))
    if not passed:
        expected_state = "FAIL"
    elif item["coverage"] == "COMPLETE":
        expected_state = "PASS"
    else:
        expected_state = "PARTIAL"
    if state != expected_state:
        raise ObservableEvidenceError(f"{label} state contradicts metric/coverage")
    if (
        independence_required
        and state == "PASS"
        and not {
            "PRIMARY_SCIENCE",
            "INDEPENDENT_SCIENCE",
        }
        <= roles
    ):
        raise ObservableEvidenceError(
            f"{label} PASS lacks primary/independent science evidence"
        )
    return item


def _validate_budget_map(
    value: object,
    *,
    names: Sequence[str],
    minimum_required: frozenset[str],
    label: str,
    inventory: Mapping[str, Mapping[str, object]],
) -> Mapping[str, Mapping[str, object]]:
    if not isinstance(value, Mapping) or set(value) != set(names):
        raise ObservableEvidenceError(f"{label} inventory changed")
    result: dict[str, Mapping[str, object]] = {}
    for name in names:
        record = _exact(value[name], {"applicability", "assessment"}, f"{label} {name}")
        applicability = record["applicability"]
        if applicability not in APPLICABILITY:
            raise ObservableEvidenceError(f"{label} {name} applicability changed")
        if name in minimum_required and applicability != "REQUIRED":
            raise ObservableEvidenceError(
                f"{label} {name} cannot be marked not applicable"
            )
        assessment = _validate_assessment(
            record["assessment"],
            label=f"{label} {name}",
            inventory=inventory,
            independence_required=None,
            science_required=applicability == "REQUIRED",
        )
        if applicability == "NOT_APPLICABLE" and assessment["state"] != "NOT_ASSESSED":
            raise ObservableEvidenceError(
                f"{label} {name} N/A component claims a result"
            )
        result[name] = record
    return result


def _required_states(records: Mapping[str, Mapping[str, object]]) -> list[str]:
    return [
        str(record["assessment"]["state"])
        for record in records.values()
        if record["applicability"] == "REQUIRED"
    ]


def _derive_certificate_state(
    *,
    domain_complete: bool,
    assessed_items: int,
    checks: Mapping[str, Mapping[str, object]],
    numerical: Mapping[str, Mapping[str, object]],
    convention: Mapping[str, Mapping[str, object]],
    has_primary: bool,
    has_independent: bool,
) -> str:
    states = [str(item["state"]) for item in checks.values()]
    states.extend(_required_states(numerical))
    states.extend(_required_states(convention))
    if "FAIL" in states:
        return "FAIL"
    if (
        domain_complete
        and states
        and all(state == "PASS" for state in states)
        and has_primary
        and has_independent
    ):
        return "PASS"
    if assessed_items > 0 or any(state in {"PARTIAL", "PASS"} for state in states):
        return "PARTIAL"
    return "NOT_ASSESSED"


def certificate_id(
    observable: str, gate: str, domain: Mapping[str, object], domain_sha256: str
) -> str:
    payload = {
        "acceptance_gate": gate,
        "domain_id": domain["domain_id"],
        "domain_sha256": domain_sha256,
        "observable": observable,
    }
    return f"{observable}:{sha256_bytes(canonical_json_bytes(payload))[:20]}"


def validate_certificate(value: object) -> Mapping[str, object]:
    fields = {
        "schema",
        "certificate_id",
        "observable",
        "acceptance_gate",
        "parameter_domain_identity",
        "evidence_inventory",
        "acceptance_checks",
        "numerical_budget",
        "convention_budget",
        "secondary_evidence_ids",
        "limitations",
        "li_figure_agreement_primary_gate",
        "global_green_permitted",
        "state",
    }
    item = _exact(value, fields, "observable certificate")
    observable = item["observable"]
    gate = item["acceptance_gate"]
    if item["schema"] != CERTIFICATE_SCHEMA or observable not in OBSERVABLE_GATES:
        raise ObservableEvidenceError("observable certificate schema/name changed")
    if gate != OBSERVABLE_GATES[observable]:
        raise ObservableEvidenceError("observable acceptance gate changed")
    if (
        item["global_green_permitted"] is not False
        or item["li_figure_agreement_primary_gate"] is not False
    ):
        raise ObservableEvidenceError("global or Li-primary acceptance is forbidden")
    domain_identity = _identity(
        item["parameter_domain_identity"], "parameter domain identity"
    )
    domain = _validate_domain(
        domain_identity, observable=str(observable), gate=str(gate)
    )
    expected_id = certificate_id(
        str(observable), str(gate), domain, str(domain_identity["sha256"])
    )
    if item["certificate_id"] != expected_id:
        raise ObservableEvidenceError(
            "certificate id is not derived from observable/domain"
        )
    raw_inventory = item["evidence_inventory"]
    if not isinstance(raw_inventory, Mapping) or not raw_inventory:
        raise ObservableEvidenceError("certificate evidence inventory is empty")
    inventory: dict[str, Mapping[str, object]] = {}
    for evidence_id, descriptor in raw_inventory.items():
        if not isinstance(evidence_id, str) or not _ID.fullmatch(evidence_id):
            raise ObservableEvidenceError("evidence id is not canonical")
        inventory[evidence_id] = _validate_evidence_descriptor(descriptor, evidence_id)
    _validate_independence_inventory(inventory)
    _validate_domain_binding(inventory, domain_identity)
    expected_checks = REQUIRED_CHECKS[str(observable)]
    checks_value = item["acceptance_checks"]
    if not isinstance(checks_value, Mapping) or set(checks_value) != set(
        expected_checks
    ):
        raise ObservableEvidenceError("observable acceptance-check inventory changed")
    checks = {
        name: _validate_assessment(
            checks_value[name],
            label=f"acceptance check {name}",
            inventory=inventory,
            independence_required=independence_required,
            science_required=True,
        )
        for name, independence_required in expected_checks.items()
    }
    numerical = _validate_budget_map(
        item["numerical_budget"],
        names=NUMERICAL_BUDGETS,
        minimum_required=frozenset(NUMERICAL_BUDGETS),
        label="numerical budget",
        inventory=inventory,
    )
    convention = _validate_budget_map(
        item["convention_budget"],
        names=CONVENTION_BUDGETS,
        minimum_required=MINIMUM_CONVENTION_BUDGETS[str(observable)],
        label="convention budget",
        inventory=inventory,
    )
    secondary = item["secondary_evidence_ids"]
    if (
        not isinstance(secondary, list)
        or len(secondary) != len(set(secondary))
        or any(evidence_id not in inventory for evidence_id in secondary)
    ):
        raise ObservableEvidenceError("secondary evidence references are invalid")
    allowed_secondary = {
        "SECONDARY_PAPER_REGRESSION",
        "SOFTWARE_TEST_ONLY",
        "CONTRACT_ONLY",
    }
    if any(
        inventory[evidence_id]["role"] not in allowed_secondary
        for evidence_id in secondary
    ):
        raise ObservableEvidenceError(
            "science evidence cannot be hidden as secondary evidence"
        )
    used: set[str] = set(secondary)
    for assessment in checks.values():
        used.update(assessment["evidence_ids"])
    for budget in (numerical, convention):
        for record in budget.values():
            used.update(record["assessment"]["evidence_ids"])
    if used != set(inventory):
        raise ObservableEvidenceError(
            "evidence inventory contains unreferenced artifacts"
        )
    if any(
        inventory[evidence_id]["role"] in allowed_secondary
        for assessment in checks.values()
        for evidence_id in assessment["evidence_ids"]
    ):
        raise ObservableEvidenceError(
            "secondary-only evidence cannot enter an acceptance check"
        )
    limitations = item["limitations"]
    if not isinstance(limitations, list) or any(
        not isinstance(text, str) or not text.strip() for text in limitations
    ):
        raise ObservableEvidenceError("certificate limitations are invalid")
    science_roles = {
        str(descriptor["role"])
        for descriptor in inventory.values()
        if descriptor["role"] in {"PRIMARY_SCIENCE", "INDEPENDENT_SCIENCE"}
    }
    coverage = domain["coverage"]
    derived = _derive_certificate_state(
        domain_complete=bool(coverage["complete"]),
        assessed_items=int(coverage["assessed_items"]),
        checks=checks,
        numerical=numerical,
        convention=convention,
        has_primary="PRIMARY_SCIENCE" in science_roles,
        has_independent="INDEPENDENT_SCIENCE" in science_roles,
    )
    if item["state"] != derived:
        raise ObservableEvidenceError(
            "certificate state is not derived from checks/domain/budgets"
        )
    if derived in {"PARTIAL", "PASS", "FAIL"} and not science_roles:
        raise ObservableEvidenceError("assessed certificate lacks science evidence")
    return item


def _certificate_index(
    certificates: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for certificate in certificates:
        identity = certificate["parameter_domain_identity"]
        result.append(
            {
                "acceptance_gate": certificate["acceptance_gate"],
                "certificate_id": certificate["certificate_id"],
                "domain_sha256": identity["sha256"],
                "observable": certificate["observable"],
                "state": certificate["state"],
            }
        )
    return result


def predecessor_contract_identity() -> dict[str, object]:
    identity = direct_file_identity(ZERO_CONTRACT_PATH)
    if identity["sha256"] != ZERO_CONTRACT_SHA256:
        raise ObservableEvidenceError("zero-science observable predecessor hash drift")
    payload = _load_canonical_json(
        identity, "zero-science predecessor", schema=ZERO_CONTRACT_SCHEMA
    )
    validate_zero_contract(payload)
    return identity


def build_bundle(certificates: Sequence[Mapping[str, object]]) -> dict[str, object]:
    validated = [validate_certificate(certificate) for certificate in certificates]
    if not validated or all(
        certificate["state"] == "NOT_ASSESSED" for certificate in validated
    ):
        raise ObservableEvidenceError(
            "populated bundle requires at least one assessed certificate"
        )
    order = [
        (
            str(certificate["acceptance_gate"]),
            str(certificate["observable"]),
            str(certificate["certificate_id"]),
        )
        for certificate in validated
    ]
    if order != sorted(order) or len(set(order)) != len(order):
        raise ObservableEvidenceError("certificates are not canonical ordered unique")
    index = _certificate_index(validated)
    state_counts = {
        state: sum(certificate["state"] == state for certificate in validated)
        for state in STATES
    }
    return {
        "schema": BUNDLE_SCHEMA,
        "release_scope": "PER_OBSERVABLE_PER_EXPLICIT_PARAMETER_DOMAIN",
        "contract_only": False,
        "global_green_permitted": False,
        "li_figure_agreement_primary_gate": False,
        "predecessor_contract_identity": predecessor_contract_identity(),
        "certificates": list(validated),
        "certificate_count": len(validated),
        "certificate_index_sha256": sha256_bytes(canonical_json_bytes(index)),
        "state_counts": state_counts,
        "scientific_pass_claimed": state_counts["PASS"] > 0,
    }


def validate_bundle(value: object) -> Mapping[str, object]:
    fields = {
        "schema",
        "release_scope",
        "contract_only",
        "global_green_permitted",
        "li_figure_agreement_primary_gate",
        "predecessor_contract_identity",
        "certificates",
        "certificate_count",
        "certificate_index_sha256",
        "state_counts",
        "scientific_pass_claimed",
    }
    item = _exact(value, fields, "observable evidence bundle")
    if (
        item["schema"] != BUNDLE_SCHEMA
        or item["release_scope"] != "PER_OBSERVABLE_PER_EXPLICIT_PARAMETER_DOMAIN"
        or item["contract_only"] is not False
        or item["global_green_permitted"] is not False
        or item["li_figure_agreement_primary_gate"] is not False
    ):
        raise ObservableEvidenceError("observable bundle release policy changed")
    if item["predecessor_contract_identity"] != predecessor_contract_identity():
        raise ObservableEvidenceError("observable bundle predecessor identity changed")
    certificates = item["certificates"]
    if not isinstance(certificates, list):
        raise ObservableEvidenceError("observable certificates are not a list")
    rebuilt = build_bundle(certificates)
    for name in (
        "certificate_count",
        "certificate_index_sha256",
        "state_counts",
        "scientific_pass_claimed",
    ):
        if item[name] != rebuilt[name]:
            raise ObservableEvidenceError(f"observable bundle {name} is not derived")
    return item


def validate_submission(value: object) -> tuple[Mapping[str, object], ...]:
    item = _exact(value, {"schema", "certificates"}, "observable evidence submission")
    if item["schema"] != SUBMISSION_SCHEMA or not isinstance(
        item["certificates"], list
    ):
        raise ObservableEvidenceError("observable evidence submission schema changed")
    return tuple(
        validate_certificate(certificate) for certificate in item["certificates"]
    )
