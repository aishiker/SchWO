#!/usr/bin/env python3
"""Publish the selected 30-key Phase-6 V1 radial acceptance evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from schwgw.validation.phase6_v1_radial_acceptance import (
    V1RadialAcceptanceError,
    build_selected_comparison,
    publish_selected_acceptance,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--direct-root", required=True, type=Path)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check-only", action="store_true")
    action.add_argument("--output-root", type=Path)
    args = parser.parse_args()
    try:
        if args.check_only:
            _, summary = build_selected_comparison(args.direct_root)
        else:
            summary = publish_selected_acceptance(
                direct_root=args.direct_root, output_root=args.output_root
            )
    except (V1RadialAcceptanceError, OSError, RuntimeError, ValueError) as exc:
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
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["overall_state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
