#!/usr/bin/env python3
"""Recompute paper-facing Fig. 2 with a three-radius Jost ladder."""

from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np

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
from schwgw.paper_figures.li_hou_zhao import (
    compute_strict_np_psi4_convergence,
    save_figure2_dataset,
)
from schwgw.perturbations import Sector


class _SingleRadiusOracleSolution:
    """Minimal unit-incoming radial state certified only at one radius."""

    def __init__(
        self,
        *,
        sector: Sector,
        ell: int,
        k: float,
        background,
        radius: float,
        config: BoundaryConfig,
        oracle,
    ) -> None:
        self.sector = sector
        self.ell = ell
        self.k = k
        self.background = background
        self.r_grid = np.asarray((radius,), dtype=float)
        self.valid_until_r = radius
        self.A_in = complex(oracle.A_in)
        self.A_out = complex(oracle.A_out)
        self.phase_factor = -self.A_out / (((-1) ** ell) * self.A_in)
        self.phase_shift = complex(-0.5j * np.log(self.phase_factor))
        self._radius = radius
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
            ode_status=(
                f"{raw['riccati_status']}; {raw['outward_status']}"
            ),
            r_in=float(background.horizon_radius * (1.0 + config.r_in_eps)),
            r_out=float(config.r_out),
            atol=float(config.atol),
            rtol=float(config.rtol),
            match_condition_number=float(raw["match_condition_number"]),
            flux_residual=residual,
            solver="fig2_single_radius_q018_jost_rout",
            barrier_action=0.0,
            raw_wronskian_residual=residual,
            expected_flux_scale=0.0,
            warnings=(),
            outer_basis="jost_1_over_r",
            outer_series_order=160,
        )

    def _validate_radius(self, value) -> None:
        radius = np.asarray(value, dtype=float)
        if np.any(radius != self._radius):
            raise ValueError("single-radius Fig. 2 oracle cannot extrapolate in r")

    def psi_at(self, radius):
        self._validate_radius(radius)
        return self._psi

    def dpsi_dr_at(self, radius):
        self._validate_radius(radius)
        return self._derivative


def _fig2_radial_solver(sector, ell, k, background, config):
    """Use the unchanged solver first, then a local Riccati fallback."""

    try:
        return solve_radial_mode(sector, ell, k, background, config)
    except RuntimeError as exc:
        if not any(
            marker in str(exc)
            for marker in (
                "Stabilized radial BVP solve failed",
                "evanescent_tail_required_radius_uncovered",
                "evanescent_tail_required_radius_solver_failed",
                "q018_experimental_oracle_out_of_envelope",
            )
        ):
            raise
    if config.required_eval_radius is None or config.r_out is None:
        raise RuntimeError("Fig. 2 Q018 fallback requires explicit radii")
    sector_enum = sector if isinstance(sector, Sector) else Sector(str(sector))
    oracle = solve_q018_rescaled_oracle(
        RescaledOracleRequest(
            sector=sector_enum,
            ell=int(ell),
            k=float(k),
            required_radius=float(config.required_eval_radius),
            r_out=float(config.r_out),
            r_in_eps=float(config.r_in_eps),
            rtol=float(config.rtol),
            atol=float(config.atol),
        ),
        background,
    )
    return _SingleRadiusOracleSolution(
        sector=sector_enum,
        ell=int(ell),
        k=float(k),
        background=background,
        radius=float(config.required_eval_radius),
        config=config,
        oracle=oracle,
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    if path.exists():
        raise FileExistsError(path)
    temporary = path.with_name(f".{path.name}.partial.npz")
    if temporary.exists():
        raise FileExistsError(temporary)
    np.savez(temporary, **arrays)
    with temporary.open("rb") as handle:
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _atomic_json(path: Path, payload: dict) -> None:
    if path.exists():
        raise FileExistsError(path)
    temporary = path.with_name(f".{path.name}.partial")
    text = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with temporary.open("x", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _progress(record: dict[str, object]) -> None:
    print(json.dumps(record, sort_keys=True), flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--r-out-ladder", nargs=3, type=float, default=(300.0, 600.0, 1200.0)
    )
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args(argv)
    radii = tuple(float(value) for value in args.r_out_ladder)
    if tuple(sorted(set(radii))) != radii:
        parser.error("r-out ladder must contain three unique increasing radii")
    expected = (
        args.output_dir / "fig2_strict_psi4_convergence_data.npz",
        args.output_dir / "fig2_strict_psi4_convergence_data.json",
        args.output_dir / "fig2_strict_psi4_rout_supplement.npz",
        args.output_dir / "fig2_strict_psi4_rout_supplement.json",
    )
    collisions = [str(path) for path in expected if path.exists()]
    if collisions:
        raise FileExistsError(f"refusing output collisions: {collisions}")
    if args.preflight:
        _progress(
            {
                "event": "fig2_jost_rout_preflight_passed",
                "output_dir": str(args.output_dir),
                "r_out_ladder": list(radii),
                "scientific_solver_started": False,
            }
        )
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    datasets = []
    for r_out in radii:
        _progress({"event": "fig2_r_out_started", "r_out": r_out})
        dataset = compute_strict_np_psi4_convergence(
            radial_solver=_fig2_radial_solver,
            boundary_config=BoundaryConfig(
                r_in_eps=1.0e-6,
                r_out=r_out,
                rtol=1.0e-10,
                atol=1.0e-12,
                required_eval_radius=60.0,
                experimental_required_radius_oracle="q018_riccati",
                outer_basis="jost_1_over_r",
                outer_series_order=160,
            ),
            progress=lambda record, radius=r_out: _progress(
                {**record, "r_out": radius}
            ),
        )
        datasets.append(dataset)
        _progress({"event": "fig2_r_out_complete", "r_out": r_out})

    shell_ladder = np.stack(
        [dataset.psi4_shell_kinnersley for dataset in datasets]
    )
    cumulative_ladder = np.stack(
        [dataset.psi4_kinnersley for dataset in datasets]
    )
    shell_fit = extrapolate_r_out_ladder(np.asarray(radii), shell_ladder)
    cumulative_fit = extrapolate_r_out_ladder(
        np.asarray(radii), cumulative_ladder
    )
    amplitude = np.abs(cumulative_fit.extrapolated)
    if np.any(amplitude <= 0.0) or not np.all(np.isfinite(amplitude)):
        raise RuntimeError("Fig. 2 r-out extrapolation is zero or non-finite")
    metadata = {
        **datasets[-1].metadata,
        "schema_version": "li_hou_zhao_figure2_strict_np_psi4_rout_v2",
        "r_out_ladder": list(radii),
        "r_out_extrapolation": "quadratic in 1/r_out",
        "outer_basis": "jost_1_over_r",
        "outer_series_order": 160,
        "max_shell_r_out_uncertainty": float(np.max(shell_fit.uncertainty)),
        "max_cumulative_r_out_uncertainty": float(
            np.max(cumulative_fit.uncertainty)
        ),
        "paper_curve_alignment_claim": False,
        "high_barrier_local_oracle": (
            "unchanged solve_radial_mode first; generic single-radius "
            "Riccati/Jost fallback only for structured high-barrier failures"
        ),
        "source_command": [sys.executable, *sys.argv],
    }
    extrapolated = replace(
        datasets[-1],
        psi4_kinnersley=cumulative_fit.extrapolated,
        psi4_shell_kinnersley=shell_fit.extrapolated,
        log10_abs_psi4=np.log10(amplitude),
        solve_counts=np.sum(
            np.stack([dataset.solve_counts for dataset in datasets]), axis=0
        ),
        elapsed_seconds_by_frequency=np.sum(
            np.stack(
                [dataset.elapsed_seconds_by_frequency for dataset in datasets]
            ),
            axis=0,
        ),
        metadata=metadata,
    )
    base_paths = save_figure2_dataset(extrapolated, args.output_dir)
    supplement = expected[2]
    _atomic_npz(
        supplement,
        {
            "r_out_ladder": np.asarray(radii),
            "psi4_shell_kinnersley_r_out_ladder": shell_ladder,
            "psi4_kinnersley_r_out_ladder": cumulative_ladder,
            "psi4_shell_r_out_extrapolation_uncertainty": shell_fit.uncertainty,
            "psi4_cumulative_r_out_extrapolation_uncertainty": (
                cumulative_fit.uncertainty
            ),
            "psi4_shell_r_out_adjacent_relative_change": (
                shell_fit.adjacent_relative_change
            ),
            "psi4_cumulative_r_out_adjacent_relative_change": (
                cumulative_fit.adjacent_relative_change
            ),
        },
    )
    supplement_json = expected[3]
    _atomic_json(
        supplement_json,
        {
            "schema_version": "li_hou_zhao_figure2_rout_supplement_v1",
            "npz": str(supplement),
            "npz_sha256": _sha256(supplement),
            "r_out_ladder": list(radii),
            "r_out_extrapolation": "quadratic in 1/r_out",
            "outer_basis": "jost_1_over_r",
            "outer_series_order": 160,
            "base_npz": str(base_paths[0]),
            "base_npz_sha256": _sha256(base_paths[0]),
            "max_shell_r_out_uncertainty": metadata[
                "max_shell_r_out_uncertainty"
            ],
            "max_cumulative_r_out_uncertainty": metadata[
                "max_cumulative_r_out_uncertainty"
            ],
        },
    )
    _progress(
        {
            "event": "fig2_jost_rout_complete",
            "base_npz": str(base_paths[0]),
            "base_npz_sha256": _sha256(base_paths[0]),
            "supplement_npz": str(supplement),
            "supplement_npz_sha256": _sha256(supplement),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
