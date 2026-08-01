from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from schwgw.scattering.kirchhoff import compute_kirchhoff_eq47
from schwgw.viz.tablei_uniform import UniformFigureError, render_tablei_uniform_figures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render direct-sample uniform-40 Fig.5/Fig.6"
    )
    parser.add_argument("merged_npz", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=600)
    parser.add_argument("--kirchhoff-dps", type=int, default=60)
    args = parser.parse_args(argv)
    try:
        with np.load(args.merged_npz, allow_pickle=False) as data:
            kM_values = np.asarray(data["kM_values"], dtype=float)
            radius = np.asarray(data["point_r"], dtype=float)
            theta = np.asarray(data["point_theta"], dtype=float)
        kirchhoff = compute_kirchhoff_eq47(
            kM_values=kM_values,
            r_over_M=radius,
            theta=theta,
            dps=args.kirchhoff_dps,
        )
        render_tablei_uniform_figures(
            args.merged_npz,
            kirchhoff_complex=kirchhoff.F_complex,
            output_dir=args.output_dir,
            dpi=args.dpi,
            created_by_cli=True,
        )
    except UniformFigureError as exc:
        print(f"uniform render error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
