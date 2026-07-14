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
        argument = np.exp(tortoise / (2.0 * self.M) - 1.0)
        radius = 2.0 * self.M * (1.0 + lambertw(argument, k=0).real)
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
