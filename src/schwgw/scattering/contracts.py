"""Typed, implementation-neutral contracts for scattering pipelines."""

from __future__ import annotations

import hashlib
import json
import math
import numbers
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Protocol, Sequence, runtime_checkable

import numpy as np


_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
_RADIAL_STRUCTURES = frozenset({"scalar", "coupled"})


def _required_text(value: object, *, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string.")
    if not value.strip():
        raise ValueError(f"{name} must be non-empty.")
    return value


def _sha256(value: object, *, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a lowercase SHA-256 string.")
    if _SHA256_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{name} must contain exactly 64 lowercase hex characters.")
    return value


def _component_names(value: object, *, name: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)):
        raise TypeError(f"{name} must be a sequence of component names.")
    try:
        names = tuple(value)  # type: ignore[arg-type]
    except TypeError as error:
        raise TypeError(f"{name} must be a sequence of component names.") from error
    if not names:
        raise ValueError(f"{name} must contain at least one component.")
    normalized = tuple(
        _required_text(component, name=f"{name}[{index}]")
        for index, component in enumerate(names)
    )
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{name} must contain unique component names.")
    return normalized


def _readonly_copy(value: object, *, dtype: np.dtype[object]) -> np.ndarray:
    """Return an owning-independent array backed by immutable bytes."""

    copied = np.array(value, dtype=dtype, copy=True, order="C")
    immutable = np.frombuffer(copied.tobytes(order="C"), dtype=copied.dtype)
    return immutable.reshape(copied.shape)


@dataclass(frozen=True)
class ProvenanceIdentity:
    """Complete identity boundary for reusable numerical evidence."""

    implementation_sha256: str
    physics_sha256: str
    solver_sha256: str
    config_sha256: str
    source_sha256: str
    gate_sha256: str

    def __post_init__(self) -> None:
        for name in (
            "implementation_sha256",
            "physics_sha256",
            "solver_sha256",
            "config_sha256",
            "source_sha256",
            "gate_sha256",
        ):
            object.__setattr__(
                self,
                name,
                _sha256(getattr(self, name), name=name),
            )

    @property
    def canonical_digest(self) -> str:
        """SHA-256 of the canonical six-component identity payload."""

        payload = {
            "implementation_sha256": self.implementation_sha256,
            "physics_sha256": self.physics_sha256,
            "solver_sha256": self.solver_sha256,
            "config_sha256": self.config_sha256,
            "source_sha256": self.source_sha256,
            "gate_sha256": self.gate_sha256,
        }
        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ConventionMetadata:
    """Explicit scientific conventions attached to a scattering result."""

    units: str
    metric_signature: str
    fourier_sign: str
    tortoise_definition: str
    ingoing_phase: str
    outgoing_phase: str
    normalization: str
    phase_convention: str
    provenance: ProvenanceIdentity

    def __post_init__(self) -> None:
        for name in (
            "units",
            "metric_signature",
            "fourier_sign",
            "tortoise_definition",
            "ingoing_phase",
            "outgoing_phase",
            "normalization",
            "phase_convention",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(getattr(self, name), name=name),
            )
        if not isinstance(self.provenance, ProvenanceIdentity):
            raise TypeError("provenance must be a ProvenanceIdentity.")


@dataclass(frozen=True)
class ChannelSpec:
    """Field and radial-state structure for one scattering channel."""

    name: str
    field_spin: float
    polarization: str
    parity: str
    radial_structure: str
    component_names: tuple[str, ...]
    physical_claim: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _required_text(self.name, name="name"))
        if isinstance(self.field_spin, bool) or not isinstance(
            self.field_spin,
            numbers.Real,
        ):
            raise TypeError("field_spin must be a finite real number.")
        spin = float(self.field_spin)
        if not math.isfinite(spin):
            raise ValueError("field_spin must be finite.")
        object.__setattr__(self, "field_spin", spin)
        object.__setattr__(
            self,
            "polarization",
            _required_text(self.polarization, name="polarization"),
        )
        object.__setattr__(self, "parity", _required_text(self.parity, name="parity"))
        structure = _required_text(
            self.radial_structure,
            name="radial_structure",
        )
        if structure not in _RADIAL_STRUCTURES:
            raise ValueError("radial_structure must be 'scalar' or 'coupled'.")
        object.__setattr__(self, "radial_structure", structure)
        components = _component_names(
            self.component_names,
            name="component_names",
        )
        if structure == "scalar" and len(components) != 1:
            raise ValueError("a scalar channel must have exactly one component.")
        if structure == "coupled" and len(components) < 2:
            raise ValueError("a coupled channel must have at least two components.")
        object.__setattr__(self, "component_names", components)
        if not isinstance(self.physical_claim, bool):
            raise TypeError("physical_claim must be an explicit bool.")


@dataclass(frozen=True, order=True)
class ModeKey:
    """Totally ordered scientific key used for deterministic reductions."""

    frequency: float
    ell: int
    m: int
    channel: str

    def __post_init__(self) -> None:
        if isinstance(self.frequency, bool) or not isinstance(
            self.frequency,
            numbers.Real,
        ):
            raise TypeError("frequency must be a finite real number.")
        frequency = float(self.frequency)
        if not math.isfinite(frequency):
            raise ValueError("frequency must be finite.")
        object.__setattr__(self, "frequency", frequency)
        for name in ("ell", "m"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, numbers.Integral):
                raise TypeError(f"{name} must be an integer.")
            object.__setattr__(self, name, int(value))
        object.__setattr__(
            self,
            "channel",
            _required_text(self.channel, name="channel"),
        )


@dataclass(frozen=True)
class ObserverPoint:
    """A point in an explicitly named, otherwise unrestricted chart."""

    label: str
    coordinate_system: str
    coordinates: tuple[float, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "label", _required_text(self.label, name="label"))
        object.__setattr__(
            self,
            "coordinate_system",
            _required_text(self.coordinate_system, name="coordinate_system"),
        )
        if isinstance(self.coordinates, (str, bytes)):
            raise TypeError("coordinates must be a sequence of finite real numbers.")
        try:
            raw_coordinates = tuple(self.coordinates)
        except TypeError as error:
            raise TypeError(
                "coordinates must be a sequence of finite real numbers."
            ) from error
        if not raw_coordinates:
            raise ValueError("coordinates must contain at least one value.")
        coordinates: list[float] = []
        for index, coordinate in enumerate(raw_coordinates):
            if isinstance(coordinate, bool) or not isinstance(
                coordinate,
                numbers.Real,
            ):
                raise TypeError(f"coordinates[{index}] must be a real number.")
            normalized = float(coordinate)
            if not math.isfinite(normalized):
                raise ValueError(f"coordinates[{index}] must be finite.")
            coordinates.append(normalized)
        object.__setattr__(self, "coordinates", tuple(coordinates))


@dataclass(frozen=True, eq=False)
class RadialStateBatch:
    """Immutable scalar or coupled radial states at multiple coordinates."""

    radial_coordinates: np.ndarray
    values: np.ndarray
    derivatives: np.ndarray
    component_names: tuple[str, ...]
    finite_mask: np.ndarray = field(init=False, repr=False)

    def __post_init__(self) -> None:
        raw_values = np.asarray(self.values)
        raw_derivatives = np.asarray(self.derivatives)
        if not np.iscomplexobj(raw_values):
            raise TypeError("values must be a complex array.")
        if not np.iscomplexobj(raw_derivatives):
            raise TypeError("derivatives must be a complex array.")

        radial_coordinates = _readonly_copy(
            self.radial_coordinates,
            dtype=np.dtype(np.float64),
        )
        values = _readonly_copy(raw_values, dtype=np.dtype(np.complex128))
        derivatives = _readonly_copy(
            raw_derivatives,
            dtype=np.dtype(np.complex128),
        )
        components = _component_names(
            self.component_names,
            name="component_names",
        )

        if radial_coordinates.ndim != 1:
            raise ValueError("radial_coordinates must be one-dimensional.")
        if not np.all(np.isfinite(radial_coordinates)):
            raise ValueError("radial_coordinates must be finite.")
        if values.ndim != 2 or derivatives.ndim != 2:
            raise ValueError("values and derivatives must be two-dimensional.")
        if values.shape != derivatives.shape:
            raise ValueError("values and derivatives must have the same shape.")
        if values.shape[0] != radial_coordinates.shape[0]:
            raise ValueError(
                "the state batch length must match radial_coordinates."
            )
        if values.shape[1] != len(components):
            raise ValueError(
                "the state component axis must match component_names."
            )

        finite_mask = _readonly_copy(
            np.isfinite(values) & np.isfinite(derivatives),
            dtype=np.dtype(np.bool_),
        )
        object.__setattr__(self, "radial_coordinates", radial_coordinates)
        object.__setattr__(self, "values", values)
        object.__setattr__(self, "derivatives", derivatives)
        object.__setattr__(self, "component_names", components)
        object.__setattr__(self, "finite_mask", finite_mask)

    @property
    def shape(self) -> tuple[int, int]:
        """Point-by-component shape of the stored radial states."""

        return self.values.shape


@runtime_checkable
class BackgroundGeometryProtocol(Protocol):
    """Coordinate and tortoise data supplied by a generic background."""

    name: str
    coordinate_name: str
    physical_claim: bool

    def coordinate_domain(self) -> tuple[float, float]: ...

    def tortoise_coordinate(
        self,
        radial_coordinates: np.ndarray,
    ) -> np.ndarray: ...

    def tortoise_jacobian(
        self,
        radial_coordinates: np.ndarray,
    ) -> np.ndarray: ...


@runtime_checkable
class PotentialProviderProtocol(Protocol):
    """Scalar or matrix-valued effective-potential provider."""

    name: str
    physical_claim: bool

    def potential_matrix(
        self,
        radial_coordinate: float,
        mode: ModeKey,
        channel: ChannelSpec,
        background: BackgroundGeometryProtocol,
    ) -> np.ndarray: ...


@runtime_checkable
class RadialSystemProtocol(Protocol):
    """First-order scalar or coupled radial evolution system."""

    name: str
    component_names: tuple[str, ...]
    physical_claim: bool

    def rhs(
        self,
        radial_coordinate: float,
        state: np.ndarray,
        mode: ModeKey,
        channel: ChannelSpec,
        background: BackgroundGeometryProtocol,
        potential: PotentialProviderProtocol,
    ) -> np.ndarray: ...


@runtime_checkable
class BoundaryAsymptoticsProtocol(Protocol):
    """Inner-boundary state and outer asymptotic basis contract."""

    name: str
    physical_claim: bool

    def inner_state(
        self,
        mode: ModeKey,
        channel: ChannelSpec,
        background: BackgroundGeometryProtocol,
    ) -> np.ndarray: ...

    def outer_basis(
        self,
        radial_coordinate: float,
        mode: ModeKey,
        channel: ChannelSpec,
        background: BackgroundGeometryProtocol,
    ) -> Mapping[str, np.ndarray]: ...


@runtime_checkable
class IncidentSourceProtocol(Protocol):
    """Incident-mode amplitudes with optional ordered sparse support."""

    name: str
    physical_claim: bool

    def supported_m_values(self, ell: int) -> tuple[int, ...] | None: ...

    def amplitude(self, mode: ModeKey, channel: ChannelSpec) -> np.ndarray: ...


@runtime_checkable
class AngularModeCouplingProtocol(Protocol):
    """Angular basis and inter-mode coupling without a fixed support rule."""

    name: str
    physical_claim: bool

    def supported_m_values(self, ell: int) -> tuple[int, ...] | None: ...

    def evaluate(
        self,
        mode: ModeKey,
        observer: ObserverPoint,
        channel: ChannelSpec,
    ) -> np.ndarray: ...

    def coupling(
        self,
        source_mode: ModeKey,
        target_mode: ModeKey,
        channel: ChannelSpec,
    ) -> complex: ...


@runtime_checkable
class DomainDriverProtocol(Protocol):
    """Frequency- or time-domain orchestration boundary."""

    domain_kind: str
    physical_claim: bool

    def run(self, problem: object, backend: SolverBackendProtocol) -> object: ...


@runtime_checkable
class SolverBackendProtocol(Protocol):
    """Numerical backend for scalar or coupled radial systems."""

    name: str
    physical_claim: bool

    def solve(
        self,
        system: RadialSystemProtocol,
        boundary: BoundaryAsymptoticsProtocol,
        mode: ModeKey,
        channel: ChannelSpec,
        background: BackgroundGeometryProtocol,
        potential: PotentialProviderProtocol,
        radial_coordinates: np.ndarray,
    ) -> RadialStateBatch: ...


@runtime_checkable
class ObservableProjectorProtocol(Protocol):
    """Project generic radial states onto observer-space artifacts."""

    name: str
    physical_claim: bool

    def project(
        self,
        radial_states: Mapping[ModeKey, RadialStateBatch],
        observers: Sequence[ObserverPoint],
        angular: AngularModeCouplingProtocol,
    ) -> object: ...


@runtime_checkable
class ArtifactWriterProtocol(Protocol):
    """Persist an artifact together with its complete conventions."""

    format_name: str
    physical_claim: bool

    def write(
        self,
        artifact: object,
        conventions: ConventionMetadata,
    ) -> Path | Mapping[str, object]: ...


__all__ = [
    "AngularModeCouplingProtocol",
    "ArtifactWriterProtocol",
    "BackgroundGeometryProtocol",
    "BoundaryAsymptoticsProtocol",
    "ChannelSpec",
    "ConventionMetadata",
    "DomainDriverProtocol",
    "IncidentSourceProtocol",
    "ModeKey",
    "ObservableProjectorProtocol",
    "ObserverPoint",
    "PotentialProviderProtocol",
    "ProvenanceIdentity",
    "RadialStateBatch",
    "RadialSystemProtocol",
    "SolverBackendProtocol",
]
