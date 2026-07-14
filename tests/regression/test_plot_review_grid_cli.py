from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from schwgw import cli
import schwgw.viz.tablei_review_grid as review_grid


KM = np.asarray(
    [
        0.1,
        0.2,
        0.3,
        0.5,
        0.75,
        1.0,
        1.25,
        1.5,
        1.75,
        2.0,
        2.25,
        2.5,
        2.75,
        3.0,
        3.25,
        3.5,
        3.75,
        4.0,
    ]
)
POINT_IDS = np.asarray(
    [
        "near_axis_x0_z30",
        "near_axis_x1_z30",
        "near_axis_x2_z30",
        "near_axis_x3_z30",
        "far_axis_x10_z30",
        "far_axis_x15_z30",
        "far_axis_x20_z30",
        "far_axis_x25_z30",
    ]
)
POINT_X = np.asarray([0, 1, 2, 3, 10, 15, 20, 25], dtype=float)
POINT_Z = np.full(8, 30.0)
POINT_R = np.hypot(POINT_X, POINT_Z)
POINT_THETA = np.arctan2(POINT_X, POINT_Z)
PAPER_XI = 0.5 * np.sqrt(POINT_R) * np.tan(POINT_THETA)
EXPECTED_OUTPUTS = {
    "fig5_near_axis_review_grid.png",
    "fig5_near_axis_review_grid.pdf",
    "fig5_near_axis_review_grid.json",
    "fig6_far_axis_review_grid.png",
    "fig6_far_axis_review_grid.pdf",
    "fig6_far_axis_review_grid.json",
    "sampling_diagnostics.json",
    "manifest.md",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def _write_pair(tmp_path: Path) -> tuple[Path, Path, dict[str, str]]:
    exact_dir = tmp_path / "exact"
    kirchhoff_dir = tmp_path / "kirchhoff"
    exact_dir.mkdir()
    kirchhoff_dir.mkdir()
    exact = exact_dir / "exact.npz"
    kirchhoff = kirchhoff_dir / "kirchhoff.npz"
    phase_plus = KM[:, None] * np.linspace(0.4, 2.4, 8)
    phase_cross = KM[:, None] * np.linspace(0.6, 2.8, 8)
    abs_plus = 1.0 + 0.04 * KM[:, None] + 0.02 * np.arange(8)[None, :]
    abs_cross = 1.1 + 0.03 * KM[:, None] + 0.015 * np.arange(8)[None, :]
    exact_metadata = {
        "case_id": "SYNTHETIC_EXACT_REVIEW_GRID",
        "schema_version": "phase5_t8aj_fig5_fig6_review_grid_v2",
        "no_interpolation": True,
        "no_smoothing": True,
        "no_fill": True,
        "no_plotting": True,
        "no_kirchhoff": True,
        "no_paper_level_production": True,
    }
    np.savez_compressed(
        exact,
        kM_values=KM,
        point_ids=POINT_IDS,
        point_group=np.asarray(["near_axis"] * 4 + ["far_axis"] * 4),
        point_x=POINT_X,
        point_y=np.zeros(8),
        point_z=POINT_Z,
        point_r=POINT_R,
        point_theta=POINT_THETA,
        paper_xi_over_xi0=PAPER_XI,
        F_plus_complex=abs_plus * np.exp(1j * phase_plus),
        F_cross_complex=abs_cross * np.exp(1j * phase_cross),
        abs_F_plus=abs_plus,
        abs_F_cross=abs_cross,
        arg_F_plus_unwrapped=phase_plus,
        arg_F_cross_unwrapped=phase_cross,
        valid_ratio_plus_mask=np.ones((18, 8), dtype=bool),
        valid_ratio_cross_mask=np.ones((18, 8), dtype=bool),
        metadata_json=np.asarray(json.dumps(exact_metadata, sort_keys=True)),
    )
    _write_json(Path(str(exact) + ".json"), exact_metadata)
    (exact_dir / "manifest.md").write_text(
        f"{_sha(exact)}\n{_sha(Path(str(exact) + '.json'))}\n", encoding="utf-8"
    )

    kir_phase = KM[:, None] * np.linspace(0.5, 2.2, 8)
    kir_abs = 0.9 + 0.025 * KM[:, None] + 0.01 * np.arange(8)[None, :]
    dtype = {
        "kM_values": "float64",
        "point_ids": "<U16",
        "point_x": "float64",
        "point_y": "float64",
        "point_z": "float64",
        "point_r": "float64",
        "point_theta": "float64",
        "paper_xi_over_xi0": "float64",
        "F_kirchhoff_complex": "complex128",
        "abs_F_kirchhoff": "float64",
        "arg_F_kirchhoff_unwrapped": "float64",
        "valid_kirchhoff_mask": "bool",
    }
    kirchhoff_metadata = {
        "case_id": "SYNTHETIC_KIRCHHOFF_REVIEW_GRID",
        "schema_version": "phase5_t8al_kirchhoff_review_grid_v2_units_dtype",
        "comparison_only": True,
        "polarization_independent": True,
        "not_denominator": True,
        "not_mask": True,
        "not_normalization": True,
        "no_interpolation": True,
        "no_smoothing": True,
        "no_solver_rerun": True,
        "dtype": dtype,
        "units": {name: "synthetic test unit" for name in dtype},
    }
    np.savez_compressed(
        kirchhoff,
        kM_values=KM,
        point_ids=POINT_IDS,
        point_x=POINT_X,
        point_y=np.zeros(8),
        point_z=POINT_Z,
        point_r=POINT_R,
        point_theta=POINT_THETA,
        paper_xi_over_xi0=PAPER_XI,
        F_kirchhoff_complex=kir_abs * np.exp(1j * kir_phase),
        abs_F_kirchhoff=kir_abs,
        arg_F_kirchhoff_unwrapped=kir_phase,
        valid_kirchhoff_mask=np.ones((18, 8), dtype=bool),
        metadata_json=np.asarray(json.dumps(kirchhoff_metadata, sort_keys=True)),
    )
    kir_sidecar = dict(kirchhoff_metadata)
    kir_sidecar["output_npz_path"] = str(kirchhoff)
    kir_sidecar["output_npz_sha256"] = _sha(kirchhoff)
    _write_json(Path(str(kirchhoff) + ".json"), kir_sidecar)
    (kirchhoff_dir / "manifest.md").write_text(
        f"{_sha(kirchhoff)}\n{_sha(Path(str(kirchhoff) + '.json'))}\n",
        encoding="utf-8",
    )
    hashes = {
        "exact_npz": _sha(exact),
        "exact_json": _sha(Path(str(exact) + ".json")),
        "exact_manifest": _sha(exact_dir / "manifest.md"),
        "kirchhoff_npz": _sha(kirchhoff),
        "kirchhoff_json": _sha(Path(str(kirchhoff) + ".json")),
        "kirchhoff_manifest": _sha(kirchhoff_dir / "manifest.md"),
    }
    return exact, kirchhoff, hashes


def test_cli_plot_review_grid_writes_exact_eight_outputs(tmp_path, monkeypatch) -> None:
    exact, kirchhoff, hashes = _write_pair(tmp_path)
    monkeypatch.setattr(review_grid, "_FROZEN_SOURCE_HASHES", hashes)
    output_dir = tmp_path / "outputs"

    exit_code = cli.main(
        [
            "plot-tablei-review-grid",
            str(exact),
            str(kirchhoff),
            "--out-dir",
            str(output_dir),
            "--dpi",
            "90",
        ]
    )

    assert exit_code == 0
    assert {path.name for path in output_dir.iterdir()} == EXPECTED_OUTPUTS
    sidecar = json.loads(
        (output_dir / "fig5_near_axis_review_grid.json").read_text(encoding="utf-8")
    )
    assert sidecar["created_by_cli"] is True


def test_cli_plot_review_grid_missing_kirchhoff_sidecar_fails_closed(
    tmp_path, monkeypatch, capsys
) -> None:
    exact, kirchhoff, hashes = _write_pair(tmp_path)
    monkeypatch.setattr(review_grid, "_FROZEN_SOURCE_HASHES", hashes)
    Path(str(kirchhoff) + ".json").unlink()

    exit_code = cli.main(
        [
            "plot-tablei-review-grid",
            str(exact),
            str(kirchhoff),
            "--out-dir",
            str(tmp_path / "outputs"),
        ]
    )

    assert exit_code == 2
    assert "missing source file" in capsys.readouterr().err
