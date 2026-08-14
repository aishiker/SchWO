from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess

import pytest

import schwgw.validation.phase6_v3_hp_unitarity_resume as resume


def _identity(path: Path) -> dict[str, int | str]:
    info = path.stat()
    return {
        "device": info.st_dev,
        "inode": info.st_ino,
        "mode": info.st_mode & 0o777,
        "nlink": info.st_nlink,
    }


def test_frozen_controller_gate_and_exact_suffix_plan() -> None:
    result = resume.verify_controller_gate()
    assert result["package"]["gate_id"] == resume.GATE_ID
    for prefix in (0, 1, 435, 495):
        plan = resume.remaining_route_a_ordinals(prefix)
        assert plan == tuple(range(prefix, 496))
        assert all(ordinal >= prefix for ordinal in plan)
    assert resume.remaining_route_a_ordinals(435) == tuple(range(435, 496))
    with pytest.raises(resume.ResumeContractError):
        resume.remaining_route_a_ordinals(-1)
    with pytest.raises(resume.ResumeContractError):
        resume.remaining_route_a_ordinals(497)


def test_atomic_publication_never_exposes_partial_final_name(tmp_path: Path) -> None:
    target = tmp_path / "authority.json"
    payload = b'{"complete":true}\n'

    def die(stage: str, _path: Path, _offset: int) -> None:
        if stage == "during_staging_write":
            raise resume.InjectedInterruption

    with pytest.raises(resume.InjectedInterruption):
        resume.atomic_publish(target, payload, staging_token="dead", hook=die)
    assert not target.exists()
    staging = list(tmp_path.glob(".*.staging.*"))
    assert len(staging) == 1
    assert staging[0].read_bytes() == payload

    completed = tmp_path / "completed.json"
    identity = resume.atomic_publish(completed, payload, staging_token="ok")
    assert completed.read_bytes() == payload
    assert identity["mode"] == 0o444
    with pytest.raises(FileExistsError):
        resume.atomic_publish(completed, payload, staging_token="duplicate")


_ROUTE_APPEND_BLOCKS = {
    "route_a": b'{"stage":"route_a"}\n',
    "route_u": b'{"stage":"route_u"}\n',
    "route_b": b'{"stage":"route_b"}\n',
}


@pytest.mark.parametrize(
    ("stage", "block", "cut"),
    [
        (stage, block, cut)
        for stage, block in _ROUTE_APPEND_BLOCKS.items()
        for cut in range(len(block) + 1)
    ],
)
def test_authenticated_missing_tail_is_completed_byte_exactly(
    tmp_path: Path, stage: str, block: bytes, cut: int
) -> None:
    prefix = b'{"old":1}\n'
    path = tmp_path / f"{stage}-records-{cut}.jsonl"
    path.write_bytes(prefix + block[:cut])
    identity = _identity(path)
    resume.append_authenticated_tail(
        path,
        pre_size=len(prefix),
        pre_sha256=hashlib.sha256(prefix).hexdigest(),
        block=block,
        expected_identity=identity,
    )
    assert path.read_bytes() == prefix + block


@pytest.mark.parametrize(
    "death_stage",
    (
        "after_staging_create",
        "during_staging_write",
        "after_staging_fsync",
        "before_atomic_rename",
        "after_atomic_rename",
    ),
)
def test_route_c_staged_publication_is_atomic_at_every_boundary(
    tmp_path: Path, death_stage: str
) -> None:
    target = tmp_path / "external_raw.json"
    payload = b'{"route":"c","records":23}\n'

    def die(stage: str, _path: Path, _offset: int) -> None:
        if stage == death_stage:
            raise resume.InjectedInterruption

    with pytest.raises(resume.InjectedInterruption):
        resume.atomic_publish(target, payload, staging_token=death_stage, hook=die)
    if target.exists():
        assert target.read_bytes() == payload
        assert target.stat().st_mode & 0o777 == 0o444
    else:
        assert list(tmp_path.glob(".external_raw.json.staging.*"))


@pytest.mark.parametrize(
    ("boundary", "target_name", "prepared_expected", "solve_count"),
    (
        ("before_atomic_rename", "intent.json", False, 1),
        ("after_atomic_rename", "intent.json", False, 1),
        ("after_empty_target_creation", "external_records.jsonl", False, 2),
        ("after_empty_target_creation", "external_raw.json", False, 2),
        ("before_prepared_publication", "prepared.json", False, 2),
        ("after_atomic_rename", "prepared.json", True, 1),
    ),
)
def test_route_c_completion_uses_prepared_commit_not_file_existence(
    tmp_path: Path,
    boundary: str,
    target_name: str,
    prepared_expected: bool,
    solve_count: int,
) -> None:
    root = tmp_path / "root"
    attempt1 = root / "resume_control/attempt_0001"
    attempt2 = root / "resume_control/attempt_0002"
    attempt1.mkdir(parents=True)
    attempt2.mkdir()
    for attempt in (attempt1, attempt2):
        (attempt / "authority_commit.json").write_text('{"authority":true}\n')
    calls = 0
    fired = False

    def solve():
        nonlocal calls
        calls += 1
        return [
            (root / "external_records.jsonl", b'{"ordinal":0}\n'),
            (root / "external_raw.json", b'{"raw":true}\n'),
        ], None

    def die(stage: str, path: Path, _offset: int) -> None:
        nonlocal fired
        if not fired and stage == boundary and path.name == target_name:
            fired = True
            raise resume.InjectedInterruption

    with pytest.raises(resume.InjectedInterruption):
        resume._transaction(
            attempt1,
            stage="route_c",
            ordinal=0,
            input_payload={"record_count": 23},
            solve=solve,
            checkpoint_path=None,
            authority_commit=attempt1 / "authority_commit.json",
            hook=die,
        )
    assert fired
    prepared = attempt1 / "transactions/route_c_0000/prepared.json"
    assert prepared.exists() is prepared_expected
    if prepared_expected:
        resume._recover_prepared(root, attempt2, hook=None)
    else:
        resume._transaction(
            attempt2,
            stage="route_c",
            ordinal=0,
            input_payload={"record_count": 23},
            solve=solve,
            checkpoint_path=None,
            authority_commit=attempt2 / "authority_commit.json",
            hook=None,
        )
    assert calls == solve_count
    assert resume._committed_transaction_exists(root, "route_c", 0)
    assert (root / "external_records.jsonl").read_bytes() == b'{"ordinal":0}\n'
    assert (root / "external_raw.json").read_bytes() == b'{"raw":true}\n'


def test_authenticated_tail_rejects_mismatch_and_identity_drift(tmp_path: Path) -> None:
    prefix = b"prefix\n"
    block = b"prepared\n"
    path = tmp_path / "records.jsonl"
    path.write_bytes(prefix + b"wrong")
    with pytest.raises(resume.ResumeContractError, match="mismatched append suffix"):
        resume.append_authenticated_tail(
            path,
            pre_size=len(prefix),
            pre_sha256=hashlib.sha256(prefix).hexdigest(),
            block=block,
        )
    path.write_bytes(prefix)
    wrong = {**_identity(path), "inode": path.stat().st_ino + 1}
    with pytest.raises(resume.ResumeContractError, match="identity drift"):
        resume.append_authenticated_tail(
            path,
            pre_size=len(prefix),
            pre_sha256=hashlib.sha256(prefix).hexdigest(),
            block=block,
            expected_identity=wrong,
        )


def test_stable_lock_path_is_never_removed_and_concurrent_owner_fails(
    tmp_path: Path,
) -> None:
    lock = tmp_path / ".writer.lock"
    lock.write_bytes(b"")
    inode = lock.stat().st_ino
    with resume.stable_writer_exclusion(tmp_path):
        assert lock.exists() and lock.stat().st_ino == inode
        second = os.open(lock, os.O_RDWR)
        try:
            with pytest.raises(BlockingIOError):
                fcntl.flock(second, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(second)
    assert lock.exists() and lock.stat().st_ino == inode


def test_unsafe_lock_and_duplicate_json_fail_closed(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.write_bytes(b"")
    (tmp_path / ".writer.lock").symlink_to(target)
    with pytest.raises(resume.ResumeContractError, match="unsafe resume file"):
        with resume.stable_writer_exclusion(tmp_path):
            pass
    with pytest.raises(resume.ResumeContractError, match="duplicate JSON key"):
        resume.strict_json_bytes(b'{"a":1,"a":2}', where="fixture")


def test_prepared_transaction_recovers_partial_targets_without_rewrite(
    tmp_path: Path,
) -> None:
    data = tmp_path / "data.jsonl"
    prefix = b'{"ordinal":0}\n'
    block = b'{"ordinal":1}\n'
    data.write_bytes(prefix + block[:5])
    before_inode = data.stat().st_ino
    checkpoint = b'{"ordinal":1}\n'
    prepared = {
        "schema": "schwo.phase6.v3_1_u.prepared_transaction.v1",
        "stage": "route_a",
        "ordinal": 1,
        "intent": {},
        "targets": [
            {
                "path": str(data),
                "pre_size": len(prefix),
                "pre_sha256": hashlib.sha256(prefix).hexdigest(),
                "file_identity": _identity(data),
                "block_sha256": hashlib.sha256(block).hexdigest(),
                "block_size": len(block),
                "block_base64": __import__("base64").b64encode(block).decode(),
            }
        ],
        "checkpoint_sha256": hashlib.sha256(checkpoint).hexdigest(),
        "checkpoint_base64": __import__("base64").b64encode(checkpoint).decode(),
    }
    prepared_path = tmp_path / "prepared.json"
    prepared_path.write_bytes(
        json.dumps(prepared, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    checkpoint_path = tmp_path / "checkpoint.json"
    commit_path = tmp_path / "commit.json"
    resume.execute_prepared_transaction(
        prepared_path,
        checkpoint_path=checkpoint_path,
        commit_path=commit_path,
        token="recover",
    )
    assert data.read_bytes() == prefix + block
    assert data.stat().st_ino == before_inode
    assert checkpoint_path.read_bytes() == checkpoint
    assert commit_path.is_file()
    first_commit = commit_path.read_bytes()
    resume.execute_prepared_transaction(
        prepared_path,
        checkpoint_path=checkpoint_path,
        commit_path=commit_path,
        token="idempotent",
    )
    assert commit_path.read_bytes() == first_commit


def test_controller_ast_has_no_unlink_replace_truncate_or_seek() -> None:
    source = resume.CONTROLLER_PATH.read_text()
    assert ".unlink(" not in source
    assert "os.replace(" not in source
    assert "O_TRUNC" not in source
    assert ".seek(" not in source
    assert "renamex_np" in source and "O_APPEND" in source and "flock" in source
    function = source[source.index("def _resume_root_active(") :]
    assert (
        function.index('stage="route_a"')
        < function.index('stage="route_u"')
        < function.index('stage="route_b"')
        < function.index('stage="route_c"')
    )


@pytest.mark.parametrize(
    "death_stage",
    (
        "after_staging_create",
        "during_staging_write",
        "after_staging_fsync",
        "before_atomic_rename",
        "after_atomic_rename",
    ),
)
def test_authority_publication_death_keeps_stable_lock_and_monotone_chain(
    tmp_path: Path, death_stage: str
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    lock = root / ".writer.lock"
    lock.write_bytes(b"")
    for name in ("run_contract.json", "source_start.json", "inventory.json"):
        (root / name).write_text("{}\n")
    hashes = resume.implementation_hashes()
    approval = tmp_path / "approval.md"
    approval.write_text(
        "\n".join(
            (
                "ADVANCE_DECISION: ADVANCE",
                "CLAIM_STATUS: NOT_ASSESSED",
                "V3.1-U RESUME-CONTROLLER",
                resume.PACKAGE_SHA256,
                *hashes.values(),
            )
        )
    )
    approval_sha = hashlib.sha256(approval.read_bytes()).hexdigest()
    inspection = {
        "prefix": {"next_ordinal": 435},
        "liveness": {"active_writer": False},
        "lock_identity": resume._file_identity(lock),
    }

    def make_authority(name: str) -> resume.Authority:
        dispatch = tmp_path / name
        chain = resume._prior_authority_chain(root)
        dispatch.write_bytes(
            resume.canonical_bytes(
                {
                    "schema": "schwo.phase6.v3_1_u.resume_dispatch.v1",
                    "gate_id": resume.GATE_ID,
                    "single_use": True,
                    "exact_root": str(root.resolve()),
                    "next_attempt": chain["next_attempt"],
                    "prefix": inspection["prefix"],
                    "stable_lock_identity": inspection["lock_identity"],
                    "prior_authority_chain_sha256": chain["sha256"],
                    "implementation_approval": {
                        "path": str(approval.resolve()),
                        "sha256": approval_sha,
                    },
                    "implementation_hashes": hashes,
                    "authorized_at_utc": "2026-08-12T00:00:00Z",
                }
            )
        )
        return resume.Authority(
            approval,
            approval_sha,
            dispatch,
            hashlib.sha256(dispatch.read_bytes()).hexdigest(),
        )

    authority = make_authority("dispatch-1.json")
    inode = lock.stat().st_ino
    fired = False

    def die(stage: str, path: Path, _offset: int) -> None:
        nonlocal fired
        if path.name == "resume_authority.json" and stage == death_stage:
            fired = True
            raise resume.InjectedInterruption

    with resume.stable_writer_exclusion(root) as (_fd, lock_identity):
        with pytest.raises(resume.InjectedInterruption):
            resume._publish_attempt_authority(
                root, inspection, authority, lock_identity, hook=die
            )
    assert fired
    assert lock.exists() and lock.stat().st_ino == inode and lock.read_bytes() == b""
    attempt1 = root / "resume_control/attempt_0001"
    final = attempt1 / "resume_authority.json"
    if final.exists():
        json.loads(final.read_text())
    with resume.stable_writer_exclusion(root) as (_fd, lock_identity):
        with pytest.raises(resume.ResumeContractError, match="dispatch binding"):
            resume._publish_attempt_authority(
                root, inspection, authority, lock_identity
            )
    authority2 = make_authority("dispatch-2.json")
    with resume.stable_writer_exclusion(root) as (_fd, lock_identity):
        attempt2, _ = resume._publish_attempt_authority(
            root, inspection, authority2, lock_identity
        )
    assert attempt2.name == "attempt_0002"
    adjudication = json.loads(
        (attempt2 / "abandoned_attempt_adjudication.json").read_text()
    )
    assert adjudication["prior_attempts"] == [
        {
            "attempt": 1,
            "authority_committed": False,
            "files": sorted(path.name for path in attempt1.iterdir() if path.is_file()),
            "classification": "ABANDONED_PRE_SCIENCE",
        }
    ]
    assert (attempt2 / "authority_commit.json").is_file()


def test_hardlinked_data_and_unknown_prepared_suffix_fail_closed(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.write_bytes(b"prefix\n")
    linked = tmp_path / "linked"
    os.link(source, linked)
    with pytest.raises(resume.ResumeContractError, match="unsafe resume file"):
        resume._file_identity(source)
    ordinary = tmp_path / "ordinary"
    ordinary.write_bytes(b"prefix\nunauthenticated")
    with pytest.raises(resume.ResumeContractError, match="mismatched append suffix"):
        resume.append_authenticated_tail(
            ordinary,
            pre_size=len(b"prefix\n"),
            pre_sha256=hashlib.sha256(b"prefix\n").hexdigest(),
            block=b"expected\n",
        )


def test_formal_target_chain_rejects_gap_duplicate_and_trailing_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "chain"
    root.mkdir()
    for name in ("records.jsonl", "ladder_records.jsonl"):
        (root / name).write_bytes(b"")
    monkeypatch.setattr(resume, "ORIGINAL_PREFIX_RECORDS_SIZE", 0)
    monkeypatch.setattr(resume, "ORIGINAL_PREFIX_LADDERS_SIZE", 0)
    monkeypatch.setattr(
        resume, "ORIGINAL_PREFIX_RECORDS_SHA256", hashlib.sha256(b"").hexdigest()
    )
    monkeypatch.setattr(
        resume, "ORIGINAL_PREFIX_LADDERS_SHA256", hashlib.sha256(b"").hexdigest()
    )
    first = b'{"ordinal":0}\n'
    second = b'{"ordinal":1}\n'
    route_u = root / "route_u_records.jsonl"
    route_u.write_bytes(first + second)
    base = {
        "stage": "route_u",
        "state": "COMMITTED",
        "attempt": "attempt_0001",
    }
    transactions = [
        {
            **base,
            "ordinal": 0,
            "targets": [
                {
                    "name": "route_u_records.jsonl",
                    "pre_size": 0,
                    "pre_sha256": hashlib.sha256(b"").hexdigest(),
                    "end_size": len(first),
                    "end_sha256": hashlib.sha256(first).hexdigest(),
                    "block_size": len(first),
                    "block_sha256": hashlib.sha256(first).hexdigest(),
                }
            ],
        },
        {
            **base,
            "ordinal": 1,
            "targets": [
                {
                    "name": "route_u_records.jsonl",
                    "pre_size": len(first),
                    "pre_sha256": hashlib.sha256(first).hexdigest(),
                    "end_size": len(first + second),
                    "end_sha256": hashlib.sha256(first + second).hexdigest(),
                    "block_size": len(second),
                    "block_sha256": hashlib.sha256(second).hexdigest(),
                }
            ],
        },
    ]
    resume._validate_formal_target_chains(root, transactions)
    broken = json.loads(json.dumps(transactions))
    broken[1]["targets"][0]["pre_sha256"] = "0" * 64
    with pytest.raises(resume.ResumeContractError, match="discontinuous"):
        resume._validate_formal_target_chains(root, broken)
    with pytest.raises(resume.ResumeContractError, match="duplicate prepared"):
        resume._validate_formal_target_chains(root, [*transactions, transactions[1]])
    route_u.write_bytes(first + second + b"unauthenticated")
    with pytest.raises(resume.ResumeContractError, match="trailing bytes"):
        resume._validate_formal_target_chains(root, transactions)


def test_liveness_ignores_caffeinate_parent_but_detects_resume_process(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    for name in (".writer.lock", "records.jsonl", "ladder_records.jsonl"):
        (root / name).write_bytes(b"")
    root_text = str(root.resolve())
    caffeinate = (
        f"90001 1 90001 S caffeinate /opt/homebrew/bin/python3.14 "
        f"{resume.CLI_PATH} resume --root {root_text}\n"
    )
    writer = (
        f"90002 1 90002 S /opt/homebrew/bin/python3.14 "
        f"{resume.CLI_PATH} resume --root {root_text}\n"
    )

    def fake_run(command, **_kwargs):
        if command[0] == "ps":
            return subprocess.CompletedProcess(command, 0, caffeinate, "")
        return subprocess.CompletedProcess(command, 1, "", "")

    monkeypatch.setattr(resume.subprocess, "run", fake_run)
    assert resume._process_liveness(root)["active_writer"] is False

    def writer_run(command, **_kwargs):
        if command[0] == "ps":
            return subprocess.CompletedProcess(command, 0, writer, "")
        return subprocess.CompletedProcess(command, 1, "", "")

    monkeypatch.setattr(resume.subprocess, "run", writer_run)
    result = resume._process_liveness(root)
    assert result["active_writer"] is True
    assert result["related_process_rows"] == [writer.strip()]
