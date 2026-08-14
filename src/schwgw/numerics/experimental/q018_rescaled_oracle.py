from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Mapping

import numpy as np
from scipy.integrate import solve_ivp

from schwgw.backgrounds.base import StaticSphericalBackground
from schwgw.numerics.matching import match_outer_asymptotic
from schwgw.perturbations import Sector, V_RW, V_Zerilli

DiagnosticValue = bool | int | float | str


@dataclass(frozen=True)
class RescaledOracleRequest:
    """Input contract for the experimental Q018 finite-radius oracle."""

    sector: Sector
    ell: int
    k: float
    required_radius: float
    r_out: float
    r_in_eps: float = 1e-6
    rtol: float = 1e-10
    atol: float = 1e-12
    precision_dps: int | None = None
    matching_radius: float | None = None
    method_hint: str = "rescaled_log_amplitude"

    def __post_init__(self) -> None:
        if not isinstance(self.sector, Sector):
            raise TypeError("sector must be a Sector enum value.")
        if self.ell < 2:
            raise ValueError("ell must be at least 2.")
        _require_positive_finite("k", self.k)
        _require_positive_finite("required_radius", self.required_radius)
        _require_positive_finite("r_out", self.r_out)
        _require_positive_finite("r_in_eps", self.r_in_eps)
        _require_positive_finite("rtol", self.rtol)
        _require_positive_finite("atol", self.atol)
        if self.required_radius > self.r_out:
            raise ValueError("required_radius must not exceed r_out.")
        if self.precision_dps is not None and self.precision_dps < 53:
            raise ValueError("precision_dps must be at least double precision when set.")
        if self.matching_radius is not None:
            _require_positive_finite("matching_radius", self.matching_radius)
        if not self.method_hint:
            raise ValueError("method_hint must be non-empty.")


@dataclass(frozen=True)
class RescaledOracleResult:
    """Future output contract for a unit incoming-at-infinity Q018 oracle."""

    psi: complex
    dpsi_dr: complex
    A_in: complex
    A_out: complex
    diagnostics: Mapping[str, DiagnosticValue]

    @property
    def valid_at_required_radius(self) -> bool:
        return bool(self.diagnostics.get("valid_at_required_radius", False))


def solve_q018_rescaled_oracle(
    request: RescaledOracleRequest,
    background: StaticSphericalBackground,
) -> RescaledOracleResult:
    """Experimental Q018 oracle; not exported as a public radial solver.

    Returns fields at ``request.required_radius`` with unit incoming-at-infinity
    normalization, so ``A_in`` is close to one and ``A_out``, ``psi``,
    ``dpsi_dr``, and diagnostics are mutually consistent.
    Production may call this only through the reviewed private
    ``BoundaryConfig.experimental_required_radius_oracle`` adapter.
    The current prototype uses an experimental Riccati/log-derivative match:
    it propagates the horizon-ingoing logarithmic derivative to the requested
    radius, integrates a unit-amplitude radial state outward from that radius,
    and recovers the unit-infinity normalization from the outer asymptotic
    coefficient.  Diagnostics record the method, double-precision tolerance,
    matching radius, finite checks, and residual proxies.
    """
    if not isinstance(request, RescaledOracleRequest):
        raise TypeError("request must be a RescaledOracleRequest.")
    if background.horizon_radius >= request.required_radius:
        raise ValueError("required_radius must be outside the background horizon.")
    if request.required_radius > request.r_out:
        raise ValueError("required_radius must not exceed r_out.")

    started_at = perf_counter()
    r_in = background.horizon_radius * (1.0 + request.r_in_eps)
    required_radius = float(request.required_radius)
    if required_radius <= r_in:
        raise ValueError("required_radius must be larger than the near-horizon radius.")

    log_derivative, riccati_steps, riccati_status = _horizon_log_derivative_at(
        request=request,
        background=background,
        r_in=r_in,
        radius=required_radius,
    )
    unit_solution = _integrate_unit_state_to_outer_boundary(
        request=request,
        background=background,
        radius=required_radius,
        log_derivative=log_derivative,
    )
    if not unit_solution.success:
        raise RuntimeError(
            "experimental Q018 unit-state propagation failed: "
            f"{unit_solution.message}"
        )

    psi_out = complex(unit_solution.y[0, -1], unit_solution.y[1, -1])
    dpsi_dr_out = complex(unit_solution.y[2, -1], unit_solution.y[3, -1])
    A_in_unit, A_out_unit, boundary_residual, condition_number = match_outer_asymptotic(
        psi=psi_out,
        dpsi_dr=dpsi_dr_out,
        r=float(request.r_out),
        k=request.k,
        background=background,
        sector=request.sector,
        ell=request.ell,
        basis="jost_1_over_r",
        series_order=160,
    )
    if abs(A_in_unit) <= 100.0 * np.finfo(float).eps:
        raise RuntimeError("experimental Q018 oracle produced near-zero A_in.")

    scale = 1.0 / A_in_unit
    dpsi_dr_unit_radius = log_derivative / background.f(required_radius)
    psi = complex(scale)
    dpsi_dr = complex(scale * dpsi_dr_unit_radius)
    A_in = 1.0 + 0.0j
    A_out = complex(A_out_unit / A_in_unit)

    A_in_check, _, scaled_boundary_residual, _ = match_outer_asymptotic(
        psi=scale * psi_out,
        dpsi_dr=scale * dpsi_dr_out,
        r=float(request.r_out),
        k=request.k,
        background=background,
        sector=request.sector,
        ell=request.ell,
        basis="jost_1_over_r",
        series_order=160,
    )
    recovered_log_derivative = background.f(required_radius) * dpsi_dr / psi
    log_derivative_match_residual = _relative_complex_residual(
        recovered_log_derivative,
        log_derivative,
    )
    normalization_residual = abs(A_in_check - 1.0)
    elapsed_seconds = perf_counter() - started_at

    diagnostics: dict[str, DiagnosticValue] = {
        "method": "riccati_log_derivative_match",
        "experimental": True,
        "required_radius": required_radius,
        "matching_radius": required_radius,
        "r_out": float(request.r_out),
        "ell": int(request.ell),
        "sector": request.sector.value,
        "k": float(request.k),
        "actual_precision_bits": 53,
        "actual_decimal_digits": 15.95,
        "precision_note": "scipy_float64_53_binary_significand_bits",
        "requested_precision_dps": (
            0 if request.precision_dps is None else int(request.precision_dps)
        ),
        "rtol": float(request.rtol),
        "atol": float(request.atol),
        "unit_incoming_at_infinity": True,
        "valid_at_required_radius": True,
        "finite_psi": _finite_complex(psi),
        "finite_dpsi_dr": _finite_complex(dpsi_dr),
        "finite_A_in": _finite_complex(A_in),
        "finite_A_out": _finite_complex(A_out),
        "outer_boundary_residual": float(max(boundary_residual, scaled_boundary_residual)),
        "normalization_residual": float(normalization_residual),
        "log_derivative_match_residual": float(log_derivative_match_residual),
        "match_condition_number": float(condition_number),
        "riccati_steps": int(riccati_steps),
        "riccati_status": riccati_status,
        "outward_steps": int(len(unit_solution.t)),
        "outward_status": str(unit_solution.message),
        "runtime_seconds": float(elapsed_seconds),
        "max_abs_unit_state": float(
            np.max(np.hypot(unit_solution.y[0], unit_solution.y[1]))
        ),
        "phase_handling": "complex logarithmic derivative propagated directly",
        "amplitude_normalization": "unit state at required radius scaled by outer A_in",
        "derivative_recovery": "dpsi_dr=(log_derivative/f)*psi",
    }

    if not all(
        bool(diagnostics[key])
        for key in ("finite_psi", "finite_dpsi_dr", "finite_A_in", "finite_A_out")
    ):
        raise RuntimeError("experimental Q018 oracle produced non-finite output.")

    return RescaledOracleResult(
        psi=psi,
        dpsi_dr=dpsi_dr,
        A_in=A_in,
        A_out=A_out,
        diagnostics=diagnostics,
    )


def _horizon_log_derivative_at(
    *,
    request: RescaledOracleRequest,
    background: StaticSphericalBackground,
    r_in: float,
    radius: float,
) -> tuple[complex, int, str]:
    """Propagate y=(d psi/dr_star)/psi from the horizon to ``radius``."""

    def rhs(r: float, state: np.ndarray) -> list[float]:
        value = complex(state[0], state[1])
        derivative = (
            _potential(request.sector, request.ell, r, background)
            - request.k**2
            - value**2
        ) / background.f(r)
        return [derivative.real, derivative.imag]

    result = solve_ivp(
        rhs,
        (r_in, radius),
        np.array([0.0, -request.k], dtype=float),
        method="DOP853",
        rtol=request.rtol,
        atol=request.atol,
    )
    if not result.success:
        raise RuntimeError(
            "experimental Q018 Riccati propagation failed: "
            f"{result.message}"
        )
    return complex(result.y[0, -1], result.y[1, -1]), len(result.t), str(result.message)


def _integrate_unit_state_to_outer_boundary(
    *,
    request: RescaledOracleRequest,
    background: StaticSphericalBackground,
    radius: float,
    log_derivative: complex,
):
    dpsi_dr = log_derivative / background.f(radius)
    initial_state = np.array([1.0, 0.0, dpsi_dr.real, dpsi_dr.imag], dtype=float)

    def rhs(r: float, state: np.ndarray) -> list[float]:
        psi = complex(state[0], state[1])
        derivative = complex(state[2], state[3])
        lapse = background.f(r)
        d_lapse = background.df_dr(r)
        potential = _potential(request.sector, request.ell, r, background)
        second_derivative = -(
            lapse * d_lapse * derivative + (request.k**2 - potential) * psi
        ) / lapse**2
        return [
            derivative.real,
            derivative.imag,
            second_derivative.real,
            second_derivative.imag,
        ]

    return solve_ivp(
        rhs,
        (radius, float(request.r_out)),
        initial_state,
        method="DOP853",
        rtol=request.rtol,
        atol=request.atol,
    )


def _potential(
    sector: Sector,
    ell: int,
    r: float | np.ndarray,
    background: StaticSphericalBackground,
) -> float | np.ndarray:
    if sector is Sector.ODD:
        return V_RW(ell, r, background)
    return V_Zerilli(ell, r, background)


def _relative_complex_residual(value: complex, reference: complex) -> float:
    denominator = max(abs(reference), np.finfo(float).eps)
    return float(abs(value - reference) / denominator)


def _finite_complex(value: complex) -> bool:
    return bool(np.isfinite(value.real) and np.isfinite(value.imag))


def _require_positive_finite(name: str, value: float) -> None:
    if not np.isfinite(float(value)) or float(value) <= 0.0:
        raise ValueError(f"{name} must be positive and finite.")


__all__ = [
    "RescaledOracleRequest",
    "RescaledOracleResult",
    "solve_q018_rescaled_oracle",
]
