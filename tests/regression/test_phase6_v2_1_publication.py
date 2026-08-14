from __future__ import annotations

import json
from pathlib import Path

import pytest

from schwgw.validation.phase6_v2_mode_amplitudes import (
    build_v2_1_records,
    publish_v2_1_mode_amplitudes,
    validate_published_v2_1_mode_amplitudes,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = (
    PROJECT_ROOT / "runs/phase6/radial_validation/"
    "v1_radial_selected_acceptance_v1_20260810_py314"
)


@pytest.mark.skipif(not SOURCE_ROOT.exists(), reason="frozen V1 source unavailable")
def test_real_frozen_source_builds_exact_structural_inventory() -> None:
    bundle = build_v2_1_records(PROJECT_ROOT)
    assert len(bundle.records) == 120
    assert {record["m"] for record in bundle.records} == {-2, 2}
    assert {record["incident_column"]["column"] for record in bundle.records} == {
        "plus",
        "cross",
    }
    assert [record["record_ordinal"] for record in bundle.records] == list(range(120))
    assert all(
        record["total_free_scattered_identity"]["threshold"] is None
        and "complex_residual" in record["total_free_scattered_identity"]
        for record in bundle.records
    )
    high_ell_horizon = bundle.records[-1]["li_normalization"]["T_horizon_physical"]
    assert high_ell_horizon["abs"] != "0.0"


@pytest.mark.skipif(not SOURCE_ROOT.exists(), reason="frozen V1 source unavailable")
def test_exclusive_publication_and_independent_reload(tmp_path: Path) -> None:
    root = tmp_path / "v2_1_mode_amplitudes_v1_test_py314"
    report = publish_v2_1_mode_amplitudes(
        project_root=PROJECT_ROOT,
        output_root=root,
        verification={"commands": [], "stage": "TEST_FIXTURE"},
    )
    assert report["record_count"] == 120
    reloaded = validate_published_v2_1_mode_amplitudes(root)
    assert reloaded["summary"]["radial_solve_count"] == 0
    assert reloaded["summary"]["global_status"] is None
    assert reloaded["summary"]["global_green_permitted"] is False
    assert len(reloaded["records"]) == 120
    manifest = json.loads((root / "manifest.json").read_text())
    assert set(manifest["files"]) == {
        "records.jsonl",
        "report.json",
        "source_ledger.json",
        "summary.json",
    }
    with pytest.raises(FileExistsError):
        publish_v2_1_mode_amplitudes(
            project_root=PROJECT_ROOT,
            output_root=root,
            verification={"commands": [], "stage": "COLLISION_TEST"},
        )
