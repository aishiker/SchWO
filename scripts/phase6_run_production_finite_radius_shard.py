#!/usr/bin/env python3
"""Run exactly one immutable Phase-6 production finite-radius shard."""

from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import stat
import sys

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from schwgw.numerics.conditioned_radial import (  # noqa: E402
    ConditionedRadialResult,
    solve_conditioned_radial_at_radius,
)
from schwgw.validation.phase6_conditioning_scan import (  # noqa: E402
    OuterSelection,
    select_outer_boundary,
)
from schwgw.validation.phase6_domain import (  # noqa: E402
    RadialKey,
    canonical_json_bytes,
    source_file_identity,
)
from schwgw.validation.phase6_production_finite_radius import (  # noqa: E402
    DEFAULT_POLICY,
    KEY_TERMINAL_SCHEMA,
    MANIFEST_SCHEMA,
    RUN_CONTRACT_SCHEMA,
    SHARD_FAILURE_SCHEMA,
    SHARD_RESULT_SCHEMA,
    FrozenProductionContract,
    TableISite,
    execute_production_finite_radius_key,
    key_artifact_filenames,
    load_frozen_production_contract,
    scientific_context_hash,
    source_hash_map,
    validate_solver_payload,
)


DOMAIN_ROOT = ROOT / "runs/phase6/v1_domain_freeze_v3_20260806"
EXECUTION_ROOT = ROOT / "runs/phase6/v1_execution_contract_v4_20260806"
MODULE_SOURCE = ROOT / "src/schwgw/validation/phase6_production_finite_radius.py"
RUNNER_SOURCE = Path(__file__).resolve()
CONDITIONING_SOURCE = ROOT / "src/schwgw/validation/phase6_conditioning_scan.py"
CONDITIONED_SOURCE = ROOT / "src/schwgw/numerics/conditioned_radial.py"
MATCHING_SOURCE = ROOT / "src/schwgw/numerics/matching.py"
POTENTIAL_SOURCE = ROOT / "src/schwgw/perturbations/potentials.py"
BACKGROUND_SOURCE = ROOT / "src/schwgw/backgrounds/schwarzschild.py"
BACKGROUND_BASE_SOURCE = ROOT / "src/schwgw/backgrounds/base.py"
DOMAIN_SOURCE = ROOT / "src/schwgw/validation/phase6_domain.py"
EXECUTION_SOURCE = ROOT / "src/schwgw/validation/phase6_execution_contract.py"
DOC_SOURCE = ROOT / "docs/phase6_production_finite_radius_v1.md"


class ShardRunError(RuntimeError):
    """Raised after an infrastructure/protocol failure is sealed durably."""


def _implementation_paths() -> dict[str, Path]:
    return {
        "background_base": BACKGROUND_BASE_SOURCE,
        "conditioned_backend": CONDITIONED_SOURCE,
        "conditioning_selector": CONDITIONING_SOURCE,
        "domain_contract_module": DOMAIN_SOURCE,
        "execution_contract_module": EXECUTION_SOURCE,
        "matching": MATCHING_SOURCE,
        "phase6_production_doc": DOC_SOURCE,
        "production_gate_module": MODULE_SOURCE,
        "production_gate_runner": RUNNER_SOURCE,
        "schwarzschild_background": BACKGROUND_SOURCE,
        "rw_zerilli_potentials": POTENTIAL_SOURCE,
    }


def _implementation_identities() -> dict[str, Mapping[str, object]]:
    identities: dict[str, Mapping[str, object]] = {}
    for name, path in _implementation_paths().items():
        if path.is_symlink() or not path.is_file():
            raise ShardRunError(f"implementation source is missing or aliased: {path}")
        identity = source_file_identity(path)
        if identity["nlink"] != 1:
            raise ShardRunError(
                f"implementation source has ambiguous hardlinks: {path}"
            )
        identities[name] = identity
    return identities


def _runtime_identity() -> dict[str, object]:
    return {
        "executable": str(Path(sys.executable).resolve(strict=True)),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "scipy": scipy.__version__,
    }


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _publish_json_exclusive(path: Path, payload: object) -> dict[str, object]:
    """Publish canonical JSON by O_EXCL staging, hardlink, chmod, and fsync."""

    if path.exists() or path.is_symlink():
        raise FileExistsError(f"refusing to replace artifact: {path}")
    staging = path.parent / f".{path.name}.o_excl_staging.{os.getpid()}"
    data = canonical_json_bytes(payload)
    descriptor: int | None = None
    try:
        descriptor = os.open(staging, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            descriptor = None
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(staging, path)
        os.chmod(path, 0o444)
        staging.unlink()
        _fsync_directory(path.parent)
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        if staging.exists() and not staging.is_symlink():
            staging.unlink()
        raise
    identity = source_file_identity(path)
    if identity["mode"] != 0o444 or identity["nlink"] != 1:
        raise ShardRunError(f"published identity is not immutable: {path}")
    return identity


def _strict_json(path: Path) -> dict[str, object]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON constant: {token}")
            ),
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise ShardRunError(f"cannot parse canonical JSON: {path}") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
        raise ShardRunError(f"artifact is not canonical JSON: {path}")
    return value


def _validate_identity(path: Path, expected: Mapping[str, object]) -> None:
    if set(expected) != {"mode", "nlink", "path", "sha256", "size"}:
        raise ShardRunError("artifact identity schema changed")
    actual = source_file_identity(path)
    if actual != dict(expected) or actual["mode"] != 0o444 or actual["nlink"] != 1:
        raise ShardRunError(f"artifact identity mismatch: {path}")


def _direct_fresh_root(path: str | Path) -> Path:
    root = Path(path)
    if not root.is_absolute():
        raise ShardRunError("output root must be an absolute path")
    if root.exists() or root.is_symlink():
        raise ShardRunError("output root must be fresh and absent")
    parent = root.parent.resolve(strict=True)
    if parent != root.parent or parent.is_symlink():
        raise ShardRunError("output parent must be direct and unaliased")
    root.mkdir(mode=0o700)
    if root.resolve(strict=True) != root or root.is_symlink():
        raise ShardRunError("created output root is aliased")
    return root


def _execution_mode(
    *,
    selector_injected: bool,
    solver_injected: bool,
    test_mode: bool,
) -> dict[str, object]:
    if not test_mode and (selector_injected or solver_injected):
        raise ShardRunError("dependency injection requires explicit test_mode=True")
    if test_mode:
        return {
            "contract_only": False,
            "kernel_unit_test_only": True,
            "science_executed": False,
            "scientific_evidence": False,
            "selector_injected": selector_injected,
            "solver_injected": solver_injected,
            "status": "TEST_ONLY_FAKE_INJECTION_NO_SCIENTIFIC_USE",
        }
    return {
        "contract_only": False,
        "kernel_unit_test_only": False,
        "science_executed": True,
        "scientific_evidence": True,
        "selector_injected": False,
        "solver_injected": False,
        "status": "PRODUCTION_SCIENCE_EXECUTION",
    }


def _build_run_contract(
    *,
    output_root: Path,
    resume_from: Path | None,
    frozen: FrozenProductionContract,
    shard: Mapping[str, object],
    keys: Sequence[RadialKey],
    source_identities: Mapping[str, Mapping[str, object]],
    execution_mode: Mapping[str, object],
) -> dict[str, object]:
    record: dict[str, object] = {
        "bound_inputs": {
            "coordinate_source": dict(frozen.coordinate_source_identity),
            "domain": {
                name: dict(value) for name, value in frozen.domain_identities.items()
            },
            "execution": {
                name: dict(value) for name, value in frozen.execution_identities.items()
            },
        },
        "context_sha256": "pending",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "domain": {
            "D_prod_key_count": 16_048,
            "D_prod_sha256": frozen.domain_identities["D_prod.jsonl"]["sha256"],
            "frequency_count": 40,
            "production_shard_count": 80,
        },
        "execution_mode": dict(execution_mode),
        "global_green_permitted": False,
        "implementation_source_identities": {
            name: dict(value) for name, value in source_identities.items()
        },
        "implementation_source_sha256s": source_hash_map(source_identities),
        "output_root": str(output_root),
        "paper_figure_agreement_gate": "PROHIBITED",
        "policy": DEFAULT_POLICY.to_record(),
        "policy_sha256": DEFAULT_POLICY.sha256,
        "production_coverage_rule": (
            "exact D_prod coverage strictly contains every historical Q018-labelled "
            "production mode without consulting a legacy classifier"
        ),
        "resume_from": None if resume_from is None else str(resume_from),
        "runtime": _runtime_identity(),
        "schema": RUN_CONTRACT_SCHEMA,
        "scope_qualification": {
            "detector_response": "NOT_ASSESSED",
            "finite_radius_observer_qualification": "NOT_ASSESSED",
            "full_paper_figure_rerun": False,
            "infinity_waveform": "NOT_ASSESSED",
            "radial_master_field_states": "ASSESSED_PER_MODE",
        },
        "shard": dict(shard),
        "shard_keys": [key.to_record() for key in keys],
        "table_i_sites": [site.to_record() for site in frozen.sites],
    }
    record["context_sha256"] = scientific_context_hash(record)
    return record


def _publish_key_payload(
    root: Path,
    *,
    ordinal: int,
    key: RadialKey,
    payload: Mapping[str, object],
) -> Mapping[str, object]:
    filename = key_artifact_filenames(ordinal, key)["payload"]
    return _publish_json_exclusive(root / filename, payload)


def _terminal_payload(
    *,
    ordinal: int,
    key: RadialKey,
    execution_status: str,
    acceptance_state: str,
    solver_call_count: int,
    payload_identity: Mapping[str, object] | None,
    predecessor_terminal_identity: Mapping[str, object] | None = None,
    reason: str | None = None,
) -> dict[str, object]:
    return {
        "acceptance_state": acceptance_state,
        "execution_status": execution_status,
        "global_green_permitted": False,
        "key": key.to_record(),
        "ordinal": ordinal,
        "payload_identity": (
            None if payload_identity is None else dict(payload_identity)
        ),
        "predecessor_terminal_identity": (
            None
            if predecessor_terminal_identity is None
            else dict(predecessor_terminal_identity)
        ),
        "provenance": {"legacy": False, "np": False, "pseudoinverse": False},
        "reason": reason,
        "schema": KEY_TERMINAL_SCHEMA,
        "solver_call_count": solver_call_count,
    }


def _publish_terminal(
    root: Path,
    *,
    ordinal: int,
    key: RadialKey,
    payload: Mapping[str, object],
) -> Mapping[str, object]:
    filename = key_artifact_filenames(ordinal, key)["terminal"]
    return _publish_json_exclusive(root / filename, payload)


def _validate_terminal(
    terminal: Mapping[str, object],
    *,
    ordinal: int,
    key: RadialKey,
) -> None:
    if set(terminal) != {
        "acceptance_state",
        "execution_status",
        "global_green_permitted",
        "key",
        "ordinal",
        "payload_identity",
        "predecessor_terminal_identity",
        "provenance",
        "reason",
        "schema",
        "solver_call_count",
    }:
        raise ShardRunError("terminal schema changed")
    if (
        terminal.get("schema") != KEY_TERMINAL_SCHEMA
        or terminal.get("key") != key.to_record()
        or terminal.get("ordinal") != ordinal
        or terminal.get("global_green_permitted") is not False
        or terminal.get("acceptance_state") not in {"PARTIAL", "FAIL"}
        or terminal.get("provenance")
        != {"legacy": False, "np": False, "pseudoinverse": False}
        or isinstance(terminal.get("solver_call_count"), bool)
        or terminal.get("solver_call_count") not in {0, 1}
    ):
        raise ShardRunError("terminal content changed")


def _predecessor_terminals(
    predecessor: Path,
    *,
    expected_contract: Mapping[str, object],
    keys: Sequence[RadialKey],
) -> dict[RadialKey, tuple[dict[str, object], Mapping[str, object]]]:
    if (
        predecessor.is_symlink()
        or not predecessor.is_dir()
        or predecessor.resolve(strict=True) != predecessor
        or stat.S_IMODE(predecessor.stat().st_mode) != 0o555
    ):
        raise ShardRunError("resume predecessor must be a direct immutable root")
    predecessor_contract = _strict_json(predecessor / "run_contract.json")
    if predecessor_contract.get("context_sha256") != expected_contract.get(
        "context_sha256"
    ):
        raise ShardRunError("resume predecessor scientific context differs")
    result: dict[RadialKey, tuple[dict[str, object], Mapping[str, object]]] = {}
    for ordinal, key in enumerate(keys):
        terminal_path = predecessor / key_artifact_filenames(ordinal, key)["terminal"]
        terminal = _strict_json(terminal_path)
        _validate_terminal(terminal, ordinal=ordinal, key=key)
        result[key] = (terminal, source_file_identity(terminal_path))
    if len(result) != len(keys):
        raise ShardRunError("predecessor terminal inventory changed")
    return result


def _resume_terminal(
    predecessor: Path,
    terminal: Mapping[str, object],
    terminal_identity: Mapping[str, object],
    *,
    ordinal: int,
    key: RadialKey,
    sites: Sequence[TableISite],
) -> dict[str, object] | None:
    status = terminal.get("execution_status")
    if status == "NOT_STARTED_DUE_TO_SHARD_FAILURE":
        return None
    payload_identity = terminal.get("payload_identity")
    reusable = False
    if status in {"COMPLETED", "REUSED_STRICT_PASS"} and isinstance(
        payload_identity, Mapping
    ):
        payload_path = Path(str(payload_identity.get("path", "")))
        try:
            _validate_identity(payload_path, payload_identity)
            payload = _strict_json(payload_path)
            validate_solver_payload(payload, key=key, sites=sites)
            reusable = (
                payload.get("acceptance_state") == "PASS"
                and payload["numerical_budget"]["status"] == "PASS"  # type: ignore[index]
                and payload["convention_budget"]["status"] == "PASS"  # type: ignore[index]
                and all(
                    value == "PASS"
                    for value in payload["observable_statuses"].values()  # type: ignore[union-attr]
                )
            )
        except Exception:
            reusable = False
    if reusable:
        return _terminal_payload(
            ordinal=ordinal,
            key=key,
            execution_status="REUSED_STRICT_PASS",
            acceptance_state="PARTIAL",
            solver_call_count=0,
            payload_identity=payload_identity,
            predecessor_terminal_identity=terminal_identity,
            reason="STRICT_PASS_PREDECESSOR_REUSED_WITHOUT_ACCEPTANCE_PROMOTION",
        )
    return _terminal_payload(
        ordinal=ordinal,
        key=key,
        execution_status="BLOCKED_NONREUSABLE_PREDECESSOR",
        acceptance_state="FAIL",
        solver_call_count=0,
        payload_identity=None,
        predecessor_terminal_identity=terminal_identity,
        reason="resume requires exact all-PASS predecessor evidence",
    )


def _status_worst(values: Sequence[str]) -> str:
    if not values:
        return "NOT_ASSESSED"
    if "FAIL" in values:
        return "FAIL"
    if "PARTIAL" in values:
        return "PARTIAL"
    if all(value == "PASS" for value in values):
        return "PASS"
    return "NOT_ASSESSED"


def _aggregate_shard(
    *,
    root: Path,
    run_contract: Mapping[str, object],
    keys: Sequence[RadialKey],
    terminals: Sequence[Mapping[str, object]],
    terminal_identities: Sequence[Mapping[str, object]],
    source_identities: Mapping[str, Mapping[str, object]],
    infrastructure_failure: str | None,
) -> dict[str, object]:
    if len(terminals) != len(keys) or len(terminal_identities) != len(keys):
        raise ShardRunError("cannot aggregate an incomplete terminal inventory")
    acceptance_values = [str(item["acceptance_state"]) for item in terminals]
    overall = (
        "FAIL" if "FAIL" in acceptance_values or infrastructure_failure else "PARTIAL"
    )
    execution_mode = run_contract["execution_mode"]
    if not isinstance(execution_mode, Mapping):
        raise ShardRunError("run execution mode is malformed")
    payloads: list[Mapping[str, object]] = []
    failures: list[dict[str, object]] = []
    for terminal in terminals:
        identity = terminal.get("payload_identity")
        if isinstance(identity, Mapping):
            payload = _strict_json(Path(str(identity["path"])))
            payloads.append(payload)
            if payload["acceptance_state"] == "FAIL":
                failures.append(
                    {
                        "failures": payload["failures"],
                        "key": payload["key"],
                        "payload_identity": dict(identity),
                    }
                )
        elif terminal["acceptance_state"] == "FAIL":
            failures.append({"key": terminal["key"], "reason": terminal.get("reason")})
    observables: dict[str, str] = {}
    observable_names = sorted(
        {
            name
            for payload in payloads
            for name in payload["observable_statuses"]  # type: ignore[union-attr]
        }
    )
    for name in observable_names:
        observables[name] = _status_worst(
            [
                str(payload["observable_statuses"].get(name, "NOT_ASSESSED"))  # type: ignore[union-attr]
                for payload in payloads
            ]
        )
    result = {
        "acceptance": overall,
        "all_terminal_identities": [dict(item) for item in terminal_identities],
        "contract_only": bool(execution_mode["contract_only"]),
        "convention_budget": {
            "components": {
                name: float(np.finfo(float).max)
                for name in (
                    "observer",
                    "tetrad",
                    "polarization_basis",
                    "phase_origin",
                    "total_scattered_definition",
                )
            },
            "status": "FAIL" if overall == "FAIL" else "PARTIAL",
        },
        "failures": failures,
        "global_green_permitted": False,
        "implementation_source_sha256s": source_hash_map(source_identities),
        "infrastructure_failure": infrastructure_failure,
        "kernel_unit_test_only": bool(execution_mode["kernel_unit_test_only"]),
        "numerical_budget": {
            "components": {
                name: (
                    float(np.finfo(float).eps)
                    if name == "arithmetic_precision"
                    else float(np.finfo(float).max)
                )
                for name in (
                    "lmax",
                    "r_in",
                    "r_out",
                    "jost_order",
                    "ode_tolerance",
                    "arithmetic_precision",
                    "axis_limit",
                    "backend_difference",
                )
            },
            "status": "FAIL" if overall == "FAIL" else "PARTIAL",
        },
        "observable_statuses": observables,
        "overall_state": overall,
        "root": str(root),
        "schema": SHARD_RESULT_SCHEMA,
        "science_executed": bool(execution_mode["science_executed"]),
        "scientific_evidence": bool(execution_mode["scientific_evidence"]),
        "shard": run_contract["shard"],
        "summary": {
            "blocked_nonreusable_predecessor_count": sum(
                item["execution_status"] == "BLOCKED_NONREUSABLE_PREDECESSOR"
                for item in terminals
            ),
            "key_count": len(keys),
            "mode_state_counts": {
                state: acceptance_values.count(state) for state in ("PARTIAL", "FAIL")
            },
            "payload_count": len(payloads),
            "solver_call_count_this_run": sum(
                int(item["solver_call_count"]) for item in terminals
            ),
            "terminal_count": len(terminals),
        },
    }
    if (
        any(item["acceptance_state"] == "FAIL" for item in terminals)
        and overall != "FAIL"
    ):
        raise ShardRunError("mode failure was hidden by shard aggregation")
    return result


def _seal_root(root: Path) -> None:
    for path in root.iterdir():
        if path.is_symlink() or not path.is_file():
            raise ShardRunError(f"non-regular artifact in output root: {path}")
        os.chmod(path, 0o444)
    os.chmod(root, 0o555)
    _fsync_directory(root.parent)


def _publish_manifest(root: Path, *, status: str) -> Mapping[str, object]:
    files = {
        path.name: source_file_identity(path)
        for path in sorted(root.iterdir())
        if path.is_file() and path.name != "manifest.json"
    }
    return _publish_json_exclusive(
        root / "manifest.json",
        {
            "file_count_excluding_manifest": len(files),
            "files": files,
            "global_green_permitted": False,
            "schema": MANIFEST_SCHEMA,
            "status": status,
        },
    )


def _validate_completed_root(
    root: Path,
    *,
    frozen: FrozenProductionContract,
    keys: Sequence[RadialKey],
) -> dict[str, object]:
    if (
        root.is_symlink()
        or root.resolve(strict=True) != root
        or stat.S_IMODE(root.stat().st_mode) != 0o555
    ):
        raise ShardRunError("terminal output root is not direct immutable")
    manifest = _strict_json(root / "manifest.json")
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ShardRunError("manifest schema changed")
    files = manifest.get("files")
    actual_names = {path.name for path in root.iterdir() if path.is_file()}
    if (
        not isinstance(files, Mapping)
        or set(files) | {"manifest.json"} != actual_names
        or manifest.get("file_count_excluding_manifest") != len(files)
    ):
        raise ShardRunError("manifest file inventory changed")
    for name, identity in files.items():
        if not isinstance(name, str) or not isinstance(identity, Mapping):
            raise ShardRunError("manifest identity schema changed")
        _validate_identity(root / name, identity)
    run_contract = _strict_json(root / "run_contract.json")
    shard_result = _strict_json(root / "shard_result.json")
    if run_contract.get("schema") != RUN_CONTRACT_SCHEMA:
        raise ShardRunError("run contract schema changed")
    if run_contract.get("context_sha256") != scientific_context_hash(run_contract):
        raise ShardRunError("run context hash changed")
    terminal_identities: list[Mapping[str, object]] = []
    terminals: list[Mapping[str, object]] = []
    expected_failures: list[dict[str, object]] = []
    for ordinal, key in enumerate(keys):
        terminal_path = root / key_artifact_filenames(ordinal, key)["terminal"]
        terminal = _strict_json(terminal_path)
        _validate_terminal(terminal, ordinal=ordinal, key=key)
        terminals.append(terminal)
        terminal_identities.append(source_file_identity(terminal_path))
        payload_identity = terminal.get("payload_identity")
        if isinstance(payload_identity, Mapping):
            payload_path = Path(str(payload_identity["path"]))
            _validate_identity(payload_path, payload_identity)
            payload = _strict_json(payload_path)
            validate_solver_payload(payload, key=key, sites=frozen.sites)
            if payload["acceptance_state"] == "FAIL":
                expected_failures.append(
                    {
                        "failures": payload["failures"],
                        "key": payload["key"],
                        "payload_identity": dict(payload_identity),
                    }
                )
        elif terminal["acceptance_state"] == "FAIL":
            expected_failures.append(
                {"key": terminal["key"], "reason": terminal.get("reason")}
            )
    if shard_result.get("schema") != SHARD_RESULT_SCHEMA:
        raise ShardRunError("shard result schema changed")
    if shard_result.get("all_terminal_identities") != [
        dict(item) for item in terminal_identities
    ]:
        raise ShardRunError("shard result terminal identities changed")
    if shard_result.get("failures") != expected_failures:
        raise ShardRunError("shard result failure ledger changed")
    expected_overall = (
        "FAIL"
        if any(item["acceptance_state"] == "FAIL" for item in terminals)
        or shard_result.get("infrastructure_failure") is not None
        else "PARTIAL"
    )
    if (
        shard_result.get("overall_state") != expected_overall
        or shard_result.get("acceptance") != expected_overall
        or shard_result.get("global_green_permitted") is not False
    ):
        raise ShardRunError("shard result acceptance aggregation changed")
    return shard_result


def _finalize_failure(
    root: Path,
    *,
    run_contract: Mapping[str, object],
    keys: Sequence[RadialKey],
    terminals: list[Mapping[str, object]],
    terminal_identities: list[Mapping[str, object]],
    source_identities: Mapping[str, Mapping[str, object]],
    failure: BaseException,
    next_ordinal: int,
) -> None:
    for ordinal in range(next_ordinal, len(keys)):
        key = keys[ordinal]
        terminal = _terminal_payload(
            ordinal=ordinal,
            key=key,
            execution_status="NOT_STARTED_DUE_TO_SHARD_FAILURE",
            acceptance_state="FAIL",
            solver_call_count=0,
            payload_identity=None,
            reason="preceding shard infrastructure failure",
        )
        identity = _publish_terminal(root, ordinal=ordinal, key=key, payload=terminal)
        terminals.append(terminal)
        terminal_identities.append(identity)
    failure_text = (
        f"{type(failure).__name__}: {str(failure) or '<empty exception message>'}"
    )
    _publish_json_exclusive(
        root / "failure.json",
        {
            "error": failure_text,
            "global_green_permitted": False,
            "schema": SHARD_FAILURE_SCHEMA,
            "status": "FAIL",
        },
    )
    shard_result = _aggregate_shard(
        root=root,
        run_contract=run_contract,
        keys=keys,
        terminals=terminals,
        terminal_identities=terminal_identities,
        source_identities=source_identities,
        infrastructure_failure=failure_text,
    )
    shard_result["scientific_evidence"] = False
    _publish_json_exclusive(root / "shard_result.json", shard_result)
    _publish_manifest(root, status="FAILED_CLOSED")
    _seal_root(root)


def run_shard(
    output_root: str | Path,
    *,
    shard_id: str,
    resume_from: str | Path | None = None,
    selector: Callable[[RadialKey], OuterSelection] = select_outer_boundary,
    solver: Callable[..., ConditionedRadialResult] = solve_conditioned_radial_at_radius,
    test_mode: bool = False,
) -> dict[str, object]:
    """Execute one production shard; no all-shards orchestration is provided."""

    selector_injected = selector is not select_outer_boundary
    solver_injected = solver is not solve_conditioned_radial_at_radius
    execution_mode = _execution_mode(
        selector_injected=selector_injected,
        solver_injected=solver_injected,
        test_mode=test_mode,
    )
    frozen = load_frozen_production_contract(DOMAIN_ROOT, EXECUTION_ROOT)
    shard = frozen.shard_record(shard_id)
    keys = frozen.shard_keys(shard_id)
    predecessor = None
    if resume_from is not None:
        predecessor = Path(resume_from).resolve(strict=True)
    root = _direct_fresh_root(output_root)
    source_identities = _implementation_identities()
    run_contract = _build_run_contract(
        output_root=root,
        resume_from=predecessor,
        frozen=frozen,
        shard=shard,
        keys=keys,
        source_identities=source_identities,
        execution_mode=execution_mode,
    )
    _publish_json_exclusive(root / "run_contract.json", run_contract)
    terminals: list[Mapping[str, object]] = []
    terminal_identities: list[Mapping[str, object]] = []
    next_ordinal = 0
    try:
        predecessor_terminals = (
            {}
            if predecessor is None
            else _predecessor_terminals(
                predecessor,
                expected_contract=run_contract,
                keys=keys,
            )
        )
        for ordinal, key in enumerate(keys):
            next_ordinal = ordinal
            if key in predecessor_terminals:
                prior_terminal, prior_identity = predecessor_terminals[key]
                resume_terminal = _resume_terminal(
                    predecessor,
                    prior_terminal,
                    prior_identity,
                    ordinal=ordinal,
                    key=key,
                    sites=frozen.sites,
                )
                if resume_terminal is not None:
                    identity = _publish_terminal(
                        root,
                        ordinal=ordinal,
                        key=key,
                        payload=resume_terminal,
                    )
                    terminals.append(resume_terminal)
                    terminal_identities.append(identity)
                    next_ordinal = ordinal + 1
                    continue
            selection = selector(key)
            payload = execute_production_finite_radius_key(
                key,
                selection,
                frozen.sites,
                solver=solver,
            )
            payload_identity: Mapping[str, object] | None = None
            try:
                payload_identity = _publish_key_payload(
                    root,
                    ordinal=ordinal,
                    key=key,
                    payload=payload,
                )
            except Exception as exc:
                terminal = _terminal_payload(
                    ordinal=ordinal,
                    key=key,
                    execution_status="EXECUTION_FAILED_AFTER_SOLVER_CALL",
                    acceptance_state="FAIL",
                    solver_call_count=int(payload["solver_call_count"]),
                    payload_identity=None,
                    reason=f"{type(exc).__name__}: {str(exc)}",
                )
                identity = _publish_terminal(
                    root, ordinal=ordinal, key=key, payload=terminal
                )
                terminals.append(terminal)
                terminal_identities.append(identity)
                next_ordinal = ordinal + 1
                raise
            terminal = _terminal_payload(
                ordinal=ordinal,
                key=key,
                execution_status="COMPLETED",
                acceptance_state=str(payload["acceptance_state"]),
                solver_call_count=int(payload["solver_call_count"]),
                payload_identity=payload_identity,
            )
            identity = _publish_terminal(
                root, ordinal=ordinal, key=key, payload=terminal
            )
            terminals.append(terminal)
            terminal_identities.append(identity)
            next_ordinal = ordinal + 1
        after_identities = _implementation_identities()
        if after_identities != source_identities:
            raise ShardRunError("implementation source changed during shard execution")
        frozen_after = load_frozen_production_contract(DOMAIN_ROOT, EXECUTION_ROOT)
        if (
            frozen_after.domain_identities != frozen.domain_identities
            or frozen_after.execution_identities != frozen.execution_identities
            or frozen_after.coordinate_source_identity
            != frozen.coordinate_source_identity
        ):
            raise ShardRunError("frozen input changed during shard execution")
        shard_result = _aggregate_shard(
            root=root,
            run_contract=run_contract,
            keys=keys,
            terminals=terminals,
            terminal_identities=terminal_identities,
            source_identities=source_identities,
            infrastructure_failure=None,
        )
        _publish_json_exclusive(root / "shard_result.json", shard_result)
        _publish_manifest(root, status="COMPLETE")
        _seal_root(root)
        return _validate_completed_root(root, frozen=frozen, keys=keys)
    except Exception as exc:
        if stat.S_IMODE(root.stat().st_mode) != 0o555:
            try:
                _finalize_failure(
                    root,
                    run_contract=run_contract,
                    keys=keys,
                    terminals=terminals,
                    terminal_identities=terminal_identities,
                    source_identities=source_identities,
                    failure=exc,
                    next_ordinal=next_ordinal,
                )
            except Exception as sealing_exc:
                raise ShardRunError(
                    "production finite-radius shard failed and could not seal all terminals"
                ) from sealing_exc
        raise ShardRunError("production finite-radius shard failed closed") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--shard-id", required=True)
    parser.add_argument("--resume-from", type=Path)
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    result = run_shard(
        arguments.output_root,
        shard_id=arguments.shard_id,
        resume_from=arguments.resume_from,
    )
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
