from __future__ import annotations

from io import BytesIO
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
from typing import NoReturn

import numpy as np
import pytest

import schwgw.io.tablei_risk_pilot as pilot
from schwgw.io.tablei_risk_pilot import (
    METADATA_SCHEMA_VERSION,
    PilotContractError,
    repair_delta0p1_risk_pilot_metadata,
)


_PROJECT_PACKAGE = Path("runs/phase5/fig5_fig6_delta0p1_risk_pilot")
_DURABLE_SOURCE = (
    _PROJECT_PACKAGE
    / "quarantine"
    / "t8ao_pre_units_metadata"
    / "source"
)


def _frozen_source() -> Path:
    source = _DURABLE_SOURCE if _DURABLE_SOURCE.is_dir() else _PROJECT_PACKAGE
    if not (source / "manifest.md").is_file():
        pytest.skip("frozen T8an package is unavailable")
    return source


def _copy_frozen_v1_package(tmp_path: Path) -> Path:
    source = _frozen_source()
    output = tmp_path / "risk_pilot"
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        if "quarantine" in relative.parts:
            continue
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
    return output


def _canonical_array_fingerprints(root: Path) -> dict[str, str]:
    paths = tuple(sorted((root / "frequencies").glob("*.npz"))) + (
        root / "risk_pilot_values.npz",
    )
    result: dict[str, str] = {}
    for path in paths:
        with np.load(path, allow_pickle=False) as data:
            for name in data.files:
                if name == "metadata_json":
                    continue
                stream = BytesIO()
                np.save(stream, data[name], allow_pickle=False)
                key = f"{path.relative_to(root)}::{name}"
                result[key] = hashlib.sha256(stream.getvalue()).hexdigest()
    return dict(sorted(result.items()))


def _assert_all_required_metadata_surfaces(root: Path) -> None:
    json_paths = tuple(sorted((root / "frequencies").glob("*.npz.json"))) + (
        root / "risk_pilot_values.npz.json",
        root / "checkpoint_ledger.json",
        root / "risk_pilot_sampling_audit.json",
    )
    for path in json_paths:
        value = json.loads(path.read_text(encoding="utf-8"))
        assert value["schema_version"] == METADATA_SCHEMA_VERSION
        assert value["units"] == pilot.UNITS_CONTRACT
        assert value["ordering"] == pilot.ORDERING_CONTRACT
        assert value["generation_contract_hash"] == pilot.GENERATION_CONTRACT_HASH
        assert value["metadata_contract_hash"]
    for path in tuple(sorted((root / "frequencies").glob("*.npz"))) + (
        root / "risk_pilot_values.npz",
    ):
        with np.load(path, allow_pickle=False) as data:
            value = json.loads(str(data["metadata_json"].item()))
        assert value["schema_version"] == METADATA_SCHEMA_VERSION
        assert value["units"] == pilot.UNITS_CONTRACT
        assert value["ordering"] == pilot.ORDERING_CONTRACT
    manifest = (root / "manifest.md").read_text(encoding="utf-8")
    assert "## Units" in manifest
    assert "## Ordering" in manifest


def test_metadata_repair_preserves_arrays_and_never_calls_science(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = _copy_frozen_v1_package(tmp_path)
    before = _canonical_array_fingerprints(output)

    def forbidden(*args: object, **kwargs: object) -> NoReturn:
        del args, kwargs
        raise AssertionError("scientific compute path called by metadata repair")

    monkeypatch.setattr(pilot, "compute_polarization", forbidden)
    monkeypatch.setattr(pilot, "compute_flat_no_lens_polarization", forbidden)
    monkeypatch.setattr(pilot, "solve_radial_mode", forbidden)
    monkeypatch.setattr(pilot, "_compute_frequency", forbidden)
    monkeypatch.setattr(pilot, "run_delta0p1_risk_pilot", forbidden)

    repaired = repair_delta0p1_risk_pilot_metadata(output_dir=output)
    assert repaired == output / "risk_pilot_values.npz"
    assert _canonical_array_fingerprints(output) == before
    _assert_all_required_metadata_surfaces(output)


def test_metadata_repair_stops_on_active_hash_mismatch(tmp_path: Path) -> None:
    output = _copy_frozen_v1_package(tmp_path)
    sidecar = output / "frequencies" / "kM_0p4.npz.json"
    sidecar.write_bytes(sidecar.read_bytes() + b" ")
    with pytest.raises(PilotContractError, match="pre-repair|manifest|hash"):
        repair_delta0p1_risk_pilot_metadata(output_dir=output)


def test_metadata_repair_stops_on_tampered_backup(tmp_path: Path) -> None:
    output = _copy_frozen_v1_package(tmp_path)
    repair_delta0p1_risk_pilot_metadata(output_dir=output)
    backup_manifest = (
        output
        / "quarantine"
        / "t8ao_pre_units_metadata"
        / "source"
        / "manifest.md"
    )
    backup_manifest.write_bytes(backup_manifest.read_bytes() + b"tampered")
    with pytest.raises(PilotContractError, match="backup|source|hash"):
        repair_delta0p1_risk_pilot_metadata(output_dir=output)


def test_metadata_repair_resumes_a_mixed_active_tree(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = _copy_frozen_v1_package(tmp_path)
    before = _canonical_array_fingerprints(output)
    real_replace = os.replace
    active_replacements = 0

    def interrupt(source: str | Path, destination: str | Path) -> None:
        nonlocal active_replacements
        source_path = Path(source)
        destination_path = Path(destination)
        if (
            source_path.name.endswith(".t8ao-install.tmp")
            and output in destination_path.parents
        ):
            active_replacements += 1
            if active_replacements == 5:
                raise OSError("synthetic T8ao interruption")
        real_replace(source, destination)

    monkeypatch.setattr(pilot.os, "replace", interrupt)
    with pytest.raises(OSError, match="synthetic T8ao interruption"):
        repair_delta0p1_risk_pilot_metadata(output_dir=output)
    monkeypatch.setattr(pilot.os, "replace", real_replace)

    repair_delta0p1_risk_pilot_metadata(output_dir=output)
    assert _canonical_array_fingerprints(output) == before
    _assert_all_required_metadata_surfaces(output)


def test_metadata_repair_rejects_units_or_ordering_drift(tmp_path: Path) -> None:
    output = _copy_frozen_v1_package(tmp_path)
    repair_delta0p1_risk_pilot_metadata(output_dir=output)
    candidate = (
        output
        / "quarantine"
        / "t8ao_pre_units_metadata"
        / "candidate"
        / "risk_pilot_sampling_audit.json"
    )
    value = json.loads(candidate.read_text(encoding="utf-8"))
    value["ordering"]["frequency_order"] = list(reversed(pilot.PILOT_FREQUENCIES))
    candidate.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
    with pytest.raises(PilotContractError, match="candidate|ordering|hash"):
        repair_delta0p1_risk_pilot_metadata(output_dir=output)


def test_scientific_runner_rejects_a_metadata_repaired_package(
    tmp_path: Path,
) -> None:
    output = _copy_frozen_v1_package(tmp_path)
    repair_delta0p1_risk_pilot_metadata(output_dir=output)
    with pytest.raises(PilotContractError, match="metadata-repaired package"):
        pilot.run_delta0p1_risk_pilot(output_dir=output, resume=True)


def test_metadata_repair_script_has_metadata_only_scope() -> None:
    path = Path("scripts/phase5_repair_delta0p1_risk_pilot_metadata.py")
    text = path.read_text(encoding="utf-8")
    assert "repair_delta0p1_risk_pilot_metadata" in text
    assert "--output-dir" in text
    for forbidden in (
        "run_delta0p1_risk_pilot",
        "compute_polarization",
        "solve_radial_mode",
        "schwgw.viz",
        "kirchhoff",
        "--frequency",
    ):
        assert forbidden not in text.lower()


def test_metadata_repair_script_passes_only_output_dir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = Path("scripts/phase5_repair_delta0p1_risk_pilot_metadata.py")
    spec = importlib.util.spec_from_file_location("phase5_t8ao_metadata_repair", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    received: dict[str, object] = {}

    def fake_repair(**kwargs: object) -> Path:
        received.update(kwargs)
        return tmp_path / "risk_pilot_values.npz"

    monkeypatch.setattr(module, "repair_delta0p1_risk_pilot_metadata", fake_repair)
    output = tmp_path / "risk_pilot"
    assert module.main(["--output-dir", str(output)]) == 0
    assert received == {"output_dir": output}
