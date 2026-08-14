"""Full complex 2x2 polarization-transfer diagnostics for Phase 6."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from types import MappingProxyType
from typing import Mapping

import numpy as np
from numpy.typing import ArrayLike, NDArray


DEFAULT_INCIDENT_BASIS_LABEL = (
    "asymptotic Cartesian linear (+,cross) basis on the (x,y) axes"
)
DEFAULT_OBSERVER_BASIS_LABEL = (
    "observer-tetrad linear (+,cross) basis on the transverse (e1,e2) legs"
)


@dataclass(frozen=True)
class AbsolutePhaseConvention:
    """Frozen references required before absolute transfer phases are compared."""

    units: str = "G=c=M=1"
    fourier: str = "exp(-i omega t)"
    tortoise_coordinate: str = "r*=r+2M log(r/(2M)-1)"
    tortoise_additive_constant: str = "C_r*=0 in the displayed formula"
    retarded_time: str = "u=t-r*"
    coordinate_time_origin: str = "t=0 at the incident phase-reference event"
    incident_phase_baseline: str = (
        "exp[-i omega(t-z)] has zero phase at t=z=0; unit +/cross columns"
    )
    coulomb_subtraction: str = (
        "none beyond the logarithmic phase in frozen r* and Jost "
        "exp(+-i omega r*) factors"
    )
    field_split: str = "total and scattered matrices stored separately"

    def __post_init__(self) -> None:
        for name, value in self.to_mapping().items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"phase convention field {name} must be non-empty")
            lowered = value.casefold()
            if any(
                marker in lowered
                for marker in (
                    "unspecified",
                    "unknown",
                    "placeholder",
                    "per artifact",
                    "to be recorded",
                    "tbd",
                )
            ):
                raise ValueError(f"phase convention field {name} is not frozen")

    def to_mapping(self) -> Mapping[str, str]:
        return MappingProxyType(
            {
                "units": self.units,
                "fourier": self.fourier,
                "tortoise_coordinate": self.tortoise_coordinate,
                "tortoise_additive_constant": self.tortoise_additive_constant,
                "retarded_time": self.retarded_time,
                "coordinate_time_origin": self.coordinate_time_origin,
                "incident_phase_baseline": self.incident_phase_baseline,
                "coulomb_subtraction": self.coulomb_subtraction,
                "field_split": self.field_split,
            }
        )

    def sha256(self) -> str:
        payload = json.dumps(
            dict(self.to_mapping()),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class PolarizationTransferMatrix:
    """A linear-polarization transfer matrix with a frozen field definition."""

    matrix: NDArray[np.complex128]
    field_definition: str
    phase_convention: AbsolutePhaseConvention
    incident_basis_label: str = DEFAULT_INCIDENT_BASIS_LABEL
    observer_basis_label: str = DEFAULT_OBSERVER_BASIS_LABEL
    incident_basis_angle_rad: float = 0.0
    observer_basis_angle_rad: float = 0.0

    def __post_init__(self) -> None:
        matrix = np.asarray(self.matrix, dtype=np.complex128)
        if matrix.shape != (2, 2) or not _finite_complex_array(matrix):
            raise ValueError("matrix must be a finite complex 2x2 array")
        if self.field_definition not in ("total", "scattered"):
            raise ValueError("field_definition must be total or scattered")
        if not isinstance(self.phase_convention, AbsolutePhaseConvention):
            raise TypeError("phase_convention must be AbsolutePhaseConvention")
        for name in ("incident_basis_label", "observer_basis_label"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        for name in ("incident_basis_angle_rad", "observer_basis_angle_rad"):
            value = float(getattr(self, name))
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            object.__setattr__(self, name, value)
        matrix = np.array(matrix, copy=True)
        matrix.setflags(write=False)
        object.__setattr__(self, "matrix", matrix)

    @property
    def singular_values(self) -> NDArray[np.float64]:
        values = np.asarray(
            np.linalg.svd(self.matrix, compute_uv=False), dtype=np.float64
        )
        values.setflags(write=False)
        return values

    @property
    def trace_fdagger_f(self) -> float:
        return float(np.trace(self.matrix.conj().T @ self.matrix).real)

    @property
    def determinant(self) -> complex:
        # The closed 2x2 formula is exact for this fixed matrix shape and avoids
        # a spurious complex-LAPACK warning in NumPy 2.4 on CPython 3.14.
        return complex(
            self.matrix[0, 0] * self.matrix[1, 1]
            - self.matrix[0, 1] * self.matrix[1, 0]
        )

    @property
    def helicity_matrix(self) -> NDArray[np.complex128]:
        transform = linear_to_helicity_transform()
        result = transform @ self.matrix @ transform.conj().T
        result.setflags(write=False)
        return result

    @property
    def helicity_mixing_power(self) -> float:
        matrix = self.helicity_matrix
        return float(abs(matrix[0, 1]) ** 2 + abs(matrix[1, 0]) ** 2)


def polarization_transfer_from_columns(
    plus_incident_output: ArrayLike,
    cross_incident_output: ArrayLike,
    *,
    field_definition: str,
    phase_convention: AbsolutePhaseConvention,
    incident_basis_label: str = DEFAULT_INCIDENT_BASIS_LABEL,
    observer_basis_label: str = DEFAULT_OBSERVER_BASIS_LABEL,
) -> PolarizationTransferMatrix:
    """Build ``F`` from responses to unit ``+`` and unit ``cross`` inputs."""

    plus_column = np.asarray(plus_incident_output, dtype=np.complex128)
    cross_column = np.asarray(cross_incident_output, dtype=np.complex128)
    if plus_column.shape != (2,) or cross_column.shape != (2,):
        raise ValueError("each response column must have shape (2,)")
    matrix = np.column_stack((plus_column, cross_column))
    return PolarizationTransferMatrix(
        matrix=matrix,
        field_definition=field_definition,
        phase_convention=phase_convention,
        incident_basis_label=incident_basis_label,
        observer_basis_label=observer_basis_label,
    )


def polarization_basis_rotation(angle: float) -> NDArray[np.float64]:
    """Return the frozen spin-2 linear-basis rotation matrix.

    For a counter-clockwise rotation of the transverse axes by ``angle``,
    ``(h_plus',h_cross') = R(angle) (h_plus,h_cross)`` with
    ``R=[[cos(2a),sin(2a)],[-sin(2a),cos(2a)]]``.
    """

    angle_value = float(angle)
    if not math.isfinite(angle_value):
        raise ValueError("angle must be finite")
    cosine = math.cos(2.0 * angle_value)
    sine = math.sin(2.0 * angle_value)
    result = np.array([[cosine, sine], [-sine, cosine]], dtype=np.float64)
    result.setflags(write=False)
    return result


def rotate_polarization_transfer(
    transfer: PolarizationTransferMatrix,
    *,
    incident_basis_angle: float,
    observer_basis_angle: float,
) -> PolarizationTransferMatrix:
    """Transform a transfer matrix under independent input/output basis rotations."""

    if not isinstance(transfer, PolarizationTransferMatrix):
        raise TypeError("transfer must be a PolarizationTransferMatrix")
    incident = polarization_basis_rotation(incident_basis_angle)
    observer = polarization_basis_rotation(observer_basis_angle)
    transformed = observer @ transfer.matrix @ incident.T
    return PolarizationTransferMatrix(
        matrix=transformed,
        field_definition=transfer.field_definition,
        phase_convention=transfer.phase_convention,
        incident_basis_label=transfer.incident_basis_label,
        observer_basis_label=transfer.observer_basis_label,
        incident_basis_angle_rad=(
            transfer.incident_basis_angle_rad + float(incident_basis_angle)
        ),
        observer_basis_angle_rad=(
            transfer.observer_basis_angle_rad + float(observer_basis_angle)
        ),
    )


def linear_to_helicity_transform() -> NDArray[np.complex128]:
    """Return ``(h_R,h_L)=(h_+-i h_x,h_++i h_x)/sqrt(2)``."""

    result = np.array(
        [[1.0, -1.0j], [1.0, 1.0j]],
        dtype=np.complex128,
    ) / math.sqrt(2.0)
    result.setflags(write=False)
    return result


def _finite_complex_array(values: NDArray[np.complex128]) -> bool:
    return bool(np.all(np.isfinite(values.real)) and np.all(np.isfinite(values.imag)))


__all__ = [
    "AbsolutePhaseConvention",
    "DEFAULT_INCIDENT_BASIS_LABEL",
    "DEFAULT_OBSERVER_BASIS_LABEL",
    "PolarizationTransferMatrix",
    "linear_to_helicity_transform",
    "polarization_basis_rotation",
    "polarization_transfer_from_columns",
    "rotate_polarization_transfer",
]
