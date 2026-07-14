import json
import os

import numpy as np
import pytest

import schwgw.numerics as public_numerics
from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
from schwgw.numerics import BoundaryConfig, solve_radial_mode
from schwgw.numerics.experimental.q018_rescaled_oracle import (
    RescaledOracleRequest,
    solve_q018_rescaled_oracle,
)
from schwgw.perturbations import Sector


Q018_ORACLE_MATRIX = tuple(
    (sector, ell)
    for ell in range(153, 181)
    for sector in (Sector.ODD, Sector.EVEN)
)

Q018_ORACLE_SENSITIVITY_MATRIX = (
    (Sector.ODD, 153),
    (Sector.EVEN, 153),
    (Sector.ODD, 180),
    (Sector.EVEN, 180),
)


def _oracle_request(
    *,
    sector: Sector,
    ell: int,
    rtol: float = 1e-10,
    atol: float = 1e-12,
) -> RescaledOracleRequest:
    return RescaledOracleRequest(
        sector=sector,
        ell=ell,
        k=2.0,
        required_radius=60.0,
        r_out=300.0,
        r_in_eps=1e-6,
        rtol=rtol,
        atol=atol,
        precision_dps=80,
        method_hint="rescaled_log_amplitude",
    )


def test_rescaled_oracle_contract_is_experimental_and_not_publicly_exported() -> None:
    request = _oracle_request(sector=Sector.ODD, ell=153)

    assert request.sector is Sector.ODD
    assert request.ell == 153
    assert request.required_radius == 60.0
    assert request.r_out == 300.0

    docstring = solve_q018_rescaled_oracle.__doc__
    assert docstring is not None
    assert "experimental" in docstring.lower()
    assert "unit incoming-at-infinity" in docstring
    assert "not exported as a public radial solver" in docstring.lower()
    assert "reviewed private" in docstring.lower()
    assert not hasattr(public_numerics, "solve_q018_rescaled_oracle")

    background = SchwarzschildBackground(M=1.0)
    with pytest.raises(RuntimeError, match="evanescent_tail_required_radius_uncovered"):
        solve_radial_mode(
            Sector.ODD,
            153,
            2.0,
            background,
            BoundaryConfig(
                r_in_eps=1e-6,
                r_out=300.0,
                rtol=1e-10,
                atol=1e-12,
                required_eval_radius=60.0,
            ),
        )


@pytest.mark.full_regression
@pytest.mark.parametrize("sector,ell", Q018_ORACLE_MATRIX)
@pytest.mark.skipif(
    os.environ.get("Q018_RUN_EXPERIMENTAL_ORACLE_TESTS") != "1",
    reason="set Q018_RUN_EXPERIMENTAL_ORACLE_TESTS=1 to run the oracle validation matrix",
)
def test_q018_rescaled_oracle_returns_finite_matrix_r60_when_enabled(
    sector: Sector,
    ell: int,
) -> None:
    background = SchwarzschildBackground(M=1.0)
    request = _oracle_request(sector=sector, ell=ell)

    result = solve_q018_rescaled_oracle(request, background)

    assert np.isfinite(result.psi.real)
    assert np.isfinite(result.psi.imag)
    assert np.isfinite(result.dpsi_dr.real)
    assert np.isfinite(result.dpsi_dr.imag)
    assert abs(result.A_in - 1.0) < 1e-8
    assert np.isfinite(result.A_out.real)
    assert np.isfinite(result.A_out.imag)
    assert result.valid_at_required_radius
    assert result.diagnostics["method"] == "riccati_log_derivative_match"
    assert result.diagnostics["method"] not in {"placeholder", "mock", "hardcoded"}
    assert result.diagnostics["required_radius"] == request.required_radius
    assert result.diagnostics["r_out"] == request.r_out
    assert result.diagnostics["ell"] == request.ell
    assert result.diagnostics["sector"] == request.sector.value
    assert result.diagnostics["k"] == request.k
    assert result.diagnostics["rtol"] == request.rtol
    assert result.diagnostics["atol"] == request.atol
    assert result.diagnostics["unit_incoming_at_infinity"] is True
    assert result.diagnostics["experimental"] is True
    assert result.diagnostics["valid_at_required_radius"] is True
    assert result.diagnostics["finite_psi"] is True
    assert result.diagnostics["finite_dpsi_dr"] is True
    assert result.diagnostics["finite_A_in"] is True
    assert result.diagnostics["finite_A_out"] is True
    assert result.diagnostics["riccati_steps"] > 0
    assert result.diagnostics["outward_steps"] > 0
    assert result.diagnostics["runtime_seconds"] >= 0.0
    assert np.isfinite(result.diagnostics["log_derivative_match_residual"])
    assert result.diagnostics["log_derivative_match_residual"] < 1e-7
    assert np.isfinite(result.diagnostics["outer_boundary_residual"])
    assert result.diagnostics["outer_boundary_residual"] < 1e-8
    assert result.diagnostics["normalization_residual"] < 1e-8

    repeat = solve_q018_rescaled_oracle(request, background)
    assert repeat.psi == pytest.approx(result.psi, rel=1e-12, abs=1e-18)
    assert repeat.dpsi_dr == pytest.approx(result.dpsi_dr, rel=1e-12, abs=1e-18)
    assert repeat.A_out == pytest.approx(result.A_out, rel=1e-12, abs=1e-18)


@pytest.mark.full_regression
@pytest.mark.parametrize("sector,ell", Q018_ORACLE_SENSITIVITY_MATRIX)
@pytest.mark.skipif(
    os.environ.get("Q018_RUN_EXPERIMENTAL_ORACLE_TESTS") != "1",
    reason="set Q018_RUN_EXPERIMENTAL_ORACLE_TESTS=1 to run oracle sensitivity checks",
)
def test_q018_rescaled_oracle_tolerance_sensitivity_when_enabled(
    sector: Sector,
    ell: int,
) -> None:
    background = SchwarzschildBackground(M=1.0)
    baseline = solve_q018_rescaled_oracle(
        _oracle_request(sector=sector, ell=ell),
        background,
    )
    loose = solve_q018_rescaled_oracle(
        _oracle_request(sector=sector, ell=ell, rtol=1e-9, atol=1e-11),
        background,
    )
    tight = solve_q018_rescaled_oracle(
        _oracle_request(sector=sector, ell=ell, rtol=1e-11, atol=1e-13),
        background,
    )

    for candidate in (loose, tight):
        assert candidate.valid_at_required_radius
        assert abs(candidate.A_in - 1.0) < 1e-8
        assert candidate.diagnostics["outer_boundary_residual"] < 1e-8
        assert candidate.diagnostics["normalization_residual"] < 1e-8
        assert candidate.diagnostics["log_derivative_match_residual"] < 1e-7
        assert candidate.psi == pytest.approx(baseline.psi, rel=5e-6, abs=1e-22)
        assert candidate.dpsi_dr == pytest.approx(
            baseline.dpsi_dr,
            rel=5e-6,
            abs=1e-22,
        )
        assert candidate.A_out == pytest.approx(baseline.A_out, rel=5e-6, abs=1e-12)


@pytest.mark.full_regression
@pytest.mark.parametrize("sector,ell", Q018_ORACLE_MATRIX)
@pytest.mark.skipif(
    os.environ.get("Q018_RUN_EXPERIMENTAL_ORACLE_TESTS") != "1",
    reason="set Q018_RUN_EXPERIMENTAL_ORACLE_TESTS=1 to run production guard matrix",
)
def test_production_required_radius_fails_closed_for_q018_matrix_when_enabled(
    sector: Sector,
    ell: int,
) -> None:
    background = SchwarzschildBackground(M=1.0)

    with pytest.raises(
        RuntimeError,
        match="evanescent_tail_required_radius_uncovered",
    ) as raised:
        solve_radial_mode(
            sector,
            ell,
            2.0,
            background,
            BoundaryConfig(
                r_in_eps=1e-6,
                r_out=300.0,
                rtol=1e-10,
                atol=1e-12,
                required_eval_radius=60.0,
            ),
        )

    metadata = json.loads(raised.value.args[0].split("metadata=", 1)[1])
    assert metadata["code"] == "evanescent_tail_required_radius_uncovered"
    assert metadata["sector"] == sector.value
    assert metadata["ell"] == ell
    assert metadata["required_eval_radius"] == 60.0
    assert metadata["required_eval_radius_covered"] is False
    assert metadata["valid_until_r"] < 60.0
