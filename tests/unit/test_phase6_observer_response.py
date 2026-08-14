from __future__ import annotations

import numpy as np
import pytest

from schwgw.validation.phase6_observer_response import (
    ObserverFrame,
    arm_fractional_acceleration,
    cartesian_inertial_observer,
    check_radial_frame_transport,
    michelson_fractional_acceleration,
    project_vacuum_tidal_tensors,
    radial_freefall_from_infinity_observer,
    schwarzschild_background_tidal,
    schwarzschild_radial_pure_gauge_oracle,
    static_schwarzschild_observer,
)


def _flat_tt_riemann(*, k: float, plus: complex, cross: complex) -> np.ndarray:
    metric_perturbation = np.zeros((4, 4), dtype=np.complex128)
    metric_perturbation[1, 1] = plus
    metric_perturbation[2, 2] = -plus
    metric_perturbation[1, 2] = metric_perturbation[2, 1] = cross
    covector = np.array([-k, 0.0, 0.0, k], dtype=np.complex128)
    second = -np.einsum("m,n,ab->abmn", covector, covector, metric_perturbation)
    return 0.5 * (
        np.einsum("adbc->abcd", second)
        + np.einsum("bcad->abcd", second)
        - np.einsum("acbd->abcd", second)
        - np.einsum("bdac->abcd", second)
    )


def test_static_and_freefall_frames_are_orthonormal_and_distinct() -> None:
    static = static_schwarzschild_observer(mass=1.0, r=10.0, theta=1.1)
    freefall = radial_freefall_from_infinity_observer(mass=1.0, r=10.0, theta=1.1)
    assert static.label != freefall.label
    assert static.u[1] == 0.0
    assert freefall.u[1] < 0.0
    assert "Fermi-Walker" in static.tetrad_transport
    assert "Fermi-Walker" in freefall.tetrad_transport

    static_transport = check_radial_frame_transport(static)
    freefall_transport = check_radial_frame_transport(freefall)
    assert static_transport.acceleration_norm > 0.0
    assert static_transport.maximum_transport_residual < 2.0e-15
    assert freefall_transport.acceleration_norm < 2.0e-15
    assert freefall_transport.maximum_transport_residual < 2.0e-15
    assert "parallel transport" in freefall_transport.transport_law


def test_flat_tt_projection_recovers_electric_tidal_and_detector_response() -> None:
    k = 2.0
    plus = 0.7 - 0.1j
    cross = -0.2 + 0.4j
    projected = project_vacuum_tidal_tensors(
        _flat_tt_riemann(k=k, plus=plus, cross=cross),
        cartesian_inertial_observer(),
    )
    expected = (
        0.5
        * k**2
        * np.array(
            [[plus, cross, 0.0], [cross, -plus, 0.0], [0.0, 0.0, 0.0]],
            dtype=np.complex128,
        )
    )
    np.testing.assert_allclose(projected.electric, expected, atol=2e-15)
    np.testing.assert_allclose(projected.electric, projected.electric.T, atol=2e-15)
    assert np.trace(projected.electric) == pytest.approx(0.0j, abs=2e-15)
    assert arm_fractional_acceleration(projected.electric, [1, 0, 0]) == pytest.approx(
        -0.5 * k**2 * plus
    )
    assert michelson_fractional_acceleration(
        projected.electric,
        [1, 0, 0],
        [0, 1, 0],
    ) == pytest.approx(-(k**2) * plus)


@pytest.mark.parametrize(
    "observer_factory",
    [static_schwarzschild_observer, radial_freefall_from_infinity_observer],
)
def test_schwarzschild_background_and_radial_pure_gauge_detector_oracle(
    observer_factory,
) -> None:
    observer = observer_factory(mass=1.0, r=12.0, theta=0.9)
    tidal = schwarzschild_background_tidal(mass=1.0, r=12.0, observer=observer)
    np.testing.assert_allclose(np.trace(tidal.electric), 0.0, atol=1e-18)
    np.testing.assert_allclose(tidal.magnetic, np.zeros((3, 3)), atol=1e-18)
    oracle = schwarzschild_radial_pure_gauge_oracle(
        mass=1.0,
        r=12.0,
        observer=observer,
        first_arm=[1.0, 0.0, 0.0],
        second_arm=[0.0, 1.0, 0.0],
        gauge_vector_radial=0.17,
    )
    assert oracle.transformed.coordinate_perturbation != 0.0j
    assert oracle.transformed.worldline_pullback != 0.0j
    assert oracle.metric_perturbation_norm > 0.0
    assert oracle.linearized_riemann_norm > 0.0
    assert oracle.tetrad_perturbation_norm > 0.0
    assert "metric jets" in oracle.pipeline
    assert oracle.metric_curvature_consistency_residual < 1.0e-18
    assert oracle.transformed.coordinate_perturbation == pytest.approx(
        -oracle.transformed.worldline_pullback
    )
    assert oracle.absolute_residual < 1e-18


def test_schwarzschild_observer_domain_binding_fails_closed() -> None:
    observer = static_schwarzschild_observer(mass=1.0, r=10.0, theta=0.9)

    with pytest.raises(ValueError, match="not bound"):
        schwarzschild_background_tidal(mass=1.0, r=12.0, observer=observer)
    with pytest.raises(ValueError, match="not bound"):
        schwarzschild_background_tidal(mass=2.0, r=10.0, observer=observer)


def test_background_tidal_projects_actual_rotated_tetrad_and_gauge_oracle_rejects_it() -> (
    None
):
    base = static_schwarzschild_observer(mass=1.0, r=10.0, theta=0.9)
    angle = 0.3
    rotation = np.array(
        [
            [np.cos(angle), np.sin(angle), 0.0],
            [-np.sin(angle), np.cos(angle), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    rotated = ObserverFrame(
        label=base.label,
        worldline=base.worldline,
        tetrad_transport=base.tetrad_transport,
        coordinates=base.coordinates,
        background_name=base.background_name,
        mass=base.mass,
        radius=base.radius,
        theta=base.theta,
        metric=base.metric,
        u=base.u,
        spatial_legs=rotation @ base.spatial_legs,
    )
    principal = schwarzschild_background_tidal(
        mass=1.0,
        r=10.0,
        observer=base,
    )
    projected = schwarzschild_background_tidal(
        mass=1.0,
        r=10.0,
        observer=rotated,
    )
    np.testing.assert_allclose(
        projected.electric,
        rotation @ principal.electric @ rotation.T,
        rtol=2e-13,
        atol=2e-15,
    )
    with pytest.raises(ValueError, match="exact factory tetrad"):
        schwarzschild_radial_pure_gauge_oracle(
            mass=1.0,
            r=10.0,
            observer=rotated,
            first_arm=[1.0, 0.0, 0.0],
            second_arm=[0.0, 1.0, 0.0],
            gauge_vector_radial=0.1,
        )
