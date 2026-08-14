"""Complete V3.1 repair-cycle-2 orchestration and evidence validation."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import UTC, datetime
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Iterable, Mapping, Sequence

import mpmath as mp

from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
from schwgw.numerics.conditioned_radial import ConditionedRadialRequest
from schwgw.perturbations import Sector
from schwgw.validation.phase6_mpmath_radial import (
    MpmathEvaluationPoint,
    MpmathMode,
    MpmathSolveConfig,
    result_for,
    solve_mode_batch,
)
from schwgw.validation.phase6_v3_continued_jost import (
    continued_jost_geometry,
    solve_continued_jost_node,
)
from schwgw.validation.phase6_v3_mode_greybody_ap import solve_exact_radius_direct
from schwgw.validation.phase6_v3_mode_greybody import (
    BHPT_PACKAGE_ROOT,
    FREQUENCIES,
    ROOT,
    WOLFRAM_KERNEL,
    WOLFRAM_KERNEL_SHA256,
    ModeKey,
    V31ContractError,
    build_anchor_inventory,
    build_inventory_payload,
    build_mode_inventory,
    canonical_bytes,
    run_external_smoke,
    sha256,
)


PACKAGE_PATH = ROOT / "configs/phase6_v3_1_repair_cycle2_package.json"
PACKAGE_SHA256 = "5bce1966b76c85b49c79cb7d98c481403a4b5006bb48bd2d4d47ea67f879b2c4"
DESIGN_PATH = ROOT / "docs/phase6_v3_1_repair_cycle2_design.md"
DESIGN_SHA256 = "746d8753408bdb74cd1a9597108a63cf3c67842dc6cbedcbbb56fb68c0f967a7"
T4_PROMPT_PATH = ROOT / "docs/prompts/phase6_t4_v3_1_repair_cycle2.md"
T4_PROMPT_SHA256 = "f2d0b45613ca8c10c5b36715379f215644dce31079e577ff11279b478ec81ed9"
T7_APPROVAL_PATH = (
    ROOT / "docs/handoffs/archive/T7_2026-08-11_v3_1_repair_cycle2_package_review.md"
)
T7_APPROVAL_SHA256 = "6c3d9371ec2d191f4b6ee10076ad264127bc858142c0972225e2a18638431cc1"
THRESHOLD_PATH = ROOT / "configs/phase6_v3_0_thresholds.json"
EXTERNAL_WLS = ROOT / "scripts/phase6_v3_1_bhpt_mst_cycle2.wls"
EXTERNAL_SNAPSHOT_ROOT = (
    ROOT / "runs/phase6/external_sources/bhpt_reggewheeler_2e012092_v1_20260813/source"
)
EXTERNAL_SNAPSHOT_AUTHORITY = (
    ROOT / "runs/phase6/external_sources/"
    "bhpt_reggewheeler_2e012092_v1_20260813.snapshot.json"
)
EXTERNAL_SNAPSHOT_AUTHORITY_SHA256 = (
    "8d5498ab5f825e721c6cd3764f302831c8b7bcf138a1ee9600a0f5e6f6e4e488"
)
EXTERNAL_CONTENT_INVENTORY_SHA256 = (
    "d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2"
)
EXTERNAL_RESTORED_IDENTITY_SHA256 = (
    "a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27"
)
EXTERNAL_COMMIT_ASSOCIATION = "2e01209271fb3d0d92705d5c27bd9e00a6140981"
EXTERNAL_REQUIRED_DIRECTORY_PATHS = (
    ".",
    "Kernel",
    "Kernel/MST",
    "Tests",
    "Tests/Correctness",
)
# Exact package-entry graph reached by Needs["ReggeWheeler`"] for the frozen
# MST call.  This is deliberately narrower than the 25-file source snapshot:
# documentation, tests, and the unused ConvolveSource implementation are
# authenticated source bytes, but they are not loaded numerical sources.
EXTERNAL_REQUIRED_LOADED_SOURCE_PATHS = (
    "Kernel/ReggeWheeler.m",
    "Kernel/MST/RenormalizedAngularMomentum.m",
    "Kernel/MST/MST.m",
    "Kernel/NumericalIntegration.m",
    "Kernel/Hyperboloidal.wl",
    "Kernel/ReggeWheelerRadial.m",
    "Kernel/ReggeWheelerSource.m",
    "Kernel/ReggeWheelerMode.m",
)
EXTERNAL_ARTIFACT_NAMES = (
    "external_request.json",
    "external_source_start.json",
    "external_prelaunch.json",
    "external_stdout.raw",
    "external_stderr.raw",
    "external_receipt.json",
    "external_child_payload.raw.json",
    "external_attempt_records.jsonl",
    "external_source_end.json",
    "external_terminal.json",
)
MPMATH_BACKEND = ROOT / "src/schwgw/validation/phase6_mpmath_radial.py"
EXPECTED_COUNTS = {
    "route_a_modes": 496,
    "route_a_nodes": 9920,
    "route_b_keys": 102,
    "route_b_nodes": 458,
    "route_c_records": 23,
    "thresholds": 16,
    "certificates": 5,
}
STATUS_START_SHA256 = "a33a7377c2395650c6dea0db3f06a7f51439aaca8658d1eda7774cb3e7218518"
T0_START_SHA256 = "90cc3a70ef07a7356d056cc8a1ae3594b9fb609fed1c8a8560d9b5cfd41c90b3"
CERTIFICATE_IDS = (
    "V3_MODE_GREYBODY_NUMERICAL",
    "V3_MODE_GREYBODY_FLUX_VS_S",
    "V3_MODE_GREYBODY_EXTERNAL",
    "V3_MODE_PARITY_PROBABILITY",
    "V3_MODE_DOMAIN_COVERAGE",
)


def compact_jsonl_record(payload: Mapping[str, Any]) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise V31ContractError(f"JSONL terminal newline missing: {path.name}")
    records: list[dict[str, Any]] = []
    for line in raw.splitlines():
        if not line or b"\n" in line or b"\r" in line:
            raise V31ContractError(f"invalid JSONL physical record: {path.name}")
        value = json.loads(line)
        if (
            not isinstance(value, dict)
            or compact_jsonl_record(value).rstrip(b"\n") != line
        ):
            raise V31ContractError(f"noncanonical JSONL record: {path.name}")
        records.append(value)
    return records


def verify_cycle2_start_gate() -> dict[str, Any]:
    package = json.loads(PACKAGE_PATH.read_text())
    fixed = {
        PACKAGE_PATH: PACKAGE_SHA256,
        DESIGN_PATH: DESIGN_SHA256,
        T4_PROMPT_PATH: T4_PROMPT_SHA256,
        T7_APPROVAL_PATH: T7_APPROVAL_SHA256,
        ROOT / "status.md": STATUS_START_SHA256,
        ROOT / "docs/handoffs/T0_current.md": T0_START_SHA256,
    }
    for item in package["package_members"]:
        fixed[ROOT / item["path"]] = item["sha256"]
    for item in package["protected_radial_files"]:
        fixed[ROOT / item["path"]] = item["sha256"]
    upstream = package["upstream_identities"]
    fixed.update(
        {
            ROOT / "configs/phase6_v3_0_domain.json": upstream["v3_0_authorities"][
                "domain"
            ],
            ROOT / "configs/phase6_v3_0_thresholds.json": upstream["v3_0_authorities"][
                "thresholds"
            ],
            ROOT / "configs/phase6_v3_0_external_anchor_matrix.json": upstream[
                "v3_0_authorities"
            ]["anchor_matrix"],
            ROOT / "docs/phase6_v3_0_validation_contract.md": upstream[
                "v3_0_authorities"
            ]["validation_contract"],
            ROOT / "docs/phase6_v3_0_formula_map.md": upstream["v3_0_authorities"][
                "formula_map"
            ],
            ROOT / "docs/phase6_v3_0_phase_taxonomy.md": upstream["v3_0_authorities"][
                "phase_taxonomy"
            ],
            ROOT / "docs/phase6_v3_0_literature_matrix.md": upstream[
                "v3_0_authorities"
            ]["literature_matrix"],
            ROOT
            / "references/notes/phase6_v3_absorption_scattering_conventions.md": upstream[
                "v3_0_authorities"
            ]["convention_note"],
            ROOT
            / "runs/phase6/radial_validation/v1_final_radial_baseline_v2_20260810_py314/manifest.json": upstream[
                "v1_radial_manifest"
            ],
            ROOT
            / "runs/phase6/radial_validation/v1_production_state_evidence_v2_20260810_py314/manifest.json": upstream[
                "v1_production_radial_states_manifest"
            ],
            ROOT
            / "runs/phase6/radial_validation/v1_radial_selected_acceptance_v1_20260810_py314/manifest.json": upstream[
                "v1_selected_independent_manifest"
            ],
            ROOT
            / "runs/phase6/asymptotic_waveform/v2_selected_release_v2_20260811T083414_py314/manifest.json": upstream[
                "v2_release_manifest"
            ],
            ROOT
            / "runs/phase6/radial_validation/v1_final_radial_baseline_v2_20260810_py314/plan.json": upstream[
                "d_union_plan"
            ]["sha256"],
        }
    )
    identities: dict[str, Any] = {}
    package_member_paths = {
        PACKAGE_PATH,
        *(ROOT / item["path"] for item in package["package_members"]),
    }
    for path, expected in fixed.items():
        resolved = path.resolve(strict=True)
        info = resolved.stat()
        if (
            sha256(resolved) != expected
            or not stat.S_ISREG(info.st_mode)
            or info.st_nlink != 1
            or resolved.is_symlink()
        ):
            raise V31ContractError(f"cycle-2 frozen identity drift: {path}")
        if path in package_member_paths and stat.S_IMODE(info.st_mode) != 0o444:
            raise V31ContractError(f"cycle-2 package mode drift: {path}")
        identities[str(path)] = _file_identity(resolved)
    approval = T7_APPROVAL_PATH.read_text()
    if (
        "ADVANCE_DECISION: ADVANCE" not in approval
        or "CLAIM_STATUS: NOT_ASSESSED" not in approval
        or "ACCEPT GREEN / V3.1 REPAIR CYCLE 2 PACKAGE READY FOR T4" not in approval
        or PACKAGE_SHA256 not in approval
    ):
        raise V31ContractError("formal T7 cycle-2 approval mismatch")
    if sha256(WOLFRAM_KERNEL) != WOLFRAM_KERNEL_SHA256:
        raise V31ContractError("external WolframKernel identity drift")
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=BHPT_PACKAGE_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=BHPT_PACKAGE_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    if commit != upstream["bhpt_reggewheeler"]["commit"] or dirty:
        raise V31ContractError("BHPT source identity drift")
    for failure in package["failure_evidence"].values():
        if isinstance(failure, dict) and "path" in failure and "sha256" in failure:
            path = Path(failure["path"])
            if not path.is_absolute():
                path = ROOT / path
            if sha256(path.resolve(strict=True)) != failure["sha256"]:
                raise V31ContractError("cycle-1 failure identity drift")
    return {"package": package, "identities": identities}


def route_a_node_graph(key: ModeKey) -> list[dict[str, Any]]:
    k = float(key.kM)
    base = max(300.0, math.sqrt(key.ell * (key.ell + 1)) / k)
    candidates: list[dict[str, Any]] = []
    for eps in (1e-8, 1e-10, 1e-12):
        candidates.append(_node(eps, 1, 160, 1e-10, 1e-12, "r_in", base))
    for multiplier in (1, 2, 4, 8):
        for order in (80, 120, 160, 200):
            candidates.append(
                _node(1e-10, multiplier, order, 1e-10, 1e-12, "outer_jost", base)
            )
    for rtol, atol in ((1e-9, 1e-11), (1e-10, 1e-12), (3e-11, 3e-13)):
        candidates.append(_node(1e-10, 1, 160, rtol, atol, "tolerance", base))
    unique: list[dict[str, Any]] = []
    by_tuple: dict[tuple[Any, ...], dict[str, Any]] = {}
    for item in candidates:
        identity = _node_tuple(item)
        if identity in by_tuple:
            by_tuple[identity]["memberships"].extend(item["memberships"])
        else:
            copied = {**item, "memberships": list(item["memberships"])}
            by_tuple[identity] = copied
            unique.append(copied)
    for ordinal, item in enumerate(unique):
        item["node_ordinal"] = ordinal
        item["memberships"] = sorted(set(item["memberships"]))
    if len(unique) != 20:
        raise V31ContractError("Route-A node graph is not exactly 20")
    return unique


def solve_route_a_mode(key: ModeKey) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    for node in route_a_node_graph(key):
        records.append(_solve_route_a_node_record(key, node))
    baseline = _route_a_baseline(records)
    metrics = route_a_mode_metrics(records)
    return (
        {
            "schema": "schwo.phase6.v3_1.route_a_mode_record.v2",
            "mode": key.payload(),
            "baseline": baseline["result"],
            "metrics": metrics,
            "node_count": 20,
            "protected_call_count": 20,
        },
        records,
    )


def _solve_route_a_node_record(key: ModeKey, node: Mapping[str, Any]) -> dict[str, Any]:
    request = ConditionedRadialRequest(
        sector=Sector(key.parity),
        ell=key.ell,
        k=float(key.kM),
        required_radius=40.0,
        r_out=float(node["r_out"]),
        r_in_eps=float(node["r_in_eps"]),
        rtol=float(node["rtol"]),
        atol=float(node["atol"]),
        outer_series_order=int(node["jost_order"]),
    )
    started = time.perf_counter()
    result = solve_continued_jost_node(request, SchwarzschildBackground(M=1.0))
    return {
        "schema": "schwo.phase6.v3_1.route_a_ladder_record.v2",
        "mode": key.payload(),
        "node": dict(node),
        "elapsed_seconds": time.perf_counter() - started,
        "result": result,
        "scientific_evidence": True,
    }


def route_a_mode_metrics(records: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    if len(records) != 20:
        raise V31ContractError("Route-A mode ladder is incomplete")
    lookup = {_node_tuple(item["node"]): item for item in records}
    rin = [lookup[(eps, 1, 160, 1e-10, 1e-12)] for eps in (1e-8, 1e-10, 1e-12)]
    tol = [
        lookup[(1e-10, 1, 160, rtol, atol)]
        for rtol, atol in ((1e-9, 1e-11), (1e-10, 1e-12), (3e-11, 3e-13))
    ]
    outer_pairs: list[tuple[Mapping[str, Any], Mapping[str, Any]]] = []
    for multiplier in (1, 2, 4, 8):
        row = [
            lookup[(1e-10, multiplier, order, 1e-10, 1e-12)]
            for order in (80, 120, 160, 200)
        ]
        outer_pairs.extend(zip(row, row[1:]))
    for order in (80, 120, 160, 200):
        column = [
            lookup[(1e-10, multiplier, order, 1e-10, 1e-12)]
            for multiplier in (1, 2, 4, 8)
        ]
        outer_pairs.extend(zip(column, column[1:]))
    return {
        "rin_s_max": _max_s_pairs(zip(rin, rin[1:])),
        "rin_log_gamma_max": _max_log_pairs(zip(rin, rin[1:])),
        "outer_jost_s_max": _max_s_pairs(outer_pairs),
        "outer_jost_log_gamma_max": _max_log_pairs(outer_pairs),
        "tolerance_s_max": _max_s_pairs(zip(tol, tol[1:])),
        "tolerance_log_gamma_max": _max_log_pairs(zip(tol, tol[1:])),
    }


def ap_node_plan() -> list[dict[str, Any]]:
    inventory = build_mode_inventory()
    anchors = build_anchor_inventory(inventory)["ap"]
    turning = "V3A-MODE-AP-TURNING-001"
    nodes: list[dict[str, Any]] = []
    for key_ordinal, item in enumerate(anchors):
        for dps in (80, 120, 180):
            nodes.append(_ap_node(key_ordinal, item, dps, 1e-10, 1, 160, "precision"))
        if turning in item["memberships"]:
            nodes.extend(
                (
                    _ap_node(key_ordinal, item, 180, 1e-8, 1, 160, "turning_rin"),
                    _ap_node(key_ordinal, item, 180, 1e-12, 1, 160, "turning_rin"),
                    _ap_node(key_ordinal, item, 180, 1e-10, 2, 160, "turning_outer"),
                    _ap_node(key_ordinal, item, 180, 1e-10, 1, 200, "turning_jost"),
                )
            )
    for ordinal, item in enumerate(nodes):
        item["node_ordinal"] = ordinal
    if len(anchors) != 102 or len(nodes) != 458:
        raise V31ContractError("Route-B AP inventory mismatch")
    return nodes


def solve_ap_node(node: Mapping[str, Any]) -> dict[str, Any]:
    item = node["key"]
    k = float(item["kM"])
    ell = int(item["ell"])
    r_base = max(300.0, math.sqrt(ell * (ell + 1)) / k)
    r_match = r_base * int(node["r_out_multiplier"])
    geometry = continued_jost_geometry(ell=ell, k=k, r_match=r_match)
    mode = MpmathMode(
        f"v31_{item['kM']}_{item['parity']}_{ell}",
        "v3_1_ap_anchor",
        item["parity"],
        ell,
        k,
        40.0,
    )
    config = MpmathSolveConfig(
        working_dps=int(node["dps"]),
        r_in_eps=float(node["r_in_eps"]),
        maximum_step_rstar=min(0.2, 0.015 / k),
        pilot_match_radius_M=r_match,
    )
    point = MpmathEvaluationPoint("required_radius_40M", "40")
    if geometry.auxiliary_exponent == 0:
        batch = solve_exact_radius_direct(
            mode,
            config,
            evaluation_point=point,
            match_radius=r_match,
            jost_order=int(node["jost_order"]),
        )
        result = batch["result"]
    else:
        batch = solve_mode_batch(
            mode,
            config,
            evaluation_points=(point,),
            r_out_nodes=(geometry.jost_initialization_radius,),
            jost_orders=(int(node["jost_order"]),),
        )
        result = result_for(
            batch,
            r_out=geometry.jost_initialization_radius,
            jost_order=int(node["jost_order"]),
        )
    return {
        "schema": "schwo.phase6.v3_1.ap_record.v2",
        "node": dict(node),
        "geometry": asdict(geometry),
        "result": result,
        "integration_steps": batch["integration_steps"],
        "elapsed_seconds": batch["elapsed_seconds"],
        "route_a_code_shared": False,
        "protected_radial_imported": False,
        "scientific_evidence": True,
    }


def external_source_identity(
    *, runtime_observed: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Rebuild the stable external-source identity without invoking Wolfram."""

    authority_identity = _file_identity(EXTERNAL_SNAPSHOT_AUTHORITY)
    if authority_identity["sha256"] != EXTERNAL_SNAPSHOT_AUTHORITY_SHA256:
        raise V31ContractError("external snapshot authority drift")
    authority = json.loads(EXTERNAL_SNAPSHOT_AUTHORITY.read_text())
    restoration = authority.get("restoration", {})
    historical = authority.get("historical_authority", {})
    audit = authority.get("audit_archive", {})
    if (
        authority.get("schema") != "schwo.phase6.external_source_snapshot.v1"
        or restoration.get("root") != str(EXTERNAL_SNAPSHOT_ROOT.relative_to(ROOT))
        or restoration.get("file_count") != 25
        or restoration.get("content_inventory_sha256")
        != EXTERNAL_CONTENT_INVENTORY_SHA256
        or restoration.get("restored_identity_inventory_sha256")
        != EXTERNAL_RESTORED_IDENTITY_SHA256
        or historical.get("commit_assertion") != EXTERNAL_COMMIT_ASSOCIATION
    ):
        raise V31ContractError("external snapshot authority semantics drift")
    audit_path = ROOT / str(audit.get("path", ""))
    audit_identity = _file_identity(audit_path)
    if audit_identity["sha256"] != audit.get("sha256"):
        raise V31ContractError("external audit archive identity drift")
    historical_ledger_path = ROOT / str(
        historical.get("immutable_source_ledger_path", "")
    )
    historical_ledger_identity = _file_identity(historical_ledger_path)
    if historical_ledger_identity["sha256"] != historical.get(
        "immutable_source_ledger_sha256"
    ):
        raise V31ContractError("external historical source-ledger identity drift")
    expected_records = authority.get("source_content_records")
    if not isinstance(expected_records, list) or len(expected_records) != 25:
        raise V31ContractError("external snapshot file inventory malformed")
    expected_by_path = {item["path"]: item for item in expected_records}
    if len(expected_by_path) != 25 or any(
        ".git" in Path(p).parts for p in expected_by_path
    ):
        raise V31ContractError("external snapshot path inventory malformed")
    files, directories = _validate_external_snapshot_tree(
        EXTERNAL_SNAPSHOT_ROOT, expected_by_path
    )
    content_projection = [
        {"path": item["path"], "sha256": item["sha256"], "size": item["size"]}
        for item in files
    ]
    identity_projection = files
    if (
        hashlib.sha256(canonical_bytes(content_projection)).hexdigest()
        != EXTERNAL_CONTENT_INVENTORY_SHA256
    ):
        raise V31ContractError("external content inventory digest drift")
    if (
        hashlib.sha256(canonical_bytes(identity_projection)).hexdigest()
        != EXTERNAL_RESTORED_IDENTITY_SHA256
    ):
        raise V31ContractError("external restored identity digest drift")
    required_loaded_source_records = [
        {
            "path": str((EXTERNAL_SNAPSHOT_ROOT / relative).resolve(strict=True)),
            "sha256": expected_by_path[relative]["sha256"],
            "size": expected_by_path[relative]["size"],
        }
        for relative in EXTERNAL_REQUIRED_LOADED_SOURCE_PATHS
    ]
    kernel = _file_identity(WOLFRAM_KERNEL)
    if kernel["sha256"] != WOLFRAM_KERNEL_SHA256:
        raise V31ContractError("external WolframKernel identity drift")
    static = {
        "schema": "schwo.phase6.v3_1_u.external_source_identity.v1",
        "wls": _file_identity(EXTERNAL_WLS),
        "python_runner": _file_identity(Path(__file__).resolve()),
        "wolfram_kernel": {"path": str(WOLFRAM_KERNEL), **kernel},
        "snapshot_authority": {
            "path": str(EXTERNAL_SNAPSHOT_AUTHORITY),
            **authority_identity,
        },
        "audit_archive": {"path": str(audit_path), **audit_identity},
        "historical_source_ledger": {
            "path": str(historical_ledger_path),
            **historical_ledger_identity,
        },
        "snapshot_root": str(EXTERNAL_SNAPSHOT_ROOT),
        "source_files": files,
        "source_directories": directories,
        "required_loaded_source_records": required_loaded_source_records,
        "content_inventory_sha256": EXTERNAL_CONTENT_INVENTORY_SHA256,
        "restored_identity_inventory_sha256": EXTERNAL_RESTORED_IDENTITY_SHA256,
        "historical_commit_association": EXTERNAL_COMMIT_ASSOCIATION,
        "snapshot_contains_git_metadata": False,
        "commit_proof_nonclaim": (
            "commit association inherited only from immutable historical ledger "
            "and exact 25-file byte equality; restored snapshot has no .git"
        ),
    }
    if runtime_observed is not None:
        _validate_external_runtime_observed(
            runtime_observed,
            expected_by_path,
            required_loaded_source_records,
        )
        static["runtime_observed"] = dict(runtime_observed)
    return static


def validate_external_child_payload(
    payload: Mapping[str, Any], anchors: Sequence[Mapping[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """Validate exact 23-outcome totality and disjoint PASS/ERROR schemas."""

    expected_header = {
        "schema",
        "terminal",
        "requested_anchor_count",
        "outcome_count",
        "outcomes",
        "fresh_external_call_count",
        "overall_status",
        "first_failure",
        "wolfram_version",
        "system_id",
        "loaded_source_records",
        "method_contract",
    }
    if (
        set(payload) != expected_header
        or payload.get("schema") != "schwo.phase6.v3_1_u.external_batch_terminal.v1"
        or payload.get("terminal") is not True
    ):
        raise V31ContractError("external child terminal envelope schema mismatch")
    outcomes = payload.get("outcomes")
    if (
        not isinstance(outcomes, list)
        or len(outcomes) != 23
        or payload.get("outcome_count") != 23
        or payload.get("requested_anchor_count") != 23
    ):
        raise V31ContractError("external Route-C outcome cardinality mismatch")
    pass_keys = {
        "schema",
        "ordinal",
        "key",
        "status",
        "method",
        "fresh_external_call_count",
        "genuinely_independent",
        "even_independent_solve",
        "incidence",
        "reflection",
        "transmission",
        "reflection_ratio",
        "S",
        "T_horizon",
        "Gamma_flux",
        "log_Gamma_flux",
    }
    error_keys = {
        "schema",
        "ordinal",
        "key",
        "status",
        "error",
        "fresh_external_call_count",
    }
    records: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for ordinal, (outcome, expected_key) in enumerate(zip(outcomes, anchors)):
        if (
            not isinstance(outcome, Mapping)
            or outcome.get("schema") != "schwo.phase6.v3_1_u.external_anchor_outcome.v1"
            or outcome.get("ordinal") != ordinal
            or outcome.get("key") != expected_key
        ):
            raise V31ContractError("external Route-C outcome order/key mismatch")
        status_value = outcome.get("status")
        if status_value == "PASS":
            if (
                set(outcome) != pass_keys
                or outcome.get("method") != "MST"
                or outcome.get("fresh_external_call_count") != 1
                or outcome.get("genuinely_independent") is not True
                or outcome.get("even_independent_solve") is not False
            ):
                raise V31ContractError("external Route-C PASS schema mismatch")
            complex_values = {}
            for field in (
                "incidence",
                "reflection",
                "transmission",
                "reflection_ratio",
                "S",
                "T_horizon",
            ):
                complex_values[field] = _validate_external_complex(outcome[field])
            gamma = mp.mpf(str(outcome["Gamma_flux"]).replace("*^", "e"))
            log_gamma = mp.mpf(str(outcome["log_Gamma_flux"]).replace("*^", "e"))
            if (
                not mp.isfinite(gamma)
                or not mp.isfinite(log_gamma)
                or gamma <= 0
                or complex_values["incidence"] == 0
                or abs(abs(complex_values["T_horizon"]) ** 2 - gamma)
                > mp.mpf("1e-40") * max(mp.mpf(1), gamma)
                or abs(mp.log(gamma) - log_gamma) > mp.mpf("1e-40")
            ):
                raise V31ContractError("external Route-C amplitude identity mismatch")
            records.append(dict(outcome))
        elif status_value == "ERROR":
            error = outcome.get("error")
            if (
                set(outcome) != error_keys
                or not isinstance(error, Mapping)
                or set(error) != {"code", "detail"}
                or error.get("code")
                not in {"MST_FAILED", "AMPLITUDE_INVALID", "PACKAGE_LOAD_FAILED"}
                or not all(isinstance(error[k], str) and error[k] for k in error)
                or outcome.get("fresh_external_call_count")
                != (0 if error["code"] == "PACKAGE_LOAD_FAILED" else 1)
            ):
                raise V31ContractError("external Route-C ERROR schema mismatch")
            failures.append(dict(outcome))
        else:
            raise V31ContractError("external Route-C unknown outcome status")
    first_failure = (
        None
        if not failures
        else {
            "ordinal": failures[0]["ordinal"],
            "key": failures[0]["key"],
            "error": failures[0]["error"],
        }
    )
    if (
        payload.get("first_failure") != first_failure
        or payload.get("overall_status")
        != ("PASS" if first_failure is None else "ERROR")
        or payload.get("fresh_external_call_count")
        != sum(int(item["fresh_external_call_count"]) for item in outcomes)
    ):
        raise V31ContractError("external Route-C terminal summary mismatch")
    method = payload.get("method_contract")
    if method != {
        "Method": "MST",
        "WorkingPrecision": 90,
        "PrecisionGoal": 45,
        "AccuracyGoal": 45,
        "Potential": "ReggeWheeler",
        "BoundaryConditions": "In",
    }:
        raise V31ContractError("external Route-C method contract drift")
    return records, first_failure


def _validate_external_complex(value: Any) -> mp.mpc:
    if not isinstance(value, Mapping) or set(value) != {"real", "imag"}:
        raise V31ContractError("external Route-C complex schema mismatch")
    real = mp.mpf(str(value["real"]).replace("*^", "e"))
    imag = mp.mpf(str(value["imag"]).replace("*^", "e"))
    if not mp.isfinite(real) or not mp.isfinite(imag):
        raise V31ContractError("external Route-C nonfinite amplitude")
    return mp.mpc(real, imag)


def run_external_records(evidence_root: Path) -> list[dict[str, Any]]:
    """Launch the one-shot 23-anchor child and durably close every branch."""

    evidence_root.mkdir(mode=0o700, parents=False, exist_ok=False)
    anchors = build_anchor_inventory(build_mode_inventory())["external"]
    source_start = external_source_identity()
    request_payload = {
        "schema": "schwo.phase6.v3_1_u.external_request.v1",
        "anchors": anchors,
        "method_contract": {
            "Method": "MST",
            "WorkingPrecision": 90,
            "PrecisionGoal": 45,
            "AccuracyGoal": 45,
            "Potential": "ReggeWheeler",
            "BoundaryConditions": "In",
            "sector": "odd",
            "even_independent_solve": False,
        },
        "snapshot_root": str(EXTERNAL_SNAPSHOT_ROOT),
    }
    request = evidence_root / "external_request.json"
    child_payload_path = evidence_root / "external_child_payload.raw.json"
    _exclusive_publish(request, canonical_bytes(request_payload))
    _exclusive_publish(
        evidence_root / "external_source_start.json", canonical_bytes(source_start)
    )
    argv = [str(WOLFRAM_KERNEL), "-noprompt", "-script", str(EXTERNAL_WLS)]
    environment = os.environ.copy()
    environment.update(
        {
            "SCHWO_V31_BHPT_PACKAGE_ROOT": str(EXTERNAL_SNAPSHOT_ROOT),
            "SCHWO_V31_BHPT_INPUT": str(request),
            "SCHWO_V31_BHPT_OUTPUT": str(child_payload_path),
        }
    )
    _exclusive_publish(
        evidence_root / "external_prelaunch.json",
        canonical_bytes(
            {
                "schema": "schwo.phase6.v3_1_u.external_prelaunch.v1",
                "argv": argv,
                "cwd": str(ROOT),
                "environment": {
                    key: environment[key]
                    for key in sorted(environment)
                    if key.startswith("SCHWO_V31_")
                },
                "source_start_sha256": hashlib.sha256(
                    canonical_bytes(source_start)
                ).hexdigest(),
            }
        ),
    )
    stdout_path = evidence_root / "external_stdout.raw"
    stderr_path = evidence_root / "external_stderr.raw"
    stdout_fd = _exclusive_stream_fd(stdout_path)
    stderr_fd = _exclusive_stream_fd(stderr_path)
    started = time.monotonic_ns()
    process: subprocess.Popen[bytes] | None = None
    timed_out = threading.Event()
    timer: threading.Timer | None = None
    returncode: int | None = None
    launch_error: BaseException | None = None
    try:
        process = subprocess.Popen(
            argv,
            cwd=ROOT,
            env=environment,
            stdout=stdout_fd,
            stderr=stderr_fd,
            start_new_session=True,
        )
        timer = threading.Timer(1800.0, _kill_for_timeout, args=(process, timed_out))
        timer.start()
        returncode = process.wait()
    except BaseException as exc:
        launch_error = exc
    finally:
        if timer is not None:
            timer.cancel()
        for fd in (stdout_fd, stderr_fd):
            os.fsync(fd)
            os.close(fd)
        os.chmod(stdout_path, 0o444)
        os.chmod(stderr_path, 0o444)
    elapsed = time.monotonic_ns() - started
    signal_value = -returncode if returncode is not None and returncode < 0 else None
    process_group_empty = True if process is None else _process_group_empty(process.pid)
    receipt = {
        "schema": "schwo.phase6.v3_1_u.external_receipt.v1",
        "pid": None if process is None else process.pid,
        "returncode": returncode,
        "signal": signal_value,
        "sid": None if process is None else process.pid,
        "pgid": None if process is None else process.pid,
        "timeout": timed_out.is_set(),
        "wait_calls": 1 if process is not None else 0,
        "reaped": process is not None and process.poll() is not None,
        "process_group_empty": process_group_empty,
        "wait_error_count": 0 if launch_error is None else 1,
        "elapsed_ns": elapsed,
        "launch_error": None
        if launch_error is None
        else {"type": type(launch_error).__name__, "message": str(launch_error)},
        "stdout": _file_identity(stdout_path),
        "stderr": _file_identity(stderr_path),
    }
    _exclusive_publish(
        evidence_root / "external_receipt.json", canonical_bytes(receipt)
    )
    payload: Mapping[str, Any] | None = None
    parse_error: str | None = None
    records: list[dict[str, Any]] = []
    first_failure: dict[str, Any] | None = None
    if not child_payload_path.exists():
        _exclusive_publish(child_payload_path, b"")
    if child_payload_path.is_file() and not child_payload_path.is_symlink():
        _fsync_existing(child_payload_path)
        os.chmod(child_payload_path, 0o444)
        try:
            payload_value = _load_strict_json(child_payload_path)
            if not isinstance(payload_value, Mapping):
                raise V31ContractError("external child payload is not an object")
            payload = payload_value
            records, first_failure = validate_external_child_payload(payload, anchors)
        except BaseException as exc:
            parse_error = f"{type(exc).__name__}: {exc}"
    else:
        parse_error = "external child payload missing"
    attempts = (
        []
        if payload is None or not isinstance(payload.get("outcomes"), list)
        else list(payload["outcomes"])
    )
    with _JsonlWriter(evidence_root / "external_attempt_records.jsonl") as writer:
        for item in attempts:
            _append_jsonl(writer, item)
    observed = (
        None
        if payload is None
        else {
            "wolfram_version": payload.get("wolfram_version"),
            "system_id": payload.get("system_id"),
            "loaded_source_records": payload.get("loaded_source_records"),
        }
    )
    source_end_error: str | None = None
    try:
        source_end = (
            external_source_identity(runtime_observed=observed)
            if observed is not None
            else external_source_identity()
        )
    except BaseException as exc:
        source_end_error = f"{type(exc).__name__}: {exc}"
        source_end = {
            "schema": "schwo.phase6.v3_1_u.external_source_end_failure.v1",
            "error": source_end_error,
        }
    _exclusive_publish(
        evidence_root / "external_source_end.json", canonical_bytes(source_end)
    )
    terminal_pass = (
        launch_error is None
        and returncode == 0
        and not timed_out.is_set()
        and process_group_empty
        and stderr_path.stat().st_size == 0
        and parse_error is None
        and source_end_error is None
        and len(records) == 23
        and first_failure is None
        and {k: v for k, v in source_end.items() if k != "runtime_observed"}
        == source_start
    )
    terminal = {
        "schema": "schwo.phase6.v3_1_u.external_terminal.v1",
        "status": "PASS" if terminal_pass else "ERROR",
        "terminal": True,
        "non_resumable": True,
        "retry_permitted": False,
        "receipt": _file_identity(evidence_root / "external_receipt.json"),
        "child_payload": _file_identity(child_payload_path)
        if child_payload_path.is_file()
        else None,
        "attempt_records": _file_identity(
            evidence_root / "external_attempt_records.jsonl"
        ),
        "outcome_count": len(attempts),
        "pass_count": len(records),
        "first_failure": first_failure,
        "parse_error": parse_error,
        "source_end_error": source_end_error,
    }
    _exclusive_publish(
        evidence_root / "external_terminal.json", canonical_bytes(terminal)
    )
    if terminal_pass:
        with _JsonlWriter(evidence_root / "external_records.jsonl") as writer:
            for record in records:
                _append_jsonl(writer, record)
        _exclusive_publish(
            evidence_root / "external_result.json",
            canonical_bytes(
                {
                    "schema": "schwo.phase6.v3_1_u.external_result.v1",
                    "status": "PASS",
                    "record_count": 23,
                    "records": _file_identity(evidence_root / "external_records.jsonl"),
                    "terminal": _file_identity(
                        evidence_root / "external_terminal.json"
                    ),
                }
            ),
        )
        return records
    _exclusive_publish(
        evidence_root / "external_failure.json",
        canonical_bytes(
            {
                "schema": "schwo.phase6.v3_1_u.external_failure.v1",
                "status": "ERROR",
                "scientific_pass": False,
                "non_resumable": True,
                "first_failure": first_failure,
                "parse_error": parse_error,
                "source_end_error": source_end_error,
                "returncode": returncode,
                "signal": signal_value,
                "timeout": timed_out.is_set(),
            }
        ),
    )
    _exclusive_publish(
        evidence_root / "external_failure_manifest.json",
        canonical_bytes(
            {
                "schema": "schwo.phase6.v3_1_u.external_failure_manifest.v1",
                "status": "FAILED",
                "artifacts": {
                    p.name: _file_identity(p)
                    for p in sorted(evidence_root.iterdir())
                    if p.is_file() and p.name != "external_failure_manifest.json"
                },
            }
        ),
    )
    raise V31ContractError("external Route-C terminal failure")


def synthetic_payload() -> dict[str, Any]:
    inventory = build_inventory_payload()
    modes = build_mode_inventory()
    route_a_nodes = sum(len(route_a_node_graph(key)) for key in modes)
    ap_nodes = ap_node_plan()
    return {
        "schema": "schwo.phase6.v3_1.synthetic_full_route.v2",
        "scientific_evidence": False,
        "science_executed": False,
        "kernel_unit_test_only": True,
        "counts": {
            "route_a_modes": len(modes),
            "route_a_nodes": route_a_nodes,
            "route_b_keys": inventory["route_b_mode_count"],
            "route_b_nodes": len(ap_nodes),
            "route_c_records": inventory["route_c_mode_count"],
            "thresholds": len(_v31_thresholds()),
            "certificates": len(CERTIFICATE_IDS),
        },
        "certificates": [
            {"certificate_id": value, "status": "SYNTHETIC_PASS"}
            for value in CERTIFICATE_IDS
        ],
    }


def publish_synthetic_root(root: Path) -> dict[str, Any]:
    root.mkdir(mode=0o700, parents=False, exist_ok=False)
    payload = synthetic_payload()
    if payload["counts"] != EXPECTED_COUNTS:
        raise V31ContractError("synthetic exact count mismatch")
    identity = _exclusive_publish(root / "synthetic.json", canonical_bytes(payload))
    manifest = _exclusive_publish(
        root / "manifest.json",
        canonical_bytes(
            {
                "schema": "schwo.phase6.v3_1.synthetic_manifest.v2",
                "artifact": identity,
                "scientific_evidence": False,
            }
        ),
    )
    validate_synthetic_root(root)
    return {"root": str(root), "manifest": manifest, "counts": payload["counts"]}


def validate_synthetic_root(root: Path) -> None:
    manifest = json.loads((root / "manifest.json").read_text())
    artifact = manifest["artifact"]
    path = root / "synthetic.json"
    if _file_identity(path) != artifact:
        raise V31ContractError("synthetic artifact identity mismatch")
    payload = json.loads(path.read_text())
    if (
        payload["counts"] != EXPECTED_COUNTS
        or payload["scientific_evidence"] is not False
    ):
        raise V31ContractError("synthetic payload mismatch")


def threshold_boundary_status(field_id: str, observed: float) -> str:
    """Apply exactly one frozen V3.1 upper-bound threshold."""

    thresholds = {item["field_id"]: item for item in _v31_thresholds()}
    if field_id not in thresholds or not math.isfinite(observed) or observed < 0:
        raise V31ContractError("invalid frozen threshold observation")
    return "PASS" if observed <= float(thresholds[field_id]["value"]) else "FAIL"


def run_preexecution_sentinels(output: Path) -> dict[str, Any]:
    """Run every frozen real pre-execution sentinel outside official evidence."""

    if output.exists():
        raise V31ContractError("sentinel output collision")
    verify_cycle2_start_gate()
    all_modes = build_mode_inventory()
    lookup = {(key.kM, key.ell, key.parity): key for key in all_modes}
    started = time.perf_counter()

    first_key = lookup[("0.005", 2, "odd")]
    first_mode, first_records = solve_route_a_mode(first_key)
    first_metrics = first_mode["metrics"]
    metric_fields = {
        "rin_s_max": "V3T-RIN-S-001",
        "rin_log_gamma_max": "V3T-RIN-LOGGAMMA-001",
        "outer_jost_s_max": "V3T-ROUT-JOST-S-001",
        "outer_jost_log_gamma_max": "V3T-ROUT-JOST-LOGGAMMA-001",
        "tolerance_s_max": "V3T-TOLERANCE-S-001",
        "tolerance_log_gamma_max": "V3T-TOLERANCE-LOGGAMMA-001",
    }
    first_outcomes = {
        field: threshold_boundary_status(field_id, first_metrics[field])
        for field, field_id in metric_fields.items()
    }
    if len(first_records) != 20 or set(first_outcomes.values()) != {"PASS"}:
        raise V31ContractError("first-key exact 20-node sentinel failed")

    direct = next(
        item
        for item in first_records
        if _node_tuple(item["node"]) == (1e-10, 4, 160, 1e-10, 1e-12)
    )
    shadow_request = ConditionedRadialRequest(
        sector=Sector.ODD,
        ell=2,
        k=0.005,
        required_radius=40.0,
        r_out=float(direct["node"]["r_out"]),
        r_in_eps=1e-10,
        rtol=1e-10,
        atol=1e-12,
        outer_series_order=160,
    )
    shadow_result = solve_continued_jost_node(
        shadow_request,
        SchwarzschildBackground(M=1.0),
        shadow_auxiliary_exponent=1,
    )
    shadow_s = _sre(direct["result"]["S"], shadow_result["S"])
    shadow_log = abs(
        float(direct["result"]["log_Gamma_flux"])
        - float(shadow_result["log_Gamma_flux"])
    )
    if (
        threshold_boundary_status("V3T-S-COMPLEX-001", shadow_s) != "PASS"
        or threshold_boundary_status("V3T-ROUT-JOST-LOGGAMMA-001", shadow_log) != "PASS"
    ):
        raise V31ContractError("direct-versus-shadow continuation sentinel failed")

    stratum_keys = (
        ("0.005", 2, "odd"),
        ("0.005", 2, "even"),
        ("0.01", 12, "odd"),
        ("0.01", 12, "even"),
        ("2", 10, "odd"),
        ("2", 10, "even"),
        ("8", 49, "odd"),
        ("8", 49, "even"),
    )
    strata: list[dict[str, Any]] = []
    stratum_baselines: dict[tuple[str, int, str], Mapping[str, Any]] = {}
    route_a_seconds: list[float] = []
    baseline_tuple = (1e-10, 1, 160, 1e-10, 1e-12)
    for identity in stratum_keys:
        key = lookup[identity]
        baseline_node = next(
            node
            for node in route_a_node_graph(key)
            if _node_tuple(node) == baseline_tuple
        )
        record = _solve_route_a_node_record(key, baseline_node)
        baseline = record["result"]
        if baseline["diagnostics"]["protected_route_a_call_count"] != 1:
            raise V31ContractError("stratum protected call count mismatch")
        stratum_baselines[identity] = baseline
        route_a_seconds.append(float(record["elapsed_seconds"]))
        strata.append({"mode": key.payload(), "baseline_record": record})

    ap_records: list[dict[str, Any]] = []
    ap_seconds: list[float] = []
    plan = ap_node_plan()
    for identity in (
        ("0.005", 2, "odd"),
        ("0.005", 2, "even"),
        ("2", 10, "odd"),
        ("2", 10, "even"),
    ):
        for dps in (80, 120):
            selected = [
                node
                for node in plan
                if node["key"]["kM"] == identity[0]
                and int(node["key"]["ell"]) == identity[1]
                and node["key"]["parity"] == identity[2]
                and node["dps"] == dps
                and node["membership"] == "precision"
            ]
            if len(selected) != 1:
                raise V31ContractError("AP sentinel node is not unique")
            record = solve_ap_node(selected[0])
            ap_records.append(record)
            ap_seconds.append(float(record["elapsed_seconds"]))
    for identity in (
        ("0.005", 2, "odd"),
        ("0.005", 2, "even"),
        ("2", 10, "odd"),
        ("2", 10, "even"),
    ):
        records = [
            item
            for item in ap_records
            if (
                item["node"]["key"]["kM"],
                int(item["node"]["key"]["ell"]),
                item["node"]["key"]["parity"],
            )
            == identity
        ]
        records.sort(key=lambda item: item["node"]["dps"])
        if len(records) != 2:
            raise V31ContractError("AP sentinel precision pair incomplete")
        precision_s = _mp_symmetric_relative(
            _mp_complex(records[0]["result"]["S"]),
            _mp_complex(records[1]["result"]["S"]),
        )
        precision_log = float(
            abs(_mp_log_gamma(records[0]) - _mp_log_gamma(records[1]))
        )
        route_s = _mp_symmetric_relative(
            _mp_complex(stratum_baselines[identity]["S"]),
            _mp_complex(records[1]["result"]["S"]),
        )
        route_log = float(
            abs(
                mp.mpf(str(stratum_baselines[identity]["log_Gamma_flux"]))
                - _mp_log_gamma(records[1])
            )
        )
        for field_id, value in (
            ("V3T-PRECISION-S-001", precision_s),
            ("V3T-PRECISION-LOGGAMMA-001", precision_log),
            ("V3T-S-COMPLEX-001", route_s),
            ("V3T-LOGGAMMA-001", route_log),
        ):
            if threshold_boundary_status(field_id, value) != "PASS":
                raise V31ContractError(f"AP sentinel threshold failed: {field_id}")

    external_path = output.with_suffix(".external.json")
    external_started = time.perf_counter()
    external = run_external_smoke(external_path)
    external_seconds = time.perf_counter() - external_started
    if external["fresh_external_call_count"] != 1:
        raise V31ContractError("external sentinel call count mismatch")

    free_bytes = shutil.disk_usage(ROOT).free
    projected_seconds = (
        (sum(route_a_seconds) / len(route_a_seconds)) * 9920
        + (sum(ap_seconds) / len(ap_seconds)) * 458
        + external_seconds * 23
    )
    resource_projection = {
        "route_a_node_seconds_mean": sum(route_a_seconds) / len(route_a_seconds),
        "route_b_node_seconds_mean": sum(ap_seconds) / len(ap_seconds),
        "route_c_record_seconds": external_seconds,
        "projected_total_seconds": projected_seconds,
        "projected_output_bytes": 512 * 1024 * 1024,
        "free_bytes": free_bytes,
        "disk_gate_passed": free_bytes >= 2 * 1024 * 1024 * 1024,
    }
    if not resource_projection["disk_gate_passed"]:
        raise V31ContractError("official resource disk gate failed")
    payload = {
        "schema": "schwo.phase6.v3_1.preexecution_sentinels.v2",
        "scientific_evidence": False,
        "science_executed": True,
        "kernel_unit_test_only": True,
        "first_key": {
            "mode": first_mode,
            "records": first_records,
            "threshold_outcomes": first_outcomes,
        },
        "direct_shadow": {
            "direct": direct,
            "shadow": shadow_result,
            "S_symmetric_relative": shadow_s,
            "log_Gamma_absolute_difference": shadow_log,
        },
        "strata": strata,
        "ap_records": ap_records,
        "external": external,
        "resource_projection": resource_projection,
        "elapsed_seconds": time.perf_counter() - started,
    }
    _exclusive_publish(output, canonical_bytes(payload))
    _file_identity(external_path)
    return payload


def run_official_cycle2(root: Path) -> dict[str, Any]:
    """Execute the unique complete r3 candidate after external preflight gates."""

    root = root.resolve()
    root.mkdir(mode=0o700, parents=False, exist_ok=False)
    lock = root / ".writer.lock"
    lock_fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    started = time.perf_counter()
    current_stage = "prelaunch"
    try:
        start_gate = verify_cycle2_start_gate()
        source_start = build_source_ledger(start_gate)
        inventory = build_inventory_payload()
        _exclusive_publish(root / "inventory.json", canonical_bytes(inventory))
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
        ladder_path = root / "ladder_records.jsonl"
        records_path = root / "records.jsonl"
        with (
            _exclusive_jsonl_writer(ladder_path) as ladder_writer,
            _exclusive_jsonl_writer(records_path) as mode_writer,
        ):
            for ordinal, key in enumerate(build_mode_inventory()):
                mode, ladder = solve_route_a_mode(key)
                for item in ladder:
                    _append_jsonl(ladder_writer, item)
                _append_jsonl(mode_writer, mode)
                ladder_records.extend(ladder)
                mode_records.append(mode)
                mode_blockers = _mode_threshold_blockers(mode)
                _exclusive_publish(
                    checkpoints / f"route_a_{ordinal:04d}.json",
                    canonical_bytes(
                        {
                            "schema": "schwo.phase6.v3_1.mode_checkpoint.v2",
                            "ordinal": ordinal,
                            "mode": key.payload(),
                            "status": (
                                "FAILED_SCIENTIFIC"
                                if mode_blockers
                                else "COMPUTED_NOT_ACCEPTED"
                            ),
                            "blocking_thresholds": mode_blockers,
                        }
                    ),
                )
                if mode_blockers:
                    _exclusive_publish(
                        root / "failed_evaluation.json",
                        canonical_bytes(
                            {
                                "schema": "schwo.phase6.v3_1.early_mode_failure.v2",
                                "mode_ordinal": ordinal,
                                "mode": key.payload(),
                                "blocking_thresholds": mode_blockers,
                                "scientific_pass": False,
                            }
                        ),
                    )
                    raise V31ContractError("official V3.1 per-mode threshold failure")
        current_stage = "route_b"
        ap_records: list[dict[str, Any]] = []
        with _exclusive_jsonl_writer(root / "ap_records.jsonl") as ap_writer:
            for node in ap_node_plan():
                record = solve_ap_node(node)
                _append_jsonl(ap_writer, record)
                ap_records.append(record)
        current_stage = "route_c"
        external_raw = root / "external_raw.json"
        external_records = run_external_records(external_raw)
        with _exclusive_jsonl_writer(root / "external_records.jsonl") as writer:
            for item in external_records:
                _append_jsonl(writer, item)
        current_stage = "validation"
        evaluation = evaluate_all_thresholds(
            mode_records, ladder_records, ap_records, external_records
        )
        if not evaluation["all_pass"]:
            _exclusive_publish(
                root / "failed_evaluation.json", canonical_bytes(evaluation)
            )
            raise V31ContractError("official V3.1 threshold/certificate failure")
        source_end = build_source_ledger(start_gate)
        if source_end != source_start:
            raise V31ContractError("source identity drift during official execution")
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
                    "schema": "schwo.phase6.v3_1.report.v2",
                    "terminal": True,
                    "candidate_success": True,
                    "elapsed_seconds": time.perf_counter() - started,
                    "counts": EXPECTED_COUNTS,
                    "global_status": None,
                    "global_green_permitted": False,
                    "independent_review_state": "NOT_ASSESSED",
                }
            ),
        )
        os.close(lock_fd)
        lock_fd = -1
        lock.unlink()
        _seal_tree(root)
        manifest = build_manifest(root)
        os.chmod(root, 0o755)
        _exclusive_publish(root / "manifest.json", canonical_bytes(manifest))
        os.chmod(root, 0o555)
        validate_official_candidate(root)
        with tempfile.TemporaryDirectory(prefix="schwo_v31_r3_reload_") as directory:
            copied = Path(directory) / root.name
            shutil.copytree(root, copied, copy_function=shutil.copy2)
            validate_official_candidate(copied, validate_live_sources=False)
        return {
            "root": str(root),
            "manifest": _file_identity(root / "manifest.json"),
            "evaluation": evaluation,
        }
    except BaseException as exc:
        if lock_fd >= 0:
            os.close(lock_fd)
        if lock.exists() and not lock.is_symlink():
            lock.unlink()
        _terminalize_failure_best_effort(root, current_stage, exc)
        raise


def evaluate_all_thresholds(
    mode_records: Sequence[Mapping[str, Any]],
    ladder_records: Sequence[Mapping[str, Any]],
    ap_records: Sequence[Mapping[str, Any]],
    external_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if (
        len(mode_records),
        len(ladder_records),
        len(ap_records),
        len(external_records),
    ) != (496, 9920, 458, 23):
        raise V31ContractError("official record cardinality mismatch")
    thresholds = {item["field_id"]: item for item in _v31_thresholds()}
    extrema: dict[str, float] = {key: 0.0 for key in thresholds}
    for mode in mode_records:
        metrics = mode["metrics"]
        extrema["V3T-RIN-S-001"] = max(extrema["V3T-RIN-S-001"], metrics["rin_s_max"])
        extrema["V3T-RIN-LOGGAMMA-001"] = max(
            extrema["V3T-RIN-LOGGAMMA-001"], metrics["rin_log_gamma_max"]
        )
        extrema["V3T-ROUT-JOST-S-001"] = max(
            extrema["V3T-ROUT-JOST-S-001"], metrics["outer_jost_s_max"]
        )
        extrema["V3T-ROUT-JOST-LOGGAMMA-001"] = max(
            extrema["V3T-ROUT-JOST-LOGGAMMA-001"], metrics["outer_jost_log_gamma_max"]
        )
        extrema["V3T-TOLERANCE-S-001"] = max(
            extrema["V3T-TOLERANCE-S-001"], metrics["tolerance_s_max"]
        )
        extrema["V3T-TOLERANCE-LOGGAMMA-001"] = max(
            extrema["V3T-TOLERANCE-LOGGAMMA-001"], metrics["tolerance_log_gamma_max"]
        )
        result = mode["baseline"]
        extrema["V3T-FLUX-BALANCE-001"] = max(
            extrema["V3T-FLUX-BALANCE-001"], abs(result["flux_balance_residual"])
        )
        gf, gs = float(result["Gamma_flux"]), float(result["Gamma_S"])
        extrema["V3T-GAMMA-PHYSICAL-001"] = max(
            extrema["V3T-GAMMA-PHYSICAL-001"], max(-gf, gf - 1, -gs, gs - 1, 0.0)
        )
        if gf >= 1e-8:
            extrema["V3T-GAMMA-ROUTES-001"] = max(
                extrema["V3T-GAMMA-ROUTES-001"], abs(gf - gs)
            )
        elif gf > 0:
            difference = (
                math.inf
                if gs <= 0
                else abs(float(result["log_Gamma_flux"]) - math.log(gs))
            )
            extrema["V3T-GAMMA-ROUTES-LOG-001"] = max(
                extrema["V3T-GAMMA-ROUTES-LOG-001"], difference
            )
    by_ap: dict[tuple[str, int, str], list[Mapping[str, Any]]] = defaultdict(list)
    for item in ap_records:
        key = item["node"]["key"]
        by_ap[(key["kM"], int(key["ell"]), key["parity"])].append(item)
    mode_lookup = {
        (item["mode"]["kM"], int(item["mode"]["ell"]), item["mode"]["parity"]): item
        for item in mode_records
    }
    for key, records in by_ap.items():
        precision = sorted(
            (item for item in records if item["node"]["membership"] == "precision"),
            key=lambda item: item["node"]["dps"],
        )
        if len(precision) != 3:
            raise V31ContractError("AP precision ladder incomplete")
        for left, right in zip(precision, precision[1:]):
            extrema["V3T-PRECISION-S-001"] = max(
                extrema["V3T-PRECISION-S-001"],
                _mp_symmetric_relative(
                    _mp_complex(left["result"]["S"]), _mp_complex(right["result"]["S"])
                ),
            )
            extrema["V3T-PRECISION-LOGGAMMA-001"] = max(
                extrema["V3T-PRECISION-LOGGAMMA-001"],
                float(abs(_mp_log_gamma(left) - _mp_log_gamma(right))),
            )
        ap_final = precision[-1]
        route_a = mode_lookup[key]["baseline"]
        extrema["V3T-S-COMPLEX-001"] = max(
            extrema["V3T-S-COMPLEX-001"],
            _mp_symmetric_relative(
                _mp_complex(route_a["S"]), _mp_complex(ap_final["result"]["S"])
            ),
        )
        extrema["V3T-LOGGAMMA-001"] = max(
            extrema["V3T-LOGGAMMA-001"],
            float(
                abs(mp.mpf(str(route_a["log_Gamma_flux"])) - _mp_log_gamma(ap_final))
            ),
        )
    for frequency in FREQUENCIES:
        for ell in sorted(
            {
                int(item["mode"]["ell"])
                for item in mode_records
                if item["mode"]["kM"] == frequency
            }
        ):
            odd = mode_lookup[(frequency, ell, "odd")]["baseline"]
            even = mode_lookup[(frequency, ell, "even")]["baseline"]
            extrema["V3T-PARITY-PROB-001"] = max(
                extrema["V3T-PARITY-PROB-001"],
                abs(odd["Gamma_flux"] - even["Gamma_flux"]),
                abs(abs(_complex(odd["S"])) ** 2 - abs(_complex(even["S"])) ** 2),
            )
            if min(abs(_complex(odd["S"])), abs(_complex(even["S"]))) >= 1e-10:
                sigma = (ell - 1) * ell * (ell + 1) * (ell + 2)
                expected = (sigma + 12j * float(frequency)) / (
                    sigma - 12j * float(frequency)
                )
                observed = _complex(even["S"]) / _complex(odd["S"])
                extrema["V3T-PARITY-PHASE-001"] = max(
                    extrema["V3T-PARITY-PHASE-001"],
                    abs(
                        _principal_phase(
                            math.atan2(observed.imag, observed.real)
                            - math.atan2(expected.imag, expected.real)
                        )
                    ),
                )
    external_lookup = {
        (item["key"]["kM"], int(item["key"]["ell"]), "odd"): item
        for item in external_records
    }
    for key, external in external_lookup.items():
        extrema["V3T-S-COMPLEX-001"] = max(
            extrema["V3T-S-COMPLEX-001"],
            _mp_symmetric_relative(
                _mp_complex(mode_lookup[key]["baseline"]["S"]),
                _mp_complex(external["S"]),
            ),
        )
    outcomes = [
        {
            "field_id": field_id,
            "observed": observed,
            "limit": float(thresholds[field_id]["value"]),
            "status": "PASS"
            if observed <= float(thresholds[field_id]["value"])
            else "FAIL",
        }
        for field_id, observed in extrema.items()
    ]
    all_pass = all(item["status"] == "PASS" for item in outcomes)
    certificates = [
        {"certificate_id": item, "status": "PASS" if all_pass else "FAIL"}
        for item in CERTIFICATE_IDS
    ]
    return {
        "all_pass": all_pass,
        "thresholds": outcomes,
        "summary": {
            "schema": "schwo.phase6.v3_1.summary.v2",
            "overall_state": "PASS" if all_pass else "FAILED_SCIENTIFIC",
            "counts": EXPECTED_COUNTS,
            "thresholds": outcomes,
            "certificates": certificates,
            "global_status": None,
            "global_green_permitted": False,
            "independent_review_state": "NOT_ASSESSED",
        },
        "uncertainty_budget": {
            "schema": "schwo.phase6.v3_1.uncertainty.v2",
            "threshold_extrema": extrema,
            "common_absolute_phase": "PARTIAL",
            "budgets_combined": False,
        },
    }


def _mode_threshold_blockers(mode: Mapping[str, Any]) -> list[dict[str, Any]]:
    result = mode["baseline"]
    observations: list[tuple[str, float]] = [
        ("V3T-FLUX-BALANCE-001", abs(float(result["flux_balance_residual"]))),
        (
            "V3T-GAMMA-PHYSICAL-001",
            max(
                -float(result["Gamma_flux"]),
                float(result["Gamma_flux"]) - 1.0,
                -float(result["Gamma_S"]),
                float(result["Gamma_S"]) - 1.0,
                0.0,
            ),
        ),
    ]
    gamma_flux = float(result["Gamma_flux"])
    gamma_s = float(result["Gamma_S"])
    if gamma_flux >= 1e-8:
        observations.append(("V3T-GAMMA-ROUTES-001", abs(gamma_flux - gamma_s)))
    elif gamma_flux > 0:
        observations.append(
            (
                "V3T-GAMMA-ROUTES-LOG-001",
                math.inf
                if gamma_s <= 0
                else abs(float(result["log_Gamma_flux"]) - math.log(gamma_s)),
            )
        )
    return [
        {"field_id": field_id, "observed": observed, "status": "FAIL"}
        for field_id, observed in observations
        if threshold_boundary_status(field_id, observed) != "PASS"
    ]


def build_source_ledger(start_gate: Mapping[str, Any]) -> dict[str, Any]:
    package = start_gate["package"]
    paths = [
        ROOT / "configs/phase6_v3_0_domain.json",
        ROOT / "configs/phase6_v3_0_thresholds.json",
        ROOT / "configs/phase6_v3_0_external_anchor_matrix.json",
        ROOT / "docs/phase6_v3_0_validation_contract.md",
        ROOT / "docs/phase6_v3_0_formula_map.md",
        ROOT / "docs/phase6_v3_0_phase_taxonomy.md",
        ROOT / "docs/phase6_v3_0_literature_matrix.md",
        ROOT / "references/notes/phase6_v3_absorption_scattering_conventions.md",
        ROOT
        / "runs/phase6/radial_validation/v1_final_radial_baseline_v2_20260810_py314/manifest.json",
        ROOT
        / "runs/phase6/radial_validation/v1_production_state_evidence_v2_20260810_py314/manifest.json",
        ROOT
        / "runs/phase6/radial_validation/v1_radial_selected_acceptance_v1_20260810_py314/manifest.json",
        ROOT
        / "runs/phase6/asymptotic_waveform/v2_selected_release_v2_20260811T083414_py314/manifest.json",
        ROOT
        / "runs/phase6/radial_validation/v1_final_radial_baseline_v2_20260810_py314/plan.json",
        Path(__file__).resolve(),
        ROOT / "src/schwgw/validation/phase6_v3_continued_jost.py",
        ROOT / "src/schwgw/validation/phase6_mpmath_radial.py",
        ROOT / "src/schwgw/validation/phase6_v3_mode_greybody_ap.py",
        ROOT / "scripts/phase6_v3_1_mode_greybody.py",
        EXTERNAL_WLS,
        WOLFRAM_KERNEL,
    ]
    paths.extend(ROOT / item["path"] for item in package["protected_radial_files"])
    ledger = dict(start_gate["identities"])
    ledger.update(
        {str(path): _file_identity(path.resolve(strict=True)) for path in paths}
    )
    ledger["bhpt_source"] = external_source_identity()
    return ledger


def validate_official_candidate(
    root: Path, *, validate_live_sources: bool = True
) -> None:
    root = root.resolve(strict=True)
    if stat.S_IMODE(root.stat().st_mode) != 0o555:
        raise V31ContractError("official root mode mismatch")
    manifest = json.loads((root / "manifest.json").read_text())
    if manifest["artifact_rev"] != 3 or manifest["scientific_stage"] != "V3.1":
        raise V31ContractError("official manifest stage/revision mismatch")
    actual_files = {
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() and path.name != "manifest.json"
    }
    if actual_files != set(manifest["artifacts"]):
        raise V31ContractError("official artifact set mismatch")
    for relative, expected in manifest["artifacts"].items():
        if _file_identity(root / relative) != expected:
            raise V31ContractError(f"official artifact drift: {relative}")
    if json.loads((root / "inventory.json").read_text()) != build_inventory_payload():
        raise V31ContractError("official inventory mismatch")
    mode_records = load_jsonl(root / "records.jsonl")
    ladder_records = load_jsonl(root / "ladder_records.jsonl")
    ap_records = load_jsonl(root / "ap_records.jsonl")
    external_records = load_jsonl(root / "external_records.jsonl")
    expected_modes = build_mode_inventory()
    if [item["mode"] for item in mode_records] != [
        key.payload() for key in expected_modes
    ]:
        raise V31ContractError("official Route-A mode order mismatch")
    for ordinal, (mode_record, key) in enumerate(zip(mode_records, expected_modes)):
        if (
            mode_record.get("node_count") != 20
            or mode_record.get("protected_call_count") != 20
        ):
            raise V31ContractError("official Route-A mode count mismatch")
        group = ladder_records[20 * ordinal : 20 * (ordinal + 1)]
        if [item["mode"] for item in group] != [key.payload()] * 20:
            raise V31ContractError("official Route-A ladder grouping mismatch")
        if [item["node"] for item in group] != route_a_node_graph(key):
            raise V31ContractError("official Route-A ladder graph mismatch")
        for item in group:
            result = item["result"]
            geometry = continued_jost_geometry(
                ell=key.ell,
                k=float(key.kM),
                r_match=float(item["node"]["r_out"]),
            )
            if (
                result["diagnostics"].get("protected_route_a_call_count") != 1
                or result["requested_match_radius"] != geometry.requested_match_radius
                or result["jost_initialization_radius"]
                != geometry.jost_initialization_radius
                or result["auxiliary_exponent"] != geometry.auxiliary_exponent
            ):
                raise V31ContractError("official continued-Jost identity mismatch")
    if [item["node"] for item in ap_records] != ap_node_plan():
        raise V31ContractError("official Route-B node order mismatch")
    expected_external = build_anchor_inventory(expected_modes)["external"]
    if [item["key"] for item in external_records] != expected_external:
        raise V31ContractError("official Route-C order mismatch")
    source_map = json.loads((root / "source_map.json").read_text())
    source_start = json.loads((root / "source_start.json").read_text())
    if (
        source_map.get("start") != source_map.get("end")
        or source_map["start"] != source_start
    ):
        raise V31ContractError("official source start/end mismatch")
    counts = {
        "route_a_modes": len(mode_records),
        "route_a_nodes": len(ladder_records),
        "route_b_nodes": len(ap_records),
        "route_c_records": len(external_records),
    }
    counts["route_b_keys"] = len(
        {
            (
                item["node"]["key"]["kM"],
                item["node"]["key"]["ell"],
                item["node"]["key"]["parity"],
            )
            for item in ap_records
        }
    )
    summary = json.loads((root / "summary.json").read_text())
    counts["thresholds"] = len(summary["thresholds"])
    counts["certificates"] = len(summary["certificates"])
    if [item["field_id"] for item in summary["thresholds"]] != [
        item["field_id"] for item in _v31_thresholds()
    ] or [item["certificate_id"] for item in summary["certificates"]] != list(
        CERTIFICATE_IDS
    ):
        raise V31ContractError("official threshold/certificate order mismatch")
    if counts != EXPECTED_COUNTS or not all(
        item["status"] == "PASS" for item in summary["certificates"]
    ):
        raise V31ContractError("official exact count/certificate mismatch")
    if validate_live_sources:
        verify_cycle2_start_gate()


def build_manifest(root: Path) -> dict[str, Any]:
    artifacts: dict[str, Any] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            artifacts[str(path.relative_to(root))] = _file_identity(path)
    return {
        "schema": "schwo.phase6.v3_1.manifest.v2",
        "scientific_stage": "V3.1",
        "artifact_rev": 3,
        "timezone": "UTC",
        "terminal": True,
        "overall_state": "PASS",
        "global_status": None,
        "global_green_permitted": False,
        "independent_review_state": "NOT_ASSESSED",
        "artifacts": artifacts,
    }


def _run_contract(root: Path, source_ledger: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": "schwo.phase6.v3_1.run_contract.v2",
        "created_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "official_root": str(root),
        "artifact_rev": 3,
        "scientific_stage": "V3.1",
        "counts": EXPECTED_COUNTS,
        "python": sys.version,
        "executable": str(Path(sys.executable).resolve()),
        "argv": sys.argv,
        "cwd": str(Path.cwd().resolve()),
        "source_start_sha256": hashlib.sha256(
            canonical_bytes(source_ledger)
        ).hexdigest(),
        "resume_policy": "exact contiguous checkpoint after system interruption only",
    }


def _v31_thresholds() -> list[dict[str, Any]]:
    thresholds = [
        item
        for item in json.loads(THRESHOLD_PATH.read_text())["thresholds"]
        if "V3.1" in item["blocking_stages"]
    ]
    if len(thresholds) != 16:
        raise V31ContractError("frozen V3.1 threshold count mismatch")
    return thresholds


def _node(
    r_in: float,
    multiplier: int,
    order: int,
    rtol: float,
    atol: float,
    membership: str,
    base: float,
) -> dict[str, Any]:
    return {
        "r_in_eps": r_in,
        "r_out_multiplier": multiplier,
        "r_out": base * multiplier,
        "jost_order": order,
        "rtol": rtol,
        "atol": atol,
        "memberships": [membership],
    }


def _node_tuple(node: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        node["r_in_eps"],
        node["r_out_multiplier"],
        node["jost_order"],
        node["rtol"],
        node["atol"],
    )


def _route_a_baseline(records: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    selected = [
        item
        for item in records
        if _node_tuple(item["node"]) == (1e-10, 1, 160, 1e-10, 1e-12)
    ]
    if len(selected) != 1:
        raise V31ContractError("Route-A baseline is not unique")
    return selected[0]


def _ap_node(
    key_ordinal: int,
    item: Mapping[str, Any],
    dps: int,
    r_in: float,
    multiplier: int,
    order: int,
    membership: str,
) -> dict[str, Any]:
    return {
        "key_ordinal": key_ordinal,
        "key": dict(item),
        "dps": dps,
        "r_in_eps": r_in,
        "r_out_multiplier": multiplier,
        "jost_order": order,
        "membership": membership,
    }


def _complex(value: Mapping[str, Any]) -> complex:
    return complex(float(value["real"]), float(value["imag"]))


def _mp_complex(value: Mapping[str, Any]) -> mp.mpc:
    return mp.mpc(mp.mpf(str(value["real"])), mp.mpf(str(value["imag"])))


def _mp_log_gamma(record: Mapping[str, Any]) -> mp.mpf:
    return mp.log(
        mp.mpf(str(record["result"]["signed_flux"]["horizon_transmission_fraction"]))
    )


def _mp_symmetric_relative(left: mp.mpc, right: mp.mpc) -> float:
    return float(2 * abs(left - right) / max(abs(left) + abs(right), mp.mpf("1e-1000")))


def _sre(left: Mapping[str, Any], right: Mapping[str, Any]) -> float:
    a, b = _complex(left), _complex(right)
    return 2.0 * abs(a - b) / max(abs(a) + abs(b), 1e-300)


def _max_s_pairs(pairs: Iterable[tuple[Mapping[str, Any], Mapping[str, Any]]]) -> float:
    return max(
        (_sre(left["result"]["S"], right["result"]["S"]) for left, right in pairs),
        default=0.0,
    )


def _max_log_pairs(
    pairs: Iterable[tuple[Mapping[str, Any], Mapping[str, Any]]],
) -> float:
    return max(
        (
            abs(
                float(left["result"]["log_Gamma_flux"])
                - float(right["result"]["log_Gamma_flux"])
            )
            for left, right in pairs
        ),
        default=0.0,
    )


def _principal_phase(value: float) -> float:
    return math.atan2(math.sin(value), math.cos(value))


def _file_identity(path: Path) -> dict[str, Any]:
    resolved = path.resolve(strict=True)
    info = resolved.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or path.is_symlink():
        raise V31ContractError(f"unsafe file identity: {path}")
    return {
        "sha256": sha256(resolved),
        "size": info.st_size,
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
    }


def _validate_external_snapshot_tree(
    snapshot_root: Path, expected_by_path: Mapping[str, Mapping[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Rebuild exact file and directory closure for a snapshot or temp copy."""

    if snapshot_root.is_symlink():
        raise V31ContractError("external snapshot root is a symlink")
    root = snapshot_root.resolve(strict=True)
    nodes = list(root.rglob("*"))
    if any(path.is_symlink() for path in nodes):
        raise V31ContractError("external snapshot contains a symlink")
    if any(not path.is_file() and not path.is_dir() for path in nodes):
        raise V31ContractError("external snapshot contains a special file")
    actual_paths = sorted(
        path.relative_to(root).as_posix() for path in nodes if path.is_file()
    )
    if actual_paths != sorted(expected_by_path):
        raise V31ContractError("external snapshot missing or extra source file")
    files: list[dict[str, Any]] = []
    for relative in actual_paths:
        path = root / relative
        identity = _file_identity(path)
        expected = expected_by_path[relative]
        if (
            identity["sha256"] != expected["sha256"]
            or identity["size"] != expected["size"]
            or identity["mode"] != 0o444
            or identity["nlink"] != 1
        ):
            raise V31ContractError(f"external source identity drift: {relative}")
        files.append({"path": relative, **identity})
    actual_directories = sorted(
        ["."] + [path.relative_to(root).as_posix() for path in nodes if path.is_dir()]
    )
    if actual_directories != sorted(EXTERNAL_REQUIRED_DIRECTORY_PATHS):
        raise V31ContractError("external snapshot directory inventory drift")
    directories: list[dict[str, Any]] = []
    for relative in EXTERNAL_REQUIRED_DIRECTORY_PATHS:
        path = root if relative == "." else root / relative
        info = path.stat()
        if not stat.S_ISDIR(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o555:
            raise V31ContractError(f"external snapshot directory drift: {relative}")
        directories.append(
            {
                "path": relative,
                "mode": stat.S_IMODE(info.st_mode),
                "nlink": info.st_nlink,
                "device": info.st_dev,
                "inode": info.st_ino,
            }
        )
    return files, directories


def _bhpt_source_tree_identity() -> dict[str, Any]:
    identity = external_source_identity()
    return {
        "root": identity["snapshot_root"],
        "file_count": len(identity["source_files"]),
        "records": identity["source_files"],
        "canonical_sha256": hashlib.sha256(
            canonical_bytes(identity["source_files"])
        ).hexdigest(),
    }


def _validate_external_runtime_observed(
    observed: Mapping[str, Any],
    expected_by_path: Mapping[str, Mapping[str, Any]],
    required_records: Sequence[Mapping[str, Any]],
) -> None:
    if set(observed) != {"wolfram_version", "system_id", "loaded_source_records"}:
        raise V31ContractError("external runtime-observed schema mismatch")
    if not isinstance(observed["wolfram_version"], str) or not observed[
        "wolfram_version"
    ].startswith("14.3"):
        raise V31ContractError("external Wolfram version drift")
    if not isinstance(observed["system_id"], str) or not observed["system_id"]:
        raise V31ContractError("external Wolfram system identity missing")
    loaded = observed["loaded_source_records"]
    if (
        not isinstance(loaded, list)
        or len(loaded) != len(required_records)
        or any(not isinstance(value, Mapping) for value in loaded)
    ):
        raise V31ContractError("external loaded-source inventory missing")
    if any(set(value) != {"path", "sha256", "size"} for value in loaded):
        raise V31ContractError("external loaded-source record schema mismatch")
    paths = [str(value["path"]) for value in loaded]
    if len(paths) != len(set(paths)):
        raise V31ContractError("external loaded-source inventory duplicate")
    root = EXTERNAL_SNAPSHOT_ROOT.resolve(strict=True)
    for value in loaded:
        path = Path(str(value["path"]))
        if path.is_symlink():
            raise V31ContractError("external loaded-source alias forbidden")
        resolved = path.resolve(strict=True)
        if resolved.parent != root and root not in resolved.parents:
            raise V31ContractError("external loaded-source path escaped snapshot")
        relative = resolved.relative_to(root).as_posix()
        if relative not in expected_by_path:
            raise V31ContractError("external loaded-source path is not authenticated")
        identity = _file_identity(resolved)
        expected = expected_by_path[relative]
        if (
            str(resolved) != str(path)
            or value["sha256"] != identity["sha256"]
            or value["size"] != identity["size"]
            or identity["sha256"] != expected["sha256"]
            or identity["size"] != expected["size"]
            or identity["mode"] != 0o444
            or identity["nlink"] != 1
        ):
            raise V31ContractError("external loaded-source identity drift")
    if loaded != list(required_records):
        raise V31ContractError("external loaded-source inventory mismatch")


def _load_strict_json(path: Path) -> Any:
    def object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise V31ContractError("duplicate key in external child JSON")
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise V31ContractError(f"non-finite JSON constant forbidden: {value}")

    try:
        return json.loads(
            path.read_text(),
            object_pairs_hook=object_pairs,
            parse_constant=reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise V31ContractError("torn or noncanonical external child JSON") from exc


def _exclusive_stream_fd(path: Path) -> int:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return os.open(path, flags, 0o600)


def _kill_for_timeout(
    process: subprocess.Popen[bytes], timed_out: threading.Event
) -> None:
    if process.poll() is None:
        timed_out.set()
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def _process_group_empty(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    return False


def _fsync_existing(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


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

    def __exit__(self, *_: Any) -> None:
        if self.fd >= 0:
            os.fsync(self.fd)
            os.close(self.fd)
            os.chmod(self.path, 0o444)
            _fsync_directory(self.path.parent)
            self.fd = -1


def _exclusive_jsonl_writer(path: Path) -> _JsonlWriter:
    return _JsonlWriter(path)


def _append_jsonl(writer: _JsonlWriter, payload: Mapping[str, Any]) -> None:
    os.write(writer.fd, compact_jsonl_record(payload))
    os.fsync(writer.fd)


def _seal_tree(root: Path) -> None:
    for path in root.rglob("*"):
        os.chmod(path, 0o555 if path.is_dir() else 0o444)


def _terminalize_failure_best_effort(
    root: Path, stage: str, exc: BaseException
) -> None:
    try:
        path = root / "failure.json"
        if not path.exists():
            _exclusive_publish(
                path,
                canonical_bytes(
                    {
                        "schema": "schwo.phase6.v3_1.failure.v2",
                        "stage": stage,
                        "exception_type": type(exc).__name__,
                        "exception_message": str(exc),
                        "scientific_pass": False,
                    }
                ),
            )
        manifest_path = root / "failure_manifest.json"
        if not manifest_path.exists():
            artifacts = {
                str(item.relative_to(root)): _file_identity(item)
                for item in sorted(root.rglob("*"))
                if item.is_file() and item != manifest_path
            }
            _exclusive_publish(
                manifest_path,
                canonical_bytes(
                    {
                        "schema": "schwo.phase6.v3_1.failure_manifest.v2",
                        "terminal": True,
                        "scientific_pass": False,
                        "stage": stage,
                        "artifacts": artifacts,
                    }
                ),
            )
        _seal_tree(root)
        os.chmod(root, 0o555)
    except BaseException:
        pass


__all__ = [
    "EXPECTED_COUNTS",
    "ap_node_plan",
    "compact_jsonl_record",
    "evaluate_all_thresholds",
    "load_jsonl",
    "publish_synthetic_root",
    "route_a_mode_metrics",
    "route_a_node_graph",
    "run_external_records",
    "run_official_cycle2",
    "run_preexecution_sentinels",
    "solve_ap_node",
    "solve_route_a_mode",
    "synthetic_payload",
    "threshold_boundary_status",
    "validate_official_candidate",
    "validate_synthetic_root",
    "verify_cycle2_start_gate",
]
