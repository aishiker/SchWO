"""Spin-weighted spherical harmonics in the project Wigner-D convention."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from schwgw.angular.wigner import wigner_D


def _validate_spin_indices(s: int, ell: int, m: int) -> None:
    if not all(isinstance(value, int) for value in (s, ell, m)):
        raise TypeError("s, ell, and m must be integers")
    if ell < 0:
        raise ValueError("ell must be non-negative")
    if abs(s) > ell:
        raise ValueError("abs(s) must be <= ell")
    if abs(m) > ell:
        raise ValueError("abs(m) must be <= ell")


def spin_weighted_sph_harm(s: int, ell: int, m: int, theta: Any, phi: Any) -> np.ndarray:
    """Return ``_sY_ell,m(theta, phi)`` in the frozen project convention."""

    _validate_spin_indices(s, ell, m)
    normalization = math.sqrt((2 * ell + 1) / (4.0 * math.pi))
    spin_phase = -1 if s % 2 else 1
    return spin_phase * normalization * np.conj(wigner_D(ell, m, -s, phi, theta, 0.0))
