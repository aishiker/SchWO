from __future__ import annotations

import argparse
from pathlib import Path

from schwgw.io.tablei_another_bounded_local_refinement import (
    AnotherBoundedLocalRefinementContractError,
    run_another_bounded_local_refinement,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the bounded point-only another bounded-local refinement"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("runs/phase5/fig5_fig6_another_bounded_local_refinement"),
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
        default=Path("runs/phase5/fig5_fig6_targeted_adaptive_radial_gate"),
    )
    parser.add_argument(
        "--accepted-further-local-dir",
        type=Path,
        default=Path("runs/phase5/fig5_fig6_further_local_refinement"),
    )
    parser.add_argument(
        "--accepted-t7cb-evidence",
        type=Path,
        default=Path(
            "docs/handoffs/archive/"
            "T7_2026-07-18_pre_t7cc_literal_failed_child_radial_review.md"
        ),
    )
    parser.add_argument(
        "--accepted-literal-failed-child-dir",
        type=Path,
        default=Path(
            "runs/phase5/fig5_fig6_literal_failed_child_refinement"
        ),
    )
    parser.add_argument(
        "--accepted-t7cd-evidence",
        type=Path,
        default=Path(
            "docs/handoffs/archive/"
            "T7_2026-07-20_pre_t7ce_another_bounded_local_radial_review.md"
        ),
    )
    parser.add_argument(
        "--radial-gate-dir",
        type=Path,
        default=Path("runs/phase5/fig5_fig6_another_bounded_local_radial_gate"),
    )
    parser.add_argument("--resume", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        run_another_bounded_local_refinement(
            output_dir=args.output_dir,
            accepted_review_npz=args.accepted_review_npz,
            accepted_risk_pilot_dir=args.accepted_risk_pilot_dir,
            accepted_adaptive_dir=args.accepted_adaptive_dir,
            accepted_t7bz_evidence=args.accepted_t7bz_evidence,
            accepted_t4aa_gate_dir=args.accepted_t4aa_gate_dir,
            accepted_further_local_dir=args.accepted_further_local_dir,
            accepted_t7cb_evidence=args.accepted_t7cb_evidence,
            accepted_literal_failed_child_dir=(
                args.accepted_literal_failed_child_dir
            ),
            accepted_t7cd_evidence=args.accepted_t7cd_evidence,
            radial_gate_dir=args.radial_gate_dir,
            resume=args.resume,
        )
    except AnotherBoundedLocalRefinementContractError as exc:
        print(f"another bounded-local contract error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
