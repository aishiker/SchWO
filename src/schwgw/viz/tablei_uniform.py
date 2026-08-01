"""Direct-sample Fig. 5/6 renderer for the merged uniform Table-I artifact."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


class UniformFigureError(ValueError):
    """Raised when a uniform-40 figure cannot be rendered faithfully."""


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_tablei_uniform_figures(
    merged_npz: str | Path,
    *,
    kirchhoff_complex: np.ndarray,
    output_dir: str | Path,
    dpi: int = 600,
    created_by_cli: bool = False,
) -> dict[str, Path]:
    """Render Fig.5 (near) and Fig.6 (far) from direct 40-point samples.

    The stored and displayed phase is ``np.angle``'s principal branch.  No
    unwrapping, smoothing, or interpolation is applied to any plotted curve.
    """
    if dpi <= 0:
        raise UniformFigureError("dpi must be positive")
    source = Path(merged_npz)
    if not source.is_file():
        raise UniformFigureError(f"missing merge artifact: {source}")
    with np.load(source, allow_pickle=False) as data:
        km = np.asarray(data["kM_values"], float)
        plus = np.asarray(data["F_plus_complex"], complex)
        cross = np.asarray(data["F_cross_complex"], complex)
        groups = np.asarray(data["point_group"]).astype(str)
        point_x = np.asarray(data["point_x"], float)
        point_z = np.asarray(data["point_z"], float)
        xi_ratio = np.asarray(data["paper_xi_over_xi0"], float)
    expected = np.arange(1, 41) / 10
    if (
        not np.array_equal(km, expected)
        or plus.shape != (40, 8)
        or cross.shape != (40, 8)
    ):
        raise UniformFigureError(
            "merged artifact is not a 40-by-8 uniform direct-sample grid"
        )
    if not np.array_equal(groups, np.asarray(["near_axis"] * 4 + ["far_axis"] * 4)):
        raise UniformFigureError("unexpected Table-I point grouping")
    # Rendering is deliberately read-only: the caller must evaluate Eq. (47)
    # on this exact grid before entering the visualization layer.
    kir = np.asarray(kirchhoff_complex, dtype=np.complex128)
    if kir.shape != (40, 8):
        raise UniformFigureError("Kirchhoff comparison must have shape (40, 8)")
    if not np.all(np.isfinite(kir.real) & np.isfinite(kir.imag)):
        raise UniformFigureError("Kirchhoff comparison contains non-finite values")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    names = {
        "fig5_png": out / "fig5_near_axis_uniform40.png",
        "fig5_pdf": out / "fig5_near_axis_uniform40.pdf",
        "fig5_json": out / "fig5_near_axis_uniform40.json",
        "fig6_png": out / "fig6_far_axis_uniform40.png",
        "fig6_pdf": out / "fig6_far_axis_uniform40.pdf",
        "fig6_json": out / "fig6_far_axis_uniform40.json",
    }
    if any(path.exists() for path in names.values()):
        raise UniformFigureError("refusing to overwrite a uniform figure artifact")
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    for group, indices, stem in (
        ("near_axis", range(4), "fig5"),
        ("far_axis", range(4, 8), "fig6"),
    ):
        fig, axes = plt.subplots(
            2,
            4,
            figsize=(11.7, 5.15),
            sharex=True,
            sharey="row",
            constrained_layout=True,
        )
        legend_handles = []
        for col, index in enumerate(indices):
            top, bottom = axes[0, col], axes[1, col]
            plus_line = top.plot(
                km,
                np.abs(plus[:, index]),
                color="#1111cc",
                marker="^",
                linestyle="None",
                ms=3.3,
                label=r"$+$, scattering (exact)",
            )[0]
            cross_line = top.plot(
                km,
                np.abs(cross[:, index]),
                color="#ed1c24",
                marker="^",
                linestyle="None",
                ms=3.3,
                label=r"$\times$, scattering (exact)",
            )[0]
            kirchhoff_line = top.plot(
                km,
                np.abs(kir[:, index]),
                color="black",
                linestyle="--",
                lw=1.15,
                label="Kirchhoff integral",
            )[0]
            if col == 0:
                legend_handles = [plus_line, cross_line, kirchhoff_line]
            bottom.plot(
                km,
                np.angle(plus[:, index]),
                color="#1111cc",
                marker="^",
                linestyle="None",
                ms=3.3,
            )
            bottom.plot(
                km,
                np.angle(cross[:, index]),
                color="#ed1c24",
                marker="^",
                linestyle="None",
                ms=3.3,
            )
            bottom.plot(km, np.angle(kir[:, index]), "k--", lw=1.15)
            top.text(
                0.05,
                0.87,
                rf"$(x,z)=({point_x[index]:.1f},{point_z[index]:.1f})M$",
                transform=top.transAxes,
                fontsize=8,
            )
            top.text(
                0.12,
                0.67,
                rf"$\xi/\xi_0={xi_ratio[index]:.4f}$",
                transform=top.transAxes,
                fontsize=8,
            )
            bottom.set_xlabel(r"$Mk$")
            top.set_xlim(0.0, 4.05)
            top.set_ylim(0.0, 10.0 if stem == "fig5" else 4.0)
            bottom.set_ylim(-1.25 * np.pi, 1.25 * np.pi)
            bottom.set_yticks([-np.pi, -np.pi / 2, 0.0, np.pi / 2, np.pi])
            bottom.set_yticklabels(
                [r"$-\pi$", r"$-\pi/2$", "0", r"$\pi/2$", r"$\pi$"]
            )
            top.grid(color="0.75", linewidth=0.55, alpha=0.65)
            bottom.grid(color="0.75", linewidth=0.55, alpha=0.65)
        axes[0, 0].set_ylabel(r"$|F|$")
        axes[1, 0].set_ylabel(r"$\theta_F$")
        fig.legend(
            legend_handles,
            [
                r"$+$, scattering (exact)",
                r"$\times$, scattering (exact)",
                "Kirchhoff integral",
            ],
            loc="outside upper center",
            ncol=3,
            frameon=True,
        )
        fig.savefig(names[f"{stem}_png"], dpi=dpi)
        fig.savefig(names[f"{stem}_pdf"])
        plt.close(fig)
        sidecar = {
            "schema_version": "phase5_tablei_uniform40_figures_v1",
            "figure": stem,
            "group": group,
            "source_npz": str(source),
            "source_sha256": _sha(source),
            "dpi": dpi,
            "kirchhoff": (
                "caller-supplied Eq. (47) values evaluated at the identical "
                "40-by-8 grid; renderer performs no scattering computation"
            ),
            "no_interpolation": True,
            "no_smoothing": True,
            "phase": "principal raw phase (np.angle); no display unwrap",
            "created_by_cli": created_by_cli,
        }
        names[f"{stem}_json"].write_text(
            json.dumps(sidecar, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return names


__all__ = ["UniformFigureError", "render_tablei_uniform_figures"]
