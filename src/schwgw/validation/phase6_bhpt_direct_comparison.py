"""Strict Phase-6 comparison of BHPT direct and conditioned radial amplitudes.

This module is a read-only evidence consumer.  It never invokes either radial
solver.  A comparison can be built only from a terminal immutable BHPT direct
root, the immutable 86-shard conditioning campaign, and the eight immutable
conditioning shards that contain the frozen 30-key external-calibration set.

The comparison deliberately has no acceptance threshold.  The 24 available
internal amplitudes therefore remain ``PARTIAL`` and the six frozen internal
solver failures remain ``FAIL``.  No phase or normalization fit is permitted.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, localcontext
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat

from schwgw.validation.phase6_bhpt_direct import (
    EVIDENCE_SCHEMA as BHPT_EVIDENCE_SCHEMA,
    EXPECTED_KEY_LIST_SHA256,
    RAW_SCHEMA as BHPT_RAW_SCHEMA,
    REQUEST_SCHEMA as BHPT_REQUEST_SCHEMA,
    _validate_frozen_root as validate_frozen_bhpt_root,
    validate_external_payload,
)
from schwgw.validation.phase6_conditioning_campaign import (
    CAMPAIGN_INDEX_SCHEMA,
    ValidatedConditioningShard,
    validate_conditioning_shard_root,
    validate_published_conditioning_campaign,
)
from schwgw.validation.phase6_conditioning_scan import key_artifact_filenames
from schwgw.validation.phase6_domain import (
    RadialKey,
    canonical_json_bytes,
    source_file_identity,
)
from schwgw.validation.phase6_execution_contract import (
    external_direct_calibration_keys,
)
from schwgw.validation.phase6_release import (
    CONVENTION_BUDGET_FIELDS,
    NUMERICAL_BUDGET_FIELDS,
)


COMPARISON_SCHEMA = "schwgw_phase6_bhpt_direct_conditioned_comparison_v1"
MANIFEST_SCHEMA = "schwgw_phase6_bhpt_direct_conditioned_comparison_manifest_v1"
TYPED_RESULT_SCHEMA = "schwgw_phase6_v1_typed_physical_result_v1"
COMPARISON_SCOPE = "SELECTED_30_KEY_CROSS_BACKEND_COMPARISON_NOT_DOMAIN_ACCEPTANCE"
FORMAL_ROOT_MODE = 0o555
FORMAL_FILE_MODE = 0o444
EXPECTED_KEY_COUNT = 30
EXPECTED_PARTIAL_COUNT = 24
EXPECTED_FAIL_COUNT = 6
PROJECT_ROOT = Path(__file__).resolve().parents[3]
COMPARISON_MODULE_PATH = Path(__file__).resolve()
COMPARISON_RUNNER_PATH = (
    PROJECT_ROOT / "scripts" / "phase6_compare_bhpt_direct_conditioned.py"
)
FLOAT64_UNASSESSED_SENTINEL = Decimal(str(float.fromhex("0x1.fffffffffffffp+1023")))

_ID = re.compile(r"[a-z0-9][a-z0-9_.-]{0,95}")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_EXPECTED_FAIL_KEYS = frozenset(
    RadialKey(kM=kM, sector=sector, ell=ell)
    for kM, ell in (("1", 20), ("2", 60), ("4", 120))
    for sector in ("odd", "even")
)


def _item_id(key: RadialKey) -> str:
    km = key.kM.replace("-", "m").replace(".", "p")
    return f"radial_km_{km}_{key.sector}_ell_{key.ell:03d}"


_EXPECTED_ITEM_IDS = tuple(
    sorted(_item_id(key) for key in external_direct_calibration_keys())
)


class BHPTConditionedComparisonError(ValueError):
    """Raised when source evidence, comparison algebra, or publication drifts."""


@dataclass(frozen=True)
class DecimalComplex:
    """Small Decimal complex type used to avoid losing BHPT output precision."""

    real: Decimal
    imag: Decimal

    def __sub__(self, other: "DecimalComplex") -> "DecimalComplex":
        return DecimalComplex(self.real - other.real, self.imag - other.imag)

    def scale(self, factor: int | Decimal) -> "DecimalComplex":
        value = Decimal(factor)
        return DecimalComplex(self.real * value, self.imag * value)

    def absolute(self) -> Decimal:
        with localcontext() as context:
            context.prec = 100
            return (self.real * self.real + self.imag * self.imag).sqrt()


def _exact(value: object, fields: set[str], label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != fields:
        raise BHPTConditionedComparisonError(f"{label} exact schema changed")
    return value


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise BHPTConditionedComparisonError(f"{label} is not canonical")
    return value


def _sha(value: object, label: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise BHPTConditionedComparisonError(f"{label} is not SHA-256")
    return value


def _decimal(value: object, label: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise BHPTConditionedComparisonError(f"{label} is not numeric")
    try:
        parsed = Decimal(str(value))
    except InvalidOperation as exc:
        raise BHPTConditionedComparisonError(f"{label} is not decimal") from exc
    if not parsed.is_finite():
        raise BHPTConditionedComparisonError(f"{label} is not finite")
    return parsed


def _decimal_text(value: Decimal) -> str:
    if value == 0:
        return "0"
    return str(value.normalize())


def _complex(value: object, label: str) -> DecimalComplex:
    if not isinstance(value, Mapping) or not {"real", "imag"} <= set(value):
        raise BHPTConditionedComparisonError(f"{label} lacks real/imag")
    if set(value) not in ({"real", "imag"}, {"real", "imag", "abs"}):
        raise BHPTConditionedComparisonError(f"{label} complex schema changed")
    result = DecimalComplex(
        _decimal(value["real"], f"{label}.real"),
        _decimal(value["imag"], f"{label}.imag"),
    )
    if "abs" in value:
        recorded = _decimal(value["abs"], f"{label}.abs")
        scale = max(Decimal(1), recorded, result.absolute())
        if abs(recorded - result.absolute()) > Decimal("5e-15") * scale:
            raise BHPTConditionedComparisonError(f"{label}.abs is inconsistent")
    return result


def _close_complex(
    actual: DecimalComplex,
    expected: DecimalComplex,
    *,
    label: str,
    relative_tolerance: Decimal = Decimal("5e-15"),
) -> None:
    scale = max(Decimal(1), actual.absolute(), expected.absolute())
    if (actual - expected).absolute() > relative_tolerance * scale:
        raise BHPTConditionedComparisonError(f"{label} is inconsistent")


def _wrapped_phase_difference(left: DecimalComplex, right: DecimalComplex) -> float:
    left_phase = math.atan2(float(left.imag), float(left.real))
    right_phase = math.atan2(float(right.imag), float(right.real))
    return math.remainder(left_phase - right_phase, 2.0 * math.pi)


def _metric(left: DecimalComplex, right: DecimalComplex) -> dict[str, object]:
    difference = left - right
    wrapped = _wrapped_phase_difference(left, right)
    return {
        "complex_abs_difference": _decimal_text(difference.absolute()),
        "modulus_abs_difference": _decimal_text(
            abs(left.absolute() - right.absolute())
        ),
        "wrapped_phase_difference_abs_rad": format(abs(wrapped), ".17g"),
        "wrapped_phase_difference_rad": format(wrapped, ".17g"),
    }


def _direct_root(path: str | Path, label: str) -> Path:
    root = Path(path)
    if not root.is_absolute():
        raise BHPTConditionedComparisonError(f"{label} must be absolute")
    try:
        resolved = root.resolve(strict=True)
    except OSError as exc:
        raise BHPTConditionedComparisonError(f"{label} is unavailable") from exc
    if root != resolved or any(
        component.is_symlink() for component in (root, *root.parents)
    ):
        raise BHPTConditionedComparisonError(f"{label} is aliased")
    status = root.lstat()
    if not stat.S_ISDIR(status.st_mode) or stat.S_IMODE(status.st_mode) != 0o555:
        raise BHPTConditionedComparisonError(f"{label} is not immutable 0555")
    return root


def _strict_file_identity(path: Path) -> dict[str, object]:
    try:
        status = path.lstat()
    except OSError as exc:
        raise BHPTConditionedComparisonError(f"missing artifact: {path}") from exc
    if (
        path.is_symlink()
        or not stat.S_ISREG(status.st_mode)
        or stat.S_IMODE(status.st_mode) != FORMAL_FILE_MODE
        or status.st_nlink != 1
    ):
        raise BHPTConditionedComparisonError(
            f"artifact is not immutable 0444/nlink1: {path}"
        )
    return source_file_identity(path)


def _read_json(path: Path) -> Mapping[str, object]:
    _strict_file_identity(path)
    try:
        value = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BHPTConditionedComparisonError(f"invalid JSON artifact: {path}") from exc
    if not isinstance(value, Mapping):
        raise BHPTConditionedComparisonError(f"JSON artifact is not an object: {path}")
    return value


def _root_descriptor(root: Path) -> dict[str, object]:
    return {"mode": stat.S_IMODE(root.lstat().st_mode), "path": str(root)}


def _identity_sha(value: object, label: str) -> str:
    if not isinstance(value, Mapping):
        raise BHPTConditionedComparisonError(f"{label} identity is missing")
    return _sha(value.get("sha256"), f"{label} identity hash")


def _load_external_bhpt(root_path: str | Path) -> dict[str, object]:
    root = _direct_root(root_path, "BHPT direct root")
    try:
        validate_frozen_bhpt_root(root)
    except Exception as exc:
        raise BHPTConditionedComparisonError(
            "BHPT direct formal root failed strict reload"
        ) from exc
    evidence = _read_json(root / "evidence.json")
    manifest = _read_json(root / "manifest.json")
    request_path = root / "request.json"
    request = _read_json(request_path)
    if (
        evidence.get("schema_version") != BHPT_EVIDENCE_SCHEMA
        or evidence.get("status") != "PASS"
        or evidence.get("status_scope") != "SOURCE_METHOD_SCHEMA_AND_ALGEBRA_ONLY"
        or evidence.get("scientific_acceptance_status") != "NOT_ASSESSED"
        or evidence.get("science_executed") is not True
        or evidence.get("blocker") is not None
        or evidence.get("record_count") != EXPECTED_KEY_COUNT
        or evidence.get("even_is_independent_radial_solution") is not True
        or evidence.get("parity_derived_even_used") is not False
        or evidence.get("internal_solver_fallback_used") is not False
        or evidence.get("global_green_permitted") is not False
    ):
        raise BHPTConditionedComparisonError(
            "BHPT direct root is not a terminal 30-record source/method PASS"
        )
    if (
        manifest.get("terminal_status") != "PASS"
        or manifest.get("returncode") != 0
        or manifest.get("science_executed") is not True
        or manifest.get("external_record_count") != EXPECTED_KEY_COUNT
    ):
        raise BHPTConditionedComparisonError("BHPT direct manifest is not successful")
    raw_path = root / "external_bhpt_direct.json"
    raw = _read_json(raw_path)
    if raw.get("schema_version") != BHPT_RAW_SCHEMA:
        raise BHPTConditionedComparisonError("BHPT direct raw schema changed")
    request_sha256 = _sha(evidence.get("request_sha256"), "BHPT request hash")
    request_identity = _strict_file_identity(request_path)
    if (
        request.get("schema_version") != BHPT_REQUEST_SCHEMA
        or request_identity["sha256"] != request_sha256
    ):
        raise BHPTConditionedComparisonError("BHPT request/evidence linkage changed")
    try:
        validated = validate_external_payload(
            raw, expected_request_sha256=request_sha256
        )
    except Exception as exc:
        raise BHPTConditionedComparisonError(
            "BHPT direct raw payload failed strict validation"
        ) from exc
    raw_identity = _strict_file_identity(raw_path)
    if (
        validated.get("status") != "PASS"
        or evidence.get("external_json") != str(raw_path)
        or evidence.get("external_json_sha256") != raw_identity["sha256"]
    ):
        raise BHPTConditionedComparisonError("BHPT raw/evidence linkage changed")
    producer = request.get("producer_source")
    orchestrators = request.get("orchestrator_sources")
    toolkit = request.get("toolkit_source")
    toolkit_files = toolkit.get("files") if isinstance(toolkit, Mapping) else None
    if (
        not isinstance(orchestrators, Mapping)
        or set(orchestrators) != {"runner", "validation_module"}
        or not isinstance(toolkit_files, Mapping)
    ):
        raise BHPTConditionedComparisonError(
            "BHPT direct implementation source ledger changed"
        )
    implementation_hashes = {
        "bhpt_direct_producer_wls": _identity_sha(producer, "BHPT producer"),
        "bhpt_direct_runner": _identity_sha(
            orchestrators["runner"], "BHPT direct runner"
        ),
        "bhpt_direct_validation_module": _identity_sha(
            orchestrators["validation_module"], "BHPT direct validation module"
        ),
    }
    for name, identity in sorted(toolkit_files.items()):
        if str(name).endswith(".m"):
            implementation_hashes[f"bhpt_toolkit_{name}"] = _identity_sha(
                identity, f"BHPT toolkit {name}"
            )
    return {
        "evidence": dict(evidence),
        "payload": dict(raw),
        "source": {
            "files": {
                "evidence.json": _strict_file_identity(root / "evidence.json"),
                "external_bhpt_direct.json": raw_identity,
                "manifest.json": _strict_file_identity(root / "manifest.json"),
                "request.json": request_identity,
            },
            "implementation_source_sha256s": dict(
                sorted(implementation_hashes.items())
            ),
            "root": _root_descriptor(root),
        },
    }


def _expected_shard_ids() -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                f"kM={key.kM};sector={key.sector}"
                for key in external_direct_calibration_keys()
            }
        )
    )


def _campaign_entry_map(index: Mapping[str, object]) -> dict[str, Mapping[str, object]]:
    entries = index.get("shards")
    if not isinstance(entries, list) or len(entries) != 86:
        raise BHPTConditionedComparisonError(
            "conditioning campaign shard ledger changed"
        )
    result: dict[str, Mapping[str, object]] = {}
    for entry in entries:
        if not isinstance(entry, Mapping) or not isinstance(
            entry.get("shard"), Mapping
        ):
            raise BHPTConditionedComparisonError(
                "conditioning shard entry is malformed"
            )
        shard_id = entry["shard"].get("shard_id")
        if not isinstance(shard_id, str) or shard_id in result:
            raise BHPTConditionedComparisonError("conditioning shard ids changed")
        result[shard_id] = entry
    return result


def _load_conditioning_campaign(root_path: str | Path) -> dict[str, object]:
    root = _direct_root(root_path, "conditioning campaign root")
    try:
        validate_published_conditioning_campaign(root)
    except Exception as exc:
        raise BHPTConditionedComparisonError(
            "conditioning campaign failed full immutable reload"
        ) from exc
    index = _read_json(root / "conditioning_campaign_index.json")
    if (
        index.get("schema") != CAMPAIGN_INDEX_SCHEMA
        or index.get("scientific_evidence") is not True
        or index.get("science_executed") is not True
        or index.get("kernel_unit_test_only") is not False
        or index.get("contract_only") is not False
        or index.get("global_green_permitted") is not False
        or index.get("li_figure_agreement_primary_gate") is not False
        or index.get("production_finite_radius_states") != "NOT_ASSESSED"
    ):
        raise BHPTConditionedComparisonError("conditioning campaign claims changed")
    coverage = index.get("coverage")
    if not isinstance(coverage, Mapping) or (
        coverage.get("key_count") != 17_818
        or coverage.get("D_union_key_list_sha256")
        != "a5793564dfc28e815699966208ae6605eeeedce9e3629f09512b70e08196810b"
        or coverage.get("shard_count") != 86
    ):
        raise BHPTConditionedComparisonError("conditioning campaign domain changed")
    implementation_hashes = index.get("implementation_source_sha_hashes")
    if (
        not isinstance(implementation_hashes, Mapping)
        or not implementation_hashes
        or any(
            not isinstance(name, str)
            or _sha(digest, f"conditioning implementation {name}") != digest
            for name, digest in implementation_hashes.items()
        )
    ):
        raise BHPTConditionedComparisonError(
            "conditioning implementation source hashes changed"
        )
    return {
        "entry_map": _campaign_entry_map(index),
        "index": dict(index),
        "source": {
            "files": {
                "conditioning_campaign_index.json": _strict_file_identity(
                    root / "conditioning_campaign_index.json"
                ),
                "manifest.json": _strict_file_identity(root / "manifest.json"),
            },
            "implementation_source_sha256s": dict(
                sorted(implementation_hashes.items())
            ),
            "root": _root_descriptor(root),
        },
    }


def _map_and_validate_shards(
    shard_roots: Sequence[str | Path],
    *,
    campaign_entries: Mapping[str, Mapping[str, object]],
) -> dict[str, ValidatedConditioningShard]:
    if len(shard_roots) != len(_expected_shard_ids()):
        raise BHPTConditionedComparisonError("exactly eight shard roots are required")
    mapped: dict[str, Path] = {}
    for raw_root in shard_roots:
        root = _direct_root(raw_root, "conditioning comparison shard root")
        contract = _read_json(root / "run_contract.json")
        shard = contract.get("shard")
        shard_id = shard.get("shard_id") if isinstance(shard, Mapping) else None
        if not isinstance(shard_id, str) or shard_id in mapped:
            raise BHPTConditionedComparisonError("duplicate/malformed comparison shard")
        mapped[shard_id] = root
    if set(mapped) != set(_expected_shard_ids()):
        raise BHPTConditionedComparisonError(
            "comparison shard ids do not match the frozen 30-key domain"
        )
    validated: dict[str, ValidatedConditioningShard] = {}
    for shard_id in _expected_shard_ids():
        entry = campaign_entries.get(shard_id)
        root = mapped[shard_id]
        if not isinstance(entry, Mapping) or entry.get("root") != str(root):
            raise BHPTConditionedComparisonError(
                "explicit shard root differs from conditioning campaign ledger"
            )
        try:
            item = validate_conditioning_shard_root(root, expected_shard_id=shard_id)
        except Exception as exc:
            raise BHPTConditionedComparisonError(
                f"conditioning shard failed strict reload: {shard_id}"
            ) from exc
        if entry.get("identities") != {
            name: dict(identity) for name, identity in item.top_identities.items()
        }:
            raise BHPTConditionedComparisonError(
                "conditioning campaign/shard top identities changed"
            )
        validated[shard_id] = item
    return validated


def _load_internal_records(
    shards: Mapping[str, ValidatedConditioningShard],
) -> tuple[dict[str, object], ...]:
    records: list[dict[str, object]] = []
    for key in external_direct_calibration_keys():
        shard_id = f"kM={key.kM};sector={key.sector}"
        shard = shards[shard_id]
        try:
            ordinal = shard.keys.index(key)
        except ValueError as exc:
            raise BHPTConditionedComparisonError(
                f"conditioning shard lacks calibration key: {key.to_record()}"
            ) from exc
        names = key_artifact_filenames(ordinal, key)
        paths = {name: shard.root / filename for name, filename in names.items()}
        terminal = _read_json(paths["terminal"])
        checkpoint = _read_json(paths["checkpoint"])
        result = _read_json(paths["result"])
        payload = _read_json(paths["payload"])
        if (
            terminal.get("key") != key.to_record()
            or checkpoint.get("key") != key.to_record()
            or result.get("key") != key.to_record()
            or payload.get("key") != key.to_record()
            or not isinstance(payload.get("solver_payload"), Mapping)
        ):
            raise BHPTConditionedComparisonError("internal key linkage changed")
        identities = {name: _strict_file_identity(path) for name, path in paths.items()}
        if (
            terminal.get("checkpoint_identity") != identities["checkpoint"]
            or checkpoint.get("result_identity") != identities["result"]
            or result.get("payload_identity") != identities["payload"]
        ):
            raise BHPTConditionedComparisonError("internal artifact chain changed")
        records.append(
            {
                "acceptance_state": checkpoint.get("acceptance_state"),
                "artifact_identities": identities,
                "execution_status": terminal.get("execution_status"),
                "key": key.to_record(),
                "shard_id": shard_id,
                "solver_payload": dict(payload["solver_payload"]),
            }
        )
    return tuple(records)


def load_comparison_inputs(
    *,
    bhpt_root: str | Path,
    conditioning_campaign_root: str | Path,
    conditioning_shard_roots: Sequence[str | Path],
) -> dict[str, object]:
    """Strictly reload all immutable source evidence without running a solver."""

    external = _load_external_bhpt(bhpt_root)
    campaign = _load_conditioning_campaign(conditioning_campaign_root)
    shards = _map_and_validate_shards(
        conditioning_shard_roots,
        campaign_entries=campaign["entry_map"],  # type: ignore[arg-type]
    )
    internal_records = _load_internal_records(shards)
    shard_sources = [
        {
            "root": _root_descriptor(shards[shard_id].root),
            "shard": dict(shards[shard_id].shard),
            "top_identities": {
                name: dict(identity)
                for name, identity in shards[shard_id].top_identities.items()
            },
        }
        for shard_id in _expected_shard_ids()
    ]
    return {
        "external_evidence": external["evidence"],
        "external_payload": external["payload"],
        "internal_records": internal_records,
        "source_evidence": {
            "bhpt_direct": external["source"],
            "conditioning_campaign": campaign["source"],
            "conditioning_shards": shard_sources,
        },
    }


def _component(
    *,
    state: str,
    applicability: str,
    estimate: str | None,
    units: str | None,
    assessed_items: int,
    unassessed_items: int,
    reason: str,
) -> dict[str, object]:
    return {
        "applicability": applicability,
        "assessed_items": assessed_items,
        "estimate": estimate,
        "reason": reason,
        "state": state,
        "unassessed_items": unassessed_items,
        "units": units,
    }


def _aggregate_internal_component(
    records: Sequence[Mapping[str, object]], name: str
) -> dict[str, object]:
    values: list[Decimal] = []
    for record in records:
        if record["state"] != "PARTIAL":
            continue
        internal = record["internal"]
        if not isinstance(internal, Mapping):
            continue
        budget = internal.get("numerical_uncertainty_budget")
        components = budget.get("components") if isinstance(budget, Mapping) else None
        if not isinstance(components, Mapping):
            continue
        value = _decimal(components[name], f"internal numerical {name}")
        if value != FLOAT64_UNASSESSED_SENTINEL:
            values.append(value)
    assessed = len(values)
    return _component(
        state="PARTIAL" if values else "NOT_ASSESSED",
        applicability="REQUIRED",
        estimate=_decimal_text(max(values)) if values else None,
        units="dimensionless",
        assessed_items=assessed,
        unassessed_items=EXPECTED_KEY_COUNT - assessed,
        reason=(
            "maximum assessed conditioned-radial component; sentinel values and "
            "six failed modes remain unassessed"
        ),
    )


def _max_metric(
    records: Sequence[Mapping[str, object]],
    path: Sequence[str],
    *,
    partial_only: bool = True,
) -> str:
    values: list[Decimal] = []
    for record in records:
        if partial_only and record["state"] != "PARTIAL":
            continue
        value: object = record
        for name in path:
            if not isinstance(value, Mapping):
                raise BHPTConditionedComparisonError("comparison metric path changed")
            value = value[name]
        values.append(_decimal(value, ".".join(path)))
    expected_count = EXPECTED_PARTIAL_COUNT if partial_only else EXPECTED_KEY_COUNT
    if len(values) != expected_count:
        raise BHPTConditionedComparisonError("comparison metric coverage changed")
    return _decimal_text(max(values))


def _comparison_budgets(
    records: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], dict[str, object]]:
    numerical_components = {
        name: _aggregate_internal_component(records, name)
        for name in NUMERICAL_BUDGET_FIELDS
        if name != "backend_difference"
    }
    numerical_components["backend_difference"] = _component(
        state="PARTIAL",
        applicability="REQUIRED",
        estimate=_max_metric(
            records, ("metrics", "phase_factor", "complex_abs_difference")
        ),
        units="complex_absolute_difference",
        assessed_items=EXPECTED_PARTIAL_COUNT,
        unassessed_items=EXPECTED_FAIL_COUNT,
        reason="no-fit BHPT phase_factor versus conditioned S difference; no threshold frozen",
    )
    numerical = {
        "components": numerical_components,
        "cross_backend_diagnostics": {
            "external_flux_residual_abs_max": _max_metric(
                records,
                ("external", "selected_flux_unitarity_residual_abs"),
                partial_only=False,
            ),
            "external_matching_radius_phase_spread_abs_max": _max_metric(
                records,
                ("external", "matching_radius_phase_spread_abs"),
                partial_only=False,
            ),
            "internal_flux_residual_abs_max": _max_metric(
                records, ("internal", "flux_residual_abs")
            ),
            "phase_factor_complex_abs_difference_max": _max_metric(
                records, ("metrics", "phase_factor", "complex_abs_difference")
            ),
            "reflection_ratio_complex_abs_difference_max": _max_metric(
                records, ("metrics", "reflection_ratio", "complex_abs_difference")
            ),
            "transmission_modulus_abs_difference_max": _max_metric(
                records, ("metrics", "transmission_modulus_abs_difference")
            ),
        },
        "status": "FAIL",
    }
    convention_components = {
        name: _component(
            state="NOT_ASSESSED",
            applicability=(
                "NOT_APPLICABLE"
                if name in {"observer", "worldline", "tetrad", "polarization_basis"}
                else "REQUIRED"
            ),
            estimate=None,
            units=None,
            assessed_items=0,
            unassessed_items=EXPECTED_KEY_COUNT,
            reason=(
                "mode-level radial comparison has no local observer/polarization claim"
                if name in {"observer", "worldline", "tetrad", "polarization_basis"}
                else "not assessed by this comparison"
            ),
        )
        for name in CONVENTION_BUDGET_FIELDS
    }
    convention_components["phase_origin"] = _component(
        state="PARTIAL",
        applicability="REQUIRED",
        estimate=_max_metric(
            records,
            ("metrics", "phase_factor", "wrapped_phase_difference_abs_rad"),
        ),
        units="rad",
        assessed_items=EXPECTED_PARTIAL_COUNT,
        unassessed_items=EXPECTED_FAIL_COUNT,
        reason="absolute no-fit S/phase_factor comparison; horizon transmission phase remains open",
    )
    convention_components["total_scattered_definition"] = _component(
        state="PARTIAL",
        applicability="REQUIRED",
        estimate=_max_metric(
            records, ("metrics", "reflection_ratio", "complex_abs_difference")
        ),
        units="complex_absolute_difference",
        assessed_items=EXPECTED_PARTIAL_COUNT,
        unassessed_items=EXPECTED_FAIL_COUNT,
        reason="Reflection/Incidence is compared directly with conditioned A_out at A_in=1",
    )
    convention = {
        "components": convention_components,
        "status": "PARTIAL",
        "transmission_complex_phase": {
            "reason": (
                "the two horizon/master complex-phase normalization ledgers are not "
                "proven identical; only transmission modulus is compared"
            ),
            "state": "NOT_ASSESSED",
        },
    }
    return numerical, convention


def _compare_one(
    external: Mapping[str, object], internal: Mapping[str, object]
) -> dict[str, object]:
    key = RadialKey.from_record(
        {name: external[name] for name in ("ell", "kM", "sector")}
    )
    if internal.get("key") != key.to_record():
        raise BHPTConditionedComparisonError("external/internal key order changed")
    acceptance = internal.get("acceptance_state")
    execution = internal.get("execution_status")
    solver = internal.get("solver_payload")
    if not isinstance(solver, Mapping) or solver.get("key") != key.to_record():
        raise BHPTConditionedComparisonError("internal solver payload key changed")
    external_budget = external.get("numerical_uncertainty_budget")
    if not isinstance(external_budget, Mapping):
        raise BHPTConditionedComparisonError("external record budget missing")
    external_summary = {
        "matching_radius_phase_spread_abs": external_budget[
            "matching_radius_phase_spread_abs"
        ],
        "selected_flux_unitarity_residual_abs": external_budget[
            "selected_flux_unitarity_residual_abs"
        ],
        "values": {
            name: external[name]
            for name in ("phase_factor", "reflection_ratio", "transmission")
        },
    }
    base = {
        "acceptance_threshold_frozen": False,
        "artifact_identities": internal.get("artifact_identities", {}),
        "external": external_summary,
        "key": key.to_record(),
        "phase_or_normalization_fit": False,
        "shard_id": internal.get("shard_id"),
    }
    if acceptance == "FAIL" and execution == "COMPLETED_FAIL_CLOSED":
        failures = solver.get("failures")
        if not isinstance(failures, Mapping) or not failures:
            raise BHPTConditionedComparisonError("internal FAIL lacks diagnostics")
        return {
            **base,
            "failure": {
                "code": "INTERNAL_CONDITIONED_RADIAL_FAIL_CLOSED",
                "reasons": dict(failures),
            },
            "internal": {
                "acceptance_state": "FAIL",
                "convention_uncertainty_budget": solver.get("convention_budget"),
                "ladder_nodes": solver.get("ladder_nodes"),
                "numerical_uncertainty_budget": solver.get("numerical_budget"),
            },
            "metrics": {
                "phase_factor": None,
                "reflection_ratio": None,
                "transmission_complex": {
                    "reason": "internal conditioned radial solve failed closed",
                    "state": "NOT_ASSESSED",
                },
                "transmission_modulus_abs_difference": None,
            },
            "state": "FAIL",
        }
    if acceptance != "PARTIAL" or execution != "COMPLETED":
        raise BHPTConditionedComparisonError("internal terminal state changed")
    results = solver.get("results")
    baseline = results.get("baseline") if isinstance(results, Mapping) else None
    if not isinstance(baseline, Mapping):
        raise BHPTConditionedComparisonError("internal PARTIAL lacks baseline result")
    diagnostics = baseline.get("diagnostics")
    if not isinstance(diagnostics, Mapping) or (
        diagnostics.get("normalization_definition")
        != "A_in set exactly to one after Jost ratio"
        or diagnostics.get("outer_basis") != "jost_1_over_r"
        or diagnostics.get("paper_specific_envelope_used") is not False
        or diagnostics.get("scientific_acceptance") is not False
    ):
        raise BHPTConditionedComparisonError("internal normalization ledger changed")
    a_in = _complex(baseline.get("A_in"), "internal A_in")
    _close_complex(a_in, DecimalComplex(Decimal(1), Decimal(0)), label="A_in=1")
    a_out = _complex(baseline.get("A_out"), "internal A_out")
    internal_s = _complex(baseline.get("S"), "internal S")
    expected_s = a_out.scale(-((-1) ** key.ell))
    _close_complex(internal_s, expected_s, label="internal S definition")
    internal_t = _complex(baseline.get("T_horizon"), "internal T_horizon")
    external_s = _complex(external.get("phase_factor"), "external phase_factor")
    external_r = _complex(external.get("reflection_ratio"), "external reflection_ratio")
    external_t = _complex(external.get("transmission"), "external transmission")
    phase_metric = _metric(external_s, internal_s)
    reflection_metric = _metric(external_r, a_out)
    transmission_modulus = abs(external_t.absolute() - internal_t.absolute())
    flux_residual = _decimal(diagnostics.get("flux_residual"), "internal flux residual")
    return {
        **base,
        "failure": None,
        "internal": {
            "acceptance_state": "PARTIAL",
            "convention_uncertainty_budget": solver.get("convention_budget"),
            "flux_residual_abs": _decimal_text(abs(flux_residual)),
            "ladder_nodes": solver.get("ladder_nodes"),
            "numerical_uncertainty_budget": solver.get("numerical_budget"),
            "values": {
                "A_out": baseline.get("A_out"),
                "S": baseline.get("S"),
                "T_horizon": baseline.get("T_horizon"),
            },
        },
        "metrics": {
            "phase_factor": phase_metric,
            "reflection_ratio": reflection_metric,
            "transmission_complex": {
                "reason": (
                    "horizon/master complex-phase normalization equivalence is not "
                    "closed; no fitted phase is allowed"
                ),
                "state": "NOT_ASSESSED",
            },
            "transmission_modulus_abs_difference": _decimal_text(transmission_modulus),
        },
        "state": "PARTIAL",
    }


def _implementation_identities(
    supplied: Mapping[str, Mapping[str, object]] | None,
) -> dict[str, Mapping[str, object]]:
    identities = (
        {
            "comparison_module": source_file_identity(COMPARISON_MODULE_PATH),
            "comparison_runner": source_file_identity(COMPARISON_RUNNER_PATH),
        }
        if supplied is None
        else {name: dict(identity) for name, identity in supplied.items()}
    )
    if set(identities) != {"comparison_module", "comparison_runner"}:
        raise BHPTConditionedComparisonError(
            "comparison implementation inventory changed"
        )
    for name, identity in identities.items():
        if not isinstance(identity, Mapping):
            raise BHPTConditionedComparisonError("implementation identity is malformed")
        _sha(identity.get("sha256"), f"{name} source hash")
    return identities


def _validate_hash_ledger(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or not value:
        raise BHPTConditionedComparisonError(f"{label} hash ledger is missing")
    for name, digest in value.items():
        if not isinstance(name, str) or not name:
            raise BHPTConditionedComparisonError(f"{label} hash name changed")
        _sha(digest, f"{label} {name}")
    return value


def _validate_source_evidence(value: object) -> Mapping[str, object]:
    item = _exact(
        value,
        {"bhpt_direct", "conditioning_campaign", "conditioning_shards"},
        "comparison source evidence",
    )
    expected_files = {
        "bhpt_direct": {
            "evidence.json",
            "external_bhpt_direct.json",
            "manifest.json",
            "request.json",
        },
        "conditioning_campaign": {
            "conditioning_campaign_index.json",
            "manifest.json",
        },
    }
    for source_name in ("bhpt_direct", "conditioning_campaign"):
        source = _exact(
            item[source_name],
            {"files", "implementation_source_sha256s", "root"},
            f"{source_name} source",
        )
        root = _exact(source["root"], {"mode", "path"}, f"{source_name} root")
        if root["mode"] != FORMAL_ROOT_MODE or not isinstance(root["path"], str):
            raise BHPTConditionedComparisonError(
                f"{source_name} immutable root identity changed"
            )
        files = source["files"]
        if not isinstance(files, Mapping) or set(files) != expected_files[source_name]:
            raise BHPTConditionedComparisonError(
                f"{source_name} source artifact inventory changed"
            )
        for filename, identity in files.items():
            _identity_sha(identity, f"{source_name} {filename}")
        _validate_hash_ledger(
            source["implementation_source_sha256s"],
            f"{source_name} implementation",
        )
    shards = item["conditioning_shards"]
    if not isinstance(shards, list) or len(shards) != 8:
        raise BHPTConditionedComparisonError(
            "conditioning comparison shard provenance changed"
        )
    shard_ids: list[str] = []
    for index, raw_shard in enumerate(shards):
        shard = _exact(
            raw_shard,
            {"root", "shard", "top_identities"},
            f"conditioning source shard[{index}]",
        )
        root = _exact(
            shard["root"], {"mode", "path"}, f"conditioning shard[{index}] root"
        )
        descriptor = shard["shard"]
        if (
            root["mode"] != FORMAL_ROOT_MODE
            or not isinstance(root["path"], str)
            or not isinstance(descriptor, Mapping)
            or not isinstance(descriptor.get("shard_id"), str)
        ):
            raise BHPTConditionedComparisonError(
                "conditioning shard source identity changed"
            )
        shard_ids.append(str(descriptor["shard_id"]))
        identities = shard["top_identities"]
        if not isinstance(identities, Mapping) or set(identities) != {
            "manifest.json",
            "run_contract.json",
            "shard_checkpoint.json",
            "shard_result.json",
        }:
            raise BHPTConditionedComparisonError(
                "conditioning shard top identity inventory changed"
            )
        for filename, identity in identities.items():
            _identity_sha(identity, f"conditioning shard[{index}] {filename}")
    if tuple(shard_ids) != _expected_shard_ids():
        raise BHPTConditionedComparisonError(
            "conditioning shard source order/domain changed"
        )
    return item


def _all_implementation_hashes(
    comparison_identities: Mapping[str, Mapping[str, object]],
    source_evidence: Mapping[str, object],
) -> list[str]:
    validated_sources = _validate_source_evidence(source_evidence)
    hashes = {
        _identity_sha(identity, f"comparison implementation {name}")
        for name, identity in comparison_identities.items()
    }
    for source_name in ("bhpt_direct", "conditioning_campaign"):
        source = validated_sources[source_name]
        if not isinstance(source, Mapping):  # validated above; keeps typing explicit
            raise BHPTConditionedComparisonError("source ledger changed")
        ledger = _validate_hash_ledger(
            source["implementation_source_sha256s"],
            f"{source_name} implementation",
        )
        hashes.update(str(value) for value in ledger.values())
    return sorted(hashes)


def build_comparison_payload(
    *,
    comparison_id: str,
    external_payload: Mapping[str, object],
    internal_records: Sequence[Mapping[str, object]],
    source_evidence: Mapping[str, object],
    implementation_source_identities: Mapping[str, Mapping[str, object]] | None = None,
) -> dict[str, object]:
    """Build the exact 30-key comparison from already loaded source records."""

    _identifier(comparison_id, "comparison_id")
    try:
        validated = validate_external_payload(external_payload)
    except Exception as exc:
        raise BHPTConditionedComparisonError(
            "external payload validation failed"
        ) from exc
    if validated.get("status") != "PASS":
        raise BHPTConditionedComparisonError(
            "external payload is not source/method PASS"
        )
    external_records = external_payload.get("records")
    if not isinstance(external_records, list) or len(external_records) != 30:
        raise BHPTConditionedComparisonError("external 30-key record set changed")
    if len(internal_records) != 30:
        raise BHPTConditionedComparisonError("internal 30-key record set changed")
    expected = [key.to_record() for key in external_direct_calibration_keys()]
    external_keys = [
        {name: record[name] for name in ("ell", "kM", "sector")}
        for record in external_records
        if isinstance(record, Mapping)
    ]
    internal_keys = [record.get("key") for record in internal_records]
    if external_keys != expected or internal_keys != expected:
        raise BHPTConditionedComparisonError("comparison key order/hash domain changed")
    records = [
        _compare_one(external, internal)
        for external, internal in zip(external_records, internal_records, strict=True)
    ]
    fail_keys = {
        RadialKey.from_record(record["key"])
        for record in records
        if record["state"] == "FAIL"
    }
    if fail_keys != _EXPECTED_FAIL_KEYS:
        raise BHPTConditionedComparisonError(
            "the six frozen internal fail-closed keys were hidden or changed"
        )
    counts = Counter(str(record["state"]) for record in records)
    if counts != Counter({"PARTIAL": 24, "FAIL": 6}):
        raise BHPTConditionedComparisonError("comparison state counts changed")
    numerical, convention = _comparison_budgets(records)
    identities = _implementation_identities(implementation_source_identities)
    validated_sources = _validate_source_evidence(source_evidence)
    payload = {
        "acceptance_scope": COMPARISON_SCOPE,
        "comparison_id": comparison_id,
        "comparison_status_counts": {
            "FAIL": counts["FAIL"],
            "NOT_ASSESSED": 0,
            "PARTIAL": counts["PARTIAL"],
            "PASS": 0,
        },
        "contract_only": False,
        "convention_uncertainty_budget": convention,
        "domain": {
            "count": EXPECTED_KEY_COUNT,
            "key_list_sha256": EXPECTED_KEY_LIST_SHA256,
            "purpose": COMPARISON_SCOPE,
        },
        "even_sector_qualification": {
            "external_even_direct_radial_solution": True,
            "external_even_independent_mst": False,
            "parity_derived_even_used": False,
        },
        "full_paper_figure_rerun": False,
        "global_green_permitted": False,
        "implementation_source_identities": identities,
        "implementation_source_sha256s": {
            name: identity["sha256"] for name, identity in identities.items()
        },
        "kernel_unit_test_only": False,
        "li_figure_agreement_primary_gate": False,
        "no_phase_or_normalization_fit": True,
        "numerical_uncertainty_budget": numerical,
        "overall_state": "FAIL",
        "paper_agreement_gate": False,
        "release_projection": {
            "gate": "V1",
            "independence_class": "EXTERNAL_SOURCE",
            "observable": "radial_s_matrix_flux",
            "report_schema": TYPED_RESULT_SCHEMA,
            "role": "INDEPENDENT_SCIENCE",
        },
        "records": records,
        "schema": COMPARISON_SCHEMA,
        "science_executed": True,
        "scientific_acceptance": False,
        "scientific_evidence": True,
        "source_evidence": dict(validated_sources),
        "source_role_ledger": {
            "comparison_result": {
                "composite_consumer": True,
                "independence_class": "EXTERNAL_SOURCE",
                "release_role": "INDEPENDENT_SCIENCE",
            },
            "external_bhpt_direct": {
                "evidence_key": "bhpt_direct",
                "evidence_role": "INDEPENDENT_EXTERNAL_REFERENCE",
                "even_sector_method": "INDEPENDENT_DIRECT_ZERILLI_NOT_MST",
                "independence_class": "EXTERNAL_SOURCE",
            },
            "internal_schwo_conditioned_radial": {
                "evidence_key": "conditioning_campaign",
                "evidence_role": "PRIMARY_PROJECT_AMPLITUDE",
                "independence_class": "SAME_IMPLEMENTATION",
            },
        },
        "status": "COMPLETE_WITH_INTERNAL_SCIENTIFIC_FAILURES",
        "transmission_comparison_qualification": {
            "complex_amplitude": "NOT_ASSESSED",
            "modulus": "PARTIAL_NO_THRESHOLD",
            "reason": (
                "unit-incoming flux moduli are compared, but identical horizon/master "
                "complex-phase normalization is not proven"
            ),
        },
    }
    validate_comparison_payload(payload)
    return payload


def validate_comparison_payload(payload: object) -> Mapping[str, object]:
    """Validate release fields and fail-closed 24/6 scientific accounting."""

    fields = {
        "acceptance_scope",
        "comparison_id",
        "comparison_status_counts",
        "contract_only",
        "convention_uncertainty_budget",
        "domain",
        "even_sector_qualification",
        "full_paper_figure_rerun",
        "global_green_permitted",
        "implementation_source_identities",
        "implementation_source_sha256s",
        "kernel_unit_test_only",
        "li_figure_agreement_primary_gate",
        "no_phase_or_normalization_fit",
        "numerical_uncertainty_budget",
        "overall_state",
        "paper_agreement_gate",
        "release_projection",
        "records",
        "schema",
        "science_executed",
        "scientific_acceptance",
        "scientific_evidence",
        "source_evidence",
        "source_role_ledger",
        "status",
        "transmission_comparison_qualification",
    }
    item = _exact(payload, fields, "comparison payload")
    if (
        item["schema"] != COMPARISON_SCHEMA
        or item["acceptance_scope"] != COMPARISON_SCOPE
        or item["overall_state"] != "FAIL"
        or item["status"] != "COMPLETE_WITH_INTERNAL_SCIENTIFIC_FAILURES"
        or item["scientific_evidence"] is not True
        or item["science_executed"] is not True
        or item["scientific_acceptance"] is not False
        or item["kernel_unit_test_only"] is not False
        or item["contract_only"] is not False
        or item["global_green_permitted"] is not False
        or item["li_figure_agreement_primary_gate"] is not False
        or item["paper_agreement_gate"] is not False
        or item["full_paper_figure_rerun"] is not False
        or item["no_phase_or_normalization_fit"] is not True
    ):
        raise BHPTConditionedComparisonError("comparison release policy changed")
    _identifier(item["comparison_id"], "comparison_id")
    if item["domain"] != {
        "count": 30,
        "key_list_sha256": EXPECTED_KEY_LIST_SHA256,
        "purpose": COMPARISON_SCOPE,
    }:
        raise BHPTConditionedComparisonError("comparison domain changed")
    if item["comparison_status_counts"] != {
        "FAIL": 6,
        "NOT_ASSESSED": 0,
        "PARTIAL": 24,
        "PASS": 0,
    }:
        raise BHPTConditionedComparisonError("comparison status counts changed")
    if item["release_projection"] != {
        "gate": "V1",
        "independence_class": "EXTERNAL_SOURCE",
        "observable": "radial_s_matrix_flux",
        "report_schema": TYPED_RESULT_SCHEMA,
        "role": "INDEPENDENT_SCIENCE",
    }:
        raise BHPTConditionedComparisonError("typed release projection changed")
    if item["source_role_ledger"] != {
        "comparison_result": {
            "composite_consumer": True,
            "independence_class": "EXTERNAL_SOURCE",
            "release_role": "INDEPENDENT_SCIENCE",
        },
        "external_bhpt_direct": {
            "evidence_key": "bhpt_direct",
            "evidence_role": "INDEPENDENT_EXTERNAL_REFERENCE",
            "even_sector_method": "INDEPENDENT_DIRECT_ZERILLI_NOT_MST",
            "independence_class": "EXTERNAL_SOURCE",
        },
        "internal_schwo_conditioned_radial": {
            "evidence_key": "conditioning_campaign",
            "evidence_role": "PRIMARY_PROJECT_AMPLITUDE",
            "independence_class": "SAME_IMPLEMENTATION",
        },
    }:
        raise BHPTConditionedComparisonError("comparison source-role ledger changed")
    records = item["records"]
    if not isinstance(records, list) or len(records) != 30:
        raise BHPTConditionedComparisonError("comparison records changed")
    if [record.get("key") for record in records if isinstance(record, Mapping)] != [
        key.to_record() for key in external_direct_calibration_keys()
    ]:
        raise BHPTConditionedComparisonError("comparison record order changed")
    fail_keys: set[RadialKey] = set()
    for record in records:
        if not isinstance(record, Mapping) or record.get("state") not in {
            "PARTIAL",
            "FAIL",
        }:
            raise BHPTConditionedComparisonError("comparison record state changed")
        metrics = record.get("metrics")
        if not isinstance(metrics, Mapping):
            raise BHPTConditionedComparisonError("comparison record metrics missing")
        transmission = metrics.get("transmission_complex")
        if (
            not isinstance(transmission, Mapping)
            or transmission.get("state") != "NOT_ASSESSED"
        ):
            raise BHPTConditionedComparisonError(
                "complex transmission was promoted without a normalization ledger"
            )
        key = RadialKey.from_record(record["key"])
        if record["state"] == "FAIL":
            fail_keys.add(key)
            if record.get("failure") is None:
                raise BHPTConditionedComparisonError("FAIL record lacks diagnostics")
        elif record.get("failure") is not None:
            raise BHPTConditionedComparisonError("PARTIAL record carries failure")
    if fail_keys != _EXPECTED_FAIL_KEYS:
        raise BHPTConditionedComparisonError("frozen failure inventory changed")
    numerical = item["numerical_uncertainty_budget"]
    convention = item["convention_uncertainty_budget"]
    if (
        not isinstance(numerical, Mapping)
        or numerical.get("status") != "FAIL"
        or not isinstance(numerical.get("components"), Mapping)
        or set(numerical["components"]) != set(NUMERICAL_BUDGET_FIELDS)
        or not isinstance(convention, Mapping)
        or convention.get("status") != "PARTIAL"
        or not isinstance(convention.get("components"), Mapping)
        or set(convention["components"]) != set(CONVENTION_BUDGET_FIELDS)
    ):
        raise BHPTConditionedComparisonError("separate uncertainty budgets changed")
    identities = item["implementation_source_identities"]
    hashes = item["implementation_source_sha256s"]
    if not isinstance(identities, Mapping) or not isinstance(hashes, Mapping):
        raise BHPTConditionedComparisonError("implementation provenance missing")
    if set(identities) != set(hashes) or any(
        not isinstance(identity, Mapping)
        or _sha(identity.get("sha256"), "implementation identity hash") != hashes[name]
        for name, identity in identities.items()
    ):
        raise BHPTConditionedComparisonError("implementation provenance changed")
    _all_implementation_hashes(identities, item["source_evidence"])
    return item


def _typed_budget_projection(
    native: object,
    fields: Sequence[str],
    label: str,
) -> dict[str, dict[str, object]]:
    if not isinstance(native, Mapping) or not isinstance(
        native.get("components"), Mapping
    ):
        raise BHPTConditionedComparisonError(f"{label} native budget changed")
    components = native["components"]
    if set(components) != set(fields):
        raise BHPTConditionedComparisonError(f"{label} component inventory changed")
    projected: dict[str, dict[str, object]] = {}
    for name in fields:
        component = components[name]
        if not isinstance(component, Mapping) or set(component) != {
            "applicability",
            "assessed_items",
            "estimate",
            "reason",
            "state",
            "unassessed_items",
            "units",
        }:
            raise BHPTConditionedComparisonError(
                f"{label}.{name} native component changed"
            )
        state = component["state"]
        if state not in {"PASS", "PARTIAL", "FAIL", "NOT_ASSESSED"}:
            raise BHPTConditionedComparisonError(f"{label}.{name} state changed")
        estimate = component["estimate"]
        if estimate is not None:
            estimate = _decimal_text(_decimal(estimate, f"{label}.{name} estimate"))
        units = component["units"]
        if units is None:
            units = "dimensionless"
        if not isinstance(units, str) or not units:
            raise BHPTConditionedComparisonError(f"{label}.{name} units changed")
        applicability = component["applicability"]
        assessed = component["assessed_items"]
        unassessed = component["unassessed_items"]
        reason = component["reason"]
        if (
            applicability not in {"REQUIRED", "NOT_APPLICABLE"}
            or isinstance(assessed, bool)
            or not isinstance(assessed, int)
            or isinstance(unassessed, bool)
            or not isinstance(unassessed, int)
            or assessed < 0
            or unassessed < 0
            or assessed + unassessed != EXPECTED_KEY_COUNT
            or not isinstance(reason, str)
            or not reason
        ):
            raise BHPTConditionedComparisonError(
                f"{label}.{name} coverage/reason changed"
            )
        projected[name] = {
            "estimate": estimate,
            "reason": (
                f"{reason}; applicability={applicability}; "
                f"assessed_items={assessed}; unassessed_items={unassessed}"
            ),
            "state": state,
            "units": units,
        }
    return projected


def _typed_domain() -> dict[str, object]:
    ell_by_km: dict[str, list[int]] = {}
    for key in external_direct_calibration_keys():
        values = ell_by_km.setdefault(key.kM, [])
        if key.ell not in values:
            values.append(key.ell)
    return {
        "description": (
            "frozen 30-key BHPT direct versus SchWO conditioned-radial "
            "cross-backend calibration domain"
        ),
        "domain_id": "bhpt_direct_conditioned_selected_30",
        "expected_item_ids": list(_EXPECTED_ITEM_IDS),
        "expected_items": EXPECTED_KEY_COUNT,
        "parameters": {
            "ell_by_kM": ell_by_km,
            "external_direct_key_list_sha256": EXPECTED_KEY_LIST_SHA256,
            "kM": sorted(ell_by_km, key=Decimal),
            "sectors": ["even", "odd"],
        },
        "selection_policy": (
            "exact D_external_direct_calibration v4 key inventory; selected-only, "
            "not full production-domain coverage"
        ),
    }


def _build_typed_report_unchecked(
    comparison: Mapping[str, object],
    *,
    comparison_sha256: str,
) -> dict[str, object]:
    records = comparison["records"]
    if not isinstance(records, list):
        raise BHPTConditionedComparisonError("comparison records changed")
    item_results = sorted(
        (
            {
                "item_id": _item_id(RadialKey.from_record(record["key"])),
                "state": record["state"],
            }
            for record in records
            if isinstance(record, Mapping)
        ),
        key=lambda item: str(item["item_id"]),
    )
    identities = comparison["implementation_source_identities"]
    sources = comparison["source_evidence"]
    if not isinstance(identities, Mapping) or not isinstance(sources, Mapping):
        raise BHPTConditionedComparisonError("comparison provenance changed")
    return {
        "convention_uncertainty_budget": _typed_budget_projection(
            comparison["convention_uncertainty_budget"],
            CONVENTION_BUDGET_FIELDS,
            "typed convention",
        ),
        "full_paper_figure_rerun": False,
        "gate": "V1",
        "global_green_permitted": False,
        "implementation_source_sha256s": _all_implementation_hashes(
            identities, sources
        ),
        "independence_class": "EXTERNAL_SOURCE",
        "item_results": item_results,
        "kernel_unit_test_only": False,
        "li_figure_agreement_primary_gate": False,
        "limitations": [
            (
                "selected 30-key calibration only; this is not full conditioning "
                "or production-domain acceptance"
            ),
            (
                "24 comparable keys remain PARTIAL because no numerical acceptance "
                "threshold is frozen; no item is PASS"
            ),
            (
                "six conditioned-radial internal failures remain FAIL: "
                "(kM,ell)=(1,20),(2,60),(4,120) in both parity sectors"
            ),
            (
                "complex horizon transmission is NOT_ASSESSED because identical "
                "master/horizon phase normalization is not proven; only its modulus "
                "is compared"
            ),
            (
                "the external even sector is an independently integrated Zerilli "
                "radial solution, not an independently implemented even-sector MST"
            ),
            (
                "this composite cross-check consumes both external BHPT and internal "
                "SchWO amplitudes and must not be presented as a standalone external "
                "domain-wide acceptance result"
            ),
            f"native comparison.json sha256={comparison_sha256}",
        ],
        "numerical_uncertainty_budget": _typed_budget_projection(
            comparison["numerical_uncertainty_budget"],
            NUMERICAL_BUDGET_FIELDS,
            "typed numerical",
        ),
        "observable": "radial_s_matrix_flux",
        "observer_qualification": {
            "detector_response_claim_permitted": False,
            "output_kind": "RADIAL_S_MATRIX_CROSS_BACKEND_COMPARISON",
            "worldline_tetrad_pure_gauge_test": "NOT_ASSESSED",
        },
        "parameter_domain": _typed_domain(),
        "reason": (
            "24 no-threshold cross-backend comparisons are PARTIAL and six "
            "conditioned-radial modes fail closed"
        ),
        "result_id": comparison["comparison_id"],
        "role": "INDEPENDENT_SCIENCE",
        "schema": TYPED_RESULT_SCHEMA,
        "science_executed": True,
        "scientific_evidence": True,
        "state": "FAIL",
    }


def validate_typed_report(
    report: object,
    *,
    comparison: Mapping[str, object],
    comparison_sha256: str,
) -> Mapping[str, object]:
    """Validate the exact release-preparation typed-result projection."""

    validate_comparison_payload(comparison)
    digest = _sha(comparison_sha256, "native comparison hash")
    expected = _build_typed_report_unchecked(comparison, comparison_sha256=digest)
    fields = {
        "convention_uncertainty_budget",
        "full_paper_figure_rerun",
        "gate",
        "global_green_permitted",
        "implementation_source_sha256s",
        "independence_class",
        "item_results",
        "kernel_unit_test_only",
        "li_figure_agreement_primary_gate",
        "limitations",
        "numerical_uncertainty_budget",
        "observable",
        "observer_qualification",
        "parameter_domain",
        "reason",
        "result_id",
        "role",
        "schema",
        "science_executed",
        "scientific_evidence",
        "state",
    }
    item = _exact(report, fields, "typed comparison report")
    if item != expected:
        raise BHPTConditionedComparisonError(
            "typed report differs from its native comparison"
        )
    if [record["item_id"] for record in item["item_results"]] != list(
        _EXPECTED_ITEM_IDS
    ):
        raise BHPTConditionedComparisonError("typed item inventory changed")
    states = Counter(str(record["state"]) for record in item["item_results"])
    if states != Counter({"PARTIAL": 24, "FAIL": 6}) or item["state"] != "FAIL":
        raise BHPTConditionedComparisonError("typed 24/6 fail-closed state changed")
    return item


def build_typed_report(
    comparison: Mapping[str, object],
    *,
    comparison_sha256: str,
) -> dict[str, object]:
    """Build an exact ``TYPED_PHYSICAL_RESULT_V1`` report from native detail."""

    validate_comparison_payload(comparison)
    digest = _sha(comparison_sha256, "native comparison hash")
    report = _build_typed_report_unchecked(comparison, comparison_sha256=digest)
    validate_typed_report(report, comparison=comparison, comparison_sha256=digest)
    return report


def build_bhpt_conditioned_comparison(
    *,
    comparison_id: str,
    bhpt_root: str | Path,
    conditioning_campaign_root: str | Path,
    conditioning_shard_roots: Sequence[str | Path],
    implementation_source_identities: Mapping[str, Mapping[str, object]] | None = None,
) -> dict[str, object]:
    """Reload immutable evidence and build the comparison without writing."""

    loaded = load_comparison_inputs(
        bhpt_root=bhpt_root,
        conditioning_campaign_root=conditioning_campaign_root,
        conditioning_shard_roots=conditioning_shard_roots,
    )
    return build_comparison_payload(
        comparison_id=comparison_id,
        external_payload=loaded["external_payload"],  # type: ignore[arg-type]
        internal_records=loaded["internal_records"],  # type: ignore[arg-type]
        source_evidence=loaded["source_evidence"],  # type: ignore[arg-type]
        implementation_source_identities=implementation_source_identities,
    )


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _publish_exclusive(path: Path, payload: object) -> dict[str, object]:
    data = canonical_json_bytes(payload)
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
    os.chmod(path, FORMAL_FILE_MODE)
    _fsync_directory(path.parent)
    identity = _strict_file_identity(path)
    if identity["sha256"] != hashlib.sha256(data).hexdigest():
        raise BHPTConditionedComparisonError("published bytes changed")
    return identity


def _fresh_output_root(path: str | Path) -> Path:
    root = Path(path)
    if not root.is_absolute() or root.resolve(strict=False) != root:
        raise BHPTConditionedComparisonError("output root must be absolute/canonical")
    if root.exists() or root.is_symlink():
        raise FileExistsError("comparison output root must be fresh")
    parent = root.parent.resolve(strict=True)
    if (
        parent != root.parent
        or not parent.is_dir()
        or any(component.is_symlink() for component in (parent, *parent.parents))
    ):
        raise BHPTConditionedComparisonError("output parent is aliased/unavailable")
    os.mkdir(root, 0o700)
    _fsync_directory(parent)
    return root


def preflight_bhpt_conditioned_comparison(
    *,
    comparison_id: str,
    bhpt_root: str | Path,
    conditioning_campaign_root: str | Path,
    conditioning_shard_roots: Sequence[str | Path],
) -> dict[str, object]:
    """Strict no-write preflight for the 30-key comparison."""

    payload = build_bhpt_conditioned_comparison(
        comparison_id=comparison_id,
        bhpt_root=bhpt_root,
        conditioning_campaign_root=conditioning_campaign_root,
        conditioning_shard_roots=conditioning_shard_roots,
    )
    comparison_sha256 = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    report = build_typed_report(payload, comparison_sha256=comparison_sha256)
    return {
        "comparison_id": comparison_id,
        "comparison_payload_sha256": comparison_sha256,
        "comparison_status_counts": payload["comparison_status_counts"],
        "output_written": False,
        "overall_state": payload["overall_state"],
        "report_sha256": hashlib.sha256(canonical_json_bytes(report)).hexdigest(),
        "report_schema": report["schema"],
        "status": payload["status"],
    }


def publish_bhpt_conditioned_comparison(
    output_root: str | Path,
    *,
    comparison_id: str,
    bhpt_root: str | Path,
    conditioning_campaign_root: str | Path,
    conditioning_shard_roots: Sequence[str | Path],
) -> dict[str, object]:
    """Publish a fresh immutable comparison root; never overwrite or retry it."""

    payload = build_bhpt_conditioned_comparison(
        comparison_id=comparison_id,
        bhpt_root=bhpt_root,
        conditioning_campaign_root=conditioning_campaign_root,
        conditioning_shard_roots=conditioning_shard_roots,
    )
    root = _fresh_output_root(output_root)
    try:
        comparison_identity = _publish_exclusive(root / "comparison.json", payload)
        report = build_typed_report(
            payload,
            comparison_sha256=str(comparison_identity["sha256"]),
        )
        report_identity = _publish_exclusive(root / "report.json", report)
        manifest = {
            "comparison_identity": comparison_identity,
            "comparison_status_counts": {
                "FAIL": EXPECTED_FAIL_COUNT,
                "NOT_ASSESSED": 0,
                "PARTIAL": EXPECTED_PARTIAL_COUNT,
                "PASS": 0,
            },
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "global_green_permitted": False,
            "key_count": EXPECTED_KEY_COUNT,
            "li_figure_agreement_primary_gate": False,
            "overall_state": "FAIL",
            "release_projection": dict(payload["release_projection"]),
            "report_identity": report_identity,
            "schema": MANIFEST_SCHEMA,
            "source_role_ledger": dict(payload["source_role_ledger"]),
            "status": "COMPLETE_WITH_INTERNAL_SCIENTIFIC_FAILURES",
        }
        manifest_identity = _publish_exclusive(root / "manifest.json", manifest)
        os.chmod(root, FORMAL_ROOT_MODE)
        _fsync_directory(root)
        _fsync_directory(root.parent)
        validate_published_bhpt_conditioned_comparison(root)
    except BaseException:
        for child in root.iterdir():
            if child.is_file() and not child.is_symlink():
                os.chmod(child, FORMAL_FILE_MODE)
        os.chmod(root, FORMAL_ROOT_MODE)
        _fsync_directory(root)
        _fsync_directory(root.parent)
        raise
    return {
        "comparison_identity": comparison_identity,
        "evidence_root": str(root),
        "manifest_identity": manifest_identity,
        "overall_state": "FAIL",
        "report_identity": report_identity,
        "status": payload["status"],
    }


def validate_published_bhpt_conditioned_comparison(root_path: str | Path) -> None:
    """Reload the immutable root and independently rebuild the comparison."""

    root = _direct_root(root_path, "BHPT/conditioned comparison root")
    if {child.name for child in root.iterdir()} != {
        "comparison.json",
        "manifest.json",
        "report.json",
    }:
        raise BHPTConditionedComparisonError("comparison root inventory changed")
    comparison_path = root / "comparison.json"
    payload = _read_json(comparison_path)
    validate_comparison_payload(payload)
    comparison_identity = _strict_file_identity(comparison_path)
    report_path = root / "report.json"
    report = _read_json(report_path)
    report_identity = _strict_file_identity(report_path)
    validate_typed_report(
        report,
        comparison=payload,
        comparison_sha256=str(comparison_identity["sha256"]),
    )
    manifest = _exact(
        _read_json(root / "manifest.json"),
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
        "comparison manifest",
    )
    if (
        manifest["schema"] != MANIFEST_SCHEMA
        or manifest["comparison_identity"] != comparison_identity
        or manifest["report_identity"] != report_identity
        or manifest["comparison_status_counts"]
        != {
            "FAIL": 6,
            "NOT_ASSESSED": 0,
            "PARTIAL": 24,
            "PASS": 0,
        }
        or manifest["global_green_permitted"] is not False
        or manifest["li_figure_agreement_primary_gate"] is not False
        or manifest["key_count"] != 30
        or manifest["overall_state"] != "FAIL"
        or manifest["release_projection"] != payload["release_projection"]
        or manifest["source_role_ledger"] != payload["source_role_ledger"]
        or manifest["status"] != "COMPLETE_WITH_INTERNAL_SCIENTIFIC_FAILURES"
    ):
        raise BHPTConditionedComparisonError("comparison manifest changed")
    sources = payload["source_evidence"]
    if not isinstance(sources, Mapping):
        raise BHPTConditionedComparisonError("comparison source ledger missing")
    bhpt = sources.get("bhpt_direct")
    campaign = sources.get("conditioning_campaign")
    shards = sources.get("conditioning_shards")
    if (
        not isinstance(bhpt, Mapping)
        or not isinstance(bhpt.get("root"), Mapping)
        or not isinstance(campaign, Mapping)
        or not isinstance(campaign.get("root"), Mapping)
        or not isinstance(shards, list)
    ):
        raise BHPTConditionedComparisonError("comparison source roots changed")
    shard_roots = []
    for shard in shards:
        if not isinstance(shard, Mapping) or not isinstance(shard.get("root"), Mapping):
            raise BHPTConditionedComparisonError("comparison shard source changed")
        shard_roots.append(shard["root"].get("path"))
    rebuilt = build_bhpt_conditioned_comparison(
        comparison_id=str(payload["comparison_id"]),
        bhpt_root=str(bhpt["root"].get("path")),
        conditioning_campaign_root=str(campaign["root"].get("path")),
        conditioning_shard_roots=shard_roots,
    )
    if rebuilt != payload:
        raise BHPTConditionedComparisonError(
            "published comparison differs from strict source rebuild"
        )
    rebuilt_report = build_typed_report(
        rebuilt,
        comparison_sha256=str(comparison_identity["sha256"]),
    )
    if rebuilt_report != report:
        raise BHPTConditionedComparisonError(
            "published typed report differs from strict source rebuild"
        )


__all__ = [
    "BHPTConditionedComparisonError",
    "COMPARISON_SCHEMA",
    "MANIFEST_SCHEMA",
    "TYPED_RESULT_SCHEMA",
    "build_bhpt_conditioned_comparison",
    "build_comparison_payload",
    "build_typed_report",
    "load_comparison_inputs",
    "preflight_bhpt_conditioned_comparison",
    "publish_bhpt_conditioned_comparison",
    "validate_comparison_payload",
    "validate_published_bhpt_conditioned_comparison",
    "validate_typed_report",
]
