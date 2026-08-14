"""Fail-closed Phase-6 V2 selected-domain release certification.

This module is a release-only consumer.  It natively reloads the immutable
V2.1, V2.2 and V2.3 evidence, derives twelve bounded certificates, and never
calls a solver or evaluates a new scientific observable.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, NoReturn

from schwgw.validation.phase6_v2_flux_closure import (
    _assert_immutable_root,
    _exclusive_writer,
    _seal,
    _validate_manifest,
    _write_exclusive,
    canonical_json_bytes,
    file_identity,
    sha256_file,
    validate_published_v2_3_flux_closure,
)
from schwgw.validation.phase6_v2_mode_amplitudes import (
    validate_published_v2_1_mode_amplitudes,
)
from schwgw.validation.phase6_v2_waveform_routes import (
    validate_published_v2_2_waveform_routes,
)

SCHEMA = "schwgw.phase6.v2_selected_release.v1"
CERTIFICATE_SCHEMA = "schwgw.phase6.v2_selected_release.certificate.v1"
TERMINAL_DECISION = "PASS / V2 SELECTED-DOMAIN RELEASE"
CURRENT_RELEASE_PREFIX = "v2_selected_release_v2_"
REQUIRED_T7_GATE = (
    "ACCEPT GREEN / V2.3 SELECTED-DOMAIN WAVEFORM AND FLUX CLOSURE READY FOR V2.4"
)
DISPATCH_T7_SHA256 = "7876b07b2105c09e6d29b04fa126a71bf9638b462a130ef9474af565b6fadc95"

V21_ROOT = Path(
    "runs/phase6/asymptotic_waveform/v2_1_mode_amplitudes_v1_20260810T184729_py314"
)
V22_ROOT = Path(
    "runs/phase6/asymptotic_waveform/v2_2_waveform_routes_v3_20260811T113135_py314"
)
V23_ROOT = Path(
    "runs/phase6/asymptotic_waveform/v2_3_flux_closure_v2_20260811T050013_py314"
)
V24_V1_ROOT = Path(
    "runs/phase6/asymptotic_waveform/v2_selected_release_v1_20260811T081608_py314"
)

CERTIFICATE_IDS = (
    "V2_MODE_AMPLITUDE_NORMALIZATION",
    "V2_TOTAL_FREE_SCATTERED_DECOMPOSITION",
    "V2_MASTER_ROUTE_WAVEFORM",
    "V2_CURVATURE_ROUTE_WAVEFORM",
    "V2_EXTERNAL_ROUTE_WAVEFORM",
    "V2_ROUTE_CROSSCHECK",
    "V2_INFINITY_FLUX",
    "V2_HORIZON_FLUX",
    "V2_RADIAL_FLUX_BALANCE",
    "V2_WAVEFORM_CURRENT_FLUX_EQUIVALENCE",
    "V2_ABSOLUTE_PHASE_CONVENTION",
    "V2_SELECTED_DOMAIN_RELEASE_POLICY",
)
STATES = frozenset({"PASS", "PARTIAL", "FAIL", "NOT_ASSESSED"})

V21_HASHES = {
    "manifest.json": "ae39829a3e95169f88aa7ce95639e5e3d473c9b7db23d6301cea24d40109ad90",
    "records.jsonl": "eb0e36ae49a1b868f22279d9948e748a69f89d281890df3e6af5ea4356d1bcc5",
    "report.json": "a9fbfd658211eb17b2b7d99177ad233b342eefaafffedf10ba56f0b41fb74a3a",
    "source_ledger.json": "1f3064dd334dbc4e0af2c8772c3230d5fd58fc8172003595eafb41035acd4dbc",
    "summary.json": "ae2e1c226c2330cc6f6fbdbb38381fd4db4ea71d71f504ff766398ab6ede1e27",
}
V22_HASHES = {
    "manifest.json": "3981aeb5424cbac4e7774fc84b5f03d5764561ea21a7338a60f19bf5f0d46660",
    "records.jsonl": "2f7b466036d1481766794aa13581dd9824c851a7e405117f94e192d849f526c9",
    "report.json": "fc66bb1a66f10257b80827ee292d180b0582587c3291332471971731dc352f9b",
    "source_ledger.json": "9fdbd6302fdc0eea93cc1ced1db76f2355343b3538dfee35f5145ac8e5b518a1",
    "summary.json": "fdd314e760c4fa71c555f9eadb13eeb8389d0b24c0f6e8822eb1005afc9b8b19",
}
V23_HASHES = {
    "manifest.json": "a0fc62a4e8fc47176832d8b749285e7f0be9cad46e69911900230f591028694b",
    "records.jsonl": "ba8617224c89c7122e27d0399dafc510d126dd2b4cfd0ca2d8f741ae2a454d39",
    "report.json": "3d8fa27847887f4cb9605f18b1241f948a87362f6a2f3f4e056d678061cd6166",
    "source_ledger.json": "2c91e4b4f1567b5911e3fda2611b64d303e8dba16484be9d450403225677ac2a",
    "summary.json": "336379cf0e20e14af898f4e4dee04523fb851d4c70c23efedfed3d49d935c29f",
}
V24_V1_HASHES = {
    "manifest.json": "1500c198333c87e0a75bdb0bfedf881f11bc9eb307a17fd1ef5cf97a2df27d3f",
    "release_ledger.json": "8bbc4d098ca64ac256a63a09e4e5744191f314038fe140c131eaf7606f75ba49",
    "report.json": "44b6e50302653784798b7015eb9fb5509b08e5f85603a720a5f8216fd1b0fc0c",
    "source_map.json": "bc459ba099dbbec3bf48b7c68c9a55828c2b9029a24afbd0d9143c02166108c7",
    "summary.json": "25dcc333085e3cd7150bf9e954766ae60a942f3a6e51c20ff36a4081077045cb",
}

FROZEN_IDENTITIES: dict[str, str] = {
    "docs/prompts/phase6_t6_v2_4_selected_release.md": (
        "635f08459f876d0be6bd2f9a76acc8bd89cec6ada0529b33318e2010bc500806"
    ),
    "docs/prompts/phase6_t6_v2_1_mode_amplitudes.md": (
        "d5795b7888fee147eefa408cfdbfaef1771bd5d59a7ca0e3bac9aebce2754f55"
    ),
    "docs/prompts/phase6_t6_v2_2_external_precision_repair_v3.md": (
        "8e1c589ff7381b89d76f23e242d2497c2bab73ffcf7823fd998799a3d3cd97a4"
    ),
    "docs/prompts/phase6_t6_v2_2_waveform_routes_v2.md": (
        "4fd8f01c51cb8df41a14e6ac15b46270e6da108a3fba99b366c61c06b0787689"
    ),
    "docs/prompts/phase6_t6_v2_3_flux_closure_v2.md": (
        "25f2f42febaaec9c6eb8ebe621ff1d095648c5aca4f0154c4b3c8b9acd959ba0"
    ),
    "docs/prompts/phase6_t6_v2_3_summary_precision_repair_v2.md": (
        "531cc709a766693d925adb9ff82163648b155adf538540872563d63abdde23c9"
    ),
    "docs/prompts/phase6_t7_v2_3_review_v2.md": (
        "a421746dbc57b01240f960625cd76979221de16fd8f5d349922d5cee74f51b52"
    ),
    "docs/review_gate_liveness_protocol.md": (
        "3dac4a6acf9021ed917cbf911a67d13827a97f3593b67c011ee7c1f162015181"
    ),
    "docs/phase6_v2_0_material_reviews_20260810.md": (
        "0c1e6c5e6735cf3892beb7ffbab6c41cd9e72cd3ecada11bb37059b6e56dbd07"
    ),
    "configs/phase6_v2_2_waveform_threshold_contract_20260811.json": (
        "8c2ab9ca254df9c15e3947479bb0af3bb6204f37d326b52c16a0984604ae005e"
    ),
    "docs/phase6_v2_2_waveform_threshold_rationale_20260811.md": (
        "c96a0c640ffb2789c34e8e9ff364d42cc6cfe427b374a7cff1299d196b3c91b6"
    ),
    "tests/unit/test_phase6_v2_2_threshold_contract.py": (
        "71918930e4b1384ab66adaf5e7d89bc55c31c30f156fa6f153332542759c611a"
    ),
    "configs/phase6_v2_3_flux_threshold_contract_20260811.json": (
        "6cc64b32534c0211da90a7fbec7fb783b91a3b852cfda2991640a37e9de88808"
    ),
    "docs/phase6_v2_3_flux_threshold_rationale_20260811.md": (
        "ce0da14d565bd1db9a63d848f8c7f68078c144899da7911861ad590494586ee8"
    ),
    "tests/unit/test_phase6_v2_3_threshold_contract.py": (
        "ba85493073d653de1ee5847f05668e0eaeb418a3697827df2c2e2b2afe2ea5e4"
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
    "runs/phase6/radial_validation/"
    "v1_radial_selected_acceptance_v1_20260810_py314/manifest.json": (
        "aa66df4f449372e1af660cee8b0757d23ab494bd631bde1c229eb2ee29a2d78c"
    ),
    "runs/phase6/radial_validation/"
    "v1_external_bhpt_direct_bounded_selected_v1_20260810_py314/manifest.json": (
        "e12c49b00efecc9c65d42699f2a5052ecac1fe2c988312ed21c4da085fe5ee6d"
    ),
    "src/schwgw/scattering/gauge_invariant_asymptotics.py": (
        "2942968170b0675bc4c77f487a6cde6bec621969bc1157d69b3c951676c77365"
    ),
    "src/schwgw/validation/phase6_v2_mode_amplitudes.py": (
        "334835c371f4cb8cf0c292f5373f95b11e371c36813b6e450fb85677f83e4b3a"
    ),
    "scripts/phase6_publish_v2_1_mode_amplitudes.py": (
        "1421bf8dc6514d6e45b367a9aa57b76fd60448e42497b768c06d12e8c9e2a227"
    ),
    "tests/unit/test_phase6_v2_mode_amplitudes.py": (
        "cd8d89188020622aebc95e7ff1d1d45418ac0e17b6981e48089d656090c863d5"
    ),
    "tests/regression/test_phase6_v2_1_publication.py": (
        "4b334aef37eff82d05691f4367fb3910205dbc774355f1f8a198192d4094f919"
    ),
    "docs/phase6_v2_1_mode_amplitudes_20260810.md": (
        "8b3bbc9756ec401bb9c6b9ac517f26d5b2baec194f254e3b9581e4ddcb1982c0"
    ),
    "src/schwgw/scattering/phase6_v2_2_waveform_routes.py": (
        "d7a8ca0c711ec5082145556116447f045e73c453b40fa480ec647d178637b515"
    ),
    "src/schwgw/validation/phase6_v2_waveform_routes.py": (
        "2e996d5070f6db370523dbd3c9f620a6b2dcca6c9d37c79c9c9ed2b8860b4fe4"
    ),
    "scripts/phase6_v2_2_publish_waveform_routes.py": (
        "879925a6ea428ba0ccf4e2acadae3a87648ab9b9613771b4af6923b7a803fb47"
    ),
    "tests/unit/test_phase6_v2_2_waveform_routes.py": (
        "da88978565b7587e421f8692fe993a046a1246659caa8e7e41fd31e5978dde27"
    ),
    "tests/regression/test_phase6_v2_2_waveform_publication.py": (
        "a5a7f1879b1d153d31c2a5c6d765d28c4002512bf11e94fca9893a31d88c77d6"
    ),
    "docs/phase6_v2_2_waveform_routes_20260811.md": (
        "ef9c58af085bedb3889a3b72920e41aa6128616d6a57ab58f28e0660bf060f79"
    ),
    "src/schwgw/validation/phase6_v2_flux_closure.py": (
        "dd14b7910890ff752c34e9fae55147a2ad08e33777b07a13919737342f1eaa8a"
    ),
    "scripts/phase6_v2_3_publish_flux_closure.py": (
        "3e07834eb2b948862aac3811659d94cb4896b0c8ee2c8d74e0e4b94f6f62f983"
    ),
    "tests/unit/test_phase6_v2_3_flux_closure.py": (
        "147288fb8416bbaf71847ad69c6b08bbcb2d9b334c870b4bc9e1fe29e6239d08"
    ),
    "tests/regression/test_phase6_v2_3_flux_publication.py": (
        "7db015fd0575dfd8e7355a6724df1f353e5c0dc10709f3eef7efdd751ec71dee"
    ),
    "docs/phase6_v2_3_flux_closure_20260811.md": (
        "aa483b8309d56cbfc96c163f00c87f75b19d2bfe019a4cea9f42270cb6a1b670"
    ),
}
for _root, _hashes in (
    (V21_ROOT, V21_HASHES),
    (V22_ROOT, V22_HASHES),
    (V23_ROOT, V23_HASHES),
    (V24_V1_ROOT, V24_V1_HASHES),
):
    for _name, _digest in _hashes.items():
        FROZEN_IDENTITIES[str(_root / _name)] = _digest

AUTHORITY_IDENTITIES = {
    "convention_contract": {
        "path": "configs/phase6_v2_0_convention_contract_20260810.json",
        "sha256": "1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517",
    },
    "selected_domain": {
        "path": "configs/phase6_v2_0_selected_domain_20260810.json",
        "sha256": "9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818",
    },
    "protected_radial_sources": {
        path: digest
        for path, digest in FROZEN_IDENTITIES.items()
        if path.startswith("src/schwgw/numerics/")
    },
}

NONCLAIMS = {
    "full_domain_v2": "NOT_ASSESSED",
    "v1_full_domain_independent_scientific_certification": "PARTIAL",
    "complete_angular_waveform": "NOT_ASSESSED",
    "finite_radius_observer_response": "NOT_ASSESSED",
    "li_figure_equivalence": "NOT_ASSESSED",
    "parameter_extrapolation_to_17818_keys": "FORBIDDEN",
    "project_wide_status": "NOT_DERIVED",
}


class Phase6V24Error(RuntimeError):
    """Fail-closed V2.4 release error."""


@dataclass(frozen=True)
class ReleaseGate:
    project_root: Path
    identities: tuple[Mapping[str, Any], ...]
    t7_identity: Mapping[str, Any]
    v21: Mapping[str, Any]
    v22: Mapping[str, Any]
    v23: Mapping[str, Any]


def _fail(message: str) -> NoReturn:
    raise Phase6V24Error(message)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> tuple[Mapping[str, Any], ...]:
    return tuple(
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
    )


def _channel(record: Mapping[str, Any]) -> tuple[int, str, int]:
    column = record["incident_column"]
    if isinstance(column, Mapping):
        column = column["column"]
    return int(record["radial_key"]["ordinal"]), str(column), int(record["m"])


def _root_evidence(root: Path, hashes: Mapping[str, str]) -> Mapping[str, Any]:
    return {
        "root": str(root),
        "files": [
            {"path": str(root / name), "sha256": digest}
            for name, digest in hashes.items()
        ],
    }


ROOT_EVIDENCE = {
    "V2.1": _root_evidence(V21_ROOT, V21_HASHES),
    "V2.2": _root_evidence(V22_ROOT, V22_HASHES),
    "V2.3": _root_evidence(V23_ROOT, V23_HASHES),
}


def verify_release_inputs(
    project_root: Path,
    *,
    require_dispatch_review_identity: bool = True,
) -> ReleaseGate:
    """Rehash and natively reload every accepted predecessor."""

    project_root = project_root.resolve()
    identities: list[Mapping[str, Any]] = []
    for relative, expected in FROZEN_IDENTITIES.items():
        path = project_root / relative
        if not path.is_file() or sha256_file(path) != expected:
            _fail(f"frozen V2.4 input identity mismatch: {relative}")
        identities.append(file_identity(path))

    t7_path = project_root / "docs/handoffs/T7_current.md"
    t7_identity = file_identity(t7_path)
    t7_text = t7_path.read_text(encoding="utf-8")
    for required in (
        "ADVANCE_DECISION: ADVANCE",
        "CLAIM_STATUS: PARTIAL",
        f"GATE_LABEL: {REQUIRED_T7_GATE}",
    ):
        if required not in t7_text:
            _fail(f"required V2.4 T7 gate text absent: {required}")
    if require_dispatch_review_identity and t7_identity["sha256"] != DISPATCH_T7_SHA256:
        _fail("V2.4 dispatch T7 handoff identity mismatch")

    for root in (V21_ROOT, V22_ROOT, V23_ROOT):
        _assert_immutable_root(project_root / root, 5)
    _assert_immutable_root(project_root / V24_V1_ROOT, 5)
    _validate_manifest(project_root / V24_V1_ROOT)

    v21 = validate_published_v2_1_mode_amplitudes(project_root / V21_ROOT)
    v22 = validate_published_v2_2_waveform_routes(
        project_root / V22_ROOT, project_root=project_root
    )
    v23 = validate_published_v2_3_flux_closure(project_root / V23_ROOT, project_root)
    _validate_native_evidence(v21, v22, v23)
    return ReleaseGate(
        project_root=project_root,
        identities=tuple(identities),
        t7_identity=t7_identity,
        v21=v21,
        v22=v22,
        v23=v23,
    )


def _validate_native_evidence(
    v21: Mapping[str, Any],
    v22: Mapping[str, Any],
    v23: Mapping[str, Any],
) -> None:
    record_sets = tuple(tuple(bundle["records"]) for bundle in (v21, v22, v23))
    if any(len(records) != 120 for records in record_sets):
        _fail("V2.4 predecessor record cardinality mismatch")
    expected_channels = [("plus", -2), ("plus", 2), ("cross", -2), ("cross", 2)]
    for ordinal in range(30):
        start = ordinal * 4
        for records in record_sets:
            if [
                (_channel(record)[1], _channel(record)[2])
                for record in records[start : start + 4]
            ] != expected_channels:
                _fail(f"V2.4 channel order mismatch at radial key {ordinal}")
            if any(
                _channel(record)[0] != ordinal for record in records[start : start + 4]
            ):
                _fail(f"V2.4 radial-key order mismatch at {ordinal}")
    if any(
        [_channel(record) for record in records]
        != [_channel(record) for record in record_sets[0]]
        for records in record_sets[1:]
    ):
        _fail("V2.4 predecessor inventories are not identical")

    v21_summary = v21["summary"]
    v22_summary = v22["summary"]
    v23_summary = v23["summary"]
    if (
        v21_summary["global_status"] is not None
        or v21_summary["global_green_permitted"]
    ):
        _fail("V2.1 claim ceiling changed")
    if (
        v22_summary["claim_status"] != "PARTIAL"
        or v22_summary["selected_domain_comparator_state"] != "PASS"
        or v22_summary["comparator_failure_count"] != 0
    ):
        _fail("V2.2 accepted selected-domain state changed")
    if (
        v23_summary["claim_status"] != "PARTIAL"
        or v23_summary["selected_domain_flux_closure"] != "PASS"
        or v23_summary["absolute_phase"] != "PARTIAL"
        or v23_summary["full_domain_v2"] != "NOT_ASSESSED"
        or v23_summary["global_status"] is not None
        or v23_summary["global_green_permitted"]
    ):
        _fail("V2.3 accepted selected-domain state changed")

    for record in record_sets[0]:
        if record["claims"]["structural_domain_state"] != "PASS":
            _fail("V2.1 structural record state changed")
        if record["total_free_scattered_identity"]["threshold"] is not None:
            _fail("V2.1 algebraic identity threshold changed")
    for record in record_sets[1]:
        if record["claims"]["selected_route_comparator_state"] != "PASS":
            _fail("V2.2 route record state changed")
        if record["absolute_phase"]["state"] != "PARTIAL":
            _fail("V2.2 absolute-phase ceiling changed")
        if set(record["route_amplitudes"]) != {"A", "B", "C"}:
            _fail("V2.2 route inventory changed")
        for pair in record["pairwise_comparisons"].values():
            if pair["state"] != "PASS" or any(
                item["state"] != "PASS" for item in pair["comparators"].values()
            ):
                _fail("V2.2 comparator state changed")
    for record in record_sets[2]:
        if not record["mandatory_predicates_passed"]:
            _fail("V2.3 mandatory predicate changed")
        if record["radial_solve_count"] != 0:
            _fail("V2.3 radial solve count changed")
        comparators = record["comparators"]
        flat = [
            comparators["schwo_balance"],
            comparators["external_balance"],
            comparators["route_A_B_total_outgoing_flux"],
            comparators["schwo_external_total_outgoing_fraction"],
            comparators["schwo_external_horizon_fraction"],
            *comparators["waveform_current"].values(),
        ]
        if not all(item["passed"] for item in flat):
            _fail("V2.3 comparator state changed")


def _budget_block(
    label: str,
    records: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any]:
    numerical: list[Mapping[str, Any]] = []
    convention: list[Mapping[str, Any]] = []
    for record in records:
        if "uncertainty_budgets" in record:
            numerical.append(record["uncertainty_budgets"]["numerical"])
            convention.append(record["uncertainty_budgets"]["convention"])
        else:
            numerical.append(record["numerical_uncertainty_budget"])
            convention.append(record["convention_uncertainty_budget"])

    def summarize(items: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        components = sorted({key for item in items for key in item})
        state_counts: dict[str, Mapping[str, int]] = {}
        for component in components:
            state_counts[component] = dict(
                sorted(
                    Counter(
                        str(item.get(component, {"state": "NOT_ASSESSED"})["state"])
                        for item in items
                    ).items()
                )
            )
        digest = hashlib.sha256(canonical_json_bytes(list(items))).hexdigest()
        return {
            "source_record_count": len(items),
            "components": components,
            "component_state_counts": state_counts,
            "canonical_source_slice_sha256": digest,
            "missing_component_policy": "PARTIAL_OR_NOT_ASSESSED_NEVER_ZERO_FILLED",
        }

    return {
        "source": label,
        "numerical": summarize(numerical),
        "convention": summarize(convention),
    }


def _domain(records: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    keys: list[Mapping[str, Any]] = []
    for ordinal in range(30):
        key = records[ordinal * 4]["radial_key"]
        keys.append(
            {
                "ordinal": int(key["ordinal"]),
                "sector": key["sector"],
                "ell": int(key["ell"]),
                "kM": key["kM"],
            }
        )
    return {
        "authority": AUTHORITY_IDENTITIES["selected_domain"],
        "scope": "EXACT_SELECTED_DOMAIN_ONLY",
        "radial_pair_count": 15,
        "radial_key_count": 30,
        "radial_keys": keys,
        "m_values": [-2, 2],
        "incident_columns": ["plus", "cross"],
        "channels_per_key": 4,
        "record_count": 120,
        "full_domain_key_count": 17818,
        "extrapolation_permitted": False,
    }


def _evidence(labels: Sequence[str]) -> list[Mapping[str, Any]]:
    return [ROOT_EVIDENCE[label] for label in labels]


def _certificate(
    *,
    certificate_id: str,
    observable: str,
    state: str,
    state_derivation: Mapping[str, Any],
    domain: Mapping[str, Any],
    budgets: Sequence[Mapping[str, Any]],
    evidence_labels: Sequence[str],
    independence_boundary: Mapping[str, Any],
) -> Mapping[str, Any]:
    if state not in STATES:
        _fail(f"invalid V2.4 certificate state: {state}")
    return {
        "schema": CERTIFICATE_SCHEMA,
        "certificate_id": certificate_id,
        "observable": observable,
        "state": state,
        "state_derivation": state_derivation,
        "parameter_channel_domain": domain,
        "numerical_uncertainty_budget": {
            "source_snapshots": [budget["numerical"] for budget in budgets],
            "aggregation": "SOURCE_STATES_PRESERVED_NO_NUMERICAL_RECOMPUTATION",
        },
        "convention_uncertainty_budget": {
            "source_snapshots": [budget["convention"] for budget in budgets],
            "aggregation": "SOURCE_STATES_PRESERVED_NO_CONVENTION_UPGRADE",
        },
        "evidence_roots_and_hashes": _evidence(evidence_labels),
        "accepted_review": {
            "advance_decision": "ADVANCE",
            "claim_status": "PARTIAL",
            "gate_label": REQUIRED_T7_GATE,
            "t7_handoff_path": "docs/handoffs/T7_current.md",
            "t7_handoff_sha256_at_dispatch": DISPATCH_T7_SHA256,
        },
        "independence_boundary": independence_boundary,
        "nonclaims": NONCLAIMS,
        "authority_identities": AUTHORITY_IDENTITIES,
    }


def build_release_ledger(gate: ReleaseGate) -> Mapping[str, Any]:
    """Derive the twelve release certificates without evaluating science."""

    v21_records = tuple(gate.v21["records"])
    v22_records = tuple(gate.v22["records"])
    v23_records = tuple(gate.v23["records"])
    domain = _domain(v21_records)
    budgets = {
        "V2.1": _budget_block("V2.1", v21_records),
        "V2.2": _budget_block("V2.2", v22_records),
        "V2.3": _budget_block("V2.3", v23_records),
    }
    shared_nonclaim = {
        "shared_frozen_conventions": True,
        "selected_domain_only": True,
        "new_science_or_measurement": False,
    }
    specs = (
        (
            "V2_MODE_AMPLITUDE_NORMALIZATION",
            "Li and Martel--Poisson mode-level incoming/outgoing/horizon normalization",
            "PASS",
            {
                "source": "V2.1",
                "field": "claims.structural_domain_state",
                "required": "PASS",
                "records": 120,
            },
            (budgets["V2.1"],),
            ("V2.1",),
            {
                **shared_nonclaim,
                "class": "SAME_SCHWO_RADIAL_SOURCE_ANALYTIC_NORMALIZATION",
            },
        ),
        (
            "V2_TOTAL_FREE_SCATTERED_DECOMPOSITION",
            "complex total = free + scattered asymptotic coefficient identity",
            "PASS",
            {
                "source": "V2.1",
                "field": "total_free_scattered_identity",
                "records": 120,
                "threshold": None,
            },
            (budgets["V2.1"],),
            ("V2.1",),
            {
                **shared_nonclaim,
                "class": "ALGEBRAIC_DEFINITION_CHECK_NO_FITTED_THRESHOLD",
            },
        ),
        (
            "V2_MASTER_ROUTE_WAVEFORM",
            "Route A accepted Li-master to MP ZM/CPM scattered waveform coefficient",
            "PASS",
            {"source": "V2.2", "field": "route_amplitudes.A", "records": 120},
            (budgets["V2.1"], budgets["V2.2"]),
            ("V2.1", "V2.2"),
            {
                **shared_nonclaim,
                "class": "SCHWO_MASTER_ROUTE",
                "shared_radial_source": "V2.1 SchWO",
            },
        ),
        (
            "V2_CURVATURE_ROUTE_WAVEFORM",
            "Route B RW-gauge metric leading coefficient to asymptotic curvature waveform",
            "PASS",
            {
                "source": "V2.2",
                "field": "route_amplitudes.B",
                "records": 120,
                "symmetric_tetrad_factor": 2,
            },
            (budgets["V2.1"], budgets["V2.2"]),
            ("V2.1", "V2.2"),
            {
                **shared_nonclaim,
                "class": "INDEPENDENT_OBSERVABLE_MAP_SHARED_SCHWO_RADIAL_SOURCE",
            },
        ),
        (
            "V2_EXTERNAL_ROUTE_WAVEFORM",
            "Route C external direct odd RW and independently solved even Zerilli waveform",
            "PASS",
            {
                "source": "V2.2",
                "field": "route_amplitudes.C",
                "records": 120,
                "even_parity_derived": False,
            },
            (budgets["V2.2"],),
            ("V2.2",),
            {
                **shared_nonclaim,
                "class": "EXTERNAL_INDEPENDENT_RADIAL_ALGORITHM_SHARED_ANALYTIC_CONVENTIONS",
            },
        ),
        (
            "V2_ROUTE_CROSSCHECK",
            "A/B, A/C and B/C frozen route comparators",
            "PASS",
            {
                "source": "V2.2",
                "field": "selected_domain_comparator_state",
                "required": "PASS",
                "comparator_count": 1440,
                "failures": 0,
            },
            (budgets["V2.2"],),
            ("V2.2",),
            {
                **shared_nonclaim,
                "class": "MIXED_SHARED_AND_INDEPENDENT_ROUTE_SOURCES_NO_RESCALE_OR_PHASE_FIT",
            },
        ),
        (
            "V2_INFINITY_FLUX",
            "selected-domain positive future-null-infinity total-outgoing MP flux",
            "PASS",
            {
                "source": "V2.3",
                "field": "claims.selected_domain_flux_closure",
                "required": "PASS",
                "records": 120,
            },
            (budgets["V2.3"],),
            ("V2.1", "V2.2", "V2.3"),
            {**shared_nonclaim, "class": "TOTAL_OUTGOING_FREE_PLUS_SCATTERED_ONLY"},
        ),
        (
            "V2_HORIZON_FLUX",
            "selected-domain positive future-horizon ingoing MP flux including tiny channels",
            "PASS",
            {
                "source": "V2.3",
                "field": "exact_predicates.no_dropped_tiny_horizon_modes",
                "required": True,
                "records": 120,
            },
            (budgets["V2.3"],),
            ("V2.1", "V2.3"),
            {
                **shared_nonclaim,
                "class": "SCHWO_AND_EXTERNAL_HORIZON_EVIDENCE_NO_SIGNAL_FLOOR",
            },
        ),
        (
            "V2_RADIAL_FLUX_BALANCE",
            "incoming = total outgoing + horizon normalized flux closure",
            "PASS",
            {
                "source": "V2.3",
                "fields": ["comparators.schwo_balance", "comparators.external_balance"],
                "records": 120,
                "all_passed": True,
            },
            (budgets["V2.3"],),
            ("V2.1", "V2.3"),
            {
                **shared_nonclaim,
                "class": "SCHWO_AND_EXTERNAL_RADIAL_BALANCE_SCATTERED_ONLY_FORBIDDEN",
            },
        ),
        (
            "V2_WAVEFORM_CURRENT_FLUX_EQUIVALENCE",
            "amplitude-derived versus signed-current-derived MP flux",
            "PASS",
            {
                "source": "V2.3",
                "field": "comparators.waveform_current",
                "records": 120,
                "channels_per_record": 6,
                "all_passed": True,
            },
            (budgets["V2.3"],),
            ("V2.3",),
            {
                **shared_nonclaim,
                "class": "TWO_ANALYTIC_MAPS_OF_SAME_FROZEN_MODE_COEFFICIENT",
            },
        ),
        (
            "V2_ABSOLUTE_PHASE_CONVENTION",
            "common absolute phase convention across selected waveform routes",
            "PARTIAL",
            {
                "sources": ["V2.2", "V2.3"],
                "fields": ["absolute_phase", "claim_status"],
                "source_ceiling": "PARTIAL",
                "publisher_upgrade_forbidden": True,
            },
            (budgets["V2.2"], budgets["V2.3"]),
            ("V2.2", "V2.3"),
            {
                **shared_nonclaim,
                "class": "RELATIVE_PHASE_TESTED_ABSOLUTE_PHASE_NOT_CONVENTION_FREE",
            },
        ),
        (
            "V2_SELECTED_DOMAIN_RELEASE_POLICY",
            "bounded 30-key/120-record release policy and nonclaim enforcement",
            "PASS",
            {
                "sources": ["V2.1", "V2.2", "V2.3"],
                "certificate_count": 12,
                "global_status": None,
                "source_upgrade": False,
            },
            (budgets["V2.1"], budgets["V2.2"], budgets["V2.3"]),
            ("V2.1", "V2.2", "V2.3"),
            {**shared_nonclaim, "class": "RELEASE_CERTIFIER_ONLY_NATIVE_SOURCE_RELOAD"},
        ),
    )
    certificates = [
        _certificate(
            certificate_id=certificate_id,
            observable=observable,
            state=state,
            state_derivation=derivation,
            domain=domain,
            budgets=budget_sources,
            evidence_labels=evidence_labels,
            independence_boundary=independence,
        )
        for (
            certificate_id,
            observable,
            state,
            derivation,
            budget_sources,
            evidence_labels,
            independence,
        ) in specs
    ]
    validate_certificate_inventory(certificates)
    return {
        "schema": SCHEMA,
        "release_id": "phase6_v2_selected_domain_release_v1",
        "certificates": certificates,
        "certificate_state_counts": {
            "PASS": 11,
            "PARTIAL": 1,
            "FAIL": 0,
            "NOT_ASSESSED": 0,
        },
        "global_status": None,
        "global_green_permitted": False,
        "selected_domain_release_policy": "PASS",
        "claim_status": "PARTIAL",
        "absolute_phase": "PARTIAL",
        "full_domain_v2": "NOT_ASSESSED",
        "radial_solve_count": 0,
        "nonclaims": NONCLAIMS,
    }


def validate_certificate_inventory(certificates: Sequence[Mapping[str, Any]]) -> None:
    if len(certificates) != 12:
        _fail("V2.4 release requires exactly twelve certificates")
    if tuple(item.get("certificate_id") for item in certificates) != CERTIFICATE_IDS:
        _fail("V2.4 certificate identity/order mismatch")
    for item in certificates:
        required = {
            "schema",
            "certificate_id",
            "observable",
            "state",
            "state_derivation",
            "parameter_channel_domain",
            "numerical_uncertainty_budget",
            "convention_uncertainty_budget",
            "evidence_roots_and_hashes",
            "accepted_review",
            "independence_boundary",
            "nonclaims",
            "authority_identities",
        }
        if set(item) != required or item["state"] not in STATES:
            _fail(
                f"V2.4 certificate schema/state mismatch: {item.get('certificate_id')}"
            )
        domain = item["parameter_channel_domain"]
        if domain["record_count"] != 120 or domain["radial_key_count"] != 30:
            _fail("V2.4 certificate domain mismatch")
        if domain["extrapolation_permitted"]:
            _fail("V2.4 certificate permits forbidden domain extrapolation")
        if (
            item["certificate_id"] == "V2_ABSOLUTE_PHASE_CONVENTION"
            and item["state"] != "PARTIAL"
        ):
            _fail("V2.4 absolute-phase source ceiling was upgraded")
    if sum(item["state"] == "PASS" for item in certificates) != 11:
        _fail("V2.4 certificate PASS count mismatch")


def build_release_summary(ledger: Mapping[str, Any]) -> Mapping[str, Any]:
    return {
        "schema": SCHEMA,
        "terminal_decision": TERMINAL_DECISION,
        "certificate_count": 12,
        "certificate_state_counts": ledger["certificate_state_counts"],
        "selected_domain_release_policy": "PASS",
        "claim_status": "PARTIAL",
        "absolute_phase": "PARTIAL",
        "full_domain_v2": "NOT_ASSESSED",
        "v1_full_domain_independent_scientific_certification": "PARTIAL",
        "global_status": None,
        "global_green_permitted": False,
        "radial_key_count": 30,
        "record_count": 120,
        "full_domain_key_count": 17818,
        "domain_extrapolation_permitted": False,
        "radial_solve_count": 0,
        "new_science_computed": False,
        "nonclaims": NONCLAIMS,
    }


def build_source_map(gate: ReleaseGate) -> Mapping[str, Any]:
    owned = (
        gate.project_root / "src/schwgw/validation/phase6_v2_selected_release.py",
        gate.project_root / "scripts/phase6_v2_4_publish_selected_release.py",
        gate.project_root / "tests/unit/test_phase6_v2_4_selected_release.py",
        gate.project_root / "tests/regression/test_phase6_v2_4_release_publication.py",
    )
    return {
        "schema": SCHEMA,
        "frozen_input_identities": list(gate.identities),
        "accepted_predecessor_roots": ROOT_EVIDENCE,
        "superseded_v2_4_v1_release": {
            **_root_evidence(V24_V1_ROOT, V24_V1_HASHES),
            "authority_state": "IMMUTABLE_SUPERSEDED_FORBIDDEN_CURRENT_AUTHORITY",
        },
        "accepted_t7_handoff_at_build": gate.t7_identity,
        "owned_implementation_identities": [file_identity(path) for path in owned],
        "authority_identities": AUTHORITY_IDENTITIES,
        "source_policy": {
            "native_v2_1_reload": True,
            "native_v2_2_reload": True,
            "native_v2_3_reload": True,
            "new_science_computed": False,
            "radial_solver_called": False,
            "angular_sum_performed": False,
            "li_figures_run": False,
        },
        "v2_3_historical_read_only_control_plane_repair": {
            "classification": "CONTROL_PLANE_REPAIR",
            "check_only_requires_dispatch_review_identity": False,
            "historical_reconstruction_tests_require_dispatch_review_identity": False,
            "publish_requires_dispatch_review_identity": True,
            "dispatch_t7_sha256_unchanged": (
                "d8911118767749712b82927c4511a8a9ea3217b1e60808c5ef0101c8ab577554"
            ),
            "science_validation_module_unchanged": {
                "path": "src/schwgw/validation/phase6_v2_flux_closure.py",
                "sha256": (
                    "dd14b7910890ff752c34e9fae55147a2ad08e33777b07a13919737342f1eaa8a"
                ),
            },
            "published_v2_3_roots_changed": False,
            "science_records_changed": False,
        },
        "v2_4_historical_read_only_control_plane_repair": {
            "classification": "CONTROL_PLANE_REPAIR",
            "check_only_requires_dispatch_review_identity": False,
            "historical_reconstruction_tests_require_dispatch_review_identity": False,
            "publish_start_end_require_dispatch_review_identity": True,
            "dispatch_t7_sha256_unchanged": DISPATCH_T7_SHA256,
            "v1_release_authority": "IMMUTABLE_SUPERSEDED_FORBIDDEN_CURRENT_AUTHORITY",
            "v1_release_bytes_changed": False,
            "certificate_derivation_changed": False,
            "threshold_convention_domain_changed": False,
        },
    }


def build_report(
    ledger: Mapping[str, Any],
    summary: Mapping[str, Any],
    verification: Mapping[str, Any],
) -> Mapping[str, Any]:
    return {
        "schema": SCHEMA,
        "terminal_decision": TERMINAL_DECISION,
        "task_class": "RELEASE_CERTIFICATION_AGGREGATION_ONLY",
        "release_ledger": ledger,
        "summary": summary,
        "verification": verification,
        "source_upgrade_permitted": False,
        "global_status": None,
        "global_green_permitted": False,
        "nonclaims": NONCLAIMS,
    }


def _release_manifest(root: Path, names: Sequence[str]) -> Mapping[str, Any]:
    return {
        "schema": SCHEMA,
        "root_name": root.name,
        "artifacts": [
            {
                "path": name,
                "sha256": sha256_file(root / name),
                "bytes": (root / name).stat().st_size,
            }
            for name in names
        ],
    }


def publish_selected_release(
    project_root: Path,
    output_root: Path,
    *,
    verification: Mapping[str, Any],
) -> Mapping[str, Any]:
    project_root = project_root.resolve()
    output_root = output_root.resolve()
    expected_parent = (project_root / "runs/phase6/asymptotic_waveform").resolve()
    if output_root.parent != expected_parent:
        _fail("V2.4 release root outside authorized parent")
    if not output_root.name.startswith(
        CURRENT_RELEASE_PREFIX
    ) or not output_root.name.endswith("_py314"):
        _fail("V2.4 release root name mismatch")
    if output_root.exists():
        _fail("V2.4 release root collision")

    start_gate = verify_release_inputs(project_root)
    ledger = build_release_ledger(start_gate)
    summary = build_release_summary(ledger)
    if (
        canonical_json_bytes(ledger)
        != (project_root / V24_V1_ROOT / "release_ledger.json").read_bytes()
    ):
        _fail("V2.4 repair changed v1 certificate ledger bytes")
    if (
        canonical_json_bytes(summary)
        != (project_root / V24_V1_ROOT / "summary.json").read_bytes()
    ):
        _fail("V2.4 repair changed v1 summary bytes")
    source_map = build_source_map(start_gate)
    report = build_report(ledger, summary, verification)

    output_root.mkdir(mode=0o700)
    with _exclusive_writer(output_root):
        _write_exclusive(
            output_root / "release_ledger.json", canonical_json_bytes(ledger)
        )
        _write_exclusive(
            output_root / "source_map.json", canonical_json_bytes(source_map)
        )
        _write_exclusive(output_root / "summary.json", canonical_json_bytes(summary))
        _write_exclusive(output_root / "report.json", canonical_json_bytes(report))
        end_gate = verify_release_inputs(project_root)
        if (
            end_gate.identities != start_gate.identities
            or end_gate.t7_identity != start_gate.t7_identity
        ):
            _fail("V2.4 source identities changed during publication")
        manifest = _release_manifest(
            output_root,
            ("release_ledger.json", "source_map.json", "summary.json", "report.json"),
        )
        _write_exclusive(output_root / "manifest.json", canonical_json_bytes(manifest))
    directory_fd = os.open(output_root, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    _seal(output_root)
    return validate_published_selected_release(output_root, project_root)


def validate_published_selected_release(
    output_root: Path,
    project_root: Path,
) -> Mapping[str, Any]:
    output_root = output_root.resolve()
    project_root = project_root.resolve()
    _assert_immutable_root(output_root, 5)
    manifest = _validate_manifest(output_root)
    expected = {"release_ledger.json", "source_map.json", "summary.json", "report.json"}
    if {item["path"] for item in manifest["artifacts"]} != expected:
        _fail("V2.4 manifest inventory mismatch")

    gate = verify_release_inputs(project_root, require_dispatch_review_identity=False)
    ledger = _read_json(output_root / "release_ledger.json")
    source_map = _read_json(output_root / "source_map.json")
    summary = _read_json(output_root / "summary.json")
    report = _read_json(output_root / "report.json")
    expected_ledger = build_release_ledger(gate)
    expected_summary = build_release_summary(expected_ledger)
    if ledger != expected_ledger:
        _fail("V2.4 native predecessor reconstruction mismatch")
    if summary != expected_summary:
        _fail("V2.4 release summary reconstruction mismatch")
    if report != build_report(
        expected_ledger, expected_summary, report["verification"]
    ):
        _fail("V2.4 release report reconstruction mismatch")
    if source_map["accepted_t7_handoff_at_build"]["sha256"] != DISPATCH_T7_SHA256:
        _fail("V2.4 build-time T7 identity mismatch")
    if source_map["source_policy"]["radial_solver_called"]:
        _fail("V2.4 source map reports a radial solve")
    if source_map["source_policy"]["new_science_computed"]:
        _fail("V2.4 source map reports new science")
    validate_certificate_inventory(ledger["certificates"])
    return {
        "manifest": manifest,
        "release_ledger": ledger,
        "source_map": source_map,
        "summary": summary,
        "report": report,
    }


def fresh_output_root(project_root: Path, timestamp: str | None = None) -> Path:
    if timestamp is None:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    return (
        project_root
        / "runs/phase6/asymptotic_waveform"
        / f"{CURRENT_RELEASE_PREFIX}{timestamp}_py314"
    )


def validate_in_temporary_copy(output_root: Path, project_root: Path) -> None:
    with tempfile.TemporaryDirectory() as temporary:
        target = Path(temporary) / output_root.name
        target.mkdir(mode=0o700)
        for source in output_root.iterdir():
            target.joinpath(source.name).write_bytes(source.read_bytes())
            target.joinpath(source.name).chmod(0o444)
        target.chmod(0o555)
        validate_published_selected_release(target, project_root)
