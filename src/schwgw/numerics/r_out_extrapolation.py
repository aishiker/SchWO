"""Finite-outer-boundary ladders and inverse-radius extrapolation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ROutExtrapolation:
    r_out: np.ndarray
    values: np.ndarray
    extrapolated: np.ndarray
    linear_extrapolated: np.ndarray
    quadratic_extrapolated: np.ndarray
    uncertainty: np.ndarray
    adjacent_relative_change: np.ndarray
    fit_residual: np.ndarray


def extrapolate_r_out_ladder(
    r_out: np.ndarray | tuple[float, ...] | list[float],
    values: np.ndarray,
) -> ROutExtrapolation:
    """Extrapolate complex observables linearly/quadratically in ``1/r_out``.

    The ladder axis is the first axis of ``values``.  Three or more radii are
    required so that a quadratic intercept and a linear-vs-quadratic
    truncation estimate are both available.  This is an evidence surface, not
    a license to hide non-converged fixed-radius data: callers must retain the
    complete ladder and inspect ``uncertainty`` and adjacent changes.
    """

    radii = np.asarray(r_out, dtype=np.float64)
    observed = np.asarray(values, dtype=np.complex128)
    if radii.ndim != 1 or radii.size < 3:
        raise ValueError("r_out ladder must be a one-dimensional sequence of length >= 3")
    if not np.all(np.isfinite(radii)) or np.any(radii <= 0.0):
        raise ValueError("r_out ladder must contain finite positive radii")
    if np.any(np.diff(radii) <= 0.0):
        raise ValueError("r_out ladder must be strictly increasing")
    if observed.shape[:1] != radii.shape:
        raise ValueError("values first axis must match the r_out ladder")
    if not np.all(np.isfinite(observed)):
        raise ValueError("r_out ladder values must be finite")

    inverse = 1.0 / radii
    flattened = observed.reshape(radii.size, -1)
    linear = np.empty(flattened.shape[1], dtype=np.complex128)
    quadratic = np.empty_like(linear)
    fitted = np.empty_like(flattened)
    for index in range(flattened.shape[1]):
        linear_coefficients = np.polynomial.polynomial.polyfit(
            inverse, flattened[:, index], deg=1
        )
        quadratic_coefficients = np.polynomial.polynomial.polyfit(
            inverse, flattened[:, index], deg=2
        )
        linear[index] = linear_coefficients[0]
        quadratic[index] = quadratic_coefficients[0]
        fitted[:, index] = np.polynomial.polynomial.polyval(
            inverse, quadratic_coefficients
        )
    target_shape = observed.shape[1:]
    linear = linear.reshape(target_shape)
    quadratic = quadratic.reshape(target_shape)
    uncertainty = np.abs(quadratic - linear)
    denominator = np.maximum(
        1.0,
        np.maximum(np.abs(observed[1:]), np.abs(observed[:-1])),
    )
    adjacent = np.abs(observed[1:] - observed[:-1]) / denominator
    fit_residual = np.max(
        np.abs(fitted.reshape(observed.shape) - observed), axis=0
    )
    return ROutExtrapolation(
        r_out=radii,
        values=observed,
        extrapolated=quadratic,
        linear_extrapolated=linear,
        quadratic_extrapolated=quadratic,
        uncertainty=uncertainty,
        adjacent_relative_change=adjacent,
        fit_residual=fit_residual,
    )


__all__ = ["ROutExtrapolation", "extrapolate_r_out_ladder"]
