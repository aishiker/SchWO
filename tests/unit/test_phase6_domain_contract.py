"""Tests for the non-numerical Phase-6 V1 radial-domain freeze."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from schwgw.io.tablei_paper_inferred import load_uniform_source_contract
from schwgw.validation.phase6_domain import (
    AUDIT_EXTENSION_LMAX,
    AUDIT_REQUIRED_LMAX,
    DomainContractError,
    DomainBundle,
    ProductionLmax,
    RadialKey,
    build_v1_domain,
    canonical_km,
    canonical_production_schedule,
    contract_payload,
    jsonl_bytes,
    read_jsonl_keys,
    source_file_identity,
    validate_contract_payload,
    validate_ordered_unique_keys,
)


def _accepted_bundle():
    schedule, _ = load_uniform_source_contract()
    return build_v1_domain(schedule)


def _domain_bytes(bundle):
    return {
        "D_prod.jsonl": jsonl_bytes(bundle.production),
        "D_ext.jsonl": jsonl_bytes(bundle.extension),
        "D_required.jsonl": jsonl_bytes(bundle.required),
        "D_union.jsonl": jsonl_bytes(bundle.union),
    }


def _identities(data_by_name):
    from schwgw.validation.phase6_domain import sha256_bytes

    return {
        name: {"sha256": sha256_bytes(data)}
        for name, data in data_by_name.items()
    }


def _schedule_bindings():
    _, bindings = load_uniform_source_contract()
    return [
        {
            "binding_source": str(raw["source"]),
            "binding_source_sha256": str(raw["source_sha256"]),
            "kM": canonical_km(raw["kM"]),
            "kind": raw["kind"],
            "lmax_pair": list(raw["lmax_pair"]),
            "resolved_source_identity": source_file_identity(Path(str(raw["source"]))),
            "row": raw["row"],
        }
        for raw in bindings
    ]


def _consumed_predecessor():
    names = (
        "D_ext.jsonl",
        "D_prod.jsonl",
        "D_required.jsonl",
        "D_union.jsonl",
        "domain_contract.json",
        "manifest.json",
    )
    return {
        "evidence_root": "/test/consumed-v1",
        "file_identities": {
            name: {
                "mode": 0o444,
                "nlink": 1,
                "path": f"/test/consumed-v1/{name}",
                "sha256": "b" * 64,
                "size": 1,
            }
            for name in names
        },
        "reason": "PREVIOUS_FREEZE_CONSUMED_NON_AUTHORITATIVE",
    }


def _payload(bundle, data_by_name):
    return contract_payload(
        bundle,
        source_identities={
            name: {
                "mode": 0o644,
                "nlink": 1,
                "path": f"/test/{name}",
                "sha256": "a" * 64,
                "size": 1,
            }
            for name in (
                "accepted_uniform40_merged_npz",
                "accepted_uniform40_merged_sidecar",
                "phase6_config",
                "phase6_domain_module",
                "phase6_freeze_script",
                "uniform_source_contract_loader",
            )
        },
        domain_file_identities={
            name: {
                "count": data.count(b"\n"),
                "mode": 0o444,
                "nlink": 1,
                "path": f"/test/{name}",
                "sha256": identity["sha256"],
                "size": len(data),
            }
            for name, (data, identity) in {
                name: (data, _identities(data_by_name)[name])
                for name, data in data_by_name.items()
            }.items()
        },
        schedule_source_bindings=_schedule_bindings(),
        consumed_predecessors=[_consumed_predecessor()],
    )


def test_actual_uniform40_schedule_builds_exact_frozen_sets() -> None:
    bundle = _accepted_bundle()
    assert len(bundle.production_lmax) == 40
    assert len(bundle.production) == 16048
    assert len(bundle.extension) == 1770
    assert len(bundle.required) == 3392
    assert len(bundle.union) == 17818
    assert len(set(bundle.production) & set(bundle.required)) == 1622
    assert not (set(bundle.production) & set(bundle.extension))
    assert set(bundle.required) - set(bundle.production) == set(bundle.extension)
    assert set(bundle.required) <= set(bundle.union)
    assert bundle.production_lmax[0].kM == "0.1"
    assert bundle.production_lmax[-1].kM == "4"
    assert bundle.production_lmax[0].final_lmax == 84
    assert bundle.production_lmax[-1].final_lmax == 360


def test_policy_extension_is_not_misrepresented_as_production() -> None:
    bundle = _accepted_bundle()
    data_by_name = _domain_bytes(bundle)
    payload = _payload(bundle, data_by_name)
    assert AUDIT_EXTENSION_LMAX == {"0.01": 84, "0.05": 84, "8": 720}
    assert AUDIT_REQUIRED_LMAX["8"] == 720
    assert payload["global_green_permitted"] is False
    assert payload["audit_extension_policy"]["status"] == "VALIDATION_POLICY_ONLY"
    assert "not completed production facts" in payload["audit_extension_policy"]["description"]
    validate_contract_payload(payload, bundle=bundle, domain_file_bytes=data_by_name)


def test_rejects_missing_or_changed_source_schedule() -> None:
    schedule, _ = load_uniform_source_contract()
    missing = dict(schedule)
    missing.pop(0.1)
    with pytest.raises(DomainContractError, match="production frequency set differs"):
        canonical_production_schedule(missing)

    broken = dict(schedule)
    broken[0.1] = (84, 84)
    with pytest.raises(DomainContractError, match="non-increasing"):
        canonical_production_schedule(broken)


@pytest.mark.parametrize("value", ["0", "0.0", "0.10", "01", "1.", "1e-1", "-0.1"])
def test_rejects_noncanonical_frequency_strings(value: str) -> None:
    with pytest.raises(DomainContractError):
        canonical_km(value)


def test_rejects_corrupt_ordered_key_records() -> None:
    keys = (RadialKey("0.1", "odd", 2), RadialKey("0.1", "odd", 3))
    assert validate_ordered_unique_keys(keys) == keys
    with pytest.raises(DomainContractError, match="duplicate"):
        validate_ordered_unique_keys((keys[0], keys[0]))
    with pytest.raises(DomainContractError, match="canonical strict order"):
        validate_ordered_unique_keys(tuple(reversed(keys)))


def test_rejects_hash_and_arithmetic_mismatch_in_contract_payload() -> None:
    bundle = _accepted_bundle()
    data_by_name = _domain_bytes(bundle)
    payload = _payload(bundle, data_by_name)
    corrupted_hash = deepcopy(payload)
    corrupted_hash["domain_files"]["D_prod.jsonl"]["sha256"] = "0" * 64
    with pytest.raises(DomainContractError, match="digest mismatch"):
        validate_contract_payload(
            corrupted_hash, bundle=bundle, domain_file_bytes=data_by_name
        )

    corrupted_count = deepcopy(payload)
    corrupted_count["set_arithmetic"]["D_union"] = 1
    with pytest.raises(DomainContractError, match="arithmetic metadata mismatch"):
        validate_contract_payload(
            corrupted_count, bundle=bundle, domain_file_bytes=data_by_name
        )


def test_rejects_synchronized_contract_lmax_tampering_against_source_bytes() -> None:
    bundle = _accepted_bundle()
    data_by_name = _domain_bytes(bundle)
    payload = _payload(bundle, data_by_name)
    payload["production_source"]["frequency_lmax"][0]["lmax_pair"] = [72, 84]
    payload["production_source"]["schedule_source_bindings"][0]["lmax_pair"] = [72, 84]
    tampered_bundle = DomainBundle(
        production_lmax=(ProductionLmax("0.1", (72, 84)), *bundle.production_lmax[1:]),
        production=bundle.production,
        extension=bundle.extension,
        required=bundle.required,
        union=bundle.union,
    )
    with pytest.raises(DomainContractError, match="differs from source bytes"):
        validate_contract_payload(
            payload, bundle=tampered_bundle, domain_file_bytes=data_by_name
        )


def test_rejects_jsonl_missing_final_lf_and_crlf(tmp_path: Path) -> None:
    keys = (RadialKey("0.1", "odd", 2), RadialKey("0.1", "odd", 3))
    raw = jsonl_bytes(keys)
    missing_lf = tmp_path / "missing-final-lf.jsonl"
    missing_lf.write_bytes(raw[:-1])
    with pytest.raises(DomainContractError, match="final LF"):
        read_jsonl_keys(missing_lf)
    crlf = tmp_path / "crlf.jsonl"
    crlf.write_bytes(raw.replace(b"\n", b"\r\n"))
    with pytest.raises(DomainContractError, match="final LF"):
        read_jsonl_keys(crlf)


def test_rejects_hardlinked_source_identity(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    alias = tmp_path / "source-alias.bin"
    source.write_bytes(b"source")
    alias.hardlink_to(source)
    with pytest.raises(DomainContractError, match="nlink1"):
        source_file_identity(source)
