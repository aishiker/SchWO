from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import runpy
import sys

import mpmath as mp
import pytest

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.perturbations.potentials import (
    regge_wheeler_potential,
    zerilli_potential,
)
from schwgw.validation.phase6_mpmath_radial import (
    EVIDENCE_SCHEMA,
    MpmathRadialContractError,
    MpmathEvaluationPoint,
    MpmathMode,
    MpmathSolveConfig,
    complex_from_record,
    prove_call_graph_isolation,
    radial_potential,
    result_for,
    selected_stage_a_modes,
    solve_mode_batch,
    validate_stage_a_evidence,
    _complex_record,
    _validate_complex_evidence_record,
    _validate_external_comparisons,
    _rhs,
)


def _generic_points() -> tuple[MpmathEvaluationPoint, ...]:
    with mp.workdps(120):
        return tuple(
            MpmathEvaluationPoint(
                f"point_{index}", mp.nstr(mp.sqrt(900 + x * x), 110)
            )
            for index, x in enumerate((0, 1, 2, 3, 10, 15, 20, 25))
        )


def _low_solution(step: float = 0.2):
    batch = solve_mode_batch(
        selected_stage_a_modes()[0],
        MpmathSolveConfig(
            working_dps=40,
            r_in_eps=1.0e-6,
            maximum_step_rstar=step,
        ),
        evaluation_points=_generic_points(),
        r_out_nodes=(100.0,),
        jost_orders=(40,),
    )
    return result_for(batch, r_out=100.0, jost_order=40)


def _available_external_records(mode: MpmathMode) -> list[dict[str, object]]:
    zero = {"real": "0.0", "imag": "0.0", "abs": "0.0"}
    even_flag = False if mode.sector == "even" else None
    return [
        {
            "backend": "project_scipy_jost_radial_solver",
            "status": "AVAILABLE",
            "genuinely_independent": False,
            "shared_components": [],
            "role": "cross-backend comparison only; not part of mpmath call graph",
            "solver": "fixture_float64_solver",
            "actual_precision_bits": 53,
            "actual_decimal_digits": 15.95,
            "S": deepcopy(zero),
            "absolute_S_difference_decimal": "0.0",
            "no_phase_or_normalization_fit": True,
        },
        {
            "backend": "local_mpmath_mst",
            "status": "AVAILABLE",
            "method": "MST recurrence",
            "genuinely_independent": False,
            "independence_role": "algorithmic internal cross-check; not source-independent external evidence",
            "even_independent_solve": even_flag,
            "even_note": (
                "parity-derived; not an independent even radial solve"
                if mode.sector == "even"
                else None
            ),
            "requested_precision_dps": 70,
            "actual_precision_bits": 53,
            "actual_decimal_digits": 15.95,
            "recurrence_residual": "0.0",
            "S": deepcopy(zero),
            "absolute_S_difference_decimal": "0.0",
            "no_phase_or_normalization_fit": True,
        },
        {
            "backend": "frozen_external_bhpt_reggewheeler_mst",
            "status": "AVAILABLE",
            "method": "MST",
            "genuinely_independent": mode.sector == "odd",
            "even_independent_solve": even_flag,
            "even_note": (
                "Chandrasekhar parity-derived; not an independent even solve"
                if mode.sector == "even"
                else None
            ),
            "actual_precision_bits": 53,
            "actual_decimal_digits": 15.95,
            "S": deepcopy(zero),
            "absolute_S_difference_decimal": "0.0",
            "no_phase_or_normalization_fit": True,
        },
    ]


@pytest.mark.parametrize("digits", (50, 70, 100))
@pytest.mark.parametrize(
    "value",
    (
        mp.mpc("-0.999999999999999999999999999999999999", "1e-80"),
        mp.mpc("8.089964910653827338381694687666064477e-228", "-5.553231956553979464254275155405531904e-227"),
        mp.mpc("0.12345678901234567890123456789", "-0.98765432109876543210987654321"),
        mp.mpc(
            "0.000000000000000000000000009353063174916279786258086188929803502405982803869140921254500478941527990823694338649331318153732438",
            "-0.00000000000000000000000000705697439999262878137674078979884152609624884158382139137605855367806692570236472368498462086025867",
        ),
    ),
)
def test_arbitrary_precision_complex_records_are_self_consistent(
    digits: int,
    value: mp.mpc,
) -> None:
    with mp.workdps(140):
        record = _complex_record(value, digits)
    _validate_complex_evidence_record(record, "adversarial AP record")


def _valid_evidence() -> dict:
    baseline = deepcopy(_low_solution())
    script = (
        Path(__file__).resolve().parents[2]
        / "scripts/phase6_mpmath_radial_selected_anchors.py"
    )
    script_namespace = runpy.run_path(str(script))
    axis_record = script_namespace["_axis_record"]
    project_root = Path(__file__).resolve().parents[2]
    backend_source = (
        project_root / "src/schwgw/validation/phase6_mpmath_radial.py"
    ).resolve(strict=True)
    isolation = prove_call_graph_isolation(backend_source)
    v3_diagnostic = json.loads(
        (
            project_root
            / "runs/phase6/radial_validation/"
            "v1_stage_a_mpmath_selected_anchors_v3_20260806_py314/"
            "selected_anchor_evidence.json"
        ).read_text(encoding="utf-8")
    )
    checkpoints_by_mode = {
        record["mode"]["mode_id"]: record["checkpoint_identities"]
        for record in v3_diagnostic["modes"]
    }
    records = []
    for mode in selected_stage_a_modes():
        current = deepcopy(baseline)
        current["mode"] = mode.to_metadata()
        with mp.workdps(120):
            reflected = mp.mpc(
                mp.mpf(current["reflection_amplitude_Aout_over_Ain"]["real"]),
                mp.mpf(current["reflection_amplitude_Aout_over_Ain"]["imag"]),
            )
            scattering = -reflected / ((-1) ** mode.ell)
            current["S"] = {
                "real": mp.nstr(mp.re(scattering), 40),
                "imag": mp.nstr(mp.im(scattering), 40),
                "abs": mp.nstr(abs(scattering), 40),
            }
        current["backend"]["requested_precision_dps"] = 100
        current["backend"]["actual_decimal_digits"] = 100
        current["backend"]["actual_precision_bits"] = 336
        current["backend"]["even_independent_solve"] = mode.sector == "even"
        current["configuration"].update(
            {
                "r_in_eps": 1.0e-6,
                "r_out_M": 300.0,
                "actual_r_out_M": "300.0",
                "r_out_radius_error": "0.0",
                "maximum_step_rstar": 0.025,
                "Jost_order_cap": 160,
                "common_match_radius_M": 60.0,
            }
        )
        axes = {
            "precision_dps": axis_record(
                "precision_dps", (50, 70, 100), (current,) * 3, (None,) * 3
            ),
            "step_rstar": axis_record(
                "step_rstar", (0.1, 0.05, 0.025), (current,) * 3, (None,) * 3
            ),
            "r_in_eps": axis_record(
                "r_in_eps", (3e-6, 1e-6, 3e-7), (current,) * 3, (None,) * 3
            ),
            "r_out_M": axis_record(
                "r_out_M", (300.0, 600.0), (current,) * 2, (None,) * 2
            ),
            "jost_order": axis_record(
                "jost_order", (80, 120, 160), (current,) * 3, (None,) * 3
            ),
        }
        records.append(
            {
                "mode": mode.to_metadata(),
                "status": "STABLE_SELECTED_ANCHOR_INCOMPLETE_LADDERS",
                "baseline": current,
                "S_status": "STABLE_BOUNDED_SELECTED_NODES",
                "finite_radius_state_status": "STABLE_BOUNDED_SELECTED_NODES",
                "finite_radius_state_ladder": {
                    "precision_nodes_dps": [50, 70, 100],
                    "precision_max_relative_state_differences_decimal": ["0.0", "0.0"],
                    "step_nodes_rstar": [0.1, 0.05, 0.025],
                    "step_max_relative_state_differences_decimal": ["0.0", "0.0"],
                    "missing_flag": False,
                    "failure_reason": None,
                    "precision_nonmonotonic_flag": False,
                    "step_nonmonotonic_flag": False,
                    "closure_permitted": False,
                },
                "flux_status": "RESOLVED_INTERNAL_FLUX_ACCOUNTING",
                "ladders": axes,
                "external_comparisons": _available_external_records(mode),
                "numerical_uncertainty": {
                    "metric": "absolute complex S difference",
                    "conservative_max_over_ladders_and_independent_backends_decimal": "0.0",
                    "closed": False,
                    "reason": "bounded Stage-A anchors do not close full V1 uncertainty",
                },
                "convention_uncertainty": {
                    "Fourier_convention": "exp(-i k t)",
                    "S_definition": "-unit_incoming_A_out/[(-1)^ell unit_incoming_A_in]",
                    "tortoise_definition": "r+2 log(r/2-1)",
                    "phase_or_normalization_fit": False,
                    "closed": False,
                },
                "blockers": [],
                "closure_blockers": [
                    "bounded Stage-A nodes omit the full declared Phase-6 ladder",
                    "AP fixed-step ladder is not the production adaptive-tolerance ladder",
                    "full 17,818-key policy-extended union domain is not evaluated",
                ],
                "checkpoint_identities": deepcopy(checkpoints_by_mode[mode.mode_id]),
            }
        )
    source = Path(__file__).resolve(strict=True)
    source_stat = source.stat()
    domain_root = project_root / "runs/phase6/v1_domain_freeze_v3_20260806"
    consumed = [
        (
            "v1_stage_a_mpmath_selected_anchors_v1_20260806_py314",
            "ce797ffff60938b9674aadf996241a51a5f18c070ddec004806ab91e09a68887",
            "a2a57946ef7842b00506de696ab92c710a079465032f322769850595c7f092b1",
            "e7961e278a803543d447d7788410f04f71ef49a2f5ddfbb97a95eeeca3c35c13",
        ),
        (
            "v1_stage_a_mpmath_selected_anchors_v2_20260806_py314",
            "5b7f1366c79e71da189c7edc815e77acb695560df62b642f4ee541c97c4aa6fb",
            "3d191185ba74a1ef4a769162a42b813eae50dc3969620b738a4892a3d071f6f0",
            "0cf03dbff5b78d5e9b52cebf166798f49f18abdb3857af53fbb3dbb00a5f55bc",
        ),
        (
            "v1_stage_a_mpmath_selected_anchors_v3_20260806_py314",
            "2264414fb090018c9ca450b91a021bc34ac2cc4893ffdd45a06a32c37a304d95",
            "6b9f03c972228d2993cbd577a85899c7423f137834bf913cc302c5bee02b988e",
            "1350d28bf97442b2ac7f0b20ed7958f8baca73a95c4c10fd73a5cf4d2f38197d",
        ),
    ]
    point_payload = [point.to_metadata() for point in _generic_points()]
    point_bytes = (
        json.dumps(point_payload, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()
    runtime_output_root = (
        project_root
        / "runs/phase6/radial_validation/"
        "v1_stage_a_mpmath_selected_anchors_v3_20260806_py314"
    ).resolve(strict=True)
    overlay = (
        project_root
        / "runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314"
    ).resolve(strict=True)
    original_argv = list(sys.argv)
    original_sys_path = list(sys.path)
    canonical_prefix = [str(script.parent), str(overlay), str(project_root / "src")]
    sys.argv = [str(script), "--output-root", str(runtime_output_root)]
    sys.path = canonical_prefix + [
        entry for entry in original_sys_path if entry not in set(canonical_prefix)
    ]
    try:
        runtime_identity = script_namespace["_runtime_identity"](
            runtime_output_root
        )
    finally:
        sys.argv = original_argv
        sys.path = original_sys_path
    return {
        "schema_version": EVIDENCE_SCHEMA,
        "scope": "bounded_selected_anchor_pilot",
        "overall_status": "YELLOW_SELECTED_ANCHORS_ONLY",
        "global_green_permitted": False,
        "runtime_identity": runtime_identity,
        "execution_contract": {
            "root": str(
                project_root / "runs/phase6/v1_execution_contract_v4_20260806"
            ),
            "contract_sha256": "25ad4b4e723edbd44651edaa63df415141de504b85288b12c2a6a973fcb420ab",
            "manifest_sha256": "1de9d445d888cbb5ddbf426cc062d2fb5128cad111437ce7d147df6e004aed48",
            "payload_role": "bounded Stage-A calibration payload",
            "resumable_full_shard_pass": False,
        },
        "evaluation_point_contract": {
            "points": point_payload,
            "sha256": hashlib.sha256(point_bytes).hexdigest(),
            "role": "Stage-A runner-frozen finite-state requests; generic backend input",
        },
        "declared_domain": {
            "covered_keys": [mode.to_metadata() for mode in selected_stage_a_modes()],
            "covered_key_count": 8,
            "production_deduplicated_key_count": 16048,
            "production_missing_key_count": 16040,
            "policy_extended_union_key_count": 17818,
            "policy_extended_union_missing_key_count": 17810,
            "audit_extension_key_count": 1770,
            "audit_required_key_count": 3392,
            "production_required_overlap_count": 1622,
            "inventory_provenance": "immutable T8 v1 domain freeze v3",
            "counts_claim_scope": "exact immutable domain manifests",
            "exact_domain_manifests_available": True,
            "domain_freeze": {
                "root": str(domain_root),
                "D_prod_sha256": "54f13ea2473fb0a04ca5e16277edae31335c03b11753973d83a934cce2f0872b",
                "D_ext_sha256": "ec41b9c7898344717f8d290525a2462461dc3614d7fb0b75fe5c8ae4b1e80bfe",
                "D_required_sha256": "2468dbac29608bbfd7faa4143f9632fe3134df1c6a162cdbfbeeba15b7b3e021",
                "D_union_sha256": "a5793564dfc28e815699966208ae6605eeeedce9e3629f09512b70e08196810b",
                "domain_contract_sha256": "7ed99b905c3a1301d96101f357ab1fd9f4bc6e9a4922cb242d28e7cf06bb3bcf",
                "manifest_sha256": "f11d127e0bcfafa8f2fe24b2d3cec3e0cedc60f644d4285e6d52e53d8358d2d2",
            },
            "full_v1_domain_complete": False,
        },
        "backend_identity": {
            "name": "independent_mpmath_rw_zerilli_rk4_jost",
            "implementation_version": "schwgw_phase6_independent_mpmath_radial_backend_v1",
            "implementation_source_sha256": isolation["source_sha256"],
            "actual_backend": f"mpmath {mp.__version__}",
            "genuinely_independent": True,
            "input_sha256": "0" * 64,
            "dependency_hashes": {
                "mpmath_source_sha256": hashlib.sha256(
                    Path(mp.__file__).read_bytes()
                ).hexdigest()
            },
            "shared_components": [
                "RW/Zerilli equations and scattering conventions only"
            ],
            "call_graph_isolation": "AST/import audit; no project SciPy radial/Jost/matching imports or calls",
            "project_scipy_radial_solver_in_backend_call_graph": False,
            "project_jost_in_backend_call_graph": False,
            "project_matching_in_backend_call_graph": False,
        },
        "call_graph_isolation": isolation,
        "diagnostic_thresholds": {
            "scope": "provisional selected-anchor diagnostics only",
            "adaptive_tolerance_ladder_present": False,
        },
        "consumed_diagnostic_roots": [
            {
                "path": str(
                    project_root / "runs/phase6/radial_validation" / name
                ),
                "role": "consumed diagnostic",
                "authoritative": False,
                "evidence_sha256": evidence,
                "manifest_sha256": manifest,
                "checkpoint_sha256": checkpoint,
            }
            for name, evidence, manifest, checkpoint in consumed
        ],
        "modes": records,
        "source_identities": [
            {
                "path": str(source),
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "size": source_stat.st_size,
                "mode": source_stat.st_mode & 0o7777,
                "nlink": source_stat.st_nlink,
            }
        ],
        "limitations": ["selected anchors only"],
        "runtime_cost": {},
    }


def test_selected_stage_a_inventory_spans_both_sectors_and_regimes() -> None:
    modes = selected_stage_a_modes()
    assert len(modes) == 8
    assert {mode.sector for mode in modes} == {"odd", "even"}
    assert {mode.regime for mode in modes} == {
        "low_ell_absorptive",
        "ordinary",
        "turning",
        "q018_anchor",
    }


@pytest.mark.parametrize(("sector", "ell"), [("odd", 2), ("even", 2), ("odd", 20), ("even", 20)])
def test_independent_potentials_equal_project_equations(sector: str, ell: int) -> None:
    background = SchwarzschildBackground(M=1.0)
    for radius in (2.5, 10.0, 60.0):
        independent = float(radial_potential(sector, ell, mp.mpf(str(radius))))
        project = (
            regge_wheeler_potential(ell, radius, background)
            if sector == "odd"
            else zerilli_potential(ell, radius, background)
        )
        assert independent == pytest.approx(project, rel=2e-15, abs=2e-15)


def test_solver_flux_sign_normalization_and_precision_truth() -> None:
    result = _low_solution()
    flux = result["signed_flux"]
    assert float(flux["F_inf_in"]) < 0.0
    assert float(flux["F_inf_out"]) > 0.0
    assert float(flux["F_H"]) == pytest.approx(
        -float(flux["horizon_transmission_fraction"])
    )
    assert flux["horizon_flux_inferred_from_one_minus_R"] is False
    assert float(flux["relative_balance_residual"]) < 1e-4
    assert result["backend"]["requested_precision_dps"] == 40
    assert result["backend"]["actual_decimal_digits"] == 40
    assert result["backend"]["actual_precision_bits"] >= 133
    assert complex_from_record(result["S"]) == pytest.approx(
        -complex_from_record(result["reflection_amplitude_Aout_over_Ain"])
    )
    with mp.workdps(100):
        def parsed(field: str) -> mp.mpc:
            record = result[field]
            return mp.mpc(mp.mpf(record["real"]), mp.mpf(record["imag"]))

        reflection = parsed("reflection_amplitude_Aout_over_Ain")
        transmission = parsed("unit_incoming_horizon_amplitude_T_H")
        assert parsed("unit_incoming_A_in") == 1
        assert parsed("unit_incoming_A_out") == reflection
        assert abs(parsed("horizon_normalized_A_in") * transmission - 1) < mp.mpf(
            "1e-35"
        )
        assert abs(
            parsed("horizon_normalized_A_out") * transmission - reflection
        ) < mp.mpf("1e-35")


def test_step_refinement_reduces_current_drift() -> None:
    coarse = _low_solution(0.1)
    fine = _low_solution(0.05)
    assert float(fine["wronskian"]["maximum_relative_current_drift"]) < float(
        coarse["wronskian"]["maximum_relative_current_drift"]
    )
    assert abs(complex_from_record(fine["S"]) - complex_from_record(coarse["S"])) < 1e-6


@pytest.mark.parametrize("mode_index", [4, 6])
def test_real_bidirectional_turning_and_q018_propagate_two_bases(mode_index: int) -> None:
    mode = selected_stage_a_modes()[mode_index]
    slopes = _rhs(mode, [mp.mpf("100"), 1 + 0j, 2 + 0j, 3 + 0j, 4 + 0j])
    assert len(slopes) == 5
    batch = solve_mode_batch(
        mode,
        MpmathSolveConfig(
            working_dps=35,
            r_in_eps=1.0e-6,
            maximum_step_rstar=1.0,
        ),
        evaluation_points=_generic_points(),
        r_out_nodes=(100.0,),
        jost_orders=(40,),
    )
    result = result_for(batch, r_out=100.0, jost_order=40)
    assert result["configuration"]["integration_architecture"] == (
        "bidirectional_log_derivative_match"
    )
    assert len(result["finite_radius_states"]) == 8
    assert all(
        state["authoritative_branch"] == "T_H times outward horizon solution"
        for state in result["finite_radius_states"]
    )
    assert set(result["unit_incoming_horizon_amplitude_T_H"]) == {
        "real",
        "imag",
        "abs",
    }
    assert result["integration"]["outer_basis_steps"] > 0
    assert result["wronskian"]["raw_unit_horizon_signed_current"] != (
        result["wronskian"]["inner_signed_current"]
    )
    if mode.regime == "q018_anchor":
        assert isinstance(
            result["finite_radius_state_resolution"][
                "outer_combination_crosscheck_resolved"
            ],
            bool,
        )
        authoritative = complex_from_record(
            result["finite_radius_states"][0]["psi_over_Ain"]
        )
        cancellation_dominated = complex_from_record(
            result["finite_radius_states"][0]["outer_combination_crosscheck"][
                "psi_over_Ain"
            ]
        )
        assert authoritative != cancellation_dominated


def test_regime_label_cannot_select_or_change_numerical_backend() -> None:
    original = MpmathMode("label_a", "ordinary", "odd", 2, 0.5)
    relabeled = MpmathMode("label_b", "q018_anchor", "odd", 2, 0.5)
    config = MpmathSolveConfig(working_dps=35, maximum_step_rstar=1.0)
    first = result_for(
        solve_mode_batch(
            original,
            config,
            evaluation_points=_generic_points(),
            r_out_nodes=(100.0,),
            jost_orders=(40,),
        ),
        r_out=100.0,
        jost_order=40,
    )
    second = result_for(
        solve_mode_batch(
            relabeled,
            config,
            evaluation_points=tuple(
                MpmathEvaluationPoint(f"relabel_{index}", point.radius_M)
                for index, point in enumerate(_generic_points())
            ),
            r_out_nodes=(100.0,),
            jost_orders=(40,),
        ),
        r_out=100.0,
        jost_order=40,
    )
    first_configuration = dict(first["configuration"])
    second_configuration = dict(second["configuration"])
    first_configuration.pop("evaluation_points", None)
    second_configuration.pop("evaluation_points", None)
    assert first_configuration == second_configuration
    assert first["S"] == second["S"]
    for left, right in zip(
        first["finite_radius_states"], second["finite_radius_states"]
    ):
        assert left["radius_M"] == right["radius_M"]
        assert left["psi_over_Ain"] == right["psi_over_Ain"]
        assert left["dpsi_dr_over_Ain"] == right["dpsi_dr_over_Ain"]


def test_backend_has_no_stage_a_table_or_point_policy() -> None:
    source = (
        Path(__file__).resolve().parents[2]
        / "src/schwgw/validation/phase6_mpmath_radial.py"
    ).read_text(encoding="utf-8")
    assert "TABLE_I" not in source
    assert "_table_i" not in source
    assert "near_axis" not in source
    assert "mode.regime" not in source


def test_backend_ast_proves_no_project_scipy_jost_or_matching_import() -> None:
    source = (
        Path(__file__).resolve().parents[2]
        / "src/schwgw/validation/phase6_mpmath_radial.py"
    )
    proof = prove_call_graph_isolation(source)
    assert proof["isolation_passed"] is True
    assert proof["forbidden_imports"] == []
    assert proof["forbidden_calls"] == []
    assert proof["imports"] == [
        "__future__",
        "ast",
        "dataclasses",
        "hashlib",
        "json",
        "math",
        "mpmath",
        "os",
        "pathlib",
        "platform",
        "shlex",
        "sys",
        "time",
        "typing",
    ]


def test_external_comparison_inventory_is_fixed_under_each_backend_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    script = (
        Path(__file__).resolve().parents[2]
        / "scripts/phase6_mpmath_radial_selected_anchors.py"
    )
    namespace = runpy.run_path(str(script))
    collect = namespace["_collect_external_comparisons"]
    mode = selected_stage_a_modes()[0]
    available = _available_external_records(mode)
    function_names = ("_scipy_comparison", "_mst_comparison", "_bhpt_comparison")
    backend_ids = [record["backend"] for record in available]

    for failed_index, failed_name in enumerate(function_names):
        for index, function_name in enumerate(function_names):
            if function_name == failed_name:
                def fail(*args: object, name: str = failed_name, **kwargs: object) -> None:
                    del args, kwargs
                    raise RuntimeError(f"forced {name} failure")

                replacement = fail
            else:
                record = available[index]

                def succeed(
                    *args: object,
                    result: dict[str, object] = record,
                    **kwargs: object,
                ) -> dict[str, object]:
                    del args, kwargs
                    return deepcopy(result)

                replacement = succeed
            monkeypatch.setitem(collect.__globals__, function_name, replacement)

        result = collect(mode, {}, [])
        assert [item["backend"] for item in result] == backend_ids
        assert result[failed_index]["status"] == "OPEN_OR_FAIL_CLOSED"
        assert result[failed_index]["genuinely_independent"] is False
        assert "S" not in result[failed_index]
        assert "absolute_S_difference_decimal" not in result[failed_index]
        _validate_external_comparisons(result, mode.to_metadata())


@pytest.mark.parametrize(
    "value",
    (
        complex(-0.9999999999999999, 1.0e-16),
        complex(0.12345678901234568, -0.9876543210987654),
        complex(1.0e-15, -1.0),
    ),
)
def test_float64_comparison_records_are_precision_honest_and_self_consistent(
    value: complex,
) -> None:
    script = (
        Path(__file__).resolve().parents[2]
        / "scripts/phase6_mpmath_radial_selected_anchors.py"
    )
    namespace = runpy.run_path(str(script))
    make_record = namespace["_comparison_complex_record"]
    mode = selected_stage_a_modes()[0]
    records = _available_external_records(mode)
    records[0]["S"] = make_record(value)

    assert all(
        len(
            record.lower()
            .split("e", maxsplit=1)[0]
            .lstrip("+-")
            .replace(".", "")
            .lstrip("0")
        )
        <= 17
        for record in records[0]["S"].values()
    )
    _validate_external_comparisons(records, mode.to_metadata())


def test_runner_significant_digits_ignore_fixed_point_leading_zeros() -> None:
    script = (
        Path(__file__).resolve().parents[2]
        / "scripts/phase6_mpmath_radial_selected_anchors.py"
    )
    namespace = runpy.run_path(str(script))
    count = namespace["_decimal_significant_digits"]

    assert count("0.0000000000000000000000000093530") == 5
    assert count("-7.0560e-27") == 5
    assert count("0.0000") == 1


def test_stage_a_snapshots_sources_before_science_and_rechecks_afterward() -> None:
    script = (
        Path(__file__).resolve().parents[2]
        / "scripts/phase6_mpmath_radial_selected_anchors.py"
    )
    source = script.read_text(encoding="utf-8")
    source = source[source.index("def _run_allocated(") :]
    snapshot = source.index('execution_state["stage"] = "source_identity_snapshot"')
    first_mode = source.index("for mode_index, mode in enumerate(selected_stage_a_modes())")
    recheck = source.index('execution_state["stage"] = "source_identity_recheck"')

    assert snapshot < first_mode < recheck
    assert (
        'raise RuntimeError("Stage-A source/input identity changed during execution")'
        in source
    )


def test_external_comparison_schemas_reject_false_acceptance_surfaces() -> None:
    odd = selected_stage_a_modes()[0]
    even = selected_stage_a_modes()[1]
    available = _available_external_records(odd)
    _validate_external_comparisons(available, odd.to_metadata())
    _validate_external_comparisons(
        _available_external_records(even), even.to_metadata()
    )

    display_label = deepcopy(available)
    display_label[0]["backend"] = "SciPy"
    with pytest.raises(MpmathRadialContractError, match="order mismatch"):
        _validate_external_comparisons(display_label, odd.to_metadata())

    with pytest.raises(MpmathRadialContractError, match="order mismatch"):
        _validate_external_comparisons(
            [available[1], available[0], available[2]], odd.to_metadata()
        )
    with pytest.raises(MpmathRadialContractError, match="order mismatch"):
        _validate_external_comparisons(
            [available[0], available[0], available[2]], odd.to_metadata()
        )
    with pytest.raises(MpmathRadialContractError, match="inventory mismatch"):
        _validate_external_comparisons(available[:2], odd.to_metadata())

    fake_independent = deepcopy(available)
    fake_independent[1]["genuinely_independent"] = True
    with pytest.raises(MpmathRadialContractError, match="independence/schema"):
        _validate_external_comparisons(fake_independent, odd.to_metadata())

    fake_scipy_independent = deepcopy(available)
    fake_scipy_independent[0]["genuinely_independent"] = True
    with pytest.raises(MpmathRadialContractError, match="precision mismatch"):
        _validate_external_comparisons(fake_scipy_independent, odd.to_metadata())

    parity_spoof = _available_external_records(even)
    parity_spoof[2]["genuinely_independent"] = True
    with pytest.raises(MpmathRadialContractError, match="available comparison"):
        _validate_external_comparisons(parity_spoof, even.to_metadata())

    missing_success_field = deepcopy(available)
    del missing_success_field[0]["S"]
    with pytest.raises(MpmathRadialContractError, match="schema/role"):
        _validate_external_comparisons(missing_success_field, odd.to_metadata())

    open_scipy = {
        "backend": "project_scipy_jost_radial_solver",
        "status": "OPEN_OR_FAIL_CLOSED",
        "genuinely_independent": False,
        "shared_components": [],
        "role": "cross-backend comparison only; not part of mpmath call graph",
        "actual_precision_bits": 53,
        "actual_decimal_digits": 15.95,
        "blocker": "fixture failure",
    }
    open_inventory = [open_scipy, available[1], available[2]]
    _validate_external_comparisons(open_inventory, odd.to_metadata())
    mixed_failure = deepcopy(open_inventory)
    mixed_failure[0]["S"] = {"real": "0", "imag": "0", "abs": "0"}
    mixed_failure[0]["absolute_S_difference_decimal"] = "0"
    with pytest.raises(MpmathRadialContractError, match="schema/role"):
        _validate_external_comparisons(mixed_failure, odd.to_metadata())

    forged_open_bhpt = deepcopy(open_inventory)
    forged_open_bhpt[2] = {
        "backend": "frozen_external_bhpt_reggewheeler_mst",
        "status": "OPEN_OR_FAIL_CLOSED",
        "genuinely_independent": True,
        "even_independent_solve": None,
        "actual_precision_bits": 53,
        "actual_decimal_digits": 15.95,
        "blocker": "fixture failure",
    }
    with pytest.raises(MpmathRadialContractError, match="open comparison"):
        _validate_external_comparisons(forged_open_bhpt, odd.to_metadata())


def test_evidence_schema_accepts_selected_scope_and_rejects_overstatement() -> None:
    payload = _valid_evidence()
    validate_stage_a_evidence(payload)

    failed_anchor = deepcopy(payload)
    failed_anchor["modes"][-1]["status"] = "FAIL_CLOSED_NUMERICAL_INSTABILITY"
    failed_anchor["modes"][-1]["baseline"] = None
    failed_anchor["modes"][-1]["blockers"] = ["high-barrier integration failed"]
    failed_anchor["modes"][-1]["external_comparisons"] = []
    failed_anchor["modes"][-1]["numerical_uncertainty"] = {"closed": False}
    failed_anchor["modes"][-1]["convention_uncertainty"] = {"closed": False}
    for field in (
        "S_status",
        "finite_radius_state_status",
        "finite_radius_state_ladder",
        "flux_status",
    ):
        del failed_anchor["modes"][-1][field]
    validate_stage_a_evidence(failed_anchor)

    global_claim = deepcopy(payload)
    global_claim["global_green_permitted"] = True
    with pytest.raises(MpmathRadialContractError, match="global GREEN"):
        validate_stage_a_evidence(global_claim)

    wrong_precision = deepcopy(payload)
    wrong_precision["modes"][0]["baseline"]["backend"]["actual_decimal_digits"] = 53
    with pytest.raises(MpmathRadialContractError, match="decimal digits"):
        validate_stage_a_evidence(wrong_precision)

    parity_derived = deepcopy(payload)
    parity_derived["modes"][1]["baseline"]["backend"]["even_independent_solve"] = False
    with pytest.raises(MpmathRadialContractError, match="independent solve"):
        validate_stage_a_evidence(parity_derived)

    inferred_flux = deepcopy(payload)
    inferred_flux["modes"][0]["baseline"]["signed_flux"][
        "horizon_flux_inferred_from_one_minus_R"
    ] = True
    with pytest.raises(MpmathRadialContractError, match="inferred"):
        validate_stage_a_evidence(inferred_flux)

    spoofed_mode = deepcopy(payload)
    spoofed_mode["modes"][0]["baseline"]["mode"]["ell"] = 3
    with pytest.raises(MpmathRadialContractError, match="outer mode binding"):
        validate_stage_a_evidence(spoofed_mode)

    tiny_abs_spoof = deepcopy(payload)
    tiny_abs_spoof["modes"][0]["baseline"]["finite_radius_states"][0][
        "psi_over_Ain"
    ] = {"real": "1e-300", "imag": "0.0", "abs": "1e-100"}
    with pytest.raises(MpmathRadialContractError, match="magnitude mismatch"):
        validate_stage_a_evidence(tiny_abs_spoof)

    source_spoof = deepcopy(payload)
    source_spoof["source_identities"][0]["sha256"] = "0" * 64
    with pytest.raises(MpmathRadialContractError, match="content/stat drift"):
        validate_stage_a_evidence(source_spoof)

    unhealthy_jost = deepcopy(payload)
    unhealthy_jost["modes"][0]["baseline"]["matching"][
        "basis_determinant_relative"
    ] = "0.0"
    with pytest.raises(MpmathRadialContractError, match="raw gates"):
        validate_stage_a_evidence(unhealthy_jost)

    wrong_ladder_order = deepcopy(payload)
    wrong_ladder_order["modes"][0]["ladders"]["step_rstar"]["nodes"] = [
        0.05,
        0.1,
        0.025,
    ]
    with pytest.raises(MpmathRadialContractError, match="node order"):
        validate_stage_a_evidence(wrong_ladder_order)

    wrong_richardson = deepcopy(payload)
    wrong_richardson["modes"][0]["ladders"]["step_rstar"][
        "remainder_estimate_decimal"
    ] = "1e-3"
    with pytest.raises(MpmathRadialContractError, match="Richardson diagnostics"):
        validate_stage_a_evidence(wrong_richardson)

    inconsistent_blocker = deepcopy(payload)
    inconsistent_blocker["modes"][0]["blockers"] = ["forged blocker"]
    with pytest.raises(MpmathRadialContractError, match="blockers/status"):
        validate_stage_a_evidence(inconsistent_blocker)

    negative_residual = deepcopy(payload)
    negative_residual["modes"][0]["baseline"]["matching"][
        "reconstruction_residual"
    ] = "-1e-30"
    with pytest.raises(MpmathRadialContractError, match="negative"):
        validate_stage_a_evidence(negative_residual)

    config_drift = deepcopy(payload)
    config_drift["modes"][0]["baseline"]["configuration"]["r_out_M"] = 600.0
    with pytest.raises(MpmathRadialContractError, match="configuration drift"):
        validate_stage_a_evidence(config_drift)

    amplitude_drift = deepcopy(payload)
    amplitude_drift["modes"][0]["baseline"]["horizon_normalized_A_in"][
        "real"
    ] = "2.0"
    amplitude_drift["modes"][0]["baseline"]["horizon_normalized_A_in"][
        "abs"
    ] = mp.nstr(
        abs(
            mp.mpc(
                "2.0",
                amplitude_drift["modes"][0]["baseline"][
                    "horizon_normalized_A_in"
                ]["imag"],
            )
        ),
        40,
    )
    with pytest.raises(MpmathRadialContractError, match="amplitude normalization"):
        validate_stage_a_evidence(amplitude_drift)

    runtime_tree_drift = deepcopy(payload)
    runtime_tree_drift["runtime_identity"]["mpmath"]["package_tree"][
        "canonical_inventory_sha256"
    ] = "0" * 64
    with pytest.raises(MpmathRadialContractError, match="package inventory drift"):
        validate_stage_a_evidence(runtime_tree_drift)

    execution_contract_drift = deepcopy(payload)
    execution_contract_drift["execution_contract"]["contract_sha256"] = "0" * 64
    with pytest.raises(MpmathRadialContractError, match="execution-contract binding"):
        validate_stage_a_evidence(execution_contract_drift)


def test_runtime_identity_is_independently_reloadable_and_tamper_evident(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _valid_evidence()
    runtime = payload["runtime_identity"]
    package = runtime["mpmath"]["package_tree"]
    assert package["derived_bytecode_policy"] == (
        "exclude __pycache__ directories and *.pyc files"
    )
    project_root = Path(__file__).resolve().parents[2]
    expected_overlay = (
        project_root
        / "runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314"
    ).resolve(strict=True)
    assert package["root"] == str(expected_overlay)
    relative_paths = {record["relative_path"] for record in package["files"]}
    assert {
        "mpmath/__init__.py",
        "mpmath-1.4.1.dist-info/METADATA",
        "mpmath-1.4.1.dist-info/RECORD",
        "mpmath-1.4.1.dist-info/licenses/LICENSE",
    } <= relative_paths
    assert all(
        "__pycache__" not in Path(record["relative_path"]).parts
        and Path(record["relative_path"]).suffix != ".pyc"
        for record in package["files"]
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["independent_phase6_validator", "--evidence", "immutable.json"],
    )
    monkeypatch.setattr(sys, "path", ["/independent/validator/imports", *sys.path])
    validate_stage_a_evidence(payload)

    argv_drift = deepcopy(payload)
    argv_drift["runtime_identity"]["invocation"]["argv"][1] = "--other-root"
    with pytest.raises(MpmathRadialContractError, match="invocation identity"):
        validate_stage_a_evidence(argv_drift)

    sys_path_drift = deepcopy(payload)
    stored_path = sys_path_drift["runtime_identity"]["loading"]["sys_path"]
    stored_path[1], stored_path[2] = stored_path[2], stored_path[1]
    with pytest.raises(MpmathRadialContractError, match="overlay loading"):
        validate_stage_a_evidence(sys_path_drift)

    environment_drift = deepcopy(payload)
    environment_drift["runtime_identity"]["invocation"]["environment"][
        "PYTHONDONTWRITEBYTECODE"
    ] = "0"
    with pytest.raises(MpmathRadialContractError, match="invocation identity"):
        validate_stage_a_evidence(environment_drift)

    command_drift = deepcopy(payload)
    command_drift["runtime_identity"]["invocation"][
        "reproducible_command"
    ] += " --forged"
    with pytest.raises(MpmathRadialContractError, match="invocation identity"):
        validate_stage_a_evidence(command_drift)

    derived_bytecode_drift = deepcopy(payload)
    derived_package = derived_bytecode_drift["runtime_identity"]["mpmath"][
        "package_tree"
    ]
    derived_package["files"].append(
        {
            "relative_path": "__pycache__/forged.cpython-314.pyc",
            "sha256": "0" * 64,
            "size": 1,
            "mode": 0o444,
            "nlink": 1,
        }
    )
    derived_package["file_count"] += 1
    with pytest.raises(MpmathRadialContractError, match="package inventory"):
        validate_stage_a_evidence(derived_bytecode_drift)

    def refresh_inventory(identity: dict) -> None:
        files = identity["files"]
        identity["file_count"] = len(files)
        identity["canonical_inventory_sha256"] = hashlib.sha256(
            (json.dumps(files, sort_keys=True, separators=(",", ":")) + "\n").encode()
        ).hexdigest()

    missing_metadata = deepcopy(payload)
    missing_package = missing_metadata["runtime_identity"]["mpmath"]["package_tree"]
    missing_package["files"] = [
        record
        for record in missing_package["files"]
        if record["relative_path"] != "mpmath-1.4.1.dist-info/METADATA"
    ]
    refresh_inventory(missing_package)
    with pytest.raises(MpmathRadialContractError, match="distribution inventory"):
        validate_stage_a_evidence(missing_metadata)

    tampered_metadata = deepcopy(payload)
    tampered_package = tampered_metadata["runtime_identity"]["mpmath"][
        "package_tree"
    ]
    next(
        record
        for record in tampered_package["files"]
        if record["relative_path"] == "mpmath-1.4.1.dist-info/METADATA"
    )["sha256"] = "0" * 64
    refresh_inventory(tampered_package)
    with pytest.raises(MpmathRadialContractError, match="package inventory drift"):
        validate_stage_a_evidence(tampered_metadata)

    extra_relevant = deepcopy(payload)
    extra_package = extra_relevant["runtime_identity"]["mpmath"]["package_tree"]
    extra_package["files"].append(
        {
            "relative_path": "mpmath-1.4.1.dist-info/FORGED",
            "sha256": "0" * 64,
            "size": 1,
            "mode": 0o444,
            "nlink": 1,
        }
    )
    refresh_inventory(extra_package)
    with pytest.raises(MpmathRadialContractError, match="package inventory drift"):
        validate_stage_a_evidence(extra_relevant)

    extra_record_field = deepcopy(payload)
    extra_field_package = extra_record_field["runtime_identity"]["mpmath"][
        "package_tree"
    ]
    extra_field_package["files"][0]["unexpected"] = True
    refresh_inventory(extra_field_package)
    with pytest.raises(MpmathRadialContractError, match="package inventory drift"):
        validate_stage_a_evidence(extra_record_field)


def test_runtime_identity_generation_requires_no_bytecode_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    script = (
        Path(__file__).resolve().parents[2]
        / "scripts/phase6_mpmath_radial_selected_anchors.py"
    )
    namespace = runpy.run_path(str(script))
    output_root = (
        Path(__file__).resolve().parents[2]
        / "runs/phase6/radial_validation/"
        "v1_stage_a_mpmath_selected_anchors_v3_20260806_py314"
    ).resolve(strict=True)
    monkeypatch.setenv("PYTHONDONTWRITEBYTECODE", "0")
    with pytest.raises(RuntimeError, match="PYTHONDONTWRITEBYTECODE=1"):
        namespace["_runtime_identity"](output_root)


def test_runtime_inventory_ignores_pyc_but_binds_distribution_files(
    tmp_path: Path,
) -> None:
    script = (
        Path(__file__).resolve().parents[2]
        / "scripts/phase6_mpmath_radial_selected_anchors.py"
    )
    namespace = runpy.run_path(str(script))
    overlay = tmp_path / "overlay"
    package = overlay / "mpmath"
    dist_info = overlay / "mpmath-1.4.1.dist-info"
    cache = package / "__pycache__"
    package.mkdir(parents=True)
    dist_info.mkdir()
    cache.mkdir()
    (package / "__init__.py").write_text("__version__ = '1.4.1'\n", encoding="utf-8")
    (dist_info / "METADATA").write_text("Name: mpmath\n", encoding="utf-8")
    (dist_info / "RECORD").write_text("mpmath/__init__.py,,\n", encoding="utf-8")
    pyc = cache / "__init__.cpython-314.pyc"
    pyc.write_bytes(b"derived-one")
    first = namespace["_package_tree_identity"](overlay)
    pyc.write_bytes(b"derived-two-with-different-bytes")
    second = namespace["_package_tree_identity"](overlay)
    assert first == second
    (dist_info / "LICENSE").write_text("license\n", encoding="utf-8")
    third = namespace["_package_tree_identity"](overlay)
    assert third["canonical_inventory_sha256"] != first["canonical_inventory_sha256"]
    assert third["file_count"] == first["file_count"] + 1


def test_production_comparison_projection_retains_sub_float64_precision() -> None:
    script = (
        Path(__file__).resolve().parents[2]
        / "scripts/phase6_mpmath_radial_selected_anchors.py"
    )
    namespace = runpy.run_path(str(script))
    with mp.workdps(100):
        external = namespace["_external_complex"]("1e-300", "-2e-300")
        reference = namespace["_mp_complex_record_checked"](
            {
                "real": "3e-300",
                "imag": "-2e-300",
                "abs": mp.nstr(mp.sqrt(13) * mp.mpf("1e-300"), 90),
            }
        )
        difference = abs(reference - external)
        assert abs(difference / mp.mpf("2e-300") - 1) < mp.mpf("1e-90")
        assert mp.nstr(difference, 100) != "0.0"


def test_live_axis_projection_is_mpmath_strict_and_never_bridges_failures() -> None:
    script = (
        Path(__file__).resolve().parents[2]
        / "scripts/phase6_mpmath_radial_selected_anchors.py"
    )
    axis_record = runpy.run_path(str(script))["_axis_record"]
    result = _low_solution()
    complete = axis_record(
        "step_rstar",
        (0.1, 0.05, 0.025),
        (result, result, result),
        (None, None, None),
    )
    assert complete["richardson_order"] == 4

    missing_middle = axis_record(
        "step_rstar",
        (0.1, 0.05, 0.025),
        (result, None, result),
        (None, "failed node", None),
    )
    assert missing_middle["adjacent_S_differences_decimal"] == [None, None]
    assert missing_middle["max_adjacent_S_difference_decimal"] is None

    with pytest.raises(RuntimeError, match="length mismatch"):
        axis_record("precision_dps", (50, 70, 100), (result,), (None,))
    drifted_abs = deepcopy(result)
    drifted_abs["S"]["abs"] = "9.0"
    with pytest.raises(RuntimeError, match="absolute value"):
        axis_record(
            "precision_dps",
            (50, 70, 100),
            (result, drifted_abs, result),
            (None, None, None),
        )
