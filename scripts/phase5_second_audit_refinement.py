#!/usr/bin/env python3
"""Generate bounded evidence for the 2026-08-03 second scientific audit.

This program does not promote or replace any accepted Figure 1--8 artifact.
It records the new Jost outer-boundary surface, finite-``r_out`` ladders,
explicit observer-frame probes, Fig. 4 shell/Q018 branches, and Fig. 5/6
phase decompositions in a fresh no-overwrite directory.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any

import numpy as np
from PIL import Image

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.io.direct_tablei import (
    AMPLITUDES,
    DenseRadialSpanCache,
    _radial_bounds,
    compute_direct_response_columns,
)
from schwgw.io.tablei import TABLEI_POINTS
from schwgw.numerics import BoundaryConfig, extrapolate_r_out_ladder, solve_radial_mode
from schwgw.numerics.matching import outer_asymptotic_basis
from schwgw.perturbations import Sector
from schwgw.scattering import compare_complex_phase


SCHEMA_VERSION = "schwgw_second_audit_refinement_v1"
R_OUT_LADDER = (300.0, 600.0, 1200.0)
PANEL_X_BOUNDS = ((266, 574), (580, 888), (894, 1202), (1208, 1516))
K_VALUES = np.arange(0.1, 4.01, 0.1)
OBSERVER_FRAMES = ("static_orthonormal", "li_literal_cartesian")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return _json_safe(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    return value


def _atomic_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".npz", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        np.savez(temporary, **arrays)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    text = json.dumps(_json_safe(payload), indent=2, sort_keys=True, allow_nan=False) + "\n"
    with tempfile.NamedTemporaryFile(
        dir=path.parent,
        mode="w",
        encoding="utf-8",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        handle.write(text)
        handle.flush()
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _warning_codes(solution: Any) -> str:
    warnings = getattr(solution.diagnostics, "warnings", ()) or ()
    return ",".join(str(getattr(warning, "code", "unknown")) for warning in warnings)


def _outer_basis_probe() -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    background = SchwarzschildBackground(M=1.0)
    rows: list[tuple[str, int, float, float, int, str, float, float, int]] = []
    for sector in (Sector.ODD, Sector.EVEN):
        for ell, k in ((2, 0.5), (20, 2.0), (120, 2.0), (140, 2.0), (240, 2.0)):
            for sign in (-1, 1):
                for basis in ("plane_wave", "jost_1_over_r"):
                    state = outer_asymptotic_basis(
                        sector=sector,
                        ell=ell,
                        r=300.0,
                        k=k,
                        background=background,
                        sign=sign,
                        basis=basis,
                        series_order=160,
                    )
                    rows.append(
                        (
                            sector.value,
                            ell,
                            k,
                            300.0,
                            sign,
                            basis,
                            state.series_residual,
                            state.tail_ratio,
                            state.series_order,
                        )
                    )
    arrays = {
        "outer_probe_sector": np.asarray([row[0] for row in rows]),
        "outer_probe_ell": np.asarray([row[1] for row in rows]),
        "outer_probe_kM": np.asarray([row[2] for row in rows]),
        "outer_probe_r_out": np.asarray([row[3] for row in rows]),
        "outer_probe_sign": np.asarray([row[4] for row in rows]),
        "outer_probe_basis": np.asarray([row[5] for row in rows]),
        "outer_probe_ode_residual": np.asarray([row[6] for row in rows]),
        "outer_probe_tail_ratio": np.asarray([row[7] for row in rows]),
        "outer_probe_series_order": np.asarray([row[8] for row in rows]),
    }
    jost = arrays["outer_probe_basis"] == "jost_1_over_r"
    plane = arrays["outer_probe_basis"] == "plane_wave"
    metadata = {
        "max_jost_local_ode_residual": float(
            np.max(arrays["outer_probe_ode_residual"][jost])
        ),
        "min_plane_wave_local_ode_residual": float(
            np.min(arrays["outer_probe_ode_residual"][plane])
        ),
        "plane_wave_retained_only_as_explicit_diagnostic": True,
    }
    return arrays, metadata


def _radial_shell_ladder(
    *, profile: str
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    background = SchwarzschildBackground(M=1.0)
    shell_ells = (
        np.arange(108, 133, dtype=np.int64)
        if profile == "full"
        else np.asarray((108, 112, 116, 120, 124, 128, 132), dtype=np.int64)
    )
    phase = np.empty((len(R_OUT_LADDER), shell_ells.size, 2), dtype=np.complex128)
    solver = np.empty(phase.shape, dtype="U48")
    warning_codes = np.empty(phase.shape, dtype="U160")
    boundary_residual = np.empty(phase.shape, dtype=np.float64)
    for radius_index, r_out in enumerate(R_OUT_LADDER):
        boundary = BoundaryConfig(
            r_in_eps=1.0e-6,
            r_out=r_out,
            rtol=1.0e-10,
            atol=1.0e-12,
            outer_basis="jost_1_over_r",
            outer_series_order=160,
        )
        for ell_index, ell in enumerate(shell_ells):
            for sector_index, sector in enumerate((Sector.ODD, Sector.EVEN)):
                solution = solve_radial_mode(sector, int(ell), 2.0, background, boundary)
                phase[radius_index, ell_index, sector_index] = solution.phase_factor
                solver[radius_index, ell_index, sector_index] = solution.diagnostics.solver
                warning_codes[radius_index, ell_index, sector_index] = _warning_codes(
                    solution
                )
                boundary_residual[radius_index, ell_index, sector_index] = (
                    solution.diagnostics.boundary_residual
                )
    fit = extrapolate_r_out_ladder(np.asarray(R_OUT_LADDER), phase)

    q018_ells = (
        np.arange(153, 181, dtype=np.int64)
        if profile == "full"
        else np.asarray((153, 160, 170, 180), dtype=np.int64)
    )
    q018_phase = np.full((q018_ells.size, 2), np.nan + 1.0j * np.nan)
    q018_solver = np.empty(q018_phase.shape, dtype="U64")
    q018_warning = np.empty(q018_phase.shape, dtype="U192")
    q018_error = np.empty(q018_phase.shape, dtype="U512")
    q018_boundary = BoundaryConfig(
        r_in_eps=1.0e-6,
        r_out=300.0,
        rtol=1.0e-10,
        atol=1.0e-12,
        required_eval_radius=60.0,
        experimental_required_radius_oracle="q018_riccati",
        outer_basis="jost_1_over_r",
        outer_series_order=160,
    )
    for ell_index, ell in enumerate(q018_ells):
        for sector_index, sector in enumerate((Sector.ODD, Sector.EVEN)):
            try:
                solution = solve_radial_mode(
                    sector, int(ell), 2.0, background, q018_boundary
                )
            except RuntimeError as exc:
                q018_solver[ell_index, sector_index] = "failed_closed"
                q018_warning[ell_index, sector_index] = ""
                q018_error[ell_index, sector_index] = str(exc)[:512]
            else:
                q018_phase[ell_index, sector_index] = solution.phase_factor
                q018_solver[ell_index, sector_index] = solution.diagnostics.solver
                q018_warning[ell_index, sector_index] = _warning_codes(solution)
                q018_error[ell_index, sector_index] = ""
    arrays = {
        "fig24_r_out_ladder": np.asarray(R_OUT_LADDER),
        "fig4_shell_ell": shell_ells,
        "fig4_shell_sector": np.asarray(("odd", "even")),
        "fig4_shell_phase_factor_ladder": phase,
        "fig4_shell_phase_factor_extrapolated": fit.extrapolated,
        "fig4_shell_phase_factor_uncertainty": fit.uncertainty,
        "fig4_shell_adjacent_relative_change": fit.adjacent_relative_change,
        "fig4_shell_solver": solver,
        "fig4_shell_warning_codes": warning_codes,
        "fig4_shell_boundary_residual": boundary_residual,
        "fig4_q018_ell": q018_ells,
        "fig4_q018_phase_factor": q018_phase,
        "fig4_q018_solver": q018_solver,
        "fig4_q018_warning_codes": q018_warning,
        "fig4_q018_error": q018_error,
    }
    metadata = {
        "kM": 2.0,
        "kr_at_observer_r60": 120.0,
        "shell_range": [int(shell_ells[0]), int(shell_ells[-1])],
        "shell_sampling": profile,
        "q018_envelope": [153, 180],
        "q018_sampling": profile,
        "max_shell_extrapolation_uncertainty": float(np.max(fit.uncertainty)),
        "fig2_scope": (
            "same high-frequency radial shell identities; strict Psi4 shell "
            "reconstruction remains a separate high-precision audit"
        ),
        "fig4_scope": "radial shell/Q018 audit; not a replacement raster",
    }
    return arrays, metadata


def _tablei_ladder(
    *, frequencies: tuple[float, ...], lmax: int
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    background = SchwarzschildBackground(M=1.0)
    shape = (
        len(R_OUT_LADDER),
        len(frequencies),
        len(OBSERVER_FRAMES),
        len(TABLEI_POINTS),
        2,
    )
    response = np.empty(shape, dtype=np.complex128)
    axis_epsilons = np.asarray((1.0e-4, 1.0e-5, 1.0e-6, 1.0e-7))
    axis_response = np.empty(
        (
            len(R_OUT_LADDER),
            len(frequencies),
            len(OBSERVER_FRAMES),
            axis_epsilons.size,
            2,
        ),
        dtype=np.complex128,
    )
    cache_counts = np.empty((len(R_OUT_LADDER), len(frequencies), 3), dtype=np.int64)
    lower, anchor, upper = _radial_bounds()
    for radius_index, r_out in enumerate(R_OUT_LADDER):
        boundary = BoundaryConfig(
            r_in_eps=1.0e-6,
            r_out=r_out,
            rtol=1.0e-10,
            atol=1.0e-12,
            outer_basis="jost_1_over_r",
            outer_series_order=160,
        )
        for frequency_index, kM in enumerate(frequencies):
            cache = DenseRadialSpanCache(lower=lower, anchor=anchor, upper=upper)
            for frame_index, observer_frame in enumerate(OBSERVER_FRAMES):
                for point_index, point in enumerate(TABLEI_POINTS):
                    columns = compute_direct_response_columns(
                        background=background,
                        k=kM,
                        r=point.r,
                        theta=point.theta,
                        phi=point.phi,
                        lmax=lmax,
                        boundary_config=boundary,
                        radial_solver=cache,
                        observer_frame=observer_frame,
                    )
                    incident_phase = np.exp(1.0j * kM * point.r * np.cos(point.theta))
                    response[radius_index, frequency_index, frame_index, point_index] = (
                        columns.F_plus
                        + columns.h_plus_from_cross
                        / (AMPLITUDES["plus"] * incident_phase),
                        columns.F_cross
                        + columns.h_cross_from_plus
                        / (AMPLITUDES["cross"] * incident_phase),
                    )
                axis = TABLEI_POINTS[0]
                for epsilon_index, epsilon in enumerate(axis_epsilons):
                    columns = compute_direct_response_columns(
                        background=background,
                        k=kM,
                        r=axis.r,
                        theta=axis.theta,
                        phi=axis.phi,
                        lmax=lmax,
                        boundary_config=boundary,
                        radial_solver=cache,
                        observer_frame=observer_frame,
                        axis_regularization=float(epsilon),
                    )
                    incident_phase = np.exp(1.0j * kM * axis.r)
                    axis_response[
                        radius_index, frequency_index, frame_index, epsilon_index
                    ] = (
                        columns.F_plus
                        + columns.h_plus_from_cross
                        / (AMPLITUDES["plus"] * incident_phase),
                        columns.F_cross
                        + columns.h_cross_from_plus
                        / (AMPLITUDES["cross"] * incident_phase),
                    )
            counts = cache.metadata()
            cache_counts[radius_index, frequency_index] = (
                counts["unique_solution_count"],
                counts["reuse_count"],
                counts["dense_local_q018_count"],
            )
    fit = extrapolate_r_out_ladder(np.asarray(R_OUT_LADDER), response)
    arrays = {
        "fig56_probe_kM": np.asarray(frequencies),
        "fig56_probe_lmax": np.asarray(lmax),
        "fig56_probe_frames": np.asarray(OBSERVER_FRAMES),
        "fig56_probe_point_ids": np.asarray([point.point_id for point in TABLEI_POINTS]),
        "fig56_probe_polarization": np.asarray(("plus", "cross")),
        "fig56_response_ladder": response,
        "fig56_response_extrapolated": fit.extrapolated,
        "fig56_response_uncertainty": fit.uncertainty,
        "fig56_response_adjacent_relative_change": fit.adjacent_relative_change,
        "fig56_axis_epsilon": axis_epsilons,
        "fig56_axis_response": axis_response,
        "fig56_cache_counts": cache_counts,
    }
    frame_delta = np.abs(response[:, :, 0] - response[:, :, 1]) / np.maximum(
        1.0, np.maximum(np.abs(response[:, :, 0]), np.abs(response[:, :, 1]))
    )
    metadata = {
        "frequencies": list(frequencies),
        "lmax": lmax,
        "profile": "bounded representative" if len(frequencies) < 40 else "full",
        "max_r_out_extrapolation_uncertainty": float(np.max(fit.uncertainty)),
        "max_static_vs_li_literal_relative_delta": float(np.max(frame_delta)),
        "raw_and_extrapolated_retained": True,
        "observer_frame_policy": {
            "static_orthonormal": "physical default",
            "li_literal_cartesian": "literal paper-convention diagnostic",
        },
    }
    return arrays, metadata


def _marker_mask(image: np.ndarray, color: str) -> np.ndarray:
    if color == "red":
        return (
            (image[:, :, 0] > 180)
            & (image[:, :, 0] > image[:, :, 1] * 1.45)
            & (image[:, :, 0] > image[:, :, 2] * 1.35)
            & (image[:, :, 1] < 160)
        )
    return (
        (image[:, :, 2] > 150)
        & (image[:, :, 2] > image[:, :, 0] * 1.35)
        & (image[:, :, 2] > image[:, :, 1] * 1.25)
        & (image[:, :, 0] < 170)
    )


def _extract_markers(
    mask: np.ndarray,
    *,
    y_bounds: tuple[int, int],
    y_limits: tuple[float, float],
) -> np.ndarray:
    values = np.full((40, 4), np.nan)
    y0, y1 = y_bounds
    for panel, (x0, x1) in enumerate(PANEL_X_BOUNDS):
        for row, km in enumerate(K_VALUES):
            x = x0 + (x1 - x0) * km / 4.0
            for radius in (3, 4, 5):
                lo = max(x0, int(round(x)) - radius)
                hi = min(x1 + 1, int(round(x)) + radius + 1)
                y_hits, _ = np.where(mask[y0 : y1 + 1, lo:hi])
                if y_hits.size:
                    y = float(np.median(y_hits + y0))
                    values[row, panel] = y_limits[0] + (y - y0) / (y1 - y0) * (
                        y_limits[1] - y_limits[0]
                    )
                    break
    return values


def _paper_phase_diagnostics(
    *, paper_page: Path, merged_npz: Path
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    image = np.asarray(Image.open(paper_page).convert("RGB"))
    if image.shape != (2200, 1700, 3):
        raise ValueError("paper phase digitization requires the frozen 1700x2200 raster")
    red = _marker_mask(image, "red")
    reference_abs = np.concatenate(
        (
            _extract_markers(red, y_bounds=(215, 474), y_limits=(10.0, 0.0)),
            _extract_markers(red, y_bounds=(1014, 1273), y_limits=(4.0, 0.0)),
        ),
        axis=1,
    )
    reference_arg = np.concatenate(
        (
            _extract_markers(
                red,
                y_bounds=(487, 746),
                y_limits=(1.25 * np.pi, -1.25 * np.pi),
            ),
            _extract_markers(
                red,
                y_bounds=(1286, 1545),
                y_limits=(1.25 * np.pi, -1.25 * np.pi),
            ),
        ),
        axis=1,
    )
    with np.load(merged_npz, allow_pickle=False) as data:
        kM = np.asarray(data["kM_values"], dtype=np.float64)
        computed = {
            "plus": np.asarray(data["F_plus_complex"], dtype=np.complex128),
            "cross": np.asarray(data["F_cross_complex"], dtype=np.complex128),
        }
    if not np.allclose(kM, K_VALUES, rtol=0.0, atol=1.0e-14):
        raise ValueError("merged Fig. 5/6 frequency grid differs from paper digitization")
    reference = reference_abs * np.exp(1.0j * reference_arg)
    arrays: dict[str, np.ndarray] = {
        "paper_phase_kM": kM,
        "paper_red_abs": reference_abs,
        "paper_red_phase_raw": reference_arg,
    }
    report: dict[str, Any] = {
        "paper_page": str(paper_page),
        "paper_page_sha256": _sha256(paper_page),
        "merged_npz": str(merged_npz),
        "merged_npz_sha256": _sha256(merged_npz),
        "raster_level_only": True,
        "polarizations": {},
    }
    finite_reference = np.isfinite(reference_abs) & np.isfinite(reference_arg)
    for name, values in computed.items():
        wrapped = np.full(values.shape, np.nan)
        unwrapped = np.full(values.shape, np.nan)
        panel_removed = np.full(values.shape, np.nan)
        panel_metrics: list[dict[str, Any]] = []
        for panel in range(values.shape[1]):
            mask = finite_reference[:, panel]
            diagnostics = compare_complex_phase(
                values[mask, panel], reference[mask, panel], frequency_axis=0
            )
            wrapped[mask, panel] = diagnostics.wrapped_residual
            unwrapped[mask, panel] = diagnostics.unwrapped_residual
            panel_removed[mask, panel] = diagnostics.panel_offset_removed_residual
            panel_metrics.append(
                {
                    "panel": panel,
                    "sample_count": int(np.count_nonzero(mask)),
                    "raw_circular_mae_rad": diagnostics.raw_mae,
                    "unwrapped_mae_rad": float(
                        np.mean(np.abs(diagnostics.unwrapped_residual))
                    ),
                    "global_offset_rad": diagnostics.global_offset,
                    "offset_removed_mae_rad": diagnostics.global_offset_removed_mae,
                }
            )
        all_mask = finite_reference
        global_diagnostics = compare_complex_phase(
            values[all_mask], reference[all_mask], frequency_axis=0
        )
        arrays[f"fig56_{name}_phase_wrapped_residual"] = wrapped
        arrays[f"fig56_{name}_phase_unwrapped_residual"] = unwrapped
        arrays[f"fig56_{name}_phase_panel_offset_removed_residual"] = panel_removed
        report["polarizations"][name] = {
            "global_raw_circular_mae_rad": global_diagnostics.raw_mae,
            "one_global_offset_rad": global_diagnostics.global_offset,
            "one_global_offset_removed_mae_rad": (
                global_diagnostics.global_offset_removed_mae
            ),
            "panels": panel_metrics,
        }
    return arrays, report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--profile", choices=("quick", "full"), default="quick")
    parser.add_argument("--tablei-frequencies", type=float, nargs="+", default=(0.5, 2.0))
    parser.add_argument("--tablei-lmax", type=int, default=12)
    parser.add_argument(
        "--paper-page",
        type=Path,
        default=Path(
            "runs/phase5/paper_figures/audit_repairs_20260802/"
            "paper_reference_pages/page-10.png"
        ),
    )
    parser.add_argument(
        "--fig56-merged",
        type=Path,
        default=Path(
            "runs/phase5/paper_figures/direct_curvature_odejet_recompute_20260802/"
            "fig56_direct_curvature_uniform40.npz"
        ),
    )
    args = parser.parse_args()
    if args.tablei_lmax < 2:
        parser.error("--tablei-lmax must be at least 2")
    frequencies = tuple(float(value) for value in args.tablei_frequencies)
    if not frequencies or any(value <= 0.0 for value in frequencies):
        parser.error("--tablei-frequencies must contain positive values")
    args.tablei_frequencies = frequencies
    return args


def main() -> int:
    args = parse_args()
    if args.output_dir.exists():
        raise FileExistsError(f"refusing existing evidence root: {args.output_dir}")
    args.output_dir.mkdir(parents=True)
    arrays: dict[str, np.ndarray] = {}
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "strict_li_paper_reproduction_green": False,
        "paper_equivalence": "YELLOW",
        "profile": args.profile,
        "sections": {},
    }
    for key, producer in (
        ("outer_basis", _outer_basis_probe),
        ("fig2_fig4_shells", lambda: _radial_shell_ladder(profile=args.profile)),
        (
            "fig5_fig6_tablei",
            lambda: _tablei_ladder(
                frequencies=args.tablei_frequencies,
                lmax=args.tablei_lmax,
            ),
        ),
        (
            "fig5_fig6_phase",
            lambda: _paper_phase_diagnostics(
                paper_page=args.paper_page,
                merged_npz=args.fig56_merged,
            ),
        ),
    ):
        section_arrays, section_report = producer()
        overlap = set(arrays).intersection(section_arrays)
        if overlap:
            raise RuntimeError(f"duplicate audit arrays: {sorted(overlap)}")
        arrays.update(section_arrays)
        report["sections"][key] = section_report
        _atomic_npz(args.output_dir / f"{key}.npz", section_arrays)
        _atomic_json(args.output_dir / f"{key}.json", section_report)
        print(json.dumps({"event": "second_audit_section_complete", "section": key}))
    npz_path = args.output_dir / "second_audit_refinement.npz"
    _atomic_npz(npz_path, arrays)
    report["npz"] = str(npz_path)
    report["npz_sha256"] = _sha256(npz_path)
    report["array_count"] = len(arrays)
    report_path = args.output_dir / "second_audit_refinement.json"
    _atomic_json(report_path, report)
    print(
        json.dumps(
            {
                "event": "second_audit_refinement_complete",
                "report": str(report_path),
                "report_sha256": _sha256(report_path),
                "paper_equivalence": "YELLOW",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
