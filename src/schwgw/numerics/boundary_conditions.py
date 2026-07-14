from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from schwgw.backgrounds.base import StaticSphericalBackground


@dataclass(frozen=True)
class BoundaryConfig:
    """Radial integration domain and ODE tolerance settings."""

    r_in_eps: float = 1e-6
    r_out: float | None = None
    rtol: float = 1e-10
    atol: float = 1e-12
    method: str = "DOP853"
    max_step: float | None = None
    dense_output: bool = True
    required_eval_radius: float | None = None
    experimental_required_radius_oracle: str | None = None


def radial_domain(
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    config: BoundaryConfig,
) -> tuple[float, float]:
    """Return the exterior radial interval used by the shooting solve."""
    _validate_mode_parameters(ell=ell, k=k)
    if config.r_in_eps <= 0.0:
        raise ValueError("r_in_eps must be positive.")

    r_in = background.horizon_radius * (1.0 + config.r_in_eps)
    r_out = (
        float(config.r_out)
        if config.r_out is not None
        else float(background.asymptotic_region_hint(k, ell))
    )
    if r_out <= r_in:
        raise ValueError("r_out must be larger than the near-horizon radius r_in.")
    if config.required_eval_radius is not None:
        required_eval_radius = float(config.required_eval_radius)
        if not np.isfinite(required_eval_radius):
            raise ValueError("required_eval_radius must be finite when provided.")
        if required_eval_radius <= background.horizon_radius:
            raise ValueError("required_eval_radius must be outside the horizon.")
        if required_eval_radius > r_out:
            raise ValueError("required_eval_radius must not exceed r_out.")
    return r_in, r_out


def horizon_ingoing_initial_data(
    r_in: float,
    k: float,
    background: StaticSphericalBackground,
) -> tuple[complex, complex]:
    """Leading ingoing horizon data for exp(-i k r_star)."""
    if k <= 0.0:
        raise ValueError("Wave number k must be positive.")
    if r_in <= background.horizon_radius:
        raise ValueError("Horizon initial data require r_in > r_horizon.")

    psi = np.exp(-1j * k * background.r_star(r_in))
    dpsi_dr = (-1j * k / background.f(r_in)) * psi
    return complex(psi), complex(dpsi_dr)


def _validate_mode_parameters(ell: int, k: float) -> None:
    if ell < 2:
        raise ValueError("Radiative RW/Zerilli modes require ell >= 2.")
    if k <= 0.0:
        raise ValueError("Wave number k must be positive.")
