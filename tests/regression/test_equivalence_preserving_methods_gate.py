from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest


SCRIPT = Path("scripts/phase5_equivalence_preserving_methods_gate.py")
FROZEN_FREQUENCIES = (0.86875, 1.58125, 2.91875, 3.759375, 3.89375)
FROZEN_LMAX = {
    0.86875: (24, 36, 60, 84),
    1.58125: (72, 96, 120, 144),
    2.91875: (192, 216, 240, 264),
    3.759375: (276, 300, 324, 348),
    3.89375: (288, 312, 336, 360),
}
FROZEN_POINTS = (
    "near_axis_x0_z30",
    "near_axis_x1_z30",
    "near_axis_x2_z30",
    "near_axis_x3_z30",
    "far_axis_x10_z30",
    "far_axis_x15_z30",
    "far_axis_x20_z30",
    "far_axis_x25_z30",
)


def _load_gate() -> Any:
    spec = importlib.util.spec_from_file_location(
        "phase5_equivalence_preserving_methods_gate",
        SCRIPT,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _identity(module: Any, suffix: str = "0") -> Any:
    return module.BenchmarkIdentity(
        implementation_sha256="1" * 64,
        physics_sha256="2" * 64,
        solver_sha256="3" * 64,
        config_sha256="4" * 64,
        source_sha256="5" * 64,
        gate_sha256="6" * 64,
        environment_sha256=(suffix * 64)[:64],
    )


def test_gate_freezes_only_the_predeclared_existing_matrix() -> None:
    module = _load_gate()

    assert SCRIPT.is_file()
    assert module.FROZEN_FREQUENCIES == FROZEN_FREQUENCIES
    assert module.FROZEN_LMAX_VALUES == FROZEN_LMAX
    assert module.FROZEN_POINT_IDS == FROZEN_POINTS
    assert module.FREQUENCY_CASE_COUNT == 5 * 4 * 8
    assert module.FULL_IMAGE_RESOLUTION == (241, 241)
    assert module.FULL_IMAGE_VALID_COUNT == 57_884
    assert module.FULL_IMAGE_MASKED_COUNT == 197
    assert module.FULL_IMAGE_CONVERGENCE_PROBE_COUNT == 48
    assert module.FULL_IMAGE_OPTIMIZED_CACHE_HIT_COUNT == 10_367_742
    assert module.DIAGNOSTIC_FAILED_CHILD_MIDPOINT_COUNT == 87

    module.validate_frozen_frequency_request(FROZEN_FREQUENCIES)
    with pytest.raises(module.GateContractError, match="frozen frequency matrix"):
        module.validate_frozen_frequency_request((*FROZEN_FREQUENCIES, 0.94375))
    with pytest.raises(module.GateContractError, match="frozen frequency matrix"):
        module.validate_frozen_frequency_request(FROZEN_FREQUENCIES[:-1])


def test_complex_error_budget_keeps_guarded_phase_separate() -> None:
    module = _load_gate()
    reference = np.asarray([1.0 + 2.0j, 1.0e-14 + 0.0j])
    candidate = reference.copy()

    metrics = module.compare_complex_arrays(candidate, reference)

    assert metrics.max_absolute == 0.0
    assert metrics.max_normalized_relative == 0.0
    assert metrics.max_guarded_phase == 0.0
    assert metrics.phase_sample_count == 1
    assert metrics.passed

    failed = module.compare_complex_arrays(
        reference + np.asarray([6.0e-12 + 0.0j, 0.0j]),
        reference,
    )
    assert not failed.passed


def test_full_image_comparison_allows_only_the_frozen_cache_hit_reduction() -> None:
    module = _load_gate()
    reference = (
        Path("runs/phase5/equivalence_preserving_methods_gate/legacy/full_image")
        / module.FULL_IMAGE_FILENAME
    )
    order, arrays, metadata, _ = module._read_npz(reference)
    optimized_metadata = copy.deepcopy(metadata)
    optimized_metadata["diagnostics"]["run_radial_cache"]["hit_count"] = (
        module.FULL_IMAGE_OPTIMIZED_CACHE_HIT_COUNT
    )

    comparison = module._compare_full_image_result(
        order,
        arrays,
        optimized_metadata,
        reference,
    )

    assert comparison["scientific_diagnostics_exact"]
    assert comparison["optimized_run_cache"]["hit_count"] == 10_367_742

    corrupted = copy.deepcopy(optimized_metadata)
    corrupted["diagnostics"]["summary"]["mode_count_max"] -= 1.0
    with pytest.raises(
        module.GateContractError,
        match="scientific diagnostics mismatch",
    ):
        module._compare_full_image_result(
            order,
            arrays,
            corrupted,
            reference,
        )


def test_performance_budget_uses_true_solve_counts_and_all_cases() -> None:
    module = _load_gate()
    legacy = (
        module.CaseResources("f0", 10.0, 9.0, 1.0, 100, 1_000),
        module.CaseResources("f1", 20.0, 18.0, 2.0, 120, 2_000),
    )
    optimized = (
        module.CaseResources("f0", 8.0, 7.0, 1.0, 70, 1_100),
        module.CaseResources("f1", 16.0, 14.0, 2.0, 84, 2_100),
    )

    result = module.evaluate_performance(legacy, optimized)

    assert result.legacy_solve_count == 220
    assert result.optimized_solve_count == 154
    assert result.solve_count_limit == 154
    assert result.passed

    mislabeled_batch = (
        module.CaseResources("f0", 8.0, 7.0, 1.0, 71, 1_100),
        module.CaseResources("f1", 16.0, 14.0, 2.0, 84, 2_100),
    )
    assert not module.evaluate_performance(legacy, mislabeled_batch).passed


def test_deterministic_executor_matches_serial_order() -> None:
    module = _load_gate()
    units = (
        module.WorkUnit(("b", 2), {"value": 2}),
        module.WorkUnit(("a", 3), {"value": 3}),
        module.WorkUnit(("a", 1), {"value": 1}),
    )

    def worker(unit: Any) -> dict[str, int]:
        time.sleep(0.002 * (4 - int(unit.payload["value"])))
        return {"value": int(unit.payload["value"])}

    serial = module.execute_deterministically(units, worker, max_workers=1)
    parallel = module.execute_deterministically(units, worker, max_workers=2)

    assert tuple(item.key for item in serial) == (("a", 1), ("a", 3), ("b", 2))
    assert parallel == serial
    with pytest.raises(module.GateContractError, match="at most two workers"):
        module.execute_deterministically(units, worker, max_workers=3)


def test_scientific_order_treats_numeric_components_numerically() -> None:
    module = _load_gate()
    units = (
        module.WorkUnit(("odd", 10, 1.0), {"value": 10}),
        module.WorkUnit(("odd", 2, 1.0), {"value": 2}),
    )

    ordered = module._ordered_units(units)

    assert tuple(unit.key for unit in ordered) == (
        ("odd", 2, 1.0),
        ("odd", 10, 1.0),
    )


def test_raw_warning_comparison_binds_policy_and_exact_tuples() -> None:
    module = _load_gate()
    record = {
        "policy": module.RAW_WARNING_SCHEMA,
        "total_count": 1,
        "entries": [
            {
                "category": "RuntimeWarning",
                "source": "scipy/integrate/_ivp/rk.py",
                "line": 63,
                "message": "overflow encountered in dot",
                "count": 1,
            }
        ],
        "all_recognized": True,
    }

    module._compare_warning_records(record, record)
    wrong_policy = {**record, "policy": "permissive"}
    with pytest.raises(module.GateContractError, match="warning policy"):
        module._compare_warning_records(wrong_policy, record)

    malformed_records = []
    extra_key = copy.deepcopy(record)
    extra_key["unexpected"] = True
    malformed_records.append(extra_key)
    string_total = copy.deepcopy(record)
    string_total["total_count"] = "1"
    malformed_records.append(string_total)
    floating_line = copy.deepcopy(record)
    floating_line["entries"][0]["line"] = 63.0
    malformed_records.append(floating_line)
    boolean_count = copy.deepcopy(record)
    boolean_count["entries"][0]["count"] = True
    malformed_records.append(boolean_count)
    wrong_sum = copy.deepcopy(record)
    wrong_sum["total_count"] = 2
    malformed_records.append(wrong_sum)
    for malformed in malformed_records:
        with pytest.raises(module.GateContractError):
            module._compare_warning_records(malformed, record)

    ordered = copy.deepcopy(record)
    ordered["total_count"] = 2
    ordered["entries"].append(
        {
            "category": "RuntimeWarning",
            "source": "src/schwgw/scattering/partial_wave.py",
            "line": 777,
            "message": "invalid value encountered in matmul",
            "count": 1,
        }
    )
    ordered["entries"].sort(
        key=lambda entry: (
            entry["source"],
            entry["line"],
            entry["message"],
            entry["category"],
            entry["count"],
        )
    )
    reversed_order = copy.deepcopy(ordered)
    reversed_order["entries"].reverse()
    with pytest.raises(module.GateContractError, match="canonical order"):
        module._compare_warning_records(reversed_order, ordered)


def test_warning_subrecords_are_strictly_typed_and_exact() -> None:
    module = _load_gate()
    frequency = {
        "codes": ["oracle_used"],
        "total_count": 1,
        "oracle_adapter_use_count": 1,
    }
    assert module._validate_frequency_structured_warning_record(frequency) == (
        frequency
    )
    malformed_frequency = {**frequency, "total_count": True}
    with pytest.raises(module.GateContractError):
        module._validate_frequency_structured_warning_record(
            malformed_frequency
        )

    empty_raw = {
        "policy": module.RAW_WARNING_SCHEMA,
        "total_count": 0,
        "entries": [],
        "all_recognized": True,
    }
    empty_structured = {
        "policy": "exact_empty_full_image_record",
        "total_count": 0,
        "entries": [],
    }
    module._validate_empty_full_image_warning_records(
        empty_raw,
        empty_structured,
    )
    with pytest.raises(module.GateContractError):
        module._validate_empty_full_image_warning_records(
            {**empty_raw, "all_recognized": False},
            empty_structured,
        )
    with pytest.raises(module.GateContractError):
        module._validate_empty_full_image_warning_records(
            empty_raw,
            {**empty_structured, "total_count": False},
        )


def test_stage_profile_binds_schema_calls_timings_and_derivations() -> None:
    module = _load_gate()
    resource_record = {
        "wall_seconds": 20.0,
        "user_cpu_seconds": 14.0,
        "system_cpu_seconds": 2.0,
        "cpu_seconds": 16.0,
        "peak_rss": 1_000,
        "peak_rss_unit": "bytes_on_macos",
        "minor_faults": 1,
        "major_faults": 0,
    }
    profile = {
        "radial": {
            "calls": 5,
            "wall_seconds": 2.0,
            "cpu_seconds": 1.0,
        },
        "polarization": {
            "calls": 32,
            "wall_seconds": 8.0,
            "cpu_seconds": 6.0,
        },
        "flat": {
            "calls": 32,
            "wall_seconds": 3.0,
            "cpu_seconds": 2.0,
        },
        "polarization_nonradial_wall_seconds": 6.0,
        "polarization_nonradial_cpu_seconds": 5.0,
        "unattributed_wall_seconds": 9.0,
    }

    module._validate_resource_record(resource_record)
    module._validate_stage_profile(
        profile,
        case_kind="frequency",
        resource_record=resource_record,
        solve_count=5,
    )

    malformed_profiles = []
    boolean_calls = copy.deepcopy(profile)
    boolean_calls["radial"]["calls"] = True
    malformed_profiles.append(boolean_calls)
    nonfinite_timing = copy.deepcopy(profile)
    nonfinite_timing["flat"]["wall_seconds"] = float("nan")
    malformed_profiles.append(nonfinite_timing)
    wrong_derived = copy.deepcopy(profile)
    wrong_derived["unattributed_wall_seconds"] = 8.0
    malformed_profiles.append(wrong_derived)
    wrong_call_count = copy.deepcopy(profile)
    wrong_call_count["polarization"]["calls"] = 31
    malformed_profiles.append(wrong_call_count)
    for malformed in malformed_profiles:
        with pytest.raises(module.GateContractError):
            module._validate_stage_profile(
                malformed,
                case_kind="frequency",
                resource_record=resource_record,
                solve_count=5,
            )


def test_full_image_residual_record_is_bound_to_scientific_metadata() -> None:
    module = _load_gate()
    maxima = {
        "boundary_residual": 1.0e-13,
        "wronskian_residual": 2.0e-13,
        "flux_residual": 3.0e-13,
    }
    metadata = {
        "diagnostics": {
            "summary": {
                "max_boundary_residual_max": 1.0e-13,
                "max_wronskian_residual_max": 2.0e-13,
            }
        }
    }

    module._validate_full_image_residual_binding(maxima, metadata)
    corrupted = copy.deepcopy(metadata)
    corrupted["diagnostics"]["summary"]["max_boundary_residual_max"] = 2.0e-13
    with pytest.raises(module.GateContractError, match="residual mismatch"):
        module._validate_full_image_residual_binding(maxima, corrupted)


def test_source_command_binds_fixed_run_case_and_identity() -> None:
    module = _load_gate()
    identity = _identity(module, "f")
    frozen = {
        "runner": {"sha256": "a" * 64},
        "implementation": {"commit": "b" * 40},
        "identity": identity,
    }
    paths = module.ArtifactPaths(
        case_id="frequency:0p86875",
        directory=Path("unused"),
        npz=Path("unused/kM_0p86875.npz"),
        sidecar=Path("unused/kM_0p86875.npz.json"),
        lock=Path("unused/.kM_0p86875.npz.lock"),
        quarantine=Path("unused/quarantine"),
    )
    command = [
        str(Path(module.__file__).resolve()),
        "--mode",
        "run",
        "--case",
        "frequency",
        "--frequency",
        "0.86875",
        "--expected-self-sha256",
        "a" * 64,
        "--expected-implementation-commit",
        "b" * 40,
        "--max-workers",
        "2",
    ]

    assert module._validate_run_source_command(frozen, paths, command) == command
    corrupted = list(command)
    corrupted[2] = "preflight"
    with pytest.raises(module.GateContractError, match="command identity"):
        module._validate_run_source_command(frozen, paths, corrupted)


def test_frequency_embedded_metadata_is_fully_bound() -> None:
    module = _load_gate()
    identity = _identity(module, "e")
    token = module.FREQUENCY_TOKENS[module.FROZEN_FREQUENCIES[0]]
    frequency = module.FROZEN_FREQUENCIES[0]
    arrays = {
        "final_pair_delta_plus": np.asarray([1.0e-8, 2.0e-8]),
        "final_pair_delta_cross": np.asarray([3.0e-8, 4.0e-8]),
    }
    tablei = SimpleNamespace(
        SCHEMA_VERSION="tablei-schema",
        ADAPTER_NAME="adapter",
        UNITS_CONTRACT={"F": "dimensionless"},
        DTYPE_CONTRACT={"F": "complex128"},
        ORDERING_CONTRACT={"points": "frozen"},
        NON_CLAIM_FLAGS={"spin2": False},
    )
    inputs = {
        "source_paths": {"source": "source.npz"},
        "source_hashes": {"source": "1" * 64},
        "gate_paths": {"gate": "gate.json"},
        "gate_hashes": {"gate": "2" * 64},
        "manifest_sha256": "3" * 64,
    }
    frozen = {
        "modules": {"tablei": tablei},
        "tablei_inputs": inputs,
        "runner": {"sha256": "4" * 64},
        "implementation": {
            "commit": "5" * 40,
            "manifest_sha256": "6" * 64,
        },
        "identity": identity,
        "selected_code_hashes": {"code.py": "7" * 64},
        "source": {
            "manifest_sha256": "8" * 64,
            "physics_manifest_sha256": "9" * 64,
            "solver_manifest_sha256": "a" * 64,
        },
        "config_identity": {"sha256": "b" * 64},
        "gates": {"manifest_sha256": "c" * 64},
        "environment": {"environment_sha256": "d" * 64},
    }
    generation, generation_sha256, metadata_sha256 = (
        module._frequency_generation_contract(frozen)
    )
    non_claims = {
        "new_frequency": False,
        "production_artifact": False,
        "publication_plot": False,
        "spin2_physics_implemented_or_validated": False,
    }
    source_command = ["fixed", "command"]
    benchmark = {
        "generation_contract": generation,
        "generation_contract_sha256": generation_sha256,
        "metadata_contract_sha256": metadata_sha256,
        "source_command": source_command,
        "non_claims": non_claims,
        "structured_warning_record": {
            "codes": ["oracle_used"],
            "total_count": 2,
            "oracle_adapter_use_count": 1,
        },
    }
    metadata = {
        "schema_version": tablei.SCHEMA_VERSION,
        "complete": True,
        "kM": frequency,
        "frequency_token": token,
        "point_ids": list(module.FROZEN_POINT_IDS),
        "lmax_values": list(module.FROZEN_LMAX_VALUES[frequency]),
        "final_lmax_pair": list(module.FROZEN_LMAX_VALUES[frequency][-2:]),
        "max_final_pair_delta_plus": 2.0e-8,
        "max_final_pair_delta_cross": 4.0e-8,
        "runtime_seconds": 1.0,
        "radial_solve_count": 10,
        "radial_reuse_count": 20,
        "radial_warning_codes": ["oracle_used"],
        "radial_warning_count": 2,
        "adapter_use_count": 1,
        "adapter": tablei.ADAPTER_NAME,
        "generation_contract_hash": generation_sha256,
        "metadata_contract_hash": metadata_sha256,
        "source_paths": inputs["source_paths"],
        "source_hashes": inputs["source_hashes"],
        "gate_paths": inputs["gate_paths"],
        "gate_hashes": inputs["gate_hashes"],
        "implementation": frozen["implementation"],
        "selected_code_hashes": frozen["selected_code_hashes"],
        "units": tablei.UNITS_CONTRACT,
        "dtypes": tablei.DTYPE_CONTRACT,
        "ordering": tablei.ORDERING_CONTRACT,
        "flags": tablei.NON_CLAIM_FLAGS,
        "array_fingerprints": {
            name: module._legacy_frequency_fingerprint(value)
            for name, value in arrays.items()
        },
        "t4ae_optimized_methods": {
            "schema_version": module.OUTPUT_SCHEMA_VERSION,
            "runner_sha256": frozen["runner"]["sha256"],
            "implementation_commit": frozen["implementation"]["commit"],
            "benchmark_identity_sha256": identity.canonical_digest,
            "generation_contract_sha256": generation_sha256,
            "source_command": source_command,
            "non_claims": non_claims,
        },
    }

    module._validate_frequency_embedded_metadata(
        frozen,
        token=token,
        arrays=arrays,
        metadata=metadata,
        benchmark=benchmark,
    )
    corruptions = (
        ("source_hashes", {"source": "f" * 64}),
        ("radial_warning_count", 1),
        (
            "array_fingerprints",
            {
                **metadata["array_fingerprints"],
                "final_pair_delta_plus": "0" * 64,
            },
        ),
        ("max_final_pair_delta_cross", 5.0e-8),
    )
    for name, value in corruptions:
        corrupted = copy.deepcopy(metadata)
        corrupted[name] = value
        with pytest.raises(module.GateContractError):
            module._validate_frequency_embedded_metadata(
                frozen,
                token=token,
                arrays=arrays,
                metadata=corrupted,
                benchmark=benchmark,
            )


def test_output_scope_rejects_foreign_temporary_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_gate()
    monkeypatch.setattr(module, "OUTPUT_ROOT", tmp_path)
    frequency_dir = tmp_path / "frequencies"
    frequency_dir.mkdir()
    foreign = frequency_dir / "foreign.tmp.crashed"
    foreign.write_text("partial", encoding="utf-8")

    with pytest.raises(module.GateContractError, match="unexpected"):
        module._validate_output_scope()

    foreign.unlink()
    paths = module._artifact_paths("frequency", module.FROZEN_FREQUENCIES[0])
    recognized = paths.npz.with_name(paths.npz.name + ".tmp.crashed")
    recognized.write_text("partial", encoding="utf-8")
    module._validate_output_scope()
    assert module._artifact_state(paths)["state"] == "partial"
    another = module._artifact_paths("frequency", module.FROZEN_FREQUENCIES[1])
    with pytest.raises(module.GateContractError, match="another optimized case"):
        module._validate_cross_case_run_states(another)


@pytest.mark.parametrize(
    ("fault", "payload"),
    (
        ("truncated", '{"schema_version":'),
        ("corrupt", "not-json"),
        (
            "interrupted",
            json.dumps(
                {
                    "schema_version": "t4ae_work_unit_v1",
                    "state": "running",
                    "identity_sha256": "0" * 64,
                    "key": ["case", 1],
                    "payload": {"value": 1},
                    "payload_sha256": "0" * 64,
                }
            ),
        ),
    ),
)
def test_atomic_checkpoint_faults_are_quarantined(
    tmp_path: Path,
    fault: str,
    payload: str,
) -> None:
    module = _load_gate()
    store = module.AtomicCheckpointStore(tmp_path, _identity(module))
    path = store.checkpoint_path(("case", 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")

    assert store.load_complete(("case", 1)) is None
    quarantined = tuple((tmp_path / "quarantine").glob(f"*.{fault}.*"))
    assert len(quarantined) == 1
    assert not path.exists()


def test_stale_checkpoint_is_rejected_without_recomputation(tmp_path: Path) -> None:
    module = _load_gate()
    original = module.AtomicCheckpointStore(tmp_path, _identity(module, "a"))
    original.write_complete(("case", 1), {"value": 7})
    stale = module.AtomicCheckpointStore(tmp_path, _identity(module, "b"))

    assert stale.load_complete(("case", 1)) is None
    assert tuple((tmp_path / "quarantine").glob("*.identity_mismatch.*"))


def test_interrupted_checkpoint_temporary_is_quarantined(tmp_path: Path) -> None:
    module = _load_gate()
    store = module.AtomicCheckpointStore(tmp_path, _identity(module, "d"))
    path = store.checkpoint_path(("case", 2))
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".tmp.crashed")
    partial.write_text('{"state":"partial"}', encoding="utf-8")

    assert store.load_complete(("case", 2)) is None
    assert not partial.exists()
    assert tuple((tmp_path / "quarantine").glob("*.interrupted.*"))


def test_complete_matching_checkpoint_is_reused(tmp_path: Path) -> None:
    module = _load_gate()
    store = module.AtomicCheckpointStore(tmp_path, _identity(module, "c"))
    unit = module.WorkUnit(("case", 1), {"value": 7})
    store.write_complete(unit.key, {"value": 49})
    calls = 0

    def forbidden_worker(_: Any) -> dict[str, int]:
        nonlocal calls
        calls += 1
        raise AssertionError("complete matching work unit must not be recomputed")

    result = module.execute_with_resume(
        (unit,),
        forbidden_worker,
        checkpoint_store=store,
        max_workers=1,
    )

    assert calls == 0
    assert result[0].payload == {"value": 49}
    assert result[0].reused


def test_stale_resume_lock_binds_frozen_control_identity(tmp_path: Path) -> None:
    module = _load_gate()
    identity = _identity(module, "e")
    frozen = {
        "identity": identity,
        "runner": {"sha256": "a" * 64},
        "implementation": {"commit": "b" * 40},
    }
    paths = module.ArtifactPaths(
        case_id="frequency:0p86875",
        directory=tmp_path,
        npz=tmp_path / "case.npz",
        sidecar=tmp_path / "case.npz.json",
        lock=tmp_path / ".case.npz.lock",
        quarantine=tmp_path / "quarantine",
    )
    command = ("runner.py", "--mode", "run")
    payload = {
        "case_id": paths.case_id,
        "identity_sha256": identity.canonical_digest,
        "runner_sha256": "f" * 64,
        "implementation_commit": "b" * 40,
        "command": list(command),
    }

    with pytest.raises(
        module.GateContractError,
        match="resume lock identity mismatch",
    ):
        module._validate_resume_lock_identity(
            payload,
            frozen=frozen,
            paths=paths,
            command=command,
        )


def _fake_matrix_audit(
    module: Any,
    case_id: str,
    *,
    wall_seconds: float,
    solve_count: int,
) -> dict[str, Any]:
    comparison = {
        "max_absolute_difference": 0.0,
        "max_normalized_relative_difference": 0.0,
        "max_guarded_phase_difference_rad": 0.0,
    }
    if case_id.startswith("frequency:"):
        comparison.update(
            {
                "max_final_pair_delta_plus": 1.0e-5,
                "max_final_pair_delta_cross": 2.0e-5,
                "max_final_pair_delta_difference_plus": 0.0,
                "max_final_pair_delta_difference_cross": 0.0,
            }
        )
    else:
        comparison.update(
            {
                "max_pixel_nrmse": 0.0,
                "max_normalized_pixel_linf": 0.0,
            }
        )
    maxima = {
        "boundary_residual": 1.0e-13,
        "wronskian_residual": 2.0e-13,
        "flux_residual": 3.0e-13,
    }
    return {
        "case_id": case_id,
        "comparison": {"legacy": comparison, "golden": comparison},
        "resource_record": {
            "wall_seconds": wall_seconds,
            "user_cpu_seconds": wall_seconds * 0.9,
            "system_cpu_seconds": wall_seconds * 0.1,
            "cpu_seconds": wall_seconds,
            "peak_rss": 1_000,
            "peak_rss_unit": "bytes_on_macos",
        },
        "cache_metrics": {
            "ode_oracle_solve_count": solve_count,
        },
        "radial_residual_maxima": maxima,
        "radial_residual_hard_gate": {
            "limits": {
                "boundary_residual": module.BOUNDARY_RESIDUAL_HARD_LIMIT,
                "wronskian_residual": module.WRONSKIAN_RESIDUAL_HARD_LIMIT,
                "flux_residual": module.FLUX_RESIDUAL_HARD_LIMIT,
            },
            "validated": maxima,
            "passed": True,
        },
    }


def test_matrix_audit_requires_exact_six_and_aggregates_performance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_gate()
    paths = tuple(object() for _ in module.FROZEN_CASE_IDS)
    audits = tuple(
        _fake_matrix_audit(
            module,
            case_id,
            wall_seconds=8.0,
            solve_count=70,
        )
        for case_id in module.FROZEN_CASE_IDS
    )
    legacy = tuple(
        module.CaseResources(case_id, 10.0, 9.0, 1.0, 100, 1_000)
        for case_id in module.FROZEN_CASE_IDS
    )
    monkeypatch.setattr(module, "_validate_output_scope", lambda: None)
    monkeypatch.setattr(
        module,
        "_require_global_idle",
        lambda: {"state": "idle", "lock": None, "quarantined": []},
    )
    monkeypatch.setattr(module, "_matrix_paths", lambda: paths)
    monkeypatch.setattr(
        module,
        "_artifact_state",
        lambda _: {"state": "complete_pair"},
    )
    monkeypatch.setattr(
        module,
        "_audit_optimized_pair",
        lambda _frozen, path: audits[paths.index(path)],
    )
    monkeypatch.setattr(module, "_legacy_matrix_resources", lambda: legacy)

    record = module._audit_matrix({})

    assert record["case_ids"] == list(module.FROZEN_CASE_IDS)
    assert record["performance_gate_passed"]
    assert record["performance"]["legacy_solve_count"] == 600
    assert record["performance"]["optimized_solve_count"] == 420
    assert (
        record["residual_evidence"][
            "frequency_legacy_worsening_comparison"
        ]
        == "unavailable_in_immutable_legacy_baseline"
    )

    monkeypatch.setattr(
        module,
        "_artifact_state",
        lambda path: {
            "state": "absent" if path is paths[-1] else "complete_pair"
        },
    )
    with pytest.raises(module.GateContractError, match="exact-six matrix"):
        module._audit_matrix({})


def test_preflight_payload_exposes_fixed_no_solver_contract() -> None:
    module = _load_gate()

    payload = module._preflight_payload()

    assert payload["frequencies"] == list(module.FROZEN_FREQUENCIES)
    assert payload["frequency_case_count"] == 160
    assert payload["full_image_resolution"] == [241, 241]
    assert payload["full_image_valid_count"] == 57_884
    assert payload["full_image_masked_count"] == 197
    assert payload["diagnostic_failed_child_midpoint_count"] == 87
    assert not payload["spin2_theory_implemented_or_validated"]


def test_script_contains_no_forbidden_downstream_actions() -> None:
    text = SCRIPT.read_text(encoding="utf-8").lower()

    assert "phase5_equivalence_preserving_methods_gate" in SCRIPT.name
    assert "kirchhoff" not in text
    assert "github" not in text
    assert "schwgw.viz" not in text
    assert "matplotlib" not in text
    assert "failed_child_midpoints_as_inputs" not in text
