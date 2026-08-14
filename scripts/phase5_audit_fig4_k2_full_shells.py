#!/usr/bin/env python3
"""Compute the full Fig. 4 kM=2 shell/branch audit at selected angles."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np

from phase5_generate_direct_curvature_angular import _AnchorRadialCache
from schwgw.backgrounds import SchwarzschildBackground
from schwgw.numerics import BoundaryConfig, extrapolate_r_out_ladder
from schwgw.perturbations import Sector
from schwgw.scattering import compute_direct_metric_polarization


FRAMES = ("static_orthonormal", "li_literal_cartesian")
SELECTED_THETA = (0.25 * np.pi, 0.5 * np.pi, 0.75 * np.pi, 0.95 * np.pi)
CHECKPOINT_LMAX = (120, 160, 200, 240)


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


def _atomic_json(path: Path, payload: dict[str, object]) -> None:
    if path.exists():
        raise FileExistsError(path)
    temporary = path.with_name(f".{path.name}.partial")
    text = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with temporary.open("x", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _warning_codes(solution: object) -> str:
    diagnostics = getattr(solution, "diagnostics", None)
    warnings = getattr(diagnostics, "warnings", ()) or ()
    return ",".join(str(getattr(item, "code", "unknown")) for item in warnings)


def _relative_delta(current: np.ndarray, previous: np.ndarray) -> np.ndarray:
    return np.abs(current - previous) / np.maximum(
        1.0, np.maximum(np.abs(current), np.abs(previous))
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--r-out-ladder",
        nargs=3,
        type=float,
        default=(300.0, 600.0, 1200.0),
    )
    args = parser.parse_args(argv)
    radii = tuple(float(value) for value in args.r_out_ladder)
    if tuple(sorted(set(radii))) != radii or radii[0] <= 60.0:
        parser.error("r-out ladder must contain three increasing values above 60")
    if args.output_dir.exists():
        raise FileExistsError(f"refusing existing audit root: {args.output_dir}")
    args.output_dir.mkdir(parents=True)

    ell = np.arange(2, CHECKPOINT_LMAX[-1] + 1, dtype=np.int64)
    cumulative = np.empty(
        (len(radii), len(FRAMES), len(SELECTED_THETA), ell.size, 2),
        dtype=np.complex128,
    )
    branch_solver = np.empty((len(radii), ell.size, 2), dtype="U64")
    branch_warning = np.empty((len(radii), ell.size, 2), dtype="U256")
    branch_boundary = np.empty((len(radii), ell.size, 2), dtype=np.float64)
    branch_wronskian = np.empty_like(branch_boundary)
    branch_condition = np.empty_like(branch_boundary)
    cache_records: list[dict[str, object]] = []
    background = SchwarzschildBackground(M=1.0)

    for radius_index, r_out in enumerate(radii):
        boundary = BoundaryConfig(
            r_in_eps=1.0e-6,
            r_out=r_out,
            rtol=1.0e-10,
            atol=1.0e-12,
            required_eval_radius=60.0,
            experimental_required_radius_oracle="q018_riccati",
            outer_basis="jost_1_over_r",
            outer_series_order=160,
        )
        cache = _AnchorRadialCache()
        for frame_index, frame in enumerate(FRAMES):
            for angle_index, theta in enumerate(SELECTED_THETA):
                for ell_index, lmax in enumerate(ell):
                    result = compute_direct_metric_polarization(
                        background=background,
                        k=2.0,
                        r=60.0,
                        theta=float(theta),
                        phi=0.0,
                        A_plus=0.9 + 1.1j,
                        A_cross=0.4 + 0.6j,
                        lmax=int(lmax),
                        boundary_config=boundary,
                        radial_solver=cache,
                        observer_frame=frame,
                    )
                    cumulative[
                        radius_index, frame_index, angle_index, ell_index
                    ] = (result.h_plus, result.h_cross)
                print(
                    json.dumps(
                        {
                            "event": "fig4_selected_angle_shells_complete",
                            "r_out": r_out,
                            "observer_frame": frame,
                            "theta_over_pi": float(theta / np.pi),
                            **cache.metadata(),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )

        for ell_index, ell_value in enumerate(ell):
            for sector_index, sector in enumerate((Sector.ODD, Sector.EVEN)):
                key = (sector.value, int(ell_value), 2.0)
                solution = cache._solutions[key]
                diagnostics = solution.diagnostics
                branch_solver[radius_index, ell_index, sector_index] = str(
                    diagnostics.solver
                )
                branch_warning[radius_index, ell_index, sector_index] = (
                    _warning_codes(solution)
                )
                branch_boundary[radius_index, ell_index, sector_index] = float(
                    diagnostics.boundary_residual
                )
                branch_wronskian[radius_index, ell_index, sector_index] = float(
                    diagnostics.wronskian_residual
                )
                branch_condition[radius_index, ell_index, sector_index] = float(
                    diagnostics.match_condition_number
                )
        cache_records.append({"r_out": r_out, **cache.metadata()})

    zero = np.zeros((*cumulative.shape[:-2], 1, 2), dtype=np.complex128)
    shell = np.diff(np.concatenate((zero, cumulative), axis=-2), axis=-2)
    shell_fit = extrapolate_r_out_ladder(np.asarray(radii), shell)
    cumulative_fit = extrapolate_r_out_ladder(np.asarray(radii), cumulative)
    checkpoint_indices = np.asarray([value - 2 for value in CHECKPOINT_LMAX])
    checkpoint_values = cumulative[..., checkpoint_indices, :]
    checkpoint_delta = _relative_delta(
        checkpoint_values[..., 1:, :], checkpoint_values[..., :-1, :]
    )
    if not np.allclose(
        np.sum(shell, axis=-2),
        cumulative[..., -1, :],
        rtol=3.0e-13,
        atol=3.0e-13,
    ):
        raise RuntimeError("Fig. 4 shell contributions do not reconstruct lmax=240")

    npz = args.output_dir / "fig4_k2_full_shell_audit.npz"
    _atomic_npz(
        npz,
        {
            "kM": np.asarray(2.0),
            "observer_r": np.asarray(60.0),
            "r_out_ladder": np.asarray(radii),
            "observer_frames": np.asarray(FRAMES),
            "selected_theta": np.asarray(SELECTED_THETA),
            "selected_theta_over_pi": np.asarray(SELECTED_THETA) / np.pi,
            "ell": ell,
            "polarization": np.asarray(("plus", "cross")),
            "cumulative_field_r_out_ladder": cumulative,
            "shell_field_r_out_ladder": shell,
            "cumulative_field_extrapolated": cumulative_fit.extrapolated,
            "shell_field_extrapolated": shell_fit.extrapolated,
            "cumulative_r_out_uncertainty": cumulative_fit.uncertainty,
            "shell_r_out_uncertainty": shell_fit.uncertainty,
            "checkpoint_lmax": np.asarray(CHECKPOINT_LMAX),
            "checkpoint_field_r_out_ladder": checkpoint_values,
            "checkpoint_relative_delta": checkpoint_delta,
            "branch_sector": np.asarray(("odd", "even")),
            "branch_solver": branch_solver,
            "branch_warning_codes": branch_warning,
            "branch_boundary_residual": branch_boundary,
            "branch_wronskian_residual": branch_wronskian,
            "branch_match_condition_number": branch_condition,
        },
    )
    report: dict[str, object] = {
        "schema_version": "schwgw_fig4_k2_full_shell_audit_v1",
        "npz": str(npz),
        "npz_sha256": _sha256(npz),
        "kM": 2.0,
        "observer_r": 60.0,
        "r_out_ladder": list(radii),
        "observer_frames": list(FRAMES),
        "selected_theta_over_pi": [float(value / np.pi) for value in SELECTED_THETA],
        "ell_range": [2, int(ell[-1])],
        "checkpoint_lmax": list(CHECKPOINT_LMAX),
        "max_checkpoint_relative_delta": float(np.max(checkpoint_delta)),
        "max_shell_r_out_uncertainty": float(np.max(shell_fit.uncertainty)),
        "max_cumulative_r_out_uncertainty": float(
            np.max(cumulative_fit.uncertainty)
        ),
        "max_boundary_residual": float(np.max(branch_boundary)),
        "max_wronskian_residual": float(np.max(branch_wronskian)),
        "max_match_condition_number": float(np.max(branch_condition)),
        "radial_cache_by_r_out": cache_records,
        "paper_equivalence": "YELLOW",
        "strict_li_reproduction_green": False,
    }
    sidecar = args.output_dir / "fig4_k2_full_shell_audit.json"
    _atomic_json(sidecar, report)
    print(
        json.dumps(
            {
                "event": "fig4_k2_full_shell_audit_complete",
                "sidecar": str(sidecar),
                "sidecar_sha256": _sha256(sidecar),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
