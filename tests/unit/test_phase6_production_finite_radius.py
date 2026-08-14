from __future__ import annotations

import ast
from dataclasses import replace
import json
import math
import os
from pathlib import Path
import runpy
import stat
from typing import Any

import pytest

from schwgw.numerics.conditioned_radial import (
    ConditionedFiniteRadiusState,
    ConditionedRadialResult,
)
from schwgw.validation import phase6_production_finite_radius_campaign as campaign
from schwgw.validation.phase6_conditioning_scan import (
    OuterCandidateDiagnostic,
    OuterSelection,
)
from schwgw.validation.phase6_domain import (
    RadialKey,
    canonical_json_bytes,
    source_file_identity,
)
from schwgw.validation.phase6_production_finite_radius import (
    EXPECTED_COORDINATE_SOURCE_SHA256,
    EXPECTED_TABLE_I_X_M,
    MANIFEST_SCHEMA,
    ProductionFiniteRadiusError,
    execute_production_finite_radius_key,
    load_frozen_production_contract,
    scientific_context_hash,
    validate_solver_payload,
)


ROOT = Path(__file__).resolve().parents[2]
DOMAIN_ROOT = ROOT / "runs/phase6/v1_domain_freeze_v3_20260806"
EXECUTION_ROOT = ROOT / "runs/phase6/v1_execution_contract_v4_20260806"
MODULE_PATH = ROOT / "src/schwgw/validation/phase6_production_finite_radius.py"
RUNNER_PATH = ROOT / "scripts/phase6_run_production_finite_radius_shard.py"
SMALL_SHARD_ID = "kM=0.1;sector=odd"


@pytest.fixture(scope="module")
def frozen():
    return load_frozen_production_contract(DOMAIN_ROOT, EXECUTION_ROOT)


@pytest.fixture(scope="module")
def runner() -> dict[str, Any]:
    return runpy.run_path(str(RUNNER_PATH))


def _supported_selection(key: RadialKey, r_out_M: float = 300.0) -> OuterSelection:
    return OuterSelection(
        key=key,
        status="SUPPORTED",
        selected_r_out_M=r_out_M,
        turning_proxy_M=1.0,
        candidates=(
            OuterCandidateDiagnostic(
                r_out_M=r_out_M,
                turning_proxy_margin=r_out_M,
                potential_to_k2=0.01,
                k_r_out=float(key.kM) * r_out_M,
                estimated_outer_segments=54,
                scaled_jost_condition=2.0,
                relative_jost_determinant=0.5,
                status="PASS",
                blockers=(),
            ),
        ),
        blocker=None,
    )


def _fake_result(request: Any) -> ConditionedRadialResult:
    radii = (request.required_radius, *request.evaluation_radii)
    states = tuple(
        ConditionedFiniteRadiusState(
            radius=radius,
            psi=complex(0.25 + 1.0e-4 * index, 0.1),
            dpsi_dr=complex(-0.08, 0.2 + 1.0e-4 * index),
            log_abs_psi=math.log(abs(complex(0.25 + 1.0e-4 * index, 0.1))),
            phase_psi=math.atan2(0.1, 0.25 + 1.0e-4 * index),
            log_abs_dpsi_dr=math.log(abs(complex(-0.08, 0.2 + 1.0e-4 * index))),
            phase_dpsi_dr=math.atan2(0.2 + 1.0e-4 * index, -0.08),
            complex_state_status="FINITE_COMPLEX",
            complex_derivative_status="FINITE_COMPLEX",
        )
        for index, radius in enumerate(radii)
    )
    outgoing = 0.2 + 0.1j
    transmission = math.sqrt(1.0 - abs(outgoing) ** 2) + 0.0j
    flux_balance = abs(outgoing) ** 2 + abs(transmission) ** 2
    primary = states[0]
    return ConditionedRadialResult(
        psi=primary.psi,
        dpsi_dr=primary.dpsi_dr,
        A_in=1.0 + 0.0j,
        A_out=outgoing,
        T_horizon=transmission,
        log_abs_T_horizon=math.log(abs(transmission)),
        phase_T_horizon=0.0,
        log_abs_psi=primary.log_abs_psi,
        phase_psi=primary.phase_psi,
        log_abs_dpsi_dr=primary.log_abs_dpsi_dr,
        phase_dpsi_dr=primary.phase_dpsi_dr,
        finite_radius_states=states,
        diagnostics={
            "actual_decimal_digits": 15.95,
            "actual_precision_bits": 53,
            "atol": request.atol,
            "backend": "scipy_float64_conditioned_radial_v1",
            "ell": request.ell,
            "finite_radius_checkpoint_count": 8,
            "finite_radius_checkpoint_radii": ",".join(
                format(radius, ".17g") for radius in radii
            ),
            "flux_balance": flux_balance,
            "flux_residual": abs(flux_balance - 1.0),
            "k": request.k,
            "method": "scaled_log_riccati_jost_ratio",
            "normalization_definition": "A_in set exactly to one after Jost ratio",
            "outer_basis": request.outer_basis,
            "outer_series_order": request.outer_series_order,
            "paper_specific_envelope_used": False,
            "r_out": request.r_out,
            "required_radius": request.required_radius,
            "rtol": request.rtol,
            "scientific_acceptance": False,
            "sector": request.sector.value,
            "unit_incoming_at_infinity": True,
            "valid_at_required_radius": True,
        },
    )


def _restore_permissions(root: Path) -> None:
    if not root.exists():
        return
    for path in sorted(root.rglob("*"), reverse=True):
        if path.is_dir() and not path.is_symlink():
            os.chmod(path, 0o700)
        elif path.is_file() and not path.is_symlink():
            os.chmod(path, 0o600)
    os.chmod(root, 0o700)


def _write_canonical_json(path: Path, payload: object) -> None:
    path.write_bytes(canonical_json_bytes(payload))
    os.chmod(path, 0o444)


def _rebuild_complete_manifest(root: Path) -> None:
    manifest_path = root / "manifest.json"
    manifest_path.unlink()
    for path in root.iterdir():
        if path.is_file():
            os.chmod(path, 0o444)
    files = {
        path.name: source_file_identity(path)
        for path in sorted(root.iterdir())
        if path.is_file()
    }
    _write_canonical_json(
        manifest_path,
        {
            "file_count_excluding_manifest": len(files),
            "files": files,
            "global_green_permitted": False,
            "schema": MANIFEST_SCHEMA,
            "status": "COMPLETE",
        },
    )
    os.chmod(root, 0o555)


def _promote_test_root_to_formal_fixture(root: Path) -> None:
    """Convert injected test artifacts into a structural formal-root fixture."""

    _restore_permissions(root)
    run_contract_path = root / "run_contract.json"
    run_contract = json.loads(run_contract_path.read_text(encoding="utf-8"))
    run_contract["execution_mode"] = {
        "contract_only": False,
        "kernel_unit_test_only": False,
        "science_executed": True,
        "scientific_evidence": True,
        "selector_injected": False,
        "solver_injected": False,
        "status": "PRODUCTION_SCIENCE_EXECUTION",
    }
    run_contract["context_sha256"] = scientific_context_hash(run_contract)
    _write_canonical_json(run_contract_path, run_contract)

    shard_result_path = root / "shard_result.json"
    shard_result = json.loads(shard_result_path.read_text(encoding="utf-8"))
    shard_result.update(
        {
            "contract_only": False,
            "kernel_unit_test_only": False,
            "science_executed": True,
            "scientific_evidence": True,
        }
    )
    _write_canonical_json(shard_result_path, shard_result)
    _rebuild_complete_manifest(root)


def _rewrite_formal_fixture_with_stale_source(root: Path) -> None:
    _restore_permissions(root)
    run_contract_path = root / "run_contract.json"
    run_contract = json.loads(run_contract_path.read_text(encoding="utf-8"))
    source_name = "production_gate_module"
    run_contract["implementation_source_identities"][source_name]["sha256"] = "0" * 64
    run_contract["implementation_source_sha256s"][source_name] = "0" * 64
    run_contract["context_sha256"] = scientific_context_hash(run_contract)
    _write_canonical_json(run_contract_path, run_contract)
    _rebuild_complete_manifest(root)


def test_frozen_contract_binds_16048_keys_40_frequencies_80_shards_and_sites(
    frozen: Any,
) -> None:
    assert len(frozen.production_keys) == 16_048
    assert len({key.kM for key in frozen.production_keys}) == 40
    assert len(frozen.shard_records) == 80
    assert sum(record["key_count"] for record in frozen.shard_records) == 16_048
    assert all(record["extension_key_count"] == 0 for record in frozen.shard_records)
    assert len(frozen.sites) == 8
    assert tuple(site.x_M for site in frozen.sites) == EXPECTED_TABLE_I_X_M
    assert tuple(site.z_M for site in frozen.sites) == (30.0,) * 8
    assert frozen.sites[0].radius_M_decimal == "30.0"
    assert frozen.sites[-1].radius_M_decimal.startswith("39.05124837953327")
    assert frozen.coordinate_source_identity["sha256"] == (
        EXPECTED_COORDINATE_SOURCE_SHA256
    )


def test_gate_imports_no_legacy_paper_or_public_radial_solver_path() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }
    assert not any("legacy" in name for name in imports)
    assert not any("paper_oracles" in name for name in imports)
    assert not any(name.endswith("radial_solver") for name in imports)
    assert not any("experimental.q018" in name for name in imports)


def test_one_generic_solve_returns_exact_eight_states_and_separate_budgets(
    frozen: Any,
) -> None:
    key = RadialKey("2", "odd", 153)
    calls: list[Any] = []

    def solver(request: Any, background: Any) -> ConditionedRadialResult:
        del background
        calls.append(request)
        return _fake_result(request)

    payload = execute_production_finite_radius_key(
        key,
        _supported_selection(key, 600.0),
        frozen.sites,
        solver=solver,
    )
    assert len(calls) == 1
    request = calls[0]
    assert request.required_radius == frozen.sites[0].radius_M
    assert request.evaluation_radii == tuple(site.radius_M for site in frozen.sites[1:])
    assert request.r_out == 600.0
    assert payload["acceptance_state"] == "PARTIAL"
    assert payload["solver_call_count"] == 1
    assert len(payload["result"]["finite_radius_states"]) == 8
    assert payload["observable_statuses"]["flux_conservation"] == "PASS"
    assert (
        payload["observable_statuses"]["production_eight_radius_radial_states"]
        == "PARTIAL"
    )
    assert payload["observable_statuses"]["detector_response"] == "NOT_ASSESSED"
    assert payload["numerical_budget"]["status"] == "PARTIAL"
    assert payload["convention_budget"]["status"] == "PARTIAL"
    for name in ("observer", "tetrad", "polarization_basis"):
        assert payload["convention_budget"]["components"][name] > 0.0
        assert (
            payload["convention_budget"]["component_statuses"][name] == "NOT_ASSESSED"
        )
    validate_solver_payload(payload, key=key, sites=frozen.sites)


def test_unsupported_and_malformed_results_fail_closed_without_promotion(
    frozen: Any,
) -> None:
    key = RadialKey("4", "even", 360)
    unsupported = OuterSelection(
        key=key,
        status="UNSUPPORTED_FAIL_CLOSED",
        selected_r_out_M=None,
        turning_proxy_M=90.0,
        candidates=(),
        blocker="NO_FROZEN_R_OUT_NODE_PASSES_ALL_RAW_GATES",
    )
    calls = 0

    def forbidden_solver(*_: Any) -> ConditionedRadialResult:
        nonlocal calls
        calls += 1
        raise AssertionError("unsupported mode reached solver")

    blocked = execute_production_finite_radius_key(
        key, unsupported, frozen.sites, solver=forbidden_solver
    )
    assert calls == 0
    assert blocked["acceptance_state"] == "FAIL"
    assert blocked["solver_call_count"] == 0

    def malformed_solver(request: Any, background: Any) -> ConditionedRadialResult:
        del background
        result = _fake_result(request)
        return ConditionedRadialResult(
            **{
                **result.__dict__,
                "finite_radius_states": result.finite_radius_states[:-1],
            }
        )

    malformed = execute_production_finite_radius_key(
        key,
        _supported_selection(key),
        frozen.sites,
        solver=malformed_solver,
    )
    assert malformed["acceptance_state"] == "FAIL"
    assert malformed["solver_call_count"] == 1
    assert malformed["result"] is None
    assert "eight-state" in next(iter(malformed["failures"].values()))

    def flux_failing_solver(request: Any, background: Any) -> ConditionedRadialResult:
        del background
        result = _fake_result(request)
        diagnostics = dict(result.diagnostics)
        diagnostics.update({"flux_balance": 0.5, "flux_residual": 0.5})
        return replace(
            result,
            A_out=0.5 + 0.0j,
            T_horizon=0.5 + 0.0j,
            log_abs_T_horizon=math.log(0.5),
            diagnostics=diagnostics,
        )

    flux_failed = execute_production_finite_radius_key(
        key,
        _supported_selection(key),
        frozen.sites,
        solver=flux_failing_solver,
    )
    assert flux_failed["acceptance_state"] == "FAIL"
    assert len(flux_failed["result"]["finite_radius_states"]) == 8
    assert flux_failed["result"]["flux"]["status"] == "FAIL"
    assert flux_failed["observable_statuses"]["flux_conservation"] == "FAIL"


def test_shard_runner_is_immutable_and_nonpass_resume_is_zero_call_blocked(
    runner: dict[str, Any],
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    resumed = tmp_path / "resumed"
    calls = 0

    def solver(request: Any, background: Any) -> ConditionedRadialResult:
        nonlocal calls
        del background
        calls += 1
        return _fake_result(request)

    try:
        result = runner["run_shard"](
            first,
            shard_id=SMALL_SHARD_ID,
            selector=_supported_selection,
            solver=solver,
            test_mode=True,
        )
        assert result["overall_state"] == "PARTIAL"
        assert result["scientific_evidence"] is False
        assert result["science_executed"] is False
        assert result["kernel_unit_test_only"] is True
        assert result["contract_only"] is False
        assert calls == 83
        assert result["summary"]["terminal_count"] == 83
        assert len(result["all_terminal_identities"]) == 83
        assert stat.S_IMODE(first.stat().st_mode) == 0o555
        assert all(
            stat.S_IMODE(path.stat().st_mode) == 0o444 for path in first.iterdir()
        )
        with pytest.raises(
            campaign.ProductionCampaignError,
            match="not scientific evidence",
        ):
            campaign.validate_shard_root(
                first,
                frozen=load_frozen_production_contract(DOMAIN_ROOT, EXECUTION_ROOT),
            )
        calls = 0
        resumed_result = runner["run_shard"](
            resumed,
            shard_id=SMALL_SHARD_ID,
            resume_from=first,
            selector=_supported_selection,
            solver=solver,
            test_mode=True,
        )
        assert calls == 0
        assert resumed_result["overall_state"] == "FAIL"
        assert resumed_result["summary"]["blocked_nonreusable_predecessor_count"] == 83
        assert resumed_result["summary"]["mode_state_counts"] == {
            "PARTIAL": 0,
            "FAIL": 83,
        }
    finally:
        _restore_permissions(resumed)
        _restore_permissions(first)


def test_any_mode_failure_forces_shard_fail(
    runner: dict[str, Any],
    tmp_path: Path,
) -> None:
    output = tmp_path / "one-mode-fail"

    def solver(request: Any, background: Any) -> ConditionedRadialResult:
        del background
        if request.ell == 3:
            raise ArithmeticError("deliberate mode failure")
        return _fake_result(request)

    try:
        result = runner["run_shard"](
            output,
            shard_id=SMALL_SHARD_ID,
            selector=_supported_selection,
            solver=solver,
            test_mode=True,
        )
        assert result["overall_state"] == "FAIL"
        assert result["acceptance"] == "FAIL"
        assert result["summary"]["mode_state_counts"] == {
            "PARTIAL": 82,
            "FAIL": 1,
        }
        assert len(result["failures"]) == 1
        failed_terminal = json.loads(
            (output / "key_0001__kM_0p1__odd__ell_0003__terminal.json").read_text(
                encoding="utf-8"
            )
        )
        assert (
            result["failures"][0]["payload_identity"]
            == failed_terminal["payload_identity"]
        )
    finally:
        _restore_permissions(output)


def test_formal_fail_fixture_roundtrips_ledger_and_rejects_stale_source(
    runner: dict[str, Any],
    frozen: Any,
    tmp_path: Path,
) -> None:
    output = tmp_path / "formal-fail-fixture"

    def solver(request: Any, background: Any) -> ConditionedRadialResult:
        del background
        if request.ell == 3:
            raise ArithmeticError("deliberate formal-fixture mode failure")
        return _fake_result(request)

    try:
        runner["run_shard"](
            output,
            shard_id=SMALL_SHARD_ID,
            selector=_supported_selection,
            solver=solver,
            test_mode=True,
        )
        _promote_test_root_to_formal_fixture(output)
        validated = campaign.validate_shard_root(output, frozen=frozen)
        assert validated["shard_result"]["overall_state"] == "FAIL"
        assert len(validated["failures"]) == 1
        assert validated["failures"][0]["key"] == {
            "ell": 3,
            "kM": "0.1",
            "sector": "odd",
        }
        assert (
            validated["failures"][0]["payload_identity"]
            == (validated["payload_identities"][1])
        )

        _rewrite_formal_fixture_with_stale_source(output)
        with pytest.raises(campaign.ProductionCampaignError, match="source identity"):
            campaign.validate_shard_root(output, frozen=frozen)
    finally:
        _restore_permissions(output)


def _synthetic_shard_evidence(frozen: Any, *, fail_first: bool = False):
    source_identity = source_file_identity(MODULE_PATH)
    source_hashes = {"gate": source_identity["sha256"]}
    result: dict[str, dict[str, object]] = {}
    for shard_index, shard in enumerate(frozen.shard_records):
        keys = frozen.shard_keys(shard["shard_id"])
        modes = []
        failures = []
        for mode_index, key in enumerate(keys):
            failed = fail_first and shard_index == 0 and mode_index == 0
            terminal_identity = {
                "mode": 0o444,
                "nlink": 1,
                "path": f"/synthetic/{shard['shard_id']}/{mode_index}/terminal",
                "sha256": f"{(mode_index + shard_index) % 16:x}" * 64,
                "size": 1,
            }
            mode = {
                "acceptance_state": "FAIL" if failed else "PARTIAL",
                "has_exact_eight_radial_states": not failed,
                "key": key.to_record(),
                "observable_statuses": {
                    "flux_conservation": "FAIL" if failed else "PASS",
                    "production_eight_radius_radial_states": (
                        "FAIL" if failed else "PARTIAL"
                    ),
                },
                "payload_identity": terminal_identity,
                "terminal_identity": terminal_identity,
            }
            modes.append(mode)
            if failed:
                failures.append(
                    {
                        "failures": {"mode": "deliberate"},
                        "key": key.to_record(),
                        "payload_identity": terminal_identity,
                    }
                )
        result[shard["shard_id"]] = {
            "failures": failures,
            "implementation_source_identities": {"gate": source_identity},
            "implementation_source_sha256s": source_hashes,
            "keys": [key.to_record() for key in keys],
            "mode_records": modes,
            "payload_identities": [mode["payload_identity"] for mode in modes],
            "root": f"/synthetic/{shard['shard_id']}",
            "root_manifest_identity": source_identity,
            "shard": dict(shard),
            "shard_result": {},
            "shard_result_identity": source_identity,
            "terminal_identities": [mode["terminal_identity"] for mode in modes],
        }
    return result


def test_campaign_builder_proves_exact_80_shard_union_and_exposes_failures(
    frozen: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    roots = [tmp_path / str(index) for index in range(80)]
    for root in roots:
        root.mkdir()
    clean = _synthetic_shard_evidence(frozen)
    ordered_ids = [shard["shard_id"] for shard in frozen.shard_records]
    monkeypatch.setattr(
        campaign,
        "validate_shard_root",
        lambda root, *, frozen: clean[ordered_ids[int(Path(root).name)]],
    )
    identity = source_file_identity(MODULE_PATH)
    payload = campaign.build_campaign_result(
        roots,
        frozen=frozen,
        campaign_implementation_identities={"campaign_test_source": identity},
    )
    assert payload["overall_state"] == "PARTIAL"
    assert payload["coverage"] == {
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
    }
    assert len(payload["all_raw_terminal_identities"]) == 16_048
    assert len(payload["shard_result_identities"]) == 80
    assert payload["global_green_permitted"] is False
    assert (
        payload["release_qualification"]["finite_radius_outputs_are_observer_qualified"]
        is False
    )

    failed = _synthetic_shard_evidence(frozen, fail_first=True)
    monkeypatch.setattr(
        campaign,
        "validate_shard_root",
        lambda root, *, frozen: failed[ordered_ids[int(Path(root).name)]],
    )
    failed_payload = campaign.build_campaign_result(
        roots,
        frozen=frozen,
        campaign_implementation_identities={"campaign_test_source": identity},
    )
    assert failed_payload["overall_state"] == "FAIL"
    assert failed_payload["coverage"]["missing_eight_state_mode_count"] == 1
    assert failed_payload["mode_state_counts"] == {"PARTIAL": 16_047, "FAIL": 1}
    assert len(failed_payload["failures"]) == 1


def test_campaign_requires_exactly_80_unique_roots(
    frozen: Any,
    tmp_path: Path,
) -> None:
    identity = source_file_identity(MODULE_PATH)
    with pytest.raises(campaign.ProductionCampaignError, match="exactly 80"):
        campaign.build_campaign_result(
            [Path("/synthetic/one")],
            frozen=frozen,
            campaign_implementation_identities={"test": identity},
        )
    same = tmp_path / "same"
    same.mkdir()
    with pytest.raises(campaign.ProductionCampaignError, match="unique"):
        campaign.build_campaign_result(
            [same] * 80,
            frozen=frozen,
            campaign_implementation_identities={"test": identity},
        )


def test_validator_rejects_observer_convention_promotion(frozen: Any) -> None:
    key = RadialKey("1", "even", 40)
    payload = execute_production_finite_radius_key(
        key,
        _supported_selection(key),
        frozen.sites,
        solver=lambda request, background: _fake_result(request),
    )
    payload["observable_statuses"]["detector_response"] = "PASS"
    with pytest.raises(ProductionFiniteRadiusError, match="observer/convention"):
        validate_solver_payload(payload, key=key, sites=frozen.sites)
