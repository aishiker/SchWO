from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from schwgw.io.kirchhoff import generate_kirchhoff_review_grid_artifact


KM_VALUES = np.array(
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
POINT_X = np.array([0.0, 1.0, 2.0, 3.0, 10.0, 15.0, 20.0, 25.0])
POINT_Z = np.full(8, 30.0)
POINT_IDS = np.array(
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
PAPER_XI = np.array([0.0, 0.0913, 0.1828, 0.2745, 0.9372, 1.4479, 2.0015, 2.6038])

EXPECTED_UNITS = {
    "kM_values": "dimensionless (M k)",
    "point_ids": "identifier",
    "point_x": "dimensionless (x/M)",
    "point_y": "dimensionless (y/M)",
    "point_z": "dimensionless (z/M)",
    "point_r": "dimensionless (r/M)",
    "point_theta": "radian",
    "paper_xi_over_xi0": "dimensionless",
    "gamma": "dimensionless",
    "eta": "dimensionless",
    "eta_minus_paper": "dimensionless",
    "F_kirchhoff_complex": "dimensionless",
    "abs_F_kirchhoff": "dimensionless",
    "arg_F_kirchhoff_principal": "radian",
    "arg_F_kirchhoff_unwrapped": "radian",
    "valid_kirchhoff_mask": "boolean",
}

EXPECTED_DTYPES = {
    "kM_values": "float64",
    "point_ids": "<U16",
    "point_x": "float64",
    "point_y": "float64",
    "point_z": "float64",
    "point_r": "float64",
    "point_theta": "float64",
    "paper_xi_over_xi0": "float64",
    "gamma": "float64",
    "eta": "float64",
    "eta_minus_paper": "float64",
    "F_kirchhoff_complex": "complex128",
    "abs_F_kirchhoff": "float64",
    "arg_F_kirchhoff_principal": "float64",
    "arg_F_kirchhoff_unwrapped": "float64",
    "valid_kirchhoff_mask": "bool",
}


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_source(tmp_path: Path, *, mutate_kM: bool = False) -> Path:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    source = source_dir / "tablei_dense_review_values.npz"
    kM = KM_VALUES.copy()
    if mutate_kM:
        kM[4] += 0.01
    point_y = np.zeros(8)
    point_r = np.hypot(POINT_X, POINT_Z)
    point_theta = np.arctan2(POINT_X, POINT_Z)
    np.savez(
        source,
        kM_values=kM,
        point_ids=POINT_IDS,
        point_x=POINT_X,
        point_y=point_y,
        point_z=POINT_Z,
        point_r=point_r,
        point_theta=point_theta,
        paper_xi_over_xi0=PAPER_XI,
    )
    Path(str(source) + ".json").write_text("{}\n", encoding="utf-8")
    (source_dir / "manifest.md").write_text("synthetic source\n", encoding="utf-8")
    return source


def test_generate_kirchhoff_review_grid_artifact_contract(tmp_path: Path) -> None:
    source = _write_source(tmp_path)
    output_npz, sidecar, manifest = generate_kirchhoff_review_grid_artifact(
        source,
        tmp_path / "output",
        dps=40,
        enforce_accepted_source=False,
    )

    assert output_npz.name == "tablei_kirchhoff_baseline_values.npz"
    assert sidecar == Path(str(output_npz) + ".json")
    assert manifest == output_npz.parent / "manifest.md"
    required_arrays = {
        "kM_values",
        "point_ids",
        "point_x",
        "point_y",
        "point_z",
        "point_r",
        "point_theta",
        "paper_xi_over_xi0",
        "gamma",
        "eta",
        "eta_minus_paper",
        "F_kirchhoff_complex",
        "abs_F_kirchhoff",
        "arg_F_kirchhoff_principal",
        "arg_F_kirchhoff_unwrapped",
        "valid_kirchhoff_mask",
        "metadata_json",
    }
    with np.load(output_npz, allow_pickle=False) as data:
        assert required_arrays <= set(data.files)
        assert data["F_kirchhoff_complex"].shape == (18, 8)
        assert data["valid_kirchhoff_mask"].all()
        assert np.max(np.abs(data["eta_minus_paper"])) < 5.0e-5
        embedded = json.loads(str(data["metadata_json"].item()))
        assert embedded["schema_version"] == (
            "phase5_kirchhoff_review_grid_v3_explicit_convention"
        )
        assert embedded["units"] == EXPECTED_UNITS
        assert embedded["dtype"] == EXPECTED_DTYPES
        for name, expected_dtype in EXPECTED_DTYPES.items():
            assert str(data[name].dtype) == expected_dtype
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    assert metadata["schema_version"] == (
        "phase5_kirchhoff_review_grid_v3_explicit_convention"
    )
    assert metadata["prefactor_convention"] == "standard_point_mass"
    assert metadata["formula_and_branches"]["real_exponential_prefactor"] == (
        "exp(-pi gamma/2)"
    )
    assert metadata["units"] == EXPECTED_UNITS
    assert metadata["dtype"] == EXPECTED_DTYPES
    manifest_text = manifest.read_text(encoding="utf-8")
    assert "## Units and dtypes" in manifest_text
    assert "standard point-mass exp(-pi gamma/2)" in manifest_text
    for name in EXPECTED_UNITS:
        expected_line = (
            f"- `{name}`: unit=`{EXPECTED_UNITS[name]}`; "
            f"dtype=`{EXPECTED_DTYPES[name]}`"
        )
        assert expected_line in manifest_text
    assert metadata["comparison_only"] is True
    assert metadata["not_denominator"] is True
    assert metadata["not_mask"] is True
    assert metadata["not_normalization"] is True
    assert metadata["polarization_independent"] is True
    assert metadata["no_solver_rerun"] is True
    assert metadata["no_plotting"] is True
    assert metadata["not_40_frequency_production"] is True
    assert metadata["no_fixtures"] is True
    assert metadata["no_paper_style_candidates"] is True
    assert metadata["output_npz_sha256"] == _file_sha256(output_npz)


def test_generate_rejects_nonaccepted_frequency_grid(tmp_path: Path) -> None:
    source = _write_source(tmp_path, mutate_kM=True)
    with pytest.raises(ValueError, match="exact accepted 18-frequency grid"):
        generate_kirchhoff_review_grid_artifact(
            source,
            tmp_path / "output",
            enforce_accepted_source=False,
        )
