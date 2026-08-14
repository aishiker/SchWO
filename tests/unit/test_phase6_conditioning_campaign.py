from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
import hashlib
from pathlib import Path

import pytest

import schwgw.validation.phase6_conditioning_campaign as campaign
from schwgw.validation.phase6_conditioning_campaign import (
    CAMPAIGN_INDEX_SCHEMA,
    ConditioningCampaignError,
    ValidatedConditioningShard,
    campaign_index_from_validated_shards,
    campaign_shard_root_name,
    resolve_explicit_shard_roots,
    resolve_roots_parent,
    validate_conditioning_shard_root,
)
from schwgw.validation.phase6_conditioning_scan import load_frozen_scan_contract
from schwgw.validation.phase6_domain import source_file_identity
from schwgw.validation.phase6_execution_contract import (
    ACCEPTANCE_STATES,
    CONVENTION_BUDGET_FIELDS,
    NUMERICAL_BUDGET_FIELDS,
)


ROOT = Path(__file__).resolve().parents[2]
DOMAIN_ROOT = ROOT / "runs/phase6/v1_domain_freeze_v3_20260806"
EXECUTION_ROOT = ROOT / "runs/phase6/v1_execution_contract_v4_20260806"
REPRESENTATIVE_ROOT = (
    ROOT / "runs/phase6/radial_validation/"
    "v1_conditioning_scan_k0p5_odd_v1_20260808_py314"
)
RUNNER = ROOT / "scripts/phase6_publish_conditioning_campaign.py"
MODULE = ROOT / "src/schwgw/validation/phase6_conditioning_campaign.py"
SENTINEL = float.fromhex("0x1.fffffffffffffp+1023")


def _frozen():
    return load_frozen_scan_contract(DOMAIN_ROOT, EXECUTION_ROOT)


def _states(**updates: int) -> dict[str, int]:
    result = {state: 0 for state in ACCEPTANCE_STATES}
    result.update(updates)
    return result


def _identity(path: str, token: str) -> dict[str, object]:
    return {
        "mode": 0o444,
        "nlink": 1,
        "path": path,
        "sha256": hashlib.sha256(token.encode()).hexdigest(),
        "size": 1,
    }


def _source_identities() -> dict[str, Mapping[str, object]]:
    return {
        "campaign_module": source_file_identity(MODULE),
        "campaign_runner": source_file_identity(RUNNER),
    }


def _synthetic_validated_shards() -> tuple[ValidatedConditioningShard, ...]:
    frozen = _frozen()
    source_hashes = {
        "source:conditioned_backend": "1" * 64,
        "source:matching": "2" * 64,
        "source:potentials": "3" * 64,
        "source:scan_module": "4" * 64,
        "source:shard_runner": "5" * 64,
    }
    result = []
    for index, record in enumerate(frozen.shard_records):
        shard_id = str(record["shard_id"])
        keys = frozen.shard_keys(shard_id)
        key_count = len(keys)
        transition_count = sum(key in frozen.transition_keys for key in keys)
        calibration = _states(
            NOT_ASSESSED=key_count - transition_count,
            PARTIAL=transition_count,
        )
        observable_counts = {
            "conditioning_transition_calibration": calibration,
            "flux_conservation": _states(PASS=key_count),
            "production_finite_radius_states": _states(NOT_ASSESSED=key_count),
            "radial_s_matrix": _states(PARTIAL=key_count),
            "required_radius_radial_state": _states(PARTIAL=key_count),
        }
        result.append(
            ValidatedConditioningShard(
                root=Path(f"/synthetic/conditioning/{index:02d}"),
                shard=dict(record),
                keys=keys,
                top_identities={
                    name: _identity(
                        f"/synthetic/conditioning/{index:02d}/{name}",
                        f"{index}:{name}",
                    )
                    for name in (
                        "manifest.json",
                        "run_contract.json",
                        "shard_checkpoint.json",
                        "shard_result.json",
                    )
                },
                context_sha256=hashlib.sha256(shard_id.encode()).hexdigest(),
                source_hashes=source_hashes,
                backend_hashes={"conditioned_backend": "1" * 64},
                code_hashes={"scan_module": "4" * 64},
                config_hashes={"conditioning_policy": "6" * 64},
                runtime_identity={"runtime": "synthetic-consistent"},
                solver_call_count=key_count + 9 * transition_count,
                elapsed_seconds=float(index + 1),
                terminal_status_counts={
                    "COMPLETED": key_count,
                    "COMPLETED_FAIL_CLOSED": 0,
                },
                key_acceptance_counts=_states(PARTIAL=key_count),
                numerical_status_counts=_states(PARTIAL=key_count),
                convention_status_counts=_states(PARTIAL=key_count),
                observable_status_counts=observable_counts,
                numerical_components={
                    name: tuple(0.0 for _ in keys) for name in NUMERICAL_BUDGET_FIELDS
                },
                convention_components={
                    name: tuple(SENTINEL for _ in keys)
                    for name in CONVENTION_BUDGET_FIELDS
                },
                failure_reason_counts={},
                transition_key_count=transition_count,
                transition_solver_call_count=10 * transition_count,
                transition_key_status_counts=_states(PARTIAL=transition_count),
                transition_node_status_counts=_states(PASS=10 * transition_count),
                supported_key_count=key_count,
                unsupported_key_count=0,
                selected_r_out_counts={"300": key_count},
            )
        )
    return tuple(result)


def test_representative_shard_is_reloaded_without_hiding_scientific_failures():
    if not REPRESENTATIVE_ROOT.is_dir():
        pytest.skip("representative immutable campaign shard is not present")
    shard = validate_conditioning_shard_root(REPRESENTATIVE_ROOT)
    assert shard.shard_id == "kM=0.5;sector=odd"
    assert len(shard.keys) == 83
    assert shard.solver_call_count == 155
    assert shard.terminal_status_counts == {
        "COMPLETED": 74,
        "COMPLETED_FAIL_CLOSED": 9,
    }
    assert shard.key_acceptance_counts == _states(PARTIAL=74, FAIL=9)
    assert shard.numerical_status_counts == _states(PARTIAL=74, FAIL=9)
    assert shard.convention_status_counts == _states(PARTIAL=74, FAIL=9)
    assert shard.observable_status_counts["production_finite_radius_states"] == (
        _states(NOT_ASSESSED=83)
    )
    assert shard.transition_key_count == 8
    assert shard.transition_solver_call_count == 80
    assert sum(shard.failure_reason_counts.values()) == 27


def test_representative_shard_symlink_is_rejected(tmp_path: Path):
    if not REPRESENTATIVE_ROOT.is_dir():
        pytest.skip("representative immutable campaign shard is not present")
    alias = tmp_path / "alias"
    alias.symlink_to(REPRESENTATIVE_ROOT, target_is_directory=True)
    with pytest.raises(ConditioningCampaignError, match="direct non-aliased"):
        validate_conditioning_shard_root(alias)


def test_strict_root_name_matches_existing_campaign_convention():
    record = _frozen().shard_record("kM=0.5;sector=odd")
    assert campaign_shard_root_name(record) == (
        "v1_conditioning_scan_k0p5_odd_v1_20260808_py314"
    )


def test_roots_parent_requires_exact_campaign_namespace(tmp_path: Path):
    frozen = _frozen()
    for record in frozen.shard_records:
        (tmp_path / campaign_shard_root_name(record)).mkdir()
    roots = resolve_roots_parent(tmp_path, frozen=frozen)
    assert len(roots) == 86
    assert roots[1].name == campaign_shard_root_name(frozen.shard_records[1])
    extra = tmp_path / "v1_conditioning_scan_unexpected"
    extra.mkdir()
    with pytest.raises(ConditioningCampaignError, match="namespace mismatch"):
        resolve_roots_parent(tmp_path, frozen=frozen)


def test_explicit_roots_require_exactly_86_unique_existing_paths(tmp_path: Path):
    roots = []
    for index in range(86):
        path = tmp_path / f"root_{index:02d}"
        path.mkdir()
        roots.append(path)
    assert resolve_explicit_shard_roots(roots) == tuple(roots)
    with pytest.raises(ConditioningCampaignError, match="exactly 86"):
        resolve_explicit_shard_roots(roots[:-1])
    with pytest.raises(ConditioningCampaignError, match="duplicates"):
        resolve_explicit_shard_roots([*roots[:-1], roots[0]])


def test_full_synthetic_reduction_covers_exact_union_and_freezes_release_metadata():
    frozen = _frozen()
    payload = campaign_index_from_validated_shards(
        _synthetic_validated_shards(),
        frozen=frozen,
        campaign_source_identities=_source_identities(),
    )
    assert payload["schema"] == CAMPAIGN_INDEX_SCHEMA
    assert payload["coverage"] == {
        "D_union_exact_coverage": True,
        "D_union_key_list_sha256": (
            "a5793564dfc28e815699966208ae6605eeeedce9e3629f09512b70e08196810b"
        ),
        "extension_key_count": 1770,
        "key_count": 17818,
        "production_key_count": 16048,
        "shard_count": 86,
        "transition_key_count": 158,
    }
    assert payload["scientific_evidence"] is True
    assert payload["science_executed"] is True
    assert payload["kernel_unit_test_only"] is False
    assert payload["contract_only"] is False
    assert payload["overall_state"] == "PARTIAL"
    assert payload["global_green_permitted"] is False
    assert payload["li_figure_agreement_primary_gate"] is False
    assert payload["paper_agreement_gate"] is False
    assert payload["production_finite_radius_states"] == "NOT_ASSESSED"
    assert payload["execution_integrity"] == {
        "completed_shard_count": 86,
        "execution_failure_key_count": 0,
        "execution_failure_shard_count": 0,
        "scientific_failures_are_not_execution_failures": True,
        "status": "PASS_COMPLETE_IMMUTABLE_CAMPAIGN",
    }
    assert len(payload["implementation_source_sha_hashes"]) == 7


def test_scientific_fail_is_overall_fail_but_not_execution_failure():
    frozen = _frozen()
    shards = list(_synthetic_validated_shards())
    first = shards[0]
    key_count = len(first.keys)
    observables = {
        name: dict(counts) for name, counts in first.observable_status_counts.items()
    }
    observables["flux_conservation"] = _states(PASS=key_count - 1, FAIL=1)
    shards[0] = replace(
        first,
        terminal_status_counts={
            "COMPLETED": key_count - 1,
            "COMPLETED_FAIL_CLOSED": 1,
        },
        key_acceptance_counts=_states(PARTIAL=key_count - 1, FAIL=1),
        numerical_status_counts=_states(PARTIAL=key_count - 1, FAIL=1),
        convention_status_counts=_states(PARTIAL=key_count - 1, FAIL=1),
        observable_status_counts=observables,
        failure_reason_counts={"SyntheticScientificFailure": 1},
    )
    payload = campaign_index_from_validated_shards(
        shards,
        frozen=frozen,
        campaign_source_identities=_source_identities(),
    )
    assert payload["overall_state"] == "FAIL"
    assert payload["status"] == "INDEX_COMPLETE_WITH_SCIENTIFIC_FAILURES"
    assert payload["failure_summary"]["scientific_failure_key_count"] == 1
    assert payload["execution_integrity"]["execution_failure_key_count"] == 0


def test_reduction_rejects_missing_duplicate_or_source_drift():
    frozen = _frozen()
    shards = list(_synthetic_validated_shards())
    with pytest.raises(ConditioningCampaignError, match="86 shards"):
        campaign_index_from_validated_shards(
            shards[:-1],
            frozen=frozen,
            campaign_source_identities=_source_identities(),
        )
    with pytest.raises(ConditioningCampaignError, match="ordering/identity"):
        campaign_index_from_validated_shards(
            [*shards[:-1], shards[0]],
            frozen=frozen,
            campaign_source_identities=_source_identities(),
        )
    changed = dict(shards[-1].source_hashes)
    changed["source:scan_module"] = "f" * 64
    shards[-1] = replace(shards[-1], source_hashes=changed)
    with pytest.raises(ConditioningCampaignError, match="hashes drifted"):
        campaign_index_from_validated_shards(
            shards,
            frozen=frozen,
            campaign_source_identities=_source_identities(),
        )


def test_reduction_rejects_finite_radius_promotion():
    frozen = _frozen()
    shards = list(_synthetic_validated_shards())
    first = shards[0]
    observables = {
        name: dict(counts) for name, counts in first.observable_status_counts.items()
    }
    observables["production_finite_radius_states"] = _states(
        NOT_ASSESSED=len(first.keys) - 1,
        PARTIAL=1,
    )
    shards[0] = replace(first, observable_status_counts=observables)
    with pytest.raises(ConditioningCampaignError, match="promoted"):
        campaign_index_from_validated_shards(
            shards,
            frozen=frozen,
            campaign_source_identities=_source_identities(),
        )


def test_exclusive_json_publication_is_0444_and_no_overwrite(tmp_path: Path):
    identity = campaign._publish_json_exclusive(tmp_path / "index.json", {"a": 1})
    assert identity["mode"] == 0o444
    assert (tmp_path / "index.json").read_bytes() == b'{"a":1}\n'
    assert not any("staging" in path.name for path in tmp_path.iterdir())
    with pytest.raises(FileExistsError):
        campaign._publish_json_exclusive(tmp_path / "index.json", {"a": 2})
