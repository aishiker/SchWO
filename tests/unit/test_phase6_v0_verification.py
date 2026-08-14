from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import stat

import pytest

import scripts.phase6_publish_v0_verification as v0_cli
import schwgw.validation.phase6_v0_verification as v0
from schwgw.validation.phase6_domain import canonical_json_bytes
from schwgw.validation.phase6_release_preparation import preflight_release_map
from schwgw.validation.phase6_v0_verification import (
    CHECK_REPORT_SCHEMA,
    REQUIRED_CHECK_IDS,
    VERIFICATION_SCHEMA,
    Phase6V0VerificationError,
    preflight_v0_verification,
    publish_v0_verification,
    validate_published_v0_root,
)
from tests.unit.test_phase6_release_preparation import (
    _base_map,
    _certificate,
    _source,
)


def _identity(path: Path) -> dict[str, object]:
    info = path.lstat()
    return {
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
        "path": str(path.absolute()),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size": info.st_size,
    }


def _report_payload(
    tmp_path: Path,
    check_id: str,
    *,
    outcome: str = "PASS",
) -> tuple[dict[str, object], Path]:
    source_root = tmp_path / f"source-{check_id}"
    source_root.mkdir()
    source_path = source_root / "actual_check_output.txt"
    source_path.write_text(f"actual output for {check_id}\n", encoding="utf-8")
    counts = {
        "passed": int(outcome == "PASS"),
        "failed": int(outcome == "FAIL"),
        "skipped": int(outcome == "SKIP"),
    }
    payload = {
        "schema": CHECK_REPORT_SCHEMA,
        "check_id": check_id,
        "command_argv": ["python", "-m", "pytest", check_id],
        "working_directory": str(tmp_path.resolve()),
        "exit_status": 1 if outcome == "FAIL" else 0,
        "assertions": [
            {
                "assertion_id": f"{check_id}.actual_result",
                "outcome": outcome,
                "detail": "terminal machine-readable fixture assertion",
            }
        ],
        "counts": counts,
        "source_identities": [_identity(source_path)],
        "execution_complete": True,
        "global_green_permitted": False,
        "li_figure_agreement_primary_gate": False,
    }
    return payload, source_path


def _frozen_report(
    tmp_path: Path,
    check_id: str,
    *,
    outcome: str = "PASS",
    mutate: Callable[[dict[str, object]], None] | None = None,
) -> tuple[Path, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    payload, source_path = _report_payload(tmp_path, check_id, outcome=outcome)
    if mutate is not None:
        mutate(payload)
    root = tmp_path / f"report-{check_id}"
    root.mkdir()
    report_path = root / "check_report.json"
    report_path.write_bytes(canonical_json_bytes(payload))
    os.chmod(report_path, 0o444)
    os.chmod(root, 0o555)
    return report_path.resolve(), source_path


def _all_reports(
    tmp_path: Path,
    *,
    outcomes: dict[str, str] | None = None,
) -> tuple[dict[str, Path], dict[str, Path]]:
    reports: dict[str, Path] = {}
    sources: dict[str, Path] = {}
    for check_id in REQUIRED_CHECK_IDS:
        report, source = _frozen_report(
            tmp_path,
            check_id,
            outcome=(outcomes or {}).get(check_id, "PASS"),
        )
        reports[check_id] = report
        sources[check_id] = source
    return reports, sources


def test_publish_pass_root_is_immutable_and_release_adapter_compatible(
    tmp_path: Path,
) -> None:
    reports, _ = _all_reports(tmp_path)
    output = tmp_path.resolve() / "v0-formal-root"

    result = publish_v0_verification("phase6_v0_fixture", reports, output)

    assert result == validate_published_v0_root(output)
    assert result["verification_state"] == "PASS"
    assert result["check_state_counts"] == {"PARTIAL": 0, "PASS": 4, "FAIL": 0}
    assert stat.S_IMODE(output.stat().st_mode) == 0o555
    assert stat.S_IMODE((output / "verification.json").stat().st_mode) == 0o444
    assert (output / "verification.json").stat().st_nlink == 1
    verification = json.loads((output / "verification.json").read_text())
    assert verification["schema"] == VERIFICATION_SCHEMA
    assert verification["global_green_permitted"] is False

    release_map = _base_map()
    release_map["sources"] = [
        _source(
            "v0_formal",
            "V0_IMPLEMENTATION_VERIFICATION_V1",
            output,
            {"verification.json": result["verification_sha256"]},
        )
    ]
    _certificate(release_map, "V0", "claim_provenance_cleanup")["evidence_ids"] = [
        "v0_formal"
    ]
    preparation = preflight_release_map(release_map)
    assert (
        preparation["certificate_states"]["cert_v0_claim_provenance_cleanup"] == "PASS"
    )

    with pytest.raises(Phase6V0VerificationError, match="overwrite"):
        publish_v0_verification("phase6_v0_fixture", reports, output)


def test_native_failure_and_skip_derive_fail_and_partial(tmp_path: Path) -> None:
    failed_reports, _ = _all_reports(
        tmp_path / "failed",
        outcomes={"full_test_suite": "FAIL"},
    )
    failed = preflight_v0_verification("v0_failed", failed_reports)
    assert failed["verification_state"] == "FAIL"
    assert failed["check_state_counts"] == {"PARTIAL": 0, "PASS": 3, "FAIL": 1}

    skipped_reports, _ = _all_reports(
        tmp_path / "skipped",
        outcomes={"legacy_np_isolation": "SKIP"},
    )
    partial = preflight_v0_verification("v0_partial", skipped_reports)
    assert partial["verification_state"] == "PARTIAL"
    assert partial["check_state_counts"] == {"PARTIAL": 1, "PASS": 3, "FAIL": 0}


def test_source_report_cannot_supply_state_or_forge_counts(tmp_path: Path) -> None:
    def add_state(payload: dict[str, object]) -> None:
        payload["state"] = "PASS"

    forged, _ = _frozen_report(tmp_path / "state", "full_test_suite", mutate=add_state)
    reports, _ = _all_reports(tmp_path / "other-state")
    reports["full_test_suite"] = forged
    with pytest.raises(Phase6V0VerificationError, match="schema changed"):
        preflight_v0_verification("v0_forged_state", reports)

    def forge_counts(payload: dict[str, object]) -> None:
        payload["counts"]["passed"] = 2

    forged_counts, _ = _frozen_report(
        tmp_path / "counts", "full_test_suite", mutate=forge_counts
    )
    reports, _ = _all_reports(tmp_path / "other-counts")
    reports["full_test_suite"] = forged_counts
    with pytest.raises(Phase6V0VerificationError, match="not derived"):
        preflight_v0_verification("v0_forged_counts", reports)


def test_exit_status_must_match_failed_assertions(tmp_path: Path) -> None:
    def forge_exit(payload: dict[str, object]) -> None:
        payload["exit_status"] = 7

    forged, _ = _frozen_report(tmp_path / "exit", "full_test_suite", mutate=forge_exit)
    reports, _ = _all_reports(tmp_path / "other-exit")
    reports["full_test_suite"] = forged

    with pytest.raises(Phase6V0VerificationError, match="exit_status contradicts"):
        preflight_v0_verification("v0_forged_exit", reports)


def test_referenced_source_identity_drift_fails_closed(tmp_path: Path) -> None:
    reports, sources = _all_reports(tmp_path)
    sources["stale_production_metadata"].write_text(
        "changed after report publication\n", encoding="utf-8"
    )

    with pytest.raises(Phase6V0VerificationError, match="identity drifted"):
        preflight_v0_verification("v0_source_drift", reports)


def test_mutable_or_hardlinked_check_report_fails_closed(tmp_path: Path) -> None:
    reports, _ = _all_reports(tmp_path / "mutable")
    mutable = reports["legacy_np_isolation"]
    os.chmod(mutable, 0o644)
    with pytest.raises(Phase6V0VerificationError, match="immutable nlink1"):
        preflight_v0_verification("v0_mutable", reports)

    reports, _ = _all_reports(tmp_path / "hardlink")
    aliased = reports["legacy_np_isolation"]
    root = aliased.parent
    os.chmod(root, 0o755)
    os.link(aliased, root / "alias.json")
    os.chmod(root, 0o555)
    with pytest.raises(Phase6V0VerificationError, match="immutable nlink1"):
        preflight_v0_verification("v0_hardlink", reports)


def test_report_paths_must_be_exact_and_absolute(tmp_path: Path) -> None:
    reports, _ = _all_reports(tmp_path)
    missing = dict(reports)
    missing.pop("full_test_suite")
    with pytest.raises(Phase6V0VerificationError, match="exactly the four"):
        preflight_v0_verification("v0_missing", missing)

    relative = dict(reports)
    relative["full_test_suite"] = Path("relative-check-report.json")
    with pytest.raises(Phase6V0VerificationError, match="must be absolute"):
        preflight_v0_verification("v0_relative", relative)


def test_check_only_cli_writes_nothing(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    reports, _ = _all_reports(tmp_path)
    before = {path for path in tmp_path.rglob("*")}
    argv = ["--verification-id", "v0_cli_check", "--check-only"]
    for check_id, flag in v0_cli.REPORT_ARGUMENTS.items():
        argv.extend([flag, str(reports[check_id])])

    assert v0_cli.main(argv) == 0

    result = json.loads(capsys.readouterr().out)
    assert result["output_written"] is False
    assert result["verification_state"] == "PASS"
    assert {path for path in tmp_path.rglob("*")} == before


def test_published_root_rejects_extra_file_and_hardlink(tmp_path: Path) -> None:
    reports, _ = _all_reports(tmp_path)
    output = tmp_path.resolve() / "v0-layout"
    publish_v0_verification("v0_layout", reports, output)
    os.chmod(output, 0o755)
    extra = output / "extra.json"
    extra.write_bytes(canonical_json_bytes({"extra": True}))
    os.chmod(extra, 0o444)
    os.chmod(output, 0o555)
    with pytest.raises(Phase6V0VerificationError, match="layout/mode"):
        validate_published_v0_root(output)

    output = tmp_path.resolve() / "v0-hardlink-output"
    publish_v0_verification("v0_hardlink_output", reports, output)
    os.chmod(output, 0o755)
    os.link(output / "verification.json", output / "verification-alias.json")
    os.chmod(output, 0o555)
    with pytest.raises(Phase6V0VerificationError, match="layout/mode"):
        validate_published_v0_root(output)


def test_publication_failure_seals_partial_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reports, _ = _all_reports(tmp_path)
    output = tmp_path.resolve() / "v0-failed-publication"
    original = v0._exclusive_bytes

    def fail_after_write(path: Path, data: bytes) -> dict[str, object]:
        original(path, data)
        raise RuntimeError("injected V0 publication failure")

    monkeypatch.setattr(v0, "_exclusive_bytes", fail_after_write)
    with pytest.raises(RuntimeError, match="injected V0"):
        publish_v0_verification("v0_failed_publish", reports, output)

    assert stat.S_IMODE(output.stat().st_mode) == 0o555
    assert stat.S_IMODE((output / "verification.json").stat().st_mode) == 0o444


def test_report_payload_is_not_mutated_by_preflight(tmp_path: Path) -> None:
    reports, _ = _all_reports(tmp_path)
    originals = {
        check_id: deepcopy(json.loads(path.read_text()))
        for check_id, path in reports.items()
    }

    preflight_v0_verification("v0_read_only", reports)

    assert {
        check_id: json.loads(path.read_text()) for check_id, path in reports.items()
    } == originals
