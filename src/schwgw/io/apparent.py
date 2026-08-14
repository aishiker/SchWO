"""Saved-grid workflow for diagnostic apparent polarizations (paper Fig. 7)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
import inspect
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import numpy as np

from schwgw.io.config import SolverConfig


ApparentSolver = Callable[..., Any]
ProgressCallback = Callable[[dict[str, Any]], None]


@dataclass(frozen=True)
class ApparentGridResult:
    """One x-z grid of incident-frame apparent polarization diagnostics."""

    x: np.ndarray
    z: np.ndarray
    r: np.ndarray
    theta: np.ndarray
    phi: np.ndarray
    valid_mask: np.ndarray
    h_x: np.ndarray
    h_y: np.ndarray
    h_b: np.ndarray
    h_longitudinal: np.ndarray
    metadata: dict[str, Any]

    def __post_init__(self) -> None:
        _validate_apparent_grid(self)


class _ApparentRunRadialCache:
    def __init__(self, raw_solver: Callable[..., Any]) -> None:
        self._raw_solver = raw_solver
        self._cache: dict[tuple[Any, ...], Any] = {}
        self.hit_count = 0
        self.unique_solution_count = 0

    def __call__(
        self,
        sector: Any,
        ell: int,
        k: float,
        background: Any,
        boundary_config: Any,
    ) -> Any:
        key = _radial_cache_key(sector, ell, k, background, boundary_config)
        if key in self._cache:
            self.hit_count += 1
            return self._cache[key]
        solution = self._raw_solver(sector, ell, k, background, boundary_config)
        self._cache[key] = solution
        self.unique_solution_count += 1
        return solution

    def metadata(self) -> dict[str, int | bool]:
        return {
            "enabled": True,
            "unique_solution_count": int(self.unique_solution_count),
            "hit_count": int(self.hit_count),
            "key_count": int(len(self._cache)),
        }

    def warning_metadata(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        seen: set[str] = set()
        for solution in self._cache.values():
            diagnostics = getattr(solution, "diagnostics", None)
            for warning in getattr(diagnostics, "warnings", ()) or ():
                payload = (
                    warning.to_metadata()
                    if hasattr(warning, "to_metadata")
                    else dict(warning)
                )
                safe = _json_safe(payload)
                marker = json.dumps(safe, sort_keys=True, separators=(",", ":"))
                if marker not in seen:
                    records.append(safe)
                    seen.add(marker)
        return records


def run_apparent_solver_grid(
    config: SolverConfig,
    *,
    apparent_solver: ApparentSolver | None = None,
    source_command: list[str] | None = None,
    progress: ProgressCallback | None = None,
) -> ApparentGridResult:
    """Compute a Fig. 7 x-z grid with one shared radial-mode cache."""

    from schwgw.backgrounds import SchwarzschildBackground
    from schwgw.numerics import BoundaryConfig, solve_radial_mode
    from schwgw.scattering.partial_wave import compute_apparent_polarizations

    if config.observer.kind != "xz_plane":
        raise ValueError("Fig. 7 apparent-mode production requires an xz_plane grid.")
    solver = (
        compute_apparent_polarizations
        if apparent_solver is None
        else apparent_solver
    )
    accepts_radial_solver = _accepts_keyword(solver, "radial_solver")
    background = SchwarzschildBackground(M=config.background.M)
    boundary = BoundaryConfig(
        r_in_eps=config.numerics.boundary.r_in_eps,
        r_out=config.numerics.boundary.r_out,
        rtol=config.numerics.boundary.rtol,
        atol=config.numerics.boundary.atol,
        required_eval_radius=config.numerics.boundary.required_eval_radius,
        conditioning_backend=config.numerics.boundary.conditioning_backend,
        experimental_required_radius_oracle=(
            config.numerics.boundary.experimental_required_radius_oracle
        ),
        outer_basis=config.numerics.boundary.outer_basis,
        outer_series_order=config.numerics.boundary.outer_series_order,
    )
    k = config.wave.kM / config.background.M
    radial_cache = _ApparentRunRadialCache(solve_radial_mode)

    x = np.asarray(config.observer.x_values, dtype=np.float64)
    z = np.asarray(config.observer.z_values, dtype=np.float64)
    xx, zz = np.meshgrid(x, z)
    radius = np.sqrt(xx * xx + zz * zz)
    valid_mask = np.isfinite(radius) & (radius > 2.0 * config.background.M)
    theta = np.full(radius.shape, np.nan, dtype=np.float64)
    phi = np.full(radius.shape, np.nan, dtype=np.float64)
    with np.errstate(invalid="ignore", divide="ignore"):
        cosine = np.clip(zz[valid_mask] / radius[valid_mask], -1.0, 1.0)
    theta[valid_mask] = np.arccos(cosine)
    phi[valid_mask] = np.where(xx[valid_mask] >= 0.0, 0.0, np.pi)

    empty = np.nan + 1j * np.nan
    fields = {
        name: np.full(radius.shape, empty, dtype=np.complex128)
        for name in ("h_x", "h_y", "h_b", "h_longitudinal")
    }
    diagnostic_maxima: dict[str, float] = {}
    points = np.argwhere(valid_mask)
    for point_number, (z_index, x_index) in enumerate(points, start=1):
        kwargs = {
            "background": background,
            "k": k,
            "r": float(radius[z_index, x_index]),
            "theta": float(theta[z_index, x_index]),
            "phi": float(phi[z_index, x_index]),
            "A_plus": config.wave.A_plus,
            "A_cross": config.wave.A_cross,
            "lmax": config.numerics.lmax,
            "boundary_config": boundary,
        }
        if accepts_radial_solver:
            kwargs["radial_solver"] = radial_cache
        result = solver(**kwargs)
        if getattr(result, "physical_claim", None) is not False:
            raise RuntimeError("Fig. 7 solver must return physical_claim=False.")
        fields["h_x"][z_index, x_index] = result.h_x
        fields["h_y"][z_index, x_index] = result.h_y
        fields["h_b"][z_index, x_index] = result.h_b
        fields["h_longitudinal"][z_index, x_index] = result.h_longitudinal
        if result.h_longitudinal != 2.0 * result.h_b:
            raise RuntimeError("Fig. 7 longitudinal/breathing identity drift.")
        for name, value in result.diagnostics.items():
            numeric = float(value)
            diagnostic_maxima[name] = max(
                diagnostic_maxima.get(name, -np.inf),
                numeric,
            )
        if progress is not None and (
            point_number == 1
            or point_number % 1000 == 0
            or point_number == len(points)
        ):
            progress(
                {
                    "event": "fig7_grid_progress",
                    "completed": point_number,
                    "total": len(points),
                    "kM": config.wave.kM,
                }
            )

    convergence = _apparent_convergence(
        config=config,
        solver=solver,
        accepts_radial_solver=accepts_radial_solver,
        radial_solver=radial_cache,
        background=background,
        boundary=boundary,
        k=k,
        observer_r=float(np.max(radius[valid_mask])),
    )
    bridge_metadata = getattr(solver, "__schwgw_bridge_metadata__", None)
    if bridge_metadata is None:
        bridge_metadata = {
            "tetrad": "incident-aligned strict Newman-Penrose",
            "direct_metric_curvature": False,
            "strict_np_lower_scalar_completion": False,
        }
    metadata = {
        "case_id": config.case_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "figure": 7,
        "schema_version": "li_hou_zhao_fig7_apparent_xz_v1",
        "physical_claim": False,
        "interpretation": (
            "incident-frame tetrad-dependent apparent polarizations; "
            "not additional propagating degrees of freedom"
        ),
        "convention": {
            "fourier": "exp(-i k t)",
            "metric_signature": "(-,+,+,+)",
            **dict(bridge_metadata),
            "units": "G=c=M=1",
        },
        "definitions": {
            "h_x": "-(Psi1+Psi3)/(2 k^2)",
            "h_y": "+i(Psi1-Psi3)/(2 k^2)",
            "h_b": "-Psi2/(2 k^2)",
            "h_longitudinal": "-Psi2/k^2 = 2 h_b",
        },
        "config": config.to_dict(),
        "grid": {
            "kind": "xz_plane",
            "shape": list(radius.shape),
            "valid_point_count": int(np.count_nonzero(valid_mask)),
            "invalid_point_count": int(valid_mask.size - np.count_nonzero(valid_mask)),
            "coordinate_conversion": (
                "r=sqrt(x^2+z^2), theta=arccos(z/r), "
                "phi=0 if x>=0 else pi"
            ),
        },
        "diagnostics": {
            "maxima": diagnostic_maxima,
            "run_radial_cache": radial_cache.metadata(),
            "radial_diagnostic_warnings": radial_cache.warning_metadata(),
            "convergence": convergence,
        },
        "source_command": source_command,
    }
    return ApparentGridResult(
        x=x,
        z=z,
        r=radius,
        theta=theta,
        phi=phi,
        valid_mask=valid_mask,
        h_x=fields["h_x"],
        h_y=fields["h_y"],
        h_b=fields["h_b"],
        h_longitudinal=fields["h_longitudinal"],
        metadata=metadata,
    )


def save_apparent_results(result: ApparentGridResult, path: str | Path) -> None:
    """Atomically save a Fig. 7 result as a no-pickle NPZ."""

    _validate_apparent_grid(result)
    output = Path(path)
    if output.suffix.lower() != ".npz":
        raise ValueError("Fig. 7 output path must end with .npz.")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing Fig. 7 artifact: {output}")
    payload = {
        "x": result.x,
        "z": result.z,
        "r": result.r,
        "theta": result.theta,
        "phi": result.phi,
        "valid_mask": result.valid_mask,
        "h_x": result.h_x,
        "h_y": result.h_y,
        "h_b": result.h_b,
        "h_longitudinal": result.h_longitudinal,
        "metadata_json": np.asarray(
            json.dumps(result.metadata, sort_keys=True, separators=(",", ":"))
        ),
    }
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w+b",
            prefix=f".{output.name}.",
            suffix=".partial",
            dir=output.parent,
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            np.savez(handle, **payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, output)
        directory_fd = os.open(output.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def load_apparent_results(path: str | Path) -> ApparentGridResult:
    """Load and validate a Fig. 7 no-pickle NPZ."""

    source = Path(path)
    required = {
        "x",
        "z",
        "r",
        "theta",
        "phi",
        "valid_mask",
        "h_x",
        "h_y",
        "h_b",
        "h_longitudinal",
        "metadata_json",
    }
    with np.load(source, allow_pickle=False) as data:
        missing = required - set(data.files)
        if missing:
            raise ValueError(f"Fig. 7 artifact missing fields: {sorted(missing)}")
        metadata = json.loads(str(data["metadata_json"]))
        result = ApparentGridResult(
            x=np.asarray(data["x"], dtype=np.float64),
            z=np.asarray(data["z"], dtype=np.float64),
            r=np.asarray(data["r"], dtype=np.float64),
            theta=np.asarray(data["theta"], dtype=np.float64),
            phi=np.asarray(data["phi"], dtype=np.float64),
            valid_mask=np.asarray(data["valid_mask"], dtype=bool),
            h_x=np.asarray(data["h_x"], dtype=np.complex128),
            h_y=np.asarray(data["h_y"], dtype=np.complex128),
            h_b=np.asarray(data["h_b"], dtype=np.complex128),
            h_longitudinal=np.asarray(data["h_longitudinal"], dtype=np.complex128),
            metadata=metadata,
        )
    return result


def _apparent_convergence(
    *,
    config: SolverConfig,
    solver: ApparentSolver,
    accepts_radial_solver: bool,
    radial_solver: Callable[..., Any],
    background: Any,
    boundary: Any,
    k: float,
    observer_r: float,
) -> dict[str, Any]:
    convergence = config.convergence
    if convergence is None or not convergence.enabled:
        return {"enabled": False}
    samples: dict[int, list[tuple[float, float, tuple[complex, ...]]]] = {}
    for lmax in convergence.lmax_values:
        rows = []
        for theta in convergence.theta_values:
            for phi in convergence.phi_values:
                kwargs = {
                    "background": background,
                    "k": k,
                    "r": observer_r,
                    "theta": theta,
                    "phi": phi,
                    "A_plus": config.wave.A_plus,
                    "A_cross": config.wave.A_cross,
                    "lmax": lmax,
                    "boundary_config": boundary,
                }
                if accepts_radial_solver:
                    kwargs["radial_solver"] = radial_solver
                result = solver(**kwargs)
                rows.append(
                    (
                        float(theta),
                        float(phi),
                        (
                            result.h_x,
                            result.h_y,
                            result.h_b,
                            result.h_longitudinal,
                        ),
                    )
                )
        samples[lmax] = rows
    history = []
    for previous_lmax, current_lmax in zip(
        convergence.lmax_values[:-1],
        convergence.lmax_values[1:],
        strict=True,
    ):
        changes = []
        near_axis_changes = []
        for previous, current in zip(
            samples[previous_lmax],
            samples[current_lmax],
            strict=True,
        ):
            for old, new in zip(previous[2], current[2], strict=True):
                change = abs(new - old) / max(abs(new), abs(old), 1.0e-30)
                changes.append(float(change))
                if abs(current[0]) <= 0.05:
                    near_axis_changes.append(float(change))
        history.append(
            {
                "previous_lmax": int(previous_lmax),
                "current_lmax": int(current_lmax),
                "max_relative_change": max(changes),
                "near_axis_max_relative_change": (
                    max(near_axis_changes) if near_axis_changes else max(changes)
                ),
            }
        )
    final = history[-1]
    return {
        "enabled": True,
        "history": history,
        "final_lmax_pair": [
            int(convergence.lmax_values[-2]),
            int(convergence.lmax_values[-1]),
        ],
        "selected_threshold": convergence.selected_threshold,
        "near_axis_threshold": convergence.near_axis_threshold,
        "final_pair_passed": bool(
            final["max_relative_change"] <= convergence.selected_threshold
            and final["near_axis_max_relative_change"]
            <= convergence.near_axis_threshold
        ),
    }


def _validate_apparent_grid(result: ApparentGridResult) -> None:
    if not isinstance(result, ApparentGridResult):
        raise TypeError("result must be an ApparentGridResult instance.")
    if result.x.ndim != 1 or result.z.ndim != 1:
        raise ValueError("x and z must be one-dimensional axes.")
    shape = (result.z.size, result.x.size)
    for name in (
        "r",
        "theta",
        "phi",
        "valid_mask",
        "h_x",
        "h_y",
        "h_b",
        "h_longitudinal",
    ):
        if np.asarray(getattr(result, name)).shape != shape:
            raise ValueError(f"{name} shape must match the x-z mesh.")
    valid = np.asarray(result.valid_mask, dtype=bool)
    for name in ("h_x", "h_y", "h_b", "h_longitudinal"):
        values = np.asarray(getattr(result, name), dtype=np.complex128)
        if not np.all(np.isfinite(values[valid].real)) or not np.all(
            np.isfinite(values[valid].imag)
        ):
            raise ValueError(f"{name} must be finite on valid grid points.")
        if not np.all(np.isnan(values[~valid].real)) or not np.all(
            np.isnan(values[~valid].imag)
        ):
            raise ValueError(f"{name} must be complex NaN on invalid grid points.")
    if not np.array_equal(
        np.asarray(result.h_longitudinal)[valid],
        2.0 * np.asarray(result.h_b)[valid],
    ):
        raise ValueError("h_longitudinal must equal 2*h_b exactly.")
    if result.metadata.get("physical_claim") is not False:
        raise ValueError("Fig. 7 metadata must keep physical_claim=false.")


def _accepts_keyword(callable_object: Callable[..., Any], keyword: str) -> bool:
    try:
        signature = inspect.signature(callable_object)
    except (TypeError, ValueError):
        return False
    return keyword in signature.parameters or any(
        parameter.kind is inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    )


def _radial_cache_key(
    sector: Any,
    ell: int,
    k: float,
    background: Any,
    boundary: Any,
) -> tuple[Any, ...]:
    boundary_key = tuple(
        getattr(boundary, name, None)
        for name in (
            "r_in_eps",
            "r_out",
            "rtol",
            "atol",
            "method",
            "max_step",
            "dense_output",
            "required_eval_radius",
            "experimental_required_radius_oracle",
        )
    )
    return (
        getattr(sector, "value", sector),
        int(ell),
        float(k),
        getattr(background, "name", type(background).__name__),
        float(getattr(background, "M", 0.0)),
        boundary_key,
    )


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    return value


__all__ = [
    "ApparentGridResult",
    "load_apparent_results",
    "run_apparent_solver_grid",
    "save_apparent_results",
]
