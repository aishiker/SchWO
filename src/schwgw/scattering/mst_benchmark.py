"""Independent BHPT Toolkit normalization checks for the local MST phases.

The external record is deliberately expressed in the scattering convention
used by :mod:`schwgw.numerics.radial_solver`::

    S_l^- = -A_out / ((-1)^l A_in).

Black Hole Perturbation Toolkit's ``ReggeWheeler`` paclet supplies ``A_in``
and ``A_out`` as the ``Incidence`` and ``Reflection`` amplitudes of its
ingoing solution.  The even-parity value in the external file is derived
from the exact Chandrasekhar/Starobinsky parity relation; it is not advertised
as a second independent radial calculation.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
import math
from pathlib import Path
from typing import Any

from schwgw.scattering.mst import MSTPhaseFactor, schwarzschild_mst_phase_factor


BHPT_MST_BENCHMARK_SCHEMA = "schwo_bhpt_reggewheeler_mst_benchmark_v1"
BHPT_MST_COMPARISON_SCHEMA = "schwo_bhpt_reggewheeler_mst_comparison_v1"
BHPT_ODD_PHASE_DEFINITION = "-Reflection/((-1)^ell*Incidence)"
DEFAULT_BENCHMARK_KM = (0.5, 1.0, 1.5, 2.0)
DEFAULT_BENCHMARK_ELL = tuple(range(20, 41))


class MSTBenchmarkError(ValueError):
    """Raised when an external MST benchmark violates its frozen contract."""


def _finite_real(value: object, *, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MSTBenchmarkError(f"{label} must be a finite JSON number")
    result = float(value)
    if not math.isfinite(result):
        raise MSTBenchmarkError(f"{label} must be finite")
    return result


def _complex_record(value: object, *, label: str) -> complex:
    if not isinstance(value, Mapping) or set(value) != {"real", "imag"}:
        raise MSTBenchmarkError(f"{label} must contain exactly real and imag")
    result = complex(
        _finite_real(value["real"], label=f"{label}.real"),
        _finite_real(value["imag"], label=f"{label}.imag"),
    )
    if result == 0.0j:
        raise MSTBenchmarkError(f"{label} must be nonzero")
    return result


def _parity_ratio(*, ell: int, kM: float) -> complex:
    sigma = (ell - 1) * ell * (ell + 1) * (ell + 2)
    epsilon = 2.0 * kM
    return complex((sigma + 6.0j * epsilon) / (sigma - 6.0j * epsilon))


def validate_bhpt_mst_benchmark(
    payload: Mapping[str, Any],
    *,
    expected_kM: Iterable[float] = DEFAULT_BENCHMARK_KM,
    expected_ell: Iterable[int] = DEFAULT_BENCHMARK_ELL,
    internal_tolerance: float = 5.0e-12,
) -> list[dict[str, Any]]:
    """Validate and normalize one external BHPT/MST JSON payload.

    No global phase, conjugation, offset, or fitted normalization is allowed.
    """

    if payload.get("schema_version") != BHPT_MST_BENCHMARK_SCHEMA:
        raise MSTBenchmarkError("unexpected BHPT MST benchmark schema")
    if payload.get("toolkit") != "BlackHolePerturbationToolkit/ReggeWheeler":
        raise MSTBenchmarkError("unexpected external MST implementation")
    if payload.get("toolkit_url") != "https://bhptoolkit.org/ReggeWheeler/":
        raise MSTBenchmarkError("unexpected external MST source URL")
    if payload.get("toolkit_license") != "MIT":
        raise MSTBenchmarkError("unexpected external MST license")
    if payload.get("method") != "MST":
        raise MSTBenchmarkError("external benchmark did not use MST")
    if payload.get("potential") != "ReggeWheeler":
        raise MSTBenchmarkError("external benchmark did not use Regge-Wheeler")
    if payload.get("boundary_conditions") != "In":
        raise MSTBenchmarkError("external benchmark did not use the In solution")
    if payload.get("odd_phase_definition") != BHPT_ODD_PHASE_DEFINITION:
        raise MSTBenchmarkError("external odd-phase convention changed")
    if payload.get("even_phase_source") != "exact_chandrasekhar_starobinsky_ratio":
        raise MSTBenchmarkError("external even-phase provenance changed")
    records = payload.get("records")
    if not isinstance(records, list):
        raise MSTBenchmarkError("external benchmark records must be a list")

    frequencies = tuple(float(value) for value in expected_kM)
    multipoles = tuple(int(value) for value in expected_ell)
    expected = {(frequency, ell) for frequency in frequencies for ell in multipoles}
    observed: set[tuple[float, int]] = set()
    normalized: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            raise MSTBenchmarkError(f"record {index} is not an object")
        kM = _finite_real(record.get("kM"), label=f"records[{index}].kM")
        ell_raw = record.get("ell")
        if isinstance(ell_raw, bool) or not isinstance(ell_raw, int) or ell_raw < 2:
            raise MSTBenchmarkError(f"records[{index}].ell must be an integer >= 2")
        ell = int(ell_raw)
        key = (kM, ell)
        if key not in expected:
            raise MSTBenchmarkError(f"unexpected external benchmark key {key}")
        if key in observed:
            raise MSTBenchmarkError(f"duplicate external benchmark key {key}")
        observed.add(key)
        incidence = _complex_record(record.get("incidence"), label="incidence")
        reflection = _complex_record(record.get("reflection"), label="reflection")
        odd = _complex_record(record.get("odd"), label="odd")
        even = _complex_record(record.get("even_from_chandrasekhar"), label="even")
        reconstructed_odd = -reflection / (((-1) ** ell) * incidence)
        reconstructed_even = odd * _parity_ratio(ell=ell, kM=kM)
        odd_internal_error = abs(odd - reconstructed_odd)
        even_internal_error = abs(even - reconstructed_even)
        if odd_internal_error > internal_tolerance:
            raise MSTBenchmarkError(
                f"external odd phase is inconsistent with amplitudes at {key}: "
                f"{odd_internal_error}"
            )
        if even_internal_error > internal_tolerance:
            raise MSTBenchmarkError(
                f"external even phase is inconsistent with parity relation at {key}: "
                f"{even_internal_error}"
            )
        normalized.append(
            {
                "kM": kM,
                "ell": ell,
                "incidence": incidence,
                "reflection": reflection,
                "odd": odd,
                "even": even,
                "external_odd_internal_error": odd_internal_error,
                "external_even_internal_error": even_internal_error,
            }
        )
    if observed != expected:
        missing = sorted(expected - observed)
        raise MSTBenchmarkError(f"external benchmark key set is incomplete: {missing}")
    normalized.sort(key=lambda item: (item["kM"], item["ell"]))
    return normalized


def compare_bhpt_mst_benchmark(
    payload: Mapping[str, Any],
    *,
    expected_kM: Iterable[float] = DEFAULT_BENCHMARK_KM,
    expected_ell: Iterable[int] = DEFAULT_BENCHMARK_ELL,
    tolerance: float = 1.0e-9,
    working_dps: int = 70,
    phase_solver: Callable[..., MSTPhaseFactor] = schwarzschild_mst_phase_factor,
) -> dict[str, Any]:
    """Compare external BHPT amplitudes to the local direct MST implementation."""

    if not math.isfinite(tolerance) or tolerance <= 0.0:
        raise MSTBenchmarkError("comparison tolerance must be finite and positive")
    records = validate_bhpt_mst_benchmark(
        payload,
        expected_kM=expected_kM,
        expected_ell=expected_ell,
    )
    comparisons: list[dict[str, Any]] = []
    for external in records:
        project = phase_solver(
            external["ell"],
            k=external["kM"],
            working_dps=working_dps,
        )
        odd_error = abs(external["odd"] - project.odd)
        even_error = abs(external["even"] - project.even)
        odd_phase_error = abs(math.atan2(
            (external["odd"] / project.odd).imag,
            (external["odd"] / project.odd).real,
        ))
        even_phase_error = abs(math.atan2(
            (external["even"] / project.even).imag,
            (external["even"] / project.even).real,
        ))
        comparisons.append(
            {
                "kM": external["kM"],
                "ell": external["ell"],
                "odd_abs_error": float(odd_error),
                "even_abs_error": float(even_error),
                "odd_wrapped_phase_error": float(odd_phase_error),
                "even_wrapped_phase_error": float(even_phase_error),
                "external_odd_modulus": float(abs(external["odd"])),
                "external_even_modulus": float(abs(external["even"])),
                "project_recurrence_residual": float(project.recurrence_residual),
            }
        )
    max_odd = max(record["odd_abs_error"] for record in comparisons)
    max_even = max(record["even_abs_error"] for record in comparisons)
    return {
        "schema_version": BHPT_MST_COMPARISON_SCHEMA,
        "status": "PASS" if max(max_odd, max_even) <= tolerance else "FAIL",
        "strict_no_fitted_phase_or_normalization": True,
        "external_even_is_independently_solved": False,
        "external_even_source": "exact Chandrasekhar/Starobinsky parity relation",
        "comparison_tolerance": tolerance,
        "record_count": len(comparisons),
        "max_odd_abs_error": float(max_odd),
        "max_even_abs_error": float(max_even),
        "max_odd_wrapped_phase_error": float(
            max(record["odd_wrapped_phase_error"] for record in comparisons)
        ),
        "max_even_wrapped_phase_error": float(
            max(record["even_wrapped_phase_error"] for record in comparisons)
        ),
        "records": comparisons,
    }


def benchmark_source_identity(package_root: str | Path) -> dict[str, Any]:
    """Return the external package path required by the benchmark launcher."""

    root = Path(package_root).resolve()
    radial = root / "Kernel" / "ReggeWheelerRadial.m"
    paclet = root / "PacletInfo.wl"
    if not radial.is_file() or not paclet.is_file():
        raise MSTBenchmarkError(
            "package root must contain PacletInfo.wl and Kernel/ReggeWheelerRadial.m"
        )
    return {"package_root": str(root), "radial_source": str(radial), "paclet": str(paclet)}


__all__ = [
    "BHPT_MST_BENCHMARK_SCHEMA",
    "BHPT_MST_COMPARISON_SCHEMA",
    "BHPT_ODD_PHASE_DEFINITION",
    "DEFAULT_BENCHMARK_ELL",
    "DEFAULT_BENCHMARK_KM",
    "MSTBenchmarkError",
    "benchmark_source_identity",
    "compare_bhpt_mst_benchmark",
    "validate_bhpt_mst_benchmark",
]
