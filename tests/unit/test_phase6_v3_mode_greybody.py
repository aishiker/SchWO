from __future__ import annotations

import json
from pathlib import Path

import pytest

from schwgw.scattering.absorption import mode_absorption_from_raw
from schwgw.validation.phase6_v3_mode_greybody import (
    V31ContractError,
    build_inventory_payload,
    validate_blocker_candidate,
)


def test_exact_inventory_and_anchor_routes() -> None:
    inventory = build_inventory_payload()
    assert inventory["route_a_pair_count"] == 248
    assert inventory["route_a_mode_count"] == 496
    assert inventory["route_a"][0]["parity"] == "odd"
    assert inventory["route_a"][1]["parity"] == "even"
    assert all(item["parity"] == "odd" for item in inventory["route_c"])
    assert {80, 120, 180} == set(
        inventory["ladders"]["arbitrary_precision_decimal_digits"]
    )


def test_direct_horizon_route_is_not_reconstructed_from_s() -> None:
    result = mode_absorption_from_raw(
        ell=2,
        A_in=1 + 0j,
        A_out=0.5 + 0j,
        incident_flux=2.0,
        outgoing_flux=0.5,
        horizon_flux=1.0,
    )
    assert result.gamma_flux == 0.5
    assert result.gamma_s == 0.75
    assert result.gamma_flux != result.gamma_s


def test_absorption_rejects_invalid_flux() -> None:
    with pytest.raises(ValueError):
        mode_absorption_from_raw(
            ell=2,
            A_in=1 + 0j,
            A_out=0j,
            incident_flux=1.0,
            outgoing_flux=0.0,
            horizon_flux=-1.0,
        )


def test_blocker_validator_rejects_inventory_drift(tmp_path: Path) -> None:
    # A skeletal root is enough to prove the validator does not accept a
    # summary-only or missing-artifact claim.
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "overall_state": "FAILED_NOT_ASSESSED",
                "global_green_permitted": False,
                "artifacts": {},
            }
        )
    )
    with pytest.raises(V31ContractError, match="artifact set"):
        validate_blocker_candidate(tmp_path)
