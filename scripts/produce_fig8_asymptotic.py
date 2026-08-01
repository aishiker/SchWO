#!/usr/bin/env python3
"""Produce the fixed four-frequency Appendix-D/E Fig. 8 dataset.

Use ``--preflight`` to inspect the immutable science/output contract without
invoking any radial solver.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from schwgw.io.asymptotic import (
    FIG8_KM_VALUES,
    FIG8_REDUCTION_ORDERS,
    default_fig8_theta_grid,
    produce_fig8_asymptotic_dataset,
    save_fig8_asymptotic_dataset,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output", type=Path, help="Output .npz path (JSON sidecar is adjacent)."
    )
    parser.add_argument(
        "--lmax", type=int, required=True, help="Final ell cutoff (>=2)."
    )
    parser.add_argument(
        "--theta-count", type=int, default=720, help="Uniform samples on (0, pi]."
    )
    parser.add_argument(
        "--lmax-ladder",
        type=int,
        nargs="*",
        help="Strictly increasing ladder ending at --lmax.",
    )
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Print contract and exit without a solver call.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        theta = default_fig8_theta_grid(count=args.theta_count)
        contract = {
            "figure": 8,
            "kM_values_fixed_order": list(FIG8_KM_VALUES),
            "ell": [2, args.lmax],
            "theta": {
                "interval": "(0, pi]",
                "count": int(theta.size),
                "theta_zero_present": False,
            },
            "reduction_orders": list(FIG8_REDUCTION_ORDERS),
            "boundary": {
                "r_in_eps": 1.0e-6,
                "r_out": 300.0,
                "rtol": 1.0e-10,
                "atol": 1.0e-12,
            },
            "output_npz": str(args.output),
            "output_json": str(args.output.with_suffix(".json")),
            "preflight_zero_science": bool(args.preflight),
        }
        if args.preflight:
            print(json.dumps(contract, sort_keys=True))
            return 0
        dataset = produce_fig8_asymptotic_dataset(
            lmax=args.lmax,
            theta=theta,
            lmax_ladder=args.lmax_ladder,
            source_command=["produce_fig8_asymptotic.py", *sys.argv[1:]],
            progress=lambda event: print(
                json.dumps(event, sort_keys=True), file=sys.stderr
            ),
        )
        save_fig8_asymptotic_dataset(dataset, args.output)
    except (OSError, ValueError) as exc:
        print(f"produce_fig8_asymptotic: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
