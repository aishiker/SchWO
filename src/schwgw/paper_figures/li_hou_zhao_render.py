"""Journal-quality renderers for Li-Hou-Zhao Figures 1 and 2.

Fig. 2 output is deliberately labelled as a stable recomputation.  The
published raster can be embedded in a separate comparison figure, but is
never represented as computed data.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import numpy as np

from schwgw.paper_figures.li_hou_zhao import Figure1Dataset, Figure2Dataset


RenderStyle = Literal["paper", "journal", "accessible"]
SectorName = Literal["odd", "even"]

_RC = {
    "axes.linewidth": 0.65,
    "font.family": "serif",
    "font.size": 7.0,
    "legend.fontsize": 6.2,
    "lines.linewidth": 0.9,
    "mathtext.fontset": "dejavuserif",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "savefig.transparent": False,
    "svg.fonttype": "none",
    "xtick.direction": "in",
    "xtick.major.size": 2.5,
    "xtick.major.width": 0.55,
    "ytick.direction": "in",
    "ytick.major.size": 2.5,
    "ytick.major.width": 0.55,
}


def build_figure1_figure(
    dataset: Figure1Dataset,
    *,
    sector: SectorName = "odd",
    style: RenderStyle = "journal",
) -> Figure:
    if sector not in {"odd", "even"}:
        raise ValueError("sector must be 'odd' or 'even'.")
    if style not in {"paper", "journal"}:
        raise ValueError("Fig. 1 style must be 'paper' or 'journal'.")
    exact = getattr(dataset, f"exact_{sector}")
    asymptotic = getattr(dataset, f"asymptotic_{sector}")
    with plt.rc_context(_RC):
        figure, axes = plt.subplots(
            2,
            4,
            figsize=(7.08, 3.35),
            sharex=True,
            sharey=True,
        )
        red = "#E41A1C"
        blue = "#315BFF"
        for index, (axis, ell) in enumerate(zip(axes.flat, dataset.ell_values, strict=True)):
            axis.plot(dataset.r, exact[index].real, color=red, linestyle="-")
            axis.plot(dataset.r, exact[index].imag, color=red, linestyle="--")
            axis.plot(dataset.r, asymptotic[index].real, color=blue, linestyle="-")
            axis.plot(dataset.r, asymptotic[index].imag, color=blue, linestyle="--")
            axis.text(
                0.07,
                0.88,
                rf"$\ell={int(ell)}$",
                transform=axis.transAxes,
                fontsize=8.0,
                ha="left",
                va="top",
            )
            axis.set_xlim(6.0, 66.0)
            axis.set_ylim(-3.65, 3.65)
            axis.set_xticks((10, 20, 30, 40, 50, 60))
            axis.set_yticks((-3, -2, -1, 0, 1, 2, 3))
            if style == "paper":
                axis.grid(True, color="0.82", linewidth=0.4, alpha=0.72)
            else:
                axis.grid(True, color="0.88", linewidth=0.35, alpha=0.55)
            axis.tick_params(top=True, right=True)
        for axis in axes[1, :]:
            axis.set_xlabel(r"$r/M$", fontsize=8.2)
        sector_symbol = "-" if sector == "odd" else "+"
        axes[0, 0].set_ylabel(rf"$\widehat{{u}}_\ell^{{({sector_symbol})}}(k,r)$", fontsize=8.2)
        axes[1, 0].set_ylabel(rf"$\widehat{{u}}_\ell^{{({sector_symbol})}}(k,r)$", fontsize=8.2)

        exact_handles = (
            Line2D([], [], color=red, linestyle="-", label="Real, exact"),
            Line2D([], [], color=red, linestyle="--", label="Imag, exact"),
        )
        asymptotic_handles = (
            Line2D([], [], color=blue, linestyle="-", label="Real, asymptotic"),
            Line2D([], [], color=blue, linestyle="--", label="Imag, asymptotic"),
        )
        axes[0, 1].legend(handles=exact_handles, loc="lower right", frameon=True)
        axes[0, 2].legend(handles=asymptotic_handles, loc="lower right", frameon=True)
        figure.subplots_adjust(left=0.075, right=0.995, bottom=0.14, top=0.99, wspace=0.025, hspace=0.065)
    return figure


def build_figure2_figure(
    dataset: Figure2Dataset,
    *,
    style: RenderStyle = "paper",
) -> Figure:
    if style not in {"paper", "accessible"}:
        raise ValueError("Fig. 2 style must be 'paper' or 'accessible'.")
    if dataset.kM_values.size != 4 or dataset.theta_values.size != 4:
        raise ValueError("Fig. 2 renderer requires the frozen 4x4 coordinate grid.")
    paper_colors = ("#FF2A2A", "#315BFF", "#2CA02C", "#FF9900")
    accessible_colors = ("#000000", "#0072B2", "#009E73", "#D55E00")
    colors = paper_colors if style == "paper" else accessible_colors
    linestyles = ("-", "-", "-", "-") if style == "paper" else ("-", "--", "-.", ":")
    labels = (r"$\theta=0$", r"$\theta=\pi/6$", r"$\theta=\pi/3$", r"$\theta=\pi/2$")
    with plt.rc_context(_RC):
        figure, axes = plt.subplots(2, 2, figsize=(7.08, 4.25), sharex=True)
        for frequency_index, (axis, kM) in enumerate(
            zip(axes.flat, dataset.kM_values, strict=True)
        ):
            for theta_index, (color, linestyle, label) in enumerate(
                zip(colors, linestyles, labels, strict=True)
            ):
                axis.plot(
                    dataset.lmax_values,
                    dataset.log10_abs_psi4[frequency_index, theta_index],
                    color=color,
                    linestyle=linestyle,
                    label=label,
                )
            axis.set_xlim(2, 180)
            axis.set_xticks((30, 60, 90, 120, 150, 180))
            axis.margins(y=0.09)
            axis.grid(True, color="0.87", linewidth=0.35, alpha=0.6)
            axis.tick_params(top=True, right=True)
            axis.text(
                0.10,
                0.11,
                rf"$k={float(kM):g}/M$",
                transform=axis.transAxes,
                fontsize=7.5,
                ha="left",
                va="bottom",
            )
        axes[0, 1].legend(loc="lower right", frameon=True, ncol=2)
        axes[1, 0].set_xlabel(r"$L$", fontsize=8.2)
        axes[1, 1].set_xlabel(r"$L$", fontsize=8.2)
        axes[0, 0].set_ylabel(r"$\log_{10}|\widetilde{\Psi}_4(L)|$", fontsize=8.0)
        axes[1, 0].set_ylabel(r"$\log_{10}|\widetilde{\Psi}_4(L)|$", fontsize=8.0)
        figure.subplots_adjust(left=0.085, right=0.995, bottom=0.115, top=0.99, wspace=0.10, hspace=0.055)
    return figure


def build_figure2_reference_comparison(
    dataset: Figure2Dataset,
    paper_reference_image: str | Path,
) -> Figure:
    """Place the published raster above the stable Eq. (34) recomputation.

    The top panel is explicitly an image reference.  It is not digitized,
    resampled into, or otherwise substituted for the computed arrays.
    """

    reference_path = Path(paper_reference_image)
    if not reference_path.is_file():
        raise FileNotFoundError(reference_path)
    if dataset.kM_values.size != 4 or dataset.theta_values.size != 4:
        raise ValueError("Fig. 2 comparison requires the frozen 4x4 grid.")

    colors = ("#FF2A2A", "#315BFF", "#2CA02C", "#FF9900")
    labels = (r"$\theta=0$", r"$\theta=\pi/6$", r"$\theta=\pi/3$", r"$\theta=\pi/2$")
    with plt.rc_context(_RC):
        figure = plt.figure(figsize=(7.08, 6.65))
        grid = figure.add_gridspec(
            3,
            2,
            height_ratios=(1.20, 1.0, 1.0),
            left=0.085,
            right=0.995,
            bottom=0.075,
            top=0.965,
            wspace=0.10,
            hspace=0.21,
        )
        reference_axis = figure.add_subplot(grid[0, :])
        reference_axis.imshow(mpimg.imread(reference_path), interpolation="none")
        reference_axis.set_axis_off()
        reference_axis.set_title(
            "(a) Published Fig. 2 raster (reference only)",
            fontsize=8.2,
            loc="left",
            pad=3.0,
        )

        axes = np.asarray(
            [
                figure.add_subplot(grid[1, 0]),
                figure.add_subplot(grid[1, 1]),
                figure.add_subplot(grid[2, 0]),
                figure.add_subplot(grid[2, 1]),
            ],
            dtype=object,
        ).reshape(2, 2)
        for frequency_index, (axis, kM) in enumerate(
            zip(axes.flat, dataset.kM_values, strict=True)
        ):
            for theta_index, (color, label) in enumerate(zip(colors, labels, strict=True)):
                axis.plot(
                    dataset.lmax_values,
                    dataset.log10_abs_psi4[frequency_index, theta_index],
                    color=color,
                    label=label,
                )
            axis.set_xlim(2, 180)
            axis.set_xticks((30, 60, 90, 120, 150, 180))
            axis.margins(y=0.09)
            axis.grid(True, color="0.87", linewidth=0.35, alpha=0.6)
            axis.tick_params(top=True, right=True)
            axis.text(
                0.10,
                0.11,
                rf"$k={float(kM):g}/M$",
                transform=axis.transAxes,
                fontsize=7.5,
                ha="left",
                va="bottom",
            )
        axes[0, 1].legend(loc="lower right", frameon=True, ncol=2)
        axes[1, 0].set_xlabel(r"$L$", fontsize=8.2)
        axes[1, 1].set_xlabel(r"$L$", fontsize=8.2)
        axes[0, 0].set_ylabel(r"$\log_{10}|\widetilde{\Psi}_4(L)|$", fontsize=8.0)
        axes[1, 0].set_ylabel(r"$\log_{10}|\widetilde{\Psi}_4(L)|$", fontsize=8.0)
        figure.text(
            0.085,
            0.646,
            "(b) Stable finite-radius recomputation of Eq. (34)",
            fontsize=8.2,
            ha="left",
            va="bottom",
        )
    return figure


def render_figure1_set(dataset: Figure1Dataset, output_dir: str | Path) -> list[Path]:
    output = Path(output_dir)
    outputs: list[Path] = []
    for sector, style, stem in (
        ("odd", "journal", "fig1_odd_primary_journal"),
        ("odd", "paper", "fig1_odd_paper_faithful"),
        ("even", "journal", "fig1_even_candidate_journal"),
    ):
        figure = build_figure1_figure(dataset, sector=sector, style=style)
        outputs.extend(_save_formats(figure, output, stem))
        plt.close(figure)
    return outputs


def render_figure2_set(dataset: Figure2Dataset, output_dir: str | Path) -> list[Path]:
    output = Path(output_dir)
    outputs: list[Path] = []
    for style, stem in (
        ("paper", "fig2_strict_psi4_stable_recomputation"),
        ("accessible", "fig2_strict_psi4_stable_accessible"),
    ):
        figure = build_figure2_figure(dataset, style=style)
        outputs.extend(_save_formats(figure, output, stem))
        plt.close(figure)
    return outputs


def render_figure2_reference_comparison(
    dataset: Figure2Dataset,
    paper_reference_image: str | Path,
    output_dir: str | Path,
) -> list[Path]:
    figure = build_figure2_reference_comparison(dataset, paper_reference_image)
    try:
        return _save_formats(
            figure,
            Path(output_dir),
            "fig2_published_vs_stable_recomputation",
        )
    finally:
        plt.close(figure)


def _save_formats(figure: Figure, output: Path, stem: str) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    paths = [output / f"{stem}.{suffix}" for suffix in ("pdf", "svg", "png")]
    with plt.rc_context(_RC):
        for path in paths:
            if path.exists():
                raise FileExistsError(path)
            temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp{path.suffix}")
            if temporary.exists():
                raise FileExistsError(temporary)
            metadata = {"Creator": "schw-gw-waveoptics"}
            if path.suffix == ".pdf":
                metadata.update({"CreationDate": None, "ModDate": None})
            figure.savefig(
                temporary,
                dpi=600 if path.suffix == ".png" else None,
                format=path.suffix.removeprefix("."),
                bbox_inches="tight",
                metadata=metadata,
            )
            if path.exists():
                temporary.unlink(missing_ok=True)
                raise FileExistsError(path)
            os.replace(temporary, path)
    return paths


__all__ = [
    "build_figure1_figure",
    "build_figure2_figure",
    "build_figure2_reference_comparison",
    "render_figure1_set",
    "render_figure2_reference_comparison",
    "render_figure2_set",
]
