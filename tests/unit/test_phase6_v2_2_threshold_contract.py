from __future__ import annotations

import glob
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "configs/phase6_v2_2_waveform_threshold_contract_20260811.json"
COMPARISON_GLOB = str(
    ROOT / "runs/phase6/radial_validation/"
    "v1_radial_selected_acceptance_v1_20260810_py314/comparison_*.json"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_contract() -> dict[str, object]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_v2_2_threshold_sources_and_domain_are_exact() -> None:
    contract = _load_contract()
    assert contract["schema"] == "schwgw_phase6_v2_2_waveform_threshold_contract_v1"
    assert contract["frozen_before_v2_2_execution"] is True
    assert contract["science_executed_for_threshold_calibration"] is False
    assert contract["global_green_permitted"] is False

    for identity in contract["source_identities"].values():
        source = ROOT / identity["path"]
        assert source.is_file()
        assert _sha256(source) == identity["sha256"]

    domain = contract["exact_domain"]
    assert domain["radial_key_count"] == 30
    assert domain["odd_key_count"] == domain["even_key_count"] == 15
    assert domain["record_count_per_route"] == 120
    assert domain["m_values"] == [-2, 2]
    assert domain["incident_columns"] == ["plus", "cross"]
    assert domain["route_pairs"] == ["A_B", "A_C", "B_C"]
    assert domain["angular_sum"] is False
    assert domain["finite_radius_observer_frame"] is False
    assert domain["total_plane_wave_sum"] is False


def test_preexecution_signal_diagnostics_rebuild_from_immutable_v1() -> None:
    contract = _load_contract()
    rows = []
    for filename in sorted(glob.glob(COMPARISON_GLOB)):
        record = json.loads(Path(filename).read_text(encoding="utf-8"))
        internal = complex(
            float(record["nodes"]["baseline"]["S"]["real"]),
            float(record["nodes"]["baseline"]["S"]["imag"]),
        )
        external = complex(
            float(record["external"]["S"]["real"]),
            float(record["external"]["S"]["imag"]),
        )
        rows.append((abs(1 - internal), abs(1 - external), abs(internal - external)))

    assert len(rows) == 30
    diagnostics = contract["preexecution_source_diagnostics"]
    assert min(row[0] for row in rows) == diagnostics["schwo_min_normalized_signal"]
    assert min(row[1] for row in rows) == diagnostics["external_min_normalized_signal"]
    assert max(row[0] for row in rows) == diagnostics["schwo_max_normalized_signal"]
    assert math.isclose(
        max(row[2] for row in rows),
        diagnostics["max_observed_schwo_external_complex_S_difference"],
        rel_tol=8 * math.ulp(1.0),
        abs_tol=0.0,
    )
    assert diagnostics["observed_values_are_acceptance_thresholds"] is False
    assert (
        min(min(row[0], row[1]) for row in rows)
        > 2
        * contract["common_applicability"]["phase_and_relative_magnitude_signal_floor"]
    )


def test_route_pair_thresholds_obey_frozen_error_propagation() -> None:
    contract = _load_contract()
    floor = contract["common_applicability"][
        "phase_and_relative_magnitude_signal_floor"
    ]
    thresholds = contract["route_pair_thresholds"]
    expected_epsilons = {"A_B": 1e-12, "A_C": 2e-6, "B_C": 2.001e-6}

    assert set(thresholds) == set(expected_epsilons)
    for pair, epsilon in expected_epsilons.items():
        policy = thresholds[pair]
        assert policy["scale_normalized_complex_difference_max"] == epsilon
        assert (
            policy["phase_invariant_scale_normalized_magnitude_difference_max"]
            == epsilon
        )
        assert policy["relative_magnitude_difference_max"] >= epsilon / floor
        assert policy["wrapped_relative_phase_rad_max"] >= 2 * math.asin(
            epsilon / (2 * floor)
        )

    assert contract["acceptance_logic"]["absolute_phase_status"] == "PARTIAL"
    assert contract["acceptance_logic"]["global_status"] is None
    assert (
        contract["separate_uncertainty_budget_policy"]["combined_scalar_forbidden"]
        is True
    )
