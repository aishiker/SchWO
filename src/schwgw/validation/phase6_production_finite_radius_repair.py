"""Fail-closed repair diagnostic for the production eight-radius state gate.

This module consumes the immutable Phase-6 production finite-radius campaign,
selects exactly its failed modes, and evaluates those modes with the isolated
scaled-tortoise backend.  The output is radial-state evidence only.  It does
not establish an observer response, an infinity waveform, a polarization
convention, or scientific acceptance.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
import json
import math
from pathlib import Path
from typing import Any

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.numerics.conditioned_radial import (
    ConditionedRadialRequest,
    ConditionedRadialResult,
)
from schwgw.numerics.scaled_tortoise_radial import (
    solve_scaled_tortoise_radial_at_radius,
)
from schwgw.perturbations import Sector
from schwgw.validation.phase6_domain import (
    RadialKey,
    canonical_json_bytes,
    sha256_bytes,
    source_file_identity,
)
from schwgw.validation.phase6_production_finite_radius import (
    DEFAULT_POLICY,
    FrozenProductionContract,
    TableISite,
    load_frozen_production_contract,
    validate_solver_payload,
)
from schwgw.validation.phase6_production_finite_radius_campaign import (
    validate_campaign_result,
)

REPAIR_SCHEMA = "schwgw.phase6.production_finite_radius_repair_record.v1"
INVENTORY_SCHEMA = "schwgw.phase6.production_finite_radius_repair_inventory.v1"
EXPECTED_FAILURE_COUNT = 3_382
EXPECTED_FAILURE_REASON = (
    "RuntimeError: conditioned Riccati propagation failed: Required step size "
    "is less than spacing between numbers."
)
EXPECTED_CAMPAIGN_RESULT_SHA256 = (
    "eb089da8bf1ac947dc56c3f44fc5eef7856c6b7d21a7f63e676801b24d952a3f"
)
EXPECTED_CAMPAIGN_MANIFEST_SHA256 = (
    "f214d97d792bb90e51ecf914c4ddb4d77f209472e66768c03a6cdef68bef3cfe"
)
EXPECTED_BACKEND = "scipy_float64_scaled_tortoise_radial_repair_v1"
EXPECTED_METHOD = "scaled_tortoise_full_state_jost_ratio"
SUPERSEDED_REPRESENTATIVE_ROOT = (
    "v1_production_finite_radius_k0p5_odd_v1_20260808_py314"
)


@dataclass(frozen=True)
class RepairMode:
    """One failed production key selected for repair diagnostics."""

    ordinal: int
    key: RadialKey
    shard_id: str
    selected_r_out_M: float
    predecessor_failures: Mapping[str, str]
    predecessor_payload_identity: Mapping[str, Any]

    def to_record(self) -> dict[str, Any]:
        return {
            "ordinal": self.ordinal,
            "key": self.key.to_record(),
            "key_id": repair_key_id(self.key),
            "shard_id": self.shard_id,
            "selected_r_out_M": self.selected_r_out_M,
            "predecessor_failures": dict(self.predecessor_failures),
            "predecessor_payload_identity": dict(self.predecessor_payload_identity),
        }


@dataclass(frozen=True)
class RepairInventory:
    """Validated immutable predecessor plus its exact failed-mode inventory."""

    campaign_root: Path
    campaign_result_identity: Mapping[str, Any]
    campaign_manifest_identity: Mapping[str, Any]
    frozen: FrozenProductionContract
    modes: tuple[RepairMode, ...]
    inventory_sha256: str

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": INVENTORY_SCHEMA,
            "campaign_root": str(self.campaign_root.resolve()),
            "campaign_result_identity": dict(self.campaign_result_identity),
            "campaign_manifest_identity": dict(self.campaign_manifest_identity),
            "failure_mode_count": len(self.modes),
            "inventory_sha256": self.inventory_sha256,
            "modes": [mode.to_record() for mode in self.modes],
        }


RepairSolver = Callable[
    [ConditionedRadialRequest, SchwarzschildBackground], ConditionedRadialResult
]


def _load_canonical_json(path: Path) -> Mapping[str, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON in {path}") from exc
    if not isinstance(value, Mapping):
        raise RuntimeError(f"JSON root must be an object: {path}")
    if raw != canonical_json_bytes(value):
        raise RuntimeError(f"JSON is not canonical: {path}")
    return value


def _require_immutable_file(path: Path, *, sha256: str | None = None) -> dict[str, Any]:
    identity = source_file_identity(path)
    if identity["mode"] != 0o444 or identity["nlink"] != 1:
        raise RuntimeError(f"evidence file is not immutable 0444/nlink1: {path}")
    if sha256 is not None and identity["sha256"] != sha256:
        raise RuntimeError(
            f"unexpected SHA-256 for {path}: {identity['sha256']} != {sha256}"
        )
    return identity


def _same_identity(observed: Mapping[str, Any], expected: Mapping[str, Any]) -> bool:
    return all(observed.get(name) == expected.get(name) for name in expected)


def _canonical_key_order(key: RadialKey) -> tuple[Decimal, int, int]:
    return (Decimal(key.kM), 0 if key.sector == "odd" else 1, key.ell)


def repair_key_id(key: RadialKey) -> str:
    """Stable human-readable identity for one repair key."""

    return f"kM={key.kM};sector={key.sector};ell={key.ell}"


def load_repair_inventory(
    campaign_root: Path,
    *,
    domain_root: Path,
    execution_root: Path,
) -> RepairInventory:
    """Load and validate the exact 3,382-mode repair inventory.

    This deliberately performs the full predecessor campaign validation before
    consuming any failure entry.  The superseded representative v1 shard is
    rejected even if it is somehow introduced into a modified campaign.
    """

    campaign_root = campaign_root.resolve()
    if not campaign_root.is_dir() or campaign_root.stat().st_mode & 0o777 != 0o555:
        raise RuntimeError(
            f"campaign root is not an immutable 0555 directory: {campaign_root}"
        )

    result_path = campaign_root / "campaign_result.json"
    manifest_path = campaign_root / "manifest.json"
    result_identity = _require_immutable_file(
        result_path, sha256=EXPECTED_CAMPAIGN_RESULT_SHA256
    )
    manifest_identity = _require_immutable_file(
        manifest_path, sha256=EXPECTED_CAMPAIGN_MANIFEST_SHA256
    )
    result = _load_canonical_json(result_path)
    manifest = _load_canonical_json(manifest_path)

    validate_campaign_result(result)
    manifest_result = manifest.get("campaign_result_identity")
    if not isinstance(manifest_result, Mapping) or not _same_identity(
        result_identity, manifest_result
    ):
        raise RuntimeError("campaign manifest does not bind RESULT.json")

    frozen = load_frozen_production_contract(
        domain_root=domain_root,
        execution_root=execution_root,
    )
    failures = result.get("failures")
    coverage = result.get("coverage")
    missing = (
        coverage.get("missing_eight_state_modes")
        if isinstance(coverage, Mapping)
        else None
    )
    if not isinstance(failures, Sequence) or isinstance(failures, (str, bytes)):
        raise RuntimeError("campaign failures must be a sequence")
    if not isinstance(missing, Sequence) or isinstance(missing, (str, bytes)):
        raise RuntimeError("campaign missing_state_records must be a sequence")
    if (
        len(failures) != EXPECTED_FAILURE_COUNT
        or len(missing) != EXPECTED_FAILURE_COUNT
    ):
        raise RuntimeError(
            "predecessor failure coverage changed: "
            f"failures={len(failures)}, missing={len(missing)}"
        )

    missing_keys = [RadialKey.from_record(item) for item in missing]
    failure_keys: list[RadialKey] = []
    modes: list[RepairMode] = []
    seen: set[RadialKey] = set()

    for ordinal, item in enumerate(failures):
        if not isinstance(item, Mapping):
            raise RuntimeError(f"failure entry {ordinal} is not an object")
        key_record = item.get("key")
        key = RadialKey.from_record(key_record)
        failure_keys.append(key)
        if key in seen:
            raise RuntimeError(
                f"duplicate predecessor failure key: {repair_key_id(key)}"
            )
        seen.add(key)
        if key not in set(frozen.production_keys):
            raise RuntimeError(
                f"failure key is outside frozen D_prod: {repair_key_id(key)}"
            )

        reasons = item.get("failures")
        if reasons != {"production_finite_radius": EXPECTED_FAILURE_REASON}:
            raise RuntimeError(
                f"unexpected predecessor failure reason for {repair_key_id(key)}: {reasons!r}"
            )
        shard_id = item.get("shard_id")
        if not isinstance(shard_id, str) or not shard_id:
            raise RuntimeError(f"invalid shard id for {repair_key_id(key)}")
        payload_identity = item.get("payload_identity")
        if not isinstance(payload_identity, Mapping):
            raise RuntimeError(f"missing payload identity for {repair_key_id(key)}")
        payload_path = Path(str(payload_identity.get("path", ""))).resolve()
        if payload_path.parent.name == SUPERSEDED_REPRESENTATIVE_ROOT:
            raise RuntimeError("superseded kM=0.5 odd v1 shard is forbidden")
        observed_identity = _require_immutable_file(payload_path)
        if not _same_identity(observed_identity, payload_identity):
            raise RuntimeError(f"payload identity drift for {repair_key_id(key)}")
        payload = _load_canonical_json(payload_path)
        validate_solver_payload(payload, key=key, sites=frozen.sites)
        if payload.get("key") != key.to_record() or payload.get("failures") != reasons:
            raise RuntimeError(
                f"failure ledger/payload mismatch for {repair_key_id(key)}"
            )

        selection = payload.get("outer_selection")
        if not isinstance(selection, Mapping) or selection.get("status") != "SUPPORTED":
            raise RuntimeError(
                f"unsupported predecessor outer selection for {repair_key_id(key)}"
            )
        r_out = float(selection.get("selected_r_out_M", math.nan))
        if not math.isfinite(r_out) or r_out <= max(
            site.radius_M for site in frozen.sites
        ):
            raise RuntimeError(
                f"invalid predecessor r_out for {repair_key_id(key)}: {r_out}"
            )

        modes.append(
            RepairMode(
                ordinal=ordinal,
                key=key,
                shard_id=shard_id,
                selected_r_out_M=r_out,
                predecessor_failures=dict(reasons),
                predecessor_payload_identity=dict(payload_identity),
            )
        )

    if failure_keys != missing_keys:
        raise RuntimeError("failure ledger and missing-state ledger differ")
    if failure_keys != sorted(failure_keys, key=_canonical_key_order):
        raise RuntimeError("failure inventory is not in canonical production order")

    inventory_bytes = canonical_json_bytes([mode.to_record() for mode in modes])
    return RepairInventory(
        campaign_root=campaign_root,
        campaign_result_identity=result_identity,
        campaign_manifest_identity=manifest_identity,
        frozen=frozen,
        modes=tuple(modes),
        inventory_sha256=sha256_bytes(inventory_bytes),
    )


def build_repair_request(
    mode: RepairMode,
    sites: Sequence[TableISite],
) -> ConditionedRadialRequest:
    """Build one solve request covering all exact production Table-I radii."""

    radii = tuple(site.radius_M for site in sites)
    if len(radii) != 8 or radii != tuple(sorted(radii)) or len(set(radii)) != 8:
        raise RuntimeError("repair requires exactly eight increasing Table-I radii")
    return ConditionedRadialRequest(
        ell=mode.key.ell,
        k=float(mode.key.kM),
        sector=Sector(mode.key.sector),
        required_radius=radii[0],
        r_out=mode.selected_r_out_M,
        r_in_eps=DEFAULT_POLICY.r_in_eps,
        rtol=DEFAULT_POLICY.rtol,
        atol=DEFAULT_POLICY.atol,
        outer_series_order=DEFAULT_POLICY.outer_series_order,
        outer_basis="jost_1_over_r",
        evaluation_radii=radii[1:],
        integration_method="DOP853",
    )


def _complex_record(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag)}


def _site_record(site: TableISite) -> dict[str, Any]:
    return dict(site.to_record())


def _request_record(request: ConditionedRadialRequest) -> dict[str, Any]:
    return {
        "ell": request.ell,
        "kM": format(request.k, ".17g"),
        "sector": request.sector.value,
        "required_radius_M": format(request.required_radius, ".17g"),
        "evaluation_radii_M": [
            format(value, ".17g") for value in request.evaluation_radii
        ],
        "r_out_M": format(request.r_out, ".17g"),
        "r_in_eps_M": format(request.r_in_eps, ".17g"),
        "rtol": format(request.rtol, ".17g"),
        "atol": format(request.atol, ".17g"),
        "outer_series_order": request.outer_series_order,
        "outer_basis": request.outer_basis,
        "integration_method": request.integration_method,
    }


def _state_record(site: TableISite, state: Any) -> dict[str, Any]:
    psi = complex(state.psi)
    dpsi = complex(state.dpsi_dr)
    log_amplitude = float(state.log_abs_psi)
    phase = float(state.phase_psi)
    log_derivative_amplitude = float(state.log_abs_dpsi_dr)
    derivative_phase = float(state.phase_dpsi_dr)
    if not all(
        math.isfinite(value)
        for value in (
            psi.real,
            psi.imag,
            dpsi.real,
            dpsi.imag,
            log_amplitude,
            phase,
            log_derivative_amplitude,
            derivative_phase,
        )
    ):
        raise RuntimeError(f"non-finite radial state at {site.point_id}")
    return {
        **_site_record(site),
        "psi": _complex_record(psi),
        "dpsi_dr": _complex_record(dpsi),
        "log_abs_psi": log_amplitude,
        "phase_psi_rad": phase,
        "log_abs_dpsi_dr": log_derivative_amplitude,
        "phase_dpsi_dr_rad": derivative_phase,
        "complex_state_status": str(state.complex_state_status),
        "complex_derivative_status": str(state.complex_derivative_status),
        "state_status": "MEASURED",
    }


def _diagnostics_record(result: ConditionedRadialResult) -> dict[str, Any]:
    diagnostics = dict(result.diagnostics)
    retained = {
        key: value
        for key, value in diagnostics.items()
        if isinstance(value, (bool, int, float, str)) or value is None
    }
    return retained


def _result_record(
    result: ConditionedRadialResult,
    sites: Sequence[TableISite],
) -> dict[str, Any]:
    state_map = {float(item.radius): item for item in result.finite_radius_states}
    states: list[dict[str, Any]] = []
    for site in sites:
        radius = float(site.radius_M_decimal)
        matches = [state for value, state in state_map.items() if value == radius]
        if len(matches) != 1:
            raise RuntimeError(f"backend did not return exact radius {radius}")
        states.append(_state_record(site, matches[0]))
    diagnostics = _diagnostics_record(result)
    radial_s = result.A_out / result.A_in
    return {
        "states": states,
        "A_in": _complex_record(result.A_in),
        "A_out": _complex_record(result.A_out),
        "radial_S": _complex_record(radial_s),
        "T_horizon": _complex_record(result.T_horizon),
        "log_abs_T_horizon": float(result.log_abs_T_horizon),
        "phase_T_horizon_rad": float(result.phase_T_horizon),
        "flux_diagnostics": {
            "reflection_probability": diagnostics.get("reflection_probability"),
            "horizon_transmission_probability": diagnostics.get(
                "horizon_transmission_probability"
            ),
            "flux_balance": diagnostics.get("flux_balance"),
            "flux_residual": diagnostics.get("flux_residual"),
            "maximum_current_relative_drift": diagnostics.get(
                "maximum_current_relative_drift"
            ),
            "current_drift_resolved": diagnostics.get("current_drift_resolved"),
            "interpretation": diagnostics.get("flux_interpretation"),
        },
        "diagnostics": diagnostics,
    }


def _common_record(
    mode: RepairMode,
    sites: Sequence[TableISite],
    request: ConditionedRadialRequest,
) -> dict[str, Any]:
    return {
        "schema": REPAIR_SCHEMA,
        "ordinal": mode.ordinal,
        "key": mode.key.to_record(),
        "key_id": repair_key_id(mode.key),
        "shard_id": mode.shard_id,
        "solver_call_count": 1,
        "predecessor": {
            "failure_reasons": dict(mode.predecessor_failures),
            "payload_identity": dict(mode.predecessor_payload_identity),
            "selected_r_out_M": mode.selected_r_out_M,
        },
        "backend_request": _request_record(request),
        "table_i_sites": [_site_record(site) for site in sites],
        "diagnostic_only": True,
        "scientific_acceptance": False,
        "global_green_permitted": False,
        "scope_qualification": {
            "production_radial_states": "ASSESSED",
            "observer_response": "NOT_ASSESSED",
            "detector_response": "NOT_ASSESSED",
            "infinity_waveform": "NOT_ASSESSED",
            "polarization_convention": "NOT_ASSESSED",
        },
        "numerical_uncertainty": {
            "status": "NOT_CLOSED",
            "budget": "unbounded_pending_independent_ladders",
            "upper_bound": None,
        },
        "convention_uncertainty": {
            "status": "NOT_ASSESSED",
            "budget": "unbounded_observer_tetrad_polarization_convention",
            "upper_bound": None,
        },
    }


def validate_repair_record(
    record: Mapping[str, Any],
    *,
    mode: RepairMode,
    sites: Sequence[TableISite],
) -> None:
    """Fail closed on one repair result, including diagnostic provenance."""

    request = build_repair_request(mode, sites)
    expected_common = _common_record(mode, sites, request)
    for name, expected in expected_common.items():
        if record.get(name) != expected:
            raise RuntimeError(
                f"repair record field mismatch for {name}: {repair_key_id(mode.key)}"
            )
    if record.get("status") not in {"MEASURED", "FAIL"}:
        raise RuntimeError(f"invalid repair status for {repair_key_id(mode.key)}")
    if record.get("scientific_acceptance") is not False:
        raise RuntimeError("repair diagnostic cannot establish scientific acceptance")

    if record["status"] == "FAIL":
        if record.get("result") is not None:
            raise RuntimeError("failed repair record cannot contain a result")
        failures = record.get("failures")
        if not isinstance(failures, Mapping) or set(failures) != {"repair_backend"}:
            raise RuntimeError("failed repair record needs one repair_backend reason")
        return

    if record.get("failures") != {}:
        raise RuntimeError("measured repair record cannot contain failures")
    result = record.get("result")
    if not isinstance(result, Mapping):
        raise RuntimeError("measured repair record is missing result")
    states = result.get("states")
    if not isinstance(states, Sequence) or len(states) != 8:
        raise RuntimeError("measured repair record requires eight states")
    for state, site in zip(states, sites, strict=True):
        if not isinstance(state, Mapping):
            raise RuntimeError("radial state is not an object")
        for name, expected in _site_record(site).items():
            if state.get(name) != expected:
                raise RuntimeError(f"state/site mismatch at {site.point_id}")
        if state.get("state_status") != "MEASURED":
            raise RuntimeError(f"invalid state status at {site.point_id}")
    diagnostics = result.get("diagnostics")
    if not isinstance(diagnostics, Mapping):
        raise RuntimeError("repair result lacks diagnostics")
    required = {
        "method": EXPECTED_METHOD,
        "backend": EXPECTED_BACKEND,
        "backend_version": 1,
        "scientific_acceptance": False,
        "independent_validation": False,
        "paper_specific_envelope_used": False,
        "riccati_variable_used": False,
        "legacy_path_used": False,
        "newman_penrose_path_used": False,
        "pseudoinverse_used": False,
    }
    for name, expected in required.items():
        if diagnostics.get(name) != expected:
            raise RuntimeError(
                "repair backend provenance mismatch for "
                f"{name}: {repair_key_id(mode.key)}"
            )


def execute_repair_mode(
    mode: RepairMode,
    sites: Sequence[TableISite],
    *,
    solver: RepairSolver = solve_scaled_tortoise_radial_at_radius,
) -> dict[str, Any]:
    """Execute exactly one solve for a failed mode and serialize its 8 states."""

    request = build_repair_request(mode, sites)
    record = _common_record(mode, sites, request)
    try:
        result = solver(request, SchwarzschildBackground(M=1.0))
        record.update(
            {
                "status": "MEASURED",
                "result": _result_record(result, sites),
                "failures": {},
            }
        )
    except Exception as exc:  # noqa: BLE001 - scientific failures are evidence
        record.update(
            {
                "status": "FAIL",
                "result": None,
                "failures": {
                    "repair_backend": f"{type(exc).__name__}: {exc}",
                },
            }
        )
    validate_repair_record(record, mode=mode, sites=sites)
    return record


__all__ = [
    "EXPECTED_BACKEND",
    "EXPECTED_CAMPAIGN_MANIFEST_SHA256",
    "EXPECTED_CAMPAIGN_RESULT_SHA256",
    "EXPECTED_FAILURE_COUNT",
    "EXPECTED_FAILURE_REASON",
    "INVENTORY_SCHEMA",
    "REPAIR_SCHEMA",
    "RepairInventory",
    "RepairMode",
    "build_repair_request",
    "execute_repair_mode",
    "load_repair_inventory",
    "repair_key_id",
    "validate_repair_record",
]
