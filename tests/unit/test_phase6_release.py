from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import stat

import pytest

import scripts.phase6_publish_v1_release as release_publisher
from scripts.phase6_publish_v1_release import (
    preflight_submission,
    publish_submission,
    validate_published_root,
)
from schwgw.validation.phase6_domain import canonical_json_bytes
from schwgw.validation.phase6_release import (
    CERTIFICATE_SCHEMA,
    CONVENTION_BUDGET_FIELDS,
    EVIDENCE_ENVELOPE_SCHEMA,
    LEDGER_SCHEMA,
    NUMERICAL_BUDGET_FIELDS,
    REQUIRED_LEDGER_SLICES,
    SUBMISSION_SCHEMA,
    Phase6ReleaseError,
    authoritative_contract_bindings,
    build_ledger,
    direct_file_identity,
    load_evidence_inventory,
    validate_contract_bindings,
    validate_ledger,
    validate_submission,
)


POLICY = {
    "acceptance_is_per_observable_and_domain": True,
    "full_paper_figure_rerun_performed": False,
    "global_green_permitted": False,
    "li_figure_agreement_primary_gate": False,
    "publisher_generated_science": False,
}


def _frozen_bytes(
    tmp_path: Path, name: str, filename: str, data: bytes
) -> dict[str, object]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    root = tmp_path / name
    root.mkdir()
    path = root / filename
    path.write_bytes(data)
    os.chmod(path, 0o444)
    os.chmod(root, 0o555)
    return direct_file_identity(path)


def _frozen_json(
    tmp_path: Path, name: str, payload: object, *, filename: str = "artifact.json"
) -> dict[str, object]:
    return _frozen_bytes(tmp_path, name, filename, canonical_json_bytes(payload))


def _scope(gate: str, observable: str) -> dict[str, str]:
    return {
        "domain_id": f"domain_{gate.lower()}_{observable}",
        "gate": gate,
        "observable": observable,
    }


def _source_payload(
    name: str,
    *,
    role: str,
    state: str,
    blocker: dict[str, str] | None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema": f"schwgw_phase6_test_release_source_{name}_v1",
        "global_green_permitted": False,
        "paper_agreement_primary_gate": False,
    }
    if role in {"PRIMARY_SCIENCE", "INDEPENDENT_SCIENCE"}:
        implementation_hash = hashlib.sha256(
            f"implementation:{name}".encode()
        ).hexdigest()
        payload.update(
            {
                "scientific_evidence": True,
                "kernel_unit_test_only": False,
                "contract_only": False,
                "overall_state": state,
                "measurement": name,
                "implementation_source_sha256": implementation_hash,
            }
        )
    elif role == "BLOCKER":
        assert blocker is not None
        payload.update(
            {
                "status": "NOT_ASSESSED",
                "science_executed": False,
                "blocker": blocker["code"],
                "reason": blocker["reason"],
            }
        )
    elif role == "CONTRACT_ONLY":
        payload.update(
            {
                "contract_only": True,
                "solver_runs": 0,
                "scientific_pass_claimed": False,
            }
        )
    elif role == "FAILURE_DIAGNOSTIC":
        payload.update(
            {
                "status": "FAIL_CLOSED_EXECUTION",
                "failure": {"reason": "fixture failure"},
            }
        )
    elif role == "SECONDARY_PAPER_REGRESSION":
        payload.update(
            {
                "secondary_paper_regression": True,
                "paper_agreement_primary_gate": False,
            }
        )
    else:
        payload.update(
            {
                "verification_evidence": True,
                "verification_state": state,
                "verification_scope": name,
            }
        )
    return payload


def _envelope(
    tmp_path: Path,
    evidence_id: str,
    *,
    role: str,
    scopes: list[dict[str, str]],
    state: str,
    independence: str = "NONE",
    blocker: dict[str, str] | None = None,
    source_identity: dict[str, object] | None = None,
    additional_sources: list[dict[str, object]] | None = None,
) -> tuple[dict[str, object], dict[str, object]]:
    if source_identity is None:
        source = _source_payload(evidence_id, role=role, state=state, blocker=blocker)
        source_identity = _frozen_json(tmp_path, f"source-{evidence_id}", source)
        source_schema = source["schema"]
        raw = source
    else:
        raw = json.loads(Path(str(source_identity["path"])).read_text())
        source_schema = raw.get("schema", raw.get("schema_version"))
    scientific = role in {"PRIMARY_SCIENCE", "INDEPENDENT_SCIENCE"}
    implementation_hashes = (
        [str(raw["implementation_source_sha256"])]
        if scientific and "implementation_source_sha256" in raw
        else []
    )
    source_artifacts = [
        {
            "artifact_role": "RESULT",
            "expected_schema": source_schema,
            "identity": source_identity,
            "media_type": "application/json",
        }
    ]
    source_artifacts.extend(additional_sources or [])
    source_artifacts.sort(key=lambda item: str(item["identity"]["path"]))
    payload = {
        "schema": EVIDENCE_ENVELOPE_SCHEMA,
        "evidence_id": evidence_id,
        "role": role,
        "independence_class": independence,
        "declared_state": state,
        "scientific_evidence": scientific,
        "science_executed": scientific,
        "kernel_unit_test_only": role == "IMPLEMENTATION_VERIFICATION",
        "blocker": blocker,
        "implementation_source_sha256s": implementation_hashes,
        "scopes": sorted(
            scopes,
            key=lambda item: (item["gate"], item["observable"], item["domain_id"]),
        ),
        "source_artifacts": source_artifacts,
        "producer": "phase6 release test fixture",
        "method": "structural test fixture; no physical claim",
        "global_green_permitted": False,
        "li_figure_agreement_primary_gate": False,
        "full_paper_figure_rerun": False,
    }
    identity = _frozen_json(
        tmp_path, f"envelope-{evidence_id}", payload, filename="evidence.json"
    )
    return payload, identity


def _not_applicable_budget(fields: tuple[str, ...]) -> dict[str, object]:
    return {
        field: {
            "applicability": "NOT_APPLICABLE",
            "estimate": None,
            "evidence_ids": [],
            "reason": "not a physical observable uncertainty component",
            "state": "NOT_ASSESSED",
            "units": None,
        }
        for field in fields
    }


def _open_budget(fields: tuple[str, ...]) -> dict[str, object]:
    return {
        field: {
            "applicability": "REQUIRED",
            "estimate": None,
            "evidence_ids": [],
            "reason": "not assessed on this explicit parameter domain",
            "state": "NOT_ASSESSED",
            "units": "dimensionless",
        }
        for field in fields
    }


def _pass_budget(fields: tuple[str, ...], evidence_ids: list[str]) -> dict[str, object]:
    return {
        field: {
            "applicability": "REQUIRED",
            "estimate": "0.001",
            "evidence_ids": sorted(evidence_ids),
            "reason": "complete synthetic protocol fixture is below its frozen threshold",
            "state": "PASS",
            "units": "dimensionless",
        }
        for field in fields
    }


def _certificate(
    gate: str,
    observable: str,
    *,
    state: str,
    evidence_ids: list[str],
    blocker: dict[str, str] | None,
) -> dict[str, object]:
    physical = gate not in {"V0", "V6"}
    complete = state == "PASS"
    return {
        "schema": CERTIFICATE_SCHEMA,
        "certificate_id": f"cert_{gate.lower()}_{observable}",
        "gate": gate,
        "observable": observable,
        "parameter_domain": {
            "coverage": {
                "assessed_items": 1 if complete else 0,
                "complete": complete,
                "expected_items": 1,
            },
            "description": f"exact {gate} {observable} protocol fixture domain",
            "domain_id": f"domain_{gate.lower()}_{observable}",
            "parameters": {"fixture_case": ["a"]},
            "selection_policy": "exact one-case structural fixture",
        },
        "state": state,
        "reason": "explicit per-observable and per-domain structural fixture",
        "primary_acceptance_gate": (
            "independent physical measurement and frozen thresholds"
            if physical
            else "frozen implementation and policy verification"
        ),
        "evidence_ids": sorted(evidence_ids),
        "numerical_uncertainty_budget": (
            _open_budget(NUMERICAL_BUDGET_FIELDS)
            if physical
            else _not_applicable_budget(NUMERICAL_BUDGET_FIELDS)
        ),
        "convention_uncertainty_budget": (
            _open_budget(CONVENTION_BUDGET_FIELDS)
            if physical
            else _not_applicable_budget(CONVENTION_BUDGET_FIELDS)
        ),
        "limitations": [] if complete else ["observable remains unassessed"],
        "blocker": blocker,
    }


def _base_submission(tmp_path: Path) -> dict[str, object]:
    physical_slices = sorted(
        REQUIRED_LEDGER_SLICES
        - {
            ("V0", "claim_provenance_cleanup"),
            ("V6", "release_uncertainty_policy"),
        }
    )
    blocker = {
        "code": "BLOCKED_BY_RUNTIME",
        "reason": "independent runtime is intentionally unavailable in this fixture",
    }
    _, blocker_identity = _envelope(
        tmp_path,
        "blocker_runtime",
        role="BLOCKER",
        scopes=[_scope(gate, observable) for gate, observable in physical_slices],
        state="NOT_ASSESSED",
        blocker=blocker,
    )
    _, implementation_identity = _envelope(
        tmp_path,
        "implementation_v0",
        role="IMPLEMENTATION_VERIFICATION",
        scopes=[_scope("V0", "claim_provenance_cleanup")],
        state="PASS",
    )
    _, policy_identity = _envelope(
        tmp_path,
        "policy_v6",
        role="POLICY_VERIFICATION",
        scopes=[_scope("V6", "release_uncertainty_policy")],
        state="PASS",
    )
    certificates = [
        _certificate(
            "V0",
            "claim_provenance_cleanup",
            state="PASS",
            evidence_ids=["implementation_v0"],
            blocker=None,
        )
    ]
    certificates.extend(
        _certificate(
            gate,
            observable,
            state="NOT_ASSESSED",
            evidence_ids=["blocker_runtime"],
            blocker=blocker,
        )
        for gate, observable in physical_slices
    )
    certificates.append(
        _certificate(
            "V6",
            "release_uncertainty_policy",
            state="PASS",
            evidence_ids=["policy_v6"],
            blocker=None,
        )
    )
    certificates.sort(key=lambda item: item["certificate_id"])
    return {
        "schema": SUBMISSION_SCHEMA,
        "release_id": "phase6_v1_test_release",
        "contract_bindings": authoritative_contract_bindings(),
        "evidence_envelope_identities": [
            blocker_identity,
            implementation_identity,
            policy_identity,
        ],
        "certificates": certificates,
        "policy": deepcopy(POLICY),
    }


def _certificate_by_gate(
    submission: dict[str, object], gate: str, observable: str
) -> dict[str, object]:
    return next(
        item
        for item in submission["certificates"]
        if item["gate"] == gate and item["observable"] == observable
    )


def _add_v1_science(
    tmp_path: Path,
    submission: dict[str, object],
    *,
    independent: bool,
) -> None:
    scope = _scope("V1", "radial_s_matrix_flux")
    identities = list(submission["evidence_envelope_identities"])
    _, primary_identity = _envelope(
        tmp_path,
        "primary_v1",
        role="PRIMARY_SCIENCE",
        scopes=[scope],
        state="PASS",
        independence="SAME_IMPLEMENTATION",
    )
    identities.append(primary_identity)
    evidence_ids = ["primary_v1"]
    if independent:
        _, independent_identity = _envelope(
            tmp_path,
            "independent_v1",
            role="INDEPENDENT_SCIENCE",
            scopes=[scope],
            state="PASS",
            independence="EXTERNAL_SOURCE",
        )
        identities.append(independent_identity)
        evidence_ids.append("independent_v1")
    identities.sort(
        key=lambda identity: json.loads(Path(str(identity["path"])).read_text())[
            "evidence_id"
        ]
    )
    submission["evidence_envelope_identities"] = identities
    certificate = _certificate_by_gate(submission, "V1", "radial_s_matrix_flux")
    certificate["state"] = "PASS"
    certificate["blocker"] = None
    certificate["limitations"] = []
    certificate["evidence_ids"] = sorted(evidence_ids)
    certificate["parameter_domain"]["coverage"] = {
        "assessed_items": 1,
        "complete": True,
        "expected_items": 1,
    }
    certificate["numerical_uncertainty_budget"] = _pass_budget(
        NUMERICAL_BUDGET_FIELDS, evidence_ids
    )
    certificate["convention_uncertainty_budget"] = _pass_budget(
        CONVENTION_BUDGET_FIELDS, evidence_ids
    )


def test_authoritative_contract_bindings_are_exact_v3_v4_v8_v2() -> None:
    bindings = authoritative_contract_bindings()

    assert set(bindings) == {
        "domain_v3",
        "execution_v4",
        "aggregation_v8",
        "observable_v2",
    }
    assert (
        bindings["observable_v2"]["contract_identity"]["sha256"]
        == "3853df8fbc245b81552198d99201778e4020d82f618e3f80ac745768fc3d104b"
    )
    validate_contract_bindings(bindings)


def test_submission_and_ledger_keep_states_per_certificate(tmp_path: Path) -> None:
    submission = _base_submission(tmp_path)

    inventory, certificates = validate_submission(submission)
    ledger = build_ledger(submission, submission_sha256="a" * 64)

    assert len(inventory) == 3
    assert len(certificates) == 9
    assert ledger["schema"] == LEDGER_SCHEMA
    assert ledger["state_counts"] == {
        "NOT_ASSESSED": 7,
        "PARTIAL": 0,
        "PASS": 2,
        "FAIL": 0,
    }
    assert ledger["global_status"] is None
    assert ledger["policy"]["global_green_permitted"] is False
    validate_ledger(ledger)


def test_publisher_uses_o_excl_and_seals_exact_root(tmp_path: Path) -> None:
    submission = _base_submission(tmp_path)
    submission_path = tmp_path / "submission.json"
    submission_path.write_bytes(canonical_json_bytes(submission))
    output = tmp_path / "formal_release"

    result = publish_submission(submission_path, output)

    assert result["certificate_count"] == 9
    assert stat.S_IMODE(output.stat().st_mode) == 0o555
    assert {path.name for path in output.iterdir()} == {
        "manifest.json",
        "release_ledger.json",
    }
    assert all(stat.S_IMODE(path.stat().st_mode) == 0o444 for path in output.iterdir())
    assert validate_published_root(output) == result
    with pytest.raises(Phase6ReleaseError, match="overwrite"):
        publish_submission(submission_path, output)


def test_preflight_validates_everything_without_writing_output(tmp_path: Path) -> None:
    submission = _base_submission(tmp_path)
    submission_path = tmp_path / "submission.json"
    submission_path.write_bytes(canonical_json_bytes(submission))

    result = preflight_submission(submission_path)

    assert result["certificate_count"] == 9
    assert result["evidence_envelope_count"] == 3
    assert result["global_status"] is None
    assert result["output_written"] is False
    assert {path.name for path in tmp_path.iterdir()} == {
        "envelope-blocker_runtime",
        "envelope-implementation_v0",
        "envelope-policy_v6",
        "source-blocker_runtime",
        "source-implementation_v0",
        "source-policy_v6",
        "submission.json",
    }


def test_publisher_seals_partial_root_after_publication_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    submission = _base_submission(tmp_path)
    submission_path = tmp_path / "submission.json"
    submission_path.write_bytes(canonical_json_bytes(submission))
    output = tmp_path / "failed-release"
    original = release_publisher._publish_file
    calls = 0

    def fail_on_manifest(path: Path, data: bytes) -> dict[str, object]:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("injected manifest publication failure")
        return original(path, data)

    monkeypatch.setattr(release_publisher, "_publish_file", fail_on_manifest)
    with pytest.raises(RuntimeError, match="injected"):
        publish_submission(submission_path, output)

    assert stat.S_IMODE(output.stat().st_mode) == 0o555
    assert {path.name for path in output.iterdir()} == {"release_ledger.json"}
    assert stat.S_IMODE((output / "release_ledger.json").stat().st_mode) == 0o444


def test_published_manifest_tampering_is_detected(tmp_path: Path) -> None:
    submission = _base_submission(tmp_path)
    submission_path = tmp_path / "submission.json"
    submission_path.write_bytes(canonical_json_bytes(submission))
    output = tmp_path / "tamper-release"
    publish_submission(submission_path, output)
    manifest_path = output / "manifest.json"
    os.chmod(output, 0o755)
    os.chmod(manifest_path, 0o644)
    manifest = json.loads(manifest_path.read_text())
    manifest["pass_certificate_count"] += 1
    manifest_path.write_bytes(canonical_json_bytes(manifest))
    os.chmod(manifest_path, 0o444)
    os.chmod(output, 0o555)

    with pytest.raises(Phase6ReleaseError, match="not derived"):
        validate_published_root(output)


def test_stale_contract_hash_and_old_label_fail_closed(tmp_path: Path) -> None:
    submission = _base_submission(tmp_path)
    submission["contract_bindings"]["observable_v2"]["contract_identity"]["sha256"] = (
        "0" * 64
    )

    with pytest.raises(Phase6ReleaseError, match="identity no longer matches"):
        validate_submission(submission)

    submission = _base_submission(tmp_path / "second")
    submission["contract_bindings"]["observable_v1"] = submission[
        "contract_bindings"
    ].pop("observable_v2")
    with pytest.raises(Phase6ReleaseError, match="contract bindings schema"):
        validate_submission(submission)


def test_mutable_and_missing_evidence_fail_closed(tmp_path: Path) -> None:
    submission = _base_submission(tmp_path)
    identity = submission["evidence_envelope_identities"][0]
    path = Path(str(identity["path"]))
    os.chmod(path.parent, 0o755)

    with pytest.raises(Phase6ReleaseError, match="0555"):
        validate_submission(submission)

    os.chmod(path.parent, 0o555)
    submission["evidence_envelope_identities"][0]["path"] = str(
        tmp_path / "absent.json"
    )
    with pytest.raises(Phase6ReleaseError, match="cannot identify"):
        validate_submission(submission)


def test_duplicate_source_bytes_cannot_be_role_laundered(tmp_path: Path) -> None:
    submission = _base_submission(tmp_path)
    first_identity = submission["evidence_envelope_identities"][0]
    first = json.loads(Path(str(first_identity["path"])).read_text())
    shared_source = first["source_artifacts"][0]["identity"]
    _, duplicate = _envelope(
        tmp_path,
        "blocker_runtime_copy",
        role="BLOCKER",
        scopes=[_scope("V1", "radial_s_matrix_flux")],
        state="NOT_ASSESSED",
        blocker=first["blocker"],
        source_identity=shared_source,
    )
    identities = list(submission["evidence_envelope_identities"])
    identities.append(duplicate)
    identities.sort(
        key=lambda identity: json.loads(Path(str(identity["path"])).read_text())[
            "evidence_id"
        ]
    )

    with pytest.raises(Phase6ReleaseError, match="duplicated across envelopes"):
        load_evidence_inventory(identities)


def test_shared_immutable_input_is_not_mistaken_for_duplicate_result(
    tmp_path: Path,
) -> None:
    domain_identity = authoritative_contract_bindings()["domain_v3"][
        "contract_identity"
    ]
    shared_input = {
        "artifact_role": "INPUT",
        "expected_schema": "schwgw_phase6_v1_domain_contract_v1",
        "identity": domain_identity,
        "media_type": "application/json",
    }
    _, first = _envelope(
        tmp_path,
        "implementation_a",
        role="IMPLEMENTATION_VERIFICATION",
        scopes=[_scope("V0", "claim_provenance_cleanup")],
        state="PASS",
        additional_sources=[shared_input],
    )
    _, second = _envelope(
        tmp_path,
        "policy_b",
        role="POLICY_VERIFICATION",
        scopes=[_scope("V6", "release_uncertainty_policy")],
        state="PASS",
        additional_sources=[shared_input],
    )

    assert set(load_evidence_inventory([first, second])) == {
        "implementation_a",
        "policy_b",
    }


def test_canonical_jsonl_preserves_frozen_domain_order(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[2]
    union_identity = direct_file_identity(
        project_root / "runs/phase6/v1_domain_freeze_v3_20260806/D_union.jsonl"
    )
    _, envelope = _envelope(
        tmp_path,
        "implementation_with_domain",
        role="IMPLEMENTATION_VERIFICATION",
        scopes=[_scope("V0", "claim_provenance_cleanup")],
        state="PASS",
        additional_sources=[
            {
                "artifact_role": "INPUT",
                "expected_schema": None,
                "identity": union_identity,
                "media_type": "application/x-jsonlines",
            }
        ],
    )

    assert set(load_evidence_inventory([envelope])) == {"implementation_with_domain"}


def test_blocker_cannot_pretend_to_be_science(tmp_path: Path) -> None:
    blocker = {
        "code": "BLOCKED_BY_RUNTIME",
        "reason": "runtime unavailable",
    }
    blocker_source = _source_payload(
        "blocked", role="BLOCKER", state="NOT_ASSESSED", blocker=blocker
    )
    blocker_source["implementation_source_sha256"] = hashlib.sha256(
        b"fake-blocked-implementation"
    ).hexdigest()
    source_identity = _frozen_json(tmp_path, "blocked-source", blocker_source)

    _, identity = _envelope(
        tmp_path,
        "fake_science",
        role="PRIMARY_SCIENCE",
        scopes=[_scope("V1", "radial_s_matrix_flux")],
        state="PASS",
        independence="SAME_IMPLEMENTATION",
        source_identity=source_identity,
    )
    with pytest.raises(Phase6ReleaseError, match="science envelope lacks"):
        load_evidence_inventory([identity])


def test_finite_float_in_science_source_is_allowed_but_nan_is_rejected(
    tmp_path: Path,
) -> None:
    source = _source_payload(
        "float_measurement",
        role="PRIMARY_SCIENCE",
        state="PARTIAL",
        blocker=None,
    )
    source["runtime_seconds"] = 0.125
    source_identity = _frozen_json(tmp_path, "float-source", source)
    _, identity = _envelope(
        tmp_path,
        "float_science",
        role="PRIMARY_SCIENCE",
        scopes=[_scope("V1", "radial_s_matrix_flux")],
        state="PARTIAL",
        independence="SAME_IMPLEMENTATION",
        source_identity=source_identity,
    )

    assert set(load_evidence_inventory([identity])) == {"float_science"}

    nan_source = deepcopy(source)
    nan_source["runtime_seconds"] = float("nan")
    nan_identity = _frozen_json(tmp_path, "nan-source", nan_source)
    _, nan_envelope = _envelope(
        tmp_path,
        "nan_science",
        role="PRIMARY_SCIENCE",
        scopes=[_scope("V1", "radial_s_matrix_flux")],
        state="PARTIAL",
        independence="SAME_IMPLEMENTATION",
        source_identity=nan_identity,
    )
    with pytest.raises(Phase6ReleaseError, match="non-finite"):
        load_evidence_inventory([nan_envelope])


def test_certificate_blocker_must_match_immutable_blocker_evidence(
    tmp_path: Path,
) -> None:
    submission = _base_submission(tmp_path)
    certificate = _certificate_by_gate(submission, "V1", "radial_s_matrix_flux")
    certificate["blocker"] = {
        "code": "BLOCKED_BY_RUNTIME",
        "reason": "a different runtime explanation",
    }

    with pytest.raises(Phase6ReleaseError, match="does not match"):
        validate_submission(submission)


def test_certificate_text_cannot_smuggle_a_global_green_claim(tmp_path: Path) -> None:
    submission = _base_submission(tmp_path)
    certificate = _certificate_by_gate(submission, "V0", "claim_provenance_cleanup")
    certificate["reason"] = "the project-wide result is GREEN"

    with pytest.raises(Phase6ReleaseError, match="global result"):
        validate_submission(submission)


def test_physical_pass_requires_independent_science(tmp_path: Path) -> None:
    submission = _base_submission(tmp_path)
    _add_v1_science(tmp_path, submission, independent=False)

    with pytest.raises(Phase6ReleaseError, match="primary and independent"):
        validate_submission(submission)


def test_physical_pass_with_two_independent_sources_and_budgets_is_valid(
    tmp_path: Path,
) -> None:
    submission = _base_submission(tmp_path)
    _add_v1_science(tmp_path, submission, independent=True)

    _, certificates = validate_submission(submission)
    v1 = next(
        certificate for certificate in certificates if certificate["gate"] == "V1"
    )

    assert v1["state"] == "PASS"
    assert all(
        record["state"] == "PASS"
        for record in v1["numerical_uncertainty_budget"].values()
    )
    assert all(
        record["state"] == "PASS"
        for record in v1["convention_uncertainty_budget"].values()
    )


def test_independent_pass_cannot_reuse_primary_implementation_source(
    tmp_path: Path,
) -> None:
    submission = _base_submission(tmp_path)
    _add_v1_science(tmp_path, submission, independent=True)
    primary_identity = next(
        identity
        for identity in submission["evidence_envelope_identities"]
        if json.loads(Path(str(identity["path"])).read_text())["evidence_id"]
        == "primary_v1"
    )
    primary_envelope = json.loads(Path(str(primary_identity["path"])).read_text())
    shared_hash = primary_envelope["implementation_source_sha256s"][0]
    source = _source_payload(
        "independent_shared_source",
        role="INDEPENDENT_SCIENCE",
        state="PASS",
        blocker=None,
    )
    source["implementation_source_sha256"] = shared_hash
    source_identity = _frozen_json(tmp_path / "shared-independent", "source", source)
    _, replacement = _envelope(
        tmp_path / "shared-independent",
        "independent_v1",
        role="INDEPENDENT_SCIENCE",
        scopes=[_scope("V1", "radial_s_matrix_flux")],
        state="PASS",
        independence="EXTERNAL_SOURCE",
        source_identity=source_identity,
    )
    submission["evidence_envelope_identities"] = [
        replacement
        if json.loads(Path(str(identity["path"])).read_text())["evidence_id"]
        == "independent_v1"
        else identity
        for identity in submission["evidence_envelope_identities"]
    ]

    with pytest.raises(Phase6ReleaseError, match="reuses an implementation source"):
        validate_submission(submission)


def test_missing_budget_component_and_secondary_paper_promotion_are_rejected(
    tmp_path: Path,
) -> None:
    submission = _base_submission(tmp_path)
    _add_v1_science(tmp_path, submission, independent=True)
    v1 = _certificate_by_gate(submission, "V1", "radial_s_matrix_flux")
    v1["numerical_uncertainty_budget"].pop("lmax")

    with pytest.raises(Phase6ReleaseError, match="numerical budget schema"):
        validate_submission(submission)

    submission = _base_submission(tmp_path / "secondary")
    scope = _scope("V1", "radial_s_matrix_flux")
    _, secondary = _envelope(
        tmp_path / "secondary",
        "paper_secondary",
        role="SECONDARY_PAPER_REGRESSION",
        scopes=[scope],
        state="PASS",
    )
    identities = list(submission["evidence_envelope_identities"])
    identities.append(secondary)
    identities.sort(
        key=lambda identity: json.loads(Path(str(identity["path"])).read_text())[
            "evidence_id"
        ]
    )
    submission["evidence_envelope_identities"] = identities
    v1 = _certificate_by_gate(submission, "V1", "radial_s_matrix_flux")
    v1["state"] = "PASS"
    v1["blocker"] = None
    v1["limitations"] = []
    v1["evidence_ids"] = ["paper_secondary"]
    v1["parameter_domain"]["coverage"] = {
        "assessed_items": 1,
        "complete": True,
        "expected_items": 1,
    }
    v1["numerical_uncertainty_budget"] = _pass_budget(
        NUMERICAL_BUDGET_FIELDS, ["paper_secondary"]
    )
    v1["convention_uncertainty_budget"] = _pass_budget(
        CONVENTION_BUDGET_FIELDS, ["paper_secondary"]
    )

    with pytest.raises(Phase6ReleaseError, match="promoted by invalid evidence"):
        validate_submission(submission)


@pytest.mark.parametrize(
    "primary_gate",
    ["Li agreement", "paper-figure similarity", "raster match"],
)
def test_li_paper_and_raster_are_never_primary_gates(
    tmp_path: Path, primary_gate: str
) -> None:
    submission = _base_submission(tmp_path)
    certificate = _certificate_by_gate(submission, "V3", "spin2_scattering_limits")
    certificate["primary_acceptance_gate"] = primary_gate

    with pytest.raises(Phase6ReleaseError, match="cannot be a primary gate"):
        validate_submission(submission)


def test_global_policy_and_full_paper_rerun_are_rejected(tmp_path: Path) -> None:
    submission = _base_submission(tmp_path)
    submission["policy"]["global_green_permitted"] = True
    with pytest.raises(Phase6ReleaseError, match="release policy"):
        validate_submission(submission)

    submission = _base_submission(tmp_path / "rerun")
    submission["policy"]["full_paper_figure_rerun_performed"] = True
    with pytest.raises(Phase6ReleaseError, match="release policy"):
        validate_submission(submission)


def test_every_v0_v1_v1q_v2_to_v6_slice_is_required(tmp_path: Path) -> None:
    submission = _base_submission(tmp_path)
    submission["certificates"] = [
        certificate
        for certificate in submission["certificates"]
        if certificate["gate"] != "V1Q"
    ]

    with pytest.raises(Phase6ReleaseError, match="omits required gate slices"):
        validate_submission(submission)


def test_duplicate_observable_domain_certificate_is_rejected(tmp_path: Path) -> None:
    submission = _base_submission(tmp_path)
    duplicate = deepcopy(submission["certificates"][0])
    duplicate["certificate_id"] = "cert_v0_duplicate"
    submission["certificates"].append(duplicate)
    submission["certificates"].sort(key=lambda item: item["certificate_id"])

    with pytest.raises(Phase6ReleaseError, match="duplicate certificate"):
        validate_submission(submission)


def test_noncanonical_submission_is_not_published(tmp_path: Path) -> None:
    submission = _base_submission(tmp_path)
    submission_path = tmp_path / "pretty.json"
    submission_path.write_text(json.dumps(submission, indent=2), encoding="utf-8")

    with pytest.raises(Phase6ReleaseError, match="canonical JSON"):
        publish_submission(submission_path, tmp_path / "unused-release")


def test_ledger_cannot_acquire_a_global_status(tmp_path: Path) -> None:
    submission = _base_submission(tmp_path)
    ledger = build_ledger(submission, submission_sha256="b" * 64)
    ledger["global_status"] = "PASS"

    with pytest.raises(Phase6ReleaseError, match="global status"):
        validate_ledger(ledger)


def test_symlink_and_hardlink_evidence_aliases_are_rejected(tmp_path: Path) -> None:
    frozen = _frozen_json(
        tmp_path,
        "original",
        {"schema": "alias_fixture_v1", "global_green_permitted": False},
    )
    original = Path(str(frozen["path"]))
    symlink = tmp_path / "symlink.json"
    symlink.symlink_to(original)
    with pytest.raises(Phase6ReleaseError, match="symlink"):
        direct_file_identity(symlink)

    hardlink_root = tmp_path / "hardlink-root"
    hardlink_root.mkdir()
    hardlink = hardlink_root / "hardlink.json"
    os.link(original, hardlink)
    os.chmod(hardlink_root, 0o555)
    with pytest.raises(Phase6ReleaseError, match="nlink1"):
        direct_file_identity(original)
