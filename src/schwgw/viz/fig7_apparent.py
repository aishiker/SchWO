"""Journal renderers for saved diagnostic Fig. 7 apparent wavefields.

The renderer is deliberately read-only: it consumes the four saved apparent
polarization grids and never invokes a solver.  Bilinear interpolation is a
display choice only; a nearest-neighbor audit image is emitted alongside the
publication display.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from schwgw.io.apparent import ApparentGridResult, load_apparent_results


EXPECTED_KM_VALUES = (0.5, 1.0, 1.5, 2.0)
FIG7_COMPONENTS = (
    ("h_x", r"$\mathrm{Re}\,\widetilde{h}_{x}$"),
    ("h_y", r"$\mathrm{Re}\,\widetilde{h}_{y}$"),
    ("h_b", r"$\mathrm{Re}\,\widetilde{h}_{b}$"),
    ("h_longitudinal", r"$\mathrm{Re}\,\widetilde{h}_{L}$"),
)
FIG7_RENDERER_SCHEMA = "li_hou_zhao_fig7_apparent_renderer_v1"
FIG7_PAPER_COLOR_LIMIT = 0.9


class Fig7ApparentPlotError(ValueError):
    """Raised when saved Fig. 7 diagnostics cannot be rendered safely."""


@dataclass(frozen=True)
class Fig7ApparentArtifacts:
    """Paths written by :func:`render_fig7_apparent_four_frequency`."""

    pdf: Path
    display_png: Path
    audit_png: Path
    manifest: Path


def render_fig7_apparent_four_frequency(
    result_paths: list[str | Path] | tuple[str | Path, ...],
    *,
    output_dir: str | Path,
    basename: str = "fig7_apparent_four_frequency",
    created_by_cli: bool = False,
) -> Fig7ApparentArtifacts:
    """Render the 4-by-4 Fig. 7 apparent-polarization comparison.

    Inputs must be the four saved ``kM=(0.5, 1, 1.5, 2)`` Fig. 7 grids in
    increasing order.  The output directory receives a PDF, a 600 dpi
    bilinear display PNG, a 600 dpi nearest-neighbor audit PNG, one JSON
    sidecar for each image, and a JSON manifest binding the source hashes.
    """

    if len(result_paths) != len(EXPECTED_KM_VALUES):
        raise Fig7ApparentPlotError(
            "Fig. 7 rendering requires exactly four saved apparent grids."
        )
    if not basename or Path(basename).name != basename:
        raise Fig7ApparentPlotError("basename must be a non-empty filename stem.")

    paths = [Path(path) for path in result_paths]
    results = [load_apparent_results(path) for path in paths]
    kM_values = [_required_kM(result) for result in results]
    if not np.allclose(kM_values, EXPECTED_KM_VALUES, rtol=0.0, atol=1.0e-12):
        raise Fig7ApparentPlotError(
            "Fig. 7 inputs must have kM values [0.5, 1.0, 1.5, 2.0] "
            "in increasing kM order."
        )
    mass = _require_shared_grid_and_mass(results)
    output_root = Path(output_dir)
    artifacts = _artifact_paths(output_root, basename)
    _refuse_collisions(artifacts)
    output_root.mkdir(parents=True, exist_ok=True)

    row_color_scales = _row_color_scales(results)
    source_records = [_source_record(path, result, kM) for path, result, kM in zip(
        paths, results, kM_values, strict=True
    )]
    _render_panel(
        results,
        kM_values=kM_values,
        row_color_scales=row_color_scales,
        mass=mass,
        interpolation="bilinear",
        output_path=artifacts.pdf,
        dpi=600,
        output_format="pdf",
    )
    _render_panel(
        results,
        kM_values=kM_values,
        row_color_scales=row_color_scales,
        mass=mass,
        interpolation="bilinear",
        output_path=artifacts.display_png,
        dpi=600,
        output_format="png",
    )
    _render_panel(
        results,
        kM_values=kM_values,
        row_color_scales=row_color_scales,
        mass=mass,
        interpolation="nearest",
        output_path=artifacts.audit_png,
        dpi=600,
        output_format="png",
    )

    render_common = _render_common_metadata(
        source_records=source_records,
        kM_values=kM_values,
        row_color_scales=row_color_scales,
        mass=mass,
        created_by_cli=created_by_cli,
    )
    sidecars = {
        artifacts.pdf: ("pdf", "bilinear", "journal_vector_pdf"),
        artifacts.display_png: ("png", "bilinear", "display"),
        artifacts.audit_png: ("png", "nearest", "numerical_audit"),
    }
    sidecar_records = []
    for output_path, (output_format, interpolation, purpose) in sidecars.items():
        sidecar_path = output_path.with_suffix(output_path.suffix + ".json")
        payload = {
            **render_common,
            "artifact": {
                "path": str(output_path),
                "sha256": _file_sha256(output_path),
                "format": output_format,
                "purpose": purpose,
                "dpi": 600,
                "display_interpolation": interpolation,
                "display_interpolation_only": True,
            },
        }
        sidecar_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        sidecar_records.append(
            {
                "path": str(sidecar_path),
                "sha256": _file_sha256(sidecar_path),
                "artifact_path": str(output_path),
            }
        )

    manifest = {
        **render_common,
        "artifacts": [
            {
                "path": str(path),
                "sha256": _file_sha256(path),
                "format": output_format,
                "purpose": purpose,
                "display_interpolation": interpolation,
                "display_interpolation_only": True,
            }
            for path, (output_format, interpolation, purpose) in sidecars.items()
        ],
        "sidecars": sidecar_records,
    }
    artifacts.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return artifacts


def _artifact_paths(output_dir: Path, basename: str) -> Fig7ApparentArtifacts:
    pdf = output_dir / f"{basename}.pdf"
    display_png = output_dir / f"{basename}_display_bilinear_600dpi.png"
    audit_png = output_dir / f"{basename}_numerical_audit_nearest_600dpi.png"
    return Fig7ApparentArtifacts(
        pdf=pdf,
        display_png=display_png,
        audit_png=audit_png,
        manifest=output_dir / f"{basename}.manifest.json",
    )


def _refuse_collisions(artifacts: Fig7ApparentArtifacts) -> None:
    planned = [
        artifacts.pdf,
        artifacts.display_png,
        artifacts.audit_png,
        artifacts.manifest,
        artifacts.pdf.with_suffix(artifacts.pdf.suffix + ".json"),
        artifacts.display_png.with_suffix(artifacts.display_png.suffix + ".json"),
        artifacts.audit_png.with_suffix(artifacts.audit_png.suffix + ".json"),
    ]
    collisions = [str(path) for path in planned if path.exists()]
    if collisions:
        raise FileExistsError(f"Refusing Fig. 7 renderer output collisions: {collisions}")


def _required_kM(result: ApparentGridResult) -> float:
    try:
        value = result.metadata["config"]["wave"]["kM"]
    except (KeyError, TypeError) as exc:
        raise Fig7ApparentPlotError("Fig. 7 source metadata missing config.wave.kM.") from exc
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Fig7ApparentPlotError("Fig. 7 source config.wave.kM must be numeric.")
    kM = float(value)
    if not np.isfinite(kM):
        raise Fig7ApparentPlotError("Fig. 7 source config.wave.kM must be finite.")
    return kM


def _require_shared_grid_and_mass(results: list[ApparentGridResult]) -> float:
    reference = results[0]
    mass = _required_mass(reference)
    for result in results[1:]:
        if not np.array_equal(result.x, reference.x) or not np.array_equal(
            result.z, reference.z
        ):
            raise Fig7ApparentPlotError("Fig. 7 inputs must share identical x-z axes.")
        if not np.array_equal(result.r, reference.r) or not np.array_equal(
            result.valid_mask, reference.valid_mask
        ):
            raise Fig7ApparentPlotError(
                "Fig. 7 inputs must share identical radius and validity masks."
            )
        if not np.isclose(_required_mass(result), mass, rtol=0.0, atol=1.0e-12):
            raise Fig7ApparentPlotError("Fig. 7 inputs must use one background mass.")
    return mass


def _required_mass(result: ApparentGridResult) -> float:
    try:
        value = result.metadata["config"]["background"]["M"]
    except (KeyError, TypeError) as exc:
        raise Fig7ApparentPlotError(
            "Fig. 7 source metadata missing config.background.M."
        ) from exc
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Fig7ApparentPlotError("Fig. 7 source config.background.M must be numeric.")
    mass = float(value)
    if not np.isfinite(mass) or mass <= 0.0:
        raise Fig7ApparentPlotError("Fig. 7 source config.background.M must be positive.")
    return mass


def _row_color_scales(
    results: list[ApparentGridResult],
) -> dict[str, tuple[float, float]]:
    maximum = max(
        max(
            float(np.max(np.abs(np.real(getattr(result, component)[result.valid_mask]))))
            for result in results
        )
        for component, _ in FIG7_COMPONENTS
    )
    if not np.isfinite(maximum):
        raise Fig7ApparentPlotError("Fig. 7 has no finite valid apparent fields.")
    common = (-FIG7_PAPER_COLOR_LIMIT, FIG7_PAPER_COLOR_LIMIT)
    return {component: common for component, _ in FIG7_COMPONENTS}


def _render_panel(
    results: list[ApparentGridResult],
    *,
    kM_values: list[float],
    row_color_scales: dict[str, tuple[float, float]],
    mass: float,
    interpolation: str,
    output_path: Path,
    dpi: int,
    output_format: str,
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise Fig7ApparentPlotError(f"matplotlib is required for Fig. 7: {exc}") from exc

    reference = results[0]
    extent = [
        float(np.min(reference.x) / mass),
        float(np.max(reference.x) / mass),
        float(np.min(reference.z) / mass),
        float(np.max(reference.z) / mass),
    ]
    figure, axes = plt.subplots(
        len(FIG7_COMPONENTS),
        len(results),
        figsize=(7.1, 8.3),
        dpi=dpi,
        sharex=True,
        sharey=True,
        constrained_layout=True,
    )
    for row_index, (component, label) in enumerate(FIG7_COMPONENTS):
        vmin, vmax = row_color_scales[component]
        image = None
        for column_index, (result, kM) in enumerate(
            zip(results, kM_values, strict=True)
        ):
            axis = axes[row_index, column_index]
            values = np.real(getattr(result, component))
            masked_values = np.ma.array(
                values,
                mask=(~result.valid_mask) | (~np.isfinite(values)),
            )
            image = axis.imshow(
                masked_values,
                origin="lower",
                aspect="equal",
                extent=extent,
                cmap="viridis",
                vmin=vmin,
                vmax=vmax,
                interpolation=interpolation,
            )
            _draw_overlays(axis)
            if row_index == 0:
                axis.set_title(rf"$kM={kM:g}$", fontsize=8, pad=2)
            if column_index == 0:
                axis.set_ylabel(label + "\n" + r"$z/M$", fontsize=7)
            if row_index == len(FIG7_COMPONENTS) - 1:
                axis.set_xlabel(r"$x/M$", fontsize=7)
            axis.tick_params(axis="both", which="major", labelsize=6, pad=1)
            axis.spines["top"].set_visible(False)
            axis.spines["right"].set_visible(False)
        if image is not None:
            colorbar = figure.colorbar(
                image,
                ax=axes[row_index, :].ravel().tolist(),
                fraction=0.026,
                pad=0.012,
            )
            colorbar.set_label(label, fontsize=7)
            colorbar.ax.tick_params(labelsize=6, pad=1)
    figure.savefig(output_path, format=output_format, dpi=dpi)
    plt.close(figure)


def _draw_overlays(axis: Any) -> None:
    from matplotlib.patches import Circle

    axis.add_patch(
        Circle(
            (0.0, 0.0),
            3.0,
            facecolor="0.60",
            edgecolor="none",
            zorder=4,
        )
    )
    axis.add_patch(Circle((0.0, 0.0), 2.0, color="black", zorder=5))


def _source_record(path: Path, result: ApparentGridResult, kM: float) -> dict[str, Any]:
    return {
        "path": str(path),
        "sha256": _file_sha256(path),
        "size_bytes": path.stat().st_size,
        "case_id": result.metadata.get("case_id"),
        "kM": kM,
        "physical_claim": result.metadata.get("physical_claim"),
    }


def _render_common_metadata(
    *,
    source_records: list[dict[str, Any]],
    kM_values: list[float],
    row_color_scales: dict[str, tuple[float, float]],
    mass: float,
    created_by_cli: bool,
) -> dict[str, Any]:
    return {
        "schema_version": FIG7_RENDERER_SCHEMA,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by_cli": bool(created_by_cli),
        "plot_type": "fig7_apparent_four_frequency",
        "physical_claim": False,
        "no_solver_rerun": True,
        "quantity": "real",
        "components": [component for component, _ in FIG7_COMPONENTS],
        "kM_values": kM_values,
        "source_inputs": source_records,
        "row_color_scales": {
            component: {"vmin": limits[0], "vmax": limits[1]}
            for component, limits in row_color_scales.items()
        },
        "coordinates": {"x": "x/M", "z": "z/M", "background_mass": mass},
        "overlays": {
            "event_horizon": {"radius_over_M": 2.0, "style": "black filled"},
            "light_ring": {"radius_over_M": 3.0, "style": "gray filled disk"},
        },
        "display_policy": {
            "fixed_paper_color_limit": FIG7_PAPER_COLOR_LIMIT,
            "color_clipping_is_display_only": True,
            "interpolation_is_display_only": True,
            "physical_data_modified": False,
            "numerical_audit_interpolation": "nearest",
        },
    }


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


__all__ = [
    "EXPECTED_KM_VALUES",
    "FIG7_COMPONENTS",
    "Fig7ApparentArtifacts",
    "Fig7ApparentPlotError",
    "render_fig7_apparent_four_frequency",
]
