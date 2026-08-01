from __future__ import annotations

from types import SimpleNamespace

import matplotlib.pyplot as plt
import numpy as np

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.paper_figures.li_hou_zhao import (
    FIG2_KM,
    FIG2_THETA,
    compute_figure1_dataset,
    compute_strict_np_psi4_convergence,
    leading_radial_asymptote,
    load_figure1_dataset,
    load_figure2_dataset,
    normalized_radial,
    save_figure1_dataset,
    save_figure2_dataset,
)
from schwgw.paper_figures.li_hou_zhao_render import (
    _save_formats,
    build_figure1_figure,
    build_figure2_figure,
    build_figure2_reference_comparison,
)
from schwgw.perturbations import Sector, reconstruct_metric_mode
from schwgw.scattering.weyl import assemble_weyl_scalars, weyl_mode_components
from schwgw.waves.incident import IncidentPlaneGW


class _FakeRadialSolution:
    def __init__(self, sector: Sector, ell: int, k: float) -> None:
        self.sector = sector
        self.ell = ell
        self.k = k
        self.background = SchwarzschildBackground(M=1.0)
        self.A_in = 1.0 + 0.0j
        self.phase_factor = complex(0.65 + 0.001 * ell, 0.17 if sector is Sector.ODD else -0.11)
        self.A_out = -((-1) ** ell) * self.A_in * self.phase_factor
        self.phase_shift = 123.0 + 456.0j  # Must not enter the asymptote.
        self.valid_until_r = 300.0
        self.diagnostics = SimpleNamespace(
            atol=1.0e-12,
            barrier_action=0.0,
            boundary_residual=1.0e-12,
            flux_residual=2.0e-12,
            match_condition_number=3.0,
            ode_n_steps=17,
            ode_status="success",
            r_in=2.000001,
            r_out=300.0,
            raw_wronskian_residual=4.0e-12,
            rtol=1.0e-10,
            solver="fake-test-solver",
            warnings=(),
            wronskian_residual=4.0e-12,
        )

    def psi_at(self, r):
        radius = np.asarray(r, dtype=np.float64)
        value = (0.3 + 0.01 * self.ell) + 1j * (
            0.02 * radius + (0.07 if self.sector is Sector.ODD else -0.04)
        )
        return complex(value) if radius.shape == () else value.astype(np.complex128)

    def dpsi_dr_at(self, r):
        radius = np.asarray(r, dtype=np.float64)
        value = np.zeros_like(radius, dtype=np.complex128) + 0.02j
        return complex(value) if radius.shape == () else value


def _fake_solver(sector, ell, k, background, boundary_config):
    assert background == SchwarzschildBackground(M=1.0)
    assert boundary_config.required_eval_radius is not None
    return _FakeRadialSolution(Sector(sector), ell, k)


def test_radial_normalization_phase_identity_and_tortoise_coordinate() -> None:
    solution = _FakeRadialSolution(Sector.ODD, 3, 1.0)
    radius = np.asarray((6.0, 12.0, 60.0))
    np.testing.assert_array_equal(
        normalized_radial(solution, radius),
        solution.psi_at(radius) / solution.A_in,
    )
    expected = np.exp(-1j * solution.k * solution.background.r_star(radius)) + (
        solution.A_out / solution.A_in
    ) * np.exp(1j * solution.k * solution.background.r_star(radius))
    np.testing.assert_array_equal(leading_radial_asymptote(solution, radius), expected)
    areal_radius_wrong = np.exp(-1j * radius) + (solution.A_out / solution.A_in) * np.exp(
        1j * radius
    )
    assert not np.array_equal(expected, areal_radius_wrong)
    assert solution.A_out / solution.A_in == -((-1) ** solution.ell) * solution.phase_factor


def test_figure1_shapes_order_sectors_round_trip_and_plot(tmp_path) -> None:
    dataset = compute_figure1_dataset(
        radial_solver=_fake_solver,
        r=np.linspace(6.0, 66.0, 9),
    )
    assert dataset.metadata["solve_count"] == 16
    assert dataset.metadata["primary_sector"] == "odd"
    assert dataset.exact_odd.shape == (8, 9)
    assert dataset.exact_even.shape == (8, 9)
    assert not np.array_equal(dataset.exact_odd, dataset.exact_even)
    npz, _ = save_figure1_dataset(dataset, tmp_path / "fig1")
    loaded = load_figure1_dataset(npz)
    np.testing.assert_array_equal(loaded.exact_odd, dataset.exact_odd)
    figure = build_figure1_figure(loaded, sector="odd", style="journal")
    assert len(figure.axes) == 8
    assert all(len(axis.lines) == 4 for axis in figure.axes)
    plt.close(figure)


def _direct_shell_psi4(k: float, theta: float, ell: int, radius: float = 60.0) -> complex:
    background = SchwarzschildBackground(M=1.0)
    incident = IncidentPlaneGW(k=k, A_plus=0.9 + 1.1j, A_cross=0.4 + 0.6j)
    modes = []
    for sector in (Sector.ODD, Sector.EVEN):
        solution = _FakeRadialSolution(sector, ell, k)
        for m in range(-ell, ell + 1):
            coefficient = (
                incident.c_lm_odd(ell, m)
                if sector is Sector.ODD
                else incident.c_lm_even(ell, m)
            )
            if coefficient == 0.0:
                continue
            scale = coefficient / solution.A_in
            metric = reconstruct_metric_mode(
                sector,
                ell,
                k,
                radius,
                scale * solution.psi_at(radius),
                scale * solution.dpsi_dr_at(radius),
                background,
            )
            modes.append(
                weyl_mode_components(
                    sector, ell, m, k, radius, theta, 0.0, metric, background
                )
            )
    return complex(assemble_weyl_scalars(modes)["Psi4"])


def test_strict_psi4_is_direct_kinnersley_cumulative_and_shared(monkeypatch) -> None:
    import schwgw.scattering.partial_wave as partial_wave
    import schwgw.scattering.weyl as weyl

    def forbidden(*args, **kwargs):
        raise AssertionError("incident-tetrad/package/polarization route was called")

    monkeypatch.setattr(weyl, "transform_strict_np_weyl_to_incident_tetrad", forbidden)
    monkeypatch.setattr(weyl, "compute_packaged_polarization_scalars", forbidden)
    monkeypatch.setattr(partial_wave, "compute_polarization", forbidden)
    calls = []

    def counted_solver(sector, ell, k, background, boundary_config):
        calls.append((Sector(sector), ell, k))
        solution = _fake_solver(sector, ell, k, background, boundary_config)
        solution.diagnostics.solver = "q018_required_radius_oracle"
        solution.diagnostics.warnings = (
            SimpleNamespace(
                to_metadata=lambda: {
                    "code": "q018_required_radius_oracle_used",
                    "required_eval_radius": 60.0,
                }
            ),
        )
        return solution

    theta = np.asarray((0.0, np.pi / 3.0))
    dataset = compute_strict_np_psi4_convergence(
        kM_values=(0.5,),
        theta_values=theta,
        lmax=3,
        radial_solver=counted_solver,
    )
    assert len(calls) == 4
    assert dataset.solve_counts.tolist() == [4]
    expected_shells = np.asarray(
        [[_direct_shell_psi4(0.5, angle, ell) for ell in (2, 3)] for angle in theta]
    )
    np.testing.assert_allclose(dataset.psi4_shell_kinnersley[0], expected_shells)
    np.testing.assert_allclose(dataset.psi4_kinnersley[0], np.cumsum(expected_shells, axis=1))
    assert dataset.metadata["observable"] == "strict_np_psi4"
    assert dataset.metadata["frame"] == "kinnersley"
    assert dataset.metadata["not_packaged_polarization_scalars"] is True
    assert dataset.metadata["paper_curve_alignment_claim"] is False
    assert "do not label this dataset paper-faithful" in dataset.metadata[
        "paper_curve_alignment_note"
    ]
    assert dataset.metadata["boundary_config"]["experimental_required_radius_oracle"] == "q018_riccati"
    assert dataset.metadata["solve_diagnostics"][0]["solver"] == "q018_required_radius_oracle"
    assert dataset.metadata["solve_diagnostics"][0]["warnings"][0]["code"] == "q018_required_radius_oracle_used"


def test_figure2_round_trip_and_plot_structure(tmp_path) -> None:
    dataset = compute_strict_np_psi4_convergence(
        kM_values=FIG2_KM,
        theta_values=FIG2_THETA,
        lmax=2,
        radial_solver=_fake_solver,
    )
    npz, _ = save_figure2_dataset(dataset, tmp_path / "fig2")
    loaded = load_figure2_dataset(npz)
    np.testing.assert_array_equal(loaded.psi4_kinnersley, dataset.psi4_kinnersley)
    figure = build_figure2_figure(loaded, style="paper")
    assert len(figure.axes) == 4
    assert all(len(axis.lines) == 4 for axis in figure.axes)
    plt.close(figure)


def test_figure2_reference_comparison_keeps_raster_separate(tmp_path) -> None:
    dataset = compute_strict_np_psi4_convergence(
        kM_values=FIG2_KM,
        theta_values=FIG2_THETA,
        lmax=2,
        radial_solver=_fake_solver,
    )
    reference = tmp_path / "published.png"
    plt.imsave(reference, np.ones((20, 40, 3), dtype=np.float64))
    before = dataset.log10_abs_psi4.copy()
    figure = build_figure2_reference_comparison(dataset, reference)
    assert len(figure.axes) == 5
    np.testing.assert_array_equal(dataset.log10_abs_psi4, before)
    assert figure.axes[0].images
    plt.close(figure)


def test_save_formats_applies_frozen_rc_at_serialization(monkeypatch, tmp_path) -> None:
    figure = plt.figure()
    observed: list[tuple[int, int, str]] = []

    def fake_savefig(path, *, format, **kwargs):
        observed.append(
            (
                int(plt.rcParams["pdf.fonttype"]),
                int(plt.rcParams["ps.fonttype"]),
                str(plt.rcParams["svg.fonttype"]),
            )
        )
        path.write_bytes(b"save-time-rc-fixture")

    monkeypatch.setattr(figure, "savefig", fake_savefig)
    with plt.rc_context({"pdf.fonttype": 3, "ps.fonttype": 3, "svg.fonttype": "path"}):
        _save_formats(figure, tmp_path, "fixture")
    assert observed == [(42, 42, "none")] * 3
    plt.close(figure)
