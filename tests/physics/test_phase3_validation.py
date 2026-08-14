from __future__ import annotations

import numpy as np
import pytest

import schwgw.scattering.partial_wave as partial_wave_module
from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
from schwgw.numerics import BoundaryConfig
from schwgw.scattering import (
    PolarizationResult,
    compute_flat_no_lens_polarization,
    compute_flat_no_lens_partial_wave_diagnostic,
    compute_flat_no_lens_partial_wave_raw_strict_np_weyl,
    compute_flat_no_lens_partial_wave_strict_np_weyl,
    compute_polarization,
    direct_cartesian_tt_packaged_weyl,
    direct_cartesian_tt_polarization,
    direct_cartesian_tt_strict_np_weyl,
    flat_no_lens_expected_polarization,
    polarization_from_weyl,
)


pytestmark = pytest.mark.physics

K = 0.5
R_OBS = 20.0
A_PLUS = 0.9 + 0.2j
A_CROSS = 0.1 - 0.3j
PROBES = [(R_OBS, 0.0, 0.0), (R_OBS, 0.05, 0.0), (R_OBS, 0.4, 0.0)]


def test_phase3_selected_probe_smoke_values_are_finite() -> None:
    bg = SchwarzschildBackground(M=1.0)
    boundary_config = _fast_boundary_config()

    for radius, theta, phi in PROBES:
        result = compute_polarization(
            background=bg,
            k=K,
            r=radius,
            theta=theta,
            phi=phi,
            A_plus=A_PLUS,
            A_cross=A_CROSS,
            lmax=3,
            boundary_config=boundary_config,
        )

        _assert_finite_result(result)
        assert result.diagnostics["lmax"] == 3.0
        assert result.diagnostics["radial_solve_count"] == 4.0
        assert result.diagnostics["mode_count"] == 8.0
        assert result.diagnostics["nonzero_coefficient_count"] == 8.0
        assert result.diagnostics["full_np_pseudoinverse_bridge"] == 1.0
        assert result.diagnostics["observable_bridge_validated"] == 0.0
        assert (
            result.diagnostics["positive_frequency_reality_bridge_validated"]
            == 0.0
        )


def test_phase3_lmax_scaling_smoke_records_finite_relative_changes() -> None:
    bg = SchwarzschildBackground(M=1.0)
    boundary_config = _fast_boundary_config()

    results = [
        compute_polarization(
            background=bg,
            k=K,
            r=R_OBS,
            theta=0.4,
            phi=0.0,
            A_plus=A_PLUS,
            A_cross=A_CROSS,
            lmax=lmax,
            boundary_config=boundary_config,
        )
        for lmax in (3, 4, 5)
    ]

    for result, lmax in zip(results, (3, 4, 5), strict=True):
        _assert_finite_result(result)
        assert result.diagnostics["lmax"] == float(lmax)
        assert result.diagnostics["radial_solve_count"] == float(2 * (lmax - 1))
        assert result.diagnostics["mode_count"] == float(4 * (lmax - 1))

    assert np.isfinite(_relative_field_change(results[0], results[1]))
    assert np.isfinite(_relative_field_change(results[1], results[2]))


def test_phase3_parity_sector_count_matches_plus_z_m_selection() -> None:
    bg = SchwarzschildBackground(M=1.0)
    result = compute_polarization(
        background=bg,
        k=K,
        r=R_OBS,
        theta=0.4,
        phi=0.0,
        A_plus=A_PLUS,
        A_cross=A_CROSS,
        lmax=5,
        boundary_config=_fast_boundary_config(),
    )

    # For each ell, +z incidence activates m=-2 and m=+2.  Both parity
    # sectors are then weighted by nonzero T5 coefficients.
    assert result.diagnostics["nonzero_coefficient_count"] == 16.0
    assert result.diagnostics["radial_solve_count"] == 8.0


@pytest.mark.xfail(
    reason=(
        "T7b kept this as a full-validation oracle: diagnostic lmax sweeps "
        "remain far above the final <1e-3 near-axis convergence threshold."
    ),
    strict=False,
)
def test_phase3_near_axis_refinement_threshold_entrypoint() -> None:
    bg = SchwarzschildBackground(M=1.0)
    boundary_config = _fast_boundary_config()

    coarse = compute_polarization(
        background=bg,
        k=K,
        r=R_OBS,
        theta=0.05,
        phi=0.0,
        A_plus=A_PLUS,
        A_cross=A_CROSS,
        lmax=4,
        boundary_config=boundary_config,
    )
    refined = compute_polarization(
        background=bg,
        k=K,
        r=R_OBS,
        theta=0.05,
        phi=0.0,
        A_plus=A_PLUS,
        A_cross=A_CROSS,
        lmax=5,
        boundary_config=boundary_config,
    )

    assert _relative_field_change(coarse, refined) < 1e-3


@pytest.mark.full_regression
@pytest.mark.skip(
    reason=(
        "Far-axis asymptotic comparison requires an explicit asymptotic "
        "scattering baseline. Phase 3 T7a only reserves this full-validation "
        "entrypoint; it is not part of the finite-radius algorithm definition."
    )
)
def test_phase3_far_axis_asymptotic_comparison_entrypoint() -> None:
    raise AssertionError("Skipped until an asymptotic comparison oracle is implemented.")


@pytest.mark.parametrize(
    ("A_plus", "A_cross"),
    [
        (1.0 + 0.0j, 0.0j),
        (0.0j, 1.0 - 0.2j),
        (0.9 + 0.2j, 0.1 - 0.3j),
    ],
)
def test_phase3_direct_cartesian_tt_oracle_recovers_incident_polarization(
    A_plus: complex,
    A_cross: complex,
) -> None:
    result = direct_cartesian_tt_polarization(
        k=K,
        z=R_OBS * np.cos(0.4),
        A_plus=A_plus,
        A_cross=A_cross,
    )
    expected = flat_no_lens_expected_polarization(
        k=K,
        r=R_OBS,
        theta=0.4,
        A_plus=A_plus,
        A_cross=A_cross,
    )

    assert result.diagnostics["direct_cartesian_tt"] == 1.0
    assert _relative_complex_pair_error((result.h_plus, result.h_cross), expected) < 1e-10


@pytest.mark.parametrize(
    ("A_plus", "A_cross"),
    [
        (1.0 + 0.0j, 0.0j),
        (0.0j, 1.0 - 0.2j),
        (0.9 + 0.2j, 0.1 - 0.3j),
    ],
)
def test_phase3_flat_no_lens_adapter_recovers_incident_polarization(
    A_plus: complex,
    A_cross: complex,
) -> None:
    result = compute_flat_no_lens_polarization(
        k=K,
        r=R_OBS,
        theta=0.4,
        phi=0.0,
        A_plus=A_plus,
        A_cross=A_cross,
        lmax=40,
    )
    expected_plus, expected_cross = flat_no_lens_expected_polarization(
        k=K,
        r=R_OBS,
        theta=0.4,
        A_plus=A_plus,
        A_cross=A_cross,
    )

    assert result.diagnostics["radial_solve_count"] == 0.0
    assert result.diagnostics["flat_no_lens"] == 1.0
    assert result.diagnostics["q011_conjugation_literal"] == 0.0
    assert _relative_complex_pair_error(
        (result.h_plus, result.h_cross),
        (expected_plus, expected_cross),
    ) < 1e-5


def test_phase3_flat_no_lens_partial_wave_strict_np_matches_direct_tensor_contraction() -> None:
    actual = compute_flat_no_lens_partial_wave_strict_np_weyl(
        k=K,
        r=R_OBS,
        theta=0.4,
        phi=0.0,
        A_plus=A_PLUS,
        A_cross=A_CROSS,
        lmax=40,
        tetrad="incident",
    )
    expected = direct_cartesian_tt_strict_np_weyl(
        k=K,
        z=R_OBS * np.cos(0.4),
        A_plus=A_PLUS,
        A_cross=A_CROSS,
    )

    assert _relative_weyl_error(actual, expected) < 1e-5


@pytest.mark.parametrize(
    ("theta", "expected_full_error", "expected_psi4_error"),
    [
        (0.4, 0.11862586646193823, 0.017563685045674821),
        (1.0, 0.9623614893755684, 0.3401586263709983),
    ],
)
def test_phase3_raw_full_np_defect_is_not_hidden_by_type_n_completion(
    theta: float,
    expected_full_error: float,
    expected_psi4_error: float,
) -> None:
    common = {
        "k": K,
        "r": R_OBS,
        "theta": theta,
        "phi": 0.0,
        "A_plus": 1.0 + 0.0j,
        "A_cross": 0.0j,
        "lmax": 40,
    }
    raw = compute_flat_no_lens_partial_wave_raw_strict_np_weyl(
        **common,
        tetrad="incident",
    )
    completed = compute_flat_no_lens_partial_wave_strict_np_weyl(
        **common,
        tetrad="incident",
    )
    expected = direct_cartesian_tt_strict_np_weyl(
        k=K,
        z=R_OBS * np.cos(theta),
        A_plus=1.0 + 0.0j,
        A_cross=0.0j,
    )

    raw_full_error = _relative_weyl_error(raw, expected)
    raw_psi4_error = abs(raw["Psi4"] - expected["Psi4"]) / abs(expected["Psi4"])
    completed_error = _relative_weyl_error(completed, expected)

    assert raw_full_error == pytest.approx(expected_full_error, rel=2.0e-12)
    assert raw_psi4_error == pytest.approx(expected_psi4_error, rel=2.0e-12)
    assert completed_error < 5.0e-14
    assert raw_full_error > 1.0e-1
    assert completed_error < raw_full_error * 1.0e-10


@pytest.mark.parametrize(
    ("A_plus", "A_cross"),
    [
        (1.0 + 0.0j, 0.0j),
        (0.0j, 1.0 - 0.2j),
        (0.9 + 0.2j, 0.1 - 0.3j),
    ],
)
def test_phase3_packaged_flat_scalars_recover_incident_polarization(
    A_plus: complex,
    A_cross: complex,
) -> None:
    packaged = direct_cartesian_tt_packaged_weyl(
        k=K,
        z=R_OBS * np.cos(0.4),
        A_plus=A_plus,
        A_cross=A_cross,
    )
    actual = polarization_from_weyl(K, packaged["Psi0"], packaged["Psi4"])
    expected = flat_no_lens_expected_polarization(
        k=K,
        r=R_OBS,
        theta=0.4,
        A_plus=A_plus,
        A_cross=A_cross,
    )

    assert _relative_complex_pair_error(actual, expected) < 1e-10


@pytest.mark.parametrize(
    ("A_plus", "A_cross"),
    [
        (1.0 + 0.0j, 0.0j),
        (0.0j, 1.0 - 0.2j),
        (0.9 + 0.2j, 0.1 - 0.3j),
    ],
)
def test_phase3_flat_no_lens_partial_wave_diagnostic_recovers_incident_polarization(
    A_plus: complex,
    A_cross: complex,
) -> None:
    common = dict(
        k=K,
        r=R_OBS,
        theta=0.4,
        phi=0.0,
        A_plus=A_plus,
        A_cross=A_cross,
        lmax=40,
    )
    expected = flat_no_lens_expected_polarization(
        k=K,
        r=R_OBS,
        theta=0.4,
        A_plus=A_plus,
        A_cross=A_cross,
    )

    result = compute_flat_no_lens_partial_wave_diagnostic(**common, q011_z_conjugation="linear")

    assert result.diagnostics["partial_wave_diagnostic"] == 1.0
    assert result.diagnostics["radial_solve_count"] == 0.0
    assert _relative_complex_pair_error((result.h_plus, result.h_cross), expected) < 1e-5


def test_phase3_flat_no_lens_partial_wave_diagnostic_does_not_call_direct_oracle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_direct_oracle(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("partial-wave diagnostic must not call direct Cartesian oracle")

    monkeypatch.setattr(
        partial_wave_module,
        "direct_cartesian_tt_packaged_weyl",
        fail_direct_oracle,
    )
    monkeypatch.setattr(
        partial_wave_module,
        "direct_cartesian_tt_strict_np_weyl",
        fail_direct_oracle,
    )
    monkeypatch.setattr(
        partial_wave_module,
        "direct_cartesian_tt_polarization",
        fail_direct_oracle,
    )

    strict = compute_flat_no_lens_partial_wave_strict_np_weyl(
        k=K,
        r=R_OBS,
        theta=0.4,
        phi=0.0,
        A_plus=A_PLUS,
        A_cross=A_CROSS,
        lmax=5,
        tetrad="incident",
    )
    diagnostic = compute_flat_no_lens_partial_wave_diagnostic(
        k=K,
        r=R_OBS,
        theta=0.4,
        phi=0.0,
        A_plus=A_PLUS,
        A_cross=A_CROSS,
        lmax=5,
    )

    assert set(strict) == {"Psi0", "Psi1", "Psi2", "Psi3", "Psi4"}
    _assert_finite_result(diagnostic)


def test_phase3_flat_no_lens_partial_wave_diagnostic_records_higher_ell_contributions() -> None:
    result = compute_flat_no_lens_partial_wave_diagnostic(
        k=K,
        r=R_OBS,
        theta=0.4,
        phi=0.0,
        A_plus=A_PLUS,
        A_cross=A_CROSS,
        lmax=5,
    )

    assert result.diagnostics["ell_2_contribution_norm"] > 0.0
    assert result.diagnostics["ell_3_contribution_norm"] > 0.0
    assert result.diagnostics["ell_4_contribution_norm"] > 0.0
    assert result.diagnostics["ell_5_contribution_norm"] > 0.0


def _fast_boundary_config() -> BoundaryConfig:
    return BoundaryConfig(r_in_eps=1e-5, r_out=50.0, rtol=1e-8, atol=1e-10)


def _assert_finite_result(result: PolarizationResult) -> None:
    for value in (result.h_plus, result.h_cross, result.psi0_hat, result.psi4_hat):
        assert np.isfinite(value.real)
        assert np.isfinite(value.imag)
    for value in result.diagnostics.values():
        assert np.isfinite(value)


def _relative_field_change(coarse: PolarizationResult, refined: PolarizationResult) -> float:
    numerator = np.linalg.norm(
        [refined.h_plus - coarse.h_plus, refined.h_cross - coarse.h_cross]
    )
    denominator = max(
        np.linalg.norm([refined.h_plus, refined.h_cross]),
        np.finfo(float).eps,
    )
    return float(numerator / denominator)


def _relative_complex_pair_error(
    actual: tuple[complex, complex],
    expected: tuple[complex, complex],
) -> float:
    numerator = np.linalg.norm([actual[0] - expected[0], actual[1] - expected[1]])
    denominator = max(np.linalg.norm([expected[0], expected[1]]), np.finfo(float).eps)
    return float(numerator / denominator)


def _relative_weyl_error(
    actual: dict[str, complex],
    expected: dict[str, complex],
) -> float:
    labels = ("Psi0", "Psi1", "Psi2", "Psi3", "Psi4")
    numerator = np.linalg.norm([actual[label] - expected[label] for label in labels])
    denominator = max(np.linalg.norm([expected[label] for label in labels]), np.finfo(float).eps)
    return float(numerator / denominator)
