#!/usr/bin/env python3
"""Validate the five completed audit-repair surfaces from durable artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
import sys
from typing import Any

import numpy as np
import scipy

from schwgw.io.apparent import load_apparent_results
from schwgw.io.asymptotic import load_fig8_asymptotic_dataset
from schwgw.io.results import load_results


KM_VALUES = (0.5, 1.0, 1.5, 2.0)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _token(value: float) -> str:
    return f"{value:g}".replace(".", "p")


def _finite_on_mask(values: np.ndarray, mask: np.ndarray) -> bool:
    selected = np.asarray(values)[mask]
    return bool(np.all(np.isfinite(selected.real) & np.isfinite(selected.imag)))


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--direct-dir", type=Path, required=True)
    parser.add_argument("--fig56-merged", type=Path, required=True)
    parser.add_argument("--fig8-dataset", type=Path, required=True)
    parser.add_argument("--fig2-high-precision", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise FileExistsError(f"refusing validation collision: {args.output}")

    direct_records = []
    for kM in KM_VALUES:
        token = _token(kM)
        physical_path = args.direct_dir / f"fig3_direct_curvature_kM_{token}.npz"
        apparent_path = args.direct_dir / f"fig7_direct_curvature_kM_{token}.npz"
        angular_path = args.direct_dir / f"fig4_direct_curvature_kM_{token}.npz"
        physical = load_results(physical_path)
        apparent = load_apparent_results(apparent_path)
        angular = load_results(angular_path)
        if physical.valid_mask is None or apparent.valid_mask is None:
            raise ValueError("direct x-z artifacts are missing validity masks")
        if physical.h_plus.shape != (241, 241) or angular.h_plus.shape != (1025, 1):
            raise ValueError("direct-curvature artifacts have unexpected production shapes")
        if not np.array_equal(physical.valid_mask, apparent.valid_mask):
            raise ValueError("physical and apparent x-z masks differ")
        middle = physical.h_plus.shape[1] // 2
        left = slice(0, middle)
        right_reversed = slice(None, middle, -1)
        for name, values in (
            ("h_plus", physical.h_plus),
            ("h_cross", physical.h_cross),
            ("h_b", apparent.h_b),
            ("h_longitudinal", apparent.h_longitudinal),
        ):
            if not np.array_equal(
                values[:, left], values[:, right_reversed], equal_nan=True
            ):
                raise ValueError(f"direct x-reflection even parity failed for {name}")
        for name, values in (("h_x", apparent.h_x), ("h_y", apparent.h_y)):
            if not np.array_equal(
                values[:, left], -values[:, right_reversed], equal_nan=True
            ):
                raise ValueError(f"direct x-reflection odd parity failed for {name}")
        if not all(
            _finite_on_mask(values, physical.valid_mask)
            for values in (physical.h_plus, physical.h_cross)
        ):
            raise ValueError("direct physical fields contain non-finite valid values")
        if not all(
            _finite_on_mask(values, apparent.valid_mask)
            for values in (
                apparent.h_x,
                apparent.h_y,
                apparent.h_b,
                apparent.h_longitudinal,
            )
        ):
            raise ValueError("direct apparent fields contain non-finite valid values")
        np.testing.assert_allclose(
            apparent.h_longitudinal[apparent.valid_mask],
            2.0 * apparent.h_b[apparent.valid_mask],
            rtol=0.0,
            atol=0.0,
        )
        if not np.all(np.isfinite(angular.h_plus)) or not np.all(
            np.isfinite(angular.h_cross)
        ):
            raise ValueError("direct angular fields contain non-finite values")
        convergence = physical.metadata["diagnostics"]["convergence"]
        if convergence.get("final_pair_passed") is not True:
            raise ValueError(f"direct x-z lmax convergence failed for kM={kM}")
        angular_convergence = angular.metadata["diagnostics"][
            "lmax_convergence_policy"
        ]
        if angular_convergence.get("final_pair_passed") is not True:
            raise ValueError(f"direct angular lmax convergence failed for kM={kM}")
        angular_points = angular.metadata["diagnostics"]["points"]
        if not angular_points or any(
            float(point.get("radial_ode_jet", 0.0)) != 1.0
            for point in angular_points
        ):
            raise ValueError(f"direct angular ODE-jet contract failed for kM={kM}")
        physical_maxima = physical.metadata["diagnostics"]["maxima"]
        if float(physical_maxima.get("radial_ode_jet", 0.0)) != 1.0:
            raise ValueError(f"direct x-z ODE-jet contract failed for kM={kM}")
        bridge = physical.metadata["convention"]["polarization_bridge"]
        if (
            bridge
            != "direct RW-gauge metric -> linearized Riemann -> incident-frame E"
            or physical.metadata["convention"].get("polarization_bridge_validated")
            is not True
            or apparent.metadata["convention"].get(
                "strict_np_lower_scalar_completion"
            )
            is not False
        ):
            raise ValueError("direct-curvature bridge metadata failed closed")
        direct_records.append(
            {
                "kM": kM,
                "physical_sha256": _sha256(physical_path),
                "apparent_sha256": _sha256(apparent_path),
                "angular_sha256": _sha256(angular_path),
                "valid_points": int(np.count_nonzero(physical.valid_mask)),
                "masked_points": int(physical.valid_mask.size - np.count_nonzero(physical.valid_mask)),
                "convergence": convergence,
                "angular_convergence": angular_convergence,
                "radial_ode_jet": True,
                "angular_magnitude_second_difference": {
                    "plus_max": float(
                        np.max(np.abs(np.diff(np.abs(angular.h_plus[:, 0]), 2)))
                    ),
                    "cross_max": float(
                        np.max(np.abs(np.diff(np.abs(angular.h_cross[:, 0]), 2)))
                    ),
                    "plus_rms": float(
                        np.sqrt(
                            np.mean(
                                np.abs(
                                    np.diff(np.abs(angular.h_plus[:, 0]), 2)
                                )
                                ** 2
                            )
                        )
                    ),
                    "cross_rms": float(
                        np.sqrt(
                            np.mean(
                                np.abs(
                                    np.diff(np.abs(angular.h_cross[:, 0]), 2)
                                )
                                ** 2
                            )
                        )
                    ),
                },
                "physical_bridge": bridge,
                "strict_np_lower_completion": apparent.metadata["convention"][
                    "strict_np_lower_scalar_completion"
                ],
            }
        )

    with np.load(args.fig56_merged, allow_pickle=False) as table:
        if table["F_plus_complex"].shape != (40, 8):
            raise ValueError("direct Table-I merge has the wrong shape")
        metadata = json.loads(str(table["metadata_json"].item()))
        if (
            metadata.get("schema_version")
            != "phase5_fig5_fig6_direct_metric_curvature_merged_v2"
            or "simultaneous" not in metadata.get("primary_response_surface", "")
            or metadata.get("dense_solution_radial_differencing") is not False
            or "RW/Zerilli ODE" not in metadata.get("radial_derivative_method", "")
            or table["F_plus_diagonal_complex"].shape != (40, 8)
            or table["F_cross_diagonal_complex"].shape != (40, 8)
        ):
            raise ValueError("direct Table-I mixed/diagonal response contract failed")
        table_metrics = {
            "sha256": _sha256(args.fig56_merged),
            "shape": list(table["F_plus_complex"].shape),
            "finite": bool(
                np.all(np.isfinite(table["F_plus_complex"]))
                and np.all(np.isfinite(table["F_cross_complex"]))
            ),
            "max_final_pair_delta_plus": float(table["final_pair_delta_plus"].max()),
            "max_final_pair_delta_cross": float(table["final_pair_delta_cross"].max()),
            "max_plus_cross_magnitude_delta": float(
                np.max(np.abs(table["abs_F_plus"] - table["abs_F_cross"]))
            ),
            "primary_response_surface": metadata["primary_response_surface"],
            "max_primary_vs_diagonal_plus_delta": float(
                np.max(
                    np.abs(
                        table["F_plus_complex"]
                        - table["F_plus_diagonal_complex"]
                    )
                )
            ),
            "max_primary_vs_diagonal_cross_delta": float(
                np.max(
                    np.abs(
                        table["F_cross_complex"]
                        - table["F_cross_diagonal_complex"]
                    )
                )
            ),
        }
    if not table_metrics["finite"] or max(
        table_metrics["max_final_pair_delta_plus"],
        table_metrics["max_final_pair_delta_cross"],
    ) > 1.0e-4:
        raise ValueError("direct Table-I scientific/convergence gate failed")

    mst = load_fig8_asymptotic_dataset(args.fig8_dataset)
    parity_residuals = []
    modulus_deviation = []
    for row, kM in enumerate(KM_VALUES):
        sigma = (mst.ell - 1) * mst.ell * (mst.ell + 1) * (mst.ell + 2)
        expected = (sigma + 12.0j * kM) / (sigma - 12.0j * kM)
        high = mst.ell >= 20
        parity_residuals.append(
            float(
                np.max(
                    np.abs(
                        mst.phase_factor_even[row, high]
                        / mst.phase_factor_odd[row, high]
                        - expected[high]
                    )
                )
            )
        )
        modulus_deviation.append(
            float(
                max(
                    np.max(np.abs(np.abs(mst.phase_factor_odd[row, high]) - 1.0)),
                    np.max(np.abs(np.abs(mst.phase_factor_even[row, high]) - 1.0)),
                )
            )
        )
    if max(parity_residuals) > 1.0e-12:
        raise ValueError("direct MST parity relation failed")
    if not np.array_equal(mst.ell, np.arange(2, 503, dtype=np.int64)):
        raise ValueError("direct MST ell grid is not the frozen 2..502 sequence")
    tail = mst.metadata["tail"]
    if not (
        tail["direct_mst_phase_solver_used"] is True
        and tail["empirical_overlap_blend_used"] is False
        and tail["empirical_phase_offset_used"] is False
    ):
        raise ValueError("Fig. 8 is not a direct, unblended MST dataset")
    transaction_records = mst.metadata["transactions"]
    if max(record["max_recurrence_residual"] for record in transaction_records) > 1.0e-25:
        raise ValueError("direct MST recurrence residual gate failed")
    if max(
        max(record["transition"].values()) for record in transaction_records
    ) > 5.0e-3:
        raise ValueError("direct MST low/high transition gate failed")
    mst_metrics = {
        "sha256": _sha256(args.fig8_dataset),
        "ell_range": [int(mst.ell[0]), int(mst.ell[-1])],
        "direct_mst_parity_relation_ell_min": 20,
        "parity_relation_max_residual_by_kM": parity_residuals,
        "high_ell_unit_modulus_max_deviation_by_kM": modulus_deviation,
        "finite_cross_sections": bool(np.all(np.isfinite(mst.differential_cross_section))),
        "tail": tail,
        "transactions": transaction_records,
        "ladder": mst.metadata["lmax_ladder_diagnostics"],
    }
    if not mst_metrics["finite_cross_sections"]:
        raise ValueError("Fig. 8 cross section contains non-finite values")

    fig2 = json.loads(args.fig2_high_precision.read_text(encoding="utf-8"))
    if (
        fig2.get("mpmath_working_precision_digits") != 80
        or len(fig2.get("cases", [])) != 4
        or fig2.get("all_shells_below_unit_amplitude") is not True
        or max(case["shell_relative_difference"] for case in fig2["cases"])
        > 5.0e-5
    ):
        raise ValueError("Fig. 2 high-precision evidence has an unexpected contract")

    payload = {
        "schema_version": "schwgw_audit_repairs_validation_v1",
        "status": "PASS",
        "runtime": {
            "python": sys.version,
            "python_implementation": platform.python_implementation(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
        },
        "fig2_high_precision": {
            "path": str(args.fig2_high_precision),
            "sha256": _sha256(args.fig2_high_precision),
            "working_decimal_digits": fig2["mpmath_working_precision_digits"],
            "records": fig2["cases"],
        },
        "direct_curvature_fig3_fig4_fig7": direct_records,
        "direct_curvature_fig5_fig6": table_metrics,
        "direct_mst_fig8": mst_metrics,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(_json_safe(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"event": "audit_repairs_validation_passed", "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
