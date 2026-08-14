from __future__ import annotations

from dataclasses import replace

import pytest

from schwgw.scattering.mst import schwarzschild_mst_phase_factor
from schwgw.scattering.mst_benchmark import (
    BHPT_MST_BENCHMARK_SCHEMA,
    BHPT_ODD_PHASE_DEFINITION,
    MSTBenchmarkError,
    compare_bhpt_mst_benchmark,
    validate_bhpt_mst_benchmark,
)


pytest.importorskip("mpmath")


def _complex(value: complex) -> dict[str, float]:
    return {"real": value.real, "imag": value.imag}


def _payload() -> dict:
    ell = 20
    kM = 0.5
    phase = schwarzschild_mst_phase_factor(
        ell,
        k=kM,
        truncation=20,
        guard_terms=16,
        working_dps=50,
    )
    incidence = 2.0 + 0.5j
    reflection = -((-1) ** ell) * incidence * phase.odd
    return {
        "schema_version": BHPT_MST_BENCHMARK_SCHEMA,
        "toolkit": "BlackHolePerturbationToolkit/ReggeWheeler",
        "toolkit_url": "https://bhptoolkit.org/ReggeWheeler/",
        "toolkit_license": "MIT",
        "method": "MST",
        "potential": "ReggeWheeler",
        "boundary_conditions": "In",
        "odd_phase_definition": BHPT_ODD_PHASE_DEFINITION,
        "even_phase_source": "exact_chandrasekhar_starobinsky_ratio",
        "records": [
            {
                "kM": kM,
                "ell": ell,
                "incidence": _complex(incidence),
                "reflection": _complex(reflection),
                "odd": _complex(phase.odd),
                "even_from_chandrasekhar": _complex(phase.even),
            }
        ],
    }


def test_bhpt_mst_benchmark_strict_convention_passes_without_phase_fit() -> None:
    result = compare_bhpt_mst_benchmark(
        _payload(),
        expected_kM=(0.5,),
        expected_ell=(20,),
        tolerance=2.0e-12,
        working_dps=50,
        phase_solver=lambda ell, *, k, working_dps: schwarzschild_mst_phase_factor(
            ell,
            k=k,
            truncation=20,
            guard_terms=16,
            working_dps=working_dps,
        ),
    )

    assert result["status"] == "PASS"
    assert result["strict_no_fitted_phase_or_normalization"] is True
    assert result["external_even_is_independently_solved"] is False
    assert result["record_count"] == 1
    assert result["max_odd_abs_error"] < 2.0e-12


def test_bhpt_mst_benchmark_rejects_amplitude_phase_inconsistency() -> None:
    payload = _payload()
    payload["records"][0]["odd"]["imag"] += 0.01

    with pytest.raises(MSTBenchmarkError, match="inconsistent with amplitudes"):
        validate_bhpt_mst_benchmark(
            payload,
            expected_kM=(0.5,),
            expected_ell=(20,),
        )


def test_bhpt_mst_benchmark_does_not_accept_a_conjugated_solution() -> None:
    payload = _payload()
    original_solver = schwarzschild_mst_phase_factor

    def conjugated_solver(ell: int, *, k: float, working_dps: int):
        phase = original_solver(
            ell,
            k=k,
            truncation=20,
            guard_terms=16,
            working_dps=working_dps,
        )
        return replace(phase, odd=phase.odd.conjugate(), even=phase.even.conjugate())

    result = compare_bhpt_mst_benchmark(
        payload,
        expected_kM=(0.5,),
        expected_ell=(20,),
        tolerance=1.0e-12,
        working_dps=50,
        phase_solver=conjugated_solver,
    )

    assert result["status"] == "FAIL"
    assert result["max_odd_abs_error"] > 1.0e-6
