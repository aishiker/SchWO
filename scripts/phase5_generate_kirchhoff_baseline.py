from __future__ import annotations

import argparse
from pathlib import Path

from schwgw.io.kirchhoff import generate_kirchhoff_review_grid_artifact


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(
            "runs/phase5/fig5_fig6_dense_review_grid/"
            "tablei_dense_review_values.npz"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("runs/phase5/fig5_fig6_kirchhoff_baseline"),
    )
    parser.add_argument("--dps", type=int, default=60)
    args = parser.parse_args()
    paths = generate_kirchhoff_review_grid_artifact(
        args.source,
        args.output_dir,
        dps=args.dps,
    )
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
