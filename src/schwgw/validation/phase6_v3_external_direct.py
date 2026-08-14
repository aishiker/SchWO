"""Pure contracts for the Phase-6 V3.1-X external direct route.

This module contains no numerical solver entry point.  It builds and validates
the frozen Route-C graph, materializes byte-reviewed BHPT source overlays, and
derives redundant scattering quantities from independently serialized In/Up
basis values.  The Wolfram child is intentionally isolated in the companion
WLS script and the process/publication controller lives in the replacement
module.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Any, Iterable, Mapping, Sequence

import mpmath as mp


class ExternalDirectContractError(RuntimeError):
    """Fail-closed V3.1-X contract violation."""


ROOT = Path(__file__).resolve().parents[3]
GATE_ID = "phase6_v3_1_x_external_direct_route_v1"
PACKAGE_PATH = ROOT / "configs/phase6_v3_1_x_external_direct_route_package.json"
PACKAGE_SHA256 = "6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752"
DESIGN_PATH = ROOT / "docs/phase6_v3_1_x_external_direct_route_design.md"
DESIGN_SHA256 = "9a75c6f80cd8360438d395caf887a13b8c88e97faef94139c6ed4dfeba4fdb8d"
T4_PROMPT_PATH = ROOT / "docs/prompts/phase6_t4_v3_1_x_external_direct_route.md"
T4_PROMPT_SHA256 = "3c65164bcad33e7f86e993c2ec9536643cc5f2ec5c179020c923902e8caf4c4f"
T7_PACKAGE_REVIEW_PATH = (
    ROOT / "docs/handoffs/archive/"
    "T7_2026-08-13_v3_1_x_external_direct_route_package_review.md"
)
T7_PACKAGE_REVIEW_SHA256 = (
    "4ecfdbbf0df84657fb4a24d0ebb8143c4bb0b01cdc3d925b4eca4bf4df0bad50"
)
T7_PACKAGE_PROMPT_PATH = (
    ROOT / "docs/prompts/phase6_t7_v3_1_x_external_direct_route_package_review.md"
)
T7_PACKAGE_PROMPT_SHA256 = (
    "7faaab2183328b83dc5c85c82bfb5c6695ca5d028fdab7180538afa7c2c3ce5b"
)
T7_SCIENCE_PROMPT_PATH = (
    ROOT / "docs/prompts/phase6_t7_v3_1_x_external_direct_route_science_review.md"
)
T7_SCIENCE_PROMPT_SHA256 = (
    "339d5d9609e37f263ca3b3c615e5048f4059c80accc03183e02a74df6ffebd7f"
)
BHPT_SNAPSHOT_AUTHORITY = (
    ROOT / "runs/phase6/external_sources/"
    "bhpt_reggewheeler_2e012092_v1_20260813.snapshot.json"
)
BHPT_SNAPSHOT_AUTHORITY_SHA256 = (
    "8d5498ab5f825e721c6cd3764f302831c8b7bcf138a1ee9600a0f5e6f6e4e488"
)
BHPT_SNAPSHOT_ROOT = (
    ROOT / "runs/phase6/external_sources/bhpt_reggewheeler_2e012092_v1_20260813/source"
)
BHPT_CONTENT_SHA256 = "d849db67cb8f411af234f81695624868c76378e52d360acd5f65cd4d0660e6e2"
BHPT_IDENTITY_SHA256 = (
    "a1d2842d604dbd20226cc35ada71bfb49029f6b717bee33f0969f6d5bdda2f27"
)
NUMERICAL_SOURCE = BHPT_SNAPSHOT_ROOT / "Kernel/NumericalIntegration.m"
NUMERICAL_SOURCE_SHA256 = (
    "6619df2ceaa83d373152ff20740a884c8a8bd401e50c0c91a20c1d21cc879ae0"
)

CANONICAL_KEY_SHA256 = (
    "5e93fca57b6d4fb82762043fedea4631de92111164c8c4a991d76925e3867c76"
)
NODE_ORDER = ("P0", "P1", "I0", "I2", "O2", "O4", "O8")
OVERLAP_LABELS = ("0.80", "0.88", "0.96")
SELECTED_OVERLAP = "0.88"
SELECTED_NODE = "P1"
SENTINEL_FULL_LADDER_ORDINALS = (3, 22)
CERTIFICATE_IDS = (
    "V3_MODE_GREYBODY_NUMERICAL",
    "V3_MODE_GREYBODY_FLUX_VS_S",
    "V3_MODE_GREYBODY_EXTERNAL",
    "V3_MODE_PARITY_PROBABILITY",
    "V3_MODE_DOMAIN_COVERAGE",
)

OLD_RIN = b"rin=2+10^-5"
OLD_ROUT = b"rout =100*Abs[\\[Omega]]^-1;"
SNAPSHOT_DIRECTORIES = (".", "Kernel", "Kernel/MST", "Tests", "Tests/Correctness")
LOADED_SOURCE_CONTEXTS = (
    "ReggeWheeler`",
    "ReggeWheeler`MST`MST`",
    "ReggeWheeler`MST`RenormalizedAngularMomentum`",
    "ReggeWheeler`NumericalIntegration`",
    "ReggeWheeler`Hyperboloidal`",
    "ReggeWheeler`ReggeWheelerRadial`",
    "ReggeWheeler`ReggeWheelerSource`",
    "ReggeWheeler`ReggeWheelerMode`",
)
LOADED_SOURCE_PATHS = (
    "Kernel/ReggeWheeler.m",
    "Kernel/MST/MST.m",
    "Kernel/MST/RenormalizedAngularMomentum.m",
    "Kernel/NumericalIntegration.m",
    "Kernel/Hyperboloidal.wl",
    "Kernel/ReggeWheelerRadial.m",
    "Kernel/ReggeWheelerSource.m",
    "Kernel/ReggeWheelerMode.m",
)


@dataclass(frozen=True, slots=True)
class RouteCKey:
    """One immutable odd external anchor."""

    kM: str
    ell: int
    parity: str = "odd"
    anchor_id: str = "V3A-MODE-BHPT-RW-001"

    def payload(self) -> dict[str, Any]:
        return {
            "anchor_id": self.anchor_id,
            "ell": self.ell,
            "kM": self.kM,
            "parity": self.parity,
        }


@dataclass(frozen=True, slots=True)
class NodeSpec:
    """One predeclared direct-integration ladder node."""

    node_id: str
    working_precision: int
    precision_goal: int
    accuracy_goal: int
    rin_exponent: int
    outer_multiplier: int
    overlay_variant: str

    def payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class OverlayVariant:
    name: str
    rin: bytes
    rout: bytes
    sha256: str


ROUTE_C_KEYS = tuple(
    RouteCKey(k, ell)
    for k, ells in (
        ("0.1", (2, 3, 4, 8)),
        ("0.5", (2, 3, 4, 10)),
        ("1", (2, 3, 4, 5, 13)),
        ("2", (2, 3, 4, 10, 18)),
        ("4", (2, 3, 4, 20, 28)),
    )
    for ell in ells
)

NODE_SPECS = (
    NodeSpec("P0", 90, 45, 45, 10, 1, "rin10_m1"),
    NodeSpec("P1", 120, 60, 60, 10, 1, "rin10_m1"),
    NodeSpec("I0", 120, 60, 60, 8, 1, "rin8_m1"),
    NodeSpec("I2", 120, 60, 60, 12, 1, "rin12_m1"),
    NodeSpec("O2", 120, 60, 60, 10, 2, "rin10_m2"),
    NodeSpec("O4", 120, 60, 60, 10, 4, "rin10_m4"),
    NodeSpec("O8", 120, 60, 60, 10, 8, "rin10_m8"),
)

OVERLAY_VARIANTS = {
    item.name: item
    for item in (
        OverlayVariant(
            "rin8_m1",
            b"rin=2+10^-8",
            b"rout =Max[300,8 Sqrt[l(l+1)]/Abs[\\[Omega]]];",
            "ec110e7612a14fce135be77a649324a98498da04b18785502e969ec437622380",
        ),
        OverlayVariant(
            "rin10_m1",
            b"rin=2+10^-10",
            b"rout =Max[300,8 Sqrt[l(l+1)]/Abs[\\[Omega]]];",
            "a8601cd1b377bf4741035a03bec98590ebffbec0004a63af498a260f1d05c5fc",
        ),
        OverlayVariant(
            "rin12_m1",
            b"rin=2+10^-12",
            b"rout =Max[300,8 Sqrt[l(l+1)]/Abs[\\[Omega]]];",
            "574f64024363e59b2fea678f33ed3b373e73374b33efb318fe781aa5b6607958",
        ),
        OverlayVariant(
            "rin10_m2",
            b"rin=2+10^-10",
            b"rout =2 Max[300,8 Sqrt[l(l+1)]/Abs[\\[Omega]]];",
            "42369d4584fc079224d5ae9bd6e7565aafeb0a52d0d2a0f06c1666d54dbee008",
        ),
        OverlayVariant(
            "rin10_m4",
            b"rin=2+10^-10",
            b"rout =4 Max[300,8 Sqrt[l(l+1)]/Abs[\\[Omega]]];",
            "b5c7b2e496daac3f7d1edf48843b41e7633800329d528065c0f87a94db641bbf",
        ),
        OverlayVariant(
            "rin10_m8",
            b"rin=2+10^-10",
            b"rout =8 Max[300,8 Sqrt[l(l+1)]/Abs[\\[Omega]]];",
            "8bdf36d3bba5dc2ffa6e4949dffcd15d42a90acba9c0f9cf431fa8c30e71ffd5",
        ),
    )
}

ROUTE_ADMISSION = {
    "external_precision_log_gamma_absolute_change_max": mp.mpf("0.0001"),
    "external_precision_s_symmetric_relative_change_max": mp.mpf("5e-7"),
    "external_rin_log_gamma_absolute_change_max": mp.mpf("0.0002"),
    "external_rin_s_symmetric_relative_change_max": mp.mpf("1e-6"),
    "external_rout_log_gamma_absolute_change_max": mp.mpf("0.0003"),
    "external_rout_s_symmetric_relative_change_max": mp.mpf("2e-6"),
    "per_node_signed_current_balance_absolute_max": mp.mpf("1e-8"),
    "three_overlap_log_gamma_absolute_spread_max": mp.mpf("0.0002"),
    "three_overlap_s_symmetric_relative_spread_max": mp.mpf("2e-6"),
}
DIRECT_GAMMA_ABSOLUTE_LIMIT = mp.mpf("2e-8")
DIRECT_GAMMA_LOG_LIMIT = mp.mpf("2e-4")
GAMMA_PHYSICAL_LIMIT = mp.mpf("2e-10")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode()


def compact_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def compact_jsonl_record(payload: Mapping[str, Any]) -> bytes:
    return compact_bytes(payload) + b"\n"


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise ExternalDirectContractError(f"noncanonical JSON: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise ExternalDirectContractError("torn JSONL tail")
    result: list[dict[str, Any]] = []
    for line in raw.splitlines():
        item = json.loads(line)
        if not isinstance(item, dict) or compact_bytes(item) != line:
            raise ExternalDirectContractError("noncanonical JSONL record")
        result.append(item)
    return result


def route_c_inventory() -> list[dict[str, Any]]:
    payload = [item.payload() for item in ROUTE_C_KEYS]
    if hashlib.sha256(compact_bytes(payload)).hexdigest() != CANONICAL_KEY_SHA256:
        raise ExternalDirectContractError("Route-C key inventory identity drift")
    return payload


def official_plan() -> list[dict[str, Any]]:
    result = []
    for key_ordinal, key in enumerate(ROUTE_C_KEYS):
        for node_ordinal, node in enumerate(NODE_SPECS):
            result.append(
                {
                    "call_ordinal": len(result),
                    "key_ordinal": key_ordinal,
                    "key": key.payload(),
                    "node_ordinal": node_ordinal,
                    "node": node.payload(),
                }
            )
    if len(result) != 161:
        raise ExternalDirectContractError("official graph cardinality drift")
    return result


def sentinel_plan() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    selected = NODE_SPECS[1]
    for key_ordinal, key in enumerate(ROUTE_C_KEYS):
        result.append(
            {
                "call_ordinal": len(result),
                "key_ordinal": key_ordinal,
                "key": key.payload(),
                "node_ordinal": 1,
                "node": selected.payload(),
            }
        )
    for key_ordinal in SENTINEL_FULL_LADDER_ORDINALS:
        for node_ordinal, node in enumerate(NODE_SPECS):
            if node.node_id == SELECTED_NODE:
                continue
            result.append(
                {
                    "call_ordinal": len(result),
                    "key_ordinal": key_ordinal,
                    "key": ROUTE_C_KEYS[key_ordinal].payload(),
                    "node_ordinal": node_ordinal,
                    "node": node.payload(),
                }
            )
    if len(result) != 35:
        raise ExternalDirectContractError("sentinel graph cardinality drift")
    return result


def expected_graph(stage: str) -> list[dict[str, Any]]:
    if stage == "sentinel":
        return sentinel_plan()
    if stage == "official":
        return official_plan()
    raise ExternalDirectContractError("unknown execution stage")


def exact_frequency_fraction(label: str) -> tuple[int, int]:
    mapping = {"0.1": (1, 10), "0.5": (1, 2), "1": (1, 1), "2": (2, 1), "4": (4, 1)}
    try:
        return mapping[label]
    except KeyError as exc:
        raise ExternalDirectContractError("unfrozen frequency label") from exc


def outer_radius(key: Mapping[str, Any], node: Mapping[str, Any]) -> mp.mpf:
    k = mp.mpf(str(key["kM"]))
    ell = int(key["ell"])
    multiplier = int(node["outer_multiplier"])
    return multiplier * max(mp.mpf(300), 8 * mp.sqrt(ell * (ell + 1)) / k)


def overlap_radii(
    key: Mapping[str, Any], node: Mapping[str, Any]
) -> tuple[mp.mpf, ...]:
    r_out = outer_radius(key, node)
    return tuple(r_out * mp.mpf(label) for label in OVERLAP_LABELS)


def _snapshot_content_records(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        info = path.stat()
        if path.is_symlink() or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ExternalDirectContractError("snapshot file/link drift")
        records.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": sha256(path),
                "size": info.st_size,
            }
        )
    return records


def _snapshot_identity_records(root: Path) -> list[dict[str, Any]]:
    """Return the frozen five-field source identity index, never inode data."""

    records: list[dict[str, Any]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        info = path.stat()
        if path.is_symlink() or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ExternalDirectContractError("snapshot file/link drift")
        if stat.S_IMODE(info.st_mode) != 0o444:
            raise ExternalDirectContractError("snapshot file mode drift")
        records.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": sha256(path),
                "size": info.st_size,
                "mode": stat.S_IMODE(info.st_mode),
                "nlink": info.st_nlink,
            }
        )
    return records


def base_snapshot_identity(root: Path = BHPT_SNAPSHOT_ROOT) -> dict[str, Any]:
    """Rebuild the frozen 25-file/five-directory BHPT snapshot closure."""

    root = root.resolve(strict=True)
    if root.is_symlink():
        raise ExternalDirectContractError("snapshot root symlink")
    paths = [root, *root.rglob("*")]
    if any(path.is_symlink() for path in paths):
        raise ExternalDirectContractError("snapshot symlink")
    if any(not path.is_file() and not path.is_dir() for path in paths):
        raise ExternalDirectContractError("snapshot special file")
    directories = sorted(
        "." if path == root else path.relative_to(root).as_posix()
        for path in paths
        if path.is_dir()
    )
    if directories != sorted(SNAPSHOT_DIRECTORIES):
        raise ExternalDirectContractError("snapshot directory inventory drift")
    for relative in SNAPSHOT_DIRECTORIES:
        directory = root if relative == "." else root / relative
        if stat.S_IMODE(directory.stat().st_mode) != 0o555:
            raise ExternalDirectContractError("snapshot directory mode drift")
    content_records = _snapshot_content_records(root)
    identity_records = _snapshot_identity_records(root)
    if len(content_records) != 25 or [item["path"] for item in content_records] != [
        item["path"] for item in identity_records
    ]:
        raise ExternalDirectContractError("snapshot file inventory drift")
    authority = json.loads(BHPT_SNAPSHOT_AUTHORITY.read_text())
    if authority.get("source_content_records") != content_records:
        raise ExternalDirectContractError("snapshot authority content drift")
    if root == BHPT_SNAPSHOT_ROOT.resolve() and (
        hashlib.sha256(canonical_bytes_list(content_records)).hexdigest()
        != BHPT_CONTENT_SHA256
        or hashlib.sha256(canonical_bytes_list(identity_records)).hexdigest()
        != BHPT_IDENTITY_SHA256
    ):
        raise ExternalDirectContractError("base BHPT snapshot identity drift")
    return {
        "schema": "schwo.phase6.v3_1_x.bhpt_snapshot_identity.v1",
        "root": str(root),
        "content_records": content_records,
        "identity_records": identity_records,
        "content_inventory_sha256": hashlib.sha256(
            canonical_bytes_list(content_records)
        ).hexdigest(),
        "identity_inventory_sha256": hashlib.sha256(
            canonical_bytes_list(identity_records)
        ).hexdigest(),
        "directory_paths": list(SNAPSHOT_DIRECTORIES),
    }


def validate_base_snapshot(root: Path = BHPT_SNAPSHOT_ROOT) -> list[dict[str, Any]]:
    return list(base_snapshot_identity(root)["content_records"])


def canonical_bytes_list(payload: Sequence[Mapping[str, Any]]) -> bytes:
    return (json.dumps(list(payload), sort_keys=True, indent=2) + "\n").encode()


def transformed_numerical_source(base: bytes, variant_name: str) -> bytes:
    try:
        variant = OVERLAY_VARIANTS[variant_name]
    except KeyError as exc:
        raise ExternalDirectContractError("unknown overlay variant") from exc
    if base.count(OLD_RIN) != 2 or base.count(OLD_ROUT) != 2:
        raise ExternalDirectContractError("reviewed overlay occurrence count drift")
    transformed = base.replace(OLD_RIN, variant.rin, 1).replace(
        OLD_ROUT, variant.rout, 1
    )
    if (
        transformed.count(OLD_RIN) != 1
        or transformed.count(OLD_ROUT) != 1
        or transformed.count(variant.rin) != 1
        or transformed.count(variant.rout) != 1
        or hashlib.sha256(transformed).hexdigest() != variant.sha256
    ):
        raise ExternalDirectContractError("overlay transformed identity drift")
    return transformed


def _exclusive_file(path: Path, data: bytes, *, mode: int = 0o444) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "wb", closefd=False) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.fchmod(fd, mode)
        os.fsync(fd)
    finally:
        os.close(fd)


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def materialize_overlay(
    base_root: Path, output_root: Path, variant_name: str
) -> dict[str, Any]:
    """Exclusively copy the 25-file snapshot and apply one reviewed variant."""

    base_root = base_root.resolve(strict=True)
    base_records = validate_base_snapshot(base_root)
    output_root.mkdir(mode=0o700, parents=False, exist_ok=False)
    directories = sorted(
        [item for item in base_root.rglob("*") if item.is_dir()],
        key=lambda item: (len(item.parts), item.as_posix()),
    )
    for source in directories:
        if source.is_symlink():
            raise ExternalDirectContractError("snapshot directory symlink")
        (output_root / source.relative_to(base_root)).mkdir(mode=0o700)
    numerical_relative = Path("Kernel/NumericalIntegration.m")
    for record in base_records:
        relative = Path(record["path"])
        data = (base_root / relative).read_bytes()
        if relative == numerical_relative:
            data = transformed_numerical_source(data, variant_name)
        _exclusive_file(output_root / relative, data)
    for directory in reversed(
        [output_root, *[item for item in output_root.rglob("*") if item.is_dir()]]
    ):
        os.chmod(directory, 0o555)
        _fsync_directory(directory)
    _fsync_directory(output_root.parent)
    return validate_overlay(output_root, variant_name, base_records=base_records)


def validate_overlay(
    root: Path,
    variant_name: str,
    *,
    base_records: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    root = root.resolve(strict=True)
    variant = OVERLAY_VARIANTS.get(variant_name)
    if variant is None:
        raise ExternalDirectContractError("unknown overlay variant")
    expected = list(base_records or validate_base_snapshot())
    actual = _snapshot_content_records(root)
    if len(actual) != 25 or [x["path"] for x in actual] != [
        x["path"] for x in expected
    ]:
        raise ExternalDirectContractError("overlay inventory drift")
    for item, base in zip(actual, expected, strict=True):
        expected_hash = (
            variant.sha256
            if item["path"] == "Kernel/NumericalIntegration.m"
            else base["sha256"]
        )
        if item["sha256"] != expected_hash or (
            item["path"] != "Kernel/NumericalIntegration.m"
            and item["size"] != base["size"]
        ):
            raise ExternalDirectContractError(f"overlay byte drift: {item['path']}")
    all_paths = [root, *root.rglob("*")]
    directories = sorted(
        "." if path == root else path.relative_to(root).as_posix()
        for path in all_paths
        if path.is_dir()
    )
    if directories != sorted(SNAPSHOT_DIRECTORIES):
        raise ExternalDirectContractError("overlay directory inventory drift")
    for path in all_paths:
        info = path.stat()
        if path.is_symlink() or (path.is_file() and info.st_nlink != 1):
            raise ExternalDirectContractError("overlay link drift")
        expected_mode = 0o555 if path.is_dir() else 0o444
        if stat.S_IMODE(info.st_mode) != expected_mode:
            raise ExternalDirectContractError("overlay mode drift")
    identity_records = _snapshot_identity_records(root)
    return {
        "schema": "schwo.phase6.v3_1_x.overlay_identity.v1",
        "variant": variant_name,
        "root": str(root),
        "file_count": 25,
        "numerical_source_sha256": variant.sha256,
        "records": actual,
        "content_sha256": hashlib.sha256(canonical_bytes_list(actual)).hexdigest(),
        "identity_records": identity_records,
        "identity_sha256": hashlib.sha256(
            canonical_bytes_list(identity_records)
        ).hexdigest(),
        "base_content_sha256": BHPT_CONTENT_SHA256,
        "source_bytes_modified": 1,
        "old_odd_occurrence_replaced": True,
        "even_occurrence_unchanged": True,
    }


def _strict_keys(value: Mapping[str, Any], expected: Iterable[str], label: str) -> None:
    if set(value) != set(expected):
        raise ExternalDirectContractError(f"{label} schema mismatch")


def _mp_real(value: Any, label: str) -> mp.mpf:
    if not isinstance(value, str) or not value or len(value) > 1000:
        raise ExternalDirectContractError(f"{label} is not a canonical decimal string")
    try:
        result = mp.mpf(value)
    except (ValueError, TypeError) as exc:
        raise ExternalDirectContractError(f"{label} is not numeric") from exc
    if not mp.isfinite(result):
        raise ExternalDirectContractError(f"{label} is nonfinite")
    return result


def _decimal_significant_digits(value: str, label: str) -> int:
    """Count canonical nonzero decimal digits without accepting zero padding."""

    match = re.fullmatch(r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:e[+-]?\d+)?", value)
    if match is None:
        raise ExternalDirectContractError(f"{label} decimal syntax is noncanonical")
    raw_mantissa = value.split("e", maxsplit=1)[0]
    if "." in raw_mantissa and raw_mantissa.endswith("0"):
        raise ExternalDirectContractError(f"{label} decimal has padded trailing zero")
    mantissa = raw_mantissa.lstrip("-").replace(".", "")
    significant = mantissa.lstrip("0")
    if not significant:
        raise ExternalDirectContractError(f"{label} nonexact value has no digits")
    return len(significant)


def _raw_real(value: Any, label: str, node: Mapping[str, Any]) -> mp.mpf:
    """Validate one WLS scalar plus its non-forgeable precision witness."""

    if not isinstance(value, Mapping):
        raise ExternalDirectContractError(f"{label} precision witness missing")
    _strict_keys(
        value,
        (
            "decimal",
            "exact_zero",
            "source_precision_digits",
            "source_accuracy_digits",
            "serialized_significant_digits",
        ),
        label,
    )
    decimal = value["decimal"]
    exact_zero = value["exact_zero"]
    if not isinstance(decimal, str) or not isinstance(exact_zero, bool):
        raise ExternalDirectContractError(f"{label} precision witness type mismatch")
    if exact_zero:
        if (
            decimal != "0"
            or value["source_precision_digits"] is not None
            or value["source_accuracy_digits"] is not None
            or value["serialized_significant_digits"] != 0
        ):
            raise ExternalDirectContractError(f"{label} exact-zero witness mismatch")
        return mp.mpf(0)
    decimal_digits = _decimal_significant_digits(decimal, label)
    precision = value["source_precision_digits"]
    accuracy = value["source_accuracy_digits"]
    serialized = value["serialized_significant_digits"]
    if (
        not isinstance(precision, int)
        or not isinstance(accuracy, int)
        or not isinstance(serialized, int)
        or precision < int(node["working_precision"])
        or accuracy < int(node["accuracy_goal"])
        or serialized != decimal_digits
        or serialized < int(node["precision_goal"])
    ):
        raise ExternalDirectContractError(f"{label} precision witness insufficient")
    result = _mp_real(decimal, label)
    if result == 0:
        raise ExternalDirectContractError(f"{label} nonexact zero witness")
    return result


def _mp_complex(value: Any, label: str) -> mp.mpc:
    if not isinstance(value, Mapping):
        raise ExternalDirectContractError(f"{label} complex record missing")
    _strict_keys(value, ("real", "imag"), label)
    return mp.mpc(
        _mp_real(value["real"], f"{label}.real"),
        _mp_real(value["imag"], f"{label}.imag"),
    )


def _raw_complex(value: Any, label: str, node: Mapping[str, Any]) -> mp.mpc:
    if not isinstance(value, Mapping):
        raise ExternalDirectContractError(f"{label} complex witness missing")
    _strict_keys(value, ("real", "imag"), label)
    return mp.mpc(
        _raw_real(value["real"], f"{label}.real", node),
        _raw_real(value["imag"], f"{label}.imag", node),
    )


def _validate_loaded_source_records(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) != len(LOADED_SOURCE_PATHS):
        raise ExternalDirectContractError(f"{label} loaded source cardinality mismatch")
    records: list[dict[str, Any]] = []
    for item, context, path in zip(
        value, LOADED_SOURCE_CONTEXTS, LOADED_SOURCE_PATHS, strict=True
    ):
        if not isinstance(item, Mapping):
            raise ExternalDirectContractError(f"{label} loaded source type mismatch")
        _strict_keys(
            item, ("context", "path", "sha256", "size", "mode", "nlink"), label
        )
        if (
            item["context"] != context
            or item["path"] != path
            or not isinstance(item["sha256"], str)
            or len(item["sha256"]) != 64
            or not isinstance(item["size"], int)
            or item["size"] <= 0
            or item["mode"] != 0o444
            or item["nlink"] != 1
        ):
            raise ExternalDirectContractError(
                f"{label} loaded source order/identity mismatch"
            )
        records.append(dict(item))
    return records


def validate_loaded_source_boundaries(
    raw: Mapping[str, Any], expected_records: Sequence[Mapping[str, Any]] | None
) -> list[dict[str, Any]]:
    """Bind observed WLS contexts/files to the reviewed overlay request."""

    start = _validate_loaded_source_records(raw["loaded_source_start"], "start")
    end = _validate_loaded_source_records(raw["loaded_source_end"], "end")
    if raw["loaded_contexts_start"] != list(LOADED_SOURCE_CONTEXTS) or raw[
        "loaded_contexts_end"
    ] != list(LOADED_SOURCE_CONTEXTS):
        raise ExternalDirectContractError("actual loaded context inventory mismatch")
    if start != end:
        raise ExternalDirectContractError("loaded source start/end drift")
    if expected_records is not None:
        expected = list(expected_records)
        if len(expected) != len(LOADED_SOURCE_PATHS):
            raise ExternalDirectContractError(
                "request loaded-source cardinality mismatch"
            )
        projection = [
            {
                "context": context,
                "path": item.get("path"),
                "sha256": item.get("sha256"),
                "size": item.get("size"),
                "mode": item.get("mode"),
                "nlink": item.get("nlink"),
            }
            for context, item in zip(LOADED_SOURCE_CONTEXTS, expected, strict=True)
        ]
        if start != projection:
            raise ExternalDirectContractError("actual loaded source/request mismatch")
    return start


def mp_string(value: mp.mpf | mp.mpc, digits: int = 90) -> str | dict[str, str]:
    if isinstance(value, mp.mpc):
        return {
            "real": mp.nstr(value.real, digits),
            "imag": mp.nstr(value.imag, digits),
        }
    return mp.nstr(value, digits)


def _symrel(left: mp.mpc, right: mp.mpc) -> mp.mpf:
    scale = abs(left) + abs(right)
    return mp.mpf(0) if scale == 0 else 2 * abs(left - right) / scale


def derive_node_record(
    raw: Mapping[str, Any],
    expected: Mapping[str, Any],
    *,
    expected_loaded_sources: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Validate one minimal WLS payload and derive all redundant observables."""

    expected_fields = {
        "schema",
        "call_ordinal",
        "key_ordinal",
        "key",
        "node_ordinal",
        "node",
        "method",
        "potential",
        "boundary_conditions",
        "frequency",
        "external_api_call_count",
        "external_boundary_solution_count",
        "mst_call_count",
        "internal_solver_call_count",
        "overlay",
        "overlaps",
        "loaded_contexts_start",
        "loaded_contexts_end",
        "loaded_source_start",
        "loaded_source_end",
        "runtime",
    }
    _strict_keys(raw, expected_fields, "raw node")
    if (
        raw["schema"] != "schwo.phase6.v3_1_x.external_direct_raw_node.v1"
        or raw["call_ordinal"] != expected["call_ordinal"]
        or raw["key_ordinal"] != expected["key_ordinal"]
        or raw["key"] != expected["key"]
        or raw["node_ordinal"] != expected["node_ordinal"]
        or raw["node"] != expected["node"]
        or raw["method"] != "NumericalIntegration"
        or raw["potential"] != "ReggeWheeler"
        or raw["boundary_conditions"] != ["In", "Up"]
        or raw["external_api_call_count"] != 1
        or raw["external_boundary_solution_count"] != 2
        or raw["mst_call_count"] != 0
        or raw["internal_solver_call_count"] != 0
    ):
        raise ExternalDirectContractError("raw node identity/method drift")
    numerator, denominator = exact_frequency_fraction(expected["key"]["kM"])
    frequency = raw["frequency"]
    _strict_keys(
        frequency,
        ("label", "exact_numerator", "exact_denominator", "input_precision_digits"),
        "frequency",
    )
    if (
        frequency["label"] != expected["key"]["kM"]
        or frequency["exact_numerator"] != numerator
        or frequency["exact_denominator"] != denominator
        or not isinstance(frequency["input_precision_digits"], int)
        or frequency["input_precision_digits"]
        < expected["node"]["working_precision"] + 10
    ):
        raise ExternalDirectContractError("machine/imprecise frequency input")
    overlay = raw["overlay"]
    if (
        not isinstance(overlay, Mapping)
        or overlay.get("variant") != expected["node"]["overlay_variant"]
        or overlay.get("numerical_source_sha256")
        != OVERLAY_VARIANTS[expected["node"]["overlay_variant"]].sha256
    ):
        raise ExternalDirectContractError("node overlay binding mismatch")
    loaded_sources = validate_loaded_source_boundaries(raw, expected_loaded_sources)
    overlaps = raw["overlaps"]
    if not isinstance(overlaps, list) or len(overlaps) != 3:
        raise ExternalDirectContractError("overlap cardinality mismatch")
    digits = int(expected["node"]["working_precision"])
    key = expected["key"]
    k = mp.mpf(key["kM"])
    expected_radii = overlap_radii(key, expected["node"])
    derived: list[dict[str, Any]] = []
    with mp.workdps(digits + 30):
        for index, (item, label, expected_radius) in enumerate(
            zip(overlaps, OVERLAP_LABELS, expected_radii, strict=True)
        ):
            _strict_keys(
                item, ("fraction", "radius_M", "H", "Hdot", "U", "Udot"), "overlap"
            )
            radius = _raw_real(item["radius_M"], "radius_M", expected["node"])
            if item["fraction"] != label or abs(radius - expected_radius) > abs(
                expected_radius
            ) * mp.mpf(10) ** (-(digits - 10)):
                raise ExternalDirectContractError("overlap radius/order mismatch")
            h = _raw_complex(item["H"], "H", expected["node"])
            hdot = _raw_complex(item["Hdot"], "Hdot", expected["node"])
            up = _raw_complex(item["U"], "U", expected["node"])
            updot = _raw_complex(item["Udot"], "Udot", expected["node"])
            incoming = mp.conj(up)
            incoming_dot = mp.conj(updot)
            term_left = incoming * updot
            term_right = up * incoming_dot
            determinant = term_left - term_right
            determinant_scale = abs(term_left) + abs(term_right)
            if determinant == 0 or determinant_scale == 0:
                raise ExternalDirectContractError("zero overlap determinant")
            relative_determinant = abs(determinant) / determinant_scale
            if relative_determinant <= mp.power(
                10, -int(expected["node"]["precision_goal"])
            ):
                raise ExternalDirectContractError("unresolved overlap determinant")
            a_in = (h * updot - up * hdot) / determinant
            a_out = (incoming * hdot - h * incoming_dot) / determinant
            if a_in == 0:
                raise ExternalDirectContractError("zero incoming amplitude")
            s_value = mp.power(-1, int(key["ell"]) + 1) * a_out / a_in
            gamma_flux = 1 / abs(a_in) ** 2
            gamma_s = 1 - abs(s_value) ** 2
            if gamma_flux <= 0 or gamma_s <= 0:
                raise ExternalDirectContractError("nonpositive Gamma")
            h_current = mp.im(mp.conj(h) * hdot)
            up_current = mp.im(mp.conj(up) * updot)
            f_inf_in = k * abs(a_in) ** 2
            f_inf_out = k * abs(a_out) ** 2
            f_h = k
            raw_balance = f_inf_in - f_inf_out - f_h
            balance = raw_balance / f_inf_in
            derived.append(
                {
                    "schema": "schwo.phase6.v3_1_x.external_direct_overlap.v1",
                    "overlap_ordinal": index,
                    "fraction": label,
                    "radius_M": mp_string(radius, digits),
                    "H": mp_string(h, digits),
                    "Hdot": mp_string(hdot, digits),
                    "U": mp_string(up, digits),
                    "Udot": mp_string(updot, digits),
                    "D": mp_string(determinant, digits),
                    "relative_determinant": mp_string(relative_determinant, digits),
                    "A_in_horizon_normalized": mp_string(a_in, digits),
                    "A_out_horizon_normalized": mp_string(a_out, digits),
                    "A_H_horizon_normalized": {"real": "1.0", "imag": "0.0"},
                    "S": mp_string(s_value, digits),
                    "Gamma_flux": mp_string(gamma_flux, digits),
                    "Gamma_S": mp_string(gamma_s, digits),
                    "log_Gamma_flux": mp_string(mp.log(gamma_flux), digits),
                    "log_Gamma_S": mp_string(mp.log(gamma_s), digits),
                    "signed_currents": {
                        "H": mp_string(h_current, digits),
                        "Up": mp_string(up_current, digits),
                    },
                    "positive_fluxes": {
                        "F_inf_in": mp_string(f_inf_in, digits),
                        "F_inf_out": mp_string(f_inf_out, digits),
                        "F_H": mp_string(f_h, digits),
                    },
                    "signed_current_balance": mp_string(balance, digits),
                    "signed_current_balance_raw": mp_string(raw_balance, digits),
                }
            )
    return {
        "schema": "schwo.phase6.v3_1_x.external_direct_node.v1",
        "call_ordinal": expected["call_ordinal"],
        "key_ordinal": expected["key_ordinal"],
        "key": dict(key),
        "node_ordinal": expected["node_ordinal"],
        "node": dict(expected["node"]),
        "method": "NumericalIntegration",
        "potential": "ReggeWheeler",
        "boundary_conditions": ["In", "Up"],
        "external_api_call_count": 1,
        "external_boundary_solution_count": 2,
        "mst_call_count": 0,
        "internal_solver_call_count": 0,
        "overlaps": derived,
        "selected_overlap_ordinal": 1,
        "overlay": dict(overlay),
        "loaded_source_identity": loaded_sources,
        "loaded_contexts": list(LOADED_SOURCE_CONTEXTS),
        "runtime": raw["runtime"],
        "numerical_budget": {"status": "COMPUTED_NOT_YET_AGGREGATED"},
        "convention_budget": {
            "status": "FROZEN",
            "fourier_sign": "exp(-i omega t)",
            "tortoise": "r_star=r+2 log(r/2-1), M=1",
            "potential": "ReggeWheeler odd",
            "boundary_normalization": "In/Up unit transmission",
            "current_orientation": "F_inf_in-F_inf_out-F_H=0",
            "v3_f02": "S=(-1)^(ell+1) A_out/A_in",
            "phase_or_normalization_fit": False,
        },
    }


def validate_node_records(records: Sequence[Mapping[str, Any]], stage: str) -> None:
    plan = expected_graph(stage)
    if len(records) != len(plan):
        raise ExternalDirectContractError("node record totality mismatch")
    for record, expected in zip(records, plan, strict=True):
        if (
            record.get("call_ordinal") != expected["call_ordinal"]
            or record.get("key_ordinal") != expected["key_ordinal"]
            or record.get("key") != expected["key"]
            or record.get("node_ordinal") != expected["node_ordinal"]
            or record.get("node") != expected["node"]
            or record.get("external_api_call_count") != 1
            or record.get("external_boundary_solution_count") != 2
            or record.get("mst_call_count") != 0
            or record.get("internal_solver_call_count") != 0
            or len(record.get("overlaps", ())) != 3
            or record.get("numerical_budget") == record.get("convention_budget")
        ):
            raise ExternalDirectContractError("node record order/schema drift")


def _selected(record: Mapping[str, Any]) -> Mapping[str, Any]:
    return record["overlaps"][1]


def _record_observables(record: Mapping[str, Any]) -> tuple[mp.mpc, mp.mpf]:
    selected = _selected(record)
    return _mp_complex(selected["S"], "S"), _mp_real(
        selected["Gamma_flux"], "Gamma_flux"
    )


def aggregate_key_records(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if len(records) != 7 or [item["node"]["node_id"] for item in records] != list(
        NODE_ORDER
    ):
        raise ExternalDirectContractError("key ladder order/totality mismatch")
    if len({json.dumps(item["key"], sort_keys=True) for item in records}) != 1:
        raise ExternalDirectContractError("cross-key ladder")
    values = {item["node"]["node_id"]: _record_observables(item) for item in records}

    def pair(left: str, right: str) -> tuple[mp.mpf, mp.mpf]:
        ls, lg = values[left]
        rs, rg = values[right]
        return _symrel(ls, rs), abs(mp.log(lg) - mp.log(rg))

    precision = pair("P0", "P1")
    inner_pairs = (pair("I0", "P1"), pair("P1", "I2"))
    outer_pairs = (pair("P1", "O2"), pair("O2", "O4"), pair("O4", "O8"))
    inner = tuple(max(item[index] for item in inner_pairs) for index in (0, 1))
    outer = tuple(max(item[index] for item in outer_pairs) for index in (0, 1))
    overlap_s: list[mp.mpf] = []
    overlap_log: list[mp.mpf] = []
    balance: list[mp.mpf] = []
    route_sep: list[mp.mpf] = []
    route_abs: list[mp.mpf] = []
    physical_violation: list[mp.mpf] = []
    for record in records:
        overlaps = record["overlaps"]
        s_values = [_mp_complex(item["S"], "S") for item in overlaps]
        gamma_values = [_mp_real(item["Gamma_flux"], "Gamma_flux") for item in overlaps]
        overlap_s.append(max(_symrel(a, b) for a in s_values for b in s_values))
        overlap_log.append(
            max(abs(mp.log(a) - mp.log(b)) for a in gamma_values for b in gamma_values)
        )
        balance.extend(
            abs(_mp_real(item["signed_current_balance"], "balance"))
            for item in overlaps
        )
        route_sep.extend(
            abs(
                mp.log(_mp_real(item["Gamma_flux"], "gf"))
                - mp.log(_mp_real(item["Gamma_S"], "gs"))
            )
            for item in overlaps
        )
        route_abs.extend(
            abs(_mp_real(item["Gamma_flux"], "gf") - _mp_real(item["Gamma_S"], "gs"))
            for item in overlaps
        )
        physical_violation.extend(
            max(
                mp.mpf(0),
                -_mp_real(item[field], field),
                _mp_real(item[field], field) - 1,
            )
            for item in overlaps
            for field in ("Gamma_flux", "Gamma_S")
        )
    metrics = {
        "precision_s": precision[0],
        "precision_log_gamma": precision[1],
        "rin_s": inner[0],
        "rin_log_gamma": inner[1],
        "rout_s": outer[0],
        "rout_log_gamma": outer[1],
        "overlap_s": max(overlap_s),
        "overlap_log_gamma": max(overlap_log),
        "signed_current_balance": max(balance),
        "direct_flux_vs_s_log": max(route_sep),
        "direct_flux_vs_s_abs": max(route_abs),
        "gamma_physical_violation": max(physical_violation),
    }
    gates = {
        "precision_s": metrics["precision_s"]
        <= ROUTE_ADMISSION["external_precision_s_symmetric_relative_change_max"],
        "precision_log_gamma": metrics["precision_log_gamma"]
        <= ROUTE_ADMISSION["external_precision_log_gamma_absolute_change_max"],
        "rin_s": metrics["rin_s"]
        <= ROUTE_ADMISSION["external_rin_s_symmetric_relative_change_max"],
        "rin_log_gamma": metrics["rin_log_gamma"]
        <= ROUTE_ADMISSION["external_rin_log_gamma_absolute_change_max"],
        "rout_s": metrics["rout_s"]
        <= ROUTE_ADMISSION["external_rout_s_symmetric_relative_change_max"],
        "rout_log_gamma": metrics["rout_log_gamma"]
        <= ROUTE_ADMISSION["external_rout_log_gamma_absolute_change_max"],
        "overlap_s": metrics["overlap_s"]
        <= ROUTE_ADMISSION["three_overlap_s_symmetric_relative_spread_max"],
        "overlap_log_gamma": metrics["overlap_log_gamma"]
        <= ROUTE_ADMISSION["three_overlap_log_gamma_absolute_spread_max"],
        "signed_current_balance": metrics["signed_current_balance"]
        <= ROUTE_ADMISSION["per_node_signed_current_balance_absolute_max"],
        "gamma_physical": metrics["gamma_physical_violation"] <= GAMMA_PHYSICAL_LIMIT,
        "direct_flux_vs_s": all(
            (
                abs(
                    _mp_real(item["Gamma_flux"], "gf") - _mp_real(item["Gamma_S"], "gs")
                )
                <= DIRECT_GAMMA_ABSOLUTE_LIMIT
                if _mp_real(item["Gamma_flux"], "gf") >= mp.mpf("1e-8")
                else abs(
                    mp.log(_mp_real(item["Gamma_flux"], "gf"))
                    - mp.log(_mp_real(item["Gamma_S"], "gs"))
                )
                <= DIRECT_GAMMA_LOG_LIMIT
            )
            for record in records
            for item in record["overlaps"]
        ),
    }
    return {
        "schema": "schwo.phase6.v3_1_x.external_direct_key_budget.v1",
        "key": records[0]["key"],
        "selected_node": SELECTED_NODE,
        "selected_overlap": SELECTED_OVERLAP,
        "numerical_budget": {
            "metrics": {key: mp.nstr(value, 90) for key, value in metrics.items()},
            "gates": gates,
            "status": "PASS" if all(gates.values()) else "FAIL",
            "conservative_uncertainty_is_axis_max": True,
        },
        "convention_budget": records[0]["convention_budget"],
    }


def node_admission_budget(record: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate every criterion applicable to a single sentinel node."""

    overlaps = record.get("overlaps")
    if not isinstance(overlaps, list) or len(overlaps) != 3:
        raise ExternalDirectContractError("sentinel node overlap cardinality mismatch")
    s_values = [_mp_complex(item["S"], "S") for item in overlaps]
    gamma_flux = [_mp_real(item["Gamma_flux"], "Gamma_flux") for item in overlaps]
    gamma_s = [_mp_real(item["Gamma_S"], "Gamma_S") for item in overlaps]
    overlap_s = max(_symrel(left, right) for left in s_values for right in s_values)
    overlap_log = max(
        abs(mp.log(left) - mp.log(right)) for left in gamma_flux for right in gamma_flux
    )
    balance = max(
        abs(_mp_real(item["signed_current_balance"], "signed_current_balance"))
        for item in overlaps
    )
    direct_abs = max(
        abs(left - right) for left, right in zip(gamma_flux, gamma_s, strict=True)
    )
    direct_log = max(
        abs(mp.log(left) - mp.log(right))
        for left, right in zip(gamma_flux, gamma_s, strict=True)
    )
    physical = max(
        max(mp.mpf(0), -value, value - 1) for value in [*gamma_flux, *gamma_s]
    )
    route_gate = all(
        abs(left - right) <= DIRECT_GAMMA_ABSOLUTE_LIMIT
        if left >= mp.mpf("1e-8")
        else abs(mp.log(left) - mp.log(right)) <= DIRECT_GAMMA_LOG_LIMIT
        for left, right in zip(gamma_flux, gamma_s, strict=True)
    )
    metrics = {
        "three_overlap_s": overlap_s,
        "three_overlap_log_gamma": overlap_log,
        "signed_current_balance": balance,
        "direct_gamma_absolute": direct_abs,
        "direct_gamma_log": direct_log,
        "gamma_physical_violation": physical,
    }
    gates = {
        "three_overlap_s": overlap_s
        <= ROUTE_ADMISSION["three_overlap_s_symmetric_relative_spread_max"],
        "three_overlap_log_gamma": overlap_log
        <= ROUTE_ADMISSION["three_overlap_log_gamma_absolute_spread_max"],
        "signed_current_balance": balance
        <= ROUTE_ADMISSION["per_node_signed_current_balance_absolute_max"],
        "direct_gamma_route": route_gate,
        "gamma_physical": physical <= GAMMA_PHYSICAL_LIMIT,
    }
    return {
        "schema": "schwo.phase6.v3_1_x.external_direct_node_admission.v1",
        "call_ordinal": record["call_ordinal"],
        "key_ordinal": record["key_ordinal"],
        "key": record["key"],
        "node": record["node"],
        "metrics": {key: mp.nstr(value, 90) for key, value in metrics.items()},
        "gates": gates,
        "status": "PASS" if all(gates.values()) else "FAIL",
    }


def build_sentinel_budgets(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Close every sentinel node and the two fixed-extrema full ladders."""

    validate_node_records(records, "sentinel")
    node_budgets = [node_admission_budget(record) for record in records]
    full_ladders: list[dict[str, Any]] = []
    for key_ordinal in SENTINEL_FULL_LADDER_ORDINALS:
        ladder = sorted(
            (record for record in records if record["key_ordinal"] == key_ordinal),
            key=lambda record: int(record["node_ordinal"]),
        )
        if len(ladder) != 7:
            raise ExternalDirectContractError("sentinel fixed-extrema ladder missing")
        full_ladders.append(aggregate_key_records(ladder))
    status = (
        "PASS"
        if all(item["status"] == "PASS" for item in node_budgets)
        and all(item["numerical_budget"]["status"] == "PASS" for item in full_ladders)
        else "FAIL"
    )
    return {
        "schema": "schwo.phase6.v3_1_x.external_direct_sentinel_budget.v1",
        "node_budgets": node_budgets,
        "fixed_extrema_ladders": full_ladders,
        "node_count": 35,
        "fixed_extrema_ordinals": list(SENTINEL_FULL_LADDER_ORDINALS),
        "status": status,
    }


def validate_sentinel_budgets(
    payload: Mapping[str, Any], records: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    expected = build_sentinel_budgets(records)
    if dict(payload) != expected or expected["status"] != "PASS":
        raise ExternalDirectContractError("sentinel numerical admission failure")
    return expected


def validate_official_budgets(
    records: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    validate_node_records(records, "official")
    budgets = [
        aggregate_key_records(records[index : index + 7]) for index in range(0, 161, 7)
    ]
    if len(budgets) != 23 or any(
        item["numerical_budget"]["status"] != "PASS" for item in budgets
    ):
        raise ExternalDirectContractError("Route-C numerical budget failure")
    return budgets


def resource_projection(
    sentinel_records: Sequence[Mapping[str, Any]],
    *,
    free_bytes: int,
    projected_output_bytes: int = 20_000_000,
    safety_factor: mp.mpf = mp.mpf(2),
) -> dict[str, Any]:
    validate_node_records(sentinel_records, "sentinel")
    if safety_factor < 2 or free_bytes <= 0 or projected_output_bytes <= 0:
        raise ExternalDirectContractError("invalid resource inputs")
    by_node: dict[str, list[mp.mpf]] = {node: [] for node in NODE_ORDER}
    for record in sentinel_records:
        runtime = record["runtime"]
        if not isinstance(runtime, Mapping):
            raise ExternalDirectContractError("runtime record missing")
        seconds = _mp_real(runtime.get("elapsed_seconds"), "elapsed_seconds")
        if seconds <= 0:
            raise ExternalDirectContractError("nonpositive runtime")
        by_node[record["node"]["node_id"]].append(seconds)
    if any(not values for values in by_node.values()):
        raise ExternalDirectContractError("sentinel timing class missing")
    projected = safety_factor * sum(max(by_node[node]) * 23 for node in NODE_ORDER)
    return {
        "schema": "schwo.phase6.v3_1_x.resource_projection.v1",
        "sentinel_call_count": 35,
        "official_call_count": 161,
        "class_max_seconds": {
            node: mp.nstr(max(values), 40) for node, values in by_node.items()
        },
        "safety_factor": mp.nstr(safety_factor, 20),
        "projected_wall_seconds": mp.nstr(projected, 40),
        "runtime_limit_seconds": 36 * 3600,
        "runtime_gate_passed": projected <= 36 * 3600,
        "projected_output_bytes": projected_output_bytes,
        "free_bytes": free_bytes,
        "disk_gate_passed": projected_output_bytes <= free_bytes // 4,
    }


def static_contract() -> dict[str, Any]:
    """Zero-science graph and source contract for preflight/review."""

    inventory = route_c_inventory()
    official = official_plan()
    sentinel = sentinel_plan()
    base = NUMERICAL_SOURCE.read_bytes()
    overlay_hashes = {
        name: hashlib.sha256(transformed_numerical_source(base, name)).hexdigest()
        for name in OVERLAY_VARIANTS
    }
    if overlay_hashes != {name: item.sha256 for name, item in OVERLAY_VARIANTS.items()}:
        raise ExternalDirectContractError("overlay static hash mismatch")
    return {
        "schema": "schwo.phase6.v3_1_x.external_direct_static_contract.v1",
        "gate_id": GATE_ID,
        "scientific_evidence": False,
        "science_solver_calls": 0,
        "wolfram_launches": 0,
        "route_c_inventory": inventory,
        "route_c_inventory_sha256": hashlib.sha256(
            compact_bytes(inventory)
        ).hexdigest(),
        "official": {
            "keys": 23,
            "calls": len(official),
            "boundary_solutions": 2 * len(official),
            "overlaps": 3 * len(official),
        },
        "sentinel": {
            "keys": 23,
            "calls": len(sentinel),
            "boundary_solutions": 2 * len(sentinel),
            "overlaps": 3 * len(sentinel),
        },
        "overlay_hashes": overlay_hashes,
        "node_order": list(NODE_ORDER),
        "certificate_ids": list(CERTIFICATE_IDS),
        "threshold_count": 16,
        "mst_call_count": 0,
        "internal_solver_call_count": 0,
        "predecessor_science_reused": False,
        "sentinel_science_reused_officially": False,
    }
