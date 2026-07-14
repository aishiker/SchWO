from __future__ import annotations

from dataclasses import fields
from types import SimpleNamespace

import numpy as np
import pytest

import schwgw.scattering.transmission as transmission_module
from schwgw.scattering.transmission import (
    PointwiseAmplificationResult,
    compute_pointwise_amplification,
    flat_no_lens_baseline_at_point,
)


def _assert_complex_nan(values: np.ndarray) -> None:
    assert np.all(np.isnan(values.real))
    assert np.all(np.isnan(values.imag))


def test_no_lens_identity_ratios_are_one_on_valid_points() -> None:
    h_plus = np.array([1.0 + 0.5j, -2.0 + 1.0j])
    h_cross = np.array([0.25 - 0.75j, 1.5j])

    result = compute_pointwise_amplification(
        h_plus_lensed=h_plus,
        h_cross_lensed=h_cross,
        h_plus_unlensed=h_plus,
        h_cross_unlensed=h_cross,
        valid_lensed_mask=np.array([True, True]),
        A_plus=1.0 + 0.2j,
        A_cross=0.4 - 0.1j,
    )

    assert isinstance(result, PointwiseAmplificationResult)
    np.testing.assert_allclose(result.F_plus_complex, np.ones_like(h_plus))
    np.testing.assert_allclose(result.F_cross_complex, np.ones_like(h_cross))
    np.testing.assert_allclose(result.amplification_plus, 1.0)
    np.testing.assert_allclose(result.amplification_cross, 1.0)
    np.testing.assert_allclose(result.intensity_plus_ratio, 1.0)
    np.testing.assert_allclose(result.intensity_cross_ratio, 1.0)
    np.testing.assert_allclose(result.F_pol_norm, 1.0)
    np.testing.assert_allclose(result.I_pol_ratio, 1.0)
    assert result.valid_ratio_plus_mask.tolist() == [True, True]
    assert result.valid_ratio_cross_mask.tolist() == [True, True]
    assert result.valid_ratio_norm_mask.tolist() == [True, True]
    normalization = result.metadata["normalization"]
    assert normalization["kind"] == "pointwise_wave_optics_amplification"
    assert normalization["version"] == "m5a_t1_v1"
    assert normalization["baseline_api"] == "compute_flat_no_lens_polarization"


def test_complex_ratios_preserve_phase_and_derived_summaries() -> None:
    plus_unlensed = np.array([1.0 + 2.0j, -3.0 + 1.0j])
    cross_unlensed = np.array([2.0 - 0.5j, 1.0 + 1.0j])
    plus_factor = np.array([2.0j, -0.5 + 0.25j])
    cross_factor = np.array([1.5 - 0.5j, -1.0j])
    plus_lensed = plus_factor * plus_unlensed
    cross_lensed = cross_factor * cross_unlensed

    result = compute_pointwise_amplification(
        h_plus_lensed=plus_lensed,
        h_cross_lensed=cross_lensed,
        h_plus_unlensed=plus_unlensed,
        h_cross_unlensed=cross_unlensed,
        valid_lensed_mask=None,
        A_plus=1.0,
        A_cross=1.0,
    )

    np.testing.assert_allclose(result.F_plus_complex, plus_factor)
    np.testing.assert_allclose(result.F_cross_complex, cross_factor)
    np.testing.assert_allclose(result.amplification_plus, np.abs(plus_factor))
    np.testing.assert_allclose(result.amplification_cross, np.abs(cross_factor))
    np.testing.assert_allclose(result.intensity_plus_ratio, np.abs(plus_factor) ** 2)
    np.testing.assert_allclose(result.intensity_cross_ratio, np.abs(cross_factor) ** 2)
    h_norm_lensed = np.sqrt(np.abs(plus_lensed) ** 2 + np.abs(cross_lensed) ** 2)
    h_norm_unlensed = np.sqrt(np.abs(plus_unlensed) ** 2 + np.abs(cross_unlensed) ** 2)
    np.testing.assert_allclose(result.F_pol_norm, h_norm_lensed / h_norm_unlensed)
    np.testing.assert_allclose(
        result.I_pol_ratio,
        h_norm_lensed**2 / h_norm_unlensed**2,
    )


def test_pure_plus_masks_cross_ratio_without_masking_plus_or_norm() -> None:
    result = compute_pointwise_amplification(
        h_plus_lensed=np.array([2.0 + 0.0j]),
        h_cross_lensed=np.array([0.5 + 0.0j]),
        h_plus_unlensed=np.array([1.0 + 0.0j]),
        h_cross_unlensed=np.array([0.0 + 0.0j]),
        valid_lensed_mask=np.array([True]),
        A_plus=1.0,
        A_cross=0.0,
    )

    np.testing.assert_allclose(result.F_plus_complex, np.array([2.0 + 0.0j]))
    _assert_complex_nan(result.F_cross_complex)
    np.testing.assert_allclose(result.F_pol_norm, np.array([np.sqrt(4.25)]))
    assert result.valid_ratio_plus_mask.tolist() == [True]
    assert result.valid_ratio_cross_mask.tolist() == [False]
    assert result.valid_ratio_norm_mask.tolist() == [True]


def test_pure_cross_masks_plus_ratio_without_masking_cross_or_norm() -> None:
    result = compute_pointwise_amplification(
        h_plus_lensed=np.array([0.5 + 0.0j]),
        h_cross_lensed=np.array([3.0 + 0.0j]),
        h_plus_unlensed=np.array([0.0 + 0.0j]),
        h_cross_unlensed=np.array([1.5 + 0.0j]),
        valid_lensed_mask=np.array([True]),
        A_plus=0.0,
        A_cross=1.5,
    )

    _assert_complex_nan(result.F_plus_complex)
    np.testing.assert_allclose(result.F_cross_complex, np.array([2.0 + 0.0j]))
    np.testing.assert_allclose(result.F_pol_norm, np.array([np.sqrt(9.25) / 1.5]))
    assert result.valid_ratio_plus_mask.tolist() == [False]
    assert result.valid_ratio_cross_mask.tolist() == [True]
    assert result.valid_ratio_norm_mask.tolist() == [True]


def test_combined_norm_is_valid_if_either_polarization_denominator_is_valid() -> None:
    result = compute_pointwise_amplification(
        h_plus_lensed=np.array([0.0, 4.0, 0.0], dtype=complex),
        h_cross_lensed=np.array([6.0, 0.0, 0.0], dtype=complex),
        h_plus_unlensed=np.array([0.0, 2.0, 0.0], dtype=complex),
        h_cross_unlensed=np.array([3.0, 0.0, 0.0], dtype=complex),
        valid_lensed_mask=np.array([True, True, True]),
        A_plus=1.0,
        A_cross=1.0,
    )

    assert result.valid_ratio_plus_mask.tolist() == [False, True, False]
    assert result.valid_ratio_cross_mask.tolist() == [True, False, False]
    assert result.valid_ratio_norm_mask.tolist() == [True, True, False]
    np.testing.assert_allclose(result.F_pol_norm[:2], np.array([2.0, 2.0]))
    np.testing.assert_allclose(result.I_pol_ratio[:2], np.array([4.0, 4.0]))
    assert np.isnan(result.F_pol_norm[2])
    assert np.isnan(result.I_pol_ratio[2])


def test_zero_incident_amplitudes_make_all_ratios_invalid_and_nan() -> None:
    result = compute_pointwise_amplification(
        h_plus_lensed=np.array([0.0 + 0.0j]),
        h_cross_lensed=np.array([0.0 + 0.0j]),
        h_plus_unlensed=np.array([0.0 + 0.0j]),
        h_cross_unlensed=np.array([0.0 + 0.0j]),
        valid_lensed_mask=np.array([True]),
        A_plus=0.0,
        A_cross=0.0,
    )

    assert result.valid_ratio_plus_mask.tolist() == [False]
    assert result.valid_ratio_cross_mask.tolist() == [False]
    assert result.valid_ratio_norm_mask.tolist() == [False]
    _assert_complex_nan(result.F_plus_complex)
    _assert_complex_nan(result.F_cross_complex)
    assert np.isnan(result.F_pol_norm[0])
    assert np.isnan(result.I_pol_ratio[0])


def test_shape_mismatch_and_invalid_denominator_factors_raise_clear_errors() -> None:
    common = dict(
        h_plus_lensed=np.ones(2, dtype=complex),
        h_cross_lensed=np.ones(2, dtype=complex),
        h_plus_unlensed=np.ones(2, dtype=complex),
        h_cross_unlensed=np.ones(2, dtype=complex),
        valid_lensed_mask=np.array([True, True]),
        A_plus=1.0,
        A_cross=1.0,
    )

    with pytest.raises(ValueError, match="same shape"):
        compute_pointwise_amplification(
            **{**common, "h_cross_unlensed": np.ones((1, 2), dtype=complex)}
        )
    with pytest.raises(ValueError, match="valid_lensed_mask"):
        compute_pointwise_amplification(
            **{**common, "valid_lensed_mask": np.array([[True, True]])}
        )
    with pytest.raises(ValueError, match="denominator_atol_factor"):
        compute_pointwise_amplification(**{**common, "denominator_atol_factor": 0.0})
    with pytest.raises(ValueError, match="denominator_rtol_factor"):
        compute_pointwise_amplification(**{**common, "denominator_rtol_factor": -1.0})


def test_flat_no_lens_baseline_helper_uses_flat_api_and_not_radial_solver(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_flat_no_lens_polarization(**kwargs: object) -> SimpleNamespace:
        calls.append(dict(kwargs))
        return SimpleNamespace(h_plus=2.0 + 3.0j, h_cross=-1.0 + 0.5j)

    def forbidden_radial_solver(*args: object, **kwargs: object) -> object:
        raise AssertionError("flat baseline must not call solve_radial_mode")

    monkeypatch.setattr(
        transmission_module,
        "compute_flat_no_lens_polarization",
        fake_flat_no_lens_polarization,
    )
    monkeypatch.setattr(
        "schwgw.scattering.partial_wave.solve_radial_mode",
        forbidden_radial_solver,
    )

    baseline = flat_no_lens_baseline_at_point(
        k=0.5,
        r=20.0,
        theta=0.4,
        phi=0.3,
        A_plus=0.7 - 0.2j,
        A_cross=0.1 + 0.4j,
        lmax=6,
    )

    assert baseline == (2.0 + 3.0j, -1.0 + 0.5j)
    assert calls == [
        {
            "k": 0.5,
            "r": 20.0,
            "theta": 0.4,
            "phi": 0.3,
            "A_plus": 0.7 - 0.2j,
            "A_cross": 0.1 + 0.4j,
            "lmax": 6,
        }
    ]


def test_metadata_and_public_fields_avoid_bare_transmission_terminology() -> None:
    result = compute_pointwise_amplification(
        h_plus_lensed=np.array([1.0 + 0.0j]),
        h_cross_lensed=np.array([1.0 + 0.0j]),
        h_plus_unlensed=np.array([1.0 + 0.0j]),
        h_cross_unlensed=np.array([1.0 + 0.0j]),
        valid_lensed_mask=np.array([True]),
        A_plus=1.0,
        A_cross=1.0,
    )

    normalization = result.metadata["normalization"]
    assert normalization["excludes_radial_horizon_transmission"] is True
    assert normalization["no_schwarzschild_horizon_boundary_in_baseline"] is True
    assert normalization["no_tiny_M_baseline"] is True
    assert normalization["excludes_radial_horizon_transmission"] is True
    public_field_names = {field.name for field in fields(PointwiseAmplificationResult)}
    assert "transmission" not in public_field_names
