#!/usr/bin/env python3
"""Generate the four diagnostic Li-Hou-Zhao Fig. 7 x-z datasets."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys

from schwgw.io import load_config
from schwgw.io.apparent import run_apparent_solver_grid, save_apparent_results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("configs", nargs="+", type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="validate configs and planned paths without running any solver",
    )
    args = parser.parse_args(argv)
    if len(args.configs) != 4:
        parser.error("Fig. 7 production requires exactly four frequency configs.")

    planned: list[tuple[object, Path]] = []
    seen_frequencies: set[float] = set()
    for config_path in args.configs:
        source = load_config(config_path)
        if source.observer.kind != "xz_plane":
            raise ValueError(f"Expected xz_plane config: {config_path}")
        if source.wave.kM in seen_frequencies:
            raise ValueError(f"Duplicate kM={source.wave.kM:g}")
        seen_frequencies.add(source.wave.kM)
        token = f"{source.wave.kM:g}".replace(".", "p")
        case_id = source.case_id.replace("FIG3", "FIG7_APPARENT")
        output = args.out_dir / f"fig7_apparent_kM_{token}_dx0p25.npz"
        planned.append((replace(source, case_id=case_id, output=str(output)), output))
    if seen_frequencies != {0.5, 1.0, 1.5, 2.0}:
        raise ValueError("Fig. 7 frequencies must be exactly {0.5,1.0,1.5,2.0}.")
    collisions = [str(path) for _, path in planned if path.exists()]
    if collisions:
        raise FileExistsError(f"Refusing output collisions: {collisions}")
    if args.preflight:
        print(
            json.dumps(
                {
                    "event": "fig7_preflight_passed",
                    "outputs": [str(path) for _, path in planned],
                },
                sort_keys=True,
            )
        )
        return 0

    args.out_dir.mkdir(parents=True, exist_ok=True)
    source_command = [sys.executable, *sys.argv]
    for config, output in planned:
        result = run_apparent_solver_grid(
            config,  # type: ignore[arg-type]
            source_command=source_command,
            progress=lambda record: print(json.dumps(record, sort_keys=True), flush=True),
        )
        save_apparent_results(result, output)
        print(
            json.dumps(
                {
                    "event": "fig7_frequency_complete",
                    "kM": config.wave.kM,  # type: ignore[union-attr]
                    "output": str(output),
                },
                sort_keys=True,
            ),
            flush=True,
        )
    print("fig7_apparent_four_frequency_production_passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
