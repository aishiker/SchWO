from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from schwgw.validation import phase6_v2_selected_release as release


PROJECT = Path(__file__).resolve().parents[2]
V1_ROOT = (
    PROJECT
    / "runs/phase6/asymptotic_waveform"
    / "v2_selected_release_v1_20260811T081608_py314"
)


def test_check_only_cli_reconstructs_twelve_certificates() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT / "scripts/phase6_v2_4_publish_selected_release.py"),
            "check-only",
            "--project-root",
            str(PROJECT),
        ],
        cwd=PROJECT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    payload = json.loads(result.stdout)
    assert payload["certificate_count"] == 12
    assert payload["certificate_state_counts"] == {
        "FAIL": 0,
        "NOT_ASSESSED": 0,
        "PARTIAL": 1,
        "PASS": 11,
    }
    assert payload["global_status"] is None
    assert payload["radial_solve_count"] == 0


def test_exclusive_writer_and_file_creation_are_fail_closed(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    with release._exclusive_writer(root):
        release._write_exclusive(root / "one.json", b"{}\n")
        with pytest.raises(FileExistsError):
            release._write_exclusive(root / "one.json", b"{}\n")
    assert (root / "one.json").read_bytes() == b"{}\n"


def test_manifest_detects_artifact_tamper(tmp_path) -> None:
    root = tmp_path / "release"
    root.mkdir()
    names = ("release_ledger.json", "source_map.json", "summary.json", "report.json")
    for name in names:
        (root / name).write_bytes(b"{}\n")
    manifest = release._release_manifest(root, names)
    release._write_exclusive(
        root / "manifest.json", release.canonical_json_bytes(manifest)
    )
    release._validate_manifest(root)
    (root / "summary.json").write_bytes(b'{"tampered":true}\n')
    with pytest.raises(Exception, match="manifest"):
        release._validate_manifest(root)


def test_historical_read_only_rebuild_survives_live_handoff_advance(
    monkeypatch,
) -> None:
    monkeypatch.setattr(release, "DISPATCH_T7_SHA256", "0" * 64)
    with pytest.raises(release.Phase6V24Error, match="dispatch T7 handoff"):
        release.verify_release_inputs(PROJECT)
    gate = release.verify_release_inputs(
        PROJECT, require_dispatch_review_identity=False
    )
    assert len(release.build_release_ledger(gate)["certificates"]) == 12


def test_publish_path_keeps_dispatch_identity_gate_enabled(monkeypatch) -> None:
    def strict_probe(
        project_root: Path,
        *,
        require_dispatch_review_identity: bool = True,
    ) -> None:
        assert project_root == PROJECT
        assert require_dispatch_review_identity is True
        raise release.Phase6V24Error("strict publish gate probe")

    monkeypatch.setattr(release, "verify_release_inputs", strict_probe)
    output = (
        PROJECT
        / "runs/phase6/asymptotic_waveform"
        / "v2_selected_release_v2_control_plane_gate_probe_py314"
    )
    assert not output.exists()
    with pytest.raises(release.Phase6V24Error, match="strict publish gate probe"):
        release.publish_selected_release(PROJECT, output, verification={})
    assert not output.exists()


def test_v1_release_remains_immutable_and_natively_reloadable() -> None:
    bundle = release.validate_published_selected_release(V1_ROOT, PROJECT)
    assert bundle["summary"]["certificate_count"] == 12
    assert bundle["summary"]["global_status"] is None
    gate = release.verify_release_inputs(
        PROJECT, require_dispatch_review_identity=False
    )
    ledger = release.build_release_ledger(gate)
    summary = release.build_release_summary(ledger)
    assert (
        release.canonical_json_bytes(ledger)
        == (V1_ROOT / "release_ledger.json").read_bytes()
    )
    assert (
        release.canonical_json_bytes(summary) == (V1_ROOT / "summary.json").read_bytes()
    )
