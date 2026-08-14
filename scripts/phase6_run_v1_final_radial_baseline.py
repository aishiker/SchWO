#!/usr/bin/env python3
"""Run/resume the full D_union repaired-boundary Phase-6 V1 baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from schwgw.validation.phase6_v1_final_radial_baseline import (
    V1FinalBaselineError,
    run_final_baseline,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--limit",
        type=int,
        help="Diagnostic ordered prefix only; omit for the exact 17,818-key domain.",
    )
    args = parser.parse_args()
    try:
        return run_final_baseline(
            output_root=args.output_root,
            workers=args.workers,
            resume=args.resume,
            limit=args.limit,
        )
    except (V1FinalBaselineError, OSError, RuntimeError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "global_green_permitted": False,
                    "reason": f"{type(exc).__name__}: {exc}",
                    "status": "FAIL_CLOSED_RESUMABLE_IF_MUTABLE_ROOT",
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
