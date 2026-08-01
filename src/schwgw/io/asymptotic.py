"""Durable Fig. 8 asymptotic-scattering datasets.

This module is intentionally separate from the finite-radius production
artifacts.  It records the radial solver's branch-free ``phase_factor`` and
the three truncated Appendix-E approximants used only for Fig. 8.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import numpy as np

from schwgw.scattering.asymptotic import (
    matched_schwarzschild_phase_factors,
    parity_scattering_series,
    scattering_matrix_cross_section,
)


FIG8_KM_VALUES = (0.5, 1.0, 1.5, 2.0)
FIG8_REDUCTION_ORDERS = (0, 1, 2)
FIG8_SCHEMA_VERSION = "schwgw_fig8_asymptotic_scattering_v1"
FIG8_HYBRID_SCHEMA_VERSION = "schwgw_fig8_matched_schwarzschild_tail_v2"
RadialSolver = Callable[..., Any]
ProgressCallback = Callable[[dict[str, Any]], None]


@dataclass(frozen=True)
class Fig8AsymptoticDataset:
    """Saved direct-phase-factor scattering data for the four Fig. 8 panels."""

    kM: np.ndarray
    ell: np.ndarray
    phase_factor_odd: np.ndarray
    phase_factor_even: np.ndarray
    theta: np.ndarray
    reduction_orders: np.ndarray
    M22: np.ndarray
    M12: np.ndarray
    differential_cross_section: np.ndarray
    lmax_ladder: np.ndarray
    lmax_ladder_cross_section: np.ndarray
    metadata: dict[str, Any]

    def __post_init__(self) -> None:
        _validate_dataset(self)


def default_fig8_theta_grid(*, count: int = 720) -> np.ndarray:
    """Return a uniform grid on ``(0, pi]`` with no forward-axis sample."""

    if isinstance(count, bool) or not isinstance(count, int) or count < 2:
        raise ValueError("Fig. 8 theta count must be an integer of at least 2.")
    return np.linspace(np.pi / count, np.pi, count, dtype=np.float64)


def produce_fig8_asymptotic_dataset(
    *,
    lmax: int,
    theta: Sequence[float] | np.ndarray | None = None,
    lmax_ladder: Sequence[int] | None = None,
    radial_solver: RadialSolver | None = None,
    progress: ProgressCallback | None = None,
    source_command: Sequence[str] | None = None,
) -> Fig8AsymptoticDataset:
    """Produce a Fig. 8 dataset using an injectable radial-mode solver.

    The default solver is :func:`solve_radial_mode`; tests should inject a
    cheap synthetic solver.  Phase shifts are deliberately never read: the
    stored input is exactly ``solution.phase_factor`` for each parity sector.
    """

    minimum_lmax = 2 + max(FIG8_REDUCTION_ORDERS)
    if isinstance(lmax, bool) or not isinstance(lmax, int) or lmax < minimum_lmax:
        raise ValueError(
            "Fig. 8 lmax must supply the q=2 upper edge and be at least 4."
        )
    theta_values = (
        default_fig8_theta_grid()
        if theta is None
        else np.asarray(theta, dtype=np.float64)
    )
    _validate_theta_grid(theta_values)
    ladder = _normalise_ladder(lmax, lmax_ladder)
    if radial_solver is None:
        from schwgw.numerics import solve_radial_mode as solver
    else:
        solver = radial_solver
    from schwgw.backgrounds import SchwarzschildBackground
    from schwgw.numerics import BoundaryConfig
    from schwgw.perturbations import Sector

    background = SchwarzschildBackground(M=1.0)
    boundary = BoundaryConfig(r_in_eps=1.0e-6, r_out=300.0, rtol=1.0e-10, atol=1.0e-12)
    ell = np.arange(2, lmax + 1, dtype=np.int64)
    shape_modes = (len(FIG8_KM_VALUES), ell.size)
    odd = np.empty(shape_modes, dtype=np.complex128)
    even = np.empty(shape_modes, dtype=np.complex128)
    radial_diagnostics: dict[str, dict[str, list[dict[str, Any]]]] = {}
    total = len(FIG8_KM_VALUES) * ell.size * 2
    completed = 0
    for frequency_index, kM in enumerate(FIG8_KM_VALUES):
        k = kM / background.M
        frequency_diagnostics = {"odd": [], "even": []}
        for ell_index, ell_value in enumerate(ell):
            for sector, destination, label in (
                (Sector.ODD, odd, "odd"),
                (Sector.EVEN, even, "even"),
            ):
                solution = solver(sector, int(ell_value), k, background, boundary)
                phase_factor = complex(solution.phase_factor)
                if not np.isfinite(phase_factor.real) or not np.isfinite(
                    phase_factor.imag
                ):
                    raise ValueError(
                        "Fig. 8 radial solver returned a non-finite phase_factor."
                    )
                destination[frequency_index, ell_index] = phase_factor
                frequency_diagnostics[label].append(
                    {
                        "ell": int(ell_value),
                        "diagnostics": _json_safe(
                            getattr(solution, "diagnostics", None)
                        ),
                    }
                )
                completed += 1
                if progress is not None:
                    progress(
                        {
                            "event": "fig8_radial_mode_progress",
                            "completed": completed,
                            "total": total,
                            "kM": kM,
                            "ell": int(ell_value),
                            "sector": label,
                        }
                    )
        radial_diagnostics[f"{kM:g}"] = frequency_diagnostics

    curve_shape = (len(FIG8_KM_VALUES), len(FIG8_REDUCTION_ORDERS), theta_values.size)
    M22 = np.empty(curve_shape, dtype=np.complex128)
    M12 = np.empty_like(M22)
    cross_section = np.empty(curve_shape, dtype=np.float64)
    ladder_cross_section = np.empty(
        (
            len(FIG8_KM_VALUES),
            ladder.size,
            len(FIG8_REDUCTION_ORDERS),
            theta_values.size,
        ),
        dtype=np.float64,
    )
    for frequency_index, kM in enumerate(FIG8_KM_VALUES):
        k = kM / background.M
        full_series = parity_scattering_series(
            even[frequency_index], odd[frequency_index], ell=ell
        )
        common_target_lmax = int(ell[-1]) - max(FIG8_REDUCTION_ORDERS)
        for order_index, order in enumerate(FIG8_REDUCTION_ORDERS):
            result = scattering_matrix_cross_section(
                theta_values,
                full_series,
                k=k,
                reduction_order=order,
                target_lmax=common_target_lmax,
            )
            M22[frequency_index, order_index] = result.M22
            M12[frequency_index, order_index] = result.M12
            cross_section[frequency_index, order_index] = (
                result.differential_cross_section
            )
        for ladder_index, ladder_lmax in enumerate(ladder):
            count = int(ladder_lmax) - 1
            ladder_target_lmax = int(ladder_lmax) - max(FIG8_REDUCTION_ORDERS)
            series = parity_scattering_series(
                even[frequency_index, :count],
                odd[frequency_index, :count],
                ell=ell[:count],
            )
            for order_index, order in enumerate(FIG8_REDUCTION_ORDERS):
                ladder_cross_section[frequency_index, ladder_index, order_index] = (
                    scattering_matrix_cross_section(
                        theta_values,
                        series,
                        k=k,
                        reduction_order=order,
                        target_lmax=ladder_target_lmax,
                    ).differential_cross_section
                )

    metadata = {
        "schema_version": FIG8_SCHEMA_VERSION,
        "figure": 8,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "convention": {
            "units": "G=c=M=1",
            "fourier": "exp(-i k t)",
            "phase_input": "solution.phase_factor=exp(2 i delta); phase_shift is not read",
            "parity": "even=Zerilli (+1), odd=Regge-Wheeler (-1)",
        },
        "boundary": asdict(boundary),
        "provenance": {
            "radial_solver": getattr(solver, "__module__", type(solver).__module__)
            + "."
            + getattr(solver, "__qualname__", type(solver).__qualname__),
            "source_command": list(source_command)
            if source_command is not None
            else None,
            "fixed_kM_order": list(FIG8_KM_VALUES),
        },
        "radial_diagnostics": radial_diagnostics,
        "lmax_ladder_diagnostics": _ladder_diagnostics(ladder, ladder_cross_section),
        "forward_axis": {
            "theta_zero_present": False,
            "policy": "excluded; theta grid is (0, pi]",
        },
    }
    return Fig8AsymptoticDataset(
        kM=np.asarray(FIG8_KM_VALUES, dtype=np.float64),
        ell=ell,
        phase_factor_odd=odd,
        phase_factor_even=even,
        theta=theta_values,
        reduction_orders=np.asarray(FIG8_REDUCTION_ORDERS, dtype=np.int64),
        M22=M22,
        M12=M12,
        differential_cross_section=cross_section,
        lmax_ladder=ladder,
        lmax_ladder_cross_section=ladder_cross_section,
        metadata=metadata,
    )


def build_fig8_matched_dataset(
    raw: Fig8AsymptoticDataset,
    *,
    output_lmax: int = 502,
    target_lmax: int = 500,
    overlap_half_width: int = 15,
    r_out: float = 300.0,
    source_record: Mapping[str, Any] | None = None,
) -> Fig8AsymptoticDataset:
    """Post-process saved numerical phases into the converged Fig. 8 series.

    No radial solver is called.  The four fixed numerical phase sequences are
    corrected at leading finite radius, matched in a nonabsorptive overlap to
    the Schwarzschild Coulomb/MST tail, and evaluated with a common target
    cutoff for all three Appendix-E reduction orders.
    """

    if not isinstance(raw, Fig8AsymptoticDataset):
        raise TypeError("raw must be a Fig8AsymptoticDataset instance.")
    if not np.array_equal(raw.kM, np.asarray(FIG8_KM_VALUES)):
        raise ValueError("raw Fig. 8 frequencies are not in the fixed order.")
    if output_lmax < target_lmax + max(FIG8_REDUCTION_ORDERS):
        raise ValueError("output_lmax must supply the common q=2 upper edge.")
    if target_lmax < 4:
        raise ValueError("target_lmax must be at least 4.")
    if (
        isinstance(overlap_half_width, bool)
        or not isinstance(overlap_half_width, int)
        or overlap_half_width < 2
    ):
        raise ValueError("overlap_half_width must be an integer of at least 2.")

    theta = np.asarray(raw.theta, dtype=np.float64)
    ell = np.arange(2, output_lmax + 1, dtype=np.int64)
    odd = np.empty((len(FIG8_KM_VALUES), ell.size), dtype=np.complex128)
    even = np.empty_like(odd)
    matching: dict[str, Any] = {}
    for index, kM in enumerate(FIG8_KM_VALUES):
        center = int(round(60.0 * kM))
        overlap = (center - overlap_half_width, center + overlap_half_width)
        matched = matched_schwarzschild_phase_factors(
            raw.phase_factor_odd[index],
            raw.phase_factor_even[index],
            raw.ell,
            k=kM,
            r_out=r_out,
            output_lmax=output_lmax,
            overlap_ell=overlap,
        )
        odd[index] = matched.odd
        even[index] = matched.even
        matching[f"{kM:g}"] = {
            "overlap_ell": list(matched.overlap_ell),
            "tail_phase_offset_radians": matched.tail_phase_offset,
            "maximum_overlap_phase_residual_radians": (
                matched.maximum_overlap_phase_residual
            ),
        }

    curve_shape = (len(FIG8_KM_VALUES), len(FIG8_REDUCTION_ORDERS), theta.size)
    M22 = np.empty(curve_shape, dtype=np.complex128)
    M12 = np.empty_like(M22)
    cross_section = np.empty(curve_shape, dtype=np.float64)
    phase_ladder = np.asarray((302, 402, output_lmax), dtype=np.int64)
    if output_lmax < 402:
        phase_ladder = np.asarray((output_lmax,), dtype=np.int64)
    ladder_cross_section = np.empty(
        (
            len(FIG8_KM_VALUES),
            phase_ladder.size,
            len(FIG8_REDUCTION_ORDERS),
            theta.size,
        ),
        dtype=np.float64,
    )
    for frequency_index, kM in enumerate(FIG8_KM_VALUES):
        for ladder_index, phase_lmax in enumerate(phase_ladder):
            count = int(phase_lmax) - 1
            ladder_series = parity_scattering_series(
                even[frequency_index, :count],
                odd[frequency_index, :count],
                ell=ell[:count],
            )
            common_target = (
                target_lmax
                if int(phase_lmax) == output_lmax
                else int(phase_lmax) - max(FIG8_REDUCTION_ORDERS)
            )
            for order_index, order in enumerate(FIG8_REDUCTION_ORDERS):
                result = scattering_matrix_cross_section(
                    theta,
                    ladder_series,
                    k=kM,
                    reduction_order=order,
                    target_lmax=common_target,
                )
                ladder_cross_section[
                    frequency_index, ladder_index, order_index
                ] = result.differential_cross_section
                if int(phase_lmax) == output_lmax:
                    M22[frequency_index, order_index] = result.M22
                    M12[frequency_index, order_index] = result.M12
                    cross_section[frequency_index, order_index] = (
                        result.differential_cross_section
                    )

    metadata = {
        "schema_version": FIG8_HYBRID_SCHEMA_VERSION,
        "figure": 8,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "no_radial_solver_rerun": True,
        "source_record": _json_safe(source_record),
        "convention": {
            "units": "G=c=M=1",
            "fourier": "exp(-i k t)",
            "parity": "even=Zerilli (+1), odd=Regge-Wheeler (-1)",
        },
        "finite_radius_phase_correction": "exp[-i ell(ell+1)/(k r_out)]",
        "r_out": float(r_out),
        "tail": {
            "method": "Poisson-Sasaki/Dolan Schwarzschild large-ell Coulomb-MST tail",
            "matching": matching,
            "blend": "raised cosine in phase and log amplitude",
        },
        "common_target_lmax": int(target_lmax),
        "supplied_phase_lmax": int(output_lmax),
        "lmax_ladder_diagnostics": _ladder_diagnostics(
            phase_ladder, ladder_cross_section
        ),
        "forward_axis": {
            "theta_zero_present": False,
            "policy": "excluded; theta grid is (0, pi]",
        },
    }
    return Fig8AsymptoticDataset(
        kM=np.asarray(FIG8_KM_VALUES, dtype=np.float64),
        ell=ell,
        phase_factor_odd=odd,
        phase_factor_even=even,
        theta=theta,
        reduction_orders=np.asarray(FIG8_REDUCTION_ORDERS, dtype=np.int64),
        M22=M22,
        M12=M12,
        differential_cross_section=cross_section,
        lmax_ladder=phase_ladder,
        lmax_ladder_cross_section=ladder_cross_section,
        metadata=metadata,
    )


def save_fig8_asymptotic_dataset(
    result: Fig8AsymptoticDataset, path: str | Path
) -> tuple[Path, Path]:
    """Atomically write no-pickle NPZ arrays and a matching JSON sidecar.

    Existing NPZ *or* JSON paths are never overwritten.
    """

    _validate_dataset(result)
    output = Path(path)
    if output.suffix.lower() != ".npz":
        raise ValueError("Fig. 8 dataset path must end with .npz.")
    sidecar = output.with_suffix(".json")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() or sidecar.exists():
        raise FileExistsError(
            f"Refusing to overwrite Fig. 8 artifact pair: {output}, {sidecar}"
        )
    metadata_json = json.dumps(result.metadata, sort_keys=True, separators=(",", ":"))
    payload = {name: getattr(result, name) for name in _ARRAY_FIELDS}
    payload["metadata_json"] = np.asarray(metadata_json)
    temporary_npz: Path | None = None
    temporary_json: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w+b",
            prefix=f".{output.name}.",
            suffix=".partial",
            dir=output.parent,
            delete=False,
        ) as handle:
            temporary_npz = Path(handle.name)
            np.savez(handle, **payload)
            handle.flush()
            os.fsync(handle.fileno())
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix=f".{sidecar.name}.",
            suffix=".partial",
            dir=sidecar.parent,
            delete=False,
        ) as handle:
            temporary_json = Path(handle.name)
            handle.write(metadata_json + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_npz, output)
        temporary_npz = None
        os.replace(temporary_json, sidecar)
        temporary_json = None
        _fsync_directory(output.parent)
    finally:
        for temporary in (temporary_npz, temporary_json):
            if temporary is not None and temporary.exists():
                temporary.unlink()
    return output, sidecar


def load_fig8_asymptotic_dataset(path: str | Path) -> Fig8AsymptoticDataset:
    """Load a Fig. 8 artifact pair and enforce its complete schema."""

    source = Path(path)
    if source.suffix.lower() != ".npz":
        raise ValueError("Fig. 8 dataset path must end with .npz.")
    sidecar = source.with_suffix(".json")
    if not sidecar.is_file():
        raise ValueError(f"Fig. 8 metadata sidecar is missing: {sidecar}")
    try:
        external_metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("Fig. 8 metadata sidecar is not valid JSON.") from exc
    if not isinstance(external_metadata, dict):
        raise ValueError("Fig. 8 metadata sidecar must be a JSON object.")
    required = set(_ARRAY_FIELDS) | {"metadata_json"}
    with np.load(source, allow_pickle=False) as data:
        if set(data.files) != required:
            raise ValueError("Fig. 8 NPZ fields do not match the strict schema.")
        for name in _ARRAY_FIELDS:
            if data[name].dtype != np.dtype(_FIELD_DTYPES[name]):
                raise ValueError(f"Fig. 8 NPZ field {name} has an invalid dtype.")
        try:
            embedded_metadata = json.loads(str(data["metadata_json"]))
        except json.JSONDecodeError as exc:
            raise ValueError("Fig. 8 embedded metadata is not valid JSON.") from exc
        if embedded_metadata != external_metadata:
            raise ValueError("Fig. 8 NPZ and JSON sidecar metadata differ.")
        result = Fig8AsymptoticDataset(
            **{
                name: np.asarray(data[name], dtype=_FIELD_DTYPES[name])
                for name in _ARRAY_FIELDS
            },
            metadata=external_metadata,
        )
    return result


_ARRAY_FIELDS = (
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
_FIELD_DTYPES = {
    "kM": np.float64,
    "ell": np.int64,
    "phase_factor_odd": np.complex128,
    "phase_factor_even": np.complex128,
    "theta": np.float64,
    "reduction_orders": np.int64,
    "M22": np.complex128,
    "M12": np.complex128,
    "differential_cross_section": np.float64,
    "lmax_ladder": np.int64,
    "lmax_ladder_cross_section": np.float64,
}


def _normalise_ladder(lmax: int, ladder: Sequence[int] | None) -> np.ndarray:
    values = [lmax] if ladder is None else list(ladder)
    if not values or any(
        isinstance(value, bool) or not isinstance(value, int) for value in values
    ):
        raise ValueError("Fig. 8 lmax ladder must contain integer values.")
    if (
        values[-1] != lmax
        or any(value < 2 + max(FIG8_REDUCTION_ORDERS) for value in values)
        or any(b <= a for a, b in zip(values, values[1:]))
    ):
        raise ValueError("Fig. 8 lmax ladder must strictly increase and end at lmax.")
    return np.asarray(values, dtype=np.int64)


def _validate_dataset(result: Fig8AsymptoticDataset) -> None:
    if not isinstance(result, Fig8AsymptoticDataset):
        raise TypeError("result must be a Fig8AsymptoticDataset instance.")
    kM, ell, theta, orders, ladder = (
        np.asarray(getattr(result, name))
        for name in ("kM", "ell", "theta", "reduction_orders", "lmax_ladder")
    )
    if not np.array_equal(kM, np.asarray(FIG8_KM_VALUES)):
        raise ValueError("Fig. 8 kM must be exactly (0.5, 1, 1.5, 2) in that order.")
    if ell.ndim != 1 or not np.array_equal(ell, np.arange(2, ell.size + 2)):
        raise ValueError("Fig. 8 ell must be the contiguous range 2..lmax.")
    _validate_theta_grid(theta)
    if not np.array_equal(orders, np.asarray(FIG8_REDUCTION_ORDERS)):
        raise ValueError("Fig. 8 reduction orders must be exactly (0, 1, 2).")
    _normalise_ladder(int(ell[-1]), [int(value) for value in ladder])
    expected_modes = (4, ell.size)
    expected_curves = (4, 3, theta.size)
    if (
        np.asarray(result.phase_factor_odd).shape != expected_modes
        or np.asarray(result.phase_factor_even).shape != expected_modes
    ):
        raise ValueError("Fig. 8 phase-factor arrays have an invalid shape.")
    for name in ("M22", "M12", "differential_cross_section"):
        if np.asarray(getattr(result, name)).shape != expected_curves:
            raise ValueError(f"Fig. 8 {name} has an invalid shape.")
    if np.asarray(result.lmax_ladder_cross_section).shape != (
        4,
        ladder.size,
        3,
        theta.size,
    ):
        raise ValueError("Fig. 8 lmax ladder cross sections have an invalid shape.")
    for name in ("phase_factor_odd", "phase_factor_even", "M22", "M12"):
        values = np.asarray(getattr(result, name), dtype=np.complex128)
        if not np.all(np.isfinite(values.real)) or not np.all(np.isfinite(values.imag)):
            raise ValueError(f"Fig. 8 {name} must be finite.")
    for name in ("differential_cross_section", "lmax_ladder_cross_section"):
        values = np.asarray(getattr(result, name), dtype=np.float64)
        if not np.all(np.isfinite(values)) or np.any(values < 0.0):
            raise ValueError(f"Fig. 8 {name} must be finite and nonnegative.")
    expected_cross_section = (
        np.abs(np.asarray(result.M22)) ** 2 + np.abs(np.asarray(result.M12)) ** 2
    )
    if not np.allclose(
        result.differential_cross_section,
        expected_cross_section,
        rtol=2e-12,
        atol=2e-12,
    ):
        raise ValueError("Fig. 8 cross section must equal |M22|^2+|M12|^2.")
    metadata = result.metadata
    if not isinstance(metadata, dict) or metadata.get("schema_version") not in {
        FIG8_SCHEMA_VERSION,
        FIG8_HYBRID_SCHEMA_VERSION,
    }:
        raise ValueError("Fig. 8 metadata has an invalid schema version.")
    if metadata["schema_version"] == FIG8_SCHEMA_VERSION:
        if not isinstance(metadata.get("radial_diagnostics"), dict) or not isinstance(
            metadata.get("provenance"), dict
        ):
            raise ValueError(
                "Fig. 8 metadata must retain radial diagnostics and provenance."
            )
    elif not isinstance(metadata.get("tail"), dict) or not isinstance(
        metadata.get("source_record"), dict
    ):
        raise ValueError("Matched Fig. 8 metadata must retain tail and source records.")


def _ladder_diagnostics(ladder: np.ndarray, values: np.ndarray) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for previous_index, current_index in zip(
        range(ladder.size - 1), range(1, ladder.size)
    ):
        old, new = values[:, previous_index], values[:, current_index]
        relative = np.abs(new - old) / np.maximum(
            np.maximum(np.abs(new), np.abs(old)), 1.0e-30
        )
        records.append(
            {
                "previous_lmax": int(ladder[previous_index]),
                "current_lmax": int(ladder[current_index]),
                "max_relative_change": float(np.max(relative)),
            }
        )
    return records


def _validate_theta_grid(theta: np.ndarray) -> None:
    if (
        theta.ndim != 1
        or theta.size < 2
        or not np.all(np.isfinite(theta))
        or np.any(theta <= 0.0)
        or np.any(theta > np.pi)
        or np.any(np.diff(theta) <= 0.0)
    ):
        raise ValueError("Fig. 8 theta must be a strictly increasing grid in (0, pi].")


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, np.generic):
        return _json_safe(value.item())
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    try:
        return _json_safe(asdict(value))
    except TypeError:
        return repr(value)


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


__all__ = [
    "FIG8_HYBRID_SCHEMA_VERSION",
    "FIG8_KM_VALUES",
    "FIG8_REDUCTION_ORDERS",
    "FIG8_SCHEMA_VERSION",
    "Fig8AsymptoticDataset",
    "build_fig8_matched_dataset",
    "default_fig8_theta_grid",
    "load_fig8_asymptotic_dataset",
    "produce_fig8_asymptotic_dataset",
    "save_fig8_asymptotic_dataset",
]
