from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from schwgw.io.results import (
    AmplificationGridResult,
    GridResult,
    load_amplification_results,
    load_results,
)


COMPONENTS = {"h_plus", "h_cross"}
QUANTITIES = {"real", "imag", "abs", "phase"}
AMPLIFICATION_QUANTITIES = {
    "F_pol_norm",
    "I_pol_ratio",
    "amplification_plus",
    "amplification_cross",
    "abs_F_plus",
    "abs_F_cross",
    "phase_plus",
    "phase_cross",
    "intensity_plus_ratio",
    "intensity_cross_ratio",
}
FIG3_INTERPOLATIONS = {"nearest", "bilinear", "bicubic"}
FIG3_RENDER_STYLES = {"default", "publication"}
DEFAULT_FIG3_DPI = 180
FIGURE_OUTPUT_FORMATS = {"png", "pdf"}


class PlotError(ValueError):
    """Raised when a saved result cannot be plotted as requested."""


def plot_wavefield_from_result(
    result_path: str | Path,
    *,
    component: str,
    quantity: str,
    output_path: str | Path,
) -> Path:
    """Plot a stored complex field component without recomputing physics."""

    _validate_component_quantity(component, quantity)
    result = load_results(result_path)
    values = _quantity_values(getattr(result, component), quantity)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    _render_values(result, values, component=component, quantity=quantity, output_path=output)
    sidecar = output.with_suffix(output.suffix + ".json")
    sidecar.write_text(
        json.dumps(
            _plot_metadata(
                result,
                source_result_path=Path(result_path),
                component=component,
                quantity=quantity,
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return sidecar


def plot_amplification_from_result(
    result_path: str | Path,
    *,
    quantity: str,
    output_path: str | Path,
    dpi: int = DEFAULT_FIG3_DPI,
) -> Path:
    """Plot a stored M5 amplification quantity from saved fields only."""

    dpi = _validate_dpi(dpi)
    result = load_amplification_results(result_path)
    values, valid_ratio_mask, mask_field = _amplification_quantity_values(
        result,
        quantity,
    )
    if values.shape != valid_ratio_mask.shape:
        raise PlotError(f"{quantity} shape does not match {mask_field}.")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output_format = _output_format(output)
    _render_amplification_values(
        result,
        values=values,
        valid_ratio_mask=valid_ratio_mask,
        quantity=quantity,
        output_path=output,
        dpi=dpi,
        output_format=output_format,
    )

    sidecar = output.with_suffix(output.suffix + ".json")
    sidecar.write_text(
        json.dumps(
            _amplification_plot_metadata(
                result,
                source_result_path=Path(result_path),
                quantity=quantity,
                mask_field=mask_field,
                valid_ratio_mask=valid_ratio_mask,
                values=values,
                output_path=output,
                dpi=dpi,
                output_format=output_format,
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return sidecar


def plot_convergence_from_result(result_path: str | Path, *, output_path: str | Path) -> Path:
    """Plot saved convergence history, if present in result metadata."""

    result = load_results(result_path)
    diagnostics = result.metadata.get("diagnostics", {})
    history = diagnostics.get("lmax_convergence_history")
    if not history:
        raise PlotError(
            "Result metadata does not contain lmax_convergence_history; "
            "plot-convergence will not rerun the solver."
        )
    policy = diagnostics.get("lmax_convergence_policy", {})
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    _render_convergence_history(history, policy=policy, output_path=output)

    sidecar = output.with_suffix(output.suffix + ".json")
    sidecar.write_text(
        json.dumps(
            _convergence_plot_metadata(
                result,
                source_result_path=Path(result_path),
                history=history,
                policy=policy,
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return sidecar


def plot_fig3_panel_from_result(
    result_path: str | Path,
    *,
    quantity: str,
    interpolation: str = "nearest",
    output_path: str | Path,
    dpi: int = DEFAULT_FIG3_DPI,
) -> Path:
    """Plot the single-frequency Fig.3-lite x-z panel from saved fields only."""

    if quantity != "real":
        raise PlotError("plot-fig3-panel supports only quantity='real' in this slice.")
    if interpolation not in FIG3_INTERPOLATIONS:
        raise PlotError(
            f"interpolation must be one of {sorted(FIG3_INTERPOLATIONS)}."
        )
    dpi = _validate_dpi(dpi)

    result = load_results(result_path)
    _require_xz_plane(result, command="plot-fig3-panel")

    h_plus_values = _quantity_values(result.h_plus, quantity)
    h_cross_values = _quantity_values(result.h_cross, quantity)
    color_vmin, color_vmax = _symmetric_color_limits(
        result,
        [h_plus_values, h_cross_values],
    )
    mass = _background_mass(result)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output_format = _output_format(output)
    _render_fig3_panel(
        result,
        h_plus_values=h_plus_values,
        h_cross_values=h_cross_values,
        color_vmin=color_vmin,
        color_vmax=color_vmax,
        interpolation=interpolation,
        mass=mass,
        output_path=output,
        dpi=dpi,
        output_format=output_format,
    )

    sidecar = output.with_suffix(output.suffix + ".json")
    sidecar.write_text(
        json.dumps(
            _fig3_panel_metadata(
                result,
                source_result_path=Path(result_path),
                quantity=quantity,
                interpolation=interpolation,
                color_vmin=color_vmin,
                color_vmax=color_vmax,
                mass=mass,
                dpi=dpi,
                output_format=output_format,
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return sidecar


def plot_fig3_multifrequency_panel_from_results(
    result_paths: list[str | Path] | tuple[str | Path, ...],
    *,
    quantity: str,
    interpolation: str = "nearest",
    output_path: str | Path,
    dpi: int = DEFAULT_FIG3_DPI,
    style: str = "default",
) -> Path:
    """Plot the four-frequency Fig.3-lite x-z panel from saved fields only."""

    if len(result_paths) != 4:
        raise PlotError("plot-fig3-multifrequency-panel requires exactly four inputs.")
    if quantity != "real":
        raise PlotError(
            "plot-fig3-multifrequency-panel supports only quantity='real' in this slice."
        )
    if interpolation not in FIG3_INTERPOLATIONS:
        raise PlotError(
            f"interpolation must be one of {sorted(FIG3_INTERPOLATIONS)}."
        )
    dpi = _validate_dpi(dpi)
    style = _validate_fig3_render_style(style)

    paths = [Path(path) for path in result_paths]
    results = [load_results(path) for path in paths]
    for result in results:
        _require_xz_plane(result, command="plot-fig3-multifrequency-panel")

    kM_values = [_required_wave_kM(result) for result in results]
    expected_kM_values = [0.5, 1.0, 1.5, 2.0]
    if not np.allclose(kM_values, expected_kM_values, rtol=0.0, atol=1.0e-12):
        raise PlotError(
            "plot-fig3-multifrequency-panel requires kM values "
            "[0.5, 1.0, 1.5, 2.0] in increasing kM order."
        )
    _require_matching_xz_coordinates(results)

    h_plus_values = [_quantity_values(result.h_plus, quantity) for result in results]
    h_cross_values = [_quantity_values(result.h_cross, quantity) for result in results]
    row_color_scales = {
        "h_plus": _symmetric_color_limits_across_results(results, h_plus_values),
        "h_cross": _symmetric_color_limits_across_results(results, h_cross_values),
    }
    mass = _shared_background_mass(results)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output_format = _output_format(output)
    _render_fig3_multifrequency_panel(
        results,
        h_plus_values=h_plus_values,
        h_cross_values=h_cross_values,
        kM_values=kM_values,
        row_color_scales=row_color_scales,
        interpolation=interpolation,
        mass=mass,
        output_path=output,
        dpi=dpi,
        output_format=output_format,
        style=style,
    )

    sidecar = output.with_suffix(output.suffix + ".json")
    sidecar.write_text(
        json.dumps(
            _fig3_multifrequency_panel_metadata(
                results,
                source_result_paths=paths,
                kM_values=kM_values,
                quantity=quantity,
                interpolation=interpolation,
                row_color_scales=row_color_scales,
                mass=mass,
                dpi=dpi,
                output_format=output_format,
                style=style,
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return sidecar


def plot_fig4_exact_angular_from_result(
    result_path: str | Path,
    *,
    output_path: str | Path,
    phi: float = 0.0,
    dpi: int = 300,
    _created_by_cli: bool = False,
) -> Path:
    """Plot fixed-phi Fig.4 exact angular curves from saved fields only."""

    dpi = _validate_dpi(dpi)
    source_path = Path(result_path)
    result = load_results(source_path)
    theta, phi_values = _require_fig4_exact_angular_result(result)
    phi_index = _strict_phi_index(phi_values, phi)
    abs_h_plus = np.abs(result.h_plus[:, phi_index])
    abs_h_cross = np.abs(result.h_cross[:, phi_index])

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output_format = _output_format(output)
    if output_format != "png":
        raise PlotError("plot-fig4-exact-angular supports PNG output in this slice.")
    _render_fig4_exact_angular_curves(
        theta,
        abs_h_plus=abs_h_plus,
        abs_h_cross=abs_h_cross,
        output_path=output,
        dpi=dpi,
    )

    sidecar = output.with_suffix(output.suffix + ".json")
    sidecar.write_text(
        json.dumps(
            _fig4_exact_angular_metadata(
                result,
                source_result_path=source_path,
                output_path=output,
                phi_selected=float(phi_values[phi_index]),
                phi_selected_index=phi_index,
                dpi=dpi,
                output_format=output_format,
                created_by_cli=_created_by_cli,
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return sidecar


def plot_fig4_all_frequency_exact_angular_from_results(
    result_paths: list[str | Path] | tuple[str | Path, ...],
    *,
    output_path: str | Path,
    phi: float = 0.0,
    dpi: int = 300,
    _created_by_cli: bool = False,
) -> Path:
    """Plot fixed-phi all-frequency Fig.4 exact angular curves from saved fields."""

    if len(result_paths) != 4:
        raise PlotError(
            "plot-fig4-all-frequency-exact-angular requires exactly four inputs."
        )
    dpi = _validate_dpi(dpi)

    paths = [Path(path) for path in result_paths]
    results = [load_results(path) for path in paths]
    coordinates = [_require_fig4_exact_angular_result(result) for result in results]
    theta = coordinates[0][0]
    phi_values = coordinates[0][1]
    _require_fig4_production_angular_shapes(results, coordinates)
    _require_matching_angular_coordinates(coordinates)

    kM_values = [_required_fig4_wave_kM(result) for result in results]
    expected_kM_values = [0.5, 1.0, 1.5, 2.0]
    if not np.allclose(kM_values, expected_kM_values, rtol=0.0, atol=1.0e-12):
        raise PlotError(
            "plot-fig4-all-frequency-exact-angular requires kM values "
            "[0.5, 1.0, 1.5, 2.0] in increasing kM order."
        )

    phi_index = _strict_phi_index(phi_values, phi)
    abs_h_plus = [np.abs(result.h_plus[:, phi_index]) for result in results]
    abs_h_cross = [np.abs(result.h_cross[:, phi_index]) for result in results]

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output_format = _output_format(output)
    if output_format != "png":
        raise PlotError(
            "plot-fig4-all-frequency-exact-angular supports PNG output in this slice."
        )
    _render_fig4_all_frequency_exact_angular_curves(
        theta,
        abs_h_plus=abs_h_plus,
        abs_h_cross=abs_h_cross,
        kM_values=kM_values,
        output_path=output,
        dpi=dpi,
    )

    sidecar = output.with_suffix(output.suffix + ".json")
    sidecar.write_text(
        json.dumps(
            _fig4_all_frequency_exact_angular_metadata(
                results,
                source_result_paths=paths,
                output_path=output,
                phi_selected=float(phi_values[phi_index]),
                phi_selected_index=phi_index,
                dpi=dpi,
                output_format=output_format,
                created_by_cli=_created_by_cli,
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return sidecar


def plot_tablei_four_frequency_report(
    extraction_path: str | Path,
    *,
    output_dir: str | Path,
    dpi: int = DEFAULT_FIG3_DPI,
    _created_by_cli: bool = False,
) -> dict[str, Path]:
    """Create read-only Table-I four-frequency reporting artifacts."""

    dpi = _validate_dpi(dpi)
    source_npz = Path(extraction_path)
    source_json = source_npz.with_suffix(source_npz.suffix + ".json")
    if not source_json.is_file():
        raise PlotError("Table-I extraction JSON sidecar is required.")

    table = _load_tablei_extraction(source_npz)
    sidecar_metadata = json.loads(source_json.read_text(encoding="utf-8"))
    _validate_tablei_metadata(table, sidecar_metadata)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "tablei_four_frequency_values.csv"
    markdown_path = out_dir / "tablei_four_frequency_values.md"
    near_png = out_dir / "fig5_near_axis_tablei_four_frequency_pilot.png"
    far_png = out_dir / "fig6_far_axis_tablei_four_frequency_pilot.png"

    _write_tablei_csv(table, csv_path)
    _write_tablei_markdown(table, markdown_path)
    _render_tablei_group_pilot(
        table,
        group="near_axis",
        output_path=near_png,
        dpi=dpi,
    )
    _render_tablei_group_pilot(
        table,
        group="far_axis",
        output_path=far_png,
        dpi=dpi,
    )

    artifact_paths = {
        "csv": csv_path,
        "markdown": markdown_path,
        "near_axis_png": near_png,
        "far_axis_png": far_png,
    }
    near_sidecar = near_png.with_suffix(near_png.suffix + ".json")
    far_sidecar = far_png.with_suffix(far_png.suffix + ".json")
    for group, png_path, sidecar_path in [
        ("near_axis", near_png, near_sidecar),
        ("far_axis", far_png, far_sidecar),
    ]:
        sidecar_path.write_text(
            json.dumps(
                _tablei_report_sidecar_metadata(
                    table,
                    extraction_metadata=sidecar_metadata,
                    source_npz=source_npz,
                    source_json=source_json,
                    artifact_paths=artifact_paths,
                    plotted_group=group,
                    output_path=png_path,
                    dpi=dpi,
                    created_by_cli=_created_by_cli,
                ),
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    return {
        "csv": csv_path,
        "markdown": markdown_path,
        "near_axis_png": near_png,
        "near_axis_sidecar": near_sidecar,
        "far_axis_png": far_png,
        "far_axis_sidecar": far_sidecar,
    }


def _load_tablei_extraction(path: Path) -> dict[str, Any]:
    required = [
        "kM_values",
        "point_ids",
        "point_group",
        "point_x",
        "point_y",
        "point_z",
        "point_r",
        "point_theta",
        "point_phi",
        "paper_theta_deg",
        "paper_xi_over_xi0",
        "x_indices",
        "z_indices",
        "F_plus_complex",
        "F_cross_complex",
        "abs_F_plus",
        "abs_F_cross",
        "arg_F_plus_principal",
        "arg_F_cross_principal",
        "arg_F_plus_unwrapped",
        "arg_F_cross_unwrapped",
        "valid_ratio_plus_mask",
        "valid_ratio_cross_mask",
        "valid_ratio_norm_mask",
        "valid_field_mask",
        "source_valid_mask",
    ]
    with np.load(path, allow_pickle=False) as data:
        missing = [name for name in required if name not in data.files]
        if missing:
            raise PlotError(f"Table-I extraction missing arrays: {missing}.")
        table = {name: np.array(data[name]) for name in required}
        if "metadata_json" in data.files:
            table["embedded_metadata_json"] = str(data["metadata_json"])
    _validate_tablei_shapes(table)
    return table


def _validate_tablei_shapes(table: dict[str, Any]) -> None:
    kM = table["kM_values"]
    point_ids = table["point_ids"]
    if kM.ndim != 1 or point_ids.ndim != 1:
        raise PlotError("Table-I kM_values and point_ids must be one-dimensional.")
    shape = (int(kM.size), int(point_ids.size))
    matrix_names = [
        "F_plus_complex",
        "F_cross_complex",
        "abs_F_plus",
        "abs_F_cross",
        "arg_F_plus_principal",
        "arg_F_cross_principal",
        "arg_F_plus_unwrapped",
        "arg_F_cross_unwrapped",
        "valid_ratio_plus_mask",
        "valid_ratio_cross_mask",
        "valid_ratio_norm_mask",
        "valid_field_mask",
        "source_valid_mask",
    ]
    for name in matrix_names:
        if table[name].shape != shape:
            raise PlotError(f"Table-I {name} shape must be {shape}.")
    for name in [
        "point_group",
        "point_x",
        "point_y",
        "point_z",
        "point_r",
        "point_theta",
        "point_phi",
        "paper_theta_deg",
        "paper_xi_over_xi0",
        "x_indices",
        "z_indices",
    ]:
        if table[name].shape != point_ids.shape:
            raise PlotError(f"Table-I {name} shape must match point_ids.")
    expected = np.asarray([0.5, 1.0, 1.5, 2.0], dtype=float)
    if kM.shape != expected.shape or not np.allclose(kM, expected, rtol=0.0, atol=1e-12):
        raise PlotError("Table-I reporting requires kM=[0.5,1.0,1.5,2.0].")


def _validate_tablei_metadata(
    table: dict[str, Any],
    metadata: dict[str, Any],
) -> None:
    if metadata.get("case_id") is None:
        raise PlotError("Table-I extraction sidecar missing case_id.")
    for key in [
        "no_solver_rerun",
        "no_field_recomputation",
        "no_interpolation",
        "no_kirchhoff_baseline",
        "not_paper_level_dense_scan",
        "no_kM4",
        "no_dense_Mk_scan",
        "no_new_physics_convention",
    ]:
        if metadata.get(key) is not True:
            raise PlotError(f"Table-I extraction sidecar must record {key}=true.")
    if "embedded_metadata_json" in table:
        embedded = json.loads(table["embedded_metadata_json"])
        if embedded != metadata:
            raise PlotError("Table-I embedded metadata_json differs from JSON sidecar.")


def _write_tablei_csv(table: dict[str, Any], output_path: Path) -> None:
    headers = [
        "kM",
        "point_id",
        "point_group",
        "x",
        "y",
        "z",
        "r",
        "theta",
        "phi",
        "paper_theta_deg",
        "paper_xi_over_xi0",
        "x_index",
        "z_index",
        "valid_ratio_plus_mask",
        "F_plus_real",
        "F_plus_imag",
        "abs_F_plus",
        "arg_F_plus_principal",
        "arg_F_plus_unwrapped",
        "valid_ratio_cross_mask",
        "F_cross_real",
        "F_cross_imag",
        "abs_F_cross",
        "arg_F_cross_principal",
        "arg_F_cross_unwrapped",
        "valid_ratio_norm_mask",
        "valid_field_mask",
        "source_valid_mask",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        for frequency_index, kM in enumerate(table["kM_values"]):
            for point_index, point_id in enumerate(table["point_ids"]):
                f_plus = table["F_plus_complex"][frequency_index, point_index]
                f_cross = table["F_cross_complex"][frequency_index, point_index]
                writer.writerow(
                    [
                        _csv_value(kM),
                        str(point_id),
                        str(table["point_group"][point_index]),
                        _csv_value(table["point_x"][point_index]),
                        _csv_value(table["point_y"][point_index]),
                        _csv_value(table["point_z"][point_index]),
                        _csv_value(table["point_r"][point_index]),
                        _csv_value(table["point_theta"][point_index]),
                        _csv_value(table["point_phi"][point_index]),
                        _csv_value(table["paper_theta_deg"][point_index]),
                        _csv_value(table["paper_xi_over_xi0"][point_index]),
                        int(table["x_indices"][point_index]),
                        int(table["z_indices"][point_index]),
                        bool(
                            table["valid_ratio_plus_mask"][
                                frequency_index,
                                point_index,
                            ]
                        ),
                        _csv_value(np.real(f_plus)),
                        _csv_value(np.imag(f_plus)),
                        _csv_value(table["abs_F_plus"][frequency_index, point_index]),
                        _csv_value(
                            table["arg_F_plus_principal"][
                                frequency_index,
                                point_index,
                            ]
                        ),
                        _csv_value(
                            table["arg_F_plus_unwrapped"][
                                frequency_index,
                                point_index,
                            ]
                        ),
                        bool(
                            table["valid_ratio_cross_mask"][
                                frequency_index,
                                point_index,
                            ]
                        ),
                        _csv_value(np.real(f_cross)),
                        _csv_value(np.imag(f_cross)),
                        _csv_value(table["abs_F_cross"][frequency_index, point_index]),
                        _csv_value(
                            table["arg_F_cross_principal"][
                                frequency_index,
                                point_index,
                            ]
                        ),
                        _csv_value(
                            table["arg_F_cross_unwrapped"][
                                frequency_index,
                                point_index,
                            ]
                        ),
                        bool(
                            table["valid_ratio_norm_mask"][
                                frequency_index,
                                point_index,
                            ]
                        ),
                        bool(table["valid_field_mask"][frequency_index, point_index]),
                        bool(table["source_valid_mask"][frequency_index, point_index]),
                    ]
                )


def _write_tablei_markdown(table: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# Table-I Four-Frequency Read-Only Pilot",
        "",
        "This is a sparse four-frequency read-only pilot from the accepted Table-I extraction artifact. It is not a paper-level Fig.5/Fig.6 reproduction and includes no Kirchhoff comparison curves.",
        "",
    ]
    lines.extend(_tablei_markdown_group(table, "near_axis", "Near-Axis Four-Frequency Read-Only Pilot"))
    lines.append("")
    lines.extend(_tablei_markdown_group(table, "far_axis", "Far-Axis Four-Frequency Read-Only Pilot"))
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _tablei_markdown_group(
    table: dict[str, Any],
    group: str,
    title: str,
) -> list[str]:
    indices = _tablei_group_indices(table, group)
    lines = [
        f"## {title}",
        "",
        "| kM | point_id | |F_plus| | arg F_plus diagnostic | |F_cross| | arg F_cross diagnostic |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for point_index in indices:
        for frequency_index, kM in enumerate(table["kM_values"]):
            lines.append(
                "| "
                + " | ".join(
                    [
                        _csv_value(kM),
                        str(table["point_ids"][point_index]),
                        _csv_value(table["abs_F_plus"][frequency_index, point_index]),
                        _csv_value(
                            table["arg_F_plus_unwrapped"][
                                frequency_index,
                                point_index,
                            ]
                        ),
                        _csv_value(table["abs_F_cross"][frequency_index, point_index]),
                        _csv_value(
                            table["arg_F_cross_unwrapped"][
                                frequency_index,
                                point_index,
                            ]
                        ),
                    ]
                )
                + " |"
            )
    return lines


def _render_tablei_group_pilot(
    table: dict[str, Any],
    *,
    group: str,
    output_path: Path,
    dpi: int,
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise PlotError(f"matplotlib is required for PNG output: {exc}") from exc

    point_indices = _tablei_group_indices(table, group)
    if not point_indices:
        raise PlotError(f"Table-I group has no points: {group}.")
    colors = ["#0072B2", "#D55E00", "#009E73", "#CC79A7"]
    markers = ["o", "s", "^", "D"]
    kM = table["kM_values"]
    fig, axes = plt.subplots(
        2,
        2,
        figsize=(7.0, 5.2),
        dpi=dpi,
        sharex=True,
        constrained_layout=True,
    )
    panel_specs = [
        (axes[0, 0], "abs_F_plus", "valid_ratio_plus_mask", r"$|F_+|$"),
        (axes[0, 1], "abs_F_cross", "valid_ratio_cross_mask", r"$|F_\times|$"),
        (
            axes[1, 0],
            "arg_F_plus_unwrapped",
            "valid_ratio_plus_mask",
            r"diagnostic arg $F_+$",
        ),
        (
            axes[1, 1],
            "arg_F_cross_unwrapped",
            "valid_ratio_cross_mask",
            r"diagnostic arg $F_\times$",
        ),
    ]
    for ax, value_name, mask_name, ylabel in panel_specs:
        for local_index, point_index in enumerate(point_indices):
            values = np.asarray(table[value_name][:, point_index], dtype=float)
            mask = np.asarray(table[mask_name][:, point_index], dtype=bool)
            finite = mask & np.isfinite(values)
            ax.plot(
                kM[finite],
                values[finite],
                marker=markers[local_index % len(markers)],
                color=colors[local_index % len(colors)],
                linewidth=1.4,
                markersize=4.5,
                label=str(table["point_ids"][point_index]),
            )
        ax.set_ylabel(ylabel)
        ax.grid(True, color="0.88", linewidth=0.6)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    axes[1, 0].set_xlabel("kM")
    axes[1, 1].set_xlabel("kM")
    axes[0, 0].set_title("Four-frequency read-only pilot")
    axes[0, 1].legend(frameon=False, fontsize=7)
    fig.savefig(output_path, format="png")
    plt.close(fig)


def _tablei_report_sidecar_metadata(
    table: dict[str, Any],
    *,
    extraction_metadata: dict[str, Any],
    source_npz: Path,
    source_json: Path,
    artifact_paths: dict[str, Path],
    plotted_group: str,
    output_path: Path,
    dpi: int,
    created_by_cli: bool,
) -> dict[str, Any]:
    plotted_indices = _tablei_group_indices(table, plotted_group)
    output_artifacts = {
        name: _artifact_record(path) for name, path in artifact_paths.items()
    }
    source_npz = Path(source_npz)
    source_json = Path(source_json)
    return {
        "plot_type": "tablei_four_frequency_readonly_pilot",
        "case_id": "FIG5_FIG6_TABLEI_FOUR_FREQUENCY_REPORTING_PILOT",
        "source_extraction_npz_path": str(source_npz),
        "source_extraction_npz_size_bytes": int(source_npz.stat().st_size),
        "source_extraction_npz_sha256": _file_sha256(source_npz),
        "source_extraction_json_path": str(source_json),
        "source_extraction_json_size_bytes": int(source_json.stat().st_size),
        "source_extraction_json_sha256": _file_sha256(source_json),
        "source_extraction_case_id": extraction_metadata.get("case_id"),
        "source_extraction_schema_version": extraction_metadata.get("schema_version"),
        "output_path": str(output_path),
        "output_size_bytes": int(output_path.stat().st_size),
        "output_sha256": _file_sha256(output_path),
        "output_artifacts": output_artifacts,
        "plotted_group": plotted_group,
        "plotted_point_ids": [
            str(table["point_ids"][point_index]) for point_index in plotted_indices
        ],
        "plotted_quantities": [
            "abs_F_plus",
            "abs_F_cross",
            "arg_F_plus_unwrapped",
            "arg_F_cross_unwrapped",
        ],
        "kM_values": [float(value) for value in table["kM_values"]],
        "phase_policy": extraction_metadata.get(
            "phase_policy",
            {
                "principal": "angle in (-pi, pi]",
                "unwrapped": (
                    "diagnostic only; unwrap independently along frequency and "
                    "restart across invalid values"
                ),
                "four_frequency_unwrap_is_diagnostic_only": True,
            },
        ),
        "mask_policy": {
            "plus": "use valid_ratio_plus_mask for plus component plots",
            "cross": "use valid_ratio_cross_mask for cross component plots",
            "norm": "carry valid_ratio_norm_mask in CSV only",
            "invalid_values": (
                "preserve masks and NaN values; do not fill, clip, smooth, "
                "regularize, or substitute component ratios"
            ),
        },
        "no_solver_rerun": True,
        "no_field_recomputation": True,
        "no_interpolation": True,
        "no_kirchhoff_baseline": True,
        "not_paper_level_dense_scan": True,
        "no_kM4": True,
        "no_dense_Mk_scan": True,
        "no_new_physics_convention": True,
        "read_only_from_tablei_extraction": True,
        "created_by_cli": bool(created_by_cli),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "requested_dpi": int(dpi),
        "output_format": "png",
        "git_commit": None,
        "git_status_available": False,
        "source_code_sha_policy": "unavailable_not_git_repository",
    }


def _artifact_record(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "size_bytes": int(path.stat().st_size),
        "sha256": _file_sha256(path),
    }


def _tablei_group_indices(table: dict[str, Any], group: str) -> list[int]:
    return [
        index
        for index, value in enumerate(table["point_group"])
        if str(value) == group
    ]


def _csv_value(value: Any) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if np.isnan(numeric):
        return "nan"
    if np.isposinf(numeric):
        return "inf"
    if np.isneginf(numeric):
        return "-inf"
    return f"{numeric:.16g}"


def _render_amplification_values(
    result: AmplificationGridResult,
    *,
    values: np.ndarray,
    valid_ratio_mask: np.ndarray,
    quantity: str,
    output_path: Path,
    dpi: int,
    output_format: str,
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise PlotError(f"matplotlib is required for PNG output: {exc}") from exc

    masked_values = np.ma.array(
        values,
        mask=(~valid_ratio_mask) | (~np.isfinite(values)),
    )
    fig, ax = plt.subplots(figsize=(4.8, 3.4), dpi=dpi, constrained_layout=True)
    if _grid_kind(result) == "xz_plane":
        if result.x is None or result.z is None:
            raise PlotError("x-z amplification result is missing x or z fields.")
        image = ax.imshow(
            masked_values,
            origin="lower",
            aspect="auto",
            extent=[
                float(result.x.min()),
                float(result.x.max()),
                float(result.z.min()),
                float(result.z.max()),
            ],
            cmap="viridis",
        )
        ax.set_xlabel("x/M")
        ax.set_ylabel("z/M")
    else:
        theta = result.theta
        phi = result.phi
        if theta.ndim == 1 and phi.ndim == 1 and theta.size >= 2 and phi.size >= 2:
            image = ax.imshow(
                masked_values,
                origin="lower",
                aspect="auto",
                extent=[
                    float(phi.min()),
                    float(phi.max()),
                    float(theta.min()),
                    float(theta.max()),
                ],
                cmap="viridis",
            )
            ax.set_xlabel("phi")
            ax.set_ylabel("theta")
        else:
            finite = np.isfinite(values) & valid_ratio_mask
            image = ax.scatter(
                result.phi[finite],
                result.theta[finite],
                c=values[finite],
                s=36,
                cmap="viridis",
            )
            ax.set_xlabel("phi")
            ax.set_ylabel("theta")
    ax.set_title(quantity)
    fig.colorbar(image, ax=ax, label=quantity)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(output_path, format=output_format)
    plt.close(fig)


def _render_fig4_exact_angular_curves(
    theta: np.ndarray,
    *,
    abs_h_plus: np.ndarray,
    abs_h_cross: np.ndarray,
    output_path: Path,
    dpi: int,
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise PlotError(f"matplotlib is required for PNG output: {exc}") from exc

    fig, ax = plt.subplots(figsize=(5.2, 3.4), dpi=dpi, constrained_layout=True)
    theta_over_pi = theta / np.pi
    ax.plot(
        theta_over_pi,
        abs_h_plus,
        color="#0072B2",
        linewidth=1.8,
        label=r"$|h_+|$",
    )
    ax.plot(
        theta_over_pi,
        abs_h_cross,
        color="#D55E00",
        linewidth=1.8,
        linestyle="--",
        label=r"$|h_\times|$",
    )
    ax.set_xlabel(r"$\theta/\pi$")
    ax.set_ylabel("Exact finite-radius amplitude")
    ax.set_title("r=60M, kM=2, fixed phi=0")
    ax.grid(True, color="0.88", linewidth=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False)
    fig.savefig(output_path, format="png")
    plt.close(fig)


def _render_fig4_all_frequency_exact_angular_curves(
    theta: np.ndarray,
    *,
    abs_h_plus: list[np.ndarray],
    abs_h_cross: list[np.ndarray],
    kM_values: list[float],
    output_path: Path,
    dpi: int,
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise PlotError(f"matplotlib is required for PNG output: {exc}") from exc

    theta_over_pi = theta / np.pi
    colors = ["#0072B2", "#D55E00", "#009E73", "#CC79A7"]
    linestyles = ["-", "--", "-.", ":"]
    fig, axes = plt.subplots(
        2,
        1,
        figsize=(6.4, 5.4),
        dpi=dpi,
        sharex=True,
        constrained_layout=True,
    )
    for ax, component, values_by_frequency in [
        (axes[0], r"$|h_+|$", abs_h_plus),
        (axes[1], r"$|h_\times|$", abs_h_cross),
    ]:
        for kM, values, color, linestyle in zip(
            kM_values,
            values_by_frequency,
            colors,
            linestyles,
            strict=True,
        ):
            ax.plot(
                theta_over_pi,
                values,
                color=color,
                linestyle=linestyle,
                linewidth=1.7,
                label=f"kM={kM:g}",
            )
        ax.set_ylabel(f"{component}\nExact finite-radius amplitude")
        ax.grid(True, color="0.88", linewidth=0.6)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(frameon=False, fontsize=8, ncol=2)
    axes[0].set_title("r=60M, kM=0.5,1.0,1.5,2.0, fixed phi=0")
    axes[1].set_xlabel(r"$\theta/\pi$")
    fig.savefig(output_path, format="png")
    plt.close(fig)


def _render_fig3_panel(
    result: GridResult,
    *,
    h_plus_values: np.ndarray,
    h_cross_values: np.ndarray,
    color_vmin: float,
    color_vmax: float,
    interpolation: str,
    mass: float | None,
    output_path: Path,
    dpi: int,
    output_format: str,
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise PlotError(f"matplotlib is required for PNG output: {exc}") from exc

    assert result.x is not None
    assert result.z is not None
    assert result.valid_mask is not None
    extent = [
        float(result.x.min()),
        float(result.x.max()),
        float(result.z.min()),
        float(result.z.max()),
    ]
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(7.2, 3.4),
        dpi=dpi,
        sharex=True,
        sharey=True,
        constrained_layout=True,
    )
    image = None
    for ax, component, values in zip(
        axes,
        ("h_plus", "h_cross"),
        (h_plus_values, h_cross_values),
        strict=True,
    ):
        masked_values = np.ma.array(
            values,
            mask=(~result.valid_mask) | (~np.isfinite(values)),
        )
        image = ax.imshow(
            masked_values,
            origin="lower",
            aspect="equal",
            extent=extent,
            cmap="RdBu_r",
            vmin=color_vmin,
            vmax=color_vmax,
            interpolation=interpolation,
        )
        if mass is not None:
            _draw_xz_overlays(ax, mass)
        ax.set_xlabel("x/M")
        ax.set_title(f"real({component})")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    axes[0].set_ylabel("z/M")
    if image is not None:
        fig.colorbar(image, ax=list(axes), label="real field amplitude")
    fig.savefig(output_path, format=output_format)
    plt.close(fig)


def _render_fig3_multifrequency_panel(
    results: list[GridResult],
    *,
    h_plus_values: list[np.ndarray],
    h_cross_values: list[np.ndarray],
    kM_values: list[float],
    row_color_scales: dict[str, tuple[float, float]],
    interpolation: str,
    mass: float | None,
    output_path: Path,
    dpi: int,
    output_format: str,
    style: str,
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise PlotError(f"matplotlib is required for PNG output: {exc}") from exc

    reference = results[0]
    assert reference.x is not None
    assert reference.z is not None
    style_params = _fig3_multifrequency_style_params(style)
    extent = [
        float(reference.x.min()),
        float(reference.x.max()),
        float(reference.z.min()),
        float(reference.z.max()),
    ]
    fig, axes = plt.subplots(
        2,
        4,
        figsize=style_params["figsize"],
        dpi=dpi,
        sharex=True,
        sharey=True,
        constrained_layout=True,
    )
    row_images = []
    row_specs = [
        ("h_plus", h_plus_values),
        ("h_cross", h_cross_values),
    ]
    component_labels = {
        "h_plus": r"$\mathrm{Re}\,\widetilde{h}_{+}$",
        "h_cross": r"$\mathrm{Re}\,\widetilde{h}_{\times}$",
    }
    for row_index, (component, values_by_frequency) in enumerate(row_specs):
        color_vmin, color_vmax = row_color_scales[component]
        row_image = None
        for column_index, (result, kM, values) in enumerate(
            zip(results, kM_values, values_by_frequency, strict=True)
        ):
            assert result.valid_mask is not None
            ax = axes[row_index, column_index]
            masked_values = np.ma.array(
                values,
                mask=(~result.valid_mask) | (~np.isfinite(values)),
            )
            row_image = ax.imshow(
                masked_values,
                origin="lower",
                aspect="equal",
                extent=extent,
                cmap="RdBu_r",
                vmin=color_vmin,
                vmax=color_vmax,
                interpolation=interpolation,
            )
            if mass is not None:
                _draw_xz_overlays(
                    ax,
                    mass,
                    linewidth=style_params["overlay_linewidth"],
            )
            if row_index == 0:
                title_kwargs = _fig3_text_kwargs(
                    fontsize=style_params["title_fontsize"],
                    pad=style_params["title_pad"],
                )
                ax.set_title(f"kM={kM:g}", **title_kwargs)
            if column_index == 0:
                ax.set_ylabel(
                    component_labels[component] + "\n" + r"$z/M$",
                    **_fig3_text_kwargs(fontsize=style_params["label_fontsize"]),
                )
            if row_index == 1:
                ax.set_xlabel(
                    r"$x/M$",
                    **_fig3_text_kwargs(fontsize=style_params["label_fontsize"]),
                )
            tick_kwargs = _fig3_text_kwargs(
                labelsize=style_params["tick_labelsize"],
                pad=style_params["tick_pad"],
            )
            if tick_kwargs:
                ax.tick_params(axis="both", which="major", **tick_kwargs)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
        row_images.append((component, row_image))

    for row_index, (component, image) in enumerate(row_images):
        if image is not None:
            fig.colorbar(
                image,
                ax=axes[row_index, :].ravel().tolist(),
                label=component_labels[component],
                fraction=style_params["colorbar_fraction"],
                pad=style_params["colorbar_pad"],
            )
            cbar = fig.axes[-1]
            if style_params["colorbar_tick_labelsize"] is not None:
                cbar.tick_params(labelsize=style_params["colorbar_tick_labelsize"])
            if style_params["colorbar_label_fontsize"] is not None:
                cbar.yaxis.label.set_size(style_params["colorbar_label_fontsize"])
    fig.savefig(output_path, format=output_format)
    plt.close(fig)


def _draw_xz_overlays(ax: Any, mass: float, *, linewidth: float = 0.8) -> None:
    from matplotlib.patches import Circle

    light_ring = Circle(
        (0.0, 0.0),
        3.0 * mass,
        facecolor="0.7",
        edgecolor="0.45",
        linewidth=linewidth,
        alpha=0.45,
        zorder=3,
    )
    horizon = Circle(
        (0.0, 0.0),
        2.0 * mass,
        facecolor="black",
        edgecolor="black",
        linewidth=linewidth,
        alpha=0.95,
        zorder=4,
    )
    ax.add_patch(light_ring)
    ax.add_patch(horizon)


def _render_convergence_history(
    history: list[dict[str, Any]],
    *,
    policy: dict[str, Any],
    output_path: Path,
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise PlotError(f"matplotlib is required for PNG output: {exc}") from exc

    current_lmax = _history_float_array(history, "current_lmax")
    selected = _history_float_array(history, "max_relative_change")
    near_axis = _history_float_array(history, "near_axis_max_relative_change")
    selected_plot = np.maximum(selected, 1.0e-30)
    near_axis_plot = np.maximum(near_axis, 1.0e-30)

    fig, ax = plt.subplots(figsize=(4.8, 3.4), dpi=160, constrained_layout=True)
    ax.semilogy(current_lmax, selected_plot, marker="o", linewidth=1.5, label="all probes")
    ax.semilogy(
        current_lmax,
        near_axis_plot,
        marker="s",
        linewidth=1.5,
        label="near axis",
    )
    selected_threshold = _optional_positive_float(policy, "selected_threshold")
    near_axis_threshold = _optional_positive_float(policy, "near_axis_threshold")
    if selected_threshold is not None:
        ax.axhline(
            selected_threshold,
            color="tab:blue",
            linestyle="--",
            linewidth=1.0,
            label="selected threshold",
        )
    if near_axis_threshold is not None:
        ax.axhline(
            near_axis_threshold,
            color="tab:orange",
            linestyle=":",
            linewidth=1.2,
            label="near-axis threshold",
        )
    ax.set_xlabel("current lmax")
    ax.set_ylabel("adjacent-pair relative change")
    ax.set_title("lmax convergence history")
    ax.legend(frameon=False, fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(output_path, format="png")
    plt.close(fig)


def _history_float_array(history: list[dict[str, Any]], key: str) -> np.ndarray:
    values = []
    for index, row in enumerate(history):
        if not isinstance(row, dict) or key not in row:
            raise PlotError(f"lmax_convergence_history[{index}] missing {key}.")
        value = row[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise PlotError(f"lmax_convergence_history[{index}].{key} must be numeric.")
        values.append(float(value))
    return np.asarray(values, dtype=float)


def _optional_positive_float(raw: dict[str, Any], key: str) -> float | None:
    value = raw.get(key) if isinstance(raw, dict) else None
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = float(value)
    return value if value > 0.0 else None


def _render_values(
    result: GridResult,
    values: np.ndarray,
    *,
    component: str,
    quantity: str,
    output_path: Path,
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise PlotError(f"matplotlib is required for PNG output: {exc}") from exc

    title = f"{component} {quantity}"
    fig, ax = plt.subplots(figsize=(4.8, 3.4), dpi=160, constrained_layout=True)
    if _grid_kind(result) == "xz_plane":
        if result.x is None or result.z is None or result.valid_mask is None:
            raise PlotError("x-z result is missing x, z, or valid_mask fields.")
        masked_values = np.ma.array(
            values,
            mask=(~result.valid_mask) | (~np.isfinite(values)),
        )
        image = ax.imshow(
            masked_values,
            origin="lower",
            aspect="auto",
            extent=[
                float(result.x.min()),
                float(result.x.max()),
                float(result.z.min()),
                float(result.z.max()),
            ],
            cmap="viridis",
        )
        ax.set_xlabel("x")
        ax.set_ylabel("z")
        ax.set_title(title)
        fig.colorbar(image, ax=ax, label=_colorbar_label(component, quantity))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        fig.savefig(output_path, format="png")
        plt.close(fig)
        return

    theta = result.theta
    phi = result.phi
    if theta.size >= 2 and phi.size >= 2:
        image = ax.imshow(
            values,
            origin="lower",
            aspect="auto",
            extent=[float(phi.min()), float(phi.max()), float(theta.min()), float(theta.max())],
            cmap="viridis",
        )
        ax.set_xlabel("phi")
        ax.set_ylabel("theta")
        fig.colorbar(image, ax=ax, label=_colorbar_label(component, quantity))
    elif theta.size >= 2:
        ax.plot(theta, values[:, 0], marker="o", linewidth=1.5)
        ax.set_xlabel("theta")
        ax.set_ylabel(_colorbar_label(component, quantity))
    elif phi.size >= 2:
        ax.plot(phi, values[0, :], marker="o", linewidth=1.5)
        ax.set_xlabel("phi")
        ax.set_ylabel(_colorbar_label(component, quantity))
    else:
        ax.scatter([0.0], [float(values[0, 0])], s=56)
        ax.set_xlabel("single saved point")
        ax.set_ylabel(_colorbar_label(component, quantity))
    ax.set_title(title)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.savefig(output_path, format="png")
    plt.close(fig)


def _validate_component_quantity(component: str, quantity: str) -> None:
    if component not in COMPONENTS:
        raise PlotError(f"component must be one of {sorted(COMPONENTS)}.")
    if quantity not in QUANTITIES:
        raise PlotError(f"quantity must be one of {sorted(QUANTITIES)}.")


def _quantity_values(values: np.ndarray, quantity: str) -> np.ndarray:
    if quantity == "real":
        return np.real(values)
    if quantity == "imag":
        return np.imag(values)
    if quantity == "abs":
        return np.abs(values)
    if quantity == "phase":
        return np.angle(values)
    raise PlotError(f"quantity must be one of {sorted(QUANTITIES)}.")


def _amplification_quantity_values(
    result: AmplificationGridResult,
    quantity: str,
) -> tuple[np.ndarray, np.ndarray, str]:
    if quantity == "F_pol_norm":
        return (
            np.asarray(result.F_pol_norm, dtype=float),
            np.asarray(result.valid_ratio_norm_mask, dtype=bool),
            "valid_ratio_norm_mask",
        )
    if quantity == "I_pol_ratio":
        return (
            np.asarray(result.I_pol_ratio, dtype=float),
            np.asarray(result.valid_ratio_norm_mask, dtype=bool),
            "valid_ratio_norm_mask",
        )
    if quantity == "amplification_plus":
        return (
            np.asarray(result.amplification_plus, dtype=float),
            np.asarray(result.valid_ratio_plus_mask, dtype=bool),
            "valid_ratio_plus_mask",
        )
    if quantity == "amplification_cross":
        return (
            np.asarray(result.amplification_cross, dtype=float),
            np.asarray(result.valid_ratio_cross_mask, dtype=bool),
            "valid_ratio_cross_mask",
        )
    if quantity == "abs_F_plus":
        return (
            np.abs(result.F_plus_complex),
            np.asarray(result.valid_ratio_plus_mask, dtype=bool),
            "valid_ratio_plus_mask",
        )
    if quantity == "abs_F_cross":
        return (
            np.abs(result.F_cross_complex),
            np.asarray(result.valid_ratio_cross_mask, dtype=bool),
            "valid_ratio_cross_mask",
        )
    if quantity == "phase_plus":
        return (
            np.angle(result.F_plus_complex),
            np.asarray(result.valid_ratio_plus_mask, dtype=bool),
            "valid_ratio_plus_mask",
        )
    if quantity == "phase_cross":
        return (
            np.angle(result.F_cross_complex),
            np.asarray(result.valid_ratio_cross_mask, dtype=bool),
            "valid_ratio_cross_mask",
        )
    if quantity == "intensity_plus_ratio":
        return (
            np.asarray(result.intensity_plus_ratio, dtype=float),
            np.asarray(result.valid_ratio_plus_mask, dtype=bool),
            "valid_ratio_plus_mask",
        )
    if quantity == "intensity_cross_ratio":
        return (
            np.asarray(result.intensity_cross_ratio, dtype=float),
            np.asarray(result.valid_ratio_cross_mask, dtype=bool),
            "valid_ratio_cross_mask",
        )
    raise PlotError(f"quantity must be one of {sorted(AMPLIFICATION_QUANTITIES)}.")


def _plot_metadata(
    result: GridResult,
    *,
    source_result_path: Path,
    component: str,
    quantity: str,
) -> dict[str, Any]:
    config = result.metadata.get("config", {})
    wave = config.get("wave", {}) if isinstance(config, dict) else {}
    observer = config.get("observer", {}) if isinstance(config, dict) else {}
    numerics = config.get("numerics", {}) if isinstance(config, dict) else {}
    payload = {
        "source_result_path": str(source_result_path),
        "component": component,
        "quantity": quantity,
        "case_id": result.metadata.get("case_id"),
        "kM": wave.get("kM"),
        "observer_r": observer.get("r"),
        "lmax": result.metadata.get("lmax", numerics.get("lmax")),
        "convention": result.metadata.get("convention", {}),
        "source_result_created_at": result.metadata.get("created_at"),
    }
    payload.update(_grid_plot_metadata(result))
    return payload


def _amplification_plot_metadata(
    result: AmplificationGridResult,
    *,
    source_result_path: Path,
    quantity: str,
    mask_field: str,
    valid_ratio_mask: np.ndarray,
    values: np.ndarray,
    output_path: Path,
    dpi: int,
    output_format: str,
) -> dict[str, Any]:
    metadata = result.metadata
    normalization = metadata.get("normalization", {})
    normalization = normalization if isinstance(normalization, dict) else {}
    grid_kind = _grid_kind(result)
    valid_count = int(np.count_nonzero(valid_ratio_mask))
    finite_valid_count = int(np.count_nonzero(valid_ratio_mask & np.isfinite(values)))
    payload: dict[str, Any] = {
        "plot_type": "pointwise_wave_optics_amplification",
        "quantity": quantity,
        "mask_field": mask_field,
        "source_amplification_result_path": str(source_result_path),
        "case_id": metadata.get("case_id"),
        "source_case_id": metadata.get("source_case_id"),
        "source_lensed_result_path": metadata.get("source_lensed_result_path"),
        "source_grid": metadata.get("source_grid"),
        "source_convention": metadata.get("source_convention"),
        "normalization": normalization,
        "baseline": {
            "baseline": normalization.get("baseline"),
            "baseline_api": normalization.get("baseline_api"),
        },
        "grid_kind": grid_kind,
        "shape": list(values.shape),
        "valid_count": valid_count,
        "invalid_count": int(valid_ratio_mask.size - valid_count),
        "finite_valid_count": finite_valid_count,
        "nonfinite_valid_count": int(valid_count - finite_valid_count),
        "output_path": str(output_path),
        "requested_dpi": dpi,
        "output_format": output_format,
        "invalid_value_policy": (
            "Entries outside the saved ratio mask or with non-finite values are "
            "rendered as masked values."
        ),
    }
    if grid_kind == "xz_plane" and result.x is not None and result.z is not None:
        payload["x_range"] = [float(result.x.min()), float(result.x.max())]
        payload["z_range"] = [float(result.z.min()), float(result.z.max())]
    return payload


def _convergence_plot_metadata(
    result: GridResult,
    *,
    source_result_path: Path,
    history: list[dict[str, Any]],
    policy: dict[str, Any],
) -> dict[str, Any]:
    config = result.metadata.get("config", {})
    wave = config.get("wave", {}) if isinstance(config, dict) else {}
    observer = config.get("observer", {}) if isinstance(config, dict) else {}
    diagnostics = result.metadata.get("diagnostics", {})
    return {
        "source_result_path": str(source_result_path),
        "case_id": result.metadata.get("case_id"),
        "kM": wave.get("kM"),
        "observer_r": observer.get("r"),
        "lmax_values": policy.get("lmax_values", _lmax_values_from_history(history)),
        "final_lmax_pair": diagnostics.get("final_lmax_pair"),
        "final_pair_passed": policy.get("final_pair_passed"),
        "thresholds": {
            "selected": policy.get("selected_threshold"),
            "near_axis": policy.get("near_axis_threshold"),
        },
        "convention": (
            "Adjacent lmax relative change uses max(abs(new), abs(old), tiny) "
            "as denominator; plot reads saved metadata only."
        ),
        "source_result_created_at": result.metadata.get("created_at"),
    }


def _fig3_panel_metadata(
    result: GridResult,
    *,
    source_result_path: Path,
    quantity: str,
    interpolation: str,
    color_vmin: float,
    color_vmax: float,
    mass: float | None,
    dpi: int,
    output_format: str,
) -> dict[str, Any]:
    config = result.metadata.get("config", {})
    wave = config.get("wave", {}) if isinstance(config, dict) else {}
    numerics = config.get("numerics", {}) if isinstance(config, dict) else {}
    diagnostics = _diagnostics(result)
    policy = _lmax_policy(result)
    payload = {
        "source_result_path": str(source_result_path),
        "case_id": result.metadata.get("case_id"),
        "plot_type": "fig3_lite_panel",
        "grid_kind": _grid_kind(result),
        "quantity": quantity,
        "interpolation": interpolation,
        "components": ["h_plus", "h_cross"],
        "kM": wave.get("kM"),
        "lmax": result.metadata.get("lmax", numerics.get("lmax")),
        "requested_dpi": dpi,
        "output_format": output_format,
        "final_lmax_pair": diagnostics.get("final_lmax_pair"),
        "final_pair_passed": policy.get("final_pair_passed"),
        "symmetric_color_scale": True,
        "color_vmin": color_vmin,
        "color_vmax": color_vmax,
        "overlays": _overlay_metadata(mass),
        "convention": result.metadata.get("convention", {}),
    }
    payload.update(_grid_plot_metadata(result))
    payload.update(_actual_mask_counts(result))
    payload.update(_sampling_metadata(result))
    return payload


def _fig3_multifrequency_panel_metadata(
    results: list[GridResult],
    *,
    source_result_paths: list[Path],
    kM_values: list[float],
    quantity: str,
    interpolation: str,
    row_color_scales: dict[str, tuple[float, float]],
    mass: float | None,
    dpi: int,
    output_format: str,
    style: str,
) -> dict[str, Any]:
    reference = results[0]
    style_params = _fig3_multifrequency_style_params(style)
    payload: dict[str, Any] = {
        "plot_type": "fig3_multifrequency_panel",
        "source_result_paths": [str(path) for path in source_result_paths],
        "case_ids": [result.metadata.get("case_id") for result in results],
        "kM_values": kM_values,
        "components": ["h_plus", "h_cross"],
        "quantity": quantity,
        "interpolation": interpolation,
        "requested_dpi": dpi,
        "output_format": output_format,
        "render_style": style,
        "figure_size_inches": list(style_params["figsize"]),
        "publication_rendering_candidate": style == "publication",
        "row_color_scales": {
            component: {"vmin": limits[0], "vmax": limits[1]}
            for component, limits in row_color_scales.items()
        },
        "overlays": _overlay_metadata(mass),
        "convention": reference.metadata.get("convention", {}),
        "source_summaries": [
            _fig3_multifrequency_source_summary(result, source_result_path=path)
            for result, path in zip(results, source_result_paths, strict=True)
        ],
        "valid_point_counts": [
            _actual_mask_counts(result).get("valid_point_count") for result in results
        ],
        "invalid_point_counts": [
            _actual_mask_counts(result).get("invalid_point_count") for result in results
        ],
        "samples_per_wavelength": [
            _sampling_metadata(result).get("samples_per_wavelength")
            for result in results
        ],
        "final_lmax_pairs": [
            _diagnostics(result).get("final_lmax_pair") for result in results
        ],
        "final_pair_passed": [
            _lmax_policy(result).get("final_pair_passed") for result in results
        ],
    }
    payload.update(_grid_plot_metadata(reference))
    payload.update(_actual_mask_counts(reference))
    reference_sampling = _sampling_metadata(reference)
    if "grid_spacing" in reference_sampling:
        payload["grid_spacing"] = reference_sampling["grid_spacing"]
    return payload


def _validate_fig3_render_style(style: str) -> str:
    if style not in FIG3_RENDER_STYLES:
        raise PlotError(
            f"style must be one of {sorted(FIG3_RENDER_STYLES)}."
        )
    return style


def _fig3_multifrequency_style_params(style: str) -> dict[str, Any]:
    if style == "publication":
        return {
            "figsize": (7.1, 3.65),
            "title_fontsize": 7.0,
            "title_pad": 2.0,
            "label_fontsize": 6.5,
            "tick_labelsize": 6.0,
            "tick_pad": 1.0,
            "colorbar_label_fontsize": 6.5,
            "colorbar_tick_labelsize": 6.0,
            "colorbar_fraction": 0.028,
            "colorbar_pad": 0.012,
            "overlay_linewidth": 0.45,
        }
    return {
        "figsize": (11.2, 5.6),
        "title_fontsize": None,
        "title_pad": None,
        "label_fontsize": None,
        "tick_labelsize": None,
        "tick_pad": None,
        "colorbar_label_fontsize": None,
        "colorbar_tick_labelsize": None,
        "colorbar_fraction": 0.15,
        "colorbar_pad": 0.05,
        "overlay_linewidth": 0.8,
    }


def _fig3_text_kwargs(**kwargs: Any) -> dict[str, Any]:
    return {key: value for key, value in kwargs.items() if value is not None}


def _fig3_multifrequency_source_summary(
    result: GridResult,
    *,
    source_result_path: Path,
) -> dict[str, Any]:
    counts = _actual_mask_counts(result)
    sampling = _sampling_metadata(result)
    diagnostics = _diagnostics(result)
    policy = _lmax_policy(result)
    return {
        "source_result_path": str(source_result_path),
        "case_id": result.metadata.get("case_id"),
        "kM": _wave_kM(result),
        "valid_point_count": counts.get("valid_point_count"),
        "invalid_point_count": counts.get("invalid_point_count"),
        "samples_per_wavelength": sampling.get("samples_per_wavelength"),
        "final_lmax_pair": diagnostics.get("final_lmax_pair"),
        "final_pair_passed": policy.get("final_pair_passed"),
    }


def _fig4_exact_angular_metadata(
    result: GridResult,
    *,
    source_result_path: Path,
    output_path: Path,
    phi_selected: float,
    phi_selected_index: int,
    dpi: int,
    output_format: str,
    created_by_cli: bool,
) -> dict[str, Any]:
    config = _metadata_object(result.metadata, "config")
    wave = _metadata_object(config, "wave")
    observer = _metadata_object(config, "observer")
    numerics = _metadata_object(config, "numerics")
    boundary = _metadata_object(numerics, "boundary")
    diagnostics = _metadata_object(result.metadata, "diagnostics")
    policy = _metadata_object(diagnostics, "lmax_convergence_policy")
    cache = _metadata_object(diagnostics, "run_radial_cache")
    final_history = _fig4_final_history_row(diagnostics)
    q018 = _q018_oracle_summary(diagnostics, boundary)
    source_path = Path(source_result_path)

    return {
        "plot_type": "fig4_exact_angular_curves",
        "source_npz_path": str(source_path),
        "source_npz_sha256": _file_sha256(source_path),
        "source_npz_size_bytes": int(source_path.stat().st_size),
        "source_case_id": _required_metadata_value(result.metadata, "case_id"),
        "source_grid_kind": "angular",
        "source_r": _required_number(_grid_radius(result, observer), "source r"),
        "source_kM": _required_number(wave.get("kM"), "source wave.kM"),
        "source_lmax": int(
            _required_number(
                result.metadata.get("lmax", numerics.get("lmax")),
                "source lmax",
            )
        ),
        "field_names": ["h_plus", "h_cross"],
        "plotted_quantities": ["abs_h_plus", "abs_h_cross"],
        "curve_extraction_policy": "fixed_phi_cut",
        "phi_selected": float(phi_selected),
        "phi_selected_index": int(phi_selected_index),
        "theta_count": int(result.theta.size),
        "phi_count": int(result.phi.size),
        "theta_range": _axis_range_metadata(result.theta, observer.get("theta_range")),
        "phi_range": _axis_range_metadata(result.phi, observer.get("phi_range")),
        "no_phi_average": True,
        "no_solver_rerun": True,
        "no_field_recomputation": True,
        "no_strict_psi4": True,
        "no_asymptotic_comparison": True,
        "convergence_caveat": "selected_17x8_final_pair_only_not_full_grid",
        "final_lmax_pair": _required_int_list(
            diagnostics.get("final_lmax_pair"),
            "final_lmax_pair",
        ),
        "final_selected_max_relative_change": _required_number(
            final_history.get("max_relative_change"),
            "final selected max relative change",
        ),
        "final_near_axis_max_relative_change": _required_number(
            final_history.get("near_axis_max_relative_change"),
            "final near-axis max relative change",
        ),
        "selected_threshold": _required_number(
            policy.get("selected_threshold"),
            "selected_threshold",
        ),
        "near_axis_threshold": _required_number(
            policy.get("near_axis_threshold"),
            "near_axis_threshold",
        ),
        "q018_oracle_warning_count": q018["warning_count"],
        "q018_oracle_warning_code": "q018_required_radius_oracle_used",
        "q018_oracle_ell_range": q018["ell_range"],
        "q018_oracle_ell_count": q018["ell_count"],
        "q018_oracle_sectors": q018["sectors"],
        "q018_required_eval_radius": q018["required_eval_radius"],
        "q018_opt_in": q018["opt_in"],
        "q018_valid_at_required_radius": q018["valid_at_required_radius"],
        "radial_cache_unique_solution_count": int(
            _required_number(
                cache.get("unique_solution_count"),
                "radial cache unique_solution_count",
            )
        ),
        "radial_cache_key_count": int(
            _required_number(cache.get("key_count"), "radial cache key_count")
        ),
        "radial_cache_hit_count": int(
            _required_number(cache.get("hit_count"), "radial cache hit_count")
        ),
        "created_by_cli": bool(created_by_cli),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "requested_dpi": int(dpi),
        "output_format": output_format,
        "output_path": str(output_path),
        "git_commit": None,
        "git_status_available": False,
        "source_code_sha_policy": "unavailable_not_git_repository",
    }


def _fig4_all_frequency_exact_angular_metadata(
    results: list[GridResult],
    *,
    source_result_paths: list[Path],
    output_path: Path,
    phi_selected: float,
    phi_selected_index: int,
    dpi: int,
    output_format: str,
    created_by_cli: bool,
) -> dict[str, Any]:
    reference = results[0]
    source_infos = [
        _fig4_all_frequency_source_info(result, source_result_path=path)
        for result, path in zip(results, source_result_paths, strict=True)
    ]
    return {
        "plot_type": "fig4_all_frequency_exact_angular_curves",
        "source_npz_paths": [str(path) for path in source_result_paths],
        "source_npz_sha256": [info["source_npz_sha256"] for info in source_infos],
        "source_npz_size_bytes": [
            info["source_npz_size_bytes"] for info in source_infos
        ],
        "source_case_ids": [info["source_case_id"] for info in source_infos],
        "source_grid_kind": "angular",
        "source_r_values": [info["source_r"] for info in source_infos],
        "source_kM_values": [info["source_kM"] for info in source_infos],
        "source_lmax_values": [info["source_lmax"] for info in source_infos],
        "field_names": ["h_plus", "h_cross"],
        "plotted_quantities": ["abs_h_plus", "abs_h_cross"],
        "curve_extraction_policy": "fixed_phi_cut",
        "phi_selected": float(phi_selected),
        "phi_selected_index": int(phi_selected_index),
        "theta_count": int(reference.theta.size),
        "phi_count": int(reference.phi.size),
        "theta_range": source_infos[0]["theta_range"],
        "phi_range": source_infos[0]["phi_range"],
        "no_phi_average": True,
        "no_solver_rerun": True,
        "no_field_recomputation": True,
        "no_strict_psi4": True,
        "no_asymptotic_comparison": True,
        "no_kirchhoff_baseline": True,
        "convergence_caveat": "selected_17x8_final_pair_only_not_full_grid",
        "final_lmax_pairs": [info["final_lmax_pair"] for info in source_infos],
        "final_selected_max_relative_changes": [
            info["final_selected_max_relative_change"] for info in source_infos
        ],
        "final_near_axis_max_relative_changes": [
            info["final_near_axis_max_relative_change"] for info in source_infos
        ],
        "selected_thresholds": [info["selected_threshold"] for info in source_infos],
        "near_axis_thresholds": [info["near_axis_threshold"] for info in source_infos],
        "q018_oracle_warning_counts": [
            info["q018_oracle_warning_count"] for info in source_infos
        ],
        "q018_oracle_warning_codes": [
            info["q018_oracle_warning_codes"] for info in source_infos
        ],
        "q018_oracle_ell_ranges": [
            info["q018_oracle_ell_range"] for info in source_infos
        ],
        "q018_oracle_ell_counts": [
            info["q018_oracle_ell_count"] for info in source_infos
        ],
        "q018_oracle_sectors": [
            info["q018_oracle_sectors"] for info in source_infos
        ],
        "q018_opt_ins": [info["q018_opt_in"] for info in source_infos],
        "radial_cache_unique_solution_counts": [
            info["radial_cache_unique_solution_count"] for info in source_infos
        ],
        "radial_cache_key_counts": [
            info["radial_cache_key_count"] for info in source_infos
        ],
        "radial_cache_hit_counts": [
            info["radial_cache_hit_count"] for info in source_infos
        ],
        "k1p5_max_match_condition_number_diagnostic": source_infos[
            2
        ]["max_match_condition_number"],
        "source_summaries": source_infos,
        "created_by_cli": bool(created_by_cli),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "requested_dpi": int(dpi),
        "output_format": output_format,
        "output_path": str(output_path),
        "git_commit": None,
        "git_status_available": False,
        "source_code_sha_policy": "unavailable_not_git_repository",
    }


def _fig4_all_frequency_source_info(
    result: GridResult,
    *,
    source_result_path: Path,
) -> dict[str, Any]:
    config = _metadata_object(result.metadata, "config")
    wave = _metadata_object(config, "wave")
    observer = _metadata_object(config, "observer")
    numerics = _metadata_object(config, "numerics")
    boundary = _metadata_object(numerics, "boundary")
    diagnostics = _metadata_object(result.metadata, "diagnostics")
    policy = _metadata_object(diagnostics, "lmax_convergence_policy")
    cache = _metadata_object(diagnostics, "run_radial_cache")
    final_history = _fig4_final_history_row(diagnostics)
    q018 = _q018_oracle_summary_or_none(diagnostics, boundary)
    radial_summary = _metadata_object(
        diagnostics,
        "summary" if isinstance(diagnostics.get("summary"), dict) else "radial_summary",
    )
    source_path = Path(source_result_path)

    return {
        "source_npz_path": str(source_path),
        "source_npz_sha256": _file_sha256(source_path),
        "source_npz_size_bytes": int(source_path.stat().st_size),
        "source_case_id": _required_metadata_value(result.metadata, "case_id"),
        "source_grid_kind": "angular",
        "source_r": _required_number(_grid_radius(result, observer), "source r"),
        "source_kM": _required_number(wave.get("kM"), "source wave.kM"),
        "source_lmax": int(
            _required_number(
                result.metadata.get("lmax", numerics.get("lmax")),
                "source lmax",
            )
        ),
        "theta_range": _axis_range_metadata(result.theta, observer.get("theta_range")),
        "phi_range": _axis_range_metadata(result.phi, observer.get("phi_range")),
        "final_lmax_pair": _required_int_list(
            diagnostics.get("final_lmax_pair"),
            "final_lmax_pair",
        ),
        "final_selected_max_relative_change": _required_number(
            final_history.get("max_relative_change"),
            "final selected max relative change",
        ),
        "final_near_axis_max_relative_change": _required_number(
            final_history.get("near_axis_max_relative_change"),
            "final near-axis max relative change",
        ),
        "selected_threshold": _required_number(
            policy.get("selected_threshold"),
            "selected_threshold",
        ),
        "near_axis_threshold": _required_number(
            policy.get("near_axis_threshold"),
            "near_axis_threshold",
        ),
        "q018_oracle_warning_count": q018["warning_count"],
        "q018_oracle_warning_codes": q018["warning_codes"],
        "q018_oracle_ell_range": q018["ell_range"],
        "q018_oracle_ell_count": q018["ell_count"],
        "q018_oracle_sectors": q018["sectors"],
        "q018_opt_in": q018["opt_in"],
        "radial_cache_unique_solution_count": int(
            _required_number(
                cache.get("unique_solution_count"),
                "radial cache unique_solution_count",
            )
        ),
        "radial_cache_key_count": int(
            _required_number(cache.get("key_count"), "radial cache key_count")
        ),
        "radial_cache_hit_count": int(
            _required_number(cache.get("hit_count"), "radial cache hit_count")
        ),
        "max_match_condition_number": _required_number(
            radial_summary.get("max_match_condition_number_max"),
            "max_match_condition_number_max",
        ),
    }


def _overlay_metadata(mass: float | None) -> dict[str, Any]:
    if mass is None:
        return {"drawn": False}
    return {
        "drawn": True,
        "event_horizon_radius": 2.0 * mass,
        "light_ring_radius": 3.0 * mass,
    }


def _validate_dpi(dpi: int) -> int:
    if isinstance(dpi, bool) or not isinstance(dpi, int):
        raise PlotError("dpi must be a positive integer.")
    if dpi <= 0:
        raise PlotError("dpi must be a positive integer.")
    return int(dpi)


def _output_format(output_path: Path) -> str:
    suffix = output_path.suffix.lower().lstrip(".")
    if not suffix:
        return "png"
    if suffix not in FIGURE_OUTPUT_FORMATS:
        raise PlotError(
            f"output format must be one of {sorted(FIGURE_OUTPUT_FORMATS)}."
        )
    return suffix


def _lmax_values_from_history(history: list[dict[str, Any]]) -> list[int]:
    if not history:
        return []
    values = [int(history[0]["previous_lmax"])]
    values.extend(int(row["current_lmax"]) for row in history)
    return values


def _grid_kind(result: GridResult) -> str:
    grid = result.metadata.get("grid", {})
    if isinstance(grid, dict) and isinstance(grid.get("kind"), str):
        return grid["kind"]
    if result.x is not None or result.z is not None:
        return "xz_plane"
    return "angular"


def _require_xz_plane(result: GridResult, *, command: str) -> None:
    if _grid_kind(result) != "xz_plane":
        raise PlotError(f"{command} requires an x-z plane result.")
    if result.x is None or result.z is None or result.valid_mask is None:
        raise PlotError("x-z result is missing x, z, or valid_mask fields.")
    if result.h_plus.shape != result.valid_mask.shape:
        raise PlotError("x-z result h_plus shape does not match valid_mask.")
    if result.h_cross.shape != result.valid_mask.shape:
        raise PlotError("x-z result h_cross shape does not match valid_mask.")


def _require_fig4_exact_angular_result(result: GridResult) -> tuple[np.ndarray, np.ndarray]:
    if _grid_kind(result) != "angular":
        raise PlotError("plot-fig4-exact-angular requires an angular result.")
    theta = np.asarray(result.theta, dtype=float)
    phi = np.asarray(result.phi, dtype=float)
    if theta.ndim != 1 or phi.ndim != 1:
        raise PlotError("plot-fig4-exact-angular requires 1D theta and phi arrays.")
    expected_shape = (theta.size, phi.size)
    if result.h_plus.shape != expected_shape:
        raise PlotError("h_plus shape does not match (theta.size, phi.size).")
    if result.h_cross.shape != expected_shape:
        raise PlotError("h_cross shape does not match (theta.size, phi.size).")
    if not np.all(np.isfinite(theta)) or not np.all(np.isfinite(phi)):
        raise PlotError("theta and phi coordinates must be finite.")
    return theta, phi


def _require_fig4_production_angular_shapes(
    results: list[GridResult],
    coordinates: list[tuple[np.ndarray, np.ndarray]],
) -> None:
    for result, (theta, phi) in zip(results, coordinates, strict=True):
        expected_shape = (65, 64)
        if theta.shape != (65,) or phi.shape != (64,):
            raise PlotError(
                "plot-fig4-all-frequency-exact-angular requires theta=(65,) "
                "and phi=(64,) production grids."
            )
        if result.h_plus.shape != expected_shape or result.h_cross.shape != expected_shape:
            raise PlotError(
                "plot-fig4-all-frequency-exact-angular requires h_plus/h_cross "
                "shape (65,64)."
            )


def _require_matching_angular_coordinates(
    coordinates: list[tuple[np.ndarray, np.ndarray]],
) -> None:
    reference_theta, reference_phi = coordinates[0]
    for theta, phi in coordinates[1:]:
        if not np.allclose(theta, reference_theta, rtol=0.0, atol=1.0e-12):
            raise PlotError(
                "plot-fig4-all-frequency-exact-angular requires matching theta and phi grids."
            )
        if not np.allclose(phi, reference_phi, rtol=0.0, atol=1.0e-12):
            raise PlotError(
                "plot-fig4-all-frequency-exact-angular requires matching theta and phi grids."
            )


def _strict_phi_index(phi_values: np.ndarray, requested_phi: float) -> int:
    requested = float(requested_phi)
    matches = np.flatnonzero(np.isclose(phi_values, requested, rtol=0.0, atol=1.0e-12))
    if matches.size != 1:
        raise PlotError("requested phi is not present in the saved phi coordinates.")
    return int(matches[0])


def _require_matching_xz_coordinates(results: list[GridResult]) -> None:
    reference = results[0]
    assert reference.x is not None
    assert reference.z is not None
    for result in results[1:]:
        assert result.x is not None
        assert result.z is not None
        if not np.array_equal(result.x, reference.x) or not np.array_equal(
            result.z,
            reference.z,
        ):
            raise PlotError(
                "plot-fig3-multifrequency-panel requires matching x-z coordinates."
            )


def _grid_plot_metadata(result: GridResult) -> dict[str, Any]:
    grid = result.metadata.get("grid", {})
    grid = grid if isinstance(grid, dict) else {}
    payload: dict[str, Any] = {"grid_kind": _grid_kind(result)}
    if payload["grid_kind"] == "xz_plane":
        if result.x is not None and result.z is not None:
            payload["x_range"] = [float(result.x.min()), float(result.x.max())]
            payload["z_range"] = [float(result.z.min()), float(result.z.max())]
        payload["valid_point_count"] = grid.get("valid_point_count")
        payload["invalid_point_count"] = grid.get("invalid_point_count")
        payload["coordinate_conversion"] = grid.get("coordinate_conversion")
    return payload


def _sampling_metadata(result: GridResult) -> dict[str, Any]:
    if result.x is None or result.z is None:
        return {}
    dx = _uniform_spacing(result.x)
    dz = _uniform_spacing(result.z)
    if dx is None or dz is None:
        return {}
    payload: dict[str, Any] = {"grid_spacing": {"x": dx, "z": dz}}
    kM = _wave_kM(result)
    if kM is not None:
        wavelength = 2.0 * np.pi / kM
        payload["samples_per_wavelength"] = {
            "wavelength_over_M": float(wavelength),
            "x": float(wavelength / dx),
            "z": float(wavelength / dz),
        }
    return payload


def _uniform_spacing(values: np.ndarray) -> float | None:
    if values.ndim != 1 or values.size < 2:
        return None
    diffs = np.diff(values.astype(float))
    if not np.all(np.isfinite(diffs)):
        return None
    if not (np.all(diffs > 0.0) or np.all(diffs < 0.0)):
        return None
    if not np.allclose(diffs, diffs[0], rtol=1.0e-12, atol=1.0e-12):
        return None
    return float(abs(diffs[0]))


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _metadata_object(metadata: dict[str, Any], key: str) -> dict[str, Any]:
    value = metadata.get(key)
    if not isinstance(value, dict):
        raise PlotError(f"source metadata missing object: {key}.")
    return value


def _required_metadata_value(metadata: dict[str, Any], key: str) -> Any:
    value = metadata.get(key)
    if value is None:
        raise PlotError(f"source metadata missing value: {key}.")
    return value


def _required_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PlotError(f"source metadata missing numeric {label}.")
    numeric = float(value)
    if not np.isfinite(numeric):
        raise PlotError(f"source metadata {label} must be finite.")
    return numeric


def _required_int_list(value: Any, label: str) -> list[int]:
    if not isinstance(value, list) or not value:
        raise PlotError(f"source metadata missing list {label}.")
    return [int(_required_number(item, label)) for item in value]


def _grid_radius(result: GridResult, observer: dict[str, Any]) -> Any:
    grid = result.metadata.get("grid", {})
    if isinstance(grid, dict) and grid.get("r") is not None:
        return grid["r"]
    return observer.get("r")


def _axis_range_metadata(values: np.ndarray, saved_range: Any) -> dict[str, Any]:
    if isinstance(saved_range, dict):
        return saved_range
    spacing = _uniform_spacing(values)
    payload: dict[str, Any] = {
        "start": float(values[0]),
        "stop": float(values[-1]),
        "endpoint": True,
    }
    if spacing is not None:
        payload["step"] = spacing
    return payload


def _fig4_final_history_row(diagnostics: dict[str, Any]) -> dict[str, Any]:
    history = diagnostics.get("lmax_convergence_history")
    if not isinstance(history, list) or not history:
        raise PlotError("source metadata missing lmax_convergence_history.")
    final_pair = diagnostics.get("final_lmax_pair")
    if isinstance(final_pair, list) and len(final_pair) == 2:
        for row in reversed(history):
            if (
                isinstance(row, dict)
                and row.get("previous_lmax") == final_pair[0]
                and row.get("current_lmax") == final_pair[1]
            ):
                return row
    row = history[-1]
    if not isinstance(row, dict):
        raise PlotError("source metadata lmax_convergence_history row is invalid.")
    return row


def _q018_oracle_summary(
    diagnostics: dict[str, Any],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    warnings = diagnostics.get("radial_diagnostic_warnings")
    if not isinstance(warnings, list):
        raise PlotError("source metadata missing radial_diagnostic_warnings.")
    q018_warnings = [
        warning
        for warning in warnings
        if isinstance(warning, dict)
        and warning.get("code") == "q018_required_radius_oracle_used"
    ]
    if not q018_warnings:
        raise PlotError("source metadata missing q018 required-radius oracle warnings.")
    ells = sorted(
        {
            int(_required_number(warning.get("ell"), "q018 warning ell"))
            for warning in q018_warnings
        }
    )
    sectors = sorted(
        {
            str(warning.get("sector"))
            for warning in q018_warnings
            if isinstance(warning.get("sector"), str)
        }
    )
    if not ells or not sectors:
        raise PlotError("source metadata has incomplete q018 warning coverage.")
    required_eval_radius = boundary.get("required_eval_radius")
    if required_eval_radius is None:
        required_eval_radius = q018_warnings[0].get("required_eval_radius")
    opt_in = boundary.get("experimental_required_radius_oracle")
    if opt_in is None:
        opt_in = q018_warnings[0].get("experimental_required_radius_oracle")
    if not isinstance(opt_in, str):
        raise PlotError("source metadata missing q018 opt-in label.")
    return {
        "warning_count": int(len(q018_warnings)),
        "ell_range": [int(ells[0]), int(ells[-1])],
        "ell_count": int(len(ells)),
        "sectors": sectors,
        "required_eval_radius": _required_number(
            required_eval_radius,
            "q018 required_eval_radius",
        ),
        "opt_in": opt_in,
        "valid_at_required_radius": all(
            warning.get("valid_at_required_radius") is True
            for warning in q018_warnings
        ),
    }


def _q018_oracle_summary_or_none(
    diagnostics: dict[str, Any],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    warnings = diagnostics.get("radial_diagnostic_warnings", [])
    if warnings is None:
        warnings = []
    if not isinstance(warnings, list):
        raise PlotError("source metadata radial_diagnostic_warnings must be a list.")
    q018_warnings = [
        warning
        for warning in warnings
        if isinstance(warning, dict)
        and warning.get("code") == "q018_required_radius_oracle_used"
    ]
    opt_in = boundary.get("experimental_required_radius_oracle")
    if not q018_warnings:
        if opt_in is not None:
            raise PlotError("source metadata has q018 opt-in but no oracle warnings.")
        return {
            "warning_count": 0,
            "warning_codes": [],
            "ell_range": None,
            "ell_count": 0,
            "sectors": [],
            "opt_in": None,
        }
    ells = sorted(
        {
            int(_required_number(warning.get("ell"), "q018 warning ell"))
            for warning in q018_warnings
        }
    )
    sectors = sorted(
        {
            str(warning.get("sector"))
            for warning in q018_warnings
            if isinstance(warning.get("sector"), str)
        }
    )
    if not ells or not sectors:
        raise PlotError("source metadata has incomplete q018 warning coverage.")
    if not isinstance(opt_in, str):
        opt_in = q018_warnings[0].get("experimental_required_radius_oracle")
    if not isinstance(opt_in, str):
        raise PlotError("source metadata missing q018 opt-in label.")
    return {
        "warning_count": int(len(q018_warnings)),
        "warning_codes": sorted(
            {
                str(warning.get("code"))
                for warning in q018_warnings
                if isinstance(warning.get("code"), str)
            }
        ),
        "ell_range": [int(ells[0]), int(ells[-1])],
        "ell_count": int(len(ells)),
        "sectors": sectors,
        "opt_in": opt_in,
    }


def _wave_kM(result: GridResult) -> float | None:
    config = result.metadata.get("config", {})
    wave = config.get("wave", {}) if isinstance(config, dict) else {}
    kM = wave.get("kM") if isinstance(wave, dict) else None
    if isinstance(kM, bool) or not isinstance(kM, (int, float)):
        return None
    kM = float(kM)
    if not np.isfinite(kM) or kM <= 0.0:
        return None
    return kM


def _required_wave_kM(result: GridResult) -> float:
    kM = _wave_kM(result)
    if kM is None:
        raise PlotError("plot-fig3-multifrequency-panel requires saved wave.kM metadata.")
    return kM


def _required_fig4_wave_kM(result: GridResult) -> float:
    kM = _wave_kM(result)
    if kM is None:
        raise PlotError(
            "plot-fig4-all-frequency-exact-angular requires saved wave.kM metadata."
        )
    return kM


def _diagnostics(result: GridResult) -> dict[str, Any]:
    diagnostics = result.metadata.get("diagnostics", {})
    return diagnostics if isinstance(diagnostics, dict) else {}


def _lmax_policy(result: GridResult) -> dict[str, Any]:
    policy = _diagnostics(result).get("lmax_convergence_policy", {})
    return policy if isinstance(policy, dict) else {}


def _actual_mask_counts(result: GridResult) -> dict[str, int]:
    if result.valid_mask is None:
        return {}
    valid_point_count = int(np.count_nonzero(result.valid_mask))
    return {
        "valid_point_count": valid_point_count,
        "invalid_point_count": int(result.valid_mask.size - valid_point_count),
    }


def _symmetric_color_limits(
    result: GridResult,
    values_by_component: list[np.ndarray],
) -> tuple[float, float]:
    assert result.valid_mask is not None
    finite_values = []
    for values in values_by_component:
        valid_finite = result.valid_mask & np.isfinite(values)
        finite_values.append(values[valid_finite])
    finite_values = [values for values in finite_values if values.size]
    if not finite_values:
        raise PlotError("plot-fig3-panel found no finite valid field values.")
    merged = np.concatenate(finite_values)
    vmax = float(np.max(np.abs(merged)))
    if not np.isfinite(vmax):
        raise PlotError("plot-fig3-panel found non-finite color scale.")
    if vmax == 0.0:
        vmax = float(np.finfo(float).eps)
    return -vmax, vmax


def _symmetric_color_limits_across_results(
    results: list[GridResult],
    values_by_result: list[np.ndarray],
) -> tuple[float, float]:
    finite_values = []
    for result, values in zip(results, values_by_result, strict=True):
        assert result.valid_mask is not None
        valid_finite = result.valid_mask & np.isfinite(values)
        finite_values.append(values[valid_finite])
    finite_values = [values for values in finite_values if values.size]
    if not finite_values:
        raise PlotError(
            "plot-fig3-multifrequency-panel found no finite valid field values."
        )
    merged = np.concatenate(finite_values)
    vmax = float(np.max(np.abs(merged)))
    if not np.isfinite(vmax):
        raise PlotError("plot-fig3-multifrequency-panel found non-finite color scale.")
    if vmax == 0.0:
        vmax = float(np.finfo(float).eps)
    return -vmax, vmax


def _background_mass(result: GridResult) -> float | None:
    config = result.metadata.get("config", {})
    background = config.get("background", {}) if isinstance(config, dict) else {}
    mass = background.get("M") if isinstance(background, dict) else None
    if isinstance(mass, bool) or not isinstance(mass, (int, float)):
        return None
    mass = float(mass)
    if not np.isfinite(mass) or mass <= 0.0:
        return None
    return mass


def _shared_background_mass(results: list[GridResult]) -> float | None:
    masses = [_background_mass(result) for result in results]
    finite_masses = [mass for mass in masses if mass is not None]
    if not finite_masses:
        return None
    first = finite_masses[0]
    if any(not np.isclose(mass, first, rtol=0.0, atol=1.0e-12) for mass in finite_masses):
        raise PlotError(
            "plot-fig3-multifrequency-panel requires matching background M metadata."
        )
    return first


def _colorbar_label(component: str, quantity: str) -> str:
    return f"{quantity}({component})"


__all__ = [
    "PlotError",
    "plot_amplification_from_result",
    "plot_convergence_from_result",
    "plot_fig3_multifrequency_panel_from_results",
    "plot_fig3_panel_from_result",
    "plot_fig4_all_frequency_exact_angular_from_results",
    "plot_fig4_exact_angular_from_result",
    "plot_wavefield_from_result",
]
