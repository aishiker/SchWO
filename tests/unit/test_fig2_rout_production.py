from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.numerics import BoundaryConfig
from schwgw.perturbations import Sector


def _load_script_module():
    path = Path("scripts/phase5_recompute_fig2_jost_rout.py")
    spec = importlib.util.spec_from_file_location("fig2_rout_production", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_high_barrier_fig2_mode_uses_finite_local_jost_oracle() -> None:
    module = _load_script_module()
    config = BoundaryConfig(
        r_in_eps=1.0e-6,
        r_out=300.0,
        rtol=1.0e-10,
        atol=1.0e-12,
        required_eval_radius=60.0,
        experimental_required_radius_oracle="q018_riccati",
        outer_basis="jost_1_over_r",
        outer_series_order=160,
    )

    solution = module._fig2_radial_solver(
        Sector.EVEN,
        175,
        0.5,
        SchwarzschildBackground(M=1.0),
        config,
    )

    assert solution.diagnostics.solver == "fig2_single_radius_q018_jost_rout"
    assert solution.A_in == 1.0 + 0.0j
    assert np.isfinite(solution.psi_at(60.0))
    assert np.isfinite(solution.dpsi_dr_at(60.0))
    assert solution.diagnostics.boundary_residual < 1.0e-12


def test_expanded_rout_mode_uses_generic_local_jost_oracle() -> None:
    """Close the exact Python-3.14 r_out=600 production blocker."""

    module = _load_script_module()
    config = BoundaryConfig(
        r_in_eps=1.0e-6,
        r_out=600.0,
        rtol=1.0e-10,
        atol=1.0e-12,
        required_eval_radius=60.0,
        experimental_required_radius_oracle="q018_riccati",
        outer_basis="jost_1_over_r",
        outer_series_order=160,
    )

    solution = module._fig2_radial_solver(
        Sector.ODD,
        145,
        1.5,
        SchwarzschildBackground(M=1.0),
        config,
    )

    assert solution.diagnostics.solver == "fig2_single_radius_q018_jost_rout"
    assert solution.A_in == 1.0 + 0.0j
    assert np.isfinite(solution.psi_at(60.0))
    assert np.isfinite(solution.dpsi_dr_at(60.0))
    assert solution.diagnostics.boundary_residual < 1.0e-12
