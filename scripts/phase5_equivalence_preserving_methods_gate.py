#!/usr/bin/env python3
"""Deterministic support code for the frozen T4ae methods-only gate.

This module does not select scientific frequencies.  It accepts only the
five predeclared, already-existing benchmark frequencies and the frozen
full-image configuration.  Its small public surface is intentionally usable
from fault-injection tests before any long benchmark is launched.
"""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Callable, Iterable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
import cProfile
from dataclasses import asdict, dataclass
import hashlib
from io import BytesIO
import importlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import pstats
import re
import resource
import subprocess
import sys
import time
from typing import Any, Generic, TypeVar
import warnings

import numpy as np
from numpy.typing import ArrayLike
import scipy


FROZEN_FREQUENCIES = (0.86875, 1.58125, 2.91875, 3.759375, 3.89375)
FROZEN_LMAX_VALUES = {
    0.86875: (24, 36, 60, 84),
    1.58125: (72, 96, 120, 144),
    2.91875: (192, 216, 240, 264),
    3.759375: (276, 300, 324, 348),
    3.89375: (288, 312, 336, 360),
}
FROZEN_POINT_IDS = (
    "near_axis_x0_z30",
    "near_axis_x1_z30",
    "near_axis_x2_z30",
    "near_axis_x3_z30",
    "far_axis_x10_z30",
    "far_axis_x15_z30",
    "far_axis_x20_z30",
    "far_axis_x25_z30",
)
BOUNDARY_CONTRACT = {
    "M": 1.0,
    "r_out": 300.0,
    "r_in_eps": 1.0e-6,
    "rtol": 1.0e-10,
    "atol": 1.0e-12,
}
FREQUENCY_CASE_COUNT = 5 * 4 * 8
FULL_IMAGE_RESOLUTION = (241, 241)
FULL_IMAGE_VALID_COUNT = 57_884
FULL_IMAGE_MASKED_COUNT = 197
FULL_IMAGE_CONVERGENCE_PROBE_COUNT = 48
FULL_IMAGE_OPTIMIZED_CACHE_HIT_COUNT = 10_367_742
DIAGNOSTIC_FAILED_CHILD_MIDPOINT_COUNT = 87

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = (
    REPOSITORY_ROOT
    / "runs/phase5/equivalence_preserving_methods_gate/optimized"
)
GLOBAL_RUNNER_LOCK = OUTPUT_ROOT / ".runner.lock"
GLOBAL_QUARANTINE_ROOT = OUTPUT_ROOT / "quarantine"
LEGACY_ROOT = (
    REPOSITORY_ROOT
    / "runs/phase5/equivalence_preserving_methods_gate/legacy"
)
FREQUENCY_GOLDEN_ROOT = (
    REPOSITORY_ROOT
    / "runs/phase5/fig5_fig6_another_bounded_local_refinement/frequencies"
)
FULL_IMAGE_GOLDEN = (
    REPOSITORY_ROOT
    / "runs/phase5/fig3_four_frequency_dx0p25_production"
    / "t8ah_li_fig3_xz_k1p0_dx0p25.npz"
)
FULL_IMAGE_CONFIG = (
    REPOSITORY_ROOT / "configs/li_fig3_xz_production_k1p0_dx0p25.yaml"
)

FROZEN_CANDIDATE_COMMIT = "39f89289c01af7ae1709ee1e4458450d0e88b49e"
FROZEN_CANDIDATE_PARENT = "8fb8608c187280dc39fd56a78b976e6cf75a6ada"
FROZEN_LEGACY_COMMIT = FROZEN_CANDIDATE_PARENT
EXACT_IMPLEMENTATION_PATHS = (
    "docs/architecture.md",
    "docs/extension_interface.md",
    "docs/numerics.md",
    "docs/validation_plan.md",
    "scripts/phase5_equivalence_preserving_methods_gate.py",
    "src/schwgw/numerics/radial_cache.py",
    "src/schwgw/scattering/contracts.py",
    "src/schwgw/scattering/legacy_adapter.py",
    "src/schwgw/scattering/partial_wave.py",
    "tests/physics/test_q018_production_integration_design.py",
    "tests/physics/test_scalar_adapter_equivalence.py",
    "tests/regression/test_equivalence_preserving_methods_gate.py",
    "tests/unit/test_radial_cache.py",
    "tests/unit/test_scattering_contracts.py",
)
FREQUENCY_TOKENS = {
    0.86875: "0p86875",
    1.58125: "1p58125",
    2.91875: "2p91875",
    3.759375: "3p759375",
    3.89375: "3p89375",
}
FROZEN_CASE_IDS = tuple(
    f"frequency:{FREQUENCY_TOKENS[value]}" for value in FROZEN_FREQUENCIES
) + ("full-image:241x241",)
FREQUENCY_GOLDEN_SHA256 = {
    "0p86875": "58768a1c4be7b351dd5c44351b98ecd61b80b96f74ebebd5f4f3d156d2ad42c5",
    "1p58125": "4edbfcd8d6024876f6efdebd29e47736d36f1385ed29a8ad3ff6adf0e6704b9e",
    "2p91875": "d6b81923284142dfe5faf13e8932b4e5c12aed1cd253c459ab10641ab0949b8b",
    "3p759375": "22a82e643a9b348b82999f2f065f25e9e47b017582da964d1b33d2ec3473b386",
    "3p89375": "770340a9dcfbd17abb5de160f6289de473c184c1de75297fb45a8e23626b35d3",
}
LEGACY_FREQUENCY_NPZ_SHA256 = {
    "0p86875": "cfe8d6cc99ddd0a6e8290eb3bfd6eb07a4bf3f7fec98b07cdf8af8efe2740c10",
    "1p58125": "caaa6f4a0c8c1320de6cf0d6c2431b20592a63b4796d2f3a8286170d18709b67",
    "2p91875": "3bf0abfb7abc090918778012560a967ca91b6ec06bb934d529a7a758133402aa",
    "3p759375": "21d51922bedd2685113494495053c6cf2096dfb51ee08d67bbb02e13ea3d690e",
    "3p89375": "6a5aaf40484f4c2da9f01671e96cc2ad32a97542009d1fdecd1d5ffeab096ec6",
}
LEGACY_FREQUENCY_SIDECAR_SHA256 = {
    "0p86875": "b3cf47671e119576ce142e5730b4f600137246a9fb354778ab0d92cb022d302d",
    "1p58125": "ec6c7d29d7bc96c5ed7147dfd1e5207fd89627380018e93c6f724e2b607ea39b",
    "2p91875": "d5c839cdf2e2a8b0cb1c5b87754a87898684bf0e433ef2bcc1d06f2529bb9788",
    "3p759375": "890299945ff79fa9b87f9ed080e083758146349dad49a16f25ded0fb15a03166",
    "3p89375": "1a1fa986692a4384c959a6d81b4220da880b4dadb7738e6935f31830671b241e",
}
LEGACY_FULL_IMAGE_NPZ_SHA256 = (
    "210ae9715256ac9c26d53d869a5f3b8d46f92c254cf1df22825d3ef9ae171674"
)
LEGACY_FULL_IMAGE_SIDECAR_SHA256 = (
    "08f7a8e3e4ae508265b4f6480ebcb528289f3827202beff3cb12a22d67821b7a"
)
FULL_IMAGE_GOLDEN_SHA256 = (
    "0de560ce7a2696074e708506240c69e43eb4d40520447ec378208b37f64c0132"
)
FULL_IMAGE_FILENAME = "t8ah_li_fig3_xz_k1p0_dx0p25.npz"
FULL_IMAGE_ARRAY_ORDER = (
    "theta",
    "phi",
    "h_plus",
    "h_cross",
    "metadata_json",
    "x",
    "z",
    "r",
    "valid_mask",
)
FULL_IMAGE_SCIENTIFIC_ARRAY_ORDER = (
    "theta",
    "phi",
    "h_plus",
    "h_cross",
    "x",
    "z",
    "r",
    "valid_mask",
)
FULL_IMAGE_STABLE_METADATA_KEYS = (
    "boundary",
    "case_id",
    "config",
    "convention",
    "grid",
    "lmax",
)
FULL_IMAGE_METADATA_DTYPE = np.dtype("<U14000000")
PIXEL_NRMSE_BUDGET = 1.0e-11
NORMALIZED_LINF_BUDGET = 5.0e-10
CONFIG_SHA256 = (
    "4b714db46cc92488db95417d7211ec2f05d0ffc383867d680f5b403e13904971"
)
CONFIG_BLOB_SHA1 = "5de5c234630c39909568ec20e2d4c2c5c3012071"

GATE_PATHS = {
    "t4ae_prompt": (
        REPOSITORY_ROOT
        / "docs/prompts/phase5_t4ae_equivalence_preserving_methods_gate.md"
    ),
    "t7cg_prompt": (
        REPOSITORY_ROOT
        / "docs/prompts/phase5_t7cg_methods_prequalification_package_review.md"
    ),
    "t7ch_prompt": (
        REPOSITORY_ROOT
        / "docs/prompts/phase5_t7ch_equivalence_preserving_methods_review.md"
    ),
    "plan": (
        REPOSITORY_ROOT
        / "docs/superpowers/plans"
        / "2026-07-24-t4ae-equivalence-preserving-methods-gate.md"
    ),
    "design": (
        REPOSITORY_ROOT
        / "docs/superpowers/specs"
        / "2026-07-24-t4ae-equivalence-preserving-methods-prequalification-design.md"
    ),
}
EXPECTED_GATE_HASHES = {
    "t4ae_prompt": "9e8a65679e4f04e23a24aa6a0bcc0df83dd77c53c76366e136a75518d6c0ec9a",
    "t7cg_prompt": "881e934f4b8ae4735a8106f369a5258b253d0619c6ac66cb03a4dada8dfb717c",
    "t7ch_prompt": "cee666db6adf78811d706d70b3e8e31793caf01cd13ff3161c84d97dd681ebfe",
    "plan": "e6e65f9f3ffe478046ad73294fa40766918d47384a9f0f6851469162b8953d81",
    "design": "99f6f22056ccf50f5d54a11d98f93151d67e747bf9f07909ffecb04151b1a78f",
}
THREAD_VARIABLES = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "BLIS_NUM_THREADS",
    "PYTHONHASHSEED",
)
EXPECTED_THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "BLIS_NUM_THREADS": "1",
    "PYTHONHASHSEED": "0",
}
FREQUENCY_EXACT_ARRAY_NAMES = {
    "kM",
    "point_ids",
    "point_group",
    "point_x",
    "point_y",
    "point_z",
    "point_r",
    "point_theta",
    "point_phi",
    "lmax_values",
    "valid_ratio_plus_mask",
    "valid_ratio_cross_mask",
}
FREQUENCY_STABLE_METADATA_KEYS = (
    "schema_version",
    "kM",
    "frequency_token",
    "point_ids",
    "lmax_values",
    "final_lmax_pair",
    "adapter",
    "units",
    "dtypes",
    "ordering",
    "flags",
)
FREQUENCY_EMBEDDED_METADATA_KEYS = {
    "schema_version",
    "complete",
    "kM",
    "frequency_token",
    "point_ids",
    "lmax_values",
    "final_lmax_pair",
    "max_final_pair_delta_plus",
    "max_final_pair_delta_cross",
    "runtime_seconds",
    "radial_solve_count",
    "radial_reuse_count",
    "radial_warning_codes",
    "radial_warning_count",
    "adapter_use_count",
    "adapter",
    "generation_contract_hash",
    "metadata_contract_hash",
    "source_paths",
    "source_hashes",
    "gate_paths",
    "gate_hashes",
    "implementation",
    "selected_code_hashes",
    "units",
    "dtypes",
    "ordering",
    "flags",
    "array_fingerprints",
    "t4ae_optimized_methods",
}
RAW_WARNING_SCHEMA = "strict_location_line_message_allowlist_v1"
_ALLOWED_RAW_RUNTIME_WARNINGS = {
    ("scipy/integrate/_ivp/rk.py", 63, "overflow encountered in dot"),
    (
        "scipy/integrate/_ivp/rk.py",
        63,
        "invalid value encountered in multiply",
    ),
    (
        "scipy/integrate/_ivp/rk.py",
        521,
        "invalid value encountered in divide",
    ),
    (
        "scipy/integrate/_ivp/rk.py",
        522,
        "invalid value encountered in divide",
    ),
    ("scipy/integrate/_ivp/rk.py", 547, "overflow encountered in dot"),
    ("scipy/integrate/_ivp/rk.py", 547, "invalid value encountered in dot"),
    (
        "scipy/integrate/_ivp/rk.py",
        547,
        "invalid value encountered in multiply",
    ),
    (
        "src/schwgw/numerics/radial_solver.py",
        2716,
        "overflow encountered in scalar multiply",
    ),
    (
        "src/schwgw/numerics/radial_solver.py",
        2716,
        "invalid value encountered in scalar multiply",
    ),
    (
        "src/schwgw/numerics/radial_solver.py",
        2716,
        "overflow encountered in scalar divide",
    ),
    (
        "src/schwgw/numerics/radial_solver.py",
        2716,
        "invalid value encountered in scalar divide",
    ),
    (
        "src/schwgw/numerics/radial_solver.py",
        2716,
        "invalid value encountered in divide",
    ),
}
OUTPUT_SCHEMA_VERSION = "t4ae_optimized_methods_benchmark_v1"
ATOMIC_SCHEMA_VERSION = "t4ae_atomic_npz_json_pair_v1"
RUNNER_VERSION = "t4ae_equivalence_preserving_methods_gate_v1"

ABSOLUTE_BUDGET = 5.0e-12
NORMALIZED_RELATIVE_BUDGET = 5.0e-10
PHASE_GUARD = 1.0e-10
PHASE_BUDGET = 5.0e-9
SOLVE_RATIO_LIMIT = 0.70
WALL_RATIO_LIMIT = 0.85
CPU_RATIO_LIMIT = 0.85
CASE_WALL_RATIO_LIMIT = 1.05
RSS_RATIO_LIMIT = 1.25
BOUNDARY_RESIDUAL_HARD_LIMIT = 1.0e-8
WRONSKIAN_RESIDUAL_HARD_LIMIT = 1.0e-7
FLUX_RESIDUAL_HARD_LIMIT = 1.0e-7

WORK_UNIT_SCHEMA_VERSION = "t4ae_work_unit_v1"
_HEX_64 = re.compile(r"^[0-9a-f]{64}$")
_HEX_40 = re.compile(r"^[0-9a-f]{40}$")
_Payload = TypeVar("_Payload")
_ResultPayload = TypeVar("_ResultPayload")


class GateContractError(RuntimeError):
    """Raised when frozen scope, identity, or atomic state is invalid."""


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        if not all(isinstance(key, str) for key in value):
            raise GateContractError(
                "canonical JSON mappings require string keys"
            )
        return {
            key: _json_safe(item)
            for key, item in sorted(value.items())
        }
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"real": float(value.real), "imag": float(value.imag)}
    return value


def _canonical_json(value: Any) -> str:
    try:
        return json.dumps(
            _json_safe(value),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise GateContractError("value is not canonical-JSON serializable") from exc


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _scientific_sort_key(value: Any) -> tuple[Any, ...]:
    if isinstance(value, np.generic):
        return _scientific_sort_key(value.item())
    if value is None:
        return (0,)
    if isinstance(value, bool):
        return (1, int(value))
    if isinstance(value, (int, float)):
        numeric = float(value)
        if not math.isfinite(numeric):
            raise GateContractError("scientific sort keys must be finite")
        return (2, value)
    if isinstance(value, str):
        return (3, value)
    if isinstance(value, Path):
        return (4, str(value))
    if isinstance(value, complex):
        if not math.isfinite(value.real) or not math.isfinite(value.imag):
            raise GateContractError("scientific sort keys must be finite")
        return (5, value.real, value.imag)
    if isinstance(value, (tuple, list)):
        return (
            6,
            tuple(_scientific_sort_key(item) for item in value),
        )
    if isinstance(value, Mapping):
        if not all(isinstance(key, str) for key in value):
            raise GateContractError(
                "scientific-key mappings require string keys"
            )
        return (
            7,
            tuple(
                (key, _scientific_sort_key(item))
                for key, item in sorted(value.items())
            ),
        )
    raise GateContractError(
        f"unsupported scientific sort-key type: {type(value).__qualname__}"
    )


def _validate_sha256(value: str, label: str) -> str:
    if not isinstance(value, str) or _HEX_64.fullmatch(value) is None:
        raise GateContractError(f"{label} must be 64 lowercase hexadecimal digits")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _git_blob_oid(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(
        header + payload,
        usedforsecurity=False,
    ).hexdigest()


def _git(*arguments: str) -> str:
    try:
        completed = subprocess.run(
            ("git", "-C", str(REPOSITORY_ROOT), *arguments),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise GateContractError(
            f"cannot establish git identity for {arguments!r}: {exc}"
        ) from exc
    return completed.stdout.strip()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GateContractError(f"cannot read canonical JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise GateContractError(f"canonical JSON is not an object: {path}")
    return value


def _array_fingerprint(array: np.ndarray) -> dict[str, Any]:
    contiguous = np.ascontiguousarray(array)
    digest = hashlib.sha256()
    digest.update(contiguous.dtype.str.encode("ascii"))
    digest.update(b"\0")
    digest.update(_canonical_json(list(contiguous.shape)).encode("ascii"))
    digest.update(b"\0")
    digest.update(contiguous.tobytes(order="C"))
    return {
        "shape": list(contiguous.shape),
        "dtype": str(contiguous.dtype),
        "sha256": digest.hexdigest(),
    }


def _payload_fingerprints(
    arrays: Mapping[str, np.ndarray],
    order: Sequence[str],
) -> dict[str, dict[str, Any]]:
    if tuple(arrays) != tuple(order):
        raise GateContractError("payload order changed before fingerprinting")
    return {name: _array_fingerprint(arrays[name]) for name in order}


def _legacy_frequency_fingerprint(array: np.ndarray) -> str:
    stream = BytesIO()
    np.save(stream, np.asarray(array), allow_pickle=False)
    return _sha256_bytes(stream.getvalue())


def _read_npz(
    path: Path,
) -> tuple[tuple[str, ...], dict[str, np.ndarray], dict[str, Any], str]:
    try:
        with np.load(path, allow_pickle=False) as archive:
            order = tuple(archive.files)
            if "metadata_json" not in archive.files:
                raise GateContractError(f"metadata_json is absent from {path}")
            arrays = {
                name: np.asarray(archive[name]).copy()
                for name in archive.files
                if name != "metadata_json"
            }
            metadata_array = np.asarray(archive["metadata_json"])
    except (OSError, ValueError, KeyError) as exc:
        raise GateContractError(f"cannot read NPZ {path}: {exc}") from exc
    if metadata_array.shape != () or metadata_array.dtype.kind != "U":
        raise GateContractError(f"metadata_json schema mismatch in {path}")
    metadata_text = str(metadata_array.item())
    try:
        metadata = json.loads(metadata_text)
    except json.JSONDecodeError as exc:
        raise GateContractError(f"invalid embedded metadata in {path}: {exc}") from exc
    if not isinstance(metadata, dict):
        raise GateContractError(f"embedded metadata is not an object in {path}")
    return order, arrays, metadata, metadata_text


@dataclass(frozen=True)
class BenchmarkIdentity:
    """Complete identity boundary for one benchmark/checkpoint family."""

    implementation_sha256: str
    physics_sha256: str
    solver_sha256: str
    config_sha256: str
    source_sha256: str
    gate_sha256: str
    environment_sha256: str

    def __post_init__(self) -> None:
        for field_name, value in asdict(self).items():
            _validate_sha256(value, field_name)

    @property
    def canonical_digest(self) -> str:
        return _canonical_sha256(asdict(self))


def _verify_self(expected_self_sha256: str) -> str:
    _validate_sha256(expected_self_sha256, "expected_self_sha256")
    actual = _sha256(Path(__file__).resolve())
    if actual != expected_self_sha256:
        raise GateContractError(
            "runner self SHA-256 mismatch: "
            f"expected {expected_self_sha256}, got {actual}"
        )
    return actual


def _tree_entries(
    commit: str,
    prefix: str,
    *,
    require_worktree_match: bool,
) -> list[dict[str, Any]]:
    listing = _git("ls-tree", "-r", commit, "--", prefix)
    entries: list[dict[str, Any]] = []
    for row in listing.splitlines():
        prefix_record, relative = row.split("\t", 1)
        mode, kind, blob_sha1 = prefix_record.split()
        if kind != "blob":
            raise GateContractError(f"unexpected tree entry kind: {row}")
        path = REPOSITORY_ROOT / relative
        if not path.is_file():
            raise GateContractError(f"implementation/source path is absent: {relative}")
        payload = path.read_bytes()
        worktree_blob = _git_blob_oid(payload)
        if require_worktree_match and worktree_blob != blob_sha1:
            raise GateContractError(
                "commit/worktree blob mismatch: "
                f"{relative}: {blob_sha1} != {worktree_blob}"
            )
        entries.append(
            {
                "path": relative,
                "mode": mode,
                "blob_sha1": blob_sha1,
                "worktree_blob_sha1": worktree_blob,
                "sha256": _sha256_bytes(payload),
                "size": len(payload),
            }
        )
    if [record["path"] for record in entries] != sorted(
        record["path"] for record in entries
    ):
        raise GateContractError("git tree entries are not in canonical path order")
    return entries


def _implementation_identity(expected_commit: str) -> dict[str, Any]:
    if _HEX_40.fullmatch(expected_commit) is None:
        raise GateContractError(
            "expected implementation commit must be 40 lowercase hex digits"
        )
    root = Path(_git("rev-parse", "--show-toplevel")).resolve()
    if root != REPOSITORY_ROOT:
        raise GateContractError("repository root identity mismatch")
    head = _git("rev-parse", "HEAD")
    if head != expected_commit:
        raise GateContractError(
            f"implementation HEAD mismatch: expected {expected_commit}, got {head}"
        )
    parent = _git("rev-parse", "HEAD^")
    if parent != FROZEN_CANDIDATE_COMMIT:
        raise GateContractError(
            "implementation commit is not directly based on the frozen candidate"
        )
    candidate_parent = _git("rev-parse", f"{FROZEN_CANDIDATE_COMMIT}^")
    if candidate_parent != FROZEN_CANDIDATE_PARENT:
        raise GateContractError("frozen candidate parent identity changed")
    commit_paths = tuple(
        sorted(
            _git(
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                expected_commit,
            ).splitlines()
        )
    )
    if commit_paths != tuple(sorted(EXACT_IMPLEMENTATION_PATHS)):
        raise GateContractError(
            "implementation commit does not change exactly the frozen fourteen paths"
        )
    dirty = _git(
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--",
        *EXACT_IMPLEMENTATION_PATHS,
    )
    if dirty:
        raise GateContractError(
            "exact implementation scope has worktree changes: "
            + _canonical_json(dirty.splitlines())
        )

    records = []
    for relative in EXACT_IMPLEMENTATION_PATHS:
        path = REPOSITORY_ROOT / relative
        payload = path.read_bytes()
        commit_blob = _git("rev-parse", f"{expected_commit}:{relative}")
        worktree_blob = _git_blob_oid(payload)
        if worktree_blob != commit_blob:
            raise GateContractError(
                f"exact-fourteen commit/worktree blob mismatch: {relative}"
            )
        records.append(
            {
                "path": relative,
                "blob_sha1": commit_blob,
                "worktree_blob_sha1": worktree_blob,
                "sha256": _sha256_bytes(payload),
                "size": len(payload),
            }
        )
    records.sort(key=lambda record: record["path"])
    return {
        "commit": head,
        "parent": parent,
        "candidate_parent": candidate_parent,
        "path_count": len(records),
        "paths": list(EXACT_IMPLEMENTATION_PATHS),
        "entries": records,
        "manifest_sha256": _canonical_sha256(records),
    }


def _source_identity(expected_commit: str) -> dict[str, Any]:
    dirty = _git(
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--",
        "src/schwgw",
    )
    if dirty:
        raise GateContractError(
            "source worktree is not commit-identical: "
            + _canonical_json(dirty.splitlines())
        )
    entries = _tree_entries(
        expected_commit,
        "src/schwgw",
        require_worktree_match=True,
    )
    if not entries:
        raise GateContractError("source tree is empty")
    physics_entries = [
        record
        for record in entries
        if record["path"].split("/")[2]
        in {"angular", "backgrounds", "perturbations", "scattering", "waves"}
    ]
    solver_entries = [
        record
        for record in entries
        if record["path"].startswith("src/schwgw/numerics/")
        or record["path"]
        in {
            "src/schwgw/io/config.py",
            "src/schwgw/io/results.py",
            "src/schwgw/io/tablei_another_bounded_local_refinement.py",
            "src/schwgw/scattering/partial_wave.py",
        }
    ]
    return {
        "tree_sha1": _git("rev-parse", f"{expected_commit}:src/schwgw"),
        "count": len(entries),
        "entries": entries,
        "manifest_sha256": _canonical_sha256(entries),
        "physics_manifest_sha256": _canonical_sha256(physics_entries),
        "solver_manifest_sha256": _canonical_sha256(solver_entries),
    }


def _gate_identity() -> dict[str, Any]:
    records = {}
    for name, path in GATE_PATHS.items():
        actual = _sha256(path)
        expected = EXPECTED_GATE_HASHES[name]
        if actual != expected:
            raise GateContractError(
                f"frozen gate mismatch for {name}: expected {expected}, got {actual}"
            )
        records[name] = {
            "path": str(path),
            "sha256": actual,
            "size": path.stat().st_size,
        }
    return {
        "records": records,
        "manifest_sha256": _canonical_sha256(records),
    }


def _config_identity(expected_commit: str) -> dict[str, Any]:
    payload = FULL_IMAGE_CONFIG.read_bytes()
    actual_sha256 = _sha256_bytes(payload)
    if actual_sha256 != CONFIG_SHA256:
        raise GateContractError("full-image config SHA-256 mismatch")
    commit_blob = _git(
        "rev-parse",
        f"{expected_commit}:configs/{FULL_IMAGE_CONFIG.name}",
    )
    if commit_blob != CONFIG_BLOB_SHA1 or _git_blob_oid(payload) != commit_blob:
        raise GateContractError("full-image config commit/worktree blob mismatch")
    return {
        "path": str(FULL_IMAGE_CONFIG),
        "repository_path": f"configs/{FULL_IMAGE_CONFIG.name}",
        "blob_sha1": commit_blob,
        "sha256": actual_sha256,
        "size": len(payload),
    }


def _blas_dependency(name: str) -> dict[str, Any]:
    config = getattr(np.__config__, "CONFIG", {})
    dependencies = config.get("Build Dependencies", {})
    payload = dependencies.get(name, {})
    return _json_safe(payload) if isinstance(payload, Mapping) else {}


def _environment_identity() -> dict[str, Any]:
    thread_environment = {
        name: os.environ.get(name) for name in THREAD_VARIABLES
    }
    if thread_environment != EXPECTED_THREAD_ENVIRONMENT:
        raise GateContractError(
            "controlled thread environment mismatch: "
            + _canonical_json(
                {
                    "expected": EXPECTED_THREAD_ENVIRONMENT,
                    "actual": thread_environment,
                }
            )
        )
    record = {
        "python": sys.version,
        "executable": sys.executable,
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "blas": _blas_dependency("blas"),
        "lapack": _blas_dependency("lapack"),
        "thread_environment": thread_environment,
    }
    legacy = _read_json(
        LEGACY_ROOT / "full_image" / f"{FULL_IMAGE_FILENAME}.json"
    )["benchmark_record"]["environment"]
    for name in (
        "python",
        "executable",
        "numpy",
        "scipy",
        "platform",
        "machine",
        "processor",
        "cpu_count",
        "blas",
        "lapack",
        "thread_environment",
    ):
        if record[name] != legacy[name]:
            raise GateContractError(
                f"optimized/legacy environment mismatch: {name}"
            )
    record["environment_sha256"] = _canonical_sha256(record)
    return record


def _load_runtime_modules() -> dict[str, Any]:
    return {
        "config": importlib.import_module("schwgw.io.config"),
        "results": importlib.import_module("schwgw.io.results"),
        "numerics": importlib.import_module("schwgw.numerics"),
        "partial_wave": importlib.import_module(
            "schwgw.scattering.partial_wave"
        ),
        "tablei": importlib.import_module(
            "schwgw.io.tablei_another_bounded_local_refinement"
        ),
    }


def _source_path_for_module(path: Path) -> Path:
    if path.suffix in {".pyc", ".pyo"}:
        try:
            return Path(importlib.util.source_from_cache(str(path)))
        except ValueError as exc:
            raise GateContractError(
                f"cannot map loaded bytecode to source: {path}"
            ) from exc
    return path


def _loaded_module_identity(
    source: Mapping[str, Any],
) -> dict[str, Any]:
    expected = {record["path"]: record for record in source["entries"]}
    records = []
    for name, module in sorted(sys.modules.items()):
        if name != "schwgw" and not name.startswith("schwgw."):
            continue
        raw_path = getattr(module, "__file__", None)
        if raw_path is None:
            raise GateContractError(f"loaded schwgw module has no path: {name}")
        path = _source_path_for_module(Path(raw_path)).resolve()
        try:
            relative = str(path.relative_to(REPOSITORY_ROOT))
        except ValueError as exc:
            raise GateContractError(
                f"loaded schwgw module escaped repository: {name} -> {path}"
            ) from exc
        source_record = expected.get(relative)
        if source_record is None:
            raise GateContractError(
                f"loaded schwgw module is not in frozen source: {relative}"
            )
        payload = path.read_bytes()
        if (
            _sha256_bytes(payload) != source_record["sha256"]
            or _git_blob_oid(payload) != source_record["blob_sha1"]
        ):
            raise GateContractError(f"loaded module identity mismatch: {name}")
        records.append(
            {
                "module": name,
                "repository_path": relative,
                "sha256": source_record["sha256"],
                "blob_sha1": source_record["blob_sha1"],
            }
        )
    required = {
        "schwgw.io.config",
        "schwgw.io.results",
        "schwgw.io.tablei_another_bounded_local_refinement",
        "schwgw.numerics",
        "schwgw.numerics.radial_solver",
        "schwgw.scattering.partial_wave",
    }
    missing = required - {record["module"] for record in records}
    if missing:
        raise GateContractError(
            "required runtime module is absent: " + _canonical_json(sorted(missing))
        )
    return {
        "count": len(records),
        "modules": records,
        "manifest_sha256": _canonical_sha256(records),
    }


@dataclass(frozen=True)
class ComplexErrorMetrics:
    max_absolute: float
    max_normalized_relative: float
    max_guarded_phase: float
    phase_sample_count: int
    passed: bool


def compare_complex_arrays(
    candidate: ArrayLike,
    reference: ArrayLike,
) -> ComplexErrorMetrics:
    """Apply the frozen complex-value and guarded-phase error budget."""

    actual = np.asarray(candidate)
    expected = np.asarray(reference)
    if actual.shape != expected.shape:
        raise GateContractError("complex-array shape mismatch")
    if actual.dtype.kind != "c" or expected.dtype.kind != "c":
        actual = np.asarray(actual, dtype=np.complex128)
        expected = np.asarray(expected, dtype=np.complex128)
    if not np.array_equal(np.isfinite(actual), np.isfinite(expected)):
        raise GateContractError("complex-array finite pattern mismatch")
    finite = np.isfinite(actual) & np.isfinite(expected)
    if not np.any(finite):
        return ComplexErrorMetrics(0.0, 0.0, 0.0, 0, True)

    actual_finite = actual[finite]
    expected_finite = expected[finite]
    difference = np.abs(actual_finite - expected_finite)
    denominator = np.maximum(
        np.maximum(np.abs(actual_finite), np.abs(expected_finite)),
        1.0e-30,
    )
    max_absolute = float(np.max(difference))
    max_relative = float(np.max(difference / denominator))
    phase_mask = (
        (np.abs(actual_finite) > PHASE_GUARD)
        & (np.abs(expected_finite) > PHASE_GUARD)
    )
    phase_count = int(np.count_nonzero(phase_mask))
    max_phase = 0.0
    if phase_count:
        max_phase = float(
            np.max(
                np.abs(
                    np.angle(
                        actual_finite[phase_mask]
                        * np.conjugate(expected_finite[phase_mask])
                    )
                )
            )
        )
    return ComplexErrorMetrics(
        max_absolute=max_absolute,
        max_normalized_relative=max_relative,
        max_guarded_phase=max_phase,
        phase_sample_count=phase_count,
        passed=bool(
            max_absolute <= ABSOLUTE_BUDGET
            and max_relative <= NORMALIZED_RELATIVE_BUDGET
            and max_phase <= PHASE_BUDGET
        ),
    )


def _compare_real_arrays(
    candidate: np.ndarray,
    reference: np.ndarray,
) -> dict[str, Any]:
    actual = np.asarray(candidate)
    expected = np.asarray(reference)
    if actual.shape != expected.shape or actual.dtype != expected.dtype:
        raise GateContractError("real-array shape/dtype mismatch")
    if not np.array_equal(np.isfinite(actual), np.isfinite(expected)):
        raise GateContractError("real-array finite pattern mismatch")
    finite = np.isfinite(actual) & np.isfinite(expected)
    if not np.any(finite):
        return {
            "max_absolute": 0.0,
            "max_normalized_relative": 0.0,
            "passed": True,
        }
    actual_finite = actual[finite]
    expected_finite = expected[finite]
    difference = np.abs(actual_finite - expected_finite)
    denominator = np.maximum(
        np.maximum(np.abs(actual_finite), np.abs(expected_finite)),
        1.0e-30,
    )
    max_absolute = float(np.max(difference))
    max_relative = float(np.max(difference / denominator))
    return {
        "max_absolute": max_absolute,
        "max_normalized_relative": max_relative,
        "passed": bool(
            max_absolute <= ABSOLUTE_BUDGET
            and max_relative <= NORMALIZED_RELATIVE_BUDGET
        ),
    }


def _scientific_array_comparison(
    candidate_order: Sequence[str],
    candidate: Mapping[str, np.ndarray],
    reference_order: Sequence[str],
    reference: Mapping[str, np.ndarray],
    *,
    exact_names: set[str],
) -> dict[str, Any]:
    if tuple(candidate_order) != tuple(reference_order):
        raise GateContractError("array order mismatch")
    if set(candidate) != set(reference):
        raise GateContractError("scientific array-name mismatch")
    bitwise = True
    max_absolute = 0.0
    max_relative = 0.0
    max_phase = 0.0
    phase_count = 0
    per_array: dict[str, Any] = {}
    for name in candidate_order:
        actual = np.asarray(candidate[name])
        expected = np.asarray(reference[name])
        if actual.shape != expected.shape or actual.dtype != expected.dtype:
            raise GateContractError(f"array shape/dtype mismatch: {name}")
        if actual.dtype.kind in {"b", "i", "u", "f", "c"}:
            actual_finite = np.isfinite(actual)
            expected_finite = np.isfinite(expected)
            if not np.array_equal(actual_finite, expected_finite):
                raise GateContractError(f"array finite pattern mismatch: {name}")
            if actual.dtype.kind == "f":
                category_pairs = ((actual, expected),)
            elif actual.dtype.kind == "c":
                category_pairs = (
                    (actual.real, expected.real),
                    (actual.imag, expected.imag),
                )
            else:
                category_pairs = ()
            for actual_part, expected_part in category_pairs:
                if (
                    not np.array_equal(
                        np.isnan(actual_part),
                        np.isnan(expected_part),
                    )
                    or not np.array_equal(
                        np.isposinf(actual_part),
                        np.isposinf(expected_part),
                    )
                    or not np.array_equal(
                        np.isneginf(actual_part),
                        np.isneginf(expected_part),
                    )
                ):
                    raise GateContractError(
                        f"array nonfinite category mismatch: {name}"
                    )
            value_equal = bool(
                np.array_equal(actual, expected, equal_nan=True)
            )
        else:
            value_equal = bool(np.array_equal(actual, expected))
        bitwise_equal = bool(
            np.ascontiguousarray(actual).tobytes(order="C")
            == np.ascontiguousarray(expected).tobytes(order="C")
        )
        bitwise = bitwise and bitwise_equal
        if name in exact_names:
            if not bitwise_equal:
                raise GateContractError(f"exact array mismatch: {name}")
            per_array[name] = {"exact": True, "bitwise": True}
            continue
        if actual.dtype.kind == "c":
            metrics = compare_complex_arrays(actual, expected)
            record = asdict(metrics)
            max_absolute = max(max_absolute, metrics.max_absolute)
            max_relative = max(
                max_relative,
                metrics.max_normalized_relative,
            )
            max_phase = max(max_phase, metrics.max_guarded_phase)
            phase_count += metrics.phase_sample_count
            if not metrics.passed:
                raise GateContractError(
                    f"complex equivalence budget exceeded: {name}"
                )
        elif actual.dtype.kind in {"f", "i", "u"}:
            record = _compare_real_arrays(actual, expected)
            max_absolute = max(max_absolute, record["max_absolute"])
            max_relative = max(
                max_relative,
                record["max_normalized_relative"],
            )
            if not record["passed"]:
                raise GateContractError(
                    f"real equivalence budget exceeded: {name}"
                )
        else:
            if not value_equal:
                raise GateContractError(f"non-numeric array mismatch: {name}")
            record = {"exact": True}
        record["bitwise"] = bitwise_equal
        per_array[name] = record
    return {
        "array_order_exact": True,
        "array_names_exact": True,
        "schema_shape_dtype_finite_exact": True,
        "bitwise_all": bitwise,
        "max_absolute_difference": max_absolute,
        "max_normalized_relative_difference": max_relative,
        "max_guarded_phase_difference_rad": max_phase,
        "guarded_phase_sample_count": phase_count,
        "per_array": per_array,
        "budget_passed": True,
    }


def _frequency_paths(
    root: Path,
    token: str,
) -> tuple[Path, Path]:
    npz = root / "frequencies" / f"kM_{token}.npz"
    return npz, npz.with_name(npz.name + ".json")


def _audit_legacy_frequency(token: str) -> dict[str, Any]:
    if token not in LEGACY_FREQUENCY_NPZ_SHA256:
        raise GateContractError(f"unknown frozen frequency token: {token}")
    npz, sidecar_path = _frequency_paths(LEGACY_ROOT, token)
    golden = FREQUENCY_GOLDEN_ROOT / f"kM_{token}.npz"
    expected = {
        "npz": LEGACY_FREQUENCY_NPZ_SHA256[token],
        "sidecar": LEGACY_FREQUENCY_SIDECAR_SHA256[token],
        "golden": FREQUENCY_GOLDEN_SHA256[token],
    }
    actual = {
        "npz": _sha256(npz),
        "sidecar": _sha256(sidecar_path),
        "golden": _sha256(golden),
    }
    if actual != expected:
        raise GateContractError(
            "immutable legacy frequency identity mismatch: "
            + _canonical_json({"token": token, "expected": expected, "actual": actual})
        )
    sidecar = _read_json(sidecar_path)
    if (
        sidecar.get("npz_sha256") != expected["npz"]
        or sidecar.get("frequency_token") != token
        or sidecar.get("implementation", {}).get("commit")
        != FROZEN_LEGACY_COMMIT
        or sidecar.get("legacy_golden_comparison", {}).get("golden_sha256")
        != expected["golden"]
        or sidecar.get("legacy_golden_comparison", {}).get("budget_passed")
        is not True
    ):
        raise GateContractError(
            f"legacy frequency sidecar provenance mismatch: {token}"
        )
    order, arrays, embedded, _ = _read_npz(npz)
    golden_order, golden_arrays, _, _ = _read_npz(golden)
    scientific_order = tuple(name for name in order if name != "metadata_json")
    golden_scientific_order = tuple(
        name for name in golden_order if name != "metadata_json"
    )
    comparison = _scientific_array_comparison(
        scientific_order,
        arrays,
        golden_scientific_order,
        golden_arrays,
        exact_names=set(scientific_order),
    )
    for name, fingerprint in sidecar.get("array_fingerprints", {}).items():
        if (
            name not in arrays
            or _legacy_frequency_fingerprint(arrays[name]) != fingerprint
        ):
            raise GateContractError(
                f"legacy frequency fingerprint mismatch: {token}/{name}"
            )
    sidecar_without_commit = dict(sidecar)
    sidecar_without_commit.pop("npz_sha256", None)
    if embedded != sidecar_without_commit:
        raise GateContractError(
            f"legacy frequency embedded/sidecar metadata mismatch: {token}"
        )
    raw = sidecar.get(
        "raw_runtime_warning_record",
        {
            "policy": RAW_WARNING_SCHEMA,
            "total_count": 0,
            "entries": [],
            "all_recognized": True,
        },
    )
    return {
        "token": token,
        "npz_path": str(npz),
        "sidecar_path": str(sidecar_path),
        "golden_path": str(golden),
        "npz_sha256": expected["npz"],
        "sidecar_sha256": expected["sidecar"],
        "golden_sha256": expected["golden"],
        "scientific_comparison": comparison,
        "metadata": sidecar,
        "raw_warning_record": raw,
    }


def _audit_legacy_full_image() -> dict[str, Any]:
    npz = LEGACY_ROOT / "full_image" / FULL_IMAGE_FILENAME
    sidecar_path = npz.with_name(npz.name + ".json")
    actual = {
        "npz": _sha256(npz),
        "sidecar": _sha256(sidecar_path),
        "golden": _sha256(FULL_IMAGE_GOLDEN),
    }
    expected = {
        "npz": LEGACY_FULL_IMAGE_NPZ_SHA256,
        "sidecar": LEGACY_FULL_IMAGE_SIDECAR_SHA256,
        "golden": FULL_IMAGE_GOLDEN_SHA256,
    }
    if actual != expected:
        raise GateContractError(
            "immutable legacy full-image identity mismatch: "
            + _canonical_json({"expected": expected, "actual": actual})
        )
    sidecar = _read_json(sidecar_path)
    if (
        sidecar.get("npz_sha256") != expected["npz"]
        or sidecar.get("implementation_commit") != FROZEN_LEGACY_COMMIT
        or sidecar.get("golden_sha256") != expected["golden"]
        or sidecar.get("comparison", {}).get("budget_passed") is not True
        or sidecar.get("transaction", {}).get("state") != "complete"
    ):
        raise GateContractError("legacy full-image sidecar provenance mismatch")
    order, arrays, metadata, metadata_text = _read_npz(npz)
    golden_order, golden_arrays, golden_metadata, _ = _read_npz(
        FULL_IMAGE_GOLDEN
    )
    if order != FULL_IMAGE_ARRAY_ORDER or golden_order != FULL_IMAGE_ARRAY_ORDER:
        raise GateContractError("legacy/golden full-image array order mismatch")
    comparison = _scientific_array_comparison(
        FULL_IMAGE_SCIENTIFIC_ARRAY_ORDER,
        arrays,
        FULL_IMAGE_SCIENTIFIC_ARRAY_ORDER,
        golden_arrays,
        exact_names=set(FULL_IMAGE_SCIENTIFIC_ARRAY_ORDER),
    )
    if {
        key: metadata[key] for key in FULL_IMAGE_STABLE_METADATA_KEYS
    } != {
        key: golden_metadata[key] for key in FULL_IMAGE_STABLE_METADATA_KEYS
    }:
        raise GateContractError("legacy/golden full-image stable metadata mismatch")
    if metadata.get("diagnostics") != golden_metadata.get("diagnostics"):
        raise GateContractError(
            "legacy/golden full-image diagnostics mismatch"
        )
    if sidecar.get("metadata_json_sha256") != _sha256_bytes(
        metadata_text.encode("utf-8")
    ):
        raise GateContractError("legacy full-image metadata fingerprint mismatch")
    payload = dict(arrays)
    payload["metadata_json"] = np.asarray(
        metadata_text,
        dtype=FULL_IMAGE_METADATA_DTYPE,
    )
    ordered_payload = {
        name: payload[name] for name in FULL_IMAGE_ARRAY_ORDER
    }
    if sidecar.get("array_fingerprints") != _payload_fingerprints(
        ordered_payload,
        FULL_IMAGE_ARRAY_ORDER,
    ):
        raise GateContractError("legacy full-image array fingerprint mismatch")
    return {
        "npz_path": str(npz),
        "sidecar_path": str(sidecar_path),
        "golden_path": str(FULL_IMAGE_GOLDEN),
        "npz_sha256": expected["npz"],
        "sidecar_sha256": expected["sidecar"],
        "golden_sha256": expected["golden"],
        "scientific_comparison": comparison,
        "metadata": metadata,
        "sidecar": sidecar,
    }


def _validate_full_image_config(config_module: Any) -> dict[str, Any]:
    config = config_module.load_config(FULL_IMAGE_CONFIG)
    payload = config.to_dict()
    if (
        payload.get("case_id") != "LI_FIG3_XZ_K1P0_DX0P25_PRODUCTION"
        or payload.get("background") != {"M": 1.0}
        or payload.get("wave")
        != {
            "kM": 1.0,
            "A_plus": {"real": 0.9, "imag": 1.1},
            "A_cross": {"real": 0.4, "imag": 0.6},
        }
        or payload.get("numerics")
        != {
            "lmax": 180,
            "boundary": {
                "r_in_eps": 1.0e-6,
                "r_out": 300.0,
                "rtol": 1.0e-10,
                "atol": 1.0e-12,
            },
        }
    ):
        raise GateContractError("loaded full-image scientific config mismatch")
    observer = payload.get("observer", {})
    if (
        observer.get("kind") != "xz_plane"
        or observer.get("invalid_radius_policy") != "mask"
        or len(observer.get("x_values", [])) != FULL_IMAGE_RESOLUTION[0]
        or len(observer.get("z_values", [])) != FULL_IMAGE_RESOLUTION[1]
    ):
        raise GateContractError("loaded full-image grid contract mismatch")
    if payload.get("convergence") != {
        "enabled": True,
        "lmax_values": [108, 132, 156, 180],
        "theta_values": [0.0, 0.05, 0.2, 1.0, 2.0, 3.0],
        "phi_values": [0.0, np.pi],
        "selected_threshold": 1.0e-4,
        "near_axis_threshold": 1.0e-3,
    }:
        raise GateContractError("loaded full-image convergence contract mismatch")
    legacy = _audit_legacy_full_image()
    if payload != legacy["metadata"]["config"]:
        raise GateContractError("loaded config/legacy full-image config mismatch")
    return {"object": config, "payload": payload}


def _tablei_input_identity(tablei: Any) -> dict[str, Any]:
    tablei._validate_frozen_scope()
    tablei._validate_start_gate()
    tablei._validate_frozen_package()
    source_paths, source_hashes, gate_paths, gate_hashes = tablei._input_records(
        tablei._DEFAULT_REVIEW_NPZ,
        tablei._DEFAULT_RISK_DIR,
        tablei._DEFAULT_ADAPTIVE_DIR,
        tablei._DEFAULT_T7BZ_EVIDENCE,
        tablei._DEFAULT_T4AA_GATE_DIR,
        tablei._DEFAULT_FURTHER_LOCAL_DIR,
        tablei._DEFAULT_T7CB_EVIDENCE,
        tablei._DEFAULT_LITERAL_FAILED_CHILD_DIR,
        tablei._DEFAULT_T7CD_EVIDENCE,
        tablei._DEFAULT_GATE_DIR,
    )
    return {
        "source_paths": source_paths,
        "source_hashes": source_hashes,
        "gate_paths": gate_paths,
        "gate_hashes": gate_hashes,
        "manifest_sha256": _canonical_sha256(
            {
                "source_hashes": source_hashes,
                "gate_hashes": gate_hashes,
            }
        ),
    }


def _selected_code_hashes() -> dict[str, str]:
    relative_paths = (
        "scripts/phase5_equivalence_preserving_methods_gate.py",
        "src/schwgw/io/config.py",
        "src/schwgw/io/results.py",
        "src/schwgw/io/tablei.py",
        "src/schwgw/io/tablei_another_bounded_local_refinement.py",
        "src/schwgw/numerics/radial_cache.py",
        "src/schwgw/numerics/radial_solver.py",
        "src/schwgw/numerics/q018_tablei_another_bounded_local_envelope.py",
        "src/schwgw/scattering/contracts.py",
        "src/schwgw/scattering/legacy_adapter.py",
        "src/schwgw/scattering/partial_wave.py",
    )
    return {
        relative: _sha256(REPOSITORY_ROOT / relative)
        for relative in relative_paths
    }


def _frequency_generation_contract(
    frozen: Mapping[str, Any],
) -> tuple[dict[str, Any], str, str]:
    tablei = frozen["modules"]["tablei"]
    inputs = frozen["tablei_inputs"]
    generation = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "runner_version": RUNNER_VERSION,
        "frequencies": list(FROZEN_FREQUENCIES),
        "frequency_tokens": {
            str(k): FREQUENCY_TOKENS[k] for k in FROZEN_FREQUENCIES
        },
        "lmax_values": {
            str(k): list(FROZEN_LMAX_VALUES[k]) for k in FROZEN_FREQUENCIES
        },
        "point_ids": list(FROZEN_POINT_IDS),
        "boundary": dict(BOUNDARY_CONTRACT),
        "amplitudes": {
            "A_plus": {"real": 0.9, "imag": 1.1},
            "A_cross": {"real": 0.4, "imag": 0.6},
        },
        "incident_direction": "+z",
        "convergence_tolerance": 1.0e-4,
        "adapter": tablei.ADAPTER_NAME,
        "implementation_commit": frozen["implementation"]["commit"],
        "implementation_manifest_sha256": frozen["implementation"][
            "manifest_sha256"
        ],
        "source_manifest_sha256": frozen["source"]["manifest_sha256"],
        "physics_manifest_sha256": frozen["source"][
            "physics_manifest_sha256"
        ],
        "solver_manifest_sha256": frozen["source"][
            "solver_manifest_sha256"
        ],
        "config_sha256": frozen["config_identity"]["sha256"],
        "gate_manifest_sha256": frozen["gates"]["manifest_sha256"],
        "tablei_input_manifest_sha256": frozen["tablei_inputs"][
            "manifest_sha256"
        ],
        "environment_sha256": frozen["environment"]["environment_sha256"],
        "selected_code_hashes": frozen["selected_code_hashes"],
        "output_root": str(OUTPUT_ROOT),
        "max_workers": 2,
        "worker_threads": 1,
        "baseline_arrays_are_comparison_only": True,
        "diagnostic_failed_child_midpoints_are_run_inputs": False,
        "spin2_physics_implemented_or_validated": False,
    }
    generation_sha256 = _canonical_sha256(generation)
    metadata_contract = {
        "schema_version": tablei.SCHEMA_VERSION,
        "generation_contract_sha256": generation_sha256,
        "units": tablei.UNITS_CONTRACT,
        "dtypes": tablei.DTYPE_CONTRACT,
        "ordering": tablei.ORDERING_CONTRACT,
        "flags": tablei.NON_CLAIM_FLAGS,
        "source_hashes": inputs["source_hashes"],
        "gate_hashes": inputs["gate_hashes"],
        "benchmark_identity_sha256": frozen["identity"].canonical_digest,
    }
    return generation, generation_sha256, _canonical_sha256(metadata_contract)


def _benchmark_identity(
    *,
    implementation: Mapping[str, Any],
    source: Mapping[str, Any],
    gates: Mapping[str, Any],
    config_identity: Mapping[str, Any],
    environment: Mapping[str, Any],
    tablei_inputs: Mapping[str, Any],
) -> BenchmarkIdentity:
    return BenchmarkIdentity(
        implementation_sha256=str(implementation["manifest_sha256"]),
        physics_sha256=str(source["physics_manifest_sha256"]),
        solver_sha256=str(source["solver_manifest_sha256"]),
        config_sha256=str(config_identity["sha256"]),
        source_sha256=str(source["manifest_sha256"]),
        gate_sha256=_canonical_sha256(
            {
                "frozen_gate_manifest_sha256": gates["manifest_sha256"],
                "tablei_input_manifest_sha256": tablei_inputs[
                    "manifest_sha256"
                ],
            }
        ),
        environment_sha256=str(environment["environment_sha256"]),
    )


def _frozen_identity(
    expected_self_sha256: str,
    expected_implementation_commit: str,
) -> dict[str, Any]:
    self_sha256 = _verify_self(expected_self_sha256)
    implementation = _implementation_identity(expected_implementation_commit)
    source = _source_identity(expected_implementation_commit)
    gates = _gate_identity()
    config_identity = _config_identity(expected_implementation_commit)
    environment = _environment_identity()
    modules = _load_runtime_modules()
    loaded_modules = _loaded_module_identity(source)
    selected_code_hashes = _selected_code_hashes()
    tablei_inputs = _tablei_input_identity(modules["tablei"])
    full_image_config = _validate_full_image_config(modules["config"])
    identity = _benchmark_identity(
        implementation=implementation,
        source=source,
        gates=gates,
        config_identity=config_identity,
        environment=environment,
        tablei_inputs=tablei_inputs,
    )
    return {
        "identity": identity,
        "runner": {
            "path": str(Path(__file__).resolve()),
            "version": RUNNER_VERSION,
            "sha256": self_sha256,
        },
        "implementation": implementation,
        "source": source,
        "gates": gates,
        "config_identity": config_identity,
        "environment": environment,
        "modules": modules,
        "loaded_modules": loaded_modules,
        "selected_code_hashes": selected_code_hashes,
        "tablei_inputs": tablei_inputs,
        "full_image_config": full_image_config,
    }


def _identity_payload(frozen: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "benchmark_identity_sha256": frozen["identity"].canonical_digest,
        "benchmark_identity": asdict(frozen["identity"]),
        "runner": frozen["runner"],
        "implementation": frozen["implementation"],
        "source": frozen["source"],
        "gates": frozen["gates"],
        "config": frozen["config_identity"],
        "environment": frozen["environment"],
        "loaded_modules": frozen["loaded_modules"],
        "selected_code_hashes": frozen["selected_code_hashes"],
        "tablei_inputs": frozen["tablei_inputs"],
    }


def _recheck_identity(
    frozen: Mapping[str, Any],
    *,
    phase: str,
) -> dict[str, Any]:
    expected_commit = frozen["implementation"]["commit"]
    self_sha256 = _verify_self(frozen["runner"]["sha256"])
    implementation = _implementation_identity(expected_commit)
    source = _source_identity(expected_commit)
    gates = _gate_identity()
    config = _config_identity(expected_commit)
    environment = _environment_identity()
    loaded = _loaded_module_identity(source)
    selected = _selected_code_hashes()
    tablei_inputs = _tablei_input_identity(frozen["modules"]["tablei"])
    identity = _benchmark_identity(
        implementation=implementation,
        source=source,
        gates=gates,
        config_identity=config,
        environment=environment,
        tablei_inputs=tablei_inputs,
    )
    if (
        implementation != frozen["implementation"]
        or source != frozen["source"]
        or gates != frozen["gates"]
        or config != frozen["config_identity"]
        or environment != frozen["environment"]
        or selected != frozen["selected_code_hashes"]
        or tablei_inputs != frozen["tablei_inputs"]
        or identity != frozen["identity"]
        or loaded["manifest_sha256"]
        != frozen["loaded_modules"]["manifest_sha256"]
    ):
        raise GateContractError(f"frozen identity changed during {phase}")
    return {
        "phase": phase,
        "runner_sha256": self_sha256,
        "implementation_commit": expected_commit,
        "benchmark_identity_sha256": frozen["identity"].canonical_digest,
        "source_manifest_sha256": source["manifest_sha256"],
        "loaded_module_manifest_sha256": loaded["manifest_sha256"],
        "gate_manifest_sha256": gates["manifest_sha256"],
        "tablei_input_manifest_sha256": tablei_inputs["manifest_sha256"],
        "config_sha256": config["sha256"],
        "environment_sha256": environment["environment_sha256"],
    }


@dataclass(frozen=True)
class CaseResources:
    case_id: str
    wall_seconds: float
    user_cpu_seconds: float
    system_cpu_seconds: float
    solve_count: int
    peak_rss_bytes: int

    def __post_init__(self) -> None:
        if not isinstance(self.case_id, str) or not self.case_id:
            raise GateContractError("case_id must be nonempty")
        for label in ("wall_seconds", "user_cpu_seconds", "system_cpu_seconds"):
            value = float(getattr(self, label))
            if not math.isfinite(value) or value < 0.0:
                raise GateContractError(f"{label} must be finite and nonnegative")
        if (
            isinstance(self.solve_count, bool)
            or not isinstance(self.solve_count, int)
            or self.solve_count < 0
        ):
            raise GateContractError("solve_count must be an integer")
        if (
            isinstance(self.peak_rss_bytes, bool)
            or not isinstance(self.peak_rss_bytes, int)
            or self.peak_rss_bytes < 0
        ):
            raise GateContractError("peak RSS must be a nonnegative integer")

    @property
    def cpu_seconds(self) -> float:
        return float(self.user_cpu_seconds + self.system_cpu_seconds)


@dataclass(frozen=True)
class PerformanceResult:
    legacy_solve_count: int
    optimized_solve_count: int
    solve_count_limit: int
    legacy_wall_seconds: float
    optimized_wall_seconds: float
    legacy_cpu_seconds: float
    optimized_cpu_seconds: float
    legacy_peak_rss_bytes: int
    optimized_peak_rss_bytes: int
    solve_count_passed: bool
    wall_passed: bool
    cpu_passed: bool
    each_case_wall_passed: bool
    peak_rss_passed: bool
    passed: bool


def evaluate_performance(
    legacy: Sequence[CaseResources],
    optimized: Sequence[CaseResources],
) -> PerformanceResult:
    """Evaluate all frozen performance gates without relabeling work."""

    if not legacy or not optimized:
        raise GateContractError("performance evidence must contain cases")
    legacy_by_id = {record.case_id: record for record in legacy}
    optimized_by_id = {record.case_id: record for record in optimized}
    if (
        len(legacy_by_id) != len(legacy)
        or len(optimized_by_id) != len(optimized)
        or tuple(legacy_by_id) != tuple(optimized_by_id)
    ):
        raise GateContractError("legacy/optimized case identity or order mismatch")

    legacy_solves = sum(record.solve_count for record in legacy)
    optimized_solves = sum(record.solve_count for record in optimized)
    solve_limit = math.floor(SOLVE_RATIO_LIMIT * legacy_solves)
    legacy_wall = sum(record.wall_seconds for record in legacy)
    optimized_wall = sum(record.wall_seconds for record in optimized)
    legacy_cpu = sum(record.cpu_seconds for record in legacy)
    optimized_cpu = sum(record.cpu_seconds for record in optimized)
    legacy_rss = max((record.peak_rss_bytes for record in legacy), default=0)
    optimized_rss = max((record.peak_rss_bytes for record in optimized), default=0)

    solve_pass = optimized_solves <= solve_limit
    wall_pass = optimized_wall <= WALL_RATIO_LIMIT * legacy_wall
    cpu_pass = optimized_cpu <= CPU_RATIO_LIMIT * legacy_cpu
    per_case_pass = all(
        optimized_by_id[case_id].wall_seconds
        <= CASE_WALL_RATIO_LIMIT * legacy_by_id[case_id].wall_seconds
        for case_id in legacy_by_id
    )
    rss_pass = optimized_rss <= RSS_RATIO_LIMIT * legacy_rss
    return PerformanceResult(
        legacy_solve_count=legacy_solves,
        optimized_solve_count=optimized_solves,
        solve_count_limit=solve_limit,
        legacy_wall_seconds=legacy_wall,
        optimized_wall_seconds=optimized_wall,
        legacy_cpu_seconds=legacy_cpu,
        optimized_cpu_seconds=optimized_cpu,
        legacy_peak_rss_bytes=legacy_rss,
        optimized_peak_rss_bytes=optimized_rss,
        solve_count_passed=solve_pass,
        wall_passed=wall_pass,
        cpu_passed=cpu_pass,
        each_case_wall_passed=per_case_pass,
        peak_rss_passed=rss_pass,
        passed=bool(
            solve_pass and wall_pass and cpu_pass and per_case_pass and rss_pass
        ),
    )


@dataclass(frozen=True)
class WorkUnit(Generic[_Payload]):
    key: tuple[Any, ...]
    payload: _Payload

    def __post_init__(self) -> None:
        if not isinstance(self.key, tuple) or not self.key:
            raise GateContractError("work-unit key must be a nonempty tuple")
        _canonical_json(self.key)
        _canonical_json(self.payload)


@dataclass(frozen=True)
class WorkResult(Generic[_ResultPayload]):
    key: tuple[Any, ...]
    payload: _ResultPayload
    reused: bool = False


def _ordered_units(
    units: Iterable[WorkUnit[_Payload]],
) -> tuple[WorkUnit[_Payload], ...]:
    materialized = tuple(units)
    digests = [_canonical_json(unit.key) for unit in materialized]
    if len(set(digests)) != len(digests):
        raise GateContractError("work-unit keys must be unique")
    return tuple(
        sorted(
            materialized,
            key=lambda unit: _scientific_sort_key(unit.key),
        )
    )


def execute_deterministically(
    units: Iterable[WorkUnit[_Payload]],
    worker: Callable[[WorkUnit[_Payload]], _ResultPayload],
    *,
    max_workers: int,
) -> tuple[WorkResult[_ResultPayload], ...]:
    """Execute with at most two workers and return stable scientific order."""

    if isinstance(max_workers, bool) or max_workers not in (1, 2):
        raise GateContractError("deterministic executor permits at most two workers")
    ordered = _ordered_units(units)
    if max_workers == 1:
        payloads = tuple(worker(unit) for unit in ordered)
    else:
        with ThreadPoolExecutor(max_workers=2) as executor:
            payloads = tuple(executor.map(worker, ordered))
    return tuple(
        WorkResult(key=unit.key, payload=payload, reused=False)
        for unit, payload in zip(ordered, payloads, strict=True)
    )


class AtomicCheckpointStore:
    """Content-addressed complete-work-unit JSON store with quarantine."""

    def __init__(self, root: str | Path, identity: BenchmarkIdentity) -> None:
        self.root = Path(root)
        self.identity = identity
        self.checkpoint_dir = self.root / "checkpoint"
        self.quarantine_dir = self.root / "quarantine"

    def checkpoint_path(self, key: tuple[Any, ...]) -> Path:
        if not isinstance(key, tuple) or not key:
            raise GateContractError("checkpoint key must be a nonempty tuple")
        token = _canonical_sha256(key)
        return self.checkpoint_dir / f"{token}.json"

    def temporary_paths(self, key: tuple[Any, ...]) -> tuple[Path, ...]:
        path = self.checkpoint_path(key)
        if not path.parent.exists():
            return ()
        return tuple(
            sorted(
                path.parent.glob(f"{path.name}.tmp.*"),
                key=lambda candidate: candidate.name,
            )
        )

    def _quarantine(self, path: Path, reason: str) -> None:
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        reason_token = re.sub(r"[^a-z0-9_]+", "_", reason.lower()).strip("_")
        destination = self.quarantine_dir / (
            f"{path.name}.{reason_token}.{os.getpid()}"
        )
        serial = 0
        while destination.exists():
            serial += 1
            destination = self.quarantine_dir / (
                f"{path.name}.{reason_token}.{os.getpid()}.{serial}"
            )
        os.replace(path, destination)
        _fsync_directory(self.quarantine_dir)
        _fsync_directory(path.parent)

    def write_complete(
        self,
        key: tuple[Any, ...],
        payload: Mapping[str, Any],
    ) -> Path:
        payload_copy = dict(payload)
        record = {
            "schema_version": WORK_UNIT_SCHEMA_VERSION,
            "state": "complete",
            "identity_sha256": self.identity.canonical_digest,
            "key": _json_safe(key),
            "payload": _json_safe(payload_copy),
            "payload_sha256": _canonical_sha256(payload_copy),
        }
        path = self.checkpoint_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(
            path.name + f".tmp.{os.getpid()}.{time.time_ns()}"
        )
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o644,
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(_canonical_json(record))
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            _commit_no_overwrite(temporary, path)
        except BaseException:
            if temporary.exists():
                temporary.unlink()
            raise
        return path

    def load_complete(
        self,
        key: tuple[Any, ...],
    ) -> dict[str, Any] | None:
        path = self.checkpoint_path(key)
        temporary = self.temporary_paths(key)
        for partial in temporary:
            self._quarantine(partial, "interrupted")
        if not path.is_file():
            return None
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError:
            self._quarantine(path, "unreadable")
            return None
        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            reason = "truncated" if raw.lstrip().startswith("{") else "corrupt"
            self._quarantine(path, reason)
            return None
        if not isinstance(record, dict):
            self._quarantine(path, "corrupt")
            return None
        expected_keys = {
            "schema_version",
            "state",
            "identity_sha256",
            "key",
            "payload",
            "payload_sha256",
        }
        if set(record) != expected_keys:
            self._quarantine(path, "corrupt")
            return None
        if record.get("schema_version") != WORK_UNIT_SCHEMA_VERSION:
            self._quarantine(path, "stale_schema")
            return None
        if record.get("state") != "complete":
            self._quarantine(path, "interrupted")
            return None
        if record.get("identity_sha256") != self.identity.canonical_digest:
            self._quarantine(path, "identity_mismatch")
            return None
        if record.get("key") != _json_safe(key):
            self._quarantine(path, "key_mismatch")
            return None
        payload = record.get("payload")
        if not isinstance(payload, dict):
            self._quarantine(path, "corrupt")
            return None
        try:
            payload_sha256 = _canonical_sha256(payload)
        except GateContractError:
            self._quarantine(path, "corrupt")
            return None
        if record.get("payload_sha256") != payload_sha256:
            self._quarantine(path, "corrupt")
            return None
        return dict(payload)


@dataclass(frozen=True)
class ArtifactPaths:
    case_id: str
    directory: Path
    npz: Path
    sidecar: Path
    lock: Path
    quarantine: Path


def _artifact_paths(case_kind: str, frequency: float | None) -> ArtifactPaths:
    if case_kind == "frequency":
        if frequency not in FREQUENCY_TOKENS:
            raise GateContractError("frequency is outside the frozen matrix")
        token = FREQUENCY_TOKENS[float(frequency)]
        directory = OUTPUT_ROOT / "frequencies"
        npz = directory / f"kM_{token}.npz"
        case_id = f"frequency:{token}"
    elif case_kind == "full-image":
        if frequency is not None:
            raise GateContractError("full-image case accepts no frequency")
        directory = OUTPUT_ROOT / "full_image"
        npz = directory / FULL_IMAGE_FILENAME
        case_id = "full-image:241x241"
    else:
        raise GateContractError(f"unsupported artifact case: {case_kind}")
    return ArtifactPaths(
        case_id=case_id,
        directory=directory,
        npz=npz,
        sidecar=npz.with_name(npz.name + ".json"),
        lock=directory / f".{npz.name}.lock",
        quarantine=directory / "quarantine",
    )


def _temporary_paths(paths: ArtifactPaths) -> tuple[Path, ...]:
    if not paths.directory.exists():
        return ()
    return tuple(
        sorted(
            (
                *paths.directory.glob(f"{paths.npz.name}.tmp.*"),
                *paths.directory.glob(f"{paths.sidecar.name}.tmp.*"),
            ),
            key=lambda path: path.name,
        )
    )


def _quarantine_records(paths: ArtifactPaths) -> tuple[Path, ...]:
    if not paths.quarantine.exists():
        return ()
    return tuple(
        sorted(
            (
                path
                for path in paths.quarantine.rglob("*")
                if path.is_file()
            ),
            key=lambda path: str(path),
        )
    )


def _process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _lock_record(paths: ArtifactPaths) -> dict[str, Any] | None:
    if not paths.lock.exists():
        return None
    payload = _read_json(paths.lock)
    expected = {
        "schema_version",
        "pid",
        "case_id",
        "identity_sha256",
        "runner_sha256",
        "implementation_commit",
        "command",
        "created_unix_ns",
    }
    if (
        set(payload) != expected
        or payload.get("schema_version") != "t4ae_optimized_lock_v1"
        or payload.get("case_id") != paths.case_id
    ):
        raise GateContractError(f"lock schema mismatch: {paths.lock}")
    pid = payload.get("pid")
    if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
        raise GateContractError(f"lock PID is invalid: {paths.lock}")
    return {
        "path": str(paths.lock),
        "payload": payload,
        "owner_process_exists": _process_exists(pid),
    }


def _validate_resume_lock_identity(
    payload: Mapping[str, Any],
    *,
    frozen: Mapping[str, Any],
    paths: ArtifactPaths,
    command: Sequence[str],
) -> None:
    expected = {
        "case_id": paths.case_id,
        "identity_sha256": frozen["identity"].canonical_digest,
        "runner_sha256": frozen["runner"]["sha256"],
        "implementation_commit": frozen["implementation"]["commit"],
        "command": list(command),
    }
    mismatched = {
        name: {
            "expected": value,
            "actual": payload.get(name),
        }
        for name, value in expected.items()
        if payload.get(name) != value
    }
    if mismatched:
        raise GateContractError(
            "stale resume lock identity mismatch: "
            + _canonical_json(mismatched)
        )


def _global_quarantine_records() -> tuple[Path, ...]:
    if not GLOBAL_QUARANTINE_ROOT.exists():
        return ()
    return tuple(
        sorted(
            (
                path
                for path in GLOBAL_QUARANTINE_ROOT.rglob("*")
                if path.is_file()
            ),
            key=lambda path: str(path),
        )
    )


def _global_lock_record() -> dict[str, Any] | None:
    if not GLOBAL_RUNNER_LOCK.exists():
        return None
    payload = _read_json(GLOBAL_RUNNER_LOCK)
    expected = {
        "schema_version",
        "pid",
        "case_id",
        "identity_sha256",
        "runner_sha256",
        "implementation_commit",
        "command",
        "created_unix_ns",
    }
    if (
        set(payload) != expected
        or payload.get("schema_version")
        != "t4ae_optimized_global_lock_v1"
    ):
        raise GateContractError(
            f"global runner lock schema mismatch: {GLOBAL_RUNNER_LOCK}"
        )
    pid = payload.get("pid")
    if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
        raise GateContractError(
            f"global runner lock PID is invalid: {GLOBAL_RUNNER_LOCK}"
        )
    return {
        "path": str(GLOBAL_RUNNER_LOCK),
        "payload": payload,
        "owner_process_exists": _process_exists(pid),
    }


def _quarantine_stale_global_lock(
    lock: Mapping[str, Any],
    *,
    runner_sha256: str,
) -> None:
    if lock.get("owner_process_exists") is not False:
        raise GateContractError("only an absent-owner global lock may be quarantined")
    GLOBAL_QUARANTINE_ROOT.mkdir(parents=True, exist_ok=True)
    destination = GLOBAL_QUARANTINE_ROOT / (
        f"{time.time_ns()}-pid{os.getpid()}-{runner_sha256[:12]}"
    )
    destination.mkdir(parents=False, exist_ok=False)
    moved_lock = destination / GLOBAL_RUNNER_LOCK.name
    os.replace(GLOBAL_RUNNER_LOCK, moved_lock)
    reason = {
        "schema_version": "t4ae_optimized_global_quarantine_v1",
        "reason": "stale global runner lock with absent owner",
        "runner_sha256": runner_sha256,
        "moved": {
            "from": str(GLOBAL_RUNNER_LOCK),
            "to": str(moved_lock),
        },
        "stale_lock": lock.get("payload"),
    }
    reason_path = destination / "reason.json"
    descriptor = os.open(
        reason_path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o644,
    )
    with os.fdopen(descriptor, "wb") as handle:
        handle.write((_canonical_json(reason) + "\n").encode("utf-8"))
        handle.flush()
        os.fsync(handle.fileno())
    _fsync_directory(destination)
    _fsync_directory(GLOBAL_QUARANTINE_ROOT)
    _fsync_directory(OUTPUT_ROOT)


def _acquire_global_lock(
    frozen: Mapping[str, Any],
    *,
    case_id: str,
    command: Sequence[str],
) -> dict[str, Any]:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    if _global_quarantine_records():
        raise GateContractError(
            "global runner quarantine requires anomaly review"
        )
    existing = _global_lock_record()
    if existing is not None:
        if existing["owner_process_exists"]:
            raise GateContractError("refusing a second live optimized runner")
        _quarantine_stale_global_lock(
            existing,
            runner_sha256=frozen["runner"]["sha256"],
        )
        raise GateContractError(
            "stale global runner lock was quarantined; anomaly review is required"
        )
    payload = {
        "schema_version": "t4ae_optimized_global_lock_v1",
        "pid": os.getpid(),
        "case_id": case_id,
        "identity_sha256": frozen["identity"].canonical_digest,
        "runner_sha256": frozen["runner"]["sha256"],
        "implementation_commit": frozen["implementation"]["commit"],
        "command": list(command),
        "created_unix_ns": time.time_ns(),
    }
    try:
        descriptor = os.open(
            GLOBAL_RUNNER_LOCK,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o644,
        )
    except FileExistsError as exc:
        raise GateContractError(
            "refusing a concurrent optimized runner"
        ) from exc
    with os.fdopen(descriptor, "wb") as handle:
        handle.write((_canonical_json(payload) + "\n").encode("utf-8"))
        handle.flush()
        os.fsync(handle.fileno())
    _fsync_directory(OUTPUT_ROOT)
    return payload


def _release_global_lock(owned_lock: Mapping[str, Any]) -> None:
    if not GLOBAL_RUNNER_LOCK.exists():
        raise GateContractError("owned global runner lock disappeared")
    current = _read_json(GLOBAL_RUNNER_LOCK)
    if current != dict(owned_lock):
        raise GateContractError("owned global runner lock identity changed")
    GLOBAL_RUNNER_LOCK.unlink()
    _fsync_directory(OUTPUT_ROOT)


def _require_global_idle() -> dict[str, Any]:
    lock = _global_lock_record()
    quarantined = _global_quarantine_records()
    if lock is not None or quarantined:
        raise GateContractError(
            "optimized runner global state is not idle: "
            + _canonical_json(
                {
                    "lock": lock,
                    "quarantined": [str(path) for path in quarantined],
                }
            )
        )
    return {
        "state": "idle",
        "lock": None,
        "quarantined": [],
    }


def _artifact_state(
    paths: ArtifactPaths,
    *,
    allow_owned_lock: bool = False,
    owned_lock: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    lock = _lock_record(paths)
    if lock is not None:
        lock_is_owned = (
            allow_owned_lock
            and owned_lock is not None
            and lock["payload"] == dict(owned_lock)
        )
        if not lock_is_owned:
            return {
                "state": "locked",
                "lock": lock,
                "temporary": [
                    str(path) for path in _temporary_paths(paths)
                ],
                "quarantined": [
                    str(path) for path in _quarantine_records(paths)
                ],
            }
    temporary = _temporary_paths(paths)
    quarantined = _quarantine_records(paths)
    npz_exists = paths.npz.exists()
    sidecar_exists = paths.sidecar.exists()
    if quarantined:
        state = "quarantined"
    elif temporary:
        state = "partial"
    elif npz_exists and sidecar_exists:
        state = "complete_pair"
    elif npz_exists or sidecar_exists:
        state = "partial"
    else:
        state = "absent"
    return {
        "state": state,
        "npz": npz_exists,
        "sidecar": sidecar_exists,
        "lock": lock,
        "temporary": [str(path) for path in temporary],
        "quarantined": [str(path) for path in quarantined],
    }


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(
        path,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
    )
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _commit_no_overwrite(temporary: Path, target: Path) -> None:
    if target.exists():
        raise GateContractError(f"refusing to overwrite artifact: {target}")
    try:
        os.link(temporary, target)
    except FileExistsError as exc:
        raise GateContractError(
            f"atomic target appeared concurrently: {target}"
        ) from exc
    _fsync_directory(target.parent)
    temporary.unlink()
    _fsync_directory(target.parent)


def _atomic_npz(
    target: Path,
    payload: Mapping[str, np.ndarray],
    *,
    transaction_id: str,
) -> None:
    temporary = target.with_name(
        f"{target.name}.tmp.{os.getpid()}.{transaction_id}"
    )
    descriptor = os.open(
        temporary,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o644,
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            np.savez(handle, **payload)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        if temporary.exists():
            temporary.unlink()
        raise
    _commit_no_overwrite(temporary, target)


def _atomic_json(
    target: Path,
    payload: Mapping[str, Any],
    *,
    transaction_id: str,
) -> None:
    temporary = target.with_name(
        f"{target.name}.tmp.{os.getpid()}.{transaction_id}"
    )
    encoded = (_canonical_json(payload) + "\n").encode("utf-8")
    descriptor = os.open(
        temporary,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o644,
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        if temporary.exists():
            temporary.unlink()
        raise
    _commit_no_overwrite(temporary, target)


def _acquire_lock(
    paths: ArtifactPaths,
    frozen: Mapping[str, Any],
    command: Sequence[str],
) -> dict[str, Any]:
    paths.directory.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "t4ae_optimized_lock_v1",
        "pid": os.getpid(),
        "case_id": paths.case_id,
        "identity_sha256": frozen["identity"].canonical_digest,
        "runner_sha256": frozen["runner"]["sha256"],
        "implementation_commit": frozen["implementation"]["commit"],
        "command": list(command),
        "created_unix_ns": time.time_ns(),
    }
    try:
        descriptor = os.open(
            paths.lock,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o644,
        )
    except FileExistsError as exc:
        raise GateContractError(
            "refusing a second runner because the case lock exists"
        ) from exc
    with os.fdopen(descriptor, "wb") as handle:
        handle.write((_canonical_json(payload) + "\n").encode("utf-8"))
        handle.flush()
        os.fsync(handle.fileno())
    _fsync_directory(paths.directory)
    return payload


def _release_lock(
    paths: ArtifactPaths,
    owned_lock: Mapping[str, Any],
) -> None:
    if not paths.lock.exists():
        raise GateContractError("owned lock disappeared before release")
    current = _read_json(paths.lock)
    if current != dict(owned_lock):
        raise GateContractError("owned lock identity changed before release")
    paths.lock.unlink()
    _fsync_directory(paths.directory)


def _quarantine_artifacts(
    paths: ArtifactPaths,
    *,
    reason: str,
    runner_sha256: str,
    include_lock: bool = False,
) -> None:
    candidates = [
        path
        for path in (
            paths.npz,
            paths.sidecar,
            *_temporary_paths(paths),
            *((paths.lock,) if include_lock else ()),
        )
        if path.exists()
    ]
    if not candidates:
        return
    destination = paths.quarantine / (
        f"{time.time_ns()}-pid{os.getpid()}-{runner_sha256[:12]}"
    )
    destination.mkdir(parents=True, exist_ok=False)
    moved = []
    for path in candidates:
        target = destination / path.name
        os.replace(path, target)
        moved.append({"from": str(path), "to": str(target)})
    reason_record = {
        "schema_version": "t4ae_optimized_quarantine_v1",
        "case_id": paths.case_id,
        "reason": reason,
        "runner_sha256": runner_sha256,
        "moved": moved,
    }
    reason_path = destination / "reason.json"
    descriptor = os.open(
        reason_path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o644,
    )
    with os.fdopen(descriptor, "wb") as handle:
        handle.write((_canonical_json(reason_record) + "\n").encode("utf-8"))
        handle.flush()
        os.fsync(handle.fileno())
    _fsync_directory(destination)
    _fsync_directory(paths.quarantine)
    _fsync_directory(paths.directory)


def execute_with_resume(
    units: Iterable[WorkUnit[_Payload]],
    worker: Callable[[WorkUnit[_Payload]], Mapping[str, Any]],
    *,
    checkpoint_store: AtomicCheckpointStore,
    max_workers: int,
) -> tuple[WorkResult[dict[str, Any]], ...]:
    """Reuse every complete matching unit and execute only absent units."""

    ordered = _ordered_units(units)
    reused: dict[str, WorkResult[dict[str, Any]]] = {}
    missing: list[WorkUnit[_Payload]] = []
    for unit in ordered:
        digest = _canonical_json(unit.key)
        payload = checkpoint_store.load_complete(unit.key)
        if payload is None:
            missing.append(unit)
        else:
            reused[digest] = WorkResult(unit.key, payload, reused=True)

    computed = execute_deterministically(missing, worker, max_workers=max_workers)
    computed_by_key: dict[str, WorkResult[dict[str, Any]]] = {}
    for result in computed:
        if not isinstance(result.payload, Mapping):
            raise GateContractError("resumable worker result must be a mapping")
        payload = dict(result.payload)
        checkpoint_store.write_complete(result.key, payload)
        checked = checkpoint_store.load_complete(result.key)
        if checked != payload:
            raise GateContractError("fresh checkpoint failed independent reload")
        computed_by_key[_canonical_json(result.key)] = WorkResult(
            result.key,
            payload,
            reused=False,
        )
    return tuple(
        reused.get(_canonical_json(unit.key))
        or computed_by_key[_canonical_json(unit.key)]
        for unit in ordered
    )


def _profile_top(
    profile: cProfile.Profile,
    *,
    count: int = 50,
) -> list[dict[str, Any]]:
    stats = pstats.Stats(profile)
    ordered = sorted(
        stats.stats.items(),
        key=lambda item: item[1][3],
        reverse=True,
    )
    rows = []
    for (filename, line, function), values in ordered[:count]:
        primitive_calls, calls, total, cumulative, _ = values
        rows.append(
            {
                "file": filename,
                "line": line,
                "function": function,
                "primitive_calls": primitive_calls,
                "calls": calls,
                "total_seconds": total,
                "cumulative_seconds": cumulative,
            }
        )
    return rows


def _warning_source(filename: str) -> str:
    normalized = str(Path(filename))
    if "/site-packages/" in normalized:
        return normalized.split("/site-packages/", 1)[1]
    if "/src/" in normalized:
        return "src/" + normalized.split("/src/", 1)[1]
    return normalized


def _raw_warning_record(
    caught: Sequence[warnings.WarningMessage],
) -> dict[str, Any]:
    counts: Counter[tuple[str, int, str]] = Counter()
    rejected: Counter[tuple[str, str, int, str]] = Counter()
    for item in caught:
        source = _warning_source(item.filename)
        key = (source, int(item.lineno), str(item.message))
        counts[key] += 1
        if (
            item.category is not RuntimeWarning
            or key not in _ALLOWED_RAW_RUNTIME_WARNINGS
        ):
            rejected[
                (
                    item.category.__name__,
                    source,
                    int(item.lineno),
                    str(item.message),
                )
            ] += 1
    if rejected:
        raise GateContractError(
            "unrecognized runtime warning(s): "
            + _canonical_json(
                [
                    {
                        "category": category,
                        "source": source,
                        "line": line,
                        "message": message,
                        "count": count,
                    }
                    for (
                        category,
                        source,
                        line,
                        message,
                    ), count in sorted(rejected.items())
                ]
            )
        )
    entries = [
        {
            "category": "RuntimeWarning",
            "source": source,
            "line": line,
            "message": message,
            "count": count,
        }
        for (source, line, message), count in sorted(counts.items())
    ]
    return {
        "policy": RAW_WARNING_SCHEMA,
        "total_count": int(sum(counts.values())),
        "entries": entries,
        "all_recognized": True,
    }


def _warning_signature(record: Mapping[str, Any]) -> tuple[tuple[Any, ...], ...]:
    expected_record_keys = {
        "policy",
        "total_count",
        "entries",
        "all_recognized",
    }
    if not isinstance(record, Mapping) or set(record) != expected_record_keys:
        raise GateContractError("raw warning record schema mismatch")
    if record.get("policy") != RAW_WARNING_SCHEMA:
        raise GateContractError("raw warning policy mismatch")
    if record.get("all_recognized") is not True:
        raise GateContractError("raw warning classification mismatch")
    total_count = record.get("total_count")
    if (
        isinstance(total_count, bool)
        or not isinstance(total_count, int)
        or total_count < 0
    ):
        raise GateContractError("raw warning total_count must be an integer")
    entries = record.get("entries")
    if not isinstance(entries, list):
        raise GateContractError("raw warning entries must be a list")

    expected_entry_keys = {
        "category",
        "source",
        "line",
        "message",
        "count",
    }
    signature: list[tuple[str, str, int, str, int]] = []
    for entry in entries:
        if not isinstance(entry, Mapping) or set(entry) != expected_entry_keys:
            raise GateContractError("raw warning entry schema mismatch")
        category = entry.get("category")
        source = entry.get("source")
        line = entry.get("line")
        message = entry.get("message")
        count = entry.get("count")
        if category != "RuntimeWarning":
            raise GateContractError("raw warning category mismatch")
        if not isinstance(source, str) or not source:
            raise GateContractError("raw warning source must be nonempty")
        if isinstance(line, bool) or not isinstance(line, int) or line <= 0:
            raise GateContractError("raw warning line must be a positive integer")
        if not isinstance(message, str) or not message:
            raise GateContractError("raw warning message must be nonempty")
        if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            raise GateContractError("raw warning count must be a positive integer")
        signature.append((category, source, line, message, count))

    result = tuple(signature)
    if len(set(result)) != len(result):
        raise GateContractError("raw warning entries must be unique")
    if result != tuple(
        sorted(
            result,
            key=lambda item: (item[1], item[2], item[3], item[0], item[4]),
        )
    ):
        raise GateContractError("raw warning entries are out of canonical order")
    if total_count != sum(item[4] for item in result):
        raise GateContractError("raw warning total_count does not match entries")
    return result


def _compare_warning_records(
    candidate: Mapping[str, Any],
    legacy: Mapping[str, Any],
) -> None:
    candidate_signature = _warning_signature(candidate)
    legacy_signature = _warning_signature(legacy)
    if (
        candidate["total_count"] != legacy["total_count"]
        or candidate_signature != legacy_signature
    ):
        raise GateContractError(
            "optimized/legacy raw warning policy, tuple, or count mismatch"
        )


def _validate_frequency_structured_warning_record(
    record: Mapping[str, Any],
) -> dict[str, Any]:
    expected_keys = {"codes", "total_count", "oracle_adapter_use_count"}
    if not isinstance(record, Mapping) or set(record) != expected_keys:
        raise GateContractError("frequency structured warning schema mismatch")
    codes = record.get("codes")
    if (
        not isinstance(codes, list)
        or any(not isinstance(code, str) or not code for code in codes)
        or codes != sorted(set(codes))
    ):
        raise GateContractError("frequency structured warning codes mismatch")
    total_count = record.get("total_count")
    adapter_count = record.get("oracle_adapter_use_count")
    for label, value in (
        ("total_count", total_count),
        ("oracle_adapter_use_count", adapter_count),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise GateContractError(
                f"frequency structured warning {label} must be an integer"
            )
    if adapter_count > total_count:
        raise GateContractError(
            "frequency structured oracle count exceeds warning count"
        )
    return {
        "codes": list(codes),
        "total_count": total_count,
        "oracle_adapter_use_count": adapter_count,
    }


def _validate_frequency_embedded_metadata(
    frozen: Mapping[str, Any],
    *,
    token: str,
    arrays: Mapping[str, np.ndarray],
    metadata: Mapping[str, Any],
    benchmark: Mapping[str, Any],
) -> None:
    if (
        not isinstance(metadata, Mapping)
        or set(metadata) != FREQUENCY_EMBEDDED_METADATA_KEYS
    ):
        raise GateContractError(
            "optimized frequency embedded metadata schema mismatch"
        )
    try:
        frequency = next(
            value
            for value, candidate in FREQUENCY_TOKENS.items()
            if candidate == token
        )
    except StopIteration as exc:
        raise GateContractError(
            "optimized frequency embedded token mismatch"
        ) from exc
    tablei = frozen["modules"]["tablei"]
    inputs = frozen["tablei_inputs"]
    _, generation_sha256, metadata_sha256 = _frequency_generation_contract(
        frozen
    )
    expected_methods = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "runner_sha256": frozen["runner"]["sha256"],
        "implementation_commit": frozen["implementation"]["commit"],
        "benchmark_identity_sha256": frozen["identity"].canonical_digest,
        "generation_contract_sha256": generation_sha256,
        "source_command": benchmark["source_command"],
        "non_claims": benchmark["non_claims"],
    }
    expected_exact = {
        "schema_version": tablei.SCHEMA_VERSION,
        "complete": True,
        "kM": frequency,
        "frequency_token": token,
        "point_ids": list(FROZEN_POINT_IDS),
        "lmax_values": list(FROZEN_LMAX_VALUES[frequency]),
        "final_lmax_pair": list(FROZEN_LMAX_VALUES[frequency][-2:]),
        "adapter": tablei.ADAPTER_NAME,
        "generation_contract_hash": generation_sha256,
        "metadata_contract_hash": metadata_sha256,
        "source_paths": inputs["source_paths"],
        "source_hashes": inputs["source_hashes"],
        "gate_paths": inputs["gate_paths"],
        "gate_hashes": inputs["gate_hashes"],
        "implementation": frozen["implementation"],
        "selected_code_hashes": frozen["selected_code_hashes"],
        "units": tablei.UNITS_CONTRACT,
        "dtypes": tablei.DTYPE_CONTRACT,
        "ordering": tablei.ORDERING_CONTRACT,
        "flags": tablei.NON_CLAIM_FLAGS,
        "t4ae_optimized_methods": expected_methods,
    }
    for name, expected in expected_exact.items():
        if metadata.get(name) != expected:
            raise GateContractError(
                f"optimized frequency embedded provenance mismatch: {name}"
            )
    if (
        isinstance(metadata["kM"], bool)
        or not isinstance(metadata["kM"], (int, float))
        or metadata["complete"] is not True
    ):
        raise GateContractError(
            "optimized frequency embedded scalar identity mismatch"
        )

    runtime = metadata["runtime_seconds"]
    if (
        isinstance(runtime, bool)
        or not isinstance(runtime, (int, float))
        or not math.isfinite(float(runtime))
        or float(runtime) < 0.0
    ):
        raise GateContractError(
            "optimized frequency embedded runtime mismatch"
        )
    for name in (
        "radial_solve_count",
        "radial_reuse_count",
        "radial_warning_count",
        "adapter_use_count",
    ):
        value = metadata[name]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise GateContractError(
                f"optimized frequency embedded count mismatch: {name}"
            )

    warning_record = _validate_frequency_structured_warning_record(
        benchmark["structured_warning_record"]
    )
    if (
        metadata["radial_warning_codes"] != warning_record["codes"]
        or metadata["radial_warning_count"]
        != warning_record["total_count"]
        or metadata["adapter_use_count"]
        != warning_record["oracle_adapter_use_count"]
    ):
        raise GateContractError(
            "optimized frequency embedded warning/count mismatch"
        )

    expected_fingerprints = {
        name: _legacy_frequency_fingerprint(value)
        for name, value in arrays.items()
    }
    if metadata["array_fingerprints"] != expected_fingerprints:
        raise GateContractError(
            "optimized frequency embedded array fingerprint mismatch"
        )
    for polarization in ("plus", "cross"):
        field = f"final_pair_delta_{polarization}"
        value = np.asarray(arrays[field], dtype=np.float64)
        if value.size == 0 or not np.all(np.isfinite(value)):
            raise GateContractError(
                "optimized frequency embedded final-pair array mismatch"
            )
        expected_maximum = float(np.max(value))
        recorded_maximum = metadata[f"max_final_pair_delta_{polarization}"]
        if (
            isinstance(recorded_maximum, bool)
            or not isinstance(recorded_maximum, (int, float))
            or not math.isfinite(float(recorded_maximum))
            or float(recorded_maximum) != expected_maximum
        ):
            raise GateContractError(
                "optimized frequency embedded final-pair maximum mismatch: "
                f"{polarization}"
            )


def _validate_empty_full_image_warning_records(
    raw_record: Mapping[str, Any],
    structured_record: Mapping[str, Any],
) -> None:
    if _warning_signature(raw_record) or raw_record["total_count"] != 0:
        raise GateContractError("optimized full-image raw warning audit mismatch")
    expected_structured = {
        "policy": "exact_empty_full_image_record",
        "total_count": 0,
        "entries": [],
    }
    if (
        not isinstance(structured_record, Mapping)
        or set(structured_record) != set(expected_structured)
        or structured_record.get("policy") != expected_structured["policy"]
        or isinstance(structured_record.get("total_count"), bool)
        or structured_record.get("total_count") != 0
        or not isinstance(structured_record.get("total_count"), int)
        or structured_record.get("entries") != []
        or not isinstance(structured_record.get("entries"), list)
    ):
        raise GateContractError(
            "optimized full-image structured warning audit mismatch"
        )


def _diagnostic_warning_entries(solution: Any) -> tuple[dict[str, Any], ...]:
    diagnostics = getattr(solution, "diagnostics", None)
    entries = []
    for warning in getattr(diagnostics, "warnings", ()) or ():
        if hasattr(warning, "to_metadata"):
            payload = warning.to_metadata()
        elif isinstance(warning, Mapping):
            payload = dict(warning)
        else:
            payload = {"code": str(warning)}
        entries.append(_json_safe(payload))
    return tuple(entries)


def _solution_metrics(solution: Any) -> dict[str, Any]:
    diagnostics = getattr(solution, "diagnostics", None)
    solver_name = str(getattr(diagnostics, "solver", "unknown"))
    warning_entries = _diagnostic_warning_entries(solution)
    oracle = "oracle" in solver_name.lower() or any(
        "oracle_used" in str(entry.get("code", ""))
        for entry in warning_entries
    )
    residuals = {}
    for name in (
        "boundary_residual",
        "wronskian_residual",
        "effective_wronskian_residual",
        "raw_wronskian_residual",
        "flux_residual",
        "match_condition_number",
    ):
        value = getattr(diagnostics, name, None)
        if isinstance(value, (int, float, np.generic)):
            numeric = float(value)
            if not math.isfinite(numeric):
                raise GateContractError(
                    f"nonfinite radial diagnostic metric: {name}"
                )
            residuals[name] = numeric
    return {
        "solver": solver_name,
        "oracle": oracle,
        "warning_entries": list(warning_entries),
        "residuals": residuals,
    }


def _new_stage_profile() -> dict[str, Any]:
    return {
        "radial": {
            "calls": 0,
            "wall_seconds": 0.0,
            "cpu_seconds": 0.0,
        },
        "polarization": {
            "calls": 0,
            "wall_seconds": 0.0,
            "cpu_seconds": 0.0,
        },
        "flat": {
            "calls": 0,
            "wall_seconds": 0.0,
            "cpu_seconds": 0.0,
        },
    }


def _resource_record(
    *,
    wall_seconds: float,
    usage_start: resource.struct_rusage,
    usage_end: resource.struct_rusage,
) -> dict[str, Any]:
    user = usage_end.ru_utime - usage_start.ru_utime
    system = usage_end.ru_stime - usage_start.ru_stime
    return {
        "wall_seconds": wall_seconds,
        "user_cpu_seconds": user,
        "system_cpu_seconds": system,
        "cpu_seconds": user + system,
        "peak_rss": usage_end.ru_maxrss,
        "peak_rss_unit": "bytes_on_macos",
        "minor_faults": usage_end.ru_minflt - usage_start.ru_minflt,
        "major_faults": usage_end.ru_majflt - usage_start.ru_majflt,
    }


def _compare_frequency_result(
    order: Sequence[str],
    arrays: Mapping[str, np.ndarray],
    metadata: Mapping[str, Any],
    reference: Mapping[str, Any],
) -> dict[str, Any]:
    reference_order, reference_arrays, reference_metadata, _ = _read_npz(
        Path(reference["npz_path"])
    )
    scientific_order = tuple(name for name in order if name != "metadata_json")
    reference_scientific_order = tuple(
        name for name in reference_order if name != "metadata_json"
    )
    comparison = _scientific_array_comparison(
        scientific_order,
        arrays,
        reference_scientific_order,
        reference_arrays,
        exact_names=FREQUENCY_EXACT_ARRAY_NAMES,
    )
    for name in FREQUENCY_STABLE_METADATA_KEYS:
        if metadata.get(name) != reference_metadata.get(name):
            raise GateContractError(
                f"frequency stable metadata mismatch: {name}"
            )
    for name in ("plus", "cross"):
        field = f"final_pair_delta_{name}"
        actual_delta = np.asarray(arrays[field], dtype=np.float64)
        reference_delta = np.asarray(
            reference_arrays[field],
            dtype=np.float64,
        )
        if float(np.max(actual_delta)) > 1.0e-4:
            raise GateContractError(f"final adjacent-lmax gate failed: {name}")
        delta_difference = float(
            np.max(np.abs(actual_delta - reference_delta))
        )
        if delta_difference > 1.0e-10:
            raise GateContractError(
                f"legacy/optimized final-pair delta mismatch: {name}"
            )
        comparison[f"max_final_pair_delta_{name}"] = float(
            np.max(actual_delta)
        )
        comparison[f"max_final_pair_delta_difference_{name}"] = (
            delta_difference
        )
    if not np.array_equal(
        arrays["F_plus_history"][-1],
        arrays["F_plus_complex"],
    ) or not np.array_equal(
        arrays["F_cross_history"][-1],
        arrays["F_cross_complex"],
    ):
        raise GateContractError("frequency final-row/history relation mismatch")
    comparison["history_final_row_relation_exact"] = True
    return comparison


def _projection_nrmse(
    candidate: np.ndarray,
    reference: np.ndarray,
) -> float:
    difference = candidate - reference
    numerator = float(np.sqrt(np.mean(np.square(difference))))
    candidate_rms = float(np.sqrt(np.mean(np.square(candidate))))
    reference_rms = float(np.sqrt(np.mean(np.square(reference))))
    return numerator / max(candidate_rms, reference_rms, 1.0e-30)


def _compare_full_image_result(
    order: Sequence[str],
    arrays: Mapping[str, np.ndarray],
    metadata: Mapping[str, Any],
    reference_path: Path,
) -> dict[str, Any]:
    reference_order, reference_arrays, reference_metadata, _ = _read_npz(
        reference_path
    )
    if tuple(order) != FULL_IMAGE_ARRAY_ORDER:
        raise GateContractError("full-image output array order mismatch")
    if tuple(reference_order) != FULL_IMAGE_ARRAY_ORDER:
        raise GateContractError("full-image reference array order mismatch")
    for name in FULL_IMAGE_STABLE_METADATA_KEYS:
        if metadata.get(name) != reference_metadata.get(name):
            raise GateContractError(
                f"full-image stable metadata mismatch: {name}"
            )
    diagnostics = metadata.get("diagnostics")
    reference_diagnostics = reference_metadata.get("diagnostics")
    if not isinstance(diagnostics, Mapping) or not isinstance(
        reference_diagnostics,
        Mapping,
    ):
        raise GateContractError("full-image diagnostics schema mismatch")
    scientific_diagnostics = {
        name: value
        for name, value in diagnostics.items()
        if name != "run_radial_cache"
    }
    reference_scientific_diagnostics = {
        name: value
        for name, value in reference_diagnostics.items()
        if name != "run_radial_cache"
    }
    if scientific_diagnostics != reference_scientific_diagnostics:
        raise GateContractError(
            "full-image scientific diagnostics mismatch"
        )
    run_cache = diagnostics.get("run_radial_cache")
    if run_cache != {
        "enabled": True,
        "unique_solution_count": 358,
        "hit_count": FULL_IMAGE_OPTIMIZED_CACHE_HIT_COUNT,
        "key_count": 358,
    }:
        raise GateContractError(
            "full-image optimized run-cache accounting mismatch"
        )
    exact_names = {"theta", "phi", "x", "z", "r", "valid_mask"}
    comparison = _scientific_array_comparison(
        FULL_IMAGE_SCIENTIFIC_ARRAY_ORDER,
        arrays,
        FULL_IMAGE_SCIENTIFIC_ARRAY_ORDER,
        reference_arrays,
        exact_names=exact_names,
    )
    valid_mask = np.asarray(arrays["valid_mask"], dtype=bool)
    if valid_mask.shape != FULL_IMAGE_RESOLUTION:
        raise GateContractError("full-image valid mask resolution mismatch")
    valid_count = int(np.count_nonzero(valid_mask))
    if (
        valid_count != FULL_IMAGE_VALID_COUNT
        or valid_mask.size - valid_count != FULL_IMAGE_MASKED_COUNT
    ):
        raise GateContractError("full-image valid/masked cardinality mismatch")
    nrmse: dict[str, dict[str, float]] = {}
    max_nrmse = 0.0
    max_linf = 0.0
    for name in ("h_plus", "h_cross"):
        actual = np.asarray(arrays[name])[valid_mask]
        expected = np.asarray(reference_arrays[name])[valid_mask]
        nrmse[name] = {}
        for projection, actual_part, expected_part in (
            ("real", actual.real, expected.real),
            ("imag", actual.imag, expected.imag),
            ("abs", np.abs(actual), np.abs(expected)),
        ):
            value = _projection_nrmse(actual_part, expected_part)
            nrmse[name][projection] = value
            max_nrmse = max(max_nrmse, value)
        maximum_difference = float(np.max(np.abs(actual - expected)))
        denominator = max(
            float(np.max(np.abs(actual))),
            float(np.max(np.abs(expected))),
            1.0e-30,
        )
        max_linf = max(max_linf, maximum_difference / denominator)
    if max_nrmse > PIXEL_NRMSE_BUDGET:
        raise GateContractError("full-image pixel NRMSE budget exceeded")
    if max_linf > NORMALIZED_LINF_BUDGET:
        raise GateContractError(
            "full-image normalized pixel L-infinity budget exceeded"
        )
    history = diagnostics.get("lmax_convergence_history", [])
    if (
        diagnostics.get("final_lmax_pair") != [156, 180]
        or len(history) != 3
        or history[-1].get("previous_lmax") != 156
        or history[-1].get("current_lmax") != 180
        or history[-1].get("max_relative_change", math.inf) > 1.0e-4
    ):
        raise GateContractError("full-image lmax convergence contract mismatch")
    legacy_summary = reference_metadata["diagnostics"]["summary"]
    actual_summary = diagnostics["summary"]
    residual_comparison = {}
    for name in (
        "max_boundary_residual_max",
        "max_wronskian_residual_max",
    ):
        actual_value = float(actual_summary[name])
        legacy_value = float(legacy_summary[name])
        limit = max(legacy_value * 1.05, legacy_value + 5.0e-13)
        if not math.isfinite(actual_value) or actual_value > limit:
            raise GateContractError(
                f"full-image residual worsening budget exceeded: {name}"
            )
        residual_comparison[name] = {
            "actual": actual_value,
            "legacy": legacy_value,
            "limit": limit,
            "passed": True,
        }
    comparison.update(
        {
            "coordinates_valid_mask_exact": True,
            "valid_point_count": valid_count,
            "invalid_point_count": valid_mask.size - valid_count,
            "stable_metadata_exact": True,
            "scientific_diagnostics_exact": True,
            "optimized_run_cache": dict(run_cache),
            "history_final_row_relation_exact": True,
            "pixel_nrmse": nrmse,
            "max_pixel_nrmse": max_nrmse,
            "max_normalized_pixel_linf": max_linf,
            "residual_comparison": residual_comparison,
        }
    )
    return comparison


def _max_residual_summary(
    solution_records: Sequence[Mapping[str, Any]],
) -> dict[str, float]:
    if not solution_records:
        raise GateContractError("radial residual evidence is empty")
    names = sorted(
        {
            name
            for record in solution_records
            for name in record.get("residuals", {})
        }
    )
    maxima = {
        name: max(
            float(record.get("residuals", {}).get(name, -math.inf))
            for record in solution_records
            if name in record.get("residuals", {})
        )
        for name in names
    }
    _validate_radial_residual_maxima(maxima)
    return maxima


def _validate_radial_residual_maxima(
    maxima: Mapping[str, Any],
) -> dict[str, float]:
    limits = {
        "boundary_residual": BOUNDARY_RESIDUAL_HARD_LIMIT,
        "wronskian_residual": WRONSKIAN_RESIDUAL_HARD_LIMIT,
        "flux_residual": FLUX_RESIDUAL_HARD_LIMIT,
    }
    validated: dict[str, float] = {}
    for name, limit in limits.items():
        value = maxima.get(name)
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float, np.generic))
            or not math.isfinite(float(value))
            or float(value) < 0.0
        ):
            raise GateContractError(
                f"radial residual maximum is missing or invalid: {name}"
            )
        numeric = float(value)
        if numeric >= limit:
            raise GateContractError(
                f"radial residual hard gate failed: {name}"
            )
        validated[name] = numeric
    return validated


def _validate_resource_record(record: Mapping[str, Any]) -> None:
    expected_keys = {
        "wall_seconds",
        "user_cpu_seconds",
        "system_cpu_seconds",
        "cpu_seconds",
        "peak_rss",
        "peak_rss_unit",
        "minor_faults",
        "major_faults",
    }
    if not isinstance(record, Mapping) or set(record) != expected_keys:
        raise GateContractError("optimized resource record schema mismatch")
    for name in (
        "wall_seconds",
        "user_cpu_seconds",
        "system_cpu_seconds",
        "cpu_seconds",
    ):
        value = record.get(name)
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or float(value) < 0.0
        ):
            raise GateContractError(f"invalid optimized resource metric: {name}")
    for name in ("peak_rss", "minor_faults", "major_faults"):
        value = record.get(name)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise GateContractError(f"invalid optimized resource metric: {name}")
    if record.get("peak_rss_unit") != "bytes_on_macos":
        raise GateContractError("optimized peak-RSS unit mismatch")
    if not math.isclose(
        float(record["cpu_seconds"]),
        float(record["user_cpu_seconds"])
        + float(record["system_cpu_seconds"]),
        rel_tol=0.0,
        abs_tol=1.0e-12,
    ):
        raise GateContractError("optimized CPU resource accounting mismatch")


def _validate_stage_profile(
    profile: Mapping[str, Any],
    *,
    case_kind: str,
    resource_record: Mapping[str, Any],
    solve_count: int,
) -> None:
    expected_keys = {
        "radial",
        "polarization",
        "flat",
        "polarization_nonradial_wall_seconds",
        "polarization_nonradial_cpu_seconds",
        "unattributed_wall_seconds",
    }
    if not isinstance(profile, Mapping) or set(profile) != expected_keys:
        raise GateContractError("optimized stage profile schema mismatch")
    stages: dict[str, Mapping[str, Any]] = {}
    for stage_name in ("radial", "polarization", "flat"):
        stage = profile.get(stage_name)
        if (
            not isinstance(stage, Mapping)
            or set(stage) != {"calls", "wall_seconds", "cpu_seconds"}
        ):
            raise GateContractError(
                f"optimized stage profile schema mismatch: {stage_name}"
            )
        calls = stage.get("calls")
        if isinstance(calls, bool) or not isinstance(calls, int) or calls < 0:
            raise GateContractError(
                f"optimized stage calls must be an integer: {stage_name}"
            )
        for metric in ("wall_seconds", "cpu_seconds"):
            value = stage.get(metric)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
                or float(value) < 0.0
            ):
                raise GateContractError(
                    f"invalid optimized stage metric: {stage_name}.{metric}"
                )
        stages[stage_name] = stage

    if stages["radial"]["calls"] != solve_count:
        raise GateContractError("optimized stage/solve accounting mismatch")
    expected_calls = {
        "frequency": {"polarization": 32, "flat": 32},
        "full-image": {"polarization": 57_932, "flat": 0},
    }
    if case_kind not in expected_calls:
        raise GateContractError("unsupported stage-profile case kind")
    for stage_name, expected in expected_calls[case_kind].items():
        if stages[stage_name]["calls"] != expected:
            raise GateContractError(
                f"optimized stage call-count mismatch: {stage_name}"
            )

    derived = {
        "polarization_nonradial_wall_seconds": (
            float(stages["polarization"]["wall_seconds"])
            - float(stages["radial"]["wall_seconds"])
        ),
        "polarization_nonradial_cpu_seconds": (
            float(stages["polarization"]["cpu_seconds"])
            - float(stages["radial"]["cpu_seconds"])
        ),
        "unattributed_wall_seconds": (
            float(resource_record["wall_seconds"])
            - float(stages["polarization"]["wall_seconds"])
            - (
                float(stages["flat"]["wall_seconds"])
                if case_kind == "frequency"
                else 0.0
            )
        ),
    }
    for name, expected in derived.items():
        value = profile.get(name)
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or float(value) < 0.0
            or not math.isclose(
                float(value),
                expected,
                rel_tol=0.0,
                abs_tol=1.0e-12,
            )
        ):
            raise GateContractError(
                f"optimized derived stage metric mismatch: {name}"
            )


def _validate_profile_top(rows: Any) -> None:
    if not isinstance(rows, list) or not rows or len(rows) > 50:
        raise GateContractError("optimized cumulative profile schema mismatch")
    expected_keys = {
        "file",
        "line",
        "function",
        "primitive_calls",
        "calls",
        "total_seconds",
        "cumulative_seconds",
    }
    previous = math.inf
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != expected_keys:
            raise GateContractError("optimized cumulative profile row mismatch")
        if not isinstance(row.get("file"), str) or not row["file"]:
            raise GateContractError("optimized profile file must be nonempty")
        if not isinstance(row.get("function"), str) or not row["function"]:
            raise GateContractError("optimized profile function must be nonempty")
        for name in ("line", "primitive_calls", "calls"):
            value = row.get(name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise GateContractError(
                    f"optimized profile integer metric mismatch: {name}"
                )
        for name in ("total_seconds", "cumulative_seconds"):
            value = row.get(name)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
                or float(value) < 0.0
            ):
                raise GateContractError(
                    f"optimized profile timing metric mismatch: {name}"
                )
        cumulative = float(row["cumulative_seconds"])
        if cumulative > previous:
            raise GateContractError(
                "optimized cumulative profile is out of canonical order"
            )
        previous = cumulative


def _expected_post_compute_identity(
    frozen: Mapping[str, Any],
    *,
    phase: str,
) -> dict[str, Any]:
    return {
        "phase": phase,
        "runner_sha256": frozen["runner"]["sha256"],
        "implementation_commit": frozen["implementation"]["commit"],
        "benchmark_identity_sha256": frozen["identity"].canonical_digest,
        "source_manifest_sha256": frozen["source"]["manifest_sha256"],
        "loaded_module_manifest_sha256": frozen["loaded_modules"][
            "manifest_sha256"
        ],
        "gate_manifest_sha256": frozen["gates"]["manifest_sha256"],
        "tablei_input_manifest_sha256": frozen["tablei_inputs"][
            "manifest_sha256"
        ],
        "config_sha256": frozen["config_identity"]["sha256"],
        "environment_sha256": frozen["environment"]["environment_sha256"],
    }


def _validate_run_source_command(
    frozen: Mapping[str, Any],
    paths: ArtifactPaths,
    command: Any,
) -> list[str]:
    if (
        not isinstance(command, list)
        or any(not isinstance(item, str) or not item for item in command)
        or len(command) < 11
    ):
        raise GateContractError("optimized source command schema mismatch")
    worker_token = command[-1]
    if worker_token not in {"1", "2"}:
        raise GateContractError("optimized source command worker mismatch")
    if paths.case_id.startswith("frequency:"):
        token = paths.case_id.split(":", 1)[1]
        frequency = next(
            value
            for value, candidate in FREQUENCY_TOKENS.items()
            if candidate == token
        )
        expected = [
            str(Path(__file__).resolve()),
            "--mode",
            "run",
            "--case",
            "frequency",
            "--frequency",
            repr(frequency),
        ]
    else:
        expected = [
            str(Path(__file__).resolve()),
            "--mode",
            "run",
            "--case",
            "full-image",
        ]
    expected.extend(
        [
            "--expected-self-sha256",
            frozen["runner"]["sha256"],
            "--expected-implementation-commit",
            frozen["implementation"]["commit"],
            "--max-workers",
            worker_token,
        ]
    )
    if command != expected:
        raise GateContractError("optimized source command identity mismatch")
    return expected


def _validate_benchmark_case_binding(
    frozen: Mapping[str, Any],
    paths: ArtifactPaths,
    benchmark: Mapping[str, Any],
) -> str:
    if paths.case_id.startswith("frequency:"):
        case_kind = "frequency"
        expected_keys = {
            "schema_version",
            "case_kind",
            "case_id",
            "kM",
            "source_command",
            "runner",
            "identity",
            "generation_contract",
            "generation_contract_sha256",
            "metadata_contract_sha256",
            "post_compute_identity_recheck",
            "resource_record",
            "stage_profile",
            "profile_top_cumulative",
            "cache_metrics",
            "radial_residual_maxima",
            "raw_warning_record",
            "structured_warning_record",
            "legacy_identity",
            "legacy_comparison",
            "golden_comparison",
            "non_claims",
        }
        token = paths.case_id.split(":", 1)[1]
        expected_frequency = next(
            frequency
            for frequency, candidate in FREQUENCY_TOKENS.items()
            if candidate == token
        )
        phase = f"{paths.case_id}:post_compute"
    else:
        case_kind = "full-image"
        expected_keys = {
            "schema_version",
            "case_kind",
            "case_id",
            "source_command",
            "runner",
            "identity",
            "post_compute_identity_recheck",
            "resource_record",
            "stage_profile",
            "profile_top_cumulative",
            "cache_metrics",
            "radial_residual_maxima",
            "raw_warning_record",
            "structured_warning_record",
            "legacy_identity",
            "legacy_comparison",
            "golden_comparison",
            "non_claims",
        }
        phase = "full-image:post_compute"

    if not isinstance(benchmark, Mapping) or set(benchmark) != expected_keys:
        raise GateContractError("optimized benchmark record schema mismatch")
    if case_kind == "frequency":
        if (
            isinstance(benchmark.get("kM"), bool)
            or benchmark.get("kM") != expected_frequency
        ):
            raise GateContractError("optimized benchmark frequency mismatch")
        generation, generation_sha256, metadata_sha256 = (
            _frequency_generation_contract(frozen)
        )
        if (
            benchmark.get("generation_contract") != generation
            or benchmark.get("generation_contract_sha256")
            != generation_sha256
            or benchmark.get("metadata_contract_sha256") != metadata_sha256
        ):
            raise GateContractError(
                "optimized benchmark generation contract mismatch"
            )
    expected_non_claims = {
        "new_frequency": False,
        "production_artifact": False,
        "publication_plot": False,
        "spin2_physics_implemented_or_validated": False,
    }
    _validate_run_source_command(
        frozen,
        paths,
        benchmark.get("source_command"),
    )
    if (
        benchmark.get("schema_version") != OUTPUT_SCHEMA_VERSION
        or benchmark.get("case_kind") != case_kind
        or benchmark.get("case_id") != paths.case_id
        or benchmark.get("runner") != frozen["runner"]
        or benchmark.get("identity") != _identity_payload(frozen)
        or benchmark.get("post_compute_identity_recheck")
        != _expected_post_compute_identity(frozen, phase=phase)
        or benchmark.get("non_claims") != expected_non_claims
    ):
        raise GateContractError("optimized benchmark case/provenance mismatch")
    _validate_profile_top(benchmark.get("profile_top_cumulative"))
    return case_kind


def _validate_full_image_residual_binding(
    maxima: Mapping[str, Any],
    metadata: Mapping[str, Any],
) -> None:
    diagnostics = metadata.get("diagnostics")
    summary = (
        diagnostics.get("summary")
        if isinstance(diagnostics, Mapping)
        else None
    )
    if not isinstance(summary, Mapping):
        raise GateContractError("full-image residual metadata schema mismatch")
    bindings = {
        "boundary_residual": "max_boundary_residual_max",
        "wronskian_residual": "max_wronskian_residual_max",
    }
    for benchmark_name, metadata_name in bindings.items():
        benchmark_value = maxima.get(benchmark_name)
        metadata_value = summary.get(metadata_name)
        if (
            isinstance(benchmark_value, bool)
            or isinstance(metadata_value, bool)
            or not isinstance(benchmark_value, (int, float))
            or not isinstance(metadata_value, (int, float))
            or not math.isfinite(float(benchmark_value))
            or not math.isfinite(float(metadata_value))
            or float(benchmark_value) != float(metadata_value)
        ):
            raise GateContractError(
                f"full-image benchmark/metadata residual mismatch: "
                f"{benchmark_name}"
            )


def _run_frequency_solver(
    frozen: Mapping[str, Any],
    frequency: float,
    command: Sequence[str],
) -> dict[str, Any]:
    if frequency not in FREQUENCY_TOKENS:
        raise GateContractError("frequency is outside the frozen matrix")
    tablei = frozen["modules"]["tablei"]
    partial_wave = frozen["modules"]["partial_wave"]
    numerics = frozen["modules"]["numerics"]
    generation, generation_hash, metadata_hash = (
        _frequency_generation_contract(frozen)
    )
    inputs = frozen["tablei_inputs"]
    stages = _new_stage_profile()
    solution_records: list[dict[str, Any]] = []
    true_ode_solve_count = 0
    true_oracle_solve_count = 0

    def timed_radial(*args: Any, **kwargs: Any) -> Any:
        nonlocal true_ode_solve_count, true_oracle_solve_count
        wall_start = time.perf_counter()
        cpu_start = time.process_time()
        try:
            solution = numerics.solve_radial_mode(*args, **kwargs)
        finally:
            stages["radial"]["calls"] += 1
            stages["radial"]["wall_seconds"] += (
                time.perf_counter() - wall_start
            )
            stages["radial"]["cpu_seconds"] += (
                time.process_time() - cpu_start
            )
        metrics = _solution_metrics(solution)
        solution_records.append(metrics)
        if metrics["oracle"]:
            true_oracle_solve_count += 1
        else:
            true_ode_solve_count += 1
        return solution

    def timed_polarization(*args: Any, **kwargs: Any) -> Any:
        wall_start = time.perf_counter()
        cpu_start = time.process_time()
        try:
            return partial_wave.compute_polarization(*args, **kwargs)
        finally:
            stages["polarization"]["calls"] += 1
            stages["polarization"]["wall_seconds"] += (
                time.perf_counter() - wall_start
            )
            stages["polarization"]["cpu_seconds"] += (
                time.process_time() - cpu_start
            )

    def timed_flat(*args: Any, **kwargs: Any) -> Any:
        wall_start = time.perf_counter()
        cpu_start = time.process_time()
        try:
            return partial_wave.compute_flat_no_lens_polarization(
                *args,
                **kwargs,
            )
        finally:
            stages["flat"]["calls"] += 1
            stages["flat"]["wall_seconds"] += time.perf_counter() - wall_start
            stages["flat"]["cpu_seconds"] += time.process_time() - cpu_start

    usage_start = resource.getrusage(resource.RUSAGE_SELF)
    wall_start = time.perf_counter()
    profile = cProfile.Profile()
    profile.enable()
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            arrays, raw_metadata = tablei._compute_frequency(
                frequency,
                generation_hash=generation_hash,
                metadata_hash=metadata_hash,
                source_paths=inputs["source_paths"],
                source_hashes=inputs["source_hashes"],
                gate_paths=inputs["gate_paths"],
                gate_hashes=inputs["gate_hashes"],
                implementation=frozen["implementation"],
                selected_code_hashes=frozen["selected_code_hashes"],
                polarization_solver=timed_polarization,
                flat_solver=timed_flat,
                radial_solver=timed_radial,
            )
    finally:
        profile.disable()
    wall_seconds = time.perf_counter() - wall_start
    usage_end = resource.getrusage(resource.RUSAGE_SELF)
    post_compute_identity = _recheck_identity(
        frozen,
        phase=f"frequency:{FREQUENCY_TOKENS[frequency]}:post_compute",
    )
    raw_warning_record = _raw_warning_record(caught)
    legacy = _audit_legacy_frequency(FREQUENCY_TOKENS[frequency])
    _compare_warning_records(
        raw_warning_record,
        legacy["raw_warning_record"],
    )
    legacy_metadata = legacy["metadata"]
    for name in (
        "radial_warning_codes",
        "radial_warning_count",
        "adapter_use_count",
    ):
        if raw_metadata.get(name) != legacy_metadata.get(name):
            raise GateContractError(
                f"optimized/legacy structured warning mismatch: {name}"
            )
    solve_count = int(raw_metadata["radial_solve_count"])
    if (
        stages["radial"]["calls"] != solve_count
        or true_ode_solve_count + true_oracle_solve_count != solve_count
    ):
        raise GateContractError("frequency true-solve accounting mismatch")
    stages["polarization_nonradial_wall_seconds"] = (
        stages["polarization"]["wall_seconds"]
        - stages["radial"]["wall_seconds"]
    )
    stages["polarization_nonradial_cpu_seconds"] = (
        stages["polarization"]["cpu_seconds"]
        - stages["radial"]["cpu_seconds"]
    )
    stages["unattributed_wall_seconds"] = (
        wall_seconds
        - stages["polarization"]["wall_seconds"]
        - stages["flat"]["wall_seconds"]
    )
    metadata = dict(raw_metadata)
    metadata["t4ae_optimized_methods"] = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "runner_sha256": frozen["runner"]["sha256"],
        "implementation_commit": frozen["implementation"]["commit"],
        "benchmark_identity_sha256": frozen["identity"].canonical_digest,
        "generation_contract_sha256": generation_hash,
        "source_command": list(command),
        "non_claims": {
            "new_frequency": False,
            "production_artifact": False,
            "publication_plot": False,
            "spin2_physics_implemented_or_validated": False,
        },
    }
    arrays = dict(arrays)
    arrays["metadata_json"] = np.asarray(_canonical_json(metadata))
    order = tuple(arrays)
    legacy_comparison = _compare_frequency_result(
        order,
        {name: arrays[name] for name in order if name != "metadata_json"},
        metadata,
        legacy,
    )
    golden_comparison = _compare_frequency_result(
        order,
        {name: arrays[name] for name in order if name != "metadata_json"},
        metadata,
        {
            "npz_path": str(
                FREQUENCY_GOLDEN_ROOT
                / f"kM_{FREQUENCY_TOKENS[frequency]}.npz"
            )
        },
    )
    resource_record = _resource_record(
        wall_seconds=wall_seconds,
        usage_start=usage_start,
        usage_end=usage_end,
    )
    cache_metrics = {
        "ode_solve_count": true_ode_solve_count,
        "oracle_solve_count": true_oracle_solve_count,
        "ode_oracle_solve_count": solve_count,
        "cache_hit_count": int(raw_metadata["radial_reuse_count"]),
        "cache_miss_count": solve_count,
        "cache_rejection_count": 0,
        "cache_key_count": solve_count,
        "benchmark_identity_sha256": frozen["identity"].canonical_digest,
    }
    benchmark_record = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "case_kind": "frequency",
        "case_id": f"frequency:{FREQUENCY_TOKENS[frequency]}",
        "kM": frequency,
        "source_command": list(command),
        "runner": frozen["runner"],
        "identity": _identity_payload(frozen),
        "generation_contract": generation,
        "generation_contract_sha256": generation_hash,
        "metadata_contract_sha256": metadata_hash,
        "post_compute_identity_recheck": post_compute_identity,
        "resource_record": resource_record,
        "stage_profile": stages,
        "profile_top_cumulative": _profile_top(profile),
        "cache_metrics": cache_metrics,
        "radial_residual_maxima": _max_residual_summary(solution_records),
        "raw_warning_record": raw_warning_record,
        "structured_warning_record": {
            "codes": list(raw_metadata["radial_warning_codes"]),
            "total_count": int(raw_metadata["radial_warning_count"]),
            "oracle_adapter_use_count": int(raw_metadata["adapter_use_count"]),
        },
        "legacy_identity": {
            key: legacy[key]
            for key in (
                "npz_path",
                "sidecar_path",
                "golden_path",
                "npz_sha256",
                "sidecar_sha256",
                "golden_sha256",
            )
        },
        "legacy_comparison": legacy_comparison,
        "golden_comparison": golden_comparison,
        "non_claims": {
            "new_frequency": False,
            "production_artifact": False,
            "publication_plot": False,
            "spin2_physics_implemented_or_validated": False,
        },
    }
    return {
        "payload": arrays,
        "metadata_text": str(arrays["metadata_json"].item()),
        "benchmark_record": benchmark_record,
        "comparison": {
            "legacy": legacy_comparison,
            "golden": golden_comparison,
        },
    }


def _run_full_image_solver(
    frozen: Mapping[str, Any],
    command: Sequence[str],
) -> dict[str, Any]:
    modules = frozen["modules"]
    config = frozen["full_image_config"]["object"]
    results = modules["results"]
    numerics = modules["numerics"]
    partial_wave = modules["partial_wave"]
    original_public_radial = numerics.solve_radial_mode
    stages = _new_stage_profile()
    solution_records: list[dict[str, Any]] = []
    true_ode_solve_count = 0
    true_oracle_solve_count = 0

    def timed_radial(*args: Any, **kwargs: Any) -> Any:
        nonlocal true_ode_solve_count, true_oracle_solve_count
        wall_start = time.perf_counter()
        cpu_start = time.process_time()
        try:
            solution = original_public_radial(*args, **kwargs)
        finally:
            stages["radial"]["calls"] += 1
            stages["radial"]["wall_seconds"] += (
                time.perf_counter() - wall_start
            )
            stages["radial"]["cpu_seconds"] += (
                time.process_time() - cpu_start
            )
        metrics = _solution_metrics(solution)
        solution_records.append(metrics)
        if metrics["oracle"]:
            true_oracle_solve_count += 1
        else:
            true_ode_solve_count += 1
        return solution

    def timed_polarization(*args: Any, **kwargs: Any) -> Any:
        wall_start = time.perf_counter()
        cpu_start = time.process_time()
        try:
            return partial_wave.compute_polarization(*args, **kwargs)
        finally:
            stages["polarization"]["calls"] += 1
            stages["polarization"]["wall_seconds"] += (
                time.perf_counter() - wall_start
            )
            stages["polarization"]["cpu_seconds"] += (
                time.process_time() - cpu_start
            )

    source_command = list(command)
    usage_start = resource.getrusage(resource.RUSAGE_SELF)
    wall_start = time.perf_counter()
    profile = cProfile.Profile()
    numerics.solve_radial_mode = timed_radial
    profile.enable()
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = results.run_solver_grid(
                config,
                polarization_solver=timed_polarization,
                source_command=source_command,
            )
    finally:
        profile.disable()
        numerics.solve_radial_mode = original_public_radial
    wall_seconds = time.perf_counter() - wall_start
    usage_end = resource.getrusage(resource.RUSAGE_SELF)
    post_compute_identity = _recheck_identity(
        frozen,
        phase="full-image:post_compute",
    )
    raw_warning_record = _raw_warning_record(caught)
    if raw_warning_record["total_count"] != 0:
        raise GateContractError("full-image run emitted raw warnings")
    diagnostics = result.metadata["diagnostics"]
    if diagnostics.get("radial_diagnostic_warnings") != []:
        raise GateContractError("full-image run emitted structured warnings")
    cache = diagnostics["run_radial_cache"]
    if (
        stages["radial"]["calls"] != 358
        or stages["polarization"]["calls"] != 57_932
        or stages["flat"]["calls"] != 0
        or cache
        != {
            "enabled": True,
            "unique_solution_count": 358,
            "hit_count": FULL_IMAGE_OPTIMIZED_CACHE_HIT_COUNT,
            "key_count": 358,
        }
        or true_ode_solve_count != 358
        or true_oracle_solve_count != 0
    ):
        raise GateContractError("full-image call/cache/true-solve contract mismatch")
    arrays = {
        "theta": np.asarray(result.theta),
        "phi": np.asarray(result.phi),
        "h_plus": np.asarray(result.h_plus),
        "h_cross": np.asarray(result.h_cross),
        "x": np.asarray(result.x),
        "z": np.asarray(result.z),
        "r": np.asarray(result.r),
        "valid_mask": np.asarray(result.valid_mask),
    }
    legacy_comparison = _compare_full_image_result(
        FULL_IMAGE_ARRAY_ORDER,
        arrays,
        result.metadata,
        LEGACY_ROOT / "full_image" / FULL_IMAGE_FILENAME,
    )
    golden_comparison = _compare_full_image_result(
        FULL_IMAGE_ARRAY_ORDER,
        arrays,
        result.metadata,
        FULL_IMAGE_GOLDEN,
    )
    stages["polarization_nonradial_wall_seconds"] = (
        stages["polarization"]["wall_seconds"]
        - stages["radial"]["wall_seconds"]
    )
    stages["polarization_nonradial_cpu_seconds"] = (
        stages["polarization"]["cpu_seconds"]
        - stages["radial"]["cpu_seconds"]
    )
    stages["unattributed_wall_seconds"] = (
        wall_seconds - stages["polarization"]["wall_seconds"]
    )
    metadata = dict(result.metadata)
    metadata_text = _canonical_json(metadata)
    payload = {
        "theta": arrays["theta"],
        "phi": arrays["phi"],
        "h_plus": arrays["h_plus"],
        "h_cross": arrays["h_cross"],
        "metadata_json": np.asarray(
            metadata_text,
            dtype=FULL_IMAGE_METADATA_DTYPE,
        ),
        "x": arrays["x"],
        "z": arrays["z"],
        "r": arrays["r"],
        "valid_mask": arrays["valid_mask"],
    }
    resource_record = _resource_record(
        wall_seconds=wall_seconds,
        usage_start=usage_start,
        usage_end=usage_end,
    )
    legacy = _audit_legacy_full_image()
    benchmark_record = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "case_kind": "full-image",
        "case_id": "full-image:241x241",
        "source_command": source_command,
        "runner": frozen["runner"],
        "identity": _identity_payload(frozen),
        "post_compute_identity_recheck": post_compute_identity,
        "resource_record": resource_record,
        "stage_profile": stages,
        "profile_top_cumulative": _profile_top(profile),
        "cache_metrics": {
            "ode_solve_count": true_ode_solve_count,
            "oracle_solve_count": true_oracle_solve_count,
            "ode_oracle_solve_count": 358,
            "cache_hit_count": int(cache["hit_count"]),
            "cache_miss_count": int(cache["unique_solution_count"]),
            "cache_rejection_count": 0,
            "cache_key_count": int(cache["key_count"]),
            "benchmark_identity_sha256": frozen[
                "identity"
            ].canonical_digest,
        },
        "radial_residual_maxima": _max_residual_summary(solution_records),
        "raw_warning_record": raw_warning_record,
        "structured_warning_record": {
            "policy": "exact_empty_full_image_record",
            "total_count": 0,
            "entries": [],
        },
        "legacy_identity": {
            key: legacy[key]
            for key in (
                "npz_path",
                "sidecar_path",
                "golden_path",
                "npz_sha256",
                "sidecar_sha256",
                "golden_sha256",
            )
        },
        "legacy_comparison": legacy_comparison,
        "golden_comparison": golden_comparison,
        "non_claims": {
            "new_frequency": False,
            "production_artifact": False,
            "publication_plot": False,
            "spin2_physics_implemented_or_validated": False,
        },
    }
    return {
        "payload": payload,
        "metadata_text": metadata_text,
        "benchmark_record": benchmark_record,
        "comparison": {
            "legacy": legacy_comparison,
            "golden": golden_comparison,
        },
    }


def _transaction_id(
    frozen: Mapping[str, Any],
    paths: ArtifactPaths,
) -> str:
    return _canonical_sha256(
        {
            "schema_version": ATOMIC_SCHEMA_VERSION,
            "benchmark_identity_sha256": frozen[
                "identity"
            ].canonical_digest,
            "case_id": paths.case_id,
            "npz_name": paths.npz.name,
            "sidecar_name": paths.sidecar.name,
        }
    )


def _validate_output_scope() -> None:
    if not OUTPUT_ROOT.exists():
        return
    allowed_directories = {"frequencies", "full_image", "quarantine"}
    for child in OUTPUT_ROOT.iterdir():
        if child.name == GLOBAL_RUNNER_LOCK.name and child.is_file():
            continue
        if child.name not in allowed_directories or not child.is_dir():
            raise GateContractError(
                f"unexpected optimized output path: {child}"
            )
    for case_kind, directory in (
        ("frequency", OUTPUT_ROOT / "frequencies"),
        ("full-image", OUTPUT_ROOT / "full_image"),
    ):
        if not directory.exists():
            continue
        allowed_names = {"quarantine"}
        temporary_prefixes: set[str] = set()
        if case_kind == "frequency":
            for token in FREQUENCY_TOKENS.values():
                name = f"kM_{token}.npz"
                allowed_names.update(
                    {name, f"{name}.json", f".{name}.lock"}
                )
                temporary_prefixes.update(
                    {f"{name}.tmp.", f"{name}.json.tmp."}
                )
        else:
            allowed_names.update(
                {
                    FULL_IMAGE_FILENAME,
                    f"{FULL_IMAGE_FILENAME}.json",
                    f".{FULL_IMAGE_FILENAME}.lock",
                }
            )
            temporary_prefixes.update(
                {
                    f"{FULL_IMAGE_FILENAME}.tmp.",
                    f"{FULL_IMAGE_FILENAME}.json.tmp.",
                }
            )
        for child in directory.iterdir():
            if child.name in allowed_names:
                continue
            if child.is_file() and any(
                child.name.startswith(prefix)
                and len(child.name) > len(prefix)
                for prefix in temporary_prefixes
            ):
                continue
            raise GateContractError(
                f"unexpected optimized case output path: {child}"
            )


def _build_sidecar(
    frozen: Mapping[str, Any],
    paths: ArtifactPaths,
    run_record: Mapping[str, Any],
) -> dict[str, Any]:
    payload = run_record["payload"]
    order = tuple(payload)
    npz_sha256 = _sha256(paths.npz)
    metadata_text = str(run_record["metadata_text"])
    transaction_id = _transaction_id(frozen, paths)
    benchmark_record = dict(run_record["benchmark_record"])
    return {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "case_id": paths.case_id,
        "identity_sha256": frozen["identity"].canonical_digest,
        "runner_sha256": frozen["runner"]["sha256"],
        "implementation_commit": frozen["implementation"]["commit"],
        "implementation_manifest_sha256": frozen["implementation"][
            "manifest_sha256"
        ],
        "source_manifest_sha256": frozen["source"]["manifest_sha256"],
        "physics_manifest_sha256": frozen["source"][
            "physics_manifest_sha256"
        ],
        "solver_manifest_sha256": frozen["source"][
            "solver_manifest_sha256"
        ],
        "config_sha256": frozen["config_identity"]["sha256"],
        "gate_manifest_sha256": frozen["gates"]["manifest_sha256"],
        "tablei_input_manifest_sha256": frozen["tablei_inputs"][
            "manifest_sha256"
        ],
        "environment_sha256": frozen["environment"]["environment_sha256"],
        "npz_sha256": npz_sha256,
        "metadata_json_sha256": _sha256_bytes(
            metadata_text.encode("utf-8")
        ),
        "array_order": list(order),
        "array_fingerprints": _payload_fingerprints(payload, order),
        "comparison": run_record["comparison"],
        "benchmark_record": benchmark_record,
        "benchmark_record_sha256": _canonical_sha256(benchmark_record),
        "transaction": {
            "schema_version": ATOMIC_SCHEMA_VERSION,
            "transaction_id": transaction_id,
            "state": "complete",
            "commit_order": ["npz", "sidecar"],
            "canonical_member_order": [
                paths.npz.name,
                paths.sidecar.name,
            ],
            "members": [
                {
                    "name": paths.npz.name,
                    "role": "payload",
                    "sha256": npz_sha256,
                },
                {
                    "name": paths.sidecar.name,
                    "role": "commit_marker",
                },
            ],
            "npz_sha256": npz_sha256,
            "sidecar_is_commit_marker": True,
        },
    }


def _commit_run_record(
    frozen: Mapping[str, Any],
    paths: ArtifactPaths,
    run_record: Mapping[str, Any],
) -> None:
    transaction_id = _transaction_id(frozen, paths)
    _recheck_identity(frozen, phase=f"{paths.case_id}:pre_npz_commit")
    _atomic_npz(
        paths.npz,
        run_record["payload"],
        transaction_id=transaction_id,
    )
    sidecar = _build_sidecar(frozen, paths, run_record)
    _atomic_json(
        paths.sidecar,
        sidecar,
        transaction_id=transaction_id,
    )
    _recheck_identity(frozen, phase=f"{paths.case_id}:post_sidecar_commit")


def _audit_optimized_pair(
    frozen: Mapping[str, Any],
    paths: ArtifactPaths,
    *,
    allow_owned_lock: bool = False,
    owned_lock: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    state = _artifact_state(
        paths,
        allow_owned_lock=allow_owned_lock,
        owned_lock=owned_lock,
    )
    if state["state"] != "complete_pair":
        raise GateContractError(
            "optimized atomic pair is not complete: " + _canonical_json(state)
        )
    sidecar = _read_json(paths.sidecar)
    expected_sidecar_keys = {
        "schema_version",
        "case_id",
        "identity_sha256",
        "runner_sha256",
        "implementation_commit",
        "implementation_manifest_sha256",
        "source_manifest_sha256",
        "physics_manifest_sha256",
        "solver_manifest_sha256",
        "config_sha256",
        "gate_manifest_sha256",
        "tablei_input_manifest_sha256",
        "environment_sha256",
        "npz_sha256",
        "metadata_json_sha256",
        "array_order",
        "array_fingerprints",
        "comparison",
        "benchmark_record",
        "benchmark_record_sha256",
        "transaction",
    }
    if set(sidecar) != expected_sidecar_keys:
        raise GateContractError("optimized sidecar key contract mismatch")
    expected_identity = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "case_id": paths.case_id,
        "identity_sha256": frozen["identity"].canonical_digest,
        "runner_sha256": frozen["runner"]["sha256"],
        "implementation_commit": frozen["implementation"]["commit"],
        "implementation_manifest_sha256": frozen["implementation"][
            "manifest_sha256"
        ],
        "source_manifest_sha256": frozen["source"]["manifest_sha256"],
        "physics_manifest_sha256": frozen["source"][
            "physics_manifest_sha256"
        ],
        "solver_manifest_sha256": frozen["source"][
            "solver_manifest_sha256"
        ],
        "config_sha256": frozen["config_identity"]["sha256"],
        "gate_manifest_sha256": frozen["gates"]["manifest_sha256"],
        "tablei_input_manifest_sha256": frozen["tablei_inputs"][
            "manifest_sha256"
        ],
        "environment_sha256": frozen["environment"]["environment_sha256"],
    }
    for name, expected in expected_identity.items():
        if sidecar.get(name) != expected:
            raise GateContractError(f"optimized sidecar identity mismatch: {name}")
    npz_sha256 = _sha256(paths.npz)
    if sidecar.get("npz_sha256") != npz_sha256:
        raise GateContractError("optimized sidecar/NPZ hash mismatch")
    order, arrays, metadata, metadata_text = _read_npz(paths.npz)
    if sidecar.get("array_order") != list(order):
        raise GateContractError("optimized array-order sidecar mismatch")
    payload = dict(arrays)
    if paths.case_id.startswith("full-image:"):
        payload["metadata_json"] = np.asarray(
            metadata_text,
            dtype=FULL_IMAGE_METADATA_DTYPE,
        )
        payload = {name: payload[name] for name in FULL_IMAGE_ARRAY_ORDER}
    else:
        payload["metadata_json"] = np.asarray(metadata_text)
        payload = {name: payload[name] for name in order}
    if sidecar.get("array_fingerprints") != _payload_fingerprints(
        payload,
        order,
    ):
        raise GateContractError("optimized array fingerprint mismatch")
    if sidecar.get("metadata_json_sha256") != _sha256_bytes(
        metadata_text.encode("utf-8")
    ):
        raise GateContractError("optimized metadata fingerprint mismatch")

    benchmark_value = sidecar.get("benchmark_record")
    if not isinstance(benchmark_value, Mapping):
        raise GateContractError("optimized benchmark record schema mismatch")
    benchmark = benchmark_value
    case_kind = _validate_benchmark_case_binding(
        frozen,
        paths,
        benchmark,
    )
    if paths.case_id.startswith("frequency:"):
        token = paths.case_id.split(":", 1)[1]
        _validate_frequency_embedded_metadata(
            frozen,
            token=token,
            arrays=arrays,
            metadata=metadata,
            benchmark=benchmark,
        )
        legacy = _audit_legacy_frequency(token)
        legacy_comparison = _compare_frequency_result(
            order,
            arrays,
            metadata,
            legacy,
        )
        golden_comparison = _compare_frequency_result(
            order,
            arrays,
            metadata,
            {
                "npz_path": str(
                    FREQUENCY_GOLDEN_ROOT / f"kM_{token}.npz"
                )
            },
        )
        _compare_warning_records(
            benchmark["raw_warning_record"],
            legacy["raw_warning_record"],
        )
        legacy_metadata = legacy["metadata"]
        expected_structured_warning_record = {
            "codes": list(legacy_metadata["radial_warning_codes"]),
            "total_count": int(legacy_metadata["radial_warning_count"]),
            "oracle_adapter_use_count": int(
                legacy_metadata["adapter_use_count"]
            ),
        }
        if (
            _validate_frequency_structured_warning_record(
                benchmark["structured_warning_record"]
            )
            != expected_structured_warning_record
        ):
            raise GateContractError(
                "optimized frequency structured-warning audit mismatch"
            )
        expected_legacy_identity = {
            key: legacy[key]
            for key in (
                "npz_path",
                "sidecar_path",
                "golden_path",
                "npz_sha256",
                "sidecar_sha256",
                "golden_sha256",
            )
        }
    else:
        if metadata.get("source_command") != benchmark["source_command"]:
            raise GateContractError(
                "optimized full-image embedded command mismatch"
            )
        legacy = _audit_legacy_full_image()
        legacy_comparison = _compare_full_image_result(
            order,
            arrays,
            metadata,
            LEGACY_ROOT / "full_image" / FULL_IMAGE_FILENAME,
        )
        golden_comparison = _compare_full_image_result(
            order,
            arrays,
            metadata,
            FULL_IMAGE_GOLDEN,
        )
        _validate_empty_full_image_warning_records(
            benchmark["raw_warning_record"],
            benchmark["structured_warning_record"],
        )
        expected_legacy_identity = {
            key: legacy[key]
            for key in (
                "npz_path",
                "sidecar_path",
                "golden_path",
                "npz_sha256",
                "sidecar_sha256",
                "golden_sha256",
            )
        }
    comparison = {
        "legacy": legacy_comparison,
        "golden": golden_comparison,
    }
    if sidecar.get("comparison") != comparison:
        raise GateContractError("optimized sidecar comparison record mismatch")
    if sidecar.get("benchmark_record_sha256") != _canonical_sha256(benchmark):
        raise GateContractError("optimized benchmark record hash mismatch")
    if (
        benchmark.get("legacy_identity") != expected_legacy_identity
        or benchmark.get("legacy_comparison") != legacy_comparison
        or benchmark.get("golden_comparison") != golden_comparison
    ):
        raise GateContractError(
            "optimized benchmark legacy/golden provenance mismatch"
        )
    resource_record = benchmark["resource_record"]
    _validate_resource_record(resource_record)
    cache = benchmark.get("cache_metrics", {})
    cache_count_names = (
        "ode_solve_count",
        "oracle_solve_count",
        "ode_oracle_solve_count",
        "cache_hit_count",
        "cache_miss_count",
        "cache_rejection_count",
        "cache_key_count",
    )
    if (
        not isinstance(cache, Mapping)
        or set(cache)
        != {*cache_count_names, "benchmark_identity_sha256"}
    ):
        raise GateContractError("optimized cache metric schema mismatch")
    for name in cache_count_names:
        value = cache.get(name)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise GateContractError(f"invalid optimized cache metric: {name}")
    if (
        cache.get("ode_solve_count", 0) + cache.get("oracle_solve_count", 0)
        != cache.get("ode_oracle_solve_count")
        or cache.get("cache_miss_count")
        != cache.get("ode_oracle_solve_count")
        or cache.get("cache_key_count")
        != cache.get("ode_oracle_solve_count")
        or cache.get("benchmark_identity_sha256")
        != frozen["identity"].canonical_digest
    ):
        raise GateContractError("optimized solve/cache accounting mismatch")
    if case_kind == "frequency":
        embedded_solve_count = metadata.get("radial_solve_count")
        embedded_reuse_count = metadata.get("radial_reuse_count")
        if (
            isinstance(embedded_solve_count, bool)
            or not isinstance(embedded_solve_count, int)
            or embedded_solve_count < 0
            or isinstance(embedded_reuse_count, bool)
            or not isinstance(embedded_reuse_count, int)
            or embedded_reuse_count < 0
            or cache["ode_oracle_solve_count"] != embedded_solve_count
            or cache["cache_hit_count"]
            != embedded_reuse_count
            or cache["cache_rejection_count"] != 0
        ):
            raise GateContractError(
                "optimized frequency cache/scientific metadata mismatch"
            )
    else:
        diagnostics = metadata.get("diagnostics")
        run_cache = (
            diagnostics.get("run_radial_cache")
            if isinstance(diagnostics, Mapping)
            else None
        )
        if (
            run_cache
            != {
                "enabled": True,
                "unique_solution_count": 358,
                "hit_count": FULL_IMAGE_OPTIMIZED_CACHE_HIT_COUNT,
                "key_count": 358,
            }
            or cache["ode_solve_count"] != 358
            or cache["oracle_solve_count"] != 0
            or cache["ode_oracle_solve_count"] != 358
            or cache["cache_hit_count"] != FULL_IMAGE_OPTIMIZED_CACHE_HIT_COUNT
            or cache["cache_miss_count"] != 358
            or cache["cache_rejection_count"] != 0
            or cache["cache_key_count"] != 358
        ):
            raise GateContractError(
                "optimized full-image cache/scientific metadata mismatch"
            )
    _validate_stage_profile(
        benchmark["stage_profile"],
        case_kind=case_kind,
        resource_record=resource_record,
        solve_count=cache["ode_oracle_solve_count"],
    )
    residual_maxima = benchmark.get("radial_residual_maxima")
    if not isinstance(residual_maxima, Mapping):
        raise GateContractError("optimized radial residual schema mismatch")
    validated_residuals = _validate_radial_residual_maxima(residual_maxima)
    if case_kind == "full-image":
        _validate_full_image_residual_binding(residual_maxima, metadata)
    transaction = sidecar.get("transaction")
    expected_transaction = {
        "schema_version": ATOMIC_SCHEMA_VERSION,
        "transaction_id": _transaction_id(frozen, paths),
        "state": "complete",
        "commit_order": ["npz", "sidecar"],
        "canonical_member_order": [paths.npz.name, paths.sidecar.name],
        "members": [
            {
                "name": paths.npz.name,
                "role": "payload",
                "sha256": npz_sha256,
            },
            {
                "name": paths.sidecar.name,
                "role": "commit_marker",
            },
        ],
        "npz_sha256": npz_sha256,
        "sidecar_is_commit_marker": True,
    }
    if transaction != expected_transaction:
        raise GateContractError("optimized transaction membership mismatch")
    _recheck_identity(frozen, phase=f"{paths.case_id}:post_audit")
    return {
        "event": "optimized_complete_pair_audit_passed",
        "case_id": paths.case_id,
        "state": "complete_matching_pair",
        "npz_path": str(paths.npz),
        "sidecar_path": str(paths.sidecar),
        "npz_sha256": npz_sha256,
        "sidecar_sha256": _sha256(paths.sidecar),
        "identity_sha256": frozen["identity"].canonical_digest,
        "comparison": comparison,
        "resource_record": resource_record,
        "stage_profile": benchmark["stage_profile"],
        "cache_metrics": cache,
        "radial_residual_maxima": dict(residual_maxima),
        "radial_residual_hard_gate": {
            "limits": {
                "boundary_residual": BOUNDARY_RESIDUAL_HARD_LIMIT,
                "wronskian_residual": WRONSKIAN_RESIDUAL_HARD_LIMIT,
                "flux_residual": FLUX_RESIDUAL_HARD_LIMIT,
            },
            "validated": validated_residuals,
            "passed": True,
        },
        "warning_counts": {
            "raw": benchmark["raw_warning_record"]["total_count"],
            "structured": benchmark["structured_warning_record"][
                "total_count"
            ],
        },
    }


def _case_resources(
    *,
    case_id: str,
    resource_record: Mapping[str, Any],
    solve_count: Any,
) -> CaseResources:
    required = (
        "wall_seconds",
        "user_cpu_seconds",
        "system_cpu_seconds",
        "peak_rss",
    )
    missing = [name for name in required if name not in resource_record]
    if missing:
        raise GateContractError(
            "resource record is incomplete: " + _canonical_json(missing)
        )
    if resource_record.get("peak_rss_unit") != "bytes_on_macos":
        raise GateContractError("resource peak-RSS unit mismatch")
    return CaseResources(
        case_id=case_id,
        wall_seconds=float(resource_record["wall_seconds"]),
        user_cpu_seconds=float(resource_record["user_cpu_seconds"]),
        system_cpu_seconds=float(resource_record["system_cpu_seconds"]),
        solve_count=solve_count,
        peak_rss_bytes=resource_record["peak_rss"],
    )


def _legacy_matrix_resources() -> tuple[CaseResources, ...]:
    records: list[CaseResources] = []
    for frequency in FROZEN_FREQUENCIES:
        token = FREQUENCY_TOKENS[frequency]
        audit = _audit_legacy_frequency(token)
        metadata = audit["metadata"]
        records.append(
            _case_resources(
                case_id=f"frequency:{token}",
                resource_record=metadata["resource_record"],
                solve_count=metadata["radial_solve_count"],
            )
        )
    full_audit = _audit_legacy_full_image()
    benchmark = full_audit["sidecar"]["benchmark_record"]
    records.append(
        _case_resources(
            case_id="full-image:241x241",
            resource_record=benchmark["resource_record"],
            solve_count=benchmark["cache_metrics"][
                "ode_oracle_solve_count"
            ],
        )
    )
    result = tuple(records)
    if tuple(record.case_id for record in result) != FROZEN_CASE_IDS:
        raise GateContractError("legacy matrix case identity/order mismatch")
    return result


def _optimized_matrix_resources(
    audits: Sequence[Mapping[str, Any]],
) -> tuple[CaseResources, ...]:
    records = tuple(
        _case_resources(
            case_id=str(audit["case_id"]),
            resource_record=audit["resource_record"],
            solve_count=audit["cache_metrics"]["ode_oracle_solve_count"],
        )
        for audit in audits
    )
    if tuple(record.case_id for record in records) != FROZEN_CASE_IDS:
        raise GateContractError("optimized matrix case identity/order mismatch")
    return records


def _equivalence_maxima(
    audits: Sequence[Mapping[str, Any]],
) -> dict[str, float]:
    names = (
        "max_absolute_difference",
        "max_normalized_relative_difference",
        "max_guarded_phase_difference_rad",
        "max_pixel_nrmse",
        "max_normalized_pixel_linf",
        "max_final_pair_delta_plus",
        "max_final_pair_delta_cross",
        "max_final_pair_delta_difference_plus",
        "max_final_pair_delta_difference_cross",
    )
    maxima: dict[str, float] = {}
    for name in names:
        values = []
        for audit in audits:
            comparison = audit["comparison"]["legacy"]
            if name in comparison:
                value = comparison[name]
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float, np.generic))
                    or not math.isfinite(float(value))
                    or float(value) < 0.0
                ):
                    raise GateContractError(
                        f"invalid equivalence maximum: {name}"
                    )
                values.append(float(value))
        if values:
            maxima[name] = max(values)
    required = {
        "max_absolute_difference",
        "max_normalized_relative_difference",
        "max_guarded_phase_difference_rad",
        "max_final_pair_delta_plus",
        "max_final_pair_delta_cross",
        "max_final_pair_delta_difference_plus",
        "max_final_pair_delta_difference_cross",
    }
    if not required.issubset(maxima):
        raise GateContractError("aggregate equivalence maxima are incomplete")
    return maxima


def _matrix_paths() -> tuple[ArtifactPaths, ...]:
    return tuple(
        _artifact_paths("frequency", frequency)
        for frequency in FROZEN_FREQUENCIES
    ) + (_artifact_paths("full-image", None),)


def _validate_cross_case_run_states(current: ArtifactPaths) -> None:
    unsafe: list[dict[str, Any]] = []
    for paths in _matrix_paths():
        if paths.case_id == current.case_id:
            continue
        state = _artifact_state(paths)
        if state["state"] in {"locked", "partial", "quarantined"}:
            unsafe.append(state)
    if unsafe:
        raise GateContractError(
            "another optimized case has unsafe atomic state: "
            + _canonical_json(unsafe)
        )


def _audit_matrix(frozen: Mapping[str, Any]) -> dict[str, Any]:
    _validate_output_scope()
    global_state = _require_global_idle()
    paths = _matrix_paths()
    states = tuple(_artifact_state(path) for path in paths)
    if any(state["state"] != "complete_pair" for state in states):
        raise GateContractError(
            "optimized exact-six matrix is incomplete or unsafe: "
            + _canonical_json(states)
        )
    audits = tuple(
        _audit_optimized_pair(frozen, path) for path in paths
    )
    if tuple(audit["case_id"] for audit in audits) != FROZEN_CASE_IDS:
        raise GateContractError("optimized audit case identity/order mismatch")
    legacy_resources = _legacy_matrix_resources()
    optimized_resources = _optimized_matrix_resources(audits)
    performance = evaluate_performance(legacy_resources, optimized_resources)
    residual_records = {
        audit["case_id"]: {
            "maxima": audit["radial_residual_maxima"],
            "hard_gate": audit["radial_residual_hard_gate"],
        }
        for audit in audits
    }
    return {
        "event": "optimized_exact_six_matrix_audit_passed",
        "case_ids": list(FROZEN_CASE_IDS),
        "pair_audits": list(audits),
        "equivalence_maxima": _equivalence_maxima(audits),
        "performance": asdict(performance),
        "performance_gate_passed": performance.passed,
        "residual_evidence": {
            "optimized_existing_hard_gates_passed": True,
            "full_image_legacy_worsening_comparison": "exact_metadata",
            "frequency_legacy_worsening_comparison": (
                "unavailable_in_immutable_legacy_baseline"
            ),
            "records": residual_records,
        },
        "legacy_resources": [
            asdict(record) for record in legacy_resources
        ],
        "optimized_resources": [
            asdict(record) for record in optimized_resources
        ],
        "global_runner_state": global_state,
        "frozen_contract": _preflight_payload(),
        "solver_started": False,
    }


def _preflight_case(
    frozen: Mapping[str, Any],
    *,
    case_kind: str,
    frequency: float | None,
) -> dict[str, Any]:
    _validate_output_scope()
    global_state = _require_global_idle()
    if case_kind == "matrix":
        if frequency is not None:
            raise GateContractError("matrix preflight accepts no frequency")
        legacy = {
            "frequencies": [
                {
                    key: audit[key]
                    for key in (
                        "token",
                        "npz_path",
                        "sidecar_path",
                        "golden_path",
                        "npz_sha256",
                        "sidecar_sha256",
                        "golden_sha256",
                    )
                }
                for audit in (
                    _audit_legacy_frequency(FREQUENCY_TOKENS[value])
                    for value in FROZEN_FREQUENCIES
                )
            ],
            "full_image": {
                key: value
                for key, value in _audit_legacy_full_image().items()
                if key
                in {
                    "npz_path",
                    "sidecar_path",
                    "golden_path",
                    "npz_sha256",
                    "sidecar_sha256",
                    "golden_sha256",
                }
            },
        }
        output_states = [
            _artifact_state(_artifact_paths("frequency", value))
            for value in FROZEN_FREQUENCIES
        ]
        output_states.append(
            _artifact_state(_artifact_paths("full-image", None))
        )
        unsafe = [
            state
            for state in output_states
            if state["state"] in {"locked", "partial", "quarantined"}
        ]
        if unsafe:
            raise GateContractError(
                "optimized matrix contains unsafe artifact state: "
                + _canonical_json(unsafe)
            )
        complete_audits = []
        for value in FROZEN_FREQUENCIES:
            paths = _artifact_paths("frequency", value)
            if _artifact_state(paths)["state"] == "complete_pair":
                complete_audits.append(_audit_optimized_pair(frozen, paths))
        full_paths = _artifact_paths("full-image", None)
        if _artifact_state(full_paths)["state"] == "complete_pair":
            complete_audits.append(
                _audit_optimized_pair(frozen, full_paths)
            )
        return {
            "event": "optimized_matrix_preflight_passed",
            "case_kind": "matrix",
            "legacy": legacy,
            "output_states": output_states,
            "complete_pair_audits": complete_audits,
            "global_runner_state": global_state,
            "frozen_contract": _preflight_payload(),
        }
    paths = _artifact_paths(case_kind, frequency)
    if case_kind == "frequency":
        legacy_record = _audit_legacy_frequency(
            FREQUENCY_TOKENS[float(frequency)]
        )
    else:
        legacy_record = _audit_legacy_full_image()
    state = _artifact_state(paths)
    if state["state"] in {"locked", "partial", "quarantined"}:
        raise GateContractError(
            "optimized case state is unsafe: " + _canonical_json(state)
        )
    record = {
        "event": "optimized_case_preflight_passed",
        "case_kind": case_kind,
        "case_id": paths.case_id,
        "legacy_identity": {
            key: legacy_record[key]
            for key in (
                "npz_path",
                "sidecar_path",
                "golden_path",
                "npz_sha256",
                "sidecar_sha256",
                "golden_sha256",
            )
        },
        "artifact_state": state,
        "global_runner_state": global_state,
        "frozen_contract": _preflight_payload(),
    }
    if state["state"] == "complete_pair":
        record["complete_pair_audit"] = _audit_optimized_pair(
            frozen,
            paths,
        )
    return record


def _run_case(
    frozen: Mapping[str, Any],
    *,
    case_kind: str,
    frequency: float | None,
    command: Sequence[str],
) -> dict[str, Any]:
    if case_kind not in {"frequency", "full-image"}:
        raise GateContractError("run mode requires one fixed case")
    paths = _artifact_paths(case_kind, frequency)
    _validate_output_scope()
    _validate_cross_case_run_states(paths)
    state = _artifact_state(paths)
    if state["state"] == "locked":
        lock = state["lock"]
        if lock is not None and not lock["owner_process_exists"]:
            lock_payload = lock["payload"]
            if (
                paths.npz.is_file()
                and paths.sidecar.is_file()
                and not _temporary_paths(paths)
                and not _quarantine_records(paths)
            ):
                try:
                    _validate_resume_lock_identity(
                        lock_payload,
                        frozen=frozen,
                        paths=paths,
                        command=command,
                    )
                    record = _audit_optimized_pair(
                        frozen,
                        paths,
                        allow_owned_lock=True,
                        owned_lock=lock_payload,
                    )
                except BaseException as exc:
                    _quarantine_artifacts(
                        paths,
                        reason=(
                            "stale-lock complete pair audit failed: "
                            f"{type(exc).__name__}: {exc}"
                        ),
                        runner_sha256=frozen["runner"]["sha256"],
                        include_lock=True,
                    )
                    raise GateContractError(
                        "stale-lock complete pair failed audit and was "
                        "quarantined"
                    ) from exc
                global_lock = _global_lock_record()
                if global_lock is not None:
                    if global_lock["owner_process_exists"]:
                        raise GateContractError(
                            "live global runner appeared during stale-lock "
                            "recovery"
                        )
                    global_payload = global_lock["payload"]
                    _validate_resume_lock_identity(
                        global_payload,
                        frozen=frozen,
                        paths=paths,
                        command=command,
                    )
                    shared_fields = (
                        "pid",
                        "case_id",
                        "identity_sha256",
                        "runner_sha256",
                        "implementation_commit",
                        "command",
                    )
                    if any(
                        global_payload.get(name) != lock_payload.get(name)
                        for name in shared_fields
                    ):
                        raise GateContractError(
                            "stale case/global lock identities disagree"
                        )
                _release_lock(paths, lock_payload)
                if global_lock is not None:
                    _release_global_lock(global_lock["payload"])
                record["event"] = (
                    "optimized_complete_matching_pair_recovered_after_"
                    "stale_lock"
                )
                record["solver_started"] = False
                record["stale_lock_recovered"] = True
                return record
            _quarantine_artifacts(
                paths,
                reason="stale lock with absent owner",
                runner_sha256=frozen["runner"]["sha256"],
                include_lock=True,
            )
            raise GateContractError(
                "stale lock was quarantined; anomaly review is required"
            )
        raise GateContractError("refusing a second live case runner")
    if state["state"] == "quarantined":
        raise GateContractError(
            "quarantined case evidence requires anomaly review"
        )
    if state["state"] == "partial":
        _quarantine_artifacts(
            paths,
            reason="pre-run partial atomic transaction",
            runner_sha256=frozen["runner"]["sha256"],
        )
        raise GateContractError(
            "partial transaction was quarantined; anomaly review is required"
        )
    if state["state"] == "complete_pair":
        _require_global_idle()
        try:
            record = _audit_optimized_pair(frozen, paths)
        except BaseException as exc:
            _quarantine_artifacts(
                paths,
                reason=(
                    "complete pair identity/audit mismatch: "
                    f"{type(exc).__name__}: {exc}"
                ),
                runner_sha256=frozen["runner"]["sha256"],
            )
            raise GateContractError(
                "mismatched complete pair was quarantined; no recomputation "
                "was started"
            ) from exc
        record["event"] = "optimized_complete_matching_pair_reused"
        record["solver_started"] = False
        return record

    global_owned_lock = _acquire_global_lock(
        frozen,
        case_id=paths.case_id,
        command=command,
    )
    try:
        owned_lock = _acquire_lock(paths, frozen, command)
    except BaseException:
        _release_global_lock(global_owned_lock)
        raise
    try:
        locked_state = _artifact_state(
            paths,
            allow_owned_lock=True,
            owned_lock=owned_lock,
        )
        if locked_state["state"] != "absent":
            raise GateContractError(
                "artifact state changed after lock acquisition"
            )
        print(
            _canonical_json(
                {
                    "event": "optimized_case_start",
                    "case_id": paths.case_id,
                    "identity_sha256": frozen[
                        "identity"
                    ].canonical_digest,
                    "implementation_commit": frozen["implementation"][
                        "commit"
                    ],
                }
            ),
            flush=True,
        )
        if case_kind == "frequency":
            run_record = _run_frequency_solver(
                frozen,
                float(frequency),
                command,
            )
        else:
            run_record = _run_full_image_solver(frozen, command)
        _commit_run_record(frozen, paths, run_record)
        audit = _audit_optimized_pair(
            frozen,
            paths,
            allow_owned_lock=True,
            owned_lock=owned_lock,
        )
        audit["event"] = "optimized_case_complete"
        audit["solver_started"] = True
        return audit
    except BaseException as exc:
        failed_state = _artifact_state(
            paths,
            allow_owned_lock=True,
            owned_lock=owned_lock,
        )
        if failed_state["state"] in {"partial", "complete_pair"}:
            _quarantine_artifacts(
                paths,
                reason=(
                    "run or post-write audit failed: "
                    f"{type(exc).__name__}: {exc}"
                ),
                runner_sha256=frozen["runner"]["sha256"],
            )
        raise
    finally:
        try:
            _release_lock(paths, owned_lock)
        finally:
            _release_global_lock(global_owned_lock)


def _audit_case(
    frozen: Mapping[str, Any],
    *,
    case_kind: str,
    frequency: float | None,
) -> dict[str, Any]:
    if case_kind == "matrix":
        if frequency is not None:
            raise GateContractError("matrix audit accepts no frequency")
        return _audit_matrix(frozen)
    paths = _artifact_paths(case_kind, frequency)
    return _audit_optimized_pair(frozen, paths)


def validate_frozen_frequency_request(frequencies: Sequence[float]) -> None:
    requested = tuple(float(value) for value in frequencies)
    if requested != FROZEN_FREQUENCIES:
        raise GateContractError(
            "request must equal the exact frozen frequency matrix in exact order"
        )


def validate_frozen_frequency(frequency: float) -> float:
    value = float(frequency)
    if value not in FREQUENCY_TOKENS:
        raise GateContractError("frequency must be one of the five frozen values")
    return value


def _preflight_payload() -> dict[str, Any]:
    validate_frozen_frequency_request(FROZEN_FREQUENCIES)
    return {
        "boundary": dict(BOUNDARY_CONTRACT),
        "frequency_case_count": FREQUENCY_CASE_COUNT,
        "frequencies": list(FROZEN_FREQUENCIES),
        "full_image_resolution": list(FULL_IMAGE_RESOLUTION),
        "full_image_valid_count": FULL_IMAGE_VALID_COUNT,
        "full_image_masked_count": FULL_IMAGE_MASKED_COUNT,
        "full_image_convergence_probe_count": FULL_IMAGE_CONVERGENCE_PROBE_COUNT,
        "diagnostic_failed_child_midpoint_count": (
            DIAGNOSTIC_FAILED_CHILD_MIDPOINT_COUNT
        ),
        "scientific_thresholds_unchanged": True,
        "spin2_theory_implemented_or_validated": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Frozen T4ae optimized methods benchmark/preflight/audit runner. "
            "It accepts only five existing frequency cases or the fixed "
            "241x241 full-image case."
        )
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=("preflight", "run", "audit"),
    )
    parser.add_argument(
        "--case",
        required=True,
        choices=("matrix", "frequency", "full-image"),
    )
    parser.add_argument(
        "--frequency",
        type=float,
        help="One exact frozen kM value; valid only for --case frequency.",
    )
    parser.add_argument(
        "--expected-self-sha256",
        required=True,
        help="Mandatory SHA-256 of this exact committed runner.",
    )
    parser.add_argument(
        "--expected-implementation-commit",
        required=True,
        help="Mandatory exact-fourteen-path implementation commit.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        choices=(1, 2),
        default=1,
        help=(
            "Bounded orchestration contract. Each fixed scientific case is "
            "currently executed serially."
        ),
    )
    arguments = parser.parse_args(argv)
    if arguments.case == "frequency":
        if arguments.frequency is None:
            parser.error("--case frequency requires --frequency")
        frequency = validate_frozen_frequency(arguments.frequency)
    else:
        if arguments.frequency is not None:
            parser.error("--frequency is valid only with --case frequency")
        frequency = None
    if arguments.case == "matrix" and arguments.mode == "run":
        parser.error("--case matrix is not available in --mode run")

    frozen = _frozen_identity(
        arguments.expected_self_sha256,
        arguments.expected_implementation_commit,
    )
    command = [
        str(Path(__file__).resolve()),
        "--mode",
        arguments.mode,
        "--case",
        arguments.case,
    ]
    if frequency is not None:
        command.extend(("--frequency", repr(frequency)))
    command.extend(
        (
            "--expected-self-sha256",
            arguments.expected_self_sha256,
            "--expected-implementation-commit",
            arguments.expected_implementation_commit,
            "--max-workers",
            str(arguments.max_workers),
        )
    )
    if arguments.mode == "preflight":
        record = _preflight_case(
            frozen,
            case_kind=arguments.case,
            frequency=frequency,
        )
        record["solver_started"] = False
    elif arguments.mode == "audit":
        record = _audit_case(
            frozen,
            case_kind=arguments.case,
            frequency=frequency,
        )
        record["solver_started"] = False
    else:
        record = _run_case(
            frozen,
            case_kind=arguments.case,
            frequency=frequency,
            command=command,
        )
    record["runner_sha256"] = frozen["runner"]["sha256"]
    record["implementation_commit"] = frozen["implementation"]["commit"]
    record["identity_sha256"] = frozen["identity"].canonical_digest
    record["max_workers_contract"] = arguments.max_workers
    print(_canonical_json(record), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
