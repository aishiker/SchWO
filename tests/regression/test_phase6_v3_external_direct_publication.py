from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
from types import SimpleNamespace

import mpmath as mp
import pytest

import schwgw.validation.phase6_v3_external_direct as direct
import schwgw.validation.phase6_v3_mode_greybody_external_direct_replacement as replacement
from schwgw.validation.phase6_v3_external_direct import ExternalDirectContractError


REPAIR_REVIEW_RELATIVE_PATH = Path(
    "docs/handoffs/archive/"
    "T7_2026-08-13_v3_1_x_sentinel_repair_cycle2_source_ledger_"
    "implementation_delta_review.md"
)
MICRO_REVIEW_RELATIVE_PATH = Path(
    "docs/handoffs/archive/"
    "T7_2026-08-13_v3_1_x_source_load_micro_sentinel_terminal_review.md"
)
SENTINEL_ATTEMPT_0003 = (
    "T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0003.json"
)


def _scalar(value: mp.mpf, node: dict[str, object]) -> dict[str, object]:
    if value == 0:
        return {
            "decimal": "0",
            "exact_zero": True,
            "source_precision_digits": None,
            "source_accuracy_digits": None,
            "serialized_significant_digits": 0,
        }
    text = mp.nstr(value, int(node["working_precision"]))
    digits = direct._decimal_significant_digits(text, "fake")
    assert digits >= int(node["precision_goal"])
    return {
        "decimal": text,
        "exact_zero": False,
        "source_precision_digits": int(node["working_precision"]),
        "source_accuracy_digits": int(node["accuracy_goal"]),
        "serialized_significant_digits": digits,
    }


def _complex(value: mp.mpc, node: dict[str, object]) -> dict[str, object]:
    return {"real": _scalar(value.real, node), "imag": _scalar(value.imag, node)}


def _fake_child(
    request_path: Path, output_path: Path, expected: dict[str, object]
) -> dict[str, object]:
    mp.mp.dps = max(mp.mp.dps, 160)
    request = json.loads(request_path.read_text())
    key = expected["key"]
    node = expected["node"]
    assert isinstance(key, dict) and isinstance(node, dict)
    k = mp.mpf(key["kM"])
    perturbation = mp.power(10, -(int(node["working_precision"]) - 9))
    a_in = mp.mpf(2) + perturbation
    a_out = mp.sqrt(3)
    h = a_in + a_out
    hdot = mp.mpc(0, k * (a_out - a_in))
    numerator, denominator = direct.exact_frequency_fraction(key["kM"])
    raw = {
        "schema": "schwo.phase6.v3_1_x.external_direct_raw_node.v1",
        "call_ordinal": expected["call_ordinal"],
        "key_ordinal": expected["key_ordinal"],
        "key": key,
        "node_ordinal": expected["node_ordinal"],
        "node": node,
        "method": "NumericalIntegration",
        "potential": "ReggeWheeler",
        "boundary_conditions": ["In", "Up"],
        "frequency": {
            "label": key["kM"],
            "exact_numerator": numerator,
            "exact_denominator": denominator,
            "input_precision_digits": node["working_precision"] + 20,
        },
        "external_api_call_count": 1,
        "external_boundary_solution_count": 2,
        "mst_call_count": 0,
        "internal_solver_call_count": 0,
        "overlay": request["overlay"],
        "overlaps": [
            {
                "fraction": label,
                "radius_M": _scalar(radius * (1 + perturbation), node),
                "H": _complex(mp.mpc(h), node),
                "Hdot": _complex(hdot, node),
                "U": _complex(mp.mpc(1 + perturbation), node),
                "Udot": _complex(mp.mpc(0, k + perturbation), node),
            }
            for label, radius in zip(
                direct.OVERLAP_LABELS,
                direct.overlap_radii(key, node),
                strict=True,
            )
        ],
        "loaded_contexts_start": list(direct.LOADED_SOURCE_CONTEXTS),
        "loaded_contexts_end": list(direct.LOADED_SOURCE_CONTEXTS),
        "loaded_source_start": request["loaded_source_records"],
        "loaded_source_end": request["loaded_source_records"],
        "runtime": {
            "elapsed_seconds": "1.0",
            "fake_child": True,
            "observed_environment": dict(replacement.OBSERVED_CLEAN_LAUNCH_ENVIRONMENT),
        },
    }
    command = [
        str(replacement.WOLFRAM_KERNEL),
        "-script",
        str(replacement.WLS_PATH),
        str(request_path),
        str(output_path.with_suffix(".child.raw.json")),
    ]
    prelaunch_path = output_path.with_suffix(".prelaunch.json")
    prelaunch = replacement._exclusive_publish(
        prelaunch_path,
        direct.canonical_bytes(
            {
                "schema": "schwo.phase6.v3_1_x.child_prelaunch.v1",
                "call_ordinal": expected["call_ordinal"],
                "argv": command,
                "cwd": str(replacement.ROOT),
                "request": replacement._file_identity(request_path),
                "requested_environment": dict(
                    replacement.REQUESTED_EXECUTION_ENVIRONMENT
                ),
                "kernel": replacement._file_identity(replacement.WOLFRAM_KERNEL),
                "wls": replacement._file_identity(replacement.WLS_PATH),
                "raw_final_path": str(output_path),
                "raw_staging_path": str(output_path.with_suffix(".child.raw.json")),
                "child_execution_kind": "REAL_WOLFRAM_KERNEL",
                "started_utc": "2026-08-13T00:00:00.000000Z",
                "started_ns": 1,
            }
        ),
    )
    running = replacement._exclusive_publish(
        output_path.with_suffix(".running.json"),
        direct.canonical_bytes(
            {
                "schema": "schwo.phase6.v3_1_x.child_running.v1",
                "call_ordinal": expected["call_ordinal"],
                "pid": 1,
                "sid": 1,
                "pgid": 1,
                "prelaunch": prelaunch,
                "requested_environment": dict(
                    replacement.REQUESTED_EXECUTION_ENVIRONMENT
                ),
                "started_utc": "2026-08-13T00:00:00.000000Z",
                "started_ns": 1,
            }
        ),
    )
    stdout = replacement._exclusive_publish(output_path.with_suffix(".stdout.raw"), b"")
    stderr = replacement._exclusive_publish(output_path.with_suffix(".stderr.raw"), b"")
    receipt = {
        "schema": "schwo.phase6.v3_1_x.child_receipt.v2",
        "call_ordinal": expected["call_ordinal"],
        "argv": command,
        "cwd": str(replacement.ROOT),
        "requested_environment": dict(replacement.REQUESTED_EXECUTION_ENVIRONMENT),
        "observed_environment": dict(replacement.OBSERVED_CLEAN_LAUNCH_ENVIRONMENT),
        "started_utc": "2026-08-13T00:00:00.000000Z",
        "finished_utc": "2026-08-13T00:00:01.000000Z",
        "started_ns": 1,
        "finished_ns": 2,
        "pid": 1,
        "sid": 1,
        "pgid": 1,
        "returncode": 0,
        "signal": None,
        "timed_out": False,
        "popen_wait_called": True,
        "child_reaped": True,
        "process_group_empty": True,
        "cleanup_actions": ["wait"],
        "wait_error": None,
        "stdout": {"state": "CLOSED", "identity": stdout, "error": None},
        "stderr": {"state": "CLOSED", "identity": stderr, "error": None},
        "exception_type": None,
        "exception_message": None,
        "child_execution_kind": "REAL_WOLFRAM_KERNEL",
        "prelaunch": prelaunch,
        "running": running,
    }
    receipt_identity = replacement._exclusive_publish(
        output_path.with_suffix(".receipt.json"), direct.canonical_bytes(receipt)
    )
    replacement._exclusive_publish(
        output_path.with_suffix(".terminal.json"),
        direct.canonical_bytes(
            {
                **receipt,
                "schema": "schwo.phase6.v3_1_x.child_terminal.v2",
                "receipt": receipt_identity,
            }
        ),
    )
    replacement._exclusive_publish(output_path, direct.canonical_bytes(raw))
    return raw


def _fake_gate() -> dict[str, object]:
    return {
        "package_identity": {"sha256": replacement.PACKAGE_SHA256},
        "identities": {"fixed": True},
        "implementation_hashes": replacement.implementation_hashes(),
        "static_contract": direct.static_contract(),
    }


def _patch_control(
    monkeypatch: pytest.MonkeyPatch,
    root: Path,
    stage: str,
) -> None:
    gate = _fake_gate()
    authority = {
        "payload": {
            "stage": stage,
            "one_use_id": "f" * 64,
            "implementation_hashes": gate["implementation_hashes"],
            "invocation": {"schema": "fake.invocation"},
            "requested_environment": {
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONPATH": "runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src",
            },
            "observed_environment": dict(replacement.OBSERVED_CLEAN_LAUNCH_ENVIRONMENT),
        },
        "identity": {"sha256": "a" * 64},
        "root": root,
        "implementation_review": {"sha256": "b" * 64},
    }
    monkeypatch.setattr(replacement, "verify_start_gate", lambda: gate)
    monkeypatch.setattr(
        replacement,
        "build_source_ledger",
        lambda _gate: {"schema": "fixed.source", "science": False},
    )
    monkeypatch.setattr(
        replacement, "validate_dispatch", lambda *_args, **_kwargs: authority
    )
    monkeypatch.setattr(
        replacement.os, "environ", dict(replacement.OBSERVED_CLEAN_LAUNCH_ENVIRONMENT)
    )


def _evaluation() -> dict[str, object]:
    thresholds = [
        {
            "field_id": f"V3T-{index:02d}",
            "observed": 0.0,
            "limit": 1.0,
            "status": "PASS",
        }
        for index in range(16)
    ]
    summary = {
        "schema": "fake.summary",
        "overall_state": "PASS",
        "counts": dict(replacement.EXPECTED_COUNTS),
        "thresholds": thresholds,
        "certificates": [
            {"certificate_id": item, "status": "PASS"}
            for item in direct.CERTIFICATE_IDS
        ],
        "global_status": None,
        "global_green_permitted": False,
    }
    return {
        "all_pass": True,
        "summary": summary,
        "thresholds": thresholds,
        "uncertainty_budget": {"schema": "fake.budget", "budgets_combined": False},
    }


def _fake_routes() -> dict[str, object]:
    return {
        "hp": SimpleNamespace(evaluate_all_thresholds=lambda *_args: _evaluation()),
        "modes": [{"mode": index} for index in range(496)],
        "ladders": [{"node": index} for index in range(9920)],
        "route_map": {"schema": "fake.route_map", "entries": []},
        "route_u": [{"node": index} for index in range(954)],
        "route_u_ladders": [{"mode": index} for index in range(318)],
        "ap": [{"node": index} for index in range(458)],
    }


def test_fake_full_sentinel_publication_reload_and_distinct_copy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "v3_1_x_external_direct_sentinel_v1_20260813T120000Z_py314"
    _patch_control(monkeypatch, root, "sentinel")
    result = replacement.run_sentinel(
        tmp_path / "fake_dispatch.json", "a" * 64, child_runner=_fake_child
    )
    assert result["resource_projection"]["runtime_gate_passed"] is True
    assert stat.S_IMODE(root.stat().st_mode) == 0o555
    replacement.validate_sentinel(root)
    assert len(direct.load_jsonl(root / "external_evidence/records.jsonl")) == 35
    copy_root = tmp_path / "copy"
    shutil.copytree(root, copy_root, copy_function=shutil.copy2)
    replacement.validate_sentinel(copy_root)


def test_fake_full_official_publication_reload_and_no_reuse(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "v3_1_x_external_direct_v1_20260813T130000Z_py314"
    _patch_control(monkeypatch, root, "official")
    result = replacement.run_official(
        tmp_path / "fake_dispatch.json",
        "a" * 64,
        child_runner=_fake_child,
        fresh_routes_runner=_fake_routes,
    )
    assert result["evaluation"]["all_pass"] is True
    replacement.validate_official(root, validate_live_sources=False)
    official = direct.load_canonical(root / "official_result.json")
    assert official["counts"] == replacement.EXPECTED_COUNTS
    assert official["predecessor_science_reused"] is False
    assert official["sentinel_science_reused"] is False
    assert len(direct.load_jsonl(root / "external_evidence/records.jsonl")) == 161


def test_fake_child_failure_terminalizes_and_never_retries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "v3_1_x_external_direct_sentinel_v1_20260813T140000Z_py314"
    _patch_control(monkeypatch, root, "sentinel")
    calls = 0

    def failing(
        request: Path, output: Path, expected: dict[str, object]
    ) -> dict[str, object]:
        nonlocal calls
        calls += 1
        if calls == 3:
            raise RuntimeError("fake child failure")
        return _fake_child(request, output, expected)

    with pytest.raises(RuntimeError, match="fake child failure"):
        replacement.run_sentinel(
            tmp_path / "fake_dispatch.json", "a" * 64, child_runner=failing
        )
    assert calls == 3
    assert stat.S_IMODE(root.stat().st_mode) == 0o555
    assert direct.load_canonical(root / "failure.json")["scientific_pass"] is False
    outcomes = direct.load_jsonl(root / "external_evidence/outcomes.jsonl")
    assert len(outcomes) == 35
    assert outcomes[2]["status"] == "ERROR"
    assert all(
        item["status"] == "NOT_STARTED_AFTER_PRIOR_FAILURE" for item in outcomes[3:]
    )
    replacement.validate_manifest(root, expected_state="FAIL")


def test_manifest_rejects_unknown_tampered_missing_and_hardlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "v3_1_x_external_direct_sentinel_v1_20260813T150000Z_py314"
    _patch_control(monkeypatch, root, "sentinel")
    replacement.run_sentinel(
        tmp_path / "fake_dispatch.json", "a" * 64, child_runner=_fake_child
    )
    os.chmod(root, 0o755)
    extra = root / "unknown.control"
    extra.write_text("x")
    os.chmod(extra, 0o444)
    os.chmod(root, 0o555)
    with pytest.raises(ExternalDirectContractError, match="manifest"):
        replacement.validate_sentinel(root)
    os.chmod(root, 0o755)
    extra.unlink()
    target = root / "sentinel_result.json"
    os.chmod(target, 0o644)
    target.write_text("{}\n")
    os.chmod(target, 0o444)
    os.chmod(root, 0o555)
    with pytest.raises(ExternalDirectContractError):
        replacement.validate_sentinel(root)


def _write_review(path: Path, *, sentinel: bool = False) -> str:
    if sentinel:
        text = (
            "ADVANCE_DECISION: ADVANCE\n"
            "CLAIM_STATUS: PASS\n"
            "GATE_LABEL: ACCEPT GREEN / V3.1-X SENTINEL SUFFICIENT FOR "
            "ONE-USE OFFICIAL DISPATCH\n"
        )
    else:
        text = "\n".join(
            [
                *replacement.IMPLEMENTATION_REVIEW_REQUIRED_TOKENS,
                *replacement.IMPLEMENTATION_REVIEW_REQUIRED_AUTHORITY_HASHES,
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    os.chmod(path, 0o444)
    return direct.sha256(path)


def _write_complete_repair_review(path: Path, gate: dict[str, object]) -> str:
    _write_review(path)
    os.chmod(path, 0o644)
    with path.open("a") as handle:
        handle.write("\n".join(gate["implementation_hashes"].values()) + "\n")
    os.chmod(path, 0o444)
    return direct.sha256(path)


def _write_micro_review(
    path: Path,
    gate: dict[str, object],
    micro_root: Path,
    micro_manifest_sha: str,
    *,
    extra_text: str = "",
) -> str:
    text = "\n".join(
        [
            *replacement.MICRO_REVIEW_REQUIRED_TOKENS,
            str(micro_root),
            micro_manifest_sha,
            replacement.REPAIR2_PACKAGE_SHA256,
            *gate["implementation_hashes"].values(),
            extra_text,
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    os.chmod(path, 0o444)
    return direct.sha256(path)


def _write_micro_root(root: Path, gate: dict[str, object]) -> str:
    root.mkdir()
    source = replacement.build_source_ledger(gate)
    (root / "source_start.json").write_bytes(direct.canonical_bytes(source))
    os.chmod(root / "source_start.json", 0o444)
    manifest = {
        "schema": "synthetic.micro.manifest.v1",
        "scientific_evidence": False,
        "fake_child": True,
    }
    (root / "manifest.json").write_bytes(direct.canonical_bytes(manifest))
    os.chmod(root / "manifest.json", 0o444)
    os.chmod(root, 0o555)
    return direct.sha256(root / "manifest.json")


def _dispatch_payload(
    path: Path,
    root: Path,
    review: Path,
    review_sha: str,
    stage: str,
    gate: dict[str, object],
) -> dict[str, object]:
    payload = {
        "schema": "schwo.phase6.v3_1_x.external_direct_dispatch.v1",
        "gate_id": direct.GATE_ID,
        "stage": stage,
        "exact_root": str(root),
        "package_sha256": (
            replacement.PACKAGE_SHA256
            if stage == "official"
            else replacement.REPAIR2_PACKAGE_SHA256
        ),
        "implementation_hashes": gate["implementation_hashes"],
        "implementation_review": {"path": str(review), "sha256": review_sha},
        "invocation": replacement._expected_invocation(stage, path, "ignored"),
        "requested_environment": {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": "runs/phase5/paper_figures/runtime_overlays/mpmath_1p4p1_py314:src",
        },
        "observed_environment": dict(os.environ),
        "one_use_id": "1" * 64,
        "predecessor_science_reused": False,
        "sentinel_science_reused": False,
    }
    if stage == replacement.MICRO_STAGE:
        payload["operation"] = replacement.MICRO_OPERATION
    elif stage == "sentinel":
        payload["operation"] = replacement.FULL_WLS_OPERATION
    return payload


def _seal_dispatch(
    path: Path,
    payload: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> str:
    if path.exists():
        os.chmod(path, 0o644)
    path.write_bytes(direct.canonical_bytes(payload))
    os.chmod(path, 0o444)
    digest = direct.sha256(path)
    monkeypatch.setattr(
        replacement.sys,
        "argv",
        [
            str(replacement.CLI_PATH),
            str(payload["stage"]),
            "--dispatch",
            str(path),
            "--dispatch-sha256",
            digest,
        ],
    )
    return digest


def _prepare_valid_attempt_0003_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> SimpleNamespace:
    gate = replacement.verify_start_gate()
    monkeypatch.setattr(
        replacement.os, "environ", dict(replacement.OBSERVED_CLEAN_LAUNCH_ENVIRONMENT)
    )
    review = tmp_path / REPAIR_REVIEW_RELATIVE_PATH
    review_sha = _write_complete_repair_review(review, gate)
    dispatch_archive = tmp_path / "dispatch_archive"
    dispatch_archive.mkdir()
    dispatch = dispatch_archive / SENTINEL_ATTEMPT_0003
    root_parent = tmp_path / "root_parent"
    root_parent.mkdir()
    micro_root = (
        root_parent / "v3_1_x_source_load_micro_sentinel_v1_20260813T175959Z_py314"
    )
    micro_manifest_sha = _write_micro_root(micro_root, gate)
    micro_review = tmp_path / MICRO_REVIEW_RELATIVE_PATH
    micro_review_sha = _write_micro_review(
        micro_review, gate, micro_root, micro_manifest_sha
    )
    root = (
        root_parent
        / "v3_1_x_external_direct_sentinel_repair2_v1_20260813T180000Z_py314"
    )
    monkeypatch.setattr(replacement, "DISPATCH_ARCHIVE_DIR", dispatch_archive)
    monkeypatch.setattr(replacement, "ROOT_PARENT", root_parent)
    monkeypatch.setattr(replacement, "IMPLEMENTATION_REVIEW_PATH", review)
    monkeypatch.setattr(replacement, "MICRO_REVIEW_PATH", micro_review)
    monkeypatch.setattr(
        replacement,
        "validate_source_load_micro",
        lambda *_args, **_kwargs: None,
        raising=False,
    )
    payload = _dispatch_payload(dispatch, root, review, review_sha, "sentinel", gate)
    payload["micro_review"] = {
        "path": str(micro_review),
        "sha256": micro_review_sha,
    }
    payload["micro_root"] = {
        "path": str(micro_root),
        "manifest_sha256": micro_manifest_sha,
    }
    digest = _seal_dispatch(dispatch, payload, monkeypatch)
    return SimpleNamespace(
        gate=gate,
        review=review,
        micro_review=micro_review,
        micro_root=micro_root,
        micro_manifest_sha=micro_manifest_sha,
        dispatch=dispatch,
        root=root,
        root_parent=root_parent,
        payload=payload,
        digest=digest,
    )


def _prepare_valid_micro_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> SimpleNamespace:
    gate = replacement.verify_start_gate()
    monkeypatch.setattr(
        replacement.os, "environ", dict(replacement.OBSERVED_CLEAN_LAUNCH_ENVIRONMENT)
    )
    review = tmp_path / REPAIR_REVIEW_RELATIVE_PATH
    review_sha = _write_complete_repair_review(review, gate)
    dispatch_archive = tmp_path / "dispatch_archive"
    dispatch_archive.mkdir()
    dispatch = (
        dispatch_archive / "T0_2026-08-13_v3_1_x_source_load_micro_sentinel_dispatch_"
        "attempt_0001.json"
    )
    root_parent = tmp_path / "root_parent"
    root_parent.mkdir()
    root = root_parent / "v3_1_x_source_load_micro_sentinel_v1_20260813T180000Z_py314"
    monkeypatch.setattr(replacement, "DISPATCH_ARCHIVE_DIR", dispatch_archive)
    monkeypatch.setattr(replacement, "ROOT_PARENT", root_parent)
    monkeypatch.setattr(replacement, "IMPLEMENTATION_REVIEW_PATH", review)
    payload = _dispatch_payload(
        dispatch,
        root,
        review,
        review_sha,
        replacement.MICRO_STAGE,
        gate,
    )
    digest = _seal_dispatch(dispatch, payload, monkeypatch)
    return SimpleNamespace(
        gate=gate,
        review=review,
        dispatch=dispatch,
        root=root,
        root_parent=root_parent,
        payload=payload,
        digest=digest,
    )


def _fake_micro_wls_result(
    request: dict[str, object],
    expected: dict[str, object],
    *,
    fake_child: bool,
) -> dict[str, object]:
    records = request["loaded_source_records"]
    projection = replacement.normalize_loaded_source_ledger(records)
    return {
        "schema": "schwo.phase6.v3_1_x.source_load_micro_wls_result.v1",
        "operation": replacement.MICRO_OPERATION,
        "key": expected["key"],
        "node": expected["node"],
        "overlay": request["overlay"],
        "projection_field_order": list(replacement.SOURCE_FIELD_ORDER),
        "expected_source_projection": projection,
        "loaded_contexts_start": list(direct.LOADED_SOURCE_CONTEXTS),
        "loaded_contexts_end": list(direct.LOADED_SOURCE_CONTEXTS),
        "loaded_source_start": records,
        "loaded_source_end": records,
        "loaded_source_projection_start": projection,
        "loaded_source_projection_end": projection,
        "preload_state": {
            "packages": ["System`"],
            "context_path": ["System`"],
            "search_path": ["/frozen/system"],
            "regge_wheeler_context_count": 0,
            "regge_wheeler_paclet_candidate_count": 1,
            "find_file_before_load": "/installed/ReggeWheeler.m",
        },
        "paclet": {
            "candidate_count_after_load": 2,
            "loaded_count": 1,
            "loaded_root": request["overlay"]["root"],
        },
        "counters": dict(replacement.MICRO_COUNTERS),
        "scientific_evidence": False,
        "reusable_as_science": False,
        "reusable_as_full_sentinel_record": False,
        "terminal_state": "PASS_PENDING_FORMAL_T7_REVIEW",
        "runtime": {
            "wolfram_version": "synthetic",
            "system_id": "synthetic",
            "observed_environment": dict(replacement.OBSERVED_CLEAN_LAUNCH_ENVIRONMENT),
            "fake_child": fake_child,
        },
    }


def test_micro_formal_boundary_rejects_self_confirming_fake_result(
    tmp_path: Path,
) -> None:
    expected = direct.sentinel_plan()[0]
    overlay_root = tmp_path / "overlay"
    overlay = direct.materialize_overlay(
        direct.BHPT_SNAPSHOT_ROOT,
        overlay_root,
        expected["node"]["overlay_variant"],
    )
    request = replacement.build_wls_request(
        expected, overlay, operation=replacement.MICRO_OPERATION
    )
    raw = _fake_micro_wls_result(request, expected, fake_child=True)
    with pytest.raises(ExternalDirectContractError, match="micro runtime identity"):
        replacement._validate_micro_wls_result(raw, request, expected)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("preloaded_context", "preloaded context contamination"),
        ("candidate_bool", "preloaded context contamination"),
        ("wrong_loaded_root", "Paclet origin mismatch"),
        ("zero_postload_candidates", "Paclet origin mismatch"),
    ],
)
def test_micro_preload_and_paclet_origin_fail_closed(
    tmp_path: Path, mutation: str, message: str
) -> None:
    expected = direct.sentinel_plan()[0]
    overlay = direct.materialize_overlay(
        direct.BHPT_SNAPSHOT_ROOT,
        tmp_path / "overlay",
        expected["node"]["overlay_variant"],
    )
    request = replacement.build_wls_request(
        expected, overlay, operation=replacement.MICRO_OPERATION
    )
    raw = _fake_micro_wls_result(request, expected, fake_child=False)
    if mutation == "preloaded_context":
        raw["preload_state"]["packages"].append("ReggeWheeler`")
    elif mutation == "candidate_bool":
        raw["preload_state"]["regge_wheeler_paclet_candidate_count"] = True
    elif mutation == "wrong_loaded_root":
        raw["paclet"]["loaded_root"] = str(tmp_path / "alternate")
    else:
        raw["paclet"]["candidate_count_after_load"] = 0
    with pytest.raises(ExternalDirectContractError, match=message):
        replacement._validate_micro_wls_result(raw, request, expected)


def test_micro_public_runner_rejects_fake_without_wolfram_or_science(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _prepare_valid_micro_dispatch(tmp_path, monkeypatch)
    calls = 0

    def fake_child(
        request_path: Path,
        _output_path: Path,
        expected: dict[str, object],
        **_kwargs: object,
    ) -> dict[str, object]:
        nonlocal calls
        calls += 1
        request = replacement.load_canonical(request_path)
        return _fake_micro_wls_result(request, expected, fake_child=True)

    monkeypatch.setattr(replacement, "verify_start_gate", lambda: case.gate)
    monkeypatch.setattr(replacement, "run_wolfram_child", fake_child)
    with pytest.raises(ExternalDirectContractError, match="micro runtime identity"):
        replacement.run_source_load_micro(case.dispatch, case.digest)
    assert calls == 1
    assert stat.S_IMODE(case.root.stat().st_mode) == 0o555
    failure = replacement.load_canonical(case.root / "failure.json")
    assert failure["scientific_pass"] is False
    assert failure["retry_permitted"] is False
    assert not (case.root / "micro_result.json").exists()


def test_exact_future_namespace_review_surrogate_passes_without_consumption_or_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _prepare_valid_attempt_0003_dispatch(tmp_path, monkeypatch)
    authority = replacement.validate_dispatch(
        case.dispatch,
        case.digest,
        stage="sentinel",
        start_gate=case.gate,
    )
    assert authority["root"] == case.root
    assert case.gate["scientific_evidence"] is False
    assert not case.root.exists()
    assert not list(case.root_parent.glob("*/dispatch_consumption.json"))


@pytest.mark.parametrize(
    "mutation,expected",
    [
        ("missing_micro_review", "dispatch schema mismatch"),
        ("missing_micro_root", "dispatch schema mismatch"),
        ("wrong_micro_review_path", "review path mismatch"),
        ("wrong_micro_review_digest", "frozen identity drift"),
        ("failure_envelope", "review verdict mismatch"),
        ("full_sentinel_label", "review verdict mismatch"),
        ("wrong_micro_manifest", "frozen identity drift"),
        ("micro_operation", "sentinel dispatch operation mismatch"),
    ],
)
def test_full_attempt_0003_requires_exact_micro_authority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
    expected: str,
) -> None:
    case = _prepare_valid_attempt_0003_dispatch(tmp_path, monkeypatch)
    if mutation == "missing_micro_review":
        case.payload.pop("micro_review")
    elif mutation == "missing_micro_root":
        case.payload.pop("micro_root")
    elif mutation == "wrong_micro_review_path":
        case.payload["micro_review"]["path"] = str(tmp_path / "alternate-review.md")
    elif mutation == "wrong_micro_review_digest":
        case.payload["micro_review"]["sha256"] = "0" * 64
    elif mutation in {"failure_envelope", "full_sentinel_label"}:
        text = case.micro_review.read_text()
        addition = (
            "\n".join(replacement.MICRO_REVIEW_FAILURE_TOKENS)
            if mutation == "failure_envelope"
            else "35-call sentinel\n35/70/105"
        )
        os.chmod(case.micro_review, 0o644)
        case.micro_review.write_text(text + addition + "\n")
        os.chmod(case.micro_review, 0o444)
        case.payload["micro_review"]["sha256"] = direct.sha256(case.micro_review)
    elif mutation == "wrong_micro_manifest":
        case.payload["micro_root"]["manifest_sha256"] = "0" * 64
    else:
        case.payload["operation"] = replacement.MICRO_OPERATION
    digest = _seal_dispatch(case.dispatch, case.payload, monkeypatch)
    with pytest.raises(ExternalDirectContractError, match=expected):
        replacement.validate_dispatch(
            case.dispatch,
            digest,
            stage="sentinel",
            start_gate=case.gate,
        )
    assert not case.root.exists()


def test_full_attempt_0003_rehashes_source_after_micro_approval(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _prepare_valid_attempt_0003_dispatch(tmp_path, monkeypatch)
    source_path = case.micro_root / "source_start.json"
    os.chmod(case.micro_root, 0o755)
    os.chmod(source_path, 0o644)
    source = direct.load_canonical(source_path)
    source["implementation_hashes"] = {
        **source["implementation_hashes"],
        "synthetic/source_drift.py": "0" * 64,
    }
    source_path.write_bytes(direct.canonical_bytes(source))
    os.chmod(source_path, 0o444)
    os.chmod(case.micro_root, 0o555)
    with pytest.raises(
        ExternalDirectContractError, match="source drift after micro approval"
    ):
        replacement.validate_dispatch(
            case.dispatch,
            case.digest,
            stage="sentinel",
            start_gate=case.gate,
        )
    assert not case.root.exists()


def test_micro_full_operation_and_official_namespace_remain_distinct() -> None:
    assert replacement.MICRO_OPERATION != replacement.FULL_WLS_OPERATION
    assert replacement.MICRO_DISPATCH_PATTERN.fullmatch(
        "T0_2026-08-13_v3_1_x_source_load_micro_sentinel_dispatch_attempt_0001.json"
    )
    assert replacement.SENTINEL_DISPATCH_PATTERN.fullmatch(SENTINEL_ATTEMPT_0003)
    assert not replacement.MICRO_DISPATCH_PATTERN.fullmatch(SENTINEL_ATTEMPT_0003)
    assert not replacement.SENTINEL_DISPATCH_PATTERN.fullmatch(
        "T0_2026-08-13_v3_1_x_source_load_micro_sentinel_dispatch_attempt_0001.json"
    )
    assert replacement.OFFICIAL_DISPATCH_PATTERN.pattern == (
        r"T0_\d{4}-\d{2}-\d{2}_v3_1_x_external_direct_official_dispatch_"
        r"attempt_0001\.json"
    )
    assert replacement.OFFICIAL_DISPATCH_PATTERN.fullmatch(
        "T0_2026-08-13_v3_1_x_external_direct_official_dispatch_attempt_0001.json"
    )
    assert replacement.OFFICIAL_DISPATCH_PATTERN.fullmatch(
        "T0_2099-12-31_v3_1_x_external_direct_official_dispatch_attempt_0001.json"
    )
    assert not replacement.OFFICIAL_DISPATCH_PATTERN.fullmatch(
        "T0_2026-08-13_v3_1_x_external_direct_official_dispatch_attempt_0002.json"
    )


def test_consumed_immutable_attempt_0001_rejects_before_payload_or_review() -> None:
    gate = replacement.verify_start_gate()
    predecessor = (
        replacement.DISPATCH_ARCHIVE_DIR
        / "T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0001.json"
    )
    assert direct.sha256(predecessor) == (
        "5a8bebeca2f1f0d9bcedf6bf4bf7986d8a9710df2b581bf2f56ef145597997a9"
    )
    with pytest.raises(
        ExternalDirectContractError, match="dispatch authority namespace mismatch"
    ):
        replacement.validate_dispatch(
            predecessor,
            direct.sha256(predecessor),
            stage="sentinel",
            start_gate=gate,
        )


def test_existing_failed_sentinel_root_cannot_be_reused() -> None:
    failed_root = (
        replacement.ROOT_PARENT
        / "v3_1_x_external_direct_sentinel_v1_20260813T055002Z_py314"
    )
    assert failed_root.is_dir()
    with pytest.raises(
        ExternalDirectContractError, match="execution root must be absent"
    ):
        replacement._validate_utc_namespace(failed_root, "sentinel")


@pytest.mark.parametrize(
    "basename",
    [
        "T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0000.json",
        "T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0001.json",
        "T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0002.json",
        "T0_2026-08-13_v3_1_x_external_direct_sentinel_dispatch_attempt_0042.json",
        "T0_2026-08-12_v3_1_x_external_direct_sentinel_dispatch_attempt_0003.json",
        "T0_2026-08-14_v3_1_x_external_direct_sentinel_dispatch_attempt_0003.json",
        f"{SENTINEL_ATTEMPT_0003}.bak",
        f"alias_{SENTINEL_ATTEMPT_0003}",
    ],
)
def test_sentinel_dispatch_rejects_all_nonexact_attempt_names_with_fresh_payload(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    basename: str,
) -> None:
    case = _prepare_valid_attempt_0003_dispatch(tmp_path, monkeypatch)
    candidate = case.dispatch.with_name(basename)
    fresh_payload = _dispatch_payload(
        candidate,
        case.root,
        case.review,
        direct.sha256(case.review),
        "sentinel",
        case.gate,
    )
    digest = _seal_dispatch(candidate, fresh_payload, monkeypatch)
    with pytest.raises(
        ExternalDirectContractError, match="dispatch authority namespace mismatch"
    ):
        replacement.validate_dispatch(
            candidate,
            digest,
            stage="sentinel",
            start_gate=case.gate,
        )
    assert not case.root.exists()
    assert not list(case.root_parent.glob("*/dispatch_consumption.json"))


def test_sentinel_dispatch_rejects_wrong_parent_symlink_and_parent_alias(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _prepare_valid_attempt_0003_dispatch(tmp_path, monkeypatch)

    wrong_parent = tmp_path / "wrong_parent"
    wrong_parent.mkdir()
    wrong_path = wrong_parent / SENTINEL_ATTEMPT_0003
    wrong_path.write_bytes(case.dispatch.read_bytes())
    os.chmod(wrong_path, 0o444)
    wrong_sha = direct.sha256(wrong_path)
    monkeypatch.setattr(
        replacement.sys,
        "argv",
        [
            str(replacement.CLI_PATH),
            "sentinel",
            "--dispatch",
            str(wrong_path),
            "--dispatch-sha256",
            wrong_sha,
        ],
    )
    with pytest.raises(
        ExternalDirectContractError, match="dispatch authority namespace mismatch"
    ):
        replacement.validate_dispatch(
            wrong_path,
            wrong_sha,
            stage="sentinel",
            start_gate=case.gate,
        )

    symlink_archive = tmp_path / "symlink_archive"
    symlink_archive.mkdir()
    symlink_path = symlink_archive / SENTINEL_ATTEMPT_0003
    symlink_path.symlink_to(case.dispatch)
    monkeypatch.setattr(replacement, "DISPATCH_ARCHIVE_DIR", symlink_archive)
    with pytest.raises(
        ExternalDirectContractError, match="dispatch authority namespace mismatch"
    ):
        replacement.validate_dispatch(
            symlink_path,
            case.digest,
            stage="sentinel",
            start_gate=case.gate,
        )

    archive_alias = tmp_path / "archive_alias"
    archive_alias.symlink_to(case.dispatch.parent, target_is_directory=True)
    alias_path = archive_alias / SENTINEL_ATTEMPT_0003
    monkeypatch.setattr(replacement, "DISPATCH_ARCHIVE_DIR", case.dispatch.parent)
    with pytest.raises(
        ExternalDirectContractError, match="dispatch authority namespace mismatch"
    ):
        replacement.validate_dispatch(
            alias_path,
            case.digest,
            stage="sentinel",
            start_gate=case.gate,
        )

    assert not case.root.exists()
    assert not list(case.root_parent.glob("*/dispatch_consumption.json"))


@pytest.mark.parametrize(
    "review_relative_path",
    [
        "docs/handoffs/archive/"
        "T7_2026-08-13_v3_1_x_external_direct_route_sentinel_terminal_review.md",
        "docs/handoffs/archive/T7_2026-08-13_v3_1_x_authority_bridge_delta_review.md",
        "docs/handoffs/archive/"
        "T7_2026-08-13_v3_1_x_external_direct_route_implementation_"
        "delta_recheck_1.md",
        "docs/handoffs/archive/"
        "T7_2026-08-13_v3_1_x_external_direct_route_implementation_"
        "delta_recheck_2.md",
    ],
)
def test_old_yellow_bridge_and_escalate_predecessor_authorities_fail(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    review_relative_path: str,
) -> None:
    case = _prepare_valid_attempt_0003_dispatch(tmp_path, monkeypatch)
    predecessor = replacement.ROOT / review_relative_path
    monkeypatch.setattr(replacement, "IMPLEMENTATION_REVIEW_PATH", predecessor)
    case.payload["implementation_review"] = {
        "path": str(predecessor),
        "sha256": direct.sha256(predecessor),
    }
    digest = _seal_dispatch(case.dispatch, case.payload, monkeypatch)
    with pytest.raises(ExternalDirectContractError, match="review verdict mismatch"):
        replacement.validate_dispatch(
            case.dispatch,
            digest,
            stage="sentinel",
            start_gate=case.gate,
        )


def test_arbitrary_implementation_review_path_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _prepare_valid_attempt_0003_dispatch(tmp_path, monkeypatch)
    arbitrary = tmp_path / "arbitrary" / "review.md"
    arbitrary_sha = _write_complete_repair_review(arbitrary, case.gate)
    case.payload["implementation_review"] = {
        "path": str(arbitrary),
        "sha256": arbitrary_sha,
    }
    digest = _seal_dispatch(case.dispatch, case.payload, monkeypatch)
    with pytest.raises(ExternalDirectContractError, match="review path mismatch"):
        replacement.validate_dispatch(
            case.dispatch,
            digest,
            stage="sentinel",
            start_gate=case.gate,
        )


def test_missing_future_implementation_review_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _prepare_valid_attempt_0003_dispatch(tmp_path, monkeypatch)
    os.chmod(case.review, 0o644)
    case.review.unlink()
    with pytest.raises(FileNotFoundError):
        replacement.validate_dispatch(
            case.dispatch,
            case.digest,
            stage="sentinel",
            start_gate=case.gate,
        )


@pytest.mark.parametrize(
    "mutation",
    ["digest", "token", "missing_authority", "missing_hash", "stale_hash"],
)
def test_review_digest_token_and_implementation_hash_adversaries_fail(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    case = _prepare_valid_attempt_0003_dispatch(tmp_path, monkeypatch)
    if mutation == "digest":
        case.payload["implementation_review"]["sha256"] = "0" * 64
        expected = "frozen identity drift"
    else:
        text = case.review.read_text()
        first_hash = next(iter(case.gate["implementation_hashes"].values()))
        if mutation == "token":
            text = text.replace("ADVANCE_DECISION: ADVANCE", "ADVANCE_DECISION: REPAIR")
            expected = "review verdict mismatch"
        elif mutation == "missing_authority":
            authority_hash = (
                replacement.IMPLEMENTATION_REVIEW_REQUIRED_AUTHORITY_HASHES[0]
            )
            text = text.replace(f"{authority_hash}\n", "")
            expected = "implementation review authority mismatch"
        elif mutation == "missing_hash":
            text = text.replace(f"{first_hash}\n", "")
            expected = "implementation review hash binding mismatch"
        else:
            text = text.replace(first_hash, "0" * 64)
            expected = "implementation review hash binding mismatch"
        os.chmod(case.review, 0o644)
        case.review.write_text(text)
        os.chmod(case.review, 0o444)
        case.payload["implementation_review"]["sha256"] = direct.sha256(case.review)
    digest = _seal_dispatch(case.dispatch, case.payload, monkeypatch)
    with pytest.raises(ExternalDirectContractError, match=expected):
        replacement.validate_dispatch(
            case.dispatch,
            digest,
            stage="sentinel",
            start_gate=case.gate,
        )


@pytest.mark.parametrize("implementation_index", range(6))
def test_every_live_implementation_hash_is_required_by_future_review(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    implementation_index: int,
) -> None:
    case = _prepare_valid_attempt_0003_dispatch(tmp_path, monkeypatch)
    implementation_hash = list(case.gate["implementation_hashes"].values())[
        implementation_index
    ]
    text = case.review.read_text().replace(f"{implementation_hash}\n", "")
    os.chmod(case.review, 0o644)
    case.review.write_text(text)
    os.chmod(case.review, 0o444)
    case.payload["implementation_review"]["sha256"] = direct.sha256(case.review)
    digest = _seal_dispatch(case.dispatch, case.payload, monkeypatch)
    with pytest.raises(
        ExternalDirectContractError,
        match="implementation review hash binding mismatch",
    ):
        replacement.validate_dispatch(
            case.dispatch,
            digest,
            stage="sentinel",
            start_gate=case.gate,
        )


@pytest.mark.parametrize(
    "mutation",
    ["environment", "argv", "cwd", "executable", "launcher", "root_reuse", "replay"],
)
def test_runtime_and_replay_adversaries_fail(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    case = _prepare_valid_attempt_0003_dispatch(tmp_path, monkeypatch)
    if mutation == "environment":
        monkeypatch.setattr(
            replacement.os,
            "environ",
            {
                **replacement.OBSERVED_CLEAN_LAUNCH_ENVIRONMENT,
                "SCHWO_UNREVIEWED_EXTRA": "1",
            },
        )
        expected = "environment"
    elif mutation == "argv":
        monkeypatch.setattr(replacement.sys, "argv", ["wrong"])
        expected = "live executable/argv/cwd mismatch"
    elif mutation == "cwd":
        monkeypatch.chdir(tmp_path)
        expected = "live executable/argv/cwd mismatch"
    elif mutation == "executable":
        monkeypatch.setattr(replacement.sys, "executable", "/bin/sh")
        expected = "live executable/argv/cwd mismatch"
    elif mutation == "launcher":
        case.payload["invocation"]["launcher"] = "/tmp/not-the-frozen-launcher"
        case.digest = _seal_dispatch(case.dispatch, case.payload, monkeypatch)
        expected = "dispatch invocation mismatch"
    elif mutation == "root_reuse":
        case.root.mkdir()
        expected = "execution root must be absent"
    else:
        consumed_root = (
            case.root_parent
            / "v3_1_x_external_direct_sentinel_v1_20260813T175959Z_py314"
        )
        consumed_root.mkdir()
        (consumed_root / "dispatch_consumption.json").write_bytes(
            direct.canonical_bytes({"one_use_id": case.payload["one_use_id"]})
        )
        expected = "dispatch replay"
    with pytest.raises(ExternalDirectContractError, match=expected):
        replacement.validate_dispatch(
            case.dispatch,
            case.digest,
            stage="sentinel",
            start_gate=case.gate,
        )


def test_dispatch_root_hash_argv_environment_and_replay_adversaries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _prepare_valid_attempt_0003_dispatch(tmp_path, monkeypatch)
    authority = replacement.validate_dispatch(
        case.dispatch, case.digest, stage="sentinel", start_gate=case.gate
    )
    assert authority["root"] == case.root
    mutations = []
    for field, value in (
        ("exact_root", str(tmp_path / "wrong")),
        ("package_sha256", "0" * 64),
        ("requested_environment", {}),
        ("observed_environment", {}),
        ("predecessor_science_reused", True),
    ):
        mutant = copy.deepcopy(case.payload)
        mutant[field] = value
        mutations.append(mutant)
    for mutant in mutations:
        bad_sha = _seal_dispatch(case.dispatch, mutant, monkeypatch)
        with pytest.raises(ExternalDirectContractError):
            replacement.validate_dispatch(
                case.dispatch, bad_sha, stage="sentinel", start_gate=case.gate
            )


def test_dispatch_rejects_unreviewed_environment_authority_and_review_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _prepare_valid_attempt_0003_dispatch(tmp_path, monkeypatch)
    replacement.validate_dispatch(
        case.dispatch, case.digest, stage="sentinel", start_gate=case.gate
    )
    monkeypatch.setattr(
        replacement.os,
        "environ",
        {
            **replacement.OBSERVED_CLEAN_LAUNCH_ENVIRONMENT,
            "SCHWO_UNREVIEWED_EXTRA": "1",
        },
    )
    with pytest.raises(ExternalDirectContractError, match="environment"):
        replacement.validate_dispatch(
            case.dispatch,
            case.digest,
            stage="sentinel",
            start_gate=case.gate,
        )


def test_publication_collision_symlink_and_nofollow(tmp_path: Path) -> None:
    target = tmp_path / "record.json"
    identity = replacement._exclusive_publish(target, b"{}\n")
    assert identity["mode"] == 0o444 and identity["nlink"] == 1
    with pytest.raises(FileExistsError):
        replacement._exclusive_publish(target, b"x")
    link = tmp_path / "link.json"
    link.symlink_to(target)
    with pytest.raises(FileExistsError):
        replacement._exclusive_publish(link, b"x")


class _LifecyclePopen:
    def __init__(
        self, *_args: object, timeout: bool = False, **_kwargs: object
    ) -> None:
        self.pid = 91827
        self.returncode: int | None = None
        self._timeout = timeout
        self._waits = 0

    def poll(self) -> int | None:
        return self.returncode

    def wait(self, timeout: float | None = None) -> int:
        del timeout
        self._waits += 1
        if self._timeout and self._waits == 1:
            raise subprocess.TimeoutExpired("fake", 1)
        if self.returncode is None:
            self.returncode = -9 if self._timeout else 0
        return self.returncode


class _DuplicateRawPopen(_LifecyclePopen):
    launches = 0

    def __init__(self, command: list[str], **kwargs: object) -> None:
        super().__init__(command, **kwargs)
        type(self).launches += 1
        self._staging = Path(command[-1])

    def wait(self, timeout: float | None = None) -> int:
        runtime = json.dumps(
            {
                "observed_environment": dict(
                    replacement.OBSERVED_CLEAN_LAUNCH_ENVIRONMENT
                )
            },
            sort_keys=True,
        )
        self._staging.write_text(
            '{"runtime":' + runtime + ',"runtime":' + runtime + "}"
        )
        return super().wait(timeout)


def test_duplicate_raw_staging_rejects_after_one_popen_and_before_acceptance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = tmp_path / "request.json"
    request.write_bytes(direct.canonical_bytes({"schema": "synthetic.request"}))
    os.chmod(request, 0o444)
    output = tmp_path / "call_0000.raw.json"
    expected = direct.sentinel_plan()[0]
    _DuplicateRawPopen.launches = 0
    monkeypatch.setattr(replacement.subprocess, "Popen", _DuplicateRawPopen)
    monkeypatch.setattr(replacement.os, "getpgid", lambda _pid: 91827)
    monkeypatch.setattr(replacement.os, "getsid", lambda _pid: 91827)
    monkeypatch.setattr(replacement.os, "killpg", lambda *_args: None)
    monkeypatch.setattr(replacement, "_process_group_empty", lambda _pgid: True)
    with pytest.raises(ExternalDirectContractError, match="lifecycle exception"):
        replacement.run_wolfram_child(request, output, expected)
    assert _DuplicateRawPopen.launches == 1
    assert not output.exists()
    receipt = replacement.load_canonical(output.with_suffix(".receipt.json"))
    terminal = replacement.load_canonical(output.with_suffix(".terminal.json"))
    assert receipt["exception_type"] == "ExternalDirectContractError"
    assert terminal["child_reaped"] is True
    assert terminal["process_group_empty"] is True


@pytest.mark.parametrize("failure", ["stream", "running", "timeout"])
def test_child_lifecycle_failures_publish_durable_receipt_and_terminal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    request = tmp_path / "request.json"
    request.write_bytes(direct.canonical_bytes({"schema": "fake"}))
    os.chmod(request, 0o444)
    output = tmp_path / "call_0000.raw.json"
    expected = direct.sentinel_plan()[0]
    monkeypatch.setattr(replacement.os, "getpgid", lambda _pid: 91827)
    monkeypatch.setattr(replacement.os, "getsid", lambda _pid: 91827)
    monkeypatch.setattr(replacement.os, "killpg", lambda *_args: None)
    monkeypatch.setattr(replacement, "_process_group_empty", lambda _pgid: True)
    if failure == "stream":
        monkeypatch.setattr(
            replacement,
            "_open_exclusive_stream",
            lambda _path: (_ for _ in ()).throw(OSError("stream-open")),
        )
    else:
        monkeypatch.setattr(
            replacement.subprocess,
            "Popen",
            lambda *_args, **_kwargs: _LifecyclePopen(timeout=failure == "timeout"),
        )
    if failure == "running":
        original_publish = replacement._exclusive_publish

        def fail_running(
            path: Path, *args: object, **kwargs: object
        ) -> dict[str, object]:
            if path.name.endswith(".running.json"):
                raise OSError("running-publication")
            return original_publish(path, *args, **kwargs)

        monkeypatch.setattr(replacement, "_exclusive_publish", fail_running)
    with pytest.raises(ExternalDirectContractError):
        replacement.run_wolfram_child(request, output, expected, timeout_seconds=0.01)
    receipt = direct.load_canonical(output.with_suffix(".receipt.json"))
    terminal = direct.load_canonical(output.with_suffix(".terminal.json"))
    assert (
        receipt["requested_environment"] == replacement.REQUESTED_EXECUTION_ENVIRONMENT
    )
    assert terminal["receipt"] == replacement._file_identity(
        output.with_suffix(".receipt.json")
    )
    assert terminal["finished_utc"].endswith("Z")
    assert terminal["exception_type"] is not None or terminal["timed_out"] is True


def test_execution_outcome_rejects_semantically_tampered_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "v3_1_x_external_direct_sentinel_v1_20260813T151500Z_py314"
    _patch_control(monkeypatch, root, "sentinel")
    replacement.run_sentinel(
        tmp_path / "fake_dispatch.json", "a" * 64, child_runner=_fake_child
    )
    os.chmod(root, 0o755)
    receipt = next((root / "external_evidence").glob("node_evidence/*.receipt.json"))
    os.chmod(receipt, 0o644)
    payload = direct.load_canonical(receipt)
    payload["child_reaped"] = False
    receipt.write_bytes(direct.canonical_bytes(payload))
    os.chmod(receipt, 0o444)
    os.chmod(root, 0o555)
    with pytest.raises(ExternalDirectContractError):
        replacement.validate_sentinel(root)
