#!/usr/bin/env python3
"""Phase-6 V3.1-U preflight, sentinel, official, and reload CLI."""

from __future__ import annotations

import argparse
from pathlib import Path

from schwgw.validation.phase6_v3_mode_greybody_hp_replacement import (
    run_official,
    run_preexecution_sentinels,
    validate_import_isolation,
    validate_official_candidate,
    verify_start_gate,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("preflight")
    sentinel = commands.add_parser("sentinels")
    sentinel.add_argument("--output", type=Path, required=True)
    official = commands.add_parser("official")
    official.add_argument("--output-root", type=Path, required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "preflight":
        verify_start_gate()
        validate_import_isolation()
        print("v3_1_u_preflight=PASS")
        return 0
    if args.command == "sentinels":
        result = run_preexecution_sentinels(args.output)
        print(result["resource_projection"]["projected_runtime_seconds_conservative"])
        return 0
    if args.command == "official":
        result = run_official(args.output_root)
        print(result["manifest"]["sha256"])
        return 0
    validate_official_candidate(args.root)
    print("v3_1_u_candidate=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
