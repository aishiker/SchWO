from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from schwgw.viz.tablei_uniform import UniformFigureError, render_tablei_uniform_figures


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _circular_error(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    return np.abs(np.angle(np.exp(1j * (np.angle(first) - np.angle(second)))))


def _comparison_metrics(
    *,
    plus: np.ndarray,
    cross: np.ndarray,
    fresnel: np.ndarray,
    rayleigh_sommerfeld: np.ndarray,
) -> dict[str, object]:
    metrics: dict[str, object] = {}
    for group, point_slice in (
        ("all", slice(None)),
        ("near_axis", slice(0, 4)),
        ("far_axis", slice(4, 8)),
    ):
        group_metrics = {}
        for polarization, field in (("plus", plus), ("cross", cross)):
            polarization_metrics = {}
            for name, baseline in (
                ("fresnel", fresnel),
                ("rayleigh_sommerfeld_I", rayleigh_sommerfeld),
            ):
                field_view = field[:, point_slice]
                baseline_view = baseline[:, point_slice]
                polarization_metrics[name] = {
                    "amplitude_mae": float(
                        np.mean(np.abs(np.abs(field_view) - np.abs(baseline_view)))
                    ),
                    "phase_circular_mae_rad": float(
                        np.mean(_circular_error(field_view, baseline_view))
                    ),
                    "complex_relative_mean": float(
                        np.mean(
                            np.abs(field_view - baseline_view)
                            / np.maximum(
                                np.abs(field_view), np.finfo(float).tiny
                            )
                        )
                    ),
                }
            group_metrics[polarization] = polarization_metrics
        metrics[group] = group_metrics
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Render the existing inferred Fig. 5/6 scattering data with the "
            "coordinate-matched Rayleigh--Sommerfeld-I phase-screen diagnostic."
        )
    )
    parser.add_argument("merged_npz", type=Path)
    parser.add_argument("rs_diagnostic_npz", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=600)
    args = parser.parse_args()

    with np.load(args.merged_npz, allow_pickle=False) as merged:
        kM = np.asarray(merged["kM_values"], dtype=float)
        point_x = np.asarray(merged["point_x"], dtype=float)
        plus = np.asarray(merged["F_plus_complex"], dtype=complex)
        cross = np.asarray(merged["F_cross_complex"], dtype=complex)
    with np.load(args.rs_diagnostic_npz, allow_pickle=False) as diagnostic:
        diagnostic_kM = np.asarray(diagnostic["kM"], dtype=float)
        diagnostic_x = np.asarray(diagnostic["x_over_M"], dtype=float)
        fresnel_all = np.asarray(diagnostic["fresnel_F"], dtype=complex)
        rs_all = np.asarray(diagnostic["rs_li_lift_F"], dtype=complex)
    if not np.array_equal(point_x, diagnostic_x):
        raise ValueError("Fig. 5/6 and RS Table-I point grids differ.")
    grid_indices = np.asarray(
        [
            int(
                np.flatnonzero(
                    np.isclose(diagnostic_kM, value, rtol=0.0, atol=1.0e-13)
                )[0]
            )
            for value in kM
        ]
    )
    fresnel = fresnel_all[grid_indices]
    rayleigh_sommerfeld = rs_all[grid_indices]

    try:
        rendered = render_tablei_uniform_figures(
            args.merged_npz,
            kirchhoff_complex=rayleigh_sommerfeld,
            output_dir=args.output_dir,
            dpi=args.dpi,
            created_by_cli=True,
            scattering_description=(
                "existing direct-curvature inferred diagonal response; no new "
                "black-hole scattering solve"
            ),
            kirchhoff_description=(
                "Rayleigh--Sommerfeld-I exact angular-spectrum propagation of "
                "the same scalar point-mass phase screen, using the "
                "Eq. (47)-coordinate-matched geometry"
            ),
            scattering_legend="direct curvature",
            kirchhoff_legend="Rayleigh--Sommerfeld I",
        )
    except UniformFigureError as exc:
        print(f"RS Fig. 5/6 render error: {exc}")
        return 2

    report = {
        "schema": "schwo_fig56_rayleigh_sommerfeld_diagnostic_v1",
        "scientific_status": "comparison_only_not_strict_reproduction",
        "merged_npz": {
            "path": str(args.merged_npz),
            "sha256": _sha256(args.merged_npz),
        },
        "rs_diagnostic_npz": {
            "path": str(args.rs_diagnostic_npz),
            "sha256": _sha256(args.rs_diagnostic_npz),
        },
        "metrics_against_existing_inferred_scattering": _comparison_metrics(
            plus=plus,
            cross=cross,
            fresnel=fresnel,
            rayleigh_sommerfeld=rayleigh_sommerfeld,
        ),
        "interpretation": (
            "These distances do not test strict paper agreement.  They only "
            "show whether replacing paraxial propagation by RS-I moves the "
            "scalar baseline closer to the existing inferred spin-2 curves."
        ),
        "rendered": {
            key: {
                "path": str(path),
                "sha256": _sha256(path),
                "size": path.stat().st_size,
            }
            for key, path in rendered.items()
        },
    }
    report_path = args.output_dir / "comparison_metrics.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
