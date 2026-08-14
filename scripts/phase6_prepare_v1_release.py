#!/usr/bin/env python3
"""Compose a fresh immutable Phase-6 V1 release preparation root.

The command reads terminal evidence only.  It never runs a solver, renders a
paper figure, or assigns a user-supplied scientific state.  ``--check-only``
performs the complete native-source preflight without creating an output path.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import stat

from schwgw.validation.phase6_domain import canonical_json_bytes
from schwgw.validation.phase6_release_preparation import (
    Phase6PreparationError,
    preflight_release_map,
    publish_preparation,
)


def load_release_map(path: Path) -> dict[str, object]:
    """Load one direct, canonical, nlink-1 declarative release map."""

    absolute = path.absolute()
    if any(component.is_symlink() for component in (absolute, *absolute.parents)):
        raise Phase6PreparationError("release-map path contains a symlink")
    try:
        resolved = absolute.resolve(strict=True)
        info = absolute.lstat()
    except OSError as exc:
        raise Phase6PreparationError(f"cannot read release map: {absolute}") from exc
    if resolved != absolute or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise Phase6PreparationError("release map must be a direct regular nlink1 file")
    raw = absolute.read_bytes()
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise Phase6PreparationError("release map is not JSON") from exc
    if not isinstance(payload, dict) or canonical_json_bytes(payload) != raw:
        raise Phase6PreparationError("release map must be canonical JSON")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-map", type=Path, required=True)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="validate native roots and derive states without writing anything",
    )
    args = parser.parse_args(argv)
    release_map = load_release_map(args.release_map)
    if args.check_only:
        if args.output_root is not None:
            parser.error("--check-only cannot be combined with --output-root")
        result = preflight_release_map(release_map)
    else:
        if args.output_root is None:
            parser.error("--output-root is required unless --check-only is used")
        result = publish_preparation(release_map, args.output_root)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
