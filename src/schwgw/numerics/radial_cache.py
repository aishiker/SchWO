"""Identity-scoped radial samples with certified dense and exact-oracle reuse.

This module is intentionally not re-exported from :mod:`schwgw.numerics`.
The cache accepts an injected solver and never selects or invokes a scientific
backend on its own.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, fields, is_dataclass
import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping

import numpy as np

from schwgw.scattering.contracts import ProvenanceIdentity


_PROVENANCE_COMPONENTS = (
    "implementation_sha256",
    "physics_sha256",
    "solver_sha256",
    "config_sha256",
    "source_sha256",
    "gate_sha256",
)
_ORACLE_ADMISSION_COMPONENTS = (
    "artifact_sha256",
    "schema_version",
    "snapshot_sha256",
)
_RESIDUAL_FIELDS = (
    "boundary_residual",
    "wronskian_residual",
    "flux_residual",
    "raw_wronskian_residual",
    "match_condition_number",
)
_REQUIRED_DIAGNOSTIC_FIELDS = (
    "solver",
    "rtol",
    "atol",
    "warnings",
    *_RESIDUAL_FIELDS,
)
_SAMPLE_VALUE_FIELDS = (
    "psi",
    "dpsi_dr",
    "A_in",
    "A_out",
    "phase_factor",
    "phase_shift",
)


class RadialCacheContractError(RuntimeError):
    """Structured fail-closed radial-cache contract violation."""

    def __init__(self, code: str, metadata: Mapping[str, object]) -> None:
        self.code = str(code)
        self.metadata = dict(metadata)
        component = self.metadata.get("component")
        suffix = "" if component is None else f" ({component})"
        super().__init__(f"{self.code}{suffix}")


@dataclass(frozen=True)
class ImmutableRecord:
    """Deeply immutable attribute view used for cached diagnostics."""

    type_name: str
    items: tuple[tuple[str, object], ...]

    def __post_init__(self) -> None:
        if not isinstance(self.type_name, str) or not self.type_name:
            raise TypeError("immutable record type_name must be non-empty")
        if not isinstance(self.items, tuple):
            raise TypeError("immutable record items must be a tuple")
        names: list[str] = []
        for item in self.items:
            if (
                not isinstance(item, tuple)
                or len(item) != 2
                or not isinstance(item[0], str)
                or not item[0]
            ):
                raise TypeError(
                    "immutable record items must be (non-empty string, value) pairs"
                )
            names.append(item[0])
        if len(names) != len(set(names)):
            raise ValueError("immutable record item names must be unique")

    def __getattr__(self, name: str) -> object:
        for key, value in self.items:
            if key == name:
                return value
        raise AttributeError(name)


@dataclass(frozen=True, slots=True)
class RadialModeKey:
    """Radius-independent scientific mode key."""

    sector: str
    ell: int
    k: float

    def __post_init__(self) -> None:
        if not isinstance(self.sector, str) or not self.sector:
            raise TypeError("sector must be a non-empty string")
        if isinstance(self.ell, bool) or not isinstance(self.ell, int):
            raise TypeError("ell must be an integer")
        if self.ell < 0:
            raise ValueError("ell must be non-negative")
        if not _finite_real(self.k):
            raise ValueError("k must be finite")


@dataclass(frozen=True, slots=True)
class RadialCacheRequest:
    """One point evaluation under a complete current consumer identity."""

    mode: RadialModeKey
    point_id: str
    radius: float
    rtol: float
    atol: float
    consumer_identity: ProvenanceIdentity

    def __post_init__(self) -> None:
        if not isinstance(self.mode, RadialModeKey):
            raise TypeError("mode must be a RadialModeKey")
        if not isinstance(self.point_id, str) or not self.point_id:
            raise TypeError("point_id must be a non-empty string")
        _require_positive_finite("radius", self.radius)
        _require_positive_finite("rtol", self.rtol)
        _require_positive_finite("atol", self.atol)
        if not isinstance(self.consumer_identity, ProvenanceIdentity):
            raise TypeError("consumer_identity must be a ProvenanceIdentity")


@dataclass(frozen=True, slots=True)
class OracleAdmissionIdentity:
    """Expected content, schema, snapshot, and historical oracle origin."""

    artifact_sha256: str
    schema_version: str
    snapshot_sha256: str
    origin_identity: ProvenanceIdentity

    def __post_init__(self) -> None:
        _require_sha256("artifact_sha256", self.artifact_sha256)
        if not isinstance(self.schema_version, str) or not self.schema_version:
            raise TypeError("schema_version must be a non-empty string")
        _require_sha256("snapshot_sha256", self.snapshot_sha256)
        if not isinstance(self.origin_identity, ProvenanceIdentity):
            raise TypeError("origin_identity must be a ProvenanceIdentity")


@dataclass(frozen=True, slots=True)
class OracleRadialRecord:
    """One radius- and point-specific immutable oracle record."""

    mode: RadialModeKey
    point_id: str
    radius: float
    rtol: float
    atol: float
    psi: complex
    dpsi_dr: complex
    A_in: complex
    A_out: complex
    phase_factor: complex
    phase_shift: complex
    diagnostics: Any

    def __post_init__(self) -> None:
        if not isinstance(self.mode, RadialModeKey):
            raise TypeError("mode must be a RadialModeKey")
        if not isinstance(self.point_id, str) or not self.point_id:
            raise TypeError("point_id must be a non-empty string")
        _require_positive_finite("radius", self.radius)
        _require_positive_finite("rtol", self.rtol)
        _require_positive_finite("atol", self.atol)
        object.__setattr__(
            self,
            "diagnostics",
            _immutable_copy(self.diagnostics),
        )


@dataclass(frozen=True, slots=True)
class OracleRadialArtifact:
    """In-memory read-only view of an independently authenticated artifact."""

    admission: OracleAdmissionIdentity
    records: tuple[OracleRadialRecord, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.admission, OracleAdmissionIdentity):
            raise TypeError("admission must be an OracleAdmissionIdentity")
        if not isinstance(self.records, tuple):
            raise TypeError("records must be a tuple")
        if not all(isinstance(record, OracleRadialRecord) for record in self.records):
            raise TypeError("records must contain only OracleRadialRecord values")


@dataclass(frozen=True, slots=True)
class RadialSample:
    """Immutable scalar sample returned to one current consumer."""

    mode: RadialModeKey
    point_id: str
    radius: float
    rtol: float
    atol: float
    psi: complex
    dpsi_dr: complex
    A_in: complex
    A_out: complex
    phase_factor: complex
    phase_shift: complex
    diagnostics: Any
    source: str
    consumer_identity: ProvenanceIdentity
    oracle_admission: OracleAdmissionIdentity | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "diagnostics",
            _immutable_copy(self.diagnostics),
        )


@dataclass(frozen=True, slots=True)
class RadialCacheStats:
    """Immutable counter snapshot with independent solve/cache categories."""

    fresh_ode_solve_count: int
    fresh_oracle_solve_count: int
    ordinary_hit_count: int
    ordinary_miss_count: int
    ordinary_rejection_count: int
    oracle_hit_count: int
    oracle_miss_count: int
    oracle_rejection_count: int
    request_rejection_count: int


@dataclass(frozen=True, slots=True)
class _OrdinaryKey:
    mode: RadialModeKey
    rtol: float
    atol: float
    consumer_identity: ProvenanceIdentity


@dataclass(frozen=True, slots=True)
class _OracleKey:
    mode: RadialModeKey
    point_id: str
    radius: float
    rtol: float
    atol: float
    consumer_identity: ProvenanceIdentity


@dataclass(frozen=True, slots=True)
class _DenseEntry:
    solution: Any
    lower: float
    upper: float

    def covers(self, radius: float) -> bool:
        return self.lower <= radius <= self.upper


@dataclass(frozen=True, slots=True)
class _OracleEntry:
    record: OracleRadialRecord
    admission: OracleAdmissionIdentity | None


class RadialCache:
    """Identity-scoped cache for injected ordinary or oracle radial solves."""

    def __init__(
        self,
        *,
        current_identity: ProvenanceIdentity,
        solver: Callable[[RadialCacheRequest], Any],
        expected_oracle_admission: OracleAdmissionIdentity | None = None,
    ) -> None:
        if not isinstance(current_identity, ProvenanceIdentity):
            raise TypeError("current_identity must be a ProvenanceIdentity")
        if not callable(solver):
            raise TypeError("solver must be callable")
        if (
            expected_oracle_admission is not None
            and not isinstance(
                expected_oracle_admission,
                OracleAdmissionIdentity,
            )
        ):
            raise TypeError(
                "expected_oracle_admission must be an "
                "OracleAdmissionIdentity or None"
            )
        self._current_identity = current_identity
        self._solver = solver
        self._expected_oracle_admission = expected_oracle_admission
        self._ordinary: dict[_OrdinaryKey, list[_DenseEntry]] = {}
        self._oracle: dict[_OracleKey, _OracleEntry] = {}
        self._fresh_ode_solve_count = 0
        self._fresh_oracle_solve_count = 0
        self._ordinary_hit_count = 0
        self._ordinary_miss_count = 0
        self._ordinary_rejection_count = 0
        self._oracle_hit_count = 0
        self._oracle_miss_count = 0
        self._oracle_rejection_count = 0
        self._request_rejection_count = 0

    @property
    def current_identity(self) -> ProvenanceIdentity:
        return self._current_identity

    @property
    def stats(self) -> RadialCacheStats:
        return RadialCacheStats(
            fresh_ode_solve_count=self._fresh_ode_solve_count,
            fresh_oracle_solve_count=self._fresh_oracle_solve_count,
            ordinary_hit_count=self._ordinary_hit_count,
            ordinary_miss_count=self._ordinary_miss_count,
            ordinary_rejection_count=self._ordinary_rejection_count,
            oracle_hit_count=self._oracle_hit_count,
            oracle_miss_count=self._oracle_miss_count,
            oracle_rejection_count=self._oracle_rejection_count,
            request_rejection_count=self._request_rejection_count,
        )

    def admit_oracle(self, artifact: OracleRadialArtifact) -> None:
        """Atomically admit a fully matching finite read-only oracle artifact."""

        if not isinstance(artifact, OracleRadialArtifact):
            self._reject_oracle(
                "radial_cache_oracle_admission_mismatch",
                {
                    "component": "artifact",
                    "expected": "OracleRadialArtifact",
                    "actual": type(artifact).__qualname__,
                },
            )
        expected = self._expected_oracle_admission
        if expected is None:
            self._reject_oracle(
                "radial_cache_oracle_admission_mismatch",
                {
                    "component": "expected_oracle_admission",
                    "expected": "explicit admission identity",
                    "actual": None,
                },
            )
        self._validate_admission(expected, artifact.admission)
        admitted: dict[_OracleKey, _OracleEntry] = {}
        for index, record in enumerate(artifact.records):
            self._validate_oracle_record(record, record_index=index)
            record = _immutable_record_copy(record)
            key = self._oracle_key_from_record(record)
            if key in admitted or key in self._oracle:
                self._reject_oracle(
                    "radial_cache_oracle_record_collision",
                    {
                        "component": "record_key",
                        "record_index": index,
                        "point_id": record.point_id,
                        "radius": record.radius,
                    },
                )
            admitted[key] = _OracleEntry(
                record=record,
                admission=artifact.admission,
            )
        actual_content_sha256 = oracle_artifact_sha256(
            artifact.admission,
            tuple(entry.record for entry in admitted.values()),
        )
        if actual_content_sha256 != artifact.admission.artifact_sha256:
            self._reject_oracle(
                "radial_cache_oracle_admission_mismatch",
                {
                    "component": "artifact_content_sha256",
                    "expected": artifact.admission.artifact_sha256,
                    "actual": actual_content_sha256,
                },
            )
        self._oracle.update(admitted)

    def evaluate_many(
        self,
        requests: Iterable[RadialCacheRequest],
    ) -> tuple[RadialSample, ...]:
        """Evaluate requests with exact-oracle priority and stable output order."""

        ordered = tuple(requests)
        for request in ordered:
            if not isinstance(request, RadialCacheRequest):
                self._request_rejection_count += 1
                raise RadialCacheContractError(
                    "radial_cache_invalid_request",
                    {
                        "component": "request",
                        "expected": "RadialCacheRequest",
                        "actual": type(request).__qualname__,
                    },
                )
            self._validate_current_identity(request.consumer_identity)

        results: list[RadialSample | None] = [None] * len(ordered)
        unresolved: list[tuple[int, RadialCacheRequest]] = []
        for index, request in enumerate(ordered):
            oracle = self._lookup_oracle(request)
            if oracle is None:
                unresolved.append((index, request))
            else:
                results[index] = oracle

        for index, request in sorted(
            unresolved,
            key=lambda item: (-item[1].radius, item[0]),
        ):
            results[index] = self._evaluate_uncached_request(request)

        if any(result is None for result in results):
            raise AssertionError("radial cache left an unresolved request")
        return tuple(result for result in results if result is not None)

    def _validate_current_identity(
        self,
        actual: ProvenanceIdentity,
    ) -> None:
        for component in _PROVENANCE_COMPONENTS:
            expected_value = getattr(self._current_identity, component)
            actual_value = getattr(actual, component)
            if actual_value != expected_value:
                self._request_rejection_count += 1
                raise RadialCacheContractError(
                    "radial_cache_identity_mismatch",
                    {
                        "component": component,
                        "expected": expected_value,
                        "actual": actual_value,
                    },
                )

    def _validate_admission(
        self,
        expected: OracleAdmissionIdentity,
        actual: OracleAdmissionIdentity,
    ) -> None:
        for component in _ORACLE_ADMISSION_COMPONENTS:
            expected_value = getattr(expected, component)
            actual_value = getattr(actual, component)
            if actual_value != expected_value:
                self._reject_oracle(
                    "radial_cache_oracle_admission_mismatch",
                    {
                        "component": component,
                        "expected": expected_value,
                        "actual": actual_value,
                    },
                )
        for component in _PROVENANCE_COMPONENTS:
            expected_value = getattr(expected.origin_identity, component)
            actual_value = getattr(actual.origin_identity, component)
            if actual_value != expected_value:
                self._reject_oracle(
                    "radial_cache_oracle_admission_mismatch",
                    {
                        "component": f"origin_identity.{component}",
                        "expected": expected_value,
                        "actual": actual_value,
                    },
                )

    def _lookup_oracle(
        self,
        request: RadialCacheRequest,
    ) -> RadialSample | None:
        if not self._oracle_enabled:
            return None
        entry = self._oracle.get(self._oracle_key(request))
        if entry is not None:
            self._oracle_hit_count += 1
            return self._sample_from_record(
                request,
                entry.record,
                admission=entry.admission,
            )
        if self._has_oracle_mode_candidate(request):
            self._oracle_rejection_count += 1
        else:
            self._oracle_miss_count += 1
        return None

    def _has_oracle_mode_candidate(
        self,
        request: RadialCacheRequest,
    ) -> bool:
        return any(
            key.mode == request.mode
            and key.consumer_identity == request.consumer_identity
            for key in self._oracle
        )

    def _evaluate_uncached_request(
        self,
        request: RadialCacheRequest,
    ) -> RadialSample:
        ordinary_key = self._ordinary_key(request)
        for entry in self._ordinary.get(ordinary_key, ()):
            if entry.covers(request.radius):
                self._ordinary_hit_count += 1
                return self._sample_from_solution(
                    request,
                    entry.solution,
                    source="ordinary_dense",
                    oracle_admission=None,
                )

        self._ordinary_miss_count += 1
        self._fresh_ode_solve_count += 1
        solution = _snapshot_solution(self._solver(request))
        if _is_oracle_solution(solution):
            self._fresh_ode_solve_count -= 1
            self._fresh_oracle_solve_count += 1
            self._oracle_rejection_count += 1
            raise RadialCacheContractError(
                "radial_cache_unadmitted_oracle_solution",
                {
                    "component": "solver.diagnostics.solver",
                    "actual": str(solution.diagnostics.solver),
                },
            )
        source = "fresh_ode"
        try:
            _validate_solution_identity(request, solution)
            lower, upper = _certified_interval(solution)
            if not lower <= request.radius <= upper:
                raise RadialCacheContractError(
                    "radial_cache_uncertified_radius",
                    {
                        "component": "radius",
                        "requested_radius": request.radius,
                        "certified_lower": lower,
                        "certified_upper": upper,
                        "source": source,
                    },
                )
            sample = self._sample_from_solution(
                request,
                solution,
                source="ordinary_dense",
                oracle_admission=None,
                validation_source=source,
            )
        except RadialCacheContractError:
            self._ordinary_rejection_count += 1
            raise

        self._ordinary.setdefault(ordinary_key, []).append(
            _DenseEntry(
                solution=solution,
                lower=lower,
                upper=upper,
            )
        )
        return sample

    def _sample_from_solution(
        self,
        request: RadialCacheRequest,
        solution: Any,
        *,
        source: str,
        oracle_admission: OracleAdmissionIdentity | None,
        validation_source: str | None = None,
    ) -> RadialSample:
        try:
            values = {
                "psi": complex(solution.psi_at(request.radius)),
                "dpsi_dr": complex(solution.dpsi_dr_at(request.radius)),
                "A_in": complex(solution.A_in),
                "A_out": complex(solution.A_out),
                "phase_factor": complex(solution.phase_factor),
                "phase_shift": complex(solution.phase_shift),
            }
            diagnostics = solution.diagnostics
        except (AttributeError, TypeError, ValueError) as exc:
            raise RadialCacheContractError(
                "radial_cache_invalid_payload",
                {
                    "component": "solution",
                    "source": validation_source or source,
                    "error": str(exc),
                },
            ) from exc
        _validate_finite_payload(
            values=values,
            diagnostics=diagnostics,
            source=validation_source or source,
        )
        return RadialSample(
            mode=request.mode,
            point_id=request.point_id,
            radius=request.radius,
            rtol=request.rtol,
            atol=request.atol,
            psi=values["psi"],
            dpsi_dr=values["dpsi_dr"],
            A_in=values["A_in"],
            A_out=values["A_out"],
            phase_factor=values["phase_factor"],
            phase_shift=values["phase_shift"],
            diagnostics=diagnostics,
            source=source,
            consumer_identity=request.consumer_identity,
            oracle_admission=oracle_admission,
        )

    def _sample_from_record(
        self,
        request: RadialCacheRequest,
        record: OracleRadialRecord,
        *,
        admission: OracleAdmissionIdentity | None,
    ) -> RadialSample:
        return RadialSample(
            mode=request.mode,
            point_id=request.point_id,
            radius=request.radius,
            rtol=request.rtol,
            atol=request.atol,
            psi=complex(record.psi),
            dpsi_dr=complex(record.dpsi_dr),
            A_in=complex(record.A_in),
            A_out=complex(record.A_out),
            phase_factor=complex(record.phase_factor),
            phase_shift=complex(record.phase_shift),
            diagnostics=record.diagnostics,
            source="oracle_exact",
            consumer_identity=request.consumer_identity,
            oracle_admission=admission,
        )

    def _validate_oracle_record(
        self,
        record: OracleRadialRecord,
        *,
        record_index: int,
    ) -> None:
        values = {
            name: getattr(record, name)
            for name in _SAMPLE_VALUE_FIELDS
        }
        try:
            _validate_finite_payload(
                values=values,
                diagnostics=record.diagnostics,
                source="oracle",
                record_index=record_index,
            )
        except RadialCacheContractError as exc:
            self._oracle_rejection_count += 1
            raise exc
        for component in ("rtol", "atol"):
            expected = float(getattr(record, component))
            actual = float(
                _diagnostic_value(record.diagnostics, component)
            )
            if actual != expected:
                self._reject_oracle(
                    "radial_cache_oracle_record_identity_mismatch",
                    {
                        "component": f"diagnostics.{component}",
                        "expected": expected,
                        "actual": actual,
                        "record_index": record_index,
                    },
                )

    def _ordinary_key(self, request: RadialCacheRequest) -> _OrdinaryKey:
        return _OrdinaryKey(
            mode=request.mode,
            rtol=request.rtol,
            atol=request.atol,
            consumer_identity=request.consumer_identity,
        )

    def _oracle_key(self, request: RadialCacheRequest) -> _OracleKey:
        return _OracleKey(
            mode=request.mode,
            point_id=request.point_id,
            radius=request.radius,
            rtol=request.rtol,
            atol=request.atol,
            consumer_identity=request.consumer_identity,
        )

    def _oracle_key_from_record(
        self,
        record: OracleRadialRecord,
    ) -> _OracleKey:
        return _OracleKey(
            mode=record.mode,
            point_id=record.point_id,
            radius=record.radius,
            rtol=record.rtol,
            atol=record.atol,
            consumer_identity=self._current_identity,
        )

    @property
    def _oracle_enabled(self) -> bool:
        return (
            self._expected_oracle_admission is not None
            or bool(self._oracle)
        )

    def _reject_oracle(
        self,
        code: str,
        metadata: Mapping[str, object],
    ) -> None:
        self._oracle_rejection_count += 1
        raise RadialCacheContractError(code, metadata)


def _immutable_record_copy(record: OracleRadialRecord) -> OracleRadialRecord:
    return OracleRadialRecord(
        mode=record.mode,
        point_id=record.point_id,
        radius=record.radius,
        rtol=record.rtol,
        atol=record.atol,
        psi=complex(record.psi),
        dpsi_dr=complex(record.dpsi_dr),
        A_in=complex(record.A_in),
        A_out=complex(record.A_out),
        phase_factor=complex(record.phase_factor),
        phase_shift=complex(record.phase_shift),
        diagnostics=record.diagnostics,
    )


def oracle_artifact_sha256(
    admission: OracleAdmissionIdentity,
    records: Iterable[OracleRadialRecord],
) -> str:
    """Hash the exact canonical oracle content, excluding its own digest."""

    if not isinstance(admission, OracleAdmissionIdentity):
        raise TypeError("admission must be an OracleAdmissionIdentity")
    ordered = tuple(records)
    if not all(isinstance(record, OracleRadialRecord) for record in ordered):
        raise TypeError("records must contain only OracleRadialRecord values")
    payload = {
        "schema_version": admission.schema_version,
        "snapshot_sha256": admission.snapshot_sha256,
        "origin_identity": {
            component: getattr(admission.origin_identity, component)
            for component in _PROVENANCE_COMPONENTS
        },
        "records": [
            {
                "mode": {
                    "sector": record.mode.sector,
                    "ell": record.mode.ell,
                    "k": record.mode.k,
                },
                "point_id": record.point_id,
                "radius": record.radius,
                "rtol": record.rtol,
                "atol": record.atol,
                **{
                    name: getattr(record, name)
                    for name in _SAMPLE_VALUE_FIELDS
                },
                "diagnostics": record.diagnostics,
            }
            for record in ordered
        ],
    }
    canonical = json.dumps(
        _canonical_value(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _snapshot_solution(solution: Any) -> Any:
    try:
        return copy.deepcopy(solution)
    except Exception as exc:
        raise RadialCacheContractError(
            "radial_cache_invalid_payload",
            {
                "component": "solution_snapshot",
                "source": "solver",
                "error": str(exc),
            },
        ) from exc


def _immutable_copy(value: object) -> object:
    if isinstance(value, ImmutableRecord):
        return ImmutableRecord(
            type_name=value.type_name,
            items=tuple(
                (key, _immutable_copy(item))
                for key, item in value.items
            ),
        )
    if is_dataclass(value) and not isinstance(value, type):
        return ImmutableRecord(
            type_name=f"{type(value).__module__}.{type(value).__qualname__}",
            items=tuple(
                (field.name, _immutable_copy(getattr(value, field.name)))
                for field in fields(value)
            ),
        )
    if isinstance(value, Mapping):
        return MappingProxyType(
            {
                _immutable_mapping_key(key): _immutable_copy(item)
                for key, item in value.items()
            }
        )
    if isinstance(value, (tuple, list)):
        return tuple(_immutable_copy(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_immutable_copy(item) for item in value)
    if isinstance(value, np.ndarray):
        copied = np.array(value, copy=True, order="C")
        immutable = np.frombuffer(copied.tobytes(order="C"), dtype=copied.dtype)
        return immutable.reshape(copied.shape)
    if isinstance(value, np.generic):
        return _immutable_copy(value.item())
    if value is None or isinstance(
        value,
        (str, bytes, bool, int, float, complex, Path),
    ):
        return value
    raise TypeError(
        "cached diagnostics must contain only dataclasses, mappings, "
        "sequences, arrays, paths, or immutable scalar values"
    )


def _immutable_mapping_key(value: object) -> object:
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, (str, bytes, bool, int, float, complex, Path)):
        return value
    raise TypeError("cached diagnostic mapping keys must be immutable scalars")


def _canonical_value(value: object) -> object:
    if isinstance(value, ImmutableRecord):
        return {
            "__record_type__": value.type_name,
            "items": {
                key: _canonical_value(item)
                for key, item in value.items
            },
        }
    if is_dataclass(value) and not isinstance(value, type):
        return _canonical_value(_immutable_copy(value))
    if isinstance(value, Mapping):
        encoded_items = [
            {
                "key": _canonical_value(key),
                "value": _canonical_value(item),
            }
            for key, item in value.items()
        ]
        return {
            "__mapping_items__": sorted(
                encoded_items,
                key=lambda item: json.dumps(
                    item["key"],
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            )
        }
    if isinstance(value, (tuple, list)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, (set, frozenset)):
        canonical_items = [_canonical_value(item) for item in value]
        return sorted(
            canonical_items,
            key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")),
        )
    if isinstance(value, np.ndarray):
        array = np.ascontiguousarray(value)
        return {
            "__ndarray__": {
                "dtype": array.dtype.str,
                "shape": list(array.shape),
                "sha256": hashlib.sha256(array.tobytes(order="C")).hexdigest(),
            }
        }
    if isinstance(value, np.generic):
        return _canonical_value(value.item())
    if isinstance(value, float):
        if not np.isfinite(value):
            raise ValueError("canonical oracle content must be finite")
        return {"__float_hex__": value.hex()}
    if isinstance(value, complex):
        if not _finite_complex(value):
            raise ValueError("canonical oracle content must be finite")
        return {
            "__complex_hex__": [
                float(value.real).hex(),
                float(value.imag).hex(),
            ]
        }
    if isinstance(value, Path):
        return {"__path__": str(value)}
    if value is None or isinstance(value, (str, bytes, bool, int)):
        if isinstance(value, bytes):
            return {"__bytes_hex__": value.hex()}
        return value
    raise TypeError(f"unsupported canonical oracle value: {type(value).__qualname__}")


def _certified_interval(solution: Any) -> tuple[float, float]:
    try:
        grid = np.asarray(solution.r_grid, dtype=float)
    except (AttributeError, TypeError, ValueError) as exc:
        raise RadialCacheContractError(
            "radial_cache_invalid_payload",
            {
                "component": "r_grid",
                "source": "solver",
                "error": str(exc),
            },
        ) from exc
    if (
        grid.ndim != 1
        or grid.size < 2
        or not np.all(np.isfinite(grid))
        or np.any(np.diff(grid) <= 0.0)
    ):
        raise RadialCacheContractError(
            "radial_cache_invalid_payload",
            {
                "component": "r_grid",
                "source": "solver",
            },
        )
    lower = float(grid[0])
    valid_until = getattr(solution, "valid_until_r", None)
    upper = float(grid[-1] if valid_until is None else valid_until)
    if not np.isfinite(upper) or upper < lower or upper > float(grid[-1]):
        raise RadialCacheContractError(
            "radial_cache_invalid_payload",
            {
                "component": "valid_until_r",
                "source": "solver",
            },
        )
    return lower, upper


_MISSING = object()


def _diagnostic_value(diagnostics: Any, name: str) -> object:
    if isinstance(diagnostics, Mapping):
        return diagnostics.get(name, _MISSING)
    return getattr(diagnostics, name, _MISSING)


def _validate_solution_identity(
    request: RadialCacheRequest,
    solution: Any,
) -> None:
    actual_sector = getattr(solution, "sector", _MISSING)
    if actual_sector is not _MISSING:
        actual_sector = getattr(actual_sector, "value", actual_sector)
    actual_ell = getattr(solution, "ell", _MISSING)
    actual_k = getattr(solution, "k", _MISSING)
    expected = {
        "sector": request.mode.sector,
        "ell": request.mode.ell,
        "k": request.mode.k,
        "rtol": request.rtol,
        "atol": request.atol,
    }
    diagnostics = getattr(solution, "diagnostics", _MISSING)
    actual = {
        "sector": actual_sector,
        "ell": actual_ell,
        "k": actual_k,
        "rtol": (
            _MISSING
            if diagnostics is _MISSING
            else _diagnostic_value(diagnostics, "rtol")
        ),
        "atol": (
            _MISSING
            if diagnostics is _MISSING
            else _diagnostic_value(diagnostics, "atol")
        ),
    }
    for name, expected_value in expected.items():
        actual_value = actual[name]
        if actual_value is _MISSING or actual_value != expected_value:
            raise RadialCacheContractError(
                "radial_cache_solution_identity_mismatch",
                {
                    "component": name,
                    "expected": expected_value,
                    "actual": (
                        None if actual_value is _MISSING else actual_value
                    ),
                },
            )


def _validate_finite_payload(
    *,
    values: Mapping[str, object],
    diagnostics: Any,
    source: str,
    record_index: int | None = None,
) -> None:
    for name in _SAMPLE_VALUE_FIELDS:
        if not _finite_complex(values[name]):
            metadata: dict[str, object] = {
                "source": source,
                "field": name,
            }
            if record_index is not None:
                metadata["record_index"] = record_index
            raise RadialCacheContractError(
                "radial_cache_nonfinite_payload",
                metadata,
            )
    for name in _REQUIRED_DIAGNOSTIC_FIELDS:
        value = _diagnostic_value(diagnostics, name)
        if value is _MISSING:
            metadata = {
                "source": source,
                "field": f"diagnostics.{name}",
            }
            if record_index is not None:
                metadata["record_index"] = record_index
            raise RadialCacheContractError(
                "radial_cache_missing_diagnostic",
                metadata,
            )
        if name == "solver":
            if not isinstance(value, str) or not value:
                raise RadialCacheContractError(
                    "radial_cache_invalid_payload",
                    {
                        "source": source,
                        "field": "diagnostics.solver",
                    },
                )
            continue
        if name == "warnings":
            if not isinstance(value, tuple):
                raise RadialCacheContractError(
                    "radial_cache_invalid_payload",
                    {
                        "source": source,
                        "field": "diagnostics.warnings",
                    },
                )
            continue
        if name in {"rtol", "atol"}:
            if not _finite_real(value) or float(value) <= 0.0:
                raise RadialCacheContractError(
                    "radial_cache_invalid_payload",
                    {
                        "source": source,
                        "field": f"diagnostics.{name}",
                    },
                )
            continue
        if not _finite_real(value):
            metadata = {
                "source": source,
                "field": f"diagnostics.{name}",
            }
            if record_index is not None:
                metadata["record_index"] = record_index
            raise RadialCacheContractError(
                "radial_cache_nonfinite_payload",
                metadata,
            )


def _is_oracle_solution(solution: Any) -> bool:
    diagnostics = getattr(solution, "diagnostics", None)
    solver = str(_diagnostic_value(diagnostics, "solver"))
    if "oracle" in solver.lower():
        return True
    warnings_value = _diagnostic_value(diagnostics, "warnings")
    if warnings_value is _MISSING or warnings_value is None:
        return False
    for warning in warnings_value:
        code = (
            warning.get("code", "")
            if isinstance(warning, Mapping)
            else getattr(warning, "code", "")
        )
        if "oracle" in str(code).lower():
            return True
    return False


def _finite_complex(value: object) -> bool:
    try:
        number = complex(value)
    except (TypeError, ValueError):
        return False
    return bool(np.isfinite(number.real) and np.isfinite(number.imag))


def _finite_real(value: object) -> bool:
    if isinstance(value, bool):
        return False
    try:
        return bool(np.isfinite(float(value)))
    except (TypeError, ValueError):
        return False


def _require_positive_finite(name: str, value: object) -> None:
    if not _finite_real(value) or float(value) <= 0.0:
        raise ValueError(f"{name} must be positive and finite")


def _require_sha256(name: str, value: object) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{name} must be lowercase 64-hex")


if tuple(field.name for field in fields(ProvenanceIdentity)) != (
    _PROVENANCE_COMPONENTS
):
    raise TypeError("ProvenanceIdentity does not match the six-component contract")


__all__ = [
    "ImmutableRecord",
    "OracleAdmissionIdentity",
    "OracleRadialArtifact",
    "OracleRadialRecord",
    "RadialCache",
    "RadialCacheContractError",
    "RadialCacheRequest",
    "RadialCacheStats",
    "RadialModeKey",
    "RadialSample",
    "oracle_artifact_sha256",
]
