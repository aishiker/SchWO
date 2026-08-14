from __future__ import annotations

import argparse
import hashlib
import json
import time
import warnings
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
from schwgw.io.tablei import TABLEI_POINTS
from schwgw.numerics import BoundaryConfig, solve_radial_mode
from schwgw.numerics.experimental.q018_rescaled_oracle import (
    RescaledOracleRequest,
    solve_q018_rescaled_oracle,
)
from schwgw.perturbations import Sector


SCHEMA_VERSION = "phase5_t4z_delta0p1_radial_gate_v1"
CHECKPOINT_SCHEMA_VERSION = "phase5_t4z_delta0p1_radial_checkpoint_v1"
PREFLIGHT_SCHEMA_VERSION = "phase5_t4z_delta0p1_radial_preflight_v1"
FREQUENCIES = (0.4, 0.8, 0.9, 1.6, 1.7, 2.8, 2.9, 3.8, 3.9)
LMAX_VALUES = {
    0.4: (24, 36, 60, 84),
    0.8: (24, 36, 60, 84),
    0.9: (24, 36, 60, 84),
    1.6: (72, 96, 120, 144),
    1.7: (84, 108, 132, 156),
    2.8: (180, 204, 228, 252),
    2.9: (192, 216, 240, 264),
    3.8: (276, 300, 324, 348),
    3.9: (288, 312, 336, 360),
}
BOUNDARY = {
    "r_out": 300.0,
    "r_in_eps": 1e-6,
    "rtol": 1e-10,
    "atol": 1e-12,
}
OUTPUT_DIR = Path("runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate")
CHECKPOINT_DIR = OUTPUT_DIR / "checkpoint"
CLASSIFICATION_PATH = OUTPUT_DIR / "classification_manifest.json"
ORACLE_PATH = OUTPUT_DIR / "oracle_validation.json"
PREFLIGHT_PATH = OUTPUT_DIR / "resume_preflight.json"
ENVELOPE_PATH = Path("src/schwgw/numerics/q018_delta0p1_risk_envelope.py")
ADAPTER_NAME = "q018_tablei_delta0p1_risk_pilot_transition"
ADAPTER_SOLVER = "q018_tablei_delta0p1_risk_pilot_transition_oracle"
ADAPTER_WARNING = "q018_tablei_delta0p1_risk_pilot_transition_oracle_used"

DEFAULT_COVERED = "default_covered"
FAIL_UNCOVERED = "default_fail_closed_uncovered"
FAIL_SOLVER = "default_fail_closed_solver_failed"
FAIL_OTHER = "default_error_other"
STRUCTURED_CLASSES = (FAIL_UNCOVERED, FAIL_SOLVER)

SELECTED_SOURCE_PATHS = (
    Path("src/schwgw/numerics/radial_solver.py"),
    Path("src/schwgw/numerics/experimental/q018_rescaled_oracle.py"),
    Path("src/schwgw/io/tablei.py"),
    Path("scripts/phase5_delta0p1_risk_radial_gate.py"),
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def _atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)


def _atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected a JSON object in {path}")
    return payload


def _source_hashes() -> dict[str, str]:
    return {str(path): _sha256(path) for path in SELECTED_SOURCE_PATHS}


def _point_contract() -> list[dict[str, Any]]:
    return [
        {
            "point_id": point.point_id,
            "r": point.r,
            "x": point.x,
            "y": point.y,
            "z": point.z,
            "theta": point.theta,
            "phi": point.phi,
        }
        for point in TABLEI_POINTS
    ]


def _frequency_token(k: float) -> str:
    return f"{k:.1f}".replace(".", "p")


def _checkpoint_path(k: float) -> Path:
    return CHECKPOINT_DIR / f"kM_{_frequency_token(k)}.json"


def _contract_payload(k: float, source_hashes: Mapping[str, str]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "frequency": k,
        "frequencies": list(FREQUENCIES),
        "lmax_values": list(LMAX_VALUES[k]),
        "ell_min": 2,
        "ell_max": max(LMAX_VALUES[k]),
        "sectors": [Sector.ODD.value, Sector.EVEN.value],
        "points": _point_contract(),
        "boundary": dict(BOUNDARY),
        "source_hashes": dict(source_hashes),
        "classification_labels": [
            DEFAULT_COVERED,
            FAIL_UNCOVERED,
            FAIL_SOLVER,
            FAIL_OTHER,
        ],
    }


def _checkpoint_matches(payload: Mapping[str, Any], contract_sha256: str) -> bool:
    return (
        payload.get("schema_version") == CHECKPOINT_SCHEMA_VERSION
        and payload.get("contract_sha256") == contract_sha256
        and payload.get("complete") is True
        and payload.get("decision") == "PASS"
    )


def _quarantine(path: Path) -> Path:
    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    destination = path.with_name(path.name + f".quarantine.{timestamp}")
    counter = 1
    while destination.exists():
        destination = path.with_name(
            path.name + f".quarantine.{timestamp}.{counter}"
        )
        counter += 1
    path.replace(destination)
    return destination


def _complex_payload(value: complex) -> list[float]:
    return [float(value.real), float(value.imag)]


def _payload_complex(value: Sequence[float]) -> complex:
    return complex(float(value[0]), float(value[1]))


def _finite_complex(value: complex) -> bool:
    return bool(np.isfinite(value.real) and np.isfinite(value.imag))


def _exception_metadata(exc: RuntimeError) -> dict[str, Any]:
    message = str(exc)
    if "metadata=" not in message:
        return {"message": message, "metadata_parse_error": True}
    try:
        payload = json.loads(message.split("metadata=", 1)[1])
    except json.JSONDecodeError:
        return {"message": message, "metadata_parse_error": True}
    if not isinstance(payload, dict):
        return {"message": message, "metadata_parse_error": True}
    return payload


def _classify_default_record(
    *,
    background: SchwarzschildBackground,
    k: float,
    ell: int,
    sector: Sector,
    point_id: str,
    required_radius: float,
) -> dict[str, Any]:
    config = BoundaryConfig(
        r_in_eps=BOUNDARY["r_in_eps"],
        r_out=BOUNDARY["r_out"],
        rtol=BOUNDARY["rtol"],
        atol=BOUNDARY["atol"],
        required_eval_radius=required_radius,
    )
    base = {
        "k": k,
        "ell": ell,
        "sector": sector.value,
        "point_id": point_id,
        "required_eval_radius": required_radius,
    }
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=".*(overflow encountered|invalid value encountered).*",
                category=RuntimeWarning,
            )
            solution = solve_radial_mode(sector, ell, k, background, config)
        psi = complex(solution.psi_at(required_radius))
        dpsi_dr = complex(solution.dpsi_dr_at(required_radius))
        finite = all(
            _finite_complex(value)
            for value in (psi, dpsi_dr, solution.A_in, solution.A_out)
        )
        if not finite:
            return {
                **base,
                "classification": FAIL_OTHER,
                "error_metadata": {
                    "code": "default_nonfinite_solution",
                    "solver": solution.diagnostics.solver,
                },
            }
        return {
            **base,
            "classification": DEFAULT_COVERED,
            "solver": solution.diagnostics.solver,
            "valid_until_r": solution.valid_until_r,
            "boundary_residual": float(solution.diagnostics.boundary_residual),
            "wronskian_residual": float(solution.diagnostics.wronskian_residual),
            "flux_residual": float(solution.diagnostics.flux_residual),
            "match_condition_number": float(
                solution.diagnostics.match_condition_number
            ),
            "warning_codes": [
                warning.code for warning in solution.diagnostics.warnings
            ],
        }
    except RuntimeError as exc:
        metadata = _exception_metadata(exc)
        code = metadata.get("code")
        if code == "evanescent_tail_required_radius_uncovered":
            classification = FAIL_UNCOVERED
        elif code == "evanescent_tail_required_radius_solver_failed":
            classification = FAIL_SOLVER
        else:
            classification = FAIL_OTHER
        return {
            **base,
            "classification": classification,
            "error_metadata": metadata,
        }
    except Exception as exc:  # noqa: BLE001 - classify all unexpected failures
        return {
            **base,
            "classification": FAIL_OTHER,
            "error_metadata": {
                "code": "default_unstructured_exception",
                "exception_type": type(exc).__name__,
                "message": str(exc),
            },
        }


def _oracle_request(
    *,
    sector: Sector,
    ell: int,
    k: float,
    required_radius: float,
    precision_dps: int = 80,
    rtol: float | None = None,
    atol: float | None = None,
) -> RescaledOracleRequest:
    return RescaledOracleRequest(
        sector=sector,
        ell=ell,
        k=k,
        required_radius=required_radius,
        r_out=BOUNDARY["r_out"],
        r_in_eps=BOUNDARY["r_in_eps"],
        rtol=BOUNDARY["rtol"] if rtol is None else rtol,
        atol=BOUNDARY["atol"] if atol is None else atol,
        precision_dps=precision_dps,
        method_hint="rescaled_log_amplitude",
    )


def _validate_oracle_record(
    *,
    background: SchwarzschildBackground,
    default_record: Mapping[str, Any],
) -> dict[str, Any]:
    sector = Sector(str(default_record["sector"]))
    request = _oracle_request(
        sector=sector,
        ell=int(default_record["ell"]),
        k=float(default_record["k"]),
        required_radius=float(default_record["required_eval_radius"]),
    )
    try:
        result = solve_q018_rescaled_oracle(request, background)
    except Exception as exc:  # noqa: BLE001 - scientific gate records exact failure
        return {
            **{key: default_record[key] for key in (
                "k",
                "ell",
                "sector",
                "point_id",
                "required_eval_radius",
                "classification",
            )},
            "oracle_validated": False,
            "error": f"{type(exc).__name__}: {exc}",
        }
    diagnostics = dict(result.diagnostics)
    outer = float(diagnostics["outer_boundary_residual"])
    normalization = float(diagnostics["normalization_residual"])
    log_match = float(diagnostics["log_derivative_match_residual"])
    effective = max(outer, normalization, log_match)
    finite = all(
        _finite_complex(value)
        for value in (result.psi, result.dpsi_dr, result.A_in, result.A_out)
    )
    validated = bool(
        result.valid_at_required_radius
        and finite
        and abs(result.A_in - 1.0) < 1e-8
        and effective < 1e-7
        and outer < 1e-8
        and normalization < 1e-8
    )
    return {
        **{key: default_record[key] for key in (
            "k",
            "ell",
            "sector",
            "point_id",
            "required_eval_radius",
            "classification",
        )},
        "oracle_validated": validated,
        "valid_at_required_radius": bool(result.valid_at_required_radius),
        "finite_psi": _finite_complex(result.psi),
        "finite_dpsi_dr": _finite_complex(result.dpsi_dr),
        "finite_A_in": _finite_complex(result.A_in),
        "finite_A_out": _finite_complex(result.A_out),
        "psi": _complex_payload(result.psi),
        "dpsi_dr": _complex_payload(result.dpsi_dr),
        "A_in": _complex_payload(result.A_in),
        "A_out": _complex_payload(result.A_out),
        "abs_A_in_minus_one": float(abs(result.A_in - 1.0)),
        "outer_boundary_residual": outer,
        "normalization_residual": normalization,
        "log_derivative_match_residual": log_match,
        "effective_residual": effective,
        "match_condition_number": float(diagnostics["match_condition_number"]),
        "requested_precision_dps": int(diagnostics["requested_precision_dps"]),
        "actual_precision_bits": int(diagnostics["actual_precision_bits"]),
        "actual_decimal_digits": float(diagnostics["actual_decimal_digits"]),
        "precision_note": str(diagnostics["precision_note"]),
        "runtime_seconds": float(diagnostics["runtime_seconds"]),
    }


def _relative_complex(value: complex, reference: complex) -> float:
    return float(abs(value - reference) / max(abs(reference), np.finfo(float).eps))


def _sensitivity_record(
    *,
    background: SchwarzschildBackground,
    base: Mapping[str, Any],
) -> dict[str, Any]:
    sector = Sector(str(base["sector"]))
    common = {
        "sector": sector,
        "ell": int(base["ell"]),
        "k": float(base["k"]),
        "required_radius": float(base["required_eval_radius"]),
    }
    variants = {
        "dps70": _oracle_request(**common, precision_dps=70),
        "dps80": _oracle_request(**common, precision_dps=80),
        "dps100": _oracle_request(**common, precision_dps=100),
        "loose": _oracle_request(
            **common,
            precision_dps=80,
            rtol=1e-9,
            atol=1e-11,
        ),
        "tight": _oracle_request(
            **common,
            precision_dps=80,
            rtol=1e-11,
            atol=1e-13,
        ),
    }
    results = {
        name: solve_q018_rescaled_oracle(request, background)
        for name, request in variants.items()
    }
    reference = results["dps80"]
    comparisons: dict[str, dict[str, float]] = {}
    maximum = 0.0
    for name, result in results.items():
        values = {
            "rel_psi": _relative_complex(result.psi, reference.psi),
            "rel_dpsi_dr": _relative_complex(result.dpsi_dr, reference.dpsi_dr),
            "rel_A_out": _relative_complex(result.A_out, reference.A_out),
        }
        maximum = max(maximum, *values.values())
        comparisons[name] = values
    return {
        "k": common["k"],
        "ell": common["ell"],
        "sector": sector.value,
        "point_id": str(base["point_id"]),
        "required_eval_radius": common["required_radius"],
        "requested_precision_dps": [70, 80, 100],
        "actual_precision_note": str(reference.diagnostics["precision_note"]),
        "comparisons_to_dps80": comparisons,
        "max_relative_sensitivity": maximum,
        "passed": maximum < 5e-6,
    }


def _select_sensitivity_anchors(
    records: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    if not records:
        return []
    ordered = sorted(
        records,
        key=lambda item: (
            int(item["ell"]),
            str(item["point_id"]),
            str(item["sector"]),
        ),
    )
    indices = sorted({0, len(ordered) // 2, len(ordered) - 1})
    return [ordered[index] for index in indices]


def _run_frequency(
    *,
    k: float,
    source_hashes: Mapping[str, str],
) -> dict[str, Any]:
    started = time.perf_counter()
    background = SchwarzschildBackground(M=1.0)
    records: list[dict[str, Any]] = []
    ell_max = max(LMAX_VALUES[k])
    print(
        f"T4Z frequency kM={k:.1f}: classifying ell=2..{ell_max}",
        flush=True,
    )
    for ell in range(2, ell_max + 1):
        for sector in (Sector.ODD, Sector.EVEN):
            for point in TABLEI_POINTS:
                records.append(
                    _classify_default_record(
                        background=background,
                        k=k,
                        ell=ell,
                        sector=sector,
                        point_id=point.point_id,
                        required_radius=point.r,
                    )
                )
        if ell == ell_max or ell % 12 == 0:
            counts = Counter(record["classification"] for record in records)
            print(
                f"T4Z kM={k:.1f} ell={ell}/{ell_max} "
                f"records={len(records)} counts={dict(sorted(counts.items()))}",
                flush=True,
            )

    counts = Counter(record["classification"] for record in records)
    transition_records = [
        record
        for record in records
        if record["classification"] in STRUCTURED_CLASSES
    ]
    oracle_records: list[dict[str, Any]] = []
    if counts[FAIL_OTHER] == 0:
        print(
            f"T4Z kM={k:.1f}: validating {len(transition_records)} transitions",
            flush=True,
        )
        for index, record in enumerate(transition_records, start=1):
            oracle_records.append(
                _validate_oracle_record(background=background, default_record=record)
            )
            if index == len(transition_records) or index % 50 == 0:
                print(
                    f"T4Z kM={k:.1f} oracle={index}/{len(transition_records)}",
                    flush=True,
                )

    sensitivity_records: list[dict[str, Any]] = []
    if counts[FAIL_OTHER] == 0 and all(
        record["oracle_validated"] for record in oracle_records
    ):
        for anchor in _select_sensitivity_anchors(oracle_records):
            sensitivity_records.append(
                _sensitivity_record(background=background, base=anchor)
            )

    expected_record_count = (ell_max - 1) * 2 * len(TABLEI_POINTS)
    scientific_pass = bool(
        len(records) == expected_record_count
        and counts[FAIL_OTHER] == 0
        and len(oracle_records) == len(transition_records)
        and all(record["oracle_validated"] for record in oracle_records)
        and all(record["passed"] for record in sensitivity_records)
    )
    contract = _contract_payload(k, source_hashes)
    return {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "complete": True,
        "decision": "PASS" if scientific_pass else "FAIL",
        "frequency": k,
        "contract": contract,
        "contract_sha256": _canonical_sha256(contract),
        "source_hashes": dict(source_hashes),
        "records": records,
        "oracle_records": oracle_records,
        "sensitivity_records": sensitivity_records,
        "summary": {
            "ell_min": 2,
            "ell_max": ell_max,
            "expected_record_count": expected_record_count,
            "actual_record_count": len(records),
            "counts_by_classification": dict(sorted(counts.items())),
            "transition_record_count": len(transition_records),
            "oracle_validated_count": sum(
                bool(record["oracle_validated"]) for record in oracle_records
            ),
            "sensitivity_record_count": len(sensitivity_records),
            "max_relative_sensitivity": max(
                (
                    float(record["max_relative_sensitivity"])
                    for record in sensitivity_records
                ),
                default=0.0,
            ),
            "runtime_seconds": time.perf_counter() - started,
        },
    }


def _transition_key(record: Mapping[str, Any]) -> tuple[float, int, str, str]:
    return (
        float(record["k"]),
        int(record["ell"]),
        str(record["point_id"]),
        str(record["sector"]),
    )


def _compress_transition_records(
    records: Sequence[Mapping[str, Any]],
) -> dict[float, tuple[tuple[int, int, tuple[str, ...]], ...]]:
    sectors_by_mode: dict[tuple[float, int, str], set[str]] = defaultdict(set)
    for record in records:
        key = (float(record["k"]), int(record["ell"]), str(record["point_id"]))
        sectors_by_mode[key].add(str(record["sector"]))
    required_sectors = {Sector.ODD.value, Sector.EVEN.value}
    asymmetric = [
        key for key, sectors in sectors_by_mode.items() if sectors != required_sectors
    ]
    if asymmetric:
        raise RuntimeError(
            "transition sector symmetry required by frozen envelope interface; "
            f"first asymmetric records={asymmetric[:5]}"
        )

    point_order = {point.point_id: index for index, point in enumerate(TABLEI_POINTS)}
    points_by_k_ell: dict[tuple[float, int], set[str]] = defaultdict(set)
    for k, ell, point_id in sectors_by_mode:
        points_by_k_ell[(k, ell)].add(point_id)

    compressed: dict[float, tuple[tuple[int, int, tuple[str, ...]], ...]] = {}
    for k in FREQUENCIES:
        items = [
            (
                ell,
                tuple(sorted(point_ids, key=point_order.__getitem__)),
            )
            for (frequency, ell), point_ids in points_by_k_ell.items()
            if frequency == k
        ]
        items.sort()
        segments: list[tuple[int, int, tuple[str, ...]]] = []
        for ell, point_ids in items:
            if segments and ell == segments[-1][1] + 1 and point_ids == segments[-1][2]:
                previous = segments[-1]
                segments[-1] = (previous[0], ell, point_ids)
            else:
                segments.append((ell, ell, point_ids))
        compressed[k] = tuple(segments)

    expanded = {
        (k, ell, point_id, sector)
        for k, segments in compressed.items()
        for ell_min, ell_max, point_ids in segments
        for ell in range(ell_min, ell_max + 1)
        for point_id in point_ids
        for sector in (Sector.ODD.value, Sector.EVEN.value)
    }
    raw = {_transition_key(record) for record in records}
    if expanded != raw:
        raise RuntimeError(
            "compressed transition segments do not exactly reproduce raw records; "
            f"missing={len(raw - expanded)} extra={len(expanded - raw)}"
        )
    return compressed


def _write_envelope_module(
    *,
    segments: Mapping[float, tuple[tuple[int, int, tuple[str, ...]], ...]],
    classification_sha256: str,
    oracle_validation_sha256: str,
) -> None:
    points = tuple((point.point_id, point.r) for point in TABLEI_POINTS)
    lines = [
        '"""Generated immutable T4z Delta0p1 risk-pilot Q018 envelope."""',
        "",
        "from __future__ import annotations",
        "",
        f"FREQUENCIES: tuple[float, ...] = {FREQUENCIES!r}",
        f"POINTS: tuple[tuple[str, float], ...] = {points!r}",
        "TRANSITION_SEGMENTS: dict[",
        "    float, tuple[tuple[int, int, tuple[str, ...]], ...]",
        "] = {",
    ]
    for k in FREQUENCIES:
        lines.append(f"    {k!r}: {segments[k]!r},")
    lines.extend(
        [
            "}",
            f'CLASSIFICATION_SHA256: str = "{classification_sha256}"',
            f'ORACLE_VALIDATION_SHA256: str = "{oracle_validation_sha256}"',
            "",
            "__all__ = [",
            '    "FREQUENCIES",',
            '    "POINTS",',
            '    "TRANSITION_SEGMENTS",',
            '    "CLASSIFICATION_SHA256",',
            '    "ORACLE_VALIDATION_SHA256",',
            "]",
            "",
        ]
    )
    _atomic_text(ENVELOPE_PATH, "\n".join(lines))


def _aggregate(checkpoints: Sequence[Mapping[str, Any]]) -> None:
    classification_records = [
        record for checkpoint in checkpoints for record in checkpoint["records"]
    ]
    oracle_records = [
        record
        for checkpoint in checkpoints
        for record in checkpoint["oracle_records"]
    ]
    sensitivity_records = [
        record
        for checkpoint in checkpoints
        for record in checkpoint["sensitivity_records"]
    ]
    transitions = [
        record
        for record in classification_records
        if record["classification"] in STRUCTURED_CLASSES
    ]
    segments = _compress_transition_records(transitions)
    counts = Counter(record["classification"] for record in classification_records)
    source_hashes = dict(checkpoints[0]["source_hashes"])
    classification = {
        "schema_version": SCHEMA_VERSION,
        "thread": "T4z",
        "stage": "classification",
        "decision_candidate": "GREEN / DELTA0P1 RISK-PILOT RADIAL GATE READY",
        "inputs": {
            "frequencies": list(FREQUENCIES),
            "lmax_values": {str(k): list(LMAX_VALUES[k]) for k in FREQUENCIES},
            "boundary": dict(BOUNDARY),
            "sectors": [Sector.ODD.value, Sector.EVEN.value],
            "points": _point_contract(),
        },
        "source_hashes": source_hashes,
        "checkpoint_sha256": {
            str(checkpoint["frequency"]): _sha256(
                _checkpoint_path(float(checkpoint["frequency"]))
            )
            for checkpoint in checkpoints
        },
        "records": classification_records,
        "transition_records": transitions,
        "transition_segments": {
            str(k): [
                [ell_min, ell_max, list(point_ids)]
                for ell_min, ell_max, point_ids in segments[k]
            ]
            for k in FREQUENCIES
        },
        "summary": {
            "total_records": len(classification_records),
            "counts_by_classification": dict(sorted(counts.items())),
            "default_error_other_count": counts[FAIL_OTHER],
            "transition_record_count": len(transitions),
            "frequency_count": len(FREQUENCIES),
            "checkpoint_count": len(checkpoints),
            "runtime_seconds": sum(
                float(checkpoint["summary"]["runtime_seconds"])
                for checkpoint in checkpoints
            ),
        },
        "non_artifact_statement": {
            "radial_only": True,
            "no_tablei_amplification": True,
            "no_t8": True,
            "no_kirchhoff": True,
            "no_plotting": True,
            "not_40_frequency_production": True,
        },
    }
    _atomic_json(CLASSIFICATION_PATH, classification)

    oracle_summary = {
        "total_records": len(oracle_records),
        "oracle_validated": sum(
            bool(record["oracle_validated"]) for record in oracle_records
        ),
        "max_abs_A_in_minus_one": max(
            (float(record["abs_A_in_minus_one"]) for record in oracle_records),
            default=0.0,
        ),
        "max_effective_residual": max(
            (float(record["effective_residual"]) for record in oracle_records),
            default=0.0,
        ),
        "max_outer_boundary_residual": max(
            (float(record["outer_boundary_residual"]) for record in oracle_records),
            default=0.0,
        ),
        "max_normalization_residual": max(
            (float(record["normalization_residual"]) for record in oracle_records),
            default=0.0,
        ),
        "max_log_derivative_match_residual": max(
            (
                float(record["log_derivative_match_residual"])
                for record in oracle_records
            ),
            default=0.0,
        ),
        "max_match_condition_number": max(
            (float(record["match_condition_number"]) for record in oracle_records),
            default=0.0,
        ),
        "sensitivity_record_count": len(sensitivity_records),
        "max_relative_sensitivity": max(
            (
                float(record["max_relative_sensitivity"])
                for record in sensitivity_records
            ),
            default=0.0,
        ),
    }
    oracle = {
        "schema_version": SCHEMA_VERSION,
        "thread": "T4z",
        "stage": "oracle_validation",
        "classification_sha256": _sha256(CLASSIFICATION_PATH),
        "source_hashes": source_hashes,
        "records": oracle_records,
        "sensitivity_records": sensitivity_records,
        "summary": oracle_summary,
        "non_artifact_statement": classification["non_artifact_statement"],
    }
    _atomic_json(ORACLE_PATH, oracle)
    _write_envelope_module(
        segments=segments,
        classification_sha256=_sha256(CLASSIFICATION_PATH),
        oracle_validation_sha256=_sha256(ORACLE_PATH),
    )


def _run_classification() -> None:
    source_hashes = _source_hashes()
    checkpoints: list[dict[str, Any]] = []
    for k in FREQUENCIES:
        contract_sha256 = _canonical_sha256(_contract_payload(k, source_hashes))
        path = _checkpoint_path(k)
        if path.exists():
            checkpoint = _load_json(path)
            if _checkpoint_matches(checkpoint, contract_sha256):
                print(f"T4Z kM={k:.1f}: reused exact PASS checkpoint", flush=True)
                checkpoints.append(checkpoint)
                continue
            quarantined = _quarantine(path)
            print(f"T4Z kM={k:.1f}: quarantined {quarantined}", flush=True)
        checkpoint = _run_frequency(k=k, source_hashes=source_hashes)
        _atomic_json(path, checkpoint)
        print(
            f"T4Z kM={k:.1f}: checkpoint decision={checkpoint['decision']} "
            f"sha256={_sha256(path)}",
            flush=True,
        )
        if checkpoint["decision"] != "PASS":
            raise RuntimeError(
                f"T4z scientific gate stopped at kM={k:.1f}; "
                "checkpoint decision is FAIL"
            )
        checkpoints.append(checkpoint)
    _aggregate(checkpoints)
    _audit()


def _audit() -> None:
    classification = _load_json(CLASSIFICATION_PATH)
    oracle = _load_json(ORACLE_PATH)
    checkpoints = [_load_json(_checkpoint_path(k)) for k in FREQUENCIES]
    expected_total = sum(
        (max(LMAX_VALUES[k]) - 1) * 2 * len(TABLEI_POINTS) for k in FREQUENCIES
    )
    records = classification["records"]
    transitions = classification["transition_records"]
    oracle_records = oracle["records"]
    if len(checkpoints) != len(FREQUENCIES):
        raise RuntimeError("checkpoint cardinality mismatch")
    if any(checkpoint["decision"] != "PASS" for checkpoint in checkpoints):
        raise RuntimeError("a frequency checkpoint is not PASS")
    if len(records) != expected_total:
        raise RuntimeError(
            f"classification cardinality mismatch: {len(records)} != {expected_total}"
        )
    if classification["summary"]["default_error_other_count"] != 0:
        raise RuntimeError("default_error_other_count is nonzero")
    if len(transitions) != len(oracle_records):
        raise RuntimeError("transition/oracle cardinality mismatch")
    if {_transition_key(record) for record in transitions} != {
        _transition_key(record) for record in oracle_records
    }:
        raise RuntimeError("transition/oracle record sets differ")
    if not all(record["oracle_validated"] for record in oracle_records):
        raise RuntimeError("at least one oracle record failed validation")
    _compress_transition_records(transitions)
    print(
        "T4Z_CLASSIFICATION_AND_ORACLE_AUDIT=PASS "
        f"records={len(records)} transitions={len(transitions)} "
        f"checkpoints={len(checkpoints)}",
        flush=True,
    )


def _oracle_map() -> dict[tuple[float, int, str, str], Mapping[str, Any]]:
    oracle = _load_json(ORACLE_PATH)
    return {_transition_key(record): record for record in oracle["records"]}


def _run_preflight() -> None:
    from schwgw.numerics.q018_delta0p1_risk_envelope import (
        CLASSIFICATION_SHA256,
        ORACLE_VALIDATION_SHA256,
    )

    if _sha256(CLASSIFICATION_PATH) != CLASSIFICATION_SHA256:
        raise RuntimeError("classification hash does not match generated envelope")
    if _sha256(ORACLE_PATH) != ORACLE_VALIDATION_SHA256:
        raise RuntimeError("oracle-validation hash does not match generated envelope")
    classification = _load_json(CLASSIFICATION_PATH)
    oracle_by_key = _oracle_map()
    transitions = classification["transition_records"]
    background = SchwarzschildBackground(M=1.0)
    preflight_records: list[dict[str, Any]] = []
    started = time.perf_counter()
    counts_by_k = Counter(float(record["k"]) for record in transitions)
    completed_by_k: Counter[float] = Counter()
    for index, record in enumerate(transitions, start=1):
        k = float(record["k"])
        sector = Sector(str(record["sector"]))
        radius = float(record["required_eval_radius"])
        config = BoundaryConfig(
            r_in_eps=BOUNDARY["r_in_eps"],
            r_out=BOUNDARY["r_out"],
            rtol=BOUNDARY["rtol"],
            atol=BOUNDARY["atol"],
            required_eval_radius=radius,
            experimental_required_radius_oracle=ADAPTER_NAME,
        )
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=".*(overflow encountered|invalid value encountered).*",
                category=RuntimeWarning,
            )
            solution = solve_radial_mode(
                sector,
                int(record["ell"]),
                k,
                background,
                config,
            )
        warning_metadata = [
            warning.to_metadata() for warning in solution.diagnostics.warnings
        ]
        adapter_warnings = [
            warning
            for warning in warning_metadata
            if warning["code"] == ADAPTER_WARNING
        ]
        direct = oracle_by_key[_transition_key(record)]
        psi = complex(solution.psi_at(radius))
        dpsi_dr = complex(solution.dpsi_dr_at(radius))
        rel_psi = _relative_complex(psi, _payload_complex(direct["psi"]))
        rel_dpsi_dr = _relative_complex(
            dpsi_dr,
            _payload_complex(direct["dpsi_dr"]),
        )
        rel_A_out = _relative_complex(
            solution.A_out,
            _payload_complex(direct["A_out"]),
        )
        passed = bool(
            solution.diagnostics.solver == ADAPTER_SOLVER
            and len(adapter_warnings) == 1
            and adapter_warnings[0].get("review_grid_point_id")
            == record["point_id"]
            and adapter_warnings[0].get("experimental_required_radius_oracle")
            == ADAPTER_NAME
            and all(_finite_complex(value) for value in (psi, dpsi_dr, solution.A_out))
            and rel_psi < 1e-12
            and rel_dpsi_dr < 1e-12
            and rel_A_out < 1e-12
            and solution.diagnostics.wronskian_residual < 1e-7
            and solution.diagnostics.boundary_residual < 1e-8
        )
        preflight_records.append(
            {
                "k": k,
                "ell": int(record["ell"]),
                "sector": sector.value,
                "point_id": str(record["point_id"]),
                "required_eval_radius": radius,
                "solver": solution.diagnostics.solver,
                "warning_code": adapter_warnings[0]["code"]
                if len(adapter_warnings) == 1
                else "",
                "relative_psi": rel_psi,
                "relative_dpsi_dr": rel_dpsi_dr,
                "relative_A_out": rel_A_out,
                "effective_residual": float(solution.diagnostics.wronskian_residual),
                "boundary_residual": float(solution.diagnostics.boundary_residual),
                "match_condition_number": float(
                    solution.diagnostics.match_condition_number
                ),
                "passed": passed,
            }
        )
        completed_by_k[k] += 1
        if index == len(transitions) or index % 50 == 0:
            print(
                f"T4Z preflight={index}/{len(transitions)} "
                f"kM={k:.1f} frequency={completed_by_k[k]}/{counts_by_k[k]}",
                flush=True,
            )
    failures = [record for record in preflight_records if not record["passed"]]
    payload = {
        "schema_version": PREFLIGHT_SCHEMA_VERSION,
        "thread": "T4z",
        "stage": "resume_preflight",
        "adapter_name": ADAPTER_NAME,
        "classification_sha256": _sha256(CLASSIFICATION_PATH),
        "oracle_validation_sha256": _sha256(ORACLE_PATH),
        "records": preflight_records,
        "failures": failures,
        "summary": {
            "transition_records_expected": len(transitions),
            "adapter_validated": len(preflight_records) - len(failures),
            "failures": len(failures),
            "max_relative_psi": max(
                (record["relative_psi"] for record in preflight_records),
                default=0.0,
            ),
            "max_relative_dpsi_dr": max(
                (record["relative_dpsi_dr"] for record in preflight_records),
                default=0.0,
            ),
            "max_relative_A_out": max(
                (record["relative_A_out"] for record in preflight_records),
                default=0.0,
            ),
            "max_effective_residual": max(
                (record["effective_residual"] for record in preflight_records),
                default=0.0,
            ),
            "max_boundary_residual": max(
                (record["boundary_residual"] for record in preflight_records),
                default=0.0,
            ),
            "max_match_condition_number": max(
                (
                    record["match_condition_number"]
                    for record in preflight_records
                ),
                default=0.0,
            ),
            "runtime_seconds": time.perf_counter() - started,
        },
        "non_artifact_statement": {
            "radial_only": True,
            "no_tablei_amplification": True,
            "no_t8": True,
            "no_kirchhoff": True,
            "no_plotting": True,
            "not_40_frequency_production": True,
        },
    }
    _atomic_json(PREFLIGHT_PATH, payload)
    if failures:
        raise RuntimeError(f"resume preflight has {len(failures)} failures")
    print(
        "T4Z_RESUME_PREFLIGHT=PASS "
        f"records={len(preflight_records)} sha256={_sha256(PREFLIGHT_PATH)}",
        flush=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the frozen T4z Delta0p1 radial/Q018 gate."
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Audit existing classification/oracle/checkpoint artifacts.",
    )
    parser.add_argument(
        "--resume-preflight",
        action="store_true",
        help="Validate every measured transition through the integrated adapter.",
    )
    args = parser.parse_args()
    if args.audit and args.resume_preflight:
        parser.error("choose only one of --audit or --resume-preflight")
    if args.audit:
        _audit()
    elif args.resume_preflight:
        _run_preflight()
    else:
        _run_classification()


if __name__ == "__main__":
    main()
