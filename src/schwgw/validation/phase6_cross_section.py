"""Li-independent analytic and semiclassical spin-2 benchmarks."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.optimize import brentq
from scipy.special import jn_zeros, jnp_zeros, jv


DOLAN_GLORY_SOURCE = (
    "Dolan, Class. Quantum Grav. 25, 235002 (2008), Eq. (5); "
    "Schwarzschild b_g/M=5.3570 and b_g^2|db/dtheta|/M^3=4.896"
)


@dataclass(frozen=True)
class Spin2GloryGeometry:
    """Dimensionless Schwarzschild geodesic inputs to the glory formula."""

    b_g_over_M: float = 5.3570
    b_g2_abs_db_dtheta_over_M3: float = 4.896
    source: str = DOLAN_GLORY_SOURCE

    def __post_init__(self) -> None:
        for name in ("b_g_over_M", "b_g2_abs_db_dtheta_over_M3"):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")
            object.__setattr__(self, name, value)


@dataclass(frozen=True)
class GloryApplicability:
    """Explicit high-frequency/backward-angle validity window."""

    minimum_kM: float = 1.0
    maximum_backward_offset: float = 0.5
    interpretation: str = "semiclassical benchmark only; theta close to pi"

    def __post_init__(self) -> None:
        minimum = float(self.minimum_kM)
        offset = float(self.maximum_backward_offset)
        if not math.isfinite(minimum) or minimum <= 0.0:
            raise ValueError("minimum_kM must be finite and positive")
        if not math.isfinite(offset) or offset <= 0.0:
            raise ValueError("maximum_backward_offset must be finite and positive")
        if offset >= 0.5 * math.pi:
            raise ValueError("maximum_backward_offset must be smaller than pi/2")
        if not isinstance(self.interpretation, str) or not self.interpretation.strip():
            raise ValueError("interpretation must be non-empty")
        object.__setattr__(self, "minimum_kM", minimum)
        object.__setattr__(self, "maximum_backward_offset", offset)


@dataclass(frozen=True)
class GloryRingBenchmark:
    """First spin-2 glory-ring location and full width at half maximum."""

    kM: float
    theta_peak: float
    backward_offset: float
    fwhm: float
    peak_cross_section_over_M2: float
    geometry: Spin2GloryGeometry
    applicability: GloryApplicability


def spin2_low_frequency_cross_section(
    theta: ArrayLike,
    *,
    mass: float = 1.0,
) -> float | NDArray[np.float64]:
    """Return the exact leading ``M omega -> 0`` spin-2 cross section.

    The returned quantity is
    ``M^2 [cos(theta/2)^8 + sin(theta/2)^8] / sin(theta/2)^4``.
    The forward axis is excluded because the long-range cross section diverges.
    """

    mass_value = _positive_finite(mass, "mass")
    values = np.asarray(theta, dtype=np.float64)
    if (
        not np.all(np.isfinite(values))
        or np.any(values <= 0.0)
        or np.any(values > math.pi)
    ):
        raise ValueError("theta must lie in (0, pi]")
    half = 0.5 * values
    result = mass_value**2 * (np.cos(half) ** 8 + np.sin(half) ** 8) / np.sin(half) ** 4
    if values.shape == ():
        return float(result)
    return np.asarray(result, dtype=np.float64)


def spin2_absorption_cross_section(
    ell: Sequence[int] | NDArray[np.integer],
    transmission_even: ArrayLike,
    transmission_odd: ArrayLike,
    *,
    k: float,
) -> float:
    """Return the unpolarized spin-2 absorption cross section.

    ``transmission_even/odd`` are independently determined horizon-flux
    fractions, not values inferred from ``1-|R|^2``.  The parity average is

    ``pi/(2 k^2) sum_l (2l+1) [Gamma_even + Gamma_odd]``.
    """

    k_value = _positive_finite(k, "k")
    ell_values = np.asarray(ell)
    even = np.asarray(transmission_even, dtype=np.float64)
    odd = np.asarray(transmission_odd, dtype=np.float64)
    if ell_values.ndim != 1 or ell_values.size == 0:
        raise ValueError("ell must be a non-empty one-dimensional sequence")
    if not np.issubdtype(ell_values.dtype, np.integer):
        raise TypeError("ell values must be integers")
    ell_values = ell_values.astype(np.int64, copy=False)
    if not np.array_equal(ell_values, np.arange(2, int(ell_values[-1]) + 1)):
        raise ValueError("ell must be the contiguous range 2..ell_max")
    if even.shape != ell_values.shape or odd.shape != ell_values.shape:
        raise ValueError("transmission arrays must match ell")
    for values in (even, odd):
        if (
            not np.all(np.isfinite(values))
            or np.any(values < 0.0)
            or np.any(values > 1.0)
        ):
            raise ValueError("transmission fractions must lie in [0, 1]")
    weights = 2.0 * ell_values.astype(np.float64) + 1.0
    result = math.pi / (2.0 * k_value**2) * np.sum(weights * (even + odd))
    return float(result)


def geometric_optics_absorption_cross_section(*, mass: float = 1.0) -> float:
    """Return the Schwarzschild capture limit ``27 pi M^2``."""

    mass_value = _positive_finite(mass, "mass")
    return 27.0 * math.pi * mass_value**2


def spin2_backward_glory_cross_section(
    theta: ArrayLike,
    *,
    kM: float,
    mass: float = 1.0,
    geometry: Spin2GloryGeometry = Spin2GloryGeometry(),
    applicability: GloryApplicability = GloryApplicability(),
) -> float | NDArray[np.float64]:
    """Return the dimensionally explicit Schwarzschild spin-2 glory model.

    In dimensionless form,

    ``M^-2 d sigma/d Omega = 2 pi (M omega) G J_4^2[(b_g/M)(M omega) sin theta]``

    where ``G=b_g^2 |db/dtheta|/M^3``.  This resolves the dimensional
    ambiguity that results if the tabulated dimensionful ``b_g`` values are
    inserted directly into Dolan's normalized presentation.
    """

    coupling = _positive_finite(kM, "kM")
    mass_value = _positive_finite(mass, "mass")
    if not isinstance(geometry, Spin2GloryGeometry):
        raise TypeError("geometry must be a Spin2GloryGeometry")
    if not isinstance(applicability, GloryApplicability):
        raise TypeError("applicability must be a GloryApplicability")
    if coupling < applicability.minimum_kM:
        raise ValueError("kM is outside the frozen high-frequency glory domain")
    values = np.asarray(theta, dtype=np.float64)
    if (
        not np.all(np.isfinite(values))
        or np.any(values < 0.0)
        or np.any(values > math.pi)
    ):
        raise ValueError("theta must lie in [0, pi]")
    if np.any(math.pi - values > applicability.maximum_backward_offset):
        raise ValueError("theta is outside the frozen backward-glory window")
    argument = geometry.b_g_over_M * coupling * np.sin(values)
    dimensionless = (
        2.0
        * math.pi
        * coupling
        * geometry.b_g2_abs_db_dtheta_over_M3
        * jv(4, argument) ** 2
    )
    result = mass_value**2 * dimensionless
    if values.shape == ():
        return float(result)
    return np.asarray(result, dtype=np.float64)


def first_spin2_glory_ring(
    *,
    kM: float,
    geometry: Spin2GloryGeometry = Spin2GloryGeometry(),
    applicability: GloryApplicability = GloryApplicability(),
) -> GloryRingBenchmark:
    """Return the first backward glory-ring peak and its FWHM.

    The domain requires the entire first ``J_4^2`` lobe to fit between the
    backward axis and ``theta=pi/2``.  This makes the reported width a genuine
    two-sided FWHM rather than a clipped estimate.
    """

    coupling = _positive_finite(kM, "kM")
    if not isinstance(geometry, Spin2GloryGeometry):
        raise TypeError("geometry must be a Spin2GloryGeometry")
    if not isinstance(applicability, GloryApplicability):
        raise TypeError("applicability must be a GloryApplicability")
    if coupling < applicability.minimum_kM:
        raise ValueError("kM is outside the frozen high-frequency glory domain")
    x_peak = float(jnp_zeros(4, 1)[0])
    x_zero = float(jn_zeros(4, 1)[0])
    scale = geometry.b_g_over_M * coupling
    if scale <= x_zero:
        raise ValueError("kM is too small for an unclipped first glory-ring FWHM")
    peak_level = float(jv(4, x_peak) ** 2)
    half_level = 0.5 * peak_level

    def half_equation(value: float) -> float:
        return float(jv(4, value) ** 2 - half_level)

    x_left = brentq(half_equation, 0.0, x_peak)
    x_right = brentq(half_equation, x_peak, x_zero)
    delta_peak = math.asin(x_peak / scale)
    delta_left = math.asin(x_left / scale)
    delta_right = math.asin(x_right / scale)
    if delta_right > applicability.maximum_backward_offset:
        raise ValueError(
            "the first glory-ring FWHM extends outside the frozen backward window"
        )
    theta_peak = math.pi - delta_peak
    peak_cross_section = spin2_backward_glory_cross_section(
        theta_peak,
        kM=coupling,
        mass=1.0,
        geometry=geometry,
        applicability=applicability,
    )
    return GloryRingBenchmark(
        kM=coupling,
        theta_peak=theta_peak,
        backward_offset=delta_peak,
        fwhm=delta_right - delta_left,
        peak_cross_section_over_M2=float(peak_cross_section),
        geometry=geometry,
        applicability=applicability,
    )


def _positive_finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


__all__ = [
    "DOLAN_GLORY_SOURCE",
    "GloryRingBenchmark",
    "GloryApplicability",
    "Spin2GloryGeometry",
    "first_spin2_glory_ring",
    "geometric_optics_absorption_cross_section",
    "spin2_absorption_cross_section",
    "spin2_backward_glory_cross_section",
    "spin2_low_frequency_cross_section",
]
