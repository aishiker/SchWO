#!/usr/bin/env python3
"""Run and compare the independent BHPT Toolkit MST normalization benchmark."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any

from schwgw.scattering.mst_benchmark import (
    MSTBenchmarkError,
    benchmark_source_identity,
    compare_bhpt_mst_benchmark,
)


PROJECT = Path(__file__).resolve().parents[1]
WLS = PROJECT / "scripts" / "bhpt_reggewheeler_mst_benchmark.wls"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _git_commit(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _record_process(path: Path, result: subprocess.CompletedProcess[str]) -> None:
    _atomic_json(
        path,
        {
            "argv": result.args,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        },
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--package-root", type=Path)
    parser.add_argument("--external-json", type=Path)
    parser.add_argument("--wolframscript", default="wolframscript")
    parser.add_argument("--timeout-seconds", type=float, default=7200.0)
    args = parser.parse_args(argv)
    if args.package_root is None and args.external_json is None:
        parser.error("--package-root is required unless --external-json is supplied")
    root = args.output_dir.resolve()
    root.mkdir(parents=True, exist_ok=False)

    request: dict[str, Any] = {
        "schema_version": "schwo_bhpt_mst_benchmark_request_v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT),
        "wls_path": str(WLS),
        "wls_sha256": _sha256(WLS),
        "frequency_kM": [0.5, 1.0, 1.5, 2.0],
        "ell_range": [20, 40],
        "toolkit_url": "https://bhptoolkit.org/ReggeWheeler/",
        "toolkit_repository": (
            "https://github.com/BlackHolePerturbationToolkit/ReggeWheeler"
        ),
        "toolkit_license": "MIT",
        "strict_no_fitted_phase_or_normalization": True,
    }
    if args.external_json is not None:
        external = args.external_json.resolve()
        request["external_json"] = str(external)
        request["external_json_sha256"] = _sha256(external)
    else:
        assert args.package_root is not None
        source = benchmark_source_identity(args.package_root)
        package_root = Path(source["package_root"])
        radial = Path(source["radial_source"])
        request.update(source)
        request["package_commit"] = _git_commit(package_root)
        request["radial_source_sha256"] = _sha256(radial)
    _atomic_json(root / "request.json", request)

    if args.external_json is None:
        executable = shutil.which(args.wolframscript)
        if executable is None:
            _atomic_json(
                root / "blocked.json",
                {
                    "status": "BLOCKED",
                    "reason": "wolframscript_not_found",
                    "science_executed": False,
                    "strict_paper_reproduction_claim": False,
                },
            )
            return 3
        preflight = subprocess.run(
            [executable, "-code", "$Version"],
            cwd=PROJECT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        _record_process(root / "wolfram_preflight.json", preflight)
        if preflight.returncode != 0:
            _atomic_json(
                root / "blocked.json",
                {
                    "status": "BLOCKED",
                    "reason": "wolfram_kernel_unavailable",
                    "wolframscript_returncode": preflight.returncode,
                    "science_executed": False,
                    "external_mst_records_generated": 0,
                    "strict_paper_reproduction_claim": False,
                },
            )
            return 3
        external = root / "external_bhpt_mst.json"
        env = os.environ.copy()
        env.update(
            {
                "SCHWO_BHPT_OUTPUT": str(external),
                "SCHWO_BHPT_PACKAGE_ROOT": str(package_root),
                "SCHWO_BHPT_SOURCE_COMMIT": request["package_commit"] or "unknown",
                "SCHWO_BHPT_RADIAL_SHA256": request["radial_source_sha256"],
            }
        )
        try:
            run = subprocess.run(
                [executable, "-file", str(WLS)],
                cwd=PROJECT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=args.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            _atomic_json(
                root / "blocked.json",
                {
                    "status": "BLOCKED",
                    "reason": "external_mst_timeout",
                    "timeout_seconds": args.timeout_seconds,
                    "stdout": exc.stdout,
                    "stderr": exc.stderr,
                    "strict_paper_reproduction_claim": False,
                },
            )
            return 3
        _record_process(root / "wolfram_run.json", run)
        if run.returncode != 0 or not external.is_file():
            _atomic_json(
                root / "blocked.json",
                {
                    "status": "BLOCKED",
                    "reason": "external_mst_generation_failed",
                    "wolframscript_returncode": run.returncode,
                    "external_json_exists": external.is_file(),
                    "strict_paper_reproduction_claim": False,
                },
            )
            return 3

    try:
        payload = json.loads(external.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _atomic_json(
            root / "comparison_failure.json",
            {
                "status": "FAIL",
                "reason": "external_mst_json_invalid",
                "detail": str(exc),
                "external_json": str(external),
                "external_json_size": (
                    external.stat().st_size if external.is_file() else None
                ),
                "external_json_sha256": (
                    _sha256(external) if external.is_file() else None
                ),
                "strict_paper_reproduction_claim": False,
            },
        )
        return 2
    try:
        comparison = compare_bhpt_mst_benchmark(payload)
    except MSTBenchmarkError as exc:
        _atomic_json(
            root / "comparison_failure.json",
            {
                "status": "FAIL",
                "reason": str(exc),
                "strict_paper_reproduction_claim": False,
            },
        )
        return 2
    comparison["external_json"] = str(external)
    comparison["external_json_sha256"] = _sha256(external)
    comparison["strict_paper_reproduction_claim"] = False
    _atomic_json(root / "comparison.json", comparison)
    print(json.dumps({key: comparison[key] for key in (
        "status", "record_count", "max_odd_abs_error", "max_even_abs_error"
    )}, sort_keys=True))
    return 0 if comparison["status"] == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MSTBenchmarkError as exc:
        print(f"BHPT MST benchmark error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
