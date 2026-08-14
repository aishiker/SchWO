#!/usr/bin/env python3
"""Digitize the published Fig. 4 exact curves and compare repaired data.

The paper does not provide raw Fig. 4 values.  This script therefore treats
the frozen 1700x2200 page raster as a low-resolution diagnostic, explicitly
records the pixel calibration, and restricts the extraction to theta/pi >=
0.2 where the main exact curves are below the inset boxes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from schwgw.io.results import load_results


KM_VALUES = (0.5, 1.0, 1.5, 2.0)
PANEL_X = ((234, 879), (894, 1539), (234, 879), (894, 1539))
# Least-squares calibration from the horizontal y=2,4,6,8 grid lines.
PANEL_Y_ZERO = (1239.75, 1239.75, 1513.0, 1513.0)
PANEL_PIXELS_PER_UNIT = (28.85, 28.85, 28.85, 28.85)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _token(value: float) -> str:
    return f"{value:g}".replace(".", "p")


def _color_mask(image: np.ndarray, channel: str) -> np.ndarray:
    red = image[:, :, 0]
    green = image[:, :, 1]
    blue = image[:, :, 2]
    if channel == "red":
        return (red > 180) & (green < 90) & (blue < 90)
    if channel == "blue":
        return (blue > 180) & (red < 90) & (green < 90)
    raise ValueError(f"unsupported color channel: {channel}")


def _digitize_curve(
    mask: np.ndarray,
    *,
    panel: int,
    theta_over_pi: np.ndarray,
) -> np.ndarray:
    x0, x1 = PANEL_X[panel]
    y_zero = PANEL_Y_ZERO[panel]
    pixels_per_unit = PANEL_PIXELS_PER_UNIT[panel]
    # The main exact curves are below |h|=3 for theta/pi >= 0.2.  Keeping this
    # narrow band excludes every inset exact curve without selecting by shape.
    y_min = int(np.floor(y_zero - 3.0 * pixels_per_unit))
    y_max = int(np.ceil(y_zero + 2.0))
    values = np.full(theta_over_pi.shape, np.nan, dtype=np.float64)
    for index, angle in enumerate(theta_over_pi):
        x = int(round(x0 + float(angle) * (x1 - x0)))
        hits = np.empty(0, dtype=np.int64)
        for radius in (2, 3, 4, 5):
            lo = max(x0, x - radius)
            hi = min(x1 + 1, x + radius + 1)
            local_y, _ = np.where(mask[y_min : y_max + 1, lo:hi])
            if local_y.size:
                hits = local_y + y_min
                break
        if hits.size:
            values[index] = (y_zero - float(np.median(hits))) / pixels_per_unit
    return values


def _metrics(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float | int]:
    valid = np.isfinite(reference) & np.isfinite(candidate)
    if np.count_nonzero(valid) < 50:
        raise ValueError("too few published-raster samples survived extraction")
    residual = candidate[valid] - reference[valid]
    return {
        "sample_count": int(np.count_nonzero(valid)),
        "mean_absolute_error": float(np.mean(np.abs(residual))),
        "root_mean_square_error": float(np.sqrt(np.mean(residual**2))),
        "maximum_absolute_error": float(np.max(np.abs(residual))),
        "mean_signed_error": float(np.mean(residual)),
    }


def _nullable(values: np.ndarray) -> list[float | None]:
    return [float(value) if np.isfinite(value) else None for value in values]


def _historical_metrics(
    path: Path,
    *,
    published_plus: list[np.ndarray],
    published_cross: list[np.ndarray],
    sample_angles: np.ndarray,
) -> dict[str, object]:
    with np.load(path, allow_pickle=False) as data:
        theta = np.asarray(data["theta"], dtype=np.float64) / np.pi
        plus = np.asarray(data["h_plus_exact"], dtype=np.complex128)
        cross = np.asarray(data["h_cross_exact"], dtype=np.complex128)
    if theta.shape != (4, 1025) or plus.shape != theta.shape or cross.shape != theta.shape:
        raise ValueError("historical Fig. 4 comparison has an unexpected shape")
    records = []
    for panel, kM in enumerate(KM_VALUES):
        candidate_plus = np.interp(sample_angles, theta[panel], np.abs(plus[panel]))
        candidate_cross = np.interp(
            sample_angles,
            theta[panel],
            np.abs(cross[panel]),
        )
        records.append(
            {
                "kM": kM,
                "plus": _metrics(published_plus[panel], candidate_plus),
                "cross": _metrics(published_cross[panel], candidate_cross),
            }
        )
    return {"path": str(path), "sha256": _sha256(path), "records": records}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-page", type=Path, required=True)
    parser.add_argument("--direct-dir", type=Path, required=True)
    parser.add_argument("--historical-scattered", type=Path)
    parser.add_argument("--historical-double-counted", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise FileExistsError(f"refusing comparison collision: {args.output}")

    image = np.asarray(Image.open(args.paper_page).convert("RGB"))
    if image.shape != (2200, 1700, 3):
        raise ValueError("Fig. 4 digitizer is calibrated to the frozen 1700x2200 page")
    blue_mask = _color_mask(image, "blue")
    red_mask = _color_mask(image, "red")
    sample_angles = np.linspace(0.2, 1.0, 161, dtype=np.float64)

    records = []
    published_plus_rows = []
    published_cross_rows = []
    for panel, kM in enumerate(KM_VALUES):
        path = args.direct_dir / f"fig4_direct_curvature_kM_{_token(kM)}.npz"
        result = load_results(path)
        theta = np.asarray(result.theta, dtype=np.float64).reshape(-1) / np.pi
        repaired_plus = np.interp(sample_angles, theta, np.abs(result.h_plus[:, 0]))
        repaired_cross = np.interp(sample_angles, theta, np.abs(result.h_cross[:, 0]))
        published_plus = _digitize_curve(
            blue_mask,
            panel=panel,
            theta_over_pi=sample_angles,
        )
        published_cross = _digitize_curve(
            red_mask,
            panel=panel,
            theta_over_pi=sample_angles,
        )
        published_plus_rows.append(published_plus)
        published_cross_rows.append(published_cross)
        records.append(
            {
                "kM": kM,
                "repaired_source": str(path),
                "repaired_source_sha256": _sha256(path),
                "plus": _metrics(published_plus, repaired_plus),
                "cross": _metrics(published_cross, repaired_cross),
                "published_plus": _nullable(published_plus),
                "published_cross": _nullable(published_cross),
                "repaired_plus": _nullable(repaired_plus),
                "repaired_cross": _nullable(repaired_cross),
            }
        )

    historical = {}
    if args.historical_scattered is not None:
        historical["route_b_scattered_only"] = _historical_metrics(
            args.historical_scattered,
            published_plus=published_plus_rows,
            published_cross=published_cross_rows,
            sample_angles=sample_angles,
        )
    if args.historical_double_counted is not None:
        historical["route_b_renderer_with_incident_double_count"] = _historical_metrics(
            args.historical_double_counted,
            published_plus=published_plus_rows,
            published_cross=published_cross_rows,
            sample_angles=sample_angles,
        )
    payload = {
        "schema_version": "schwgw_fig4_published_raster_comparison_v1",
        "status": "RASTER_DIAGNOSTIC_NOT_RAW_DATA",
        "paper_page": str(args.paper_page),
        "paper_page_sha256": _sha256(args.paper_page),
        "theta_over_pi": sample_angles.tolist(),
        "pixel_calibration": {
            "panel_x": [list(pair) for pair in PANEL_X],
            "panel_y_zero": list(PANEL_Y_ZERO),
            "panel_pixels_per_amplitude_unit": list(PANEL_PIXELS_PER_UNIT),
            "exact_plus_color": "saturated blue",
            "exact_cross_color": "saturated red",
            "main_curve_amplitude_window": [0.0, 3.0],
        },
        "records": records,
        "historical": historical,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"event": "fig4_published_raster_comparison_complete"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
