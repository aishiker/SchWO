from __future__ import annotations

from dataclasses import dataclass
import json

import numpy as np
import pytest

from schwgw.io.asymptotic import (
    FIG8_KM_VALUES,
    load_fig8_asymptotic_dataset,
    produce_fig8_asymptotic_dataset,
    save_fig8_asymptotic_dataset,
)


@dataclass
class _Solution:
    phase_factor: complex
    diagnostics: dict[str, float]


def _synthetic_radial_solver(sector, ell, k, background, boundary):
    del background
    assert boundary.r_in_eps == 1.0e-6
    assert boundary.r_out == 300.0
    assert boundary.rtol == 1.0e-10
    assert boundary.atol == 1.0e-12
    parity = 1.0 if getattr(sector, "value", sector) == "even" else -1.0
    phase = np.exp(1j * parity * (0.02 * ell + 0.01 * k))
    return _Solution(phase_factor=complex(phase), diagnostics={"residual": 1.0e-12})


def test_fig8_producer_uses_phase_factor_and_strict_round_trip(tmp_path) -> None:
    events = []
    dataset = produce_fig8_asymptotic_dataset(
        lmax=4,
        theta=np.array([0.2, 0.9, np.pi]),
        lmax_ladder=(4,),
        radial_solver=_synthetic_radial_solver,
        progress=events.append,
        source_command=["synthetic"],
    )

    assert np.array_equal(dataset.kM, FIG8_KM_VALUES)
    assert dataset.phase_factor_odd.shape == (4, 3)
    assert dataset.M22.shape == (4, 3, 3)
    assert dataset.lmax_ladder_cross_section.shape == (4, 1, 3, 3)
    assert dataset.theta[0] > 0.0
    assert len(events) == 24
    assert dataset.metadata["convention"]["phase_input"].startswith(
        "solution.phase_factor"
    )

    output = tmp_path / "fig8.npz"
    npz, sidecar = save_fig8_asymptotic_dataset(dataset, output)
    loaded = load_fig8_asymptotic_dataset(npz)
    assert sidecar.is_file()
    np.testing.assert_allclose(
        loaded.differential_cross_section, dataset.differential_cross_section
    )
    assert loaded.metadata == dataset.metadata
    with pytest.raises(FileExistsError, match="overwrite"):
        save_fig8_asymptotic_dataset(dataset, output)


def test_fig8_loader_rejects_missing_or_mismatched_sidecar(tmp_path) -> None:
    dataset = produce_fig8_asymptotic_dataset(
        lmax=4,
        theta=np.array([0.4, np.pi]),
        radial_solver=_synthetic_radial_solver,
    )
    output = tmp_path / "fig8.npz"
    save_fig8_asymptotic_dataset(dataset, output)
    output.with_suffix(".json").unlink()
    with pytest.raises(ValueError, match="sidecar is missing"):
        load_fig8_asymptotic_dataset(output)

    save_fig8_asymptotic_dataset(dataset, tmp_path / "fig8_other.npz")
    bad_sidecar = tmp_path / "fig8_other.json"
    payload = json.loads(bad_sidecar.read_text(encoding="utf-8"))
    payload["figure"] = 999
    bad_sidecar.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="metadata differ"):
        load_fig8_asymptotic_dataset(tmp_path / "fig8_other.npz")


def test_fig8_rejects_forward_axis_and_nonfinal_ladder() -> None:
    with pytest.raises(ValueError, match="theta"):
        produce_fig8_asymptotic_dataset(
            lmax=4, theta=np.array([0.0, np.pi]), radial_solver=_synthetic_radial_solver
        )
    with pytest.raises(ValueError, match="end at lmax"):
        produce_fig8_asymptotic_dataset(
            lmax=5,
            theta=np.array([0.4, np.pi]),
            lmax_ladder=(4,),
            radial_solver=_synthetic_radial_solver,
        )
