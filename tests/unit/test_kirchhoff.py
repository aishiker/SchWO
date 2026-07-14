from __future__ import annotations

import importlib

import mpmath as mp
import numpy as np
import pytest

import schwgw.numerics.radial_solver as radial_solver
import schwgw.scattering.kirchhoff as kirchhoff_module
from schwgw.scattering.kirchhoff import (
    KirchhoffEq47Result,
    compute_kirchhoff_eq47,
)


def test_eq47_shapes_eta_axis_value_and_metadata() -> None:
    kM = np.array([0.1, 1.0, 4.0])
    r_over_M = np.array([30.0, np.hypot(25.0, 30.0)])
    theta = np.array([0.0, np.arctan2(25.0, 30.0)])

    result = compute_kirchhoff_eq47(
        kM_values=kM,
        r_over_M=r_over_M,
        theta=theta,
        dps=60,
    )

    assert isinstance(result, KirchhoffEq47Result)
    assert result.F_complex.shape == (3, 2)
    np.testing.assert_allclose(result.gamma, -2.0 * kM, rtol=0.0, atol=0.0)
    np.testing.assert_allclose(
        result.eta,
        0.5 * np.sqrt(r_over_M) * np.tan(theta),
        rtol=0.0,
        atol=2.0e-15,
    )
    assert result.valid_mask.all()
    np.testing.assert_allclose(result.abs_F, np.abs(result.F_complex))
    np.testing.assert_allclose(result.arg_F_principal, np.angle(result.F_complex))
    assert result.metadata["baseline"]["comparison_only"] is True
    assert result.metadata["baseline"]["not_denominator"] is True
    assert result.metadata["baseline"]["polarization_independent"] is True

    with mp.workdps(80):
        gamma = mp.mpf("-0.2")
        axis_value = mp.exp(
            mp.pi * gamma / 2
            + (-1j * gamma) * mp.log(-gamma)
            + mp.loggamma(1 + 1j * gamma)
        )
    assert result.F_complex[0, 0] == pytest.approx(complex(axis_value), rel=2e-14)


def test_eq47_matches_kummer_transformation_at_high_risk_corner() -> None:
    r_over_M = np.array([np.hypot(25.0, 30.0)])
    theta = np.array([np.arctan2(25.0, 30.0)])
    result = compute_kirchhoff_eq47(
        kM_values=np.array([4.0]),
        r_over_M=r_over_M,
        theta=theta,
        dps=80,
    )

    with mp.workdps(100):
        gamma = mp.mpf("-8")
        eta = mp.mpf(str(result.eta[0]))
        a = -1j * gamma
        z = -1j * gamma * eta**2
        prefactor = mp.exp(
            mp.pi * gamma / 2
            + (-1j * gamma) * mp.log(-gamma)
            + mp.loggamma(1 + 1j * gamma)
        )
        transformed = prefactor * mp.exp(z) * mp.hyp1f1(1 - a, 1, -z)

    assert result.F_complex[0, 0] == pytest.approx(
        complex(transformed), rel=3e-13, abs=3e-13
    )


def test_eq47_never_calls_radial_solver(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: object, **kwargs: object) -> object:
        raise AssertionError("Kirchhoff comparison must not call the radial solver")

    monkeypatch.setattr(radial_solver, "solve_radial_mode", forbidden)
    result = compute_kirchhoff_eq47(
        kM_values=np.array([0.5]),
        r_over_M=np.array([30.0]),
        theta=np.array([0.0]),
        dps=40,
    )
    assert result.valid_mask.tolist() == [[True]]


@pytest.mark.parametrize(
    ("kM", "r_over_M", "theta", "message"),
    [
        ([0.0], [30.0], [0.0], "kM_values"),
        ([0.1], [-1.0], [0.0], "r_over_M"),
        ([0.1], [30.0], [np.pi / 2], "theta"),
    ],
)
def test_eq47_rejects_invalid_domain(kM, r_over_M, theta, message) -> None:
    with pytest.raises(ValueError, match=message):
        compute_kirchhoff_eq47(
            kM_values=np.asarray(kM),
            r_over_M=np.asarray(r_over_M),
            theta=np.asarray(theta),
        )


def test_eq47_reports_missing_optional_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = importlib.import_module

    def fake_import(name: str):
        if name == "mpmath":
            raise ModuleNotFoundError("mpmath")
        return real_import(name)

    monkeypatch.setattr(kirchhoff_module.importlib, "import_module", fake_import)
    with pytest.raises(RuntimeError, match=r"\[oracle\]"):
        compute_kirchhoff_eq47(
            kM_values=np.array([0.1]),
            r_over_M=np.array([30.0]),
            theta=np.array([0.0]),
        )
