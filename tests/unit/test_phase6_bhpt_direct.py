from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import stat

import pytest

import schwgw.validation.phase6_bhpt_direct as direct
from schwgw.validation.phase6_bhpt_direct import (
    BHPTDirectContractError,
    CALIBRATION_PURPOSE,
    EVIDENCE_SCHEMA,
    EXPECTED_KEY_LIST_SHA256,
    EXPECTED_SOURCE_SHA256,
    EXPECTED_UPSTREAM_COMMIT,
    MATCH_FRACTIONS,
    RAW_SCHEMA,
    SELECTED_MATCH_INDEX,
    validate_execution_contract,
    validate_external_payload,
    validate_source_snapshot,
)
from schwgw.validation.phase6_execution_contract import (
    EXTERNAL_DIRECT_CALIBRATION_SCHEMA,
    external_direct_calibration_keys,
)


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if text in {"", "-0"} else text


def _complex(
    real: Decimal | int | str, imag: Decimal | int | str = 0
) -> dict[str, str]:
    return {
        "real": _decimal_text(Decimal(real)),
        "imag": _decimal_text(Decimal(imag)),
    }


def _record(key: dict[str, object]) -> dict[str, object]:
    ell = int(key["ell"])
    km = Decimal(str(key["kM"]))
    incidence = _complex(2)
    reflection = _complex(1)
    transmission = _complex("0.5")
    ratio = _complex("0.5")
    phase = _complex(Decimal("-0.5") / Decimal((-1) ** ell))
    matches = []
    for fraction in MATCH_FRACTIONS:
        radius = Decimal(100) * Decimal(fraction) / km
        matches.append(
            {
                "match_fraction_of_upstream_outer_boundary": fraction,
                "match_radius_M": _decimal_text(radius),
                "basis_wronskian_abs": "2",
                "incidence": deepcopy(incidence),
                "reflection": deepcopy(reflection),
                "transmission": deepcopy(transmission),
                "reflection_ratio": deepcopy(ratio),
                "phase_factor": deepcopy(phase),
                "flux_unitarity_residual_abs": "0.5",
            }
        )
    convention = {
        "status": "FROZEN_FOR_EXTERNAL_CALIBRATION_NOT_GLOBAL",
        "Fourier_convention": "exp(-i*k*t)",
        "tortoise_definition": "r_star=r+2*log(r/2-1), M=1",
        "phase_factor_definition": "-Reflection/((-1)^ell*Incidence)",
        "absolute_phase_origin": "BHPT tortoise coordinate with no additive constant",
        "phase_or_normalization_fit": False,
        "remaining_convention_uncertainty": (
            "comparison consumers must prove the same master-function and phase convention"
        ),
    }
    return {
        **key,
        "potential": "ReggeWheeler" if key["sector"] == "odd" else "Zerilli",
        "method": "NumericalIntegration",
        "boundary_conditions_solved": ["In", "Up"],
        "external_api_call_count": 1,
        "external_boundary_solution_count": 2,
        "sector_is_independent_external_radial_solution": True,
        "parity_derived_even_used": False,
        "derived_from_sector": None,
        "match_records": matches,
        "selected_match_index": SELECTED_MATCH_INDEX,
        "incidence": deepcopy(incidence),
        "reflection": deepcopy(reflection),
        "transmission": deepcopy(transmission),
        "reflection_ratio": deepcopy(ratio),
        "phase_factor": deepcopy(phase),
        "numerical_uncertainty_budget": {
            "status": "PARTIAL_MEASURED_NOT_ACCEPTANCE",
            "matching_radius_phase_spread_abs": "0",
            "selected_flux_unitarity_residual_abs": "0.5",
            "working_precision_decimal_digits": 800,
            "precision_goal_decimal_digits": 200,
            "accuracy_goal_decimal_digits": 200,
            "unquantified_sources": ["fixture upstream-boundary error"],
        },
        "convention_uncertainty_budget": convention,
    }


def _payload() -> dict[str, object]:
    keys = [key.to_record() for key in external_direct_calibration_keys()]
    return {
        "schema_version": RAW_SCHEMA,
        "acceptance_scope": CALIBRATION_PURPOSE,
        "global_green_permitted": False,
        "scientific_acceptance_status": "NOT_ASSESSED",
        "paper_figure_agreement_used": False,
        "request_sha256": "a" * 64,
        "external_direct_domain": {
            "schema": EXTERNAL_DIRECT_CALIBRATION_SCHEMA,
            "purpose": CALIBRATION_PURPOSE,
            "count": 30,
            "key_list_sha256": EXPECTED_KEY_LIST_SHA256,
        },
        "toolkit": {
            "name": "BlackHolePerturbationToolkit/ReggeWheeler",
            "repository": (
                "https://github.com/BlackHolePerturbationToolkit/ReggeWheeler"
            ),
            "license": "MIT",
            "source_commit": EXPECTED_UPSTREAM_COMMIT,
            "source_hashes": deepcopy(EXPECTED_SOURCE_SHA256),
        },
        "runtime": {"wolfram_version": "fixture", "system_id": "fixture"},
        "backend_contract": {
            "method": "NumericalIntegration",
            "spin_weight_argument": 2,
            "potential_by_sector": {"odd": "ReggeWheeler", "even": "Zerilli"},
            "boundary_conditions_solved": ["In", "Up"],
            "external_api_calls_per_key": 1,
            "external_api_call_count": 30,
            "external_boundary_solutions_per_key": 2,
            "external_boundary_solution_count": 60,
            "even_is_independent_radial_solution": True,
            "parity_derived_even_used": False,
            "internal_solver_fallback_used": False,
            "project_solver_components_used": [],
        },
        "precision": {
            "working_precision_decimal_digits": 800,
            "precision_goal_decimal_digits": 200,
            "accuracy_goal_decimal_digits": 200,
            "serialized_output_digits": 100,
        },
        "matching": {
            "method": "two-solution Wronskian decomposition",
            "upstream_outer_boundary_radius_formula_M": "100/abs(kM)",
            "match_radius_fractions_of_upstream_outer_boundary": list(MATCH_FRACTIONS),
            "selected_match_index": SELECTED_MATCH_INDEX,
            "phase_factor_definition": "-Reflection/((-1)^ell*Incidence)",
            "transmission_definition": "1/Incidence",
            "reflection_ratio_definition": "Reflection/Incidence",
        },
        "numerical_uncertainty_budget": {
            "status": "PARTIAL_PER_RECORD_NOT_DOMAIN_ACCEPTANCE",
            "measured_terms": [
                "three-radius matching spread",
                "selected-radius flux unitarity residual",
            ],
            "acceptance_threshold_frozen": False,
        },
        "convention_uncertainty_budget": {
            "status": "FROZEN_FOR_EXTERNAL_CALIBRATION_NOT_GLOBAL",
            "Fourier_convention": "exp(-i*k*t)",
            "tortoise_definition": "r_star=r+2*log(r/2-1), M=1",
            "phase_factor_definition": "-Reflection/((-1)^ell*Incidence)",
            "absolute_phase_origin": (
                "BHPT tortoise coordinate with no additive constant"
            ),
            "phase_or_normalization_fit": False,
            "remaining_convention_uncertainty": (
                "comparison consumers must prove the same master-function "
                "and phase convention"
            ),
        },
        "record_count": 30,
        "records": [_record(key) for key in keys],
    }


def test_execution_contract_binds_exact_v4_30_key_bytes() -> None:
    result = validate_execution_contract()

    assert result["count"] == 30
    assert result["key_list_sha256"] == EXPECTED_KEY_LIST_SHA256
    assert result["purpose"] == CALIBRATION_PURPOSE
    assert len(result["records"]) == 30


def test_external_payload_accepts_only_schema_not_scientific_domain() -> None:
    result = validate_external_payload(_payload(), expected_request_sha256="a" * 64)

    assert result["schema_version"] == EVIDENCE_SCHEMA
    assert result["status"] == "PASS"
    assert result["status_scope"] == "SOURCE_METHOD_SCHEMA_AND_ALGEBRA_ONLY"
    assert result["scientific_acceptance_status"] == "NOT_ASSESSED"
    assert result["even_is_independent_radial_solution"] is True
    assert result["global_green_permitted"] is False


@pytest.mark.parametrize(
    ("mutator", "match"),
    [
        (
            lambda payload: payload["backend_contract"].__setitem__("method", "MST"),
            "direct integration",
        ),
        (
            lambda payload: payload["backend_contract"].__setitem__(
                "parity_derived_even_used", True
            ),
            "direct integration",
        ),
        (
            lambda payload: payload["records"][1].__setitem__(
                "potential", "ReggeWheeler"
            ),
            "independent radial potential",
        ),
        (
            lambda payload: payload["records"][1].__setitem__(
                "parity_derived_even_used", True
            ),
            "direct-solve provenance",
        ),
        (
            lambda payload: payload["records"][0]["phase_factor"].__setitem__(
                "imag", "0.1"
            ),
            "selected phase_factor",
        ),
        (
            lambda payload: payload["records"][0]["match_records"][0].__setitem__(
                "match_radius_M", "3"
            ),
            "matching radius",
        ),
        (
            lambda payload: payload["numerical_uncertainty_budget"].__setitem__(
                "status", "PASS"
            ),
            "top-level numerical budget",
        ),
    ],
)
def test_external_payload_rejects_method_even_and_algebra_drift(
    mutator, match: str
) -> None:
    payload = _payload()
    mutator(payload)

    with pytest.raises(BHPTDirectContractError, match=match):
        validate_external_payload(payload, expected_request_sha256="a" * 64)


def test_source_snapshot_requires_exact_commit_and_all_three_hashes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "ReggeWheeler"
    (root / "Kernel").mkdir(parents=True)
    contents = {
        "Kernel/ReggeWheelerRadial.m": b"radial fixture\n",
        "Kernel/NumericalIntegration.m": b"direct fixture\n",
        "LICENSE": b"license fixture\n",
    }
    for relative, data in contents.items():
        (root / relative).write_bytes(data)
    hashes = {
        relative: hashlib.sha256(data).hexdigest()
        for relative, data in contents.items()
    }
    monkeypatch.setattr(direct, "EXPECTED_SOURCE_SHA256", hashes)
    monkeypatch.setattr(
        direct,
        "_git_head",
        lambda path: (EXPECTED_UPSTREAM_COMMIT, path.resolve(strict=True)),
    )
    monkeypatch.setattr(direct, "_require_clean_git_worktree", lambda _: None)

    identity = validate_source_snapshot(root)
    assert identity["commit"] == EXPECTED_UPSTREAM_COMMIT
    assert identity["git_worktree_status"] == "CLEAN_TRACKED_AND_UNTRACKED"
    assert set(identity["files"]) == set(contents)

    (root / "LICENSE").write_bytes(b"modified\n")
    with pytest.raises(BHPTDirectContractError, match="source hash mismatch"):
        validate_source_snapshot(root)


def test_missing_wolfram_kernel_is_not_assessed_and_never_falls_back(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = {
        "package_root": str(tmp_path),
        "repository": "fixture",
        "commit": EXPECTED_UPSTREAM_COMMIT,
        "license": "MIT",
        "files": {},
    }
    monkeypatch.setattr(direct, "validate_source_snapshot", lambda _: source)
    monkeypatch.setattr(
        direct,
        "_runtime_probe",
        lambda requested: {
            "requested_kernel": str(requested),
            "requested_kernel_resolution": None,
            "path_WolframKernel": None,
            "common_kernel_candidates": [],
            "wolframscript_wrapper": {"resolved_executable": None},
            "runtime_acceptance_rule": "fixture requires WolframKernel",
        },
    )
    output = tmp_path / "missing_runtime_evidence"

    returncode = direct.run_selected_direct(
        output_dir=output,
        package_root=tmp_path,
        wolfram_kernel=tmp_path / "definitely_absent_WolframKernel",
    )

    evidence = json.loads((output / "evidence.json").read_text(encoding="utf-8"))
    assert returncode == 3
    assert evidence["status"] == "NOT_ASSESSED"
    assert evidence["blocker"] == "BLOCKED_BY_RUNTIME"
    assert evidence["science_executed"] is False
    assert evidence["external_record_count"] == 0
    assert evidence["internal_solver_fallback_used"] is False
    assert evidence["external_direct_domain"]["count"] == 30
    assert evidence["external_direct_domain"]["assessed_count"] == 0
    assert len(evidence["per_mode_statuses"]) == 30
    assert {item["status"] for item in evidence["per_mode_statuses"]} == {
        "NOT_ASSESSED"
    }
    assert all(
        item["numerical_uncertainty_budget"]["status"] == "NOT_ASSESSED"
        and item["convention_uncertainty_budget"]["status"]
        == "FROZEN_REQUEST_ONLY_NOT_VALIDATED"
        for item in evidence["per_mode_statuses"]
    )
    assert not (output / "external_bhpt_direct.json").exists()
    assert stat.S_IMODE(output.stat().st_mode) == 0o555
    assert all(stat.S_IMODE(path.stat().st_mode) == 0o444 for path in output.iterdir())
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["terminal_status"] == "NOT_ASSESSED"
    assert manifest["terminal_blocker"] == "BLOCKED_BY_RUNTIME"
    assert manifest["paper_figure_runs"] == 0
    direct._validate_frozen_root(output)

    with pytest.raises(BHPTDirectContractError, match="fresh and absent"):
        direct.run_selected_direct(
            output_dir=output,
            package_root=tmp_path,
            wolfram_kernel=tmp_path / "definitely_absent_WolframKernel",
        )


def test_wolfram_source_requests_direct_rw_and_independent_zerilli() -> None:
    source = direct.WLS_PATH.read_text(encoding="utf-8")

    assert 'Method -> {"NumericalIntegration", "Domain" -> domainRules}' in source
    assert '"odd", "ReggeWheeler"' in source
    assert '"even", "Zerilli"' in source
    assert '"BoundaryConditions" -> {"In", "Up"}' in source
    assert '"external_api_call_count" -> 1' in source
    assert '"external_boundary_solution_count" -> 2' in source
    assert '"parity_derived_even_used" -> False' in source
    assert "exact_chandrasekhar_starobinsky_ratio" not in source
    assert "solve_radial_mode" not in source
