#!/usr/bin/env python3
"""Run the bounded two-precision Phase-6 BHPT direct campaign."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from schwgw.validation.phase6_bhpt_direct_bounded import (
    BHPTBoundedDirectError,
    run_bounded_direct_campaign,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--wolfram-kernel", required=True, type=Path)
    parser.add_argument("--timeout-seconds", type=float, default=900.0)
    parser.add_argument(
        "--limit",
        type=int,
        help="Diagnostic prefix only; omitted for the exact formal 30-key domain.",
    )
    args = parser.parse_args()
    try:
        return run_bounded_direct_campaign(
            output_root=args.output_root,
            package_root=args.package_root,
            wolfram_kernel=args.wolfram_kernel,
            timeout_seconds=args.timeout_seconds,
            limit=args.limit,
        )
    except (BHPTBoundedDirectError, OSError) as exc:
        print(
            json.dumps(
                {
                    "global_green_permitted": False,
                    "reason": f"{type(exc).__name__}: {exc}",
                    "status": "FAIL_CLOSED",
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
