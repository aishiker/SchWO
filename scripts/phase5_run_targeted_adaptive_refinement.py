from __future__ import annotations

import argparse
from pathlib import Path

from schwgw.io.tablei_adaptive_refinement import (
    AdaptiveRefinementContractError,
    run_targeted_adaptive_refinement,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the bounded point-only targeted adaptive refinement"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("runs/phase5/fig5_fig6_targeted_adaptive_refinement"),
    )
    parser.add_argument(
        "--accepted-review-npz",
        type=Path,
        default=Path(
            "runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz"
        ),
    )
    parser.add_argument(
        "--accepted-risk-pilot-dir",
        type=Path,
        default=Path("runs/phase5/fig5_fig6_delta0p1_risk_pilot"),
    )
    parser.add_argument(
        "--radial-gate-dir",
        type=Path,
        default=Path("runs/phase5/fig5_fig6_targeted_adaptive_radial_gate"),
    )
    parser.add_argument("--resume", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        run_targeted_adaptive_refinement(
            output_dir=args.output_dir,
            accepted_review_npz=args.accepted_review_npz,
            accepted_risk_pilot_dir=args.accepted_risk_pilot_dir,
            radial_gate_dir=args.radial_gate_dir,
            resume=args.resume,
        )
    except AdaptiveRefinementContractError as exc:
        print(f"targeted-adaptive contract error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
