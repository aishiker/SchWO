#!/usr/bin/env python3
"""Produce and merge direct metric-curvature Fig. 5/6 Table-I data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from schwgw.io.direct_tablei import (
    DEFAULT_R_OUT_LADDER,
    DirectTableIError,
    merge_direct_tablei_uniform,
    produce_direct_tablei_uniform,
)


def _progress(record: dict) -> None:
    print(json.dumps(record, sort_keys=True), flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    produce = subparsers.add_parser("produce")
    produce.add_argument("--output-dir", type=Path, required=True)
    produce.add_argument("--frequencies", nargs="+", type=float)
    produce.add_argument("--resume", action="store_true")
    produce.add_argument(
        "--observer-frame",
        choices=("static_orthonormal", "li_literal_cartesian"),
        default="static_orthonormal",
    )
    produce.add_argument(
        "--r-out-ladder",
        nargs=3,
        type=float,
        default=DEFAULT_R_OUT_LADDER,
    )
    merge = subparsers.add_parser("merge")
    merge.add_argument("--transaction-dir", type=Path, required=True)
    merge.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == "produce":
            produce_direct_tablei_uniform(
                output_dir=args.output_dir,
                frequencies=args.frequencies,
                resume=args.resume,
                observer_frame=args.observer_frame,
                r_out_ladder=tuple(args.r_out_ladder),
                progress=_progress,
            )
        else:
            path = merge_direct_tablei_uniform(
                transaction_dir=args.transaction_dir,
                output_path=args.output,
            )
            _progress({"event": "direct_tablei_merge_complete", "path": str(path)})
    except DirectTableIError as exc:
        print(f"direct Fig. 5/6 production error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
