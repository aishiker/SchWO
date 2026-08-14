from __future__ import annotations

from pathlib import Path
import re

import pytest

import schwgw.validation.phase6_release_preparation as release_preparation
from schwgw.validation.phase6_domain import source_file_identity
from schwgw.validation.phase6_v1_production_state_evidence import (
    publish_production_state_evidence,
    validate_production_state_sources,
    validate_published_production_state_evidence,
)


CAMPAIGN = Path(
    "runs/phase6/radial_validation/v1_production_finite_radius_campaign_v1_20260808_py314"
).absolute()
REPAIR = Path(
    "runs/phase6/radial_validation/v1_production_finite_radius_repair_diagnostic_v1_20260809_py314"
).absolute()


@pytest.mark.skipif(
    not CAMPAIGN.exists() or not REPAIR.exists(),
    reason="formal production sources are unavailable",
)
def test_production_state_composition_roundtrip(tmp_path) -> None:
    source = validate_production_state_sources(
        campaign_root=CAMPAIGN, repair_root=REPAIR
    )
    assert len(source["production_keys"]) == 16_048
    assert source["implementation_source_sha256s"]
    assert all(
        re.fullmatch(r"[0-9a-f]{64}", value)
        for value in source["implementation_source_sha256s"]
    )
    root = tmp_path / "production_states"
    report = publish_production_state_evidence(
        campaign_root=CAMPAIGN, repair_root=REPAIR, output_root=root
    )
    assert report["state"] == "PARTIAL"
    assert report["parameter_domain"]["expected_items"] == 16_048
    assert validate_published_production_state_evidence(root) == report
    artifacts = {
        path.name: source_file_identity(path)["sha256"]
        for path in sorted(root.iterdir())
    }
    release_source = {
        "adapter": "V1_PRODUCTION_STATE_EVIDENCE_V1",
        "evidence_id": "production_backend_repaired",
        "expected_artifacts": [
            {"relative_path": name, "sha256": digest}
            for name, digest in sorted(artifacts.items())
        ],
        "origin_root": str(root),
        "selector": {"projection": "generic_conditioning_backend"},
    }
    origin = release_preparation._load_origin(release_source)
    derived = release_preparation._derive_source(release_source, origin)
    assert derived.state == "PARTIAL"
    assert derived.expected_items == 16_048
    assert derived.native_domain["gate"] == "V1Q"
    assert derived.native_domain["observable"] == "generic_conditioning_backend"
