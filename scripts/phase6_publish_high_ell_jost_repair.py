#!/usr/bin/env python3
"""Check or publish the Phase-6 V1 high-ell adaptive-Jost repair evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from schwgw.validation.phase6_high_ell_jost_repair import (
    DEFAULT_BOUNDARY_ROOT,
    build_repair_report,
    publish_repair_evidence,
    validate_published_repair_evidence,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--boundary-root",
        type=Path,
        default=DEFAULT_BOUNDARY_ROOT,
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check-only", action="store_true")
    mode.add_argument("--output-root", type=Path)
    mode.add_argument("--validate-root", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    runner = Path(__file__).resolve(strict=True)
    if args.check_only:
        report = build_repair_report(
            boundary_root=args.boundary_root,
            runner_path=runner,
        )
        result = {
            "mode": "CHECK_ONLY",
            "overall_state": report["overall_state"],
            "aggregate": report["aggregate"],
            "global_green_permitted": False,
        }
    elif args.output_root is not None:
        result = publish_repair_evidence(
            output_root=args.output_root,
            boundary_root=args.boundary_root,
            runner_path=runner,
        )
    else:
        result = validate_published_repair_evidence(
            args.validate_root,
            boundary_root=args.boundary_root,
            runner_path=runner,
        )
    print(json.dumps(result, allow_nan=False, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
