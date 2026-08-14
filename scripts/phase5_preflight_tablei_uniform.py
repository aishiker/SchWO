from __future__ import annotations

import argparse
import json
from pathlib import Path

from schwgw.io.tablei_uniform import UniformContractError, preflight_tablei_uniform


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only Fig.5/6 uniform-40 preflight"
    )
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
    parser.add_argument("--transaction-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        print(
            json.dumps(
                preflight_tablei_uniform(
                    review_npz=args.review_npz,
                    pilot_npz=args.pilot_npz,
                    transaction_dir=args.transaction_dir,
                ),
                indent=2,
                sort_keys=True,
            )
        )
    except UniformContractError as exc:
        print(f"uniform preflight error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
