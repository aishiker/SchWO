from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from schwgw.scattering.kirchhoff import (
    compute_kirchhoff_eq47,
    compute_kirchhoff_figure_consistent,
)


POINT_X_OVER_M = np.asarray([0.0, 1.0, 2.0, 3.0, 10.0, 15.0, 20.0, 25.0])
POINT_Z_OVER_M = 30.0


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Render the literal positive-sign Kirchhoff result beside the "
            "figure-consistent negative-sign result for the Fig. 5/6 points."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "runs/phase5/paper_figures/"
            "kirchhoff_prefactor_sign_diagnostic_20260810_v2"
        ),
    )
    parser.add_argument("--samples", type=int, default=241)
    parser.add_argument("--dps", type=int, default=50)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.samples < 80:
        raise ValueError("--samples must be at least 80 for a smooth diagnostic.")

    args.output_dir.mkdir(parents=True, exist_ok=False)
    kM = np.linspace(0.05, 4.0, args.samples)
    radius = np.hypot(POINT_X_OVER_M, POINT_Z_OVER_M)
    theta = np.arctan2(POINT_X_OVER_M, POINT_Z_OVER_M)

    printed = compute_kirchhoff_eq47(
        kM_values=kM,
        r_over_M=radius,
        theta=theta,
        dps=args.dps,
    )
    figure_consistent = compute_kirchhoff_figure_consistent(
        kM_values=kM,
        r_over_M=radius,
        theta=theta,
        dps=args.dps,
    )

    expected_ratio = np.exp(2.0 * np.pi * kM)[:, None]
    ratio_residual = np.max(
        np.abs(
            figure_consistent.F_complex
            / printed.F_complex
            / expected_ratio
            - 1.0
        )
    )
    phase_difference = np.angle(
        figure_consistent.F_complex / printed.F_complex
    )
    max_phase_difference = np.max(np.abs(phase_difference))

    data_path = args.output_dir / "kirchhoff_prefactor_sign_diagnostic.npz"
    np.savez_compressed(
        data_path,
        kM=kM,
        x_over_M=POINT_X_OVER_M,
        z_over_M=np.asarray(POINT_Z_OVER_M),
        r_over_M=radius,
        theta=theta,
        printed_positive_F=printed.F_complex,
        printed_positive_abs_F=printed.abs_F,
        figure_consistent_negative_F=figure_consistent.F_complex,
        figure_consistent_negative_abs_F=figure_consistent.abs_F,
    )

    colors = ("#111111", "#D62728", "#1F77B4", "#2CA02C")
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 7.7), sharex=True)
    groups = (
        (slice(0, 4), "Near axis: $z/M=30$, $x/M=0,1,2,3$"),
        (slice(4, 8), "Farther from axis: $z/M=30$, $x/M=10,15,20,25$"),
    )
    columns = (
        (printed.abs_F, r"Printed Eq. (47): $e^{+\pi\gamma/2}$"),
        (
            figure_consistent.abs_F,
            r"Figure-consistent form: $e^{-\pi\gamma/2}$",
        ),
    )
    for row, (point_slice, row_label) in enumerate(groups):
        for column, (values, column_label) in enumerate(columns):
            axis = axes[row, column]
            indices = range(*point_slice.indices(POINT_X_OVER_M.size))
            for color, point_index in zip(colors, indices, strict=True):
                axis.plot(
                    kM,
                    values[:, point_index],
                    color=color,
                    linewidth=1.55,
                    label=rf"$x/M={POINT_X_OVER_M[point_index]:g}$",
                )
            axis.set_xlim(float(kM[0]), float(kM[-1]))
            axis.grid(True, color="#D8D8D8", linewidth=0.55, alpha=0.75)
            axis.tick_params(direction="in", top=True, right=True)
            if row == 0:
                axis.set_title(column_label, fontsize=12.5, pad=9)
            if column == 0:
                axis.set_ylabel(r"$|F_{\mathrm{K}}|$", fontsize=12)
            if row == 1:
                axis.set_xlabel(r"$kM$", fontsize=12)
            axis.text(
                0.025,
                0.955,
                row_label,
                transform=axis.transAxes,
                ha="left",
                va="top",
                fontsize=9.5,
                bbox={"facecolor": "white", "alpha": 0.88, "edgecolor": "none"},
            )
            axis.legend(
                loc="upper right",
                fontsize=8.3,
                frameon=True,
                framealpha=0.92,
                ncol=2,
            )

    for row in range(2):
        ymax = max(float(axes[row, 0].get_ylim()[1]), float(axes[row, 1].get_ylim()[1]))
        axes[row, 0].set_ylim(0.0, ymax)
        axes[row, 1].set_ylim(0.0, ymax)

    fig.suptitle(
        "Kirchhoff prefactor-sign diagnostic at the Li--Hou--Zhao Fig. 5/6 points",
        fontsize=13.5,
        y=0.995,
    )
    fig.text(
        0.5,
        0.012,
        r"The sign changes only the magnitude: "
        r"$F_{-}/F_{+}=e^{2\pi kM}>0$; the complex phase is identical.",
        ha="center",
        va="bottom",
        fontsize=10.5,
    )
    fig.tight_layout(rect=(0.0, 0.045, 1.0, 0.975))

    png_path = args.output_dir / "kirchhoff_prefactor_sign_diagnostic.png"
    pdf_path = args.output_dir / "kirchhoff_prefactor_sign_diagnostic.pdf"
    fig.savefig(png_path, dpi=600, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    metadata = {
        "schema": "schwo_kirchhoff_prefactor_sign_diagnostic_v1",
        "purpose": (
            "Direct comparison of the literal positive sign printed in "
            "Li--Hou--Zhao Eq. (47) with the negative sign required by the "
            "standard point-mass identity and the paper's Fig. 5/6 curves."
        ),
        "samples": args.samples,
        "dps": args.dps,
        "kM_range": [float(kM[0]), float(kM[-1])],
        "x_over_M": POINT_X_OVER_M.tolist(),
        "z_over_M": POINT_Z_OVER_M,
        "printed_entrypoint": "compute_kirchhoff_eq47",
        "figure_consistent_entrypoint": "compute_kirchhoff_figure_consistent",
        "max_complex_ratio_residual": float(ratio_residual),
        "max_phase_difference_rad": float(max_phase_difference),
        "files": {
            data_path.name: {"sha256": _sha256(data_path), "size": data_path.stat().st_size},
            png_path.name: {"sha256": _sha256(png_path), "size": png_path.stat().st_size},
            pdf_path.name: {"sha256": _sha256(pdf_path), "size": pdf_path.stat().st_size},
        },
    }
    metadata_path = args.output_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metadata, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
