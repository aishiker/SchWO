from __future__ import annotations

import argparse
from pathlib import Path

from schwgw.io.tablei_uniform import UniformContractError, merge_tablei_uniform


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Merge direct Fig.5/6 uniform-40 rows without interpolation"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--transaction-dir", type=Path, required=True)
    parser.add_argument(
        "--review-npz",
        type=Path,
        default=Path(
            "runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz"
        ),
    )
    parser.add_argument(
        "--pilot-npz",
        type=Path,
        default=Path("runs/phase5/fig5_fig6_delta0p1_risk_pilot/risk_pilot_values.npz"),
    )
    args = parser.parse_args(argv)
    try:
        merge_tablei_uniform(
            output_path=args.output,
            transaction_dir=args.transaction_dir,
            review_npz=args.review_npz,
            pilot_npz=args.pilot_npz,
        )
    except UniformContractError as exc:
        print(f"uniform merge contract error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
