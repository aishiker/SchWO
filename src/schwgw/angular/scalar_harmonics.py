"""Scalar spherical harmonics in the project angular convention."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.special import gammaln, lpmv


def _validate_ell_m(ell: int, m: int) -> None:
    if not isinstance(ell, int) or not isinstance(m, int):
        raise TypeError("ell and m must be integers")
    if ell < 0:
        raise ValueError("ell must be non-negative")
    if abs(m) > ell:
        raise ValueError("abs(m) must be <= ell")


def _positive_m_scalar_sph_harm(ell: int, m: int, theta: Any, phi: Any) -> np.ndarray:
    theta_array = np.asarray(theta)
    phi_array = np.asarray(phi)
    log_norm = (
        0.5
        * (
            math.log((2 * ell + 1) / (4.0 * math.pi))
            + gammaln(ell - m + 1)
            - gammaln(ell + m + 1)
        )
    )
    norm = math.exp(log_norm)
    associated_legendre = lpmv(m, ell, np.cos(theta_array))
    return norm * associated_legendre * np.exp(1j * m * phi_array)


def scalar_sph_harm(ell: int, m: int, theta: Any, phi: Any) -> np.ndarray:
    """Return unit-normalized scalar spherical harmonic ``Y_ell,m(theta, phi)``.

    The convention is the frozen project convention in ``docs/physics_spec.md``
    Sec. 1.2. SciPy's ``lpmv`` already includes the Condon-Shortley phase, so
    the non-negative-m branch does not apply an extra ``(-1)^m`` factor.
    """

    _validate_ell_m(ell, m)
    if m < 0:
        positive_m = -m
        return (-1) ** positive_m * np.conj(
            _positive_m_scalar_sph_harm(ell, positive_m, theta, phi)
        )
    return _positive_m_scalar_sph_harm(ell, m, theta, phi)
