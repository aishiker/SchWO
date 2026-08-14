#!/usr/bin/env python3
"""Freeze zero-science Phase-6 gates 4--7 observable evidence contract."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from schwgw.validation.phase6_domain import canonical_json_bytes
from schwgw.validation.phase6_observable_contract import SCHEMA, file_identity, validate_payload, zero_payload

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "runs/phase6/v1_observable_contract_v2_20260806"


def _write(path: Path, data: bytes) -> dict[str, object]:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.chmod(path, 0o444)
    return file_identity(path, immutable=True)


def freeze(output: Path) -> dict[str, object]:
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    payload = zero_payload(ROOT)
    validate_payload(payload)
    output.mkdir(mode=0o700)
    contract = _write(output / "observable_contract.json", canonical_json_bytes(payload))
    manifest = _write(output / "manifest.json", canonical_json_bytes({"schema": SCHEMA, "contract": contract, "solver_runs": 0, "scientific_pass_claimed": False, "global_green_permitted": False}))
    os.chmod(output, 0o555)
    reloaded = json.loads((output / "observable_contract.json").read_text())
    validate_payload(reloaded)
    return {"root": str(output), "contract_sha256": contract["sha256"], "manifest_sha256": manifest["sha256"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=DEFAULT)
    print(json.dumps(freeze(parser.parse_args().output_root), sort_keys=True))
