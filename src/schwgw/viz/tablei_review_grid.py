from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

import numpy as np


class ReviewGridPlotError(RuntimeError):
    """Raised when plotting cannot preserve the frozen review-grid contract."""


_EXPECTED_KM = np.asarray(
    [
        0.1,
        0.2,
        0.3,
        0.5,
        0.75,
        1.0,
        1.25,
        1.5,
        1.75,
        2.0,
        2.25,
        2.5,
        2.75,
        3.0,
        3.25,
        3.5,
        3.75,
        4.0,
    ],
    dtype=float,
)
_EXPECTED_POINT_IDS = np.asarray(
    [
        "near_axis_x0_z30",
        "near_axis_x1_z30",
        "near_axis_x2_z30",
        "near_axis_x3_z30",
        "far_axis_x10_z30",
        "far_axis_x15_z30",
        "far_axis_x20_z30",
        "far_axis_x25_z30",
    ]
)
_EXPECTED_POINT_GROUP = np.asarray(["near_axis"] * 4 + ["far_axis"] * 4)
_EXPECTED_POINT_X = np.asarray([0, 1, 2, 3, 10, 15, 20, 25], dtype=float)
_EXPECTED_POINT_Z = np.full(8, 30.0)
_FROZEN_SOURCE_HASHES = {
    "exact_npz": "a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb",
    "exact_json": "2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537",
    "exact_manifest": "86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf",
    "kirchhoff_npz": "66c59851e6eaf6bf5691c8026e0d528edbf304ae4bbcfc47a0290c14f87fdb55",
    "kirchhoff_json": "0b20d62be1fe39b48ce90ca2a8d0f7798fff489a777f18b2bf2d7c268376fdf3",
    "kirchhoff_manifest": "fb138038b783d2a511df94f6552a5d77a06ae7f1a32dc4c80ea54ee7f3c5e632",
}
_OUTPUT_NAMES = {
    "fig5_png": "fig5_near_axis_review_grid.png",
    "fig5_pdf": "fig5_near_axis_review_grid.pdf",
    "fig5_json": "fig5_near_axis_review_grid.json",
    "fig6_png": "fig6_far_axis_review_grid.png",
    "fig6_pdf": "fig6_far_axis_review_grid.pdf",
    "fig6_json": "fig6_far_axis_review_grid.json",
    "diagnostics": "sampling_diagnostics.json",
    "manifest": "manifest.md",
}
_GRID_ARRAYS = (
    "kM_values",
    "point_ids",
    "point_x",
    "point_y",
    "point_z",
    "point_r",
    "point_theta",
    "paper_xi_over_xi0",
)
_EXACT_MATRIX_ARRAYS = (
    "F_plus_complex",
    "F_cross_complex",
    "abs_F_plus",
    "abs_F_cross",
    "arg_F_plus_unwrapped",
    "arg_F_cross_unwrapped",
    "valid_ratio_plus_mask",
    "valid_ratio_cross_mask",
)
_KIRCHHOFF_MATRIX_ARRAYS = (
    "F_kirchhoff_complex",
    "abs_F_kirchhoff",
    "arg_F_kirchhoff_unwrapped",
    "valid_kirchhoff_mask",
)
_FLAGS = {
    "read_only": True,
    "no_solver_rerun": True,
    "no_physics_recomputation": True,
    "no_interpolation": True,
    "no_smoothing": True,
    "no_fill": True,
    "review_grid_only": True,
    "not_40_frequency_production": True,
    "not_paper_style": True,
    "kirchhoff_comparison_only": True,
    "kirchhoff_polarization_independent": True,
    "exact_line_policy": "thin guide through adjacent valid saved samples only",
}


def plot_tablei_review_grid_diagnostics(
    exact_npz: str | Path,
    kirchhoff_npz: str | Path,
    *,
    output_dir: str | Path,
    dpi: int = 300,
    created_by_cli: bool = False,
) -> dict[str, Path]:
    if int(dpi) <= 0:
        raise ReviewGridPlotError("dpi must be positive")
    sources = _load_and_validate_sources(Path(exact_npz), Path(kirchhoff_npz))
    diagnostics = _sampling_diagnostics(sources)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    unexpected = sorted(
        path.name for path in out.iterdir() if path.name not in _OUTPUT_NAMES.values()
    )
    if unexpected:
        raise ReviewGridPlotError(
            f"Output directory contains unexpected files: {unexpected}"
        )
    paths = {key: out / name for key, name in _OUTPUT_NAMES.items()}
    _render_group(
        sources,
        "near_axis",
        paths["fig5_png"],
        paths["fig5_pdf"],
        int(dpi),
    )
    _render_group(
        sources,
        "far_axis",
        paths["fig6_png"],
        paths["fig6_pdf"],
        int(dpi),
    )
    paths["diagnostics"].write_text(
        json.dumps(diagnostics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_figure_sidecar(
        sources, diagnostics, "near_axis", paths, created_by_cli, int(dpi)
    )
    _write_figure_sidecar(
        sources, diagnostics, "far_axis", paths, created_by_cli, int(dpi)
    )
    paths["manifest"].write_text(_manifest_text(sources, paths), encoding="utf-8")
    if {path.name for path in out.iterdir()} != set(_OUTPUT_NAMES.values()):
        raise ReviewGridPlotError("Review-grid output cardinality is not exactly eight")
    return paths


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _triplet(npz_path: Path) -> tuple[Path, Path, Path]:
    return (
        npz_path,
        npz_path.with_suffix(npz_path.suffix + ".json"),
        npz_path.parent / "manifest.md",
    )


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReviewGridPlotError(f"Cannot read JSON metadata {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReviewGridPlotError(f"Metadata must be an object: {path}")
    return value


def _load_and_validate_sources(
    exact_npz: Path, kirchhoff_npz: Path
) -> dict[str, Any]:
    exact_triplet = _triplet(exact_npz)
    kirchhoff_triplet = _triplet(kirchhoff_npz)
    for path in (*exact_triplet, *kirchhoff_triplet):
        if not path.is_file():
            raise ReviewGridPlotError(f"missing source file: {path}")

    actual_hashes = {
        "exact_npz": _file_sha256(exact_triplet[0]),
        "exact_json": _file_sha256(exact_triplet[1]),
        "exact_manifest": _file_sha256(exact_triplet[2]),
        "kirchhoff_npz": _file_sha256(kirchhoff_triplet[0]),
        "kirchhoff_json": _file_sha256(kirchhoff_triplet[1]),
        "kirchhoff_manifest": _file_sha256(kirchhoff_triplet[2]),
    }
    if actual_hashes != _FROZEN_SOURCE_HASHES:
        raise ReviewGridPlotError(
            "frozen source hash mismatch: "
            f"expected {_FROZEN_SOURCE_HASHES}, got {actual_hashes}"
        )

    exact_sidecar = _read_json(exact_triplet[1])
    kirchhoff_sidecar = _read_json(kirchhoff_triplet[1])
    exact_arrays, exact_embedded = _load_npz(
        exact_npz, (*_GRID_ARRAYS, "point_group", *_EXACT_MATRIX_ARRAYS)
    )
    kirchhoff_arrays, kirchhoff_embedded = _load_npz(
        kirchhoff_npz, (*_GRID_ARRAYS, *_KIRCHHOFF_MATRIX_ARRAYS)
    )
    if exact_embedded != exact_sidecar:
        raise ReviewGridPlotError("exact embedded metadata and sidecar mismatch")
    kirchhoff_comparable = dict(kirchhoff_sidecar)
    kirchhoff_comparable.pop("output_npz_path", None)
    kirchhoff_comparable.pop("output_npz_sha256", None)
    if kirchhoff_embedded != kirchhoff_comparable:
        raise ReviewGridPlotError("Kirchhoff embedded metadata and sidecar mismatch")
    if exact_embedded.get("schema_version") != "phase5_t8aj_fig5_fig6_review_grid_v2":
        raise ReviewGridPlotError("exact source schema mismatch")
    if kirchhoff_embedded.get("schema_version") != (
        "phase5_t8al_kirchhoff_review_grid_v2_units_dtype"
    ):
        raise ReviewGridPlotError("Kirchhoff source schema mismatch")
    _require_flags(
        exact_embedded,
        (
            "no_interpolation",
            "no_smoothing",
            "no_fill",
            "no_plotting",
            "no_kirchhoff",
            "no_paper_level_production",
        ),
        "exact",
    )
    _require_flags(
        kirchhoff_embedded,
        (
            "comparison_only",
            "polarization_independent",
            "not_denominator",
            "not_mask",
            "not_normalization",
            "no_interpolation",
            "no_smoothing",
            "no_solver_rerun",
        ),
        "Kirchhoff",
    )
    if not isinstance(kirchhoff_embedded.get("units"), dict) or not isinstance(
        kirchhoff_embedded.get("dtype"), dict
    ):
        raise ReviewGridPlotError("Kirchhoff units/dtype metadata is missing")

    if not np.array_equal(exact_arrays["kM_values"], _EXPECTED_KM):
        raise ReviewGridPlotError("exact accepted frequency grid mismatch")
    if not np.array_equal(exact_arrays["point_ids"], _EXPECTED_POINT_IDS):
        raise ReviewGridPlotError("exact accepted point IDs mismatch")
    if not np.array_equal(exact_arrays["point_group"], _EXPECTED_POINT_GROUP):
        raise ReviewGridPlotError("exact accepted point groups mismatch")
    if not np.array_equal(exact_arrays["point_x"], _EXPECTED_POINT_X) or not np.array_equal(
        exact_arrays["point_z"], _EXPECTED_POINT_Z
    ):
        raise ReviewGridPlotError("exact accepted Table-I coordinates mismatch")
    for name in _GRID_ARRAYS:
        if not np.array_equal(exact_arrays[name], kirchhoff_arrays[name]):
            raise ReviewGridPlotError(f"paired grid mismatch for {name}")
    _validate_matrices(exact_arrays, _EXACT_MATRIX_ARRAYS, "exact")
    _validate_matrices(kirchhoff_arrays, _KIRCHHOFF_MATRIX_ARRAYS, "Kirchhoff")

    dtype_metadata = kirchhoff_embedded["dtype"]
    for name in (*_GRID_ARRAYS, *_KIRCHHOFF_MATRIX_ARRAYS):
        declared = dtype_metadata.get(name)
        if declared is None or declared != str(kirchhoff_arrays[name].dtype):
            raise ReviewGridPlotError(f"Kirchhoff dtype metadata mismatch for {name}")
    for manifest, npz_hash, json_hash in (
        (exact_triplet[2], actual_hashes["exact_npz"], actual_hashes["exact_json"]),
        (
            kirchhoff_triplet[2],
            actual_hashes["kirchhoff_npz"],
            actual_hashes["kirchhoff_json"],
        ),
    ):
        text = manifest.read_text(encoding="utf-8")
        if npz_hash not in text or json_hash not in text:
            raise ReviewGridPlotError(f"source manifest hash record mismatch: {manifest}")

    plus_mask = exact_arrays["valid_ratio_plus_mask"]
    cross_mask = exact_arrays["valid_ratio_cross_mask"]
    kirchhoff_mask = kirchhoff_arrays["valid_kirchhoff_mask"]
    _require_finite_where_valid(
        (exact_arrays["abs_F_plus"], exact_arrays["arg_F_plus_unwrapped"]),
        plus_mask,
        "exact plus",
    )
    _require_finite_where_valid(
        (exact_arrays["abs_F_cross"], exact_arrays["arg_F_cross_unwrapped"]),
        cross_mask,
        "exact cross",
    )
    _require_finite_where_valid(
        (
            kirchhoff_arrays["abs_F_kirchhoff"],
            kirchhoff_arrays["arg_F_kirchhoff_unwrapped"],
        ),
        kirchhoff_mask,
        "Kirchhoff",
    )
    return {
        "kM": exact_arrays["kM_values"],
        "point_ids": exact_arrays["point_ids"],
        "point_group": exact_arrays["point_group"],
        "point_x": exact_arrays["point_x"],
        "point_z": exact_arrays["point_z"],
        "abs_plus": exact_arrays["abs_F_plus"],
        "abs_cross": exact_arrays["abs_F_cross"],
        "phase_plus": exact_arrays["arg_F_plus_unwrapped"],
        "phase_cross": exact_arrays["arg_F_cross_unwrapped"],
        "plus_mask": plus_mask,
        "cross_mask": cross_mask,
        "kirchhoff_abs": kirchhoff_arrays["abs_F_kirchhoff"],
        "kirchhoff_phase": kirchhoff_arrays["arg_F_kirchhoff_unwrapped"],
        "kirchhoff_mask": kirchhoff_mask,
        "exact_metadata": exact_embedded,
        "kirchhoff_metadata": kirchhoff_embedded,
        "source_hashes": actual_hashes,
        "exact_triplet": exact_triplet,
        "kirchhoff_triplet": kirchhoff_triplet,
    }


def _load_npz(
    path: Path, required: tuple[str, ...]
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    try:
        with np.load(path, allow_pickle=False) as data:
            missing = [name for name in (*required, "metadata_json") if name not in data]
            if missing:
                raise ReviewGridPlotError(f"source NPZ missing arrays {missing}: {path}")
            arrays = {name: np.asarray(data[name]) for name in required}
            embedded = json.loads(str(data["metadata_json"].item()))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise ReviewGridPlotError(f"Cannot read source NPZ {path}: {exc}") from exc
    if not isinstance(embedded, dict):
        raise ReviewGridPlotError(f"embedded metadata must be an object: {path}")
    return arrays, embedded


def _require_flags(metadata: dict[str, Any], names: tuple[str, ...], label: str) -> None:
    for name in names:
        if metadata.get(name) is not True:
            raise ReviewGridPlotError(f"{label} required metadata flag is not true: {name}")


def _validate_matrices(
    arrays: dict[str, np.ndarray], names: tuple[str, ...], label: str
) -> None:
    for name in names:
        if arrays[name].shape != (18, 8):
            raise ReviewGridPlotError(f"{label} array shape mismatch for {name}")
    for name in names:
        if "mask" in name and arrays[name].dtype != np.dtype(bool):
            raise ReviewGridPlotError(f"{label} mask dtype mismatch for {name}")


def _require_finite_where_valid(
    arrays: tuple[np.ndarray, ...], mask: np.ndarray, label: str
) -> None:
    for array in arrays:
        if not np.all(np.isfinite(array[mask])):
            raise ReviewGridPlotError(f"{label} contains non-finite valid values")


def _pair_metrics(
    values: np.ndarray, mask: np.ndarray, kM: np.ndarray
) -> dict[str, Any]:
    valid = mask[:-1] & mask[1:] & np.isfinite(values[:-1]) & np.isfinite(values[1:])
    absolute = np.where(valid, np.abs(np.diff(values, axis=0)), np.nan)
    scale = np.maximum(1.0, np.maximum(np.abs(values[:-1]), np.abs(values[1:])))
    relative = np.where(valid, absolute / scale, np.nan)
    slope = np.where(valid, absolute / np.diff(kM)[:, None], np.nan)
    return {
        "valid_pair": valid,
        "absolute_step": absolute,
        "relative_step": relative,
        "absolute_slope": slope,
    }


def _sampling_diagnostics(sources: dict[str, Any]) -> dict[str, Any]:
    groups: dict[str, Any] = {}
    all_proxy_pass = True
    for group in ("near_axis", "far_axis"):
        indices = np.flatnonzero(sources["point_group"] == group)
        group_result: dict[str, Any] = {}
        for component in ("plus", "cross"):
            magnitude = sources[f"abs_{component}"][:, indices]
            phase = sources[f"phase_{component}"][:, indices]
            mask = sources[f"{component}_mask"][:, indices]
            magnitude_metrics = _pair_metrics(magnitude, mask, sources["kM"])
            phase_metrics = _pair_metrics(phase, mask, sources["kM"])
            magnitude_max = {
                "absolute_step": _maximum_record(
                    magnitude_metrics["absolute_step"], indices, sources
                ),
                "relative_step": _maximum_record(
                    magnitude_metrics["relative_step"], indices, sources
                ),
            }
            phase_max = _maximum_record(
                phase_metrics["absolute_slope"], indices, sources
            )
            max_slope = float(phase_max["value"])
            projected = 0.1 * max_slope
            safety_projected = 1.5 * projected
            proxy_pass = bool(safety_projected < np.pi / 2)
            all_proxy_pass &= proxy_pass
            adjacent_pairs = _adjacent_records(
                magnitude_metrics, phase_metrics, indices, sources
            )
            group_result[component] = {
                "adjacent_pairs": adjacent_pairs,
                "magnitude_maxima": magnitude_max,
                "phase": {
                    "max_observed_phase_slope": phase_max,
                    "projected_phase_step_0p1": projected,
                    "safety_factor": 1.5,
                    "safety_projected_phase_step_0p1": safety_projected,
                    "phase_proxy_limit": float(np.pi / 2),
                    "phase_proxy_pass": proxy_pass,
                },
            }
        groups[group] = group_result
    recommendation = (
        "DELTA_0P1_PROVISIONAL_REVIEW"
        if all_proxy_pass
        else "DELTA_0P05_OR_TARGETED_MIDPOINT_REVIEW"
    )
    return {
        "schema_version": "phase5_t8am_review_grid_sampling_diagnostics_v1",
        "frequency_grid": sources["kM"].tolist(),
        "candidate_delta_kM": 0.1,
        "phase_safety_factor": 1.5,
        "phase_proxy_is_diagnostic_not_theorem": True,
        "magnitude_has_no_automatic_threshold": True,
        "groups": groups,
        "all_phase_proxies_pass": bool(all_proxy_pass),
        "sampling_recommendation": recommendation,
        "source_hashes": dict(sources["source_hashes"]),
        "flags": dict(_FLAGS),
    }


def _maximum_record(
    values: np.ndarray, point_indices: np.ndarray, sources: dict[str, Any]
) -> dict[str, Any]:
    if not np.any(np.isfinite(values)):
        raise ReviewGridPlotError("sampling metric has no finite adjacent pairs")
    flat = int(np.nanargmax(values))
    interval_index, local_point_index = np.unravel_index(flat, values.shape)
    point_index = int(point_indices[local_point_index])
    return {
        "value": float(values[interval_index, local_point_index]),
        "point_id": str(sources["point_ids"][point_index]),
        "interval": [
            float(sources["kM"][interval_index]),
            float(sources["kM"][interval_index + 1]),
        ],
    }


def _adjacent_records(
    magnitude: dict[str, np.ndarray],
    phase: dict[str, np.ndarray],
    point_indices: np.ndarray,
    sources: dict[str, Any],
) -> list[dict[str, Any]]:
    records = []
    for local_point, point_index in enumerate(point_indices):
        for interval in range(len(sources["kM"]) - 1):
            valid = bool(
                magnitude["valid_pair"][interval, local_point]
                and phase["valid_pair"][interval, local_point]
            )
            records.append(
                {
                    "point_id": str(sources["point_ids"][point_index]),
                    "interval": [
                        float(sources["kM"][interval]),
                        float(sources["kM"][interval + 1]),
                    ],
                    "delta_kM": float(np.diff(sources["kM"])[interval]),
                    "valid_endpoint_pair": valid,
                    "absolute_magnitude_step": _optional_float(
                        magnitude["absolute_step"][interval, local_point], valid
                    ),
                    "relative_magnitude_step": _optional_float(
                        magnitude["relative_step"][interval, local_point], valid
                    ),
                    "absolute_unwrapped_phase_step": _optional_float(
                        phase["absolute_step"][interval, local_point], valid
                    ),
                    "absolute_unwrapped_phase_slope": _optional_float(
                        phase["absolute_slope"][interval, local_point], valid
                    ),
                }
            )
    return records


def _optional_float(value: float, valid: bool) -> float | None:
    return float(value) if valid and np.isfinite(value) else None


def _valid_segments(
    x: np.ndarray, y: np.ndarray, mask: np.ndarray
) -> list[tuple[np.ndarray, np.ndarray]]:
    valid = np.asarray(mask, dtype=bool) & np.isfinite(y)
    segments: list[tuple[np.ndarray, np.ndarray]] = []
    start: int | None = None
    for index, is_valid in enumerate(valid):
        if is_valid and start is None:
            start = index
        if start is not None and (not is_valid or index == len(valid) - 1):
            stop = index if not is_valid else index + 1
            if stop - start >= 2:
                segments.append((x[start:stop], y[start:stop]))
            start = None
    return segments


def _render_group(
    sources: dict[str, Any],
    group: str,
    png_path: Path,
    pdf_path: Path,
    dpi: int,
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
    except ImportError as exc:
        raise ReviewGridPlotError(f"matplotlib is required for diagnostics: {exc}") from exc

    colors = ["#0072B2", "#D55E00", "#009E73", "#CC79A7"]
    markers = ["o", "s", "^", "D"]
    indices = np.flatnonzero(sources["point_group"] == group)
    figure, axes = plt.subplots(
        2, 2, figsize=(7.0, 5.4), dpi=dpi, constrained_layout=True, sharex=True
    )
    panels = (
        (sources["abs_plus"], sources["plus_mask"], "magnitude", r"$|F_+|$", "(A)"),
        (
            sources["abs_cross"],
            sources["cross_mask"],
            "magnitude",
            r"$|F_\times|$",
            "(B)",
        ),
        (
            sources["phase_plus"],
            sources["plus_mask"],
            "phase",
            r"unwrapped arg $F_+$",
            "(C)",
        ),
        (
            sources["phase_cross"],
            sources["cross_mask"],
            "phase",
            r"unwrapped arg $F_\times$",
            "(D)",
        ),
    )
    for axis, (values, mask, kind, title, panel_label) in zip(
        axes.flat, panels, strict=True
    ):
        kirchhoff_values = (
            sources["kirchhoff_abs"] if kind == "magnitude" else sources["kirchhoff_phase"]
        )
        for local, point_index in enumerate(indices):
            exact_valid = mask[:, point_index] & np.isfinite(values[:, point_index])
            axis.plot(
                sources["kM"][exact_valid],
                values[exact_valid, point_index],
                linestyle="none",
                marker=markers[local],
                markersize=3.5,
                markerfacecolor=colors[local],
                markeredgecolor=colors[local],
            )
            for segment_x, segment_y in _valid_segments(
                sources["kM"], values[:, point_index], mask[:, point_index]
            ):
                axis.plot(segment_x, segment_y, color=colors[local], linewidth=0.8)
            for segment_x, segment_y in _valid_segments(
                sources["kM"],
                kirchhoff_values[:, point_index],
                sources["kirchhoff_mask"][:, point_index],
            ):
                axis.plot(
                    segment_x,
                    segment_y,
                    color=colors[local],
                    linewidth=1.1,
                    linestyle="--",
                )
        axis.set_title(title, fontsize=9)
        axis.text(0.02, 0.96, panel_label, transform=axis.transAxes, va="top", weight="bold")
        axis.set_ylabel("dimensionless" if kind == "magnitude" else "phase (radian)")
        axis.grid(True, which="major", color="0.9", linewidth=0.5)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
    axes[1, 0].set_xlabel(r"$kM$")
    axes[1, 1].set_xlabel(r"$kM$")
    style_handles = [
        Line2D([0], [0], color="0.25", marker="o", linewidth=0.8, markersize=3.5),
        Line2D([0], [0], color="0.25", marker="s", linewidth=0.8, markersize=3.5),
        Line2D([0], [0], color="0.25", linestyle="--", linewidth=1.1),
    ]
    axes[0, 0].legend(
        style_handles,
        ["exact F_plus", "exact F_cross", "Kirchhoff scalar comparison"],
        fontsize=6.5,
        frameon=False,
        loc="best",
    )
    point_handles = [
        Line2D(
            [0],
            [0],
            color=colors[local],
            marker=markers[local],
            linestyle="none",
            markersize=4,
        )
        for local in range(4)
    ]
    point_labels = [f"x/M={sources['point_x'][index]:g}" for index in indices]
    figure.legend(
        point_handles,
        point_labels,
        ncol=4,
        loc="outside lower center",
        fontsize=7,
        frameon=False,
        title="Table-I points at z/M=30",
        title_fontsize=7,
    )
    group_label = "Near-axis" if group == "near_axis" else "Far-axis"
    figure.suptitle(
        f"{group_label} Fig.5/Fig.6 diagnostics\n"
        "18-point nonuniform review grid — diagnostic only",
        fontsize=10,
    )
    figure.savefig(png_path, dpi=dpi)
    figure.savefig(pdf_path)
    plt.close(figure)


def _write_figure_sidecar(
    sources: dict[str, Any],
    diagnostics: dict[str, Any],
    group: str,
    paths: dict[str, Path],
    created_by_cli: bool,
    dpi: int,
) -> None:
    prefix = "fig5" if group == "near_axis" else "fig6"
    indices = np.flatnonzero(sources["point_group"] == group)
    metadata = {
        "schema_version": "phase5_t8am_review_grid_figure_v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by_cli": bool(created_by_cli),
        "group": group,
        "point_ids": [str(sources["point_ids"][index]) for index in indices],
        "point_x_over_M": [float(sources["point_x"][index]) for index in indices],
        "point_z_over_M": [float(sources["point_z"][index]) for index in indices],
        "kM_values": sources["kM"].tolist(),
        "source_triplets": _source_records(sources),
        "source_schemas": {
            "exact": sources["exact_metadata"]["schema_version"],
            "kirchhoff": sources["kirchhoff_metadata"]["schema_version"],
        },
        "source_case_ids": {
            "exact": sources["exact_metadata"].get("case_id"),
            "kirchhoff": sources["kirchhoff_metadata"].get("case_id"),
        },
        "plotted_arrays": {
            "exact": [
                "abs_F_plus",
                "abs_F_cross",
                "arg_F_plus_unwrapped",
                "arg_F_cross_unwrapped",
            ],
            "kirchhoff_scalar": [
                "abs_F_kirchhoff",
                "arg_F_kirchhoff_unwrapped",
            ],
        },
        "mask_policy": "honor each saved mask independently; no fill or invalid-gap connection",
        "phase_policy": "use saved unwrapped phase for diagnostic display and adjacent metrics",
        "palette": ["#0072B2", "#D55E00", "#009E73", "#CC79A7"],
        "markers": ["o", "s", "^", "D"],
        "line_styles": {
            "exact": "markers plus 0.8-width adjacent-valid-sample solid guides",
            "kirchhoff_scalar": "1.1-width dashed comparison lines without spin markers",
        },
        "panel_layout": ["|F_plus|", "|F_cross|", "arg F_plus", "arg F_cross"],
        "dpi": dpi,
        "output_sha256": {
            "png": _file_sha256(paths[f"{prefix}_png"]),
            "pdf": _file_sha256(paths[f"{prefix}_pdf"]),
        },
        "sampling_recommendation": diagnostics["sampling_recommendation"],
        "group_sampling_metrics": diagnostics["groups"][group],
        "flags": dict(_FLAGS),
        "git": _git_info(),
    }
    paths[f"{prefix}_json"].write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _source_records(sources: dict[str, Any]) -> dict[str, Any]:
    records = {}
    for label, triplet in (
        ("exact", sources["exact_triplet"]),
        ("kirchhoff", sources["kirchhoff_triplet"]),
    ):
        records[label] = {
            kind: {
                "path": str(path),
                "size_bytes": path.stat().st_size,
                "sha256": sources["source_hashes"][f"{label}_{kind}"],
            }
            for kind, path in zip(("npz", "json", "manifest"), triplet, strict=True)
        }
    return records


def _git_info() -> dict[str, Any]:
    result: dict[str, Any] = {}
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        status = subprocess.run(
            ["git", "status", "--short"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return result
    result["head"] = head.stdout.strip()
    result["status_short"] = status.stdout.splitlines()
    return result


def _manifest_text(sources: dict[str, Any], paths: dict[str, Path]) -> str:
    companion_keys = (
        "fig5_png",
        "fig5_pdf",
        "fig5_json",
        "fig6_png",
        "fig6_pdf",
        "fig6_json",
        "diagnostics",
    )
    outputs = "\n".join(
        f"- `{paths[key].name}` — SHA256 `{_file_sha256(paths[key])}`"
        for key in companion_keys
    )
    source_hashes = "\n".join(
        f"- `{name}`: `{value}`" for name, value in sources["source_hashes"].items()
    )
    return f"""# Fig.5/Fig.6 Review-Grid Diagnostics Manifest

Status: diagnostic-only; pending T7bu sampling review.

These outputs use only saved values from the accepted 18-point nonuniform
review grid. They contain no solver or physics rerun, interpolation, smoothing,
fill, 40/79-frequency production, or paper-style claim. Kirchhoff is a scalar,
polarization-independent comparison only.

## Frozen source hashes

{source_hashes}

## Companion artifacts

{outputs}
"""
