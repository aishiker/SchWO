#!/usr/bin/env python3
"""Check, publish once, or reload the Phase-6 V2 selected-domain release."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from schwgw.validation.phase6_v2_selected_release import (
    build_release_ledger,
    build_release_summary,
    fresh_output_root,
    publish_selected_release,
    validate_in_temporary_copy,
    validate_published_selected_release,
    verify_release_inputs,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action", choices=("check-only", "publish", "reload"), help="operation"
    )
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--timestamp")
    parser.add_argument(
        "--verification-json",
        default="{}",
        help="verification metadata supplied after all prepublication checks",
    )
    parser.add_argument(
        "--temporary-copy-reload",
        action="store_true",
        help="also reload from a distinct temporary filesystem location",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    project = args.project_root.resolve()
    if args.action == "check-only":
        gate = verify_release_inputs(project, require_dispatch_review_identity=False)
        ledger = build_release_ledger(gate)
        summary = build_release_summary(ledger)
        print(
            json.dumps(
                {
                    "action": "check-only",
                    "certificate_count": len(ledger["certificates"]),
                    "certificate_state_counts": ledger["certificate_state_counts"],
                    "global_status": summary["global_status"],
                    "radial_solve_count": summary["radial_solve_count"],
                    "t7_handoff_sha256": gate.t7_identity["sha256"],
                },
                sort_keys=True,
            )
        )
        return 0

    output = args.output_root
    if output is None:
        if args.action == "reload":
            raise SystemExit("reload requires --output-root")
        output = fresh_output_root(project, args.timestamp)
    output = output.resolve()

    if args.action == "publish":
        bundle = publish_selected_release(
            project, output, verification=json.loads(args.verification_json)
        )
    else:
        bundle = validate_published_selected_release(output, project)
    if args.temporary_copy_reload:
        validate_in_temporary_copy(output, project)
    print(
        json.dumps(
            {
                "action": args.action,
                "output_root": str(output),
                "certificate_count": bundle["summary"]["certificate_count"],
                "terminal_decision": bundle["summary"]["terminal_decision"],
                "global_status": bundle["summary"]["global_status"],
                "radial_solve_count": bundle["summary"]["radial_solve_count"],
                "temporary_copy_reload": args.temporary_copy_reload,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
