"""Joint production of direct-curvature Fig. 3 and Fig. 7 grids."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Any

import numpy as np

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.io.apparent import ApparentGridResult
from schwgw.io.config import SolverConfig
from schwgw.io.results import GridResult
from schwgw.numerics import BoundaryConfig, solve_radial_mode
from schwgw.scattering.apparent import apparent_polarizations_from_strict_np
from schwgw.scattering.metric_curvature import (
    compute_metric_curvature_polarization,
    strict_np_from_incident_riemann,
)
from schwgw.validation import finite_radius_tidal_response_metadata


ProgressCallback = Callable[[dict[str, Any]], None]


@dataclass(frozen=True)
class DirectCurvatureGridPair:
    """Physical transverse field and apparent diagnostics from one curvature grid."""

    physical: GridResult
    apparent: ApparentGridResult


class _RadialCache:
    def __init__(self) -> None:
        self._cache: dict[tuple[Any, ...], Any] = {}
        self.hit_count = 0
        self.unique_solution_count = 0

    def __call__(
        self,
        sector: Any,
        ell: int,
        k: float,
        background: Any,
        boundary: Any,
    ) -> Any:
        key = (
            getattr(sector, "value", sector),
            int(ell),
            float(k),
            float(background.M),
            tuple(
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
                    "outer_basis",
                    "outer_series_order",
                )
            ),
        )
        if key in self._cache:
            self.hit_count += 1
            return self._cache[key]
        solution = solve_radial_mode(sector, ell, k, background, boundary)
        self._cache[key] = solution
        self.unique_solution_count += 1
        return solution

    def metadata(self) -> dict[str, int | bool]:
        return {
            "enabled": True,
            "unique_solution_count": self.unique_solution_count,
            "hit_count": self.hit_count,
            "key_count": len(self._cache),
        }

    def warnings(self) -> list[dict[str, Any]]:
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


def run_direct_curvature_xz_grids(
    config: SolverConfig,
    *,
    source_command: list[str] | None = None,
    progress: ProgressCallback | None = None,
) -> DirectCurvatureGridPair:
    """Compute Fig. 3 and Fig. 7 fields from one shared direct-curvature pass."""

    if config.observer.kind != "xz_plane":
        raise ValueError("joint direct-curvature production requires an xz_plane grid.")
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
    cache = _RadialCache()
    x = np.asarray(config.observer.x_values, dtype=np.float64)
    z = np.asarray(config.observer.z_values, dtype=np.float64)
    if not np.array_equal(x, -x[::-1]) or x[x.size // 2] != 0.0:
        raise ValueError(
            "direct-curvature x-z production requires an exact x-reflection grid"
        )
    xx, zz = np.meshgrid(x, z)
    radius = np.sqrt(xx**2 + zz**2)
    valid = np.isfinite(radius) & (radius > 2.0 * config.background.M)
    theta = np.full(radius.shape, np.nan, dtype=np.float64)
    phi = np.full(radius.shape, np.nan, dtype=np.float64)
    theta[valid] = np.arccos(np.clip(zz[valid] / radius[valid], -1.0, 1.0))
    phi[valid] = np.where(xx[valid] >= 0.0, 0.0, np.pi)
    empty = np.nan + 1.0j * np.nan
    fields = {
        name: np.full(radius.shape, empty, dtype=np.complex128)
        for name in (
            "h_plus",
            "h_cross",
            "h_x",
            "h_y",
            "h_b",
            "h_longitudinal",
        )
    }
    maxima: dict[str, float] = {}
    primary = valid & (xx >= 0.0)
    points = np.argwhere(primary)
    completed = 0
    next_report = 1000
    for number, (z_index, x_index) in enumerate(points, start=1):
        direct = compute_metric_curvature_polarization(
            background=background,
            k=k,
            r=float(radius[z_index, x_index]),
            theta=float(theta[z_index, x_index]),
            phi=float(phi[z_index, x_index]),
            A_plus=config.wave.A_plus,
            A_cross=config.wave.A_cross,
            lmax=config.numerics.lmax,
            boundary_config=boundary,
            radial_solver=cache,
            observer_frame=config.observer.observer_frame,
        )
        strict_np = strict_np_from_incident_riemann(
            direct.riemann,
            M=config.background.M,
            r=float(radius[z_index, x_index]),
            theta=float(direct.polarization.diagnostics["axis_evaluation_theta"]),
            phi=float(phi[z_index, x_index]),
            observer_frame=config.observer.observer_frame,
        )
        apparent = apparent_polarizations_from_strict_np(
            k,
            strict_np,
            diagnostics=direct.polarization.diagnostics,
        )
        mirror_index = x.size - 1 - int(x_index)
        point_values = {
            "h_plus": direct.polarization.h_plus,
            "h_cross": direct.polarization.h_cross,
            "h_x": apparent.h_x,
            "h_y": apparent.h_y,
            "h_b": apparent.h_b,
            "h_longitudinal": apparent.h_longitudinal,
        }
        reflection_parity = {
            "h_plus": 1.0,
            "h_cross": 1.0,
            "h_x": -1.0,
            "h_y": -1.0,
            "h_b": 1.0,
            "h_longitudinal": 1.0,
        }
        for name, value in point_values.items():
            fields[name][z_index, x_index] = value
            if mirror_index != x_index:
                fields[name][z_index, mirror_index] = reflection_parity[name] * value
        completed += 1 if mirror_index == x_index else 2
        for name, value in direct.polarization.diagnostics.items():
            maxima[name] = max(maxima.get(name, -np.inf), float(value))
        if progress is not None and (
            number == 1 or completed >= next_report or number == len(points)
        ):
            progress(
                {
                    "event": "direct_curvature_xz_progress",
                    "completed": completed,
                    "total": int(np.count_nonzero(valid)),
                    "evaluated": number,
                    "evaluated_total": len(points),
                    "kM": config.wave.kM,
                }
            )
            while next_report <= completed:
                next_report += 1000
    if completed != int(np.count_nonzero(valid)):
        raise RuntimeError("x-reflection fill did not close the valid grid")

    convergence = _convergence(
        config=config,
        background=background,
        boundary=boundary,
        cache=cache,
        k=k,
        observer_r=float(np.max(radius[valid])),
    )
    now = datetime.now(timezone.utc).isoformat()
    common = {
        "created_at": now,
        "config": config.to_dict(),
        "source_command": source_command,
        "grid": {
            "kind": "xz_plane",
            "shape": list(radius.shape),
            "valid_point_count": int(np.count_nonzero(valid)),
            "invalid_point_count": int(valid.size - np.count_nonzero(valid)),
            "evaluated_point_count": int(np.count_nonzero(primary)),
            "x_reflection_reused_point_count": int(
                np.count_nonzero(valid) - np.count_nonzero(primary)
            ),
            "x_reflection_exact_m_plus_minus_2": True,
            "x_reflection_parity": {
                "h_plus": 1,
                "h_cross": 1,
                "h_x": -1,
                "h_y": -1,
                "h_b": 1,
                "h_longitudinal": 1,
            },
            "coordinate_conversion": (
                "r=sqrt(x^2+z^2), theta=arccos(z/r), phi=0 if x>=0 else pi"
            ),
        },
        "diagnostics": {
            "maxima": maxima,
            "run_radial_cache": cache.metadata(),
            "radial_diagnostic_warnings": cache.warnings(),
            "convergence": convergence,
        },
        "observer_frame": config.observer.observer_frame,
    }
    physical_metadata = {
        **common,
        "case_id": config.case_id.replace("FIG3", "FIG3_DIRECT_CURVATURE"),
        "schema_version": "li_hou_zhao_fig3_direct_curvature_xz_v1",
        "figure": 3,
        "convention": {
            "fourier": "exp(-i k t)",
            "metric_signature": "(-,+,+,+)",
            "units": "G=c=M=1",
            "field_content": "total_incident_plus_reflected",
            **finite_radius_tidal_response_metadata(
                observer_worldline=(
                    "fixed Schwarzschild-coordinate observer; interpretation "
                    f"qualified by frame={config.observer.observer_frame}"
                ),
                tetrad=(
                    "runtime explicit static orthonormal or Li-literal "
                    "Cartesian-Jacobian frame"
                ),
                polarization_basis="incident-aligned transverse x/y basis",
                phase_origin=(
                    "r_star=r+2M log(r/2M-1), Fourier exp(-i k t), "
                    "coordinate t origin fixed by incident baseline"
                ),
                axis_regularization=(
                    "theta clamped to 1e-6; Phase-6 axis ladder not yet closed"
                ),
                production_backend=(
                    "RW/Zerilli radial solve -> RW-gauge metric -> "
                    "linearized Riemann"
                ),
            ),
            "polarization_bridge": (
                "direct RW-gauge metric -> linearized Riemann -> incident-frame E"
            ),
            "polarization_bridge_validated": True,
            "positive_frequency_reality_bridge_required": False,
            "physical_claim": False,
            "physical_claim_scope": (
                "qualified by the explicit gauge and observer frame"
            ),
            "gauge": "Regge-Wheeler",
            "observer_frame": config.observer.observer_frame,
            "physical_within_frozen_gauge_frame_convention": True,
            "literal_li_paper_observer_equivalence": (
                config.observer.observer_frame == "li_literal_cartesian"
            ),
            "paper_equivalence": "YELLOW",
        },
    }
    apparent_metadata = {
        **common,
        "case_id": config.case_id.replace("FIG3", "FIG7_DIRECT_CURVATURE"),
        "schema_version": "li_hou_zhao_fig7_direct_curvature_xz_v1",
        "figure": 7,
        "physical_claim": False,
        "interpretation": (
            "incident-frame tetrad-dependent apparent polarizations; "
            "not additional propagating degrees of freedom"
        ),
        "convention": {
            "fourier": "exp(-i k t)",
            "metric_signature": "(-,+,+,+)",
            "units": "G=c=M=1",
            "tetrad": "direct incident-frame Riemann contractions",
            "strict_np_lower_scalar_completion": False,
            "observer_frame": config.observer.observer_frame,
        },
        "definitions": {
            "h_x": "-(Psi1+Psi3)/(2 k^2)",
            "h_y": "+i(Psi1-Psi3)/(2 k^2)",
            "h_b": "-Psi2/(2 k^2)",
            "h_longitudinal": "-Psi2/k^2 = 2 h_b",
        },
    }
    physical = GridResult(
        x=x,
        z=z,
        r=radius,
        theta=theta,
        phi=phi,
        valid_mask=valid,
        h_plus=fields["h_plus"],
        h_cross=fields["h_cross"],
        metadata=physical_metadata,
    )
    apparent = ApparentGridResult(
        x=x,
        z=z,
        r=radius,
        theta=theta,
        phi=phi,
        valid_mask=valid,
        h_x=fields["h_x"],
        h_y=fields["h_y"],
        h_b=fields["h_b"],
        h_longitudinal=fields["h_longitudinal"],
        metadata=apparent_metadata,
    )
    return DirectCurvatureGridPair(physical=physical, apparent=apparent)


def _convergence(
    *,
    config: SolverConfig,
    background: SchwarzschildBackground,
    boundary: BoundaryConfig,
    cache: _RadialCache,
    k: float,
    observer_r: float,
) -> dict[str, Any]:
    policy = config.convergence
    if policy is None or not policy.enabled:
        return {"enabled": False}
    samples: dict[int, list[np.ndarray]] = {}
    for lmax in policy.lmax_values:
        rows: list[np.ndarray] = []
        for theta in policy.theta_values:
            for phi in policy.phi_values:
                direct = compute_metric_curvature_polarization(
                    background=background,
                    k=k,
                    r=observer_r,
                    theta=theta,
                    phi=phi,
                    A_plus=config.wave.A_plus,
                    A_cross=config.wave.A_cross,
                    lmax=lmax,
                    boundary_config=boundary,
                    radial_solver=cache,
                    observer_frame=config.observer.observer_frame,
                )
                strict_np = strict_np_from_incident_riemann(
                    direct.riemann,
                    M=config.background.M,
                    r=observer_r,
                    theta=float(
                        direct.polarization.diagnostics["axis_evaluation_theta"]
                    ),
                    phi=phi,
                    observer_frame=config.observer.observer_frame,
                )
                apparent = apparent_polarizations_from_strict_np(k, strict_np)
                rows.append(
                    np.asarray(
                        (
                            direct.polarization.h_plus,
                            direct.polarization.h_cross,
                            apparent.h_x,
                            apparent.h_y,
                            apparent.h_b,
                            apparent.h_longitudinal,
                        ),
                        dtype=np.complex128,
                    )
                )
        samples[lmax] = rows
    history = []
    for previous, current in zip(
        policy.lmax_values[:-1], policy.lmax_values[1:], strict=True
    ):
        changes = []
        for old, new in zip(samples[previous], samples[current], strict=True):
            denominator = np.maximum(np.maximum(np.abs(old), np.abs(new)), 1.0e-30)
            changes.extend((np.abs(new - old) / denominator).tolist())
        history.append(
            {
                "previous_lmax": int(previous),
                "current_lmax": int(current),
                "max_relative_change": max(changes),
            }
        )
    return {
        "enabled": True,
        "history": history,
        "final_lmax_pair": list(policy.lmax_values[-2:]),
        "selected_threshold": policy.selected_threshold,
        "near_axis_threshold": policy.near_axis_threshold,
        "final_pair_passed": bool(
            history[-1]["max_relative_change"] <= policy.near_axis_threshold
        ),
    }


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


__all__ = ["DirectCurvatureGridPair", "run_direct_curvature_xz_grids"]
