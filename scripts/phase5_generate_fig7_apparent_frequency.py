#!/usr/bin/env python3
"""Generate one no-overwrite Li-Hou-Zhao Fig. 7 frequency artifact."""

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
    parser.add_argument("config", type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args(argv)

    source = load_config(args.config)
    if source.observer.kind != "xz_plane":
        raise ValueError("Fig. 7 frequency production requires an xz_plane grid.")
    token = f"{source.wave.kM:g}".replace(".", "p")
    output = args.out_dir / f"fig7_apparent_kM_{token}_dx0p25.npz"
    config = replace(
        source,
        case_id=source.case_id.replace("FIG3", "FIG7_APPARENT"),
        output=str(output),
    )
    if output.exists():
        raise FileExistsError(f"Refusing output collision: {output}")
    if args.preflight:
        print(
            json.dumps(
                {
                    "event": "fig7_frequency_preflight_passed",
                    "kM": config.wave.kM,
                    "output": str(output),
                },
                sort_keys=True,
            )
        )
        return 0

    result = run_apparent_solver_grid(
        config,
        source_command=[sys.executable, *sys.argv],
        progress=lambda record: print(json.dumps(record, sort_keys=True), flush=True),
    )
    save_apparent_results(result, output)
    print(
        json.dumps(
            {
                "event": "fig7_frequency_complete",
                "kM": config.wave.kM,
                "output": str(output),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
