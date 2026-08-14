from __future__ import annotations

import numpy as np
import pytest
from scipy.special import eval_jacobi, lpmv

from schwgw.scattering.asymptotic import (
    evaluate_reduced_legendre_series,
    matched_schwarzschild_phase_factors,
    outer_matching_phase_corrected,
    parity_scattering_series,
    poisson_sasaki_odd_phase_factor,
    reduce_legendre_series,
    reduce_truncated_legendre_series,
    scattering_matrix_cross_section,
    schwarzschild_even_from_odd,
)
def _direct(theta: np.ndarray, coefficients: np.ndarray) -> np.ndarray:
    x = np.cos(theta)
    values = np.zeros(theta.shape, dtype=np.complex128)
    for ell, coefficient in enumerate(coefficients, start=2):
        values += coefficient * lpmv(2, ell, x)
    return values


@pytest.mark.parametrize("order", [0, 1, 2])
def test_series_reduction_preserves_finite_associated_legendre_sum(order: int) -> None:
    coefficients = np.array(
        [0.3 + 0.2j, -0.1 + 0.7j, 0.5 - 0.4j, -0.25 - 0.1j],
        dtype=np.complex128,
    )
    # The reduced representation is deliberately singular at the forward
    # axis; keep this algebraic identity test outside that ill-conditioned
    # display region and test theta=0 rejection separately below.
    theta = np.linspace(0.2, np.pi, 41)

    reduced = reduce_legendre_series(coefficients, reduction_order=order)
    evaluated = evaluate_reduced_legendre_series(theta, reduced)

    np.testing.assert_allclose(
        evaluated,
        _direct(theta, coefficients),
        rtol=2e-12,
        atol=2e-12,
    )
    assert reduced.ell[-1] == 5 + order


def test_parity_series_uses_direct_phase_factors_and_fixed_parity_sign() -> None:
    even = np.array([1.0 + 0.0j, 0.2 + 0.3j])
    odd = np.array([-0.5 + 0.25j, 1.0 + 0.0j])

    series = parity_scattering_series(even, odd)

    ell = np.array([2.0, 3.0])
    sigma = (ell - 1.0) * ell * (ell + 1.0) * (ell + 2.0)
    prefactor = (2.0 * ell + 1.0) / (4.0 * np.pi * sigma)
    np.testing.assert_array_equal(series.ell, np.array([2, 3]))
    np.testing.assert_allclose(
        series.symmetric,
        prefactor * ((even - 1.0) + (odd - 1.0)),
    )
    np.testing.assert_allclose(
        series.antisymmetric,
        prefactor * ((even - 1.0) - (odd - 1.0)),
    )
    assert series.ell.flags.writeable is False
    assert series.symmetric.flags.writeable is False


def test_reduced_series_rejects_forward_axis_and_invalid_contracts() -> None:
    reduced = reduce_legendre_series([1.0 + 0.0j], reduction_order=1)
    with pytest.raises(ValueError, match="forward axis"):
        evaluate_reduced_legendre_series(0.0, reduced)
    with pytest.raises(ValueError, match="nonnegative"):
        reduce_legendre_series([1.0], reduction_order=-1)
    with pytest.raises(ValueError, match="same shape"):
        parity_scattering_series([1.0, 1.0], [1.0])
    with pytest.raises(ValueError, match="contiguous"):
        parity_scattering_series([1.0, 1.0], [1.0, 1.0], ell=[2, 4])


def test_truncated_reduction_consumes_exact_upper_edge() -> None:
    coefficients = np.array(
        [0.3 + 0.2j, -0.1 + 0.7j, 0.5 - 0.4j, 0.2 + 0.1j]
    )
    reduced = reduce_truncated_legendre_series(coefficients, reduction_order=1)

    expected = np.empty(3, dtype=np.complex128)
    for ell in range(2, 5):
        center = coefficients[ell - 2]
        lower = coefficients[ell - 3] if ell > 2 else 0.0j
        upper = coefficients[ell - 1]
        expected[ell - 2] = (
            center
            - (ell - 2) / (2 * ell - 1) * lower
            - (ell + 3) / (2 * ell + 3) * upper
        )
    np.testing.assert_allclose(reduced.coefficients, expected)
    np.testing.assert_array_equal(reduced.ell, np.array([2, 3, 4]))
    with pytest.raises(ValueError, match="upper edge"):
        reduce_truncated_legendre_series([1.0], reduction_order=1)
    with pytest.raises(ValueError, match="target_lmax"):
        reduce_truncated_legendre_series(
            coefficients, reduction_order=1, target_lmax=5
        )


def test_scattering_matrix_matches_direct_wigner_d_partial_wave_sum() -> None:
    # Choose phase factors so that the symmetric and antisymmetric Appendix-D
    # coefficients are both nonzero for the sole ell=2 term.
    series = parity_scattering_series(
        np.array([0.4 + 0.3j]),
        np.array([-0.2 + 0.1j]),
    )
    theta = np.array([0.2, 0.7, 1.4, np.pi])
    result = scattering_matrix_cross_section(
        theta,
        series,
        k=0.5,
        reduction_order=0,
    )

    sigma2 = 24.0
    cosine = np.cos(theta)
    d22 = np.cos(theta / 2.0) ** 4 * eval_jacobi(0, 0, 4, cosine)
    d2minus2 = np.sin(theta / 2.0) ** 4 * eval_jacobi(0, 0, 4, -cosine)
    operator_m22 = series.symmetric[0] * sigma2 * d22
    operator_m12 = series.antisymmetric[0] * sigma2 * d2minus2
    prefactor = np.pi / (0.5j)
    np.testing.assert_allclose(result.M22, prefactor * operator_m22, rtol=2e-12, atol=2e-12)
    np.testing.assert_allclose(result.M12, prefactor * operator_m12, rtol=2e-12, atol=2e-12)
    np.testing.assert_allclose(
        result.differential_cross_section,
        np.abs(result.M22) ** 2 + np.abs(result.M12) ** 2,
    )
    assert result.M22.flags.writeable is False


def test_scattering_matrix_masks_forward_axis_by_contract() -> None:
    series = parity_scattering_series([0.5 + 0.0j], [0.25 + 0.0j])
    with pytest.raises(ValueError, match=r"\(0, pi\]"):
        scattering_matrix_cross_section(
            np.array([0.0, 0.1]),
            series,
            k=1.0,
            reduction_order=2,
        )


def test_outer_phase_correction_and_parity_relation_are_exact() -> None:
    ell = np.arange(2, 9)
    phase = np.exp(1j * np.linspace(-0.4, 0.8, ell.size))
    corrected = outer_matching_phase_corrected(
        phase, ell, k=0.5, r_out=300.0
    )
    np.testing.assert_allclose(
        corrected,
        phase * np.exp(-1j * ell * (ell + 1) / 150.0),
        rtol=0.0,
        atol=2e-15,
    )
    even = schwarzschild_even_from_odd(corrected, ell, k=0.5)
    sigma = (ell - 1) * ell * (ell + 1) * (ell + 2)
    np.testing.assert_allclose(
        even / corrected,
        (sigma + 6j) / (sigma - 6j),
        rtol=0.0,
        atol=2e-15,
    )


def test_matched_phase_series_preserves_low_modes_and_closes_tail() -> None:
    raw_ell = np.arange(2, 61)
    k = 0.5
    tail = poisson_sasaki_odd_phase_factor(raw_ell, k=k)
    convention_offset = 0.13
    corrected_odd = tail * np.exp(1j * convention_offset)
    corrected_even = schwarzschild_even_from_odd(corrected_odd, raw_ell, k=k)
    finite_radius = np.exp(1j * raw_ell * (raw_ell + 1) / (k * 300.0))
    numerical_odd = corrected_odd * finite_radius
    numerical_even = corrected_even * finite_radius
    result = matched_schwarzschild_phase_factors(
        numerical_odd,
        numerical_even,
        raw_ell,
        k=k,
        r_out=300.0,
        output_lmax=100,
        overlap_ell=(20, 40),
    )
    np.testing.assert_allclose(result.odd[:19], corrected_odd[:19], atol=2e-15)
    expected_tail = poisson_sasaki_odd_phase_factor(
        np.arange(2, 101), k=k
    ) * np.exp(1j * convention_offset)
    np.testing.assert_allclose(result.odd[39:], expected_tail[39:], atol=3e-15)
    assert abs(result.tail_phase_offset - convention_offset) < 2e-15
    assert result.maximum_overlap_phase_residual < 2e-15


def test_poisson_sasaki_tail_reproduces_spin2_low_frequency_limit() -> None:
    k = 0.005
    ell = np.arange(2, 503)
    odd = poisson_sasaki_odd_phase_factor(ell, k=k)
    even = schwarzschild_even_from_odd(odd, ell, k=k)
    theta = np.linspace(0.2, np.pi, 120)
    result = scattering_matrix_cross_section(
        theta,
        parity_scattering_series(even, odd, ell=ell),
        k=k,
        reduction_order=2,
        target_lmax=500,
    )
    expected = np.cos(theta / 2.0) ** 8 / np.sin(theta / 2.0) ** 4
    expected += np.sin(theta / 2.0) ** 4
    np.testing.assert_allclose(
        result.differential_cross_section,
        expected,
        rtol=1.2e-4,
        atol=2.5e-5,
    )
