#!/usr/bin/env python3
"""Run the bounded Phase-6 selected-mode radial S-matrix pilot."""

from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import stat
import time
from typing import Any

import mpmath
import numpy as np
import scipy

from schwgw.scattering.mst import schwarzschild_mst_phase_factor
from schwgw.scattering.mst_benchmark import validate_bhpt_mst_benchmark
from schwgw.validation.phase6_radial_pilot import (
    PILOT_SCHEMA,
    attach_external_comparisons,
    backend_capabilities,
    bhpt_record_for_mode,
    run_mode_ladder,
    selected_pilot_modes,
    sha256_file,
    validate_pilot_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
BHPT_ROOT = ROOT / "runs/phase5/paper_figures/bhpt_mst_benchmark_20260803_v4"
BHPT_JSON = BHPT_ROOT / "external_bhpt_mst.json"
PHASE6_CONFIG = ROOT / "configs/phase6_independent_physical_validation.yaml"
AUDIT = ROOT / "audits/SchWO_physical_validation_audit_20260806.md"


def _canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def _publish_json(path: Path, payload: object) -> dict[str, object]:
    data = _canonical_bytes(payload)
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
    os.chmod(path, 0o444)
    _fsync_directory(path.parent)
    identity = _file_identity(path)
    if path.read_bytes() != data:
        raise RuntimeError(f"published JSON reload mismatch: {path}")
    return identity


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _file_identity(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    status = resolved.lstat()
    if not stat.S_ISREG(status.st_mode) or status.st_nlink != 1:
        raise RuntimeError(f"evidence file must be regular nlink1: {resolved}")
    return {
        "path": str(resolved),
        "sha256": sha256_file(resolved),
        "size": status.st_size,
        "mode": stat.S_IMODE(status.st_mode),
        "inode": status.st_ino,
        "nlink": status.st_nlink,
    }


def _source_identity(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    return {"path": str(resolved), "sha256": sha256_file(resolved)}


def _prove_mst_call_graph_isolation(path: Path) -> dict[str, object]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported = []
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
        elif isinstance(node, ast.Call):
            function = node.func
            if isinstance(function, ast.Name):
                calls.append(function.id)
            elif isinstance(function, ast.Attribute):
                calls.append(function.attr)
    forbidden_imports = [
        name
        for name in imported
        if name.endswith("radial_solver") or name.endswith("numerics.matching")
    ]
    forbidden_calls = sorted(set(calls) & {"solve_radial_mode", "match_outer_asymptotic"})
    if forbidden_imports or forbidden_calls:
        raise RuntimeError("MST call graph is not isolated from the primary radial path")
    return {
        "source": str(path.resolve()),
        "forbidden_imports": forbidden_imports,
        "forbidden_calls": forbidden_calls,
        "isolated": True,
    }


def _provenance(external: dict[str, Any]) -> dict[str, dict[str, str]]:
    radial = ROOT / "src/schwgw/numerics/radial_solver.py"
    matching = ROOT / "src/schwgw/numerics/matching.py"
    flux = ROOT / "src/schwgw/scattering/radial_validation.py"
    mst = ROOT / "src/schwgw/scattering/mst.py"
    high_precision = ROOT / "scripts/verify_fig2_high_precision.py"
    mpmath_record = (
        Path(mpmath.__file__).resolve().parent.parent / "mpmath-1.4.1.dist-info/RECORD"
    )
    common_inputs = {
        "phase6_config": sha256_file(PHASE6_CONFIG),
        "physical_validation_audit": sha256_file(AUDIT),
    }
    return {
        "scipy_source": {
            "radial_solver.py": sha256_file(radial),
            "matching.py": sha256_file(matching),
            "radial_validation.py": sha256_file(flux),
        },
        "scipy_dependencies": {
            "numpy.__init__": sha256_file(Path(np.__file__)),
            "scipy.__init__": sha256_file(Path(scipy.__file__)),
        },
        "common_inputs": common_inputs,
        "mst_source": {"mst.py": sha256_file(mst)},
        "mpmath_dependencies": {
            "mpmath.__init__": sha256_file(Path(mpmath.__file__)),
            "mpmath.RECORD": sha256_file(mpmath_record),
        },
        "bhpt_source": {
            "ReggeWheelerRadial.m": str(external["regge_wheeler_radial_sha256"]),
            "benchmark_launcher.wls": sha256_file(
                ROOT / "scripts/bhpt_reggewheeler_mst_benchmark.wls"
            ),
        },
        "bhpt_dependencies": {
            "request.json": sha256_file(BHPT_ROOT / "request.json"),
            "wolfram_run.json": sha256_file(BHPT_ROOT / "wolfram_run.json"),
        },
        "bhpt_inputs": {"external_bhpt_mst.json": sha256_file(BHPT_JSON)},
        "mpmath_ode_candidate_source": {
            "verify_fig2_high_precision.py": sha256_file(high_precision)
        },
    }


def run(output_root: Path) -> dict[str, object]:
    started = time.perf_counter()
    if output_root.exists():
        raise FileExistsError(f"output root already exists: {output_root}")
    output_root.mkdir(parents=True, mode=0o700)
    if stat.S_IMODE(output_root.stat().st_mode) != 0o700:
        raise RuntimeError("fresh evidence root mode mismatch")

    external = json.loads(BHPT_JSON.read_text(encoding="utf-8"))
    validate_bhpt_mst_benchmark(external)
    provenance = _provenance(external)
    mst_source = ROOT / "src/schwgw/scattering/mst.py"
    call_graph_proof = _prove_mst_call_graph_isolation(mst_source)
    source_paths = (
        Path(__file__),
        ROOT / "src/schwgw/validation/phase6_radial_pilot.py",
        ROOT / "src/schwgw/numerics/radial_solver.py",
        ROOT / "src/schwgw/numerics/boundary_conditions.py",
        ROOT / "src/schwgw/numerics/matching.py",
        ROOT / "src/schwgw/scattering/radial_validation.py",
        mst_source,
        PHASE6_CONFIG,
        AUDIT,
        BHPT_JSON,
    )
    sources = [_source_identity(path) for path in source_paths]

    modes = []
    mst_cache: dict[tuple[float, int], object] = {}
    raw_bhpt_records = external["records"]
    for mode in selected_pilot_modes():
        record = run_mode_ladder(mode)
        key = (mode.kM, mode.ell)
        if key not in mst_cache:
            try:
                mst_cache[key] = schwarzschild_mst_phase_factor(
                    mode.ell,
                    k=mode.kM,
                    working_dps=70,
                )
            except RuntimeError as exc:
                mst_cache[key] = exc
        mst = mst_cache[key]
        mst_failed = isinstance(mst, RuntimeError)
        attach_external_comparisons(
            record,
            bhpt_record=bhpt_record_for_mode(raw_bhpt_records, mode),
            mst_odd=None if mst_failed else mst.odd,
            mst_even=None if mst_failed else mst.even,
            mst_recurrence_residual=None if mst_failed else mst.recurrence_residual,
            mst_blocker=(
                f"{type(mst).__name__}: {mst}" if mst_failed else None
            ),
        )
        modes.append(record)

    capabilities = backend_capabilities(
        mpmath_version=mpmath.__version__, provenance=provenance
    )
    evidence = {
        "schema_version": PILOT_SCHEMA,
        "scope": "selected_mode_development_pilot",
        "overall_status": "YELLOW_PARTIAL_SELECTED_MODE_EVIDENCE",
        "global_green_permitted": False,
        "pilot_domain": {
            "covered_keys": [mode.to_metadata() for mode in selected_pilot_modes()],
            "covered_key_count": len(selected_pilot_modes()),
            "production_deduplicated_key_count": 16048,
            "production_standard_backend_key_count": 6400,
            "production_q018_dense_local_key_count": 9648,
            "production_missing_key_count": 16048 - len(selected_pilot_modes()),
            "full_v1_domain_kM": [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 4.0, 8.0],
            "full_v1_domain_ell": "2..actual_production_lmax",
            "full_v1_domain_sectors": ["odd", "even"],
            "full_v1_domain_complete": False,
            "inventory_source": "T8 read-only production-domain inventory dispatch",
        },
        "backend_capabilities": [item.to_metadata() for item in capabilities],
        "modes": modes,
        "source_identities": {
            "files": sources,
            "backend_provenance": provenance,
            "mst_call_graph_isolation": call_graph_proof,
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "mpmath": mpmath.__version__,
        },
        "limitations": [
            "bounded seven-key pilot; 16041 production keys are not covered",
            "full declared r_in/r_out/Jost ladders are intentionally incomplete",
            "BHPT direct integration is not callable locally",
            "independent arbitrary-precision ODE S-matrix backend is not implemented",
            "even MST values are parity-derived and are not independent even solves",
            "Q018 horizon flux is unresolved and receives no physical-flux PASS",
            "numerical and convention uncertainty budgets remain open",
            "no V1/full-domain/project/global GREEN claim",
        ],
    }
    validate_pilot_evidence(evidence)
    evidence_identity = _publish_json(output_root / "selected_mode_evidence.json", evidence)
    elapsed = time.perf_counter() - started
    manifest = {
        "schema_version": "schwgw_phase6_radial_selected_pilot_manifest_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "evidence": evidence_identity,
        "source_identities": sources,
        "backend_call_graph_proof": call_graph_proof,
        "elapsed_seconds": elapsed,
        "science_scope": "seven selected radial modes only",
        "paper_figure_runs": 0,
        "full_domain_runs": 0,
        "global_green_permitted": False,
    }
    manifest_identity = _publish_json(output_root / "manifest.json", manifest)
    checkpoint = {
        "schema_version": "schwgw_phase6_radial_selected_pilot_checkpoint_v1",
        "status": "YELLOW_PARTIAL_SELECTED_MODE_EVIDENCE",
        "evidence": evidence_identity,
        "manifest": manifest_identity,
        "covered_key_count": len(selected_pilot_modes()),
        "production_missing_key_count": 16048 - len(selected_pilot_modes()),
        "global_green_permitted": False,
    }
    checkpoint_identity = _publish_json(output_root / "checkpoint.json", checkpoint)
    os.chmod(output_root, 0o555)
    _fsync_directory(output_root.parent)
    return {
        "root": str(output_root.resolve()),
        "evidence": evidence_identity,
        "manifest": manifest_identity,
        "checkpoint": checkpoint_identity,
        "elapsed_seconds": elapsed,
        "modes": [
            {
                "mode_id": record["mode"]["mode_id"],
                "numerical_uncertainty": record["numerical_uncertainty"],
                "internal": record["layers"]["internal_flux_wronskian"],
                "external": record["layers"]["external_algorithm"][
                    "diagnostic_comparison_status"
                ],
            }
            for record in modes
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    arguments = parser.parse_args()
    print(json.dumps(run(arguments.output_root), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
