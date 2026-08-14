from __future__ import annotations

from pathlib import Path

import pytest

from schwgw.validation.phase6_v1_ap_selected_evidence import (
    publish_ap_selected_evidence,
    validate_ap_selected_source,
    validate_published_ap_selected_evidence,
)


SOURCE = Path(
    "runs/phase6/radial_validation/ap_radial_repair_selected_24_v1_20260809_py314"
).absolute()


@pytest.mark.skipif(not SOURCE.exists(), reason="formal AP source is unavailable")
def test_ap_selected_source_and_wrapper_roundtrip(tmp_path) -> None:
    source = validate_ap_selected_source(SOURCE)
    assert len(source["anchors"]) == 24
    root = tmp_path / "ap_wrapper"
    report = publish_ap_selected_evidence(source_root=SOURCE, output_root=root)
    assert report["state"] == "PARTIAL"
    assert report["parameter_domain"]["expected_items"] == 24
    assert (
        report["numerical_uncertainty_budget"]["arithmetic_precision"]["state"]
        == "PASS"
    )
    assert validate_published_ap_selected_evidence(root) == report
