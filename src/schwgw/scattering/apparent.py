"""Diagnostic apparent-polarization projections used by Li-Hou-Zhao Fig. 7.

These quantities are projections of the strict Newman-Penrose Weyl scalars
in the incident-aligned tetrad.  They are environmental/tetrad-dependent
diagnostics, not additional propagating degrees of freedom.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Mapping

from schwgw.scattering.weyl import StrictNPScalars


@dataclass(frozen=True)
class ApparentPolarizationResult:
    """Frequency-domain apparent strains and their second derivatives."""

    h_x: complex
    h_y: complex
    h_b: complex
    h_longitudinal: complex
    hddot_x: complex
    hddot_y: complex
    hddot_b: complex
    hddot_longitudinal: complex
    k: float
    diagnostics: Mapping[str, float]
    frame: str = "incident"
    physical_claim: bool = False

    def __post_init__(self) -> None:
        for name in (
            "h_x",
            "h_y",
            "h_b",
            "h_longitudinal",
            "hddot_x",
            "hddot_y",
            "hddot_b",
            "hddot_longitudinal",
        ):
            object.__setattr__(self, name, complex(getattr(self, name)))
        k_value = float(self.k)
        if not math.isfinite(k_value) or k_value <= 0.0:
            raise ValueError("Wave number k must be finite and positive.")
        object.__setattr__(self, "k", k_value)
        if self.frame != "incident":
            raise ValueError("Apparent polarizations require the incident tetrad.")
        if self.physical_claim is not False:
            raise ValueError("Apparent polarizations must remain diagnostic-only.")
        object.__setattr__(self, "diagnostics", MappingProxyType(dict(self.diagnostics)))


def apparent_polarization_acceleration_from_strict_np(
    strict_np_scalars: StrictNPScalars,
) -> tuple[complex, complex, complex, complex]:
    """Return complex continuations whose real parts reproduce paper Eq. (42).

    With the project Fourier convention ``exp(-i k t)``, the real parts obey

    ``ddot(h_x) = (Re Psi1 + Re Psi3)/2``,
    ``ddot(h_y) = (Im Psi1 - Im Psi3)/2``,
    ``ddot(h_b) = Re Psi2/2``, and ``ddot(h_L) = Re Psi2``.
    """

    _require_incident_strict_np(strict_np_scalars)
    psi1 = strict_np_scalars.psi1
    psi2 = strict_np_scalars.psi2
    psi3 = strict_np_scalars.psi3
    return (
        0.5 * (psi1 + psi3),
        -0.5j * (psi1 - psi3),
        0.5 * psi2,
        psi2,
    )


def apparent_polarizations_from_strict_np(
    k: float,
    strict_np_scalars: StrictNPScalars,
    *,
    diagnostics: Mapping[str, float] | None = None,
) -> ApparentPolarizationResult:
    """Project strict incident-frame NP scalars to Fig. 7 diagnostics."""

    k_value = float(k)
    if not math.isfinite(k_value) or k_value <= 0.0:
        raise ValueError("Wave number k must be finite and positive.")
    hddot_x, hddot_y, hddot_b, hddot_longitudinal = (
        apparent_polarization_acceleration_from_strict_np(strict_np_scalars)
    )
    scale = -(k_value**-2)
    return ApparentPolarizationResult(
        h_x=scale * hddot_x,
        h_y=scale * hddot_y,
        h_b=scale * hddot_b,
        h_longitudinal=scale * hddot_longitudinal,
        hddot_x=hddot_x,
        hddot_y=hddot_y,
        hddot_b=hddot_b,
        hddot_longitudinal=hddot_longitudinal,
        k=k_value,
        diagnostics={} if diagnostics is None else diagnostics,
    )


def _require_incident_strict_np(strict_np_scalars: StrictNPScalars) -> None:
    if not isinstance(strict_np_scalars, StrictNPScalars):
        raise TypeError("strict_np_scalars must be a StrictNPScalars instance.")
    if strict_np_scalars.frame != "incident":
        raise ValueError("strict_np_scalars must be in the incident frame.")
    for value in strict_np_scalars.as_mapping().values():
        if not math.isfinite(value.real) or not math.isfinite(value.imag):
            raise ValueError("strict_np_scalars must contain only finite values.")


__all__ = [
    "ApparentPolarizationResult",
    "apparent_polarization_acceleration_from_strict_np",
    "apparent_polarizations_from_strict_np",
]
