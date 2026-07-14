from __future__ import annotations

import json
import math
import hashlib
from pathlib import Path

import numpy as np
import pytest

from schwgw.io.results import (
    AmplificationGridResult,
    GridResult,
    save_amplification_results,
    save_results,
)
from schwgw.viz.results import (
    PlotError,
    _amplification_quantity_values,
    plot_amplification_from_result,
    plot_convergence_from_result,
    plot_fig3_multifrequency_panel_from_results,
    plot_fig3_panel_from_result,
    plot_fig4_all_frequency_exact_angular_from_results,
    plot_fig4_exact_angular_from_result,
    plot_tablei_four_frequency_report,
    plot_wavefield_from_result,
)


def test_plot_wavefield_writes_png_and_sidecar_for_2d_result(tmp_path):
    result_path = tmp_path / "result.npz"
    output_path = tmp_path / "hplus_real.png"
    save_results(_synthetic_result(), result_path)

    sidecar = plot_wavefield_from_result(
        result_path,
        component="h_plus",
        quantity="real",
        output_path=output_path,
    )

    assert output_path.read_bytes().startswith(b"\x89PNG")
    assert output_path.stat().st_size > 1000
    assert sidecar == output_path.with_suffix(output_path.suffix + ".json")
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["source_result_path"] == str(result_path)
    assert metadata["component"] == "h_plus"
    assert metadata["quantity"] == "real"
    assert metadata["case_id"] == "SYNTH"
    assert metadata["kM"] == 1.0
    assert metadata["observer_r"] == 60.0
    assert metadata["lmax"] == 2
    assert metadata["source_result_created_at"] == "2026-07-05T00:00:00+00:00"


def test_plot_wavefield_handles_single_point_smoke_result(tmp_path):
    result_path = tmp_path / "single.npz"
    output_path = tmp_path / "single.png"
    result = _synthetic_result(
        theta=np.array([0.0]),
        phi=np.array([0.0]),
        h_plus=np.array([[1.0 + 2.0j]], dtype=np.complex128),
    )
    save_results(result, result_path)

    plot_wavefield_from_result(
        result_path,
        component="h_cross",
        quantity="abs",
        output_path=output_path,
    )

    assert output_path.read_bytes().startswith(b"\x89PNG")
    assert output_path.with_suffix(".png.json").exists()


def test_plot_wavefield_writes_xz_plane_png_and_sidecar(tmp_path):
    result_path = tmp_path / "xz_result.npz"
    output_path = tmp_path / "xz_hplus_abs.png"
    save_results(_synthetic_xz_result(), result_path)

    sidecar = plot_wavefield_from_result(
        result_path,
        component="h_plus",
        quantity="abs",
        output_path=output_path,
    )

    assert output_path.read_bytes().startswith(b"\x89PNG")
    assert output_path.stat().st_size > 1000
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["source_result_path"] == str(result_path)
    assert metadata["grid_kind"] == "xz_plane"
    assert metadata["x_range"] == [-1.0, 3.0]
    assert metadata["z_range"] == [0.0, 4.0]
    assert metadata["valid_point_count"] == 4
    assert metadata["invalid_point_count"] == 2
    assert metadata["component"] == "h_plus"
    assert metadata["quantity"] == "abs"


def test_plot_fig3_panel_writes_png_and_sidecar_from_xz_result(tmp_path):
    result_path = tmp_path / "xz_result.npz"
    output_path = tmp_path / "fig3_panel.png"
    save_results(_synthetic_xz_result(), result_path)

    sidecar = plot_fig3_panel_from_result(
        result_path,
        quantity="real",
        output_path=output_path,
    )

    assert output_path.read_bytes().startswith(b"\x89PNG")
    assert output_path.stat().st_size > 1000
    assert sidecar == output_path.with_suffix(output_path.suffix + ".json")
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["source_result_path"] == str(result_path)
    assert metadata["case_id"] == "SYNTH_XZ"
    assert metadata["plot_type"] == "fig3_lite_panel"
    assert metadata["grid_kind"] == "xz_plane"
    assert metadata["quantity"] == "real"
    assert metadata["components"] == ["h_plus", "h_cross"]
    assert metadata["kM"] == 1.0
    assert metadata["lmax"] == 2
    assert metadata["requested_dpi"] == 180
    assert metadata["output_format"] == "png"
    assert metadata["final_lmax_pair"] == [1, 2]
    assert metadata["final_pair_passed"] is True
    assert metadata["x_range"] == [-1.0, 3.0]
    assert metadata["z_range"] == [0.0, 4.0]
    assert metadata["valid_point_count"] == 4
    assert metadata["invalid_point_count"] == 2
    assert metadata["symmetric_color_scale"] is True
    assert np.isfinite(metadata["color_vmin"])
    assert np.isfinite(metadata["color_vmax"])
    assert metadata["color_vmin"] == -metadata["color_vmax"]
    assert metadata["overlays"] == {
        "drawn": True,
        "event_horizon_radius": 2.0,
        "light_ring_radius": 3.0,
    }
    assert metadata["convention"] == {"fourier": "exp(-i k t)", "units": "G=c=M=1"}


def test_plot_fig3_panel_records_interpolation_grid_spacing_and_sampling(tmp_path):
    result_path = tmp_path / "uniform_xz_result.npz"
    output_path = tmp_path / "fig3_panel.png"
    save_results(_synthetic_uniform_xz_result(), result_path)

    sidecar = plot_fig3_panel_from_result(
        result_path,
        quantity="real",
        output_path=output_path,
    )

    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["interpolation"] == "nearest"
    assert metadata["grid_spacing"] == {"x": 1.0, "z": 1.0}
    assert metadata["samples_per_wavelength"]["wavelength_over_M"] == pytest.approx(
        2.0 * math.pi
    )
    assert metadata["samples_per_wavelength"]["x"] == pytest.approx(2.0 * math.pi)
    assert metadata["samples_per_wavelength"]["z"] == pytest.approx(2.0 * math.pi)


def test_plot_fig3_panel_accepts_publication_dpi(tmp_path):
    result_path = tmp_path / "uniform_xz_result.npz"
    output_path = tmp_path / "fig3_panel_300dpi.png"
    save_results(_synthetic_uniform_xz_result(), result_path)

    sidecar = plot_fig3_panel_from_result(
        result_path,
        quantity="real",
        output_path=output_path,
        dpi=300,
    )

    assert output_path.read_bytes().startswith(b"\x89PNG")
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["requested_dpi"] == 300
    assert metadata["output_format"] == "png"


def test_plot_fig3_multifrequency_panel_writes_png_and_sidecar(tmp_path):
    result_paths = _save_multifrequency_results(tmp_path)
    output_path = tmp_path / "fig3_multifrequency.png"

    sidecar = plot_fig3_multifrequency_panel_from_results(
        result_paths,
        quantity="real",
        output_path=output_path,
    )

    assert output_path.read_bytes().startswith(b"\x89PNG")
    assert output_path.stat().st_size > 1000
    assert sidecar == output_path.with_suffix(output_path.suffix + ".json")
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["plot_type"] == "fig3_multifrequency_panel"
    assert metadata["source_result_paths"] == [str(path) for path in result_paths]
    assert metadata["case_ids"] == [
        "SYNTH_XZ_K0P5",
        "SYNTH_XZ_K1P0",
        "SYNTH_XZ_K1P5",
        "SYNTH_XZ_K2P0",
    ]
    assert metadata["kM_values"] == [0.5, 1.0, 1.5, 2.0]
    assert metadata["components"] == ["h_plus", "h_cross"]
    assert metadata["quantity"] == "real"
    assert metadata["interpolation"] == "nearest"
    assert metadata["requested_dpi"] == 180
    assert metadata["output_format"] == "png"
    assert metadata["grid_kind"] == "xz_plane"
    assert metadata["x_range"] == [-3.0, 3.0]
    assert metadata["z_range"] == [-3.0, 3.0]
    assert metadata["grid_spacing"] == {"x": 1.0, "z": 1.0}
    assert metadata["valid_point_counts"] == [36, 36, 36, 36]
    assert metadata["invalid_point_counts"] == [13, 13, 13, 13]
    assert [item["x"] for item in metadata["samples_per_wavelength"]] == pytest.approx(
        [4.0 * math.pi, 2.0 * math.pi, 2.0 * math.pi / 1.5, math.pi]
    )
    assert metadata["final_lmax_pairs"] == [[4, 8], [8, 12], [12, 16], [16, 20]]
    assert metadata["final_pair_passed"] == [True, True, True, True]
    assert set(metadata["row_color_scales"]) == {"h_plus", "h_cross"}
    assert metadata["row_color_scales"]["h_plus"]["vmin"] == -metadata["row_color_scales"][
        "h_plus"
    ]["vmax"]
    assert metadata["row_color_scales"]["h_cross"]["vmin"] == -metadata[
        "row_color_scales"
    ]["h_cross"]["vmax"]
    assert metadata["overlays"] == {
        "drawn": True,
        "event_horizon_radius": 2.0,
        "light_ring_radius": 3.0,
    }
    assert metadata["convention"] == {"fourier": "exp(-i k t)", "units": "G=c=M=1"}


def test_plot_fig3_multifrequency_panel_accepts_publication_dpi(tmp_path):
    result_paths = _save_multifrequency_results(tmp_path)
    output_path = tmp_path / "fig3_multifrequency_300dpi.png"

    sidecar = plot_fig3_multifrequency_panel_from_results(
        result_paths,
        quantity="real",
        output_path=output_path,
        dpi=300,
    )

    assert output_path.read_bytes().startswith(b"\x89PNG")
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["requested_dpi"] == 300
    assert metadata["output_format"] == "png"


def test_plot_fig3_multifrequency_panel_rejects_wrong_input_count(tmp_path):
    result_paths = _save_multifrequency_results(tmp_path)[:3]

    with pytest.raises(PlotError, match="requires exactly four"):
        plot_fig3_multifrequency_panel_from_results(
            result_paths,
            quantity="real",
            output_path=tmp_path / "bad.png",
        )


def test_plot_fig3_multifrequency_panel_rejects_mixed_grids(tmp_path):
    result_paths = _save_multifrequency_results(tmp_path)
    mixed_path = tmp_path / "mixed_grid.npz"
    save_results(
        _synthetic_multifrequency_xz_result(
            2.0,
            "SYNTH_XZ_K2P0_MIXED",
            x=np.array([-3.0, -2.0, 0.0, 1.0, 2.0, 3.0]),
        ),
        mixed_path,
    )
    result_paths[-1] = mixed_path

    with pytest.raises(PlotError, match="matching x-z coordinates"):
        plot_fig3_multifrequency_panel_from_results(
            result_paths,
            quantity="real",
            output_path=tmp_path / "bad.png",
        )


def test_plot_fig3_multifrequency_panel_rejects_non_xz_input(tmp_path):
    result_paths = _save_multifrequency_results(tmp_path)
    angular_path = tmp_path / "angular.npz"
    save_results(_synthetic_result(), angular_path)
    result_paths[1] = angular_path

    with pytest.raises(PlotError, match="requires an x-z plane result"):
        plot_fig3_multifrequency_panel_from_results(
            result_paths,
            quantity="real",
            output_path=tmp_path / "bad.png",
        )


def test_plot_fig3_multifrequency_panel_rejects_wrong_k_order(tmp_path):
    result_paths = _save_multifrequency_results(tmp_path)
    result_paths[1], result_paths[2] = result_paths[2], result_paths[1]

    with pytest.raises(PlotError, match="in increasing kM order"):
        plot_fig3_multifrequency_panel_from_results(
            result_paths,
            quantity="real",
            output_path=tmp_path / "bad.png",
        )


def test_plot_fig3_panel_masks_invalid_points_without_crashing(tmp_path):
    result_path = tmp_path / "xz_result.npz"
    output_path = tmp_path / "masked_panel.png"
    result = _synthetic_xz_result()
    result.h_plus[0, 2] = np.nan + 1j * np.nan
    save_results(result, result_path)

    sidecar = plot_fig3_panel_from_result(
        result_path,
        quantity="real",
        output_path=output_path,
    )

    assert output_path.read_bytes().startswith(b"\x89PNG")
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["valid_point_count"] == 4
    assert metadata["invalid_point_count"] == 2
    assert metadata["symmetric_color_scale"] is True


def test_plot_fig3_panel_rejects_non_xz_result(tmp_path):
    result_path = tmp_path / "angular_result.npz"
    save_results(_synthetic_result(), result_path)

    with pytest.raises(PlotError, match="requires an x-z plane result"):
        plot_fig3_panel_from_result(
            result_path,
            quantity="real",
            output_path=tmp_path / "bad.png",
        )


def test_plot_fig3_panel_rejects_non_real_quantity(tmp_path):
    result_path = tmp_path / "xz_result.npz"
    save_results(_synthetic_xz_result(), result_path)

    with pytest.raises(PlotError, match="supports only quantity='real'"):
        plot_fig3_panel_from_result(
            result_path,
            quantity="abs",
            output_path=tmp_path / "bad.png",
        )


def test_plot_fig4_exact_angular_writes_png_and_sidecar(tmp_path):
    result_path = tmp_path / "fig4_angular.npz"
    output_path = tmp_path / "fig4_exact.png"
    save_results(_synthetic_fig4_angular_result(), result_path)

    sidecar = plot_fig4_exact_angular_from_result(
        result_path,
        output_path=output_path,
        phi=0.0,
        dpi=300,
    )

    assert output_path.read_bytes().startswith(b"\x89PNG")
    assert output_path.stat().st_size > 1000
    assert sidecar == output_path.with_suffix(output_path.suffix + ".json")


def test_plot_fig4_exact_angular_sidecar_records_readonly_policy(tmp_path):
    result_path = tmp_path / "fig4_angular.npz"
    output_path = tmp_path / "fig4_exact.png"
    save_results(_synthetic_fig4_angular_result(), result_path)

    sidecar = plot_fig4_exact_angular_from_result(
        result_path,
        output_path=output_path,
        phi=0.0,
        dpi=300,
    )

    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["plot_type"] == "fig4_exact_angular_curves"
    assert metadata["curve_extraction_policy"] == "fixed_phi_cut"
    assert metadata["no_solver_rerun"] is True
    assert metadata["no_phi_average"] is True
    assert metadata["field_names"] == ["h_plus", "h_cross"]
    assert metadata["plotted_quantities"] == ["abs_h_plus", "abs_h_cross"]
    assert metadata["theta_count"] == 3
    assert metadata["phi_count"] == 2
    assert metadata["phi_selected"] == 0.0
    assert metadata["phi_selected_index"] == 0
    assert metadata["source_npz_sha256"] == hashlib.sha256(result_path.read_bytes()).hexdigest()


def test_plot_fig4_exact_angular_rejects_xz_plane_result(tmp_path):
    result_path = tmp_path / "xz_result.npz"
    save_results(_synthetic_xz_result(), result_path)

    with pytest.raises(PlotError, match="requires an angular result"):
        plot_fig4_exact_angular_from_result(
            result_path,
            output_path=tmp_path / "bad.png",
        )


def test_plot_fig4_exact_angular_rejects_missing_phi(tmp_path):
    result_path = tmp_path / "fig4_angular.npz"
    save_results(_synthetic_fig4_angular_result(), result_path)

    with pytest.raises(PlotError, match="requested phi"):
        plot_fig4_exact_angular_from_result(
            result_path,
            output_path=tmp_path / "bad.png",
            phi=0.123,
        )


def test_plot_fig4_all_frequency_exact_angular_writes_png_and_sidecar(tmp_path):
    result_paths = _save_fig4_all_frequency_angular_results(tmp_path)
    output_path = tmp_path / "fig4_all_frequency.png"

    sidecar = plot_fig4_all_frequency_exact_angular_from_results(
        result_paths,
        output_path=output_path,
        phi=0.0,
        dpi=300,
    )

    assert output_path.read_bytes().startswith(b"\x89PNG")
    assert output_path.stat().st_size > 1000
    assert sidecar == output_path.with_suffix(output_path.suffix + ".json")


def test_plot_fig4_all_frequency_exact_angular_sidecar_records_readonly_policy(
    tmp_path,
):
    result_paths = _save_fig4_all_frequency_angular_results(tmp_path)
    output_path = tmp_path / "fig4_all_frequency.png"

    sidecar = plot_fig4_all_frequency_exact_angular_from_results(
        result_paths,
        output_path=output_path,
        phi=0.0,
        dpi=300,
    )

    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["plot_type"] == "fig4_all_frequency_exact_angular_curves"
    assert metadata["curve_extraction_policy"] == "fixed_phi_cut"
    assert metadata["source_kM_values"] == [0.5, 1.0, 1.5, 2.0]
    assert metadata["source_npz_sha256"] == [
        hashlib.sha256(path.read_bytes()).hexdigest() for path in result_paths
    ]
    assert metadata["final_lmax_pairs"] == [[72, 84], [96, 108], [132, 156], [156, 180]]
    assert metadata["no_solver_rerun"] is True
    assert metadata["no_phi_average"] is True
    assert metadata["no_strict_psi4"] is True
    assert metadata["no_kirchhoff_baseline"] is True
    assert metadata["q018_oracle_warning_counts"] == [0, 0, 0, 4]
    assert metadata["q018_opt_ins"] == [None, None, None, "q018_riccati"]


def test_plot_fig4_all_frequency_exact_angular_rejects_wrong_input_count(tmp_path):
    result_paths = _save_fig4_all_frequency_angular_results(tmp_path)[:3]

    with pytest.raises(PlotError, match="requires exactly four"):
        plot_fig4_all_frequency_exact_angular_from_results(
            result_paths,
            output_path=tmp_path / "bad.png",
        )


def test_plot_fig4_all_frequency_exact_angular_rejects_wrong_k_order(tmp_path):
    result_paths = _save_fig4_all_frequency_angular_results(tmp_path)
    result_paths[1], result_paths[2] = result_paths[2], result_paths[1]

    with pytest.raises(PlotError, match="in increasing kM order"):
        plot_fig4_all_frequency_exact_angular_from_results(
            result_paths,
            output_path=tmp_path / "bad.png",
        )


def test_plot_fig4_all_frequency_exact_angular_rejects_mismatched_grids(tmp_path):
    result_paths = _save_fig4_all_frequency_angular_results(tmp_path)
    mismatched_path = tmp_path / "mismatched.npz"
    save_results(
        _synthetic_fig4_all_frequency_angular_result(
            2.0,
            "SYNTH_FIG4_ALL_K2P0_MISMATCHED",
            theta=np.linspace(0.0, math.pi, 65) + 1.0e-6,
        ),
        mismatched_path,
    )
    result_paths[-1] = mismatched_path

    with pytest.raises(PlotError, match="matching theta and phi"):
        plot_fig4_all_frequency_exact_angular_from_results(
            result_paths,
            output_path=tmp_path / "bad.png",
        )


def test_plot_fig4_all_frequency_exact_angular_rejects_missing_phi(tmp_path):
    result_paths = _save_fig4_all_frequency_angular_results(tmp_path)

    with pytest.raises(PlotError, match="requested phi"):
        plot_fig4_all_frequency_exact_angular_from_results(
            result_paths,
            output_path=tmp_path / "bad.png",
            phi=0.123,
        )


def test_plot_amplification_writes_png_and_required_sidecar(tmp_path):
    result_path = tmp_path / "amplification.npz"
    output_path = tmp_path / "F_pol_norm.png"
    save_amplification_results(_synthetic_amplification_result(), result_path)

    sidecar = plot_amplification_from_result(
        result_path,
        quantity="F_pol_norm",
        output_path=output_path,
        dpi=240,
    )

    assert output_path.read_bytes().startswith(b"\x89PNG")
    assert output_path.stat().st_size > 1000
    assert sidecar == output_path.with_suffix(output_path.suffix + ".json")
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["plot_type"] == "pointwise_wave_optics_amplification"
    assert metadata["quantity"] == "F_pol_norm"
    assert metadata["mask_field"] == "valid_ratio_norm_mask"
    assert metadata["source_amplification_result_path"] == str(result_path)
    assert metadata["case_id"] == "SYNTH_XZ_AMPLIFICATION"
    assert metadata["source_case_id"] == "SYNTH_XZ"
    assert metadata["normalization"]["baseline"] == "flat_no_lens"
    assert metadata["baseline"]["baseline"] == "flat_no_lens"
    assert metadata["grid_kind"] == "xz_plane"
    assert metadata["shape"] == [2, 3]
    assert metadata["valid_count"] == 4
    assert metadata["invalid_count"] == 2
    assert metadata["output_path"] == str(output_path)
    assert metadata["requested_dpi"] == 240
    assert metadata["x_range"] == [-1.0, 3.0]
    assert metadata["z_range"] == [0.0, 4.0]


@pytest.mark.parametrize(
    ("quantity", "mask_field"),
    [
        ("F_pol_norm", "valid_ratio_norm_mask"),
        ("I_pol_ratio", "valid_ratio_norm_mask"),
        ("amplification_plus", "valid_ratio_plus_mask"),
        ("amplification_cross", "valid_ratio_cross_mask"),
    ],
)
def test_plot_amplification_uses_quantity_specific_masks(
    tmp_path, quantity, mask_field
):
    result_path = tmp_path / f"{quantity}.npz"
    output_path = tmp_path / f"{quantity}.png"
    save_amplification_results(_synthetic_amplification_result(), result_path)

    sidecar = plot_amplification_from_result(
        result_path,
        quantity=quantity,
        output_path=output_path,
    )

    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["quantity"] == quantity
    assert metadata["mask_field"] == mask_field


def test_plot_amplification_keeps_invalid_ratio_values_nan():
    result = _synthetic_amplification_result()

    plus_values, plus_valid, plus_mask_field = _amplification_quantity_values(
        result,
        "amplification_plus",
    )
    cross_values, cross_valid, cross_mask_field = _amplification_quantity_values(
        result,
        "amplification_cross",
    )

    assert plus_mask_field == "valid_ratio_plus_mask"
    assert cross_mask_field == "valid_ratio_cross_mask"
    assert not plus_valid[0, 0]
    assert not cross_valid[0, 1]
    assert np.isnan(plus_values[0, 0])
    assert np.isnan(cross_values[0, 1])


def test_plot_amplification_rejects_unsupported_quantity(tmp_path):
    result_path = tmp_path / "amplification.npz"
    save_amplification_results(_synthetic_amplification_result(), result_path)

    with pytest.raises(PlotError, match="quantity must be one of"):
        plot_amplification_from_result(
            result_path,
            quantity="transmission",
            output_path=tmp_path / "bad.png",
        )


def test_plot_tablei_four_frequency_report_writes_reports_plots_and_sidecars(tmp_path):
    source_path = tmp_path / "tablei.npz"
    output_dir = tmp_path / "reporting"
    _write_synthetic_tablei_extraction(source_path)

    outputs = plot_tablei_four_frequency_report(
        source_path,
        output_dir=output_dir,
        dpi=160,
    )

    expected_names = {
        "tablei_four_frequency_values.csv",
        "tablei_four_frequency_values.md",
        "fig5_near_axis_tablei_four_frequency_pilot.png",
        "fig5_near_axis_tablei_four_frequency_pilot.png.json",
        "fig6_far_axis_tablei_four_frequency_pilot.png",
        "fig6_far_axis_tablei_four_frequency_pilot.png.json",
    }
    assert {path.name for path in output_dir.iterdir()} == expected_names
    assert set(outputs) == {
        "csv",
        "markdown",
        "near_axis_png",
        "near_axis_sidecar",
        "far_axis_png",
        "far_axis_sidecar",
    }
    assert outputs["near_axis_png"].read_bytes().startswith(b"\x89PNG")
    assert outputs["far_axis_png"].read_bytes().startswith(b"\x89PNG")

    csv_text = outputs["csv"].read_text(encoding="utf-8")
    assert "kM,point_id,point_group" in csv_text
    assert "near_axis_x0_z30" in csv_text
    assert "far_axis_x10_z30" in csv_text
    assert "F_plus_real" in csv_text
    assert "arg_F_cross_unwrapped" in csv_text

    markdown = outputs["markdown"].read_text(encoding="utf-8")
    assert "Near-Axis Four-Frequency Read-Only Pilot" in markdown
    assert "Far-Axis Four-Frequency Read-Only Pilot" in markdown
    assert "paper-level Fig.5/Fig.6 reproduction" in markdown
    assert "kM=4" not in markdown

    near_metadata = json.loads(outputs["near_axis_sidecar"].read_text(encoding="utf-8"))
    assert near_metadata["plot_type"] == "tablei_four_frequency_readonly_pilot"
    assert near_metadata["source_extraction_npz_path"] == str(source_path)
    assert near_metadata["source_extraction_npz_sha256"] == hashlib.sha256(
        source_path.read_bytes()
    ).hexdigest()
    assert near_metadata["source_extraction_json_sha256"] == hashlib.sha256(
        source_path.with_suffix(".npz.json").read_bytes()
    ).hexdigest()
    assert near_metadata["plotted_group"] == "near_axis"
    assert near_metadata["plotted_point_ids"] == [
        "near_axis_x0_z30",
        "near_axis_x1_z30",
    ]
    assert near_metadata["plotted_quantities"] == [
        "abs_F_plus",
        "abs_F_cross",
        "arg_F_plus_unwrapped",
        "arg_F_cross_unwrapped",
    ]
    assert near_metadata["output_artifacts"]["csv"]["path"] == str(outputs["csv"])
    assert near_metadata["output_artifacts"]["markdown"]["path"] == str(
        outputs["markdown"]
    )
    assert near_metadata["no_solver_rerun"] is True
    assert near_metadata["no_field_recomputation"] is True
    assert near_metadata["no_interpolation"] is True
    assert near_metadata["no_kirchhoff_baseline"] is True
    assert near_metadata["not_paper_level_dense_scan"] is True
    assert near_metadata["no_kM4"] is True
    assert near_metadata["no_dense_Mk_scan"] is True
    assert near_metadata["no_new_physics_convention"] is True
    assert near_metadata["read_only_from_tablei_extraction"] is True

    far_metadata = json.loads(outputs["far_axis_sidecar"].read_text(encoding="utf-8"))
    assert far_metadata["plotted_group"] == "far_axis"
    assert far_metadata["plotted_point_ids"] == ["far_axis_x10_z30"]


def test_plot_tablei_four_frequency_report_keeps_invalid_component_values(tmp_path):
    source_path = tmp_path / "tablei_invalid.npz"
    output_dir = tmp_path / "reporting"
    _write_synthetic_tablei_extraction(source_path, invalid_cross=True)

    outputs = plot_tablei_four_frequency_report(source_path, output_dir=output_dir)

    csv_text = outputs["csv"].read_text(encoding="utf-8")
    assert "False,nan,nan,nan,nan,nan" in csv_text
    sidecar = json.loads(outputs["near_axis_sidecar"].read_text(encoding="utf-8"))
    assert sidecar["mask_policy"]["invalid_values"] == (
        "preserve masks and NaN values; do not fill, clip, smooth, regularize, "
        "or substitute component ratios"
    )


def test_plot_tablei_four_frequency_report_rejects_missing_json_sidecar(tmp_path):
    source_path = tmp_path / "tablei.npz"
    _write_synthetic_tablei_extraction(source_path)
    source_path.with_suffix(".npz.json").unlink()

    with pytest.raises(PlotError, match="JSON sidecar"):
        plot_tablei_four_frequency_report(
            source_path,
            output_dir=tmp_path / "reporting",
        )


def test_viz_results_remain_read_only_without_solver_imports():
    viz_dir = Path(__file__).resolve().parents[2] / "src" / "schwgw" / "viz"
    forbidden = [
        "schwgw.scattering",
        "schwgw.perturbations",
        "schwgw.angular",
        "schwgw.numerics",
        "schwgw.backgrounds",
        "compute_polarization",
        "run_solver_grid",
        "solve_radial",
        "compute_pointwise_amplification",
        "flat_no_lens_baseline_at_point",
    ]
    for path in viz_dir.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        for marker in forbidden:
            assert marker not in source, f"{path.name} imports or calls {marker}"


def test_plot_convergence_writes_png_and_sidecar_from_saved_history(tmp_path):
    result_path = tmp_path / "result.npz"
    output_path = tmp_path / "convergence.png"
    result = _synthetic_result()
    result.metadata["diagnostics"] = _convergence_diagnostics()
    save_results(result, result_path)

    sidecar = plot_convergence_from_result(result_path, output_path=output_path)

    assert output_path.read_bytes().startswith(b"\x89PNG")
    assert output_path.stat().st_size > 1000
    assert sidecar == output_path.with_suffix(output_path.suffix + ".json")
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["source_result_path"] == str(result_path)
    assert metadata["case_id"] == "SYNTH"
    assert metadata["kM"] == 1.0
    assert metadata["observer_r"] == 60.0
    assert metadata["lmax_values"] == [2, 3, 4]
    assert metadata["final_lmax_pair"] == [3, 4]
    assert metadata["final_pair_passed"] is False
    assert metadata["thresholds"] == {
        "selected": 1.0e-4,
        "near_axis": 1.0e-3,
    }
    assert "relative change" in metadata["convention"]


def test_plot_convergence_fails_without_saved_history(tmp_path):
    result_path = tmp_path / "result.npz"
    save_results(_synthetic_result(), result_path)

    with pytest.raises(PlotError, match="does not contain lmax_convergence_history"):
        plot_convergence_from_result(result_path, output_path=tmp_path / "conv.png")


@pytest.mark.parametrize(
    ("component", "quantity", "message"),
    [
        ("psi4", "real", "component must be one of"),
        ("h_plus", "power", "quantity must be one of"),
    ],
)
def test_plot_wavefield_rejects_invalid_component_or_quantity(
    tmp_path, component, quantity, message
):
    result_path = tmp_path / "result.npz"
    save_results(_synthetic_result(), result_path)

    with pytest.raises(PlotError, match=message):
        plot_wavefield_from_result(
            result_path,
            component=component,
            quantity=quantity,
            output_path=tmp_path / "bad.png",
        )


def _synthetic_result(
    *,
    theta: np.ndarray | None = None,
    phi: np.ndarray | None = None,
    h_plus: np.ndarray | None = None,
) -> GridResult:
    theta = np.array([0.0, 0.2]) if theta is None else theta
    phi = np.array([0.0, 0.3, 0.6]) if phi is None else phi
    if h_plus is None:
        h_plus = np.array(
            [
                [1.0 + 0.5j, 2.0 + 0.25j, 3.0 - 0.25j],
                [4.0 + 0.0j, 5.0 - 0.5j, 6.0 - 0.75j],
            ],
            dtype=np.complex128,
        )
    return GridResult(
        theta=theta,
        phi=phi,
        h_plus=h_plus,
        h_cross=-h_plus,
        metadata={
            "case_id": "SYNTH",
            "created_at": "2026-07-05T00:00:00+00:00",
            "convention": {"fourier": "exp(-i k t)", "units": "G=c=M=1"},
            "config": {
                "wave": {"kM": 1.0},
                "observer": {"r": 60.0},
                "numerics": {"lmax": 2},
            },
            "lmax": 2,
        },
    )


def _synthetic_xz_result() -> GridResult:
    x = np.array([-1.0, 0.0, 3.0])
    z = np.array([0.0, 4.0])
    xx, zz = np.meshgrid(x, z)
    r = np.sqrt(xx * xx + zz * zz)
    valid_mask = r > 2.0
    theta = np.full_like(r, np.nan, dtype=float)
    theta[valid_mask] = np.arccos(zz[valid_mask] / r[valid_mask])
    phi = np.where(xx < 0.0, np.pi, 0.0)
    phi = np.where(valid_mask, phi, np.nan)
    h_plus = np.full(r.shape, np.nan + 1j * np.nan, dtype=np.complex128)
    h_plus[valid_mask] = r[valid_mask] + 1j * phi[valid_mask]
    return GridResult(
        theta=theta,
        phi=phi,
        h_plus=h_plus,
        h_cross=-h_plus,
        metadata={
            "case_id": "SYNTH_XZ",
            "created_at": "2026-07-05T00:00:00+00:00",
            "convention": {"fourier": "exp(-i k t)", "units": "G=c=M=1"},
            "config": {
                "background": {"M": 1.0},
                "wave": {"kM": 1.0},
                "observer": {
                    "kind": "xz_plane",
                    "x_values": x.tolist(),
                    "z_values": z.tolist(),
                    "invalid_radius_policy": "mask",
                },
                "numerics": {"lmax": 2},
            },
            "grid": {
                "kind": "xz_plane",
                "x_values": x.tolist(),
                "z_values": z.tolist(),
                "valid_point_count": int(valid_mask.sum()),
                "invalid_point_count": int(valid_mask.size - valid_mask.sum()),
                "coordinate_conversion": (
                    "r=sqrt(x^2+z^2), theta=arccos(z/r), "
                    "phi=0 if x>=0 else pi"
                ),
            },
            "lmax": 2,
            "diagnostics": {
                "final_lmax_pair": [1, 2],
                "lmax_convergence_policy": {"final_pair_passed": True},
            },
        },
        x=x,
        z=z,
        r=r,
        valid_mask=valid_mask,
    )


def _synthetic_fig4_angular_result() -> GridResult:
    theta = np.array([0.0, math.pi / 2.0, math.pi])
    phi = np.array([0.0, math.pi / 2.0])
    h_plus = np.array(
        [
            [1.0 + 0.0j, 1.2 + 0.1j],
            [2.0 + 0.5j, 2.2 + 0.2j],
            [3.0 - 0.5j, 3.2 - 0.2j],
        ],
        dtype=np.complex128,
    )
    warnings = [
        _q018_warning(153, "odd"),
        _q018_warning(153, "even"),
        _q018_warning(154, "odd"),
        _q018_warning(154, "even"),
    ]
    return GridResult(
        theta=theta,
        phi=phi,
        h_plus=h_plus,
        h_cross=-0.5 * h_plus,
        metadata={
            "case_id": "SYNTH_FIG4_ANGULAR",
            "created_at": "2026-07-05T00:00:00+00:00",
            "convention": {"fourier": "exp(-i k t)", "units": "G=c=M=1"},
            "config": {
                "background": {"M": 1.0},
                "wave": {"kM": 2.0},
                "observer": {
                    "kind": "angular",
                    "r": 60.0,
                    "theta_range": {
                        "start": 0.0,
                        "stop": math.pi,
                        "step": math.pi / 2.0,
                        "endpoint": True,
                    },
                    "phi_range": {
                        "start": 0.0,
                        "stop": math.pi,
                        "step": math.pi / 2.0,
                        "endpoint": False,
                    },
                },
                "numerics": {
                    "lmax": 180,
                    "boundary": {
                        "required_eval_radius": 60.0,
                        "experimental_required_radius_oracle": "q018_riccati",
                    },
                },
            },
            "grid": {
                "kind": "angular",
                "r": 60.0,
                "theta_values": theta.tolist(),
                "phi_values": phi.tolist(),
                "valid_point_count": int(theta.size * phi.size),
                "invalid_point_count": 0,
            },
            "lmax": 180,
            "diagnostics": {
                "final_lmax_pair": [156, 180],
                "lmax_convergence_history": [
                    {
                        "previous_lmax": 156,
                        "current_lmax": 180,
                        "max_relative_change": 1.0e-7,
                        "near_axis_max_relative_change": 1.0e-9,
                    }
                ],
                "lmax_convergence_policy": {
                    "selected_threshold": 1.0e-4,
                    "near_axis_threshold": 1.0e-3,
                },
                "radial_diagnostic_warnings": warnings,
                "run_radial_cache": {
                    "unique_solution_count": 358,
                    "key_count": 358,
                    "hit_count": 1644506,
                },
            },
        },
    )


def _q018_warning(ell: int, sector: str) -> dict[str, object]:
    return {
        "code": "q018_required_radius_oracle_used",
        "ell": ell,
        "sector": sector,
        "required_eval_radius": 60.0,
        "experimental_required_radius_oracle": "q018_riccati",
        "valid_at_required_radius": True,
    }


def _save_fig4_all_frequency_angular_results(tmp_path) -> list[Path]:
    paths = []
    for kM, case_id in [
        (0.5, "SYNTH_FIG4_ALL_K0P5"),
        (1.0, "SYNTH_FIG4_ALL_K1P0"),
        (1.5, "SYNTH_FIG4_ALL_K1P5"),
        (2.0, "SYNTH_FIG4_ALL_K2P0"),
    ]:
        path = tmp_path / f"{case_id}.npz"
        save_results(_synthetic_fig4_all_frequency_angular_result(kM, case_id), path)
        paths.append(path)
    return paths


def _synthetic_fig4_all_frequency_angular_result(
    kM: float,
    case_id: str,
    *,
    theta: np.ndarray | None = None,
    phi: np.ndarray | None = None,
) -> GridResult:
    theta = np.linspace(0.0, math.pi, 65) if theta is None else theta
    phi = np.linspace(0.0, 2.0 * math.pi, 64, endpoint=False) if phi is None else phi
    theta_grid, phi_grid = np.meshgrid(theta, phi, indexing="ij")
    h_plus = (
        (1.0 + kM) * (1.0 + np.cos(theta_grid) ** 2)
        + 0.1j * np.sin(phi_grid)
    ).astype(np.complex128)
    h_cross = (
        (0.5 + kM) * np.sin(theta_grid)
        - 0.1j * np.cos(phi_grid)
    ).astype(np.complex128)
    lmax = {0.5: 84, 1.0: 108, 1.5: 156, 2.0: 180}[kM]
    final_pair = {
        0.5: [72, 84],
        1.0: [96, 108],
        1.5: [132, 156],
        2.0: [156, 180],
    }[kM]
    boundary = {"required_eval_radius": 60.0}
    warnings = []
    if kM == 2.0:
        boundary["experimental_required_radius_oracle"] = "q018_riccati"
        warnings = [
            _q018_warning(153, "odd"),
            _q018_warning(153, "even"),
            _q018_warning(154, "odd"),
            _q018_warning(154, "even"),
        ]
    return GridResult(
        theta=theta,
        phi=phi,
        h_plus=h_plus,
        h_cross=h_cross,
        metadata={
            "case_id": case_id,
            "created_at": "2026-07-08T00:00:00+00:00",
            "convention": {"fourier": "exp(-i k t)", "units": "G=c=M=1"},
            "config": {
                "background": {"M": 1.0},
                "wave": {"kM": kM},
                "observer": {
                    "kind": "angular",
                    "r": 60.0,
                    "theta_range": {
                        "start": 0.0,
                        "stop": math.pi,
                        "step": math.pi / 64.0,
                        "endpoint": True,
                    },
                    "phi_range": {
                        "start": 0.0,
                        "stop": 2.0 * math.pi,
                        "step": 2.0 * math.pi / 64.0,
                        "endpoint": False,
                    },
                },
                "numerics": {"lmax": lmax, "boundary": boundary},
            },
            "grid": {
                "kind": "angular",
                "r": 60.0,
                "theta_values": theta.tolist(),
                "phi_values": phi.tolist(),
                "valid_point_count": int(theta.size * phi.size),
                "invalid_point_count": 0,
            },
            "lmax": lmax,
            "diagnostics": {
                "final_lmax_pair": final_pair,
                "lmax_convergence_history": [
                    {
                        "previous_lmax": final_pair[0],
                        "current_lmax": final_pair[1],
                        "max_relative_change": 1.0e-7,
                        "near_axis_max_relative_change": 1.0e-9,
                    }
                ],
                "lmax_convergence_policy": {
                    "selected_threshold": 1.0e-4,
                    "near_axis_threshold": 1.0e-3,
                    "final_pair_passed": True,
                },
                "radial_diagnostic_warnings": warnings,
                "run_radial_cache": {
                    "unique_solution_count": int(2 * lmax - 2),
                    "key_count": int(2 * lmax - 2),
                    "hit_count": int(1000 * lmax),
                },
                "radial_summary": {
                    "max_match_condition_number_max": (
                        4.939017032749817e144 if kM == 1.5 else 2.0
                    ),
                },
            },
        },
    )


def _synthetic_uniform_xz_result() -> GridResult:
    x = np.array([-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0])
    z = np.array([-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0])
    xx, zz = np.meshgrid(x, z)
    r = np.sqrt(xx * xx + zz * zz)
    valid_mask = r > 2.0
    theta = np.full_like(r, np.nan, dtype=float)
    theta[valid_mask] = np.arccos(zz[valid_mask] / r[valid_mask])
    phi = np.where(xx < 0.0, np.pi, 0.0)
    phi = np.where(valid_mask, phi, np.nan)
    h_plus = np.full(r.shape, np.nan + 1j * np.nan, dtype=np.complex128)
    h_plus[valid_mask] = r[valid_mask] + 1j * phi[valid_mask]
    return GridResult(
        theta=theta,
        phi=phi,
        h_plus=h_plus,
        h_cross=-h_plus,
        metadata={
            "case_id": "SYNTH_XZ_UNIFORM",
            "created_at": "2026-07-05T00:00:00+00:00",
            "convention": {"fourier": "exp(-i k t)", "units": "G=c=M=1"},
            "config": {
                "background": {"M": 1.0},
                "wave": {"kM": 1.0},
                "observer": {
                    "kind": "xz_plane",
                    "x_values": x.tolist(),
                    "z_values": z.tolist(),
                    "invalid_radius_policy": "mask",
                },
                "numerics": {"lmax": 2},
            },
            "grid": {
                "kind": "xz_plane",
                "x_values": x.tolist(),
                "z_values": z.tolist(),
                "valid_point_count": int(valid_mask.sum()),
                "invalid_point_count": int(valid_mask.size - valid_mask.sum()),
                "coordinate_conversion": (
                    "r=sqrt(x^2+z^2), theta=arccos(z/r), "
                    "phi=0 if x>=0 else pi"
                ),
            },
            "lmax": 2,
        },
        x=x,
        z=z,
        r=r,
        valid_mask=valid_mask,
    )


def _synthetic_amplification_result() -> AmplificationGridResult:
    x = np.array([-1.0, 0.0, 3.0])
    z = np.array([0.0, 4.0])
    xx, zz = np.meshgrid(x, z)
    r = np.sqrt(xx * xx + zz * zz)
    theta = np.array(
        [
            [np.nan, np.nan, np.pi / 2.0],
            [1.82, 0.0, 0.93],
        ],
        dtype=float,
    )
    phi = np.array(
        [
            [np.nan, np.nan, 0.0],
            [np.pi, 0.0, 0.0],
        ],
        dtype=float,
    )
    valid_mask = np.array(
        [
            [False, False, True],
            [True, True, True],
        ],
        dtype=bool,
    )
    valid_ratio_plus_mask = np.array(
        [
            [False, True, True],
            [True, False, True],
        ],
        dtype=bool,
    )
    valid_ratio_cross_mask = np.array(
        [
            [False, False, True],
            [True, True, True],
        ],
        dtype=bool,
    )
    valid_ratio_norm_mask = np.array(
        [
            [False, False, True],
            [True, True, True],
        ],
        dtype=bool,
    )
    F_plus_complex = np.array(
        [
            [np.nan + 1j * np.nan, 1.2 + 0.1j, 0.9 + 0.2j],
            [1.1 - 0.2j, np.nan + 1j * np.nan, 1.3 + 0.4j],
        ],
        dtype=np.complex128,
    )
    F_cross_complex = np.array(
        [
            [np.nan + 1j * np.nan, np.nan + 1j * np.nan, 0.8 - 0.1j],
            [1.4 + 0.2j, 1.0 + 0.0j, 1.2 - 0.3j],
        ],
        dtype=np.complex128,
    )
    amplification_plus = np.abs(F_plus_complex)
    amplification_cross = np.abs(F_cross_complex)
    intensity_plus_ratio = amplification_plus * amplification_plus
    intensity_cross_ratio = amplification_cross * amplification_cross
    F_pol_norm = np.array(
        [
            [np.nan, np.nan, 0.85],
            [1.25, 1.05, 1.18],
        ],
        dtype=float,
    )
    I_pol_ratio = F_pol_norm * F_pol_norm
    return AmplificationGridResult(
        theta=theta,
        phi=phi,
        F_plus_complex=F_plus_complex,
        F_cross_complex=F_cross_complex,
        amplification_plus=amplification_plus,
        amplification_cross=amplification_cross,
        intensity_plus_ratio=intensity_plus_ratio,
        intensity_cross_ratio=intensity_cross_ratio,
        F_pol_norm=F_pol_norm,
        I_pol_ratio=I_pol_ratio,
        valid_ratio_plus_mask=valid_ratio_plus_mask,
        valid_ratio_cross_mask=valid_ratio_cross_mask,
        valid_ratio_norm_mask=valid_ratio_norm_mask,
        metadata={
            "case_id": "SYNTH_XZ_AMPLIFICATION",
            "source_case_id": "SYNTH_XZ",
            "source_lensed_result_path": "/saved/lensed.npz",
            "source_grid": {
                "kind": "xz_plane",
                "valid_point_count": int(valid_mask.sum()),
                "invalid_point_count": int(valid_mask.size - valid_mask.sum()),
            },
            "source_convention": {"fourier": "exp(-i k t)", "units": "G=c=M=1"},
            "grid": {
                "kind": "xz_plane",
                "valid_point_count": int(valid_mask.sum()),
                "invalid_point_count": int(valid_mask.size - valid_mask.sum()),
            },
            "normalization": {
                "baseline": "flat_no_lens",
                "baseline_api": "compute_flat_no_lens_polarization",
                "ratio_definition": "pointwise lensed field divided by saved baseline",
                "polarization_norm": "sqrt(|A_plus|^2 + |A_cross|^2)",
            },
        },
        x=x,
        z=z,
        r=r,
        valid_mask=valid_mask,
    )


def _write_synthetic_tablei_extraction(
    path: Path,
    *,
    invalid_cross: bool = False,
) -> None:
    kM_values = np.array([0.5, 1.0, 1.5, 2.0], dtype=float)
    point_ids = np.array(
        ["near_axis_x0_z30", "near_axis_x1_z30", "far_axis_x10_z30"]
    )
    point_group = np.array(["near_axis", "near_axis", "far_axis"])
    shape = (kM_values.size, point_ids.size)
    f_plus = np.empty(shape, dtype=np.complex128)
    f_cross = np.empty(shape, dtype=np.complex128)
    for frequency_index, kM in enumerate(kM_values):
        for point_index in range(point_ids.size):
            f_plus[frequency_index, point_index] = complex(
                1.0 + kM + 0.1 * point_index,
                0.2 * point_index,
            )
            f_cross[frequency_index, point_index] = complex(
                0.5 + 0.25 * kM + 0.2 * point_index,
                -0.1 * frequency_index,
            )
    valid_plus = np.ones(shape, dtype=bool)
    valid_cross = np.ones(shape, dtype=bool)
    valid_norm = np.ones(shape, dtype=bool)
    source_valid = np.ones(shape, dtype=bool)
    if invalid_cross:
        f_cross[1, 0] = np.nan + 1j * np.nan
        valid_cross[1, 0] = False
    arg_plus = np.angle(f_plus)
    arg_cross = np.angle(f_cross)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        kM_values=kM_values,
        point_ids=point_ids,
        point_group=point_group,
        point_x=np.array([0.0, 1.0, 10.0]),
        point_y=np.zeros(3),
        point_z=np.full(3, 30.0),
        point_r=np.array([30.0, math.sqrt(901.0), math.sqrt(1000.0)]),
        point_theta=np.array([0.0, math.atan2(1.0, 30.0), math.atan2(10.0, 30.0)]),
        point_phi=np.zeros(3),
        paper_theta_deg=np.array([0.0, 1.90915, 18.4349]),
        paper_xi_over_xi0=np.array([0.0, 0.0913, 0.9372]),
        x_indices=np.array([60, 62, 80]),
        z_indices=np.array([120, 120, 120]),
        F_plus_complex=f_plus,
        F_cross_complex=f_cross,
        abs_F_plus=np.abs(f_plus),
        abs_F_cross=np.abs(f_cross),
        arg_F_plus_principal=arg_plus,
        arg_F_cross_principal=arg_cross,
        arg_F_plus_unwrapped=arg_plus,
        arg_F_cross_unwrapped=arg_cross,
        valid_ratio_plus_mask=valid_plus,
        valid_ratio_cross_mask=valid_cross,
        valid_ratio_norm_mask=valid_norm,
        valid_field_mask=source_valid,
        source_valid_mask=source_valid,
        metadata_json=np.asarray(
            json.dumps(
                {
                    "case_id": "SYNTH_TABLEI",
                    "schema_version": "phase5_t8ac_tablei_v1",
                    "phase_policy": {
                        "principal": "angle in (-pi, pi]",
                        "unwrapped": "diagnostic",
                        "four_frequency_unwrap_is_diagnostic_only": True,
                    },
                    "no_solver_rerun": True,
                    "no_field_recomputation": True,
                    "no_interpolation": True,
                    "no_kirchhoff_baseline": True,
                    "not_paper_level_dense_scan": True,
                    "no_kM4": True,
                    "no_dense_Mk_scan": True,
                    "no_new_physics_convention": True,
                },
                sort_keys=True,
            )
        ),
    )
    path.with_suffix(path.suffix + ".json").write_text(
        json.dumps(
            {
                "case_id": "SYNTH_TABLEI",
                "schema_version": "phase5_t8ac_tablei_v1",
                "phase_policy": {
                    "principal": "angle in (-pi, pi]",
                    "unwrapped": "diagnostic",
                    "four_frequency_unwrap_is_diagnostic_only": True,
                },
                "no_solver_rerun": True,
                "no_field_recomputation": True,
                "no_interpolation": True,
                "no_kirchhoff_baseline": True,
                "not_paper_level_dense_scan": True,
                "no_kM4": True,
                "no_dense_Mk_scan": True,
                "no_new_physics_convention": True,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _save_multifrequency_results(tmp_path) -> list[Path]:
    paths = []
    for kM, case_id in [
        (0.5, "SYNTH_XZ_K0P5"),
        (1.0, "SYNTH_XZ_K1P0"),
        (1.5, "SYNTH_XZ_K1P5"),
        (2.0, "SYNTH_XZ_K2P0"),
    ]:
        path = tmp_path / f"{case_id}.npz"
        save_results(_synthetic_multifrequency_xz_result(kM, case_id), path)
        paths.append(path)
    return paths


def _synthetic_multifrequency_xz_result(
    kM: float,
    case_id: str,
    *,
    x: np.ndarray | None = None,
    z: np.ndarray | None = None,
) -> GridResult:
    x = np.array([-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0]) if x is None else x
    z = np.array([-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0]) if z is None else z
    xx, zz = np.meshgrid(x, z)
    r = np.sqrt(xx * xx + zz * zz)
    valid_mask = r > 2.0
    theta = np.full_like(r, np.nan, dtype=float)
    theta[valid_mask] = np.arccos(zz[valid_mask] / r[valid_mask])
    phi = np.where(xx < 0.0, np.pi, 0.0)
    phi = np.where(valid_mask, phi, np.nan)
    h_plus = np.full(r.shape, np.nan + 1j * np.nan, dtype=np.complex128)
    h_cross = np.full(r.shape, np.nan + 1j * np.nan, dtype=np.complex128)
    h_plus[valid_mask] = kM * r[valid_mask] + 1j * phi[valid_mask]
    h_cross[valid_mask] = -(kM + 0.25) * r[valid_mask] + 0.5j * phi[valid_mask]
    lmax = int(4 + 8 * kM)
    return GridResult(
        theta=theta,
        phi=phi,
        h_plus=h_plus,
        h_cross=h_cross,
        metadata={
            "case_id": case_id,
            "created_at": "2026-07-05T00:00:00+00:00",
            "convention": {"fourier": "exp(-i k t)", "units": "G=c=M=1"},
            "config": {
                "background": {"M": 1.0},
                "wave": {"kM": kM},
                "observer": {
                    "kind": "xz_plane",
                    "x_values": x.tolist(),
                    "z_values": z.tolist(),
                    "invalid_radius_policy": "mask",
                },
                "numerics": {"lmax": lmax},
            },
            "grid": {
                "kind": "xz_plane",
                "x_values": x.tolist(),
                "z_values": z.tolist(),
                "valid_point_count": int(valid_mask.sum()),
                "invalid_point_count": int(valid_mask.size - valid_mask.sum()),
                "coordinate_conversion": (
                    "r=sqrt(x^2+z^2), theta=arccos(z/r), "
                    "phi=0 if x>=0 else pi"
                ),
            },
            "lmax": lmax,
            "diagnostics": {
                "final_lmax_pair": [lmax - 4, lmax],
                "lmax_convergence_policy": {"final_pair_passed": True},
            },
        },
        x=x,
        z=z,
        r=r,
        valid_mask=valid_mask,
    )


def _convergence_diagnostics() -> dict:
    return {
        "lmax_convergence_history": [
            {
                "previous_lmax": 2,
                "current_lmax": 3,
                "max_relative_change": 2.0e-2,
                "near_axis_max_relative_change": 3.0e-2,
                "probe_count": 2,
            },
            {
                "previous_lmax": 3,
                "current_lmax": 4,
                "max_relative_change": 2.0e-3,
                "near_axis_max_relative_change": 4.0e-3,
                "probe_count": 2,
            },
        ],
        "lmax_convergence_policy": {
            "enabled": True,
            "lmax_values": [2, 3, 4],
            "theta_values": [0.0, 0.05],
            "phi_values": [0.0],
            "selected_threshold": 1.0e-4,
            "near_axis_threshold": 1.0e-3,
            "relative_change_denominator": "max(abs(new), abs(old), 1e-30)",
            "final_pair_passed": False,
        },
        "final_lmax_pair": [3, 4],
    }
