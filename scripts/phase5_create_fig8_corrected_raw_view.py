#!/usr/bin/env python3
"""Create a metadata-corrected, array-identical Fig. 8 raw input view."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from schwgw.io.asymptotic import Fig8AsymptoticDataset, save_fig8_asymptotic_dataset


ARRAY_FIELDS = (
    "kM",
    "ell",
    "phase_factor_odd",
    "phase_factor_even",
    "theta",
    "reduction_orders",
    "M22",
    "M12",
    "differential_cross_section",
    "lmax_ladder",
    "lmax_ladder_cross_section",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    if args.source.suffix != ".npz" or args.output.suffix != ".npz":
        parser.error("source and output must be NPZ paths")
    source_sidecar = args.source.with_suffix(".json")
    if not args.source.is_file() or not source_sidecar.is_file():
        raise FileNotFoundError("source Fig. 8 NPZ/JSON pair is incomplete")
    external_metadata = json.loads(source_sidecar.read_text(encoding="utf-8"))
    with np.load(args.source, allow_pickle=False) as source:
        if set(source.files) != set(ARRAY_FIELDS) | {"metadata_json"}:
            raise ValueError("source Fig. 8 array set is unexpected")
        embedded_metadata = json.loads(str(source["metadata_json"]))
        if embedded_metadata != external_metadata:
            raise ValueError("source embedded/external metadata mismatch")
        arrays = {name: np.asarray(source[name]) for name in ARRAY_FIELDS}

    corrected_metadata = {
        **external_metadata,
        "strict_paper_reproduction_claim": False,
        "paper_equivalence": "YELLOW",
        "metadata_correction": {
            "reason": (
                "historical raw artifact predates the mandatory explicit "
                "strict-paper claim; missing is corrected to false"
            ),
            "source_npz": str(args.source),
            "source_npz_sha256": _sha256(args.source),
            "source_json": str(source_sidecar),
            "source_json_sha256": _sha256(source_sidecar),
            "scientific_arrays_modified": False,
        },
    }
    corrected = Fig8AsymptoticDataset(
        **arrays,
        metadata=corrected_metadata,
    )
    output, sidecar = save_fig8_asymptotic_dataset(corrected, args.output)

    with np.load(output, allow_pickle=False) as written:
        for name, expected in arrays.items():
            if not np.array_equal(written[name], expected, equal_nan=True):
                raise RuntimeError(f"corrected raw view changed array {name}")
    print(
        json.dumps(
            {
                "event": "fig8_corrected_raw_view_complete",
                "output": str(output),
                "output_sha256": _sha256(output),
                "sidecar": str(sidecar),
                "sidecar_sha256": _sha256(sidecar),
                "scientific_arrays_modified": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
