#!/usr/bin/env python3
"""Phase-6 V3.1 cycle-2 preflight, sentinel and official producer CLI."""

from __future__ import annotations

import argparse
from pathlib import Path

from schwgw.validation.phase6_v3_mode_greybody import (
    build_inventory_payload,
    probe_external_runtime,
    publish_external_blocker_candidate,
    run_external_smoke,
    run_official_candidate,
    validate_blocker_candidate,
    validate_terminal_candidate,
    verify_frozen_inputs,
)
from schwgw.validation.phase6_v3_mode_greybody_cycle2 import (
    publish_synthetic_root,
    run_preexecution_sentinels,
    run_official_cycle2,
    validate_official_candidate,
    verify_cycle2_start_gate,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("preflight")
    smoke = subparsers.add_parser("external-smoke")
    smoke.add_argument("--output", type=Path, required=True)
    publish = subparsers.add_parser("publish-external-blocker")
    publish.add_argument("--output-root", type=Path, required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("--root", type=Path, required=True)
    run = subparsers.add_parser("run")
    run.add_argument("--output-root", type=Path, required=True)
    synthetic = subparsers.add_parser("cycle2-synthetic")
    synthetic.add_argument("--output-root", type=Path, required=True)
    official = subparsers.add_parser("cycle2-official")
    official.add_argument("--output-root", type=Path, required=True)
    validate_cycle2 = subparsers.add_parser("cycle2-validate")
    validate_cycle2.add_argument("--root", type=Path, required=True)
    subparsers.add_parser("cycle2-preflight")
    sentinels = subparsers.add_parser("cycle2-sentinels")
    sentinels.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "preflight":
        verify_frozen_inputs()
        inventory = build_inventory_payload()
        external = probe_external_runtime()
        print(
            f"route_a={inventory['route_a_mode_count']} route_b={inventory['route_b_mode_count']} route_c={inventory['route_c_mode_count']} external_available={external['available']}"
        )
        return 0
    if args.command == "publish-external-blocker":
        result = publish_external_blocker_candidate(args.output_root)
        print(result["root"])
        return 0
    if args.command == "external-smoke":
        result = run_external_smoke(args.output)
        print(result["wolfram_version"])
        return 0
    if args.command == "run":
        result = run_official_candidate(args.output_root)
        print(result["blocker"])
        return 2
    if args.command == "cycle2-preflight":
        verify_cycle2_start_gate()
        print("cycle2_start_gate=PASS")
        return 0
    if args.command == "cycle2-synthetic":
        result = publish_synthetic_root(args.output_root)
        print(result["manifest"]["sha256"])
        return 0
    if args.command == "cycle2-sentinels":
        result = run_preexecution_sentinels(args.output)
        print(result["resource_projection"]["projected_total_seconds"])
        return 0
    if args.command == "cycle2-official":
        result = run_official_cycle2(args.output_root)
        print(result["manifest"]["sha256"])
        return 0
    if args.command == "cycle2-validate":
        validate_official_candidate(args.root)
        print("cycle2_candidate=PASS")
        return 0
    try:
        validate_terminal_candidate(args.root)
    except Exception:
        validate_blocker_candidate(args.root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
