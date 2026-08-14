"""Direct RW-gauge metric-to-curvature polarization observables.

This module implements the paper-facing observable bridge without using the
strict-NP lower-scalar completion.  It assembles the RW-gauge metric from the
Appendix-A tensor harmonics, differentiates the metric perturbation, evaluates
the first variation of the Riemann tensor on Schwarzschild, and projects the
electric tidal tensor onto the incident Cartesian orthonormal frame.

The Fourier convention is ``exp(-i k t)`` and the coordinate ordering is
``(t, r, theta, phi)`` throughout.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math
from typing import Callable, Literal

import numpy as np
from scipy.special import sph_harm_y
from scipy.special import spherical_jn

from schwgw.backgrounds.base import StaticSphericalBackground
from schwgw.numerics import BoundaryConfig, solve_radial_mode
from schwgw.perturbations import Sector, V_RW, V_Zerilli, reconstruct_metric_mode
from schwgw.scattering.observables import (
    ElectricTidalComponents,
    PolarizationResult,
    package_electric_tidal_components,
    polarization_acceleration_from_packaged_scalars,
    polarization_from_packaged_scalars,
)
from schwgw.scattering.apparent import (
    ApparentPolarizationResult,
    apparent_polarizations_from_strict_np,
)
from schwgw.scattering.weyl import StrictNPScalars
from schwgw.waves.incident import IncidentPlaneGW


RadialSolver = Callable[
    [Sector, int, float, StaticSphericalBackground, BoundaryConfig | None],
    object,
]
ObserverFrame = Literal["static_orthonormal", "li_literal_cartesian"]


@dataclass(frozen=True)
class MetricPerturbationJet:
    """Metric perturbation and its first two coordinate derivatives."""

    value: np.ndarray
    first: np.ndarray
    second: np.ndarray

    def __post_init__(self) -> None:
        value = np.asarray(self.value, dtype=np.complex128)
        first = np.asarray(self.first, dtype=np.complex128)
        second = np.asarray(self.second, dtype=np.complex128)
        if value.shape != (4, 4):
            raise ValueError("metric perturbation value must have shape (4, 4).")
        if first.shape != (4, 4, 4):
            raise ValueError("first metric derivatives must have shape (4, 4, 4).")
        if second.shape != (4, 4, 4, 4):
            raise ValueError("second metric derivatives must have shape (4, 4, 4, 4).")
        if not (
            np.all(np.isfinite(value))
            and np.all(np.isfinite(first))
            and np.all(np.isfinite(second))
        ):
            raise ValueError("metric perturbation jet must be finite.")
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "first", first)
        object.__setattr__(self, "second", second)


@dataclass(frozen=True)
class DirectMetricCurvatureResult:
    """Direct metric-curvature observable plus audit intermediates."""

    polarization: PolarizationResult
    tidal: ElectricTidalComponents
    metric_jet: MetricPerturbationJet
    riemann: np.ndarray


def compute_direct_metric_polarization(
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
    radial_step_fraction: float = 1.0e-4,
    axis_regularization: float = 1.0e-6,
    observer_frame: ObserverFrame = "static_orthonormal",
) -> PolarizationResult:
    """Return only the production polarization from the direct bridge.

    :func:`compute_metric_curvature_polarization` deliberately retains the
    metric and curvature intermediates for scientific audit.  Grid runners
    consume the historical :class:`PolarizationResult` surface, so this
    narrow adapter exposes that surface without changing the calculation.
    """

    return compute_metric_curvature_polarization(
        background=background,
        k=k,
        r=r,
        theta=theta,
        phi=phi,
        A_plus=A_plus,
        A_cross=A_cross,
        lmax=lmax,
        boundary_config=boundary_config,
        radial_solver=radial_solver,
        radial_step_fraction=radial_step_fraction,
        axis_regularization=axis_regularization,
        observer_frame=observer_frame,
    ).polarization


def compute_direct_metric_apparent_polarizations(
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
    radial_step_fraction: float = 1.0e-4,
    axis_regularization: float = 1.0e-6,
    observer_frame: ObserverFrame = "static_orthonormal",
) -> ApparentPolarizationResult:
    """Return Fig. 7 diagnostics from direct incident-frame contractions."""

    result = compute_metric_curvature_polarization(
        background=background,
        k=k,
        r=r,
        theta=theta,
        phi=phi,
        A_plus=A_plus,
        A_cross=A_cross,
        lmax=lmax,
        boundary_config=boundary_config,
        radial_solver=radial_solver,
        radial_step_fraction=radial_step_fraction,
        axis_regularization=axis_regularization,
        observer_frame=observer_frame,
    )
    evaluation_theta = float(
        result.polarization.diagnostics.get("axis_evaluation_theta", theta)
    )
    strict_np = strict_np_from_incident_riemann(
        result.riemann,
        M=float(background.M),
        r=r,
        theta=evaluation_theta,
        phi=phi,
        observer_frame=observer_frame,
    )
    diagnostics = dict(result.polarization.diagnostics)
    diagnostics.update(
        {
            "strict_np_direct_riemann_contraction": 1.0,
            "strict_np_wigner_transform": 0.0,
            "strict_np_lower_scalar_completion": 0.0,
        }
    )
    return apparent_polarizations_from_strict_np(
        k,
        strict_np,
        diagnostics=diagnostics,
    )


@dataclass(frozen=True)
class _FlatSphericalBackground:
    M: float = 0.0
    name: str = "flat_spherical"

    @property
    def horizon_radius(self) -> float:
        return 0.0

    def f(self, r: object) -> float | np.ndarray:
        values = np.ones_like(np.asarray(r, dtype=float))
        return float(values) if values.shape == () else values

    def df_dr(self, r: object) -> float | np.ndarray:
        values = np.zeros_like(np.asarray(r, dtype=float))
        return float(values) if values.shape == () else values


@dataclass(frozen=True)
class _FlatMasterSolution:
    sector: Sector
    ell: int
    k: float
    A_in: complex = 1.0 + 0.0j
    diagnostics: object | None = None

    def psi_at(self, r: float) -> complex:
        radius = float(r)
        bessel = spherical_jn(self.ell, self.k * radius)
        normalization = 2.0 * self.k / ((1.0j) ** (self.ell + 1))
        return complex(normalization * radius * bessel)

    def dpsi_dr_at(self, r: float) -> complex:
        radius = float(r)
        argument = self.k * radius
        radial_factor = spherical_jn(self.ell, argument) + argument * spherical_jn(
            self.ell, argument, derivative=True
        )
        normalization = 2.0 * self.k / ((1.0j) ** (self.ell + 1))
        return complex(normalization * radial_factor)


def compute_metric_curvature_polarization(
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
    radial_step_fraction: float = 1.0e-4,
    axis_regularization: float = 1.0e-6,
    observer_frame: ObserverFrame = "static_orthonormal",
) -> DirectMetricCurvatureResult:
    """Return the finite-radius polarization from direct metric curvature.

    The radial master equation is solved once per ``(sector, ell)``.  Its
    equation supplies ``psi''`` and ``psi'''`` at the observer anchor; only
    the smooth algebraic reconstruction coefficients are differentiated on a
    Richardson-extrapolated stencil.  Curvature differentiation therefore
    launches no additional ODE solves and never differences dense-solution
    interpolation.
    """

    frequency = float(k)
    radius = float(r)
    polar = float(theta)
    azimuth = float(phi)
    if frequency <= 0.0:
        raise ValueError("Wave number k must be positive.")
    if not isinstance(lmax, int) or isinstance(lmax, bool):
        raise TypeError("lmax must be an integer.")
    if lmax < 2:
        raise ValueError("Direct metric-curvature extraction requires ell >= 2.")
    if radius <= background.horizon_radius:
        raise ValueError("Direct metric-curvature extraction requires r > 2M.")
    if not 0.0 <= polar <= math.pi:
        raise ValueError("theta must lie in [0, pi].")
    if radial_step_fraction <= 0.0:
        raise ValueError("radial_step_fraction must be positive.")
    if not 0.0 < axis_regularization < 1.0e-2:
        raise ValueError("axis_regularization must lie in (0, 1e-2).")
    _validate_observer_frame(observer_frame)

    evaluation_theta = min(
        max(polar, axis_regularization), math.pi - axis_regularization
    )
    wave = IncidentPlaneGW(frequency, A_plus, A_cross)
    if wave.A_plus == 0.0 and wave.A_cross == 0.0:
        metric_jet = MetricPerturbationJet(
            value=np.zeros((4, 4), dtype=np.complex128),
            first=np.zeros((4, 4, 4), dtype=np.complex128),
            second=np.zeros((4, 4, 4, 4), dtype=np.complex128),
        )
        riemann = np.zeros((4, 4, 4, 4), dtype=np.complex128)
        tidal = ElectricTidalComponents(0.0j, 0.0j)
        return DirectMetricCurvatureResult(
            polarization=_polarization_result(
                frequency=frequency,
                lmax=lmax,
                tidal=tidal,
                diagnostics={
                    "radial_solve_count": 0.0,
                    "metric_curvature_bridge_validated": 1.0,
                    "observable_bridge_validated": 1.0,
                    "axis_regularized": float(evaluation_theta != polar),
                    "axis_evaluation_theta": evaluation_theta,
                    "observer_frame_static_orthonormal": float(
                        observer_frame == "static_orthonormal"
                    ),
                    "observer_frame_li_literal_cartesian": float(
                        observer_frame == "li_literal_cartesian"
                    ),
                },
            ),
            tidal=tidal,
            metric_jet=metric_jet,
            riemann=riemann,
        )

    metric_jet, solve_diagnostics = _assemble_rw_metric_jet(
        background=background,
        wave=wave,
        r=radius,
        theta=evaluation_theta,
        phi=azimuth,
        lmax=lmax,
        boundary_config=boundary_config,
        radial_solver=radial_solver,
        radial_step_fraction=radial_step_fraction,
    )
    background_value, background_first, background_second = schwarzschild_metric_jet(
        M=float(background.M),
        r=radius,
        theta=evaluation_theta,
    )
    riemann = linearized_riemann_from_metric_jets(
        background_value,
        background_first,
        background_second,
        metric_jet.value,
        metric_jet.first,
        metric_jet.second,
    )
    tidal = project_incident_electric_tidal(
        riemann,
        M=float(background.M),
        r=radius,
        theta=evaluation_theta,
        phi=azimuth,
        observer_frame=observer_frame,
    )
    diagnostics = dict(solve_diagnostics)
    diagnostics.update(
        {
            "metric_curvature_bridge_validated": 1.0,
            "observable_bridge_validated": 1.0,
            "full_np_pseudoinverse_bridge": 0.0,
            "positive_frequency_reality_bridge_required": 0.0,
            "axis_regularized": float(evaluation_theta != polar),
            "axis_evaluation_theta": evaluation_theta,
            "radial_step_fraction": float(radial_step_fraction),
            "observer_frame_static_orthonormal": float(
                observer_frame == "static_orthonormal"
            ),
            "observer_frame_li_literal_cartesian": float(
                observer_frame == "li_literal_cartesian"
            ),
        }
    )
    return DirectMetricCurvatureResult(
        polarization=_polarization_result(
            frequency=frequency,
            lmax=lmax,
            tidal=tidal,
            diagnostics=diagnostics,
        ),
        tidal=tidal,
        metric_jet=metric_jet,
        riemann=riemann,
    )


def compute_flat_metric_curvature_partial_wave(
    *,
    k: float,
    r: float,
    theta: float,
    phi: float,
    A_plus: complex,
    A_cross: complex,
    lmax: int,
    radial_step_fraction: float = 1.0e-4,
    axis_regularization: float = 1.0e-6,
    observer_frame: ObserverFrame = "static_orthonormal",
) -> DirectMetricCurvatureResult:
    """Return the direct metric-curvature flat partial-wave oracle.

    Unlike the historical strict-NP flat diagnostic, this path retains the
    Appendix-A metric tensor and differentiates it directly.  It is therefore
    an independent end-to-end check of tensor-harmonic normalization.
    """

    background = _FlatSphericalBackground()

    def radial_solver(
        sector: Sector,
        ell: int,
        frequency: float,
        requested_background: StaticSphericalBackground,
        boundary_config: BoundaryConfig | None,
    ) -> _FlatMasterSolution:
        del requested_background, boundary_config
        return _FlatMasterSolution(sector=sector, ell=ell, k=frequency)

    return compute_metric_curvature_polarization(
        background=background,
        k=k,
        r=r,
        theta=theta,
        phi=phi,
        A_plus=A_plus,
        A_cross=A_cross,
        lmax=lmax,
        radial_solver=radial_solver,
        radial_step_fraction=radial_step_fraction,
        axis_regularization=axis_regularization,
        observer_frame=observer_frame,
    )


def schwarzschild_metric_jet(
    *,
    M: float,
    r: float,
    theta: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return Schwarzschild ``g``, ``partial g`` and ``partial partial g``."""

    mass = float(M)
    radius = float(r)
    polar = float(theta)
    if mass < 0.0:
        raise ValueError("M must be non-negative.")
    if radius <= 2.0 * mass:
        raise ValueError("Schwarzschild metric jet requires r > 2M.")
    sine = math.sin(polar)
    cosine = math.cos(polar)
    f = 1.0 - 2.0 * mass / radius
    fp = 2.0 * mass / radius**2
    fpp = -4.0 * mass / radius**3

    value = np.zeros((4, 4), dtype=np.float64)
    first = np.zeros((4, 4, 4), dtype=np.float64)
    second = np.zeros((4, 4, 4, 4), dtype=np.float64)
    value[0, 0] = -f
    value[1, 1] = 1.0 / f
    value[2, 2] = radius**2
    value[3, 3] = radius**2 * sine**2

    first[1, 0, 0] = -fp
    first[1, 1, 1] = -fp / f**2
    first[1, 2, 2] = 2.0 * radius
    first[1, 3, 3] = 2.0 * radius * sine**2
    first[2, 3, 3] = 2.0 * radius**2 * sine * cosine

    second[1, 1, 0, 0] = -fpp
    second[1, 1, 1, 1] = 2.0 * fp**2 / f**3 - fpp / f**2
    second[1, 1, 2, 2] = 2.0
    second[1, 1, 3, 3] = 2.0 * sine**2
    second[1, 2, 3, 3] = 4.0 * radius * sine * cosine
    second[2, 1, 3, 3] = second[1, 2, 3, 3]
    second[2, 2, 3, 3] = 2.0 * radius**2 * (cosine**2 - sine**2)
    return value, first, second


def linearized_riemann_from_metric_jets(
    background_metric: np.ndarray,
    background_first: np.ndarray,
    background_second: np.ndarray,
    perturbation: np.ndarray,
    perturbation_first: np.ndarray,
    perturbation_second: np.ndarray,
) -> np.ndarray:
    """Return ``delta R_{a b c d}`` from coordinate metric jets.

    This is the exact directional derivative at ``epsilon=0`` of the Riemann
    tensor of ``g + epsilon*h``.  It includes the background-curvature term
    from lowering the first index and therefore is valid away from flat space.
    """

    g = np.asarray(background_metric, dtype=np.complex128)
    dg = np.asarray(background_first, dtype=np.complex128)
    d2g = np.asarray(background_second, dtype=np.complex128)
    h = np.asarray(perturbation, dtype=np.complex128)
    dh = np.asarray(perturbation_first, dtype=np.complex128)
    d2h = np.asarray(perturbation_second, dtype=np.complex128)
    if g.shape != (4, 4) or h.shape != (4, 4):
        raise ValueError("metric values must have shape (4, 4).")
    if dg.shape != (4, 4, 4) or dh.shape != (4, 4, 4):
        raise ValueError("first derivatives must have shape (4, 4, 4).")
    if d2g.shape != (4, 4, 4, 4) or d2h.shape != (4, 4, 4, 4):
        raise ValueError("second derivatives must have shape (4, 4, 4, 4).")

    inverse = np.linalg.inv(g)
    delta_inverse = -inverse @ h @ inverse
    inverse_first = np.empty_like(dg)
    delta_inverse_first = np.empty_like(dg)
    for coordinate in range(4):
        inverse_first[coordinate] = -inverse @ dg[coordinate] @ inverse
        delta_inverse_first[coordinate] = -(
            delta_inverse @ dg[coordinate] @ inverse
            + inverse @ dh[coordinate] @ inverse
            + inverse @ dg[coordinate] @ delta_inverse
        )

    connection_kernel = np.empty((4, 4, 4), dtype=np.complex128)
    delta_connection_kernel = np.empty_like(connection_kernel)
    connection_kernel_first = np.empty((4, 4, 4, 4), dtype=np.complex128)
    delta_connection_kernel_first = np.empty_like(connection_kernel_first)
    for lower in range(4):
        for first_index in range(4):
            for second_index in range(4):
                connection_kernel[lower, first_index, second_index] = (
                    dg[first_index, second_index, lower]
                    + dg[second_index, first_index, lower]
                    - dg[lower, first_index, second_index]
                )
                delta_connection_kernel[lower, first_index, second_index] = (
                    dh[first_index, second_index, lower]
                    + dh[second_index, first_index, lower]
                    - dh[lower, first_index, second_index]
                )
                for derivative in range(4):
                    connection_kernel_first[
                        derivative, lower, first_index, second_index
                    ] = (
                        d2g[derivative, first_index, second_index, lower]
                        + d2g[derivative, second_index, first_index, lower]
                        - d2g[derivative, lower, first_index, second_index]
                    )
                    delta_connection_kernel_first[
                        derivative, lower, first_index, second_index
                    ] = (
                        d2h[derivative, first_index, second_index, lower]
                        + d2h[derivative, second_index, first_index, lower]
                        - d2h[derivative, lower, first_index, second_index]
                    )

    connection = 0.5 * np.einsum("al,lmn->amn", inverse, connection_kernel)
    delta_connection = 0.5 * (
        np.einsum("al,lmn->amn", delta_inverse, connection_kernel)
        + np.einsum("al,lmn->amn", inverse, delta_connection_kernel)
    )
    connection_first = 0.5 * (
        np.einsum("kal,lmn->kamn", inverse_first, connection_kernel)
        + np.einsum("al,klmn->kamn", inverse, connection_kernel_first)
    )
    delta_connection_first = 0.5 * (
        np.einsum("kal,lmn->kamn", delta_inverse_first, connection_kernel)
        + np.einsum("kal,lmn->kamn", inverse_first, delta_connection_kernel)
        + np.einsum("al,klmn->kamn", delta_inverse, connection_kernel_first)
        + np.einsum("al,klmn->kamn", inverse, delta_connection_kernel_first)
    )

    riemann_up = np.empty((4, 4, 4, 4), dtype=np.complex128)
    delta_riemann_up = np.empty_like(riemann_up)
    for upper in range(4):
        for lower in range(4):
            for first_index in range(4):
                for second_index in range(4):
                    riemann_up[upper, lower, first_index, second_index] = (
                        connection_first[first_index, upper, second_index, lower]
                        - connection_first[second_index, upper, first_index, lower]
                        + np.dot(
                            connection[upper, first_index, :],
                            connection[:, second_index, lower],
                        )
                        - np.dot(
                            connection[upper, second_index, :],
                            connection[:, first_index, lower],
                        )
                    )
                    delta_riemann_up[upper, lower, first_index, second_index] = (
                        delta_connection_first[first_index, upper, second_index, lower]
                        - delta_connection_first[
                            second_index, upper, first_index, lower
                        ]
                        + np.dot(
                            delta_connection[upper, first_index, :],
                            connection[:, second_index, lower],
                        )
                        + np.dot(
                            connection[upper, first_index, :],
                            delta_connection[:, second_index, lower],
                        )
                        - np.dot(
                            delta_connection[upper, second_index, :],
                            connection[:, first_index, lower],
                        )
                        - np.dot(
                            connection[upper, second_index, :],
                            delta_connection[:, first_index, lower],
                        )
                    )
    return np.einsum("ae,ebcd->abcd", h, riemann_up) + np.einsum(
        "ae,ebcd->abcd", g, delta_riemann_up
    )


def riemann_covariant_from_metric_jet(
    metric: np.ndarray,
    metric_first: np.ndarray,
    metric_second: np.ndarray,
) -> np.ndarray:
    """Return ``R_abcd`` from a coordinate metric and its first two jets."""

    g = np.asarray(metric, dtype=np.complex128)
    dg = np.asarray(metric_first, dtype=np.complex128)
    d2g = np.asarray(metric_second, dtype=np.complex128)
    if g.shape != (4, 4):
        raise ValueError("metric must have shape (4, 4).")
    if dg.shape != (4, 4, 4):
        raise ValueError("metric_first must have shape (4, 4, 4).")
    if d2g.shape != (4, 4, 4, 4):
        raise ValueError("metric_second must have shape (4, 4, 4, 4).")
    if not all(np.all(np.isfinite(value)) for value in (g, dg, d2g)):
        raise ValueError("metric jet must be finite.")

    inverse = np.linalg.inv(g)
    inverse_first = np.empty_like(dg)
    for coordinate in range(4):
        inverse_first[coordinate] = -inverse @ dg[coordinate] @ inverse

    kernel = np.empty((4, 4, 4), dtype=np.complex128)
    kernel_first = np.empty((4, 4, 4, 4), dtype=np.complex128)
    for lower in range(4):
        for first_index in range(4):
            for second_index in range(4):
                kernel[lower, first_index, second_index] = (
                    dg[first_index, second_index, lower]
                    + dg[second_index, first_index, lower]
                    - dg[lower, first_index, second_index]
                )
                for derivative in range(4):
                    kernel_first[derivative, lower, first_index, second_index] = (
                        d2g[derivative, first_index, second_index, lower]
                        + d2g[derivative, second_index, first_index, lower]
                        - d2g[derivative, lower, first_index, second_index]
                    )

    connection = 0.5 * np.einsum("al,lmn->amn", inverse, kernel)
    connection_first = 0.5 * (
        np.einsum("kal,lmn->kamn", inverse_first, kernel)
        + np.einsum("al,klmn->kamn", inverse, kernel_first)
    )
    riemann_up = np.empty((4, 4, 4, 4), dtype=np.complex128)
    for upper in range(4):
        for lower in range(4):
            for first_index in range(4):
                for second_index in range(4):
                    riemann_up[upper, lower, first_index, second_index] = (
                        connection_first[first_index, upper, second_index, lower]
                        - connection_first[second_index, upper, first_index, lower]
                        + np.dot(
                            connection[upper, first_index, :],
                            connection[:, second_index, lower],
                        )
                        - np.dot(
                            connection[upper, second_index, :],
                            connection[:, first_index, lower],
                        )
                    )
    result = np.einsum("ae,ebcd->abcd", g, riemann_up)
    if not np.all(np.isfinite(result)):
        raise RuntimeError("coordinate Riemann evaluation is non-finite")
    return result


def project_incident_electric_tidal(
    riemann: np.ndarray,
    *,
    M: float,
    r: float,
    theta: float,
    phi: float,
    observer_frame: ObserverFrame = "static_orthonormal",
) -> ElectricTidalComponents:
    """Project ``delta R`` onto one explicit incident Cartesian frame."""

    tensor = np.asarray(riemann, dtype=np.complex128)
    if tensor.shape != (4, 4, 4, 4):
        raise ValueError("riemann must have shape (4, 4, 4, 4).")
    e0, ex, ey, _ = _incident_frame(
        M=M,
        r=r,
        theta=theta,
        phi=phi,
        observer_frame=observer_frame,
    )
    E_xx = np.einsum("abcd,a,b,c,d->", tensor, e0, ex, e0, ex)
    E_xy = np.einsum("abcd,a,b,c,d->", tensor, e0, ex, e0, ey)
    return ElectricTidalComponents(complex(E_xx), complex(E_xy))


def strict_np_from_incident_riemann(
    riemann: np.ndarray,
    *,
    M: float,
    r: float,
    theta: float,
    phi: float,
    observer_frame: ObserverFrame = "static_orthonormal",
) -> StrictNPScalars:
    """Contract the linearized curvature with the incident null tetrad.

    In vacuum the linearized Riemann and Weyl tensors coincide.  The signs
    and leg order are the standard project definitions used by
    :mod:`schwgw.scattering.weyl`, but here every scalar is obtained from the
    same directly differentiated metric tensor rather than reconstructed from
    radial source identities.
    """

    tensor = np.asarray(riemann, dtype=np.complex128)
    if tensor.shape != (4, 4, 4, 4):
        raise ValueError("riemann must have shape (4, 4, 4, 4).")
    e0, ex, ey, ez = _incident_frame(
        M=M,
        r=r,
        theta=theta,
        phi=phi,
        observer_frame=observer_frame,
    )
    scale = 1.0 / math.sqrt(2.0)
    l_leg = scale * (e0 + ez)
    n_leg = scale * (e0 - ez)
    m_leg = scale * (ex + 1.0j * ey)
    mbar_leg = np.conjugate(m_leg)

    def contract(
        first: np.ndarray,
        second: np.ndarray,
        third: np.ndarray,
        fourth: np.ndarray,
    ) -> complex:
        return complex(
            -np.einsum(
                "abcd,a,b,c,d->",
                tensor,
                first,
                second,
                third,
                fourth,
            )
        )

    return StrictNPScalars(
        psi0=contract(l_leg, m_leg, l_leg, m_leg),
        psi1=contract(l_leg, n_leg, l_leg, m_leg),
        psi2=contract(l_leg, m_leg, n_leg, mbar_leg),
        psi3=contract(l_leg, n_leg, n_leg, mbar_leg),
        psi4=contract(n_leg, mbar_leg, n_leg, mbar_leg),
        frame="incident",
    )


def _incident_frame(
    *,
    M: float,
    r: float,
    theta: float,
    phi: float,
    observer_frame: ObserverFrame,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    _validate_observer_frame(observer_frame)
    if observer_frame == "static_orthonormal":
        return _incident_orthonormal_frame(M=M, r=r, theta=theta, phi=phi)
    return _li_literal_cartesian_frame(M=M, r=r, theta=theta, phi=phi)


def _incident_orthonormal_frame(
    *,
    M: float,
    r: float,
    theta: float,
    phi: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return ``(e_t,e_x,e_y,e_z)`` in Schwarzschild coordinates."""

    radius = float(r)
    polar = float(theta)
    azimuth = float(phi)
    f = 1.0 - 2.0 * float(M) / radius
    if f <= 0.0:
        raise ValueError("incident-frame projection requires r > 2M.")
    sine = math.sin(polar)
    if abs(sine) <= 100.0 * np.finfo(float).eps:
        raise ValueError(
            "incident-frame projection requires a non-singular polar coordinate."
        )
    cosine = math.cos(polar)
    cos_phi = math.cos(azimuth)
    sin_phi = math.sin(azimuth)
    e0 = np.asarray((1.0 / math.sqrt(f), 0.0, 0.0, 0.0))
    er = np.asarray((0.0, math.sqrt(f), 0.0, 0.0))
    etheta = np.asarray((0.0, 0.0, 1.0 / radius, 0.0))
    ephi = np.asarray((0.0, 0.0, 0.0, 1.0 / (radius * sine)))
    ex = sine * cos_phi * er + cosine * cos_phi * etheta - sin_phi * ephi
    ey = sine * sin_phi * er + cosine * sin_phi * etheta + cos_phi * ephi
    ez = cosine * er - sine * etheta
    return e0, ex, ey, ez


def _li_literal_cartesian_frame(
    *,
    M: float,
    r: float,
    theta: float,
    phi: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return Li's literal flat-Cartesian tetrad after the coordinate Jacobian.

    This is deliberately *not* orthonormalized with the Schwarzschild lapse.
    It is a paper-convention reproduction surface, not the physical static
    observer frame.
    """

    radius = float(r)
    polar = float(theta)
    azimuth = float(phi)
    if radius <= 2.0 * float(M):
        raise ValueError("incident-frame projection requires r > 2M.")
    sine = math.sin(polar)
    if abs(sine) <= 100.0 * np.finfo(float).eps:
        raise ValueError(
            "incident-frame projection requires a non-singular polar coordinate."
        )
    cosine = math.cos(polar)
    cos_phi = math.cos(azimuth)
    sin_phi = math.sin(azimuth)
    e0 = np.asarray((1.0, 0.0, 0.0, 0.0))
    er = np.asarray((0.0, 1.0, 0.0, 0.0))
    etheta = np.asarray((0.0, 0.0, 1.0 / radius, 0.0))
    ephi = np.asarray((0.0, 0.0, 0.0, 1.0 / (radius * sine)))
    ex = sine * cos_phi * er + cosine * cos_phi * etheta - sin_phi * ephi
    ey = sine * sin_phi * er + cosine * sin_phi * etheta + cos_phi * ephi
    ez = cosine * er - sine * etheta
    return e0, ex, ey, ez


def _validate_observer_frame(observer_frame: str) -> None:
    if observer_frame not in {"static_orthonormal", "li_literal_cartesian"}:
        raise ValueError(
            "observer_frame must be one of "
            "['static_orthonormal', 'li_literal_cartesian']."
        )


def _assemble_rw_metric_jet(
    *,
    background: StaticSphericalBackground,
    wave: IncidentPlaneGW,
    r: float,
    theta: float,
    phi: float,
    lmax: int,
    boundary_config: BoundaryConfig | None,
    radial_solver: RadialSolver,
    radial_step_fraction: float,
) -> tuple[MetricPerturbationJet, dict[str, float]]:
    value = np.zeros((4, 4), dtype=np.complex128)
    first = np.zeros((4, 4, 4), dtype=np.complex128)
    second = np.zeros((4, 4, 4, 4), dtype=np.complex128)
    radial_solutions: dict[tuple[Sector, int], object] = {}
    mode_count = 0
    boundary_residuals: list[float] = []
    wronskian_residuals: list[float] = []
    condition_numbers: list[float] = []
    step = _radial_step(
        r=r,
        horizon_radius=float(background.horizon_radius),
        fraction=radial_step_fraction,
    )
    coefficient_step = _radial_coefficient_step(
        r=r,
        horizon_radius=float(background.horizon_radius),
        requested_step=step,
    )

    for ell in range(2, lmax + 1):
        for sector in (Sector.ODD, Sector.EVEN):
            solution = radial_solver(sector, ell, wave.k, background, boundary_config)
            radial_solutions[(sector, ell)] = solution
            diagnostics = getattr(solution, "diagnostics", None)
            boundary_residuals.append(
                float(getattr(diagnostics, "boundary_residual", 0.0))
            )
            wronskian_residuals.append(
                float(getattr(diagnostics, "wronskian_residual", 0.0))
            )
            condition_numbers.append(
                float(getattr(diagnostics, "match_condition_number", 0.0))
            )
            A_in = complex(getattr(solution, "A_in"))
            if not np.isfinite(A_in.real) or not np.isfinite(A_in.imag) or A_in == 0.0:
                raise RuntimeError(f"invalid A_in for {sector.value}, ell={ell}.")
            for m in (-2, 2):
                coefficient = (
                    wave.c_lm_odd(ell, m)
                    if sector is Sector.ODD
                    else wave.c_lm_even(ell, m)
                )
                if coefficient == 0.0:
                    continue
                radial_components = _radial_component_jets(
                    sector=sector,
                    ell=ell,
                    k=wave.k,
                    r=r,
                    step=step,
                    scale=coefficient / A_in,
                    solution=solution,
                    background=background,
                )
                harmonic = _harmonic_component_jets(ell, m, theta, phi, sector)
                labels = (
                    ("Bt", "B1") if sector is Sector.ODD else ("tt", "Rt", "L0", "T0")
                )
                for label in labels:
                    radial_values = radial_components[label]
                    _accumulate_separated_component(
                        value=value,
                        first=first,
                        second=second,
                        indices=_component_indices(label),
                        radial=radial_values,
                        angular=harmonic,
                        k=wave.k,
                        m=m,
                    )
                mode_count += 1

    return MetricPerturbationJet(value=value, first=first, second=second), {
        "radial_solve_count": float(len(radial_solutions)),
        "metric_mode_count": float(mode_count),
        "max_boundary_residual": max(boundary_residuals, default=0.0),
        "max_wronskian_residual": max(wronskian_residuals, default=0.0),
        "max_match_condition_number": max(condition_numbers, default=0.0),
        "radial_stencil_step": coefficient_step,
        "requested_radial_step": step,
        "radial_ode_jet": 1.0,
    }


def _radial_component_jets(
    *,
    sector: Sector,
    ell: int,
    k: float,
    r: float,
    step: float,
    scale: complex,
    solution: object,
    background: StaticSphericalBackground,
) -> dict[str, tuple[complex, complex, complex]]:
    """Return reconstructed metric-component jets at one radius.

    Differencing the *dense ODE solution* twice is numerically unsafe at the
    high multipoles used by Figs. 3--7: interpolation error is amplified by
    ``step**-2`` before hundreds of partial waves are summed.  Instead, use
    the RW/Zerilli equation to obtain ``psi''`` and ``psi'''`` at the anchor
    radius.  Only the smooth algebraic reconstruction coefficients are
    differentiated, with a Richardson-extrapolated five-point stencil.

    The public ``radial_step_fraction`` remains a conservative lower bound on
    the coefficient stencil.  Coefficients vary on the background radial
    scale rather than the wave scale, so a larger ``1e-3 r`` base step greatly
    reduces roundoff while the Richardson pair removes the leading fourth-
    order truncation term.
    """

    radius = float(r)
    coefficient_step = _radial_coefficient_step(
        r=radius,
        horizon_radius=float(background.horizon_radius),
        requested_step=step,
    )
    if coefficient_step <= 0.0:
        raise ValueError("radial coefficient stencil requires an exterior radius")

    p0, q0, p1, q1, coefficient_jets = _radial_ode_coefficient_jets(
        sector,
        ell,
        float(k),
        radius,
        coefficient_step,
        background,
    )
    psi0 = scale * complex(solution.psi_at(radius))
    psi1 = scale * complex(solution.dpsi_dr_at(radius))
    psi2 = p0 * psi1 + q0 * psi0
    psi3 = (p1 + p0**2 + q0) * psi1 + (q1 + p0 * q0) * psi0

    result: dict[str, tuple[complex, complex, complex]] = {}
    for label, a0, a1, a2, b0, b1, b2 in coefficient_jets:
        value = a0 * psi0 + b0 * psi1
        derivative = a1 * psi0 + (a0 + b1) * psi1 + b0 * psi2
        second_derivative = (
            a2 * psi0 + (2.0 * a1 + b2) * psi1 + (a0 + 2.0 * b1) * psi2 + b0 * psi3
        )
        result[label] = (
            complex(value),
            complex(derivative),
            complex(second_derivative),
        )
    return result


def _radial_ode_coefficient_jets(
    sector: Sector,
    ell: int,
    k: float,
    radius: float,
    coefficient_step: float,
    background: StaticSphericalBackground,
) -> tuple[
    complex,
    complex,
    complex,
    complex,
    tuple[tuple[str, complex, complex, complex, complex, complex, complex], ...],
]:
    """Return cached jets when the background has a stable value hash."""

    try:
        hash(background)
    except TypeError:
        return _compute_radial_ode_coefficient_jets(
            sector,
            ell,
            k,
            radius,
            coefficient_step,
            background,
        )
    return _cached_radial_ode_coefficient_jets(
        sector,
        ell,
        k,
        radius,
        coefficient_step,
        background,
    )


@lru_cache(maxsize=131_072)
def _cached_radial_ode_coefficient_jets(
    sector: Sector,
    ell: int,
    k: float,
    radius: float,
    coefficient_step: float,
    background: StaticSphericalBackground,
) -> tuple[
    complex,
    complex,
    complex,
    complex,
    tuple[tuple[str, complex, complex, complex, complex, complex, complex], ...],
]:
    return _compute_radial_ode_coefficient_jets(
        sector,
        ell,
        k,
        radius,
        coefficient_step,
        background,
    )


def _compute_radial_ode_coefficient_jets(
    sector: Sector,
    ell: int,
    k: float,
    radius: float,
    coefficient_step: float,
    background: StaticSphericalBackground,
) -> tuple[
    complex,
    complex,
    complex,
    complex,
    tuple[tuple[str, complex, complex, complex, complex, complex, complex], ...],
]:
    """Compute ODE and reconstruction-coefficient jets at one radius."""

    labels = ("Bt", "B1") if sector is Sector.ODD else ("tt", "Rt", "L0", "T0")
    offsets = (-4, -2, -1, 0, 1, 2, 4)
    coefficient_samples: dict[str, dict[int, tuple[complex, complex]]] = {
        label: {} for label in labels
    }
    ode_samples: dict[int, tuple[float, float]] = {}
    potential = V_RW if sector is Sector.ODD else V_Zerilli
    for offset in offsets:
        sample_radius = radius + coefficient_step * offset
        psi_basis = reconstruct_metric_mode(
            sector,
            ell,
            k,
            sample_radius,
            1.0 + 0.0j,
            0.0j,
            background,
        )
        derivative_basis = reconstruct_metric_mode(
            sector,
            ell,
            k,
            sample_radius,
            0.0j,
            1.0 + 0.0j,
            background,
        )
        for label in labels:
            coefficient_samples[label][offset] = (
                complex(psi_basis.components[label]),
                complex(derivative_basis.components[label]),
            )
        lapse = float(background.f(sample_radius))
        lapse_derivative = float(background.df_dr(sample_radius))
        mode_potential = float(potential(ell, sample_radius, background))
        ode_samples[offset] = (
            -lapse_derivative / lapse,
            (mode_potential - k**2) / lapse**2,
        )

    p0, q0 = ode_samples[0]
    p1 = _richardson_first_derivative(
        {offset: complex(values[0]) for offset, values in ode_samples.items()},
        coefficient_step,
    )
    q1 = _richardson_first_derivative(
        {offset: complex(values[1]) for offset, values in ode_samples.items()},
        coefficient_step,
    )
    jets = []
    for label, samples in coefficient_samples.items():
        a_samples = {offset: values[0] for offset, values in samples.items()}
        b_samples = {offset: values[1] for offset, values in samples.items()}
        jets.append(
            (
                label,
                a_samples[0],
                _richardson_first_derivative(a_samples, coefficient_step),
                _richardson_second_derivative(a_samples, coefficient_step),
                b_samples[0],
                _richardson_first_derivative(b_samples, coefficient_step),
                _richardson_second_derivative(b_samples, coefficient_step),
            )
        )
    return complex(p0), complex(q0), p1, q1, tuple(jets)


def _richardson_first_derivative(
    samples: dict[int, complex],
    step: float,
) -> complex:
    fine = (samples[-2] - 8.0 * samples[-1] + 8.0 * samples[1] - samples[2]) / (
        12.0 * step
    )
    coarse = (samples[-4] - 8.0 * samples[-2] + 8.0 * samples[2] - samples[4]) / (
        24.0 * step
    )
    return complex((16.0 * fine - coarse) / 15.0)


def _richardson_second_derivative(
    samples: dict[int, complex],
    step: float,
) -> complex:
    fine = (
        -samples[-2]
        + 16.0 * samples[-1]
        - 30.0 * samples[0]
        + 16.0 * samples[1]
        - samples[2]
    ) / (12.0 * step**2)
    coarse = (
        -samples[-4]
        + 16.0 * samples[-2]
        - 30.0 * samples[0]
        + 16.0 * samples[2]
        - samples[4]
    ) / (48.0 * step**2)
    return complex((16.0 * fine - coarse) / 15.0)


def _harmonic_component_jets(
    ell: int,
    m: int,
    theta: float,
    phi: float,
    sector: Sector,
) -> dict[str, tuple[complex, complex, complex]]:
    y, gradient, hessian = sph_harm_y(ell, m, theta, phi, diff_n=2)
    y0 = complex(y)
    y1 = complex(gradient[0])
    y2 = complex(hessian[0, 0])
    sine = math.sin(theta)
    cosine = math.cos(theta)
    cotangent = cosine / sine
    csc2 = 1.0 / sine**2
    angular_potential = ell * (ell + 1) - m**2 * csc2
    angular_potential_derivative = 2.0 * m**2 * csc2 * cotangent
    y3 = (
        csc2 * y1
        - cotangent * y2
        - angular_potential_derivative * y0
        - angular_potential * y1
    )

    if sector is Sector.EVEN:
        sin2 = sine**2
        sin2_first = 2.0 * sine * cosine
        sin2_second = 2.0 * (cosine**2 - sine**2)
        return {
            "base": (y0, y1, y2),
            "T0_phi": (
                sin2 * y0,
                sin2_first * y0 + sin2 * y1,
                sin2_second * y0 + 2.0 * sin2_first * y1 + sin2 * y2,
            ),
            "T0_theta": (y0, y1, y2),
        }

    csc = 1.0 / sine
    csc_first = -csc * cotangent
    csc_second = csc * (cotangent**2 + csc2)
    bt0 = 1.0j * m * csc * y0
    bt1 = 1.0j * m * (csc_first * y0 + csc * y1)
    bt2 = 1.0j * m * (csc_second * y0 + 2.0 * csc_first * y1 + csc * y2)
    bphi0 = -sine * y1
    bphi1 = -(cosine * y1 + sine * y2)
    bphi2 = sine * y1 - 2.0 * cosine * y2 - sine * y3
    return {
        "Bt_theta": (bt0, bt1, bt2),
        "Bt_phi": (bphi0, bphi1, bphi2),
        "B1_theta": (bt0, bt1, bt2),
        "B1_phi": (bphi0, bphi1, bphi2),
    }


def _component_indices(label: str) -> tuple[tuple[int, int, str], ...]:
    if label == "tt":
        return ((0, 0, "base"),)
    if label == "Rt":
        return ((0, 1, "base"), (1, 0, "base"))
    if label == "L0":
        return ((1, 1, "base"),)
    if label == "T0":
        return ((2, 2, "T0_theta"), (3, 3, "T0_phi"))
    if label == "Bt":
        return (
            (0, 2, "Bt_theta"),
            (2, 0, "Bt_theta"),
            (0, 3, "Bt_phi"),
            (3, 0, "Bt_phi"),
        )
    if label == "B1":
        return (
            (1, 2, "B1_theta"),
            (2, 1, "B1_theta"),
            (1, 3, "B1_phi"),
            (3, 1, "B1_phi"),
        )
    raise ValueError(f"unknown RW-gauge component label: {label}")


def _accumulate_separated_component(
    *,
    value: np.ndarray,
    first: np.ndarray,
    second: np.ndarray,
    indices: tuple[tuple[int, int, str], ...],
    radial: tuple[complex, complex, complex],
    angular: dict[str, tuple[complex, complex, complex]],
    k: float,
    m: int,
) -> None:
    H0, H1, H2 = radial
    for row, column, angular_kind in indices:
        A0, A1, A2 = angular[angular_kind]
        component = H0 * A0
        value[row, column] += component
        derivative_values = (
            -1.0j * k * component,
            H1 * A0,
            H0 * A1,
            1.0j * m * component,
        )
        for coordinate, derivative in enumerate(derivative_values):
            first[coordinate, row, column] += derivative
        second_values = {
            (0, 0): -(k**2) * component,
            (0, 1): -1.0j * k * H1 * A0,
            (0, 2): -1.0j * k * H0 * A1,
            (0, 3): k * m * component,
            (1, 1): H2 * A0,
            (1, 2): H1 * A1,
            (1, 3): 1.0j * m * H1 * A0,
            (2, 2): H0 * A2,
            (2, 3): 1.0j * m * H0 * A1,
            (3, 3): -(m**2) * component,
        }
        for (first_coordinate, second_coordinate), derivative in second_values.items():
            second[first_coordinate, second_coordinate, row, column] += derivative
            if first_coordinate != second_coordinate:
                second[second_coordinate, first_coordinate, row, column] += derivative


def _radial_step(*, r: float, horizon_radius: float, fraction: float) -> float:
    nominal = fraction * max(abs(r), 1.0)
    horizon_clearance = r - horizon_radius
    return min(nominal, 0.2 * horizon_clearance)


def _radial_coefficient_step(
    *,
    r: float,
    horizon_radius: float,
    requested_step: float,
) -> float:
    horizon_clearance = r - horizon_radius
    return min(
        max(float(requested_step), 1.0e-3 * max(abs(r), 1.0)),
        0.1 * horizon_clearance,
    )


def _polarization_result(
    *,
    frequency: float,
    lmax: int,
    tidal: ElectricTidalComponents,
    diagnostics: dict[str, float],
) -> PolarizationResult:
    packaged = package_electric_tidal_components(tidal)
    h_plus, h_cross = polarization_from_packaged_scalars(frequency, packaged)
    hddot_plus, hddot_cross = polarization_acceleration_from_packaged_scalars(packaged)
    return PolarizationResult(
        h_plus=h_plus,
        h_cross=h_cross,
        psi0_hat=packaged.psi0_pack,
        psi4_hat=packaged.psi4_pack,
        hddot_plus=hddot_plus,
        hddot_cross=hddot_cross,
        lmax=lmax,
        diagnostics=diagnostics,
    )


__all__ = [
    "DirectMetricCurvatureResult",
    "MetricPerturbationJet",
    "ObserverFrame",
    "compute_direct_metric_apparent_polarizations",
    "compute_direct_metric_polarization",
    "compute_flat_metric_curvature_partial_wave",
    "compute_metric_curvature_polarization",
    "linearized_riemann_from_metric_jets",
    "riemann_covariant_from_metric_jet",
    "project_incident_electric_tidal",
    "schwarzschild_metric_jet",
    "strict_np_from_incident_riemann",
]


compute_direct_metric_polarization.__schwgw_bridge_metadata__ = {
    "quantity_kind": "finite_radius_observer_qualified_tidal_response",
    "primary_observable": "electric_tidal_tensor_E_ij",
    "derived_observable": "monochromatic_equivalent_tidal_strain",
    "polarization_bridge": "direct RW-gauge metric-curvature electric tidal projection",
    "polarization_bridge_implementation": (
        "linearized Riemann projected onto the explicitly selected incident frame"
    ),
    "polarization_bridge_validated": True,
    "positive_frequency_reality_bridge_validated": True,
    "physical_claim": False,
    "physical_claim_scope": "qualified by the explicit gauge and observer frame",
    "gauge": "Regge-Wheeler",
    "observer_frame": "runtime explicit: static_orthonormal | li_literal_cartesian",
    "observer_worldline": "runtime explicit and required in saved production metadata",
    "tetrad": "runtime explicit and required in saved production metadata",
    "polarization_basis": "incident-aligned transverse x/y basis",
    "phase_origin": "required in saved production metadata",
    "axis_regularization": "required in saved production metadata",
    "production_backend": "direct RW metric-curvature",
    "physical_within_frozen_gauge_frame_convention": True,
    "literal_li_paper_observer_equivalence": (
        "runtime-dependent; true only for li_literal_cartesian"
    ),
    "paper_equivalence": "YELLOW",
}
compute_direct_metric_apparent_polarizations.__schwgw_bridge_metadata__ = {
    "tetrad": "direct incident-frame Riemann contractions",
    "direct_metric_curvature": True,
    "strict_np_lower_scalar_completion": False,
}
