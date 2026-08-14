from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest

from schwgw.io.config import load_config
from schwgw.io.results import (
    AmplificationGridResult,
    load_amplification_results,
    load_results,
    run_solver_grid,
    save_amplification_results,
    save_results,
)
from schwgw.scattering.observables import PolarizationResult


@dataclass(frozen=True)
class _FakeWarning:
    ell: int
    sector: str

    def to_metadata(self):
        return {
            "code": "fake_warning",
            "severity": "warning",
            "ell": self.ell,
            "sector": self.sector,
            "k": 0.5,
        }


@dataclass(frozen=True)
class _FakeRadialDiagnostics:
    warnings: tuple[_FakeWarning, ...] = ()


@dataclass(frozen=True)
class _FakeRadialSolution:
    diagnostics: _FakeRadialDiagnostics


def test_run_solver_grid_calls_solver_for_each_angular_point(tmp_path):
    config = _write_config(tmp_path)
    calls = []

    def fake_solver(**kwargs):
        calls.append((kwargs["theta"], kwargs["phi"]))
        value = complex(kwargs["theta"] + 10.0 * kwargs["phi"], -1.0)
        return PolarizationResult(
            h_plus=value,
            h_cross=2.0 * value,
            psi0_hat=0.0j,
            psi4_hat=0.0j,
            lmax=kwargs["lmax"],
            diagnostics={"radial_solve_count": 1.0},
        )

    result = run_solver_grid(config, polarization_solver=fake_solver)

    assert calls == [(0.0, 0.0), (0.0, 0.3), (0.2, 0.0), (0.2, 0.3)]
    assert result.h_plus.shape == (2, 2)
    assert np.issubdtype(result.h_plus.dtype, np.complexfloating)
    assert result.h_cross[1, 1] == 2.0 * complex(0.2 + 3.0, -1.0)
    assert result.metadata["convention"]["fourier"] == "exp(-i k t)"
    assert result.metadata["convention"]["polarization_bridge"] == (
        "unspecified caller-supplied solver"
    )
    assert result.metadata["convention"]["physical_claim"] is False
    assert result.metadata["config"]["case_id"] == "CASE_IO"
    assert result.metadata["diagnostics"]["points"][0]["radial_solve_count"] == 1.0
    assert "lmax_convergence_history" not in result.metadata["diagnostics"]


def test_run_solver_grid_converts_xz_plane_and_masks_invalid_points(tmp_path):
    config = _write_xz_config(tmp_path)
    calls = []

    def fake_solver(**kwargs):
        calls.append((kwargs["r"], kwargs["theta"], kwargs["phi"]))
        value = complex(kwargs["r"] + kwargs["theta"], kwargs["phi"])
        return PolarizationResult(
            h_plus=value,
            h_cross=-value,
            psi0_hat=0.0j,
            psi4_hat=0.0j,
            lmax=kwargs["lmax"],
            diagnostics={"radial_solve_count": 1.0},
        )

    result = run_solver_grid(config, polarization_solver=fake_solver)

    assert result.x is not None
    assert result.z is not None
    assert result.r is not None
    assert result.valid_mask is not None
    assert result.x.tolist() == [-1.0, 0.0, 3.0]
    assert result.z.tolist() == [0.0, 4.0]
    assert result.h_plus.shape == (2, 3)
    np.testing.assert_array_equal(
        result.valid_mask,
        np.array([[False, False, True], [True, True, True]]),
    )
    assert len(calls) == 4
    assert calls[0] == pytest.approx((3.0, np.pi / 2.0, 0.0))
    assert calls[1][2] == pytest.approx(np.pi)
    assert np.isnan(result.h_plus[0, 0].real)
    assert np.isnan(result.h_plus[0, 0].imag)
    assert result.h_plus[0, 2] == pytest.approx(complex(3.0 + np.pi / 2.0, 0.0))
    grid = result.metadata["grid"]
    assert grid["kind"] == "xz_plane"
    assert grid["valid_point_count"] == 4
    assert grid["invalid_point_count"] == 2
    assert result.metadata["diagnostics"]["valid_point_count"] == 4
    assert result.metadata["diagnostics"]["skipped_point_count"] == 2


def test_run_solver_grid_shares_radial_cache_across_grid_and_convergence(
    tmp_path, monkeypatch
):
    config = _write_config(tmp_path, convergence=True)
    radial_calls = []
    radial_solver_ids = set()

    def fake_radial_solver(sector, ell, k, background, boundary_config):
        sector_value = getattr(sector, "value", sector)
        radial_calls.append((sector_value, ell))
        warnings = (
            (_FakeWarning(ell=ell, sector=sector_value),)
            if sector_value == "odd" and ell == 2
            else ()
        )
        return _FakeRadialSolution(diagnostics=_FakeRadialDiagnostics(warnings=warnings))

    import schwgw.numerics as numerics

    monkeypatch.setattr(numerics, "solve_radial_mode", fake_radial_solver)

    def fake_solver(**kwargs):
        radial_solver = kwargs["radial_solver"]
        radial_solver_ids.add(id(radial_solver))
        for ell in range(2, kwargs["lmax"] + 1):
            radial_solver("odd", ell, kwargs["k"], kwargs["background"], kwargs["boundary_config"])
            radial_solver("even", ell, kwargs["k"], kwargs["background"], kwargs["boundary_config"])
        value = complex(kwargs["lmax"] + kwargs["theta"], kwargs["phi"])
        return PolarizationResult(
            h_plus=value,
            h_cross=-value,
            psi0_hat=0.0j,
            psi4_hat=0.0j,
            lmax=kwargs["lmax"],
            diagnostics={"radial_solve_count": float(2 * (kwargs["lmax"] - 1))},
        )

    result = run_solver_grid(config, polarization_solver=fake_solver)

    assert radial_solver_ids and len(radial_solver_ids) == 1
    assert sorted(radial_calls) == [
        ("even", 2),
        ("even", 3),
        ("even", 4),
        ("odd", 2),
        ("odd", 3),
        ("odd", 4),
    ]
    diagnostics = result.metadata["diagnostics"]
    assert diagnostics["run_radial_cache"] == {
        "enabled": True,
        "unique_solution_count": 6,
        "hit_count": 42,
        "key_count": 6,
    }
    assert diagnostics["radial_diagnostic_warnings"] == [
        {
            "code": "fake_warning",
            "severity": "warning",
            "ell": 2,
            "sector": "odd",
            "k": 0.5,
        }
    ]


def test_run_solver_grid_keeps_solver_without_radial_solver_keyword_compatible(tmp_path):
    config = _write_config(tmp_path)
    calls = []

    def fake_solver(
        *,
        background,
        k,
        r,
        theta,
        phi,
        A_plus,
        A_cross,
        lmax,
        boundary_config,
    ):
        calls.append((theta, phi, lmax))
        return PolarizationResult(
            h_plus=1.0 + 0.0j,
            h_cross=0.0j,
            psi0_hat=0.0j,
            psi4_hat=0.0j,
            lmax=lmax,
            diagnostics={"radial_solve_count": 0.0},
        )

    result = run_solver_grid(config, polarization_solver=fake_solver)

    assert calls == [(0.0, 0.0, 2), (0.0, 0.3, 2), (0.2, 0.0, 2), (0.2, 0.3, 2)]
    assert result.metadata["diagnostics"]["run_radial_cache"] == {
        "enabled": False,
        "unique_solution_count": 0,
        "hit_count": 0,
        "key_count": 0,
    }
    assert result.metadata["diagnostics"]["radial_diagnostic_warnings"] == []


def test_run_solver_grid_writes_convergence_history_with_fake_solver(tmp_path):
    config = _write_config(tmp_path, convergence=True)
    calls = []

    def fake_solver(**kwargs):
        calls.append((kwargs["lmax"], kwargs["theta"], kwargs["phi"]))
        value = complex(kwargs["lmax"] + kwargs["theta"], kwargs["phi"])
        return PolarizationResult(
            h_plus=value,
            h_cross=-2.0 * value,
            psi0_hat=0.0j,
            psi4_hat=0.0j,
            lmax=kwargs["lmax"],
            diagnostics={"radial_solve_count": 1.0},
        )

    result = run_solver_grid(config, polarization_solver=fake_solver)

    diagnostics = result.metadata["diagnostics"]
    history = diagnostics["lmax_convergence_history"]
    assert [row["current_lmax"] for row in history] == [3, 4]
    assert history[0]["previous_lmax"] == 2
    assert history[0]["probe_count"] == 2
    assert history[0]["max_relative_change"] > 0.0
    assert history[0]["near_axis_max_relative_change"] > 0.0
    assert diagnostics["final_lmax_pair"] == [3, 4]
    assert diagnostics["lmax_convergence_policy"]["lmax_values"] == [2, 3, 4]
    assert "final_pair_passed" in diagnostics["lmax_convergence_policy"]
    assert (4, 0.0, 0.0) in calls


def test_save_results_writes_npz_with_complex_arrays_and_json_metadata(tmp_path):
    config = _write_config(tmp_path)
    result = run_solver_grid(config, polarization_solver=_fake_solver)
    out = tmp_path / "out.npz"

    save_results(result, out)

    with np.load(out, allow_pickle=False) as data:
        assert set(data.files) == {"theta", "phi", "h_plus", "h_cross", "metadata_json"}
        assert data["h_plus"].dtype == np.complex128
        assert data["h_plus"].shape == (2, 2)
        metadata = json.loads(str(data["metadata_json"]))
    assert metadata["case_id"] == "CASE_IO"
    assert metadata["config"]["numerics"]["lmax"] == 2
    assert metadata["diagnostics"]["summary"]["radial_solve_count_max"] == 1.0


def test_save_results_writes_xz_plane_npz_schema_and_loads_it(tmp_path):
    config = _write_xz_config(tmp_path)
    result = run_solver_grid(config, polarization_solver=_fake_solver)
    out = tmp_path / "xz.npz"

    save_results(result, out)

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
        assert data["x"].shape == (3,)
        assert data["z"].shape == (2,)
        assert data["r"].shape == (2, 3)
        assert data["valid_mask"].dtype == np.bool_
        metadata = json.loads(str(data["metadata_json"]))
    loaded = load_results(out)
    assert loaded.x is not None
    assert loaded.r is not None
    assert loaded.valid_mask is not None
    assert loaded.theta.shape == (2, 3)
    assert metadata["grid"]["kind"] == "xz_plane"
    np.testing.assert_array_equal(loaded.valid_mask, result.valid_mask)


def test_save_results_writes_hdf5_with_complex_arrays_and_json_metadata(tmp_path):
    h5py = pytest.importorskip("h5py")
    config = _write_config(tmp_path)
    result = run_solver_grid(config, polarization_solver=_fake_solver)
    out = tmp_path / "out.h5"

    save_results(result, out)

    with h5py.File(out, "r") as handle:
        assert set(handle["fields"]) == {"theta", "phi", "h_plus", "h_cross"}
        assert handle["fields/h_plus"].shape == (2, 2)
        assert np.issubdtype(handle["fields/h_cross"].dtype, np.complexfloating)
        metadata = json.loads(handle.attrs["metadata_json"])
    assert metadata["convention"]["units"] == "G=c=M=1"
    assert metadata["config"]["wave"]["A_plus"] == {"real": 0.9, "imag": 1.1}


def test_save_results_writes_xz_plane_hdf5_schema(tmp_path):
    h5py = pytest.importorskip("h5py")
    config = _write_xz_config(tmp_path)
    result = run_solver_grid(config, polarization_solver=_fake_solver)
    out = tmp_path / "xz.h5"

    save_results(result, out)

    with h5py.File(out, "r") as handle:
        assert set(handle["fields"]) == {
            "x",
            "z",
            "r",
            "theta",
            "phi",
            "valid_mask",
            "h_plus",
            "h_cross",
        }
        assert handle["fields/r"].shape == (2, 3)
        metadata = json.loads(handle.attrs["metadata_json"])
    loaded = load_results(out)
    assert loaded.valid_mask is not None
    assert metadata["grid"]["invalid_point_count"] == 2


def test_save_results_keeps_convergence_history_json_safe_in_npz_and_hdf5(tmp_path):
    config = _write_config(tmp_path, convergence=True)
    result = run_solver_grid(config, polarization_solver=_fake_solver)
    npz = tmp_path / "conv.npz"
    save_results(result, npz)

    with np.load(npz, allow_pickle=False) as data:
        metadata = json.loads(str(data["metadata_json"]))
    assert metadata["diagnostics"]["lmax_convergence_history"]

    h5py = pytest.importorskip("h5py")
    h5 = tmp_path / "conv.h5"
    save_results(result, h5)
    with h5py.File(h5, "r") as handle:
        metadata = json.loads(handle.attrs["metadata_json"])
    assert metadata["diagnostics"]["lmax_convergence_history"]


def test_save_amplification_results_npz_round_trip_preserves_arrays_and_metadata(
    tmp_path,
):
    result = _amplification_result()
    out = tmp_path / "amp.npz"

    save_amplification_results(result, out)
    loaded = load_amplification_results(out)

    _assert_amplification_round_trip(loaded, result)
    with np.load(out, allow_pickle=False) as data:
        assert set(data.files) == {
            "x",
            "z",
            "r",
            "theta",
            "phi",
            "valid_mask",
            "F_plus_complex",
            "F_cross_complex",
            "amplification_plus",
            "amplification_cross",
            "intensity_plus_ratio",
            "intensity_cross_ratio",
            "F_pol_norm",
            "I_pol_ratio",
            "valid_ratio_plus_mask",
            "valid_ratio_cross_mask",
            "valid_ratio_norm_mask",
            "metadata_json",
        }
        assert data["F_plus_complex"].dtype == np.complex128
        assert data["valid_ratio_cross_mask"].dtype == np.bool_
        metadata = json.loads(str(data["metadata_json"]))
    assert metadata["normalization"]["kind"] == "pointwise_wave_optics_amplification"
    assert metadata["normalization"]["baseline_api"] == "compute_flat_no_lens_polarization"
    assert metadata["normalization"]["mask_fields"] == [
        "valid_ratio_plus_mask",
        "valid_ratio_cross_mask",
        "valid_ratio_norm_mask",
    ]


def test_save_amplification_results_hdf5_round_trip_preserves_arrays_and_metadata(
    tmp_path,
):
    h5py = pytest.importorskip("h5py")
    result = _amplification_result()
    out = tmp_path / "amp.h5"

    save_amplification_results(result, out)
    loaded = load_amplification_results(out)

    _assert_amplification_round_trip(loaded, result)
    with h5py.File(out, "r") as handle:
        assert set(handle["fields"]) == {
            "x",
            "z",
            "r",
            "theta",
            "phi",
            "valid_mask",
            "F_plus_complex",
            "F_cross_complex",
            "amplification_plus",
            "amplification_cross",
            "intensity_plus_ratio",
            "intensity_cross_ratio",
            "F_pol_norm",
            "I_pol_ratio",
            "valid_ratio_plus_mask",
            "valid_ratio_cross_mask",
            "valid_ratio_norm_mask",
        }
        metadata = json.loads(handle.attrs["metadata_json"])
    assert metadata["normalization"]["no_tiny_M_baseline"] is True
    assert (
        metadata["normalization"]["no_schwarzschild_horizon_boundary_in_baseline"]
        is True
    )


def _fake_solver(**kwargs):
    value = complex(kwargs["theta"], kwargs["phi"])
    return PolarizationResult(
        h_plus=value,
        h_cross=-value,
        psi0_hat=0.0j,
        psi4_hat=0.0j,
        lmax=kwargs["lmax"],
        diagnostics={"radial_solve_count": 1.0},
    )


def _amplification_result() -> AmplificationGridResult:
    shape = (2, 2)
    valid_mask = np.array([[True, True], [False, True]])
    valid_plus = np.array([[True, True], [False, True]])
    valid_cross = np.array([[False, True], [False, True]])
    valid_norm = np.array([[True, True], [False, True]])
    f_plus = np.array(
        [[1.0 + 0.5j, 2.0 - 0.25j], [np.nan + 1j * np.nan, -1.0 + 0.0j]],
        dtype=np.complex128,
    )
    f_cross = np.array(
        [[np.nan + 1j * np.nan, 0.5 + 0.25j], [np.nan + 1j * np.nan, 3.0 - 1.0j]],
        dtype=np.complex128,
    )
    f_norm = np.array([[1.25, 2.5], [np.nan, 3.25]])
    i_norm = f_norm**2
    metadata = {
        "case_id": "AMP_CASE",
        "grid": {
            "kind": "xz_plane",
            "valid_point_count": 3,
            "invalid_point_count": 1,
        },
        "normalization": {
            "kind": "pointwise_wave_optics_amplification",
            "version": "m5a_t1_v1",
            "baseline": "flat_no_lens",
            "baseline_api": "compute_flat_no_lens_polarization",
            "fourier": "exp(-i k t)",
            "incident_direction": "+z",
            "same_k": True,
            "same_A_plus_A_cross": True,
            "same_observer_coordinates": True,
            "polarization_bridge": (
                "Route B incident-frame electric tidal packaged scalars"
            ),
            "no_schwarzschild_horizon_boundary_in_baseline": True,
            "no_tiny_M_baseline": True,
            "excludes_radial_horizon_transmission": True,
            "denominator_policy": (
                "independent masks, NaN where denominator mask is false"
            ),
            "denominator_atol_factor": 1.0e-14,
            "denominator_rtol_factor": 1.0e-12,
            "eps_plus": 1.0e-12,
            "eps_cross": 1.0e-14,
            "eps_norm": 1.0e-12,
            "mask_fields": [
                "valid_ratio_plus_mask",
                "valid_ratio_cross_mask",
                "valid_ratio_norm_mask",
            ],
        },
    }
    return AmplificationGridResult(
        theta=np.array([[0.0, 0.1], [np.nan, 0.2]]),
        phi=np.array([[0.0, np.pi], [np.nan, 0.0]]),
        F_plus_complex=f_plus,
        F_cross_complex=f_cross,
        amplification_plus=np.abs(f_plus),
        amplification_cross=np.abs(f_cross),
        intensity_plus_ratio=np.abs(f_plus) ** 2,
        intensity_cross_ratio=np.abs(f_cross) ** 2,
        F_pol_norm=f_norm,
        I_pol_ratio=i_norm,
        valid_ratio_plus_mask=valid_plus,
        valid_ratio_cross_mask=valid_cross,
        valid_ratio_norm_mask=valid_norm,
        metadata=metadata,
        x=np.array([-1.0, 3.0]),
        z=np.array([0.0, 4.0]),
        r=np.array([[1.0, 3.0], [4.0, 5.0]]),
        valid_mask=valid_mask,
    )


def _assert_amplification_round_trip(
    loaded: AmplificationGridResult,
    expected: AmplificationGridResult,
) -> None:
    for name in (
        "theta",
        "phi",
        "F_plus_complex",
        "F_cross_complex",
        "amplification_plus",
        "amplification_cross",
        "intensity_plus_ratio",
        "intensity_cross_ratio",
        "F_pol_norm",
        "I_pol_ratio",
    ):
        np.testing.assert_allclose(
            getattr(loaded, name),
            getattr(expected, name),
            equal_nan=True,
        )
    for name in (
        "valid_ratio_plus_mask",
        "valid_ratio_cross_mask",
        "valid_ratio_norm_mask",
        "valid_mask",
    ):
        np.testing.assert_array_equal(getattr(loaded, name), getattr(expected, name))
    np.testing.assert_allclose(loaded.x, expected.x)
    np.testing.assert_allclose(loaded.z, expected.z)
    np.testing.assert_allclose(loaded.r, expected.r)
    assert loaded.metadata == expected.metadata


def _write_config(tmp_path: Path, *, convergence: bool = False):
    convergence_block = (
        """
convergence:
  enabled: true
  lmax_values: [2, 3, 4]
  theta_values: [0.0, 0.05]
  phi_values: [0.0]
  selected_threshold: 1.0e-4
  near_axis_threshold: 1.0e-3
"""
        if convergence
        else ""
    )
    path = tmp_path / "case.yaml"
    path.write_text(
        f"""
case_id: CASE_IO
output: out.npz
background: {{M: 1.0}}
wave:
  kM: 0.5
  A_plus: {{real: 0.9, imag: 1.1}}
  A_cross: {{real: 0.4, imag: 0.6}}
observer:
  r: 20.0
  theta_values: [0.0, 0.2]
  phi_values: [0.0, 0.3]
numerics:
  lmax: {4 if convergence else 2}
  boundary: {{r_in_eps: 1.0e-6, r_out: 80.0, rtol: 1.0e-10, atol: 1.0e-12}}
{convergence_block}
""",
        encoding="utf-8",
    )
    return load_config(path)


def _write_xz_config(tmp_path: Path):
    path = tmp_path / "xz_case.yaml"
    path.write_text(
        """
case_id: CASE_XZ
output: out.npz
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
    return load_config(path)
