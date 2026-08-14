#!/usr/bin/env python3
"""Build the solver-free matched Schwarzschild Fig. 8 data product."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from schwgw.io.asymptotic import (
    build_fig8_matched_dataset,
    load_fig8_asymptotic_dataset,
    save_fig8_asymptotic_dataset,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--output-lmax", type=int, default=502)
    parser.add_argument("--target-lmax", type=int, default=500)
    parser.add_argument("--overlap-half-width", type=int, default=15)
    args = parser.parse_args(argv)
    raw = load_fig8_asymptotic_dataset(args.raw)
    sidecar = args.raw.with_suffix(".json")
    source_record = {
        "path": str(args.raw.resolve()),
        "sha256": _sha256(args.raw),
        "sidecar_path": str(sidecar.resolve()),
        "sidecar_sha256": _sha256(sidecar),
    }
    result = build_fig8_matched_dataset(
        raw,
        output_lmax=args.output_lmax,
        target_lmax=args.target_lmax,
        overlap_half_width=args.overlap_half_width,
        source_record=source_record,
    )
    save_fig8_asymptotic_dataset(result, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
