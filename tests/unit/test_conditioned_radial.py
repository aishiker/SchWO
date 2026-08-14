from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.numerics import BoundaryConfig, solve_radial_mode
from schwgw.numerics.conditioned_radial import (
    ConditionedRadialRequest,
    _probability_from_log,
    solve_conditioned_radial_at_radius,
)
from schwgw.numerics.boundary_conditions import radial_domain
from schwgw.perturbations import Sector


def _request(
    *,
    sector: Sector = Sector.ODD,
    ell: int = 153,
    order: int = 120,
) -> ConditionedRadialRequest:
    return ConditionedRadialRequest(
        sector=sector,
        ell=ell,
        k=2.0,
        required_radius=60.0,
        r_out=300.0,
        r_in_eps=1.0e-6,
        rtol=1.0e-10,
        atol=1.0e-12,
        outer_series_order=order,
    )


def test_conditioned_backend_is_generic_and_has_no_precision_alias() -> None:
    source = Path("src/schwgw/numerics/conditioned_radial.py").read_text(
        encoding="utf-8"
    )

    assert "q018" not in source.lower()
    assert "pinv" not in source.lower()
    with pytest.raises(TypeError, match="precision_dps"):
        ConditionedRadialRequest(  # type: ignore[call-arg]
            sector=Sector.ODD,
            ell=20,
            k=1.0,
            required_radius=20.0,
            r_out=80.0,
            precision_dps=80,
        )


def test_conditioned_probability_log_conversion_is_fail_closed() -> None:
    assert _probability_from_log(-1000.0) == 0.0
    assert _probability_from_log(0.0) == 1.0
    with pytest.raises(RuntimeError, match="non-finite"):
        _probability_from_log(float("nan"))
    with pytest.raises(RuntimeError, match="exceeds float64"):
        _probability_from_log(1000.0)


@pytest.mark.parametrize("sector", [Sector.ODD, Sector.EVEN])
def test_conditioned_q018_domain_mode_is_finite_without_paper_envelope(
    sector: Sector,
) -> None:
    result = solve_conditioned_radial_at_radius(
        _request(sector=sector),
        SchwarzschildBackground(M=1.0),
    )

    assert result.valid_at_required_radius is True
    assert np.isfinite(result.A_out)
    assert abs(abs(result.A_out) - 1.0) < 2.0e-6
    assert result.diagnostics["paper_specific_envelope_used"] is False
    assert result.diagnostics["scientific_acceptance"] is False
    assert result.diagnostics["actual_precision_bits"] == 53
    assert result.diagnostics["outer_boundary_residual"] < 1.0e-12
    assert result.diagnostics["flux_residual"] < 1.0e-12


def test_conditioned_jost_order_ladder_closes_for_representative_mode() -> None:
    background = SchwarzschildBackground(M=1.0)
    order_80 = solve_conditioned_radial_at_radius(
        _request(order=80),
        background,
    )
    order_120 = solve_conditioned_radial_at_radius(
        _request(order=120),
        background,
    )

    assert abs(order_80.A_out - order_120.A_out) < 1.0e-11
    assert abs(order_80.psi - order_120.psi) < 1.0e-16


def test_conditioned_batch_reuses_one_mode_solve_for_finite_radii() -> None:
    background = SchwarzschildBackground(M=1.0)
    batch = solve_conditioned_radial_at_radius(
        ConditionedRadialRequest(
            sector=Sector.ODD,
            ell=40,
            k=1.0,
            required_radius=20.0,
            evaluation_radii=(25.0, 30.0),
            r_out=80.0,
            outer_series_order=80,
        ),
        background,
    )
    independent = solve_conditioned_radial_at_radius(
        ConditionedRadialRequest(
            sector=Sector.ODD,
            ell=40,
            k=1.0,
            required_radius=30.0,
            r_out=80.0,
            outer_series_order=80,
        ),
        background,
    )

    assert [state.radius for state in batch.finite_radius_states] == [
        20.0,
        25.0,
        30.0,
    ]
    state_30 = batch.finite_radius_states[-1]
    np.testing.assert_allclose(state_30.psi, independent.psi, rtol=3.0e-10)
    np.testing.assert_allclose(
        state_30.dpsi_dr,
        independent.dpsi_dr,
        rtol=3.0e-10,
    )
    np.testing.assert_allclose(batch.A_out, independent.A_out, rtol=3.0e-10)
    np.testing.assert_allclose(
        batch.T_horizon,
        independent.T_horizon,
        rtol=3.0e-10,
    )


def test_conditioned_batch_rejects_invalid_finite_radius_inventory() -> None:
    with pytest.raises(ValueError, match="must not contain duplicates"):
        ConditionedRadialRequest(
            sector=Sector.ODD,
            ell=20,
            k=1.0,
            required_radius=20.0,
            evaluation_radii=(25.0, 25.0),
            r_out=80.0,
        )
    with pytest.raises(ValueError, match=r"\[required_radius, r_out\)"):
        ConditionedRadialRequest(
            sector=Sector.ODD,
            ell=20,
            k=1.0,
            required_radius=20.0,
            evaluation_radii=(19.0,),
            r_out=80.0,
        )


def test_forced_conditioned_backend_adapts_fail_closed_to_public_api() -> None:
    background = SchwarzschildBackground(M=1.0)
    solution = solve_radial_mode(
        Sector.ODD,
        40,
        1.0,
        background,
        BoundaryConfig(
            r_out=80.0,
            required_eval_radius=20.0,
            conditioning_backend="scaled_log_riccati_forced",
            outer_series_order=80,
        ),
    )

    warning = solution.diagnostics.warnings[0]
    assert solution.valid_until_r == 20.0
    assert np.isfinite(solution.psi_at(20.0))
    assert solution.diagnostics.solver == "conditioned_scaled_log_riccati"
    assert solution.diagnostics.wronskian_residual == 1.0
    assert solution.diagnostics.flux_residual < 1.0e-10
    assert warning.metadata is not None
    assert warning.metadata["paper_specific_envelope_used"] is False
    assert warning.metadata["wronskian_residual_available"] is False
    assert warning.metadata["flux_residual_available"] is True
    with pytest.raises(ValueError, match="outside the solved domain"):
        solution.psi_at(20.0 + 1.0e-8)


def test_auto_conditioning_selector_preserves_low_barrier_solver() -> None:
    background = SchwarzschildBackground(M=1.0)
    solution = solve_radial_mode(
        Sector.ODD,
        2,
        0.5,
        background,
        BoundaryConfig(
            r_out=40.0,
            required_eval_radius=20.0,
            conditioning_backend="scaled_log_riccati_auto",
        ),
    )

    assert solution.diagnostics.solver == "outward_shooting"


@pytest.mark.parametrize("sector", [Sector.ODD, Sector.EVEN])
def test_conditioned_low_mode_matches_independent_public_shooting(
    sector: Sector,
) -> None:
    background = SchwarzschildBackground(M=1.0)
    request = ConditionedRadialRequest(
        sector=sector,
        ell=2,
        k=0.5,
        required_radius=20.0,
        r_out=80.0,
        outer_series_order=120,
    )
    conditioned = solve_conditioned_radial_at_radius(request, background)
    shooting = solve_radial_mode(
        sector,
        2,
        0.5,
        background,
        BoundaryConfig(r_out=80.0, outer_series_order=120),
    )

    np.testing.assert_allclose(
        conditioned.A_out,
        shooting.A_out / shooting.A_in,
        rtol=0.0,
        atol=3.0e-9,
    )
    np.testing.assert_allclose(
        conditioned.T_horizon,
        1.0 / shooting.A_in,
        rtol=0.0,
        atol=3.0e-9,
    )
    assert conditioned.diagnostics["flux_residual"] < 1.0e-8


def test_conditioning_config_fails_closed_on_legacy_or_missing_radius() -> None:
    background = SchwarzschildBackground(M=1.0)
    with pytest.raises(ValueError, match="requires required_eval_radius"):
        radial_domain(
            ell=20,
            k=1.0,
            background=background,
            config=BoundaryConfig(conditioning_backend="scaled_log_riccati_auto"),
        )
    with pytest.raises(ValueError, match="cannot be enabled together"):
        radial_domain(
            ell=153,
            k=2.0,
            background=background,
            config=BoundaryConfig(
                r_out=300.0,
                required_eval_radius=60.0,
                conditioning_backend="scaled_log_riccati_auto",
                experimental_required_radius_oracle="q018_riccati",
            ),
        )
