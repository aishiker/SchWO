"""Adversarial tests for populated Phase-6 observable evidence."""

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import stat

import pytest

from scripts.phase6_publish_v1_observable_evidence import (
    publish_submission,
    validate_published_root,
)
from schwgw.validation.phase6_domain import canonical_json_bytes
from schwgw.validation.phase6_observable_contract import SCHEMA as ZERO_CONTRACT_SCHEMA
from schwgw.validation.phase6_observable_evidence import (
    CERTIFICATE_SCHEMA,
    CONVENTION_BUDGETS,
    DOMAIN_SCHEMA,
    NUMERICAL_BUDGETS,
    OBSERVABLE_GATES,
    REQUIRED_CHECKS,
    SUBMISSION_SCHEMA,
    THRESHOLD_SCHEMA,
    ZERO_CONTRACT_PATH,
    ObservableEvidenceError,
    build_bundle,
    certificate_id,
    direct_file_identity,
    validate_bundle,
    validate_certificate,
)


def _frozen_bytes(
    tmp_path: Path, name: str, filename: str, data: bytes
) -> dict[str, object]:
    root = tmp_path / name
    root.mkdir()
    path = root / filename
    path.write_bytes(data)
    os.chmod(path, 0o444)
    os.chmod(root, 0o555)
    return direct_file_identity(path)


def _frozen_json(tmp_path: Path, name: str, payload: object) -> dict[str, object]:
    return _frozen_bytes(tmp_path, name, "artifact.json", canonical_json_bytes(payload))


def _jsonl(records: list[dict[str, object]]) -> bytes:
    return b"".join(canonical_json_bytes(record) for record in records)


def _domain(
    tmp_path: Path,
    *,
    observable: str = "master_to_strain_flux",
    complete: bool,
) -> tuple[dict[str, object], dict[str, object]]:
    expected_records = [{"case": "a"}, {"case": "b"}]
    assessed_records = expected_records if complete else expected_records[:1]
    expected = _frozen_bytes(
        tmp_path, "domain-items", "items.jsonl", _jsonl(expected_records)
    )
    assessed = _frozen_bytes(
        tmp_path,
        "domain-assessed",
        "items.jsonl",
        _jsonl(assessed_records),
    )
    payload = {
        "schema": DOMAIN_SCHEMA,
        "domain_id": "selected_v2_waveform_cases",
        "observable": observable,
        "acceptance_gate": OBSERVABLE_GATES[observable],
        "parameters": {"kM": ["0.5", "1"], "sector": ["odd", "even"]},
        "selection_policy": "exact canonical two-case unit fixture",
        "item_index_identity": expected,
        "assessed_item_index_identity": assessed,
        "coverage": {
            "expected_items": 2,
            "assessed_items": len(assessed_records),
            "complete": complete,
        },
    }
    return _frozen_json(tmp_path, "domain", payload), payload


def _provenance(
    source: dict[str, object],
    domain: dict[str, object],
    *,
    science: bool,
    backend: str,
) -> dict[str, object]:
    return {
        "producer": "phase6-test-producer",
        "producer_version": "v1",
        "method": "frozen synthetic protocol fixture; no physical claim",
        "run_id": backend,
        "actual_arithmetic": {
            "backend": backend,
            "precision_kind": "BINARY_FLOAT" if science else "NOT_APPLICABLE",
            "decimal_digits": 16 if science else None,
        },
        "source_snapshot_identities": [source],
        "config_identities": [],
        "input_identities": [domain],
    }


def _descriptor(
    tmp_path: Path,
    name: str,
    *,
    role: str,
    independence: str,
    source: dict[str, object],
    domain: dict[str, object],
) -> dict[str, object]:
    schema = (
        THRESHOLD_SCHEMA if role == "THRESHOLD_POLICY" else f"phase6_test_{name}_v1"
    )
    if role == "THRESHOLD_POLICY":
        payload: dict[str, object] = {
            "schema": schema,
            "frozen_before_measurement": True,
            "global_green_permitted": False,
            "paper_agreement_primary_gate": False,
            "thresholds": {
                "maximum_relative_error": {
                    "comparison": "LE",
                    "units": "dimensionless",
                    "value": "1",
                }
            },
        }
    else:
        payload = {"schema": schema, "metric": "test-only", "value": "0"}
        if role in {"PRIMARY_SCIENCE", "INDEPENDENT_SCIENCE"}:
            payload.update(
                {
                    "scientific_evidence": True,
                    "kernel_unit_test_only": False,
                    "global_green_permitted": False,
                    "paper_agreement_primary_gate": False,
                }
            )
    artifact = _frozen_json(
        tmp_path,
        f"evidence-{name}",
        payload,
    )
    science = role in {"PRIMARY_SCIENCE", "INDEPENDENT_SCIENCE"}
    return {
        "identity": artifact,
        "media_type": "application/json",
        "expected_schema": schema,
        "role": role,
        "independence_class": independence,
        "provenance": _provenance(
            source,
            domain,
            science=science,
            backend=f"test-{name}",
        ),
    }


def _not_assessed(*, independent: bool | None = None) -> dict[str, object]:
    result: dict[str, object] = {
        "state": "NOT_ASSESSED",
        "reason": "not evaluated in this explicit domain",
        "coverage": "NONE",
        "metric": None,
        "measured_value": None,
        "threshold_value": None,
        "comparison": None,
        "units": None,
        "evidence_ids": [],
    }
    if independent is not None:
        result["independence_required"] = independent
    return result


def _partial(evidence_ids: list[str], *, independent: bool) -> dict[str, object]:
    return {
        "state": "PARTIAL",
        "reason": "one of two exact cases evaluated",
        "coverage": "INCOMPLETE",
        "metric": "maximum_relative_error",
        "measured_value": "0.1",
        "threshold_value": None,
        "comparison": None,
        "units": "dimensionless",
        "evidence_ids": evidence_ids,
        "independence_required": independent,
    }


def _pass(
    evidence_ids: list[str], *, independent: bool | None = None
) -> dict[str, object]:
    result: dict[str, object] = {
        "state": "PASS",
        "reason": "complete exact-domain fixture is below its frozen threshold",
        "coverage": "COMPLETE",
        "metric": "maximum_relative_error",
        "measured_value": "0.1",
        "threshold_value": "1",
        "comparison": "LE",
        "units": "dimensionless",
        "evidence_ids": evidence_ids,
    }
    if independent is not None:
        result["independence_required"] = independent
    return result


def _certificate(tmp_path: Path, *, state: str) -> dict[str, object]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    complete = state == "PASS"
    domain_identity, domain = _domain(tmp_path, complete=complete)
    source = _frozen_bytes(
        tmp_path, "source", "source.txt", b"immutable source snapshot\n"
    )
    primary = _descriptor(
        tmp_path,
        "primary",
        role="PRIMARY_SCIENCE",
        independence="SAME_IMPLEMENTATION",
        source=source,
        domain=domain_identity,
    )
    inventory: dict[str, object] = {"primary": primary}
    checks: dict[str, object] = {}
    if state == "PARTIAL":
        for index, (name, independent) in enumerate(
            REQUIRED_CHECKS["master_to_strain_flux"].items()
        ):
            checks[name] = (
                _partial(["primary"], independent=independent)
                if index == 0
                else _not_assessed(independent=independent)
            )
        numerical = {
            name: {"applicability": "REQUIRED", "assessment": _not_assessed()}
            for name in NUMERICAL_BUDGETS
        }
        convention = {
            name: {"applicability": "REQUIRED", "assessment": _not_assessed()}
            for name in CONVENTION_BUDGETS
        }
    else:
        inventory["independent"] = _descriptor(
            tmp_path,
            "independent",
            role="INDEPENDENT_SCIENCE",
            independence="ALGORITHMICALLY_INDEPENDENT",
            source=_frozen_bytes(
                tmp_path,
                "independent-source",
                "source.txt",
                b"independent immutable source snapshot\n",
            ),
            domain=domain_identity,
        )
        inventory["threshold"] = _descriptor(
            tmp_path,
            "threshold",
            role="THRESHOLD_POLICY",
            independence="NONE",
            source=source,
            domain=domain_identity,
        )
        for name, independent in REQUIRED_CHECKS["master_to_strain_flux"].items():
            evidence = ["primary", "threshold"]
            if independent:
                evidence.insert(1, "independent")
            checks[name] = _pass(evidence, independent=independent)
        numerical = {
            name: {
                "applicability": "REQUIRED",
                "assessment": _pass(["primary", "threshold"]),
            }
            for name in NUMERICAL_BUDGETS
        }
        convention = {
            name: {
                "applicability": "REQUIRED",
                "assessment": _pass(["primary", "threshold"]),
            }
            for name in CONVENTION_BUDGETS
        }
    observable = "master_to_strain_flux"
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
        "evidence_inventory": inventory,
        "acceptance_checks": checks,
        "numerical_budget": numerical,
        "convention_budget": convention,
        "secondary_evidence_ids": [],
        "limitations": ["synthetic protocol fixture; not scientific evidence"],
        "li_figure_agreement_primary_gate": False,
        "global_green_permitted": False,
        "state": state,
    }


def test_partial_and_pass_states_are_derived_per_domain(tmp_path: Path) -> None:
    partial = _certificate(tmp_path / "partial", state="PARTIAL")
    validate_certificate(partial)
    passed = _certificate(tmp_path / "passed", state="PASS")
    validate_certificate(passed)
    bundle = build_bundle([passed])
    validate_bundle(bundle)
    assert bundle["state_counts"] == {
        "NOT_ASSESSED": 0,
        "PARTIAL": 0,
        "PASS": 1,
        "FAIL": 0,
    }
    assert bundle["global_green_permitted"] is False


def test_claimed_pass_fails_closed_on_state_domain_or_budget_drift(
    tmp_path: Path,
) -> None:
    certificate = _certificate(tmp_path, state="PARTIAL")
    forged = deepcopy(certificate)
    forged["state"] = "PASS"
    with pytest.raises(ObservableEvidenceError, match="state is not derived"):
        validate_certificate(forged)
    missing_budget = deepcopy(certificate)
    del missing_budget["convention_budget"]["phase_origin"]
    with pytest.raises(ObservableEvidenceError, match="inventory changed"):
        validate_certificate(missing_budget)
    global_claim = deepcopy(certificate)
    global_claim["global_green_permitted"] = True
    with pytest.raises(ObservableEvidenceError, match="global or Li-primary"):
        validate_certificate(global_claim)


def test_pass_requires_primary_and_algorithmically_independent_evidence(
    tmp_path: Path,
) -> None:
    certificate = _certificate(tmp_path, state="PASS")
    forged = deepcopy(certificate)
    descriptor = forged["evidence_inventory"]["independent"]
    descriptor["independence_class"] = "SAME_IMPLEMENTATION"
    with pytest.raises(ObservableEvidenceError, match="not independently generated"):
        validate_certificate(forged)
    missing = deepcopy(certificate)
    check = missing["acceptance_checks"]["radial_flux_consistency"]
    check["evidence_ids"].remove("independent")
    with pytest.raises(ObservableEvidenceError, match="primary/independent"):
        validate_certificate(missing)


def test_independent_source_signature_and_threshold_bytes_are_bound(
    tmp_path: Path,
) -> None:
    certificate = _certificate(tmp_path, state="PASS")
    duplicate = deepcopy(certificate)
    duplicate["evidence_inventory"]["independent"]["provenance"] = deepcopy(
        duplicate["evidence_inventory"]["primary"]["provenance"]
    )
    with pytest.raises(ObservableEvidenceError, match="duplicates a primary"):
        validate_certificate(duplicate)
    threshold_drift = deepcopy(certificate)
    threshold_drift["acceptance_checks"]["master_strain_waveform"][
        "threshold_value"
    ] = "0.5"
    with pytest.raises(ObservableEvidenceError, match="not bound to its policy"):
        validate_certificate(threshold_drift)
    wrong_domain = deepcopy(certificate)
    primary_provenance = wrong_domain["evidence_inventory"]["primary"]["provenance"]
    primary_provenance["input_identities"] = [
        primary_provenance["source_snapshot_identities"][0]
    ]
    with pytest.raises(
        ObservableEvidenceError, match="not bound to the certificate domain"
    ):
        validate_certificate(wrong_domain)


@pytest.mark.parametrize("role", ["SOFTWARE_TEST_ONLY", "SECONDARY_PAPER_REGRESSION"])
def test_unit_or_paper_evidence_cannot_promote_science(
    tmp_path: Path, role: str
) -> None:
    certificate = _certificate(tmp_path, state="PASS")
    descriptor = certificate["evidence_inventory"]["primary"]
    descriptor["role"] = role
    descriptor["independence_class"] = "NONE"
    descriptor["provenance"]["actual_arithmetic"] = {
        "backend": "support-only",
        "precision_kind": "NOT_APPLICABLE",
        "decimal_digits": None,
    }
    with pytest.raises(
        ObservableEvidenceError,
        match="software-test|paper evidence|non-science|secondary-only",
    ):
        validate_certificate(certificate)


def test_zero_science_contract_cannot_be_relabelled_primary(tmp_path: Path) -> None:
    certificate = _certificate(tmp_path, state="PASS")
    descriptor = certificate["evidence_inventory"]["primary"]
    descriptor["identity"] = direct_file_identity(ZERO_CONTRACT_PATH)
    descriptor["expected_schema"] = ZERO_CONTRACT_SCHEMA
    with pytest.raises(ObservableEvidenceError, match="contract/unit/paper"):
        validate_certificate(certificate)


def test_hash_mode_and_threshold_policy_are_live_rechecked(tmp_path: Path) -> None:
    certificate = _certificate(tmp_path, state="PASS")
    no_policy = deepcopy(certificate)
    no_policy["acceptance_checks"]["master_strain_waveform"]["evidence_ids"].remove(
        "threshold"
    )
    with pytest.raises(ObservableEvidenceError, match="threshold lacks"):
        validate_certificate(no_policy)
    artifact = Path(
        str(certificate["evidence_inventory"]["primary"]["identity"]["path"])
    )
    os.chmod(artifact, 0o644)
    with pytest.raises(ObservableEvidenceError, match="mode 0444"):
        validate_certificate(certificate)


def test_publisher_is_fresh_immutable_and_reloads_exactly(tmp_path: Path) -> None:
    certificate = _certificate(tmp_path / "inputs", state="PARTIAL")
    submission = {
        "schema": SUBMISSION_SCHEMA,
        "certificates": [certificate],
    }
    submission_path = tmp_path / "submission.json"
    submission_path.write_bytes(canonical_json_bytes(submission))
    output = tmp_path / "published"
    result = publish_submission(submission_path, output)
    assert result == validate_published_root(output)
    assert stat.S_IMODE(output.lstat().st_mode) == 0o555
    assert all(stat.S_IMODE(path.lstat().st_mode) == 0o444 for path in output.iterdir())
    with pytest.raises(ObservableEvidenceError, match="overwrite"):
        publish_submission(submission_path, output)
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["publisher_generated_science"] is False
    assert manifest["global_green_permitted"] is False


def test_submission_and_bundle_reject_contract_only_empty_population(
    tmp_path: Path,
) -> None:
    certificate = _certificate(tmp_path, state="PARTIAL")
    bundle = build_bundle([certificate])
    bundle["contract_only"] = True
    with pytest.raises(ObservableEvidenceError, match="release policy"):
        validate_bundle(bundle)
    with pytest.raises(ObservableEvidenceError, match="at least one assessed"):
        build_bundle([])
