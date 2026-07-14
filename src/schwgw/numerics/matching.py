from __future__ import annotations

import numpy as np

from schwgw.backgrounds.base import StaticSphericalBackground


def match_outer_asymptotic(
    *,
    psi: complex,
    dpsi_dr: complex,
    r: float,
    k: float,
    background: StaticSphericalBackground,
) -> tuple[complex, complex, float, float]:
    """Match a radial state to A_in exp(-ikr*) + A_out exp(+ikr*)."""
    if k <= 0.0:
        raise ValueError("Wave number k must be positive.")
    if r <= background.horizon_radius:
        raise ValueError("Outer matching requires r > r_horizon.")

    r_star = background.r_star(r)
    f = background.f(r)
    ingoing = np.exp(-1j * k * r_star)
    outgoing = np.exp(1j * k * r_star)
    matrix = np.array(
        [
            [ingoing, outgoing],
            [(-1j * k / f) * ingoing, (1j * k / f) * outgoing],
        ],
        dtype=complex,
    )
    rhs = np.array([psi, dpsi_dr], dtype=complex)
    A_in, A_out = np.linalg.solve(matrix, rhs)
    reconstructed = matrix @ np.array([A_in, A_out], dtype=complex)
    denominator = max(float(np.linalg.norm(rhs)), np.finfo(float).eps)
    residual = float(np.linalg.norm(reconstructed - rhs) / denominator)
    condition_number = float(np.linalg.cond(matrix))
    return complex(A_in), complex(A_out), residual, condition_number
