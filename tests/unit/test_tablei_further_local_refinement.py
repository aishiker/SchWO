from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import schwgw.io.tablei_further_local_refinement as further
from schwgw.io.tablei_further_local_refinement import (
    ADAPTER_NAME,
    EXPECTED_ACTIVE_FILES,
    EXPECTED_MANIFEST_RECORDS,
    FREQUENCY_TOKENS,
    FURTHER_LOCAL_FREQUENCIES,
    FURTHER_LOCAL_LMAX_VALUES,
    PARENT_REFINEMENTS,
    SCHEMA_VERSION,
    FurtherLocalRefinementContractError,
    run_further_local_refinement,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_aggregate(
    path: Path, frequencies: np.ndarray, point_ids: np.ndarray
) -> None:
    shape = (len(frequencies), 8)
    phase_scale = np.linspace(0.2, 0.9, 8)
    plus = np.exp(1j * frequencies[:, None] * phase_scale)
    cross = np.exp(1j * frequencies[:, None] * (phase_scale + 0.1))
    np.savez(
        path,
        kM_values=frequencies,
        point_ids=point_ids,
        F_plus_complex=plus,
        F_cross_complex=cross,
        valid_ratio_plus_mask=np.ones(shape, dtype=bool),
        valid_ratio_cross_mask=np.ones(shape, dtype=bool),
    )


def _write_manifest(path: Path, records: int) -> None:
    path.write_text(
        "# synthetic\n\n"
        + "\n".join(
            f"- `file-{index}` — 1 bytes — SHA256 `{'0' * 64}`"
            for index in range(records)
        )
        + "\n",
        encoding="utf-8",
    )


def _write_inputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path, Path, Path, Path, Path, Path]:
    point_ids = np.asarray([point.point_id for point in further.TABLEI_POINTS])

    review = tmp_path / "review"
    review.mkdir()
    review_npz = review / "tablei_dense_review_values.npz"
    _write_aggregate(
        review_npz,
        np.asarray(
            [
                0.1,
                0.2,
                0.3,
                0.5,
                0.75,
                1.0,
                1.25,
                1.5,
                1.75,
                2.0,
                2.25,
                2.5,
                2.75,
                3.0,
                3.25,
                3.5,
                3.75,
                4.0,
            ],
            dtype=np.float64,
        ),
        point_ids,
    )
    review_json = review_npz.with_suffix(".npz.json")
    review_json.write_text("{}\n", encoding="utf-8")
    review_manifest = review / "manifest.md"
    review_manifest.write_text("synthetic review\n", encoding="utf-8")

    risk = tmp_path / "risk"
    risk.mkdir()
    risk_npz = risk / "risk_pilot_values.npz"
    _write_aggregate(
        risk_npz,
        np.asarray([0.4, 0.8, 0.9, 1.6, 1.7, 2.8, 2.9, 3.8, 3.9]),
        point_ids,
    )
    risk_json = risk / "risk_pilot_values.npz.json"
    risk_json.write_text(
        json.dumps(
            {
                "schema_version": further.ACCEPTED_RISK_SCHEMA,
                "generation_contract_hash": further.ACCEPTED_RISK_GENERATION_HASH,
                "metadata_contract_hash": further.ACCEPTED_RISK_METADATA_HASH,
                "units": {"aggregate_arrays": {}},
                "ordering": {"frequency_order": [0.4]},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    for name in ("checkpoint_ledger.json", "risk_pilot_sampling_audit.json"):
        (risk / name).write_text("{}\n", encoding="utf-8")
    risk_frequency_dir = risk / "frequencies"
    risk_frequency_dir.mkdir()
    for token in ("0p4", "0p8", "0p9", "1p6", "1p7", "2p8", "2p9", "3p8", "3p9"):
        (risk_frequency_dir / f"kM_{token}.npz").write_bytes(b"synthetic npz")
        (risk_frequency_dir / f"kM_{token}.npz.json").write_text(
            "{}\n", encoding="utf-8"
        )
    _write_manifest(risk / "manifest.md", 22)

    adaptive = tmp_path / "adaptive"
    adaptive.mkdir()
    adaptive_npz = adaptive / "adaptive_refinement_values.npz"
    _write_aggregate(
        adaptive_npz,
        np.asarray(
            [
                0.35,
                0.45,
                0.85,
                0.95,
                1.55,
                1.65,
                1.725,
                2.775,
                2.85,
                2.95,
                3.775,
                3.85,
                3.95,
            ]
        ),
        point_ids,
    )
    adaptive_json = adaptive / "adaptive_refinement_values.npz.json"
    adaptive_json.write_text(
        json.dumps(
            {
                "schema_version": further.ACCEPTED_ADAPTIVE_SCHEMA,
                "generation_contract_hash": further.ACCEPTED_ADAPTIVE_GENERATION_HASH,
                "metadata_contract_hash": further.ACCEPTED_ADAPTIVE_METADATA_HASH,
                "shape": [13, 8],
                "frequency_metadata": [{} for _ in range(13)],
                "units": {},
                "dtypes": {},
                "ordering": {},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    for name in ("checkpoint_ledger.json", "adaptive_sampling_audit.json"):
        (adaptive / name).write_text("{}\n", encoding="utf-8")
    adaptive_frequency_dir = adaptive / "frequencies"
    adaptive_frequency_dir.mkdir()
    for token in (
        "0p35",
        "0p45",
        "0p85",
        "0p95",
        "1p55",
        "1p65",
        "1p725",
        "2p775",
        "2p85",
        "2p95",
        "3p775",
        "3p85",
        "3p95",
    ):
        (adaptive_frequency_dir / f"kM_{token}.npz").write_bytes(b"synthetic npz")
        (adaptive_frequency_dir / f"kM_{token}.npz.json").write_text(
            "{}\n", encoding="utf-8"
        )
    _write_manifest(adaptive / "manifest.md", 30)

    evidence = tmp_path / "T7bz.md"
    evidence.write_text("synthetic T7bz evidence\n", encoding="utf-8")

    t4aa = tmp_path / "t4aa"
    t4aa.mkdir()
    for name in (
        "classification_manifest.json",
        "oracle_validation.json",
        "resume_preflight.json",
        "manifest.md",
    ):
        (t4aa / name).write_text("{}\n", encoding="utf-8")
    t4aa_checkpoint = t4aa / "checkpoint"
    t4aa_checkpoint.mkdir()
    for index in range(13):
        (t4aa_checkpoint / f"checkpoint_{index}.json").write_text(
            "{}\n", encoding="utf-8"
        )

    gate = tmp_path / "gate"
    gate.mkdir()
    for name in ("classification_manifest.json", "oracle_validation.json", "manifest.md"):
        (gate / name).write_text("{}\n", encoding="utf-8")
    (gate / "resume_preflight.json").write_text(
        json.dumps(
            {
                "adapter_name": ADAPTER_NAME,
                "classification_snapshot_sha256": further.CLASSIFICATION_SNAPSHOT_HASH,
                "final_adapter_snapshot_sha256": further.FINAL_ADAPTER_SNAPSHOT_HASH,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    checkpoint_dir = gate / "checkpoint"
    checkpoint_dir.mkdir()
    for token in FREQUENCY_TOKENS.values():
        (checkpoint_dir / f"kM_{token}.json").write_text(
            '{"complete": true, "decision": "PASS"}\n', encoding="utf-8"
        )

    source_paths = {
        "review_npz": review_npz,
        "review_json": review_json,
        "review_manifest": review_manifest,
        "risk_ledger": risk / "checkpoint_ledger.json",
        "risk_npz": risk_npz,
        "risk_json": risk_json,
        "risk_audit": risk / "risk_pilot_sampling_audit.json",
        "risk_manifest": risk / "manifest.md",
        "adaptive_ledger": adaptive / "checkpoint_ledger.json",
        "adaptive_npz": adaptive_npz,
        "adaptive_json": adaptive_json,
        "adaptive_audit": adaptive / "adaptive_sampling_audit.json",
        "adaptive_manifest": adaptive / "manifest.md",
        "t7bz_evidence": evidence,
        "t4aa_classification": t4aa / "classification_manifest.json",
        "t4aa_oracle": t4aa / "oracle_validation.json",
        "t4aa_preflight": t4aa / "resume_preflight.json",
        "t4aa_manifest": t4aa / "manifest.md",
    }
    gate_paths = {
        name: gate / name
        for name in (
            "classification_manifest.json",
            "oracle_validation.json",
            "resume_preflight.json",
            "manifest.md",
        )
    }
    monkeypatch.setattr(
        further,
        "_FROZEN_SOURCE_HASHES",
        {name: _sha(path) for name, path in source_paths.items()},
    )
    monkeypatch.setattr(
        further,
        "_FROZEN_GATE_HASHES",
        {name: _sha(path) for name, path in gate_paths.items()},
    )
    record = tmp_path / "T7_current.md"
    record.write_text(further.T7CA_GREEN + "\n", encoding="utf-8")
    monkeypatch.setattr(further, "_T7CA_RECORD_PATH", record)
    source_paths["t7ca_record"] = record
    monkeypatch.setattr(
        further,
        "_FROZEN_SOURCE_HASHES",
        {name: _sha(path) for name, path in source_paths.items()},
    )
    monkeypatch.setattr(
        further,
        "_implementation_identity",
        lambda: {
            "commit": "f" * 40,
            "paths": list(further.IMPLEMENTATION_PATHS),
            "blobs": {
                path: {"git_blob": "e" * 40, "sha256": "d" * 64}
                for path in further.IMPLEMENTATION_PATHS
            },
        },
    )
    return review_npz, risk, adaptive, evidence, t4aa, gate, record


class _FakePolarization:
    calls = 0

    @classmethod
    def solve(cls, **kwargs: object) -> SimpleNamespace:
        cls.calls += 1
        k = float(kwargs["k"])
        lmax = int(kwargs["lmax"])
        theta = float(kwargs["theta"])
        correction = 1.0e-6 / lmax
        return SimpleNamespace(
            h_plus=complex(1.0 + 0.1 * k + theta + correction, 0.2 * k),
            h_cross=complex(0.7 + 0.05 * k + theta + correction, 0.15 * k),
            diagnostics={},
        )


def _fake_flat(**kwargs: object) -> SimpleNamespace:
    del kwargs
    return SimpleNamespace(h_plus=1.0 + 0.0j, h_cross=1.0 + 0.0j, diagnostics={})


def test_frozen_further_local_contract() -> None:
    assert FURTHER_LOCAL_FREQUENCIES == (
        0.325,
        0.375,
        0.825,
        0.875,
        0.925,
        0.975,
        1.525,
        1.575,
        1.625,
        1.675,
        1.7125,
        1.7375,
        2.7625,
        2.7875,
        2.825,
        2.875,
        2.925,
        2.975,
        3.7625,
        3.7875,
        3.825,
        3.875,
        3.925,
        3.975,
    )
    assert FREQUENCY_TOKENS[1.7125] == "1p7125"
    assert FURTHER_LOCAL_LMAX_VALUES[1.7375] == (96, 120, 144, 168)
    assert FURTHER_LOCAL_LMAX_VALUES[3.975] == (288, 312, 336, 360)
    assert SCHEMA_VERSION == (
        "phase5_t8aq_further_local_refinement_v1_units_dtype_ordering"
    )
    assert ADAPTER_NAME == "q018_tablei_further_local_transition"
    assert EXPECTED_ACTIVE_FILES == 53
    assert EXPECTED_MANIFEST_RECORDS == 52
    assert len(PARENT_REFINEMENTS) == 24
    assert PARENT_REFINEMENTS[10] == {
        "midpoint": 1.7125,
        "parent": [1.7, 1.725],
        "children": [[1.7, 1.7125], [1.7125, 1.725]],
        "parent_width": 0.025,
    }


def test_radial_cache_reuses_only_certified_domain() -> None:
    calls: list[float] = []

    def solve(**kwargs: object) -> SimpleNamespace:
        required = float(kwargs["boundary_config"].required_eval_radius)
        calls.append(required)
        return SimpleNamespace(r_grid=np.asarray([2.1, required]), valid_until_r=required)

    cache = further._FrequencyRadialCache(solve)
    base = further.BoundaryConfig(
        r_out=300.0,
        r_in_eps=1.0e-6,
        rtol=1.0e-10,
        atol=1.0e-12,
        required_eval_radius=40.0,
        experimental_required_radius_oracle=ADAPTER_NAME,
    )
    common = {"sector": "odd", "ell": 10, "k": 2.875, "background": SimpleNamespace(M=1.0)}
    far = cache(**common, boundary_config=base)
    near_config = further.BoundaryConfig(**{**base.__dict__, "required_eval_radius": 30.0})
    near = cache(**common, boundary_config=near_config)
    assert far is near
    assert calls == [40.0]

    local_calls: list[float] = []

    def local(**kwargs: object) -> SimpleNamespace:
        required = float(kwargs["boundary_config"].required_eval_radius)
        local_calls.append(required)
        return SimpleNamespace(
            r_grid=np.asarray([required, required + 1.0e-6]), valid_until_r=required
        )

    local_cache = further._FrequencyRadialCache(local)
    local_far = local_cache(**common, boundary_config=base)
    local_near = local_cache(**common, boundary_config=near_config)
    assert local_far is not local_near
    assert local_cache(**common, boundary_config=base) is local_far
    assert local_calls == [40.0, 30.0]


def _run_fake(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, dict[str, object]]:
    review, risk, adaptive, evidence, t4aa, gate, _ = _write_inputs(
        tmp_path, monkeypatch
    )
    output = tmp_path / "further"
    kwargs: dict[str, object] = {
        "output_dir": output,
        "accepted_review_npz": review,
        "accepted_risk_pilot_dir": risk,
        "accepted_adaptive_dir": adaptive,
        "accepted_t7bz_evidence": evidence,
        "accepted_t4aa_gate_dir": t4aa,
        "radial_gate_dir": gate,
        "resume": True,
        "polarization_solver": _FakePolarization.solve,
        "flat_solver": _fake_flat,
    }
    run_further_local_refinement(**kwargs)
    return output, kwargs


def test_run_writes_exact_contract_and_resume_skips(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _FakePolarization.calls = 0
    output, kwargs = _run_fake(tmp_path, monkeypatch)
    first_calls = _FakePolarization.calls
    assert first_calls == sum(
        len(FURTHER_LOCAL_LMAX_VALUES[k]) * 8 for k in FURTHER_LOCAL_FREQUENCIES
    )
    assert len(list((output / "frequencies").glob("*.npz"))) == 24
    assert len(list((output / "frequencies").glob("*.npz.json"))) == 24
    active = [
        path
        for path in output.rglob("*")
        if path.is_file() and "quarantine" not in path.parts
    ]
    assert len(active) == EXPECTED_ACTIVE_FILES
    with np.load(output / "further_local_values.npz", allow_pickle=False) as data:
        assert data["F_plus_complex"].shape == (24, 8)
        assert data["F_plus_complex"].dtype == np.dtype("complex128")
        metadata = json.loads(str(data["metadata_json"].item()))
        assert metadata["schema_version"] == SCHEMA_VERSION
        assert metadata["ordering"]["aggregate_field_axes"] == ["frequency", "point"]
    audit = json.loads((output / "further_local_sampling_audit.json").read_text())
    assert len(audit["phase_records"]) == 816
    assert len(audit["hierarchical_magnitude_records"]) == 768
    assert len(audit["sequence_summaries"]) == 80
    assert audit["acceptance_decision_emitted"] is False
    manifest_records = [
        line
        for line in (output / "manifest.md").read_text().splitlines()
        if line.startswith("- `")
    ]
    assert len(manifest_records) == EXPECTED_MANIFEST_RECORDS
    run_further_local_refinement(**kwargs)
    assert _FakePolarization.calls == first_calls


def test_tampered_transaction_is_quarantined_and_recomputed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _FakePolarization.calls = 0
    output, kwargs = _run_fake(tmp_path, monkeypatch)
    first_calls = _FakePolarization.calls
    sidecar = output / "frequencies" / "kM_0p325.npz.json"
    value = json.loads(sidecar.read_text())
    value["generation_contract_hash"] = "0" * 64
    sidecar.write_text(json.dumps(value), encoding="utf-8")
    run_further_local_refinement(**kwargs)
    assert _FakePolarization.calls == (
        first_calls + len(FURTHER_LOCAL_LMAX_VALUES[0.325]) * 8
    )
    assert len(list((output / "quarantine").glob("kM_0p325*"))) == 2


def test_tmp_or_unexpected_output_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    review, risk, adaptive, evidence, t4aa, gate, _ = _write_inputs(
        tmp_path, monkeypatch
    )
    output = tmp_path / "further"
    (output / "frequencies").mkdir(parents=True)
    (output / "frequencies" / "kM_0p325.npz.tmp").write_bytes(b"partial")
    with pytest.raises(FurtherLocalRefinementContractError, match="unexpected"):
        run_further_local_refinement(
            output_dir=output,
            accepted_review_npz=review,
            accepted_risk_pilot_dir=risk,
            accepted_adaptive_dir=adaptive,
            accepted_t7bz_evidence=evidence,
            accepted_t4aa_gate_dir=t4aa,
            radial_gate_dir=gate,
            resume=True,
            polarization_solver=_FakePolarization.solve,
            flat_solver=_fake_flat,
        )


def test_final_pair_failure_stops_without_transaction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    review, risk, adaptive, evidence, t4aa, gate, _ = _write_inputs(
        tmp_path, monkeypatch
    )

    def divergent(**kwargs: object) -> SimpleNamespace:
        lmax = int(kwargs["lmax"])
        return SimpleNamespace(h_plus=complex(lmax), h_cross=complex(lmax), diagnostics={})

    output = tmp_path / "further"
    with pytest.raises(
        FurtherLocalRefinementContractError, match="final adjacent lmax pair"
    ):
        run_further_local_refinement(
            output_dir=output,
            accepted_review_npz=review,
            accepted_risk_pilot_dir=risk,
            accepted_adaptive_dir=adaptive,
            accepted_t7bz_evidence=evidence,
            accepted_t4aa_gate_dir=t4aa,
            radial_gate_dir=gate,
            resume=True,
            polarization_solver=divergent,
            flat_solver=_fake_flat,
        )
    assert not list((output / "frequencies").glob("*.npz"))


def test_missing_t7ca_green_fails_before_compute(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    review, risk, adaptive, evidence, t4aa, gate, record = _write_inputs(
        tmp_path, monkeypatch
    )
    record.write_text("YELLOW\n", encoding="utf-8")
    _FakePolarization.calls = 0
    with pytest.raises(FurtherLocalRefinementContractError, match="T7ca exact GREEN"):
        run_further_local_refinement(
            output_dir=tmp_path / "further",
            accepted_review_npz=review,
            accepted_risk_pilot_dir=risk,
            accepted_adaptive_dir=adaptive,
            accepted_t7bz_evidence=evidence,
            accepted_t4aa_gate_dir=t4aa,
            radial_gate_dir=gate,
            resume=True,
            polarization_solver=_FakePolarization.solve,
            flat_solver=_fake_flat,
        )
    assert _FakePolarization.calls == 0


def test_attempted_lmax_extension_is_rejected_before_compute(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    review, risk, adaptive, evidence, t4aa, gate, _ = _write_inputs(
        tmp_path, monkeypatch
    )
    changed = dict(FURTHER_LOCAL_LMAX_VALUES)
    changed[0.325] = (*changed[0.325], 108)
    monkeypatch.setattr(further, "FURTHER_LOCAL_LMAX_VALUES", changed)
    _FakePolarization.calls = 0
    with pytest.raises(FurtherLocalRefinementContractError, match="lmax extension"):
        run_further_local_refinement(
            output_dir=tmp_path / "further",
            accepted_review_npz=review,
            accepted_risk_pilot_dir=risk,
            accepted_adaptive_dir=adaptive,
            accepted_t7bz_evidence=evidence,
            accepted_t4aa_gate_dir=t4aa,
            radial_gate_dir=gate,
            resume=True,
            polarization_solver=_FakePolarization.solve,
            flat_solver=_fake_flat,
        )
    assert _FakePolarization.calls == 0


def test_gate_change_between_transactions_stops_before_next_frequency(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    review, risk, adaptive, evidence, t4aa, gate, _ = _write_inputs(
        tmp_path, monkeypatch
    )
    calls = 0

    def mutate_after_first_frequency(**kwargs: object) -> SimpleNamespace:
        nonlocal calls
        calls += 1
        result = _FakePolarization.solve(**kwargs)
        if calls == len(FURTHER_LOCAL_LMAX_VALUES[0.325]) * 8:
            (gate / "manifest.md").write_text("changed during run\n", encoding="utf-8")
        return result

    output = tmp_path / "further"
    with pytest.raises(
        FurtherLocalRefinementContractError,
        match="frozen input changed during execution",
    ):
        run_further_local_refinement(
            output_dir=output,
            accepted_review_npz=review,
            accepted_risk_pilot_dir=risk,
            accepted_adaptive_dir=adaptive,
            accepted_t7bz_evidence=evidence,
            accepted_t4aa_gate_dir=t4aa,
            radial_gate_dir=gate,
            resume=True,
            polarization_solver=mutate_after_first_frequency,
            flat_solver=_fake_flat,
        )
    assert len(list((output / "frequencies").glob("*.npz"))) == 1


def test_unexpected_active_source_file_fails_cardinality_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    review, risk, adaptive, evidence, t4aa, gate, _ = _write_inputs(
        tmp_path, monkeypatch
    )
    (adaptive / "unexpected.txt").write_text("scope drift\n", encoding="utf-8")
    with pytest.raises(
        FurtherLocalRefinementContractError, match="accepted T8ap cardinality"
    ):
        run_further_local_refinement(
            output_dir=tmp_path / "further",
            accepted_review_npz=review,
            accepted_risk_pilot_dir=risk,
            accepted_adaptive_dir=adaptive,
            accepted_t7bz_evidence=evidence,
            accepted_t4aa_gate_dir=t4aa,
            radial_gate_dir=gate,
            resume=True,
            polarization_solver=_FakePolarization.solve,
            flat_solver=_fake_flat,
        )
