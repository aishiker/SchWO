from __future__ import annotations

import math
from dataclasses import dataclass
from types import MappingProxyType
from functools import lru_cache
from typing import Mapping, Sequence

import numpy as np

from schwgw.angular.spin_weighted import spin_weighted_sph_harm
from schwgw.angular.wigner import wigner_D
from schwgw.backgrounds.base import StaticSphericalBackground
from schwgw.perturbations.potentials import (
    lambda_parameter,
    regge_wheeler_potential,
    zerilli_potential,
)
from schwgw.perturbations.reconstruction import MetricModeComponents
from schwgw.perturbations.sectors import Sector
from schwgw.scattering.observables import (
    ElectricTidalComponents,
    PackagedPolarizationScalars,
    package_electric_tidal_components,
)


_SPIN_WEIGHTS = {
    "Psi4": -2,
    "Psi3": -1,
    "Psi2": 0,
    "Psi1": 1,
    "Psi0": 2,
}


FULL_NP_PSEUDOINVERSE_BRIDGE_NAME = (
    "full strict-NP pseudoinverse tidal projection"
)
FULL_NP_PSEUDOINVERSE_BRIDGE_VALIDATED = False


@dataclass(frozen=True)
class WeylModeComponents:
    """One `(sector, ell, m)` Weyl-scalar mode in the Kinnersley tetrad."""

    sector: Sector
    ell: int
    m: int
    k: float
    r: float
    theta: float
    phi: float
    components: Mapping[str, complex]
    spin_weights: Mapping[str, int]
    angular_factors: Mapping[str, complex]
    radial_sources: Mapping[str, complex]


@dataclass(frozen=True)
class StrictNPScalars:
    """Full strict Newman-Penrose Weyl quintuple in a named tetrad frame."""

    psi0: complex
    psi1: complex
    psi2: complex
    psi3: complex
    psi4: complex
    frame: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "psi0", complex(self.psi0))
        object.__setattr__(self, "psi1", complex(self.psi1))
        object.__setattr__(self, "psi2", complex(self.psi2))
        object.__setattr__(self, "psi3", complex(self.psi3))
        object.__setattr__(self, "psi4", complex(self.psi4))
        if self.frame not in {"incident", "kinnersley"}:
            raise ValueError("frame must be 'incident' or 'kinnersley'.")

    @classmethod
    def from_mapping(
        cls,
        scalars: Mapping[str, complex],
        *,
        frame: str,
    ) -> StrictNPScalars:
        """Build a strict NP quintuple from ``Psi0`` ... ``Psi4`` labels."""

        missing = set(_SPIN_WEIGHTS) - set(scalars)
        if missing:
            raise ValueError(f"Missing strict NP scalar components: {sorted(missing)}")
        return cls(
            psi0=scalars["Psi0"],
            psi1=scalars["Psi1"],
            psi2=scalars["Psi2"],
            psi3=scalars["Psi3"],
            psi4=scalars["Psi4"],
            frame=frame,
        )

    def as_mapping(self) -> Mapping[str, complex]:
        """Return the canonical strict-NP label mapping."""

        return MappingProxyType(
            {
                "Psi0": self.psi0,
                "Psi1": self.psi1,
                "Psi2": self.psi2,
                "Psi3": self.psi3,
                "Psi4": self.psi4,
            }
        )


def weyl_mode_components(
    sector: Sector | str,
    ell: int,
    m: int,
    k: float,
    r: float,
    theta: float,
    phi: float,
    metric_mode: MetricModeComponents,
    background: StaticSphericalBackground,
) -> WeylModeComponents:
    """Compute one Weyl-scalar mode contribution in the Kinnersley tetrad."""

    sector_enum = _coerce_sector(sector)
    _validate_mode_indices(ell, m)
    if metric_mode.sector is not sector_enum:
        raise ValueError("metric_mode sector does not match requested sector.")
    if metric_mode.ell != ell:
        raise ValueError("metric_mode ell does not match requested ell.")

    radius = float(r)
    if radius <= background.horizon_radius:
        raise ValueError("Weyl mode components require exterior radius r > 2M.")
    k_value = float(k)
    if k_value <= 0.0:
        raise ValueError("Wave number k must be positive.")

    psi, dpsi_dr = _master_from_metric_mode(metric_mode, background)
    radial_sources = _radial_sources(sector_enum, ell, k_value, radius, psi, dpsi_dr, background)
    angular_factors = {
        label: complex(spin_weighted_sph_harm(spin, ell, m, theta, phi))
        for label, spin in _SPIN_WEIGHTS.items()
    }

    sigma = _sigma_l(ell)
    ell_factor = math.sqrt(2.0 * ell * (ell + 1))
    components = {
        "Psi4": math.sqrt(sigma) * radial_sources["Z4"] * angular_factors["Psi4"],
        "Psi3": ell_factor * radial_sources["Z3"] * angular_factors["Psi3"],
        "Psi2": radial_sources["Z2"] * angular_factors["Psi2"],
        "Psi1": ell_factor * radial_sources["Z1"] * angular_factors["Psi1"],
        "Psi0": math.sqrt(sigma) * radial_sources["Z0"] * angular_factors["Psi0"],
    }

    return WeylModeComponents(
        sector=sector_enum,
        ell=ell,
        m=m,
        k=k_value,
        r=radius,
        theta=float(theta),
        phi=float(phi),
        components=MappingProxyType(components),
        spin_weights=MappingProxyType(dict(_SPIN_WEIGHTS)),
        angular_factors=MappingProxyType(angular_factors),
        radial_sources=MappingProxyType(radial_sources),
    )


def assemble_weyl_scalars(modes: Sequence[WeylModeComponents]) -> dict[str, complex]:
    """Sum already computed Weyl mode components."""

    assembled = {label: 0.0j for label in _SPIN_WEIGHTS}
    for mode in modes:
        for label in assembled:
            assembled[label] += mode.components[label]
    return assembled


def transform_weyl_to_incident_tetrad(
    weyl_scalars: WeylModeComponents | Mapping[str, complex],
    theta: float,
    phi: float,
) -> dict[str, complex]:
    """Compatibility alias for the strict-NP incident-tetrad transform."""

    return transform_strict_np_weyl_to_incident_tetrad(weyl_scalars, theta, phi)


def transform_strict_np_weyl_to_incident_tetrad(
    weyl_scalars: WeylModeComponents | StrictNPScalars | Mapping[str, complex],
    theta: float,
    phi: float,
) -> dict[str, complex]:
    """Transform strict NP scalars from the flat Kinnersley frame to incident frame.

    The transform is obtained from the Weyl tensor component definition, not
    by applying the paper's Wigner-D expression to packaged polarization
    scalars.  This fixes the active/passive/index-order bridge against direct
    tensor-contraction tests.
    """

    source = _weyl_mapping(weyl_scalars)
    source_vector = np.array([source[label] for label in _NP_LABELS], dtype=complex)
    matrix = _strict_np_transform_matrix(float(theta), float(phi))
    target_vector = matrix @ source_vector
    return {
        label: complex(value)
        for label, value in zip(_NP_LABELS, target_vector, strict=True)
    }


def compute_packaged_polarization_scalars(
    strict_np_scalars: StrictNPScalars,
) -> PackagedPolarizationScalars:
    """Return the legacy full-NP pseudoinverse tidal projection.

    The input is a full strict-NP Weyl quintuple in the incident tetrad.  The
    output is the project positive-frequency packaged pair consumed by
    ``polarization_from_packaged_scalars``; it is not a strict-NP transform.

    This bridge is retained for reproducibility and diagnostics, but it is
    *not* validated as a physical observable bridge for a one-sided
    positive-frequency curved field.  In particular, reconstructing a real
    Weyl tensor from all five NP scalars also requires the unresolved
    ``(+k,m)``/``(-k,-m)`` reality partner.  Paper-facing callers must record
    :data:`FULL_NP_PSEUDOINVERSE_BRIDGE_VALIDATED` and must not present this
    result as a closed Li--Hou--Zhao observable convention.
    """

    if not isinstance(strict_np_scalars, StrictNPScalars):
        raise TypeError("strict_np_scalars must be a StrictNPScalars instance.")
    if strict_np_scalars.frame != "incident":
        raise ValueError("strict_np_scalars must be in the incident frame.")
    source = _weyl_mapping(strict_np_scalars)
    source_vector = np.array([source[label] for label in _NP_LABELS], dtype=complex)
    matrix = _full_np_pseudoinverse_tidal_matrix()
    e_xx, e_xy = matrix @ source_vector
    return package_electric_tidal_components(
        ElectricTidalComponents(
            E_xx=complex(e_xx),
            E_xy=complex(e_xy),
        )
    )


def _master_from_metric_mode(
    metric_mode: MetricModeComponents,
    background: StaticSphericalBackground,
) -> tuple[complex, complex]:
    r = metric_mode.r
    k = metric_mode.k
    f = float(background.f(r))
    lambda_ = lambda_parameter(metric_mode.ell)
    mass_over_r = background.M / r
    Lambda = lambda_ + 3.0 * mass_over_r

    if metric_mode.sector is Sector.ODD:
        psi = -f / r * metric_mode.components["B1"]
        dpsi_dr = ((1j * k / f) * metric_mode.components["Bt"] - psi) / r
        return complex(psi), complex(dpsi_dr)

    psi = (
        metric_mode.components["T0"] / r
        + f / (1j * k) * metric_mode.components["Rt"]
    ) / Lambda
    coefficient = (
        lambda_ - 3.0 * lambda_ * mass_over_r - 3.0 * mass_over_r**2
    ) / (Lambda * f)
    dpsi_dr = (metric_mode.components["Rt"] / (-1j * k) - coefficient * psi) / r
    return complex(psi), complex(dpsi_dr)


def _radial_sources(
    sector: Sector,
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
    Rpsi = r * dpsi_dr

    if sector is Sector.ODD:
        potential = float(regge_wheeler_potential(ell, r, background))
        Z4 = (
            (2.0 / k)
            * (
                r**2 * potential
                + 2j * k * r * (1.0 - 3.0 * mass_over_r)
                - 2.0 * (k * r) ** 2
            )
            * psi
            + (4.0 / k)
            * f
            * (1.0 - 3.0 * mass_over_r + 1j * k * r)
            * Rpsi
        ) / (16.0 * r**3)
        Z3 = (
            (2.0 / k)
            * (f * mass_over_r + 1j * k * r * (lambda_ + mass_over_r))
            * psi
            + (2.0 / k) * f * (lambda_ + mass_over_r) * Rpsi
        ) / (8.0 * r**3)
        Z2 = ((4.0 / k) * sigma * psi) / (16.0 * r**3)
    else:
        potential = float(zerilli_potential(ell, r, background))
        common = lambda_ - 3.0 * lambda_ * mass_over_r - 3.0 * mass_over_r**2
        Z4 = (
            (
                r**2 * potential
                + (2j * k * r / Lambda) * common
                - 2.0 * (k * r) ** 2
            )
            * psi
            + 2.0
            * f
            * (common / Lambda + 1j * k * r)
            * Rpsi
        ) / (16.0 * r**3)
        Z3 = (
            (-3.0 * f * mass_over_r + 1j * k * r * Lambda) * psi
            + f * Lambda * Rpsi
        ) / (8.0 * r**3)
        Z2 = (
            (
                4.0 * ell * (ell + 1) * lambda_**2
                + 10.0 * sigma * mass_over_r
                + 24.0 * (ell**2 + ell + 1.0) * mass_over_r**2
                - 48.0 * mass_over_r**3
            )
            * psi
            / Lambda
            - 8.0 * f * mass_over_r * Rpsi
        ) / (16.0 * r**3)

    # Positive-frequency complex amplitudes are stored linearly. The target
    # paper writes complex conjugates in Eq. (35g)-(35h); T6c keeps the
    # project storage convention linear and leaves the physical convention
    # check to the no-lens tests in T7.
    Z1 = (2.0 / f) * Z3
    Z0 = (2.0 / f) ** 2 * Z4
    return {
        "Z4": complex(Z4),
        "Z3": complex(Z3),
        "Z2": complex(Z2),
        "Z1": complex(Z1),
        "Z0": complex(Z0),
    }


def _lambda_coefficient(m_index: int, spin_index: int, theta: float, phi: float) -> complex:
    ell = 2
    factorial_ratio = math.sqrt(
        math.factorial(ell + m_index)
        * math.factorial(ell - m_index)
        / (
            math.factorial(ell + spin_index)
            * math.factorial(ell - spin_index)
        )
    )
    coefficient = (
        (-1) ** (spin_index + m_index)
        * 2.0 ** (-spin_index / 2.0)
        * factorial_ratio
        * wigner_D(ell, m_index, spin_index, phi, theta, 0.0)
    )
    return complex(coefficient)


_NP_LABELS = ("Psi0", "Psi1", "Psi2", "Psi3", "Psi4")
_MINKOWSKI_METRIC = np.diag([-1.0, 1.0, 1.0, 1.0]).astype(complex)


@lru_cache(maxsize=128)
def _strict_np_transform_matrix(theta: float, phi: float) -> np.ndarray:
    source_rows = _np_contraction_rows(_flat_kinnersley_cartesian_legs(theta, phi))
    target_rows = _np_contraction_rows(_incident_cartesian_legs())
    nullspace = _weyl_constraint_nullspace()
    source_map = source_rows @ nullspace
    target_map = target_rows @ nullspace
    return target_map @ np.linalg.pinv(source_map, rcond=1e-12)


@lru_cache(maxsize=1)
def _weyl_constraint_nullspace() -> np.ndarray:
    rows = []
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    rows.append(_tensor_row([(1.0, (a, b, c, d)), (1.0, (b, a, c, d))]))
                    rows.append(_tensor_row([(1.0, (a, b, c, d)), (1.0, (a, b, d, c))]))
                    rows.append(_tensor_row([(1.0, (a, b, c, d)), (-1.0, (c, d, a, b))]))
                    rows.append(
                        _tensor_row(
                            [
                                (1.0, (a, b, c, d)),
                                (1.0, (a, c, d, b)),
                                (1.0, (a, d, b, c)),
                            ]
                        )
                    )

    for b in range(4):
        for d in range(4):
            terms = []
            for a in range(4):
                for c in range(4):
                    metric_value = _MINKOWSKI_METRIC[a, c]
                    if metric_value != 0.0:
                        terms.append((metric_value, (a, b, c, d)))
            rows.append(_tensor_row(terms))

    constraints = np.vstack(rows)
    _, singular_values, vh = np.linalg.svd(constraints, full_matrices=True)
    rank = int(np.count_nonzero(singular_values > 1e-10))
    return vh[rank:].conj().T


@lru_cache(maxsize=1)
def _full_np_pseudoinverse_tidal_matrix() -> np.ndarray:
    """Build the legacy diagnostic map from a strict-NP quintuple to E_ij.

    The linear algebra itself is exact for one internally consistent Weyl
    tensor.  Its use on the current one-sided positive-frequency quintuple is
    the unvalidated step; naming it explicitly prevents that distinction from
    being hidden behind a generic ``electric_tidal`` label.
    """
    legs = _incident_cartesian_legs()
    nullspace = _weyl_constraint_nullspace()
    source_map = _np_contraction_rows(legs) @ nullspace
    tensor_from_np = np.linalg.pinv(source_map, rcond=1e-12)

    l_leg = legs["l"]
    n_leg = legs["n"]
    m_leg = legs["m"]
    mbar_leg = legs["mbar"]
    e0 = (l_leg + n_leg) / math.sqrt(2.0)
    ex = (m_leg + mbar_leg) / math.sqrt(2.0)
    ey = (m_leg - mbar_leg) / (1.0j * math.sqrt(2.0))

    e_xx = _weyl_tensor_contraction_row(e0, ex, e0, ex) @ nullspace @ tensor_from_np
    e_xy = _weyl_tensor_contraction_row(e0, ex, e0, ey) @ nullspace @ tensor_from_np
    return np.vstack([e_xx, e_xy])


def _tensor_row(terms: Sequence[tuple[complex, tuple[int, int, int, int]]]) -> np.ndarray:
    row = np.zeros(4**4, dtype=complex)
    for coefficient, indices in terms:
        row[_tensor_index(*indices)] += coefficient
    return row


def _weyl_tensor_contraction_row(
    first: np.ndarray,
    second: np.ndarray,
    third: np.ndarray,
    fourth: np.ndarray,
) -> np.ndarray:
    row = np.zeros(4**4, dtype=complex)
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    row[_tensor_index(a, b, c, d)] += (
                        first[a] * second[b] * third[c] * fourth[d]
                    )
    return row


def _np_contraction_rows(tetrad_legs: Mapping[str, np.ndarray]) -> np.ndarray:
    l_leg = tetrad_legs["l"]
    n_leg = tetrad_legs["n"]
    m_leg = tetrad_legs["m"]
    mbar_leg = tetrad_legs["mbar"]
    contractions = (
        (l_leg, m_leg, l_leg, m_leg),
        (l_leg, n_leg, l_leg, m_leg),
        (l_leg, m_leg, n_leg, mbar_leg),
        (l_leg, n_leg, n_leg, mbar_leg),
        (n_leg, mbar_leg, n_leg, mbar_leg),
    )
    rows = []
    for legs in contractions:
        row = np.zeros(4**4, dtype=complex)
        for a in range(4):
            for b in range(4):
                for c in range(4):
                    for d in range(4):
                        row[_tensor_index(a, b, c, d)] -= (
                            legs[0][a] * legs[1][b] * legs[2][c] * legs[3][d]
                        )
        rows.append(row)
    return np.vstack(rows)


def _flat_kinnersley_cartesian_legs(theta: float, phi: float) -> dict[str, np.ndarray]:
    radial = np.array(
        [
            math.sin(theta) * math.cos(phi),
            math.sin(theta) * math.sin(phi),
            math.cos(theta),
        ],
        dtype=complex,
    )
    theta_leg = np.array(
        [
            math.cos(theta) * math.cos(phi),
            math.cos(theta) * math.sin(phi),
            -math.sin(theta),
        ],
        dtype=complex,
    )
    phi_leg = np.array([-math.sin(phi), math.cos(phi), 0.0], dtype=complex)
    m_leg = np.concatenate([[0.0j], (theta_leg + 1.0j * phi_leg) / math.sqrt(2.0)])
    return {
        "l": np.concatenate([[1.0 + 0.0j], radial]),
        "n": 0.5 * np.concatenate([[1.0 + 0.0j], -radial]),
        "m": m_leg,
        "mbar": np.conjugate(m_leg),
    }


def _incident_cartesian_legs() -> dict[str, np.ndarray]:
    scale = 1.0 / math.sqrt(2.0)
    m_leg = scale * np.array([0.0, 1.0, 1.0j, 0.0], dtype=complex)
    return {
        "l": scale * np.array([1.0, 0.0, 0.0, 1.0], dtype=complex),
        "n": scale * np.array([1.0, 0.0, 0.0, -1.0], dtype=complex),
        "m": m_leg,
        "mbar": np.conjugate(m_leg),
    }


def _tensor_index(a: int, b: int, c: int, d: int) -> int:
    return ((a * 4 + b) * 4 + c) * 4 + d


def _weyl_mapping(
    weyl_scalars: WeylModeComponents | StrictNPScalars | Mapping[str, complex],
) -> Mapping[str, complex]:
    if isinstance(weyl_scalars, WeylModeComponents):
        return weyl_scalars.components
    if isinstance(weyl_scalars, StrictNPScalars):
        return weyl_scalars.as_mapping()
    missing = set(_SPIN_WEIGHTS) - set(weyl_scalars)
    if missing:
        raise ValueError(f"Missing Weyl scalar components: {sorted(missing)}")
    return weyl_scalars


def _validate_mode_indices(ell: int, m: int) -> None:
    if not isinstance(ell, int) or not isinstance(m, int):
        raise TypeError("ell and m must be integers.")
    if ell < 2:
        raise ValueError("Weyl modes require ell >= 2.")
    if abs(m) > ell:
        raise ValueError("abs(m) must be <= ell.")


def _sigma_l(ell: int) -> int:
    return (ell - 1) * ell * (ell + 1) * (ell + 2)


def _coerce_sector(sector: Sector | str) -> Sector:
    try:
        return sector if isinstance(sector, Sector) else Sector(sector)
    except ValueError as exc:
        raise ValueError("sector must be 'odd' or 'even'.") from exc


__all__ = [
    "FULL_NP_PSEUDOINVERSE_BRIDGE_NAME",
    "FULL_NP_PSEUDOINVERSE_BRIDGE_VALIDATED",
    "StrictNPScalars",
    "WeylModeComponents",
    "assemble_weyl_scalars",
    "compute_packaged_polarization_scalars",
    "transform_strict_np_weyl_to_incident_tetrad",
    "transform_weyl_to_incident_tetrad",
    "weyl_mode_components",
]
