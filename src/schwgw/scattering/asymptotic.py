"""Asymptotic Schwarzschild scattering diagnostics for paper Fig. 4/8.

This module is deliberately separate from the finite-radius production path.
It uses the radial solver's branch-free ``phase_factor = exp(2 i delta)``
directly and implements the Appendix-E associated-Legendre series reduction.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.special import loggamma, lpmv


@dataclass(frozen=True)
class ParityScatteringSeries:
    """Dense ``ell=2..ell_max`` coefficients for Appendix-D ``f_s/f_a``."""

    ell: NDArray[np.int64]
    symmetric: NDArray[np.complex128]
    antisymmetric: NDArray[np.complex128]

    def __post_init__(self) -> None:
        ell = np.asarray(self.ell, dtype=np.int64)
        symmetric = np.asarray(self.symmetric, dtype=np.complex128)
        antisymmetric = np.asarray(self.antisymmetric, dtype=np.complex128)
        if ell.ndim != 1 or ell.size == 0:
            raise ValueError("ell must be a non-empty one-dimensional array.")
        if not np.array_equal(ell, np.arange(2, int(ell[-1]) + 1)):
            raise ValueError("ell must be the contiguous range 2..ell_max.")
        if symmetric.shape != ell.shape or antisymmetric.shape != ell.shape:
            raise ValueError("series coefficient arrays must match ell.")
        if not _finite_complex(symmetric) or not _finite_complex(antisymmetric):
            raise ValueError("series coefficients must be finite.")
        object.__setattr__(self, "ell", _readonly(ell))
        object.__setattr__(self, "symmetric", _readonly(symmetric))
        object.__setattr__(self, "antisymmetric", _readonly(antisymmetric))


@dataclass(frozen=True)
class ReducedLegendreSeries:
    """One finite Appendix-E series after a fixed number of reductions."""

    ell: NDArray[np.int64]
    coefficients: NDArray[np.complex128]
    reduction_order: int

    def __post_init__(self) -> None:
        ell = np.asarray(self.ell, dtype=np.int64)
        coefficients = np.asarray(self.coefficients, dtype=np.complex128)
        if ell.ndim != 1 or ell.size == 0:
            raise ValueError("ell must be a non-empty one-dimensional array.")
        if not np.array_equal(ell, np.arange(2, int(ell[-1]) + 1)):
            raise ValueError("ell must be the contiguous range 2..ell_max.")
        if coefficients.shape != ell.shape:
            raise ValueError("coefficients must match ell.")
        if not _finite_complex(coefficients):
            raise ValueError("coefficients must be finite.")
        if isinstance(self.reduction_order, bool) or not isinstance(
            self.reduction_order,
            int,
        ):
            raise TypeError("reduction_order must be an integer.")
        if self.reduction_order < 0:
            raise ValueError("reduction_order must be nonnegative.")
        object.__setattr__(self, "ell", _readonly(ell))
        object.__setattr__(self, "coefficients", _readonly(coefficients))


@dataclass(frozen=True)
class ScatteringMatrixResult:
    """Helicity matrix entries and differential cross section on one grid."""

    theta: NDArray[np.float64]
    M22: NDArray[np.complex128]
    M12: NDArray[np.complex128]
    differential_cross_section: NDArray[np.float64]
    k: float
    reduction_order: int

    def __post_init__(self) -> None:
        theta = np.asarray(self.theta, dtype=np.float64)
        M22 = np.asarray(self.M22, dtype=np.complex128)
        M12 = np.asarray(self.M12, dtype=np.complex128)
        cross_section = np.asarray(self.differential_cross_section, dtype=np.float64)
        if theta.ndim != 1 or theta.size == 0:
            raise ValueError("theta must be a non-empty one-dimensional array.")
        if M22.shape != theta.shape or M12.shape != theta.shape:
            raise ValueError("matrix entries must match theta.")
        if cross_section.shape != theta.shape:
            raise ValueError("differential cross section must match theta.")
        if not np.all(np.isfinite(theta)):
            raise ValueError("theta must be finite.")
        if np.any(theta <= 0.0) or np.any(theta > np.pi):
            raise ValueError("theta must lie in (0, pi].")
        if not _finite_complex(M22) or not _finite_complex(M12):
            raise ValueError("matrix entries must be finite.")
        if not np.all(np.isfinite(cross_section)) or np.any(cross_section < 0.0):
            raise ValueError("differential cross section must be finite and nonnegative.")
        if not np.isfinite(self.k) or self.k <= 0.0:
            raise ValueError("k must be finite and positive.")
        if isinstance(self.reduction_order, bool) or not isinstance(
            self.reduction_order,
            int,
        ):
            raise TypeError("reduction_order must be an integer.")
        if self.reduction_order < 0:
            raise ValueError("reduction_order must be nonnegative.")
        object.__setattr__(self, "theta", _readonly(theta))
        object.__setattr__(self, "M22", _readonly(M22))
        object.__setattr__(self, "M12", _readonly(M12))
        object.__setattr__(self, "differential_cross_section", _readonly(cross_section))


@dataclass(frozen=True)
class HybridPhaseSeries:
    """Numerical low-``ell`` phases matched to the Schwarzschild tail."""

    ell: NDArray[np.int64]
    odd: NDArray[np.complex128]
    even: NDArray[np.complex128]
    overlap_ell: tuple[int, int]
    tail_phase_offset: float
    maximum_overlap_phase_residual: float

    def __post_init__(self) -> None:
        ell = np.asarray(self.ell, dtype=np.int64)
        odd = np.asarray(self.odd, dtype=np.complex128)
        even = np.asarray(self.even, dtype=np.complex128)
        if not np.array_equal(ell, np.arange(2, int(ell[-1]) + 1)):
            raise ValueError("ell must be the contiguous range 2..ell_max.")
        if odd.shape != ell.shape or even.shape != ell.shape:
            raise ValueError("hybrid phase-factor arrays must match ell.")
        if not _finite_complex(odd) or not _finite_complex(even):
            raise ValueError("hybrid phase factors must be finite.")
        low, high = self.overlap_ell
        if low < 2 or high <= low or high > int(ell[-1]):
            raise ValueError("overlap_ell must be a valid increasing interval.")
        if not np.isfinite(self.tail_phase_offset):
            raise ValueError("tail_phase_offset must be finite.")
        if (
            not np.isfinite(self.maximum_overlap_phase_residual)
            or self.maximum_overlap_phase_residual < 0.0
        ):
            raise ValueError("maximum overlap residual must be finite and nonnegative.")
        object.__setattr__(self, "ell", _readonly(ell))
        object.__setattr__(self, "odd", _readonly(odd))
        object.__setattr__(self, "even", _readonly(even))


def parity_scattering_series(
    phase_factor_even: ArrayLike,
    phase_factor_odd: ArrayLike,
    *,
    ell: ArrayLike | None = None,
) -> ParityScatteringSeries:
    """Return Appendix-D coefficients without taking a phase logarithm.

    The parity label is fixed as ``p=+1`` for even (Zerilli) and ``p=-1``
    for odd (Regge-Wheeler), so ``f_a`` contains ``S_even - S_odd``.
    """

    even = np.asarray(phase_factor_even, dtype=np.complex128)
    odd = np.asarray(phase_factor_odd, dtype=np.complex128)
    if even.ndim != 1 or odd.ndim != 1 or even.size == 0:
        raise ValueError("phase-factor arrays must be non-empty and one-dimensional.")
    if even.shape != odd.shape:
        raise ValueError("even and odd phase-factor arrays must have the same shape.")
    if not _finite_complex(even) or not _finite_complex(odd):
        raise ValueError("phase factors must be finite.")
    ell_values = (
        np.arange(2, 2 + even.size, dtype=np.int64)
        if ell is None
        else np.asarray(ell, dtype=np.int64)
    )
    if ell_values.shape != even.shape or not np.array_equal(
        ell_values,
        np.arange(2, 2 + even.size, dtype=np.int64),
    ):
        raise ValueError("ell must be the contiguous range 2..ell_max.")
    ell_float = ell_values.astype(np.float64)
    sigma = (ell_float - 1.0) * ell_float * (ell_float + 1.0) * (ell_float + 2.0)
    prefactor = (2.0 * ell_float + 1.0) / (4.0 * np.pi * sigma)
    even_scattered = even - 1.0
    odd_scattered = odd - 1.0
    return ParityScatteringSeries(
        ell=ell_values,
        symmetric=prefactor * (even_scattered + odd_scattered),
        antisymmetric=prefactor * (even_scattered - odd_scattered),
    )


def outer_matching_phase_corrected(
    phase_factor: ArrayLike,
    ell: ArrayLike,
    *,
    k: float,
    r_out: float,
) -> NDArray[np.complex128]:
    """Remove the leading finite-radius centrifugal phase from ``S_ell``.

    Matching a long-range radial mode to leading plane waves at finite
    ``r_out`` adds ``ell(ell+1)/(k r_out)`` to the phase of ``S_ell``.
    The correction is unit modulus and therefore does not alter absorption.
    """

    phase = np.asarray(phase_factor, dtype=np.complex128)
    ell_values = np.asarray(ell, dtype=np.int64)
    if phase.ndim != 1 or phase.size == 0 or phase.shape != ell_values.shape:
        raise ValueError("phase_factor and ell must be matching non-empty vectors.")
    if not _finite_complex(phase):
        raise ValueError("phase_factor must be finite.")
    if not np.array_equal(ell_values, np.arange(2, int(ell_values[-1]) + 1)):
        raise ValueError("ell must be the contiguous range 2..ell_max.")
    if not np.isfinite(k) or k <= 0.0 or not np.isfinite(r_out) or r_out <= 0.0:
        raise ValueError("k and r_out must be finite and positive.")
    exponent = -1j * ell_values * (ell_values + 1) / (float(k) * float(r_out))
    corrected = phase * np.exp(exponent)
    return np.asarray(corrected, dtype=np.complex128)


def poisson_sasaki_odd_phase_factor(
    ell: ArrayLike,
    *,
    k: float,
    M: float = 1.0,
) -> NDArray[np.complex128]:
    """Return the Schwarzschild large-``ell`` Coulomb/MST phase factor.

    This is the Poisson--Sasaki/Dolan asymptotic expression
    ``exp(2 i delta_l^-)`` through its universal ``1/[ell(ell+1)]`` term.
    It is used only as a large-``ell`` tail, not as a replacement for the
    numerical strong-field low multipoles.
    """

    ell_values = np.asarray(ell, dtype=np.int64)
    if ell_values.ndim != 1 or ell_values.size == 0 or np.any(ell_values < 2):
        raise ValueError("ell must be a non-empty vector with values >=2.")
    if not np.isfinite(k) or k <= 0.0 or not np.isfinite(M) or M <= 0.0:
        raise ValueError("k and M must be finite and positive.")
    epsilon = 2.0 * float(M) * float(k)
    values = ell_values.astype(np.float64)
    logarithm = (
        2j * epsilon * np.log(2.0 * epsilon)
        - 1j * epsilon
        + loggamma(values + 1.0 - 1j * epsilon)
        - loggamma(values + 1.0 + 1j * epsilon)
        + 4j * epsilon / (values * (values + 1.0))
    )
    return np.asarray(np.exp(logarithm), dtype=np.complex128)


def schwarzschild_even_from_odd(
    odd_phase_factor: ArrayLike,
    ell: ArrayLike,
    *,
    k: float,
    M: float = 1.0,
) -> NDArray[np.complex128]:
    """Apply the exact Schwarzschild even/odd parity phase relation."""

    odd = np.asarray(odd_phase_factor, dtype=np.complex128)
    ell_values = np.asarray(ell, dtype=np.int64)
    if odd.ndim != 1 or odd.size == 0 or odd.shape != ell_values.shape:
        raise ValueError("odd_phase_factor and ell must be matching vectors.")
    if not _finite_complex(odd):
        raise ValueError("odd_phase_factor must be finite.")
    if not np.isfinite(k) or k <= 0.0 or not np.isfinite(M) or M <= 0.0:
        raise ValueError("k and M must be finite and positive.")
    values = ell_values.astype(np.float64)
    sigma = (values - 1.0) * values * (values + 1.0) * (values + 2.0)
    parity_ratio = (sigma + 12j * M * k) / (sigma - 12j * M * k)
    return np.asarray(odd * parity_ratio, dtype=np.complex128)


def matched_schwarzschild_phase_factors(
    numerical_odd: ArrayLike,
    numerical_even: ArrayLike,
    numerical_ell: ArrayLike,
    *,
    k: float,
    r_out: float,
    output_lmax: int,
    overlap_ell: tuple[int, int],
    M: float = 1.0,
) -> HybridPhaseSeries:
    """Construct a smooth numerical/Coulomb matched phase-factor sequence.

    Numerical phases are corrected for the leading finite-``r_out`` phase.
    The large-``ell`` tail receives one convention-preserving constant phase
    determined by a circular mean in the supplied nonabsorptive overlap.
    A raised-cosine blend makes the matched sequence continuously approach
    the analytic tail without filtering any low-``ell`` strong-field mode.
    """

    raw_ell = np.asarray(numerical_ell, dtype=np.int64)
    odd = outer_matching_phase_corrected(
        numerical_odd, raw_ell, k=k, r_out=r_out
    )
    even = outer_matching_phase_corrected(
        numerical_even, raw_ell, k=k, r_out=r_out
    )
    if isinstance(output_lmax, bool) or not isinstance(output_lmax, int):
        raise TypeError("output_lmax must be an integer.")
    if output_lmax < int(raw_ell[-1]):
        raise ValueError("output_lmax must not discard supplied numerical modes.")
    low, high = overlap_ell
    if low < 2 or high <= low or high > int(raw_ell[-1]):
        raise ValueError("overlap_ell must lie inside the numerical sequence.")
    overlap = (raw_ell >= low) & (raw_ell <= high)
    analytic_raw = poisson_sasaki_odd_phase_factor(raw_ell, k=k, M=M)
    ratios = odd[overlap] / analytic_raw[overlap]
    if np.max(np.abs(np.abs(ratios) - 1.0)) > 1.0e-6:
        raise ValueError("matching overlap must be nonabsorptive to 1e-6.")
    unit_ratios = ratios / np.abs(ratios)
    mean = np.sum(unit_ratios)
    if abs(mean) <= 0.5 * unit_ratios.size:
        raise ValueError("matching overlap has no unique circular phase mean.")
    offset = float(np.angle(mean))
    residual = np.angle(unit_ratios * np.exp(-1j * offset))
    maximum_residual = float(np.max(np.abs(residual)))
    if maximum_residual > 0.08:
        raise ValueError("matching overlap exceeds the 0.08-radian phase gate.")

    output_ell = np.arange(2, output_lmax + 1, dtype=np.int64)
    tail_odd = poisson_sasaki_odd_phase_factor(output_ell, k=k, M=M)
    tail_odd *= np.exp(1j * offset)
    tail_even = schwarzschild_even_from_odd(
        tail_odd, output_ell, k=k, M=M
    )
    matched_odd = np.array(tail_odd, copy=True)
    matched_even = np.array(tail_even, copy=True)
    below = raw_ell <= low
    low_indices = np.flatnonzero(below)
    matched_odd[low_indices] = odd[low_indices]
    matched_even[low_indices] = even[low_indices]
    blending = (raw_ell > low) & (raw_ell < high)
    indices = np.flatnonzero(blending)
    fraction = (raw_ell[indices] - low) / float(high - low)
    tail_weight = 0.5 - 0.5 * np.cos(np.pi * fraction)
    for destination, numerical in (
        (matched_odd, odd),
        (matched_even, even),
    ):
        phase_residual = np.angle(numerical[indices] / destination[indices])
        log_amplitude = (
            (1.0 - tail_weight) * np.log(np.abs(numerical[indices]))
            + tail_weight * np.log(np.abs(destination[indices]))
        )
        phase = np.angle(destination[indices]) + (
            1.0 - tail_weight
        ) * phase_residual
        destination[indices] = np.exp(log_amplitude + 1j * phase)
    return HybridPhaseSeries(
        ell=output_ell,
        odd=matched_odd,
        even=matched_even,
        overlap_ell=overlap_ell,
        tail_phase_offset=offset,
        maximum_overlap_phase_residual=maximum_residual,
    )
def reduce_legendre_series(
    coefficients: ArrayLike,
    *,
    reduction_order: int,
) -> ReducedLegendreSeries:
    """Apply the exact Appendix-E recursion to a finite ``ell=2..L`` series.

    One upper-edge coefficient is retained after each reduction.  This is
    required for the finite polynomial identity; silently truncating it at
    the original ``L`` would break ``f^(k)=(1-cos(theta))^k f``.
    """

    if isinstance(reduction_order, bool) or not isinstance(reduction_order, int):
        raise TypeError("reduction_order must be an integer.")
    if reduction_order < 0:
        raise ValueError("reduction_order must be nonnegative.")
    current = np.asarray(coefficients, dtype=np.complex128)
    if current.ndim != 1 or current.size == 0:
        raise ValueError("coefficients must be non-empty and one-dimensional.")
    if not _finite_complex(current):
        raise ValueError("coefficients must be finite.")

    for _ in range(reduction_order):
        previous = current
        old_lmax = previous.size + 1
        new_lmax = old_lmax + 1
        current = np.zeros(new_lmax - 1, dtype=np.complex128)
        for ell_value in range(2, new_lmax + 1):
            center = _coefficient_at(previous, ell_value)
            lower = _coefficient_at(previous, ell_value - 1)
            upper = _coefficient_at(previous, ell_value + 1)
            current[ell_value - 2] = (
                center
                - ((ell_value - 2.0) / (2.0 * ell_value - 1.0)) * lower
                - ((ell_value + 3.0) / (2.0 * ell_value + 3.0)) * upper
            )

    return ReducedLegendreSeries(
        ell=np.arange(2, current.size + 2, dtype=np.int64),
        coefficients=current,
        reduction_order=reduction_order,
    )


def reduce_truncated_legendre_series(
    coefficients: ArrayLike,
    *,
    reduction_order: int,
    target_lmax: int | None = None,
) -> ReducedLegendreSeries:
    """Apply Appendix-E reduction with a well-defined finite upper edge.

    Computing reduced coefficients through ``target_lmax`` at order ``q``
    requires the unreduced series through at least ``target_lmax + q``.
    Each recursion therefore consumes one supplied upper-edge coefficient.
    When ``target_lmax`` is omitted, the largest mathematically supported
    target is used.  Treating the missing upper coefficient as zero at every
    iteration creates a spurious edge term that is amplified by
    ``(1-cos(theta))**(-q)`` and is not an Appendix-E approximant.
    """

    if isinstance(reduction_order, bool) or not isinstance(reduction_order, int):
        raise TypeError("reduction_order must be an integer.")
    if reduction_order < 0:
        raise ValueError("reduction_order must be nonnegative.")
    current = np.asarray(coefficients, dtype=np.complex128)
    if current.ndim != 1 or current.size == 0:
        raise ValueError("coefficients must be non-empty and one-dimensional.")
    if not _finite_complex(current):
        raise ValueError("coefficients must be finite.")
    input_lmax = current.size + 1
    maximum_target = input_lmax - reduction_order
    if maximum_target < 2:
        raise ValueError("coefficients do not supply the reduction upper edge.")
    if target_lmax is None:
        target = maximum_target
    else:
        if isinstance(target_lmax, bool) or not isinstance(target_lmax, int):
            raise TypeError("target_lmax must be an integer.")
        if target_lmax < 2 or target_lmax > maximum_target:
            raise ValueError(
                "target_lmax must lie between 2 and input_lmax-reduction_order."
            )
        target = target_lmax
    current = np.array(current, copy=True)
    for _ in range(reduction_order):
        previous = current
        current = np.empty(previous.size - 1, dtype=np.complex128)
        for ell_value in range(2, previous.size + 1):
            current[ell_value - 2] = (
                _coefficient_at(previous, ell_value)
                - ((ell_value - 2.0) / (2.0 * ell_value - 1.0))
                * _coefficient_at(previous, ell_value - 1)
                - ((ell_value + 3.0) / (2.0 * ell_value + 3.0))
                * _coefficient_at(previous, ell_value + 1)
            )
    current = current[: target - 1]
    return ReducedLegendreSeries(
        ell=np.arange(2, target + 1, dtype=np.int64),
        coefficients=current,
        reduction_order=reduction_order,
    )


def scattering_matrix_cross_section(
    theta: ArrayLike,
    series: ParityScatteringSeries,
    *,
    k: float,
    reduction_order: int,
    target_lmax: int | None = None,
) -> ScatteringMatrixResult:
    """Evaluate Li-Hou-Zhao Appendix-D ``M22``, ``M12`` and ``d sigma/d Omega``.

    The angular-operator convention is frozen as

    ``L_s = d_theta - i csc(theta) d_phi - s cot(theta)`` and
    ``bar(L)_s = d_theta + i csc(theta) d_phi + s cot(theta)``.

    The forward endpoint is excluded because the reduced asymptotic series is
    singular there.  The backward endpoint is evaluated by its analytic
    associated-Legendre limit rather than by a floating ``0/0`` expression.
    """

    if not isinstance(series, ParityScatteringSeries):
        raise TypeError("series must be a ParityScatteringSeries instance.")
    if not np.isfinite(k) or k <= 0.0:
        raise ValueError("k must be finite and positive.")
    theta_values = np.asarray(theta, dtype=np.float64)
    if theta_values.ndim != 1 or theta_values.size == 0:
        raise ValueError("theta must be a non-empty one-dimensional array.")
    if not np.all(np.isfinite(theta_values)):
        raise ValueError("theta must be finite.")
    if np.any(theta_values <= 0.0) or np.any(theta_values > np.pi):
        raise ValueError("theta must lie in (0, pi].")

    symmetric = reduce_truncated_legendre_series(
        series.symmetric,
        reduction_order=reduction_order,
        target_lmax=target_lmax,
    )
    antisymmetric = reduce_truncated_legendre_series(
        series.antisymmetric,
        reduction_order=reduction_order,
        target_lmax=target_lmax,
    )
    m22_angular = _apply_spin_angular_operator(
        theta_values,
        symmetric,
        branch="M22",
    )
    m12_angular = _apply_spin_angular_operator(
        theta_values,
        antisymmetric,
        branch="M12",
    )
    prefactor = np.pi / (1j * float(k))
    M22 = prefactor * m22_angular
    M12 = prefactor * m12_angular
    cross_section = np.abs(M22) ** 2 + np.abs(M12) ** 2
    return ScatteringMatrixResult(
        theta=theta_values,
        M22=M22,
        M12=M12,
        differential_cross_section=np.asarray(cross_section, dtype=np.float64),
        k=float(k),
        reduction_order=reduction_order,
    )


def evaluate_reduced_legendre_series(
    theta: ArrayLike,
    series: ReducedLegendreSeries,
) -> complex | NDArray[np.complex128]:
    """Evaluate ``(1-cos(theta))^-k sum a_l^(k) P_l^2``."""

    if not isinstance(series, ReducedLegendreSeries):
        raise TypeError("series must be a ReducedLegendreSeries instance.")
    theta_values = np.asarray(theta, dtype=np.float64)
    if not np.all(np.isfinite(theta_values)):
        raise ValueError("theta must contain only finite values.")
    if np.any(theta_values < 0.0) or np.any(theta_values > np.pi):
        raise ValueError("theta must lie in [0, pi].")
    x = np.cos(theta_values)
    if series.reduction_order and np.any(1.0 - x == 0.0):
        raise ValueError("Reduced series is singular on the forward axis theta=0.")
    values = np.zeros(theta_values.shape, dtype=np.complex128)
    for ell_value, coefficient in zip(
        series.ell,
        series.coefficients,
        strict=True,
    ):
        values += coefficient * lpmv(2, int(ell_value), x)
    if series.reduction_order:
        values *= (1.0 - x) ** (-series.reduction_order)
    if theta_values.shape == ():
        return complex(values)
    return values


def _coefficient_at(coefficients: NDArray[np.complex128], ell: int) -> complex:
    if ell < 2 or ell > coefficients.size + 1:
        return 0.0j
    return complex(coefficients[ell - 2])


def _apply_spin_angular_operator(
    theta: NDArray[np.float64],
    series: ReducedLegendreSeries,
    *,
    branch: str,
) -> NDArray[np.complex128]:
    if branch not in {"M22", "M12"}:
        raise ValueError("branch must be 'M22' or 'M12'.")
    result = np.empty(theta.shape, dtype=np.complex128)
    backward = theta == np.pi
    interior = ~backward
    if np.any(interior):
        values, first, second = _reduced_series_theta_derivatives(
            theta[interior],
            series,
        )
        sine = np.sin(theta[interior])
        cosine = np.cos(theta[interior])
        csc = 1.0 / sine
        cot = cosine / sine
        if branch == "M22":
            # L_1 L_0 acting on f_s e^{-2 i phi}; this is the
            # helicity-preserving d^ell_{2,2}(theta) branch.
            result[interior] = (
                second
                + (4.0 * csc - cot) * first
                + (4.0 * csc * csc - 4.0 * csc * cot) * values
            )
        else:
            # L_1 L_0 acting on f_a e^{+2 i phi}; this is the
            # helicity-reversing d^ell_{2,-2}(theta) branch.
            result[interior] = (
                second
                + (-4.0 * csc - cot) * first
                + (4.0 * csc * cot + 4.0 * csc * csc) * values
            )
    if np.any(backward):
        if branch == "M22":
            result[backward] = 0.0j
        else:
            coefficient = 0.0j
            for ell_value, value in zip(
                series.ell,
                series.coefficients,
                strict=True,
            ):
                ell = int(ell_value)
                legendre_second_at_minus_one = (
                    (-1.0) ** ell
                    * (ell - 1.0)
                    * ell
                    * (ell + 1.0)
                    * (ell + 2.0)
                    / 8.0
                )
                coefficient += value * legendre_second_at_minus_one
            coefficient *= 2.0 ** (-series.reduction_order)
            result[backward] = 8.0 * coefficient
    return result


def _reduced_series_theta_derivatives(
    theta: NDArray[np.float64],
    series: ReducedLegendreSeries,
) -> tuple[
    NDArray[np.complex128],
    NDArray[np.complex128],
    NDArray[np.complex128],
]:
    x = np.cos(theta)
    sine = np.sin(theta)
    G = np.zeros(theta.shape, dtype=np.complex128)
    G_theta = np.zeros_like(G)
    G_theta_theta = np.zeros_like(G)
    for ell_value, coefficient in zip(
        series.ell,
        series.coefficients,
        strict=True,
    ):
        ell = int(ell_value)
        value = lpmv(2, ell, x)
        previous = np.zeros_like(value) if ell == 2 else lpmv(2, ell - 1, x)
        first = (ell * x * value - (ell + 2.0) * previous) / sine
        second = -(x / sine) * first - (
            ell * (ell + 1.0) - 4.0 / (sine * sine)
        ) * value
        G += coefficient * value
        G_theta += coefficient * first
        G_theta_theta += coefficient * second

    order = series.reduction_order
    if order == 0:
        return G, G_theta, G_theta_theta
    denominator = 1.0 - x
    weight = denominator ** (-order)
    weight_theta = -order * sine * denominator ** (-order - 1)
    weight_theta_theta = (
        order * (order + 1.0) * sine * sine * denominator ** (-order - 2)
        - order * x * denominator ** (-order - 1)
    )
    values = weight * G
    first = weight_theta * G + weight * G_theta
    second = (
        weight_theta_theta * G
        + 2.0 * weight_theta * G_theta
        + weight * G_theta_theta
    )
    return values, first, second


def _finite_complex(values: NDArray[np.complex128]) -> bool:
    return bool(np.all(np.isfinite(values.real)) and np.all(np.isfinite(values.imag)))


def _readonly(values: NDArray[np.generic]) -> NDArray[np.generic]:
    copied = np.array(values, copy=True, order="C")
    copied.flags.writeable = False
    return copied


__all__ = [
    "HybridPhaseSeries",
    "ParityScatteringSeries",
    "ReducedLegendreSeries",
    "ScatteringMatrixResult",
    "evaluate_reduced_legendre_series",
    "matched_schwarzschild_phase_factors",
    "outer_matching_phase_corrected",
    "parity_scattering_series",
    "poisson_sasaki_odd_phase_factor",
    "reduce_legendre_series",
    "reduce_truncated_legendre_series",
    "scattering_matrix_cross_section",
    "schwarzschild_even_from_odd",
]
