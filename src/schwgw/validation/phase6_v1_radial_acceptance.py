"""Selected-domain Phase-6 V1 radial acceptance after boundary repair.

This certifier executes a fresh SchWO float64 ladder on the exact 30-key
external-direct domain and compares it, without phase or normalization fitting,
to the immutable bounded BHPT Regge--Wheeler/Zerilli evidence.  It is explicitly
selected-domain evidence; whole-domain coverage is composed separately from the
immutable campaign and repair roots.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal, localcontext
import math
import os
from pathlib import Path
import stat
import time

from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
from schwgw.numerics.adaptive_jost_radial import (
    solve_adaptive_jost_radial_at_radius,
)
from schwgw.numerics.conditioned_radial import ConditionedRadialRequest
from schwgw.perturbations import Sector
from schwgw.validation.phase6_bhpt_direct import canonical_json_bytes, sha256_file
from schwgw.validation.phase6_bhpt_direct_bounded import (
    NODE_SCHEMA as EXTERNAL_NODE_SCHEMA,
    DecimalComplex,
    _complex as decimal_complex,
    _file_identity,
    _phase as decimal_phase,
    _read_json,
    validate_published_bounded_direct,
)
from schwgw.validation.phase6_execution_contract import (
    external_direct_calibration_keys,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RUNNER_PATH = PROJECT_ROOT / "scripts" / "phase6_publish_v1_radial_acceptance.py"
SCHEMA = "schwgw_phase6_v1_radial_selected_acceptance_v1"
SUMMARY_SCHEMA = "schwgw_phase6_v1_radial_selected_acceptance_summary_v1"
MANIFEST_SCHEMA = "schwgw_phase6_v1_radial_selected_acceptance_manifest_v1"
TYPED_RESULT_SCHEMA = "schwgw_phase6_v1_typed_physical_result_v1"
FORMAL_ROOT_MODE = 0o555
FORMAL_FILE_MODE = 0o444
EXPECTED_KEY_COUNT = 30

R_IN_COARSE = 3.0e-10
R_IN_BASELINE = 1.0e-10
R_OUT_BASELINE = 300.0
R_OUT_LADDER = 600.0
JOST_BASELINE = 160
JOST_LADDER = 224
RTOL_BASELINE = 1.0e-10
ATOL_BASELINE = 1.0e-12
RTOL_LADDER = 1.0e-12
ATOL_LADDER = 1.0e-14

THRESHOLDS = {
    "backend_complex_S": 2.0e-6,
    "backend_log_abs_T": 2.0e-6,
    "backend_phase_T_rad": 2.0e-6,
    "flux_residual": 1.0e-8,
    "jost_order_complex_S": 2.0e-6,
    "ode_tolerance_complex_S": 2.0e-6,
    "r_in_complex_S": 2.0e-6,
    "r_in_log_abs_T": 2.0e-6,
    "r_in_phase_T_rad": 2.0e-6,
    "r_out_complex_S": 2.0e-6,
}


class V1RadialAcceptanceError(ValueError):
    """Raised when the selected-domain comparison or evidence drifts."""


def _complex_record(value: complex) -> dict[str, str]:
    return {
        "abs": format(abs(value), ".17g"),
        "imag": format(value.imag, ".17g"),
        "real": format(value.real, ".17g"),
    }


def _relative_complex(left: complex, right: complex) -> float:
    return float(abs(left - right) / max(1.0, abs(left), abs(right)))


def _wrapped(left: float, right: float) -> float:
    return float(abs(math.remainder(left - right, 2.0 * math.pi)))


def _decimal_log_abs(value: DecimalComplex) -> Decimal:
    magnitude = value.absolute()
    if magnitude == 0:
        raise V1RadialAcceptanceError("external transmission vanished exactly")
    with localcontext() as context:
        context.prec = 100
        return magnitude.ln()


def _external_nodes(root: Path) -> dict[tuple[str, str, int], Mapping[str, object]]:
    summary = validate_published_bounded_direct(root)
    if (
        summary.get("overall_state") != "PASS"
        or summary.get("record_count") != EXPECTED_KEY_COUNT
        or summary.get("numerical_pass_key_count") != EXPECTED_KEY_COUNT
        or summary.get("even_is_independent_zerilli_solve") is not True
        or summary.get("parity_derived_even_used") is not False
    ):
        raise V1RadialAcceptanceError("external bounded-direct root is not 30/30 PASS")
    result: dict[tuple[str, str, int], Mapping[str, object]] = {}
    for path in sorted(root.glob("node_*__wp60.json")):
        payload = _read_json(path, formal=True)
        key = payload.get("key")
        if (
            payload.get("schema") != EXTERNAL_NODE_SCHEMA
            or payload.get("node_id") != "wp60"
            or not isinstance(key, Mapping)
        ):
            raise V1RadialAcceptanceError("external high-precision node changed")
        identity = (str(key.get("kM")), str(key.get("sector")), int(key.get("ell")))
        if identity in result:
            raise V1RadialAcceptanceError("duplicate external high-precision key")
        result[identity] = payload
    expected = {
        (key.kM, key.sector, key.ell) for key in external_direct_calibration_keys()
    }
    if set(result) != expected:
        raise V1RadialAcceptanceError("external high-precision domain changed")
    return result


def _solve(
    *,
    key: Mapping[str, object],
    r_in_eps: float,
    r_out: float,
    jost_order: int,
    rtol: float,
    atol: float,
) -> dict[str, object]:
    sector = Sector(str(key["sector"]))
    request = ConditionedRadialRequest(
        sector=sector,
        ell=int(key["ell"]),
        k=float(key["kM"]),
        required_radius=40.0,
        r_out=r_out,
        r_in_eps=r_in_eps,
        rtol=rtol,
        atol=atol,
        outer_series_order=jost_order,
    )
    result = solve_adaptive_jost_radial_at_radius(
        request, SchwarzschildBackground(M=1.0)
    )
    scattering = -result.A_out / (((-1) ** int(key["ell"])) * result.A_in)
    return {
        "A_out": _complex_record(result.A_out),
        "S": _complex_record(scattering),
        "configuration": {
            "atol": atol,
            "jost_order": jost_order,
            "r_in_eps": r_in_eps,
            "requested_r_out_M": r_out,
            "rtol": rtol,
        },
        "diagnostics": {
            "backend": result.diagnostics["backend"],
            "flux_residual": float(result.diagnostics["flux_residual"]),
            "legacy_path_used": result.diagnostics["legacy_path_used"],
            "newman_penrose_path_used": result.diagnostics["newman_penrose_path_used"],
            "paper_specific_envelope_used": result.diagnostics[
                "paper_specific_envelope_used"
            ],
            "pseudoinverse_used": result.diagnostics["pseudoinverse_used"],
            "selected_r_out_M": float(result.diagnostics["selected_r_out"]),
        },
        "log_abs_T_horizon": float(result.log_abs_T_horizon),
        "phase_T_horizon": float(result.phase_T_horizon),
    }


def _complex_from_record(value: Mapping[str, object]) -> complex:
    return complex(float(value["real"]), float(value["imag"]))


def _check(estimate: float, threshold: float) -> dict[str, object]:
    return {
        "estimate": estimate,
        "state": "PASS"
        if math.isfinite(estimate) and estimate <= threshold
        else "FAIL",
        "threshold": threshold,
    }


def _item_id(key: Mapping[str, object]) -> str:
    km = str(key["kM"]).replace(".", "p")
    return f"radial_km_{km}_{key['sector']}_ell_{int(key['ell']):03d}"


def _typed_budget_component(
    *, state: str, estimate: float, units: str, reason: str
) -> dict[str, object]:
    return {
        "estimate": estimate,
        "reason": reason,
        "state": state,
        "units": units,
    }


def build_typed_report(
    records: list[dict[str, object]], summary: Mapping[str, object]
) -> dict[str, object]:
    """Project the native comparison into the strict Phase-6 release schema."""

    passed = summary["overall_state"] == "PASS"
    state = "PASS" if passed else "FAIL"
    maxima = {
        name: max(float(record["checks"][name]["estimate"]) for record in records)
        for name in THRESHOLDS
    }
    budget_state = "PASS" if passed else "FAIL"
    not_applicable = (
        "not applicable to a sector-resolved radial master S-matrix; no observer, "
        "tetrad, polarization, or detector-response claim is made"
    )
    numerical = {
        "arithmetic_precision": _typed_budget_component(
            state=budget_state,
            estimate=maxima["backend_complex_S"],
            units="relative_complex_S",
            reason="SchWO float64 result is bounded by the independent 40/60-digit BHPT comparison",
        ),
        "axis_limit": _typed_budget_component(
            state="PASS",
            estimate=0.0,
            units="not_applicable",
            reason="no angular-axis limit enters the per-mode radial S-matrix",
        ),
        "backend_difference": _typed_budget_component(
            state=budget_state,
            estimate=maxima["backend_complex_S"],
            units="relative_complex_S",
            reason="maximum no-fit SchWO versus external BHPT direct difference",
        ),
        "jost_order": _typed_budget_component(
            state=budget_state,
            estimate=maxima["jost_order_complex_S"],
            units="relative_complex_S",
            reason="maximum 160-versus-224 Jost-order difference",
        ),
        "lmax": _typed_budget_component(
            state="PASS",
            estimate=0.0,
            units="not_applicable",
            reason="the observable is per (k,sector,ell), not a truncated angular sum",
        ),
        "ode_tolerance": _typed_budget_component(
            state=budget_state,
            estimate=maxima["ode_tolerance_complex_S"],
            units="relative_complex_S",
            reason="maximum rtol 1e-10 versus 1e-12 difference",
        ),
        "r_in": _typed_budget_component(
            state=budget_state,
            estimate=max(
                maxima["r_in_complex_S"],
                maxima["r_in_log_abs_T"],
                maxima["r_in_phase_T_rad"],
            ),
            units="max(relative_complex_S,absolute_log_T,radian)",
            reason="maximum repaired r_in_eps 3e-10 versus 1e-10 S/T difference",
        ),
        "r_out": _typed_budget_component(
            state=budget_state,
            estimate=maxima["r_out_complex_S"],
            units="relative_complex_S",
            reason="maximum requested 300M versus 600M adaptive-Jost difference",
        ),
    }
    convention = {
        name: _typed_budget_component(
            state="PASS", estimate=0.0, units="not_applicable", reason=not_applicable
        )
        for name in ("observer", "worldline", "tetrad", "polarization_basis")
    }
    convention.update(
        {
            "phase_origin": _typed_budget_component(
                state=budget_state,
                estimate=maxima["backend_phase_T_rad"],
                units="radian",
                reason=(
                    "absolute r_star origin and exp(-ikt) convention compared without "
                    "phase fitting against external BHPT"
                ),
            ),
            "total_scattered_definition": _typed_budget_component(
                state=budget_state,
                estimate=maxima["backend_complex_S"],
                units="relative_complex_S",
                reason="S=-A_out/[(-1)^ell A_in] is identical on both sides",
            ),
        }
    )
    implementation = summary.get("implementation_sources")
    if not isinstance(implementation, Mapping):
        raise V1RadialAcceptanceError("typed report implementation ledger is missing")
    expected_ids = sorted(_item_id(record["key"]) for record in records)
    return {
        "convention_uncertainty_budget": convention,
        "full_paper_figure_rerun": False,
        "gate": "V1",
        "global_green_permitted": False,
        "implementation_source_sha256s": sorted(set(implementation.values())),
        "independence_class": "EXTERNAL_SOURCE",
        "item_results": [
            {"item_id": _item_id(record["key"]), "state": record["overall_state"]}
            for record in sorted(records, key=lambda item: _item_id(item["key"]))
        ],
        "kernel_unit_test_only": False,
        "li_figure_agreement_primary_gate": False,
        "limitations": [
            "acceptance is exact only for the frozen selected 30-key domain",
            "the BHPT source overlay changes only the generic infinity boundary radius",
            "no whole-domain, detector-response, or paper-figure agreement claim follows",
        ],
        "numerical_uncertainty_budget": numerical,
        "observable": "radial_s_matrix_flux",
        "observer_qualification": {
            "detector_response_claim_permitted": False,
            "output_kind": "RADIAL_S_MATRIX_CROSS_BACKEND_COMPARISON",
            "worldline_tetrad_pure_gauge_test": "NOT_ASSESSED",
        },
        "parameter_domain": {
            "description": "frozen 30 sector-resolved BHPT direct calibration keys",
            "domain_id": "bhpt_bounded_adaptive_selected_30",
            "expected_item_ids": expected_ids,
            "expected_items": len(expected_ids),
            "parameters": {
                "kM": ["0.5", "1", "2", "4"],
                "sectors": ["odd", "even"],
            },
            "selection_policy": "frozen execution-contract v4 external-direct domain",
        },
        "reason": (
            "all selected keys pass independent BHPT and SchWO boundary/precision ladders"
            if passed
            else "one or more selected keys failed a frozen numerical gate"
        ),
        "result_id": "phase6_v1_bhpt_bounded_adaptive_selected_30",
        "role": "INDEPENDENT_SCIENCE",
        "schema": TYPED_RESULT_SCHEMA,
        "science_executed": True,
        "scientific_evidence": True,
        "state": state,
    }


def build_selected_comparison(
    direct_root: str | Path,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Execute the exact 30-key SchWO ladder and compare to external BHPT."""

    root = Path(direct_root).absolute()
    external = _external_nodes(root)
    records: list[dict[str, object]] = []
    started = time.monotonic()
    for ordinal, frozen_key in enumerate(external_direct_calibration_keys()):
        key = frozen_key.to_record()
        identity = (frozen_key.kM, frozen_key.sector, frozen_key.ell)
        ext = external[identity]
        nodes = {
            "baseline": _solve(
                key=key,
                r_in_eps=R_IN_BASELINE,
                r_out=R_OUT_BASELINE,
                jost_order=JOST_BASELINE,
                rtol=RTOL_BASELINE,
                atol=ATOL_BASELINE,
            ),
            "r_in_coarse": _solve(
                key=key,
                r_in_eps=R_IN_COARSE,
                r_out=R_OUT_BASELINE,
                jost_order=JOST_BASELINE,
                rtol=RTOL_BASELINE,
                atol=ATOL_BASELINE,
            ),
            "r_out_x2": _solve(
                key=key,
                r_in_eps=R_IN_BASELINE,
                r_out=R_OUT_LADDER,
                jost_order=JOST_BASELINE,
                rtol=RTOL_BASELINE,
                atol=ATOL_BASELINE,
            ),
            "jost_224": _solve(
                key=key,
                r_in_eps=R_IN_BASELINE,
                r_out=R_OUT_BASELINE,
                jost_order=JOST_LADDER,
                rtol=RTOL_BASELINE,
                atol=ATOL_BASELINE,
            ),
            "tight_tolerance": _solve(
                key=key,
                r_in_eps=R_IN_BASELINE,
                r_out=R_OUT_BASELINE,
                jost_order=JOST_BASELINE,
                rtol=RTOL_LADDER,
                atol=ATOL_LADDER,
            ),
        }
        baseline_s = _complex_from_record(nodes["baseline"]["S"])
        ext_s_decimal = decimal_complex(ext["phase_factor"], "external S")
        ext_s = complex(float(ext_s_decimal.real), float(ext_s_decimal.imag))
        ext_t = decimal_complex(ext["transmission"], "external T")
        checks = {
            "backend_complex_S": _check(
                _relative_complex(baseline_s, ext_s), THRESHOLDS["backend_complex_S"]
            ),
            "backend_log_abs_T": _check(
                float(
                    abs(
                        Decimal(str(nodes["baseline"]["log_abs_T_horizon"]))
                        - _decimal_log_abs(ext_t)
                    )
                ),
                THRESHOLDS["backend_log_abs_T"],
            ),
            "backend_phase_T_rad": _check(
                _wrapped(
                    float(nodes["baseline"]["phase_T_horizon"]),
                    decimal_phase(ext_t),
                ),
                THRESHOLDS["backend_phase_T_rad"],
            ),
            "flux_residual": _check(
                float(nodes["baseline"]["diagnostics"]["flux_residual"]),
                THRESHOLDS["flux_residual"],
            ),
            "jost_order_complex_S": _check(
                _relative_complex(
                    baseline_s, _complex_from_record(nodes["jost_224"]["S"])
                ),
                THRESHOLDS["jost_order_complex_S"],
            ),
            "ode_tolerance_complex_S": _check(
                _relative_complex(
                    baseline_s,
                    _complex_from_record(nodes["tight_tolerance"]["S"]),
                ),
                THRESHOLDS["ode_tolerance_complex_S"],
            ),
            "r_in_complex_S": _check(
                _relative_complex(
                    baseline_s, _complex_from_record(nodes["r_in_coarse"]["S"])
                ),
                THRESHOLDS["r_in_complex_S"],
            ),
            "r_in_log_abs_T": _check(
                abs(
                    float(nodes["baseline"]["log_abs_T_horizon"])
                    - float(nodes["r_in_coarse"]["log_abs_T_horizon"])
                ),
                THRESHOLDS["r_in_log_abs_T"],
            ),
            "r_in_phase_T_rad": _check(
                _wrapped(
                    float(nodes["baseline"]["phase_T_horizon"]),
                    float(nodes["r_in_coarse"]["phase_T_horizon"]),
                ),
                THRESHOLDS["r_in_phase_T_rad"],
            ),
            "r_out_complex_S": _check(
                _relative_complex(
                    baseline_s, _complex_from_record(nodes["r_out_x2"]["S"])
                ),
                THRESHOLDS["r_out_complex_S"],
            ),
        }
        overall = (
            "PASS"
            if all(check["state"] == "PASS" for check in checks.values())
            else "FAIL"
        )
        records.append(
            {
                "checks": checks,
                "convention_uncertainty_budget": {
                    "absolute_phase_origin": "r_star=r+2*log(r/2-1), M=1",
                    "even_sector": "independent Zerilli on both sides",
                    "fourier_convention": "exp(-i*k*t)",
                    "phase_or_normalization_fit": False,
                    "scattering_definition": "S=-A_out/[(-1)^ell A_in]",
                    "state": "PASS_SELECTED_DOMAIN",
                },
                "external": {
                    "S": {
                        "imag": str(ext_s_decimal.imag),
                        "real": str(ext_s_decimal.real),
                    },
                    "log_abs_T_horizon": str(_decimal_log_abs(ext_t)),
                    "phase_T_horizon": decimal_phase(ext_t),
                },
                "key": key,
                "nodes": nodes,
                "ordinal": ordinal,
                "overall_state": overall,
                "schema": SCHEMA,
            }
        )
    pass_count = sum(record["overall_state"] == "PASS" for record in records)
    summary = {
        "acceptance_scope": "exact external-direct selected 30-key domain",
        "convention_uncertainty_budget": {
            "absolute_phase_convention": "PASS_SELECTED_DOMAIN_NO_FIT",
            "unassessed_outside_selected_domain": True,
        },
        "elapsed_seconds": time.monotonic() - started,
        "failed_key_count": EXPECTED_KEY_COUNT - pass_count,
        "global_green_permitted": False,
        "li_figure_agreement_primary_gate": False,
        "numerical_pass_key_count": pass_count,
        "overall_state": "PASS" if pass_count == EXPECTED_KEY_COUNT else "FAIL",
        "record_count": len(records),
        "schema": SUMMARY_SCHEMA,
        "thresholds": dict(THRESHOLDS),
    }
    return records, summary


def _exclusive_json(path: Path, payload: object) -> dict[str, object]:
    data = canonical_json_bytes(payload)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(descriptor)
    os.chmod(path, FORMAL_FILE_MODE)
    return _file_identity(path, formal=True)


def publish_selected_acceptance(
    *, direct_root: str | Path, output_root: str | Path
) -> dict[str, object]:
    root = Path(output_root).absolute()
    if root.exists() or root.is_symlink():
        raise V1RadialAcceptanceError("output_root must be fresh and absent")
    direct = Path(direct_root).absolute()
    records, summary = build_selected_comparison(direct)
    root.mkdir(parents=True, mode=0o700)
    os.chmod(root, 0o700)
    identities: dict[str, dict[str, object]] = {}
    for record in records:
        key = record["key"]
        km = str(key["kM"]).replace(".", "p")
        name = (
            f"comparison_{int(record['ordinal']):02d}__kM_{km}__"
            f"{key['sector']}__ell_{int(key['ell']):04d}.json"
        )
        identities[name] = _exclusive_json(root / name, record)
    summary["direct_root"] = {
        "path": str(direct),
        "summary_sha256": sha256_file(direct / "summary.json"),
    }
    summary["implementation_sources"] = {
        "adaptive_jost_radial.py": sha256_file(
            PROJECT_ROOT / "src/schwgw/numerics/adaptive_jost_radial.py"
        ),
        "conditioned_radial.py": sha256_file(
            PROJECT_ROOT / "src/schwgw/numerics/conditioned_radial.py"
        ),
        "publisher": sha256_file(RUNNER_PATH),
        "scaled_tortoise_radial.py": sha256_file(
            PROJECT_ROOT / "src/schwgw/numerics/scaled_tortoise_radial.py"
        ),
        "validation_module": sha256_file(Path(__file__)),
    }
    summary["source_role_ledger"] = {
        "external_bhpt": {
            "even_sector": "independent direct Zerilli",
            "independence_class": "EXTERNAL_SOURCE",
            "role": "INDEPENDENT_EXTERNAL_REFERENCE",
        },
        "schwo": {
            "independence_class": "SAME_IMPLEMENTATION",
            "role": "PRIMARY_PROJECT_AMPLITUDE",
        },
    }
    identities["summary.json"] = _exclusive_json(root / "summary.json", summary)
    report = build_typed_report(records, summary)
    identities["report.json"] = _exclusive_json(root / "report.json", report)
    manifest = {
        "artifacts": identities,
        "global_green_permitted": False,
        "overall_state": summary["overall_state"],
        "schema": MANIFEST_SCHEMA,
        "summary_sha256": identities["summary.json"]["sha256"],
    }
    _exclusive_json(root / "manifest.json", manifest)
    os.chmod(root, FORMAL_ROOT_MODE)
    return validate_published_selected_acceptance(root)


def validate_published_selected_acceptance(root_path: str | Path) -> dict[str, object]:
    root = Path(root_path).absolute()
    info = root.lstat()
    if (
        root.is_symlink()
        or root.resolve(strict=True) != root
        or not stat.S_ISDIR(info.st_mode)
        or stat.S_IMODE(info.st_mode) != FORMAL_ROOT_MODE
    ):
        raise V1RadialAcceptanceError("selected acceptance root is not immutable 0555")
    manifest = _read_json(root / "manifest.json", formal=True)
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise V1RadialAcceptanceError("selected acceptance manifest changed")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, Mapping):
        raise V1RadialAcceptanceError("selected acceptance ledger is missing")
    if {path.name for path in root.iterdir() if path.is_file()} != {
        *artifacts,
        "manifest.json",
    }:
        raise V1RadialAcceptanceError("selected acceptance inventory changed")
    for name, expected in artifacts.items():
        if _file_identity(root / str(name), formal=True) != expected:
            raise V1RadialAcceptanceError(f"selected artifact identity changed: {name}")
    summary = _read_json(root / "summary.json", formal=True)
    if (
        summary.get("schema") != SUMMARY_SCHEMA
        or summary.get("record_count") != EXPECTED_KEY_COUNT
        or summary.get("global_green_permitted") is not False
        or manifest.get("summary_sha256") != sha256_file(root / "summary.json")
    ):
        raise V1RadialAcceptanceError("selected acceptance summary changed")
    comparison_paths = sorted(root.glob("comparison_*.json"))
    if len(comparison_paths) != EXPECTED_KEY_COUNT:
        raise V1RadialAcceptanceError("selected comparison inventory changed")
    records: list[dict[str, object]] = []
    expected_keys = external_direct_calibration_keys()
    for ordinal, path in enumerate(comparison_paths):
        record = _read_json(path, formal=True)
        checks = record.get("checks")
        if (
            record.get("schema") != SCHEMA
            or record.get("ordinal") != ordinal
            or record.get("key") != expected_keys[ordinal].to_record()
            or record.get("overall_state") not in {"PASS", "FAIL"}
            or not isinstance(checks, Mapping)
            or set(checks) != set(THRESHOLDS)
        ):
            raise V1RadialAcceptanceError("selected comparison record changed")
        derived = "PASS"
        for name, threshold in THRESHOLDS.items():
            check = checks[name]
            if (
                not isinstance(check, Mapping)
                or set(check) != {"estimate", "state", "threshold"}
                or float(check["threshold"]) != threshold
                or check["state"] not in {"PASS", "FAIL"}
                or not math.isfinite(float(check["estimate"]))
                or check["state"]
                != _check(float(check["estimate"]), threshold)["state"]
            ):
                raise V1RadialAcceptanceError("selected numerical check changed")
            if check["state"] == "FAIL":
                derived = "FAIL"
        if record["overall_state"] != derived:
            raise V1RadialAcceptanceError("selected record state is not derived")
        records.append(dict(record))
    pass_count = sum(record["overall_state"] == "PASS" for record in records)
    if (
        summary.get("numerical_pass_key_count") != pass_count
        or summary.get("failed_key_count") != EXPECTED_KEY_COUNT - pass_count
        or summary.get("overall_state")
        != ("PASS" if pass_count == EXPECTED_KEY_COUNT else "FAIL")
    ):
        raise V1RadialAcceptanceError("selected aggregate state changed")
    direct = summary.get("direct_root")
    if not isinstance(direct, Mapping) or set(direct) != {"path", "summary_sha256"}:
        raise V1RadialAcceptanceError("selected direct-source identity changed")
    direct_root = Path(str(direct["path"])).absolute()
    _external_nodes(direct_root)
    if sha256_file(direct_root / "summary.json") != direct["summary_sha256"]:
        raise V1RadialAcceptanceError("selected direct-source hash changed")
    expected_sources = {
        "adaptive_jost_radial.py": sha256_file(
            PROJECT_ROOT / "src/schwgw/numerics/adaptive_jost_radial.py"
        ),
        "conditioned_radial.py": sha256_file(
            PROJECT_ROOT / "src/schwgw/numerics/conditioned_radial.py"
        ),
        "publisher": sha256_file(RUNNER_PATH),
        "scaled_tortoise_radial.py": sha256_file(
            PROJECT_ROOT / "src/schwgw/numerics/scaled_tortoise_radial.py"
        ),
        "validation_module": sha256_file(Path(__file__)),
    }
    if summary.get("implementation_sources") != expected_sources:
        raise V1RadialAcceptanceError("selected implementation source drift")
    report = _read_json(root / "report.json", formal=True)
    if report != build_typed_report(records, summary):
        raise V1RadialAcceptanceError("selected typed report changed")
    return dict(summary)


__all__ = [
    "MANIFEST_SCHEMA",
    "SCHEMA",
    "SUMMARY_SCHEMA",
    "THRESHOLDS",
    "V1RadialAcceptanceError",
    "build_selected_comparison",
    "build_typed_report",
    "publish_selected_acceptance",
    "validate_published_selected_acceptance",
]
