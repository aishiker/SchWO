"""Wigner-D functions wrapped to the project convention."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.special import eval_jacobi, gammaln


def _validate_wigner_indices(ell: int, m: int, mp: int) -> None:
    if not all(isinstance(value, int) for value in (ell, m, mp)):
        raise TypeError("ell, m, and mp must be integers")
    if ell < 0:
        raise ValueError("ell must be non-negative")
    if abs(m) > ell or abs(mp) > ell:
        raise ValueError("abs(m) and abs(mp) must be <= ell")


def _minus_one_power(power: int) -> int:
    return -1 if power % 2 else 1


def _standard_small_d_scalar(ell: int, row_m: int, col_m: int, beta: float) -> float:
    sign = 1
    row = row_m
    col = col_m
    if row + col < 0:
        sign *= _minus_one_power(row - col)
        row = -row
        col = -col
    if row < col:
        sign *= _minus_one_power(row - col)
        row, col = col, row

    alpha = row - col
    beta_param = row + col
    degree = ell - row
    log_prefactor = 0.5 * (
        gammaln(ell + row + 1)
        + gammaln(ell - row + 1)
        - gammaln(ell + col + 1)
        - gammaln(ell - col + 1)
    )
    prefactor = math.exp(log_prefactor)
    sin_half = math.sin(0.5 * beta)
    cos_half = math.cos(0.5 * beta)

    return (
        sign
        * _minus_one_power(alpha)
        * prefactor
        * sin_half**alpha
        * cos_half**beta_param
        * float(eval_jacobi(degree, alpha, beta_param, math.cos(beta)))
    )


def _standard_small_d(ell: int, row_m: int, col_m: int, beta: Any) -> np.ndarray:
    beta_array = np.asarray(beta)
    if beta_array.shape == ():
        return np.asarray(_standard_small_d_scalar(ell, row_m, col_m, float(beta_array)))

    result = np.empty(beta_array.shape, dtype=float)
    for index in np.ndindex(beta_array.shape):
        result[index] = _standard_small_d_scalar(ell, row_m, col_m, float(beta_array[index]))
    return result


def _project_small_d(ell: int, m: int, mp: int, beta: Any) -> np.ndarray:
    # Preserve the project wrapper's established small-d order.  Downstream
    # partial-wave validation fixes this active/passive convention.
    return _standard_small_d(ell, mp, m, beta)


def wigner_D(ell: int, m: int, mp: int, alpha: Any, beta: Any, gamma: Any) -> np.ndarray:
    """Return ``D^ell_{m,mp}(alpha,beta,gamma)``.

    Project convention:
    ``D = exp(-i m alpha) d^ell_{m,mp}(beta) exp(-i mp gamma)``.
    """

    _validate_wigner_indices(ell, m, mp)
    small_d = _project_small_d(ell, m, mp, beta)
    return np.exp(-1j * m * np.asarray(alpha)) * small_d * np.exp(
        -1j * mp * np.asarray(gamma)
    )
