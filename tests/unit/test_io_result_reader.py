from __future__ import annotations

import json

import numpy as np
import pytest

from schwgw.io.results import GridResult, ResultFormatError, load_results, save_results


def test_load_results_reads_npz_round_trip(tmp_path):
    original = _synthetic_result()
    path = tmp_path / "result.npz"
    save_results(original, path)

    loaded = load_results(path)

    np.testing.assert_allclose(loaded.theta, original.theta)
    np.testing.assert_allclose(loaded.phi, original.phi)
    assert loaded.h_plus.dtype == np.complex128
    assert loaded.h_cross.dtype == np.complex128
    np.testing.assert_allclose(loaded.h_plus, original.h_plus)
    np.testing.assert_allclose(loaded.h_cross, original.h_cross)
    assert loaded.metadata["case_id"] == "SYNTH"


def test_load_results_reads_hdf5_round_trip(tmp_path):
    pytest.importorskip("h5py")
    original = _synthetic_result()
    path = tmp_path / "result.h5"
    save_results(original, path)

    loaded = load_results(path)

    np.testing.assert_allclose(loaded.theta, original.theta)
    np.testing.assert_allclose(loaded.phi, original.phi)
    np.testing.assert_allclose(loaded.h_plus, original.h_plus)
    np.testing.assert_allclose(loaded.h_cross, original.h_cross)
    assert loaded.metadata["config"]["wave"]["kM"] == 1.0


def test_load_results_reports_missing_npz_field(tmp_path):
    path = tmp_path / "bad.npz"
    np.savez(
        path,
        theta=np.array([0.0]),
        phi=np.array([0.0]),
        h_plus=np.array([[1.0 + 0.0j]]),
        metadata_json=np.asarray(json.dumps({})),
    )

    with pytest.raises(ResultFormatError, match="missing required field.*h_cross"):
        load_results(path)


def test_load_results_rejects_unknown_suffix(tmp_path):
    path = tmp_path / "result.txt"
    path.write_text("not a result", encoding="utf-8")

    with pytest.raises(ResultFormatError, match="Unsupported result suffix"):
        load_results(path)


def _synthetic_result() -> GridResult:
    theta = np.array([0.0, 0.2])
    phi = np.array([0.0, 0.3, 0.6])
    h_plus = np.array(
        [
            [1.0 + 0.5j, 2.0 + 0.25j, 3.0 - 0.25j],
            [4.0 + 0.0j, 5.0 - 0.5j, 6.0 - 0.75j],
        ],
        dtype=np.complex128,
    )
    return GridResult(
        theta=theta,
        phi=phi,
        h_plus=h_plus,
        h_cross=-h_plus,
        metadata={
            "case_id": "SYNTH",
            "created_at": "2026-07-05T00:00:00+00:00",
            "convention": {"fourier": "exp(-i k t)", "units": "G=c=M=1"},
            "config": {
                "wave": {"kM": 1.0},
                "observer": {"r": 60.0},
                "numerics": {"lmax": 2},
            },
            "lmax": 2,
        },
    )
