"""Frozen Phase-6 external BHPT direct-integration calibration contract.

This module validates a deliberately small, source-bound external calculation.
It never calls a SchWO radial solver and it never promotes the 30 calibration
keys to whole-domain acceptance.  The Wolfram producer solves both the ``In``
and ``Up`` problems with BHPT ``Method -> "NumericalIntegration"`` and obtains
the asymptotic coefficients by a Wronskian decomposition in their overlap.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, localcontext
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess

from schwgw.validation.phase6_execution_contract import (
    EXTERNAL_DIRECT_CALIBRATION_SCHEMA,
    calibration_jsonl_bytes,
    external_direct_calibration_keys,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
WLS_PATH = PROJECT_ROOT / "scripts" / "phase6_bhpt_direct_selected.wls"
RUNNER_PATH = PROJECT_ROOT / "scripts" / "phase6_run_bhpt_direct_selected.py"
EXECUTION_CONTRACT_ROOT = (
    PROJECT_ROOT / "runs" / "phase6" / "v1_execution_contract_v4_20260806"
)

REQUEST_SCHEMA = "schwgw_phase6_bhpt_direct_selected_request_v1"
RAW_SCHEMA = "schwgw_phase6_bhpt_direct_selected_raw_v1"
EVIDENCE_SCHEMA = "schwgw_phase6_bhpt_direct_selected_evidence_v1"
EXPECTED_UPSTREAM_COMMIT = "2e01209271fb3d0d92705d5c27bd9e00a6140981"
EXPECTED_SOURCE_SHA256 = {
    "Kernel/ReggeWheelerRadial.m": (
        "2af593f527b39d2b7ece71f99e50ecb6b84399342251985004d6d2e2c3fed41f"
    ),
    "Kernel/NumericalIntegration.m": (
        "6619df2ceaa83d373152ff20740a884c8a8bd401e50c0c91a20c1d21cc879ae0"
    ),
    "LICENSE": "b8baa31999241b81142016a24cdf8ea98f21d628d995592ba52def4ac9bca24b",
}
EXPECTED_EXECUTION_IDENTITIES = {
    "execution_contract.json": (
        "25ad4b4e723edbd44651edaa63df415141de504b85288b12c2a6a973fcb420ab"
    ),
    "manifest.json": (
        "1de9d445d888cbb5ddbf426cc062d2fb5128cad111437ce7d147df6e004aed48"
    ),
    "D_external_direct_calibration.jsonl": (
        "d572c88259ef4b42b490af263d012a8de880458902dcf5a4d303c9f587cd466b"
    ),
}
EXPECTED_KEY_LIST_SHA256 = EXPECTED_EXECUTION_IDENTITIES[
    "D_external_direct_calibration.jsonl"
]
CALIBRATION_PURPOSE = "EXTERNAL_SOURCE_CALIBRATION_ONLY_NOT_DOMAIN_ACCEPTANCE"
METHOD_NAME = "NumericalIntegration"
POTENTIAL_BY_SECTOR = {"odd": "ReggeWheeler", "even": "Zerilli"}
BOUNDARY_CONDITIONS = ("In", "Up")
MATCH_FRACTIONS = ("0.8", "0.88", "0.96")
SELECTED_MATCH_INDEX = 1
WORKING_PRECISION = 800
PRECISION_GOAL = 200
ACCURACY_GOAL = 200
OUTPUT_DIGITS = 100
FORMAL_ROOT_MODE = 0o555
FORMAL_FILE_MODE = 0o444
_DECIMAL_PATTERN = re.compile(
    r"^[+-]?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?$"
)


class BHPTDirectContractError(ValueError):
    """Raised when source, domain, or direct-output evidence drifts."""


@dataclass(frozen=True)
class _DecimalComplex:
    real: Decimal
    imag: Decimal

    def __add__(self, other: _DecimalComplex) -> _DecimalComplex:
        return _DecimalComplex(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other: _DecimalComplex) -> _DecimalComplex:
        return _DecimalComplex(self.real - other.real, self.imag - other.imag)

    def __mul__(self, other: _DecimalComplex) -> _DecimalComplex:
        return _DecimalComplex(
            self.real * other.real - self.imag * other.imag,
            self.real * other.imag + self.imag * other.real,
        )

    def __truediv__(self, other: _DecimalComplex) -> _DecimalComplex:
        denominator = other.abs_squared()
        if denominator == 0:
            raise BHPTDirectContractError("complex division by zero")
        return _DecimalComplex(
            (self.real * other.real + self.imag * other.imag) / denominator,
            (self.imag * other.real - self.real * other.imag) / denominator,
        )

    def scale(self, value: int | Decimal) -> _DecimalComplex:
        factor = Decimal(value)
        return _DecimalComplex(self.real * factor, self.imag * factor)

    def abs_squared(self) -> Decimal:
        return self.real * self.real + self.imag * self.imag

    def absolute(self) -> Decimal:
        return self.abs_squared().sqrt()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    """Return the streaming SHA-256 of a regular file."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _regular_file_identity(path: Path) -> dict[str, object]:
    original = path.absolute()
    try:
        status = original.lstat()
    except OSError as exc:
        raise BHPTDirectContractError(
            f"cannot inspect required file: {original}"
        ) from exc
    if original.is_symlink() or not original.is_file() or status.st_nlink != 1:
        raise BHPTDirectContractError(
            f"required source must be a regular nlink-1 non-symlink: {original}"
        )
    return {
        "path": str(original),
        "sha256": sha256_file(original),
        "size": status.st_size,
        "mode": status.st_mode & 0o777,
        "nlink": status.st_nlink,
    }


def _git_head(package_root: Path) -> tuple[str, Path]:
    try:
        head = subprocess.run(
            ["git", "-C", str(package_root), "rev-parse", "HEAD"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30.0,
        )
        top = subprocess.run(
            ["git", "-C", str(package_root), "rev-parse", "--show-toplevel"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30.0,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BHPTDirectContractError("cannot query BHPT git provenance") from exc
    if head.returncode != 0 or top.returncode != 0:
        raise BHPTDirectContractError(
            "BHPT package root must be an exact git checkout, not an unattested copy"
        )
    return head.stdout.strip(), Path(top.stdout.strip()).resolve(strict=True)


def _require_clean_git_worktree(package_root: Path) -> None:
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(package_root),
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30.0,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BHPTDirectContractError("cannot audit BHPT git worktree") from exc
    if result.returncode != 0:
        raise BHPTDirectContractError("cannot audit BHPT git worktree")
    if result.stdout:
        raise BHPTDirectContractError(
            "BHPT package root must be a clean exact checkout with no untracked files"
        )


def validate_source_snapshot(package_root: str | Path) -> dict[str, object]:
    """Validate the exact frozen BHPT commit and the three required file hashes."""

    original = Path(package_root).absolute()
    try:
        root_status = original.lstat()
        resolved = original.resolve(strict=True)
    except OSError as exc:
        raise BHPTDirectContractError("BHPT package root is unavailable") from exc
    if original.is_symlink() or not resolved.is_dir() or root_status.st_nlink < 1:
        raise BHPTDirectContractError(
            "BHPT package root must be a non-symlink directory"
        )
    commit, git_root = _git_head(resolved)
    if git_root != resolved:
        raise BHPTDirectContractError("BHPT package root must equal the git toplevel")
    if commit != EXPECTED_UPSTREAM_COMMIT:
        raise BHPTDirectContractError(
            f"BHPT commit mismatch: expected {EXPECTED_UPSTREAM_COMMIT}, got {commit}"
        )
    _require_clean_git_worktree(resolved)
    identities: dict[str, dict[str, object]] = {}
    for relative, expected in EXPECTED_SOURCE_SHA256.items():
        identity = _regular_file_identity(resolved / relative)
        if identity["sha256"] != expected:
            raise BHPTDirectContractError(
                f"BHPT source hash mismatch for {relative}: {identity['sha256']}"
            )
        identities[relative] = identity
    return {
        "package_root": str(resolved),
        "repository": "https://github.com/BlackHolePerturbationToolkit/ReggeWheeler",
        "commit": commit,
        "git_worktree_status": "CLEAN_TRACKED_AND_UNTRACKED",
        "license": "MIT",
        "files": identities,
    }


def validate_execution_contract(
    project_root: str | Path = PROJECT_ROOT,
) -> dict[str, object]:
    """Bind the direct runner to v4 and its exact 30-key JSONL bytes."""

    root = (
        Path(project_root).resolve(strict=True)
        / "runs"
        / "phase6"
        / "v1_execution_contract_v4_20260806"
    )
    identities: dict[str, dict[str, object]] = {}
    for name, expected in EXPECTED_EXECUTION_IDENTITIES.items():
        identity = _regular_file_identity(root / name)
        if identity["sha256"] != expected:
            raise BHPTDirectContractError(
                f"frozen execution artifact hash mismatch for {name}"
            )
        identities[name] = identity
    keys = external_direct_calibration_keys()
    expected_bytes = calibration_jsonl_bytes(keys)
    key_path = root / "D_external_direct_calibration.jsonl"
    if key_path.read_bytes() != expected_bytes:
        raise BHPTDirectContractError("frozen external-direct JSONL bytes changed")
    if len(keys) != 30 or _sha256_bytes(expected_bytes) != EXPECTED_KEY_LIST_SHA256:
        raise BHPTDirectContractError("external-direct 30-key derivation changed")
    return {
        "root": str(root),
        "schema": EXTERNAL_DIRECT_CALIBRATION_SCHEMA,
        "purpose": CALIBRATION_PURPOSE,
        "count": len(keys),
        "key_list_sha256": EXPECTED_KEY_LIST_SHA256,
        "files": identities,
        "records": [key.to_record() for key in keys],
    }


def build_request(
    *,
    source_snapshot: Mapping[str, object],
    execution_contract: Mapping[str, object],
    wls_path: str | Path = WLS_PATH,
) -> dict[str, object]:
    """Build the immutable scientific request consumed by the Wolfram producer."""

    wls_identity = _regular_file_identity(Path(wls_path))
    return {
        "schema_version": REQUEST_SCHEMA,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "acceptance_scope": CALIBRATION_PURPOSE,
        "global_green_permitted": False,
        "paper_figure_agreement_gate": "PROHIBITED",
        "execution_contract_v4": dict(execution_contract),
        "external_direct_domain": {
            "schema": EXTERNAL_DIRECT_CALIBRATION_SCHEMA,
            "purpose": CALIBRATION_PURPOSE,
            "count": 30,
            "key_list_sha256": EXPECTED_KEY_LIST_SHA256,
            "records": list(execution_contract["records"]),  # type: ignore[index]
        },
        "toolkit_source": dict(source_snapshot),
        "producer_source": wls_identity,
        "orchestrator_sources": {
            "validation_module": _regular_file_identity(Path(__file__)),
            "runner": _regular_file_identity(RUNNER_PATH),
        },
        "backend_contract": {
            "method": METHOD_NAME,
            "wolfram_option_expression": (
                'Method -> {"NumericalIntegration", "Domain" -> '
                '{"In" -> max_match_radius, "Up" -> min_match_radius}}'
            ),
            "spin_weight_argument": 2,
            "potential_by_sector": dict(POTENTIAL_BY_SECTOR),
            "boundary_conditions_solved": list(BOUNDARY_CONDITIONS),
            "external_api_calls_per_key": 1,
            "external_api_call_count": 30,
            "external_boundary_solutions_per_key": 2,
            "external_boundary_solution_count": 60,
            "even_is_independent_radial_solution": True,
            "parity_derived_even_used": False,
            "internal_solver_fallback_permitted": False,
            "project_solver_components_used": [],
        },
        "precision": {
            "working_precision_decimal_digits": WORKING_PRECISION,
            "precision_goal_decimal_digits": PRECISION_GOAL,
            "accuracy_goal_decimal_digits": ACCURACY_GOAL,
            "serialized_output_digits": OUTPUT_DIGITS,
        },
        "matching": {
            "method": "two-solution Wronskian decomposition",
            "upstream_outer_boundary_radius_formula_M": "100/abs(kM)",
            "match_radius_fractions_of_upstream_outer_boundary": list(MATCH_FRACTIONS),
            "selected_match_index": SELECTED_MATCH_INDEX,
            "phase_factor_definition": "-Reflection/((-1)^ell*Incidence)",
            "transmission_definition": "1/Incidence",
            "reflection_ratio_definition": "Reflection/Incidence",
        },
        "uncertainty_contract": {
            "numerical": {
                "required_per_record": [
                    "matching_radius_phase_spread_abs",
                    "selected_flux_unitarity_residual_abs",
                    "working_precision_decimal_digits",
                    "unquantified_sources",
                ],
                "acceptance_threshold_frozen": False,
            },
            "convention": {
                "required_per_record": [
                    "Fourier_convention",
                    "tortoise_definition",
                    "phase_factor_definition",
                    "absolute_phase_origin",
                    "phase_or_normalization_fit",
                ],
                "acceptance_threshold_frozen": False,
            },
        },
    }


def canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _exclusive_bytes(path: Path, data: bytes) -> dict[str, object]:
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
    os.chmod(path, FORMAL_FILE_MODE)
    _fsync_directory(path.parent)
    return _formal_file_identity(path)


def atomic_json(
    path: Path,
    payload: Mapping[str, object],
) -> dict[str, object]:
    """Publish canonical JSON once; existing or aliased targets fail closed."""

    return _exclusive_bytes(path, canonical_json_bytes(payload))


def _formal_file_identity(path: Path) -> dict[str, object]:
    original = path.absolute()
    try:
        status = original.lstat()
    except OSError as exc:
        raise BHPTDirectContractError(
            f"cannot inspect formal evidence file: {original}"
        ) from exc
    mode = stat.S_IMODE(status.st_mode)
    if (
        original.is_symlink()
        or not original.is_file()
        or status.st_nlink != 1
        or mode != FORMAL_FILE_MODE
    ):
        raise BHPTDirectContractError(
            "formal evidence must be an immutable regular nlink-1 file"
        )
    return {
        "path": str(original),
        "sha256": sha256_file(original),
        "size": status.st_size,
        "mode": mode,
        "nlink": status.st_nlink,
    }


def _seal_root(root: Path) -> None:
    if root.is_symlink() or root.resolve(strict=True) != root:
        raise BHPTDirectContractError("formal evidence root cannot be aliased")
    for child in root.iterdir():
        status = child.lstat()
        if child.is_symlink() or not child.is_file() or status.st_nlink != 1:
            raise BHPTDirectContractError(
                "formal evidence root contains a non-regular artifact"
            )
        os.chmod(child, FORMAL_FILE_MODE)
    os.chmod(root, FORMAL_ROOT_MODE)
    _fsync_directory(root)
    _fsync_directory(root.parent)


def _publish_manifest(root: Path, *, returncode: int) -> dict[str, object]:
    evidence = json.loads((root / "evidence.json").read_text(encoding="utf-8"))
    if not isinstance(evidence, Mapping):
        raise BHPTDirectContractError("terminal evidence must be a JSON object")
    for child in root.iterdir():
        status = child.lstat()
        if child.is_symlink() or not child.is_file() or status.st_nlink != 1:
            raise BHPTDirectContractError(
                "formal evidence root contains a non-regular artifact"
            )
        os.chmod(child, FORMAL_FILE_MODE)
    identities = {
        child.name: _formal_file_identity(child)
        for child in sorted(root.iterdir(), key=lambda item: item.name)
        if child.name != "manifest.json"
    }
    manifest = {
        "schema_version": "schwgw_phase6_bhpt_direct_selected_manifest_v1",
        "formal_evidence_root": True,
        "returncode": returncode,
        "terminal_status": evidence.get("status"),
        "terminal_blocker": evidence.get("blocker"),
        "external_record_count": evidence.get(
            "external_record_count", evidence.get("record_count", 0)
        ),
        "science_executed": evidence.get("science_executed"),
        "global_green_permitted": False,
        "paper_figure_runs": 0,
        "files": identities,
    }
    manifest_identity = atomic_json(root / "manifest.json", manifest)
    _seal_root(root)
    _validate_frozen_root(root)
    return manifest_identity


def _validate_frozen_root(root: Path) -> None:
    if (
        root.is_symlink()
        or root.resolve(strict=True) != root
        or stat.S_IMODE(root.lstat().st_mode) != FORMAL_ROOT_MODE
    ):
        raise BHPTDirectContractError("formal evidence root is not immutable 0555")
    manifest_path = root / "manifest.json"
    manifest_identity = _formal_file_identity(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        not isinstance(manifest, Mapping)
        or manifest.get("schema_version")
        != "schwgw_phase6_bhpt_direct_selected_manifest_v1"
        or manifest.get("formal_evidence_root") is not True
        or manifest.get("global_green_permitted") is not False
        or manifest.get("paper_figure_runs") != 0
    ):
        raise BHPTDirectContractError("formal direct manifest claims changed")
    identities = manifest.get("files")
    if not isinstance(identities, Mapping):
        raise BHPTDirectContractError("formal direct manifest file inventory missing")
    actual_names = {child.name for child in root.iterdir()}
    if actual_names != {*identities, "manifest.json"}:
        raise BHPTDirectContractError("formal direct root file inventory changed")
    for name, expected in identities.items():
        if not isinstance(name, str) or not isinstance(expected, Mapping):
            raise BHPTDirectContractError("formal direct file identity is malformed")
        if _formal_file_identity(root / name) != dict(expected):
            raise BHPTDirectContractError(
                f"formal direct file identity changed: {name}"
            )
    if manifest_identity["mode"] != FORMAL_FILE_MODE:
        raise BHPTDirectContractError("formal direct manifest is mutable")


def _finish(root: Path, *, returncode: int) -> int:
    _publish_manifest(root, returncode=returncode)
    return returncode


def _decimal(value: object, *, label: str) -> Decimal:
    if not isinstance(value, str) or not _DECIMAL_PATTERN.fullmatch(value):
        raise BHPTDirectContractError(f"{label} must be a canonical decimal string")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise BHPTDirectContractError(f"{label} is not decimal") from exc
    if not result.is_finite():
        raise BHPTDirectContractError(f"{label} must be finite")
    return result


def _complex(value: object, *, label: str) -> _DecimalComplex:
    if not isinstance(value, Mapping) or set(value) != {"real", "imag"}:
        raise BHPTDirectContractError(f"{label} must contain exactly real and imag")
    return _DecimalComplex(
        _decimal(value["real"], label=f"{label}.real"),
        _decimal(value["imag"], label=f"{label}.imag"),
    )


def _close_decimal(
    actual: Decimal,
    expected: Decimal,
    *,
    label: str,
    relative_tolerance: Decimal = Decimal("1e-80"),
) -> None:
    scale = max(Decimal(1), abs(actual), abs(expected))
    if abs(actual - expected) > relative_tolerance * scale:
        raise BHPTDirectContractError(f"{label} is algebraically inconsistent")


def _close_complex(
    actual: _DecimalComplex,
    expected: _DecimalComplex,
    *,
    label: str,
) -> None:
    _close_decimal(actual.real, expected.real, label=f"{label}.real")
    _close_decimal(actual.imag, expected.imag, label=f"{label}.imag")


def _validate_budget(
    record: Mapping[str, object],
    *,
    phase_spread: Decimal,
    selected_flux_residual: Decimal,
) -> None:
    numerical = record.get("numerical_uncertainty_budget")
    if not isinstance(numerical, Mapping):
        raise BHPTDirectContractError("per-record numerical uncertainty budget missing")
    required_numerical = {
        "status",
        "matching_radius_phase_spread_abs",
        "selected_flux_unitarity_residual_abs",
        "working_precision_decimal_digits",
        "precision_goal_decimal_digits",
        "accuracy_goal_decimal_digits",
        "unquantified_sources",
    }
    if set(numerical) != required_numerical:
        raise BHPTDirectContractError("per-record numerical budget fields changed")
    if numerical["status"] != "PARTIAL_MEASURED_NOT_ACCEPTANCE":
        raise BHPTDirectContractError("numerical budget overclaims acceptance")
    if (
        numerical["working_precision_decimal_digits"] != WORKING_PRECISION
        or numerical["precision_goal_decimal_digits"] != PRECISION_GOAL
        or numerical["accuracy_goal_decimal_digits"] != ACCURACY_GOAL
    ):
        raise BHPTDirectContractError("precision metadata changed")
    sources = numerical["unquantified_sources"]
    if not isinstance(sources, list) or not sources:
        raise BHPTDirectContractError(
            "unquantified numerical sources must remain explicit"
        )
    recorded_spread = _decimal(
        numerical["matching_radius_phase_spread_abs"],
        label="matching_radius_phase_spread_abs",
    )
    _close_decimal(recorded_spread, phase_spread, label="matching-radius spread")
    selected_flux = _decimal(
        numerical["selected_flux_unitarity_residual_abs"],
        label="selected_flux_unitarity_residual_abs",
    )
    if selected_flux < 0:
        raise BHPTDirectContractError("flux residual cannot be negative")
    _close_decimal(
        selected_flux,
        selected_flux_residual,
        label="selected flux budget",
    )

    convention = record.get("convention_uncertainty_budget")
    required_convention = {
        "status",
        "Fourier_convention",
        "tortoise_definition",
        "phase_factor_definition",
        "absolute_phase_origin",
        "phase_or_normalization_fit",
        "remaining_convention_uncertainty",
    }
    if not isinstance(convention, Mapping) or set(convention) != required_convention:
        raise BHPTDirectContractError("per-record convention budget fields changed")
    if convention != {
        "status": "FROZEN_FOR_EXTERNAL_CALIBRATION_NOT_GLOBAL",
        "Fourier_convention": "exp(-i*k*t)",
        "tortoise_definition": "r_star=r+2*log(r/2-1), M=1",
        "phase_factor_definition": "-Reflection/((-1)^ell*Incidence)",
        "absolute_phase_origin": "BHPT tortoise coordinate with no additive constant",
        "phase_or_normalization_fit": False,
        "remaining_convention_uncertainty": (
            "comparison consumers must prove the same master-function and phase convention"
        ),
    }:
        raise BHPTDirectContractError("convention budget drifted")


def _validate_record(record: object, expected_key: Mapping[str, object]) -> None:
    if not isinstance(record, Mapping):
        raise BHPTDirectContractError("direct result record must be an object")
    expected_fields = {
        "kM",
        "sector",
        "ell",
        "potential",
        "method",
        "boundary_conditions_solved",
        "external_api_call_count",
        "external_boundary_solution_count",
        "sector_is_independent_external_radial_solution",
        "parity_derived_even_used",
        "derived_from_sector",
        "match_records",
        "selected_match_index",
        "incidence",
        "reflection",
        "transmission",
        "reflection_ratio",
        "phase_factor",
        "numerical_uncertainty_budget",
        "convention_uncertainty_budget",
    }
    if set(record) != expected_fields:
        raise BHPTDirectContractError("direct result record fields changed")
    for name in ("kM", "sector", "ell"):
        if record[name] != expected_key[name]:
            raise BHPTDirectContractError("direct result key order or identity changed")
    sector = str(record["sector"])
    if record["potential"] != POTENTIAL_BY_SECTOR[sector]:
        raise BHPTDirectContractError(
            "sector did not use its independent radial potential"
        )
    if (
        record["method"] != METHOD_NAME
        or record["boundary_conditions_solved"] != list(BOUNDARY_CONDITIONS)
        or record["external_api_call_count"] != 1
        or record["external_boundary_solution_count"] != 2
        or record["sector_is_independent_external_radial_solution"] is not True
        or record["parity_derived_even_used"] is not False
        or record["derived_from_sector"] is not None
        or record["selected_match_index"] != SELECTED_MATCH_INDEX
    ):
        raise BHPTDirectContractError("external direct-solve provenance changed")

    matches = record["match_records"]
    if not isinstance(matches, list) or len(matches) != len(MATCH_FRACTIONS):
        raise BHPTDirectContractError("matching-radius ladder changed")
    phases: list[_DecimalComplex] = []
    for index, match in enumerate(matches):
        if not isinstance(match, Mapping):
            raise BHPTDirectContractError("match record must be an object")
        expected_match_fields = {
            "match_fraction_of_upstream_outer_boundary",
            "match_radius_M",
            "basis_wronskian_abs",
            "incidence",
            "reflection",
            "transmission",
            "reflection_ratio",
            "phase_factor",
            "flux_unitarity_residual_abs",
        }
        if set(match) != expected_match_fields:
            raise BHPTDirectContractError("match record fields changed")
        if match["match_fraction_of_upstream_outer_boundary"] != MATCH_FRACTIONS[index]:
            raise BHPTDirectContractError("matching-radius fraction changed")
        radius = _decimal(match["match_radius_M"], label="match_radius_M")
        wronskian = _decimal(match["basis_wronskian_abs"], label="basis_wronskian_abs")
        if radius <= 2 or wronskian <= 0:
            raise BHPTDirectContractError(
                "matching radius or basis Wronskian is invalid"
            )
        expected_radius = (
            Decimal(100)
            * Decimal(MATCH_FRACTIONS[index])
            / Decimal(str(expected_key["kM"]))
        )
        _close_decimal(radius, expected_radius, label="matching radius")
        incidence = _complex(match["incidence"], label="match.incidence")
        reflection = _complex(match["reflection"], label="match.reflection")
        if incidence.abs_squared() == 0:
            raise BHPTDirectContractError("incidence amplitude cannot vanish")
        transmission = _complex(match["transmission"], label="match.transmission")
        ratio = _complex(match["reflection_ratio"], label="match.reflection_ratio")
        phase = _complex(match["phase_factor"], label="match.phase_factor")
        one = _DecimalComplex(Decimal(1), Decimal(0))
        expected_transmission = one / incidence
        expected_ratio = reflection / incidence
        expected_phase = expected_ratio.scale(-((-1) ** int(record["ell"])))
        _close_complex(transmission, expected_transmission, label="transmission")
        _close_complex(ratio, expected_ratio, label="reflection ratio")
        _close_complex(phase, expected_phase, label="phase factor")
        flux_residual = abs(ratio.abs_squared() + transmission.abs_squared() - 1)
        _close_decimal(
            _decimal(
                match["flux_unitarity_residual_abs"],
                label="flux_unitarity_residual_abs",
            ),
            flux_residual,
            label="flux residual",
        )
        phases.append(phase)

    selected = matches[SELECTED_MATCH_INDEX]
    for name in (
        "incidence",
        "reflection",
        "transmission",
        "reflection_ratio",
        "phase_factor",
    ):
        _close_complex(
            _complex(record[name], label=f"record.{name}"),
            _complex(selected[name], label=f"selected.{name}"),
            label=f"selected {name}",
        )
    selected_phase = phases[SELECTED_MATCH_INDEX]
    phase_spread = max((phase - selected_phase).absolute() for phase in phases)
    selected_flux_residual = _decimal(
        selected["flux_unitarity_residual_abs"],
        label="selected.flux_unitarity_residual_abs",
    )
    _validate_budget(
        record,
        phase_spread=phase_spread,
        selected_flux_residual=selected_flux_residual,
    )


def validate_external_payload(
    payload: object,
    *,
    expected_request_sha256: str | None = None,
) -> dict[str, object]:
    """Validate exact source/method/domain binding and amplitude identities."""

    if not isinstance(payload, Mapping):
        raise BHPTDirectContractError("external BHPT payload must be an object")
    expected_payload_fields = {
        "schema_version",
        "acceptance_scope",
        "global_green_permitted",
        "scientific_acceptance_status",
        "paper_figure_agreement_used",
        "request_sha256",
        "external_direct_domain",
        "toolkit",
        "runtime",
        "backend_contract",
        "precision",
        "matching",
        "numerical_uncertainty_budget",
        "convention_uncertainty_budget",
        "record_count",
        "records",
    }
    if set(payload) != expected_payload_fields:
        raise BHPTDirectContractError("external BHPT payload fields changed")
    if payload.get("schema_version") != RAW_SCHEMA:
        raise BHPTDirectContractError("external BHPT payload schema changed")
    if (
        payload.get("acceptance_scope") != CALIBRATION_PURPOSE
        or payload.get("global_green_permitted") is not False
        or payload.get("scientific_acceptance_status") != "NOT_ASSESSED"
        or payload.get("paper_figure_agreement_used") is not False
    ):
        raise BHPTDirectContractError(
            "external payload overclaims scientific acceptance"
        )
    request_sha256 = payload.get("request_sha256")
    if (
        not isinstance(request_sha256, str)
        or re.fullmatch(r"[0-9a-f]{64}", request_sha256) is None
    ):
        raise BHPTDirectContractError("external payload request identity is invalid")
    if (
        expected_request_sha256 is not None
        and payload.get("request_sha256") != expected_request_sha256
    ):
        raise BHPTDirectContractError("external payload request identity changed")

    domain = payload.get("external_direct_domain")
    expected_domain = {
        "schema": EXTERNAL_DIRECT_CALIBRATION_SCHEMA,
        "purpose": CALIBRATION_PURPOSE,
        "count": 30,
        "key_list_sha256": EXPECTED_KEY_LIST_SHA256,
    }
    if domain != expected_domain:
        raise BHPTDirectContractError("external direct domain binding changed")
    toolkit = payload.get("toolkit")
    if not isinstance(toolkit, Mapping):
        raise BHPTDirectContractError("toolkit provenance missing")
    if (
        toolkit.get("name") != "BlackHolePerturbationToolkit/ReggeWheeler"
        or toolkit.get("repository")
        != "https://github.com/BlackHolePerturbationToolkit/ReggeWheeler"
        or toolkit.get("license") != "MIT"
        or toolkit.get("source_commit") != EXPECTED_UPSTREAM_COMMIT
        or toolkit.get("source_hashes") != EXPECTED_SOURCE_SHA256
    ):
        raise BHPTDirectContractError("frozen BHPT source provenance changed")
    runtime = payload.get("runtime")
    if (
        not isinstance(runtime, Mapping)
        or set(runtime) != {"wolfram_version", "system_id"}
        or not all(
            isinstance(runtime[name], str) and bool(runtime[name])
            for name in ("wolfram_version", "system_id")
        )
    ):
        raise BHPTDirectContractError("external Wolfram runtime provenance changed")
    backend = payload.get("backend_contract")
    if not isinstance(backend, Mapping):
        raise BHPTDirectContractError("backend contract missing")
    if (
        backend.get("method") != METHOD_NAME
        or backend.get("spin_weight_argument") != 2
        or backend.get("potential_by_sector") != POTENTIAL_BY_SECTOR
        or backend.get("boundary_conditions_solved") != list(BOUNDARY_CONDITIONS)
        or backend.get("external_api_calls_per_key") != 1
        or backend.get("external_api_call_count") != 30
        or backend.get("external_boundary_solutions_per_key") != 2
        or backend.get("external_boundary_solution_count") != 60
        or backend.get("even_is_independent_radial_solution") is not True
        or backend.get("parity_derived_even_used") is not False
        or backend.get("internal_solver_fallback_used") is not False
        or backend.get("project_solver_components_used") != []
    ):
        raise BHPTDirectContractError(
            "backend is not genuinely external direct integration"
        )
    precision = payload.get("precision")
    if precision != {
        "working_precision_decimal_digits": WORKING_PRECISION,
        "precision_goal_decimal_digits": PRECISION_GOAL,
        "accuracy_goal_decimal_digits": ACCURACY_GOAL,
        "serialized_output_digits": OUTPUT_DIGITS,
    }:
        raise BHPTDirectContractError("external precision contract changed")
    matching = payload.get("matching")
    if matching != {
        "method": "two-solution Wronskian decomposition",
        "upstream_outer_boundary_radius_formula_M": "100/abs(kM)",
        "match_radius_fractions_of_upstream_outer_boundary": list(MATCH_FRACTIONS),
        "selected_match_index": SELECTED_MATCH_INDEX,
        "phase_factor_definition": "-Reflection/((-1)^ell*Incidence)",
        "transmission_definition": "1/Incidence",
        "reflection_ratio_definition": "Reflection/Incidence",
    }:
        raise BHPTDirectContractError("matching convention changed")
    if payload.get("numerical_uncertainty_budget") != {
        "status": "PARTIAL_PER_RECORD_NOT_DOMAIN_ACCEPTANCE",
        "measured_terms": [
            "three-radius matching spread",
            "selected-radius flux unitarity residual",
        ],
        "acceptance_threshold_frozen": False,
    }:
        raise BHPTDirectContractError("top-level numerical budget changed")
    if payload.get("convention_uncertainty_budget") != {
        "status": "FROZEN_FOR_EXTERNAL_CALIBRATION_NOT_GLOBAL",
        "Fourier_convention": "exp(-i*k*t)",
        "tortoise_definition": "r_star=r+2*log(r/2-1), M=1",
        "phase_factor_definition": "-Reflection/((-1)^ell*Incidence)",
        "absolute_phase_origin": "BHPT tortoise coordinate with no additive constant",
        "phase_or_normalization_fit": False,
        "remaining_convention_uncertainty": (
            "comparison consumers must prove the same master-function and phase convention"
        ),
    }:
        raise BHPTDirectContractError("top-level convention budget changed")

    records = payload.get("records")
    expected_keys = [key.to_record() for key in external_direct_calibration_keys()]
    if not isinstance(records, list) or len(records) != 30:
        raise BHPTDirectContractError("external result must contain exactly 30 records")
    with localcontext() as context:
        context.prec = 180
        for record, key in zip(records, expected_keys, strict=True):
            _validate_record(record, key)
    if payload.get("record_count") != 30:
        raise BHPTDirectContractError("external record count metadata changed")
    return {
        "schema_version": EVIDENCE_SCHEMA,
        "status": "PASS",
        "status_scope": "SOURCE_METHOD_SCHEMA_AND_ALGEBRA_ONLY",
        "scientific_acceptance_status": "NOT_ASSESSED",
        "record_count": 30,
        "odd_record_count": 15,
        "even_record_count": 15,
        "even_is_independent_radial_solution": True,
        "parity_derived_even_used": False,
        "internal_solver_fallback_used": False,
        "global_green_permitted": False,
        "acceptance_scope": CALIBRATION_PURPOSE,
    }


def _resolve_kernel(requested: str | Path) -> str | None:
    text = os.fspath(requested)
    if os.sep in text:
        path = Path(text).expanduser().absolute()
        return str(path) if path.is_file() and os.access(path, os.X_OK) else None
    return shutil.which(text)


def _process_metadata(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    return {
        "argv": [str(item) for item in result.args],
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _runtime_probe(requested: str | Path) -> dict[str, object]:
    common_candidates = (
        Path("/Applications/Mathematica.app/Contents/MacOS/WolframKernel"),
        Path("/Applications/Wolfram.app/Contents/MacOS/WolframKernel"),
        Path("/usr/local/bin/WolframKernel"),
        Path("/opt/homebrew/bin/WolframKernel"),
    )
    candidate_records = [
        {
            "path": str(path),
            "is_file": path.is_file(),
            "is_executable": path.is_file() and os.access(path, os.X_OK),
        }
        for path in common_candidates
    ]
    wrapper = shutil.which("wolframscript")
    wrapper_probe: dict[str, object] = {
        "resolved_executable": wrapper,
        "kernel_capability_claimed": False,
    }
    if wrapper is not None:
        try:
            result = subprocess.run(
                [wrapper, "-version"],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30.0,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            wrapper_probe["version_probe"] = {
                "status": "ERROR",
                "exception": f"{type(exc).__name__}: {exc}",
            }
        else:
            wrapper_probe["version_probe"] = {
                "status": "COMPLETED",
                **_process_metadata(result),
            }
    return {
        "requested_kernel": os.fspath(requested),
        "requested_kernel_resolution": _resolve_kernel(requested),
        "path_WolframKernel": shutil.which("WolframKernel"),
        "common_kernel_candidates": candidate_records,
        "wolframscript_wrapper": wrapper_probe,
        "runtime_acceptance_rule": (
            "an executable WolframKernel is required; a wrapper alone is not a "
            "scientific runtime and no alternate solver is permitted"
        ),
    }


def _not_assessed_mode_statuses(
    *, blocker: str, reason: str, science_executed: bool = False
) -> list[dict[str, object]]:
    return [
        {
            **key.to_record(),
            "status": "NOT_ASSESSED",
            "blocker": blocker,
            "reason": reason,
            "science_executed": science_executed,
            "numerical_uncertainty_budget": {
                "status": "NOT_ASSESSED",
                "measured_terms": {},
                "unresolved_terms": [
                    "direct-integration discretization",
                    "working-precision convergence",
                    "matching-radius convergence",
                    "outer-boundary asymptotic-series truncation",
                    "flux-unitarity residual",
                ],
            },
            "convention_uncertainty_budget": {
                "status": "FROZEN_REQUEST_ONLY_NOT_VALIDATED",
                "Fourier_convention": "exp(-i*k*t)",
                "tortoise_definition": "r_star=r+2*log(r/2-1), M=1",
                "phase_factor_definition": ("-Reflection/((-1)^ell*Incidence)"),
                "absolute_phase_origin": (
                    "BHPT tortoise coordinate with no additive constant"
                ),
                "remaining_uncertainty": (
                    "no external amplitudes were produced, so the convention "
                    "mapping was not numerically cross-checked"
                ),
            },
        }
        for key in external_direct_calibration_keys()
    ]


def _base_evidence() -> dict[str, object]:
    return {
        "schema_version": EVIDENCE_SCHEMA,
        "acceptance_scope": CALIBRATION_PURPOSE,
        "global_green_permitted": False,
        "paper_figure_agreement_used": False,
        "internal_solver_fallback_used": False,
        "parity_derived_even_used": False,
        "numerical_uncertainty_budget": {
            "status": "NOT_ASSESSED",
            "measured_terms": {},
            "reason": "no validated 30-record external payload is accepted yet",
            "unresolved_terms": [
                "all direct-integration numerical terms remain unmeasured"
            ],
        },
        "convention_uncertainty_budget": {
            "status": "FROZEN_REQUEST_ONLY",
            "phase_factor_definition": "-Reflection/((-1)^ell*Incidence)",
            "tortoise_definition": "r_star=r+2*log(r/2-1), M=1",
            "remaining_uncertainty": (
                "the requested convention has not been cross-checked against "
                "an external numerical amplitude"
            ),
        },
    }


def _write_blocked(
    path: Path,
    *,
    blocker: str,
    reason: str,
    science_executed: bool,
    request_sha256: str | None = None,
    runtime_probe: Mapping[str, object] | None = None,
) -> None:
    payload = _base_evidence()
    payload.update(
        {
            "status": "NOT_ASSESSED",
            "status_scope": "FAIL_CLOSED",
            "blocker": blocker,
            "reason": reason,
            "science_executed": science_executed,
            "external_record_count": 0,
            "request_sha256": request_sha256,
            "external_direct_domain": {
                "schema": EXTERNAL_DIRECT_CALIBRATION_SCHEMA,
                "purpose": CALIBRATION_PURPOSE,
                "count": 30,
                "key_list_sha256": EXPECTED_KEY_LIST_SHA256,
                "status": "NOT_ASSESSED",
                "assessed_count": 0,
                "unassessed_count": 30,
            },
            "per_mode_statuses": _not_assessed_mode_statuses(
                blocker=blocker,
                reason=reason,
                science_executed=science_executed,
            ),
        }
    )
    if runtime_probe is not None:
        payload["runtime_probe"] = dict(runtime_probe)
    atomic_json(path, payload)


def run_selected_direct(
    *,
    output_dir: str | Path,
    package_root: str | Path,
    wolfram_kernel: str | Path = "WolframKernel",
    timeout_seconds: float = 86400.0,
    project_root: str | Path = PROJECT_ROOT,
    wls_path: str | Path = WLS_PATH,
) -> int:
    """Run the 30-key external producer, always failing closed without runtime."""

    root = Path(output_dir).absolute()
    if root.exists() or root.is_symlink():
        raise BHPTDirectContractError("output directory must be fresh and absent")
    root.mkdir(parents=True, exist_ok=False, mode=0o700)
    os.chmod(root, 0o700)
    evidence_path = root / "evidence.json"
    try:
        execution = validate_execution_contract(project_root)
    except BHPTDirectContractError as exc:
        _write_blocked(
            evidence_path,
            blocker="BLOCKED_BY_FROZEN_CONTRACT",
            reason=str(exc),
            science_executed=False,
        )
        return _finish(root, returncode=3)
    try:
        source = validate_source_snapshot(package_root)
    except BHPTDirectContractError as exc:
        _write_blocked(
            evidence_path,
            blocker="BLOCKED_BY_SOURCE_IDENTITY",
            reason=str(exc),
            science_executed=False,
        )
        return _finish(root, returncode=3)
    request = build_request(
        source_snapshot=source,
        execution_contract=execution,
        wls_path=wls_path,
    )
    request_path = root / "request.json"
    atomic_json(request_path, request)
    request_sha256 = sha256_file(request_path)

    executable = _resolve_kernel(wolfram_kernel)
    if executable is None:
        probe = _runtime_probe(wolfram_kernel)
        _write_blocked(
            evidence_path,
            blocker="BLOCKED_BY_RUNTIME",
            reason="WolframKernel executable was not found or is not executable",
            science_executed=False,
            request_sha256=request_sha256,
            runtime_probe=probe,
        )
        return _finish(root, returncode=3)
    try:
        preflight = subprocess.run(
            [
                executable,
                "-noprompt",
                "-run",
                "Print[$Version]; Print[$SystemID]; Exit[0]",
            ],
            cwd=Path(project_root),
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120.0,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        _write_blocked(
            evidence_path,
            blocker="BLOCKED_BY_RUNTIME",
            reason=f"WolframKernel preflight failed: {type(exc).__name__}: {exc}",
            science_executed=False,
            request_sha256=request_sha256,
            runtime_probe=_runtime_probe(wolfram_kernel),
        )
        return _finish(root, returncode=3)
    atomic_json(root / "wolfram_preflight.json", _process_metadata(preflight))
    if preflight.returncode != 0:
        _write_blocked(
            evidence_path,
            blocker="BLOCKED_BY_RUNTIME",
            reason=f"WolframKernel preflight exited {preflight.returncode}",
            science_executed=False,
            request_sha256=request_sha256,
            runtime_probe=_runtime_probe(wolfram_kernel),
        )
        return _finish(root, returncode=3)

    external_path = root / "external_bhpt_direct.json"
    environment = os.environ.copy()
    environment.update(
        {
            "SCHWO_BHPT_DIRECT_REQUEST": str(request_path),
            "SCHWO_BHPT_DIRECT_OUTPUT": str(external_path),
            "SCHWO_BHPT_DIRECT_PACKAGE_ROOT": str(source["package_root"]),
            "SCHWO_BHPT_DIRECT_REQUEST_SHA256": request_sha256,
        }
    )
    try:
        result = subprocess.run(
            [executable, "-noprompt", "-script", str(Path(wls_path).absolute())],
            cwd=Path(project_root),
            env=environment,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        payload = _base_evidence()
        payload.update(
            {
                "status": "FAIL",
                "status_scope": "EXTERNAL_EXECUTION_INCOMPLETE",
                "blocker": "EXTERNAL_DIRECT_TIMEOUT",
                "reason": f"external direct integration exceeded {timeout_seconds} s",
                "science_executed": True,
                "external_record_count": 0,
                "request_sha256": request_sha256,
                "stdout": exc.stdout,
                "stderr": exc.stderr,
            }
        )
        atomic_json(evidence_path, payload)
        return _finish(root, returncode=2)
    atomic_json(root / "wolfram_run.json", _process_metadata(result))
    if result.returncode != 0 or not external_path.is_file():
        payload = _base_evidence()
        payload.update(
            {
                "status": "FAIL",
                "status_scope": "EXTERNAL_EXECUTION_FAILED",
                "blocker": "EXTERNAL_DIRECT_EXECUTION_FAILED",
                "reason": f"WolframKernel producer exited {result.returncode}",
                "science_executed": True,
                "external_record_count": 0,
                "external_json_exists": external_path.is_file(),
                "request_sha256": request_sha256,
            }
        )
        atomic_json(evidence_path, payload)
        return _finish(root, returncode=2)
    try:
        raw = json.loads(external_path.read_text(encoding="utf-8"))
        validated = validate_external_payload(
            raw,
            expected_request_sha256=request_sha256,
        )
    except (OSError, json.JSONDecodeError, BHPTDirectContractError) as exc:
        payload = _base_evidence()
        payload.update(
            {
                "status": "FAIL",
                "status_scope": "EXTERNAL_PAYLOAD_REJECTED",
                "blocker": "EXTERNAL_DIRECT_PAYLOAD_INVALID",
                "reason": f"{type(exc).__name__}: {exc}",
                "science_executed": True,
                "external_record_count": 0,
                "request_sha256": request_sha256,
                "external_json_sha256": sha256_file(external_path),
            }
        )
        atomic_json(evidence_path, payload)
        return _finish(root, returncode=2)
    validated.update(
        {
            "science_executed": True,
            "blocker": None,
            "request_sha256": request_sha256,
            "external_json": str(external_path),
            "external_json_sha256": sha256_file(external_path),
            "numerical_uncertainty_budget": raw["numerical_uncertainty_budget"],
            "convention_uncertainty_budget": raw["convention_uncertainty_budget"],
        }
    )
    atomic_json(evidence_path, validated)
    return _finish(root, returncode=0)


__all__ = [
    "ACCURACY_GOAL",
    "BHPTDirectContractError",
    "CALIBRATION_PURPOSE",
    "EVIDENCE_SCHEMA",
    "EXPECTED_KEY_LIST_SHA256",
    "EXPECTED_SOURCE_SHA256",
    "EXPECTED_UPSTREAM_COMMIT",
    "MATCH_FRACTIONS",
    "METHOD_NAME",
    "OUTPUT_DIGITS",
    "PRECISION_GOAL",
    "RAW_SCHEMA",
    "REQUEST_SCHEMA",
    "SELECTED_MATCH_INDEX",
    "WORKING_PRECISION",
    "build_request",
    "run_selected_direct",
    "sha256_file",
    "validate_execution_contract",
    "validate_external_payload",
    "validate_source_snapshot",
]
