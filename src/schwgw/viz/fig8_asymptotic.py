"""Read-only journal renderer for the four-panel Fig. 8 dataset."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import numpy as np

from schwgw.io.asymptotic import (
    FIG8_KM_VALUES,
    Fig8AsymptoticDataset,
    load_fig8_asymptotic_dataset,
)


FIG8_RENDERER_SCHEMA = "schwgw_fig8_asymptotic_renderer_v1"


class Fig8AsymptoticPlotError(ValueError):
    """Raised when a Fig. 8 dataset is not safe to render."""


@dataclass(frozen=True)
class Fig8AsymptoticArtifacts:
    pdf: Path
    png: Path
    manifest: Path


def render_fig8_asymptotic_four_frequency(
    dataset_path: str | Path,
    *,
    output_dir: str | Path,
    basename: str = "fig8_asymptotic_four_frequency",
    created_by_cli: bool = False,
) -> Fig8AsymptoticArtifacts:
    """Render q=0,1,2 curves from one saved dataset without a solver rerun.

    The forward axis is not inserted, extrapolated, cropped, or smoothed: it
    remains absent because the dataset contract stores only ``theta > 0``.
    """

    if not basename or Path(basename).name != basename:
        raise Fig8AsymptoticPlotError("basename must be a non-empty filename stem.")
    source = Path(dataset_path)
    dataset = load_fig8_asymptotic_dataset(source)
    _validate_render_input(dataset)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    pdf = output / f"{basename}.pdf"
    png = output / f"{basename}.png"
    manifest = output / f"{basename}.manifest.json"
    sidecars = (pdf.with_suffix(".pdf.json"), png.with_suffix(".png.json"))
    if any(path.exists() for path in (pdf, png, manifest, *sidecars)):
        raise FileExistsError(
            "Refusing to overwrite an existing Fig. 8 render artifact."
        )

    import matplotlib.pyplot as plt

    figure, axes = plt.subplots(
        1, 4, figsize=(11.4, 3.05), sharey=True, constrained_layout=True
    )
    x = dataset.theta / np.pi
    styles = (
        {
            "color": "#2166ac",
            "linestyle": "None",
            "marker": ".",
            "markersize": 2.2,
            "label": "q=0",
        },
        {"color": "#1b9e77", "linestyle": "--", "linewidth": 1.2, "label": "q=1"},
        {"color": "#d73027", "linestyle": "-", "linewidth": 1.35, "label": "q=2"},
    )
    handles = []
    for index, (axis, kM) in enumerate(zip(axes, FIG8_KM_VALUES, strict=True)):
        for order_index, style in enumerate(styles):
            line = axis.plot(
                x, dataset.differential_cross_section[index, order_index], **style
            )[0]
            if index == 0:
                handles.append(line)
        axis.text(0.43, 0.79, rf"$k={kM:g}/M$", transform=axis.transAxes)
        axis.set_xlabel(r"$\theta/\pi$")
        axis.set_xlim(0.1, 1.0)
        axis.set_ylim(0.0, 105.0)
        axis.grid(color="0.75", linewidth=0.55, alpha=0.65)
    axes[0].set_ylabel(r"$M^{-2}(\mathrm{d}\sigma/\mathrm{d}\Omega)$")
    figure.legend(
        handles,
        ["0-th", "1-st", "2-nd"],
        loc="outside upper center",
        ncol=3,
        frameon=True,
    )
    _atomic_save_figure(figure, pdf, format="pdf")
    _atomic_save_figure(figure, png, format="png", dpi=600)
    plt.close(figure)

    source_record = {
        "path": str(source.resolve()),
        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "metadata_sidecar_sha256": hashlib.sha256(
            source.with_suffix(".json").read_bytes()
        ).hexdigest(),
    }
    common = {
        "schema_version": FIG8_RENDERER_SCHEMA,
        "figure": 8,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by_cli": created_by_cli,
        "no_solver_rerun": True,
        "source_input": source_record,
        "kM_values": list(FIG8_KM_VALUES),
        "styles": {"q0": "blue dots", "q1": "green dashed", "q2": "red solid"},
        "forward_axis": {
            "theta_zero_present": False,
            "masked_or_missing": True,
            "cropped": False,
            "smoothed": False,
        },
        "display_window": {
            "theta_over_pi": [0.1, 1.0],
            "cross_section_M_minus_2": [0.0, 105.0],
            "display_clipping_only": True,
        },
    }
    _atomic_write_json(
        pdf.with_suffix(".pdf.json"),
        {**common, "artifact": {"path": str(pdf), "format": "pdf"}},
    )
    _atomic_write_json(
        png.with_suffix(".png.json"),
        {**common, "artifact": {"path": str(png), "format": "png", "dpi": 600}},
    )
    _atomic_write_json(
        manifest,
        {
            **common,
            "artifacts": [
                str(pdf),
                str(png),
                str(pdf.with_suffix(".pdf.json")),
                str(png.with_suffix(".png.json")),
            ],
        },
    )
    return Fig8AsymptoticArtifacts(pdf=pdf, png=png, manifest=manifest)


def _validate_render_input(dataset: Fig8AsymptoticDataset) -> None:
    if not np.array_equal(dataset.kM, np.asarray(FIG8_KM_VALUES)):
        raise Fig8AsymptoticPlotError("Fig. 8 dataset has an invalid kM order.")
    if np.any(dataset.theta <= 0.0):
        raise Fig8AsymptoticPlotError("Fig. 8 forward theta=0 must be absent/masked.")
    if np.any(~np.isfinite(dataset.differential_cross_section)):
        raise Fig8AsymptoticPlotError(
            "Fig. 8 cross sections must be finite for rendering."
        )


def _atomic_save_figure(figure: Any, output: Path, **kwargs: Any) -> None:
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{output.name}.",
            suffix=".partial",
            dir=output.parent,
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
        figure.savefig(temporary, **kwargs)
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(temporary, output)
        temporary = None
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _atomic_write_json(output: Path, payload: dict[str, Any]) -> None:
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix=f".{output.name}.",
            suffix=".partial",
            dir=output.parent,
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            json.dump(payload, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, output)
        temporary = None
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


__all__ = [
    "Fig8AsymptoticArtifacts",
    "Fig8AsymptoticPlotError",
    "render_fig8_asymptotic_four_frequency",
]
