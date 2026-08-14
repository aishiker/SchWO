"""Typed adapters for the isolated legacy scalar-master diagnostic path."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeVar

import numpy as np

from schwgw.backgrounds.base import StaticSphericalBackground
from schwgw.numerics import BoundaryConfig
from schwgw.perturbations import Sector
from schwgw.scattering.contracts import ChannelSpec, ModeKey
from schwgw.waves.incident import IncidentPlaneGW


_ResultT = TypeVar("_ResultT")
_RadialSolver = Callable[
    [Sector, int, float, StaticSphericalBackground, BoundaryConfig | None],
    object,
]


LEGACY_ODD_CHANNEL = ChannelSpec(
    name="legacy_rwz_odd",
    field_spin=2,
    polarization="legacy_tensor_diagnostic",
    parity="odd",
    radial_structure="scalar",
    component_names=("master",),
    physical_claim=False,
)
LEGACY_EVEN_CHANNEL = ChannelSpec(
    name="legacy_rwz_even",
    field_spin=2,
    polarization="legacy_tensor_diagnostic",
    parity="even",
    radial_structure="scalar",
    component_names=("master",),
    physical_claim=False,
)


@dataclass(frozen=True)
class LegacyIncidentSourceAdapter:
    """Expose ``IncidentPlaneGW`` only for legacy diagnostic equivalence."""

    wave: IncidentPlaneGW
    name: str = "legacy_incident_plane_gw_plus_z"
    physical_claim: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.wave, IncidentPlaneGW):
            raise TypeError("wave must be an IncidentPlaneGW.")
        if self.physical_claim is not False:
            raise ValueError("legacy adapters cannot carry physical_claim=True.")

    def supported_m_values(self, ell: int) -> tuple[int, ...]:
        if not isinstance(ell, int):
            raise TypeError("ell must be an integer.")
        if ell < 2:
            raise ValueError("legacy radiative modes require ell >= 2.")
        return (-2, 2)

    def coefficient(self, sector: Sector, ell: int, m: int) -> complex:
        try:
            sector_enum = sector if isinstance(sector, Sector) else Sector(sector)
        except ValueError as error:
            raise ValueError("sector must be 'odd' or 'even'.") from error
        if sector_enum is Sector.ODD:
            return self.wave.c_lm_odd(ell, m)
        return self.wave.c_lm_even(ell, m)

    def amplitude(self, mode: ModeKey, channel: ChannelSpec) -> np.ndarray:
        if not isinstance(mode, ModeKey):
            raise TypeError("mode must be a ModeKey.")
        if not isinstance(channel, ChannelSpec):
            raise TypeError("channel must be a ChannelSpec.")
        if mode.frequency != self.wave.k:
            raise ValueError("mode frequency does not match the incident wave.")
        if channel not in (LEGACY_ODD_CHANNEL, LEGACY_EVEN_CHANNEL):
            raise ValueError(
                "legacy source accepts only the two frozen legacy RWZ channels."
            )
        if mode.channel != channel.name:
            raise ValueError("mode channel does not match ChannelSpec.name.")
        sector = Sector.ODD if channel == LEGACY_ODD_CHANNEL else Sector.EVEN
        return np.array([self.coefficient(sector, mode.ell, mode.m)], dtype=np.complex128)


@dataclass(frozen=True)
class LegacyScalarRWZAdapter:
    """Diagnostic-only facade for the old scalar RW/Zerilli observable path."""

    name: str = "legacy_schwarzschild_scalar_rwz_diagnostic"
    physical_claim: bool = False

    def __post_init__(self) -> None:
        if self.physical_claim is not False:
            raise ValueError("legacy adapters cannot carry physical_claim=True.")

    def incident_source(
        self,
        k: float,
        A_plus: complex,
        A_cross: complex,
    ) -> LegacyIncidentSourceAdapter:
        return LegacyIncidentSourceAdapter(IncidentPlaneGW(k, A_plus, A_cross))

    def compute_polarization(
        self,
        *,
        implementation: Callable[..., _ResultT],
        background: StaticSphericalBackground,
        k: float,
        r: float,
        theta: float,
        phi: float,
        A_plus: complex,
        A_cross: complex,
        lmax: int,
        boundary_config: BoundaryConfig | None,
        radial_solver: _RadialSolver,
    ) -> _ResultT:
        if not callable(implementation):
            raise TypeError("implementation must be callable.")
        if not callable(radial_solver):
            raise TypeError("radial_solver must be callable.")
        return implementation(
            background=background,
            k=k,
            r=r,
            theta=theta,
            phi=phi,
            lmax=lmax,
            boundary_config=boundary_config,
            radial_solver=radial_solver,
            mode_source=self.incident_source(k, A_plus, A_cross),
        )


__all__ = [
    "LEGACY_EVEN_CHANNEL",
    "LEGACY_ODD_CHANNEL",
    "LegacyIncidentSourceAdapter",
    "LegacyScalarRWZAdapter",
]
