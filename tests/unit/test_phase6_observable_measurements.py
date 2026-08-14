"""Real selected-domain tests for Phase-6 V2--V5 candidate measurements."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import stat

import numpy as np
import pytest

from scripts.phase6_run_v1_observable_measurements import (
    CANDIDATE_STATUS,
    MANIFEST_FILENAME,
    MEASUREMENT_FILENAME,
    SUBMISSION_FILENAME,
    ObservableCandidateError,
    build_candidate_submission,
    validate_candidate_root,
)
from schwgw.validation.phase6_observable_evidence import (
    OBSERVABLE_GATES,
    PROJECT_ROOT,
    validate_submission,
)
from schwgw.validation.phase6_observable_measurements import (
    ObservableMeasurementError,
    SelectedObservableMeasurementConfig,
    run_selected_observable_measurements,
    validate_measurement_payload,
)


pytestmark = pytest.mark.filterwarnings("error")


@pytest.fixture(scope="module")
def selected_config() -> SelectedObservableMeasurementConfig:
    return SelectedObservableMeasurementConfig(
        low_lmax=3,
        high_lmax=5,
        glory_lmax=5,
    )


@pytest.fixture(scope="module")
def selected_measurement(
    selected_config: SelectedObservableMeasurementConfig,
) -> dict[str, object]:
    return run_selected_observable_measurements(selected_config)


def test_selected_measurements_are_real_but_all_partial(
    selected_measurement: dict[str, object],
) -> None:
    checked = validate_measurement_payload(selected_measurement)
    assert checked["overall_state"] == "PARTIAL"
    assert checked["scientific_evidence"] is True
    assert checked["kernel_unit_test_only"] is False
    assert checked["contract_only"] is False
    assert checked["global_green_permitted"] is False
    assert checked["paper_agreement_primary_gate"] is False
    assert set(checked["observables"]) == set(OBSERVABLE_GATES)
    assert {section["state"] for section in checked["observables"].values()} == {
        "PARTIAL"
    }


def test_v2_uses_li_mp_bridge_without_promoting_missing_large_r_routes(
    selected_measurement: dict[str, object],
) -> None:
    observables = selected_measurement["observables"]
    master = observables["master_to_strain_flux"]
    crosscheck = observables["metric_psi4_external_crosscheck"]
    values = master["measurements"]

    assert values["project_master_normalization_bridge"] == (
        "IMPLEMENTED_EXPLICIT_LI_TO_MP"
    )
    assert values["project_master_values_used"] is True
    assert values["bridge"]["even_formula"] == "Psi_ZM = psi_Li_even"
    assert values["bridge"]["odd_formula"] == "Psi_CPM = (2 i / k) psi_Li_odd"
    assert values["finite_radius_total_field_used_as_infinity_waveform"] is False
    assert values["large_radius_metric_psi4_route_evaluated"] is False
    assert values["external_bhpt_amplitude_route_evaluated"] is False
    assert (
        values["finite_radius_metric_roundtrip"]["maximum_relative_residual"] < 1.0e-12
    )
    assert master["check_metrics"]["radial_flux_consistency"] is not None
    assert crosscheck["check_metrics"]["master_vs_metric"] is not None
    assert crosscheck["check_metrics"]["master_vs_psi4"] is None
    assert crosscheck["check_metrics"]["master_vs_external"] is None


def test_v3_records_conditioned_s_t_limits_and_explicit_projection(
    selected_measurement: dict[str, object],
) -> None:
    values = selected_measurement["observables"]["spin2_scattering_limits"][
        "measurements"
    ]
    records = values["radial_records"]
    assert values["radial_mode_count"] == 20
    assert {record["kM"] for record in records} == {0.1, 2.0, 4.0}
    assert {record["sector"] for record in records} == {"odd", "even"}
    assert all(record["paper_specific_envelope_used"] is False for record in records)
    assert all(record["actual_precision_bits"] == 53 for record in records)
    assert all(record["outer_basis"] == "jost_1_over_r" for record in records)
    assert all(record["match_condition_number"] >= 1.0 for record in records)
    assert all(
        0.0 <= record["absorption_transmission_probability"] <= 1.0
        for record in records
    )
    assert max(record["transmission_bound_correction"] for record in records) > 0.0
    assert values["glory"]["kM"] == 4.0
    assert values["series_reduction"]["orders"] == [0, 1, 2]
    assert values["parity"]["even_sector_independently_integrated"] is True
    assert values["parity"]["even_not_parity_derived"] is True
    for record in records:
        phase = complex(*record["phase_factor"])
        assert np.isfinite(phase.real)
        assert np.isfinite(phase.imag)


def test_v4_runs_nontrivial_metric_curvature_for_both_observers(
    selected_measurement: dict[str, object],
) -> None:
    values = selected_measurement["observables"]["finite_radius_tidal_detector"][
        "measurements"
    ]
    records = values["records"]
    assert {record["observer"] for record in records} == {
        "static_schwarzschild",
        "radial_freefall_E1",
    }
    for record in records:
        assert record["metric_perturbation_norm"] > 0.0
        assert record["linearized_riemann_norm"] > 0.0
        assert record["tetrad_perturbation_norm"] > 0.0
        assert record["maximum_transport_residual"] < 2.0e-15
        assert abs(complex(*record["coordinate_lie_term"])) > 0.0
        assert abs(complex(*record["worldline_pullback"])) > 0.0
        assert record["operational_residual"] < 1.0e-12
    assert values["finite_arm_worldline_integration_performed"] is False
    assert values["maximum_frame_transport_residual"] < 2.0e-15
    by_observer = {record["observer"]: record for record in records}
    assert by_observer["static_schwarzschild"]["acceleration_norm"] > 0.0
    assert by_observer["radial_freefall_E1"]["acceleration_norm"] < 2.0e-15


def test_v5_builds_two_column_complex_transfer_and_freezes_phase(
    selected_measurement: dict[str, object],
) -> None:
    values = selected_measurement["observables"]["complex_lensing_matrix"][
        "measurements"
    ]
    plus = np.array(
        [complex(*pair) for pair in values["plus_incident_column"]],
        dtype=np.complex128,
    )
    cross = np.array(
        [complex(*pair) for pair in values["cross_incident_column"]],
        dtype=np.complex128,
    )
    matrix = np.array(
        [[complex(*pair) for pair in row] for row in values["transfer_matrix"]],
        dtype=np.complex128,
    )
    assert np.array_equal(matrix[:, 0], plus)
    assert np.array_equal(matrix[:, 1], cross)
    assert values["incident_basis_determinant"] == 1.0
    assert min(values["singular_values"]) > 0.0
    assert values["rotation_covariance_residual"] < 1.0e-12
    assert values["direct_matrix_residual"] < 1.0e-12
    assert len(values["phase_convention_sha256"]) == 64
    assert values["production_unit_column_solves_performed"] is False


@pytest.mark.parametrize(
    "tamper",
    [
        lambda payload: payload.__setitem__("global_green_permitted", True),
        lambda payload: payload["observables"]["master_to_strain_flux"][
            "measurements"
        ].__setitem__("project_master_normalization_bridge", "OPEN_NOT_IMPLEMENTED"),
        lambda payload: payload["observables"]["spin2_scattering_limits"][
            "measurements"
        ]["radial_records"][0].__setitem__("paper_specific_envelope_used", True),
        lambda payload: payload["observables"]["finite_radius_tidal_detector"][
            "measurements"
        ]["records"][0].__setitem__("metric_perturbation_norm", 0.0),
        lambda payload: payload["observables"]["complex_lensing_matrix"][
            "measurements"
        ].__setitem__("phase_convention_sha256", "0" * 64),
    ],
)
def test_measurement_validator_rejects_science_claim_tampering(
    selected_measurement: dict[str, object], tamper: object
) -> None:
    changed = deepcopy(selected_measurement)
    tamper(changed)
    with pytest.raises(ObservableMeasurementError):
        validate_measurement_payload(changed, verify_live_sources=False)


def test_measurement_validator_rejects_stale_live_source(
    selected_measurement: dict[str, object],
) -> None:
    changed = deepcopy(selected_measurement)
    changed["observables"]["complex_lensing_matrix"]["source_identities"][
        "polarization_transfer"
    ]["sha256"] = "0" * 64
    with pytest.raises(ObservableMeasurementError, match="source drift"):
        validate_measurement_payload(changed)


def test_candidate_submission_is_sealed_partial_publisher_input(
    tmp_path: Path,
    selected_config: SelectedObservableMeasurementConfig,
) -> None:
    root = tmp_path / "phase6-selected-candidate"
    summary = build_candidate_submission(root, config=selected_config)
    assert summary["formal_release"] is False
    assert set(summary["certificate_states"].values()) == {"PARTIAL"}
    assert stat.S_IMODE(root.stat().st_mode) == 0o555
    assert all(stat.S_IMODE(path.stat().st_mode) == 0o444 for path in root.iterdir())
    assert not (root / "observable_evidence.json").exists()

    manifest = json.loads((root / MANIFEST_FILENAME).read_bytes())
    measurement = json.loads((root / MEASUREMENT_FILENAME).read_bytes())
    submission = json.loads((root / SUBMISSION_FILENAME).read_bytes())
    certificates = validate_submission(submission)
    assert manifest["status"] == CANDIDATE_STATUS
    assert manifest["formal_release"] is False
    assert manifest["formal_publisher_invoked"] is False
    assert measurement["candidate_release_only"] is True
    assert len(certificates) == 5
    assert {certificate["state"] for certificate in certificates} == {"PARTIAL"}
    for certificate in certificates:
        descriptor = certificate["evidence_inventory"]["selected_measurement"]
        assert descriptor["role"] == "PRIMARY_SCIENCE"
        assert descriptor["independence_class"] == "SAME_IMPLEMENTATION"
        assert descriptor["provenance"]["source_snapshot_identities"]
        assert not any(
            evidence["role"] == "INDEPENDENT_SCIENCE"
            for evidence in certificate["evidence_inventory"].values()
        )
    assert validate_candidate_root(root) == summary


def test_candidate_runner_refuses_formal_runs_tree_without_computation() -> None:
    forbidden = PROJECT_ROOT / "runs/phase6/forbidden-selected-candidate"
    with pytest.raises(ObservableCandidateError, match="below runs"):
        build_candidate_submission(forbidden)
