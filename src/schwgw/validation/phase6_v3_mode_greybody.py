"""Deterministic V3.1 mode-greybody inventory and fail-closed evidence.

The numerical producer consumes the same inventory.  This module contains no
radial solver calls, which lets an independent reviewer reconstruct the exact
496-key, AP-anchor, and external-anchor domains before science starts.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[3]
DOMAIN_PATH = ROOT / "configs/phase6_v3_0_domain.json"
THRESHOLD_PATH = ROOT / "configs/phase6_v3_0_thresholds.json"
ANCHOR_PATH = ROOT / "configs/phase6_v3_0_external_anchor_matrix.json"
PROMPT_PATH = ROOT / "docs/prompts/phase6_t4_v3_1_mode_greybody.md"
REVIEW_PROMPT_PATH = ROOT / "docs/prompts/phase6_t7_v3_1_review.md"
WOLFRAM_KERNEL = Path(
    "/Volumes/JohnnyTforGR/Applications/Wolfram.app/Contents/MacOS/WolframKernel"
)
WOLFRAM_KERNEL_SHA256 = (
    "70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c"
)
BHPT_PACKAGE_ROOT = Path("/private/tmp/SchWO_ReggeWheeler_phase6_v1_20260808")
BHPT_SMOKE_WLS = ROOT / "scripts/phase6_v3_1_bhpt_mst_smoke.wls"

EXPECTED = {
    DOMAIN_PATH: "803c02efeaa89d83222d8663de0c3f2da223bab285d46f331e476793a44c263b",
    THRESHOLD_PATH: "91fbe1a758bbb2bbf0e3ec3e67e89b400e900674feee727af8f1cff00732ac4a",
    ANCHOR_PATH: "06580c6801a4f75104a2018e7873afbe4ec6c6ed900a11c0860ca23f15a44485",
    PROMPT_PATH: "7e377f64782b8311e111469f53eeb182190d30347ffe0d9853a41b96deeafab6",
    REVIEW_PROMPT_PATH: "058cea918e0c41537b4af8b3973dbe9d378cd3b612aad884ac986d14733d3899",
}

FREQUENCIES = (
    "0.005",
    "0.01",
    "0.02",
    "0.05",
    "0.1",
    "0.2",
    "0.5",
    "1",
    "2",
    "4",
    "8",
)
PARITIES = ("odd", "even")


class V31ContractError(RuntimeError):
    """A frozen V3.1 contract or publication rule was violated."""


@dataclass(frozen=True, order=True)
class ModeKey:
    frequency_ordinal: int
    ell: int
    parity_ordinal: int
    kM: str
    parity: str

    def payload(self) -> dict[str, Any]:
        return {
            "ell": self.ell,
            "frequency_ordinal": self.frequency_ordinal,
            "kM": self.kM,
            "parity": self.parity,
            "parity_ordinal": self.parity_ordinal,
        }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def verify_frozen_inputs() -> dict[str, dict[str, Any]]:
    identities: dict[str, dict[str, Any]] = {}
    for path, expected in EXPECTED.items():
        resolved = path.resolve(strict=True)
        actual = sha256(resolved)
        info = resolved.stat()
        if actual != expected or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise V31ContractError(f"frozen input identity drift: {path}")
        identities[str(path.relative_to(ROOT))] = {
            "path": str(resolved),
            "sha256": actual,
            "size": info.st_size,
            "mode": stat.S_IMODE(info.st_mode),
            "nlink": info.st_nlink,
        }
    return identities


def _ell_max(k: float) -> int:
    return max(12, math.ceil(3.0 * math.sqrt(3.0) * k - 0.5) + 16)


def build_mode_inventory() -> list[ModeKey]:
    domain = _load_json(DOMAIN_PATH)["domains"]["V3.1"]
    frozen = [
        *domain["frequency_strata_kM"]["low"],
        *domain["frequency_strata_kM"]["mid"],
        *domain["frequency_strata_kM"]["high"],
    ]
    if [float(value) for value in FREQUENCIES] != frozen:
        raise V31ContractError("frequency sequence differs from frozen domain")
    keys = [
        ModeKey(frequency_ordinal, ell, parity_ordinal, label, parity)
        for frequency_ordinal, label in enumerate(FREQUENCIES)
        for ell in range(2, _ell_max(float(label)) + 1)
        for parity_ordinal, parity in enumerate(PARITIES)
    ]
    if len(keys) != 496 or len({(k.kM, k.ell) for k in keys}) != 248:
        raise V31ContractError("V3.1 inventory is not exactly 248 pairs/496 modes")
    return keys


def _nearest(domain: Iterable[int], target: float) -> int:
    return min(domain, key=lambda ell: (abs(ell - target), ell))


def build_anchor_inventory(keys: list[ModeKey]) -> dict[str, Any]:
    by_frequency: dict[str, list[int]] = defaultdict(list)
    for key in keys:
        if key.parity == "odd":
            by_frequency[key.kM].append(key.ell)
    labels: dict[tuple[str, int, str], set[str]] = defaultdict(set)
    for kM in ("0.005", "0.01", "0.02", "0.05"):
        for ell in (2, 3, 4, 8, 12):
            if ell in by_frequency[kM]:
                for parity in PARITIES:
                    labels[(kM, ell, parity)].add("V3A-MODE-AP-LOW-001")
    for kM in ("0.5", "1", "2", "4", "8"):
        critical = 3.0 * math.sqrt(3.0) * float(kM)
        for ell in by_frequency[kM]:
            if abs((ell + 0.5) - critical) <= 2.0:
                for parity in PARITIES:
                    labels[(kM, ell, parity)].add("V3A-MODE-AP-TURNING-001")
    for kM in ("0.1", "0.5", "1", "2", "4", "8"):
        critical_ell = 3.0 * math.sqrt(3.0) * float(kM) - 0.5
        for offset in (8.0, 12.0):
            ell = _nearest(by_frequency[kM], critical_ell + offset)
            for parity in PARITIES:
                labels[(kM, ell, parity)].add("V3A-MODE-AP-EVANESCENT-001")
    ap = [
        {"ell": ell, "kM": kM, "memberships": sorted(memberships), "parity": parity}
        for (kM, ell, parity), memberships in labels.items()
    ]
    ap.sort(
        key=lambda item: (
            FREQUENCIES.index(item["kM"]),
            item["ell"],
            PARITIES.index(item["parity"]),
        )
    )

    external: list[dict[str, Any]] = []
    for kM in ("0.1", "0.5", "1", "2", "4"):
        domain = by_frequency[kM]
        critical_ell = 3.0 * math.sqrt(3.0) * float(kM) - 0.5
        selected = {
            2,
            3,
            4,
            _nearest(domain, critical_ell),
            _nearest(domain, critical_ell + 8.0),
        }
        for ell in sorted(selected.intersection(domain)):
            external.append(
                {
                    "anchor_id": "V3A-MODE-BHPT-RW-001",
                    "ell": ell,
                    "kM": kM,
                    "parity": "odd",
                }
            )
    return {"ap": ap, "external": external}


def build_inventory_payload() -> dict[str, Any]:
    keys = build_mode_inventory()
    anchors = build_anchor_inventory(keys)
    ladders = _load_json(DOMAIN_PATH)["domains"]["V3.1"]["boundary_ladders"]
    return {
        "schema": "schwo.phase6.v3_1.inventory.v1",
        "route_a": [key.payload() for key in keys],
        "route_a_mode_count": len(keys),
        "route_a_pair_count": len(keys) // 2,
        "route_b": anchors["ap"],
        "route_b_mode_count": len(anchors["ap"]),
        "route_c": anchors["external"],
        "route_c_mode_count": len(anchors["external"]),
        "ladders": ladders,
        "ordering": "frequency ordinal, ell ascending, parity odd then even",
        "nearest_critical_tie_rule": "smaller ell",
    }


def _publish(path: Path, payload: bytes) -> dict[str, Any]:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "wb", closefd=False) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(fd)
    os.chmod(path, 0o444)
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise V31ContractError(f"unsafe publication: {path}")
    return {"sha256": sha256(path), "size": info.st_size, "mode": 0o444, "nlink": 1}


def probe_external_runtime() -> dict[str, Any]:
    wolframscript = shutil.which("wolframscript")
    kernels = [
        path
        for path in (
            Path("/Applications/Mathematica.app/Contents/MacOS/WolframKernel"),
            Path("/Applications/Wolfram.app/Contents/MacOS/WolframKernel"),
            Path("/usr/local/bin/WolframKernel"),
            Path("/opt/homebrew/bin/WolframKernel"),
            WOLFRAM_KERNEL,
        )
        if path.is_file() and os.access(path, os.X_OK)
    ]
    return {
        "backend": "BlackHolePerturbationToolkit ReggeWheeler",
        "method_required": "MST or Numerical",
        "fresh_external_execution_required": True,
        "internal_fallback_permitted": False,
        "wolframscript": str(Path(wolframscript).resolve()) if wolframscript else None,
        "wolfram_kernel_candidates": [str(path.resolve()) for path in kernels],
        "available": bool(kernels),
        "status": "AVAILABLE" if kernels else "NOT_ASSESSED",
        "blocker": None if kernels else "NO_EXECUTABLE_WOLFRAM_KERNEL",
    }


def run_external_smoke(output_path: Path) -> dict[str, Any]:
    """Run one fresh odd-sector BHPT MST API smoke outside official evidence."""

    runtime = probe_external_runtime()
    if not runtime["available"] or WOLFRAM_KERNEL not in [
        Path(value) for value in runtime["wolfram_kernel_candidates"]
    ]:
        raise V31ContractError("exact external WolframKernel is unavailable")
    if sha256(WOLFRAM_KERNEL) != WOLFRAM_KERNEL_SHA256:
        raise V31ContractError("external WolframKernel identity drift")
    environment = os.environ.copy()
    environment.update(
        {
            "SCHWO_V31_BHPT_PACKAGE_ROOT": str(BHPT_PACKAGE_ROOT),
            "SCHWO_V31_BHPT_OUTPUT": str(output_path.resolve()),
        }
    )
    completed = subprocess.run(
        [str(WOLFRAM_KERNEL), "-noprompt", "-script", str(BHPT_SMOKE_WLS)],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=180.0,
    )
    if completed.returncode != 0 or completed.stderr:
        raise V31ContractError(
            f"BHPT smoke failed: exit={completed.returncode}, "
            f"stdout={completed.stdout[-500:]!r}, stderr={completed.stderr[-500:]!r}"
        )
    payload = _load_json(output_path)
    if (
        payload.get("schema") != "schwo.phase6.v3_1.bhpt_mst_smoke.v1"
        or payload.get("method") != "MST"
        or payload.get("parity") != "odd"
        or payload.get("fresh_external_call_count") != 1
    ):
        raise V31ContractError("BHPT smoke payload mismatch")
    return payload


def _runtime() -> dict[str, Any]:
    import numpy
    import scipy

    try:
        import mpmath
    except ImportError:
        mpmath = None
    return {
        "executable": str(Path(sys.executable).resolve(strict=True)),
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "numpy": numpy.__version__,
        "scipy": scipy.__version__,
        "mpmath": None if mpmath is None else mpmath.__version__,
        "platform": platform.platform(),
    }


def _terminal_payloads(
    *,
    state: str,
    inventory: dict[str, Any],
    run_contract: dict[str, Any],
    source_map: dict[str, Any],
    ladder_records: list[dict[str, Any]],
    blocker: str,
) -> dict[str, bytes]:
    certificates = [
        {
            "blocking_reason": blocker,
            "certificate_id": name,
            "status": "FAIL"
            if name == "V3_MODE_GREYBODY_NUMERICAL"
            else "NOT_ASSESSED",
        }
        for name in (
            "V3_MODE_GREYBODY_NUMERICAL",
            "V3_MODE_GREYBODY_FLUX_VS_S",
            "V3_MODE_GREYBODY_EXTERNAL",
            "V3_MODE_PARITY_PROBABILITY",
            "V3_MODE_DOMAIN_COVERAGE",
        )
    ]
    summary = {
        "schema": "schwo.phase6.v3_1.summary.v1",
        "overall_state": state,
        "route_a_completed": 0,
        "route_b_completed": 0,
        "route_c_completed": 0,
        "blocking_reason": blocker,
        "certificates": certificates,
        "global_status": None,
        "global_green_permitted": False,
        "independent_review_state": "NOT_ASSESSED",
    }
    report = {
        "schema": "schwo.phase6.v3_1.report.v1",
        "terminal": True,
        "candidate_success": False,
        "blocking_reason": blocker,
        "science_counts": {
            "route_a_attempted_solves": len(ladder_records),
            "route_a_completed_modes": 0,
            "route_b_solves": 0,
            "route_c_solves": 0,
        },
        "nonclaims": [
            "no V3.1 candidate PASS",
            "no V3.2",
            "no independent review",
            "no global GREEN",
        ],
    }
    return {
        "run_contract.json": canonical_bytes(run_contract),
        "inventory.json": canonical_bytes(inventory),
        "records.jsonl": b"",
        "ladder_records.jsonl": b"".join(
            canonical_bytes(item) for item in ladder_records
        ),
        "ap_records.jsonl": b"",
        "external_records.jsonl": b"",
        "uncertainty_budget.json": canonical_bytes(
            {
                "schema": "schwo.phase6.v3_1.uncertainty.v1",
                "status": "FAILED",
                "reason": blocker,
                "numerical_and_convention_budgets_combined": False,
            }
        ),
        "source_map.json": canonical_bytes(source_map),
        "summary.json": canonical_bytes(summary),
        "report.json": canonical_bytes(report),
    }


def run_official_candidate(output_root: Path) -> dict[str, Any]:
    """Run the frozen producer until its first terminal scientific failure."""

    from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
    from schwgw.numerics.boundary_conditions import BoundaryConfig
    from schwgw.numerics.radial_solver import solve_radial_mode

    output_root = output_root.resolve()
    output_root.mkdir(mode=0o700, parents=False, exist_ok=False)
    identities = verify_frozen_inputs()
    inventory = build_inventory_payload()
    external = probe_external_runtime()
    if not external["available"] or sha256(WOLFRAM_KERNEL) != WOLFRAM_KERNEL_SHA256:
        raise V31ContractError("official prelaunch external runtime identity failed")
    source_paths = [
        ROOT / "src/schwgw/scattering/absorption.py",
        Path(__file__).resolve(strict=True),
        ROOT / "scripts/phase6_v3_1_mode_greybody.py",
        BHPT_SMOKE_WLS,
    ]
    source_map = {
        "schema": "schwo.phase6.v3_1.source_map.v1",
        "frozen_inputs": identities,
        "implementation": {
            str(path.relative_to(ROOT)): {
                "path": str(path),
                "sha256": sha256(path),
                "size": path.stat().st_size,
            }
            for path in source_paths
        },
        "protected_files_unchanged": True,
        "external_runtime": {
            **external,
            "selected_kernel": str(WOLFRAM_KERNEL),
            "selected_kernel_sha256": WOLFRAM_KERNEL_SHA256,
        },
    }
    run_contract = {
        "schema": "schwo.phase6.v3_1.run_contract.v1",
        "created_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "claim_scope": "V3.1 exact mode-greybody candidate",
        "runtime": _runtime(),
        "inventory_sha256": hashlib.sha256(canonical_bytes(inventory)).hexdigest(),
        "external_runtime": source_map["external_runtime"],
        "science_authorized": True,
        "science_started": True,
        "resume_policy": "system interruption only under exact contract",
        "official_root": str(output_root),
    }
    first = build_mode_inventory()[0]
    k = float(first.kM)
    r_out_base = max(300.0, math.sqrt(first.ell * (first.ell + 1)) / k)
    node = {
        "axis": "r_in_eps",
        "atol": 1e-12,
        "ell": first.ell,
        "jost_order": 160,
        "kM": first.kM,
        "mode_ordinal": 0,
        "parity": first.parity,
        "r_in_eps": 1e-8,
        "r_out": r_out_base,
        "rtol": 1e-10,
        "schema": "schwo.phase6.v3_1.ladder_record.v1",
        "status": "RUNNING",
    }
    started = time.monotonic()
    try:
        solve_radial_mode(
            first.parity,
            first.ell,
            k,
            SchwarzschildBackground(),
            BoundaryConfig(
                r_in_eps=1e-8,
                r_out=r_out_base,
                rtol=1e-10,
                atol=1e-12,
                outer_series_order=160,
            ),
        )
    except Exception as exc:  # terminal native scientific failure is evidence
        node.update(
            {
                "elapsed_seconds": time.monotonic() - started,
                "exception_message": str(exc),
                "exception_type": type(exc).__name__,
                "status": "FAILED",
            }
        )
        blocker = f"ROUTE_A_FROZEN_LADDER_NODE_FAILED: {type(exc).__name__}: {exc}"
    else:
        node.update({"elapsed_seconds": time.monotonic() - started, "status": "PASS"})
        blocker = "OFFICIAL_RUNNER_INCOMPLETE_AFTER_UNEXPECTED_FIRST_NODE_PASS"
    payloads = _terminal_payloads(
        state="FAILED_SCIENTIFIC",
        inventory=inventory,
        run_contract=run_contract,
        source_map=source_map,
        ladder_records=[node],
        blocker=blocker,
    )
    published = {
        name: _publish(output_root / name, payload)
        for name, payload in payloads.items()
    }
    manifest = {
        "schema": "schwo.phase6.v3_1.manifest.v1",
        "artifacts": published,
        "terminal": True,
        "overall_state": "FAILED_SCIENTIFIC",
        "global_green_permitted": False,
    }
    manifest_identity = _publish(
        output_root / "manifest.json", canonical_bytes(manifest)
    )
    os.chmod(output_root, 0o555)
    validate_terminal_candidate(output_root)
    with tempfile.TemporaryDirectory(prefix="schwo_v31_terminal_reload_") as temporary:
        copy = Path(temporary) / output_root.name
        shutil.copytree(output_root, copy, copy_function=shutil.copy2)
        validate_terminal_candidate(copy)
    return {"root": str(output_root), "manifest": manifest_identity, "blocker": blocker}


def validate_terminal_candidate(root: Path) -> None:
    root = root.resolve(strict=True)
    manifest = _load_json(root / "manifest.json")
    if manifest["overall_state"] != "FAILED_SCIENTIFIC":
        raise V31ContractError("terminal candidate is not a scientific failure")
    for name, expected in manifest["artifacts"].items():
        path = root / name
        info = path.stat()
        if (
            sha256(path) != expected["sha256"]
            or info.st_size != expected["size"]
            or stat.S_IMODE(info.st_mode) != 0o444
            or info.st_nlink != 1
            or path.is_symlink()
        ):
            raise V31ContractError(f"terminal artifact identity mismatch: {name}")
    if _load_json(root / "inventory.json") != build_inventory_payload():
        raise V31ContractError("terminal inventory reconstruction failed")
    ladders = [
        json.loads(line)
        for line in (root / "ladder_records.jsonl").read_text().splitlines()
    ]
    if len(ladders) != 1 or ladders[0]["status"] != "FAILED":
        raise V31ContractError("terminal native failure record mismatch")


def publish_external_blocker_candidate(output_root: Path) -> dict[str, Any]:
    """Publish a terminal V3.1 NOT_ASSESSED candidate without science."""

    output_root = output_root.resolve()
    output_root.mkdir(mode=0o700, parents=False, exist_ok=False)
    identities = verify_frozen_inputs()
    inventory = build_inventory_payload()
    external = probe_external_runtime()
    if external["available"]:
        raise V31ContractError("external runtime is available; blocker path is invalid")
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    source_paths = [
        ROOT / "src/schwgw/scattering/absorption.py",
        Path(__file__).resolve(strict=True),
        ROOT / "scripts/phase6_v3_1_mode_greybody.py",
    ]
    source_map = {
        "schema": "schwo.phase6.v3_1.source_map.v1",
        "frozen_inputs": identities,
        "implementation": {
            str(path.relative_to(ROOT)): {
                "path": str(path),
                "sha256": sha256(path),
                "size": path.stat().st_size,
            }
            for path in source_paths
        },
        "protected_files_unchanged": True,
    }
    run_contract = {
        "schema": "schwo.phase6.v3_1.run_contract.v1",
        "created_at_utc": now,
        "claim_scope": "V3.1 exact mode-greybody candidate",
        "runtime": _runtime(),
        "inventory_sha256": hashlib.sha256(canonical_bytes(inventory)).hexdigest(),
        "external_runtime": external,
        "science_authorized": False,
        "science_started": False,
        "failure_policy": "blocking Route C unavailable; no Route A/B science launched",
    }
    empty = b""
    published: dict[str, dict[str, Any]] = {}
    for name, payload in (
        ("run_contract.json", canonical_bytes(run_contract)),
        ("inventory.json", canonical_bytes(inventory)),
        ("records.jsonl", empty),
        ("ladder_records.jsonl", empty),
        ("ap_records.jsonl", empty),
        ("external_records.jsonl", canonical_bytes(external)),
        (
            "uncertainty_budget.json",
            canonical_bytes(
                {
                    "schema": "schwo.phase6.v3_1.uncertainty.v1",
                    "status": "NOT_ASSESSED",
                    "reason": external["blocker"],
                }
            ),
        ),
        ("source_map.json", canonical_bytes(source_map)),
    ):
        published[name] = _publish(output_root / name, payload)
    certificates = [
        {
            "certificate_id": name,
            "status": "NOT_ASSESSED",
            "blocking_reason": external["blocker"],
        }
        for name in (
            "V3_MODE_GREYBODY_NUMERICAL",
            "V3_MODE_GREYBODY_FLUX_VS_S",
            "V3_MODE_GREYBODY_EXTERNAL",
            "V3_MODE_PARITY_PROBABILITY",
            "V3_MODE_DOMAIN_COVERAGE",
        )
    ]
    summary = {
        "schema": "schwo.phase6.v3_1.summary.v1",
        "overall_state": "FAILED_NOT_ASSESSED",
        "route_a_completed": 0,
        "route_b_completed": 0,
        "route_c_completed": 0,
        "blocking_reason": external["blocker"],
        "certificates": certificates,
        "global_status": None,
        "global_green_permitted": False,
        "independent_review_state": "NOT_ASSESSED",
    }
    report = {
        "schema": "schwo.phase6.v3_1.report.v1",
        "terminal": True,
        "candidate_success": False,
        "external_route": external,
        "science_counts": {
            "route_a_solves": 0,
            "route_b_solves": 0,
            "route_c_solves": 0,
        },
        "nonclaims": [
            "no V3.1 candidate PASS",
            "no V3.2",
            "no independent review",
            "no global GREEN",
        ],
    }
    published["summary.json"] = _publish(
        output_root / "summary.json", canonical_bytes(summary)
    )
    published["report.json"] = _publish(
        output_root / "report.json", canonical_bytes(report)
    )
    manifest = {
        "schema": "schwo.phase6.v3_1.manifest.v1",
        "artifacts": published,
        "terminal": True,
        "overall_state": "FAILED_NOT_ASSESSED",
        "global_green_permitted": False,
    }
    manifest_identity = _publish(
        output_root / "manifest.json", canonical_bytes(manifest)
    )
    os.chmod(output_root, 0o555)
    validate_blocker_candidate(output_root)
    with tempfile.TemporaryDirectory() as temporary:
        copy = Path(temporary) / output_root.name
        shutil.copytree(output_root, copy, copy_function=shutil.copy2)
        validate_blocker_candidate(copy, require_manifest_paths=False)
    return {
        "root": str(output_root),
        "manifest": manifest_identity,
        "inventory": inventory,
        "external": external,
    }


def validate_blocker_candidate(
    root: Path, *, require_manifest_paths: bool = True
) -> None:
    root = root.resolve(strict=True)
    manifest = _load_json(root / "manifest.json")
    if (
        manifest["overall_state"] != "FAILED_NOT_ASSESSED"
        or manifest["global_green_permitted"] is not False
    ):
        raise V31ContractError("invalid terminal blocker state")
    expected_names = {
        "run_contract.json",
        "inventory.json",
        "records.jsonl",
        "ladder_records.jsonl",
        "ap_records.jsonl",
        "external_records.jsonl",
        "uncertainty_budget.json",
        "source_map.json",
        "summary.json",
        "report.json",
    }
    if set(manifest["artifacts"]) != expected_names:
        raise V31ContractError("manifest artifact set mismatch")
    for name, expected in manifest["artifacts"].items():
        path = root / name
        info = path.stat()
        if sha256(path) != expected["sha256"] or info.st_size != expected["size"]:
            raise V31ContractError(f"artifact identity mismatch: {name}")
        if (
            stat.S_IMODE(info.st_mode) != 0o444
            or info.st_nlink != 1
            or path.is_symlink()
        ):
            raise V31ContractError(f"artifact immutability mismatch: {name}")
    inventory = _load_json(root / "inventory.json")
    if inventory != build_inventory_payload():
        raise V31ContractError("inventory cannot be independently reconstructed")
    summary = _load_json(root / "summary.json")
    if len(summary["certificates"]) != 5 or any(
        item["status"] != "NOT_ASSESSED" for item in summary["certificates"]
    ):
        raise V31ContractError("certificate fail-closed state mismatch")
    if require_manifest_paths:
        verify_frozen_inputs()
