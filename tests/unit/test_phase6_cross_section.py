from __future__ import annotations

import math

import numpy as np
import pytest

from schwgw.validation.phase6_cross_section import (
    first_spin2_glory_ring,
    geometric_optics_absorption_cross_section,
    spin2_absorption_cross_section,
    spin2_backward_glory_cross_section,
    spin2_low_frequency_cross_section,
)


def test_low_frequency_spin2_cross_section_has_exact_backward_value() -> None:
    assert spin2_low_frequency_cross_section(math.pi, mass=2.0) == pytest.approx(4.0)
    theta = np.array([0.2, 0.7, 1.4, math.pi])
    expected = (np.cos(theta / 2.0) ** 8 + np.sin(theta / 2.0) ** 8) / np.sin(
        theta / 2.0
    ) ** 4
    np.testing.assert_allclose(spin2_low_frequency_cross_section(theta), expected)


def test_absorption_uses_direct_parity_flux_fractions() -> None:
    ell = np.arange(2, 6)
    even = np.array([0.8, 0.4, 0.1, 0.0])
    odd = np.array([0.6, 0.2, 0.05, 0.0])
    expected = math.pi / (2.0 * 0.5**2) * np.sum((2 * ell + 1) * (even + odd))
    assert spin2_absorption_cross_section(ell, even, odd, k=0.5) == pytest.approx(
        expected
    )
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        spin2_absorption_cross_section(ell, even + 1.0, odd, k=0.5)


def test_geometric_optics_limit_is_27_pi_m_squared() -> None:
    assert geometric_optics_absorption_cross_section(mass=3.0) == pytest.approx(
        27.0 * math.pi * 9.0
    )


def test_spin2_glory_has_backward_zero_and_inverse_frequency_ring_scale() -> None:
    assert spin2_backward_glory_cross_section(math.pi, kM=4.0) == pytest.approx(
        0.0,
        abs=1e-28,
    )
    ring4 = first_spin2_glory_ring(kM=4.0)
    ring8 = first_spin2_glory_ring(kM=8.0)
    assert ring4.theta_peak < math.pi
    assert ring4.peak_cross_section_over_M2 > 0.0
    assert math.sin(ring4.backward_offset) * 4.0 == pytest.approx(
        math.sin(ring8.backward_offset) * 8.0,
        rel=2e-14,
    )
    assert ring4.backward_offset / ring8.backward_offset == pytest.approx(2.0, rel=0.01)
    # The exact angular width contains arcsin rather than the strict
    # high-frequency linearization; kM=4 retains a small, expected curvature.
    assert ring4.fwhm / ring8.fwhm == pytest.approx(2.0, rel=0.03)


def test_glory_fwhm_rejects_clipped_low_frequency_lobe() -> None:
    with pytest.raises(ValueError, match="high-frequency"):
        first_spin2_glory_ring(kM=0.5)
    with pytest.raises(ValueError, match="FWHM"):
        first_spin2_glory_ring(kM=2.1)


def test_glory_formula_rejects_angles_outside_backward_window() -> None:
    with pytest.raises(ValueError, match="backward-glory"):
        spin2_backward_glory_cross_section(math.pi / 2.0, kM=4.0)
