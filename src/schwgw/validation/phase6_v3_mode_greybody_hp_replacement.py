"""V3.1-U replacement orchestration, publication, and validation.

The predecessor cycle-2 module is a read-only dependency for the unchanged
Route-A/B/C science.  This module adds only the independently routed
high-precision S-deficit branch and a fresh terminal artifact protocol.
"""

from __future__ import annotations

from datetime import UTC, datetime
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import time
from typing import Any, Mapping, Sequence

import mpmath as mp

from schwgw.validation.phase6_v3_hp_unitarity_oracle import (
    OracleMode,
    gamma_decimal_value,
    independent_geometry,
    precision_schedule,
    solve_oracle_node,
    validate_oracle_ladder,
)
from schwgw.validation.phase6_v3_mode_greybody import (
    ModeKey,
    ROOT,
    V31ContractError,
    build_inventory_payload,
    build_mode_inventory,
    canonical_bytes,
    sha256,
)
from schwgw.validation import phase6_v3_mode_greybody_cycle2 as cycle2


GATE_ID = "phase6_v3_1_hp_unitarity_deficit_replacement_v1"
ARTIFACT_REV = 1
OFFICIAL_ROOT_PARENT = ROOT / "runs/phase6/classic_scattering"
OFFICIAL_ROOT_PATTERN = re.compile(
    r"v3_1_hp_unitarity_deficit_repair2_v1_"
    r"(?P<timestamp>\d{8}T\d{6}Z)_py314"
)
SENTINEL_ROOT_PATTERN = re.compile(
    r"v3_1_u_route_c_sentinel_repair2_v1_"
    r"(?P<timestamp>\d{8}T\d{6}Z)_py314"
)
PACKAGE_PATH = ROOT / "configs/phase6_v3_1_hp_unitarity_replacement_package.json"
PACKAGE_SHA256 = "decde34bcdc90db0bc69be446357e306cfe942c84a8d575902eddaa7d1ff6877"
DESIGN_PATH = ROOT / "docs/phase6_v3_1_hp_unitarity_replacement_design.md"
DESIGN_SHA256 = "243f312182528b10a895cef679d195dcedfd97d7a2e02e388449ae3af313dd28"
T4_PROMPT_PATH = ROOT / "docs/prompts/phase6_t4_v3_1_hp_unitarity_replacement.md"
T4_PROMPT_SHA256 = "a1bffc42a381489dadd483edf2e6952d97ce236fbad3fe9ca82eb8b0ca862945"
T7_REVIEW_PROMPT_PATH = ROOT / "docs/prompts/phase6_t7_v3_1_hp_unitarity_review.md"
T7_REVIEW_PROMPT_SHA256 = (
    "8822263a09bde6d5b0bd3b2c00117eb5ac1648ae9f804a4e71380b27fa90cb82"
)
T7_APPROVAL_PATH = (
    ROOT / "docs/handoffs/archive/T7_2026-08-11_v3_1_hp_unitarity_package_review.md"
)
T7_APPROVAL_SHA256 = "9616b3fb4d0999e782e164740f5815f6bcdf46a955910cd2bcfcae032bde75cf"
REPAIR_PACKAGE_PATH = ROOT / "configs/phase6_v3_1_u_repair_cycle1_package.json"
REPAIR_PACKAGE_SHA256 = (
    "85bff01def7286ebaf1682d5b5498209dfbbc452e098e1d8633e05fcc1b7554c"
)
REPAIR_PACKAGE_REVIEW_PATH = (
    ROOT / "docs/handoffs/archive/T7_2026-08-12_v3_1_u_repair_cycle1_package_review.md"
)
REPAIR_PACKAGE_REVIEW_SHA256 = (
    "cfaf87f79cf11a9f6c0f8a73dd3faa3517cd15c105afe999cdfa687c2c5160b4"
)
TERMINAL_REVIEW_PATH = (
    ROOT
    / "docs/handoffs/archive/T7_2026-08-12_v3_1_u_terminal_scientific_failure_review.md"
)
TERMINAL_REVIEW_SHA256 = (
    "7aa90e012e7d079d7c16256647d97db663293cf9ff6f5a4346130aa1d82482f1"
)
CLARIFICATION_PATH = (
    ROOT
    / "docs/handoffs/archive/T7_2026-08-12_v3_1_u_terminal_scientific_failure_control_plane_clarification.md"
)
CLARIFICATION_SHA256 = (
    "2f661f45dc609f6f92bb475060d5860586df3a916de8acefbab5f539f8850da0"
)
FAILED_ROOT = (
    ROOT
    / "runs/phase6/classic_scattering/v3_1_hp_unitarity_deficit_v1_20260811T143911Z_py314"
)
FAILED_IDENTITIES = {
    "failure.json": "5aef8aec8511e5fa35df6459b7cd520b046e080d43f6c24fd95a8b46379d1779",
    "failure_manifest.json": (
        "6a8ab79495bad03c2d08742a6a6b79f3afc6df658eb7d7dcb20f145efa905b1e"
    ),
    "route_u_records.jsonl": (
        "645e2e116b13dbc1c70e7be1db06f3827a04ccd723e6093ffac8b06199e56c2b"
    ),
    "route_u_ladders.jsonl": (
        "d7c1381fd0e51f439056350de90022ddc8aaf1808e72ee736b304ef10b2a5537"
    ),
}
REPAIR2_PACKAGE_PATH = ROOT / "configs/phase6_v3_1_u_repair_cycle2_package.json"
REPAIR2_PACKAGE_SHA256 = (
    "61460a45d4d47ba9247e68969a5d91e2d77aac722c9324014a414ed4126dbfa2"
)
REPAIR2_DESIGN_PATH = ROOT / "docs/phase6_v3_1_u_repair_cycle2_design.md"
REPAIR2_DESIGN_SHA256 = (
    "ce57d7e8fd6cc4fc61398e448260368662d9aa39da2d53ec4e1342b84d4d0029"
)
REPAIR2_T4_PROMPT_PATH = ROOT / "docs/prompts/phase6_t4_v3_1_u_repair_cycle2.md"
REPAIR2_T4_PROMPT_SHA256 = (
    "8287aaff8564554a56bc3cc673c825019f8ead955612eae33ab3543c4b208e80"
)
REPAIR2_PACKAGE_REVIEW_PATH = (
    ROOT
    / "docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle2_package_delta_recheck_1.md"
)
REPAIR2_PACKAGE_REVIEW_SHA256 = (
    "f67ce9fa3f0b3f65a7ad34c736c06236f1b0c87674a0e943e8b749f1ca9387e5"
)
SENTINEL_ENVIRONMENT_AUTHORITY_PATH = (
    ROOT / "configs/phase6_v3_1_u_repair_cycle2_sentinel_environment_authority.json"
)
SENTINEL_ENVIRONMENT_AUTHORITY_SHA256 = (
    "936e4a403030d96ce4575e35fbefdff7d6eb29acaad564c137488a27aabec581"
)
SENTINEL_ENVIRONMENT_REVIEW_PATH = (
    ROOT / "docs/handoffs/archive/"
    "T7_2026-08-13_v3_1_u_repair_cycle2_environment_clarification_review.md"
)
SENTINEL_ENVIRONMENT_REVIEW_SHA256 = (
    "f30bff27a4e39d9959cc5b50fd3abe790490c0180f278a583832ca6e2d4016f6"
)
REPAIR2_IMPLEMENTATION_RECHECK1_PATH = (
    ROOT / "docs/handoffs/archive/"
    "T7_2026-08-13_v3_1_u_repair_cycle2_implementation_delta_recheck_1.md"
)
REPAIR2_IMPLEMENTATION_RECHECK1_SHA256 = (
    "c5f827cbbc61c413d269c611e34cf72c72433a63752e71dcace21f670cec4210"
)
FINAL_IMPLEMENTATION_REVIEW_RELATIVE_PATH = (
    "docs/handoffs/archive/"
    "T7_2026-08-13_v3_1_u_repair_cycle2_implementation_delta_recheck_2.md"
)
IMPLEMENTATION_REVIEW_PATH = ROOT / FINAL_IMPLEMENTATION_REVIEW_RELATIVE_PATH
SENTINEL_REVIEW_PATH = (
    ROOT / "docs/handoffs/archive/T7_2026-08-13_v3_1_u_repair_cycle2_sentinel_review.md"
)
SENTINEL_DISPATCH_PATH = (
    ROOT
    / "docs/handoffs/archive/T0_2026-08-13_v3_1_u_repair_cycle2_sentinel_dispatch_attempt_0001.json"
)
DISPATCH_PATH = (
    ROOT
    / "docs/handoffs/archive/T0_2026-08-13_v3_1_u_repair_cycle2_official_dispatch_attempt_0001.json"
)
REPAIR1_ALLOWED_IMPLEMENTATION_PATHS = (
    "src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py",
    "src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py",
    "tests/regression/test_phase6_v3_hp_unitarity_publication.py",
    "tests/unit/test_phase6_v3_hp_unitarity.py",
)
ALLOWED_IMPLEMENTATION_PATHS = (
    "scripts/phase6_v3_1_bhpt_mst_cycle2.wls",
    "src/schwgw/validation/phase6_v3_mode_greybody_cycle2.py",
    "src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py",
    "tests/regression/test_phase6_v3_hp_unitarity_publication.py",
    "tests/unit/test_phase6_v3_cycle2.py",
    "tests/unit/test_phase6_v3_hp_unitarity.py",
)
IMPLEMENTATION_REVIEW_TOKENS = (
    "ADVANCE_DECISION: ADVANCE",
    "CLAIM_STATUS: NOT_ASSESSED",
    "ACCEPT GREEN / V3.1-U REPAIR CYCLE 2 IMPLEMENTATION READY FOR ONE-SHOT ROUTE-C SENTINEL",
)
SENTINEL_REVIEW_TOKENS = (
    "ADVANCE_DECISION: ADVANCE",
    "ACCEPT GREEN / V3.1-U ROUTE-C SENTINEL SUFFICIENT FOR ONE-USE OFFICIAL DISPATCH",
)
SENTINEL_EXECUTABLE = Path(
    "/opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/"
    "Python.framework/Versions/3.14/bin/python3.14"
)
SENTINEL_INVOCATION = {
    "schema": "schwo.phase6.v3_1_u.route_c_sentinel_invocation.v1",
    "executable": str(SENTINEL_EXECUTABLE),
    "argv": [
        str(SENTINEL_EXECUTABLE),
        "-m",
        "schwgw.validation.phase6_v3_mode_greybody_hp_replacement",
        "route-c-sentinel",
    ],
    "cwd": str(ROOT),
    "environment_allowlist": {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": "runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src",
    },
}
ROUTE_MAP_SCHEMA = "schwo.phase6.v3_1_u.route_map.v1"
SELECTOR_LOG_THRESHOLD = mp.log(mp.mpf("1e-8"))
EXPECTED_FIXED_COUNTS = {
    "route_a_modes": 496,
    "route_a_nodes": 9920,
    "route_b_keys": 102,
    "route_b_nodes": 458,
    "route_c_records": 23,
    "thresholds": 16,
    "certificates": 5,
}


def _sentinel_environment_authority_binding() -> dict[str, str]:
    return {
        "path": str(SENTINEL_ENVIRONMENT_AUTHORITY_PATH),
        "sha256": SENTINEL_ENVIRONMENT_AUTHORITY_SHA256,
    }


def _load_sentinel_environment_authority() -> dict[str, Any]:
    """Reload and validate the non-circular requested/observed environment authority."""

    identity = _file_identity(SENTINEL_ENVIRONMENT_AUTHORITY_PATH)
    if (
        identity["sha256"] != SENTINEL_ENVIRONMENT_AUTHORITY_SHA256
        or identity["mode"] != 0o444
        or identity["nlink"] != 1
    ):
        raise V31ContractError("sentinel environment authority identity drift")
    authority = json.loads(SENTINEL_ENVIRONMENT_AUTHORITY_PATH.read_text())
    if SENTINEL_ENVIRONMENT_AUTHORITY_PATH.read_bytes() != canonical_bytes(authority):
        raise V31ContractError("sentinel environment authority is not canonical")
    requested = authority.get("requested_environment", {}).get("exact_execve_map")
    observed = authority.get("observed_environment", {}).get("exact_post_startup_map")
    boundary = authority.get("execution_boundary", {})
    launcher = boundary.get("launcher", {})
    python = authority.get("platform_identity", {}).get("python", {})
    expected_observed = {
        "LC_CTYPE": "C.UTF-8",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": (
            "runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src"
        ),
        "__CF_USER_TEXT_ENCODING": "0x1F5:0x19:0x34",
    }
    expected_launcher = {
        "path": "/usr/bin/env",
        "sha256": "6e506aec3c0cff703ac1e66cedc6f1945354ad41339a38db4425c7c88227128f",
        "size": 102368,
        "argv_prefix": [
            "/usr/bin/env",
            "-i",
            "PYTHONDONTWRITEBYTECODE=1",
            "PYTHONPATH=runs/phase5/paper_figures/runtime_overlays/"
            "mpmath_1p4p1_py314:src",
        ],
    }
    expected_python = {
        "path": str(SENTINEL_EXECUTABLE),
        "sha256": "b502cb4c5b46b8d4192ec6bcb600ce8922f1afc396fcf646e8765c6eba74a0bf",
        "size": 52448,
        "version": "3.14.6",
    }
    expected_allowed = (
        "src/schwgw/validation/phase6_v3_mode_greybody_hp_replacement.py",
        "tests/regression/test_phase6_v3_hp_unitarity_publication.py",
        "tests/unit/test_phase6_v3_hp_unitarity.py",
    )
    expected_unchanged = {
        "scripts/phase6_v3_1_bhpt_mst_cycle2.wls": (
            "894bb2ebe6bd9637e3e449e7785241085de0f673ad93ebbf7865c4a5023b888f"
        ),
        "src/schwgw/validation/phase6_v3_mode_greybody_cycle2.py": (
            "60fdc7c3f46ab21eafbe2b319f0c7b15b3ab64d6633d360f79ada078dcbd36b1"
        ),
        "tests/unit/test_phase6_v3_cycle2.py": (
            "47e29bf2ee0c900aaff1153ebee31848916b8c94b5de7e488220ef0f457b5323"
        ),
    }
    if (
        authority.get("schema")
        != "schwo.phase6.v3_1_u.repair_cycle2_sentinel_environment_authority.v1"
        or requested != SENTINEL_INVOCATION["environment_allowlist"]
        or observed != expected_observed
        or boundary.get("executable") != SENTINEL_INVOCATION["executable"]
        or boundary.get("argv") != SENTINEL_INVOCATION["argv"]
        or boundary.get("cwd") != SENTINEL_INVOCATION["cwd"]
        or launcher != expected_launcher
        or python != expected_python
        or tuple(
            authority.get("frozen_invariants", {}).get(
                "allowed_implementation_paths", ()
            )
        )
        != expected_allowed
        or authority.get("frozen_invariants", {}).get("unchanged_passed_paths")
        != expected_unchanged
        or authority.get("implementation_contract", {}).get(
            "future_final_implementation_review_path"
        )
        != FINAL_IMPLEMENTATION_REVIEW_RELATIVE_PATH
        or tuple(
            authority.get("implementation_contract", {}).get(
                "future_required_verdict_tokens", ()
            )
        )
        != IMPLEMENTATION_REVIEW_TOKENS
    ):
        raise V31ContractError("sentinel environment authority semantics drift")
    observed_bytes = (
        json.dumps(observed, sort_keys=True, separators=(",", ":")).encode("utf-8")
        + b"\n"
    )
    if (
        hashlib.sha256(observed_bytes).hexdigest()
        != authority["observed_environment"]["exact_post_startup_map_canonical_sha256"]
    ):
        raise V31ContractError("sentinel observed-environment digest drift")
    for path_value, expected in (
        (Path(launcher["path"]), launcher),
        (Path(python["path"]), python),
    ):
        live = _file_identity(path_value)
        if live["sha256"] != expected["sha256"] or live["size"] != expected["size"]:
            raise V31ContractError("sentinel environment runtime identity drift")
    return authority


def verify_start_gate() -> dict[str, Any]:
    """Rehash the immutable implementation-stage authority chain."""

    for path, expected in (
        (PACKAGE_PATH, PACKAGE_SHA256),
        (REPAIR_PACKAGE_PATH, REPAIR_PACKAGE_SHA256),
        (REPAIR2_PACKAGE_PATH, REPAIR2_PACKAGE_SHA256),
    ):
        if _file_identity(path)["sha256"] != expected:
            raise V31ContractError(f"V3.1-U frozen identity drift: {path}")
    package = json.loads(PACKAGE_PATH.read_text())
    repair_package = json.loads(REPAIR_PACKAGE_PATH.read_text())
    repair2_package = json.loads(REPAIR2_PACKAGE_PATH.read_text())
    fixed: dict[Path, str] = {
        PACKAGE_PATH: PACKAGE_SHA256,
        DESIGN_PATH: DESIGN_SHA256,
        T4_PROMPT_PATH: T4_PROMPT_SHA256,
        T7_REVIEW_PROMPT_PATH: T7_REVIEW_PROMPT_SHA256,
        T7_APPROVAL_PATH: T7_APPROVAL_SHA256,
        REPAIR_PACKAGE_PATH: REPAIR_PACKAGE_SHA256,
        REPAIR_PACKAGE_REVIEW_PATH: REPAIR_PACKAGE_REVIEW_SHA256,
        TERMINAL_REVIEW_PATH: TERMINAL_REVIEW_SHA256,
        CLARIFICATION_PATH: CLARIFICATION_SHA256,
        REPAIR2_PACKAGE_PATH: REPAIR2_PACKAGE_SHA256,
        REPAIR2_DESIGN_PATH: REPAIR2_DESIGN_SHA256,
        REPAIR2_T4_PROMPT_PATH: REPAIR2_T4_PROMPT_SHA256,
        REPAIR2_PACKAGE_REVIEW_PATH: REPAIR2_PACKAGE_REVIEW_SHA256,
        SENTINEL_ENVIRONMENT_AUTHORITY_PATH: SENTINEL_ENVIRONMENT_AUTHORITY_SHA256,
        SENTINEL_ENVIRONMENT_REVIEW_PATH: SENTINEL_ENVIRONMENT_REVIEW_SHA256,
        REPAIR2_IMPLEMENTATION_RECHECK1_PATH: REPAIR2_IMPLEMENTATION_RECHECK1_SHA256,
    }
    fixed.update(
        {
            ROOT / item["path"]: item["sha256"]
            for item in repair_package["members"]
            if item["path"] not in ALLOWED_IMPLEMENTATION_PATHS
        }
    )
    fixed.update(
        {
            ROOT / path: digest
            for path, digest in repair_package["source_bindings"].items()
            if path not in ALLOWED_IMPLEMENTATION_PATHS
        }
    )
    failed_name_map = {
        "failure_json_sha256": "failure.json",
        "failure_manifest_sha256": "failure_manifest.json",
        "records_sha256": "records.jsonl",
        "ladder_records_sha256": "ladder_records.jsonl",
        "route_u_records_sha256": "route_u_records.jsonl",
        "route_u_ladders_sha256": "route_u_ladders.jsonl",
        "ap_records_sha256": "ap_records.jsonl",
        "external_request_sha256": "external_raw.request.json",
    }
    for failed in repair2_package["failed_evidence"].values():
        failed_root = ROOT / failed["root"]
        for field, filename in failed_name_map.items():
            if field in failed:
                fixed[failed_root / filename] = failed[field]
    fixed.update(
        {
            ROOT / path: digest
            for path, digest in repair_package["protected_radial_identities"].items()
        }
    )
    fixed.update(
        {FAILED_ROOT / name: digest for name, digest in FAILED_IDENTITIES.items()}
    )
    fixed.update(
        {ROOT / item["path"]: item["sha256"] for item in repair2_package["members"]}
    )
    fixed.update(
        {
            ROOT / path: digest
            for path, digest in repair2_package["source_bindings"].items()
        }
    )
    fixed.update(
        {
            ROOT / path: digest
            for path, digest in repair2_package["protected_radial_identities"].items()
        }
    )
    identities: dict[str, Any] = {}
    for path, expected in fixed.items():
        resolved = path.resolve(strict=True)
        info = resolved.stat()
        if (
            sha256(resolved) != expected
            or not stat.S_ISREG(info.st_mode)
            or info.st_nlink != 1
            or path.is_symlink()
        ):
            raise V31ContractError(f"V3.1-U frozen identity drift: {path}")
        identities[str(path)] = _file_identity(resolved)
    approval = T7_APPROVAL_PATH.read_text()
    if not all(
        text in approval
        for text in (
            "ADVANCE_DECISION: ADVANCE",
            "CLAIM_STATUS: NOT_ASSESSED",
            "ACCEPT GREEN / V3.1-U REPLACEMENT PACKAGE READY FOR T4",
            PACKAGE_SHA256,
        )
    ):
        raise V31ContractError("formal T7 V3.1-U package approval mismatch")
    repair_approval = REPAIR_PACKAGE_REVIEW_PATH.read_text()
    if not all(
        text in repair_approval
        for text in (
            "ADVANCE_DECISION: ADVANCE",
            "CLAIM_STATUS: NOT_ASSESSED",
            "ACCEPT GREEN / V3.1-U REPAIR CYCLE 1 PACKAGE READY FOR T4",
            REPAIR_PACKAGE_SHA256,
        )
    ):
        raise V31ContractError("formal T7 repair-package approval mismatch")
    terminal_review = TERMINAL_REVIEW_PATH.read_text()
    if not all(
        text in terminal_review
        for text in (
            "ADVANCE_DECISION: REPAIR",
            "CLAIM_STATUS: FAIL",
            "v31u_auxiliary_radius_closed_boundary_roundoff",
            FAILED_IDENTITIES["failure.json"],
        )
    ):
        raise V31ContractError("terminal scientific-review authority mismatch")
    clarification = CLARIFICATION_PATH.read_text()
    if not all(
        text in clarification
        for text in (
            "CONTROL_PLANE_REPAIR",
            *REPAIR1_ALLOWED_IMPLEMENTATION_PATHS,
            FAILED_IDENTITIES["route_u_records.jsonl"],
            FAILED_IDENTITIES["route_u_ladders.jsonl"],
        )
    ):
        raise V31ContractError("terminal control-plane clarification mismatch")
    if (
        repair_package.get("schema") != "schwo.phase6.v3_1_u.repair_cycle1_package.v1"
        or tuple(repair_package["implementation_scope"]["allowed_unique_paths"])
        != REPAIR1_ALLOWED_IMPLEMENTATION_PATHS
        or repair_package["frozen_cli"]
        != {
            "path": "scripts/phase6_v3_1_hp_unitarity.py",
            "sha256": "01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4",
        }
    ):
        raise V31ContractError("repair-package semantics mismatch")
    repair2_approval = REPAIR2_PACKAGE_REVIEW_PATH.read_text()
    if not all(
        token in repair2_approval
        for token in (
            "ADVANCE_DECISION: ADVANCE",
            "CLAIM_STATUS: NOT_ASSESSED",
            "ACCEPT GREEN / V3.1-U REPAIR CYCLE 2 PACKAGE READY FOR T4",
            REPAIR2_PACKAGE_SHA256,
        )
    ):
        raise V31ContractError("formal T7 repair-2 package approval mismatch")
    environment_review = SENTINEL_ENVIRONMENT_REVIEW_PATH.read_text()
    if not all(
        token in environment_review
        for token in (
            "ADVANCE_DECISION: ADVANCE",
            "CLAIM_STATUS: NOT_ASSESSED",
            "ACCEPT GREEN / V3.1-U REPAIR CYCLE 2 ENVIRONMENT CLARIFICATION READY FOR T4",
            SENTINEL_ENVIRONMENT_AUTHORITY_SHA256,
            REPAIR2_IMPLEMENTATION_RECHECK1_SHA256,
        )
    ):
        raise V31ContractError("formal sentinel-environment review mismatch")
    environment_authority = _load_sentinel_environment_authority()
    if (
        repair2_package.get("repair_id")
        != "phase6_v3_1_u_route_c_totality_repair_cycle2_v1"
        or tuple(repair2_package["implementation_scope"]["allowed_unique_paths"])
        != ALLOWED_IMPLEMENTATION_PATHS
    ):
        raise V31ContractError("repair-2 package semantics mismatch")
    geometry = geometry_preflight()
    return {
        "package": package,
        "repair_package": repair_package,
        "repair2_package": repair2_package,
        "sentinel_environment_authority": environment_authority,
        "identities": identities,
        "package_start_predecessors": repair_package["frozen_predecessor_identities"],
        "geometry_preflight": geometry,
    }


def selector_view(
    mode_record: Mapping[str, Any], *, ordinal: int, record_sha256: str
) -> dict[str, Any]:
    """Extract the only fields the frozen Route-U selector is allowed to read."""

    baseline = mode_record["baseline"]
    return {
        "ordinal": ordinal,
        "mode": dict(mode_record["mode"]),
        "Gamma_flux_decimal": dict(baseline["Gamma_flux_decimal"]),
        "log_Gamma_flux": str(baseline["log_Gamma_flux"]),
        "source_record_sha256": record_sha256,
    }


def build_route_map(selector_views: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Build the exact 496-entry direct-flux-only selector map."""

    expected_modes = [key.payload() for key in build_mode_inventory()]
    if len(selector_views) != 496:
        raise V31ContractError("Route-U selector view cardinality mismatch")
    entries: list[dict[str, Any]] = []
    for ordinal, (view, expected_mode) in enumerate(
        zip(selector_views, expected_modes)
    ):
        if set(view) != {
            "ordinal",
            "mode",
            "Gamma_flux_decimal",
            "log_Gamma_flux",
            "source_record_sha256",
        }:
            raise V31ContractError("Route-U selector view schema mismatch")
        if view["ordinal"] != ordinal or view["mode"] != expected_mode:
            raise V31ContractError("Route-U selector view order mismatch")
        gamma = gamma_decimal_value(view["Gamma_flux_decimal"])
        direct_log = mp.mpf(view["log_Gamma_flux"])
        if not mp.isfinite(direct_log) or abs(mp.log(gamma) - direct_log) > mp.mpf(
            "2e-12"
        ):
            raise V31ContractError("Route-A direct Gamma decimal/log inconsistency")
        decision = direct_log < SELECTOR_LOG_THRESHOLD
        entries.append(
            {
                "ordinal": ordinal,
                "mode": expected_mode,
                "source_record_sha256": view["source_record_sha256"],
                "selector": {
                    "field": "direct Route-A log_Gamma_flux",
                    "operator": "<",
                    "threshold": "-18.42068074395236547214393163747491366",
                    "operand": str(view["log_Gamma_flux"]),
                    "Gamma_flux_decimal": dict(view["Gamma_flux_decimal"]),
                    "use_route_u": decision,
                    "branch": "small_gamma_route_u"
                    if decision
                    else "large_gamma_float64",
                },
            }
        )
    return {
        "schema": ROUTE_MAP_SCHEMA,
        "gate_id": GATE_ID,
        "selector_contract": "direct Route-A log_Gamma_flux < log(1e-8)",
        "selector_forbidden_inputs": [
            "S",
            "Gamma_S",
            "route mismatch or residual",
            "threshold outcome",
            "regime label",
            "Route-B/AP result",
            "Route-C/external result",
        ],
        "frozen_before_route_u": True,
        "entry_count": 496,
        "route_u_count": sum(item["selector"]["use_route_u"] for item in entries),
        "entries": entries,
    }


def validate_route_map(payload: Mapping[str, Any]) -> None:
    if (
        payload.get("schema") != ROUTE_MAP_SCHEMA
        or payload.get("entry_count") != 496
        or payload.get("frozen_before_route_u") is not True
    ):
        raise V31ContractError("Route-U map header mismatch")
    rebuilt_views = [
        {
            "ordinal": item["ordinal"],
            "mode": item["mode"],
            "Gamma_flux_decimal": item["selector"]["Gamma_flux_decimal"],
            "log_Gamma_flux": item["selector"]["operand"],
            "source_record_sha256": item["source_record_sha256"],
        }
        for item in payload["entries"]
    ]
    if build_route_map(rebuilt_views) != payload:
        raise V31ContractError("Route-U map reconstruction mismatch")


def geometry_preflight() -> dict[str, Any]:
    """Rebuild all frozen Route-U geometry nodes without a solver call."""

    manifest_path = FAILED_ROOT / "failure_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    route_map_path = FAILED_ROOT / "unitarity_route_map.json"
    if manifest.get("overall_state") != "FAILED" or manifest.get("artifacts", {}).get(
        "unitarity_route_map.json"
    ) != _file_identity(route_map_path):
        raise V31ContractError("failed Route-U map identity is not authenticated")
    route_map = json.loads(route_map_path.read_text())
    validate_route_map(route_map)
    routed = [item for item in route_map["entries"] if item["selector"]["use_route_u"]]
    if len(routed) != 318:
        raise V31ContractError("frozen Route-U geometry key count mismatch")

    def build_nodes() -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        for entry in routed:
            schedule = precision_schedule(entry["selector"]["Gamma_flux_decimal"])
            for precision_ordinal, dps in enumerate(schedule):
                with mp.workdps(dps):
                    mode = entry["mode"]
                    k = mp.mpf(mode["kM"])
                    l2 = int(mode["ell"]) * (int(mode["ell"]) + 1)
                    match_radius = max(mp.mpf(300), mp.sqrt(l2) / k)
                    outer_radius, exponent = independent_geometry(
                        ell=int(mode["ell"]),
                        k=k,
                        k_decimal=mode["kM"],
                        match_radius=match_radius,
                    )
                    nodes.append(
                        {
                            "mode_ordinal": entry["ordinal"],
                            "mode": dict(mode),
                            "precision_ordinal": precision_ordinal,
                            "dps": dps,
                            "auxiliary_exponent": exponent,
                            "match_radius": mp.nstr(match_radius, dps),
                            "outer_radius": mp.nstr(outer_radius, dps),
                        }
                    )
        return nodes

    with mp.workdps(37):
        nodes_low_ambient = build_nodes()
    with mp.workdps(301):
        nodes_high_ambient = build_nodes()
    if nodes_low_ambient != nodes_high_ambient or len(nodes_low_ambient) != 954:
        raise V31ContractError("Route-U geometry is ambient-precision dependent")
    failed_key_nodes = [
        item
        for item in nodes_low_ambient
        if item["mode"]["ell"] == 10
        and item["mode"]["kM"] == "0.005"
        and item["mode"]["parity"] == "odd"
    ]
    if [item["dps"] for item in failed_key_nodes] != [120, 160, 220] or [
        item["auxiliary_exponent"] for item in failed_key_nodes
    ] != [2, 2, 2]:
        raise V31ContractError("original failed Route-U geometry key is not closed")
    inventory_bytes = json.dumps(
        nodes_low_ambient, sort_keys=True, separators=(",", ":")
    ).encode()
    return {
        "schema": "schwo.phase6.v3_1_u.geometry_preflight.v1",
        "route_map_sha256": sha256(route_map_path),
        "key_count": len(routed),
        "node_count": len(nodes_low_ambient),
        "node_inventory_sha256": hashlib.sha256(inventory_bytes).hexdigest(),
        "ambient_precision_invariant": True,
        "science_solver_calls": 0,
        "original_failed_key_exponents": [
            item["auxiliary_exponent"] for item in failed_key_nodes
        ],
    }


def _validate_official_root_path(root: Path) -> Path:
    """Require the single official-root namespace before any publication."""

    if not root.is_absolute():
        raise V31ContractError("official V3.1-U repair root must be absolute")
    resolved = root.resolve()
    if root != resolved:
        raise V31ContractError("official V3.1-U repair root alias is forbidden")
    parent = OFFICIAL_ROOT_PARENT.resolve(strict=True)
    if resolved.parent != parent:
        raise V31ContractError("official V3.1-U repair root parent mismatch")
    match = OFFICIAL_ROOT_PATTERN.fullmatch(resolved.name)
    if match is None:
        raise V31ContractError("official V3.1-U repair root namespace mismatch")
    timestamp = match.group("timestamp")
    try:
        parsed = datetime.strptime(timestamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
    except ValueError as exc:
        raise V31ContractError(
            "official V3.1-U repair root UTC timestamp is malformed"
        ) from exc
    if parsed.strftime("%Y%m%dT%H%M%SZ") != timestamp:
        raise V31ContractError(
            "official V3.1-U repair root UTC timestamp is noncanonical"
        )
    return resolved


def _validate_sentinel_root_path(root: Path) -> Path:
    return _validate_fresh_root_path(root, SENTINEL_ROOT_PATTERN, "sentinel")


def _validate_fresh_root_path(root: Path, pattern: re.Pattern[str], label: str) -> Path:
    if not root.is_absolute():
        raise V31ContractError(f"{label} root must be absolute")
    resolved = root.resolve()
    if root != resolved:
        raise V31ContractError(f"{label} root alias is forbidden")
    if resolved.parent != OFFICIAL_ROOT_PARENT.resolve(strict=True):
        raise V31ContractError(f"{label} root parent mismatch")
    match = pattern.fullmatch(resolved.name)
    if match is None:
        raise V31ContractError(f"{label} root namespace mismatch")
    timestamp = match.group("timestamp")
    try:
        parsed = datetime.strptime(timestamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
    except ValueError as exc:
        raise V31ContractError(f"{label} root UTC timestamp is malformed") from exc
    if parsed.strftime("%Y%m%dT%H%M%SZ") != timestamp:
        raise V31ContractError(f"{label} root timestamp is noncanonical")
    if resolved.exists():
        raise V31ContractError(f"{label} root is not fresh")
    return resolved


def validate_sentinel_invocation(
    *,
    executable: str,
    argv: Sequence[str],
    cwd: Path,
    environment: Mapping[str, str],
) -> None:
    """Require the package's sole, four-token sentinel invocation."""

    observed = {
        "schema": SENTINEL_INVOCATION["schema"],
        "executable": str(Path(executable).resolve(strict=True)),
        "argv": list(argv),
        "cwd": str(cwd.resolve(strict=True)),
        "environment_allowlist": dict(environment),
    }
    if observed != SENTINEL_INVOCATION:
        raise V31ContractError("Route-C sentinel invocation mismatch")


def validate_sentinel_runtime_boundary(
    *,
    launcher: Path,
    executable: str,
    argv: Sequence[str],
    cwd: Path,
    requested_environment: Mapping[str, str],
    observed_environment: Mapping[str, str],
) -> dict[str, Any]:
    """Validate exact caller-requested and complete post-startup environments."""

    authority = _load_sentinel_environment_authority()
    boundary = authority["execution_boundary"]
    launcher_authority = boundary["launcher"]
    requested = authority["requested_environment"]["exact_execve_map"]
    observed = authority["observed_environment"]["exact_post_startup_map"]
    validate_sentinel_invocation(
        executable=executable,
        argv=argv,
        cwd=cwd,
        environment=requested_environment,
    )
    if (
        str(launcher.resolve(strict=True)) != launcher_authority["path"]
        or dict(requested_environment) != requested
        or dict(observed_environment) != observed
    ):
        raise V31ContractError("Route-C sentinel runtime boundary mismatch")
    return {
        "schema": "schwo.phase6.v3_1_u.route_c_sentinel_runtime_boundary.v1",
        "environment_authority": {
            "path": str(SENTINEL_ENVIRONMENT_AUTHORITY_PATH),
            "identity": _file_identity(SENTINEL_ENVIRONMENT_AUTHORITY_PATH),
        },
        "launcher": {
            "path": launcher_authority["path"],
            "identity": _file_identity(Path(launcher_authority["path"])),
            "argv_prefix": list(launcher_authority["argv_prefix"]),
        },
        "executable": {
            "path": boundary["executable"],
            "identity": _file_identity(Path(boundary["executable"])),
        },
        "argv": list(boundary["argv"]),
        "cwd": boundary["cwd"],
        "requested_environment": dict(requested),
        "observed_environment": dict(observed),
    }


def _validate_sentinel_environment_consumption(
    consumption: Mapping[str, Any],
) -> dict[str, Any]:
    authority = _load_sentinel_environment_authority()
    expected_authority = {
        "path": str(SENTINEL_ENVIRONMENT_AUTHORITY_PATH),
        "identity": _file_identity(SENTINEL_ENVIRONMENT_AUTHORITY_PATH),
    }
    if (
        consumption.get("environment_authority") != expected_authority
        or consumption.get("requested_environment")
        != authority["requested_environment"]["exact_execve_map"]
        or consumption.get("observed_environment")
        != authority["observed_environment"]["exact_post_startup_map"]
    ):
        raise V31ContractError("sentinel environment consumption mismatch")
    runtime = consumption.get("runtime_boundary")
    if (
        not isinstance(runtime, Mapping)
        or runtime.get("environment_authority") != expected_authority
        or runtime.get("requested_environment") != consumption["requested_environment"]
        or runtime.get("observed_environment") != consumption["observed_environment"]
        or runtime.get("launcher", {}).get("path")
        != authority["execution_boundary"]["launcher"]["path"]
        or runtime.get("argv") != authority["execution_boundary"]["argv"]
        or runtime.get("cwd") != authority["execution_boundary"]["cwd"]
    ):
        raise V31ContractError("sentinel runtime consumption mismatch")
    return {
        "environment_authority": expected_authority,
        "requested_environment": dict(consumption["requested_environment"]),
        "observed_environment": dict(consumption["observed_environment"]),
    }


def _validate_created_at(value: Any) -> None:
    if not isinstance(value, str):
        raise V31ContractError("dispatch UTC timestamp missing")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise V31ContractError("dispatch UTC timestamp malformed") from exc
    if parsed.tzinfo != UTC or parsed.isoformat().replace("+00:00", "Z") != value:
        raise V31ContractError("dispatch UTC timestamp noncanonical")


def _validate_sentinel_dispatch(start_gate: Mapping[str, Any]) -> dict[str, Any]:
    dispatch_identity = _file_identity(SENTINEL_DISPATCH_PATH)
    if dispatch_identity["mode"] != 0o444:
        raise V31ContractError("sentinel dispatch mode mismatch")
    payload = json.loads(SENTINEL_DISPATCH_PATH.read_text())
    if SENTINEL_DISPATCH_PATH.read_bytes() != canonical_bytes(payload):
        raise V31ContractError("sentinel dispatch is not canonical JSON")
    expected_keys = {
        "schema",
        "gate_id",
        "repair_id",
        "exact_root",
        "single_use",
        "created_at_utc",
        "repair_package",
        "package_review",
        "implementation_review",
        "implementation_hashes",
        "environment_authority",
        "sentinel_invocation",
        "anchors",
        "method_contract",
        "snapshot",
        "wolfram_kernel",
        "protected_radial_identities",
        "source_bindings",
        "required_verdict_tokens",
    }
    if set(payload) != expected_keys:
        raise V31ContractError("sentinel dispatch schema mismatch")
    _validate_created_at(payload.get("created_at_utc"))
    root = _validate_sentinel_root_path(Path(payload["exact_root"]))
    repair2 = start_gate["repair2_package"]
    current_hashes = {
        str(ROOT / path): sha256((ROOT / path).resolve(strict=True))
        for path in ALLOWED_IMPLEMENTATION_PATHS
    }
    review_binding = payload.get("implementation_review")
    if not isinstance(review_binding, Mapping) or set(review_binding) != {
        "path",
        "sha256",
    }:
        raise V31ContractError("sentinel implementation-review schema mismatch")
    environment_binding = payload.get("environment_authority")
    if environment_binding != _sentinel_environment_authority_binding():
        raise V31ContractError("sentinel environment-authority binding mismatch")
    environment_authority = _load_sentinel_environment_authority()
    if (
        payload["schema"] != "schwo.phase6.v3_1_u.route_c_sentinel_dispatch.v1"
        or payload["gate_id"] != GATE_ID
        or payload["repair_id"] != repair2["repair_id"]
        or payload["single_use"] is not True
        or payload["repair_package"]
        != {"path": str(REPAIR2_PACKAGE_PATH), "sha256": REPAIR2_PACKAGE_SHA256}
        or payload["package_review"]
        != {
            "path": str(REPAIR2_PACKAGE_REVIEW_PATH),
            "sha256": REPAIR2_PACKAGE_REVIEW_SHA256,
        }
        or review_binding["path"] != str(IMPLEMENTATION_REVIEW_PATH)
        or payload["implementation_hashes"] != current_hashes
        or environment_binding != _sentinel_environment_authority_binding()
        or payload["sentinel_invocation"] != SENTINEL_INVOCATION
        or payload["sentinel_invocation"]["environment_allowlist"]
        != environment_authority["requested_environment"]["exact_execve_map"]
        or payload["anchors"]
        != cycle2.build_anchor_inventory(build_mode_inventory())["external"]
        or payload["method_contract"] != repair2["external_runtime"]["method_contract"]
        or payload["snapshot"] != repair2["external_runtime"]["bhpt_snapshot"]
        or payload["wolfram_kernel"] != repair2["external_runtime"]["wolfram_kernel"]
        or payload["protected_radial_identities"]
        != repair2["protected_radial_identities"]
        or payload["source_bindings"] != repair2["source_bindings"]
        or tuple(payload["required_verdict_tokens"]) != IMPLEMENTATION_REVIEW_TOKENS
    ):
        raise V31ContractError("sentinel dispatch authority binding mismatch")
    review = _file_identity(IMPLEMENTATION_REVIEW_PATH)
    if review["sha256"] != review_binding["sha256"] or not all(
        token in IMPLEMENTATION_REVIEW_PATH.read_text()
        for token in (*IMPLEMENTATION_REVIEW_TOKENS, *current_hashes.values())
    ):
        raise V31ContractError("sentinel implementation-review authority mismatch")
    return {
        "root": root,
        "dispatch": dispatch_identity,
        "payload": payload,
        "implementation_review": review,
        "implementation_hashes": current_hashes,
        "environment_authority": {
            "path": str(SENTINEL_ENVIRONMENT_AUTHORITY_PATH),
            "identity": _file_identity(SENTINEL_ENVIRONMENT_AUTHORITY_PATH),
        },
        "requested_environment": dict(
            environment_authority["requested_environment"]["exact_execve_map"]
        ),
    }


def run_route_c_sentinel(root: Path) -> dict[str, Any]:
    """Consume the one-use authority and execute only fresh Route C."""

    if __name__ != "__main__":
        raise V31ContractError("direct-import sentinel execution is forbidden")
    runtime_boundary = _validate_current_sentinel_runtime()
    root = _validate_sentinel_root_path(root)
    start_gate = verify_start_gate()
    dispatch = _validate_sentinel_dispatch(start_gate)
    if dispatch["root"] != root:
        raise V31ContractError("sentinel exact-root authority mismatch")
    if (
        runtime_boundary["environment_authority"] != dispatch["environment_authority"]
        or runtime_boundary["requested_environment"]
        != dispatch["requested_environment"]
    ):
        raise V31ContractError("sentinel runtime/dispatch environment mismatch")
    root.mkdir(mode=0o700, parents=False, exist_ok=False)
    lock = root / ".writer.lock"
    lock_fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    stage = "dispatch_consumption"
    try:
        consumption = {
            "schema": "schwo.phase6.v3_1_u.route_c_sentinel_dispatch_consumption.v1",
            "gate_id": GATE_ID,
            "repair_id": start_gate["repair2_package"]["repair_id"],
            "exact_root": str(root),
            "dispatch": dispatch["dispatch"],
            "implementation_review": dispatch["implementation_review"],
            "implementation_hashes": dispatch["implementation_hashes"],
            "environment_authority": dispatch["environment_authority"],
            "requested_environment": dispatch["requested_environment"],
            "observed_environment": runtime_boundary["observed_environment"],
            "runtime_boundary": runtime_boundary,
            "sentinel_invocation": SENTINEL_INVOCATION,
            "science_calls_before_consumption": 0,
            "single_use": True,
        }
        consumption_identity = _exclusive_publish(
            root / "dispatch_consumption.json", canonical_bytes(consumption)
        )
        augmented_gate = {
            **start_gate,
            "identities": {
                **start_gate["identities"],
                str(SENTINEL_DISPATCH_PATH): dispatch["dispatch"],
                str(IMPLEMENTATION_REVIEW_PATH): dispatch["implementation_review"],
                str(root / "dispatch_consumption.json"): consumption_identity,
            },
        }
        source_start = build_source_ledger(augmented_gate)
        _exclusive_publish(root / "source_start.json", canonical_bytes(source_start))
        _exclusive_publish(
            root / "sentinel_contract.json",
            canonical_bytes(
                {
                    "schema": "schwo.phase6.v3_1_u.route_c_sentinel_contract.v1",
                    "gate_id": GATE_ID,
                    "exact_root": str(root),
                    "anchors": cycle2.build_anchor_inventory(build_mode_inventory())[
                        "external"
                    ],
                    "external_calls": 23,
                    "wolfram_child_launches": 1,
                    "predecessor_science_reused": False,
                    "sentinel_science_reused": False,
                    "non_resumable": True,
                    "retry_permitted": False,
                }
            ),
        )
        stage = "route_c"
        records = cycle2.run_external_records(root / "external_evidence")
        if len(records) != 23:
            raise V31ContractError("sentinel Route-C cardinality mismatch")
        source_end = build_source_ledger(augmented_gate)
        if source_end != source_start:
            raise V31ContractError("sentinel source identity drift")
        _exclusive_publish(
            root / "source_map.json",
            canonical_bytes({"start": source_start, "end": source_end}),
        )
        result_identity = _exclusive_publish(
            root / "sentinel_result.json",
            canonical_bytes(
                {
                    "schema": "schwo.phase6.v3_1_u.route_c_sentinel_result.v1",
                    "status": "PASS",
                    "terminal": True,
                    "record_count": 23,
                    "external_result": _file_identity(
                        root / "external_evidence/external_result.json"
                    ),
                    "predecessor_science_reused": False,
                    "sentinel_science_reused": False,
                    "global_green_permitted": False,
                    "independent_review_state": "NOT_ASSESSED",
                }
            ),
        )
        os.close(lock_fd)
        lock_fd = -1
        lock.unlink()
        _seal_tree(root)
        os.chmod(root, 0o755)
        manifest_identity = _exclusive_publish(
            root / "manifest.json",
            canonical_bytes(build_manifest(root, overall_state="PASS")),
        )
        os.chmod(root, 0o555)
        return {
            "root": str(root),
            "result": result_identity,
            "manifest": manifest_identity,
        }
    except BaseException as exc:
        if lock_fd >= 0:
            os.close(lock_fd)
        if lock.exists() and not lock.is_symlink():
            lock.unlink()
        _terminalize_failure(root, f"sentinel_{stage}", exc)
        raise


def _sentinel_module_main(argv: Sequence[str] | None = None) -> int:
    _validate_current_sentinel_runtime(argv)
    start_gate = verify_start_gate()
    dispatch = _validate_sentinel_dispatch(start_gate)
    run_route_c_sentinel(dispatch["root"])
    return 0


def _validate_current_sentinel_runtime(
    argv: Sequence[str] | None = None,
) -> dict[str, Any]:
    actual_argv = list(sys.orig_argv if argv is None else argv)
    authority = _load_sentinel_environment_authority()
    return validate_sentinel_runtime_boundary(
        launcher=Path(authority["execution_boundary"]["launcher"]["path"]),
        executable=sys.executable,
        argv=[str(Path(sys.executable).resolve()), *actual_argv[1:]],
        cwd=Path.cwd(),
        requested_environment=authority["requested_environment"]["exact_execve_map"],
        observed_environment=dict(os.environ),
    )


def _validate_dispatch(root: Path, start_gate: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the separate official dispatch after formal sentinel review."""

    root = _validate_fresh_root_path(root, OFFICIAL_ROOT_PATTERN, "official")
    dispatch_identity = _file_identity(DISPATCH_PATH)
    if dispatch_identity["mode"] != 0o444:
        raise V31ContractError("official dispatch mode mismatch")
    payload = json.loads(DISPATCH_PATH.read_text())
    if DISPATCH_PATH.read_bytes() != canonical_bytes(payload):
        raise V31ContractError("official dispatch is not canonical JSON")
    expected_keys = {
        "schema",
        "gate_id",
        "repair_id",
        "exact_root",
        "single_use",
        "created_at_utc",
        "repair_package",
        "package_review",
        "implementation_review",
        "implementation_hashes",
        "environment_authority",
        "sentinel_review",
        "sentinel_terminal",
        "frozen_cli",
        "protected_radial_identities",
        "source_bindings",
        "required_verdict_tokens",
        "predecessor_science_reused",
        "sentinel_science_reused",
    }
    if set(payload) != expected_keys:
        raise V31ContractError("official dispatch schema mismatch")
    _validate_created_at(payload.get("created_at_utc"))
    review_binding = payload.get("implementation_review")
    if not isinstance(review_binding, Mapping) or set(review_binding) != {
        "path",
        "sha256",
    }:
        raise V31ContractError("official implementation-review schema mismatch")
    sentinel_review = payload.get("sentinel_review")
    if not isinstance(sentinel_review, Mapping) or set(sentinel_review) != {
        "path",
        "sha256",
    }:
        raise V31ContractError("official sentinel-review schema mismatch")
    sentinel_terminal = payload.get("sentinel_terminal")
    if not isinstance(sentinel_terminal, Mapping) or set(sentinel_terminal) != {
        "root",
        "dispatch_consumption",
        "result",
        "manifest",
    }:
        raise V31ContractError("official sentinel-terminal schema mismatch")
    repair2 = start_gate["repair2_package"]
    if (
        payload["schema"] != "schwo.phase6.v3_1_u.repair_cycle2_official_dispatch.v1"
        or payload["gate_id"] != GATE_ID
        or payload["repair_id"] != repair2["repair_id"]
        or payload["exact_root"] != str(root)
        or payload["single_use"] is not True
        or not isinstance(payload["created_at_utc"], str)
        or not payload["created_at_utc"].endswith("Z")
        or payload["repair_package"]
        != {"path": str(REPAIR2_PACKAGE_PATH), "sha256": REPAIR2_PACKAGE_SHA256}
        or payload["package_review"]
        != {
            "path": str(REPAIR2_PACKAGE_REVIEW_PATH),
            "sha256": REPAIR2_PACKAGE_REVIEW_SHA256,
        }
        or review_binding["path"] != str(IMPLEMENTATION_REVIEW_PATH)
        or payload["environment_authority"] != _sentinel_environment_authority_binding()
        or payload["frozen_cli"]
        != {
            "path": str(ROOT / "scripts/phase6_v3_1_hp_unitarity.py"),
            "sha256": "01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4",
        }
        or tuple(payload["required_verdict_tokens"])
        != (*IMPLEMENTATION_REVIEW_TOKENS, *SENTINEL_REVIEW_TOKENS)
        or sentinel_review["path"] != str(SENTINEL_REVIEW_PATH)
        or payload["predecessor_science_reused"] is not False
        or payload["sentinel_science_reused"] is not False
    ):
        raise V31ContractError("official dispatch authority binding mismatch")
    if (
        payload["protected_radial_identities"] != repair2["protected_radial_identities"]
        or payload["source_bindings"] != repair2["source_bindings"]
    ):
        raise V31ContractError("official dispatch frozen-source binding mismatch")
    current_hashes = {
        str(ROOT / path): sha256((ROOT / path).resolve(strict=True))
        for path in ALLOWED_IMPLEMENTATION_PATHS
    }
    if payload["implementation_hashes"] != current_hashes:
        raise V31ContractError("official dispatch implementation hash mismatch")
    review_sha = review_binding["sha256"]
    if not isinstance(review_sha, str) or len(review_sha) != 64:
        raise V31ContractError("implementation-review digest malformed")
    review_identity = _file_identity(IMPLEMENTATION_REVIEW_PATH)
    if review_identity["sha256"] != review_sha:
        raise V31ContractError("implementation-review identity mismatch")
    review_text = IMPLEMENTATION_REVIEW_PATH.read_text()
    if not all(
        token in review_text for token in IMPLEMENTATION_REVIEW_TOKENS
    ) or not all(digest in review_text for digest in current_hashes.values()):
        raise V31ContractError("implementation-review verdict/source binding mismatch")
    sentinel_review_identity = _file_identity(SENTINEL_REVIEW_PATH)
    if sentinel_review_identity["sha256"] != sentinel_review["sha256"] or not all(
        token in SENTINEL_REVIEW_PATH.read_text() for token in SENTINEL_REVIEW_TOKENS
    ):
        raise V31ContractError("sentinel-review authority mismatch")
    sentinel_root = Path(sentinel_terminal["root"]).resolve(strict=True)
    if (
        not SENTINEL_ROOT_PATTERN.fullmatch(sentinel_root.name)
        or sentinel_root.parent != OFFICIAL_ROOT_PARENT.resolve(strict=True)
        or stat.S_IMODE(sentinel_root.stat().st_mode) != 0o555
    ):
        raise V31ContractError("sentinel terminal root binding mismatch")
    for name in ("dispatch_consumption", "result", "manifest"):
        binding = sentinel_terminal[name]
        if not isinstance(binding, Mapping) or set(binding) != {"path", "identity"}:
            raise V31ContractError("sentinel terminal identity schema mismatch")
        path = Path(binding["path"])
        live_identity = _file_identity(path)
        if (
            path.parent != sentinel_root
            or live_identity != binding["identity"]
            or live_identity["mode"] != 0o444
        ):
            raise V31ContractError("sentinel terminal identity mismatch")
    sentinel_result = json.loads(Path(sentinel_terminal["result"]["path"]).read_text())
    if (
        sentinel_result.get("status") != "PASS"
        or sentinel_result.get("record_count") != 23
    ):
        raise V31ContractError("sentinel terminal result is not PASS")
    sentinel_consumption = json.loads(
        Path(sentinel_terminal["dispatch_consumption"]["path"]).read_text()
    )
    environment_consumption = _validate_sentinel_environment_consumption(
        sentinel_consumption
    )
    sentinel_manifest = json.loads(
        Path(sentinel_terminal["manifest"]["path"]).read_text()
    )
    if (
        sentinel_manifest.get("overall_state") != "PASS"
        or sentinel_manifest.get("gate_id") != GATE_ID
        or sentinel_manifest.get("terminal") is not True
    ):
        raise V31ContractError("sentinel terminal manifest mismatch")
    return {
        "dispatch": dispatch_identity,
        "dispatch_payload_sha256": hashlib.sha256(canonical_bytes(payload)).hexdigest(),
        "implementation_review": review_identity,
        "implementation_hashes": current_hashes,
        **environment_consumption,
        "sentinel_review": sentinel_review_identity,
        "sentinel_terminal": dict(sentinel_terminal),
    }


def solve_route_u_ladder(
    entry: Mapping[str, Any], *, route_map_sha256: str
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not entry["selector"]["use_route_u"]:
        raise V31ContractError("Route-U solve requested for non-routed mode")
    mode_value = entry["mode"]
    mode = OracleMode(mode_value["kM"], int(mode_value["ell"]), mode_value["parity"])
    schedule = precision_schedule(entry["selector"]["Gamma_flux_decimal"])
    records = [
        solve_oracle_node(
            mode,
            dps=dps,
            route_a_gamma_decimal=entry["selector"]["Gamma_flux_decimal"],
            route_map_sha256=route_map_sha256,
            mode_ordinal=int(entry["ordinal"]),
            precision_ordinal=precision_ordinal,
        )
        for precision_ordinal, dps in enumerate(schedule)
    ]
    return records, validate_oracle_ladder(records)


def evaluate_all_thresholds(
    mode_records: Sequence[Mapping[str, Any]],
    ladder_records: Sequence[Mapping[str, Any]],
    route_map: Mapping[str, Any],
    route_u_records: Sequence[Mapping[str, Any]],
    route_u_ladders: Sequence[Mapping[str, Any]],
    ap_records: Sequence[Mapping[str, Any]],
    external_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Apply all frozen thresholds, replacing only the small-Gamma S operand."""

    validate_route_map(route_map)
    if len(mode_records) != 496 or len(ladder_records) != 9920:
        raise V31ContractError("V3.1-U Route-A cardinality mismatch")
    routed_entries = [
        item for item in route_map["entries"] if item["selector"]["use_route_u"]
    ]
    n_u = len(routed_entries)
    if len(route_u_records) != 3 * n_u or len(route_u_ladders) != n_u:
        raise V31ContractError("V3.1-U Route-U cardinality mismatch")
    by_u: dict[int, list[Mapping[str, Any]]] = {}
    for item in route_u_records:
        by_u.setdefault(int(item["mode_ordinal"]), []).append(item)
    for group in by_u.values():
        group.sort(key=lambda item: item["precision_ordinal"])
        validate_oracle_ladder(group)
    if sorted(by_u) != [int(item["ordinal"]) for item in routed_entries]:
        raise V31ContractError("V3.1-U Route-U mode inventory mismatch")

    # Preserve every unchanged cycle-2 threshold calculation.  Small-Gamma
    # float64 Gamma_S is replaced in a deep copy only to neutralize the obsolete
    # nonrepresentable operand before the exact Route-U extrema are installed.
    shadow = json.loads(json.dumps(mode_records))
    for ordinal, entry in enumerate(route_map["entries"]):
        if entry["selector"]["use_route_u"]:
            shadow[ordinal]["baseline"]["Gamma_S"] = shadow[ordinal]["baseline"][
                "Gamma_flux"
            ]
    base = cycle2.evaluate_all_thresholds(
        shadow, ladder_records, ap_records, external_records
    )
    outcomes = {item["field_id"]: dict(item) for item in base["thresholds"]}
    threshold_limits = {
        item["field_id"]: mp.mpf(str(item["value"]))
        for item in cycle2._v31_thresholds()
    }

    max_small = mp.mpf(0)
    max_physical = mp.mpf(0)
    small_argmax: dict[str, Any] | None = None
    for ordinal, (mode_record, entry) in enumerate(
        zip(mode_records, route_map["entries"])
    ):
        baseline = mode_record["baseline"]
        gf = gamma_decimal_value(baseline["Gamma_flux_decimal"])
        if entry["selector"]["use_route_u"]:
            final = by_u[ordinal][-1]
            gs = mp.mpf(final["Gamma_S_U"])
            difference = abs(
                mp.mpf(str(baseline["log_Gamma_flux"])) - mp.mpf(final["log_Gamma_S_U"])
            )
            if difference > max_small:
                max_small = difference
                small_argmax = {"ordinal": ordinal, "mode": mode_record["mode"]}
        else:
            gs = mp.mpf(str(baseline["Gamma_S"]))
        max_physical = max(max_physical, max(-gf, gf - 1, -gs, gs - 1, mp.mpf(0)))

    for field_id, observed, argmax in (
        ("V3T-GAMMA-ROUTES-LOG-001", max_small, small_argmax),
        ("V3T-GAMMA-PHYSICAL-001", max_physical, None),
    ):
        outcomes[field_id] = {
            "field_id": field_id,
            "observed": float(observed),
            "observed_decimal": mp.nstr(observed, 80),
            "limit": float(threshold_limits[field_id]),
            "status": "PASS" if observed <= threshold_limits[field_id] else "FAIL",
            "argmax": argmax,
        }
    ordered = [outcomes[item["field_id"]] for item in cycle2._v31_thresholds()]
    all_pass = all(item["status"] == "PASS" for item in ordered)
    certificates = [
        {"certificate_id": certificate, "status": "PASS" if all_pass else "FAIL"}
        for certificate in cycle2.CERTIFICATE_IDS
    ]
    counts = {**EXPECTED_FIXED_COUNTS, "route_u_keys": n_u, "route_u_nodes": 3 * n_u}
    return {
        "all_pass": all_pass,
        "thresholds": ordered,
        "summary": {
            "schema": "schwo.phase6.v3_1_u.summary.v1",
            "gate_id": GATE_ID,
            "overall_state": "PASS" if all_pass else "FAILED_SCIENTIFIC",
            "counts": counts,
            "thresholds": ordered,
            "certificates": certificates,
            "route_u_count_data_derived": n_u,
            "global_status": None,
            "global_green_permitted": False,
            "independent_review_state": "NOT_ASSESSED",
        },
        "uncertainty_budget": {
            "schema": "schwo.phase6.v3_1_u.uncertainty.v1",
            "route_u_precision_envelopes": list(route_u_ladders),
            "route_a_vs_route_u_max_log_difference": mp.nstr(max_small, 80),
            "common_absolute_phase": "PARTIAL",
            "numerical_and_convention_budgets_separate": True,
            "budgets_combined": False,
        },
    }


def synthetic_payload(route_u_count: int) -> dict[str, Any]:
    if (
        not isinstance(route_u_count, int)
        or isinstance(route_u_count, bool)
        or not 0 <= route_u_count <= 496
    ):
        raise V31ContractError("synthetic Route-U count out of range")
    base = cycle2.synthetic_payload()
    return {
        "schema": "schwo.phase6.v3_1_u.synthetic_graph.v1",
        "scientific_evidence": False,
        "counts": {
            **base["counts"],
            "route_u_keys": route_u_count,
            "route_u_nodes": 3 * route_u_count,
        },
        "certificates": base["certificates"],
    }


def run_preexecution_sentinels(output: Path) -> dict[str, Any]:
    """Run all mandatory non-authoritative real/synthetic V3.1-U sentinels."""

    if output.exists():
        raise V31ContractError("V3.1-U sentinel output collision")
    start = verify_start_gate()
    modes = build_mode_inventory()
    lookup = {(key.kM, key.ell, key.parity): key for key in modes}
    highest: list[ModeKey] = []
    for frequency in {key.kM for key in modes}:
        max_ell = max(key.ell for key in modes if key.kM == frequency)
        highest.extend(
            (lookup[(frequency, max_ell, "odd")], lookup[(frequency, max_ell, "even")])
        )
    highest.sort()
    selected = [lookup[("0.005", 2, "odd")], lookup[("0.005", 2, "even")], *highest]
    selected_unique = list(dict.fromkeys(selected))
    sentinel_records: list[dict[str, Any]] = []
    route_u_seconds: list[float] = []
    first_three_node: list[dict[str, Any]] = []
    for sentinel_ordinal, key in enumerate(selected_unique):
        baseline_node = next(
            node
            for node in cycle2.route_a_node_graph(key)
            if cycle2._node_tuple(node) == (1e-10, 1, 160, 1e-10, 1e-12)
        )
        route_a = cycle2._solve_route_a_node_record(key, baseline_node)
        view = selector_view(
            {"mode": key.payload(), "baseline": route_a["result"]},
            ordinal=key.frequency_ordinal * 1000 + key.ell * 2 + key.parity_ordinal,
            record_sha256=hashlib.sha256(
                cycle2.compact_jsonl_record(route_a)
            ).hexdigest(),
        )
        # Real sentinels exercise the fixed schedule even when the production
        # selector would choose the large-Gamma branch.
        fake_map_sha = hashlib.sha256(canonical_bytes(view)).hexdigest()
        mode = OracleMode(key.kM, key.ell, key.parity)
        ladder = [
            solve_oracle_node(
                mode,
                dps=dps,
                route_a_gamma_decimal=view["Gamma_flux_decimal"],
                route_map_sha256=fake_map_sha,
                mode_ordinal=sentinel_ordinal,
                precision_ordinal=index,
            )
            for index, dps in enumerate(precision_schedule(view["Gamma_flux_decimal"]))
        ]
        admission = validate_oracle_ladder(ladder)
        route_u_seconds.extend(float(item["elapsed_seconds"]) for item in ladder)
        if key.kM == "0.005" and key.ell == 2:
            first_three_node.extend(ladder)
        sentinel_records.append(
            {
                "mode": key.payload(),
                "route_a_baseline": route_a,
                "selector_view": view,
                "route_u_ladder": ladder,
                "admission": admission,
            }
        )
    # Use actual direct-flux operands to exercise both branches.
    branch_views = [item["selector_view"] for item in sentinel_records]
    large_key = lookup[("8", 2, "odd")]
    node = next(
        item
        for item in cycle2.route_a_node_graph(large_key)
        if cycle2._node_tuple(item) == (1e-10, 1, 160, 1e-10, 1e-12)
    )
    large_record = cycle2._solve_route_a_node_record(large_key, node)
    branch_views.append(
        selector_view(
            {"mode": large_key.payload(), "baseline": large_record["result"]},
            ordinal=999999,
            record_sha256=hashlib.sha256(
                cycle2.compact_jsonl_record(large_record)
            ).hexdigest(),
        )
    )
    decisions = [
        mp.mpf(item["log_Gamma_flux"]) < SELECTOR_LOG_THRESHOLD for item in branch_views
    ]
    if set(decisions) != {False, True}:
        raise V31ContractError(
            "real selector boundary sentinels did not cover both branches"
        )
    synthetic = {str(count): synthetic_payload(count) for count in (0, 1, 496)}
    free_bytes = shutil.disk_usage(ROOT).free
    mean = sum(route_u_seconds) / len(route_u_seconds)
    high = max(route_u_seconds)
    # The fixed Route-A/B/C projection is inherited from the accepted cycle-2
    # sentinel; Route-U bounds are explicitly conservative over N_U<=496.
    inherited_seconds = 16559.0729
    lower = inherited_seconds + 3 * 496 * min(route_u_seconds)
    central = inherited_seconds + 3 * 496 * mean
    conservative = inherited_seconds + 3 * 496 * high
    projected_bytes = 1024 * 1024 * 1024
    resources = {
        "route_u_node_seconds_min": min(route_u_seconds),
        "route_u_node_seconds_mean": mean,
        "route_u_node_seconds_max": high,
        "N_U_conservative": 496,
        "projected_runtime_seconds_lower": lower,
        "projected_runtime_seconds_central": central,
        "projected_runtime_seconds_conservative": conservative,
        "projected_output_bytes": projected_bytes,
        "free_bytes": free_bytes,
        "runtime_gate_passed": conservative <= 36 * 3600,
        "disk_gate_passed": projected_bytes <= free_bytes // 4,
    }
    if not resources["runtime_gate_passed"] or not resources["disk_gate_passed"]:
        raise V31ContractError("V3.1-U resource stop gate failed")
    payload = {
        "schema": "schwo.phase6.v3_1_u.preexecution_sentinels.v1",
        "scientific_evidence": False,
        "official_root_created": False,
        "start_gate": start["identities"],
        "sentinel_records": sentinel_records,
        "first_low_frequency_node_count": len(first_three_node),
        "highest_barrier_mode_count": len(highest),
        "selector_branch_decisions": decisions,
        "synthetic_graphs": synthetic,
        "resource_projection": resources,
    }
    _exclusive_publish(output, canonical_bytes(payload))
    return payload


def run_official(root: Path) -> dict[str, Any]:
    """Run the unique fresh V3.1-U official candidate."""

    root = _validate_official_root_path(root)
    start_gate = verify_start_gate()
    dispatch = _validate_dispatch(root, start_gate)
    root.mkdir(mode=0o700, parents=False, exist_ok=False)
    lock = root / ".writer.lock"
    lock_fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    current_stage = "prelaunch"
    started = time.perf_counter()
    try:
        consumption = {
            "schema": "schwo.phase6.v3_1_u.repair_cycle2_official_dispatch_consumption.v1",
            "gate_id": GATE_ID,
            "exact_root": str(root),
            "dispatch": dispatch["dispatch"],
            "dispatch_payload_sha256": dispatch["dispatch_payload_sha256"],
            "implementation_review": dispatch["implementation_review"],
            "implementation_hashes": dispatch["implementation_hashes"],
            "environment_authority": dispatch["environment_authority"],
            "requested_environment": dispatch["requested_environment"],
            "observed_environment": dispatch["observed_environment"],
            "sentinel_review": dispatch["sentinel_review"],
            "sentinel_terminal": dispatch["sentinel_terminal"],
            "science_calls_before_consumption": 0,
            "predecessor_science_reused": False,
            "sentinel_science_reused": False,
        }
        consumption_identity = _exclusive_publish(
            root / "dispatch_consumption.json", canonical_bytes(consumption)
        )
        start_gate = {
            **start_gate,
            "official_dispatch": dispatch,
            "dispatch_consumption": consumption_identity,
            "identities": {
                **start_gate["identities"],
                str(DISPATCH_PATH): dispatch["dispatch"],
                str(IMPLEMENTATION_REVIEW_PATH): dispatch["implementation_review"],
                str(SENTINEL_REVIEW_PATH): dispatch["sentinel_review"],
                str(root / "dispatch_consumption.json"): consumption_identity,
            },
        }
        source_start = build_source_ledger(start_gate)
        _exclusive_publish(
            root / "inventory.json", canonical_bytes(build_inventory_payload())
        )
        _exclusive_publish(
            root / "run_contract.json",
            canonical_bytes(_run_contract(root, source_start)),
        )
        _exclusive_publish(root / "source_start.json", canonical_bytes(source_start))
        checkpoints = root / "mode_checkpoints"
        checkpoints.mkdir(mode=0o700)

        current_stage = "route_a"
        mode_records: list[dict[str, Any]] = []
        ladder_records: list[dict[str, Any]] = []
        selector_views: list[dict[str, Any]] = []
        with (
            _JsonlWriter(root / "ladder_records.jsonl") as ladder_writer,
            _JsonlWriter(root / "records.jsonl") as mode_writer,
        ):
            for ordinal, key in enumerate(build_mode_inventory()):
                mode, ladder = cycle2.solve_route_a_mode(key)
                for record in ladder:
                    ladder_writer.append(record)
                mode_writer.append(mode)
                mode_records.append(mode)
                ladder_records.extend(ladder)
                selector_views.append(
                    selector_view(
                        mode,
                        ordinal=ordinal,
                        record_sha256=hashlib.sha256(
                            cycle2.compact_jsonl_record(mode)
                        ).hexdigest(),
                    )
                )
                _exclusive_publish(
                    checkpoints / f"route_a_{ordinal:04d}.json",
                    canonical_bytes(
                        {
                            "schema": "schwo.phase6.v3_1_u.route_a_checkpoint.v1",
                            "ordinal": ordinal,
                            "mode": key.payload(),
                            "status": "COMPUTED_NOT_ACCEPTED",
                            "node_count": 20,
                        }
                    ),
                )

        current_stage = "route_map"
        route_map = build_route_map(selector_views)
        route_map_identity = _exclusive_publish(
            root / "unitarity_route_map.json", canonical_bytes(route_map)
        )
        validate_route_map(route_map)

        current_stage = "route_u"
        route_u_records: list[dict[str, Any]] = []
        route_u_ladders: list[dict[str, Any]] = []
        with (
            _JsonlWriter(root / "route_u_records.jsonl") as node_writer,
            _JsonlWriter(root / "route_u_ladders.jsonl") as mode_writer,
        ):
            for entry in route_map["entries"]:
                if not entry["selector"]["use_route_u"]:
                    continue
                records, admission = solve_route_u_ladder(
                    entry, route_map_sha256=route_map_identity["sha256"]
                )
                for record in records:
                    node_writer.append(record)
                mode_writer.append(admission)
                route_u_records.extend(records)
                route_u_ladders.append(admission)
                _exclusive_publish(
                    checkpoints / f"route_u_{entry['ordinal']:04d}.json",
                    canonical_bytes(
                        {
                            "schema": "schwo.phase6.v3_1_u.route_u_checkpoint.v1",
                            "ordinal": entry["ordinal"],
                            "mode": entry["mode"],
                            "status": "COMPUTED_NOT_ACCEPTED",
                            "route_map_sha256": route_map_identity["sha256"],
                            "precision_schedule": admission["precision_schedule"],
                        }
                    ),
                )

        current_stage = "route_b"
        ap_records: list[dict[str, Any]] = []
        with _JsonlWriter(root / "ap_records.jsonl") as writer:
            for node in cycle2.ap_node_plan():
                record = cycle2.solve_ap_node(node)
                writer.append(record)
                ap_records.append(record)

        current_stage = "route_c"
        external_records = cycle2.run_external_records(root / "external_evidence")
        with _JsonlWriter(root / "external_records.jsonl") as writer:
            for record in external_records:
                writer.append(record)

        current_stage = "validation"
        evaluation = evaluate_all_thresholds(
            mode_records,
            ladder_records,
            route_map,
            route_u_records,
            route_u_ladders,
            ap_records,
            external_records,
        )
        if not evaluation["all_pass"]:
            _exclusive_publish(
                root / "failed_evaluation.json", canonical_bytes(evaluation)
            )
            raise V31ContractError("official V3.1-U threshold/certificate failure")
        source_end = build_source_ledger(start_gate)
        if source_end != source_start:
            raise V31ContractError(
                "V3.1-U source identity drift during official execution"
            )
        _exclusive_publish(
            root / "source_map.json",
            canonical_bytes({"start": source_start, "end": source_end}),
        )
        _exclusive_publish(
            root / "uncertainty_budget.json",
            canonical_bytes(evaluation["uncertainty_budget"]),
        )
        _exclusive_publish(
            root / "summary.json", canonical_bytes(evaluation["summary"])
        )
        _exclusive_publish(
            root / "report.json",
            canonical_bytes(
                {
                    "schema": "schwo.phase6.v3_1_u.report.v1",
                    "gate_id": GATE_ID,
                    "terminal": True,
                    "candidate_success": True,
                    "elapsed_seconds": time.perf_counter() - started,
                    "global_status": None,
                    "global_green_permitted": False,
                    "independent_review_state": "NOT_ASSESSED",
                    "nonclaims": [
                        "no V3.1 acceptance before formal T7 review",
                        "no V3.2",
                        "no global GREEN",
                    ],
                }
            ),
        )
        os.close(lock_fd)
        lock_fd = -1
        lock.unlink()
        _seal_tree(root)
        os.chmod(root, 0o755)
        manifest = build_manifest(root, overall_state="PASS")
        manifest_identity = _exclusive_publish(
            root / "manifest.json", canonical_bytes(manifest)
        )
        os.chmod(root, 0o555)
        validate_official_candidate(root)
        return {
            "root": str(root),
            "manifest": manifest_identity,
            "evaluation": evaluation,
        }
    except BaseException as exc:
        if lock_fd >= 0:
            os.close(lock_fd)
        if lock.exists() and not lock.is_symlink():
            lock.unlink()
        _terminalize_failure(root, current_stage, exc)
        raise


def validate_official_candidate(
    root: Path, *, validate_live_sources: bool = True
) -> None:
    root = root.resolve(strict=True)
    if stat.S_IMODE(root.stat().st_mode) != 0o555:
        raise V31ContractError("V3.1-U official root mode mismatch")
    manifest = json.loads((root / "manifest.json").read_text())
    if (
        manifest.get("schema") != "schwo.phase6.v3_1_u.manifest.v1"
        or manifest.get("gate_id") != GATE_ID
        or manifest.get("artifact_rev") != ARTIFACT_REV
        or manifest.get("overall_state") != "PASS"
    ):
        raise V31ContractError("V3.1-U manifest mismatch")
    actual = {
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() and path.name != "manifest.json"
    }
    if actual != set(manifest["artifacts"]):
        raise V31ContractError("V3.1-U artifact inventory mismatch")
    for relative, identity in manifest["artifacts"].items():
        if _file_identity(root / relative) != identity:
            raise V31ContractError(f"V3.1-U artifact identity mismatch: {relative}")
    modes = cycle2.load_jsonl(root / "records.jsonl")
    ladders = cycle2.load_jsonl(root / "ladder_records.jsonl")
    route_map = json.loads((root / "unitarity_route_map.json").read_text())
    u_records = cycle2.load_jsonl(root / "route_u_records.jsonl")
    u_ladders = cycle2.load_jsonl(root / "route_u_ladders.jsonl")
    ap = cycle2.load_jsonl(root / "ap_records.jsonl")
    external = cycle2.load_jsonl(root / "external_records.jsonl")
    validate_route_map(route_map)
    expected_modes = [key.payload() for key in build_mode_inventory()]
    if [item["mode"] for item in modes] != expected_modes or len(ladders) != 9920:
        raise V31ContractError("V3.1-U Route-A reload mismatch")
    if len(ap) != 458 or len(external) != 23:
        raise V31ContractError("V3.1-U Route-B/C reload mismatch")
    external_terminal = json.loads(
        (root / "external_evidence/external_terminal.json").read_text()
    )
    external_result = json.loads(
        (root / "external_evidence/external_result.json").read_text()
    )
    if (
        external_terminal.get("status") != "PASS"
        or external_terminal.get("outcome_count") != 23
        or external_result.get("record_count") != 23
        or external_result.get("status") != "PASS"
    ):
        raise V31ContractError("V3.1-U Route-C terminal evidence mismatch")
    consumption = json.loads((root / "dispatch_consumption.json").read_text())
    environment_authority = _load_sentinel_environment_authority()
    if (
        consumption.get("predecessor_science_reused") is not False
        or consumption.get("sentinel_science_reused") is not False
        or consumption.get("environment_authority")
        != {
            "path": str(SENTINEL_ENVIRONMENT_AUTHORITY_PATH),
            "identity": _file_identity(SENTINEL_ENVIRONMENT_AUTHORITY_PATH),
        }
        or consumption.get("requested_environment")
        != environment_authority["requested_environment"]["exact_execve_map"]
        or consumption.get("observed_environment")
        != environment_authority["observed_environment"]["exact_post_startup_map"]
    ):
        raise V31ContractError("V3.1-U forbidden predecessor/sentinel reuse")
    evaluation = evaluate_all_thresholds(
        modes, ladders, route_map, u_records, u_ladders, ap, external
    )
    summary = json.loads((root / "summary.json").read_text())
    if not evaluation["all_pass"] or summary != evaluation["summary"]:
        raise V31ContractError("V3.1-U terminal evaluation mismatch")
    source_map = json.loads((root / "source_map.json").read_text())
    if source_map["start"] != source_map["end"] or source_map["start"] != json.loads(
        (root / "source_start.json").read_text()
    ):
        raise V31ContractError("V3.1-U source-map mismatch")
    if validate_live_sources:
        verify_start_gate()


def build_source_ledger(start_gate: Mapping[str, Any]) -> dict[str, Any]:
    paths = [
        *(ROOT / path for path in ALLOWED_IMPLEMENTATION_PATHS),
        ROOT / "src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py",
        ROOT / "scripts/phase6_v3_1_hp_unitarity.py",
        ROOT / "src/schwgw/validation/phase6_v3_mode_greybody_cycle2.py",
        ROOT / "src/schwgw/validation/phase6_v3_mode_greybody_ap.py",
        ROOT / "src/schwgw/validation/phase6_mpmath_radial.py",
    ]
    ledger: dict[str, Any] = {}
    for path_text, expected in start_gate["identities"].items():
        if not isinstance(path_text, str) or not isinstance(expected, Mapping):
            raise V31ContractError("V3.1-U source authority ledger is malformed")
        current = _file_identity(Path(path_text))
        if current != dict(expected):
            raise V31ContractError(
                f"V3.1-U source authority identity drift: {path_text}"
            )
        ledger[path_text] = current
    ledger.update(
        {str(path): _file_identity(path.resolve(strict=True)) for path in paths}
    )
    environment_authority = _load_sentinel_environment_authority()
    ledger["sentinel_environment_authority"] = {
        "binding": _sentinel_environment_authority_binding(),
        "requested_environment": environment_authority["requested_environment"][
            "exact_execve_map"
        ],
        "observed_environment": environment_authority["observed_environment"][
            "exact_post_startup_map"
        ],
        "execution_boundary": environment_authority["execution_boundary"],
    }
    ledger["external_route_c_source"] = cycle2.external_source_identity()
    return ledger


def validate_import_isolation() -> dict[str, Any]:
    oracle_path = ROOT / "src/schwgw/validation/phase6_v3_hp_unitarity_oracle.py"
    tree = ast.parse(oracle_path.read_text())
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }
    forbidden = [
        value
        for value in imports
        if "phase6_v3_mode_greybody_cycle2" in value
        or "phase6_v3_continued_jost" in value
        or value.startswith("schwgw.numerics")
    ]
    if forbidden:
        raise V31ContractError(f"Route-U forbidden numerical imports: {forbidden}")
    return {
        "oracle_path": str(oracle_path),
        "imports": sorted(imports),
        "forbidden": [],
    }


def build_manifest(root: Path, *, overall_state: str) -> dict[str, Any]:
    artifacts = {
        str(path.relative_to(root)): _file_identity(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and path.name not in {"manifest.json", "failure_manifest.json"}
    }
    return {
        "schema": "schwo.phase6.v3_1_u.manifest.v1",
        "gate_id": GATE_ID,
        "scientific_stage": "V3.1-U",
        "artifact_rev": ARTIFACT_REV,
        "timezone": "UTC",
        "terminal": True,
        "overall_state": overall_state,
        "global_status": None,
        "global_green_permitted": False,
        "independent_review_state": "NOT_ASSESSED",
        "artifacts": artifacts,
    }


def _run_contract(root: Path, source_ledger: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": "schwo.phase6.v3_1_u.run_contract.v1",
        "gate_id": GATE_ID,
        "created_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "official_root": str(root),
        "artifact_rev": ARTIFACT_REV,
        "counts": EXPECTED_FIXED_COUNTS,
        "route_u_count": "data-derived after complete Route A",
        "python": sys.version,
        "executable": str(Path(sys.executable).resolve()),
        "argv": list(sys.argv),
        "cwd": str(Path.cwd().resolve()),
        "source_start_sha256": hashlib.sha256(
            canonical_bytes(source_ledger)
        ).hexdigest(),
        "resume_policy": "verified system interruption with exact contiguous prefix only",
        "predecessor_science_reused": False,
    }


def _exclusive_publish(path: Path, payload: bytes) -> dict[str, Any]:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    try:
        os.write(fd, payload)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(path, 0o444)
    _fsync_directory(path.parent)
    return _file_identity(path)


class _JsonlWriter:
    def __init__(self, path: Path):
        self.path = path
        self.fd = -1

    def __enter__(self) -> _JsonlWriter:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        self.fd = os.open(self.path, flags, 0o600)
        return self

    def append(self, payload: Mapping[str, Any]) -> None:
        if self.fd < 0:
            raise V31ContractError("JSONL writer is closed")
        os.write(self.fd, cycle2.compact_jsonl_record(payload))
        os.fsync(self.fd)

    def __exit__(self, *_: Any) -> None:
        if self.fd >= 0:
            os.fsync(self.fd)
            os.close(self.fd)
            os.chmod(self.path, 0o444)
            _fsync_directory(self.path.parent)
            self.fd = -1


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _file_identity(path: Path) -> dict[str, Any]:
    resolved = path.resolve(strict=True)
    info = resolved.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or path.is_symlink():
        raise V31ContractError(f"unsafe V3.1-U file: {path}")
    return {
        "sha256": sha256(resolved),
        "size": info.st_size,
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
    }


def _seal_tree(root: Path) -> None:
    for path in root.rglob("*"):
        os.chmod(path, 0o555 if path.is_dir() else 0o444)


def _terminalize_failure(root: Path, stage: str, exc: BaseException) -> None:
    try:
        if not (root / "failure.json").exists():
            _exclusive_publish(
                root / "failure.json",
                canonical_bytes(
                    {
                        "schema": "schwo.phase6.v3_1_u.failure.v1",
                        "gate_id": GATE_ID,
                        "stage": stage,
                        "exception_type": type(exc).__name__,
                        "exception_message": str(exc),
                        "scientific_pass": False,
                        "resumable": False,
                    }
                ),
            )
        _seal_tree(root)
        os.chmod(root, 0o755)
        if not (root / "failure_manifest.json").exists():
            _exclusive_publish(
                root / "failure_manifest.json",
                canonical_bytes(build_manifest(root, overall_state="FAILED")),
            )
        os.chmod(root, 0o555)
    except BaseException:
        pass


__all__ = [
    "ARTIFACT_REV",
    "EXPECTED_FIXED_COUNTS",
    "GATE_ID",
    "build_route_map",
    "build_source_ledger",
    "evaluate_all_thresholds",
    "run_official",
    "run_preexecution_sentinels",
    "run_route_c_sentinel",
    "selector_view",
    "solve_route_u_ladder",
    "synthetic_payload",
    "validate_import_isolation",
    "validate_sentinel_invocation",
    "validate_official_candidate",
    "validate_route_map",
    "verify_start_gate",
]


if __name__ == "__main__":
    raise SystemExit(_sentinel_module_main())
