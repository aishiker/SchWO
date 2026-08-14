from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from schwgw.scattering.kirchhoff import compute_kirchhoff_figure_consistent
from schwgw.scattering.rayleigh_sommerfeld import (
    compute_rayleigh_sommerfeld_point_mass_phase_screen,
)


POINT_X_OVER_M = np.asarray([0.0, 1.0, 2.0, 3.0, 10.0, 15.0, 20.0, 25.0])
POINT_Z_OVER_M = 30.0
ANCHOR_KM = np.asarray(
    [0.001, 10.0 ** (-2.25), 0.01, 0.1, 0.5, 1.0, 2.0, 4.0]
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare the standard point-mass Fresnel--Kirchhoff factor with "
            "an exact Rayleigh--Sommerfeld-I propagation of the same scalar "
            "thin-lens phase screen."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "runs/phase5/paper_figures/"
            "rayleigh_sommerfeld_point_mass_diagnostic_20260810_v3"
        ),
    )
    parser.add_argument("--dps", type=int, default=40)
    parser.add_argument("--audit-dps", type=int, default=50)
    parser.add_argument("--workers", type=int, default=4)
    return parser


def _frequency_grid() -> np.ndarray:
    long_wave = np.geomspace(1.0e-3, 0.1, 17)
    full = np.linspace(0.1, 4.0, 40)
    return np.unique(np.concatenate((long_wave, full, ANCHOR_KM)))


def _rs_worker(payload):
    point_index, kM, transverse, distance, dps, prop_target, evan_target = payload
    result = compute_rayleigh_sommerfeld_point_mass_phase_screen(
        kM_values=np.asarray(kM),
        transverse_x_over_M=np.asarray([transverse]),
        propagation_z_over_M=np.asarray([distance]),
        dps=dps,
        propagating_decay_target=prop_target,
        evanescent_decay_target=evan_target,
    )
    return (
        point_index,
        result.F_complex[:, 0],
        result.F_propagating[:, 0],
        result.F_evanescent[:, 0],
    )


def _compute_rs_grid(
    *,
    kM: np.ndarray,
    transverse: np.ndarray,
    distance: np.ndarray,
    dps: int,
    propagating_decay_target: float,
    evanescent_decay_target: float,
    workers: int,
):
    shape = (kM.size, transverse.size)
    total = np.empty(shape, dtype=np.complex128)
    propagating = np.empty_like(total)
    evanescent = np.empty_like(total)
    payloads = [
        (
            index,
            kM,
            x_value,
            z_value,
            dps,
            propagating_decay_target,
            evanescent_decay_target,
        )
        for index, (x_value, z_value) in enumerate(
            zip(transverse, distance, strict=True)
        )
    ]
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for index, values, prop_values, evan_values in executor.map(
            _rs_worker, payloads
        ):
            total[:, index] = values
            propagating[:, index] = prop_values
            evanescent[:, index] = evan_values
    return total, propagating, evanescent


def _style_axis(axis, *, panel: str) -> None:
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.tick_params(direction="out", length=3.5, width=0.8)
    axis.text(
        -0.13,
        1.04,
        f"({panel})",
        transform=axis.transAxes,
        ha="left",
        va="bottom",
        fontsize=10,
        fontweight="bold",
    )


def _plot_full_range(
    *,
    output_dir: Path,
    kM: np.ndarray,
    fresnel: np.ndarray,
    rs: np.ndarray,
) -> tuple[Path, Path]:
    colors = {
        0: "#000000",
        3: "#0072B2",
        4: "#E69F00",
        7: "#CC79A7",
    }
    fig, axes = plt.subplots(2, 2, figsize=(7.05, 5.7), sharex=True)
    groups = ((0, 3), (4, 7))
    for column, indices in enumerate(groups):
        axis = axes[0, column]
        for index in indices:
            color = colors[index]
            x_label = f"x/M={POINT_X_OVER_M[index]:g}"
            axis.plot(
                kM,
                np.abs(rs[:, index]),
                color=color,
                linewidth=1.45,
                label=f"RS-I, {x_label}",
            )
            axis.plot(
                kM,
                np.abs(fresnel[:, index]),
                color=color,
                linewidth=1.15,
                linestyle="--",
                label=f"Fresnel, {x_label}",
            )
        axis.set_ylabel(r"$|F|$")
        axis.set_xlim(0.0, 4.0)
        axis.legend(frameon=False, fontsize=7.1, ncol=1, handlelength=2.5)
        _style_axis(axis, panel="A" if column == 0 else "B")

    selected = (0, 3, 4, 7)
    amplitude_residual = np.abs(rs) / np.abs(fresnel) - 1.0
    phase_residual = np.unwrap(np.angle(rs / fresnel), axis=0)
    for index in selected:
        label = rf"$x/M={POINT_X_OVER_M[index]:g}$"
        axes[1, 0].plot(
            kM,
            amplitude_residual[:, index],
            color=colors[index],
            linewidth=1.35,
            label=label,
        )
        axes[1, 1].plot(
            kM,
            phase_residual[:, index],
            color=colors[index],
            linewidth=1.35,
            label=label,
        )
    axes[1, 0].axhline(0.0, color="#777777", linewidth=0.75)
    axes[1, 1].axhline(0.0, color="#777777", linewidth=0.75)
    axes[1, 0].set_ylabel(r"$|F_{\rm RS}|/|F_{\rm Fr}|-1$")
    axes[1, 1].set_ylabel(r"$\arg(F_{\rm RS}/F_{\rm Fr})$ (rad)")
    for column, panel in enumerate(("C", "D")):
        axes[1, column].set_xlabel(r"$kM$")
        axes[1, column].set_xlim(0.0, 4.0)
        axes[1, column].legend(frameon=False, fontsize=7.4, ncol=2)
        _style_axis(axes[1, column], panel=panel)

    fig.suptitle(
        "Exact RS-I propagation versus the point-mass Fresnel integral",
        fontsize=10.5,
        y=0.995,
    )
    fig.tight_layout(rect=(0.02, 0.01, 1.0, 0.97), h_pad=1.4, w_pad=1.5)
    png = output_dir / "rs_vs_fresnel_full_range.png"
    pdf = output_dir / "rs_vs_fresnel_full_range.pdf"
    fig.savefig(png, dpi=600, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return png, pdf


def _plot_long_wave(
    *,
    output_dir: Path,
    kM: np.ndarray,
    fresnel: np.ndarray,
    rs_li: np.ndarray,
    rs_li_evanescent: np.ndarray,
    rs_cartesian: np.ndarray,
) -> tuple[Path, Path]:
    colors = {
        0: "#000000",
        3: "#0072B2",
        4: "#E69F00",
        7: "#CC79A7",
    }
    selected = (0, 3, 4, 7)
    mask = kM <= 0.2
    fig, axes = plt.subplots(1, 3, figsize=(7.05, 2.75))
    for index in selected:
        label = rf"$x/M={POINT_X_OVER_M[index]:g}$"
        axes[0].loglog(
            kM[mask],
            np.abs(rs_li[mask, index] / fresnel[mask, index] - 1.0),
            color=colors[index],
            linewidth=1.35,
            label=label,
        )
        axes[1].loglog(
            kM[mask],
            np.abs(rs_li_evanescent[mask, index])
            / np.maximum(np.abs(rs_li[mask, index]), np.finfo(float).tiny),
            color=colors[index],
            linewidth=1.35,
            label=label,
        )
        axes[2].loglog(
            kM[mask],
            np.abs(rs_li[mask, index] / rs_cartesian[mask, index] - 1.0),
            color=colors[index],
            linewidth=1.35,
            label=label,
        )
    axes[0].set_ylabel(r"$|F_{\rm RS}/F_{\rm Fr}-1|$")
    axes[1].set_ylabel(r"$|F_{\rm ev}|/|F_{\rm RS}|$")
    axes[2].set_ylabel("geometry-lift difference")
    for index, panel in enumerate(("A", "B", "C")):
        axes[index].set_xlabel(r"$kM$")
        axes[index].set_xlim(float(kM[mask][0]), float(kM[mask][-1]))
        axes[index].legend(frameon=False, fontsize=6.8, ncol=1)
        _style_axis(axes[index], panel=panel)
    fig.suptitle(
        "Long-wavelength RS-I diagnostics and model dependence",
        fontsize=10.5,
        y=1.01,
    )
    fig.tight_layout(rect=(0.01, 0.0, 1.0, 0.96), w_pad=1.2)
    png = output_dir / "rs_long_wavelength_diagnostics.png"
    pdf = output_dir / "rs_long_wavelength_diagnostics.pdf"
    fig.savefig(png, dpi=600, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return png, pdf


def main() -> int:
    args = _parser().parse_args()
    if args.workers < 1:
        raise ValueError("--workers must be positive.")
    args.output_dir.mkdir(parents=True, exist_ok=False)

    kM = _frequency_grid()
    radius = np.hypot(POINT_X_OVER_M, POINT_Z_OVER_M)
    theta = np.arctan2(POINT_X_OVER_M, POINT_Z_OVER_M)
    eta = 0.5 * np.sqrt(radius) * np.tan(theta)

    # This lift exactly reproduces Li--Hou--Zhao's printed eta coordinate in
    # the paraxial limit: x_RS/(2 sqrt(z_RS)) = eta.
    li_distance = radius
    li_transverse = radius * np.tan(theta)
    np.testing.assert_allclose(
        li_transverse / (2.0 * np.sqrt(li_distance)),
        eta,
        rtol=0.0,
        atol=2.0e-15,
    )
    fresnel = compute_kirchhoff_figure_consistent(
        kM_values=kM,
        r_over_M=radius,
        theta=theta,
        dps=max(args.dps, 40),
    ).F_complex

    rs_li, rs_li_propagating, rs_li_evanescent = _compute_rs_grid(
        kM=kM,
        transverse=li_transverse,
        distance=li_distance,
        dps=args.dps,
        propagating_decay_target=100.0,
        evanescent_decay_target=120.0,
        workers=args.workers,
    )
    rs_cartesian, rs_cartesian_propagating, rs_cartesian_evanescent = (
        _compute_rs_grid(
            kM=kM,
            transverse=POINT_X_OVER_M,
            distance=np.full(POINT_X_OVER_M.shape, POINT_Z_OVER_M),
            dps=args.dps,
            propagating_decay_target=100.0,
            evanescent_decay_target=120.0,
            workers=args.workers,
        )
    )

    audit_point_indices = np.asarray([0, 3, 7])
    audit_rs, audit_prop, audit_evan = _compute_rs_grid(
        kM=ANCHOR_KM,
        transverse=li_transverse[audit_point_indices],
        distance=li_distance[audit_point_indices],
        dps=args.audit_dps,
        propagating_decay_target=140.0,
        evanescent_decay_target=160.0,
        workers=min(args.workers, audit_point_indices.size),
    )
    main_anchor_indices = np.asarray(
        [int(np.flatnonzero(np.isclose(kM, value, rtol=0.0, atol=1.0e-14))[0]) for value in ANCHOR_KM]
    )
    main_audit_slice = rs_li[np.ix_(main_anchor_indices, audit_point_indices)]
    convergence_absolute = np.abs(audit_rs - main_audit_slice)
    convergence_relative = convergence_absolute / np.maximum(
        np.abs(audit_rs), np.finfo(float).tiny
    )

    data_path = args.output_dir / "rayleigh_sommerfeld_point_mass_diagnostic.npz"
    np.savez_compressed(
        data_path,
        kM=kM,
        x_over_M=POINT_X_OVER_M,
        z_over_M=np.asarray(POINT_Z_OVER_M),
        r_over_M=radius,
        theta=theta,
        eta=eta,
        li_lift_transverse_x_over_M=li_transverse,
        li_lift_propagation_z_over_M=li_distance,
        fresnel_F=fresnel,
        rs_li_lift_F=rs_li,
        rs_li_lift_propagating_F=rs_li_propagating,
        rs_li_lift_evanescent_F=rs_li_evanescent,
        rs_cartesian_F=rs_cartesian,
        rs_cartesian_propagating_F=rs_cartesian_propagating,
        rs_cartesian_evanescent_F=rs_cartesian_evanescent,
        audit_kM=ANCHOR_KM,
        audit_point_indices=audit_point_indices,
        audit_rs_li_lift_F=audit_rs,
        audit_rs_li_lift_propagating_F=audit_prop,
        audit_rs_li_lift_evanescent_F=audit_evan,
        convergence_absolute=convergence_absolute,
        convergence_relative=convergence_relative,
    )

    full_png, full_pdf = _plot_full_range(
        output_dir=args.output_dir,
        kM=kM,
        fresnel=fresnel,
        rs=rs_li,
    )
    long_png, long_pdf = _plot_long_wave(
        output_dir=args.output_dir,
        kM=kM,
        fresnel=fresnel,
        rs_li=rs_li,
        rs_li_evanescent=rs_li_evanescent,
        rs_cartesian=rs_cartesian,
    )

    amplitude_residual = np.abs(rs_li) / np.abs(fresnel) - 1.0
    complex_residual = np.abs(rs_li / fresnel - 1.0)
    phase_residual = np.unwrap(np.angle(rs_li / fresnel), axis=0)
    geometry_residual = np.abs(rs_li / rs_cartesian - 1.0)
    long_mask = kM <= 0.1

    anchors = {}
    for value, grid_index in zip(ANCHOR_KM, main_anchor_indices, strict=True):
        anchors[f"{value:g}"] = {
            "max_abs_amplitude_fractional_difference": float(
                np.max(np.abs(amplitude_residual[grid_index]))
            ),
            "max_abs_phase_difference_rad": float(
                np.max(np.abs(phase_residual[grid_index]))
            ),
            "max_complex_relative_difference": float(
                np.max(complex_residual[grid_index])
            ),
            "max_evanescent_fraction": float(
                np.max(
                    np.abs(rs_li_evanescent[grid_index])
                    / np.maximum(
                        np.abs(rs_li[grid_index]), np.finfo(float).tiny
                    )
                )
            ),
            "max_geometry_lift_difference": float(
                np.max(geometry_residual[grid_index])
            ),
        }

    output_paths = (data_path, full_png, full_pdf, long_png, long_pdf)
    metadata = {
        "schema": "schwo_rayleigh_sommerfeld_point_mass_diagnostic_v1",
        "scientific_status": "scalar_phase_screen_diagnostic_only",
        "purpose": (
            "Replace only the free-space paraxial propagation in the standard "
            "point-mass diffraction integral by exact Rayleigh--Sommerfeld-I "
            "propagation, while keeping the same weak-field scalar phase screen."
        ),
        "not_claimed": [
            "strict Li-paper reproduction",
            "strong-field Schwarzschild solution",
            "spin-2 polarization transport",
            "unique physical embedding of Li Eq. (47) at large angle",
        ],
        "grid": {
            "frequency_count": int(kM.size),
            "kM_min": float(kM[0]),
            "kM_max": float(kM[-1]),
            "x_over_M": POINT_X_OVER_M.tolist(),
            "z_over_M": POINT_Z_OVER_M,
        },
        "geometry": {
            "eq47_coordinate_matched": {
                "propagation_z_over_M": "r/M",
                "transverse_x_over_M": "(r/M) tan(theta)",
                "identity": "x_RS/(2 sqrt(z_RS)) = eta in Eq. (47)",
            },
            "cartesian_comparison": {
                "propagation_z_over_M": "30",
                "transverse_x_over_M": "Table-I x/M",
            },
        },
        "quadrature": {
            "dps": args.dps,
            "propagating_decay_target": 100.0,
            "evanescent_decay_target": 120.0,
            "audit_dps": args.audit_dps,
            "audit_propagating_decay_target": 140.0,
            "audit_evanescent_decay_target": 160.0,
            "max_absolute_replay_difference": float(
                np.max(convergence_absolute)
            ),
            "max_relative_replay_difference": float(
                np.max(convergence_relative)
            ),
        },
        "summary": {
            "max_complex_relative_difference_kM_le_0p1": float(
                np.max(complex_residual[long_mask])
            ),
            "max_abs_amplitude_fractional_difference_kM_le_0p1": float(
                np.max(np.abs(amplitude_residual[long_mask]))
            ),
            "max_abs_phase_difference_kM_le_0p1_rad": float(
                np.max(np.abs(phase_residual[long_mask]))
            ),
            "max_complex_relative_difference_full_grid": float(
                np.max(complex_residual)
            ),
            "max_abs_amplitude_fractional_difference_full_grid": float(
                np.max(np.abs(amplitude_residual))
            ),
            "max_abs_phase_difference_full_grid_rad": float(
                np.max(np.abs(phase_residual))
            ),
            "anchors": anchors,
        },
        "references": [
            "https://opg.optica.org/josa/abstract.cfm?uri=josa-54-5-587",
            "https://arxiv.org/abs/astro-ph/0305055",
            "https://arxiv.org/abs/2607.24723",
        ],
        "files": {
            path.name: {"sha256": _sha256(path), "size": path.stat().st_size}
            for path in output_paths
        },
    }
    metadata_path = args.output_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metadata, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
