"""Machine-readable Phase-6 validity and uncertainty contracts.

The contracts intentionally prohibit a project-wide status.  A certificate is
valid only for one named observable on one explicit parameter domain, and it
keeps numerical uncertainty separate from convention/observable spread.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from types import MappingProxyType
from typing import Mapping


_CERTIFICATE_STATUSES = frozenset({"GREEN", "YELLOW", "RED", "NOT_ASSESSED"})
_FORBIDDEN_OBSERVABLES = frozenset({"global", "project", "schwo"})


def _nonnegative_finite(value: float, *, name: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number < 0.0:
        raise ValueError(f"{name} must be finite and nonnegative.")
    return number


def _required_text(value: str, *, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string.")
    return value


@dataclass(frozen=True)
class NumericalUncertaintyBudget:
    """Numerical error components for one accepted observable."""

    lmax: float
    r_in: float
    r_out: float
    jost_order: float
    ode_tolerance: float
    arithmetic_precision: float
    axis_limit: float
    backend_difference: float

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            object.__setattr__(
                self,
                name,
                _nonnegative_finite(getattr(self, name), name=name),
            )

    def to_metadata(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class ConventionUncertaintyBudget:
    """Convention/observable spread, kept distinct from numerical error."""

    observer: float
    tetrad: float
    polarization_basis: float
    phase_origin: float
    total_scattered_definition: float

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            object.__setattr__(
                self,
                name,
                _nonnegative_finite(getattr(self, name), name=name),
            )

    def to_metadata(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class ObservableValidityCertificate:
    """Per-observable, per-domain Phase-6 acceptance certificate."""

    observable: str
    parameter_domain: Mapping[str, object]
    status: str
    numerical_uncertainty: NumericalUncertaintyBudget
    convention_uncertainty: ConventionUncertaintyBudget
    acceptance_gate: str
    evidence: tuple[str, ...]
    limitations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        observable = _required_text(self.observable, name="observable")
        if observable.strip().lower() in _FORBIDDEN_OBSERVABLES:
            raise ValueError("Phase 6 forbids project-wide/global certificates.")
        if self.status not in _CERTIFICATE_STATUSES:
            raise ValueError(
                "status must be GREEN, YELLOW, RED, or NOT_ASSESSED."
            )
        if not isinstance(self.numerical_uncertainty, NumericalUncertaintyBudget):
            raise TypeError("numerical_uncertainty has the wrong type.")
        if not isinstance(self.convention_uncertainty, ConventionUncertaintyBudget):
            raise TypeError("convention_uncertainty has the wrong type.")
        domain = dict(self.parameter_domain)
        if not domain:
            raise ValueError("parameter_domain must be explicit and non-empty.")
        evidence = tuple(_required_text(item, name="evidence item") for item in self.evidence)
        if self.status == "GREEN" and not evidence:
            raise ValueError("GREEN requires at least one evidence identity.")
        object.__setattr__(self, "observable", observable)
        object.__setattr__(self, "parameter_domain", MappingProxyType(domain))
        object.__setattr__(
            self,
            "acceptance_gate",
            _required_text(self.acceptance_gate, name="acceptance_gate"),
        )
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(
            self,
            "limitations",
            tuple(_required_text(item, name="limitation") for item in self.limitations),
        )

    def to_metadata(self) -> dict[str, object]:
        return {
            "schema_version": "schwgw_phase6_observable_validity_v1",
            "observable": self.observable,
            "parameter_domain": dict(self.parameter_domain),
            "status": self.status,
            "acceptance_gate": self.acceptance_gate,
            "numerical_uncertainty": self.numerical_uncertainty.to_metadata(),
            "convention_uncertainty": self.convention_uncertainty.to_metadata(),
            "evidence": list(self.evidence),
            "limitations": list(self.limitations),
            "global_green_permitted": False,
        }


def legacy_np_diagnostic_metadata() -> dict[str, object]:
    """Claim metadata for the isolated legacy lower-NP/pseudoinverse path."""

    return {
        "quantity_kind": "legacy_finite_radius_polarization_diagnostic",
        "polarization_bridge": "legacy strict-NP lower-scalar completion",
        "polarization_bridge_implementation": (
            "legacy full-NP pseudoinverse tidal projection (diagnostic-only)"
        ),
        "polarization_bridge_validated": False,
        "positive_frequency_reality_bridge_validated": False,
        "legacy_diagnostic": True,
        "production_observable": False,
        "physical_claim": False,
        "physical_claim_scope": "no operational finite-radius waveform claim",
    }


def unspecified_polarization_solver_metadata() -> dict[str, object]:
    """Fail-closed metadata for injected solvers with no declared bridge."""

    return {
        "quantity_kind": "caller_supplied_polarization_output",
        "polarization_bridge": "unspecified caller-supplied solver",
        "polarization_bridge_implementation": "not declared by solver",
        "polarization_bridge_validated": False,
        "positive_frequency_reality_bridge_validated": False,
        "legacy_diagnostic": False,
        "production_observable": False,
        "physical_claim": False,
        "physical_claim_scope": "unvalidated until the solver declares its bridge",
    }


def finite_radius_tidal_response_metadata(
    *,
    observer_worldline: str,
    tetrad: str,
    polarization_basis: str,
    phase_origin: str,
    axis_regularization: str,
    production_backend: str,
) -> dict[str, object]:
    """Qualified metadata for the direct metric-curvature tidal response."""

    return {
        "quantity_kind": "finite_radius_observer_qualified_tidal_response",
        "primary_observable": "electric_tidal_tensor_E_ij",
        "derived_observable": "monochromatic_equivalent_tidal_strain",
        "gauge": "Regge-Wheeler",
        "observer_worldline": _required_text(
            observer_worldline, name="observer_worldline"
        ),
        "tetrad": _required_text(tetrad, name="tetrad"),
        "polarization_basis": _required_text(
            polarization_basis, name="polarization_basis"
        ),
        "phase_origin": _required_text(phase_origin, name="phase_origin"),
        "axis_regularization": _required_text(
            axis_regularization, name="axis_regularization"
        ),
        "production_backend": _required_text(
            production_backend, name="production_backend"
        ),
        "physical_claim": False,
        "physical_claim_scope": (
            "RW-gauge, chosen-observer equivalent tidal strain; operational "
            "detector response not yet gauge-validated"
        ),
    }
