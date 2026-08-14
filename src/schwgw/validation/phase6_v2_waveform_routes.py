"""Build, publish, and independently reconstruct Phase-6 V2.2 route evidence."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import json
import os
from pathlib import Path
import stat

import mpmath as mp

from schwgw.scattering.phase6_v2_2_waveform_routes import (
    PairComparatorValues,
    compare_route_pair,
    fixed_record_scale,
    route_a_mp_coefficient,
    route_b_rw_metric_curvature_coefficient,
    route_c_external_mp_coefficient,
)
from schwgw.validation.phase6_v2_mode_amplitudes import (
    canonical_json_bytes,
    complex_record,
    file_identity,
    sha256_file,
    validate_published_v2_1_mode_amplitudes,
    verify_frozen_v2_1_inputs,
)


WORKING_DPS = 80
TERMINAL_DECISION = "CHECKPOINT / V2.2 EXTERNAL WP60 PRECISION REPAIR V3 FROZEN"
RECORD_SCHEMA = "schwgw_phase6_v2_2_waveform_routes_record_v3"
REPORT_SCHEMA = "schwgw_phase6_v2_2_waveform_routes_report_v3"
SUMMARY_SCHEMA = "schwgw_phase6_v2_2_waveform_routes_summary_v3"
LEDGER_SCHEMA = "schwgw_phase6_v2_2_waveform_routes_source_ledger_v3"
MANIFEST_SCHEMA = "schwgw_phase6_v2_2_waveform_routes_manifest_v3"

RELATIVE_THRESHOLD = Path(
    "configs/phase6_v2_2_waveform_threshold_contract_20260811.json"
)
RELATIVE_RATIONALE = Path("docs/phase6_v2_2_waveform_threshold_rationale_20260811.md")
RELATIVE_THRESHOLD_TEST = Path("tests/unit/test_phase6_v2_2_threshold_contract.py")
RELATIVE_PROMPT = Path("docs/prompts/phase6_t6_v2_2_external_precision_repair_v3.md")
RELATIVE_V2_PROMPT = Path("docs/prompts/phase6_t6_v2_2_waveform_routes_v2.md")
RELATIVE_T7_HANDOFF = Path("docs/handoffs/T7_current.md")
RELATIVE_V21_ROOT = Path(
    "runs/phase6/asymptotic_waveform/v2_1_mode_amplitudes_v1_20260810T184729_py314"
)
RELATIVE_EXTERNAL_ROOT = Path(
    "runs/phase6/radial_validation/"
    "v1_external_bhpt_direct_bounded_selected_v1_20260810_py314"
)
RELATIVE_V2_ROOT = Path(
    "runs/phase6/asymptotic_waveform/v2_2_waveform_routes_v2_20260811T104500_py314"
)

FROZEN_HASHES = {
    str(RELATIVE_THRESHOLD): (
        "8c2ab9ca254df9c15e3947479bb0af3bb6204f37d326b52c16a0984604ae005e"
    ),
    str(RELATIVE_RATIONALE): (
        "c96a0c640ffb2789c34e8e9ff364d42cc6cfe427b374a7cff1299d196b3c91b6"
    ),
    str(RELATIVE_THRESHOLD_TEST): (
        "71918930e4b1384ab66adaf5e7d89bc55c31c30f156fa6f153332542759c611a"
    ),
    str(RELATIVE_PROMPT): (
        "8e1c589ff7381b89d76f23e242d2497c2bab73ffcf7823fd998799a3d3cd97a4"
    ),
    str(RELATIVE_V2_PROMPT): (
        "4fd8f01c51cb8df41a14e6ac15b46270e6da108a3fba99b366c61c06b0787689"
    ),
    "configs/phase6_v2_0_convention_contract_20260810.json": (
        "1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517"
    ),
    "configs/phase6_v2_0_selected_domain_20260810.json": (
        "9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818"
    ),
    "runs/phase6/radial_validation/"
    "v1_final_radial_baseline_v2_20260810_py314/plan.json": (
        "de266846ff6672dd04be255a43a1b5899af4753bea0757e00c5c2d60cf2067e3"
    ),
    "src/schwgw/numerics/radial_solver.py": (
        "9b612821535111dd168cc396b8c4159fe216431a855476e397680c5522bf74c9"
    ),
    "src/schwgw/numerics/conditioned_radial.py": (
        "91e2ae94a0353ec204cea48642a3b5d97ae3900de0232a7f32192b8638c7d7e2"
    ),
    "src/schwgw/numerics/scaled_tortoise_radial.py": (
        "d040900516ac1881f8c8579476d3b971a3af8139edc8e3a42110aa6ab21498df"
    ),
    "src/schwgw/numerics/adaptive_jost_radial.py": (
        "3e70defa6f433aa5ef93bd9da9fc86fdca896dd353cff40bef1f1e29ed87b896"
    ),
    "src/schwgw/numerics/matching.py": (
        "9b1a571b76b176a4b50401e26cc4103c7effcce45c8a78b7af59a269b82d9340"
    ),
    "src/schwgw/numerics/physical_boundary_radial.py": (
        "fbd94a2368c774d4a73ae194b472eba58c03ae0b042d7d0b7894a5be22f6967f"
    ),
    "src/schwgw/numerics/boundary_conditions.py": (
        "b6df59207afa1e4a787fe000c22196cbde97a064460c298a97186d68edf56a22"
    ),
    str(RELATIVE_V21_ROOT / "manifest.json"): (
        "ae39829a3e95169f88aa7ce95639e5e3d473c9b7db23d6301cea24d40109ad90"
    ),
    str(RELATIVE_V21_ROOT / "records.jsonl"): (
        "eb0e36ae49a1b868f22279d9948e748a69f89d281890df3e6af5ea4356d1bcc5"
    ),
    str(RELATIVE_EXTERNAL_ROOT / "manifest.json"): (
        "e12c49b00efecc9c65d42699f2a5052ecac1fe2c988312ed21c4da085fe5ee6d"
    ),
    str(RELATIVE_V2_ROOT / "manifest.json"): (
        "7b1fd01983dc03e8c3c027b74e3d01aac2962a129614248d6a2e96284cf5093f"
    ),
    str(RELATIVE_V2_ROOT / "records.jsonl"): (
        "9ae79a006fdbd9f86a385b085bc1cb4d9fcdea52b2debccf7a0b16bfb970ec74"
    ),
    str(RELATIVE_V2_ROOT / "report.json"): (
        "6e9ce7cfb18390e21fbe5385d57ff77acfc3aed7929c294c54cee7b9b1ea5a0a"
    ),
    str(RELATIVE_V2_ROOT / "source_ledger.json"): (
        "18ca221fa2b221bffdc22cd1bcb4f24b91485dce70817ae8003b4b50e81de66d"
    ),
    str(RELATIVE_V2_ROOT / "summary.json"): (
        "76e289f748490b77a6266d7ae6723f7e6f4498cc9660a2a78d402aea31b3966e"
    ),
}

PAIR_AMPLITUDES = {
    "A_B": ("A", "B"),
    "A_C": ("A", "C"),
    "B_C": ("B", "C"),
}
COMPARATOR_FIELDS = {
    "scale_normalized_complex_difference": ("scale_normalized_complex_difference_max"),
    "relative_magnitude_difference": "relative_magnitude_difference_max",
    "wrapped_relative_phase_rad": "wrapped_relative_phase_rad_max",
    "phase_invariant_scale_normalized_magnitude_difference": (
        "phase_invariant_scale_normalized_magnitude_difference_max"
    ),
}
NUMERICAL_COMPONENTS = (
    "radial_source",
    "arithmetic_precision",
    "inner_boundary",
    "outer_boundary_and_jost_order",
    "asymptotic_extraction",
    "route_comparison",
)
CONVENTION_COMPONENTS = (
    "master_normalization",
    "fourier_and_tortoise_phase",
    "incident_partial_wave_normalization",
    "null_tetrad_and_psi4",
    "total_free_scattered_definition",
    "absolute_phase",
)


class Phase6V22Error(ValueError):
    """Fail-closed V2.2 identity, evidence, formula, or publication error."""


@dataclass(frozen=True)
class V22RecordBundle:
    """In-memory three-route evidence constructed without a radial solve."""

    records: tuple[dict[str, object], ...]
    source_ledger: dict[str, object]
    frozen_hashes: dict[str, str]


def _load_json(path: Path) -> Mapping[str, object]:
    try:
        payload = json.loads(path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Phase6V22Error(f"cannot load JSON: {path}") from exc
    if not isinstance(payload, Mapping):
        raise Phase6V22Error(f"JSON root is not an object: {path}")
    return payload


def _direct_immutable_root(path: Path) -> Path:
    absolute = path.absolute()
    if absolute.is_symlink() or absolute.resolve(strict=True) != absolute:
        raise Phase6V22Error(f"immutable root is aliased: {absolute}")
    info = absolute.lstat()
    if not stat.S_ISDIR(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o555:
        raise Phase6V22Error(f"immutable root mode changed: {absolute}")
    return absolute


def _mp_number(value: object, *, label: str) -> mp.mpf:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise Phase6V22Error(f"invalid numeric value: {label}")
    result = mp.mpf(str(value))
    if not mp.isfinite(result):
        raise Phase6V22Error(f"nonfinite numeric value: {label}")
    return result


def _mp_complex(value: object, *, label: str) -> mp.mpc:
    if not isinstance(value, Mapping):
        raise Phase6V22Error(f"invalid complex value: {label}")
    return mp.mpc(
        _mp_number(value.get("real"), label=f"{label}.real"),
        _mp_number(value.get("imag"), label=f"{label}.imag"),
    )


def _decimal(value: mp.mpf) -> str:
    if not mp.isfinite(value):
        raise Phase6V22Error("nonfinite result")
    return mp.nstr(value, n=WORKING_DPS, strip_zeros=False)


def _verify_manifest_members(root: Path, manifest: Mapping[str, object]) -> None:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, Mapping) or len(artifacts) != 92:
        raise Phase6V22Error("external manifest inventory changed")
    for name, raw_identity in artifacts.items():
        if not isinstance(name, str) or not isinstance(raw_identity, Mapping):
            raise Phase6V22Error("external manifest identity changed")
        if file_identity(root / name) != dict(raw_identity):
            raise Phase6V22Error(f"external artifact identity changed: {name}")


def verify_frozen_v2_2_inputs(project_root: str | Path) -> dict[str, object]:
    """Rehash the threshold package and every frozen V2.2 dependency."""

    project = Path(project_root).absolute()
    if project.is_symlink() or project.resolve(strict=True) != project:
        raise Phase6V22Error("project root is aliased")
    hashes: dict[str, str] = {}
    identities: dict[str, object] = {}
    for relative, expected in FROZEN_HASHES.items():
        path = project / relative
        actual = sha256_file(path)
        identity = file_identity(path)
        if actual != expected:
            raise Phase6V22Error(f"frozen input identity mismatch: {relative}")
        hashes[relative] = actual
        identities[relative] = identity

    t7_text = (project / RELATIVE_T7_HANDOFF).read_text(encoding="utf-8")
    v21_decision = (
        "ADVANCE_DECISION: ADVANCE\n"
        "CLAIM_STATUS: PASS\n"
        "GATE_LABEL: ACCEPT GREEN / V2.1 MODE-LEVEL ASYMPTOTIC AMPLITUDES "
        "READY FOR V2.2"
    )
    threshold_decision = (
        "ADVANCE_DECISION: ADVANCE\n"
        "CLAIM_STATUS: PASS\n"
        "GATE_LABEL: ACCEPT GREEN / V2.2 WAVEFORM THRESHOLD CONTRACT READY "
        "FOR EXECUTION"
    )
    repair_decision = (
        "ADVANCE_DECISION: REPAIR\n"
        "CLAIM_STATUS: PARTIAL\n"
        "GATE_LABEL: REVIEW YELLOW / V2.2 CHANGES REQUIRED"
    )
    if (
        v21_decision not in t7_text
        or threshold_decision not in t7_text
        or repair_decision not in t7_text
        or "blocker_id: v22_external_wp60_precision_scope" not in t7_text
        or "completed_bounded_repairs: 0" not in t7_text
        or "same_substantive_blocker_remaining: true" not in t7_text
    ):
        raise Phase6V22Error("required formal T7 decision is missing")

    threshold = _load_json(project / RELATIVE_THRESHOLD)
    if (
        threshold.get("schema") != "schwgw_phase6_v2_2_waveform_threshold_contract_v1"
        or threshold.get("frozen_before_v2_2_execution") is not True
        or threshold.get("science_executed_for_threshold_calibration") is not False
    ):
        raise Phase6V22Error("threshold contract state changed")
    sources = threshold.get("source_identities")
    if not isinstance(sources, Mapping) or len(sources) != 13:
        raise Phase6V22Error("threshold source identity inventory changed")
    threshold_sources: dict[str, object] = {}
    for label, raw in sources.items():
        if not isinstance(label, str) or not isinstance(raw, Mapping):
            raise Phase6V22Error("threshold source identity changed")
        path = project / str(raw.get("path"))
        if sha256_file(path) != raw.get("sha256"):
            raise Phase6V22Error(f"threshold source identity mismatch: {label}")
        threshold_sources[label] = file_identity(path)

    v21_gate = verify_frozen_v2_1_inputs(project)
    v21 = validate_published_v2_1_mode_amplitudes(project / RELATIVE_V21_ROOT)
    external_root = _direct_immutable_root(project / RELATIVE_EXTERNAL_ROOT)
    external_manifest = _load_json(external_root / "manifest.json")
    _verify_manifest_members(external_root, external_manifest)
    return {
        "external_manifest": external_manifest,
        "frozen_hashes": hashes,
        "frozen_identities": identities,
        "threshold": threshold,
        "threshold_sources": threshold_sources,
        "t7_review_identity": file_identity(project / RELATIVE_T7_HANDOFF),
        "v2_1": v21,
        "v2_1_gate": v21_gate,
    }


def _external_inventory(
    project: Path,
    radial_keys: list[object],
    manifest: Mapping[str, object],
) -> tuple[dict[str, object], ...]:
    root = project / RELATIVE_EXTERNAL_ROOT
    artifacts = manifest["artifacts"]
    results = sorted(root.glob("result_*.json"))
    if len(results) != 30 or len(radial_keys) != 30:
        raise Phase6V22Error("external/domain radial-key count changed")
    inventory: list[dict[str, object]] = []
    for radial, result_path in zip(radial_keys, results, strict=True):
        if not isinstance(radial, Mapping):
            raise Phase6V22Error("selected radial-key record changed")
        result = _load_json(result_path)
        expected_key = {
            "ell": radial.get("ell"),
            "kM": radial.get("kM"),
            "sector": radial.get("sector"),
        }
        if (
            result.get("ordinal") != radial.get("ordinal")
            or result.get("key") != expected_key
            or result.get("overall_state") != "PASS"
        ):
            raise Phase6V22Error(f"external result order/state changed: {result_path}")
        node_names = result.get("node_files")
        if not isinstance(node_names, list):
            raise Phase6V22Error("external node inventory changed")
        wp60 = [name for name in node_names if str(name).endswith("__wp60.json")]
        if len(wp60) != 1:
            raise Phase6V22Error("external high-precision node is not unique")
        node_path = root / str(wp60[0])
        node = _load_json(node_path)
        expected_potential = (
            "ReggeWheeler" if radial.get("sector") == "odd" else "Zerilli"
        )
        if (
            node.get("ordinal") != radial.get("ordinal")
            or node.get("key") != expected_key
            or node.get("potential") != expected_potential
            or node.get("parity_derived_even_used") is not False
        ):
            raise Phase6V22Error("external odd/even solver provenance changed")
        result_identity = file_identity(result_path)
        node_identity = file_identity(node_path)
        if (
            not isinstance(artifacts, Mapping)
            or artifacts.get(result_path.name) != result_identity
            or artifacts.get(node_path.name) != node_identity
        ):
            raise Phase6V22Error("external result/node manifest binding changed")
        inventory.append(
            {
                # Keep the immutable decimal strings untouched here.  This loader
                # runs in callers whose ambient mpmath precision may be the default
                # 15 dps; conversion is deliberately delayed to
                # _external_s_from_source() inside mp.workdps(WORKING_DPS).
                "phase_factor_source": node.get("phase_factor"),
                "node": node,
                "node_identity": node_identity,
                "result": result,
                "result_identity": result_identity,
            }
        )
    return tuple(inventory)


def _external_s_from_source(external: Mapping[str, object]) -> mp.mpc:
    """Parse one immutable wp60 phase factor only in the frozen 80-dps context."""

    if mp.mp.dps < WORKING_DPS:
        raise Phase6V22Error("external wp60 conversion requires the 80-dps context")
    source = external.get("phase_factor_source")
    node = external.get("node")
    if not isinstance(node, Mapping) or source != node.get("phase_factor"):
        raise Phase6V22Error("external wp60 decimal source changed")
    return _mp_complex(source, label="external.wp60.phase_factor")


def _threshold_reference(pair: str, field: str, value: object) -> dict[str, object]:
    return {
        "field": f"route_pair_thresholds.{pair}.{field}",
        "path": str(RELATIVE_THRESHOLD),
        "sha256": FROZEN_HASHES[str(RELATIVE_THRESHOLD)],
        "value": value,
    }


def _comparison_record(
    *,
    pair: str,
    values: PairComparatorValues,
    threshold: Mapping[str, object],
) -> dict[str, object]:
    policy = threshold["route_pair_thresholds"][pair]  # type: ignore[index]
    floor = threshold["common_applicability"][  # type: ignore[index]
        "phase_and_relative_magnitude_signal_floor"
    ]
    floor_value = _mp_number(floor, label="signal_floor")
    floor_state = "PASS" if values.signal_floor_value >= floor_value else "FAIL"
    comparators: dict[str, object] = {}
    for name, threshold_field in COMPARATOR_FIELDS.items():
        measured = getattr(values, name)
        bound_raw = policy[threshold_field]  # type: ignore[index]
        bound = _mp_number(bound_raw, label=f"{pair}.{threshold_field}")
        comparators[name] = {
            "state": "PASS" if measured <= bound else "FAIL",
            "threshold": _threshold_reference(pair, threshold_field, bound_raw),
            "value": _decimal(measured),
        }
    state = (
        "PASS"
        if floor_state == "PASS"
        and all(item["state"] == "PASS" for item in comparators.values())  # type: ignore[index]
        else "FAIL"
    )
    return {
        "comparators": comparators,
        "pair": pair,
        "provenance_class": policy["provenance_class"],  # type: ignore[index]
        "signal_floor": {
            "state": floor_state,
            "threshold": {
                "field": (
                    "common_applicability.phase_and_relative_magnitude_signal_floor"
                ),
                "path": str(RELATIVE_THRESHOLD),
                "sha256": FROZEN_HASHES[str(RELATIVE_THRESHOLD)],
                "value": floor,
            },
            "value": _decimal(values.signal_floor_value),
        },
        "state": state,
        "threshold_source": policy["threshold_source"],  # type: ignore[index]
    }


def _numerical_budget(
    *, route_pair_state: str, v21: Mapping[str, object], external: Mapping[str, object]
) -> dict[str, object]:
    source_budget = v21["numerical_uncertainty_budget"]  # type: ignore[index]
    external_result = external["result"]
    return {
        "arithmetic_precision": {
            "state": "PASS",
            "evidence": (
                "original immutable external wp60 decimal strings and all V2.2 "
                f"formulas parsed/evaluated inside mp.workdps({WORKING_DPS})"
            ),
        },
        "asymptotic_extraction": {
            "state": "PASS",
            "evidence": (
                "independent outgoing RW-gauge leading metric coefficients and "
                "direct large-r Kinnersley Z4 limit, then exact symmetric factor two"
            ),
        },
        "inner_boundary": {
            "state": "PASS",
            "evidence": source_budget["inner_boundary"],  # type: ignore[index]
        },
        "outer_boundary_and_jost_order": {
            "state": "PASS",
            "evidence": {
                "SchWO": source_budget["outer_boundary_and_jost_order"],  # type: ignore[index]
                "external": external_result["numerical_uncertainty_budget"],  # type: ignore[index]
            },
        },
        "radial_source": {
            "state": "PASS",
            "evidence": (
                "Routes A/B use immutable accepted SchWO V2.1 input; Route C uses "
                "immutable external direct odd RW / independently solved even Zerilli"
            ),
        },
        "route_comparison": {
            "state": route_pair_state,
            "evidence": "all three route pairs and four frozen comparators evaluated",
        },
    }


def _convention_budget() -> dict[str, object]:
    return {
        "absolute_phase": {
            "state": "PARTIAL",
            "qualification": (
                "frozen claim ceiling; no phase fit, while relative phase remains mandatory"
            ),
        },
        "fourier_and_tortoise_phase": {
            "state": "PASS",
            "evidence": "exp(-i omega t), C_r_star=0 and outgoing exp(-i omega u)",
        },
        "incident_partial_wave_normalization": {
            "state": "PASS",
            "evidence": "frozen V2.1 c_lm and fixed C_record=abs(F_sector*c_lm)",
        },
        "master_normalization": {
            "state": "PASS",
            "evidence": "Psi_ZM=psi_even and Psi_CPM=(2i/omega)Psi_RW",
        },
        "null_tetrad_and_psi4": {
            "state": "PASS",
            "evidence": (
                "direct Kinnersley large-r coefficient multiplied by exactly two "
                "for the frozen symmetric outgoing tetrad"
            ),
        },
        "total_free_scattered_definition": {
            "state": "PASS",
            "evidence": "scattered coefficient only; no incoming or total plane-wave sum",
        },
    }


def _pairwise_provenance() -> dict[str, object]:
    return {
        "A_B": {
            "radial_independent": False,
            "shared_sources": [
                "SchWO V2.1 radial/master coefficient",
                "V2.0 incident, Fourier and MP normalization",
            ],
            "qualification": "independent observable map only",
        },
        "A_C": {
            "radial_independent": True,
            "shared_sources": [
                "V2.0 analytic MP/Fourier/incident/Jost-phase conventions"
            ],
            "qualification": "SchWO versus external direct RW/Zerilli radial algorithms",
        },
        "B_C": {
            "radial_and_observable_algorithms_differ": True,
            "shared_sources": [
                "V2.0 analytic MP/Fourier/incident/NP comparison conventions"
            ],
            "qualification": "not called fully independent of analytic conventions",
        },
    }


def build_v2_2_waveform_route_records(project_root: str | Path) -> V22RecordBundle:
    """Build the exact 120-record, three-route evidence inventory in memory."""

    project = Path(project_root).absolute()
    gate = verify_frozen_v2_2_inputs(project)
    threshold = gate["threshold"]
    v21_bundle = gate["v2_1"]
    if not isinstance(threshold, Mapping) or not isinstance(v21_bundle, Mapping):
        raise Phase6V22Error("frozen gate payload changed")
    v21_records = v21_bundle["records"]
    if not isinstance(v21_records, tuple) or len(v21_records) != 120:
        raise Phase6V22Error("V2.1 record inventory changed")
    domain = gate["v2_1_gate"]["domain"]  # type: ignore[index]
    radial_keys = domain.get("radial_keys") if isinstance(domain, Mapping) else None
    if not isinstance(radial_keys, list):
        raise Phase6V22Error("selected radial-key inventory changed")
    external_inventory = _external_inventory(
        project,
        radial_keys,
        gate["external_manifest"],  # type: ignore[arg-type]
    )
    threshold_policy = threshold.get("separate_uncertainty_budget_policy")
    if (
        not isinstance(threshold_policy, Mapping)
        or threshold_policy.get("numerical_components") != list(NUMERICAL_COMPONENTS)
        or threshold_policy.get("convention_components") != list(CONVENTION_COMPONENTS)
        or threshold_policy.get("combined_scalar_forbidden") is not True
    ):
        raise Phase6V22Error("threshold uncertainty vocabulary changed")

    common_ids = {
        "threshold_contract": file_identity(project / RELATIVE_THRESHOLD),
        "v2_1_manifest": file_identity(project / RELATIVE_V21_ROOT / "manifest.json"),
        "v2_1_records": file_identity(project / RELATIVE_V21_ROOT / "records.jsonl"),
        "external_manifest": file_identity(
            project / RELATIVE_EXTERNAL_ROOT / "manifest.json"
        ),
    }
    records: list[dict[str, object]] = []
    used_external: dict[str, object] = {}
    provenance = _pairwise_provenance()
    with mp.workdps(WORKING_DPS):
        for v21 in v21_records:
            if not isinstance(v21, Mapping):
                raise Phase6V22Error("V2.1 record changed")
            radial = v21.get("radial_key")
            if not isinstance(radial, Mapping):
                raise Phase6V22Error("V2.1 radial key changed")
            radial_ordinal = int(radial["ordinal"])
            external = external_inventory[radial_ordinal]
            sector = str(radial["sector"])
            ell = int(radial["ell"])
            omega = _mp_number(radial["kM"], label="omega")
            li = v21.get("li_normalization")
            if not isinstance(li, Mapping):
                raise Phase6V22Error("V2.1 Li normalization changed")
            c_lm = _mp_complex(li.get("c_lm_p"), label="c_lm")
            q_schwo = _mp_complex(
                li.get("A_out_scattered_physical"), label="Li scattered"
            )
            schwo_s = _mp_complex(
                v21.get("raw_radial_coefficients", {}).get("S_l"),  # type: ignore[union-attr]
                label="SchWO S_l",
            )
            external_s = _external_s_from_source(external)

            route_a = route_a_mp_coefficient(
                sector=sector, omega=omega, li_scattered=q_schwo
            )
            route_b_chain = route_b_rw_metric_curvature_coefficient(
                ell=ell, sector=sector, omega=omega, li_scattered=q_schwo
            )
            route_b = route_b_chain.recovered_mp_master_coefficient
            route_c = route_c_external_mp_coefficient(
                ell=ell,
                sector=sector,
                omega=omega,
                c_lm=c_lm,
                external_S_l=external_s,
            )
            scale = fixed_record_scale(sector=sector, omega=omega, c_lm=c_lm)
            amplitudes = {"A": route_a, "B": route_b, "C": route_c}
            pair_records: dict[str, object] = {}
            for pair, (left, right) in PAIR_AMPLITUDES.items():
                values = compare_route_pair(
                    amplitudes[left], amplitudes[right], record_scale=scale
                )
                pair_records[pair] = _comparison_record(
                    pair=pair, values=values, threshold=threshold
                )
            comparison_state = (
                "PASS"
                if all(item["state"] == "PASS" for item in pair_records.values())  # type: ignore[index]
                else "FAIL"
            )
            result_id = external["result_identity"]
            node_id = external["node_identity"]
            if not isinstance(result_id, Mapping) or not isinstance(node_id, Mapping):
                raise Phase6V22Error("external identity changed")
            used_external[str(result_id["path"])] = dict(result_id)
            used_external[str(node_id["path"])] = dict(node_id)
            records.append(
                {
                    "absolute_phase": {
                        "state": "PARTIAL",
                        "nonclaim": threshold["acceptance_logic"][  # type: ignore[index]
                            "absolute_phase_nonclaim"
                        ],
                        "route_phase_rad": {
                            name: complex_record(value)["phase_rad"]
                            for name, value in amplitudes.items()
                        },
                    },
                    "claims": {
                        "angles_assessed": False,
                        "angular_or_m_sum_assessed": False,
                        "finite_radius_observer_assessed": False,
                        "full_domain_v2": "NOT_ASSESSED",
                        "li_figures_assessed": False,
                        "selected_route_comparator_state": comparison_state,
                        "v1_full_domain_independent_certification": "PARTIAL",
                    },
                    "convention_uncertainty_budget": _convention_budget(),
                    "fixed_record_scale": {
                        "formula": "C_record=abs(F_sector*c_lm)",
                        "fitted": False,
                        "value": _decimal(scale),
                    },
                    "formula_identities": {
                        "H_sc": "F_sector*c_lm*(-1)^ell*(1-S_l)",
                        "F_even": "1",
                        "F_odd": "2 i/omega",
                        "route_b_kinnersley_to_symmetric": "Psi4_symmetric=2 Psi4_K",
                        "route_b_psi4": "Psi4_symmetric=-omega^2(h_plus-i h_cross)",
                    },
                    "incident_column": v21["incident_column"],
                    "m": v21["m"],
                    "normalized_signal": {
                        name: _decimal(abs(value) / scale)
                        for name, value in amplitudes.items()
                    },
                    "numerical_uncertainty_budget": _numerical_budget(
                        route_pair_state=comparison_state,
                        v21=v21,
                        external=external,
                    ),
                    "pairwise_comparisons": pair_records,
                    "pairwise_shared_source_provenance": provenance,
                    "radial_key": dict(radial),
                    "record_ordinal": len(records),
                    "route_amplitudes": {
                        "A": {
                            "coefficient": complex_record(route_a),
                            "route_id": (
                                "A_project_master_to_martel_poisson_strain_flux"
                            ),
                            "source": "accepted V2.1 Li scattered coefficient mapped to ZM/CPM",
                        },
                        "B": {
                            "coefficient": complex_record(route_b),
                            "kinnersley_r_psi4_reduced": complex_record(
                                route_b_chain.kinnersley_r_psi4_reduced
                            ),
                            "kinnersley_internal_residual": complex_record(
                                route_b_chain.kinnersley_internal_residual
                            ),
                            "metric_leading_coefficients": {
                                name: complex_record(value)
                                for name, value in route_b_chain.metric_leading_coefficients.items()
                            },
                            "route_id": (
                                "B_rw_metric_to_direct_curvature_to_asymptotic_psi4_strain"
                            ),
                            "symmetric_r_psi4_reduced": complex_record(
                                route_b_chain.symmetric_r_psi4_reduced
                            ),
                            "tetrad_route": (
                                "direct Kinnersley large-r Z4 from RW metric leading "
                                "coefficients, multiplied by exactly 2 to frozen symmetric tetrad"
                            ),
                        },
                        "C": {
                            "coefficient": complex_record(route_c),
                            "route_id": (
                                "C_external_rw_zerilli_amplitude_to_martel_poisson_strain_flux"
                            ),
                            "source": (
                                "external direct odd Regge-Wheeler / independently solved "
                                "even Zerilli phase_factor=S_l"
                            ),
                        },
                    },
                    "route_inputs": {
                        "SchWO_S_l": complex_record(schwo_s),
                        "c_lm": complex_record(c_lm),
                        "external_S_l": complex_record(external_s),
                        "external_S_l_parse_dps": WORKING_DPS,
                        "external_S_l_source_decimal": external["phase_factor_source"],
                        "li_scattered_SchWO": complex_record(q_schwo),
                        "omega": _decimal(omega),
                        "sector": sector,
                    },
                    "schema": RECORD_SCHEMA,
                    "source_identities": {
                        **common_ids,
                        "external_result": dict(result_id),
                        "external_wp60_node": dict(node_id),
                        "v2_1_record_ordinal": v21["record_ordinal"],
                    },
                }
            )
    if len(records) != 120 or [r["record_ordinal"] for r in records] != list(
        range(120)
    ):
        raise Phase6V22Error("V2.2 record cardinality/order changed")
    if Counter((r["incident_column"]["column"], r["m"]) for r in records) != Counter(  # type: ignore[index]
        {(column, m): 30 for column in ("plus", "cross") for m in (-2, 2)}
    ):
        raise Phase6V22Error("V2.2 channel inventory changed")
    ledger = {
        "arithmetic_runtime": {
            "mpmath_file": file_identity(Path(mp.__file__)),
            "mpmath_version": mp.__version__,
            "working_dps": WORKING_DPS,
        },
        "external_wp60_precision_repair": {
            "conversion_policy": (
                "retain original phase_factor decimal strings until inside "
                "mp.workdps(80)"
            ),
            "publication_reload_policy": (
                "reload immutable wp60 nodes and independently reconstruct all "
                "120 external inputs, Route-C coefficients and comparators"
            ),
            "repair_cycle": 1,
            "superseded_v2_root": str(RELATIVE_V2_ROOT),
        },
        "external_files_consumed": used_external,
        "frozen_inputs": gate["frozen_identities"],
        "implementation_sources": {
            "implementation_note": file_identity(
                project / "docs/phase6_v2_2_waveform_routes_20260811.md"
            ),
            "formula_module": file_identity(
                project / "src/schwgw/scattering/phase6_v2_2_waveform_routes.py"
            ),
            "regression_test": file_identity(
                project / "tests/regression/test_phase6_v2_2_waveform_publication.py"
            ),
            "route_test": file_identity(
                project / "tests/unit/test_phase6_v2_2_waveform_routes.py"
            ),
            "validation_module": file_identity(
                project / "src/schwgw/validation/phase6_v2_waveform_routes.py"
            ),
            **(
                {
                    "publisher": file_identity(
                        project / "scripts/phase6_v2_2_publish_waveform_routes.py"
                    )
                }
                if (
                    project / "scripts/phase6_v2_2_publish_waveform_routes.py"
                ).is_file()
                else {}
            ),
        },
        "pairwise_shared_source_provenance": provenance,
        "radial_solve_count": 0,
        "repair_review_state": {
            "blocker_id": "v22_external_wp60_precision_scope",
            "t7_handoff_identity_at_build": gate["t7_review_identity"],
        },
        "schema": LEDGER_SCHEMA,
        "threshold_source_identities": gate["threshold_sources"],
        "v2_1_source_ledger": file_identity(
            project / RELATIVE_V21_ROOT / "source_ledger.json"
        ),
    }
    hashes = gate["frozen_hashes"]
    if not isinstance(hashes, dict):
        raise Phase6V22Error("frozen hash ledger changed")
    return V22RecordBundle(tuple(records), ledger, dict(hashes))


def _summary(records: tuple[dict[str, object], ...]) -> dict[str, object]:
    failures = sum(
        pair["state"] == "FAIL"  # type: ignore[index]
        for record in records
        for pair in record["pairwise_comparisons"].values()  # type: ignore[union-attr]
    )
    return {
        "absolute_phase": "PARTIAL",
        "angles_assessed": False,
        "angular_or_m_sum_assessed": False,
        "claim_status": "PARTIAL" if failures == 0 else "FAIL",
        "comparator_count": 120 * 3 * 4,
        "comparator_failure_count": failures,
        "finite_radius_observer_assessed": False,
        "full_domain_v2": "NOT_ASSESSED",
        "global_green_permitted": False,
        "global_status": None,
        "li_figures_assessed": False,
        "radial_key_count": 30,
        "radial_pair_count": 15,
        "radial_solve_count": 0,
        "record_count": 120,
        "route_amplitude_count": 360,
        "route_pair_count": 360,
        "schema": SUMMARY_SCHEMA,
        "selected_domain_comparator_state": "PASS" if failures == 0 else "FAIL",
        "total_plane_wave_sum_assessed": False,
        "v1_full_domain_independent_scientific_certification": "PARTIAL",
    }


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _publish_exclusive(path: Path, raw: bytes) -> dict[str, object]:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    with os.fdopen(descriptor, "wb", closefd=True) as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    os.chmod(path, 0o444)
    _fsync_directory(path.parent)
    return file_identity(path)


@contextmanager
def _exclusive_writer(root: Path) -> Iterator[None]:
    lock = root / ".writer.lock"
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(lock, flags, 0o600)
    handle = os.fdopen(descriptor, "wb", closefd=True)
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        handle.write(canonical_json_bytes({"pid": os.getpid(), "schema": "writer_v1"}))
        handle.flush()
        os.fsync(handle.fileno())
        yield
    finally:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()
        lock.unlink()


def publish_v2_2_waveform_routes(
    *,
    project_root: str | Path,
    output_root: str | Path,
    verification: Mapping[str, object],
) -> dict[str, object]:
    """Publish exactly once, seal the root, and strictly reconstruct it."""

    project = Path(project_root).absolute()
    output = Path(output_root).absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"V2.2 output root already exists: {output}")
    start = verify_frozen_v2_2_inputs(project)
    bundle = build_v2_2_waveform_route_records(project)
    output.mkdir(parents=True, mode=0o700)
    os.chmod(output, 0o700)
    with _exclusive_writer(output):
        records_identity = _publish_exclusive(
            output / "records.jsonl",
            b"".join(canonical_json_bytes(record) for record in bundle.records),
        )
        ledger_identity = _publish_exclusive(
            output / "source_ledger.json", canonical_json_bytes(bundle.source_ledger)
        )
        summary = _summary(bundle.records)
        summary_identity = _publish_exclusive(
            output / "summary.json", canonical_json_bytes(summary)
        )
        end = verify_frozen_v2_2_inputs(project)
        if start["frozen_hashes"] != end["frozen_hashes"]:
            raise Phase6V22Error("frozen inputs changed during V2.2 publication")
        if start["t7_review_identity"] != end["t7_review_identity"]:
            raise Phase6V22Error("T7 repair review state changed during publication")
        report = {
            "frozen_input_hashes_end": end["frozen_hashes"],
            "frozen_input_hashes_start": start["frozen_hashes"],
            "global_green_permitted": False,
            "global_status": None,
            "radial_solve_count": 0,
            "record_count": 120,
            "repair_cycle": 1,
            "repair_review_identity_end": end["t7_review_identity"],
            "repair_review_identity_start": start["t7_review_identity"],
            "schema": REPORT_SCHEMA,
            "selected_domain_comparator_state": summary[
                "selected_domain_comparator_state"
            ],
            "terminal_decision": TERMINAL_DECISION,
            "threshold_identities": {
                str(RELATIVE_THRESHOLD): FROZEN_HASHES[str(RELATIVE_THRESHOLD)],
                str(RELATIVE_RATIONALE): FROZEN_HASHES[str(RELATIVE_RATIONALE)],
                str(RELATIVE_THRESHOLD_TEST): FROZEN_HASHES[
                    str(RELATIVE_THRESHOLD_TEST)
                ],
            },
            "verification": dict(verification),
        }
        report_identity = _publish_exclusive(
            output / "report.json", canonical_json_bytes(report)
        )
        manifest = {
            "files": {
                "records.jsonl": records_identity,
                "report.json": report_identity,
                "source_ledger.json": ledger_identity,
                "summary.json": summary_identity,
            },
            "global_green_permitted": False,
            "record_count": 120,
            "schema": MANIFEST_SCHEMA,
            "terminal_decision": TERMINAL_DECISION,
        }
        _publish_exclusive(output / "manifest.json", canonical_json_bytes(manifest))
    for child in output.iterdir():
        os.chmod(child, 0o444)
    os.chmod(output, 0o555)
    _fsync_directory(output)
    _fsync_directory(output.parent)
    reloaded = validate_published_v2_2_waveform_routes(output, project_root=project)
    if reloaded["report"] != report:
        raise Phase6V22Error("independent V2.2 reload report mismatch")
    return report


def _load_canonical_json(path: Path) -> Mapping[str, object]:
    if file_identity(path)["mode"] != 0o444:
        raise Phase6V22Error(f"published mode changed: {path}")
    payload = _load_json(path)
    if path.read_bytes() != canonical_json_bytes(payload):
        raise Phase6V22Error(f"published JSON is not canonical: {path}")
    return payload


def _reconstruct_record(
    record: Mapping[str, object],
    threshold: Mapping[str, object],
    *,
    external: Mapping[str, object],
    v21_source: Mapping[str, object],
) -> None:
    """Reconstruct a published record from V2.1 and original wp60 source bytes."""

    inputs = record.get("route_inputs")
    radial = record.get("radial_key")
    if not isinstance(inputs, Mapping) or not isinstance(radial, Mapping):
        raise Phase6V22Error("published route inputs changed")
    source_radial = v21_source.get("radial_key")
    source_li = v21_source.get("li_normalization")
    if (
        not isinstance(source_radial, Mapping)
        or not isinstance(source_li, Mapping)
        or dict(radial) != dict(source_radial)
        or record.get("source_identities", {}).get("v2_1_record_ordinal")  # type: ignore[union-attr]
        != v21_source.get("record_ordinal")
    ):
        raise Phase6V22Error("published record is not anchored to its V2.1 source")
    sector = str(source_radial["sector"])
    omega = _mp_number(source_radial["kM"], label="source omega")
    ell = int(source_radial["ell"])
    c_lm = _mp_complex(source_li["c_lm_p"], label="source c_lm")
    q_schwo = _mp_complex(
        source_li["A_out_scattered_physical"], label="source SchWO scattered"
    )
    schwo_s = _mp_complex(
        v21_source.get("raw_radial_coefficients", {}).get("S_l"),  # type: ignore[union-attr]
        label="source SchWO S_l",
    )
    external_s = _external_s_from_source(external)
    if (
        inputs.get("sector") != sector
        or inputs.get("omega") != _decimal(omega)
        or inputs.get("c_lm") != complex_record(c_lm)
        or inputs.get("li_scattered_SchWO") != complex_record(q_schwo)
        or inputs.get("SchWO_S_l") != complex_record(schwo_s)
        or inputs.get("external_S_l_parse_dps") != WORKING_DPS
        or inputs.get("external_S_l_source_decimal")
        != external.get("phase_factor_source")
        or inputs.get("external_S_l") != complex_record(external_s)
    ):
        raise Phase6V22Error("published external S_l is not source-anchored at 80 dps")
    a = route_a_mp_coefficient(sector=sector, omega=omega, li_scattered=q_schwo)
    b_chain = route_b_rw_metric_curvature_coefficient(
        ell=ell, sector=sector, omega=omega, li_scattered=q_schwo
    )
    c = route_c_external_mp_coefficient(
        ell=ell,
        sector=sector,
        omega=omega,
        c_lm=c_lm,
        external_S_l=external_s,
    )
    scale = fixed_record_scale(sector=sector, omega=omega, c_lm=c_lm)
    routes = record.get("route_amplitudes")
    if not isinstance(routes, Mapping):
        raise Phase6V22Error("published routes changed")
    expected = {"A": a, "B": b_chain.recovered_mp_master_coefficient, "C": c}
    for name, value in expected.items():
        route = routes.get(name)
        if not isinstance(route, Mapping) or route.get("coefficient") != complex_record(
            value
        ):
            raise Phase6V22Error(f"published Route {name} reconstruction mismatch")
    if record.get("fixed_record_scale", {}).get("value") != _decimal(scale):  # type: ignore[union-attr]
        raise Phase6V22Error("published fixed scale changed")
    pairs = record.get("pairwise_comparisons")
    if not isinstance(pairs, Mapping) or set(pairs) != set(PAIR_AMPLITUDES):
        raise Phase6V22Error("published pair inventory changed")
    for pair, (left, right) in PAIR_AMPLITUDES.items():
        rebuilt = _comparison_record(
            pair=pair,
            values=compare_route_pair(
                expected[left], expected[right], record_scale=scale
            ),
            threshold=threshold,
        )
        if pairs[pair] != rebuilt:
            raise Phase6V22Error(
                f"published comparator reconstruction mismatch: {pair}"
            )


def validate_published_v2_2_waveform_routes(
    root: str | Path, *, project_root: str | Path
) -> dict[str, object]:
    """Strictly reload every byte and independently reconstruct all routes."""

    project = Path(project_root).absolute()
    gate = verify_frozen_v2_2_inputs(project)
    threshold = gate["threshold"]
    if not isinstance(threshold, Mapping):
        raise Phase6V22Error("threshold payload changed")
    v21_bundle = gate["v2_1"]
    domain = gate["v2_1_gate"]["domain"]  # type: ignore[index]
    if not isinstance(v21_bundle, Mapping) or not isinstance(domain, Mapping):
        raise Phase6V22Error("source reconstruction inventory changed")
    v21_records = v21_bundle.get("records")
    radial_keys = domain.get("radial_keys")
    if not isinstance(v21_records, tuple) or not isinstance(radial_keys, list):
        raise Phase6V22Error("source reconstruction cardinality changed")
    external_inventory = _external_inventory(
        project,
        radial_keys,
        gate["external_manifest"],  # type: ignore[arg-type]
    )
    output = _direct_immutable_root(Path(root))
    expected_names = {
        "manifest.json",
        "records.jsonl",
        "report.json",
        "source_ledger.json",
        "summary.json",
    }
    if {item.name for item in output.iterdir()} != expected_names:
        raise Phase6V22Error("published V2.2 file inventory changed")
    manifest = _load_canonical_json(output / "manifest.json")
    report = _load_canonical_json(output / "report.json")
    summary = _load_canonical_json(output / "summary.json")
    ledger = _load_canonical_json(output / "source_ledger.json")
    files = manifest.get("files")
    if not isinstance(files, Mapping) or set(files) != expected_names - {
        "manifest.json"
    }:
        raise Phase6V22Error("published manifest inventory changed")
    for name, identity in files.items():
        if not isinstance(identity, Mapping) or file_identity(output / name) != dict(
            identity
        ):
            raise Phase6V22Error(f"published manifest identity mismatch: {name}")
    records: list[Mapping[str, object]] = []
    for line in (output / "records.jsonl").read_bytes().splitlines(keepends=True):
        payload = json.loads(line)
        if not isinstance(payload, Mapping) or canonical_json_bytes(payload) != line:
            raise Phase6V22Error("published JSONL is not canonical")
        records.append(payload)
    if (
        len(records) != 120
        or [r.get("record_ordinal") for r in records] != list(range(120))
        or Counter((r["incident_column"]["column"], r["m"]) for r in records)  # type: ignore[index]
        != Counter({(column, m): 30 for column in ("plus", "cross") for m in (-2, 2)})
    ):
        raise Phase6V22Error("published V2.2 record structure changed")
    source_anchored_counts = {
        "external_S_l": 0,
        "pairwise_comparisons": 0,
        "route_C_coefficients": 0,
    }
    with mp.workdps(WORKING_DPS):
        for record in records:
            record_ordinal = int(record["record_ordinal"])
            radial_ordinal = int(record["radial_key"]["ordinal"])  # type: ignore[index]
            source = v21_records[record_ordinal]
            external = external_inventory[radial_ordinal]
            if not isinstance(source, Mapping):
                raise Phase6V22Error("V2.1 source record changed")
            _reconstruct_record(
                record,
                threshold,
                external=external,
                v21_source=source,
            )
            source_anchored_counts["external_S_l"] += 1
            source_anchored_counts["route_C_coefficients"] += 1
            source_anchored_counts["pairwise_comparisons"] += 3
            numerical = record.get("numerical_uncertainty_budget")
            convention = record.get("convention_uncertainty_budget")
            if (
                not isinstance(numerical, Mapping)
                or set(numerical) != set(NUMERICAL_COMPONENTS)
                or not isinstance(convention, Mapping)
                or set(convention) != set(CONVENTION_COMPONENTS)
                or convention["absolute_phase"]["state"] != "PARTIAL"  # type: ignore[index]
            ):
                raise Phase6V22Error("published uncertainty budgets changed")
    if source_anchored_counts != {
        "external_S_l": 120,
        "pairwise_comparisons": 360,
        "route_C_coefficients": 120,
    }:
        raise Phase6V22Error("source-anchored reconstruction count changed")
    if (
        manifest.get("schema") != MANIFEST_SCHEMA
        or manifest.get("terminal_decision") != TERMINAL_DECISION
        or report.get("schema") != REPORT_SCHEMA
        or report.get("terminal_decision") != TERMINAL_DECISION
        or report.get("radial_solve_count") != 0
        or summary.get("schema") != SUMMARY_SCHEMA
        or summary.get("record_count") != 120
        or summary.get("radial_solve_count") != 0
        or summary.get("global_status") is not None
        or summary.get("global_green_permitted") is not False
        or ledger.get("schema") != LEDGER_SCHEMA
        or ledger.get("radial_solve_count") != 0
    ):
        raise Phase6V22Error("published report/summary/ledger state changed")
    return {
        "manifest": manifest,
        "records": tuple(records),
        "report": report,
        "source_anchored_reconstruction": {
            **source_anchored_counts,
            "ambient_dps_at_entry": mp.mp.dps,
            "source": "original immutable external wp60 phase_factor decimal strings",
            "working_dps": WORKING_DPS,
        },
        "source_ledger": ledger,
        "summary": summary,
    }


__all__ = [
    "Phase6V22Error",
    "TERMINAL_DECISION",
    "V22RecordBundle",
    "build_v2_2_waveform_route_records",
    "publish_v2_2_waveform_routes",
    "validate_published_v2_2_waveform_routes",
    "verify_frozen_v2_2_inputs",
]
