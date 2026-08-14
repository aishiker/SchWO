from __future__ import annotations

import copy
from pathlib import Path

import mpmath as mp
import pytest

from schwgw.validation import phase6_v2_flux_closure as flux


PROJECT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def bundle() -> tuple[tuple[dict[str, object], ...], flux.FrozenGate]:
    records, gate = flux.build_v2_3_flux_closure_records(
        PROJECT, require_dispatch_review_identity=False
    )
    return records, gate  # type: ignore[return-value]


def test_exact_mandatory_inventory_and_predicates(bundle) -> None:
    records, _ = bundle
    flux.validate_record_inventory(records)
    assert len(records) == 120
    assert {record["radial_key"]["ordinal"] for record in records} == set(range(30))
    assert all(record["mandatory_predicates_passed"] for record in records)
    assert all(record["precision"]["working_dps"] == 100 for record in records)


def test_tiny_horizon_fraction_retained_without_binary64(bundle) -> None:
    records, _ = bundle
    values = [
        mp.mpf(
            record["flux_fractions"]["external_direct"]["horizon_over_incoming"][
                "value"
            ]
        )
        for record in records
    ]
    minimum = min(values)
    assert minimum > 0
    assert minimum < mp.mpf("1e-1490")
    assert all(
        record["precision"]["binary64_used_for_mandatory_quantities"] is False
        for record in records
    )


def test_currents_have_frozen_orientation_and_fluxes_are_positive(bundle) -> None:
    records, _ = bundle
    for record in records:
        for source in ("schwo", "external_direct"):
            evidence = record["boundary_evidence"][source]
            assert mp.mpf(evidence["infinity_incoming"]["signed_current"]["value"]) < 0
            assert (
                mp.mpf(evidence["infinity_total_outgoing"]["signed_current"]["value"])
                > 0
            )
            assert mp.mpf(evidence["horizon_ingoing"]["signed_current"]["value"]) < 0
            for boundary in evidence.values():
                assert mp.mpf(boundary["flux_from_amplitude"]["value"]) > 0
                assert mp.mpf(boundary["flux_from_current"]["value"]) > 0


def test_no_signal_floor_and_no_scattered_only_balance(bundle) -> None:
    records, _ = bundle
    assert all(
        record["diagnostics"]["signal_floor_applied"] is False for record in records
    )
    assert all(record["diagnostics"]["used_in_balance"] is False for record in records)
    assert all(
        record["diagnostics"]["scattered_only_balance_forbidden"] is True
        for record in records
    )
    with mp.workdps(100):
        assert (
            flux.normalized_balance_residual(mp.mpf(1), mp.mpf(3) / 4, mp.mpf(1) / 4)
            == 0
        )
        assert (
            flux.normalized_balance_residual(mp.mpf(1), mp.mpf("0.1"), mp.mpf("0.2"))
            != 0
        )


def test_ambient_precision_is_restored() -> None:
    original = mp.mp.dps
    try:
        mp.mp.dps = 17
        flux.build_v2_3_flux_closure_records(
            PROJECT, require_dispatch_review_identity=False
        )
        assert mp.mp.dps == 17
    finally:
        mp.mp.dps = original


def test_summary_extrema_are_exact_at_ambient_15_and_100() -> None:
    original = mp.mp.dps
    serialized: dict[int, tuple[bytes, bytes]] = {}
    try:
        for ambient_dps in (15, 100):
            mp.mp.dps = ambient_dps
            records, gate = flux.build_v2_3_flux_closure_records(
                PROJECT, require_dispatch_review_identity=False
            )
            summary = flux._summary(records, gate)
            report = flux._report(records, gate, summary, verification={})
            assert mp.mp.dps == ambient_dps

            with mp.workdps(flux.WORKING_DPS):
                expected_horizon = flux._extrema(
                    records,
                    (
                        "flux_fractions",
                        "external_direct",
                        "horizon_over_incoming",
                    ),
                )["minimum"]
                expected_schwo = flux._extrema(
                    records, ("comparators", "schwo_balance", "value")
                )
                expected_external = flux._extrema(
                    records, ("comparators", "external_balance", "value")
                )
            assert summary["minimum_horizon_flux_fraction"] == expected_horizon
            assert summary["schwo_balance_residual_extrema"] == expected_schwo
            assert summary["external_balance_residual_extrema"] == expected_external
            flux._validate_summary_extrema(records, summary)

            records_bytes = b"".join(
                flux.canonical_json_bytes(record) for record in records
            )
            assert (
                records_bytes
                == (PROJECT / flux.V23_PREDECESSOR_ROOT / "records.jsonl").read_bytes()
            )
            serialized[ambient_dps] = (
                flux.canonical_json_bytes(summary),
                flux.canonical_json_bytes(report),
            )
        assert serialized[15] == serialized[100]
    finally:
        mp.mp.dps = original


def test_record_omission_fails_closed(bundle) -> None:
    records, _ = bundle
    with pytest.raises(flux.Phase6V23Error, match="exactly 120"):
        flux.validate_record_inventory(records[:-1])


def test_external_wp60_source_and_thresholds_are_anchored(bundle) -> None:
    records, gate = bundle
    assert len(gate.external_nodes) == 30
    assert all(
        record["source_provenance"]["external_original_wp60_strings_parsed_directly"]
        is True
        for record in records
    )
    threshold_hash = flux.FROZEN_IDENTITIES[str(flux.THRESHOLD_CONTRACT)]
    for record in records:
        results = [
            record["comparators"]["schwo_balance"],
            record["comparators"]["external_balance"],
            record["comparators"]["route_A_B_total_outgoing_flux"],
            record["comparators"]["schwo_external_total_outgoing_fraction"],
            record["comparators"]["schwo_external_horizon_fraction"],
            *record["comparators"]["waveform_current"].values(),
        ]
        assert all(result["threshold_sha256"] == threshold_hash for result in results)
        assert all(result["passed"] for result in results)


def test_route_factor_tamper_fails_closed(bundle) -> None:
    _, gate = bundle
    v22 = copy.deepcopy(gate.v22_records[0])
    coefficient = v22["route_amplitudes"]["A"]["coefficient"]
    coefficient["real"] = str(mp.mpf(coefficient["real"]) * 2)
    coefficient["imag"] = str(mp.mpf(coefficient["imag"]) * 2)
    with (
        mp.workdps(flux.WORKING_DPS),
        pytest.raises(
            flux.Phase6V23Error, match="total-outgoing reconstruction mismatch"
        ),
    ):
        flux._record(
            ordinal=0,
            v21=gate.v21_records[0],
            v22=v22,
            comparison=gate.comparisons[0],
            comparison_identity=gate.comparison_identities[0],
            external_node=gate.external_nodes[0],
            external_node_identity=gate.external_node_identities[0],
            contract=gate.contract,
        )
