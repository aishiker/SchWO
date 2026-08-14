from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.numerics import BoundaryConfig
from schwgw.perturbations import Sector


def _load_script_module():
    path = Path("scripts/phase5_generate_direct_curvature_angular.py")
    spec = importlib.util.spec_from_file_location("fig4_rout_production", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_extended_fig4_outer_radius_uses_generic_local_q018_oracle() -> None:
    module = _load_script_module()
    boundary = BoundaryConfig(
        r_in_eps=1.0e-6,
        r_out=600.0,
        rtol=1.0e-10,
        atol=1.0e-12,
        required_eval_radius=60.0,
        experimental_required_radius_oracle="q018_riccati",
        outer_basis="jost_1_over_r",
        outer_series_order=160,
    )
    cache = module._AnchorRadialCache()

    solution = cache(
        Sector.ODD,
        153,
        2.0,
        SchwarzschildBackground(M=1.0),
        boundary,
    )

    assert solution.diagnostics.solver == "fig4_single_radius_q018_jost_rout"
    assert solution.A_in == 1.0 + 0.0j
    assert np.isfinite(solution.psi_at(60.0))
    assert np.isfinite(solution.dpsi_dr_at(60.0))
    assert solution.diagnostics.boundary_residual < 1.0e-12
    assert cache.metadata()["generic_q018_count"] == 1
    assert cache.metadata()["standard_solver_count"] == 0
