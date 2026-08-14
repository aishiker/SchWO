from __future__ import annotations

import glob
import hashlib
import json
import math
from pathlib import Path

import mpmath as mp


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "configs/phase6_v2_3_flux_threshold_contract_20260811.json"
COMPARISON_GLOB = str(
    ROOT / "runs/phase6/radial_validation/"
    "v1_radial_selected_acceptance_v1_20260810_py314/comparison_*.json"
)
EXTERNAL_ROOT = (
    ROOT / "runs/phase6/radial_validation/"
    "v1_external_bhpt_direct_bounded_selected_v1_20260810_py314"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_contract() -> dict[str, object]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _mp_complex(record: dict[str, object]) -> mp.mpc:
    return mp.mpc(str(record["real"]), str(record["imag"]))


def _assert_mp_close(observed: mp.mpf, expected: str) -> None:
    target = mp.mpf(expected)
    assert mp.almosteq(
        observed, target, rel_eps=mp.mpf("1e-75"), abs_eps=mp.mpf("1e-90")
    )


def test_v2_3_threshold_sources_and_domain_are_exact() -> None:
    contract = _load_contract()
    assert contract["schema"] == "schwgw_phase6_v2_3_flux_threshold_contract_v1"
    assert contract["frozen_before_v2_3_execution"] is True
    assert contract["science_executed_for_threshold_calibration"] is False
    assert contract["global_green_permitted"] is False

    for identity in contract["source_identities"].values():
        source = ROOT / identity["path"]
        assert source.is_file()
        assert _sha256(source) == identity["sha256"]

    domain = contract["exact_domain"]
    assert domain["radial_key_count"] == 30
    assert domain["odd_key_count"] == domain["even_key_count"] == 15
    assert domain["record_count"] == 120
    assert domain["m_values"] == [-2, 2]
    assert domain["incident_columns"] == ["plus", "cross"]
    assert domain["angular_sum"] is False
    assert domain["finite_radius_observer_frame"] is False
    assert domain["total_plane_wave_sum"] is False


def test_preexecution_flux_diagnostics_rebuild_from_immutable_sources() -> None:
    contract = _load_contract()
    rows: list[dict[str, mp.mpf]] = []
    with mp.workdps(100):
        for filename in sorted(glob.glob(COMPARISON_GLOB)):
            comparison_path = Path(filename)
            comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
            ordinal = int(comparison_path.name.split("__", 1)[0].split("_")[1])
            matches = list(EXTERNAL_ROOT.glob(f"node_{ordinal:02d}__*__wp60.json"))
            assert len(matches) == 1
            external = json.loads(matches[0].read_text(encoding="utf-8"))

            schwo_s = _mp_complex(comparison["nodes"]["baseline"]["S"])
            schwo_t2 = mp.exp(
                2 * mp.mpf(str(comparison["nodes"]["baseline"]["log_abs_T_horizon"]))
            )
            external_s = _mp_complex(external["phase_factor"])
            external_t = _mp_complex(external["transmission"])
            external_t2 = abs(external_t) ** 2
            rows.append(
                {
                    "schwo_balance": abs(1 - abs(schwo_s) ** 2 - schwo_t2),
                    "external_balance": abs(1 - abs(external_s) ** 2 - external_t2),
                    "complex_s": abs(schwo_s - external_s),
                    "log_t": abs(
                        mp.mpf(
                            str(comparison["nodes"]["baseline"]["log_abs_T_horizon"])
                        )
                        - mp.log(abs(external_t))
                    ),
                    "outgoing_fraction": abs(abs(schwo_s) ** 2 - abs(external_s) ** 2),
                    "horizon_relative": abs(schwo_t2 - external_t2)
                    / max(schwo_t2, external_t2),
                    "minimum_horizon": min(schwo_t2, external_t2),
                    "abs_s": abs(schwo_s),
                }
            )

        assert len(rows) == 30
        diagnostics = contract["preexecution_source_diagnostics"]
        _assert_mp_close(
            max(row["schwo_balance"] for row in rows),
            diagnostics["max_schwo_radial_balance_residual"],
        )
        _assert_mp_close(
            max(row["external_balance"] for row in rows),
            diagnostics["max_external_radial_balance_residual"],
        )
        _assert_mp_close(
            max(row["complex_s"] for row in rows),
            diagnostics["max_observed_schwo_external_complex_S_difference"],
        )
        _assert_mp_close(
            max(row["log_t"] for row in rows),
            diagnostics["max_observed_schwo_external_log_abs_T_difference"],
        )
        _assert_mp_close(
            max(row["outgoing_fraction"] for row in rows),
            diagnostics["max_observed_total_outgoing_flux_fraction_difference"],
        )
        _assert_mp_close(
            max(row["horizon_relative"] for row in rows),
            diagnostics["max_observed_horizon_flux_symmetric_relative_difference"],
        )
        _assert_mp_close(
            min(row["minimum_horizon"] for row in rows),
            diagnostics["minimum_observed_horizon_flux_fraction"],
        )
        _assert_mp_close(
            min(row["abs_s"] for row in rows),
            diagnostics["minimum_observed_abs_S"],
        )
        assert diagnostics["observed_values_are_acceptance_thresholds"] is False


def test_flux_thresholds_are_analytic_images_of_preexisting_bounds() -> None:
    contract = _load_contract()
    thresholds = contract["frozen_thresholds"]
    assert thresholds["schwo_normalized_balance_residual_max"]["value"] == 1e-8
    assert thresholds["external_normalized_balance_residual_max"]["value"] == 1e-15

    epsilon_ab = 1e-11
    ab_flux_bound = 2 * epsilon_ab + epsilon_ab**2
    assert (
        thresholds["waveform_vs_current_relative_flux_residual_max"]["value"]
        >= ab_flux_bound
    )
    assert (
        thresholds["route_A_B_total_outgoing_flux_fraction_difference_max"]["value"]
        >= ab_flux_bound
    )

    epsilon_external = 2e-6
    assert (
        thresholds["schwo_external_total_outgoing_flux_fraction_difference_max"][
            "value"
        ]
        >= 2 * epsilon_external + epsilon_external**2
    )
    assert (
        thresholds["schwo_external_horizon_flux_symmetric_relative_difference_max"][
            "value"
        ]
        >= math.exp(2 * epsilon_external) - 1
    )

    assert contract["exact_predicates"]["radial_solve_count"] == 0
    assert contract["exact_predicates"]["no_dropped_tiny_horizon_modes"] is True
    assert contract["acceptance_logic"]["absolute_phase_status"] == "PARTIAL"
    assert contract["acceptance_logic"]["global_status"] is None
    assert (
        contract["separate_uncertainty_budget_policy"]["combined_scalar_forbidden"]
        is True
    )
