from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import stat

import pytest

import schwgw.validation.phase6_bhpt_direct as direct
import schwgw.validation.phase6_bhpt_direct_comparison as comparison
import schwgw.validation.phase6_release_preparation as preparation
from schwgw.validation.phase6_bhpt_direct_comparison import (
    BHPTConditionedComparisonError,
    TYPED_RESULT_SCHEMA,
    build_comparison_payload,
    build_typed_report,
    publish_bhpt_conditioned_comparison,
    validate_published_bhpt_conditioned_comparison,
)
from schwgw.validation.phase6_domain import canonical_json_bytes
from schwgw.validation.phase6_execution_contract import (
    CONVENTION_BUDGET_FIELDS,
    NUMERICAL_BUDGET_FIELDS,
    external_direct_calibration_keys,
)

from tests.unit.test_phase6_bhpt_direct import _payload as external_payload


_FAIL_TUPLES = {
    (kM, sector, ell)
    for kM, ell in (("1", 20), ("2", 60), ("4", 120))
    for sector in ("odd", "even")
}
_SENTINEL = float.fromhex("0x1.fffffffffffffp+1023")


def _identity(seed: str) -> dict[str, object]:
    return {"sha256": hashlib.sha256(seed.encode()).hexdigest()}


def _source_evidence() -> dict[str, object]:
    direct_files = {
        name: _identity(f"direct-{name}")
        for name in (
            "evidence.json",
            "external_bhpt_direct.json",
            "manifest.json",
            "request.json",
        )
    }
    campaign_files = {
        name: _identity(f"campaign-{name}")
        for name in ("conditioning_campaign_index.json", "manifest.json")
    }
    shards = []
    for shard_id in comparison._expected_shard_ids():
        shards.append(
            {
                "root": {"mode": 0o555, "path": f"/fixture/{shard_id}"},
                "shard": {"shard_id": shard_id},
                "top_identities": {
                    name: _identity(f"{shard_id}-{name}")
                    for name in (
                        "manifest.json",
                        "run_contract.json",
                        "shard_checkpoint.json",
                        "shard_result.json",
                    )
                },
            }
        )
    return {
        "bhpt_direct": {
            "files": direct_files,
            "implementation_source_sha256s": {
                "bhpt_direct_validation": hashlib.sha256(b"direct").hexdigest(),
                "bhpt_toolkit": hashlib.sha256(b"toolkit").hexdigest(),
            },
            "root": {"mode": 0o555, "path": "/fixture/bhpt"},
        },
        "conditioning_campaign": {
            "files": campaign_files,
            "implementation_source_sha256s": {
                "conditioned_backend": hashlib.sha256(b"conditioned").hexdigest(),
                "conditioning_scan": hashlib.sha256(b"scan").hexdigest(),
            },
            "root": {"mode": 0o555, "path": "/fixture/campaign"},
        },
        "conditioning_shards": shards,
    }


def _internal_records(external: dict[str, object]) -> list[dict[str, object]]:
    records = []
    for ordinal, (key, external_record) in enumerate(
        zip(
            external_direct_calibration_keys(),
            external["records"],
            strict=True,
        )
    ):
        assert isinstance(external_record, dict)
        failed = (key.kM, key.sector, key.ell) in _FAIL_TUPLES
        numerical = {
            "components": {
                name: _SENTINEL if failed else 1.0e-8
                for name in NUMERICAL_BUDGET_FIELDS
            },
            "status": "FAIL" if failed else "PARTIAL",
        }
        convention = {
            "components": {
                name: _SENTINEL if failed else 3.141592653589793
                for name in CONVENTION_BUDGET_FIELDS
            },
            "status": "FAIL" if failed else "PARTIAL",
        }
        solver: dict[str, object] = {
            "acceptance_state": "FAIL" if failed else "PARTIAL",
            "convention_budget": convention,
            "failures": (
                {"baseline": "fixture conditioned radial fail closed"} if failed else {}
            ),
            "key": key.to_record(),
            "ladder_nodes": [{"node_id": "baseline"}],
            "numerical_budget": numerical,
        }
        if not failed:
            solver["results"] = {
                "baseline": {
                    "A_in": {"real": "1", "imag": "0"},
                    "A_out": deepcopy(external_record["reflection_ratio"]),
                    "S": deepcopy(external_record["phase_factor"]),
                    "T_horizon": deepcopy(external_record["transmission"]),
                    "diagnostics": {
                        "flux_residual": "0.5",
                        "normalization_definition": (
                            "A_in set exactly to one after Jost ratio"
                        ),
                        "outer_basis": "jost_1_over_r",
                        "paper_specific_envelope_used": False,
                        "scientific_acceptance": False,
                    },
                }
            }
        records.append(
            {
                "acceptance_state": "FAIL" if failed else "PARTIAL",
                "artifact_identities": {"payload": _identity(f"payload-{ordinal}")},
                "execution_status": (
                    "COMPLETED_FAIL_CLOSED" if failed else "COMPLETED"
                ),
                "key": key.to_record(),
                "shard_id": f"kM={key.kM};sector={key.sector}",
                "solver_payload": solver,
            }
        )
    return records


def _comparison_payload() -> dict[str, object]:
    external = external_payload()
    return build_comparison_payload(
        comparison_id="bhpt_direct_conditioned_fixture_v1",
        external_payload=external,
        internal_records=_internal_records(external),
        source_evidence=_source_evidence(),
        implementation_source_identities={
            "comparison_module": _identity("comparison-module"),
            "comparison_runner": _identity("comparison-runner"),
        },
    )


def test_exact_30_key_comparison_preserves_six_failures_and_no_pass() -> None:
    payload = _comparison_payload()

    assert payload["overall_state"] == "FAIL"
    assert payload["comparison_status_counts"] == {
        "FAIL": 6,
        "NOT_ASSESSED": 0,
        "PARTIAL": 24,
        "PASS": 0,
    }
    assert payload["no_phase_or_normalization_fit"] is True
    assert payload["numerical_uncertainty_budget"]["status"] == "FAIL"
    assert payload["convention_uncertainty_budget"]["status"] == "PARTIAL"
    assert (
        payload["numerical_uncertainty_budget"]["cross_backend_diagnostics"][
            "external_flux_residual_abs_max"
        ]
        == "0.5"
    )
    partial = [record for record in payload["records"] if record["state"] == "PARTIAL"]
    assert len(partial) == 24
    assert all(
        record["metrics"]["transmission_complex"]["state"] == "NOT_ASSESSED"
        for record in payload["records"]
    )
    assert all(
        record["metrics"]["phase_factor"]["complex_abs_difference"] == "0"
        for record in partial
    )


def test_typed_report_is_exact_release_adapter_input_and_remains_fail() -> None:
    payload = _comparison_payload()
    comparison_sha256 = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    report = build_typed_report(payload, comparison_sha256=comparison_sha256)

    assert report["schema"] == TYPED_RESULT_SCHEMA
    assert report["state"] == "FAIL"
    assert report["role"] == "INDEPENDENT_SCIENCE"
    assert report["independence_class"] == "EXTERNAL_SOURCE"
    assert report["gate"] == "V1"
    assert report["observable"] == "radial_s_matrix_flux"
    assert len(report["parameter_domain"]["expected_item_ids"]) == 30
    assert {item["state"] for item in report["item_results"]} == {
        "PARTIAL",
        "FAIL",
    }
    artifact = preparation.OriginArtifact(
        relative_path="report.json",
        raw=canonical_json_bytes(report),
        payload=report,
        origin_identity=_identity("typed-report"),
    )
    derived = preparation._typed_physical(
        "bhpt_direct_conditioned_fixture_v1",
        (artifact,),
        production_finite_radius=False,
        allow_bhpt_direct_comparison=True,
    )
    assert derived.state == "FAIL"
    assert derived.assessed_items == 30
    assert derived.expected_items == 30


def test_builder_rejects_hiding_one_frozen_internal_failure() -> None:
    external = external_payload()
    internal = _internal_records(external)
    failed_index = next(
        index
        for index, record in enumerate(internal)
        if record["acceptance_state"] == "FAIL"
    )
    replacement = deepcopy(internal[0])
    replacement["key"] = internal[failed_index]["key"]
    replacement["solver_payload"]["key"] = internal[failed_index]["key"]
    internal[failed_index] = replacement

    with pytest.raises(
        BHPTConditionedComparisonError, match="internal S definition|six frozen"
    ):
        build_comparison_payload(
            comparison_id="hidden_failure_fixture",
            external_payload=external,
            internal_records=internal,
            source_evidence=_source_evidence(),
            implementation_source_identities={
                "comparison_module": _identity("comparison-module"),
                "comparison_runner": _identity("comparison-runner"),
            },
        )


def test_active_or_mutable_bhpt_root_cannot_be_science(tmp_path: Path) -> None:
    active = tmp_path.resolve() / "active-bhpt"
    active.mkdir(mode=0o755)

    with pytest.raises(BHPTConditionedComparisonError, match="immutable 0555"):
        comparison._load_external_bhpt(active)


def test_external_loader_requires_and_accepts_terminal_linked_source_ledger(
    tmp_path: Path,
) -> None:
    root = tmp_path.resolve() / "terminal-bhpt-fixture"
    root.mkdir()
    toolkit_files = {
        name: {"sha256": digest}
        for name, digest in direct.EXPECTED_SOURCE_SHA256.items()
    }
    request = {
        "schema_version": direct.REQUEST_SCHEMA,
        "producer_source": _identity("producer-wls"),
        "orchestrator_sources": {
            "runner": _identity("direct-runner"),
            "validation_module": _identity("direct-validation"),
        },
        "toolkit_source": {"files": toolkit_files},
    }
    request_identity = direct.atomic_json(root / "request.json", request)
    raw = external_payload()
    raw["request_sha256"] = request_identity["sha256"]
    raw_identity = direct.atomic_json(root / "external_bhpt_direct.json", raw)
    evidence = direct.validate_external_payload(
        raw, expected_request_sha256=str(request_identity["sha256"])
    )
    evidence.update(
        {
            "blocker": None,
            "convention_uncertainty_budget": raw["convention_uncertainty_budget"],
            "external_json": str(root / "external_bhpt_direct.json"),
            "external_json_sha256": raw_identity["sha256"],
            "numerical_uncertainty_budget": raw["numerical_uncertainty_budget"],
            "request_sha256": request_identity["sha256"],
            "science_executed": True,
        }
    )
    direct.atomic_json(root / "evidence.json", evidence)
    direct._publish_manifest(root, returncode=0)

    try:
        loaded = comparison._load_external_bhpt(root)
        source = loaded["source"]
        assert set(source["files"]) == {
            "evidence.json",
            "external_bhpt_direct.json",
            "manifest.json",
            "request.json",
        }
        assert set(source["implementation_source_sha256s"]) == {
            "bhpt_direct_producer_wls",
            "bhpt_direct_runner",
            "bhpt_direct_validation_module",
            "bhpt_toolkit_Kernel/NumericalIntegration.m",
            "bhpt_toolkit_Kernel/ReggeWheelerRadial.m",
        }
    finally:
        root.chmod(0o755)
        for path in root.iterdir():
            path.chmod(0o644)


def test_formal_publisher_is_three_file_immutable_and_reloads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = _comparison_payload()
    monkeypatch.setattr(
        comparison,
        "build_bhpt_conditioned_comparison",
        lambda **_: deepcopy(payload),
    )
    output = tmp_path.resolve() / "formal-comparison"

    result = publish_bhpt_conditioned_comparison(
        output,
        comparison_id="bhpt_direct_conditioned_fixture_v1",
        bhpt_root=Path("/unused/bhpt"),
        conditioning_campaign_root=Path("/unused/campaign"),
        conditioning_shard_roots=[Path(f"/unused/{index}") for index in range(8)],
    )

    assert result["overall_state"] == "FAIL"
    assert {path.name for path in output.iterdir()} == {
        "comparison.json",
        "manifest.json",
        "report.json",
    }
    assert stat.S_IMODE(output.stat().st_mode) == 0o555
    for path in output.iterdir():
        assert stat.S_IMODE(path.stat().st_mode) == 0o444
        assert path.stat().st_nlink == 1
    validate_published_bhpt_conditioned_comparison(output)
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["comparison_status_counts"] == {
        "FAIL": 6,
        "NOT_ASSESSED": 0,
        "PARTIAL": 24,
        "PASS": 0,
    }
    assert (
        manifest["comparison_identity"]["sha256"]
        in (output / "report.json").read_text()
    )
    with pytest.raises(FileExistsError, match="fresh"):
        publish_bhpt_conditioned_comparison(
            output,
            comparison_id="bhpt_direct_conditioned_fixture_v1",
            bhpt_root=Path("/unused/bhpt"),
            conditioning_campaign_root=Path("/unused/campaign"),
            conditioning_shard_roots=[Path(f"/unused/{index}") for index in range(8)],
        )


def test_cli_requires_exactly_eight_explicit_shards() -> None:
    from scripts.phase6_compare_bhpt_direct_conditioned import parse_args

    with pytest.raises(SystemExit):
        parse_args(
            [
                "--comparison-id",
                "fixture",
                "--bhpt-root",
                "/bhpt",
                "--conditioning-campaign-root",
                "/campaign",
                "--shard-root",
                "/one",
                "--check-only",
            ]
        )
