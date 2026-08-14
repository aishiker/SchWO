#!/usr/bin/env python3
"""Publish the derived Phase-6 V0 verification from four check reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from schwgw.validation.phase6_v0_verification import (
    preflight_v0_verification,
    publish_v0_verification,
)


REPORT_ARGUMENTS = {
    "full_test_suite": "--full-test-suite-report",
    "legacy_np_isolation": "--legacy-np-isolation-report",
    "legacy_pseudoinverse_isolation": "--legacy-pseudoinverse-isolation-report",
    "stale_production_metadata": "--stale-production-metadata-report",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verification-id", required=True)
    for flag in REPORT_ARGUMENTS.values():
        parser.add_argument(flag, type=Path, required=True)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="derive and validate without creating an output path",
    )
    args = parser.parse_args(argv)
    report_paths = {
        check_id: getattr(args, flag.removeprefix("--").replace("-", "_"))
        for check_id, flag in REPORT_ARGUMENTS.items()
    }
    if args.check_only:
        if args.output_root is not None:
            parser.error("--check-only cannot be combined with --output-root")
        result = preflight_v0_verification(args.verification_id, report_paths)
    else:
        if args.output_root is None:
            parser.error("--output-root is required unless --check-only is used")
        result = publish_v0_verification(
            args.verification_id,
            report_paths,
            args.output_root,
        )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
