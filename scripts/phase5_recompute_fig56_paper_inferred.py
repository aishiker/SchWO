from __future__ import annotations

import argparse
from functools import partial
import json
from pathlib import Path

from schwgw.io.tablei_paper_inferred import (
    DEFAULT_SOURCE_MERGE,
    PaperInferredTableIError,
    merge_inferred_tablei_uniform,
    produce_inferred_tablei_uniform,
)
from schwgw.scattering.paper_projection import compute_lhz_eq42_response_columns


def _progress(record: object) -> None:
    print(json.dumps(record, sort_keys=True), flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Recompute Fig. 5/6 with the inferred Eq. (42) response columns"
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

    produce = subparsers.add_parser("produce")
    produce.add_argument("--output-dir", type=Path, required=True)
    produce.add_argument("--source-merged", type=Path, default=DEFAULT_SOURCE_MERGE)
    produce.add_argument("--frequencies", nargs="+", type=float)
    produce.add_argument("--resume", action="store_true")
    produce.add_argument(
        "--eq35-z-conjugation",
        choices=("linear", "literal_conjugate"),
        default="literal_conjugate",
    )

    merge = subparsers.add_parser("merge")
    merge.add_argument("--transaction-dir", type=Path, required=True)
    merge.add_argument("--output", type=Path, required=True)
    merge.add_argument("--source-merged", type=Path, default=DEFAULT_SOURCE_MERGE)

    args = parser.parse_args(argv)
    try:
        if args.action == "produce":
            produce_inferred_tablei_uniform(
                output_dir=args.output_dir,
                source_merged_npz=args.source_merged,
                frequencies=args.frequencies,
                resume=args.resume,
                response_solver=partial(
                    compute_lhz_eq42_response_columns,
                    q011_z_conjugation=args.eq35_z_conjugation,
                ),
                progress=_progress,
            )
        else:
            result = merge_inferred_tablei_uniform(
                transaction_dir=args.transaction_dir,
                output_path=args.output,
                source_merged_npz=args.source_merged,
            )
            _progress({"event": "merged", "path": str(result)})
    except PaperInferredTableIError as exc:
        print(f"Fig. 5/6 inferred-response production error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
