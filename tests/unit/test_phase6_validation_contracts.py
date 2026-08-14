from __future__ import annotations

from types import SimpleNamespace

import pytest

from schwgw.scattering.legacy import (
    LEGACY_EVEN_CHANNEL,
    LEGACY_ODD_CHANNEL,
    LegacyScalarRWZAdapter,
)
from schwgw.scattering.radial_validation import radial_flux_budget
from schwgw.validation import (
    ConventionUncertaintyBudget,
    NumericalUncertaintyBudget,
    ObservableValidityCertificate,
    finite_radius_tidal_response_metadata,
    legacy_np_diagnostic_metadata,
)


def _numerical() -> NumericalUncertaintyBudget:
    return NumericalUncertaintyBudget(
        lmax=1e-6,
        r_in=2e-7,
        r_out=3e-6,
        jost_order=4e-8,
        ode_tolerance=5e-9,
        arithmetic_precision=6e-12,
        axis_limit=7e-5,
        backend_difference=8e-4,
    )


def _convention() -> ConventionUncertaintyBudget:
    return ConventionUncertaintyBudget(
        observer=0.1,
        tetrad=0.02,
        polarization_basis=0.0,
        phase_origin=0.4,
        total_scattered_definition=0.03,
    )


def test_certificate_separates_uncertainty_budgets_and_forbids_global_green() -> None:
    certificate = ObservableValidityCertificate(
        observable="odd_radial_S_matrix",
        parameter_domain={"kM": [0.5, 1.0], "ell": [20, 40]},
        status="GREEN",
        numerical_uncertainty=_numerical(),
        convention_uncertainty=_convention(),
        acceptance_gate="V1",
        evidence=("sha256:example",),
        limitations=("even sector excluded",),
    )
    metadata = certificate.to_metadata()
    assert metadata["global_green_permitted"] is False
    assert metadata["numerical_uncertainty"]["backend_difference"] == 8e-4
    assert metadata["convention_uncertainty"]["phase_origin"] == 0.4

    with pytest.raises(ValueError, match="global"):
        ObservableValidityCertificate(
            observable="global",
            parameter_domain={"all": True},
            status="GREEN",
            numerical_uncertainty=_numerical(),
            convention_uncertainty=_convention(),
            acceptance_gate="V6",
            evidence=("sha256:example",),
        )


def test_legacy_paths_are_diagnostic_only() -> None:
    assert LEGACY_ODD_CHANNEL.physical_claim is False
    assert LEGACY_EVEN_CHANNEL.physical_claim is False
    assert LegacyScalarRWZAdapter().physical_claim is False
    metadata = legacy_np_diagnostic_metadata()
    assert metadata["legacy_diagnostic"] is True
    assert metadata["production_observable"] is False
    assert metadata["physical_claim"] is False


def test_finite_radius_claim_is_observer_and_gauge_qualified() -> None:
    metadata = finite_radius_tidal_response_metadata(
        observer_worldline="static Schwarzschild observer at fixed r,theta,phi",
        tetrad="static orthonormal tetrad",
        polarization_basis="incident-aligned transverse x/y basis",
        phase_origin="r_star=r+2M log(r/2M-1), t=0 incident baseline",
        axis_regularization="theta ladder with extrapolated axis limit",
        production_backend="direct RW metric to linearized Riemann",
    )
    assert metadata["primary_observable"] == "electric_tidal_tensor_E_ij"
    assert metadata["physical_claim"] is False
    assert "chosen-observer" in metadata["physical_claim_scope"]


def test_radial_flux_budget_uses_incident_normalization_and_horizon_flux() -> None:
    solution = SimpleNamespace(
        k=0.5,
        A_in=2.0 + 0.0j,
        A_out=1.0 + 0.0j,
        diagnostics=SimpleNamespace(
            expected_flux_scale=3.0,
            flux_residual=2e-10,
            solver="synthetic-independent-accounting",
        ),
    )
    budget = radial_flux_budget(solution)
    assert budget.reflection == pytest.approx(0.25)
    assert budget.horizon_transmission == pytest.approx(0.75)
    assert budget.balance_residual == pytest.approx(0.0)
    assert budget.independently_validated is False
