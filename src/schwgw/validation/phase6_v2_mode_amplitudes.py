"""Build, publish, and independently reload frozen Phase-6 V2.1 amplitudes."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat

import mpmath as mp

from schwgw.scattering.gauge_invariant_asymptotics import (
    IncidentColumn,
    ModeAmplitudes,
    RawRadialAmplitudes,
    build_mode_amplitudes,
    reconstruct_raw_amplitudes,
)


RECORD_SCHEMA = "schwgw_phase6_v2_1_mode_amplitude_record_v1"
REPORT_SCHEMA = "schwgw_phase6_v2_1_mode_amplitudes_report_v1"
SUMMARY_SCHEMA = "schwgw_phase6_v2_1_mode_amplitudes_summary_v1"
LEDGER_SCHEMA = "schwgw_phase6_v2_1_mode_amplitudes_source_ledger_v1"
MANIFEST_SCHEMA = "schwgw_phase6_v2_1_mode_amplitudes_manifest_v1"
TERMINAL_DECISION = "CHECKPOINT / V2.1 MODE-LEVEL ASYMPTOTIC AMPLITUDES FROZEN"
PREDECESSOR_DECISION = (
    "ACCEPT GREEN / V2.0 CONVENTION CONTRACT READY FOR BOUNDED V2.1 IMPLEMENTATION"
)
WORKING_DPS = 80

RELATIVE_CONTRACT = Path("configs/phase6_v2_0_convention_contract_20260810.json")
RELATIVE_DOMAIN = Path("configs/phase6_v2_0_selected_domain_20260810.json")
RELATIVE_PROMPT = Path("docs/prompts/phase6_t6_v2_1_mode_amplitudes.md")
RELATIVE_MATERIAL_REVIEW = Path("docs/phase6_v2_0_material_reviews_20260810.md")
RELATIVE_SOURCE_ROOT = Path(
    "runs/phase6/radial_validation/v1_radial_selected_acceptance_v1_20260810_py314"
)

FROZEN_INPUT_SHA256 = {
    str(RELATIVE_CONTRACT): (
        "1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517"
    ),
    str(RELATIVE_DOMAIN): (
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
}
FROZEN_INPUT_MODES = {
    str(RELATIVE_CONTRACT): 0o644,
    str(RELATIVE_DOMAIN): 0o644,
    "runs/phase6/radial_validation/"
    "v1_final_radial_baseline_v2_20260810_py314/plan.json": 0o444,
    "src/schwgw/numerics/radial_solver.py": 0o644,
    "src/schwgw/numerics/conditioned_radial.py": 0o644,
    "src/schwgw/numerics/scaled_tortoise_radial.py": 0o644,
    "src/schwgw/numerics/adaptive_jost_radial.py": 0o644,
    "src/schwgw/numerics/matching.py": 0o644,
    "src/schwgw/numerics/physical_boundary_radial.py": 0o644,
    "src/schwgw/numerics/boundary_conditions.py": 0o644,
}
PROMPT_SHA256 = "d5795b7888fee147eefa408cfdbfaef1771bd5d59a7ca0e3bac9aebce2754f55"

NUMERICAL_COMPONENTS = (
    "radial_source",
    "arithmetic_precision",
    "inner_boundary",
    "outer_boundary_and_jost_order",
    "asymptotic_extraction",
    "angular_truncation",
    "route_comparison",
    "flux_balance",
)
CONVENTION_COMPONENTS = (
    "master_normalization",
    "fourier_and_tortoise_phase",
    "incident_partial_wave_normalization",
    "spin_harmonic_and_polarization_basis",
    "null_tetrad_and_psi4",
    "boundary_and_amplitude_average",
)


class Phase6V21Error(ValueError):
    """Fail-closed error for V2.1 identity, evidence, or publication drift."""


@dataclass(frozen=True)
class V21RecordBundle:
    """In-memory evidence bundle produced without any radial solve."""

    records: tuple[dict[str, object], ...]
    source_ledger: dict[str, object]
    frozen_input_hashes: dict[str, str]


def canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_identity(path: Path) -> dict[str, object]:
    absolute = path.absolute()
    info = absolute.lstat()
    if absolute.is_symlink() or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise Phase6V21Error(
            f"file identity is not a direct single-link file: {absolute}"
        )
    return {
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
        "path": str(absolute),
        "sha256": sha256_file(absolute),
        "size": info.st_size,
    }


def _load_json(path: Path) -> Mapping[str, object]:
    try:
        payload = json.loads(path.read_bytes())
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        raise Phase6V21Error(f"cannot load JSON: {path}") from exc
    if not isinstance(payload, Mapping):
        raise Phase6V21Error(f"JSON root is not an object: {path}")
    return payload


def _direct_immutable_root(path: Path) -> Path:
    absolute = path.absolute()
    if absolute.is_symlink() or absolute.resolve(strict=True) != absolute:
        raise Phase6V21Error(f"immutable root is aliased: {absolute}")
    info = absolute.lstat()
    if not stat.S_ISDIR(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o555:
        raise Phase6V21Error(f"immutable root mode changed: {absolute}")
    return absolute


def _verify_authoritative_v1_roots(contract: Mapping[str, object]) -> dict[str, object]:
    roots = contract.get("authoritative_v1_identities")
    if not isinstance(roots, Mapping):
        raise Phase6V21Error("authoritative V1 identity map is missing")
    verified: dict[str, object] = {}
    filenames = {
        "summary_sha256": "summary.json",
        "report_sha256": "report.json",
        "manifest_sha256": "manifest.json",
        "records_sha256": "records.jsonl",
        "source_ledger_sha256": "source_ledger.json",
    }
    for label, raw_entry in roots.items():
        if not isinstance(label, str) or not isinstance(raw_entry, Mapping):
            raise Phase6V21Error("authoritative V1 identity entry changed")
        entry = dict(raw_entry)
        checked: dict[str, object] = {}
        if "path" in entry:
            path = Path(str(entry["path"]))
            expected = entry.get("sha256")
            if not isinstance(expected, str) or sha256_file(path) != expected:
                raise Phase6V21Error(f"authoritative V1 file hash changed: {label}")
            identity = file_identity(path)
            if identity["mode"] != 0o444:
                raise Phase6V21Error(f"authoritative V1 file mode changed: {label}")
            if "/runs/" in str(path):
                _direct_immutable_root(path.parent)
            checked["file"] = identity
        elif "root" in entry:
            root = _direct_immutable_root(Path(str(entry["root"])))
            checked["root"] = str(root)
            checked["root_mode"] = stat.S_IMODE(root.lstat().st_mode)
            for hash_field, filename in filenames.items():
                expected = entry.get(hash_field)
                if expected is None:
                    continue
                path = root / filename
                if not isinstance(expected, str) or sha256_file(path) != expected:
                    raise Phase6V21Error(
                        f"authoritative V1 root file hash changed: {label}/{filename}"
                    )
                checked[filename] = file_identity(path)
        else:
            raise Phase6V21Error(f"authoritative V1 entry lacks path/root: {label}")
        verified[label] = checked
    return verified


def verify_frozen_v2_1_inputs(project_root: str | Path) -> dict[str, object]:
    """Rehash all explicit V2.1 frozen inputs and every V1 contract root."""

    root = Path(project_root).absolute()
    if root.is_symlink() or root.resolve(strict=True) != root:
        raise Phase6V21Error("project root is aliased")
    hashes: dict[str, str] = {}
    for relative, expected in FROZEN_INPUT_SHA256.items():
        path = root / relative
        identity = file_identity(path)
        actual = sha256_file(path)
        if actual != expected:
            raise Phase6V21Error(f"frozen input identity mismatch: {relative}")
        if identity["mode"] != FROZEN_INPUT_MODES[relative]:
            raise Phase6V21Error(f"frozen input permission mismatch: {relative}")
        hashes[relative] = actual
    prompt = root / RELATIVE_PROMPT
    prompt_identity = file_identity(prompt)
    if sha256_file(prompt) != PROMPT_SHA256 or prompt_identity["mode"] != 0o444:
        raise Phase6V21Error("frozen V2.1 prompt identity mismatch")
    hashes[str(RELATIVE_PROMPT)] = PROMPT_SHA256
    contract = _load_json(root / RELATIVE_CONTRACT)
    if contract.get("schema") != "schwgw_phase6_v2_0_convention_contract_v1":
        raise Phase6V21Error("V2.0 convention contract schema changed")
    review_text = (root / RELATIVE_MATERIAL_REVIEW).read_text(encoding="utf-8")
    decision_lines = [line.strip() for line in review_text.splitlines()]
    if decision_lines.count(PREDECESSOR_DECISION) != 1:
        raise Phase6V21Error("predecessor decision changed")
    domain = _load_json(root / RELATIVE_DOMAIN)
    if domain.get("schema") != "schwgw_phase6_v2_0_selected_domain_v1":
        raise Phase6V21Error("V2.0 selected-domain schema changed")
    budget = contract.get("uncertainty_budget_contract")
    if (
        not isinstance(budget, Mapping)
        or budget.get("numerical_components") != list(NUMERICAL_COMPONENTS)
        or budget.get("convention_components") != list(CONVENTION_COMPONENTS)
    ):
        raise Phase6V21Error("V2.0 uncertainty component vocabulary changed")
    return {
        "authoritative_v1_roots": _verify_authoritative_v1_roots(contract),
        "contract": contract,
        "domain": domain,
        "hashes": hashes,
    }


def _mp_number(value: object, *, label: str) -> mp.mpf:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise Phase6V21Error(f"invalid numeric source field: {label}")
    result = mp.mpf(str(value))
    if not mp.isfinite(result):
        raise Phase6V21Error(f"nonfinite numeric source field: {label}")
    return result


def _mp_complex(value: object, *, label: str) -> mp.mpc:
    if not isinstance(value, Mapping) or "real" not in value or "imag" not in value:
        raise Phase6V21Error(f"invalid complex source field: {label}")
    return mp.mpc(
        _mp_number(value["real"], label=f"{label}.real"),
        _mp_number(value["imag"], label=f"{label}.imag"),
    )


def _decimal_text(value: mp.mpf) -> str:
    if not mp.isfinite(value):
        raise Phase6V21Error("nonfinite arbitrary-precision output")
    return mp.nstr(value, n=WORKING_DPS, strip_zeros=False)


def complex_record(value: mp.mpc) -> dict[str, object]:
    magnitude = abs(value)
    return {
        "abs": _decimal_text(magnitude),
        "imag": _decimal_text(mp.im(value)),
        "phase_rad": None if magnitude == 0 else _decimal_text(mp.arg(value)),
        "precision_dps": WORKING_DPS,
        "real": _decimal_text(mp.re(value)),
    }


def _numerical_budget(source: Mapping[str, object]) -> dict[str, object]:
    baseline = source["nodes"]["baseline"]  # type: ignore[index]
    return {
        "radial_source": {
            "state": "PASS",
            "evidence": "frozen selected SchWO comparison record overall_state=PASS",
        },
        "arithmetic_precision": {
            "state": "PASS",
            "evidence": f"mode formulas evaluated with mpmath at {WORKING_DPS} dps",
        },
        "inner_boundary": {
            "state": "PASS",
            "evidence": {
                "r_in_eps": baseline["configuration"]["r_in_eps"],  # type: ignore[index]
                "source_check": source["checks"]["r_in_complex_S"],  # type: ignore[index]
            },
        },
        "outer_boundary_and_jost_order": {
            "state": "PASS",
            "evidence": {
                "jost_order": baseline["configuration"]["jost_order"],  # type: ignore[index]
                "selected_r_out_M": baseline["diagnostics"]["selected_r_out_M"],  # type: ignore[index]
                "jost_check": source["checks"]["jost_order_complex_S"],  # type: ignore[index]
                "r_out_check": source["checks"]["r_out_complex_S"],  # type: ignore[index]
            },
        },
        "asymptotic_extraction": {
            "state": "NOT_ASSESSED",
            "qualification": "V2.1 stores mode coefficients only; no waveform extraction",
        },
        "angular_truncation": {
            "state": "NOT_ASSESSED",
            "qualification": "no angle and no angular or m sum",
        },
        "route_comparison": {
            "state": "PARTIAL",
            "qualification": "only route A mode-amplitude construction is present",
        },
        "flux_balance": {
            "state": "NOT_ASSESSED",
            "qualification": "physical flux is outside bounded V2.1",
        },
    }


def _convention_budget() -> dict[str, object]:
    return {
        "master_normalization": {
            "state": "PASS",
            "evidence": "frozen Li-to-Martel--Poisson V2.0 bridge",
        },
        "fourier_and_tortoise_phase": {
            "state": "PASS",
            "evidence": "exp(-i omega t), C_r_star=0 frozen by V2.0",
        },
        "incident_partial_wave_normalization": {
            "state": "PASS",
            "evidence": "two frozen unit columns and c_lm^p formulas applied without fit",
        },
        "spin_harmonic_and_polarization_basis": {
            "state": "NOT_ASSESSED",
            "qualification": "no angle or spin-harmonic evaluation",
        },
        "null_tetrad_and_psi4": {
            "state": "NOT_ASSESSED",
            "qualification": "no curvature or Psi4 route",
        },
        "boundary_and_amplitude_average": {
            "state": "PARTIAL",
            "qualification": "boundary coefficient convention fixed; no averaged flux",
        },
    }


def _mp_amplitudes(mode: ModeAmplitudes) -> dict[str, object]:
    return {
        "A_in_physical": complex_record(mode.mp_factor * mode.A_in_physical),
        "A_out_free_physical": complex_record(
            mode.mp_factor * mode.A_out_free_physical
        ),
        "A_out_scattered_physical": complex_record(
            mode.mp_factor * mode.A_out_scattered_physical
        ),
        "A_out_total_physical": complex_record(
            mode.mp_factor * mode.A_out_total_physical
        ),
        "T_horizon_physical": complex_record(mode.mp_factor * mode.T_horizon_physical),
    }


def _raw_amplitudes(raw: RawRadialAmplitudes, factor: mp.mpc) -> dict[str, object]:
    return {
        "A_in_raw": complex_record(factor * raw.A_in_raw),
        "A_out_raw": complex_record(factor * raw.A_out_raw),
        "S_l": complex_record(raw.S_l),
        "T_horizon_raw": complex_record(factor * raw.T_horizon_raw),
    }


def _mode_record(
    *,
    record_ordinal: int,
    radial: Mapping[str, object],
    m: int,
    column: IncidentColumn,
    source: Mapping[str, object],
    comparison_identity: Mapping[str, object],
    common_identities: Mapping[str, object],
    raw: RawRadialAmplitudes,
    mode: ModeAmplitudes,
    log_abs: mp.mpf,
    phase: mp.mpf,
) -> dict[str, object]:
    ell = int(radial["ell"])
    sector = str(radial["sector"])
    li = {
        "A_in_physical": complex_record(mode.A_in_physical),
        "A_out_free_physical": complex_record(mode.A_out_free_physical),
        "A_out_scattered_physical": complex_record(mode.A_out_scattered_physical),
        "A_out_total_physical": complex_record(mode.A_out_total_physical),
        "T_horizon_physical": complex_record(mode.T_horizon_physical),
        "c_lm_p": complex_record(mode.c_lm),
        "master": "psi_Li_even" if sector == "even" else "psi_Li_odd",
        "normalization_factor_N_lm_p": complex_record(mode.normalization_factor),
    }
    if sector == "even":
        mp_block: dict[str, object] = {
            "Psi_ZM": {
                "physical_coefficients": _mp_amplitudes(mode),
                "raw_coefficients": _raw_amplitudes(raw, mode.mp_factor),
            },
            "conversion_factor_from_Li": complex_record(mode.mp_factor),
            "identities": ["Psi_ZM=psi_Li_even"],
        }
    else:
        mp_block = {
            "Psi_RW": {
                "physical_coefficients": {
                    name: value
                    for name, value in li.items()
                    if name.startswith("A_") or name.startswith("T_")
                },
                "raw_coefficients": _raw_amplitudes(raw, mp.mpc(1)),
            },
            "Psi_CPM": {
                "physical_coefficients": _mp_amplitudes(mode),
                "raw_coefficients": _raw_amplitudes(raw, mode.mp_factor),
            },
            "conversion_factor_Psi_CPM_from_Psi_RW": complex_record(mode.mp_factor),
            "identities": [
                "SchWO/Li master=psi_Li_odd",
                "Psi_RW=psi_Li_odd",
                "Psi_RW=(1/2) partial_t Psi_CPM",
                "Psi_CPM=(2 i/omega) psi_Li_odd under exp(-i omega t)",
            ],
            "rw_is_not_cpm": True,
        }
    source_a_out = source["nodes"]["baseline"]["A_out"]  # type: ignore[index]
    source_s = source["nodes"]["baseline"]["S"]  # type: ignore[index]
    return {
        "claims": {
            "angles_assessed": False,
            "angular_or_m_sum_assessed": False,
            "finite_radius_observer_response_assessed": False,
            "full_domain_v2_assessed": False,
            "li_figures_assessed": False,
            "structural_domain_state": "PASS",
            "v1_full_domain_independent_scientific_certification": "PARTIAL",
        },
        "convention_uncertainty_budget": _convention_budget(),
        "formula_identities": {
            "A_out_free_physical": "-(-1)^ell c_lm^p",
            "A_out_scattered_physical": ("c_lm^p[A_out_raw/A_in_raw+(-1)^ell]"),
            "A_out_total_physical": "c_lm^p A_out_raw/A_in_raw",
            "N_lm_p": "c_lm^p/A_in_raw",
            "T_horizon_physical": "c_lm^p T_horizon_raw/A_in_raw",
        },
        "incident_column": {
            "A_L": complex_record(column.A_L),
            "A_R": complex_record(column.A_R),
            "A_cross": complex_record(column.A_cross),
            "A_plus": complex_record(column.A_plus),
            "column": column.name,
        },
        "li_normalization": li,
        "m": m,
        "martel_poisson_normalization": mp_block,
        "numerical_uncertainty_budget": _numerical_budget(source),
        "radial_key": {
            "ell": ell,
            "frequency_band": radial["frequency_band"],
            "kM": radial["kM"],
            "omega_M_equals_kM": radial["kM"],
            "ordinal": radial["ordinal"],
            "regime": radial["regime"],
            "sector": sector,
        },
        "raw_radial_coefficients": {
            "A_in_raw_derived": complex_record(raw.A_in_raw),
            "A_in_reconstruction": {
                "closure_residual_complex": complex_record(raw.A_in_closure_residual),
                "formula": "A_in_raw=-A_out_raw/[(-1)^ell S_l]",
                "source_A_out_raw": source_a_out,
                "source_S_l": source_s,
            },
            "A_out_raw": complex_record(raw.A_out_raw),
            "S_l": complex_record(raw.S_l),
            "T_horizon_raw_derived": complex_record(raw.T_horizon_raw),
            "T_horizon_reconstruction": {
                "formula": (
                    "T_horizon_raw=exp(log_abs_T_horizon) exp(i phase_T_horizon)"
                ),
                "source_log_abs_T_horizon": _decimal_text(log_abs),
                "source_phase_T_horizon": _decimal_text(phase),
            },
        },
        "record_ordinal": record_ordinal,
        "route": "A_project_master_to_martel_poisson_strain_flux",
        "schema": RECORD_SCHEMA,
        "sector": sector,
        "source_identities": {
            **dict(common_identities),
            "frozen_comparison_record": dict(comparison_identity),
        },
        "total_free_scattered_identity": {
            "complex_residual": complex_record(mode.identity_residual),
            "evaluation": ("independent complex evaluation of total-(free+scattered)"),
            "identity": (
                "A_out,total,physical=A_out,free,physical+A_out,scattered,physical"
            ),
            "threshold": None,
        },
    }


def _validate_domain_structure(
    domain: Mapping[str, object],
) -> tuple[Mapping[str, object], ...]:
    keys = domain.get("radial_keys")
    pairs = domain.get("parity_pair_inventory", {}).get("pairs")  # type: ignore[union-attr]
    if not isinstance(keys, list) or len(keys) != 30:
        raise Phase6V21Error("selected domain must contain 30 radial keys")
    if not isinstance(pairs, list) or len(pairs) != 15:
        raise Phase6V21Error("selected domain must contain 15 parity pairs")
    if [item.get("ordinal") for item in keys if isinstance(item, Mapping)] != list(
        range(30)
    ):
        raise Phase6V21Error("selected radial-key ordering changed")
    counts = Counter(
        (str(item.get("kM")), int(item.get("ell", -1)))
        for item in keys
        if isinstance(item, Mapping)
    )
    sectors: dict[tuple[str, int], set[str]] = {}
    for item in keys:
        if not isinstance(item, Mapping):
            raise Phase6V21Error("selected radial-key record changed")
        pair = (str(item.get("kM")), int(item.get("ell", -1)))
        sectors.setdefault(pair, set()).add(str(item.get("sector")))
    if any(count != 2 for count in counts.values()) or any(
        value != {"odd", "even"} for value in sectors.values()
    ):
        raise Phase6V21Error("selected odd/even pairing changed")
    angular = domain.get("angular_lift")
    basis = domain.get("incident_basis")
    if (
        not isinstance(angular, Mapping)
        or angular.get("m_values") != [-2, 2]
        or angular.get("mode_channel_count") != 60
        or not isinstance(basis, Mapping)
        or basis.get("per_column_mode_channel_count") != 60
        or basis.get("route_mode_column_record_count") != 120
    ):
        raise Phase6V21Error("selected mode/column cardinality changed")
    return tuple(keys)


def build_v2_1_records(project_root: str | Path) -> V21RecordBundle:
    """Load immutable V1 bytes and build exactly 120 route-A records."""

    project = Path(project_root).absolute()
    gate = verify_frozen_v2_1_inputs(project)
    domain = gate["domain"]
    if not isinstance(domain, Mapping):
        raise Phase6V21Error("selected domain is invalid")
    radial_keys = _validate_domain_structure(domain)
    source_root = _direct_immutable_root(project / RELATIVE_SOURCE_ROOT)
    manifest_path = source_root / "manifest.json"
    manifest = _load_json(manifest_path)
    if (
        manifest.get("schema")
        != "schwgw_phase6_v1_radial_selected_acceptance_manifest_v1"
        or manifest.get("overall_state") != "PASS"
    ):
        raise Phase6V21Error("selected V1 source manifest state changed")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, Mapping):
        raise Phase6V21Error("selected V1 source inventory changed")
    comparisons = sorted(source_root.glob("comparison_*.json"))
    if len(comparisons) != 30:
        raise Phase6V21Error("selected V1 comparison count changed")
    contract_identity = file_identity(project / RELATIVE_CONTRACT)
    domain_identity = file_identity(project / RELATIVE_DOMAIN)
    manifest_identity = file_identity(manifest_path)
    common_identities = {
        "convention_contract": contract_identity,
        "selected_domain": domain_identity,
        "selected_v1_manifest": manifest_identity,
    }
    columns = (
        IncidentColumn("plus", mp.mpc(1), mp.mpc(0)),
        IncidentColumn("cross", mp.mpc(0), mp.mpc(1)),
    )
    records: list[dict[str, object]] = []
    comparison_identities: dict[str, object] = {}
    with mp.workdps(WORKING_DPS):
        for radial, comparison_path in zip(radial_keys, comparisons, strict=True):
            comparison = _load_json(comparison_path)
            expected_identity = artifacts.get(comparison_path.name)
            actual_identity = file_identity(comparison_path)
            if (
                not isinstance(expected_identity, Mapping)
                or dict(expected_identity) != actual_identity
            ):
                raise Phase6V21Error(
                    f"selected comparison identity changed: {comparison_path.name}"
                )
            if (
                comparison.get("schema")
                != "schwgw_phase6_v1_radial_selected_acceptance_v1"
                or comparison.get("overall_state") != "PASS"
                or comparison.get("ordinal") != radial.get("ordinal")
                or comparison.get("key")
                != {
                    "ell": radial.get("ell"),
                    "kM": radial.get("kM"),
                    "sector": radial.get("sector"),
                }
            ):
                raise Phase6V21Error(
                    f"selected comparison key/order changed: {comparison_path.name}"
                )
            baseline = comparison.get("nodes", {}).get("baseline")  # type: ignore[union-attr]
            if not isinstance(baseline, Mapping):
                raise Phase6V21Error("baseline radial source is missing")
            A_out = _mp_complex(baseline.get("A_out"), label="baseline.A_out")
            S_l = _mp_complex(baseline.get("S"), label="baseline.S")
            log_abs = _mp_number(
                baseline.get("log_abs_T_horizon"),
                label="baseline.log_abs_T_horizon",
            )
            phase = _mp_number(
                baseline.get("phase_T_horizon"),
                label="baseline.phase_T_horizon",
            )
            raw = reconstruct_raw_amplitudes(
                ell=int(radial["ell"]),
                A_out_raw=A_out,
                S_l=S_l,
                log_abs_T_horizon=log_abs,
                phase_T_horizon=phase,
            )
            comparison_identities[comparison_path.name] = actual_identity
            for column in columns:
                for m in (-2, 2):
                    omega = _mp_number(radial["kM"], label="radial.kM")
                    mode = build_mode_amplitudes(
                        ell=int(radial["ell"]),
                        m=m,
                        sector=str(radial["sector"]),
                        omega=omega,
                        column=column,
                        raw=raw,
                    )
                    records.append(
                        _mode_record(
                            record_ordinal=len(records),
                            radial=radial,
                            m=m,
                            column=column,
                            source=comparison,
                            comparison_identity=actual_identity,
                            common_identities=common_identities,
                            raw=raw,
                            mode=mode,
                            log_abs=log_abs,
                            phase=phase,
                        )
                    )
    if len(records) != 120 or [r["record_ordinal"] for r in records] != list(
        range(120)
    ):
        raise Phase6V21Error("V2.1 record cardinality/order changed")
    if Counter(r["incident_column"]["column"] for r in records) != Counter(  # type: ignore[index]
        {"plus": 60, "cross": 60}
    ):
        raise Phase6V21Error("V2.1 per-column cardinality changed")
    ledger = {
        "arithmetic_runtime": {
            "mpmath_file": file_identity(Path(mp.__file__)),
            "mpmath_version": mp.__version__,
            "working_dps": WORKING_DPS,
        },
        "authoritative_source_role": (
            "SchWO selected source; immutable V1 amplitudes consumed without solve"
        ),
        "comparison_records": comparison_identities,
        "common_inputs": common_identities,
        "frozen_v1_roots": gate["authoritative_v1_roots"],
        "implementation_sources": {
            "mode_amplitude_module": file_identity(
                project / "src/schwgw/scattering/gauge_invariant_asymptotics.py"
            ),
            "validation_module": file_identity(
                project / "src/schwgw/validation/phase6_v2_mode_amplitudes.py"
            ),
            **(
                {
                    "publisher": file_identity(
                        project / "scripts/phase6_publish_v2_1_mode_amplitudes.py"
                    )
                }
                if (
                    project / "scripts/phase6_publish_v2_1_mode_amplitudes.py"
                ).is_file()
                else {}
            ),
        },
        "radial_solve_count": 0,
        "schema": LEDGER_SCHEMA,
    }
    hashes = gate["hashes"]
    if not isinstance(hashes, dict):
        raise Phase6V21Error("frozen input hash ledger changed")
    return V21RecordBundle(tuple(records), ledger, dict(hashes))


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _publish_exclusive_bytes(path: Path, raw: bytes) -> dict[str, object]:
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
        handle.write(
            canonical_json_bytes({"pid": os.getpid(), "schema": "single_writer_v1"})
        )
        handle.flush()
        os.fsync(handle.fileno())
        yield
    finally:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()
        lock.unlink()


def _summary() -> dict[str, object]:
    return {
        "angles_assessed": False,
        "angular_sum_assessed": False,
        "finite_radius_observer_responses_assessed": False,
        "full_domain_v2_assessed": False,
        "global_green_permitted": False,
        "global_status": None,
        "incident_column_count": 2,
        "li_figures_assessed": False,
        "m_values": [-2, 2],
        "mode_channels_per_incident_column": 60,
        "radial_key_count": 30,
        "radial_pair_count": 15,
        "radial_solve_count": 0,
        "record_count": 120,
        "route": "A_project_master_to_martel_poisson_strain_flux",
        "schema": SUMMARY_SCHEMA,
        "scientific_scope": "bounded structural mode amplitudes only",
        "v1_full_domain_independent_scientific_certification": "PARTIAL",
        "unassessed_scope": {
            "angles": "NOT_ASSESSED",
            "angular_sum": "NOT_ASSESSED",
            "finite_radius_observer_responses": "NOT_ASSESSED",
            "full_domain_v2": "NOT_ASSESSED",
            "li_figures": "NOT_ASSESSED",
        },
    }


def publish_v2_1_mode_amplitudes(
    *,
    project_root: str | Path,
    output_root: str | Path,
    verification: Mapping[str, object],
) -> dict[str, object]:
    """Publish once to a fresh root, seal it, then perform a strict reload."""

    project = Path(project_root).absolute()
    output = Path(output_root).absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"V2.1 output root already exists: {output}")
    if output.parent.is_symlink():
        raise Phase6V21Error("V2.1 output parent is aliased")
    start_gate = verify_frozen_v2_1_inputs(project)
    bundle = build_v2_1_records(project)
    output.mkdir(parents=True, mode=0o700)
    os.chmod(output, 0o700)
    try:
        with _exclusive_writer(output):
            records_raw = b"".join(
                canonical_json_bytes(item) for item in bundle.records
            )
            records_identity = _publish_exclusive_bytes(
                output / "records.jsonl", records_raw
            )
            source_ledger_identity = _publish_exclusive_bytes(
                output / "source_ledger.json",
                canonical_json_bytes(bundle.source_ledger),
            )
            summary = _summary()
            summary_identity = _publish_exclusive_bytes(
                output / "summary.json", canonical_json_bytes(summary)
            )
            end_gate = verify_frozen_v2_1_inputs(project)
            if start_gate["hashes"] != end_gate["hashes"]:
                raise Phase6V21Error("frozen input hashes changed during publication")
            report = {
                "claims": {
                    "accepted_scientific_result_outside_120_record_domain": False,
                    "full_domain_v2": "NOT_ASSESSED",
                    "v1_full_domain_independent_scientific_certification": "PARTIAL",
                },
                "frozen_input_hashes_end": end_gate["hashes"],
                "frozen_input_hashes_start": start_gate["hashes"],
                "global_green_permitted": False,
                "global_status": None,
                "independent_reload_required_after_seal": True,
                "radial_solve_count": 0,
                "record_count": 120,
                "schema": REPORT_SCHEMA,
                "structural_domain_state": "PASS",
                "terminal_decision": TERMINAL_DECISION,
                "verification": dict(verification),
            }
            report_identity = _publish_exclusive_bytes(
                output / "report.json", canonical_json_bytes(report)
            )
            manifest = {
                "files": {
                    "records.jsonl": records_identity,
                    "report.json": report_identity,
                    "source_ledger.json": source_ledger_identity,
                    "summary.json": summary_identity,
                },
                "global_green_permitted": False,
                "record_count": 120,
                "schema": MANIFEST_SCHEMA,
                "terminal_decision": TERMINAL_DECISION,
            }
            _publish_exclusive_bytes(
                output / "manifest.json", canonical_json_bytes(manifest)
            )
        for child in output.iterdir():
            os.chmod(child, 0o444)
        os.chmod(output, 0o555)
        _fsync_directory(output)
        _fsync_directory(output.parent)
    except Exception:
        raise
    reloaded = validate_published_v2_1_mode_amplitudes(output)
    if reloaded["report"] != report:
        raise Phase6V21Error("independent reload report mismatch")
    return report


def _load_canonical_artifact_json(path: Path) -> Mapping[str, object]:
    identity = file_identity(path)
    if identity["mode"] != 0o444:
        raise Phase6V21Error(f"published artifact mode changed: {path}")
    raw = path.read_bytes()
    payload = _load_json(path)
    if raw != canonical_json_bytes(payload):
        raise Phase6V21Error(f"published JSON is not canonical: {path}")
    return payload


def validate_published_v2_1_mode_amplitudes(
    root: str | Path,
) -> dict[str, object]:
    """Independently reload every sealed artifact and structural invariant."""

    output = _direct_immutable_root(Path(root))
    expected_names = {
        "manifest.json",
        "records.jsonl",
        "report.json",
        "source_ledger.json",
        "summary.json",
    }
    if {item.name for item in output.iterdir()} != expected_names:
        raise Phase6V21Error("published file inventory changed")
    manifest = _load_canonical_artifact_json(output / "manifest.json")
    report = _load_canonical_artifact_json(output / "report.json")
    summary = _load_canonical_artifact_json(output / "summary.json")
    ledger = _load_canonical_artifact_json(output / "source_ledger.json")
    files = manifest.get("files")
    if not isinstance(files, Mapping) or set(files) != expected_names - {
        "manifest.json"
    }:
        raise Phase6V21Error("published manifest inventory changed")
    for name, expected in files.items():
        if not isinstance(expected, Mapping) or file_identity(output / name) != dict(
            expected
        ):
            raise Phase6V21Error(f"published manifest identity mismatch: {name}")
    records: list[Mapping[str, object]] = []
    raw = (output / "records.jsonl").read_bytes()
    for line in raw.splitlines(keepends=True):
        payload = json.loads(line)
        if not isinstance(payload, Mapping) or canonical_json_bytes(payload) != line:
            raise Phase6V21Error("published records JSONL is not canonical")
        records.append(payload)
    if (
        len(records) != 120
        or [item.get("record_ordinal") for item in records] != list(range(120))
        or Counter(item.get("m") for item in records) != Counter({-2: 60, 2: 60})
        or Counter(
            item.get("incident_column", {}).get("column")  # type: ignore[union-attr]
            for item in records
        )
        != Counter({"plus": 60, "cross": 60})
    ):
        raise Phase6V21Error("published record structure changed")
    if (
        report.get("schema") != REPORT_SCHEMA
        or report.get("terminal_decision") != TERMINAL_DECISION
        or report.get("record_count") != 120
        or summary.get("schema") != SUMMARY_SCHEMA
        or summary.get("radial_solve_count") != 0
        or summary.get("global_status") is not None
        or summary.get("global_green_permitted") is not False
        or ledger.get("schema") != LEDGER_SCHEMA
        or manifest.get("schema") != MANIFEST_SCHEMA
    ):
        raise Phase6V21Error("published report/summary/ledger state changed")
    for record in records:
        numerical = record.get("numerical_uncertainty_budget")
        convention = record.get("convention_uncertainty_budget")
        if (
            not isinstance(numerical, Mapping)
            or tuple(numerical) != tuple(sorted(NUMERICAL_COMPONENTS))
            or set(numerical) != set(NUMERICAL_COMPONENTS)
            or not isinstance(convention, Mapping)
            or tuple(convention) != tuple(sorted(CONVENTION_COMPONENTS))
            or set(convention) != set(CONVENTION_COMPONENTS)
        ):
            raise Phase6V21Error("published uncertainty vocabulary changed")
    return {
        "manifest": manifest,
        "records": tuple(records),
        "report": report,
        "source_ledger": ledger,
        "summary": summary,
    }


__all__ = [
    "Phase6V21Error",
    "V21RecordBundle",
    "build_v2_1_records",
    "complex_record",
    "publish_v2_1_mode_amplitudes",
    "validate_published_v2_1_mode_amplitudes",
    "verify_frozen_v2_1_inputs",
]
