from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from schwgw import cli
from schwgw.backgrounds import SchwarzschildBackground
from schwgw.io.config import ConfigError, load_config
from schwgw.io.results import (
    AmplificationGridResult,
    GridResult,
    _radial_cache_key,
    load_amplification_results,
    save_amplification_results,
    save_results,
)
from schwgw.numerics import BoundaryConfig
from schwgw.perturbations import Sector
from schwgw.scattering.partial_wave import compute_flat_no_lens_polarization
from schwgw.scattering.partial_wave import compute_polarization
from schwgw.scattering.observables import PolarizationResult


def test_cli_run_writes_npz_from_yaml_config(tmp_path, monkeypatch):
    config = _write_config(tmp_path)
    out = tmp_path / "cli.npz"

    monkeypatch.setattr(cli, "compute_polarization", _fake_solver)

    exit_code = cli.main(["run", str(config), "--out", str(out)])

    assert exit_code == 0
    with np.load(out, allow_pickle=False) as data:
        assert data["h_plus"].shape == (1, 1)
        assert data["h_plus"][0, 0] == 1.0 + 2.0j
        metadata = json.loads(str(data["metadata_json"]))
    assert metadata["source_command"][0] == "schwgw.cli"


def test_cli_run_serializes_and_passes_optional_q018_boundary_fields(tmp_path, monkeypatch):
    config = _write_q018_boundary_config(tmp_path)
    out = tmp_path / "cli_q018_boundary.npz"
    seen_boundaries = []

    def recording_solver(**kwargs):
        seen_boundaries.append(kwargs["boundary_config"])
        return _fake_solver(**kwargs)

    monkeypatch.setattr(cli, "compute_polarization", recording_solver)

    exit_code = cli.main(["run", str(config), "--out", str(out)])

    assert exit_code == 0
    assert seen_boundaries
    assert seen_boundaries[0].required_eval_radius == 60.0
    assert seen_boundaries[0].experimental_required_radius_oracle == "q018_riccati"
    with np.load(out, allow_pickle=False) as data:
        metadata = json.loads(str(data["metadata_json"]))
    assert metadata["config"]["numerics"]["boundary"] == {
        "r_in_eps": 1.0e-6,
        "r_out": 300.0,
        "rtol": 1.0e-10,
        "atol": 1.0e-12,
        "required_eval_radius": 60.0,
        "experimental_required_radius_oracle": "q018_riccati",
    }
    assert metadata["boundary"] == metadata["config"]["numerics"]["boundary"]


def test_radial_cache_key_includes_optional_q018_boundary_fields():
    background = SchwarzschildBackground(M=1.0)
    base = BoundaryConfig(r_in_eps=1e-6, r_out=300.0, rtol=1e-10, atol=1e-12)
    required_radius = BoundaryConfig(
        r_in_eps=1e-6,
        r_out=300.0,
        rtol=1e-10,
        atol=1e-12,
        required_eval_radius=60.0,
    )
    opt_in = BoundaryConfig(
        r_in_eps=1e-6,
        r_out=300.0,
        rtol=1e-10,
        atol=1e-12,
        required_eval_radius=60.0,
        experimental_required_radius_oracle="q018_riccati",
    )

    base_key = _radial_cache_key(Sector.ODD, 153, 2.0, background, base)
    required_key = _radial_cache_key(Sector.ODD, 153, 2.0, background, required_radius)
    opt_in_key = _radial_cache_key(Sector.ODD, 153, 2.0, background, opt_in)

    assert base_key != required_key
    assert required_key != opt_in_key


def test_cli_run_writes_xz_plane_npz_from_yaml_config(tmp_path, monkeypatch):
    config = _write_xz_config(tmp_path)
    out = tmp_path / "cli_xz.npz"

    monkeypatch.setattr(cli, "compute_polarization", _fake_solver)

    exit_code = cli.main(["run", str(config), "--out", str(out)])

    assert exit_code == 0
    with np.load(out, allow_pickle=False) as data:
        assert set(data.files) == {
            "x",
            "z",
            "r",
            "theta",
            "phi",
            "valid_mask",
            "h_plus",
            "h_cross",
            "metadata_json",
        }
        assert data["h_plus"].shape == (2, 3)
        metadata = json.loads(str(data["metadata_json"]))
    assert metadata["grid"]["kind"] == "xz_plane"
    assert metadata["grid"]["valid_point_count"] == 4
    assert metadata["diagnostics"]["skipped_point_count"] == 2


def test_xz_plane_config_reports_missing_x_values(tmp_path):
    config = tmp_path / "missing_x_values.yaml"
    config.write_text(
        """
case_id: CLI_XZ_MISSING_X
output: ignored.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  kind: xz_plane
  z_values: [4.0]
  invalid_radius_policy: mask
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 20.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="Missing required field: observer.x_values"):
        load_config(config)


def test_cli_run_writes_hdf5_from_yaml_config(tmp_path, monkeypatch):
    h5py = pytest.importorskip("h5py")
    config = _write_config(tmp_path)
    out = tmp_path / "cli.h5"

    monkeypatch.setattr(cli, "compute_polarization", _fake_solver)

    exit_code = cli.main(["run", str(config), "--out", str(out)])

    assert exit_code == 0
    with h5py.File(out, "r") as handle:
        assert handle["fields/h_cross"][0, 0] == -1.0 - 2.0j
        metadata = json.loads(handle.attrs["metadata_json"])
    assert metadata["config"]["case_id"] == "CLI_CASE"


def test_cli_run_returns_nonzero_for_invalid_config(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("case_id: bad\n", encoding="utf-8")

    assert cli.main(["run", str(path), "--out", str(tmp_path / "bad.npz")]) != 0


def test_cli_run_smoke_uses_real_production_solver(tmp_path):
    config = Path("configs/r60_k1_smoke.yaml")
    out = tmp_path / "real_solver_smoke.npz"

    exit_code = cli.main(["run", str(config), "--out", str(out)])

    assert exit_code == 0
    with np.load(out, allow_pickle=False) as data:
        assert data["h_plus"].shape == (1, 1)
        assert np.issubdtype(data["h_plus"].dtype, np.complexfloating)
        assert np.isfinite(data["h_plus"][0, 0])
        assert np.isfinite(data["h_cross"][0, 0])
        metadata = json.loads(str(data["metadata_json"]))
    assert metadata["config"]["case_id"] == "R60_K1_SMOKE"
    assert metadata["diagnostics"]["summary"]["radial_solve_count_max"] > 0.0


def test_cli_npz_smoke_matches_direct_production_selected_point(tmp_path):
    config_path = Path("configs/r60_k1_smoke.yaml")
    config = load_config(config_path)
    out = tmp_path / "real_solver_selected_point.npz"

    exit_code = cli.main(["run", str(config_path), "--out", str(out)])

    assert exit_code == 0
    with np.load(out, allow_pickle=False) as data:
        h_plus = data["h_plus"]
        h_cross = data["h_cross"]
        theta = data["theta"]
        phi = data["phi"]
        metadata = json.loads(str(data["metadata_json"]))

    assert h_plus.shape == (
        len(config.observer.theta_values),
        len(config.observer.phi_values),
    )
    assert h_cross.shape == h_plus.shape
    assert np.issubdtype(h_plus.dtype, np.complexfloating)
    assert np.issubdtype(h_cross.dtype, np.complexfloating)
    assert set(metadata) >= {
        "boundary",
        "case_id",
        "config",
        "convention",
        "diagnostics",
        "lmax",
        "source_command",
    }
    assert metadata["convention"]["fourier"] == "exp(-i k t)"
    assert metadata["config"] == config.to_dict()
    assert metadata["lmax"] == config.numerics.lmax
    assert metadata["boundary"] == config.to_dict()["numerics"]["boundary"]
    assert metadata["diagnostics"]["points"]
    assert metadata["diagnostics"]["summary"]["radial_solve_count_max"] == 2.0

    boundary = BoundaryConfig(
        r_in_eps=config.numerics.boundary.r_in_eps,
        r_out=config.numerics.boundary.r_out,
        rtol=config.numerics.boundary.rtol,
        atol=config.numerics.boundary.atol,
    )
    expected = compute_polarization(
        background=SchwarzschildBackground(M=config.background.M),
        k=config.wave.kM / config.background.M,
        r=config.observer.r,
        theta=float(theta[0]),
        phi=float(phi[0]),
        A_plus=config.wave.A_plus,
        A_cross=config.wave.A_cross,
        lmax=config.numerics.lmax,
        boundary_config=boundary,
    )

    assert h_plus[0, 0] == pytest.approx(expected.h_plus, rel=1e-10, abs=1e-12)
    assert h_cross[0, 0] == pytest.approx(expected.h_cross, rel=1e-10, abs=1e-12)


def test_cli_compute_amplification_smoke_writes_npz_from_xz_lensed_result(tmp_path):
    lensed = tmp_path / "lensed.npz"
    out = tmp_path / "amp.npz"
    _write_synthetic_xz_lensed_result(lensed)

    exit_code = cli.main(["compute-amplification", str(lensed), "--out", str(out)])

    assert exit_code == 0
    loaded = load_amplification_results(out)
    assert loaded.F_plus_complex.shape == (2, 2)
    assert loaded.metadata["source_lensed_result_path"] == str(lensed)
    normalization = loaded.metadata["normalization"]
    assert normalization["kind"] == "pointwise_wave_optics_amplification"
    assert normalization["baseline_api"] == "compute_flat_no_lens_polarization"
    assert normalization["no_tiny_M_baseline"] is True
    assert normalization["no_schwarzschild_horizon_boundary_in_baseline"] is True
    assert normalization["mask_fields"] == [
        "valid_ratio_plus_mask",
        "valid_ratio_cross_mask",
        "valid_ratio_norm_mask",
    ]
    assert loaded.metadata["source_command"] == [
        "schwgw.cli",
        "compute-amplification",
        str(lensed),
        "--out",
        str(out),
    ]

    expected_plus, expected_cross = _flat_baseline_arrays()
    np.testing.assert_allclose(
        loaded.F_plus_complex[loaded.valid_ratio_plus_mask],
        _synthetic_h_plus()[loaded.valid_ratio_plus_mask]
        / expected_plus[loaded.valid_ratio_plus_mask],
    )
    np.testing.assert_allclose(
        loaded.F_cross_complex[loaded.valid_ratio_cross_mask],
        _synthetic_h_cross()[loaded.valid_ratio_cross_mask]
        / expected_cross[loaded.valid_ratio_cross_mask],
    )


def test_cli_compute_amplification_masks_cross_ratio_for_pure_plus_input(tmp_path):
    lensed = tmp_path / "pure_plus_lensed.npz"
    out = tmp_path / "pure_plus_amp.npz"
    _write_synthetic_xz_lensed_result(lensed, A_cross=0.0j, h_cross=np.zeros((2, 2)))

    exit_code = cli.main(["compute-amplification", str(lensed), "--out", str(out)])

    assert exit_code == 0
    loaded = load_amplification_results(out)
    np.testing.assert_array_equal(loaded.valid_ratio_cross_mask, np.zeros((2, 2), dtype=bool))
    assert np.all(~np.isfinite(loaded.F_cross_complex.real))
    assert np.all(~np.isfinite(loaded.F_cross_complex.imag))
    assert np.count_nonzero(loaded.valid_ratio_plus_mask) == 3
    assert np.count_nonzero(loaded.valid_ratio_norm_mask) == 3
    assert np.isfinite(loaded.F_plus_complex[loaded.valid_ratio_plus_mask]).all()
    assert np.isfinite(loaded.F_pol_norm[loaded.valid_ratio_norm_mask]).all()


def test_cli_extract_tablei_four_frequency_writes_npz_and_sidecar(tmp_path, monkeypatch):
    source_paths = _write_tablei_sources(tmp_path)
    out = tmp_path / "tablei.npz"
    monkeypatch.setattr(
        cli,
        "compute_polarization",
        lambda **_: (_ for _ in ()).throw(AssertionError("solver was called")),
        raising=False,
    )

    exit_code = cli.main(
        [
            "extract-tablei-four-frequency",
            *(str(path) for path in source_paths),
            "--out",
            str(out),
            "--builtin-points",
            "test-small",
        ]
    )

    assert exit_code == 0
    with np.load(out, allow_pickle=False) as data:
        assert data["F_plus_complex"].shape == (4, 1)
        assert data["F_plus_complex"][0, 0] == complex(521.0, 0.0)
        assert data["valid_ratio_plus_mask"].all()
    metadata = json.loads(out.with_suffix(".npz.json").read_text(encoding="utf-8"))
    assert metadata["case_id"] == "FIG5_FIG6_TABLEI_FOUR_FREQUENCY_READONLY"
    assert metadata["no_solver_rerun"] is True
    assert metadata["no_interpolation"] is True
    assert metadata["no_plotting"] is True


def _fake_solver(**kwargs):
    return PolarizationResult(
        h_plus=1.0 + 2.0j,
        h_cross=-1.0 - 2.0j,
        psi0_hat=0.0j,
        psi4_hat=0.0j,
        lmax=kwargs["lmax"],
        diagnostics={"radial_solve_count": 1.0},
    )


def _write_tablei_sources(tmp_path) -> list[Path]:
    paths = []
    for kM in [0.5, 1.0, 1.5, 2.0]:
        path = tmp_path / f"tablei_k{kM:g}.npz"
        save_amplification_results(_tablei_source(kM), path)
        paths.append(path)
    return paths


def _tablei_source(kM: float) -> AmplificationGridResult:
    x = np.array([-1.0, 0.0, 1.0])
    z = np.array([-1.0, 0.0, 1.0])
    shape = (z.size, x.size)
    f_plus = np.empty(shape, dtype=np.complex128)
    f_cross = np.empty(shape, dtype=np.complex128)
    for z_index in range(z.size):
        for x_index in range(x.size):
            f_plus[z_index, x_index] = complex(1000.0 * kM + 10.0 * z_index + x_index, 0.0)
            f_cross[z_index, x_index] = -f_plus[z_index, x_index]
    masks = np.ones(shape, dtype=bool)
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
        valid_ratio_plus_mask=masks,
        valid_ratio_cross_mask=masks,
        valid_ratio_norm_mask=masks,
        metadata={
            "case_id": f"CLI_TABLEI_K{kM:g}",
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
            "source_lensed_result_path": f"cli_source_k{kM:g}.npz",
            "source_lensed_size_bytes": 2000 + int(10 * kM),
            "source_lensed_sha256": f"cli-sha{kM:g}",
            "source_q018_warning_count": 0,
            "source_q018_warning_codes": [],
        },
        x=x,
        z=z,
        r=np.ones(shape),
        valid_mask=masks,
    )


def _write_synthetic_xz_lensed_result(
    path,
    *,
    A_plus=0.9 + 1.1j,
    A_cross=0.4 + 0.6j,
    h_cross=None,
):
    h_plus = _synthetic_h_plus()
    h_cross_values = _synthetic_h_cross() if h_cross is None else np.asarray(h_cross, dtype=complex)
    h_plus = h_plus.copy()
    h_cross_values = h_cross_values.copy()
    valid_mask = np.array([[True, True], [False, True]])
    h_plus[~valid_mask] = np.nan + 1j * np.nan
    h_cross_values[~valid_mask] = np.nan + 1j * np.nan
    result = GridResult(
        theta=np.array([[np.pi / 2.0, np.pi / 2.0], [np.nan, 0.0]]),
        phi=np.array([[np.pi, 0.0], [np.nan, 0.0]]),
        h_plus=h_plus,
        h_cross=h_cross_values,
        metadata={
            "case_id": "CLI_AMP_LENSED",
            "config": {
                "background": {"M": 1.0},
                "wave": {
                    "kM": 0.5,
                    "A_plus": {"real": A_plus.real, "imag": A_plus.imag},
                    "A_cross": {"real": A_cross.real, "imag": A_cross.imag},
                },
                "numerics": {"lmax": 2},
            },
            "grid": {
                "kind": "xz_plane",
                "valid_point_count": 3,
                "invalid_point_count": 1,
            },
            "convention": {
                "fourier": "exp(-i k t)",
                "units": "G=c=M=1",
                "gauge": "Regge-Wheeler",
                "polarization_bridge": "incident-frame electric tidal packaged scalars",
            },
        },
        x=np.array([-3.0, 3.0]),
        z=np.array([0.0, 4.0]),
        r=np.array([[3.0, 3.0], [1.0, 4.0]]),
        valid_mask=valid_mask,
    )
    save_results(result, path)


def _flat_baseline_arrays():
    theta = np.array([[np.pi / 2.0, np.pi / 2.0], [np.nan, 0.0]])
    phi = np.array([[np.pi, 0.0], [np.nan, 0.0]])
    radius = np.array([[3.0, 3.0], [1.0, 4.0]])
    valid = np.array([[True, True], [False, True]])
    h_plus = np.full((2, 2), np.nan + 1j * np.nan, dtype=np.complex128)
    h_cross = np.full((2, 2), np.nan + 1j * np.nan, dtype=np.complex128)
    for index in zip(*np.nonzero(valid), strict=True):
        baseline = compute_flat_no_lens_polarization(
            k=0.5,
            r=float(radius[index]),
            theta=float(theta[index]),
            phi=float(phi[index]),
            A_plus=0.9 + 1.1j,
            A_cross=0.4 + 0.6j,
            lmax=2,
        )
        h_plus[index] = baseline.h_plus
        h_cross[index] = baseline.h_cross
    return h_plus, h_cross


def _synthetic_h_plus():
    h_plus, _ = _flat_baseline_arrays()
    values = 2.0 * h_plus
    values[0, 1] *= 1.0 - 0.5j
    return values


def _synthetic_h_cross():
    _, h_cross = _flat_baseline_arrays()
    values = 0.5 * h_cross
    values[1, 1] *= -1.0j
    return values


def _write_config(tmp_path):
    path = tmp_path / "cli.yaml"
    path.write_text(
        """
case_id: CLI_CASE
output: ignored.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer: {r: 20.0, theta_values: [0.0], phi_values: [0.0]}
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
        encoding="utf-8",
    )
    return path


def _write_q018_boundary_config(tmp_path):
    path = tmp_path / "cli_q018_boundary.yaml"
    path.write_text(
        """
case_id: CLI_Q018_BOUNDARY
output: ignored.npz
background: {M: 1.0}
wave:
  kM: 2.0
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer: {r: 60.0, theta_values: [0.0], phi_values: [0.0]}
numerics:
  lmax: 2
  boundary:
    r_in_eps: 1.0e-6
    r_out: 300.0
    rtol: 1.0e-10
    atol: 1.0e-12
    required_eval_radius: 60.0
    experimental_required_radius_oracle: q018_riccati
""",
        encoding="utf-8",
    )
    return path


def _write_xz_config(tmp_path):
    path = tmp_path / "cli_xz.yaml"
    path.write_text(
        """
case_id: CLI_XZ_CASE
output: ignored.npz
background: {M: 1.0}
wave:
  kM: 0.5
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  kind: xz_plane
  x_values: [-1.0, 0.0, 3.0]
  z_values: [0.0, 4.0]
  invalid_radius_policy: mask
numerics:
  lmax: 2
  boundary: {r_in_eps: 1.0e-6, r_out: 20.0, rtol: 1.0e-10, atol: 1.0e-12}
""",
        encoding="utf-8",
    )
    return path
