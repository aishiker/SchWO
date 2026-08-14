from __future__ import annotations

from pathlib import Path
import stat

import pytest

from schwgw.numerics.conditioned_radial import ConditionedRadialResult
from schwgw.validation import phase6_radial_failure_boundary_ladders as boundary


def _spec(index: int) -> boundary.FailedKey:
    ell = index + 5
    key = {"ell": ell, "kM": "0.3", "sector": "odd"}
    return boundary.FailedKey(
        key=key,
        key_id=f"kM=0.3;sector=odd;ell={ell}",
        shard_id="kM=0.3;sector=odd",
        selected_r_out_M=300.0,
        required_radius_M=40.0,
        predecessor_failures={"baseline": "RuntimeError: predecessor failure"},
        predecessor_payload_identity={
            "mode": 0o444,
            "nlink": 1,
            "path": f"/immutable/failure-{ell}.json",
            "sha256": f"{ell:064x}",
            "size": 100,
        },
    )


def _result(request) -> ConditionedRadialResult:
    variation = (request.r_out - 300.0) * 1.0e-7 + (request.r_in_eps - 1.0e-6) * 1.0e4
    a_out = complex(0.5 + variation, 0.2 - variation * 0.1)
    transmission = 0.7
    reflection = abs(a_out) ** 2
    balance = reflection + transmission
    return ConditionedRadialResult(
        psi=complex(1.0 + variation, 0.1),
        dpsi_dr=complex(0.2, 1.0 - variation),
        A_in=1.0 + 0.0j,
        A_out=a_out,
        T_horizon=complex(0.1 + variation * 0.01, -0.1),
        log_abs_T_horizon=-2.0 + variation,
        phase_T_horizon=-0.5 + variation * 0.1,
        log_abs_psi=variation,
        phase_psi=0.1 + variation,
        log_abs_dpsi_dr=0.2 + variation,
        phase_dpsi_dr=1.0 - variation,
        finite_radius_states=(),
        diagnostics={
            "backend": boundary.EXPECTED_BACKEND,
            "method": boundary.EXPECTED_METHOD,
            "scientific_acceptance": False,
            "independent_validation": False,
            "paper_specific_envelope_used": False,
            "legacy_path_used": False,
            "newman_penrose_path_used": False,
            "pseudoinverse_used": False,
            "riccati_variable_used": False,
            "flux_balance": balance,
            "flux_residual": abs(balance - 1.0),
            "reflection_probability": reflection,
            "horizon_transmission_probability": transmission,
            "outer_boundary_residual": 1.0e-12,
            "match_condition_number": 2.0,
            "maximum_current_relative_drift": 1.0e-13,
            "current_drift_resolved": True,
            "segment_count": 10,
            "rhs_evaluations": 100,
        },
    )


def _solver(request, _background):
    return _result(request)


def _campaign_fixture(root: Path) -> None:
    root.mkdir()
    (root / "conditioning_campaign_index.json").write_text("{}\n", encoding="utf-8")
    (root / "manifest.json").write_text("{}\n", encoding="utf-8")


def _unseal(root: Path) -> None:
    if not root.exists():
        return
    root.chmod(0o755)
    for path in root.iterdir():
        if path.is_file():
            path.chmod(0o644)


def test_boundary_nodes_are_the_exact_requested_five() -> None:
    assert [node.node_id for node in boundary.BOUNDARY_NODES] == [
        "baseline",
        "r_in_3e-6",
        "r_in_3e-7",
        "r_out_x2",
        "r_out_x4",
    ]
    requests = [
        boundary.build_request(_spec(0), node) for node in boundary.BOUNDARY_NODES
    ]
    assert [(request.r_in_eps, request.r_out) for request in requests] == [
        (1.0e-6, 300.0),
        (3.0e-6, 300.0),
        (3.0e-7, 300.0),
        (1.0e-6, 600.0),
        (1.0e-6, 1200.0),
    ]
    assert all(
        request.rtol == 1.0e-10
        and request.atol == 1.0e-12
        and request.outer_series_order == 160
        for request in requests
    )


def test_execute_failed_key_reports_boundary_deltas_and_separate_budgets() -> None:
    record = boundary.execute_failed_key(_spec(0), ordinal=1, solver=_solver)

    assert len(record["nodes"]) == 5
    assert {node["status"] for node in record["nodes"]} == {"MEASURED"}
    assert record["ladder_summary"]["state"] == "PARTIAL"
    deltas = record["ladder_summary"]["deltas_from_baseline"]
    assert set(deltas) == {"r_in_3e-6", "r_in_3e-7", "r_out_x2", "r_out_x4"}
    assert deltas["r_out_x4"]["S"]["complex_abs"] > 0.0
    assert (
        deltas["r_in_3e-6"]["required_radius_state"]["psi"]["log_abs_abs_difference"]
        > 0.0
    )
    assert (
        record["ladder_summary"]["numerical_uncertainty_budget"]["status"] == "PARTIAL"
    )
    assert (
        record["ladder_summary"]["convention_uncertainty_budget"]["status"]
        == "NOT_ASSESSED"
    )
    assert record["scientific_acceptance"] is False


def test_execute_failed_key_retains_all_node_failures() -> None:
    def fail_solver(_request, _background):
        raise RuntimeError("deliberate")

    record = boundary.execute_failed_key(_spec(0), ordinal=1, solver=fail_solver)

    assert record["ladder_summary"]["state"] == "FAIL"
    assert [node["status"] for node in record["nodes"]] == ["FAIL"] * 5
    assert all(
        node["failure"] == "RuntimeError: deliberate" for node in record["nodes"]
    )


def test_run_limit_publishes_immutable_terminal_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    campaign = tmp_path / "campaign"
    _campaign_fixture(campaign)
    specs = (_spec(0), _spec(1))
    monkeypatch.setattr(boundary, "EXPECTED_FAILED_KEY_COUNT", 2)
    monkeypatch.setattr(boundary, "discover_failed_keys", lambda _root: specs)
    output = tmp_path / "boundary"
    try:
        result = boundary.run(
            output_root=output,
            campaign_root=campaign,
            runner_path=Path(__file__),
            limit=1,
            solver=_solver,
        )
        assert result["selected_key_count"] == 1
        assert result["solver_call_count"] == 5
        assert result["key_state_counts"] == {"PARTIAL": 1}
        assert stat.S_IMODE(output.stat().st_mode) == 0o555
        assert all(
            stat.S_IMODE(path.stat().st_mode) == 0o444 for path in output.iterdir()
        )
        assert boundary.validate_terminal_root(output) == result
    finally:
        _unseal(output)


def test_run_resumes_after_last_fsynced_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    campaign = tmp_path / "campaign"
    _campaign_fixture(campaign)
    specs = (_spec(0), _spec(1))
    monkeypatch.setattr(boundary, "EXPECTED_FAILED_KEY_COUNT", 2)
    monkeypatch.setattr(boundary, "discover_failed_keys", lambda _root: specs)
    output = tmp_path / "boundary"
    calls: list[int] = []

    def interrupt_second(request, background):
        calls.append(request.ell)
        if request.ell == 6:
            raise KeyboardInterrupt
        return _solver(request, background)

    with pytest.raises(KeyboardInterrupt):
        boundary.run(
            output_root=output,
            campaign_root=campaign,
            runner_path=Path(__file__),
            solver=interrupt_second,
        )
    assert calls == [5, 5, 5, 5, 5, 6]
    assert len((output / "records.jsonl").read_text().splitlines()) == 1

    resumed: list[int] = []

    def resumed_solver(request, background):
        resumed.append(request.ell)
        return _solver(request, background)

    try:
        result = boundary.run(
            output_root=output,
            campaign_root=campaign,
            runner_path=Path(__file__),
            resume=True,
            solver=resumed_solver,
        )
        assert resumed == [6, 6, 6, 6, 6]
        assert result["key_state_counts"] == {"PARTIAL": 2}
    finally:
        _unseal(output)
