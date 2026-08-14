from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


PANEL_X_BOUNDS = ((266, 574), (580, 888), (894, 1202), (1208, 1516))
K_VALUES = np.arange(0.1, 4.01, 0.1)


def _finite_mean(values: np.ndarray) -> float | None:
    finite = np.asarray(values)[np.isfinite(values)]
    return float(np.mean(finite)) if finite.size else None


def _finite_rmse(values: np.ndarray) -> float | None:
    finite = np.asarray(values)[np.isfinite(values)]
    return float(np.sqrt(np.mean(finite**2))) if finite.size else None


def _red_marker_mask(image: np.ndarray) -> np.ndarray:
    return (
        (image[:, :, 0] > 180)
        & (image[:, :, 0] > image[:, :, 1] * 1.45)
        & (image[:, :, 0] > image[:, :, 2] * 1.35)
        & (image[:, :, 1] < 160)
    )


def _blue_marker_mask(image: np.ndarray) -> np.ndarray:
    """Select the anti-aliased blue remnants visible below red triangles."""

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
            y_hits = np.empty(0, dtype=int)
            for radius in (3, 4, 5):
                lo = max(x0, int(round(x)) - radius)
                hi = min(x1 + 1, int(round(x)) + radius + 1)
                y_hits, _ = np.where(mask[y0 : y1 + 1, lo:hi])
                if y_hits.size:
                    break
            if y_hits.size:
                y = float(np.median(y_hits + y0))
                values[row, panel] = y_limits[0] + (y - y0) / (y1 - y0) * (
                    y_limits[1] - y_limits[0]
                )
    return values


def _metrics(
    path: Path,
    *,
    original_abs: np.ndarray,
    original_arg: np.ndarray,
    suffix: str = "",
) -> dict[str, object]:
    with np.load(path, allow_pickle=False) as data:
        cross_abs = np.asarray(data[f"abs_F_cross{suffix}"])
        cross_arg = np.asarray(data[f"arg_F_cross{suffix}_principal"])
        plus_abs = np.asarray(data[f"abs_F_plus{suffix}"])
        plus_arg = np.asarray(data[f"arg_F_plus{suffix}_principal"])
    cross_amplitude_error = np.abs(cross_abs - original_abs)
    cross_phase_error = np.abs(
        np.angle(np.exp(1.0j * (cross_arg - original_arg)))
    )
    plus_amplitude_error = np.abs(plus_abs - original_abs)
    plus_phase_error = np.abs(
        np.angle(np.exp(1.0j * (plus_arg - original_arg)))
    )
    return {
        "published_amplitude_sample_count": int(np.isfinite(original_abs).sum()),
        "published_phase_sample_count": int(np.isfinite(original_arg).sum()),
        "amplitude_mae_all": _finite_mean(cross_amplitude_error),
        "amplitude_rmse_all": _finite_rmse(cross_amplitude_error),
        "phase_circular_mae_rad_all": _finite_mean(cross_phase_error),
        "phase_circular_rmse_rad_all": _finite_rmse(cross_phase_error),
        "plus_amplitude_mae_to_same_published_markers": _finite_mean(
            plus_amplitude_error
        ),
        "plus_phase_circular_mae_rad_to_same_published_markers": _finite_mean(
            plus_phase_error
        ),
        "amplitude_mae_by_panel": [
            _finite_mean(cross_amplitude_error[:, panel])
            for panel in range(8)
        ],
        "phase_circular_mae_by_panel_rad": [
            _finite_mean(cross_phase_error[:, panel])
            for panel in range(8)
        ],
        "max_plus_cross_abs_magnitude_difference": float(
            np.max(np.abs(plus_abs - cross_abs))
        ),
        "median_plus_cross_abs_magnitude_difference": float(
            np.median(np.abs(plus_abs - cross_abs))
        ),
        "max_plus_cross_circular_phase_difference_rad": float(
            np.max(np.abs(np.angle(np.exp(1.0j * (plus_arg - cross_arg)))))
        ),
    }


def _comparison_figure(
    *,
    original: np.ndarray,
    corrected_path: Path,
    crop: tuple[int, int, int, int],
    title: str,
    output: Path,
    dpi: int,
) -> None:
    x0, y0, x1, y1 = crop
    corrected = np.asarray(Image.open(corrected_path).convert("RGB"))
    figure, axes = plt.subplots(2, 1, figsize=(12, 7.1), constrained_layout=True)
    axes[0].imshow(original[y0:y1, x0:x1])
    axes[0].set_title(f"{title}: published raster")
    axes[1].imshow(corrected)
    axes[1].set_title(f"{title}: corrected reconstruction")
    for axis in axes:
        axis.set_axis_off()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=dpi, bbox_inches="tight")
    plt.close(figure)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper-page", type=Path, required=True)
    parser.add_argument("--old-merged", type=Path, required=True)
    parser.add_argument("--corrected-merged", type=Path, required=True)
    parser.add_argument("--corrected-figure-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()

    original = np.asarray(Image.open(args.paper_page).convert("RGB"))
    if original.shape != (2200, 1700, 3):
        raise ValueError("comparison is calibrated to the frozen 1700x2200 page raster")
    mask = _red_marker_mask(original)
    blue_mask = _blue_marker_mask(original)
    original_abs = np.concatenate(
        (
            _extract_markers(mask, y_bounds=(215, 474), y_limits=(10.0, 0.0)),
            _extract_markers(mask, y_bounds=(1014, 1273), y_limits=(4.0, 0.0)),
        ),
        axis=1,
    )
    original_arg = np.concatenate(
        (
            _extract_markers(
                mask,
                y_bounds=(487, 746),
                y_limits=(1.25 * np.pi, -1.25 * np.pi),
            ),
            _extract_markers(
                mask,
                y_bounds=(1286, 1545),
                y_limits=(1.25 * np.pi, -1.25 * np.pi),
            ),
        ),
        axis=1,
    )
    original_blue_abs = np.concatenate(
        (
            _extract_markers(
                blue_mask, y_bounds=(215, 474), y_limits=(10.0, 0.0)
            ),
            _extract_markers(
                blue_mask, y_bounds=(1014, 1273), y_limits=(4.0, 0.0)
            ),
        ),
        axis=1,
    )
    original_blue_arg = np.concatenate(
        (
            _extract_markers(
                blue_mask,
                y_bounds=(487, 746),
                y_limits=(1.25 * np.pi, -1.25 * np.pi),
            ),
            _extract_markers(
                blue_mask,
                y_bounds=(1286, 1545),
                y_limits=(1.25 * np.pi, -1.25 * np.pi),
            ),
        ),
        axis=1,
    )
    amplitude_overlap = np.isfinite(original_abs) & np.isfinite(original_blue_abs)
    phase_overlap = np.isfinite(original_arg) & np.isfinite(original_blue_arg)
    report = {
        "digitization": {
            "source": str(args.paper_page),
            "red_amplitude_samples": int(np.isfinite(original_abs).sum()),
            "red_phase_samples": int(np.isfinite(original_arg).sum()),
            "blue_amplitude_samples": int(np.isfinite(original_blue_abs).sum()),
            "blue_phase_samples": int(np.isfinite(original_blue_arg).sum()),
            "red_blue_overlap": {
                "amplitude_samples": int(amplitude_overlap.sum()),
                "phase_samples": int(phase_overlap.sum()),
                "amplitude_median_abs_delta": (
                    float(
                        np.median(
                            np.abs(
                                original_abs[amplitude_overlap]
                                - original_blue_abs[amplitude_overlap]
                            )
                        )
                    )
                    if np.any(amplitude_overlap)
                    else None
                ),
                "phase_median_circular_delta_rad": (
                    float(
                        np.median(
                            np.abs(
                                np.angle(
                                    np.exp(
                                        1.0j
                                        * (
                                            original_arg[phase_overlap]
                                            - original_blue_arg[phase_overlap]
                                        )
                                    )
                                )
                            )
                        )
                    )
                    if np.any(phase_overlap)
                    else None
                ),
            },
            "estimated_vertical_resolution": {
                "fig5_abs": 10.0 / 259.0,
                "fig6_abs": 4.0 / 259.0,
                "phase_rad": 2.5 * np.pi / 259.0,
            },
            "status": "raster-level diagnostic, not source-data ground truth",
        },
        "old_route_b": _metrics(
            args.old_merged,
            original_abs=original_abs,
            original_arg=original_arg,
        ),
        "direct_metric_curvature_eq45_simultaneous_response": _metrics(
            args.corrected_merged,
            original_abs=original_abs,
            original_arg=original_arg,
        ),
        "direct_metric_curvature_pure_input_diagonal_diagnostic": _metrics(
            args.corrected_merged,
            original_abs=original_abs,
            original_arg=original_arg,
            suffix="_diagonal",
        ),
        "published_blue_remnant_comparison": {
            "old_route_b": _metrics(
                args.old_merged,
                original_abs=original_blue_abs,
                original_arg=original_blue_arg,
            ),
            "direct_metric_curvature_eq45_simultaneous_response": _metrics(
                args.corrected_merged,
                original_abs=original_blue_abs,
                original_arg=original_blue_arg,
            ),
            "caution": (
                "blue samples are sparse anti-aliased remnants because the "
                "published red triangles overplot nearly coincident blue triangles"
            ),
        },
    }
    if args.output_dir.exists():
        raise FileExistsError(f"refusing comparison collision: {args.output_dir}")
    args.output_dir.mkdir(parents=True)
    (args.output_dir / "original_raster_comparison.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    _comparison_figure(
        original=original,
        corrected_path=args.corrected_figure_dir / "fig5_near_axis_uniform40.png",
        crop=(130, 110, 1570, 775),
        title="Fig. 5",
        output=args.output_dir / "fig5_original_vs_corrected.png",
        dpi=args.dpi,
    )
    _comparison_figure(
        original=original,
        corrected_path=args.corrected_figure_dir / "fig6_far_axis_uniform40.png",
        crop=(130, 920, 1570, 1570),
        title="Fig. 6",
        output=args.output_dir / "fig6_original_vs_corrected.png",
        dpi=args.dpi,
    )
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
