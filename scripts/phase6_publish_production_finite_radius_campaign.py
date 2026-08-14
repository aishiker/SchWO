#!/usr/bin/env python3
"""Validate 80 immutable shard roots and publish one campaign evidence root."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from schwgw.validation.phase6_domain import (  # noqa: E402
    canonical_json_bytes,
    source_file_identity,
)
from schwgw.validation.phase6_production_finite_radius import (  # noqa: E402
    load_frozen_production_contract,
)
from schwgw.validation.phase6_production_finite_radius_campaign import (  # noqa: E402
    CAMPAIGN_MANIFEST_SCHEMA,
    ProductionCampaignError,
    build_campaign_result,
    validate_campaign_result,
)


DOMAIN_ROOT = ROOT / "runs/phase6/v1_domain_freeze_v3_20260806"
EXECUTION_ROOT = ROOT / "runs/phase6/v1_execution_contract_v4_20260806"
CAMPAIGN_MODULE = (
    ROOT / "src/schwgw/validation/phase6_production_finite_radius_campaign.py"
)
PRODUCTION_MODULE = ROOT / "src/schwgw/validation/phase6_production_finite_radius.py"
PUBLISHER_SOURCE = Path(__file__).resolve()
SHARD_RUNNER = ROOT / "scripts/phase6_run_production_finite_radius_shard.py"
DOC_SOURCE = ROOT / "docs/phase6_production_finite_radius_v1.md"


def _campaign_source_identities() -> dict[str, dict[str, object]]:
    paths = {
        "campaign_module": CAMPAIGN_MODULE,
        "campaign_publisher": PUBLISHER_SOURCE,
        "production_gate_doc": DOC_SOURCE,
        "production_gate_module": PRODUCTION_MODULE,
        "production_shard_runner": SHARD_RUNNER,
    }
    result: dict[str, dict[str, object]] = {}
    for name, path in paths.items():
        if path.is_symlink() or not path.is_file():
            raise ProductionCampaignError(
                f"campaign implementation source is missing or aliased: {path}"
            )
        identity = source_file_identity(path)
        if identity["nlink"] != 1:
            raise ProductionCampaignError(
                f"campaign implementation source has ambiguous hardlinks: {path}"
            )
        result[name] = identity
    return result


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _publish_json_exclusive(path: Path, payload: object) -> dict[str, object]:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"refusing to replace artifact: {path}")
    staging = path.parent / f".{path.name}.o_excl_staging.{os.getpid()}"
    data = canonical_json_bytes(payload)
    descriptor: int | None = None
    try:
        descriptor = os.open(staging, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            descriptor = None
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(staging, path)
        os.chmod(path, 0o444)
        staging.unlink()
        _fsync_directory(path.parent)
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        if staging.exists() and not staging.is_symlink():
            staging.unlink()
        raise
    identity = source_file_identity(path)
    if identity["mode"] != 0o444 or identity["nlink"] != 1:
        raise ProductionCampaignError("published campaign artifact is not immutable")
    return identity


def _fresh_root(path: str | Path) -> Path:
    root = Path(path)
    if not root.is_absolute():
        raise ProductionCampaignError("campaign output root must be absolute")
    if root.exists() or root.is_symlink():
        raise ProductionCampaignError("campaign output root must be fresh and absent")
    parent = root.parent.resolve(strict=True)
    if parent != root.parent or parent.is_symlink():
        raise ProductionCampaignError("campaign output parent must be direct")
    root.mkdir(mode=0o700)
    if root.resolve(strict=True) != root:
        raise ProductionCampaignError("campaign output root is aliased")
    return root


def _strict_json(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    value = json.loads(
        raw,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON constant: {token}")
        ),
    )
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
        raise ProductionCampaignError("campaign artifact is not canonical JSON")
    return value


def publish_campaign(
    output_root: str | Path,
    *,
    shard_roots: list[str | Path],
) -> dict[str, object]:
    """Publish no-overwrite campaign evidence after full independent reload."""

    frozen = load_frozen_production_contract(DOMAIN_ROOT, EXECUTION_ROOT)
    source_identities = _campaign_source_identities()
    payload = build_campaign_result(
        shard_roots,
        frozen=frozen,
        campaign_implementation_identities=source_identities,
    )
    validate_campaign_result(payload)
    if _campaign_source_identities() != source_identities:
        raise ProductionCampaignError(
            "campaign implementation source changed during validation"
        )
    frozen_after = load_frozen_production_contract(DOMAIN_ROOT, EXECUTION_ROOT)
    if (
        frozen_after.domain_identities != frozen.domain_identities
        or frozen_after.execution_identities != frozen.execution_identities
        or frozen_after.coordinate_source_identity != frozen.coordinate_source_identity
    ):
        raise ProductionCampaignError("frozen input changed during campaign validation")
    root = _fresh_root(output_root)
    result_identity = _publish_json_exclusive(root / "campaign_result.json", payload)
    manifest = {
        "campaign_result_identity": result_identity,
        "global_green_permitted": False,
        "schema": CAMPAIGN_MANIFEST_SCHEMA,
        "status": "COMPLETE",
    }
    _publish_json_exclusive(root / "manifest.json", manifest)
    os.chmod(root, 0o555)
    _fsync_directory(root.parent)
    if (
        root.resolve(strict=True) != root
        or stat.S_IMODE(root.stat().st_mode) != 0o555
        or any(stat.S_IMODE(path.stat().st_mode) != 0o444 for path in root.iterdir())
    ):
        raise ProductionCampaignError("campaign root is not immutable")
    reloaded_manifest = _strict_json(root / "manifest.json")
    if reloaded_manifest != manifest:
        raise ProductionCampaignError("campaign manifest reload changed")
    if source_file_identity(root / "campaign_result.json") != result_identity:
        raise ProductionCampaignError("campaign result identity changed")
    reloaded = _strict_json(root / "campaign_result.json")
    validate_campaign_result(reloaded)
    return reloaded


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument(
        "--shard-root",
        type=Path,
        action="append",
        required=True,
        help="repeat exactly 80 times; order is independently canonicalized",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    result = publish_campaign(
        arguments.output_root,
        shard_roots=arguments.shard_root,
    )
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
