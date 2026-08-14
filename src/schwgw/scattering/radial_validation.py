"""Phase-6 radial S-matrix and flux-accounting diagnostics."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol


class _RadialSolutionLike(Protocol):
    k: float
    A_in: complex
    A_out: complex
    diagnostics: object


@dataclass(frozen=True)
class RadialFluxBudget:
    """Dimensionless flux fractions for a unit incident wave at infinity."""

    reflection: float
    horizon_transmission: float
    balance_residual: float
    recorded_solver_residual: float
    backend: str
    independently_validated: bool = False

    def __post_init__(self) -> None:
        for name in (
            "reflection",
            "horizon_transmission",
            "balance_residual",
            "recorded_solver_residual",
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and nonnegative.")
            object.__setattr__(self, name, value)
        if not isinstance(self.backend, str) or not self.backend.strip():
            raise ValueError("backend must be a non-empty string.")

    def to_metadata(self) -> dict[str, object]:
        return {
            "reflection_flux_fraction": self.reflection,
            "horizon_transmission_flux_fraction": self.horizon_transmission,
            "unitarity_balance_residual": self.balance_residual,
            "recorded_solver_residual": self.recorded_solver_residual,
            "backend": self.backend,
            "independently_validated": self.independently_validated,
            "acceptance_scope": "one radial mode only",
        }


def radial_flux_budget(solution: _RadialSolutionLike) -> RadialFluxBudget:
    """Compute ``|R|^2 + |T|^2 - 1`` from one radial solution.

    The solver diagnostic ``expected_flux_scale`` is the horizon Wronskian
    scale ``2 k |A_H|^2``.  Dividing it by the incident infinity flux
    ``2 k |A_in|^2`` gives the horizon-transmission fraction.  This accounting
    is a necessary internal check, not an independent validation certificate.
    """

    k = float(solution.k)
    if not math.isfinite(k) or k <= 0.0:
        raise ValueError("solution.k must be finite and positive.")
    incoming = complex(solution.A_in)
    outgoing = complex(solution.A_out)
    if not _finite_complex(incoming) or not _finite_complex(outgoing):
        raise ValueError("A_in and A_out must be finite.")
    incoming_norm = abs(incoming) ** 2
    if incoming_norm == 0.0:
        raise ValueError("A_in must be nonzero.")
    diagnostics = solution.diagnostics
    horizon_scale = float(getattr(diagnostics, "expected_flux_scale"))
    recorded = float(getattr(diagnostics, "flux_residual"))
    backend = str(getattr(diagnostics, "solver"))
    reflection = abs(outgoing) ** 2 / incoming_norm
    transmission = horizon_scale / (2.0 * k * incoming_norm)
    return RadialFluxBudget(
        reflection=reflection,
        horizon_transmission=transmission,
        balance_residual=abs(reflection + transmission - 1.0),
        recorded_solver_residual=recorded,
        backend=backend,
        independently_validated=False,
    )


def _finite_complex(value: complex) -> bool:
    return math.isfinite(value.real) and math.isfinite(value.imag)


__all__ = ["RadialFluxBudget", "radial_flux_budget"]
