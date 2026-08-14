from __future__ import annotations

import numpy as np
import pytest

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.scattering import paper_projection
from schwgw.scattering.paper_projection import (
    compute_lhz_eq42_response_columns,
    lhz_eq42_positive_frequency_projection,
)
from schwgw.scattering.partial_wave import StrictNPAssemblyResult
from schwgw.scattering.weyl import StrictNPScalars


def test_eq42_projection_uses_only_strict_psi0_and_psi4() -> None:
    strict = StrictNPScalars(
        psi0=1.0 - 2.0j,
        psi1=30.0 + 40.0j,
        psi2=500.0 - 600.0j,
        psi3=-70.0 + 80.0j,
        psi4=3.0 + 4.0j,
        frame="incident",
    )

    plus, cross = lhz_eq42_positive_frequency_projection(2.0, strict)

    assert plus == -(strict.psi4 + strict.psi0) / 4.0
    assert cross == -1.0j * (strict.psi4 - strict.psi0) / 4.0


def test_response_columns_use_pure_inputs_and_eq46_denominators(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    k = 0.8
    r = 30.0
    theta = 0.2
    phase = np.exp(1.0j * k * r * np.cos(theta))
    A_plus = 0.9 + 1.1j
    A_cross = 0.4 + 0.6j
    expected_plus = 1.2 - 0.3j
    expected_cross = 0.8 + 0.4j
    calls: list[tuple[complex, complex]] = []

    def fake_strict(**kwargs: object) -> StrictNPAssemblyResult:
        plus = complex(kwargs["A_plus"])
        cross = complex(kwargs["A_cross"])
        calls.append((plus, cross))
        if cross == 0.0j:
            psi4 = -(k**2) * plus * phase * expected_plus
        else:
            psi4 = 1.0j * (k**2) * cross * phase * expected_cross
        return StrictNPAssemblyResult(
            scalars=StrictNPScalars(
                psi0=0.0j,
                psi1=1.0j,
                psi2=999.0 + 999.0j,
                psi3=-1.0j,
                psi4=psi4,
                frame="incident",
            ),
            diagnostics={"radial_solve_count": 0.0},
            lmax=int(kwargs["lmax"]),
        )

    monkeypatch.setattr(paper_projection, "compute_strict_np_scalars", fake_strict)
    result = compute_lhz_eq42_response_columns(
        background=SchwarzschildBackground(M=1.0),
        k=k,
        r=r,
        theta=theta,
        phi=0.0,
        A_plus=A_plus,
        A_cross=A_cross,
        lmax=12,
    )

    assert calls == [(A_plus, 0.0j), (0.0j, A_cross)]
    assert result.F_plus == pytest.approx(expected_plus)
    assert result.F_cross == pytest.approx(expected_cross)
    assert result.diagnostics["route_b_used"] is False
    assert result.diagnostics["psi2_used_in_plus_or_cross"] is False
    assert result.diagnostics["physical_claim"] is False
    assert result.diagnostics["observable_bridge_validated"] is False
    assert result.diagnostics["positive_frequency_reality_bridge_validated"] is False
    assert np.isfinite(result.diagnostics["reflection_plane_off_diagonal_relative"])
    assert result.diagnostics["reflection_plane_decoupling_validated"] is False


def test_response_columns_reject_zero_probe_amplitudes() -> None:
    with pytest.raises(ValueError, match="both be nonzero"):
        compute_lhz_eq42_response_columns(
            background=SchwarzschildBackground(M=1.0),
            k=0.5,
            r=30.0,
            theta=0.0,
            phi=0.0,
            A_plus=1.0,
            A_cross=0.0,
            lmax=2,
        )


def test_response_columns_thread_literal_eq35_conjugation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def fake_strict(**kwargs: object) -> StrictNPAssemblyResult:
        calls.append(str(kwargs["q011_z_conjugation"]))
        amplitude = complex(kwargs["A_plus"] or kwargs["A_cross"])
        return StrictNPAssemblyResult(
            scalars=StrictNPScalars(
                amplitude, 0.0j, 0.0j, 0.0j, amplitude, frame="incident"
            ),
            diagnostics={},
            lmax=int(kwargs["lmax"]),
        )

    monkeypatch.setattr(paper_projection, "compute_strict_np_scalars", fake_strict)
    result = compute_lhz_eq42_response_columns(
        background=SchwarzschildBackground(M=1.0),
        k=1.0,
        r=10.0,
        theta=0.2,
        phi=0.0,
        A_plus=1.0 + 0.0j,
        A_cross=1.0 + 0.0j,
        lmax=4,
        q011_z_conjugation="literal_conjugate",
    )

    assert calls == ["literal_conjugate", "literal_conjugate"]
    assert result.diagnostics["radial_source_convention"] == (
        "Li-Hou-Zhao Eq. (35g,h) literal conjugates"
    )
