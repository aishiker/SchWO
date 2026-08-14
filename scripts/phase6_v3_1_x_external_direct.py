#!/usr/bin/env python3
"""CLI for the reviewed V3.1-X external direct route."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from schwgw.validation.phase6_v3_mode_greybody_external_direct_replacement import (
    preflight_payload,
    run_official,
    run_sentinel,
    run_source_load_micro,
    validate_official,
    validate_sentinel,
)


def _dispatch_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--dispatch", type=Path, required=True)
    parser.add_argument("--dispatch-sha256", required=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("preflight")
    source_load_micro = commands.add_parser("source-load-micro-sentinel")
    _dispatch_arguments(source_load_micro)
    sentinel = commands.add_parser("sentinel")
    _dispatch_arguments(sentinel)
    official = commands.add_parser("official")
    _dispatch_arguments(official)
    validate_s = commands.add_parser("validate-sentinel")
    validate_s.add_argument("--root", type=Path, required=True)
    validate_o = commands.add_parser("validate-official")
    validate_o.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "preflight":
        print(json.dumps(preflight_payload(), sort_keys=True, separators=(",", ":")))
        return 0
    if args.command == "source-load-micro-sentinel":
        result = run_source_load_micro(args.dispatch, args.dispatch_sha256)
        print(result["manifest"]["sha256"])
        return 0
    if args.command == "sentinel":
        result = run_sentinel(args.dispatch, args.dispatch_sha256)
        print(result["manifest"]["sha256"])
        return 0
    if args.command == "official":
        result = run_official(args.dispatch, args.dispatch_sha256)
        print(result["manifest"]["sha256"])
        return 0
    if args.command == "validate-sentinel":
        validate_sentinel(args.root)
        print("v3_1_x_sentinel=PASS")
        return 0
    validate_official(args.root)
    print("v3_1_x_official=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
