from __future__ import annotations
import numpy as np
import pytest

from schwgw.scattering.apparent import (
    ApparentPolarizationResult,
    apparent_polarization_acceleration_from_strict_np,
    apparent_polarizations_from_strict_np,
)
from schwgw.scattering.weyl import StrictNPScalars


def _strict_incident() -> StrictNPScalars:
    return StrictNPScalars(
        psi0=11.0 - 3.0j,
        psi1=2.0 + 5.0j,
        psi2=-7.0 + 13.0j,
        psi3=17.0 - 19.0j,
        psi4=23.0 + 29.0j,
        frame="incident",
    )


def test_apparent_accelerations_reproduce_li_hou_zhao_eq42_real_parts() -> None:
    strict = _strict_incident()

    hddot_x, hddot_y, hddot_b, hddot_l = (
        apparent_polarization_acceleration_from_strict_np(strict)
    )

    assert hddot_x.real == 0.5 * (strict.psi1.real + strict.psi3.real)
    assert hddot_y.real == 0.5 * (strict.psi1.imag - strict.psi3.imag)
    assert hddot_b.real == 0.5 * strict.psi2.real
    assert hddot_l.real == strict.psi2.real
    assert hddot_l == 2.0 * hddot_b


def test_apparent_strains_follow_exp_minus_ikt_and_remain_diagnostic() -> None:
    strict = _strict_incident()
    k = 2.5

    result = apparent_polarizations_from_strict_np(
        k,
        strict,
        diagnostics={"radial_solve_count": 4.0},
    )

    assert isinstance(result, ApparentPolarizationResult)
    assert result.physical_claim is False
    assert result.frame == "incident"
    assert result.diagnostics["radial_solve_count"] == 4.0
    assert result.h_longitudinal == 2.0 * result.h_b
    for strain, acceleration in (
        (result.h_x, result.hddot_x),
        (result.h_y, result.hddot_y),
        (result.h_b, result.hddot_b),
        (result.h_longitudinal, result.hddot_longitudinal),
    ):
        np.testing.assert_allclose(-(k**2) * strain, acceleration, rtol=1e-15)


def test_apparent_projection_rejects_wrong_frame_nonfinite_and_packaged_types() -> None:
    with pytest.raises(ValueError, match="incident frame"):
        apparent_polarizations_from_strict_np(
            1.0,
            StrictNPScalars(0, 0, 0, 0, 0, frame="kinnersley"),
        )
    with pytest.raises(ValueError, match="finite"):
        apparent_polarizations_from_strict_np(
            1.0,
            StrictNPScalars(0, np.nan, 0, 0, 0, frame="incident"),
        )
    with pytest.raises(TypeError, match="StrictNPScalars"):
        apparent_polarizations_from_strict_np(1.0, object())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="finite and positive"):
        apparent_polarizations_from_strict_np(0.0, _strict_incident())
