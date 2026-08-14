"""Convention-explicit complex comparisons for Phase-6 waveform routes."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping

import numpy as np


PROJECT_OUTGOING_PSI4_CONVENTION = (
    "signature=-+++; Fourier=exp(-ikt); propagation=+z; "
    "incident_cartesian_tetrad; Psi4=-k^2(h_plus-i h_cross)"
)


@dataclass(frozen=True)
class ComplexRouteComparison:
    """One complex comparison with separate numerical and phase diagnostics."""

    reference_route: str
    candidate_route: str
    absolute_difference: float
    relative_difference: float | None
    phase_difference: float | None
    reference_amplitude: float
    candidate_amplitude: float
    phase_amplitude_floor: float
    phase_resolved: bool
    genuinely_independent: bool
    independence_provenance: str
    convention: str


def outgoing_strain_to_project_strict_np_psi4(
    *,
    k: float,
    h_plus: complex,
    h_cross: complex,
) -> complex:
    """Return the strict-NP outgoing ``Psi4`` in the project's flat oracle.

    This is the exact convention realized by
    ``direct_cartesian_tt_strict_np_weyl``.  It is intentionally not replaced
    by a literature formula with a potentially different Riemann or tetrad
    sign.
    """

    k_value = float(k)
    plus = complex(h_plus)
    cross = complex(h_cross)
    if not math.isfinite(k_value) or k_value <= 0.0:
        raise ValueError("k must be finite and positive")
    if not _finite_complex(plus) or not _finite_complex(cross):
        raise ValueError("strain amplitudes must be finite")
    return -(k_value**2) * (plus - 1.0j * cross)


def compare_complex_routes(
    reference: complex,
    candidate: complex,
    *,
    reference_route: str,
    candidate_route: str,
    genuinely_independent: bool,
    independence_provenance: str,
    phase_amplitude_floor: float,
    convention: str,
) -> ComplexRouteComparison:
    """Compare two complex amplitudes without hiding an absolute phase offset."""

    reference_value = complex(reference)
    candidate_value = complex(candidate)
    for value in (reference_value, candidate_value):
        if not _finite_complex(value):
            raise ValueError("route amplitudes must be finite")
    for label in (
        reference_route,
        candidate_route,
        independence_provenance,
        convention,
    ):
        if not isinstance(label, str) or not label.strip():
            raise ValueError("route labels and convention must be non-empty")
    if type(genuinely_independent) is not bool:
        raise TypeError("genuinely_independent must be an exact bool")
    amplitude_floor = float(phase_amplitude_floor)
    if not math.isfinite(amplitude_floor) or amplitude_floor < 0.0:
        raise ValueError("phase_amplitude_floor must be finite and non-negative")
    absolute = abs(candidate_value - reference_value)
    reference_amplitude = abs(reference_value)
    candidate_amplitude = abs(candidate_value)
    relative = (
        None
        if reference_amplitude <= amplitude_floor
        else absolute / reference_amplitude
    )
    phase = None
    if reference_amplitude > amplitude_floor and candidate_amplitude > amplitude_floor:
        phase = float(np.angle(candidate_value / reference_value))
    return ComplexRouteComparison(
        reference_route=reference_route,
        candidate_route=candidate_route,
        absolute_difference=float(absolute),
        relative_difference=None if relative is None else float(relative),
        phase_difference=phase,
        reference_amplitude=float(reference_amplitude),
        candidate_amplitude=float(candidate_amplitude),
        phase_amplitude_floor=amplitude_floor,
        phase_resolved=phase is not None,
        genuinely_independent=genuinely_independent,
        independence_provenance=independence_provenance,
        convention=convention,
    )


def pairwise_route_comparisons(
    routes: Mapping[str, complex],
    *,
    independence: Mapping[tuple[str, str], bool],
    independence_provenance: Mapping[tuple[str, str], str],
    phase_amplitude_floor: float,
    convention: str,
) -> tuple[ComplexRouteComparison, ...]:
    """Return all unordered pair comparisons for named waveform routes."""

    if not isinstance(routes, Mapping) or len(routes) < 2:
        raise ValueError("at least two named routes are required")
    labels = tuple(routes)
    if any(not isinstance(label, str) or not label.strip() for label in labels):
        raise ValueError("route names must be non-empty strings")
    expected_pairs = tuple(
        (first, second)
        for first_index, first in enumerate(labels[:-1])
        for second in labels[first_index + 1 :]
    )
    independence_values = _canonical_pair_inventory(
        independence,
        labels=labels,
        expected_pairs=expected_pairs,
        label="independence",
    )
    provenance_values = _canonical_pair_inventory(
        independence_provenance,
        labels=labels,
        expected_pairs=expected_pairs,
        label="independence provenance",
    )
    comparisons: list[ComplexRouteComparison] = []
    for first, second in expected_pairs:
        independent = independence_values[(first, second)]
        provenance = provenance_values[(first, second)]
        if type(independent) is not bool:
            raise TypeError("independence declarations must be exact bools")
        comparisons.append(
            compare_complex_routes(
                routes[first],
                routes[second],
                reference_route=first,
                candidate_route=second,
                genuinely_independent=independent,
                independence_provenance=provenance,
                phase_amplitude_floor=phase_amplitude_floor,
                convention=convention,
            )
        )
    return tuple(comparisons)


def _canonical_pair_inventory(
    values: Mapping[tuple[str, str], object],
    *,
    labels: tuple[str, ...],
    expected_pairs: tuple[tuple[str, str], ...],
    label: str,
) -> dict[tuple[str, str], object]:
    """Bind exactly one directed record to every unordered route pair."""

    if not isinstance(values, Mapping):
        raise TypeError(f"{label} must be a mapping")
    label_set = set(labels)
    expected_sets = {frozenset(pair): pair for pair in expected_pairs}
    result: dict[tuple[str, str], object] = {}
    seen: set[frozenset[str]] = set()
    for key, value in values.items():
        if (
            not isinstance(key, tuple)
            or len(key) != 2
            or key[0] == key[1]
            or set(key) - label_set
        ):
            raise ValueError(f"{label} contains an invalid or extra route pair")
        unordered = frozenset(key)
        canonical = expected_sets.get(unordered)
        if canonical is None or unordered in seen:
            raise ValueError(f"{label} contains a duplicate/conflicting route pair")
        seen.add(unordered)
        result[canonical] = value
    if seen != set(expected_sets):
        raise ValueError(f"{label} inventory is incomplete")
    return result


def _finite_complex(value: complex) -> bool:
    return math.isfinite(value.real) and math.isfinite(value.imag)


__all__ = [
    "PROJECT_OUTGOING_PSI4_CONVENTION",
    "ComplexRouteComparison",
    "compare_complex_routes",
    "outgoing_strain_to_project_strict_np_psi4",
    "pairwise_route_comparisons",
]
