from __future__ import annotations

import argparse
from pathlib import Path

from schwgw.io.tablei_risk_pilot import (
    PilotContractError,
    repair_delta0p1_risk_pilot_metadata,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Repair only the Delta(kM)=0.1 risk-pilot metadata contract"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("runs/phase5/fig5_fig6_delta0p1_risk_pilot"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        repair_delta0p1_risk_pilot_metadata(output_dir=args.output_dir)
    except PilotContractError as exc:
        print(f"risk-pilot metadata repair error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
