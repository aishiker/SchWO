from __future__ import annotations

from schwgw.validation.phase6_v1_final_radial_baseline import (
    _solve_key,
    run_final_baseline,
    validate_published_final_baseline,
)


def test_final_baseline_single_key_passes_repaired_invariants() -> None:
    record = _solve_key((0, {"ell": 2, "kM": "0.01", "sector": "odd"}))
    assert record["state"] == "PASS"
    assert all(record["invariants"].values())
    assert record["diagnostics"]["selected_r_out_M"] >= 300.0


def test_limit_two_campaign_seals_and_reloads(tmp_path) -> None:
    root = tmp_path / "baseline"
    assert run_final_baseline(output_root=root, workers=1, limit=2) == 0
    summary = validate_published_final_baseline(root)
    assert summary["overall_state"] == "PARTIAL"
    assert summary["completed_key_count"] == 2
    assert summary["failed_key_count"] == 0
