#!/usr/bin/env python3
"""Generate direct-MST phase transactions and the final Fig. 8 dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from schwgw.io.fig8_mst import (
    DEFAULT_RAW,
    Fig8MSTError,
    finalize_fig8_mst_frequency,
    merge_fig8_mst_dataset,
    produce_fig8_mst_frequency,
)


def _progress(record: dict) -> None:
    print(json.dumps(record, sort_keys=True), flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    produce = subparsers.add_parser("produce")
    produce.add_argument("--kM", type=float, required=True)
    produce.add_argument("--output-dir", type=Path, required=True)
    produce.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    finalize = subparsers.add_parser("finalize")
    finalize.add_argument("--kM", type=float, required=True)
    finalize.add_argument("--output-dir", type=Path, required=True)
    finalize.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    merge = subparsers.add_parser("merge")
    merge.add_argument("--transaction-dir", type=Path, required=True)
    merge.add_argument("--output", type=Path, required=True)
    merge.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    args = parser.parse_args(argv)
    try:
        if args.action == "produce":
            npz, sidecar = produce_fig8_mst_frequency(
                kM=args.kM,
                output_dir=args.output_dir,
                raw_path=args.raw,
                progress=_progress,
            )
            _progress(
                {
                    "event": "fig8_direct_mst_frequency_complete",
                    "kM": args.kM,
                    "npz": str(npz),
                    "sidecar": str(sidecar),
                }
            )
        elif args.action == "finalize":
            npz, sidecar = finalize_fig8_mst_frequency(
                kM=args.kM,
                output_dir=args.output_dir,
                raw_path=args.raw,
            )
            _progress(
                {
                    "event": "fig8_direct_mst_frequency_finalized",
                    "kM": args.kM,
                    "npz": str(npz),
                    "sidecar": str(sidecar),
                    "science_recomputed": False,
                }
            )
        else:
            npz, sidecar = merge_fig8_mst_dataset(
                transaction_dir=args.transaction_dir,
                output_path=args.output,
                raw_path=args.raw,
            )
            _progress(
                {
                    "event": "fig8_direct_mst_merge_complete",
                    "npz": str(npz),
                    "sidecar": str(sidecar),
                }
            )
    except Fig8MSTError as exc:
        print(f"Fig. 8 direct MST production error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
