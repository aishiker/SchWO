"""Compose the original and repaired exact-eight-radius production states."""

from __future__ import annotations

from collections.abc import Mapping
import json
import os
from pathlib import Path
import re
import stat

from schwgw.validation.phase6_domain import canonical_json_bytes, source_file_identity
from schwgw.validation.phase6_production_finite_radius import (
    load_frozen_production_contract,
)
from schwgw.validation.phase6_production_finite_radius_campaign import (
    validate_campaign_result,
)
from schwgw.validation.phase6_production_finite_radius_repair import (
    EXPECTED_CAMPAIGN_MANIFEST_SHA256,
    EXPECTED_CAMPAIGN_RESULT_SHA256,
    EXPECTED_FAILURE_COUNT,
    load_repair_inventory,
    repair_key_id,
    validate_repair_record,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOMAIN_ROOT = PROJECT_ROOT / "runs/phase6/v1_domain_freeze_v3_20260806"
EXECUTION_ROOT = PROJECT_ROOT / "runs/phase6/v1_execution_contract_v4_20260806"
SOURCE_CAMPAIGN_SCHEMA = "schwgw_phase6_production_finite_radius_campaign_v1"
SOURCE_CAMPAIGN_MANIFEST_SCHEMA = (
    "schwgw_phase6_production_finite_radius_campaign_manifest_v1"
)
REPAIR_CONTRACT_SCHEMA = "schwgw.phase6.production_finite_radius_repair_contract.v1"
REPAIR_RESULT_SCHEMA = "schwgw.phase6.production_finite_radius_repair_result.v1"
REPAIR_MANIFEST_SCHEMA = "schwgw.phase6.production_finite_radius_repair_manifest.v1"
TYPED_RESULT_SCHEMA = "schwgw_phase6_v1_typed_physical_result_v1"
LEDGER_SCHEMA = "schwgw_phase6_v1_production_state_source_ledger_v1"
MANIFEST_SCHEMA = "schwgw_phase6_v1_production_state_evidence_manifest_v1"
EXPECTED_KEYS = 16_048
EXPECTED_ORIGINAL_STATES = 12_666
EXPECTED_REPAIRED_STATES = 3_382
FORMAL_ROOT_MODE = 0o555
FORMAL_FILE_MODE = 0o444
_SHA256 = re.compile(r"[0-9a-f]{64}")


class V1ProductionStateEvidenceError(ValueError):
    """Raised when the production-state repair composition drifts."""


def _implementation_hash_values(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, Mapping) or not value:
        raise V1ProductionStateEvidenceError(f"{label} ledger is missing")
    hashes = tuple(sorted(set(str(item) for item in value.values())))
    if any(_SHA256.fullmatch(item) is None for item in hashes):
        raise V1ProductionStateEvidenceError(f"{label} contains a non-SHA256 value")
    return hashes


def _strict_json(path: Path) -> Mapping[str, object]:
    identity = source_file_identity(path)
    if identity["mode"] != FORMAL_FILE_MODE or identity["nlink"] != 1:
        raise V1ProductionStateEvidenceError(f"non-immutable artifact: {path}")
    raw = path.read_bytes()
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise V1ProductionStateEvidenceError(f"invalid JSON: {path}") from exc
    if not isinstance(payload, Mapping) or raw != canonical_json_bytes(payload):
        raise V1ProductionStateEvidenceError(f"noncanonical JSON: {path}")
    return payload


def _direct_root(path: str | Path, label: str) -> Path:
    root = Path(path).absolute()
    info = root.lstat()
    if (
        root.is_symlink()
        or root.resolve(strict=True) != root
        or not stat.S_ISDIR(info.st_mode)
        or stat.S_IMODE(info.st_mode) != FORMAL_ROOT_MODE
    ):
        raise V1ProductionStateEvidenceError(f"{label} root is not immutable 0555")
    return root


def _record_filename(mode: object) -> str:
    token = mode.key.kM.replace(".", "p")
    return (
        f"record_{mode.ordinal:04d}__k{token}__{mode.key.sector}"
        f"__ell{mode.key.ell:04d}.json"
    )


def _validate_campaign(root: Path) -> Mapping[str, object]:
    result_path = root / "campaign_result.json"
    manifest_path = root / "manifest.json"
    if (
        source_file_identity(result_path)["sha256"] != EXPECTED_CAMPAIGN_RESULT_SHA256
        or source_file_identity(manifest_path)["sha256"]
        != EXPECTED_CAMPAIGN_MANIFEST_SHA256
        or set(path.name for path in root.iterdir())
        != {"campaign_result.json", "manifest.json"}
    ):
        raise V1ProductionStateEvidenceError("production campaign bytes changed")
    result = _strict_json(result_path)
    manifest = _strict_json(manifest_path)
    validate_campaign_result(result)
    if (
        result.get("schema") != SOURCE_CAMPAIGN_SCHEMA
        or result.get("coverage", {}).get("D_prod_key_count") != EXPECTED_KEYS
        or result.get("coverage", {}).get("exact_eight_state_mode_count")
        != EXPECTED_ORIGINAL_STATES
        or result.get("coverage", {}).get("missing_eight_state_mode_count")
        != EXPECTED_REPAIRED_STATES
        or result.get("mode_state_counts")
        != {"FAIL": EXPECTED_REPAIRED_STATES, "PARTIAL": EXPECTED_ORIGINAL_STATES}
        or manifest.get("schema") != SOURCE_CAMPAIGN_MANIFEST_SCHEMA
        or manifest.get("campaign_result_identity") != source_file_identity(result_path)
    ):
        raise V1ProductionStateEvidenceError("production campaign coverage changed")
    return result


def _validate_current_sources(contract: Mapping[str, object]) -> tuple[str, ...]:
    identities = contract.get("implementation_source_identities")
    hashes = contract.get("implementation_source_sha256s")
    if not isinstance(identities, Mapping) or not isinstance(hashes, Mapping):
        raise V1ProductionStateEvidenceError("repair source ledger is missing")
    observed: dict[str, Mapping[str, object]] = {}
    for name, expected in identities.items():
        if not isinstance(expected, Mapping):
            raise V1ProductionStateEvidenceError("repair source identity changed")
        observed[str(name)] = source_file_identity(Path(str(expected["path"])))
    if (
        observed != identities
        or {name: identity["sha256"] for name, identity in observed.items()} != hashes
    ):
        raise V1ProductionStateEvidenceError("repair implementation source drift")
    return _implementation_hash_values(hashes, "repair implementation source")


def validate_production_state_sources(
    *, campaign_root: str | Path, repair_root: str | Path
) -> dict[str, object]:
    campaign = _direct_root(campaign_root, "production campaign")
    repair = _direct_root(repair_root, "production repair")
    campaign_result = _validate_campaign(campaign)
    inventory = load_repair_inventory(
        campaign, domain_root=DOMAIN_ROOT, execution_root=EXECUTION_ROOT
    )
    if len(inventory.modes) != EXPECTED_FAILURE_COUNT:
        raise V1ProductionStateEvidenceError("repair inventory cardinality changed")
    contract_path = repair / "run_contract.json"
    result_path = repair / "run_result.json"
    manifest_path = repair / "manifest.json"
    contract = _strict_json(contract_path)
    result = _strict_json(result_path)
    manifest = _strict_json(manifest_path)
    implementation_hashes = _validate_current_sources(contract)
    if (
        contract.get("schema") != REPAIR_CONTRACT_SCHEMA
        or contract.get("selected_mode_count") != EXPECTED_REPAIRED_STATES
        or contract.get("full_failure_mode_count") != EXPECTED_REPAIRED_STATES
        or contract.get("limit") is not None
        or contract.get("scientific_acceptance") is not False
        or result.get("schema") != REPAIR_RESULT_SCHEMA
        or result.get("overall_state") != "PARTIAL"
        or result.get("terminal_mode_count") != EXPECTED_REPAIRED_STATES
        or result.get("measured_mode_count") != EXPECTED_REPAIRED_STATES
        or result.get("failed_mode_count") != 0
        or result.get("radial_state_record_count") != 8 * EXPECTED_REPAIRED_STATES
        or result.get("failure_ledger") != []
        or result.get("scientific_acceptance") is not False
        or manifest.get("schema") != REPAIR_MANIFEST_SCHEMA
        or manifest.get("status") != "COMPLETE"
        or manifest.get("contract_identity") != source_file_identity(contract_path)
        or manifest.get("result_identity") != source_file_identity(result_path)
    ):
        raise V1ProductionStateEvidenceError("production repair terminal changed")
    records_dir = repair / "records"
    record_identities: list[Mapping[str, object]] = []
    repaired_keys: list[dict[str, object]] = []
    for mode in inventory.modes:
        path = records_dir / _record_filename(mode)
        record = _strict_json(path)
        validate_repair_record(record, mode=mode, sites=inventory.frozen.sites)
        if record.get("status") != "MEASURED":
            raise V1ProductionStateEvidenceError(
                f"production repair mode is not measured: {repair_key_id(mode.key)}"
            )
        record_identities.append(source_file_identity(path))
        repaired_keys.append(mode.key.to_record())
    if result.get("record_identities") != record_identities or set(
        path.name for path in records_dir.glob("*.json")
    ) != {_record_filename(mode) for mode in inventory.modes}:
        raise V1ProductionStateEvidenceError("production repair record ledger changed")
    frozen = load_frozen_production_contract(DOMAIN_ROOT, EXECUTION_ROOT)
    if len(frozen.production_keys) != EXPECTED_KEYS:
        raise V1ProductionStateEvidenceError("D_prod cardinality changed")
    missing = campaign_result["coverage"]["missing_eight_state_modes"]
    if repaired_keys != missing:
        raise V1ProductionStateEvidenceError(
            "repair keys no longer match missing states"
        )
    return {
        "campaign_root": str(campaign),
        "campaign_result_identity": source_file_identity(
            campaign / "campaign_result.json"
        ),
        "campaign_manifest_identity": source_file_identity(campaign / "manifest.json"),
        "repair_root": str(repair),
        "repair_result_identity": source_file_identity(result_path),
        "repair_manifest_identity": source_file_identity(manifest_path),
        "implementation_source_sha256s": sorted(
            set(
                implementation_hashes
                + _implementation_hash_values(
                    campaign_result.get("campaign_implementation_source_sha256s"),
                    "campaign publisher implementation source",
                )
                + _implementation_hash_values(
                    campaign_result.get("implementation_source_sha256s"),
                    "campaign numerical implementation source",
                )
            )
        ),
        "production_keys": [key.to_record() for key in frozen.production_keys],
    }


def _component(
    state: str, estimate: float | None, units: str, reason: str
) -> dict[str, object]:
    return {"state": state, "estimate": estimate, "units": units, "reason": reason}


def _item_id(key: Mapping[str, object]) -> str:
    km = str(key["kM"]).replace(".", "p")
    return f"radial_km_{km}_{key['sector']}_ell_{int(key['ell']):03d}"


def build_production_state_report(source: Mapping[str, object]) -> dict[str, object]:
    keys = source["production_keys"]
    if not isinstance(keys, list) or len(keys) != EXPECTED_KEYS:
        raise V1ProductionStateEvidenceError("production typed key inventory changed")
    ids = sorted(_item_id(key) for key in keys)
    na = "not applicable to a sector-resolved radial master state"
    numerical = {
        "arithmetic_precision": _component(
            "NOT_ASSESSED", None, "relative", "full D_prod precision ladder is absent"
        ),
        "axis_limit": _component("PASS", 0.0, "not_applicable", na),
        "backend_difference": _component(
            "NOT_ASSESSED",
            None,
            "relative",
            "independent backends are selected-domain evidence",
        ),
        "jost_order": _component(
            "NOT_ASSESSED", None, "relative", "full D_prod order ladder is absent"
        ),
        "lmax": _component("PASS", 0.0, "not_applicable", na),
        "ode_tolerance": _component(
            "NOT_ASSESSED", None, "relative", "full D_prod tolerance ladder is absent"
        ),
        "r_in": _component(
            "NOT_ASSESSED", None, "relative", "full D_prod inner ladder is absent"
        ),
        "r_out": _component(
            "PARTIAL",
            8.0,
            "exact_finite_radius_states_per_mode",
            "all exact eight production states exist; asymptotic boundary ladders are separate",
        ),
    }
    convention = {
        name: _component("PASS", 0.0, "not_applicable", na)
        for name in ("observer", "worldline", "tetrad", "polarization_basis")
    }
    convention.update(
        {
            "phase_origin": _component(
                "NOT_ASSESSED", None, "radian", "absolute phase is not claimed"
            ),
            "total_scattered_definition": _component(
                "PASS",
                0.0,
                "definition",
                "stored records are radial master states, not detector responses",
            ),
        }
    )
    return {
        "schema": TYPED_RESULT_SCHEMA,
        "result_id": "phase6_v1_production_eight_radius_states_16048",
        "role": "PRIMARY_SCIENCE",
        "independence_class": "SAME_IMPLEMENTATION",
        "gate": "V1",
        "observable": "radial_s_matrix_flux",
        "parameter_domain": {
            "domain_id": "production_eight_radius_states_16048_repaired",
            "description": "exact D_prod radial master states at eight production sites",
            "parameters": {"mode_count": EXPECTED_KEYS, "states_per_mode": 8},
            "selection_policy": "exact frozen D_prod union",
            "expected_items": EXPECTED_KEYS,
            "expected_item_ids": ids,
        },
        "item_results": [{"item_id": item_id, "state": "PASS"} for item_id in ids],
        "state": "PARTIAL",
        "reason": "all exact eight-radius states exist; independent full-domain budgets remain open",
        "limitations": [
            "these are radial master-field states, not finite-radius detector responses",
            "independent arbitrary-precision and external comparisons are selected-domain",
        ],
        "implementation_source_sha256s": source["implementation_source_sha256s"],
        "numerical_uncertainty_budget": numerical,
        "convention_uncertainty_budget": convention,
        "scientific_evidence": True,
        "science_executed": True,
        "kernel_unit_test_only": False,
        "global_green_permitted": False,
        "li_figure_agreement_primary_gate": False,
        "full_paper_figure_rerun": False,
        "observer_qualification": {
            "output_kind": "PRODUCTION_FINITE_RADIUS_RADIAL_MASTER_STATES",
            "worldline_tetrad_pure_gauge_test": "NOT_ASSESSED",
            "detector_response_claim_permitted": False,
        },
    }


def _publish(path: Path, payload: object) -> dict[str, object]:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as handle:
            handle.write(canonical_json_bytes(payload))
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(descriptor)
    os.chmod(path, FORMAL_FILE_MODE)
    return source_file_identity(path)


def publish_production_state_evidence(
    *, campaign_root: str | Path, repair_root: str | Path, output_root: str | Path
) -> dict[str, object]:
    source = validate_production_state_sources(
        campaign_root=campaign_root, repair_root=repair_root
    )
    root = Path(output_root).absolute()
    if root.exists() or root.is_symlink():
        raise V1ProductionStateEvidenceError("production evidence root must be absent")
    root.mkdir(parents=True, mode=0o700)
    ledger = {
        "schema": LEDGER_SCHEMA,
        "campaign_root": source["campaign_root"],
        "campaign_result_identity": source["campaign_result_identity"],
        "campaign_manifest_identity": source["campaign_manifest_identity"],
        "repair_root": source["repair_root"],
        "repair_result_identity": source["repair_result_identity"],
        "repair_manifest_identity": source["repair_manifest_identity"],
        "global_green_permitted": False,
    }
    identities = {
        "source_ledger.json": _publish(root / "source_ledger.json", ledger),
        "report.json": _publish(
            root / "report.json", build_production_state_report(source)
        ),
    }
    _publish(
        root / "manifest.json",
        {
            "schema": MANIFEST_SCHEMA,
            "artifacts": identities,
            "global_green_permitted": False,
            "overall_state": "PARTIAL",
        },
    )
    os.chmod(root, FORMAL_ROOT_MODE)
    return validate_published_production_state_evidence(root)


def validate_published_production_state_evidence(
    root_path: str | Path,
) -> dict[str, object]:
    root = _direct_root(root_path, "production evidence")
    manifest = _strict_json(root / "manifest.json")
    artifacts = manifest.get("artifacts")
    if (
        manifest.get("schema") != MANIFEST_SCHEMA
        or manifest.get("overall_state") != "PARTIAL"
        or not isinstance(artifacts, Mapping)
        or set(path.name for path in root.iterdir()) != {*artifacts, "manifest.json"}
    ):
        raise V1ProductionStateEvidenceError("production evidence manifest changed")
    for name, expected in artifacts.items():
        if source_file_identity(root / str(name)) != expected:
            raise V1ProductionStateEvidenceError("production evidence identity changed")
    ledger = _strict_json(root / "source_ledger.json")
    if ledger.get("schema") != LEDGER_SCHEMA:
        raise V1ProductionStateEvidenceError("production source ledger changed")
    source = validate_production_state_sources(
        campaign_root=str(ledger["campaign_root"]),
        repair_root=str(ledger["repair_root"]),
    )
    for name in (
        "campaign_result_identity",
        "campaign_manifest_identity",
        "repair_result_identity",
        "repair_manifest_identity",
    ):
        if ledger.get(name) != source[name]:
            raise V1ProductionStateEvidenceError("production source linkage changed")
    report = _strict_json(root / "report.json")
    if report != build_production_state_report(source):
        raise V1ProductionStateEvidenceError("production typed report changed")
    return dict(report)


__all__ = [
    "MANIFEST_SCHEMA",
    "V1ProductionStateEvidenceError",
    "build_production_state_report",
    "publish_production_state_evidence",
    "validate_production_state_sources",
    "validate_published_production_state_evidence",
]
