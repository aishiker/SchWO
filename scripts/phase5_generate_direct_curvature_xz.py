#!/usr/bin/env python3
"""Generate paired direct-curvature Fig. 3/Fig. 7 x-z artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

from schwgw.io import (
    load_config,
    run_direct_curvature_xz_grids,
    save_apparent_results,
    save_results,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if config.observer.kind != "xz_plane":
        raise ValueError("direct-curvature Fig. 3/7 production requires xz_plane.")
    token = f"{config.wave.kM:g}".replace(".", "p")
    physical = args.output_dir / f"fig3_direct_curvature_kM_{token}.npz"
    apparent = args.output_dir / f"fig7_direct_curvature_kM_{token}.npz"
    manifest = args.output_dir / f"direct_curvature_kM_{token}.manifest.json"
    collisions = [str(path) for path in (physical, apparent, manifest) if path.exists()]
    if collisions:
        raise FileExistsError(f"refusing output collisions: {collisions}")
    if args.preflight:
        print(
            json.dumps(
                {
                    "event": "direct_curvature_xz_preflight_passed",
                    "config": str(args.config),
                    "kM": config.wave.kM,
                    "outputs": [str(physical), str(apparent), str(manifest)],
                },
                sort_keys=True,
            )
        )
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, *sys.argv]
    pair = run_direct_curvature_xz_grids(
        config,
        source_command=command,
        progress=lambda record: print(json.dumps(record, sort_keys=True), flush=True),
    )
    physical_temporary = physical.with_name(f".{physical.name}.partial.npz")
    if physical_temporary.exists():
        raise FileExistsError(f"refusing temporary collision: {physical_temporary}")
    save_results(pair.physical, physical_temporary)
    with physical_temporary.open("rb") as handle:
        os.fsync(handle.fileno())
    os.replace(physical_temporary, physical)
    save_apparent_results(pair.apparent, apparent)
    directory_fd = os.open(args.output_dir, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    payload = {
        "schema_version": "li_hou_zhao_direct_curvature_xz_pair_v1",
        "kM": config.wave.kM,
        "config": str(args.config),
        "config_sha256": _sha256(args.config),
        "polarization_bridge": (
            "RW-gauge metric -> linearized Riemann -> incident-frame projection"
        ),
        "strict_np_lower_scalar_completion": False,
        "artifacts": {
            "figure3": {"path": str(physical), "sha256": _sha256(physical)},
            "figure7": {"path": str(apparent), "sha256": _sha256(apparent)},
        },
    }
    manifest.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with manifest.open("rb") as handle:
        os.fsync(handle.fileno())
    print(
        json.dumps(
            {
                "event": "direct_curvature_xz_complete",
                "kM": config.wave.kM,
                "manifest": str(manifest),
                "manifest_sha256": _sha256(manifest),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
