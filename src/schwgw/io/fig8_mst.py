"""Durable direct-MST production for Li--Hou--Zhao Fig. 8."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import numpy as np

from schwgw.backgrounds import SchwarzschildBackground

from schwgw.io.asymptotic import (
    FIG8_DIRECT_MST_SCHEMA_VERSION,
    FIG8_KM_VALUES,
    FIG8_REDUCTION_ORDERS,
    Fig8AsymptoticDataset,
    _ladder_diagnostics,
    load_fig8_asymptotic_dataset,
    save_fig8_asymptotic_dataset,
)
from schwgw.numerics import BoundaryConfig, extrapolate_r_out_ladder, solve_radial_mode
from schwgw.perturbations import Sector
from schwgw.scattering.asymptotic import (
    outer_matching_phase_corrected,
    parity_scattering_series,
    scattering_matrix_cross_section,
)
from schwgw.scattering.mst import schwarzschild_mst_phase_factor


SCHEMA_VERSION = FIG8_DIRECT_MST_SCHEMA_VERSION
DEFAULT_RAW = Path(
    "runs/phase5/fig8_asymptotic_production/fig8_asymptotic_l180_n1440.npz"
)
MST_SOURCE_COMMIT = "354d3d70e439f1c8bb721cb4e9ea6562541110a8"


class Fig8MSTError(ValueError):
    """Raised when a direct MST transaction violates its contract."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _token(kM: float) -> str:
    return f"{kM:g}".replace(".", "p")


def _paths(root: Path, kM: float) -> tuple[Path, Path]:
    npz = root / f"fig8_direct_mst_kM_{_token(kM)}.npz"
    return npz, Path(str(npz) + ".json")


def _raw_sidecar_path(raw_file: Path) -> Path:
    """Return the sidecar path used by ``save_fig8_asymptotic_dataset``."""

    if raw_file.suffix != ".npz":
        raise Fig8MSTError("raw Fig. 8 dataset must use the .npz suffix")
    return raw_file.with_suffix(".json")


def produce_fig8_mst_frequency(
    *,
    kM: float,
    output_dir: str | Path,
    raw_path: str | Path = DEFAULT_RAW,
    mst_start: int = 20,
    output_lmax: int = 502,
    truncation: int = 30,
    guard_terms: int = 24,
    working_dps: int = 70,
    low_r_out_ladder: tuple[float, ...] = (300.0, 600.0, 1200.0),
    outer_series_order: int = 160,
    progress: Callable[[dict[str, Any]], None] | None = None,
) -> tuple[Path, Path]:
    """Produce one frequency's exact-low/direct-MST phase transaction."""

    if kM not in FIG8_KM_VALUES:
        raise Fig8MSTError("kM is outside the fixed Fig. 8 frequency set")
    if mst_start < 3 or output_lmax < mst_start:
        raise Fig8MSTError("invalid direct MST range")
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    npz_path, sidecar_path = _paths(root, kM)
    if npz_path.exists() or sidecar_path.exists():
        raise Fig8MSTError(f"refusing existing MST transaction for kM={kM}")
    raw_file = Path(raw_path)
    raw = load_fig8_asymptotic_dataset(raw_file)
    if np.flatnonzero(raw.kM == kM).size != 1:
        raise Fig8MSTError("raw dataset does not contain exactly one requested frequency")
    if not np.array_equal(raw.ell, np.arange(2, int(raw.ell[-1]) + 1)):
        raise Fig8MSTError("raw numerical ell sequence is not contiguous")
    if int(raw.ell[-1]) < mst_start:
        raise Fig8MSTError("raw phase sequence does not reach the MST transition")
    ell = np.arange(2, output_lmax + 1, dtype=np.int64)
    odd = np.empty(ell.shape, dtype=np.complex128)
    even = np.empty_like(odd)
    low_count = mst_start - 2
    low_ell = np.arange(2, mst_start, dtype=np.int64)
    low_odd_ladder, low_even_ladder, low_odd_fit, low_even_fit = (
        _jost_low_phase_ladder(
            kM=kM,
            ell=low_ell,
            r_out_ladder=low_r_out_ladder,
            outer_series_order=outer_series_order,
            progress=progress,
        )
    )
    odd[:low_count] = low_odd_fit.extrapolated
    even[:low_count] = low_even_fit.extrapolated
    mst_ell = np.arange(mst_start, output_lmax + 1, dtype=np.int64)
    nu = np.empty(mst_ell.shape, dtype=np.complex128)
    residual = np.empty(mst_ell.shape, dtype=np.float64)
    for index, ell_value in enumerate(mst_ell):
        record = schwarzschild_mst_phase_factor(
            int(ell_value),
            k=kM,
            truncation=truncation,
            guard_terms=guard_terms,
            working_dps=working_dps,
        )
        destination = low_count + index
        odd[destination] = record.odd
        even[destination] = record.even
        nu[index] = record.nu
        residual[index] = record.recurrence_residual
        if progress is not None and (
            index == 0 or (index + 1) % 25 == 0 or index + 1 == mst_ell.size
        ):
            progress(
                {
                    "event": "fig8_direct_mst_progress",
                    "kM": kM,
                    "completed": index + 1,
                    "total": int(mst_ell.size),
                    "ell": int(ell_value),
                }
            )
    transition_probe_odd, transition_probe_even, _, _ = _jost_low_phase_ladder(
        kM=kM,
        ell=np.asarray([mst_start], dtype=np.int64),
        r_out_ladder=low_r_out_ladder,
        outer_series_order=outer_series_order,
        progress=None,
    )
    transition_odd_fit = extrapolate_r_out_ladder(
        np.asarray(low_r_out_ladder), transition_probe_odd
    )
    transition_even_fit = extrapolate_r_out_ladder(
        np.asarray(low_r_out_ladder), transition_probe_even
    )
    transition = {
        "odd_abs_delta": float(abs(odd[low_count] - transition_odd_fit.extrapolated[0])),
        "even_abs_delta": float(abs(even[low_count] - transition_even_fit.extrapolated[0])),
    }
    if max(transition.values()) > 5.0e-3:
        raise Fig8MSTError(f"raw/MST transition mismatch is too large: {transition}")
    arrays = {
        "kM": np.asarray(kM),
        "ell": ell,
        "phase_factor_odd": odd,
        "phase_factor_even": even,
        "mst_ell": mst_ell,
        "renormalized_angular_momentum": nu,
        "recurrence_residual": residual,
        "low_ell": low_ell,
        "low_r_out_ladder": np.asarray(low_r_out_ladder, dtype=np.float64),
        "low_phase_factor_odd_ladder": low_odd_ladder,
        "low_phase_factor_even_ladder": low_even_ladder,
        "low_phase_factor_odd_uncertainty": low_odd_fit.uncertainty,
        "low_phase_factor_even_uncertainty": low_even_fit.uncertainty,
    }
    _atomic_npz(npz_path, arrays)
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "complete": True,
        "kM": kM,
        "raw_path": str(raw_file),
        "raw_sha256": _sha256(raw_file),
        "raw_sidecar_sha256": _sha256(_raw_sidecar_path(raw_file)),
        "raw_range": None,
        "raw_finite_radius_correction": None,
        "low_ell_range": [2, mst_start - 1],
        "low_ell_method": "RW/Zerilli Jost 1/r outer basis plus quadratic 1/r_out extrapolation",
        "low_r_out_ladder": list(low_r_out_ladder),
        "outer_series_order_cap": outer_series_order,
        "max_low_odd_extrapolation_uncertainty": float(np.max(low_odd_fit.uncertainty)),
        "max_low_even_extrapolation_uncertainty": float(np.max(low_even_fit.uncertainty)),
        "mst_range": [mst_start, output_lmax],
        "mst_truncation": truncation,
        "mst_guard_terms": guard_terms,
        "mst_working_dps": working_dps,
        "mst_reference_commit": MST_SOURCE_COMMIT,
        "empirical_phase_offset": False,
        "empirical_blend": False,
        "transition": transition,
        "max_recurrence_residual": float(residual.max()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "strict_paper_reproduction_claim": False,
        "strict_paper_reproduction_limitation": (
            "external odd-sector BHPT/MST phase benchmark passed; an "
            "independent even-sector radial normalization and the author's "
            "raw reference data remain unavailable"
        ),
    }
    metadata["npz_sha256"] = _sha256(npz_path)
    _atomic_json(sidecar_path, metadata)
    return npz_path, sidecar_path


def finalize_fig8_mst_frequency(
    *,
    kM: float,
    output_dir: str | Path,
    raw_path: str | Path = DEFAULT_RAW,
    mst_start: int = 20,
    output_lmax: int = 502,
    truncation: int = 30,
    guard_terms: int = 24,
    working_dps: int = 70,
) -> tuple[Path, Path]:
    """Close metadata for a complete NPZ left by a post-publication failure.

    This path performs no MST or radial calculation.  It is intentionally
    limited to the exact orphan shape emitted after the historical raw-sidecar
    filename bug: the NPZ must exist, its sidecar must be absent, and every
    array/value is independently reloaded and checked before the sidecar is
    published.
    """

    if kM not in FIG8_KM_VALUES:
        raise Fig8MSTError("kM is outside the fixed Fig. 8 frequency set")
    root = Path(output_dir)
    npz_path, sidecar_path = _paths(root, kM)
    if not npz_path.is_file() or sidecar_path.exists():
        raise Fig8MSTError(
            "finalization requires one existing NPZ and one absent sidecar"
        )
    raw_file = Path(raw_path)
    raw = load_fig8_asymptotic_dataset(raw_file)
    frequency_matches = np.flatnonzero(raw.kM == kM)
    if frequency_matches.size != 1:
        raise Fig8MSTError("raw dataset does not contain exactly one requested frequency")
    raw_index = int(frequency_matches[0])
    corrected_odd = outer_matching_phase_corrected(
        raw.phase_factor_odd[raw_index], raw.ell, k=kM, r_out=300.0
    )
    corrected_even = outer_matching_phase_corrected(
        raw.phase_factor_even[raw_index], raw.ell, k=kM, r_out=300.0
    )
    expected_ell = np.arange(2, output_lmax + 1, dtype=np.int64)
    expected_mst_ell = np.arange(mst_start, output_lmax + 1, dtype=np.int64)
    expected_keys = {
        "kM",
        "ell",
        "phase_factor_odd",
        "phase_factor_even",
        "mst_ell",
        "renormalized_angular_momentum",
        "recurrence_residual",
    }
    with np.load(npz_path, allow_pickle=False) as data:
        if set(data.files) != expected_keys:
            raise Fig8MSTError("orphan MST transaction has an unexpected array set")
        if float(data["kM"]) != kM:
            raise Fig8MSTError("orphan MST transaction has the wrong frequency")
        ell = np.asarray(data["ell"], dtype=np.int64)
        mst_ell = np.asarray(data["mst_ell"], dtype=np.int64)
        odd = np.asarray(data["phase_factor_odd"], dtype=np.complex128)
        even = np.asarray(data["phase_factor_even"], dtype=np.complex128)
        nu = np.asarray(
            data["renormalized_angular_momentum"], dtype=np.complex128
        )
        residual = np.asarray(data["recurrence_residual"], dtype=np.float64)
    if not np.array_equal(ell, expected_ell) or not np.array_equal(
        mst_ell, expected_mst_ell
    ):
        raise Fig8MSTError("orphan MST transaction has the wrong ell sequence")
    if odd.shape != ell.shape or even.shape != ell.shape:
        raise Fig8MSTError("orphan MST phase arrays have the wrong shape")
    if nu.shape != mst_ell.shape or residual.shape != mst_ell.shape:
        raise Fig8MSTError("orphan MST diagnostic arrays have the wrong shape")
    if not all(
        np.all(np.isfinite(values)) for values in (odd, even, nu, residual)
    ):
        raise Fig8MSTError("orphan MST transaction contains non-finite values")
    raw_transition_index = int(np.flatnonzero(raw.ell == mst_start)[0])
    low_count = mst_start - 2
    transition = {
        "odd_abs_delta": float(
            abs(odd[low_count] - corrected_odd[raw_transition_index])
        ),
        "even_abs_delta": float(
            abs(even[low_count] - corrected_even[raw_transition_index])
        ),
    }
    if max(transition.values()) > 5.0e-3:
        raise Fig8MSTError(f"raw/MST transition mismatch is too large: {transition}")
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "complete": True,
        "kM": kM,
        "raw_path": str(raw_file),
        "raw_sha256": _sha256(raw_file),
        "raw_sidecar_sha256": _sha256(_raw_sidecar_path(raw_file)),
        "raw_range": [2, mst_start - 1],
        "raw_finite_radius_correction": "exp[-i ell(ell+1)/(k r_out)]",
        "mst_range": [mst_start, output_lmax],
        "mst_truncation": truncation,
        "mst_guard_terms": guard_terms,
        "mst_working_dps": working_dps,
        "mst_reference_commit": MST_SOURCE_COMMIT,
        "empirical_phase_offset": False,
        "empirical_blend": False,
        "transition": transition,
        "max_recurrence_residual": float(residual.max()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "post_npz_metadata_failure_recovered_without_recomputation": True,
        "recovery_reason": "raw sidecar path used .npz.json instead of .json",
        "npz_sha256": _sha256(npz_path),
        "strict_paper_reproduction_claim": False,
        "strict_paper_reproduction_limitation": (
            "legacy orphan uses the superseded finite-r_out phase correction"
        ),
    }
    _atomic_json(sidecar_path, metadata)
    return npz_path, sidecar_path


def merge_fig8_mst_dataset(
    *,
    transaction_dir: str | Path,
    output_path: str | Path,
    raw_path: str | Path = DEFAULT_RAW,
    target_lmax: int = 500,
) -> tuple[Path, Path]:
    """Merge four direct-MST transactions and evaluate Appendix-E curves."""

    root = Path(transaction_dir)
    raw = load_fig8_asymptotic_dataset(raw_path)
    records = []
    odd_rows = []
    even_rows = []
    ell = None
    for kM in FIG8_KM_VALUES:
        npz, sidecar = _paths(root, kM)
        if not npz.is_file() or not sidecar.is_file():
            raise Fig8MSTError(f"missing direct MST transaction for kM={kM}")
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        if (
            metadata.get("schema_version") != SCHEMA_VERSION
            or metadata.get("complete") is not True
            or metadata.get("npz_sha256") != _sha256(npz)
        ):
            raise Fig8MSTError(f"invalid direct MST sidecar for kM={kM}")
        with np.load(npz, allow_pickle=False) as data:
            current_ell = np.asarray(data["ell"], dtype=np.int64)
            if ell is None:
                ell = current_ell
            elif not np.array_equal(ell, current_ell):
                raise Fig8MSTError("MST transactions have mismatched ell grids")
            odd_rows.append(np.asarray(data["phase_factor_odd"], np.complex128))
            even_rows.append(np.asarray(data["phase_factor_even"], np.complex128))
        records.append(
            {
                "kM": kM,
                "npz": str(npz),
                "npz_sha256": _sha256(npz),
                "sidecar_sha256": _sha256(sidecar),
                "transition": metadata["transition"],
                "max_recurrence_residual": metadata["max_recurrence_residual"],
            }
        )
    assert ell is not None
    odd = np.stack(odd_rows)
    even = np.stack(even_rows)
    theta = np.asarray(raw.theta, dtype=np.float64)
    reduction_orders = np.asarray(FIG8_REDUCTION_ORDERS, dtype=np.int64)
    ladder = np.asarray((302, 402, int(ell[-1])), dtype=np.int64)
    curve_shape = (len(FIG8_KM_VALUES), reduction_orders.size, theta.size)
    M22 = np.empty(curve_shape, dtype=np.complex128)
    M12 = np.empty_like(M22)
    cross_section = np.empty(curve_shape, dtype=np.float64)
    ladder_cross = np.empty(
        (len(FIG8_KM_VALUES), ladder.size, reduction_orders.size, theta.size),
        dtype=np.float64,
    )
    for frequency_index, kM in enumerate(FIG8_KM_VALUES):
        for ladder_index, supplied_lmax in enumerate(ladder):
            count = int(supplied_lmax) - 1
            series = parity_scattering_series(
                even[frequency_index, :count],
                odd[frequency_index, :count],
                ell=ell[:count],
            )
            common_target = (
                target_lmax
                if int(supplied_lmax) == int(ell[-1])
                else int(supplied_lmax) - max(FIG8_REDUCTION_ORDERS)
            )
            for order_index, order in enumerate(FIG8_REDUCTION_ORDERS):
                result = scattering_matrix_cross_section(
                    theta,
                    series,
                    k=kM,
                    reduction_order=order,
                    target_lmax=common_target,
                )
                ladder_cross[frequency_index, ladder_index, order_index] = (
                    result.differential_cross_section
                )
                if int(supplied_lmax) == int(ell[-1]):
                    M22[frequency_index, order_index] = result.M22
                    M12[frequency_index, order_index] = result.M12
                    cross_section[frequency_index, order_index] = (
                        result.differential_cross_section
                    )
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "figure": 8,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "convention": {
            "units": "G=c=M=1",
            "fourier": "exp(-i k t)",
            "parity": "even=Zerilli (+1), odd=Regge-Wheeler (-1)",
        },
        "transactions": records,
        "tail": {
            "method": "direct numerical Schwarzschild MST recurrence",
            "direct_mst_phase_solver_used": True,
            "empirical_overlap_blend_used": False,
            "empirical_phase_offset_used": False,
            "mst_reference_commit": MST_SOURCE_COMMIT,
        },
        "common_target_lmax": target_lmax,
        "supplied_phase_lmax": int(ell[-1]),
        "strict_paper_reproduction_claim": False,
        "strict_paper_reproduction_limitation": (
            "external odd-sector BHPT/MST phase benchmark passed; independent "
            "even-sector radial normalization and Li q=2 raw reference data "
            "remain unavailable"
        ),
        "lmax_ladder_diagnostics": _ladder_diagnostics(
            ladder, ladder_cross, theta=theta
        ),
        "forward_axis": {
            "theta_zero_present": False,
            "policy": "excluded; theta grid is (0, pi]",
        },
    }
    dataset = Fig8AsymptoticDataset(
        kM=np.asarray(FIG8_KM_VALUES, dtype=np.float64),
        ell=ell,
        phase_factor_odd=odd,
        phase_factor_even=even,
        theta=theta,
        reduction_orders=reduction_orders,
        M22=M22,
        M12=M12,
        differential_cross_section=cross_section,
        lmax_ladder=ladder,
        lmax_ladder_cross_section=ladder_cross,
        metadata=metadata,
    )
    return save_fig8_asymptotic_dataset(dataset, output_path)


def _jost_low_phase_ladder(
    *,
    kM: float,
    ell: np.ndarray,
    r_out_ladder: tuple[float, ...],
    outer_series_order: int,
    progress: Callable[[dict[str, Any]], None] | None,
):
    radii = np.asarray(r_out_ladder, dtype=np.float64)
    if radii.shape[0] < 3 or np.any(np.diff(radii) <= 0.0):
        raise Fig8MSTError("low-r_out ladder must contain at least three increasing radii")
    background = SchwarzschildBackground(M=1.0)
    odd = np.empty((radii.size, ell.size), dtype=np.complex128)
    even = np.empty_like(odd)
    total = int(radii.size * ell.size * 2)
    completed = 0
    for radius_index, radius in enumerate(radii):
        boundary = BoundaryConfig(
            r_in_eps=1.0e-6,
            r_out=float(radius),
            rtol=1.0e-11,
            atol=1.0e-13,
            outer_basis="jost_1_over_r",
            outer_series_order=outer_series_order,
        )
        for ell_index, ell_value in enumerate(ell):
            for sector, destination in ((Sector.ODD, odd), (Sector.EVEN, even)):
                solution = solve_radial_mode(
                    sector, int(ell_value), kM, background, boundary
                )
                destination[radius_index, ell_index] = solution.phase_factor
                completed += 1
                if progress is not None and (completed == 1 or completed % 25 == 0):
                    progress(
                        {
                            "event": "fig8_low_jost_ladder_progress",
                            "kM": kM,
                            "completed": completed,
                            "total": total,
                            "ell": int(ell_value),
                            "r_out": float(radius),
                            "sector": sector.value,
                        }
                    )
    odd_fit = extrapolate_r_out_ladder(radii, odd)
    even_fit = extrapolate_r_out_ladder(radii, even)
    return odd, even, odd_fit, even_fit


def _atomic_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    if path.exists():
        raise Fig8MSTError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".npz", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        np.savez(temporary, **arrays)
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    if path.exists():
        raise Fig8MSTError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        dir=path.parent, mode="w", encoding="utf-8", delete=False
    ) as handle:
        temporary = Path(handle.name)
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


__all__ = [
    "DEFAULT_RAW",
    "Fig8MSTError",
    "finalize_fig8_mst_frequency",
    "merge_fig8_mst_dataset",
    "produce_fig8_mst_frequency",
]
