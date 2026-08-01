from __future__ import annotations

import json
from types import SimpleNamespace

import numpy as np
import pytest

from schwgw.io import parse_config
from schwgw.io.apparent import (
    load_apparent_results,
    run_apparent_solver_grid,
    save_apparent_results,
)


def _config():
    return parse_config(
        {
            "case_id": "SYNTH_FIG7",
            "output": "unused.npz",
            "background": {"M": 1.0},
            "wave": {
                "kM": 1.0,
                "A_plus": {"real": 1.0, "imag": 0.0},
                "A_cross": {"real": 0.0, "imag": 0.0},
            },
            "observer": {
                "kind": "xz_plane",
                "x_values": [-3.0, 0.0, 3.0],
                "z_values": [-3.0, 0.0, 3.0],
                "invalid_radius_policy": "mask",
            },
            "numerics": {
                "lmax": 2,
                "boundary": {
                    "r_in_eps": 1.0e-6,
                    "r_out": 20.0,
                    "rtol": 1.0e-10,
                    "atol": 1.0e-12,
                },
            },
        }
    )


def _fake_solver(**kwargs):
    value = complex(kwargs["r"], kwargs["theta"])
    return SimpleNamespace(
        h_x=value,
        h_y=2.0 * value,
        h_b=3.0 * value,
        h_longitudinal=6.0 * value,
        physical_claim=False,
        diagnostics={"radial_solve_count": 0.0},
    )


def test_apparent_grid_roundtrip_preserves_masks_fields_and_nonclaim(tmp_path) -> None:
    result = run_apparent_solver_grid(_config(), apparent_solver=_fake_solver)
    output = tmp_path / "fig7.npz"
    save_apparent_results(result, output)
    loaded = load_apparent_results(output)

    np.testing.assert_array_equal(loaded.valid_mask, result.valid_mask)
    np.testing.assert_array_equal(loaded.h_x, result.h_x)
    np.testing.assert_array_equal(loaded.h_longitudinal, 2.0 * loaded.h_b)
    assert loaded.metadata["physical_claim"] is False
    assert loaded.metadata["schema_version"] == "li_hou_zhao_fig7_apparent_xz_v1"
    assert json.loads(str(np.load(output)["metadata_json"]))["figure"] == 7


def test_apparent_grid_refuses_overwrite_and_physical_claim(tmp_path) -> None:
    result = run_apparent_solver_grid(_config(), apparent_solver=_fake_solver)
    output = tmp_path / "fig7.npz"
    save_apparent_results(result, output)
    with pytest.raises(FileExistsError, match="overwrite"):
        save_apparent_results(result, output)

    def bad_solver(**kwargs):
        result = _fake_solver(**kwargs)
        return SimpleNamespace(**{**result.__dict__, "physical_claim": True})

    with pytest.raises(RuntimeError, match="physical_claim"):
        run_apparent_solver_grid(_config(), apparent_solver=bad_solver)
