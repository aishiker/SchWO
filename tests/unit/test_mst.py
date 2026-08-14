from __future__ import annotations

import numpy as np
import pytest

from schwgw.scattering.mst import schwarzschild_mst_phase_factor


pytest.importorskip(
    "mpmath",
    reason="direct MST tests require the optional schw-gw-waveoptics[oracle] extra",
)


def test_mst_phase_factor_is_unitary_and_generates_parity_ratio() -> None:
    ell = 20
    k = 2.0
    result = schwarzschild_mst_phase_factor(
        ell,
        k=k,
        truncation=20,
        guard_terms=16,
        working_dps=50,
    )

    sigma = (ell - 1) * ell * (ell + 1) * (ell + 2)
    expected_ratio = (sigma + 12.0j * k) / (sigma - 12.0j * k)
    np.testing.assert_allclose(abs(result.odd), 1.0, rtol=0.0, atol=2.0e-15)
    np.testing.assert_allclose(abs(result.even), 1.0, rtol=0.0, atol=2.0e-15)
    np.testing.assert_allclose(
        result.even / result.odd,
        expected_ratio,
        rtol=2.0e-15,
        atol=2.0e-15,
    )
    assert result.recurrence_residual < 1.0e-35


def test_mst_truncation_is_converged_at_high_ell() -> None:
    compact = schwarzschild_mst_phase_factor(
        180,
        k=2.0,
        truncation=16,
        guard_terms=12,
        working_dps=50,
    )
    production = schwarzschild_mst_phase_factor(
        180,
        k=2.0,
        truncation=30,
        guard_terms=24,
        working_dps=70,
    )

    np.testing.assert_allclose(compact.odd, production.odd, rtol=0.0, atol=3.0e-14)
    np.testing.assert_allclose(
        compact.even,
        production.even,
        rtol=0.0,
        atol=3.0e-14,
    )
