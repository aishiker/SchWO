#!/usr/bin/env python3
"""Validate and publish the complete Phase-6 conditioning campaign index.

This command never invokes a radial solver.  It accepts either exactly 86
explicit ``--shard-root`` arguments or one ``--roots-parent`` containing the
strict frozen V1 campaign namespace.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from schwgw.validation.phase6_conditioning_campaign import (
    PROJECT_ROOT,
    publish_conditioning_campaign,
    resolve_explicit_shard_roots,
    resolve_roots_parent,
)
from schwgw.validation.phase6_domain import source_file_identity


CAMPAIGN_MODULE = PROJECT_ROOT / "src/schwgw/validation/phase6_conditioning_campaign.py"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root",
        required=True,
        type=Path,
        help="Fresh absolute campaign evidence root.",
    )
    roots = parser.add_mutually_exclusive_group(required=True)
    roots.add_argument(
        "--shard-root",
        action="append",
        type=Path,
        help="One immutable shard root; repeat exactly 86 times.",
    )
    roots.add_argument(
        "--roots-parent",
        type=Path,
        help="Parent containing the exact strict V1 conditioning root names.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    if args.roots_parent is not None:
        shard_roots = resolve_roots_parent(args.roots_parent)
    else:
        shard_roots = resolve_explicit_shard_roots(args.shard_root or ())
    source_identities = {
        "campaign_module": source_file_identity(CAMPAIGN_MODULE),
        "campaign_runner": source_file_identity(Path(__file__).resolve(strict=True)),
    }
    result = publish_conditioning_campaign(
        args.output_root,
        shard_roots=shard_roots,
        campaign_source_identities=source_identities,
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
