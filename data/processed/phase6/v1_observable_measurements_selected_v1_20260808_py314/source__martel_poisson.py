"""Martel--Poisson gauge-invariant asymptotic waveform and flux formulas.

The functions in this module implement Eqs. (6.14)--(6.16) and (7.4)--(7.5)
of Martel & Poisson (2005) in the frozen SchWO angular convention.  The
vacuum, radiative ``ell>=2`` bridge from the project's historical Li
normalization to the Zerilli--Moncrief / Cunningham--Price--Moncrief
variables is explicit and convention-qualified below.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal, Sequence

from schwgw.angular import spin_weighted_sph_harm
from schwgw.perturbations import lambda_parameter


Boundary = Literal["future_null_infinity", "event_horizon"]
AmplitudeConvention = Literal["real_field_peak", "complex_rms"]

MARTEL_POISSON_SOURCE = (
    "Martel & Poisson, Phys. Rev. D 71, 104003 (2005), Eqs. (6.14)-(6.16), (7.4)-(7.5)"
)
LI_TO_MP_BRIDGE_SOURCE = (
    "Li-Hou-Zhao historical RW-gauge reconstruction combined with "
    "Martel-Poisson Eqs. (3.2), (4.23), and vacuum Eq. (5.18)"
)


@dataclass(frozen=True)
class MartelPoissonMasterMode:
    """One frequency-domain gauge-invariant Schwarzschild master mode."""

    ell: int
    m: int
    psi_even: complex = 0.0j
    psi_odd: complex = 0.0j

    def __post_init__(self) -> None:
        if isinstance(self.ell, bool) or not isinstance(self.ell, int) or self.ell < 2:
            raise ValueError("ell must be an integer >= 2")
        if (
            isinstance(self.m, bool)
            or not isinstance(self.m, int)
            or abs(self.m) > self.ell
        ):
            raise ValueError("m must be an integer with abs(m) <= ell")
        for name in ("psi_even", "psi_odd"):
            value = complex(getattr(self, name))
            if not _finite_complex(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)


@dataclass(frozen=True)
class MartelPoissonStrain:
    """Complex Fourier amplitudes of the two asymptotic polarizations."""

    h_plus: complex
    h_cross: complex
    boundary: Boundary
    areal_scale: float
    source: str = MARTEL_POISSON_SOURCE
    master_normalization: str = "Zerilli-Moncrief even; Cunningham-Price-Moncrief odd"

    def __post_init__(self) -> None:
        if not _finite_complex(complex(self.h_plus)) or not _finite_complex(
            complex(self.h_cross)
        ):
            raise ValueError("strain amplitudes must be finite")
        _validate_boundary(self.boundary)
        if not math.isfinite(float(self.areal_scale)) or self.areal_scale <= 0.0:
            raise ValueError("areal_scale must be finite and positive")


@dataclass(frozen=True)
class MartelPoissonFlux:
    """Angle-integrated energy flux for explicitly normalized master modes."""

    value: float
    boundary: Boundary
    time_average_factor: float
    amplitude_convention: str
    source: str = MARTEL_POISSON_SOURCE


@dataclass(frozen=True)
class MasterNormalizationBridge:
    """Auditable Li-master to Martel--Poisson normalization record."""

    mode: MartelPoissonMasterMode
    k: float
    li_psi_even: complex
    li_psi_odd: complex
    even_formula: str = "Psi_ZM = psi_Li_even"
    odd_formula: str = "Psi_CPM = (2 i / k) psi_Li_odd"
    angular_sign: str = "Li odd vector harmonic = -X_A^(MP)"
    assumptions: str = (
        "vacuum ell>=2; exp(-i k t); identical unit-normalized "
        "Condon-Shortley scalar harmonics; Schwarzschild RW gauge"
    )
    source: str = LI_TO_MP_BRIDGE_SOURCE


def li_master_to_martel_poisson(
    *,
    ell: int,
    m: int,
    k: float,
    psi_li_even: complex = 0.0j,
    psi_li_odd: complex = 0.0j,
) -> MasterNormalizationBridge:
    """Convert the historical project masters to MP ZM/CPM variables.

    In the frozen ``exp(-i k t)`` convention the even project variable is the
    Zerilli--Moncrief function itself.  Li's odd vector harmonic is the
    negative of Martel--Poisson's ``X_A``; consequently the project odd master
    equals MP's Regge--Wheeler function.  The vacuum identity
    ``Psi_RW=(1/2) partial_t Psi_CPM`` then gives
    ``Psi_CPM=(2 i/k) psi_Li_odd``.  The same factor applies to finite-radius,
    incoming, outgoing and horizon amplitudes.  The separate odd sign at the
    event horizon in MP Eq. (7.4) belongs in waveform assembly, not here.
    """

    k_value = float(k)
    if not math.isfinite(k_value) or k_value <= 0.0:
        raise ValueError("k must be finite and positive")
    even = complex(psi_li_even)
    odd = complex(psi_li_odd)
    if not _finite_complex(even) or not _finite_complex(odd):
        raise ValueError("Li master amplitudes must be finite")
    mode = MartelPoissonMasterMode(
        ell=ell,
        m=m,
        psi_even=even,
        psi_odd=2.0j * odd / k_value,
    )
    return MasterNormalizationBridge(
        mode=mode,
        k=k_value,
        li_psi_even=even,
        li_psi_odd=odd,
    )


def li_even_master_from_rw_metric(
    *,
    ell: int,
    k: float,
    mass: float,
    r: float,
    T0: complex,
    Rt: complex,
) -> complex:
    """Recover the historical even master from its RW-gauge metric fields."""

    radius, mass_value, k_value = _bridge_geometry(ell, k, mass, r)
    f = 1.0 - 2.0 * mass_value / radius
    capital_lambda = lambda_parameter(ell) + 3.0 * mass_value / radius
    value = complex(T0) / radius + f * complex(Rt) / (1.0j * k_value)
    value /= capital_lambda
    if not _finite_complex(value):
        raise ValueError("even RW-gauge metric amplitudes must be finite")
    return complex(value)


def martel_poisson_even_master_from_rw_metric(
    *,
    ell: int,
    mass: float,
    r: float,
    T0: complex,
    L0: complex,
    d_T0_over_r2_dr: complex,
) -> complex:
    """Evaluate MP Eq. (4.23) in Schwarzschild RW gauge.

    Project components map as ``K=T0/r^2`` and ``h_rr=L0``.  Supplying the
    derivative explicitly makes the independent reconstruction/ODE route
    visible to evidence producers instead of silently reusing the input
    master amplitude.
    """

    radius, mass_value, _ = _bridge_geometry(ell, 1.0, mass, r)
    lambda_ = lambda_parameter(ell)
    capital_lambda = lambda_ + 3.0 * mass_value / radius
    f = 1.0 - 2.0 * mass_value / radius
    K = complex(T0) / radius**2
    value = (
        radius
        / (lambda_ + 1.0)
        * (
            K
            + f / capital_lambda * (f * complex(L0) - radius * complex(d_T0_over_r2_dr))
        )
    )
    if not _finite_complex(value):
        raise ValueError("even RW-gauge metric jet must be finite")
    return complex(value)


def martel_poisson_odd_master_from_rw_metric(
    *,
    ell: int,
    k: float,
    mass: float,
    r: float,
    Bt: complex,
    B1: complex,
    dBt_dr: complex,
) -> complex:
    """Evaluate the CPM invariant from Li-sign RW-gauge odd components.

    With Li's vector harmonic equal to ``-X_A^(MP)``, MP Eq. (5.13) becomes
    ``Psi_CPM=r/lambda*(-d_r Bt-i k B1+2 Bt/r)``.
    """

    radius, _, k_value = _bridge_geometry(ell, k, mass, r)
    value = (
        radius
        / lambda_parameter(ell)
        * (-complex(dBt_dr) - 1.0j * k_value * complex(B1) + 2.0 * complex(Bt) / radius)
    )
    if not _finite_complex(value):
        raise ValueError("odd RW-gauge metric jet must be finite")
    return complex(value)


def _bridge_geometry(
    ell: int,
    k: float,
    mass: float,
    r: float,
) -> tuple[float, float, float]:
    lambda_parameter(ell)
    k_value = float(k)
    mass_value = float(mass)
    radius = float(r)
    if not all(math.isfinite(value) for value in (k_value, mass_value, radius)):
        raise ValueError("bridge geometry must be finite")
    if k_value <= 0.0 or mass_value <= 0.0 or radius <= 2.0 * mass_value:
        raise ValueError("bridge requires k>0, M>0, and r>2M")
    return radius, mass_value, k_value


def sigma_l(ell: int) -> int:
    """Return ``(ell-1) ell (ell+1) (ell+2)`` for a radiative mode."""

    if isinstance(ell, bool) or not isinstance(ell, int) or ell < 2:
        raise ValueError("ell must be an integer >= 2")
    return (ell - 1) * ell * (ell + 1) * (ell + 2)


def martel_poisson_angular_operators(
    ell: int,
    m: int,
    theta: float,
    phi: float,
) -> tuple[complex, complex]:
    """Return the angular factors ``A_lm`` and ``B_lm`` of Eqs. (6.14)-(6.15).

    ``A = [d_theta^2 + ell(ell+1)/2]Y`` and
    ``B = i m csc(theta)[d_theta-cot(theta)]Y``.
    The coordinate-axis limits are deliberately outside this routine; Phase-6
    axis evidence must use a separately recorded limit ladder.
    """

    sigma_l(ell)
    if isinstance(m, bool) or not isinstance(m, int) or abs(m) > ell:
        raise ValueError("m must be an integer with abs(m) <= ell")
    theta_value = float(theta)
    phi_value = float(phi)
    if not math.isfinite(theta_value) or not 0.0 < theta_value < math.pi:
        raise ValueError("theta must lie strictly inside (0, pi)")
    if not math.isfinite(phi_value):
        raise ValueError("phi must be finite")
    prefactor = 0.5 * math.sqrt(sigma_l(ell)) * (-1) ** m
    minus_two = prefactor * complex(
        spin_weighted_sph_harm(-2, ell, m, theta_value, phi_value)
    )
    plus_two = prefactor * complex(
        spin_weighted_sph_harm(2, ell, m, theta_value, phi_value)
    )
    angular_even = 0.5 * (minus_two + plus_two)
    angular_odd = (plus_two - minus_two) / (2.0j)
    if not _finite_complex(angular_even) or not _finite_complex(angular_odd):
        raise RuntimeError("spin-2 angular operator evaluation is non-finite")
    return complex(angular_even), complex(angular_odd)


def martel_poisson_strain(
    modes: Sequence[MartelPoissonMasterMode],
    *,
    areal_scale: float,
    theta: float,
    phi: float,
    boundary: Boundary,
    mass: float | None = None,
) -> MartelPoissonStrain:
    """Assemble ``h_plus`` and ``h_cross`` from gauge-invariant master modes.

    At future null infinity the odd contribution has the sign in Eqs.
    (6.14)-(6.15).  At the event horizon Eq. (7.4) reverses the odd-parity
    radiative field.  ``areal_scale`` is ``r`` at infinity and ``2M`` on the
    horizon; it is explicit so no finite-radius interpretation is implied.
    """

    if not isinstance(modes, Sequence) or not modes:
        raise ValueError("modes must be a non-empty sequence")
    scale = float(areal_scale)
    if not math.isfinite(scale) or scale <= 0.0:
        raise ValueError("areal_scale must be finite and positive")
    _validate_boundary(boundary)
    _validate_unique_modes(modes)
    if boundary == "event_horizon":
        if mass is None:
            raise ValueError("event_horizon strain requires explicit mass")
        mass_value = float(mass)
        if not math.isfinite(mass_value) or mass_value <= 0.0:
            raise ValueError("mass must be finite and positive")
        if not math.isclose(
            scale,
            2.0 * mass_value,
            rel_tol=16.0 * float.fromhex("0x1.0p-52"),
            abs_tol=0.0,
        ):
            raise ValueError("event_horizon areal_scale must equal 2M")
    odd_field_sign = 1.0 if boundary == "future_null_infinity" else -1.0
    h_plus = 0.0j
    h_cross = 0.0j
    for mode in modes:
        if not isinstance(mode, MartelPoissonMasterMode):
            raise TypeError("every mode must be a MartelPoissonMasterMode")
        angular_even, angular_odd = martel_poisson_angular_operators(
            mode.ell,
            mode.m,
            theta,
            phi,
        )
        h_plus += mode.psi_even * angular_even
        h_plus -= odd_field_sign * mode.psi_odd * angular_odd
        h_cross += mode.psi_even * angular_odd
        h_cross += odd_field_sign * mode.psi_odd * angular_even
    if not _finite_complex(h_plus) or not _finite_complex(h_cross):
        raise RuntimeError("Martel-Poisson strain assembly is non-finite")
    return MartelPoissonStrain(
        h_plus=h_plus / scale,
        h_cross=h_cross / scale,
        boundary=boundary,
        areal_scale=scale,
    )


def martel_poisson_flux_from_time_derivatives(
    modes: Sequence[MartelPoissonMasterMode],
    *,
    boundary: Boundary,
    time_average_factor: float,
    amplitude_convention: str,
) -> MartelPoissonFlux:
    """Evaluate the MP flux when mode fields contain time-derivative amplitudes.

    The caller must provide the factor implementing its averaging convention.
    For example, a real field represented by a complex peak amplitude uses
    ``time_average_factor=1/2``.  This explicit argument prevents an unnoticed
    factor-of-two convention change.
    """

    if not isinstance(modes, Sequence) or not modes:
        raise ValueError("modes must be a non-empty sequence")
    _validate_boundary(boundary)
    _validate_unique_modes(modes)
    average = float(time_average_factor)
    if not math.isfinite(average) or average <= 0.0:
        raise ValueError("time_average_factor must be finite and positive")
    if not isinstance(amplitude_convention, str) or not amplitude_convention.strip():
        raise ValueError("amplitude_convention must be a non-empty string")
    weighted_sum = 0.0
    for mode in modes:
        if not isinstance(mode, MartelPoissonMasterMode):
            raise TypeError("every mode must be a MartelPoissonMasterMode")
        weighted_sum += sigma_l(mode.ell) * (
            abs(mode.psi_even) ** 2 + abs(mode.psi_odd) ** 2
        )
    value = average * weighted_sum / (64.0 * math.pi)
    return MartelPoissonFlux(
        value=float(value),
        boundary=boundary,
        time_average_factor=average,
        amplitude_convention=amplitude_convention,
    )


def monochromatic_martel_poisson_flux(
    modes: Sequence[MartelPoissonMasterMode],
    *,
    k: float,
    boundary: Boundary,
    amplitude_convention: AmplitudeConvention,
) -> MartelPoissonFlux:
    """Return the MP energy flux for ``exp(-ikt)`` master amplitudes."""

    k_value = float(k)
    if not math.isfinite(k_value) or k_value <= 0.0:
        raise ValueError("k must be finite and positive")
    if amplitude_convention not in ("real_field_peak", "complex_rms"):
        raise ValueError("unsupported amplitude_convention")
    derivative_modes = tuple(
        MartelPoissonMasterMode(
            ell=mode.ell,
            m=mode.m,
            psi_even=-1.0j * k_value * mode.psi_even,
            psi_odd=-1.0j * k_value * mode.psi_odd,
        )
        for mode in modes
    )
    average = 0.5 if amplitude_convention == "real_field_peak" else 1.0
    return martel_poisson_flux_from_time_derivatives(
        derivative_modes,
        boundary=boundary,
        time_average_factor=average,
        amplitude_convention=amplitude_convention,
    )


def _validate_boundary(boundary: str) -> None:
    if boundary not in ("future_null_infinity", "event_horizon"):
        raise ValueError("boundary must be future_null_infinity or event_horizon")


def _validate_unique_modes(modes: Sequence[MartelPoissonMasterMode]) -> None:
    keys: set[tuple[int, int]] = set()
    for mode in modes:
        if not isinstance(mode, MartelPoissonMasterMode):
            raise TypeError("every mode must be a MartelPoissonMasterMode")
        key = (mode.ell, mode.m)
        if key in keys:
            raise ValueError("duplicate (ell,m) master mode")
        keys.add(key)


def _finite_complex(value: complex) -> bool:
    return math.isfinite(value.real) and math.isfinite(value.imag)


__all__ = [
    "LI_TO_MP_BRIDGE_SOURCE",
    "MARTEL_POISSON_SOURCE",
    "MasterNormalizationBridge",
    "MartelPoissonFlux",
    "MartelPoissonMasterMode",
    "MartelPoissonStrain",
    "martel_poisson_angular_operators",
    "martel_poisson_flux_from_time_derivatives",
    "martel_poisson_strain",
    "li_master_to_martel_poisson",
    "li_even_master_from_rw_metric",
    "martel_poisson_even_master_from_rw_metric",
    "martel_poisson_odd_master_from_rw_metric",
    "monochromatic_martel_poisson_flux",
    "sigma_l",
]
