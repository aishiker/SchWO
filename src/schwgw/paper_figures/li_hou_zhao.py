"""Li-Hou-Zhao Fig. 1 radial data and stable strict-Kinnersley Fig. 2 data.

The routines in this module deliberately stop before the incident-tetrad
transform and before packaged polarization scalars when computing Fig. 2.
The resulting Fig. 2 dataset is a stable recomputation of the equations in
the paper, not a digitized copy of the published raster.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any, Protocol

import numpy as np
from numpy.typing import ArrayLike, NDArray

from schwgw.backgrounds import SchwarzschildBackground
from schwgw.numerics import BoundaryConfig, RadialSolution, solve_radial_mode
from schwgw.perturbations import Sector, reconstruct_metric_mode
from schwgw.scattering.weyl import assemble_weyl_scalars, weyl_mode_components
from schwgw.waves.incident import IncidentPlaneGW


PAPER_PATH = Path("references/papers/li_hou_zhao_2025_spin_wave_optics.pdf")
PAPER_SHA256 = "a1da12f51d2667c5b3a9662eb0291efd2211dd6f093698f32ecbbd5d64f726d6"
FIG1_ELLS = np.asarray((2, 3, 4, 5, 60, 61, 62, 63), dtype=np.int64)
FIG2_KM = np.asarray((0.5, 1.0, 1.5, 2.0), dtype=np.float64)
FIG2_THETA = np.asarray((0.0, np.pi / 6.0, np.pi / 3.0, np.pi / 2.0), dtype=np.float64)
FOURIER_CONVENTION = "exp(-i k t)"
METRIC_SIGNATURE = "(-,+,+,+)"


class RadialSolver(Protocol):
    def __call__(
        self,
        sector: Sector,
        ell: int,
        k: float,
        background: SchwarzschildBackground,
        boundary_config: BoundaryConfig,
    ) -> RadialSolution: ...


ProgressCallback = Callable[[dict[str, Any]], None]


@dataclass(frozen=True)
class Figure1Dataset:
    r: NDArray[np.float64]
    r_star: NDArray[np.float64]
    ell_values: NDArray[np.int64]
    exact_odd: NDArray[np.complex128]
    asymptotic_odd: NDArray[np.complex128]
    exact_even: NDArray[np.complex128]
    asymptotic_even: NDArray[np.complex128]
    A_in_odd: NDArray[np.complex128]
    A_out_odd: NDArray[np.complex128]
    phase_factor_odd: NDArray[np.complex128]
    A_in_even: NDArray[np.complex128]
    A_out_even: NDArray[np.complex128]
    phase_factor_even: NDArray[np.complex128]
    metadata: dict[str, Any]

    def __post_init__(self) -> None:
        _validate_figure1(self)


@dataclass(frozen=True)
class Figure2Dataset:
    kM_values: NDArray[np.float64]
    theta_values: NDArray[np.float64]
    phi: float
    lmax_values: NDArray[np.int64]
    psi4_kinnersley: NDArray[np.complex128]
    psi4_shell_kinnersley: NDArray[np.complex128]
    log10_abs_psi4: NDArray[np.float64]
    solve_counts: NDArray[np.int64]
    elapsed_seconds_by_frequency: NDArray[np.float64]
    metadata: dict[str, Any]

    def __post_init__(self) -> None:
        _validate_figure2(self)


def normalized_radial(solution: RadialSolution, r: ArrayLike) -> complex | NDArray[np.complex128]:
    """Return the exact normalized master field ``psi(r) / A_in``."""

    A_in = complex(solution.A_in)
    if not np.isfinite(A_in.real) or not np.isfinite(A_in.imag) or A_in == 0.0:
        raise ValueError("A_in must be finite and nonzero.")
    value = np.asarray(solution.psi_at(r), dtype=np.complex128) / A_in
    _require_finite_complex(value, "normalized radial field")
    if np.asarray(r).shape == ():
        return complex(value)
    return value


def leading_radial_asymptote(
    solution: RadialSolution,
    r: ArrayLike,
) -> complex | NDArray[np.complex128]:
    """Return the leading two-wave asymptote using the tortoise coordinate.

    This uses ``A_out/A_in`` directly.  It never reconstructs the phase from
    ``phase_shift`` and therefore has no logarithm/branch ambiguity.
    """

    radius = np.asarray(r, dtype=np.float64)
    r_star = np.asarray(solution.background.r_star(radius), dtype=np.float64)
    ratio = complex(solution.A_out) / complex(solution.A_in)
    value = np.exp(-1j * solution.k * r_star) + ratio * np.exp(
        1j * solution.k * r_star
    )
    value = np.asarray(value, dtype=np.complex128)
    _require_finite_complex(value, "leading radial asymptote")
    if radius.shape == ():
        return complex(value)
    return value


def compute_figure1_dataset(
    *,
    radial_solver: RadialSolver = solve_radial_mode,
    r: NDArray[np.float64] | None = None,
    boundary_config: BoundaryConfig | None = None,
    progress: ProgressCallback | None = None,
) -> Figure1Dataset:
    """Compute both odd and even candidates for Li-Hou-Zhao Fig. 1."""

    radius = (
        np.linspace(6.0, 66.0, 1201, dtype=np.float64)
        if r is None
        else np.asarray(r, dtype=np.float64)
    )
    if radius.ndim != 1 or radius.size < 2 or np.any(np.diff(radius) <= 0.0):
        raise ValueError("r must be a strictly increasing one-dimensional grid.")
    if radius[0] <= 2.0 or not np.all(np.isfinite(radius)):
        raise ValueError("Fig. 1 radii must be finite and outside the horizon.")
    config = boundary_config or BoundaryConfig(
        r_in_eps=1.0e-6,
        r_out=300.0,
        rtol=1.0e-10,
        atol=1.0e-12,
        required_eval_radius=float(radius[-1]),
    )
    background = SchwarzschildBackground(M=1.0)
    r_star = np.asarray(background.r_star(radius), dtype=np.float64)
    values: dict[str, list[NDArray[np.complex128]]] = {
        "exact_odd": [],
        "asymptotic_odd": [],
        "exact_even": [],
        "asymptotic_even": [],
    }
    coefficients: dict[str, list[complex]] = {
        "A_in_odd": [],
        "A_out_odd": [],
        "phase_factor_odd": [],
        "A_in_even": [],
        "A_out_even": [],
        "phase_factor_even": [],
    }
    diagnostics: list[dict[str, Any]] = []
    started = time.perf_counter()
    for sector in (Sector.ODD, Sector.EVEN):
        for ell_value in FIG1_ELLS:
            ell = int(ell_value)
            solve_started = time.perf_counter()
            solution = radial_solver(sector, ell, 1.0, background, config)
            solve_elapsed = time.perf_counter() - solve_started
            exact = np.asarray(normalized_radial(solution, radius), dtype=np.complex128)
            asymptotic = np.asarray(
                leading_radial_asymptote(solution, radius), dtype=np.complex128
            )
            phase_identity = -complex(solution.A_out) / (
                ((-1) ** ell) * complex(solution.A_in)
            )
            if not np.array_equal(
                np.asarray(phase_identity, dtype=np.complex128),
                np.asarray(solution.phase_factor, dtype=np.complex128),
            ):
                raise RuntimeError("A_out/A_in and phase_factor identity drift.")
            suffix = sector.value
            values[f"exact_{suffix}"].append(exact)
            values[f"asymptotic_{suffix}"].append(asymptotic)
            coefficients[f"A_in_{suffix}"].append(complex(solution.A_in))
            coefficients[f"A_out_{suffix}"].append(complex(solution.A_out))
            coefficients[f"phase_factor_{suffix}"].append(
                complex(solution.phase_factor)
            )
            record = _solution_diagnostic_record(
                solution,
                solve_elapsed_seconds=solve_elapsed,
            )
            diagnostics.append(record)
            if progress is not None:
                progress(
                    {
                        "ell": ell,
                        "event": "fig1_mode_complete",
                        "sector": sector.value,
                        "solve_elapsed_seconds": solve_elapsed,
                    }
                )

    metadata = _base_metadata()
    metadata.update(
        {
            "boundary_config": asdict(config),
            "caption_sector_text": "widehat{u}^{(+)}",
            "equation_43_sector_text": "widehat{u}^{(-)}",
            "equation_44_sector_text": "widehat{u}^{(-)}",
            "figure": 1,
            "fourier_convention": FOURIER_CONVENTION,
            "kM": 1.0,
            "normalization": "solution.psi_at(r) / solution.A_in",
            "paper_ambiguity": (
                "The Fig. 1 caption uses widehat{u}^{(+)}, while the y-axis, "
                "Eq. (43), Eq. (44), and the prose use widehat{u}^{(-)}."
            ),
            "primary_sector": "odd",
            "radial_asymptote": (
                "exp(-i k r_star) + (A_out/A_in) exp(+i k r_star); "
                "equivalently exp(-i k r_star) - (-1)^ell phase_factor "
                "exp(+i k r_star)"
            ),
            "r_grid_note": (
                "The text does not state Fig. 1 endpoints or sampling; 6..66 "
                "and 1201 deterministic inclusive samples are frozen from "
                "direct page-7 geometry."
            ),
            "schema_version": "li_hou_zhao_figure1_radial_v1",
            "sector_candidates": ["odd", "even"],
            "solve_count": len(diagnostics),
            "solve_diagnostics": diagnostics,
            "total_compute_seconds": time.perf_counter() - started,
            "uses_phase_shift_logarithm": False,
            "uses_tortoise_coordinate": True,
        }
    )
    return Figure1Dataset(
        r=radius,
        r_star=r_star,
        ell_values=FIG1_ELLS.copy(),
        exact_odd=np.stack(values["exact_odd"]),
        asymptotic_odd=np.stack(values["asymptotic_odd"]),
        exact_even=np.stack(values["exact_even"]),
        asymptotic_even=np.stack(values["asymptotic_even"]),
        A_in_odd=np.asarray(coefficients["A_in_odd"], dtype=np.complex128),
        A_out_odd=np.asarray(coefficients["A_out_odd"], dtype=np.complex128),
        phase_factor_odd=np.asarray(
            coefficients["phase_factor_odd"], dtype=np.complex128
        ),
        A_in_even=np.asarray(coefficients["A_in_even"], dtype=np.complex128),
        A_out_even=np.asarray(coefficients["A_out_even"], dtype=np.complex128),
        phase_factor_even=np.asarray(
            coefficients["phase_factor_even"], dtype=np.complex128
        ),
        metadata=metadata,
    )


def compute_strict_np_psi4_convergence(
    *,
    kM_values: ArrayLike = FIG2_KM,
    theta_values: ArrayLike = FIG2_THETA,
    phi: float = 0.0,
    A_plus: complex = 0.9 + 1.1j,
    A_cross: complex = 0.4 + 0.6j,
    radius: float = 60.0,
    lmax: int = 180,
    radial_solver: RadialSolver = solve_radial_mode,
    boundary_config: BoundaryConfig | None = None,
    progress: ProgressCallback | None = None,
) -> Figure2Dataset:
    """Incrementally sum strict Kinnersley-frame ``Psi4`` through each shell.

    One radial solution is computed per ``(k, sector, ell)`` and is shared
    across all observer angles and both nonzero incident ``m`` values.
    """

    kM = np.asarray(kM_values, dtype=np.float64)
    theta = np.asarray(theta_values, dtype=np.float64)
    if kM.ndim != 1 or theta.ndim != 1 or not kM.size or not theta.size:
        raise ValueError("kM_values and theta_values must be nonempty vectors.")
    if np.any(kM <= 0.0) or not np.all(np.isfinite(kM)):
        raise ValueError("kM_values must be finite and positive.")
    if np.any((theta < 0.0) | (theta > np.pi)) or not np.all(np.isfinite(theta)):
        raise ValueError("theta_values must lie in [0, pi].")
    if not isinstance(lmax, int) or lmax < 2:
        raise ValueError("lmax must be an integer >= 2.")
    if radius <= 2.0 or not np.isfinite(radius):
        raise ValueError("radius must be finite and outside the horizon.")
    config = boundary_config or BoundaryConfig(
        r_in_eps=1.0e-6,
        r_out=300.0,
        rtol=1.0e-10,
        atol=1.0e-12,
        required_eval_radius=float(radius),
        experimental_required_radius_oracle="q018_riccati",
    )
    background = SchwarzschildBackground(M=1.0)
    lmax_values = np.arange(2, lmax + 1, dtype=np.int64)
    shape = (kM.size, theta.size, lmax_values.size)
    cumulative_values = np.empty(shape, dtype=np.complex128)
    shell_values = np.empty(shape, dtype=np.complex128)
    solve_counts = np.zeros(kM.size, dtype=np.int64)
    elapsed_by_frequency = np.zeros(kM.size, dtype=np.float64)
    mode_diagnostics: list[dict[str, Any]] = []
    total_started = time.perf_counter()

    for frequency_index, kM_value in enumerate(kM):
        frequency_started = time.perf_counter()
        k = float(kM_value / background.M)
        incident = IncidentPlaneGW(k=k, A_plus=A_plus, A_cross=A_cross)
        cumulative = np.zeros(theta.size, dtype=np.complex128)
        for shell_index, ell_value in enumerate(lmax_values):
            ell = int(ell_value)
            solutions: dict[Sector, RadialSolution] = {}
            radial_states: dict[Sector, tuple[complex, complex, complex]] = {}
            for sector in (Sector.ODD, Sector.EVEN):
                solve_started = time.perf_counter()
                solution = radial_solver(sector, ell, k, background, config)
                solve_elapsed = time.perf_counter() - solve_started
                A_in = complex(solution.A_in)
                if A_in == 0.0 or not np.isfinite(A_in.real + A_in.imag):
                    raise RuntimeError("strict-Psi4 radial solution has invalid A_in.")
                psi = complex(solution.psi_at(radius))
                derivative = complex(solution.dpsi_dr_at(radius))
                _require_finite_complex(
                    np.asarray((psi, derivative), dtype=np.complex128),
                    "strict-Psi4 radial state",
                )
                solutions[sector] = solution
                radial_states[sector] = (A_in, psi, derivative)
                solve_counts[frequency_index] += 1
                mode_diagnostics.append(
                    _solution_diagnostic_record(
                        solution,
                        solve_elapsed_seconds=solve_elapsed,
                    )
                )

            for theta_index, theta_value in enumerate(theta):
                shell_modes = []
                for m in range(-ell, ell + 1):
                    for sector in (Sector.ODD, Sector.EVEN):
                        coefficient = (
                            incident.c_lm_odd(ell, m)
                            if sector is Sector.ODD
                            else incident.c_lm_even(ell, m)
                        )
                        if coefficient == 0.0:
                            continue
                        A_in, psi, derivative = radial_states[sector]
                        scale = coefficient / A_in
                        metric_mode = reconstruct_metric_mode(
                            sector,
                            ell,
                            k,
                            radius,
                            scale * psi,
                            scale * derivative,
                            background,
                        )
                        shell_modes.append(
                            weyl_mode_components(
                                sector,
                                ell,
                                m,
                                k,
                                radius,
                                float(theta_value),
                                float(phi),
                                metric_mode,
                                background,
                            )
                        )
                shell_psi4 = complex(assemble_weyl_scalars(shell_modes)["Psi4"])
                shell_values[frequency_index, theta_index, shell_index] = shell_psi4
                cumulative[theta_index] += shell_psi4
                cumulative_values[frequency_index, theta_index, shell_index] = cumulative[
                    theta_index
                ]
        elapsed_by_frequency[frequency_index] = time.perf_counter() - frequency_started
        if progress is not None:
            progress(
                {
                    "event": "fig2_frequency_complete",
                    "frequency_index": frequency_index,
                    "kM": float(kM_value),
                    "solve_count": int(solve_counts[frequency_index]),
                    "elapsed_seconds": float(elapsed_by_frequency[frequency_index]),
                }
            )

    amplitudes = np.abs(cumulative_values)
    if np.any(amplitudes <= 0.0) or not np.all(np.isfinite(amplitudes)):
        raise RuntimeError("strict Psi4 convergence contains zero/nonfinite amplitude.")
    log_values = np.asarray(np.log10(amplitudes), dtype=np.float64)
    expected_solves = 2 * lmax_values.size
    if not np.array_equal(
        solve_counts,
        np.full(kM.size, expected_solves, dtype=np.int64),
    ):
        raise RuntimeError("radial solve sharing/count contract drift.")

    metadata = _base_metadata()
    metadata.update(
        {
            "A_cross": _complex_json(A_cross),
            "A_plus": _complex_json(A_plus),
            "boundary_config": asdict(config),
            "figure": 2,
            "fourier_convention": FOURIER_CONVENTION,
            "frame": "kinnersley",
            "incremental_shell_sum": True,
            "high_l_required_radius_oracle": (
                "reviewed q018_riccati R60/K2 envelope; used only when the "
                "unchanged ordinary solver returns its certified "
                "evanescent-tail required-radius no-go"
            ),
            "metric_signature": METRIC_SIGNATURE,
            "m_sum": (
                "sum over every integer m=-ell..ell; incident +z support is "
                "exactly m=-2,+2 and all other coefficients are zero"
            ),
            "not_packaged_polarization_scalars": True,
            "observable": "strict_np_psi4",
            "paper_curve_alignment_claim": False,
            "independent_arbitrary_precision_spotcheck_completed": False,
            "high_l_paper_discrepancy_status": (
                "strong finite-radius evidence, not an independent "
                "arbitrary-precision proof"
            ),
            "paper_curve_alignment_note": (
                "Stable finite-radius recomputation of Eq. (34). The published "
                "raster has a high-ell theta=pi/6 excursion for kM=1.5 and 2.0 "
                "that is not reproduced by the verified radial and angular "
                "implementations; do not label this dataset paper-faithful."
            ),
            "phi": float(phi),
            "radial_solve_sharing": (
                "one solve per (k,sector,ell), shared across all theta and m"
            ),
            "radius_over_M": float(radius / background.M),
            "schema_version": "li_hou_zhao_figure2_strict_np_psi4_v1",
            "solve_count_total": int(np.sum(solve_counts)),
            "solve_diagnostics": mode_diagnostics,
            "spin_weight": -2,
            "strict_path": (
                "weyl_mode_components -> assemble_weyl_scalars['Psi4']; "
                "before transform_strict_np_weyl_to_incident_tetrad and before "
                "compute_packaged_polarization_scalars"
            ),
            "tetrad_convention": (
                "Kinnersley: l={f^-1,1,0,0}, n={1/2,-f/2,0,0}, "
                "m={0,0,1,i csc(theta)}/(sqrt(2) r)"
            ),
            "total_compute_seconds": time.perf_counter() - total_started,
        }
    )
    return Figure2Dataset(
        kM_values=kM,
        theta_values=theta,
        phi=float(phi),
        lmax_values=lmax_values,
        psi4_kinnersley=cumulative_values,
        psi4_shell_kinnersley=shell_values,
        log10_abs_psi4=log_values,
        solve_counts=solve_counts,
        elapsed_seconds_by_frequency=elapsed_by_frequency,
        metadata=metadata,
    )


def save_figure1_dataset(dataset: Figure1Dataset, output_dir: str | Path) -> tuple[Path, Path]:
    output = _fresh_or_existing_directory(output_dir)
    arrays = {
        "r": dataset.r,
        "r_star": dataset.r_star,
        "ell_values": dataset.ell_values,
        "exact_odd": dataset.exact_odd,
        "asymptotic_odd": dataset.asymptotic_odd,
        "exact_even": dataset.exact_even,
        "asymptotic_even": dataset.asymptotic_even,
        "A_in_odd": dataset.A_in_odd,
        "A_out_odd": dataset.A_out_odd,
        "phase_factor_odd": dataset.phase_factor_odd,
        "A_in_even": dataset.A_in_even,
        "A_out_even": dataset.A_out_even,
        "phase_factor_even": dataset.phase_factor_even,
    }
    return _save_dataset(output, "fig1_radial_asymptotic_data", arrays, dataset.metadata)


def save_figure2_dataset(dataset: Figure2Dataset, output_dir: str | Path) -> tuple[Path, Path]:
    output = _fresh_or_existing_directory(output_dir)
    arrays = {
        "kM_values": dataset.kM_values,
        "theta_values": dataset.theta_values,
        "phi": np.asarray(dataset.phi, dtype=np.float64),
        "lmax_values": dataset.lmax_values,
        "psi4_kinnersley": dataset.psi4_kinnersley,
        "psi4_shell_kinnersley": dataset.psi4_shell_kinnersley,
        "log10_abs_psi4": dataset.log10_abs_psi4,
        "solve_counts": dataset.solve_counts,
        "elapsed_seconds_by_frequency": dataset.elapsed_seconds_by_frequency,
    }
    return _save_dataset(output, "fig2_strict_psi4_convergence_data", arrays, dataset.metadata)


def load_figure1_dataset(path: str | Path) -> Figure1Dataset:
    arrays, metadata = _load_dataset(path, "li_hou_zhao_figure1_radial_v1")
    expected = {
        "r",
        "r_star",
        "ell_values",
        "exact_odd",
        "asymptotic_odd",
        "exact_even",
        "asymptotic_even",
        "A_in_odd",
        "A_out_odd",
        "phase_factor_odd",
        "A_in_even",
        "A_out_even",
        "phase_factor_even",
    }
    if set(arrays) != expected:
        raise ValueError("Fig. 1 array inventory mismatch.")
    return Figure1Dataset(metadata=metadata, **arrays)


def load_figure2_dataset(path: str | Path) -> Figure2Dataset:
    arrays, metadata = _load_dataset(
        path,
        (
            "li_hou_zhao_figure2_strict_np_psi4_v1",
            "li_hou_zhao_figure2_strict_np_psi4_rout_v2",
        ),
    )
    expected = {
        "kM_values",
        "theta_values",
        "phi",
        "lmax_values",
        "psi4_kinnersley",
        "psi4_shell_kinnersley",
        "log10_abs_psi4",
        "solve_counts",
        "elapsed_seconds_by_frequency",
    }
    if set(arrays) != expected:
        raise ValueError("Fig. 2 array inventory mismatch.")
    phi = float(np.asarray(arrays.pop("phi")))
    return Figure2Dataset(phi=phi, metadata=metadata, **arrays)


def write_checksum_manifest(output_dir: str | Path, *, qa: Mapping[str, Any]) -> Path:
    output = Path(output_dir)
    if not output.is_dir():
        raise ValueError("output directory does not exist.")
    manifest_path = output / "manifest.json"
    if manifest_path.exists():
        raise FileExistsError(manifest_path)
    records = []
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name != manifest_path.name and not path.name.endswith(".tmp"):
            records.append(
                {
                    "name": path.name,
                    "sha256": _sha256_file(path),
                    "size": path.stat().st_size,
                }
            )
    payload = {
        "files": records,
        "qa": dict(qa),
        "schema_version": "li_hou_zhao_figure_manifest_v1",
    }
    _atomic_json(manifest_path, payload)
    return manifest_path


def _save_dataset(
    output: Path,
    stem: str,
    arrays: Mapping[str, NDArray[Any]],
    metadata: Mapping[str, Any],
) -> tuple[Path, Path]:
    npz_path = output / f"{stem}.npz"
    sidecar_path = output / f"{stem}.json"
    _atomic_npz(npz_path, arrays)
    array_contract = {
        name: {
            "dtype": str(np.asarray(value).dtype),
            "sha256": hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest(),
            "shape": list(np.asarray(value).shape),
        }
        for name, value in arrays.items()
    }
    sidecar = dict(metadata)
    sidecar.update(
        {
            "array_contract": array_contract,
            "npz_sha256": _sha256_file(npz_path),
            "npz_size": npz_path.stat().st_size,
        }
    )
    _atomic_json(sidecar_path, sidecar)
    return npz_path, sidecar_path


def _load_dataset(
    path: str | Path,
    schema: str | tuple[str, ...],
) -> tuple[dict[str, NDArray[Any]], dict[str, Any]]:
    npz_path = Path(path)
    sidecar_path = npz_path.with_suffix(".json")
    metadata = _strict_json(sidecar_path)
    accepted_schemas = (schema,) if isinstance(schema, str) else schema
    if metadata.get("schema_version") not in accepted_schemas:
        raise ValueError("dataset schema mismatch.")
    if metadata.get("npz_sha256") != _sha256_file(npz_path):
        raise ValueError("dataset NPZ identity mismatch.")
    with np.load(npz_path, allow_pickle=False) as archive:
        arrays = {name: np.asarray(archive[name]) for name in archive.files}
    if set(arrays) != set(metadata.get("array_contract", {})):
        raise ValueError("dataset array-contract inventory mismatch.")
    for name, value in arrays.items():
        contract = metadata["array_contract"][name]
        actual = {
            "dtype": str(value.dtype),
            "sha256": hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest(),
            "shape": list(value.shape),
        }
        if actual != contract:
            raise ValueError(f"dataset array identity mismatch: {name}")
    return arrays, metadata


def _validate_figure1(dataset: Figure1Dataset) -> None:
    if not np.array_equal(dataset.ell_values, FIG1_ELLS):
        raise ValueError("Fig. 1 ell order mismatch.")
    if dataset.r.ndim != 1 or dataset.r_star.shape != dataset.r.shape:
        raise ValueError("Fig. 1 radial coordinate shape mismatch.")
    shape = (FIG1_ELLS.size, dataset.r.size)
    for name in ("exact_odd", "asymptotic_odd", "exact_even", "asymptotic_even"):
        value = np.asarray(getattr(dataset, name))
        if value.shape != shape or value.dtype != np.complex128:
            raise ValueError(f"Fig. 1 curve contract mismatch: {name}")
        _require_finite_complex(value, name)
    coefficient_shape = (FIG1_ELLS.size,)
    for name in (
        "A_in_odd",
        "A_out_odd",
        "phase_factor_odd",
        "A_in_even",
        "A_out_even",
        "phase_factor_even",
    ):
        value = np.asarray(getattr(dataset, name))
        if value.shape != coefficient_shape or value.dtype != np.complex128:
            raise ValueError(f"Fig. 1 coefficient contract mismatch: {name}")
        _require_finite_complex(value, name)


def _validate_figure2(dataset: Figure2Dataset) -> None:
    if dataset.kM_values.ndim != 1 or dataset.theta_values.ndim != 1:
        raise ValueError("Fig. 2 coordinate vectors must be one-dimensional.")
    if dataset.lmax_values.ndim != 1 or dataset.lmax_values[0] != 2:
        raise ValueError("Fig. 2 lmax vector must start at 2.")
    if not np.array_equal(
        dataset.lmax_values,
        np.arange(2, int(dataset.lmax_values[-1]) + 1, dtype=np.int64),
    ):
        raise ValueError("Fig. 2 lmax values must contain every integer.")
    shape = (
        dataset.kM_values.size,
        dataset.theta_values.size,
        dataset.lmax_values.size,
    )
    for name in ("psi4_kinnersley", "psi4_shell_kinnersley"):
        value = np.asarray(getattr(dataset, name))
        if value.shape != shape or value.dtype != np.complex128:
            raise ValueError(f"Fig. 2 complex array contract mismatch: {name}")
        _require_finite_complex(value, name)
    if dataset.log10_abs_psi4.shape != shape or dataset.log10_abs_psi4.dtype != np.float64:
        raise ValueError("Fig. 2 logarithm array contract mismatch.")
    if not np.all(np.isfinite(dataset.log10_abs_psi4)):
        raise ValueError("Fig. 2 logarithm contains nonfinite values.")
    np.testing.assert_allclose(
        np.cumsum(dataset.psi4_shell_kinnersley, axis=2),
        dataset.psi4_kinnersley,
        rtol=2.0e-15,
        atol=2.0e-15,
    )
    np.testing.assert_array_equal(
        np.log10(np.abs(dataset.psi4_kinnersley)),
        dataset.log10_abs_psi4,
    )


def _solution_diagnostic_record(
    solution: RadialSolution,
    *,
    solve_elapsed_seconds: float,
) -> dict[str, Any]:
    diagnostics = solution.diagnostics
    warnings = []
    for warning in diagnostics.warnings:
        warnings.append(
            warning.to_metadata() if hasattr(warning, "to_metadata") else dict(warning)
        )
    return {
        "A_in": _complex_json(solution.A_in),
        "A_out": _complex_json(solution.A_out),
        "atol": float(diagnostics.atol),
        "barrier_action": float(diagnostics.barrier_action),
        "boundary_residual": float(diagnostics.boundary_residual),
        "ell": int(solution.ell),
        "flux_residual": float(diagnostics.flux_residual),
        "k": float(solution.k),
        "match_condition_number": float(diagnostics.match_condition_number),
        "ode_n_steps": int(diagnostics.ode_n_steps),
        "ode_status": str(diagnostics.ode_status),
        "phase_factor": _complex_json(solution.phase_factor),
        "r_in": float(diagnostics.r_in),
        "r_out": float(diagnostics.r_out),
        "raw_wronskian_residual": float(diagnostics.raw_wronskian_residual),
        "rtol": float(diagnostics.rtol),
        "sector": solution.sector.value,
        "solve_elapsed_seconds": float(solve_elapsed_seconds),
        "solver": str(diagnostics.solver),
        "valid_until_r": (
            None if solution.valid_until_r is None else float(solution.valid_until_r)
        ),
        "warnings": warnings,
        "wronskian_residual": float(diagnostics.wronskian_residual),
    }


def _base_metadata() -> dict[str, Any]:
    paper = (Path.cwd() / PAPER_PATH).resolve(strict=True)
    if _sha256_file(paper) != PAPER_SHA256:
        raise RuntimeError("authoritative paper identity drift.")
    source_paths = (
        Path(__file__),
        Path("src/schwgw/numerics/radial_solver.py"),
        Path("src/schwgw/scattering/partial_wave.py"),
        Path("src/schwgw/scattering/weyl.py"),
        Path("src/schwgw/perturbations/reconstruction.py"),
        Path("src/schwgw/waves/incident.py"),
        Path("docs/physics_spec.md"),
    )
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "implementation_sources": {
            str(path): _sha256_file(path.resolve(strict=True)) for path in source_paths
        },
        "paper": {"path": str(paper), "sha256": PAPER_SHA256},
        "platform": platform.platform(),
        "python": sys.version,
        "runtime": {
            "numpy": {"version": np.__version__, "path": str(Path(np.__file__).resolve())},
        },
        "units": "G=c=M=1",
    }


def _git_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _complex_json(value: complex) -> dict[str, float]:
    number = complex(value)
    return {"imag": float(number.imag), "real": float(number.real)}


def _require_finite_complex(value: NDArray[np.complex128], name: str) -> None:
    if not np.all(np.isfinite(value.real)) or not np.all(np.isfinite(value.imag)):
        raise ValueError(f"{name} contains nonfinite values.")


def _fresh_or_existing_directory(path: str | Path) -> Path:
    output = Path(path)
    output.mkdir(parents=True, exist_ok=True)
    if output.is_symlink() or not output.is_dir():
        raise ValueError("output must be a real directory.")
    return output


def _atomic_npz(path: Path, arrays: Mapping[str, NDArray[Any]]) -> None:
    if path.exists():
        raise FileExistsError(path)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if temporary.exists():
        raise FileExistsError(temporary)
    try:
        with temporary.open("xb") as stream:
            np.savez_compressed(stream, **arrays)
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists():
            raise FileExistsError(path)
        os.replace(temporary, path)
        _fsync_parent(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    payload = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    if path.exists():
        raise FileExistsError(path)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if temporary.exists():
        raise FileExistsError(temporary)
    try:
        with temporary.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists():
            raise FileExistsError(path)
        os.replace(temporary, path)
        _fsync_parent(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def _fsync_parent(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _strict_json(path: Path) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    value = json.loads(
        path.read_text(encoding="utf-8", errors="strict"),
        object_pairs_hook=pairs,
        parse_constant=lambda item: (_ for _ in ()).throw(
            ValueError(f"nonfinite JSON constant: {item}")
        ),
    )
    if not isinstance(value, dict):
        raise ValueError("JSON sidecar must contain an object.")
    return value


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


__all__ = [
    "FIG1_ELLS",
    "FIG2_KM",
    "FIG2_THETA",
    "Figure1Dataset",
    "Figure2Dataset",
    "compute_figure1_dataset",
    "compute_strict_np_psi4_convergence",
    "leading_radial_asymptote",
    "load_figure1_dataset",
    "load_figure2_dataset",
    "normalized_radial",
    "save_figure1_dataset",
    "save_figure2_dataset",
    "write_checksum_manifest",
]
