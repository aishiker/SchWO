"""Frozen Phase-6 V2 mode-level gauge-invariant asymptotic amplitudes.

The functions in this module are typed, deterministic, and free of filesystem
or solver effects.  They implement only the conventions frozen by the V2.0
contract.  In particular, the odd Li master is the Martel--Poisson RW
function; the CPM function is a distinct frequency-domain rescaling.
"""

from __future__ import annotations

from dataclasses import dataclass

import mpmath as mp


SECTORS = ("odd", "even")
SUPPORTED_M = (-2, 2)


class ModeAmplitudeError(ValueError):
    """Raised when a mode lies outside the frozen V2.1 structural domain."""


@dataclass(frozen=True)
class IncidentColumn:
    """One complex linear-polarization incident basis column."""

    name: str
    A_plus: mp.mpc
    A_cross: mp.mpc

    def __post_init__(self) -> None:
        if self.name not in {"plus", "cross"}:
            raise ModeAmplitudeError(f"unknown incident column: {self.name!r}")

    @property
    def A_L(self) -> mp.mpc:
        return (self.A_plus + 1j * self.A_cross) / mp.sqrt(2)

    @property
    def A_R(self) -> mp.mpc:
        return (self.A_plus - 1j * self.A_cross) / mp.sqrt(2)


@dataclass(frozen=True)
class RawRadialAmplitudes:
    """Raw radial coefficients reconstructed from frozen V1 evidence."""

    A_out_raw: mp.mpc
    S_l: mp.mpc
    A_in_raw: mp.mpc
    T_horizon_raw: mp.mpc
    A_in_closure_residual: mp.mpc


@dataclass(frozen=True)
class ModeAmplitudes:
    """Physical Li and Martel--Poisson amplitudes for one mode and column."""

    c_lm: mp.mpc
    normalization_factor: mp.mpc
    A_in_physical: mp.mpc
    A_out_total_physical: mp.mpc
    A_out_free_physical: mp.mpc
    A_out_scattered_physical: mp.mpc
    T_horizon_physical: mp.mpc
    identity_residual: mp.mpc
    li_master_name: str
    mp_master_name: str
    mp_factor: mp.mpc


def reconstruct_raw_amplitudes(
    *,
    ell: int,
    A_out_raw: mp.mpc,
    S_l: mp.mpc,
    log_abs_T_horizon: mp.mpf,
    phase_T_horizon: mp.mpf,
) -> RawRadialAmplitudes:
    """Apply the only V2.1-authorized reconstructions to frozen V1 fields."""

    if isinstance(ell, bool) or not isinstance(ell, int) or ell < 2:
        raise ModeAmplitudeError("ell must be an integer >= 2")
    if S_l == 0:
        raise ModeAmplitudeError("S_l must be nonzero to reconstruct A_in_raw")
    parity = mp.mpf(-1 if ell % 2 else 1)
    A_in_raw = -A_out_raw / (parity * S_l)
    if A_in_raw == 0:
        raise ModeAmplitudeError("reconstructed A_in_raw is zero")
    reconstructed_S = -A_out_raw / (parity * A_in_raw)
    closure = S_l - reconstructed_S
    T_horizon_raw = mp.exp(log_abs_T_horizon) * mp.exp(1j * phase_T_horizon)
    if T_horizon_raw == 0:
        raise ModeAmplitudeError(
            "arbitrary-precision horizon reconstruction underflowed"
        )
    return RawRadialAmplitudes(
        A_out_raw=A_out_raw,
        S_l=S_l,
        A_in_raw=A_in_raw,
        T_horizon_raw=T_horizon_raw,
        A_in_closure_residual=closure,
    )


def incident_master_coefficient(
    ell: int,
    m: int,
    sector: str,
    omega: mp.mpf,
    column: IncidentColumn,
) -> mp.mpc:
    """Return the frozen Li incident coefficient ``c_lm^p``."""

    if isinstance(ell, bool) or not isinstance(ell, int) or ell < 2:
        raise ModeAmplitudeError("ell must be an integer >= 2")
    if m not in SUPPORTED_M:
        raise ModeAmplitudeError("V2.1 supports only m=-2,+2")
    if sector not in SECTORS:
        raise ModeAmplitudeError(f"unknown sector: {sector!r}")
    if omega <= 0:
        raise ModeAmplitudeError("omega must be positive")
    sigma_l = mp.mpf((ell - 1) * ell * (ell + 1) * (ell + 2))
    prefactor = (1j**ell) * mp.sqrt(2 * mp.pi * (2 * ell + 1) / sigma_l)
    if m == -2:
        A_plus_lm = prefactor * column.A_L
        A_minus_lm = prefactor * column.A_L
    else:
        A_plus_lm = prefactor * column.A_R
        A_minus_lm = -prefactor * column.A_R
    if sector == "odd":
        return -(1j ** (ell + 1)) * A_minus_lm / 2
    return (1j ** (ell + 1)) * A_plus_lm / omega


def build_mode_amplitudes(
    *,
    ell: int,
    m: int,
    sector: str,
    omega: mp.mpf,
    column: IncidentColumn,
    raw: RawRadialAmplitudes,
) -> ModeAmplitudes:
    """Apply the frozen V2.0 physical normalization and decomposition."""

    c_lm = incident_master_coefficient(ell, m, sector, omega, column)
    normalization = c_lm / raw.A_in_raw
    parity = mp.mpf(-1 if ell % 2 else 1)
    total = c_lm * raw.A_out_raw / raw.A_in_raw
    free = -parity * c_lm
    scattered = c_lm * (raw.A_out_raw / raw.A_in_raw + parity)
    horizon = c_lm * raw.T_horizon_raw / raw.A_in_raw
    residual = total - (free + scattered)
    if sector == "even":
        li_name = "psi_Li_even"
        mp_name = "Psi_ZM"
        mp_factor = mp.mpc(1)
    else:
        li_name = "psi_Li_odd=Psi_RW"
        mp_name = "Psi_CPM"
        mp_factor = 2j / omega
    return ModeAmplitudes(
        c_lm=c_lm,
        normalization_factor=normalization,
        A_in_physical=c_lm,
        A_out_total_physical=total,
        A_out_free_physical=free,
        A_out_scattered_physical=scattered,
        T_horizon_physical=horizon,
        identity_residual=residual,
        li_master_name=li_name,
        mp_master_name=mp_name,
        mp_factor=mp_factor,
    )


__all__ = [
    "IncidentColumn",
    "ModeAmplitudeError",
    "ModeAmplitudes",
    "RawRadialAmplitudes",
    "build_mode_amplitudes",
    "incident_master_coefficient",
    "reconstruct_raw_amplitudes",
]
