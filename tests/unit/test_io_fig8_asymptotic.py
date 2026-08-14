from __future__ import annotations

from dataclasses import dataclass, replace
import json

import numpy as np
import pytest

from schwgw.io.asymptotic import (
    FIG8_DIRECT_MST_SCHEMA_VERSION,
    FIG8_KM_VALUES,
    load_fig8_asymptotic_dataset,
    produce_fig8_asymptotic_dataset,
    save_fig8_asymptotic_dataset,
    scan_fig8_matching_sensitivity,
)
from schwgw.scattering.asymptotic import (
    poisson_sasaki_odd_phase_factor,
    schwarzschild_even_from_odd,
)


@dataclass
class _Solution:
    phase_factor: complex
    diagnostics: dict[str, float]


def _synthetic_radial_solver(sector, ell, k, background, boundary):
    del background
    assert boundary.r_in_eps == 1.0e-6
    assert boundary.r_out == 300.0
    assert boundary.rtol == 1.0e-10
    assert boundary.atol == 1.0e-12
    parity = 1.0 if getattr(sector, "value", sector) == "even" else -1.0
    phase = np.exp(1j * parity * (0.02 * ell + 0.01 * k))
    return _Solution(phase_factor=complex(phase), diagnostics={"residual": 1.0e-12})


def _synthetic_matched_tail_solver(sector, ell, k, background, boundary):
    del background
    ell_values = np.asarray([ell], dtype=np.int64)
    odd = poisson_sasaki_odd_phase_factor(ell_values, k=k)
    if getattr(sector, "value", sector) == "even":
        phase = schwarzschild_even_from_odd(odd, ell_values, k=k)[0]
    else:
        phase = odd[0]
    finite_radius_phase = np.exp(1.0j * ell * (ell + 1) / (k * boundary.r_out))
    return _Solution(
        phase_factor=complex(phase * finite_radius_phase),
        diagnostics={"residual": 0.0},
    )


def test_fig8_producer_uses_phase_factor_and_strict_round_trip(tmp_path) -> None:
    events = []
    dataset = produce_fig8_asymptotic_dataset(
        lmax=4,
        theta=np.array([0.2, 0.9, np.pi]),
        lmax_ladder=(4,),
        radial_solver=_synthetic_radial_solver,
        progress=events.append,
        source_command=["synthetic"],
    )

    assert np.array_equal(dataset.kM, FIG8_KM_VALUES)
    assert dataset.phase_factor_odd.shape == (4, 3)
    assert dataset.M22.shape == (4, 3, 3)
    assert dataset.lmax_ladder_cross_section.shape == (4, 1, 3, 3)
    assert dataset.theta[0] > 0.0
    assert len(events) == 24
    assert dataset.metadata["convention"]["phase_input"].startswith(
        "solution.phase_factor"
    )
    assert dataset.metadata["strict_paper_reproduction_claim"] is False

    output = tmp_path / "fig8.npz"
    npz, sidecar = save_fig8_asymptotic_dataset(dataset, output)
    loaded = load_fig8_asymptotic_dataset(npz)
    assert sidecar.is_file()
    np.testing.assert_allclose(
        loaded.differential_cross_section, dataset.differential_cross_section
    )
    assert loaded.metadata == dataset.metadata
    with pytest.raises(FileExistsError, match="overwrite"):
        save_fig8_asymptotic_dataset(dataset, output)


def test_fig8_loader_rejects_missing_or_mismatched_sidecar(tmp_path) -> None:
    dataset = produce_fig8_asymptotic_dataset(
        lmax=4,
        theta=np.array([0.4, np.pi]),
        radial_solver=_synthetic_radial_solver,
    )
    output = tmp_path / "fig8.npz"
    save_fig8_asymptotic_dataset(dataset, output)
    output.with_suffix(".json").unlink()
    with pytest.raises(ValueError, match="sidecar is missing"):
        load_fig8_asymptotic_dataset(output)

    save_fig8_asymptotic_dataset(dataset, tmp_path / "fig8_other.npz")
    bad_sidecar = tmp_path / "fig8_other.json"
    payload = json.loads(bad_sidecar.read_text(encoding="utf-8"))
    payload["figure"] = 999
    bad_sidecar.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="metadata differ"):
        load_fig8_asymptotic_dataset(tmp_path / "fig8_other.npz")


def test_fig8_direct_mst_schema_has_an_explicit_unblended_contract(tmp_path) -> None:
    dataset = produce_fig8_asymptotic_dataset(
        lmax=4,
        theta=np.array([0.4, np.pi]),
        radial_solver=_synthetic_radial_solver,
    )
    metadata = {
        **dataset.metadata,
        "schema_version": FIG8_DIRECT_MST_SCHEMA_VERSION,
        "tail": {
            "direct_mst_phase_solver_used": True,
            "empirical_overlap_blend_used": False,
            "empirical_phase_offset_used": False,
        },
        "transactions": [{"kM": value} for value in FIG8_KM_VALUES],
    }
    direct = replace(dataset, metadata=metadata)
    output = tmp_path / "fig8_direct_mst.npz"
    save_fig8_asymptotic_dataset(direct, output)
    loaded = load_fig8_asymptotic_dataset(output)

    assert loaded.metadata["schema_version"] == FIG8_DIRECT_MST_SCHEMA_VERSION
    assert loaded.metadata["tail"]["empirical_overlap_blend_used"] is False
    assert loaded.metadata["strict_paper_reproduction_claim"] is False

    with pytest.raises(ValueError, match="four-frequency transaction"):
        replace(direct, metadata={**metadata, "transactions": metadata["transactions"][:3]})


def test_fig8_rejects_forward_axis_and_nonfinal_ladder() -> None:
    with pytest.raises(ValueError, match="theta"):
        produce_fig8_asymptotic_dataset(
            lmax=4, theta=np.array([0.0, np.pi]), radial_solver=_synthetic_radial_solver
        )
    with pytest.raises(ValueError, match="end at lmax"):
        produce_fig8_asymptotic_dataset(
            lmax=5,
            theta=np.array([0.4, np.pi]),
            lmax_ladder=(4,),
            radial_solver=_synthetic_radial_solver,
        )


def test_fig8_ladder_diagnostics_separate_reduction_orders_and_frequencies() -> None:
    dataset = produce_fig8_asymptotic_dataset(
        lmax=5,
        theta=np.array([0.2 * np.pi, 0.6 * np.pi, np.pi]),
        lmax_ladder=(4, 5),
        radial_solver=_synthetic_radial_solver,
    )

    record = dataset.metadata["lmax_ladder_diagnostics"][0]
    assert record["aggregate_warning"].startswith("mixes q=0,1,2")
    by_order = record["by_reduction_order"]
    assert [item["reduction_order"] for item in by_order] == [0, 1, 2]
    assert all(len(item["by_frequency"]) == 4 for item in by_order)
    assert all(
        item["stable_window"]
        == {"theta_over_pi_min": 0.2, "theta_over_pi_max": 1.0}
        for item in by_order
    )
    assert all(
        np.isfinite(frequency["normalized_linf_change"])
        for item in by_order
        for frequency in item["by_frequency"]
    )


def test_fig8_matching_sensitivity_is_solver_free_and_reference_is_zero() -> None:
    raw = produce_fig8_asymptotic_dataset(
        lmax=140,
        theta=np.array([0.2 * np.pi, 0.6 * np.pi, np.pi]),
        lmax_ladder=(140,),
        radial_solver=_synthetic_matched_tail_solver,
    )
    report = scan_fig8_matching_sensitivity(
        raw,
        r_out_values=(300.0, 360.0),
        overlap_half_width_values=(15, 20),
        output_lmax=152,
        target_lmax=150,
    )

    assert report["no_radial_solver_rerun"] is True
    assert report["reduction_order"] == 2
    assert len(report["records"]) == 4
    reference = next(
        item
        for item in report["records"]
        if item["r_out"] == 300.0 and item["overlap_half_width"] == 15
    )
    assert reference["q2_max_normalized_linf_difference"] == pytest.approx(0.0)
    assert all(
        len(item["q2_by_frequency"]) == 4
        for item in report["records"]
        if item["status"] == "passed_existing_matching_gates"
    )
    assert any(
        item["status"] == "rejected_by_existing_matching_gate"
        for item in report["records"]
    )
