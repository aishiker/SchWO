#!/usr/bin/env python3
"""Compute/render Li-Hou-Zhao Figures 1 and 2 without mixing the stages."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from schwgw.paper_figures.li_hou_zhao import (
    compute_figure1_dataset,
    compute_strict_np_psi4_convergence,
    load_figure1_dataset,
    load_figure2_dataset,
    save_figure1_dataset,
    save_figure2_dataset,
    write_checksum_manifest,
)
from schwgw.paper_figures.li_hou_zhao_render import (
    render_figure1_set,
    render_figure2_reference_comparison,
    render_figure2_set,
)


def _progress(value: dict[str, object]) -> None:
    print(json.dumps(value, sort_keys=True), flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("compute-fig1", "compute-fig2"):
        child = subparsers.add_parser(name)
        child.add_argument("--output-dir", type=Path, required=True)
    for name in ("render-fig1", "render-fig2"):
        child = subparsers.add_parser(name)
        child.add_argument("--input", type=Path, required=True)
        child.add_argument("--output-dir", type=Path, required=True)
    comparison = subparsers.add_parser("render-fig2-comparison")
    comparison.add_argument("--input", type=Path, required=True)
    comparison.add_argument("--reference-image", type=Path, required=True)
    comparison.add_argument("--output-dir", type=Path, required=True)
    manifest = subparsers.add_parser("manifest")
    manifest.add_argument("--output-dir", type=Path, required=True)
    manifest.add_argument("--qa-json", type=str, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if arguments.command == "compute-fig1":
        dataset = compute_figure1_dataset(progress=_progress)
        paths = save_figure1_dataset(dataset, arguments.output_dir)
    elif arguments.command == "render-fig1":
        dataset = load_figure1_dataset(arguments.input)
        paths = render_figure1_set(dataset, arguments.output_dir)
    elif arguments.command == "compute-fig2":
        dataset = compute_strict_np_psi4_convergence(progress=_progress)
        paths = save_figure2_dataset(dataset, arguments.output_dir)
    elif arguments.command == "render-fig2":
        dataset = load_figure2_dataset(arguments.input)
        paths = render_figure2_set(dataset, arguments.output_dir)
    elif arguments.command == "render-fig2-comparison":
        dataset = load_figure2_dataset(arguments.input)
        paths = render_figure2_reference_comparison(
            dataset,
            arguments.reference_image,
            arguments.output_dir,
        )
    else:
        qa = json.loads(arguments.qa_json)
        if not isinstance(qa, dict):
            raise ValueError("--qa-json must encode an object.")
        paths = (write_checksum_manifest(arguments.output_dir, qa=qa),)
    print(json.dumps({"outputs": [str(path) for path in paths]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
