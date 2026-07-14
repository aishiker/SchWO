from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

import schwgw.viz.tablei_review_grid as review_grid
from schwgw.viz.tablei_review_grid import (
    ReviewGridPlotError,
    plot_tablei_review_grid_diagnostics,
)


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
    ],
    dtype=float,
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
POINT_GROUP = np.asarray(["near_axis"] * 4 + ["far_axis"] * 4)
POINT_X = np.asarray([0, 1, 2, 3, 10, 15, 20, 25], dtype=float)
POINT_Z = np.full(8, 30.0)
POINT_R = np.hypot(POINT_X, POINT_Z)
POINT_THETA = np.arctan2(POINT_X, POINT_Z)
PAPER_XI = 0.5 * np.sqrt(POINT_R) * np.tan(POINT_THETA)

OUTPUT_NAMES = {
    "fig5_near_axis_review_grid.png",
    "fig5_near_axis_review_grid.pdf",
    "fig5_near_axis_review_grid.json",
    "fig6_far_axis_review_grid.png",
    "fig6_far_axis_review_grid.pdf",
    "fig6_far_axis_review_grid.json",
    "sampling_diagnostics.json",
    "manifest.md",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_mapping(exact: Path, kirchhoff: Path) -> dict[str, str]:
    return {
        "exact_npz": _sha256(exact),
        "exact_json": _sha256(Path(str(exact) + ".json")),
        "exact_manifest": _sha256(exact.parent / "manifest.md"),
        "kirchhoff_npz": _sha256(kirchhoff),
        "kirchhoff_json": _sha256(Path(str(kirchhoff) + ".json")),
        "kirchhoff_manifest": _sha256(kirchhoff.parent / "manifest.md"),
    }


def _write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_pair(
    tmp_path: Path,
    *,
    invalid_plus: tuple[int, int] | None = None,
) -> tuple[Path, Path, dict[str, str]]:
    exact_dir = tmp_path / "exact"
    kirchhoff_dir = tmp_path / "kirchhoff"
    exact_dir.mkdir()
    kirchhoff_dir.mkdir()
    exact = exact_dir / "tablei_dense_review_values.npz"
    kirchhoff = kirchhoff_dir / "tablei_kirchhoff_baseline_values.npz"

    phase_plus = KM[:, None] * np.linspace(0.4, 2.4, 8)
    phase_cross = KM[:, None] * np.linspace(0.6, 2.8, 8)
    abs_plus = 1.0 + 0.04 * KM[:, None] + 0.02 * np.arange(8)[None, :]
    abs_cross = 1.1 + 0.03 * KM[:, None] + 0.015 * np.arange(8)[None, :]
    f_plus = abs_plus * np.exp(1j * phase_plus)
    f_cross = abs_cross * np.exp(1j * phase_cross)
    plus_mask = np.ones((18, 8), dtype=bool)
    if invalid_plus is not None:
        plus_mask[invalid_plus] = False
        f_plus[invalid_plus] = np.nan + 1j * np.nan
        abs_plus[invalid_plus] = np.nan
        phase_plus[invalid_plus] = np.nan
    cross_mask = np.ones((18, 8), dtype=bool)
    exact_metadata = {
        "case_id": "SYNTHETIC_EXACT_REVIEW_GRID",
        "schema_version": "phase5_t8aj_fig5_fig6_review_grid_v2",
        "no_interpolation": True,
        "no_smoothing": True,
        "no_fill": True,
        "no_plotting": True,
        "no_kirchhoff": True,
        "no_paper_level_production": True,
        "not_40_frequency_production": True,
    }
    np.savez_compressed(
        exact,
        kM_values=KM,
        point_ids=POINT_IDS,
        point_group=POINT_GROUP,
        point_x=POINT_X,
        point_y=np.zeros(8),
        point_z=POINT_Z,
        point_r=POINT_R,
        point_theta=POINT_THETA,
        paper_xi_over_xi0=PAPER_XI,
        F_plus_complex=f_plus,
        F_cross_complex=f_cross,
        abs_F_plus=abs_plus,
        abs_F_cross=abs_cross,
        arg_F_plus_unwrapped=phase_plus,
        arg_F_cross_unwrapped=phase_cross,
        valid_ratio_plus_mask=plus_mask,
        valid_ratio_cross_mask=cross_mask,
        metadata_json=np.asarray(json.dumps(exact_metadata, sort_keys=True)),
    )
    _write_json(Path(str(exact) + ".json"), exact_metadata)
    exact_npz_hash = _sha256(exact)
    exact_json_hash = _sha256(Path(str(exact) + ".json"))
    (exact_dir / "manifest.md").write_text(
        f"exact NPZ {exact_npz_hash}\nexact JSON {exact_json_hash}\n",
        encoding="utf-8",
    )

    kirchhoff_phase = KM[:, None] * np.linspace(0.5, 2.2, 8)
    kirchhoff_abs = 0.9 + 0.025 * KM[:, None] + 0.01 * np.arange(8)[None, :]
    kirchhoff_values = kirchhoff_abs * np.exp(1j * kirchhoff_phase)
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
        "dtype": {
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
        },
        "units": {"F_kirchhoff_complex": "dimensionless"},
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
        F_kirchhoff_complex=kirchhoff_values,
        abs_F_kirchhoff=kirchhoff_abs,
        arg_F_kirchhoff_unwrapped=kirchhoff_phase,
        valid_kirchhoff_mask=np.ones((18, 8), dtype=bool),
        metadata_json=np.asarray(json.dumps(kirchhoff_metadata, sort_keys=True)),
    )
    kirchhoff_sidecar = dict(kirchhoff_metadata)
    kirchhoff_sidecar.update(
        {
            "output_npz_path": str(kirchhoff),
            "output_npz_sha256": _sha256(kirchhoff),
        }
    )
    _write_json(Path(str(kirchhoff) + ".json"), kirchhoff_sidecar)
    kirchhoff_npz_hash = _sha256(kirchhoff)
    kirchhoff_json_hash = _sha256(Path(str(kirchhoff) + ".json"))
    (kirchhoff_dir / "manifest.md").write_text(
        f"Kirchhoff NPZ {kirchhoff_npz_hash}\nKirchhoff JSON {kirchhoff_json_hash}\n",
        encoding="utf-8",
    )
    return exact, kirchhoff, _hash_mapping(exact, kirchhoff)


def _patch_hashes(monkeypatch: pytest.MonkeyPatch, hashes: dict[str, str]) -> None:
    monkeypatch.setattr(review_grid, "_FROZEN_SOURCE_HASHES", hashes)


def test_review_grid_plot_api_is_importable() -> None:
    assert callable(plot_tablei_review_grid_diagnostics)


def test_plot_review_grid_writes_exact_eight_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exact, kirchhoff, hashes = write_pair(tmp_path)
    _patch_hashes(monkeypatch, hashes)

    paths = plot_tablei_review_grid_diagnostics(
        exact, kirchhoff, output_dir=tmp_path / "outputs", dpi=90
    )

    assert {path.name for path in paths.values()} == OUTPUT_NAMES
    assert {path.name for path in (tmp_path / "outputs").iterdir()} == OUTPUT_NAMES
    assert paths["fig5_png"].read_bytes().startswith(b"\x89PNG")
    assert paths["fig6_png"].read_bytes().startswith(b"\x89PNG")
    assert paths["fig5_pdf"].read_bytes().startswith(b"%PDF-")
    assert paths["fig6_pdf"].read_bytes().startswith(b"%PDF-")
    assert paths["fig5_png"].stat().st_size > 1000
    assert paths["fig6_png"].stat().st_size > 1000
    sidecar = json.loads(paths["fig5_json"].read_text(encoding="utf-8"))
    assert sidecar["flags"]["no_physics_recomputation"] is True
    assert sidecar["flags"]["kirchhoff_polarization_independent"] is True
    assert sidecar["output_sha256"]["png"] == _sha256(paths["fig5_png"])
    assert sidecar["output_sha256"]["pdf"] == _sha256(paths["fig5_pdf"])
    manifest = paths["manifest"].read_text(encoding="utf-8")
    for key in ("fig5_png", "fig5_pdf", "fig5_json", "fig6_png", "fig6_pdf", "fig6_json", "diagnostics"):
        assert _sha256(paths[key]) in manifest


def test_plot_review_grid_rejects_missing_sidecar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exact, kirchhoff, hashes = write_pair(tmp_path)
    _patch_hashes(monkeypatch, hashes)
    Path(str(kirchhoff) + ".json").unlink()

    with pytest.raises(ReviewGridPlotError, match="missing source file"):
        plot_tablei_review_grid_diagnostics(
            exact, kirchhoff, output_dir=tmp_path / "outputs"
        )


def test_plot_review_grid_rejects_source_hash_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exact, kirchhoff, hashes = write_pair(tmp_path)
    _patch_hashes(monkeypatch, hashes)
    Path(str(exact) + ".json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(ReviewGridPlotError, match="frozen source hash mismatch"):
        plot_tablei_review_grid_diagnostics(
            exact, kirchhoff, output_dir=tmp_path / "outputs"
        )


def test_plot_review_grid_rejects_grid_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exact, kirchhoff, _ = write_pair(tmp_path)
    with np.load(kirchhoff, allow_pickle=False) as data:
        arrays = {name: data[name] for name in data.files}
    arrays["point_x"] = arrays["point_x"].copy()
    arrays["point_x"][1] += 0.5
    np.savez_compressed(kirchhoff, **arrays)
    sidecar = json.loads(Path(str(kirchhoff) + ".json").read_text(encoding="utf-8"))
    sidecar["output_npz_sha256"] = _sha256(kirchhoff)
    _write_json(Path(str(kirchhoff) + ".json"), sidecar)
    (kirchhoff.parent / "manifest.md").write_text(
        f"Kirchhoff NPZ {_sha256(kirchhoff)}\n"
        f"Kirchhoff JSON {_sha256(Path(str(kirchhoff) + '.json'))}\n",
        encoding="utf-8",
    )
    _patch_hashes(monkeypatch, _hash_mapping(exact, kirchhoff))

    with pytest.raises(ReviewGridPlotError, match="paired grid mismatch"):
        plot_tablei_review_grid_diagnostics(
            exact, kirchhoff, output_dir=tmp_path / "outputs"
        )


def test_plot_review_grid_rejects_metadata_flag_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exact, kirchhoff, _ = write_pair(tmp_path)
    with np.load(exact, allow_pickle=False) as data:
        arrays = {name: data[name] for name in data.files}
    metadata = json.loads(str(arrays["metadata_json"].item()))
    metadata["no_smoothing"] = False
    arrays["metadata_json"] = np.asarray(json.dumps(metadata, sort_keys=True))
    np.savez_compressed(exact, **arrays)
    _write_json(Path(str(exact) + ".json"), metadata)
    (exact.parent / "manifest.md").write_text(
        f"exact NPZ {_sha256(exact)}\n"
        f"exact JSON {_sha256(Path(str(exact) + '.json'))}\n",
        encoding="utf-8",
    )
    _patch_hashes(monkeypatch, _hash_mapping(exact, kirchhoff))

    with pytest.raises(ReviewGridPlotError, match="required metadata flag"):
        plot_tablei_review_grid_diagnostics(
            exact, kirchhoff, output_dir=tmp_path / "outputs"
        )


def test_sampling_metrics_are_deterministic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exact, kirchhoff, hashes = write_pair(tmp_path)
    _patch_hashes(monkeypatch, hashes)
    sources = review_grid._load_and_validate_sources(exact, kirchhoff)

    first = review_grid._sampling_diagnostics(sources)
    second = review_grid._sampling_diagnostics(sources)

    assert first == second
    assert first["sampling_recommendation"] == "DELTA_0P1_PROVISIONAL_REVIEW"
    phase_plus = KM[:, None] * np.linspace(0.4, 2.4, 8)
    expected = 1.5 * 0.1 * float(
        np.max(np.abs(np.diff(phase_plus[:, :4], axis=0)) / np.diff(KM)[:, None])
    )
    actual = first["groups"]["near_axis"]["plus"]["phase"][
        "safety_projected_phase_step_0p1"
    ]
    assert actual == pytest.approx(expected)
    assert first["groups"]["near_axis"]["plus"]["phase"]["phase_proxy_pass"] is True


def test_invalid_pair_is_not_connected_or_filled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exact, kirchhoff, hashes = write_pair(tmp_path, invalid_plus=(5, 0))
    _patch_hashes(monkeypatch, hashes)
    sources = review_grid._load_and_validate_sources(exact, kirchhoff)
    diagnostics = review_grid._sampling_diagnostics(sources)

    pairs = diagnostics["groups"]["near_axis"]["plus"]["adjacent_pairs"]
    point_pairs = [pair for pair in pairs if pair["point_id"] == POINT_IDS[0]]
    assert point_pairs[4]["valid_endpoint_pair"] is False
    assert point_pairs[5]["valid_endpoint_pair"] is False
    assert point_pairs[4]["absolute_magnitude_step"] is None
    segments = review_grid._valid_segments(KM, sources["abs_plus"][:, 0], sources["plus_mask"][:, 0])
    assert all(not (segment[0][0] < KM[5] < segment[0][-1]) for segment in segments)
