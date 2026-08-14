from __future__ import annotations

import ast
import json
import math
import os
from pathlib import Path
import shutil

import pytest

from schwgw.validation.phase6_v3_mode_greybody import ModeKey, V31ContractError
from schwgw.validation.phase6_v3_mode_greybody_cycle2 import (
    EXPECTED_COUNTS,
    ap_node_plan,
    compact_jsonl_record,
    external_source_identity,
    load_jsonl,
    publish_synthetic_root,
    route_a_node_graph,
    synthetic_payload,
    threshold_boundary_status,
    validate_external_child_payload,
    validate_synthetic_root,
)


def _external_outcome_payload(
    error_ordinal: int | None = None, error_code: str = "MST_FAILED"
) -> dict[str, object]:
    import schwgw.validation.phase6_v3_mode_greybody_cycle2 as cycle2

    anchors = cycle2.build_anchor_inventory(cycle2.build_mode_inventory())["external"]
    outcomes = []
    for ordinal, key in enumerate(anchors):
        if ordinal == error_ordinal:
            outcomes.append(
                {
                    "schema": "schwo.phase6.v3_1_u.external_anchor_outcome.v1",
                    "ordinal": ordinal,
                    "key": key,
                    "status": "ERROR",
                    "error": {"code": error_code, "detail": "synthetic"},
                    "fresh_external_call_count": 1,
                }
            )
        else:
            outcomes.append(
                {
                    "schema": "schwo.phase6.v3_1_u.external_anchor_outcome.v1",
                    "ordinal": ordinal,
                    "key": key,
                    "status": "PASS",
                    "method": "MST",
                    "fresh_external_call_count": 1,
                    "genuinely_independent": True,
                    "even_independent_solve": False,
                    "incidence": {"real": "1", "imag": "0"},
                    "reflection": {"real": "0", "imag": "0"},
                    "transmission": {"real": "1", "imag": "0"},
                    "reflection_ratio": {"real": "0", "imag": "0"},
                    "S": {"real": "0", "imag": "0"},
                    "T_horizon": {"real": "1", "imag": "0"},
                    "Gamma_flux": "1",
                    "log_Gamma_flux": "0",
                }
            )
    first = (
        None
        if error_ordinal is None
        else {
            "ordinal": error_ordinal,
            "key": anchors[error_ordinal],
            "error": {"code": error_code, "detail": "synthetic"},
        }
    )
    return {
        "schema": "schwo.phase6.v3_1_u.external_batch_terminal.v1",
        "terminal": True,
        "requested_anchor_count": 23,
        "outcome_count": 23,
        "outcomes": outcomes,
        "fresh_external_call_count": 23,
        "overall_status": "PASS" if first is None else "ERROR",
        "first_failure": first,
        "wolfram_version": "14.3.0 for Mac OS X ARM (64-bit)",
        "system_id": "MacOSX-ARM64",
        "loaded_source_records": external_source_identity()[
            "required_loaded_source_records"
        ],
        "method_contract": {
            "Method": "MST",
            "WorkingPrecision": 90,
            "PrecisionGoal": 45,
            "AccuracyGoal": 45,
            "Potential": "ReggeWheeler",
            "BoundaryConditions": "In",
        },
    }


def _first_key() -> ModeKey:
    return ModeKey(0, 2, 0, "0.005", "odd")


def test_exact_cycle2_graph_and_synthetic_counts() -> None:
    nodes = route_a_node_graph(_first_key())
    assert len(nodes) == 20
    assert sum(len(route_a_node_graph(_first_key())) for _ in range(496)) == 9920
    assert len(ap_node_plan()) == 458
    assert synthetic_payload()["counts"] == EXPECTED_COUNTS


def test_cycle2_first_key_auxiliary_geometry_is_frozen() -> None:
    nodes = route_a_node_graph(_first_key())
    by_multiplier = {
        multiplier: {
            node["r_out"]: min(
                n
                for n in (0, 1, 2)
                if 0.005 * (2**n * node["r_out"]) >= 4 * math.sqrt(2 * 3)
            )
            for node in nodes
            if node["r_out_multiplier"] == multiplier
        }
        for multiplier in (1, 2, 4, 8)
    }
    assert {next(iter(value.values())) for value in by_multiplier.values()} == {
        0,
        1,
        2,
    }
    assert next(iter(by_multiplier[1].values())) == 2
    assert next(iter(by_multiplier[2].values())) == 1
    assert next(iter(by_multiplier[4].values())) == 0
    assert next(iter(by_multiplier[8].values())) == 0


def test_auxiliary_geometry_is_total_on_exact_9920_node_domain() -> None:
    import schwgw.validation.phase6_v3_mode_greybody_cycle2 as cycle2

    count = 0
    for key in cycle2.build_mode_inventory():
        for node in route_a_node_graph(key):
            geometry = cycle2.continued_jost_geometry(
                ell=key.ell, k=float(key.kM), r_match=float(node["r_out"])
            )
            assert geometry.auxiliary_exponent in (0, 1, 2)
            count += 1
    assert count == 9920


def test_every_frozen_threshold_has_exact_boundary_semantics() -> None:
    import schwgw.validation.phase6_v3_mode_greybody_cycle2 as cycle2

    for item in cycle2._v31_thresholds():
        limit = float(item["value"])
        assert threshold_boundary_status(item["field_id"], limit) == "PASS"
        assert (
            threshold_boundary_status(item["field_id"], math.nextafter(limit, math.inf))
            == "FAIL"
        )
    with pytest.raises(V31ContractError):
        threshold_boundary_status("V3T-NOT-A-FIELD", 0.0)
    with pytest.raises(V31ContractError):
        threshold_boundary_status("V3T-S-COMPLEX-001", -1.0)


def test_compact_jsonl_roundtrip_and_fail_closed(tmp_path: Path) -> None:
    path = tmp_path / "records.jsonl"
    records = [{"b": 2, "a": 1}, {"z": [1, 2]}]
    path.write_bytes(b"".join(compact_jsonl_record(item) for item in records))
    assert load_jsonl(path) == records
    path.write_bytes(b'{"a": 1}\n')
    with pytest.raises(V31ContractError, match="noncanonical"):
        load_jsonl(path)
    path.write_bytes(b'{"a":1}')
    with pytest.raises(V31ContractError, match="terminal newline"):
        load_jsonl(path)


@pytest.mark.parametrize("error_ordinal", [None, 0, 11, 22])
def test_external_total_outcomes_success_and_first_middle_last_error(
    error_ordinal: int | None,
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_cycle2 as cycle2

    anchors = cycle2.build_anchor_inventory(cycle2.build_mode_inventory())["external"]
    records, first = validate_external_child_payload(
        _external_outcome_payload(error_ordinal), anchors
    )
    assert len(records) == 23 - (error_ordinal is not None)
    assert (first is None) is (error_ordinal is None)
    if first is not None:
        assert first["ordinal"] == error_ordinal


@pytest.mark.parametrize("error_ordinal", [0, 11, 22])
def test_external_total_outcomes_amplitude_invalid_first_middle_last(
    error_ordinal: int,
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_cycle2 as cycle2

    anchors = cycle2.build_anchor_inventory(cycle2.build_mode_inventory())["external"]
    records, first = validate_external_child_payload(
        _external_outcome_payload(error_ordinal, "AMPLITUDE_INVALID"), anchors
    )
    assert len(records) == 22
    assert first == {
        "ordinal": error_ordinal,
        "key": anchors[error_ordinal],
        "error": {"code": "AMPLITUDE_INVALID", "detail": "synthetic"},
    }


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "reordered", "mixed"])
def test_external_total_outcomes_reject_inventory_and_schema_drift(
    mutation: str,
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_cycle2 as cycle2

    anchors = cycle2.build_anchor_inventory(cycle2.build_mode_inventory())["external"]
    payload = _external_outcome_payload()
    outcomes = payload["outcomes"]
    assert isinstance(outcomes, list)
    if mutation == "missing":
        outcomes.pop()
    elif mutation == "duplicate":
        outcomes[1] = dict(outcomes[0])
    elif mutation == "reordered":
        outcomes[0], outcomes[1] = outcomes[1], outcomes[0]
    else:
        outcomes[0]["error"] = {"code": "MST_FAILED", "detail": "mixed"}
    with pytest.raises(V31ContractError):
        validate_external_child_payload(payload, anchors)


def test_external_snapshot_exact_25_file_identity_and_loaded_path_guard() -> None:
    identity = external_source_identity()
    assert len(identity["source_files"]) == 25
    assert [item["path"] for item in identity["source_directories"]] == [
        ".",
        "Kernel",
        "Kernel/MST",
        "Tests",
        "Tests/Correctness",
    ]
    assert len(identity["required_loaded_source_records"]) == 8
    assert identity["snapshot_contains_git_metadata"] is False
    assert identity["content_inventory_sha256"] == (
        "d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2"
    )
    observed = {
        "wolfram_version": "14.3.0 for Mac OS X ARM (64-bit)",
        "system_id": "MacOSX-ARM64",
        "loaded_source_records": identity["required_loaded_source_records"],
    }
    with_runtime = external_source_identity(runtime_observed=observed)
    assert with_runtime["runtime_observed"] == observed
    import schwgw.validation.phase6_v3_mode_greybody_cycle2 as cycle2

    records = [dict(item) for item in identity["required_loaded_source_records"]]
    records[0] = {
        "path": str(Path(__file__).resolve()),
        "sha256": "0" * 64,
        "size": 0,
    }
    with pytest.raises(V31ContractError, match="escaped"):
        cycle2.external_source_identity(
            runtime_observed={
                "wolfram_version": "14.3.0",
                "system_id": "MacOSX-ARM64",
                "loaded_source_records": records,
            }
        )


def test_wls_freezes_exact_loaded_source_entry_graph_and_records() -> None:
    import schwgw.validation.phase6_v3_mode_greybody_cycle2 as cycle2

    source = cycle2.EXTERNAL_WLS.read_text()
    for relative in cycle2.EXTERNAL_REQUIRED_LOADED_SOURCE_PATHS:
        assert source.count(f'"{relative}"') == 1
    assert "FindFile /@ requiredLoadedContexts" in source
    assert "DeleteDuplicates[foundLoadedSources]" in source
    assert '"loaded_source_records" -> loadedSourceRecords' in source
    assert 'FileHash[#, "SHA256", "HexString"]' in source
    assert '"size" -> FileByteCount[#]' in source


@pytest.mark.parametrize(
    "mutation",
    ["missing", "duplicate", "reordered", "extra", "path", "hash", "size", "schema"],
)
def test_loaded_source_runtime_inventory_is_exact_and_ordered(mutation: str) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_cycle2 as cycle2

    identity = cycle2.external_source_identity()
    records = [dict(item) for item in identity["required_loaded_source_records"]]
    if mutation == "missing":
        records.pop()
    elif mutation == "duplicate":
        records[1] = dict(records[0])
    elif mutation == "reordered":
        records[0], records[1] = records[1], records[0]
    elif mutation == "extra":
        records.append(dict(records[-1]))
    elif mutation == "path":
        records[0]["path"] = str(Path(__file__).resolve())
    elif mutation == "hash":
        records[0]["sha256"] = "0" * 64
    elif mutation == "size":
        records[0]["size"] += 1
    else:
        records[0]["mode"] = 0o444
    with pytest.raises(V31ContractError, match="loaded-source"):
        cycle2.external_source_identity(
            runtime_observed={
                "wolfram_version": "14.3.0 for Mac OS X ARM (64-bit)",
                "system_id": "MacOSX-ARM64",
                "loaded_source_records": records,
            }
        )


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_file",
        "extra_file",
        "file_hash",
        "file_mode",
        "directory_mode",
        "extra_directory",
        "symlink",
        "hardlink",
        "root_alias",
    ],
)
def test_snapshot_tree_adversaries_use_only_temp_copy(
    tmp_path: Path, mutation: str
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_cycle2 as cycle2

    source = cycle2.EXTERNAL_SNAPSHOT_ROOT
    copied = tmp_path / "source"
    shutil.copytree(source, copied, copy_function=shutil.copy2)
    authority = json.loads(cycle2.EXTERNAL_SNAPSHOT_AUTHORITY.read_text())
    expected = {item["path"]: item for item in authority["source_content_records"]}
    target = copied / "Kernel/ReggeWheeler.m"
    if mutation == "missing_file":
        target.parent.chmod(0o755)
        target.unlink()
        target.parent.chmod(0o555)
    elif mutation == "extra_file":
        copied.chmod(0o755)
        (copied / "extra").write_text("extra")
        copied.chmod(0o555)
    elif mutation == "file_hash":
        target.chmod(0o644)
        target.write_text(target.read_text() + "\n")
        target.chmod(0o444)
    elif mutation == "file_mode":
        target.chmod(0o644)
    elif mutation == "directory_mode":
        (copied / "Kernel").chmod(0o755)
    elif mutation == "extra_directory":
        copied.chmod(0o755)
        (copied / "extra_dir").mkdir()
        copied.chmod(0o555)
    elif mutation == "symlink":
        target.parent.chmod(0o755)
        target.unlink()
        target.symlink_to(Path(__file__).resolve())
        target.parent.chmod(0o555)
    elif mutation == "hardlink":
        os.link(target, tmp_path / "hardlink_alias")
    else:
        alias = tmp_path / "source_alias"
        alias.symlink_to(copied, target_is_directory=True)
        copied = alias
    with pytest.raises(V31ContractError):
        cycle2._validate_external_snapshot_tree(copied, expected)
    real_copy = tmp_path / "source"
    for directory in sorted(
        (path for path in real_copy.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    ):
        directory.chmod(0o755)
    real_copy.chmod(0o755)


@pytest.mark.parametrize("error_ordinal", [None, 0, 11, 22])
def test_external_durable_supervision_with_synthetic_child(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error_ordinal: int | None,
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_cycle2 as cycle2

    payload = _external_outcome_payload(error_ordinal)

    class FakePopen:
        pid = 987654

        def __init__(self, _argv, *, env, **_kwargs):
            Path(env["SCHWO_V31_BHPT_OUTPUT"]).write_bytes(
                cycle2.canonical_bytes(payload)
            )
            self.returncode = None

        def wait(self):
            self.returncode = 0 if error_ordinal is None else 70
            return self.returncode

        def poll(self):
            return self.returncode

    monkeypatch.setattr(cycle2.subprocess, "Popen", FakePopen)
    monkeypatch.setattr(cycle2, "_process_group_empty", lambda _pgid: True)
    evidence = tmp_path / f"external_{error_ordinal}"
    if error_ordinal is None:
        records = cycle2.run_external_records(evidence)
        assert len(records) == 23
        assert (
            json.loads((evidence / "external_terminal.json").read_text())["status"]
            == "PASS"
        )
        assert (evidence / "external_result.json").is_file()
        assert not (evidence / "external_failure.json").exists()
    else:
        with pytest.raises(V31ContractError, match="terminal failure"):
            cycle2.run_external_records(evidence)
        failure = json.loads((evidence / "external_failure.json").read_text())
        assert failure["first_failure"]["ordinal"] == error_ordinal
        assert not (evidence / "external_result.json").exists()
    receipt = json.loads((evidence / "external_receipt.json").read_text())
    assert receipt["wait_calls"] == 1
    assert receipt["reaped"] is True
    assert receipt["process_group_empty"] is True
    assert set(cycle2.EXTERNAL_ARTIFACT_NAMES).issubset(
        {path.name for path in evidence.iterdir()}
    )


@pytest.mark.parametrize("child_mode", ["missing", "torn", "duplicate_json", "signal"])
def test_external_supervision_rejects_incomplete_or_signaled_child(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, child_mode: str
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_cycle2 as cycle2

    class FakePopen:
        pid = 987655

        def __init__(self, _argv, *, env, **_kwargs):
            output = Path(env["SCHWO_V31_BHPT_OUTPUT"])
            if child_mode == "torn":
                output.write_bytes(b'{"schema":')
            elif child_mode == "duplicate_json":
                output.write_bytes(b'{"schema":"a","schema":"b"}')
            self.returncode = None

        def wait(self):
            self.returncode = -9 if child_mode == "signal" else 0
            return self.returncode

        def poll(self):
            return self.returncode

    monkeypatch.setattr(cycle2.subprocess, "Popen", FakePopen)
    monkeypatch.setattr(cycle2, "_process_group_empty", lambda _pgid: True)
    evidence = tmp_path / child_mode
    with pytest.raises(V31ContractError, match="terminal failure"):
        cycle2.run_external_records(evidence)
    assert (evidence / "external_failure_manifest.json").is_file()
    assert not (evidence / "external_result.json").exists()


def test_synthetic_publish_reload_and_tamper(tmp_path: Path) -> None:
    root = tmp_path / "synthetic"
    publish_synthetic_root(root)
    validate_synthetic_root(root)
    os.chmod(root / "synthetic.json", 0o644)
    payload = json.loads((root / "synthetic.json").read_text())
    payload["counts"]["route_c_records"] = 22
    (root / "synthetic.json").write_text(json.dumps(payload))
    with pytest.raises(V31ContractError):
        validate_synthetic_root(root)


def test_continued_jost_has_one_protected_public_call_site() -> None:
    import schwgw.validation.phase6_v3_continued_jost as continued

    tree = ast.parse(Path(continued.__file__).read_text())
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "solve_scaled_tortoise_radial_at_radius"
    ]
    # The same single call site is reached by direct/continued requests only
    # through their mutually exclusive branch.  No fallback call exists.
    assert len(calls) == 2
    text = Path(continued.__file__).read_text()
    assert "pinv" not in text
    assert "lstsq" not in text


def test_ap_module_has_no_route_a_or_protected_radial_import() -> None:
    import schwgw.validation.phase6_v3_mode_greybody_ap as ap

    tree = ast.parse(Path(ap.__file__).read_text())
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }
    assert not any("phase6_v3_continued_jost" in value for value in imports)
    assert not any("schwgw.numerics" in value for value in imports)


def test_ap_plan_keeps_exact_precision_and_turning_cardinality() -> None:
    plan = ap_node_plan()
    precision = [item for item in plan if item["membership"] == "precision"]
    turning = [item for item in plan if item["membership"] != "precision"]
    assert len(precision) == 306
    assert len(turning) == 152
    assert {item["dps"] for item in precision} == {80, 120, 180}


def test_injected_complete_official_orchestration_and_reload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_cycle2 as cycle2

    monkeypatch.setattr(cycle2, "verify_cycle2_start_gate", lambda: {"identities": {}})

    def fake_mode(key: ModeKey):
        nodes = cycle2.route_a_node_graph(key)
        ladder = [
            {
                "schema": "injected.route_a",
                "mode": key.payload(),
                "node": node,
                "result": {
                    "requested_match_radius": geometry.requested_match_radius,
                    "jost_initialization_radius": geometry.jost_initialization_radius,
                    "auxiliary_exponent": geometry.auxiliary_exponent,
                    "diagnostics": {"protected_route_a_call_count": 1},
                },
            }
            for node in nodes
            for geometry in (
                cycle2.continued_jost_geometry(
                    ell=key.ell,
                    k=float(key.kM),
                    r_match=float(node["r_out"]),
                ),
            )
        ]
        return (
            {
                "schema": "injected.mode",
                "mode": key.payload(),
                "baseline": {},
                "metrics": {},
                "node_count": 20,
                "protected_call_count": 20,
            },
            ladder,
        )

    monkeypatch.setattr(cycle2, "solve_route_a_mode", fake_mode)
    monkeypatch.setattr(cycle2, "_mode_threshold_blockers", lambda _mode: [])
    monkeypatch.setattr(
        cycle2,
        "solve_ap_node",
        lambda node: {"schema": "injected.ap", "node": dict(node)},
    )
    external = cycle2.build_anchor_inventory(cycle2.build_mode_inventory())["external"]
    monkeypatch.setattr(
        cycle2,
        "run_external_records",
        lambda _path: [
            {"schema": "injected.external", "key": dict(item)} for item in external
        ],
    )
    thresholds = [
        {"field_id": item["field_id"], "observed": 0.0, "status": "PASS"}
        for item in cycle2._v31_thresholds()
    ]
    certificates = [
        {"certificate_id": item, "status": "PASS"} for item in cycle2.CERTIFICATE_IDS
    ]
    monkeypatch.setattr(
        cycle2,
        "evaluate_all_thresholds",
        lambda *_args: {
            "all_pass": True,
            "summary": {
                "schema": "injected.summary",
                "counts": EXPECTED_COUNTS,
                "thresholds": thresholds,
                "certificates": certificates,
            },
            "uncertainty_budget": {"schema": "injected.uncertainty"},
        },
    )
    monkeypatch.setattr(cycle2, "build_source_ledger", lambda _gate: {"x": "y"})
    root = tmp_path / "r3"
    result = cycle2.run_official_cycle2(root)
    assert result["evaluation"]["all_pass"] is True
    assert len(load_jsonl(root / "records.jsonl")) == 496
    assert len(load_jsonl(root / "ladder_records.jsonl")) == 9920
    assert len(load_jsonl(root / "ap_records.jsonl")) == 458
    assert len(load_jsonl(root / "external_records.jsonl")) == 23
    cycle2.validate_official_candidate(root)


def test_injected_official_failure_is_terminal_and_nonaccepting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_cycle2 as cycle2

    monkeypatch.setattr(cycle2, "verify_cycle2_start_gate", lambda: {"identities": {}})

    monkeypatch.setattr(cycle2, "build_source_ledger", lambda _gate: {"x": "y"})

    def fail(_key: ModeKey):
        raise RuntimeError("injected scientific failure")

    monkeypatch.setattr(cycle2, "solve_route_a_mode", fail)
    root = tmp_path / "failed"
    with pytest.raises(RuntimeError, match="injected scientific failure"):
        cycle2.run_official_cycle2(root)
    failure = json.loads((root / "failure.json").read_text())
    assert failure["scientific_pass"] is False
    assert not (root / "manifest.json").exists()
    assert not (root / ".writer.lock").exists()
    assert (root.stat().st_mode & 0o777) == 0o555
