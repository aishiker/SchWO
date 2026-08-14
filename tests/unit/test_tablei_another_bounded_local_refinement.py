from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import schwgw.io.tablei_another_bounded_local_refinement as literal
from schwgw.io.tablei_another_bounded_local_refinement import (
    ADAPTER_NAME,
    EXPECTED_ACTIVE_FILES,
    EXPECTED_MANIFEST_RECORDS,
    FREQUENCY_TOKENS,
    ANOTHER_BOUNDED_LOCAL_FREQUENCIES,
    ANOTHER_BOUNDED_LOCAL_LMAX_VALUES,
    PARENT_REFINEMENTS,
    SCHEMA_VERSION,
    AnotherBoundedLocalRefinementContractError,
    run_another_bounded_local_refinement,
)


EXPECTED_FREQUENCIES = (
    0.86875, 0.94375, 0.95625, 0.96875,
    1.54375, 1.56875, 1.58125, 1.59375, 1.63125, 1.65625, 1.69375,
    1.703125, 1.715625,
    2.778125, 2.784375, 2.80625, 2.81875, 2.83125, 2.84375, 2.85625,
    2.86875, 2.88125, 2.89375, 2.90625, 2.91875, 2.93125, 2.94375,
    2.95625, 2.96875, 2.98125, 2.99375,
    3.753125, 3.759375, 3.765625, 3.771875, 3.778125, 3.784375,
    3.790625, 3.796875, 3.80625, 3.81875, 3.83125, 3.84375,
    3.85625, 3.86875, 3.88125, 3.89375, 3.90625, 3.91875,
    3.93125, 3.94375, 3.95625, 3.96875, 3.98125, 3.99375,
)


def _write_values(path: Path, frequencies: tuple[float, ...]) -> None:
    values = np.asarray(frequencies, dtype=np.float64)
    phase = np.linspace(0.1, 0.8, 8)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        kM_values=values,
        F_plus_complex=np.exp(1j * values[:, None] * phase),
        F_cross_complex=np.exp(1j * values[:, None] * (phase + 0.05)),
    )


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


def _fake_inputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[dict[str, object], Path]:
    prior = tuple(
        value
        for sequence in literal.SEQUENCES
        for value in sequence
        if value not in ANOTHER_BOUNDED_LOCAL_FREQUENCIES
    )
    assert len(prior) == len(set(prior))
    review = tmp_path / "review.npz"
    risk = tmp_path / "risk"
    adaptive = tmp_path / "adaptive"
    further = tmp_path / "further"
    t8ar = tmp_path / "t8ar"
    _write_values(review, prior)
    _write_values(risk / "risk_pilot_values.npz", ())
    _write_values(adaptive / "adaptive_refinement_values.npz", ())
    _write_values(further / "further_local_values.npz", ())
    _write_values(t8ar / "literal_failed_child_values.npz", ())
    identity = tmp_path / "identity.txt"
    identity.write_text("frozen\n", encoding="utf-8")
    source_paths = {"identity": str(identity)}
    source_hashes = {"identity": literal._sha256(identity)}
    gate_paths = {"gate": str(identity)}
    gate_hashes = {"gate": literal._sha256(identity)}
    monkeypatch.setattr(literal, "_validate_start_gate", lambda: None)
    monkeypatch.setattr(literal, "_validate_frozen_package", lambda: None)
    monkeypatch.setattr(
        literal,
        "_input_records",
        lambda *args: (source_paths, source_hashes, gate_paths, gate_hashes),
    )
    implementation = {
        "commit": "f" * 40,
        "paths": list(literal.IMPLEMENTATION_PATHS),
        "blobs": {
            path: {"git_blob": "e" * 40, "sha256": "d" * 64}
            for path in literal.IMPLEMENTATION_PATHS
        },
    }
    monkeypatch.setattr(literal, "_implementation_identity", lambda: implementation)
    monkeypatch.setattr(literal, "_verify_runtime_identity", lambda **kwargs: None)
    output = tmp_path / "output"
    kwargs: dict[str, object] = {
        "output_dir": output,
        "accepted_review_npz": review,
        "accepted_risk_pilot_dir": risk,
        "accepted_adaptive_dir": adaptive,
        "accepted_t7bz_evidence": identity,
        "accepted_t4aa_gate_dir": tmp_path / "t4aa",
        "accepted_further_local_dir": further,
        "accepted_t7cb_evidence": identity,
        "accepted_literal_failed_child_dir": t8ar,
        "accepted_t7cd_evidence": identity,
        "radial_gate_dir": tmp_path / "gate",
        "resume": True,
        "polarization_solver": _FakePolarization.solve,
        "flat_solver": _fake_flat,
    }
    return kwargs, output


def test_frozen_another_bounded_local_contract() -> None:
    assert ANOTHER_BOUNDED_LOCAL_FREQUENCIES == EXPECTED_FREQUENCIES
    assert len(FREQUENCY_TOKENS) == 55
    assert FREQUENCY_TOKENS[1.703125] == "1p703125"
    assert ANOTHER_BOUNDED_LOCAL_LMAX_VALUES[3.99375] == (288, 312, 336, 360)
    assert len(PARENT_REFINEMENTS) == 55
    assert ADAPTER_NAME == "q018_tablei_another_bounded_local_transition"
    assert SCHEMA_VERSION == (
        "phase5_t8as_another_bounded_local_refinement_v1_units_dtype_ordering"
    )
    assert EXPECTED_ACTIVE_FILES == 115
    assert EXPECTED_MANIFEST_RECORDS == 114


def test_run_writes_exact_contract_and_resume_skips(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _FakePolarization.calls = 0
    kwargs, output = _fake_inputs(tmp_path, monkeypatch)
    run_another_bounded_local_refinement(**kwargs)
    first_calls = _FakePolarization.calls
    assert first_calls == sum(
        len(ANOTHER_BOUNDED_LOCAL_LMAX_VALUES[k]) * 8
        for k in ANOTHER_BOUNDED_LOCAL_FREQUENCIES
    )
    assert len(list((output / "frequencies").glob("*.npz"))) == 55
    assert len(list((output / "frequencies").glob("*.npz.json"))) == 55
    active = [path for path in output.rglob("*") if path.is_file()]
    assert len(active) == EXPECTED_ACTIVE_FILES
    with np.load(output / "another_bounded_local_values.npz", allow_pickle=False) as data:
        assert data["F_plus_complex"].shape == (55, 8)
        assert data["F_plus_complex"].dtype == np.dtype("complex128")
        metadata = json.loads(str(data["metadata_json"].item()))
        assert metadata["schema_version"] == SCHEMA_VERSION
    audit = json.loads((output / "another_bounded_local_sampling_audit.json").read_text())
    assert audit["phase_record_count"] == 2352
    assert audit["hierarchical_magnitude_record_count"] == 1760
    assert len(audit["sequence_summaries"]) == 80
    assert audit["diagnostic_only"] is True
    assert audit["acceptance_decision_emitted"] is False
    assert sum(
        line.startswith("- `")
        for line in (output / "manifest.md").read_text().splitlines()
    ) == EXPECTED_MANIFEST_RECORDS
    run_another_bounded_local_refinement(**kwargs)
    assert _FakePolarization.calls == first_calls


def test_tampered_transaction_is_quarantined_and_recomputed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _FakePolarization.calls = 0
    kwargs, output = _fake_inputs(tmp_path, monkeypatch)
    run_another_bounded_local_refinement(**kwargs)
    first_calls = _FakePolarization.calls
    sidecar = output / "frequencies" / "kM_0p86875.npz.json"
    value = json.loads(sidecar.read_text())
    value["generation_contract_hash"] = "0" * 64
    sidecar.write_text(json.dumps(value), encoding="utf-8")
    run_another_bounded_local_refinement(**kwargs)
    assert _FakePolarization.calls == (
        first_calls + len(ANOTHER_BOUNDED_LOCAL_LMAX_VALUES[0.86875]) * 8
    )
    assert len(list((output / "quarantine").glob("kM_0p86875*"))) == 2


def test_tmp_output_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    kwargs, output = _fake_inputs(tmp_path, monkeypatch)
    (output / "frequencies").mkdir(parents=True)
    (output / "frequencies" / "kM_0p86875.npz.tmp").write_bytes(b"partial")
    with pytest.raises(AnotherBoundedLocalRefinementContractError, match="unexpected"):
        run_another_bounded_local_refinement(**kwargs)


def test_final_pair_failure_stops_without_transaction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    kwargs, output = _fake_inputs(tmp_path, monkeypatch)

    def divergent(**values: object) -> SimpleNamespace:
        lmax = int(values["lmax"])
        return SimpleNamespace(h_plus=complex(lmax), h_cross=complex(lmax), diagnostics={})

    kwargs["polarization_solver"] = divergent
    with pytest.raises(
        AnotherBoundedLocalRefinementContractError, match="final adjacent lmax pair"
    ):
        run_another_bounded_local_refinement(**kwargs)
    assert not list((output / "frequencies").glob("*.npz"))


def test_missing_t7ce_green_fails_before_compute(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = tmp_path / "T7.md"
    record.write_text("YELLOW\n", encoding="utf-8")
    monkeypatch.setattr(literal, "_T7CE_RECORD_PATH", record)
    with pytest.raises(AnotherBoundedLocalRefinementContractError, match="T7ce exact GREEN"):
        literal._validate_start_gate()


def test_attempted_lmax_extension_is_rejected_before_compute(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    changed = dict(ANOTHER_BOUNDED_LOCAL_LMAX_VALUES)
    changed[0.86875] = (*changed[0.86875], 108)
    monkeypatch.setattr(literal, "ANOTHER_BOUNDED_LOCAL_LMAX_VALUES", changed)
    with pytest.raises(AnotherBoundedLocalRefinementContractError, match="lmax extension"):
        literal._validate_frozen_scope()


def test_source_change_between_transactions_stops(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    kwargs, output = _fake_inputs(tmp_path, monkeypatch)
    checks = 0

    def verify(**values: object) -> None:
        nonlocal checks
        del values
        checks += 1
        if checks == 2:
            raise AnotherBoundedLocalRefinementContractError(
                "frozen input changed during execution"
            )

    monkeypatch.setattr(literal, "_verify_runtime_identity", verify)
    with pytest.raises(
        AnotherBoundedLocalRefinementContractError,
        match="frozen input changed during execution",
    ):
        run_another_bounded_local_refinement(**kwargs)
    assert len(list((output / "frequencies").glob("*.npz"))) == 1


def test_unexpected_active_source_file_fails_cardinality_gate(tmp_path: Path) -> None:
    risk = tmp_path / "risk"
    risk.mkdir()
    for index in range(24):
        (risk / f"file-{index}").write_text("scope drift\n", encoding="utf-8")
    with pytest.raises(
        AnotherBoundedLocalRefinementContractError, match="accepted T8ao cardinality"
    ):
        literal._input_records(
            tmp_path / "review.npz",
            risk,
            tmp_path / "adaptive",
            tmp_path / "T7bz.md",
            tmp_path / "t4aa",
            tmp_path / "further",
            tmp_path / "T7cb.md",
            tmp_path / "t8ar",
            tmp_path / "T7cd.md",
            tmp_path / "gate",
        )
