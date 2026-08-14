from __future__ import annotations

import json

import pytest

from scripts.phase6_build_v1_repaired_release_map import _load_json
from schwgw.validation.phase6_domain import canonical_json_bytes
from schwgw.validation.phase6_release_preparation import Phase6PreparationError


def test_builder_accepts_native_pretty_json_without_reencoding(tmp_path) -> None:
    path = tmp_path / "producer.json"
    payload = {"schema": "producer_specific_v1", "state": "PASS"}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    assert _load_json(path, require_domain_canonical_bytes=False) == payload


def test_builder_keeps_release_map_canonical_bytes_strict(tmp_path) -> None:
    path = tmp_path / "release_map.json"
    payload = {"schema": "release_map_fixture_v1", "state": "PARTIAL"}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    with pytest.raises(Phase6PreparationError, match="noncanonical domain/release"):
        _load_json(path, require_domain_canonical_bytes=True)

    path.write_bytes(canonical_json_bytes(payload))
    assert _load_json(path, require_domain_canonical_bytes=True) == payload
