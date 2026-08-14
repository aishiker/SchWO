from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

from schwgw.backgrounds import SchwarzschildBackground
import schwgw.io.direct_tablei as direct_tablei
from schwgw.io.direct_tablei import (
    AMPLITUDES,
    DenseRadialSpanCache,
    simultaneous_response_from_columns,
)
from schwgw.numerics import BoundaryConfig, solve_radial_mode
from schwgw.perturbations import Sector


def test_dense_local_q018_matches_standard_solution_near_anchor() -> None:
    background = SchwarzschildBackground(M=1.0)
    config = BoundaryConfig(
        r_in_eps=1.0e-6,
        r_out=300.0,
        rtol=1.0e-10,
        atol=1.0e-12,
        required_eval_radius=30.0,
    )
    step = 3.0e-3
    cache = DenseRadialSpanCache(
        lower=30.0 - 2.0 * step,
        anchor=30.0,
        upper=30.0 + 2.0 * step,
    )
    local = cache(Sector.ODD, 20, 0.5, background, config)
    standard = solve_radial_mode(Sector.ODD, 20, 0.5, background, config)

    for radius in (30.0 - step, 30.0, 30.0 + step):
        np.testing.assert_allclose(
            local.psi_at(radius),
            standard.psi_at(radius),
            rtol=8.0e-8,
            atol=1.0e-10,
        )
        np.testing.assert_allclose(
            local.dpsi_dr_at(radius),
            standard.dpsi_dr_at(radius),
            rtol=8.0e-8,
            atol=1.0e-10,
        )
    assert cache.metadata()["unique_solution_count"] == 1
    assert cache.metadata()["dense_local_q018_count"] == 1


def test_low_frequency_high_ell_dense_span_uses_rescaled_oracle() -> None:
    background = SchwarzschildBackground(M=1.0)
    config = BoundaryConfig(
        r_in_eps=1.0e-6,
        r_out=1200.0,
        rtol=1.0e-10,
        atol=1.0e-12,
        outer_basis="jost_1_over_r",
        outer_series_order=160,
    )

    solution = direct_tablei._solve_tablei_dense_mode(
        sector=Sector.EVEN,
        ell=58,
        k=0.1,
        background=background,
        config=config,
    )

    assert solution.diagnostics.solver == "direct_tablei_dense_local_q018"
    assert np.isfinite(solution.psi_at(30.0))
    assert np.isfinite(solution.dpsi_dr_at(30.0))
    assert solution.diagnostics.boundary_residual < 1.0e-12


def test_simultaneous_response_adds_off_diagonal_columns_before_ratio() -> None:
    radius = np.asarray((10.0, 20.0))
    theta = np.asarray((0.3, 0.8))
    diagonal_plus = np.asarray((1.2 + 0.3j, 0.8 - 0.1j))
    diagonal_cross = np.asarray((0.9 - 0.2j, 1.1 + 0.4j))
    cross_from_plus = np.asarray((0.2 + 0.1j, -0.3 + 0.05j))
    plus_from_cross = np.asarray((-0.1 + 0.4j, 0.2 - 0.2j))

    plus, cross = simultaneous_response_from_columns(
        kM=0.7,
        point_r=radius,
        point_theta=theta,
        F_plus_diagonal=diagonal_plus,
        F_cross_diagonal=diagonal_cross,
        h_cross_from_plus=cross_from_plus,
        h_plus_from_cross=plus_from_cross,
    )

    phase = np.exp(1.0j * 0.7 * radius * np.cos(theta))
    np.testing.assert_allclose(
        plus,
        diagonal_plus + plus_from_cross / (AMPLITUDES["plus"] * phase),
    )
    np.testing.assert_allclose(
        cross,
        diagonal_cross + cross_from_plus / (AMPLITUDES["cross"] * phase),
    )


def test_frequency_production_extrapolates_three_rout_values_and_binds_frame(
    monkeypatch,
) -> None:
    def synthetic_columns(**kwargs):
        radius = kwargs["boundary_config"].r_out
        assert radius is not None
        tail = 4.0 / radius + 8.0 / radius**2
        return SimpleNamespace(
            F_plus=(1.2 + 0.3j) + tail,
            F_cross=(0.8 - 0.2j) - 0.5j * tail,
            h_cross_from_plus=(0.02 + 0.01j) + 0.2 * tail,
            h_plus_from_cross=(-0.01 + 0.03j) - 0.1j * tail,
        )

    monkeypatch.setattr(
        direct_tablei,
        "compute_direct_response_columns",
        synthetic_columns,
    )
    arrays, metadata = direct_tablei._compute_frequency(
        0.5,
        (2, 3),
        observer_frame="li_literal_cartesian",
        r_out_ladder=(300.0, 600.0, 1200.0),
    )

    assert arrays["F_plus_r_out_ladder"].shape == (3, 2, 8)
    np.testing.assert_allclose(arrays["F_plus_complex"], 1.2 + 0.3j, atol=1e-14)
    np.testing.assert_allclose(arrays["F_cross_complex"], 0.8 - 0.2j, atol=1e-14)
    assert metadata["observer_frame"] == "li_literal_cartesian"
    assert metadata["physical_claim"] is False
    assert metadata["primary_observable"] == "electric_tidal_tensor_E_ij"
    assert metadata["derived_observable"] == "monochromatic_equivalent_tidal_strain"
    assert metadata["observer_worldline"].startswith(
        "fixed Schwarzschild-coordinate observer"
    )
    assert "Phase-6 axis ladder not yet closed" in metadata["axis_regularization"]
    assert metadata["physical_within_frozen_gauge_frame_convention"] is True
    assert metadata["literal_li_paper_observer_equivalence"] is True
    assert metadata["r_out_ladder"] == [300.0, 600.0, 1200.0]
    assert metadata["paper_equivalence"] == "YELLOW"


def test_low_frequency_outer_ladder_rejects_unresolved_jost_columns() -> None:
    background = direct_tablei.SchwarzschildBackground(M=1.0)

    with pytest.raises(
        direct_tablei.DirectTableIError,
        match="ill-conditioned before science",
    ):
        direct_tablei._validate_outer_ladder_conditioning(
            kM=0.1,
            lmax=84,
            r_out_ladder=(300.0, 600.0, 1200.0),
            background=background,
        )


def test_default_outer_ladder_resolves_low_frequency_jost_columns() -> None:
    background = direct_tablei.SchwarzschildBackground(M=1.0)

    record = direct_tablei._validate_outer_ladder_conditioning(
        kM=0.1,
        lmax=84,
        r_out_ladder=direct_tablei.DEFAULT_R_OUT_LADDER,
        background=background,
    )

    assert direct_tablei.DEFAULT_R_OUT_LADDER == (1200.0, 1800.0, 2400.0)
    assert record["max_condition_number"] < 15.0
    assert record["max_local_ode_residual"] < 2.0e-10
