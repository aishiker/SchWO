from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

import schwgw.validation.phase6_v3_hp_unitarity_resume as resume
from schwgw.validation.phase6_v3_mode_greybody import build_mode_inventory
from schwgw.validation import phase6_v3_mode_greybody_cycle2 as cycle2


def _copy_actual_prefix(destination: Path) -> Path:
    source = resume.REAL_ROOT
    destination.mkdir()
    for name in (
        ".writer.lock",
        "inventory.json",
        "run_contract.json",
        "source_start.json",
        "records.jsonl",
        "ladder_records.jsonl",
    ):
        shutil.copyfile(source / name, destination / name)
        shutil.copymode(source / name, destination / name)
    shutil.copytree(source / "mode_checkpoints", destination / "mode_checkpoints")
    return destination


def test_actual_prefix_copy_is_read_only_valid_and_compact_checkpoint_bound(
    tmp_path: Path,
) -> None:
    copied = _copy_actual_prefix(tmp_path / "actual-prefix-copy")
    result = resume.inspect_interrupted_root(
        copied, logical_root=resume.REAL_ROOT, check_liveness=False
    )
    prefix = result["prefix"]
    assert prefix["mode_count"] == 435
    assert prefix["ladder_count"] == 8700
    assert prefix["next_ordinal"] == 435
    assert prefix["next_mode"] == {
        "frequency_ordinal": 10,
        "kM": "8",
        "ell": 28,
        "parity": "even",
        "parity_ordinal": 1,
    }
    assert prefix["checkpoint_inventory_sha256"] == resume.CHECKPOINT_INVENTORY_SHA256
    assert result["mutations"] == 0 and result["science_calls"] == 0


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("records_torn", "unauthenticated Route-A records suffix"),
        ("records_duplicate", "unauthenticated Route-A records suffix"),
        ("checkpoint_gap", "checkpoint gap"),
        ("checkpoint_key", "checkpoint"),
        ("source_drift", "source_start"),
        ("early_route_map", "Route-A mode mismatch"),
    ],
)
def test_actual_prefix_copy_corruption_fails_closed(
    tmp_path: Path, mutation: str, message: str
) -> None:
    copied = _copy_actual_prefix(tmp_path / mutation)
    if mutation == "records_torn":
        with (copied / "records.jsonl").open("ab") as stream:
            stream.write(b"{")
    elif mutation == "records_duplicate":
        first = (copied / "records.jsonl").read_bytes().splitlines(keepends=True)[0]
        with (copied / "records.jsonl").open("ab") as stream:
            stream.write(first)
    elif mutation == "checkpoint_gap":
        os.rename(
            copied / "mode_checkpoints/route_a_0434.json",
            copied / "mode_checkpoints/route_a_0436.json",
        )
    elif mutation == "checkpoint_key":
        path = copied / "mode_checkpoints/route_a_0434.json"
        payload = json.loads(path.read_text())
        payload["mode"]["ell"] += 1
        path.chmod(0o600)
        path.write_text(json.dumps(payload))
    elif mutation == "source_drift":
        path = copied / "source_start.json"
        path.chmod(0o600)
        path.write_bytes(path.read_bytes() + b" ")
    elif mutation == "early_route_map":
        # A completed extra science record without resume_control authority is illegal.
        records = copied / "records.jsonl"
        ladders = copied / "ladder_records.jsonl"
        records.chmod(0o600)
        ladders.chmod(0o600)
        with records.open("ab") as stream:
            stream.write(records.read_bytes().splitlines(keepends=True)[-1])
        last_twenty = ladders.read_bytes().splitlines(keepends=True)[-20:]
        with ladders.open("ab") as stream:
            stream.writelines(last_twenty)
        shutil.copyfile(
            copied / "mode_checkpoints/route_a_0434.json",
            copied / "mode_checkpoints/route_a_0435.json",
        )
    with pytest.raises(resume.ResumeContractError, match=message):
        resume.inspect_interrupted_root(
            copied, logical_root=resume.REAL_ROOT, check_liveness=False
        )


def test_real_root_start_end_identity_is_unchanged_and_has_no_writer() -> None:
    root = resume.REAL_ROOT
    before = {
        name: (
            hashlib.sha256((root / name).read_bytes()).hexdigest(),
            (root / name).stat().st_size,
            (root / name).stat().st_ino,
        )
        for name in (
            ".writer.lock",
            "records.jsonl",
            "ladder_records.jsonl",
            "run_contract.json",
            "source_start.json",
            "inventory.json",
        )
    }
    result = resume.inspect_interrupted_root(root)
    after = {
        name: (
            hashlib.sha256((root / name).read_bytes()).hexdigest(),
            (root / name).stat().st_size,
            (root / name).stat().st_ino,
        )
        for name in before
    }
    assert before == after
    assert result["liveness"]["active_writer"] is False
    assert not (root / "resume_control").exists()


@pytest.mark.parametrize(("mode", "active"), (("rb", False), ("r+b", True)))
def test_liveness_excludes_read_only_observer_but_detects_writable_fd(
    tmp_path: Path, mode: str, active: bool
) -> None:
    root = tmp_path / "liveness-root"
    root.mkdir()
    for name in (".writer.lock", "records.jsonl", "ladder_records.jsonl"):
        (root / name).write_bytes(b"")
    child = subprocess.Popen(
        [
            sys.executable,
            "-c",
            (
                "import sys; f=open(sys.argv[1],sys.argv[2]); "
                "print('READY',flush=True); sys.stdin.readline(); f.close()"
            ),
            str(root / "records.jsonl"),
            mode,
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert child.stdout is not None and child.stdout.readline().strip() == "READY"
        result = resume._process_liveness(root)
        assert result["active_writer"] is active
        assert (child.pid in result["other_open_writer_pids"]) is active
        assert result["read_only_observers_excluded"] is True
    finally:
        assert child.stdin is not None
        child.stdin.write("\n")
        child.stdin.flush()
        child.wait(timeout=5)


def _authority_files(
    tmp_path: Path, root: Path, *, token: str = ""
) -> resume.Authority:
    hashes = resume.implementation_hashes()
    approval = tmp_path / f"implementation-approval{token}.md"
    approval.write_text(
        "\n".join(
            [
                "ADVANCE_DECISION: ADVANCE",
                "CLAIM_STATUS: NOT_ASSESSED",
                "ACCEPT GREEN / V3.1-U RESUME-CONTROLLER IMPLEMENTATION READY",
                resume.PACKAGE_SHA256,
                *hashes.values(),
            ]
        )
    )
    approval.chmod(0o444)
    approval_sha = hashlib.sha256(approval.read_bytes()).hexdigest()
    dispatch = tmp_path / f"dispatch{token}.json"
    dispatch.write_bytes(
        resume.canonical_bytes(
            resume.build_dispatch_payload(
                root,
                implementation_approval=approval,
                implementation_approval_sha256=approval_sha,
                authorized_at_utc="2026-08-12T00:00:00Z",
                check_liveness=True,
            )
        )
    )
    dispatch.chmod(0o444)
    return resume.Authority(
        approval,
        approval_sha,
        dispatch,
        hashlib.sha256(dispatch.read_bytes()).hexdigest(),
    )


def _set_resume_argv(
    monkeypatch: pytest.MonkeyPatch, root: Path, authority: resume.Authority
) -> None:
    monkeypatch.setattr(
        resume.sys,
        "argv",
        [
            str(resume.CLI_PATH.resolve()),
            "resume",
            "--root",
            str(root.resolve()),
            "--implementation-approval",
            str(authority.implementation_approval.resolve()),
            "--implementation-approval-sha256",
            authority.implementation_approval_sha256,
            "--dispatch",
            str(authority.dispatch.resolve()),
            "--dispatch-sha256",
            authority.dispatch_sha256,
        ],
    )


def test_resume_runtime_rejects_noncanonical_invocation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    copied = _copy_actual_prefix(tmp_path / "runtime-copy")
    authority = _authority_files(tmp_path, copied)
    _set_resume_argv(monkeypatch, copied, authority)
    resume._validate_resume_runtime(copied, authority)
    monkeypatch.setattr(resume.sys, "argv", [*resume.sys.argv, "--extra"])
    with pytest.raises(resume.ResumeContractError, match="runtime/cwd/argv"):
        resume._validate_resume_runtime(copied, authority)


def test_t7_unknown_attempt_control_adversary_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    copied = _copy_actual_prefix(tmp_path / "unknown-control-copy")
    authority = _authority_files(tmp_path, copied)
    _set_resume_argv(monkeypatch, copied, authority)
    inspection = resume.inspect_interrupted_root(
        copied, logical_root=resume.REAL_ROOT, check_liveness=True
    )
    with resume.stable_writer_exclusion(copied) as (_fd, lock_identity):
        attempt, _ = resume._publish_attempt_authority(
            copied, inspection, authority, lock_identity
        )
    (attempt / "unknown_control.json").write_bytes(b"{}\n")
    with pytest.raises(resume.ResumeContractError, match="unknown attempt-level"):
        resume._validate_resume_control_prefix(copied, 435)
    os.unlink(attempt / "unknown_control.json")
    unknown_root_control = copied / "resume_control/unknown_control.json"
    unknown_root_control.write_bytes(b"{}\n")
    with pytest.raises(resume.ResumeContractError, match="unknown resume-control"):
        resume._validate_resume_control_prefix(copied, 435)


def test_t7_rehashed_empty_authority_set_adversary_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    copied = _copy_actual_prefix(tmp_path / "empty-authority-copy")
    authority = _authority_files(tmp_path, copied)
    _set_resume_argv(monkeypatch, copied, authority)
    inspection = resume.inspect_interrupted_root(
        copied, logical_root=resume.REAL_ROOT, check_liveness=True
    )
    with resume.stable_writer_exclusion(copied) as (_fd, lock_identity):
        attempt, _ = resume._publish_attempt_authority(
            copied, inspection, authority, lock_identity
        )
    _replace_authority_files_with_empty_mappings(attempt)
    with pytest.raises(resume.ResumeContractError, match="attempt-intent"):
        resume._validate_resume_control_prefix(copied, 435)


def _fake_route_a(key):
    result = {
        "S": {"real": 0.9, "imag": 0.0},
        "Gamma_flux": 0.01,
        "Gamma_S": 0.01,
        "Gamma_flux_decimal": {"exponent10": -2, "mantissa": "1"},
        "log_Gamma_flux": "-4.605170185988091368",
    }
    ladders = [
        {
            "schema": "injected.route_a_ladder",
            "mode": key.payload(),
            "node": node,
            "result": dict(result),
            "scientific_evidence": False,
        }
        for node in cycle2.route_a_node_graph(key)
    ]
    return (
        {
            "schema": "schwo.phase6.v3_1.route_a_mode_record.v2",
            "mode": key.payload(),
            "baseline": dict(result),
            "metrics": cycle2.route_a_mode_metrics(ladders),
            "node_count": 20,
            "protected_call_count": 20,
        },
        ladders,
    )


def _passing_evaluation() -> dict[str, object]:
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
    counts = {
        **resume.original.EXPECTED_FIXED_COUNTS,
        "route_u_keys": 0,
        "route_u_nodes": 0,
    }
    summary = {
        "schema": "schwo.phase6.v3_1_u.summary.v1",
        "gate_id": resume.original.GATE_ID,
        "overall_state": "PASS",
        "counts": counts,
        "thresholds": thresholds,
        "certificates": certificates,
        "route_u_count_data_derived": 0,
        "global_status": None,
        "global_green_permitted": False,
        "independent_review_state": "NOT_ASSESSED",
    }
    return {
        "all_pass": True,
        "thresholds": thresholds,
        "summary": summary,
        "uncertainty_budget": {"schema": "injected.uncertainty"},
    }


def _rewrite_terminal_manifest(root: Path, *, overall_state: str) -> None:
    filename = "manifest.json" if overall_state == "PASS" else "failure_manifest.json"
    path = root / filename
    path.chmod(0o600)
    path.write_bytes(
        resume.canonical_bytes(
            resume.original.build_manifest(root, overall_state=overall_state)
        )
    )
    path.chmod(0o444)


def _rewrite_authority_commit(attempt: Path) -> None:
    path = attempt / "authority_commit.json"
    path.chmod(0o600)
    path.write_bytes(
        resume.canonical_bytes(
            {
                "schema": "schwo.phase6.v3_1_u.resume_authority_commit.v1",
                "attempt": int(attempt.name.removeprefix("attempt_")),
                "authority_files": {
                    name: resume._file_identity(attempt / name)
                    for name in resume._AUTHORITY_FILE_ORDER
                },
                "science_calls_before_commit": 0,
            }
        )
    )
    path.chmod(0o444)


def _replace_authority_files_with_empty_mappings(attempt: Path) -> None:
    for name in resume._AUTHORITY_FILE_ORDER:
        path = attempt / name
        path.chmod(0o600)
        path.write_bytes(b"{}\n")
        path.chmod(0o444)
    _rewrite_authority_commit(attempt)


def test_temp_actual_prefix_copy_continues_exact_435_to_495_and_closes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    copied = _copy_actual_prefix(tmp_path / "resume-copy")
    authority1 = _authority_files(tmp_path, copied, token="-1")
    inspection = resume.inspect_interrupted_root(
        copied, logical_root=resume.REAL_ROOT, check_liveness=True
    )

    def abandon(stage: str, path: Path, _offset: int) -> None:
        if path.name == "resume_authority.json" and stage == "after_staging_create":
            raise resume.InjectedInterruption

    with resume.stable_writer_exclusion(copied) as (_fd, lock_identity):
        with pytest.raises(resume.InjectedInterruption):
            resume._publish_attempt_authority(
                copied, inspection, authority1, lock_identity, hook=abandon
            )
    authority = _authority_files(tmp_path, copied, token="-2")
    _set_resume_argv(monkeypatch, copied, authority)
    calls: list[int] = []
    ordinal_by_mode = {
        json.dumps(key.payload(), sort_keys=True): ordinal
        for ordinal, key in enumerate(build_mode_inventory())
    }

    def solve_a(key):
        calls.append(ordinal_by_mode[json.dumps(key.payload(), sort_keys=True)])
        return _fake_route_a(key)

    def solve_u(entry, *, route_map_sha256):
        del route_map_sha256
        schedule = [80, 120, 180]
        records = [
            {
                "mode_ordinal": entry["ordinal"],
                "precision_ordinal": ordinal,
                "Gamma_S_U": "0.01",
                "log_Gamma_S_U": "-4.605170185988091368",
            }
            for ordinal in range(3)
        ]
        return records, {"precision_schedule": schedule}

    def external(path: Path):
        path.write_text("{}\n")
        return [
            {"schema": "injected.external", "ordinal": ordinal} for ordinal in range(23)
        ]

    callbacks = resume.ScienceCallbacks(
        solve_a,
        solve_u,
        lambda node: {"schema": "injected.ap", "node": dict(node)},
        external,
    )
    monkeypatch.setattr(
        resume.original, "evaluate_all_thresholds", lambda *_: _passing_evaluation()
    )
    original_validator_calls: list[bool] = []
    monkeypatch.setattr(
        resume.original,
        "validate_official_candidate",
        lambda _root, *, validate_live_sources=True: original_validator_calls.append(
            validate_live_sources
        ),
    )
    result = resume._resume_root(
        copied,
        authority,
        logical_root=resume.REAL_ROOT,
        callbacks=callbacks,
    )
    assert result["attempt"] == "attempt_0002"
    assert calls == list(range(435, 496))
    assert all(call >= 435 for call in calls)
    assert original_validator_calls == [True, True]
    assert (copied / "records.jsonl").read_bytes()[
        : resume.ORIGINAL_PREFIX_RECORDS_SIZE
    ]
    assert (
        hashlib.sha256(
            (copied / "records.jsonl").read_bytes()[
                : resume.ORIGINAL_PREFIX_RECORDS_SIZE
            ]
        ).hexdigest()
        == resume.ORIGINAL_PREFIX_RECORDS_SHA256
    )
    assert (copied / ".writer.lock").exists()
    assert (copied / ".writer.lock").stat().st_mode & 0o777 == 0o444
    assert (copied / "resume_authority_index.json").is_file()
    assert (copied / "manifest.json").is_file()
    index = json.loads((copied / "resume_authority_index.json").read_text())
    assert [item["classification"] for item in index["attempts"]] == [
        "ABANDONED_PRE_SCIENCE",
        "COMMITTED_AUTHORITY",
    ]

    # Formal T7 adversary 1: a self-consistently re-manifested unknown control
    # path must be rejected by the additive grammar, not accepted by the
    # predecessor's generic manifest validator.
    attempt2 = copied / "resume_control/attempt_0002"
    copied.chmod(0o755)
    attempt2.chmod(0o755)
    unknown = attempt2 / "unknown_control.json"
    unknown.write_bytes(b"{}\n")
    unknown.chmod(0o444)
    _rewrite_terminal_manifest(copied, overall_state="PASS")
    copied.chmod(0o555)
    with pytest.raises(resume.ResumeContractError, match="unknown attempt-level"):
        resume.validate_resumed_candidate(copied, authority=authority)
    copied.chmod(0o755)
    attempt2.chmod(0o755)
    os.unlink(unknown)
    _rewrite_terminal_manifest(copied, overall_state="PASS")
    copied.chmod(0o555)

    # A prior abandoned attempt is also semantically reconstructed rather than
    # trusted through the current attempt's authority chain.
    attempt1 = copied / "resume_control/attempt_0001"
    attempt1.chmod(0o755)
    prior_intent = attempt1 / "attempt_intent.json"
    original_prior_intent = prior_intent.read_bytes()
    prior_intent.chmod(0o600)
    prior_intent.write_bytes(b"{}\n")
    prior_intent.chmod(0o444)
    _rewrite_terminal_manifest(copied, overall_state="PASS")
    copied.chmod(0o555)
    with pytest.raises(resume.ResumeContractError, match="attempt-intent"):
        resume.validate_resumed_candidate(copied, authority=authority)
    copied.chmod(0o755)
    prior_intent.chmod(0o600)
    prior_intent.write_bytes(original_prior_intent)
    prior_intent.chmod(0o444)
    attempt1.chmod(0o555)
    _rewrite_terminal_manifest(copied, overall_state="PASS")

    # Formal T7 adversary 2: replacing all seven authority records with empty
    # mappings remains invalid even after recomputing both the self-reported
    # authority commit and the predecessor manifest.
    _replace_authority_files_with_empty_mappings(attempt2)
    _rewrite_terminal_manifest(copied, overall_state="PASS")
    copied.chmod(0o555)
    with pytest.raises(resume.ResumeContractError, match="attempt-intent"):
        resume.validate_resumed_candidate(copied, authority=authority)


def test_actual_prefix_partial_prepared_tail_recovers_without_resolve(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    copied = _copy_actual_prefix(tmp_path / "partial-copy")
    authority1 = _authority_files(tmp_path, copied, token="-1")
    _set_resume_argv(monkeypatch, copied, authority1)
    inspection = resume.inspect_interrupted_root(
        copied, logical_root=resume.REAL_ROOT, check_liveness=True
    )
    key = build_mode_inventory()[435]
    solves = 0

    def solve_once():
        nonlocal solves
        solves += 1
        mode, ladders = _fake_route_a(key)
        checkpoint = resume.canonical_bytes(
            {
                "schema": "schwo.phase6.v3_1_u.route_a_checkpoint.v1",
                "ordinal": 435,
                "mode": key.payload(),
                "status": "COMPUTED_NOT_ACCEPTED",
                "node_count": 20,
            }
        )
        return [
            (copied / "ladder_records.jsonl", resume._jsonl_block(ladders)),
            (
                copied / "records.jsonl",
                cycle2.compact_jsonl_record(mode),
            ),
        ], checkpoint

    fired = False

    def die(stage: str, path: Path, offset: int) -> None:
        nonlocal fired
        if (
            not fired
            and stage == "after_append_byte"
            and path.name == "ladder_records.jsonl"
            and offset == 17
        ):
            fired = True
            raise resume.InjectedInterruption

    with resume.stable_writer_exclusion(copied) as (_fd, lock_identity):
        attempt1, _ = resume._publish_attempt_authority(
            copied, inspection, authority1, lock_identity
        )
        with pytest.raises(resume.InjectedInterruption):
            resume._transaction(
                attempt1,
                stage="route_a",
                ordinal=435,
                input_payload=key.payload(),
                solve=solve_once,
                checkpoint_path=copied / "mode_checkpoints/route_a_0435.json",
                authority_commit=attempt1 / "authority_commit.json",
                hook=die,
            )
    assert fired and solves == 1
    partial = resume.inspect_interrupted_root(
        copied, logical_root=resume.REAL_ROOT, check_liveness=True
    )
    assert partial["prefix"]["next_ordinal"] == 435
    authority2 = _authority_files(tmp_path, copied, token="-2")
    _set_resume_argv(monkeypatch, copied, authority2)
    with resume.stable_writer_exclusion(copied) as (_fd, lock_identity):
        attempt2, _ = resume._publish_attempt_authority(
            copied, partial, authority2, lock_identity
        )
        resume._recover_prepared(copied, attempt2, hook=None)
    recovered = resume.inspect_interrupted_root(
        copied, logical_root=resume.REAL_ROOT, check_liveness=False
    )
    assert recovered["prefix"]["next_ordinal"] == 436
    assert solves == 1
    assert (
        attempt2 / "recovered_transactions/attempt_0001__route_a_0435/commit.json"
    ).is_file()

    transaction = attempt1 / "transactions/route_a_0435"
    extra_transaction = transaction / "extra_control.json"
    extra_transaction.write_bytes(b"{}\n")
    with pytest.raises(resume.ResumeContractError, match="unknown transaction"):
        resume._validate_resume_control_prefix(copied, 436)
    os.unlink(extra_transaction)
    recovery = attempt2 / "recovered_transactions/attempt_0001__route_a_0435"
    extra_recovery = recovery / "extra_control.json"
    extra_recovery.write_bytes(b"{}\n")
    with pytest.raises(resume.ResumeContractError, match="extra recovery"):
        resume._validate_resume_control_prefix(copied, 436)
    os.unlink(extra_recovery)

    # Prior committed attempts are semantically rebuilt independently of their
    # recomputed self-reported commit identity.
    prior_intent = attempt1 / "attempt_intent.json"
    prior_intent.chmod(0o600)
    prior_intent.write_bytes(b"{}\n")
    prior_intent.chmod(0o444)
    _rewrite_authority_commit(attempt1)
    with pytest.raises(resume.ResumeContractError, match="attempt-intent"):
        resume.inspect_interrupted_root(
            copied, logical_root=resume.REAL_ROOT, check_liveness=False
        )


def test_post_authority_scientific_error_is_terminal_and_nonresumable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    copied = _copy_actual_prefix(tmp_path / "failure-copy")
    authority = _authority_files(tmp_path, copied)
    _set_resume_argv(monkeypatch, copied, authority)

    def fail_science(_key):
        raise RuntimeError("injected scientific failure")

    callbacks = resume.ScienceCallbacks(
        fail_science,
        lambda *_args, **_kwargs: pytest.fail("Route U must not start"),
        lambda _node: pytest.fail("Route B must not start"),
        lambda _path: pytest.fail("Route C must not start"),
    )
    flock_boundaries: list[str] = []

    def failure_boundary(stage: str, _path: Path, _offset: int) -> None:
        if stage not in {"failure_flock_held", "failure_root_sealed_under_flock"}:
            return
        contender = os.open(copied / ".writer.lock", os.O_RDONLY)
        try:
            with pytest.raises(BlockingIOError):
                fcntl.flock(contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(contender)
        flock_boundaries.append(stage)

    with pytest.raises(RuntimeError, match="injected scientific failure"):
        resume._resume_root(
            copied,
            authority,
            logical_root=resume.REAL_ROOT,
            callbacks=callbacks,
            hook=failure_boundary,
        )
    failure = json.loads((copied / "failure.json").read_text())
    assert failure["scientific_pass"] is False
    assert failure["resumable"] is False
    assert (copied / "failure_manifest.json").is_file()
    assert not (copied / "manifest.json").exists()
    assert copied.stat().st_mode & 0o777 == 0o555
    assert (copied / ".writer.lock").stat().st_mode & 0o777 == 0o444
    assert flock_boundaries == [
        "failure_flock_held",
        "failure_root_sealed_under_flock",
    ]
    with pytest.raises(resume.ResumeContractError, match="terminal/nonresumable"):
        resume.inspect_interrupted_root(
            copied, logical_root=resume.REAL_ROOT, check_liveness=False
        )

    # FAIL terminal variants are subject to the same exact attempt grammar and
    # independent semantic authority reconstruction.
    attempt = copied / "resume_control/attempt_0001"
    copied.chmod(0o755)
    attempt.chmod(0o755)
    unknown = attempt / "unknown_control.json"
    unknown.write_bytes(b"{}\n")
    unknown.chmod(0o444)
    _rewrite_terminal_manifest(copied, overall_state="FAILED")
    copied.chmod(0o555)
    with pytest.raises(resume.ResumeContractError, match="unknown attempt-level"):
        resume._validate_resume_control_prefix(copied, 435)
    copied.chmod(0o755)
    attempt.chmod(0o755)
    os.unlink(unknown)
    _replace_authority_files_with_empty_mappings(attempt)
    _rewrite_terminal_manifest(copied, overall_state="FAILED")
    copied.chmod(0o555)
    with pytest.raises(resume.ResumeContractError, match="attempt-intent"):
        resume._validate_resume_control_prefix(copied, 435)
