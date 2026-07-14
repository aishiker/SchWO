"""Incident plane-wave coefficients in the frozen ``+z`` convention."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.special import spherical_jn

from schwgw.waves.polarizations import linear_to_circular


def _as_complex_scalar(value: Any, name: str) -> complex:
    try:
        return complex(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must be convertible to a complex scalar") from exc


def _validate_radiative_mode(ell: int, m: int) -> None:
    if not isinstance(ell, int) or not isinstance(m, int):
        raise TypeError("ell and m must be integers")
    if ell < 2:
        raise ValueError("ell must be at least 2 for radiative gravitational modes")
    if abs(m) > ell:
        raise ValueError("abs(m) must be <= ell")


def _positive_radius_array(r: Any) -> tuple[np.ndarray, bool]:
    try:
        radius = np.asarray(r, dtype=float)
    except (TypeError, ValueError) as exc:
        raise TypeError("r must be a positive real scalar or array-like") from exc
    if np.any(radius <= 0.0):
        raise ValueError("r must be positive")
    return radius, radius.shape == ()


def sigma_l(ell: int) -> int:
    """Return ``sigma_l = (ell-1) ell (ell+1) (ell+2)`` for ``ell >= 2``."""

    if not isinstance(ell, int):
        raise TypeError("ell must be an integer")
    if ell < 2:
        raise ValueError("ell must be at least 2")
    return (ell - 1) * ell * (ell + 1) * (ell + 2)


@dataclass(frozen=True)
class IncidentPlaneGW:
    """Incident plane gravitational wave propagating along ``+z``."""

    k: float
    A_plus: complex
    A_cross: complex
    incident_direction: str = "+z"

    def __post_init__(self) -> None:
        try:
            k_value = float(self.k)
        except (TypeError, ValueError) as exc:
            raise TypeError("k must be a positive real scalar") from exc
        if k_value <= 0.0:
            raise ValueError("k must be positive")
        if self.incident_direction != "+z":
            raise NotImplementedError(
                "Only incident_direction='+z' is implemented in Phase 2; "
                "generic directions require future Wigner-D rotation support."
            )

        object.__setattr__(self, "k", k_value)
        object.__setattr__(self, "A_plus", _as_complex_scalar(self.A_plus, "A_plus"))
        object.__setattr__(self, "A_cross", _as_complex_scalar(self.A_cross, "A_cross"))

    @property
    def A_L(self) -> complex:
        """Left circular amplitude in the project convention."""

        return linear_to_circular(self.A_plus, self.A_cross)[0]

    @property
    def A_R(self) -> complex:
        """Right circular amplitude in the project convention."""

        return linear_to_circular(self.A_plus, self.A_cross)[1]

    def _A_lm(self, ell: int, m: int, parity_sign: int) -> complex:
        _validate_radiative_mode(ell, m)
        if m not in (-2, 2):
            return 0.0

        normalization = (1j) ** ell * math.sqrt(
            2.0 * math.pi * (2 * ell + 1) / sigma_l(ell)
        )
        selected_left = self.A_L if m == -2 else 0.0
        selected_right = self.A_R if m == 2 else 0.0
        return normalization * (selected_left + parity_sign * selected_right)

    def A_lm_plus(self, ell: int, m: int) -> complex:
        """Return ``A_lm^(+)``."""

        return self._A_lm(ell, m, parity_sign=1)

    def A_lm_even(self, ell: int, m: int) -> complex:
        """Alias for ``A_lm^(+)``."""

        return self.A_lm_plus(ell, m)

    def A_lm_minus(self, ell: int, m: int) -> complex:
        """Return ``A_lm^(-)``."""

        return self._A_lm(ell, m, parity_sign=-1)

    def A_lm_odd(self, ell: int, m: int) -> complex:
        """Alias for ``A_lm^(-)``."""

        return self.A_lm_minus(ell, m)

    def c_lm_odd(self, ell: int, m: int) -> complex:
        """Return ``c_lm^(-) = -[i^(ell+1)/2] A_lm^(-)``."""

        return -((1j) ** (ell + 1)) / 2.0 * self.A_lm_minus(ell, m)

    def c_lm_even(self, ell: int, m: int) -> complex:
        """Return ``c_lm^(+) = [i^(ell+1)/k] A_lm^(+)``."""

        return ((1j) ** (ell + 1)) / self.k * self.A_lm_plus(ell, m)

    def flat_space_master_odd(self, ell: int, m: int, r: Any) -> complex | np.ndarray:
        """Return ``D_lm^(-)(k,r) = -k r A_lm^(-) j_l(k r)``."""

        radius, is_scalar = _positive_radius_array(r)
        values = -self.k * radius * self.A_lm_minus(ell, m) * spherical_jn(ell, self.k * radius)
        if is_scalar:
            return complex(values)
        return values

    def flat_space_master_even(self, ell: int, m: int, r: Any) -> complex | np.ndarray:
        """Return ``D_lm^(+)(k,r) = 2 r A_lm^(+) j_l(k r)``."""

        radius, is_scalar = _positive_radius_array(r)
        values = 2.0 * radius * self.A_lm_plus(ell, m) * spherical_jn(ell, self.k * radius)
        if is_scalar:
            return complex(values)
        return values
