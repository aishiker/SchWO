from __future__ import annotations

import math

from schwgw.validation import phase6_v1_radial_acceptance as acceptance


def test_selected_solver_uses_repaired_boundaries_and_no_legacy_path() -> None:
    node = acceptance._solve(
        key={"ell": 2, "kM": "0.5", "sector": "odd"},
        r_in_eps=acceptance.R_IN_BASELINE,
        r_out=acceptance.R_OUT_BASELINE,
        jost_order=acceptance.JOST_BASELINE,
        rtol=acceptance.RTOL_BASELINE,
        atol=acceptance.ATOL_BASELINE,
    )
    diagnostics = node["diagnostics"]
    assert diagnostics["legacy_path_used"] is False
    assert diagnostics["newman_penrose_path_used"] is False
    assert diagnostics["pseudoinverse_used"] is False
    assert diagnostics["paper_specific_envelope_used"] is False
    assert diagnostics["selected_r_out_M"] >= acceptance.R_OUT_BASELINE
    assert diagnostics["flux_residual"] <= acceptance.THRESHOLDS["flux_residual"]
    assert math.isfinite(node["log_abs_T_horizon"])
    assert math.isfinite(node["phase_T_horizon"])


def test_acceptance_check_is_fail_closed() -> None:
    assert acceptance._check(1.0e-7, 2.0e-6)["state"] == "PASS"
    assert acceptance._check(3.0e-6, 2.0e-6)["state"] == "FAIL"
    assert acceptance._check(float("nan"), 2.0e-6)["state"] == "FAIL"
