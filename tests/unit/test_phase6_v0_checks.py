from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess

import pytest

import scripts.phase6_run_v0_check as check_cli
import schwgw.validation.phase6_v0_checks as checks
from schwgw.validation.phase6_v0_checks import (
    Phase6V0CheckError,
    run_v0_check,
    validate_published_check_root,
)
from schwgw.validation.phase6_v0_verification import (
    REQUIRED_CHECK_IDS,
    publish_v0_verification,
)


STATIC_CHECKS = tuple(
    check_id for check_id in REQUIRED_CHECK_IDS if check_id != "full_test_suite"
)


def _fake_pytest(
    *,
    failure: bool = False,
):
    def run(
        argv,
        *,
        cwd,
        env,
        check,
        stdout,
        stderr,
    ) -> subprocess.CompletedProcess[bytes]:
        assert argv[:4] == [str(checks.PYTHON314), "-m", "pytest", "-q"]
        assert cwd == checks.PROJECT_ROOT
        assert env["PYTHONDONTWRITEBYTECODE"] == "1"
        assert env["PYTHONPATH"] == (
            f"{checks.OVERLAY_ROOT}:{checks.PROJECT_ROOT / 'src'}"
        )
        assert check is False
        assert stdout == subprocess.PIPE
        assert stderr == subprocess.PIPE
        junit = Path(
            next(
                value.split("=", 1)[1]
                for value in argv
                if value.startswith("--junitxml=")
            )
        )
        terminal = (
            '<failure message="fixture failure">failed</failure>' if failure else ""
        )
        junit.write_text(
            "<?xml version='1.0' encoding='utf-8'?>"
            "<testsuites><testsuite tests='2' failures='1' skipped='1'>"
            f"<testcase classname='fixture' name='first'>{terminal}</testcase>"
            "<testcase classname='fixture' name='second'><skipped /></testcase>"
            "</testsuite></testsuites>",
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(
            argv,
            1 if failure else 0,
            stdout=b"fixture pytest stdout\n",
            stderr=b"fixture pytest stderr\n",
        )

    return run


@pytest.mark.parametrize("check_id", STATIC_CHECKS)
def test_frozen_static_runner_derives_pass_without_user_state(
    tmp_path: Path,
    check_id: str,
) -> None:
    output = tmp_path.resolve() / check_id

    result = run_v0_check(check_id, output)

    assert result == validate_published_check_root(output, expected_check_id=check_id)
    assert result["state"] == "PASS"
    assert result["passed"] > 0
    assert result["failed"] == 0
    assert stat.S_IMODE(output.stat().st_mode) == 0o555
    assert {child.name for child in output.iterdir()} == {"check_report.json"}
    report = json.loads((output / "check_report.json").read_text())
    assert "state" not in report
    assert report["counts"]["passed"] == len(report["assertions"])
    assert report["exit_status"] == 0
    assert report["command_argv"] == [
        str(checks.PYTHON314),
        str(checks.RUNNER_PATH),
        "--check-id",
        check_id,
        "--output-root",
        str(output),
    ]

    with pytest.raises(Phase6V0CheckError, match="fresh"):
        run_v0_check(check_id, output)


def test_full_suite_runner_derives_junit_counts_and_immutable_sources(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(checks.subprocess, "run", _fake_pytest())
    output = tmp_path.resolve() / "full-suite"

    result = run_v0_check("full_test_suite", output)

    assert result["state"] == "PASS"
    assert result["passed"] == 1
    assert result["failed"] == 0
    assert result["skipped"] == 1
    assert {child.name for child in output.iterdir()} == {
        "check_report.json",
        "junit.xml",
        "pytest.stderr.txt",
        "pytest.stdout.txt",
    }
    assert all(
        stat.S_IMODE(child.stat().st_mode) == 0o444 and child.stat().st_nlink == 1
        for child in output.iterdir()
    )
    report = json.loads((output / "check_report.json").read_text())
    assert report["command_argv"] == [
        str(checks.PYTHON314),
        "-m",
        "pytest",
        "-q",
        f"--junitxml={output / 'junit.xml'}",
    ]
    assert result == validate_published_check_root(
        output, expected_check_id="full_test_suite"
    )


def test_full_suite_native_failure_cannot_be_promoted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(checks.subprocess, "run", _fake_pytest(failure=True))

    result = run_v0_check("full_test_suite", tmp_path.resolve() / "full-suite-failed")

    assert result["state"] == "FAIL"
    assert result["failed"] == 1
    assert result["passed"] == 0
    assert result["skipped"] == 1


def test_trusted_reports_feed_final_v0_without_handwritten_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(checks.subprocess, "run", _fake_pytest())
    report_paths: dict[str, Path] = {}
    for check_id in REQUIRED_CHECK_IDS:
        result = run_v0_check(check_id, tmp_path.resolve() / f"report-{check_id}")
        report_paths[check_id] = Path(result["report_path"])

    final = publish_v0_verification(
        "phase6_v0_trusted_fixture",
        report_paths,
        tmp_path.resolve() / "final-verification",
    )

    assert final["verification_state"] == "PASS"
    assert final["check_state_counts"] == {"PARTIAL": 0, "PASS": 4, "FAIL": 0}
    assert final["output_written"] is True


def test_runner_cli_exposes_no_state_or_count_override(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        check_cli.main(
            [
                "--check-id",
                "stale_production_metadata",
                "--output-root",
                str(tmp_path / "forged"),
                "--state",
                "PASS",
            ]
        )
    assert not (tmp_path / "forged").exists()
    assert "unrecognized arguments" in capsys.readouterr().err


def test_root_reload_detects_bound_output_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(checks.subprocess, "run", _fake_pytest())
    output = tmp_path.resolve() / "full-suite"
    run_v0_check("full_test_suite", output)
    stdout = output / "pytest.stdout.txt"
    os.chmod(stdout, 0o644)
    stdout.write_text("drifted output\n", encoding="utf-8")
    os.chmod(stdout, 0o444)

    with pytest.raises(Phase6V0CheckError, match="identity drifted"):
        validate_published_check_root(output, expected_check_id="full_test_suite")


def test_publication_failure_seals_partial_check_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path.resolve() / "failed-root"

    def fail_publish(path: Path, data: bytes) -> dict[str, object]:
        raise RuntimeError("injected trusted-check publication failure")

    monkeypatch.setattr(checks, "_publish_file", fail_publish)
    with pytest.raises(RuntimeError, match="injected trusted-check"):
        run_v0_check("stale_production_metadata", output)

    assert stat.S_IMODE(output.stat().st_mode) == 0o555
