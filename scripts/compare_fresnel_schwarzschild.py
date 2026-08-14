from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from compare_rayleigh_sommerfeld_schwarzschild import (
    DEFAULT_LI,
    DEFAULT_RS,
    DEFAULT_STATIC,
    _comparison_arrays,
    _exact_frequency_indices,
    _frame_systematic,
    _load_rs,
    _load_schwarzschild,
    _metric_report,
    _summary,
)


DEFAULT_OUTPUT = Path(
    "runs/phase5/paper_figures/fresnel_vs_schwarzschild_20260810_v2"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _style_axis(axis, *, panel: str) -> None:
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.tick_params(direction="out", length=3.5, width=0.8)
    axis.text(
        -0.13,
        1.04,
        f"({panel})",
        transform=axis.transAxes,
        ha="left",
        va="bottom",
        fontsize=10,
        fontweight="bold",
    )


def _mean_over_polarizations(
    comparisons: dict[str, dict[str, dict[str, np.ndarray]]],
    *,
    candidate: str,
    metric: str,
) -> np.ndarray:
    return np.mean(
        np.stack(
            [
                comparisons[candidate][polarization][metric]
                for polarization in ("plus", "cross")
            ]
        ),
        axis=(0, 2),
    )


def _render_summary(
    *,
    output_dir: Path,
    kM: np.ndarray,
    comparisons: dict[str, dict[str, dict[str, np.ndarray]]],
    dpi: int,
) -> dict[str, Path]:
    colors = {"fresnel": "#CC79A7", "rs": "#0072B2"}
    labels = {"fresnel": "Fresnel", "rs": "RS-I"}
    fig, axes = plt.subplots(2, 2, figsize=(7.05, 5.45), sharex=True)

    for column, polarization in enumerate(("plus", "cross")):
        axis = axes[0, column]
        polarization_symbol = "+" if polarization == "plus" else r"\times"
        for candidate in ("fresnel", "rs"):
            arrays = comparisons[candidate][polarization]
            axis.plot(
                kM,
                np.mean(arrays["complex_relative"], axis=1),
                color=colors[candidate],
                linewidth=1.5,
                label=f"{labels[candidate]}, raw",
            )
            axis.plot(
                kM,
                np.mean(arrays["complex_offset_removed_relative"], axis=1),
                color=colors[candidate],
                linewidth=1.15,
                linestyle=":",
                label=f"{labels[candidate]}, aligned",
            )
        axis.set_ylabel("Mean complex residual")
        axis.set_title(
            rf"$F_{{{polarization_symbol}}}$ response",
            fontsize=9,
        )
        axis.legend(
            frameon=False,
            fontsize=6.5,
            ncol=2,
            handlelength=1.6,
            columnspacing=0.65,
            loc="upper left",
        )

    for candidate in ("fresnel", "rs"):
        axes[1, 0].plot(
            kM,
            _mean_over_polarizations(
                comparisons,
                candidate=candidate,
                metric="amplitude_fractional",
            ),
            color=colors[candidate],
            linewidth=1.5,
            label=labels[candidate],
        )
        axes[1, 1].plot(
            kM,
            _mean_over_polarizations(
                comparisons,
                candidate=candidate,
                metric="phase_absolute",
            ),
            color=colors[candidate],
            linewidth=1.5,
            label=f"{labels[candidate]}, raw",
        )
        axes[1, 1].plot(
            kM,
            _mean_over_polarizations(
                comparisons,
                candidate=candidate,
                metric="phase_offset_removed_absolute",
            ),
            color=colors[candidate],
            linewidth=1.15,
            linestyle=":",
            label=f"{labels[candidate]}, aligned",
        )

    axes[1, 0].set_ylabel("Mean amplitude residual")
    axes[1, 0].set_title("Both polarizations and all eight points", fontsize=9)
    axes[1, 0].legend(frameon=False, fontsize=7.0)
    axes[1, 1].set_ylabel("Mean phase residual (rad)")
    axes[1, 1].set_title("Raw and one-offset-removed phase", fontsize=9)
    axes[1, 1].legend(
        frameon=False,
        fontsize=6.5,
        ncol=2,
        handlelength=1.6,
        columnspacing=0.65,
        loc="upper left",
    )

    for axis, panel in zip(axes.flat, "ABCD", strict=True):
        axis.axvline(np.pi, color="#777777", linewidth=0.75, linestyle="-.")
        axis.set_xlim(float(kM[0]), float(kM[-1]))
        _style_axis(axis, panel=panel)
    axes[1, 0].set_xlabel(r"$kM$")
    axes[1, 1].set_xlabel(r"$kM$")
    axes[0, 0].annotate(
        r"$\lambda=r_s$",
        xy=(np.pi, 0.98),
        xycoords=("data", "axes fraction"),
        xytext=(4, -2),
        textcoords="offset points",
        fontsize=7,
        va="top",
    )
    fig.suptitle(
        "Point-mass Fresnel and RS-I responses versus Schwarzschild",
        fontsize=10.3,
        y=0.995,
    )
    fig.tight_layout(rect=(0.02, 0.01, 1.0, 0.97), h_pad=1.5, w_pad=1.6)
    png = output_dir / "fresnel_rs_vs_schwarzschild_summary.png"
    pdf = output_dir / "fresnel_rs_vs_schwarzschild_summary.pdf"
    fig.savefig(png, dpi=dpi, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return {"summary_png": png, "summary_pdf": pdf}


def _paired_anchor_report(
    *,
    comparisons: dict[str, dict[str, dict[str, np.ndarray]]],
    kM: np.ndarray,
) -> dict[str, object]:
    report: dict[str, object] = {}
    for value in (0.1, 0.3, 0.5, 1.0, 1.6, 3.1, 3.2, 4.0):
        matches = np.flatnonzero(np.isclose(kM, value, rtol=0.0, atol=1.0e-13))
        if matches.size != 1:
            raise ValueError(f"missing exact report anchor kM={value:g}")
        index = int(matches[0])
        entry: dict[str, object] = {"lambda_over_rs": float(np.pi / value)}
        for candidate in ("fresnel", "rs"):
            entry[candidate] = {
                polarization: {
                    "mean_complex_relative": float(
                        np.mean(
                            comparisons[candidate][polarization][
                                "complex_relative"
                            ][index]
                        )
                    ),
                    "maximum_complex_relative": float(
                        np.max(
                            comparisons[candidate][polarization][
                                "complex_relative"
                            ][index]
                        )
                    ),
                    "mean_complex_offset_removed_relative": float(
                        np.mean(
                            comparisons[candidate][polarization][
                                "complex_offset_removed_relative"
                            ][index]
                        )
                    ),
                }
                for polarization in ("plus", "cross")
            }
        report[f"{value:g}"] = entry
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare the standard point-mass Fresnel factor against direct "
            "Schwarzschild polarization responses and retain RS-I as a "
            "secondary model comparison."
        )
    )
    parser.add_argument("--schwarzschild-static", type=Path, default=DEFAULT_STATIC)
    parser.add_argument("--schwarzschild-li", type=Path, default=DEFAULT_LI)
    parser.add_argument("--optics", type=Path, default=DEFAULT_RS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dpi", type=int, default=600)
    args = parser.parse_args()
    if args.output_dir.exists():
        if any(args.output_dir.iterdir()):
            raise FileExistsError(f"nonempty output directory: {args.output_dir}")
    else:
        args.output_dir.mkdir(parents=True, exist_ok=False)

    static = _load_schwarzschild(
        args.schwarzschild_static,
        expected_frame="static_orthonormal",
    )
    li_literal = _load_schwarzschild(
        args.schwarzschild_li,
        expected_frame="li_literal_cartesian",
    )
    optics = _load_rs(args.optics)
    if not np.array_equal(static["kM"], li_literal["kM"]):
        raise ValueError("Schwarzschild observer-frame frequency grids differ")
    for coordinate in ("x_over_M", "z_over_M"):
        if not np.array_equal(static[coordinate], li_literal[coordinate]):
            raise ValueError(f"Schwarzschild observer-frame {coordinate} grids differ")
        if not np.array_equal(static[coordinate], optics[coordinate]):
            raise ValueError(f"optical and Schwarzschild {coordinate} grids differ")

    indices = _exact_frequency_indices(optics["kM"], static["kM"])
    candidates = {
        "fresnel": optics["fresnel"][indices],
        "rs": optics["cartesian"][indices],
    }
    comparisons = {
        candidate: {
            polarization: _comparison_arrays(
                reference=static[polarization],
                candidate=values,
            )
            for polarization in ("plus", "cross")
        }
        for candidate, values in candidates.items()
    }

    arrays_path = args.output_dir / "fresnel_vs_schwarzschild_arrays.npz"
    np.savez_compressed(
        arrays_path,
        kM=static["kM"],
        optics_source_indices=indices,
        optics_source_kM=optics["kM"][indices],
        lambda_over_rs=np.pi / static["kM"],
        x_over_M=static["x_over_M"],
        z_over_M=static["z_over_M"],
        F_fresnel=candidates["fresnel"],
        F_rs_cartesian=candidates["rs"],
        F_schwarzschild_plus_static=static["plus"],
        F_schwarzschild_cross_static=static["cross"],
        **{
            f"{candidate}_{polarization}_{name}": values
            for candidate, by_polarization in comparisons.items()
            for polarization, metrics in by_polarization.items()
            for name, values in metrics.items()
        },
    )
    rendered = _render_summary(
        output_dir=args.output_dir,
        kM=static["kM"],
        comparisons=comparisons,
        dpi=args.dpi,
    )

    frame_systematics = {
        polarization: _frame_systematic(
            static=static[polarization],
            li_literal=li_literal[polarization],
        )
        for polarization in ("plus", "cross")
    }
    report = {
        "schema": "schwo_fresnel_vs_schwarzschild_v1",
        "scientific_status": "qualified_model_comparison_not_absolute_truth",
        "fresnel_definition": {
            "model": "standard scalar point-mass Fresnel diffraction factor",
            "gamma": "-2Mk",
            "prefactor": "exp(-pi*gamma/2)",
            "coordinate": "eta=0.5*sqrt(r/M)*tan(theta)",
            "paper_note": (
                "figure-consistent sign, not the inconsistent literal plus "
                "sign printed in Li-Hou-Zhao v1 Eq. (47)"
            ),
            "polarization_independent": True,
        },
        "schwarzschild_reference": {
            "model": "linear spin-2 perturbations on exact Schwarzschild background",
            "observable": "pure-input diagonal direct metric-curvature response",
            "gauge": "Regge-Wheeler",
            "observer_frame": "static_orthonormal",
            "absolute_truth": False,
        },
        "sampling": {
            "frequency_count": int(static["kM"].size),
            "point_count": int(static["x_over_M"].size),
            "interpolation": False,
            "smoothing": False,
            "maximum_absolute_frequency_roundoff": float(
                np.max(np.abs(optics["kM"][indices] - static["kM"]))
            ),
        },
        "metrics": {
            candidate: {
                polarization: _metric_report(metrics, static["kM"])
                for polarization, metrics in by_polarization.items()
            }
            for candidate, by_polarization in comparisons.items()
        },
        "paired_anchors": _paired_anchor_report(
            comparisons=comparisons,
            kM=static["kM"],
        ),
        "observer_frame_systematic": {
            polarization: {
                name: _summary(values) for name, values in metrics.items()
            }
            for polarization, metrics in frame_systematics.items()
        },
        "numerical_convergence": {
            "schwarzschild_max_r_out_uncertainty": float(
                max(
                    np.max(static["r_out_uncertainty_plus"]),
                    np.max(static["r_out_uncertainty_cross"]),
                )
            ),
            "schwarzschild_max_final_pair_delta": float(
                max(
                    np.max(static["final_pair_delta_plus"]),
                    np.max(static["final_pair_delta_cross"]),
                )
            ),
        },
        "inputs": {
            "schwarzschild_static": {
                "path": str(args.schwarzschild_static),
                "sha256": _sha256(args.schwarzschild_static),
            },
            "schwarzschild_li_literal": {
                "path": str(args.schwarzschild_li),
                "sha256": _sha256(args.schwarzschild_li),
            },
            "optics": {
                "path": str(args.optics),
                "sha256": _sha256(args.optics),
            },
        },
        "outputs": {
            "arrays": {
                "path": str(arrays_path),
                "sha256": _sha256(arrays_path),
                "size": arrays_path.stat().st_size,
            },
            **{
                name: {
                    "path": str(path),
                    "sha256": _sha256(path),
                    "size": path.stat().st_size,
                }
                for name, path in rendered.items()
            },
        },
    }
    report_path = args.output_dir / "comparison_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
