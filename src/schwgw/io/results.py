from __future__ import annotations

import json
import inspect
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import numpy as np

from schwgw.io.config import SolverConfig


PolarizationSolver = Callable[..., Any]
RELATIVE_CHANGE_FLOOR = 1.0e-30
NEAR_AXIS_THETA_MAX = 0.05


class ResultFormatError(ValueError):
    """Raised when a saved result file does not match the T8 output schema."""


@dataclass(frozen=True)
class GridResult:
    theta: np.ndarray
    phi: np.ndarray
    h_plus: np.ndarray
    h_cross: np.ndarray
    metadata: dict[str, Any]
    x: np.ndarray | None = None
    z: np.ndarray | None = None
    r: np.ndarray | None = None
    valid_mask: np.ndarray | None = None


@dataclass(frozen=True)
class AmplificationGridResult:
    theta: np.ndarray
    phi: np.ndarray
    F_plus_complex: np.ndarray
    F_cross_complex: np.ndarray
    amplification_plus: np.ndarray
    amplification_cross: np.ndarray
    intensity_plus_ratio: np.ndarray
    intensity_cross_ratio: np.ndarray
    F_pol_norm: np.ndarray
    I_pol_ratio: np.ndarray
    valid_ratio_plus_mask: np.ndarray
    valid_ratio_cross_mask: np.ndarray
    valid_ratio_norm_mask: np.ndarray
    metadata: dict[str, Any]
    x: np.ndarray | None = None
    z: np.ndarray | None = None
    r: np.ndarray | None = None
    valid_mask: np.ndarray | None = None


class _RunRadialCache:
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

    def metadata(self, *, enabled: bool) -> dict[str, Any]:
        return {
            "enabled": bool(enabled),
            "unique_solution_count": int(self.unique_solution_count if enabled else 0),
            "hit_count": int(self.hit_count if enabled else 0),
            "key_count": int(len(self._cache) if enabled else 0),
        }

    def warning_metadata(self) -> list[dict[str, Any]]:
        warnings = []
        seen = set()
        for solution in self._cache.values():
            diagnostics = getattr(solution, "diagnostics", None)
            for warning in getattr(diagnostics, "warnings", ()) or ():
                if hasattr(warning, "to_metadata"):
                    payload = warning.to_metadata()
                else:
                    payload = dict(warning)
                safe_payload = _json_safe_metadata(payload)
                marker = json.dumps(safe_payload, sort_keys=True)
                if marker not in seen:
                    warnings.append(safe_payload)
                    seen.add(marker)
        return warnings


def run_solver_grid(
    config: SolverConfig,
    *,
    polarization_solver: PolarizationSolver | None = None,
    source_command: list[str] | None = None,
) -> GridResult:
    """Run the production polarization solver on a configured observer grid."""

    from schwgw.backgrounds import SchwarzschildBackground
    from schwgw.numerics import BoundaryConfig, solve_radial_mode
    from schwgw.scattering.partial_wave import compute_polarization

    solver = compute_polarization if polarization_solver is None else polarization_solver
    solver_accepts_radial_solver = _accepts_keyword(solver, "radial_solver")
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
    radial_cache = _RunRadialCache(solve_radial_mode)

    if config.observer.kind == "xz_plane":
        grid = _run_xz_plane_grid(
            config=config,
            solver=solver,
            solver_accepts_radial_solver=solver_accepts_radial_solver,
            radial_solver=radial_cache,
            background=background,
            boundary=boundary,
            k=k,
        )
    else:
        grid = _run_angular_grid(
            config=config,
            solver=solver,
            solver_accepts_radial_solver=solver_accepts_radial_solver,
            radial_solver=radial_cache,
            background=background,
            boundary=boundary,
            k=k,
        )

    diagnostic_metadata: dict[str, Any] = {
        "points": grid["diagnostics"],
        "summary": _summarize_diagnostics(grid["diagnostics"]),
        "valid_point_count": grid["valid_point_count"],
        "invalid_point_count": grid["invalid_point_count"],
        "skipped_point_count": grid["invalid_point_count"],
    }
    if config.convergence is not None and config.convergence.enabled:
        diagnostic_metadata.update(
            _build_lmax_convergence_diagnostics(
                config=config,
                solver=solver,
                solver_accepts_radial_solver=solver_accepts_radial_solver,
                radial_solver=radial_cache,
                background=background,
                boundary=boundary,
                k=k,
                observer_r=grid["convergence_r"],
            )
        )
    diagnostic_metadata["run_radial_cache"] = radial_cache.metadata(
        enabled=solver_accepts_radial_solver,
    )
    diagnostic_metadata["radial_diagnostic_warnings"] = (
        radial_cache.warning_metadata() if solver_accepts_radial_solver else []
    )

    bridge_metadata = getattr(solver, "__schwgw_bridge_metadata__", None)
    if bridge_metadata is None:
        from schwgw.validation import unspecified_polarization_solver_metadata

        bridge_metadata = unspecified_polarization_solver_metadata()
    metadata = {
        "case_id": config.case_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "convention": {
            "fourier": "exp(-i k t)",
            "units": "G=c=M=1",
            "gauge": "Regge-Wheeler",
            "field_content": "total_incident_plus_reflected",
            "field_content_basis": (
                "radial modes normalized by A_in to incident partial-wave coefficients"
            ),
            **dict(bridge_metadata),
        },
        "config": config.to_dict(),
        "grid": grid["metadata"],
        "lmax": config.numerics.lmax,
        "boundary": config.to_dict()["numerics"]["boundary"],
        "diagnostics": diagnostic_metadata,
        "source_command": source_command,
    }
    return GridResult(
        theta=grid["theta"],
        phi=grid["phi"],
        h_plus=grid["h_plus"],
        h_cross=grid["h_cross"],
        metadata=metadata,
        x=grid.get("x"),
        z=grid.get("z"),
        r=grid.get("r"),
        valid_mask=grid.get("valid_mask"),
    )


def _run_angular_grid(
    *,
    config: SolverConfig,
    solver: PolarizationSolver,
    solver_accepts_radial_solver: bool,
    radial_solver: Callable[..., Any],
    background: Any,
    boundary: Any,
    k: float,
) -> dict[str, Any]:
    if config.observer.r is None:
        raise ValueError("Angular observer grid requires observer.r.")
    theta = np.asarray(config.observer.theta_values, dtype=float)
    phi = np.asarray(config.observer.phi_values, dtype=float)
    h_plus = np.empty((theta.size, phi.size), dtype=np.complex128)
    h_cross = np.empty((theta.size, phi.size), dtype=np.complex128)
    diagnostics: list[dict[str, float]] = []

    for theta_index, theta_value in enumerate(theta):
        for phi_index, phi_value in enumerate(phi):
            result = _call_polarization_solver(
                solver,
                accepts_radial_solver=solver_accepts_radial_solver,
                radial_solver=radial_solver,
                background=background,
                k=k,
                r=config.observer.r,
                theta=float(theta_value),
                phi=float(phi_value),
                A_plus=config.wave.A_plus,
                A_cross=config.wave.A_cross,
                lmax=config.numerics.lmax,
                boundary_config=boundary,
            )
            h_plus[theta_index, phi_index] = result.h_plus
            h_cross[theta_index, phi_index] = result.h_cross
            diagnostics.append(dict(result.diagnostics))

    point_count = int(theta.size * phi.size)
    return {
        "theta": theta,
        "phi": phi,
        "h_plus": h_plus,
        "h_cross": h_cross,
        "diagnostics": diagnostics,
        "valid_point_count": point_count,
        "invalid_point_count": 0,
        "convergence_r": float(config.observer.r),
        "metadata": {
            "kind": "angular",
            "r": float(config.observer.r),
            "theta_values": theta.tolist(),
            "phi_values": phi.tolist(),
            "valid_point_count": point_count,
            "invalid_point_count": 0,
        },
    }


def _run_xz_plane_grid(
    *,
    config: SolverConfig,
    solver: PolarizationSolver,
    solver_accepts_radial_solver: bool,
    radial_solver: Callable[..., Any],
    background: Any,
    boundary: Any,
    k: float,
) -> dict[str, Any]:
    x = np.asarray(config.observer.x_values, dtype=float)
    z = np.asarray(config.observer.z_values, dtype=float)
    xx, zz = np.meshgrid(x, z)
    radius = np.sqrt(xx * xx + zz * zz)
    horizon_radius = 2.0 * config.background.M
    valid_mask = np.isfinite(radius) & (radius > horizon_radius)

    theta = np.full(radius.shape, np.nan, dtype=float)
    phi = np.full(radius.shape, np.nan, dtype=float)
    if np.any(valid_mask):
        with np.errstate(invalid="ignore", divide="ignore"):
            cosine = np.clip(zz[valid_mask] / radius[valid_mask], -1.0, 1.0)
        theta[valid_mask] = np.arccos(cosine)
        phi[valid_mask] = np.where(xx[valid_mask] >= 0.0, 0.0, np.pi)

    h_plus = np.full(radius.shape, np.nan + 1j * np.nan, dtype=np.complex128)
    h_cross = np.full(radius.shape, np.nan + 1j * np.nan, dtype=np.complex128)
    diagnostics: list[dict[str, float]] = []

    for z_index, x_index in np.argwhere(valid_mask):
        result = _call_polarization_solver(
            solver,
            accepts_radial_solver=solver_accepts_radial_solver,
            radial_solver=radial_solver,
            background=background,
            k=k,
            r=float(radius[z_index, x_index]),
            theta=float(theta[z_index, x_index]),
            phi=float(phi[z_index, x_index]),
            A_plus=config.wave.A_plus,
            A_cross=config.wave.A_cross,
            lmax=config.numerics.lmax,
            boundary_config=boundary,
        )
        h_plus[z_index, x_index] = result.h_plus
        h_cross[z_index, x_index] = result.h_cross
        diagnostics.append(dict(result.diagnostics))

    valid_count = int(np.count_nonzero(valid_mask))
    invalid_count = int(valid_mask.size - valid_count)
    return {
        "x": x,
        "z": z,
        "r": radius,
        "theta": theta,
        "phi": phi,
        "valid_mask": valid_mask,
        "h_plus": h_plus,
        "h_cross": h_cross,
        "diagnostics": diagnostics,
        "valid_point_count": valid_count,
        "invalid_point_count": invalid_count,
        "convergence_r": float(np.nanmax(radius[valid_mask])),
        "metadata": {
            "kind": "xz_plane",
            "x_values": x.tolist(),
            "z_values": z.tolist(),
            "valid_point_count": valid_count,
            "invalid_point_count": invalid_count,
            "coordinate_conversion": (
                "r=sqrt(x^2+z^2), theta=arccos(z/r), phi=0 if x>=0 else pi"
            ),
        },
    }


def _build_lmax_convergence_diagnostics(
    *,
    config: SolverConfig,
    solver: PolarizationSolver,
    solver_accepts_radial_solver: bool,
    radial_solver: Callable[..., Any],
    background: Any,
    boundary: Any,
    k: float,
    observer_r: float,
) -> dict[str, Any]:
    convergence = config.convergence
    if convergence is None:
        return {}

    probes = [
        (float(theta), float(phi))
        for theta in convergence.theta_values
        for phi in convergence.phi_values
    ]
    samples: dict[int, list[dict[str, Any]]] = {}
    for lmax in convergence.lmax_values:
        lmax_samples = []
        for theta_value, phi_value in probes:
            result = _call_polarization_solver(
                solver,
                accepts_radial_solver=solver_accepts_radial_solver,
                radial_solver=radial_solver,
                background=background,
                k=k,
                r=observer_r,
                theta=theta_value,
                phi=phi_value,
                A_plus=config.wave.A_plus,
                A_cross=config.wave.A_cross,
                lmax=lmax,
                boundary_config=boundary,
            )
            lmax_samples.append(
                {
                    "theta": theta_value,
                    "phi": phi_value,
                    "h_plus": complex(result.h_plus),
                    "h_cross": complex(result.h_cross),
                }
            )
        samples[lmax] = lmax_samples

    history = []
    for previous_lmax, current_lmax in zip(
        convergence.lmax_values[:-1],
        convergence.lmax_values[1:],
        strict=True,
    ):
        previous_samples = samples[previous_lmax]
        current_samples = samples[current_lmax]
        row = _compare_lmax_samples(
            previous_lmax=previous_lmax,
            current_lmax=current_lmax,
            previous_samples=previous_samples,
            current_samples=current_samples,
        )
        history.append(row)

    final_pair = [
        int(convergence.lmax_values[-2]),
        int(convergence.lmax_values[-1]),
    ]
    final_row = history[-1]
    final_pair_passed = (
        final_row["max_relative_change"] <= convergence.selected_threshold
        and final_row["near_axis_max_relative_change"] <= convergence.near_axis_threshold
    )
    return {
        "lmax_convergence_history": history,
        "lmax_convergence_policy": {
            "enabled": True,
            "lmax_values": list(convergence.lmax_values),
            "theta_values": list(convergence.theta_values),
            "phi_values": list(convergence.phi_values),
            "selected_threshold": convergence.selected_threshold,
            "near_axis_threshold": convergence.near_axis_threshold,
            "near_axis_theta_max": NEAR_AXIS_THETA_MAX,
            "observer_r": float(observer_r),
            "relative_change_denominator": (
                f"max(abs(new), abs(old), {RELATIVE_CHANGE_FLOOR:g})"
            ),
            "final_pair_passed": bool(final_pair_passed),
        },
        "final_lmax_pair": final_pair,
    }


def _call_polarization_solver(
    solver: PolarizationSolver,
    *,
    accepts_radial_solver: bool,
    radial_solver: Callable[..., Any],
    **kwargs: Any,
) -> Any:
    if accepts_radial_solver:
        kwargs["radial_solver"] = radial_solver
    return solver(**kwargs)


def _accepts_keyword(callable_object: Callable[..., Any], keyword: str) -> bool:
    try:
        signature = inspect.signature(callable_object)
    except (TypeError, ValueError):
        return False
    for parameter in signature.parameters.values():
        if parameter.kind is inspect.Parameter.VAR_KEYWORD:
            return True
        if parameter.name == keyword and parameter.kind in {
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        }:
            return True
    return False


def _radial_cache_key(
    sector: Any,
    ell: int,
    k: float,
    background: Any,
    boundary_config: Any,
) -> tuple[Any, ...]:
    boundary_key = None
    if boundary_config is not None:
        boundary_key = (
            getattr(boundary_config, "r_in_eps", None),
            getattr(boundary_config, "r_out", None),
            getattr(boundary_config, "rtol", None),
            getattr(boundary_config, "atol", None),
            getattr(boundary_config, "method", None),
            getattr(boundary_config, "max_step", None),
            getattr(boundary_config, "dense_output", None),
            getattr(boundary_config, "required_eval_radius", None),
            getattr(boundary_config, "experimental_required_radius_oracle", None),
        )
    return (
        getattr(sector, "value", sector),
        int(ell),
        float(k),
        getattr(background, "name", type(background).__name__),
        float(getattr(background, "M", 0.0)),
        boundary_key,
    )


def _json_safe_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe_metadata(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe_metadata(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"real": float(value.real), "imag": float(value.imag)}
    return value


def _compare_lmax_samples(
    *,
    previous_lmax: int,
    current_lmax: int,
    previous_samples: list[dict[str, Any]],
    current_samples: list[dict[str, Any]],
) -> dict[str, Any]:
    max_change = -1.0
    near_axis_max_change = -1.0
    worst_probe: dict[str, Any] | None = None
    near_axis_probe_count = 0

    for previous, current in zip(previous_samples, current_samples, strict=True):
        theta = float(current["theta"])
        phi = float(current["phi"])
        is_near_axis = abs(theta) <= NEAR_AXIS_THETA_MAX
        if is_near_axis:
            near_axis_probe_count += 1
        for component in ("h_plus", "h_cross"):
            change = _relative_complex_change(current[component], previous[component])
            if change > max_change:
                max_change = change
                worst_probe = {
                    "theta": theta,
                    "phi": phi,
                    "component": component,
                }
            if is_near_axis and change > near_axis_max_change:
                near_axis_max_change = change

    if near_axis_probe_count == 0:
        near_axis_probe_count = len(current_samples)
        near_axis_max_change = max_change
    row = {
        "previous_lmax": int(previous_lmax),
        "current_lmax": int(current_lmax),
        "max_relative_change": float(max_change),
        "near_axis_max_relative_change": float(near_axis_max_change),
        "probe_count": len(current_samples),
        "near_axis_probe_count": near_axis_probe_count,
    }
    if worst_probe is not None:
        row["worst_probe"] = worst_probe
    return row


def _relative_complex_change(new: complex, old: complex) -> float:
    denominator = max(abs(new), abs(old), RELATIVE_CHANGE_FLOOR)
    return float(abs(new - old) / denominator)


def save_results(result: GridResult, path: str | Path) -> None:
    """Save a grid result as NPZ or HDF5 based on file suffix."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = output_path.suffix.lower()
    if suffix == ".npz":
        _save_npz(result, output_path)
        return
    if suffix in {".h5", ".hdf5"}:
        _save_hdf5(result, output_path)
        return
    raise ValueError("Output path must end with .npz, .h5, or .hdf5.")


def save_amplification_results(result: AmplificationGridResult, path: str | Path) -> None:
    """Save an M5 pointwise amplification result as NPZ or HDF5."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = output_path.suffix.lower()
    if suffix == ".npz":
        _save_amplification_npz(result, output_path)
        return
    if suffix in {".h5", ".hdf5"}:
        _save_amplification_hdf5(result, output_path)
        return
    raise ValueError("Output path must end with .npz, .h5, or .hdf5.")


def load_results(path: str | Path) -> GridResult:
    """Load a T8 result file, preserving complex field arrays."""

    result_path = Path(path)
    suffix = result_path.suffix.lower()
    if suffix == ".npz":
        return _load_npz(result_path)
    if suffix in {".h5", ".hdf5"}:
        return _load_hdf5(result_path)
    raise ResultFormatError("Unsupported result suffix; expected .npz, .h5, or .hdf5.")


def load_amplification_results(path: str | Path) -> AmplificationGridResult:
    """Load an M5 pointwise amplification result file."""

    result_path = Path(path)
    suffix = result_path.suffix.lower()
    if suffix == ".npz":
        return _load_amplification_npz(result_path)
    if suffix in {".h5", ".hdf5"}:
        return _load_amplification_hdf5(result_path)
    raise ResultFormatError("Unsupported result suffix; expected .npz, .h5, or .hdf5.")


def _save_npz(result: GridResult, path: Path) -> None:
    payload = {
        "theta": result.theta,
        "phi": result.phi,
        "h_plus": result.h_plus,
        "h_cross": result.h_cross,
        "metadata_json": np.asarray(_metadata_json(result.metadata)),
    }
    if _is_xz_result(result):
        payload.update(
            {
                "x": result.x,
                "z": result.z,
                "r": result.r,
                "valid_mask": result.valid_mask,
            }
        )
    np.savez(path, **payload)


def _save_hdf5(result: GridResult, path: Path) -> None:
    try:
        import h5py
    except ImportError as exc:
        raise RuntimeError("HDF5 output requires h5py to be installed.") from exc

    with h5py.File(path, "w") as handle:
        fields = handle.create_group("fields")
        fields.create_dataset("theta", data=result.theta)
        fields.create_dataset("phi", data=result.phi)
        fields.create_dataset("h_plus", data=result.h_plus)
        fields.create_dataset("h_cross", data=result.h_cross)
        if _is_xz_result(result):
            fields.create_dataset("x", data=result.x)
            fields.create_dataset("z", data=result.z)
            fields.create_dataset("r", data=result.r)
            fields.create_dataset("valid_mask", data=result.valid_mask)
        handle.attrs["metadata_json"] = _metadata_json(result.metadata)


def _amplification_payload(result: AmplificationGridResult) -> dict[str, Any]:
    payload = {
        "theta": result.theta,
        "phi": result.phi,
        "F_plus_complex": result.F_plus_complex,
        "F_cross_complex": result.F_cross_complex,
        "amplification_plus": result.amplification_plus,
        "amplification_cross": result.amplification_cross,
        "intensity_plus_ratio": result.intensity_plus_ratio,
        "intensity_cross_ratio": result.intensity_cross_ratio,
        "F_pol_norm": result.F_pol_norm,
        "I_pol_ratio": result.I_pol_ratio,
        "valid_ratio_plus_mask": result.valid_ratio_plus_mask,
        "valid_ratio_cross_mask": result.valid_ratio_cross_mask,
        "valid_ratio_norm_mask": result.valid_ratio_norm_mask,
        "metadata_json": np.asarray(_metadata_json(result.metadata)),
    }
    if _is_xz_amplification_result(result):
        payload.update(
            {
                "x": result.x,
                "z": result.z,
                "r": result.r,
                "valid_mask": result.valid_mask,
            }
        )
    return payload


def _save_amplification_npz(result: AmplificationGridResult, path: Path) -> None:
    np.savez(path, **_amplification_payload(result))


def _save_amplification_hdf5(result: AmplificationGridResult, path: Path) -> None:
    try:
        import h5py
    except ImportError as exc:
        raise RuntimeError("HDF5 output requires h5py to be installed.") from exc

    payload = _amplification_payload(result)
    metadata_json = payload.pop("metadata_json")
    with h5py.File(path, "w") as handle:
        fields = handle.create_group("fields")
        for name, value in payload.items():
            fields.create_dataset(name, data=value)
        handle.attrs["metadata_json"] = str(metadata_json)


def _load_npz(path: Path) -> GridResult:
    required = {"theta", "phi", "h_plus", "h_cross", "metadata_json"}
    try:
        with np.load(path, allow_pickle=False) as data:
            missing = required - set(data.files)
            if missing:
                raise ResultFormatError(
                    f"NPZ result missing required field(s): {', '.join(sorted(missing))}."
                )
            theta = np.asarray(data["theta"], dtype=float)
            phi = np.asarray(data["phi"], dtype=float)
            h_plus = np.asarray(data["h_plus"])
            h_cross = np.asarray(data["h_cross"])
            metadata = _parse_metadata_json(str(data["metadata_json"]))
            x = np.asarray(data["x"], dtype=float) if "x" in data.files else None
            z = np.asarray(data["z"], dtype=float) if "z" in data.files else None
            radius = np.asarray(data["r"], dtype=float) if "r" in data.files else None
            valid_mask = (
                np.asarray(data["valid_mask"], dtype=bool)
                if "valid_mask" in data.files
                else None
            )
    except ResultFormatError:
        raise
    except OSError as exc:
        raise ResultFormatError(f"Could not read NPZ result {path}: {exc}") from exc
    return _validated_grid_result(
        theta,
        phi,
        h_plus,
        h_cross,
        metadata,
        x=x,
        z=z,
        r=radius,
        valid_mask=valid_mask,
    )


def _load_amplification_npz(path: Path) -> AmplificationGridResult:
    required = _required_amplification_fields() | {"metadata_json"}
    try:
        with np.load(path, allow_pickle=False) as data:
            missing = required - set(data.files)
            if missing:
                raise ResultFormatError(
                    f"NPZ amplification result missing required field(s): {', '.join(sorted(missing))}."
                )
            arrays = {name: np.asarray(data[name]) for name in required - {"metadata_json"}}
            metadata = _parse_metadata_json(str(data["metadata_json"]))
            x = np.asarray(data["x"], dtype=float) if "x" in data.files else None
            z = np.asarray(data["z"], dtype=float) if "z" in data.files else None
            radius = np.asarray(data["r"], dtype=float) if "r" in data.files else None
            valid_mask = (
                np.asarray(data["valid_mask"], dtype=bool)
                if "valid_mask" in data.files
                else None
            )
    except ResultFormatError:
        raise
    except OSError as exc:
        raise ResultFormatError(
            f"Could not read NPZ amplification result {path}: {exc}"
        ) from exc
    return _validated_amplification_result(
        metadata=metadata,
        x=x,
        z=z,
        r=radius,
        valid_mask=valid_mask,
        **arrays,
    )


def _load_hdf5(path: Path) -> GridResult:
    try:
        import h5py
    except ImportError as exc:
        raise RuntimeError("HDF5 input requires h5py to be installed.") from exc

    try:
        with h5py.File(path, "r") as handle:
            if "fields" not in handle:
                raise ResultFormatError("HDF5 result missing required group: fields.")
            fields = handle["fields"]
            required = {"theta", "phi", "h_plus", "h_cross"}
            missing = required - set(fields.keys())
            if missing:
                raise ResultFormatError(
                    f"HDF5 result missing required field(s): {', '.join(sorted(missing))}."
                )
            if "metadata_json" not in handle.attrs:
                raise ResultFormatError("HDF5 result missing required metadata_json attribute.")
            theta = np.asarray(fields["theta"], dtype=float)
            phi = np.asarray(fields["phi"], dtype=float)
            h_plus = np.asarray(fields["h_plus"])
            h_cross = np.asarray(fields["h_cross"])
            metadata = _parse_metadata_json(str(handle.attrs["metadata_json"]))
            x = np.asarray(fields["x"], dtype=float) if "x" in fields else None
            z = np.asarray(fields["z"], dtype=float) if "z" in fields else None
            radius = np.asarray(fields["r"], dtype=float) if "r" in fields else None
            valid_mask = (
                np.asarray(fields["valid_mask"], dtype=bool)
                if "valid_mask" in fields
                else None
            )
    except ResultFormatError:
        raise
    except OSError as exc:
        raise ResultFormatError(f"Could not read HDF5 result {path}: {exc}") from exc
    return _validated_grid_result(
        theta,
        phi,
        h_plus,
        h_cross,
        metadata,
        x=x,
        z=z,
        r=radius,
        valid_mask=valid_mask,
    )


def _load_amplification_hdf5(path: Path) -> AmplificationGridResult:
    try:
        import h5py
    except ImportError as exc:
        raise RuntimeError("HDF5 input requires h5py to be installed.") from exc

    try:
        with h5py.File(path, "r") as handle:
            if "fields" not in handle:
                raise ResultFormatError("HDF5 amplification result missing required group: fields.")
            fields = handle["fields"]
            required = _required_amplification_fields()
            missing = required - set(fields.keys())
            if missing:
                raise ResultFormatError(
                    f"HDF5 amplification result missing required field(s): {', '.join(sorted(missing))}."
                )
            if "metadata_json" not in handle.attrs:
                raise ResultFormatError("HDF5 amplification result missing required metadata_json attribute.")
            arrays = {name: np.asarray(fields[name]) for name in required}
            metadata = _parse_metadata_json(str(handle.attrs["metadata_json"]))
            x = np.asarray(fields["x"], dtype=float) if "x" in fields else None
            z = np.asarray(fields["z"], dtype=float) if "z" in fields else None
            radius = np.asarray(fields["r"], dtype=float) if "r" in fields else None
            valid_mask = (
                np.asarray(fields["valid_mask"], dtype=bool)
                if "valid_mask" in fields
                else None
            )
    except ResultFormatError:
        raise
    except OSError as exc:
        raise ResultFormatError(
            f"Could not read HDF5 amplification result {path}: {exc}"
        ) from exc
    return _validated_amplification_result(
        metadata=metadata,
        x=x,
        z=z,
        r=radius,
        valid_mask=valid_mask,
        **arrays,
    )


def _metadata_json(metadata: dict[str, Any]) -> str:
    return json.dumps(metadata, sort_keys=True, separators=(",", ":"))


def _parse_metadata_json(value: str) -> dict[str, Any]:
    try:
        metadata = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ResultFormatError(f"metadata_json is not valid JSON: {exc}") from exc
    if not isinstance(metadata, dict):
        raise ResultFormatError("metadata_json must decode to a JSON object.")
    return metadata


def _validated_grid_result(
    theta: np.ndarray,
    phi: np.ndarray,
    h_plus: np.ndarray,
    h_cross: np.ndarray,
    metadata: dict[str, Any],
    *,
    x: np.ndarray | None = None,
    z: np.ndarray | None = None,
    r: np.ndarray | None = None,
    valid_mask: np.ndarray | None = None,
) -> GridResult:
    grid_metadata = metadata.get("grid", {})
    grid_kind = grid_metadata.get("kind") if isinstance(grid_metadata, dict) else None
    has_xz_fields = any(item is not None for item in (x, z, r, valid_mask))
    if grid_kind == "xz_plane" or has_xz_fields:
        return _validated_xz_grid_result(
            theta,
            phi,
            h_plus,
            h_cross,
            metadata,
            x=x,
            z=z,
            r=r,
            valid_mask=valid_mask,
        )

    if theta.ndim != 1 or theta.size == 0:
        raise ResultFormatError("theta must be a non-empty 1D array.")
    if phi.ndim != 1 or phi.size == 0:
        raise ResultFormatError("phi must be a non-empty 1D array.")
    expected_shape = (theta.size, phi.size)
    if h_plus.shape != expected_shape:
        raise ResultFormatError(
            f"h_plus must have shape {expected_shape}, got {h_plus.shape}."
        )
    if h_cross.shape != expected_shape:
        raise ResultFormatError(
            f"h_cross must have shape {expected_shape}, got {h_cross.shape}."
        )
    if not np.issubdtype(h_plus.dtype, np.complexfloating):
        h_plus = h_plus.astype(np.complex128)
    if not np.issubdtype(h_cross.dtype, np.complexfloating):
        h_cross = h_cross.astype(np.complex128)
    return GridResult(
        theta=theta,
        phi=phi,
        h_plus=np.asarray(h_plus, dtype=np.complex128),
        h_cross=np.asarray(h_cross, dtype=np.complex128),
        metadata=metadata,
    )


def _validated_amplification_result(
    *,
    theta: np.ndarray,
    phi: np.ndarray,
    F_plus_complex: np.ndarray,
    F_cross_complex: np.ndarray,
    amplification_plus: np.ndarray,
    amplification_cross: np.ndarray,
    intensity_plus_ratio: np.ndarray,
    intensity_cross_ratio: np.ndarray,
    F_pol_norm: np.ndarray,
    I_pol_ratio: np.ndarray,
    valid_ratio_plus_mask: np.ndarray,
    valid_ratio_cross_mask: np.ndarray,
    valid_ratio_norm_mask: np.ndarray,
    metadata: dict[str, Any],
    x: np.ndarray | None = None,
    z: np.ndarray | None = None,
    r: np.ndarray | None = None,
    valid_mask: np.ndarray | None = None,
) -> AmplificationGridResult:
    theta = np.asarray(theta, dtype=float)
    phi = np.asarray(phi, dtype=float)
    f_plus = np.asarray(F_plus_complex, dtype=np.complex128)
    f_cross = np.asarray(F_cross_complex, dtype=np.complex128)
    shape = f_plus.shape
    if shape == ():
        raise ResultFormatError("F_plus_complex must be an array.")
    arrays = {
        "F_cross_complex": np.asarray(f_cross),
        "amplification_plus": np.asarray(amplification_plus, dtype=float),
        "amplification_cross": np.asarray(amplification_cross, dtype=float),
        "intensity_plus_ratio": np.asarray(intensity_plus_ratio, dtype=float),
        "intensity_cross_ratio": np.asarray(intensity_cross_ratio, dtype=float),
        "F_pol_norm": np.asarray(F_pol_norm, dtype=float),
        "I_pol_ratio": np.asarray(I_pol_ratio, dtype=float),
        "valid_ratio_plus_mask": np.asarray(valid_ratio_plus_mask, dtype=bool),
        "valid_ratio_cross_mask": np.asarray(valid_ratio_cross_mask, dtype=bool),
        "valid_ratio_norm_mask": np.asarray(valid_ratio_norm_mask, dtype=bool),
    }
    for name, array in arrays.items():
        if array.shape != shape:
            raise ResultFormatError(f"{name} must have shape {shape}, got {array.shape}.")

    grid_metadata = metadata.get("grid", {})
    grid_kind = grid_metadata.get("kind") if isinstance(grid_metadata, dict) else None
    has_xz_fields = any(item is not None for item in (x, z, r, valid_mask))
    if grid_kind == "xz_plane" or has_xz_fields:
        if x is None or z is None or r is None or valid_mask is None:
            raise ResultFormatError(
                "x-z amplification result requires x, z, r, and valid_mask fields."
            )
        x = np.asarray(x, dtype=float)
        z = np.asarray(z, dtype=float)
        r = np.asarray(r, dtype=float)
        valid_mask = np.asarray(valid_mask, dtype=bool)
        if x.ndim != 1 or x.size == 0:
            raise ResultFormatError("x must be a non-empty 1D array.")
        if z.ndim != 1 or z.size == 0:
            raise ResultFormatError("z must be a non-empty 1D array.")
        expected_shape = (z.size, x.size)
        for name, array in {
            "r": r,
            "theta": theta,
            "phi": phi,
            "valid_mask": valid_mask,
            "F_plus_complex": f_plus,
        }.items():
            if array.shape != expected_shape:
                raise ResultFormatError(
                    f"{name} must have shape {expected_shape}, got {array.shape}."
                )
    else:
        if theta.ndim != 1 or phi.ndim != 1:
            raise ResultFormatError("angular amplification theta and phi must be 1D arrays.")
        expected_shape = (theta.size, phi.size)
        if shape != expected_shape:
            raise ResultFormatError(
                f"amplification fields must have shape {expected_shape}, got {shape}."
            )

    return AmplificationGridResult(
        theta=theta,
        phi=phi,
        F_plus_complex=f_plus,
        F_cross_complex=f_cross,
        amplification_plus=arrays["amplification_plus"],
        amplification_cross=arrays["amplification_cross"],
        intensity_plus_ratio=arrays["intensity_plus_ratio"],
        intensity_cross_ratio=arrays["intensity_cross_ratio"],
        F_pol_norm=arrays["F_pol_norm"],
        I_pol_ratio=arrays["I_pol_ratio"],
        valid_ratio_plus_mask=arrays["valid_ratio_plus_mask"],
        valid_ratio_cross_mask=arrays["valid_ratio_cross_mask"],
        valid_ratio_norm_mask=arrays["valid_ratio_norm_mask"],
        metadata=metadata,
        x=x,
        z=z,
        r=r,
        valid_mask=valid_mask,
    )


def _validated_xz_grid_result(
    theta: np.ndarray,
    phi: np.ndarray,
    h_plus: np.ndarray,
    h_cross: np.ndarray,
    metadata: dict[str, Any],
    *,
    x: np.ndarray | None,
    z: np.ndarray | None,
    r: np.ndarray | None,
    valid_mask: np.ndarray | None,
) -> GridResult:
    if x is None or z is None or r is None or valid_mask is None:
        raise ResultFormatError("x-z result requires x, z, r, and valid_mask fields.")
    if x.ndim != 1 or x.size == 0:
        raise ResultFormatError("x must be a non-empty 1D array.")
    if z.ndim != 1 or z.size == 0:
        raise ResultFormatError("z must be a non-empty 1D array.")
    expected_shape = (z.size, x.size)
    for name, array in {
        "r": r,
        "theta": theta,
        "phi": phi,
        "valid_mask": valid_mask,
        "h_plus": h_plus,
        "h_cross": h_cross,
    }.items():
        if array.shape != expected_shape:
            raise ResultFormatError(
                f"{name} must have shape {expected_shape}, got {array.shape}."
            )
    if not np.issubdtype(h_plus.dtype, np.complexfloating):
        h_plus = h_plus.astype(np.complex128)
    if not np.issubdtype(h_cross.dtype, np.complexfloating):
        h_cross = h_cross.astype(np.complex128)
    return GridResult(
        theta=theta,
        phi=phi,
        h_plus=np.asarray(h_plus, dtype=np.complex128),
        h_cross=np.asarray(h_cross, dtype=np.complex128),
        metadata=metadata,
        x=x,
        z=z,
        r=r,
        valid_mask=np.asarray(valid_mask, dtype=bool),
    )


def _is_xz_result(result: GridResult) -> bool:
    grid = result.metadata.get("grid", {})
    if isinstance(grid, dict) and grid.get("kind") == "xz_plane":
        return True
    return any(
        item is not None for item in (result.x, result.z, result.r, result.valid_mask)
    )


def _is_xz_amplification_result(result: AmplificationGridResult) -> bool:
    grid = result.metadata.get("grid", {})
    if isinstance(grid, dict) and grid.get("kind") == "xz_plane":
        return True
    return any(
        item is not None for item in (result.x, result.z, result.r, result.valid_mask)
    )


def _required_amplification_fields() -> set[str]:
    return {
        "theta",
        "phi",
        "F_plus_complex",
        "F_cross_complex",
        "amplification_plus",
        "amplification_cross",
        "intensity_plus_ratio",
        "intensity_cross_ratio",
        "F_pol_norm",
        "I_pol_ratio",
        "valid_ratio_plus_mask",
        "valid_ratio_cross_mask",
        "valid_ratio_norm_mask",
    }


def _summarize_diagnostics(diagnostics: list[dict[str, float]]) -> dict[str, float]:
    keys = sorted({key for item in diagnostics for key in item})
    summary: dict[str, float] = {}
    for key in keys:
        values = [float(item[key]) for item in diagnostics if key in item]
        if values:
            summary[f"{key}_max"] = max(values)
    return summary


__all__ = [
    "AmplificationGridResult",
    "GridResult",
    "ResultFormatError",
    "load_amplification_results",
    "load_results",
    "run_solver_grid",
    "save_amplification_results",
    "save_results",
]
