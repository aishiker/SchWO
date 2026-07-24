from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from types import MappingProxyType, SimpleNamespace
from typing import Any, Callable

import numpy as np
import pytest

import schwgw.scattering.partial_wave as partial_wave_module
from schwgw.backgrounds.schwarzschild import SchwarzschildBackground
from schwgw.perturbations import Sector
from schwgw.scattering.contracts import (
    ChannelSpec,
    IncidentSourceProtocol,
    ModeKey,
)
from schwgw.scattering.legacy_adapter import (
    LEGACY_ODD_CHANNEL,
    LegacyIncidentSourceAdapter,
    LegacyScalarRWZAdapter,
)
from schwgw.scattering.partial_wave import compute_polarization
from schwgw.scattering.weyl import WeylModeComponents
from schwgw.waves.incident import IncidentPlaneGW
from schwgw.waves.polarizations import circular_to_linear


pytestmark = pytest.mark.physics

_FROZEN_FREQUENCY_LMAX = (
    (0.86875, (24, 36, 60, 84)),
    (1.58125, (72, 96, 120, 144)),
    (2.91875, (192, 216, 240, 264)),
    (3.759375, (276, 300, 324, 348)),
    (3.89375, (288, 312, 336, 360)),
)
_FROZEN_POINTS = (
    ("near_axis_x0_z30", 0.0),
    ("near_axis_x1_z30", 1.0),
    ("near_axis_x2_z30", 2.0),
    ("near_axis_x3_z30", 3.0),
    ("far_axis_x10_z30", 10.0),
    ("far_axis_x15_z30", 15.0),
    ("far_axis_x20_z30", 20.0),
    ("far_axis_x25_z30", 25.0),
)
_FROZEN_MATRIX = tuple(
    pytest.param(k, lmax, point_id, x, id=f"k{k:g}-l{lmax}-{point_id}")
    for k, lmax_values in _FROZEN_FREQUENCY_LMAX
    for lmax in lmax_values
    for point_id, x in _FROZEN_POINTS
)
_FROZEN_FREQUENCY_LMAX_PAIRS = tuple(
    pytest.param(k, lmax, id=f"k{k:g}-l{lmax}")
    for k, lmax_values in _FROZEN_FREQUENCY_LMAX
    for lmax in lmax_values
)
_ORDINARY_AMPLITUDES = (0.73 - 0.19j, -0.31 + 0.41j)
_PURE_LEFT_AMPLITUDES = circular_to_linear(1.2 - 0.4j, 0.0j)
_PURE_RIGHT_AMPLITUDES = circular_to_linear(0.0j, -0.6 + 0.9j)
_AMPLITUDE_CASES = (
    pytest.param(*_ORDINARY_AMPLITUDES, id="ordinary-complex"),
    pytest.param(*_PURE_LEFT_AMPLITUDES, id="pure-left-circular"),
    pytest.param(*_PURE_RIGHT_AMPLITUDES, id="pure-right-circular"),
    pytest.param(0.0j, 0.0j, id="both-zero"),
)
_NP_LABELS = ("Psi0", "Psi1", "Psi2", "Psi3", "Psi4")
_COMPONENT_FACTORS = (
    1.0 + 0.0j,
    -0.25 + 0.5j,
    0.75 - 0.125j,
    -0.5 - 0.25j,
    0.125 + 0.875j,
)
_ODD_CHANNEL = ChannelSpec(
    name="legacy_rwz_odd",
    field_spin=2,
    polarization="legacy_tensor",
    parity="odd",
    radial_structure="scalar",
    component_names=("master",),
    physical_claim=True,
)
_EVEN_CHANNEL = ChannelSpec(
    name="legacy_rwz_even",
    field_spin=2,
    polarization="legacy_tensor",
    parity="even",
    radial_structure="scalar",
    component_names=("master",),
    physical_claim=True,
)


@dataclass
class _IndependentLegacySource:
    """Independent source using the frozen ``IncidentPlaneGW`` coefficients."""

    wave: IncidentPlaneGW
    m_values: tuple[int, ...] | None
    coefficient_query_count: int = 0
    name: str = "independent_legacy_reference"
    physical_claim: bool = True

    def supported_m_values(self, ell: int) -> tuple[int, ...] | None:
        del ell
        return self.m_values

    def amplitude(self, mode: ModeKey, channel: ChannelSpec) -> np.ndarray:
        self.coefficient_query_count += 1
        assert mode.channel == channel.name
        if channel.parity == "odd":
            value = self.wave.c_lm_odd(mode.ell, mode.m)
        elif channel.parity == "even":
            value = self.wave.c_lm_even(mode.ell, mode.m)
        else:
            raise AssertionError(f"unexpected legacy channel parity: {channel.parity}")
        return np.array([value], dtype=np.complex128)


@dataclass
class _RecordingModeSource:
    m_values: tuple[int, ...] | None
    coefficient_queries: list[tuple[Sector, int, int]] = field(default_factory=list)
    support_queries: list[int] = field(default_factory=list)
    name: str = "generic_recording_source"
    physical_claim: bool = False

    def supported_m_values(self, ell: int) -> tuple[int, ...] | None:
        self.support_queries.append(ell)
        return self.m_values

    def amplitude(self, mode: ModeKey, channel: ChannelSpec) -> np.ndarray:
        assert mode.channel == channel.name
        if channel.parity == "odd":
            sector = Sector.ODD
            value = complex(mode.ell + 0.125 * mode.m, 0.25)
        elif channel.parity == "even":
            sector = Sector.EVEN
            value = complex(-0.5 * mode.ell, mode.m + 0.75)
        else:
            raise AssertionError(f"unexpected legacy channel parity: {channel.parity}")
        self.coefficient_queries.append((sector, mode.ell, mode.m))
        return np.array([value], dtype=np.complex128)


class _DerivedLegacySource(LegacyIncidentSourceAdapter):
    """A structural source that must not inherit the exact legacy fast path."""

    amplitude_query_count = 0

    def amplitude(self, mode: ModeKey, channel: ChannelSpec) -> np.ndarray:
        type(self).amplitude_query_count += 1
        return np.array(
            [complex(mode.ell + mode.m, 1.0 if channel.parity == "odd" else 2.0)],
            dtype=np.complex128,
        )


def _point_coordinates(x: float) -> tuple[float, float, float]:
    z = 30.0
    return math.hypot(x, z), math.atan2(x, z), 0.0


def _synthetic_mode(
    *,
    sector: Sector,
    ell: int,
    m: int,
    coefficient: complex,
    k: float,
    r: float,
    theta: float,
    phi: float,
    **_: Any,
) -> WeylModeComponents:
    """Cheap deterministic mode preserving coefficient and reduction order."""

    parity_factor = 1.0 + 0.375j if sector is Sector.ODD else -0.625 + 0.25j
    point_factor = complex(
        1.0 + 1.0e-7 * (ell + m) + 1.0e-8 * (r + theta),
        1.0e-8 * (k + phi),
    )
    value = complex(coefficient) * parity_factor * point_factor
    components = {
        label: value * factor
        for label, factor in zip(_NP_LABELS, _COMPONENT_FACTORS, strict=True)
    }
    zeros = {label: 0.0j for label in _NP_LABELS}
    return WeylModeComponents(
        sector=sector,
        ell=ell,
        m=m,
        k=k,
        r=r,
        theta=theta,
        phi=phi,
        components=MappingProxyType(components),
        spin_weights=MappingProxyType(
            {"Psi0": 2, "Psi1": 1, "Psi2": 0, "Psi3": -1, "Psi4": -2}
        ),
        angular_factors=MappingProxyType(zeros),
        radial_sources=MappingProxyType(zeros),
    )


def _install_synthetic_mode_kernel(
    monkeypatch: pytest.MonkeyPatch,
    *,
    mode_order: list[tuple[Sector, int, int]] | None = None,
    reduction_order: list[tuple[tuple[Sector, int, int], ...]] | None = None,
) -> None:
    real_assemble = partial_wave_module.assemble_weyl_scalars

    def recording_mode(**kwargs: Any) -> WeylModeComponents:
        mode = _synthetic_mode(**kwargs)
        if mode_order is not None:
            mode_order.append((mode.sector, mode.ell, mode.m))
        return mode

    def recording_assemble(
        modes: list[WeylModeComponents],
    ) -> dict[str, complex]:
        if reduction_order is not None:
            reduction_order.append(
                tuple((mode.sector, mode.ell, mode.m) for mode in modes)
            )
        return real_assemble(modes)

    monkeypatch.setattr(partial_wave_module, "_scaled_weyl_mode", recording_mode)
    monkeypatch.setattr(partial_wave_module, "assemble_weyl_scalars", recording_assemble)
    monkeypatch.setattr(
        partial_wave_module,
        "transform_strict_np_weyl_to_incident_tetrad",
        lambda scalars, *, theta, phi: dict(scalars),
    )


def _compute_with_source(
    *,
    k: float,
    lmax: int,
    x: float,
    source: object,
    radial_solver: Callable[..., object] | None = None,
):
    r, theta, phi = _point_coordinates(x)
    kwargs: dict[str, object] = {}
    if radial_solver is not None:
        kwargs["radial_solver"] = radial_solver
    return compute_polarization(
        background=SchwarzschildBackground(M=1.0),
        k=k,
        r=r,
        theta=theta,
        phi=phi,
        A_plus=_ORDINARY_AMPLITUDES[0],
        A_cross=_ORDINARY_AMPLITUDES[1],
        lmax=lmax,
        mode_source=source,
        **kwargs,
    )


def _assert_results_exact(reference: object, candidate: object) -> None:
    for name in (
        "h_plus",
        "h_cross",
        "psi0_hat",
        "psi4_hat",
        "hddot_plus",
        "hddot_cross",
    ):
        assert getattr(candidate, name) == getattr(reference, name)
    assert getattr(candidate, "lmax") == getattr(reference, "lmax")
    assert dict(getattr(candidate, "diagnostics")) == dict(
        getattr(reference, "diagnostics")
    )


@pytest.mark.parametrize(("k", "lmax", "point_id", "x"), _FROZEN_MATRIX)
def test_ordered_sparse_adapter_matches_independent_legacy_on_frozen_matrix(
    monkeypatch: pytest.MonkeyPatch,
    k: float,
    lmax: int,
    point_id: str,
    x: float,
) -> None:
    """Exercise all 160 frozen frequency/point/lmax combinations without ODEs."""

    del point_id
    _install_synthetic_mode_kernel(monkeypatch)
    wave = IncidentPlaneGW(k, *_ORDINARY_AMPLITUDES)
    independent_reference = _IndependentLegacySource(wave, m_values=(-2, 2))
    sparse_source = LegacyIncidentSourceAdapter(wave)

    reference = _compute_with_source(
        k=k,
        lmax=lmax,
        x=x,
        source=independent_reference,
    )
    candidate = _compute_with_source(k=k, lmax=lmax, x=x, source=sparse_source)

    _assert_results_exact(reference, candidate)
    assert independent_reference.coefficient_query_count == 4 * (lmax - 1)


@pytest.mark.parametrize(("k", "lmax"), _FROZEN_FREQUENCY_LMAX_PAIRS)
def test_ordered_sparse_adapter_matches_direct_legacy_full_m_reference(
    monkeypatch: pytest.MonkeyPatch,
    k: float,
    lmax: int,
) -> None:
    """Directly compare full-m and sparse paths for every frozen k/lmax pair."""

    _install_synthetic_mode_kernel(monkeypatch)
    wave = IncidentPlaneGW(k, *_ORDINARY_AMPLITUDES)
    full_m_reference = _IndependentLegacySource(wave, m_values=None)
    sparse_source = LegacyIncidentSourceAdapter(wave)

    reference = _compute_with_source(
        k=k,
        lmax=lmax,
        x=3.0,
        source=full_m_reference,
    )
    candidate = _compute_with_source(k=k, lmax=lmax, x=3.0, source=sparse_source)

    _assert_results_exact(reference, candidate)
    assert full_m_reference.coefficient_query_count == 2 * sum(
        2 * ell + 1 for ell in range(2, lmax + 1)
    )


@pytest.mark.parametrize(("A_plus", "A_cross"), _AMPLITUDE_CASES)
@pytest.mark.parametrize("k", tuple(case[0] for case in _FROZEN_FREQUENCY_LMAX))
def test_legacy_source_adapter_preserves_frozen_incident_normalization(
    k: float,
    A_plus: complex,
    A_cross: complex,
) -> None:
    legacy_wave = IncidentPlaneGW(k, A_plus, A_cross)
    source = LegacyScalarRWZAdapter().incident_source(k, A_plus, A_cross)

    assert isinstance(source, LegacyIncidentSourceAdapter)
    assert isinstance(source, IncidentSourceProtocol)
    assert source.supported_m_values(2) == (-2, 2)
    assert source.supported_m_values(9) == (-2, 2)
    for ell in (2, 7):
        for m in range(-ell, ell + 1):
            for sector, channel, expected in (
                (Sector.ODD, _ODD_CHANNEL, legacy_wave.c_lm_odd(ell, m)),
                (Sector.EVEN, _EVEN_CHANNEL, legacy_wave.c_lm_even(ell, m)),
            ):
                mode = ModeKey(
                    frequency=k,
                    ell=ell,
                    m=m,
                    channel=channel.name,
                )
                amplitude = source.amplitude(mode, channel)
                assert amplitude.shape == (1,)
                assert amplitude.dtype == np.dtype(np.complex128)
                assert amplitude[0] == expected
                assert source.coefficient(sector, ell, m) == expected


def test_default_legacy_path_runs_through_full_adapter_facade_exactly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_synthetic_mode_kernel(monkeypatch)
    calls = 0
    real_facade = LegacyScalarRWZAdapter.compute_polarization

    def recording_facade(
        adapter: LegacyScalarRWZAdapter,
        **kwargs: Any,
    ) -> object:
        nonlocal calls
        calls += 1
        return real_facade(adapter, **kwargs)

    monkeypatch.setattr(
        LegacyScalarRWZAdapter,
        "compute_polarization",
        recording_facade,
    )
    k = 0.86875
    r, theta, phi = _point_coordinates(3.0)
    default = compute_polarization(
        background=SchwarzschildBackground(M=1.0),
        k=k,
        r=r,
        theta=theta,
        phi=phi,
        A_plus=_ORDINARY_AMPLITUDES[0],
        A_cross=_ORDINARY_AMPLITUDES[1],
        lmax=4,
    )
    explicit = _compute_with_source(
        k=k,
        lmax=4,
        x=3.0,
        source=LegacyIncidentSourceAdapter(
            IncidentPlaneGW(k, *_ORDINARY_AMPLITUDES)
        ),
    )

    assert calls == 1
    _assert_results_exact(explicit, default)


@pytest.mark.parametrize(
    "spoofed_channel",
    (
        replace(LEGACY_ODD_CHANNEL, field_spin=0),
        replace(LEGACY_ODD_CHANNEL, polarization="toy"),
        replace(LEGACY_ODD_CHANNEL, component_names=("toy",)),
        replace(LEGACY_ODD_CHANNEL, physical_claim=False),
        replace(LEGACY_ODD_CHANNEL, name="spoofed_legacy_name"),
    ),
)
def test_legacy_source_rejects_channel_specs_outside_the_two_frozen_channels(
    spoofed_channel: ChannelSpec,
) -> None:
    source = LegacyScalarRWZAdapter().incident_source(
        0.86875,
        *_ORDINARY_AMPLITUDES,
    )
    mode = ModeKey(
        frequency=0.86875,
        ell=2,
        m=-2,
        channel=spoofed_channel.name,
    )

    with pytest.raises(ValueError, match="two frozen legacy RWZ channels"):
        source.amplitude(mode, spoofed_channel)


def test_legacy_fast_path_queries_only_minus2_plus2_in_frozen_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    coefficient_queries: list[tuple[Sector, int, int]] = []
    mode_order: list[tuple[Sector, int, int]] = []
    reduction_order: list[tuple[tuple[Sector, int, int], ...]] = []
    real_coefficient = LegacyIncidentSourceAdapter.coefficient

    def recording_coefficient(
        source: LegacyIncidentSourceAdapter,
        sector: Sector,
        ell: int,
        m: int,
    ) -> complex:
        coefficient_queries.append((sector, ell, m))
        return real_coefficient(source, sector, ell, m)

    monkeypatch.setattr(
        LegacyIncidentSourceAdapter,
        "coefficient",
        recording_coefficient,
    )
    _install_synthetic_mode_kernel(
        monkeypatch,
        mode_order=mode_order,
        reduction_order=reduction_order,
    )
    source = LegacyScalarRWZAdapter().incident_source(
        0.86875,
        *_ORDINARY_AMPLITUDES,
    )

    _compute_with_source(k=0.86875, lmax=4, x=2.0, source=source)

    expected = [
        (sector, ell, m)
        for ell in range(2, 5)
        for m in (-2, 2)
        for sector in (Sector.ODD, Sector.EVEN)
    ]
    assert coefficient_queries == expected
    assert mode_order == expected
    assert reduction_order == [tuple(expected)]


def test_sparse_source_query_and_reduction_order_is_exact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mode_order: list[tuple[Sector, int, int]] = []
    reduction_order: list[tuple[tuple[Sector, int, int], ...]] = []
    _install_synthetic_mode_kernel(
        monkeypatch,
        mode_order=mode_order,
        reduction_order=reduction_order,
    )
    source = _RecordingModeSource(m_values=(2, -2))

    _compute_with_source(k=0.86875, lmax=4, x=3.0, source=source)

    expected = [
        (sector, ell, m)
        for ell in range(2, 5)
        for m in (2, -2)
        for sector in (Sector.ODD, Sector.EVEN)
    ]
    assert source.support_queries == [2, 3, 4]
    assert source.coefficient_queries == expected
    assert mode_order == expected
    assert reduction_order == [tuple(expected)]


def test_generic_source_none_support_falls_back_to_full_ordered_m_range(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A generic source is not assumed to be the legacy ``+z`` source."""

    mode_order: list[tuple[Sector, int, int]] = []
    reduction_order: list[tuple[tuple[Sector, int, int], ...]] = []
    _install_synthetic_mode_kernel(
        monkeypatch,
        mode_order=mode_order,
        reduction_order=reduction_order,
    )
    source = _RecordingModeSource(m_values=None)

    _compute_with_source(k=1.58125, lmax=4, x=10.0, source=source)

    expected = [
        (sector, ell, m)
        for ell in range(2, 5)
        for m in range(-ell, ell + 1)
        for sector in (Sector.ODD, Sector.EVEN)
    ]
    assert source.support_queries == [2, 3, 4]
    assert source.coefficient_queries == expected
    assert mode_order == expected
    assert reduction_order == [tuple(expected)]


def test_generic_scalar_source_rejects_nonvector_singleton_shape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_synthetic_mode_kernel(monkeypatch)

    class MatrixSingletonSource(_RecordingModeSource):
        def amplitude(
            self,
            mode: ModeKey,
            channel: ChannelSpec,
        ) -> np.ndarray:
            del mode, channel
            return np.asarray([[1.0 + 0.0j]], dtype=np.complex128)

    with pytest.raises(ValueError, match=r"shape \(1,\)"):
        _compute_with_source(
            k=0.86875,
            lmax=2,
            x=2.0,
            source=MatrixSingletonSource(m_values=(0,)),
        )


def test_legacy_subclass_uses_public_generic_path_and_does_not_zero_short_circuit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_synthetic_mode_kernel(monkeypatch)
    _DerivedLegacySource.amplitude_query_count = 0
    source = _DerivedLegacySource(IncidentPlaneGW(0.86875, 0.0j, 0.0j))

    result = _compute_with_source(k=0.86875, lmax=3, x=2.0, source=source)

    assert _DerivedLegacySource.amplitude_query_count == 8
    assert result.diagnostics["mode_count"] == 8.0
    assert result.diagnostics["nonzero_coefficient_count"] == 8.0


def test_exact_legacy_fast_path_rejects_mismatched_source_frequency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_synthetic_mode_kernel(monkeypatch)
    source = LegacyIncidentSourceAdapter(
        IncidentPlaneGW(1.58125, *_ORDINARY_AMPLITUDES)
    )

    with pytest.raises(ValueError, match="source frequency"):
        _compute_with_source(k=0.86875, lmax=2, x=2.0, source=source)


def test_actual_rwz_kernel_matches_independent_full_m_legacy_reference() -> None:
    k = 0.86875
    wave = IncidentPlaneGW(k, *_ORDINARY_AMPLITUDES)

    def fake_solver(
        sector: Sector,
        ell: int,
        k_value: float,
        background: object,
        boundary_config: object,
    ) -> _FakeRadialSolution:
        del k_value, background, boundary_config
        return _FakeRadialSolution(sector=sector, ell=ell)

    reference = _compute_with_source(
        k=k,
        lmax=2,
        x=2.0,
        source=_IndependentLegacySource(wave, m_values=None),
        radial_solver=fake_solver,
    )
    candidate = _compute_with_source(
        k=k,
        lmax=2,
        x=2.0,
        source=LegacyIncidentSourceAdapter(wave),
        radial_solver=fake_solver,
    )

    _assert_results_exact(reference, candidate)


def test_one_radial_solve_per_sector_and_ell_preserves_incoming_normalization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    solver_calls: list[tuple[Sector, int]] = []
    solutions: dict[tuple[Sector, int], _FakeRadialSolution] = {}
    reconstructed: list[tuple[Sector, int, int, complex, complex]] = []
    source = LegacyScalarRWZAdapter().incident_source(
        2.91875,
        *_ORDINARY_AMPLITUDES,
    )

    def fake_solver(
        sector: Sector,
        ell: int,
        k: float,
        background: object,
        boundary_config: object,
    ) -> _FakeRadialSolution:
        del k, background, boundary_config
        solver_calls.append((sector, ell))
        solution = _FakeRadialSolution(sector=sector, ell=ell)
        solutions[(sector, ell)] = solution
        return solution

    def fake_reconstruct(
        sector: Sector,
        ell: int,
        k: float,
        r: float,
        psi: complex,
        dpsi_dr: complex,
        background: object,
    ) -> tuple[complex, complex]:
        del sector, ell, k, r, background
        return psi, dpsi_dr

    def fake_weyl(
        sector: Sector,
        ell: int,
        m: int,
        k: float,
        r: float,
        theta: float,
        phi: float,
        metric_mode: tuple[complex, complex],
        background: object,
    ) -> WeylModeComponents:
        del background
        psi, dpsi_dr = metric_mode
        reconstructed.append((sector, ell, m, psi, dpsi_dr))
        return _synthetic_mode(
            sector=sector,
            ell=ell,
            m=m,
            coefficient=psi + 0.125j * dpsi_dr,
            k=k,
            r=r,
            theta=theta,
            phi=phi,
        )

    monkeypatch.setattr(partial_wave_module, "reconstruct_metric_mode", fake_reconstruct)
    monkeypatch.setattr(partial_wave_module, "weyl_mode_components", fake_weyl)
    monkeypatch.setattr(
        partial_wave_module,
        "transform_strict_np_weyl_to_incident_tetrad",
        lambda scalars, *, theta, phi: dict(scalars),
    )

    _compute_with_source(
        k=2.91875,
        lmax=4,
        x=15.0,
        source=source,
        radial_solver=fake_solver,
    )

    expected_solver_order = [
        (sector, ell)
        for ell in range(2, 5)
        for sector in (Sector.ODD, Sector.EVEN)
    ]
    assert solver_calls == expected_solver_order
    assert set(solutions) == set(expected_solver_order)
    assert all(solution.psi_radii == solution.dpsi_radii for solution in solutions.values())
    expected_radius = math.hypot(15.0, 30.0)
    assert all(
        solution.psi_radii == [expected_radius]
        and solution.dpsi_radii == [expected_radius]
        for solution in solutions.values()
    )

    expected_modes = [
        (sector, ell, m)
        for ell in range(2, 5)
        for m in (-2, 2)
        for sector in (Sector.ODD, Sector.EVEN)
    ]
    assert [(sector, ell, m) for sector, ell, m, _, _ in reconstructed] == expected_modes
    for sector, ell, m, psi, dpsi_dr in reconstructed:
        solution = solutions[(sector, ell)]
        coefficient = source.coefficient(sector, ell, m)
        scale = coefficient / solution.A_in
        assert psi == scale * solution.psi_value
        assert dpsi_dr == scale * solution.dpsi_value


def test_both_zero_legacy_amplitudes_short_circuit_without_solver() -> None:
    def forbidden_solver(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise AssertionError("both-zero legacy amplitudes must not invoke the solver")

    r, theta, phi = _point_coordinates(25.0)
    result = compute_polarization(
        background=SchwarzschildBackground(M=1.0),
        k=3.89375,
        r=r,
        theta=theta,
        phi=phi,
        A_plus=0.0j,
        A_cross=0.0j,
        lmax=360,
        radial_solver=forbidden_solver,
    )

    assert (
        result.h_plus,
        result.h_cross,
        result.psi0_hat,
        result.psi4_hat,
        result.hddot_plus,
        result.hddot_cross,
    ) == (0.0j,) * 6
    assert result.diagnostics["mode_count"] == 0.0
    assert result.diagnostics["radial_solve_count"] == 0.0


@dataclass
class _FakeRadialSolution:
    sector: Sector
    ell: int
    psi_radii: list[float] = field(default_factory=list)
    dpsi_radii: list[float] = field(default_factory=list)

    @property
    def A_in(self) -> complex:
        parity_offset = 0.125j if self.sector is Sector.ODD else -0.25j
        return complex(1.0 + 0.01 * self.ell) + parity_offset

    @property
    def psi_value(self) -> complex:
        parity_sign = 1.0 if self.sector is Sector.ODD else -1.0
        return complex(parity_sign * self.ell, 0.5)

    @property
    def dpsi_value(self) -> complex:
        parity_sign = 1.0 if self.sector is Sector.ODD else -1.0
        return complex(0.25, parity_sign * self.ell)

    @property
    def diagnostics(self) -> SimpleNamespace:
        return SimpleNamespace(
            boundary_residual=0.0,
            wronskian_residual=0.0,
            match_condition_number=1.0,
        )

    def psi_at(self, r: float) -> complex:
        self.psi_radii.append(float(r))
        return self.psi_value

    def dpsi_dr_at(self, r: float) -> complex:
        self.dpsi_radii.append(float(r))
        return self.dpsi_value
