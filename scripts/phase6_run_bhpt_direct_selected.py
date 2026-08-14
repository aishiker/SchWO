#!/usr/bin/env python3
"""Run the frozen 30-key external BHPT direct-integration calibration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from schwgw.validation.phase6_bhpt_direct import (
    BHPTDirectContractError,
    run_selected_direct,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help=(
            "Fresh, absent output directory; every terminal outcome is sealed as "
            "an immutable formal evidence root."
        ),
    )
    parser.add_argument(
        "--package-root",
        type=Path,
        required=True,
        help=(
            "Exact git checkout of BlackHolePerturbationToolkit/ReggeWheeler at "
            "the frozen upstream commit."
        ),
    )
    parser.add_argument(
        "--wolfram-kernel",
        default="WolframKernel",
        help="WolframKernel executable or absolute path; no alternate solver is used.",
    )
    parser.add_argument("--timeout-seconds", type=float, default=86400.0)
    args = parser.parse_args(argv)
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")
    try:
        return run_selected_direct(
            output_dir=args.output_dir,
            package_root=args.package_root,
            wolfram_kernel=args.wolfram_kernel,
            timeout_seconds=args.timeout_seconds,
        )
    except BHPTDirectContractError as exc:
        print(
            json.dumps(
                {
                    "status": "FAIL",
                    "reason": str(exc),
                    "internal_solver_fallback_used": False,
                    "global_green_permitted": False,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
