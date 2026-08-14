"""Observer-qualified tidal and detector-response tools for Phase 6."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from numpy.typing import ArrayLike, NDArray

from schwgw.scattering.metric_curvature import (
    MetricPerturbationJet,
    linearized_riemann_from_metric_jets,
    riemann_covariant_from_metric_jet,
    schwarzschild_metric_jet,
)


@dataclass(frozen=True)
class ObserverFrame:
    """One timelike observer and an oriented orthonormal spatial triad."""

    label: str
    worldline: str
    tetrad_transport: str
    coordinates: str
    background_name: str
    mass: float | None
    radius: float | None
    theta: float | None
    metric: NDArray[np.float64]
    u: NDArray[np.float64]
    spatial_legs: NDArray[np.float64]

    def __post_init__(self) -> None:
        if any(
            not isinstance(value, str) or not value.strip()
            for value in (
                self.label,
                self.worldline,
                self.tetrad_transport,
                self.coordinates,
                self.background_name,
            )
        ):
            raise ValueError("observer metadata must be non-empty")
        metric = np.asarray(self.metric, dtype=np.float64)
        u = np.asarray(self.u, dtype=np.float64)
        legs = np.asarray(self.spatial_legs, dtype=np.float64)
        if metric.shape != (4, 4) or u.shape != (4,) or legs.shape != (3, 4):
            raise ValueError("metric/u/spatial_legs shapes must be (4,4)/(4,)/(3,4)")
        if not all(np.all(np.isfinite(value)) for value in (metric, u, legs)):
            raise ValueError("observer frame arrays must be finite")
        if self.background_name == "Schwarzschild":
            if self.mass is None or self.radius is None or self.theta is None:
                raise ValueError("Schwarzschild observer requires mass/radius/theta")
            mass = _positive_finite(self.mass, "mass")
            radius = _positive_finite(self.radius, "radius")
            theta = float(self.theta)
            if radius <= 2.0 * mass or not 0.0 < theta < math.pi:
                raise ValueError("Schwarzschild observer domain is invalid")
            expected_metric = _schwarzschild_metric(mass, radius, theta)
            if not np.allclose(metric, expected_metric, rtol=0.0, atol=2e-12):
                raise ValueError("observer metric does not match its bound domain")
            object.__setattr__(self, "mass", mass)
            object.__setattr__(self, "radius", radius)
            object.__setattr__(self, "theta", theta)
        elif self.background_name == "Minkowski":
            if any(value is not None for value in (self.mass, self.radius, self.theta)):
                raise ValueError("Cartesian Minkowski observer has no spherical domain")
        else:
            raise ValueError("unsupported observer background")
        tetrad = np.vstack((u, legs))
        gram = tetrad @ metric @ tetrad.T
        if not np.allclose(gram, np.diag([-1.0, 1.0, 1.0, 1.0]), rtol=0.0, atol=2e-12):
            raise ValueError("observer tetrad is not orthonormal")
        for name, value in (("metric", metric), ("u", u), ("spatial_legs", legs)):
            stored = np.array(value, copy=True)
            stored.setflags(write=False)
            object.__setattr__(self, name, stored)


@dataclass(frozen=True)
class TidalTensors:
    """Electric and magnetic vacuum-curvature tensors in an observer frame."""

    electric: NDArray[np.complex128]
    magnetic: NDArray[np.complex128]
    observer_label: str
    magnetic_convention: str = "B_ij=(1/2) epsilon_i^{kl} C_klj0; epsilon_123=+1"

    def __post_init__(self) -> None:
        if not isinstance(self.observer_label, str) or not self.observer_label.strip():
            raise ValueError("observer_label must be non-empty")
        for name in ("electric", "magnetic"):
            value = np.asarray(getattr(self, name), dtype=np.complex128)
            if value.shape != (3, 3) or not _finite_complex_array(value):
                raise ValueError(f"{name} must be a finite complex 3x3 array")
            stored = np.array(value, copy=True)
            stored.setflags(write=False)
            object.__setattr__(self, name, stored)


@dataclass(frozen=True)
class OperationalGaugeScalar:
    """Gauge-completed perturbation of a detector scalar along a worldline."""

    coordinate_perturbation: complex
    worldline_pullback: complex
    operational_perturbation: complex
    rule: str = "delta Q_op=delta Q_coordinate+delta z^mu partial_mu Q0"


@dataclass(frozen=True)
class RadialPureGaugeOracle:
    """Nontrivial radial pure-gauge cancellation for one detector scalar."""

    observer_label: str
    background_signal: float
    background_radial_derivative: float
    gauge_vector_radial: float
    metric_perturbation_norm: float
    linearized_riemann_norm: float
    tetrad_perturbation_norm: float
    expected_coordinate_lie_term: float
    metric_curvature_consistency_residual: float
    transformed: OperationalGaugeScalar
    absolute_residual: float
    pipeline: str = (
        "h=-Lie_xi(g) -> metric jets -> delta R; delta tetrad=-Lie_xi(e); delta z=+xi"
    )


@dataclass(frozen=True)
class FrameTransportCheck:
    """Connection-level transport residual for one frozen observer tetrad."""

    observer_label: str
    transport_law: str
    four_acceleration: NDArray[np.float64]
    spatial_leg_residuals: NDArray[np.float64]
    acceleration_norm: float
    maximum_transport_residual: float

    def __post_init__(self) -> None:
        acceleration = np.asarray(self.four_acceleration, dtype=np.float64)
        residuals = np.asarray(self.spatial_leg_residuals, dtype=np.float64)
        if (
            not isinstance(self.observer_label, str)
            or not self.observer_label
            or not isinstance(self.transport_law, str)
            or not self.transport_law
            or acceleration.shape != (4,)
            or residuals.shape != (3, 4)
            or not np.all(np.isfinite(acceleration))
            or not np.all(np.isfinite(residuals))
            or not math.isfinite(self.acceleration_norm)
            or self.acceleration_norm < 0.0
            or not math.isfinite(self.maximum_transport_residual)
            or self.maximum_transport_residual < 0.0
        ):
            raise ValueError("frame transport check is malformed")
        for name, value in (
            ("four_acceleration", acceleration),
            ("spatial_leg_residuals", residuals),
        ):
            stored = np.array(value, copy=True)
            stored.setflags(write=False)
            object.__setattr__(self, name, stored)


def static_schwarzschild_observer(
    *,
    mass: float,
    r: float,
    theta: float,
) -> ObserverFrame:
    """Return the nonrotating static Schwarzschild observer frame."""

    mass_value, radius, theta_value, f = _schwarzschild_inputs(mass, r, theta)
    metric = _schwarzschild_metric(mass_value, radius, theta_value)
    return ObserverFrame(
        label="static_schwarzschild",
        worldline="r,theta,phi constant; proper acceleration nonzero",
        tetrad_transport="nonrotating Fermi-Walker orthonormal tetrad",
        coordinates="Schwarzschild (t,r,theta,phi)",
        background_name="Schwarzschild",
        mass=mass_value,
        radius=radius,
        theta=theta_value,
        metric=metric,
        u=np.array([1.0 / math.sqrt(f), 0.0, 0.0, 0.0]),
        spatial_legs=np.array(
            [
                [0.0, math.sqrt(f), 0.0, 0.0],
                [0.0, 0.0, 1.0 / radius, 0.0],
                [0.0, 0.0, 0.0, 1.0 / (radius * math.sin(theta_value))],
            ]
        ),
    )


def radial_freefall_from_infinity_observer(
    *,
    mass: float,
    r: float,
    theta: float,
) -> ObserverFrame:
    """Return the ingoing radial geodesic frame with specific energy E=1."""

    mass_value, radius, theta_value, f = _schwarzschild_inputs(mass, r, theta)
    metric = _schwarzschild_metric(mass_value, radius, theta_value)
    infall_speed = math.sqrt(2.0 * mass_value / radius)
    return ObserverFrame(
        label="radial_freefall_E1",
        worldline="ingoing radial timelike geodesic; specific energy E=1",
        tetrad_transport="parallel transported (therefore Fermi-Walker) radial tetrad",
        coordinates="Schwarzschild (t,r,theta,phi)",
        background_name="Schwarzschild",
        mass=mass_value,
        radius=radius,
        theta=theta_value,
        metric=metric,
        u=np.array([1.0 / f, -infall_speed, 0.0, 0.0]),
        spatial_legs=np.array(
            [
                [-infall_speed / f, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0 / radius, 0.0],
                [0.0, 0.0, 0.0, 1.0 / (radius * math.sin(theta_value))],
            ]
        ),
    )


def cartesian_inertial_observer() -> ObserverFrame:
    """Return the standard inertial Cartesian frame for flat-space oracles."""

    return ObserverFrame(
        label="cartesian_inertial",
        worldline="x,y,z constant",
        tetrad_transport="parallel transported Cartesian tetrad",
        coordinates="Cartesian (t,x,y,z)",
        background_name="Minkowski",
        mass=None,
        radius=None,
        theta=None,
        metric=np.diag([-1.0, 1.0, 1.0, 1.0]),
        u=np.array([1.0, 0.0, 0.0, 0.0]),
        spatial_legs=np.eye(4, dtype=float)[1:],
    )


def project_vacuum_tidal_tensors(
    riemann_covariant: ArrayLike,
    observer: ObserverFrame,
) -> TidalTensors:
    """Project a covariant vacuum Riemann/Weyl tensor into ``E_ij`` and ``B_ij``."""

    if not isinstance(observer, ObserverFrame):
        raise TypeError("observer must be an ObserverFrame")
    riemann = np.asarray(riemann_covariant, dtype=np.complex128)
    if riemann.shape != (4, 4, 4, 4) or not _finite_complex_array(riemann):
        raise ValueError("riemann_covariant must be a finite complex (4,4,4,4) array")
    tetrad = np.vstack((observer.u, observer.spatial_legs)).astype(np.complex128)
    frame = np.einsum(
        "abcd,Aa,Bb,Cc,Dd->ABCD",
        riemann,
        tetrad,
        tetrad,
        tetrad,
        tetrad,
        optimize=True,
    )
    electric = np.asarray(frame[0, 1:, 0, 1:], dtype=np.complex128)
    epsilon = np.zeros((3, 3, 3), dtype=float)
    epsilon[0, 1, 2] = epsilon[1, 2, 0] = epsilon[2, 0, 1] = 1.0
    epsilon[0, 2, 1] = epsilon[2, 1, 0] = epsilon[1, 0, 2] = -1.0
    magnetic = np.zeros((3, 3), dtype=np.complex128)
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for ell in range(3):
                    magnetic[i, j] += (
                        0.5 * epsilon[i, k, ell] * frame[k + 1, ell + 1, j + 1, 0]
                    )
    return TidalTensors(
        electric=electric,
        magnetic=magnetic,
        observer_label=observer.label,
    )


def schwarzschild_background_tidal(
    *,
    mass: float,
    r: float,
    observer: ObserverFrame,
) -> TidalTensors:
    """Project the exact Schwarzschild curvature into the supplied bound frame.

    The result is computed from the actual tetrad legs.  It is therefore valid
    for rotated orthonormal frames as well as the two factory principal frames;
    the observer label is never used as a substitute for the tetrad geometry.
    """

    mass_value = _positive_finite(mass, "mass")
    radius = _positive_finite(r, "r")
    if radius <= 2.0 * mass_value:
        raise ValueError("r must be outside the horizon")
    if (
        observer.background_name != "Schwarzschild"
        or observer.mass != mass_value
        or observer.radius != radius
    ):
        raise ValueError("observer frame is not bound to the requested M,r domain")
    if observer.theta is None:
        raise ValueError("Schwarzschild observer is missing theta")
    metric, first, second = schwarzschild_metric_jet(
        M=mass_value,
        r=radius,
        theta=observer.theta,
    )
    return project_vacuum_tidal_tensors(
        riemann_covariant_from_metric_jet(metric, first, second),
        observer,
    )


def arm_fractional_acceleration(electric: ArrayLike, arm: ArrayLike) -> complex:
    """Return local ``ddot L/L = -a^i E_ij a^j`` at one event.

    This is the geodesic-deviation response of infinitesimally separated,
    instantaneously comoving freely falling test masses.  It is not a finite
    arm response and does not describe an arm held static by external forces.
    """

    tensor = np.asarray(electric, dtype=np.complex128)
    direction = np.asarray(arm, dtype=np.float64)
    if tensor.shape != (3, 3) or not _finite_complex_array(tensor):
        raise ValueError("electric must be a finite complex 3x3 array")
    if direction.shape != (3,) or not np.all(np.isfinite(direction)):
        raise ValueError("arm must be a finite three-vector")
    norm = float(np.linalg.norm(direction))
    if norm == 0.0:
        raise ValueError("arm must be nonzero")
    unit = direction / norm
    return complex(-(unit @ tensor @ unit))


def michelson_fractional_acceleration(
    electric: ArrayLike,
    first_arm: ArrayLike,
    second_arm: ArrayLike,
) -> complex:
    """Return the first-minus-second differential fractional arm acceleration."""

    return arm_fractional_acceleration(
        electric, first_arm
    ) - arm_fractional_acceleration(
        electric,
        second_arm,
    )


def gauge_complete_detector_scalar(
    *,
    coordinate_perturbation: complex,
    background_gradient: ArrayLike,
    worldline_displacement: ArrayLike,
) -> OperationalGaugeScalar:
    """Complete a detector scalar with the consistently shifted worldline.

    The detector tetrad is part of the background scalar field ``Q0`` and is
    transported with the observer congruence.  Under a gauge vector ``xi``,
    ``delta Q -> delta Q-xi^mu partial_mu Q0`` and
    ``delta z^mu -> delta z^mu+xi^mu``; the returned sum is invariant.
    """

    coordinate = complex(coordinate_perturbation)
    gradient = np.asarray(background_gradient, dtype=np.complex128)
    displacement = np.asarray(worldline_displacement, dtype=np.complex128)
    if not _finite_complex(coordinate):
        raise ValueError("coordinate_perturbation must be finite")
    if gradient.shape != (4,) or displacement.shape != (4,):
        raise ValueError(
            "background_gradient and worldline_displacement must have shape (4,)"
        )
    if not _finite_complex_array(gradient) or not _finite_complex_array(displacement):
        raise ValueError("gauge-completion arrays must be finite")
    pullback = complex(displacement @ gradient)
    return OperationalGaugeScalar(
        coordinate_perturbation=coordinate,
        worldline_pullback=pullback,
        operational_perturbation=coordinate + pullback,
    )


def schwarzschild_radial_pure_gauge_oracle(
    *,
    mass: float,
    r: float,
    observer: ObserverFrame,
    first_arm: ArrayLike,
    second_arm: ArrayLike,
    gauge_vector_radial: float,
) -> RadialPureGaugeOracle:
    """Exercise a radial pure gauge through metric, curvature and frame jets."""

    mass_value = _positive_finite(mass, "mass")
    radius = _positive_finite(r, "r")
    xi_r = float(gauge_vector_radial)
    if not math.isfinite(xi_r) or xi_r == 0.0:
        raise ValueError("gauge_vector_radial must be finite and nonzero")
    if observer.theta is None:
        raise ValueError("radial gauge oracle requires a Schwarzschild observer")
    _validate_factory_radial_frame(observer)
    background = schwarzschild_background_tidal(
        mass=mass_value,
        r=radius,
        observer=observer,
    )
    signal = michelson_fractional_acceleration(
        background.electric,
        first_arm,
        second_arm,
    )
    if abs(signal.imag) > 1e-14:
        raise ValueError("background detector signal must be real")
    signal_value = float(signal.real)
    radial_derivative = -3.0 * signal_value / radius
    background_metric, background_first, background_second = schwarzschild_metric_jet(
        M=mass_value,
        r=radius,
        theta=observer.theta,
    )
    pure_gauge_metric = _constant_radial_pure_gauge_metric_jet(
        mass=mass_value,
        r=radius,
        theta=observer.theta,
        xi_r=xi_r,
        background_first=background_first,
        background_second=background_second,
    )
    background_riemann = riemann_covariant_from_metric_jet(
        background_metric,
        background_first,
        background_second,
    )
    delta_riemann = linearized_riemann_from_metric_jets(
        background_metric,
        background_first,
        background_second,
        pure_gauge_metric.value,
        pure_gauge_metric.first,
        pure_gauge_metric.second,
    )
    delta_u, delta_legs = _constant_radial_lie_dragged_frame(
        observer,
        xi_r=xi_r,
    )
    delta_electric = _linearized_electric_with_frame(
        background_riemann=background_riemann,
        delta_riemann=delta_riemann,
        observer=observer,
        delta_u=delta_u,
        delta_legs=delta_legs,
    )
    coordinate_gauge_term = michelson_fractional_acceleration(
        delta_electric,
        first_arm,
        second_arm,
    )
    expected_coordinate_term = -xi_r * radial_derivative
    consistency_residual = float(abs(coordinate_gauge_term - expected_coordinate_term))
    gradient = np.array([0.0, radial_derivative, 0.0, 0.0], dtype=np.complex128)
    displacement = np.array([0.0, xi_r, 0.0, 0.0], dtype=np.complex128)
    transformed = gauge_complete_detector_scalar(
        coordinate_perturbation=coordinate_gauge_term,
        background_gradient=gradient,
        worldline_displacement=displacement,
    )
    return RadialPureGaugeOracle(
        observer_label=observer.label,
        background_signal=signal_value,
        background_radial_derivative=radial_derivative,
        gauge_vector_radial=xi_r,
        metric_perturbation_norm=float(np.linalg.norm(pure_gauge_metric.value)),
        linearized_riemann_norm=float(np.linalg.norm(delta_riemann)),
        tetrad_perturbation_norm=float(
            np.linalg.norm(delta_u) + np.linalg.norm(delta_legs)
        ),
        expected_coordinate_lie_term=float(expected_coordinate_term),
        metric_curvature_consistency_residual=consistency_residual,
        transformed=transformed,
        absolute_residual=float(abs(transformed.operational_perturbation)),
    )


def check_radial_frame_transport(observer: ObserverFrame) -> FrameTransportCheck:
    """Evaluate the declared Fermi--Walker law from the exact connection.

    The derivative is taken along the frozen radial worldline.  For the E=1
    free-fall frame the four-acceleration and the Fermi--Walker right-hand side
    both vanish, so this simultaneously checks parallel transport.
    """

    _validate_factory_radial_frame(observer)
    assert observer.mass is not None
    assert observer.radius is not None
    assert observer.theta is not None
    metric, first, _second = schwarzschild_metric_jet(
        M=observer.mass,
        r=observer.radius,
        theta=observer.theta,
    )
    connection = _christoffel_from_metric_jet(metric, first)
    du_dr, dlegs_dr = _factory_frame_radial_derivatives(observer)
    acceleration = observer.u[1] * du_dr + np.einsum(
        "mab,a,b->m",
        connection,
        observer.u,
        observer.u,
        optimize=True,
    )
    u_covariant = metric @ observer.u
    acceleration_covariant = metric @ acceleration
    residuals = np.empty((3, 4), dtype=np.float64)
    for index, leg in enumerate(observer.spatial_legs):
        covariant_derivative = observer.u[1] * dlegs_dr[index] + np.einsum(
            "mab,a,b->m",
            connection,
            observer.u,
            leg,
            optimize=True,
        )
        fermi_walker_rhs = (
            observer.u * float(acceleration_covariant @ leg)
            - acceleration * float(u_covariant @ leg)
        )
        residuals[index] = covariant_derivative - fermi_walker_rhs
    acceleration_norm = math.sqrt(
        abs(float(acceleration @ metric @ acceleration))
    )
    return FrameTransportCheck(
        observer_label=observer.label,
        transport_law=(
            "parallel transport (geodesic special case of Fermi-Walker)"
            if observer.label == "radial_freefall_E1"
            else "Fermi-Walker transport"
        ),
        four_acceleration=acceleration,
        spatial_leg_residuals=residuals,
        acceleration_norm=acceleration_norm,
        maximum_transport_residual=float(np.max(np.abs(residuals))),
    )


def _constant_radial_pure_gauge_metric_jet(
    *,
    mass: float,
    r: float,
    theta: float,
    xi_r: float,
    background_first: NDArray[np.float64],
    background_second: NDArray[np.float64],
) -> MetricPerturbationJet:
    """Return jets of ``h_ab=-Lie_xi g_ab`` for constant ``xi^r``."""

    value = -xi_r * np.asarray(background_first[1], dtype=np.complex128)
    first = -xi_r * np.asarray(background_second[:, 1], dtype=np.complex128)
    second = np.zeros((4, 4, 4, 4), dtype=np.complex128)
    sine = math.sin(theta)
    cosine = math.cos(theta)
    third_rrr = np.zeros((4, 4), dtype=float)
    third_rrr[0, 0] = -12.0 * mass / r**4
    third_rrr[1, 1] = -12.0 * mass / (r - 2.0 * mass) ** 4
    second[1, 1] = -xi_r * third_rrr
    second[1, 2, 3, 3] = -xi_r * 4.0 * sine * cosine
    second[2, 1, 3, 3] = second[1, 2, 3, 3]
    second[2, 2, 3, 3] = -xi_r * 4.0 * r * (cosine**2 - sine**2)
    return MetricPerturbationJet(value=value, first=first, second=second)


def _constant_radial_lie_dragged_frame(
    observer: ObserverFrame,
    *,
    xi_r: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Return ``delta e=-Lie_xi e=-xi^r partial_r e`` for the frozen frames."""

    if observer.mass is None or observer.radius is None or observer.theta is None:
        raise ValueError("Lie-dragged radial frame requires Schwarzschild metadata")
    du_dr, dlegs_dr = _factory_frame_radial_derivatives(observer)
    return -xi_r * du_dr, -xi_r * dlegs_dr


def _factory_frame_radial_derivatives(
    observer: ObserverFrame,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Exact coordinate-r derivatives of the two frozen radial frames."""

    if observer.mass is None or observer.radius is None or observer.theta is None:
        raise ValueError("radial frame derivatives require Schwarzschild metadata")
    mass = observer.mass
    radius = observer.radius
    theta = observer.theta
    f = 1.0 - 2.0 * mass / radius
    fp = 2.0 * mass / radius**2
    du_dr = np.zeros(4, dtype=float)
    dlegs_dr = np.zeros((3, 4), dtype=float)
    if observer.label == "static_schwarzschild":
        du_dr[0] = -0.5 * fp / f**1.5
        dlegs_dr[0, 1] = 0.5 * fp / math.sqrt(f)
    elif observer.label == "radial_freefall_E1":
        speed = math.sqrt(2.0 * mass / radius)
        du_dr[0] = -fp / f**2
        du_dr[1] = speed / (2.0 * radius)
        dlegs_dr[0, 0] = speed / (2.0 * radius * f) + speed * fp / f**2
    else:
        raise ValueError("unsupported Schwarzschild observer for radial Lie drag")
    dlegs_dr[1, 2] = -1.0 / radius**2
    dlegs_dr[2, 3] = -1.0 / (radius**2 * math.sin(theta))
    return du_dr, dlegs_dr


def _christoffel_from_metric_jet(
    metric: NDArray[np.float64],
    first: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Return ``Gamma^mu_ab`` from ``partial_alpha g_mu_nu``."""

    inverse = np.linalg.inv(np.asarray(metric, dtype=np.float64))
    derivative = np.asarray(first, dtype=np.float64)
    connection = np.empty((4, 4, 4), dtype=np.float64)
    for mu in range(4):
        for alpha in range(4):
            for beta in range(4):
                connection[mu, alpha, beta] = 0.5 * sum(
                    inverse[mu, nu]
                    * (
                        derivative[alpha, nu, beta]
                        + derivative[beta, nu, alpha]
                        - derivative[nu, alpha, beta]
                    )
                    for nu in range(4)
                )
    return connection


def _validate_factory_radial_frame(observer: ObserverFrame) -> None:
    """Require the exact factory frame used by the analytic Lie-drag jets."""

    if observer.mass is None or observer.radius is None or observer.theta is None:
        raise ValueError("radial gauge oracle requires bound Schwarzschild metadata")
    factories = {
        "static_schwarzschild": static_schwarzschild_observer,
        "radial_freefall_E1": radial_freefall_from_infinity_observer,
    }
    factory = factories.get(observer.label)
    if factory is None:
        raise ValueError("radial gauge oracle requires a frozen factory frame")
    expected = factory(
        mass=observer.mass,
        r=observer.radius,
        theta=observer.theta,
    )
    if not (
        observer.worldline == expected.worldline
        and observer.tetrad_transport == expected.tetrad_transport
        and observer.coordinates == expected.coordinates
        and np.array_equal(observer.u, expected.u)
        and np.array_equal(observer.spatial_legs, expected.spatial_legs)
    ):
        raise ValueError("radial gauge oracle requires the exact factory tetrad")


def _linearized_electric_with_frame(
    *,
    background_riemann: NDArray[np.complex128],
    delta_riemann: NDArray[np.complex128],
    observer: ObserverFrame,
    delta_u: NDArray[np.float64],
    delta_legs: NDArray[np.float64],
) -> NDArray[np.complex128]:
    """Linearize ``R(u,e_i,u,e_j)`` including all four frame legs."""

    u = observer.u
    legs = observer.spatial_legs
    result = np.empty((3, 3), dtype=np.complex128)
    for i in range(3):
        for j in range(3):
            result[i, j] = np.einsum(
                "abcd,a,b,c,d->",
                delta_riemann,
                u,
                legs[i],
                u,
                legs[j],
            )
            result[i, j] += np.einsum(
                "abcd,a,b,c,d->",
                background_riemann,
                delta_u,
                legs[i],
                u,
                legs[j],
            )
            result[i, j] += np.einsum(
                "abcd,a,b,c,d->",
                background_riemann,
                u,
                delta_legs[i],
                u,
                legs[j],
            )
            result[i, j] += np.einsum(
                "abcd,a,b,c,d->",
                background_riemann,
                u,
                legs[i],
                delta_u,
                legs[j],
            )
            result[i, j] += np.einsum(
                "abcd,a,b,c,d->",
                background_riemann,
                u,
                legs[i],
                u,
                delta_legs[j],
            )
    if not _finite_complex_array(result):
        raise RuntimeError("linearized observer electric tensor is non-finite")
    return result


def _schwarzschild_inputs(
    mass: float,
    r: float,
    theta: float,
) -> tuple[float, float, float, float]:
    mass_value = _positive_finite(mass, "mass")
    radius = _positive_finite(r, "r")
    theta_value = float(theta)
    if radius <= 2.0 * mass_value:
        raise ValueError("r must be outside the horizon")
    if not math.isfinite(theta_value) or not 0.0 < theta_value < math.pi:
        raise ValueError("theta must lie strictly inside (0, pi)")
    return mass_value, radius, theta_value, 1.0 - 2.0 * mass_value / radius


def _schwarzschild_metric(mass: float, r: float, theta: float) -> NDArray[np.float64]:
    f = 1.0 - 2.0 * mass / r
    return np.diag([-f, 1.0 / f, r**2, r**2 * math.sin(theta) ** 2])


def _positive_finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def _finite_complex(value: complex) -> bool:
    return math.isfinite(value.real) and math.isfinite(value.imag)


def _finite_complex_array(values: NDArray[np.complex128]) -> bool:
    return bool(np.all(np.isfinite(values.real)) and np.all(np.isfinite(values.imag)))


__all__ = [
    "FrameTransportCheck",
    "ObserverFrame",
    "OperationalGaugeScalar",
    "RadialPureGaugeOracle",
    "TidalTensors",
    "arm_fractional_acceleration",
    "cartesian_inertial_observer",
    "check_radial_frame_transport",
    "gauge_complete_detector_scalar",
    "michelson_fractional_acceleration",
    "project_vacuum_tidal_tensors",
    "radial_freefall_from_infinity_observer",
    "schwarzschild_background_tidal",
    "schwarzschild_radial_pure_gauge_oracle",
    "static_schwarzschild_observer",
]
