from __future__ import annotations

from dataclasses import FrozenInstanceError, dataclass, fields, replace
from typing import Any

import numpy as np
import pytest

from schwgw.numerics.radial_cache import (
    ImmutableRecord,
    OracleAdmissionIdentity,
    OracleRadialArtifact,
    OracleRadialRecord,
    RadialCache,
    RadialCacheContractError,
    RadialCacheRequest,
    RadialCacheStats,
    RadialModeKey,
    RadialSample,
    oracle_artifact_sha256,
)
from schwgw.scattering.contracts import ProvenanceIdentity


PROVENANCE_FIELDS = (
    "implementation_sha256",
    "physics_sha256",
    "solver_sha256",
    "config_sha256",
    "source_sha256",
    "gate_sha256",
)
T4AD_SCHEMA = "phase5_t4ad_another_bounded_local_radial_gate_v1"
T4AD_SNAPSHOT = "9f8c99dae0c182183a5e54d8bc8371e55f28ef2004dc928ad087829d33710bf7"


@dataclass(frozen=True)
class _Warning:
    code: str
    metadata: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class _Diagnostics:
    solver: str
    rtol: float = 1.0e-10
    atol: float = 1.0e-12
    boundary_residual: float = 1.0e-13
    wronskian_residual: float = 2.0e-13
    flux_residual: float = 3.0e-13
    raw_wronskian_residual: float = 4.0e-13
    match_condition_number: float = 1.25
    warnings: tuple[_Warning, ...] = ()


@dataclass
class _MutableDiagnostics:
    solver: str
    rtol: float = 1.0e-10
    atol: float = 1.0e-12
    boundary_residual: float = 1.0e-13
    wronskian_residual: float = 2.0e-13
    flux_residual: float = 3.0e-13
    raw_wronskian_residual: float = 4.0e-13
    match_condition_number: float = 1.25
    warnings: list[_Warning] | tuple[_Warning, ...] = ()


@dataclass(frozen=True)
class _DenseSolution:
    sector: str
    ell: int
    k: float
    lower: float
    upper: float
    diagnostics: _Diagnostics
    scale: float = 1.0
    valid_until_r: float | None = None
    A_in: complex = 1.0 + 0.0j
    A_out: complex = 0.25 - 0.5j
    phase_factor: complex = 0.5 + 0.25j
    phase_shift: complex = 0.125 - 0.25j
    psi_override: complex | None = None

    @property
    def r_grid(self) -> np.ndarray:
        return np.asarray([self.lower, self.upper], dtype=float)

    def psi_at(self, radius: float) -> complex:
        if self.psi_override is not None:
            return self.psi_override
        return self.scale * complex(radius, -radius)

    def dpsi_dr_at(self, radius: float) -> complex:
        return self.scale * complex(1.0 + radius / 100.0, -0.5)


def _current_identity() -> ProvenanceIdentity:
    return ProvenanceIdentity(
        implementation_sha256="1" * 64,
        physics_sha256="2" * 64,
        solver_sha256="3" * 64,
        config_sha256="4" * 64,
        source_sha256="5" * 64,
        gate_sha256="6" * 64,
    )


def _origin_identity() -> ProvenanceIdentity:
    return ProvenanceIdentity(
        implementation_sha256="a" * 64,
        physics_sha256="b" * 64,
        solver_sha256="c" * 64,
        config_sha256="d" * 64,
        source_sha256="e" * 64,
        gate_sha256="f" * 64,
    )


def _admission(
    *,
    origin_identity: ProvenanceIdentity | None = None,
) -> OracleAdmissionIdentity:
    return OracleAdmissionIdentity(
        artifact_sha256="7" * 64,
        schema_version=T4AD_SCHEMA,
        snapshot_sha256=T4AD_SNAPSHOT,
        origin_identity=origin_identity or _origin_identity(),
    )


def _request(
    *,
    sector: str = "odd",
    ell: int = 12,
    k: float = 1.5,
    point_id: str = "near_axis_x0_z30",
    radius: float = 30.0,
    rtol: float = 1.0e-10,
    atol: float = 1.0e-12,
    consumer_identity: ProvenanceIdentity | None = None,
) -> RadialCacheRequest:
    return RadialCacheRequest(
        mode=RadialModeKey(sector=sector, ell=ell, k=k),
        point_id=point_id,
        radius=radius,
        rtol=rtol,
        atol=atol,
        consumer_identity=consumer_identity or _current_identity(),
    )


def _oracle_record(
    request: RadialCacheRequest,
    *,
    psi: complex = 101.0 - 7.0j,
    dpsi_dr: complex = -3.0 + 5.0j,
    A_in: complex = 1.0 + 0.0j,
    A_out: complex = 0.75 + 0.25j,
    diagnostics: _Diagnostics | None = None,
) -> OracleRadialRecord:
    return OracleRadialRecord(
        mode=request.mode,
        point_id=request.point_id,
        radius=request.radius,
        rtol=request.rtol,
        atol=request.atol,
        psi=psi,
        dpsi_dr=dpsi_dr,
        A_in=A_in,
        A_out=A_out,
        phase_factor=-0.75 - 0.25j,
        phase_shift=0.125 + 0.375j,
        diagnostics=diagnostics
        or _Diagnostics(
            solver="q018_tablei_another_bounded_local_transition_oracle",
            warnings=(
                _Warning(
                    code=(
                        "q018_tablei_another_bounded_local_"
                        "transition_oracle_used"
                    ),
                    metadata=(("origin", "T4ad"),),
                ),
            ),
        ),
    )


def _artifact(
    admission: OracleAdmissionIdentity,
    *records: OracleRadialRecord,
) -> OracleRadialArtifact:
    ordered = tuple(records)
    bound_admission = replace(
        admission,
        artifact_sha256=oracle_artifact_sha256(admission, ordered),
    )
    return OracleRadialArtifact(admission=bound_admission, records=ordered)


def _ordinary_solver(
    calls: list[RadialCacheRequest],
    *,
    lower: float = 20.0,
    upper: float | None = None,
    diagnostics: _Diagnostics | None = None,
) -> Any:
    def solve(request: RadialCacheRequest) -> _DenseSolution:
        calls.append(request)
        solved_upper = request.radius if upper is None else upper
        request_diagnostics = replace(
            diagnostics or _Diagnostics(solver="outward_shooting"),
            rtol=request.rtol,
            atol=request.atol,
        )
        return _DenseSolution(
            sector=request.mode.sector,
            ell=request.mode.ell,
            k=request.mode.k,
            lower=lower,
            upper=solved_upper,
            valid_until_r=solved_upper,
            diagnostics=request_diagnostics,
        )

    return solve


def test_current_identity_is_the_complete_six_component_provenance() -> None:
    current = _current_identity()
    calls: list[RadialCacheRequest] = []
    cache = RadialCache(
        current_identity=current,
        solver=_ordinary_solver(calls),
    )

    (sample,) = cache.evaluate_many((_request(consumer_identity=current),))

    assert tuple(field.name for field in fields(ProvenanceIdentity)) == (
        PROVENANCE_FIELDS
    )
    assert isinstance(sample, RadialSample)
    assert sample.consumer_identity == current
    assert sample.oracle_admission is None
    assert len(calls) == 1


@pytest.mark.parametrize("component", PROVENANCE_FIELDS)
def test_each_wrong_current_identity_component_fails_closed_before_solver(
    component: str,
) -> None:
    current = _current_identity()
    wrong = replace(current, **{component: "0" * 64})
    calls: list[RadialCacheRequest] = []
    cache = RadialCache(
        current_identity=current,
        solver=_ordinary_solver(calls),
    )

    with pytest.raises(RadialCacheContractError) as raised:
        cache.evaluate_many((_request(consumer_identity=wrong),))

    assert raised.value.code == "radial_cache_identity_mismatch"
    assert raised.value.metadata["component"] == component
    assert raised.value.metadata["expected"] == getattr(current, component)
    assert raised.value.metadata["actual"] == getattr(wrong, component)
    assert calls == []
    assert cache.stats.request_rejection_count == 1


def test_ordinary_dense_solution_reuses_one_closed_certified_interval() -> None:
    calls: list[RadialCacheRequest] = []
    diagnostics = _Diagnostics(
        solver="outward_shooting",
        boundary_residual=7.0e-14,
        wronskian_residual=8.0e-14,
        flux_residual=9.0e-14,
        warnings=(_Warning("ordinary_warning"),),
    )
    cache = RadialCache(
        current_identity=_current_identity(),
        solver=_ordinary_solver(calls, lower=20.0, diagnostics=diagnostics),
    )
    requests = (
        _request(point_id="p20", radius=20.0),
        _request(point_id="p80", radius=80.0),
        _request(point_id="p40", radius=40.0),
        _request(point_id="p60", radius=60.0),
    )

    samples = cache.evaluate_many(requests)

    assert isinstance(samples, tuple)
    assert [sample.radius for sample in samples] == [20.0, 80.0, 40.0, 60.0]
    assert [sample.psi for sample in samples] == [
        complex(20.0, -20.0),
        complex(80.0, -80.0),
        complex(40.0, -40.0),
        complex(60.0, -60.0),
    ]
    assert [request.radius for request in calls] == [80.0]
    assert all(sample.source == "ordinary_dense" for sample in samples)
    assert all(
        sample.diagnostics.solver == diagnostics.solver
        and sample.diagnostics.boundary_residual
        == diagnostics.boundary_residual
        and sample.diagnostics.wronskian_residual
        == diagnostics.wronskian_residual
        for sample in samples
    )
    assert cache.stats.fresh_ode_solve_count == 1
    assert cache.stats.ordinary_miss_count == 1
    assert cache.stats.ordinary_hit_count == 3


def test_ordinary_dense_reuse_does_not_cross_closed_interval_boundary() -> None:
    calls: list[RadialCacheRequest] = []
    cache = RadialCache(
        current_identity=_current_identity(),
        solver=_ordinary_solver(calls, lower=20.0),
    )
    exact_upper = _request(point_id="upper", radius=40.0)
    exact_lower = _request(point_id="lower", radius=20.0)
    just_outside = _request(
        point_id="outside",
        radius=float(np.nextafter(40.0, np.inf)),
    )

    first = cache.evaluate_many((exact_upper,))[0]
    lower = cache.evaluate_many((exact_lower,))[0]
    outside = cache.evaluate_many((just_outside,))[0]

    assert first.source == "ordinary_dense"
    assert lower.source == "ordinary_dense"
    assert outside.source == "ordinary_dense"
    assert [request.radius for request in calls] == [
        40.0,
        float(np.nextafter(40.0, np.inf)),
    ]


def test_requested_order_survives_descending_internal_radius_schedule() -> None:
    calls: list[RadialCacheRequest] = []
    cache = RadialCache(
        current_identity=_current_identity(),
        solver=_ordinary_solver(calls, lower=10.0),
    )
    requests = tuple(
        _request(point_id=f"point-{index}", radius=radius)
        for index, radius in enumerate((31.0, 55.0, 42.0, 70.0, 24.0))
    )

    samples = cache.evaluate_many(requests)

    assert [request.radius for request in calls] == [70.0]
    assert [sample.radius for sample in samples] == [
        request.radius for request in requests
    ]
    assert [sample.psi for sample in samples] == [
        complex(request.radius, -request.radius) for request in requests
    ]


def test_exact_oracle_has_priority_over_covering_ordinary_dense_solution() -> None:
    current = _current_identity()
    admission = _admission()
    exact_request = _request(point_id="oracle-point", radius=40.0)
    exact_record = _oracle_record(exact_request, psi=900.0 + 1.0j)
    artifact = _artifact(admission, exact_record)
    calls: list[RadialCacheRequest] = []
    cache = RadialCache(
        current_identity=current,
        solver=_ordinary_solver(calls, lower=20.0),
        expected_oracle_admission=artifact.admission,
    )
    cache.admit_oracle(artifact)

    ordinary = cache.evaluate_many(
        (_request(point_id="far-ordinary", radius=60.0),)
    )[0]
    oracle = cache.evaluate_many((exact_request,))[0]

    assert ordinary.source == "ordinary_dense"
    assert oracle.source == "oracle_exact"
    assert oracle.psi == 900.0 + 1.0j
    assert oracle.diagnostics == exact_record.diagnostics
    assert [request.radius for request in calls] == [60.0]
    assert cache.stats.oracle_hit_count == 1


def test_oracle_exact_point_cannot_certify_a_neighboring_float() -> None:
    admission = _admission()
    exact = _request(point_id="same-point", radius=30.0)
    neighboring = replace(
        exact,
        radius=float(np.nextafter(exact.radius, np.inf)),
    )
    artifact = _artifact(admission, _oracle_record(exact))
    calls: list[RadialCacheRequest] = []
    cache = RadialCache(
        current_identity=_current_identity(),
        solver=_ordinary_solver(calls, lower=20.0),
        expected_oracle_admission=artifact.admission,
    )
    cache.admit_oracle(artifact)

    (sample,) = cache.evaluate_many((neighboring,))

    assert sample.source == "ordinary_dense"
    assert sample.psi != 101.0 - 7.0j
    assert calls == [neighboring]
    assert cache.stats.oracle_rejection_count == 1


@pytest.mark.parametrize(
    ("component", "mutate"),
    (
        ("sector", lambda request: replace(
            request,
            mode=replace(request.mode, sector="even"),
        )),
        ("ell", lambda request: replace(
            request,
            mode=replace(request.mode, ell=request.mode.ell + 1),
        )),
        ("k", lambda request: replace(
            request,
            mode=replace(request.mode, k=float(np.nextafter(request.mode.k, np.inf))),
        )),
        ("point_id", lambda request: replace(request, point_id="different-point")),
        ("radius", lambda request: replace(
            request,
            radius=float(np.nextafter(request.radius, np.inf)),
        )),
        ("rtol", lambda request: replace(request, rtol=2.0e-10)),
        ("atol", lambda request: replace(request, atol=2.0e-12)),
    ),
)
def test_oracle_key_strictly_binds_scientific_point_and_tolerances(
    component: str,
    mutate: Any,
) -> None:
    admission = _admission()
    exact = _request()
    changed = mutate(exact)
    artifact = _artifact(admission, _oracle_record(exact))
    calls: list[RadialCacheRequest] = []
    cache = RadialCache(
        current_identity=_current_identity(),
        solver=_ordinary_solver(calls, lower=20.0),
        expected_oracle_admission=artifact.admission,
    )
    cache.admit_oracle(artifact)

    (sample,) = cache.evaluate_many((changed,))

    assert sample.source == "ordinary_dense", component
    assert sample.psi != 101.0 - 7.0j
    assert calls == [changed]
    if component in {"sector", "ell", "k"}:
        assert cache.stats.oracle_miss_count == 1
    else:
        assert cache.stats.oracle_rejection_count == 1


def test_multiple_oracle_radii_for_one_mode_remain_distinct_exact_records() -> None:
    admission = _admission()
    at_30 = _request(point_id="p30", radius=30.0)
    at_40 = _request(point_id="p40", radius=40.0)
    between = _request(point_id="p35", radius=35.0)
    artifact = _artifact(
        admission,
        _oracle_record(at_30, psi=30.0 + 3.0j),
        _oracle_record(at_40, psi=40.0 + 4.0j),
    )
    calls: list[RadialCacheRequest] = []
    cache = RadialCache(
        current_identity=_current_identity(),
        solver=_ordinary_solver(calls, lower=20.0),
        expected_oracle_admission=artifact.admission,
    )
    cache.admit_oracle(artifact)

    samples = cache.evaluate_many((at_40, between, at_30))

    assert [sample.radius for sample in samples] == [40.0, 35.0, 30.0]
    assert samples[0].source == "oracle_exact"
    assert samples[0].psi == 40.0 + 4.0j
    assert samples[1].source == "ordinary_dense"
    assert samples[1].psi == 35.0 - 35.0j
    assert samples[2].source == "oracle_exact"
    assert samples[2].psi == 30.0 + 3.0j
    assert calls == [between]


@pytest.mark.parametrize(
    ("component", "changed_value"),
    (
        ("artifact_sha256", "8" * 64),
        ("schema_version", "wrong_oracle_schema"),
        ("snapshot_sha256", "9" * 64),
    ),
)
def test_wrong_oracle_artifact_schema_or_snapshot_is_structured_fail_closed(
    component: str,
    changed_value: str,
) -> None:
    record = _oracle_record(_request())
    expected = _artifact(_admission(), record).admission
    actual = replace(expected, **{component: changed_value})
    artifact = OracleRadialArtifact(admission=actual, records=(record,))
    calls: list[RadialCacheRequest] = []
    cache = RadialCache(
        current_identity=_current_identity(),
        solver=_ordinary_solver(calls),
        expected_oracle_admission=expected,
    )

    with pytest.raises(RadialCacheContractError) as raised:
        cache.admit_oracle(artifact)

    assert raised.value.code == "radial_cache_oracle_admission_mismatch"
    assert raised.value.metadata["component"] == component
    assert raised.value.metadata["expected"] == getattr(expected, component)
    assert raised.value.metadata["actual"] == getattr(actual, component)
    assert calls == []
    assert cache.stats.oracle_rejection_count == 1


@pytest.mark.parametrize("component", PROVENANCE_FIELDS)
def test_each_wrong_oracle_origin_component_is_structured_fail_closed(
    component: str,
) -> None:
    record = _oracle_record(_request())
    expected = _artifact(_admission(), record).admission
    wrong_origin = replace(
        expected.origin_identity,
        **{component: "0" * 64},
    )
    actual = replace(expected, origin_identity=wrong_origin)
    artifact = OracleRadialArtifact(admission=actual, records=(record,))
    calls: list[RadialCacheRequest] = []
    cache = RadialCache(
        current_identity=_current_identity(),
        solver=_ordinary_solver(calls),
        expected_oracle_admission=expected,
    )

    with pytest.raises(RadialCacheContractError) as raised:
        cache.admit_oracle(artifact)

    assert raised.value.code == "radial_cache_oracle_admission_mismatch"
    assert raised.value.metadata["component"] == f"origin_identity.{component}"
    assert raised.value.metadata["expected"] == getattr(
        expected.origin_identity,
        component,
    )
    assert raised.value.metadata["actual"] == getattr(wrong_origin, component)
    assert calls == []
    assert cache.stats.oracle_rejection_count == 1


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("psi", complex(np.nan, 0.0)),
        ("dpsi_dr", complex(0.0, np.inf)),
        ("A_in", complex(np.inf, 0.0)),
        ("A_out", complex(0.0, np.nan)),
    ),
)
def test_nonfinite_oracle_payload_is_rejected_before_solver(
    field_name: str,
    value: complex,
) -> None:
    admission = _admission()
    request = _request()
    record = replace(_oracle_record(request), **{field_name: value})
    calls: list[RadialCacheRequest] = []
    cache = RadialCache(
        current_identity=_current_identity(),
        solver=_ordinary_solver(calls),
        expected_oracle_admission=admission,
    )

    with pytest.raises(RadialCacheContractError) as raised:
        cache.admit_oracle(
            OracleRadialArtifact(admission=admission, records=(record,))
        )

    assert raised.value.code == "radial_cache_nonfinite_payload"
    assert raised.value.metadata["source"] == "oracle"
    assert raised.value.metadata["field"] == field_name
    assert calls == []
    assert cache.stats.oracle_rejection_count == 1


def test_nonfinite_oracle_residual_is_rejected_before_solver() -> None:
    admission = _admission()
    diagnostics = replace(
        _Diagnostics(solver="authenticated_oracle"),
        boundary_residual=float("nan"),
    )
    record = _oracle_record(_request(), diagnostics=diagnostics)
    calls: list[RadialCacheRequest] = []
    cache = RadialCache(
        current_identity=_current_identity(),
        solver=_ordinary_solver(calls),
        expected_oracle_admission=admission,
    )

    with pytest.raises(RadialCacheContractError) as raised:
        cache.admit_oracle(
            OracleRadialArtifact(admission=admission, records=(record,))
        )

    assert raised.value.code == "radial_cache_nonfinite_payload"
    assert raised.value.metadata["source"] == "oracle"
    assert raised.value.metadata["field"] == "diagnostics.boundary_residual"
    assert calls == []


def test_forged_finite_records_cannot_reuse_a_declared_artifact_hash() -> None:
    request = _request()
    trusted_record = _oracle_record(request, psi=101.0 - 7.0j)
    trusted = _artifact(_admission(), trusted_record)
    forged = OracleRadialArtifact(
        admission=trusted.admission,
        records=(_oracle_record(request, psi=999.0 + 0.0j),),
    )
    calls: list[RadialCacheRequest] = []
    cache = RadialCache(
        current_identity=_current_identity(),
        solver=_ordinary_solver(calls),
        expected_oracle_admission=trusted.admission,
    )

    with pytest.raises(RadialCacheContractError) as raised:
        cache.admit_oracle(forged)

    assert raised.value.code == "radial_cache_oracle_admission_mismatch"
    assert raised.value.metadata["component"] == "artifact_content_sha256"
    assert cache.stats.oracle_rejection_count == 1
    assert calls == []


def test_duplicate_oracle_admission_is_atomic_and_publishes_nothing() -> None:
    request = _request()
    record = _oracle_record(request)
    artifact = _artifact(_admission(), record, record)
    calls: list[RadialCacheRequest] = []
    cache = RadialCache(
        current_identity=_current_identity(),
        solver=_ordinary_solver(calls),
        expected_oracle_admission=artifact.admission,
    )

    with pytest.raises(RadialCacheContractError) as raised:
        cache.admit_oracle(artifact)
    (fallback,) = cache.evaluate_many((request,))

    assert raised.value.code == "radial_cache_oracle_record_collision"
    assert fallback.source == "ordinary_dense"
    assert fallback.psi != record.psi
    assert calls == [request]


def test_solver_returned_interval_must_certify_the_requested_radius() -> None:
    calls: list[RadialCacheRequest] = []

    def solve(request: RadialCacheRequest) -> _DenseSolution:
        calls.append(request)
        return _DenseSolution(
            sector=request.mode.sector,
            ell=request.mode.ell,
            k=request.mode.k,
            lower=20.0,
            upper=25.0,
            valid_until_r=25.0,
            diagnostics=_Diagnostics(
                solver="outward_shooting",
                rtol=request.rtol,
                atol=request.atol,
            ),
        )

    cache = RadialCache(current_identity=_current_identity(), solver=solve)
    request = _request(radius=30.0)

    for _ in range(2):
        with pytest.raises(RadialCacheContractError) as raised:
            cache.evaluate_many((request,))
        assert raised.value.code == "radial_cache_uncertified_radius"

    assert calls == [request, request]
    assert cache.stats.ordinary_rejection_count == 2
    assert cache.stats.fresh_ode_solve_count == 2


def test_nonfinite_fresh_solver_payload_is_rejected_and_not_cached() -> None:
    calls: list[RadialCacheRequest] = []

    def solve(request: RadialCacheRequest) -> _DenseSolution:
        calls.append(request)
        return _DenseSolution(
            sector=request.mode.sector,
            ell=request.mode.ell,
            k=request.mode.k,
            lower=20.0,
            upper=request.radius,
            valid_until_r=request.radius,
            diagnostics=_Diagnostics(
                solver="outward_shooting",
                rtol=request.rtol,
                atol=request.atol,
            ),
            psi_override=complex(np.nan, 0.0),
        )

    cache = RadialCache(
        current_identity=_current_identity(),
        solver=solve,
    )
    request = _request()

    for _ in range(2):
        with pytest.raises(RadialCacheContractError) as raised:
            cache.evaluate_many((request,))
        assert raised.value.code == "radial_cache_nonfinite_payload"
        assert raised.value.metadata["source"] == "fresh_ode"
        assert raised.value.metadata["field"] == "psi"

    assert calls == [request, request]
    assert cache.stats.ordinary_rejection_count == 2
    assert cache.stats.fresh_ode_solve_count == 2


def test_cache_stats_separate_ode_oracle_hits_misses_and_rejections() -> None:
    admission = _admission()
    admitted_request = _request(point_id="admitted", radius=30.0)
    artifact = _artifact(admission, _oracle_record(admitted_request))
    calls: list[RadialCacheRequest] = []

    def solve(request: RadialCacheRequest) -> _DenseSolution:
        calls.append(request)
        if request.mode.ell == 99:
            return _DenseSolution(
                sector=request.mode.sector,
                ell=request.mode.ell,
                k=request.mode.k,
                lower=request.radius,
                upper=request.radius + 1.0e-6,
                valid_until_r=request.radius,
                diagnostics=_Diagnostics(
                    solver="q018_tablei_another_bounded_local_transition_oracle",
                    rtol=request.rtol,
                    atol=request.atol,
                ),
                scale=9.0,
            )
        return _DenseSolution(
            sector=request.mode.sector,
            ell=request.mode.ell,
            k=request.mode.k,
            lower=20.0,
            upper=50.0,
            valid_until_r=50.0,
            diagnostics=_Diagnostics(
                solver="outward_shooting",
                rtol=request.rtol,
                atol=request.atol,
            ),
        )

    cache = RadialCache(
        current_identity=_current_identity(),
        solver=solve,
        expected_oracle_admission=artifact.admission,
    )
    cache.admit_oracle(artifact)
    ordinary_miss = _request(point_id="ordinary-31", radius=31.0)
    ordinary_hit = _request(point_id="ordinary-40", radius=40.0)
    fresh_oracle = _request(ell=99, point_id="fresh-oracle", radius=36.0)

    cache.evaluate_many((admitted_request,))
    cache.evaluate_many((ordinary_miss,))
    cache.evaluate_many((ordinary_hit,))
    for _ in range(2):
        with pytest.raises(RadialCacheContractError) as raised:
            cache.evaluate_many((fresh_oracle,))
        assert raised.value.code == "radial_cache_unadmitted_oracle_solution"

    stats = cache.stats
    assert isinstance(stats, RadialCacheStats)
    assert stats.fresh_ode_solve_count == 1
    assert stats.fresh_oracle_solve_count == 2
    assert stats.ordinary_hit_count == 1
    assert stats.ordinary_miss_count == 3
    assert stats.ordinary_rejection_count == 0
    assert stats.oracle_hit_count == 1
    assert stats.oracle_miss_count == 2
    assert stats.oracle_rejection_count == 4
    assert stats.request_rejection_count == 0
    assert calls == [ordinary_miss, fresh_oracle, fresh_oracle]
    with pytest.raises(FrozenInstanceError):
        setattr(stats, "fresh_ode_solve_count", 999)


def test_samples_are_immutable_and_propagate_warning_residual_provenance() -> None:
    current = _current_identity()
    origin = _origin_identity()
    admission = _admission(origin_identity=origin)
    ordinary_diagnostics = _Diagnostics(
        solver="bidirectional_match",
        boundary_residual=1.1e-12,
        wronskian_residual=1.2e-12,
        flux_residual=1.3e-12,
        raw_wronskian_residual=1.4e-12,
        match_condition_number=2.5,
        warnings=(_Warning("ordinary_structured_warning"),),
    )
    oracle_diagnostics = _Diagnostics(
        solver="q018_tablei_another_bounded_local_transition_oracle",
        boundary_residual=2.1e-12,
        wronskian_residual=2.2e-12,
        flux_residual=2.3e-12,
        raw_wronskian_residual=2.4e-12,
        match_condition_number=3.5,
        warnings=(
            _Warning(
                "q018_tablei_another_bounded_local_transition_oracle_used",
                metadata=(("snapshot", T4AD_SNAPSHOT),),
            ),
        ),
    )
    exact = _request(point_id="oracle", radius=30.0)
    record = _oracle_record(exact, diagnostics=oracle_diagnostics)
    artifact = _artifact(admission, record)
    calls: list[RadialCacheRequest] = []
    cache = RadialCache(
        current_identity=current,
        solver=_ordinary_solver(
            calls,
            lower=20.0,
            diagnostics=ordinary_diagnostics,
        ),
        expected_oracle_admission=artifact.admission,
    )
    cache.admit_oracle(artifact)

    ordinary, oracle = cache.evaluate_many(
        (
            _request(point_id="ordinary", radius=40.0),
            exact,
        )
    )

    assert current != origin
    assert ordinary.diagnostics.solver == ordinary_diagnostics.solver
    assert ordinary.diagnostics.warnings[0].code == "ordinary_structured_warning"
    assert ordinary.consumer_identity == current
    assert ordinary.oracle_admission is None
    assert oracle.diagnostics.solver == oracle_diagnostics.solver
    assert oracle.diagnostics.boundary_residual == 2.1e-12
    assert oracle.diagnostics.raw_wronskian_residual == 2.4e-12
    assert oracle.diagnostics.warnings[0].code == (
        "q018_tablei_another_bounded_local_transition_oracle_used"
    )
    assert oracle.consumer_identity == current
    assert oracle.oracle_admission == artifact.admission
    assert oracle.oracle_admission.origin_identity == origin
    assert oracle.consumer_identity != oracle.oracle_admission.origin_identity
    with pytest.raises(FrozenInstanceError):
        setattr(ordinary, "psi", 0.0j)
    with pytest.raises(FrozenInstanceError):
        setattr(oracle, "radius", 31.0)
    with pytest.raises(FrozenInstanceError):
        setattr(record, "psi", 0.0j)


def test_cached_diagnostics_are_deep_snapshots_not_mutable_aliases() -> None:
    request = _request(point_id="mutable-oracle")
    oracle_diagnostics = _MutableDiagnostics(
        solver="authenticated_oracle",
        warnings=[_Warning("before-admission")],
    )
    record = _oracle_record(request, diagnostics=oracle_diagnostics)  # type: ignore[arg-type]
    artifact = _artifact(_admission(), record)
    ordinary_diagnostics = _MutableDiagnostics(solver="outward_shooting")
    calls: list[RadialCacheRequest] = []
    cache = RadialCache(
        current_identity=_current_identity(),
        solver=_ordinary_solver(  # type: ignore[arg-type]
            calls,
            diagnostics=ordinary_diagnostics,
        ),
        expected_oracle_admission=artifact.admission,
    )
    cache.admit_oracle(artifact)

    oracle_diagnostics.boundary_residual = float("nan")
    assert isinstance(oracle_diagnostics.warnings, list)
    oracle_diagnostics.warnings.append(_Warning("after-admission"))
    oracle = cache.evaluate_many((request,))[0]
    ordinary_request = _request(point_id="ordinary", radius=40.0)
    ordinary = cache.evaluate_many((ordinary_request,))[0]
    ordinary_diagnostics.boundary_residual = float("nan")
    ordinary_again = cache.evaluate_many((ordinary_request,))[0]

    assert oracle.diagnostics.boundary_residual == 1.0e-13
    assert tuple(warning.code for warning in oracle.diagnostics.warnings) == (
        "before-admission",
    )
    assert ordinary.diagnostics.boundary_residual == 1.0e-13
    assert ordinary_again.diagnostics.boundary_residual == 1.0e-13
    with pytest.raises(FrozenInstanceError):
        setattr(oracle.diagnostics, "boundary_residual", float("nan"))


def test_manual_immutable_record_is_recursively_snapshotted() -> None:
    request = _request(point_id="manual-record")
    nested = {"warnings": [_Warning("before-snapshot")]}
    diagnostics = ImmutableRecord(
        type_name="manual",
        items=(
            ("solver", "authenticated_oracle"),
            ("rtol", request.rtol),
            ("atol", request.atol),
            ("boundary_residual", 1.0e-13),
            ("wronskian_residual", 2.0e-13),
            ("flux_residual", 3.0e-13),
            ("raw_wronskian_residual", 4.0e-13),
            ("match_condition_number", 1.25),
            ("warnings", ()),
            ("nested", nested),
        ),
    )
    record = _oracle_record(
        request,
        diagnostics=diagnostics,  # type: ignore[arg-type]
    )
    artifact = _artifact(_admission(), record)
    cache = RadialCache(
        current_identity=_current_identity(),
        solver=lambda _: pytest.fail("exact oracle must not call solver"),
        expected_oracle_admission=artifact.admission,
    )
    cache.admit_oracle(artifact)

    nested["warnings"].append(_Warning("after-snapshot"))
    sample = cache.evaluate_many((request,))[0]

    assert tuple(warning.code for warning in sample.diagnostics.nested["warnings"]) == (
        "before-snapshot",
    )


def test_mapping_diagnostics_are_checked_for_nonfinite_residuals() -> None:
    request = _request(point_id="mapping-nonfinite")
    record = _oracle_record(
        request,
        diagnostics={  # type: ignore[arg-type]
            "solver": "authenticated_oracle",
            "rtol": request.rtol,
            "atol": request.atol,
            "boundary_residual": float("nan"),
            "wronskian_residual": 2.0e-13,
            "flux_residual": 3.0e-13,
            "raw_wronskian_residual": 4.0e-13,
            "match_condition_number": 1.25,
            "warnings": (),
        },
    )
    admission = _admission()
    cache = RadialCache(
        current_identity=_current_identity(),
        solver=lambda _: pytest.fail("invalid oracle must not call solver"),
        expected_oracle_admission=admission,
    )

    with pytest.raises(RadialCacheContractError) as raised:
        cache.admit_oracle(
            OracleRadialArtifact(
                admission=admission,
                records=(record,),
            )
        )

    assert raised.value.code == "radial_cache_nonfinite_payload"
    assert raised.value.metadata["field"] == "diagnostics.boundary_residual"


def test_oracle_hash_preserves_mapping_key_types_without_string_collision() -> None:
    request = _request(point_id="typed-mapping-keys")
    first = _oracle_record(
        request,
        diagnostics={1: "integer", "1": "string"},  # type: ignore[arg-type]
    )
    second = _oracle_record(
        request,
        diagnostics={1: "string", "1": "integer"},  # type: ignore[arg-type]
    )

    assert oracle_artifact_sha256(_admission(), (first,)) != (
        oracle_artifact_sha256(_admission(), (second,))
    )


def test_immutable_record_rejects_duplicate_semantic_keys() -> None:
    with pytest.raises(ValueError, match="must be unique"):
        ImmutableRecord(
            type_name="forged",
            items=(
                ("solver", "forged"),
                ("solver", "trusted"),
            ),
        )


def test_oracle_admission_requires_complete_diagnostic_provenance() -> None:
    request = _request(point_id="missing-diagnostics")
    record = _oracle_record(
        request,
        diagnostics={"solver": "authenticated_oracle"},  # type: ignore[arg-type]
    )
    admission = _admission()
    cache = RadialCache(
        current_identity=_current_identity(),
        solver=lambda _: pytest.fail("invalid oracle must not call solver"),
        expected_oracle_admission=admission,
    )

    with pytest.raises(RadialCacheContractError) as raised:
        cache.admit_oracle(
            OracleRadialArtifact(
                admission=admission,
                records=(record,),
            )
        )

    assert raised.value.code == "radial_cache_missing_diagnostic"
    assert raised.value.metadata["field"] == "diagnostics.rtol"


@pytest.mark.parametrize(
    ("component", "replacement"),
    (
        ("rtol", 2.0e-10),
        ("atol", 2.0e-12),
    ),
)
def test_oracle_record_diagnostics_bind_exact_tolerances(
    component: str,
    replacement: float,
) -> None:
    request = _request(point_id=f"oracle-{component}-mismatch")
    diagnostics = _Diagnostics(
        solver="q018_tablei_another_bounded_local_transition_oracle",
        rtol=request.rtol,
        atol=request.atol,
    )
    record = _oracle_record(
        request,
        diagnostics=replace(
            diagnostics,
            **{component: replacement},
        ),
    )
    artifact = _artifact(_admission(), record)
    cache = RadialCache(
        current_identity=_current_identity(),
        solver=lambda _: pytest.fail("invalid oracle must not call solver"),
        expected_oracle_admission=artifact.admission,
    )

    with pytest.raises(RadialCacheContractError) as raised:
        cache.admit_oracle(artifact)

    assert (
        raised.value.code
        == "radial_cache_oracle_record_identity_mismatch"
    )
    assert raised.value.metadata["component"] == f"diagnostics.{component}"
    assert raised.value.metadata["expected"] == getattr(request, component)
    assert raised.value.metadata["actual"] == replacement
    assert cache.stats.oracle_rejection_count == 1


@pytest.mark.parametrize(
    ("component", "replacement"),
    (
        ("sector", "even"),
        ("ell", 13),
        ("k", 1.6),
        ("rtol", 2.0e-10),
        ("atol", 2.0e-12),
    ),
)
def test_fresh_solution_identity_and_tolerances_match_the_request(
    component: str,
    replacement: object,
) -> None:
    request = _request()

    def solve(actual_request: RadialCacheRequest) -> _DenseSolution:
        values: dict[str, object] = {
            "sector": actual_request.mode.sector,
            "ell": actual_request.mode.ell,
            "k": actual_request.mode.k,
            "rtol": actual_request.rtol,
            "atol": actual_request.atol,
        }
        values[component] = replacement
        return _DenseSolution(
            sector=str(values["sector"]),
            ell=int(values["ell"]),
            k=float(values["k"]),
            lower=20.0,
            upper=40.0,
            valid_until_r=40.0,
            diagnostics=_Diagnostics(
                solver="outward_shooting",
                rtol=float(values["rtol"]),
                atol=float(values["atol"]),
            ),
        )

    cache = RadialCache(
        current_identity=_current_identity(),
        solver=solve,
    )

    with pytest.raises(RadialCacheContractError) as raised:
        cache.evaluate_many((request,))

    assert raised.value.code == "radial_cache_solution_identity_mismatch"
    assert raised.value.metadata["component"] == component
    assert cache.stats.fresh_ode_solve_count == 1
    assert cache.stats.ordinary_rejection_count == 1
