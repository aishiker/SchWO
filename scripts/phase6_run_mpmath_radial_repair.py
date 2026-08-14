#!/usr/bin/env python3
"""Plan, benchmark, or resume the Phase-6 mpmath radial repair campaign."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from schwgw.validation.phase6_mpmath_radial_repair import (
    APRadialRepairError,
    build_repair_plan,
    run_repair_campaign,
)


ROOT = Path(__file__).resolve().parents[1]
RADIAL_VALIDATION_ROOT = ROOT / "runs/phase6/radial_validation"
DEFAULT_CONDITIONING_ROOT = (
    RADIAL_VALIDATION_ROOT / "v1_conditioning_campaign_v1_20260808_py314"
)
MODULE_PATH = (ROOT / "src/schwgw/validation/phase6_mpmath_radial_repair.py").resolve(
    strict=True
)
SCRIPT_PATH = Path(__file__).resolve(strict=True)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the isolated arbitrary-precision selected-anchor radial repair. "
            "A campaign kind must be explicitly selected."
        )
    )
    kind = parser.add_mutually_exclusive_group(required=True)
    kind.add_argument(
        "--benchmark-two",
        action="store_true",
        help="run only the frozen two-anchor timing benchmark",
    )
    kind.add_argument(
        "--full-selected-repair",
        action="store_true",
        help="run the frozen 24-anchor repair (requires explicit opt-in)",
    )
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--conditioning-campaign-root",
        type=Path,
        default=DEFAULT_CONDITIONING_ROOT,
    )
    parser.add_argument("--output-root", type=Path)
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="validate source/runtime/selection and print the plan without writing",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="resume an existing mode-0700 partial root with the identical plan",
    )
    return parser


def _validated_output(path: Path | None, *, plan_only: bool) -> Path | None:
    if plan_only:
        if path is not None:
            raise APRadialRepairError("--plan-only does not accept --output-root")
        return None
    if path is None:
        raise APRadialRepairError("an execution requires --output-root")
    output = path.absolute()
    parent = RADIAL_VALIDATION_ROOT.resolve(strict=True)
    if output.parent.resolve(strict=True) != parent:
        raise APRadialRepairError(
            "repair output must be a direct child of runs/phase6/radial_validation"
        )
    return output


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not re.fullmatch(r"[a-z0-9][a-z0-9_]{2,95}", args.run_id):
        raise APRadialRepairError("run ID must be 3-96 lowercase alphanumeric/_ chars")
    if args.plan_only and args.resume:
        raise APRadialRepairError("--plan-only cannot be combined with --resume")
    output = _validated_output(args.output_root, plan_only=args.plan_only)
    campaign_kind = (
        "FULL_SELECTED_REPAIR"
        if args.full_selected_repair
        else "TWO_ANCHOR_TIMING_BENCHMARK"
    )
    plan = build_repair_plan(
        run_id=args.run_id,
        campaign_root=args.conditioning_campaign_root,
        implementation_paths=(MODULE_PATH, SCRIPT_PATH),
        campaign_kind=campaign_kind,
    )
    if args.plan_only:
        print(json.dumps(plan, sort_keys=True, separators=(",", ":")))
        return 0
    assert output is not None
    summary = run_repair_campaign(output_root=output, plan=plan, resume=args.resume)
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
