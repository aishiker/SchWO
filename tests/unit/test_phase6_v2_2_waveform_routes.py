from __future__ import annotations

import json
from pathlib import Path

import mpmath as mp

from schwgw.scattering.phase6_v2_2_waveform_routes import (
    compare_route_pair,
    fixed_record_scale,
    route_a_mp_coefficient,
    route_b_rw_metric_curvature_coefficient,
    route_c_external_mp_coefficient,
    scattered_li_master_coefficient,
)
from schwgw.validation.phase6_v2_waveform_routes import (
    WORKING_DPS,
    build_v2_2_waveform_route_records,
    verify_frozen_v2_2_inputs,
)
from schwgw.validation.phase6_v2_mode_amplitudes import complex_record


ROOT = Path(__file__).resolve().parents[2]


def test_route_b_independent_metric_curvature_chain_recovers_mp_master() -> None:
    with mp.workdps(80):
        q = mp.mpc("0.125", "-0.375")
        for sector, omega in (("even", mp.mpf("2")), ("odd", mp.mpf("0.5"))):
            route_a = route_a_mp_coefficient(sector=sector, omega=omega, li_scattered=q)
            chain = route_b_rw_metric_curvature_coefficient(
                ell=3, sector=sector, omega=omega, li_scattered=q
            )
            assert chain.kinnersley_internal_residual == 0
            assert mp.almosteq(chain.recovered_mp_master_coefficient, route_a)
            assert chain.symmetric_r_psi4_reduced == (
                2 * chain.kinnersley_r_psi4_reduced
            )


def test_external_route_and_all_comparators_use_fixed_unfitted_scale() -> None:
    with mp.workdps(80):
        ell = 3
        omega = mp.mpf("1")
        c_lm = mp.mpc("0.25", "0.5")
        schwo_s = mp.mpc("0.1", "-0.2")
        external_s = schwo_s + mp.mpc("1e-8", "-2e-8")
        q = scattered_li_master_coefficient(ell=ell, c_lm=c_lm, S_l=schwo_s)
        route_a = route_a_mp_coefficient(sector="odd", omega=omega, li_scattered=q)
        route_c = route_c_external_mp_coefficient(
            ell=ell,
            sector="odd",
            omega=omega,
            c_lm=c_lm,
            external_S_l=external_s,
        )
        scale = fixed_record_scale(sector="odd", omega=omega, c_lm=c_lm)
        values = compare_route_pair(route_a, route_c, record_scale=scale)
        assert mp.almosteq(
            values.scale_normalized_complex_difference, abs(schwo_s - external_s)
        )
        assert values.signal_floor_value > mp.mpf("0.1")
        assert values.phase_invariant_scale_normalized_magnitude_difference >= 0
        assert values.relative_magnitude_difference >= 0
        assert values.wrapped_relative_phase_rad >= 0


def test_real_frozen_inputs_build_exact_passing_120_record_inventory() -> None:
    gate = verify_frozen_v2_2_inputs(ROOT)
    assert len(gate["frozen_hashes"]) == 23
    bundle = build_v2_2_waveform_route_records(ROOT)
    assert len(bundle.records) == 120
    assert [record["record_ordinal"] for record in bundle.records] == list(range(120))
    assert {
        (record["incident_column"]["column"], record["m"]) for record in bundle.records
    } == {("plus", -2), ("plus", 2), ("cross", -2), ("cross", 2)}
    assert all(
        pair["state"] == "PASS"
        for record in bundle.records
        for pair in record["pairwise_comparisons"].values()
    )
    assert all(
        record["absolute_phase"]["state"] == "PARTIAL" for record in bundle.records
    )
    assert bundle.source_ledger["radial_solve_count"] == 0


def test_external_wp60_strings_are_parsed_source_anchored_from_default_dps() -> None:
    original_dps = mp.mp.dps
    try:
        mp.mp.dps = 15
        bundle = build_v2_2_waveform_route_records(ROOT)
        assert mp.mp.dps == 15
        matched_external = 0
        matched_route_c = 0
        for record in bundle.records:
            inputs = record["route_inputs"]
            source_path = Path(
                record["source_identities"]["external_wp60_node"]["path"]
            )
            node = json.loads(source_path.read_bytes())
            raw = node["phase_factor"]
            assert all(isinstance(raw[part], str) for part in ("real", "imag"))
            assert max(len(raw[part]) for part in ("real", "imag")) >= 40
            assert inputs["external_S_l_source_decimal"] == raw
            assert inputs["external_S_l_parse_dps"] == WORKING_DPS
            with mp.workdps(WORKING_DPS):
                external_s = mp.mpc(mp.mpf(raw["real"]), mp.mpf(raw["imag"]))
                assert inputs["external_S_l"] == complex_record(external_s)
                c_lm = mp.mpc(
                    mp.mpf(inputs["c_lm"]["real"]),
                    mp.mpf(inputs["c_lm"]["imag"]),
                )
                route_c = route_c_external_mp_coefficient(
                    ell=record["radial_key"]["ell"],
                    sector=inputs["sector"],
                    omega=mp.mpf(inputs["omega"]),
                    c_lm=c_lm,
                    external_S_l=external_s,
                )
                assert record["route_amplitudes"]["C"]["coefficient"] == complex_record(
                    route_c
                )
            matched_external += 1
            matched_route_c += 1
        assert matched_external == 120
        assert matched_route_c == 120
    finally:
        mp.mp.dps = original_dps


def test_route_b_module_has_no_forbidden_observer_or_legacy_api() -> None:
    source = (ROOT / "src/schwgw/scattering/phase6_v2_2_waveform_routes.py").read_text(
        encoding="utf-8"
    )
    for forbidden in (
        "static_orthonormal",
        "li_literal_cartesian",
        "pseudoinverse",
        "compute_direct_metric_polarization",
        "polarization_from_weyl",
        "solve_radial_mode",
    ):
        assert forbidden not in source
