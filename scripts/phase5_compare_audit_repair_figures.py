#!/usr/bin/env python3
"""Create source-bound paper/new-render comparison sheets for Figs. 3--8."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
from PIL import Image


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sheet(
    *,
    paper_page: Path,
    crop: tuple[int, int, int, int],
    reproduction: Path,
    output: Path,
    title: str,
) -> None:
    paper = Image.open(paper_page).convert("RGB").crop(crop)
    new = Image.open(reproduction).convert("RGB")
    figure, axes = plt.subplots(2, 1, figsize=(12.0, 8.8), constrained_layout=True)
    axes[0].imshow(paper)
    axes[0].set_title(f"{title}: Li--Hou--Zhao published raster")
    axes[1].imshow(new)
    axes[1].set_title(f"{title}: SchWO audited repair")
    for axis in axes:
        axis.set_axis_off()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(figure)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-page9", type=Path, required=True)
    parser.add_argument("--paper-page10", type=Path, required=True)
    parser.add_argument("--paper-page14", type=Path, required=True)
    parser.add_argument("--paper-page15", type=Path, required=True)
    parser.add_argument("--render-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    inputs = {
        "fig3": (
            args.paper_page9,
            (110, 115, 1570, 895),
            args.render_dir
            / "figure3"
            / "fig3_direct_curvature_bilinear_600dpi.png",
        ),
        "fig4": (
            args.paper_page9,
            (105, 930, 1585, 1615),
            args.render_dir
            / "figure4"
            / "fig4_exact_asymptotic_q2_comparison_600dpi.png",
        ),
        "fig5": (
            args.paper_page10,
            (130, 110, 1570, 775),
            args.render_dir / "figure5_figure6" / "fig5_near_axis_uniform40.png",
        ),
        "fig6": (
            args.paper_page10,
            (130, 920, 1570, 1570),
            args.render_dir / "figure5_figure6" / "fig6_far_axis_uniform40.png",
        ),
        "fig7": (
            args.paper_page14,
            (115, 100, 1580, 1530),
            args.render_dir
            / "figure7"
            / "fig7_direct_curvature_display_bilinear_600dpi.png",
        ),
        "fig8": (
            args.paper_page15,
            (140, 900, 1590, 1470),
            args.render_dir / "figure8" / "fig8_direct_mst.png",
        ),
    }
    missing = [
        str(path)
        for page, _, reproduction in inputs.values()
        for path in (page, reproduction)
        if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError(f"missing comparison input: {missing}")
    if args.output_dir.exists():
        raise FileExistsError(f"refusing comparison collision: {args.output_dir}")
    args.output_dir.mkdir(parents=True)
    records = []
    for figure, (page, crop, reproduction) in inputs.items():
        output = args.output_dir / f"{figure}_published_vs_audited_repair.png"
        if output.exists():
            raise FileExistsError(f"refusing comparison collision: {output}")
        _sheet(
            paper_page=page,
            crop=crop,
            reproduction=reproduction,
            output=output,
            title=figure.upper(),
        )
        records.append(
            {
                "figure": figure,
                "published_page": str(page),
                "published_page_sha256": _sha256(page),
                "crop_pixels": list(crop),
                "reproduction": str(reproduction),
                "reproduction_sha256": _sha256(reproduction),
                "comparison": str(output),
                "comparison_sha256": _sha256(output),
            }
        )
    (args.output_dir / "comparison_manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "schwgw_audit_repairs_paper_comparison_v1",
                "records": records,
                "claim": (
                    "visual panel comparison only; published raw numerical data "
                    "were unavailable"
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"event": "audit_repair_comparisons_complete"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
