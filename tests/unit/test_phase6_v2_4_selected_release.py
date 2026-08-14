from __future__ import annotations

import copy
from pathlib import Path

import pytest

from schwgw.validation import phase6_v2_selected_release as release


PROJECT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def built() -> tuple[release.ReleaseGate, dict[str, object]]:
    gate = release.verify_release_inputs(
        PROJECT, require_dispatch_review_identity=False
    )
    return gate, release.build_release_ledger(gate)  # type: ignore[return-value]


def test_exact_certificate_inventory_and_source_ceiling(built) -> None:
    _, ledger = built
    certificates = ledger["certificates"]
    assert (
        tuple(item["certificate_id"] for item in certificates)
        == release.CERTIFICATE_IDS
    )
    assert len(certificates) == 12
    assert [item["state"] for item in certificates].count("PASS") == 11
    assert certificates[10]["state"] == "PARTIAL"
    release.validate_certificate_inventory(certificates)


def test_every_certificate_has_exact_bounded_domain_and_budgets(built) -> None:
    _, ledger = built
    for certificate in ledger["certificates"]:
        domain = certificate["parameter_channel_domain"]
        assert domain["radial_pair_count"] == 15
        assert domain["radial_key_count"] == 30
        assert domain["record_count"] == 120
        assert domain["m_values"] == [-2, 2]
        assert domain["incident_columns"] == ["plus", "cross"]
        assert domain["extrapolation_permitted"] is False
        assert certificate["numerical_uncertainty_budget"]
        assert certificate["convention_uncertainty_budget"]
        assert certificate["authority_identities"] == release.AUTHORITY_IDENTITIES
        assert certificate["nonclaims"] == release.NONCLAIMS


def test_summary_keeps_global_and_full_domain_nonclaims(built) -> None:
    _, ledger = built
    summary = release.build_release_summary(ledger)
    assert summary["global_status"] is None
    assert summary["global_green_permitted"] is False
    assert summary["absolute_phase"] == "PARTIAL"
    assert summary["full_domain_v2"] == "NOT_ASSESSED"
    assert summary["domain_extrapolation_permitted"] is False
    assert summary["radial_solve_count"] == 0
    assert summary["new_science_computed"] is False


def test_omission_and_absolute_phase_upgrade_fail_closed(built) -> None:
    _, ledger = built
    certificates = copy.deepcopy(ledger["certificates"])
    with pytest.raises(release.Phase6V24Error, match="exactly twelve"):
        release.validate_certificate_inventory(certificates[:-1])
    certificates[10]["state"] = "PASS"
    with pytest.raises(release.Phase6V24Error, match="source ceiling"):
        release.validate_certificate_inventory(certificates)


def test_native_inventory_order_and_no_radial_solve(built) -> None:
    gate, _ = built
    release._validate_native_evidence(gate.v21, gate.v22, gate.v23)
    assert all(record["radial_solve_count"] == 0 for record in gate.v23["records"])
    channels = [release._channel(record) for record in gate.v21["records"]]
    assert channels[:4] == [
        (0, "plus", -2),
        (0, "plus", 2),
        (0, "cross", -2),
        (0, "cross", 2),
    ]


def test_frozen_identity_tamper_fails_closed(monkeypatch) -> None:
    identities = dict(release.FROZEN_IDENTITIES)
    path = "configs/phase6_v2_0_selected_domain_20260810.json"
    identities[path] = "0" * 64
    monkeypatch.setattr(release, "FROZEN_IDENTITIES", identities)
    with pytest.raises(release.Phase6V24Error, match="identity mismatch"):
        release.verify_release_inputs(PROJECT)
