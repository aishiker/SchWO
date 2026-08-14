from __future__ import annotations

import argparse
from datetime import datetime, timezone
import sys

import numpy as np

from schwgw.io import (
    AmplificationGridResult,
    ConfigError,
    GridResult,
    ResultFormatError,
    load_config,
    load_results,
    run_solver_grid,
    save_amplification_results,
    save_results,
)


compute_polarization = None


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        return _run(args)
    if args.command == "plot-wavefield":
        return _plot_wavefield(args)
    if args.command == "plot-convergence":
        return _plot_convergence(args)
    if args.command == "plot-fig3-panel":
        return _plot_fig3_panel(args)
    if args.command == "plot-fig3-multifrequency-panel":
        return _plot_fig3_multifrequency_panel(args)
    if args.command == "plot-fig4-exact-angular":
        return _plot_fig4_exact_angular(args)
    if args.command == "plot-fig4-all-frequency-exact-angular":
        return _plot_fig4_all_frequency_exact_angular(args)
    if args.command == "plot-fig7-apparent-four-frequency":
        return _plot_fig7_apparent_four_frequency(args)
    if args.command == "plot-amplification":
        return _plot_amplification(args)
    if args.command == "plot-tablei-four-frequency":
        return _plot_tablei_four_frequency(args)
    if args.command == "plot-tablei-review-grid":
        return _plot_tablei_review_grid(args)
    if args.command == "compute-amplification":
        return _compute_amplification(args)
    if args.command == "extract-tablei-four-frequency":
        return _extract_tablei_four_frequency(args)
    parser.print_help()
    return 0


def _run(args: argparse.Namespace) -> int:
    try:
        solver = compute_polarization
        if solver is None:
            from schwgw.scattering.partial_wave import compute_polarization as solver

        config = load_config(args.config)
        output = args.out if args.out is not None else config.output
        command = ["schwgw.cli", "run", str(args.config), "--out", str(output)]
        result = run_solver_grid(
            config,
            polarization_solver=solver,
            source_command=command,
        )
        save_results(result, output)
    except (ConfigError, RuntimeError, ValueError) as exc:
        print(f"schwgw run: {exc}", file=sys.stderr)
        return 2
    return 0


def _plot_wavefield(args: argparse.Namespace) -> int:
    try:
        from schwgw.viz import plot_wavefield_from_result

        plot_wavefield_from_result(
            args.result,
            component=args.component,
            quantity=args.quantity,
            output_path=args.out,
        )
    except (RuntimeError, ValueError) as exc:
        print(f"schwgw plot-wavefield: {exc}", file=sys.stderr)
        return 2
    return 0


def _plot_convergence(args: argparse.Namespace) -> int:
    try:
        from schwgw.viz import plot_convergence_from_result

        plot_convergence_from_result(args.result, output_path=args.out)
    except (RuntimeError, ValueError) as exc:
        print(f"schwgw plot-convergence: {exc}", file=sys.stderr)
        return 2
    return 0


def _plot_fig3_panel(args: argparse.Namespace) -> int:
    try:
        from schwgw.viz import plot_fig3_panel_from_result

        plot_fig3_panel_from_result(
            args.result,
            quantity=args.quantity,
            interpolation=args.interpolation,
            output_path=args.out,
            dpi=args.dpi,
        )
    except (RuntimeError, ValueError) as exc:
        print(f"schwgw plot-fig3-panel: {exc}", file=sys.stderr)
        return 2
    return 0


def _plot_fig3_multifrequency_panel(args: argparse.Namespace) -> int:
    try:
        from schwgw.viz import plot_fig3_multifrequency_panel_from_results

        plot_fig3_multifrequency_panel_from_results(
            args.results,
            quantity=args.quantity,
            interpolation=args.interpolation,
            output_path=args.out,
            dpi=args.dpi,
            style=args.style,
        )
    except (RuntimeError, ValueError) as exc:
        print(f"schwgw plot-fig3-multifrequency-panel: {exc}", file=sys.stderr)
        return 2
    return 0


def _plot_fig4_exact_angular(args: argparse.Namespace) -> int:
    try:
        from schwgw.viz import plot_fig4_exact_angular_from_result

        plot_fig4_exact_angular_from_result(
            args.result,
            output_path=args.out,
            phi=args.phi,
            dpi=args.dpi,
            _created_by_cli=True,
        )
    except (RuntimeError, ValueError) as exc:
        print(f"schwgw plot-fig4-exact-angular: {exc}", file=sys.stderr)
        return 2
    return 0


def _plot_fig4_all_frequency_exact_angular(args: argparse.Namespace) -> int:
    try:
        from schwgw.viz import plot_fig4_all_frequency_exact_angular_from_results

        plot_fig4_all_frequency_exact_angular_from_results(
            args.results,
            output_path=args.out,
            phi=args.phi,
            dpi=args.dpi,
            _created_by_cli=True,
        )
    except (RuntimeError, ValueError) as exc:
        print(
            f"schwgw plot-fig4-all-frequency-exact-angular: {exc}",
            file=sys.stderr,
        )
        return 2
    return 0


def _plot_fig7_apparent_four_frequency(args: argparse.Namespace) -> int:
    try:
        from schwgw.viz import render_fig7_apparent_four_frequency

        render_fig7_apparent_four_frequency(
            args.results,
            output_dir=args.out_dir,
            basename=args.basename,
            created_by_cli=True,
        )
    except (RuntimeError, ValueError) as exc:
        print(f"schwgw plot-fig7-apparent-four-frequency: {exc}", file=sys.stderr)
        return 2
    return 0


def _plot_amplification(args: argparse.Namespace) -> int:
    try:
        from schwgw.viz import plot_amplification_from_result

        plot_amplification_from_result(
            args.result,
            quantity=args.quantity,
            output_path=args.out,
            dpi=args.dpi,
        )
    except (RuntimeError, ValueError) as exc:
        print(f"schwgw plot-amplification: {exc}", file=sys.stderr)
        return 2
    return 0


def _plot_tablei_four_frequency(args: argparse.Namespace) -> int:
    try:
        from schwgw.viz import plot_tablei_four_frequency_report

        plot_tablei_four_frequency_report(
            args.result,
            output_dir=args.out_dir,
            dpi=args.dpi,
            _created_by_cli=True,
        )
    except (RuntimeError, ValueError) as exc:
        print(f"schwgw plot-tablei-four-frequency: {exc}", file=sys.stderr)
        return 2
    return 0


def _plot_tablei_review_grid(args: argparse.Namespace) -> int:
    try:
        from schwgw.viz import plot_tablei_review_grid_diagnostics

        plot_tablei_review_grid_diagnostics(
            args.exact_result,
            args.kirchhoff_result,
            output_dir=args.out_dir,
            dpi=args.dpi,
            created_by_cli=True,
        )
    except (RuntimeError, ValueError) as exc:
        print(f"schwgw plot-tablei-review-grid: {exc}", file=sys.stderr)
        return 2
    return 0


def _compute_amplification(args: argparse.Namespace) -> int:
    try:
        lensed = load_results(args.result)
        command = [
            "schwgw.cli",
            "compute-amplification",
            str(args.result),
            "--out",
            str(args.out),
        ]
        result = _compute_amplification_from_lensed_result(
            lensed,
            source_lensed_result_path=str(args.result),
            source_command=command,
        )
        save_amplification_results(result, args.out)
    except (ResultFormatError, RuntimeError, ValueError) as exc:
        print(f"schwgw compute-amplification: {exc}", file=sys.stderr)
        return 2
    return 0


def _extract_tablei_four_frequency(args: argparse.Namespace) -> int:
    try:
        from schwgw.io import (
            builtin_tablei_points,
            extract_tablei_four_frequency_from_amplification_results,
        )

        extract_tablei_four_frequency_from_amplification_results(
            args.results,
            output_path=args.out,
            points=builtin_tablei_points(args.builtin_points),
            created_by_cli=True,
        )
    except (ResultFormatError, RuntimeError, ValueError) as exc:
        print(f"schwgw extract-tablei-four-frequency: {exc}", file=sys.stderr)
        return 2
    return 0


def _compute_amplification_from_lensed_result(
    lensed: GridResult,
    *,
    source_lensed_result_path: str,
    source_command: list[str],
) -> AmplificationGridResult:
    from schwgw.scattering.transmission import (
        compute_pointwise_amplification,
        flat_no_lens_baseline_at_point,
    )

    config = _metadata_dict(lensed.metadata, "config")
    background = _metadata_dict(config, "background")
    wave = _metadata_dict(config, "wave")
    numerics = _metadata_dict(config, "numerics")
    mass = float(background.get("M", 1.0))
    k = float(wave["kM"]) / mass
    a_plus = _metadata_complex(wave["A_plus"])
    a_cross = _metadata_complex(wave["A_cross"])
    lmax = int(numerics.get("lmax", lensed.metadata.get("lmax", 2)))

    radius, theta_grid, phi_grid, valid_mask = _observer_arrays(lensed)
    h_plus_unlensed = np.full(lensed.h_plus.shape, np.nan + 1j * np.nan, dtype=np.complex128)
    h_cross_unlensed = np.full(lensed.h_cross.shape, np.nan + 1j * np.nan, dtype=np.complex128)
    for index in zip(*np.nonzero(valid_mask), strict=True):
        baseline_plus, baseline_cross = flat_no_lens_baseline_at_point(
            k=k,
            r=float(radius[index]),
            theta=float(theta_grid[index]),
            phi=float(phi_grid[index]),
            A_plus=a_plus,
            A_cross=a_cross,
            lmax=lmax,
        )
        h_plus_unlensed[index] = baseline_plus
        h_cross_unlensed[index] = baseline_cross

    amplification = compute_pointwise_amplification(
        h_plus_lensed=lensed.h_plus,
        h_cross_lensed=lensed.h_cross,
        h_plus_unlensed=h_plus_unlensed,
        h_cross_unlensed=h_cross_unlensed,
        valid_lensed_mask=valid_mask,
        A_plus=a_plus,
        A_cross=a_cross,
    )
    metadata = dict(amplification.metadata)
    metadata.update(
        {
            "case_id": f"{lensed.metadata.get('case_id', 'UNKNOWN')}_AMPLIFICATION",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source_lensed_result_path": source_lensed_result_path,
            "source_command": source_command,
            "source_case_id": lensed.metadata.get("case_id"),
            "source_grid": lensed.metadata.get("grid"),
            "source_convention": lensed.metadata.get("convention"),
            "grid": lensed.metadata.get("grid", {}),
            "k": k,
            "lmax": lmax,
            "baseline_api": "compute_flat_no_lens_polarization",
        }
    )
    return AmplificationGridResult(
        theta=lensed.theta,
        phi=lensed.phi,
        F_plus_complex=amplification.F_plus_complex,
        F_cross_complex=amplification.F_cross_complex,
        amplification_plus=amplification.amplification_plus,
        amplification_cross=amplification.amplification_cross,
        intensity_plus_ratio=amplification.intensity_plus_ratio,
        intensity_cross_ratio=amplification.intensity_cross_ratio,
        F_pol_norm=amplification.F_pol_norm,
        I_pol_ratio=amplification.I_pol_ratio,
        valid_ratio_plus_mask=amplification.valid_ratio_plus_mask,
        valid_ratio_cross_mask=amplification.valid_ratio_cross_mask,
        valid_ratio_norm_mask=amplification.valid_ratio_norm_mask,
        metadata=metadata,
        x=lensed.x,
        z=lensed.z,
        r=lensed.r,
        valid_mask=lensed.valid_mask,
    )


def _observer_arrays(result: GridResult) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    grid = result.metadata.get("grid", {})
    grid_kind = grid.get("kind") if isinstance(grid, dict) else None
    if grid_kind == "xz_plane" or result.r is not None or result.valid_mask is not None:
        if result.r is None or result.valid_mask is None:
            raise ValueError("x-z lensed result requires saved r and valid_mask fields.")
        return (
            np.asarray(result.r, dtype=float),
            np.asarray(result.theta, dtype=float),
            np.asarray(result.phi, dtype=float),
            np.asarray(result.valid_mask, dtype=bool),
        )

    observer_r = grid.get("r") if isinstance(grid, dict) else None
    if observer_r is None:
        observer_r = _metadata_dict(result.metadata, "config").get("observer", {}).get("r")
    if observer_r is None:
        raise ValueError("Angular lensed result metadata must record observer radius.")
    theta_grid, phi_grid = np.meshgrid(result.theta, result.phi, indexing="ij")
    valid_mask = np.isfinite(result.h_plus) & np.isfinite(result.h_cross)
    radius = np.full(result.h_plus.shape, float(observer_r), dtype=float)
    return radius, theta_grid, phi_grid, valid_mask


def _metadata_dict(metadata: dict, key: str) -> dict:
    value = metadata.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"Saved lensed result metadata missing object: {key}.")
    return value


def _metadata_complex(value: object) -> complex:
    if isinstance(value, dict):
        return complex(float(value.get("real", 0.0)), float(value.get("imag", 0.0)))
    return complex(value)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="schwgw")
    subparsers = parser.add_subparsers(dest="command")

    run = subparsers.add_parser("run", help="run a YAML-driven solver output job")
    run.add_argument("config", help="YAML solver config")
    run.add_argument("--out", help="output .npz, .h5, or .hdf5 path")

    wavefield = subparsers.add_parser(
        "plot-wavefield",
        help="plot a saved h_plus/h_cross field without recomputing physics",
    )
    wavefield.add_argument("result", help="saved .npz, .h5, or .hdf5 result")
    wavefield.add_argument("--component", required=True, help="h_plus or h_cross")
    wavefield.add_argument("--quantity", required=True, help="real, imag, abs, or phase")
    wavefield.add_argument("--out", required=True, help="output PNG path")

    convergence = subparsers.add_parser(
        "plot-convergence",
        help="plot saved convergence history without rerunning the solver",
    )
    convergence.add_argument("result", help="saved .npz, .h5, or .hdf5 result")
    convergence.add_argument("--out", required=True, help="output PNG path")

    fig3_panel = subparsers.add_parser(
        "plot-fig3-panel",
        help="plot saved x-z h_plus/h_cross Fig.3-lite panel without recomputing physics",
    )
    fig3_panel.add_argument("result", help="saved .npz, .h5, or .hdf5 x-z result")
    fig3_panel.add_argument("--quantity", required=True, help="real")
    fig3_panel.add_argument(
        "--interpolation",
        choices=["nearest", "bilinear", "bicubic"],
        default="nearest",
        help="display interpolation for imshow; default is nearest",
    )
    fig3_panel.add_argument("--out", required=True, help="output PNG or PDF path")
    fig3_panel.add_argument(
        "--dpi",
        type=_positive_int,
        default=180,
        help="figure DPI for raster output; default is 180",
    )

    fig3_multifrequency = subparsers.add_parser(
        "plot-fig3-multifrequency-panel",
        help=(
            "plot saved x-z h_plus/h_cross Fig.3-lite panels for "
            "kM=0.5,1.0,1.5,2.0 without recomputing physics"
        ),
    )
    fig3_multifrequency.add_argument(
        "results",
        nargs=4,
        help="four saved .npz, .h5, or .hdf5 x-z results in increasing kM order",
    )
    fig3_multifrequency.add_argument("--quantity", required=True, help="real")
    fig3_multifrequency.add_argument(
        "--interpolation",
        choices=["nearest", "bilinear", "bicubic"],
        default="nearest",
        help="display interpolation for imshow; default is nearest",
    )
    fig3_multifrequency.add_argument(
        "--out",
        required=True,
        help="output PNG or PDF path",
    )
    fig3_multifrequency.add_argument(
        "--dpi",
        type=_positive_int,
        default=180,
        help="figure DPI for raster output; default is 180",
    )
    fig3_multifrequency.add_argument(
        "--style",
        choices=["default", "publication"],
        default="default",
        help="rendering layout style; default preserves the historical layout",
    )
    fig4_exact = subparsers.add_parser(
        "plot-fig4-exact-angular",
        help=(
            "plot saved R60 kM=2 exact angular h_plus/h_cross curves at fixed phi "
            "without recomputing physics"
        ),
    )
    fig4_exact.add_argument("result", help="saved angular .npz result")
    fig4_exact.add_argument("--out", required=True, help="output PNG path")
    fig4_exact.add_argument(
        "--phi",
        type=float,
        default=0.0,
        help="saved phi coordinate to extract; default is 0.0",
    )
    fig4_exact.add_argument(
        "--dpi",
        type=_positive_int,
        default=300,
        help="figure DPI for raster output; default is 300",
    )
    fig4_all_frequency = subparsers.add_parser(
        "plot-fig4-all-frequency-exact-angular",
        help=(
            "plot saved R60 exact angular h_plus/h_cross curves for "
            "kM=0.5,1.0,1.5,2.0 at fixed phi without recomputing physics"
        ),
    )
    fig4_all_frequency.add_argument(
        "results",
        nargs=4,
        help="four saved angular .npz results in increasing kM order",
    )
    fig4_all_frequency.add_argument("--out", required=True, help="output PNG path")
    fig4_all_frequency.add_argument(
        "--phi",
        type=float,
        default=0.0,
        help="saved phi coordinate to extract; default is 0.0",
    )
    fig4_all_frequency.add_argument(
        "--dpi",
        type=_positive_int,
        default=300,
        help="figure DPI for raster output; default is 300",
    )
    fig7_apparent = subparsers.add_parser(
        "plot-fig7-apparent-four-frequency",
        help=(
            "render saved diagnostic Fig. 7 apparent wavefields for "
            "kM=0.5,1.0,1.5,2.0 without recomputing physics"
        ),
    )
    fig7_apparent.add_argument(
        "results",
        nargs=4,
        help="four saved Fig. 7 apparent NPZ files in increasing kM order",
    )
    fig7_apparent.add_argument(
        "--out-dir",
        required=True,
        help="directory for PDF, display PNG, numerical-audit PNG, and manifest",
    )
    fig7_apparent.add_argument(
        "--basename",
        default="fig7_apparent_four_frequency",
        help="output filename stem; default is fig7_apparent_four_frequency",
    )
    amplification_plot = subparsers.add_parser(
        "plot-amplification",
        help="plot a saved M5 pointwise amplification field without recomputing physics",
    )
    amplification_plot.add_argument(
        "result",
        help="saved amplification .npz, .h5, or .hdf5 result",
    )
    amplification_plot.add_argument(
        "--quantity",
        required=True,
        help=(
            "F_pol_norm, I_pol_ratio, amplification_plus, amplification_cross, "
            "or a supported saved scalar"
        ),
    )
    amplification_plot.add_argument("--out", required=True, help="output PNG or PDF path")
    amplification_plot.add_argument(
        "--dpi",
        type=_positive_int,
        default=180,
        help="figure DPI for raster output; default is 180",
    )
    tablei_plot = subparsers.add_parser(
        "plot-tablei-four-frequency",
        help=(
            "create read-only CSV, Markdown, and pilot PNG reports from a "
            "saved Table-I four-frequency extraction artifact"
        ),
    )
    tablei_plot.add_argument("result", help="saved Table-I extraction .npz result")
    tablei_plot.add_argument(
        "--out-dir",
        required=True,
        help="output reporting directory",
    )
    tablei_plot.add_argument(
        "--dpi",
        type=_positive_int,
        default=180,
        help="figure DPI for raster output; default is 180",
    )
    review = subparsers.add_parser(
        "plot-tablei-review-grid",
        help="plot accepted exact and Kirchhoff Table-I review-grid diagnostics",
    )
    review.add_argument("exact_result", help="accepted exact review-grid NPZ")
    review.add_argument(
        "kirchhoff_result", help="accepted Kirchhoff review-grid NPZ"
    )
    review.add_argument(
        "--out-dir", required=True, help="diagnostic output directory"
    )
    review.add_argument("--dpi", type=_positive_int, default=300)
    amplification = subparsers.add_parser(
        "compute-amplification",
        help="compute saved M5 pointwise amplification fields from a saved lensed result",
    )
    amplification.add_argument("result", help="saved lensed .npz, .h5, or .hdf5 result")
    amplification.add_argument("--out", required=True, help="output .npz, .h5, or .hdf5 path")
    tablei = subparsers.add_parser(
        "extract-tablei-four-frequency",
        help=(
            "extract Fig.5/Fig.6 Table-I four-frequency values from saved "
            "M5 amplification artifacts without recomputing physics"
        ),
    )
    tablei.add_argument(
        "results",
        nargs=4,
        help="four saved M5 amplification .npz results in kM=0.5,1.0,1.5,2.0 order",
    )
    tablei.add_argument("--out", required=True, help="output Table-I .npz path")
    tablei.add_argument(
        "--builtin-points",
        choices=["table-i", "test-small"],
        default="table-i",
        help="built-in extraction point set; default is table-i",
    )
    return parser


def _positive_int(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if value <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
