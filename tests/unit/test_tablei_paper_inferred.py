from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from schwgw.io.tablei_paper_inferred import (
    _compute_frequency,
    load_uniform_source_contract,
)
from schwgw.io.tablei import TABLEI_POINTS
from schwgw.io.tablei_uniform import UNIFORM_FREQUENCIES, _sha256
from schwgw.scattering.paper_projection import LHZEq42ResponseResult
from schwgw.scattering.weyl import StrictNPScalars


def _fake_response(**kwargs: object) -> LHZEq42ResponseResult:
    lmax = int(kwargs["lmax"])
    radius = float(kwargs["r"])
    scale = 1.0 + 1.0e-6 / lmax + 1.0e-4j * radius
    strict_plus = StrictNPScalars(1, 2, 3, 4, 5, frame="incident")
    strict_cross = StrictNPScalars(6, 7, 8, 9, 10, frame="incident")
    return LHZEq42ResponseResult(
        F_plus=scale,
        F_cross=scale + 1.0e-3j,
        h_plus_from_plus=scale,
        h_cross_from_cross=scale,
        h_cross_from_plus=0.01j,
        h_plus_from_cross=-0.02j,
        plus_strict_np=strict_plus,
        cross_strict_np=strict_cross,
        diagnostics={"test": True},
    )


def _unused_radial_solver(**kwargs: object) -> object:
    raise AssertionError(f"fake response must not call radial solver: {kwargs}")


def test_inferred_frequency_stores_two_lmax_response_and_strict_np_histories() -> None:
    arrays, metadata = _compute_frequency(
        0.1,
        lmax_pair=(60, 84),
        response_solver=_fake_response,
        radial_solver=_unused_radial_solver,
    )

    assert arrays["F_plus_history"].shape == (2, 8)
    assert arrays["F_cross_history"].shape == (2, 8)
    assert arrays["plus_strict_np_history"].shape == (2, 8, 5)
    assert arrays["cross_strict_np_history"].shape == (2, 8, 5)
    assert np.array_equal(arrays["plus_strict_np_history"][0, 0], np.arange(1, 6))
    assert metadata["route_b_used"] is False
    assert metadata["psi2_used_in_plus_or_cross"] is False
    assert metadata["max_final_pair_delta_plus"] < 1.0e-4


def test_uniform_source_contract_reconstructs_all_frozen_lmax_pairs(
    tmp_path: Path,
) -> None:
    lmax_source = tmp_path / "lmax_source.npz"
    pairs = np.asarray([(60 + index, 84 + index) for index in range(40)])
    np.savez(
        lmax_source,
        kM_values=np.asarray(UNIFORM_FREQUENCIES),
        final_lmax_pair=pairs,
    )
    source = tmp_path / "uniform.npz"
    np.savez(
        source,
        kM_values=np.asarray(UNIFORM_FREQUENCIES),
        point_ids=np.asarray([point.point_id for point in TABLEI_POINTS]),
    )
    binding_hash = _sha256(lmax_source)
    Path(str(source) + ".json").write_text(
        json.dumps(
            {
                "source_binding": [
                    {
                        "kM": km,
                        "kind": "accepted",
                        "row": index,
                        "source": str(lmax_source),
                        "sha256": binding_hash,
                    }
                    for index, km in enumerate(UNIFORM_FREQUENCIES)
                ]
            }
        ),
        encoding="utf-8",
    )

    schedule, bindings = load_uniform_source_contract(source)

    assert len(schedule) == 40
    assert len(bindings) == 40
    assert schedule[0.1] == (60, 84)
    assert schedule[1.0] == (69, 93)
    assert schedule[2.0] == (79, 103)
    assert schedule[4.0] == (99, 123)
