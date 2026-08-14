"""Full-domain Phase-6 V1 radial baseline with repaired inner/outer boundaries."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
import fcntl
import hashlib
import json
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
from schwgw.validation.phase6_conditioning_scan import load_frozen_scan_contract
from schwgw.validation.phase6_domain import RadialKey


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RUNNER_PATH = PROJECT_ROOT / "scripts" / "phase6_run_v1_final_radial_baseline.py"
DOMAIN_ROOT = PROJECT_ROOT / "runs/phase6/v1_domain_freeze_v3_20260806"
EXECUTION_ROOT = PROJECT_ROOT / "runs/phase6/v1_execution_contract_v4_20260806"
PLAN_SCHEMA = "schwgw_phase6_v1_final_radial_baseline_plan_v1"
RECORD_SCHEMA = "schwgw_phase6_v1_final_radial_baseline_record_v1"
SUMMARY_SCHEMA = "schwgw_phase6_v1_final_radial_baseline_summary_v1"
MANIFEST_SCHEMA = "schwgw_phase6_v1_final_radial_baseline_manifest_v1"
EXPECTED_KEY_COUNT = 17_818
EXPECTED_UNION_SHA256 = (
    "a5793564dfc28e815699966208ae6605eeeedce9e3629f09512b70e08196810b"
)
R_IN_EPS = 1.0e-9
REQUESTED_R_OUT_M = 300.0
REQUIRED_RADIUS_M = 40.0
JOST_ORDER = 160
RTOL = 1.0e-10
ATOL = 1.0e-12
FLUX_THRESHOLD = 1.0e-8
FORMAL_ROOT_MODE = 0o555
FORMAL_FILE_MODE = 0o444


class V1FinalBaselineError(ValueError):
    """Raised when the full-domain plan, checkpoint, or evidence drifts."""


def canonical_jsonl_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _identity(path: Path, *, formal: bool = False) -> dict[str, object]:
    absolute = path.absolute()
    info = absolute.lstat()
    if (
        absolute.is_symlink()
        or not stat.S_ISREG(info.st_mode)
        or info.st_nlink != 1
        or (formal and stat.S_IMODE(info.st_mode) != FORMAL_FILE_MODE)
    ):
        raise V1FinalBaselineError(f"invalid file identity: {absolute}")
    return {
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
        "path": str(absolute),
        "sha256": sha256_file(absolute),
        "size": info.st_size,
    }


def _exclusive_json(path: Path, payload: object) -> dict[str, object]:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as handle:
            handle.write(canonical_json_bytes(payload))
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        os.close(descriptor)
    os.chmod(path, FORMAL_FILE_MODE)
    return _identity(path, formal=True)


def _complex_record(value: complex) -> dict[str, str]:
    return {
        "abs": format(abs(value), ".17g"),
        "imag": format(value.imag, ".17g"),
        "real": format(value.real, ".17g"),
    }


def _solve_key(payload: tuple[int, dict[str, object]]) -> dict[str, object]:
    ordinal, key = payload
    started = time.monotonic()
    try:
        request = ConditionedRadialRequest(
            sector=Sector(str(key["sector"])),
            ell=int(key["ell"]),
            k=float(key["kM"]),
            required_radius=REQUIRED_RADIUS_M,
            r_out=REQUESTED_R_OUT_M,
            r_in_eps=R_IN_EPS,
            rtol=RTOL,
            atol=ATOL,
            outer_series_order=JOST_ORDER,
        )
        result = solve_adaptive_jost_radial_at_radius(
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
                    "selected_jost_series_residual"
                ],
                "jost_maximum_tail_ratio": diagnostics["selected_jost_tail_ratio"],
                "selected_r_out_M": diagnostics["selected_r_out"],
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


def _validate_record(record: object, expected: RadialKey, ordinal: int) -> None:
    if not isinstance(record, Mapping):
        raise V1FinalBaselineError("record is not an object")
    if (
        record.get("schema") != RECORD_SCHEMA
        or record.get("ordinal") != ordinal
        or record.get("key") != expected.to_record()
        or record.get("state") not in {"PASS", "FAIL"}
        or record.get("scientific_acceptance") is not False
    ):
        raise V1FinalBaselineError("record identity/state changed")
    if record["state"] == "PASS":
        if record.get("failure") is not None:
            raise V1FinalBaselineError("PASS record carries a failure")
        invariants = record.get("invariants")
        if not isinstance(invariants, Mapping) or not all(
            value is True for value in invariants.values()
        ):
            raise V1FinalBaselineError("PASS record invariants changed")
    elif not isinstance(record.get("failure"), str):
        raise V1FinalBaselineError("FAIL record lacks a reason")


def _load_records(path: Path, keys: tuple[RadialKey, ...]) -> list[dict[str, object]]:
    if not path.exists():
        return []
    if path.is_symlink() or not path.is_file() or path.stat().st_nlink != 1:
        raise V1FinalBaselineError("records checkpoint identity changed")
    records: list[dict[str, object]] = []
    with path.open("rb") as handle:
        for ordinal, line in enumerate(handle):
            if not line.endswith(b"\n"):
                raise V1FinalBaselineError("records checkpoint has a partial line")
            try:
                record = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                raise V1FinalBaselineError(
                    "records checkpoint JSON is invalid"
                ) from exc
            if line != canonical_jsonl_bytes(record):
                raise V1FinalBaselineError("records checkpoint is noncanonical")
            if ordinal >= len(keys):
                raise V1FinalBaselineError("records checkpoint exceeds D_union")
            _validate_record(record, keys[ordinal], ordinal)
            records.append(dict(record))
    return records


@contextmanager
def _writer_lock(root: Path) -> Iterator[None]:
    lock = root / "writer.lock"
    descriptor = os.open(lock, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise V1FinalBaselineError(
                "another final-baseline writer is active"
            ) from exc
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _plan(keys: tuple[RadialKey, ...], *, limit: int | None) -> dict[str, object]:
    union_path = PROJECT_ROOT / "runs/phase6/v1_domain_freeze_v3_20260806/D_union.jsonl"
    if sha256_file(union_path) != EXPECTED_UNION_SHA256:
        raise V1FinalBaselineError("frozen D_union hash changed")
    return {
        "configuration": {
            "atol": ATOL,
            "jost_order": JOST_ORDER,
            "r_in_eps": R_IN_EPS,
            "requested_r_out_M": REQUESTED_R_OUT_M,
            "required_radius_M": REQUIRED_RADIUS_M,
            "rtol": RTOL,
        },
        "domain": {
            "D_union_sha256": EXPECTED_UNION_SHA256,
            "execution_count": len(keys),
            "full_count": EXPECTED_KEY_COUNT,
            "limit": limit,
        },
        "global_green_permitted": False,
        "implementation_sources": {
            "adaptive_jost_radial.py": sha256_file(
                PROJECT_ROOT / "src/schwgw/numerics/adaptive_jost_radial.py"
            ),
            "conditioned_radial.py": sha256_file(
                PROJECT_ROOT / "src/schwgw/numerics/conditioned_radial.py"
            ),
            "runner": sha256_file(RUNNER_PATH),
            "scaled_tortoise_radial.py": sha256_file(
                PROJECT_ROOT / "src/schwgw/numerics/scaled_tortoise_radial.py"
            ),
            "validation_module": sha256_file(Path(__file__)),
        },
        "li_figure_agreement_primary_gate": False,
        "schema": PLAN_SCHEMA,
    }


def run_final_baseline(
    *,
    output_root: str | Path,
    workers: int,
    resume: bool = False,
    limit: int | None = None,
) -> int:
    """Run or resume the exact ordered D_union campaign and seal on completion."""

    if workers < 1:
        raise V1FinalBaselineError("workers must be positive")
    contract = load_frozen_scan_contract(DOMAIN_ROOT, EXECUTION_ROOT)
    all_keys = contract.union_keys
    if len(all_keys) != EXPECTED_KEY_COUNT:
        raise V1FinalBaselineError("D_union cardinality changed")
    if limit is not None:
        if limit < 1 or limit > EXPECTED_KEY_COUNT:
            raise V1FinalBaselineError("limit must lie in [1,17818]")
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
            raise V1FinalBaselineError(
                "resume root must be a direct mutable 0700 directory"
            )
    else:
        if root.exists() or root.is_symlink():
            raise V1FinalBaselineError("fresh output root must be absent")
        root.mkdir(parents=True, mode=0o700)
        os.chmod(root, 0o700)
        _exclusive_json(root / "plan.json", _plan(keys, limit=limit))
    with _writer_lock(root):
        plan = json.loads((root / "plan.json").read_bytes())
        if plan != _plan(keys, limit=limit):
            raise V1FinalBaselineError("resume plan changed")
        records_path = root / "records.jsonl"
        records = _load_records(records_path, keys)
        start_ordinal = len(records)
        started = time.monotonic()
        if start_ordinal < len(keys):
            flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            descriptor = os.open(records_path, flags, 0o600)
            try:
                with os.fdopen(descriptor, "ab", closefd=False) as handle:
                    payloads = (
                        (ordinal, keys[ordinal].to_record())
                        for ordinal in range(start_ordinal, len(keys))
                    )
                    with ProcessPoolExecutor(max_workers=workers) as executor:
                        for record in executor.map(_solve_key, payloads, chunksize=1):
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
            "acceptance_scope": "full D_union repaired-boundary algorithmic baseline",
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
        identities["summary.json"] = _exclusive_json(root / "summary.json", summary)
        manifest = {
            "artifacts": identities,
            "global_green_permitted": False,
            "overall_state": overall,
            "schema": MANIFEST_SCHEMA,
        }
        _exclusive_json(root / "manifest.json", manifest)
        os.chmod(root, FORMAL_ROOT_MODE)
    validate_published_final_baseline(root)
    return 0 if overall in {"PASS", "PARTIAL"} else 2


def validate_published_final_baseline(root_path: str | Path) -> dict[str, object]:
    root = Path(root_path).absolute()
    info = root.lstat()
    if (
        root.is_symlink()
        or root.resolve(strict=True) != root
        or not stat.S_ISDIR(info.st_mode)
        or stat.S_IMODE(info.st_mode) != FORMAL_ROOT_MODE
    ):
        raise V1FinalBaselineError("final-baseline root is not immutable 0555")
    manifest = json.loads((root / "manifest.json").read_bytes())
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise V1FinalBaselineError("final-baseline manifest changed")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, Mapping):
        raise V1FinalBaselineError("final-baseline artifact ledger missing")
    if {path.name for path in root.iterdir() if path.is_file()} != {
        *artifacts,
        "manifest.json",
    }:
        raise V1FinalBaselineError("final-baseline inventory changed")
    for name, expected in artifacts.items():
        if _identity(root / str(name), formal=True) != expected:
            raise V1FinalBaselineError(f"final-baseline identity changed: {name}")
    summary = json.loads((root / "summary.json").read_bytes())
    plan = json.loads((root / "plan.json").read_bytes())
    if summary.get("schema") != SUMMARY_SCHEMA or plan.get("schema") != PLAN_SCHEMA:
        raise V1FinalBaselineError("final-baseline schema changed")
    contract = load_frozen_scan_contract(DOMAIN_ROOT, EXECUTION_ROOT)
    count = int(plan["domain"]["execution_count"])
    keys = contract.union_keys[:count]
    records = _load_records(root / "records.jsonl", keys)
    if (
        len(records) != summary.get("completed_key_count")
        or sha256_file(root / "records.jsonl") != summary.get("records_sha256")
        or summary.get("global_green_permitted") is not False
    ):
        raise V1FinalBaselineError("final-baseline summary linkage changed")
    return dict(summary)


__all__ = [
    "MANIFEST_SCHEMA",
    "PLAN_SCHEMA",
    "RECORD_SCHEMA",
    "SUMMARY_SCHEMA",
    "V1FinalBaselineError",
    "run_final_baseline",
    "validate_published_final_baseline",
]
