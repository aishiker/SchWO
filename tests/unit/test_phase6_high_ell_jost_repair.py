from __future__ import annotations

import json
from pathlib import Path

from schwgw.validation.phase6_high_ell_jost_repair import (
    DEFAULT_BOUNDARY_ROOT,
    EXPECTED_REPAIR_KEY_COUNT,
    build_repair_report,
    derive_repair_record,
)

RUNNER = Path("scripts/phase6_publish_high_ell_jost_repair.py").resolve(strict=True)


def _residual_source(key_id: str) -> dict[str, object]:
    path = DEFAULT_BOUNDARY_ROOT / "records.jsonl"
    for raw in path.read_text(encoding="utf-8").splitlines():
        record = json.loads(raw)
        if record["key_id"] == key_id:
            return record
    raise AssertionError(f"missing frozen residual source {key_id}")


def test_worst_key_is_repaired_by_generic_radius_and_jost_ladders() -> None:
    records_path = DEFAULT_BOUNDARY_ROOT / "records.jsonl"
    record = derive_repair_record(
        _residual_source("kM=8;sector=odd;ell=720"),
        source_records_sha256=__import__("hashlib")
        .sha256(records_path.read_bytes())
        .hexdigest(),
    )

    assert record["adaptive_selection"]["selected_radius_factor"] == 4.0
    assert record["adaptive_selection"]["selected_r_out_M"] == 1200.0
    assert record["radius_ladder"]["state"] == "PASS"
    assert record["jost_order_ladder"]["state"] == "PASS"
    assert record["numerical_uncertainty_budget"]["state"] == "PASS"
    assert record["convention_uncertainty_budget"]["state"] == "NOT_ASSESSED"
    assert record["algorithmic_failure_repaired"] is True
    assert record["overall_state"] == "PARTIAL"
    assert record["scientific_acceptance"] is False
    assert record["global_green_permitted"] is False


def test_full_report_closes_all_230_algorithmic_failures_without_green() -> None:
    report = build_repair_report(
        boundary_root=DEFAULT_BOUNDARY_ROOT,
        runner_path=RUNNER,
    )

    assert report["aggregate"]["key_count"] == EXPECTED_REPAIR_KEY_COUNT
    assert report["aggregate"]["algorithmic_failure_repaired_count"] == 230
    assert report["aggregate"]["numerical_failure_count"] == 0
    assert report["aggregate"]["selected_radius_factor_counts"] == {
        "2.0": 218,
        "4.0": 12,
    }
    assert report["aggregate"]["state_counts"] == {"PARTIAL": 230}
    assert report["numerical_uncertainty_budget"]["state"] == "PASS"
    assert report["convention_uncertainty_budget"]["state"] == "NOT_ASSESSED"
    assert report["overall_state"] == "PARTIAL"
    assert report["independent_scientific_validation"] is False
    assert report["scientific_acceptance"] is False
    assert report["global_green_permitted"] is False
