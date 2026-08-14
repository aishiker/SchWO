#!/usr/bin/env python3
"""Validate and publish the Phase-6 V1 selected AP evidence wrapper."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from schwgw.validation.phase6_v1_ap_selected_evidence import (
    V1APSelectedEvidenceError,
    publish_ap_selected_evidence,
    validate_ap_selected_source,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check-only", action="store_true")
    action.add_argument("--output-root", type=Path)
    args = parser.parse_args()
    try:
        if args.check_only:
            source = validate_ap_selected_source(args.source_root)
            result = {
                "anchor_count": len(source["anchors"]),
                "state": "PARTIAL",
            }
        else:
            result = publish_ap_selected_evidence(
                source_root=args.source_root, output_root=args.output_root
            )
    except (V1APSelectedEvidenceError, OSError, RuntimeError, ValueError) as exc:
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
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
