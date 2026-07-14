from __future__ import annotations

import argparse
from pathlib import Path

from schwgw.io.tablei_risk_pilot import PilotContractError, run_delta0p1_risk_pilot


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the bounded point-only risk pilot")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("runs/phase5/fig5_fig6_delta0p1_risk_pilot"),
    )
    parser.add_argument(
        "--accepted-review-npz",
        type=Path,
        default=Path(
            "runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz"
        ),
    )
    parser.add_argument(
        "--radial-gate-dir",
        type=Path,
        default=Path(
            "runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate"
        ),
    )
    parser.add_argument("--resume", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        run_delta0p1_risk_pilot(
            output_dir=args.output_dir,
            accepted_review_npz=args.accepted_review_npz,
            radial_gate_dir=args.radial_gate_dir,
            resume=args.resume,
        )
    except PilotContractError as exc:
        print(f"risk-pilot contract error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
