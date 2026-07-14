from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from schwgw.io.results import AmplificationGridResult, save_amplification_results
from schwgw.io.tablei import (
    TableIPoint,
    extract_tablei_four_frequency_from_amplification_results,
)


def test_tablei_extraction_writes_npz_and_sidecar_with_exact_zx_indexing(tmp_path):
    source_paths = _save_sources(tmp_path)
    points = [
        TableIPoint(
            point_id="p0",
            group="near_axis",
            x=0.0,
            y=0.0,
            z=1.0,
            paper_theta_deg=0.0,
            paper_xi_over_xi0=0.0,
            x_index=1,
            z_index=2,
        ),
        TableIPoint(
            point_id="p1",
            group="far_axis",
            x=2.0,
            y=0.0,
            z=1.0,
            paper_theta_deg=63.4349,
            paper_xi_over_xi0=1.0,
            x_index=3,
            z_index=2,
        ),
    ]
    output_path = tmp_path / "tablei.npz"

    sidecar = extract_tablei_four_frequency_from_amplification_results(
        source_paths,
        output_path=output_path,
        points=points,
    )

    assert sidecar == output_path.with_suffix(output_path.suffix + ".json")
    with np.load(output_path, allow_pickle=False) as data:
        assert data["F_plus_complex"].shape == (4, 2)
        assert data["F_cross_complex"].shape == (4, 2)
        assert data["point_ids"].tolist() == ["p0", "p1"]
        assert data["point_group"].tolist() == ["near_axis", "far_axis"]
        assert data["x_indices"].tolist() == [1, 3]
        assert data["z_indices"].tolist() == [2, 2]
        # This proves extraction uses source arrays as [z_index, x_index].
        assert data["F_plus_complex"][0, 0] == _plus_value(0.5, z_index=2, x_index=1)
        assert data["F_plus_complex"][0, 1] == _plus_value(0.5, z_index=2, x_index=3)
        assert data["valid_ratio_plus_mask"].dtype == np.bool_
        assert data["source_valid_mask"].all()
        assert data["valid_field_mask"].all()
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["case_id"] == "FIG5_FIG6_TABLEI_FOUR_FREQUENCY_READONLY"
    assert metadata["array_axis_order"] == "ratio_arrays_indexed_as_z_then_x_before_extraction"
    assert metadata["extraction_array_shape"] == [4, 2]
    assert metadata["no_interpolation"] is True
    assert metadata["no_solver_rerun"] is True
    assert metadata["no_kirchhoff_baseline"] is True
    assert metadata["not_paper_level_dense_scan"] is True
    assert metadata["no_kM4"] is True


def test_tablei_extraction_preserves_masks_nans_and_unwrap_gaps(tmp_path):
    source_paths = _save_sources(tmp_path, invalid_frequency_index=1)
    points = [
        TableIPoint(
            point_id="p0",
            group="near_axis",
            x=0.0,
            y=0.0,
            z=1.0,
            paper_theta_deg=0.0,
            paper_xi_over_xi0=0.0,
            x_index=1,
            z_index=2,
        )
    ]
    output_path = tmp_path / "tablei.npz"

    extract_tablei_four_frequency_from_amplification_results(
        source_paths,
        output_path=output_path,
        points=points,
    )

    with np.load(output_path, allow_pickle=False) as data:
        assert data["valid_ratio_cross_mask"][:, 0].tolist() == [
            True,
            False,
            True,
            True,
        ]
        assert np.isnan(data["F_cross_complex"][1, 0].real)
        assert np.isnan(data["F_cross_complex"][1, 0].imag)
        assert np.isnan(data["arg_F_cross_principal"][1, 0])
        assert np.isnan(data["arg_F_cross_unwrapped"][1, 0])
        expected_second_segment = np.unwrap(data["arg_F_cross_principal"][2:, 0])
        np.testing.assert_allclose(
            data["arg_F_cross_unwrapped"][2:, 0],
            expected_second_segment,
        )


def test_tablei_extraction_rejects_coordinate_mismatch_without_interpolation(tmp_path):
    source_paths = _save_sources(tmp_path)
    points = [
        TableIPoint(
            point_id="off_grid",
            group="near_axis",
            x=0.25,
            y=0.0,
            z=1.0,
            paper_theta_deg=0.0,
            paper_xi_over_xi0=0.0,
            x_index=1,
            z_index=2,
        )
    ]

    with pytest.raises(ValueError, match="does not match requested x"):
        extract_tablei_four_frequency_from_amplification_results(
            source_paths,
            output_path=tmp_path / "bad.npz",
            points=points,
        )


def test_tablei_extraction_rejects_wrong_frequency_order(tmp_path):
    source_paths = _save_sources(tmp_path)
    source_paths[1], source_paths[2] = source_paths[2], source_paths[1]

    with pytest.raises(ValueError, match="in increasing kM order"):
        extract_tablei_four_frequency_from_amplification_results(
            source_paths,
            output_path=tmp_path / "bad.npz",
            points=[
                TableIPoint(
                    point_id="p0",
                    group="near_axis",
                    x=0.0,
                    y=0.0,
                    z=1.0,
                    paper_theta_deg=0.0,
                    paper_xi_over_xi0=0.0,
                    x_index=1,
                    z_index=2,
                )
            ],
        )


def _save_sources(tmp_path, *, invalid_frequency_index: int | None = None) -> list[Path]:
    paths = []
    for index, kM in enumerate([0.5, 1.0, 1.5, 2.0]):
        path = tmp_path / f"k{kM:g}.npz"
        result = _synthetic_amplification_result(
            kM,
            invalid_cross=index == invalid_frequency_index,
        )
        save_amplification_results(result, path)
        paths.append(path)
    return paths


def _synthetic_amplification_result(kM: float, *, invalid_cross: bool = False):
    x = np.array([-1.0, 0.0, 1.0, 2.0])
    z = np.array([-1.0, 0.0, 1.0])
    shape = (z.size, x.size)
    f_plus = np.empty(shape, dtype=np.complex128)
    f_cross = np.empty(shape, dtype=np.complex128)
    for z_index in range(z.size):
        for x_index in range(x.size):
            f_plus[z_index, x_index] = _plus_value(kM, z_index, x_index)
            f_cross[z_index, x_index] = np.exp(1j * (2.5 + 0.7 * kM + 0.1 * x_index))
    valid_plus = np.ones(shape, dtype=bool)
    valid_cross = np.ones(shape, dtype=bool)
    valid_norm = np.ones(shape, dtype=bool)
    valid_mask = np.ones(shape, dtype=bool)
    if invalid_cross:
        f_cross[2, 1] = np.nan + 1j * np.nan
        valid_cross[2, 1] = False
    return AmplificationGridResult(
        theta=np.zeros(shape),
        phi=np.zeros(shape),
        F_plus_complex=f_plus,
        F_cross_complex=f_cross,
        amplification_plus=np.abs(f_plus),
        amplification_cross=np.abs(f_cross),
        intensity_plus_ratio=np.abs(f_plus) ** 2,
        intensity_cross_ratio=np.abs(f_cross) ** 2,
        F_pol_norm=np.ones(shape),
        I_pol_ratio=np.ones(shape),
        valid_ratio_plus_mask=valid_plus,
        valid_ratio_cross_mask=valid_cross,
        valid_ratio_norm_mask=valid_norm,
        metadata={
            "case_id": f"SYNTH_K{kM:g}",
            "k": kM,
            "lmax": int(80 + 10 * kM),
            "normalization": {
                "kind": "pointwise_wave_optics_amplification",
                "baseline_api": "compute_flat_no_lens_polarization",
                "incident_direction": "+z",
                "fourier": "exp(-i k t)",
                "polarization_bridge": (
                    "Route B incident-frame electric tidal packaged scalars"
                ),
            },
            "source_lensed_result_path": f"source_k{kM:g}.npz",
            "source_lensed_size_bytes": 1000 + int(10 * kM),
            "source_lensed_sha256": f"sha{kM:g}",
            "source_q018_warning_count": 0,
            "source_q018_warning_codes": [],
        },
        x=x,
        z=z,
        r=np.ones(shape),
        valid_mask=valid_mask,
    )


def _plus_value(kM: float, z_index: int, x_index: int) -> complex:
    return complex(100.0 * kM + 10.0 * z_index + x_index, -x_index)
