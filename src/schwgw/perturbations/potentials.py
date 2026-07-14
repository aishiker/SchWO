from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import ArrayLike

from schwgw.backgrounds.base import StaticSphericalBackground


def _return_scalar_if_scalar_input(values: np.ndarray, original: Any) -> float | np.ndarray:
    if np.isscalar(original):
        return float(values)
    return values


def lambda_parameter(ell: int) -> float:
    """Zerilli lambda = (ell - 1)(ell + 2)/2 for radiative modes."""
    _validate_ell(ell)
    return 0.5 * (ell - 1) * (ell + 2)


def regge_wheeler_potential(
    ell: int, r: ArrayLike, bg: StaticSphericalBackground
) -> float | np.ndarray:
    """Odd-parity Regge-Wheeler potential V_l^(-)(r)."""
    _validate_ell(ell)
    radius = _validate_exterior_radius(r, bg)
    mass = bg.M
    potential = bg.f(radius) / radius**2 * (ell * (ell + 1) - 6.0 * mass / radius)
    return _return_scalar_if_scalar_input(np.asarray(potential, dtype=float), r)


def zerilli_potential(
    ell: int, r: ArrayLike, bg: StaticSphericalBackground
) -> float | np.ndarray:
    """Even-parity Zerilli potential V_l^(+)(r)."""
    lambda_ = lambda_parameter(ell)
    radius = _validate_exterior_radius(r, bg)
    mass_over_r = bg.M / radius
    Lambda = lambda_ + 3.0 * mass_over_r
    bracket = (
        2.0 * lambda_**2 * (lambda_ + 1.0)
        + 6.0 * lambda_**2 * mass_over_r
        + 18.0 * lambda_ * mass_over_r**2
        + 18.0 * mass_over_r**3
    )
    potential = bg.f(radius) / radius**2 * bracket / Lambda**2
    return _return_scalar_if_scalar_input(np.asarray(potential, dtype=float), r)


V_RW = regge_wheeler_potential
V_Zerilli = zerilli_potential


def _validate_ell(ell: int) -> None:
    if ell < 2:
        raise ValueError("Radiative RW/Zerilli modes require ell >= 2.")


def _validate_exterior_radius(r: ArrayLike, bg: StaticSphericalBackground) -> np.ndarray:
    radius = np.asarray(r, dtype=float)
    if np.any(radius <= bg.horizon_radius):
        raise ValueError("RW/Zerilli potentials are evaluated in the exterior r > 2M.")
    return radius
