from __future__ import annotations

import numpy as np
import pytest

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.io.direct_tablei import DenseRadialSpanCache
from schwgw.numerics import BoundaryConfig, solve_radial_mode
from schwgw.perturbations import Sector, reconstruct_metric_mode
from schwgw.scattering.metric_curvature import (
    compute_direct_metric_apparent_polarizations,
    compute_direct_metric_polarization,
    compute_flat_metric_curvature_partial_wave,
    compute_metric_curvature_polarization,
    linearized_riemann_from_metric_jets,
    project_incident_electric_tidal,
    schwarzschild_metric_jet,
    strict_np_from_incident_riemann,
)
from schwgw.scattering.partial_wave import flat_no_lens_expected_polarization
from schwgw.scattering.tetrads import kinnersley_tetrad
from schwgw.scattering.weyl import weyl_mode_components
from schwgw.waves import IncidentPlaneGW


def _independent_riemann_lowered(
    metric: np.ndarray,
    first: np.ndarray,
    second: np.ndarray,
) -> np.ndarray:
    """Independent full-Riemann implementation for curved regression tests."""

    inverse = np.linalg.inv(metric)
    inverse_first = np.empty_like(first, dtype=np.complex128)
    for derivative in range(4):
        inverse_first[derivative] = -inverse @ first[derivative] @ inverse
    kernel = np.empty((4, 4, 4), dtype=np.complex128)
    kernel_first = np.empty((4, 4, 4, 4), dtype=np.complex128)
    for lower in range(4):
        for row in range(4):
            for column in range(4):
                kernel[lower, row, column] = (
                    first[row, column, lower]
                    + first[column, row, lower]
                    - first[lower, row, column]
                )
                for derivative in range(4):
                    kernel_first[derivative, lower, row, column] = (
                        second[derivative, row, column, lower]
                        + second[derivative, column, row, lower]
                        - second[derivative, lower, row, column]
                    )
    connection = 0.5 * np.einsum("al,lmn->amn", inverse, kernel)
    connection_first = 0.5 * (
        np.einsum("qal,lmn->qamn", inverse_first, kernel)
        + np.einsum("al,qlmn->qamn", inverse, kernel_first)
    )
    riemann_up = np.empty((4, 4, 4, 4), dtype=np.complex128)
    for upper in range(4):
        for lower in range(4):
            for first_index in range(4):
                for second_index in range(4):
                    riemann_up[upper, lower, first_index, second_index] = (
                        connection_first[
                            first_index, upper, second_index, lower
                        ]
                        - connection_first[
                            second_index, upper, first_index, lower
                        ]
                        + np.dot(
                            connection[upper, first_index, :],
                            connection[:, second_index, lower],
                        )
                        - np.dot(
                            connection[upper, second_index, :],
                            connection[:, first_index, lower],
                        )
                    )
    return np.einsum("ae,ebcd->abcd", metric, riemann_up)


def test_linearized_riemann_recovers_flat_cartesian_tt_tidal_tensor() -> None:
    k = 0.7
    plus = 1.2 - 0.3j
    cross = 0.4 + 0.2j
    background = np.diag((-1.0, 1.0, 1.0, 1.0))
    perturbation = np.zeros((4, 4), dtype=np.complex128)
    perturbation[1, 1] = plus
    perturbation[2, 2] = -plus
    perturbation[1, 2] = perturbation[2, 1] = cross
    wave_covector = np.asarray((-k, 0.0, 0.0, k), dtype=np.complex128)
    first = 1.0j * np.einsum("a,ij->aij", wave_covector, perturbation)
    second = -np.einsum(
        "a,b,ij->abij", wave_covector, wave_covector, perturbation
    )

    riemann = linearized_riemann_from_metric_jets(
        background,
        np.zeros((4, 4, 4)),
        np.zeros((4, 4, 4, 4)),
        perturbation,
        first,
        second,
    )

    np.testing.assert_allclose(riemann[0, 1, 0, 1], 0.5 * k**2 * plus)
    np.testing.assert_allclose(riemann[0, 1, 0, 2], 0.5 * k**2 * cross)
    np.testing.assert_allclose(riemann, -riemann.swapaxes(0, 1), atol=1.0e-15)
    np.testing.assert_allclose(riemann, -riemann.swapaxes(2, 3), atol=1.0e-15)
    np.testing.assert_allclose(
        riemann,
        riemann.transpose(2, 3, 0, 1),
        atol=1.0e-15,
    )


def test_observer_frame_switch_exposes_li_literal_lapse_difference() -> None:
    radius = 30.0
    polar = 0.7
    riemann = np.zeros((4, 4, 4, 4), dtype=np.complex128)
    riemann[0, 2, 0, 2] = 1.0 + 0.0j

    static = project_incident_electric_tidal(
        riemann,
        M=1.0,
        r=radius,
        theta=polar,
        phi=0.0,
        observer_frame="static_orthonormal",
    )
    literal = project_incident_electric_tidal(
        riemann,
        M=1.0,
        r=radius,
        theta=polar,
        phi=0.0,
        observer_frame="li_literal_cartesian",
    )

    lapse = 1.0 - 2.0 / radius
    assert static.E_xx / literal.E_xx == pytest.approx(1.0 / lapse)
    with pytest.raises(ValueError, match="observer_frame"):
        project_incident_electric_tidal(
            riemann,
            M=1.0,
            r=radius,
            theta=polar,
            phi=0.0,
            observer_frame="unspecified",  # type: ignore[arg-type]
        )


def test_positive_negative_frequency_pair_reconstructs_real_tidal_tensor() -> None:
    """The explicit ``(+k,-k)`` pair is real without an NP completion.

    For the frozen ``exp(-ikt)`` convention the negative-frequency metric jet
    is the complex conjugate of the positive-frequency jet at ``t=0``.
    Because the background and the directional Riemann operator are real and
    linear, summing that pair before or after curvature evaluation must agree
    exactly up to floating-point roundoff and must leave no imaginary field.
    """

    k = 0.9
    background = np.diag((-1.0, 1.0, 1.0, 1.0))
    positive = np.zeros((4, 4), dtype=np.complex128)
    positive[1, 1] = 0.9 + 1.1j
    positive[2, 2] = -positive[1, 1]
    positive[1, 2] = positive[2, 1] = 0.4 + 0.6j
    covector = np.asarray((-k, 0.0, 0.0, k), dtype=np.complex128)
    positive_first = 1.0j * np.einsum("a,ij->aij", covector, positive)
    positive_second = -np.einsum(
        "a,b,ij->abij", covector, covector, positive
    )
    positive_riemann = linearized_riemann_from_metric_jets(
        background,
        np.zeros((4, 4, 4)),
        np.zeros((4, 4, 4, 4)),
        positive,
        positive_first,
        positive_second,
    )

    real_pair_riemann = linearized_riemann_from_metric_jets(
        background,
        np.zeros((4, 4, 4)),
        np.zeros((4, 4, 4, 4)),
        positive + positive.conjugate(),
        positive_first + positive_first.conjugate(),
        positive_second + positive_second.conjugate(),
    )

    np.testing.assert_allclose(
        real_pair_riemann,
        positive_riemann + positive_riemann.conjugate(),
        rtol=0.0,
        atol=2.0e-15,
    )
    np.testing.assert_allclose(real_pair_riemann.imag, 0.0, rtol=0.0, atol=0.0)


def test_direct_metric_bridge_zero_source_uses_no_radial_solver() -> None:
    def forbidden(*args: object, **kwargs: object) -> object:
        raise AssertionError("zero source must not launch a radial solve")

    result = compute_metric_curvature_polarization(
        background=SchwarzschildBackground(M=1.0),
        k=0.5,
        r=20.0,
        theta=0.4,
        phi=0.3,
        A_plus=0.0,
        A_cross=0.0,
        lmax=4,
        radial_solver=forbidden,
    )

    assert result.polarization.h_plus == 0.0j
    assert result.polarization.h_cross == 0.0j
    assert result.polarization.diagnostics["radial_solve_count"] == 0.0
    assert result.polarization.diagnostics["observable_bridge_validated"] == 1.0


def test_flat_metric_partial_waves_recover_incident_plane_wave_without_np_completion() -> None:
    k = 0.5
    radius = 20.0
    theta = 1.0
    A_plus = 1.0 + 0.0j
    A_cross = 0.0 + 0.2j
    result = compute_flat_metric_curvature_partial_wave(
        k=k,
        r=radius,
        theta=theta,
        phi=0.3,
        A_plus=A_plus,
        A_cross=A_cross,
        lmax=30,
    )
    expected_plus, expected_cross = flat_no_lens_expected_polarization(
        k=k,
        r=radius,
        theta=theta,
        A_plus=A_plus,
        A_cross=A_cross,
    )

    np.testing.assert_allclose(
        result.polarization.h_plus,
        expected_plus,
        rtol=3.0e-9,
        atol=1.0e-10,
    )
    np.testing.assert_allclose(
        result.polarization.h_cross,
        expected_cross,
        rtol=4.0e-9,
        atol=1.0e-10,
    )
    strict_np = strict_np_from_incident_riemann(
        result.riemann,
        M=0.0,
        r=radius,
        theta=theta,
        phi=0.3,
    )
    lower = np.asarray(
        [strict_np.psi0, strict_np.psi1, strict_np.psi2, strict_np.psi3]
    )
    assert np.max(np.abs(lower)) < 2.0e-10


def test_direct_metric_bridge_preserves_reflection_plane_polarization_parity() -> None:
    """Pure plus/cross columns remain diagonal without an NP completion."""

    common = {
        "k": 0.5,
        "r": 20.0,
        "theta": 0.7,
        "phi": 0.0,
        "lmax": 30,
    }
    plus = compute_flat_metric_curvature_partial_wave(
        **common,
        A_plus=0.9 + 1.1j,
        A_cross=0.0j,
    ).polarization
    cross = compute_flat_metric_curvature_partial_wave(
        **common,
        A_plus=0.0j,
        A_cross=0.4 + 0.6j,
    ).polarization

    assert abs(plus.h_cross) < 2.0e-10
    assert abs(cross.h_plus) < 2.0e-10
    assert abs(plus.h_plus) > 0.1
    assert abs(cross.h_cross) > 0.1


def test_incident_frame_x_reflection_has_the_exact_m_plus_minus_2_parities() -> None:
    """The x-z renderer may mirror only with the tensor/vector parities."""

    radius = 20.0
    cache = DenseRadialSpanCache(lower=19.99, anchor=radius, upper=20.01)
    common = {
        "background": SchwarzschildBackground(M=1.0),
        "k": 0.5,
        "r": radius,
        "theta": 0.7,
        "A_plus": 0.9 + 1.1j,
        "A_cross": 0.4 + 0.6j,
        "lmax": 4,
        "boundary_config": BoundaryConfig(
            r_out=100.0,
            rtol=1.0e-11,
            atol=1.0e-13,
        ),
        "radial_solver": cache,
    }
    physical_zero = compute_direct_metric_polarization(**common, phi=0.0)
    physical_pi = compute_direct_metric_polarization(**common, phi=np.pi)
    apparent_zero = compute_direct_metric_apparent_polarizations(**common, phi=0.0)
    apparent_pi = compute_direct_metric_apparent_polarizations(**common, phi=np.pi)

    np.testing.assert_allclose(
        (physical_pi.h_plus, physical_pi.h_cross),
        (physical_zero.h_plus, physical_zero.h_cross),
        rtol=0.0,
        atol=2.0e-14,
    )
    np.testing.assert_allclose(
        (apparent_pi.h_b, apparent_pi.h_longitudinal),
        (apparent_zero.h_b, apparent_zero.h_longitudinal),
        rtol=0.0,
        atol=2.0e-14,
    )
    np.testing.assert_allclose(
        (apparent_pi.h_x, apparent_pi.h_y),
        (-apparent_zero.h_x, -apparent_zero.h_y),
        rtol=0.0,
        atol=2.0e-14,
    )


def test_direct_bridge_recovers_tablei_axis_limit_in_flat_space() -> None:
    """The Table-I ``(x,z)=(0,30)M`` axis regularization has the right limit."""

    k = 0.5
    radius = 30.0
    A_plus = 0.9 + 1.1j
    A_cross = 0.4 + 0.6j
    result = compute_flat_metric_curvature_partial_wave(
        k=k,
        r=radius,
        theta=0.0,
        phi=0.0,
        A_plus=A_plus,
        A_cross=A_cross,
        lmax=45,
        axis_regularization=1.0e-6,
    ).polarization
    expected_plus, expected_cross = flat_no_lens_expected_polarization(
        k=k,
        r=radius,
        theta=0.0,
        A_plus=A_plus,
        A_cross=A_cross,
    )

    np.testing.assert_allclose(
        result.h_plus,
        expected_plus,
        rtol=8.0e-12,
        atol=1.0e-12,
    )
    np.testing.assert_allclose(
        result.h_cross,
        expected_cross,
        rtol=8.0e-12,
        atol=1.0e-12,
    )


def test_curved_direct_bridge_radial_stencil_is_converged() -> None:
    """The ODE jet plus coefficient stencil is stable under step halving."""

    radius = 20.0
    coarse_step = 4.0e-3 * radius
    cache = DenseRadialSpanCache(
        lower=radius - 2.0 * coarse_step,
        anchor=radius,
        upper=radius + 2.0 * coarse_step,
    )
    common = {
        "background": SchwarzschildBackground(M=1.0),
        "k": 0.5,
        "r": radius,
        "theta": 0.7,
        "phi": 0.0,
        "A_plus": 0.9 + 1.1j,
        "A_cross": 0.4 + 0.6j,
        "lmax": 12,
        "boundary_config": BoundaryConfig(
            r_out=100.0,
            rtol=1.0e-11,
            atol=1.0e-13,
        ),
        "radial_solver": cache,
    }
    coarse = compute_metric_curvature_polarization(
        **common,
        radial_step_fraction=4.0e-3,
    ).polarization
    production = compute_metric_curvature_polarization(
        **common,
        radial_step_fraction=2.0e-3,
    ).polarization
    fine = compute_metric_curvature_polarization(
        **common,
        radial_step_fraction=1.0e-3,
    ).polarization

    def relative(left: complex, right: complex) -> float:
        return abs(left - right) / max(1.0, abs(left), abs(right))

    assert max(
        relative(coarse.h_plus, production.h_plus),
        relative(coarse.h_cross, production.h_cross),
    ) < 2.0e-8
    assert max(
        relative(production.h_plus, fine.h_plus),
        relative(production.h_cross, fine.h_cross),
    ) < 1.0e-8
    assert cache.metadata()["unique_solution_count"] == 22


def test_metric_curvature_jet_queries_the_ode_solution_only_at_the_anchor() -> None:
    """Curvature derivatives must not finite-difference dense ODE interpolation."""

    radius = 20.0

    class AnchorOnlySolution:
        A_in = 1.0 + 0.0j
        diagnostics = None

        def psi_at(self, query_radius: float) -> complex:
            assert query_radius == radius
            return 0.7 - 0.2j

        def dpsi_dr_at(self, query_radius: float) -> complex:
            assert query_radius == radius
            return 0.03 + 0.04j

    calls: list[tuple[Sector, int]] = []

    def anchor_only_solver(
        sector: Sector,
        ell: int,
        k: float,
        background: SchwarzschildBackground,
        boundary: BoundaryConfig | None,
    ) -> AnchorOnlySolution:
        del k, background, boundary
        calls.append((sector, ell))
        return AnchorOnlySolution()

    result = compute_metric_curvature_polarization(
        background=SchwarzschildBackground(M=1.0),
        k=0.5,
        r=radius,
        theta=0.7,
        phi=0.0,
        A_plus=0.9 + 1.1j,
        A_cross=0.4 + 0.6j,
        lmax=2,
        radial_solver=anchor_only_solver,
    )

    assert calls == [(Sector.ODD, 2), (Sector.EVEN, 2)]
    assert result.polarization.diagnostics["radial_ode_jet"] == 1.0
    assert np.isfinite(result.polarization.h_plus)
    assert np.isfinite(result.polarization.h_cross)


def test_direct_production_adapters_preserve_zero_source_contract() -> None:
    def forbidden(*args: object, **kwargs: object) -> object:
        raise AssertionError("zero source must not launch a radial solve")

    kwargs = {
        "background": SchwarzschildBackground(M=1.0),
        "k": 0.5,
        "r": 20.0,
        "theta": 0.0,
        "phi": 0.0,
        "A_plus": 0.0j,
        "A_cross": 0.0j,
        "lmax": 4,
        "radial_solver": forbidden,
    }
    physical = compute_direct_metric_polarization(**kwargs)
    apparent = compute_direct_metric_apparent_polarizations(**kwargs)

    assert physical.h_plus == physical.h_cross == 0.0j
    assert physical.diagnostics["observable_bridge_validated"] == 1.0
    assert apparent.h_x == apparent.h_y == 0.0j
    assert apparent.h_b == apparent.h_longitudinal == 0.0j
    assert apparent.physical_claim is False
    assert apparent.diagnostics["strict_np_direct_riemann_contraction"] == 1.0


def test_direct_metric_riemann_matches_independent_psi4_formula() -> None:
    background = SchwarzschildBackground(M=1.0)
    config = BoundaryConfig(
        r_out=100.0,
        rtol=1.0e-11,
        atol=1.0e-13,
        required_eval_radius=20.0,
    )
    k = 0.5
    radius = 20.0
    theta = 0.4
    phi = 0.3
    A_plus = 1.0 + 0.0j
    A_cross = 0.0 + 0.2j
    direct = compute_metric_curvature_polarization(
        background=background,
        k=k,
        r=radius,
        theta=theta,
        phi=phi,
        A_plus=A_plus,
        A_cross=A_cross,
        lmax=2,
        boundary_config=config,
        radial_step_fraction=3.0e-4,
    )
    tetrad = kinnersley_tetrad(background, radius, theta).legs
    direct_psi4 = -np.einsum(
        "abcd,a,b,c,d->",
        direct.riemann,
        tetrad["n"],
        tetrad["mbar"],
        tetrad["n"],
        tetrad["mbar"],
    )

    wave = IncidentPlaneGW(k, A_plus, A_cross)
    formula_psi4 = 0.0j
    for sector in (Sector.ODD, Sector.EVEN):
        solution = solve_radial_mode(sector, 2, k, background, config)
        for m in (-2, 2):
            coefficient = (
                wave.c_lm_odd(2, m)
                if sector is Sector.ODD
                else wave.c_lm_even(2, m)
            )
            scale = coefficient / solution.A_in
            metric = reconstruct_metric_mode(
                sector,
                2,
                k,
                radius,
                scale * solution.psi_at(radius),
                scale * solution.dpsi_dr_at(radius),
                background,
            )
            formula_psi4 += weyl_mode_components(
                sector,
                2,
                m,
                k,
                radius,
                theta,
                phi,
                metric,
                background,
            ).components["Psi4"]

    np.testing.assert_allclose(direct_psi4, formula_psi4, rtol=3.0e-5, atol=1.0e-10)
    first_bianchi = (
        direct.riemann
        + direct.riemann.transpose(0, 2, 3, 1)
        + direct.riemann.transpose(0, 3, 1, 2)
    )
    np.testing.assert_allclose(first_bianchi, 0.0, rtol=0.0, atol=2.0e-13)

    background_metric, background_first, background_second = (
        schwarzschild_metric_jet(M=1.0, r=radius, theta=theta)
    )
    background_riemann = _independent_riemann_lowered(
        background_metric.astype(np.complex128),
        background_first.astype(np.complex128),
        background_second.astype(np.complex128),
    )
    inverse = np.linalg.inv(background_metric)
    delta_inverse = -inverse @ direct.metric_jet.value @ inverse
    linearized_ricci = np.einsum(
        "ac,abcd->bd", inverse, direct.riemann
    ) + np.einsum("ac,abcd->bd", delta_inverse, background_riemann)
    relative_ricci = np.max(np.abs(linearized_ricci)) / np.max(
        np.abs(direct.riemann)
    )
    assert relative_ricci < 2.0e-11
    assert direct.polarization.diagnostics["full_np_pseudoinverse_bridge"] == 0.0
    assert direct.polarization.diagnostics["metric_curvature_bridge_validated"] == 1.0
