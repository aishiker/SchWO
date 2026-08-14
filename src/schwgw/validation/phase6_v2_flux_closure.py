"""Phase-6 V2.3 selected-domain infinity/horizon flux closure.

This module is deliberately a pure, arbitrary-precision consumer of frozen
V1/V2 evidence.  It never invokes a radial solver and never performs an
angular sum.  The public builder reconstructs all 120 records from immutable
source bytes; the publication validator repeats that reconstruction.
"""

from __future__ import annotations

import json
import math
import os
import stat
import tempfile
from collections.abc import Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
import fcntl
from pathlib import Path
from typing import Any, Iterator, NoReturn

import mpmath as mp

from schwgw.validation.phase6_v2_mode_amplitudes import (
    canonical_json_bytes,
    file_identity,
    sha256_file,
    validate_published_v2_1_mode_amplitudes,
)
from schwgw.validation.phase6_v2_waveform_routes import (
    validate_published_v2_2_waveform_routes,
)

WORKING_DPS = 100
SCHEMA = "schwgw.phase6.v2_3_flux_closure.v1"
TERMINAL_DECISION = "PASS / V2.3 SELECTED-DOMAIN FLUX CLOSURE EVIDENCE V2"
REQUIRED_T7_GATE = (
    "ACCEPT GREEN / V2.3 FLUX THRESHOLD CONTRACT READY FOR BOUNDED EXECUTION"
)
REQUIRED_V22_GATE = "ACCEPT GREEN / V2.2 SELECTED-DOMAIN WAVEFORM ROUTES READY FOR V2.3"

THRESHOLD_CONTRACT = Path("configs/phase6_v2_3_flux_threshold_contract_20260811.json")
V22_ROOT = Path(
    "runs/phase6/asymptotic_waveform/v2_2_waveform_routes_v3_20260811T113135_py314"
)
V21_ROOT = Path(
    "runs/phase6/asymptotic_waveform/v2_1_mode_amplitudes_v1_20260810T184729_py314"
)
SELECTED_ROOT = Path(
    "runs/phase6/radial_validation/v1_radial_selected_acceptance_v1_20260810_py314"
)
EXTERNAL_ROOT = Path(
    "runs/phase6/radial_validation/"
    "v1_external_bhpt_direct_bounded_selected_v1_20260810_py314"
)
V23_PREDECESSOR_ROOT = Path(
    "runs/phase6/asymptotic_waveform/v2_3_flux_closure_v1_20260811T044845_py314"
)

FROZEN_IDENTITIES: dict[str, str] = {
    "configs/phase6_v2_3_flux_threshold_contract_20260811.json": (
        "6cc64b32534c0211da90a7fbec7fb783b91a3b852cfda2991640a37e9de88808"
    ),
    "docs/phase6_v2_3_flux_threshold_rationale_20260811.md": (
        "ce0da14d565bd1db9a63d848f8c7f68078c144899da7911861ad590494586ee8"
    ),
    "tests/unit/test_phase6_v2_3_threshold_contract.py": (
        "ba85493073d653de1ee5847f05668e0eaeb418a3697827df2c2e2b2afe2ea5e4"
    ),
    "docs/prompts/phase6_t7_v2_3_threshold_contract_review.md": (
        "128803a461cb82717580959f85d84c55d91278e752b9025391e2336b08ecbafc"
    ),
    "docs/prompts/phase6_t6_v2_3_flux_closure_v2.md": (
        "25f2f42febaaec9c6eb8ebe621ff1d095648c5aca4f0154c4b3c8b9acd959ba0"
    ),
    "docs/prompts/phase6_t6_v2_3_summary_precision_repair_v2.md": (
        "531cc709a766693d925adb9ff82163648b155adf538540872563d63abdde23c9"
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
    str(V22_ROOT / "manifest.json"): (
        "3981aeb5424cbac4e7774fc84b5f03d5764561ea21a7338a60f19bf5f0d46660"
    ),
    str(V22_ROOT / "records.jsonl"): (
        "2f7b466036d1481766794aa13581dd9824c851a7e405117f94e192d849f526c9"
    ),
    str(V22_ROOT / "report.json"): (
        "fc66bb1a66f10257b80827ee292d180b0582587c3291332471971731dc352f9b"
    ),
    str(V22_ROOT / "source_ledger.json"): (
        "9fdbd6302fdc0eea93cc1ced1db76f2355343b3538dfee35f5145ac8e5b518a1"
    ),
    str(V22_ROOT / "summary.json"): (
        "fdd314e760c4fa71c555f9eadb13eeb8389d0b24c0f6e8822eb1005afc9b8b19"
    ),
    str(V23_PREDECESSOR_ROOT / "manifest.json"): (
        "1371e85d80f97c5b3152a5103c3a7bda64a8e0094052cf2e8d3cd8e35d1ceb2b"
    ),
    str(V23_PREDECESSOR_ROOT / "records.jsonl"): (
        "ba8617224c89c7122e27d0399dafc510d126dd2b4cfd0ca2d8f741ae2a454d39"
    ),
    str(V23_PREDECESSOR_ROOT / "report.json"): (
        "d76ed626701f7d40c890a95ee30b32f77ca8314213d36bc6278b9993848afcad"
    ),
    str(V23_PREDECESSOR_ROOT / "source_ledger.json"): (
        "930e68580dd6d7594349af673b6b436118b34657e2bdad84e551c6c25e69f7ee"
    ),
    str(V23_PREDECESSOR_ROOT / "summary.json"): (
        "2b6d334d586b12565a1800ef4edeeea046c2e0151f52bad5adf6ad04447db45e"
    ),
}

DISPATCH_T7_SHA256 = "d8911118767749712b82927c4511a8a9ea3217b1e60808c5ef0101c8ab577554"


class Phase6V23Error(RuntimeError):
    """Fail-closed V2.3 validation error."""


@dataclass(frozen=True)
class FrozenGate:
    contract: Mapping[str, Any]
    identities: tuple[Mapping[str, Any], ...]
    t7_identity: Mapping[str, Any]
    v21_records: tuple[Mapping[str, Any], ...]
    v22_records: tuple[Mapping[str, Any], ...]
    comparisons: tuple[Mapping[str, Any], ...]
    comparison_identities: tuple[Mapping[str, Any], ...]
    external_nodes: tuple[Mapping[str, Any], ...]
    external_node_identities: tuple[Mapping[str, Any], ...]


def _fail(message: str) -> NoReturn:
    raise Phase6V23Error(message)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> tuple[Mapping[str, Any], ...]:
    return tuple(
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
    )


def _mp_real(value: Any) -> mp.mpf:
    if isinstance(value, Mapping):
        if "value" in value:
            value = value["value"]
        else:
            _fail("arbitrary-precision real record is missing value")
    return mp.mpf(str(value))


def _mp_complex(value: Mapping[str, Any]) -> mp.mpc:
    return mp.mpc(_mp_real(value["real"]), _mp_real(value["imag"]))


def _decimal(value: mp.mpf | int, *, digits: int = WORKING_DPS) -> str:
    if isinstance(value, int):
        return str(value)
    return mp.nstr(value, n=digits, strip_zeros=False, min_fixed=-6, max_fixed=20)


def _real_record(value: mp.mpf, *, signed: bool = False) -> Mapping[str, Any]:
    return {
        "value": _decimal(value),
        "sign": int(mp.sign(value)) if signed else None,
        "precision_digits": WORKING_DPS,
        "serialization": "decimal_string_no_binary64",
    }


def _complex_record(value: mp.mpc) -> Mapping[str, Any]:
    return {
        "real": _decimal(value.real),
        "imag": _decimal(value.imag),
        "abs": _decimal(abs(value)),
        "phase": _decimal(mp.arg(value)),
        "precision_digits": WORKING_DPS,
        "serialization": "decimal_string_no_binary64",
    }


def _close(left: mp.mpc | mp.mpf, right: mp.mpc | mp.mpf) -> bool:
    if left == right:
        return True
    scale = max(abs(left), abs(right))
    return bool(scale != 0 and abs(left - right) <= mp.mpf("1e-75") * scale)


def _relative_difference(left: mp.mpf, right: mp.mpf) -> mp.mpf:
    scale = max(abs(left), abs(right))
    if scale == 0:
        return mp.mpf(0)
    return abs(left - right) / scale


def _symmetric_relative_difference(left: mp.mpf, right: mp.mpf) -> mp.mpf:
    """Frozen V2.3 symmetric relative comparator: |a-b|/max(|a|,|b|)."""

    denom = max(abs(left), abs(right))
    if denom == 0:
        return mp.mpf(0)
    return abs(left - right) / denom


def normalized_balance_residual(
    incoming_flux: mp.mpf,
    total_outgoing_flux: mp.mpf,
    horizon_flux: mp.mpf,
) -> mp.mpf:
    """Return |F_in-F_out,total-F_horizon|/F_in without a signal floor."""

    if incoming_flux <= 0:
        _fail("incoming flux must be strictly positive")
    return abs(incoming_flux - total_outgoing_flux - horizon_flux) / incoming_flux


def _assert_immutable_root(root: Path, expected_files: int | None = None) -> None:
    root_info = root.lstat()
    if root.is_symlink() or not stat.S_ISDIR(root_info.st_mode):
        _fail(f"missing immutable root: {root}")
    if stat.S_IMODE(root.stat().st_mode) != 0o555:
        _fail(f"immutable root mode mismatch: {root}")
    files = tuple(path for path in root.rglob("*") if path.is_file())
    if expected_files is not None and len(files) != expected_files:
        _fail(f"immutable root file-count mismatch: {root}")
    for path in files:
        info = path.lstat()
        if path.is_symlink() or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            _fail(f"immutable source is not a direct single-link file: {path}")
        if stat.S_IMODE(path.stat().st_mode) != 0o444:
            _fail(f"immutable source file mode mismatch: {path}")


def _validate_manifest(root: Path) -> Mapping[str, Any]:
    manifest = _read_json(root / "manifest.json")
    artifacts = manifest.get("artifacts")
    if isinstance(artifacts, Mapping):
        items = tuple(artifacts.values())
    elif isinstance(artifacts, list):
        items = tuple(artifacts)
    else:
        _fail(f"manifest artifact inventory missing: {root}")
    for item in items:
        raw_path = Path(str(item["path"]))
        path = raw_path if raw_path.is_absolute() else root / raw_path
        if not path.is_file():
            _fail(f"manifest path missing: {path}")
        expected_size = item.get("bytes", item.get("size"))
        if sha256_file(path) != item["sha256"] or path.stat().st_size != expected_size:
            _fail(f"manifest identity mismatch: {path}")
    return manifest


def _validate_gate_text(path: Path, required: Sequence[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for item in required:
        if item not in text:
            _fail(f"required gate text absent from {path}: {item}")


def verify_frozen_v2_3_inputs(
    project_root: Path,
    *,
    require_dispatch_review_identity: bool = True,
) -> FrozenGate:
    """Rehash and natively reload every frozen V2.3 input."""

    project_root = project_root.resolve()
    identities: list[Mapping[str, Any]] = []
    for relative, expected in FROZEN_IDENTITIES.items():
        path = project_root / relative
        if not path.is_file() or sha256_file(path) != expected:
            _fail(f"frozen input identity mismatch: {relative}")
        identities.append(file_identity(path))

    t7_path = project_root / "docs/handoffs/T7_current.md"
    t7_identity = file_identity(t7_path)
    if require_dispatch_review_identity and t7_identity["sha256"] != DISPATCH_T7_SHA256:
        _fail("dispatch T7 handoff identity mismatch")
    _validate_gate_text(
        t7_path,
        (
            "ADVANCE_DECISION: ADVANCE",
            "CLAIM_STATUS: PASS",
            f"GATE_LABEL: {REQUIRED_T7_GATE}",
            f"GATE_LABEL: {REQUIRED_V22_GATE}",
        ),
    )

    contract_path = project_root / THRESHOLD_CONTRACT
    contract = _read_json(contract_path)
    for source in contract["source_identities"].values():
        path = project_root / source["path"]
        if sha256_file(path) != source["sha256"]:
            _fail(f"threshold-contract source identity mismatch: {source['path']}")

    selected_root = project_root / SELECTED_ROOT
    _assert_immutable_root(selected_root, 33)
    _validate_manifest(selected_root)

    external_root = project_root / EXTERNAL_ROOT
    _assert_immutable_root(external_root, 93)
    _validate_manifest(external_root)

    predecessor_root = project_root / V23_PREDECESSOR_ROOT
    _assert_immutable_root(predecessor_root, 5)
    _validate_manifest(predecessor_root)

    v21_root = project_root / V21_ROOT
    _assert_immutable_root(v21_root, 5)
    v21_bundle = validate_published_v2_1_mode_amplitudes(v21_root)
    v21_records = tuple(v21_bundle["records"])

    v22_root = project_root / V22_ROOT
    _assert_immutable_root(v22_root, 5)
    v22_bundle = validate_published_v2_2_waveform_routes(
        v22_root, project_root=project_root
    )
    v22_records = tuple(v22_bundle["records"])

    comparison_paths = tuple(sorted(selected_root.glob("comparison_*.json")))
    comparisons = tuple(_read_json(path) for path in comparison_paths)
    comparison_identities = tuple(file_identity(path) for path in comparison_paths)
    node_paths = tuple(sorted(external_root.glob("node_*__wp60.json")))
    external_nodes = tuple(_read_json(path) for path in node_paths)
    node_identities = tuple(file_identity(path) for path in node_paths)

    if not (
        len(v21_records) == 120
        and len(v22_records) == 120
        and len(comparisons) == 30
        and len(external_nodes) == 30
    ):
        _fail("frozen V2.3 source cardinality mismatch")

    return FrozenGate(
        contract=contract,
        identities=tuple(identities),
        t7_identity=t7_identity,
        v21_records=v21_records,
        v22_records=v22_records,
        comparisons=comparisons,
        comparison_identities=comparison_identities,
        external_nodes=external_nodes,
        external_node_identities=node_identities,
    )


def _threshold(contract: Mapping[str, Any], field: str) -> mp.mpf:
    value: Any = contract["frozen_thresholds"]
    for part in field.split("."):
        value = value[part]
    if isinstance(value, Mapping):
        value = value["value"]
    return _mp_real(value)


def _threshold_result(
    *,
    value: mp.mpf,
    contract: Mapping[str, Any],
    field: str,
    predicate: str,
) -> Mapping[str, Any]:
    threshold = _threshold(contract, field)
    if predicate == "less_than_or_equal":
        passed = bool(value <= threshold)
        symbol = "<="
    elif predicate == "strict_less_than":
        passed = bool(value < threshold)
        symbol = "<"
    else:
        _fail(f"unsupported threshold predicate: {predicate}")
    return {
        "value": _real_record(value),
        "threshold": _real_record(threshold),
        "predicate": predicate,
        "symbol": symbol,
        "passed": passed,
        "threshold_field": f"frozen_thresholds.{field}.value",
        "threshold_path": str(THRESHOLD_CONTRACT),
        "threshold_sha256": FROZEN_IDENTITIES[str(THRESHOLD_CONTRACT)],
    }


def _boundary_evidence(
    amplitude: mp.mpc,
    *,
    omega: mp.mpf,
    sigma_l: int,
    orientation: int,
) -> Mapping[str, Any]:
    magnitude_squared = abs(amplitude) ** 2
    signed_current = orientation * omega * magnitude_squared
    flux_from_amplitude = mp.mpf(sigma_l) * omega**2 * magnitude_squared / (128 * mp.pi)
    flux_from_current = mp.mpf(sigma_l) * omega * abs(signed_current) / (128 * mp.pi)
    return {
        "amplitude": _complex_record(amplitude),
        "amplitude_squared": _real_record(magnitude_squared),
        "signed_current": _real_record(signed_current, signed=True),
        "current_orientation": orientation,
        "flux_from_amplitude": _real_record(flux_from_amplitude),
        "flux_from_current": _real_record(flux_from_current),
        "waveform_current_relative_residual": _real_record(
            _relative_difference(flux_from_amplitude, flux_from_current)
        ),
    }


def _selected_external_coefficients(
    node: Mapping[str, Any],
    *,
    expected_ordinal: int,
    expected_sector: str,
    expected_ell: int,
) -> tuple[mp.mpc, mp.mpc, mp.mpc, mp.mpc, mp.mpc, mp.mpc, int]:
    if node["ordinal"] != expected_ordinal:
        _fail("external node ordinal mismatch")
    if node["key"]["sector"] != expected_sector:
        _fail("external node sector mismatch")
    if node["key"]["ell"] != expected_ell:
        _fail("external node ell mismatch")
    if node["potential"] != ("ReggeWheeler" if expected_sector == "odd" else "Zerilli"):
        _fail("external direct potential mismatch")
    if expected_sector == "even" and node.get("parity_derived_even_used") is not False:
        _fail("external even witness is not independently solved")

    index = int(node["selected_match_index"])
    selected = node["match_records"][index]
    matching_incidence = _mp_complex(selected["incidence"])
    matching_reflection = _mp_complex(selected["reflection"])
    incidence = mp.mpc(1)
    reflection = _mp_complex(selected["reflection_ratio"])
    transmission = _mp_complex(selected["transmission"])
    phase_factor = _mp_complex(selected["phase_factor"])
    if not _close(phase_factor, _mp_complex(node["phase_factor"])):
        _fail("external selected phase-factor identity mismatch")
    if not _close(transmission, _mp_complex(node["transmission"])):
        _fail("external selected transmission identity mismatch")
    return (
        incidence,
        reflection,
        transmission,
        phase_factor,
        matching_incidence,
        matching_reflection,
        index,
    )


def _uncertainty_budgets() -> Mapping[str, Any]:
    numerical = {
        name: {
            "state": "ASSESSED",
            "zero_filled": False,
            "assessment": "thresholded per record from frozen evidence",
        }
        for name in (
            "schwo_radial_balance",
            "external_radial_balance",
            "arithmetic_precision",
            "waveform_current_map",
            "route_A_B_flux_map",
            "schwo_external_outgoing_flux",
            "schwo_external_horizon_flux",
        )
    }
    convention = {
        name: {
            "state": "ASSESSED" if name != "absolute_phase" else "PARTIAL",
            "zero_filled": False,
            "assessment": (
                "frozen convention applied"
                if name != "absolute_phase"
                else "absolute phase remains outside the accepted claim"
            ),
        }
        for name in (
            "master_normalization",
            "fourier_and_tortoise_phase",
            "incident_partial_wave_normalization",
            "current_orientation",
            "time_average_and_real_field_amplitude",
            "total_free_scattered_definition",
            "absolute_phase",
        )
    }
    return {"numerical": numerical, "convention": convention}


def _record(
    *,
    ordinal: int,
    v21: Mapping[str, Any],
    v22: Mapping[str, Any],
    comparison: Mapping[str, Any],
    comparison_identity: Mapping[str, Any],
    external_node: Mapping[str, Any],
    external_node_identity: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> Mapping[str, Any]:
    radial = v21["radial_key"]
    if v22["radial_key"] != radial:
        _fail("V2.1/V2.2 radial-key mismatch")
    if (v21["m"], v21["incident_column"]) != (
        v22["m"],
        v22["incident_column"],
    ):
        _fail("V2.1/V2.2 channel ordering mismatch")
    radial_ordinal = int(radial["ordinal"])
    sector = str(radial["sector"])
    ell = int(radial["ell"])
    if comparison["ordinal"] != radial_ordinal or comparison["key"] != {
        "ell": ell,
        "kM": radial["kM"],
        "sector": sector,
    }:
        _fail("selected SchWO comparison ordering mismatch")

    omega = _mp_real(radial["omega_M_equals_kM"])
    sigma_l = math.factorial(ell + 2) // math.factorial(ell - 2)
    bridge = mp.mpc(1) if sector == "even" else 2j / omega
    if sector == "even":
        expected_bridge = _mp_complex(
            v21["martel_poisson_normalization"]["conversion_factor_from_Li"]
        )
    else:
        expected_bridge = _mp_complex(
            v21["martel_poisson_normalization"]["conversion_factor_Psi_CPM_from_Psi_RW"]
        )
    if not _close(bridge, expected_bridge):
        _fail("Li-to-MP master bridge mismatch")

    raw = v21["raw_radial_coefficients"]
    ain_raw = _mp_complex(raw["A_in_raw_derived"])
    aout_raw = _mp_complex(raw["A_out_raw"])
    t_raw = _mp_complex(raw["T_horizon_raw_derived"])
    s_l = _mp_complex(raw["S_l"])
    if not _close(ain_raw, -aout_raw / (((-1) ** ell) * s_l)):
        _fail("SchWO incoming reconstruction identity mismatch")

    c_lm = _mp_complex(v21["li_normalization"]["c_lm_p"])
    n_schwo = c_lm / ain_raw
    incoming_schwo = bridge * n_schwo * ain_raw
    outgoing_schwo = bridge * n_schwo * aout_raw
    horizon_schwo = bridge * n_schwo * t_raw
    free_schwo = bridge * (-((-1) ** ell) * c_lm)
    scatter_a = _mp_complex(v22["route_amplitudes"]["A"]["coefficient"])
    scatter_b = _mp_complex(v22["route_amplitudes"]["B"]["coefficient"])
    total_a = free_schwo + scatter_a
    total_b = free_schwo + scatter_b
    if not (_close(total_a, outgoing_schwo) and _close(total_b, outgoing_schwo)):
        _fail("Route A/B total-outgoing reconstruction mismatch")

    (
        ain_ext_raw,
        aout_ext_raw,
        t_ext_raw,
        s_ext,
        matching_incidence,
        matching_reflection,
        selected_index,
    ) = _selected_external_coefficients(
        external_node,
        expected_ordinal=radial_ordinal,
        expected_sector=sector,
        expected_ell=ell,
    )
    phase_identity_residual = abs(s_ext + aout_ext_raw / (((-1) ** ell) * ain_ext_raw))
    if phase_identity_residual > mp.mpf("1e-38") * max(abs(s_ext), mp.mpf(1)):
        _fail("external phase-factor reconstruction identity mismatch")
    n_external = c_lm / ain_ext_raw
    incoming_external = bridge * n_external * ain_ext_raw
    outgoing_external = bridge * n_external * aout_ext_raw
    horizon_external = bridge * n_external * t_ext_raw
    if not _close(incoming_schwo, incoming_external):
        _fail("SchWO/external incident normalization mismatch")

    schwo_in = _boundary_evidence(
        incoming_schwo, omega=omega, sigma_l=sigma_l, orientation=-1
    )
    schwo_out = _boundary_evidence(
        outgoing_schwo, omega=omega, sigma_l=sigma_l, orientation=1
    )
    schwo_h = _boundary_evidence(
        horizon_schwo, omega=omega, sigma_l=sigma_l, orientation=-1
    )
    route_a_out = _boundary_evidence(
        total_a, omega=omega, sigma_l=sigma_l, orientation=1
    )
    route_b_out = _boundary_evidence(
        total_b, omega=omega, sigma_l=sigma_l, orientation=1
    )
    external_in = _boundary_evidence(
        incoming_external, omega=omega, sigma_l=sigma_l, orientation=-1
    )
    external_out = _boundary_evidence(
        outgoing_external, omega=omega, sigma_l=sigma_l, orientation=1
    )
    external_h = _boundary_evidence(
        horizon_external, omega=omega, sigma_l=sigma_l, orientation=-1
    )

    def flux(evidence: Mapping[str, Any]) -> mp.mpf:
        return _mp_real(evidence["flux_from_amplitude"])

    fin = flux(schwo_in)
    fout = flux(schwo_out)
    fh = flux(schwo_h)
    efin = flux(external_in)
    efout = flux(external_out)
    efh = flux(external_h)
    route_a_flux = flux(route_a_out)
    route_b_flux = flux(route_b_out)

    waveform_current_values = {
        "schwo_infinity_incoming": _mp_real(
            schwo_in["waveform_current_relative_residual"]
        ),
        "schwo_infinity_total_outgoing": _mp_real(
            schwo_out["waveform_current_relative_residual"]
        ),
        "schwo_horizon": _mp_real(schwo_h["waveform_current_relative_residual"]),
        "external_infinity_incoming": _mp_real(
            external_in["waveform_current_relative_residual"]
        ),
        "external_infinity_total_outgoing": _mp_real(
            external_out["waveform_current_relative_residual"]
        ),
        "external_horizon": _mp_real(external_h["waveform_current_relative_residual"]),
    }
    comparators: dict[str, Any] = {
        "schwo_balance": _threshold_result(
            value=normalized_balance_residual(fin, fout, fh),
            contract=contract,
            field="schwo_normalized_balance_residual_max",
            predicate="less_than_or_equal",
        ),
        "external_balance": _threshold_result(
            value=normalized_balance_residual(efin, efout, efh),
            contract=contract,
            field="external_normalized_balance_residual_max",
            predicate="less_than_or_equal",
        ),
        "waveform_current": {
            name: _threshold_result(
                value=value,
                contract=contract,
                field="waveform_vs_current_relative_flux_residual_max",
                predicate="less_than_or_equal",
            )
            for name, value in waveform_current_values.items()
        },
        "route_A_B_total_outgoing_flux": _threshold_result(
            value=abs(route_a_flux - route_b_flux) / fin,
            contract=contract,
            field="route_A_B_total_outgoing_flux_fraction_difference_max",
            predicate="strict_less_than",
        ),
        "schwo_external_total_outgoing_fraction": _threshold_result(
            value=abs(fout / fin - efout / efin),
            contract=contract,
            field="schwo_external_total_outgoing_flux_fraction_difference_max",
            predicate="strict_less_than",
        ),
        "schwo_external_horizon_fraction": _threshold_result(
            value=_symmetric_relative_difference(fh / fin, efh / efin),
            contract=contract,
            field="schwo_external_horizon_flux_symmetric_relative_difference_max",
            predicate="strict_less_than",
        ),
    }
    all_results = [
        comparators["schwo_balance"],
        comparators["external_balance"],
        comparators["route_A_B_total_outgoing_flux"],
        comparators["schwo_external_total_outgoing_fraction"],
        comparators["schwo_external_horizon_fraction"],
        *comparators["waveform_current"].values(),
    ]
    if not all(result["passed"] for result in all_results):
        failed = [
            (result["threshold_field"], result["value"]["value"])
            for result in all_results
            if not result["passed"]
        ]
        _fail(f"scientific V2.3 comparator failed at record {ordinal}: {failed}")

    boundary_items = (
        schwo_in,
        schwo_out,
        schwo_h,
        route_a_out,
        route_b_out,
        external_in,
        external_out,
        external_h,
    )
    finite_values = all(
        mp.isfinite(_mp_real(item[field]))
        for item in boundary_items
        for field in (
            "amplitude_squared",
            "signed_current",
            "flux_from_amplitude",
            "flux_from_current",
        )
    )
    positivity = all(flux(item) > 0 for item in boundary_items)
    current_signs = (
        _mp_real(schwo_in["signed_current"]) < 0
        and _mp_real(schwo_out["signed_current"]) > 0
        and _mp_real(schwo_h["signed_current"]) < 0
        and _mp_real(external_in["signed_current"]) < 0
        and _mp_real(external_out["signed_current"]) > 0
        and _mp_real(external_h["signed_current"]) < 0
    )
    if not (finite_values and positivity and current_signs):
        _fail(f"V2.3 exact finite/positivity/current predicate failed at {ordinal}")

    free_flux = flux(
        _boundary_evidence(free_schwo, omega=omega, sigma_l=sigma_l, orientation=1)
    )
    scatter_a_flux = flux(
        _boundary_evidence(scatter_a, omega=omega, sigma_l=sigma_l, orientation=1)
    )
    interference_a = route_a_flux - free_flux - scatter_a_flux

    return {
        "schema": SCHEMA,
        "record_ordinal": ordinal,
        "radial_key": radial,
        "m": int(v21["m"]),
        "incident_column": v21["incident_column"]["column"],
        "sector": sector,
        "ell": ell,
        "omega": _real_record(omega),
        "sigma_l": sigma_l,
        "precision": {
            "working_dps": WORKING_DPS,
            "minimum_required_dps": 80,
            "binary64_used_for_mandatory_quantities": False,
            "external_decimal_parse_context": "mp.workdps(100)",
            "ambient_precision_restored_by_context_manager": True,
        },
        "normalization": {
            "real_field_peak_time_average_factor": "1/2",
            "flux_formula": "sigma_l*omega^2*abs(Psi_MP)^2/(128*pi)",
            "signed_current_formula": "J=orientation*omega*abs(Psi_MP)^2",
            "li_to_mp_bridge": _complex_record(bridge),
            "li_to_mp_bridge_identity": "1 (even); 2i/omega (odd)",
            "N_schwo": _complex_record(n_schwo),
            "N_external": _complex_record(n_external),
            "incident_coefficient_li": _complex_record(c_lm),
            "incident_normalization_shared": True,
        },
        "raw_coefficients": {
            "schwo": {
                "A_in": _complex_record(ain_raw),
                "A_out_total": _complex_record(aout_raw),
                "T_horizon": _complex_record(t_raw),
                "S_l": _complex_record(s_l),
                "incoming_identity_verified": True,
            },
            "external_direct": {
                "A_in": _complex_record(ain_ext_raw),
                "A_out_total": _complex_record(aout_ext_raw),
                "T_horizon": _complex_record(t_ext_raw),
                "S_l": _complex_record(s_ext),
                "matching_basis_incidence_source": _complex_record(matching_incidence),
                "matching_basis_reflection_source": _complex_record(
                    matching_reflection
                ),
                "normalized_raw_definition": (
                    "A_in=1; A_out=reflection_ratio; T_horizon=transmission"
                ),
                "selected_match_index": selected_index,
                "phase_factor_identity_verified": True,
                "phase_factor_identity_complex_residual_abs": _real_record(
                    phase_identity_residual
                ),
                "potential": external_node["potential"],
                "parity_derived_even": external_node.get("parity_derived_even_used"),
            },
        },
        "physical_mp_coefficients": {
            "schwo": {
                "infinity_incoming": _complex_record(incoming_schwo),
                "infinity_total_outgoing": _complex_record(outgoing_schwo),
                "horizon_ingoing": _complex_record(horizon_schwo),
                "infinity_free": _complex_record(free_schwo),
                "infinity_scattered_route_A": _complex_record(scatter_a),
                "infinity_scattered_route_B": _complex_record(scatter_b),
                "infinity_total_route_A": _complex_record(total_a),
                "infinity_total_route_B": _complex_record(total_b),
                "total_route_A_identity_verified": True,
                "total_route_B_identity_verified": True,
            },
            "external_direct": {
                "infinity_incoming": _complex_record(incoming_external),
                "infinity_total_outgoing": _complex_record(outgoing_external),
                "horizon_ingoing": _complex_record(horizon_external),
            },
        },
        "boundary_evidence": {
            "schwo": {
                "infinity_incoming": schwo_in,
                "infinity_total_outgoing": schwo_out,
                "horizon_ingoing": schwo_h,
                "route_A_total_outgoing": route_a_out,
                "route_B_total_outgoing": route_b_out,
            },
            "external_direct": {
                "infinity_incoming": external_in,
                "infinity_total_outgoing": external_out,
                "horizon_ingoing": external_h,
            },
        },
        "flux_fractions": {
            "schwo": {
                "total_outgoing_over_incoming": _real_record(fout / fin),
                "horizon_over_incoming": _real_record(fh / fin),
                "route_A_total_outgoing_over_incoming": _real_record(
                    route_a_flux / fin
                ),
                "route_B_total_outgoing_over_incoming": _real_record(
                    route_b_flux / fin
                ),
            },
            "external_direct": {
                "total_outgoing_over_incoming": _real_record(efout / efin),
                "horizon_over_incoming": _real_record(efh / efin),
            },
        },
        "comparators": comparators,
        "mandatory_predicates_passed": True,
        "exact_predicates": {
            "record_inventory_member": True,
            "finite_values": finite_values,
            "positivity": positivity,
            "current_signs": current_signs,
            "normalization_factors": True,
            "route_A_B_identity": True,
            "total_outgoing_balance_used": True,
            "radial_solve_count": 0,
            "no_dropped_tiny_horizon_modes": True,
            "no_fit_or_retuned_factor": True,
        },
        "radial_solve_count": 0,
        "diagnostics": {
            "free_flux_square": _real_record(free_flux),
            "scattered_route_A_flux_square": _real_record(scatter_a_flux),
            "free_scattered_interference_route_A": _real_record(interference_a),
            "squares_are_nonadditive_diagnostics": True,
            "used_in_balance": False,
            "scattered_only_balance_forbidden": True,
            "signal_floor_applied": False,
        },
        "uncertainty_budgets": _uncertainty_budgets(),
        "source_provenance": {
            "v2_1_record_source": str(V21_ROOT / "records.jsonl"),
            "v2_2_record_source": str(V22_ROOT / "records.jsonl"),
            "selected_comparison_source": comparison_identity,
            "external_node_source": external_node_identity,
            "external_original_wp60_strings_parsed_directly": True,
            "radial_solver_called": False,
        },
        "claims": {
            "selected_domain_flux_closure": "PASS",
            "absolute_phase": "PARTIAL",
            "full_domain": "NOT_ASSESSED",
            "full_domain_v2": "NOT_ASSESSED",
            "angles_or_angular_sum": "NOT_ASSESSED",
            "finite_radius_observer": "NOT_ASSESSED",
            "li_figures": "NOT_ASSESSED",
        },
    }


def validate_record_inventory(records: Sequence[Mapping[str, Any]]) -> None:
    """Validate the exact mandatory 120-record structural inventory."""

    if len(records) != 120:
        _fail("V2.3 inventory must contain exactly 120 records")
    expected_ordinal = 0
    radial_channels: dict[int, list[tuple[str, int]]] = {}
    for record in records:
        if record["record_ordinal"] != expected_ordinal:
            _fail("V2.3 record ordering mismatch")
        expected_ordinal += 1
        radial_channels.setdefault(record["radial_key"]["ordinal"], []).append(
            (record["incident_column"], record["m"])
        )
        if not record["mandatory_predicates_passed"]:
            _fail("V2.3 record has a failed mandatory predicate")
        if record["diagnostics"]["signal_floor_applied"]:
            _fail("V2.3 signal-floor use is forbidden")
        if record["diagnostics"]["used_in_balance"]:
            _fail("V2.3 scattered/free diagnostic was used in balance")
    expected_channels = [
        ("plus", -2),
        ("plus", 2),
        ("cross", -2),
        ("cross", 2),
    ]
    if tuple(radial_channels) != tuple(range(30)):
        _fail("V2.3 radial-key inventory mismatch")
    for ordinal, channels in radial_channels.items():
        if channels != expected_channels:
            _fail(f"V2.3 channel inventory mismatch at radial key {ordinal}")


def build_v2_3_flux_closure_records(
    project_root: Path,
    *,
    require_dispatch_review_identity: bool = True,
) -> tuple[tuple[Mapping[str, Any], ...], FrozenGate]:
    """Reconstruct all mandatory records with ambient precision restoration."""

    gate = verify_frozen_v2_3_inputs(
        project_root,
        require_dispatch_review_identity=require_dispatch_review_identity,
    )
    records: list[Mapping[str, Any]] = []
    with mp.workdps(WORKING_DPS):
        for ordinal, (v21, v22) in enumerate(
            zip(gate.v21_records, gate.v22_records, strict=True)
        ):
            radial_ordinal = int(v21["radial_key"]["ordinal"])
            records.append(
                _record(
                    ordinal=ordinal,
                    v21=v21,
                    v22=v22,
                    comparison=gate.comparisons[radial_ordinal],
                    comparison_identity=gate.comparison_identities[radial_ordinal],
                    external_node=gate.external_nodes[radial_ordinal],
                    external_node_identity=gate.external_node_identities[
                        radial_ordinal
                    ],
                    contract=gate.contract,
                )
            )
    validate_record_inventory(records)
    return tuple(records), gate


def _extrema(
    records: Sequence[Mapping[str, Any]], path: Sequence[str]
) -> Mapping[str, Any]:
    with mp.workdps(WORKING_DPS):
        values: list[tuple[mp.mpf, int]] = []
        for record in records:
            item: Any = record
            for key in path:
                item = item[key]
            values.append((_mp_real(item), int(record["record_ordinal"])))
        minimum = min(values, key=lambda pair: pair[0])
        maximum = max(values, key=lambda pair: pair[0])
        return {
            "minimum": _real_record(minimum[0]),
            "minimum_record_ordinal": minimum[1],
            "maximum": _real_record(maximum[0]),
            "maximum_record_ordinal": maximum[1],
        }


def _summary(
    records: Sequence[Mapping[str, Any]], gate: FrozenGate
) -> Mapping[str, Any]:
    with mp.workdps(WORKING_DPS):
        return {
            "schema": SCHEMA,
            "terminal_decision": TERMINAL_DECISION,
            "claim_status": "PARTIAL",
            "selected_domain_flux_closure": "PASS",
            "record_count": 120,
            "radial_key_count": 30,
            "m_values": [-2, 2],
            "incident_columns": ["plus", "cross"],
            "mandatory_record_policy": "120/120; no omission; no signal floor",
            "working_dps": WORKING_DPS,
            "radial_solve_count": 0,
            "global_status": None,
            "global_green_permitted": False,
            "absolute_phase": "PARTIAL",
            "full_domain": "NOT_ASSESSED",
            "full_domain_v2": "NOT_ASSESSED",
            "angles_or_angular_sum": "NOT_ASSESSED",
            "finite_radius_observer": "NOT_ASSESSED",
            "li_figures": "NOT_ASSESSED",
            "minimum_horizon_flux_fraction": _extrema(
                records,
                ("flux_fractions", "external_direct", "horizon_over_incoming"),
            )["minimum"],
            "schwo_balance_residual_extrema": _extrema(
                records, ("comparators", "schwo_balance", "value")
            ),
            "external_balance_residual_extrema": _extrema(
                records, ("comparators", "external_balance", "value")
            ),
            "accepted_preexecution_review": {
                "advance_decision": "ADVANCE",
                "claim_status": "PASS",
                "gate_label": REQUIRED_T7_GATE,
                "t7_handoff_identity_at_build": gate.t7_identity,
            },
            "accepted_v2_2_review": {
                "advance_decision": "ADVANCE",
                "claim_status": "PARTIAL",
                "gate_label": REQUIRED_V22_GATE,
            },
            "threshold_contract_identity": gate.identities[0],
        }


def _validate_summary_extrema(
    records: Sequence[Mapping[str, Any]], summary: Mapping[str, Any]
) -> None:
    """Require exact 100-dps summary extrema reconstructed from record strings."""

    with mp.workdps(WORKING_DPS):
        expected_horizon = _extrema(
            records,
            ("flux_fractions", "external_direct", "horizon_over_incoming"),
        )["minimum"]
        expected_schwo = _extrema(records, ("comparators", "schwo_balance", "value"))
        expected_external = _extrema(
            records, ("comparators", "external_balance", "value")
        )
    if summary.get("minimum_horizon_flux_fraction") != expected_horizon:
        _fail("V2.3 minimum horizon summary precision mismatch")
    if summary.get("schwo_balance_residual_extrema") != expected_schwo:
        _fail("V2.3 SchWO balance summary precision mismatch")
    if summary.get("external_balance_residual_extrema") != expected_external:
        _fail("V2.3 external balance summary precision mismatch")


def _source_ledger(project_root: Path, gate: FrozenGate) -> Mapping[str, Any]:
    implementation_paths = (
        project_root / "src/schwgw/validation/phase6_v2_flux_closure.py",
        project_root / "scripts/phase6_v2_3_publish_flux_closure.py",
        project_root / "tests/unit/test_phase6_v2_3_flux_closure.py",
        project_root / "tests/regression/test_phase6_v2_3_flux_publication.py",
    )
    return {
        "schema": SCHEMA,
        "frozen_input_identities": list(gate.identities),
        "contract_source_identities": gate.contract["source_identities"],
        "external_node_identities": list(gate.external_node_identities),
        "t7_handoff_identity_at_build": gate.t7_identity,
        "implementation_identities": [
            file_identity(path) for path in implementation_paths
        ],
        "source_policy": {
            "radial_solver_called": False,
            "frozen_sources_only": True,
            "external_original_wp60_decimal_strings": True,
            "angular_sum_performed": False,
            "observation_angle_used": False,
            "li_figures_run": False,
        },
    }


def _report(
    records: Sequence[Mapping[str, Any]],
    gate: FrozenGate,
    summary: Mapping[str, Any],
    verification: Mapping[str, Any],
) -> Mapping[str, Any]:
    return {
        "schema": SCHEMA,
        "terminal_decision": TERMINAL_DECISION,
        "scientific_scope": (
            "Selected-domain future-null-infinity total-outgoing and horizon "
            "MP-master flux closure for exactly 120 frozen channels."
        ),
        "formulae": {
            "signed_currents": {
                "incoming": "J_in=-omega*abs(A_in_MP)^2",
                "outgoing": "J_out=+omega*abs(A_out_total_MP)^2",
                "horizon": "J_h=-omega*abs(T_horizon_MP)^2",
            },
            "flux": "F=sigma_l*omega*abs(J)/(128*pi)",
            "equivalent_flux": "F=sigma_l*omega^2*abs(Psi_MP)^2/(128*pi)",
            "sigma_l": "(ell+2)!/(ell-2)!",
            "total_outgoing": "A_free+A_scattered",
            "real_field_peak_time_average_factor": "1/2",
        },
        "summary": summary,
        "thresholds": gate.contract["frozen_thresholds"],
        "acceptance_logic": gate.contract["acceptance_logic"],
        "verification": verification,
        "nonclaims": {
            "full_domain": "NOT_ASSESSED",
            "full_domain_v2": "NOT_ASSESSED",
            "absolute_phase": "PARTIAL",
            "angles_or_angular_sum": "NOT_ASSESSED",
            "finite_radius_observer": "NOT_ASSESSED",
            "li_figures": "NOT_ASSESSED",
            "global_status": None,
            "global_green_permitted": False,
        },
        "record_count": len(records),
    }


def _write_exclusive(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


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


def _seal(root: Path) -> None:
    for path in root.iterdir():
        if path.is_file():
            path.chmod(0o444)
    root.chmod(0o555)


def _manifest(root: Path, files: Sequence[str]) -> Mapping[str, Any]:
    return {
        "schema": SCHEMA,
        "root_name": root.name,
        "artifacts": [
            {
                "path": name,
                "sha256": sha256_file(root / name),
                "bytes": (root / name).stat().st_size,
            }
            for name in files
        ],
    }


def publish_v2_3_flux_closure(
    project_root: Path,
    output_root: Path,
    *,
    verification: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Publish exactly once and independently reload the immutable root."""

    project_root = project_root.resolve()
    output_root = output_root.resolve()
    expected_parent = (project_root / "runs/phase6/asymptotic_waveform").resolve()
    if output_root.parent != expected_parent:
        _fail("V2.3 output root is outside the authorized parent")
    if not output_root.name.startswith(
        "v2_3_flux_closure_v2_"
    ) or not output_root.name.endswith("_py314"):
        _fail("V2.3 output-root name mismatch")
    if output_root.exists():
        _fail("V2.3 output-root collision")

    records, start_gate = build_v2_3_flux_closure_records(project_root)
    summary = _summary(records, start_gate)
    ledger = _source_ledger(project_root, start_gate)
    report = _report(records, start_gate, summary, verification)

    output_root.mkdir(mode=0o700)
    try:
        with _exclusive_writer(output_root):
            records_bytes = b"".join(canonical_json_bytes(record) for record in records)
            predecessor_records = (
                project_root / V23_PREDECESSOR_ROOT / "records.jsonl"
            ).read_bytes()
            if records_bytes != predecessor_records:
                _fail("V2.3 repair changed predecessor scientific records bytes")
            _write_exclusive(output_root / "records.jsonl", records_bytes)
            _write_exclusive(
                output_root / "summary.json", canonical_json_bytes(summary)
            )
            _write_exclusive(output_root / "report.json", canonical_json_bytes(report))
            _write_exclusive(
                output_root / "source_ledger.json", canonical_json_bytes(ledger)
            )
            end_gate = verify_frozen_v2_3_inputs(project_root)
            if (
                end_gate.identities != start_gate.identities
                or end_gate.t7_identity != start_gate.t7_identity
            ):
                _fail("frozen input identity changed between V2.3 start and end")
            manifest = _manifest(
                output_root,
                (
                    "records.jsonl",
                    "summary.json",
                    "report.json",
                    "source_ledger.json",
                ),
            )
            _write_exclusive(
                output_root / "manifest.json", canonical_json_bytes(manifest)
            )
        dir_fd = os.open(output_root, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
        _seal(output_root)
    except BaseException:
        # Publication failures are intentionally left visible for forensic review;
        # successful publication is guaranteed fresh and immutable.
        raise
    return validate_published_v2_3_flux_closure(output_root, project_root)


def validate_published_v2_3_flux_closure(
    output_root: Path,
    project_root: Path,
) -> Mapping[str, Any]:
    """Strictly reload and reconstruct a sealed V2.3 publication."""

    output_root = output_root.resolve()
    project_root = project_root.resolve()
    _assert_immutable_root(output_root, 5)
    manifest = _validate_manifest(output_root)
    expected_names = {
        "records.jsonl",
        "summary.json",
        "report.json",
        "source_ledger.json",
    }
    if {item["path"] for item in manifest["artifacts"]} != expected_names:
        _fail("V2.3 manifest inventory mismatch")
    published_records = _read_jsonl(output_root / "records.jsonl")
    validate_record_inventory(published_records)
    rebuilt_records, gate = build_v2_3_flux_closure_records(
        project_root, require_dispatch_review_identity=False
    )
    if published_records != rebuilt_records:
        _fail("V2.3 immutable-source reconstruction mismatch")
    if (output_root / "records.jsonl").read_bytes() != (
        project_root / V23_PREDECESSOR_ROOT / "records.jsonl"
    ).read_bytes():
        _fail("V2.3 repair records differ from immutable predecessor")
    summary = _read_json(output_root / "summary.json")
    report = _read_json(output_root / "report.json")
    ledger = _read_json(output_root / "source_ledger.json")
    if summary["record_count"] != 120 or summary["radial_solve_count"] != 0:
        _fail("V2.3 summary invariant mismatch")
    if summary["global_status"] is not None or summary["global_green_permitted"]:
        _fail("V2.3 global claim ceiling mismatch")
    if summary["terminal_decision"] != TERMINAL_DECISION:
        _fail("V2.3 terminal decision mismatch")
    _validate_summary_extrema(published_records, summary)
    if report["record_count"] != 120:
        _fail("V2.3 report record-count mismatch")
    if report.get("summary") != summary:
        _fail("V2.3 report/summary control-plane mismatch")
    if ledger["source_policy"]["radial_solver_called"]:
        _fail("V2.3 source ledger reports a radial solve")
    recorded_t7 = ledger["t7_handoff_identity_at_build"]
    if recorded_t7["sha256"] != DISPATCH_T7_SHA256:
        _fail("V2.3 build-time T7 identity mismatch")
    if gate.contract["schema"] != "schwgw_phase6_v2_3_flux_threshold_contract_v1":
        _fail("V2.3 threshold-contract schema mismatch")
    return {
        "manifest": manifest,
        "records": published_records,
        "summary": summary,
        "report": report,
        "source_ledger": ledger,
    }


def fresh_output_root(project_root: Path, timestamp: str | None = None) -> Path:
    """Return the authorized timestamped output path without creating it."""

    if timestamp is None:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    return (
        project_root
        / "runs/phase6/asymptotic_waveform"
        / f"v2_3_flux_closure_v2_{timestamp}_py314"
    )


def validate_in_temporary_copy(output_root: Path, project_root: Path) -> None:
    """Exercise independent reload from a distinct filesystem location."""

    with tempfile.TemporaryDirectory() as temporary:
        target = Path(temporary) / output_root.name
        target.mkdir(mode=0o700)
        for source in output_root.iterdir():
            target.joinpath(source.name).write_bytes(source.read_bytes())
            target.joinpath(source.name).chmod(0o444)
        target.chmod(0o555)
        validate_published_v2_3_flux_closure(target, project_root)
