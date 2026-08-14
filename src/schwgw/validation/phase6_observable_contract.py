"""Zero-science evidence contracts for Phase-6 V1 gates 4--7."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import hashlib
import stat

from schwgw.validation.phase6_polarization_transfer import (
    AbsolutePhaseConvention,
    DEFAULT_INCIDENT_BASIS_LABEL,
    DEFAULT_OBSERVER_BASIS_LABEL,
)

SCHEMA = "schwgw_phase6_v1_observable_contract_v2"
SUPERSEDED_SCHEMA = "schwgw_phase6_v1_observable_contract_v1"
STATES = ("NOT_ASSESSED", "PARTIAL", "PASS", "FAIL")
OBSERVABLES = (
    "master_to_strain_flux",
    "metric_psi4_external_crosscheck",
    "spin2_scattering_limits",
    "finite_radius_tidal_detector",
    "complex_lensing_matrix",
)
NUMERICAL = (
    "r_in",
    "r_out",
    "jost_order",
    "ode_tolerance",
    "arithmetic_precision",
    "backend_difference",
    "lmax_tail",
    "axis_limit",
)
CONVENTION = (
    "observer",
    "worldline",
    "tetrad",
    "polarization_basis",
    "phase_origin",
    "total_scattered_definition",
)


class ObservableContractError(ValueError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_identity(path: str | Path, *, immutable: bool = False) -> dict[str, object]:
    path = Path(path).absolute()
    if any(item.is_symlink() for item in (path, *path.parents)):
        raise ObservableContractError("symlinked evidence path")
    path = path.resolve(strict=True)
    info = path.lstat()
    if (
        not stat.S_ISREG(info.st_mode)
        or info.st_nlink != 1
        or (immutable and stat.S_IMODE(info.st_mode) != 0o444)
    ):
        raise ObservableContractError(
            "evidence file identity is not immutable regular nlink1"
        )
    return {
        "path": str(path),
        "sha256": sha256_bytes(path.read_bytes()),
        "size": info.st_size,
        "mode": stat.S_IMODE(info.st_mode),
        "nlink": info.st_nlink,
    }


def _exact(value: object, fields: set[str], label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != fields:
        raise ObservableContractError(f"{label} schema changed")
    return value


def convention_ledger() -> dict[str, str]:
    phase = AbsolutePhaseConvention()
    return {
        "units": phase.units,
        "signature": "-+++",
        "fourier": phase.fourier,
        "rstar": (f"{phase.tortoise_coordinate}; {phase.tortoise_additive_constant}"),
        "retarded": (f"{phase.retarded_time}; {phase.coordinate_time_origin}"),
        "horizon": "ingoing exp(-i omega r*) for exp(-i omega t)",
        "infinity": "Jost exp(+-i omega r*) with recorded finite order",
        "S": "S_l=-R_l/(-1)^ell; R_l=A_out/A_in",
        "harmonics": "Condon-Shortley; project spin-weighted-harmonic identity",
        "tetrad": (
            "asymptotic strict-NP convention or explicitly bound observer "
            "worldline/tetrad per artifact"
        ),
        "basis": (
            f"incident={DEFAULT_INCIDENT_BASIS_LABEL}; "
            f"observer={DEFAULT_OBSERVER_BASIS_LABEL}; "
            "R(a)=[[cos(2a),sin(2a)],[-sin(2a),cos(2a)]]"
        ),
        "coulomb": (
            f"{phase.coulomb_subtraction}; absolute_phase_sha256={phase.sha256()}"
        ),
        "field_split": phase.field_split,
    }


def superseded_predecessor(project_root: Path) -> dict[str, object]:
    root = (
        project_root / "runs/phase6/v1_observable_contract_v1_20260806"
    ).absolute()
    if (
        root.is_symlink()
        or not root.is_dir()
        or stat.S_IMODE(root.lstat().st_mode) != 0o555
    ):
        raise ObservableContractError("superseded observable root is not immutable")
    return {
        "files": {
            name: file_identity(root / name, immutable=True)
            for name in ("manifest.json", "observable_contract.json")
        },
        "reason": "SUPERSEDED_AFTER_ABSOLUTE_PHASE_AND_BASIS_LEDGER_HARDENING",
        "root": str(root),
        "schema": SUPERSEDED_SCHEMA,
    }


def _component(value: object, *, contract_only: bool) -> None:
    record = _exact(
        value,
        {"state", "reason", "parameter_domain", "raw_result_identities"},
        "component",
    )
    if (
        record["state"] not in STATES
        or not isinstance(record["reason"], str)
        or not record["reason"]
        or not isinstance(record["parameter_domain"], Mapping)
        or not record["parameter_domain"]
        or not isinstance(record["raw_result_identities"], list)
    ):
        raise ObservableContractError("component fields invalid")
    if contract_only and record["state"] != "NOT_ASSESSED":
        raise ObservableContractError("contract-only component cannot claim a result")
    if record["state"] == "PARTIAL" and not record["raw_result_identities"]:
        raise ObservableContractError("PARTIAL requires immutable raw results")
    if record["state"] == "PASS":
        raise ObservableContractError("zero-science validator forbids PASS")


def validate_payload(payload: object, *, contract_only: bool = True) -> None:
    fields = {
        "schema",
        "contract_only",
        "global_green_permitted",
        "certificate_scope",
        "convention_ledger",
        "observables",
        "numerical_budget",
        "convention_budget",
        "source_references",
        "superseded_predecessor",
    }
    item = _exact(payload, fields, "observable contract")
    if (
        item["schema"] != SCHEMA
        or item["contract_only"] is not True
        or item["global_green_permitted"] is not False
        or not isinstance(item["certificate_scope"], str)
        or any(
            word in item["certificate_scope"].lower()
            for word in ("global", "project", "schwo")
        )
        or item["convention_ledger"] != convention_ledger()
    ):
        raise ObservableContractError("contract scope/convention ledger drift")
    predecessor = _exact(
        item["superseded_predecessor"],
        {"files", "reason", "root", "schema"},
        "superseded predecessor",
    )
    expected_predecessor = superseded_predecessor(
        Path(__file__).resolve().parents[3]
    )
    if predecessor != expected_predecessor:
        raise ObservableContractError("superseded predecessor identity drift")
    for group, names in (
        ("observables", OBSERVABLES),
        ("numerical_budget", NUMERICAL),
        ("convention_budget", CONVENTION),
    ):
        records = item[group]
        if not isinstance(records, Mapping) or set(records) != set(names):
            raise ObservableContractError(f"{group} inventory changed")
        for record in records.values():
            _component(record, contract_only=contract_only)
    refs = item["source_references"]
    if not isinstance(refs, Mapping) or set(refs) != {
        "martel_poisson_pdf",
        "third_audit",
    }:
        raise ObservableContractError("source reference inventory changed")
    for identity in refs.values():
        if file_identity(identity["path"]) != identity:
            raise ObservableContractError("source reference identity drift")


def zero_payload(project_root: Path) -> dict[str, object]:
    def component() -> dict[str, object]:
        return {
            "state": "NOT_ASSESSED",
            "reason": "zero-science contract-only fixture",
            "parameter_domain": {"status": "future explicit mode-key domain required"},
            "raw_result_identities": [],
        }

    return {
        "schema": SCHEMA,
        "contract_only": True,
        "global_green_permitted": False,
        "certificate_scope": "per-observable explicit parameter-domain only",
        "convention_ledger": convention_ledger(),
        "observables": {name: component() for name in OBSERVABLES},
        "numerical_budget": {name: component() for name in NUMERICAL},
        "convention_budget": {name: component() for name in CONVENTION},
        "superseded_predecessor": superseded_predecessor(project_root),
        "source_references": {
            "martel_poisson_pdf": file_identity(
                project_root
                / "references/papers/Gravitational perturbations of the Schwarzschild spacetime.pdf"
            ),
            "third_audit": file_identity(
                project_root / "audits/SchWO_physical_validation_audit_20260806.md"
            ),
        },
    }
