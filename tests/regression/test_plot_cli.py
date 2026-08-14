from __future__ import annotations

import json
import math

import numpy as np
import pytest

from schwgw import cli
from schwgw.io.results import (
    AmplificationGridResult,
    GridResult,
    save_amplification_results,
    save_results,
)


def test_cli_plot_wavefield_writes_png_and_sidecar_from_npz(tmp_path, monkeypatch):
    result_path = tmp_path / "result.npz"
    output_path = tmp_path / "plot.png"
    save_results(_synthetic_result(), result_path)
    monkeypatch.setattr(
        cli,
        "compute_polarization",
        lambda **_: (_ for _ in ()).throw(AssertionError("solver was called")),
        raising=False,
    )

    exit_code = cli.main(
        [
            "plot-wavefield",
            str(result_path),
            "--component",
            "h_plus",
            "--quantity",
            "real",
            "--out",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert output_path.read_bytes().startswith(b"\x89PNG")
    metadata = json.loads(output_path.with_suffix(".png.json").read_text())
    assert metadata["component"] == "h_plus"
    assert metadata["quantity"] == "real"
    assert metadata["case_id"] == "CLI_PLOT"


def test_cli_plot_wavefield_writes_png_and_sidecar_from_xz_npz(tmp_path, monkeypatch):
    result_path = tmp_path / "xz_result.npz"
    output_path = tmp_path / "xz_plot.png"
    save_results(_synthetic_xz_result(), result_path)
    monkeypatch.setattr(
        cli,
        "compute_polarization",
        lambda **_: (_ for _ in ()).throw(AssertionError("solver was called")),
        raising=False,
    )

    exit_code = cli.main(
        [
            "plot-wavefield",
            str(result_path),
            "--component",
            "h_plus",
            "--quantity",
            "abs",
            "--out",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert output_path.read_bytes().startswith(b"\x89PNG")
    metadata = json.loads(output_path.with_suffix(".png.json").read_text())
    assert metadata["grid_kind"] == "xz_plane"
    assert metadata["x_range"] == [-1.0, 3.0]
    assert metadata["z_range"] == [0.0, 4.0]


def test_cli_plot_fig3_panel_writes_png_and_sidecar_from_xz_npz(tmp_path, monkeypatch):
    result_path = tmp_path / "xz_result.npz"
    output_path = tmp_path / "fig3_panel.png"
    save_results(_synthetic_xz_result(), result_path)
    monkeypatch.setattr(
        cli,
        "compute_polarization",
        lambda **_: (_ for _ in ()).throw(AssertionError("solver was called")),
        raising=False,
    )

    exit_code = cli.main(
        [
            "plot-fig3-panel",
            str(result_path),
            "--quantity",
            "real",
            "--out",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert output_path.read_bytes().startswith(b"\x89PNG")
    metadata = json.loads(output_path.with_suffix(".png.json").read_text())
    assert metadata["plot_type"] == "fig3_lite_panel"
    assert metadata["grid_kind"] == "xz_plane"
    assert metadata["components"] == ["h_plus", "h_cross"]
    assert metadata["overlays"]["drawn"] is True
    assert metadata["overlays"]["event_horizon_radius"] == 2.0
    assert metadata["overlays"]["light_ring_radius"] == pytest.approx(
        3.0 * np.sqrt(3.0)
    )
    assert metadata["colormap"] == "viridis"


def test_cli_plot_fig3_panel_accepts_interpolation_option(tmp_path, monkeypatch):
    result_path = tmp_path / "uniform_xz_result.npz"
    output_path = tmp_path / "fig3_panel_bilinear.png"
    save_results(_synthetic_uniform_xz_result(), result_path)
    monkeypatch.setattr(
        cli,
        "compute_polarization",
        lambda **_: (_ for _ in ()).throw(AssertionError("solver was called")),
        raising=False,
    )

    exit_code = cli.main(
        [
            "plot-fig3-panel",
            str(result_path),
            "--quantity",
            "real",
            "--interpolation",
            "bilinear",
            "--out",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert output_path.read_bytes().startswith(b"\x89PNG")
    metadata = json.loads(output_path.with_suffix(".png.json").read_text())
    assert metadata["interpolation"] == "bilinear"
    assert metadata["grid_spacing"] == {"x": 1.0, "z": 1.0}
    assert metadata["samples_per_wavelength"]["x"] == pytest.approx(2.0 * np.pi)
    assert metadata["samples_per_wavelength"]["z"] == pytest.approx(2.0 * np.pi)


def test_cli_plot_fig3_panel_accepts_dpi_option(tmp_path, monkeypatch):
    result_path = tmp_path / "uniform_xz_result.npz"
    output_path = tmp_path / "fig3_panel_300dpi.png"
    save_results(_synthetic_uniform_xz_result(), result_path)
    monkeypatch.setattr(
        cli,
        "compute_polarization",
        lambda **_: (_ for _ in ()).throw(AssertionError("solver was called")),
        raising=False,
    )

    exit_code = cli.main(
        [
            "plot-fig3-panel",
            str(result_path),
            "--quantity",
            "real",
            "--dpi",
            "300",
            "--out",
            str(output_path),
        ]
    )

    assert exit_code == 0
    metadata = json.loads(output_path.with_suffix(".png.json").read_text())
    assert metadata["requested_dpi"] == 300
    assert metadata["output_format"] == "png"


def test_cli_plot_fig3_multifrequency_panel_writes_png_and_sidecar_from_npz(
    tmp_path, monkeypatch
):
    result_paths = _save_multifrequency_results(tmp_path)
    output_path = tmp_path / "fig3_multifrequency_bilinear.png"
    monkeypatch.setattr(
        cli,
        "compute_polarization",
        lambda **_: (_ for _ in ()).throw(AssertionError("solver was called")),
        raising=False,
    )

    exit_code = cli.main(
        [
            "plot-fig3-multifrequency-panel",
            *(str(path) for path in result_paths),
            "--quantity",
            "real",
            "--interpolation",
            "bilinear",
            "--out",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert output_path.read_bytes().startswith(b"\x89PNG")
    metadata = json.loads(output_path.with_suffix(".png.json").read_text())
    assert metadata["plot_type"] == "fig3_multifrequency_panel"
    assert metadata["source_result_paths"] == [str(path) for path in result_paths]
    assert metadata["kM_values"] == [0.5, 1.0, 1.5, 2.0]
    assert metadata["interpolation"] == "bilinear"
    assert metadata["grid_spacing"] == {"x": 1.0, "z": 1.0}
    assert [item["x"] for item in metadata["samples_per_wavelength"]] == pytest.approx(
        [4.0 * np.pi, 2.0 * np.pi, 2.0 * np.pi / 1.5, np.pi]
    )


def test_cli_plot_fig3_multifrequency_panel_accepts_dpi_option(tmp_path, monkeypatch):
    result_paths = _save_multifrequency_results(tmp_path)
    output_path = tmp_path / "fig3_multifrequency_300dpi.png"
    monkeypatch.setattr(
        cli,
        "compute_polarization",
        lambda **_: (_ for _ in ()).throw(AssertionError("solver was called")),
        raising=False,
    )

    exit_code = cli.main(
        [
            "plot-fig3-multifrequency-panel",
            *(str(path) for path in result_paths),
            "--quantity",
            "real",
            "--dpi",
            "300",
            "--out",
            str(output_path),
        ]
    )

    assert exit_code == 0
    metadata = json.loads(output_path.with_suffix(".png.json").read_text())
    assert metadata["requested_dpi"] == 300
    assert metadata["output_format"] == "png"


def test_cli_plot_fig3_multifrequency_panel_accepts_publication_style(
    tmp_path, monkeypatch
):
    result_paths = _save_multifrequency_results(tmp_path)
    output_path = tmp_path / "fig3_multifrequency_publication.pdf"
    monkeypatch.setattr(
        cli,
        "compute_polarization",
        lambda **_: (_ for _ in ()).throw(AssertionError("solver was called")),
        raising=False,
    )

    exit_code = cli.main(
        [
            "plot-fig3-multifrequency-panel",
            *(str(path) for path in result_paths),
            "--quantity",
            "real",
            "--style",
            "publication",
            "--out",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert output_path.read_bytes().startswith(b"%PDF")
    metadata = json.loads(output_path.with_suffix(".pdf.json").read_text())
    assert metadata["render_style"] == "publication"
    assert metadata["publication_rendering_candidate"] is True
    assert metadata["figure_size_inches"] == [7.1, 3.65]
    assert metadata["output_format"] == "pdf"


def test_cli_plot_fig3_panel_returns_nonzero_for_angular_result(tmp_path):
    result_path = tmp_path / "result.npz"
    save_results(_synthetic_result(), result_path)

    exit_code = cli.main(
        [
            "plot-fig3-panel",
            str(result_path),
            "--quantity",
            "real",
            "--out",
            str(tmp_path / "bad.png"),
        ]
    )

    assert exit_code != 0


def test_cli_plot_fig4_exact_angular_writes_png_and_sidecar_from_npz(
    tmp_path, monkeypatch
):
    result_path = tmp_path / "fig4_angular.npz"
    output_path = tmp_path / "fig4_exact.png"
    save_results(_synthetic_fig4_angular_result(), result_path)
    monkeypatch.setattr(
        cli,
        "compute_polarization",
        lambda **_: (_ for _ in ()).throw(AssertionError("solver was called")),
        raising=False,
    )

    exit_code = cli.main(
        [
            "plot-fig4-exact-angular",
            str(result_path),
            "--out",
            str(output_path),
            "--phi",
            "0.0",
            "--dpi",
            "300",
        ]
    )

    assert exit_code == 0
    assert output_path.read_bytes().startswith(b"\x89PNG")
    metadata = json.loads(output_path.with_suffix(".png.json").read_text())
    assert metadata["plot_type"] == "fig4_exact_angular_curves"
    assert metadata["curve_extraction_policy"] == "fixed_phi_cut"
    assert metadata["no_solver_rerun"] is True
    assert metadata["no_strict_psi4"] is True
    assert metadata["created_by_cli"] is True


def test_cli_plot_fig4_all_frequency_exact_angular_writes_png_and_sidecar_from_npz(
    tmp_path, monkeypatch
):
    result_paths = _save_fig4_all_frequency_angular_results(tmp_path)
    output_path = tmp_path / "fig4_all_frequency.png"
    monkeypatch.setattr(
        cli,
        "compute_polarization",
        lambda **_: (_ for _ in ()).throw(AssertionError("solver was called")),
        raising=False,
    )

    exit_code = cli.main(
        [
            "plot-fig4-all-frequency-exact-angular",
            *(str(path) for path in result_paths),
            "--out",
            str(output_path),
            "--phi",
            "0.0",
            "--dpi",
            "300",
        ]
    )

    assert exit_code == 0
    assert output_path.read_bytes().startswith(b"\x89PNG")
    metadata = json.loads(output_path.with_suffix(".png.json").read_text())
    assert metadata["plot_type"] == "fig4_all_frequency_exact_angular_curves"
    assert metadata["curve_extraction_policy"] == "fixed_phi_cut"
    assert metadata["source_kM_values"] == [0.5, 1.0, 1.5, 2.0]
    assert metadata["no_solver_rerun"] is True
    assert metadata["no_strict_psi4"] is True


def test_cli_plot_amplification_writes_png_and_sidecar_from_npz(tmp_path, monkeypatch):
    result_path = tmp_path / "amplification.npz"
    output_path = tmp_path / "amplification.png"
    save_amplification_results(_synthetic_amplification_result(), result_path)
    monkeypatch.setattr(
        cli,
        "compute_polarization",
        lambda **_: (_ for _ in ()).throw(AssertionError("solver was called")),
        raising=False,
    )

    exit_code = cli.main(
        [
            "plot-amplification",
            str(result_path),
            "--quantity",
            "F_pol_norm",
            "--out",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert output_path.read_bytes().startswith(b"\x89PNG")
    metadata = json.loads(output_path.with_suffix(".png.json").read_text())
    assert metadata["plot_type"] == "pointwise_wave_optics_amplification"
    assert metadata["source_amplification_result_path"] == str(result_path)
    assert metadata["quantity"] == "F_pol_norm"
    assert metadata["mask_field"] == "valid_ratio_norm_mask"


def test_cli_plot_amplification_returns_nonzero_for_invalid_quantity(tmp_path):
    result_path = tmp_path / "amplification.npz"
    save_amplification_results(_synthetic_amplification_result(), result_path)

    exit_code = cli.main(
        [
            "plot-amplification",
            str(result_path),
            "--quantity",
            "transmission",
            "--out",
            str(tmp_path / "bad.png"),
        ]
    )

    assert exit_code != 0


def test_cli_plot_tablei_four_frequency_writes_reporting_artifacts(tmp_path, monkeypatch):
    source_path = tmp_path / "tablei.npz"
    output_dir = tmp_path / "reporting"
    _write_synthetic_tablei_extraction(source_path)
    monkeypatch.setattr(
        cli,
        "compute_polarization",
        lambda **_: (_ for _ in ()).throw(AssertionError("solver was called")),
        raising=False,
    )

    exit_code = cli.main(
        [
            "plot-tablei-four-frequency",
            str(source_path),
            "--out-dir",
            str(output_dir),
            "--dpi",
            "160",
        ]
    )

    assert exit_code == 0
    assert (output_dir / "tablei_four_frequency_values.csv").exists()
    assert (output_dir / "tablei_four_frequency_values.md").exists()
    near_png = output_dir / "fig5_near_axis_tablei_four_frequency_pilot.png"
    far_png = output_dir / "fig6_far_axis_tablei_four_frequency_pilot.png"
    assert near_png.read_bytes().startswith(b"\x89PNG")
    assert far_png.read_bytes().startswith(b"\x89PNG")
    metadata = json.loads(near_png.with_suffix(".png.json").read_text())
    assert metadata["plot_type"] == "tablei_four_frequency_readonly_pilot"
    assert metadata["created_by_cli"] is True
    assert metadata["read_only_from_tablei_extraction"] is True
    assert metadata["no_solver_rerun"] is True
    assert metadata["no_kM4"] is True


def test_cli_plot_wavefield_writes_png_and_sidecar_from_hdf5(tmp_path):
    pytest.importorskip("h5py")
    result_path = tmp_path / "result.h5"
    output_path = tmp_path / "plot_h5.png"
    save_results(_synthetic_result(), result_path)

    exit_code = cli.main(
        [
            "plot-wavefield",
            str(result_path),
            "--component",
            "h_cross",
            "--quantity",
            "abs",
            "--out",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert output_path.read_bytes().startswith(b"\x89PNG")
    metadata = json.loads(output_path.with_suffix(".png.json").read_text())
    assert metadata["component"] == "h_cross"
    assert metadata["quantity"] == "abs"


def test_cli_plot_wavefield_returns_nonzero_for_invalid_quantity(tmp_path):
    result_path = tmp_path / "result.npz"
    save_results(_synthetic_result(), result_path)

    exit_code = cli.main(
        [
            "plot-wavefield",
            str(result_path),
            "--component",
            "h_plus",
            "--quantity",
            "power",
            "--out",
            str(tmp_path / "bad.png"),
        ]
    )

    assert exit_code != 0


def test_cli_plot_convergence_fails_without_saved_history(tmp_path, monkeypatch):
    result_path = tmp_path / "result.npz"
    save_results(_synthetic_result(), result_path)
    monkeypatch.setattr(
        cli,
        "compute_polarization",
        lambda **_: (_ for _ in ()).throw(AssertionError("solver was called")),
        raising=False,
    )

    exit_code = cli.main(
        ["plot-convergence", str(result_path), "--out", str(tmp_path / "conv.png")]
    )

    assert exit_code != 0


def test_cli_plot_convergence_writes_png_from_saved_history(tmp_path, monkeypatch):
    result_path = tmp_path / "result.npz"
    output_path = tmp_path / "conv.png"
    result = _synthetic_result()
    result.metadata["diagnostics"] = _convergence_diagnostics()
    save_results(result, result_path)
    monkeypatch.setattr(
        cli,
        "compute_polarization",
        lambda **_: (_ for _ in ()).throw(AssertionError("solver was called")),
        raising=False,
    )

    exit_code = cli.main(
        ["plot-convergence", str(result_path), "--out", str(output_path)]
    )

    assert exit_code == 0
    assert output_path.read_bytes().startswith(b"\x89PNG")
    metadata = json.loads(output_path.with_suffix(".png.json").read_text())
    assert metadata["lmax_values"] == [2, 3, 4]
    assert metadata["final_lmax_pair"] == [3, 4]


def test_cli_convergence_smoke_run_plots_convergence_and_wavefield(tmp_path):
    result_path = tmp_path / "smoke.npz"
    convergence_path = tmp_path / "convergence.png"
    wavefield_path = tmp_path / "wavefield.png"

    run_exit = cli.main(
        [
            "run",
            "configs/r60_k1_convergence_smoke.yaml",
            "--out",
            str(result_path),
        ]
    )
    convergence_exit = cli.main(
        ["plot-convergence", str(result_path), "--out", str(convergence_path)]
    )
    wavefield_exit = cli.main(
        [
            "plot-wavefield",
            str(result_path),
            "--component",
            "h_plus",
            "--quantity",
            "abs",
            "--out",
            str(wavefield_path),
        ]
    )

    assert run_exit == 0
    assert convergence_exit == 0
    assert wavefield_exit == 0
    with np.load(result_path, allow_pickle=False) as data:
        metadata = json.loads(str(data["metadata_json"]))
    assert metadata["diagnostics"]["lmax_convergence_history"]
    assert convergence_path.read_bytes().startswith(b"\x89PNG")
    assert wavefield_path.read_bytes().startswith(b"\x89PNG")


def _synthetic_result() -> GridResult:
    theta = np.array([0.0, 0.2])
    phi = np.array([0.0, 0.3])
    h_plus = np.array(
        [[1.0 + 0.0j, 2.0 + 1.0j], [3.0 - 0.5j, 4.0 - 1.0j]],
        dtype=np.complex128,
    )
    return GridResult(
        theta=theta,
        phi=phi,
        h_plus=h_plus,
        h_cross=-h_plus,
        metadata={
            "case_id": "CLI_PLOT",
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
            "case_id": "CLI_XZ_PLOT",
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
            "case_id": "CLI_FIG4_ANGULAR",
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


def _save_fig4_all_frequency_angular_results(tmp_path) -> list:
    paths = []
    for kM, case_id in [
        (0.5, "CLI_FIG4_ALL_K0P5"),
        (1.0, "CLI_FIG4_ALL_K1P0"),
        (1.5, "CLI_FIG4_ALL_K1P5"),
        (2.0, "CLI_FIG4_ALL_K2P0"),
    ]:
        path = tmp_path / f"{case_id}.npz"
        save_results(_synthetic_fig4_all_frequency_angular_result(kM, case_id), path)
        paths.append(path)
    return paths


def _synthetic_fig4_all_frequency_angular_result(kM: float, case_id: str) -> GridResult:
    theta = np.linspace(0.0, math.pi, 65)
    phi = np.linspace(0.0, 2.0 * math.pi, 64, endpoint=False)
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
            "case_id": "CLI_XZ_UNIFORM",
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
    F_pol_norm = np.array(
        [
            [np.nan, np.nan, 0.85],
            [1.25, 1.05, 1.18],
        ],
        dtype=float,
    )
    return AmplificationGridResult(
        theta=np.array(
            [
                [np.nan, np.nan, np.pi / 2.0],
                [1.82, 0.0, 0.93],
            ],
            dtype=float,
        ),
        phi=np.array(
            [
                [np.nan, np.nan, 0.0],
                [np.pi, 0.0, 0.0],
            ],
            dtype=float,
        ),
        F_plus_complex=F_plus_complex,
        F_cross_complex=F_cross_complex,
        amplification_plus=amplification_plus,
        amplification_cross=amplification_cross,
        intensity_plus_ratio=amplification_plus * amplification_plus,
        intensity_cross_ratio=amplification_cross * amplification_cross,
        F_pol_norm=F_pol_norm,
        I_pol_ratio=F_pol_norm * F_pol_norm,
        valid_ratio_plus_mask=valid_ratio_plus_mask,
        valid_ratio_cross_mask=valid_ratio_cross_mask,
        valid_ratio_norm_mask=valid_ratio_norm_mask,
        metadata={
            "case_id": "CLI_XZ_AMPLIFICATION",
            "source_case_id": "CLI_XZ",
            "source_lensed_result_path": "/saved/lensed.npz",
            "source_grid": {"kind": "xz_plane"},
            "source_convention": {"fourier": "exp(-i k t)", "units": "G=c=M=1"},
            "grid": {
                "kind": "xz_plane",
                "valid_point_count": int(valid_mask.sum()),
                "invalid_point_count": int(valid_mask.size - valid_mask.sum()),
            },
            "normalization": {
                "baseline": "flat_no_lens",
                "baseline_api": "compute_flat_no_lens_polarization",
            },
        },
        x=x,
        z=z,
        r=r,
        valid_mask=valid_mask,
    )


def _write_synthetic_tablei_extraction(path) -> None:
    kM_values = np.array([0.5, 1.0, 1.5, 2.0], dtype=float)
    point_ids = np.array(
        ["near_axis_x0_z30", "near_axis_x1_z30", "far_axis_x10_z30"]
    )
    point_group = np.array(["near_axis", "near_axis", "far_axis"])
    shape = (kM_values.size, point_ids.size)
    f_plus = np.ones(shape, dtype=np.complex128) * (1.0 + 0.5j)
    f_cross = np.ones(shape, dtype=np.complex128) * (0.5 - 0.25j)
    masks = np.ones(shape, dtype=bool)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        kM_values=kM_values,
        point_ids=point_ids,
        point_group=point_group,
        point_x=np.array([0.0, 1.0, 10.0]),
        point_y=np.zeros(3),
        point_z=np.full(3, 30.0),
        point_r=np.array([30.0, np.sqrt(901.0), np.sqrt(1000.0)]),
        point_theta=np.array([0.0, np.arctan2(1.0, 30.0), np.arctan2(10.0, 30.0)]),
        point_phi=np.zeros(3),
        paper_theta_deg=np.array([0.0, 1.90915, 18.4349]),
        paper_xi_over_xi0=np.array([0.0, 0.0913, 0.9372]),
        x_indices=np.array([60, 62, 80]),
        z_indices=np.array([120, 120, 120]),
        F_plus_complex=f_plus,
        F_cross_complex=f_cross,
        abs_F_plus=np.abs(f_plus),
        abs_F_cross=np.abs(f_cross),
        arg_F_plus_principal=np.angle(f_plus),
        arg_F_cross_principal=np.angle(f_cross),
        arg_F_plus_unwrapped=np.angle(f_plus),
        arg_F_cross_unwrapped=np.angle(f_cross),
        valid_ratio_plus_mask=masks,
        valid_ratio_cross_mask=masks,
        valid_ratio_norm_mask=masks,
        valid_field_mask=masks,
        source_valid_mask=masks,
        metadata_json=np.asarray(
            json.dumps(
                {
                    "case_id": "CLI_TABLEI",
                    "schema_version": "phase5_t8ac_tablei_v1",
                    "phase_policy": {"principal": "angle in (-pi, pi]"},
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
                "case_id": "CLI_TABLEI",
                "schema_version": "phase5_t8ac_tablei_v1",
                "phase_policy": {"principal": "angle in (-pi, pi]"},
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


def _save_multifrequency_results(tmp_path) -> list:
    paths = []
    for kM, case_id in [
        (0.5, "CLI_XZ_K0P5"),
        (1.0, "CLI_XZ_K1P0"),
        (1.5, "CLI_XZ_K1P5"),
        (2.0, "CLI_XZ_K2P0"),
    ]:
        path = tmp_path / f"{case_id}.npz"
        save_results(_synthetic_multifrequency_xz_result(kM, case_id), path)
        paths.append(path)
    return paths


def _synthetic_multifrequency_xz_result(kM: float, case_id: str) -> GridResult:
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
