#!/usr/bin/env python3
"""Compare terminal BHPT-direct and conditioned-radial 30-key evidence.

The command is a strict evidence consumer.  It never invokes a radial solver
and never fits a phase or normalization.  Use ``--check-only`` for a no-write
preflight or ``--output-root`` for one fresh immutable formal publication.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

from schwgw.validation.phase6_bhpt_direct_comparison import (
    BHPTConditionedComparisonError,
    preflight_bhpt_conditioned_comparison,
    publish_bhpt_conditioned_comparison,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comparison-id", required=True)
    parser.add_argument("--bhpt-root", required=True, type=Path)
    parser.add_argument("--conditioning-campaign-root", required=True, type=Path)
    parser.add_argument(
        "--shard-root",
        action="append",
        required=True,
        type=Path,
        help="One conditioning shard root; repeat exactly eight times.",
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--check-only",
        action="store_true",
        help="Strictly reload and compare without writing any output.",
    )
    action.add_argument(
        "--output-root",
        type=Path,
        help="Fresh absent absolute root for one immutable publication.",
    )
    args = parser.parse_args(argv)
    if len(args.shard_root) != 8:
        parser.error("--shard-root must be repeated exactly eight times")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    keyword = {
        "comparison_id": args.comparison_id,
        "bhpt_root": args.bhpt_root,
        "conditioning_campaign_root": args.conditioning_campaign_root,
        "conditioning_shard_roots": args.shard_root,
    }
    try:
        if args.check_only:
            result = preflight_bhpt_conditioned_comparison(**keyword)
        else:
            result = publish_bhpt_conditioned_comparison(
                args.output_root,
                **keyword,
            )
    except (BHPTConditionedComparisonError, FileExistsError, OSError) as exc:
        print(
            json.dumps(
                {
                    "global_green_permitted": False,
                    "reason": f"{type(exc).__name__}: {exc}",
                    "status": "FAIL_CLOSED_NO_RETRY",
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
