#!/usr/bin/env python3
"""Build a sealed candidate submission from bounded Phase-6 V2--V5 measurements.

This runner never calls the formal evidence publisher and refuses output below
``runs/``.  Its output is publisher input for review, not a formal result root.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat

from schwgw.validation.phase6_domain import canonical_json_bytes
from schwgw.validation.phase6_observable_evidence import (
    CERTIFICATE_SCHEMA,
    DOMAIN_SCHEMA,
    OBSERVABLE_GATES,
    REQUIRED_CHECKS,
    SUBMISSION_SCHEMA,
    certificate_id,
    direct_file_identity,
    validate_submission,
)
from schwgw.validation.phase6_observable_measurements import (
    MEASUREMENT_SCHEMA,
    OBSERVABLE_SOURCE_LABELS,
    PROJECT_ROOT,
    SOURCE_PATHS,
    SelectedObservableMeasurementConfig,
    run_selected_observable_measurements,
    validate_measurement_payload,
)


CANDIDATE_MANIFEST_SCHEMA = "schwgw_phase6_selected_observable_candidate_manifest_v1"
CANDIDATE_STATUS = "PARTIAL_ONLY_NOT_FORMAL_RELEASE"
CONFIG_FILENAME = "measurement_config.json"
MEASUREMENT_FILENAME = "selected_measurements.json"
SUBMISSION_FILENAME = "submission.json"
MANIFEST_FILENAME = "candidate_manifest.json"


class ObservableCandidateError(ValueError):
    """Raised when a candidate package is unsafe, stale, or contradictory."""


def build_candidate_submission(
    output_root: str | Path,
    *,
    config: SelectedObservableMeasurementConfig = SelectedObservableMeasurementConfig(),
) -> dict[str, object]:
    """Run selected measurements and build a sealed, non-formal candidate root."""

    if not isinstance(config, SelectedObservableMeasurementConfig):
        raise TypeError("config must be SelectedObservableMeasurementConfig")
    root = _candidate_path(output_root)
    measurement = run_selected_observable_measurements(config)
    validate_measurement_payload(measurement)
    _new_root(root)
    try:
        source_identities = _snapshot_sources(root)
        config_identity = _write_json(root / CONFIG_FILENAME, config.to_record())
        measurement_identity = _write_json(root / MEASUREMENT_FILENAME, measurement)
        certificates = []
        domain_identities: dict[str, dict[str, object]] = {}
        for observable, section_value in measurement["observables"].items():
            section = dict(section_value)
            domain_identity, domain = _write_domain(root, observable, section)
            domain_identities[observable] = domain_identity
            certificates.append(
                _certificate_from_section(
                    observable=observable,
                    section=section,
                    domain=domain,
                    domain_identity=domain_identity,
                    measurement_identity=measurement_identity,
                    config_identity=config_identity,
                    source_identities=source_identities,
                )
            )
        certificates.sort(
            key=lambda item: (
                str(item["acceptance_gate"]),
                str(item["observable"]),
                str(item["certificate_id"]),
            )
        )
        submission = {"schema": SUBMISSION_SCHEMA, "certificates": certificates}
        submission_identity = _write_json(root / SUBMISSION_FILENAME, submission)
        manifest = {
            "schema": CANDIDATE_MANIFEST_SCHEMA,
            "status": CANDIDATE_STATUS,
            "formal_release": False,
            "formal_publisher_invoked": False,
            "candidate_release_only": True,
            "global_green_permitted": False,
            "paper_agreement_primary_gate": False,
            "measurement_identity": measurement_identity,
            "config_identity": config_identity,
            "submission_identity": submission_identity,
            "source_snapshot_identities": source_identities,
            "domain_identities": domain_identities,
            "certificate_states": {
                str(item["observable"]): str(item["state"]) for item in certificates
            },
        }
        _write_json(root / MANIFEST_FILENAME, manifest)
        _seal_root(root)
        return validate_candidate_root(root)
    except BaseException:
        _seal_root(root)
        raise


def validate_candidate_root(root: str | Path) -> dict[str, object]:
    """Validate a sealed candidate without promoting it to a formal bundle."""

    path = Path(root).absolute()
    if any(item.is_symlink() for item in (path, *path.parents)):
        raise ObservableCandidateError("candidate path contains a symlink component")
    try:
        resolved = path.resolve(strict=True)
        info = path.lstat()
    except OSError as exc:
        raise ObservableCandidateError(
            f"cannot inspect candidate root: {path}"
        ) from exc
    if (
        resolved != path
        or not stat.S_ISDIR(info.st_mode)
        or stat.S_IMODE(info.st_mode) != 0o555
    ):
        raise ObservableCandidateError(
            "candidate root must be a direct mode-0555 directory"
        )
    expected_files = _expected_filenames()
    if {child.name for child in path.iterdir()} != expected_files:
        raise ObservableCandidateError("candidate root layout changed")
    if "observable_evidence.json" in expected_files:
        raise ObservableCandidateError(
            "candidate root resembles a formal published root"
        )

    manifest = _load_canonical_json(path / MANIFEST_FILENAME)
    fields = {
        "schema",
        "status",
        "formal_release",
        "formal_publisher_invoked",
        "candidate_release_only",
        "global_green_permitted",
        "paper_agreement_primary_gate",
        "measurement_identity",
        "config_identity",
        "submission_identity",
        "source_snapshot_identities",
        "domain_identities",
        "certificate_states",
    }
    if not isinstance(manifest, dict) or set(manifest) != fields:
        raise ObservableCandidateError("candidate manifest schema changed")
    if (
        manifest["schema"] != CANDIDATE_MANIFEST_SCHEMA
        or manifest["status"] != CANDIDATE_STATUS
        or manifest["formal_release"] is not False
        or manifest["formal_publisher_invoked"] is not False
        or manifest["candidate_release_only"] is not True
        or manifest["global_green_permitted"] is not False
        or manifest["paper_agreement_primary_gate"] is not False
    ):
        raise ObservableCandidateError("candidate release policy changed")

    measurement_identity = direct_file_identity(path / MEASUREMENT_FILENAME)
    config_identity = direct_file_identity(path / CONFIG_FILENAME)
    submission_identity = direct_file_identity(path / SUBMISSION_FILENAME)
    if (
        manifest["measurement_identity"] != measurement_identity
        or manifest["config_identity"] != config_identity
        or manifest["submission_identity"] != submission_identity
    ):
        raise ObservableCandidateError("candidate core identity changed")

    measurement = _load_canonical_json(path / MEASUREMENT_FILENAME)
    validate_measurement_payload(measurement, verify_live_sources=False)
    if measurement.get("schema") != MEASUREMENT_SCHEMA:
        raise ObservableCandidateError("candidate measurement schema changed")
    if _load_canonical_json(path / CONFIG_FILENAME) != measurement["config"]:
        raise ObservableCandidateError("candidate config is not measurement-bound")

    sources = manifest["source_snapshot_identities"]
    if not isinstance(sources, dict) or set(sources) != set(SOURCE_PATHS):
        raise ObservableCandidateError("candidate source inventory changed")
    for label, identity in sources.items():
        if identity != direct_file_identity(path / _source_filename(label)):
            raise ObservableCandidateError(
                f"candidate source identity changed: {label}"
            )
    for observable, section in measurement["observables"].items():
        for label, live_identity in section["source_identities"].items():
            snapshot = sources[label]
            if (
                live_identity["sha256"] != snapshot["sha256"]
                or live_identity["size"] != snapshot["size"]
            ):
                raise ObservableCandidateError(
                    f"candidate measurement is not snapshot-bound: {observable}/{label}"
                )

    domains = manifest["domain_identities"]
    if not isinstance(domains, dict) or set(domains) != set(OBSERVABLE_GATES):
        raise ObservableCandidateError("candidate domain inventory changed")
    for observable, identity in domains.items():
        if identity != direct_file_identity(path / _domain_filename(observable)):
            raise ObservableCandidateError(
                f"candidate domain identity changed: {observable}"
            )

    submission = _load_canonical_json(path / SUBMISSION_FILENAME)
    certificates = validate_submission(submission)
    states = {str(item["observable"]): str(item["state"]) for item in certificates}
    if (
        len(certificates) != len(OBSERVABLE_GATES)
        or set(states) != set(OBSERVABLE_GATES)
        or set(states.values()) != {"PARTIAL"}
        or manifest["certificate_states"] != states
    ):
        raise ObservableCandidateError("candidate certificate state inventory changed")
    return {
        "candidate_root": str(path),
        "formal_release": False,
        "measurement_sha256": measurement_identity["sha256"],
        "submission_sha256": submission_identity["sha256"],
        "certificate_states": states,
    }


def _candidate_path(value: str | Path) -> Path:
    path = Path(value).absolute()
    runs = (PROJECT_ROOT / "runs").absolute()
    if path == runs or path.is_relative_to(runs):
        raise ObservableCandidateError("candidate output below runs/ is forbidden")
    return path


def _new_root(root: Path) -> None:
    if any(item.is_symlink() for item in (root.parent, *root.parent.parents)):
        raise ObservableCandidateError("candidate parent contains a symlink component")
    if root.exists() or root.is_symlink() or not root.parent.is_dir():
        raise ObservableCandidateError(f"refusing to overwrite candidate root: {root}")
    os.mkdir(root, 0o700)
    _fsync_directory(root.parent)


def _snapshot_sources(root: Path) -> dict[str, dict[str, object]]:
    result = {}
    for label, source in sorted(SOURCE_PATHS.items()):
        absolute = source.absolute()
        if any(item.is_symlink() for item in (absolute, *absolute.parents)):
            raise ObservableCandidateError(f"source path contains a symlink: {label}")
        try:
            resolved = absolute.resolve(strict=True)
            info = absolute.lstat()
        except OSError as exc:
            raise ObservableCandidateError(f"cannot snapshot source: {label}") from exc
        if resolved != absolute or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ObservableCandidateError(
                f"source is not a direct nlink1 file: {label}"
            )
        result[label] = _write_bytes(
            root / _source_filename(label), absolute.read_bytes()
        )
    return result


def _write_domain(
    root: Path,
    observable: str,
    section: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    explicit = section["explicit_domain"]
    records = [dict(record) for record in explicit["items"]]
    lines = sorted({canonical_json_bytes(record) for record in records})
    if len(lines) != len(records):
        raise ObservableCandidateError(f"domain items are not unique: {observable}")
    data = b"".join(lines)
    item_identity = _write_bytes(root / _item_filename(observable), data)
    assessed_identity = _write_bytes(root / _assessed_filename(observable), data)
    domain = {
        "schema": DOMAIN_SCHEMA,
        "domain_id": explicit["domain_id"],
        "observable": observable,
        "acceptance_gate": OBSERVABLE_GATES[observable],
        "parameters": explicit["parameters"],
        "selection_policy": explicit["selection_policy"],
        "item_index_identity": item_identity,
        "assessed_item_index_identity": assessed_identity,
        "coverage": {
            "expected_items": len(records),
            "assessed_items": len(records),
            "complete": True,
        },
    }
    identity = _write_json(root / _domain_filename(observable), domain)
    return identity, domain


def _certificate_from_section(
    *,
    observable: str,
    section: dict[str, object],
    domain: dict[str, object],
    domain_identity: dict[str, object],
    measurement_identity: dict[str, object],
    config_identity: dict[str, object],
    source_identities: dict[str, dict[str, object]],
) -> dict[str, object]:
    evidence_id = "selected_measurement"
    evidence_inventory = {
        evidence_id: {
            "identity": measurement_identity,
            "media_type": "application/json",
            "expected_schema": MEASUREMENT_SCHEMA,
            "role": "PRIMARY_SCIENCE",
            "independence_class": "SAME_IMPLEMENTATION",
            "provenance": {
                "producer": "phase6-selected-observable-measurement-runner",
                "producer_version": "v1",
                "method": (
                    "bounded real arithmetic on implemented Phase-6 primitives; "
                    "candidate-only and no paper-figure acceptance"
                ),
                "run_id": str(domain["domain_id"]),
                "actual_arithmetic": section["actual_arithmetic"],
                "source_snapshot_identities": [
                    source_identities[label]
                    for label in OBSERVABLE_SOURCE_LABELS[observable]
                ],
                "config_identities": [config_identity],
                "input_identities": [domain_identity],
            },
        }
    }
    checks = {
        name: _assessment_from_metric(
            metric,
            evidence_id=evidence_id,
            independence_required=independence_required,
            reason_if_open=f"{name} was not evaluated in this selected measurement",
        )
        for name, independence_required in REQUIRED_CHECKS[observable].items()
        for metric in [section["check_metrics"][name]]
    }
    numerical = {
        name: _budget_from_measurement(record, evidence_id=evidence_id)
        for name, record in section["numerical_budget"].items()
    }
    convention = {
        name: _budget_from_measurement(record, evidence_id=evidence_id)
        for name, record in section["convention_budget"].items()
    }
    return {
        "schema": CERTIFICATE_SCHEMA,
        "certificate_id": certificate_id(
            observable,
            OBSERVABLE_GATES[observable],
            domain,
            str(domain_identity["sha256"]),
        ),
        "observable": observable,
        "acceptance_gate": OBSERVABLE_GATES[observable],
        "parameter_domain_identity": domain_identity,
        "evidence_inventory": evidence_inventory,
        "acceptance_checks": checks,
        "numerical_budget": numerical,
        "convention_budget": convention,
        "secondary_evidence_ids": [],
        "limitations": list(section["limitations"]),
        "li_figure_agreement_primary_gate": False,
        "global_green_permitted": False,
        "state": "PARTIAL",
    }


def _assessment_from_metric(
    metric: object,
    *,
    evidence_id: str,
    independence_required: bool | None,
    reason_if_open: str,
) -> dict[str, object]:
    if metric is None:
        result: dict[str, object] = {
            "state": "NOT_ASSESSED",
            "reason": reason_if_open,
            "coverage": "NONE",
            "metric": None,
            "measured_value": None,
            "threshold_value": None,
            "comparison": None,
            "units": None,
            "evidence_ids": [],
        }
    else:
        result = {
            "state": "PARTIAL",
            "reason": f"{metric['reason']} No a-priori threshold or independent backend is bound.",
            "coverage": "INCOMPLETE",
            "metric": "selected_measurement",
            "measured_value": _decimal_text(metric["value"]),
            "threshold_value": None,
            "comparison": None,
            "units": metric["units"],
            "evidence_ids": [evidence_id],
        }
    if independence_required is not None:
        result["independence_required"] = independence_required
    return result


def _budget_from_measurement(
    record: dict[str, object], *, evidence_id: str
) -> dict[str, object]:
    applicability = str(record["applicability"])
    if record["state"] == "PARTIAL":
        assessment = {
            "state": "PARTIAL",
            "reason": f"{record['reason']} No a-priori threshold is bound.",
            "coverage": "INCOMPLETE",
            "metric": "selected_budget_value",
            "measured_value": _decimal_text(record["value"]),
            "threshold_value": None,
            "comparison": None,
            "units": record["units"],
            "evidence_ids": [evidence_id],
        }
    else:
        assessment = {
            "state": "NOT_ASSESSED",
            "reason": str(record["reason"]),
            "coverage": "NONE",
            "metric": None,
            "measured_value": None,
            "threshold_value": None,
            "comparison": None,
            "units": None,
            "evidence_ids": [],
        }
    return {"applicability": applicability, "assessment": assessment}


def _decimal_text(value: object) -> str:
    number = float(value)
    if not number >= 0.0 or not number < float("inf"):
        raise ObservableCandidateError(
            "candidate metric must be finite and nonnegative"
        )
    return format(number, ".1074f").rstrip("0").rstrip(".") or "0"


def _write_json(path: Path, payload: object) -> dict[str, object]:
    return _write_bytes(path, canonical_json_bytes(payload))


def _write_bytes(path: Path, data: bytes) -> dict[str, object]:
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
    return direct_file_identity(path, require_immutable_parent=False)


def _load_canonical_json(path: Path) -> dict[str, object]:
    identity = direct_file_identity(path)
    raw = Path(str(identity["path"])).read_bytes()
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ObservableCandidateError(
            f"candidate file is not JSON: {path.name}"
        ) from exc
    if not isinstance(payload, dict) or canonical_json_bytes(payload) != raw:
        raise ObservableCandidateError(f"candidate JSON is not canonical: {path.name}")
    return payload


def _seal_root(root: Path) -> None:
    if not root.exists() or root.is_symlink():
        return
    for child in root.iterdir():
        if child.is_file() and not child.is_symlink():
            os.chmod(child, 0o444)
    os.chmod(root, 0o555)
    _fsync_directory(root)
    _fsync_directory(root.parent)


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _source_filename(label: str) -> str:
    return f"source__{label}.py"


def _item_filename(observable: str) -> str:
    return f"domain_items__{observable}.jsonl"


def _assessed_filename(observable: str) -> str:
    return f"assessed_items__{observable}.jsonl"


def _domain_filename(observable: str) -> str:
    return f"domain__{observable}.json"


def _expected_filenames() -> set[str]:
    result = {
        CONFIG_FILENAME,
        MEASUREMENT_FILENAME,
        SUBMISSION_FILENAME,
        MANIFEST_FILENAME,
    }
    result.update(_source_filename(label) for label in SOURCE_PATHS)
    for observable in OBSERVABLE_GATES:
        result.update(
            {
                _item_filename(observable),
                _assessed_filename(observable),
                _domain_filename(observable),
            }
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_candidate_submission(args.output_root), sort_keys=True))


if __name__ == "__main__":
    main()
