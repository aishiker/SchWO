from __future__ import annotations

from typing import Protocol

from numpy.typing import ArrayLike


class StaticSphericalBackground(Protocol):
    """Interface for static spherically symmetric backgrounds."""

    name: str
    M: float

    @property
    def horizon_radius(self) -> float:
        """Outer horizon radius in Schwarzschild-like coordinates."""

    def f(self, r: ArrayLike) -> ArrayLike:
        """Metric lapse-like function."""

    def df_dr(self, r: ArrayLike) -> ArrayLike:
        """Radial derivative of the metric lapse-like function."""

    def r_star(self, r: ArrayLike) -> ArrayLike:
        """Tortoise coordinate."""

    def r_from_r_star(self, r_star: ArrayLike) -> ArrayLike:
        """Exterior inverse tortoise coordinate."""

    def drstar_dr(self, r: ArrayLike) -> ArrayLike:
        """Derivative of the tortoise coordinate with respect to r."""

    def asymptotic_region_hint(self, k: float, ell: int) -> float:
        """Heuristic radius where matching to asymptotic waves is reasonable."""
