from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from schwgw.validation.phase6_observable_contract import (
    ObservableContractError,
    convention_ledger,
    validate_payload,
    zero_payload,
)
from schwgw.validation.phase6_polarization_transfer import AbsolutePhaseConvention


ROOT = Path(__file__).resolve().parents[2]


def test_zero_fixture_is_contract_only_not_assessed() -> None:
    validate_payload(zero_payload(ROOT))


def test_convention_ledger_binds_the_frozen_absolute_phase_identity() -> None:
    ledger = convention_ledger()
    assert AbsolutePhaseConvention().sha256() in ledger["coulomb"]
    assert "asymptotic Cartesian" in ledger["basis"]
    assert not any(
        marker in value.casefold()
        for value in ledger.values()
        for marker in ("unspecified", "placeholder", "to be recorded", "tbd")
    )


def test_zero_fixture_binds_superseded_v1_without_mutating_it() -> None:
    predecessor = zero_payload(ROOT)["superseded_predecessor"]
    assert predecessor["schema"].endswith("_v1")
    assert predecessor["reason"].startswith("SUPERSEDED_AFTER_")
    assert set(predecessor["files"]) == {
        "manifest.json",
        "observable_contract.json",
    }
    assert all(item["mode"] == 0o444 for item in predecessor["files"].values())


@pytest.mark.parametrize(
    "mutate",
    [
        lambda value: value.__setitem__(
            "certificate_scope", "SchWO global certificate"
        ),
        lambda value: value["convention_ledger"].__setitem__("fourier", "exp(+ikt)"),
        lambda value: value["observables"]["master_to_strain_flux"].__setitem__(
            "state", "PASS"
        ),
        lambda value: value["observables"]["complex_lensing_matrix"].__setitem__(
            "state", "PARTIAL"
        ),
        lambda value: value["source_references"]["third_audit"].__setitem__(
            "sha256", "0" * 64
        ),
    ],
)
def test_adversarial_claims_fail_closed(mutate) -> None:
    payload = deepcopy(zero_payload(ROOT))
    mutate(payload)
    with pytest.raises(ObservableContractError):
        validate_payload(payload)
