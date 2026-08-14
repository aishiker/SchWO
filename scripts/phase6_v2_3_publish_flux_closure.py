#!/usr/bin/env python3
"""Check, publish once, or reload Phase-6 V2.3 flux-closure evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from schwgw.validation.phase6_v2_flux_closure import (
    build_v2_3_flux_closure_records,
    fresh_output_root,
    publish_v2_3_flux_closure,
    validate_in_temporary_copy,
    validate_published_v2_3_flux_closure,
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
        help="canonical verification metadata supplied after all prepublish checks",
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
        records, gate = build_v2_3_flux_closure_records(
            project, require_dispatch_review_identity=False
        )
        print(
            json.dumps(
                {
                    "action": "check-only",
                    "record_count": len(records),
                    "mandatory_predicates_passed": all(
                        record["mandatory_predicates_passed"] for record in records
                    ),
                    "radial_solve_count": 0,
                    "working_dps": records[0]["precision"]["working_dps"],
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
        verification = json.loads(args.verification_json)
        bundle = publish_v2_3_flux_closure(project, output, verification=verification)
    else:
        bundle = validate_published_v2_3_flux_closure(output, project)

    if args.temporary_copy_reload:
        validate_in_temporary_copy(output, project)
    print(
        json.dumps(
            {
                "action": args.action,
                "output_root": str(output),
                "record_count": len(bundle["records"]),
                "terminal_decision": bundle["summary"]["terminal_decision"],
                "radial_solve_count": bundle["summary"]["radial_solve_count"],
                "manifest_sha256": bundle["manifest"]["artifacts"][0]["sha256"],
                "temporary_copy_reload": args.temporary_copy_reload,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
