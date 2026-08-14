from __future__ import annotations

from dataclasses import dataclass
import importlib
from types import MappingProxyType
from typing import Mapping

import numpy as np


@dataclass(frozen=True)
class RayleighSommerfeldPhaseScreenResult:
    """Scalar RS-I propagation of the point-mass thin-lens phase screen.

    This is a diagnostic model, not a replacement for Schwarzschild spin-2
    scattering.  The boundary field on the lens plane is fixed to

    ``U_L(rho) = (rho / rho_E)**(-4j*kM)``,

    and is propagated with the exact outgoing angular-spectrum transfer
    function.  It therefore keeps the Rayleigh--Sommerfeld obliquity,
    spherical-distance, and evanescent contributions that are discarded by
    the paraxial Fresnel integral.
    """

    kM: np.ndarray
    transverse_x_over_M: np.ndarray
    propagation_z_over_M: np.ndarray
    F_complex: np.ndarray
    F_propagating: np.ndarray
    F_evanescent: np.ndarray
    abs_F: np.ndarray
    arg_F_principal: np.ndarray
    valid_mask: np.ndarray
    metadata: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "kM", np.asarray(self.kM, dtype=float))
        object.__setattr__(
            self,
            "transverse_x_over_M",
            np.asarray(self.transverse_x_over_M, dtype=float),
        )
        object.__setattr__(
            self,
            "propagation_z_over_M",
            np.asarray(self.propagation_z_over_M, dtype=float),
        )
        object.__setattr__(
            self, "F_complex", np.asarray(self.F_complex, dtype=complex)
        )
        object.__setattr__(
            self, "F_propagating", np.asarray(self.F_propagating, dtype=complex)
        )
        object.__setattr__(
            self, "F_evanescent", np.asarray(self.F_evanescent, dtype=complex)
        )
        object.__setattr__(self, "abs_F", np.asarray(self.abs_F, dtype=float))
        object.__setattr__(
            self, "arg_F_principal", np.asarray(self.arg_F_principal, dtype=float)
        )
        object.__setattr__(
            self, "valid_mask", np.asarray(self.valid_mask, dtype=bool)
        )
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


def compute_rayleigh_sommerfeld_point_mass_phase_screen(
    *,
    kM_values: np.ndarray,
    transverse_x_over_M: np.ndarray,
    propagation_z_over_M: np.ndarray,
    dps: int = 40,
    propagating_decay_target: float = 100.0,
    evanescent_decay_target: float = 120.0,
) -> RayleighSommerfeldPhaseScreenResult:
    r"""Propagate a scalar point-mass phase screen with RS-I.

    The source is a unit plane wave incident normally on a planar phase
    screen.  In units ``M=1`` the lens-plane field is

    .. math::

       U_L(\rho)=\left(\rho/\sqrt{4z}\right)^{-4 i kM}.

    The exact forward angular-spectrum propagator is used:

    .. math::

       \exp\!\left[i z\sqrt{k^2-q^2}\right]\quad(q\leq k),

    with the outgoing evanescent branch for ``q > k``.  The result is divided
    by the unlensed plane wave ``exp(i k z)``.  The radial Hankel transform of
    the power-law phase screen is analytic, reducing the computation to two
    one-dimensional quadratures.

    This construction supplies mathematically consistent Dirichlet data for
    RS-I, but it retains the weak-field, scalar, infinitesimally thin phase
    screen.  In particular, it does not model the strong-field core or spin-2
    polarization transport.
    """

    kM = _positive_vector(kM_values, name="kM_values")
    transverse = _finite_vector(
        transverse_x_over_M, name="transverse_x_over_M"
    )
    distance = _positive_vector(
        propagation_z_over_M, name="propagation_z_over_M"
    )
    if transverse.size != distance.size:
        raise ValueError(
            "transverse_x_over_M and propagation_z_over_M must have equal size."
        )

    precision = int(dps)
    if precision != dps or precision < 30:
        raise ValueError("dps must be an integer greater than or equal to 30.")
    propagating_target = float(propagating_decay_target)
    if not np.isfinite(propagating_target) or propagating_target < 60.0:
        raise ValueError(
            "propagating_decay_target must be finite and at least 60."
        )
    evanescent_target = float(evanescent_decay_target)
    if not np.isfinite(evanescent_target) or evanescent_target < 50.0:
        raise ValueError("evanescent_decay_target must be finite and at least 50.")

    mp = _load_mpmath()
    propagating = np.empty((kM.size, transverse.size), dtype=np.complex128)
    evanescent = np.empty_like(propagating)
    with mp.workdps(precision):
        for frequency_index, kM_value in enumerate(kM):
            for point_index, (x_value, z_value) in enumerate(
                zip(transverse, distance, strict=True)
            ):
                propagating_value, evanescent_value = _angular_spectrum_point(
                    mp=mp,
                    kM=float(kM_value),
                    transverse_x_over_M=abs(float(x_value)),
                    propagation_z_over_M=float(z_value),
                    propagating_decay_target=propagating_target,
                    evanescent_decay_target=evanescent_target,
                )
                propagating[frequency_index, point_index] = complex(
                    propagating_value
                )
                evanescent[frequency_index, point_index] = complex(
                    evanescent_value
                )

    values = propagating + evanescent
    valid = np.isfinite(values.real) & np.isfinite(values.imag)
    if not valid.all():
        bad = np.argwhere(~valid).tolist()
        raise RuntimeError(
            f"Rayleigh--Sommerfeld backend returned non-finite values at {bad}."
        )

    metadata = {
        "baseline": {
            "kind": "rayleigh_sommerfeld_I_point_mass_phase_screen_diagnostic",
            "equation": (
                "exact outgoing angular spectrum of "
                "U_L(rho)=(rho/sqrt(4 M z))^(-4 i kM)"
            ),
            "boundary_data": "Dirichlet field on an infinite planar phase screen",
            "source": "unit plane wave incident normally from infinity",
            "normalization": "divide by exp(i k z)",
            "propagating_branch": "sqrt(k^2-q^2) >= 0",
            "evanescent_branch": "+i sqrt(q^2-k^2)",
            "fourier": "exp(-i k t)",
            "scalar_only": True,
            "thin_lens": True,
            "weak_field_phase_screen": True,
            "strong_field_core_resolved": False,
            "spin2_polarization_transport": False,
            "comparison_only": True,
            "not_strict_li_reproduction": True,
            "backend": "mpmath",
            "backend_version": str(mp.__version__),
            "dps": precision,
            "propagating_tail": (
                "analytic Abel integral after subtracting the asymptotic "
                "plane-wave term"
            ),
            "propagating_decay_target": propagating_target,
            "evanescent_decay_target": evanescent_target,
        }
    }
    return RayleighSommerfeldPhaseScreenResult(
        kM=kM,
        transverse_x_over_M=transverse,
        propagation_z_over_M=distance,
        F_complex=values,
        F_propagating=propagating,
        F_evanescent=evanescent,
        abs_F=np.abs(values),
        arg_F_principal=np.angle(values),
        valid_mask=valid,
        metadata=metadata,
    )


def _angular_spectrum_point(
    *,
    mp,
    kM: float,
    transverse_x_over_M: float,
    propagation_z_over_M: float,
    propagating_decay_target: float,
    evanescent_decay_target: float,
):
    q = mp.mpf(str(kM))
    x = mp.mpf(str(transverse_x_over_M))
    z = mp.mpf(str(propagation_z_over_M))
    w = 4 * q
    rho_einstein = 2 * mp.sqrt(z)

    hankel_prefactor = (
        rho_einstein ** (1j * w)
        * 2 ** (1 - 1j * w)
        * mp.gamma(1 - 1j * w / 2)
        / mp.gamma(1j * w / 2)
        * mp.exp(-1j * q * z)
    )

    # q_perp = k exp(-u).  The integrand tends to the unlensed plane-wave
    # value exp(i*k*z), so subtract it before quadrature and integrate its
    # Abel-regularized Fourier tail analytically.  The remaining integral is
    # absolutely convergent as exp(-2*u), including at very small kM.
    plane_wave_limit = mp.exp(1j * q * z)

    def propagating_difference(u):
        exp_minus_u = mp.exp(-u)
        finite_u_value = (
            mp.besselj(0, q * x * exp_minus_u)
            * mp.exp(1j * q * z * mp.sqrt(1 - exp_minus_u**2))
        )
        return mp.exp(-1j * w * u) * (finite_u_value - plane_wave_limit)

    propagating_cap = mp.mpf(str(propagating_decay_target)) / 2
    propagating_segments = [mp.mpf("0"), mp.mpf("1")]
    while propagating_segments[-1] * 2 < propagating_cap:
        propagating_segments.append(propagating_segments[-1] * 2)
    if propagating_segments[-1] != propagating_cap:
        propagating_segments.append(propagating_cap)
    propagating_integral = q ** (1j * w) * (
        mp.quad(propagating_difference, propagating_segments)
        - 1j * plane_wave_limit / w
    )

    # q_perp = k exp(s) on the evanescent branch.  The finite cap enforces a
    # conservative exp(-target) upper-tail suppression before truncation.
    def evanescent_integrand(s):
        exp_s = mp.exp(s)
        return (
            mp.exp(1j * w * s)
            * mp.besselj(0, q * x * exp_s)
            * mp.exp(-q * z * mp.sqrt(exp_s**2 - 1))
        )

    evanescent_cap = max(
        mp.mpf("5"), mp.log(mp.mpf(str(evanescent_decay_target)) / (q * z))
    )
    evanescent_integral = q ** (1j * w) * mp.quad(
        evanescent_integrand, [0, evanescent_cap]
    )

    return (
        hankel_prefactor * propagating_integral,
        hankel_prefactor * evanescent_integral,
    )


def _load_mpmath():
    try:
        return importlib.import_module("mpmath")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Rayleigh--Sommerfeld diagnostics require the project optional "
            "dependency; install with `pip install -e '.[oracle]'`."
        ) from exc


def _positive_vector(values: np.ndarray, *, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size == 0:
        raise ValueError(f"{name} must be a non-empty one-dimensional array.")
    if not np.isfinite(array).all() or np.any(array <= 0.0):
        raise ValueError(f"{name} must contain positive finite values.")
    return array


def _finite_vector(values: np.ndarray, *, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size == 0:
        raise ValueError(f"{name} must be a non-empty one-dimensional array.")
    if not np.isfinite(array).all():
        raise ValueError(f"{name} must contain finite values.")
    return array
