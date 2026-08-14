"""Direct metric-curvature production for Li--Hou--Zhao Figs. 5 and 6."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from types import MappingProxyType, SimpleNamespace
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.io.tablei import TABLEI_POINTS
from schwgw.io.tablei_paper_inferred import load_uniform_source_contract
from schwgw.io.tablei_uniform import (
    CONVERGENCE_TOLERANCE,
    UNIFORM_FREQUENCIES,
    _atomic_json_no_overwrite,
    _atomic_npz_no_overwrite,
    _json_safe,
    _sha256,
)
from schwgw.numerics import (
    BoundaryConfig,
    extrapolate_r_out_ladder,
    solve_radial_mode,
)
from schwgw.numerics.matching import outer_asymptotic_basis
from schwgw.numerics.experimental.q018_rescaled_oracle import (
    RescaledOracleRequest,
    solve_q018_rescaled_oracle,
)
from schwgw.perturbations import Sector, V_RW, V_Zerilli
from schwgw.scattering.metric_curvature import compute_direct_metric_polarization
from schwgw.validation import finite_radius_tidal_response_metadata


SCHEMA_VERSION = "phase5_fig5_fig6_direct_metric_curvature_rout_v2"
MERGED_SCHEMA_VERSION = "phase5_fig5_fig6_direct_metric_curvature_merged_rout_v3"
AMPLITUDES = {"plus": 0.9 + 1.1j, "cross": 0.4 + 0.6j}
RADIAL_STEP_FRACTION = 1.0e-4
DEFAULT_R_OUT_LADDER = (1200.0, 1800.0, 2400.0)
MAX_OUTER_BASIS_CONDITION = 1.0e12
MAX_OUTER_BASIS_LOCAL_RESIDUAL = 1.0e-7
OBSERVER_FRAMES = ("static_orthonormal", "li_literal_cartesian")


class DirectTableIError(ValueError):
    """Raised when the direct Fig. 5/6 contract is not satisfied."""


@dataclass(frozen=True)
class DirectResponseColumns:
    F_plus: complex
    F_cross: complex
    h_plus_from_plus: complex
    h_cross_from_cross: complex
    h_cross_from_plus: complex
    h_plus_from_cross: complex
    diagnostics: MappingProxyType


class _DenseOracleSolution:
    """Unit-incoming solution with exact dense local ODE propagation."""

    def __init__(
        self,
        *,
        sector: Sector,
        ell: int,
        k: float,
        background: SchwarzschildBackground,
        lower: float,
        anchor: float,
        upper: float,
        oracle: Any,
        inward: Any,
        outward: Any,
    ) -> None:
        self.sector = sector
        self.ell = ell
        self.k = k
        self.background = background
        self.r_grid = np.asarray((lower, anchor, upper), dtype=float)
        self.valid_until_r = upper
        self.A_in = complex(oracle.A_in)
        self.A_out = complex(oracle.A_out)
        self.phase_factor = -self.A_out / (((-1) ** ell) * self.A_in)
        self.phase_shift = complex(-0.5j * np.log(self.phase_factor))
        self._anchor = anchor
        self._inward = inward
        self._outward = outward
        raw = dict(oracle.diagnostics)
        residual = max(
            float(raw["outer_boundary_residual"]),
            float(raw["normalization_residual"]),
            float(raw["log_derivative_match_residual"]),
        )
        self.diagnostics = SimpleNamespace(
            boundary_residual=float(raw["outer_boundary_residual"]),
            wronskian_residual=residual,
            flux_residual=residual,
            match_condition_number=float(raw["match_condition_number"]),
            warnings=(),
            solver="direct_tablei_dense_local_q018",
        )

    def _state(self, radius: float) -> np.ndarray:
        value = float(radius)
        if value < self.r_grid[0] or value > self.r_grid[-1]:
            raise ValueError("dense local oracle evaluation is outside its domain")
        solver = self._inward if value < self._anchor else self._outward
        state = np.asarray(solver.sol(value), dtype=np.complex128)
        if state.shape != (2,) or not np.all(np.isfinite(state)):
            raise RuntimeError("dense local oracle returned a non-finite state")
        return state

    def psi_at(self, radius: float) -> complex:
        return complex(self._state(radius)[0])

    def dpsi_dr_at(self, radius: float) -> complex:
        return complex(self._state(radius)[1])


class DenseRadialSpanCache:
    """Cache one dense full-domain or Q018-local solution per radial mode."""

    def __init__(self, *, lower: float, anchor: float, upper: float) -> None:
        if not lower < anchor < upper:
            raise ValueError("dense radial span must satisfy lower < anchor < upper")
        self._lower = float(lower)
        self._anchor = float(anchor)
        self._upper = float(upper)
        self._solutions: dict[tuple[Any, ...], Any] = {}
        self.solve_count = 0
        self.reuse_count = 0
        self.local_oracle_count = 0

    def __call__(
        self,
        sector: Sector,
        ell: int,
        k: float,
        background: SchwarzschildBackground,
        boundary_config: BoundaryConfig | None = None,
    ) -> Any:
        config = boundary_config or BoundaryConfig()
        key = (
            sector.value,
            int(ell),
            float(k),
            float(background.M),
            float(config.r_in_eps),
            None if config.r_out is None else float(config.r_out),
            float(config.rtol),
            float(config.atol),
            (
                None
                if config.required_eval_radius is None
                else float(config.required_eval_radius)
            ),
            config.outer_basis,
            int(config.outer_series_order),
        )
        if key in self._solutions:
            self.reuse_count += 1
            return self._solutions[key]
        solution = _solve_dense_span_mode(
            sector=sector,
            ell=ell,
            k=k,
            background=background,
            config=config,
            lower=self._lower,
            anchor=self._anchor,
            upper=self._upper,
        )
        self._solutions[key] = solution
        self.solve_count += 1
        if isinstance(solution, _DenseOracleSolution):
            self.local_oracle_count += 1
        return solution

    def metadata(self) -> dict[str, int]:
        return {
            "unique_solution_count": self.solve_count,
            "reuse_count": self.reuse_count,
            "dense_local_q018_count": self.local_oracle_count,
        }


def _radial_bounds() -> tuple[float, float, float]:
    anchor = min(point.r for point in TABLEI_POINTS)
    lower = anchor - 2.0 * RADIAL_STEP_FRACTION * max(anchor, 1.0)
    maximum = max(point.r for point in TABLEI_POINTS)
    upper = maximum + 2.0 * RADIAL_STEP_FRACTION * max(maximum, 1.0)
    return lower, anchor, upper


def _solve_tablei_dense_mode(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: SchwarzschildBackground,
    config: BoundaryConfig,
) -> Any:
    lower, anchor, upper = _radial_bounds()
    return _solve_dense_span_mode(
        sector=sector,
        ell=ell,
        k=k,
        background=background,
        config=config,
        lower=lower,
        anchor=anchor,
        upper=upper,
    )


def _solve_dense_span_mode(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: SchwarzschildBackground,
    config: BoundaryConfig,
    lower: float,
    anchor: float,
    upper: float,
) -> Any:
    dense_config = BoundaryConfig(
        r_in_eps=config.r_in_eps,
        r_out=config.r_out,
        rtol=config.rtol,
        atol=config.atol,
        required_eval_radius=upper,
        outer_basis=config.outer_basis,
        outer_series_order=config.outer_series_order,
    )
    if _local_span_is_evanescent(
        sector=sector,
        ell=ell,
        k=k,
        background=background,
        lower=lower,
        anchor=anchor,
        upper=upper,
    ):
        return _solve_dense_local_q018(
            sector=sector,
            ell=ell,
            k=k,
            background=background,
            config=config,
            lower=lower,
            anchor=anchor,
            upper=upper,
        )
    try:
        solution = solve_radial_mode(sector, ell, k, background, dense_config)
    except RuntimeError as exc:
        if not any(
            marker in str(exc)
            for marker in (
                "evanescent_tail_required_radius_uncovered",
                "evanescent_tail_required_radius_solver_failed",
            )
        ):
            raise
    else:
        certified_upper = (
            solution.r_grid[-1]
            if solution.valid_until_r is None
            else solution.valid_until_r
        )
        if float(solution.r_grid[0]) <= lower and float(certified_upper) >= upper:
            return solution
    return _solve_dense_local_q018(
        sector=sector,
        ell=ell,
        k=k,
        background=background,
        config=config,
        lower=lower,
        anchor=anchor,
        upper=upper,
    )


def _local_span_is_evanescent(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: SchwarzschildBackground,
    lower: float,
    anchor: float,
    upper: float,
) -> bool:
    """Return true only when the whole required local span is forbidden."""

    potentials = np.asarray(
        [
            (
                V_RW(ell, radius, background)
                if sector is Sector.ODD
                else V_Zerilli(ell, radius, background)
            )
            for radius in (lower, anchor, upper)
        ],
        dtype=np.float64,
    )
    return bool(np.all(potentials > float(k) ** 2))


def _solve_dense_local_q018(
    *,
    sector: Sector,
    ell: int,
    k: float,
    background: SchwarzschildBackground,
    config: BoundaryConfig,
    lower: float,
    anchor: float,
    upper: float,
) -> _DenseOracleSolution:
    if config.r_out is None:
        raise DirectTableIError("direct Table-I oracle requires finite r_out")
    oracle = solve_q018_rescaled_oracle(
        RescaledOracleRequest(
            sector=sector,
            ell=ell,
            k=float(k),
            required_radius=anchor,
            r_out=float(config.r_out),
            r_in_eps=float(config.r_in_eps),
            rtol=float(config.rtol),
            atol=float(config.atol),
            method_hint="direct_metric_curvature_tablei_dense_local",
        ),
        background,
    )
    residual = max(
        float(oracle.diagnostics["outer_boundary_residual"]),
        float(oracle.diagnostics["normalization_residual"]),
        float(oracle.diagnostics["log_derivative_match_residual"]),
    )
    if not oracle.valid_at_required_radius or residual > 1.0e-7:
        raise DirectTableIError("dense local Q018 oracle failed its residual gate")

    potential = V_RW if sector is Sector.ODD else V_Zerilli

    def rhs(radius: float, state: np.ndarray) -> np.ndarray:
        psi, derivative = state
        lapse = float(background.f(radius))
        lapse_derivative = float(background.df_dr(radius))
        value = float(potential(ell, radius, background))
        second = -(
            lapse * lapse_derivative * derivative + (k**2 - value) * psi
        ) / lapse**2
        return np.asarray((derivative, second), dtype=np.complex128)

    initial = np.asarray((oracle.psi, oracle.dpsi_dr), dtype=np.complex128)
    kwargs = {
        "method": "DOP853",
        "rtol": float(config.rtol),
        "atol": float(config.atol),
        "dense_output": True,
    }
    inward = solve_ivp(rhs, (anchor, lower), initial, **kwargs)
    outward = solve_ivp(rhs, (anchor, upper), initial, **kwargs)
    if not inward.success or not outward.success or inward.sol is None or outward.sol is None:
        raise DirectTableIError("dense local Q018 propagation failed")
    return _DenseOracleSolution(
        sector=sector,
        ell=ell,
        k=k,
        background=background,
        lower=lower,
        anchor=anchor,
        upper=upper,
        oracle=oracle,
        inward=inward,
        outward=outward,
    )


def compute_direct_response_columns(
    *,
    background: SchwarzschildBackground,
    k: float,
    r: float,
    theta: float,
    phi: float,
    lmax: int,
    boundary_config: BoundaryConfig,
    radial_solver: Callable[..., Any],
    observer_frame: str = "static_orthonormal",
    axis_regularization: float = 1.0e-6,
) -> DirectResponseColumns:
    plus = compute_direct_metric_polarization(
        background=background,
        k=k,
        r=r,
        theta=theta,
        phi=phi,
        A_plus=AMPLITUDES["plus"],
        A_cross=0.0j,
        lmax=lmax,
        boundary_config=boundary_config,
        radial_solver=radial_solver,
        observer_frame=observer_frame,
        axis_regularization=axis_regularization,
    )
    cross = compute_direct_metric_polarization(
        background=background,
        k=k,
        r=r,
        theta=theta,
        phi=phi,
        A_plus=0.0j,
        A_cross=AMPLITUDES["cross"],
        lmax=lmax,
        boundary_config=boundary_config,
        radial_solver=radial_solver,
        observer_frame=observer_frame,
        axis_regularization=axis_regularization,
    )
    phase = np.exp(1.0j * float(k) * float(r) * math.cos(float(theta)))
    diagonal_scale = max(abs(plus.h_plus), abs(cross.h_cross), np.finfo(float).tiny)
    leakage = max(abs(plus.h_cross), abs(cross.h_plus)) / diagonal_scale
    return DirectResponseColumns(
        F_plus=plus.h_plus / (AMPLITUDES["plus"] * phase),
        F_cross=cross.h_cross / (AMPLITUDES["cross"] * phase),
        h_plus_from_plus=plus.h_plus,
        h_cross_from_cross=cross.h_cross,
        h_cross_from_plus=plus.h_cross,
        h_plus_from_cross=cross.h_plus,
        diagnostics=MappingProxyType(
            {
                "bridge": "direct RW metric -> linearized Riemann -> incident E",
                "physical_claim": False,
                "physical_claim_scope": (
                    "qualified by the explicit gauge and observer frame"
                ),
                "gauge": "Regge-Wheeler",
                "observer_frame": observer_frame,
                "physical_within_frozen_gauge_frame_convention": True,
                "literal_li_paper_observer_equivalence": (
                    observer_frame == "li_literal_cartesian"
                ),
                "paper_equivalence": "YELLOW",
                "off_diagonal_relative": float(leakage),
            }
        ),
    )


def _relative_delta(final: np.ndarray, previous: np.ndarray) -> np.ndarray:
    return np.abs(final - previous) / np.maximum(
        1.0, np.maximum(np.abs(final), np.abs(previous))
    )


def simultaneous_response_from_columns(
    *,
    kM: float,
    point_r: np.ndarray,
    point_theta: np.ndarray,
    F_plus_diagonal: np.ndarray,
    F_cross_diagonal: np.ndarray,
    h_cross_from_plus: np.ndarray,
    h_plus_from_cross: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Assemble Li--Hou--Zhao Eq. (45) for the fixed mixed incident wave.

    The per-frequency transactions deliberately solve the two pure-input
    columns independently so that the response matrix can be audited.  The
    paper, however, fixes non-zero ``A_plus`` and ``A_cross`` simultaneously.
    Linearity therefore gives the paper-facing lensed components by adding
    the off-diagonal response before dividing by the corresponding Eq. (46)
    incident component.  No extra ODE solve or empirical fit enters here.
    """

    radius = np.asarray(point_r, dtype=np.float64)
    polar = np.asarray(point_theta, dtype=np.float64)
    plus = np.asarray(F_plus_diagonal, dtype=np.complex128)
    cross = np.asarray(F_cross_diagonal, dtype=np.complex128)
    cross_from_plus = np.asarray(h_cross_from_plus, dtype=np.complex128)
    plus_from_cross = np.asarray(h_plus_from_cross, dtype=np.complex128)
    expected_shape = np.broadcast_shapes(
        radius.shape,
        polar.shape,
        plus.shape,
        cross.shape,
        cross_from_plus.shape,
        plus_from_cross.shape,
    )
    if expected_shape != plus.shape or cross.shape != plus.shape:
        raise DirectTableIError("response-column arrays do not share one shape")
    phase = np.exp(1.0j * float(kM) * radius * np.cos(polar))
    incident_plus = AMPLITUDES["plus"] * phase
    incident_cross = AMPLITUDES["cross"] * phase
    if np.any(incident_plus == 0.0) or np.any(incident_cross == 0.0):
        raise DirectTableIError("Eq. (46) incident denominator unexpectedly vanished")
    return (
        plus + plus_from_cross / incident_plus,
        cross + cross_from_plus / incident_cross,
    )


def _frequency_paths(root: Path, kM: float) -> tuple[Path, Path]:
    token = f"{kM:g}".replace(".", "p")
    npz = root / "frequencies" / f"kM_{token}.npz"
    return npz, Path(str(npz) + ".json")


def _compute_frequency(
    kM: float,
    lmax_pair: tuple[int, int],
    *,
    observer_frame: str,
    r_out_ladder: tuple[float, float, float],
) -> tuple[dict, dict]:
    background = SchwarzschildBackground(M=1.0)
    outer_basis_preflight = _validate_outer_ladder_conditioning(
        kM=kM,
        lmax=max(lmax_pair),
        r_out_ladder=r_out_ladder,
        background=background,
    )
    lower, anchor, upper = _radial_bounds()
    radii = np.asarray(r_out_ladder, dtype=np.float64)
    plus_ladder = np.empty((3, 2, len(TABLEI_POINTS)), dtype=np.complex128)
    cross_ladder = np.empty_like(plus_ladder)
    offdiag_ladder = np.empty(
        (3, 2, len(TABLEI_POINTS), 2), dtype=np.complex128
    )
    cache_records = []
    for radius_index, r_out in enumerate(radii):
        cache = DenseRadialSpanCache(lower=lower, anchor=anchor, upper=upper)
        boundary = BoundaryConfig(
            r_in_eps=1e-6,
            r_out=float(r_out),
            rtol=1e-10,
            atol=1e-12,
            outer_basis="jost_1_over_r",
            outer_series_order=160,
        )
        for row, lmax in enumerate(lmax_pair):
            for index, point in enumerate(TABLEI_POINTS):
                result = compute_direct_response_columns(
                    background=background,
                    k=kM,
                    r=point.r,
                    theta=point.theta,
                    phi=point.phi,
                    lmax=lmax,
                    boundary_config=boundary,
                    radial_solver=cache,
                    observer_frame=observer_frame,
                )
                plus_ladder[radius_index, row, index] = result.F_plus
                cross_ladder[radius_index, row, index] = result.F_cross
                offdiag_ladder[radius_index, row, index] = (
                    result.h_cross_from_plus,
                    result.h_plus_from_cross,
                )
        cache_records.append({"r_out": float(r_out), **cache.metadata()})
    plus_fit = extrapolate_r_out_ladder(radii, plus_ladder)
    cross_fit = extrapolate_r_out_ladder(radii, cross_ladder)
    offdiag_fit = extrapolate_r_out_ladder(radii, offdiag_ladder)
    plus = plus_fit.extrapolated
    cross = cross_fit.extrapolated
    offdiag = offdiag_fit.extrapolated
    dplus = _relative_delta(plus[-1], plus[-2])
    dcross = _relative_delta(cross[-1], cross[-2])
    maximum = float(max(dplus.max(), dcross.max()))
    if maximum > CONVERGENCE_TOLERANCE:
        raise DirectTableIError(
            f"direct-curvature final lmax pair failed at kM={kM}: {maximum}"
        )
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "complete": True,
        "kM": kM,
        "lmax_values": list(lmax_pair),
        "convergence_tolerance": CONVERGENCE_TOLERANCE,
        "max_final_pair_delta_plus": float(dplus.max()),
        "max_final_pair_delta_cross": float(dcross.max()),
        "radial_cache_by_r_out": cache_records,
        "radial_stencil_step_fraction": RADIAL_STEP_FRACTION,
        **finite_radius_tidal_response_metadata(
            observer_worldline=(
                "fixed Schwarzschild-coordinate observer; interpretation "
                f"qualified by frame={observer_frame}"
            ),
            tetrad=(
                "runtime explicit static orthonormal or Li-literal "
                "Cartesian-Jacobian frame"
            ),
            polarization_basis="incident-aligned transverse x/y basis",
            phase_origin=(
                "r_star=r+2M log(r/2M-1), Fourier exp(-i k t), "
                "incident plane-wave baseline exp(i k z)"
            ),
            axis_regularization=(
                "theta clamped to 1e-6; Phase-6 axis ladder not yet closed"
            ),
            production_backend=(
                "Jost/r_out RWZ radial solve -> RW-gauge metric -> "
                "linearized Riemann"
            ),
        ),
        "polarization_bridge": (
            "direct RW-gauge metric -> linearized Riemann -> incident-frame E"
        ),
        "response_surface": "pure-plus and pure-cross diagonal columns",
        "physical_claim": False,
        "physical_claim_scope": (
            "qualified by the explicit gauge and observer frame"
        ),
        "gauge": "Regge-Wheeler",
        "observer_frame": observer_frame,
        "physical_within_frozen_gauge_frame_convention": True,
        "literal_li_paper_observer_equivalence": (
            observer_frame == "li_literal_cartesian"
        ),
        "paper_equivalence": "YELLOW",
        "outer_basis": "jost_1_over_r",
        "outer_series_order": 160,
        "outer_basis_preflight": outer_basis_preflight,
        "r_out_ladder": list(r_out_ladder),
        "r_out_extrapolation": "quadratic in 1/r_out",
        "max_r_out_uncertainty_plus": float(np.max(plus_fit.uncertainty)),
        "max_r_out_uncertainty_cross": float(np.max(cross_fit.uncertainty)),
        "max_r_out_uncertainty_off_diagonal": float(
            np.max(offdiag_fit.uncertainty)
        ),
        "no_interpolation": True,
        "no_smoothing": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
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
        "lmax_values": np.asarray(lmax_pair),
        "r_out_ladder": radii,
        "F_plus_r_out_ladder": plus_ladder,
        "F_cross_r_out_ladder": cross_ladder,
        "off_diagonal_r_out_ladder": offdiag_ladder,
        "F_plus_r_out_extrapolation_uncertainty": plus_fit.uncertainty,
        "F_cross_r_out_extrapolation_uncertainty": cross_fit.uncertainty,
        "off_diagonal_r_out_extrapolation_uncertainty": offdiag_fit.uncertainty,
        "F_plus_r_out_adjacent_relative_change": plus_fit.adjacent_relative_change,
        "F_cross_r_out_adjacent_relative_change": cross_fit.adjacent_relative_change,
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
        "off_diagonal_history": offdiag,
        "metadata_json": np.asarray(json.dumps(_json_safe(metadata), sort_keys=True)),
    }
    return arrays, metadata


def _validate_outer_ladder_conditioning(
    *,
    kM: float,
    lmax: int,
    r_out_ladder: tuple[float, float, float],
    background: SchwarzschildBackground,
) -> dict[str, float]:
    """Reject a finite-radius ladder that cannot resolve the Jost basis.

    Low-frequency high-ell modes can still lie inside their centrifugal
    barrier at ``r_out=300``.  There the two oscillatory Jost columns become
    numerically indistinguishable in double precision even though each local
    series residual is small.  A production ladder must therefore satisfy
    both the local-equation and two-column conditioning gates before any ODE
    solve is launched.
    """

    maximum_condition = 0.0
    maximum_residual = 0.0
    for r_out in r_out_ladder:
        for sector in (Sector.ODD, Sector.EVEN):
            incoming = outer_asymptotic_basis(
                sector=sector,
                ell=lmax,
                r=r_out,
                k=kM,
                background=background,
                sign=-1,
                basis="jost_1_over_r",
                series_order=160,
            )
            outgoing = outer_asymptotic_basis(
                sector=sector,
                ell=lmax,
                r=r_out,
                k=kM,
                background=background,
                sign=1,
                basis="jost_1_over_r",
                series_order=160,
            )
            matrix = np.asarray(
                (
                    (incoming.psi, outgoing.psi),
                    (incoming.dpsi_dr, outgoing.dpsi_dr),
                ),
                dtype=np.complex128,
            )
            condition = float(np.linalg.cond(matrix))
            residual = max(incoming.series_residual, outgoing.series_residual)
            if not np.isfinite(condition) or condition > MAX_OUTER_BASIS_CONDITION:
                raise DirectTableIError(
                    "Jost outer-basis ladder is ill-conditioned before science: "
                    f"kM={kM}, ell={lmax}, sector={sector.value}, "
                    f"r_out={r_out}, condition={condition}"
                )
            if residual > MAX_OUTER_BASIS_LOCAL_RESIDUAL:
                raise DirectTableIError(
                    "Jost outer-basis local residual failed before science: "
                    f"kM={kM}, ell={lmax}, sector={sector.value}, "
                    f"r_out={r_out}, residual={residual}"
                )
            maximum_condition = max(maximum_condition, condition)
            maximum_residual = max(maximum_residual, residual)
    return {
        "max_condition_number": maximum_condition,
        "max_local_ode_residual": maximum_residual,
        "condition_limit": MAX_OUTER_BASIS_CONDITION,
        "local_ode_residual_limit": MAX_OUTER_BASIS_LOCAL_RESIDUAL,
    }


def produce_direct_tablei_uniform(
    *,
    output_dir: str | Path,
    frequencies: Sequence[float] | None = None,
    resume: bool = False,
    observer_frame: str = "static_orthonormal",
    r_out_ladder: tuple[float, float, float] = DEFAULT_R_OUT_LADDER,
    progress: Callable[[dict[str, Any]], None] | None = None,
) -> Path:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    schedule, _ = load_uniform_source_contract()
    selected = UNIFORM_FREQUENCIES if frequencies is None else tuple(frequencies)
    if len(set(selected)) != len(selected) or tuple(sorted(selected)) != selected:
        raise DirectTableIError("frequencies must be unique and ordered")
    if any(value not in schedule for value in selected):
        raise DirectTableIError("requested frequency is outside the frozen 0.1 grid")
    if observer_frame not in OBSERVER_FRAMES:
        raise DirectTableIError("unsupported observer frame")
    if (
        tuple(sorted(set(r_out_ladder))) != tuple(r_out_ladder)
        or len(r_out_ladder) != 3
        or r_out_ladder[0] <= max(point.r for point in TABLEI_POINTS)
    ):
        raise DirectTableIError(
            "r_out_ladder must contain three unique increasing outer radii"
        )
    for kM in selected:
        npz, sidecar = _frequency_paths(root, kM)
        if npz.exists() or sidecar.exists():
            if resume and _transaction_valid(
                npz,
                sidecar,
                kM,
                schedule[kM],
                observer_frame=observer_frame,
                r_out_ladder=r_out_ladder,
            ):
                continue
            raise DirectTableIError(f"refusing existing transaction for kM={kM}")
        arrays, metadata = _compute_frequency(
            kM,
            schedule[kM],
            observer_frame=observer_frame,
            r_out_ladder=r_out_ladder,
        )
        _atomic_npz_no_overwrite(npz, arrays)
        metadata["npz_sha256"] = _sha256(npz)
        _atomic_json_no_overwrite(sidecar, metadata)
        if progress is not None:
            progress({"event": "direct_tablei_frequency_complete", "kM": kM})
    return root


def _transaction_valid(
    npz: Path,
    sidecar: Path,
    kM: float,
    lmax_pair: tuple[int, int],
    *,
    observer_frame: str | None = None,
    r_out_ladder: tuple[float, float, float] | None = None,
) -> bool:
    try:
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        with np.load(npz, allow_pickle=False) as data:
            okay = (
                float(data["kM"]) == kM
                and tuple(np.asarray(data["lmax_values"], dtype=int)) == lmax_pair
                and data["F_plus_complex"].shape == (8,)
                and data["F_cross_complex"].shape == (8,)
                and data["F_plus_r_out_ladder"].shape == (3, 2, 8)
                and data["F_cross_r_out_ladder"].shape == (3, 2, 8)
            )
        return bool(
            okay
            and metadata.get("schema_version") == SCHEMA_VERSION
            and metadata.get("npz_sha256") == _sha256(npz)
            and (
                observer_frame is None
                or metadata.get("observer_frame") == observer_frame
            )
            and (
                r_out_ladder is None
                or metadata.get("r_out_ladder") == list(r_out_ladder)
            )
        )
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False


def merge_direct_tablei_uniform(
    *,
    transaction_dir: str | Path,
    output_path: str | Path,
) -> Path:
    root = Path(transaction_dir)
    output = Path(output_path)
    if output.exists() or Path(str(output) + ".json").exists():
        raise DirectTableIError(f"refusing to overwrite {output}")
    schedule, bindings = load_uniform_source_contract()
    rows = {
        name: []
        for name in (
            "F_plus_complex",
            "F_cross_complex",
            "F_plus_diagonal_complex",
            "F_cross_diagonal_complex",
            "h_cross_from_plus_complex",
            "h_plus_from_cross_complex",
            "final_pair_delta_plus",
            "final_pair_delta_cross",
            "final_pair_delta_plus_diagonal",
            "final_pair_delta_cross_diagonal",
            "r_out_uncertainty_plus_diagonal",
            "r_out_uncertainty_cross_diagonal",
        )
    }
    transactions = []
    first = None
    observer_frame = None
    r_out_ladder = None
    for kM in UNIFORM_FREQUENCIES:
        npz, sidecar = _frequency_paths(root, kM)
        try:
            transaction_metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise DirectTableIError(
                f"missing or invalid transaction metadata for kM={kM}"
            ) from exc
        current_frame = transaction_metadata.get("observer_frame")
        current_ladder = transaction_metadata.get("r_out_ladder")
        if observer_frame is None:
            observer_frame = current_frame
            r_out_ladder = current_ladder
        elif current_frame != observer_frame or current_ladder != r_out_ladder:
            raise DirectTableIError("transactions mix observer frames or r_out ladders")
        if not _transaction_valid(npz, sidecar, kM, schedule[kM]):
            raise DirectTableIError(f"missing or invalid transaction for kM={kM}")
        with np.load(npz, allow_pickle=False) as data:
            if first is None:
                first = {name: np.asarray(data[name]) for name in data.files}
            diagonal_plus_history = np.asarray(
                data["F_plus_history"], dtype=np.complex128
            )
            diagonal_cross_history = np.asarray(
                data["F_cross_history"], dtype=np.complex128
            )
            off_diagonal_history = np.asarray(
                data["off_diagonal_history"], dtype=np.complex128
            )
            if (
                diagonal_plus_history.shape != (2, 8)
                or diagonal_cross_history.shape != (2, 8)
                or off_diagonal_history.shape != (2, 8, 2)
            ):
                raise DirectTableIError(
                    f"invalid response-column history for kM={kM}"
                )
            simultaneous_plus_history, simultaneous_cross_history = (
                simultaneous_response_from_columns(
                    kM=kM,
                    point_r=np.asarray(data["point_r"], dtype=np.float64),
                    point_theta=np.asarray(data["point_theta"], dtype=np.float64),
                    F_plus_diagonal=diagonal_plus_history,
                    F_cross_diagonal=diagonal_cross_history,
                    h_cross_from_plus=off_diagonal_history[:, :, 0],
                    h_plus_from_cross=off_diagonal_history[:, :, 1],
                )
            )
            simultaneous_delta_plus = _relative_delta(
                simultaneous_plus_history[-1], simultaneous_plus_history[-2]
            )
            simultaneous_delta_cross = _relative_delta(
                simultaneous_cross_history[-1], simultaneous_cross_history[-2]
            )
            maximum = float(
                max(simultaneous_delta_plus.max(), simultaneous_delta_cross.max())
            )
            if maximum > CONVERGENCE_TOLERANCE:
                raise DirectTableIError(
                    "mixed-input direct-curvature final lmax pair failed at "
                    f"kM={kM}: {maximum}"
                )
            rows["F_plus_complex"].append(simultaneous_plus_history[-1])
            rows["F_cross_complex"].append(simultaneous_cross_history[-1])
            rows["F_plus_diagonal_complex"].append(diagonal_plus_history[-1])
            rows["F_cross_diagonal_complex"].append(diagonal_cross_history[-1])
            rows["h_cross_from_plus_complex"].append(
                off_diagonal_history[-1, :, 0]
            )
            rows["h_plus_from_cross_complex"].append(
                off_diagonal_history[-1, :, 1]
            )
            rows["final_pair_delta_plus"].append(simultaneous_delta_plus)
            rows["final_pair_delta_cross"].append(simultaneous_delta_cross)
            rows["final_pair_delta_plus_diagonal"].append(
                np.asarray(data["final_pair_delta_plus"], dtype=np.float64)
            )
            rows["final_pair_delta_cross_diagonal"].append(
                np.asarray(data["final_pair_delta_cross"], dtype=np.float64)
            )
            rows["r_out_uncertainty_plus_diagonal"].append(
                np.asarray(
                    data["F_plus_r_out_extrapolation_uncertainty"][-1],
                    dtype=np.float64,
                )
            )
            rows["r_out_uncertainty_cross_diagonal"].append(
                np.asarray(
                    data["F_cross_r_out_extrapolation_uncertainty"][-1],
                    dtype=np.float64,
                )
            )
        transactions.append(
            {
                "kM": kM,
                "npz": str(npz),
                "npz_sha256": _sha256(npz),
                "sidecar_sha256": _sha256(sidecar),
            }
        )
    assert first is not None
    arrays = {
        "kM_values": np.asarray(UNIFORM_FREQUENCIES),
        **{
            name: first[name]
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
                "r_out_ladder",
            )
        },
        **{name: np.stack(values) for name, values in rows.items()},
    }
    arrays["abs_F_plus"] = np.abs(arrays["F_plus_complex"])
    arrays["abs_F_cross"] = np.abs(arrays["F_cross_complex"])
    arrays["arg_F_plus_principal"] = np.angle(arrays["F_plus_complex"])
    arrays["arg_F_cross_principal"] = np.angle(arrays["F_cross_complex"])
    arrays["abs_F_plus_diagonal"] = np.abs(arrays["F_plus_diagonal_complex"])
    arrays["abs_F_cross_diagonal"] = np.abs(arrays["F_cross_diagonal_complex"])
    arrays["arg_F_plus_diagonal_principal"] = np.angle(
        arrays["F_plus_diagonal_complex"]
    )
    arrays["arg_F_cross_diagonal_principal"] = np.angle(
        arrays["F_cross_diagonal_complex"]
    )
    arrays["arg_F_plus_unwrapped"] = np.unwrap(
        arrays["arg_F_plus_principal"], axis=0
    )
    arrays["arg_F_cross_unwrapped"] = np.unwrap(
        arrays["arg_F_cross_principal"], axis=0
    )
    arrays["arg_F_plus_diagonal_unwrapped"] = np.unwrap(
        arrays["arg_F_plus_diagonal_principal"], axis=0
    )
    arrays["arg_F_cross_diagonal_unwrapped"] = np.unwrap(
        arrays["arg_F_cross_diagonal_principal"], axis=0
    )
    metadata = {
        "schema_version": MERGED_SCHEMA_VERSION,
        "shape": [40, 8],
        "transactions": transactions,
        "lmax_source_bindings": bindings,
        "incident_amplitudes": _json_safe(AMPLITUDES),
        "primary_response_surface": (
            "Li-Hou-Zhao Eq. (45)-(46) component ratios for simultaneous "
            "fixed A_plus/A_cross incidence"
        ),
        "diagnostic_response_surface": (
            "pure-input diagonal response columns retained separately; not "
            "selected as the paper definition"
        ),
        "mixed_response_assembly": (
            "linear sum of diagonal and off-diagonal metric-curvature "
            "columns; no additional ODE solves and no empirical fit"
        ),
        "radial_derivative_method": (
            "RW/Zerilli ODE psi2/psi3 plus Richardson-extrapolated "
            "reconstruction-coefficient derivatives"
        ),
        "dense_solution_radial_differencing": False,
        "requested_radial_step_fraction": RADIAL_STEP_FRACTION,
        "radial_coefficient_step_floor_fraction": 1.0e-3,
        "physical_claim": False,
        "physical_claim_scope": (
            "qualified by the explicit gauge and observer frame"
        ),
        "gauge": "Regge-Wheeler",
        "observer_frame": observer_frame,
        "physical_within_frozen_gauge_frame_convention": True,
        "literal_li_paper_observer_equivalence": (
            observer_frame == "li_literal_cartesian"
        ),
        "paper_equivalence": "YELLOW",
        "r_out_ladder": r_out_ladder,
        "r_out_extrapolation": "quadratic in 1/r_out",
        "no_interpolation": True,
        "no_smoothing": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    arrays["metadata_json"] = np.asarray(
        json.dumps(_json_safe(metadata), sort_keys=True)
    )
    _atomic_npz_no_overwrite(output, arrays)
    metadata["npz_sha256"] = _sha256(output)
    _atomic_json_no_overwrite(Path(str(output) + ".json"), metadata)
    return output


__all__ = [
    "DEFAULT_R_OUT_LADDER",
    "DenseRadialSpanCache",
    "DirectResponseColumns",
    "DirectTableIError",
    "OBSERVER_FRAMES",
    "compute_direct_response_columns",
    "merge_direct_tablei_uniform",
    "produce_direct_tablei_uniform",
    "simultaneous_response_from_columns",
]
