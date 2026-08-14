"""Full D_union baseline with turning-aware Jost and r_in=1e-10 boundaries."""

from __future__ import annotations

from collections.abc import Mapping
from concurrent.futures import ProcessPoolExecutor
from importlib.metadata import version
import json
import math
import os
from pathlib import Path
import platform
import stat
import time

from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
from schwgw.numerics.conditioned_radial import ConditionedRadialRequest
from schwgw.numerics.physical_boundary_radial import (
    solve_physical_boundary_radial_at_radius,
)
from schwgw.perturbations import Sector
from schwgw.validation.phase6_conditioning_scan import load_frozen_scan_contract
from schwgw.validation.phase6_v1_final_radial_baseline import (
    ATOL,
    DOMAIN_ROOT,
    EXECUTION_ROOT,
    EXPECTED_KEY_COUNT,
    EXPECTED_UNION_SHA256,
    FLUX_THRESHOLD,
    FORMAL_FILE_MODE,
    FORMAL_ROOT_MODE,
    JOST_ORDER,
    RECORD_SCHEMA,
    REQUIRED_RADIUS_M,
    REQUESTED_R_OUT_M,
    RTOL,
    _complex_record,
    _exclusive_json,
    _identity,
    _load_records,
    _validate_record,
    _writer_lock,
    canonical_jsonl_bytes,
    sha256_file,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RUNNER_PATH = PROJECT_ROOT / "scripts" / "phase6_run_v1_final_radial_baseline_v2.py"
PLAN_SCHEMA = "schwgw_phase6_v1_final_radial_baseline_plan_v2"
SUMMARY_SCHEMA = "schwgw_phase6_v1_final_radial_baseline_summary_v2"
MANIFEST_SCHEMA = "schwgw_phase6_v1_final_radial_baseline_manifest_v2"
TYPED_RESULT_SCHEMA = "schwgw_phase6_v1_typed_physical_result_v1"
R_IN_EPS_V2 = 1.0e-10


class V1FinalBaselineV2Error(ValueError):
    """Raised when the turning-aware full-domain campaign drifts."""


def _solve_key_v2(payload: tuple[int, dict[str, object]]) -> dict[str, object]:
    ordinal, key = payload
    started = time.monotonic()
    try:
        request = ConditionedRadialRequest(
            sector=Sector(str(key["sector"])),
            ell=int(key["ell"]),
            k=float(key["kM"]),
            required_radius=REQUIRED_RADIUS_M,
            r_out=REQUESTED_R_OUT_M,
            r_in_eps=R_IN_EPS_V2,
            rtol=RTOL,
            atol=ATOL,
            outer_series_order=JOST_ORDER,
        )
        result = solve_physical_boundary_radial_at_radius(
            request, SchwarzschildBackground(M=1.0)
        )
        scattering = -result.A_out / (((-1) ** int(key["ell"])) * result.A_in)
        diagnostics = result.diagnostics
        flux = float(diagnostics["flux_residual"])
        invariants = {
            "finite_S": math.isfinite(scattering.real)
            and math.isfinite(scattering.imag),
            "finite_log_abs_T": math.isfinite(result.log_abs_T_horizon),
            "finite_phase_T": math.isfinite(result.phase_T_horizon),
            "flux_gate": math.isfinite(flux) and flux <= FLUX_THRESHOLD,
            "legacy_path_isolated": diagnostics["legacy_path_used"] is False,
            "newman_penrose_path_isolated": diagnostics["newman_penrose_path_used"]
            is False,
            "paper_envelope_absent": diagnostics["paper_specific_envelope_used"]
            is False,
            "pseudoinverse_isolated": diagnostics["pseudoinverse_used"] is False,
        }
        state = "PASS" if all(invariants.values()) else "FAIL"
        return {
            "S": _complex_record(scattering),
            "diagnostics": {
                "backend": diagnostics["backend"],
                "flux_residual": flux,
                "jost_condition_number": diagnostics["selected_jost_condition_number"],
                "jost_maximum_series_residual": diagnostics[
                    "selected_jost_maximum_series_residual"
                ],
                "jost_maximum_tail_ratio": diagnostics[
                    "selected_jost_maximum_tail_ratio"
                ],
                "selected_r_out_M": diagnostics["selected_r_out"],
                "turning_proxy_M": diagnostics["turning_proxy_M"],
            },
            "elapsed_seconds": time.monotonic() - started,
            "failure": None,
            "invariants": invariants,
            "key": key,
            "log_abs_T_horizon": result.log_abs_T_horizon,
            "ordinal": ordinal,
            "phase_T_horizon": result.phase_T_horizon,
            "schema": RECORD_SCHEMA,
            "scientific_acceptance": False,
            "state": state,
        }
    except Exception as exc:
        return {
            "elapsed_seconds": time.monotonic() - started,
            "failure": f"{type(exc).__name__}: {exc}",
            "key": key,
            "ordinal": ordinal,
            "schema": RECORD_SCHEMA,
            "scientific_acceptance": False,
            "state": "FAIL",
        }


def _plan(keys_count: int, *, limit: int | None) -> dict[str, object]:
    union_path = DOMAIN_ROOT / "D_union.jsonl"
    if sha256_file(union_path) != EXPECTED_UNION_SHA256:
        raise V1FinalBaselineV2Error("frozen D_union hash changed")
    return {
        "configuration": {
            "atol": ATOL,
            "jost_order": JOST_ORDER,
            "outer_policy": "max(requested_r_out,sqrt(ell*(ell+1))/k) times (1,2,4,8) with Jost quality gates",
            "r_in_eps": R_IN_EPS_V2,
            "requested_r_out_M": REQUESTED_R_OUT_M,
            "required_radius_M": REQUIRED_RADIUS_M,
            "rtol": RTOL,
        },
        "domain": {
            "D_union_sha256": EXPECTED_UNION_SHA256,
            "execution_count": keys_count,
            "full_count": EXPECTED_KEY_COUNT,
            "limit": limit,
        },
        "global_green_permitted": False,
        "implementation_sources": {
            "adaptive_jost_radial.py": sha256_file(
                PROJECT_ROOT / "src/schwgw/numerics/adaptive_jost_radial.py"
            ),
            "background_base.py": sha256_file(
                PROJECT_ROOT / "src/schwgw/backgrounds/base.py"
            ),
            "conditioned_radial.py": sha256_file(
                PROJECT_ROOT / "src/schwgw/numerics/conditioned_radial.py"
            ),
            "matching.py": sha256_file(
                PROJECT_ROOT / "src/schwgw/numerics/matching.py"
            ),
            "perturbations_init.py": sha256_file(
                PROJECT_ROOT / "src/schwgw/perturbations/__init__.py"
            ),
            "perturbations_potentials.py": sha256_file(
                PROJECT_ROOT / "src/schwgw/perturbations/potentials.py"
            ),
            "perturbations_reconstruction.py": sha256_file(
                PROJECT_ROOT / "src/schwgw/perturbations/reconstruction.py"
            ),
            "perturbations_sectors.py": sha256_file(
                PROJECT_ROOT / "src/schwgw/perturbations/sectors.py"
            ),
            "phase6_conditioning_scan.py": sha256_file(
                PROJECT_ROOT / "src/schwgw/validation/phase6_conditioning_scan.py"
            ),
            "phase6_domain.py": sha256_file(
                PROJECT_ROOT / "src/schwgw/validation/phase6_domain.py"
            ),
            "phase6_v1_final_radial_baseline.py": sha256_file(
                PROJECT_ROOT
                / "src/schwgw/validation/phase6_v1_final_radial_baseline.py"
            ),
            "physical_boundary_radial.py": sha256_file(
                PROJECT_ROOT / "src/schwgw/numerics/physical_boundary_radial.py"
            ),
            "runner": sha256_file(RUNNER_PATH),
            "scaled_tortoise_radial.py": sha256_file(
                PROJECT_ROOT / "src/schwgw/numerics/scaled_tortoise_radial.py"
            ),
            "validation_module": sha256_file(Path(__file__)),
        },
        "li_figure_agreement_primary_gate": False,
        "runtime": {
            "numpy": version("numpy"),
            "python": platform.python_version(),
            "scipy": version("scipy"),
        },
        "schema": PLAN_SCHEMA,
    }


def _item_id(record: Mapping[str, object]) -> str:
    key = record["key"]
    if not isinstance(key, Mapping):
        raise V1FinalBaselineV2Error("record key changed")
    km = str(key["kM"]).replace(".", "p")
    return f"radial_km_{km}_{key['sector']}_ell_{int(key['ell']):03d}"


def _budget_component(
    *, state: str, estimate: float | None, units: str, reason: str
) -> dict[str, object]:
    return {
        "estimate": estimate,
        "reason": reason,
        "state": state,
        "units": units,
    }


def _typed_report(
    records: list[dict[str, object]],
    summary: Mapping[str, object],
    plan: Mapping[str, object],
) -> dict[str, object]:
    fail_count = int(summary["failed_key_count"])
    full_domain = int(summary["completed_key_count"]) == EXPECTED_KEY_COUNT
    result_state = "FAIL" if fail_count else "PARTIAL"
    not_applicable = (
        "not applicable to one sector-resolved radial master mode; no observer, "
        "tetrad, angular-axis, detector, or lmax-truncation claim is made"
    )
    numerical = {
        "arithmetic_precision": _budget_component(
            state="NOT_ASSESSED",
            estimate=None,
            units="relative_complex_S",
            reason="full-domain arbitrary-precision comparison is not performed",
        ),
        "axis_limit": _budget_component(
            state="PASS", estimate=0.0, units="not_applicable", reason=not_applicable
        ),
        "backend_difference": _budget_component(
            state="NOT_ASSESSED",
            estimate=None,
            units="relative_complex_S",
            reason="independent backends are validated on separate selected domains",
        ),
        "jost_order": _budget_component(
            state="PARTIAL" if not fail_count else "FAIL",
            estimate=max(
                (
                    float(record["diagnostics"]["jost_maximum_series_residual"])
                    for record in records
                    if record["state"] == "PASS"
                ),
                default=None,
            ),
            units="maximum_series_residual",
            reason=(
                "every accepted key passes the frozen Jost residual/tail/conditioning "
                "selector, but a full-domain order ladder is not performed"
            ),
        ),
        "lmax": _budget_component(
            state="PASS", estimate=0.0, units="not_applicable", reason=not_applicable
        ),
        "ode_tolerance": _budget_component(
            state="NOT_ASSESSED",
            estimate=None,
            units="relative_complex_S",
            reason="one frozen ODE tolerance is used per full-domain key",
        ),
        "r_in": _budget_component(
            state="PARTIAL" if not fail_count else "FAIL",
            estimate=R_IN_EPS_V2,
            units="epsilon_at_r_in_over_2M",
            reason=(
                "the repaired near-horizon offset is used throughout; full-domain "
                "r_in ladders remain separate diagnostic evidence"
            ),
        ),
        "r_out": _budget_component(
            state="PARTIAL" if not fail_count else "FAIL",
            estimate=max(
                (
                    float(record["diagnostics"]["selected_r_out_M"])
                    for record in records
                    if record["state"] == "PASS"
                ),
                default=None,
            ),
            units="M_selected_maximum",
            reason=(
                "each key uses the generic turning-proxy plus Jost-quality selector; "
                "a full-domain solution-difference r_out ladder is not performed"
            ),
        ),
    }
    convention = {
        name: _budget_component(
            state="PASS", estimate=0.0, units="not_applicable", reason=not_applicable
        )
        for name in ("observer", "worldline", "tetrad", "polarization_basis")
    }
    convention.update(
        {
            "phase_origin": _budget_component(
                state="NOT_ASSESSED",
                estimate=None,
                units="radian",
                reason=(
                    "absolute phase is frozen and externally checked only on the "
                    "separate selected BHPT domain"
                ),
            ),
            "total_scattered_definition": _budget_component(
                state="PASS",
                estimate=0.0,
                units="definition",
                reason="S=-A_out/[(-1)^ell A_in] is fixed for every stored key",
            ),
        }
    )
    implementation = plan.get("implementation_sources")
    if not isinstance(implementation, Mapping):
        raise V1FinalBaselineV2Error("plan implementation ledger changed")
    ordered = sorted(records, key=_item_id)
    expected_ids = [_item_id(record) for record in ordered]
    return {
        "convention_uncertainty_budget": convention,
        "full_paper_figure_rerun": False,
        "gate": "V1",
        "global_green_permitted": False,
        "implementation_source_sha256s": sorted(set(implementation.values())),
        "independence_class": "SAME_IMPLEMENTATION",
        "item_results": [
            {"item_id": _item_id(record), "state": record["state"]}
            for record in ordered
        ],
        "kernel_unit_test_only": False,
        "li_figure_agreement_primary_gate": False,
        "limitations": [
            "full-domain algorithmic success does not substitute for full-domain arbitrary precision",
            "external BHPT and arbitrary-precision comparisons remain selected-domain certificates",
            "no detector, angular sum, paper-raster, or project-wide claim follows",
        ],
        "numerical_uncertainty_budget": numerical,
        "observable": "radial_s_matrix_flux",
        "observer_qualification": {
            "detector_response_claim_permitted": False,
            "output_kind": "RADIAL_S_MATRIX_ALGORITHMIC_BASELINE",
            "worldline_tetrad_pure_gauge_test": "NOT_ASSESSED",
        },
        "parameter_domain": {
            "description": "exact frozen D_union turning-aware radial baseline",
            "domain_id": (
                "final_turning_aware_d_union_17818"
                if full_domain
                else f"diagnostic_turning_aware_prefix_{len(records)}"
            ),
            "expected_item_ids": expected_ids,
            "expected_items": len(expected_ids),
            "parameters": {
                "D_union_sha256": EXPECTED_UNION_SHA256,
                "key_count": len(expected_ids),
            },
            "selection_policy": "exact ordered D_union or explicitly limited prefix",
        },
        "reason": (
            "all keys pass the repaired finite/flux/Jost-path invariants, with independent budgets still selected-domain"
            if not fail_count
            else "one or more keys fail a frozen full-domain algorithmic invariant"
        ),
        "result_id": (
            "phase6_v1_final_turning_aware_d_union_17818"
            if full_domain
            else f"phase6_v1_final_turning_prefix_{len(records)}"
        ),
        "role": "PRIMARY_SCIENCE",
        "schema": TYPED_RESULT_SCHEMA,
        "science_executed": True,
        "scientific_evidence": True,
        "state": result_state,
    }


def run_final_baseline_v2(
    *,
    output_root: str | Path,
    workers: int,
    resume: bool = False,
    limit: int | None = None,
) -> int:
    if workers < 1:
        raise V1FinalBaselineV2Error("workers must be positive")
    contract = load_frozen_scan_contract(DOMAIN_ROOT, EXECUTION_ROOT)
    all_keys = contract.union_keys
    if len(all_keys) != EXPECTED_KEY_COUNT:
        raise V1FinalBaselineV2Error("D_union cardinality changed")
    if limit is not None:
        if limit < 1 or limit > EXPECTED_KEY_COUNT:
            raise V1FinalBaselineV2Error("limit must lie in [1,17818]")
        keys = all_keys[:limit]
    else:
        keys = all_keys
    root = Path(output_root).absolute()
    if resume:
        if (
            root.is_symlink()
            or not root.is_dir()
            or stat.S_IMODE(root.stat().st_mode) != 0o700
        ):
            raise V1FinalBaselineV2Error("resume root must be direct mutable 0700")
    else:
        if root.exists() or root.is_symlink():
            raise V1FinalBaselineV2Error("fresh output root must be absent")
        root.mkdir(parents=True, mode=0o700)
        os.chmod(root, 0o700)
        _exclusive_json(root / "plan.json", _plan(len(keys), limit=limit))
    with _writer_lock(root):
        if json.loads((root / "plan.json").read_bytes()) != _plan(
            len(keys), limit=limit
        ):
            raise V1FinalBaselineV2Error("resume plan changed")
        records_path = root / "records.jsonl"
        records = _load_records(records_path, keys)
        started = time.monotonic()
        if len(records) < len(keys):
            flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            descriptor = os.open(records_path, flags, 0o600)
            try:
                with os.fdopen(descriptor, "ab", closefd=False) as handle:
                    payloads = (
                        (ordinal, keys[ordinal].to_record())
                        for ordinal in range(len(records), len(keys))
                    )
                    with ProcessPoolExecutor(max_workers=workers) as executor:
                        for record in executor.map(
                            _solve_key_v2, payloads, chunksize=1
                        ):
                            ordinal = len(records)
                            _validate_record(record, keys[ordinal], ordinal)
                            handle.write(canonical_jsonl_bytes(record))
                            handle.flush()
                            os.fsync(handle.fileno())
                            records.append(record)
            finally:
                os.close(descriptor)
        pass_count = sum(record["state"] == "PASS" for record in records)
        fail_count = len(records) - pass_count
        overall = (
            "PASS"
            if fail_count == 0 and len(keys) == EXPECTED_KEY_COUNT
            else "PARTIAL"
            if fail_count == 0
            else "FAIL"
        )
        selected_radii = [
            float(record["diagnostics"]["selected_r_out_M"])
            for record in records
            if record["state"] == "PASS"
        ]
        summary = {
            "acceptance_scope": "full D_union turning-aware/r_in-repaired algorithmic baseline",
            "completed_key_count": len(records),
            "elapsed_seconds_this_invocation": time.monotonic() - started,
            "failed_key_count": fail_count,
            "global_green_permitted": False,
            "li_figure_agreement_primary_gate": False,
            "numerical_state": "PASS" if fail_count == 0 else "FAIL",
            "overall_state": overall,
            "pass_key_count": pass_count,
            "records_sha256": sha256_file(records_path),
            "schema": SUMMARY_SCHEMA,
            "scientific_acceptance": False,
            "selected_r_out_counts": {
                format(radius, ".17g"): selected_radii.count(radius)
                for radius in sorted(set(selected_radii))
            },
        }
        os.chmod(records_path, FORMAL_FILE_MODE)
        os.chmod(root / "writer.lock", FORMAL_FILE_MODE)
        identities = {
            "plan.json": _identity(root / "plan.json", formal=True),
            "records.jsonl": _identity(records_path, formal=True),
            "writer.lock": _identity(root / "writer.lock", formal=True),
        }
        plan = json.loads((root / "plan.json").read_bytes())
        identities["summary.json"] = _exclusive_json(root / "summary.json", summary)
        identities["report.json"] = _exclusive_json(
            root / "report.json", _typed_report(records, summary, plan)
        )
        _exclusive_json(
            root / "manifest.json",
            {
                "artifacts": identities,
                "global_green_permitted": False,
                "overall_state": overall,
                "schema": MANIFEST_SCHEMA,
            },
        )
        os.chmod(root, FORMAL_ROOT_MODE)
    validate_published_final_baseline_v2(root)
    return 0 if overall in {"PASS", "PARTIAL"} else 2


def validate_published_final_baseline_v2(
    root_path: str | Path,
) -> dict[str, object]:
    root = Path(root_path).absolute()
    info = root.lstat()
    if (
        root.is_symlink()
        or root.resolve(strict=True) != root
        or not stat.S_ISDIR(info.st_mode)
        or stat.S_IMODE(info.st_mode) != FORMAL_ROOT_MODE
    ):
        raise V1FinalBaselineV2Error("v2 final-baseline root is not immutable 0555")
    manifest = json.loads((root / "manifest.json").read_bytes())
    if manifest.get("schema") != MANIFEST_SCHEMA or not isinstance(
        manifest.get("artifacts"), Mapping
    ):
        raise V1FinalBaselineV2Error("v2 manifest changed")
    artifacts = manifest["artifacts"]
    if {path.name for path in root.iterdir() if path.is_file()} != {
        *artifacts,
        "manifest.json",
    }:
        raise V1FinalBaselineV2Error("v2 artifact inventory changed")
    for name, expected in artifacts.items():
        if _identity(root / str(name), formal=True) != expected:
            raise V1FinalBaselineV2Error(f"v2 artifact identity changed: {name}")
    summary = json.loads((root / "summary.json").read_bytes())
    plan = json.loads((root / "plan.json").read_bytes())
    if summary.get("schema") != SUMMARY_SCHEMA or plan.get("schema") != PLAN_SCHEMA:
        raise V1FinalBaselineV2Error("v2 plan/summary schema changed")
    limit = plan.get("domain", {}).get("limit")
    count = plan.get("domain", {}).get("execution_count")
    if (
        isinstance(count, bool)
        or not isinstance(count, int)
        or (
            limit is not None
            and (isinstance(limit, bool) or not isinstance(limit, int))
        )
        or plan != _plan(count, limit=limit)
    ):
        raise V1FinalBaselineV2Error("v2 live plan/source/runtime identity changed")
    contract = load_frozen_scan_contract(DOMAIN_ROOT, EXECUTION_ROOT)
    records = _load_records(root / "records.jsonl", contract.union_keys[:count])
    if (
        len(records) != summary.get("completed_key_count")
        or sha256_file(root / "records.jsonl") != summary.get("records_sha256")
        or summary.get("global_green_permitted") is not False
        or json.loads((root / "report.json").read_bytes())
        != _typed_report(records, summary, plan)
    ):
        raise V1FinalBaselineV2Error("v2 summary linkage changed")
    return dict(summary)


__all__ = [
    "MANIFEST_SCHEMA",
    "PLAN_SCHEMA",
    "SUMMARY_SCHEMA",
    "V1FinalBaselineV2Error",
    "_solve_key_v2",
    "run_final_baseline_v2",
    "validate_published_final_baseline_v2",
]
