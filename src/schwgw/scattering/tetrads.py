from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

import numpy as np

from schwgw.backgrounds.base import StaticSphericalBackground


@dataclass(frozen=True)
class NullTetrad:
    """Null tetrad vectors and metric components in one coordinate chart."""

    coordinates: str
    legs: Mapping[str, np.ndarray]
    metric: np.ndarray


def kinnersley_tetrad(
    background: StaticSphericalBackground,
    r: float,
    theta: float,
) -> NullTetrad:
    """Return the Schwarzschild Kinnersley tetrad in `(t,r,theta,phi)` coordinates."""

    radius = float(r)
    if radius <= background.horizon_radius:
        raise ValueError("Kinnersley tetrad requires exterior radius r > 2M.")

    theta_value = float(theta)
    sin_theta = np.sin(theta_value)
    if abs(sin_theta) <= 100.0 * np.finfo(float).eps:
        raise ValueError("Kinnersley tetrad is singular on the polar axis.")

    f = float(background.f(radius))
    m_leg = np.array(
        [0.0, 0.0, 1.0, 1j / sin_theta],
        dtype=complex,
    ) / (np.sqrt(2.0) * radius)
    legs = {
        "l": np.array([1.0 / f, 1.0, 0.0, 0.0], dtype=complex),
        "n": 0.5 * np.array([1.0, -f, 0.0, 0.0], dtype=complex),
        "m": m_leg,
        "mbar": np.conjugate(m_leg),
    }
    metric = np.diag(
        [-f, 1.0 / f, radius**2, radius**2 * sin_theta**2],
    ).astype(complex)
    return NullTetrad(
        coordinates="schwarzschild",
        legs=MappingProxyType(legs),
        metric=metric,
    )


def incident_cartesian_tetrad() -> NullTetrad:
    """Return the incident-wave-aligned Cartesian null tetrad."""

    scale = 1.0 / np.sqrt(2.0)
    m_leg = scale * np.array([0.0, 1.0, 1j, 0.0], dtype=complex)
    legs = {
        "l": scale * np.array([1.0, 0.0, 0.0, 1.0], dtype=complex),
        "n": scale * np.array([1.0, 0.0, 0.0, -1.0], dtype=complex),
        "m": m_leg,
        "mbar": np.conjugate(m_leg),
    }
    return NullTetrad(
        coordinates="cartesian",
        legs=MappingProxyType(legs),
        metric=np.diag([-1.0, 1.0, 1.0, 1.0]).astype(complex),
    )


def tetrad_inner_product(tetrad: NullTetrad, first: str, second: str) -> complex:
    """Return the bilinear metric inner product of two tetrad legs."""

    try:
        first_leg = tetrad.legs[first]
        second_leg = tetrad.legs[second]
    except KeyError as exc:
        raise ValueError("Unknown tetrad leg label.") from exc
    return complex(first_leg @ tetrad.metric @ second_leg)


def tetrad_inner_products(tetrad: NullTetrad) -> dict[tuple[str, str], complex]:
    """Return all pairwise bilinear inner products between tetrad legs."""

    labels = ("l", "n", "m", "mbar")
    return {
        (first, second): tetrad_inner_product(tetrad, first, second)
        for first in labels
        for second in labels
    }


__all__ = [
    "NullTetrad",
    "incident_cartesian_tetrad",
    "kinnersley_tetrad",
    "tetrad_inner_product",
    "tetrad_inner_products",
]
