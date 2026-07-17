from __future__ import annotations

import argparse
from pathlib import Path

from schwgw.io.tablei_further_local_refinement import (
    FurtherLocalRefinementContractError,
    run_further_local_refinement,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the bounded point-only further-local refinement"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("runs/phase5/fig5_fig6_further_local_refinement"),
    )
    parser.add_argument(
        "--accepted-review-npz",
        type=Path,
        default=Path(
            "runs/phase5/fig5_fig6_dense_review_grid/"
            "tablei_dense_review_values.npz"
        ),
    )
    parser.add_argument(
        "--accepted-risk-pilot-dir",
        type=Path,
        default=Path("runs/phase5/fig5_fig6_delta0p1_risk_pilot"),
    )
    parser.add_argument(
        "--accepted-adaptive-dir",
        type=Path,
        default=Path("runs/phase5/fig5_fig6_targeted_adaptive_refinement"),
    )
    parser.add_argument(
        "--accepted-t7bz-evidence",
        type=Path,
        default=Path(
            "docs/handoffs/archive/"
            "T7_2026-07-16_pre_t7ca_further_local_radial_review.md"
        ),
    )
    parser.add_argument(
        "--accepted-t4aa-gate-dir",
        type=Path,
        default=Path(
            "runs/phase5/fig5_fig6_targeted_adaptive_radial_gate"
        ),
    )
    parser.add_argument(
        "--radial-gate-dir",
        type=Path,
        default=Path("runs/phase5/fig5_fig6_further_local_radial_gate"),
    )
    parser.add_argument("--resume", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        run_further_local_refinement(
            output_dir=args.output_dir,
            accepted_review_npz=args.accepted_review_npz,
            accepted_risk_pilot_dir=args.accepted_risk_pilot_dir,
            accepted_adaptive_dir=args.accepted_adaptive_dir,
            accepted_t7bz_evidence=args.accepted_t7bz_evidence,
            accepted_t4aa_gate_dir=args.accepted_t4aa_gate_dir,
            radial_gate_dir=args.radial_gate_dir,
            resume=args.resume,
        )
    except FurtherLocalRefinementContractError as exc:
        print(f"further-local contract error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
