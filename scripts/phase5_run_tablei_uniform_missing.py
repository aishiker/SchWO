from __future__ import annotations

import argparse
from pathlib import Path

from schwgw.io.tablei_uniform import UniformContractError, run_tablei_uniform_missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute only missing direct uniform-40 Table-I transactions"
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--frequencies",
        type=float,
        nargs="*",
        help="Ordered subset of missing kM values; default computes all missing values.",
    )
    args = parser.parse_args(argv)
    try:
        run_tablei_uniform_missing(
            output_dir=args.output_dir,
            resume=args.resume,
            frequencies=args.frequencies,
        )
    except UniformContractError as exc:
        print(f"uniform production contract error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
