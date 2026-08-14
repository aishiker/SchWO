from __future__ import annotations

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
from schwgw.validation.phase6_conditioning_scan import (
    EXPECTED_DOMAIN_IDENTITIES,
    EXPECTED_EXECUTION_IDENTITIES,
    ConditioningPolicy,
    OuterCandidateDiagnostic,
    OuterSelection,
    calibration_solve_nodes,
    execute_key_scan,
    load_frozen_scan_contract,
    scan_context_hash,
    select_outer_boundary,
)
from schwgw.validation.phase6_domain import RadialKey


ROOT = Path(__file__).resolve().parents[2]
DOMAIN_ROOT = ROOT / "runs/phase6/v1_domain_freeze_v3_20260806"
EXECUTION_ROOT = ROOT / "runs/phase6/v1_execution_contract_v4_20260806"
RUNNER_PATH = ROOT / "scripts/phase6_run_conditioning_scan_shard.py"
SMALL_SHARD_ID = "kM=0.01;sector=odd"


@pytest.fixture(scope="module")
def runner() -> dict[str, Any]:
    return runpy.run_path(str(RUNNER_PATH))


def _supported_selection(
    key: RadialKey,
    *,
    r_out_M: float = 300.0,
) -> OuterSelection:
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
                estimated_outer_segments=52,
                scaled_jost_condition=2.0,
                relative_jost_determinant=0.5,
                status="PASS",
                blockers=(),
            ),
        ),
        blocker=None,
    )


def _fake_result(request: Any) -> ConditionedRadialResult:
    perturbation = (
        1.0e-8 * request.r_in_eps
        + 1.0e-13 * request.r_out
        + 1.0e-15 * request.outer_series_order
        + 1.0e-3 * request.rtol
    )
    psi = 0.3 + perturbation + 0.2j
    derivative = -0.1 + 0.4j
    outgoing = 0.2 + perturbation + 0.1j
    transmission = math.sqrt(1.0 - abs(outgoing) ** 2) + 0.0j
    flux_residual = abs(abs(outgoing) ** 2 + abs(transmission) ** 2 - 1.0)
    primary_state = ConditionedFiniteRadiusState(
        radius=request.required_radius,
        psi=psi,
        dpsi_dr=derivative,
        log_abs_psi=math.log(abs(psi)),
        phase_psi=float(math.atan2(psi.imag, psi.real)),
        log_abs_dpsi_dr=math.log(abs(derivative)),
        phase_dpsi_dr=float(math.atan2(derivative.imag, derivative.real)),
        complex_state_status="FINITE_COMPLEX",
        complex_derivative_status="FINITE_COMPLEX",
    )
    return ConditionedRadialResult(
        psi=psi,
        dpsi_dr=derivative,
        A_in=1.0 + 0.0j,
        A_out=outgoing,
        T_horizon=transmission,
        log_abs_T_horizon=math.log(abs(transmission)),
        phase_T_horizon=0.0,
        log_abs_psi=math.log(abs(psi)),
        phase_psi=float(math.atan2(psi.imag, psi.real)),
        log_abs_dpsi_dr=math.log(abs(derivative)),
        phase_dpsi_dr=float(math.atan2(derivative.imag, derivative.real)),
        finite_radius_states=(primary_state,),
        diagnostics={
            "actual_decimal_digits": 15.95,
            "actual_precision_bits": 53,
            "atol": request.atol,
            "backend": "scipy_float64_conditioned_radial_v1",
            "complex_derivative_status": "FINITE_COMPLEX",
            "complex_state_status": "FINITE_COMPLEX",
            "ell": request.ell,
            "finite_radius_checkpoint_count": 1,
            "finite_radius_checkpoint_radii": format(request.required_radius, ".17g"),
            "flux_residual": flux_residual,
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


def test_frozen_scan_contract_binds_exact_domain_execution_and_shards() -> None:
    frozen = load_frozen_scan_contract(DOMAIN_ROOT, EXECUTION_ROOT)

    assert len(frozen.union_keys) == 17_818
    assert len(frozen.transition_keys) == 158
    assert len(frozen.shard_records) == 86
    assert {
        name: value["sha256"] for name, value in frozen.domain_identities.items()
    } == EXPECTED_DOMAIN_IDENTITIES
    assert {
        name: value["sha256"] for name, value in frozen.execution_identities.items()
    } == EXPECTED_EXECUTION_IDENTITIES
    assert len(frozen.shard_keys(SMALL_SHARD_ID)) == 83


def test_outer_selector_uses_frozen_candidates_and_fails_closed() -> None:
    key = RadialKey("0.1", "odd", 20)
    policy = ConditioningPolicy(
        r_out_candidates_M=(300.0, 600.0, 1200.0),
        maximum_estimated_outer_segments=4096,
    )
    basis_calls: list[float] = []

    def basis_probe(
        probe_key: RadialKey,
        radius: float,
        order: int,
    ) -> dict[str, float]:
        assert probe_key == key
        assert order == policy.baseline_jost_order
        basis_calls.append(radius)
        return {
            "condition": 1.0e9 if radius == 300.0 else 2.0,
            "relative_determinant": 0.5,
        }

    selected = select_outer_boundary(
        key,
        policy=policy,
        potential_probe=lambda *_: 1.0e-3,
        basis_probe=basis_probe,
    )
    assert selected.supported is True
    assert selected.selected_r_out_M == 600.0
    assert basis_calls == [300.0, 600.0]
    assert [item.status for item in selected.candidates] == ["FAIL_CLOSED", "PASS"]

    unsupported = select_outer_boundary(
        key,
        policy=policy,
        potential_probe=lambda *_: 1.0,
        basis_probe=lambda *_: pytest.fail("analytic failure must skip Jost probe"),
    )
    assert unsupported.supported is False
    assert unsupported.selected_r_out_M is None
    assert unsupported.blocker == "NO_FROZEN_R_OUT_NODE_PASSES_ALL_RAW_GATES"


def test_calibration_plan_has_one_baseline_and_exact_axis_ladders() -> None:
    selection = _supported_selection(RadialKey("1", "even", 40), r_out_M=600.0)

    baseline_only = calibration_solve_nodes(selection, transition_key=False)
    transition = calibration_solve_nodes(selection, transition_key=True)

    assert len(baseline_only) == 1
    assert len(transition) == 10
    assert sum(node.is_baseline for node in transition) == 1
    assert [node.axis for node in transition].count("r_in") == 2
    assert [node.axis for node in transition].count("r_out") == 2
    assert [node.axis for node in transition].count("jost_order") == 3
    assert [node.axis for node in transition].count("ode_tolerance") == 2
    configs = {
        (node.r_in_eps, node.r_out_M, node.jost_order, node.rtol, node.atol)
        for node in transition
    }
    assert len(configs) == len(transition)


def test_execute_key_scan_counts_calls_and_keeps_scope_budgets_separate() -> None:
    key = RadialKey("1", "even", 40)
    selection = _supported_selection(key, r_out_M=600.0)
    calls: list[Any] = []

    def solver(request: Any, background: Any) -> ConditionedRadialResult:
        del background
        calls.append(request)
        return _fake_result(request)

    payload = execute_key_scan(
        key,
        selection,
        transition_key=True,
        solver=solver,
    )

    assert len(calls) == 10
    assert payload["baseline_solver_call_count"] == 1
    assert payload["total_solver_call_count"] == 10
    assert payload["acceptance_state"] == "PARTIAL"
    assert payload["numerical_budget"]["status"] == "PARTIAL"
    assert payload["convention_budget"]["status"] == "PARTIAL"
    assert payload["observable_statuses"]["flux_conservation"] == "PASS"
    assert (
        payload["observable_statuses"]["production_finite_radius_states"]
        == "NOT_ASSESSED"
    )
    assert payload["scope_qualification"] == {
        "mode_level_s_matrix_only": True,
        "observer_response_claim": False,
        "production_finite_radius_states": "NOT_ASSESSED",
        "required_radius_M": 40.0,
    }
    baseline = payload["results"]["baseline"]
    assert baseline["required_radius_state"]["radius_M"] == 40.0
    assert baseline["additional_requested_finite_radius_states"] == []


def test_unsupported_and_failed_baseline_are_zero_retry_fail_closed() -> None:
    key = RadialKey("1", "odd", 40)
    unsupported = OuterSelection(
        key=key,
        status="UNSUPPORTED_FAIL_CLOSED",
        selected_r_out_M=None,
        turning_proxy_M=40.5,
        candidates=(),
        blocker="NO_FROZEN_R_OUT_NODE_PASSES_ALL_RAW_GATES",
    )
    calls = 0

    def forbidden_solver(*_: Any) -> ConditionedRadialResult:
        nonlocal calls
        calls += 1
        raise AssertionError("unsupported key reached the solver")

    blocked = execute_key_scan(
        key,
        unsupported,
        transition_key=False,
        solver=forbidden_solver,
    )
    assert calls == 0
    assert blocked["acceptance_state"] == "FAIL"
    assert blocked["baseline_solver_call_count"] == 0
    assert blocked["ladder_nodes"][0]["node_id"] == "baseline_preflight"

    def failing_solver(*_: Any) -> ConditionedRadialResult:
        nonlocal calls
        calls += 1
        raise ArithmeticError("deliberate no-science failure")

    failed = execute_key_scan(
        key,
        _supported_selection(key),
        transition_key=False,
        solver=failing_solver,
    )
    assert calls == 1
    assert failed["total_solver_call_count"] == 1
    assert failed["acceptance_state"] == "FAIL"
    assert list(failed["failures"]) == ["baseline"]


def test_scan_context_hash_excludes_only_publication_fields() -> None:
    record = {
        "context_sha256": "old",
        "created_at_utc": "t0",
        "output_root": "/one",
        "resume_from": None,
        "scientific": {"policy": "bound"},
    }
    first = scan_context_hash(record)
    record.update(
        {
            "context_sha256": first,
            "created_at_utc": "t1",
            "output_root": "/two",
            "resume_from": "/predecessor",
        }
    )
    assert scan_context_hash(record) == first
    record["scientific"] = {"policy": "changed"}
    assert scan_context_hash(record) != first


def test_shard_runner_publishes_immutable_partial_and_blocks_nonpass_resume(
    runner: dict[str, Any],
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    resumed = tmp_path / "resumed"
    calls = 0

    def selector(key: RadialKey) -> OuterSelection:
        return _supported_selection(key)

    def solver(request: Any, background: Any) -> ConditionedRadialResult:
        nonlocal calls
        del background
        calls += 1
        return _fake_result(request)

    try:
        result = runner["run_shard"](
            first,
            shard_id=SMALL_SHARD_ID,
            selector=selector,
            solver=solver,
            test_mode=True,
        )
        assert result["status"] == "PARTIAL"
        assert calls == 83
        assert stat.S_IMODE(first.stat().st_mode) == 0o555
        assert all(
            stat.S_IMODE(path.stat().st_mode) == 0o444 for path in first.iterdir()
        )
        contract = json.loads((first / "run_contract.json").read_text())
        assert contract["execution_mode"] == {
            "scientific_use_permitted": False,
            "selector_injected": True,
            "solver_injected": True,
            "status": "TEST_ONLY_FAKE_INJECTION_NO_SCIENTIFIC_USE",
        }
        calls = 0
        resumed_result = runner["run_shard"](
            resumed,
            shard_id=SMALL_SHARD_ID,
            resume_from=first,
            selector=selector,
            solver=solver,
            test_mode=True,
        )
        assert resumed_result["status"] == "FAIL"
        assert calls == 0
        shard_result = json.loads((resumed / "shard_result.json").read_text())
        assert shard_result["summary"] == {
            "blocked_nonreusable_predecessor_count": 83,
            "key_count": 83,
            "reused_strict_pass_count": 0,
            "solver_call_count_this_run": 0,
        }
        terminal_paths = sorted(resumed.glob("*__terminal.json"))
        assert len(terminal_paths) == 83
        assert {
            json.loads(path.read_text())["execution_status"] for path in terminal_paths
        } == {"BLOCKED_NONREUSABLE_PREDECESSOR"}
    finally:
        _restore_permissions(resumed)
        _restore_permissions(first)


def test_shard_runner_fault_injection_publishes_every_terminal(
    runner: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output = tmp_path / "failed"
    calls = 0

    def solver(request: Any, background: Any) -> ConditionedRadialResult:
        nonlocal calls
        del background
        calls += 1
        return _fake_result(request)

    def fail_publication(**_: Any) -> dict[str, object]:
        raise OSError("deliberate post-solver publication failure")

    monkeypatch.setitem(
        runner["run_shard"].__globals__,
        "_publish_key_artifacts",
        fail_publication,
    )
    try:
        with pytest.raises(
            runner["ShardRunError"],
            match="conditioning shard failed closed",
        ):
            runner["run_shard"](
                output,
                shard_id=SMALL_SHARD_ID,
                selector=_supported_selection,
                solver=solver,
                test_mode=True,
            )
        assert calls == 1
        assert stat.S_IMODE(output.stat().st_mode) == 0o555
        assert (output / "failure.json").is_file()
        terminal_paths = sorted(output.glob("*__terminal.json"))
        assert len(terminal_paths) == 83
        statuses = [
            json.loads(path.read_text())["execution_status"] for path in terminal_paths
        ]
        assert statuses.count("EXECUTION_FAILED_AFTER_SOLVER_CALL") == 1
        assert statuses.count("NOT_STARTED_DUE_TO_SHARD_FAILURE") == 82
        assert not list(output.glob(".*o_excl_staging*"))
    finally:
        _restore_permissions(output)
