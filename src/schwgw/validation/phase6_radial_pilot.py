"""Bounded Phase-6 selected-mode radial S-matrix validation pilot.

This module deliberately produces mode-local evidence.  It does not implement
or permit a project-wide or V1-wide GREEN verdict.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
import math
from pathlib import Path
from typing import Any

import numpy as np

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.numerics import BoundaryConfig, RadialSolution, solve_radial_mode
from schwgw.perturbations import Sector
PILOT_SCHEMA = "schwgw_phase6_radial_s_matrix_selected_mode_pilot_v1"
MODE_SCHEMA = "schwgw_phase6_radial_s_matrix_mode_evidence_v1"
BACKEND_SCHEMA = "schwgw_phase6_radial_backend_capability_v1"


class RadialPilotContractError(ValueError):
    """Raised when selected-mode evidence violates the Phase-6 contract."""


@dataclass(frozen=True)
class SelectedMode:
    mode_id: str
    regime: str
    sector: Sector
    ell: int
    kM: float
    r_eval: float | None = None
    q018_oracle: str | None = None

    def __post_init__(self) -> None:
        if not self.mode_id or not self.regime:
            raise RadialPilotContractError("mode_id and regime must be non-empty")
        if self.ell < 2 or not math.isfinite(self.kM) or self.kM <= 0.0:
            raise RadialPilotContractError("selected mode parameters are invalid")
        if self.r_eval is not None and (
            not math.isfinite(self.r_eval) or self.r_eval <= 2.0
        ):
            raise RadialPilotContractError("r_eval must lie outside the horizon")
        if self.q018_oracle is not None and self.r_eval is None:
            raise RadialPilotContractError("Q018 modes require an evaluation radius")

    def to_metadata(self) -> dict[str, object]:
        result: dict[str, object] = {
            "mode_id": self.mode_id,
            "regime": self.regime,
            "sector": self.sector.value,
            "ell": self.ell,
            "kM": self.kM,
        }
        if self.r_eval is not None:
            result["r_eval_M"] = self.r_eval
            result["turning_ratio_ell_over_k_r_eval"] = self.ell / (
                self.kM * self.r_eval
            )
        if self.q018_oracle is not None:
            result["experimental_required_radius_oracle"] = self.q018_oracle
        return result


@dataclass(frozen=True)
class BackendCapability:
    backend_id: str
    algorithm: str
    status: str
    genuinely_independent: bool
    implementation_version: str
    source_sha256: Mapping[str, str]
    dependency_sha256: Mapping[str, str]
    input_sha256: Mapping[str, str]
    shared_components: tuple[str, ...]
    call_graph_isolation: str
    actual_backend: str | None = None
    actual_precision_bits: int | None = None
    actual_working_dps: int | None = None
    blocker: str | None = None

    def __post_init__(self) -> None:
        if self.status not in {"AVAILABLE", "OPEN"}:
            raise RadialPilotContractError("backend status must be AVAILABLE or OPEN")
        if not self.backend_id or not self.algorithm:
            raise RadialPilotContractError("backend identity must be explicit")
        if not self.implementation_version or not self.call_graph_isolation:
            raise RadialPilotContractError("backend provenance must be explicit")
        for name in ("source_sha256", "dependency_sha256", "input_sha256"):
            identities = dict(getattr(self, name))
            if self.status == "AVAILABLE" and not identities:
                raise RadialPilotContractError(
                    f"available backend requires non-empty {name}"
                )
            if any(
                not key or len(value) != 64
                for key, value in identities.items()
            ):
                raise RadialPilotContractError(f"{name} must contain SHA-256 identities")
        if self.status == "AVAILABLE":
            if self.actual_backend is None or self.blocker is not None:
                raise RadialPilotContractError(
                    "available backend requires actual_backend and no blocker"
                )
            if self.actual_precision_bits is None and self.actual_working_dps is None:
                raise RadialPilotContractError(
                    "available backend must state its actual precision"
                )
        elif not self.blocker or self.actual_backend is not None:
            raise RadialPilotContractError(
                "OPEN backend requires an exact blocker and no claimed backend"
            )

    def to_metadata(self) -> dict[str, object]:
        result = {"schema_version": BACKEND_SCHEMA, **asdict(self)}
        result["source_sha256"] = dict(self.source_sha256)
        result["dependency_sha256"] = dict(self.dependency_sha256)
        result["input_sha256"] = dict(self.input_sha256)
        result["shared_components"] = list(self.shared_components)
        return result


def selected_pilot_modes() -> tuple[SelectedMode, ...]:
    """Return the fixed, bounded development-pilot mode set."""

    return (
        SelectedMode(
            "absorptive_odd_k0p5_l2",
            "low_ell_absorptive_anchor",
            Sector.ODD,
            2,
            0.5,
        ),
        SelectedMode(
            "absorptive_even_k0p5_l2",
            "low_ell_absorptive_anchor",
            Sector.EVEN,
            2,
            0.5,
        ),
        SelectedMode(
            "ordinary_odd_k1_l20", "ordinary_oscillatory", Sector.ODD, 20, 1.0
        ),
        SelectedMode(
            "ordinary_even_k1_l20", "ordinary_oscillatory", Sector.EVEN, 20, 1.0
        ),
        SelectedMode(
            "turning_odd_k2_l120_r60",
            "near_turning_ell_equals_k_r_eval",
            Sector.ODD,
            120,
            2.0,
            r_eval=60.0,
        ),
        SelectedMode(
            "turning_even_k2_l120_r60",
            "near_turning_ell_equals_k_r_eval",
            Sector.EVEN,
            120,
            2.0,
            r_eval=60.0,
        ),
        SelectedMode(
            "q018_odd_k2_l153_r60",
            "q018_high_barrier_anchor",
            Sector.ODD,
            153,
            2.0,
            r_eval=60.0,
            q018_oracle="q018_riccati",
        ),
    )


def backend_capabilities(
    *,
    mpmath_version: str,
    provenance: Mapping[str, Mapping[str, str]],
) -> tuple[BackendCapability, ...]:
    """Return truthful backend capabilities for this bounded slice."""

    return (
        BackendCapability(
            backend_id="scipy_float64_radial_ode",
            algorithm="project RW/Zerilli solve_ivp/solve_bvp/bidirectional/Q018 path",
            status="AVAILABLE",
            genuinely_independent=False,
            implementation_version="SchWO working-tree Phase-6 selected pilot",
            source_sha256=provenance["scipy_source"],
            dependency_sha256=provenance["scipy_dependencies"],
            input_sha256=provenance["common_inputs"],
            shared_components=(
                "project radial_solver",
                "project Jost outer basis",
                "project outer matching",
            ),
            call_graph_isolation=(
                "primary implementation; repeat solves through this graph count only "
                "as internal stability"
            ),
            actual_backend="SciPy float64",
            actual_precision_bits=53,
        ),
        BackendCapability(
            backend_id="local_mpmath_mst",
            algorithm="independent local MST recurrence for the asymptotic S matrix",
            status="AVAILABLE",
            genuinely_independent=True,
            implementation_version=f"SchWO MST recurrence + mpmath {mpmath_version}",
            source_sha256=provenance["mst_source"],
            dependency_sha256=provenance["mpmath_dependencies"],
            input_sha256=provenance["common_inputs"],
            shared_components=(),
            call_graph_isolation=(
                "MST recurrence does not call solve_radial_mode, SciPy ODE, project "
                "Jost evaluation, or project outer matching"
            ),
            actual_backend=f"mpmath {mpmath_version}",
            actual_working_dps=70,
        ),
        BackendCapability(
            backend_id="bhpt_reggewheeler_mst",
            algorithm="external BlackHolePerturbationToolkit ReggeWheeler MST",
            status="AVAILABLE",
            genuinely_independent=True,
            implementation_version="frozen BHPT ReggeWheeler external evidence v4",
            source_sha256=provenance["bhpt_source"],
            dependency_sha256=provenance["bhpt_dependencies"],
            input_sha256=provenance["bhpt_inputs"],
            shared_components=(),
            call_graph_isolation=(
                "external WolframKernel/BHPT computation; no project radial solver, "
                "Jost, or matching call"
            ),
            actual_backend="WolframKernel + BHPT ReggeWheeler MST frozen Phase-5 evidence",
            actual_working_dps=80,
        ),
        BackendCapability(
            backend_id="bhpt_direct_integration",
            algorithm="external BHPT ReggeWheeler direct numerical integration",
            status="OPEN",
            genuinely_independent=True,
            implementation_version="not implemented",
            source_sha256={},
            dependency_sha256={},
            input_sha256=provenance["common_inputs"],
            shared_components=(),
            call_graph_isolation="no callable backend; fail-closed capability only",
            blocker=(
                "No locally callable, source-bound BHPT direct-integration launcher/API "
                "is present; the available frozen BHPT evidence explicitly uses MST."
            ),
        ),
        BackendCapability(
            backend_id="independent_arbitrary_precision_ode",
            algorithm="independent arbitrary-precision RW/Zerilli ODE S-matrix solve",
            status="OPEN",
            genuinely_independent=True,
            implementation_version="not promoted from finite-radius Fig.2 helper",
            source_sha256=provenance["mpmath_ode_candidate_source"],
            dependency_sha256=provenance["mpmath_dependencies"],
            input_sha256=provenance["common_inputs"],
            shared_components=("RW/Zerilli equations only",),
            call_graph_isolation="no callable Phase-6 S-matrix backend; fail closed",
            blocker=(
                "The existing mpmath helper is a finite-radius Fig.2 spot-check, not a "
                "reusable audited Phase-6 S-matrix backend; adapting and validating it "
                "is outside this bounded selected-mode slice."
            ),
        ),
    )


def complex_metadata(value: complex) -> dict[str, float]:
    result = complex(value)
    if not _finite_complex(result):
        raise RadialPilotContractError("complex evidence value must be finite")
    return {"real": result.real, "imag": result.imag}


def complex_from_metadata(value: object, *, label: str) -> complex:
    if not isinstance(value, Mapping) or set(value) != {"real", "imag"}:
        raise RadialPilotContractError(f"{label} must contain exactly real and imag")
    try:
        result = complex(float(value["real"]), float(value["imag"]))
    except (TypeError, ValueError) as exc:
        raise RadialPilotContractError(f"{label} is not numeric") from exc
    if not _finite_complex(result):
        raise RadialPilotContractError(f"{label} must be finite")
    return result


def _finite_complex(value: complex) -> bool:
    return math.isfinite(value.real) and math.isfinite(value.imag)


def baseline_boundary(mode: SelectedMode) -> BoundaryConfig:
    return BoundaryConfig(
        r_in_eps=1.0e-6,
        r_out=300.0,
        rtol=1.0e-10,
        atol=1.0e-12,
        outer_basis="jost_1_over_r",
        outer_series_order=160,
        required_eval_radius=mode.r_eval if mode.q018_oracle else None,
        experimental_required_radius_oracle=mode.q018_oracle,
    )


def _config_metadata(config: BoundaryConfig) -> dict[str, object]:
    return {
        "r_in_eps": config.r_in_eps,
        "r_out_M": config.r_out,
        "rtol": config.rtol,
        "atol": config.atol,
        "method": config.method,
        "outer_basis": config.outer_basis,
        "jost_order": config.outer_series_order,
        "required_eval_radius_M": config.required_eval_radius,
        "experimental_required_radius_oracle": (
            config.experimental_required_radius_oracle
        ),
    }


def _solution_metadata(solution: RadialSolution) -> dict[str, object]:
    diagnostics = solution.diagnostics
    flux = _signed_flux_metadata(solution)
    phase_reconstructed = -solution.A_out / (((-1) ** solution.ell) * solution.A_in)
    warning_records = [warning.to_metadata() for warning in diagnostics.warnings]
    q018_precision = None
    if warning_records and "actual_precision_bits" in warning_records[0]:
        q018_precision = {
            "actual_precision_bits": int(
                warning_records[0]["actual_precision_bits"]
            ),
            "actual_decimal_digits": float(
                warning_records[0]["actual_decimal_digits"]
            ),
            "requested_precision_dps": int(
                warning_records[0]["requested_precision_dps"]
            ),
            "truth": (
                "SciPy float64; 53 is a binary significand-bit count, and "
                "requested dps is not actual precision"
            ),
        }
    return {
        "A_in": complex_metadata(solution.A_in),
        "A_out": complex_metadata(solution.A_out),
        "phase_factor": complex_metadata(solution.phase_factor),
        "phase_factor_identity_residual": abs(solution.phase_factor - phase_reconstructed),
        "flux": flux,
        "diagnostics": {
            "solver": diagnostics.solver,
            "backend_truth": "SciPy float64",
            "actual_precision_bits": 53,
            "actual_decimal_digits": 15.95,
            "requested_precision_dps": (
                None if q018_precision is None else q018_precision["requested_precision_dps"]
            ),
            "rounding": "IEEE-754 round-to-nearest ties-to-even",
            "guard_digits": 0,
            "boundary_residual": diagnostics.boundary_residual,
            "wronskian_residual": diagnostics.wronskian_residual,
            "raw_wronskian_residual": diagnostics.raw_wronskian_residual,
            "flux_residual": diagnostics.flux_residual,
            "expected_flux_scale": diagnostics.expected_flux_scale,
            "match_condition_number": diagnostics.match_condition_number,
            "barrier_action": diagnostics.barrier_action,
            "ode_n_steps": diagnostics.ode_n_steps,
            "ode_status": diagnostics.ode_status,
            "r_in": diagnostics.r_in,
            "r_out": diagnostics.r_out,
            "outer_basis": diagnostics.outer_basis,
            "outer_series_order": diagnostics.outer_series_order,
            "warnings": warning_records,
            "q018_precision_truth": q018_precision,
        },
    }


def _signed_flux_metadata(solution: RadialSolution) -> dict[str, object]:
    """Return direct signed currents without inferring horizon flux from ``R``."""

    diagnostics = solution.diagnostics
    k = float(solution.k)
    incoming = complex(solution.A_in)
    outgoing = complex(solution.A_out)
    f_grid = solution.background.f(solution.r_grid)
    dpsi_drstar = f_grid * solution.dpsi_dr
    wronskians = (
        np.conjugate(solution.psi) * dpsi_drstar
        - solution.psi * np.conjugate(dpsi_drstar)
    )
    flux_in = -2.0 * k * abs(incoming) ** 2
    flux_out = 2.0 * k * abs(outgoing) ** 2
    incident_scale = 2.0 * k * abs(incoming) ** 2
    horizon_scale = float(diagnostics.expected_flux_scale)
    signed_current_inner = float(0.5 * wronskians[0].imag)
    signed_current_outer = float(0.5 * wronskians[-1].imag)
    direct_current_horizon_flux = 2.0 * signed_current_inner
    horizon_flux_source: str | None = None
    if diagnostics.solver == "q018_required_radius_oracle":
        flux_horizon = None
    elif horizon_scale > 0.0:
        flux_horizon = -horizon_scale
        horizon_flux_source = "diagnostics.expected_flux_scale"
    elif (
        diagnostics.solver == "outward_shooting"
        and math.isfinite(direct_current_horizon_flux)
        and direct_current_horizon_flux < 0.0
    ):
        # The outward solution is normalized by the unchanged solver to a unit
        # ingoing horizon wave.  Its first returned (psi, dpsi/dr) state therefore
        # supplies the horizon current directly, even though the legacy diagnostic
        # field is left at its default zero for this branch.
        flux_horizon = direct_current_horizon_flux
        horizon_flux_source = "direct_inner_current_from_horizon_normalized_solution"
    else:
        flux_horizon = None
    transmission_fraction = (
        0.0 if flux_horizon is None else -flux_horizon / incident_scale
    )
    horizon_flux_resolved = (
        flux_horizon is not None
        and transmission_fraction > math.sqrt(np.finfo(float).eps)
    )
    if not horizon_flux_resolved:
        if diagnostics.solver == "q018_required_radius_oracle":
            blocker = (
                "Q018 required-radius result does not persist an independently resolved "
                "horizon amplitude/flux; expected_flux_scale=0 is not a physical zero."
            )
        elif horizon_scale <= 0.0:
            blocker = (
                "This solver result provides neither a positive persisted horizon "
                "flux scale nor an admissible direct horizon-normalized inner current; "
                "F_H cannot be inferred from 1-|R|^2."
            )
        else:
            blocker = (
                "The recorded horizon-transmission fraction is below sqrt(float64 eps), "
                "so flux balance is not resolved at this arithmetic precision."
            )
        return {
            "status": "NOT_ASSESSED_HORIZON_FLUX_UNRESOLVED_FLOAT64",
            "F_inf_in_signed": flux_in,
            "F_inf_out_signed": flux_out,
            "F_H_signed": None,
            "F_loss_signed": None,
            "absolute_balance_residual": None,
            "relative_balance_residual": None,
            "balance_definition": "(F_inf_in + F_inf_out) - F_H",
            "horizon_flux_inferred_from_one_minus_R": False,
            "horizon_flux_source": horizon_flux_source,
            "internal_accounting_only": True,
            "independently_validated": False,
            "expected_flux_scale_recorded": horizon_scale,
            "recorded_transmission_fraction": transmission_fraction,
            "float64_resolution_floor": math.sqrt(np.finfo(float).eps),
            "signed_wronskian_inner": complex_metadata(complex(wronskians[0])),
            "signed_wronskian_outer": complex_metadata(complex(wronskians[-1])),
            "signed_current_inner": signed_current_inner,
            "signed_current_outer": signed_current_outer,
            "blocker": blocker,
        }
    assert flux_horizon is not None
    absolute = abs((flux_in + flux_out) - flux_horizon)
    relative = absolute / abs(flux_in)
    return {
        "status": "RESOLVED_INTERNAL_ACCOUNTING",
        "F_inf_in_signed": flux_in,
        "F_inf_out_signed": flux_out,
        "F_H_signed": flux_horizon,
        "F_loss_signed": 0.0,
        "absolute_balance_residual": absolute,
        "relative_balance_residual": relative,
        "balance_definition": "(F_inf_in + F_inf_out) - F_H",
        "horizon_flux_inferred_from_one_minus_R": False,
        "horizon_flux_source": horizon_flux_source,
        "internal_accounting_only": True,
        "independently_validated": False,
        "expected_flux_scale_recorded": horizon_scale,
        "recorded_transmission_fraction": transmission_fraction,
        "float64_resolution_floor": math.sqrt(np.finfo(float).eps),
        "reflection_flux_fraction": flux_out / -flux_in,
        "horizon_transmission_flux_fraction": transmission_fraction,
        "signed_wronskian_inner": complex_metadata(complex(wronskians[0])),
        "signed_wronskian_outer": complex_metadata(complex(wronskians[-1])),
        "signed_current_inner": signed_current_inner,
        "signed_current_outer": signed_current_outer,
    }


def _ordinary_ladder_configs(
    mode: SelectedMode,
) -> tuple[tuple[str, str, float | str, BoundaryConfig], ...]:
    base = baseline_boundary(mode)
    records: list[tuple[str, str, float | str, BoundaryConfig]] = [
        ("baseline", "baseline", "baseline", base)
    ]
    for value in (3.0e-6, 3.0e-7):
        records.append(
            (
                f"r_in_eps_{value:.0e}",
                "r_in_eps",
                value,
                BoundaryConfig(**{**asdict(base), "r_in_eps": value}),
            )
        )
    for value in (600.0, 1200.0):
        records.append(
            (
                f"r_out_{int(value)}",
                "r_out",
                value,
                BoundaryConfig(**{**asdict(base), "r_out": value}),
            )
        )
    for value in (80, 120):
        records.append(
            (
                f"jost_order_{value}",
                "jost_order",
                value,
                BoundaryConfig(**{**asdict(base), "outer_series_order": value}),
            )
        )
    for label, rtol, atol in (
        ("loose", 1.0e-9, 1.0e-11),
        ("tight", 3.0e-11, 3.0e-13),
    ):
        records.append(
            (
                f"ode_tolerance_{label}",
                "ode_tolerance",
                f"rtol={rtol:.0e},atol={atol:.0e}",
                BoundaryConfig(**{**asdict(base), "rtol": rtol, "atol": atol}),
            )
        )
    return tuple(records)


def run_mode_ladder(
    mode: SelectedMode,
    *,
    solver: Callable[..., RadialSolution] = solve_radial_mode,
) -> dict[str, object]:
    """Run a one-factor-at-a-time float64 ladder for one selected mode."""

    background = SchwarzschildBackground(M=1.0)
    if mode.q018_oracle:
        configs = (("baseline", "baseline", "baseline", baseline_boundary(mode)),)
    else:
        configs = _ordinary_ladder_configs(mode)
    runs: list[dict[str, object]] = []
    for run_id, axis, value, config in configs:
        try:
            solution = solver(mode.sector, mode.ell, mode.kM, background, config)
        except Exception as exc:
            runs.append(
                {
                    "run_id": run_id,
                    "axis": axis,
                    "axis_value": value,
                    "config": _config_metadata(config),
                    "status": "FAIL",
                    "failure_reason": f"{type(exc).__name__}: {exc}",
                    "result": None,
                }
            )
            continue
        runs.append(
            {
                "run_id": run_id,
                "axis": axis,
                "axis_value": value,
                "config": _config_metadata(config),
                "status": "PASS",
                "failure_reason": None,
                "result": _solution_metadata(solution),
            }
        )
    if runs[0]["status"] != "PASS":
        raise RadialPilotContractError(
            f"baseline failed for {mode.mode_id}: {runs[0]['failure_reason']}"
        )
    baseline = complex_from_metadata(
        runs[0]["result"]["phase_factor"],  # type: ignore[index]
        label="baseline.phase_factor",
    )
    axis_uncertainty = _ladder_bookkeeping(runs, baseline, q018=bool(mode.q018_oracle))
    baseline_result = runs[0]["result"]
    diagnostic = baseline_result["diagnostics"]  # type: ignore[index]
    flux = baseline_result["flux"]  # type: ignore[index]
    flux_resolved = flux["status"] == "RESOLVED_INTERNAL_ACCOUNTING"
    internal_diagnostics_pass = (
        float(diagnostic["boundary_residual"]) <= 1.0e-8
        and float(diagnostic["wronskian_residual"]) <= 1.0e-7
        and float(diagnostic["flux_residual"]) <= 1.0e-7
    )
    physical_flux_pass = bool(
        flux_resolved and float(flux["relative_balance_residual"]) <= 1.0e-7
    )
    measured = [
        float(record["max_abs_phase_factor_delta"])
        for record in axis_uncertainty.values()
        if record["max_abs_phase_factor_delta"] is not None
    ]
    return {
        "schema_version": MODE_SCHEMA,
        "mode": mode.to_metadata(),
        "layers": {
            "internal_flux_wronskian": {
                "diagnostic_status": "PASS" if internal_diagnostics_pass else "FAIL",
                "physical_flux_status": (
                    "PASS_INTERNAL_ACCOUNTING_ONLY"
                    if physical_flux_pass
                    else (
                        str(flux["status"])
                        if not flux_resolved
                        else "FAIL"
                    )
                ),
                "diagnostic_gate": (
                    "boundary <= 1e-8 and resolved effective Wronskian <= 1e-7 "
                    "are diagnostics; this pilot uses <=1e-7 fail-closed envelope"
                ),
            },
            "numerical_ladder": {
                "status": (
                    "MEASURED_SELECTED_LADDER" if measured else "INCOMPLETE_Q018"
                ),
                "uncertainty_metric": "absolute complex phase-factor delta",
                "axes": axis_uncertainty,
                "selected_mode_max_numerical_delta": max(measured, default=None),
                "conservative_measured_max": max(measured, default=None),
                "full_phase6_ladder_complete": all(
                    bool(record["closure_permitted"])
                    for record in axis_uncertainty.values()
                ),
            },
            "external_algorithm": {"status": "PENDING_ATTACHMENT"},
            "convention_normalization": {
                "status": "YELLOW",
                "normalization_identity_checked": True,
                "phase_origin_uncertainty": "OPEN; no fitted global phase allowed",
                "numerical_and_convention_uncertainty_separate": True,
            },
        },
        "baseline": baseline_result,
        "ladder_runs": runs,
    }


def _ladder_bookkeeping(
    runs: Sequence[Mapping[str, object]],
    baseline: complex,
    *,
    q018: bool,
) -> dict[str, dict[str, object]]:
    declared: dict[str, tuple[object, ...]] = {
        "r_in_eps": (1e-4, 3e-5, 1e-5, 3e-6, 1e-6, 3e-7),
        "r_out": (300.0, 600.0, 1200.0, 1800.0, 2400.0),
        "jost_order": (40, 80, 120, 160, 200),
        "ode_tolerance": (
            "rtol=1e-09,atol=1e-11",
            "rtol=1e-10,atol=1e-12",
            "rtol=3e-11,atol=3e-13",
        ),
    }
    baseline_values: dict[str, object] = {
        "r_in_eps": 1e-6,
        "r_out": 300.0,
        "jost_order": 160,
        "ode_tolerance": "rtol=1e-10,atol=1e-12",
    }
    output: dict[str, dict[str, object]] = {}
    baseline_run = runs[0]
    for axis, full_nodes in declared.items():
        axis_runs = [baseline_run] + [record for record in runs if record["axis"] == axis]
        value_to_run = {baseline_values[axis]: baseline_run}
        value_to_run.update({record["axis_value"]: record for record in axis_runs[1:]})
        ordered_runs = [value_to_run[node] for node in full_nodes if node in value_to_run]
        missing = [node for node in full_nodes if node not in value_to_run]
        failed = [
            {
                "node": record["axis_value"],
                "failure_reason": record["failure_reason"],
            }
            for record in ordered_runs
            if record["status"] != "PASS"
        ]
        successful = [record for record in ordered_runs if record["status"] == "PASS"]
        phase_values = [
            complex_from_metadata(
                record["result"]["phase_factor"],  # type: ignore[index]
                label=f"{record['run_id']}.phase_factor",
            )
            for record in successful
        ]
        successive = [
            abs(right - left) for left, right in zip(phase_values, phase_values[1:])
        ]
        baseline_deltas = [abs(value - baseline) for value in phase_values]
        nonmonotonic = any(
            later > earlier
            for earlier, later in zip(successive, successive[1:])
        )
        final_pair = None
        if len(successful) >= 2:
            final_pair = {
                "nodes": [successful[-2]["axis_value"], successful[-1]["axis_value"]],
                "phase_factors": [
                    successful[-2]["result"]["phase_factor"],  # type: ignore[index]
                    successful[-1]["result"]["phase_factor"],  # type: ignore[index]
                ],
                "absolute_difference": successive[-1],
            }
        closure = not missing and not failed and len(successful) == len(full_nodes)
        reason = None
        if q018:
            reason = "Q018 anchor variations are outside its reviewed literal envelope"
        elif missing:
            reason = "bounded pilot intentionally omitted full-domain ladder nodes"
        elif failed:
            reason = "one or more selected ladder nodes failed"
        output[axis] = {
            "status": (
                "MEASURED_SELECTED_LADDER"
                if len(successful) >= 2
                else ("BASELINE_ONLY" if successful else "NOT_MEASURED")
            ),
            "declared_nodes": list(full_nodes),
            "run_nodes": [record["axis_value"] for record in ordered_runs],
            "missing_nodes": missing,
            "failed_nodes": failed,
            "missing_flag": bool(missing),
            "nonmonotonic_flag": nonmonotonic,
            "final_pair": final_pair,
            "extrapolation_model": "none; raw selected ladder only",
            "remainder_estimate": None if not successive else successive[-1],
            "max_abs_phase_factor_delta": (
                None if len(baseline_deltas) < 2 else max(baseline_deltas)
            ),
            "closure_permitted": closure,
            "closure_blocker": reason,
        }
    return output


def attach_external_comparisons(
    mode_record: dict[str, object],
    *,
    bhpt_record: Mapping[str, object] | None,
    mst_odd: complex | None,
    mst_even: complex | None,
    mst_recurrence_residual: float | None,
    mst_blocker: str | None = None,
) -> None:
    """Attach comparison records without phase or normalization fitting."""

    mode = mode_record["mode"]
    sector = str(mode["sector"])  # type: ignore[index]
    regime = str(mode["regime"])  # type: ignore[index]
    baseline = complex_from_metadata(
        mode_record["baseline"]["phase_factor"],  # type: ignore[index]
        label="baseline.phase_factor",
    )
    if mst_odd is None or mst_even is None or mst_recurrence_residual is None:
        if not mst_blocker or any(
            value is not None for value in (mst_odd, mst_even, mst_recurrence_residual)
        ):
            raise RadialPilotContractError("incomplete MST comparison or blocker")
        comparisons: list[dict[str, object]] = [
            {
                "backend": "local_mpmath_mst",
                "status": "OPEN_FOR_SELECTED_KEY",
                "actual_backend": None,
                "strict_no_phase_or_normalization_fit": True,
                "value": None,
                "absolute_complex_difference": None,
                "recurrence_residual": None,
                "genuinely_independent_for_this_sector": False,
                "even_independent_solve": False if sector == "even" else None,
                "blocker": mst_blocker,
            }
        ]
    else:
        if mst_blocker is not None:
            raise RadialPilotContractError("successful MST comparison cannot have blocker")
        mst_value = mst_odd if sector == "odd" else mst_even
        comparisons = [{
            "backend": "local_mpmath_mst",
            "status": "AVAILABLE_FOR_SELECTED_KEY",
            "actual_backend": "mpmath",
            "actual_working_dps": 70,
            "strict_no_phase_or_normalization_fit": True,
            "value": complex_metadata(mst_value),
            "absolute_complex_difference": abs(baseline - mst_value),
            "recurrence_residual": float(mst_recurrence_residual),
            "genuinely_independent_for_this_sector": sector == "odd",
            "even_independent_solve": False if sector == "even" else None,
            "even_sector_note": (
                None
                if sector == "odd"
                else "even MST value is parity-derived, not an independent even solve"
            ),
        }]
    if bhpt_record is not None:
        key = "odd" if sector == "odd" else "even_from_chandrasekhar"
        value = complex_from_metadata(bhpt_record[key], label=f"BHPT.{key}")
        comparisons.append(
            {
                "backend": "bhpt_reggewheeler_mst_frozen_external_evidence",
                "method": "MST",
                "strict_no_phase_or_normalization_fit": True,
                "value": complex_metadata(value),
                "absolute_complex_difference": abs(baseline - value),
                "genuinely_independent_for_this_sector": sector == "odd",
                "even_independent_solve": False if sector == "even" else None,
                "even_sector_note": (
                    None
                    if sector == "odd"
                    else "BHPT even value is exact-parity-derived and non-independent"
                ),
            }
        )
    independent_differences = [
        float(record["absolute_complex_difference"])
        for record in comparisons
        if record["genuinely_independent_for_this_sector"] is True
    ]
    if mst_blocker is not None:
        comparison_status = "EXTERNAL_BACKEND_UNAVAILABLE_FOR_SELECTED_KEY"
    elif not independent_differences:
        comparison_status = "NO_INDEPENDENT_EVEN_SOLVE"
    elif regime == "ordinary_oscillatory":
        comparison_status = (
            "DIAGNOSTIC_PASS"
            if max(independent_differences) <= 1.0e-9
            else "DIAGNOSTIC_FAIL"
        )
    else:
        comparison_status = "UNCALIBRATED_DENSE_REGIME_DIFFERENCE_RECORDED"
    mode_record["layers"]["external_algorithm"] = {  # type: ignore[index]
        "status": "PARTIAL",
        "ordinary_mst_diagnostic_tolerance": 1.0e-9,
        "diagnostic_comparison_status": comparison_status,
        "comparisons": comparisons,
        "bhpt_direct_integration": "OPEN",
        "independent_arbitrary_precision_ode": "OPEN",
        "even_independent_solve": False if sector == "even" else None,
    }
    ladder = mode_record["layers"]["numerical_ladder"]  # type: ignore[index]
    ladder_components = {
        name: record["max_abs_phase_factor_delta"]
        for name, record in ladder["axes"].items()
    }
    measured_values = [
        float(value) for value in ladder_components.values() if value is not None
    ] + independent_differences
    unresolved = []
    if not ladder["full_phase6_ladder_complete"]:
        unresolved.append("full declared r_in/r_out/Jost/tolerance ladders")
    unresolved.extend(
        ["independent arbitrary-precision ODE", "BHPT direct integration"]
    )
    if sector == "even":
        unresolved.append("independent even-sector external radial solve")
    mode_record["numerical_uncertainty"] = {
        "metric": "absolute complex phase-factor difference",
        "components": {
            **ladder_components,
            "arithmetic_precision": None,
            "backend_difference": (
                max(independent_differences) if independent_differences else None
            ),
        },
        "conservative_max_over_measured_components": max(
            measured_values, default=None
        ),
        "closed": False,
        "unresolved": unresolved,
    }
    mode_record["convention_uncertainty"] = {
        "separate_from_numerical": True,
        "normalization_identity_residual": mode_record["baseline"][
            "phase_factor_identity_residual"
        ],  # type: ignore[index]
        "phase_origin": "OPEN; no fitted phase/normalization",
        "amplitude_normalization": "A_in/A_out convention checked algebraically",
        "closed": False,
    }


def validate_pilot_evidence(payload: Mapping[str, Any]) -> None:
    """Fail closed on malformed or globally overstated pilot evidence."""

    required = {
        "schema_version",
        "scope",
        "overall_status",
        "global_green_permitted",
        "pilot_domain",
        "backend_capabilities",
        "modes",
        "source_identities",
        "limitations",
    }
    if set(payload) != required:
        raise RadialPilotContractError("pilot evidence top-level schema mismatch")
    if payload["schema_version"] != PILOT_SCHEMA:
        raise RadialPilotContractError("unexpected pilot schema")
    if payload["scope"] != "selected_mode_development_pilot":
        raise RadialPilotContractError("pilot scope changed")
    if payload["global_green_permitted"] is not False:
        raise RadialPilotContractError("Phase 6 forbids global GREEN")
    if payload["overall_status"] == "GREEN":
        raise RadialPilotContractError("selected pilot cannot claim V1 GREEN")
    domain = payload["pilot_domain"]
    if not isinstance(domain, Mapping):
        raise RadialPilotContractError("pilot domain inventory is missing")
    if domain.get("covered_key_count") != len(selected_pilot_modes()):
        raise RadialPilotContractError("covered key inventory mismatch")
    if domain.get("production_deduplicated_key_count") != 16048:
        raise RadialPilotContractError("declared production-domain inventory drift")
    if domain.get("production_missing_key_count") != 16048 - len(
        selected_pilot_modes()
    ):
        raise RadialPilotContractError("missing production-key inventory mismatch")
    if domain.get("full_v1_domain_complete") is not False:
        raise RadialPilotContractError("selected pilot cannot close the full V1 domain")
    modes = payload["modes"]
    if not isinstance(modes, list) or len(modes) != len(selected_pilot_modes()):
        raise RadialPilotContractError("selected pilot mode count mismatch")
    expected_ids = [mode.mode_id for mode in selected_pilot_modes()]
    observed_ids = [record.get("mode", {}).get("mode_id") for record in modes]
    if observed_ids != expected_ids or len(set(observed_ids)) != len(observed_ids):
        raise RadialPilotContractError("selected pilot mode order/identity mismatch")
    for record in modes:
        if record.get("schema_version") != MODE_SCHEMA:
            raise RadialPilotContractError("mode evidence schema mismatch")
        layers = record.get("layers")
        if not isinstance(layers, Mapping) or set(layers) != {
            "internal_flux_wronskian",
            "numerical_ladder",
            "external_algorithm",
            "convention_normalization",
        }:
            raise RadialPilotContractError("verification layers are not separate")
        baseline = record.get("baseline")
        if not isinstance(baseline, Mapping):
            raise RadialPilotContractError("mode baseline is missing")
        incoming = complex_from_metadata(baseline.get("A_in"), label="A_in")
        outgoing = complex_from_metadata(baseline.get("A_out"), label="A_out")
        phase = complex_from_metadata(baseline.get("phase_factor"), label="phase_factor")
        ell = int(record["mode"]["ell"])
        if abs(phase + outgoing / (((-1) ** ell) * incoming)) > 5.0e-12:
            raise RadialPilotContractError("phase-factor convention identity failed")
        diagnostics = baseline.get("diagnostics")
        if not isinstance(diagnostics, Mapping):
            raise RadialPilotContractError("mode diagnostics are missing")
        if diagnostics.get("backend_truth") != "SciPy float64":
            raise RadialPilotContractError("float64 backend truth changed")
        if diagnostics.get("actual_precision_bits") != 53:
            raise RadialPilotContractError("SciPy precision must be recorded as 53 bits")
        if diagnostics.get("actual_decimal_digits") != 15.95:
            raise RadialPilotContractError("float64 decimal precision truth changed")
        is_q018 = "experimental_required_radius_oracle" in record["mode"]
        q018_precision = diagnostics.get("q018_precision_truth")
        if is_q018 and not isinstance(q018_precision, Mapping):
            raise RadialPilotContractError("Q018 precision truth is missing")
        if q018_precision is not None:
            if not isinstance(q018_precision, Mapping):
                raise RadialPilotContractError("Q018 precision truth is malformed")
            if "actual_precision_dps" in q018_precision:
                raise RadialPilotContractError(
                    "Q018 binary precision may not be labelled as decimal dps"
                )
            if q018_precision.get("actual_precision_bits") != 53:
                raise RadialPilotContractError("Q018 actual precision bits are missing")
            if q018_precision.get("actual_decimal_digits") != 15.95:
                raise RadialPilotContractError(
                    "Q018 actual decimal precision estimate is missing"
                )
        if diagnostics.get("rounding") != "IEEE-754 round-to-nearest ties-to-even":
            raise RadialPilotContractError("rounding metadata is missing")
        flux = baseline.get("flux")
        if not isinstance(flux, Mapping):
            raise RadialPilotContractError("signed flux evidence is missing")
        for name in (
            "F_inf_in_signed",
            "F_inf_out_signed",
            "F_H_signed",
            "F_loss_signed",
            "absolute_balance_residual",
            "relative_balance_residual",
            "signed_wronskian_inner",
            "signed_wronskian_outer",
        ):
            if name not in flux:
                raise RadialPilotContractError(f"signed flux field {name} is missing")
        if flux.get("horizon_flux_inferred_from_one_minus_R") is not False:
            raise RadialPilotContractError("horizon flux may not be inferred from R")
        if flux.get("internal_accounting_only") is not True:
            raise RadialPilotContractError("flux witness must remain internal accounting")
        if flux.get("independently_validated") is not False:
            raise RadialPilotContractError("internal flux cannot claim independence")
        if record["mode"].get("q018_oracle") is not None:
            # Reserved for potential future schema spelling; current key is below.
            raise RadialPilotContractError("unexpected Q018 mode key spelling")
        physical_status = layers["internal_flux_wronskian"].get(
            "physical_flux_status"
        )
        if record["mode"]["regime"] == "low_ell_absorptive_anchor":
            if (
                flux.get("status") != "RESOLVED_INTERNAL_ACCOUNTING"
                or flux.get("F_H_signed") is None
                or flux.get("horizon_flux_source")
                != "direct_inner_current_from_horizon_normalized_solution"
                or physical_status != "PASS_INTERNAL_ACCOUNTING_ONLY"
            ):
                raise RadialPilotContractError(
                    "low-ell absorptive anchor lacks resolved direct-current flux"
                )
        if is_q018:
            if (
                flux.get("F_H_signed") is not None
                or physical_status == "PASS_INTERNAL_ACCOUNTING_ONLY"
            ):
                raise RadialPilotContractError("Q018 may not receive physical-flux PASS")
        elif (
            flux.get("F_H_signed") is None
            and physical_status == "PASS_INTERNAL_ACCOUNTING_ONLY"
        ):
            raise RadialPilotContractError(
                "unresolved ordinary horizon flux may not receive PASS"
            )
        ladder = layers["numerical_ladder"]
        axes = ladder.get("axes") if isinstance(ladder, Mapping) else None
        if not isinstance(axes, Mapping) or set(axes) != {
            "r_in_eps",
            "r_out",
            "jost_order",
            "ode_tolerance",
        }:
            raise RadialPilotContractError("ladder axis inventory mismatch")
        for axis, bookkeeping in axes.items():
            if not isinstance(bookkeeping, Mapping):
                raise RadialPilotContractError(f"{axis} ladder bookkeeping missing")
            for field in (
                "declared_nodes",
                "run_nodes",
                "missing_nodes",
                "failed_nodes",
                "missing_flag",
                "nonmonotonic_flag",
                "final_pair",
                "extrapolation_model",
                "remainder_estimate",
                "closure_permitted",
            ):
                if field not in bookkeeping:
                    raise RadialPilotContractError(f"{axis} ladder field {field} missing")
            if bookkeeping["missing_nodes"] and bookkeeping["closure_permitted"]:
                raise RadialPilotContractError("incomplete ladder cannot close")
        if record.get("numerical_uncertainty", {}).get("closed") is not False:
            raise RadialPilotContractError("pilot numerical uncertainty cannot be closed")
        if record.get("convention_uncertainty", {}).get("closed") is not False:
            raise RadialPilotContractError("pilot convention uncertainty cannot be closed")
        external = layers["external_algorithm"]
        if record["mode"]["sector"] == "even":
            if external.get("even_independent_solve") is not False:
                raise RadialPilotContractError("even parity evidence must be non-independent")
            if any(
                item.get("even_independent_solve") is not False
                for item in external.get("comparisons", [])
            ):
                raise RadialPilotContractError("even comparison independence overstated")
    capabilities = payload["backend_capabilities"]
    if not isinstance(capabilities, list):
        raise RadialPilotContractError("backend capabilities must be a list")
    by_id = {record.get("backend_id"): record for record in capabilities}
    for backend_id, record in by_id.items():
        if not isinstance(record, Mapping):
            raise RadialPilotContractError("backend record is malformed")
        for field in (
            "implementation_version",
            "source_sha256",
            "dependency_sha256",
            "input_sha256",
            "shared_components",
            "call_graph_isolation",
        ):
            if field not in record:
                raise RadialPilotContractError(
                    f"backend {backend_id} provenance field {field} is missing"
                )
    for required_open in ("bhpt_direct_integration", "independent_arbitrary_precision_ode"):
        record = by_id.get(required_open)
        if not isinstance(record, Mapping) or record.get("status") != "OPEN":
            raise RadialPilotContractError(f"{required_open} must fail closed as OPEN")
        if not record.get("blocker"):
            raise RadialPilotContractError(f"{required_open} blocker is missing")


def bhpt_record_for_mode(
    records: Sequence[Mapping[str, object]], mode: SelectedMode
) -> Mapping[str, object] | None:
    matches = [
        record
        for record in records
        if float(record["kM"]) == mode.kM and int(record["ell"]) == mode.ell
    ]
    if not matches:
        return None
    if len(matches) != 1:
        raise RadialPilotContractError("BHPT benchmark key is not unique")
    return matches[0]


def sha256_file(path: str | Path) -> str:
    import hashlib

    target = Path(path)
    digest = hashlib.sha256()
    with target.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


__all__ = [
    "BACKEND_SCHEMA",
    "MODE_SCHEMA",
    "PILOT_SCHEMA",
    "BackendCapability",
    "RadialPilotContractError",
    "SelectedMode",
    "attach_external_comparisons",
    "backend_capabilities",
    "baseline_boundary",
    "bhpt_record_for_mode",
    "complex_from_metadata",
    "complex_metadata",
    "run_mode_ladder",
    "selected_pilot_modes",
    "sha256_file",
    "validate_pilot_evidence",
]
