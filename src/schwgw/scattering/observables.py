from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class PolarizationResult:
    """Finite-radius polarization observable assembled from Weyl scalars."""

    h_plus: complex
    h_cross: complex
    psi0_hat: complex
    psi4_hat: complex
    lmax: int
    diagnostics: Mapping[str, float]
    hddot_plus: complex = 0.0j
    hddot_cross: complex = 0.0j

    def __post_init__(self) -> None:
        object.__setattr__(self, "h_plus", complex(self.h_plus))
        object.__setattr__(self, "h_cross", complex(self.h_cross))
        object.__setattr__(self, "psi0_hat", complex(self.psi0_hat))
        object.__setattr__(self, "psi4_hat", complex(self.psi4_hat))
        object.__setattr__(self, "lmax", int(self.lmax))
        object.__setattr__(self, "diagnostics", MappingProxyType(dict(self.diagnostics)))
        object.__setattr__(self, "hddot_plus", complex(self.hddot_plus))
        object.__setattr__(self, "hddot_cross", complex(self.hddot_cross))


@dataclass(frozen=True)
class ElectricTidalComponents:
    """Incident-frame electric tidal components used by Route B packaging."""

    E_xx: complex
    E_xy: complex

    def __post_init__(self) -> None:
        object.__setattr__(self, "E_xx", complex(self.E_xx))
        object.__setattr__(self, "E_xy", complex(self.E_xy))


@dataclass(frozen=True)
class PackagedPolarizationScalars:
    """Positive-frequency packaged scalars for polarization recovery.

    These are not strict Newman-Penrose Weyl scalars.  They encode the Route B
    tidal projections as ``Psi0_pack/Psi4_pack``.
    """

    psi0_pack: complex
    psi4_pack: complex

    def __post_init__(self) -> None:
        object.__setattr__(self, "psi0_pack", complex(self.psi0_pack))
        object.__setattr__(self, "psi4_pack", complex(self.psi4_pack))


def package_electric_tidal_components(
    tidal_components: ElectricTidalComponents,
) -> PackagedPolarizationScalars:
    """Return Route B packaged scalars from incident-frame tidal components."""

    if not isinstance(tidal_components, ElectricTidalComponents):
        raise TypeError("tidal_components must be an ElectricTidalComponents instance.")
    return PackagedPolarizationScalars(
        psi0_pack=-tidal_components.E_xx - 1.0j * tidal_components.E_xy,
        psi4_pack=-tidal_components.E_xx + 1.0j * tidal_components.E_xy,
    )


def packaged_scalars_to_mapping(
    packaged_scalars: PackagedPolarizationScalars,
) -> dict[str, complex]:
    """Return a compatibility mapping for explicitly packaged scalars."""

    if not isinstance(packaged_scalars, PackagedPolarizationScalars):
        raise TypeError("packaged_scalars must be a PackagedPolarizationScalars instance.")
    return {
        "Psi0": packaged_scalars.psi0_pack,
        "Psi4": packaged_scalars.psi4_pack,
    }


def polarization_acceleration_from_packaged_scalars(
    packaged_scalars: PackagedPolarizationScalars,
) -> tuple[complex, complex]:
    """Return Fourier amplitudes of ``ddot h_+`` and ``ddot h_x``."""

    if not isinstance(packaged_scalars, PackagedPolarizationScalars):
        raise TypeError("packaged_scalars must be a PackagedPolarizationScalars instance.")
    psi0 = packaged_scalars.psi0_pack
    psi4 = packaged_scalars.psi4_pack
    return psi4 + psi0, 1.0j * (psi4 - psi0)


def polarization_from_packaged_scalars(
    k: float,
    packaged_scalars: PackagedPolarizationScalars,
) -> tuple[complex, complex]:
    """Return ``(h_+, h_x)`` from project packaged polarization scalars."""

    k_value = float(k)
    if k_value <= 0.0:
        raise ValueError("Wave number k must be positive.")

    hddot_plus, hddot_cross = polarization_acceleration_from_packaged_scalars(
        packaged_scalars
    )
    return -hddot_plus / k_value**2, -hddot_cross / k_value**2


def polarization_acceleration_from_weyl(
    psi0_hat: complex,
    psi4_hat: complex,
) -> tuple[complex, complex]:
    """Compatibility wrapper for packaged scalar inputs.

    ``psi0_hat`` and ``psi4_hat`` must be project packaged scalars
    ``Psi0_pack/Psi4_pack``, not raw strict NP scalars.
    """

    return polarization_acceleration_from_packaged_scalars(
        PackagedPolarizationScalars(
            psi0_pack=psi0_hat,
            psi4_pack=psi4_hat,
        )
    )


def polarization_from_weyl(
    k: float,
    psi0_hat: complex,
    psi4_hat: complex,
) -> tuple[complex, complex]:
    """Compatibility wrapper for packaged polarization scalars.

    ``psi0_hat`` and ``psi4_hat`` are project packaged scalars
    ``Psi0_pack/Psi4_pack``. They must not be raw strict NP
    ``Psi0_NP/Psi4_NP`` tetrad contractions.

    Convention:
    ``h_+ = -(hat(Psi4) + hat(Psi0)) / k^2`` and
    ``h_x = -i (hat(Psi4) - hat(Psi0)) / k^2``.
    """

    return polarization_from_packaged_scalars(
        k,
        PackagedPolarizationScalars(
            psi0_pack=psi0_hat,
            psi4_pack=psi4_hat,
        ),
    )


__all__ = [
    "ElectricTidalComponents",
    "PackagedPolarizationScalars",
    "PolarizationResult",
    "package_electric_tidal_components",
    "packaged_scalars_to_mapping",
    "polarization_acceleration_from_packaged_scalars",
    "polarization_acceleration_from_weyl",
    "polarization_from_packaged_scalars",
    "polarization_from_weyl",
]
