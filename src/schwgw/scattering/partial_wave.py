from __future__ import annotations

import math
from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable, Literal

import numpy as np
from numpy.typing import ArrayLike
from scipy.special import spherical_jn

from schwgw.backgrounds.base import StaticSphericalBackground
from schwgw.numerics import BoundaryConfig, solve_radial_mode
from schwgw.perturbations import Sector, reconstruct_metric_mode
from schwgw.scattering.contracts import (
    ChannelSpec,
    IncidentSourceProtocol,
    ModeKey,
)
from schwgw.scattering.apparent import (
    ApparentPolarizationResult,
    apparent_polarizations_from_strict_np,
)
from schwgw.scattering.legacy_adapter import (
    LEGACY_EVEN_CHANNEL,
    LEGACY_ODD_CHANNEL,
    LegacyIncidentSourceAdapter,
    LegacyScalarRWZAdapter,
)
from schwgw.scattering.observables import (
    PolarizationResult,
    polarization_acceleration_from_packaged_scalars,
    polarization_acceleration_from_weyl,
    polarization_from_packaged_scalars,
    polarization_from_weyl,
)
from schwgw.scattering.tetrads import incident_cartesian_tetrad
from schwgw.scattering.weyl import (
    StrictNPScalars,
    WeylModeComponents,
    assemble_weyl_scalars,
    compute_packaged_polarization_scalars,
    transform_strict_np_weyl_to_incident_tetrad,
    weyl_mode_components,
)
from schwgw.waves.incident import IncidentPlaneGW
from schwgw.waves.polarizations import circular_to_linear


RadialSolver = Callable[
    [Sector, int, float, StaticSphericalBackground, BoundaryConfig | None],
    object,
]
Q011ZConjugation = Literal["linear", "literal_conjugate"]


@dataclass(frozen=True)
class _FlatBackground:
    M: float = 0.0
    name: str = "flat"

    @property
    def horizon_radius(self) -> float:
        return 0.0

    def f(self, r: ArrayLike) -> float | np.ndarray:
        return _scalar_or_array(np.ones_like(np.asarray(r, dtype=float)), r)

    def df_dr(self, r: ArrayLike) -> float | np.ndarray:
        return _scalar_or_array(np.zeros_like(np.asarray(r, dtype=float)), r)

    def r_star(self, r: ArrayLike) -> float | np.ndarray:
        return _scalar_or_array(np.asarray(r, dtype=float), r)

    def r_from_r_star(self, r_star: ArrayLike) -> float | np.ndarray:
        return _scalar_or_array(np.asarray(r_star, dtype=float), r_star)

    def drstar_dr(self, r: ArrayLike) -> float | np.ndarray:
        return _scalar_or_array(np.ones_like(np.asarray(r, dtype=float)), r)

    def asymptotic_region_hint(self, k: float, ell: int) -> float:
        if k <= 0.0:
            raise ValueError("Wave number k must be positive.")
        if ell < 2:
            raise ValueError("Radiative flat-space modes require ell >= 2.")
        return 10.0 * ell / k


def compute_polarization(
    *,
    background: StaticSphericalBackground,
    k: float,
    r: float,
    theta: float,
    phi: float,
    A_plus: complex,
    A_cross: complex,
    lmax: int,
    boundary_config: BoundaryConfig | None = None,
    radial_solver: RadialSolver = solve_radial_mode,
    mode_source: IncidentSourceProtocol | None = None,
) -> PolarizationResult:
    """Assemble finite-radius polarization from RW/Zerilli partial waves."""

    k_value = float(k)
    if k_value <= 0.0:
        raise ValueError("Wave number k must be positive.")
    if not isinstance(lmax, int):
        raise TypeError("lmax must be an integer.")
    if lmax < 2:
        raise ValueError("Partial-wave polarization extraction requires ell >= 2.")
    radius = float(r)
    if radius <= background.horizon_radius:
        raise ValueError("Partial-wave polarization extraction requires r > 2M.")

    if mode_source is None:
        return LegacyScalarRWZAdapter().compute_polarization(
            implementation=_compute_polarization_from_source,
            background=background,
            k=k_value,
            r=radius,
            theta=theta,
            phi=phi,
            A_plus=A_plus,
            A_cross=A_cross,
            lmax=lmax,
            boundary_config=boundary_config,
            radial_solver=radial_solver,
        )
    return _compute_polarization_from_source(
        background=background,
        k=k_value,
        r=radius,
        theta=theta,
        phi=phi,
        lmax=lmax,
        boundary_config=boundary_config,
        radial_solver=radial_solver,
        mode_source=mode_source,
    )


def compute_apparent_polarizations(
    *,
    background: StaticSphericalBackground,
    k: float,
    r: float,
    theta: float,
    phi: float,
    A_plus: complex,
    A_cross: complex,
    lmax: int,
    boundary_config: BoundaryConfig | None = None,
    radial_solver: RadialSolver = solve_radial_mode,
    mode_source: IncidentSourceProtocol | None = None,
) -> ApparentPolarizationResult:
    """Assemble diagnostic Fig. 7 apparent modes from strict NP scalars.

    This shares the exact radial/Weyl/tetrad assembly with
    :func:`compute_polarization`, but it does not use packaged physical
    polarization scalars and it always returns ``physical_claim=False``.
    """

    k_value = float(k)
    if k_value <= 0.0:
        raise ValueError("Wave number k must be positive.")
    if not isinstance(lmax, int):
        raise TypeError("lmax must be an integer.")
    if lmax < 2:
        raise ValueError("Partial-wave apparent-mode extraction requires ell >= 2.")
    radius = float(r)
    if radius <= background.horizon_radius:
        raise ValueError("Partial-wave apparent-mode extraction requires r > 2M.")

    if mode_source is None:
        return LegacyScalarRWZAdapter().compute_polarization(
            implementation=_compute_apparent_polarizations_from_source,
            background=background,
            k=k_value,
            r=radius,
            theta=theta,
            phi=phi,
            A_plus=A_plus,
            A_cross=A_cross,
            lmax=lmax,
            boundary_config=boundary_config,
            radial_solver=radial_solver,
        )
    return _compute_apparent_polarizations_from_source(
        background=background,
        k=k_value,
        r=radius,
        theta=theta,
        phi=phi,
        lmax=lmax,
        boundary_config=boundary_config,
        radial_solver=radial_solver,
        mode_source=mode_source,
    )


def _compute_polarization_from_source(
    *,
    background: StaticSphericalBackground,
    k: float,
    r: float,
    theta: float,
    phi: float,
    lmax: int,
    boundary_config: BoundaryConfig | None,
    radial_solver: RadialSolver,
    mode_source: IncidentSourceProtocol,
) -> PolarizationResult:
    """Execute the frozen path for one already-typed incident source."""

    k_value = k
    radius = r
    source = mode_source
    if not isinstance(source, IncidentSourceProtocol):
        raise TypeError("mode_source must satisfy IncidentSourceProtocol.")
    if (
        type(source) is LegacyIncidentSourceAdapter
        and source.wave.A_plus == 0.0
        and source.wave.A_cross == 0.0
    ):
        return _zero_result(lmax)

    strict_incident_np, diagnostics = _assemble_incident_strict_np_from_source(
        background=background,
        k=k_value,
        r=radius,
        theta=theta,
        phi=phi,
        lmax=lmax,
        boundary_config=boundary_config,
        radial_solver=radial_solver,
        mode_source=source,
    )
    packaged_scalars = compute_packaged_polarization_scalars(strict_incident_np)
    psi0_hat = packaged_scalars.psi0_pack
    psi4_hat = packaged_scalars.psi4_pack
    h_plus, h_cross = polarization_from_packaged_scalars(k_value, packaged_scalars)
    hddot_plus, hddot_cross = polarization_acceleration_from_packaged_scalars(
        packaged_scalars
    )
    return PolarizationResult(
        h_plus=h_plus,
        h_cross=h_cross,
        psi0_hat=psi0_hat,
        psi4_hat=psi4_hat,
        hddot_plus=hddot_plus,
        hddot_cross=hddot_cross,
        lmax=lmax,
        diagnostics=diagnostics,
    )


def _compute_apparent_polarizations_from_source(
    *,
    background: StaticSphericalBackground,
    k: float,
    r: float,
    theta: float,
    phi: float,
    lmax: int,
    boundary_config: BoundaryConfig | None,
    radial_solver: RadialSolver,
    mode_source: IncidentSourceProtocol,
) -> ApparentPolarizationResult:
    source = mode_source
    if not isinstance(source, IncidentSourceProtocol):
        raise TypeError("mode_source must satisfy IncidentSourceProtocol.")
    if (
        type(source) is LegacyIncidentSourceAdapter
        and source.wave.A_plus == 0.0
        and source.wave.A_cross == 0.0
    ):
        return apparent_polarizations_from_strict_np(
            k,
            StrictNPScalars(0.0j, 0.0j, 0.0j, 0.0j, 0.0j, frame="incident"),
            diagnostics=_zero_diagnostics(lmax),
        )

    strict_incident_np, diagnostics = _assemble_incident_strict_np_from_source(
        background=background,
        k=k,
        r=r,
        theta=theta,
        phi=phi,
        lmax=lmax,
        boundary_config=boundary_config,
        radial_solver=radial_solver,
        mode_source=source,
    )
    return apparent_polarizations_from_strict_np(
        k,
        strict_incident_np,
        diagnostics=diagnostics,
    )


def _assemble_incident_strict_np_from_source(
    *,
    background: StaticSphericalBackground,
    k: float,
    r: float,
    theta: float,
    phi: float,
    lmax: int,
    boundary_config: BoundaryConfig | None,
    radial_solver: RadialSolver,
    mode_source: IncidentSourceProtocol,
) -> tuple[StrictNPScalars, dict[str, float]]:
    """Return the shared strict incident-frame NP assembly and diagnostics."""

    radial_cache: dict[tuple[Sector, int], object] = {}
    radial_state_cache: dict[
        tuple[Sector, int, float],
        tuple[complex, complex, complex],
    ] = {}
    weyl_modes: list[WeylModeComponents] = []
    nonzero_coefficients = 0

    for ell in range(2, lmax + 1):
        for m in _ordered_source_m_values(mode_source, ell):
            odd_coefficient = _source_coefficient(
                mode_source,
                sector=Sector.ODD,
                ell=ell,
                m=m,
                k=k,
            )
            even_coefficient = _source_coefficient(
                mode_source,
                sector=Sector.EVEN,
                ell=ell,
                m=m,
                k=k,
            )
            if odd_coefficient != 0.0:
                nonzero_coefficients += 1
                weyl_modes.append(
                    _scaled_weyl_mode(
                        sector=Sector.ODD,
                        ell=ell,
                        m=m,
                        coefficient=odd_coefficient,
                        radial_cache=radial_cache,
                        radial_state_cache=radial_state_cache,
                        radial_solver=radial_solver,
                        boundary_config=boundary_config,
                        background=background,
                        k=k,
                        r=r,
                        theta=float(theta),
                        phi=float(phi),
                    )
                )
            if even_coefficient != 0.0:
                nonzero_coefficients += 1
                weyl_modes.append(
                    _scaled_weyl_mode(
                        sector=Sector.EVEN,
                        ell=ell,
                        m=m,
                        coefficient=even_coefficient,
                        radial_cache=radial_cache,
                        radial_state_cache=radial_state_cache,
                        radial_solver=radial_solver,
                        boundary_config=boundary_config,
                        background=background,
                        k=k,
                        r=r,
                        theta=float(theta),
                        phi=float(phi),
                    )
                )

    assembled = assemble_weyl_scalars(weyl_modes)
    incident_tetrad_weyl = transform_strict_np_weyl_to_incident_tetrad(
        assembled,
        theta=float(theta),
        phi=float(phi),
    )
    strict_incident_np = StrictNPScalars.from_mapping(
        incident_tetrad_weyl,
        frame="incident",
    )
    diagnostics = _diagnostics(
        radial_cache=radial_cache,
        lmax=lmax,
        mode_count=len(weyl_modes),
        nonzero_coefficients=nonzero_coefficients,
    )
    return strict_incident_np, diagnostics


def compute_flat_no_lens_polarization(
    *,
    k: float,
    r: float,
    theta: float,
    phi: float,
    A_plus: complex,
    A_cross: complex,
    lmax: int,
    q011_z_conjugation: Q011ZConjugation = "linear",
) -> PolarizationResult:
    """Return the M=0 no-lens oracle from direct Cartesian TT curvature."""

    k_value = float(k)
    if k_value <= 0.0:
        raise ValueError("Wave number k must be positive.")
    if not isinstance(lmax, int):
        raise TypeError("lmax must be an integer.")
    if lmax < 2:
        raise ValueError("Flat no-lens polarization extraction requires ell >= 2.")
    radius = float(r)
    if radius <= 0.0:
        raise ValueError("Flat no-lens polarization extraction requires r > 0.")
    if q011_z_conjugation not in ("linear", "literal_conjugate"):
        raise ValueError("q011_z_conjugation must be 'linear' or 'literal_conjugate'.")

    result = direct_cartesian_tt_polarization(
        k=k_value,
        z=radius * math.cos(float(theta)),
        A_plus=A_plus,
        A_cross=A_cross,
    )
    diagnostics = dict(result.diagnostics)
    diagnostics.update(
        {
            "lmax": float(lmax),
            "flat_no_lens": 1.0,
            "q011_conjugation_literal": float(q011_z_conjugation == "literal_conjugate"),
        }
    )
    return PolarizationResult(
        h_plus=result.h_plus,
        h_cross=result.h_cross,
        psi0_hat=result.psi0_hat,
        psi4_hat=result.psi4_hat,
        hddot_plus=result.hddot_plus,
        hddot_cross=result.hddot_cross,
        lmax=lmax,
        diagnostics=diagnostics,
    )


def compute_flat_no_lens_partial_wave_diagnostic(
    *,
    k: float,
    r: float,
    theta: float,
    phi: float,
    A_plus: complex,
    A_cross: complex,
    lmax: int,
    q011_z_conjugation: Q011ZConjugation = "linear",
) -> PolarizationResult:
    """Diagnostic-only M=0 assembly through T5/T6 partial-wave formulas."""

    k_value = float(k)
    if k_value <= 0.0:
        raise ValueError("Wave number k must be positive.")
    if not isinstance(lmax, int):
        raise TypeError("lmax must be an integer.")
    if lmax < 2:
        raise ValueError("Flat no-lens polarization extraction requires ell >= 2.")
    radius = float(r)
    if radius <= 0.0:
        raise ValueError("Flat no-lens polarization extraction requires r > 0.")
    if q011_z_conjugation not in ("linear", "literal_conjugate"):
        raise ValueError("q011_z_conjugation must be 'linear' or 'literal_conjugate'.")

    incident_wave = IncidentPlaneGW(k_value, A_plus, A_cross)
    if incident_wave.A_plus == 0.0 and incident_wave.A_cross == 0.0:
        result = _zero_result(lmax)
        diagnostics = dict(result.diagnostics)
        diagnostics.update(
            {
                "flat_no_lens": 1.0,
                "partial_wave_diagnostic": 1.0,
                "q011_conjugation_literal": float(q011_z_conjugation == "literal_conjugate"),
            }
        )
        return PolarizationResult(
            h_plus=result.h_plus,
            h_cross=result.h_cross,
            psi0_hat=result.psi0_hat,
            psi4_hat=result.psi4_hat,
            hddot_plus=result.hddot_plus,
            hddot_cross=result.hddot_cross,
            lmax=result.lmax,
            diagnostics=diagnostics,
        )

    packaged_weyl, assembly = _flat_packaged_weyl_from_partial_waves(
        incident_wave=incident_wave,
        k=k_value,
        radius=radius,
        theta=float(theta),
        phi=float(phi),
        lmax=lmax,
        q011_z_conjugation=q011_z_conjugation,
    )
    psi0_hat = packaged_weyl["Psi0"]
    psi4_hat = packaged_weyl["Psi4"]
    h_plus, h_cross = polarization_from_weyl(k_value, psi0_hat, psi4_hat)
    hddot_plus, hddot_cross = polarization_acceleration_from_weyl(psi0_hat, psi4_hat)
    diagnostics = {
        "lmax": float(lmax),
        "mode_count": float(assembly["mode_count"]),
        "nonzero_coefficient_count": float(assembly["nonzero_coefficients"]),
        "radial_solve_count": 0.0,
        "max_boundary_residual": 0.0,
        "max_wronskian_residual": 0.0,
        "max_match_condition_number": 0.0,
        "flat_no_lens": 1.0,
        "partial_wave_diagnostic": 1.0,
        "strict_np_bridge": 1.0,
        "q011_conjugation_literal": float(q011_z_conjugation == "literal_conjugate"),
    }
    diagnostics.update(assembly["ell_contribution_norms"])

    return PolarizationResult(
        h_plus=h_plus,
        h_cross=h_cross,
        psi0_hat=psi0_hat,
        psi4_hat=psi4_hat,
        hddot_plus=hddot_plus,
        hddot_cross=hddot_cross,
        lmax=lmax,
        diagnostics=diagnostics,
    )


def compute_flat_no_lens_partial_wave_strict_np_weyl(
    *,
    k: float,
    r: float,
    theta: float,
    phi: float,
    A_plus: complex,
    A_cross: complex,
    lmax: int,
    tetrad: Literal["kinnersley", "incident"] = "incident",
) -> dict[str, complex]:
    """Return flat diagnostic strict-NP scalars for the M=0 partial-wave bridge."""

    k_value = float(k)
    if k_value <= 0.0:
        raise ValueError("Wave number k must be positive.")
    if not isinstance(lmax, int):
        raise TypeError("lmax must be an integer.")
    if lmax < 2:
        raise ValueError("Flat no-lens strict-NP diagnostic requires ell >= 2.")
    radius = float(r)
    if radius <= 0.0:
        raise ValueError("Flat no-lens strict-NP diagnostic requires r > 0.")
    if tetrad not in ("kinnersley", "incident"):
        raise ValueError("tetrad must be 'kinnersley' or 'incident'.")

    incident_wave = IncidentPlaneGW(k_value, A_plus, A_cross)
    assembly = _assemble_flat_partial_wave_modes(
        incident_wave=incident_wave,
        k=k_value,
        radius=radius,
        theta=float(theta),
        phi=float(phi),
        lmax=lmax,
        q011_z_conjugation="linear",
    )
    completed = _complete_flat_type_n_kinnersley_weyl(
        assembly["assembled"],
        theta=float(theta),
        phi=float(phi),
    )
    if tetrad == "kinnersley":
        return completed
    return transform_strict_np_weyl_to_incident_tetrad(
        completed,
        theta=float(theta),
        phi=float(phi),
    )


def _flat_packaged_weyl_from_partial_waves(
    *,
    incident_wave: IncidentPlaneGW,
    k: float,
    radius: float,
    theta: float,
    phi: float,
    lmax: int,
    q011_z_conjugation: Q011ZConjugation,
) -> tuple[dict[str, complex], dict[str, object]]:
    right_assembly = _assemble_flat_partial_wave_modes(
        incident_wave=incident_wave,
        k=k,
        radius=radius,
        theta=theta,
        phi=phi,
        lmax=lmax,
        q011_z_conjugation=q011_z_conjugation,
    )
    right_incident = _flat_completed_incident_weyl(
        right_assembly["assembled"],
        theta=theta,
        phi=phi,
    )

    left_as_right_plus, left_as_right_cross = circular_to_linear(0.0j, incident_wave.A_L)
    left_as_right_wave = IncidentPlaneGW(
        k,
        left_as_right_plus,
        left_as_right_cross,
    )
    left_assembly = _assemble_flat_partial_wave_modes(
        incident_wave=left_as_right_wave,
        k=k,
        radius=radius,
        theta=theta,
        phi=phi,
        lmax=lmax,
        q011_z_conjugation=q011_z_conjugation,
    )
    left_incident = _flat_completed_incident_weyl(
        left_assembly["assembled"],
        theta=theta,
        phi=phi,
    )

    return (
        {
            "Psi0": 0.5 * left_incident["Psi4"],
            "Psi1": 0.0j,
            "Psi2": 0.0j,
            "Psi3": 0.0j,
            "Psi4": 0.5 * right_incident["Psi4"],
        },
        right_assembly,
    )


def _flat_completed_incident_weyl(
    kinnersley_weyl: object,
    *,
    theta: float,
    phi: float,
) -> dict[str, complex]:
    completed = _complete_flat_type_n_kinnersley_weyl(
        kinnersley_weyl,
        theta=theta,
        phi=phi,
    )
    return transform_strict_np_weyl_to_incident_tetrad(completed, theta=theta, phi=phi)


def _complete_flat_type_n_kinnersley_weyl(
    kinnersley_weyl: object,
    *,
    theta: float,
    phi: float,
) -> dict[str, complex]:
    source = dict(kinnersley_weyl)  # type: ignore[arg-type]
    upper_only = {
        "Psi0": 0.0j,
        "Psi1": 0.0j,
        "Psi2": 0.0j,
        "Psi3": source["Psi3"],
        "Psi4": source["Psi4"],
    }
    upper_incident = transform_strict_np_weyl_to_incident_tetrad(
        upper_only,
        theta=theta,
        phi=phi,
    )
    target_labels = ("Psi0", "Psi1", "Psi2", "Psi3")
    lower_labels = ("Psi0", "Psi1", "Psi2")
    matrix = np.zeros((len(target_labels), len(lower_labels)), dtype=complex)
    for col, label in enumerate(lower_labels):
        basis = {key: 0.0j for key in ("Psi0", "Psi1", "Psi2", "Psi3", "Psi4")}
        basis[label] = 1.0 + 0.0j
        transformed = transform_strict_np_weyl_to_incident_tetrad(
            basis,
            theta=theta,
            phi=phi,
        )
        for row, target_label in enumerate(target_labels):
            matrix[row, col] = transformed[target_label]

    rhs = -np.array([upper_incident[label] for label in target_labels], dtype=complex)
    lower_values, *_ = np.linalg.lstsq(matrix, rhs, rcond=1e-12)
    completed = dict(upper_only)
    for label, value in zip(lower_labels, lower_values, strict=True):
        completed[label] = complex(value)
    return completed


def _assemble_flat_partial_wave_modes(
    *,
    incident_wave: IncidentPlaneGW,
    k: float,
    radius: float,
    theta: float,
    phi: float,
    lmax: int,
    q011_z_conjugation: Q011ZConjugation,
) -> dict[str, object]:
    background = _FlatBackground()
    weyl_modes: list[WeylModeComponents] = []
    modes_by_ell: dict[int, list[WeylModeComponents]] = {ell: [] for ell in range(2, lmax + 1)}
    nonzero_coefficients = 0

    for ell in range(2, lmax + 1):
        for m in range(-ell, ell + 1):
            for sector in (Sector.ODD, Sector.EVEN):
                psi, dpsi_dr = _flat_master_and_derivative(
                    incident_wave,
                    sector,
                    ell,
                    m,
                    radius,
                )
                if psi == 0.0:
                    continue
                nonzero_coefficients += 1
                metric_mode = reconstruct_metric_mode(
                    sector,
                    ell,
                    k,
                    radius,
                    psi,
                    dpsi_dr,
                    background,
                )
                mode = weyl_mode_components(
                    sector,
                    ell,
                    m,
                    k,
                    radius,
                    theta,
                    phi,
                    metric_mode,
                    background,
                )
                adjusted_mode = _q011_adjusted_mode(mode, background, q011_z_conjugation)
                weyl_modes.append(adjusted_mode)
                modes_by_ell[ell].append(adjusted_mode)

    ell_contribution_norms = {}
    for ell, ell_modes in modes_by_ell.items():
        ell_assembled = assemble_weyl_scalars(ell_modes)
        ell_incident = transform_strict_np_weyl_to_incident_tetrad(
            ell_assembled,
            theta=theta,
            phi=phi,
        )
        ell_contribution_norms[f"ell_{ell}_contribution_norm"] = _weyl_norm(ell_incident)

    return {
        "assembled": assemble_weyl_scalars(weyl_modes),
        "mode_count": len(weyl_modes),
        "nonzero_coefficients": nonzero_coefficients,
        "ell_contribution_norms": ell_contribution_norms,
    }


def flat_no_lens_expected_polarization(
    *,
    k: float,
    r: float,
    theta: float,
    A_plus: complex,
    A_cross: complex,
) -> tuple[complex, complex]:
    """Return the direct incident plane-wave polarization at an M=0 probe."""

    k_value = float(k)
    radius = float(r)
    if k_value <= 0.0:
        raise ValueError("Wave number k must be positive.")
    if radius <= 0.0:
        raise ValueError("Flat no-lens expected polarization requires r > 0.")
    phase = np.exp(1.0j * k_value * radius * math.cos(float(theta)))
    return complex(A_plus) * phase, complex(A_cross) * phase


def direct_cartesian_tt_weyl(
    *,
    k: float,
    z: float,
    A_plus: complex,
    A_cross: complex,
) -> dict[str, complex]:
    """Compatibility alias returning packaged flat Cartesian TT scalars."""

    return direct_cartesian_tt_packaged_weyl(
        k=k,
        z=z,
        A_plus=A_plus,
        A_cross=A_cross,
    )


def direct_cartesian_tt_packaged_weyl(
    *,
    k: float,
    z: float,
    A_plus: complex,
    A_cross: complex,
) -> dict[str, complex]:
    """Return packaged flat Cartesian TT scalars for polarization recovery."""

    k_value = float(k)
    if k_value <= 0.0:
        raise ValueError("Wave number k must be positive.")

    phase = np.exp(1.0j * k_value * float(z))
    h = np.zeros((4, 4), dtype=complex)
    h[1, 1] = complex(A_plus) * phase
    h[2, 2] = -complex(A_plus) * phase
    h[1, 2] = complex(A_cross) * phase
    h[2, 1] = complex(A_cross) * phase

    covector = np.array([-k_value, 0.0, 0.0, k_value], dtype=complex)
    second_derivatives = -np.einsum("m,n,ab->abmn", covector, covector, h)
    riemann = _linearized_riemann_from_second_derivatives(second_derivatives)

    tetrad = incident_cartesian_tetrad()
    time_leg = (tetrad.legs["l"] + tetrad.legs["n"]) / np.sqrt(2.0)
    x_leg = (tetrad.legs["m"] + tetrad.legs["mbar"]) / np.sqrt(2.0)
    y_leg = (tetrad.legs["m"] - tetrad.legs["mbar"]) / (1.0j * np.sqrt(2.0))

    r_txtx = _contract_riemann(riemann, time_leg, x_leg, time_leg, x_leg)
    r_txty = _contract_riemann(riemann, time_leg, x_leg, time_leg, y_leg)

    # Eq. (41)-(42) use the electric tidal projections packaged as Psi0/Psi4.
    psi4 = -r_txtx + 1.0j * r_txty
    psi0 = -r_txtx - 1.0j * r_txty
    return {
        "Psi0": complex(psi0),
        "Psi1": 0.0j,
        "Psi2": 0.0j,
        "Psi3": 0.0j,
        "Psi4": complex(psi4),
    }


def direct_cartesian_tt_strict_np_weyl(
    *,
    k: float,
    z: float,
    A_plus: complex,
    A_cross: complex,
    tetrad: MappingProxyType | dict[str, np.ndarray] | None = None,
) -> dict[str, complex]:
    """Return strict NP Weyl scalars for a flat Cartesian TT wave."""

    k_value = float(k)
    if k_value <= 0.0:
        raise ValueError("Wave number k must be positive.")

    phase = np.exp(1.0j * k_value * float(z))
    h = np.zeros((4, 4), dtype=complex)
    h[1, 1] = complex(A_plus) * phase
    h[2, 2] = -complex(A_plus) * phase
    h[1, 2] = complex(A_cross) * phase
    h[2, 1] = complex(A_cross) * phase

    covector = np.array([-k_value, 0.0, 0.0, k_value], dtype=complex)
    second_derivatives = -np.einsum("m,n,ab->abmn", covector, covector, h)
    riemann = _linearized_riemann_from_second_derivatives(second_derivatives)

    legs = incident_cartesian_tetrad().legs if tetrad is None else tetrad
    l_leg = legs["l"]
    n_leg = legs["n"]
    m_leg = legs["m"]
    mbar_leg = legs["mbar"]
    return {
        "Psi0": -_contract_riemann(riemann, l_leg, m_leg, l_leg, m_leg),
        "Psi1": -_contract_riemann(riemann, l_leg, n_leg, l_leg, m_leg),
        "Psi2": -_contract_riemann(riemann, l_leg, m_leg, n_leg, mbar_leg),
        "Psi3": -_contract_riemann(riemann, l_leg, n_leg, n_leg, mbar_leg),
        "Psi4": -_contract_riemann(riemann, n_leg, mbar_leg, n_leg, mbar_leg),
    }


def direct_cartesian_tt_polarization(
    *,
    k: float,
    z: float,
    A_plus: complex,
    A_cross: complex,
) -> PolarizationResult:
    """Recover polarizations from a direct flat Cartesian TT curvature oracle."""

    weyl_scalars = direct_cartesian_tt_weyl(
        k=k,
        z=z,
        A_plus=A_plus,
        A_cross=A_cross,
    )
    h_plus, h_cross = polarization_from_weyl(k, weyl_scalars["Psi0"], weyl_scalars["Psi4"])
    hddot_plus, hddot_cross = polarization_acceleration_from_weyl(
        weyl_scalars["Psi0"],
        weyl_scalars["Psi4"],
    )
    return PolarizationResult(
        h_plus=h_plus,
        h_cross=h_cross,
        psi0_hat=weyl_scalars["Psi0"],
        psi4_hat=weyl_scalars["Psi4"],
        hddot_plus=hddot_plus,
        hddot_cross=hddot_cross,
        lmax=0,
        diagnostics={"direct_cartesian_tt": 1.0, "radial_solve_count": 0.0},
    )


def _ordered_source_m_values(
    source: IncidentSourceProtocol,
    ell: int,
) -> tuple[int, ...] | range:
    declared = source.supported_m_values(ell)
    if declared is None:
        return range(-ell, ell + 1)
    if not isinstance(declared, tuple):
        raise TypeError("supported_m_values must return a tuple or None.")

    seen: set[int] = set()
    for m in declared:
        if isinstance(m, bool) or not isinstance(m, int):
            raise TypeError("supported m values must be integers.")
        if abs(m) > ell:
            raise ValueError("supported m values must satisfy abs(m) <= ell.")
        if m in seen:
            raise ValueError("supported m values must be unique.")
        seen.add(m)
    return declared


def _source_coefficient(
    source: IncidentSourceProtocol,
    *,
    sector: Sector,
    ell: int,
    m: int,
    k: float,
) -> complex:
    if type(source) is LegacyIncidentSourceAdapter:
        if source.wave.k != k:
            raise ValueError(
                "legacy source frequency does not match the polarization request."
            )
        return source.coefficient(sector, ell, m)

    channel = LEGACY_ODD_CHANNEL if sector is Sector.ODD else LEGACY_EVEN_CHANNEL
    mode = ModeKey(
        frequency=k,
        ell=ell,
        m=m,
        channel=channel.name,
    )
    return _scalar_source_amplitude(source, mode=mode, channel=channel)


def _scalar_source_amplitude(
    source: IncidentSourceProtocol,
    *,
    mode: ModeKey,
    channel: ChannelSpec,
) -> complex:
    raw = source.amplitude(mode, channel)
    values = np.asarray(raw)
    if values.shape != (1,):
        raise ValueError(
            "scalar legacy channels require source amplitude shape (1,)."
        )
    if not np.iscomplexobj(values):
        raise TypeError("source amplitude must be complex.")
    value = complex(values.reshape(-1)[0])
    if not np.isfinite(value.real) or not np.isfinite(value.imag):
        raise RuntimeError("source amplitude must be finite.")
    return value


def _scaled_weyl_mode(
    *,
    sector: Sector,
    ell: int,
    m: int,
    coefficient: complex,
    radial_cache: dict[tuple[Sector, int], object],
    radial_state_cache: dict[
        tuple[Sector, int, float],
        tuple[complex, complex, complex],
    ],
    radial_solver: RadialSolver,
    boundary_config: BoundaryConfig | None,
    background: StaticSphericalBackground,
    k: float,
    r: float,
    theta: float,
    phi: float,
):
    A_in, psi_at_radius, dpsi_dr_at_radius = _radial_state_at_point(
        sector=sector,
        ell=ell,
        radial_cache=radial_cache,
        radial_state_cache=radial_state_cache,
        radial_solver=radial_solver,
        boundary_config=boundary_config,
        background=background,
        k=k,
        r=r,
    )
    scale = coefficient / A_in
    psi = scale * psi_at_radius
    dpsi_dr = scale * dpsi_dr_at_radius
    metric_mode = reconstruct_metric_mode(sector, ell, k, r, psi, dpsi_dr, background)
    return weyl_mode_components(sector, ell, m, k, r, theta, phi, metric_mode, background)


def _radial_state_at_point(
    *,
    sector: Sector,
    ell: int,
    radial_cache: dict[tuple[Sector, int], object],
    radial_state_cache: dict[
        tuple[Sector, int, float],
        tuple[complex, complex, complex],
    ],
    radial_solver: RadialSolver,
    boundary_config: BoundaryConfig | None,
    background: StaticSphericalBackground,
    k: float,
    r: float,
) -> tuple[complex, complex, complex]:
    key = (sector, ell, float(r))
    if key not in radial_state_cache:
        solution = _radial_solution(
            sector=sector,
            ell=ell,
            radial_cache=radial_cache,
            radial_solver=radial_solver,
            boundary_config=boundary_config,
            background=background,
            k=k,
        )
        A_in = complex(getattr(solution, "A_in"))
        if abs(A_in) <= np.finfo(float).eps:
            raise RuntimeError(
                "Radial solution has near-zero A_in for "
                f"sector={sector.value}, ell={ell}."
            )
        radial_state_cache[key] = (
            A_in,
            complex(solution.psi_at(r)),
            complex(solution.dpsi_dr_at(r)),
        )
    return radial_state_cache[key]


def _radial_solution(
    *,
    sector: Sector,
    ell: int,
    radial_cache: dict[tuple[Sector, int], object],
    radial_solver: RadialSolver,
    boundary_config: BoundaryConfig | None,
    background: StaticSphericalBackground,
    k: float,
) -> object:
    key = (sector, ell)
    if key not in radial_cache:
        radial_cache[key] = radial_solver(sector, ell, k, background, boundary_config)
    return radial_cache[key]


def _flat_master_and_derivative(
    incident_wave: IncidentPlaneGW,
    sector: Sector,
    ell: int,
    m: int,
    r: float,
) -> tuple[complex, complex]:
    x = incident_wave.k * r
    j_ell = spherical_jn(ell, x)
    dj_ell = spherical_jn(ell, x, derivative=True)
    radial_factor = j_ell + x * dj_ell

    if sector is Sector.ODD:
        amplitude = incident_wave.A_lm_minus(ell, m)
        return (
            complex(-incident_wave.k * r * amplitude * j_ell),
            complex(-incident_wave.k * amplitude * radial_factor),
        )

    amplitude = incident_wave.A_lm_plus(ell, m)
    return (
        complex(2.0 * r * amplitude * j_ell),
        complex(2.0 * amplitude * radial_factor),
    )


def _q011_adjusted_mode(
    mode: WeylModeComponents,
    background: StaticSphericalBackground,
    q011_z_conjugation: Q011ZConjugation,
) -> WeylModeComponents:
    if q011_z_conjugation == "linear":
        return mode

    f = float(background.f(mode.r))
    radial_sources = dict(mode.radial_sources)
    radial_sources["Z1"] = (2.0 / f) * np.conjugate(radial_sources["Z3"])
    radial_sources["Z0"] = (2.0 / f) ** 2 * np.conjugate(radial_sources["Z4"])

    components = dict(mode.components)
    components["Psi1"] = (
        math.sqrt(2.0 * mode.ell * (mode.ell + 1))
        * radial_sources["Z1"]
        * mode.angular_factors["Psi1"]
    )
    components["Psi0"] = (
        math.sqrt(_sigma_l(mode.ell))
        * radial_sources["Z0"]
        * mode.angular_factors["Psi0"]
    )

    return WeylModeComponents(
        sector=mode.sector,
        ell=mode.ell,
        m=mode.m,
        k=mode.k,
        r=mode.r,
        theta=mode.theta,
        phi=mode.phi,
        components=MappingProxyType(components),
        spin_weights=mode.spin_weights,
        angular_factors=mode.angular_factors,
        radial_sources=MappingProxyType(radial_sources),
    )


def _linearized_riemann_from_second_derivatives(
    second_derivatives: np.ndarray,
) -> np.ndarray:
    return 0.5 * (
        np.einsum("adbc->abcd", second_derivatives)
        + np.einsum("bcad->abcd", second_derivatives)
        - np.einsum("acbd->abcd", second_derivatives)
        - np.einsum("bdac->abcd", second_derivatives)
    )


def _contract_riemann(
    riemann: np.ndarray,
    first: np.ndarray,
    second: np.ndarray,
    third: np.ndarray,
    fourth: np.ndarray,
) -> complex:
    return complex(np.einsum("abcd,a,b,c,d->", riemann, first, second, third, fourth))


def _flat_kinnersley_cartesian_legs(theta: float, phi: float) -> dict[str, np.ndarray]:
    radial = np.array(
        [
            math.sin(theta) * math.cos(phi),
            math.sin(theta) * math.sin(phi),
            math.cos(theta),
        ],
        dtype=complex,
    )
    theta_leg = np.array(
        [
            math.cos(theta) * math.cos(phi),
            math.cos(theta) * math.sin(phi),
            -math.sin(theta),
        ],
        dtype=complex,
    )
    phi_leg = np.array([-math.sin(phi), math.cos(phi), 0.0], dtype=complex)
    m_leg = np.concatenate([[0.0j], (theta_leg + 1.0j * phi_leg) / math.sqrt(2.0)])
    return {
        "l": np.concatenate([[1.0 + 0.0j], radial]),
        "n": 0.5 * np.concatenate([[1.0 + 0.0j], -radial]),
        "m": m_leg,
        "mbar": np.conjugate(m_leg),
    }


def _diagnostics(
    *,
    radial_cache: dict[tuple[Sector, int], object],
    lmax: int,
    mode_count: int,
    nonzero_coefficients: int,
) -> dict[str, float]:
    boundary_residuals = []
    wronskian_residuals = []
    condition_numbers = []
    for solution in radial_cache.values():
        diagnostics = getattr(solution, "diagnostics", None)
        boundary_residuals.append(float(getattr(diagnostics, "boundary_residual", 0.0)))
        wronskian_residuals.append(float(getattr(diagnostics, "wronskian_residual", 0.0)))
        condition_numbers.append(float(getattr(diagnostics, "match_condition_number", 0.0)))

    return {
        "lmax": float(lmax),
        "mode_count": float(mode_count),
        "nonzero_coefficient_count": float(nonzero_coefficients),
        "radial_solve_count": float(len(radial_cache)),
        "max_boundary_residual": max(boundary_residuals, default=0.0),
        "max_wronskian_residual": max(wronskian_residuals, default=0.0),
        "max_match_condition_number": max(condition_numbers, default=0.0),
    }


def _weyl_norm(weyl_scalars: dict[str, complex]) -> float:
    return float(
        np.linalg.norm(
            [
                weyl_scalars["Psi0"],
                weyl_scalars["Psi1"],
                weyl_scalars["Psi2"],
                weyl_scalars["Psi3"],
                weyl_scalars["Psi4"],
            ]
        )
    )


def _zero_result(lmax: int) -> PolarizationResult:
    return PolarizationResult(
        h_plus=0.0j,
        h_cross=0.0j,
        psi0_hat=0.0j,
        psi4_hat=0.0j,
        hddot_plus=0.0j,
        hddot_cross=0.0j,
        lmax=lmax,
        diagnostics=_zero_diagnostics(lmax),
    )


def _zero_diagnostics(lmax: int) -> dict[str, float]:
    return {
        "lmax": float(lmax),
        "mode_count": 0.0,
        "nonzero_coefficient_count": 0.0,
        "radial_solve_count": 0.0,
        "max_boundary_residual": 0.0,
        "max_wronskian_residual": 0.0,
        "max_match_condition_number": 0.0,
    }


def _sigma_l(ell: int) -> int:
    return (ell - 1) * ell * (ell + 1) * (ell + 2)


def _scalar_or_array(values: np.ndarray, original: ArrayLike) -> float | np.ndarray:
    if np.isscalar(original) or np.asarray(original).ndim == 0:
        return float(values)
    return values


__all__ = [
    "compute_apparent_polarizations",
    "PolarizationResult",
    "compute_flat_no_lens_polarization",
    "compute_flat_no_lens_partial_wave_diagnostic",
    "compute_flat_no_lens_partial_wave_strict_np_weyl",
    "compute_polarization",
    "direct_cartesian_tt_packaged_weyl",
    "direct_cartesian_tt_polarization",
    "direct_cartesian_tt_strict_np_weyl",
    "direct_cartesian_tt_weyl",
    "flat_no_lens_expected_polarization",
]
