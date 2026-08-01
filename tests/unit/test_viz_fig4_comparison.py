from __future__ import annotations

import numpy as np
import pytest

from schwgw.viz.fig4_comparison import (
    Fig4ComparisonError,
    add_incident_plane_wave,
    asymptotic_total_polarizations,
    render_fig4_exact_asymptotic_comparison,
)


def test_add_incident_plane_wave_adds_eq46_without_reserializing_fields() -> None:
    theta = np.array([0.0, 0.4, np.pi])
    scattered_plus = np.array([1.0j, 2.0j, 3.0j])
    scattered_cross = np.array([0.5, 1.0, 1.5], dtype=complex)
    A_plus = 0.9 + 1.1j
    A_cross = 0.4 + 0.6j
    h_plus, h_cross = add_incident_plane_wave(
        theta,
        scattered_plus=scattered_plus,
        scattered_cross=scattered_cross,
        k=0.5,
        r=60.0,
        A_plus=A_plus,
        A_cross=A_cross,
    )
    phase = np.exp(1j * 0.5 * 60.0 * np.cos(theta))
    np.testing.assert_allclose(h_plus, scattered_plus + A_plus * phase)
    np.testing.assert_allclose(h_cross, scattered_cross + A_cross * phase)


def test_asymptotic_total_polarizations_reduces_to_incident_wave_for_zero_matrix() -> None:
    theta = np.array([0.0, 0.4, np.pi])
    A_plus = 0.9 + 1.1j
    A_cross = 0.4 + 0.6j
    h_plus, h_cross = asymptotic_total_polarizations(
        theta,
        k=0.5,
        r=60.0,
        M=1.0,
        M22=np.zeros(3, dtype=complex),
        M12=np.zeros(3, dtype=complex),
        A_plus=A_plus,
        A_cross=A_cross,
    )
    phase = np.exp(1j * 0.5 * 60.0 * np.cos(theta))
    np.testing.assert_allclose(h_plus, A_plus * phase, rtol=2e-15, atol=2e-15)
    np.testing.assert_allclose(h_cross, A_cross * phase, rtol=2e-15, atol=2e-15)


def test_asymptotic_total_polarizations_validates_matrix_shape_and_radius() -> None:
    with pytest.raises(Fig4ComparisonError, match="match theta"):
        asymptotic_total_polarizations(
            [0.2, 0.4],
            k=1.0,
            r=60.0,
            M=1.0,
            M22=[0.0j],
            M12=[0.0j],
            A_plus=1.0j,
            A_cross=1.0,
        )


def test_renderer_rejects_invalid_precomputed_asymptotic_shape(tmp_path) -> None:
    source = tmp_path / "asymptotic.npz"
    source.write_bytes(b"precomputed")
    values = np.zeros((4, 1024), dtype=np.complex128)
    with pytest.raises(Fig4ComparisonError, match=r"shape \(4, 1025\)"):
        render_fig4_exact_asymptotic_comparison(
            [tmp_path / f"exact_{index}.npz" for index in range(4)],
            asymptotic_plus=values,
            asymptotic_cross=values,
            asymptotic_source=source,
            output_dir=tmp_path / "out",
        )


def test_renderer_rejects_finite_forward_axis_in_precomputed_fields(tmp_path) -> None:
    source = tmp_path / "asymptotic.npz"
    source.write_bytes(b"precomputed")
    values = np.ones((4, 1025), dtype=np.complex128)
    with pytest.raises(Fig4ComparisonError, match="NaN exactly at theta=0"):
        render_fig4_exact_asymptotic_comparison(
            [tmp_path / f"exact_{index}.npz" for index in range(4)],
            asymptotic_plus=values,
            asymptotic_cross=values,
            asymptotic_source=source,
            output_dir=tmp_path / "out",
        )
    with pytest.raises(Fig4ComparisonError, match="horizon"):
        asymptotic_total_polarizations(
            [0.2],
            k=1.0,
            r=2.0,
            M=1.0,
            M22=[0.0j],
            M12=[0.0j],
            A_plus=1.0j,
            A_cross=1.0,
        )
