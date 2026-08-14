from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import ArrayLike
from scipy.special import lambertw


def _return_scalar_if_scalar_input(values: np.ndarray, original: Any) -> float | np.ndarray:
    if np.isscalar(original) or np.asarray(original).ndim == 0:
        return float(values)
    return values


@dataclass(frozen=True)
class SchwarzschildBackground:
    """Schwarzschild metric in units G = c = 1."""

    M: float = 1.0
    name: str = "schwarzschild"

    def __post_init__(self) -> None:
        if self.M <= 0.0:
            raise ValueError("Schwarzschild mass M must be positive.")

    @property
    def horizon_radius(self) -> float:
        return 2.0 * self.M

    def f(self, r: ArrayLike) -> float | np.ndarray:
        radius = self._validate_positive_radius(r)
        lapse = 1.0 - 2.0 * self.M / radius
        return _return_scalar_if_scalar_input(lapse, r)

    def df_dr(self, r: ArrayLike) -> float | np.ndarray:
        radius = self._validate_positive_radius(r)
        derivative = 2.0 * self.M / radius**2
        return _return_scalar_if_scalar_input(derivative, r)

    def r_star(self, r: ArrayLike) -> float | np.ndarray:
        radius = self._validate_exterior_radius(r)
        tortoise = radius + 2.0 * self.M * np.log(radius / (2.0 * self.M) - 1.0)
        return _return_scalar_if_scalar_input(tortoise, r)

    def r_from_r_star(self, r_star: ArrayLike) -> float | np.ndarray:
        tortoise = np.asarray(r_star, dtype=float)
        logarithmic_argument = tortoise / (2.0 * self.M) - 1.0
        scaled_radius = np.empty_like(logarithmic_argument)
        direct = logarithmic_argument <= 700.0
        scaled_radius[direct] = lambertw(
            np.exp(logarithmic_argument[direct]), k=0
        ).real
        if np.any(~direct):
            # For large positive y, evaluating W(exp(y)) directly overflows.
            # Solve w + log(w) = y with Newton iterations instead.  The
            # asymptotic seed is already close and the update is quadratic.
            y = logarithmic_argument[~direct]
            w = y - np.log(y)
            for _ in range(5):
                w -= (w + np.log(w) - y) / (1.0 + 1.0 / w)
            scaled_radius[~direct] = w
        radius = 2.0 * self.M * (1.0 + scaled_radius)
        return _return_scalar_if_scalar_input(radius, r_star)

    def drstar_dr(self, r: ArrayLike) -> float | np.ndarray:
        radius = self._validate_exterior_radius(r)
        derivative = 1.0 / (1.0 - 2.0 * self.M / radius)
        return _return_scalar_if_scalar_input(derivative, r)

    def asymptotic_region_hint(self, k: float, ell: int) -> float:
        if k <= 0.0:
            raise ValueError("Wave number k must be positive.")
        if ell < 2:
            raise ValueError("Radiative Schwarzschild perturbations require ell >= 2.")
        return max(50.0 * self.M, 10.0 * ell / k)

    def _validate_positive_radius(self, r: ArrayLike) -> np.ndarray:
        radius = np.asarray(r, dtype=float)
        if np.any(radius <= 0.0):
            raise ValueError("Radius r must be positive.")
        return radius

    def _validate_exterior_radius(self, r: ArrayLike) -> np.ndarray:
        radius = self._validate_positive_radius(r)
        if np.any(radius <= self.horizon_radius):
            raise ValueError("Schwarzschild tortoise coordinate requires r > 2M.")
        return radius
