#!/usr/bin/env python3
"""Run one frozen Phase-6 V0 check into a fresh immutable report root."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from schwgw.validation.phase6_v0_checks import run_v0_check
from schwgw.validation.phase6_v0_verification import REQUIRED_CHECK_IDS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-id", choices=REQUIRED_CHECK_IDS, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_v0_check(args.check_id, args.output_root)
    print(json.dumps(result, sort_keys=True))
    return 1 if result["state"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
