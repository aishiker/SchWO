from __future__ import annotations

import json
import os
from pathlib import Path
import runpy
import stat

import pytest


SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "scripts/phase6_mpmath_radial_selected_anchors.py"
)


@pytest.fixture(scope="module")
def runner() -> dict[str, object]:
    return runpy.run_path(str(SCRIPT))


def _make_mode_tree(runner: dict[str, object], root: Path) -> Path:
    checkpoint_root = root / "mode_checkpoints"
    checkpoint_root.mkdir(parents=True)
    for mode in runner["selected_stage_a_modes"]():
        (checkpoint_root / mode.mode_id).mkdir()
    return checkpoint_root


def _failure(stage: str = "fault_injection") -> dict[str, str]:
    return {
        "stage": stage,
        "exception_type": "InjectedFailure",
        "message": "deliberate zero-science test failure",
    }


def _publish_batch_prefix(
    runner: dict[str, object],
    mode_root: Path,
    *,
    count: int,
) -> list[dict[str, object]]:
    publish = runner["_publish_json"]
    for label in runner["EXPECTED_BATCH_LABELS"][:count]:
        publish(
            mode_root / f"{label}.json",
            {
                "schema_version": "schwgw_phase6_mpmath_mode_checkpoint_v1",
                "label": label,
                "status": "PASS",
                "failure": None,
                "batch": {},
            },
        )
    return runner["_checkpoint_prefix"](mode_root)


def _restore_test_tree_permissions(root: Path) -> None:
    if not root.exists():
        return
    for path in sorted(root.rglob("*"), reverse=True):
        if path.is_dir() and not path.is_symlink():
            os.chmod(path, 0o700)
        elif path.is_file() and not path.is_symlink():
            os.chmod(path, 0o600)
    os.chmod(root, 0o700)


def test_completed_mode_terminal_is_exclusive_and_reload_bound(
    runner: dict[str, object], tmp_path: Path
) -> None:
    checkpoint_root = _make_mode_tree(runner, tmp_path)
    mode = runner["selected_stage_a_modes"]()[0]
    mode_root = checkpoint_root / mode.mode_id
    identities = _publish_batch_prefix(
        runner,
        mode_root,
        count=len(runner["EXPECTED_BATCH_LABELS"]),
    )
    evidence = {
        "mode": mode.to_metadata(),
        "status": "FAIL_CLOSED_NUMERICAL_INSTABILITY",
        "checkpoint_identities": identities,
    }
    terminal_identity = runner["_publish_mode_terminal"](
        mode_index=0,
        mode=mode,
        mode_root=mode_root,
        execution_status="COMPLETED",
        mode_evidence=evidence,
        failure=None,
    )
    before = (mode_root / "terminal.json").read_bytes()
    assert terminal_identity["nlink"] == 1
    assert terminal_identity["mode"] == 0o444
    assert not list(mode_root.glob(".*o_excl_staging*"))

    with pytest.raises(FileExistsError, match="output collision"):
        runner["_publish_mode_terminal"](
            mode_index=0,
            mode=mode,
            mode_root=mode_root,
            execution_status="COMPLETED",
            mode_evidence=evidence,
            failure=None,
        )
    assert (mode_root / "terminal.json").read_bytes() == before


def test_atomic_terminal_publish_cleans_staging_on_link_failure(
    runner: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    target = tmp_path / "terminal.json"

    def fail_link(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise OSError("injected atomic-link failure")

    monkeypatch.setattr(os, "link", fail_link)
    with pytest.raises(OSError, match="atomic-link failure"):
        runner["_publish_terminal_json"](target, {"status": "terminal"})
    assert not target.exists()
    assert list(tmp_path.iterdir()) == []


def test_terminal_reload_enforces_exact_mode_order_cardinality_and_schema(
    runner: dict[str, object], tmp_path: Path
) -> None:
    modes = runner["selected_stage_a_modes"]()

    valid_root = _make_mode_tree(runner, tmp_path / "valid")
    for index, mode in enumerate(modes):
        runner["_publish_mode_terminal"](
            mode_index=index,
            mode=mode,
            mode_root=valid_root / mode.mode_id,
            execution_status="NOT_STARTED_DUE_TO_RUN_FAILURE",
            mode_evidence=None,
            failure=_failure(),
        )
    records, identities = runner["_reload_mode_terminals"](
        valid_root,
        require_all_completed=False,
    )
    assert records == []
    assert len(identities) == len(modes)

    wrong_order_root = _make_mode_tree(runner, tmp_path / "wrong_order")
    for index, mode in enumerate(modes):
        payload = runner["_mode_terminal_payload"](
            mode_index=(1 if index == 0 else index),
            mode=mode,
            execution_status="NOT_STARTED_DUE_TO_RUN_FAILURE",
            checkpoint_identities=[],
            mode_evidence=None,
            failure=_failure(),
        )
        runner["_publish_json"](
            wrong_order_root / mode.mode_id / "terminal.json", payload
        )
    with pytest.raises(RuntimeError, match="order/key binding"):
        runner["_reload_mode_terminals"](
            wrong_order_root,
            require_all_completed=False,
        )

    wrong_schema_root = _make_mode_tree(runner, tmp_path / "wrong_schema")
    for index, mode in enumerate(modes):
        payload = runner["_mode_terminal_payload"](
            mode_index=index,
            mode=mode,
            execution_status="NOT_STARTED_DUE_TO_RUN_FAILURE",
            checkpoint_identities=[],
            mode_evidence=None,
            failure=_failure(),
        )
        if index == 0:
            payload["unexpected"] = True
        runner["_publish_json"](
            wrong_schema_root / mode.mode_id / "terminal.json", payload
        )
    with pytest.raises(RuntimeError, match="exact schema"):
        runner["_reload_mode_terminals"](
            wrong_schema_root,
            require_all_completed=False,
        )

    (valid_root / "foreign_mode").mkdir()
    with pytest.raises(RuntimeError, match="cardinality/key"):
        runner["_reload_mode_terminals"](
            valid_root,
            require_all_completed=False,
        )


def test_all_completed_terminals_reload_in_frozen_mode_order(
    runner: dict[str, object], tmp_path: Path
) -> None:
    checkpoint_root = _make_mode_tree(runner, tmp_path)
    expected_records = []
    for index, mode in enumerate(runner["selected_stage_a_modes"]()):
        mode_root = checkpoint_root / mode.mode_id
        identities = _publish_batch_prefix(
            runner,
            mode_root,
            count=len(runner["EXPECTED_BATCH_LABELS"]),
        )
        record = {
            "mode": mode.to_metadata(),
            "status": "FAIL_CLOSED_NUMERICAL_INSTABILITY",
            "checkpoint_identities": identities,
        }
        expected_records.append(record)
        runner["_publish_mode_terminal"](
            mode_index=index,
            mode=mode,
            mode_root=mode_root,
            execution_status="COMPLETED",
            mode_evidence=record,
            failure=None,
        )

    records, identities = runner["_reload_mode_terminals"](
        checkpoint_root,
        require_all_completed=True,
    )
    assert records == expected_records
    assert [record["mode"] for record in records] == [
        mode.to_metadata() for mode in runner["selected_stage_a_modes"]()
    ]
    assert len(identities) == 8


def test_checkpoint_reload_rejects_gaps_and_identity_reordering(
    runner: dict[str, object], tmp_path: Path
) -> None:
    checkpoint_root = _make_mode_tree(runner, tmp_path)
    mode = runner["selected_stage_a_modes"]()[0]
    mode_root = checkpoint_root / mode.mode_id
    second_label = runner["EXPECTED_BATCH_LABELS"][1]
    runner["_publish_json"](
        mode_root / f"{second_label}.json",
        {
            "schema_version": "schwgw_phase6_mpmath_mode_checkpoint_v1",
            "label": second_label,
            "status": "PASS",
            "failure": None,
            "batch": {},
        },
    )
    with pytest.raises(RuntimeError, match="ordered prefix"):
        runner["_checkpoint_prefix"](mode_root)

    ordered_root = _make_mode_tree(runner, tmp_path / "ordered")
    ordered_mode_root = ordered_root / mode.mode_id
    identities = _publish_batch_prefix(
        runner,
        ordered_mode_root,
        count=len(runner["EXPECTED_BATCH_LABELS"]),
    )
    evidence = {
        "mode": mode.to_metadata(),
        "status": "FAIL_CLOSED_NUMERICAL_INSTABILITY",
        "checkpoint_identities": identities,
    }
    payload = runner["_mode_terminal_payload"](
        mode_index=0,
        mode=mode,
        execution_status="COMPLETED",
        checkpoint_identities=[identities[1], identities[0], *identities[2:]],
        mode_evidence=evidence,
        failure=None,
    )
    runner["_publish_json"](ordered_mode_root / "terminal.json", payload)
    with pytest.raises(RuntimeError, match="identity/order"):
        runner["_validate_mode_terminal"](
            payload,
            mode_index=0,
            mode=mode,
            mode_root=ordered_mode_root,
        )


def test_canonical_reload_rejects_duplicate_keys_and_noncanonical_bytes(
    runner: dict[str, object], tmp_path: Path
) -> None:
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_bytes(b'{"a":1,"a":2}\n')
    with pytest.raises(RuntimeError, match="duplicate JSON key"):
        runner["_reload_canonical_json"](duplicate)

    noncanonical = tmp_path / "noncanonical.json"
    noncanonical.write_text(json.dumps({"b": 2, "a": 1}), encoding="utf-8")
    with pytest.raises(RuntimeError, match="not canonical"):
        runner["_reload_canonical_json"](noncanonical)


def test_fault_injection_publishes_all_mode_terminals_and_top_failure(
    runner: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    validation_root = (tmp_path / "radial_validation").resolve()
    validation_root.mkdir()
    output_root = validation_root / "fresh_fault_injection"
    bhpt = tmp_path / "bhpt.json"
    bhpt.write_text('{"records":[]}\n', encoding="utf-8")
    run = runner["run"]
    globals_ = run.__globals__
    monkeypatch.setitem(globals_, "RADIAL_VALIDATION_ROOT", validation_root)
    monkeypatch.setitem(globals_, "BHPT_EVIDENCE", bhpt)
    monkeypatch.setitem(globals_, "_runtime_identity", lambda _: {})
    monkeypatch.setitem(
        globals_,
        "prove_call_graph_isolation",
        lambda _: {"isolation_passed": True},
    )
    call_count = 0

    def injected_mode_evidence(mode, mode_root, bhpt_records):
        nonlocal call_count
        del bhpt_records
        call_count += 1
        if call_count == 1:
            identities = _publish_batch_prefix(
                runner,
                mode_root,
                count=len(runner["EXPECTED_BATCH_LABELS"]),
            )
            record = {
                "mode": mode.to_metadata(),
                "status": "FAIL_CLOSED_NUMERICAL_INSTABILITY",
                "checkpoint_identities": identities,
            }
            return record, identities
        raise RuntimeError("injected failure before any scientific solver call")

    monkeypatch.setitem(globals_, "_mode_evidence", injected_mode_evidence)
    try:
        with pytest.raises(RuntimeError, match="durable failure artifact"):
            run(output_root)
        assert call_count == 2
        failure = runner["_reload_canonical_json"](output_root / "failure.json")
        assert failure["schema_version"] == runner["RUN_FAILURE_SCHEMA"]
        assert failure["terminal_protocol_complete"] is True
        assert failure["mode_execution_status_counts"] == {
            "COMPLETED": 1,
            "EXECUTION_FAILED": 1,
            "NOT_STARTED_DUE_TO_RUN_FAILURE": 6,
        }
        assert failure["published_success_artifacts"] == {
            "selected_anchor_evidence.json": False,
            "manifest.json": False,
            "checkpoint.json": False,
        }
        assert len(failure["mode_terminal_identities"]) == 8
        modes, terminal_identities = runner["_reload_mode_terminals"](
            output_root / "mode_checkpoints",
            require_all_completed=False,
        )
        assert len(modes) == 1
        assert len(terminal_identities) == 8
        assert stat.S_IMODE(output_root.stat().st_mode) == 0o555
    finally:
        _restore_test_tree_permissions(output_root)


def test_failure_artifact_and_terminal_are_never_overwritten(
    runner: dict[str, object], tmp_path: Path
) -> None:
    output_root = tmp_path.resolve()
    checkpoint_root = _make_mode_tree(runner, output_root)
    exc = RuntimeError("first failure")
    identity = runner["_publish_run_failure"](
        output_root,
        stage="setup",
        active_mode_id=None,
        exc=exc,
    )
    before = (output_root / "failure.json").read_bytes()
    assert identity["mode"] == 0o444
    with pytest.raises(FileExistsError, match="output collision"):
        runner["_publish_run_failure"](
            output_root,
            stage="second_attempt",
            active_mode_id=None,
            exc=RuntimeError("must not replace"),
        )
    assert (output_root / "failure.json").read_bytes() == before
    assert len(list(checkpoint_root.glob("*/terminal.json"))) == 8
