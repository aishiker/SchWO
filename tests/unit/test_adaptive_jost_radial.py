from __future__ import annotations

from pathlib import Path

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.numerics.adaptive_jost_radial import (
    JOST_SERIES_RESIDUAL_LIMIT,
    JOST_TAIL_RATIO_LIMIT,
    select_conditioned_outer_radius,
    solve_adaptive_jost_radial_at_radius,
)
from schwgw.numerics.conditioned_radial import ConditionedRadialRequest
from schwgw.perturbations import Sector


def _request(*, sector: Sector, ell: int, k: float) -> ConditionedRadialRequest:
    return ConditionedRadialRequest(
        sector=sector,
        ell=ell,
        k=k,
        required_radius=40.0,
        r_out=300.0,
        rtol=1.0e-10,
        atol=1.0e-12,
        outer_series_order=160,
    )


def test_adaptive_backend_is_generic_and_keeps_v1_source_immutable() -> None:
    source = Path("src/schwgw/numerics/adaptive_jost_radial.py").read_text(
        encoding="utf-8"
    )

    assert "paper_specific_envelope_used" in source
    assert "np.linalg.pinv" not in source
    assert "legacy" not in source.lower()
    assert "scaled_tortoise_radial.py" not in source


def test_selector_keeps_a_well_conditioned_requested_radius() -> None:
    selection = select_conditioned_outer_radius(
        _request(sector=Sector.ODD, ell=16, k=0.5),
        SchwarzschildBackground(M=1.0),
    )

    assert selection.selected_radius_factor == 1.0
    assert selection.selected_r_out_M == 300.0
    assert selection.selected_quality.state == "PASS"


def test_selector_expands_only_as_far_as_high_ell_basis_quality_requires() -> None:
    background = SchwarzschildBackground(M=1.0)
    mild = select_conditioned_outer_radius(
        _request(sector=Sector.ODD, ell=605, k=8.0),
        background,
    )
    worst = select_conditioned_outer_radius(
        _request(sector=Sector.EVEN, ell=720, k=8.0),
        background,
    )

    assert mild.selected_radius_factor == 2.0
    assert mild.selected_r_out_M == 600.0
    assert worst.selected_radius_factor == 4.0
    assert worst.selected_r_out_M == 1200.0
    assert worst.selected_quality.maximum_series_residual <= JOST_SERIES_RESIDUAL_LIMIT
    assert worst.selected_quality.maximum_tail_ratio <= JOST_TAIL_RATIO_LIMIT
    assert [candidate.state for candidate in worst.candidates] == [
        "FAIL",
        "FAIL",
        "PASS",
    ]


def test_adaptive_backend_resolves_the_worst_frozen_high_ell_key() -> None:
    result = solve_adaptive_jost_radial_at_radius(
        _request(sector=Sector.ODD, ell=720, k=8.0),
        SchwarzschildBackground(M=1.0),
    )
    boundary_reference = complex(-0.08161565914738862, 0.9966638772334241)

    assert abs(result.A_out - boundary_reference) < 2.0e-12
    assert abs(result.log_abs_T_horizon - (-3444.1061443547583)) < 2.0e-9
    assert result.diagnostics["backend"] == (
        "scipy_float64_adaptive_jost_scaled_tortoise_v2"
    )
    assert result.diagnostics["base_backend"] == (
        "scipy_float64_scaled_tortoise_radial_repair_v1"
    )
    assert result.diagnostics["selected_r_out"] == 1200.0
    assert result.diagnostics["selected_r_out_factor"] == 4.0
    assert result.diagnostics["adaptive_outer_radius_used"] is True
    assert result.diagnostics["paper_specific_envelope_used"] is False
    assert result.diagnostics["legacy_path_used"] is False
    assert result.diagnostics["pseudoinverse_used"] is False
    assert result.diagnostics["scientific_acceptance"] is False
    assert result.diagnostics["flux_residual"] < 1.0e-12
