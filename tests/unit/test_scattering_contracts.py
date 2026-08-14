from __future__ import annotations

import hashlib
import json
from dataclasses import FrozenInstanceError, MISSING, fields
from typing import Any

import numpy as np
import pytest

from schwgw.scattering.contracts import (
    AngularModeCouplingProtocol,
    ArtifactWriterProtocol,
    BackgroundGeometryProtocol,
    BoundaryAsymptoticsProtocol,
    ChannelSpec,
    ConventionMetadata,
    DomainDriverProtocol,
    IncidentSourceProtocol,
    ModeKey,
    ObservableProjectorProtocol,
    ObserverPoint,
    PotentialProviderProtocol,
    ProvenanceIdentity,
    RadialStateBatch,
    RadialSystemProtocol,
    SolverBackendProtocol,
)


_IDENTITY_FIELDS = (
    "implementation_sha256",
    "physics_sha256",
    "solver_sha256",
    "config_sha256",
    "source_sha256",
    "gate_sha256",
)


def _identity_values() -> dict[str, str]:
    return {
        name: character * 64
        for name, character in zip(_IDENTITY_FIELDS, "012345", strict=True)
    }


def _identity(**overrides: str) -> ProvenanceIdentity:
    values = _identity_values()
    values.update(overrides)
    return ProvenanceIdentity(**values)


def _convention_values() -> dict[str, object]:
    return {
        "units": "G=c=M=1",
        "metric_signature": "(-,+,+,+)",
        "fourier_sign": "exp(-i k t)",
        "tortoise_definition": "r_*=r+2M log(r/(2M)-1)",
        "ingoing_phase": "exp(-i k r_*)",
        "outgoing_phase": "exp(+i k r_*)",
        "normalization": "current RW/Zerilli master-variable normalization",
        "phase_convention": "-A_out/((-1)^ell A_in)",
        "provenance": _identity(),
    }


def _scalar_channel() -> ChannelSpec:
    return ChannelSpec(
        name="toy_scalar",
        field_spin=0,
        polarization="toy_scalar_polarization",
        parity="none",
        radial_structure="scalar",
        component_names=("amplitude",),
        physical_claim=False,
    )


def _coupled_channel() -> ChannelSpec:
    return ChannelSpec(
        name="toy_coupled",
        field_spin=1,
        polarization="toy_mixed_polarization",
        parity="mixed",
        radial_structure="coupled",
        component_names=("u", "v"),
        physical_claim=False,
    )


def test_provenance_identity_has_exactly_six_required_sha256_components() -> None:
    identity = _identity()

    assert tuple(field.name for field in fields(identity)) == _IDENTITY_FIELDS
    for field in fields(identity):
        assert field.default is MISSING
        assert field.default_factory is MISSING
        assert getattr(identity, field.name) == _identity_values()[field.name]


@pytest.mark.parametrize("missing_field", _IDENTITY_FIELDS)
def test_provenance_identity_fails_closed_when_a_component_is_missing(
    missing_field: str,
) -> None:
    values = _identity_values()
    values.pop(missing_field)

    with pytest.raises(TypeError):
        ProvenanceIdentity(**values)


@pytest.mark.parametrize("field_name", _IDENTITY_FIELDS)
@pytest.mark.parametrize(
    "bad_hash",
    (
        "",
        "a" * 63,
        "a" * 65,
        "g" * 64,
        "A" * 64,
        None,
    ),
)
def test_provenance_identity_rejects_every_noncanonical_hash(
    field_name: str,
    bad_hash: str | None,
) -> None:
    values: dict[str, Any] = _identity_values()
    values[field_name] = bad_hash

    with pytest.raises((TypeError, ValueError)):
        ProvenanceIdentity(**values)


def test_provenance_identity_canonical_digest_is_stable_and_auditable() -> None:
    values = _identity_values()
    identity = ProvenanceIdentity(**dict(reversed(tuple(values.items()))))
    canonical_json = json.dumps(
        values,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    expected = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    assert identity.canonical_digest == expected
    assert len(identity.canonical_digest) == 64
    assert identity.canonical_digest == _identity().canonical_digest
    with pytest.raises((AttributeError, FrozenInstanceError)):
        identity.canonical_digest = "f" * 64


def test_convention_metadata_requires_every_scientific_convention_explicitly() -> None:
    values = _convention_values()
    convention = ConventionMetadata(**values)
    required_fields = tuple(values)
    convention_fields = {field.name: field for field in fields(convention)}

    assert tuple(convention_fields) == required_fields
    for name, expected in values.items():
        assert convention_fields[name].default is MISSING
        assert convention_fields[name].default_factory is MISSING
        assert getattr(convention, name) == expected

    with pytest.raises(FrozenInstanceError):
        convention.fourier_sign = "exp(+i k t)"


@pytest.mark.parametrize("missing_field", tuple(_convention_values()))
def test_convention_metadata_cannot_silently_default_a_convention(
    missing_field: str,
) -> None:
    values = _convention_values()
    values.pop(missing_field)

    with pytest.raises(TypeError):
        ConventionMetadata(**values)


def test_convention_metadata_requires_typed_provenance() -> None:
    values = _convention_values()
    values["provenance"] = "0" * 64

    with pytest.raises(TypeError):
        ConventionMetadata(**values)


def test_channel_spec_represents_scalar_and_coupled_radial_structures() -> None:
    scalar = _scalar_channel()
    coupled = _coupled_channel()

    assert scalar.radial_structure == "scalar"
    assert scalar.component_names == ("amplitude",)
    assert scalar.physical_claim is False

    assert coupled.radial_structure == "coupled"
    assert coupled.component_names == ("u", "v")
    assert coupled.physical_claim is False
    with pytest.raises(FrozenInstanceError):
        coupled.physical_claim = True


@pytest.mark.parametrize(
    ("radial_structure", "component_names"),
    (
        ("scalar", ()),
        ("scalar", ("u", "v")),
        ("coupled", ("u",)),
        ("coupled", ("u", "u")),
        ("unknown", ("u",)),
    ),
)
def test_channel_spec_rejects_inconsistent_or_ambiguous_structure(
    radial_structure: str,
    component_names: tuple[str, ...],
) -> None:
    with pytest.raises(ValueError):
        ChannelSpec(
            name="invalid_toy",
            field_spin=0,
            polarization="toy",
            parity="none",
            radial_structure=radial_structure,
            component_names=component_names,
            physical_claim=False,
        )


def test_mode_key_has_deterministic_scientific_order() -> None:
    keys = [
        ModeKey(frequency=1.0, ell=0, m=0, channel="alpha"),
        ModeKey(frequency=0.5, ell=2, m=1, channel="alpha"),
        ModeKey(frequency=0.5, ell=2, m=-1, channel="beta"),
        ModeKey(frequency=0.5, ell=1, m=0, channel="zeta"),
        ModeKey(frequency=0.5, ell=2, m=-1, channel="alpha"),
    ]

    assert sorted(reversed(keys)) == [
        ModeKey(frequency=0.5, ell=1, m=0, channel="zeta"),
        ModeKey(frequency=0.5, ell=2, m=-1, channel="alpha"),
        ModeKey(frequency=0.5, ell=2, m=-1, channel="beta"),
        ModeKey(frequency=0.5, ell=2, m=1, channel="alpha"),
        ModeKey(frequency=1.0, ell=0, m=0, channel="alpha"),
    ]


def test_observer_point_preserves_a_generic_coordinate_chart() -> None:
    point = ObserverPoint(
        label="toy_observer_7",
        coordinate_system="toy_rho_chi",
        coordinates=(3.5, -0.25),
    )

    assert point.label == "toy_observer_7"
    assert point.coordinate_system == "toy_rho_chi"
    assert point.coordinates == (3.5, -0.25)
    with pytest.raises(FrozenInstanceError):
        point.coordinates = (0.0, 0.0)


def test_radial_state_batch_preserves_scalar_complex_shape_and_finite_pattern() -> None:
    batch = RadialStateBatch(
        radial_coordinates=np.array([1.0, 2.0, 3.0]),
        values=np.array(
            [[1.0 + 2.0j], [complex(np.nan, np.nan)], [-3.0 + 0.5j]],
            dtype=np.complex128,
        ),
        derivatives=np.array(
            [[0.5 - 1.0j], [complex(np.nan, np.nan)], [4.0 + 2.0j]],
            dtype=np.complex128,
        ),
        component_names=("amplitude",),
    )

    assert batch.shape == (3, 1)
    assert batch.values.shape == batch.derivatives.shape
    assert batch.component_names == ("amplitude",)
    assert np.issubdtype(batch.values.dtype, np.complexfloating)
    assert np.issubdtype(batch.derivatives.dtype, np.complexfloating)
    np.testing.assert_array_equal(
        batch.finite_mask,
        np.array([[True], [False], [True]]),
    )


def test_radial_state_batch_supports_coupled_off_diagonal_state() -> None:
    values = np.array(
        [
            [1.0 + 0.0j, 2.0 - 1.0j],
            [complex(np.nan, np.nan), -3.0 + 4.0j],
        ],
        dtype=np.complex128,
    )
    derivatives = np.array(
        [
            [0.25j, 1.0 + 1.0j],
            [complex(np.nan, np.nan), 2.0 - 0.5j],
        ],
        dtype=np.complex128,
    )
    batch = RadialStateBatch(
        radial_coordinates=np.array([-1.0, 1.0]),
        values=values,
        derivatives=derivatives,
        component_names=("u", "v"),
    )

    assert batch.shape == (2, 2)
    assert batch.component_names == ("u", "v")
    np.testing.assert_array_equal(
        batch.finite_mask,
        np.array([[True, True], [False, True]]),
    )


def test_radial_state_batch_copies_and_freezes_every_array() -> None:
    radial_coordinates = np.array([1.0, 2.0])
    values = np.array([[1.0 + 2.0j], [3.0 + 4.0j]])
    derivatives = np.array([[5.0 + 6.0j], [7.0 + 8.0j]])
    expected_coordinates = radial_coordinates.copy()
    expected_values = values.copy()
    expected_derivatives = derivatives.copy()

    batch = RadialStateBatch(
        radial_coordinates=radial_coordinates,
        values=values,
        derivatives=derivatives,
        component_names=("amplitude",),
    )
    radial_coordinates[:] = -100.0
    values[:] = -200.0
    derivatives[:] = -300.0

    np.testing.assert_array_equal(batch.radial_coordinates, expected_coordinates)
    np.testing.assert_array_equal(batch.values, expected_values)
    np.testing.assert_array_equal(batch.derivatives, expected_derivatives)
    assert not np.shares_memory(batch.radial_coordinates, radial_coordinates)
    assert not np.shares_memory(batch.values, values)
    assert not np.shares_memory(batch.derivatives, derivatives)
    for array in (
        batch.radial_coordinates,
        batch.values,
        batch.derivatives,
        batch.finite_mask,
    ):
        assert array.flags.writeable is False
        with pytest.raises(ValueError):
            array.flat[0] = 0


@pytest.mark.parametrize(
    ("radial_coordinates", "values", "derivatives", "component_names"),
    (
        (
            np.array([1.0, 2.0]),
            np.ones((3, 1), dtype=complex),
            np.ones((3, 1), dtype=complex),
            ("u",),
        ),
        (
            np.array([1.0, 2.0]),
            np.ones((2, 1), dtype=complex),
            np.ones((2, 2), dtype=complex),
            ("u",),
        ),
        (
            np.array([1.0, 2.0]),
            np.ones((2, 2), dtype=complex),
            np.ones((2, 2), dtype=complex),
            ("u",),
        ),
        (
            np.array([1.0, 2.0]),
            np.ones(2, dtype=complex),
            np.ones(2, dtype=complex),
            ("u",),
        ),
    ),
)
def test_radial_state_batch_rejects_shape_or_component_mismatch(
    radial_coordinates: np.ndarray,
    values: np.ndarray,
    derivatives: np.ndarray,
    component_names: tuple[str, ...],
) -> None:
    with pytest.raises(ValueError):
        RadialStateBatch(
            radial_coordinates=radial_coordinates,
            values=values,
            derivatives=derivatives,
            component_names=component_names,
        )


class _ToyBackground:
    name = "toy_two_function_geometry"
    coordinate_name = "rho"
    physical_claim = False

    def coordinate_domain(self) -> tuple[float, float]:
        return (-4.0, 9.0)

    def tortoise_coordinate(self, radial_coordinates: np.ndarray) -> np.ndarray:
        radial_coordinates = np.asarray(radial_coordinates, dtype=float)
        return radial_coordinates + 0.1 * radial_coordinates**3

    def tortoise_jacobian(self, radial_coordinates: np.ndarray) -> np.ndarray:
        radial_coordinates = np.asarray(radial_coordinates, dtype=float)
        return 1.0 + 0.3 * radial_coordinates**2


class _ToyPotentialProvider:
    name = "toy_matrix_potential"
    physical_claim = False

    def potential_matrix(
        self,
        radial_coordinate: float,
        mode: ModeKey,
        channel: ChannelSpec,
        background: BackgroundGeometryProtocol,
    ) -> np.ndarray:
        del mode, channel, background
        return np.array(
            [[radial_coordinate, 0.25], [-0.5, -radial_coordinate]],
            dtype=np.complex128,
        )


class _ToyRadialSystem:
    name = "toy_coupled_first_order_system"
    component_names = ("u", "v")
    physical_claim = False

    def rhs(
        self,
        radial_coordinate: float,
        state: np.ndarray,
        mode: ModeKey,
        channel: ChannelSpec,
        background: BackgroundGeometryProtocol,
        potential: PotentialProviderProtocol,
    ) -> np.ndarray:
        matrix = potential.potential_matrix(
            radial_coordinate,
            mode,
            channel,
            background,
        )
        return matrix @ np.asarray(state, dtype=np.complex128)


class _ToyBoundaryAsymptotics:
    name = "toy_two_ended_boundary"
    physical_claim = False

    def inner_state(
        self,
        mode: ModeKey,
        channel: ChannelSpec,
        background: BackgroundGeometryProtocol,
    ) -> np.ndarray:
        del mode, background
        return np.ones(len(channel.component_names), dtype=np.complex128)

    def outer_basis(
        self,
        radial_coordinate: float,
        mode: ModeKey,
        channel: ChannelSpec,
        background: BackgroundGeometryProtocol,
    ) -> dict[str, np.ndarray]:
        del radial_coordinate, mode, background
        size = len(channel.component_names)
        return {
            "left": np.eye(size, dtype=np.complex128),
            "right": 1j * np.eye(size, dtype=np.complex128),
        }


class _ToyIncidentSource:
    name = "toy_sparse_source"
    physical_claim = False

    def supported_m_values(self, ell: int) -> tuple[int, ...] | None:
        return (0, ell, -1)

    def amplitude(self, mode: ModeKey, channel: ChannelSpec) -> np.ndarray:
        del mode
        return np.ones(len(channel.component_names), dtype=np.complex128)


class _ToyAngularModeCoupling:
    name = "toy_full_angular_fallback"
    physical_claim = False

    def supported_m_values(self, ell: int) -> tuple[int, ...] | None:
        del ell
        return None

    def evaluate(
        self,
        mode: ModeKey,
        observer: ObserverPoint,
        channel: ChannelSpec,
    ) -> np.ndarray:
        del mode, observer
        return np.ones(len(channel.component_names), dtype=np.complex128)

    def coupling(
        self,
        source_mode: ModeKey,
        target_mode: ModeKey,
        channel: ChannelSpec,
    ) -> complex:
        del source_mode, target_mode, channel
        return 0.125j


class _ToyDomainDriver:
    domain_kind = "time"
    physical_claim = False

    def run(self, problem: object, backend: SolverBackendProtocol) -> object:
        del backend
        return problem


class _ToySolverBackend:
    name = "toy_vector_backend"
    physical_claim = False

    def solve(
        self,
        system: RadialSystemProtocol,
        boundary: BoundaryAsymptoticsProtocol,
        mode: ModeKey,
        channel: ChannelSpec,
        background: BackgroundGeometryProtocol,
        potential: PotentialProviderProtocol,
        radial_coordinates: np.ndarray,
    ) -> RadialStateBatch:
        del system, boundary, mode, background, potential
        coordinates = np.asarray(radial_coordinates, dtype=float)
        shape = (len(coordinates), len(channel.component_names))
        return RadialStateBatch(
            radial_coordinates=coordinates,
            values=np.ones(shape, dtype=np.complex128),
            derivatives=1j * np.ones(shape, dtype=np.complex128),
            component_names=channel.component_names,
        )


class _ToyObservableProjector:
    name = "toy_vector_projector"
    physical_claim = False

    def project(
        self,
        radial_states: dict[ModeKey, RadialStateBatch],
        observers: tuple[ObserverPoint, ...],
        angular: AngularModeCouplingProtocol,
    ) -> dict[str, object]:
        del angular
        return {"state_count": len(radial_states), "observer_count": len(observers)}


class _ToyArtifactWriter:
    format_name = "toy_in_memory"
    physical_claim = False

    def write(
        self,
        artifact: object,
        conventions: ConventionMetadata,
    ) -> dict[str, object]:
        return {"artifact": artifact, "conventions": conventions}


@pytest.mark.parametrize(
    ("protocol", "implementation"),
    (
        (BackgroundGeometryProtocol, _ToyBackground()),
        (PotentialProviderProtocol, _ToyPotentialProvider()),
        (RadialSystemProtocol, _ToyRadialSystem()),
        (BoundaryAsymptoticsProtocol, _ToyBoundaryAsymptotics()),
        (IncidentSourceProtocol, _ToyIncidentSource()),
        (AngularModeCouplingProtocol, _ToyAngularModeCoupling()),
        (DomainDriverProtocol, _ToyDomainDriver()),
        (SolverBackendProtocol, _ToySolverBackend()),
        (ObservableProjectorProtocol, _ToyObservableProjector()),
        (ArtifactWriterProtocol, _ToyArtifactWriter()),
    ),
)
def test_protocols_are_runtime_checkable_and_structural(
    protocol: type[object],
    implementation: object,
) -> None:
    assert isinstance(implementation, protocol)
    assert not isinstance(object(), protocol)


def test_generic_contract_accepts_non_schwarzschild_coupled_time_domain_mocks() -> None:
    background = _ToyBackground()
    potential = _ToyPotentialProvider()
    system = _ToyRadialSystem()
    channel = _coupled_channel()
    mode = ModeKey(frequency=0.75, ell=3, m=1, channel=channel.name)
    state = np.array([1.0 + 0.5j, -2.0j])

    matrix = potential.potential_matrix(0.4, mode, channel, background)
    derivative = system.rhs(0.4, state, mode, channel, background, potential)

    assert background.coordinate_name == "rho"
    assert background.physical_claim is False
    assert matrix.shape == (2, 2)
    assert matrix[0, 1] != 0.0
    assert matrix[1, 0] != 0.0
    assert derivative.shape == (2,)
    assert _ToyDomainDriver.domain_kind == "time"
    components = (
        background,
        potential,
        system,
        _ToyBoundaryAsymptotics(),
        _ToyIncidentSource(),
        _ToyAngularModeCoupling(),
        _ToyDomainDriver(),
        _ToySolverBackend(),
        _ToyObservableProjector(),
        _ToyArtifactWriter(),
    )
    assert all(component.physical_claim is False for component in components)


def test_source_and_angular_protocols_distinguish_ordered_sparse_support_from_fallback() -> None:
    sparse_source = _ToyIncidentSource()
    full_fallback = _ToyAngularModeCoupling()

    assert sparse_source.supported_m_values(3) == (0, 3, -1)
    assert isinstance(sparse_source.supported_m_values(3), tuple)
    assert full_fallback.supported_m_values(3) is None
