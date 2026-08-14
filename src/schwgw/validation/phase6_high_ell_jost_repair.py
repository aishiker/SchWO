"""Certify the Phase-6 V1 high-ell adaptive-Jost repair.

The immutable failed-domain boundary campaign contains two successful outer
radius nodes for each of the 230 residual failures.  This module validates that
source root, applies the generic basis-quality selector from
``adaptive_jost_radial``, and derives per-key radius and Jost-order numerical
budgets.  It never changes or overwrites predecessor evidence and it does not
turn same-equation convergence into independent scientific validation.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import hashlib
import json
import math
import os
from pathlib import Path
import stat
from typing import Any, Final

import numpy as np

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.numerics.adaptive_jost_radial import (
    JOST_CONDITION_NUMBER_LIMIT,
    JOST_RELATIVE_DETERMINANT_MINIMUM,
    JOST_SERIES_RESIDUAL_LIMIT,
    JOST_TAIL_RATIO_LIMIT,
    select_conditioned_outer_radius,
)
from schwgw.numerics.conditioned_radial import ConditionedRadialRequest
from schwgw.numerics.matching import outer_asymptotic_basis
from schwgw.perturbations import Sector
from schwgw.validation.phase6_radial_failure_boundary_ladders import (
    KEY_RECORD_SCHEMA as BOUNDARY_KEY_RECORD_SCHEMA,
    validate_terminal_root as validate_boundary_root,
)

REPORT_SCHEMA = "schwgw_phase6_v1_high_ell_adaptive_jost_repair_report_v1"
MANIFEST_SCHEMA = "schwgw_phase6_v1_high_ell_adaptive_jost_repair_manifest_v1"
RECORD_SCHEMA = "schwgw_phase6_v1_high_ell_adaptive_jost_repair_key_v1"
EXPECTED_REPAIR_KEY_COUNT: Final[int] = 230
EXPECTED_KM: Final[str] = "8"
EXPECTED_ELL_MINIMUM: Final[int] = 605
EXPECTED_ELL_MAXIMUM: Final[int] = 720
EXPECTED_MISSING_ELLS: Final[frozenset[int]] = frozenset({606})
FIXED_REQUIRED_RADIUS_M: Final[float] = 40.0
FIXED_RTOL: Final[float] = 1.0e-10
FIXED_ATOL: Final[float] = 1.0e-12
FIXED_JOST_ORDER: Final[int] = 160
COMPARISON_JOST_ORDER: Final[int] = 224

RADIUS_S_COMPLEX_GATE: Final[float] = 1.0e-6
RADIUS_S_PHASE_GATE_RAD: Final[float] = 1.0e-6
RADIUS_LOG_T_GATE: Final[float] = 1.0e-6
RADIUS_T_PHASE_GATE_RAD: Final[float] = 1.0e-6
JOST_S_COMPLEX_GATE: Final[float] = 1.0e-8
JOST_S_PHASE_GATE_RAD: Final[float] = 1.0e-8
JOST_LOG_T_GATE: Final[float] = 1.0e-8
JOST_T_PHASE_GATE_RAD: Final[float] = 1.0e-8
FLUX_RESIDUAL_GATE: Final[float] = 1.0e-8

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BOUNDARY_ROOT = (
    PROJECT_ROOT / "runs/phase6/radial_validation/"
    "v1_radial_failure_boundary_ladders_diagnostic_v1_20260809_py314"
)


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _identity(path: Path) -> dict[str, Any]:
    absolute = path.absolute()
    status = absolute.lstat()
    if (
        absolute.is_symlink()
        or not stat.S_ISREG(status.st_mode)
        or status.st_nlink != 1
    ):
        raise RuntimeError(f"identity source must be a regular nlink1 file: {absolute}")
    return {
        "mode": stat.S_IMODE(status.st_mode),
        "nlink": status.st_nlink,
        "path": str(absolute),
        "sha256": _sha256_file(absolute),
        "size": status.st_size,
    }


def _validate_identity(expected: Mapping[str, Any], path: Path) -> None:
    if dict(expected) != _identity(path):
        raise RuntimeError(f"file identity changed: {path}")


def _load_canonical_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict) or raw != _canonical_bytes(value):
        raise RuntimeError(f"non-canonical JSON object: {path}")
    return value


def _load_boundary_records(root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    validation = validate_boundary_root(root)
    records_path = root.resolve(strict=True) / "records.jsonl"
    records: list[dict[str, Any]] = []
    for ordinal, raw in enumerate(
        records_path.read_bytes().splitlines(keepends=True), 1
    ):
        try:
            record = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"invalid boundary JSONL record {ordinal}") from exc
        if not isinstance(record, dict) or raw != _canonical_bytes(record):
            raise RuntimeError(f"non-canonical boundary JSONL record {ordinal}")
        if record.get("schema") != BOUNDARY_KEY_RECORD_SCHEMA:
            raise RuntimeError("boundary record schema changed")
        records.append(record)
    if len(records) != int(validation["selected_key_count"]):
        raise RuntimeError("boundary record count changed")
    return records, validation


def _wrapped_phase_difference(left: float, right: float) -> float:
    return float(abs(math.atan2(math.sin(left - right), math.cos(left - right))))


def _complex(record: Mapping[str, Any]) -> complex:
    value = complex(float(record["real"]), float(record["imag"]))
    if not np.isfinite(value.real) or not np.isfinite(value.imag):
        raise RuntimeError("non-finite complex source observable")
    return value


def _observable_delta(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> dict[str, float]:
    left_s = _complex(left["S"])
    right_s = _complex(right["S"])
    return {
        "S_complex_abs": float(abs(left_s - right_s)),
        "S_modulus_abs": float(abs(abs(left_s) - abs(right_s))),
        "S_wrapped_phase_abs_rad": _wrapped_phase_difference(
            float(left["S"]["phase_rad"]),
            float(right["S"]["phase_rad"]),
        ),
        "log_abs_T_abs": float(
            abs(float(left["log_abs_T_horizon"]) - float(right["log_abs_T_horizon"]))
        ),
        "T_wrapped_phase_abs_rad": _wrapped_phase_difference(
            float(left["phase_T_horizon_rad"]),
            float(right["phase_T_horizon_rad"]),
        ),
        "maximum_flux_residual": float(
            max(
                float(left["flux"]["flux_residual"]),
                float(right["flux"]["flux_residual"]),
            )
        ),
    }


def _basis_pair(
    request: ConditionedRadialRequest,
    background: SchwarzschildBackground,
    *,
    r_out: float,
    order: int,
) -> tuple[Any, Any, np.ndarray]:
    incoming = outer_asymptotic_basis(
        sector=request.sector,
        ell=request.ell,
        r=r_out,
        k=request.k,
        background=background,
        sign=-1,
        basis=request.outer_basis,
        series_order=order,
    )
    outgoing = outer_asymptotic_basis(
        sector=request.sector,
        ell=request.ell,
        r=r_out,
        k=request.k,
        background=background,
        sign=1,
        basis=request.outer_basis,
        series_order=order,
    )
    matrix = np.asarray(
        [
            [incoming.psi, outgoing.psi],
            [incoming.dpsi_dr, outgoing.dpsi_dr],
        ],
        dtype=np.complex128,
    )
    return incoming, outgoing, matrix


def _jost_order_delta(
    request: ConditionedRadialRequest,
    background: SchwarzschildBackground,
    *,
    r_out: float,
    source_node: Mapping[str, Any],
) -> dict[str, Any]:
    incoming_160, outgoing_160, matrix_160 = _basis_pair(
        request,
        background,
        r_out=r_out,
        order=FIXED_JOST_ORDER,
    )
    incoming_224, outgoing_224, matrix_224 = _basis_pair(
        request,
        background,
        r_out=r_out,
        order=COMPARISON_JOST_ORDER,
    )
    reflection_160 = _complex(source_node["A_out"])
    state = matrix_160 @ np.asarray([1.0 + 0.0j, reflection_160])
    try:
        coefficients_224 = np.linalg.solve(matrix_224, state)
    except np.linalg.LinAlgError as exc:
        raise RuntimeError("224-order Jost rematch is singular") from exc
    incoming_coefficient_224 = complex(coefficients_224[0])
    if (
        not np.isfinite(incoming_coefficient_224.real)
        or not np.isfinite(incoming_coefficient_224.imag)
        or abs(incoming_coefficient_224) <= np.finfo(float).tiny
    ):
        raise RuntimeError("224-order incoming coefficient is unresolved")
    reflection_224 = complex(coefficients_224[1] / incoming_coefficient_224)
    parity = (-1) ** request.ell
    scattering_160 = -reflection_160 / parity
    scattering_224 = -reflection_224 / parity
    delta = {
        "S_complex_abs": float(abs(scattering_160 - scattering_224)),
        "S_modulus_abs": float(abs(abs(scattering_160) - abs(scattering_224))),
        "S_wrapped_phase_abs_rad": _wrapped_phase_difference(
            float(np.angle(scattering_160)),
            float(np.angle(scattering_224)),
        ),
        "log_abs_T_abs": float(abs(math.log(abs(incoming_coefficient_224)))),
        "T_wrapped_phase_abs_rad": float(abs(np.angle(incoming_coefficient_224))),
    }
    return {
        "orders": [FIXED_JOST_ORDER, COMPARISON_JOST_ORDER],
        "delta": delta,
        "basis_quality": {
            "order_160": {
                "maximum_series_residual": float(
                    max(incoming_160.series_residual, outgoing_160.series_residual)
                ),
                "maximum_tail_ratio": float(
                    max(incoming_160.tail_ratio, outgoing_160.tail_ratio)
                ),
                "condition_number": float(np.linalg.cond(matrix_160)),
            },
            "order_224": {
                "maximum_series_residual": float(
                    max(incoming_224.series_residual, outgoing_224.series_residual)
                ),
                "maximum_tail_ratio": float(
                    max(incoming_224.tail_ratio, outgoing_224.tail_ratio)
                ),
                "condition_number": float(np.linalg.cond(matrix_224)),
            },
        },
    }


def _passes_radius(delta: Mapping[str, float]) -> bool:
    return bool(
        delta["S_complex_abs"] <= RADIUS_S_COMPLEX_GATE
        and delta["S_wrapped_phase_abs_rad"] <= RADIUS_S_PHASE_GATE_RAD
        and delta["log_abs_T_abs"] <= RADIUS_LOG_T_GATE
        and delta["T_wrapped_phase_abs_rad"] <= RADIUS_T_PHASE_GATE_RAD
        and delta["maximum_flux_residual"] <= FLUX_RESIDUAL_GATE
    )


def _passes_jost(comparison: Mapping[str, Any]) -> bool:
    delta = comparison["delta"]
    quality = comparison["basis_quality"]
    return bool(
        delta["S_complex_abs"] <= JOST_S_COMPLEX_GATE
        and delta["S_wrapped_phase_abs_rad"] <= JOST_S_PHASE_GATE_RAD
        and delta["log_abs_T_abs"] <= JOST_LOG_T_GATE
        and delta["T_wrapped_phase_abs_rad"] <= JOST_T_PHASE_GATE_RAD
        and quality["order_160"]["maximum_series_residual"]
        <= JOST_SERIES_RESIDUAL_LIMIT
        and quality["order_160"]["maximum_tail_ratio"] <= JOST_TAIL_RATIO_LIMIT
        and quality["order_160"]["condition_number"] <= JOST_CONDITION_NUMBER_LIMIT
        and quality["order_224"]["condition_number"] <= JOST_CONDITION_NUMBER_LIMIT
    )


def derive_repair_record(
    source: Mapping[str, Any],
    *,
    source_records_sha256: str,
) -> dict[str, Any]:
    """Derive one conservative repair result from a validated source record."""

    if source.get("ladder_summary", {}).get("state") != "FAIL":
        raise RuntimeError("repair source is not a residual failed key")
    key = source["key"]
    if str(key["kM"]) != EXPECTED_KM:
        raise RuntimeError("residual repair escaped the frozen kM=8 domain")
    request = ConditionedRadialRequest(
        sector=Sector(str(key["sector"])),
        ell=int(key["ell"]),
        k=float(key["kM"]),
        required_radius=FIXED_REQUIRED_RADIUS_M,
        r_out=float(source["selected_r_out_M"]),
        rtol=FIXED_RTOL,
        atol=FIXED_ATOL,
        outer_series_order=FIXED_JOST_ORDER,
    )
    background = SchwarzschildBackground(M=1.0)
    selection = select_conditioned_outer_radius(request, background)
    if selection.selected_radius_factor not in {2.0, 4.0}:
        raise RuntimeError("frozen high-ell repair selected an unexpected radius")

    nodes = {node["node"]["node_id"]: node for node in source["nodes"]}
    node_600 = nodes.get("r_out_x2")
    node_1200 = nodes.get("r_out_x4")
    if (
        not isinstance(node_600, Mapping)
        or not isinstance(node_1200, Mapping)
        or node_600.get("status") != "MEASURED"
        or node_1200.get("status") != "MEASURED"
    ):
        raise RuntimeError("high-ell repair source lacks measured radius nodes")
    selected_node = node_600 if selection.selected_radius_factor == 2.0 else node_1200
    if float(selected_node["request"]["r_out_M"]) != selection.selected_r_out_M:
        raise RuntimeError("selector and source radius node disagree")

    radius_delta = _observable_delta(node_600, node_1200)
    jost_comparison = _jost_order_delta(
        request,
        background,
        r_out=selection.selected_r_out_M,
        source_node=selected_node,
    )
    radius_state = "PASS" if _passes_radius(radius_delta) else "FAIL"
    jost_state = "PASS" if _passes_jost(jost_comparison) else "FAIL"
    flux_state = (
        "PASS"
        if float(selected_node["flux"]["flux_residual"]) <= FLUX_RESIDUAL_GATE
        else "FAIL"
    )
    numerical_state = (
        "PASS" if {radius_state, jost_state, flux_state} == {"PASS"} else "FAIL"
    )
    overall_state = "PARTIAL" if numerical_state == "PASS" else "FAIL"
    return {
        "schema": RECORD_SCHEMA,
        "source_record_ordinal": int(source["ordinal"]),
        "source_records_sha256": source_records_sha256,
        "key": dict(key),
        "key_id": str(source["key_id"]),
        "predecessor_state": "FAIL",
        "predecessor_failure": "scaled-tortoise incoming Jost coefficient is unresolved",
        "adaptive_selection": selection.as_record(),
        "selected_source_node_id": str(selected_node["node"]["node_id"]),
        "selected_observables": {
            "S": dict(selected_node["S"]),
            "A_out": dict(selected_node["A_out"]),
            "log_abs_T_horizon": float(selected_node["log_abs_T_horizon"]),
            "phase_T_horizon_rad": float(selected_node["phase_T_horizon_rad"]),
            "flux": dict(selected_node["flux"]),
        },
        "radius_ladder": {
            "radii_M": [600.0, 1200.0],
            "delta": radius_delta,
            "state": radius_state,
        },
        "jost_order_ladder": {**jost_comparison, "state": jost_state},
        "numerical_uncertainty_budget": {
            "state": numerical_state,
            "radius_ladder": radius_state,
            "jost_order": jost_state,
            "flux_conservation": flux_state,
            "arithmetic_precision": "NOT_ASSESSED_FOR_THIS_EXACT_KEY",
            "independent_backend": "NOT_ASSESSED",
        },
        "convention_uncertainty_budget": {
            "state": "NOT_ASSESSED",
            "upper_bound": None,
            "frozen_fourier_convention": "exp(-i k t)",
            "frozen_tortoise_origin": "r_star=r+2*log(r/2-1), M=1",
            "external_absolute_phase_crosscheck": "NOT_ASSESSED",
        },
        "overall_state": overall_state,
        "algorithmic_failure_repaired": numerical_state == "PASS",
        "same_equation_same_implementation_family": True,
        "independent_scientific_validation": False,
        "scientific_acceptance": False,
        "global_green_permitted": False,
    }


def _source_identities(runner_path: Path) -> dict[str, Any]:
    paths = {
        "adaptive_backend": PROJECT_ROOT
        / "src/schwgw/numerics/adaptive_jost_radial.py",
        "base_scaled_tortoise_backend_v1": PROJECT_ROOT
        / "src/schwgw/numerics/scaled_tortoise_radial.py",
        "jost_matching": PROJECT_ROOT / "src/schwgw/numerics/matching.py",
        "certifier": Path(__file__).resolve(strict=True),
        "publisher": runner_path.resolve(strict=True),
    }
    return {name: _identity(path) for name, path in paths.items()}


def _inventory_sha256(records: Sequence[Mapping[str, Any]]) -> str:
    return hashlib.sha256(
        _canonical_bytes([str(record["key_id"]) for record in records])
    ).hexdigest()


def _maximum_with_key(
    records: Sequence[Mapping[str, Any]],
    *,
    section: str,
    field: str,
) -> dict[str, Any]:
    selected = max(
        records,
        key=lambda record: float(record[section]["delta"][field]),
    )
    return {
        "key_id": selected["key_id"],
        "value": float(selected[section]["delta"][field]),
    }


def build_repair_report(
    *,
    boundary_root: Path = DEFAULT_BOUNDARY_ROOT,
    runner_path: Path,
) -> dict[str, Any]:
    """Build a deterministic report from immutable predecessor evidence."""

    boundary = boundary_root.resolve(strict=True)
    source_records, validation = _load_boundary_records(boundary)
    residual = [
        record
        for record in source_records
        if record.get("ladder_summary", {}).get("state") == "FAIL"
    ]
    if len(residual) != EXPECTED_REPAIR_KEY_COUNT:
        raise RuntimeError("residual high-ell inventory count changed")
    sectors = Counter(str(record["key"]["sector"]) for record in residual)
    ells_by_sector = {
        sector: {
            int(record["key"]["ell"])
            for record in residual
            if str(record["key"]["sector"]) == sector
        }
        for sector in ("even", "odd")
    }
    ells = [int(record["key"]["ell"]) for record in residual]
    expected_ells = (
        set(range(EXPECTED_ELL_MINIMUM, EXPECTED_ELL_MAXIMUM + 1))
        - EXPECTED_MISSING_ELLS
    )
    if (
        sectors != {"even": 115, "odd": 115}
        or min(ells) != EXPECTED_ELL_MINIMUM
        or max(ells) != EXPECTED_ELL_MAXIMUM
        or any(values != expected_ells for values in ells_by_sector.values())
    ):
        raise RuntimeError("residual high-ell domain changed")
    source_records_identity = _identity(boundary / "records.jsonl")
    repaired = [
        derive_repair_record(
            record,
            source_records_sha256=source_records_identity["sha256"],
        )
        for record in residual
    ]
    state_counts = Counter(str(record["overall_state"]) for record in repaired)
    selected_factors = Counter(
        str(record["adaptive_selection"]["selected_radius_factor"])
        for record in repaired
    )
    numerical_failures = sum(
        record["numerical_uncertainty_budget"]["state"] != "PASS" for record in repaired
    )
    overall_state = "PARTIAL" if numerical_failures == 0 else "FAIL"
    return {
        "schema": REPORT_SCHEMA,
        "report_id": "phase6_v1_high_ell_adaptive_jost_repair_20260810",
        "scope": {
            "observable": "radial S-matrix and horizon transmission log/phase",
            "domain_role": "extended kM=8 high-ell validation slice",
            "kM": EXPECTED_KM,
            "ell_minimum": EXPECTED_ELL_MINIMUM,
            "ell_maximum": EXPECTED_ELL_MAXIMUM,
            "excluded_ell_values": sorted(EXPECTED_MISSING_ELLS),
            "sectors": ["even", "odd"],
            "key_count": EXPECTED_REPAIR_KEY_COUNT,
            "production_finite_radius_states": "NOT_ASSESSED",
            "paper_figure_runs": 0,
        },
        "source_boundary_validation": validation,
        "source_artifact_identities": {
            "run_contract": _identity(boundary / "run_contract.json"),
            "records": source_records_identity,
            "summary": _identity(boundary / "summary.json"),
            "manifest": _identity(boundary / "manifest.json"),
        },
        "implementation_source_identities": _source_identities(runner_path),
        "repair_policy": {
            "selector": "first passing radius in factors [1,2,4,8]",
            "paper_specific_envelope_used": False,
            "requested_r_out_M": 300.0,
            "jost_series_order": FIXED_JOST_ORDER,
            "comparison_jost_series_order": COMPARISON_JOST_ORDER,
            "basis_gates": {
                "maximum_series_residual": JOST_SERIES_RESIDUAL_LIMIT,
                "maximum_tail_ratio": JOST_TAIL_RATIO_LIMIT,
                "maximum_condition_number": JOST_CONDITION_NUMBER_LIMIT,
                "minimum_relative_determinant": JOST_RELATIVE_DETERMINANT_MINIMUM,
            },
            "observable_gates": {
                "radius_S_complex_abs": RADIUS_S_COMPLEX_GATE,
                "radius_S_phase_abs_rad": RADIUS_S_PHASE_GATE_RAD,
                "radius_log_abs_T_abs": RADIUS_LOG_T_GATE,
                "radius_T_phase_abs_rad": RADIUS_T_PHASE_GATE_RAD,
                "jost_S_complex_abs": JOST_S_COMPLEX_GATE,
                "jost_S_phase_abs_rad": JOST_S_PHASE_GATE_RAD,
                "jost_log_abs_T_abs": JOST_LOG_T_GATE,
                "jost_T_phase_abs_rad": JOST_T_PHASE_GATE_RAD,
                "flux_residual": FLUX_RESIDUAL_GATE,
            },
        },
        "key_inventory_sha256": _inventory_sha256(repaired),
        "records": repaired,
        "aggregate": {
            "key_count": len(repaired),
            "state_counts": dict(sorted(state_counts.items())),
            "selected_radius_factor_counts": dict(sorted(selected_factors.items())),
            "algorithmic_failure_repaired_count": sum(
                bool(record["algorithmic_failure_repaired"]) for record in repaired
            ),
            "numerical_failure_count": numerical_failures,
            "maximum_radius_S_complex_abs": _maximum_with_key(
                repaired,
                section="radius_ladder",
                field="S_complex_abs",
            ),
            "maximum_radius_S_phase_abs_rad": _maximum_with_key(
                repaired,
                section="radius_ladder",
                field="S_wrapped_phase_abs_rad",
            ),
            "maximum_radius_log_abs_T_abs": _maximum_with_key(
                repaired,
                section="radius_ladder",
                field="log_abs_T_abs",
            ),
            "maximum_jost_S_complex_abs": _maximum_with_key(
                repaired,
                section="jost_order_ladder",
                field="S_complex_abs",
            ),
            "maximum_jost_S_phase_abs_rad": _maximum_with_key(
                repaired,
                section="jost_order_ladder",
                field="S_wrapped_phase_abs_rad",
            ),
            "maximum_jost_log_abs_T_abs": _maximum_with_key(
                repaired,
                section="jost_order_ladder",
                field="log_abs_T_abs",
            ),
        },
        "numerical_uncertainty_budget": {
            "state": "PASS" if numerical_failures == 0 else "FAIL",
            "coverage": f"{len(repaired)}/{EXPECTED_REPAIR_KEY_COUNT}",
            "r_out_ladder": "PASS" if numerical_failures == 0 else "FAIL",
            "jost_order": "PASS" if numerical_failures == 0 else "FAIL",
            "flux_conservation": "PASS" if numerical_failures == 0 else "FAIL",
            "arithmetic_precision": "NOT_ASSESSED_FOR_EXACT_230_KEY_DOMAIN",
            "independent_backend": "NOT_ASSESSED",
        },
        "convention_uncertainty_budget": {
            "state": "NOT_ASSESSED",
            "upper_bound": None,
            "absolute_phase_convention": "FROZEN_NOT_EXTERNALLY_CROSSCHECKED",
        },
        "overall_state": overall_state,
        "algorithmic_failure_repaired": numerical_failures == 0,
        "source_science_executed": True,
        "publisher_generated_science": False,
        "same_equation_same_implementation_family": True,
        "independent_scientific_validation": False,
        "scientific_acceptance": False,
        "limitations": [
            "the 60/80-dps mpmath checks are selected implementation-family anchors, not these exact 230 keys",
            "the external BHPT-direct run timed out and supplies no exact-key comparison",
            "absolute phase and observer/tetrad conventions are not independently cross-checked here",
        ],
        "li_figure_agreement_primary_gate": False,
        "global_green_permitted": False,
    }


def _write_exclusive(path: Path, value: Mapping[str, Any]) -> None:
    payload = _canonical_bytes(value)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("exclusive evidence write made no progress")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def publish_repair_evidence(
    *,
    output_root: Path,
    runner_path: Path,
    boundary_root: Path = DEFAULT_BOUNDARY_ROOT,
) -> dict[str, Any]:
    """Publish once to a fresh root and independently reload it."""

    absolute = output_root.absolute()
    parent = absolute.parent.resolve(strict=True)
    root = parent / absolute.name
    if root.exists() or root.is_symlink():
        raise RuntimeError("fresh repair evidence root already exists")
    report = build_repair_report(boundary_root=boundary_root, runner_path=runner_path)
    os.mkdir(root, mode=0o700)
    try:
        report_path = root / "repair_report.json"
        _write_exclusive(report_path, report)
        report_path.chmod(0o444)
        manifest = {
            "schema": MANIFEST_SCHEMA,
            "status": "COMPLETE",
            "global_green_permitted": False,
            "report_identity": _identity(report_path),
        }
        manifest_path = root / "manifest.json"
        _write_exclusive(manifest_path, manifest)
        manifest_path.chmod(0o444)
        root.chmod(0o555)
        _fsync_directory(root)
        _fsync_directory(parent)
    except Exception:
        # Preserve a failed fresh root for audit; never delete or overwrite it.
        raise
    return validate_published_repair_evidence(
        root,
        boundary_root=boundary_root,
        runner_path=runner_path,
    )


def validate_published_repair_evidence(
    root: Path,
    *,
    boundary_root: Path = DEFAULT_BOUNDARY_ROOT,
    runner_path: Path,
) -> dict[str, Any]:
    """Reload all claims and rebuild the deterministic report."""

    resolved = root.resolve(strict=True)
    if resolved.is_symlink() or stat.S_IMODE(resolved.stat().st_mode) != 0o555:
        raise RuntimeError("published repair root must be a direct 0555 directory")
    expected_files = {"manifest.json", "repair_report.json"}
    if {path.name for path in resolved.iterdir()} != expected_files:
        raise RuntimeError("published repair root inventory changed")
    for path in resolved.iterdir():
        identity = _identity(path)
        if identity["mode"] != 0o444 or identity["nlink"] != 1:
            raise RuntimeError("published repair artifact mode/link changed")
    report = _load_canonical_json(resolved / "repair_report.json")
    manifest = _load_canonical_json(resolved / "manifest.json")
    expected_report = build_repair_report(
        boundary_root=boundary_root,
        runner_path=runner_path,
    )
    if report != expected_report:
        raise RuntimeError("published repair report does not rebuild exactly")
    expected_manifest = {
        "schema": MANIFEST_SCHEMA,
        "status": "COMPLETE",
        "global_green_permitted": False,
        "report_identity": _identity(resolved / "repair_report.json"),
    }
    if manifest != expected_manifest:
        raise RuntimeError("published repair manifest changed")
    return {
        "root": str(resolved),
        "overall_state": report["overall_state"],
        "key_count": report["aggregate"]["key_count"],
        "algorithmic_failure_repaired_count": report["aggregate"][
            "algorithmic_failure_repaired_count"
        ],
        "selected_radius_factor_counts": report["aggregate"][
            "selected_radius_factor_counts"
        ],
        "report_sha256": _sha256_file(resolved / "repair_report.json"),
        "manifest_sha256": _sha256_file(resolved / "manifest.json"),
    }


__all__ = [
    "DEFAULT_BOUNDARY_ROOT",
    "EXPECTED_REPAIR_KEY_COUNT",
    "MANIFEST_SCHEMA",
    "RECORD_SCHEMA",
    "REPORT_SCHEMA",
    "build_repair_report",
    "derive_repair_record",
    "publish_repair_evidence",
    "validate_published_repair_evidence",
]
