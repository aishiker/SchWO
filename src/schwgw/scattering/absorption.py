"""Phase-6 mode absorption observables from independent raw flux routes.

This module deliberately keeps the horizon-current route separate from the
unitarity route.  In particular, ``gamma_flux`` is never inferred from the
complex S matrix.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ModeAbsorption:
    """Raw mode scattering and greybody observables in one normalization."""

    S: complex
    reflection_probability: float
    incident_flux: float
    outgoing_flux: float
    horizon_flux: float
    gamma_flux: float
    gamma_s: float
    flux_balance_residual: float
    log_gamma_flux: float | None
    log_gamma_s: float | None


def mode_absorption_from_raw(
    *,
    ell: int,
    A_in: complex,
    A_out: complex,
    incident_flux: float,
    outgoing_flux: float,
    horizon_flux: float,
) -> ModeAbsorption:
    """Build observables while preserving the direct horizon-flux route.

    The supplied fluxes are positive physical flux magnitudes obtained from
    separately recorded signed currents.  They are not reconstructed here.
    """

    values = (incident_flux, outgoing_flux, horizon_flux)
    if ell < 2 or A_in == 0 or not all(math.isfinite(value) for value in values):
        raise ValueError("invalid raw mode absorption operands")
    if any(value < 0.0 for value in values) or incident_flux == 0.0:
        raise ValueError("physical flux magnitudes must be nonnegative and F_in>0")
    S = ((-1) ** (ell + 1)) * A_out / A_in
    reflection = abs(S) ** 2
    gamma_flux = horizon_flux / incident_flux
    gamma_s = 1.0 - reflection
    balance = abs((outgoing_flux + horizon_flux - incident_flux) / incident_flux)
    return ModeAbsorption(
        S=complex(S),
        reflection_probability=float(reflection),
        incident_flux=float(incident_flux),
        outgoing_flux=float(outgoing_flux),
        horizon_flux=float(horizon_flux),
        gamma_flux=float(gamma_flux),
        gamma_s=float(gamma_s),
        flux_balance_residual=float(balance),
        log_gamma_flux=math.log(gamma_flux) if gamma_flux > 0.0 else None,
        log_gamma_s=math.log(gamma_s) if gamma_s > 0.0 else None,
    )
