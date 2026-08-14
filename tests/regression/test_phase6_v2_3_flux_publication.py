from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from schwgw.validation import phase6_v2_flux_closure as flux
from schwgw.validation.phase6_v2_mode_amplitudes import canonical_json_bytes


PROJECT = Path(__file__).resolve().parents[2]


def test_check_only_cli_reconstructs_120_without_radial_solve() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(PROJECT / "scripts/phase6_v2_3_publish_flux_closure.py"),
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
    payload = json.loads(completed.stdout)
    assert payload["record_count"] == 120
    assert payload["mandatory_predicates_passed"] is True
    assert payload["radial_solve_count"] == 0
    assert payload["working_dps"] == 100


def _mini_sealed_root(tmp_path: Path) -> Path:
    root = tmp_path / "v2_3_flux_closure_v1_test_py314"
    root.mkdir(mode=0o700)
    names = ("records.jsonl", "summary.json", "report.json", "source_ledger.json")
    for name in names:
        (root / name).write_bytes(canonical_json_bytes({"name": name}))
    manifest = flux._manifest(root, names)
    (root / "manifest.json").write_bytes(canonical_json_bytes(manifest))
    flux._seal(root)
    return root


def test_exclusive_writer_and_sealing(tmp_path: Path) -> None:
    root = tmp_path / "writer"
    root.mkdir()
    path = root / "one.json"
    with flux._exclusive_writer(root):
        assert (root / ".writer.lock").is_file()
        with pytest.raises(FileExistsError):
            with flux._exclusive_writer(root):
                pass
        flux._write_exclusive(path, b"{}\n")
        with pytest.raises(FileExistsError):
            flux._write_exclusive(path, b"{}\n")
    assert not (root / ".writer.lock").exists()
    flux._seal(root)
    assert stat.S_IMODE(root.stat().st_mode) == 0o555
    assert stat.S_IMODE(path.stat().st_mode) == 0o444


def test_manifest_tamper_is_detected(tmp_path: Path) -> None:
    root = _mini_sealed_root(tmp_path)
    (root / "summary.json").chmod(0o644)
    (root / "summary.json").write_bytes(b'{"tampered":true}\n')
    (root / "summary.json").chmod(0o444)
    with pytest.raises(flux.Phase6V23Error, match="manifest identity mismatch"):
        flux._validate_manifest(root)


def test_frozen_source_gate_rejects_identity_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    identities = dict(flux.FROZEN_IDENTITIES)
    first = next(iter(identities))
    identities[first] = "0" * 64
    monkeypatch.setattr(flux, "FROZEN_IDENTITIES", identities)
    with pytest.raises(flux.Phase6V23Error, match="frozen input identity mismatch"):
        flux.verify_frozen_v2_3_inputs(PROJECT)


def test_historical_reload_allows_handoff_advance_but_publish_gate_stays_strict() -> (
    None
):
    with pytest.raises(flux.Phase6V23Error, match="dispatch T7 handoff identity"):
        flux.verify_frozen_v2_3_inputs(PROJECT)
    gate = flux.verify_frozen_v2_3_inputs(
        PROJECT, require_dispatch_review_identity=False
    )
    assert gate.t7_identity["sha256"] != flux.DISPATCH_T7_SHA256


def test_publish_path_keeps_dispatch_identity_gate_enabled(monkeypatch) -> None:
    def strict_probe(
        project_root: Path,
        *,
        require_dispatch_review_identity: bool = True,
    ) -> None:
        assert project_root == PROJECT
        assert require_dispatch_review_identity is True
        raise flux.Phase6V23Error("strict publish gate probe")

    monkeypatch.setattr(flux, "build_v2_3_flux_closure_records", strict_probe)
    output = (
        PROJECT
        / "runs/phase6/asymptotic_waveform"
        / "v2_3_flux_closure_v2_control_plane_gate_probe_py314"
    )
    assert not output.exists()
    with pytest.raises(flux.Phase6V23Error, match="strict publish gate probe"):
        flux.publish_v2_3_flux_closure(PROJECT, output, verification={})
    assert not output.exists()
