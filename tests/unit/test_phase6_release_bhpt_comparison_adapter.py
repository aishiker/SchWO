from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path

import pytest

import schwgw.validation.phase6_bhpt_direct_comparison as native_comparison
from schwgw.validation.phase6_bhpt_direct_comparison import build_typed_report
from schwgw.validation.phase6_domain import canonical_json_bytes
from schwgw.validation.phase6_release import direct_file_identity
from schwgw.validation.phase6_release_preparation import (
    Phase6PreparationError,
    preflight_release_map,
    prepare_release_map,
)
from tests.unit.test_phase6_bhpt_direct_comparison import _comparison_payload
from tests.unit.test_phase6_release_preparation import (
    _base_map,
    _certificate,
    _source,
)


def _write_immutable(path: Path, payload: object) -> None:
    path.write_bytes(canonical_json_bytes(payload))
    os.chmod(path, 0o444)


def _comparison_root(
    tmp_path: Path,
) -> tuple[Path, dict[str, str], dict[str, object]]:
    root = tmp_path.resolve()
    root.mkdir(parents=True)
    comparison = _comparison_payload()
    comparison_path = root / "comparison.json"
    _write_immutable(comparison_path, comparison)
    os.chmod(root, 0o555)
    comparison_identity = direct_file_identity(comparison_path)
    os.chmod(root, 0o755)
    report = build_typed_report(
        comparison,
        comparison_sha256=str(comparison_identity["sha256"]),
    )
    report_path = root / "report.json"
    _write_immutable(report_path, report)
    os.chmod(root, 0o555)
    report_identity = direct_file_identity(report_path)
    os.chmod(root, 0o755)
    manifest = {
        "comparison_identity": comparison_identity,
        "comparison_status_counts": {
            "FAIL": 6,
            "NOT_ASSESSED": 0,
            "PARTIAL": 24,
            "PASS": 0,
        },
        "created_at_utc": "2026-08-08T00:00:00+00:00",
        "global_green_permitted": False,
        "key_count": 30,
        "li_figure_agreement_primary_gate": False,
        "overall_state": "FAIL",
        "release_projection": deepcopy(comparison["release_projection"]),
        "report_identity": report_identity,
        "schema": native_comparison.MANIFEST_SCHEMA,
        "source_role_ledger": deepcopy(comparison["source_role_ledger"]),
        "status": "COMPLETE_WITH_INTERNAL_SCIENTIFIC_FAILURES",
    }
    manifest_path = root / "manifest.json"
    _write_immutable(manifest_path, manifest)
    os.chmod(root, 0o555)
    artifacts = {
        name: str(direct_file_identity(root / name)["sha256"])
        for name in ("comparison.json", "manifest.json", "report.json")
    }
    return root, artifacts, report


def _comparison_map(
    root: Path,
    artifacts: dict[str, str],
    report: dict[str, object],
    *,
    adapter: str = "BHPT_DIRECT_COMPARISON_V1",
) -> dict[str, object]:
    release_map = _base_map()
    certificate = _certificate(release_map, "V1", "radial_s_matrix_flux")
    native_domain = report["parameter_domain"]
    assert isinstance(native_domain, dict)
    certificate["parameter_domain"] = {
        name: deepcopy(native_domain[name])
        for name in (
            "domain_id",
            "description",
            "parameters",
            "selection_policy",
            "expected_items",
        )
    }
    certificate["evidence_ids"] = ["bhpt_direct_comparison"]
    release_map["sources"] = [
        _source(
            "bhpt_direct_comparison",
            adapter,
            root,
            artifacts,
        )
    ]
    return release_map


def test_dedicated_comparison_adapter_binds_three_files_and_source_roles(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, artifacts, report = _comparison_root(tmp_path / "comparison")
    validated: list[Path] = []
    monkeypatch.setattr(
        native_comparison,
        "validate_published_bhpt_conditioned_comparison",
        lambda path: validated.append(Path(path)),
    )
    release_map = _comparison_map(root, artifacts, report)

    plan = prepare_release_map(release_map)
    preflight = preflight_release_map(release_map)
    derived = plan.sources["bhpt_direct_comparison"][0]

    assert validated == [root, root]
    assert derived.adapter == "BHPT_DIRECT_COMPARISON_V1"
    assert derived.state == "FAIL"
    assert derived.role == "INDEPENDENT_SCIENCE"
    assert derived.independence_class == "EXTERNAL_SOURCE"
    assert derived.expected_items == derived.assessed_items == 30
    assert derived.native_summary["native_item_state_counts"] == {
        "NOT_ASSESSED": 0,
        "PARTIAL": 24,
        "PASS": 0,
        "FAIL": 6,
    }
    assert "external_source_evidence" in derived.native_summary
    assert "internal_source_evidence" in derived.native_summary
    assert preflight["certificate_states"]["cert_v1_radial_s_matrix_flux"] == "FAIL"


def test_comparison_report_copy_cannot_bypass_native_detail_and_manifest(
    tmp_path: Path,
) -> None:
    _, _, report = _comparison_root(tmp_path / "comparison")
    copied = tmp_path.resolve() / "report-only"
    copied.mkdir()
    _write_immutable(copied / "report.json", report)
    os.chmod(copied, 0o555)
    artifacts = {
        "report.json": str(direct_file_identity(copied / "report.json")["sha256"])
    }
    release_map = _comparison_map(
        copied,
        artifacts,
        report,
        adapter="TYPED_PHYSICAL_RESULT_V1",
    )

    with pytest.raises(Phase6PreparationError, match="dedicated three-file adapter"):
        preflight_release_map(release_map)


def test_comparison_manifest_source_role_tamper_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, artifacts, report = _comparison_root(tmp_path / "comparison")
    monkeypatch.setattr(
        native_comparison,
        "validate_published_bhpt_conditioned_comparison",
        lambda path: None,
    )
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["source_role_ledger"]["external_bhpt_direct"]["evidence_role"] = (
        "PRIMARY_PROJECT_AMPLITUDE"
    )
    os.chmod(root, 0o755)
    os.chmod(manifest_path, 0o644)
    _write_immutable(manifest_path, manifest)
    os.chmod(root, 0o555)
    artifacts["manifest.json"] = str(direct_file_identity(manifest_path)["sha256"])
    release_map = _comparison_map(root, artifacts, report)

    with pytest.raises(Phase6PreparationError, match="linkage changed"):
        preflight_release_map(release_map)
