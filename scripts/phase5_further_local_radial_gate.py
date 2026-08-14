from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
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


SCHEMA_VERSION = "phase5_t4ab_further_local_radial_gate_v1"
CHECKPOINT_SCHEMA_VERSION = "phase5_t4ab_further_local_radial_checkpoint_v1"
PREFLIGHT_SCHEMA_VERSION = "phase5_t4ab_further_local_radial_preflight_v1"
FREQUENCIES = (
    0.325, 0.375, 0.825, 0.875, 0.925, 0.975,
    1.525, 1.575, 1.625, 1.675, 1.7125, 1.7375,
    2.7625, 2.7875, 2.825, 2.875, 2.925, 2.975,
    3.7625, 3.7875, 3.825, 3.875, 3.925, 3.975,
)
FREQUENCY_TOKENS = {
    k: str(k).replace(".", "p") for k in FREQUENCIES
}
LMAX_VALUES = {
    0.325: (24, 36, 60, 84), 0.375: (24, 36, 60, 84),
    0.825: (24, 36, 60, 84), 0.875: (24, 36, 60, 84),
    0.925: (24, 36, 60, 84), 0.975: (24, 48, 72, 96),
    1.525: (72, 96, 120, 144), 1.575: (72, 96, 120, 144),
    1.625: (84, 108, 132, 156), 1.675: (84, 108, 132, 156),
    1.7125: (84, 108, 132, 156), 1.7375: (96, 120, 144, 168),
    2.7625: (180, 204, 228, 252), 2.7875: (180, 204, 228, 252),
    2.825: (192, 216, 240, 264), 2.875: (192, 216, 240, 264),
    2.925: (192, 216, 240, 264), 2.975: (204, 228, 252, 276),
    3.7625: (276, 300, 324, 348), 3.7875: (276, 300, 324, 348),
    3.825: (276, 300, 324, 348), 3.875: (288, 312, 336, 360),
    3.925: (288, 312, 336, 360), 3.975: (288, 312, 336, 360),
}
BOUNDARY = {
    "r_out": 300.0,
    "r_in_eps": 1e-6,
    "rtol": 1e-10,
    "atol": 1e-12,
}
OUTPUT_DIR = Path("runs/phase5/fig5_fig6_further_local_radial_gate")
CHECKPOINT_DIR = OUTPUT_DIR / "checkpoint"
CLASSIFICATION_PATH = OUTPUT_DIR / "classification_manifest.json"
ORACLE_PATH = OUTPUT_DIR / "oracle_validation.json"
PREFLIGHT_PATH = OUTPUT_DIR / "resume_preflight.json"
MANIFEST_PATH = OUTPUT_DIR / "manifest.md"
ENVELOPE_PATH = Path("src/schwgw/numerics/q018_further_local_envelope.py")
ADAPTER_NAME = "q018_tablei_further_local_transition"
ADAPTER_SOLVER = "q018_tablei_further_local_transition_oracle"
ADAPTER_WARNING = "q018_tablei_further_local_transition_oracle_used"

DEFAULT_COVERED = "default_covered"
FAIL_UNCOVERED = "default_fail_closed_uncovered"
FAIL_SOLVER = "default_fail_closed_solver_failed"
FAIL_OTHER = "default_error_other"
STRUCTURED_CLASSES = (FAIL_UNCOVERED, FAIL_SOLVER)

CLASSIFICATION_SOURCE_PATHS = (
    Path("src/schwgw/numerics/radial_solver.py"),
    Path("src/schwgw/numerics/experimental/q018_rescaled_oracle.py"),
    Path("src/schwgw/io/tablei.py"),
    Path("scripts/phase5_further_local_radial_gate.py"),
    Path(
        "docs/superpowers/specs/"
        "2026-07-16-t4ab-t8aq-further-local-refinement-design.md"
    ),
    Path(
        "docs/superpowers/plans/"
        "2026-07-16-t4ab-further-local-radial-gate.md"
    ),
    Path("docs/prompts/phase5_t4ab_further_local_radial_gate.md"),
)
FROZEN_INPUT_HASHES = {
    Path("runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz"): "a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb",
    Path("runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json"): "2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537",
    Path("runs/phase5/fig5_fig6_dense_review_grid/manifest.md"): "86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf",
    Path("runs/phase5/fig5_fig6_delta0p1_risk_pilot/checkpoint_ledger.json"): "8729ad80043a1837793264b101a776a08e92191c7856cf792ed34683b743859e",
    Path("runs/phase5/fig5_fig6_delta0p1_risk_pilot/risk_pilot_values.npz"): "69cf9812ddd51d6486f854b77b76d202c281d719041cc07e8e87c1af9bd973f7",
    Path("runs/phase5/fig5_fig6_delta0p1_risk_pilot/risk_pilot_values.npz.json"): "b812a4325b9afca91ee360b68dc3e959115f2d992fba21b60cf70a7ad3ce3566",
    Path("runs/phase5/fig5_fig6_delta0p1_risk_pilot/risk_pilot_sampling_audit.json"): "7e1e8646bfa51b09cd96ee301e8847fdc830128d7eca7ac770031bc7b13ce42b",
    Path("runs/phase5/fig5_fig6_delta0p1_risk_pilot/manifest.md"): "27301b9f300563a5feb654b48d9ef11ca8eb1e10f9c065c805534adfb27bfd78",
    Path("runs/phase5/fig5_fig6_targeted_adaptive_radial_gate/classification_manifest.json"): "aa3af55cd8454d610ebcd31fd8bbda5d37522a9a4e2279c8622decf3459a1b83",
    Path("runs/phase5/fig5_fig6_targeted_adaptive_radial_gate/oracle_validation.json"): "002889f81ebce0574b948912217bf1231add3411253855db71adf2769b441d02",
    Path("runs/phase5/fig5_fig6_targeted_adaptive_radial_gate/resume_preflight.json"): "a39bacfea6f2728129fde71b791c6f4f18eba05b34e9fa7dcf49b8b64d9824d4",
    Path("runs/phase5/fig5_fig6_targeted_adaptive_radial_gate/manifest.md"): "a796e4c34af8a80f800ec1f9ebc04089e4b3af9d79a190bc5a733b7c9f4c85d8",
    Path("docs/handoffs/T7_current.md"): "8edd808e543460f943eb217af248b2edd52d7ea7d1827e99315b4f49f6521d9e",
    Path("runs/phase5/fig5_fig6_targeted_adaptive_refinement/adaptive_refinement_values.npz"): "ec6328ad5b9acfdd341a00877a7aaf355d49a0d39db1569f3e488b34b9980f17",
    Path("runs/phase5/fig5_fig6_targeted_adaptive_refinement/adaptive_refinement_values.npz.json"): "9d9c821ab8c7f5af1ceb5136451e859a41bccd5456fe3beee834b876ffdc38cc",
    Path("runs/phase5/fig5_fig6_targeted_adaptive_refinement/adaptive_sampling_audit.json"): "4606960110b658b74894c1b82a604c333481290ca0c451f3013574906eea5d67",
    Path("runs/phase5/fig5_fig6_targeted_adaptive_refinement/checkpoint_ledger.json"): "2dfcaa7802ed8c7e3b3225429bb8b312d651441f378719331d023a5adb1e1caf",
    Path("runs/phase5/fig5_fig6_targeted_adaptive_refinement/manifest.md"): "b728b1f5b4d45e622d5bebc32e710ac2be786556ab1ee7b7d9f26ca545223e5c",
    Path("docs/superpowers/specs/2026-07-16-t4ab-t8aq-further-local-refinement-design.md"): "88fa71a39606b9b37ea202a0e16d25af7a2e4597bce0c697df02c57a666c365b",
    Path("docs/superpowers/plans/2026-07-16-t4ab-further-local-radial-gate.md"): "7812fe2062cd04d494c1ed427c2bf37bb036c8864ab4f0330b96ceb928c5ce0a",
    Path("docs/superpowers/plans/2026-07-16-t8aq-further-local-refinement.md"): "56891ef34f168a05e43806d7177ca721c10180483224c75ef95df5a1e118b56b",
    Path("docs/prompts/phase5_t4ab_further_local_radial_gate.md"): "2e6dbb5508d800442b0cfec9e89c5de4daacfe34abbd475963fabeae24727e3e",
    Path("docs/prompts/phase5_t7ca_further_local_radial_review.md"): "132e6ec9cca4d91fbcef38d1354ee0e9028f2d30de73e308b8acb1ed1571cb85",
    Path("docs/prompts/phase5_t8aq_further_local_refinement.md"): "ad34bc2338fadcc51685b499910ff13a4ecda5f7567af186f0d39bc99f33f354",
    Path("docs/prompts/phase5_t7cb_further_local_refinement_review.md"): "99f03928c2b3e51d2cd30614d6401fb4da81375a99fa08bf330fdb2d4459e10b",
}
IMPLEMENTATION_PATHS = (
    Path("scripts/phase5_further_local_radial_gate.py"),
    Path("src/schwgw/numerics/q018_further_local_envelope.py"),
    Path("src/schwgw/numerics/radial_solver.py"),
    Path("tests/physics/test_q018_production_integration_design.py"),
    Path("tests/physics/test_radial_solver.py"),
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def _verify_frozen_inputs() -> dict[str, str]:
    actual = {str(path): _sha256(path) for path in FROZEN_INPUT_HASHES}
    mismatches = {
        str(path): {"expected": expected, "actual": actual[str(path)]}
        for path, expected in FROZEN_INPUT_HASHES.items()
        if actual[str(path)] != expected
    }
    if mismatches:
        raise RuntimeError(
            "frozen input hash mismatch: "
            f"{json.dumps(mismatches, sort_keys=True)}"
        )
    return actual


def _global_contract(frozen_input_hashes: Mapping[str, str]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "frequencies": list(FREQUENCIES),
        "frequency_tokens": {
            str(k): FREQUENCY_TOKENS[k] for k in FREQUENCIES
        },
        "lmax_values": {str(k): list(LMAX_VALUES[k]) for k in FREQUENCIES},
        "ell_min": 2,
        "sectors": [Sector.ODD.value, Sector.EVEN.value],
        "points": _point_contract(),
        "boundary": dict(BOUNDARY),
        "classification_labels": [
            DEFAULT_COVERED,
            FAIL_UNCOVERED,
            FAIL_SOLVER,
            FAIL_OTHER,
        ],
        "expected_record_count": 81_792,
        "frozen_input_hashes": dict(frozen_input_hashes),
    }


def _classification_snapshot(
    frozen_input_hashes: Mapping[str, str],
) -> dict[str, Any]:
    payload = {
        "schema_version": "phase5_t4ab_classification_snapshot_v1",
        "source_hashes": {
            str(path): _sha256(path) for path in CLASSIFICATION_SOURCE_PATHS
        },
        "input_contract": _global_contract(frozen_input_hashes),
    }
    return {"payload": payload, "sha256": _canonical_sha256(payload)}


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
    return FREQUENCY_TOKENS[k]


def _checkpoint_path(k: float) -> Path:
    return CHECKPOINT_DIR / f"kM_{_frequency_token(k)}.json"


def _contract_payload(
    k: float,
    classification_snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "frequency": k,
        "frequency_token": FREQUENCY_TOKENS[k],
        "lmax_values": list(LMAX_VALUES[k]),
        "ell_min": 2,
        "ell_max": max(LMAX_VALUES[k]),
        "sectors": [Sector.ODD.value, Sector.EVEN.value],
        "points": _point_contract(),
        "boundary": dict(BOUNDARY),
        "classification_snapshot_sha256": classification_snapshot["sha256"],
        "classification_labels": [
            DEFAULT_COVERED,
            FAIL_UNCOVERED,
            FAIL_SOLVER,
            FAIL_OTHER,
        ],
    }


def _checkpoint_output_sha256(payload: Mapping[str, Any]) -> str:
    content = dict(payload)
    content.pop("output_sha256", None)
    return _canonical_sha256(content)


def _checkpoint_matches(
    payload: Mapping[str, Any],
    *,
    k: float,
    contract: Mapping[str, Any],
    classification_snapshot: Mapping[str, Any],
) -> bool:
    expected_count = (max(LMAX_VALUES[k]) - 1) * 2 * len(TABLEI_POINTS)
    records = payload.get("records")
    oracle_records = payload.get("oracle_records")
    sensitivity_records = payload.get("sensitivity_records")
    if not isinstance(records, list):
        return False
    if not isinstance(oracle_records, list) or not isinstance(
        sensitivity_records, list
    ):
        return False
    keys = {
        (
            float(record.get("k", float("nan"))),
            str(record.get("sector", "")),
            int(record.get("ell", -1)),
            str(record.get("point_id", "")),
        )
        for record in records
    }
    expected_keys = {
        (k, sector.value, ell, point.point_id)
        for sector in (Sector.ODD, Sector.EVEN)
        for ell in range(2, max(LMAX_VALUES[k]) + 1)
        for point in TABLEI_POINTS
    }
    transition_keys = {
        _transition_key(record)
        for record in records
        if record.get("classification") in STRUCTURED_CLASSES
    }
    oracle_keys = {_transition_key(record) for record in oracle_records}
    return bool(
        payload.get("schema_version") == CHECKPOINT_SCHEMA_VERSION
        and payload.get("contract") == contract
        and payload.get("contract_sha256") == _canonical_sha256(contract)
        and payload.get("classification_snapshot") == classification_snapshot
        and payload.get("classification_snapshot_sha256")
        == classification_snapshot["sha256"]
        and payload.get("complete") is True
        and payload.get("decision") == "PASS"
        and payload.get("output_sha256") == _checkpoint_output_sha256(payload)
        and len(records) == expected_count
        and keys == expected_keys
        and all(
            record.get("classification")
            in {DEFAULT_COVERED, FAIL_UNCOVERED, FAIL_SOLVER, FAIL_OTHER}
            for record in records
        )
        and not any(
            record.get("classification") == FAIL_OTHER for record in records
        )
        and transition_keys == oracle_keys
        and len(oracle_records) == len(transition_keys)
        and all(record.get("oracle_validated") is True for record in oracle_records)
        and all(record.get("passed") is True for record in sensitivity_records)
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
        "actual_precision_bits": {
            name: int(result.diagnostics["actual_precision_bits"])
            for name, result in results.items()
        },
        "actual_decimal_digits": {
            name: float(result.diagnostics["actual_decimal_digits"])
            for name, result in results.items()
        },
        "actual_precision_note": str(reference.diagnostics["precision_note"]),
        "variant_contracts": {
            name: {
                "requested_precision_dps": int(request.precision_dps or 0),
                "rtol": float(request.rtol),
                "atol": float(request.atol),
            }
            for name, request in variants.items()
        },
        "comparisons_to_dps80": comparisons,
        "max_relative_sensitivity": maximum,
        "passed": maximum < 5e-6,
    }


def _select_sensitivity_anchors(
    records: Sequence[Mapping[str, Any]],
) -> tuple[list[Mapping[str, Any]], list[dict[str, Any]]]:
    anchors: list[Mapping[str, Any]] = []
    groups: list[dict[str, Any]] = []
    for sector in (Sector.ODD, Sector.EVEN):
        ordered = sorted(
            (record for record in records if record["sector"] == sector.value),
            key=lambda item: (int(item["ell"]), str(item["point_id"])),
        )
        selected: list[Mapping[str, Any]] = []
        if ordered:
            selected.extend((ordered[0], ordered[-1]))
            covered_points = {str(record["point_id"]) for record in selected}
            for point in TABLEI_POINTS:
                if point.point_id in covered_points:
                    continue
                first = next(
                    (
                        record
                        for record in ordered
                        if record["point_id"] == point.point_id
                    ),
                    None,
                )
                if first is not None:
                    selected.append(first)
                    covered_points.add(point.point_id)
        deduplicated = {
            _transition_key(record): record for record in selected
        }
        ordered_selected = [deduplicated[key] for key in sorted(deduplicated)]
        anchors.extend(ordered_selected)
        groups.append(
            {
                "sector": sector.value,
                "transition_count": len(ordered),
                "anchor_keys": [
                    list(_transition_key(record)) for record in ordered_selected
                ],
            }
        )
    return anchors, groups


def _run_frequency(
    *,
    k: float,
    classification_snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    started = time.perf_counter()
    background = SchwarzschildBackground(M=1.0)
    records: list[dict[str, Any]] = []
    ell_max = max(LMAX_VALUES[k])
    print(
        f"T4AB frequency kM={k:.17g}: classifying ell=2..{ell_max}",
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
                f"T4AB kM={k:.17g} ell={ell}/{ell_max} "
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
            f"T4AB kM={k:.17g}: validating {len(transition_records)} transitions",
            flush=True,
        )
        for index, record in enumerate(transition_records, start=1):
            oracle_records.append(
                _validate_oracle_record(background=background, default_record=record)
            )
            if index == len(transition_records) or index % 50 == 0:
                print(
                    f"T4AB kM={k:.17g} oracle={index}/{len(transition_records)}",
                    flush=True,
                )

    sensitivity_records: list[dict[str, Any]] = []
    anchors, sensitivity_anchor_groups = _select_sensitivity_anchors(
        oracle_records
    )
    if counts[FAIL_OTHER] == 0 and all(
        record["oracle_validated"] for record in oracle_records
    ):
        for anchor in anchors:
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
    contract = _contract_payload(k, classification_snapshot)
    payload = {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "complete": True,
        "decision": "PASS" if scientific_pass else "FAIL",
        "frequency": k,
        "contract": contract,
        "contract_sha256": _canonical_sha256(contract),
        "classification_snapshot": dict(classification_snapshot),
        "classification_snapshot_sha256": classification_snapshot["sha256"],
        "records": records,
        "oracle_records": oracle_records,
        "sensitivity_records": sensitivity_records,
        "sensitivity_anchor_groups": sensitivity_anchor_groups,
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
    payload["output_sha256"] = _checkpoint_output_sha256(payload)
    return payload


def _transition_key(record: Mapping[str, Any]) -> tuple[float, str, int, str]:
    return (
        float(record["k"]),
        str(record["sector"]),
        int(record["ell"]),
        str(record["point_id"]),
    )


def _compress_transition_records(
    records: Sequence[Mapping[str, Any]],
) -> dict[tuple[float, str], tuple[tuple[int, int, tuple[str, ...]], ...]]:
    point_order = {point.point_id: index for index, point in enumerate(TABLEI_POINTS)}
    points_by_group_ell: dict[tuple[float, str, int], set[str]] = defaultdict(set)
    for record in records:
        key = (
            float(record["k"]),
            str(record["sector"]),
            int(record["ell"]),
        )
        points_by_group_ell[key].add(str(record["point_id"]))

    compressed: dict[
        tuple[float, str], tuple[tuple[int, int, tuple[str, ...]], ...]
    ] = {}
    for k in FREQUENCIES:
        for sector in (Sector.ODD, Sector.EVEN):
            items = [
                (
                    ell,
                    tuple(sorted(point_ids, key=point_order.__getitem__)),
                )
                for (frequency, group_sector, ell), point_ids
                in points_by_group_ell.items()
                if frequency == k and group_sector == sector.value
            ]
            items.sort()
            segments: list[tuple[int, int, tuple[str, ...]]] = []
            for ell, point_ids in items:
                if (
                    segments
                    and ell == segments[-1][1] + 1
                    and point_ids == segments[-1][2]
                ):
                    previous = segments[-1]
                    segments[-1] = (previous[0], ell, point_ids)
                else:
                    segments.append((ell, ell, point_ids))
            compressed[(k, sector.value)] = tuple(segments)

    expanded = {
        (k, sector, ell, point_id)
        for (k, sector), segments in compressed.items()
        for ell_min, ell_max, point_ids in segments
        for ell in range(ell_min, ell_max + 1)
        for point_id in point_ids
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
    segments: Mapping[
        tuple[float, str], tuple[tuple[int, int, tuple[str, ...]], ...]
    ],
    classification_sha256: str,
    oracle_validation_sha256: str,
    classification_snapshot: Mapping[str, Any],
) -> None:
    points = tuple((point.point_id, point.r) for point in TABLEI_POINTS)
    lines = [
        '"""Generated immutable T4ab further-local Q018 envelope."""',
        "",
        "from __future__ import annotations",
        "",
        f"FREQUENCIES: tuple[float, ...] = {FREQUENCIES!r}",
        f"FREQUENCY_TOKENS: dict[float, str] = {FREQUENCY_TOKENS!r}",
        f"POINTS: tuple[tuple[str, float], ...] = {points!r}",
        "TRANSITION_SEGMENTS: dict[",
        "    tuple[float, str], tuple[tuple[int, int, tuple[str, ...]], ...]",
        "] = {",
    ]
    for k in FREQUENCIES:
        for sector in (Sector.ODD, Sector.EVEN):
            key = (k, sector.value)
            lines.append(f"    {key!r}: {segments[key]!r},")
    lines.extend(
        [
            "}",
            f"SOURCE_HASHES: dict[str, str] = {classification_snapshot['payload']['source_hashes']!r}",
            f'CLASSIFICATION_SNAPSHOT_SHA256: str = "{classification_snapshot["sha256"]}"',
            f'CLASSIFICATION_SHA256: str = "{classification_sha256}"',
            f'ORACLE_VALIDATION_SHA256: str = "{oracle_validation_sha256}"',
            "",
            "__all__ = [",
            '    "FREQUENCIES",',
            '    "FREQUENCY_TOKENS",',
            '    "POINTS",',
            '    "TRANSITION_SEGMENTS",',
            '    "SOURCE_HASHES",',
            '    "CLASSIFICATION_SNAPSHOT_SHA256",',
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
    sensitivity_anchor_groups = [
        {
            "k": float(checkpoint["frequency"]),
            **group,
        }
        for checkpoint in checkpoints
        for group in checkpoint["sensitivity_anchor_groups"]
    ]
    transitions = [
        record
        for record in classification_records
        if record["classification"] in STRUCTURED_CLASSES
    ]
    segments = _compress_transition_records(transitions)
    counts = Counter(record["classification"] for record in classification_records)
    classification_snapshot = dict(checkpoints[0]["classification_snapshot"])
    if any(
        checkpoint["classification_snapshot"] != classification_snapshot
        for checkpoint in checkpoints
    ):
        raise RuntimeError("classification snapshot differs across checkpoints")
    classification = {
        "schema_version": SCHEMA_VERSION,
        "thread": "T4ab",
        "stage": "classification",
        "decision_candidate": "GREEN / FURTHER LOCAL RADIAL GATE READY",
        "inputs": {
            "frequencies": list(FREQUENCIES),
            "lmax_values": {str(k): list(LMAX_VALUES[k]) for k in FREQUENCIES},
            "boundary": dict(BOUNDARY),
            "sectors": [Sector.ODD.value, Sector.EVEN.value],
            "points": _point_contract(),
        },
        "classification_snapshot": classification_snapshot,
        "classification_snapshot_sha256": classification_snapshot["sha256"],
        "checkpoint_sha256": {
            str(checkpoint["frequency"]): _sha256(
                _checkpoint_path(float(checkpoint["frequency"]))
            )
            for checkpoint in checkpoints
        },
        "records": classification_records,
        "transition_records": transitions,
        "transition_segments": {
            str(k): {
                sector.value: [
                    [ell_min, ell_max, list(point_ids)]
                    for ell_min, ell_max, point_ids in segments[(k, sector.value)]
                ]
                for sector in (Sector.ODD, Sector.EVEN)
            }
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
            "no_lmax_extension": True,
            "no_uniform_0p025_or_0p0125_scan": True,
            "no_recursive_midpoint": True,
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
        "thread": "T4ab",
        "stage": "oracle_validation",
        "classification_sha256": _sha256(CLASSIFICATION_PATH),
        "classification_snapshot": classification_snapshot,
        "classification_snapshot_sha256": classification_snapshot["sha256"],
        "records": oracle_records,
        "sensitivity_records": sensitivity_records,
        "sensitivity_anchor_groups": sensitivity_anchor_groups,
        "summary": oracle_summary,
        "non_artifact_statement": classification["non_artifact_statement"],
    }
    _atomic_json(ORACLE_PATH, oracle)
    _write_envelope_module(
        segments=segments,
        classification_sha256=_sha256(CLASSIFICATION_PATH),
        oracle_validation_sha256=_sha256(ORACLE_PATH),
        classification_snapshot=classification_snapshot,
    )


def _run_classification() -> None:
    frozen_input_hashes = _verify_frozen_inputs()
    classification_snapshot = _classification_snapshot(frozen_input_hashes)
    checkpoints: list[dict[str, Any]] = []
    for k in FREQUENCIES:
        contract = _contract_payload(k, classification_snapshot)
        path = _checkpoint_path(k)
        if path.exists():
            checkpoint = _load_json(path)
            if _checkpoint_matches(
                checkpoint,
                k=k,
                contract=contract,
                classification_snapshot=classification_snapshot,
            ):
                print(f"T4AB kM={k:.17g}: reused exact PASS checkpoint", flush=True)
                checkpoints.append(checkpoint)
                continue
            quarantined = _quarantine(path)
            print(f"T4AB kM={k:.17g}: quarantined {quarantined}", flush=True)
        checkpoint = _run_frequency(
            k=k,
            classification_snapshot=classification_snapshot,
        )
        _atomic_json(path, checkpoint)
        print(
            f"T4AB kM={k:.17g}: checkpoint decision={checkpoint['decision']} "
            f"sha256={_sha256(path)}",
            flush=True,
        )
        if checkpoint["decision"] != "PASS":
            raise RuntimeError(
                f"T4ab scientific gate stopped at kM={k:.17g}; "
                "checkpoint decision is FAIL"
            )
        checkpoints.append(checkpoint)
    _aggregate(checkpoints)
    _audit()


def _audit() -> None:
    _verify_frozen_inputs()
    classification = _load_json(CLASSIFICATION_PATH)
    oracle = _load_json(ORACLE_PATH)
    checkpoints = [_load_json(_checkpoint_path(k)) for k in FREQUENCIES]
    expected_total = sum(
        (max(LMAX_VALUES[k]) - 1) * 2 * len(TABLEI_POINTS) for k in FREQUENCIES
    )
    records = classification["records"]
    transitions = classification["transition_records"]
    oracle_records = oracle["records"]
    classification_snapshot = classification["classification_snapshot"]
    if (
        classification_snapshot["sha256"]
        != _canonical_sha256(classification_snapshot["payload"])
    ):
        raise RuntimeError("classification snapshot hash is invalid")
    if len(checkpoints) != len(FREQUENCIES):
        raise RuntimeError("checkpoint cardinality mismatch")
    for k, checkpoint in zip(FREQUENCIES, checkpoints, strict=True):
        contract = _contract_payload(k, classification_snapshot)
        if not _checkpoint_matches(
            checkpoint,
            k=k,
            contract=contract,
            classification_snapshot=classification_snapshot,
        ):
            raise RuntimeError(f"checkpoint kM={k:.17g} failed fresh validation")
    if len(records) != expected_total:
        raise RuntimeError(
            f"classification cardinality mismatch: {len(records)} != {expected_total}"
        )
    record_keys = [_transition_key(record) for record in records]
    if len(set(record_keys)) != expected_total:
        raise RuntimeError("classification keys are duplicated or incomplete")
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
    if any(
        not record["passed"]
        for checkpoint in checkpoints
        for record in checkpoint["sensitivity_records"]
    ):
        raise RuntimeError("at least one sensitivity anchor failed")
    if oracle["classification_sha256"] != _sha256(CLASSIFICATION_PATH):
        raise RuntimeError("oracle does not bind the classification artifact")
    if oracle["classification_snapshot"] != classification_snapshot:
        raise RuntimeError("oracle classification snapshot mismatch")
    _compress_transition_records(transitions)
    print(
        "T4AB_CLASSIFICATION_AND_ORACLE_AUDIT=PASS "
        f"records={len(records)} transitions={len(transitions)} "
        f"checkpoints={len(checkpoints)}",
        flush=True,
    )


def _oracle_map() -> dict[tuple[float, str, int, str], Mapping[str, Any]]:
    oracle = _load_json(ORACLE_PATH)
    return {_transition_key(record): record for record in oracle["records"]}


def _git_bytes(*args: str) -> bytes:
    completed = subprocess.run(
        ("git", *args),
        check=True,
        capture_output=True,
    )
    return completed.stdout


def _final_adapter_snapshot(
    classification_snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    commit = _git_bytes("rev-parse", "HEAD").decode().strip()
    commit_paths = tuple(
        sorted(
            line
            for line in _git_bytes(
                "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"
            ).decode().splitlines()
            if line
        )
    )
    expected_paths = tuple(sorted(str(path) for path in IMPLEMENTATION_PATHS))
    if commit_paths != expected_paths:
        raise RuntimeError(
            "implementation commit path set mismatch: "
            f"expected={expected_paths!r} actual={commit_paths!r}"
        )
    blobs: dict[str, dict[str, str]] = {}
    for path in IMPLEMENTATION_PATHS:
        committed = _git_bytes("show", f"HEAD:{path}")
        worktree_sha256 = _sha256(path)
        committed_sha256 = _sha256_bytes(committed)
        if worktree_sha256 != committed_sha256:
            raise RuntimeError(f"implementation path differs from HEAD: {path}")
        blobs[str(path)] = {
            "git_blob": _git_bytes("rev-parse", f"HEAD:{path}").decode().strip(),
            "sha256": committed_sha256,
        }
    payload = {
        "schema_version": "phase5_t4ab_final_adapter_snapshot_v1",
        "implementation_commit": commit,
        "implementation_paths": list(expected_paths),
        "implementation_blobs": blobs,
        "classification_snapshot_sha256": classification_snapshot["sha256"],
    }
    return {"payload": payload, "sha256": _canonical_sha256(payload)}


def _run_preflight() -> None:
    from schwgw.numerics.q018_further_local_envelope import (
        CLASSIFICATION_SHA256,
        CLASSIFICATION_SNAPSHOT_SHA256,
        ORACLE_VALIDATION_SHA256,
    )

    _verify_frozen_inputs()
    if _sha256(CLASSIFICATION_PATH) != CLASSIFICATION_SHA256:
        raise RuntimeError("classification hash does not match generated envelope")
    if _sha256(ORACLE_PATH) != ORACLE_VALIDATION_SHA256:
        raise RuntimeError("oracle-validation hash does not match generated envelope")
    classification = _load_json(CLASSIFICATION_PATH)
    classification_snapshot = classification["classification_snapshot"]
    if classification_snapshot["sha256"] != CLASSIFICATION_SNAPSHOT_SHA256:
        raise RuntimeError("generated envelope classification snapshot mismatch")
    final_adapter_snapshot = _final_adapter_snapshot(classification_snapshot)
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
            and all(
                _finite_complex(value)
                for value in (psi, dpsi_dr, solution.A_in, solution.A_out)
            )
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
                f"T4AB preflight={index}/{len(transitions)} "
                f"kM={k:.17g} frequency={completed_by_k[k]}/{counts_by_k[k]}",
                flush=True,
        )
    expected_keys = {_transition_key(record) for record in transitions}
    preflight_keys = {_transition_key(record) for record in preflight_records}
    if len(preflight_records) != len(expected_keys) or preflight_keys != expected_keys:
        raise RuntimeError("resume preflight transition key set mismatch")
    failures = [record for record in preflight_records if not record["passed"]]
    payload = {
        "schema_version": PREFLIGHT_SCHEMA_VERSION,
        "thread": "T4ab",
        "stage": "resume_preflight",
        "adapter_name": ADAPTER_NAME,
        "classification_sha256": _sha256(CLASSIFICATION_PATH),
        "oracle_validation_sha256": _sha256(ORACLE_PATH),
        "classification_snapshot": classification_snapshot,
        "classification_snapshot_sha256": classification_snapshot["sha256"],
        "final_adapter_snapshot": final_adapter_snapshot,
        "final_adapter_snapshot_sha256": final_adapter_snapshot["sha256"],
        "snapshot_bridge": {
            "classification_snapshot_sha256": classification_snapshot["sha256"],
            "final_adapter_snapshot_sha256": final_adapter_snapshot["sha256"],
            "linked": (
                final_adapter_snapshot["payload"][
                    "classification_snapshot_sha256"
                ]
                == classification_snapshot["sha256"]
            ),
        },
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
            "no_lmax_extension": True,
            "no_uniform_0p025_or_0p0125_scan": True,
            "no_recursive_midpoint": True,
        },
    }
    _atomic_json(PREFLIGHT_PATH, payload)
    if failures:
        raise RuntimeError(f"resume preflight has {len(failures)} failures")
    _write_manifest(payload)
    print(
        "T4AB_RESUME_PREFLIGHT=PASS "
        f"records={len(preflight_records)} sha256={_sha256(PREFLIGHT_PATH)}",
        flush=True,
    )


def _write_manifest(preflight: Mapping[str, Any]) -> None:
    classification = _load_json(CLASSIFICATION_PATH)
    oracle = _load_json(ORACLE_PATH)
    checkpoint_lines = [
        f"- `{_checkpoint_path(k)}`: `{_sha256(_checkpoint_path(k))}`"
        for k in FREQUENCIES
    ]
    lines = [
        "# T4ab Further-Local Radial Gate Manifest",
        "",
        "- Decision candidate: `GREEN / FURTHER LOCAL RADIAL GATE READY`",
        f"- Classification rows: `{classification['summary']['total_records']}`",
        f"- Transition rows: `{classification['summary']['transition_record_count']}`",
        f"- Oracle validated: `{oracle['summary']['oracle_validated']}`",
        f"- Adapter preflight validated: `{preflight['summary']['adapter_validated']}`",
        f"- Classification SHA-256: `{_sha256(CLASSIFICATION_PATH)}`",
        f"- Oracle SHA-256: `{_sha256(ORACLE_PATH)}`",
        f"- Preflight SHA-256: `{_sha256(PREFLIGHT_PATH)}`",
        f"- Classification snapshot: `{classification['classification_snapshot_sha256']}`",
        f"- Final adapter snapshot: `{preflight['final_adapter_snapshot_sha256']}`",
        "",
        "## Checkpoints",
        "",
        *checkpoint_lines,
        "",
        "Radial-only evidence. No T8aq, observable, plot, fixture, Kirchhoff,",
        "paper artifact, lmax extension, full-grid/uniform scan, or recursive",
        "midpoint was produced.",
        "",
    ]
    _atomic_text(MANIFEST_PATH, "\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the frozen T4ab further-local radial/Q018 gate."
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
