from __future__ import annotations

import json

import pytest

import schwgw.validation.phase6_v1_final_radial_baseline_v2 as baseline_v2
from schwgw.validation.phase6_v1_final_radial_baseline_v2 import (
    _solve_key_v2,
    run_final_baseline_v2,
    validate_published_final_baseline_v2,
)


def test_turning_aware_worker_repairs_small_frequency_high_ell() -> None:
    record = _solve_key_v2((0, {"ell": 50, "kM": "0.01", "sector": "odd"}))
    assert record["state"] == "PASS"
    assert all(record["invariants"].values())
    assert record["diagnostics"]["selected_r_out_M"] >= ((50 * 51) ** 0.5 / 0.01)
    assert record["diagnostics"]["turning_proxy_M"] > 300.0


def test_limit_two_v2_campaign_seals_and_reloads(tmp_path) -> None:
    root = tmp_path / "baseline_v2"
    assert run_final_baseline_v2(output_root=root, workers=1, limit=2) == 0
    summary = validate_published_final_baseline_v2(root)
    assert summary["overall_state"] == "PARTIAL"
    assert summary["completed_key_count"] == 2
    assert summary["failed_key_count"] == 0
    report = json.loads((root / "report.json").read_bytes())
    assert report["state"] == "PARTIAL"
    assert report["parameter_domain"]["expected_items"] == 2
    assert report["numerical_uncertainty_budget"]["r_out"]["state"] == "PARTIAL"
    assert report["numerical_uncertainty_budget"]["backend_difference"]["state"] == (
        "NOT_ASSESSED"
    )


def test_v2_live_plan_provenance_drift_fails_closed(tmp_path, monkeypatch) -> None:
    root = tmp_path / "baseline_v2_drift"
    assert run_final_baseline_v2(output_root=root, workers=1, limit=1) == 0
    original_version = baseline_v2.version
    monkeypatch.setattr(
        baseline_v2,
        "version",
        lambda name: "0.0.0-tampered" if name == "numpy" else original_version(name),
    )
    with pytest.raises(ValueError, match="live plan/source/runtime identity changed"):
        validate_published_final_baseline_v2(root)
