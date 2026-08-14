"""Selected real measurements for Phase-6 V2--V5 candidate evidence.

This module deliberately produces only ``PARTIAL`` candidate measurements.
It exercises the implemented physics primitives on a small, explicit domain,
including the Li-to-Martel--Poisson normalization bridge, but it does not close
an external absolute-amplitude/Psi4 comparison, production-domain ladders, or
the operational detector and transfer-matrix release gates.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
import hashlib
import json
import math

import numpy as np

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.numerics.conditioned_radial import (
    ConditionedRadialRequest,
    solve_conditioned_radial_at_radius,
)
from schwgw.perturbations import (
    Sector,
    V_RW,
    V_Zerilli,
    lambda_parameter,
    reconstruct_metric_mode,
)
from schwgw.scattering.asymptotic import (
    parity_scattering_series,
    scattering_matrix_cross_section,
)
from schwgw.validation.phase6_asymptotic import (
    li_even_master_from_rw_metric,
    li_master_to_martel_poisson,
    martel_poisson_even_master_from_rw_metric,
    martel_poisson_odd_master_from_rw_metric,
    martel_poisson_strain,
    monochromatic_martel_poisson_flux,
)
from schwgw.validation.phase6_cross_checks import (
    PROJECT_OUTGOING_PSI4_CONVENTION,
    outgoing_strain_to_project_strict_np_psi4,
)
from schwgw.validation.phase6_cross_section import (
    first_spin2_glory_ring,
    geometric_optics_absorption_cross_section,
    spin2_absorption_cross_section,
    spin2_low_frequency_cross_section,
)
from schwgw.validation.phase6_observable_evidence import (
    CONVENTION_BUDGETS,
    NUMERICAL_BUDGETS,
    OBSERVABLE_GATES,
    REQUIRED_CHECKS,
)
from schwgw.validation.phase6_observer_response import (
    check_radial_frame_transport,
    radial_freefall_from_infinity_observer,
    schwarzschild_radial_pure_gauge_oracle,
    static_schwarzschild_observer,
)
from schwgw.validation.phase6_polarization_transfer import (
    AbsolutePhaseConvention,
    linear_to_helicity_transform,
    polarization_basis_rotation,
    polarization_transfer_from_columns,
    rotate_polarization_transfer,
)
from schwgw.validation.phase6_domain import source_file_identity


MEASUREMENT_SCHEMA = "schwgw_phase6_selected_observable_measurements_v1"
CONFIG_SCHEMA = "schwgw_phase6_selected_observable_measurement_config_v1"
MEASUREMENT_STATES = ("NOT_ASSESSED", "PARTIAL")
APPLICABILITY = ("REQUIRED", "NOT_APPLICABLE")
PROJECT_ROOT = Path(__file__).resolve().parents[3]

SOURCE_PATHS = {
    "measurement_runner": PROJECT_ROOT
    / "src/schwgw/validation/phase6_observable_measurements.py",
    "conditioned_radial": PROJECT_ROOT / "src/schwgw/numerics/conditioned_radial.py",
    "metric_reconstruction": PROJECT_ROOT
    / "src/schwgw/perturbations/reconstruction.py",
    "scattering_asymptotic": PROJECT_ROOT / "src/schwgw/scattering/asymptotic.py",
    "martel_poisson": PROJECT_ROOT / "src/schwgw/validation/phase6_asymptotic.py",
    "waveform_cross_checks": PROJECT_ROOT
    / "src/schwgw/validation/phase6_cross_checks.py",
    "cross_section": PROJECT_ROOT / "src/schwgw/validation/phase6_cross_section.py",
    "observer_response": PROJECT_ROOT
    / "src/schwgw/validation/phase6_observer_response.py",
    "metric_curvature": PROJECT_ROOT / "src/schwgw/scattering/metric_curvature.py",
    "polarization_transfer": PROJECT_ROOT
    / "src/schwgw/validation/phase6_polarization_transfer.py",
}

OBSERVABLE_SOURCE_LABELS = {
    "master_to_strain_flux": (
        "measurement_runner",
        "conditioned_radial",
        "metric_reconstruction",
        "martel_poisson",
        "waveform_cross_checks",
    ),
    "metric_psi4_external_crosscheck": (
        "measurement_runner",
        "conditioned_radial",
        "metric_reconstruction",
        "martel_poisson",
        "waveform_cross_checks",
    ),
    "spin2_scattering_limits": (
        "measurement_runner",
        "conditioned_radial",
        "scattering_asymptotic",
        "cross_section",
    ),
    "finite_radius_tidal_detector": (
        "measurement_runner",
        "observer_response",
        "metric_curvature",
    ),
    "complex_lensing_matrix": (
        "measurement_runner",
        "conditioned_radial",
        "scattering_asymptotic",
        "polarization_transfer",
    ),
}


class ObservableMeasurementError(ValueError):
    """Raised when a selected measurement payload is stale or contradictory."""


@dataclass(frozen=True)
class SelectedObservableMeasurementConfig:
    """Bounded V2--V5 measurement domain; never a production-domain request."""

    mass: float = 1.0
    required_radius: float = 20.0
    r_out: float = 160.0
    r_in_eps: float = 1.0e-6
    rtol: float = 1.0e-9
    atol: float = 1.0e-11
    outer_series_order: int = 80
    low_kM: float = 0.1
    low_lmax: int = 8
    high_kM: float = 2.0
    high_lmax: int = 14
    glory_kM: float = 4.0
    glory_lmax: int = 14
    reduction_orders: tuple[int, ...] = (0, 1, 2)
    observer_radius: float = 12.0
    observer_theta: float = 0.9
    gauge_vector_radial: float = 0.17
    transfer_incident_rotation: float = 0.23
    transfer_observer_rotation: float = -0.41

    def __post_init__(self) -> None:
        for name in (
            "mass",
            "required_radius",
            "r_out",
            "r_in_eps",
            "rtol",
            "atol",
            "low_kM",
            "high_kM",
            "glory_kM",
            "observer_radius",
            "gauge_vector_radial",
        ):
            value = float(getattr(self, name))
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")
            object.__setattr__(self, name, value)
        if (
            self.required_radius <= 2.0 * self.mass
            or self.required_radius >= self.r_out
        ):
            raise ValueError("required_radius must lie outside 2M and below r_out")
        if self.mass != 1.0:
            raise ValueError("V1 selected measurements freeze M=1")
        if self.observer_radius <= 2.0 * self.mass:
            raise ValueError("observer_radius must lie outside 2M")
        theta = float(self.observer_theta)
        if not math.isfinite(theta) or not 0.0 < theta < math.pi:
            raise ValueError("observer_theta must lie in (0,pi)")
        object.__setattr__(self, "observer_theta", theta)
        for name in ("transfer_incident_rotation", "transfer_observer_rotation"):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)
        for name in ("low_lmax", "high_lmax", "glory_lmax", "outer_series_order"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
        if self.low_lmax < 3 or self.high_lmax < 5 or self.glory_lmax < 5:
            raise ValueError(
                "selected lmax values are too small for the frozen diagnostics"
            )
        if not self.low_kM < self.high_kM < self.glory_kM:
            raise ValueError(
                "selected frequencies must satisfy low_kM < high_kM < glory_kM"
            )
        if not isinstance(
            self.reduction_orders, tuple
        ) or self.reduction_orders != tuple(sorted(set(self.reduction_orders))):
            raise ValueError("reduction_orders must be an ordered unique tuple")
        if self.reduction_orders != (0, 1, 2):
            raise ValueError("V1 candidate freezes reduction_orders=(0,1,2)")
        if self.glory_lmax - max(self.reduction_orders) < 2:
            raise ValueError("glory_lmax does not supply the reduction upper edge")

    def to_record(self) -> dict[str, object]:
        record = asdict(self)
        record["reduction_orders"] = list(self.reduction_orders)
        return {"schema": CONFIG_SCHEMA, **record}


def run_selected_observable_measurements(
    config: SelectedObservableMeasurementConfig = SelectedObservableMeasurementConfig(),
) -> dict[str, object]:
    """Run the bounded measurements and return a strict candidate payload."""

    if not isinstance(config, SelectedObservableMeasurementConfig):
        raise TypeError("config must be SelectedObservableMeasurementConfig")
    started = perf_counter()
    live_sources = {
        label: source_file_identity(path) for label, path in SOURCE_PATHS.items()
    }
    v2_common = _measure_v2(config)
    v3, radial_cache = _measure_v3(config)
    v4 = _measure_v4(config)
    v5 = _measure_v5(config, radial_cache)
    observables = {
        "master_to_strain_flux": _v2_master_section(config, live_sources, v2_common),
        "metric_psi4_external_crosscheck": _v2_crosscheck_section(
            config, live_sources, v2_common
        ),
        "spin2_scattering_limits": _v3_section(config, live_sources, v3),
        "finite_radius_tidal_detector": _v4_section(config, live_sources, v4),
        "complex_lensing_matrix": _v5_section(config, live_sources, v5),
    }
    payload = {
        "schema": MEASUREMENT_SCHEMA,
        "scientific_evidence": True,
        "kernel_unit_test_only": False,
        "contract_only": False,
        "global_green_permitted": False,
        "paper_agreement_primary_gate": False,
        "candidate_release_only": True,
        "overall_state": "PARTIAL",
        "config": config.to_record(),
        "runtime_seconds": float(perf_counter() - started),
        "observables": observables,
    }
    validate_measurement_payload(payload)
    return payload


def validate_measurement_payload(
    value: object,
    *,
    verify_live_sources: bool = True,
) -> Mapping[str, object]:
    fields = {
        "schema",
        "scientific_evidence",
        "kernel_unit_test_only",
        "contract_only",
        "global_green_permitted",
        "paper_agreement_primary_gate",
        "candidate_release_only",
        "overall_state",
        "config",
        "runtime_seconds",
        "observables",
    }
    item = _exact(value, fields, "measurement payload")
    if (
        item["schema"] != MEASUREMENT_SCHEMA
        or item["scientific_evidence"] is not True
        or item["kernel_unit_test_only"] is not False
        or item["contract_only"] is not False
        or item["global_green_permitted"] is not False
        or item["paper_agreement_primary_gate"] is not False
        or item["candidate_release_only"] is not True
        or item["overall_state"] != "PARTIAL"
    ):
        raise ObservableMeasurementError("measurement claim policy changed")
    _validate_config_record(item["config"])
    _nonnegative_finite(item["runtime_seconds"], "measurement runtime")
    observables = item["observables"]
    if not isinstance(observables, Mapping) or set(observables) != set(
        OBSERVABLE_GATES
    ):
        raise ObservableMeasurementError("measurement observable inventory changed")
    for observable, section in observables.items():
        _validate_section(
            section,
            observable=str(observable),
            verify_live_sources=verify_live_sources,
        )
    return item


def _measure_v2(config: SelectedObservableMeasurementConfig) -> dict[str, object]:
    background = SchwarzschildBackground(M=config.mass)
    k = 0.5
    ell = 2
    results = {
        sector: solve_conditioned_radial_at_radius(
            ConditionedRadialRequest(
                sector=sector,
                ell=ell,
                k=k,
                required_radius=config.required_radius,
                r_out=config.r_out,
                r_in_eps=config.r_in_eps,
                rtol=config.rtol,
                atol=config.atol,
                outer_series_order=config.outer_series_order,
            ),
            background,
        )
        for sector in (Sector.EVEN, Sector.ODD)
    }
    outgoing_bridge = li_master_to_martel_poisson(
        ell=2,
        m=2,
        k=k,
        psi_li_even=results[Sector.EVEN].A_out,
        psi_li_odd=results[Sector.ODD].A_out,
    )
    horizon_bridge = li_master_to_martel_poisson(
        ell=2,
        m=2,
        k=k,
        psi_li_even=results[Sector.EVEN].T_horizon,
        psi_li_odd=results[Sector.ODD].T_horizon,
    )
    finite_bridge = li_master_to_martel_poisson(
        ell=2,
        m=2,
        k=k,
        psi_li_even=results[Sector.EVEN].psi,
        psi_li_odd=results[Sector.ODD].psi,
    )
    infinity = martel_poisson_strain(
        [outgoing_bridge.mode],
        areal_scale=100.0,
        theta=1.1,
        phi=0.3,
        boundary="future_null_infinity",
    )
    horizon = martel_poisson_strain(
        [horizon_bridge.mode],
        areal_scale=2.0 * config.mass,
        theta=1.1,
        phi=0.3,
        boundary="event_horizon",
        mass=config.mass,
    )
    infinity_flux = monochromatic_martel_poisson_flux(
        [outgoing_bridge.mode],
        k=k,
        boundary="future_null_infinity",
        amplitude_convention="real_field_peak",
    )
    horizon_flux = monochromatic_martel_poisson_flux(
        [horizon_bridge.mode],
        k=k,
        boundary="event_horizon",
        amplitude_convention="real_field_peak",
    )
    psi4 = outgoing_strain_to_project_strict_np_psi4(
        k=k,
        h_plus=infinity.h_plus,
        h_cross=infinity.h_cross,
    )
    metric_roundtrip = _v2_metric_roundtrip(
        background=background,
        ell=ell,
        k=k,
        radius=config.required_radius,
        results=results,
        finite_bridge=finite_bridge,
    )
    radial_flux_residual = max(
        float(result.diagnostics["flux_residual"]) for result in results.values()
    )
    return {
        "kM": k * config.mass,
        "input_master_normalization": "historical Li RW/Zerilli project masters",
        "project_master_normalization_bridge": "IMPLEMENTED_EXPLICIT_LI_TO_MP",
        "project_master_values_used": True,
        "bridge": {
            "even_formula": outgoing_bridge.even_formula,
            "odd_formula": outgoing_bridge.odd_formula,
            "angular_sign": outgoing_bridge.angular_sign,
            "assumptions": outgoing_bridge.assumptions,
            "source": outgoing_bridge.source,
        },
        "outgoing_mode": {
            "ell": ell,
            "m": 2,
            "psi_li_even": _complex_pair(outgoing_bridge.li_psi_even),
            "psi_li_odd": _complex_pair(outgoing_bridge.li_psi_odd),
            "psi_mp_even": _complex_pair(outgoing_bridge.mode.psi_even),
            "psi_mp_odd": _complex_pair(outgoing_bridge.mode.psi_odd),
        },
        "horizon_mode": {
            "ell": ell,
            "m": 2,
            "psi_li_even": _complex_pair(horizon_bridge.li_psi_even),
            "psi_li_odd": _complex_pair(horizon_bridge.li_psi_odd),
            "psi_mp_even": _complex_pair(horizon_bridge.mode.psi_even),
            "psi_mp_odd": _complex_pair(horizon_bridge.mode.psi_odd),
        },
        "infinity_strain": {
            "h_plus": _complex_pair(infinity.h_plus),
            "h_cross": _complex_pair(infinity.h_cross),
            "areal_scale": infinity.areal_scale,
        },
        "horizon_strain": {
            "h_plus": _complex_pair(horizon.h_plus),
            "h_cross": _complex_pair(horizon.h_cross),
            "areal_scale": horizon.areal_scale,
        },
        "infinity_flux": infinity_flux.value,
        "horizon_flux": horizon_flux.value,
        "psi4_from_infinity_strain": _complex_pair(psi4),
        "psi4_convention": PROJECT_OUTGOING_PSI4_CONVENTION,
        "algebraic_strain_to_psi4_route_evaluated": True,
        "metric_route_evaluated": True,
        "metric_route_scope": "finite_radius_metric_to_master_roundtrip_only",
        "finite_radius_metric_roundtrip": metric_roundtrip,
        "radial_flux_residual": radial_flux_residual,
        "finite_radius_total_field_used_as_infinity_waveform": False,
        "large_radius_metric_psi4_route_evaluated": False,
        "external_bhpt_amplitude_route_evaluated": False,
    }


def _v2_metric_roundtrip(
    *,
    background: SchwarzschildBackground,
    ell: int,
    k: float,
    radius: float,
    results: Mapping[Sector, object],
    finite_bridge: object,
) -> dict[str, object]:
    recovered: dict[str, dict[str, object]] = {}
    residuals: list[float] = []
    for sector in (Sector.EVEN, Sector.ODD):
        result = results[sector]
        psi = complex(result.psi)
        derivative = complex(result.dpsi_dr)
        metric = reconstruct_metric_mode(
            sector,
            ell,
            k,
            radius,
            psi,
            derivative,
            background,
        ).components
        f = float(background.f(radius))
        fp = float(background.df_dr(radius))
        potential = float(
            (V_Zerilli if sector is Sector.EVEN else V_RW)(ell, radius, background)
        )
        second_derivative = -(f * fp * derivative + (k**2 - potential) * psi) / f**2
        if sector is Sector.EVEN:
            direct_li = li_even_master_from_rw_metric(
                ell=ell,
                k=k,
                mass=background.M,
                r=radius,
                T0=metric["T0"],
                Rt=metric["Rt"],
            )
            lambda_ = lambda_parameter(ell)
            mass_over_r = background.M / radius
            capital_lambda = lambda_ + 3.0 * mass_over_r
            numerator = (
                lambda_ * (lambda_ + 1.0)
                + 3.0 * lambda_ * mass_over_r
                + 6.0 * mass_over_r**2
            )
            coefficient = numerator / capital_lambda
            coefficient_du = (
                (3.0 * lambda_ + 12.0 * mass_over_r) * capital_lambda - 3.0 * numerator
            ) / capital_lambda**2
            coefficient_dr = coefficient_du * (-mass_over_r / radius)
            metric_derivative = (
                fp * derivative
                + f * second_derivative
                + coefficient_dr * psi / radius
                + coefficient * derivative / radius
                - coefficient * psi / radius**2
            )
            recovered_mp = martel_poisson_even_master_from_rw_metric(
                ell=ell,
                mass=background.M,
                r=radius,
                T0=metric["T0"],
                L0=metric["L0"],
                d_T0_over_r2_dr=metric_derivative,
            )
            expected_mp = complex(finite_bridge.mode.psi_even)
            direct_li_residual = _relative_complex_error(direct_li, psi)
        else:
            metric_derivative = fp / (1.0j * k) * (psi + radius * derivative) + f / (
                1.0j * k
            ) * (2.0 * derivative + radius * second_derivative)
            recovered_mp = martel_poisson_odd_master_from_rw_metric(
                ell=ell,
                k=k,
                mass=background.M,
                r=radius,
                Bt=metric["Bt"],
                B1=metric["B1"],
                dBt_dr=metric_derivative,
            )
            expected_mp = complex(finite_bridge.mode.psi_odd)
            direct_li_residual = _relative_complex_error(
                -f * complex(metric["B1"]) / radius, psi
            )
        mp_residual = _relative_complex_error(recovered_mp, expected_mp)
        residuals.extend((direct_li_residual, mp_residual))
        recovered[sector.value] = {
            "li_master": _complex_pair(psi),
            "mp_master_expected": _complex_pair(expected_mp),
            "mp_master_from_metric": _complex_pair(recovered_mp),
            "direct_li_metric_roundtrip_relative_residual": direct_li_residual,
            "mp_metric_roundtrip_relative_residual": mp_residual,
            "metric_components": {
                name: _complex_pair(value) for name, value in metric.items()
            },
        }
    return {
        "radius": radius,
        "finite_radius_total_field_only": True,
        "sectors": recovered,
        "maximum_relative_residual": float(max(residuals)),
    }


def _measure_v3(
    config: SelectedObservableMeasurementConfig,
) -> tuple[dict[str, object], dict[str, object]]:
    background = SchwarzschildBackground(M=config.mass)
    low = _radial_grid(config, background, k=config.low_kM, lmax=config.low_lmax)
    high = _radial_grid(config, background, k=config.high_kM, lmax=config.high_lmax)
    glory_radial = _radial_grid(
        config, background, k=config.glory_kM, lmax=config.glory_lmax
    )
    low_ell = np.arange(2, config.low_lmax + 1, dtype=np.int64)
    high_ell = np.arange(2, config.high_lmax + 1, dtype=np.int64)
    glory_ell = np.arange(2, config.glory_lmax + 1, dtype=np.int64)

    low_series = parity_scattering_series(
        low["even_phase"], low["odd_phase"], ell=low_ell
    )
    low_theta = np.array([0.4, 1.0, 2.0, math.pi], dtype=np.float64)
    low_scattering = scattering_matrix_cross_section(
        low_theta,
        low_series,
        k=config.low_kM,
        reduction_order=0,
        target_lmax=config.low_lmax,
    )
    low_target = np.asarray(
        spin2_low_frequency_cross_section(low_theta, mass=config.mass), dtype=float
    )
    low_relative = np.abs(
        low_scattering.differential_cross_section - low_target
    ) / np.maximum(low_target, np.finfo(float).tiny)
    low_absorption = spin2_absorption_cross_section(
        low_ell,
        low["even_transmission"],
        low["odd_transmission"],
        k=config.low_kM,
    )

    high_absorption = spin2_absorption_cross_section(
        high_ell,
        high["even_transmission"],
        high["odd_transmission"],
        k=config.high_kM,
    )
    geometric = geometric_optics_absorption_cross_section(mass=config.mass)
    high_absorption_relative = abs(high_absorption - geometric) / geometric

    glory_series = parity_scattering_series(
        glory_radial["even_phase"], glory_radial["odd_phase"], ell=glory_ell
    )
    glory = first_spin2_glory_ring(kM=config.glory_kM)
    backward_theta = np.linspace(math.pi - 0.5, math.pi, 121)
    target_lmax = config.glory_lmax - max(config.reduction_orders)
    reductions = {
        order: scattering_matrix_cross_section(
            backward_theta,
            glory_series,
            k=config.glory_kM,
            reduction_order=order,
            target_lmax=target_lmax,
        )
        for order in config.reduction_orders
    }
    reference = reductions[max(config.reduction_orders)].differential_cross_section
    pair_deltas = {
        f"q{order}_vs_q{max(config.reduction_orders)}": float(
            np.max(np.abs(result.differential_cross_section - reference))
            / max(float(np.max(np.abs(reference))), np.finfo(float).tiny)
        )
        for order, result in reductions.items()
        if order != max(config.reduction_orders)
    }
    peak_index = int(np.argmax(reference))
    numerical_peak_theta = float(backward_theta[peak_index])
    numerical_peak_offset = math.pi - numerical_peak_theta
    glory_offset_difference = abs(numerical_peak_offset - glory.backward_offset)

    values = glory_ell.astype(float)
    sigma = (values - 1.0) * values * (values + 1.0) * (values + 2.0)
    exact_parity_ratio = (sigma + 12j * config.mass * config.glory_kM) / (
        sigma - 12j * config.mass * config.glory_kM
    )
    parity_residual = float(
        np.max(
            np.abs(
                glory_radial["even_phase"] / glory_radial["odd_phase"]
                - exact_parity_ratio
            )
        )
    )

    measurement = {
        "conditioned_backend": "scipy_float64_conditioned_radial_v1",
        "phase_definition": "S_l=-A_out/[(-1)^ell A_in]; A_in=1",
        "transmission_definition": "direct conditioned horizon amplitude squared",
        "absorption_transmission_definition": (
            "direct probability projected to [0,1]; the raw value and projection "
            "correction remain explicit per mode"
        ),
        "low_frequency": {
            "kM": config.low_kM,
            "ell_range": [2, config.low_lmax],
            "theta": low_theta.tolist(),
            "computed_cross_section_over_M2": low_scattering.differential_cross_section.tolist(),
            "analytic_cross_section_over_M2": low_target.tolist(),
            "maximum_relative_difference": float(np.max(low_relative)),
            "absorption_cross_section_over_M2": float(low_absorption / config.mass**2),
            "maximum_flux_residual": low["maximum_flux_residual"],
            "maximum_transmission_bound_correction": low[
                "maximum_transmission_bound_correction"
            ],
        },
        "high_frequency": {
            "kM": config.high_kM,
            "ell_range": [2, config.high_lmax],
            "absorption_cross_section_over_M2": float(high_absorption / config.mass**2),
            "geometric_limit_27pi": float(geometric / config.mass**2),
            "relative_difference_to_27pi": float(high_absorption_relative),
            "maximum_flux_residual": high["maximum_flux_residual"],
            "maximum_transmission_bound_correction": high[
                "maximum_transmission_bound_correction"
            ],
        },
        "glory": {
            "kM": config.glory_kM,
            "ell_range": [2, config.glory_lmax],
            "semiclassical_peak_theta": glory.theta_peak,
            "semiclassical_backward_offset": glory.backward_offset,
            "selected_radial_peak_theta": numerical_peak_theta,
            "selected_radial_backward_offset": numerical_peak_offset,
            "absolute_offset_difference": glory_offset_difference,
            "selected_reduction_order": max(config.reduction_orders),
            "applicability": glory.applicability.interpretation,
            "maximum_flux_residual": glory_radial["maximum_flux_residual"],
            "maximum_transmission_bound_correction": glory_radial[
                "maximum_transmission_bound_correction"
            ],
        },
        "series_reduction": {
            "orders": list(config.reduction_orders),
            "common_target_lmax": target_lmax,
            "theta_range": [float(backward_theta[0]), float(backward_theta[-1])],
            "relative_differences": pair_deltas,
        },
        "parity": {
            "maximum_exact_relation_residual": parity_residual,
            "even_sector_independently_integrated": True,
            "even_not_parity_derived": True,
        },
        "radial_mode_count": int(
            low["mode_count"] + high["mode_count"] + glory_radial["mode_count"]
        ),
        "radial_records": low["records"] + high["records"] + glory_radial["records"],
    }
    return measurement, {
        "high_scattering": reductions[max(config.reduction_orders)],
        "high_glory": glory,
        "glory_radial": glory_radial,
        "series_target_lmax": target_lmax,
    }


def _radial_grid(
    config: SelectedObservableMeasurementConfig,
    background: SchwarzschildBackground,
    *,
    k: float,
    lmax: int,
) -> dict[str, object]:
    ell = np.arange(2, lmax + 1, dtype=np.int64)
    phase: dict[Sector, list[complex]] = {Sector.ODD: [], Sector.EVEN: []}
    transmission: dict[Sector, list[float]] = {Sector.ODD: [], Sector.EVEN: []}
    records: list[dict[str, object]] = []
    flux_residuals: list[float] = []
    bound_corrections: list[float] = []
    for sector in (Sector.ODD, Sector.EVEN):
        for ell_value in ell:
            result = solve_conditioned_radial_at_radius(
                ConditionedRadialRequest(
                    sector=sector,
                    ell=int(ell_value),
                    k=k,
                    required_radius=config.required_radius,
                    r_out=config.r_out,
                    r_in_eps=config.r_in_eps,
                    rtol=config.rtol,
                    atol=config.atol,
                    outer_series_order=config.outer_series_order,
                ),
                background,
            )
            phase_factor = -result.A_out / ((-1) ** int(ell_value))
            gamma = float(result.diagnostics["horizon_transmission_probability"])
            gamma_for_absorption = float(np.clip(gamma, 0.0, 1.0))
            bound_correction = abs(gamma_for_absorption - gamma)
            flux = float(result.diagnostics["flux_residual"])
            phase[sector].append(phase_factor)
            transmission[sector].append(gamma_for_absorption)
            flux_residuals.append(flux)
            bound_corrections.append(bound_correction)
            records.append(
                {
                    "kM": k,
                    "sector": sector.value,
                    "ell": int(ell_value),
                    "phase_factor": _complex_pair(phase_factor),
                    "reflection_probability": float(
                        result.diagnostics["reflection_probability"]
                    ),
                    "horizon_transmission_probability": gamma,
                    "absorption_transmission_probability": gamma_for_absorption,
                    "transmission_bound_correction": bound_correction,
                    "flux_residual": flux,
                    "outer_boundary_residual": float(
                        result.diagnostics["outer_boundary_residual"]
                    ),
                    "match_condition_number": float(
                        result.diagnostics["match_condition_number"]
                    ),
                    "match_condition_number_censored_at_float_max": bool(
                        result.diagnostics[
                            "match_condition_number_censored_at_float_max"
                        ]
                    ),
                    "actual_precision_bits": int(
                        result.diagnostics["actual_precision_bits"]
                    ),
                    "outer_basis": str(result.diagnostics["outer_basis"]),
                    "outer_series_order": int(result.diagnostics["outer_series_order"]),
                    "integration_status": str(result.diagnostics["integration_status"]),
                    "paper_specific_envelope_used": bool(
                        result.diagnostics["paper_specific_envelope_used"]
                    ),
                }
            )
    return {
        "odd_phase": np.asarray(phase[Sector.ODD], dtype=np.complex128),
        "even_phase": np.asarray(phase[Sector.EVEN], dtype=np.complex128),
        "odd_transmission": np.asarray(transmission[Sector.ODD], dtype=float),
        "even_transmission": np.asarray(transmission[Sector.EVEN], dtype=float),
        "records": records,
        "mode_count": len(records),
        "maximum_flux_residual": float(max(flux_residuals)),
        "maximum_transmission_bound_correction": float(max(bound_corrections)),
    }


def _measure_v4(config: SelectedObservableMeasurementConfig) -> dict[str, object]:
    factories = (static_schwarzschild_observer, radial_freefall_from_infinity_observer)
    records: list[dict[str, object]] = []
    for factory in factories:
        observer = factory(
            mass=config.mass,
            r=config.observer_radius,
            theta=config.observer_theta,
        )
        oracle = schwarzschild_radial_pure_gauge_oracle(
            mass=config.mass,
            r=config.observer_radius,
            observer=observer,
            first_arm=[1.0, 0.0, 0.0],
            second_arm=[0.0, 1.0, 0.0],
            gauge_vector_radial=config.gauge_vector_radial,
        )
        transport = check_radial_frame_transport(observer)
        tetrad = np.vstack((observer.u, observer.spatial_legs))
        gram_residual = float(
            np.max(
                np.abs(
                    tetrad @ observer.metric @ tetrad.T - np.diag([-1.0, 1.0, 1.0, 1.0])
                )
            )
        )
        records.append(
            {
                "observer": observer.label,
                "worldline": observer.worldline,
                "tetrad_transport": observer.tetrad_transport,
                "transport_law_evaluated": transport.transport_law,
                "four_acceleration": transport.four_acceleration.tolist(),
                "spatial_leg_transport_residuals": (
                    transport.spatial_leg_residuals.tolist()
                ),
                "acceleration_norm": transport.acceleration_norm,
                "maximum_transport_residual": transport.maximum_transport_residual,
                "tetrad_orthonormality_residual": gram_residual,
                "metric_perturbation_norm": oracle.metric_perturbation_norm,
                "linearized_riemann_norm": oracle.linearized_riemann_norm,
                "tetrad_perturbation_norm": oracle.tetrad_perturbation_norm,
                "metric_curvature_consistency_residual": oracle.metric_curvature_consistency_residual,
                "coordinate_lie_term": _complex_pair(
                    oracle.transformed.coordinate_perturbation
                ),
                "worldline_pullback": _complex_pair(
                    oracle.transformed.worldline_pullback
                ),
                "operational_residual": oracle.absolute_residual,
                "pipeline": oracle.pipeline,
            }
        )
    return {
        "records": records,
        "maximum_operational_residual": float(
            max(record["operational_residual"] for record in records)
        ),
        "maximum_metric_curvature_consistency_residual": float(
            max(record["metric_curvature_consistency_residual"] for record in records)
        ),
        "maximum_tetrad_orthonormality_residual": float(
            max(record["tetrad_orthonormality_residual"] for record in records)
        ),
        "maximum_frame_transport_residual": float(
            max(record["maximum_transport_residual"] for record in records)
        ),
        "gauge_family": "constant nonzero radial xi^r in Schwarzschild coordinates",
        "finite_arm_worldline_integration_performed": False,
    }


def _measure_v5(
    config: SelectedObservableMeasurementConfig,
    radial_cache: Mapping[str, object],
) -> dict[str, object]:
    scattering = radial_cache["high_scattering"]
    glory = radial_cache["high_glory"]
    index = int(np.argmin(np.abs(scattering.theta - glory.theta_peak)))
    m22 = complex(scattering.M22[index])
    m12 = complex(scattering.M12[index])
    helicity_matrix = np.array([[m22, m12], [m12, m22]], dtype=np.complex128)
    transform = linear_to_helicity_transform()
    linear_matrix = transform.conj().T @ helicity_matrix @ transform

    def response(incident: np.ndarray) -> np.ndarray:
        return transform.conj().T @ helicity_matrix @ transform @ incident

    plus_incident = np.array([1.0, 0.0], dtype=np.complex128)
    cross_incident = np.array([0.0, 1.0], dtype=np.complex128)
    plus_column = response(plus_incident)
    cross_column = response(cross_incident)
    phase = AbsolutePhaseConvention()
    transfer = polarization_transfer_from_columns(
        plus_column,
        cross_column,
        field_definition="scattered",
        phase_convention=phase,
    )
    rotated = rotate_polarization_transfer(
        transfer,
        incident_basis_angle=config.transfer_incident_rotation,
        observer_basis_angle=config.transfer_observer_rotation,
    )
    incident_rotation = polarization_basis_rotation(config.transfer_incident_rotation)
    observer_rotation = polarization_basis_rotation(config.transfer_observer_rotation)

    def rotated_response(incident: np.ndarray) -> np.ndarray:
        old_incident = incident_rotation.T @ incident
        return observer_rotation @ response(old_incident)

    independently_rebuilt = np.column_stack(
        (rotated_response(plus_incident), rotated_response(cross_incident))
    )
    covariance_residual = float(np.max(np.abs(rotated.matrix - independently_rebuilt)))
    direct_matrix_residual = float(np.max(np.abs(transfer.matrix - linear_matrix)))
    return {
        "kM": config.glory_kM,
        "theta": float(scattering.theta[index]),
        "azimuth": 0.0,
        "radial_series_target_lmax": int(radial_cache["series_target_lmax"]),
        "radial_reduction_order": int(scattering.reduction_order),
        "incident_basis_rotation_rad": config.transfer_incident_rotation,
        "observer_basis_rotation_rad": config.transfer_observer_rotation,
        "helicity_matrix": _complex_matrix(helicity_matrix),
        "plus_incident_column": [_complex_pair(value) for value in plus_column],
        "cross_incident_column": [_complex_pair(value) for value in cross_column],
        "incident_basis_determinant": float(
            _determinant_2x2(
                np.column_stack((plus_incident, cross_incident))
            ).real
        ),
        "transfer_matrix": _complex_matrix(transfer.matrix),
        "direct_matrix_residual": direct_matrix_residual,
        "singular_values": transfer.singular_values.tolist(),
        "trace_fdagger_f": transfer.trace_fdagger_f,
        "determinant": _complex_pair(transfer.determinant),
        "helicity_mixing_power": transfer.helicity_mixing_power,
        "rotation_covariance_residual": covariance_residual,
        "rotated_transfer_matrix": _complex_matrix(rotated.matrix),
        "phase_convention": dict(phase.to_mapping()),
        "phase_convention_sha256": phase.sha256(),
        "field_definition": transfer.field_definition,
        "production_unit_column_solves_performed": False,
        "column_origin": (
            "two linearly independent unit linear-polarization inputs propagated "
            "through the selected conditioned-radial asymptotic helicity matrix"
        ),
    }


def _v2_master_section(
    config: SelectedObservableMeasurementConfig,
    sources: Mapping[str, Mapping[str, object]],
    measurement: Mapping[str, object],
) -> dict[str, object]:
    infinity = measurement["infinity_strain"]
    waveform_scale = max(
        abs(complex(*infinity["h_plus"])),
        abs(complex(*infinity["h_cross"])),
    )
    checks = {
        "master_strain_waveform": _metric(
            waveform_scale,
            "strain_amplitude",
            "Li outgoing amplitudes mapped through the explicit MP normalization bridge.",
        ),
        "infinity_flux": _metric(
            measurement["infinity_flux"],
            "M^-2",
            "MP infinity flux evaluated from the bridged Li outgoing coefficient.",
        ),
        "horizon_flux": _metric(
            measurement["horizon_flux"],
            "M^-2",
            "MP horizon flux evaluated from the bridged Li horizon coefficient.",
        ),
        "radial_flux_consistency": _metric(
            measurement["radial_flux_residual"],
            "absolute_flux_balance",
            "Maximum conditioned-radial flux residual across the selected parities.",
        ),
    }
    numerical = _selected_radial_numerical_budget(config)
    return _section(
        observable="master_to_strain_flux",
        domain_id="selected_li_mp_waveform_v1",
        parameters={
            "kM": "0.5",
            "ell": [2],
            "m": [2],
            "boundaries": ["future_null_infinity", "event_horizon"],
        },
        items=[
            {"boundary": "future_null_infinity", "ell": 2, "m": 2},
            {"boundary": "event_horizon", "ell": 2, "m": 2},
        ],
        selection_policy=(
            "one Li-normalized conditioned outgoing/horizon coefficient per parity, "
            "mapped through the explicit MP bridge"
        ),
        sources=sources,
        check_metrics=checks,
        numerical=numerical,
        convention=_v2_convention_budget(),
        measurements=dict(measurement),
        limitations=[
            "only one frequency/multipole and one radial setting are evaluated",
            "large-radius metric/Psi4 and external absolute-amplitude routes are not closed",
        ],
    )


def _v2_crosscheck_section(
    config: SelectedObservableMeasurementConfig,
    sources: Mapping[str, Mapping[str, object]],
    measurement: Mapping[str, object],
) -> dict[str, object]:
    checks = {
        "master_vs_metric": _metric(
            measurement["finite_radius_metric_roundtrip"]["maximum_relative_residual"],
            "relative_error",
            "Finite-radius Li master to RW metric to MP invariant roundtrip.",
        ),
        "master_vs_psi4": None,
        "master_vs_external": None,
    }
    return _section(
        observable="metric_psi4_external_crosscheck",
        domain_id="selected_li_metric_bridge_v1",
        parameters={
            "kM": "0.5",
            "ell": [2],
            "m": [2],
            "route": "Li master to finite-radius RW metric to MP invariant",
        },
        items=[
            {"comparison": "Li_metric_MP_even", "ell": 2, "m": 2},
            {"comparison": "Li_metric_MP_odd", "ell": 2, "m": 2},
        ],
        selection_policy=(
            "finite-radius metric roundtrip for both parities; algebraic strain-to-Psi4 "
            "is recorded but not accepted as a large-radius cross-check"
        ),
        sources=sources,
        check_metrics=checks,
        numerical=_selected_radial_numerical_budget(config),
        convention=_v2_convention_budget(),
        measurements=dict(measurement),
        limitations=[
            "finite-radius total metric is used only for a master roundtrip, never as an infinity waveform",
            "large-radius metric/Psi4 and external BHPT absolute-amplitude routes remain NOT_ASSESSED",
        ],
    )


def _v3_section(
    config: SelectedObservableMeasurementConfig,
    sources: Mapping[str, Mapping[str, object]],
    measurement: Mapping[str, object],
) -> dict[str, object]:
    low = measurement["low_frequency"]
    high = measurement["high_frequency"]
    glory = measurement["glory"]
    series = measurement["series_reduction"]
    parity = measurement["parity"]
    series_delta = max(series["relative_differences"].values())
    checks = {
        "low_frequency_differential": _metric(
            low["maximum_relative_difference"],
            "relative_error",
            "Finite selected conditioned-radial partial wave compared with the analytic low-frequency target.",
        ),
        "low_frequency_absorption": _metric(
            low["absorption_cross_section_over_M2"],
            "M^2",
            "Selected direct horizon-transmission absorption at low kM.",
        ),
        "high_frequency_absorption": _metric(
            high["relative_difference_to_27pi"],
            "relative_error",
            "Selected truncated absorption compared with 27*pi*M^2.",
        ),
        "backward_glory": _metric(
            glory["absolute_offset_difference"],
            "radian",
            "Selected radial scattering peak compared with the semiclassical first glory ring.",
        ),
        "helicity_parity": _metric(
            parity["maximum_exact_relation_residual"],
            "complex_absolute_error",
            "Independently integrated odd/even phase factors checked against the exact parity relation.",
        ),
        "series_lmax_convergence": _metric(
            series_delta,
            "relative_difference",
            "q=0,1,2 comparison at one common selected target lmax.",
        ),
    }
    numerical = {
        "r_in": _budget(
            "PARTIAL",
            config.r_in_eps,
            "relative_horizon_offset",
            "One r_in value; no ladder.",
        ),
        "r_out": _budget("PARTIAL", config.r_out, "M", "One r_out value; no ladder."),
        "jost_order": _budget(
            "PARTIAL", config.outer_series_order, "order", "One Jost order; no ladder."
        ),
        "ode_tolerance": _budget(
            "PARTIAL", config.rtol, "relative", "One DOP853 tolerance pair; no ladder."
        ),
        "arithmetic_precision": _budget(
            "PARTIAL", 15.95, "decimal_digits", "Actual SciPy float64 precision."
        ),
        "backend_difference": _budget(
            "NOT_ASSESSED",
            None,
            "not_assessed",
            "No independent backend in this candidate.",
        ),
        "lmax_tail": _budget(
            "PARTIAL",
            series_delta,
            "relative_difference",
            "Selected common-target q ladder only.",
        ),
        "axis_limit": _budget(
            "NOT_ASSESSED", None, "not_assessed", "No forward-axis ladder."
        ),
    }
    convention = {
        "observer": _budget(
            "NOT_ASSESSED",
            None,
            "not_applicable",
            "Cross section is asymptotic; no local observer.",
            applicability="NOT_APPLICABLE",
        ),
        "worldline": _budget(
            "NOT_ASSESSED",
            None,
            "not_applicable",
            "Cross section is asymptotic; no worldline.",
            applicability="NOT_APPLICABLE",
        ),
        "tetrad": _budget(
            "NOT_ASSESSED",
            None,
            "not_applicable",
            "Cross section uses a frozen helicity basis.",
            applicability="NOT_APPLICABLE",
        ),
        "polarization_basis": _budget(
            "PARTIAL",
            parity["maximum_exact_relation_residual"],
            "complex_absolute_error",
            "Odd/even parity and helicity convention recorded.",
        ),
        "phase_origin": _budget(
            "PARTIAL",
            0.0,
            "radian",
            "Frozen r* formula and S=-R/(-1)^ell used; no external phase comparison.",
        ),
        "total_scattered_definition": _budget(
            "PARTIAL",
            0.0,
            "categorical_residual",
            "Scattered asymptotic matrix used explicitly.",
        ),
    }
    items = [
        {
            "kM": _number_text(config.low_kM),
            "ell_min": 2,
            "ell_max": config.low_lmax,
            "sectors": ["odd", "even"],
        },
        {
            "kM": _number_text(config.high_kM),
            "ell_min": 2,
            "ell_max": config.high_lmax,
            "sectors": ["odd", "even"],
        },
    ]
    return _section(
        observable="spin2_scattering_limits",
        domain_id="selected_conditioned_spin2_benchmarks_v1",
        parameters={
            "frequencies": [
                _number_text(config.low_kM),
                _number_text(config.high_kM),
                _number_text(config.glory_kM),
            ],
            "reduction_orders": list(config.reduction_orders),
        },
        items=[
            *items,
            {
                "kM": _number_text(config.glory_kM),
                "ell_min": 2,
                "ell_max": config.glory_lmax,
                "sectors": ["odd", "even"],
                "purpose": "backward_glory_and_transfer",
            },
        ],
        selection_policy=(
            "three bounded frequency blocks, both parities, no production-domain "
            "extrapolation"
        ),
        sources=sources,
        check_metrics=checks,
        numerical=numerical,
        convention=convention,
        measurements=dict(measurement),
        limitations=[
            "low/high limits are sampled at finite kM and finite lmax",
            "no arbitrary-precision or external-backend difference is included",
            "glory and series diagnostics are selected-window results only",
        ],
    )


def _v4_section(
    config: SelectedObservableMeasurementConfig,
    sources: Mapping[str, Mapping[str, object]],
    measurement: Mapping[str, object],
) -> dict[str, object]:
    records = measurement["records"]
    by_observer = {record["observer"]: record for record in records}
    checks = {
        "static_observer_response": _metric(
            by_observer["static_schwarzschild"]["operational_residual"],
            "absolute_response",
            "Nontrivial metric-curvature-frame-worldline cancellation for the static frame.",
        ),
        "freefall_observer_response": _metric(
            by_observer["radial_freefall_E1"]["operational_residual"],
            "absolute_response",
            "Nontrivial metric-curvature-frame-worldline cancellation for the E=1 freefall frame.",
        ),
        "pure_gauge_response_invariance": _metric(
            measurement["maximum_operational_residual"],
            "absolute_response",
            "Maximum selected two-observer operational residual.",
        ),
        "tetrad_transport": _metric(
            measurement["maximum_frame_transport_residual"],
            "connection_transport_residual",
            "Static Fermi-Walker and E=1 freefall parallel transport are evaluated from the Schwarzschild connection.",
        ),
    }
    numerical = _mostly_open_numerical(
        "Selected float64 analytic/metric-jet oracle; no numerical ladder."
    )
    numerical["arithmetic_precision"] = _budget(
        "PARTIAL", 15.95, "decimal_digits", "Actual NumPy float64 precision."
    )
    numerical["backend_difference"] = _budget(
        "PARTIAL",
        measurement["maximum_metric_curvature_consistency_residual"],
        "absolute_response",
        "Metric-curvature Lie term compared with its analytic scalar derivative.",
    )
    convention = {
        "observer": _budget(
            "PARTIAL",
            0.0,
            "categorical_residual",
            "Static and E=1 radial-freefall observers are explicit.",
        ),
        "worldline": _budget(
            "PARTIAL",
            0.0,
            "categorical_residual",
            "Worldline displacement delta z=+xi is included.",
        ),
        "tetrad": _budget(
            "PARTIAL",
            measurement["maximum_tetrad_orthonormality_residual"],
            "gram_residual",
            "Exact factory tetrads and Lie-dragged perturbations are included.",
        ),
        "polarization_basis": _budget(
            "PARTIAL",
            0.0,
            "categorical_residual",
            "Radial-versus-polar principal arm basis is explicit.",
        ),
        "phase_origin": _budget(
            "NOT_ASSESSED",
            None,
            "not_assessed",
            "Static pure gauge has no waveform phase comparison.",
        ),
        "total_scattered_definition": _budget(
            "PARTIAL",
            0.0,
            "categorical_residual",
            "Background plus coordinate perturbation plus worldline pullback are separated.",
        ),
    }
    return _section(
        observable="finite_radius_tidal_detector",
        domain_id="selected_two_observer_radial_gauge_v1",
        parameters={
            "M": _number_text(config.mass),
            "r": _number_text(config.observer_radius),
            "theta": _number_text(config.observer_theta),
            "xi_r": _number_text(config.gauge_vector_radial),
        },
        items=[
            {"observer": "radial_freefall_E1"},
            {"observer": "static_schwarzschild"},
        ],
        selection_policy="exact two frozen observer factories and one nonzero constant radial gauge vector",
        sources=sources,
        check_metrics=checks,
        numerical=numerical,
        convention=convention,
        measurements=dict(measurement),
        limitations=[
            "only one constant radial pure-gauge family is exercised",
            "finite-arm worldline integration and a general transported detector are not implemented",
        ],
    )


def _v5_section(
    config: SelectedObservableMeasurementConfig,
    sources: Mapping[str, Mapping[str, object]],
    measurement: Mapping[str, object],
) -> dict[str, object]:
    minimum_singular = min(measurement["singular_values"])
    checks = {
        "two_incident_basis_rank": _metric(
            minimum_singular,
            "minimum_singular_value",
            "Two linearly independent unit input columns were propagated through the selected radial scattering map.",
        ),
        "basis_rotation_covariance": _metric(
            measurement["rotation_covariance_residual"],
            "complex_absolute_error",
            "Rotated columns were rebuilt independently from the basis maps.",
        ),
        "phase_convention_frozen": _metric(
            0.0,
            "hash_reconstruction_residual",
            "AbsolutePhaseConvention mapping rehashes to the stored SHA-256.",
        ),
        "matrix_diagnostics": _metric(
            measurement["direct_matrix_residual"],
            "complex_absolute_error",
            "Column-built matrix agrees with the direct helicity-to-linear transform.",
        ),
    }
    numerical = {
        "r_in": _budget(
            "PARTIAL",
            config.r_in_eps,
            "relative_horizon_offset",
            "Inherited selected conditioned radial value; no ladder.",
        ),
        "r_out": _budget(
            "PARTIAL",
            config.r_out,
            "M",
            "Inherited selected conditioned radial value; no ladder.",
        ),
        "jost_order": _budget(
            "PARTIAL",
            config.outer_series_order,
            "order",
            "Inherited selected Jost order; no ladder.",
        ),
        "ode_tolerance": _budget(
            "PARTIAL",
            config.rtol,
            "relative",
            "Inherited selected DOP853 tolerance; no ladder.",
        ),
        "arithmetic_precision": _budget(
            "PARTIAL", 15.95, "decimal_digits", "Actual NumPy/SciPy float64 precision."
        ),
        "backend_difference": _budget(
            "NOT_ASSESSED", None, "not_assessed", "No independent transfer backend."
        ),
        "lmax_tail": _budget(
            "PARTIAL",
            measurement["radial_series_target_lmax"],
            "lmax",
            "One selected common target lmax.",
        ),
        "axis_limit": _budget(
            "NOT_ASSESSED", None, "not_assessed", "Selected backward angle is off-axis."
        ),
    }
    convention = {
        "observer": _budget(
            "PARTIAL",
            0.0,
            "categorical_residual",
            "Asymptotic Cartesian output basis is explicit.",
        ),
        "worldline": _budget(
            "PARTIAL",
            0.0,
            "categorical_residual",
            "Asymptotic inertial reference is explicit; no finite-radius detector.",
        ),
        "tetrad": _budget(
            "PARTIAL",
            0.0,
            "categorical_residual",
            "Incident Cartesian tetrad convention is frozen.",
        ),
        "polarization_basis": _budget(
            "PARTIAL",
            measurement["rotation_covariance_residual"],
            "complex_absolute_error",
            "Linear/helicity basis maps and rotations are explicit.",
        ),
        "phase_origin": _budget(
            "PARTIAL",
            0.0,
            "hash_reconstruction_residual",
            "Full absolute phase mapping and SHA-256 are stored.",
        ),
        "total_scattered_definition": _budget(
            "PARTIAL",
            0.0,
            "categorical_residual",
            "Matrix is explicitly scattered, not total.",
        ),
    }
    return _section(
        observable="complex_lensing_matrix",
        domain_id="selected_radial_scattering_transfer_v1",
        parameters={
            "kM": _number_text(config.glory_kM),
            "theta": _number_text(measurement["theta"]),
            "field_definition": "scattered",
        },
        items=[{"incident_column": "unit_cross"}, {"incident_column": "unit_plus"}],
        selection_policy="two linearly independent unit columns at one selected radial-scattering angle",
        sources=sources,
        check_metrics=checks,
        numerical=numerical,
        convention=convention,
        measurements=dict(measurement),
        limitations=[
            "columns are selected asymptotic scattering responses, not full finite-radius production solves",
            "no external transfer backend or production parameter-domain coverage is included",
        ],
    )


def _section(
    *,
    observable: str,
    domain_id: str,
    parameters: Mapping[str, object],
    items: Sequence[Mapping[str, object]],
    selection_policy: str,
    sources: Mapping[str, Mapping[str, object]],
    check_metrics: Mapping[str, object],
    numerical: Mapping[str, object],
    convention: Mapping[str, object],
    measurements: Mapping[str, object],
    limitations: Sequence[str],
) -> dict[str, object]:
    labels = OBSERVABLE_SOURCE_LABELS[observable]
    return {
        "observable": observable,
        "acceptance_gate": OBSERVABLE_GATES[observable],
        "state": "PARTIAL",
        "explicit_domain": {
            "domain_id": domain_id,
            "parameters": dict(parameters),
            "items": [dict(item) for item in items],
            "selection_policy": selection_policy,
        },
        "actual_arithmetic": {
            "backend": "CPython-NumPy-SciPy float64",
            "precision_kind": "BINARY_FLOAT",
            "decimal_digits": 16,
        },
        "source_identities": {label: dict(sources[label]) for label in labels},
        "check_metrics": dict(check_metrics),
        "numerical_budget": dict(numerical),
        "convention_budget": dict(convention),
        "measurements": dict(measurements),
        "limitations": list(limitations),
    }


def _mostly_open_numerical(reason: str) -> dict[str, object]:
    result = {
        name: _budget("NOT_ASSESSED", None, "not_assessed", reason)
        for name in NUMERICAL_BUDGETS
    }
    result["arithmetic_precision"] = _budget(
        "PARTIAL", 15.95, "decimal_digits", "Actual float64 arithmetic recorded."
    )
    return result


def _selected_radial_numerical_budget(
    config: SelectedObservableMeasurementConfig,
) -> dict[str, object]:
    result = _mostly_open_numerical(
        "No ladder or independent backend was evaluated for this selected V2 route."
    )
    result.update(
        {
            "r_in": _budget(
                "PARTIAL",
                config.r_in_eps,
                "relative_horizon_offset",
                "One selected r_in value; no ladder.",
            ),
            "r_out": _budget(
                "PARTIAL", config.r_out, "M", "One selected r_out value; no ladder."
            ),
            "jost_order": _budget(
                "PARTIAL",
                config.outer_series_order,
                "order",
                "One selected Jost order; no ladder.",
            ),
            "ode_tolerance": _budget(
                "PARTIAL",
                config.rtol,
                "relative",
                "One selected DOP853 tolerance pair; no ladder.",
            ),
        }
    )
    return result


def _v2_convention_budget() -> dict[str, object]:
    return {
        "observer": _budget(
            "PARTIAL",
            0.0,
            "categorical_residual",
            "Asymptotic/horizon boundaries are explicit.",
        ),
        "worldline": _budget(
            "PARTIAL",
            0.0,
            "categorical_residual",
            "No finite-radius worldline claim is made.",
        ),
        "tetrad": _budget(
            "PARTIAL",
            0.0,
            "categorical_residual",
            "Project strict-NP conversion convention is explicit.",
        ),
        "polarization_basis": _budget(
            "PARTIAL",
            0.0,
            "categorical_residual",
            "MP plus/cross angular convention is explicit.",
        ),
        "phase_origin": _budget(
            "PARTIAL",
            0.0,
            "radian",
            "Fourier, Li-to-MP bridge, and outgoing Psi4 signs are explicit.",
        ),
        "total_scattered_definition": _budget(
            "PARTIAL",
            0.0,
            "categorical_residual",
            "Li outgoing/horizon coefficients are separated from the finite-radius total field.",
        ),
    }


def _budget(
    state: str,
    value: float | int | None,
    units: str,
    reason: str,
    *,
    applicability: str = "REQUIRED",
) -> dict[str, object]:
    return {
        "applicability": applicability,
        "state": state,
        "value": None if value is None else float(value),
        "units": units,
        "reason": reason,
    }


def _metric(value: object, units: str, reason: str) -> dict[str, object]:
    return {"value": float(value), "units": units, "reason": reason}


def _validate_section(
    value: object,
    *,
    observable: str,
    verify_live_sources: bool,
) -> None:
    fields = {
        "observable",
        "acceptance_gate",
        "state",
        "explicit_domain",
        "actual_arithmetic",
        "source_identities",
        "check_metrics",
        "numerical_budget",
        "convention_budget",
        "measurements",
        "limitations",
    }
    item = _exact(value, fields, f"measurement section {observable}")
    if (
        item["observable"] != observable
        or item["acceptance_gate"] != OBSERVABLE_GATES[observable]
        or item["state"] != "PARTIAL"
    ):
        raise ObservableMeasurementError(
            f"measurement section {observable} claim changed"
        )
    domain = _exact(
        item["explicit_domain"],
        {"domain_id", "parameters", "items", "selection_policy"},
        f"measurement section {observable} domain",
    )
    for name in ("domain_id", "selection_policy"):
        _required_text(domain[name], f"measurement section {observable} {name}")
    if not isinstance(domain["parameters"], Mapping) or not domain["parameters"]:
        raise ObservableMeasurementError(
            f"measurement section {observable} parameters are empty"
        )
    if not isinstance(domain["items"], list) or not domain["items"]:
        raise ObservableMeasurementError(
            f"measurement section {observable} items are empty"
        )
    _validate_finite_json(
        domain["parameters"], f"measurement section {observable} parameters"
    )
    _validate_finite_json(domain["items"], f"measurement section {observable} items")
    arithmetic = _exact(
        item["actual_arithmetic"],
        {"backend", "precision_kind", "decimal_digits"},
        f"measurement section {observable} arithmetic",
    )
    _required_text(arithmetic["backend"], f"measurement section {observable} backend")
    if (
        arithmetic["precision_kind"] != "BINARY_FLOAT"
        or arithmetic["decimal_digits"] != 16
    ):
        raise ObservableMeasurementError(
            f"measurement section {observable} arithmetic changed"
        )
    sources = item["source_identities"]
    expected_labels = set(OBSERVABLE_SOURCE_LABELS[observable])
    if not isinstance(sources, Mapping) or set(sources) != expected_labels:
        raise ObservableMeasurementError(
            f"measurement section {observable} source inventory changed"
        )
    for label, identity in sources.items():
        checked = _validate_source_identity(
            identity, f"measurement section {observable} source {label}"
        )
        if (
            verify_live_sources
            and source_file_identity(Path(str(checked["path"]))) != checked
        ):
            raise ObservableMeasurementError(
                f"measurement section {observable} source drift: {label}"
            )
    checks = item["check_metrics"]
    if not isinstance(checks, Mapping) or set(checks) != set(
        REQUIRED_CHECKS[observable]
    ):
        raise ObservableMeasurementError(
            f"measurement section {observable} check inventory changed"
        )
    for name, metric in checks.items():
        if metric is None:
            continue
        record = _exact(
            metric,
            {"value", "units", "reason"},
            f"measurement check {observable}/{name}",
        )
        _nonnegative_finite(record["value"], f"measurement check {observable}/{name}")
        _required_text(record["units"], f"measurement check {observable}/{name} units")
        _required_text(
            record["reason"], f"measurement check {observable}/{name} reason"
        )
    _validate_budget_map(
        item["numerical_budget"], NUMERICAL_BUDGETS, f"{observable} numerical"
    )
    _validate_budget_map(
        item["convention_budget"], CONVENTION_BUDGETS, f"{observable} convention"
    )
    if not isinstance(item["measurements"], Mapping) or not item["measurements"]:
        raise ObservableMeasurementError(
            f"measurement section {observable} values are empty"
        )
    _validate_finite_json(
        item["measurements"], f"measurement section {observable} values"
    )
    _validate_observable_measurements(observable, item["measurements"])
    limitations = item["limitations"]
    if not isinstance(limitations, list) or not limitations:
        raise ObservableMeasurementError(
            f"measurement section {observable} limitations are empty"
        )
    for limitation in limitations:
        _required_text(limitation, f"measurement section {observable} limitation")


def _validate_observable_measurements(
    observable: str, value: Mapping[str, object]
) -> None:
    if observable in {"master_to_strain_flux", "metric_psi4_external_crosscheck"}:
        _validate_v2_measurements(value)
    elif observable == "spin2_scattering_limits":
        _validate_v3_measurements(value)
    elif observable == "finite_radius_tidal_detector":
        _validate_v4_measurements(value)
    elif observable == "complex_lensing_matrix":
        _validate_v5_measurements(value)
    else:  # pragma: no cover - inventory is checked before dispatch
        raise ObservableMeasurementError(
            f"unknown observable measurements: {observable}"
        )


def _validate_v2_measurements(value: Mapping[str, object]) -> None:
    fields = {
        "kM",
        "input_master_normalization",
        "project_master_normalization_bridge",
        "project_master_values_used",
        "bridge",
        "outgoing_mode",
        "horizon_mode",
        "infinity_strain",
        "horizon_strain",
        "infinity_flux",
        "horizon_flux",
        "psi4_from_infinity_strain",
        "psi4_convention",
        "algebraic_strain_to_psi4_route_evaluated",
        "metric_route_evaluated",
        "metric_route_scope",
        "finite_radius_metric_roundtrip",
        "radial_flux_residual",
        "finite_radius_total_field_used_as_infinity_waveform",
        "large_radius_metric_psi4_route_evaluated",
        "external_bhpt_amplitude_route_evaluated",
    }
    item = _exact(value, fields, "V2 measurements")
    if (
        item["project_master_normalization_bridge"] != "IMPLEMENTED_EXPLICIT_LI_TO_MP"
        or item["project_master_values_used"] is not True
        or item["algebraic_strain_to_psi4_route_evaluated"] is not True
        or item["metric_route_evaluated"] is not True
        or item["metric_route_scope"] != "finite_radius_metric_to_master_roundtrip_only"
        or item["finite_radius_total_field_used_as_infinity_waveform"] is not False
        or item["large_radius_metric_psi4_route_evaluated"] is not False
        or item["external_bhpt_amplitude_route_evaluated"] is not False
    ):
        raise ObservableMeasurementError("V2 bridge/scope status changed")
    k = _positive_finite(item["kM"], "V2 kM")
    _required_text(item["input_master_normalization"], "V2 master normalization")
    _required_text(item["psi4_convention"], "V2 Psi4 convention")
    bridge = _exact(
        item["bridge"],
        {"even_formula", "odd_formula", "angular_sign", "assumptions", "source"},
        "V2 bridge",
    )
    if (
        bridge["even_formula"] != "Psi_ZM = psi_Li_even"
        or bridge["odd_formula"] != "Psi_CPM = (2 i / k) psi_Li_odd"
        or bridge["angular_sign"] != "Li odd vector harmonic = -X_A^(MP)"
    ):
        raise ObservableMeasurementError("V2 normalization formula changed")
    for name in ("assumptions", "source"):
        _required_text(bridge[name], f"V2 bridge {name}")
    for route in ("outgoing_mode", "horizon_mode"):
        mode = _exact(
            item[route],
            {
                "ell",
                "m",
                "psi_li_even",
                "psi_li_odd",
                "psi_mp_even",
                "psi_mp_odd",
            },
            f"V2 {route}",
        )
        if mode["ell"] != 2 or mode["m"] != 2:
            raise ObservableMeasurementError("V2 selected mode changed")
        li_even = _complex_from_pair(mode["psi_li_even"], f"V2 {route} Li even")
        li_odd = _complex_from_pair(mode["psi_li_odd"], f"V2 {route} Li odd")
        mp_even = _complex_from_pair(mode["psi_mp_even"], f"V2 {route} MP even")
        mp_odd = _complex_from_pair(mode["psi_mp_odd"], f"V2 {route} MP odd")
        if mp_even != li_even or mp_odd != 2.0j * li_odd / k:
            raise ObservableMeasurementError(
                f"V2 {route} bridge values are not derived"
            )
    for boundary in ("infinity_strain", "horizon_strain"):
        strain = _exact(
            item[boundary], {"h_plus", "h_cross", "areal_scale"}, f"V2 {boundary}"
        )
        _complex_from_pair(strain["h_plus"], f"V2 {boundary} plus")
        _complex_from_pair(strain["h_cross"], f"V2 {boundary} cross")
        _nonnegative_finite(strain["areal_scale"], f"V2 {boundary} scale")
    _nonnegative_finite(item["infinity_flux"], "V2 infinity flux")
    _nonnegative_finite(item["horizon_flux"], "V2 horizon flux")
    _complex_from_pair(item["psi4_from_infinity_strain"], "V2 Psi4")
    _nonnegative_finite(item["radial_flux_residual"], "V2 radial flux residual")
    roundtrip = _exact(
        item["finite_radius_metric_roundtrip"],
        {
            "radius",
            "finite_radius_total_field_only",
            "sectors",
            "maximum_relative_residual",
        },
        "V2 finite-radius roundtrip",
    )
    _positive_finite(roundtrip["radius"], "V2 roundtrip radius")
    if roundtrip["finite_radius_total_field_only"] is not True:
        raise ObservableMeasurementError("V2 finite-radius roundtrip scope changed")
    sectors = roundtrip["sectors"]
    if not isinstance(sectors, Mapping) or set(sectors) != {"even", "odd"}:
        raise ObservableMeasurementError("V2 roundtrip sector inventory changed")
    residuals: list[float] = []
    for sector, record_value in sectors.items():
        record = _exact(
            record_value,
            {
                "li_master",
                "mp_master_expected",
                "mp_master_from_metric",
                "direct_li_metric_roundtrip_relative_residual",
                "mp_metric_roundtrip_relative_residual",
                "metric_components",
            },
            f"V2 roundtrip {sector}",
        )
        li = _complex_from_pair(record["li_master"], f"V2 roundtrip {sector} Li")
        expected = _complex_from_pair(
            record["mp_master_expected"], f"V2 roundtrip {sector} expected MP"
        )
        recovered = _complex_from_pair(
            record["mp_master_from_metric"], f"V2 roundtrip {sector} recovered MP"
        )
        if expected != (li if sector == "even" else 2.0j * li / k):
            raise ObservableMeasurementError(f"V2 roundtrip {sector} bridge changed")
        mp_residual = _relative_complex_error(recovered, expected)
        stored_mp = _nonnegative_finite(
            record["mp_metric_roundtrip_relative_residual"],
            f"V2 roundtrip {sector} MP residual",
        )
        direct_residual = _nonnegative_finite(
            record["direct_li_metric_roundtrip_relative_residual"],
            f"V2 roundtrip {sector} Li residual",
        )
        if stored_mp != mp_residual:
            raise ObservableMeasurementError(
                f"V2 roundtrip {sector} MP residual is not derived"
            )
        residuals.extend((stored_mp, direct_residual))
        components = record["metric_components"]
        expected_components = (
            {"T0", "Rt", "L0", "tt"} if sector == "even" else {"Bt", "B1"}
        )
        if (
            not isinstance(components, Mapping)
            or set(components) != expected_components
        ):
            raise ObservableMeasurementError(
                f"V2 roundtrip {sector} metric inventory changed"
            )
        for name, component in components.items():
            _complex_from_pair(component, f"V2 roundtrip {sector} metric {name}")
    if float(roundtrip["maximum_relative_residual"]) != max(residuals):
        raise ObservableMeasurementError("V2 maximum roundtrip residual is not derived")


def _validate_v3_measurements(value: Mapping[str, object]) -> None:
    fields = {
        "conditioned_backend",
        "phase_definition",
        "transmission_definition",
        "absorption_transmission_definition",
        "low_frequency",
        "high_frequency",
        "glory",
        "series_reduction",
        "parity",
        "radial_mode_count",
        "radial_records",
    }
    item = _exact(value, fields, "V3 measurements")
    if (
        item["conditioned_backend"] != "scipy_float64_conditioned_radial_v1"
        or item["transmission_definition"]
        != "direct conditioned horizon amplitude squared"
    ):
        raise ObservableMeasurementError("V3 backend/transmission route changed")
    _required_text(
        item["absorption_transmission_definition"],
        "V3 absorption transmission definition",
    )
    _required_text(item["phase_definition"], "V3 phase definition")
    low = _exact(
        item["low_frequency"],
        {
            "kM",
            "ell_range",
            "theta",
            "computed_cross_section_over_M2",
            "analytic_cross_section_over_M2",
            "maximum_relative_difference",
            "absorption_cross_section_over_M2",
            "maximum_flux_residual",
            "maximum_transmission_bound_correction",
        },
        "V3 low-frequency measurements",
    )
    high = _exact(
        item["high_frequency"],
        {
            "kM",
            "ell_range",
            "absorption_cross_section_over_M2",
            "geometric_limit_27pi",
            "relative_difference_to_27pi",
            "maximum_flux_residual",
            "maximum_transmission_bound_correction",
        },
        "V3 high-frequency measurements",
    )
    for label, record in (("low", low), ("high", high)):
        _positive_finite(record["kM"], f"V3 {label} kM")
        ell_range = record["ell_range"]
        if (
            not isinstance(ell_range, list)
            or len(ell_range) != 2
            or ell_range[0] != 2
            or isinstance(ell_range[1], bool)
            or not isinstance(ell_range[1], int)
            or ell_range[1] < 2
        ):
            raise ObservableMeasurementError(f"V3 {label} ell range changed")
        _nonnegative_finite(record["maximum_flux_residual"], f"V3 {label} flux")
        _nonnegative_finite(
            record["maximum_transmission_bound_correction"],
            f"V3 {label} transmission projection",
        )
    theta = low["theta"]
    computed = low["computed_cross_section_over_M2"]
    analytic = low["analytic_cross_section_over_M2"]
    if not all(isinstance(series, list) for series in (theta, computed, analytic)):
        raise ObservableMeasurementError("V3 low-frequency arrays changed")
    if not theta or len(theta) != len(computed) or len(theta) != len(analytic):
        raise ObservableMeasurementError("V3 low-frequency array lengths changed")
    for label, series in (
        ("theta", theta),
        ("computed", computed),
        ("analytic", analytic),
    ):
        for index, number in enumerate(series):
            _nonnegative_finite(number, f"V3 low {label}[{index}]")
    for label, number in (
        ("low relative difference", low["maximum_relative_difference"]),
        ("low absorption", low["absorption_cross_section_over_M2"]),
        ("high absorption", high["absorption_cross_section_over_M2"]),
        ("27pi", high["geometric_limit_27pi"]),
        ("high relative difference", high["relative_difference_to_27pi"]),
    ):
        _nonnegative_finite(number, f"V3 {label}")
    glory = _exact(
        item["glory"],
        {
            "kM",
            "ell_range",
            "semiclassical_peak_theta",
            "semiclassical_backward_offset",
            "selected_radial_peak_theta",
            "selected_radial_backward_offset",
            "absolute_offset_difference",
            "selected_reduction_order",
            "applicability",
            "maximum_flux_residual",
            "maximum_transmission_bound_correction",
        },
        "V3 glory measurements",
    )
    _positive_finite(glory["kM"], "V3 glory kM")
    glory_ell_range = glory["ell_range"]
    if (
        not isinstance(glory_ell_range, list)
        or len(glory_ell_range) != 2
        or glory_ell_range[0] != 2
        or isinstance(glory_ell_range[1], bool)
        or not isinstance(glory_ell_range[1], int)
        or glory_ell_range[1] < 5
    ):
        raise ObservableMeasurementError("V3 glory ell range changed")
    for name in (
        "semiclassical_peak_theta",
        "semiclassical_backward_offset",
        "selected_radial_peak_theta",
        "selected_radial_backward_offset",
        "absolute_offset_difference",
        "maximum_flux_residual",
        "maximum_transmission_bound_correction",
    ):
        _nonnegative_finite(glory[name], f"V3 glory {name}")
    if glory["selected_reduction_order"] != 2:
        raise ObservableMeasurementError("V3 selected glory reduction order changed")
    _required_text(glory["applicability"], "V3 glory applicability")
    reduction = _exact(
        item["series_reduction"],
        {"orders", "common_target_lmax", "theta_range", "relative_differences"},
        "V3 series-reduction measurements",
    )
    if reduction["orders"] != [0, 1, 2]:
        raise ObservableMeasurementError("V3 series-reduction orders changed")
    if (
        isinstance(reduction["common_target_lmax"], bool)
        or not isinstance(reduction["common_target_lmax"], int)
        or reduction["common_target_lmax"] < 2
    ):
        raise ObservableMeasurementError("V3 common target lmax changed")
    if (
        not isinstance(reduction["theta_range"], list)
        or len(reduction["theta_range"]) != 2
    ):
        raise ObservableMeasurementError("V3 reduction theta range changed")
    for index, number in enumerate(reduction["theta_range"]):
        _nonnegative_finite(number, f"V3 reduction theta[{index}]")
    deltas = reduction["relative_differences"]
    if not isinstance(deltas, Mapping) or set(deltas) != {"q0_vs_q2", "q1_vs_q2"}:
        raise ObservableMeasurementError("V3 reduction comparison inventory changed")
    for name, number in deltas.items():
        _nonnegative_finite(number, f"V3 reduction {name}")
    parity = _exact(
        item["parity"],
        {
            "maximum_exact_relation_residual",
            "even_sector_independently_integrated",
            "even_not_parity_derived",
        },
        "V3 parity measurements",
    )
    if (
        parity["even_sector_independently_integrated"] is not True
        or parity["even_not_parity_derived"] is not True
    ):
        raise ObservableMeasurementError("V3 even-sector independence changed")
    _nonnegative_finite(parity["maximum_exact_relation_residual"], "V3 parity residual")
    records = item["radial_records"]
    count = item["radial_mode_count"]
    if (
        isinstance(count, bool)
        or not isinstance(count, int)
        or not isinstance(records, list)
        or len(records) != count
        or count < 1
    ):
        raise ObservableMeasurementError("V3 radial mode inventory changed")
    identities: set[tuple[float, str, int]] = set()
    record_by_identity: dict[tuple[float, str, int], Mapping[str, object]] = {}
    for index, record_value in enumerate(records):
        record = _exact(
            record_value,
            {
                "kM",
                "sector",
                "ell",
                "phase_factor",
                "reflection_probability",
                "horizon_transmission_probability",
                "absorption_transmission_probability",
                "transmission_bound_correction",
                "flux_residual",
                "outer_boundary_residual",
                "match_condition_number",
                "match_condition_number_censored_at_float_max",
                "actual_precision_bits",
                "outer_basis",
                "outer_series_order",
                "integration_status",
                "paper_specific_envelope_used",
            },
            f"V3 radial record {index}",
        )
        if (
            record["sector"] not in {Sector.ODD.value, Sector.EVEN.value}
            or isinstance(record["ell"], bool)
            or not isinstance(record["ell"], int)
            or record["ell"] < 2
            or record["actual_precision_bits"] != 53
            or record["outer_basis"] != "jost_1_over_r"
            or isinstance(record["outer_series_order"], bool)
            or not isinstance(record["outer_series_order"], int)
            or record["outer_series_order"] < 2
            or not isinstance(
                record["match_condition_number_censored_at_float_max"], bool
            )
            or record["paper_specific_envelope_used"] is not False
        ):
            raise ObservableMeasurementError(f"V3 radial record {index} route changed")
        key = (float(record["kM"]), str(record["sector"]), int(record["ell"]))
        if key in identities:
            raise ObservableMeasurementError("V3 radial mode inventory has duplicates")
        identities.add(key)
        record_by_identity[key] = record
        _positive_finite(record["kM"], f"V3 radial record {index} kM")
        _complex_from_pair(record["phase_factor"], f"V3 radial record {index} phase")
        for name in (
            "reflection_probability",
            "horizon_transmission_probability",
            "absorption_transmission_probability",
            "transmission_bound_correction",
            "flux_residual",
            "outer_boundary_residual",
            "match_condition_number",
        ):
            _nonnegative_finite(record[name], f"V3 radial record {index} {name}")
        _required_text(
            record["integration_status"],
            f"V3 radial record {index} integration status",
        )
        projected = float(record["absorption_transmission_probability"])
        raw = float(record["horizon_transmission_probability"])
        correction = float(record["transmission_bound_correction"])
        if (
            not 0.0 <= projected <= 1.0
            or projected != float(np.clip(raw, 0.0, 1.0))
            or correction != abs(projected - raw)
        ):
            raise ObservableMeasurementError(
                f"V3 radial record {index} transmission projection is not derived"
            )
        if float(record["flux_residual"]) != abs(
            float(record["reflection_probability"]) + raw - 1.0
        ):
            raise ObservableMeasurementError(
                f"V3 radial record {index} flux residual is not derived"
            )

    blocks = (
        (low, "low"),
        (high, "high"),
        (glory, "glory"),
    )
    expected_identities: set[tuple[float, str, int]] = set()
    for block, label in blocks:
        frequency = float(block["kM"])
        ell_max = int(block["ell_range"][1])
        block_records = []
        for sector in (Sector.ODD.value, Sector.EVEN.value):
            for ell in range(2, ell_max + 1):
                identity = (frequency, sector, ell)
                expected_identities.add(identity)
                if identity not in record_by_identity:
                    raise ObservableMeasurementError(
                        f"V3 {label} radial domain is incomplete"
                    )
                block_records.append(record_by_identity[identity])
        maximum_flux = max(float(record["flux_residual"]) for record in block_records)
        maximum_correction = max(
            float(record["transmission_bound_correction"]) for record in block_records
        )
        if (
            float(block["maximum_flux_residual"]) != maximum_flux
            or float(block["maximum_transmission_bound_correction"])
            != maximum_correction
        ):
            raise ObservableMeasurementError(f"V3 {label} aggregate is not derived")
    if identities != expected_identities:
        raise ObservableMeasurementError("V3 radial domain has extra modes")

    low_computed = np.asarray(low["computed_cross_section_over_M2"], dtype=float)
    low_analytic = np.asarray(low["analytic_cross_section_over_M2"], dtype=float)
    low_relative = float(
        np.max(
            np.abs(low_computed - low_analytic)
            / np.maximum(low_analytic, np.finfo(float).tiny)
        )
    )
    if float(low["maximum_relative_difference"]) != low_relative:
        raise ObservableMeasurementError("V3 low-frequency residual is not derived")
    geometric = float(high["geometric_limit_27pi"])
    high_relative = (
        abs(float(high["absorption_cross_section_over_M2"]) - geometric) / geometric
    )
    if float(high["relative_difference_to_27pi"]) != high_relative:
        raise ObservableMeasurementError("V3 high-frequency residual is not derived")
    glory_offset = abs(
        float(glory["selected_radial_backward_offset"])
        - float(glory["semiclassical_backward_offset"])
    )
    if float(glory["absolute_offset_difference"]) != glory_offset:
        raise ObservableMeasurementError("V3 glory offset residual is not derived")

    glory_frequency = float(glory["kM"])
    ell_values = np.arange(2, int(glory["ell_range"][1]) + 1, dtype=float)
    even = np.asarray(
        [
            _complex_from_pair(
                record_by_identity[(glory_frequency, Sector.EVEN.value, int(ell))][
                    "phase_factor"
                ],
                f"V3 parity even ell={int(ell)}",
            )
            for ell in ell_values
        ]
    )
    odd = np.asarray(
        [
            _complex_from_pair(
                record_by_identity[(glory_frequency, Sector.ODD.value, int(ell))][
                    "phase_factor"
                ],
                f"V3 parity odd ell={int(ell)}",
            )
            for ell in ell_values
        ]
    )
    sigma = (ell_values - 1.0) * ell_values * (ell_values + 1.0) * (ell_values + 2.0)
    exact_ratio = (sigma + 12.0j * glory_frequency) / (sigma - 12.0j * glory_frequency)
    parity_residual = float(np.max(np.abs(even / odd - exact_ratio)))
    if float(parity["maximum_exact_relation_residual"]) != parity_residual:
        raise ObservableMeasurementError("V3 parity residual is not derived")


def _validate_v4_measurements(value: Mapping[str, object]) -> None:
    fields = {
        "records",
        "maximum_operational_residual",
        "maximum_metric_curvature_consistency_residual",
        "maximum_tetrad_orthonormality_residual",
        "maximum_frame_transport_residual",
        "gauge_family",
        "finite_arm_worldline_integration_performed",
    }
    item = _exact(value, fields, "V4 measurements")
    if item["finite_arm_worldline_integration_performed"] is not False:
        raise ObservableMeasurementError("V4 finite-arm completion claim changed")
    _required_text(item["gauge_family"], "V4 gauge family")
    records = item["records"]
    if not isinstance(records, list) or len(records) != 2:
        raise ObservableMeasurementError("V4 observer inventory changed")
    expected_observers = {"static_schwarzschild", "radial_freefall_E1"}
    observed: set[str] = set()
    for index, record_value in enumerate(records):
        record = _exact(
            record_value,
            {
                "observer",
                "worldline",
                "tetrad_transport",
                "transport_law_evaluated",
                "four_acceleration",
                "spatial_leg_transport_residuals",
                "acceleration_norm",
                "maximum_transport_residual",
                "tetrad_orthonormality_residual",
                "metric_perturbation_norm",
                "linearized_riemann_norm",
                "tetrad_perturbation_norm",
                "metric_curvature_consistency_residual",
                "coordinate_lie_term",
                "worldline_pullback",
                "operational_residual",
                "pipeline",
            },
            f"V4 observer record {index}",
        )
        observed.add(_required_text(record["observer"], f"V4 observer {index}"))
        for name in (
            "worldline",
            "tetrad_transport",
            "transport_law_evaluated",
            "pipeline",
        ):
            _required_text(record[name], f"V4 observer {index} {name}")
        metric_norm = _positive_finite(
            record["metric_perturbation_norm"], f"V4 observer {index} metric norm"
        )
        curvature_norm = _positive_finite(
            record["linearized_riemann_norm"],
            f"V4 observer {index} curvature norm",
        )
        tetrad_norm = _positive_finite(
            record["tetrad_perturbation_norm"], f"V4 observer {index} tetrad norm"
        )
        del metric_norm, curvature_norm, tetrad_norm
        for name in (
            "tetrad_orthonormality_residual",
            "metric_curvature_consistency_residual",
            "operational_residual",
        ):
            _nonnegative_finite(record[name], f"V4 observer {index} {name}")
        coordinate = _complex_from_pair(
            record["coordinate_lie_term"], f"V4 observer {index} coordinate term"
        )
        pullback = _complex_from_pair(
            record["worldline_pullback"], f"V4 observer {index} worldline pullback"
        )
        if abs(coordinate) == 0.0 or abs(pullback) == 0.0:
            raise ObservableMeasurementError("V4 pure-gauge route became trivial")
        acceleration = np.asarray(record["four_acceleration"], dtype=float)
        transport_residuals = np.asarray(
            record["spatial_leg_transport_residuals"], dtype=float
        )
        if (
            acceleration.shape != (4,)
            or transport_residuals.shape != (3, 4)
            or not np.all(np.isfinite(acceleration))
            or not np.all(np.isfinite(transport_residuals))
        ):
            raise ObservableMeasurementError("V4 transport arithmetic is malformed")
        acceleration_norm = _nonnegative_finite(
            record["acceleration_norm"], f"V4 observer {index} acceleration norm"
        )
        transport_maximum = _nonnegative_finite(
            record["maximum_transport_residual"],
            f"V4 observer {index} transport residual",
        )
        if transport_maximum != float(np.max(np.abs(transport_residuals))):
            raise ObservableMeasurementError("V4 transport residual is not derived")
        if record["observer"] == "static_schwarzschild" and acceleration_norm <= 0.0:
            raise ObservableMeasurementError("V4 static acceleration became trivial")
    if observed != expected_observers:
        raise ObservableMeasurementError("V4 observer labels changed")
    derived_maxima = {
        "maximum_operational_residual": max(
            float(record["operational_residual"]) for record in records
        ),
        "maximum_metric_curvature_consistency_residual": max(
            float(record["metric_curvature_consistency_residual"]) for record in records
        ),
        "maximum_tetrad_orthonormality_residual": max(
            float(record["tetrad_orthonormality_residual"]) for record in records
        ),
        "maximum_frame_transport_residual": max(
            float(record["maximum_transport_residual"]) for record in records
        ),
    }
    for name in (
        "maximum_operational_residual",
        "maximum_metric_curvature_consistency_residual",
        "maximum_tetrad_orthonormality_residual",
        "maximum_frame_transport_residual",
    ):
        _nonnegative_finite(item[name], f"V4 {name}")
        if float(item[name]) != derived_maxima[name]:
            raise ObservableMeasurementError(f"V4 {name} is not derived")


def _validate_v5_measurements(value: Mapping[str, object]) -> None:
    fields = {
        "kM",
        "theta",
        "azimuth",
        "radial_series_target_lmax",
        "radial_reduction_order",
        "incident_basis_rotation_rad",
        "observer_basis_rotation_rad",
        "helicity_matrix",
        "plus_incident_column",
        "cross_incident_column",
        "incident_basis_determinant",
        "transfer_matrix",
        "direct_matrix_residual",
        "singular_values",
        "trace_fdagger_f",
        "determinant",
        "helicity_mixing_power",
        "rotation_covariance_residual",
        "rotated_transfer_matrix",
        "phase_convention",
        "phase_convention_sha256",
        "field_definition",
        "production_unit_column_solves_performed",
        "column_origin",
    }
    item = _exact(value, fields, "V5 measurements")
    if (
        item["field_definition"] != "scattered"
        or item["production_unit_column_solves_performed"] is not False
        or item["radial_reduction_order"] != 2
    ):
        raise ObservableMeasurementError("V5 field/production status changed")
    _positive_finite(item["kM"], "V5 kM")
    _nonnegative_finite(item["theta"], "V5 theta")
    _nonnegative_finite(item["azimuth"], "V5 azimuth")
    for name in ("incident_basis_rotation_rad", "observer_basis_rotation_rad"):
        if isinstance(item[name], bool) or not isinstance(item[name], (int, float)):
            raise ObservableMeasurementError(f"V5 {name} must be numeric")
        if not math.isfinite(float(item[name])):
            raise ObservableMeasurementError(f"V5 {name} must be finite")
    if (
        isinstance(item["radial_series_target_lmax"], bool)
        or not isinstance(item["radial_series_target_lmax"], int)
        or item["radial_series_target_lmax"] < 2
    ):
        raise ObservableMeasurementError("V5 radial target lmax changed")
    _required_text(item["column_origin"], "V5 column origin")
    helicity = _complex_array(item["helicity_matrix"], (2, 2), "V5 helicity matrix")
    plus = _complex_array(item["plus_incident_column"], (2,), "V5 plus column")
    cross = _complex_array(item["cross_incident_column"], (2,), "V5 cross column")
    transfer = _complex_array(item["transfer_matrix"], (2, 2), "V5 transfer matrix")
    _complex_array(item["rotated_transfer_matrix"], (2, 2), "V5 rotated matrix")
    if not np.array_equal(transfer[:, 0], plus) or not np.array_equal(
        transfer[:, 1], cross
    ):
        raise ObservableMeasurementError("V5 stored response columns do not build F")
    transform = linear_to_helicity_transform()
    recomputed = transform.conj().T @ helicity @ transform
    if float(np.max(np.abs(recomputed - transfer))) != float(
        item["direct_matrix_residual"]
    ):
        raise ObservableMeasurementError("V5 direct matrix residual is not derived")
    if float(_determinant_2x2(np.eye(2, dtype=np.complex128)).real) != float(
        item["incident_basis_determinant"]
    ):
        raise ObservableMeasurementError("V5 incident basis rank changed")
    singular = item["singular_values"]
    if not isinstance(singular, list) or len(singular) != 2:
        raise ObservableMeasurementError("V5 singular-value inventory changed")
    for index, number in enumerate(singular):
        _nonnegative_finite(number, f"V5 singular value {index}")
    if min(float(number) for number in singular) <= 0.0:
        raise ObservableMeasurementError("V5 selected transfer is rank deficient")
    recomputed_singular = np.linalg.svd(transfer, compute_uv=False)
    if not np.array_equal(np.asarray(singular, dtype=float), recomputed_singular):
        raise ObservableMeasurementError("V5 singular values are not derived")
    for name in (
        "direct_matrix_residual",
        "trace_fdagger_f",
        "helicity_mixing_power",
        "rotation_covariance_residual",
    ):
        _nonnegative_finite(item[name], f"V5 {name}")
    _complex_from_pair(item["determinant"], "V5 determinant")
    if float(item["trace_fdagger_f"]) != float(
        np.trace(transfer.conj().T @ transfer).real
    ):
        raise ObservableMeasurementError("V5 trace diagnostic is not derived")
    if _complex_from_pair(
        item["determinant"], "V5 determinant"
    ) != _determinant_2x2(transfer):
        raise ObservableMeasurementError("V5 determinant is not derived")
    helicity_from_transfer = transform @ transfer @ transform.conj().T
    mixing = float(
        abs(helicity_from_transfer[0, 1]) ** 2 + abs(helicity_from_transfer[1, 0]) ** 2
    )
    if float(item["helicity_mixing_power"]) != mixing:
        raise ObservableMeasurementError("V5 helicity mixing power is not derived")
    incident_rotation = polarization_basis_rotation(
        float(item["incident_basis_rotation_rad"])
    )
    observer_rotation = polarization_basis_rotation(
        float(item["observer_basis_rotation_rad"])
    )
    expected_rotated = observer_rotation @ transfer @ incident_rotation.T
    stored_rotated = _complex_array(
        item["rotated_transfer_matrix"], (2, 2), "V5 rotated matrix"
    )
    if not np.array_equal(stored_rotated, expected_rotated):
        raise ObservableMeasurementError("V5 rotated transfer matrix is not derived")
    unit = np.eye(2, dtype=np.complex128)
    independently_rebuilt = np.column_stack(
        [
            observer_rotation
            @ (
                transform.conj().T
                @ helicity
                @ transform
                @ (incident_rotation.T @ column)
            )
            for column in unit.T
        ]
    )
    covariance = float(np.max(np.abs(stored_rotated - independently_rebuilt)))
    if float(item["rotation_covariance_residual"]) != covariance:
        raise ObservableMeasurementError(
            "V5 rotation covariance residual is not derived"
        )
    phase = item["phase_convention"]
    expected_phase = dict(AbsolutePhaseConvention().to_mapping())
    if phase != expected_phase:
        raise ObservableMeasurementError("V5 absolute phase convention changed")
    phase_hash = hashlib.sha256(
        json.dumps(phase, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if item["phase_convention_sha256"] != phase_hash:
        raise ObservableMeasurementError("V5 absolute phase hash is not derived")


def _complex_from_pair(value: object, label: str) -> complex:
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(
            isinstance(item, bool) or not isinstance(item, (int, float))
            for item in value
        )
    ):
        raise ObservableMeasurementError(f"{label} is not a complex pair")
    result = complex(float(value[0]), float(value[1]))
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise ObservableMeasurementError(f"{label} is non-finite")
    return result


def _complex_array(value: object, shape: tuple[int, ...], label: str) -> np.ndarray:
    try:
        raw = np.asarray(value, dtype=object)
    except (TypeError, ValueError) as exc:
        raise ObservableMeasurementError(f"{label} has invalid structure") from exc
    if raw.shape != shape + (2,):
        raise ObservableMeasurementError(f"{label} has invalid shape")
    result = np.empty(shape, dtype=np.complex128)
    for index in np.ndindex(shape):
        result[index] = _complex_from_pair(raw[index].tolist(), f"{label}{index}")
    return result


def _positive_finite(value: object, label: str) -> float:
    number = _nonnegative_finite(value, label)
    if number <= 0.0:
        raise ObservableMeasurementError(f"{label} must be positive")
    return number


def _validate_budget_map(value: object, names: Sequence[str], label: str) -> None:
    if not isinstance(value, Mapping) or set(value) != set(names):
        raise ObservableMeasurementError(f"{label} budget inventory changed")
    for name, record_value in value.items():
        record = _exact(
            record_value,
            {"applicability", "state", "value", "units", "reason"},
            f"{label} budget {name}",
        )
        if (
            record["applicability"] not in APPLICABILITY
            or record["state"] not in MEASUREMENT_STATES
        ):
            raise ObservableMeasurementError(
                f"{label} budget {name} state/applicability changed"
            )
        _required_text(record["units"], f"{label} budget {name} units")
        _required_text(record["reason"], f"{label} budget {name} reason")
        if record["state"] == "PARTIAL":
            _nonnegative_finite(record["value"], f"{label} budget {name} value")
        elif record["value"] is not None:
            raise ObservableMeasurementError(
                f"{label} unassessed budget {name} claims a value"
            )
        if (
            record["applicability"] == "NOT_APPLICABLE"
            and record["state"] != "NOT_ASSESSED"
        ):
            raise ObservableMeasurementError(
                f"{label} N/A budget {name} claims a result"
            )


def _validate_source_identity(value: object, label: str) -> dict[str, object]:
    item = _exact(value, {"mode", "nlink", "path", "sha256", "size"}, label)
    if (
        not isinstance(item["path"], str)
        or not isinstance(item["sha256"], str)
        or len(item["sha256"]) != 64
        or isinstance(item["mode"], bool)
        or not isinstance(item["mode"], int)
        or item["nlink"] != 1
        or isinstance(item["size"], bool)
        or not isinstance(item["size"], int)
        or item["size"] < 0
    ):
        raise ObservableMeasurementError(f"{label} identity changed")
    return dict(item)


def _validate_config_record(value: object) -> None:
    item = _exact(
        value,
        {"schema", *SelectedObservableMeasurementConfig.__dataclass_fields__},
        "measurement config",
    )
    if item["schema"] != CONFIG_SCHEMA:
        raise ObservableMeasurementError("measurement config schema changed")
    try:
        SelectedObservableMeasurementConfig(
            **{
                name: tuple(item[name]) if name == "reduction_orders" else item[name]
                for name in SelectedObservableMeasurementConfig.__dataclass_fields__
            }
        )
    except (TypeError, ValueError) as exc:
        raise ObservableMeasurementError("measurement config is invalid") from exc


def _validate_finite_json(value: object, label: str) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ObservableMeasurementError(f"{label} contains a non-finite float")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_finite_json(item, f"{label}[{index}]")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                raise ObservableMeasurementError(f"{label} contains an invalid key")
            _validate_finite_json(item, f"{label}.{key}")
        return
    raise ObservableMeasurementError(f"{label} contains an unsupported value")


def _exact(value: object, fields: set[str], label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != fields:
        raise ObservableMeasurementError(f"{label} schema changed")
    return value


def _required_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ObservableMeasurementError(f"{label} must be non-empty text")
    return value


def _nonnegative_finite(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ObservableMeasurementError(f"{label} must be numeric")
    number = float(value)
    if not math.isfinite(number) or number < 0.0:
        raise ObservableMeasurementError(f"{label} must be finite and nonnegative")
    return number


def _complex_pair(value: complex) -> list[float]:
    result = complex(value)
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise ObservableMeasurementError("complex measurement is non-finite")
    return [float(result.real), float(result.imag)]


def _relative_complex_error(value: complex, reference: complex) -> float:
    actual = complex(value)
    expected = complex(reference)
    scale = max(abs(expected), np.finfo(float).tiny)
    return float(abs(actual - expected) / scale)


def _complex_matrix(values: np.ndarray) -> list[list[list[float]]]:
    matrix = np.asarray(values, dtype=np.complex128)
    if matrix.shape != (2, 2):
        raise ObservableMeasurementError("complex transfer matrix must be 2x2")
    return [
        [_complex_pair(matrix[row, column]) for column in range(2)] for row in range(2)
    ]


def _determinant_2x2(values: np.ndarray) -> complex:
    matrix = np.asarray(values, dtype=np.complex128)
    if matrix.shape != (2, 2):
        raise ObservableMeasurementError("determinant input must be complex 2x2")
    return complex(
        matrix[0, 0] * matrix[1, 1] - matrix[0, 1] * matrix[1, 0]
    )


def _number_text(value: object) -> str:
    number = float(value)
    if not math.isfinite(number):
        raise ObservableMeasurementError("domain number must be finite")
    return np.format_float_positional(number, trim="-")


__all__ = [
    "CONFIG_SCHEMA",
    "MEASUREMENT_SCHEMA",
    "OBSERVABLE_SOURCE_LABELS",
    "SOURCE_PATHS",
    "ObservableMeasurementError",
    "SelectedObservableMeasurementConfig",
    "run_selected_observable_measurements",
    "validate_measurement_payload",
]
