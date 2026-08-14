from __future__ import annotations

import math

import numpy as np
import pytest
from scipy.special import sph_harm_y

from schwgw.angular import spin_weighted_sph_harm
from schwgw.backgrounds import SchwarzschildBackground
from schwgw.numerics import BoundaryConfig, solve_radial_mode
from schwgw.perturbations import (
    Sector,
    V_RW,
    V_Zerilli,
    lambda_parameter,
    reconstruct_metric_mode,
)
from schwgw.scattering.partial_wave import direct_cartesian_tt_strict_np_weyl
from schwgw.scattering.metric_curvature import _harmonic_component_jets
from schwgw.validation.phase6_asymptotic import (
    MartelPoissonMasterMode,
    li_even_master_from_rw_metric,
    li_master_to_martel_poisson,
    martel_poisson_even_master_from_rw_metric,
    martel_poisson_odd_master_from_rw_metric,
    martel_poisson_angular_operators,
    martel_poisson_strain,
    monochromatic_martel_poisson_flux,
    sigma_l,
)
from schwgw.validation.phase6_cross_checks import (
    PROJECT_OUTGOING_PSI4_CONVENTION,
    compare_complex_routes,
    outgoing_strain_to_project_strict_np_psi4,
    pairwise_route_comparisons,
)


def test_mp_angular_operators_match_frozen_spin_weight_identity() -> None:
    for ell, m in ((2, 2), (3, 1), (4, -2), (5, 0)):
        angular_even, angular_odd = martel_poisson_angular_operators(
            ell,
            m,
            0.73,
            0.31,
        )
        expected = (
            0.5
            * math.sqrt(sigma_l(ell))
            * (-1) ** m
            * spin_weighted_sph_harm(-2, ell, m, 0.73, 0.31)
        )
        np.testing.assert_allclose(
            angular_even - 1.0j * angular_odd,
            expected,
            rtol=3e-13,
            atol=3e-13,
        )
        expected_plus = (
            0.5
            * math.sqrt(sigma_l(ell))
            * (-1) ** m
            * spin_weighted_sph_harm(2, ell, m, 0.73, 0.31)
        )
        np.testing.assert_allclose(
            angular_even + 1.0j * angular_odd,
            expected_plus,
            rtol=3e-13,
            atol=3e-13,
        )


@pytest.mark.parametrize("m", [0, 2, -2, 719, -719])
def test_mp_angular_operators_remain_finite_at_phase6_high_ell(m: int) -> None:
    angular_even, angular_odd = martel_poisson_angular_operators(
        720,
        m,
        0.7,
        0.2,
    )

    assert np.isfinite(angular_even)
    assert np.isfinite(angular_odd)


@pytest.mark.parametrize("theta", [1.0e-3, 1.0e-4, 1.0e-6, 1.0e-8])
def test_mp_axis_ladder_nodes_are_finite_but_not_an_extrapolation(
    theta: float,
) -> None:
    angular_even, angular_odd = martel_poisson_angular_operators(
        120,
        2,
        theta,
        0.0,
    )

    assert np.isfinite(angular_even)
    assert np.isfinite(angular_odd)


def test_mp_infinity_and_horizon_odd_sign_are_explicit() -> None:
    mode = MartelPoissonMasterMode(
        ell=3,
        m=2,
        psi_even=0.4 - 0.2j,
        psi_odd=-0.1 + 0.7j,
    )
    angular_even, angular_odd = martel_poisson_angular_operators(3, 2, 0.8, 0.2)
    infinity = martel_poisson_strain(
        [mode],
        areal_scale=100.0,
        theta=0.8,
        phi=0.2,
        boundary="future_null_infinity",
    )
    horizon = martel_poisson_strain(
        [mode],
        areal_scale=2.0,
        theta=0.8,
        phi=0.2,
        boundary="event_horizon",
        mass=1.0,
    )
    assert infinity.h_plus == pytest.approx(
        (mode.psi_even * angular_even - mode.psi_odd * angular_odd) / 100.0
    )
    assert infinity.h_cross == pytest.approx(
        (mode.psi_even * angular_odd + mode.psi_odd * angular_even) / 100.0
    )
    assert horizon.h_plus == pytest.approx(
        (mode.psi_even * angular_even + mode.psi_odd * angular_odd) / 2.0
    )
    assert horizon.h_cross == pytest.approx(
        (mode.psi_even * angular_odd - mode.psi_odd * angular_even) / 2.0
    )


def test_li_to_mp_master_normalization_bridge_is_explicit_and_invertible() -> None:
    li_even = 0.4 - 0.7j
    li_odd = -0.2 + 0.3j
    k = 0.8
    bridge = li_master_to_martel_poisson(
        ell=3,
        m=-2,
        k=k,
        psi_li_even=li_even,
        psi_li_odd=li_odd,
    )
    assert bridge.mode.psi_even == li_even
    assert bridge.mode.psi_odd == pytest.approx(2.0j * li_odd / k)
    assert bridge.mode.psi_odd * k / (2.0j) == pytest.approx(li_odd)
    assert bridge.even_formula == "Psi_ZM = psi_Li_even"
    assert bridge.odd_formula == "Psi_CPM = (2 i / k) psi_Li_odd"
    assert "exp(-i k t)" in bridge.assumptions


def test_li_to_mp_bridge_rejects_zero_frequency_and_nonfinite_amplitudes() -> None:
    with pytest.raises(ValueError, match="positive"):
        li_master_to_martel_poisson(ell=2, m=2, k=0.0)
    with pytest.raises(ValueError, match="finite"):
        li_master_to_martel_poisson(
            ell=2,
            m=2,
            k=1.0,
            psi_li_even=complex(float("nan"), 0.0),
        )


@pytest.mark.parametrize("sector", [Sector.EVEN, Sector.ODD])
def test_li_to_mp_bridge_roundtrips_through_rw_metric_and_ode(
    sector: Sector,
) -> None:
    background = SchwarzschildBackground(M=1.0)
    ell = 3
    k = 0.7
    radius = 20.0
    solution = solve_radial_mode(
        sector,
        ell,
        k,
        background,
        BoundaryConfig(r_out=80.0, outer_series_order=120),
    )

    def metric_at(r: float):
        return reconstruct_metric_mode(
            sector,
            ell,
            k,
            r,
            solution.psi_at(r),
            solution.dpsi_dr_at(r),
            background,
        ).components

    metric = metric_at(radius)
    expected_li = solution.psi_at(radius)
    derivative_li = solution.dpsi_dr_at(radius)
    f = background.f(radius)
    fp = background.df_dr(radius)
    potential = (V_Zerilli if sector is Sector.EVEN else V_RW)(
        ell,
        radius,
        background,
    )
    second_derivative_li = (
        -(f * fp * derivative_li + (k**2 - potential) * expected_li) / f**2
    )
    if sector is Sector.EVEN:
        direct_li = li_even_master_from_rw_metric(
            ell=ell,
            k=k,
            mass=1.0,
            r=radius,
            T0=metric["T0"],
            Rt=metric["Rt"],
        )
        lambda_ = lambda_parameter(ell)
        mass_over_r = 1.0 / radius
        capital_lambda = lambda_ + 3.0 * mass_over_r
        numerator = (
            lambda_ * (lambda_ + 1.0)
            + 3.0 * lambda_ * mass_over_r
            + 6.0 * mass_over_r**2
        )
        coefficient = numerator / capital_lambda
        coefficient_du = (
            (3.0 * lambda_ + 12.0 * mass_over_r) * capital_lambda - 3.0 * numerator
        ) / capital_lambda**2
        coefficient_dr = coefficient_du * (-mass_over_r / radius)
        derivative = (
            fp * derivative_li
            + f * second_derivative_li
            + coefficient_dr * expected_li / radius
            + coefficient * derivative_li / radius
            - coefficient * expected_li / radius**2
        )
        mp = martel_poisson_even_master_from_rw_metric(
            ell=ell,
            mass=1.0,
            r=radius,
            T0=metric["T0"],
            L0=metric["L0"],
            d_T0_over_r2_dr=derivative,
        )
        assert direct_li == pytest.approx(expected_li, rel=2e-13, abs=2e-13)
        assert mp == pytest.approx(expected_li, rel=3e-13, abs=3e-13)
    else:
        derivative = fp / (1.0j * k) * (expected_li + radius * derivative_li) + f / (
            1.0j * k
        ) * (2.0 * derivative_li + radius * second_derivative_li)
        mp = martel_poisson_odd_master_from_rw_metric(
            ell=ell,
            k=k,
            mass=background.M,
            r=radius,
            Bt=metric["Bt"],
            B1=metric["B1"],
            dBt_dr=derivative,
        )
        expected_mp = 2.0j * expected_li / k
        assert -background.f(radius) * metric["B1"] / radius == pytest.approx(
            expected_li,
            rel=2e-13,
            abs=2e-13,
        )
        assert mp == pytest.approx(expected_mp, rel=3e-13, abs=3e-13)


def test_production_odd_angular_assembly_is_negative_mp_vector_harmonic() -> None:
    ell = 4
    m = -2
    theta = 0.83
    phi = 0.27
    y, gradient = sph_harm_y(ell, m, theta, phi, diff_n=1)
    production = _harmonic_component_jets(
        ell,
        m,
        theta,
        phi,
        Sector.ODD,
    )
    li_theta = 1.0j * m * complex(y) / math.sin(theta)
    li_phi = -math.sin(theta) * complex(gradient[0])
    assert production["Bt_theta"][0] == pytest.approx(li_theta)
    assert production["Bt_phi"][0] == pytest.approx(li_phi)
    # MP Eq. (3.2): X_A=(-csc(theta) d_phi Y, +sin(theta) d_theta Y).
    mp_x_theta = -li_theta
    mp_x_phi = -li_phi
    assert production["B1_theta"][0] == pytest.approx(-mp_x_theta)
    assert production["B1_phi"][0] == pytest.approx(-mp_x_phi)


def test_mp_flux_records_peak_vs_rms_factor_of_two() -> None:
    mode = MartelPoissonMasterMode(
        ell=2,
        m=2,
        psi_even=2.0 + 1.0j,
        psi_odd=-0.5j,
    )
    peak = monochromatic_martel_poisson_flux(
        [mode],
        k=0.4,
        boundary="future_null_infinity",
        amplitude_convention="real_field_peak",
    )
    rms = monochromatic_martel_poisson_flux(
        [mode],
        k=0.4,
        boundary="future_null_infinity",
        amplitude_convention="complex_rms",
    )
    expected_peak = (
        0.5
        * sigma_l(2)
        * 0.4**2
        * (abs(mode.psi_even) ** 2 + abs(mode.psi_odd) ** 2)
        / (64.0 * math.pi)
    )
    assert peak.value == pytest.approx(expected_peak)
    assert rms.value == pytest.approx(2.0 * peak.value)
    assert peak.time_average_factor == 0.5


def test_project_psi4_helper_is_fixed_by_direct_flat_oracle() -> None:
    k = 2.0
    z = 0.37
    plus = (0.7 - 0.2j) * np.exp(1.0j * k * z)
    cross = (-0.1 + 0.4j) * np.exp(1.0j * k * z)
    direct = direct_cartesian_tt_strict_np_weyl(
        k=k,
        z=z,
        A_plus=0.7 - 0.2j,
        A_cross=-0.1 + 0.4j,
    )
    converted = outgoing_strain_to_project_strict_np_psi4(
        k=k,
        h_plus=plus,
        h_cross=cross,
    )
    assert converted == pytest.approx(direct["Psi4"], rel=2e-15, abs=2e-15)


def test_complex_route_comparisons_preserve_phase_and_independence() -> None:
    comparison = compare_complex_routes(
        1.0 + 0.0j,
        np.exp(0.2j),
        reference_route="MP",
        candidate_route="metric/Psi4",
        genuinely_independent=False,
        independence_provenance="shared project metric reconstruction",
        phase_amplitude_floor=1.0e-12,
        convention=PROJECT_OUTGOING_PSI4_CONVENTION,
    )
    assert comparison.phase_difference == pytest.approx(0.2)
    assert comparison.genuinely_independent is False
    pairs = pairwise_route_comparisons(
        {"MP": 1.0j, "metric/Psi4": 1.0j, "BHPT": 1.0j},
        independence={
            ("MP", "metric/Psi4"): False,
            ("MP", "BHPT"): True,
            ("metric/Psi4", "BHPT"): True,
        },
        independence_provenance={
            ("MP", "metric/Psi4"): "shared project master normalization",
            ("MP", "BHPT"): "external BHPT source and algorithm",
            ("metric/Psi4", "BHPT"): "external BHPT source and algorithm",
        },
        phase_amplitude_floor=1.0e-12,
        convention=PROJECT_OUTGOING_PSI4_CONVENTION,
    )
    assert len(pairs) == 3
    assert sum(item.genuinely_independent for item in pairs) == 2


def test_complex_route_comparison_fails_closed_on_bool_and_phase_floor() -> None:
    with pytest.raises(TypeError, match="exact bool"):
        compare_complex_routes(
            1.0,
            1.0,
            reference_route="A",
            candidate_route="B",
            genuinely_independent="false",  # type: ignore[arg-type]
            independence_provenance="fixture",
            phase_amplitude_floor=1.0e-12,
            convention="fixture",
        )
    comparison = compare_complex_routes(
        1.0e-30,
        1.0e-30j,
        reference_route="A",
        candidate_route="B",
        genuinely_independent=False,
        independence_provenance="shared fixture",
        phase_amplitude_floor=1.0e-20,
        convention="fixture",
    )
    assert comparison.phase_resolved is False
    assert comparison.phase_difference is None
    assert comparison.relative_difference is None


def test_pairwise_route_inventory_rejects_reverse_conflict_and_extra_pair() -> None:
    routes = {"A": 1.0j, "B": 1.0j}
    with pytest.raises(ValueError, match="duplicate/conflicting"):
        pairwise_route_comparisons(
            routes,
            independence={("A", "B"): True, ("B", "A"): False},
            independence_provenance={("A", "B"): "external"},
            phase_amplitude_floor=1.0e-12,
            convention="fixture",
        )
    with pytest.raises(ValueError, match="invalid or extra"):
        pairwise_route_comparisons(
            routes,
            independence={("A", "C"): True},
            independence_provenance={("A", "B"): "external"},
            phase_amplitude_floor=1.0e-12,
            convention="fixture",
        )


def test_mp_axis_and_implicit_conventions_fail_closed() -> None:
    with pytest.raises(ValueError, match="strictly"):
        martel_poisson_angular_operators(2, 2, 0.0, 0.0)
    with pytest.raises(ValueError, match="unsupported"):
        monochromatic_martel_poisson_flux(
            [MartelPoissonMasterMode(2, 2, 1.0j, 0.0j)],
            k=1.0,
            boundary="future_null_infinity",
            amplitude_convention="unspecified",  # type: ignore[arg-type]
        )


def test_mp_horizon_scale_and_duplicate_modes_fail_closed() -> None:
    mode = MartelPoissonMasterMode(2, 2, 1.0j, 0.0j)
    with pytest.raises(ValueError, match="explicit mass"):
        martel_poisson_strain(
            [mode],
            areal_scale=2.0,
            theta=0.7,
            phi=0.1,
            boundary="event_horizon",
        )
    with pytest.raises(ValueError, match="equal 2M"):
        martel_poisson_strain(
            [mode],
            areal_scale=3.0,
            theta=0.7,
            phi=0.1,
            boundary="event_horizon",
            mass=1.0,
        )
    with pytest.raises(ValueError, match="duplicate"):
        monochromatic_martel_poisson_flux(
            [mode, mode],
            k=1.0,
            boundary="future_null_infinity",
            amplitude_convention="complex_rms",
        )
    with pytest.raises(ValueError, match="equal 2M"):
        martel_poisson_strain(
            [mode],
            areal_scale=1.0e-13,
            theta=0.7,
            phi=0.1,
            boundary="event_horizon",
            mass=1.0e-14,
        )
