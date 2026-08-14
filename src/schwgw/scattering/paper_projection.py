"""Paper-facing polarization projections with explicit inference boundaries."""

from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Mapping

import numpy as np

from schwgw.backgrounds.base import StaticSphericalBackground
from schwgw.numerics import BoundaryConfig, solve_radial_mode
from schwgw.scattering.partial_wave import (
    Q011ZConjugation,
    RadialSolver,
    StrictNPAssemblyResult,
    compute_strict_np_scalars,
)
from schwgw.scattering.weyl import StrictNPScalars


@dataclass(frozen=True)
class LHZEq42ResponseResult:
    """Diagonal response columns inferred for Li--Hou--Zhao Figs. 5--6."""

    F_plus: complex
    F_cross: complex
    h_plus_from_plus: complex
    h_cross_from_cross: complex
    h_cross_from_plus: complex
    h_plus_from_cross: complex
    plus_strict_np: StrictNPScalars
    cross_strict_np: StrictNPScalars
    diagnostics: Mapping[str, object]

    def __post_init__(self) -> None:
        for name in (
            "F_plus",
            "F_cross",
            "h_plus_from_plus",
            "h_cross_from_cross",
            "h_cross_from_plus",
            "h_plus_from_cross",
        ):
            value = complex(getattr(self, name))
            if not math.isfinite(value.real) or not math.isfinite(value.imag):
                raise ValueError(f"{name} must be finite.")
            object.__setattr__(self, name, value)
        for name in ("plus_strict_np", "cross_strict_np"):
            value = getattr(self, name)
            if not isinstance(value, StrictNPScalars) or value.frame != "incident":
                raise TypeError(f"{name} must be incident-frame StrictNPScalars.")
        object.__setattr__(self, "diagnostics", MappingProxyType(dict(self.diagnostics)))


def lhz_eq42_positive_frequency_projection(
    k: float,
    strict_np: StrictNPScalars,
) -> tuple[complex, complex]:
    r"""Return the complex continuation of paper Eqs. (42a)--(42b).

    For the frozen ``exp(-ikt)`` convention this candidate continuation is

    ``h_plus = -(Psi4 + Psi0)/k**2`` and
    ``h_cross = -i*(Psi4 - Psi0)/k**2``.

    The paper states the real-time equations but does not state this
    analytic-signal bridge explicitly, so callers must retain the inference
    label in their output metadata.
    """

    k_value = float(k)
    if not math.isfinite(k_value) or k_value <= 0.0:
        raise ValueError("Wave number k must be finite and positive.")
    if not isinstance(strict_np, StrictNPScalars):
        raise TypeError("strict_np must be StrictNPScalars.")
    if strict_np.frame != "incident":
        raise ValueError("strict_np must be in the incident frame.")
    return (
        -(strict_np.psi4 + strict_np.psi0) / k_value**2,
        -1.0j * (strict_np.psi4 - strict_np.psi0) / k_value**2,
    )


def compute_lhz_eq42_response_columns(
    *,
    background: StaticSphericalBackground,
    k: float,
    r: float,
    theta: float,
    phi: float,
    A_plus: complex,
    A_cross: complex,
    lmax: int,
    boundary_config: BoundaryConfig | None = None,
    radial_solver: RadialSolver = solve_radial_mode,
    q011_z_conjugation: Q011ZConjugation = "linear",
) -> LHZEq42ResponseResult:
    """Compute the two diagonal polarization-response columns.

    ``F_plus`` is obtained from a pure-plus incident source and ``F_cross``
    from a pure-cross source.  This is the minimal response-matrix
    interpretation consistent with the paper's separate ratios in Eq. (45),
    its complex demonstration amplitudes, and the near-coincident markers in
    Fig. 5.  It remains an explicitly labelled reconstruction hypothesis,
    not a verbatim algorithm supplied by the authors.
    """

    plus_amplitude = complex(A_plus)
    cross_amplitude = complex(A_cross)
    if plus_amplitude == 0.0j or cross_amplitude == 0.0j:
        raise ValueError("A_plus and A_cross must both be nonzero response probes.")

    plus = compute_strict_np_scalars(
        background=background,
        k=k,
        r=r,
        theta=theta,
        phi=phi,
        A_plus=plus_amplitude,
        A_cross=0.0j,
        lmax=lmax,
        boundary_config=boundary_config,
        radial_solver=radial_solver,
        q011_z_conjugation=q011_z_conjugation,
    )
    cross = compute_strict_np_scalars(
        background=background,
        k=k,
        r=r,
        theta=theta,
        phi=phi,
        A_plus=0.0j,
        A_cross=cross_amplitude,
        lmax=lmax,
        boundary_config=boundary_config,
        radial_solver=radial_solver,
        q011_z_conjugation=q011_z_conjugation,
    )
    h_plus_from_plus, h_cross_from_plus = lhz_eq42_positive_frequency_projection(
        k, plus.scalars
    )
    h_plus_from_cross, h_cross_from_cross = lhz_eq42_positive_frequency_projection(
        k, cross.scalars
    )
    phase = np.exp(1.0j * float(k) * float(r) * math.cos(float(theta)))
    denominator_plus = plus_amplitude * phase
    denominator_cross = cross_amplitude * phase
    diagonal_scale = max(
        abs(h_plus_from_plus),
        abs(h_cross_from_cross),
        np.finfo(float).tiny,
    )
    reflection_plane_leakage = max(
        abs(h_cross_from_plus),
        abs(h_plus_from_cross),
    ) / diagonal_scale
    return LHZEq42ResponseResult(
        F_plus=h_plus_from_plus / denominator_plus,
        F_cross=h_cross_from_cross / denominator_cross,
        h_plus_from_plus=h_plus_from_plus,
        h_cross_from_cross=h_cross_from_cross,
        h_cross_from_plus=h_cross_from_plus,
        h_plus_from_cross=h_plus_from_cross,
        plus_strict_np=plus.scalars,
        cross_strict_np=cross.scalars,
        diagnostics={
            "projection": "Li-Hou-Zhao Eqs. (42a,b), positive-frequency continuation",
            "transmission_denominator": "Li-Hou-Zhao Eq. (46)",
            "response_surface": "pure-plus diagonal / pure-cross diagonal",
            "inference_status": "paper-consistent reconstruction hypothesis",
            "physical_claim": False,
            "observable_bridge_validated": False,
            "positive_frequency_reality_bridge_validated": False,
            "reflection_plane_expected_decoupling": True,
            "reflection_plane_off_diagonal_relative": float(
                reflection_plane_leakage
            ),
            "reflection_plane_decoupling_validated": bool(
                abs(float(phi)) <= 1.0e-14
                and reflection_plane_leakage <= 1.0e-8
            ),
            "radial_source_convention": (
                "Li-Hou-Zhao Eq. (35g,h) literal conjugates"
                if q011_z_conjugation == "literal_conjugate"
                else "existing linear positive-frequency Z1/Z0"
            ),
            "route_b_used": False,
            "psi2_used_in_plus_or_cross": False,
            "plus_assembly": dict(plus.diagnostics),
            "cross_assembly": dict(cross.diagnostics),
        },
    )


def strict_np_vector(result: StrictNPAssemblyResult | StrictNPScalars) -> np.ndarray:
    """Return ``Psi0..Psi4`` in a stable complex vector for diagnostics."""

    scalars = result.scalars if isinstance(result, StrictNPAssemblyResult) else result
    if not isinstance(scalars, StrictNPScalars):
        raise TypeError("result must contain StrictNPScalars.")
    return np.asarray(list(scalars.as_mapping().values()), dtype=np.complex128)


__all__ = [
    "LHZEq42ResponseResult",
    "compute_lhz_eq42_response_columns",
    "lhz_eq42_positive_frequency_projection",
    "strict_np_vector",
]
