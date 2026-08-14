#!/usr/bin/env python3
"""Check, publish, or reload the bounded Phase-6 V2.1 evidence root."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from schwgw.validation.phase6_v2_mode_amplitudes import (  # noqa: E402
    build_v2_1_records,
    canonical_json_bytes,
    publish_v2_1_mode_amplitudes,
    validate_published_v2_1_mode_amplitudes,
    verify_frozen_v2_1_inputs,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check", help="rehash inputs and build 120 records in memory")
    publish = subparsers.add_parser("publish", help="publish once to a fresh root")
    publish.add_argument("--output-root", type=Path, required=True)
    publish.add_argument("--verification-json", required=True)
    reload_parser = subparsers.add_parser(
        "reload", help="strictly reload a sealed root"
    )
    reload_parser.add_argument("--root", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "check":
        gate = verify_frozen_v2_1_inputs(ROOT)
        bundle = build_v2_1_records(ROOT)
        result = {
            "frozen_input_count": len(gate["hashes"]),
            "radial_solve_count": 0,
            "record_count": len(bundle.records),
            "status": "PASS",
        }
    elif args.command == "publish":
        verification = json.loads(args.verification_json)
        if not isinstance(verification, dict):
            raise TypeError("--verification-json must encode an object")
        result = publish_v2_1_mode_amplitudes(
            project_root=ROOT,
            output_root=args.output_root,
            verification=verification,
        )
    else:
        reloaded = validate_published_v2_1_mode_amplitudes(args.root)
        result = {
            "record_count": len(reloaded["records"]),
            "status": "PASS",
            "summary": reloaded["summary"],
        }
    sys.stdout.buffer.write(canonical_json_bytes(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
