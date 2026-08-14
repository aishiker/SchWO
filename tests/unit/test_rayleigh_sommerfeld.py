from __future__ import annotations

import importlib

import numpy as np
import pytest

import schwgw.scattering.rayleigh_sommerfeld as rs_module
from schwgw.scattering.kirchhoff import compute_kirchhoff_figure_consistent
from schwgw.scattering.rayleigh_sommerfeld import (
    RayleighSommerfeldPhaseScreenResult,
    compute_rayleigh_sommerfeld_point_mass_phase_screen,
)


def _compute(*, kM: list[float], x: list[float], z: list[float]):
    return compute_rayleigh_sommerfeld_point_mass_phase_screen(
        kM_values=np.asarray(kM),
        transverse_x_over_M=np.asarray(x),
        propagation_z_over_M=np.asarray(z),
        dps=40,
    )


def test_rs_phase_screen_axis_reference_and_component_closure() -> None:
    result = _compute(kM=[0.1], x=[0.0], z=[30.0])

    assert isinstance(result, RayleighSommerfeldPhaseScreenResult)
    assert result.F_complex.shape == (1, 1)
    assert result.valid_mask.tolist() == [[True]]
    assert result.F_complex[0, 0] == pytest.approx(
        1.254042473446463 - 0.2687290331118868j,
        rel=2.0e-12,
        abs=2.0e-12,
    )
    np.testing.assert_allclose(
        result.F_complex,
        result.F_propagating + result.F_evanescent,
        rtol=0.0,
        atol=0.0,
    )
    assert result.metadata["baseline"]["comparison_only"] is True
    assert result.metadata["baseline"]["strong_field_core_resolved"] is False


def test_rs_phase_screen_is_radially_symmetric_in_transverse_coordinate() -> None:
    result = _compute(kM=[0.1], x=[-3.0, 3.0], z=[30.0, 30.0])
    np.testing.assert_allclose(
        result.F_complex[:, 0],
        result.F_complex[:, 1],
        rtol=0.0,
        atol=0.0,
    )


def test_rs_subtracted_propagating_tail_is_stable_at_long_wave_far_axis() -> None:
    result = compute_rayleigh_sommerfeld_point_mass_phase_screen(
        kM_values=np.asarray([10.0 ** (-2.5)]),
        transverse_x_over_M=np.asarray([32.54270698294439]),
        propagation_z_over_M=np.asarray([39.05124837953327]),
        dps=30,
    )
    assert result.F_complex[0, 0] == pytest.approx(
        1.0025611815464923 - 0.023065204932948426j,
        rel=2.0e-12,
        abs=2.0e-12,
    )


def test_rs_phase_screen_approaches_fresnel_at_large_distance() -> None:
    kM = np.asarray([0.1])
    eta = 0.5
    distances = np.asarray([30.0, 300.0])
    transverse = 2.0 * eta * np.sqrt(distances)
    result = compute_rayleigh_sommerfeld_point_mass_phase_screen(
        kM_values=kM,
        transverse_x_over_M=transverse,
        propagation_z_over_M=distances,
        dps=40,
    )
    fresnel = compute_kirchhoff_figure_consistent(
        kM_values=kM,
        r_over_M=distances,
        theta=np.arctan(transverse / distances),
        dps=50,
    ).F_complex[0]
    residual = np.abs(result.F_complex[0] / fresnel - 1.0)
    assert residual[1] < residual[0]
    assert residual[1] < 3.5e-3


def test_rs_long_wave_limit_moves_toward_unity_and_fresnel() -> None:
    kM = np.asarray([0.001, 0.1])
    result = compute_rayleigh_sommerfeld_point_mass_phase_screen(
        kM_values=kM,
        transverse_x_over_M=np.asarray([0.0]),
        propagation_z_over_M=np.asarray([30.0]),
        dps=40,
    )
    fresnel = compute_kirchhoff_figure_consistent(
        kM_values=kM,
        r_over_M=np.asarray([30.0]),
        theta=np.asarray([0.0]),
        dps=50,
    ).F_complex[:, 0]
    residual = np.abs(result.F_complex[:, 0] / fresnel - 1.0)
    assert abs(result.F_complex[0, 0] - 1.0) < abs(result.F_complex[1, 0] - 1.0)
    assert residual[0] < residual[1]
    assert residual[0] < 6.0e-3


@pytest.mark.parametrize(
    ("kM", "x", "z", "message"),
    [
        ([0.0], [0.0], [30.0], "kM_values"),
        ([0.1], [0.0], [0.0], "propagation_z_over_M"),
        ([0.1], [0.0, 1.0], [30.0], "equal size"),
    ],
)
def test_rs_phase_screen_rejects_invalid_domain(kM, x, z, message) -> None:
    with pytest.raises(ValueError, match=message):
        _compute(kM=kM, x=x, z=z)


def test_rs_phase_screen_reports_missing_optional_backend(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import = importlib.import_module

    def fake_import(name: str):
        if name == "mpmath":
            raise ModuleNotFoundError("mpmath")
        return real_import(name)

    monkeypatch.setattr(rs_module.importlib, "import_module", fake_import)
    with pytest.raises(RuntimeError, match=r"\[oracle\]"):
        _compute(kM=[0.1], x=[0.0], z=[30.0])
