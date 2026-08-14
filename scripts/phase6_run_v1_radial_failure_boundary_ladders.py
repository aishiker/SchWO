#!/usr/bin/env python3
"""Run the resumable Phase-6 V1 failed-domain pole-safe boundary ladders."""

from __future__ import annotations

import argparse
from pathlib import Path

from schwgw.validation.phase6_radial_failure_boundary_ladders import (
    DEFAULT_CAMPAIGN_ROOT,
    require_exact_cpython314,
    run,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--campaign-root", type=Path, default=DEFAULT_CAMPAIGN_ROOT)
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Smoke only: run the first N of the exact 5,798 failed keys.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume an explicitly existing unsealed root after validation.",
    )
    arguments = parser.parse_args()
    require_exact_cpython314()
    result = run(
        output_root=arguments.output_root,
        campaign_root=arguments.campaign_root,
        runner_path=Path(__file__),
        limit=arguments.limit,
        resume=arguments.resume,
    )
    print(result)


if __name__ == "__main__":
    main()
