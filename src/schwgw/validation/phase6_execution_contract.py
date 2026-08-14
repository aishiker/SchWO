"""Generic Phase-6 V1 calibration and shard/resume execution contract.

This is a data-contract module only: it derives bounded calibration key sets,
partitions an already frozen radial domain, and validates provenance required
for a future resumable execution.  It never imports or invokes a solver.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal, ROUND_FLOOR, localcontext
import json
import math
from pathlib import Path

import numpy as np

from schwgw.validation.phase6_domain import (
    DomainBundle,
    DomainContractError,
    RadialKey,
    canonical_json_bytes,
    jsonl_bytes,
    sha256_bytes,
    source_file_identity,
    validate_ordered_unique_keys,
)


EXECUTION_SCHEMA = "schwgw_phase6_v1_execution_contract_v1"
TRANSITION_CALIBRATION_SCHEMA = "schwgw_phase6_conditioning_transition_calibration_v1"
EXTERNAL_DIRECT_CALIBRATION_SCHEMA = "schwgw_phase6_external_direct_calibration_v1"
SHARD_SCHEMA = "schwgw_phase6_v1_shard_inventory_v1"
CHECKPOINT_SCHEMA = "schwgw_phase6_v1_key_checkpoint_v1"
KEY_RESULT_SCHEMA = "schwgw_phase6_v1_key_result_v1"
KEY_PAYLOAD_ENVELOPE_SCHEMA = "schwgw_phase6_v1_key_payload_envelope_v1"
SHARD_CHECKPOINT_SCHEMA = "schwgw_phase6_v1_shard_checkpoint_v1"
SHARD_RESULT_SCHEMA = "schwgw_phase6_v1_shard_result_v1"
ACCEPTANCE_STATES = ("NOT_ASSESSED", "PARTIAL", "PASS", "FAIL")
NUMERICAL_BUDGET_FIELDS = (
    "lmax",
    "r_in",
    "r_out",
    "jost_order",
    "ode_tolerance",
    "arithmetic_precision",
    "axis_limit",
    "backend_difference",
)
CONVENTION_BUDGET_FIELDS = (
    "observer",
    "tetrad",
    "polarization_basis",
    "phase_origin",
    "total_scattered_definition",
)
TRANSITION_KM = ("0.1", "0.5", "1", "2", "3", "4")
GENERIC_REFERENCE_RADIUS_M = Decimal("40")
EXTERNAL_DIRECT_SPEC: dict[str, tuple[int, ...]] = {
    "0.5": (2,),
    "1": (20, 39, 40, 41),
    "2": (60, 79, 80, 81, 153),
    "4": (120, 159, 160, 161, 360),
}
EXPECTED_TRANSITION_KEY_LIST_SHA256 = (
    "942fce669ee62f8194859f0481f7f3e926f4771176ec627d9013cda610dcb951"
)


class ExecutionContractError(ValueError):
    """Raised when execution-domain, resume, or provenance validation fails."""


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _positive_decimal(value: Decimal | str | float | int) -> Decimal:
    try:
        decimal = value if isinstance(value, Decimal) else Decimal(str(value))
    except Exception as exc:  # Decimal has several implementation-specific errors.
        raise ExecutionContractError(f"invalid radius: {value!r}") from exc
    if not decimal.is_finite() or decimal <= 2:
        raise ExecutionContractError(f"finite-response radius must be > 2M: {value!r}")
    return decimal


def finite_response_radii_from_source(path: str | Path) -> tuple[Decimal, ...]:
    """Derive radial checkpoints from source Cartesian coordinate arrays only."""

    source = Path(path)
    try:
        with np.load(source, allow_pickle=False) as data:
            coordinates = tuple(np.asarray(data[name]) for name in ("point_x", "point_y", "point_z"))
    except (OSError, KeyError, ValueError) as exc:
        raise ExecutionContractError("cannot load finite-response coordinate source") from exc
    if any(array.ndim != 1 for array in coordinates):
        raise ExecutionContractError("finite-response coordinate arrays must be one-dimensional")
    if len({array.size for array in coordinates}) != 1 or coordinates[0].size == 0:
        raise ExecutionContractError("finite-response coordinate arrays have inconsistent size")
    radii: list[Decimal] = []
    with localcontext() as context:
        context.prec = 60
        for values in zip(*coordinates, strict=True):
            pieces = tuple(Decimal(str(float(value))) for value in values)
            if any(not piece.is_finite() for piece in pieces):
                raise ExecutionContractError("finite-response coordinate is non-finite")
            radius = sum((piece * piece for piece in pieces), Decimal(0)).sqrt()
            radii.append(_positive_decimal(radius))
    if len(set(radii)) != len(radii):
        raise ExecutionContractError("finite-response source contains duplicate radii")
    return tuple(radii)


def transition_calibration_keys(
    finite_response_radii: Sequence[Decimal | str | float | int],
    *,
    reference_radius_M: Decimal | str | float | int = GENERIC_REFERENCE_RADIUS_M,
) -> tuple[RadialKey, ...]:
    """Build generic conditioning-transition keys by literal nearest-shell rule."""

    radii = tuple(_positive_decimal(value) for value in finite_response_radii)
    if not radii:
        raise ExecutionContractError("at least one finite-response radius is required")
    reference = _positive_decimal(reference_radius_M)
    if reference != GENERIC_REFERENCE_RADIUS_M:
        raise ExecutionContractError("generic reference radius must remain exactly 40M")
    candidates: set[RadialKey] = set()
    for km in TRANSITION_KM:
        frequency = Decimal(km)
        for radius in (*radii, reference):
            center = int(
                (frequency * radius + Decimal("0.5")).to_integral_value(
                    rounding=ROUND_FLOOR
                )
            )
            for ell in (center - 1, center, center + 1):
                if ell >= 2:
                    candidates.update(RadialKey(km, sector, ell) for sector in ("odd", "even"))
    result = tuple(sorted(candidates, key=RadialKey.order_key))
    validate_ordered_unique_keys(result)
    if len(result) != 158:
        raise ExecutionContractError("transition calibration cardinality must be 158")
    if sha256_bytes(calibration_jsonl_bytes(result)) != EXPECTED_TRANSITION_KEY_LIST_SHA256:
        raise ExecutionContractError("transition calibration key-list hash changed")
    return result


def external_direct_calibration_keys() -> tuple[RadialKey, ...]:
    """Return the frozen external-source direct-calibration keys, independently."""

    keys = tuple(
        RadialKey(km, sector, ell)
        for km in sorted(EXTERNAL_DIRECT_SPEC, key=Decimal)
        for sector in ("odd", "even")
        for ell in EXTERNAL_DIRECT_SPEC[km]
    )
    validate_ordered_unique_keys(keys)
    if len(keys) != 30:
        raise ExecutionContractError("external direct calibration cardinality must be 30")
    return keys


def _shard_id(km: str, sector: str) -> str:
    return f"kM={km};sector={sector}"


@dataclass(frozen=True)
class ShardInventory:
    """A natural frequency/sector partition of an exact frozen union domain."""

    shard_id: str
    kM: str
    sector: str
    keys: tuple[RadialKey, ...]
    production_key_count: int
    extension_key_count: int

    @property
    def key_list_sha256(self) -> str:
        return sha256_bytes(jsonl_bytes(self.keys))

    def to_record(self) -> dict[str, object]:
        return {
            "extension_key_count": self.extension_key_count,
            "kM": self.kM,
            "key_count": len(self.keys),
            "key_list_sha256": self.key_list_sha256,
            "production_key_count": self.production_key_count,
            "sector": self.sector,
            "shard_id": self.shard_id,
        }


def shard_inventory(bundle: DomainBundle) -> tuple[ShardInventory, ...]:
    """Partition D_union by its canonical physical frequency and sector."""

    grouped: dict[tuple[str, str], list[RadialKey]] = defaultdict(list)
    for key in bundle.union:
        grouped[(key.kM, key.sector)].append(key)
    production = set(bundle.production)
    extension = set(bundle.extension)
    records = tuple(
        ShardInventory(
            shard_id=_shard_id(km, sector),
            kM=km,
            sector=sector,
            keys=tuple(sorted(keys, key=RadialKey.order_key)),
            production_key_count=sum(key in production for key in keys),
            extension_key_count=sum(key in extension for key in keys),
        )
        for (km, sector), keys in sorted(
            grouped.items(), key=lambda item: (Decimal(item[0][0]), item[0][1] != "odd")
        )
    )
    validate_shard_inventory(records, bundle)
    return records


def validate_shard_inventory(records: Sequence[ShardInventory], bundle: DomainBundle) -> None:
    """Require 86 disjoint shards whose exact union is D_union."""

    if len(records) != 86:
        raise ExecutionContractError("shard inventory must contain exactly 86 shards")
    all_keys: list[RadialKey] = []
    seen_shards: set[str] = set()
    production = set(bundle.production)
    extension = set(bundle.extension)
    previous: tuple[Decimal, int] | None = None
    for record in records:
        if not isinstance(record, ShardInventory):
            raise ExecutionContractError("invalid shard record type")
        order = (Decimal(record.kM), 0 if record.sector == "odd" else 1)
        if previous is not None and order <= previous:
            raise ExecutionContractError("shard order changed")
        previous = order
        if record.shard_id != _shard_id(record.kM, record.sector) or record.shard_id in seen_shards:
            raise ExecutionContractError("shard identity changed")
        seen_shards.add(record.shard_id)
        validate_ordered_unique_keys(record.keys)
        if any(key.kM != record.kM or key.sector != record.sector for key in record.keys):
            raise ExecutionContractError("shard contains a foreign key")
        if record.production_key_count != sum(key in production for key in record.keys):
            raise ExecutionContractError("shard production membership count changed")
        if record.extension_key_count != sum(key in extension for key in record.keys):
            raise ExecutionContractError("shard extension membership count changed")
        if record.production_key_count + record.extension_key_count != len(record.keys):
            raise ExecutionContractError("shard membership is not a disjoint partition")
        all_keys.extend(record.keys)
    if len(all_keys) != len(set(all_keys)) or set(all_keys) != set(bundle.union):
        raise ExecutionContractError("shard union differs from D_union")
    if sum(item.production_key_count for item in records) != len(bundle.production):
        raise ExecutionContractError("shard production aggregate changed")
    if sum(item.extension_key_count for item in records) != len(bundle.extension):
        raise ExecutionContractError("shard extension aggregate changed")


def calibration_jsonl_bytes(keys: Iterable[RadialKey]) -> bytes:
    return jsonl_bytes(keys)


def _validate_state(value: object, *, label: str) -> str:
    if value not in ACCEPTANCE_STATES:
        raise ExecutionContractError(f"invalid {label} acceptance state: {value!r}")
    return str(value)


def _validate_budget(value: object, *, fields: tuple[str, ...], label: str) -> None:
    if not isinstance(value, Mapping) or set(value) != {"components", "status"}:
        raise ExecutionContractError(f"{label} budget schema changed")
    _validate_state(value["status"], label=f"{label} budget")
    components = value["components"]
    if not isinstance(components, Mapping) or set(components) != set(fields):
        raise ExecutionContractError(f"{label} budget components changed")
    for name, component in components.items():
        if isinstance(component, bool) or not isinstance(component, (int, float)) or not math.isfinite(component) or component < 0:
            raise ExecutionContractError(f"invalid {label} budget component: {name}")


def _expected_hash_map(expected_context: Mapping[str, object], label: str) -> Mapping[str, str]:
    value = expected_context.get(label)
    if not isinstance(value, Mapping) or not value:
        raise ExecutionContractError(f"expected {label} is missing")
    if any(not isinstance(name, str) or not isinstance(digest, str) or len(digest) != 64 for name, digest in value.items()):
        raise ExecutionContractError(f"expected {label} is invalid")
    return value  # type: ignore[return-value]


def _expected_scalar(expected_context: Mapping[str, object], label: str) -> str:
    value = expected_context.get(label)
    if not isinstance(value, str) or len(value) != 64:
        raise ExecutionContractError(f"expected {label} is missing")
    return value


def _expected_shard_keys(expected_context: Mapping[str, object]) -> tuple[RadialKey, ...]:
    raw = expected_context.get("shard_keys")
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)) or not raw:
        raise ExecutionContractError("expected shard_keys are missing")
    keys = tuple(
        item if isinstance(item, RadialKey) else RadialKey.from_record(item)
        for item in raw
        if isinstance(item, (RadialKey, Mapping))
    )
    if len(keys) != len(raw):
        raise ExecutionContractError("expected shard key is invalid")
    return validate_ordered_unique_keys(keys)


def _expected_actual_precision(expected_context: Mapping[str, object]) -> Mapping[str, object]:
    value = expected_context.get("actual_precision")
    if not isinstance(value, Mapping) or set(value) != {"backend", "digits"}:
        raise ExecutionContractError("expected actual_precision is invalid")
    if not isinstance(value["backend"], str) or not value["backend"]:
        raise ExecutionContractError("expected actual_precision backend is invalid")
    if not isinstance(value["digits"], int) or value["digits"] < 1:
        raise ExecutionContractError("expected actual_precision digits is invalid")
    return value


def _expected_ladder_descriptors(expected_context: Mapping[str, object]) -> list[dict[str, object]]:
    raw = expected_context.get("ladder_axis_descriptors")
    if not isinstance(raw, list) or not raw:
        raise ExecutionContractError("expected ladder axis descriptors are missing")
    descriptors: list[dict[str, object]] = []
    for item in raw:
        if not isinstance(item, Mapping) or set(item) != {"actual_precision_digits", "node_id", "tolerance"}:
            raise ExecutionContractError("expected ladder descriptor schema is invalid")
        node_id, digits, tolerance = item["node_id"], item["actual_precision_digits"], item["tolerance"]
        if not isinstance(node_id, str) or not node_id:
            raise ExecutionContractError("expected ladder node id is invalid")
        if not isinstance(digits, int) or digits < 1:
            raise ExecutionContractError("expected ladder precision is invalid")
        if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)) or not math.isfinite(tolerance) or tolerance < 0:
            raise ExecutionContractError("expected ladder tolerance is invalid")
        descriptors.append(dict(item))
    if len({item["node_id"] for item in descriptors}) != len(descriptors):
        raise ExecutionContractError("expected ladder node ids are not unique")
    expected_hash = _expected_scalar(expected_context, "ladder_axis_map_sha256")
    if sha256_bytes(canonical_json_bytes(descriptors)) != expected_hash:
        raise ExecutionContractError("expected ladder axis map hash does not match descriptors")
    return descriptors


def resume_claims_sha256(checkpoint: Mapping[str, object]) -> str:
    """Bind every reusable claim without creating a result-identity cycle."""

    return sha256_bytes(canonical_json_bytes({
        name: value for name, value in checkpoint.items() if name != "result_identity"
    }))


def _immutable_artifact_under_root(path: Path, expected_root: object, *, label: str) -> dict[str, object]:
    if not isinstance(expected_root, str) or not expected_root:
        raise ExecutionContractError("expected evidence root is missing")
    root = Path(expected_root).absolute()
    candidate = path.absolute()
    try:
        root_status = root.lstat()
    except OSError as exc:
        raise ExecutionContractError("evidence root cannot be lstat") from exc
    if root.is_symlink() or not root.is_dir() or root.resolve(strict=True) != root or (root_status.st_mode & 0o777) != 0o555:
        raise ExecutionContractError("evidence root must be a direct 0555 directory")
    if candidate.parent != root or candidate.resolve(strict=True) != candidate:
        raise ExecutionContractError(f"{label} must be a direct child of the evidence root")
    try:
        identity = source_file_identity(candidate)
    except DomainContractError as exc:
        raise ExecutionContractError(f"{label} path is not immutable") from exc
    if identity["mode"] != 0o444:
        raise ExecutionContractError(f"{label} mode must be 0444")
    return identity


def validate_key_checkpoint(
    checkpoint: Mapping[str, object], *, expected_context: Mapping[str, object], result_path: Path
) -> None:
    """Fail closed against an external immutable result artifact before reuse."""

    required = {
        "acceptance_state", "actual_precision", "attempts", "backend_hashes",
        "code_hashes", "config_hashes", "convention_budget",
        "domain_contract_sha256", "domain_union_key_list_sha256",
        "execution_contract_sha256", "execution_manifest_sha256",
        "global_green_permitted", "key", "ladder", "numerical_budget",
        "observable_statuses", "provenance", "result_identity", "schema", "shard", "source_hashes",
    }
    if set(checkpoint) != required or checkpoint.get("schema") != CHECKPOINT_SCHEMA:
        raise ExecutionContractError("checkpoint schema changed")
    if checkpoint.get("global_green_permitted") is not False:
        raise ExecutionContractError("checkpoint may not assert global GREEN")
    for label in (
        "domain_contract_sha256", "domain_union_key_list_sha256",
        "execution_contract_sha256", "execution_manifest_sha256",
    ):
        if checkpoint.get(label) != _expected_scalar(expected_context, label):
            raise ExecutionContractError(f"checkpoint {label} mismatch")
    for label in ("backend_hashes", "code_hashes", "config_hashes", "source_hashes"):
        hashes = checkpoint[label]
        if not isinstance(hashes, Mapping) or dict(hashes) != dict(_expected_hash_map(expected_context, label)):
            raise ExecutionContractError(f"checkpoint {label} mismatch")
    key_raw = checkpoint["key"]
    if not isinstance(key_raw, Mapping):
        raise ExecutionContractError("checkpoint key is invalid")
    key = RadialKey.from_record(key_raw)
    shard = checkpoint["shard"]
    expected_shard = expected_context.get("shard")
    if not isinstance(shard, Mapping) or not isinstance(expected_shard, Mapping) or dict(shard) != dict(expected_shard):
        raise ExecutionContractError("checkpoint shard identity mismatch")
    expected_keys = _expected_shard_keys(expected_context)
    if key not in expected_keys:
        raise ExecutionContractError("checkpoint key is outside exact expected shard")
    if shard.get("key_list_sha256") != sha256_bytes(jsonl_bytes(expected_keys)):
        raise ExecutionContractError("checkpoint shard key-list hash mismatch")
    identity = checkpoint["result_identity"]
    if not isinstance(identity, Mapping) or set(identity) != {"mode", "nlink", "path", "sha256", "size"}:
        raise ExecutionContractError("result no-overwrite identity schema changed")
    actual_identity = _immutable_artifact_under_root(
        result_path, expected_context.get("evidence_root"), label="result artifact"
    )
    if dict(identity) != actual_identity:
        raise ExecutionContractError("result artifact identity mismatch")
    actual_precision = checkpoint["actual_precision"]
    if not isinstance(actual_precision, Mapping) or set(actual_precision) != {"backend", "digits"}:
        raise ExecutionContractError("actual precision schema changed")
    if not isinstance(actual_precision["backend"], str) or not actual_precision["backend"]:
        raise ExecutionContractError("actual precision backend missing")
    if not isinstance(actual_precision["digits"], int) or actual_precision["digits"] < 1:
        raise ExecutionContractError("actual precision digits invalid")
    if dict(actual_precision) != dict(_expected_actual_precision(expected_context)):
        raise ExecutionContractError("actual precision differs from expected context")
    attempts = checkpoint["attempts"]
    if not isinstance(attempts, list) or not attempts or any(
        not isinstance(item, Mapping) or set(item) != {"attempt", "status"} for item in attempts
    ):
        raise ExecutionContractError("checkpoint attempt inventory changed")
    if [item["attempt"] for item in attempts] != list(range(1, len(attempts) + 1)):
        raise ExecutionContractError("checkpoint attempts are not ordered")
    if any(_validate_state(item["status"], label="attempt") == "PASS" for item in attempts[:-1]):
        raise ExecutionContractError("checkpoint has attempts after PASS")
    ladder = checkpoint["ladder"]
    expected_ladder_hash = _expected_scalar(expected_context, "ladder_axis_map_sha256")
    expected_descriptors = _expected_ladder_descriptors(expected_context)
    if not isinstance(ladder, Mapping) or set(ladder) != {"axis_map_sha256", "failures", "nodes"}:
        raise ExecutionContractError("ladder inventory schema changed")
    if ladder.get("axis_map_sha256") != expected_ladder_hash:
        raise ExecutionContractError("ladder axis map mismatch")
    nodes, failures = ladder["nodes"], ladder["failures"]
    if not isinstance(nodes, list) or not isinstance(failures, list):
        raise ExecutionContractError("ladder inventory missing")
    if [item.get("node_id") if isinstance(item, Mapping) else None for item in nodes] != [item["node_id"] for item in expected_descriptors]:
        raise ExecutionContractError("ladder node order/identity mismatch")
    for node, descriptor in zip(nodes, expected_descriptors, strict=True):
        if not isinstance(node, Mapping) or set(node) != {"actual_precision_digits", "node_id", "status", "tolerance"}:
            raise ExecutionContractError("ladder node schema changed")
        if not isinstance(node["actual_precision_digits"], int) or node["actual_precision_digits"] < 1:
            raise ExecutionContractError("ladder node precision invalid")
        if isinstance(node["tolerance"], bool) or not isinstance(node["tolerance"], (int, float)) or not math.isfinite(node["tolerance"]) or node["tolerance"] < 0:
            raise ExecutionContractError("ladder node tolerance invalid")
        if {name: node[name] for name in descriptor} != descriptor:
            raise ExecutionContractError("ladder node descriptor differs from expected axis metadata")
        _validate_state(node["status"], label="ladder node")
    failure_ids = []
    for failure in failures:
        if not isinstance(failure, Mapping) or set(failure) != {"node_id", "reason"}:
            raise ExecutionContractError("ladder failure schema changed")
        if not isinstance(failure["node_id"], str) or not isinstance(failure["reason"], str) or not failure["reason"]:
            raise ExecutionContractError("ladder failure invalid")
        failure_ids.append(failure["node_id"])
    failed_nodes = [node["node_id"] for node in nodes if node["status"] == "FAIL"]
    if failure_ids != failed_nodes or len(failure_ids) != len(set(failure_ids)):
        raise ExecutionContractError("ladder failures do not correspond exactly to FAIL nodes")
    if nodes[-1]["actual_precision_digits"] != actual_precision["digits"]:
        raise ExecutionContractError("final ladder precision differs from actual precision")
    _validate_budget(checkpoint["numerical_budget"], fields=NUMERICAL_BUDGET_FIELDS, label="numerical")
    _validate_budget(checkpoint["convention_budget"], fields=CONVENTION_BUDGET_FIELDS, label="convention")
    observable_states = checkpoint["observable_statuses"]
    if not isinstance(observable_states, Mapping) or not observable_states:
        raise ExecutionContractError("per-observable acceptance statuses missing")
    for name, state in observable_states.items():
        if not isinstance(name, str) or not name or any(token in name.lower() for token in ("global", "project", "schwo")):
            raise ExecutionContractError("observable name is not key-local")
        _validate_state(state, label="observable")
    _validate_state(checkpoint["acceptance_state"], label="key")
    provenance = checkpoint["provenance"]
    if not isinstance(provenance, Mapping) or set(provenance) != {"legacy", "np", "pseudoinverse"}:
        raise ExecutionContractError("provenance schema changed")
    if any(value is not False for value in provenance.values()):
        raise ExecutionContractError("legacy/NP/pseudoinverse provenance rejects production acceptance")
    try:
        raw_result = result_path.read_bytes()
        result = json.loads(raw_result)
    except (OSError, json.JSONDecodeError) as exc:
        raise ExecutionContractError("result artifact cannot be parsed") from exc
    if not isinstance(result, Mapping) or raw_result != canonical_json_bytes(result):
        raise ExecutionContractError("result artifact is not canonical JSON")
    result_fields = {
        "acceptance_state", "actual_precision", "domain_contract_sha256",
        "domain_union_key_list_sha256", "execution_contract_sha256",
        "execution_manifest_sha256", "key", "observable_statuses", "payload_identity",
        "payload_schema", "resume_claims_sha256", "schema", "shard",
    }
    if set(result) != result_fields or result.get("schema") != KEY_RESULT_SCHEMA:
        raise ExecutionContractError("result artifact schema changed")
    for field in result_fields - {"schema"}:
        if field in {"payload_identity", "payload_schema", "resume_claims_sha256"}:
            continue
        if result.get(field) != checkpoint.get(field):
            raise ExecutionContractError(f"result artifact {field} linkage mismatch")
    if result.get("resume_claims_sha256") != resume_claims_sha256(checkpoint):
        raise ExecutionContractError("result artifact does not bind complete resume claims")
    payload_schema = result.get("payload_schema")
    payload_identity = result.get("payload_identity")
    if not isinstance(payload_schema, str) or not payload_schema:
        raise ExecutionContractError("result payload schema missing")
    if not isinstance(payload_identity, Mapping) or set(payload_identity) != {"mode", "nlink", "path", "sha256", "size"}:
        raise ExecutionContractError("result payload identity schema changed")
    payload_path = Path(str(payload_identity.get("path", "")))
    actual_payload_identity = _immutable_artifact_under_root(
        payload_path, expected_context.get("evidence_root"), label="result payload"
    )
    if dict(payload_identity) != actual_payload_identity:
        raise ExecutionContractError("result payload identity mismatch")
    try:
        raw_payload = payload_path.read_bytes()
        payload = json.loads(raw_payload)
    except (OSError, json.JSONDecodeError) as exc:
        raise ExecutionContractError("result payload cannot be parsed") from exc
    if not isinstance(payload, Mapping) or raw_payload != canonical_json_bytes(payload):
        raise ExecutionContractError("result payload is not canonical JSON")
    if payload_schema != KEY_PAYLOAD_ENVELOPE_SCHEMA or payload.get("schema") != payload_schema:
        raise ExecutionContractError("result payload envelope schema linkage mismatch")
    payload_fields = {
        "domain_contract_sha256", "domain_union_key_list_sha256",
        "execution_contract_sha256", "execution_manifest_sha256", "key", "schema",
        "shard", "solver_payload", "solver_payload_schema",
    }
    if set(payload) != payload_fields:
        raise ExecutionContractError("result payload envelope fields changed")
    for field in payload_fields - {"schema", "solver_payload", "solver_payload_schema"}:
        if payload.get(field) != checkpoint.get(field):
            raise ExecutionContractError(f"result payload {field} linkage mismatch")
    solver_schema = payload.get("solver_payload_schema")
    solver_payload = payload.get("solver_payload")
    if not isinstance(solver_schema, str) or not solver_schema:
        raise ExecutionContractError("solver payload schema discriminator missing")
    if not isinstance(solver_payload, Mapping) or solver_payload.get("schema_version") != solver_schema:
        raise ExecutionContractError("solver payload schema_version linkage mismatch")


def validate_resume_eligible(
    checkpoint: Mapping[str, object], *, expected_context: Mapping[str, object], result_path: Path
) -> None:
    """Reuse only a key with exact identity and fully PASS local evidence."""

    validate_key_checkpoint(checkpoint, expected_context=expected_context, result_path=result_path)
    if checkpoint["acceptance_state"] != "PASS":
        raise ExecutionContractError("only PASS key checkpoints may be reused")
    if checkpoint["attempts"][-1]["status"] != "PASS":  # type: ignore[index]
        raise ExecutionContractError("latest attempt is not PASS")
    for label in ("numerical_budget", "convention_budget"):
        if checkpoint[label]["status"] != "PASS":  # type: ignore[index]
            raise ExecutionContractError(f"{label} does not permit reuse")
    if any(state != "PASS" for state in checkpoint["observable_statuses"].values()):  # type: ignore[index]
        raise ExecutionContractError("all local observable statuses must PASS for reuse")
    if any(node["status"] != "PASS" for node in checkpoint["ladder"]["nodes"]):  # type: ignore[index]
        raise ExecutionContractError("all required ladder nodes must PASS for reuse")


def execution_contract_payload(
    *,
    bound_domain: Mapping[str, object],
    finite_radius_source: Mapping[str, object],
    transition_keys: Sequence[RadialKey],
    external_keys: Sequence[RadialKey],
    shards: Sequence[ShardInventory],
    source_identities: Mapping[str, Mapping[str, object]],
    consumed_execution_predecessors: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Build deterministic, generic execution metadata without a science result."""

    transition = validate_ordered_unique_keys(transition_keys)
    external = validate_ordered_unique_keys(external_keys)
    if len(transition) != 158 or len(external) != 30:
        raise ExecutionContractError("calibration cardinality changed")
    if len(shards) != 86:
        raise ExecutionContractError("shard cardinality changed")
    if not consumed_execution_predecessors:
        raise ExecutionContractError("consumed execution predecessor provenance is required")
    return {
        "acceptance_vocabulary": list(ACCEPTANCE_STATES),
        "bound_domain": dict(bound_domain),
        "consumed_execution_predecessors": [
            dict(item) for item in consumed_execution_predecessors
        ],
        "checkpoint_resume_contract": {
            "key_checkpoint_schema": CHECKPOINT_SCHEMA,
            "key_result_schema": KEY_RESULT_SCHEMA,
            "immutable_result_identity_fields": ["path", "sha256", "size", "mode", "nlink"],
            "result_artifact_schema": KEY_RESULT_SCHEMA,
            "result_envelope_required_fields": [
                "resume_claims_sha256",
                "payload_schema",
                "payload_identity",
                "key",
                "shard",
                "actual_precision",
                "acceptance_state",
                "observable_statuses",
            ],
            "resume_rule": "reuse requires exact schema/domain/code/config/hash identity and PASS key result artifact",
            "reject_provenance": ["legacy", "np", "pseudoinverse"],
            "required_fields": [
                "actual_precision",
                "attempts",
                "ladder.nodes",
                "ladder.failures",
                "numerical_budget",
                "convention_budget",
                "observable_statuses",
                "result_identity",
            ],
            "shard_checkpoint_schema": SHARD_CHECKPOINT_SCHEMA,
            "shard_result_schema": SHARD_RESULT_SCHEMA,
            "shard_required_fields": [
                "shard_id",
                "key_list_sha256",
                "key_checkpoint_identities",
                "attempts",
                "backend_hashes",
                "source_hashes",
                "code_hashes",
                "config_hashes",
                "domain_contract_sha256",
                "domain_union_key_list_sha256",
                "numerical_budget",
                "convention_budget",
                "observable_statuses",
            ],
        },
        "domain_acceptance": {
            "global_green_permitted": False,
            "per_domain_states": list(ACCEPTANCE_STATES),
            "per_observable_states": list(ACCEPTANCE_STATES),
            "paper_agreement_gate": "PROHIBITED",
        },
        "external_direct_calibration": {
            "count": len(external),
            "key_list_sha256": sha256_bytes(calibration_jsonl_bytes(external)),
            "purpose": "EXTERNAL_SOURCE_CALIBRATION_ONLY_NOT_DOMAIN_ACCEPTANCE",
            "schema": EXTERNAL_DIRECT_CALIBRATION_SCHEMA,
        },
        "generic_transition_calibration": {
            "construction": {
                "formula": "ell = floor(kM * radius_M + 0.5) + offset; offset in {-1,0,1}; ell >= 2",
                "kM": list(TRANSITION_KM),
                "reference_radius_M": _decimal_text(GENERIC_REFERENCE_RADIUS_M),
                "response_radius_source": dict(finite_radius_source),
            },
            "count": len(transition),
            "key_list_sha256": sha256_bytes(calibration_jsonl_bytes(transition)),
            "purpose": "GENERIC_CONDITIONING_TRANSITION_CALIBRATION_ONLY",
            "schema": TRANSITION_CALIBRATION_SCHEMA,
        },
        "schema": EXECUTION_SCHEMA,
        "shard_inventory": {
            "count": len(shards),
            "records": [record.to_record() for record in shards],
            "schema": SHARD_SCHEMA,
        },
        "source_identities": dict(sorted(source_identities.items())),
        "status": "EXECUTION_CONTRACT_FROZEN_NO_NUMERICAL_SOLVES",
    }


__all__ = [
    "ACCEPTANCE_STATES",
    "CHECKPOINT_SCHEMA",
    "CONVENTION_BUDGET_FIELDS",
    "EXECUTION_SCHEMA",
    "EXTERNAL_DIRECT_CALIBRATION_SCHEMA",
    "ExecutionContractError",
    "EXPECTED_TRANSITION_KEY_LIST_SHA256",
    "GENERIC_REFERENCE_RADIUS_M",
    "KEY_RESULT_SCHEMA",
    "KEY_PAYLOAD_ENVELOPE_SCHEMA",
    "NUMERICAL_BUDGET_FIELDS",
    "ShardInventory",
    "SHARD_CHECKPOINT_SCHEMA",
    "SHARD_RESULT_SCHEMA",
    "calibration_jsonl_bytes",
    "execution_contract_payload",
    "external_direct_calibration_keys",
    "finite_response_radii_from_source",
    "shard_inventory",
    "resume_claims_sha256",
    "transition_calibration_keys",
    "validate_key_checkpoint",
    "validate_resume_eligible",
    "validate_shard_inventory",
]
