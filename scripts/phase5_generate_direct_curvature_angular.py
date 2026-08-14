#!/usr/bin/env python3
"""Generate one direct metric-curvature Fig. 4 angular artifact."""

from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np

from schwgw.io import load_config, run_solver_grid
from schwgw.io.results import GridResult
from schwgw.numerics import (
    BoundaryConfig,
    RadialDiagnostics,
    extrapolate_r_out_ladder,
    solve_radial_mode,
)
from schwgw.numerics.experimental.q018_rescaled_oracle import (
    RescaledOracleRequest,
    solve_q018_rescaled_oracle,
)
from schwgw.perturbations import Sector
from schwgw.scattering import compute_direct_metric_polarization


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _save_ladder_result(
    result: GridResult,
    *,
    h_plus_ladder: np.ndarray,
    h_cross_ladder: np.ndarray,
    h_plus_uncertainty: np.ndarray,
    h_cross_uncertainty: np.ndarray,
    r_out_ladder: np.ndarray,
    path: Path,
) -> None:
    payload: dict[str, Any] = {
        "theta": result.theta,
        "phi": result.phi,
        "h_plus": result.h_plus,
        "h_cross": result.h_cross,
        "h_plus_r_out_ladder": h_plus_ladder,
        "h_cross_r_out_ladder": h_cross_ladder,
        "h_plus_r_out_extrapolation_uncertainty": h_plus_uncertainty,
        "h_cross_r_out_extrapolation_uncertainty": h_cross_uncertainty,
        "r_out_ladder": r_out_ladder,
        "metadata_json": np.asarray(
            json.dumps(result.metadata, sort_keys=True, allow_nan=False)
        ),
    }
    if result.x is not None:
        payload.update(
            {
                "x": result.x,
                "z": result.z,
                "r": result.r,
                "valid_mask": result.valid_mask,
            }
        )
    np.savez(path, **payload)


class _AnchorRadialCache:
    """Cache one certified anchor solution per ``(sector, ell, k)``.

    The ODE-jet curvature bridge queries ``psi`` and ``dpsi/dr`` only at the
    observer radius.  Keeping the config's frozen required-radius oracle is
    therefore both sufficient and more accurate than differentiating a dense
    interpolant.
    """

    def __init__(self) -> None:
        self._solutions: dict[tuple[str, int, float], Any] = {}
        self.solve_count = 0
        self.standard_solver_count = 0
        self.generic_q018_count = 0
        self.reuse_count = 0

    def __call__(
        self,
        sector: Any,
        ell: int,
        k: float,
        background: Any,
        boundary: Any,
    ) -> Any:
        key = (str(getattr(sector, "value", sector)), int(ell), float(k))
        if key in self._solutions:
            self.reuse_count += 1
            return self._solutions[key]
        try:
            solution = solve_radial_mode(sector, ell, k, background, boundary)
        except RuntimeError as exc:
            if not any(
                marker in str(exc)
                for marker in (
                    "q018_experimental_oracle_out_of_envelope",
                    "Stabilized radial BVP solve failed",
                    "evanescent_tail_required_radius_uncovered",
                    "evanescent_tail_required_radius_solver_failed",
                )
            ):
                raise
            solution = _generic_q018_anchor_solution(
                sector=sector,
                ell=ell,
                k=k,
                background=background,
                boundary=boundary,
            )
            self.generic_q018_count += 1
        else:
            self.standard_solver_count += 1
        self._solutions[key] = solution
        self.solve_count += 1
        return solution

    def metadata(self) -> dict[str, int | bool]:
        return {
            "enabled": True,
            "unique_solution_count": self.solve_count,
            "standard_solver_count": self.standard_solver_count,
            "generic_q018_count": self.generic_q018_count,
            "reuse_count": self.reuse_count,
            "key_count": len(self._solutions),
        }


class _SingleRadiusQ018Solution:
    """Unit-incoming radial state certified at the Fig. 4 observer radius."""

    def __init__(
        self,
        *,
        sector: Sector,
        ell: int,
        k: float,
        background: Any,
        radius: float,
        boundary: BoundaryConfig,
        oracle: Any,
    ) -> None:
        self.sector = sector
        self.ell = int(ell)
        self.k = float(k)
        self.background = background
        self.r_grid = np.asarray((radius,), dtype=float)
        self.valid_until_r = float(radius)
        self.A_in = complex(oracle.A_in)
        self.A_out = complex(oracle.A_out)
        self.phase_factor = -self.A_out / (((-1) ** self.ell) * self.A_in)
        self.phase_shift = complex(-0.5j * np.log(self.phase_factor))
        self._radius = float(radius)
        self._psi = complex(oracle.psi)
        self._derivative = complex(oracle.dpsi_dr)
        raw = dict(oracle.diagnostics)
        residual = max(
            float(raw["outer_boundary_residual"]),
            float(raw["normalization_residual"]),
            float(raw["log_derivative_match_residual"]),
        )
        self.diagnostics = RadialDiagnostics(
            boundary_residual=float(raw["outer_boundary_residual"]),
            wronskian_residual=residual,
            ode_n_steps=int(raw["riccati_steps"]) + int(raw["outward_steps"]),
            ode_status=f"{raw['riccati_status']}; {raw['outward_status']}",
            r_in=float(background.horizon_radius * (1.0 + boundary.r_in_eps)),
            r_out=float(boundary.r_out),
            atol=float(boundary.atol),
            rtol=float(boundary.rtol),
            match_condition_number=float(raw["match_condition_number"]),
            flux_residual=residual,
            solver="fig4_single_radius_q018_jost_rout",
            barrier_action=0.0,
            raw_wronskian_residual=residual,
            expected_flux_scale=0.0,
            warnings=(),
            outer_basis="jost_1_over_r",
            outer_series_order=160,
        )

    def _validate_radius(self, radius: Any) -> None:
        values = np.asarray(radius, dtype=float)
        if np.any(values != self._radius):
            raise ValueError("single-radius Fig. 4 Q018 solution cannot extrapolate in r")

    def psi_at(self, radius: Any) -> complex:
        self._validate_radius(radius)
        return self._psi

    def dpsi_dr_at(self, radius: Any) -> complex:
        self._validate_radius(radius)
        return self._derivative


def _generic_q018_anchor_solution(
    *,
    sector: Any,
    ell: int,
    k: float,
    background: Any,
    boundary: BoundaryConfig,
) -> _SingleRadiusQ018Solution:
    """Extend the reviewed local Q018 method to the requested outer radius."""

    if boundary.required_eval_radius is None or boundary.r_out is None:
        raise RuntimeError("Fig. 4 Q018 fallback requires explicit radii")
    sector_enum = sector if isinstance(sector, Sector) else Sector(str(sector))
    radius = float(boundary.required_eval_radius)
    oracle = solve_q018_rescaled_oracle(
        RescaledOracleRequest(
            sector=sector_enum,
            ell=int(ell),
            k=float(k),
            required_radius=radius,
            r_out=float(boundary.r_out),
            r_in_eps=float(boundary.r_in_eps),
            rtol=float(boundary.rtol),
            atol=float(boundary.atol),
        ),
        background,
    )
    if not oracle.valid_at_required_radius:
        raise RuntimeError("Fig. 4 generic Q018 result is invalid at the observer radius")
    return _SingleRadiusQ018Solution(
        sector=sector_enum,
        ell=int(ell),
        k=float(k),
        background=background,
        radius=radius,
        boundary=boundary,
        oracle=oracle,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument(
        "--r-out-ladder",
        nargs=3,
        type=float,
        default=(300.0, 600.0, 1200.0),
    )
    parser.add_argument(
        "--observer-frame",
        choices=("static_orthonormal", "li_literal_cartesian"),
    )
    args = parser.parse_args(argv)
    source_config = load_config(args.config)
    if source_config.observer.kind != "angular":
        raise ValueError("direct-curvature Fig. 4 production requires angular data")
    config = source_config
    if args.observer_frame is not None:
        config = replace(
            config,
            observer=replace(config.observer, observer_frame=args.observer_frame),
        )
    r_out_ladder = tuple(float(value) for value in args.r_out_ladder)
    observer_radius = float(config.observer.r or 0.0)
    if (
        tuple(sorted(set(r_out_ladder))) != r_out_ladder
        or r_out_ladder[0] <= observer_radius
    ):
        raise ValueError("r_out ladder must contain three increasing outer radii")
    token = f"{config.wave.kM:g}".replace(".", "p")
    artifact = args.output_dir / f"fig4_direct_curvature_kM_{token}.npz"
    manifest = args.output_dir / f"fig4_direct_curvature_kM_{token}.manifest.json"
    collisions = [str(path) for path in (artifact, manifest) if path.exists()]
    if collisions:
        raise FileExistsError(f"refusing output collisions: {collisions}")
    if args.preflight:
        print(
            json.dumps(
                {
                    "event": "direct_curvature_angular_preflight_passed",
                    "config": str(args.config),
                    "kM": config.wave.kM,
                    "output": str(artifact),
                    "radial_ode_jet": True,
                    "dense_radial_stencil": False,
                    "r_out_ladder": list(r_out_ladder),
                    "r_out_extrapolation": "quadratic in 1/r_out",
                    "observer_frame": config.observer.observer_frame,
                },
                sort_keys=True,
            )
        )
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    radial_cache_records = []
    for r_out in r_out_ladder:
        print(
            json.dumps(
                {
                    "event": "direct_curvature_angular_r_out_started",
                    "kM": config.wave.kM,
                    "observer_frame": config.observer.observer_frame,
                    "r_out": r_out,
                },
                sort_keys=True,
            ),
            flush=True,
        )
        radial_cache = _AnchorRadialCache()

        def direct_solver(**kwargs):
            kwargs.pop("radial_solver", None)
            return compute_direct_metric_polarization(
                **kwargs,
                radial_solver=radial_cache,
            )

        direct_solver.__schwgw_bridge_metadata__ = (
            compute_direct_metric_polarization.__schwgw_bridge_metadata__
        )
        radius_config = replace(
            config,
            numerics=replace(
                config.numerics,
                boundary=replace(config.numerics.boundary, r_out=r_out),
            ),
        )
        radius_result = run_solver_grid(
            radius_config,
            polarization_solver=direct_solver,
            source_command=[sys.executable, *sys.argv],
        )
        convergence_policy = (
            radius_result.metadata.get("diagnostics", {})
            .get("lmax_convergence_policy", {})
        )
        if not convergence_policy.get("final_pair_passed", False):
            raise RuntimeError(
                "Fig. 4 final lmax-pair convergence failed at "
                f"r_out={r_out}: {convergence_policy}"
            )
        results.append(radius_result)
        radial_cache_records.append(
            {"r_out": r_out, **radial_cache.metadata()}
        )
        print(
            json.dumps(
                {
                    "event": "direct_curvature_angular_r_out_complete",
                    "kM": config.wave.kM,
                    "observer_frame": config.observer.observer_frame,
                    "r_out": r_out,
                    **radial_cache.metadata(),
                },
                sort_keys=True,
            ),
            flush=True,
        )
    reference = results[0]
    for current in results[1:]:
        if not np.array_equal(current.theta, reference.theta) or not np.array_equal(
            current.phi, reference.phi
        ):
            raise RuntimeError("r_out ladder changed the Fig. 4 angular grid")
    h_plus_ladder = np.stack([result.h_plus for result in results])
    h_cross_ladder = np.stack([result.h_cross for result in results])
    plus_fit = extrapolate_r_out_ladder(
        np.asarray(r_out_ladder), h_plus_ladder
    )
    cross_fit = extrapolate_r_out_ladder(
        np.asarray(r_out_ladder), h_cross_ladder
    )
    metadata = {
        **results[-1].metadata,
        "r_out_ladder": list(r_out_ladder),
        "r_out_extrapolation": "quadratic in 1/r_out",
        "max_r_out_uncertainty_plus": float(np.max(plus_fit.uncertainty)),
        "max_r_out_uncertainty_cross": float(np.max(cross_fit.uncertainty)),
        "observer_frame": config.observer.observer_frame,
        "paper_equivalence": "YELLOW",
    }
    result = GridResult(
        theta=reference.theta,
        phi=reference.phi,
        h_plus=plus_fit.extrapolated,
        h_cross=cross_fit.extrapolated,
        metadata=metadata,
        x=reference.x,
        z=reference.z,
        r=reference.r,
        valid_mask=reference.valid_mask,
    )
    temporary = artifact.with_name(f".{artifact.name}.partial.npz")
    if temporary.exists():
        raise FileExistsError(f"refusing temporary collision: {temporary}")
    _save_ladder_result(
        result,
        h_plus_ladder=h_plus_ladder,
        h_cross_ladder=h_cross_ladder,
        h_plus_uncertainty=plus_fit.uncertainty,
        h_cross_uncertainty=cross_fit.uncertainty,
        r_out_ladder=np.asarray(r_out_ladder),
        path=temporary,
    )
    with temporary.open("rb") as handle:
        os.fsync(handle.fileno())
    os.replace(temporary, artifact)
    payload = {
        "schema_version": "li_hou_zhao_fig4_direct_curvature_angular_v2",
        "figure": 4,
        "kM": config.wave.kM,
        "source_config": str(args.config),
        "source_config_sha256": _sha256(args.config),
        "artifact": str(artifact),
        "artifact_sha256": _sha256(artifact),
        "radial_ode_jet": True,
        "dense_radial_stencil": False,
        "required_radius_override": config.numerics.boundary.required_eval_radius,
        "scientific_equations_changed": False,
        "radial_cache_by_r_out": radial_cache_records,
        "r_out_ladder": list(r_out_ladder),
        "r_out_extrapolation": "quadratic in 1/r_out",
        "max_r_out_uncertainty_plus": float(np.max(plus_fit.uncertainty)),
        "max_r_out_uncertainty_cross": float(np.max(cross_fit.uncertainty)),
        "observer_frame": config.observer.observer_frame,
        "paper_equivalence": "YELLOW",
        "polarization_bridge": (
            "RW-gauge metric -> linearized Riemann -> incident-frame projection"
        ),
    }
    manifest.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with manifest.open("rb") as handle:
        os.fsync(handle.fileno())
    print(
        json.dumps(
            {
                "event": "direct_curvature_angular_complete",
                "kM": config.wave.kM,
                "artifact": str(artifact),
                "sha256": payload["artifact_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
