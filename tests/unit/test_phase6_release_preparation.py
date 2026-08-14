from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
import stat

import pytest

import scripts.phase6_prepare_v1_release as preparation_cli
import schwgw.validation.phase6_release_preparation as preparation
from schwgw.validation.phase6_domain import canonical_json_bytes
from schwgw.validation.phase6_release import (
    CONVENTION_BUDGET_FIELDS,
    NUMERICAL_BUDGET_FIELDS,
    REQUIRED_LEDGER_SLICES,
)
from schwgw.validation.phase6_release_preparation import (
    POLICY,
    PRODUCTION_FINITE_RADIUS_RESULT_SCHEMA,
    RELEASE_MAP_SCHEMA,
    TYPED_PHYSICAL_RESULT_SCHEMA,
    V0_VERIFICATION_SCHEMA,
    DerivedEvidence,
    Phase6PreparationError,
    preflight_release_map,
    publish_preparation,
    validate_published_preparation,
)


def _domain(
    gate: str, observable: str, *, expected_items: int = 1
) -> dict[str, object]:
    return {
        "domain_id": f"domain_{gate.lower()}_{observable}",
        "description": f"explicit {gate} {observable} test domain",
        "parameters": {"case": ["a"]},
        "selection_policy": "exact canonical structural test domain",
        "expected_items": expected_items,
    }


def _base_map() -> dict[str, object]:
    certificates = [
        {
            "certificate_id": f"cert_{gate.lower()}_{observable}",
            "gate": gate,
            "observable": observable,
            "parameter_domain": _domain(gate, observable),
            "evidence_ids": [],
            "primary_acceptance_gate": (
                "independent physical measurements and frozen uncertainty thresholds"
                if gate not in {"V0", "V6"}
                else "machine-readable implementation and policy verification"
            ),
        }
        for gate, observable in sorted(REQUIRED_LEDGER_SLICES)
    ]
    certificates.sort(key=lambda item: str(item["certificate_id"]))
    return {
        "schema": RELEASE_MAP_SCHEMA,
        "preparation_id": "phase6_v1_test_preparation",
        "release_id": "phase6_v1_test_release",
        "sources": [],
        "certificates": certificates,
        "policy": deepcopy(POLICY),
    }


def _certificate(
    release_map: dict[str, object], gate: str, observable: str
) -> dict[str, object]:
    return next(
        certificate
        for certificate in release_map["certificates"]
        if certificate["gate"] == gate and certificate["observable"] == observable
    )


def _frozen_json_root(
    tmp_path: Path, name: str, filename: str, payload: object
) -> tuple[Path, str]:
    root = tmp_path.resolve() / name
    root.mkdir()
    raw = canonical_json_bytes(payload)
    path = root / filename
    path.write_bytes(raw)
    os.chmod(path, 0o444)
    os.chmod(root, 0o555)
    return root, preparation.sha256_bytes(raw)


def _source(
    evidence_id: str,
    adapter: str,
    root: Path,
    artifacts: dict[str, str],
    *,
    selector: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "evidence_id": evidence_id,
        "adapter": adapter,
        "origin_root": str(root),
        "expected_artifacts": [
            {"relative_path": name, "sha256": digest}
            for name, digest in sorted(artifacts.items())
        ],
        "selector": selector or {},
    }


def _typed_budget(
    fields: tuple[str, ...], *, state: str
) -> dict[str, dict[str, object]]:
    return {
        name: {
            "state": state,
            "estimate": "0.001" if state in {"PASS", "FAIL"} else None,
            "units": "dimensionless",
            "reason": "strict typed test evidence budget",
        }
        for name in fields
    }


def _typed_report(
    *,
    schema: str,
    result_id: str,
    role: str,
    independence: str,
    gate: str,
    observable: str,
    domain: dict[str, object],
    state: str,
    implementation_hash: str,
    observer_test: str = "PASS",
) -> dict[str, object]:
    item_state = "PASS" if state == "PASS" else "PARTIAL"
    budget_state = "PASS" if state == "PASS" else "PARTIAL"
    item_results = [
        {"item_id": f"item_{index:03d}", "state": item_state}
        for index in range(int(domain["expected_items"]))
    ]
    report_domain = {
        **deepcopy(domain),
        "expected_item_ids": [item["item_id"] for item in item_results],
    }
    return {
        "schema": schema,
        "result_id": result_id,
        "role": role,
        "independence_class": independence,
        "gate": gate,
        "observable": observable,
        "parameter_domain": report_domain,
        "item_results": item_results,
        "state": state,
        "reason": "strict typed fixture result",
        "limitations": ["synthetic protocol fixture; no real physical claim"],
        "implementation_source_sha256s": [implementation_hash],
        "numerical_uncertainty_budget": _typed_budget(
            NUMERICAL_BUDGET_FIELDS, state=budget_state
        ),
        "convention_uncertainty_budget": _typed_budget(
            CONVENTION_BUDGET_FIELDS, state=budget_state
        ),
        "scientific_evidence": True,
        "science_executed": True,
        "kernel_unit_test_only": False,
        "global_green_permitted": False,
        "li_figure_agreement_primary_gate": False,
        "full_paper_figure_rerun": False,
        "observer_qualification": {
            "output_kind": (
                "DETECTOR_RESPONSE"
                if observer_test == "PASS"
                else "FINITE_RADIUS_TIDAL_RESPONSE"
            ),
            "worldline_tetrad_pure_gauge_test": observer_test,
            "detector_response_claim_permitted": observer_test == "PASS",
        },
    }


def _v0_report() -> dict[str, object]:
    checks = {}
    for index, name in enumerate(
        (
            "stale_production_metadata",
            "legacy_np_isolation",
            "legacy_pseudoinverse_isolation",
            "full_test_suite",
        )
    ):
        checks[name] = {
            "state": "PASS",
            "command": f"machine-readable verification command {index}",
            "passed": 1,
            "failed": 0,
            "skipped": 0,
            "report_sha256": f"{index + 1:064x}",
        }
    return {
        "schema": V0_VERIFICATION_SCHEMA,
        "verification_id": "v0_final_verification",
        "checks": checks,
        "source_report_sha256s": sorted(
            {check["report_sha256"] for check in checks.values()}
        ),
        "verification_state": "PASS",
        "global_green_permitted": False,
        "li_figure_agreement_primary_gate": False,
    }


def test_empty_map_is_fail_closed_with_v0_partial_and_v6_pass() -> None:
    result = preflight_release_map(_base_map())

    assert result["source_evidence_count"] == 0
    assert result["generated_support_count"] == 9
    assert result["certificate_state_counts"] == {
        "NOT_ASSESSED": 7,
        "PARTIAL": 1,
        "PASS": 1,
        "FAIL": 0,
    }
    assert result["certificate_states"]["cert_v0_claim_provenance_cleanup"] == "PARTIAL"
    assert result["certificate_states"]["cert_v6_release_uncertainty_policy"] == "PASS"
    assert result["global_status"] is None
    assert result["output_written"] is False


def test_publish_preparation_is_immutable_and_release_submission_valid(
    tmp_path: Path,
) -> None:
    output = tmp_path.resolve() / "preparation"

    result = publish_preparation(_base_map(), output)

    assert result == validate_published_preparation(output)
    assert result["certificate_count"] == 9
    assert stat.S_IMODE(output.stat().st_mode) == 0o555
    assert all(
        stat.S_IMODE(path.stat().st_mode) == (0o555 if path.is_dir() else 0o444)
        for path in output.rglob("*")
    )
    with pytest.raises(Phase6PreparationError, match="overwrite"):
        publish_preparation(_base_map(), output)


def test_published_preparation_rejects_extra_sealed_layout_entries(
    tmp_path: Path,
) -> None:
    output = tmp_path.resolve() / "preparation-extra-layout"
    publish_preparation(_base_map(), output)
    normalized = output / "normalized"
    os.chmod(normalized, 0o755)
    (normalized / "unmanifested_evidence").mkdir(mode=0o555)
    os.chmod(normalized, 0o555)

    with pytest.raises(
        Phase6PreparationError, match="normalized directory inventory changed"
    ):
        validate_published_preparation(output)


def test_future_campaign_and_final_v0_roots_are_typed_not_path_hardcoded(
    tmp_path: Path,
) -> None:
    release_map = _base_map()
    v4_certificate = _certificate(release_map, "V4", "finite_radius_tidal_detector")
    v4_domain = _domain("V4", "finite_radius_tidal_detector", expected_items=2)
    v4_certificate["parameter_domain"] = v4_domain
    v4_certificate["evidence_ids"] = ["future_finite_radius_campaign"]
    v4_report = _typed_report(
        schema=PRODUCTION_FINITE_RADIUS_RESULT_SCHEMA,
        result_id="future_finite_radius_campaign",
        role="PRIMARY_SCIENCE",
        independence="SAME_IMPLEMENTATION",
        gate="V4",
        observable="finite_radius_tidal_detector",
        domain=v4_domain,
        state="PARTIAL",
        implementation_hash="a" * 64,
        observer_test="PARTIAL",
    )
    v4_root, v4_sha = _frozen_json_root(
        tmp_path, "future-campaign-root", "report.json", v4_report
    )

    v0_certificate = _certificate(release_map, "V0", "claim_provenance_cleanup")
    v0_certificate["evidence_ids"] = ["future_v0_final_verification"]
    v0_root, v0_sha = _frozen_json_root(
        tmp_path, "future-v0-root", "verification.json", _v0_report()
    )
    release_map["sources"] = sorted(
        [
            _source(
                "future_finite_radius_campaign",
                "PRODUCTION_FINITE_RADIUS_V1",
                v4_root,
                {"report.json": v4_sha},
            ),
            _source(
                "future_v0_final_verification",
                "V0_IMPLEMENTATION_VERIFICATION_V1",
                v0_root,
                {"verification.json": v0_sha},
            ),
        ],
        key=lambda item: str(item["evidence_id"]),
    )
    output = tmp_path.resolve() / "composed"

    result = publish_preparation(release_map, output)

    assert result["certificate_state_counts"] == {
        "NOT_ASSESSED": 6,
        "PARTIAL": 1,
        "PASS": 2,
        "FAIL": 0,
    }
    submission = json.loads((output / "canonical_submission.json").read_text())
    states = {
        item["certificate_id"]: item["state"] for item in submission["certificates"]
    }
    assert states["cert_v0_claim_provenance_cleanup"] == "PASS"
    assert states["cert_v4_finite_radius_tidal_detector"] == "PARTIAL"
    projection = json.loads(
        (
            output / "normalized" / "future_finite_radius_campaign" / "result.json"
        ).read_text()
    )
    snapshot = projection["source_snapshots"][0]
    assert snapshot["origin_identity"]["path"] == str(v4_root / "report.json")
    assert snapshot["origin_identity"]["sha256"] == v4_sha
    assert snapshot["snapshot_identity"]["sha256"] == v4_sha
    assert snapshot["copy_sha256_equal"] is True
    assert projection["publisher_generated_science"] is False
    assert projection["normalization_is_new_science"] is False


def test_two_disjoint_typed_sources_can_pass_only_one_explicit_domain(
    tmp_path: Path,
) -> None:
    release_map = _base_map()
    certificate = _certificate(release_map, "V3", "spin2_scattering_limits")
    domain = _domain("V3", "spin2_scattering_limits", expected_items=2)
    certificate["parameter_domain"] = domain
    certificate["evidence_ids"] = ["independent_v3", "primary_v3"]
    sources = []
    for evidence_id, role, independence, digest in (
        (
            "independent_v3",
            "INDEPENDENT_SCIENCE",
            "ALGORITHMICALLY_INDEPENDENT",
            "b" * 64,
        ),
        ("primary_v3", "PRIMARY_SCIENCE", "SAME_IMPLEMENTATION", "a" * 64),
    ):
        report = _typed_report(
            schema=TYPED_PHYSICAL_RESULT_SCHEMA,
            result_id=evidence_id,
            role=role,
            independence=independence,
            gate="V3",
            observable="spin2_scattering_limits",
            domain=domain,
            state="PASS",
            implementation_hash=digest,
        )
        root, report_sha = _frozen_json_root(
            tmp_path, f"root-{evidence_id}", "report.json", report
        )
        sources.append(
            _source(
                evidence_id,
                "TYPED_PHYSICAL_RESULT_V1",
                root,
                {"report.json": report_sha},
            )
        )
    release_map["sources"] = sorted(sources, key=lambda item: str(item["evidence_id"]))

    result = publish_preparation(release_map, tmp_path.resolve() / "typed-pass")

    assert result["certificate_state_counts"]["PASS"] == 2  # explicit V3 plus V6
    assert result["global_status"] is None


def test_production_finite_radius_cannot_pass_without_pure_gauge_detector_test(
    tmp_path: Path,
) -> None:
    domain = _domain("V4", "finite_radius_tidal_detector")
    report = _typed_report(
        schema=PRODUCTION_FINITE_RADIUS_RESULT_SCHEMA,
        result_id="forged_detector_response",
        role="PRIMARY_SCIENCE",
        independence="SAME_IMPLEMENTATION",
        gate="V4",
        observable="finite_radius_tidal_detector",
        domain=domain,
        state="PASS",
        implementation_hash="a" * 64,
        observer_test="PARTIAL",
    )
    root, digest = _frozen_json_root(tmp_path, "forged-v4", "report.json", report)
    release_map = _base_map()
    certificate = _certificate(release_map, "V4", "finite_radius_tidal_detector")
    certificate["evidence_ids"] = ["forged_v4"]
    release_map["sources"] = [
        _source(
            "forged_v4",
            "PRODUCTION_FINITE_RADIUS_V1",
            root,
            {"report.json": digest},
        )
    ]

    with pytest.raises(Phase6PreparationError, match="pure-gauge"):
        preflight_release_map(release_map)


def test_production_native_item_fail_forces_certificate_fail(tmp_path: Path) -> None:
    domain = _domain("V4", "finite_radius_tidal_detector")
    report = _typed_report(
        schema=PRODUCTION_FINITE_RADIUS_RESULT_SCHEMA,
        result_id="failed_production_campaign",
        role="PRIMARY_SCIENCE",
        independence="SAME_IMPLEMENTATION",
        gate="V4",
        observable="finite_radius_tidal_detector",
        domain=domain,
        state="PARTIAL",
        implementation_hash="a" * 64,
        observer_test="PARTIAL",
    )
    report["item_results"][0]["state"] = "FAIL"
    report["state"] = "FAIL"
    root, digest = _frozen_json_root(
        tmp_path, "failed-production", "report.json", report
    )
    release_map = _base_map()
    certificate = _certificate(release_map, "V4", "finite_radius_tidal_detector")
    certificate["evidence_ids"] = ["failed_production"]
    release_map["sources"] = [
        _source(
            "failed_production",
            "PRODUCTION_FINITE_RADIUS_V1",
            root,
            {"report.json": digest},
        )
    ]

    result = preflight_release_map(release_map)

    assert (
        result["certificate_states"]["cert_v4_finite_radius_tidal_detector"] == "FAIL"
    )
    assert result["evidence_state_counts"]["FAIL"] == 1


def test_stage_a_six_native_failures_force_fail_despite_top_level_yellow() -> None:
    modes = [
        {
            "mode": {"mode_id": f"mode_{index}"},
            "status": (
                "STABLE_SELECTED_ANCHOR_INCOMPLETE_LADDERS"
                if index < 2
                else "FAIL_CLOSED_NUMERICAL_INSTABILITY"
            ),
        }
        for index in range(8)
    ]

    state, counts, item_ids = preparation._stage_a_terminal_projection(modes)

    assert state == "FAIL"
    assert counts == {"NOT_ASSESSED": 0, "PARTIAL": 2, "PASS": 0, "FAIL": 6}
    assert len(item_ids) == 8


def test_stage_a_global_status_caveat_is_exactly_domain_qualified() -> None:
    assert preparation._stage_a_release_limitations(
        ["no V1/full-domain/project/global GREEN claim"]
    ) == ("selected-anchor evidence does not establish V1 full-domain acceptance",)


def test_stage_a_unrecognized_global_status_caveat_fails_closed() -> None:
    with pytest.raises(
        Phase6PreparationError,
        match="release-forbidden global-status wording",
    ):
        preparation._stage_a_release_limitations(
            ["this project-wide PASS claim was not an approved native rewrite"]
        )


def test_stage_a_adapter_uses_exact_eight_anchor_domain(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import schwgw.validation.phase6_mpmath_radial as native_stage_a

    modes = [
        {
            "mode": {"mode_id": f"mode_{index}"},
            "status": (
                "STABLE_SELECTED_ANCHOR_INCOMPLETE_LADDERS"
                if index < 2
                else "FAIL_CLOSED_NUMERICAL_INSTABILITY"
            ),
        }
        for index in range(8)
    ]
    evidence = {
        "schema_version": preparation.STAGE_A_EVIDENCE_SCHEMA,
        "modes": modes,
        "backend_identity": {"implementation_source_sha256": "a" * 64},
        "overall_status": "YELLOW_SELECTED_ANCHORS_ONLY",
        "limitations": ["no V1/full-domain/project/global GREEN claim"],
    }
    identity = {
        "path": "/fixture/selected_anchor_evidence.json",
        "sha256": "b" * 64,
        "size": len(canonical_json_bytes(evidence)),
        "mode": 0o444,
        "nlink": 1,
    }
    artifacts = (
        preparation.OriginArtifact(
            relative_path="selected_anchor_evidence.json",
            raw=canonical_json_bytes(evidence),
            payload=evidence,
            origin_identity=identity,
        ),
        preparation.OriginArtifact(
            relative_path="manifest.json",
            raw=b"{}",
            payload={
                "schema_version": "schwgw_phase6_mpmath_selected_anchor_manifest_v1",
                "evidence": identity,
            },
            origin_identity={**identity, "path": "/fixture/manifest.json"},
        ),
        preparation.OriginArtifact(
            relative_path="checkpoint.json",
            raw=b"{}",
            payload={
                "schema_version": "schwgw_phase6_mpmath_selected_anchor_checkpoint_v1",
                "evidence": identity,
            },
            origin_identity={**identity, "path": "/fixture/checkpoint.json"},
        ),
    )
    monkeypatch.setattr(native_stage_a, "validate_stage_a_evidence", lambda value: None)

    derived = preparation._stage_a("stage_a_fixture", artifacts)

    assert derived.expected_items == 8
    assert derived.assessed_items == 8
    assert derived.state == "FAIL"
    assert derived.native_summary["production_missing_key_count"] == 16_040
    assert derived.limitations == (
        "selected-anchor evidence does not establish V1 full-domain acceptance",
    )


def test_stage_a_domain_qualified_limitations_publish_valid_submission(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import schwgw.validation.phase6_mpmath_radial as native_stage_a

    modes = [
        {
            "mode": {"mode_id": f"mode_{index}"},
            "status": (
                "STABLE_SELECTED_ANCHOR_INCOMPLETE_LADDERS"
                if index < 2
                else "FAIL_CLOSED_NUMERICAL_INSTABILITY"
            ),
        }
        for index in range(8)
    ]
    evidence = {
        "schema_version": preparation.STAGE_A_EVIDENCE_SCHEMA,
        "modes": modes,
        "backend_identity": {"implementation_source_sha256": "a" * 64},
        "overall_status": "YELLOW_SELECTED_ANCHORS_ONLY",
        "limitations": ["no V1/full-domain/project/global GREEN claim"],
    }
    origin = tmp_path.resolve() / "stage-a-origin"
    origin.mkdir()
    evidence_path = origin / "selected_anchor_evidence.json"
    evidence_path.write_bytes(canonical_json_bytes(evidence))
    os.chmod(evidence_path, 0o444)
    evidence_info = evidence_path.lstat()
    evidence_identity = {
        "path": str(evidence_path),
        "sha256": preparation.sha256_bytes(evidence_path.read_bytes()),
        "size": evidence_info.st_size,
        "mode": 0o444,
        "nlink": 1,
    }
    linked_payloads = {
        "manifest.json": {
            "schema_version": "schwgw_phase6_mpmath_selected_anchor_manifest_v1",
            "evidence": evidence_identity,
        },
        "checkpoint.json": {
            "schema_version": "schwgw_phase6_mpmath_selected_anchor_checkpoint_v1",
            "evidence": evidence_identity,
        },
    }
    artifact_hashes = {"selected_anchor_evidence.json": evidence_identity["sha256"]}
    for filename, payload in linked_payloads.items():
        path = origin / filename
        path.write_bytes(canonical_json_bytes(payload))
        os.chmod(path, 0o444)
        artifact_hashes[filename] = preparation.sha256_bytes(path.read_bytes())
    os.chmod(origin, 0o555)

    release_map = _base_map()
    certificate = _certificate(release_map, "V1", "radial_s_matrix_flux")
    certificate["parameter_domain"] = _domain(
        "V1", "radial_s_matrix_flux", expected_items=8
    )
    certificate["evidence_ids"] = ["stage_a_fixture"]
    release_map["sources"] = [
        _source(
            "stage_a_fixture",
            "STAGE_A_MPMATH_V1",
            origin,
            artifact_hashes,
        )
    ]
    monkeypatch.setattr(native_stage_a, "validate_stage_a_evidence", lambda value: None)

    output = tmp_path.resolve() / "stage-a-preparation"
    result = publish_preparation(release_map, output)

    assert result == validate_published_preparation(output)
    assert result["certificate_state_counts"]["FAIL"] == 1
    submission = json.loads((output / "canonical_submission.json").read_text())
    stage_a_certificate = next(
        item
        for item in submission["certificates"]
        if item["certificate_id"] == "cert_v1_radial_s_matrix_flux"
    )
    assert stage_a_certificate["limitations"] == [
        "selected-anchor evidence does not establish V1 full-domain acceptance"
    ]


def test_conditioning_attempt_failure_dominates_native_partial_or_open() -> None:
    assert preparation._conditioning_status_projection("PARTIAL", "FAIL") == (
        "FAIL",
        "PRIMARY_SCIENCE",
        True,
    )
    assert preparation._conditioning_status_projection("NOT_ASSESSED", "FAIL") == (
        "FAIL",
        "FAILURE_DIAGNOSTIC",
        False,
    )
    assert preparation._conditioning_status_projection("NOT_ASSESSED", "PARTIAL") == (
        "NOT_ASSESSED",
        "BLOCKER",
        False,
    )


def test_conditioning_partition_coverage_unions_but_independent_methods_intersect() -> (
    None
):
    def derived(
        evidence_id: str, family: str, items: tuple[str, ...]
    ) -> DerivedEvidence:
        return DerivedEvidence(
            evidence_id=evidence_id,
            adapter="CONDITIONING_SHARD_V1",
            role="PRIMARY_SCIENCE",
            independence_class="SAME_IMPLEMENTATION",
            state="PARTIAL",
            blocker=None,
            science_executed=True,
            implementation_hashes=(evidence_id[0] * 64,),
            expected_items=4,
            assessed_item_ids=items,
            assessed_items=len(items),
            coverage_family=family,
            numerical_budget={},
            convention_budget={},
            native_summary={},
            native_domain=None,
            limitations=(),
            method="fixture",
        )

    first = derived("alpha", "conditioning", ("a", "b"))
    second = derived("beta", "conditioning", ("c", "d"))
    independent = derived("gamma", "independent", ("b", "c"))
    disjoint = derived("delta", "disjoint", ("x", "y"))

    assert preparation._coverage([first, second], 4) == 4
    assert preparation._coverage([first, second, independent], 4) == 2
    assert preparation._coverage([first, second, disjoint], 4) == 0

    budget_pass = replace(
        first,
        numerical_budget={
            name: {
                "state": "PASS",
                "estimate": "0.001",
                "units": "dimensionless",
                "reason": "native component pass",
            }
            for name in NUMERICAL_BUDGET_FIELDS
        },
    )
    combined = preparation._combined_budget(
        [budget_pass], fields=NUMERICAL_BUDGET_FIELDS, kind="numerical"
    )
    assert {record["state"] for record in combined.values()} == {"PARTIAL"}


def test_map_cannot_supply_state_budget_or_duplicate_source(tmp_path: Path) -> None:
    release_map = _base_map()
    forged = deepcopy(release_map)
    forged["state"] = "PASS"
    with pytest.raises(Phase6PreparationError, match="schema changed"):
        preflight_release_map(forged)

    report = _v0_report()
    root, digest = _frozen_json_root(tmp_path, "v0", "verification.json", report)
    source = _source(
        "v0_source",
        "V0_IMPLEMENTATION_VERIFICATION_V1",
        root,
        {"verification.json": digest},
    )
    source["state"] = "PASS"
    release_map["sources"] = [source]
    _certificate(release_map, "V0", "claim_provenance_cleanup")["evidence_ids"] = [
        "v0_source"
    ]
    with pytest.raises(Phase6PreparationError, match=r"source\[0\] schema"):
        preflight_release_map(release_map)


def test_mutable_modern_origin_and_hash_drift_fail_closed(tmp_path: Path) -> None:
    release_map = _base_map()
    root, digest = _frozen_json_root(
        tmp_path, "verification", "verification.json", _v0_report()
    )
    release_map["sources"] = [
        _source(
            "v0_source",
            "V0_IMPLEMENTATION_VERIFICATION_V1",
            root,
            {"verification.json": digest},
        )
    ]
    _certificate(release_map, "V0", "claim_provenance_cleanup")["evidence_ids"] = [
        "v0_source"
    ]
    os.chmod(root, 0o755)
    with pytest.raises(Phase6PreparationError, match="root must be immutable"):
        preflight_release_map(release_map)
    os.chmod(root, 0o555)
    release_map["sources"][0]["expected_artifacts"][0]["sha256"] = "0" * 64
    with pytest.raises(Phase6PreparationError, match="hash changed"):
        preflight_release_map(release_map)


def test_duplicate_native_result_bytes_are_rejected(tmp_path: Path) -> None:
    first_root, digest = _frozen_json_root(
        tmp_path, "first-v0", "verification.json", _v0_report()
    )
    second_root, second_digest = _frozen_json_root(
        tmp_path, "second-v0", "verification.json", _v0_report()
    )
    assert second_digest == digest
    release_map = _base_map()
    release_map["sources"] = [
        _source(
            "v0_duplicate_a",
            "V0_IMPLEMENTATION_VERIFICATION_V1",
            first_root,
            {"verification.json": digest},
        ),
        _source(
            "v0_duplicate_b",
            "V0_IMPLEMENTATION_VERIFICATION_V1",
            second_root,
            {"verification.json": digest},
        ),
    ]
    _certificate(release_map, "V0", "claim_provenance_cleanup")["evidence_ids"] = [
        "v0_duplicate_a",
        "v0_duplicate_b",
    ]

    with pytest.raises(Phase6PreparationError, match="duplicate native evidence"):
        preflight_release_map(release_map)


def test_v0_partial_cannot_hide_failed_machine_check(tmp_path: Path) -> None:
    report = _v0_report()
    check = report["checks"]["full_test_suite"]
    check["state"] = "PARTIAL"
    check["failed"] = 1
    report["verification_state"] = "PARTIAL"
    root, digest = _frozen_json_root(
        tmp_path, "hidden-v0-failure", "verification.json", report
    )
    release_map = _base_map()
    release_map["sources"] = [
        _source(
            "v0_hidden_failure",
            "V0_IMPLEMENTATION_VERIFICATION_V1",
            root,
            {"verification.json": digest},
        )
    ]
    _certificate(release_map, "V0", "claim_provenance_cleanup")["evidence_ids"] = [
        "v0_hidden_failure"
    ]

    with pytest.raises(Phase6PreparationError, match="hides failed"):
        preflight_release_map(release_map)


def test_legacy_mst_mutable_bytes_are_exactly_snapshotted(tmp_path: Path) -> None:
    pytest.importorskip("mpmath")
    project_root = Path(__file__).resolve().parents[2]
    native = project_root / "runs/phase5/paper_figures/bhpt_mst_benchmark_20260803_v4"
    fixture_root = tmp_path.resolve() / "legacy-mst-fixture"
    fixture_root.mkdir()
    for name, mode in (("comparison.json", 0o600), ("external_bhpt_mst.json", 0o644)):
        shutil.copyfile(native / name, fixture_root / name)
        os.chmod(fixture_root / name, mode)
    os.chmod(fixture_root, 0o755)
    release_map = _base_map()
    certificate = _certificate(release_map, "V1", "radial_s_matrix_flux")
    certificate["parameter_domain"] = _domain(
        "V1", "radial_s_matrix_flux", expected_items=84
    )
    certificate["evidence_ids"] = ["legacy_mst"]
    release_map["sources"] = [
        _source(
            "legacy_mst",
            "BHPT_MST_LEGACY_V1",
            fixture_root,
            deepcopy(preparation._LEGACY_MST_HASHES),
        )
    ]
    output = tmp_path.resolve() / "legacy-preparation"

    result = publish_preparation(release_map, output)

    assert result["certificate_state_counts"]["PARTIAL"] == 2  # V0 and MST
    for name in preparation._LEGACY_MST_HASHES:
        snapshot = output / "sources" / "legacy_mst" / name
        assert snapshot.read_bytes() == (fixture_root / name).read_bytes()
        assert stat.S_IMODE(snapshot.stat().st_mode) == 0o444
    projection = json.loads(
        (output / "normalized" / "legacy_mst" / "result.json").read_text()
    )
    assert (
        projection["native_summary"]["external_even_is_independently_solved"] is False
    )
    assert projection["release_evidence_state"] == "PARTIAL"


def test_bhpt_direct_native_pass_remains_calibration_partial(tmp_path: Path) -> None:
    from tests.unit.test_phase6_bhpt_direct import _payload  # noqa: PLC0415

    import schwgw.validation.phase6_bhpt_direct as direct  # noqa: PLC0415

    root = tmp_path.resolve() / "bhpt-direct-fixture"
    root.mkdir(mode=0o700)
    raw = _payload()
    direct.atomic_json(root / "external_bhpt_direct.json", raw)
    evidence = direct.validate_external_payload(
        raw, expected_request_sha256=str(raw["request_sha256"])
    )
    evidence.update(
        {
            "science_executed": True,
            "blocker": None,
            "request_sha256": raw["request_sha256"],
            "external_json": str(root / "external_bhpt_direct.json"),
            "external_json_sha256": direct.sha256_file(
                root / "external_bhpt_direct.json"
            ),
            "numerical_uncertainty_budget": raw["numerical_uncertainty_budget"],
            "convention_uncertainty_budget": raw["convention_uncertainty_budget"],
        }
    )
    direct.atomic_json(root / "evidence.json", evidence)
    direct._publish_manifest(root, returncode=0)
    artifacts = {
        path.name: direct.sha256_file(path) for path in root.iterdir() if path.is_file()
    }
    release_map = _base_map()
    certificate = _certificate(release_map, "V1", "radial_s_matrix_flux")
    certificate["parameter_domain"] = _domain(
        "V1", "radial_s_matrix_flux", expected_items=30
    )
    certificate["evidence_ids"] = ["bhpt_direct"]
    release_map["sources"] = [_source("bhpt_direct", "BHPT_DIRECT_V1", root, artifacts)]

    output = tmp_path.resolve() / "bhpt-direct-preparation"
    result = publish_preparation(release_map, output)

    assert result["certificate_state_counts"]["PARTIAL"] == 2  # V0 and V1
    projection = json.loads(
        (output / "normalized" / "bhpt_direct" / "result.json").read_text()
    )
    assert projection["native_summary"]["native_source_method_status"] == "PASS"
    assert (
        projection["native_summary"]["native_scientific_acceptance_status"]
        == "NOT_ASSESSED"
    )
    assert projection["release_evidence_state"] == "PARTIAL"
    assert projection["native_summary"]["even_is_independent_radial_solution"] is True


def test_check_only_cli_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    release_map_path = tmp_path.resolve() / "release-map.json"
    release_map_path.write_bytes(canonical_json_bytes(_base_map()))

    assert (
        preparation_cli.main(["--release-map", str(release_map_path), "--check-only"])
        == 0
    )

    result = json.loads(capsys.readouterr().out)
    assert result["output_written"] is False
    assert {path.name for path in tmp_path.iterdir()} == {"release-map.json"}


def test_publication_failure_seals_partial_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path.resolve() / "failed-preparation"
    original = preparation._publish_file
    calls = 0

    def fail_second(path: Path, data: bytes) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("injected preparation failure")
        original(path, data)

    monkeypatch.setattr(preparation, "_publish_file", fail_second)
    with pytest.raises(RuntimeError, match="injected"):
        publish_preparation(_base_map(), output)

    assert stat.S_IMODE(output.stat().st_mode) == 0o555
    assert all(
        stat.S_IMODE(path.stat().st_mode) == (0o555 if path.is_dir() else 0o444)
        for path in output.rglob("*")
        if not path.is_symlink()
    )
