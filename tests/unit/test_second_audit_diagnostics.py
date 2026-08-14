from __future__ import annotations

import numpy as np
import pytest

from schwgw.numerics import extrapolate_r_out_ladder
from schwgw.scattering import compare_complex_phase


def test_r_out_extrapolation_recovers_quadratic_inverse_radius_limit() -> None:
    radii = np.asarray([100.0, 200.0, 400.0, 800.0])
    limit = np.asarray([1.2 - 0.7j, -0.3 + 0.4j])
    inverse = (1.0 / radii)[:, None]
    values = limit + (2.0 + 0.5j) * inverse + (-3.0 + 4.0j) * inverse**2

    result = extrapolate_r_out_ladder(radii, values)

    np.testing.assert_allclose(result.extrapolated, limit, rtol=1.0e-12, atol=1.0e-12)
    assert result.values.shape == values.shape
    assert result.adjacent_relative_change.shape == (3, 2)
    assert np.all(result.fit_residual < 1.0e-12)


@pytest.mark.parametrize(
    ("radii", "values"),
    [
        ([100.0, 200.0], np.ones(2)),
        ([100.0, 100.0, 200.0], np.ones(3)),
        ([100.0, 200.0, 300.0], np.ones((2, 2))),
    ],
)
def test_r_out_extrapolation_rejects_invalid_ladders(radii, values) -> None:
    with pytest.raises(ValueError):
        extrapolate_r_out_ladder(radii, values)


def test_phase_diagnostics_separate_raw_and_offset_removed_residuals() -> None:
    reference_phase = np.asarray(
        [[2.8, 3.0, -3.0, -2.7], [-2.9, -2.5, -2.1, -1.8]]
    )
    panel_offsets = np.asarray([0.4, -0.2])[:, None]
    reference = np.exp(1.0j * reference_phase)
    computed = np.exp(1.0j * (reference_phase + panel_offsets))

    diagnostics = compare_complex_phase(computed, reference, frequency_axis=1)

    np.testing.assert_allclose(diagnostics.panel_offsets, [0.4, -0.2], atol=1.0e-14)
    np.testing.assert_allclose(
        diagnostics.panel_offset_removed_residual, 0.0, atol=1.0e-14
    )
    assert diagnostics.raw_mae == pytest.approx(0.3)
    assert diagnostics.global_offset_removed_mae > 0.0
    assert np.all(np.diff(diagnostics.reference_unwrapped, axis=1) > 0.0)
