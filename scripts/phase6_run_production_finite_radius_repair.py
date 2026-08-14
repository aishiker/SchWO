#!/usr/bin/env python3
"""Run the resumable Phase-6 production eight-radius repair diagnostic."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import stat
import sys
from time import perf_counter, time
from typing import Any

from schwgw.numerics.scaled_tortoise_radial import (
    solve_scaled_tortoise_radial_at_radius,
)
from schwgw.validation.phase6_domain import (
    canonical_json_bytes,
    sha256_bytes,
    source_file_identity,
)
from schwgw.validation.phase6_production_finite_radius_repair import (
    RepairInventory,
    RepairMode,
    RepairSolver,
    execute_repair_mode,
    load_repair_inventory,
    repair_key_id,
    validate_repair_record,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CAMPAIGN_ROOT = (
    PROJECT_ROOT / "runs/phase6/radial_validation/"
    "v1_production_finite_radius_campaign_v1_20260808_py314"
)
DEFAULT_DOMAIN_ROOT = PROJECT_ROOT / "runs/phase6/v1_domain_freeze_v3_20260806"
DEFAULT_EXECUTION_ROOT = PROJECT_ROOT / "runs/phase6/v1_execution_contract_v4_20260806"
CONTRACT_SCHEMA = "schwgw.phase6.production_finite_radius_repair_contract.v1"
RESULT_SCHEMA = "schwgw.phase6.production_finite_radius_repair_result.v1"
MANIFEST_SCHEMA = "schwgw.phase6.production_finite_radius_repair_manifest.v1"


class RepairRunError(RuntimeError):
    """Raised on a structural, provenance, or single-writer violation."""


def _strict_json(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON constant: {token}")
            ),
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise RepairRunError(f"cannot load canonical JSON: {path}") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
        raise RepairRunError(f"artifact is not canonical JSON: {path}")
    return value


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _publish_bytes(path: Path, data: bytes, *, mode: int = 0o444) -> None:
    """Publish bytes once using O_EXCL staging plus an atomic hard-link."""

    staging_dir = path.parent / ".staging"
    staging_dir.mkdir(mode=0o700, exist_ok=True)
    staging = staging_dir / f"{path.name}.{os.getpid()}.{time():.9f}.pending"
    descriptor = os.open(staging, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.close(descriptor)
        descriptor = -1
        os.chmod(staging, mode)
        try:
            os.link(staging, path)
        except FileExistsError as exc:
            raise RepairRunError(f"refusing to overwrite artifact: {path}") from exc
        _fsync_directory(path.parent)
        os.unlink(staging)
        _fsync_directory(staging_dir)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if staging.exists():
            os.unlink(staging)


def _publish_json(path: Path, payload: Mapping[str, Any]) -> None:
    _publish_bytes(path, canonical_json_bytes(payload))


def _validate_identity(
    path: Path, expected: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    identity = source_file_identity(path)
    if identity["mode"] != 0o444 or identity["nlink"] != 1:
        raise RepairRunError(f"artifact is not immutable 0444/nlink1: {path}")
    if expected is not None and identity != dict(expected):
        raise RepairRunError(f"artifact identity mismatch: {path}")
    return identity


def _implementation_paths() -> dict[str, Path]:
    return {
        "repair_module": PROJECT_ROOT
        / "src/schwgw/validation/phase6_production_finite_radius_repair.py",
        "repair_runner": Path(__file__).resolve(),
        "scaled_tortoise_backend": PROJECT_ROOT
        / "src/schwgw/numerics/scaled_tortoise_radial.py",
        "conditioned_radial_types": PROJECT_ROOT
        / "src/schwgw/numerics/conditioned_radial.py",
        "jost_matching": PROJECT_ROOT / "src/schwgw/numerics/matching.py",
        "schwarzschild_background": PROJECT_ROOT
        / "src/schwgw/backgrounds/schwarzschild.py",
        "background_base": PROJECT_ROOT / "src/schwgw/backgrounds/base.py",
        "perturbation_potentials": PROJECT_ROOT
        / "src/schwgw/perturbations/potentials.py",
        "perturbation_sectors": PROJECT_ROOT / "src/schwgw/perturbations/sectors.py",
        "phase6_domain": PROJECT_ROOT / "src/schwgw/validation/phase6_domain.py",
        "production_gate": PROJECT_ROOT
        / "src/schwgw/validation/phase6_production_finite_radius.py",
        "production_campaign_validator": PROJECT_ROOT
        / "src/schwgw/validation/phase6_production_finite_radius_campaign.py",
    }


def _source_identities() -> dict[str, dict[str, Any]]:
    return {
        name: source_file_identity(path)
        for name, path in _implementation_paths().items()
    }


def _source_hashes(identities: Mapping[str, Mapping[str, Any]]) -> dict[str, str]:
    return {name: str(identity["sha256"]) for name, identity in identities.items()}


def _selection_hash(modes: Sequence[RepairMode]) -> str:
    return sha256_bytes(canonical_json_bytes([mode.to_record() for mode in modes]))


def _contract(
    inventory: RepairInventory,
    modes: Sequence[RepairMode],
    *,
    limit: int | None,
    implementation_identities: Mapping[str, Mapping[str, Any]],
    kernel_unit_test_only: bool,
) -> dict[str, Any]:
    return {
        "schema": CONTRACT_SCHEMA,
        "predecessor_campaign_root": str(inventory.campaign_root),
        "predecessor_campaign_result_identity": dict(
            inventory.campaign_result_identity
        ),
        "predecessor_campaign_manifest_identity": dict(
            inventory.campaign_manifest_identity
        ),
        "full_failure_mode_count": len(inventory.modes),
        "full_failure_inventory_sha256": inventory.inventory_sha256,
        "selected_mode_count": len(modes),
        "selected_mode_inventory_sha256": _selection_hash(modes),
        "limit": limit,
        "one_solve_per_key": True,
        "exact_table_i_eight_radii": [
            site.to_record() for site in inventory.frozen.sites
        ],
        "implementation_source_identities": {
            name: dict(identity) for name, identity in implementation_identities.items()
        },
        "implementation_source_sha256s": _source_hashes(implementation_identities),
        "python_executable": str(Path(sys.executable).resolve()),
        "python_version": sys.version,
        "kernel_unit_test_only": kernel_unit_test_only,
        "science_executed": not kernel_unit_test_only,
        "scientific_evidence": not kernel_unit_test_only,
        "diagnostic_only": True,
        "scientific_acceptance": False,
        "global_green_permitted": False,
        "resume_policy": "strict_per_key_no_overwrite",
        "single_writer": True,
    }


def _record_filename(mode: RepairMode) -> str:
    token = mode.key.kM.replace(".", "p")
    return (
        f"record_{mode.ordinal:04d}__k{token}__{mode.key.sector}"
        f"__ell{mode.key.ell:04d}.json"
    )


def _validate_current_sources(contract: Mapping[str, Any]) -> None:
    expected = contract.get("implementation_source_identities")
    if not isinstance(expected, Mapping):
        raise RepairRunError("implementation source ledger is missing")
    observed = _source_identities()
    if observed != expected or _source_hashes(observed) != contract.get(
        "implementation_source_sha256s"
    ):
        raise RepairRunError("implementation source bytes changed since root creation")


def _load_record(
    path: Path, mode: RepairMode, inventory: RepairInventory
) -> dict[str, Any]:
    _validate_identity(path)
    record = _strict_json(path)
    validate_repair_record(record, mode=mode, sites=inventory.frozen.sites)
    return record


@contextmanager
def _writer_lock(root: Path):
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock_path = root / "writer.lock"
    try:
        descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
        os.write(descriptor, f"pid={os.getpid()}\n".encode())
        os.fsync(descriptor)
    except FileExistsError:
        descriptor = os.open(lock_path, os.O_RDWR)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RepairRunError(f"another writer owns {root}") from exc
        yield lock_path
    finally:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


def _resume_records(
    records_dir: Path,
    modes: Sequence[RepairMode],
    inventory: RepairInventory,
) -> dict[int, dict[str, Any]]:
    expected_names = {_record_filename(mode): mode for mode in modes}
    actual = {path.name: path for path in records_dir.glob("*.json")}
    unknown = set(actual) - set(expected_names)
    if unknown:
        raise RepairRunError(f"unknown records in resumable root: {sorted(unknown)}")
    records: dict[int, dict[str, Any]] = {}
    for name, path in actual.items():
        mode = expected_names[name]
        records[mode.ordinal] = _load_record(path, mode, inventory)
    return records


def _summary(
    inventory: RepairInventory,
    modes: Sequence[RepairMode],
    records: Sequence[Mapping[str, Any]],
    contract_identity: Mapping[str, Any],
    record_identities: Sequence[Mapping[str, Any]],
    *,
    elapsed_seconds: float,
    kernel_unit_test_only: bool,
) -> dict[str, Any]:
    measured = sum(record["status"] == "MEASURED" for record in records)
    failed = len(records) - measured
    failure_ledger = [
        {
            "ordinal": record["ordinal"],
            "key": record["key"],
            "failures": record["failures"],
        }
        for record in records
        if record["status"] == "FAIL"
    ]
    return {
        "schema": RESULT_SCHEMA,
        "overall_state": "FAIL" if failed else "PARTIAL",
        "selected_mode_count": len(modes),
        "terminal_mode_count": len(records),
        "measured_mode_count": measured,
        "failed_mode_count": failed,
        "radial_state_record_count": 8 * measured,
        "solver_call_count": len(records),
        "failure_ledger": failure_ledger,
        "full_failure_mode_count": len(inventory.modes),
        "full_failure_inventory_sha256": inventory.inventory_sha256,
        "selected_mode_inventory_sha256": _selection_hash(modes),
        "contract_identity": dict(contract_identity),
        "record_identities": [dict(identity) for identity in record_identities],
        "implementation_source_sha256s": _source_hashes(_source_identities()),
        "elapsed_seconds_this_invocation": elapsed_seconds,
        "kernel_unit_test_only": kernel_unit_test_only,
        "science_executed": not kernel_unit_test_only,
        "scientific_evidence": not kernel_unit_test_only,
        "diagnostic_only": True,
        "scientific_acceptance": False,
        "global_green_permitted": False,
        "scope_qualification": {
            "production_radial_states": "ASSESSED",
            "observer_response": "NOT_ASSESSED",
            "detector_response": "NOT_ASSESSED",
            "infinity_waveform": "NOT_ASSESSED",
            "polarization_convention": "NOT_ASSESSED",
        },
        "numerical_uncertainty": {
            "status": "NOT_CLOSED",
            "upper_bound": None,
            "pending": "independent_solver_and_parameter_ladders",
        },
        "convention_uncertainty": {
            "status": "NOT_ASSESSED",
            "upper_bound": None,
            "pending": "observer_tetrad_polarization_convention",
        },
    }


def _seal(
    root: Path,
    records_dir: Path,
    staging_dirs: Sequence[Path],
    lock_path: Path,
) -> None:
    for directory in staging_dirs:
        if any(directory.iterdir()):
            raise RepairRunError(f"staging directory is not empty: {directory}")
        os.chmod(directory, 0o555)
    os.chmod(records_dir, 0o555)
    os.chmod(lock_path, 0o444)
    os.chmod(root, 0o555)
    _fsync_directory(root.parent)


def reload_completed_root(
    root: Path,
    *,
    inventory: RepairInventory,
    modes: Sequence[RepairMode],
) -> dict[str, Any]:
    """Fully reload a sealed root, including every record identity and claim."""

    if not root.is_dir() or stat.S_IMODE(root.stat().st_mode) != 0o555:
        raise RepairRunError(f"completed repair root is not sealed 0555: {root}")
    contract_path = root / "run_contract.json"
    result_path = root / "run_result.json"
    manifest_path = root / "manifest.json"
    contract_identity = _validate_identity(contract_path)
    result_identity = _validate_identity(result_path)
    _validate_identity(manifest_path)
    contract = _strict_json(contract_path)
    _validate_current_sources(contract)
    records_dir = root / "records"
    records: list[dict[str, Any]] = []
    record_identities: list[dict[str, Any]] = []
    for mode in modes:
        path = records_dir / _record_filename(mode)
        records.append(_load_record(path, mode, inventory))
        record_identities.append(_validate_identity(path))
    if {path.name for path in records_dir.glob("*.json")} != {
        _record_filename(mode) for mode in modes
    }:
        raise RepairRunError("sealed root record coverage changed")
    result = _strict_json(result_path)
    if result.get("contract_identity") != contract_identity:
        raise RepairRunError("result does not bind run contract")
    if result.get("record_identities") != record_identities:
        raise RepairRunError("result record identity ledger changed")
    expected_manifest = {
        "schema": MANIFEST_SCHEMA,
        "status": "COMPLETE",
        "global_green_permitted": False,
        "contract_identity": contract_identity,
        "result_identity": result_identity,
        "record_count": len(modes),
        "record_inventory_sha256": sha256_bytes(
            canonical_json_bytes(record_identities)
        ),
    }
    if _strict_json(manifest_path) != expected_manifest:
        raise RepairRunError("sealed root manifest changed")
    if result.get("selected_mode_count") != len(modes):
        raise RepairRunError("sealed result mode count changed")
    if result.get("scientific_acceptance") is not False:
        raise RepairRunError("sealed diagnostic was promoted to acceptance")
    return result


def run(
    output_root: Path,
    *,
    campaign_root: Path = DEFAULT_CAMPAIGN_ROOT,
    domain_root: Path = DEFAULT_DOMAIN_ROOT,
    execution_root: Path = DEFAULT_EXECUTION_ROOT,
    limit: int | None = None,
    solver: RepairSolver = solve_scaled_tortoise_radial_at_radius,
    kernel_unit_test_only: bool = False,
) -> dict[str, Any]:
    """Run or strictly resume the selected repair inventory and seal it once."""

    if limit is not None and (isinstance(limit, bool) or limit <= 0):
        raise RepairRunError("--limit must be a positive integer")
    inventory = load_repair_inventory(
        campaign_root,
        domain_root=domain_root,
        execution_root=execution_root,
    )
    modes = inventory.modes if limit is None else inventory.modes[:limit]
    if not modes:
        raise RepairRunError("repair selection is empty")
    output_root = output_root.resolve()
    if output_root.exists() and stat.S_IMODE(output_root.stat().st_mode) == 0o555:
        return reload_completed_root(output_root, inventory=inventory, modes=modes)

    started = perf_counter()
    with _writer_lock(output_root) as lock_path:
        if stat.S_IMODE(output_root.stat().st_mode) != 0o700:
            raise RepairRunError("resumable repair root must remain mode 0700")
        records_dir = output_root / "records"
        records_dir.mkdir(mode=0o700, exist_ok=True)
        (output_root / ".staging").mkdir(mode=0o700, exist_ok=True)
        (records_dir / ".staging").mkdir(mode=0o700, exist_ok=True)

        identities = _source_identities()
        expected_contract = _contract(
            inventory,
            modes,
            limit=limit,
            implementation_identities=identities,
            kernel_unit_test_only=kernel_unit_test_only,
        )
        contract_path = output_root / "run_contract.json"
        if contract_path.exists():
            _validate_identity(contract_path)
            if _strict_json(contract_path) != expected_contract:
                raise RepairRunError("resume contract differs from original invocation")
        else:
            _publish_json(contract_path, expected_contract)
        _validate_current_sources(expected_contract)

        completed = _resume_records(records_dir, modes, inventory)
        for index, mode in enumerate(modes, start=1):
            if mode.ordinal in completed:
                continue
            record = execute_repair_mode(
                mode,
                inventory.frozen.sites,
                solver=solver,
            )
            path = records_dir / _record_filename(mode)
            _publish_json(path, record)
            completed[mode.ordinal] = _load_record(path, mode, inventory)
            if index == 1 or index % 25 == 0 or index == len(modes):
                snapshot = {
                    "completed": len(completed),
                    "failed": sum(
                        item["status"] == "FAIL" for item in completed.values()
                    ),
                    "remaining": len(modes) - len(completed),
                    "last_key": repair_key_id(mode.key),
                }
                print(json.dumps(snapshot, sort_keys=True), flush=True)

        ordered_records = [completed[mode.ordinal] for mode in modes]
        contract_identity = _validate_identity(contract_path)
        record_identities = [
            _validate_identity(records_dir / _record_filename(mode)) for mode in modes
        ]
        result = _summary(
            inventory,
            modes,
            ordered_records,
            contract_identity,
            record_identities,
            elapsed_seconds=perf_counter() - started,
            kernel_unit_test_only=kernel_unit_test_only,
        )
        result_path = output_root / "run_result.json"
        manifest_path = output_root / "manifest.json"
        if result_path.exists() or manifest_path.exists():
            raise RepairRunError("refusing to republish a terminal artifact")
        _publish_json(result_path, result)
        result_identity = _validate_identity(result_path)
        manifest = {
            "schema": MANIFEST_SCHEMA,
            "status": "COMPLETE",
            "global_green_permitted": False,
            "contract_identity": contract_identity,
            "result_identity": result_identity,
            "record_count": len(modes),
            "record_inventory_sha256": sha256_bytes(
                canonical_json_bytes(record_identities)
            ),
        }
        _publish_json(manifest_path, manifest)
        _seal(
            output_root,
            records_dir,
            (output_root / ".staging", records_dir / ".staging"),
            lock_path,
        )
    return reload_completed_root(output_root, inventory=inventory, modes=modes)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--campaign-root", type=Path, default=DEFAULT_CAMPAIGN_ROOT)
    parser.add_argument("--domain-root", type=Path, default=DEFAULT_DOMAIN_ROOT)
    parser.add_argument("--execution-root", type=Path, default=DEFAULT_EXECUTION_ROOT)
    parser.add_argument("--limit", type=int)
    return parser


def main() -> int:
    args = _parser().parse_args()
    result = run(
        args.output_root,
        campaign_root=args.campaign_root,
        domain_root=args.domain_root,
        execution_root=args.execution_root,
        limit=args.limit,
    )
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
