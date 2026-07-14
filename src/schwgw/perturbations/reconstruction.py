from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from schwgw.backgrounds.base import StaticSphericalBackground
from schwgw.perturbations.potentials import lambda_parameter, zerilli_potential
from schwgw.perturbations.sectors import Sector


@dataclass(frozen=True)
class MetricModeComponents:
    """RW-gauge metric harmonic components for one radial master mode."""

    sector: Sector
    ell: int
    k: float
    r: float
    components: Mapping[str, complex]


def reconstruct_metric_mode(
    sector: Sector | str,
    ell: int,
    k: float,
    r: float,
    psi: complex,
    dpsi_dr: complex,
    background: StaticSphericalBackground,
) -> MetricModeComponents:
    """Reconstruct RW-gauge metric components from a Schwarzschild master mode.

    The derivative argument is the areal-radius derivative ``dpsi/dr``. If a
    caller has ``dpsi/dr_star``, it must divide by ``f(r)`` before calling.
    """

    sector_enum = _coerce_sector(sector)
    radius = _validate_inputs(ell=ell, k=k, r=r, background=background)
    psi_value = complex(psi)
    derivative = complex(dpsi_dr)

    if sector_enum is Sector.ODD:
        components = _reconstruct_odd(k, radius, psi_value, derivative, background)
    else:
        components = _reconstruct_even(ell, k, radius, psi_value, derivative, background)

    return MetricModeComponents(
        sector=sector_enum,
        ell=ell,
        k=float(k),
        r=radius,
        components=MappingProxyType(components),
    )


def _reconstruct_odd(
    k: float,
    r: float,
    psi: complex,
    dpsi_dr: complex,
    background: StaticSphericalBackground,
) -> dict[str, complex]:
    f = float(background.f(r))
    return {
        "Bt": f / (1j * k) * (psi + r * dpsi_dr),
        "B1": -(r / f) * psi,
    }


def _reconstruct_even(
    ell: int,
    k: float,
    r: float,
    psi: complex,
    dpsi_dr: complex,
    background: StaticSphericalBackground,
) -> dict[str, complex]:
    f = float(background.f(r))
    mass_over_r = background.M / r
    lambda_ = lambda_parameter(ell)
    sigma = _sigma_l(ell)
    Lambda = lambda_ + 3.0 * mass_over_r
    zerilli = float(zerilli_potential(ell, r, background))

    T0 = r * (
        (sigma / 4.0 + 3.0 * lambda_ * mass_over_r + 6.0 * mass_over_r**2)
        / Lambda
        * psi
        + r * f * dpsi_dr
    )
    Rt = -1j * k * (
        (lambda_ - 3.0 * lambda_ * mass_over_r - 3.0 * mass_over_r**2)
        / (Lambda * f)
        * psi
        + r * dpsi_dr
    )
    L0 = (
        -(r / f**2) * (k**2 - 0.5 * zerilli) * psi
        - (1.0 / f) * (mass_over_r - lambda_ * f / Lambda) * dpsi_dr
    )
    return {
        "T0": T0,
        "Rt": Rt,
        "L0": L0,
        "tt": f**2 * L0,
    }


def _sigma_l(ell: int) -> int:
    return (ell - 1) * ell * (ell + 1) * (ell + 2)


def _validate_inputs(
    ell: int,
    k: float,
    r: float,
    background: StaticSphericalBackground,
) -> float:
    if not isinstance(ell, int):
        raise TypeError("ell must be an integer.")
    if ell < 2:
        raise ValueError("Radiative RW-gauge reconstruction requires ell >= 2.")

    k_value = float(k)
    if k_value <= 0.0:
        raise ValueError("Wave number k must be positive.")

    radius = float(r)
    if radius <= background.horizon_radius:
        raise ValueError("Metric reconstruction requires exterior radius r > 2M.")
    return radius


def _coerce_sector(sector: Sector | str) -> Sector:
    try:
        return sector if isinstance(sector, Sector) else Sector(sector)
    except ValueError as exc:
        raise ValueError("sector must be 'odd' or 'even'.") from exc


__all__ = ["MetricModeComponents", "reconstruct_metric_mode"]
