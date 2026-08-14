"""Turning-aware inner/outer boundary policy for the Phase-6 radial solver."""

from __future__ import annotations

from dataclasses import replace
import json
import math

from schwgw.backgrounds.base import StaticSphericalBackground
from schwgw.numerics.adaptive_jost_radial import (
    AdaptiveJostSelection,
    JostBasisQuality,
    assess_jost_basis_at_radius,
)
from schwgw.numerics.conditioned_radial import (
    ConditionedRadialRequest,
    ConditionedRadialResult,
)
from schwgw.numerics.scaled_tortoise_radial import (
    solve_scaled_tortoise_radial_at_radius,
)


TURNING_RADIUS_FACTORS = (1.0, 2.0, 4.0, 8.0)


def select_physical_outer_radius(
    request: ConditionedRadialRequest,
    background: StaticSphericalBackground,
) -> AdaptiveJostSelection:
    """Select from a ladder anchored at max(requested radius, turning proxy).

    The proxy ``sqrt(ell(ell+1))/k`` is equation-based and independent of any
    paper figure or named mode envelope.  It prevents a fixed-radius ladder
    from remaining entirely inside the centrifugal forbidden region at small
    frequency.
    """

    turning_proxy = math.sqrt(request.ell * (request.ell + 1.0)) / request.k
    base = max(float(request.r_out), turning_proxy)
    candidates: list[JostBasisQuality] = []
    for factor in TURNING_RADIUS_FACTORS:
        radius = base * factor
        quality = assess_jost_basis_at_radius(
            request, background, candidate_r_out=radius
        )
        candidates.append(quality)
        if quality.state == "PASS":
            return AdaptiveJostSelection(
                requested_r_out_M=float(request.r_out),
                selected_r_out_M=quality.candidate_r_out_M,
                selected_radius_factor=quality.candidate_r_out_M / float(request.r_out),
                selected_quality=quality,
                candidates=tuple(candidates),
            )
    compact = json.dumps(
        [candidate.as_record() for candidate in candidates],
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    raise RuntimeError(f"no turning-aware Jost outer radius passed: {compact}")


def solve_physical_boundary_radial_at_radius(
    request: ConditionedRadialRequest,
    background: StaticSphericalBackground,
) -> ConditionedRadialResult:
    """Solve with the generic turning-aware outer policy and caller r_in."""

    selection = select_physical_outer_radius(request, background)
    effective = replace(request, r_out=selection.selected_r_out_M)
    result = solve_scaled_tortoise_radial_at_radius(effective, background)
    quality = selection.selected_quality
    turning_proxy = math.sqrt(request.ell * (request.ell + 1.0)) / request.k
    diagnostics = dict(result.diagnostics)
    diagnostics.update(
        {
            "adaptive_outer_radius_used": selection.selected_r_out_M
            != float(request.r_out),
            "backend": "scipy_float64_turning_aware_jost_scaled_tortoise_v3",
            "backend_version": 3,
            "base_backend": result.diagnostics["backend"],
            "independent_validation": False,
            "method": "turning_aware_outer_radius_scaled_tortoise_full_state_jost_ratio",
            "outer_radius_selector": "generic_turning_proxy_plus_jost_quality_v2",
            "outer_radius_selector_candidates": json.dumps(
                [candidate.as_record() for candidate in selection.candidates],
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            ),
            "paper_specific_envelope_used": False,
            "requested_r_out": float(request.r_out),
            "scientific_acceptance": False,
            "selected_jost_condition_number": quality.condition_number,
            "selected_jost_maximum_series_residual": quality.maximum_series_residual,
            "selected_jost_maximum_tail_ratio": quality.maximum_tail_ratio,
            "selected_jost_relative_determinant": quality.relative_determinant,
            "selected_r_out": selection.selected_r_out_M,
            "selected_r_out_factor_from_requested": selection.selected_r_out_M
            / float(request.r_out),
            "turning_proxy_M": turning_proxy,
        }
    )
    return replace(result, diagnostics=diagnostics)


__all__ = [
    "TURNING_RADIUS_FACTORS",
    "select_physical_outer_radius",
    "solve_physical_boundary_radial_at_radius",
]
