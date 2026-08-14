#!/usr/bin/env python3
"""CLI for read-only V3.1-U inspection and reviewed additive resume."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from schwgw.validation.phase6_v3_hp_unitarity_resume import (
    Authority,
    inspect_interrupted_root,
    resume_root,
    validate_resumed_candidate,
)


def _authority(args: argparse.Namespace) -> Authority:
    return Authority(
        args.implementation_approval.resolve(strict=True),
        args.implementation_approval_sha256,
        args.dispatch.resolve(strict=True),
        args.dispatch_sha256,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("--root", type=Path, required=True)
    for name in ("resume", "validate"):
        command = commands.add_parser(name)
        command.add_argument("--root", type=Path, required=True)
        command.add_argument("--implementation-approval", type=Path, required=True)
        command.add_argument("--implementation-approval-sha256", required=True)
        command.add_argument("--dispatch", type=Path, required=True)
        command.add_argument("--dispatch-sha256", required=True)
    args = parser.parse_args()
    if args.command == "inspect":
        print(json.dumps(inspect_interrupted_root(args.root), sort_keys=True))
        return 0
    authority = _authority(args)
    if args.command == "resume":
        print(json.dumps(resume_root(args.root, authority), sort_keys=True))
        return 0
    validate_resumed_candidate(args.root, authority=authority)
    print("v3_1_u_resumed_candidate=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
