from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import schwgw.io.tablei_risk_pilot as pilot
from schwgw.io.tablei_risk_pilot import (
    GENERATION_CONTRACT_HASH,
    METADATA_REPAIR_ID,
    METADATA_SCHEMA_VERSION,
    ORDERING_CONTRACT,
    PILOT_FREQUENCIES,
    PILOT_LMAX_VALUES,
    PilotContractError,
    UNITS_CONTRACT,
    repair_delta0p1_risk_pilot_metadata,
    run_delta0p1_risk_pilot,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_inputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path, Path]:
    review_dir = tmp_path / "review"
    review_dir.mkdir()
    review_npz = review_dir / "tablei_dense_review_values.npz"
    kM = np.asarray(
        [0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75,
         2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0],
        dtype=float,
    )
    point_ids = np.asarray([point.point_id for point in pilot.TABLEI_POINTS])
    shape = (18, 8)
    plus = np.exp(1j * kM[:, None] * np.linspace(0.2, 0.9, 8))
    cross = np.exp(1j * kM[:, None] * np.linspace(0.3, 1.0, 8))
    np.savez(
        review_npz,
        kM_values=kM,
        point_ids=point_ids,
        point_group=np.asarray([point.group for point in pilot.TABLEI_POINTS]),
        point_x=np.asarray([point.x for point in pilot.TABLEI_POINTS]),
        point_y=np.asarray([point.y for point in pilot.TABLEI_POINTS]),
        point_z=np.asarray([point.z for point in pilot.TABLEI_POINTS]),
        point_r=np.asarray([point.r for point in pilot.TABLEI_POINTS]),
        point_theta=np.asarray([point.theta for point in pilot.TABLEI_POINTS]),
        point_phi=np.asarray([point.phi for point in pilot.TABLEI_POINTS]),
        F_plus_complex=plus,
        F_cross_complex=cross,
        abs_F_plus=np.abs(plus),
        abs_F_cross=np.abs(cross),
        arg_F_plus_unwrapped=np.unwrap(np.angle(plus), axis=0),
        arg_F_cross_unwrapped=np.unwrap(np.angle(cross), axis=0),
        valid_ratio_plus_mask=np.ones(shape, dtype=bool),
        valid_ratio_cross_mask=np.ones(shape, dtype=bool),
    )
    review_json = review_npz.with_suffix(".npz.json")
    review_json.write_text("{}\n", encoding="utf-8")
    review_manifest = review_dir / "manifest.md"
    review_manifest.write_text("synthetic accepted review\n", encoding="utf-8")

    gate_dir = tmp_path / "gate"
    gate_dir.mkdir()
    for name in (
        "classification_manifest.json",
        "oracle_validation.json",
        "resume_preflight.json",
    ):
        (gate_dir / name).write_text("{}\n", encoding="utf-8")
    t7_record = tmp_path / "T7_current.md"
    t7_record.write_text(
        "ACCEPT GREEN / DELTA0P1 RISK-PILOT RADIAL GATE ACCEPTED\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        pilot,
        "_FROZEN_REVIEW_HASHES",
        {
            "npz": _sha(review_npz),
            "json": _sha(review_json),
            "manifest": _sha(review_manifest),
        },
    )
    monkeypatch.setattr(
        pilot,
        "_FROZEN_GATE_HASHES",
        {
            "classification_manifest.json": _sha(gate_dir / "classification_manifest.json"),
            "oracle_validation.json": _sha(gate_dir / "oracle_validation.json"),
            "resume_preflight.json": _sha(gate_dir / "resume_preflight.json"),
        },
    )
    monkeypatch.setattr(pilot, "_T7BV_RECORD_PATH", t7_record)
    return review_npz, gate_dir, t7_record


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


def test_frozen_pilot_contract() -> None:
    assert PILOT_FREQUENCIES == (0.4, 0.8, 0.9, 1.6, 1.7, 2.8, 2.9, 3.8, 3.9)
    assert PILOT_LMAX_VALUES[3.9] == (288, 312, 336, 360)


def test_t8ao_metadata_contract_constants() -> None:
    assert GENERATION_CONTRACT_HASH == (
        "92d650a89431d64d204125b9ff17929099e016ea774fc0914c4db1ad130b07d9"
    )
    assert METADATA_SCHEMA_VERSION == (
        "phase5_t8ao_delta0p1_risk_pilot_v2_units_ordering"
    )
    assert METADATA_REPAIR_ID == "T8ao/T7bx-units-ordering"
    assert ORDERING_CONTRACT["frequency_order"] == list(PILOT_FREQUENCIES)
    assert ORDERING_CONTRACT["point_order"] == [
        point.point_id for point in pilot.TABLEI_POINTS
    ]
    assert set(UNITS_CONTRACT) == {
        "per_frequency_arrays",
        "aggregate_arrays",
        "numeric_metadata",
    }
    assert callable(repair_delta0p1_risk_pilot_metadata)


def test_radial_cache_reuses_only_certified_domain() -> None:
    calls: list[float] = []

    def solve(**kwargs: object) -> SimpleNamespace:
        required = float(kwargs["boundary_config"].required_eval_radius)
        calls.append(required)
        return SimpleNamespace(r_grid=np.asarray([2.1, required]), valid_until_r=required)

    cache = pilot._FrequencyRadialCache(solve)
    common = {
        "sector": "odd",
        "ell": 10,
        "k": 2.8,
        "background": SimpleNamespace(M=1.0),
        "boundary_config": pilot.BoundaryConfig(
            r_out=300.0,
            r_in_eps=1.0e-6,
            rtol=1.0e-10,
            atol=1.0e-12,
            required_eval_radius=40.0,
            experimental_required_radius_oracle=pilot.ADAPTER_NAME,
        ),
    }
    far = cache(**common)
    near_config = pilot.BoundaryConfig(
        **{**common["boundary_config"].__dict__, "required_eval_radius": 30.0}
    )
    near = cache(**{**common, "boundary_config": near_config})
    assert far is near
    assert calls == [40.0]

    cache2 = pilot._FrequencyRadialCache(solve)
    near_first = cache2(**{**common, "boundary_config": near_config})
    far_after = cache2(**common)
    assert near_first is not far_after
    assert calls[-2:] == [30.0, 40.0]


def test_radial_cache_keeps_disjoint_point_local_solutions() -> None:
    calls: list[float] = []

    def solve(**kwargs: object) -> SimpleNamespace:
        required = float(kwargs["boundary_config"].required_eval_radius)
        calls.append(required)
        return SimpleNamespace(
            r_grid=np.asarray([required, required + 1.0e-6]),
            valid_until_r=required,
        )

    cache = pilot._FrequencyRadialCache(solve)
    base = pilot.BoundaryConfig(
        r_out=300.0,
        r_in_eps=1.0e-6,
        rtol=1.0e-10,
        atol=1.0e-12,
        required_eval_radius=40.0,
        experimental_required_radius_oracle=pilot.ADAPTER_NAME,
    )
    common = {
        "sector": "odd",
        "ell": 164,
        "k": 2.8,
        "background": SimpleNamespace(M=1.0),
    }
    far = cache(**common, boundary_config=base)
    near_config = pilot.BoundaryConfig(
        **{**base.__dict__, "required_eval_radius": 36.0}
    )
    near = cache(**common, boundary_config=near_config)
    far_again = cache(**common, boundary_config=base)

    assert far is not near
    assert far_again is far
    assert calls == [40.0, 36.0]
    assert cache.solve_count == 2
    assert cache.reuse_count == 1


def test_cache_key_changes_with_adapter_and_tolerances() -> None:
    base = pilot.BoundaryConfig(
        r_out=300.0,
        r_in_eps=1.0e-6,
        rtol=1.0e-10,
        atol=1.0e-12,
        required_eval_radius=30.0,
        experimental_required_radius_oracle=pilot.ADAPTER_NAME,
    )
    key = pilot._radial_cache_key("odd", 10, 2.8, SimpleNamespace(M=1.0), base)
    changed_tolerance = pilot._radial_cache_key(
        "odd", 10, 2.8, SimpleNamespace(M=1.0),
        pilot.BoundaryConfig(**{**base.__dict__, "rtol": 2.0e-10}),
    )
    changed_adapter = pilot._radial_cache_key(
        "odd", 10, 2.8, SimpleNamespace(M=1.0),
        pilot.BoundaryConfig(**{**base.__dict__, "experimental_required_radius_oracle": "other"}),
    )
    assert key != changed_tolerance
    assert key != changed_adapter


def test_run_writes_exact_transactions_and_resume_skips(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    review_npz, gate_dir, _ = _write_inputs(tmp_path, monkeypatch)
    out = tmp_path / "pilot"
    _FakePolarization.calls = 0
    run_delta0p1_risk_pilot(
        output_dir=out,
        accepted_review_npz=review_npz,
        radial_gate_dir=gate_dir,
        resume=True,
        polarization_solver=_FakePolarization.solve,
        flat_solver=_fake_flat,
    )
    first_calls = _FakePolarization.calls
    assert first_calls == sum(len(PILOT_LMAX_VALUES[k]) * 8 for k in PILOT_FREQUENCIES)
    assert len(list((out / "frequencies").glob("*.npz"))) == 9
    assert len(list((out / "frequencies").glob("*.npz.json"))) == 9
    assert {
        path.name for path in out.iterdir() if path.is_file()
    } == {
        "checkpoint_ledger.json",
        "risk_pilot_values.npz",
        "risk_pilot_values.npz.json",
        "risk_pilot_sampling_audit.json",
        "manifest.md",
    }
    with np.load(out / "risk_pilot_values.npz", allow_pickle=False) as aggregate:
        assert aggregate["F_plus_complex"].shape == (9, 8)
        assert aggregate["F_cross_complex"].shape == (9, 8)
    run_delta0p1_risk_pilot(
        output_dir=out,
        accepted_review_npz=review_npz,
        radial_gate_dir=gate_dir,
        resume=True,
        polarization_solver=_FakePolarization.solve,
        flat_solver=_fake_flat,
    )
    assert _FakePolarization.calls == first_calls


def test_tampered_transaction_is_quarantined_and_recomputed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    review_npz, gate_dir, _ = _write_inputs(tmp_path, monkeypatch)
    out = tmp_path / "pilot"
    _FakePolarization.calls = 0
    kwargs = dict(
        output_dir=out,
        accepted_review_npz=review_npz,
        radial_gate_dir=gate_dir,
        resume=True,
        polarization_solver=_FakePolarization.solve,
        flat_solver=_fake_flat,
    )
    run_delta0p1_risk_pilot(**kwargs)
    first_calls = _FakePolarization.calls
    sidecar = out / "frequencies" / "kM_0p4.npz.json"
    data = json.loads(sidecar.read_text())
    data["source_hashes"]["review_npz"] = "0" * 64
    sidecar.write_text(json.dumps(data), encoding="utf-8")
    run_delta0p1_risk_pilot(**kwargs)
    assert _FakePolarization.calls == first_calls + len(PILOT_LMAX_VALUES[0.4]) * 8
    assert len(list((out / "quarantine").glob("kM_0p4*"))) == 2


def test_tmp_or_unexpected_file_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    review_npz, gate_dir, _ = _write_inputs(tmp_path, monkeypatch)
    out = tmp_path / "pilot"
    (out / "frequencies").mkdir(parents=True)
    (out / "frequencies" / "kM_0p4.npz.tmp").write_bytes(b"partial")
    with pytest.raises(PilotContractError, match="unexpected"):
        run_delta0p1_risk_pilot(
            output_dir=out,
            accepted_review_npz=review_npz,
            radial_gate_dir=gate_dir,
            resume=True,
            polarization_solver=_FakePolarization.solve,
            flat_solver=_fake_flat,
        )


def test_final_pair_failure_stops_transaction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    review_npz, gate_dir, _ = _write_inputs(tmp_path, monkeypatch)

    def divergent(**kwargs: object) -> SimpleNamespace:
        lmax = int(kwargs["lmax"])
        return SimpleNamespace(
            h_plus=complex(lmax, 0.0), h_cross=complex(lmax, 0.0), diagnostics={}
        )

    with pytest.raises(PilotContractError, match="final adjacent lmax pair"):
        run_delta0p1_risk_pilot(
            output_dir=tmp_path / "pilot",
            accepted_review_npz=review_npz,
            radial_gate_dir=gate_dir,
            resume=True,
            polarization_solver=divergent,
            flat_solver=_fake_flat,
        )


def test_missing_t7bv_green_fails_before_compute(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    review_npz, gate_dir, t7_record = _write_inputs(tmp_path, monkeypatch)
    t7_record.write_text("YELLOW\n", encoding="utf-8")
    with pytest.raises(PilotContractError, match="T7bv exact GREEN"):
        run_delta0p1_risk_pilot(
            output_dir=tmp_path / "pilot",
            accepted_review_npz=review_npz,
            radial_gate_dir=gate_dir,
            resume=True,
            polarization_solver=_FakePolarization.solve,
            flat_solver=_fake_flat,
        )
