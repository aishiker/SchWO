"""Direct Fig. 5/6 reconstruction using the inferred paper response surface.

This production path is deliberately separate from the accepted Route-B
uniform artifact.  It reuses the same 40 frequencies, Table-I observation
points, radial solver, boundary tolerances, and accepted final ``lmax`` pairs,
but evaluates the explicitly labelled Li--Hou--Zhao Eq. (42) response-column
hypothesis instead of the project's packaged polarization observable.  The
production sidecar also binds the selected Eq. (35g)--(35h) radial-source
convention so that linear and literal-conjugate transactions cannot mix.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any
import warnings

import numpy as np

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.io.tablei import TABLEI_POINTS
from schwgw.io.tablei_risk_pilot import _FrequencyRadialCache
from schwgw.io.tablei_uniform import (
    CONVERGENCE_TOLERANCE,
    UNIFORM_FREQUENCIES,
    _atomic_json_no_overwrite,
    _atomic_npz_no_overwrite,
    _json_safe,
    _sha256,
    _uniform_radial_solver,
)
from schwgw.numerics import BoundaryConfig
from schwgw.scattering.paper_projection import (
    LHZEq42ResponseResult,
    compute_lhz_eq42_response_columns,
    strict_np_vector,
)


SCHEMA_VERSION = "phase5_fig5_fig6_lhz_eq42_response_columns_v1"
DEFAULT_SOURCE_MERGE = Path(
    "runs/phase5/fig5_fig6_uniform40_direct_production/"
    "tablei_uniform40_merged.npz"
)
AMPLITUDES = {"plus": 0.9 + 1.1j, "cross": 0.4 + 0.6j}


class PaperInferredTableIError(ValueError):
    """Raised when the inferred Fig. 5/6 production contract is violated."""


def _token(km: float) -> str:
    return f"{km:g}".replace(".", "p")


def _frequency_paths(output_dir: Path, km: float) -> tuple[Path, Path]:
    npz = output_dir / "frequencies" / f"kM_{_token(km)}.npz"
    return npz, Path(str(npz) + ".json")


def _relative_delta(final: np.ndarray, previous: np.ndarray) -> np.ndarray:
    return np.abs(final - previous) / np.maximum(
        1.0,
        np.maximum(np.abs(final), np.abs(previous)),
    )


def _read_metadata_json(data: Mapping[str, np.ndarray]) -> dict[str, Any]:
    try:
        raw = np.asarray(data["metadata_json"]).item()
        value = json.loads(str(raw))
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise PaperInferredTableIError("invalid source metadata_json") from exc
    if not isinstance(value, dict):
        raise PaperInferredTableIError("source metadata_json must be an object")
    return value


def _lmax_pair_from_binding(binding: Mapping[str, Any]) -> tuple[int, int]:
    try:
        km = float(binding["kM"])
        source = Path(str(binding["source"]))
        expected_hash = str(binding["sha256"])
    except (KeyError, TypeError, ValueError) as exc:
        raise PaperInferredTableIError("malformed source binding") from exc
    if not source.is_file() or _sha256(source) != expected_hash:
        raise PaperInferredTableIError(f"source binding identity mismatch: {source}")

    with np.load(source, allow_pickle=False) as data:
        pair: np.ndarray | None = None
        if "lmax_values" in data.files:
            lmax_values = np.asarray(data["lmax_values"], dtype=int)
            if lmax_values.ndim == 1 and lmax_values.size >= 2:
                pair = lmax_values[-2:]
        elif "final_lmax_pair" in data.files:
            try:
                row = int(binding["row"])
                pair = np.asarray(data["final_lmax_pair"][row], dtype=int)
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                raise PaperInferredTableIError(
                    f"invalid final_lmax_pair binding for kM={km}"
                ) from exc
        else:
            metadata = _read_metadata_json(data)
            records = metadata.get("frequency_metadata")
            if not isinstance(records, list):
                raise PaperInferredTableIError(
                    f"source has no lmax record for kM={km}"
                )
            matches = [
                record
                for record in records
                if isinstance(record, dict)
                and abs(float(record.get("kM", np.nan)) - km) <= 1.0e-12
            ]
            if len(matches) != 1:
                raise PaperInferredTableIError(
                    f"source has ambiguous lmax metadata for kM={km}"
                )
            raw_pair = matches[0].get(
                "final_lmax_pair",
                matches[0].get("final_pair"),
            )
            pair = np.asarray(raw_pair, dtype=int)

    if pair is None or pair.shape != (2,):
        raise PaperInferredTableIError(f"invalid lmax pair for kM={km}")
    result = (int(pair[0]), int(pair[1]))
    if result[0] < 2 or result[0] >= result[1]:
        raise PaperInferredTableIError(f"non-increasing lmax pair for kM={km}")
    return result


def load_uniform_source_contract(
    source_merged_npz: str | Path = DEFAULT_SOURCE_MERGE,
) -> tuple[dict[float, tuple[int, int]], list[dict[str, Any]]]:
    """Load the exact 40-row source binding and its accepted final lmax pairs."""

    source = Path(source_merged_npz)
    sidecar = Path(str(source) + ".json")
    if not source.is_file() or not sidecar.is_file():
        raise PaperInferredTableIError("missing uniform-40 source or sidecar")
    try:
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PaperInferredTableIError("cannot read uniform-40 source sidecar") from exc
    bindings = metadata.get("source_binding")
    if not isinstance(bindings, list) or len(bindings) != len(UNIFORM_FREQUENCIES):
        raise PaperInferredTableIError("uniform-40 source binding is incomplete")

    with np.load(source, allow_pickle=False) as data:
        if not np.array_equal(
            np.asarray(data["kM_values"], dtype=float),
            np.asarray(UNIFORM_FREQUENCIES, dtype=float),
        ):
            raise PaperInferredTableIError("uniform source frequency grid changed")
        expected_ids = np.asarray([point.point_id for point in TABLEI_POINTS])
        if not np.array_equal(np.asarray(data["point_ids"]).astype(str), expected_ids):
            raise PaperInferredTableIError("uniform source Table-I point order changed")

    schedule: dict[float, tuple[int, int]] = {}
    frozen_bindings: list[dict[str, Any]] = []
    for expected_km, raw in zip(UNIFORM_FREQUENCIES, bindings, strict=True):
        if not isinstance(raw, dict) or float(raw.get("kM", np.nan)) != expected_km:
            raise PaperInferredTableIError("uniform source binding order changed")
        pair = _lmax_pair_from_binding(raw)
        schedule[expected_km] = pair
        frozen_bindings.append(
            {
                "kM": expected_km,
                "lmax_pair": list(pair),
                "kind": raw.get("kind"),
                "source": raw.get("source"),
                "source_sha256": raw.get("sha256"),
                "row": raw.get("row"),
            }
        )
    return schedule, frozen_bindings


def _warning_summary(caught: Sequence[warnings.WarningMessage]) -> dict[str, Any]:
    counts = Counter(
        f"{item.category.__module__}.{item.category.__qualname__}: {item.message}"
        for item in caught
    )
    return {
        "count": int(sum(counts.values())),
        "unique_count": len(counts),
        "records": [
            {"message": message, "count": count}
            for message, count in sorted(counts.items())
        ],
    }


def _compute_frequency(
    kM: float,
    *,
    lmax_pair: tuple[int, int],
    response_solver: Callable[..., LHZEq42ResponseResult],
    radial_solver: Callable[..., Any],
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    started = time.monotonic()
    lmax_values = tuple(int(value) for value in lmax_pair)
    if len(lmax_values) != 2 or lmax_values[0] < 2 or lmax_values[0] >= lmax_values[1]:
        raise PaperInferredTableIError("lmax_pair must contain two increasing values")

    plus = np.empty((2, 8), dtype=np.complex128)
    cross = np.empty_like(plus)
    cross_from_plus = np.empty_like(plus)
    plus_from_cross = np.empty_like(plus)
    plus_np = np.empty((2, 8, 5), dtype=np.complex128)
    cross_np = np.empty_like(plus_np)
    projection_diagnostics: dict[str, object] | None = None
    cache = _FrequencyRadialCache(radial_solver)
    background = SchwarzschildBackground(M=1.0)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        for row, lmax in enumerate(lmax_values):
            for index in sorted(
                range(len(TABLEI_POINTS)),
                key=lambda item: TABLEI_POINTS[item].r,
                reverse=True,
            ):
                point = TABLEI_POINTS[index]
                boundary = BoundaryConfig(
                    r_out=300.0,
                    r_in_eps=1.0e-6,
                    rtol=1.0e-10,
                    atol=1.0e-12,
                    required_eval_radius=point.r,
                )
                result = response_solver(
                    background=background,
                    k=kM,
                    r=point.r,
                    theta=point.theta,
                    phi=point.phi,
                    A_plus=AMPLITUDES["plus"],
                    A_cross=AMPLITUDES["cross"],
                    lmax=lmax,
                    boundary_config=boundary,
                    radial_solver=cache,
                )
                current_diagnostics = dict(result.diagnostics)
                if projection_diagnostics is None:
                    projection_diagnostics = current_diagnostics
                elif (
                    current_diagnostics.get("radial_source_convention")
                    != projection_diagnostics.get("radial_source_convention")
                ):
                    raise PaperInferredTableIError(
                        "response projection convention changed within one frequency"
                    )
                plus[row, index] = result.F_plus
                cross[row, index] = result.F_cross
                cross_from_plus[row, index] = result.h_cross_from_plus
                plus_from_cross[row, index] = result.h_plus_from_cross
                plus_np[row, index] = strict_np_vector(result.plus_strict_np)
                cross_np[row, index] = strict_np_vector(result.cross_strict_np)

    for name, value in {
        "F_plus": plus,
        "F_cross": cross,
        "h_cross_from_plus": cross_from_plus,
        "h_plus_from_cross": plus_from_cross,
        "plus_strict_np": plus_np,
        "cross_strict_np": cross_np,
    }.items():
        if not np.all(np.isfinite(value.real) & np.isfinite(value.imag)):
            raise PaperInferredTableIError(f"non-finite {name} at kM={kM}")

    dplus = _relative_delta(plus[-1], plus[-2])
    dcross = _relative_delta(cross[-1], cross[-2])
    maximum_delta = float(max(dplus.max(), dcross.max()))
    if maximum_delta > CONVERGENCE_TOLERANCE:
        raise PaperInferredTableIError(
            f"final adjacent lmax pair failed at kM={kM}: {maximum_delta}"
        )

    warning_record = _warning_summary(caught)
    metadata: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "complete": True,
        "kM": kM,
        "lmax_values": list(lmax_values),
        "final_lmax_pair": list(lmax_values),
        "convergence_tolerance": CONVERGENCE_TOLERANCE,
        "max_final_pair_delta_plus": float(dplus.max()),
        "max_final_pair_delta_cross": float(dcross.max()),
        "M": 1.0,
        "A_plus_response_probe": AMPLITUDES["plus"],
        "A_cross_response_probe": AMPLITUDES["cross"],
        "boundary": {
            "r_out": 300.0,
            "r_in_eps": 1.0e-6,
            "rtol": 1.0e-10,
            "atol": 1.0e-12,
        },
        "response_surface": "pure-plus diagonal / pure-cross diagonal",
        "projection": "Li-Hou-Zhao Eq. (42) positive-frequency continuation",
        "denominator": "Li-Hou-Zhao Eq. (46) incident plane wave",
        "inference_status": "paper-consistent reconstruction hypothesis",
        "route_b_used": False,
        "psi2_used_in_plus_or_cross": False,
        "radial_source_convention": (
            projection_diagnostics or {}
        ).get("radial_source_convention"),
        "radial_solve_count": int(cache.solve_count),
        "radial_reuse_count": int(cache.reuse_count),
        "warnings": warning_record,
        "runtime_seconds": time.monotonic() - started,
        "no_interpolation": True,
        "no_smoothing": True,
    }
    arrays = {
        "kM": np.asarray(kM),
        "point_ids": np.asarray([point.point_id for point in TABLEI_POINTS]),
        "point_group": np.asarray([point.group for point in TABLEI_POINTS]),
        "point_x": np.asarray([point.x for point in TABLEI_POINTS]),
        "point_y": np.asarray([point.y for point in TABLEI_POINTS]),
        "point_z": np.asarray([point.z for point in TABLEI_POINTS]),
        "point_r": np.asarray([point.r for point in TABLEI_POINTS]),
        "point_theta": np.asarray([point.theta for point in TABLEI_POINTS]),
        "point_phi": np.asarray([point.phi for point in TABLEI_POINTS]),
        "paper_theta_deg": np.asarray(
            [point.paper_theta_deg for point in TABLEI_POINTS]
        ),
        "paper_xi_over_xi0": np.asarray(
            [point.paper_xi_over_xi0 for point in TABLEI_POINTS]
        ),
        "lmax_values": np.asarray(lmax_values),
        "F_plus_history": plus,
        "F_cross_history": cross,
        "F_plus_complex": plus[-1],
        "F_cross_complex": cross[-1],
        "abs_F_plus": np.abs(plus[-1]),
        "abs_F_cross": np.abs(cross[-1]),
        "arg_F_plus_principal": np.angle(plus[-1]),
        "arg_F_cross_principal": np.angle(cross[-1]),
        "final_pair_delta_plus": dplus,
        "final_pair_delta_cross": dcross,
        "h_cross_from_plus_history": cross_from_plus,
        "h_plus_from_cross_history": plus_from_cross,
        "plus_strict_np_history": plus_np,
        "cross_strict_np_history": cross_np,
        "metadata_json": np.asarray(json.dumps(_json_safe(metadata), sort_keys=True)),
    }
    return arrays, metadata


def _transaction_valid(
    npz: Path,
    sidecar: Path,
    *,
    km: float,
    lmax_pair: tuple[int, int],
) -> bool:
    if not npz.is_file() or not sidecar.is_file():
        return False
    try:
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        with np.load(npz, allow_pickle=False) as data:
            okay = (
                float(data["kM"]) == km
                and tuple(np.asarray(data["lmax_values"], dtype=int)) == lmax_pair
                and data["F_plus_complex"].shape == (8,)
                and data["F_cross_complex"].shape == (8,)
                and data["plus_strict_np_history"].shape == (2, 8, 5)
                and data["cross_strict_np_history"].shape == (2, 8, 5)
            )
        return bool(
            okay
            and metadata.get("schema_version") == SCHEMA_VERSION
            and metadata.get("complete") is True
            and float(metadata.get("kM")) == km
            and metadata.get("npz_sha256") == _sha256(npz)
        )
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False


def produce_inferred_tablei_uniform(
    *,
    output_dir: str | Path,
    source_merged_npz: str | Path = DEFAULT_SOURCE_MERGE,
    frequencies: Sequence[float] | None = None,
    resume: bool = False,
    response_solver: Callable[..., LHZEq42ResponseResult] = (
        compute_lhz_eq42_response_columns
    ),
    radial_solver: Callable[..., Any] = _uniform_radial_solver,
    progress: Callable[[Mapping[str, Any]], None] | None = None,
) -> Path:
    """Produce selected direct rows transactionally; never overwrite a row."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    schedule, _ = load_uniform_source_contract(source_merged_npz)
    selected = UNIFORM_FREQUENCIES if frequencies is None else tuple(frequencies)
    if (
        len(set(selected)) != len(selected)
        or any(km not in UNIFORM_FREQUENCIES for km in selected)
        or tuple(sorted(selected)) != selected
    ):
        raise PaperInferredTableIError(
            "frequencies must be a unique ordered subset of the uniform grid"
        )

    for km in selected:
        npz, sidecar = _frequency_paths(output, km)
        pair = schedule[km]
        if npz.exists() or sidecar.exists():
            if resume and _transaction_valid(
                npz,
                sidecar,
                km=km,
                lmax_pair=pair,
            ):
                if progress is not None:
                    progress({"event": "resumed", "kM": km, "path": str(npz)})
                continue
            raise PaperInferredTableIError(
                f"existing transaction is not a verified resume: kM={km}"
            )
        if progress is not None:
            progress({"event": "started", "kM": km, "lmax_pair": list(pair)})
        arrays, metadata = _compute_frequency(
            km,
            lmax_pair=pair,
            response_solver=response_solver,
            radial_solver=radial_solver,
        )
        _atomic_npz_no_overwrite(npz, arrays)
        metadata["npz_sha256"] = _sha256(npz)
        _atomic_json_no_overwrite(sidecar, metadata)
        if progress is not None:
            progress(
                {
                    "event": "completed",
                    "kM": km,
                    "path": str(npz),
                    "runtime_seconds": metadata["runtime_seconds"],
                    "max_final_pair_delta": max(
                        metadata["max_final_pair_delta_plus"],
                        metadata["max_final_pair_delta_cross"],
                    ),
                }
            )
    return output


def merge_inferred_tablei_uniform(
    *,
    transaction_dir: str | Path,
    output_path: str | Path,
    source_merged_npz: str | Path = DEFAULT_SOURCE_MERGE,
) -> Path:
    """Merge all 40 verified inferred-response transactions without filling."""

    root = Path(transaction_dir)
    output = Path(output_path)
    sidecar = Path(str(output) + ".json")
    if output.exists() or sidecar.exists():
        raise PaperInferredTableIError(f"refusing to overwrite merge output {output}")
    source = Path(source_merged_npz)
    schedule, source_bindings = load_uniform_source_contract(source)

    row_names = (
        "F_plus_complex",
        "F_cross_complex",
        "abs_F_plus",
        "abs_F_cross",
        "arg_F_plus_principal",
        "arg_F_cross_principal",
        "final_pair_delta_plus",
        "final_pair_delta_cross",
        "h_cross_from_plus_history",
        "h_plus_from_cross_history",
        "plus_strict_np_history",
        "cross_strict_np_history",
    )
    rows: dict[str, list[np.ndarray]] = {name: [] for name in row_names}
    transaction_bindings: list[dict[str, Any]] = []
    radial_source_conventions: set[str] = set()
    for km in UNIFORM_FREQUENCIES:
        npz, row_sidecar = _frequency_paths(root, km)
        if not _transaction_valid(
            npz,
            row_sidecar,
            km=km,
            lmax_pair=schedule[km],
        ):
            raise PaperInferredTableIError(f"missing/invalid transaction at kM={km}")
        with np.load(npz, allow_pickle=False) as data:
            for name in row_names:
                rows[name].append(np.asarray(data[name]))
            row_metadata = _read_metadata_json(data)
        convention = row_metadata.get("radial_source_convention")
        if not isinstance(convention, str) or not convention:
            raise PaperInferredTableIError(
                f"missing radial-source convention at kM={km}"
            )
        radial_source_conventions.add(convention)
        transaction_bindings.append(
            {
                "kM": km,
                "path": str(npz),
                "npz_sha256": _sha256(npz),
                "sidecar_sha256": _sha256(row_sidecar),
                "lmax_pair": list(schedule[km]),
            }
        )

    if len(radial_source_conventions) != 1:
        raise PaperInferredTableIError(
            "radial-source convention changed across the 40 transactions"
        )

    with np.load(source, allow_pickle=False) as source_data:
        arrays = {
            "kM_values": np.asarray(UNIFORM_FREQUENCIES),
            **{
                name: np.asarray(source_data[name])
                for name in (
                    "point_ids",
                    "point_group",
                    "point_x",
                    "point_y",
                    "point_z",
                    "point_r",
                    "point_theta",
                    "point_phi",
                    "paper_theta_deg",
                    "paper_xi_over_xi0",
                )
            },
        }
    arrays.update({name: np.stack(values) for name, values in rows.items()})
    arrays["arg_F_plus_unwrapped"] = np.unwrap(
        arrays["arg_F_plus_principal"],
        axis=0,
    )
    arrays["arg_F_cross_unwrapped"] = np.unwrap(
        arrays["arg_F_cross_principal"],
        axis=0,
    )
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "complete": True,
        "shape": [40, 8],
        "source_uniform_npz": str(source),
        "source_uniform_sha256": _sha256(source),
        "source_lmax_bindings": source_bindings,
        "transactions": transaction_bindings,
        "response_surface": "pure-plus diagonal / pure-cross diagonal",
        "projection": "Li-Hou-Zhao Eq. (42) positive-frequency continuation",
        "denominator": "Li-Hou-Zhao Eq. (46) incident plane wave",
        "inference_status": "paper-consistent reconstruction hypothesis",
        "route_b_used": False,
        "psi2_used_in_plus_or_cross": False,
        "radial_source_convention": next(iter(radial_source_conventions)),
        "no_interpolation": True,
        "no_smoothing": True,
        "principal_phase_stored": True,
        "unwrapped_phase_display_only": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    arrays["metadata_json"] = np.asarray(
        json.dumps(_json_safe(metadata), sort_keys=True)
    )
    _atomic_npz_no_overwrite(output, arrays)
    metadata["npz_sha256"] = _sha256(output)
    _atomic_json_no_overwrite(sidecar, metadata)
    return output


__all__ = [
    "DEFAULT_SOURCE_MERGE",
    "PaperInferredTableIError",
    "SCHEMA_VERSION",
    "load_uniform_source_contract",
    "merge_inferred_tablei_uniform",
    "produce_inferred_tablei_uniform",
]
