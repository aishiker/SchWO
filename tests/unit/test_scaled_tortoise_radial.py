from __future__ import annotations

from pathlib import Path

import numpy as np

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.numerics.conditioned_radial import (
    ConditionedRadialRequest,
    solve_conditioned_radial_at_radius,
)
from schwgw.numerics.scaled_tortoise_radial import (
    solve_scaled_tortoise_radial_at_radius,
)
from schwgw.perturbations import Sector


def _request(*, ell: int, rtol: float = 1.0e-10) -> ConditionedRadialRequest:
    return ConditionedRadialRequest(
        sector=Sector.ODD,
        ell=ell,
        k=0.5,
        required_radius=40.0,
        evaluation_radii=(60.0,),
        r_out=300.0,
        rtol=rtol,
        atol=rtol * 1.0e-2,
        outer_series_order=160,
    )


def test_scaled_tortoise_source_isolated_from_riccati_and_pseudoinverse() -> None:
    source = Path("src/schwgw/numerics/scaled_tortoise_radial.py").read_text(
        encoding="utf-8"
    )

    assert "solve_ivp" in source
    assert "np.linalg.pinv" not in source
    assert "psi'/psi" in source  # diagnosis only; it is not the evolved variable


def test_scaled_tortoise_resolves_v1_riccati_failure_and_matches_ap_anchor() -> None:
    result = solve_scaled_tortoise_radial_at_radius(
        _request(ell=7, rtol=1.0e-12),
        SchwarzschildBackground(M=1.0),
    )
    ap_reference = complex(
        -0.9994091513485718583015918470167878041,
        -0.0343707462928422967685678844483510672,
    )

    assert abs(result.A_out - ap_reference) < 1.0e-10
    assert abs(result.log_abs_T_horizon - (-17.661518816119447)) < 1.0e-9
    assert result.diagnostics["riccati_variable_used"] is False
    assert result.diagnostics["positive_real_rescaling"] is True
    assert result.diagnostics["scientific_acceptance"] is False
    assert result.diagnostics["flux_residual"] < 1.0e-12
    assert [state.radius for state in result.finite_radius_states] == [40.0, 60.0]


def test_scaled_tortoise_agrees_with_v1_backend_where_both_are_regular() -> None:
    request = _request(ell=16)
    background = SchwarzschildBackground(M=1.0)
    repaired = solve_scaled_tortoise_radial_at_radius(request, background)
    predecessor = solve_conditioned_radial_at_radius(request, background)

    assert np.isfinite(repaired.A_out)
    assert abs(repaired.A_out - predecessor.A_out) < 2.0e-8
    assert abs(repaired.log_abs_T_horizon - predecessor.log_abs_T_horizon) < 2.0e-7
