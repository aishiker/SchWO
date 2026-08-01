"""Read-only Fig. 4 exact/asymptotic comparison renderer.

The finite-radius production artifacts store the scattered contribution used
for the wave-field plots.  Paper Fig. 4 instead plots the full field, so the
exact curves below add the incident plane wave from Eq. (46).  The
conventional curves must be computed before entering this module.  The
renderer validates those arrays and their durable source, but never imports or
calls a scattering implementation.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray

from schwgw.io.asymptotic import FIG8_KM_VALUES
from schwgw.io.results import load_results


class Fig4ComparisonError(ValueError):
    """Raised when the Fig. 4 comparison contract is not satisfied."""


def add_incident_plane_wave(
    theta: ArrayLike,
    *,
    scattered_plus: ArrayLike,
    scattered_cross: ArrayLike,
    k: float,
    r: float,
    A_plus: complex,
    A_cross: complex,
) -> tuple[NDArray[np.complex128], NDArray[np.complex128]]:
    """Return the full Fig. 4 field from saved scattered fields and Eq. (46)."""

    theta_values = np.asarray(theta, dtype=np.float64)
    plus = np.asarray(scattered_plus, dtype=np.complex128)
    cross = np.asarray(scattered_cross, dtype=np.complex128)
    if theta_values.ndim != 1 or theta_values.size == 0:
        raise Fig4ComparisonError("theta must be a non-empty vector")
    if plus.shape != theta_values.shape or cross.shape != theta_values.shape:
        raise Fig4ComparisonError("scattered fields must match theta")
    if np.any(theta_values < 0.0) or np.any(theta_values > np.pi):
        raise Fig4ComparisonError("theta must lie in [0, pi]")
    if not np.isfinite(k) or k <= 0.0 or not np.isfinite(r) or r <= 0.0:
        raise Fig4ComparisonError("k and r must be finite and positive")
    if not all(
        np.all(np.isfinite(value.real)) and np.all(np.isfinite(value.imag))
        for value in (plus, cross)
    ):
        raise Fig4ComparisonError("scattered fields must be finite")
    incident_phase = np.exp(1j * float(k) * float(r) * np.cos(theta_values))
    return (
        np.asarray(plus + complex(A_plus) * incident_phase, dtype=np.complex128),
        np.asarray(cross + complex(A_cross) * incident_phase, dtype=np.complex128),
    )


def asymptotic_total_polarizations(
    theta: ArrayLike,
    *,
    k: float,
    r: float,
    M: float,
    M22: ArrayLike,
    M12: ArrayLike,
    A_plus: complex,
    A_cross: complex,
) -> tuple[NDArray[np.complex128], NDArray[np.complex128]]:
    """Return incident plus reflected conventional ``h_+`` and ``h_x``.

    At ``phi=0`` Schwarzschild symmetry gives ``M11=M22`` and
    ``M21=-M12``.  The handed convention is exactly
    ``A_L,R=(A_+ +/- i A_x)/sqrt(2)``.
    """

    theta_values = np.asarray(theta, dtype=np.float64)
    m22 = np.asarray(M22, dtype=np.complex128)
    m12 = np.asarray(M12, dtype=np.complex128)
    if theta_values.ndim != 1 or theta_values.size == 0:
        raise Fig4ComparisonError("theta must be a non-empty vector")
    if m22.shape != theta_values.shape or m12.shape != theta_values.shape:
        raise Fig4ComparisonError("M22 and M12 must match theta")
    if np.any(theta_values < 0.0) or np.any(theta_values > np.pi):
        raise Fig4ComparisonError("theta must lie in [0, pi]")
    if not all(np.isfinite(value) and value > 0.0 for value in (k, r, M)):
        raise Fig4ComparisonError("k, r and M must be finite and positive")
    if r <= 2.0 * M:
        raise Fig4ComparisonError("r must lie outside the Schwarzschild horizon")
    if not (
        np.all(np.isfinite(m22.real))
        and np.all(np.isfinite(m22.imag))
        and np.all(np.isfinite(m12.real))
        and np.all(np.isfinite(m12.imag))
    ):
        raise Fig4ComparisonError("scattering matrix entries must be finite")

    root_two = np.sqrt(2.0)
    A_left = (complex(A_plus) + 1j * complex(A_cross)) / root_two
    A_right = (complex(A_plus) - 1j * complex(A_cross)) / root_two
    r_star = r + 2.0 * M * np.log(r / (2.0 * M) - 1.0)
    radial = np.exp(1j * k * r_star) / r
    left_reflected = radial * (m22 * A_left + m12 * A_right)
    right_reflected = radial * (-m12 * A_left + m22 * A_right)
    incident_phase = np.exp(1j * k * r * np.cos(theta_values))
    left = left_reflected + A_left * incident_phase
    right = right_reflected + A_right * incident_phase
    h_plus = (left + right) / root_two
    h_cross = -1j * (left - right) / root_two
    return (
        np.asarray(h_plus, dtype=np.complex128),
        np.asarray(h_cross, dtype=np.complex128),
    )


def render_fig4_exact_asymptotic_comparison(
    exact_paths: Sequence[str | Path],
    *,
    asymptotic_plus: ArrayLike,
    asymptotic_cross: ArrayLike,
    asymptotic_source: str | Path,
    output_dir: str | Path,
    dpi: int = 600,
) -> dict[str, Path]:
    """Render the four-panel exact/q=2 comparison from precomputed fields."""

    if len(exact_paths) != 4:
        raise Fig4ComparisonError("Fig. 4 requires exactly four exact inputs")
    if isinstance(dpi, bool) or not isinstance(dpi, int) or dpi <= 0:
        raise Fig4ComparisonError("dpi must be a positive integer")
    conventional_plus_rows = np.asarray(asymptotic_plus, dtype=np.complex128)
    conventional_cross_rows = np.asarray(asymptotic_cross, dtype=np.complex128)
    expected_shape = (len(FIG8_KM_VALUES), 1025)
    if (
        conventional_plus_rows.shape != expected_shape
        or conventional_cross_rows.shape != expected_shape
    ):
        raise Fig4ComparisonError(
            "precomputed asymptotic fields must both have shape (4, 1025)"
        )
    for name, values in (
        ("asymptotic_plus", conventional_plus_rows),
        ("asymptotic_cross", conventional_cross_rows),
    ):
        if not np.all(np.isnan(values[:, 0].real) & np.isnan(values[:, 0].imag)):
            raise Fig4ComparisonError(f"{name} must be NaN exactly at theta=0")
        positive_values = values[:, 1:]
        if not np.all(
            np.isfinite(positive_values.real) & np.isfinite(positive_values.imag)
        ):
            raise Fig4ComparisonError(
                f"{name} must be finite away from the forward axis"
            )
    asymptotic_path = Path(asymptotic_source)
    if not asymptotic_path.is_file():
        raise Fig4ComparisonError(
            f"missing precomputed asymptotic source: {asymptotic_path}"
        )
    paths = [Path(path) for path in exact_paths]
    results = [load_results(path) for path in paths]

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "data": out / "fig4_exact_asymptotic_q2_comparison.npz",
        "json": out / "fig4_exact_asymptotic_q2_comparison.json",
        "pdf": out / "fig4_exact_asymptotic_q2_comparison.pdf",
        "png": out / "fig4_exact_asymptotic_q2_comparison_600dpi.png",
    }
    if any(path.exists() for path in artifacts.values()):
        raise FileExistsError("refusing to overwrite Fig. 4 comparison artifacts")

    theta_rows: list[NDArray[np.float64]] = []
    exact_plus: list[NDArray[np.complex128]] = []
    exact_cross: list[NDArray[np.complex128]] = []
    scattered_plus: list[NDArray[np.complex128]] = []
    scattered_cross: list[NDArray[np.complex128]] = []
    asymptotic_plus: list[NDArray[np.complex128]] = []
    asymptotic_cross: list[NDArray[np.complex128]] = []
    lmax_values: list[int] = []
    for index, (result, kM) in enumerate(zip(results, FIG8_KM_VALUES, strict=True)):
        theta = np.asarray(result.theta, dtype=np.float64)
        phi = np.asarray(result.phi, dtype=np.float64)
        config = result.metadata.get("config", {})
        wave = config.get("wave", {}) if isinstance(config, dict) else {}
        observer = config.get("observer", {}) if isinstance(config, dict) else {}
        numerics = config.get("numerics", {}) if isinstance(config, dict) else {}
        if (
            theta.shape != (1025,)
            or phi.shape != (1,)
            or phi[0] != 0.0
            or abs(float(wave.get("kM", np.nan)) - kM) > 1.0e-12
        ):
            raise Fig4ComparisonError("exact inputs violate the fixed angular grid")
        lmax = int(numerics.get("lmax", -1))
        if lmax < 2:
            raise Fig4ComparisonError("exact lmax must be at least two")
        r = float(observer.get("r", np.nan))
        M = float(config.get("background", {}).get("M", np.nan))
        a_plus_record = wave.get("A_plus", {})
        a_cross_record = wave.get("A_cross", {})
        A_plus = complex(a_plus_record.get("real"), a_plus_record.get("imag"))
        A_cross = complex(a_cross_record.get("real"), a_cross_record.get("imag"))
        conventional_plus = conventional_plus_rows[index]
        conventional_cross = conventional_cross_rows[index]
        saved_plus = np.asarray(result.h_plus[:, 0], dtype=np.complex128)
        saved_cross = np.asarray(result.h_cross[:, 0], dtype=np.complex128)
        full_plus, full_cross = add_incident_plane_wave(
            theta,
            scattered_plus=saved_plus,
            scattered_cross=saved_cross,
            k=kM / M,
            r=r,
            A_plus=A_plus,
            A_cross=A_cross,
        )
        theta_rows.append(theta)
        scattered_plus.append(saved_plus)
        scattered_cross.append(saved_cross)
        exact_plus.append(full_plus)
        exact_cross.append(full_cross)
        asymptotic_plus.append(conventional_plus)
        asymptotic_cross.append(conventional_cross)
        lmax_values.append(lmax)

    arrays = {
        "kM": np.asarray(FIG8_KM_VALUES, dtype=np.float64),
        "lmax": np.asarray(lmax_values, dtype=np.int64),
        "theta": np.stack(theta_rows),
        "h_plus_scattered_finite_radius": np.stack(scattered_plus),
        "h_cross_scattered_finite_radius": np.stack(scattered_cross),
        "h_plus_exact": np.stack(exact_plus),
        "h_cross_exact": np.stack(exact_cross),
        "h_plus_asymptotic_q2": np.stack(asymptotic_plus),
        "h_cross_asymptotic_q2": np.stack(asymptotic_cross),
    }
    _atomic_save_npz(artifacts["data"], arrays)
    manifest = {
        "schema_version": "schwgw_fig4_exact_asymptotic_q2_v2",
        "figure": 4,
        "source_exact": [
            {"path": str(path.resolve()), "sha256": _sha256(path)} for path in paths
        ],
        "source_precomputed_asymptotic_fields": {
            "path": str(asymptotic_path.resolve()),
            "sha256": _sha256(asymptotic_path),
        },
        "reduction_order": 2,
        "asymptotic_field_policy": (
            "caller-supplied precomputed arrays; renderer performs no scattering "
            "calculation"
        ),
        "exact_field_composition": (
            "saved finite-radius scattered field + incident plane wave from Eq. (46)"
        ),
        "theta_zero_policy": "asymptotic value is NaN; no extrapolation",
        "display_ylim": [0.0, 9.0],
        "display_clipping_only": True,
        "no_solver_rerun": True,
    }
    _atomic_write_json(artifacts["json"], manifest)
    _render(arrays, artifacts["pdf"], artifacts["png"], dpi=dpi)
    return artifacts


def _render(arrays: dict[str, NDArray[Any]], pdf: Path, png: Path, *, dpi: int) -> None:
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    figure, axes = plt.subplots(
        2, 2, figsize=(11.5, 5.6), sharex=True, sharey=True, constrained_layout=True
    )
    for index, axis in enumerate(axes.flat):
        x = arrays["theta"][index] / np.pi
        axis.plot(x, np.abs(arrays["h_plus_exact"][index]), color="#002cff", lw=1.8)
        axis.plot(x, np.abs(arrays["h_cross_exact"][index]), color="#f01e1e", lw=1.8)
        axis.plot(
            x,
            np.abs(arrays["h_plus_asymptotic_q2"][index]),
            color="#7aa6d8",
            lw=1.15,
            alpha=0.62,
        )
        axis.plot(
            x,
            np.abs(arrays["h_cross_asymptotic_q2"][index]),
            color="#ff7777",
            lw=1.15,
            alpha=0.72,
        )
        axis.text(0.10, 0.82, rf"$k={arrays['kM'][index]:g}/M$", transform=axis.transAxes)
        axis.set_xlim(0.0, 1.0)
        axis.set_ylim(0.0, 9.0)
        axis.grid(color="0.75", lw=0.55, alpha=0.65)
    axes[0, 0].legend(
        [
            r"$+$, exact",
            r"$\times$, exact",
            r"$+$, asymptotic ($q=2$)",
            r"$\times$, asymptotic ($q=2$)",
        ],
        frameon=True,
        fontsize=8,
        loc="upper right",
    )
    for axis in axes[:, 0]:
        axis.set_ylabel(r"$|\tilde h_A(k,r)|$")
    for axis in axes[1, :]:
        axis.set_xlabel(r"$\theta/\pi$")
    _atomic_save_figure(figure, pdf, format="pdf")
    _atomic_save_figure(figure, png, format="png", dpi=dpi)
    plt.close(figure)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atomic_save_npz(path: Path, arrays: dict[str, NDArray[Any]]) -> None:
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w+b", prefix=f".{path.name}.", suffix=".partial", dir=path.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            np.savez(handle, **arrays)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", prefix=f".{path.name}.", suffix=".partial", dir=path.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            json.dump(payload, handle, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _atomic_save_figure(figure: Any, path: Path, **kwargs: Any) -> None:
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{path.name}.", suffix=".partial", dir=path.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
        figure.savefig(temporary, **kwargs)
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


__all__ = [
    "Fig4ComparisonError",
    "add_incident_plane_wave",
    "asymptotic_total_polarizations",
    "render_fig4_exact_asymptotic_comparison",
]
