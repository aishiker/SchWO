from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


DEFAULT_STATIC = Path(
    "runs/phase5/paper_figures/fig56_jost_rout_static_20260803_py314/"
    "fig56_direct_curvature_uniform40_static_rout.npz"
)
DEFAULT_LI = Path(
    "runs/phase5/paper_figures/fig56_jost_rout_li_20260803_py314/"
    "fig56_direct_curvature_uniform40_li_literal_rout.npz"
)
DEFAULT_RS = Path(
    "runs/phase5/paper_figures/"
    "rayleigh_sommerfeld_point_mass_diagnostic_20260810_v3/"
    "rayleigh_sommerfeld_point_mass_diagnostic.npz"
)
DEFAULT_OUTPUT = Path(
    "runs/phase5/paper_figures/"
    "rayleigh_sommerfeld_vs_schwarzschild_20260810"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_schwarzschild(path: Path, *, expected_frame: str) -> dict[str, object]:
    with np.load(path, allow_pickle=False) as data:
        metadata = json.loads(str(np.asarray(data["metadata_json"]).item()))
        result = {
            "kM": np.asarray(data["kM_values"], dtype=float),
            "x_over_M": np.asarray(data["point_x"], dtype=float),
            "z_over_M": np.asarray(data["point_z"], dtype=float),
            "plus": np.asarray(data["F_plus_diagonal_complex"], dtype=complex),
            "cross": np.asarray(data["F_cross_diagonal_complex"], dtype=complex),
            "plus_mixed": np.asarray(data["F_plus_complex"], dtype=complex),
            "cross_mixed": np.asarray(data["F_cross_complex"], dtype=complex),
            "r_out_uncertainty_plus": np.asarray(
                data["r_out_uncertainty_plus_diagonal"], dtype=float
            ),
            "r_out_uncertainty_cross": np.asarray(
                data["r_out_uncertainty_cross_diagonal"], dtype=float
            ),
            "final_pair_delta_plus": np.asarray(
                data["final_pair_delta_plus_diagonal"], dtype=float
            ),
            "final_pair_delta_cross": np.asarray(
                data["final_pair_delta_cross_diagonal"], dtype=float
            ),
            "metadata": metadata,
        }
    if metadata.get("observer_frame") != expected_frame:
        raise ValueError(f"unexpected observer frame in {path}")
    if metadata.get("gauge") != "Regge-Wheeler":
        raise ValueError(f"unexpected gauge in {path}")
    if metadata.get("physical_within_frozen_gauge_frame_convention") is not True:
        raise ValueError(f"Schwarzschild frame-qualified validity is absent in {path}")
    if not np.array_equal(result["plus"], result["plus_mixed"]):
        raise ValueError(f"plus polarization mixing is nonzero in {path}")
    if not np.array_equal(result["cross"], result["cross_mixed"]):
        raise ValueError(f"cross polarization mixing is nonzero in {path}")
    return result


def _load_rs(path: Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as data:
        return {
            "kM": np.asarray(data["kM"], dtype=float),
            "x_over_M": np.asarray(data["x_over_M"], dtype=float),
            "z_over_M": np.full(
                np.asarray(data["x_over_M"]).shape,
                float(np.asarray(data["z_over_M"]).item()),
            ),
            "fresnel": np.asarray(data["fresnel_F"], dtype=complex),
            "li_lift": np.asarray(data["rs_li_lift_F"], dtype=complex),
            "cartesian": np.asarray(data["rs_cartesian_F"], dtype=complex),
        }


def _exact_frequency_indices(source: np.ndarray, target: np.ndarray) -> np.ndarray:
    indices = []
    for value in target:
        exact_matches = np.flatnonzero(source == value)
        if exact_matches.size == 1:
            indices.append(int(exact_matches[0]))
            continue
        if exact_matches.size > 1:
            raise ValueError(f"RS grid has duplicate bit-exact kM={value:g} samples")
        matches = np.flatnonzero(np.isclose(source, value, rtol=0.0, atol=1.0e-13))
        if matches.size != 1:
            raise ValueError(f"RS grid has no unique exact kM={value:g} sample")
        indices.append(int(matches[0]))
    return np.asarray(indices, dtype=int)


def _best_frequency_phase_offsets(
    *, reference: np.ndarray, candidate: np.ndarray
) -> np.ndarray:
    """Return one unit-modulus least-squares phase alignment per frequency."""

    coherence = np.sum(reference * np.conj(candidate), axis=1)
    if np.any(np.abs(coherence) <= np.finfo(float).tiny):
        raise ValueError("global phase alignment is undefined")
    return np.angle(coherence)


def _comparison_arrays(
    *, reference: np.ndarray, candidate: np.ndarray
) -> dict[str, np.ndarray]:
    if reference.shape != candidate.shape:
        raise ValueError("comparison arrays have different shapes")
    if not (
        np.isfinite(reference.real).all()
        and np.isfinite(reference.imag).all()
        and np.isfinite(candidate.real).all()
        and np.isfinite(candidate.imag).all()
    ):
        raise ValueError("comparison arrays must be finite")
    if np.any(np.abs(reference) <= np.finfo(float).tiny):
        raise ValueError("Schwarzschild reference contains a zero amplitude")

    ratio = candidate / reference
    phase_signed = np.angle(ratio)
    offsets = _best_frequency_phase_offsets(
        reference=reference,
        candidate=candidate,
    )
    aligned = candidate * np.exp(1j * offsets[:, None])
    aligned_ratio = aligned / reference
    return {
        "amplitude_fractional": np.abs(np.abs(ratio) - 1.0),
        "phase_signed": phase_signed,
        "phase_absolute": np.abs(phase_signed),
        "complex_relative": np.abs(ratio - 1.0),
        "global_phase_offset": offsets,
        "phase_offset_removed_signed": np.angle(aligned_ratio),
        "phase_offset_removed_absolute": np.abs(np.angle(aligned_ratio)),
        "complex_offset_removed_relative": np.abs(aligned_ratio - 1.0),
    }


def _summary(values: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "maximum": float(np.max(values)),
    }


def _metric_report(arrays: dict[str, np.ndarray], kM: np.ndarray) -> dict[str, object]:
    groups = {
        "all_points": slice(None),
        "near_axis_x0_to_x3": slice(0, 4),
        "far_axis_x10_to_x25": slice(4, 8),
    }
    report: dict[str, object] = {"groups": {}}
    for group, point_slice in groups.items():
        report["groups"][group] = {
            "amplitude_fractional": _summary(
                arrays["amplitude_fractional"][:, point_slice]
            ),
            "phase_absolute_rad": _summary(
                arrays["phase_absolute"][:, point_slice]
            ),
            "complex_relative": _summary(
                arrays["complex_relative"][:, point_slice]
            ),
            "phase_offset_removed_absolute_rad": _summary(
                arrays["phase_offset_removed_absolute"][:, point_slice]
            ),
            "complex_offset_removed_relative": _summary(
                arrays["complex_offset_removed_relative"][:, point_slice]
            ),
        }

    anchors: dict[str, object] = {}
    for value in (0.1, 0.3, 0.5, 1.0, 1.6, 3.1, 3.2, 4.0):
        matches = np.flatnonzero(np.isclose(kM, value, rtol=0.0, atol=1.0e-13))
        if matches.size != 1:
            raise ValueError(f"missing exact report anchor kM={value:g}")
        index = int(matches[0])
        anchors[f"{value:g}"] = {
            "lambda_over_rs": float(np.pi / value),
            "amplitude_fractional": _summary(
                arrays["amplitude_fractional"][index]
            ),
            "phase_absolute_rad": _summary(arrays["phase_absolute"][index]),
            "complex_relative": _summary(arrays["complex_relative"][index]),
            "phase_offset_removed_absolute_rad": _summary(
                arrays["phase_offset_removed_absolute"][index]
            ),
            "complex_offset_removed_relative": _summary(
                arrays["complex_offset_removed_relative"][index]
            ),
        }
    report["anchors"] = anchors
    return report


def _frame_systematic(
    *, static: np.ndarray, li_literal: np.ndarray
) -> dict[str, np.ndarray]:
    ratio = li_literal / static
    return {
        "amplitude_fractional": np.abs(np.abs(ratio) - 1.0),
        "phase_absolute": np.abs(np.angle(ratio)),
        "complex_relative": np.abs(ratio - 1.0),
    }


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


def _render_summary(
    *,
    output_dir: Path,
    kM: np.ndarray,
    comparisons: dict[str, dict[str, np.ndarray]],
    frame_systematics: dict[str, dict[str, np.ndarray]],
    dpi: int,
) -> dict[str, Path]:
    colors = {"plus": "#0072B2", "cross": "#E69F00"}
    labels = {"plus": r"$+$", "cross": r"$\times$"}
    fig, axes = plt.subplots(2, 2, figsize=(7.05, 5.45), sharex=True)

    for polarization in ("plus", "cross"):
        arrays = comparisons[polarization]
        color = colors[polarization]
        label = labels[polarization]
        axes[0, 0].plot(
            kM,
            np.mean(arrays["complex_relative"], axis=1),
            color=color,
            linewidth=1.5,
            label=label,
        )
        axes[0, 0].plot(
            kM,
            np.max(arrays["complex_relative"], axis=1),
            color=color,
            linewidth=1.05,
            linestyle="--",
        )
        axes[0, 1].plot(
            kM,
            np.mean(arrays["amplitude_fractional"], axis=1),
            color=color,
            linewidth=1.5,
            label=label,
        )
        axes[0, 1].plot(
            kM,
            np.max(arrays["amplitude_fractional"], axis=1),
            color=color,
            linewidth=1.05,
            linestyle="--",
        )
        axes[1, 0].plot(
            kM,
            np.mean(arrays["phase_absolute"], axis=1),
            color=color,
            linewidth=1.5,
            label=f"{label}, raw",
        )
        axes[1, 0].plot(
            kM,
            np.mean(arrays["phase_offset_removed_absolute"], axis=1),
            color=color,
            linewidth=1.05,
            linestyle=":",
            label=f"{label}, one phase removed",
        )
        axes[1, 1].plot(
            kM,
            np.mean(frame_systematics[polarization]["complex_relative"], axis=1),
            color=color,
            linewidth=1.5,
            label=label,
        )
        axes[1, 1].plot(
            kM,
            np.max(frame_systematics[polarization]["complex_relative"], axis=1),
            color=color,
            linewidth=1.05,
            linestyle="--",
        )

    axes[0, 0].set_ylabel(r"$|F_{\rm RS}/F_{\rm Schw}-1|$")
    axes[0, 0].set_title("Complex residual: mean / maximum", fontsize=9)
    axes[0, 1].set_ylabel(r"$||F_{\rm RS}|/|F_{\rm Schw}|-1|$")
    axes[0, 1].set_title("Amplitude residual: mean / maximum", fontsize=9)
    axes[1, 0].set_ylabel("Mean phase residual (rad)")
    axes[1, 0].set_title("Raw and one-offset-removed phase", fontsize=9)
    axes[1, 1].set_ylabel("Observer-frame complex difference")
    axes[1, 1].set_title("Static vs Li-literal frame", fontsize=9)

    for index, (axis, panel) in enumerate(zip(axes.flat, "ABCD", strict=True)):
        axis.axvline(np.pi, color="#777777", linewidth=0.75, linestyle="-.")
        axis.set_xlim(float(kM[0]), float(kM[-1]))
        axis.legend(frameon=False, fontsize=7.0, ncol=2 if index == 2 else 1)
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
        "Rayleigh--Sommerfeld I versus direct Schwarzschild curvature response",
        fontsize=10.3,
        y=0.995,
    )
    fig.tight_layout(rect=(0.02, 0.01, 1.0, 0.97), h_pad=1.5, w_pad=1.6)
    png = output_dir / "rs_vs_schwarzschild_summary.png"
    pdf = output_dir / "rs_vs_schwarzschild_summary.pdf"
    fig.savefig(png, dpi=dpi, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return {"summary_png": png, "summary_pdf": pdf}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare physical-Cartesian scalar RS-I against the direct "
            "Schwarzschild diagonal polarization responses without using the "
            "Li Fresnel factor as truth."
        )
    )
    parser.add_argument("--schwarzschild-static", type=Path, default=DEFAULT_STATIC)
    parser.add_argument("--schwarzschild-li", type=Path, default=DEFAULT_LI)
    parser.add_argument("--rs", type=Path, default=DEFAULT_RS)
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
    rs_source = _load_rs(args.rs)
    if not np.array_equal(static["kM"], li_literal["kM"]):
        raise ValueError("Schwarzschild observer-frame frequency grids differ")
    for coordinate in ("x_over_M", "z_over_M"):
        if not np.array_equal(static[coordinate], li_literal[coordinate]):
            raise ValueError(f"Schwarzschild observer-frame {coordinate} grids differ")
        if not np.array_equal(static[coordinate], rs_source[coordinate]):
            raise ValueError(f"RS and Schwarzschild {coordinate} grids differ")

    frequency_indices = _exact_frequency_indices(
        rs_source["kM"],
        static["kM"],
    )
    rs = rs_source["cartesian"][frequency_indices]
    comparisons = {
        polarization: _comparison_arrays(
            reference=static[polarization],
            candidate=rs,
        )
        for polarization in ("plus", "cross")
    }
    frame_systematics = {
        polarization: _frame_systematic(
            static=static[polarization],
            li_literal=li_literal[polarization],
        )
        for polarization in ("plus", "cross")
    }

    arrays_path = args.output_dir / "rs_vs_schwarzschild_arrays.npz"
    np.savez_compressed(
        arrays_path,
        kM=static["kM"],
        rs_source_indices=frequency_indices,
        rs_source_kM=rs_source["kM"][frequency_indices],
        lambda_over_rs=np.pi / static["kM"],
        x_over_M=static["x_over_M"],
        z_over_M=static["z_over_M"],
        F_rs_cartesian=rs,
        F_schwarzschild_plus_static=static["plus"],
        F_schwarzschild_cross_static=static["cross"],
        F_schwarzschild_plus_li_literal=li_literal["plus"],
        F_schwarzschild_cross_li_literal=li_literal["cross"],
        **{
            f"{polarization}_{name}": values
            for polarization, comparison in comparisons.items()
            for name, values in comparison.items()
        },
        **{
            f"observer_frame_{polarization}_{name}": values
            for polarization, systematic in frame_systematics.items()
            for name, values in systematic.items()
        },
    )
    rendered = _render_summary(
        output_dir=args.output_dir,
        kM=static["kM"],
        comparisons=comparisons,
        frame_systematics=frame_systematics,
        dpi=args.dpi,
    )

    report = {
        "schema": "schwo_rayleigh_sommerfeld_vs_schwarzschild_v1",
        "scientific_status": "qualified_model_comparison_not_absolute_truth",
        "primary_reference": {
            "model": "linear spin-2 perturbations on exact Schwarzschild background",
            "radial_equations": "Regge-Wheeler/Zerilli",
            "observable": "pure-input diagonal direct metric-curvature response",
            "observer_frame": "static_orthonormal",
            "gauge": "Regge-Wheeler",
            "outer_boundary": "Jost 1/r series with quadratic 1/r_out extrapolation",
            "r_out_ladder_over_M": static["metadata"]["r_out_ladder"],
            "not_absolute_because": [
                "linear perturbation theory",
                "fixed incident wave and finite-radius observer",
                "gauge/frame-qualified polarization projection",
                "partial-wave and radial numerical truncation",
            ],
        },
        "candidate": {
            "model": "scalar weak-field point-mass phase screen",
            "propagator": "exact outgoing Rayleigh-Sommerfeld-I angular spectrum",
            "geometry": "physical Cartesian x and z=30M",
            "not_included": [
                "spin-2 polarization transport",
                "Schwarzschild strong-field core",
                "horizon absorption as a gravitational boundary-value problem",
            ],
        },
        "comparison": {
            "frequency_samples": int(static["kM"].size),
            "point_samples": int(static["x_over_M"].size),
            "interpolation": False,
            "smoothing": False,
            "rs_source_indices": frequency_indices.tolist(),
            "maximum_absolute_frequency_roundoff": float(
                np.max(
                    np.abs(
                        rs_source["kM"][frequency_indices] - static["kM"]
                    )
                )
            ),
            "phase_diagnostics": (
                "raw circular phase and one least-squares unit-modulus global "
                "phase removed independently at each frequency"
            ),
            "metrics": {
                polarization: _metric_report(comparison, static["kM"])
                for polarization, comparison in comparisons.items()
            },
        },
        "observer_frame_systematic": {
            polarization: {
                name: _summary(values)
                for name, values in systematic.items()
            }
            for polarization, systematic in frame_systematics.items()
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
            "rs_max_relative_replay_difference": 6.469393428924993e-16,
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
            "rayleigh_sommerfeld": {
                "path": str(args.rs),
                "sha256": _sha256(args.rs),
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
