"""Strict release wrapper for the independent 24-anchor mpmath campaign."""

from __future__ import annotations

from collections.abc import Mapping
import json
import math
import os
from pathlib import Path
import stat

from schwgw.validation.phase6_domain import (
    canonical_json_bytes,
    source_file_identity,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RUNNER_PATH = PROJECT_ROOT / "scripts" / "phase6_publish_v1_ap_selected_evidence.py"
SOURCE_PLAN_SCHEMA = "schwgw_phase6_ap_radial_repair_plan_v1"
SOURCE_RESULT_SCHEMA = "schwgw_phase6_ap_radial_repair_anchor_result_v1"
SOURCE_CHECKPOINT_SCHEMA = "schwgw_phase6_ap_radial_repair_checkpoint_v1"
SOURCE_SUMMARY_SCHEMA = "schwgw_phase6_ap_radial_repair_summary_v1"
SOURCE_MANIFEST_SCHEMA = "schwgw_phase6_ap_radial_repair_manifest_v1"
TYPED_RESULT_SCHEMA = "schwgw_phase6_v1_typed_physical_result_v1"
LEDGER_SCHEMA = "schwgw_phase6_v1_ap_selected_source_ledger_v1"
MANIFEST_SCHEMA = "schwgw_phase6_v1_ap_selected_evidence_manifest_v1"
EXPECTED_ANCHORS = 24
FORMAL_ROOT_MODE = 0o555
FORMAL_FILE_MODE = 0o444


class V1APSelectedEvidenceError(ValueError):
    """Raised when the AP source or its release projection drifts."""


def _strict_json(path: Path, *, formal: bool = True) -> Mapping[str, object]:
    if formal:
        identity = source_file_identity(path)
        if identity["mode"] != FORMAL_FILE_MODE or identity["nlink"] != 1:
            raise V1APSelectedEvidenceError(f"non-immutable AP artifact: {path}")
    raw = path.read_bytes()
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise V1APSelectedEvidenceError(f"invalid AP JSON: {path}") from exc
    if not isinstance(payload, Mapping) or raw != canonical_json_bytes(payload):
        raise V1APSelectedEvidenceError(f"noncanonical AP JSON: {path}")
    return payload


def _check_source_hashes(plan: Mapping[str, object]) -> tuple[str, ...]:
    isolation = plan.get("implementation_isolation")
    runtime = plan.get("runtime")
    if not isinstance(isolation, Mapping) or not isinstance(runtime, Mapping):
        raise V1APSelectedEvidenceError("AP source/runtime ledger is missing")
    paths = isolation.get("paths")
    if not isinstance(paths, list) or len(paths) != 2:
        raise V1APSelectedEvidenceError("AP implementation path inventory changed")
    hashes: list[str] = []
    for record in paths:
        if not isinstance(record, Mapping):
            raise V1APSelectedEvidenceError("AP implementation identity changed")
        path = Path(str(record.get("path"))).absolute()
        identity = source_file_identity(path)
        if identity["sha256"] != record.get("sha256"):
            raise V1APSelectedEvidenceError("AP implementation source hash drift")
        hashes.append(str(identity["sha256"]))
    origin = runtime.get("import_origin")
    if not isinstance(origin, Mapping):
        raise V1APSelectedEvidenceError("AP mpmath origin identity is missing")
    if source_file_identity(Path(str(origin.get("path"))).absolute()) != origin:
        raise V1APSelectedEvidenceError("AP mpmath origin identity drift")
    hashes.append(str(origin["sha256"]))
    return tuple(sorted(set(hashes)))


def validate_ap_selected_source(root_path: str | Path) -> dict[str, object]:
    root = Path(root_path).absolute()
    info = root.lstat()
    if (
        root.is_symlink()
        or root.resolve(strict=True) != root
        or not stat.S_ISDIR(info.st_mode)
        or stat.S_IMODE(info.st_mode) != FORMAL_ROOT_MODE
    ):
        raise V1APSelectedEvidenceError("AP source root is not immutable 0555")
    manifest = _strict_json(root / "manifest.json")
    files = manifest.get("files")
    if (
        manifest.get("schema") != SOURCE_MANIFEST_SCHEMA
        or manifest.get("status") != "SELECTED_ANCHOR_LADDERS_CLOSED"
        or manifest.get("global_green_permitted") is not False
        or not isinstance(files, Mapping)
        or set(path.name for path in root.iterdir()) != {*files, "manifest.json"}
    ):
        raise V1APSelectedEvidenceError("AP source manifest/inventory changed")
    for name, expected in files.items():
        if source_file_identity(root / str(name)) != expected:
            raise V1APSelectedEvidenceError(f"AP source identity changed: {name}")
    plan = _strict_json(root / "campaign_plan.json")
    summary = _strict_json(root / "summary.json")
    if (
        plan.get("schema") != SOURCE_PLAN_SCHEMA
        or plan.get("campaign_kind") != "FULL_SELECTED_REPAIR"
        or plan.get("planned_anchor_count") != EXPECTED_ANCHORS
        or plan.get("scientific_acceptance") is not False
        or summary.get("schema") != SOURCE_SUMMARY_SCHEMA
        or summary.get("completed_anchor_count") != EXPECTED_ANCHORS
        or summary.get("ladder_closed_anchor_count") != EXPECTED_ANCHORS
        or summary.get("scientific_acceptance") is not True
        or summary.get("status") != "SELECTED_ANCHOR_LADDERS_CLOSED"
        or manifest.get("summary_identity")
        != source_file_identity(root / "summary.json")
    ):
        raise V1APSelectedEvidenceError("AP source plan/summary changed")
    implementation_hashes = _check_source_hashes(plan)
    anchors: list[dict[str, object]] = []
    ids: set[str] = set()
    for ordinal in range(EXPECTED_ANCHORS):
        matches = sorted(root.glob(f"anchor_{ordinal:02d}__*.json"))
        if len(matches) != 1:
            raise V1APSelectedEvidenceError("AP anchor filename inventory changed")
        result = _strict_json(matches[0])
        anchor = result.get("anchor")
        numerical = result.get("numerical_uncertainty_budget")
        convention = result.get("convention_uncertainty_budget")
        if (
            result.get("schema") != SOURCE_RESULT_SCHEMA
            or result.get("status") != "LADDER_CLOSED"
            or result.get("ladder_closed") is not True
            or result.get("scientific_acceptance") is not True
            or result.get("global_green_permitted") is not False
            or not isinstance(anchor, Mapping)
            or not isinstance(numerical, Mapping)
            or numerical.get("overall_state") != "PASS"
            or not isinstance(convention, Mapping)
            or convention.get("overall_state") != "FROZEN_NOT_EXTERNALLY_CROSSCHECKED"
        ):
            raise V1APSelectedEvidenceError("AP accepted anchor changed")
        anchor_id = str(anchor.get("anchor_id"))
        if not anchor_id or anchor_id in ids:
            raise V1APSelectedEvidenceError("AP anchor id changed/duplicated")
        ids.add(anchor_id)
        for name in (
            "arithmetic_precision",
            "flux_balance",
            "jost_tail",
            "match_condition",
            "match_residual",
            "step_size",
        ):
            check = numerical.get(name)
            if (
                not isinstance(check, Mapping)
                or check.get("state") != "PASS"
                or not math.isfinite(float(check["estimate"]))
            ):
                raise V1APSelectedEvidenceError("AP numerical ladder changed")
        checkpoint = _strict_json(root / f"checkpoint_{ordinal:02d}.json")
        if (
            checkpoint.get("schema") != SOURCE_CHECKPOINT_SCHEMA
            or checkpoint.get("anchor_id") != anchor_id
            or checkpoint.get("completed_anchor_count") != ordinal + 1
            or checkpoint.get("result_identity") != source_file_identity(matches[0])
        ):
            raise V1APSelectedEvidenceError("AP checkpoint linkage changed")
        anchors.append(dict(result))
    return {
        "anchors": anchors,
        "implementation_source_sha256s": list(implementation_hashes),
        "plan_identity": source_file_identity(root / "campaign_plan.json"),
        "root": str(root),
        "summary": dict(summary),
        "summary_identity": source_file_identity(root / "summary.json"),
        "manifest_identity": source_file_identity(root / "manifest.json"),
    }


def _component(
    state: str, estimate: float | None, units: str, reason: str
) -> dict[str, object]:
    return {"state": state, "estimate": estimate, "units": units, "reason": reason}


def build_ap_typed_report(source: Mapping[str, object]) -> dict[str, object]:
    anchors = source["anchors"]
    if not isinstance(anchors, list) or len(anchors) != EXPECTED_ANCHORS:
        raise V1APSelectedEvidenceError("AP typed source anchors changed")
    ids = sorted(str(item["anchor"]["anchor_id"]) for item in anchors)
    maxima = {
        name: max(
            float(item["numerical_uncertainty_budget"][name]["estimate"])
            for item in anchors
        )
        for name in (
            "arithmetic_precision",
            "flux_balance",
            "jost_tail",
            "match_condition",
            "match_residual",
            "step_size",
        )
    }
    na = "not applicable to one sector-resolved radial master mode"
    numerical = {
        "arithmetic_precision": _component(
            "PASS",
            maxima["arithmetic_precision"],
            "relative_complex_S",
            "maximum independent 60-versus-80 dps difference",
        ),
        "axis_limit": _component("PASS", 0.0, "not_applicable", na),
        "backend_difference": _component(
            "NOT_ASSESSED",
            None,
            "relative_complex_S",
            "cross-backend comparison is a separate selected certificate",
        ),
        "jost_order": _component(
            "PARTIAL",
            maxima["jost_tail"],
            "tail_ratio",
            "Jost tail is bounded at order 160; an order ladder is not run",
        ),
        "lmax": _component("PASS", 0.0, "not_applicable", na),
        "ode_tolerance": _component(
            "PASS",
            maxima["step_size"],
            "relative_complex_S",
            "maximum independent RK4 step-size ladder difference",
        ),
        "r_in": _component(
            "NOT_ASSESSED",
            None,
            "relative_complex_S",
            "the independent selected campaign uses one frozen horizon offset",
        ),
        "r_out": _component(
            "PARTIAL",
            maxima["match_residual"],
            "inverse_M",
            "matching/Jost residuals pass, but no outer-radius ladder is run",
        ),
    }
    convention = {
        name: _component("PASS", 0.0, "not_applicable", na)
        for name in ("observer", "worldline", "tetrad", "polarization_basis")
    }
    convention.update(
        {
            "phase_origin": _component(
                "PARTIAL",
                0.0,
                "frozen_definition",
                "the absolute phase convention is frozen but not externally compared in this source",
            ),
            "total_scattered_definition": _component(
                "PASS",
                0.0,
                "definition",
                "S=-A_out/[(-1)^ell A_in] is frozen",
            ),
        }
    )
    return {
        "schema": TYPED_RESULT_SCHEMA,
        "result_id": "phase6_v1_ap_selected_24",
        "role": "INDEPENDENT_SCIENCE",
        "independence_class": "ALGORITHMICALLY_INDEPENDENT",
        "gate": "V1",
        "observable": "radial_s_matrix_flux",
        "parameter_domain": {
            "domain_id": "ap_repair_selected_24",
            "description": "stratified 24-key arbitrary-precision radial domain",
            "parameters": {"precision_dps": [60, 80], "anchor_count": 24},
            "selection_policy": "frozen k-band/sector/turning-severity stratification",
            "expected_items": EXPECTED_ANCHORS,
            "expected_item_ids": ids,
        },
        "item_results": [{"item_id": item_id, "state": "PASS"} for item_id in ids],
        "state": "PARTIAL",
        "reason": "all AP ladders close; r_in/r_out/order and external comparison remain separate",
        "limitations": [
            "selected 24-anchor coverage is not full D_union coverage",
            "the AP source does not itself compare against the project float64 backend",
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
            "output_kind": "RADIAL_S_MATRIX_ARBITRARY_PRECISION_SELECTED",
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


def publish_ap_selected_evidence(
    *, source_root: str | Path, output_root: str | Path
) -> dict[str, object]:
    source = validate_ap_selected_source(source_root)
    root = Path(output_root).absolute()
    if root.exists() or root.is_symlink():
        raise V1APSelectedEvidenceError("AP evidence output root must be absent")
    root.mkdir(parents=True, mode=0o700)
    identities: dict[str, dict[str, object]] = {}
    ledger = {
        "schema": LEDGER_SCHEMA,
        "source_root": source["root"],
        "source_plan_identity": source["plan_identity"],
        "source_summary_identity": source["summary_identity"],
        "source_manifest_identity": source["manifest_identity"],
        "global_green_permitted": False,
    }
    identities["source_ledger.json"] = _publish(root / "source_ledger.json", ledger)
    identities["report.json"] = _publish(
        root / "report.json", build_ap_typed_report(source)
    )
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
    return validate_published_ap_selected_evidence(root)


def validate_published_ap_selected_evidence(
    root_path: str | Path,
) -> dict[str, object]:
    root = Path(root_path).absolute()
    if (
        root.is_symlink()
        or root.resolve(strict=True) != root
        or stat.S_IMODE(root.lstat().st_mode) != FORMAL_ROOT_MODE
    ):
        raise V1APSelectedEvidenceError("AP evidence root is not immutable 0555")
    manifest = _strict_json(root / "manifest.json")
    artifacts = manifest.get("artifacts")
    if (
        manifest.get("schema") != MANIFEST_SCHEMA
        or manifest.get("overall_state") != "PARTIAL"
        or not isinstance(artifacts, Mapping)
        or set(path.name for path in root.iterdir()) != {*artifacts, "manifest.json"}
    ):
        raise V1APSelectedEvidenceError("AP evidence manifest changed")
    for name, expected in artifacts.items():
        if source_file_identity(root / str(name)) != expected:
            raise V1APSelectedEvidenceError("AP evidence identity changed")
    ledger = _strict_json(root / "source_ledger.json")
    if ledger.get("schema") != LEDGER_SCHEMA:
        raise V1APSelectedEvidenceError("AP source ledger changed")
    source = validate_ap_selected_source(str(ledger["source_root"]))
    if (
        ledger.get("source_plan_identity") != source["plan_identity"]
        or ledger.get("source_summary_identity") != source["summary_identity"]
        or ledger.get("source_manifest_identity") != source["manifest_identity"]
    ):
        raise V1APSelectedEvidenceError("AP source linkage changed")
    report = _strict_json(root / "report.json")
    if report != build_ap_typed_report(source):
        raise V1APSelectedEvidenceError("AP typed projection changed")
    return dict(report)


__all__ = [
    "MANIFEST_SCHEMA",
    "V1APSelectedEvidenceError",
    "build_ap_typed_report",
    "publish_ap_selected_evidence",
    "validate_ap_selected_source",
    "validate_published_ap_selected_evidence",
]
