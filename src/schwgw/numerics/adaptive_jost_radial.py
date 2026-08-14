"""Generic outer-radius conditioning for the scaled-tortoise radial solver.

The immutable Phase-6 V1 solver in :mod:`scaled_tortoise_radial` deliberately
keeps the caller-provided outer matching radius fixed.  That contract exposed
an honest failure at ``kM=8`` and very large ``ell``: a 160-term finite-radius
Jost expansion is not asymptotic enough at ``r_out=300M``.  Its columns acquire
an arbitrary large common normalization, so an absolute coefficient floor can
reject an otherwise well-resolved incoming/outgoing ratio.

This module is a new backend revision.  It leaves the evidence-bound V1 source
unchanged and selects the first radius in a dimensionless geometric ladder for
which the *basis itself* passes local ODE-residual, tail, determinant, and
condition-number gates.  It then delegates the propagation to the unchanged
pole-safe full-state solver.  The policy is independent of paper figures and
of any named mode envelope.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
import math
from typing import Final

import numpy as np

from schwgw.backgrounds.base import StaticSphericalBackground
from schwgw.numerics.conditioned_radial import (
    ConditionedRadialRequest,
    ConditionedRadialResult,
)
from schwgw.numerics.matching import outer_asymptotic_basis
from schwgw.numerics.scaled_tortoise_radial import (
    solve_scaled_tortoise_radial_at_radius,
)

OUTER_RADIUS_FACTORS: Final[tuple[float, ...]] = (1.0, 2.0, 4.0, 8.0)
JOST_SERIES_RESIDUAL_LIMIT: Final[float] = 1.0e-10
JOST_TAIL_RATIO_LIMIT: Final[float] = 1.0e-8
JOST_CONDITION_NUMBER_LIMIT: Final[float] = 1.0e8
JOST_RELATIVE_DETERMINANT_MINIMUM: Final[float] = 1.0e-8


@dataclass(frozen=True)
class JostBasisQuality:
    """Finite, JSON-safe diagnostics for one candidate matching radius."""

    requested_r_out_M: float
    candidate_r_out_M: float
    radius_factor: float
    series_order: int
    incoming_series_residual: float
    outgoing_series_residual: float
    maximum_series_residual: float
    incoming_tail_ratio: float
    outgoing_tail_ratio: float
    maximum_tail_ratio: float
    condition_number: float
    relative_determinant: float
    state: str
    failure: str | None

    def as_record(self) -> dict[str, float | int | str | None]:
        """Return a canonical-JSON-compatible record."""

        return asdict(self)


@dataclass(frozen=True)
class AdaptiveJostSelection:
    """The first passing member of a generic outer-radius ladder."""

    requested_r_out_M: float
    selected_r_out_M: float
    selected_radius_factor: float
    selected_quality: JostBasisQuality
    candidates: tuple[JostBasisQuality, ...]

    def as_record(self) -> dict[str, object]:
        return {
            "requested_r_out_M": self.requested_r_out_M,
            "selected_r_out_M": self.selected_r_out_M,
            "selected_radius_factor": self.selected_radius_factor,
            "selected_quality": self.selected_quality.as_record(),
            "candidates": [candidate.as_record() for candidate in self.candidates],
        }


def assess_jost_basis_at_radius(
    request: ConditionedRadialRequest,
    background: StaticSphericalBackground,
    *,
    candidate_r_out: float,
) -> JostBasisQuality:
    """Assess the requested Jost basis without running a radial propagation."""

    requested = float(request.r_out)
    candidate = float(candidate_r_out)
    if not math.isfinite(candidate) or candidate < requested:
        raise ValueError("candidate_r_out must be finite and at least request.r_out")
    factor = candidate / requested
    largest = float(np.finfo(float).max)
    try:
        incoming = outer_asymptotic_basis(
            sector=request.sector,
            ell=request.ell,
            r=candidate,
            k=request.k,
            background=background,
            sign=-1,
            basis=request.outer_basis,
            series_order=request.outer_series_order,
        )
        outgoing = outer_asymptotic_basis(
            sector=request.sector,
            ell=request.ell,
            r=candidate,
            k=request.k,
            background=background,
            sign=1,
            basis=request.outer_basis,
            series_order=request.outer_series_order,
        )
        matrix = np.asarray(
            [
                [incoming.psi, outgoing.psi],
                [incoming.dpsi_dr, outgoing.dpsi_dr],
            ],
            dtype=np.complex128,
        )
        column_norms = np.linalg.norm(matrix, axis=0)
        determinant = complex(np.linalg.det(matrix))
        norm_product = float(column_norms[0] * column_norms[1])
        relative_determinant = float(abs(determinant) / norm_product)
        condition_number = float(np.linalg.cond(matrix))
        maximum_residual = float(
            max(incoming.series_residual, outgoing.series_residual)
        )
        maximum_tail = float(max(incoming.tail_ratio, outgoing.tail_ratio))
        finite = all(
            math.isfinite(value)
            for value in (
                maximum_residual,
                maximum_tail,
                condition_number,
                relative_determinant,
                norm_product,
            )
        )
        passed = bool(
            finite
            and norm_product > np.finfo(float).tiny
            and maximum_residual <= JOST_SERIES_RESIDUAL_LIMIT
            and maximum_tail <= JOST_TAIL_RATIO_LIMIT
            and condition_number <= JOST_CONDITION_NUMBER_LIMIT
            and relative_determinant >= JOST_RELATIVE_DETERMINANT_MINIMUM
        )
        return JostBasisQuality(
            requested_r_out_M=requested,
            candidate_r_out_M=candidate,
            radius_factor=factor,
            series_order=int(request.outer_series_order),
            incoming_series_residual=float(incoming.series_residual),
            outgoing_series_residual=float(outgoing.series_residual),
            maximum_series_residual=maximum_residual,
            incoming_tail_ratio=float(incoming.tail_ratio),
            outgoing_tail_ratio=float(outgoing.tail_ratio),
            maximum_tail_ratio=maximum_tail,
            condition_number=(
                condition_number if math.isfinite(condition_number) else largest
            ),
            relative_determinant=(
                relative_determinant if math.isfinite(relative_determinant) else 0.0
            ),
            state="PASS" if passed else "FAIL",
            failure=None if passed else "generic Jost basis quality gates not met",
        )
    except Exception as exc:
        return JostBasisQuality(
            requested_r_out_M=requested,
            candidate_r_out_M=candidate,
            radius_factor=factor,
            series_order=int(request.outer_series_order),
            incoming_series_residual=largest,
            outgoing_series_residual=largest,
            maximum_series_residual=largest,
            incoming_tail_ratio=largest,
            outgoing_tail_ratio=largest,
            maximum_tail_ratio=largest,
            condition_number=largest,
            relative_determinant=0.0,
            state="FAIL",
            failure=f"{type(exc).__name__}: {exc}",
        )


def select_conditioned_outer_radius(
    request: ConditionedRadialRequest,
    background: StaticSphericalBackground,
    *,
    radius_factors: tuple[float, ...] = OUTER_RADIUS_FACTORS,
) -> AdaptiveJostSelection:
    """Select the first radius whose Jost columns pass generic quality gates."""

    if not radius_factors or radius_factors[0] != 1.0:
        raise ValueError("radius_factors must start at 1.0")
    if any(
        not math.isfinite(factor) or factor <= 0.0 for factor in radius_factors
    ) or any(left >= right for left, right in zip(radius_factors, radius_factors[1:])):
        raise ValueError("radius_factors must be finite, positive, and increasing")

    candidates: list[JostBasisQuality] = []
    for factor in radius_factors:
        quality = assess_jost_basis_at_radius(
            request,
            background,
            candidate_r_out=float(request.r_out) * factor,
        )
        candidates.append(quality)
        if quality.state == "PASS":
            return AdaptiveJostSelection(
                requested_r_out_M=float(request.r_out),
                selected_r_out_M=quality.candidate_r_out_M,
                selected_radius_factor=quality.radius_factor,
                selected_quality=quality,
                candidates=tuple(candidates),
            )

    compact = json.dumps(
        [candidate.as_record() for candidate in candidates],
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    raise RuntimeError(f"no conditioned Jost outer radius passed: {compact}")


def solve_adaptive_jost_radial_at_radius(
    request: ConditionedRadialRequest,
    background: StaticSphericalBackground,
) -> ConditionedRadialResult:
    """Solve after generic Jost-basis conditioning of the matching radius."""

    selection = select_conditioned_outer_radius(request, background)
    effective_request = replace(request, r_out=selection.selected_r_out_M)
    base_result = solve_scaled_tortoise_radial_at_radius(
        effective_request,
        background,
    )
    quality = selection.selected_quality
    diagnostics = dict(base_result.diagnostics)
    diagnostics.update(
        {
            "method": "adaptive_outer_radius_scaled_tortoise_full_state_jost_ratio",
            "backend": "scipy_float64_adaptive_jost_scaled_tortoise_v2",
            "backend_version": 2,
            "base_backend": str(base_result.diagnostics["backend"]),
            "requested_r_out": selection.requested_r_out_M,
            "selected_r_out": selection.selected_r_out_M,
            "selected_r_out_factor": selection.selected_radius_factor,
            "adaptive_outer_radius_used": selection.selected_radius_factor != 1.0,
            "outer_radius_selector": "generic_jost_residual_tail_conditioning_v1",
            "outer_radius_selector_candidates": json.dumps(
                [candidate.as_record() for candidate in selection.candidates],
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            ),
            "selected_jost_series_residual": quality.maximum_series_residual,
            "selected_jost_tail_ratio": quality.maximum_tail_ratio,
            "selected_jost_condition_number": quality.condition_number,
            "selected_jost_relative_determinant": quality.relative_determinant,
            "jost_series_residual_limit": JOST_SERIES_RESIDUAL_LIMIT,
            "jost_tail_ratio_limit": JOST_TAIL_RATIO_LIMIT,
            "jost_condition_number_limit": JOST_CONDITION_NUMBER_LIMIT,
            "jost_relative_determinant_minimum": JOST_RELATIVE_DETERMINANT_MINIMUM,
            "paper_specific_envelope_used": False,
            "scientific_acceptance": False,
            "independent_validation": False,
        }
    )
    return replace(base_result, diagnostics=diagnostics)


__all__ = [
    "AdaptiveJostSelection",
    "JOST_CONDITION_NUMBER_LIMIT",
    "JOST_RELATIVE_DETERMINANT_MINIMUM",
    "JOST_SERIES_RESIDUAL_LIMIT",
    "JOST_TAIL_RATIO_LIMIT",
    "JostBasisQuality",
    "OUTER_RADIUS_FACTORS",
    "assess_jost_basis_at_radius",
    "select_conditioned_outer_radius",
    "solve_adaptive_jost_radial_at_radius",
]
