from __future__ import annotations

import hashlib
import json

import numpy as np
import pytest

from schwgw import cli
from schwgw.io.apparent import ApparentGridResult, save_apparent_results
from schwgw.viz.fig7_apparent import (
    Fig7ApparentPlotError,
    render_fig7_apparent_four_frequency,
)


def test_fig7_renderer_writes_publication_and_audit_artifacts(tmp_path) -> None:
    result_paths = _save_four_frequency_apparent_grids(tmp_path)

    artifacts = render_fig7_apparent_four_frequency(
        result_paths,
        output_dir=tmp_path / "rendered",
    )

    assert artifacts.pdf.read_bytes().startswith(b"%PDF")
    assert artifacts.display_png.read_bytes().startswith(b"\x89PNG")
    assert artifacts.audit_png.read_bytes().startswith(b"\x89PNG")
    manifest = json.loads(artifacts.manifest.read_text(encoding="utf-8"))
    assert manifest["physical_claim"] is False
    assert manifest["no_solver_rerun"] is True
    assert manifest["kM_values"] == [0.5, 1.0, 1.5, 2.0]
    assert manifest["display_policy"] == {
        "colormap": "viridis",
        "fixed_paper_color_limit": 0.9,
        "color_clipping_is_display_only": True,
        "interpolation_is_display_only": True,
        "numerical_audit_interpolation": "nearest",
        "physical_data_modified": False,
    }
    assert manifest["overlays"]["event_horizon"]["radius_over_M"] == 2.0
    assert manifest["overlays"]["light_ring"]["radius_over_M"] == pytest.approx(
        3.0 * np.sqrt(3.0)
    )
    assert [record["sha256"] for record in manifest["source_inputs"]] == [
        hashlib.sha256(path.read_bytes()).hexdigest() for path in result_paths
    ]
    assert manifest["row_color_scales"]["h_x"]["vmin"] == -manifest[
        "row_color_scales"
    ]["h_x"]["vmax"]
    assert len(
        {
            record["vmax"]
            for record in manifest["row_color_scales"].values()
        }
    ) == 1
    display_sidecar = json.loads(
        artifacts.display_png.with_suffix(".png.json").read_text(encoding="utf-8")
    )
    audit_sidecar = json.loads(
        artifacts.audit_png.with_suffix(".png.json").read_text(encoding="utf-8")
    )
    assert display_sidecar["artifact"]["display_interpolation"] == "bilinear"
    assert audit_sidecar["artifact"]["display_interpolation"] == "nearest"
    assert display_sidecar["artifact"]["display_interpolation_only"] is True


def test_fig7_renderer_rejects_wrong_frequency_order(tmp_path) -> None:
    result_paths = _save_four_frequency_apparent_grids(tmp_path)

    with pytest.raises(Fig7ApparentPlotError, match="in increasing kM order"):
        render_fig7_apparent_four_frequency(
            list(reversed(result_paths)),
            output_dir=tmp_path / "rendered",
        )


def test_fig7_renderer_cli_reads_saved_grids_only(tmp_path, monkeypatch) -> None:
    result_paths = _save_four_frequency_apparent_grids(tmp_path)
    monkeypatch.setattr(
        cli,
        "compute_polarization",
        lambda **_: (_ for _ in ()).throw(AssertionError("solver was called")),
        raising=False,
    )

    exit_code = cli.main(
        [
            "plot-fig7-apparent-four-frequency",
            *(str(path) for path in result_paths),
            "--out-dir",
            str(tmp_path / "cli-rendered"),
        ]
    )

    assert exit_code == 0
    manifest_path = tmp_path / "cli-rendered" / "fig7_apparent_four_frequency.manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["created_by_cli"] is True
    assert manifest["physical_claim"] is False


def _save_four_frequency_apparent_grids(tmp_path) -> list:
    paths = []
    for kM in (0.5, 1.0, 1.5, 2.0):
        path = tmp_path / f"apparent_kM_{kM:g}.npz"
        save_apparent_results(_synthetic_apparent_grid(kM), path)
        paths.append(path)
    return paths


def _synthetic_apparent_grid(kM: float) -> ApparentGridResult:
    x = np.linspace(-4.0, 4.0, 9)
    z = np.linspace(-4.0, 4.0, 9)
    xx, zz = np.meshgrid(x, z)
    radius = np.sqrt(xx**2 + zz**2)
    valid_mask = radius > 2.0
    base = (kM * xx + zz) + 1j * (xx - kM * zz)
    fields = {}
    for name, factor in (("h_x", 1.0), ("h_y", -0.5), ("h_b", 0.25)):
        values = np.full(base.shape, np.nan + 1j * np.nan, dtype=np.complex128)
        values[valid_mask] = factor * base[valid_mask]
        fields[name] = values
    fields["h_longitudinal"] = 2.0 * fields["h_b"]
    return ApparentGridResult(
        x=x,
        z=z,
        r=radius,
        theta=np.zeros_like(radius),
        phi=np.zeros_like(radius),
        valid_mask=valid_mask,
        h_x=fields["h_x"],
        h_y=fields["h_y"],
        h_b=fields["h_b"],
        h_longitudinal=fields["h_longitudinal"],
        metadata={
            "case_id": f"SYNTH_FIG7_K{kM:g}",
            "physical_claim": False,
            "config": {
                "background": {"M": 1.0},
                "wave": {"kM": kM},
            },
        },
    )
