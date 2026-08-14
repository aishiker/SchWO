from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement
from schwgw.validation.phase6_v3_mode_greybody import (
    ModeKey,
    build_anchor_inventory,
    build_mode_inventory,
)
from schwgw.validation.phase6_v3_mode_greybody_hp_replacement import (
    EXPECTED_FIXED_COUNTS,
    run_official,
    validate_official_candidate,
)


def _fake_mode(key: ModeKey):
    baseline = {
        "Gamma_flux": 0.01,
        "Gamma_S": 0.01,
        "Gamma_flux_decimal": {"exponent10": -2, "mantissa": "1.0"},
        "log_Gamma_flux": "-4.605170185988091368",
    }
    mode = {
        "schema": "injected.route_a_mode",
        "mode": key.payload(),
        "baseline": baseline,
        "metrics": {},
        "node_count": 20,
        "protected_call_count": 20,
    }
    ladder = [
        {
            "schema": "injected.route_a_node",
            "mode": key.payload(),
            "node": {"node_ordinal": index},
            "result": {},
        }
        for index in range(20)
    ]
    return mode, ladder


def _evaluation() -> dict[str, object]:
    import schwgw.validation.phase6_v3_mode_greybody_cycle2 as cycle2

    thresholds = [
        {
            "field_id": item["field_id"],
            "observed": 0.0,
            "limit": float(item["value"]),
            "status": "PASS",
        }
        for item in cycle2._v31_thresholds()
    ]
    certificates = [
        {"certificate_id": item, "status": "PASS"} for item in cycle2.CERTIFICATE_IDS
    ]
    counts = {**EXPECTED_FIXED_COUNTS, "route_u_keys": 0, "route_u_nodes": 0}
    return {
        "all_pass": True,
        "thresholds": thresholds,
        "summary": {
            "schema": "schwo.phase6.v3_1_u.summary.v1",
            "gate_id": "phase6_v3_1_hp_unitarity_deficit_replacement_v1",
            "overall_state": "PASS",
            "counts": counts,
            "thresholds": thresholds,
            "certificates": certificates,
            "route_u_count_data_derived": 0,
            "global_status": None,
            "global_green_permitted": False,
            "independent_review_state": "NOT_ASSESSED",
        },
        "uncertainty_budget": {"schema": "injected.uncertainty"},
    }


def _inject(monkeypatch: pytest.MonkeyPatch) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    monkeypatch.setattr(
        replacement, "verify_start_gate", lambda: {"package": {}, "identities": {}}
    )
    monkeypatch.setattr(
        replacement, "build_source_ledger", lambda _gate: {"source": "fixed"}
    )
    monkeypatch.setattr(
        replacement, "_validate_official_root_path", lambda root: root.resolve()
    )
    environment_authority = replacement._load_sentinel_environment_authority()
    environment_identity = {
        "path": str(replacement.SENTINEL_ENVIRONMENT_AUTHORITY_PATH),
        "identity": replacement._file_identity(
            replacement.SENTINEL_ENVIRONMENT_AUTHORITY_PATH
        ),
    }
    monkeypatch.setattr(
        replacement,
        "_validate_dispatch",
        lambda _root, _gate: {
            "dispatch": {"sha256": "a" * 64, "size": 1, "mode": 0o444, "nlink": 1},
            "dispatch_payload_sha256": "b" * 64,
            "implementation_review": {
                "sha256": "c" * 64,
                "size": 1,
                "mode": 0o444,
                "nlink": 1,
            },
            "implementation_hashes": {"injected": "d" * 64},
            "environment_authority": environment_identity,
            "requested_environment": environment_authority["requested_environment"][
                "exact_execve_map"
            ],
            "observed_environment": environment_authority["observed_environment"][
                "exact_post_startup_map"
            ],
            "sentinel_review": {
                "sha256": "e" * 64,
                "size": 1,
                "mode": 0o444,
                "nlink": 1,
            },
            "sentinel_terminal": {"injected": True},
        },
    )
    monkeypatch.setattr(replacement.cycle2, "solve_route_a_mode", _fake_mode)
    monkeypatch.setattr(
        replacement.cycle2,
        "solve_ap_node",
        lambda node: {"schema": "injected.ap", "node": dict(node)},
    )
    anchors = build_anchor_inventory(build_mode_inventory())["external"]

    def fake_external(path: Path):
        path.mkdir()
        for name, payload in (
            ("external_terminal.json", {"status": "PASS", "outcome_count": 23}),
            ("external_result.json", {"status": "PASS", "record_count": 23}),
        ):
            target = path / name
            target.write_bytes(replacement.canonical_bytes(payload))
        return [{"schema": "injected.external", "key": dict(item)} for item in anchors]

    monkeypatch.setattr(replacement.cycle2, "run_external_records", fake_external)
    monkeypatch.setattr(
        replacement, "evaluate_all_thresholds", lambda *_args: _evaluation()
    )


def test_injected_full_publication_reload_and_tamper(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _inject(monkeypatch)
    root = tmp_path / "v3_1_u"
    result = run_official(root)
    assert result["evaluation"]["all_pass"] is True
    consumption = json.loads((root / "dispatch_consumption.json").read_text())
    assert consumption["science_calls_before_consumption"] == 0
    authority = replacement._load_sentinel_environment_authority()
    assert consumption["environment_authority"] == {
        "path": str(replacement.SENTINEL_ENVIRONMENT_AUTHORITY_PATH),
        "identity": replacement._file_identity(
            replacement.SENTINEL_ENVIRONMENT_AUTHORITY_PATH
        ),
    }
    assert (
        consumption["requested_environment"]
        == authority["requested_environment"]["exact_execve_map"]
    )
    assert (
        consumption["observed_environment"]
        == authority["observed_environment"]["exact_post_startup_map"]
    )
    assert (
        json.loads((root / "unitarity_route_map.json").read_text())["route_u_count"]
        == 0
    )
    assert (
        len(
            (root / "mode_checkpoints")
            .glob("route_a_*.json")
            .__iter__()
            .__next__()
            .name
        )
        > 0
    )
    validate_official_candidate(root)
    os.chmod(root, 0o755)
    os.chmod(root / "summary.json", 0o644)
    (root / "summary.json").write_text("{}\n")
    with pytest.raises(Exception):
        validate_official_candidate(root)


def test_official_failure_terminalizes_without_acceptance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _inject(monkeypatch)
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    def fail(_key: ModeKey):
        raise RuntimeError("injected science failure")

    monkeypatch.setattr(replacement.cycle2, "solve_route_a_mode", fail)
    root = tmp_path / "failed"
    with pytest.raises(RuntimeError, match="injected science failure"):
        run_official(root)
    assert (root / "failure.json").is_file()
    assert (root / "failure_manifest.json").is_file()
    assert not (root / "manifest.json").exists()
    assert not (root / ".writer.lock").exists()
    failure = json.loads((root / "failure.json").read_text())
    assert failure["scientific_pass"] is False
    assert failure["resumable"] is False
    assert stat_mode(root) == 0o555


def test_missing_dispatch_fails_before_root_and_science(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    calls = {"science": 0}

    def forbidden(_key: ModeKey):
        calls["science"] += 1
        raise AssertionError("science started before dispatch consumption")

    monkeypatch.setattr(
        replacement,
        "verify_start_gate",
        lambda: {
            "repair2_package": json.loads(replacement.REPAIR2_PACKAGE_PATH.read_text()),
            "identities": {},
        },
    )
    monkeypatch.setattr(replacement.cycle2, "solve_route_a_mode", forbidden)
    monkeypatch.setattr(replacement, "DISPATCH_PATH", tmp_path / "absent.json")
    parent = tmp_path / "classic_scattering"
    parent.mkdir()
    monkeypatch.setattr(replacement, "OFFICIAL_ROOT_PARENT", parent)
    root = parent / "v3_1_hp_unitarity_deficit_repair2_v1_20260813T100000Z_py314"
    with pytest.raises(FileNotFoundError):
        run_official(root)
    assert not root.exists()
    assert calls == {"science": 0}


def test_nonnamespace_root_fails_before_start_gate_and_science(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    calls = {"start_gate": 0, "science": 0}

    def forbidden_start_gate():
        calls["start_gate"] += 1
        raise AssertionError("start gate reached for nonnamespace root")

    def forbidden_science(_key: ModeKey):
        calls["science"] += 1
        raise AssertionError("science reached for nonnamespace root")

    parent = tmp_path / "classic_scattering"
    parent.mkdir()
    monkeypatch.setattr(replacement, "OFFICIAL_ROOT_PARENT", parent)
    monkeypatch.setattr(replacement, "verify_start_gate", forbidden_start_gate)
    monkeypatch.setattr(replacement.cycle2, "solve_route_a_mode", forbidden_science)
    root = parent / "wrong-name"
    with pytest.raises(Exception, match="namespace"):
        run_official(root)
    assert not root.exists()
    assert calls == {"start_gate": 0, "science": 0}


def test_cli_preflight_gate_is_independent_of_absent_future_review(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    future_review = tmp_path / "future_delta_recheck.md"
    assert not future_review.exists()
    monkeypatch.setattr(replacement, "IMPLEMENTATION_REVIEW_PATH", future_review)
    gate = replacement.verify_start_gate()
    assert len(gate["identities"]) == 70
    assert str(replacement.SENTINEL_ENVIRONMENT_AUTHORITY_PATH) in gate["identities"]
    assert gate["geometry_preflight"]["science_solver_calls"] == 0


def stat_mode(path: Path) -> int:
    return path.stat().st_mode & 0o777


def test_sentinel_dispatch_one_use_authority_and_no_science(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    package = json.loads(replacement.REPAIR2_PACKAGE_PATH.read_text())
    parent = tmp_path / "classic_scattering"
    parent.mkdir()
    root = parent / "v3_1_u_route_c_sentinel_repair2_v1_20260813T090000Z_py314"
    review = tmp_path / "implementation_review.md"
    hashes = {
        str(replacement.ROOT / path): replacement.sha256(replacement.ROOT / path)
        for path in replacement.ALLOWED_IMPLEMENTATION_PATHS
    }
    review.write_text(
        "\n".join((*replacement.IMPLEMENTATION_REVIEW_TOKENS, *hashes.values())) + "\n"
    )
    dispatch = tmp_path / "sentinel_dispatch.json"
    payload = {
        "schema": "schwo.phase6.v3_1_u.route_c_sentinel_dispatch.v1",
        "gate_id": replacement.GATE_ID,
        "repair_id": package["repair_id"],
        "exact_root": str(root),
        "single_use": True,
        "created_at_utc": "2026-08-13T09:00:00Z",
        "repair_package": {
            "path": str(replacement.REPAIR2_PACKAGE_PATH),
            "sha256": replacement.REPAIR2_PACKAGE_SHA256,
        },
        "package_review": {
            "path": str(replacement.REPAIR2_PACKAGE_REVIEW_PATH),
            "sha256": replacement.REPAIR2_PACKAGE_REVIEW_SHA256,
        },
        "implementation_review": {
            "path": str(review),
            "sha256": replacement.sha256(review),
        },
        "implementation_hashes": hashes,
        "environment_authority": replacement._sentinel_environment_authority_binding(),
        "sentinel_invocation": replacement.SENTINEL_INVOCATION,
        "anchors": build_anchor_inventory(build_mode_inventory())["external"],
        "method_contract": package["external_runtime"]["method_contract"],
        "snapshot": package["external_runtime"]["bhpt_snapshot"],
        "wolfram_kernel": package["external_runtime"]["wolfram_kernel"],
        "protected_radial_identities": package["protected_radial_identities"],
        "source_bindings": package["source_bindings"],
        "required_verdict_tokens": list(replacement.IMPLEMENTATION_REVIEW_TOKENS),
    }
    dispatch.write_bytes(replacement.canonical_bytes(payload))
    dispatch.chmod(0o444)
    monkeypatch.setattr(replacement, "OFFICIAL_ROOT_PARENT", parent)
    monkeypatch.setattr(replacement, "IMPLEMENTATION_REVIEW_PATH", review)
    monkeypatch.setattr(replacement, "SENTINEL_DISPATCH_PATH", dispatch)
    validated = replacement._validate_sentinel_dispatch({"repair2_package": package})
    assert validated["root"] == root
    assert not root.exists()
    payload["environment_authority"] = {
        "path": str(replacement.SENTINEL_ENVIRONMENT_AUTHORITY_PATH),
        "sha256": "0" * 64,
    }
    dispatch.chmod(0o644)
    dispatch.write_bytes(replacement.canonical_bytes(payload))
    dispatch.chmod(0o444)
    with pytest.raises(Exception):
        replacement._validate_sentinel_dispatch({"repair2_package": package})
    payload["environment_authority"] = (
        replacement._sentinel_environment_authority_binding()
    )
    payload["exact_root"] = str(parent / "wrong")
    dispatch.chmod(0o644)
    dispatch.write_bytes(replacement.canonical_bytes(payload))
    dispatch.chmod(0o444)
    with pytest.raises(Exception):
        replacement._validate_sentinel_dispatch({"repair2_package": package})


def test_official_route_c_recomputes_and_never_reads_sentinel_science() -> None:
    import ast
    import inspect
    import schwgw.validation.phase6_v3_mode_greybody_hp_replacement as replacement

    source = inspect.getsource(replacement.run_official)
    tree = ast.parse(source)
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "run_external_records"
    ]
    assert len(calls) == 1
    assert 'sentinel_science_reused": False' in source
    assert "sentinel_records" not in source
