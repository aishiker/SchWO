from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path

import pytest

import schwgw.validation.phase6_conditioning_campaign as native_conditioning
import schwgw.validation.phase6_production_finite_radius_campaign as native_production
from schwgw.validation.phase6_domain import canonical_json_bytes
from schwgw.validation.phase6_release import (
    CONVENTION_BUDGET_FIELDS,
    NUMERICAL_BUDGET_FIELDS,
    direct_file_identity,
)
from schwgw.validation.phase6_release_preparation import (
    CONDITIONING_CAMPAIGN_INDEX_SCHEMA,
    CONDITIONING_CAMPAIGN_MANIFEST_SCHEMA,
    PRODUCTION_CAMPAIGN_MANIFEST_SCHEMA,
    PRODUCTION_CAMPAIGN_RESULT_SCHEMA,
    Phase6PreparationError,
    preflight_release_map,
    prepare_release_map,
)
from tests.unit.test_phase6_release_preparation import (
    _base_map,
    _certificate,
    _domain,
    _source,
)


SENTINEL = float.fromhex("0x1.fffffffffffffp+1023")


def _digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _state_counts(
    expected: int,
    *,
    fail: int = 0,
    partial: int = 0,
    passed: int = 0,
    not_assessed: int | None = None,
) -> dict[str, int]:
    if not_assessed is None:
        not_assessed = expected - fail - partial - passed
    return {
        "NOT_ASSESSED": not_assessed,
        "PARTIAL": partial,
        "PASS": passed,
        "FAIL": fail,
    }


def _conditioning_component(
    *,
    assessed: int,
    expected: int = 17_818,
) -> dict[str, object]:
    return {
        "assessed_count": assessed,
        "maximum_assessed": "0.01" if assessed else None,
        "minimum_assessed": "0.001" if assessed else None,
        "unassessed_sentinel_count": expected - assessed,
    }


def _conditioning_payload(*, failure_count: int = 2) -> dict[str, object]:
    state = "FAIL" if failure_count else "PARTIAL"
    status = (
        "INDEX_COMPLETE_WITH_SCIENTIFIC_FAILURES"
        if failure_count
        else "INDEX_COMPLETE_WITHOUT_SCIENTIFIC_FAILURES"
    )
    numerical = {
        name: _conditioning_component(
            assessed=0 if name == "backend_difference" else 12_000
        )
        for name in NUMERICAL_BUDGET_FIELDS
    }
    convention = {
        name: _conditioning_component(assessed=12_000 if name == "phase_origin" else 0)
        for name in CONVENTION_BUDGET_FIELDS
        if name != "worldline"
    }
    aggregate_budget_counts = _state_counts(
        17_818,
        fail=failure_count,
        partial=17_818 - failure_count,
    )
    radial_counts = _state_counts(
        17_818,
        fail=failure_count,
        partial=17_818 - failure_count,
    )
    flux_counts = _state_counts(
        17_818,
        fail=failure_count,
        passed=17_818 - failure_count,
    )
    transition_failures = 1 if failure_count else 0
    return {
        "budget_summaries": {
            "convention": {
                "components": convention,
                "status_counts": aggregate_budget_counts,
            },
            "numerical": {
                "components": numerical,
                "status_counts": aggregate_budget_counts,
            },
        },
        "campaign_code_hashes": {"module": _digest("conditioning-code")},
        "campaign_source_identities": {},
        "contract_only": False,
        "coverage": {
            "D_union_exact_coverage": True,
            "D_union_key_list_sha256": (
                "a5793564dfc28e815699966208ae6605eeeedce9e3629f09512b70e08196810b"
            ),
            "extension_key_count": 1770,
            "key_count": 17_818,
            "production_key_count": 16_048,
            "shard_count": 86,
            "transition_key_count": 158,
        },
        "execution_integrity": {
            "completed_shard_count": 86,
            "execution_failure_key_count": 0,
            "execution_failure_shard_count": 0,
            "scientific_failures_are_not_execution_failures": True,
            "status": "PASS_COMPLETE_IMMUTABLE_CAMPAIGN",
        },
        "failure_summary": {
            "exact_reason_counts": (
                {"fixture fail-closed numerical instability": failure_count}
                if failure_count
                else {}
            ),
            "scientific_failure_key_count": failure_count,
        },
        "frozen_inputs": {},
        "generic_conditioning_source_hashes": {},
        "global_green_permitted": False,
        "implementation_source_sha_hashes": {
            "backend": _digest("conditioning-backend"),
            "campaign": _digest("conditioning-campaign"),
        },
        "kernel_unit_test_only": False,
        "li_figure_agreement_primary_gate": False,
        "observable_status_counts": {
            "conditioning_transition_calibration": _state_counts(
                17_818,
                fail=transition_failures,
                partial=158 - transition_failures,
                not_assessed=17_660,
            ),
            "flux_conservation": flux_counts,
            "production_finite_radius_states": _state_counts(
                17_818, not_assessed=17_818
            ),
            "radial_s_matrix": radial_counts,
            "required_radius_radial_state": radial_counts,
        },
        "overall_state": state,
        "paper_agreement_gate": False,
        "production_finite_radius_states": "NOT_ASSESSED",
        "runtime_identity_groups": {},
        "schema": CONDITIONING_CAMPAIGN_INDEX_SCHEMA,
        "science_executed": True,
        "scientific_evidence": True,
        "scope_qualification": {
            "observer_response_claim": False,
            "radial_s_matrix_only": True,
            "required_radius_M": 40.0,
        },
        "selection_summary": {
            "selected_r_out_counts": {"300": 17_818},
            "supported_key_count": 17_818,
            "unsupported_key_count": 0,
        },
        "shards": [{"fixture_shard": index} for index in range(86)],
        "solver_call_count": 17_818,
        "status": status,
        "terminal_completion_counts": {
            "COMPLETED": 17_818 - failure_count,
            "COMPLETED_FAIL_CLOSED": failure_count,
        },
        "transition_summary": {
            "key_count": 158,
            "key_status_counts": _state_counts(
                158,
                fail=transition_failures,
                partial=158 - transition_failures,
            ),
            "node_status_counts": _state_counts(
                1580,
                fail=10 * transition_failures,
                passed=1580 - 10 * transition_failures,
            ),
            "solver_call_count": 1580,
        },
    }


def _frozen_two_file_root(
    tmp_path: Path,
    *,
    result_name: str,
    result: dict[str, object],
    manifest_builder,
) -> tuple[Path, dict[str, str]]:
    root = tmp_path.resolve()
    root.mkdir(parents=True)
    result_path = root / result_name
    result_path.write_bytes(canonical_json_bytes(result))
    os.chmod(result_path, 0o444)
    os.chmod(root, 0o555)
    result_identity = direct_file_identity(result_path)
    os.chmod(root, 0o755)
    manifest = manifest_builder(result_identity)
    manifest_path = root / "manifest.json"
    manifest_path.write_bytes(canonical_json_bytes(manifest))
    os.chmod(manifest_path, 0o444)
    os.chmod(root, 0o555)
    return root, {
        result_name: direct_file_identity(result_path)["sha256"],
        "manifest.json": direct_file_identity(manifest_path)["sha256"],
    }


def _conditioning_root(
    tmp_path: Path, *, failure_count: int = 2
) -> tuple[Path, dict[str, str]]:
    payload = _conditioning_payload(failure_count=failure_count)
    return _frozen_two_file_root(
        tmp_path,
        result_name="conditioning_campaign_index.json",
        result=payload,
        manifest_builder=lambda identity: {
            "campaign_index_identity": identity,
            "created_at_utc": "2026-08-08T00:00:00+00:00",
            "global_green_permitted": False,
            "key_count": 17_818,
            "li_figure_agreement_primary_gate": False,
            "schema": CONDITIONING_CAMPAIGN_MANIFEST_SCHEMA,
            "shard_count": 86,
            "status": payload["status"],
        },
    )


def _production_payload(*, failure_count: int = 1) -> dict[str, object]:
    state = "FAIL" if failure_count else "PARTIAL"
    numerical = {
        name: (2.220446049250313e-16 if name == "arithmetic_precision" else SENTINEL)
        for name in NUMERICAL_BUDGET_FIELDS
    }
    convention = {
        name: SENTINEL for name in CONVENTION_BUDGET_FIELDS if name != "worldline"
    }
    return {
        "acceptance": state,
        "all_raw_terminal_identities": [{} for _ in range(16_048)],
        "campaign_implementation_source_identities": {},
        "campaign_implementation_source_sha256s": {
            "campaign": _digest("production-campaign")
        },
        "contract_only": False,
        "convention_budget": {"components": convention, "status": state},
        "coverage": {
            "D_prod_key_count": 16_048,
            "D_prod_key_list_sha256": (
                "54f13ea2473fb0a04ca5e16277edae31335c03b11753973d83a934cce2f0872b"
            ),
            "exact_eight_state_mode_count": 16_048,
            "frequency_count": 40,
            "missing_eight_state_mode_count": 0,
            "missing_eight_state_modes": [],
            "radial_state_record_count": 128_384,
            "shard_count": 80,
            "terminal_count": 16_048,
        },
        "failures": [
            {"fixture": index, "reason": "fail-closed mode"}
            for index in range(failure_count)
        ],
        "global_green_permitted": False,
        "implementation_source_identities": {},
        "implementation_source_sha256s": {"backend": _digest("production-backend")},
        "kernel_unit_test_only": False,
        "mode_state_counts": {
            "PARTIAL": 16_048 - failure_count,
            "FAIL": failure_count,
        },
        "numerical_budget": {"components": numerical, "status": state},
        "observable_statuses": {
            "convention_closure": "NOT_ASSESSED",
            "detector_response": "NOT_ASSESSED",
            "flux_conservation": "PARTIAL" if not failure_count else "NOT_ASSESSED",
            "infinity_waveform": "NOT_ASSESSED",
            "observer_qualified_tidal_response": "NOT_ASSESSED",
            "production_eight_radius_radial_states": state,
            "radial_s_matrix": state,
        },
        "overall_state": state,
        "release_qualification": {
            "finite_radius_outputs_are_observer_qualified": False,
            "full_paper_figure_rerun": False,
            "global_green_permitted": False,
            "independent_backend_difference_closed": False,
            "radial_state_evidence_only": True,
        },
        "schema": PRODUCTION_CAMPAIGN_RESULT_SCHEMA,
        "science_executed": True,
        "scientific_evidence": True,
        "shard_result_identities": [{} for _ in range(80)],
    }


def _production_root(
    tmp_path: Path, *, failure_count: int = 1
) -> tuple[Path, dict[str, str]]:
    payload = _production_payload(failure_count=failure_count)
    return _frozen_two_file_root(
        tmp_path,
        result_name="campaign_result.json",
        result=payload,
        manifest_builder=lambda identity: {
            "campaign_result_identity": identity,
            "global_green_permitted": False,
            "schema": PRODUCTION_CAMPAIGN_MANIFEST_SCHEMA,
            "status": "COMPLETE",
        },
    )


def _campaign_map(
    *,
    root: Path,
    artifacts: dict[str, str],
    adapter: str,
    gate: str,
    observable: str,
    expected_items: int,
) -> dict[str, object]:
    release_map = _base_map()
    certificate = _certificate(release_map, gate, observable)
    certificate["parameter_domain"] = _domain(
        gate,
        observable,
        expected_items=expected_items,
    )
    certificate["evidence_ids"] = ["campaign"]
    release_map["sources"] = [
        _source(
            "campaign",
            adapter,
            root,
            artifacts,
            selector={"projection": observable},
        )
    ]
    return release_map


def test_conditioning_campaign_projects_native_fail_and_component_budgets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, artifacts = _conditioning_root(tmp_path / "conditioning")
    validated: list[Path] = []
    monkeypatch.setattr(
        native_conditioning,
        "validate_published_conditioning_campaign",
        lambda path: validated.append(Path(path)),
    )
    release_map = _campaign_map(
        root=root,
        artifacts=artifacts,
        adapter="CONDITIONING_CAMPAIGN_V1",
        gate="V1Q",
        observable="generic_conditioning_backend",
        expected_items=158,
    )

    plan = prepare_release_map(release_map)
    derived = plan.sources["campaign"][0]
    preflight = preflight_release_map(release_map)

    assert validated == [root, root]
    assert derived.state == "FAIL"
    assert derived.expected_items == 158
    assert len(derived.assessed_item_ids) == 158
    assert derived.native_summary["scientific_failure_key_count"] == 2
    assert derived.numerical_budget["backend_difference"]["state"] == "NOT_ASSESSED"
    assert derived.numerical_budget["arithmetic_precision"]["state"] == "PARTIAL"
    assert "within 158 keys" in derived.numerical_budget["r_in"]["reason"]
    assert "17750" not in derived.numerical_budget["r_in"]["reason"]
    assert derived.convention_budget["observer"]["state"] == "NOT_ASSESSED"
    assert derived.convention_budget["tetrad"]["state"] == "NOT_ASSESSED"
    assert derived.convention_budget["worldline"]["state"] == "NOT_ASSESSED"
    assert (
        preflight["certificate_states"]["cert_v1q_generic_conditioning_backend"]
        == "FAIL"
    )


def test_production_campaign_projects_radial_only_and_never_v4(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, artifacts = _production_root(tmp_path / "production")
    monkeypatch.setattr(
        native_production, "validate_campaign_result", lambda value: None
    )
    release_map = _campaign_map(
        root=root,
        artifacts=artifacts,
        adapter="PRODUCTION_FINITE_RADIUS_CAMPAIGN_V1",
        gate="V1Q",
        observable="generic_conditioning_backend",
        expected_items=16_048,
    )

    plan = prepare_release_map(release_map)
    derived = plan.sources["campaign"][0]

    assert derived.state == "FAIL"
    assert derived.expected_items == 16_048
    assert (
        derived.native_summary["release_qualification"]["radial_state_evidence_only"]
        is True
    )
    assert derived.numerical_budget["arithmetic_precision"]["state"] == "PARTIAL"
    assert derived.numerical_budget["backend_difference"]["state"] == "NOT_ASSESSED"
    assert derived.convention_budget["observer"]["state"] == "NOT_ASSESSED"
    assert derived.convention_budget["worldline"]["state"] == "NOT_ASSESSED"

    wrong = _base_map()
    certificate = _certificate(wrong, "V4", "finite_radius_tidal_detector")
    certificate["parameter_domain"] = _domain(
        "V4", "finite_radius_tidal_detector", expected_items=16_048
    )
    certificate["evidence_ids"] = ["campaign"]
    wrong["sources"] = [
        _source(
            "campaign",
            "PRODUCTION_FINITE_RADIUS_CAMPAIGN_V1",
            root,
            artifacts,
            selector={"projection": "generic_conditioning_backend"},
        )
    ]
    with pytest.raises(Phase6PreparationError, match="cannot support gate V4"):
        preflight_release_map(wrong)


def test_campaign_selector_must_match_explicit_domain_certificate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, artifacts = _conditioning_root(tmp_path / "conditioning")
    monkeypatch.setattr(
        native_conditioning,
        "validate_published_conditioning_campaign",
        lambda path: None,
    )
    release_map = _campaign_map(
        root=root,
        artifacts=artifacts,
        adapter="CONDITIONING_CAMPAIGN_V1",
        gate="V1Q",
        observable="generic_conditioning_backend",
        expected_items=17_818,
    )
    release_map["sources"][0]["selector"] = {"projection": "radial_s_matrix_flux"}

    with pytest.raises(Phase6PreparationError, match="selector differs"):
        preflight_release_map(release_map)

    wrong_cardinality = _campaign_map(
        root=root,
        artifacts=artifacts,
        adapter="CONDITIONING_CAMPAIGN_V1",
        gate="V1Q",
        observable="generic_conditioning_backend",
        expected_items=17_818,
    )
    with pytest.raises(Phase6PreparationError, match="native coverage does not match"):
        preflight_release_map(wrong_cardinality)


def test_clean_production_campaign_stays_partial_not_pass(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, artifacts = _production_root(tmp_path / "production", failure_count=0)
    monkeypatch.setattr(
        native_production, "validate_campaign_result", lambda value: None
    )
    release_map = _campaign_map(
        root=root,
        artifacts=artifacts,
        adapter="PRODUCTION_FINITE_RADIUS_CAMPAIGN_V1",
        gate="V1",
        observable="radial_s_matrix_flux",
        expected_items=16_048,
    )

    result = preflight_release_map(release_map)

    assert result["evidence_state_counts"]["PARTIAL"] >= 1
    assert result["certificate_states"]["cert_v1_radial_s_matrix_flux"] == "PARTIAL"


def test_campaign_manifest_identity_and_native_validator_are_mandatory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, artifacts = _production_root(tmp_path / "production")
    monkeypatch.setattr(
        native_production, "validate_campaign_result", lambda value: None
    )
    manifest_path = root / "manifest.json"
    manifest = deepcopy(json.loads(manifest_path.read_text()))
    os.chmod(root, 0o755)
    os.chmod(manifest_path, 0o644)
    manifest["campaign_result_identity"]["sha256"] = "0" * 64
    manifest_path.write_bytes(canonical_json_bytes(manifest))
    os.chmod(manifest_path, 0o444)
    os.chmod(root, 0o555)
    artifacts["manifest.json"] = direct_file_identity(manifest_path)["sha256"]
    release_map = _campaign_map(
        root=root,
        artifacts=artifacts,
        adapter="PRODUCTION_FINITE_RADIUS_CAMPAIGN_V1",
        gate="V1Q",
        observable="generic_conditioning_backend",
        expected_items=16_048,
    )
    with pytest.raises(Phase6PreparationError, match="policy/linkage"):
        preflight_release_map(release_map)

    root, artifacts = _conditioning_root(tmp_path / "conditioning")

    def reject_native(path: Path) -> None:
        raise native_conditioning.ConditioningCampaignError("native rejection")

    monkeypatch.setattr(
        native_conditioning, "validate_published_conditioning_campaign", reject_native
    )
    release_map = _campaign_map(
        root=root,
        artifacts=artifacts,
        adapter="CONDITIONING_CAMPAIGN_V1",
        gate="V1Q",
        observable="generic_conditioning_backend",
        expected_items=158,
    )
    with pytest.raises(Phase6PreparationError, match="native validation failed"):
        preflight_release_map(release_map)


@pytest.mark.full_regression
def test_real_conditioning_campaign_temp_copy_check_only(
    tmp_path: Path,
) -> None:
    """Optional 86-root reload using real bytes but a fresh temporary root."""

    if os.environ.get("SCHWGW_RUN_FULL_CAMPAIGN_RELOAD") != "1":
        pytest.skip("set SCHWGW_RUN_FULL_CAMPAIGN_RELOAD=1 for the 45s native reload")
    project = Path(__file__).resolve().parents[2]
    native_root = (
        project / "runs/phase6/radial_validation/"
        "v1_conditioning_campaign_v1_20260808_py314"
    )
    if not native_root.is_dir():
        pytest.skip("formal conditioning campaign root is not present")
    root = tmp_path.resolve() / "conditioning-campaign-copy"
    root.mkdir()
    index_path = root / "conditioning_campaign_index.json"
    index_path.write_bytes((native_root / index_path.name).read_bytes())
    os.chmod(index_path, 0o444)
    os.chmod(root, 0o555)
    index_identity = direct_file_identity(index_path)
    os.chmod(root, 0o755)
    manifest = json.loads((native_root / "manifest.json").read_text())
    manifest["campaign_index_identity"] = index_identity
    manifest_path = root / "manifest.json"
    manifest_path.write_bytes(canonical_json_bytes(manifest))
    os.chmod(manifest_path, 0o444)
    os.chmod(root, 0o555)
    artifacts = {
        index_path.name: direct_file_identity(index_path)["sha256"],
        manifest_path.name: direct_file_identity(manifest_path)["sha256"],
    }
    release_map = _campaign_map(
        root=root,
        artifacts=artifacts,
        adapter="CONDITIONING_CAMPAIGN_V1",
        gate="V1Q",
        observable="generic_conditioning_backend",
        expected_items=158,
    )

    result = preflight_release_map(release_map)

    assert result["output_written"] is False
    assert (
        result["certificate_states"]["cert_v1q_generic_conditioning_backend"] == "FAIL"
    )


@pytest.mark.full_regression
def test_real_production_campaign_check_only() -> None:
    """Optional strict reload of the formal D_prod=16,048 radial-only campaign."""

    if os.environ.get("SCHWGW_RUN_FULL_CAMPAIGN_RELOAD") != "1":
        pytest.skip("set SCHWGW_RUN_FULL_CAMPAIGN_RELOAD=1 for native reload")
    project = Path(__file__).resolve().parents[2]
    root = (
        project / "runs/phase6/radial_validation/"
        "v1_production_finite_radius_campaign_v1_20260808_py314"
    )
    if not root.is_dir():
        pytest.skip("formal production campaign root is not present")
    artifacts = {
        name: str(direct_file_identity(root / name)["sha256"])
        for name in ("campaign_result.json", "manifest.json")
    }
    for gate, observable in (
        ("V1", "radial_s_matrix_flux"),
        ("V1Q", "generic_conditioning_backend"),
    ):
        release_map = _campaign_map(
            root=root,
            artifacts=artifacts,
            adapter="PRODUCTION_FINITE_RADIUS_CAMPAIGN_V1",
            gate=gate,
            observable=observable,
            expected_items=16_048,
        )

        result = preflight_release_map(release_map)

        certificate_id = f"cert_{gate.lower()}_{observable}"
        assert result["certificate_states"][certificate_id] == "FAIL"
        assert result["output_written"] is False
