"""Phase-6 V1 production finite-radius radial-state validation primitives.

This gate is deliberately separate from paper-figure rendering.  It binds the
exact frozen ``D_prod`` inventory and the eight Cartesian Table-I sites, then
evaluates one generic conditioned radial trajectory per mode.  The result is
radial master-field evidence only: no observer, tetrad, detector response, or
infinity-waveform claim is made here.

The generic outer selector and conditioned backend are shared with the Phase-6
conditioning scan.  Legacy paper envelopes, Newman--Penrose shortcuts, and
pseudoinverse matching are prohibited by the result validator.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import stat
from typing import Protocol

import numpy as np

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.numerics.conditioned_radial import (
    ConditionedFiniteRadiusState,
    ConditionedRadialRequest,
    ConditionedRadialResult,
    solve_conditioned_radial_at_radius,
)
from schwgw.perturbations import Sector
from schwgw.validation.phase6_conditioning_scan import (
    DEFAULT_POLICY as DEFAULT_CONDITIONING_POLICY,
    OuterSelection,
    select_outer_boundary,
)
from schwgw.validation.phase6_domain import (
    EXPECTED_PRODUCTION_KM,
    RadialKey,
    canonical_json_bytes,
    jsonl_bytes,
    read_jsonl_keys,
    sha256_bytes,
    source_file_identity,
    validate_ordered_unique_keys,
)
from schwgw.validation.phase6_execution_contract import (
    CONVENTION_BUDGET_FIELDS,
    NUMERICAL_BUDGET_FIELDS,
    finite_response_radii_from_source,
)


POLICY_SCHEMA = "schwgw_phase6_production_finite_radius_policy_v1"
SOLVER_PAYLOAD_SCHEMA = "schwgw_phase6_production_finite_radius_payload_v1"
RUN_CONTRACT_SCHEMA = "schwgw_phase6_production_finite_radius_shard_contract_v1"
KEY_TERMINAL_SCHEMA = "schwgw_phase6_production_finite_radius_terminal_v1"
SHARD_RESULT_SCHEMA = "schwgw_phase6_production_finite_radius_shard_result_v1"
SHARD_FAILURE_SCHEMA = "schwgw_phase6_production_finite_radius_failure_v1"
MANIFEST_SCHEMA = "schwgw_phase6_production_finite_radius_manifest_v1"

EXPECTED_DOMAIN_IDENTITIES = {
    "D_prod.jsonl": "54f13ea2473fb0a04ca5e16277edae31335c03b11753973d83a934cce2f0872b",
    "domain_contract.json": "7ed99b905c3a1301d96101f357ab1fd9f4bc6e9a4922cb242d28e7cf06bb3bcf",
    "manifest.json": "f11d127e0bcfafa8f2fe24b2d3cec3e0cedc60f644d4285e6d52e53d8358d2d2",
}
EXPECTED_EXECUTION_IDENTITIES = {
    "execution_contract.json": "25ad4b4e723edbd44651edaa63df415141de504b85288b12c2a6a973fcb420ab",
    "shard_inventory.jsonl": "b652ceb41d0dfa3c25f10d246e98bc707721faf4d83b049b3410dc4ca0b4efff",
    "manifest.json": "1de9d445d888cbb5ddbf426cc062d2fb5128cad111437ce7d147df6e004aed48",
}
EXPECTED_COORDINATE_SOURCE_SHA256 = (
    "76b0a3d3d3ffd44def8466e18ddcba4fe097d899e12980f988cc0e038cfef6a9"
)
EXPECTED_TABLE_I_X_M = (0.0, 1.0, 2.0, 3.0, 10.0, 15.0, 20.0, 25.0)
EXPECTED_TABLE_I_Y_M = (0.0,) * 8
EXPECTED_TABLE_I_Z_M = (30.0,) * 8
EXPECTED_TABLE_I_POINT_IDS = (
    "near_axis_x0_z30",
    "near_axis_x1_z30",
    "near_axis_x2_z30",
    "near_axis_x3_z30",
    "far_axis_x10_z30",
    "far_axis_x15_z30",
    "far_axis_x20_z30",
    "far_axis_x25_z30",
)
UNASSESSED_FINITE_BUDGET = float(np.finfo(float).max)
STATUS_VOCABULARY = frozenset({"NOT_ASSESSED", "PARTIAL", "PASS", "FAIL"})


class ProductionFiniteRadiusError(ValueError):
    """Raised when frozen inputs, requests, or radial outputs fail closed."""


class ConditionedSolver(Protocol):
    def __call__(
        self,
        request: ConditionedRadialRequest,
        background: SchwarzschildBackground,
    ) -> ConditionedRadialResult: ...


OuterSelector = Callable[[RadialKey], OuterSelection]


@dataclass(frozen=True)
class TableISite:
    ordinal: int
    point_id: str
    x_M: float
    y_M: float
    z_M: float
    radius_M_decimal: str

    @property
    def radius_M(self) -> float:
        return float(self.radius_M_decimal)

    def to_record(self) -> dict[str, object]:
        return {
            "ordinal": self.ordinal,
            "point_id": self.point_id,
            "radius_M_decimal": self.radius_M_decimal,
            "x_M": self.x_M,
            "y_M": self.y_M,
            "z_M": self.z_M,
        }


@dataclass(frozen=True)
class ProductionFiniteRadiusPolicy:
    """Frozen one-trajectory policy for the eight production radii."""

    r_in_eps: float = 1.0e-6
    rtol: float = 1.0e-10
    atol: float = 1.0e-12
    outer_series_order: int = 160
    maximum_flux_residual: float = 1.0e-6

    def __post_init__(self) -> None:
        if any(
            not math.isfinite(value) or value <= 0.0
            for value in (
                self.r_in_eps,
                self.rtol,
                self.atol,
                self.maximum_flux_residual,
            )
        ):
            raise ProductionFiniteRadiusError("policy contains a nonpositive value")
        if self.atol >= self.rtol:
            raise ProductionFiniteRadiusError("policy requires atol < rtol")
        if (
            isinstance(self.outer_series_order, bool)
            or not isinstance(self.outer_series_order, int)
            or not 2 <= self.outer_series_order <= 256
        ):
            raise ProductionFiniteRadiusError(
                "outer_series_order must be an integer in [2, 256]"
            )

    def to_record(self) -> dict[str, object]:
        return {
            "backend": {
                "atol": self.atol,
                "integration_method": "DOP853",
                "outer_basis": "jost_1_over_r",
                "outer_series_order": self.outer_series_order,
                "r_in_eps": self.r_in_eps,
                "rtol": self.rtol,
            },
            "generic_outer_selection_policy": (DEFAULT_CONDITIONING_POLICY.to_record()),
            "generic_outer_selection_policy_sha256": (
                DEFAULT_CONDITIONING_POLICY.sha256
            ),
            "maximum_flux_residual": self.maximum_flux_residual,
            "one_conditioned_trajectory_per_mode": True,
            "paper_specific_envelope_permitted": False,
            "schema": POLICY_SCHEMA,
        }

    @property
    def sha256(self) -> str:
        return sha256_bytes(canonical_json_bytes(self.to_record()))


DEFAULT_POLICY = ProductionFiniteRadiusPolicy()


@dataclass(frozen=True)
class FrozenProductionContract:
    domain_root: Path
    execution_root: Path
    production_keys: tuple[RadialKey, ...]
    shard_records: tuple[Mapping[str, object], ...]
    sites: tuple[TableISite, ...]
    domain_identities: Mapping[str, Mapping[str, object]]
    execution_identities: Mapping[str, Mapping[str, object]]
    coordinate_source_identity: Mapping[str, object]

    def shard_record(self, shard_id: str) -> Mapping[str, object]:
        matches = [item for item in self.shard_records if item["shard_id"] == shard_id]
        if len(matches) != 1:
            raise ProductionFiniteRadiusError(
                f"unknown or duplicate production shard: {shard_id}"
            )
        return matches[0]

    def shard_keys(self, shard_id: str) -> tuple[RadialKey, ...]:
        record = self.shard_record(shard_id)
        keys = tuple(
            key
            for key in self.production_keys
            if key.kM == record["kM"] and key.sector == record["sector"]
        )
        validate_ordered_unique_keys(keys)
        if (
            len(keys) != record["key_count"]
            or sha256_bytes(jsonl_bytes(keys)) != record["key_list_sha256"]
        ):
            raise ProductionFiniteRadiusError("production shard identity changed")
        return keys


def _strict_json(path: Path) -> Mapping[str, object]:
    try:
        raw = path.read_bytes()
        value = json.loads(
            raw,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON constant: {token}")
            ),
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise ProductionFiniteRadiusError(f"cannot parse frozen JSON: {path}") from exc
    if not isinstance(value, Mapping) or raw != canonical_json_bytes(value):
        raise ProductionFiniteRadiusError(f"frozen JSON is not canonical: {path}")
    return value


def _strict_jsonl_records(path: Path) -> tuple[Mapping[str, object], ...]:
    try:
        lines = path.read_bytes().splitlines()
    except OSError as exc:
        raise ProductionFiniteRadiusError(f"cannot read frozen JSONL: {path}") from exc
    records: list[Mapping[str, object]] = []
    for line in lines:
        try:
            value = json.loads(
                line,
                parse_constant=lambda token: (_ for _ in ()).throw(
                    ValueError(f"non-finite JSON constant: {token}")
                ),
            )
        except (ValueError, json.JSONDecodeError) as exc:
            raise ProductionFiniteRadiusError(
                f"cannot parse frozen JSONL: {path}"
            ) from exc
        if (
            not isinstance(value, Mapping)
            or canonical_json_bytes(value).rstrip(b"\n") != line
        ):
            raise ProductionFiniteRadiusError(f"frozen JSONL is not canonical: {path}")
        records.append(value)
    return tuple(records)


def _verified_identities(
    root: Path,
    expected: Mapping[str, str],
) -> dict[str, Mapping[str, object]]:
    if (
        root.is_symlink()
        or not root.is_dir()
        or root.resolve(strict=True) != root
        or stat.S_IMODE(root.stat().st_mode) != 0o555
    ):
        raise ProductionFiniteRadiusError(
            f"frozen root is not direct immutable: {root}"
        )
    identities: dict[str, Mapping[str, object]] = {}
    for filename, digest in expected.items():
        path = root / filename
        identity = source_file_identity(path)
        if (
            identity["sha256"] != digest
            or identity["mode"] != 0o444
            or identity["nlink"] != 1
        ):
            raise ProductionFiniteRadiusError(f"frozen input identity changed: {path}")
        identities[filename] = identity
    return identities


def _table_i_sites(
    execution_contract: Mapping[str, object],
) -> tuple[tuple[TableISite, ...], Mapping[str, object]]:
    try:
        response = execution_contract["generic_transition_calibration"]
        construction = response["construction"]  # type: ignore[index]
        source_record = construction["response_radius_source"]  # type: ignore[index]
        radius_texts = tuple(source_record["radii_M"])  # type: ignore[index]
        frozen_identity = source_record["source_identity"]  # type: ignore[index]
    except (KeyError, TypeError) as exc:
        raise ProductionFiniteRadiusError(
            "finite-response source binding is malformed"
        ) from exc
    if (
        len(radius_texts) != 8
        or not all(isinstance(value, str) for value in radius_texts)
        or not isinstance(frozen_identity, Mapping)
        or set(frozen_identity) != {"mode", "nlink", "path", "sha256", "size"}
        or frozen_identity.get("sha256") != EXPECTED_COORDINATE_SOURCE_SHA256
    ):
        raise ProductionFiniteRadiusError("finite-response source identity changed")
    coordinate_source = Path(str(frozen_identity["path"]))
    actual_identity = source_file_identity(coordinate_source)
    if actual_identity != dict(frozen_identity):
        raise ProductionFiniteRadiusError("finite-response coordinate bytes changed")
    derived_radii = finite_response_radii_from_source(coordinate_source)
    try:
        bound_radii = tuple(Decimal(value) for value in radius_texts)
    except Exception as exc:
        raise ProductionFiniteRadiusError(
            "finite-response radius text changed"
        ) from exc
    if derived_radii != bound_radii:
        raise ProductionFiniteRadiusError("finite-response radii changed")
    try:
        with np.load(coordinate_source, allow_pickle=False) as data:
            point_ids = tuple(str(value) for value in data["point_ids"])
            x_values = tuple(float(value) for value in data["point_x"])
            y_values = tuple(float(value) for value in data["point_y"])
            z_values = tuple(float(value) for value in data["point_z"])
            stored_radii = tuple(float(value) for value in data["point_r"])
    except (OSError, KeyError, ValueError) as exc:
        raise ProductionFiniteRadiusError(
            "cannot reload Table-I coordinate arrays"
        ) from exc
    if (
        point_ids != EXPECTED_TABLE_I_POINT_IDS
        or x_values != EXPECTED_TABLE_I_X_M
        or y_values != EXPECTED_TABLE_I_Y_M
        or z_values != EXPECTED_TABLE_I_Z_M
        or stored_radii != tuple(float(value) for value in radius_texts)
    ):
        raise ProductionFiniteRadiusError("Table-I site inventory changed")
    sites = tuple(
        TableISite(
            ordinal=index,
            point_id=point_ids[index],
            x_M=x_values[index],
            y_M=y_values[index],
            z_M=z_values[index],
            radius_M_decimal=radius_texts[index],
        )
        for index in range(8)
    )
    if (
        tuple(sorted(site.radius_M for site in sites))
        != tuple(site.radius_M for site in sites)
        or len({site.radius_M for site in sites}) != 8
    ):
        raise ProductionFiniteRadiusError("Table-I radii must be unique and increasing")
    return sites, actual_identity


def load_frozen_production_contract(
    domain_root: str | Path,
    execution_root: str | Path,
) -> FrozenProductionContract:
    """Bind the exact 16,048-key, 40-frequency, 80-shard production domain."""

    domain = Path(domain_root).resolve(strict=True)
    execution = Path(execution_root).resolve(strict=True)
    domain_identities = _verified_identities(domain, EXPECTED_DOMAIN_IDENTITIES)
    execution_identities = _verified_identities(
        execution, EXPECTED_EXECUTION_IDENTITIES
    )
    production_keys = read_jsonl_keys(domain / "D_prod.jsonl")
    validate_ordered_unique_keys(production_keys)
    domain_contract = _strict_json(domain / "domain_contract.json")
    execution_contract = _strict_json(execution / "execution_contract.json")
    all_shards = _strict_jsonl_records(execution / "shard_inventory.jsonl")
    if (
        len(production_keys) != 16_048
        or len({key.kM for key in production_keys}) != 40
        or tuple(sorted({key.kM for key in production_keys}, key=Decimal))
        != EXPECTED_PRODUCTION_KM
    ):
        raise ProductionFiniteRadiusError("frozen production cardinality changed")
    if (
        domain_contract.get("schema") != "schwgw_phase6_v1_domain_contract_v1"
        or domain_contract.get("global_green_permitted") is not False
        or execution_contract.get("schema") != "schwgw_phase6_v1_execution_contract_v1"
    ):
        raise ProductionFiniteRadiusError("frozen contract schema/state changed")
    domain_acceptance = execution_contract.get("domain_acceptance")
    if (
        not isinstance(domain_acceptance, Mapping)
        or domain_acceptance.get("global_green_permitted") is not False
        or domain_acceptance.get("paper_agreement_gate") != "PROHIBITED"
    ):
        raise ProductionFiniteRadiusError("execution acceptance boundary changed")
    shard_contract = execution_contract.get("shard_inventory")
    if (
        len(all_shards) != 86
        or not isinstance(shard_contract, Mapping)
        or shard_contract.get("count") != 86
        or shard_contract.get("records") != list(all_shards)
    ):
        raise ProductionFiniteRadiusError("frozen shard inventory changed")
    production_shards = tuple(
        record for record in all_shards if record.get("production_key_count", 0) != 0
    )
    if len(production_shards) != 80:
        raise ProductionFiniteRadiusError(
            "D_prod must partition into exactly 80 frequency-sector shards"
        )
    result = FrozenProductionContract(
        domain_root=domain,
        execution_root=execution,
        production_keys=production_keys,
        shard_records=production_shards,
        sites=(),
        domain_identities=domain_identities,
        execution_identities=execution_identities,
        coordinate_source_identity={},
    )
    flattened: list[RadialKey] = []
    for record in production_shards:
        if (
            set(record)
            != {
                "extension_key_count",
                "kM",
                "key_count",
                "key_list_sha256",
                "production_key_count",
                "sector",
                "shard_id",
            }
            or record["extension_key_count"] != 0
            or record["production_key_count"] != record["key_count"]
        ):
            raise ProductionFiniteRadiusError("production shard schema changed")
        flattened.extend(result.shard_keys(str(record["shard_id"])))
    if tuple(flattened) != production_keys:
        raise ProductionFiniteRadiusError("80-shard union differs from D_prod")
    sites, coordinate_identity = _table_i_sites(execution_contract)
    return FrozenProductionContract(
        domain_root=domain,
        execution_root=execution,
        production_keys=production_keys,
        shard_records=production_shards,
        sites=sites,
        domain_identities=domain_identities,
        execution_identities=execution_identities,
        coordinate_source_identity=coordinate_identity,
    )


def _finite_float(value: object, label: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ProductionFiniteRadiusError(f"invalid numeric value: {label}") from exc
    if not math.isfinite(parsed):
        raise ProductionFiniteRadiusError(f"non-finite numeric value: {label}")
    return parsed


def _complex_record(value: complex) -> dict[str, str]:
    parsed = complex(value)
    magnitude = abs(parsed)
    if not all(math.isfinite(item) for item in (parsed.real, parsed.imag, magnitude)):
        raise ProductionFiniteRadiusError("non-finite complex radial value")
    return {
        "abs": format(magnitude, ".17g"),
        "imag": format(parsed.imag, ".17g"),
        "real": format(parsed.real, ".17g"),
    }


def _state_record(
    state: ConditionedFiniteRadiusState,
    site: TableISite,
) -> dict[str, object]:
    if state.radius != site.radius_M:
        raise ProductionFiniteRadiusError("finite-radius state/site mismatch")
    if state.complex_state_status not in {"FINITE_COMPLEX", "LOG_SCALED_UNDERFLOW"}:
        raise ProductionFiniteRadiusError("unknown complex-state status")
    if state.complex_derivative_status not in {
        "FINITE_COMPLEX",
        "LOG_SCALED_UNDERFLOW",
    }:
        raise ProductionFiniteRadiusError("unknown derivative-state status")
    return {
        "complex_derivative_status": state.complex_derivative_status,
        "complex_state_status": state.complex_state_status,
        "dpsi_dr": _complex_record(state.dpsi_dr),
        "log_abs_dpsi_dr": _finite_float(state.log_abs_dpsi_dr, "log_abs_dpsi_dr"),
        "log_abs_psi": _finite_float(state.log_abs_psi, "log_abs_psi"),
        "phase_dpsi_dr": _finite_float(state.phase_dpsi_dr, "phase_dpsi_dr"),
        "phase_psi": _finite_float(state.phase_psi, "phase_psi"),
        "psi": _complex_record(state.psi),
        "site": site.to_record(),
    }


def _provenance_is_generic(diagnostics: Mapping[str, object]) -> None:
    if diagnostics.get("paper_specific_envelope_used") is not False:
        raise ProductionFiniteRadiusError("paper-specific envelope provenance found")
    forbidden_flags = {
        "legacy",
        "newman_penrose",
        "np",
        "np_path",
        "pseudoinverse",
    }
    if any(diagnostics.get(name) not in {None, False} for name in forbidden_flags):
        raise ProductionFiniteRadiusError("forbidden radial provenance flag found")
    text = " ".join(
        str(diagnostics.get(name, "")).lower()
        for name in (
            "algorithm",
            "backend",
            "method",
            "normalization_definition",
            "provenance",
        )
    )
    if any(
        token in text
        for token in (
            "legacy",
            "newman-penrose",
            "newman_penrose",
            "pseudoinverse",
        )
    ):
        raise ProductionFiniteRadiusError("forbidden radial provenance text found")


def _budgets(
    *,
    numerical_status: str,
    convention_status: str,
) -> tuple[dict[str, object], dict[str, object]]:
    if numerical_status not in {"PARTIAL", "FAIL"}:
        raise ProductionFiniteRadiusError("invalid numerical budget status")
    if convention_status not in {"PARTIAL", "FAIL"}:
        raise ProductionFiniteRadiusError("invalid convention budget status")
    numerical_components = {
        name: UNASSESSED_FINITE_BUDGET for name in NUMERICAL_BUDGET_FIELDS
    }
    numerical_component_statuses = {
        name: "NOT_ASSESSED" for name in NUMERICAL_BUDGET_FIELDS
    }
    numerical_components["arithmetic_precision"] = float(np.finfo(float).eps)
    numerical_component_statuses["arithmetic_precision"] = "PARTIAL"
    convention_components = {
        name: UNASSESSED_FINITE_BUDGET for name in CONVENTION_BUDGET_FIELDS
    }
    convention_component_statuses = {
        name: "NOT_ASSESSED" for name in CONVENTION_BUDGET_FIELDS
    }
    return (
        {
            "component_statuses": numerical_component_statuses,
            "components": numerical_components,
            "status": numerical_status,
        },
        {
            "component_statuses": convention_component_statuses,
            "components": convention_components,
            "status": convention_status,
        },
    )


def _failed_payload(
    key: RadialKey,
    selection: OuterSelection,
    sites: Sequence[TableISite],
    policy: ProductionFiniteRadiusPolicy,
    *,
    reason: str,
    solver_call_count: int,
) -> dict[str, object]:
    numerical, convention = _budgets(numerical_status="FAIL", convention_status="FAIL")
    return {
        "acceptance_state": "FAIL",
        "actual_precision": {
            "backend": "scipy_float64_conditioned_radial_v1",
            "digits": 16,
        },
        "convention_budget": convention,
        "failures": {"production_finite_radius": reason},
        "key": key.to_record(),
        "numerical_budget": numerical,
        "observable_statuses": {
            "convention_closure": "NOT_ASSESSED",
            "detector_response": "NOT_ASSESSED",
            "flux_conservation": "FAIL",
            "infinity_waveform": "NOT_ASSESSED",
            "observer_qualified_tidal_response": "NOT_ASSESSED",
            "production_eight_radius_radial_states": "FAIL",
            "radial_s_matrix": "FAIL",
        },
        "outer_selection": selection.to_record(),
        "policy_sha256": policy.sha256,
        "provenance": {"legacy": False, "np": False, "pseudoinverse": False},
        "result": None,
        "schema": SOLVER_PAYLOAD_SCHEMA,
        "scope_qualification": {
            "finite_radius_outputs_are_observer_qualified": False,
            "full_paper_figure_rerun": False,
            "infinity_waveform_claim": False,
            "radial_master_field_states_only": True,
        },
        "solver_call_count": solver_call_count,
        "table_i_sites": [site.to_record() for site in sites],
    }


def execute_production_finite_radius_key(
    key: RadialKey,
    selection: OuterSelection,
    sites: Sequence[TableISite],
    *,
    policy: ProductionFiniteRadiusPolicy = DEFAULT_POLICY,
    solver: ConditionedSolver = solve_conditioned_radial_at_radius,
    background: SchwarzschildBackground | None = None,
) -> dict[str, object]:
    """Evaluate all eight radii in exactly one generic conditioned solve."""

    if not isinstance(key, RadialKey) or selection.key != key:
        raise ProductionFiniteRadiusError("outer selection belongs to another key")
    exact_sites = tuple(sites)
    if (
        len(exact_sites) != 8
        or tuple(site.ordinal for site in exact_sites) != tuple(range(8))
        or tuple(site.x_M for site in exact_sites) != EXPECTED_TABLE_I_X_M
        or tuple(site.z_M for site in exact_sites) != EXPECTED_TABLE_I_Z_M
    ):
        raise ProductionFiniteRadiusError("eight-site production inventory changed")
    if not selection.supported or selection.selected_r_out_M is None:
        return _failed_payload(
            key,
            selection,
            exact_sites,
            policy,
            reason=selection.blocker or "NO_FROZEN_R_OUT_NODE_PASSES_ALL_RAW_GATES",
            solver_call_count=0,
        )
    production_outer_segments = math.ceil(
        (selection.selected_r_out_M - exact_sites[0].radius_M)
        / DEFAULT_CONDITIONING_POLICY.outer_segment_width_M
    )
    if (
        production_outer_segments
        > DEFAULT_CONDITIONING_POLICY.maximum_estimated_outer_segments
    ):
        return _failed_payload(
            key,
            selection,
            exact_sites,
            policy,
            reason="PRODUCTION_OUTER_SEGMENT_CAP",
            solver_call_count=0,
        )
    request = ConditionedRadialRequest(
        sector=Sector(key.sector),
        ell=key.ell,
        k=float(key.kM),
        required_radius=exact_sites[0].radius_M,
        evaluation_radii=tuple(site.radius_M for site in exact_sites[1:]),
        r_out=selection.selected_r_out_M,
        r_in_eps=policy.r_in_eps,
        rtol=policy.rtol,
        atol=policy.atol,
        outer_basis="jost_1_over_r",
        outer_series_order=policy.outer_series_order,
        integration_method="DOP853",
    )
    try:
        result = solver(request, background or SchwarzschildBackground(M=1.0))
        diagnostics = dict(result.diagnostics)
        _provenance_is_generic(diagnostics)
        expected_diagnostics = {
            "actual_precision_bits": 53,
            "atol": request.atol,
            "backend": "scipy_float64_conditioned_radial_v1",
            "ell": request.ell,
            "finite_radius_checkpoint_count": 8,
            "finite_radius_checkpoint_radii": ",".join(
                format(site.radius_M, ".17g") for site in exact_sites
            ),
            "k": request.k,
            "outer_basis": request.outer_basis,
            "outer_series_order": request.outer_series_order,
            "r_out": request.r_out,
            "required_radius": request.required_radius,
            "rtol": request.rtol,
            "scientific_acceptance": False,
            "sector": request.sector.value,
            "unit_incoming_at_infinity": True,
            "valid_at_required_radius": True,
        }
        if any(
            diagnostics.get(name) != value
            for name, value in expected_diagnostics.items()
        ):
            raise ProductionFiniteRadiusError(
                "conditioned result/request identity changed"
            )
        if result.A_in != 1.0 + 0.0j:
            raise ProductionFiniteRadiusError("result is not unit incoming")
        states = tuple(result.finite_radius_states)
        if len(states) != 8 or tuple(state.radius for state in states) != tuple(
            site.radius_M for site in exact_sites
        ):
            raise ProductionFiniteRadiusError("eight-state result inventory changed")
        if any(
            left != right
            for left, right in (
                (states[0].psi, result.psi),
                (states[0].dpsi_dr, result.dpsi_dr),
                (states[0].log_abs_psi, result.log_abs_psi),
                (states[0].phase_psi, result.phase_psi),
                (states[0].log_abs_dpsi_dr, result.log_abs_dpsi_dr),
                (states[0].phase_dpsi_dr, result.phase_dpsi_dr),
            )
        ):
            raise ProductionFiniteRadiusError("primary state/result linkage changed")
        state_records = [
            _state_record(state, site)
            for state, site in zip(states, exact_sites, strict=True)
        ]
        log_probability = 2.0 * _finite_float(
            result.log_abs_T_horizon, "log_abs_T_horizon"
        )
        if log_probability < math.log(float(np.nextafter(0.0, 1.0))):
            transmission_probability = 0.0
        elif log_probability > math.log(float(np.finfo(float).max)):
            raise ProductionFiniteRadiusError(
                "transmission probability exceeds float64"
            )
        else:
            transmission_probability = math.exp(log_probability)
        computed_flux_residual = abs(
            abs(result.A_out) ** 2 + transmission_probability - 1.0
        )
        reported_flux_residual = _finite_float(
            diagnostics.get("flux_residual"), "flux_residual"
        )
        if not math.isclose(
            computed_flux_residual,
            reported_flux_residual,
            rel_tol=5.0e-13,
            abs_tol=5.0e-15,
        ):
            raise ProductionFiniteRadiusError("flux residual is inconsistent")
        flux_passed = reported_flux_residual <= policy.maximum_flux_residual
        acceptance_state = "PARTIAL" if flux_passed else "FAIL"
        mode_failures = (
            {}
            if flux_passed
            else {
                "flux_conservation": (
                    f"FLUX_RESIDUAL_EXCEEDS_GATE: {reported_flux_residual:.17g}"
                )
            }
        )
        scattering = -result.A_out / ((-1) ** key.ell)
        raw_diagnostics: dict[str, object] = {}
        for name, value in sorted(diagnostics.items()):
            if isinstance(value, bool | int | str):
                raw_diagnostics[name] = value
            elif isinstance(value, float):
                raw_diagnostics[name] = _finite_float(value, name)
            else:
                raise ProductionFiniteRadiusError(
                    f"unsupported diagnostic type: {name}"
                )
        numerical, convention = _budgets(
            numerical_status=acceptance_state,
            convention_status="PARTIAL" if flux_passed else "FAIL",
        )
        payload = {
            "acceptance_state": acceptance_state,
            "actual_precision": {
                "backend": "scipy_float64_conditioned_radial_v1",
                "digits": 16,
            },
            "convention_budget": convention,
            "failures": mode_failures,
            "key": key.to_record(),
            "numerical_budget": numerical,
            "observable_statuses": {
                "convention_closure": "NOT_ASSESSED",
                "detector_response": "NOT_ASSESSED",
                "flux_conservation": "PASS" if flux_passed else "FAIL",
                "infinity_waveform": "NOT_ASSESSED",
                "observer_qualified_tidal_response": "NOT_ASSESSED",
                "production_eight_radius_radial_states": (
                    "PARTIAL" if flux_passed else "FAIL"
                ),
                "radial_s_matrix": "PARTIAL" if flux_passed else "FAIL",
            },
            "outer_selection": selection.to_record(),
            "policy_sha256": policy.sha256,
            "provenance": {
                "legacy": False,
                "np": False,
                "pseudoinverse": False,
            },
            "result": {
                "A_in": _complex_record(result.A_in),
                "A_out": _complex_record(result.A_out),
                "S": _complex_record(scattering),
                "T_horizon": _complex_record(result.T_horizon),
                "diagnostics": raw_diagnostics,
                "finite_radius_states": state_records,
                "flux": {
                    "balance": _finite_float(
                        diagnostics.get("flux_balance"), "flux_balance"
                    ),
                    "horizon_transmission_probability": transmission_probability,
                    "reflection_probability": float(abs(result.A_out) ** 2),
                    "residual": reported_flux_residual,
                    "status": "PASS" if flux_passed else "FAIL",
                },
                "phase_convention": {
                    "absolute_observer_phase_frozen": False,
                    "radial_normalization": "A_in=1 in jost_1_over_r basis",
                    "S_definition": "-A_out/((-1)**ell)",
                    "status": "PARTIAL",
                },
                "request": {
                    "atol": request.atol,
                    "evaluation_radii_M": list(request.evaluation_radii),
                    "integration_method": request.integration_method,
                    "outer_basis": request.outer_basis,
                    "outer_series_order": request.outer_series_order,
                    "production_estimated_outer_segments": production_outer_segments,
                    "r_in_eps": request.r_in_eps,
                    "r_out_M": request.r_out,
                    "required_radius_M": request.required_radius,
                    "rtol": request.rtol,
                },
            },
            "schema": SOLVER_PAYLOAD_SCHEMA,
            "scope_qualification": {
                "finite_radius_outputs_are_observer_qualified": False,
                "full_paper_figure_rerun": False,
                "infinity_waveform_claim": False,
                "radial_master_field_states_only": True,
            },
            "solver_call_count": 1,
            "table_i_sites": [site.to_record() for site in exact_sites],
        }
    except Exception as exc:
        payload = _failed_payload(
            key,
            selection,
            exact_sites,
            policy,
            reason=f"{type(exc).__name__}: {str(exc) or '<empty exception message>'}",
            solver_call_count=1,
        )
    validate_solver_payload(payload, key=key, sites=exact_sites, policy=policy)
    return payload


def validate_solver_payload(
    payload: Mapping[str, object],
    *,
    key: RadialKey,
    sites: Sequence[TableISite],
    policy: ProductionFiniteRadiusPolicy = DEFAULT_POLICY,
) -> None:
    """Validate a reloaded per-mode payload without trusting the producer."""

    required = {
        "acceptance_state",
        "actual_precision",
        "convention_budget",
        "failures",
        "key",
        "numerical_budget",
        "observable_statuses",
        "outer_selection",
        "policy_sha256",
        "provenance",
        "result",
        "schema",
        "scope_qualification",
        "solver_call_count",
        "table_i_sites",
    }
    if set(payload) != required or payload.get("schema") != SOLVER_PAYLOAD_SCHEMA:
        raise ProductionFiniteRadiusError("solver payload schema changed")
    if payload["key"] != key.to_record() or payload["policy_sha256"] != policy.sha256:
        raise ProductionFiniteRadiusError("solver payload key/policy changed")
    exact_sites = tuple(sites)
    if payload["table_i_sites"] != [site.to_record() for site in exact_sites]:
        raise ProductionFiniteRadiusError("solver payload site binding changed")
    if payload["provenance"] != {
        "legacy": False,
        "np": False,
        "pseudoinverse": False,
    }:
        raise ProductionFiniteRadiusError("solver payload provenance changed")
    if payload["scope_qualification"] != {
        "finite_radius_outputs_are_observer_qualified": False,
        "full_paper_figure_rerun": False,
        "infinity_waveform_claim": False,
        "radial_master_field_states_only": True,
    }:
        raise ProductionFiniteRadiusError("solver payload scope changed")
    acceptance = payload["acceptance_state"]
    if acceptance not in {"PARTIAL", "FAIL"}:
        raise ProductionFiniteRadiusError("mode acceptance must be PARTIAL or FAIL")
    calls = payload["solver_call_count"]
    if isinstance(calls, bool) or calls not in {0, 1}:
        raise ProductionFiniteRadiusError("mode solver-call count changed")
    for budget_name in ("numerical_budget", "convention_budget"):
        budget = payload[budget_name]
        expected_fields = (
            NUMERICAL_BUDGET_FIELDS
            if budget_name == "numerical_budget"
            else CONVENTION_BUDGET_FIELDS
        )
        if (
            not isinstance(budget, Mapping)
            or set(budget) != {"component_statuses", "components", "status"}
            or budget["status"] not in {"PARTIAL", "FAIL"}
            or not isinstance(budget["components"], Mapping)
            or set(budget["components"]) != set(expected_fields)
            or not isinstance(budget["component_statuses"], Mapping)
            or set(budget["component_statuses"]) != set(expected_fields)
        ):
            raise ProductionFiniteRadiusError(f"{budget_name} schema changed")
        for name, value in budget["components"].items():
            if _finite_float(value, f"{budget_name}.{name}") < 0.0:
                raise ProductionFiniteRadiusError("uncertainty budget is negative")
        if any(
            value not in STATUS_VOCABULARY
            for value in budget["component_statuses"].values()
        ):
            raise ProductionFiniteRadiusError("component status vocabulary changed")
    convention = payload["convention_budget"]
    if any(
        convention["components"][name] == 0.0  # type: ignore[index]
        for name in ("observer", "tetrad", "polarization_basis")
    ):
        raise ProductionFiniteRadiusError("unassessed conventions may not be zero")
    observables = payload["observable_statuses"]
    failures = payload["failures"]
    if not isinstance(failures, Mapping):
        raise ProductionFiniteRadiusError("mode failure ledger changed")
    if not isinstance(observables, Mapping) or any(
        value not in STATUS_VOCABULARY for value in observables.values()
    ):
        raise ProductionFiniteRadiusError("observable status vocabulary changed")
    if any(
        observables.get(name) not in {"NOT_ASSESSED", "PARTIAL"}
        for name in (
            "observer_qualified_tidal_response",
            "detector_response",
            "infinity_waveform",
            "convention_closure",
        )
    ):
        raise ProductionFiniteRadiusError("observer/convention claim was promoted")
    result = payload["result"]
    if isinstance(result, Mapping):
        if calls != 1:
            raise ProductionFiniteRadiusError("result payload lacks one solver call")
        states = result.get("finite_radius_states")
        if not isinstance(states, list) or len(states) != 8:
            raise ProductionFiniteRadiusError("payload lacks eight radial states")
        if [state.get("site") for state in states if isinstance(state, Mapping)] != [
            site.to_record() for site in exact_sites
        ]:
            raise ProductionFiniteRadiusError("payload radial state sites changed")
    if acceptance == "PARTIAL":
        if not isinstance(result, Mapping) or failures:
            raise ProductionFiniteRadiusError("PARTIAL payload lacks a clean result")
        if observables.get("flux_conservation") != "PASS":
            raise ProductionFiniteRadiusError("PARTIAL payload lacks flux PASS")
    else:
        if not failures:
            raise ProductionFiniteRadiusError("FAIL payload lacks a failure reason")
        if isinstance(result, Mapping):
            if observables.get("flux_conservation") != "FAIL":
                raise ProductionFiniteRadiusError(
                    "retained FAIL result must expose flux failure"
                )
        elif result is not None:
            raise ProductionFiniteRadiusError("FAIL payload result type changed")


def key_artifact_filenames(ordinal: int, key: RadialKey) -> dict[str, str]:
    if isinstance(ordinal, bool) or not isinstance(ordinal, int) or ordinal < 0:
        raise ProductionFiniteRadiusError("key ordinal must be nonnegative")
    token = (
        f"key_{ordinal:04d}__kM_{key.kM.replace('.', 'p')}__"
        f"{key.sector}__ell_{key.ell:04d}"
    )
    return {
        "payload": f"{token}__payload.json",
        "terminal": f"{token}__terminal.json",
    }


def source_hash_map(
    identities: Mapping[str, Mapping[str, object]],
) -> dict[str, str]:
    result: dict[str, str] = {}
    for name, identity in sorted(identities.items()):
        digest = identity.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ProductionFiniteRadiusError(f"source hash missing: {name}")
        result[name] = digest
    return result


def scientific_context_hash(record: Mapping[str, object]) -> str:
    """Hash scientific context while excluding publication location and time."""

    excluded = {
        "context_sha256",
        "created_at_utc",
        "output_root",
        "resume_from",
    }
    return hashlib.sha256(
        canonical_json_bytes(
            {name: value for name, value in record.items() if name not in excluded}
        )
    ).hexdigest()


__all__ = [
    "DEFAULT_POLICY",
    "EXPECTED_COORDINATE_SOURCE_SHA256",
    "EXPECTED_DOMAIN_IDENTITIES",
    "EXPECTED_EXECUTION_IDENTITIES",
    "EXPECTED_TABLE_I_POINT_IDS",
    "EXPECTED_TABLE_I_X_M",
    "EXPECTED_TABLE_I_Y_M",
    "EXPECTED_TABLE_I_Z_M",
    "FrozenProductionContract",
    "KEY_TERMINAL_SCHEMA",
    "MANIFEST_SCHEMA",
    "POLICY_SCHEMA",
    "ProductionFiniteRadiusError",
    "ProductionFiniteRadiusPolicy",
    "RUN_CONTRACT_SCHEMA",
    "SHARD_FAILURE_SCHEMA",
    "SHARD_RESULT_SCHEMA",
    "SOLVER_PAYLOAD_SCHEMA",
    "TableISite",
    "execute_production_finite_radius_key",
    "key_artifact_filenames",
    "load_frozen_production_contract",
    "scientific_context_hash",
    "select_outer_boundary",
    "solve_conditioned_radial_at_radius",
    "source_hash_map",
    "validate_solver_payload",
]
