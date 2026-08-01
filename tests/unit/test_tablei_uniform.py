from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from schwgw.io.tablei import TABLEI_POINTS
from schwgw.io.tablei_uniform import (
    MISSING_FREQUENCIES,
    UNIFORM_FREQUENCIES,
    UNIFORM_LMAX_VALUES,
    UniformContractError,
    _frequency_paths,
    _sha256,
    merge_tablei_uniform,
    preflight_tablei_uniform,
    run_tablei_uniform_missing,
)
import schwgw.viz.tablei_uniform as uniform_viz


def _source(path: Path, frequencies: tuple[float, ...]) -> None:
    n = len(frequencies)
    values = np.asarray(frequencies)[:, None] + 1j * np.arange(8)[None, :]
    np.savez(
        path,
        kM_values=np.asarray(frequencies),
        point_ids=np.asarray([p.point_id for p in TABLEI_POINTS]),
        point_group=np.asarray([p.group for p in TABLEI_POINTS]),
        point_x=np.asarray([p.x for p in TABLEI_POINTS]),
        point_y=np.asarray([p.y for p in TABLEI_POINTS]),
        point_z=np.asarray([p.z for p in TABLEI_POINTS]),
        point_r=np.asarray([p.r for p in TABLEI_POINTS]),
        point_theta=np.asarray([p.theta for p in TABLEI_POINTS]),
        point_phi=np.asarray([p.phi for p in TABLEI_POINTS]),
        paper_theta_deg=np.asarray([p.paper_theta_deg for p in TABLEI_POINTS]),
        paper_xi_over_xi0=np.asarray([p.paper_xi_over_xi0 for p in TABLEI_POINTS]),
        F_plus_complex=values,
        F_cross_complex=2 * values,
        abs_F_plus=np.abs(values),
        abs_F_cross=np.abs(2 * values),
        arg_F_plus_principal=np.angle(values),
        arg_F_cross_principal=np.angle(2 * values),
        final_pair_delta_plus=np.full((n, 8), 1e-6),
        final_pair_delta_cross=np.full((n, 8), 1e-6),
    )


def _transaction(root: Path, km: float) -> None:
    npz, sidecar = _frequency_paths(root, km)
    npz.parent.mkdir(parents=True, exist_ok=True)
    value = np.full(8, km + 2j)
    np.savez(
        npz,
        kM=np.asarray(km),
        lmax_values=np.asarray(UNIFORM_LMAX_VALUES[km]),
        F_plus_complex=value,
        F_cross_complex=2 * value,
        abs_F_plus=np.abs(value),
        abs_F_cross=np.abs(2 * value),
        arg_F_plus_principal=np.angle(value),
        arg_F_cross_principal=np.angle(2 * value),
        final_pair_delta_plus=np.full(8, 1e-6),
        final_pair_delta_cross=np.full(8, 1e-6),
    )
    sidecar.write_text(
        json.dumps({"complete": True, "kM": km, "npz_sha256": _sha256(npz)}),
        encoding="utf-8",
    )


def test_schedule_is_exactly_the_missing_twenty_and_has_required_finals() -> None:
    assert len(MISSING_FREQUENCIES) == 20
    assert set(UNIFORM_LMAX_VALUES) == set(MISSING_FREQUENCIES)
    assert all(len(values) in {4, 5} for values in UNIFORM_LMAX_VALUES.values())
    assert UNIFORM_LMAX_VALUES[1.1][-1] == 132
    assert UNIFORM_LMAX_VALUES[3.7][-1] == 336


def test_selected_production_frequencies_must_be_an_ordered_missing_subset(
    tmp_path: Path,
) -> None:
    with pytest.raises(UniformContractError, match="ordered subset"):
        run_tablei_uniform_missing(output_dir=tmp_path, frequencies=(0.7, 0.6))
    with pytest.raises(UniformContractError, match="ordered subset"):
        run_tablei_uniform_missing(output_dir=tmp_path, frequencies=(0.6, 0.6))
    with pytest.raises(UniformContractError, match="ordered subset"):
        run_tablei_uniform_missing(output_dir=tmp_path, frequencies=(0.5,))


def test_preflight_and_merge_bind_each_direct_row_without_interpolation(
    tmp_path: Path,
) -> None:
    accepted = tuple(k for k in UNIFORM_FREQUENCIES if k not in MISSING_FREQUENCIES)
    review_k = tuple(
        k for k in accepted if k not in {0.4, 0.8, 0.9, 1.6, 1.7, 2.8, 2.9, 3.8, 3.9}
    )
    pilot_k = tuple(k for k in accepted if k not in review_k)
    review, pilot = tmp_path / "review.npz", tmp_path / "pilot.npz"
    _source(review, review_k)
    _source(pilot, pilot_k)
    tx = tmp_path / "transactions"
    for km in MISSING_FREQUENCIES:
        _transaction(tx, km)
    report = preflight_tablei_uniform(
        review_npz=review, pilot_npz=pilot, transaction_dir=tx
    )
    assert report["ready_to_merge"] is True
    output = merge_tablei_uniform(
        output_path=tmp_path / "uniform.npz",
        review_npz=review,
        pilot_npz=pilot,
        transaction_dir=tx,
    )
    with np.load(output, allow_pickle=False) as data:
        assert np.array_equal(data["kM_values"], np.asarray(UNIFORM_FREQUENCIES))
        assert data["F_plus_complex"].shape == (40, 8)
        assert data["F_plus_complex"][5, 0] == pytest.approx(0.6 + 2j)
    metadata = json.loads(Path(str(output) + ".json").read_text(encoding="utf-8"))
    assert len(metadata["source_binding"]) == 40
    assert metadata["no_interpolation"] is True


def test_merge_refuses_to_overwrite(tmp_path: Path) -> None:
    output = tmp_path / "uniform.npz"
    output.write_bytes(b"already exists")
    with pytest.raises(UniformContractError, match="overwrite"):
        merge_tablei_uniform(output_path=output, transaction_dir=tmp_path / "tx")


def test_renderer_uses_the_same_forty_samples_and_records_principal_phase(
    tmp_path: Path,
) -> None:
    source = tmp_path / "uniform.npz"
    phase = np.arange(40)[:, None] * np.linspace(0.1, 0.8, 8)
    values = np.exp(1j * phase)
    np.savez(
        source,
        kM_values=np.asarray(UNIFORM_FREQUENCIES),
        point_group=np.asarray([p.group for p in TABLEI_POINTS]),
        point_x=np.asarray([p.x for p in TABLEI_POINTS]),
        point_z=np.asarray([p.z for p in TABLEI_POINTS]),
        point_r=np.asarray([p.r for p in TABLEI_POINTS]),
        point_theta=np.asarray([p.theta for p in TABLEI_POINTS]),
        paper_xi_over_xi0=np.asarray([p.paper_xi_over_xi0 for p in TABLEI_POINTS]),
        F_plus_complex=values,
        F_cross_complex=2 * values,
    )

    paths = uniform_viz.render_tablei_uniform_figures(
        source,
        kirchhoff_complex=0.8 * values,
        output_dir=tmp_path / "figures",
        dpi=72,
    )
    assert all(path.is_file() for path in paths.values())
    sidecar = json.loads(paths["fig5_json"].read_text(encoding="utf-8"))
    assert sidecar["phase"] == "principal raw phase (np.angle); no display unwrap"
    assert "no scattering computation" in sidecar["kirchhoff"]


def test_renderer_rejects_invalid_kirchhoff_arrays(tmp_path: Path) -> None:
    source = tmp_path / "uniform.npz"
    values = np.ones((40, 8), dtype=np.complex128)
    np.savez(
        source,
        kM_values=np.asarray(UNIFORM_FREQUENCIES),
        point_group=np.asarray([p.group for p in TABLEI_POINTS]),
        point_x=np.asarray([p.x for p in TABLEI_POINTS]),
        point_z=np.asarray([p.z for p in TABLEI_POINTS]),
        point_r=np.asarray([p.r for p in TABLEI_POINTS]),
        point_theta=np.asarray([p.theta for p in TABLEI_POINTS]),
        paper_xi_over_xi0=np.asarray([p.paper_xi_over_xi0 for p in TABLEI_POINTS]),
        F_plus_complex=values,
        F_cross_complex=values,
    )
    with pytest.raises(uniform_viz.UniformFigureError, match="shape"):
        uniform_viz.render_tablei_uniform_figures(
            source,
            kirchhoff_complex=np.ones((40, 7), dtype=np.complex128),
            output_dir=tmp_path / "shape",
        )
    bad = values.copy()
    bad[0, 0] = np.nan + 0j
    with pytest.raises(uniform_viz.UniformFigureError, match="non-finite"):
        uniform_viz.render_tablei_uniform_figures(
            source,
            kirchhoff_complex=bad,
            output_dir=tmp_path / "finite",
        )
