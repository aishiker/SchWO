from __future__ import annotations

from pathlib import Path

import mpmath as mp
import pytest

from schwgw.validation.phase6_v2_waveform_routes import (
    Phase6V22Error,
    publish_v2_2_waveform_routes,
    validate_published_v2_2_waveform_routes,
)


ROOT = Path(__file__).resolve().parents[2]
V21_ROOT = (
    ROOT / "runs/phase6/asymptotic_waveform/"
    "v2_1_mode_amplitudes_v1_20260810T184729_py314"
)
SUPERSEDED_V2_ROOT = (
    ROOT / "runs/phase6/asymptotic_waveform/"
    "v2_2_waveform_routes_v2_20260811T104500_py314"
)


@pytest.mark.skipif(not V21_ROOT.exists(), reason="accepted V2.1 root unavailable")
def test_v2_2_exclusive_publication_and_independent_reconstruction(
    tmp_path: Path,
) -> None:
    original_dps = mp.mp.dps
    try:
        mp.mp.dps = 15
        output = tmp_path / "v2_2_waveform_routes_v3_test_py314"
        report = publish_v2_2_waveform_routes(
            project_root=ROOT,
            output_root=output,
            verification={"commands": [], "stage": "TEST_FIXTURE"},
        )
        assert report["record_count"] == 120
        reloaded = validate_published_v2_2_waveform_routes(output, project_root=ROOT)
        assert mp.mp.dps == 15
        assert len(reloaded["records"]) == 120
        assert reloaded["source_anchored_reconstruction"] == {
            "ambient_dps_at_entry": 15,
            "external_S_l": 120,
            "pairwise_comparisons": 360,
            "route_C_coefficients": 120,
            "source": "original immutable external wp60 phase_factor decimal strings",
            "working_dps": 80,
        }
        assert reloaded["summary"]["selected_domain_comparator_state"] == "PASS"
        assert reloaded["summary"]["claim_status"] == "PARTIAL"
        assert reloaded["summary"]["absolute_phase"] == "PARTIAL"
        assert reloaded["summary"]["radial_solve_count"] == 0
        assert reloaded["summary"]["global_status"] is None
        with pytest.raises(FileExistsError):
            publish_v2_2_waveform_routes(
                project_root=ROOT,
                output_root=output,
                verification={"commands": [], "stage": "COLLISION_TEST"},
            )
    finally:
        mp.mp.dps = original_dps


@pytest.mark.skipif(not SUPERSEDED_V2_ROOT.exists(), reason="V2.2 v2 root unavailable")
def test_superseded_v2_root_fails_source_anchored_precision_reconstruction() -> None:
    original_dps = mp.mp.dps
    try:
        mp.mp.dps = 15
        with pytest.raises(
            Phase6V22Error,
            match="published external S_l is not source-anchored at 80 dps",
        ):
            validate_published_v2_2_waveform_routes(
                SUPERSEDED_V2_ROOT, project_root=ROOT
            )
    finally:
        mp.mp.dps = original_dps
