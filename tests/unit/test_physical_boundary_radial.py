from __future__ import annotations

from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
from schwgw.numerics.conditioned_radial import ConditionedRadialRequest
from schwgw.numerics.physical_boundary_radial import (
    select_physical_outer_radius,
    solve_physical_boundary_radial_at_radius,
)
from schwgw.perturbations import Sector


def test_small_frequency_turning_proxy_expands_fixed_radius_ladder() -> None:
    request = ConditionedRadialRequest(
        sector=Sector.ODD,
        ell=50,
        k=0.01,
        required_radius=40.0,
        r_out=300.0,
        r_in_eps=1.0e-9,
    )
    selection = select_physical_outer_radius(request, SchwarzschildBackground(M=1.0))
    assert selection.selected_r_out_M >= (50 * 51) ** 0.5 / 0.01
    assert selection.selected_quality.state == "PASS"


def test_turning_aware_solve_is_finite_and_legacy_free() -> None:
    request = ConditionedRadialRequest(
        sector=Sector.EVEN,
        ell=50,
        k=0.01,
        required_radius=40.0,
        r_out=300.0,
        r_in_eps=1.0e-9,
    )
    result = solve_physical_boundary_radial_at_radius(
        request, SchwarzschildBackground(M=1.0)
    )
    assert result.diagnostics["selected_r_out"] > 300.0
    assert result.diagnostics["paper_specific_envelope_used"] is False
    assert result.diagnostics["legacy_path_used"] is False
    assert result.diagnostics["pseudoinverse_used"] is False
