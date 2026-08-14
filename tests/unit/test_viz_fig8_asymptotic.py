from __future__ import annotations

import json

import numpy as np

from schwgw.io.asymptotic import (
    produce_fig8_asymptotic_dataset,
    save_fig8_asymptotic_dataset,
)
from schwgw.viz.fig8_asymptotic import render_fig8_asymptotic_four_frequency


class _Solution:
    def __init__(self, phase_factor: complex) -> None:
        self.phase_factor = phase_factor
        self.diagnostics = {"synthetic": 0.0}


def _solver(sector, ell, k, background, boundary):
    del background, boundary
    parity = 1.0 if sector.value == "even" else -1.0
    return _Solution(np.exp(1j * parity * (ell + k) * 0.03))


def test_fig8_renderer_preserves_missing_forward_axis_and_writes_sidecars(
    tmp_path,
) -> None:
    dataset = produce_fig8_asymptotic_dataset(
        lmax=4, theta=np.array([0.2, 0.8, np.pi]), radial_solver=_solver
    )
    source, _ = save_fig8_asymptotic_dataset(dataset, tmp_path / "fig8.npz")
    artifacts = render_fig8_asymptotic_four_frequency(
        source, output_dir=tmp_path / "render"
    )

    assert artifacts.pdf.read_bytes().startswith(b"%PDF")
    assert artifacts.png.read_bytes().startswith(b"\x89PNG")
    manifest = json.loads(artifacts.manifest.read_text(encoding="utf-8"))
    assert manifest["no_solver_rerun"] is True
    assert manifest["styles"] == {
        "q0": "blue dots",
        "q1": "green dashed",
        "q2": "red solid",
    }
    assert manifest["forward_axis"] == {
        "theta_zero_present": False,
        "masked_or_missing": True,
        "cropped": False,
        "smoothed": False,
    }
    assert artifacts.pdf.with_suffix(".pdf.json").is_file()
    png_sidecar = json.loads(
        artifacts.png.with_suffix(".png.json").read_text(encoding="utf-8")
    )
    assert png_sidecar["artifact"]["dpi"] == 600
