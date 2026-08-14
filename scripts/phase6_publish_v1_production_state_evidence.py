#!/usr/bin/env python3
"""Publish the composed Phase-6 V1 exact-eight-radius state evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from schwgw.validation.phase6_v1_production_state_evidence import (
    V1ProductionStateEvidenceError,
    publish_production_state_evidence,
    validate_production_state_sources,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", required=True, type=Path)
    parser.add_argument("--repair-root", required=True, type=Path)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check-only", action="store_true")
    action.add_argument("--output-root", type=Path)
    args = parser.parse_args()
    try:
        if args.check_only:
            source = validate_production_state_sources(
                campaign_root=args.campaign_root, repair_root=args.repair_root
            )
            result = {
                "mode_count": len(source["production_keys"]),
                "state": "PARTIAL",
            }
        else:
            result = publish_production_state_evidence(
                campaign_root=args.campaign_root,
                repair_root=args.repair_root,
                output_root=args.output_root,
            )
    except (V1ProductionStateEvidenceError, OSError, RuntimeError, ValueError) as exc:
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
