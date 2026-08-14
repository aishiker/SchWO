from __future__ import annotations

from pathlib import Path
import stat

import pytest

from schwgw.numerics.conditioned_radial import ConditionedRadialResult
from schwgw.validation import phase6_radial_success_continuity as continuity


def _spec(index: int) -> continuity.SuccessfulKey:
    ell = index + 2
    key = {"ell": ell, "kM": "0.5", "sector": "odd"}
    return continuity.SuccessfulKey(
        key=key,
        key_id=f"kM=0.5;sector=odd;ell={ell}",
        shard_id="kM=0.5;sector=odd",
        predecessor_payload_identity={
            "mode": 0o444,
            "nlink": 1,
            "path": f"/immutable/payload-{ell}.json",
            "sha256": f"{ell:064x}",
            "size": 100,
        },
        required_radius_M=40.0,
        r_out_M=300.0,
        r_in_eps=1.0e-6,
        rtol=1.0e-10,
        atol=1.0e-12,
        jost_order=160,
        predecessor_A_out=complex(0.5, 0.2),
        predecessor_T_horizon=complex(0.1, -0.1),
        predecessor_log_abs_T=-2.0,
        predecessor_phase_T=-0.5,
        predecessor_flux_residual=1.0e-10,
        predecessor_flux_balance=1.0 + 1.0e-10,
        predecessor_reflection_probability=0.29,
        predecessor_transmission_probability=0.71 + 1.0e-10,
        predecessor_numerical_budget={"status": "PARTIAL", "components": {}},
        predecessor_convention_budget={"status": "PARTIAL", "components": {}},
    )


def _result(*, ell: int) -> ConditionedRadialResult:
    a_out = complex(0.5 + ell * 1.0e-6, 0.2)
    transmission = 0.71
    reflection = abs(a_out) ** 2
    balance = reflection + transmission
    return ConditionedRadialResult(
        psi=1.0 + 0.0j,
        dpsi_dr=0.0 + 1.0j,
        A_in=1.0 + 0.0j,
        A_out=a_out,
        T_horizon=complex(0.1, -0.1),
        log_abs_T_horizon=-2.0 + ell * 1.0e-7,
        phase_T_horizon=-0.5 + ell * 1.0e-8,
        log_abs_psi=0.0,
        phase_psi=0.0,
        log_abs_dpsi_dr=0.0,
        phase_dpsi_dr=1.0,
        finite_radius_states=(),
        diagnostics={
            "backend": continuity.EXPECTED_BACKEND,
            "method": continuity.EXPECTED_METHOD,
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
            "runtime_seconds": 0.01,
        },
    )


def _solver(request, _background):
    return _result(ell=request.ell)


def _unseal(root: Path) -> None:
    if not root.exists():
        return
    root.chmod(0o755)
    for path in root.iterdir():
        if path.is_file():
            path.chmod(0o644)


def _campaign_fixture(root: Path) -> None:
    root.mkdir()
    (root / "conditioning_campaign_index.json").write_text("{}\n", encoding="utf-8")
    (root / "manifest.json").write_text("{}\n", encoding="utf-8")


def test_compare_successful_key_is_partial_with_separate_budgets() -> None:
    record = continuity.compare_successful_key(_spec(0), ordinal=1, solver=_solver)

    assert record["status"] == "PARTIAL"
    assert record["scientific_acceptance"] is False
    assert record["comparison"]["A_out"]["complex_abs_difference"] > 0.0
    assert record["comparison"]["T_horizon"]["log_abs_abs_difference"] > 0.0
    assert record["numerical_uncertainty_budget"]["status"] == "PARTIAL"
    assert record["convention_uncertainty_budget"]["status"] == "NOT_ASSESSED"


def test_compare_successful_key_retains_solver_failure() -> None:
    def fail_solver(_request, _background):
        raise RuntimeError("deliberate")

    record = continuity.compare_successful_key(_spec(0), ordinal=1, solver=fail_solver)

    assert record["status"] == "FAIL"
    assert record["failure"] == "RuntimeError: deliberate"
    assert record["candidate"] is None
    assert record["scientific_acceptance"] is False


def test_run_publishes_fresh_immutable_limit_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    campaign = tmp_path / "campaign"
    _campaign_fixture(campaign)
    specs = (_spec(0), _spec(1))
    monkeypatch.setattr(continuity, "discover_successful_keys", lambda _root: specs)
    output = tmp_path / "continuity"
    try:
        result = continuity.run(
            output_root=output,
            campaign_root=campaign,
            runner_path=Path(__file__),
            limit=1,
            solver=_solver,
        )

        assert result["selected_key_count"] == 1
        assert result["key_state_counts"] == {"PARTIAL": 1}
        assert stat.S_IMODE(output.stat().st_mode) == 0o555
        assert all(
            stat.S_IMODE(path.stat().st_mode) == 0o444 for path in output.iterdir()
        )
        assert continuity.validate_terminal_root(output) == result
        with pytest.raises(RuntimeError, match="already exists"):
            continuity.run(
                output_root=output,
                campaign_root=campaign,
                runner_path=Path(__file__),
                limit=1,
                solver=_solver,
            )
    finally:
        _unseal(output)


def test_run_resumes_exact_jsonl_prefix_without_recomputing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    campaign = tmp_path / "campaign"
    _campaign_fixture(campaign)
    specs = (_spec(0), _spec(1))
    monkeypatch.setattr(continuity, "discover_successful_keys", lambda _root: specs)
    output = tmp_path / "continuity"
    calls: list[int] = []

    def interrupt_second(request, background):
        calls.append(request.ell)
        if request.ell == 3:
            raise KeyboardInterrupt
        return _solver(request, background)

    with pytest.raises(KeyboardInterrupt):
        continuity.run(
            output_root=output,
            campaign_root=campaign,
            runner_path=Path(__file__),
            solver=interrupt_second,
        )
    assert calls == [2, 3]
    assert len((output / "records.jsonl").read_text().splitlines()) == 1

    resumed_calls: list[int] = []

    def resume_solver(request, background):
        resumed_calls.append(request.ell)
        return _solver(request, background)

    try:
        result = continuity.run(
            output_root=output,
            campaign_root=campaign,
            runner_path=Path(__file__),
            resume=True,
            solver=resume_solver,
        )
        assert resumed_calls == [3]
        assert result["key_state_counts"] == {"PARTIAL": 2}
    finally:
        _unseal(output)


def test_exact_cpython_runtime_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(continuity.platform, "python_implementation", lambda: "PyPy")
    with pytest.raises(RuntimeError, match="exact CPython 3.14"):
        continuity.require_exact_cpython314()
