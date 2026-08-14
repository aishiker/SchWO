"""Exact, non-numerical Phase-6 V1 radial-domain contract.

This module freezes *which* radial modes require independent validation.  It
does not select a numerical backend and deliberately makes no acceptance
claim.  The production portion is read from the accepted uniform-40 source;
the three extra frequencies are explicitly validation policy, not completed
production facts.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re

import numpy as np


DOMAIN_SCHEMA = "schwgw_phase6_v1_domain_contract_v1"
KEY_SCHEMA = "schwgw_phase6_radial_key_v1"
SECTORS = ("odd", "even")
SECTOR_ORDER = {sector: index for index, sector in enumerate(SECTORS)}
_CANONICAL_DECIMAL = re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]*[1-9])?")

# These entries are policy declarations for independent validation only.  They
# are intentionally separate from the observed Fig. 5/6 production schedule.
AUDIT_EXTENSION_LMAX: dict[str, int] = {"0.01": 84, "0.05": 84, "8": 720}
AUDIT_REQUIRED_LMAX: dict[str, int] = {
    "0.01": 84,
    "0.05": 84,
    "0.1": 84,
    "0.5": 84,
    "1": 108,
    "2": 180,
    "4": 360,
    "8": 720,
}
EXPECTED_PRODUCTION_KM = tuple(
    str(Decimal(value) / Decimal("10")) for value in range(1, 41)
)


class DomainContractError(ValueError):
    """Raised when the frozen domain cannot be reconstructed exactly."""


def canonical_km(value: str | float | Decimal | int) -> str:
    """Return a non-exponent, no-redundant-zero decimal frequency label."""

    if isinstance(value, str):
        if not _CANONICAL_DECIMAL.fullmatch(value):
            raise DomainContractError(f"non-canonical kM string: {value!r}")
        try:
            decimal = Decimal(value)
        except InvalidOperation as exc:
            raise DomainContractError(f"invalid kM: {value!r}") from exc
        if decimal <= 0:
            raise DomainContractError(f"kM must be positive: {value!r}")
        return value
    try:
        decimal = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise DomainContractError(f"invalid kM: {value!r}") from exc
    if not decimal.is_finite() or decimal <= 0:
        raise DomainContractError(f"invalid kM: {value!r}")
    result = format(decimal.normalize(), "f")
    if result == "-0":
        result = "0"
    if not _CANONICAL_DECIMAL.fullmatch(result):
        raise DomainContractError(f"cannot canonicalize kM: {value!r}")
    return result


@dataclass(frozen=True, order=False)
class RadialKey:
    """A single sector-resolved radial mode using canonical decimal kM."""

    kM: str
    sector: str
    ell: int

    def __post_init__(self) -> None:
        if canonical_km(self.kM) != self.kM:
            raise DomainContractError(f"kM is not canonical: {self.kM!r}")
        if self.sector not in SECTOR_ORDER:
            raise DomainContractError(f"unknown sector: {self.sector!r}")
        if isinstance(self.ell, bool) or not isinstance(self.ell, int) or self.ell < 2:
            raise DomainContractError(f"ell must be an integer >= 2: {self.ell!r}")

    def order_key(self) -> tuple[Decimal, int, int]:
        return (Decimal(self.kM), SECTOR_ORDER[self.sector], self.ell)

    def to_record(self) -> dict[str, object]:
        return {"ell": self.ell, "kM": self.kM, "sector": self.sector}

    @classmethod
    def from_record(cls, record: Mapping[str, object]) -> "RadialKey":
        if set(record) != {"ell", "kM", "sector"}:
            raise DomainContractError("radial-key record fields changed")
        km = record["kM"]
        sector = record["sector"]
        ell = record["ell"]
        if not isinstance(km, str) or not isinstance(sector, str):
            raise DomainContractError("radial-key kM and sector must be strings")
        return cls(kM=km, sector=sector, ell=ell)  # type: ignore[arg-type]


@dataclass(frozen=True)
class ProductionLmax:
    """Observed final pair in the accepted uniform-40 source binding."""

    kM: str
    lmax_pair: tuple[int, int]

    @property
    def final_lmax(self) -> int:
        return self.lmax_pair[1]

    def to_record(self) -> dict[str, object]:
        return {
            "final_lmax": self.final_lmax,
            "kM": self.kM,
            "lmax_pair": list(self.lmax_pair),
        }


@dataclass(frozen=True)
class DomainBundle:
    """All exact V1 key sets and the production lmax provenance."""

    production_lmax: tuple[ProductionLmax, ...]
    production: tuple[RadialKey, ...]
    extension: tuple[RadialKey, ...]
    required: tuple[RadialKey, ...]
    union: tuple[RadialKey, ...]


def _validate_lmax_pair(pair: object, km: str) -> tuple[int, int]:
    if not isinstance(pair, Sequence) or isinstance(pair, (str, bytes)) or len(pair) != 2:
        raise DomainContractError(f"lmax pair for kM={km} must have two entries")
    previous, final = pair
    if any(isinstance(item, bool) or not isinstance(item, int) for item in pair):
        raise DomainContractError(f"lmax pair for kM={km} must contain integers")
    if previous < 2 or previous >= final:
        raise DomainContractError(f"non-increasing lmax pair for kM={km}")
    return previous, final


def canonical_production_schedule(
    schedule: Mapping[float | str | Decimal | int, Sequence[int]],
) -> tuple[ProductionLmax, ...]:
    """Normalize and verify the actual complete 40-frequency source schedule."""

    normalized: dict[str, tuple[int, int]] = {}
    for raw_km, raw_pair in schedule.items():
        km = canonical_km(raw_km)
        if km in normalized:
            raise DomainContractError(f"duplicate canonical source frequency: {km}")
        normalized[km] = _validate_lmax_pair(raw_pair, km)
    if tuple(sorted(normalized, key=Decimal)) != EXPECTED_PRODUCTION_KM:
        missing = sorted(set(EXPECTED_PRODUCTION_KM) - set(normalized), key=Decimal)
        extra = sorted(set(normalized) - set(EXPECTED_PRODUCTION_KM), key=Decimal)
        raise DomainContractError(
            f"production frequency set differs; missing={missing}, extra={extra}"
        )
    return tuple(
        ProductionLmax(kM=km, lmax_pair=normalized[km])
        for km in EXPECTED_PRODUCTION_KM
    )


def _keys_for_lmax(lmax_by_km: Mapping[str, int]) -> tuple[RadialKey, ...]:
    keys = tuple(
        RadialKey(kM=km, sector=sector, ell=ell)
        for km in sorted(lmax_by_km, key=Decimal)
        for sector in SECTORS
        for ell in range(2, lmax_by_km[km] + 1)
    )
    validate_ordered_unique_keys(keys)
    return keys


def validate_ordered_unique_keys(keys: Iterable[RadialKey]) -> tuple[RadialKey, ...]:
    """Reject duplicates, unordered records, malformed records, and gaps."""

    materialized = tuple(keys)
    prior: tuple[Decimal, int, int] | None = None
    seen: set[RadialKey] = set()
    for key in materialized:
        if not isinstance(key, RadialKey):
            raise DomainContractError("domain contains a non-RadialKey value")
        if key in seen:
            raise DomainContractError(f"duplicate radial key: {key}")
        if prior is not None and key.order_key() <= prior:
            raise DomainContractError("radial keys are not in canonical strict order")
        seen.add(key)
        prior = key.order_key()
    return materialized


def _assert_exact_set(label: str, actual: tuple[RadialKey, ...], expected: set[RadialKey]) -> None:
    if set(actual) != expected or len(actual) != len(expected):
        raise DomainContractError(f"{label} set arithmetic mismatch")


def build_v1_domain(
    schedule: Mapping[float | str | Decimal | int, Sequence[int]],
) -> DomainBundle:
    """Build the frozen production, extension, required, and union key sets."""

    production_lmax = canonical_production_schedule(schedule)
    production_map = {entry.kM: entry.final_lmax for entry in production_lmax}
    production = _keys_for_lmax(production_map)
    extension = _keys_for_lmax(AUDIT_EXTENSION_LMAX)
    required = _keys_for_lmax(AUDIT_REQUIRED_LMAX)
    union = tuple(sorted(set(production) | set(extension), key=RadialKey.order_key))
    bundle = DomainBundle(
        production_lmax=production_lmax,
        production=production,
        extension=extension,
        required=required,
        union=union,
    )
    validate_bundle(bundle)
    return bundle


def validate_bundle(bundle: DomainBundle) -> None:
    """Validate all frozen cardinalities and literal set relationships."""

    if not isinstance(bundle, DomainBundle):
        raise DomainContractError("domain bundle type changed")
    expected_schedule = canonical_production_schedule(
        {item.kM: item.lmax_pair for item in bundle.production_lmax}
    )
    if bundle.production_lmax != expected_schedule:
        raise DomainContractError("production lmax schedule order changed")
    for label, keys in (
        ("D_prod", bundle.production),
        ("D_ext", bundle.extension),
        ("D_required", bundle.required),
        ("D_union", bundle.union),
    ):
        validate_ordered_unique_keys(keys)
    expected_production = set(
        _keys_for_lmax({item.kM: item.final_lmax for item in bundle.production_lmax})
    )
    expected_extension = set(_keys_for_lmax(AUDIT_EXTENSION_LMAX))
    expected_required = set(_keys_for_lmax(AUDIT_REQUIRED_LMAX))
    _assert_exact_set("D_prod", bundle.production, expected_production)
    _assert_exact_set("D_ext", bundle.extension, expected_extension)
    _assert_exact_set("D_required", bundle.required, expected_required)
    _assert_exact_set("D_union", bundle.union, expected_production | expected_extension)
    if len(bundle.production) != 16048:
        raise DomainContractError("D_prod cardinality must be 16048")
    if len(bundle.extension) != 1770:
        raise DomainContractError("D_ext cardinality must be 1770")
    if len(bundle.required) != 3392:
        raise DomainContractError("D_required cardinality must be 3392")
    if len(bundle.union) != 17818:
        raise DomainContractError("D_union cardinality must be 17818")
    if len(set(bundle.production) & set(bundle.required)) != 1622:
        raise DomainContractError("D_required/D_prod overlap must be 1622")
    if set(bundle.production) & set(bundle.extension):
        raise DomainContractError("D_ext must be disjoint from D_prod")
    if set(bundle.required) - set(bundle.production) != set(bundle.extension):
        raise DomainContractError("D_required minus D_prod must equal D_ext")
    if not set(bundle.required) <= set(bundle.union):
        raise DomainContractError("D_required must be a subset of D_union")


def canonical_json_bytes(payload: object) -> bytes:
    """Canonical JSON bytes used for all metadata and JSONL records."""

    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def jsonl_bytes(keys: Iterable[RadialKey]) -> bytes:
    """Compact canonical JSONL representation of an already validated key set."""

    validated = validate_ordered_unique_keys(keys)
    return b"".join(canonical_json_bytes(key.to_record()) for key in validated)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_file_identity(path: str | Path) -> dict[str, object]:
    """Return a source identity after rejecting symlink and hardlink aliases."""

    original = Path(path).absolute()
    try:
        status = original.lstat()
    except OSError as exc:
        raise DomainContractError(f"cannot lstat source identity: {original}") from exc
    if not original.is_file() or original.is_symlink() or status.st_nlink != 1:
        raise DomainContractError(f"source must be an original regular nlink1 path: {original}")
    return {
        "mode": status.st_mode & 0o777,
        "nlink": status.st_nlink,
        "path": str(original),
        "sha256": sha256_bytes(original.read_bytes()),
        "size": status.st_size,
    }


def _rederived_lmax_pair(record: Mapping[str, object]) -> tuple[int, int]:
    """Read the independently bound NPZ bytes, not contract metadata, for lmax."""

    resolved = record.get("resolved_source_identity")
    if not isinstance(resolved, Mapping):
        raise DomainContractError("schedule binding source identity missing")
    identity = source_file_identity(Path(str(resolved.get("path", ""))))
    if dict(resolved) != identity:
        raise DomainContractError("schedule binding source identity no longer matches bytes")
    try:
        with np.load(Path(str(identity["path"])), allow_pickle=False) as data:
            pair: np.ndarray | None = None
            if "lmax_values" in data.files:
                values = np.asarray(data["lmax_values"], dtype=int)
                if values.ndim == 1 and values.size >= 2:
                    pair = values[-2:]
            elif "final_lmax_pair" in data.files:
                row = record.get("row")
                if isinstance(row, bool) or not isinstance(row, int):
                    raise DomainContractError("schedule final_lmax_pair row missing")
                pair = np.asarray(data["final_lmax_pair"][row], dtype=int)
            else:
                raw_metadata = np.asarray(data["metadata_json"]).item()
                metadata = json.loads(str(raw_metadata))
                records = metadata.get("frequency_metadata")
                km = float(record["kM"])
                matches = [
                    item
                    for item in records
                    if isinstance(item, dict)
                    and abs(float(item.get("kM", np.nan)) - km) <= 1.0e-12
                ]
                if len(matches) != 1:
                    raise DomainContractError("schedule metadata lmax is ambiguous")
                pair = np.asarray(
                    matches[0].get("final_lmax_pair", matches[0].get("final_pair")),
                    dtype=int,
                )
    except (OSError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise DomainContractError("cannot rederive schedule lmax from source bytes") from exc
    if pair is None or pair.shape != (2,):
        raise DomainContractError("rederived schedule lmax pair is invalid")
    result = (int(pair[0]), int(pair[1]))
    if result[0] < 2 or result[0] >= result[1]:
        raise DomainContractError("rederived schedule lmax pair is non-increasing")
    return result


def read_jsonl_keys(path: str | Path) -> tuple[RadialKey, ...]:
    """Load strict canonical JSONL records and verify their ordering."""

    resolved = Path(path)
    try:
        raw = resolved.read_bytes()
        lines = raw.splitlines()
    except OSError as exc:
        raise DomainContractError(f"cannot read key list: {resolved}") from exc
    keys: list[RadialKey] = []
    for number, line in enumerate(lines, start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DomainContractError(f"invalid JSONL at line {number}") from exc
        if canonical_json_bytes(record).rstrip(b"\n") != line:
            raise DomainContractError(f"non-canonical JSONL at line {number}")
        if not isinstance(record, dict):
            raise DomainContractError(f"non-object JSONL record at line {number}")
        keys.append(RadialKey.from_record(record))
    validated = validate_ordered_unique_keys(keys)
    if raw != jsonl_bytes(validated):
        raise DomainContractError("JSONL bytes are not canonical (final LF/line ending/content)")
    return validated


def contract_payload(
    bundle: DomainBundle,
    *,
    source_identities: Mapping[str, Mapping[str, object]],
    domain_file_identities: Mapping[str, Mapping[str, object]],
    schedule_source_bindings: Sequence[Mapping[str, object]],
    consumed_predecessors: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Build compact deterministic metadata; full keys live in four JSONL files."""

    validate_bundle(bundle)
    return {
        "audit_extension_policy": {
            "description": (
                "kM=0.01, 0.05, and 8 lmax values are validation policy "
                "declarations, not completed production facts."
            ),
            "lmax_by_kM": AUDIT_EXTENSION_LMAX,
            "status": "VALIDATION_POLICY_ONLY",
        },
        "audit_required_policy": {
            "lmax_by_kM": AUDIT_REQUIRED_LMAX,
            "status": "REQUIRED_FOR_INDEPENDENT_VALIDATION",
        },
        "consumed_predecessors": [dict(item) for item in consumed_predecessors],
        "domain_files": dict(sorted(domain_file_identities.items())),
        "global_green_permitted": False,
        "production_source": {
            "description": "Observed final lmax pairs from accepted Fig. 5/6 uniform-40 source.",
            "frequency_lmax": [item.to_record() for item in bundle.production_lmax],
            "schedule_source_bindings": list(schedule_source_bindings),
        },
        "schema": DOMAIN_SCHEMA,
        "set_arithmetic": {
            "D_ext": len(bundle.extension),
            "D_prod": len(bundle.production),
            "D_prod_intersection_D_required": len(set(bundle.production) & set(bundle.required)),
            "D_required": len(bundle.required),
            "D_union": len(bundle.union),
            "identity": "D_union = D_prod union D_ext",
        },
        "source_identities": dict(sorted(source_identities.items())),
        "status": "DOMAIN_CONTRACT_FROZEN_NO_NUMERICAL_SOLVES",
    }


def validate_contract_payload(
    payload: Mapping[str, object],
    *,
    bundle: DomainBundle,
    domain_file_bytes: Mapping[str, bytes],
) -> None:
    """Fail closed if metadata, list hashes, or cardinality claims disagree."""

    validate_bundle(bundle)
    if payload.get("schema") != DOMAIN_SCHEMA:
        raise DomainContractError("domain-contract schema changed")
    if payload.get("global_green_permitted") is not False:
        raise DomainContractError("domain contract must forbid global acceptance")
    if payload.get("status") != "DOMAIN_CONTRACT_FROZEN_NO_NUMERICAL_SOLVES":
        raise DomainContractError("domain contract status changed")
    arithmetic = payload.get("set_arithmetic")
    if not isinstance(arithmetic, Mapping):
        raise DomainContractError("missing set arithmetic")
    expected_arithmetic = {
        "D_ext": 1770,
        "D_prod": 16048,
        "D_prod_intersection_D_required": 1622,
        "D_required": 3392,
        "D_union": 17818,
        "identity": "D_union = D_prod union D_ext",
    }
    if dict(arithmetic) != expected_arithmetic:
        raise DomainContractError("set arithmetic metadata mismatch")
    identities = payload.get("domain_files")
    if not isinstance(identities, Mapping):
        raise DomainContractError("missing domain file identities")
    expected_names = {"D_ext.jsonl", "D_prod.jsonl", "D_required.jsonl", "D_union.jsonl"}
    if set(identities) != expected_names or set(domain_file_bytes) != expected_names:
        raise DomainContractError("domain file names changed")
    expected_counts = {
        "D_prod.jsonl": len(bundle.production),
        "D_ext.jsonl": len(bundle.extension),
        "D_required.jsonl": len(bundle.required),
        "D_union.jsonl": len(bundle.union),
    }
    for name in sorted(expected_names):
        identity = identities[name]
        if not isinstance(identity, Mapping):
            raise DomainContractError(f"invalid identity for {name}")
        if set(identity) != {"count", "mode", "nlink", "path", "sha256", "size"}:
            raise DomainContractError(f"domain identity fields changed: {name}")
        if not isinstance(identity["path"], str) or not identity["path"]:
            raise DomainContractError(f"invalid domain identity path: {name}")
        if identity["count"] != expected_counts[name]:
            raise DomainContractError(f"domain list count mismatch: {name}")
        if identity["size"] != len(domain_file_bytes[name]):
            raise DomainContractError(f"domain list size mismatch: {name}")
        if identity["mode"] != 0o444 or identity["nlink"] != 1:
            raise DomainContractError(f"domain list file identity mismatch: {name}")
        if identity.get("sha256") != sha256_bytes(domain_file_bytes[name]):
            raise DomainContractError(f"domain list digest mismatch: {name}")
    extension_policy = payload.get("audit_extension_policy")
    if not isinstance(extension_policy, Mapping) or extension_policy.get("lmax_by_kM") != AUDIT_EXTENSION_LMAX:
        raise DomainContractError("audit-extension policy changed")
    if extension_policy.get("status") != "VALIDATION_POLICY_ONLY":
        raise DomainContractError("audit-extension policy provenance changed")
    source_identities = payload.get("source_identities")
    required_sources = {
        "accepted_uniform40_merged_npz",
        "accepted_uniform40_merged_sidecar",
        "phase6_config",
        "phase6_domain_module",
        "phase6_freeze_script",
        "uniform_source_contract_loader",
    }
    if not isinstance(source_identities, Mapping) or set(source_identities) != required_sources:
        raise DomainContractError("source identity names changed")
    for name in sorted(required_sources):
        identity = source_identities[name]
        if not isinstance(identity, Mapping) or set(identity) != {"mode", "nlink", "path", "sha256", "size"}:
            raise DomainContractError(f"source identity fields changed: {name}")
        if not isinstance(identity["path"], str) or not identity["path"]:
            raise DomainContractError(f"invalid source identity path: {name}")
        if not isinstance(identity["sha256"], str) or len(identity["sha256"]) != 64:
            raise DomainContractError(f"invalid source identity hash: {name}")
        if isinstance(identity["size"], bool) or not isinstance(identity["size"], int) or identity["size"] <= 0:
            raise DomainContractError(f"invalid source identity size: {name}")
        if not isinstance(identity["mode"], int) or identity["mode"] < 0 or identity["mode"] > 0o777:
            raise DomainContractError(f"invalid source identity mode: {name}")
        if identity["nlink"] != 1:
            raise DomainContractError(f"invalid source identity nlink: {name}")
    production_source = payload.get("production_source")
    if not isinstance(production_source, Mapping):
        raise DomainContractError("missing production source metadata")
    records = production_source.get("schedule_source_bindings")
    if not isinstance(records, list) or len(records) != 40:
        raise DomainContractError("schedule source binding cardinality changed")
    expected_lmax = [item.to_record() for item in bundle.production_lmax]
    for record, expected in zip(records, expected_lmax, strict=True):
        if not isinstance(record, Mapping):
            raise DomainContractError("invalid schedule source binding record")
        if record.get("kM") != expected["kM"] or record.get("lmax_pair") != expected["lmax_pair"]:
            raise DomainContractError("schedule source binding lmax provenance changed")
        if not isinstance(record.get("binding_source"), str) or not record["binding_source"]:
            raise DomainContractError("schedule binding source missing")
        if not isinstance(record.get("binding_source_sha256"), str) or len(record["binding_source_sha256"]) != 64:
            raise DomainContractError("schedule binding hash missing")
        resolved = record.get("resolved_source_identity")
        if not isinstance(resolved, Mapping) or set(resolved) != {"mode", "nlink", "path", "sha256", "size"}:
            raise DomainContractError("schedule binding resolved identity changed")
        if not isinstance(resolved["path"], str) or not resolved["path"]:
            raise DomainContractError("schedule binding resolved path missing")
        if not isinstance(resolved["sha256"], str) or len(resolved["sha256"]) != 64:
            raise DomainContractError("schedule binding resolved hash missing")
        if isinstance(resolved["size"], bool) or not isinstance(resolved["size"], int) or resolved["size"] <= 0:
            raise DomainContractError("schedule binding resolved size missing")
        if not isinstance(resolved["mode"], int) or resolved["mode"] < 0 or resolved["mode"] > 0o777:
            raise DomainContractError("schedule binding resolved mode missing")
        if resolved["nlink"] != 1:
            raise DomainContractError("schedule binding resolved nlink missing")
        if resolved.get("sha256") != record.get("binding_source_sha256"):
            raise DomainContractError("schedule binding hash/identity mismatch")
        if record.get("lmax_pair") != list(_rederived_lmax_pair(record)):
            raise DomainContractError("schedule binding lmax differs from source bytes")
    expected_predecessor_files = {
        "D_ext.jsonl",
        "D_prod.jsonl",
        "D_required.jsonl",
        "D_union.jsonl",
        "domain_contract.json",
        "manifest.json",
    }
    predecessors = payload.get("consumed_predecessors")
    if not isinstance(predecessors, list) or len(predecessors) < 1:
        raise DomainContractError("missing consumed predecessor provenance")
    seen_roots: set[str] = set()
    for predecessor in predecessors:
        if not isinstance(predecessor, Mapping):
            raise DomainContractError("consumed predecessor record changed")
        if predecessor.get("reason") != "PREVIOUS_FREEZE_CONSUMED_NON_AUTHORITATIVE":
            raise DomainContractError("consumed predecessor reason changed")
        if not isinstance(predecessor.get("evidence_root"), str) or not predecessor["evidence_root"]:
            raise DomainContractError("consumed predecessor root missing")
        if predecessor["evidence_root"] in seen_roots:
            raise DomainContractError("duplicate consumed predecessor root")
        seen_roots.add(predecessor["evidence_root"])
        predecessor_files = predecessor.get("file_identities")
        if not isinstance(predecessor_files, Mapping) or set(predecessor_files) != expected_predecessor_files:
            raise DomainContractError("consumed predecessor file set changed")
        for name, identity in predecessor_files.items():
            if not isinstance(identity, Mapping) or set(identity) != {"mode", "nlink", "path", "sha256", "size"}:
                raise DomainContractError(f"consumed predecessor identity fields changed: {name}")
            if not isinstance(identity["path"], str) or not identity["path"]:
                raise DomainContractError(f"consumed predecessor path missing: {name}")
            if not isinstance(identity["sha256"], str) or len(identity["sha256"]) != 64:
                raise DomainContractError(f"consumed predecessor hash missing: {name}")
            if isinstance(identity["size"], bool) or not isinstance(identity["size"], int) or identity["size"] <= 0:
                raise DomainContractError(f"consumed predecessor size missing: {name}")
            if not isinstance(identity["mode"], int) or identity["mode"] < 0 or identity["mode"] > 0o777:
                raise DomainContractError(f"consumed predecessor mode missing: {name}")
            if identity["nlink"] != 1:
                raise DomainContractError(f"consumed predecessor nlink missing: {name}")


__all__ = [
    "AUDIT_EXTENSION_LMAX",
    "AUDIT_REQUIRED_LMAX",
    "DOMAIN_SCHEMA",
    "DomainBundle",
    "DomainContractError",
    "ProductionLmax",
    "RadialKey",
    "build_v1_domain",
    "canonical_json_bytes",
    "canonical_km",
    "canonical_production_schedule",
    "contract_payload",
    "jsonl_bytes",
    "read_jsonl_keys",
    "sha256_bytes",
    "source_file_identity",
    "validate_bundle",
    "validate_contract_payload",
    "validate_ordered_unique_keys",
]
