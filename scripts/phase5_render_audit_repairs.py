#!/usr/bin/env python3
"""Render the completed direct-curvature and direct-MST audit repairs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from schwgw.io.asymptotic import load_fig8_asymptotic_dataset
from schwgw.io.results import load_results
from schwgw.scattering.asymptotic import (
    parity_scattering_series,
    scattering_matrix_cross_section,
)
from schwgw.scattering.kirchhoff import compute_kirchhoff_figure_consistent
from schwgw.viz.fig4_comparison import (
    asymptotic_total_polarizations,
    render_fig4_exact_asymptotic_comparison,
)
from schwgw.viz.fig7_apparent import render_fig7_apparent_four_frequency
from schwgw.viz.fig8_asymptotic import render_fig8_asymptotic_four_frequency
from schwgw.viz.results import plot_fig3_multifrequency_panel_from_results
from schwgw.viz.tablei_uniform import render_tablei_uniform_figures


KM_VALUES = (0.5, 1.0, 1.5, 2.0)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _token(value: float) -> str:
    return f"{value:g}".replace(".", "p")


def _complex_value(value: object) -> complex:
    if isinstance(value, dict):
        return complex(float(value["real"]), float(value["imag"]))
    return complex(value)


def _fig4_asymptotic_fields(
    exact_paths: list[Path],
    *,
    mst_dataset: Path,
) -> tuple[np.ndarray, np.ndarray]:
    dataset = load_fig8_asymptotic_dataset(mst_dataset)
    plus_rows = []
    cross_rows = []
    for index, (kM, exact_path) in enumerate(zip(KM_VALUES, exact_paths, strict=True)):
        exact = load_results(exact_path)
        theta = np.asarray(exact.theta, dtype=np.float64)
        if theta.shape != (1025,) or theta[0] != 0.0:
            raise ValueError("direct Fig. 4 inputs must use the frozen 1025-point grid")
        config = exact.metadata["config"]
        wave = config["wave"]
        radius = float(config["observer"]["r"])
        mass = float(config["background"]["M"])
        series = parity_scattering_series(
            dataset.phase_factor_even[index],
            dataset.phase_factor_odd[index],
            ell=dataset.ell,
        )
        scattering = scattering_matrix_cross_section(
            theta[1:],
            series,
            k=kM / mass,
            reduction_order=2,
            target_lmax=500,
        )
        positive_plus, positive_cross = asymptotic_total_polarizations(
            theta[1:],
            k=kM / mass,
            r=radius,
            M=mass,
            M22=scattering.M22,
            M12=scattering.M12,
            A_plus=_complex_value(wave["A_plus"]),
            A_cross=_complex_value(wave["A_cross"]),
        )
        plus = np.full(theta.shape, np.nan + 1.0j * np.nan, dtype=np.complex128)
        cross = np.full_like(plus, np.nan + 1.0j * np.nan)
        plus[1:] = positive_plus
        cross[1:] = positive_cross
        plus_rows.append(plus)
        cross_rows.append(cross)
    return np.stack(plus_rows), np.stack(cross_rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--direct-dir", required=True, type=Path)
    parser.add_argument("--fig56-merged", required=True, type=Path)
    parser.add_argument("--fig8-dataset", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--dpi", type=int, default=600)
    args = parser.parse_args(argv)
    if args.output_dir.exists():
        raise FileExistsError(f"refusing render collision: {args.output_dir}")
    args.output_dir.mkdir(parents=True)

    fig3_paths = [
        args.direct_dir / f"fig3_direct_curvature_kM_{_token(value)}.npz"
        for value in KM_VALUES
    ]
    fig4_paths = [
        args.direct_dir / f"fig4_direct_curvature_kM_{_token(value)}.npz"
        for value in KM_VALUES
    ]
    fig7_paths = [
        args.direct_dir / f"fig7_direct_curvature_kM_{_token(value)}.npz"
        for value in KM_VALUES
    ]
    required = [*fig3_paths, *fig4_paths, *fig7_paths, args.fig56_merged, args.fig8_dataset]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing completed repair inputs: {missing}")

    figure3 = args.output_dir / "figure3"
    figure3.mkdir()
    plot_fig3_multifrequency_panel_from_results(
        fig3_paths,
        quantity="real",
        interpolation="bilinear",
        output_path=figure3 / "fig3_direct_curvature_bilinear_600dpi.png",
        dpi=args.dpi,
        style="publication",
        row_color_vmax={"h_plus": 7.0, "h_cross": 7.0},
    )
    plot_fig3_multifrequency_panel_from_results(
        fig3_paths,
        quantity="real",
        interpolation="nearest",
        output_path=figure3 / "fig3_direct_curvature_nearest_audit_600dpi.png",
        dpi=args.dpi,
        style="publication",
    )
    plot_fig3_multifrequency_panel_from_results(
        fig3_paths,
        quantity="real",
        interpolation="bilinear",
        output_path=figure3 / "fig3_direct_curvature.pdf",
        dpi=args.dpi,
        style="publication",
        row_color_vmax={"h_plus": 7.0, "h_cross": 7.0},
    )

    figure4 = args.output_dir / "figure4"
    asymptotic_plus, asymptotic_cross = _fig4_asymptotic_fields(
        fig4_paths,
        mst_dataset=args.fig8_dataset,
    )
    render_fig4_exact_asymptotic_comparison(
        fig4_paths,
        asymptotic_plus=asymptotic_plus,
        asymptotic_cross=asymptotic_cross,
        asymptotic_source=args.fig8_dataset,
        output_dir=figure4,
        dpi=args.dpi,
    )

    with np.load(args.fig56_merged, allow_pickle=False) as data:
        kM_values = np.asarray(data["kM_values"], dtype=float)
        radius = np.asarray(data["point_r"], dtype=float)
        theta = np.asarray(data["point_theta"], dtype=float)
    kirchhoff = compute_kirchhoff_figure_consistent(
        kM_values=kM_values,
        r_over_M=radius,
        theta=theta,
        dps=60,
    )
    render_tablei_uniform_figures(
        args.fig56_merged,
        kirchhoff_complex=kirchhoff.F_complex,
        output_dir=args.output_dir / "figure5_figure6",
        dpi=args.dpi,
        created_by_cli=True,
        scattering_description=(
            "direct RW-gauge metric -> linearized Riemann -> incident-frame "
            "electric tidal field; Eq. (45)-(46) ratios for the simultaneous "
            "fixed plus/cross incident amplitudes"
        ),
        kirchhoff_description=(
            "standard point-mass branch exp(-pi*gamma/2), gamma=-2*M*k"
        ),
        scattering_legend="direct curvature",
        kirchhoff_legend="Kirchhoff, corrected prefactor",
    )

    render_fig7_apparent_four_frequency(
        fig7_paths,
        output_dir=args.output_dir / "figure7",
        basename="fig7_direct_curvature",
        created_by_cli=True,
    )
    render_fig8_asymptotic_four_frequency(
        args.fig8_dataset,
        output_dir=args.output_dir / "figure8",
        basename="fig8_direct_mst",
        created_by_cli=True,
    )

    source_records = [
        {"path": str(path), "sha256": _sha256(path), "size": path.stat().st_size}
        for path in required
    ]
    (args.output_dir / "render_manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "schwgw_audit_repairs_render_v1",
                "figures": [3, 4, 5, 6, 7, 8],
                "sources": source_records,
                "direct_metric_curvature": True,
                "direct_high_ell_mst": True,
                "kirchhoff_standard_branch": True,
                "display_interpolation_only": True,
                "figure3_publication_display_window": {
                    "h_plus": [-7.0, 7.0],
                    "h_cross": [-7.0, 7.0],
                    "source": "published Fig. 3 color bars",
                    "scientific_arrays_modified": False,
                },
                "figure3_nearest_audit_uses_full_data_range": True,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"event": "audit_repair_figures_rendered", "output": str(args.output_dir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
